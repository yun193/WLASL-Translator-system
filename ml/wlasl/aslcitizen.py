"""ASL Citizen 影片 → 關鍵點（Kaggle CPU 端執行），格式和 wlasl.preprocess 相同，訓練時直接併進 index。

只取 gloss 和 WLASL labels 完全同名（不分大小寫）的影片；變體詞（DRINK1／DRINK2）不收。
影片不整包下載：用 HTTP Range 讀官方 zip 的目錄，每支影片只抓自己那一段，擷取完就刪。
授權（Microsoft Research License）只限非商業研究、不得散布：產出只放私人 kernel 輸出，不上傳成 Dataset。

index 每筆：video_id = "aslc-<檔名>"、subset 一律 "train"（ASL Citizen test 留給本機驗收，不收）、
start/end = 1/-1（整支都是這個詞）、signer、aslc_split（原本是 train 還是 val）。

用法：python -m wlasl.aslcitizen --labels <WLASL labels.json> --out <輸出> --workers 4 [--shard 0 --shards 6]
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import struct
import time
import urllib.request
import zipfile
import zlib
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from wlasl.landmarks import ensure_model
from wlasl.preprocess import _work

URL = "https://download.microsoft.com/download/b/8/8/b88c0bae-e6c1-43e1-8726-98cf5af36ca4/ASL_Citizen.zip"
SPLITS = ("train", "val")


def _get(url: str, start: int, end: int) -> bytes:
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
    for attempt in range(6):  # 微軟下載站偶爾逾時
        try:
            return urllib.request.urlopen(req, timeout=60).read()
        except OSError:
            if attempt == 5:
                raise
            time.sleep(2**attempt)
    raise AssertionError


class HttpFile(io.RawIOBase):
    """唯讀、可 seek 的遠端檔案，只給 zipfile 讀目錄用。"""

    def __init__(self, url: str):
        self.url, self.pos = url, 0
        self.size = int(urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=60)
                        .headers["Content-Length"])

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = {0: off, 1: self.pos + off, 2: self.size + off}[whence]
        return self.pos

    def readinto(self, b):
        if self.pos >= self.size or len(b) == 0:
            return 0
        data = _get(self.url, self.pos, min(self.pos + len(b), self.size) - 1)
        b[: len(data)] = data
        self.pos += len(data)
        return len(data)


def fetch(url: str, entry: dict) -> bytes:
    """依目錄裡的位置抓一個 zip 成員（不靠共用的 ZipFile，每個 worker 可以各自抓）。"""
    head = _get(url, entry["offset"], entry["offset"] + 29)
    sig, *_, name_len, extra_len = struct.unpack("<IHHHHHIIIHH", head)
    assert sig == 0x04034B50, "不是 zip local header"
    start = entry["offset"] + 30 + name_len + extra_len
    data = _get(url, start, start + entry["csize"] - 1)
    if entry["method"] == zipfile.ZIP_DEFLATED:
        data = zlib.decompress(data, -15)
    assert len(data) == entry["size"], "長度不符"
    return data


def video_id(name: str) -> str:
    return "aslc-" + Path(name).stem.replace(" ", "_")


def build_manifest(splits: dict[str, list[dict]], labels: list[str]) -> list[dict]:
    """ASL Citizen 切分 CSV 的列 → index 項目（label 用 WLASL 的編號）。"""
    pos = {g: i for i, g in enumerate(labels)}
    items = []
    for sp in SPLITS:
        for r in splits[sp]:
            g = r["Gloss"].lower()
            if g in pos:
                items.append({"video_id": video_id(r["Video file"]), "label": pos[g], "gloss": g, "subset": "train",
                              "start": 1, "end": -1, "signer": r["Participant ID"], "aslc_split": sp,
                              "file": r["Video file"]})
    return sorted(items, key=lambda it: it["video_id"])


def _fetch_work(item: dict, entry: dict, url: str, tmp: str, out_dir: str, model_path: str) -> dict:
    path = Path(tmp) / f"{item['video_id']}.mp4"
    try:
        path.write_bytes(fetch(url, entry))
    except Exception as e:
        return {**item, "path": "", "error": f"下載 {type(e).__name__}: {e}"}
    try:
        return _work({**item, "path": str(path)}, out_dir, model_path)
    finally:
        path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", type=Path, required=True, help="WLASL labels.json（決定 label 編號）")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--model", type=Path, default=Path("/tmp/holistic_landmarker.task"))
    ap.add_argument("--tmp", type=Path, default=Path("/tmp/aslc_videos"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--url", default=URL)
    args = ap.parse_args(argv)

    labels = json.loads(args.labels.read_text(encoding="utf-8"))
    z = zipfile.ZipFile(io.BufferedReader(HttpFile(args.url), 1 << 20))
    splits = {sp: list(csv.DictReader(io.TextIOWrapper(z.open(f"ASL_Citizen/splits/{sp}.csv"), encoding="utf-8")))
              for sp in SPLITS}
    entries = {Path(i.filename).name: {"offset": i.header_offset, "csize": i.compress_size, "size": i.file_size,
                                       "method": i.compress_type}
               for i in z.infolist() if i.filename.startswith("ASL_Citizen/videos/")}
    items = build_manifest(splits, labels)[args.shard :: args.shards]
    if args.limit:
        items = items[: args.limit]

    kp_dir = args.out / "keypoints"
    kp_dir.mkdir(parents=True, exist_ok=True)
    args.tmp.mkdir(parents=True, exist_ok=True)
    model = str(ensure_model(args.model))
    (args.out / "labels.json").write_text(json.dumps(labels, ensure_ascii=False, indent=1), encoding="utf-8")
    index_path = args.out / "index.json"
    done = {r["video_id"]: r for r in json.loads(index_path.read_text())} if index_path.exists() else {}
    todo = [it for it in items if it["video_id"] not in done or not (kp_dir / f"{it['video_id']}.npy").exists()]
    print(f"共 {len(items)} 支，已完成 {len(items) - len(todo)}，待處理 {len(todo)}", flush=True)

    failed, t0 = [], time.time()
    with ProcessPoolExecutor(args.workers) as pool:
        futs = [pool.submit(_fetch_work, it, entries[it["file"]], args.url, str(args.tmp), str(kp_dir), model)
                for it in todo]
        for n, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            r.pop("path")
            if "error" in r:
                failed.append(r)
            else:
                done[r["video_id"]] = r
            if n % 100 == 0 or n == len(futs):
                print(f"{n}/{len(futs)}  {time.time() - t0:.0f}s  失敗 {len(failed)}", flush=True)
                index_path.write_text(json.dumps(sorted(done.values(), key=lambda r: r["video_id"]), indent=1))

    index_path.write_text(json.dumps(sorted(done.values(), key=lambda r: r["video_id"]), indent=1))
    (args.out / "failed.json").write_text(json.dumps(failed, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"完成：成功 {len(done)}、失敗 {len(failed)}", flush=True)


if __name__ == "__main__":
    main()
