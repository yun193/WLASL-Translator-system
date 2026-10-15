"""本機訓練後驗證：只用 numpy + onnxruntime，不需要 torch。

  python -m wlasl.evaluate --model models/<run> --data data/kaggle_out/preprocess

依序檢查四件事，結果寫進 models/<run>/report/：
  1. 前處理一致性：本機 prepare(原始 .npy) 與 Kaggle 匯出時的模型輸入是否相同
  2. 匯出一致性：ONNX 對同一份輸入的 logits 與 Kaggle 端 PyTorch logits 是否相同
  3. test 指標：top-1 / top-5（附 Wilson 95% 信賴區間）、每類準確率、最常混淆的配對、混淆矩陣圖
  4. 推論延遲：RTX 3050 Ti（CUDA）與 CPU，batch 1
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

from wlasl.dataset import labeled_span, load_raw, load_split, prepare, resample_mode

PREP_TOL = 1e-5
ONNX_TOL = 1e-3


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """二項比例的 Wilson 信賴區間；樣本少時比常態近似可靠。"""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def topk_hits(logits: np.ndarray, y: np.ndarray, k: int) -> np.ndarray:
    top = np.argsort(-logits, axis=1)[:, :k]
    return (top == y[:, None]).any(1)


def nan_aware_max_diff(a: np.ndarray, b: np.ndarray) -> float:
    """NaN 位置必須一致（不一致回傳 inf），其餘取最大絕對差。"""
    na, nb = np.isnan(a), np.isnan(b)
    if not np.array_equal(na, nb):
        return math.inf
    return float(np.abs(a[~na] - b[~nb]).max()) if (~na).any() else 0.0


def make_session(onnx_path: Path, device: str):
    import onnxruntime as ort

    if device == "cuda":
        ort.preload_dlls()
        # Ampere 以上預設 TF32，logits 會差到 ~7e-3；這個模型很小，關掉不影響速度
        providers = [("CUDAExecutionProvider", {"use_tf32": 0}), "CPUExecutionProvider"]
    else:
        providers = ["CPUExecutionProvider"]
    opts = ort.SessionOptions()
    opts.log_severity_level = 3
    sess = ort.InferenceSession(str(onnx_path), opts, providers=providers)
    return sess, sess.get_providers()[0]


def run(sess, x: np.ndarray, bs: int = 64) -> np.ndarray:
    return np.concatenate([sess.run(None, {"keypoints": x[i : i + bs]})[0] for i in range(0, len(x), bs)])


def latency(sess, sample: np.ndarray, warmup: int = 20, iters: int = 200) -> dict:
    x = sample[None]
    for _ in range(warmup):
        sess.run(None, {"keypoints": x})
    ts = []
    for _ in range(iters):
        t = time.perf_counter()
        sess.run(None, {"keypoints": x})
        ts.append((time.perf_counter() - t) * 1000)
    return {"p50_ms": float(np.percentile(ts, 50)), "p95_ms": float(np.percentile(ts, 95))}


def plot_confusion(y: np.ndarray, pred: np.ndarray, labels: list[str], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    present = sorted(set(y.tolist()) | set(pred.tolist()))
    pos = {c: i for i, c in enumerate(present)}
    cm = np.zeros((len(present), len(present)), dtype=int)
    for t, p in zip(y, pred):
        cm[pos[t], pos[p]] += 1
    fig, ax = plt.subplots(figsize=(14, 14))
    ax.imshow(cm, cmap="Blues")
    names = [labels[c] for c in present]
    ax.set_xticks(range(len(present)), names, rotation=90, fontsize=6)
    ax.set_yticks(range(len(present)), names, fontsize=6)
    ax.set_xlabel("predicted")
    ax.set_ylabel("true")
    ax.set_title(f"WLASL100 test confusion ({len(y)} videos, {len(set(y.tolist()))} classes)")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=Path, required=True, help="models/<run>，含 model.onnx / labels.json / reference.npz")
    ap.add_argument("--data", type=Path, required=True, help="含 index.json 與 keypoints/ 的前處理產出")
    ap.add_argument("--no-latency", action="store_true")
    args = ap.parse_args(argv)
    out = args.model / "report"
    out.mkdir(exist_ok=True)

    labels = json.loads((args.model / "labels.json").read_text(encoding="utf-8"))
    ref = np.load(args.model / "reference.npz")
    splits, _ = load_split(args.data, len(labels))
    mode = resample_mode(args.model)
    by_id = {r["video_id"]: r for r in splits["test"]}
    ids = [str(v) for v in ref["video_ids"]]
    records = [by_id[i] for i in ids]
    y = np.array([r["label"] for r in records])

    # 1. 前處理一致性
    local_x = np.stack([prepare(s[slice(*labeled_span(r, len(s)))], mode=mode)
                        for r, s in zip(records, load_raw(args.data, records))])
    prep_diff = nan_aware_max_diff(local_x, ref["inputs"])

    # 2. 匯出一致性（用 Kaggle 的輸入，隔離掉前處理差異）
    sess, provider = make_session(args.model / "model.onnx", "cuda")
    onnx_logits = run(sess, ref["inputs"])
    onnx_diff = float(np.abs(onnx_logits - ref["logits"]).max())
    argmax_agree = float((onnx_logits.argmax(1) == ref["logits"].argmax(1)).mean())

    # 3. test 指標（用本機前處理的輸入，這才是上線時的路徑）
    logits = run(sess, local_x)
    pred = logits.argmax(1)
    hit1, hit5 = topk_hits(logits, y, 1), topk_hits(logits, y, 5)
    per_class = {}
    for c in sorted(set(y.tolist())):
        m = y == c
        per_class[labels[c]] = {"n": int(m.sum()), "top1": float(hit1[m].mean())}
    pairs: dict[tuple[str, str], int] = {}
    for t, p in zip(y, pred):
        if t != p:
            key = (labels[t], labels[p])
            pairs[key] = pairs.get(key, 0) + 1
    confusions = sorted(pairs.items(), key=lambda kv: -kv[1])[:15]
    plot_confusion(y, pred, labels, out / "confusion.png")

    report = {
        "run": args.model.name,
        "n_test": int(len(y)),
        "n_test_classes": int(len(set(y.tolist()))),
        "checks": {
            "preprocess_max_abs_diff": prep_diff, "preprocess_ok": prep_diff <= PREP_TOL,
            "onnx_max_abs_diff": onnx_diff, "onnx_ok": onnx_diff <= ONNX_TOL,
            "onnx_argmax_agreement": argmax_agree,
        },
        "top1": float(hit1.mean()), "top1_ci95": wilson(int(hit1.sum()), len(y)),
        "top5": float(hit5.mean()), "top5_ci95": wilson(int(hit5.sum()), len(y)),
        "provider": provider,
        "worst_classes": sorted(per_class.items(), key=lambda kv: (kv[1]["top1"], -kv[1]["n"]))[:15],
        "top_confusions": [{"true": t, "pred": p, "count": n} for (t, p), n in confusions],
    }
    if not args.no_latency:
        report["latency"] = {"cuda": latency(sess, local_x[0])}
        cpu, _ = make_session(args.model / "model.onnx", "cpu")
        report["latency"]["cpu"] = latency(cpu, local_x[0])
    kaggle_metrics = args.model / "metrics.json"
    if kaggle_metrics.exists():
        report["kaggle_val"] = json.loads(kaggle_metrics.read_text())["val"]

    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    c = report["checks"]
    print(f"前處理一致性 {'OK' if c['preprocess_ok'] else 'FAIL'}  最大差 {c['preprocess_max_abs_diff']:.2e}")
    print(f"ONNX 一致性   {'OK' if c['onnx_ok'] else 'FAIL'}  最大差 {c['onnx_max_abs_diff']:.2e}  預測一致 {c['onnx_argmax_agreement']:.0%}  ({provider})")
    lo, hi = report["top1_ci95"]
    print(f"test top-1 {report['top1']:.3f}  95% CI [{lo:.3f}, {hi:.3f}]   top-5 {report['top5']:.3f}"
          f"   （{report['n_test']} 支 / {report['n_test_classes']} 類）")
    if "latency" in report:
        lat = report["latency"]
        print(f"延遲 batch1  CUDA p50 {lat['cuda']['p50_ms']:.2f} ms  CPU p50 {lat['cpu']['p50_ms']:.2f} ms")
    print(f"報告 → {out}")
    return report


if __name__ == "__main__":
    main()
