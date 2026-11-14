"""產生示範影片索引 backend/app/demo_index.json：每個詞 → Kaggle wlasl-processed 裡的影片（最多 6 支）。

來源是前處理產出的 data/kaggle_out/wlasl-prep-*/index.json（只含 Kaggle 上真的有的 11,980 支）。
索引只有影片編號和起訖時間，影片本身在使用者點詞時才由後端從 Kaggle 抓（backend/app/demo.py）。
排序：手出現比例高的在前（比較像字典式的單詞示範），同分取片段較短的。

    uv run --project backend python scripts/build_demo_index.py
"""
import glob
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PER_GLOSS = 6

rows = [r for f in sorted(glob.glob(str(ROOT / "data/kaggle_out/wlasl-prep-*/index.json")))
        for r in json.loads(Path(f).read_text(encoding="utf-8"))]
by = defaultdict(list)
for r in rows:
    end = r["end"] if r["end"] > 0 else r["frames"]
    by[r["gloss"]].append((-round(r["hand_ratio"], 2), end - r["start"], r))
out = {}
for gloss, items in sorted(by.items()):
    out[gloss] = [[r["video_id"], round((r["start"] - 1) / r["fps"], 2), round(r["end"] / r["fps"], 2) if r["end"] > 0 else None]
                  for _, _, r in sorted(items, key=lambda t: t[:2])[:PER_GLOSS]]
dst = ROOT / "backend/app/demo_index.json"
dst.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(len(out), "詞", sum(map(len, out.values())), "支", f"{dst.stat().st_size / 1024:.0f} KB")
