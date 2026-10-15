import json
import struct
from pathlib import Path

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app import config
from app.stream import FrameError, decode_frame

ROOT = Path(__file__).resolve().parents[2]
PRE = ROOT / "data" / "kaggle_out" / "preprocess"
needs_model = pytest.mark.skipif(config.MODEL_DIR is None, reason="models/ 底下沒有模型")


def jpeg_frame(ts_ms: float, h=480, w=640) -> bytes:
    img = np.full((h, w, 3), 128, dtype=np.uint8)
    ok, buf = cv2.imencode(".jpg", img)
    return struct.pack("<d", ts_ms) + buf.tobytes()


def test_decode_frame_rejects_garbage():
    with pytest.raises(FrameError):
        decode_frame(b"\x00" * 4)
    with pytest.raises(FrameError):
        decode_frame(struct.pack("<d", 1.0) + b"not a jpeg")
    with pytest.raises(FrameError):
        decode_frame(struct.pack("<d", float("nan")) + b"x")
    ts, frame = decode_frame(jpeg_frame(12.5))
    assert ts == 12.5 and frame.shape == (480, 640, 3)


@needs_model
def test_classifier_matches_reference_predictions():
    """後端分類器對 test 原始關鍵點的預測，要和 Kaggle 匯出時的 PyTorch 預測一致。"""
    from app.inference import Classifier

    clf = Classifier(config.MODEL_DIR)
    ref = np.load(config.MODEL_DIR / "reference.npz")
    for vid, logits in list(zip(ref["video_ids"], ref["logits"]))[:20]:
        raw = np.load(PRE / "keypoints" / f"{vid}.npy")
        assert clf.predict(raw).gloss == clf.labels[int(logits.argmax())]


@pytest.fixture(scope="module")
def client():
    from app.main import app

    return TestClient(app, base_url=f"http://127.0.0.1:{config.PORT}")


@needs_model
class TestWebSocket:
    def headers(self, origin=None):
        # websocket_connect 不套用 base_url，Host 要自己帶
        host = f"127.0.0.1:{config.PORT}"
        return {"host": host, "origin": origin or f"http://{host}"}

    def test_health(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200 and r.json()["classes"] == 100

    def test_http_rejects_foreign_host(self, client):
        r = client.get("/api/health", headers={"host": "evil.example:8766"})
        assert r.status_code == 403

    def test_ws_rejects_foreign_or_missing_origin(self, client):
        host = f"127.0.0.1:{config.PORT}"
        for headers in ({"host": host, "origin": "https://evil.example"}, {"host": host}):
            with pytest.raises(WebSocketDisconnect) as exc:
                with client.websocket_connect("/ws/stream", headers=headers) as ws:
                    ws.receive_json()
            assert exc.value.code == 1008

    def test_ws_frame_roundtrip_and_commands(self, client):
        with client.websocket_connect("/ws/stream", headers=self.headers()) as ws:
            ws.send_bytes(jpeg_frame(0))
            e = ws.receive_json()
            assert e["type"] == "frame" and e["hands"] == [False, False] and len(e["points"]) == 55
            ws.send_bytes(b"bad")
            assert ws.receive_json()["type"] == "error"
            ws.send_text(json.dumps({"type": "reset"}))
            assert ws.receive_json()["type"] == "reset"
            ws.send_text("not json")
            assert ws.receive_json()["type"] == "error"

    def test_ws_only_one_session(self, client):
        with client.websocket_connect("/ws/stream", headers=self.headers()) as ws:
            ws.send_bytes(jpeg_frame(0))
            ws.receive_json()
            with pytest.raises(WebSocketDisconnect) as exc:
                with client.websocket_connect("/ws/stream", headers=self.headers()) as ws2:
                    ws2.receive_json()
            assert exc.value.code == 1013


VIDEOS = ROOT / "data" / "test_videos"


@needs_model
@pytest.mark.skipif(not VIDEOS.is_dir(), reason="需要 data/test_videos")
def test_session_end_to_end_on_real_video():
    """真實 test 影片以 10 fps、640 寬 JPEG 餵進 SignSession（和上線同一條路徑），要切出詞且 top-5 命中。"""
    from app.inference import Classifier
    from app.stream import SignSession

    clf = Classifier(config.MODEL_DIR)
    ref = np.load(config.MODEL_DIR / "reference.npz")
    hits = total = 0
    for vid, label, logits in list(zip(ref["video_ids"], ref["labels"], ref["logits"]))[:10]:
        cap = cv2.VideoCapture(str(VIDEOS / f"{vid}.mp4"))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        session, signs, i = SignSession(clf), [], 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if i % max(1, round(fps / 10)) == 0:
                frame = cv2.resize(frame, (640, round(640 * frame.shape[0] / frame.shape[1])))
                data = struct.pack("<d", i * 1000 / fps) + cv2.imencode(".jpg", frame)[1].tobytes()
                signs += [e for e in session.handle_frame(data) if e["type"] == "sign"]
            i += 1
        signs += session.flush()
        session.close()
        cap.release()
        total += 1
        hits += any(clf.labels[int(label)] in [t["gloss"] for t in s["top5"]] for s in signs)
    assert hits / total >= 0.6, f"top-5 命中 {hits}/{total}"
