import math

import numpy as np
import pytest

from wlasl.evaluate import nan_aware_max_diff, topk_hits, wilson


def test_wilson_bounds():
    lo, hi = wilson(70, 100)
    assert lo == pytest.approx(0.604, abs=1e-3) and hi == pytest.approx(0.781, abs=1e-3)
    assert wilson(0, 10)[0] == 0.0 and wilson(10, 10)[1] == 1.0
    assert wilson(0, 0) == (0.0, 0.0)


def test_topk_hits():
    logits = np.array([[0.1, 0.9, 0.0], [0.8, 0.1, 0.5], [0.2, 0.3, 0.1]])
    y = np.array([1, 2, 2])
    assert topk_hits(logits, y, 1).tolist() == [True, False, False]
    assert topk_hits(logits, y, 2).tolist() == [True, True, False]


def test_nan_aware_max_diff():
    a = np.array([1.0, np.nan, 3.0])
    assert nan_aware_max_diff(a, np.array([1.0, np.nan, 3.5])) == pytest.approx(0.5)
    assert math.isinf(nan_aware_max_diff(a, np.array([1.0, 2.0, 3.0])))
