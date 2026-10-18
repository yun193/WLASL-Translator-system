"""訓練用資料增強（numpy）。輸入輸出都是正規化前的原始序列 (T, K, 3)，之後再交給 dataset.prepare。

在正規化前做，是為了讓空間增強（旋轉、縮放）不影響正規化的定義：
正規化會把肩膀拉回原點與單位長度，所以真正留下來的是「手相對身體」的變形。
"""

from __future__ import annotations

import numpy as np

from wlasl.landmarks import LEFT_HAND, POSE_IDX, RIGHT_HAND, normalize

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


def keypoint_noise(seq: np.ndarray, rng: np.random.Generator, sigma_max=0.006, p_shift=0.05, shift_sigma=0.02,
                   p_drop_max=0.04) -> np.ndarray:
    """模擬鏡頭串流（640×480 JPEG80）的關鍵點誤差，量自 test 影片與 Kaggle 擷取的差：
    手的座標差中位 0.0014、p90 0.0077、p99 0.035（長尾），且約 2% 的幀手忽有忽無。

    - 每點高斯雜訊：σ 每支影片隨機取 0～sigma_max，涵蓋中位到 p90
    - 整隻手平移：每幀每隻手以 p_shift 機率整體偏移 N(0, shift_sigma)，補長尾（追蹤跳一下）
    - 手掉幀：每幀每隻手以 0～p_drop_max 的機率設成 NaN（偵測不到）
    """
    out = seq + rng.normal(0, rng.uniform(0, sigma_max), seq.shape).astype(np.float32)
    t = len(out)
    p_drop = rng.uniform(0, p_drop_max)
    for hand in (LEFT_HAND, RIGHT_HAND):
        shift = rng.random(t) < p_shift
        out[shift, hand, :2] += rng.normal(0, shift_sigma, (shift.sum(), 1, 2)).astype(np.float32)
        out[rng.random(t) < p_drop, hand] = np.nan
    return out


# ---------- 連續手語：背景類（不是詞）與帶上下文的正樣本 ----------
# 單字影片一支一個詞、前後有手舉起放下；對話裡詞和詞直接相連，滑動窗口常常只切到半個詞或兩個詞的交界。
# 這些窗口沒有正確答案，模型以前只能硬塞進某一類（podcast 上 decide、play 等高信心亂認），
# 所以訓練時合成出來當「背景」類；反過來，正樣本也接上鄰居的片段，讓模型習慣詞前後有別的動作。

ACTIVE_Y = 1.0  # 正規化座標（肩膀中點為原點、肩寬為 1）：手腕高於這條線才算在比；量自 test，比劃中約 0.2～0.5、手放下約 1.3～1.5
_WRISTS = [POSE_IDX.index(15), POSE_IDX.index(16)]


def active_span(seq: np.ndarray, span: tuple[int, int], min_len=4) -> tuple[int, int]:
    """span 範圍內真正在比的那一段 [起, 迄)：第一個到最後一個手腕舉起的幀；找不到就回傳原範圍。"""
    a, b = span
    y = normalize(seq[a:b])[:, _WRISTS, 1]
    y = np.where(np.isnan(y), np.inf, y).min(1)
    act = np.flatnonzero(y < ACTIVE_Y)
    if len(act) < min_len:
        return a, b
    return a + int(act[0]), a + int(act[-1]) + 1


def splice(parts: list[np.ndarray], rng: np.random.Generator, fps: float) -> np.ndarray:
    """把幾段各自正規化的序列接起來，中間補 0.03～0.15 秒的線性過渡（模擬手從上一個詞移到下一個詞）。"""
    out = [normalize(parts[0])]
    for p in parts[1:]:
        p = normalize(p)
        m = int(rng.integers(1, max(2, round(0.15 * fps)) + 1))
        w = np.linspace(0, 1, m + 2, dtype=np.float32)[1:-1, None, None]
        out += [out[-1][-1] * (1 - w) + p[0] * w, p]
    return np.concatenate(out).astype(np.float32)


def _piece(seq, span, rng, lo, hi, where):
    """span 內取長度比例 lo～hi 的一段；where：head 取開頭、tail 取結尾、any 隨機位置。"""
    a, b = span
    n = max(2, int(round((b - a) * rng.uniform(lo, hi))))
    n = min(n, b - a)
    s = a if where == "head" else b - n if where == "tail" else int(rng.integers(a, b - n + 1))
    return seq[s:s + n]


def background_sample(pool: list[tuple[np.ndarray, tuple[int, int], float]], rng: np.random.Generator,
                      others: list[tuple[np.ndarray, tuple[int, int], float]] | None = None,
                      p_other=0.0) -> np.ndarray:
    """合成一個「不是詞」的片段。pool / others：(原始序列, 比劃範圍, fps)；others 是詞彙表外的詞（開放集負樣本）。

    - 交界（50%）：A 詞結尾 20～50% 接 B 詞開頭 20～50%，兩邊都不到半個詞
    - 半個詞（25%）：單一詞的 15～40%
    - 靜止（其餘）：比劃範圍外手舉起前、放下後的幀；不夠長就退回半個詞
    - 詞彙表外的詞（p_other）：整個詞，給「只認 100 詞、其他都算背景」的設定用
    """
    if others and rng.random() < p_other:
        seq, span, _ = others[rng.integers(len(others))]
        return seq[span[0]:span[1]]
    seq, span, fps = pool[rng.integers(len(pool))]
    r = rng.random()
    if r < 0.5:
        seq2, span2, _ = pool[rng.integers(len(pool))]
        return splice([_piece(seq, span, rng, 0.2, 0.5, "tail"), _piece(seq2, span2, rng, 0.2, 0.5, "head")], rng, fps)
    if r < 0.75:
        return _piece(seq, span, rng, 0.15, 0.4, "any")
    a, b = span
    rest = max([(0, a), (b, len(seq))], key=lambda x: x[1] - x[0])
    if rest[1] - rest[0] < 0.3 * fps:
        return _piece(seq, span, rng, 0.15, 0.4, "any")
    return _piece(seq, rest, rng, 0.3, 1.0, "any")


def with_context(seq: np.ndarray, span: tuple[int, int], pool, rng: np.random.Generator, fps: float,
                 max_frac=0.35) -> np.ndarray:
    """正樣本前後接上別的詞的片段（各 50% 機率，長度最多為本詞的 max_frac），詞本身仍佔窗口大半。"""
    core = seq[span[0]:span[1]]
    parts = [core]
    for where in ("tail", "head"):
        if rng.random() < 0.5:
            s2, sp2, _ = pool[rng.integers(len(pool))]
            p = _piece(s2, sp2, rng, 0.1, 0.5, where)[: max(2, int(len(core) * max_frac))]
            parts = [p, *parts] if where == "tail" else [*parts, p]
    return splice(parts, rng, fps) if len(parts) > 1 else core


def augment(seq: np.ndarray, rng: np.random.Generator, p_mirror=0.5, subsample=True, noise=False) -> np.ndarray:
    if rng.random() < p_mirror:
        seq = mirror(seq)
    if subsample:
        seq = time_subsample(seq, rng)
    seq = time_crop(seq, rng, min_keep=0.9 if subsample else 0.8)
    seq = affine(seq, rng)
    if noise:
        return keypoint_noise(seq, rng).astype(np.float32)
    jitter = rng.normal(0, 0.003, seq.shape).astype(np.float32)
    return (seq + jitter).astype(np.float32)
