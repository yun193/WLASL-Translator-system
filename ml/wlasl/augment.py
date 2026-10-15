"""訓練用資料增強（numpy）。輸入輸出都是正規化前的原始序列 (T, K, 3)，之後再交給 dataset.prepare。

在正規化前做，是為了讓空間增強（旋轉、縮放）不影響正規化的定義：
正規化會把肩膀拉回原點與單位長度，所以真正留下來的是「手相對身體」的變形。
"""

from __future__ import annotations

import numpy as np

from wlasl.landmarks import LEFT_HAND, POSE_IDX, RIGHT_HAND

# 鏡像時要對調的姿勢點（pose 原始編號的左右成對）
_POSE_PAIRS = [(2, 5), (7, 8), (9, 10), (11, 12), (13, 14), (15, 16)]
MIRROR_PERM = np.arange(RIGHT_HAND.stop)
for a, b in _POSE_PAIRS:
    ia, ib = POSE_IDX.index(a), POSE_IDX.index(b)
    MIRROR_PERM[ia], MIRROR_PERM[ib] = ib, ia
MIRROR_PERM[LEFT_HAND] = np.arange(RIGHT_HAND.start, RIGHT_HAND.stop)
MIRROR_PERM[RIGHT_HAND] = np.arange(LEFT_HAND.start, LEFT_HAND.stop)


def mirror(seq: np.ndarray) -> np.ndarray:
    """水平鏡像：x 取負、左右點對調（左手 ↔ 右手）。等同換成慣用手相反的人來比。"""
    out = seq[:, MIRROR_PERM].copy()
    out[..., 0] = -out[..., 0]
    return out


def affine(seq: np.ndarray, rng: np.random.Generator, rot_deg=10.0, scale=0.1, shear=0.1) -> np.ndarray:
    th = np.deg2rad(rng.uniform(-rot_deg, rot_deg))
    s = 1 + rng.uniform(-scale, scale)
    sh = rng.uniform(-shear, shear)
    m = s * np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]]) @ np.array([[1, sh], [0, 1]])
    out = seq.copy()
    center = np.nanmean(out[..., :2].reshape(-1, 2), axis=0)
    out[..., :2] = (out[..., :2] - center) @ m.T.astype(np.float32) + center
    return out


def time_crop(seq: np.ndarray, rng: np.random.Generator, min_keep=0.8) -> np.ndarray:
    """隨機保留 80～100% 的連續片段；之後 resample 到固定長度就等於變速。"""
    t = len(seq)
    keep = max(2, int(round(t * rng.uniform(min_keep, 1.0))))
    start = rng.integers(0, t - keep + 1)
    return seq[start : start + keep]


def choose_span(n: int, labeled: tuple[int, int], segmented: list[tuple[int, int]], fps: float,
                rng: np.random.Generator, p_segmenter=0.5, jitter_s=0.2, min_len=4) -> tuple[int, int]:
    """決定這次取整支影片的哪一段：人工標註的起訖，或上線切詞器會切出的範圍，兩端再各抖動 ±jitter_s 秒。

    上線時起訖由切詞器決定（常多包進手放下的動作），只用人工標註訓練的模型沒看過這種輸入。
    """
    a, b = labeled
    if n <= min_len:
        return 0, n
    if segmented and rng.random() < p_segmenter:
        # 取和人工標註重疊最多的那一段
        a, b = max(segmented, key=lambda s: min(s[1], b) - max(s[0], a))
    j = jitter_s * fps
    a = int(np.clip(a + rng.integers(-round(j), round(j) + 1), 0, n - min_len))
    b = int(np.clip(b + rng.integers(-round(j), round(j) + 1), a + min_len, n))
    return a, b


def time_subsample(seq: np.ndarray, rng: np.random.Generator, strides=(1, 2, 3), p=(0.4, 0.35, 0.25)) -> np.ndarray:
    """每 s 幀取 1 幀、起點隨機：訓練影片約 30 fps，上線串流只有 10～15 fps，而且每次抽到的相位不同。"""
    s = int(rng.choice(strides, p=p))
    if s == 1 or len(seq) < 2 * s:
        return seq
    return seq[rng.integers(0, s)::s]


def augment(seq: np.ndarray, rng: np.random.Generator, p_mirror=0.5, subsample=True) -> np.ndarray:
    if rng.random() < p_mirror:
        seq = mirror(seq)
    if subsample:
        seq = time_subsample(seq, rng)
    seq = time_crop(seq, rng, min_keep=0.9 if subsample else 0.8)
    seq = affine(seq, rng)
    jitter = rng.normal(0, 0.003, seq.shape).astype(np.float32)
    return (seq + jitter).astype(np.float32)
