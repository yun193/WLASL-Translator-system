"""鏡頭模式的相位一致率：同一批關鍵點重播不同分類器，把模型的差別和 MediaPipe 的差別分開。

  uv run --project backend python scripts/phasebench.py extract   擷取關鍵點（只要跑一次，存 data/phase_cache）
  uv run --project backend python scripts/phasebench.py           比較分類器，寫 docs/phase-stability/metrics.json

抽幀、縮圖、JPEG 和 eval_backend.stream_video 相同；影片檔模式和 eval_backend.extract_full 相同。
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from math import comb
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

CACHE = ROOT / "data" / "phase_cache"
VIDEOS = ROOT / "data" / "test_videos"
MODEL = ROOT / "models" / "20261018-w2000n"
SPOT_MODEL = ROOT / "models" / "20261019-w2000bg"
OUT = ROOT / "docs" / "phase-stability" / "metrics.json"
FPS = (22.0, 30.0)
PHASES = 3


def extract_one(video_id: str) -> str:
    import cv2

    from app import config, winperf
    from wlasl.landmarks import LandmarkExtractor

    winperf.disable_power_throttling()
    cap = cv2.VideoCapture(str(VIDEOS / f"{video_id}.mp4"))
    native = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    cap.release()

    out = {}
    with LandmarkExtractor(config.MP_MODEL) as ext:
        raw, ts = [], []
        for i, frame in enumerate(frames):
            h, w = frame.shape[:2]
            if h > config.MAX_VIDEO_HEIGHT:
                s = config.MAX_VIDEO_HEIGHT / h
                frame = cv2.resize(frame, (round(w * s), config.MAX_VIDEO_HEIGHT), interpolation=cv2.INTER_AREA)
            t = int(i * 1000 / native)
            raw.append(ext.process(frame, t))
            ts.append(t)
        out["raw_video"], out["ts_video"] = np.stack(raw), np.array(ts)
    for fps in FPS:
        step = 1000 / fps
        for phase in range(PHASES):
            next_t, raw, ts, last = phase * step / PHASES, [], [], -1
            with LandmarkExtractor(config.MP_MODEL) as ext:
                for i, frame in enumerate(frames):
                    t = i * 1000 / native
                    if t + 1e-6 < next_t:
                        continue
                    next_t += step
                    h, w = frame.shape[:2]
                    s = min(1, 640 / w, 480 / h)
                    if s < 1:
                        frame = cv2.resize(frame, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)
                    jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])[1]
                    last = max(int(t), last + 1)
                    raw.append(ext.process(cv2.imdecode(jpg, cv2.IMREAD_COLOR), last))
                    ts.append(last)
            out[f"raw_{fps:g}p{phase}"], out[f"ts_{fps:g}p{phase}"] = np.stack(raw), np.array(ts)
    np.savez_compressed(CACHE / f"{video_id}.npz", **out)
    return video_id


def extract():
    CACHE.mkdir(parents=True, exist_ok=True)
    vids = [p.stem for p in sorted(VIDEOS.glob("*.mp4")) if not (CACHE / f"{p.stem}.npz").is_file()]
    with ProcessPoolExecutor(4) as pool:
        for n, v in enumerate(pool.map(extract_one, vids), 1):
            print(f"[{n}/{len(vids)}] {v}", flush=True)


def replay(clf, spot, raw, ts):
    from app.stream import new_decoder

    decoder = new_decoder(clf, spot)
    signs = []
    for t, frame in zip(ts, raw):
        signs += decoder.push(float(t) / 1000, frame)
    return signs + decoder.flush()


def key_of(signs):
    return tuple(s.prediction.gloss for s in signs)


def shown_of(signs, th):
    """使用者看到的：低信心顯示成 ?。"""
    return tuple(s.prediction.gloss if s.mode == "spot" or s.prediction.prob >= th else "?" for s in signs)


def display_flips(runs, th):
    """單一詞的影片：相位間顯示不同的高信心詞、詞↔?、全部低信心（其中前 3 名順序全同）。"""
    res = {"不同高信心詞": 0, "詞↔?": 0, "全低信心": 0, "全低信心且前3名順序相同": 0}
    for signs in runs:
        if {len(s) for s in signs} != {1}:
            continue
        ps = [s[0].prediction for s in signs]
        words = {p.gloss for p in ps if p.prob >= th}
        res["不同高信心詞"] += len(words) > 1
        res["詞↔?"] += len(words) == 1 and any(p.prob < th for p in ps)
        if not words:
            res["全低信心"] += 1
            res["全低信心且前3名順序相同"] += len({tuple(g for g, _ in p.top5[:3]) for p in ps}) == 1
    return res


def sign_test(a: int, b: int) -> float:
    """配對比較的雙尾 p 值：a、b 是只有其中一邊一致的影片數。"""
    n = a + b
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(a, b) + 1)) / 2**n) if n else 1.0


def evaluate(name, clf, spot, data, gt, th):
    video = {v: replay(clf, spot, d["raw_video"], d["ts_video"]) for v, d in data.items()}
    conf = {v for v, s in video.items() if len(s) == 1 and s[0].prediction.prob >= th}
    res = {"影片檔正確": sum(key_of(s) == (gt[v],) for v, s in video.items()), "高信心支數": len(conf)}
    runs = {}
    for fps in FPS:
        keys = [f"{fps:g}p{p}" for p in range(PHASES)]
        out = {v: {k: replay(clf, spot, d[f"raw_{k}"], d[f"ts_{k}"]) for k in keys} for v, d in data.items()}
        runs[f"{fps:g}"] = out
        same = lambda f, vs: sum(len({f(out[v][k]) for k in keys}) == 1 for v in vs)
        res[f"{fps:g} fps"] = {
            "正確（各相位）": [sum(key_of(out[v][k]) == (gt[v],) for v in data) for k in keys],
            "相位一致": same(key_of, data),
            "高信心時相位一致": same(key_of, conf),
            "介面顯示一致（低信心算 ?）": same(lambda s: shown_of(s, th), data),
            "和影片檔相同": sum(key_of(out[v][k]) == key_of(video[v]) for v in data for k in keys),
            "顯示正確的詞（各相位）": [sum(shown_of(out[v][k], th) == (gt[v],) for v in data) for k in keys],
            "顯示錯誤的詞（各相位）": [sum(any(g not in ("?", gt[v]) for g in shown_of(out[v][k], th)) for v in data) for k in keys],
            "顯示翻盤拆解": display_flips([[out[v][k] for k in keys] for v in data], th),
        }
    print(name, json.dumps(res, ensure_ascii=False), flush=True)
    return res, runs


def main():
    from app import config, winperf
    from app.inference import Classifier, Ensemble

    winperf.disable_power_throttling()
    single, spot = Classifier(MODEL), Classifier(SPOT_MODEL)
    index = json.loads((MODEL / "testdata" / "index.json").read_text(encoding="utf-8"))
    gt = {r["video_id"]: r["gloss"] for r in index}
    data = {p.stem: dict(np.load(p)) for p in sorted(CACHE.glob("*.npz"))}
    print("影片", len(data), flush=True)
    res, runs = {}, {}
    th = config.MIN_CONFIDENCE
    for name, clf in (("w2000n", single), ("w2000bg", spot), ("雙模型平均", Ensemble(single, spot))):
        res[name], runs[name] = evaluate(name, clf, spot, data, gt, th)

    res["雙模型翻盤歸因"], res["介面顯示一致 w2000n vs 雙模型"] = {}, {}
    for fps in runs["w2000n"]:
        stable = lambda name, v, f=key_of: len({f(s) for s in runs[name][fps][v].values()}) == 1
        flips = [v for v in data if not stable("雙模型平均", v)]
        agree = {v for v in data if all(key_of(runs["w2000n"][fps][v][k]) == key_of(runs["w2000bg"][fps][v][k])
                                        for k in runs["w2000n"][fps][v])}
        res["雙模型翻盤歸因"][fps] = {
            "翻盤": len(flips),
            "兩模型各自都穩": sum(stable("w2000n", v) and stable("w2000bg", v) for v in flips),
            "只有 w2000bg 翻": sum(stable("w2000n", v) and not stable("w2000bg", v) for v in flips),
            "只有 w2000n 翻": sum(not stable("w2000n", v) and stable("w2000bg", v) for v in flips),
            "兩模型都翻": sum(not stable("w2000n", v) and not stable("w2000bg", v) for v in flips),
            "兩模型輸出相同的影片": [len(agree), sum(v in agree for v in flips)],
            "兩模型輸出不同的影片": [len(data) - len(agree), sum(v not in agree for v in flips)],
        }
        shown = lambda s: shown_of(s, th)
        only_ens = sum(stable("雙模型平均", v, shown) and not stable("w2000n", v, shown) for v in data)
        only_single = sum(stable("w2000n", v, shown) and not stable("雙模型平均", v, shown) for v in data)
        res["介面顯示一致 w2000n vs 雙模型"][fps] = {"只有雙模型一致": only_ens, "只有 w2000n 一致": only_single,
                                                   "p": sign_test(only_ens, only_single)}
    print(json.dumps({k: res[k] for k in ("雙模型翻盤歸因", "介面顯示一致 w2000n vs 雙模型")}, ensure_ascii=False), flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    extract() if sys.argv[1:] == ["extract"] else main()
