import numpy as np

from wlasl import landmarks as L
from wlasl.augment import active_span, background_sample, splice, with_context
from wlasl.dataset import prepare
from wlasl.segmenter import Segmenter
from wlasl.spotter import Prediction, SignDecoder, Spotter

LW, RW = L.POSE_IDX.index(15), L.POSE_IDX.index(16)


def _clip(t=40, up=(10, 30), seed=0):
    """肩膀固定、手腕在 up 範圍內舉起（y 在肩膀附近），其餘放下（y 在肩寬 1.5 倍以下）。"""
    rng = np.random.default_rng(seed)
    s = rng.uniform(0.3, 0.7, (t, L.K, 3)).astype(np.float32)
    s[:, L.L_SHOULDER, :2] = (0.7, 0.5)
    s[:, L.R_SHOULDER, :2] = (0.3, 0.5)
    s[:, [LW, RW], 1] = 0.5 + 0.4 * 1.5
    s[up[0]:up[1], [LW, RW], 1] = 0.55
    return s


def test_active_span_finds_raised_hands():
    assert active_span(_clip(), (0, 40)) == (10, 30)
    # 手一直沒舉起：退回原範圍
    s = _clip(up=(0, 0))
    assert active_span(s, (2, 38)) == (2, 38)


def test_background_and_context_samples_are_valid_inputs():
    rng = np.random.default_rng(0)
    pool = [(_clip(seed=i), (10, 30), 25.0) for i in range(5)]
    others = [(_clip(seed=9), (10, 30), 25.0)]
    for _ in range(200):
        bg = background_sample(pool, rng, others, p_other=0.2)
        assert bg.ndim == 3 and len(bg) >= 2
        assert prepare(bg).shape[0] == 64
        ctx = with_context(*pool[0][:2], pool, rng, 25.0)
        assert len(ctx) >= 20  # 詞本身完整保留


def test_splice_adds_transition_between_parts():
    rng = np.random.default_rng(0)
    a, b = _clip(seed=1)[10:20], _clip(seed=2)[10:20]
    out = splice([a, b], rng, 25.0)
    assert len(out) > 20 and out.dtype == np.float32


class _Seq:
    """假的分類器：依窗口最後一幀的標記回傳預測（frame[0,0] = 詞編號，-1 = 背景）。"""

    def __call__(self, win):
        k = int(win[-1, 0, 0])
        if k < 0:
            return Prediction("w0", 0.1, [("w0", 0.1)], background=0.9)
        return Prediction(f"w{k}", 0.9, [(f"w{k}", 0.9)])


def _stream(labels, fps=10.0, hands=True):
    for i, k in enumerate(labels):
        f = np.full((L.K, 3), np.nan, np.float32)
        f[0, 0] = k
        if hands:
            f[L.N_POSE:, :] = 0.5
        yield i / fps, f


def test_spotter_emits_once_per_run_and_skips_background():
    sp, out = Spotter(window=0.5, hop=0.2, min_hits=2, threshold=0.5), []
    clf = _Seq()
    for t, f in _stream([1] * 20 + [-1] * 10 + [2] * 20):
        win = sp.push(t, f)
        if win is not None:
            hit = sp.update(win[0], t, clf(win[1]))
            if hit:
                out.append(hit[2].gloss)
    assert out == ["w1", "w2"]


def test_decoder_isolated_uses_segment_and_continuous_uses_spotting():
    clf = _Seq()
    # 單字：比 1 秒後手放下 → 整段分類一次，偵測結果丟掉
    dec = SignDecoder(clf, Segmenter(), Spotter(window=0.5, hop=0.2), continuous_after=3.5)
    out = [s for t, f in _stream([3] * 10) for s in dec.push(t, f)]
    out += [s for t, f in _stream([3] * 10, hands=False) for s in dec.push(1.0 + t, f)]
    assert [(s.mode, s.prediction.gloss) for s in out] == [("segment", "w3")]
    # 連續比 8 秒、中間換詞 → 窗口偵測輸出每個詞，不做整段分類
    dec = SignDecoder(clf, Segmenter(), Spotter(window=0.5, hop=0.2), continuous_after=3.5)
    labels = [1] * 20 + [2] * 20 + [3] * 20 + [4] * 20
    out = [s for t, f in _stream(labels) for s in dec.push(t, f)] + dec.flush()
    assert [s.prediction.gloss for s in out] == ["w1", "w2", "w3", "w4"]
    assert {s.mode for s in out} == {"spot"}
