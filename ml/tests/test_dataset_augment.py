import numpy as np
import pytest

from wlasl import landmarks as L
from wlasl.augment import MIRROR_PERM, augment, mirror, time_crop
from wlasl.dataset import SEQ_LEN, prepare, resample


def _seq(t=30, seed=0):
    rng = np.random.default_rng(seed)
    s = rng.uniform(0, 1, (t, L.K, 3)).astype(np.float32)
    s[:, L.L_SHOULDER, :2] = (0.7, 0.5)
    s[:, L.R_SHOULDER, :2] = (0.3, 0.5)
    s[:5, L.RIGHT_HAND] = np.nan
    return s


def test_resample_lengths():
    s = _seq(10)
    assert resample(s, 64).shape == (64, L.K, 3)
    r = resample(_seq(200), 64)
    assert r.shape[0] == 64
    with pytest.raises(ValueError):
        resample(s[:0])


def test_prepare_keeps_nan_and_fixed_len():
    out = prepare(_seq(45))
    assert out.shape == (SEQ_LEN, L.K, 3) and out.dtype == np.float32
    assert np.isnan(out[0, L.RIGHT_HAND]).all()
    assert not np.isnan(out[-1, L.RIGHT_HAND]).any()


def test_mirror_is_involution_and_swaps_hands():
    s = _seq()
    m = mirror(s)
    np.testing.assert_allclose(m[:, L.LEFT_HAND, 0], -s[:, L.RIGHT_HAND, 0])
    np.testing.assert_allclose(mirror(m), s)
    assert sorted(MIRROR_PERM) == list(range(L.K))


def test_mirror_keeps_shoulder_layout_after_normalize():
    # 鏡像後左肩仍在 +x（因為左右點對調），正規化結果和原本一致
    s = _seq()
    a, b = prepare(s), prepare(mirror(s))
    np.testing.assert_allclose(b[:, L.L_SHOULDER, :2], a[:, L.L_SHOULDER, :2], atol=1e-5)


def test_time_crop_and_augment_shapes():
    rng = np.random.default_rng(0)
    s = _seq(50)
    c = time_crop(s, rng)
    assert 40 <= len(c) <= 50
    a = augment(s, rng)
    assert a.dtype == np.float32 and a.shape[1:] == (L.K, 3)
    assert prepare(a).shape == (SEQ_LEN, L.K, 3)
