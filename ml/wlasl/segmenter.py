"""切詞：把連續影格切成一段一段的單詞。

規則（v1，以時間戳計算，不依賴固定 fps；後端串流與訓練增強共用這一份）：
  - 任一手被偵測到 → 進入「比劃中」，往前補 PRE_ROLL 秒（訓練影片開頭也有手還沒舉起的幀）
  - 手消失連續超過 REST 秒 → 這個詞結束，段尾保留這段靜止
  - 比劃超過 MAX 秒 → 強制切一刀，避免連續比劃時永遠不出字
  - 手出現的時間跨度短於 MIN 秒當成雜訊丟掉
限制：連續比劃、手一直沒放下時只能靠 MAX 強制切；之後可改用手速低谷切詞。
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np
from wlasl.landmarks import N_POSE


def hands_visible(frame: np.ndarray) -> bool:
    return bool((~np.isnan(frame[N_POSE:, 0])).any())


@dataclass
class Segmenter:
    rest: float = 0.5
    pre_roll: float = 0.3
    min_len: float = 0.4
    max_len: float = 4.0
    _history: deque = field(default_factory=deque)  # 閒置時的 (t, frame)，給 pre-roll 用
    _frames: list = field(default_factory=list)
    _times: list = field(default_factory=list)
    _first_hand_t: float | None = None
    _last_hand_t: float | None = None
    last_span: tuple[float, float] = (0.0, 0.0)  # 最近一次切出的段落起訖秒數（含 pre-roll 與段尾靜止）

    @property
    def active(self) -> bool:
        return bool(self._frames)

    def push(self, t: float, frame: np.ndarray) -> np.ndarray | None:
        """餵一幀（t 為秒）；某個詞結束時回傳該段 (T, K, 3)，否則 None。"""
        visible = hands_visible(frame)
        if not self.active:
            self._history.append((t, frame))
            while self._history and t - self._history[0][0] > self.pre_roll:
                self._history.popleft()
            if visible:
                self._times = [ht for ht, _ in self._history]
                self._frames = [hf for _, hf in self._history]
                self._history.clear()
                self._first_hand_t = self._last_hand_t = t
            return None

        self._frames.append(frame)
        self._times.append(t)
        if visible:
            self._last_hand_t = t
        if t - self._last_hand_t > self.rest:
            return self._cut()
        if t - self._times[0] > self.max_len:
            return self._cut()
        return None

    def flush(self) -> np.ndarray | None:
        return self._cut() if self.active else None

    def _cut(self) -> np.ndarray | None:
        frames, span = self._frames, self._last_hand_t - self._first_hand_t
        self.last_span = (self._times[0], self._times[-1])
        self._frames, self._times, self._first_hand_t, self._last_hand_t = [], [], None, None
        # 用「手出現的時間跨度」判斷，段尾的靜止不算
        if span < self.min_len:
            return None
        return np.stack(frames)


def segment_spans(seq: np.ndarray, fps: float, **kwargs) -> list[tuple[int, int]]:
    """離線跑一遍切詞器（每幀時間 = i / fps），回傳每段的 [起, 迄) 幀索引。

    訓練時用它取得「上線時切詞器會切出的範圍」，讓模型看過和上線相同的起訖。
    """
    seg, spans = Segmenter(**kwargs), []
    for i, f in enumerate(seq):
        if seg.push(i / fps, f) is not None:
            spans.append(seg.last_span)
    if seg.flush() is not None:
        spans.append(seg.last_span)
    return [(round(a * fps), round(b * fps) + 1) for a, b in spans]
