"""2000 詞版的驗收：同一個詞換人比，上線設定能不能正確顯示。

  uv run --project backend python scripts/vocab2000.py import-kp   解開 Kaggle aslct-prep-* 的關鍵點 → data/aslcitizen/kp/*.npz
  uv run --project backend python scripts/vocab2000.py collect     跑模型與解碼器，存每支影片的原始輸出（門檻設 0，之後離線套門檻）
  uv run --project backend python scripts/vocab2000.py tune        依手語者對半：一半調門檻、一半驗收，寫 docs/vocab2000/ 與 models/<n>/serving.json

資料：ASL Citizen test 中和 WLASL2000 同名的 1,159 詞（11 位沒進訓練的手語者）；WLASL 2000 類 test（看過的人）當對照；
詞彙表外：ASL Citizen test 裡 WLASL2000 完全沒有的詞（aslcbench oov 的 unseen 組，300 支）。
驗收標準（用戶 2026-11-13 定）：顯示出來的詞 ≥90% 正確。
"""

from __future__ import annotations

import csv
import io
import json
import os
import pickle
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

import aslcbench as ab  # noqa: E402

# 換模型比較：VOCAB_MODEL／VOCAB_SPOT_MODEL 指資料夾名，VOCAB_TAG 決定快取與輸出（預設是上線的 k2000）
MODEL = ROOT / "models" / os.environ.get("VOCAB_MODEL", "20261113-k2000n")
SPOT_MODEL = ROOT / "models" / os.environ.get("VOCAB_SPOT_MODEL", "20261113-k2000bg")
TAG = os.environ.get("VOCAB_TAG", "")
OUT = ROOT / "docs" / "vocab2000" / TAG if TAG else ROOT / "docs" / "vocab2000"
CACHE = ab.DATA / f"{TAG or 'k2000'}_collect.pkl"
# 窗口偵測門檻只往保守方向挑：單字測試會偏好低門檻，但連續比劃的誤報在 2000 詞下量不到（2026-11-13 決定）
SPOT_THS = (0.78, 0.85, 0.9)
TARGET = 0.90  # 顯示的詞要 ≥90% 正確
MARGIN = 0.01  # 調門檻的那一半多留 1 點，避免剛好卡線
EXPECT = 2000


def cmd_import_kp():
    kp = ab.DATA / "kp"
    kp.mkdir(parents=True, exist_ok=True)
    n = skip = 0
    for d in sorted((ROOT / "data" / "kaggle_out").glob("aslct-prep-*")):
        idx = {r["video_id"]: r for r in json.loads((d / "index.json").read_text())}
        with zipfile.ZipFile(d / "keypoints.zip") as z:
            for name in z.namelist():
                if not name.endswith(".npy"):
                    continue
                r = idx[Path(name).stem]
                dst = kp / f"{Path(r['file']).stem}.npz"
                if dst.exists():  # 之前本機抽過的（67 詞）保留
                    skip += 1
                    continue
                np.savez_compressed(dst, raw=np.load(io.BytesIO(z.read(name))), fps=r["fps"])
                n += 1
        print(d.name, "累計新增", n, "略過", skip, flush=True)


def test_rows(labels):
    vocab = set(labels)
    rows = list(csv.DictReader(open(ab.DATA / "splits" / "test.csv", encoding="utf-8")))
    return [r for r in rows if r["Gloss"].lower() in vocab]


def run(clf, dec_clf, raw, fps, gold):
    """整段分類＋各種窗口門檻下的解碼輸出（整段分類的信心不設門檻，留給離線套用）。"""
    import spotbench as sb
    from app import config

    p = clf(raw)
    rec = {"gold": gold, "top5": [g for g, _ in p.top5], "prob": p.prob, "online": {}}
    config.MIN_CONFIDENCE = 0.0
    cfg = ab.online_cfg()
    for th in SPOT_THS:
        signs = sb.decode(dec_clf, raw, fps, {**cfg, "th": th})
        rec["online"][th] = [(s.mode, s.prediction.gloss, s.prediction.prob, [g for g, _ in s.prediction.top5[:3]])
                             for s in signs]
    return rec


def cmd_collect():
    import spotbench as sb
    from app import winperf
    from app.inference import Classifier, Ensemble
    from wlasl.dataset import labeled_span

    winperf.disable_power_throttling()
    single, bg = Classifier(MODEL), Classifier(SPOT_MODEL)
    labels = single.labels[:-1] if single.labels[-1] == "_bg" else single.labels
    assert len(labels) == EXPECT, len(labels)
    sb.SPOT["classify"] = sb.Cached(Ensemble(single, bg, use_background=True))
    clf = sb.Cached(Ensemble(single, bg))
    res = {"aslc": [], "wlasl": [], "oov": []}
    rows = test_rows(labels)
    missing = [r for r in rows if not (ab.DATA / "kp" / f"{Path(r['Video file']).stem}.npz").exists()]
    assert not missing, f"缺 {len(missing)} 支關鍵點，先跑 import-kp"
    for i, r in enumerate(rows):
        d = np.load(ab.DATA / "kp" / f"{Path(r['Video file']).stem}.npz")
        rec = run(clf, clf, d["raw"], float(d["fps"]), r["Gloss"].lower())
        rec["signer"] = r["Participant ID"]
        res["aslc"].append(rec)
        if i % 1000 == 0:
            print(f"aslc {i}/{len(rows)}", flush=True)
    td = MODEL / "testdata"
    idx = json.loads((td / "index.json").read_text())
    tl = json.loads((td / "labels.json").read_text(encoding="utf-8"))
    for r in idx:
        s = np.load(td / "keypoints" / f"{r['video_id']}.npy")
        rec = run(clf, clf, s[slice(*labeled_span(r, len(s)))], r.get("fps") or 25.0, tl[r["label"]])
        res["wlasl"].append(rec)
    for r in ab.oov_rows(labels[:100])["unseen"]:  # WLASL2000 完全沒有的詞
        d = np.load(ab.DATA / "kp" / f"{Path(r['Video file']).stem}.npz")
        res["oov"].append(run(clf, clf, d["raw"], float(d["fps"]), r["Gloss"].lower()))
    CACHE.write_bytes(pickle.dumps(res))
    print({k: len(v) for k, v in res.items()})


def shown(rec, mc, th):
    return [(g, top3) for mode, g, p, top3 in rec["online"][th] if mode == "spot" or p >= mc]


def metrics(recs, mc, th):
    r = ab.rate
    out = [shown(x, mc, th) for x in recs]
    first = [bool(o) and o[0][0] == x["gold"] for o, x in zip(out, recs)]
    conf = [x["prob"] >= mc for x in recs]
    top1 = [x["top5"][0] == x["gold"] for x in recs]
    silent = [x for o, x in zip(out, recs) if not o]
    return {"whole_top1": r(sum(top1), len(recs)), "whole_top5": r(sum(x["gold"] in x["top5"] for x in recs), len(recs)),
            "coverage": r(sum(conf), len(recs)), "confident_top1": r(sum(a and b for a, b in zip(top1, conf)), sum(conf)),
            "first_correct": r(sum(first), len(recs)), "no_output": r(len(silent), len(recs)),
            "shown_correct": r(sum(first), sum(bool(o) for o in out)),
            "multi_output": r(sum(len(o) > 1 for o in out), len(recs)),
            "silent_top3_hit": r(sum(x["gold"] in x["top5"][:3] for x in silent), len(silent))}


def false_rate(recs, mc, th):
    return ab.rate(sum(bool(shown(x, mc, th)) for x in recs), len(recs))


def cmd_tune():
    res = pickle.loads(CACHE.read_bytes())
    signers = sorted({x["signer"] for x in res["aslc"]}, key=lambda s: int(s[1:]))
    tune_s = set(signers[0::2])
    tune = [x for x in res["aslc"] if x["signer"] in tune_s]
    hold = [x for x in res["aslc"] if x["signer"] not in tune_s]
    grid = []
    for th in SPOT_THS:
        for mc in np.round(np.arange(0.10, 0.951, 0.01), 2):
            m = metrics(tune, float(mc), th)
            ok = min(m["shown_correct"]["rate"] or 0, m["confident_top1"]["rate"] or 0) >= TARGET + MARGIN
            grid.append((ok, m["first_correct"]["rate"], float(mc), th))
    ok = [g for g in grid if g[0]]
    assert ok, "沒有任何門檻組合在調門檻的那一半達到 91%"
    _, _, mc, th = max(ok, key=lambda g: (g[1], g[2]))
    out = {"target": TARGET, "tune_signers": sorted(tune_s), "holdout_signers": sorted(set(signers) - tune_s),
           "chosen": {"min_confidence": mc, "spot_threshold": th},
           "tune": metrics(tune, mc, th), "holdout": metrics(hold, mc, th), "all_aslc": metrics(res["aslc"], mc, th),
           "wlasl_test": metrics(res["wlasl"], mc, th), "oov_unseen_false": false_rate(res["oov"], mc, th),
           "curve_holdout": {f"{m:.2f}": {k: metrics(hold, m, th)[k]["rate"] for k in ("coverage", "shown_correct", "first_correct")}
                             for m in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7)},
           "per_signer": {}, "confusions": []}
    by = defaultdict(list)
    for x in res["aslc"]:
        by[x["signer"]].append(x)
    for s in signers:
        m = metrics(by[s], mc, th)
        out["per_signer"][s] = {k: m[k]["rate"] for k in ("whole_top1", "first_correct", "shown_correct", "no_output")}
    out["confusions"] = Counter(f"{x['gold']}→{x['top5'][0]}" for x in res["aslc"] if x["top5"][0] != x["gold"]).most_common(25)
    # 每個詞的換人正確率：哪些詞最難
    per_word = defaultdict(list)
    for x in res["aslc"]:
        per_word[x["gold"]].append(x["top5"][0] == x["gold"])
    acc = sorted((float(np.mean(v)), w, len(v)) for w, v in per_word.items())
    out["word_acc_quantiles"] = {q: float(np.quantile([a for a, _, _ in acc], q)) for q in (0.1, 0.25, 0.5, 0.75, 0.9)}
    out["hardest_words"] = [(w, round(a, 2), n) for a, w, n in acc[:30]]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    serving = {"min_confidence": mc, "spot_threshold": th,
               "source": "scripts/vocab2000.py tune（ASL Citizen test 一半手語者調門檻，另一半驗收）"}
    (MODEL / "serving.json").write_text(json.dumps(serving, ensure_ascii=False, indent=1), encoding="utf-8")
    f = lambda a: f"{a['k']}/{a['n']}={a['rate']:.1%} [{a['ci95'][0]:.0%},{a['ci95'][1]:.0%}]"  # noqa: E731
    print("選定", out["chosen"])
    for part in ("tune", "holdout", "all_aslc", "wlasl_test"):
        print(part, {k: f(v) for k, v in out[part].items()})
    print("詞彙表外（WLASL2000 沒有的詞）誤報", f(out["oov_unseen_false"]))
    print("驗收那一半的門檻曲線", out["curve_holdout"])


if __name__ == "__main__":
    {"import-kp": cmd_import_kp, "collect": cmd_collect, "tune": cmd_tune}[sys.argv[1]]()
