"""一條鏡頭串流的狀態：影格 → MediaPipe → 解碼（切詞＋窗口偵測）→ 分類。不依賴 WebSocket，方便單獨測試。

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
from wlasl.segmenter import Segmenter
from wlasl.spotter import Sign, SignDecoder, Spotter

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
        self.decoder = new_decoder(classifier)
        self._last_ts = -1

    def close(self) -> None:
        self.extractor.close()

    def reset(self) -> None:
        self.decoder = new_decoder(self.classifier)

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
        t0 = time.perf_counter()
        signs = self.decoder.push(ts / 1000, raw)
        infer_ms = (time.perf_counter() - t0) * 1000
        events = [{
            "type": "frame",
            "hands": [bool(~np.isnan(raw[LEFT_HAND, 0]).all()), bool(~np.isnan(raw[RIGHT_HAND, 0]).all())],
            "active": self.decoder.active,
            "continuous": self.decoder.continuous,
            "mp_ms": round(mp_ms, 1),
            "points": _points(raw, frame.shape[1] / frame.shape[0]),
        }]
        return events + [sign_event(s, infer_ms) for s in signs]

    def flush(self) -> list[dict]:
        return [sign_event(s, 0.0) for s in self.decoder.flush()]


def new_decoder(classifier: Classifier) -> SignDecoder:
    seg = Segmenter(rest=config.REST_SECONDS, pre_roll=config.PRE_ROLL_SECONDS,
                    min_len=config.MIN_SIGN_SECONDS, max_len=config.MAX_SIGN_SECONDS)
    spot = (Spotter(window=config.SPOT_WINDOW, hop=config.SPOT_HOP, min_hits=config.SPOT_MIN_HITS,
                    threshold=config.SPOT_THRESHOLD) if config.SPOTTING else None)
    return SignDecoder(classifier.predict, seg, spot, continuous_after=config.CONTINUOUS_AFTER)


def sign_event(s: Sign, infer_ms: float) -> dict:
    p = s.prediction
    return {
        "type": "sign",
        "gloss": p.gloss,
        "prob": round(p.prob, 4),
        # 窗口偵測輸出的詞已經過門檻；整段分類則看信心與是否被判成背景
        "confident": p.prob >= config.MIN_CONFIDENCE and not p.is_background,
        "top5": [{"gloss": g, "prob": round(pr, 4)} for g, pr in p.top5],
        "background": round(p.background, 4),
        "mode": s.mode,
        "frames": int(s.frames),
        "start": round(s.start, 3),
        "end": round(s.end, 3),
        "infer_ms": round(infer_ms, 2),
    }
