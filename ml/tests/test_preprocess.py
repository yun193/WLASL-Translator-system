import json

from wlasl.preprocess import build_manifest


def test_build_manifest_keeps_existing_videos_and_maps_gloss(tmp_path):
    (tmp_path / "videos").mkdir()
    (tmp_path / "videos" / "00001.mp4").write_bytes(b"")
    nslt = {"00001": {"subset": "train", "action": [1, 1, 40]},
            "00002": {"subset": "test", "action": [0, 1, 30]}}
    wlasl = [{"gloss": "book"}, {"gloss": "drink"}, {"gloss": "extra"}]
    (tmp_path / "nslt_2.json").write_text(json.dumps(nslt))
    (tmp_path / "WLASL_v0.3.json").write_text(json.dumps(wlasl))

    items, labels = build_manifest(tmp_path, subset=2)

    assert labels == ["book", "drink"]
    assert [i["video_id"] for i in items] == ["00001"]
    assert items[0]["gloss"] == "drink" and items[0]["end"] == 40
