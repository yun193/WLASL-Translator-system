"""MediaPipe 關鍵點擷取與正規化：訓練（Kaggle）與即時推論（本機）共用的唯一來源。

一幀的輸出固定是 (K, 3) float32，K = 13 個上半身姿勢點 + 左手 21 + 右手 21。
x 已乘上影像寬高比，讓 x、y 同一個尺度；偵測不到的點填 NaN。
存檔一律存未正規化的原始座標，正規化在讀取時做，改正規化方式不必重跑擷取。
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

import numpy as np

# Pose 33 點中只取上半身：鼻、眼、耳、嘴角、肩、肘、腕
POSE_IDX = (0, 2, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
N_POSE = len(POSE_IDX)
N_HAND = 21
K = N_POSE + 2 * N_HAND

POSE = slice(0, N_POSE)
LEFT_HAND = slice(N_POSE, N_POSE + N_HAND)
RIGHT_HAND = slice(N_POSE + N_HAND, K)

# 肩膀在 POSE_IDX 裡的位置（pose 11、12）
L_SHOULDER = POSE_IDX.index(11)
R_SHOULDER = POSE_IDX.index(12)

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/holistic_landmarker/"
    "holistic_landmarker/float16/latest/holistic_landmarker.task"
)


def ensure_model(path: str | Path) -> Path:
    """模型檔不存在就下載，回傳路徑。"""
    path = Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, path)
    return path


def _fill(out: np.ndarray, landmarks, idx, aspect: float) -> None:
    if not landmarks:
        return
    pts = np.array([(p.x * aspect, p.y, p.z * aspect) for p in landmarks], dtype=np.float32)
    out[:] = pts if idx is None else pts[list(idx)]


def result_to_array(result, aspect: float) -> np.ndarray:
    """HolisticLandmarkerResult → (K, 3)；aspect = 寬 / 高。"""
    out = np.full((K, 3), np.nan, dtype=np.float32)
    _fill(out[POSE], result.pose_landmarks, POSE_IDX, aspect)
    _fill(out[LEFT_HAND], result.left_hand_landmarks, None, aspect)
    _fill(out[RIGHT_HAND], result.right_hand_landmarks, None, aspect)
    return out


class LandmarkExtractor:
    """VIDEO 模式的 HolisticLandmarker；時間戳必須遞增，所以一段影片 / 一條串流用一個實例。"""

    def __init__(self, model_path: str | Path):
        from mediapipe.tasks.python import BaseOptions, vision

        options = vision.HolisticLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(ensure_model(model_path))),
            running_mode=vision.RunningMode.VIDEO,
        )
        self._landmarker = vision.HolisticLandmarker.create_from_options(options)

    def process(self, frame_bgr: np.ndarray, timestamp_ms: int) -> np.ndarray:
        import cv2
        import mediapipe as mp

        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        result = self._landmarker.detect_for_video(
            mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), timestamp_ms
        )
        return result_to_array(result, w / h)

    def close(self) -> None:
        self._landmarker.close()

    def __enter__(self) -> LandmarkExtractor:
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def extract_video(
    path: str | Path, model_path: str | Path, start: int = 1, end: int = -1
) -> tuple[np.ndarray, float]:
    """擷取影片第 start～end 幀（1 起算、含端點，end = -1 表示到結尾）→ ((T, K, 3), fps)。"""
    import cv2

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise OSError(f"無法開啟影片：{path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frames = []
    try:
        with LandmarkExtractor(model_path) as ext:
            i = 0
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                i += 1
                if i < start:
                    continue
                if end != -1 and i > end:
                    break
                frames.append(ext.process(frame, int((i - 1) * 1000 / fps)))
    finally:
        cap.release()
    seq = np.stack(frames) if frames else np.empty((0, K, 3), dtype=np.float32)
    return seq, float(fps)


def normalize(seq: np.ndarray) -> np.ndarray:
    """以整段的肩膀中點為原點、肩寬為單位長度；NaN 保留給後續補值或遮罩。

    用整段的中位數而不是逐幀計算，避免單幀偵測抖動讓整個骨架跟著跳。
    沒偵測到肩膀時退回用所有有效點的中心與標準差。
    """
    seq = np.asarray(seq, dtype=np.float32)
    ls, rs = seq[:, L_SHOULDER, :2], seq[:, R_SHOULDER, :2]
    valid = ~(np.isnan(ls).any(1) | np.isnan(rs).any(1))
    if valid.any():
        center = np.median((ls[valid] + rs[valid]) / 2, axis=0)
        scale = float(np.median(np.linalg.norm(ls[valid] - rs[valid], axis=1)))
    else:
        pts = seq[..., :2].reshape(-1, 2)
        pts = pts[~np.isnan(pts).any(1)]
        if len(pts) == 0:
            return seq.copy()
        center = pts.mean(0)
        scale = float(pts.std())
    scale = scale if scale > 1e-6 else 1.0
    out = seq.copy()
    out[..., :2] = (out[..., :2] - center) / scale
    out[..., 2] = out[..., 2] / scale
    return out
