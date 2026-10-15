"""一條鏡頭串流的狀態：影格 → MediaPipe → 切詞 → 分類。不依賴 WebSocket，方便單獨測試。

協定（WebSocket）：
  前端 → 後端  binary：前 8 bytes 為 float64（little-endian）擷取時間 ms，其後是 JPEG
               text  ：{"type": "flush"} 立刻結束目前的詞；{"type": "reset"} 清空狀態
  後端 → 前端  {"type": "frame", ...}：每幀一則，前端收到才送下一幀（一來一回 = 自然背壓）
               {"type": "sign", ...} ：切出一個詞時送出
"""
from __future__ import annotations

import struct
import time

import numpy as np
from wlasl.landmarks import LEFT_HAND, RIGHT_HAND, LandmarkExtractor

from . import config
from .inference import Classifier
from .segmenter import Segmenter

HEADER = struct.Struct("<d")


class FrameError(ValueError):
    pass


def decode_frame(data: bytes) -> tuple[float, np.ndarray]:
    import cv2

    if len(data) <= HEADER.size or len(data) > config.MAX_FRAME_BYTES:
        raise FrameError("影格大小不正確")
    (ts_ms,) = HEADER.unpack_from(data)
    if not np.isfinite(ts_ms):
        raise FrameError("時間戳不正確")
    buf = np.frombuffer(data, dtype=np.uint8, offset=HEADER.size)
    frame = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if frame is None:
        raise FrameError("無法解碼影格（需為 JPEG / PNG）")
    if frame.shape[0] * frame.shape[1] > config.MAX_FRAME_PIXELS:
        raise FrameError("影格解析度過大")
    return ts_ms, frame


def _points(raw: np.ndarray, aspect: float) -> list:
    """給前端畫骨架：還原成 0～1 的影像座標，缺點為 None。"""
    xy = raw[:, :2].astype(float)
    xy[:, 0] /= aspect
    return [None if np.isnan(p).any() else [round(p[0], 4), round(p[1], 4)] for p in xy]


class SignSession:
    def __init__(self, classifier: Classifier, extractor: LandmarkExtractor | None = None):
        self.classifier = classifier
        self.extractor = extractor or LandmarkExtractor(config.MP_MODEL)
        self.segmenter = self._new_segmenter()
        self._last_ts = -1

    @staticmethod
    def _new_segmenter() -> Segmenter:
        return Segmenter(rest=config.REST_SECONDS, pre_roll=config.PRE_ROLL_SECONDS,
                         min_len=config.MIN_SIGN_SECONDS, max_len=config.MAX_SIGN_SECONDS)

    def close(self) -> None:
        self.extractor.close()

    def reset(self) -> None:
        self.segmenter = self._new_segmenter()

    def handle_frame(self, data: bytes) -> list[dict]:
        ts_ms, frame = decode_frame(data)
        return self.process(ts_ms, frame)

    def process(self, ts_ms: float, frame: np.ndarray) -> list[dict]:
        """一幀 BGR 影像 → [frame 事件, (切出詞時) sign 事件]；串流與影片檔分析共用。"""
        # MediaPipe VIDEO 模式要求時間戳嚴格遞增
        ts = max(int(ts_ms), self._last_ts + 1)
        self._last_ts = ts
        t0 = time.perf_counter()
        raw = self.extractor.process(frame, ts)
        mp_ms = (time.perf_counter() - t0) * 1000
        segment = self.segmenter.push(ts / 1000, raw)
        events = [{
            "type": "frame",
            "hands": [bool(~np.isnan(raw[LEFT_HAND, 0]).all()), bool(~np.isnan(raw[RIGHT_HAND, 0]).all())],
            "active": self.segmenter.active,
            "mp_ms": round(mp_ms, 1),
            "points": _points(raw, frame.shape[1] / frame.shape[0]),
        }]
        if segment is not None:
            events.append(self._classify(segment))
        return events

    def flush(self) -> list[dict]:
        segment = self.segmenter.flush()
        return [self._classify(segment)] if segment is not None else []

    def _classify(self, segment: np.ndarray) -> dict:
        t0 = time.perf_counter()
        p = self.classifier.predict(segment)
        return {
            "type": "sign",
            "gloss": p.gloss,
            "prob": round(p.prob, 4),
            "confident": p.prob >= config.MIN_CONFIDENCE,
            "top5": [{"gloss": g, "prob": round(pr, 4)} for g, pr in p.top5],
            "frames": int(len(segment)),
            "start": round(self.segmenter.last_span[0], 3),
            "end": round(self.segmenter.last_span[1], 3),
            "infer_ms": round((time.perf_counter() - t0) * 1000, 2),
        }
