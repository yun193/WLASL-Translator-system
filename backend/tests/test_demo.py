import shutil

import pytest
from fastapi.testclient import TestClient

from app import config, demo

ORIGIN = {"origin": f"http://127.0.0.1:{config.PORT}"}


@pytest.fixture(scope="module")
def client():
    from app.main import app

    return TestClient(app, base_url=f"http://127.0.0.1:{config.PORT}")


def test_index_covers_live_vocabulary():
    """上線模型的每個詞都要有示範影片。"""
    if config.MODEL_DIR is None:
        pytest.skip("models/ 底下沒有模型")
    from app.inference import Classifier

    labels = [x for x in Classifier(config.MODEL_DIR).labels if x != "_bg"]
    assert all(demo.INDEX.get(x) for x in labels)
    assert all(row[0].isdigit() for rows in demo.INDEX.values() for row in rows)


def test_list_and_bad_requests(client):
    r = client.get("/api/demo/hello", headers=ORIGIN)
    assert r.status_code == 200 and r.json()["items"][0]["index"] == 0
    assert client.get("/api/demo/not-a-word", headers=ORIGIN).status_code == 404
    for bad in ("-1", "99", "x"):
        assert client.get(f"/api/demo/hello/{bad}", headers=ORIGIN).status_code in (404, 422)
    assert client.get("/api/demo/..%2F..%2Fsecret/0", headers=ORIGIN).status_code == 404


@pytest.mark.skipif(shutil.which("kaggle") is None, reason="需要 kaggle CLI 與網路")
def test_fetch_from_kaggle_and_cache(client):
    first = client.get("/api/demo/hello/0", headers=ORIGIN)
    assert first.status_code == 200 and first.headers["content-type"] == "video/mp4" and len(first.content) > 1000
    vid = demo.INDEX["hello"][0][0]
    assert (demo.CACHE_DIR / f"{vid}.mp4").is_file()
    assert client.get("/api/demo/hello/0", headers=ORIGIN).content == first.content
