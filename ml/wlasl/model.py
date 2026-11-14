"""輕量時序 Transformer（Kaggle 訓練用；本機只跑匯出的 ONNX，不 import 這個檔）。

輸入 (B, SEQ_LEN, K, 3) 正規化後座標，缺點為 NaN。NaN 處理寫在 forward 裡，匯出的 ONNX 也帶著：
  - 只用 x、y；MediaPipe 的 z 是相對深度，雜訊大
  - 缺點補 0，另外給模型三個出現旗標（姿勢、左手、右手）
  - 加上速度（前後幀差），缺點那一幀的速度為 0
  - canon（2026-11-14）：判斷慣用手（動得多的那隻），左手為主就整段鏡像成右手為主，左撇子和右撇子看起來一樣
  - hand_local（2026-11-14）：每隻手另外以手腕為原點、手腕→中指根距離為單位，手形不被手臂位置淹沒
  - arch="parts"（2026-11-15，仿 Uni-Sign ICLR 2025）：左手、右手、身體各自一個 3 層空間 GCN＋時間卷積，
    關節平均成每部位一個向量後再進 Transformer；每個關節的輸入是全身座標、速度、出現旗標、部位內局部座標
  - local="rot"（2026-11-14）：再把每隻手轉正（手腕→中指根固定朝同一方向），手腕怎麼轉手指座標都一樣；轉角另給 cos/sin
"""

from __future__ import annotations

import torch
from torch import nn

from wlasl.augment import MIRROR_PERM
from wlasl.dataset import SEQ_LEN
from wlasl.landmarks import K, LEFT_HAND, N_HAND, POSE, RIGHT_HAND

FEAT_DIM = K * 4 + 3
LOCAL_DIM = 2 * N_HAND * 2
ROT_DIM = 2 * (N_HAND * 2 + 2)


def local_dim(local: bool | str) -> int:
    return ROT_DIM if local == "rot" else LOCAL_DIM if local else 0


def hand_motion(x: torch.Tensor, hand: slice) -> torch.Tensor:
    """一隻手整段的移動量（缺點不算），(B,)。"""
    v = x[:, 1:, hand, :2] - x[:, :-1, hand, :2]
    return torch.nan_to_num(v.norm(dim=-1), nan=0.0).sum((1, 2))


def canonical_hand(x: torch.Tensor) -> torch.Tensor:
    """左手動得比右手多就鏡像（x 取負、左右點對調），讓慣用手固定在右手的位置。"""
    perm = torch.as_tensor(MIRROR_PERM, device=x.device)
    mirrored = x.index_select(2, perm) * torch.tensor([-1.0, 1.0, 1.0], device=x.device, dtype=x.dtype)
    flip = (hand_motion(x, LEFT_HAND) > hand_motion(x, RIGHT_HAND)).view(-1, 1, 1, 1)
    return torch.where(flip, mirrored, x)


def hand_local(xy: torch.Tensor, rotate: bool = False) -> torch.Tensor:
    """(B,T,K,2) 含 NaN → 每隻手相對手腕、以手掌大小為單位的座標，缺手補 0。

    rotate：再旋轉成手腕→中指根 = (0, 1)，並附上該方向 (u_x, u_y)，輸出 (B,T,ROT_DIM)；否則 (B,T,LOCAL_DIM)。
    """
    out = []
    for hand in (LEFT_HAND, RIGHT_HAND):
        h = xy[:, :, hand]
        wrist = h[:, :, :1]
        axis = h[:, :, 9:10] - wrist
        size = axis.norm(dim=-1, keepdim=True).clamp_min(1e-3)
        p = (h - wrist) / size
        if rotate:
            u = axis / size  # (B,T,1,2) 單位向量
            ux, uy = u[..., :1], u[..., 1:]
            p = torch.cat([p[..., :1] * uy - p[..., 1:] * ux, p[..., :1] * ux + p[..., 1:] * uy], dim=-1)  # 純旋轉
        feats = [torch.nan_to_num(p, nan=0.0).clamp(-5, 5).flatten(2)]
        if rotate:
            feats.append(torch.nan_to_num(u, nan=0.0).flatten(2))
        out += feats
    return torch.cat(out, dim=-1)


def build_features(x: torch.Tensor, local: bool | str = False) -> torch.Tensor:
    xy = x[..., :2]
    nan = torch.isnan(xy[..., 0])  # (B, T, K)
    present = (~nan).to(xy.dtype)
    xy = torch.where(torch.isnan(xy), torch.zeros_like(xy), xy)
    vel = xy[:, 1:] - xy[:, :-1]
    both = (present[:, 1:] * present[:, :-1]).unsqueeze(-1)
    vel = torch.cat([torch.zeros_like(xy[:, :1]), vel * both], dim=1)
    flags = torch.stack(
        [present[..., POSE].amax(-1), present[..., LEFT_HAND].amax(-1), present[..., RIGHT_HAND].amax(-1)],
        dim=-1,
    )
    b, t = x.shape[:2]
    feats = [xy.reshape(b, t, -1), vel.reshape(b, t, -1), flags]
    if local:
        feats.append(hand_local(x[..., :2], rotate=local == "rot"))
    return torch.cat(feats, dim=-1)


HAND_EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9), (9, 10), (10, 11), (11, 12),
              (9, 13), (13, 14), (14, 15), (15, 16), (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)]
# POSE_IDX 內的位置：0 鼻、1/2 眼、3/4 耳、5/6 嘴角、7/8 肩、9/10 肘、11/12 腕；鼻接兩肩讓臉和手臂連通
BODY_EDGES = [(0, 1), (1, 3), (0, 2), (2, 4), (5, 6), (0, 5), (0, 6), (7, 8), (7, 9), (9, 11), (8, 10), (10, 12), (0, 7), (0, 8)]
JOINT_DIM = 7  # 全身 xy、速度 xy、出現旗標、部位內局部 xy


def norm_adjacency(n: int, edges) -> torch.Tensor:
    a = torch.eye(n)
    for i, j in edges:
        a[i, j] = a[j, i] = 1.0
    d = a.sum(1).rsqrt()
    return d[:, None] * a * d[None, :]


class PartEncoder(nn.Module):
    """一個部位：3 層空間 GCN（每幀內關節互傳）＋ 一層時間卷積（每個關節沿時間），最後關節平均 → (B,T,dim)。"""

    def __init__(self, n: int, edges, dim: int = 64, layers: int = 3, t_kernel: int = 5, drop: float = 0.1):
        super().__init__()
        self.register_buffer("adj", norm_adjacency(n, edges))
        self.inp = nn.Linear(JOINT_DIM, dim)
        self.gcn = nn.ModuleList(nn.Linear(dim, dim) for _ in range(layers))
        self.norms = nn.ModuleList(nn.LayerNorm(dim) for _ in range(layers))
        self.temporal = nn.Conv2d(dim, dim, (t_kernel, 1), padding=(t_kernel // 2, 0), groups=dim)
        self.tnorm = nn.LayerNorm(dim)
        self.act, self.drop = nn.GELU(), nn.Dropout(drop)

    def forward(self, j: torch.Tensor) -> torch.Tensor:  # j: (B,T,N,JOINT_DIM)
        h = self.inp(j)
        for lin, ln in zip(self.gcn, self.norms):
            h = h + self.drop(self.act(lin(ln(torch.einsum("nm,btmc->btnc", self.adj, h)))))
        t = self.temporal(h.permute(0, 3, 1, 2)).permute(0, 2, 3, 1)  # (B,T,N,C)
        h = h + self.drop(self.act(self.tnorm(t)))
        return h.mean(2)


def joint_features(x: torch.Tensor) -> torch.Tensor:
    """(B,T,K,3) 含 NaN → 每個關節 (B,T,K,JOINT_DIM)。手的局部座標相對手腕、以手掌大小為單位；身體的局部座標就是全身座標。"""
    xy = x[..., :2]
    present = (~torch.isnan(xy[..., 0])).to(xy.dtype)
    xy0 = torch.nan_to_num(xy, nan=0.0)
    vel = xy0[:, 1:] - xy0[:, :-1]
    vel = torch.cat([torch.zeros_like(xy0[:, :1]), vel * (present[:, 1:] * present[:, :-1]).unsqueeze(-1)], dim=1)
    local = xy0.clone()
    for hand in (LEFT_HAND, RIGHT_HAND):
        h = xy[:, :, hand]
        wrist = h[:, :, :1]
        size = (h[:, :, 9:10] - wrist).norm(dim=-1, keepdim=True).clamp_min(1e-3)
        local[:, :, hand] = torch.nan_to_num((h - wrist) / size, nan=0.0).clamp(-5, 5)
    return torch.cat([xy0, vel, present.unsqueeze(-1), local], dim=-1)


class SignTransformer(nn.Module):
    def __init__(self, n_classes: int, d: int = 128, layers: int = 4, heads: int = 4, ff: int = 256,
                 drop: float = 0.2, seq_len: int = SEQ_LEN, canon: bool = False, local: bool | str = False,
                 arch: str = "flat", part_dim: int = 64):
        super().__init__()
        self.config = dict(n_classes=n_classes, d=d, layers=layers, heads=heads, ff=ff, drop=drop, seq_len=seq_len,
                           canon=canon, local=local, arch=arch, part_dim=part_dim)
        self.canon, self.local, self.arch = canon, local, arch
        if arch == "parts":
            self.parts = nn.ModuleList([PartEncoder(N_HAND, HAND_EDGES, part_dim), PartEncoder(N_HAND, HAND_EDGES, part_dim),
                                        PartEncoder(POSE.stop, BODY_EDGES, part_dim)])
            in_dim = 3 * part_dim + 3
        else:
            in_dim = FEAT_DIM + local_dim(local)
        self.proj = nn.Sequential(nn.Linear(in_dim, d), nn.LayerNorm(d), nn.GELU(), nn.Dropout(drop))
        self.pos = nn.Parameter(torch.zeros(1, seq_len, d))
        nn.init.trunc_normal_(self.pos, std=0.02)
        layer = nn.TransformerEncoderLayer(d, heads, ff, drop, activation="gelu", batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(layer, layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(d)
        self.head = nn.Sequential(nn.Dropout(drop), nn.Linear(d, n_classes))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.canon:
            x = canonical_hand(x)
        if self.arch == "parts":
            j = joint_features(x)
            pres = j[..., 4]
            flags = torch.stack([pres[..., POSE].amax(-1), pres[..., LEFT_HAND].amax(-1), pres[..., RIGHT_HAND].amax(-1)], -1)
            feats = torch.cat([self.parts[0](j[:, :, LEFT_HAND]), self.parts[1](j[:, :, RIGHT_HAND]),
                               self.parts[2](j[:, :, POSE]), flags], dim=-1)
        else:
            feats = build_features(x, self.local)
        h = self.proj(feats) + self.pos
        h = self.encoder(h)
        return self.head(self.norm(h.mean(1)))
