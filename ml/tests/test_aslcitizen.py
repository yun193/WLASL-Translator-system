import io
import zipfile

from wlasl import aslcitizen as ac


def test_manifest_exact_match_and_no_test_split():
    rows = lambda sp: [{"Participant ID": f"P{sp}", "Video file": f"1-{g}.mp4", "Gloss": g} for g in ("BOOK", "DRINK1", "Chair")]
    items = ac.build_manifest({"train": rows("1"), "val": rows("2"), "test": rows("3")}, ["book", "drink", "chair"])
    assert sorted((it["gloss"], it["label"], it["aslc_split"]) for it in items) == [
        ("book", 0, "train"), ("book", 0, "val"), ("chair", 2, "train"), ("chair", 2, "val")]
    assert {it["signer"] for it in items} == {"P1", "P2"}  # test 的手語者不收
    assert all(it["subset"] == "train" and it["start"] == 1 and it["end"] == -1 for it in items)


def test_video_id_has_no_spaces():
    assert ac.video_id("8006032738002744-SOCCER 2.mp4") == "aslc-8006032738002744-SOCCER_2"


def test_fetch_reads_member_by_offset(monkeypatch):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("ASL_Citizen/videos/a.mp4", b"x" * 1000, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("ASL_Citizen/videos/b.mp4", b"hello", compress_type=zipfile.ZIP_STORED)
    raw = buf.getvalue()
    monkeypatch.setattr(ac, "_get", lambda url, s, e: raw[s : e + 1])
    for i in zipfile.ZipFile(io.BytesIO(raw)).infolist():
        e = {"offset": i.header_offset, "csize": i.compress_size, "size": i.file_size, "method": i.compress_type}
        assert ac.fetch("u", e) == (b"x" * 1000 if i.filename.endswith("a.mp4") else b"hello")
