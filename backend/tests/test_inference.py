"""Ensemble：平均詞機率、不把背景類算進去。"""
from __future__ import annotations

import numpy as np
import pytest

from app.inference import Ensemble, softmax


class Fake:
    def __init__(self, run_name: str, logits: list[float]):
        self.run_name, self.labels = run_name, ["a", "b", "c"]
        self._logits = np.array(logits, dtype=np.float32)

    def logits(self, raw):
        return self._logits


def test_averages_word_probs_and_ignores_background_class():
    first, second = [3.0, 1.0, 0.0], [0.0, 2.0, 1.0, 9.0]  # 第二個模型多一個背景類
    p = Ensemble(Fake("x", first), Fake("y", second)).predict(np.zeros((4, 55, 3)))
    want = (softmax(np.array(first)) + softmax(np.array(second[:3]))) / 2
    assert p.gloss == "a"
    assert p.prob == pytest.approx(want.max())
    assert [g for g, _ in p.top5] == ["a", "b", "c"]
    assert not p.is_background


def test_run_name_lists_both_models():
    assert Ensemble(Fake("x", [0, 0, 0]), Fake("y", [0, 0, 0])).run_name == "x+y"
