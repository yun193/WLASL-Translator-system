from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app import config

ROOT = Path(__file__).resolve().parents[2]
VIDEOS = ROOT / "data" / "test_videos"
needs_data = pytest.mark.skipif(config.MODEL_DIR is None or not VIDEOS.is_dir(), reason="需要模型與 data/test_videos")


@pytest.fixture(scope="module")
def classifier():
    from app.inference import Classifier

    return Classifier(config.MODEL_DIR)


@needs_data
def test_analyze_is_deterministic(classifier):
    """同一支影片分析兩次，切詞與機率要完全相同（即時串流做不到這點）。"""
    from app.analyze import analyze_video

    a = analyze_video(VIDEOS / "00634.mp4", classifier)
    b = analyze_video(VIDEOS / "00634.mp4", classifier)
    def strip(signs):  # infer_ms 是計時，本來就每次不同
        return [{k: v for k, v in x.items() if k != "infer_ms"} for x in signs]

    assert strip(a["signs"]) == strip(b["signs"]) and len(a["signs"]) == 1
    assert a["frames"] == len(a["track"]) and a["signs"][0]["start"] < a["signs"][0]["end"]


@needs_data
def test_analyze_matches_offline_reference(classifier):
    """逐幀分析單字影片，應切出一個詞，且多數和 Kaggle 匯出時的 PyTorch 預測相同。

    不要求 100%：本機與 Kaggle 的 MediaPipe 有 20% 影片在門檻邊緣的手部偵測不同；
    上傳的是整支影片，Kaggle 端依 nslt 截掉了片尾。
    """
    from app.analyze import analyze_video

    ref = np.load(config.MODEL_DIR / "reference.npz")
    same = one_word = total = 0
    for vid, logits in list(zip(ref["video_ids"], ref["logits"]))[:10]:
        signs = analyze_video(VIDEOS / f"{vid}.mp4", classifier)["signs"]
        total += 1
        one_word += len(signs) == 1
        same += bool(signs) and signs[0]["gloss"] == classifier.labels[int(logits.argmax())]
    assert one_word >= 9, f"切成一個詞 {one_word}/{total}"
    assert same >= 7, f"和參考預測相同 {same}/{total}"


@pytest.fixture(scope="module")
def client():
    from app.main import app

    return TestClient(app, base_url=f"http://127.0.0.1:{config.PORT}")


@pytest.mark.skipif(config.MODEL_DIR is None, reason="models/ 底下沒有模型")
class TestAnalyzeHttp:
    origin = {"origin": f"http://127.0.0.1:{config.PORT}"}

    def test_rejects_cross_site(self, client):
        r = client.post("/api/analyze", content=b"x", headers={"origin": "https://evil.example", "content-type": "video/mp4"})
        assert r.status_code == 403

    def test_rejects_non_video(self, client):
        r = client.post("/api/analyze", content=b"x", headers={**self.origin, "content-type": "text/plain"})
        assert r.status_code == 415

    def test_rejects_garbage_video(self, client):
        r = client.post("/api/analyze", content=b"not a video" * 10, headers={**self.origin, "content-type": "video/mp4"})
        assert r.status_code == 422

    @needs_data
    def test_roundtrip(self, client):
        data = (VIDEOS / "00634.mp4").read_bytes()
        r = client.post("/api/analyze", content=data, headers={**self.origin, "content-type": "video/mp4"})
        assert r.status_code == 200
        body = r.json()
        assert len(body["signs"]) == 1 and len(body["track"][0]["points"]) == 55
