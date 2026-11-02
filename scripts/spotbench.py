"""連續手語解碼評估：用和後端相同的解碼器（切詞器＋窗口偵測，wlasl.spotter）重播關鍵點，三種測試。

  uv run --project backend python scripts/spotbench.py <models/run> [--spot-model <models/run>] [--grid] [--out 檔.json]

  1. 單字（isolated）：WLASL test 整支影片（前 V 類），看使用者實際看到的輸出：第一個有信心的詞對不對、多報了幾個
  2. 合成連續（synth）：test 單字取真正在比的範圍、統一成 30 fps、接起來（中間 0.03～0.15 秒過渡），
     一半是詞彙表外的詞（模型沒看過的詞，量誤報），答案和起訖已知；量召回、精確、每分鐘誤報
  3. podcast：Breakdown Ep.3 前半調參、後半驗證；逐字稿對齊和機率基準同 longvideo.py compare

合成連續手語沒有真實對話的協同構音與速度，數字會比 podcast 樂觀；背景類訓練也用同一種接法合成負樣本，
所以兩者要一起看，不能只看合成的。
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

TESTDATA = ROOT / "data" / "kaggle_out" / "export" / "testdata"  # 2000 類 test 的整支影片關鍵點（wlasl-export kernel）
PODCAST = ROOT / "docs" / "podcast-ep3"
PODCAST_KP = ROOT / "data" / "podcast" / "ep3_kp.npz"
FPS = 30.0
SPOT: dict = {}  # --spot-model：窗口偵測改用另一個模型（和後端 SPOT_MODEL_DIR 相同）


class Cached:
    """同一個窗口不重複分類（調參時只換門檻與連續命中數，窗口內容相同）。"""

    def __init__(self, clf):
        self.clf, self.memo = clf, {}

    def __call__(self, frames):
        k = hashlib.blake2b(np.ascontiguousarray(frames).tobytes(), digest_size=16).digest()
        if k not in self.memo:
            self.memo[k] = self.clf.predict(frames)
        return self.memo[k]


def decode(classify, raw, fps, p):
    from app import config
    from wlasl.segmenter import Segmenter
    from wlasl.spotter import SignDecoder, Spotter

    seg = Segmenter(rest=config.REST_SECONDS, pre_roll=config.PRE_ROLL_SECONDS,
                    min_len=config.MIN_SIGN_SECONDS, max_len=config.MAX_SIGN_SECONDS)
    spot = Spotter(window=p["window"], hop=p["hop"], min_hits=p["hits"], threshold=p["th"]) if p["spot"] else None
    dec = SignDecoder(classify, seg, spot, continuous_after=p["after"], spot_classify=SPOT.get("classify"))
    out = [s for i, f in enumerate(raw) for s in dec.push(i / fps, f)] + dec.flush()
    th = config.MIN_CONFIDENCE
    # 使用者看到的詞：偵測輸出（已過門檻），或整段分類信心過門檻且不是背景
    return [s for s in out if s.mode == "spot" or (s.prediction.prob >= th and not s.prediction.is_background)]


def load_test(vocab):
    from wlasl.dataset import labeled_span

    idx = json.loads((TESTDATA / "index.json").read_text())
    labels = json.loads((TESTDATA / "labels.json").read_text(encoding="utf-8"))
    recs = [(r, np.load(TESTDATA / "keypoints" / f"{r['video_id']}.npy")) for r in idx]
    inv = [(r, s) for r, s in recs if r["label"] < len(vocab) and labels[r["label"]] == vocab[r["label"]]]
    oov = [(r, s) for r, s in recs if r["label"] >= len(vocab)]
    return inv, oov, labels, labeled_span


def isolated(classify, inv, labels, p):
    first, extra, none = [], [], 0
    for r, s in inv:
        shown = decode(classify, s, r.get("fps") or 25.0, p)
        if not shown:
            none += 1
        first.append(bool(shown) and shown[0].prediction.gloss == labels[r["label"]])
        extra.append(max(len(shown) - 1, 0))
    return {"n": len(inv), "first_correct": float(np.mean(first)), "no_output": none / len(inv),
            "extra_per_video": float(np.mean(extra))}


def build_synth(inv, oov, labels, labeled_span, n_seq=60, per_seq=12, seed=0):
    """回傳 [(raw (T,K,3) 30fps, [(gloss, 起秒, 迄秒, 是否在詞彙表)])]。"""
    from wlasl.augment import active_span
    from wlasl.dataset import resample
    from wlasl.landmarks import normalize

    rng = np.random.default_rng(seed)
    seqs = []
    for _ in range(n_seq):
        parts, gt, t = [], [], 0
        for _ in range(per_seq):
            known = rng.random() < 0.5
            r, s = (inv if known else oov)[rng.integers(len(inv if known else oov))]
            a, b = active_span(s, labeled_span(r, len(s)))
            clip = normalize(s[a:b])
            clip = resample(clip, max(4, round(len(clip) * FPS / (r.get("fps") or 25.0))))
            if parts:
                m = int(rng.integers(1, round(0.15 * FPS) + 1))
                w = np.linspace(0, 1, m + 2, dtype=np.float32)[1:-1, None, None]
                parts.append(parts[-1][-1] * (1 - w) + clip[0] * w)
                t += m
            gt.append((labels[r["label"]], t / FPS, (t + len(clip)) / FPS, known))
            parts.append(clip)
            t += len(clip)
        seqs.append((np.concatenate(parts).astype(np.float32), gt))
    return seqs


def synth(classify, seqs, p, tol=0.25):
    tp = fp_known = fp_oov = fp_other = n_known = 0
    dur = 0.0
    for raw, gt in seqs:
        dur += len(raw) / FPS
        n_known += sum(g[3] for g in gt)
        used = set()
        for s in decode(classify, raw, FPS, p):
            g, mid = s.prediction.gloss, (s.start + s.end) / 2
            hit = next((i for i, (gl, a, b, k) in enumerate(gt)
                        if k and gl == g and i not in used and s.start <= b + tol and s.end >= a - tol), None)
            if hit is not None:
                used.add(hit)
                tp += 1
                continue
            at = next((x for x in gt if x[1] - tol <= mid <= x[2] + tol), None)
            if at is None:
                fp_other += 1
            elif at[3]:
                fp_known += 1
            else:
                fp_oov += 1
    n_out = tp + fp_known + fp_oov + fp_other
    return {"recall": tp / n_known, "precision": tp / n_out if n_out else 0.0,
            "false_per_min": (n_out - tp) / (dur / 60), "false_on_oov_per_min": fp_oov / (dur / 60),
            "outputs_per_min": n_out / (dur / 60), "minutes": dur / 60}


def podcast(classify, raw, fps, occ, p, part):
    import longvideo as lv

    dur = len(raw) / fps
    lo, hi = (0, dur / 2) if part == 1 else (dur / 2, dur)
    a, b = int(lo * fps), int(hi * fps)
    ev = [((s.start + s.end) / 2 + lo, s.prediction.gloss) for s in decode(classify, raw[a:b], fps, p)]
    o = [x for x in occ if lo <= x["t"] < hi]
    # 機率基準只在這一半內平移：平移到另一半的事件沒有逐字稿可對，基準會被低估
    rel = [(t - lo, g) for t, g in ev]
    orel = [{**x, "t": x["t"] - lo} for x in o]
    prec, prec_base = lv.with_baseline(lv.precision, rel, orel, hi - lo, 4, 2)
    rec, rec_base = lv.with_baseline(lv.recall, rel, orel, hi - lo, 4, 2)
    return {"outputs": len(ev), "outputs_per_min": len(ev) / ((hi - lo) / 60), "precision": prec,
            "precision_base": prec_base, "recall": rec, "recall_base": rec_base, "occurrences": len(o)}


def main(argv=None):
    from app.inference import Classifier
    import longvideo as lv

    ap = argparse.ArgumentParser()
    ap.add_argument("model", type=Path)
    ap.add_argument("--window", type=float, default=1.0)
    ap.add_argument("--hop", type=float, default=0.25)
    ap.add_argument("--hits", type=int, default=2)
    ap.add_argument("--th", type=float, default=0.5)
    ap.add_argument("--after", type=float, default=3.5)
    ap.add_argument("--grid", action="store_true", help="在合成連續與 podcast 前半掃 window × hits × th")
    ap.add_argument("--part", type=int, default=2, help="podcast 用哪一半：1 調參、2 驗證")
    ap.add_argument("--spot-model", type=Path, help="窗口偵測用的模型（預設和整段分類同一個）")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)

    clf = Classifier(args.model)
    classify = Cached(clf)
    if args.spot_model:
        SPOT["classify"] = Cached(Classifier(args.spot_model))
    inv, oov, labels, labeled_span = load_test(clf.labels)
    seqs = build_synth(inv, oov, labels, labeled_span)
    d = np.load(PODCAST_KP)
    raw, fps = d["raw"], float(d["fps"])
    occ = lv.match_vocab(lv.flat_tokens(json.loads((PODCAST / "transcript.json").read_text(encoding="utf-8"))),
                         set(clf.labels))
    base = {"window": args.window, "hop": args.hop, "hits": args.hits, "th": args.th, "after": args.after, "spot": True}
    res = {"model": args.model.name, "spot_model": args.spot_model.name if args.spot_model else None,
           "background": clf.has_background, "params": base}

    if args.grid:
        rows = []
        for w, h, th in itertools.product((0.6, 0.8, 1.0, 1.3), (1, 2, 3), (0.3, 0.5, 0.7)):
            p = {**base, "window": w, "hits": h, "th": th}
            rows.append({"window": w, "hits": h, "th": th, "synth": synth(classify, seqs, p),
                         "podcast1": podcast(classify, raw, fps, occ, p, 1)})
            s, q = rows[-1]["synth"], rows[-1]["podcast1"]
            print(f"w{w} h{h} th{th}  synth R {s['recall']:.3f} P {s['precision']:.3f} 誤報/分 {s['false_per_min']:.1f}"
                  f"  | podcast1 P {q['precision']:.3f}({q['precision_base']:.3f}) R {q['recall']:.3f}({q['recall_base']:.3f})"
                  f" 輸出/分 {q['outputs_per_min']:.1f}", flush=True)
        res["grid"] = rows
    else:
        no_spot = {**base, "spot": False}
        res["isolated"] = {"segmenter_only": isolated(classify, inv, labels, no_spot),
                           "decoder": isolated(classify, inv, labels, base)}
        res["synth"] = {"segmenter_only": synth(classify, seqs, no_spot), "decoder": synth(classify, seqs, base)}
        res[f"podcast{args.part}"] = {"segmenter_only": podcast(classify, raw, fps, occ, no_spot, args.part),
                                      "decoder": podcast(classify, raw, fps, occ, base, args.part)}
        print(json.dumps(res, ensure_ascii=False, indent=1))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
