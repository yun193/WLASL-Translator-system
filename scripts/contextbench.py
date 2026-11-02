"""Podcast 泛化與上下文實測：把 report.md「上下文還輪不到」這個推論變成量測。關鍵點用 longvideo.py extract 的快取。

  uv run --project backend python scripts/contextbench.py windows          存每個窗口的完整機率（只需跑一次）
  uv run --project backend python scripts/contextbench.py shift            領域落差：podcast vs WLASL test
  uv run --project backend python scripts/contextbench.py rerank           上下文重排：視覺／先驗／視覺＋先驗三臂
  uv run --project backend python scripts/contextbench.py streams <資料夾>  匯出盲讀測試用的詞串

重排實驗（只在 podcast 後半評估，lambda 在前半選）：
  先驗如果來自逐字稿，它自己就能猜中答案，所以一定要和「只用先驗、不看手」比。
  視覺＋先驗明顯高於只用先驗，才代表手語辨識提供了上下文能利用的資訊。
  local：知道前後 30 秒真實用詞（理想語言模型的上限），排除評分用的對齊範圍，避免直接洩題
  topic：只知道另一半影片的用詞（知道主題，不知道當下）
  self：只用模型自己前 120 秒的輸出（沒有偷看，是實際上線做得到的版本）
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

PODCAST = ROOT / "docs" / "podcast-ep3"
PODCAST_KP = ROOT / "data" / "podcast" / "ep3_kp.npz"
OUT = ROOT / "data" / "contextbench"
TESTDATA = ROOT / "data" / "kaggle_out" / "export" / "testdata"
RUNS = (("20261018-w2000n-2000", 1.0), ("20261018-w2000n-2000", 0.6), ("20261019-w2000bg", 1.3))
BEFORE, AFTER = 4.0, 2.0  # 和 longvideo.compare 相同的對齊：逐字稿 t，模型在 [t−4, t+2] 內輸出算對上
RATES = (2, 5, 10)  # 每分鐘輸出數；每一臂取信心最高的前 N 個，輸出量相同才能比精確
LAMBDAS = (0.25, 0.5, 1.0, 2.0)
EPS = 1e-8


def load_raw():
    d = np.load(PODCAST_KP)
    return d["raw"], float(d["fps"])


def load_occ(vocab):
    import longvideo as lv

    return lv.match_vocab(lv.flat_tokens(json.loads((PODCAST / "transcript.json").read_text(encoding="utf-8"))), set(vocab))


def run_path(model, size):
    return OUT / f"{model}_w{size}.npz"


# ---------- windows ----------
def cmd_windows(_):
    from app import winperf
    from app.inference import Classifier, softmax
    from wlasl.dataset import prepare
    from wlasl.segmenter import hands_visible

    winperf.disable_power_throttling()
    raw, fps = load_raw()
    hand = np.array([hands_visible(x) for x in raw], dtype=np.float32)
    cum = np.concatenate([[0], np.cumsum(hand)])
    OUT.mkdir(parents=True, exist_ok=True)
    hop = round(fps * 0.25)
    for model, size in RUNS:
        clf = Classifier(ROOT / "models" / model)
        win = round(fps * size)
        t, probs = [], []
        for a in range(0, len(raw) - win, hop):
            if cum[a + win] - cum[a] < win * 0.5:
                continue
            x = prepare(raw[a:a + win], mode=clf.mode)[None]
            probs.append(softmax(clf.session.run(None, {"keypoints": x})[0][0]))
            t.append((a + win / 2) / fps)
        np.savez(run_path(model, size), t=np.array(t, np.float32), probs=np.stack(probs).astype(np.float32),
                 labels=np.array(clf.labels), bg=clf.has_background)
        print(f"{model} {size}s：{len(t)} 窗口", flush=True)


# ---------- shift ----------
def motion(raw, fps):
    """手偵測率與手腕速度（肩寬／秒，排除肩寬換算後的身體大小差異）。"""
    from wlasl.landmarks import L_SHOULDER, LEFT_HAND, R_SHOULDER, RIGHT_HAND

    sw = np.linalg.norm(raw[:, L_SHOULDER, :2] - raw[:, R_SHOULDER, :2], axis=1)
    speeds = []
    rates = []
    for h in (LEFT_HAND, RIGHT_HAND):
        w = raw[:, h.start, :2]
        rates.append(~np.isnan(w[:, 0]))
        speeds.append(np.linalg.norm(np.diff(w, axis=0), axis=1) * fps / sw[1:])
    s = np.concatenate(speeds)
    return {"any_hand": float((rates[0] | rates[1]).mean()), "both_hands": float((rates[0] & rates[1]).mean()),
            "speed": s[np.isfinite(s) & (s < 50)], "shoulder": float(np.nanmedian(sw))}


def cmd_shift(_):
    from wlasl.augment import active_span
    from wlasl.dataset import labeled_span

    raw, fps = load_raw()
    pod = motion(raw, fps)
    idx = json.loads((TESTDATA / "index.json").read_text())
    any_h, both, shoulder, speed, durs = [], [], [], [], []
    for r in idx:
        s = np.load(TESTDATA / "keypoints" / f"{r['video_id']}.npy")
        f = r.get("fps") or 25.0
        a, b = active_span(s, labeled_span(r, len(s)))
        if b - a < 3:
            continue
        m = motion(s[a:b], f)
        any_h.append(m["any_hand"]); both.append(m["both_hands"]); shoulder.append(m["shoulder"])
        speed.append(m["speed"]); durs.append((b - a) / f)
    speed = np.concatenate(speed)
    res = {"podcast": {"any_hand": pod["any_hand"], "both_hands": pod["both_hands"], "shoulder": pod["shoulder"],
                       "speed_p50": float(np.percentile(pod["speed"], 50)), "speed_p90": float(np.percentile(pod["speed"], 90))},
           "wlasl_test": {"videos": len(durs), "any_hand": float(np.mean(any_h)), "both_hands": float(np.mean(both)),
                          "shoulder": float(np.nanmedian(shoulder)), "sign_seconds_p50": float(np.median(durs)),
                          "speed_p50": float(np.percentile(speed, 50)), "speed_p90": float(np.percentile(speed, 90))}}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "shift.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))


# ---------- rerank ----------
def build_events(t, idx, score, lo, hi, rate):
    """相鄰同詞窗口合併留峰值，再取分數最高的 rate×分鐘 個。"""
    ev = []
    for i in np.flatnonzero((t >= lo) & (t < hi)):
        if ev and ev[-1][1] == idx[i] and t[i] - ev[-1][3] <= 0.5:
            ev[-1][3] = t[i]
            if score[i] > ev[-1][2]:
                ev[-1][0], ev[-1][2] = t[i], score[i]
        else:
            ev.append([t[i], idx[i], score[i], t[i]])
    ev.sort(key=lambda x: -x[2])
    return ev[:int(rate * (hi - lo) / 60)]


def relative(pairs, occ, lo, hi):
    """機率基準只能在評估範圍內平移：平移到範圍外的事件沒有逐字稿可對，基準會被低估。"""
    return [(t - lo, g) for t, g in pairs], [{**o, "t": o["t"] - lo} for o in occ], hi - lo


def score_events(ev, labels, occ, lo, hi):
    import longvideo as lv

    pairs = [(float(e[0]), str(labels[e[1]])) for e in ev]
    rel, o, d = relative(pairs, occ, lo, hi)
    p, pb = lv.with_baseline(lv.precision, rel, o, d, BEFORE, AFTER)
    r, rb = lv.with_baseline(lv.recall, rel, o, d, BEFORE, AFTER)
    return {"n": len(pairs), "hits": round(p * len(pairs)), "precision": p, "precision_base": pb, "recall": r, "recall_base": rb}


def evidence_auc(t, logv, labels, occ, lo, hi, n_null=20, n_boot=1000):
    """視覺證據：同一個詞，對齊時間的窗口分數高於隨機時間的機率。0.5 = 手語辨識沒提供資訊。
    不受輸出門檻影響，用上所有出現，統計力遠高於命中數。"""
    ix = {g: i for i, g in enumerate(labels)}
    rng = np.random.default_rng(0)
    m = (t >= lo) & (t < hi)
    tt = t[m]
    best = lambda g, c: logv[m][np.searchsorted(tt, c - BEFORE):np.searchsorted(tt, c + AFTER), g].max(initial=-np.inf)
    wins = []
    for o in occ:
        g = ix[o["gloss"]]
        s = best(g, o["t"])
        null = [best(g, lo + (o["t"] - lo + rng.uniform(0.2, 0.8) * (hi - lo)) % (hi - lo)) for _ in range(n_null)]
        wins.append(np.mean([(s > x) + 0.5 * (s == x) for x in null]))
    wins = np.array(wins)
    boots = [wins[rng.integers(len(wins), size=len(wins))].mean() for _ in range(n_boot)]
    return {"auc": float(wins.mean()), "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]}


def sample_prior_hits(t, pr, labels, occ, lo, hi, rates, draws=10):
    """只知道詞頻、完全不看手：每個窗口依先驗抽一個詞，分數隨機。抽 draws 次取平均。"""
    rng = np.random.default_rng(0)
    cdf = pr.cumsum(1)
    out = {}
    rows = {r: [] for r in rates}
    for _ in range(draws):
        i = (cdf < rng.random((len(t), 1)) * cdf[:, -1:]).sum(1).clip(0, pr.shape[1] - 1)
        sc = rng.random(len(t))
        for r in rates:
            rows[r].append(score_events(build_events(t, i, sc, lo, hi, r), labels, occ, lo, hi))
    for r in rates:
        n = int(np.mean([x["n"] for x in rows[r]]))
        out[str(r)] = {"n": n, "hits": round(float(np.mean([x["hits"] for x in rows[r]]))),
                       "precision": float(np.mean([x["precision"] for x in rows[r]])),
                       "precision_base": float(np.mean([x["precision_base"] for x in rows[r]])),
                       "recall": float(np.mean([x["recall"] for x in rows[r]])),
                       "recall_base": float(np.mean([x["recall_base"] for x in rows[r]]))}
    return out


def add_range(mat, t, lo, hi, g, v):
    mat[np.searchsorted(t, lo):np.searchsorted(t, hi), g] += v


def priors(t, labels, occ, dur, self_events):
    """回傳 {臂名: (N, V) 先驗機率}。q 一律來自另一半影片，評分的這一半不參與。"""
    V, ix = len(labels), {g: i for i, g in enumerate(labels)}
    mid = dur / 2
    half = [np.ones(V, np.float32), np.ones(V, np.float32)]
    for o in occ:
        half[int(o["t"] >= mid)][ix[o["gloss"]]] += 1
    q = [half[1] / half[1].sum(), half[0] / half[0].sum()]  # 第 i 半用另一半的詞頻
    Q = np.stack([q[int(x >= mid)] for x in t])

    local = np.zeros((len(t), V), np.float32)
    for o in occ:
        g = ix[o["gloss"]]
        add_range(local, t, o["t"] - 30, o["t"] + 30, g, 1)
        add_range(local, t, o["t"] - BEFORE, o["t"] + AFTER, g, -1)  # 對齊範圍內不算，不直接洩題
    mu = 5.0
    P_local = (local + mu * Q) / (local.sum(1, keepdims=True) + mu)

    hist = np.zeros((len(t), V), np.float32)
    for et, g in self_events:
        add_range(hist, t, et + 1, et + 120, g, 1)  # 只看過去
    P_self = (hist + mu / V) / (hist.sum(1, keepdims=True) + mu)
    return {"local": P_local, "topic": Q, "self": P_self}


def cmd_rerank(_):
    import longvideo as lv

    raw, fps = load_raw()
    dur = len(raw) / fps
    mid = dur / 2
    results = {}
    for model, size in RUNS:
        d = np.load(run_path(model, size))
        t, P = d["t"], d["probs"]
        labels = [str(x) for x in d["labels"]]
        V = len(labels)
        bg = P[:, -1] if bool(d["bg"]) else np.zeros(len(t), np.float32)
        P = P[:, :V]
        occ = load_occ(labels)
        o2 = [o for o in occ if o["t"] >= mid]
        vis = P.argmax(1)
        vp = P.max(1)
        res = {"windows": len(t), "occurrences_h2": len(o2), "vocab": V}

        # 校準：信心夠高的輸出到底有多準（對上逐字稿，和機率基準比）
        res["calibration"] = []
        for th in (0.3, 0.5, 0.7, 0.9):
            m = (vp >= th) & (vp > bg) & (t >= mid)
            ev = build_events(t[m], vis[m], vp[m], mid, dur, 1e9)
            res["calibration"].append({"th": th, **score_events(ev, labels, o2, mid, dur)})

        # 候選上限：對的詞有多常出現在 top-k（重排只能從候選裡挑）
        res["topk"] = []
        order = np.argsort(-P, axis=1)
        for k in (1, 5, 10, 20, 50):
            k = min(k, V)
            m = np.flatnonzero(t >= mid)
            pairs = [(float(t[i]), labels[g]) for i in m for g in order[i, :k]]
            rel, o, d = relative(pairs, o2, mid, dur)
            r, rb = lv.with_baseline(lv.recall, rel, o, d, BEFORE, AFTER, k=5)
            res["topk"].append({"k": k, "recall": r, "recall_base": rb, "candidate_share": k / V})

        conf = (vp >= 0.5) & (vp > bg)
        self_ev = [(float(e[0]), int(e[1])) for e in build_events(t[conf], vis[conf], vp[conf], 0, dur, 1e9)]
        pri = priors(t, labels, occ, dur, self_ev)
        logv = np.log(P + EPS)
        res["evidence"] = evidence_auc(t, logv, labels, o2, mid, dur)
        print(f"  視覺證據 AUC {res['evidence']}", flush=True)
        arms = {}
        arms["視覺"] = {str(r): score_events(build_events(t, vis, vp - bg, mid, dur, r), labels, o2, mid, dur) for r in RATES}
        for name, pr in pri.items():
            logp = np.log(pr + EPS)
            pi, ps = pr.argmax(1), pr.max(1)
            # local 是當下的最佳猜測；topic、self 的 argmax 幾乎是同一個詞，合併後只剩 1 個輸出，改成依詞頻抽樣才能比
            arms[f"先驗:{name}"] = ({str(r): score_events(build_events(t, pi, ps, mid, dur, r), labels, o2, mid, dur) for r in RATES}
                                  if name == "local" else sample_prior_hits(t, pr, labels, o2, mid, dur, RATES))
            # lambda 只看前半，後半才是結果
            o1 = [o for o in occ if o["t"] < mid]
            best, best_hits = LAMBDAS[0], -1
            for lam in LAMBDAS:
                sc = logv + lam * logp
                i, s = sc.argmax(1), sc.max(1)
                h = score_events(build_events(t, i, s, 0, mid, 5), labels, o1, 0, mid)["hits"]
                if h > best_hits:
                    best, best_hits = lam, h
            sc = logv + best * logp
            i, s = sc.argmax(1), sc.max(1)
            arms[f"視覺+先驗:{name}"] = {"lambda": best, **{str(r): score_events(build_events(t, i, s, mid, dur, r), labels, o2, mid, dur)
                                                           for r in RATES}}
        res["arms"] = arms
        results[f"{model}@{size}"] = res
        print(f"== {model} {size}s  詞彙 {V}、後半可比對 {len(o2)}", flush=True)
        for a, v in arms.items():
            print(f"  {a:18s} " + " ".join(f"{r}/分 {v[str(r)]['hits']}/{v[str(r)]['n']}={v[str(r)]['precision']:.1%}"
                                           f"({v[str(r)]['precision_base']:.1%})" for r in RATES), flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "rerank.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------- streams ----------
def fmt_stream(pairs):
    """[(秒, 詞)] → 每分鐘一行，不帶任何實驗資訊。"""
    lines = {}
    for t, g in sorted(pairs):
        lines.setdefault(int(t // 60), []).append(g)
    return "\n".join(f"[{m:02d}] " + " ".join(w) for m, w in sorted(lines.items())) + "\n"


def cmd_streams(args):
    import spotbench as sb
    from app import config
    from app.inference import Classifier

    raw, fps = load_raw()
    dur = len(raw) / fps
    clf = Classifier(ROOT / "models" / "20261018-w2000n")
    spot = Classifier(ROOT / "models" / "20261019-w2000bg")
    sb.SPOT["classify"] = sb.Cached(spot)
    p = {"window": config.SPOT_WINDOW, "hop": config.SPOT_HOP, "hits": config.SPOT_MIN_HITS,
         "th": config.SPOT_THRESHOLD, "after": config.CONTINUOUS_AFTER, "spot": True}
    shown = sb.decode(sb.Cached(clf), raw, fps, p)
    online = [(float((s.start + s.end) / 2), s.prediction.gloss) for s in shown]

    d = np.load(run_path("20261018-w2000n-2000", 1.0))
    labels2k = [str(x) for x in d["labels"]]
    P = d["probs"]
    vp, vis = P.max(1), P.argmax(1)
    m = vp >= 0.5
    model2k = [(float(e[0]), labels2k[e[1]]) for e in build_events(d["t"][m], vis[m], vp[m], 0, dur, 1e9)]

    true100 = [(o["t"], o["gloss"]) for o in load_occ(clf.labels)]
    true2k = [(o["t"], o["gloss"]) for o in load_occ(labels2k)]
    rng = np.random.default_rng(0)

    def degrade(recall, precision):
        keep = [true2k[i] for i in np.flatnonzero(rng.random(len(true2k)) < recall)]
        n_false = round(len(keep) * (1 - precision) / precision)
        false = [(float(rng.uniform(0, dur)), labels2k[rng.integers(len(labels2k))]) for _ in range(n_false)]
        return keep + false

    random_n = [(float(rng.uniform(0, dur)), labels2k[rng.integers(len(labels2k))]) for _ in model2k]
    arms = {"online": online, "model2000": model2k, "perfect100": true100, "perfect2000": true2k,
            "sim_r30_p70": degrade(0.3, 0.7), "sim_r10_p50": degrade(0.1, 0.5), "random": random_n}
    # 檔名打散，盲讀者看不出是哪一組；對照表另存
    names = "abcdefg"
    perm = rng.permutation(len(arms))
    key = {}
    args.folder.mkdir(parents=True, exist_ok=True)
    for j, (arm, pairs) in zip(perm, arms.items()):
        (args.folder / f"stream_{names[j]}.txt").write_text(fmt_stream(pairs), encoding="utf-8")
        key[names[j]] = {"arm": arm, "words": len(pairs)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "stream_key.json").write_text(json.dumps(key, indent=1, sort_keys=True), encoding="utf-8")
    (OUT / "online_output.json").write_text(json.dumps(online, ensure_ascii=False), encoding="utf-8")
    print(f"詞串已寫入 {args.folder}；對照表 {OUT / 'stream_key.json'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("windows").set_defaults(fn=cmd_windows)
    sub.add_parser("shift").set_defaults(fn=cmd_shift)
    sub.add_parser("rerank").set_defaults(fn=cmd_rerank)
    a = sub.add_parser("streams"); a.add_argument("folder", type=Path); a.set_defaults(fn=cmd_streams)
    args = ap.parse_args()
    args.fn(args)
