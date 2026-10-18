"""連續手語：滑動窗口偵測（sign spotting），以及和切詞器合用的解碼器。後端串流、影片檔、離線評估共用這一份。

切詞器靠「手放下」斷詞，對話裡手幾乎不放下（podcast 97% 的幀有手），只能被單詞上限硬切，一段混了好幾個詞。
偵測器不斷詞：每 hop 秒取最近 window 秒分類一次，連續 min_hits 個窗口都是同一個詞、信心都過門檻、
而且不是背景類（不是詞），才輸出這個詞；同一串連續命中只輸出一次。

解碼器的規則：
  - 比劃開始時兩邊同時跑；手放下、段落短（單字）→ 照舊整段分類，偵測結果丟掉（單字的整段分類比較準）
  - 同一段比超過 continuous_after 秒 → 判定為連續比劃，先把暫存的偵測結果送出，之後偵測到就即時輸出、
    切詞器切出的段落不再整段分類；直到手放下才回到單字模式
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from wlasl.segmenter import Segmenter, hands_visible


@dataclass
class Prediction:
    gloss: str
    prob: float
    top5: list[tuple[str, float]]
    background: float = 0.0  # 背景類（不是詞）的機率；舊模型沒有背景類時為 0

    @property
    def is_background(self) -> bool:
        return self.background >= self.prob


@dataclass
class Spotter:
    window: float = 1.0
    hop: float = 0.25
    min_hits: int = 2
    threshold: float = 0.5
    min_hand_ratio: float = 0.5
    _buf: deque = field(default_factory=deque)
    _next_t: float = float("-inf")
    _run: list = field(default_factory=list)  # 目前這串連續命中：[(起, 迄, Prediction)]
    _emitted: bool = False

    def push(self, t: float, frame: np.ndarray) -> tuple[float, np.ndarray] | None:
        """餵一幀；到了該分類的時間回傳 (窗口起點秒, 窗口影格)，否則 None。手太少的窗口直接中斷連續命中。"""
        self._buf.append((t, frame))
        while self._buf and t - self._buf[0][0] > self.window:
            self._buf.popleft()
        if t < self._next_t or t - self._buf[0][0] < self.window * 0.9:
            return None
        self._next_t = t + self.hop
        frames = [f for _, f in self._buf]
        if sum(hands_visible(f) for f in frames) < len(frames) * self.min_hand_ratio:
            self._reset_run()
            return None
        return self._buf[0][0], np.stack(frames)

    def update(self, start: float, end: float, p: Prediction) -> tuple[float, float, Prediction] | None:
        """餵窗口分類結果；這串連續命中剛好達到 min_hits 時回傳 (起, 迄, 平均信心的 Prediction)。"""
        ok = p.prob >= self.threshold and not p.is_background
        if not ok or (self._run and self._run[-1][2].gloss != p.gloss):
            self._reset_run()
        if not ok:
            return None
        self._run.append((start, end, p))
        if len(self._run) < self.min_hits or self._emitted:
            return None
        self._emitted = True
        best = max((x[2] for x in self._run), key=lambda q: q.prob)
        mean = float(np.mean([x[2].prob for x in self._run]))
        return self._run[0][0], end, Prediction(p.gloss, mean, best.top5, best.background)

    def reset(self) -> None:
        self._buf.clear()
        self._next_t = float("-inf")
        self._reset_run()

    def _reset_run(self) -> None:
        self._run, self._emitted = [], False


@dataclass
class Sign:
    """解碼器輸出的一個詞。mode：segment（整段分類）／spot（窗口偵測）。"""
    start: float
    end: float
    prediction: Prediction
    frames: int
    mode: str


class SignDecoder:
    def __init__(self, classify: Callable[[np.ndarray], Prediction], segmenter: Segmenter,
                 spotter: Spotter | None = None, continuous_after: float = 3.5,
                 spot_classify: Callable[[np.ndarray], Prediction] | None = None):
        """classify：單字整段分類；spot_classify：窗口偵測（可換成有背景類的模型，預設同 classify）。"""
        self.classify, self.segmenter, self.spotter = classify, segmenter, spotter
        self.spot_classify = spot_classify or classify
        self.continuous_after = continuous_after
        self.continuous = False
        self._pending: list[Sign] = []

    @property
    def active(self) -> bool:
        return self.segmenter.active

    def push(self, t: float, frame: np.ndarray) -> list[Sign]:
        out: list[Sign] = []
        if self.spotter is not None:
            win = self.spotter.push(t, frame)
            if win is not None:
                hit = self.spotter.update(win[0], t, self.spot_classify(win[1]))
                if hit is not None:
                    sign = Sign(hit[0], hit[1], hit[2], len(win[1]), "spot")
                    (out if self.continuous else self._pending).append(sign)
        segment = self.segmenter.push(t, frame)
        if (self.spotter is not None and not self.continuous and self.segmenter.active
                and t - self.segmenter.started > self.continuous_after):
            self.continuous = True
            out += self._pending
            self._pending = []
        if segment is not None:
            out += self._on_segment(segment)
        return out

    def flush(self) -> list[Sign]:
        segment = self.segmenter.flush()
        out = self._on_segment(segment) if segment is not None else []
        if self.spotter is not None:
            self.spotter.reset()
        self.continuous = False
        return out

    def _on_segment(self, segment: np.ndarray) -> list[Sign]:
        a, b = self.segmenter.last_span
        if self.continuous:
            # 連續比劃中被單詞上限切開不算結束；手真的放下（或 flush）才回到單字模式
            if self.segmenter.last_reason != "max":
                self.continuous = False
            self._pending = []
            return []
        self._pending = []
        return [Sign(a, b, self.classify(segment), len(segment), "segment")]
