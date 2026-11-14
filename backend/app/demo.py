"""詞彙表的示範影片：點詞時才從 Kaggle wlasl-processed 抓那一支，本機只留小快取。

- 索引 demo_index.json（scripts/build_demo_index.py 產生）：詞 → [影片編號, 起點秒, 終點秒或 None]
- 抓檔用本機已登入的 kaggle CLI（`kaggle datasets download -f videos/<id>.mp4`），不另外存憑證
- 快取在 data/demo_cache/，超過 DEMO_CACHE_MB 就刪最久沒看的
- 影片編號只從索引取，不接受使用者輸入的路徑
"""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

from . import config

DATASET = "risangbaskoro/wlasl-processed"
INDEX: dict[str, list[list]] = json.loads((Path(__file__).with_name("demo_index.json")).read_text(encoding="utf-8"))
CACHE_DIR = config.ROOT_DIR / "data" / "demo_cache"
CACHE_BYTES = int(os.environ.get("WLASL_DEMO_CACHE_MB", "200")) * 1024 * 1024
DOWNLOAD_TIMEOUT = 60
_locks: dict[str, asyncio.Lock] = {}


class DemoError(Exception):
    pass


def items(gloss: str) -> list[dict] | None:
    rows = INDEX.get(gloss)
    return None if rows is None else [{"index": i, "start": s, "end": e} for i, (_, s, e) in enumerate(rows)]


def _download(video_id: str) -> Path:
    exe = shutil.which("kaggle")
    if exe is None:
        raise DemoError("本機找不到 kaggle CLI")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CACHE_DIR / f".dl-{video_id}"
    tmp.mkdir(exist_ok=True)
    try:
        r = subprocess.run([exe, "datasets", "download", DATASET, "-f", f"videos/{video_id}.mp4", "-p", str(tmp), "-q"],
                           capture_output=True, timeout=DOWNLOAD_TIMEOUT)
        got = tmp / f"{video_id}.mp4"
        packed = tmp / f"{video_id}.mp4.zip"
        if not got.is_file() and packed.is_file():  # 大檔 Kaggle 會包成 zip
            with zipfile.ZipFile(packed) as z:
                z.extract(f"{video_id}.mp4", tmp)
        if not got.is_file():
            raise DemoError("無法從 Kaggle 取得影片（網路或 Kaggle 登入有問題）" + (f"：{r.stderr.decode(errors='ignore')[-200:]}" if r.returncode else ""))
        dst = CACHE_DIR / f"{video_id}.mp4"
        got.replace(dst)
        return dst
    except subprocess.TimeoutExpired as exc:
        raise DemoError("從 Kaggle 下載逾時") from exc
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _prune(keep: Path) -> None:
    files = sorted((p for p in CACHE_DIR.glob("*.mp4") if p != keep), key=lambda p: p.stat().st_mtime)
    total = sum(p.stat().st_size for p in files) + keep.stat().st_size
    for p in files:
        if total <= CACHE_BYTES:
            break
        total -= p.stat().st_size
        p.unlink(missing_ok=True)


async def video_path(gloss: str, index: int) -> Path:
    """回傳快取裡的影片路徑，沒有就先從 Kaggle 抓。gloss／index 不合法時 KeyError／IndexError。"""
    rows = INDEX[gloss]
    if not 0 <= index < len(rows):
        raise IndexError(index)
    video_id = rows[index][0]
    path = CACHE_DIR / f"{video_id}.mp4"
    async with _locks.setdefault(video_id, asyncio.Lock()):
        if not path.is_file():
            path = await asyncio.to_thread(_download, video_id)
            await asyncio.to_thread(_prune, path)
    os.utime(path)  # 最近看過的留著
    return path
