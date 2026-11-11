"""依手語者重新切分（signer-independent 評估）。

WLASL 官方切分沒有分開手語者：100 詞 test 有 99/100 支的手語者在訓練時出現過，
test 正確率只代表「看過的人」。這裡把手語者分成 k 折，每折留出一組手語者：

- test：留出手語者的所有影片（不分原本的 train/val/test），模型完全沒看過這些人
- test_seen：其餘手語者的原 test 影片，同一個模型、同樣的訓練資料量下的「看過的人」對照
- train / val：其餘手語者的原 train / val

signers.json（video_id → signer_id）由 WLASL_v0.3.json 產生，打包在 wheel 裡給 Kaggle 用。
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

SIGNERS = Path(__file__).with_name("signers.json")


def load_signers(path: str | Path = SIGNERS) -> dict[str, int]:
    return json.loads(Path(path).read_text())


def assign_folds(index: list[dict], signer_of: dict[str, int], k: int, eval_classes: int) -> list[list[int]]:
    """手語者分 k 折，讓每折留出的前 eval_classes 類影片數接近：影片多的手語者先放，放進目前最少的那折。

    同數量時依 signer_id 排序，結果固定、可重現。
    """
    count = Counter(signer_of[r["video_id"]] for r in index if r["label"] < eval_classes)
    for r in index:  # 只出現在其他類的手語者也要分到某一折
        count.setdefault(signer_of[r["video_id"]], 0)
    folds: list[list[int]] = [[] for _ in range(k)]
    load = [0] * k
    for s, n in sorted(count.items(), key=lambda x: (-x[1], x[0])):
        i = min(range(k), key=lambda j: (load[j], j))
        folds[i].append(s)
        load[i] += n
    return [sorted(f) for f in folds]


def resplit(index: list[dict], signer_of: dict[str, int], holdout: set[int]) -> list[dict]:
    """回傳新的 index（subset 改寫過，原紀錄不動）。"""
    out = []
    for r in index:
        if signer_of[r["video_id"]] in holdout:
            subset = "test"
        elif r["subset"] == "test":
            subset = "test_seen"
        else:
            subset = r["subset"]
        out.append({**r, "subset": subset})
    return out
