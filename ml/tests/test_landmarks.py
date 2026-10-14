from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from wlasl import landmarks as L


def _pts(n, x=0.5, y=0.5):
    return [SimpleNamespace(x=x, y=y, z=0.0) for _ in range(n)]


def test_layout_is_contiguous():
    assert L.K == 55
    assert L.POSE.stop == L.LEFT_HAND.start
    assert L.LEFT_HAND.stop == L.RIGHT_HAND.start
    assert L.RIGHT_HAND.stop == L.K


def test_result_to_array_missing_hand_is_nan():
    pose = _pts(33)
    pose[11] = SimpleNamespace(x=0.25, y=0.5, z=0.0)
    r = SimpleNamespace(pose_landmarks=pose, left_hand_landmarks=_pts(21), right_hand_landmarks=[])
    a = L.result_to_array(r, aspect=4 / 3)
    assert a.shape == (L.K, 3) and a.dtype == np.float32
    assert np.isnan(a[L.RIGHT_HAND]).all()
    assert not np.isnan(a[L.LEFT_HAND]).any()
    # x 乘上寬高比
    assert a[L.L_SHOULDER, 0] == pytest.approx(0.25 * 4 / 3)


def test_normalize_centers_and_scales_by_shoulders():
    seq = np.full((4, L.K, 3), np.nan, dtype=np.float32)
    seq[:, L.L_SHOULDER] = (3.0, 2.0, 0.0)
    seq[:, L.R_SHOULDER] = (1.0, 2.0, 0.0)
    seq[:, L.LEFT_HAND] = (4.0, 2.0, 0.0)
    out = L.normalize(seq)
    np.testing.assert_allclose(out[:, L.L_SHOULDER, :2], [[0.5, 0.0]] * 4)
    np.testing.assert_allclose(out[:, L.R_SHOULDER, :2], [[-0.5, 0.0]] * 4)
    np.testing.assert_allclose(out[0, L.LEFT_HAND.start, :2], [1.0, 0.0])
    assert np.isnan(out[:, L.RIGHT_HAND]).all()


def test_normalize_without_shoulders_falls_back():
    seq = np.full((2, L.K, 3), np.nan, dtype=np.float32)
    seq[:, L.LEFT_HAND] = np.random.default_rng(0).normal(size=(2, 21, 3))
    out = L.normalize(seq)
    assert abs(np.nanmean(out[..., :2])) < 1e-5


def test_normalize_all_nan_is_noop():
    seq = np.full((3, L.K, 3), np.nan, dtype=np.float32)
    assert np.isnan(L.normalize(seq)).all()


SAMPLE = Path(__file__).resolve().parents[2] / "data" / "sample" / "00624.mp4"
MODEL = Path(__file__).resolve().parents[2] / "data" / "models" / "holistic_landmarker.task"


@pytest.mark.skipif(not (SAMPLE.exists() and MODEL.exists()), reason="需要 data/sample 影片與模型檔")
def test_extract_video_respects_end_frame():
    seq, fps = L.extract_video(SAMPLE, MODEL, start=1, end=93)
    assert seq.shape == (93, L.K, 3)
    assert fps == pytest.approx(29.97, abs=0.01)
    # 手語影片每一幀都看得到上半身
    assert not np.isnan(seq[:, L.POSE]).any()
