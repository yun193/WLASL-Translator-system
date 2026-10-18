"""影片檔逐幀分析：每一幀都送進 MediaPipe，結果可重現。

即時串流受後端速度限制只能取到約 10 fps，而且每次播放抽到的幀不同，預測會隨抽幀相位翻盤
（10 fps 相位間一致率只有 80%）。影片檔沒有即時壓力，就用 cv2 以原生 fps 逐幀解碼，
和 Kaggle 前處理、本機驗證是同一條路徑。
"""
from __future__ import annotations

import time
from pathlib import Path

from . import config
from .inference import Classifier
from .stream import SignSession


class VideoError(ValueError):
    pass


def analyze_video(path: Path, classifier: Classifier, spot_classifier: Classifier | None = None) -> dict:
    import cv2

    cap = cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened():
            raise VideoError("無法讀取這支影片")
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0 or fps > 240:
            raise VideoError("讀不到影片的 fps")
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if n / fps > config.MAX_VIDEO_SECONDS:
            raise VideoError(f"影片太長（上限 {config.MAX_VIDEO_SECONDS:g} 秒）")

        t0 = time.perf_counter()
        session = SignSession(classifier, spot_classifier=spot_classifier)
        track, signs, i = [], [], 0
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                h, w = frame.shape[:2]
                if h > config.MAX_VIDEO_HEIGHT:
                    s = config.MAX_VIDEO_HEIGHT / h
                    frame = cv2.resize(frame, (round(w * s), config.MAX_VIDEO_HEIGHT), interpolation=cv2.INTER_AREA)
                events = session.process(i * 1000 / fps, frame)
                f = events[0]
                track.append({"t": round(i / fps, 4), "hands": f["hands"], "active": f["active"], "points": f["points"]})
                signs += events[1:]
                i += 1
            signs += session.flush()
        finally:
            session.close()
    finally:
        cap.release()
    if i == 0:
        raise VideoError("影片沒有任何可解碼的幀")
    return {"fps": round(fps, 3), "frames": i, "duration": round(i / fps, 3),
            "elapsed_s": round(time.perf_counter() - t0, 2), "signs": signs, "track": track}
