import numpy as np
import pytest

from wlasl import landmarks as L
import json

from wlasl.augment import MIRROR_PERM, augment, choose_span, keypoint_noise, mirror, time_crop, time_subsample
from wlasl.dataset import SEQ_LEN, labeled_span, load_split, prepare, resample, resample_mode


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


def test_resample_linear_interpolates_and_does_not_spread_nan():
    s = np.zeros((3, L.K, 3), np.float32)
    s[:, 0, 0] = [0.0, 1.0, 2.0]
    s[0, 1] = np.nan
    r = resample(s, 5)
    np.testing.assert_allclose(r[:, 0, 0], [0, 0.5, 1, 1.5, 2])
    # 第 0 幀是 NaN：碰到它的內插點退回最近鄰，位置 0.5 捨入到第 0 幀所以仍是 NaN；NaN 不會再往後擴散
    assert np.isnan(r[:2, 1]).all() and not np.isnan(r[2:, 1]).any()
    near = resample(s, 5, mode="nearest")
    np.testing.assert_allclose(near[:, 0, 0], [0, 0, 1, 2, 2])  # np.round 是銀行家捨入：0.5→0、1.5→2


def test_resample_mode_defaults_to_nearest_for_old_models(tmp_path):
    assert resample_mode(tmp_path) == "nearest"
    (tmp_path / "metrics.json").write_text(json.dumps({"resample": "linear"}))
    assert resample_mode(tmp_path) == "linear"


def test_labeled_span_and_class_filter(tmp_path):
    assert labeled_span({"start": 3, "end": 10}, 8) == (2, 8)
    assert labeled_span({"start": 1, "end": -1}, 8) == (0, 8)
    idx = [{"video_id": "a", "label": 0, "subset": "train"}, {"video_id": "b", "label": 5, "subset": "test"}]
    (tmp_path / "index.json").write_text(json.dumps(idx))
    (tmp_path / "labels.json").write_text(json.dumps([str(i) for i in range(10)]))
    splits, labels = load_split(tmp_path, classes=3)
    assert labels == ["0", "1", "2"] and len(splits["train"]) == 1 and not splits["test"]


def test_choose_span_stays_in_bounds_and_uses_segmenter():
    rng = np.random.default_rng(0)
    for _ in range(200):
        a, b = choose_span(60, (10, 40), [(5, 55)], 30.0, rng)
        assert 0 <= a and b <= 60 and b - a >= 4
    # p_segmenter=1、不抖動：一定取和標註重疊最多的切詞段
    assert choose_span(60, (10, 40), [(0, 8), (12, 50)], 30.0, rng, p_segmenter=1, jitter_s=0) == (12, 50)
    assert choose_span(3, (0, 3), [], 30.0, rng) == (0, 3)


def test_time_subsample_strides():
    rng = np.random.default_rng(1)
    s = _seq(60)
    lens = {len(time_subsample(s, rng)) for _ in range(100)}
    assert lens <= {60, 30, 20} and len(lens) == 3
    assert len(time_subsample(s[:3], rng, strides=(3,), p=(1.0,))) == 3  # 太短就不抽


def test_keypoint_noise_drops_hands_but_keeps_shape():
    rng = np.random.default_rng(0)
    s = _seq(400)
    n = keypoint_noise(s, rng, p_drop_max=0.5)
    assert n.shape == s.shape and n.dtype == np.float32
    hand_nan = np.isnan(n[:, L.LEFT_HAND, 0]).all(1)
    assert 0 < hand_nan.mean() < 0.5  # 整隻手一起掉，不是零星的點
    assert not np.isnan(n[:, : L.LEFT_HAND.start]).any()  # 姿勢點不掉
    assert prepare(augment(s, rng, noise=True)).shape == (SEQ_LEN, L.K, 3)
