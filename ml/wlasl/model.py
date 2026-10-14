"""輕量時序 Transformer（Kaggle 訓練用；本機只跑匯出的 ONNX，不 import 這個檔）。

輸入 (B, SEQ_LEN, K, 3) 正規化後座標，缺點為 NaN。NaN 處理寫在 forward 裡，匯出的 ONNX 也帶著：
  - 只用 x、y；MediaPipe 的 z 是相對深度，雜訊大
  - 缺點補 0，另外給模型三個出現旗標（姿勢、左手、右手）
  - 加上速度（前後幀差），缺點那一幀的速度為 0
"""

from __future__ import annotations

import torch
from torch import nn

from wlasl.dataset import SEQ_LEN
from wlasl.landmarks import K, LEFT_HAND, POSE, RIGHT_HAND

FEAT_DIM = K * 4 + 3


def build_features(x: torch.Tensor) -> torch.Tensor:
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
    return torch.cat([xy.reshape(b, t, -1), vel.reshape(b, t, -1), flags], dim=-1)


class SignTransformer(nn.Module):
    def __init__(self, n_classes: int, d: int = 128, layers: int = 4, heads: int = 4, ff: int = 256,
                 drop: float = 0.2, seq_len: int = SEQ_LEN):
        super().__init__()
        self.config = dict(n_classes=n_classes, d=d, layers=layers, heads=heads, ff=ff, drop=drop, seq_len=seq_len)
        self.proj = nn.Sequential(nn.Linear(FEAT_DIM, d), nn.LayerNorm(d), nn.GELU(), nn.Dropout(drop))
        self.pos = nn.Parameter(torch.zeros(1, seq_len, d))
        nn.init.trunc_normal_(self.pos, std=0.02)
        layer = nn.TransformerEncoderLayer(d, heads, ff, drop, activation="gelu", batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(layer, layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(d)
        self.head = nn.Sequential(nn.Dropout(drop), nn.Linear(d, n_classes))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.proj(build_features(x)) + self.pos
        h = self.encoder(h)
        return self.head(self.norm(h.mean(1)))
