"""輕量時序 Transformer（Kaggle 訓練用；本機只跑匯出的 ONNX，不 import 這個檔）。

輸入 (B, SEQ_LEN, K, 3) 正規化後座標，缺點為 NaN。NaN 處理寫在 forward 裡，匯出的 ONNX 也帶著：
  - 只用 x、y；MediaPipe 的 z 是相對深度，雜訊大
  - 缺點補 0，另外給模型三個出現旗標（姿勢、左手、右手）
  - 加上速度（前後幀差），缺點那一幀的速度為 0
  - canon（2026-11-14）：判斷慣用手（動得多的那隻），左手為主就整段鏡像成右手為主，左撇子和右撇子看起來一樣
  - hand_local（2026-11-14）：每隻手另外以手腕為原點、手腕→中指根距離為單位，手形不被手臂位置淹沒
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


class SignTransformer(nn.Module):
    def __init__(self, n_classes: int, d: int = 128, layers: int = 4, heads: int = 4, ff: int = 256,
                 drop: float = 0.2, seq_len: int = SEQ_LEN, canon: bool = False, local: bool | str = False):
        super().__init__()
        self.config = dict(n_classes=n_classes, d=d, layers=layers, heads=heads, ff=ff, drop=drop, seq_len=seq_len,
                           canon=canon, local=local)
        self.canon, self.local = canon, local
        self.proj = nn.Sequential(nn.Linear(FEAT_DIM + local_dim(local), d), nn.LayerNorm(d), nn.GELU(), nn.Dropout(drop))
        self.pos = nn.Parameter(torch.zeros(1, seq_len, d))
        nn.init.trunc_normal_(self.pos, std=0.02)
        layer = nn.TransformerEncoderLayer(d, heads, ff, drop, activation="gelu", batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(layer, layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(d)
        self.head = nn.Sequential(nn.Dropout(drop), nn.Linear(d, n_classes))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.canon:
            x = canonical_hand(x)
        h = self.proj(build_features(x, self.local)) + self.pos
        h = self.encoder(h)
        return self.head(self.norm(h.mean(1)))
