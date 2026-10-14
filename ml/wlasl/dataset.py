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


def resample(seq: np.ndarray, length: int = SEQ_LEN) -> np.ndarray:
    """沿時間軸等距取 length 幀（最近鄰），不足時重複幀；最近鄰不會把 NaN 擴散到相鄰幀。"""
    t = len(seq)
    if t == 0:
        raise ValueError("空序列")
    idx = np.round(np.linspace(0, t - 1, length)).astype(int)
    return seq[idx]


def prepare(seq: np.ndarray, length: int = SEQ_LEN) -> np.ndarray:
    """原始關鍵點 (T, K, 3) → 模型輸入 (length, K, 3)。訓練、驗證、即時推論都走這一個函式。"""
    return resample(normalize(seq), length).astype(np.float32)


def load_split(data_dir: str | Path) -> tuple[dict[str, list[dict]], list[str]]:
    """讀 index.json / labels.json，回傳 {'train': [...], 'val': [...], 'test': [...]} 與 labels。"""
    data_dir = Path(data_dir)
    index = json.loads((data_dir / "index.json").read_text())
    labels = json.loads((data_dir / "labels.json").read_text(encoding="utf-8"))
    splits: dict[str, list[dict]] = {"train": [], "val": [], "test": []}
    for r in index:
        splits[r["subset"]].append(r)
    return splits, labels


def load_raw(data_dir: str | Path, records: list[dict]) -> list[np.ndarray]:
    kp = Path(data_dir) / "keypoints"
    return [np.load(kp / f"{r['video_id']}.npy") for r in records]
