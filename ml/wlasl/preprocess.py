"""WLASL 影片 → 關鍵點 .npy（Kaggle CPU 端執行）。

輸出目錄：
  keypoints/<video_id>.npy   (T, K, 3) float32，未正規化，缺點為 NaN；整支影片（不截 nslt 起訖）
  index.json                 每支影片的 label / gloss / subset / fps / 幀數，start / end 是 nslt 人工標註起訖
  labels.json                第 i 類的 gloss
  failed.json                擷取失敗的影片與原因
已存在的 .npy 會跳過，中斷後可以接著跑。

擷取整支影片，是為了讓訓練能取到標註起訖之外的幀（上線時切詞器常多包進手放下的動作）。
WLASL2000 約 1.2 萬支，單一 Kaggle kernel 要 8 小時，用 --shard i --shards n 拆給多個 kernel 平行跑。

用法：python -m wlasl.preprocess --root <WLASL 資料夾> --out <輸出> --subset 2000 --workers 4 [--shard 0 --shards 4]
"""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from wlasl.landmarks import N_POSE, ensure_model, extract_video


def build_manifest(root: Path, subset: int) -> tuple[list[dict], list[str]]:
    """讀 nslt_<subset>.json 與 WLASL_v0.3.json，只留影片檔實際存在的項目。"""
    nslt = json.loads((root / f"nslt_{subset}.json").read_text(encoding="utf-8"))
    wlasl = json.loads((root / "WLASL_v0.3.json").read_text(encoding="utf-8"))
    # nslt 的類別編號就是 WLASL_v0.3.json 的 gloss 順序
    labels = [e["gloss"] for e in wlasl[:subset]]
    items = []
    for vid, v in sorted(nslt.items()):
        path = root / "videos" / f"{vid}.mp4"
        if not path.exists():
            continue
        label, start, end = v["action"]
        items.append(
            {"video_id": vid, "label": label, "gloss": labels[label], "subset": v["subset"],
             "start": start, "end": end, "path": str(path)}
        )
    return items, labels


def _work(item: dict, out_dir: str, model_path: str) -> dict:
    dst = Path(out_dir) / f"{item['video_id']}.npy"
    try:
        seq, fps = extract_video(item["path"], model_path)
        if len(seq) == 0:
            raise ValueError("讀不到任何幀")
        np.save(dst, seq)
        hands = ~np.isnan(seq[:, N_POSE:, 0]).all(1)
        end = len(seq) if item["end"] == -1 else min(item["end"], len(seq))
        return {**item, "fps": fps, "frames": len(seq),
                "hand_ratio": float(hands[item["start"] - 1 : end].mean()) if end >= item["start"] else 0.0}
    except Exception as e:  # 單支影片失敗不影響整批
        return {**item, "error": f"{type(e).__name__}: {e}"}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True, help="含 videos/ 與 nslt_*.json 的資料夾")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--subset", type=int, default=100)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--model", type=Path, default=Path("/tmp/holistic_landmarker.task"))
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 支（試跑用）")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    args = ap.parse_args(argv)

    kp_dir = args.out / "keypoints"
    kp_dir.mkdir(parents=True, exist_ok=True)
    model = str(ensure_model(args.model))
    items, labels = build_manifest(args.root, args.subset)
    items = items[args.shard :: args.shards]
    if args.limit:
        items = items[: args.limit]
    (args.out / "labels.json").write_text(json.dumps(labels, ensure_ascii=False, indent=1), encoding="utf-8")

    index_path = args.out / "index.json"
    done = {r["video_id"]: r for r in json.loads(index_path.read_text())} if index_path.exists() else {}
    todo = [it for it in items if it["video_id"] not in done or not (kp_dir / f"{it['video_id']}.npy").exists()]
    print(f"共 {len(items)} 支，已完成 {len(items) - len(todo)}，待處理 {len(todo)}", flush=True)

    failed, t0 = [], time.time()
    with ProcessPoolExecutor(args.workers) as pool:
        futs = [pool.submit(_work, it, str(kp_dir), model) for it in todo]
        for n, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            r.pop("path")
            if "error" in r:
                failed.append(r)
            else:
                done[r["video_id"]] = r
            if n % 50 == 0 or n == len(futs):
                print(f"{n}/{len(futs)}  {time.time() - t0:.0f}s  失敗 {len(failed)}", flush=True)
                index_path.write_text(json.dumps(sorted(done.values(), key=lambda r: r["video_id"]), indent=1))

    index_path.write_text(json.dumps(sorted(done.values(), key=lambda r: r["video_id"]), indent=1))
    (args.out / "failed.json").write_text(json.dumps(failed, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"完成：成功 {len(done)}、失敗 {len(failed)}", flush=True)


if __name__ == "__main__":
    main()
