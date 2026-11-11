"""彙整 wlasl-signer-cv kernel 的 cv_results.json：換人（沒看過的手語者）vs 看過的手語者的單字正確率。

用法：python scripts/signer_cv_report.py data/kaggle_out/signer_cv/cv_results.json docs/signer-cv/metrics.json
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ml"))
from wlasl.evaluate import wilson  # noqa: E402

THRESH = 0.5  # 上線 MIN_CONFIDENCE


def acc(rows, key="top1"):
    k = sum(r[key] for r in rows)
    lo, hi = wilson(k, len(rows))
    return {"k": k, "n": len(rows), "acc": k / len(rows) if rows else None, "ci95": [lo, hi]}


def summarize(rows):
    conf = [r for r in rows if r["p1"] >= THRESH]
    return {"top1": acc(rows), "top5": acc(rows, "top5ok"), "coverage": len(conf) / len(rows),
            "confident_top1": acc(conf) if conf else None}


def main(src, dst):
    cv = json.loads(Path(src).read_text())
    rows = cv["results"]
    for r in rows:
        r["top1"] = r["top5"][0] == r["label"]
        r["top5ok"] = r["label"] in r["top5"]
    unseen = [r for r in rows if r["subset"] == "test"]
    seen = [r for r in rows if r["subset"] == "test_seen"]
    out = {"folds": cv["folds"], "args": cv["args"], "threshold": THRESH,
           "unseen": summarize(unseen), "seen": summarize(seen), "per_fold": {}, "per_signer": {}}
    for k in range(len(cv["folds"])):
        out["per_fold"][k] = {"unseen": summarize([r for r in unseen if r["fold"] == k]),
                              "seen": summarize([r for r in seen if r["fold"] == k])}

    # 配對比較：原 test 影片在自己手語者被留出的那折是「沒看過」，在其他折是「看過」，同一支影片前後比
    by_vid = defaultdict(lambda: {"unseen": [], "seen": []})
    for r in rows:
        if r["orig_test"]:
            by_vid[r["video_id"]]["unseen" if r["subset"] == "test" else "seen"].append(r["top1"])
    pair = [(v["unseen"][0], sum(v["seen"]) / len(v["seen"])) for v in by_vid.values() if v["unseen"] and v["seen"]]
    assert pair, "沒有可配對的原 test 影片"
    out["paired_orig_test"] = {"n": len(pair), "unseen_acc": sum(u for u, _ in pair) / len(pair),
                               "seen_acc": sum(s for _, s in pair) / len(pair),
                               "seen_right_unseen_wrong": sum(s > 0.5 and not u for u, s in pair),
                               "seen_wrong_unseen_right": sum(s < 0.5 and u for u, s in pair)}

    sig = defaultdict(list)
    for r in unseen:
        sig[r["signer"]].append(r)
    for s, rs in sorted(sig.items(), key=lambda x: -len(x[1])):
        if len(rs) >= 10:
            out["per_signer"][s] = acc(rs)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

    f = lambda a: f"{a['k']}/{a['n']}={a['acc']:.1%} [{a['ci95'][0]:.0%},{a['ci95'][1]:.0%}]"  # noqa: E731
    for name in ("unseen", "seen"):
        m = out[name]
        print(f"{name:7s} top1 {f(m['top1'])}  top5 {f(m['top5'])}  涵蓋 {m['coverage']:.0%}  高信心 {f(m['confident_top1'])}")
    for k, m in out["per_fold"].items():
        print(f"fold{k}  unseen {f(m['unseen']['top1'])}  seen {f(m['seen']['top1'])}")
    print("配對（原 test）", out["paired_orig_test"])
    print("每位手語者（≥10 支）", {s: f(a) for s, a in out["per_signer"].items()})


if __name__ == "__main__":
    main(*sys.argv[1:3])
