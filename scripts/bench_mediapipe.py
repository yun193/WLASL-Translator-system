"""MediaPipe 吞吐量基準（本機 CPU）：取樣 fps / 解析度對 test 準確率與每幀延遲的影響。

用法（repo 根目錄）：
  ml/.venv/Scripts/python.exe scripts/bench_mediapipe.py --model models/<run> --workers 4

模擬即時串流：依目標 fps 跳幀、時間戳照原影片時間，再走和上線相同的 prepare → ONNX(CPU)。
全幀那一組同時和 Kaggle 擷取的 .npy 比對，檢查 Windows 與 Linux 的 MediaPipe 是否一致。
結果寫到 models/<run>/report/bench_mediapipe.json。
"""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MP_MODEL = ROOT / "data" / "models" / "holistic_landmarker.task"


def extract(path: str, end: int, target_fps: float | None, max_h: int | None) -> tuple[np.ndarray, float]:
    """回傳 (T, K, 3) 與這支影片的平均每幀擷取毫秒。"""
    import cv2

    from wlasl.landmarks import LandmarkExtractor

    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frames, spent, i, last_slot = [], 0.0, 0, -1
    with LandmarkExtractor(MP_MODEL) as ext:
        while True:
            ok, frame = cap.read()
            if not ok or (end != -1 and i >= end):
                break
            if target_fps:
                slot = int(i * target_fps / fps)
                if slot == last_slot:
                    i += 1
                    continue
                last_slot = slot
            if max_h and frame.shape[0] > max_h:
                s = max_h / frame.shape[0]
                frame = cv2.resize(frame, (round(frame.shape[1] * s), max_h), interpolation=cv2.INTER_AREA)
            t = time.perf_counter()
            frames.append(ext.process(frame, int(i * 1000 / fps)))
            spent += time.perf_counter() - t
            i += 1
    cap.release()
    return np.stack(frames), spent * 1000 / max(1, len(frames))


def _job(args):
    return extract(*args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--data", type=Path, default=ROOT / "data" / "kaggle_out" / "preprocess")
    ap.add_argument("--videos", type=Path, default=ROOT / "data" / "test_videos")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    import onnxruntime as ort

    from wlasl.dataset import load_split, prepare, resample_mode
    from wlasl.evaluate import nan_aware_max_diff, topk_hits, wilson

    splits, _ = load_split(args.data)
    test = splits["test"]
    y = np.array([r["label"] for r in test])
    sess = ort.InferenceSession(str(args.model / "model.onnx"), providers=["CPUExecutionProvider"])

    configs = [("full", None, None), ("15fps", 15, None), ("10fps", 10, None), ("7.5fps", 7.5, None),
               ("15fps_360p", 15, 360)]
    results = {}
    for name, fps, max_h in configs:
        jobs = [(str(args.videos / f"{r['video_id']}.mp4"), r["end"], fps, max_h) for r in test]
        t0 = time.time()
        with ProcessPoolExecutor(args.workers) as pool:
            outs = list(pool.map(_job, jobs))
        x = np.stack([prepare(seq, mode=resample_mode(args.model)) for seq, _ in outs])
        logits = sess.run(None, {"keypoints": x})[0]
        h1, h5 = topk_hits(logits, y, 1), topk_hits(logits, y, 5)
        res = {"top1": float(h1.mean()), "top1_ci95": wilson(int(h1.sum()), len(y)), "top5": float(h5.mean()),
               "frames_mean": float(np.mean([len(s) for s, _ in outs])), "wall_s": round(time.time() - t0, 1)}
        if name == "full":
            diffs, nan_mismatch = [], 0
            for (seq, _), r in zip(outs, test):
                kg = np.load(args.data / "keypoints" / f"{r['video_id']}.npy")
                d = nan_aware_max_diff(seq, kg) if seq.shape == kg.shape else float("inf")
                nan_mismatch += int(not np.isfinite(d))
                if np.isfinite(d):
                    diffs.append(d)
            res["vs_kaggle"] = {"videos_nan_or_shape_mismatch": nan_mismatch,
                                "max_abs_diff_median": float(np.median(diffs)) if diffs else None,
                                "max_abs_diff_max": float(np.max(diffs)) if diffs else None}
        results[name] = res
        print(name, json.dumps(res, ensure_ascii=False), flush=True)

    # 延遲：單一行程量，避免多行程互搶 CPU；拿最大解析度的影片
    big = max(test, key=lambda r: r.get("frames", 0))
    import cv2

    probe = None
    for r in test:
        cap = cv2.VideoCapture(str(args.videos / f"{r['video_id']}.mp4"))
        if cap.get(cv2.CAP_PROP_FRAME_HEIGHT) >= 720:
            probe = r
            cap.release()
            break
        cap.release()
    probe = probe or big
    lat = {}
    for name, max_h in [("native", None), ("480p", 480), ("360p", 360)]:
        _, ms = extract(str(args.videos / f"{probe['video_id']}.mp4"), probe["end"], None, max_h)
        lat[name] = round(ms, 1)
    results["latency_ms_per_frame"] = {"video": probe["video_id"], **lat}
    print("latency", json.dumps(results["latency_ms_per_frame"]), flush=True)

    out = args.model / "report" / "bench_mediapipe.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"→ {out}")


if __name__ == "__main__":
    main()
