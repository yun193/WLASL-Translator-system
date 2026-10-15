import numpy as np

from app.segmenter import Segmenter, hands_visible
from wlasl.landmarks import K, LEFT_HAND


def frame(hand: bool) -> np.ndarray:
    f = np.full((K, 3), np.nan, dtype=np.float32)
    f[:13] = 0.5
    if hand:
        f[LEFT_HAND] = 0.6
    return f


def feed(seg, pattern, fps=10.0):
    """pattern：每幀是否有手；回傳 [(結束時間, 段長)]"""
    out = []
    for i, h in enumerate(pattern):
        r = seg.push(i / fps, frame(h))
        if r is not None:
            out.append((i / fps, len(r)))
    return out


def test_hands_visible():
    assert hands_visible(frame(True)) and not hands_visible(frame(False))


def test_single_sign_with_pre_roll_and_rest():
    seg = Segmenter(rest=0.5, pre_roll=0.3, min_len=0.4, max_len=4.0)
    cuts = feed(seg, [False] * 10 + [True] * 10 + [False] * 10)
    # 有手 1.0～1.9s，手消失超過 0.5s 後在 2.5s 切出：pre-roll 2 幀 + 10 幀手 + 6 幀靜止
    assert cuts == [(2.5, 18)]
    assert not seg.active


def test_short_blip_is_dropped():
    seg = Segmenter(min_len=0.4)
    assert feed(seg, [False] * 5 + [True] * 2 + [False] * 10) == []


def test_max_len_forces_cut():
    seg = Segmenter(max_len=1.0, pre_roll=0.0)
    cuts = feed(seg, [True] * 25)
    # 每段約 max_len（10 fps 下 11～12 幀，邊界幀受浮點誤差影響）
    assert len(cuts) == 2 and all(11 <= n <= 12 for _, n in cuts)


def test_flush_returns_pending_segment():
    seg = Segmenter(pre_roll=0.0)
    feed(seg, [True] * 8)
    assert len(seg.flush()) == 8
    assert seg.flush() is None
