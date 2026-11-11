"""讀前處理產出、切 split、把一段關鍵點轉成固定長度的模型輸入（只用 numpy，本機也能測）。

模型輸入固定為 (SEQ_LEN, K, 3)：先正規化、再重新取樣到 SEQ_LEN 幀；缺點保留 NaN，
NaN 的處理（補 0 + 出現旗標）寫在模型 forward 裡，這樣匯出的 ONNX 也包含同一套邏輯。
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from wlasl.landmarks import normalize

SEQ_LEN = 64
BG = "_bg"  # 背景類（不是詞）的標籤，固定放在 labels 最後一類


def resample(seq: np.ndarray, length: int = SEQ_LEN, mode: str = "linear") -> np.ndarray:
    """沿時間軸等距取 length 幀，不足時補幀。

    linear：相鄰兩幀線性內插，速度特徵連續；任一邊是 NaN 的點退回最近鄰，NaN 不會擴散。
    nearest：最近鄰（20261014-v1 用的方式）。輸入幀數少時會重複幀形成階梯，速度特徵忽大忽零，
    即時串流 10 fps 送進來的序列和訓練的 30 fps 差最多，這是相位不穩的原因之一。
    """
    t = len(seq)
    if t == 0:
        raise ValueError("空序列")
    pos = np.linspace(0, t - 1, length)
    near = seq[np.round(pos).astype(int)]
    if mode == "nearest":
        return near
    lo = np.floor(pos).astype(int)
    hi = np.minimum(lo + 1, t - 1)
    w = (pos - lo)[:, None, None]
    out = seq[lo] * (1 - w) + seq[hi] * w
    return np.where(np.isnan(out), near, out)


def prepare(seq: np.ndarray, length: int = SEQ_LEN, mode: str = "linear") -> np.ndarray:
    """原始關鍵點 (T, K, 3) → 模型輸入 (length, K, 3)。訓練、驗證、即時推論都走這一個函式。

    mode 是模型輸入定義的一部分，匯出時寫進 metrics.json 的 resample，推論端照著用。
    """
    return resample(normalize(seq), length, mode).astype(np.float32)


def labeled_span(record: dict, n_frames: int) -> tuple[int, int]:
    """index 裡人工標註的起訖（1 起算、含端點）→ [起, 迄) 幀索引。前處理擷取的是整支影片。"""
    return record["start"] - 1, min(record["end"], n_frames) if record["end"] != -1 else n_frames


def load_split(data_dir: str | Path, classes: int | None = None) -> tuple[dict[str, list[dict]], list[str]]:
    """讀 index.json / labels.json，回傳 {'train': [...], 'val': [...], 'test': [...]} 與 labels。

    classes：只留前 N 類（WLASL 的類別依 WLASL_v0.3.json 排序，WLASL100 就是 WLASL2000 的前 100 類）。
    """
    data_dir = Path(data_dir)
    index = json.loads((data_dir / "index.json").read_text())
    labels = json.loads((data_dir / "labels.json").read_text(encoding="utf-8"))
    if classes:
        labels = labels[:classes]
    splits: dict[str, list[dict]] = {"train": [], "val": [], "test": []}
    for r in index:
        if r["label"] < len(labels):
            splits.setdefault(r["subset"], []).append(r)  # 換人切分另有 test_seen（見 signers.py）
    return splits, labels


def load_raw(data_dir: str | Path, records: list[dict]) -> list[np.ndarray]:
    kp = Path(data_dir) / "keypoints"
    return [np.load(kp / f"{r['video_id']}.npy") for r in records]


def resample_mode(model_dir: str | Path) -> str:
    """模型匯出時記錄的 prepare mode；舊模型（20261014-v1）沒有這個欄位，是最近鄰。"""
    metrics = Path(model_dir) / "metrics.json"
    if metrics.is_file():
        return json.loads(metrics.read_text()).get("resample", "nearest")
    return "nearest"
