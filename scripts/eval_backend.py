"""把 test 影片逐支 POST 到執行中的後端 /api/analyze，量上線路徑的正確率，並拆解每支錯在哪一關。

用法（repo 根目錄，後端先用 .\\start.ps1 -NoBrowser 開起來）：
  uv run --project backend python scripts/eval_backend.py [--url http://127.0.0.1:8766] [--no-local]
                                                          [--stream-fps 15 10 --phases 2]

--stream-fps 另外模擬鏡頭模式（WebSocket、640×480 JPEG、指定 fps 抽幀）；時間戳照影片時間，
不受後端實際速度影響，量的是「後端跟得上這個 fps 時」的結果。

同一支影片同時算三種預測，依序比對就能定位錯誤來源：
  ref    Kaggle 關鍵點 + 人工標註起訖 + PyTorch（reference.npz）   → 模型本身的能力上限
  label  本機關鍵點 + 人工標註起訖 + ONNX（本腳本自己擷取）        → 換成本機 MediaPipe 後
  server 本機關鍵點 + 切詞器決定的起訖（後端 /api/analyze 回傳）   → 使用者實際看到的結果
歸因取「第一個出錯的關卡」：模型本身 → 本機關鍵點 → 切詞（沒切出 / 切成多段）→ 起訖邊界。
結果寫到 models/<run>/report/backend_eval.json。
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

STAGES = ["正確", "模型本身", "本機關鍵點", "切詞：沒切出", "切詞：切成多段", "起訖邊界"]


def post_video(url: str, path: Path) -> dict:
    req = urllib.request.Request(f"{url}/api/analyze", data=path.read_bytes(), method="POST",
                                 headers={"Content-Type": "video/mp4"})
    for attempt in range(20):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code != 503 or attempt == 19:  # 503 = 另一邊（例如瀏覽器）正在用，稍等重試
                raise RuntimeError(f"{path.name}: HTTP {e.code} {e.read().decode('utf-8', 'replace')}") from e
        except ConnectionResetError:
            # 忙碌時後端沒讀 body 就回 503 並關閉，Windows 上客戶端常收到 RST 而不是 503
            if attempt == 19:
                raise
        time.sleep(1)
    raise AssertionError


def stream_video(url: str, path: Path, fps: float, phase: int, phases: int) -> list[str]:
    """模擬鏡頭模式：照前端的規格（640×480 以內、JPEG 0.8、最多 fps 幀/秒）走 /ws/stream。

    phase 讓抽幀起點錯開 1/phases 個間隔，用來量「同一支影片換個抽幀相位會不會翻盤」。
    """
    import cv2
    from websockets.exceptions import InvalidStatus
    from websockets.sync.client import connect

    ws_url = url.replace("http", "ws", 1) + "/ws/stream"
    # 上一條連線斷開後，後端還要一點時間關 MediaPipe 才釋放名額；忙碌時握手會被拒（403）
    for attempt in range(50):
        try:
            conn = connect(ws_url, origin=url, max_size=None)
            break
        except InvalidStatus:
            if attempt == 49:
                raise
            time.sleep(0.2)
    cap = cv2.VideoCapture(str(path))
    native = cap.get(cv2.CAP_PROP_FPS)
    step = 1000 / fps
    next_t, glosses, i = phase * step / phases, [], 0
    with conn as ws:
        def drain(until: str):
            while True:
                e = json.loads(ws.recv())
                if e["type"] == "sign":
                    glosses.append(e["gloss"])
                if e["type"] == until:
                    return

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            t = i * 1000 / native
            i += 1
            if t + 1e-6 < next_t:
                continue
            next_t += step
            h, w = frame.shape[:2]
            s = min(1, 640 / w, 480 / h)
            if s < 1:
                frame = cv2.resize(frame, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)
            jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])[1].tobytes()
            ws.send(struct.pack("<d", t) + jpg)
            drain("frame")  # 一來一回，和前端一樣等回覆才送下一幀
        ws.send(json.dumps({"type": "flush"}))
        ws.send(json.dumps({"type": "reset"}))  # flush 沒切出詞時不會回訊息，靠 reset 的回覆收尾
        drain("reset")
    cap.release()
    return glosses


def extract_full(path: str) -> np.ndarray:
    """和 analyze_video 相同的解碼、縮圖與時間戳，擷取整支影片的原始關鍵點。"""
    import cv2

    from app import config, winperf
    from wlasl.landmarks import LandmarkExtractor

    winperf.disable_power_throttling()
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames, i = [], 0
    with LandmarkExtractor(config.MP_MODEL) as ext:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            h, w = frame.shape[:2]
            if h > config.MAX_VIDEO_HEIGHT:
                s = config.MAX_VIDEO_HEIGHT / h
                frame = cv2.resize(frame, (round(w * s), config.MAX_VIDEO_HEIGHT), interpolation=cv2.INTER_AREA)
            frames.append(ext.process(frame, int(i * 1000 / fps)))
            i += 1
    cap.release()
    return np.stack(frames)


def diagnose(r: dict) -> str:
    if r["server_ok"]:
        return "正確"
    if not r["ref_ok"]:
        return "模型本身"
    if r["label_ok"] is False:
        return "本機關鍵點"
    if r["n_signs"] == 0:
        return "切詞：沒切出"
    if r["n_signs"] > 1:
        return "切詞：切成多段"
    return "起訖邊界"


def pct(a: int, b: int) -> str:
    return f"{a}/{b} = {a / b:.1%}" if b else "0/0"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8766")
    ap.add_argument("--videos", type=Path, default=ROOT / "data" / "test_videos")
    ap.add_argument("--index", type=Path, help="含人工標註起訖的 index.json；預設 models/<run>/testdata，舊模型用 data/kaggle_out/preprocess")
    ap.add_argument("--no-local", action="store_true", help="略過本機擷取（不算 label 那一關）")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--stream-fps", type=float, nargs="*", default=[],
                    help="另外模擬鏡頭模式走 WebSocket，例如 --stream-fps 15 10")
    ap.add_argument("--phases", type=int, default=2, help="鏡頭模式每個 fps 跑幾種抽幀相位")
    args = ap.parse_args()

    from app import winperf
    from app.inference import Classifier

    winperf.disable_power_throttling()
    with urllib.request.urlopen(f"{args.url}/api/health", timeout=10) as r:
        health = json.loads(r.read())
    model_dir = ROOT / "models" / health["model"]
    clf = Classifier(model_dir)
    if clf.labels != health["labels"]:
        sys.exit(f"後端的模型 {health['model']} 和 {model_dir} 的類別不一致")
    labels = clf.labels

    if args.index is None:
        args.index = model_dir / "testdata" / "index.json"
        if not args.index.is_file():
            args.index = ROOT / "data" / "kaggle_out" / "preprocess" / "index.json"
    ref = np.load(model_dir / "reference.npz")
    ref_pred = {str(v): labels[int(l.argmax())] for v, l in zip(ref["video_ids"], ref["logits"])}
    index = {r["video_id"]: r for r in json.loads(args.index.read_text(encoding="utf-8"))}
    vids = sorted(v for v in ref_pred if (args.videos / f"{v}.mp4").is_file())
    print(f"模型 {health['model']}，test 影片 {len(vids)} 支，後端 {args.url}")

    local = {}
    if not args.no_local:
        t0 = time.perf_counter()
        with ProcessPoolExecutor(args.workers) as pool:
            for v, raw in zip(vids, pool.map(extract_full, [str(args.videos / f"{v}.mp4") for v in vids])):
                local[v] = raw
        print(f"本機擷取完成 {time.perf_counter() - t0:.0f} 秒")

    rows, t0 = [], time.perf_counter()
    for n, v in enumerate(vids, 1):
        meta = index[v]
        gt = meta["gloss"]
        res = post_video(args.url, args.videos / f"{v}.mp4")
        signs, fps = res["signs"], res["fps"]
        # 人工標註起訖換成秒（1 起算、含端點）
        lab_s, lab_e = (meta["start"] - 1) / fps, (meta["end"] - 1) / fps
        row = {
            "video_id": v, "gt": gt, "fps": fps, "frames": res["frames"],
            "label_span": [round(lab_s, 3), round(lab_e, 3)],
            "ref": ref_pred[v], "ref_ok": ref_pred[v] == gt,
            "n_signs": len(signs),
            "server": [s["gloss"] for s in signs],
            "server_prob": [s["prob"] for s in signs],
            "server_span": [[s["start"], s["end"]] for s in signs],
            "server_ok": len(signs) == 1 and signs[0]["gloss"] == gt,
            "server_any": any(s["gloss"] == gt for s in signs),
            "server_top5": any(t["gloss"] == gt for s in signs for t in s["top5"]),
            "elapsed_s": res["elapsed_s"],
        }
        if len(signs) == 1:
            # 切詞器多包（正）或少包（負）了多少秒
            row["extra_before"] = round(lab_s - signs[0]["start"], 3)
            row["extra_after"] = round(signs[0]["end"] - lab_e, 3)
        if v in local:
            raw = local[v]
            p_lab = clf.predict(raw[meta["start"] - 1:meta["end"]])
            p_full = clf.predict(raw)
            row.update(label=p_lab.gloss, label_ok=p_lab.gloss == gt, label_prob=round(p_lab.prob, 4),
                       full=p_full.gloss, full_ok=p_full.gloss == gt)
        else:
            row.update(label=None, label_ok=None)
        row["stage"] = diagnose(row)
        row["stream"] = {f"{f:g}fps/p{p}": stream_video(args.url, args.videos / f"{v}.mp4", f, p, args.phases)
                         for f in args.stream_fps for p in range(args.phases)}
        rows.append(row)
        mark = "✓" if row["server_ok"] else "✗"
        live = " ".join(f"{k}={'+'.join(g) or '無'}" for k, g in row["stream"].items())
        print(f"[{n:3d}/{len(vids)}] {mark} {v} {gt:>12} → {' '.join(row['server']) or '(無)':<24} "
              f"ref={row['ref']:<12} label={row['label'] or '-':<12} {row['stage']}  {live}")
    wall = time.perf_counter() - t0

    N = len(rows)
    stages = Counter(r["stage"] for r in rows)
    single = [r for r in rows if r["n_signs"] == 1]
    conf = [r for r in single if r["server_prob"][0] >= health["min_confidence"]]
    summary = {
        "model": health["model"], "videos": N, "wall_s": round(wall, 1),
        "segmenter": health["segmenter"],
        "acc": {
            "ref (Kaggle 關鍵點 + 標註起訖)": pct(sum(r["ref_ok"] for r in rows), N),
            **({"label (本機關鍵點 + 標註起訖)": pct(sum(bool(r["label_ok"]) for r in rows), N),
                "full (本機關鍵點 + 整支影片)": pct(sum(bool(r.get("full_ok")) for r in rows), N)} if local else {}),
            "server 嚴格（剛好 1 個詞且正確）": pct(sum(r["server_ok"] for r in rows), N),
            "server 任一段正確": pct(sum(r["server_any"] for r in rows), N),
            "server top-5 含正解": pct(sum(r["server_top5"] for r in rows), N),
        },
        "n_signs": dict(sorted(Counter(r["n_signs"] for r in rows).items())),
        "stages": {s: stages.get(s, 0) for s in STAGES},
        "confident": {"門檻": health["min_confidence"], "涵蓋": pct(len(conf), len(single)),
                      "其中正確": pct(sum(r["server_ok"] for r in conf), len(conf)),
                      "低信心中正確": pct(sum(r["server_ok"] for r in single if r not in conf), len(single) - len(conf))},
        "boundary": {},
        "confusions": Counter(f"{r['gt']} → {r['server'][0]}" for r in single if not r["server_ok"]).most_common(15),
    }
    for name, group in (("正確", [r for r in single if r["server_ok"]]), ("錯誤", [r for r in single if not r["server_ok"]])):
        if group:
            summary["boundary"][name] = {
                "支數": len(group),
                "多包前段秒數 中位數": round(float(np.median([r["extra_before"] for r in group])), 3),
                "多包後段秒數 中位數": round(float(np.median([r["extra_after"] for r in group])), 3),
            }

    if args.stream_fps:
        summary["stream"] = {}
        for f in args.stream_fps:
            keys = [f"{f:g}fps/p{p}" for p in range(args.phases)]
            ok = {k: sum(r["stream"][k] == [r["gt"]] for r in rows) for k in keys}
            same = sum(len({tuple(r["stream"][k]) for k in keys}) == 1 for r in rows)
            summary["stream"][f"{f:g}fps"] = {
                "嚴格正確（各相位）": [pct(ok[k], N) for k in keys],
                "切出非 1 個詞": sum(len(r["stream"][k]) != 1 for r in rows for k in keys),
                "相位間結果一致": pct(same, N),
                "和影片檔模式相同": pct(sum(r["stream"][k] == r["server"] for r in rows for k in keys), N * len(keys)),
            }

    out = model_dir / "report" / "backend_eval.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"summary": summary, "videos": rows}, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n== 正確率 ==")
    for k, val in summary["acc"].items():
        print(f"  {k:<30} {val}")
    print(f"\n== 切出幾個詞 ==  {summary['n_signs']}")
    print("\n== 錯在哪一關（取第一個出錯的關卡）==")
    for s in STAGES:
        print(f"  {s:<12} {stages.get(s, 0):3d}")
    print(f"\n== 信心門檻 {health['min_confidence']} ==  {summary['confident']}")
    print(f"\n== 起訖邊界（單一詞，正值 = 比人工標註多包）==")
    for k, val in summary["boundary"].items():
        print(f"  {k}: {val}")
    print("\n== 常見混淆（正解 → 後端）==")
    for k, c in summary["confusions"]:
        print(f"  {k}  ×{c}")
    for k, val in summary.get("stream", {}).items():
        print(f"\n== 鏡頭模式模擬 {k}（{args.phases} 種抽幀相位）==  {val}")
    print(f"\n逐支結果：{out}")


if __name__ == "__main__":
    main()
