"""窗口偵測的亂認：比較不同的輸出規則，在相同誤報率下誰保留最多對的詞。

  uv run --project backend python scripts/spotgate.py cache   每個窗口算一次兩個模型的訊號（存 data/spot_cache）
  uv run --project backend python scripts/spotgate.py         比較規則，寫 docs/spot-gate/metrics.json

切詞器和解碼狀態不受窗口結果影響，所以訊號只要算一次，之後照 Spotter.update 的規則重播，換門檻不必再跑模型。
合成連續手語依 video_id 奇偶分兩半：偶數半定門檻，奇數半、podcast 後半、YouTube 只驗證。
"""

from __future__ import annotations

import json
import pickle
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

CACHE = ROOT / "data" / "spot_cache"
OUT = ROOT / "docs" / "spot-gate" / "metrics.json"
K = 100
HITS = (1, 2, 3)
FALSE_TARGETS = (1.0, 0.75, 0.5, 0.25)  # 相對現行規則在偶數半的每分鐘誤報


class Signals:
    """一個窗口 → 兩個模型的所有訊號。"""

    def __init__(self, model_2000, spot_model):
        from app.inference import Classifier

        self.n, self.bg = Classifier(model_2000), Classifier(spot_model)
        self.rows = []

    def __call__(self, frames):
        from app.inference import softmax

        ln, lb = self.n.logits(frames), self.bg.logits(frames)
        cond, full, pb, cond_b = softmax(ln[:K]), softmax(ln), softmax(lb), softmax(lb[:K])
        word_b, word_n = int(pb[:K].argmax()), int(cond.argmax())
        ens = (cond + cond_b) / 2
        word_e = int(ens.argmax())
        self.rows.append((word_b, float(pb[word_b]), float(pb[K]), word_n, float(cond[word_n]), float(cond[word_b]),
                          float(full[word_b]), float(full[:K].sum()), word_e, float(ens[word_e]), float(full[word_e])))
        return None


COLS = ("word_b", "p_b", "bg", "word_n", "p_n", "n_of_b", "full_of_b", "mass", "word_e", "p_e", "full_of_e")


@dataclass
class Recorder:
    """假的 Spotter：不判斷，只記下每個窗口的起訖、是否中斷連續命中、輸出時會不會被丟掉。"""

    inner: object
    decoder: object = None
    spans: list = field(default_factory=list)
    gaps: list = field(default_factory=list)
    keep: list = field(default_factory=list)
    pending: list = field(default_factory=list)
    gap: bool = True

    def push(self, t, frame):
        before = self.inner._next_t
        win = self.inner.push(t, frame)
        if win is None and self.inner._next_t != before:
            self.gap = True  # 到了該分類的時間，但窗口裡手太少
        return win

    def update(self, start, end, _):
        self.spans.append((start, end))
        self.gaps.append(self.gap)
        self.gap = False
        self.keep.append(self.decoder.continuous)
        if not self.decoder.continuous:
            self.pending.append(len(self.keep) - 1)
        return None

    def reset(self):
        self.inner.reset()
        self.gap = True


def record(raw, fps, classify, signals):
    """跑真正的解碼器一次：回傳窗口紀錄和整段分類的輸出（[(起, 迄, gloss)]）。"""
    from app import config
    from wlasl.segmenter import Segmenter
    from wlasl.spotter import SignDecoder, Spotter

    signals.rows = []
    seg = Segmenter(rest=config.REST_SECONDS, pre_roll=config.PRE_ROLL_SECONDS,
                    min_len=config.MIN_SIGN_SECONDS, max_len=config.MAX_SIGN_SECONDS)
    rec = Recorder(Spotter(window=config.SPOT_WINDOW, hop=config.SPOT_HOP, min_hits=1, threshold=config.SPOT_THRESHOLD))
    dec = SignDecoder(classify, seg, rec, continuous_after=config.CONTINUOUS_AFTER, spot_classify=signals)
    rec.decoder = dec
    segments = []

    def take(signs):
        segments.extend((s.start, s.end, s.prediction.gloss) for s in signs
                        if s.prediction.prob >= config.MIN_CONFIDENCE and not s.prediction.is_background)

    for i, f in enumerate(raw):
        signs = dec.push(i / fps, f)
        take(signs)
        if dec.continuous:
            for j in rec.pending:
                rec.keep[j] = True
            rec.pending = []
        elif signs:  # 單字模式下切出一段：暫存的偵測結果丟掉
            rec.pending = []
    take(dec.flush())
    return {"spans": np.array(rec.spans, np.float32).reshape(-1, 2), "gaps": np.array(rec.gaps, bool),
            "keep": np.array(rec.keep, bool), "signals": np.array(signals.rows, np.float32).reshape(-1, len(COLS)),
            "segments": segments, "minutes": len(raw) / fps / 60}


def cmd_cache():
    from app import winperf
    from app.inference import Classifier, Ensemble
    import spotbench as sb
    import ytbench as yb

    winperf.disable_power_throttling()
    CACHE.mkdir(parents=True, exist_ok=True)
    single, spot = Classifier(yb.MODEL), Classifier(yb.SPOT_MODEL)
    classify = sb.Cached(Ensemble(single, spot))
    signals = Signals(yb.MODEL_2000, yb.SPOT_MODEL)
    inv, oov, labels, span = sb.load_test(single.labels)
    res = {"labels": list(single.labels), "synth": {}, "yt": {}}
    for part in (0, 1):
        pick = lambda recs: [(r, s) for r, s in recs if int(r["video_id"]) % 2 == part]
        rows = []
        for raw, gt in sb.build_synth(pick(inv), pick(oov), labels, span, seed=part):
            rows.append({**record(raw, sb.FPS, classify, signals), "gt": gt})
        res["synth"][part] = rows
        print("合成", part, sum(len(r["keep"]) for r in rows), flush=True)
    d = np.load(sb.PODCAST_KP)
    raw, fps = d["raw"], float(d["fps"])
    res["podcast"] = {"fps": fps, "dur": len(raw) / fps}
    for part, (a, b) in {1: (0, len(raw) // 2), 2: (len(raw) // 2, len(raw))}.items():
        res["podcast"][part] = {**record(raw[a:b], fps, classify, signals), "offset": a / fps}
        print("podcast", part, flush=True)
    for vid in {**yb.WORD_VIDEOS, **yb.TALK_VIDEOS}:
        d = np.load(yb.DATA / vid / "kp.npz")
        res["yt"][vid] = {**record(d["raw"], float(d["fps"]), classify, signals), "dur": len(d["raw"]) / float(d["fps"])}
        print(vid, len(res["yt"][vid]["keep"]), flush=True)
    (CACHE / "signals.pkl").write_bytes(pickle.dumps(res))


# ---------- 規則：回傳每個窗口的 (輸出的詞, 分數)。分數高於門檻才算命中 ----------
def col(rec, name):
    return rec["signals"][:, COLS.index(name)]


def not_bg(rec, p):
    return p * (p > col(rec, "bg"))


RULES = {
    "現行（w2000bg 信心）": lambda r: (col(r, "word_b"), not_bg(r, col(r, "p_b"))),
    "雙模型平均": lambda r: (col(r, "word_e"), not_bg(r, col(r, "p_e"))),
    "雙模型同意×信心": lambda r: (col(r, "word_b"), not_bg(r, col(r, "p_b")) * (col(r, "word_n") == col(r, "word_b"))),
    "第二模型對同詞的信心": lambda r: (col(r, "word_b"), np.sqrt(not_bg(r, col(r, "p_b")) * col(r, "n_of_b"))),
    "2000 類機率": lambda r: (col(r, "word_b"), np.sqrt(not_bg(r, col(r, "p_b")) * col(r, "full_of_b"))),
    "兩模型取低×2000 類": lambda r: (col(r, "word_b"), np.minimum(not_bg(r, col(r, "p_b")), col(r, "full_of_b"))),
    "雙模型平均×2000 類": lambda r: (col(r, "word_e"), np.sqrt(not_bg(r, col(r, "p_e")) * col(r, "full_of_e"))),
}


def replay(rec, rule, th, hits, labels):
    """和 Spotter.update 相同的規則；回傳 [(起, 迄, gloss)]，含整段分類的輸出。"""
    words, scores = RULES[rule](rec)
    out, run, last, emitted = [], 0, None, False
    start = 0.0
    for i, (w, s) in enumerate(zip(words, scores)):
        ok = s >= th
        if rec["gaps"][i] or not ok or (run and last != w):
            run, emitted = 0, False
        if not ok:
            continue
        if run == 0:
            start = rec["spans"][i][0]
        run, last = run + 1, w
        if run >= hits and not emitted:
            emitted = True
            if rec["keep"][i]:
                out.append((float(start), float(rec["spans"][i][1]), labels[int(w)]))
    return out + list(rec["segments"])


# ---------- 評估 ----------
def synth_metrics(rows, rule, th, hits, labels, tol=0.25):
    tp = false = known = 0
    minutes = 0.0
    for r in rows:
        gt, used = r["gt"], set()
        minutes += r["minutes"]
        known += sum(g[3] for g in gt)
        for a, b, gloss in replay(r, rule, th, hits, labels):
            hit = next((i for i, (g, x, y, k) in enumerate(gt) if k and g == gloss and i not in used
                        and a <= y + tol and b >= x - tol), None)
            if hit is None:
                false += 1
            else:
                used.add(hit)
                tp += 1
    return {"recall": tp / known, "false_per_min": false / minutes, "precision": tp / (tp + false) if tp + false else 0.0,
            "outputs_per_min": (tp + false) / minutes}


def podcast_metrics(res, occ, rule, th, hits, labels):
    import longvideo as lv

    rec = res["podcast"][2]
    lo, hi = rec["offset"], res["podcast"]["dur"]
    ev = [((a + b) / 2, g) for a, b, g in replay(rec, rule, th, hits, labels)]
    orel = [{**x, "t": x["t"] - lo} for x in occ if lo <= x["t"] < hi]
    p, pb = lv.with_baseline(lv.precision, ev, orel, hi - lo, 4, 2)
    r, rb = lv.with_baseline(lv.recall, ev, orel, hi - lo, 4, 2)
    return {"outputs": len(ev), "precision": p, "precision_base": pb, "recall": r, "recall_base": rb, "occurrences": len(orel)}


def talk_metrics(res, occs, rule, th, hits, labels):
    import longvideo as lv
    import ytbench as yb

    outs = hit = rec_hit = occ_n = 0
    base = 0.0
    for vid in yb.TALK_VIDEOS:
        rec = res["yt"][vid]
        ev = [((a + b) / 2, g) for a, b, g in replay(rec, rule, th, hits, labels)]
        p, pb = lv.with_baseline(lv.precision, ev, occs[vid], rec["dur"], 3, 3)
        r = lv.recall(ev, occs[vid], 3, 3)
        outs += len(ev)
        hit += round(p * len(ev))
        base += pb * len(ev)
        rec_hit += r * len(occs[vid])
        occ_n += len(occs[vid])
    return {"outputs": outs, "hits": hit, "precision": hit / outs if outs else 0.0, "precision_base": base / outs if outs else 0.0,
            "recall": rec_hit / occ_n}


def word_metrics(res, rule, th, hits, labels):
    """教學與快速影片：章節答案已知。"""
    import ytbench as yb

    vocab = set(labels)
    first = n = silent = matched = in_ch = minutes = spot_out = 0
    for vid in yb.WORD_VIDEOS:
        rec = res["yt"][vid]
        ev = [((a + b) / 2, g) for a, b, g in replay(rec, rule, th, hits, labels)]
        minutes += rec["minutes"]
        spot_out += len(ev) - len(rec["segments"])
        for a, b, gold in yb.chapters(vid, vocab)[0]:
            inside = [g for t, g in ev if a <= t < b]
            n += 1
            silent += not inside
            first += bool(inside) and inside[0] in gold
            in_ch += len(inside)
            matched += sum(g in gold for g in inside)
    return {"first_correct": first, "chapters": n, "no_output": silent, "outputs_in_chapter": in_ch, "matched": matched,
            "spot_outputs": spot_out, "spot_per_min": spot_out / minutes}


def pick_threshold(rows, rule, hits, limit, labels):
    scores = np.concatenate([RULES[rule](r)[1] for r in rows])
    grid = np.unique(np.quantile(scores[scores > 0], np.linspace(0, 1, 201)))
    for th in grid:
        if synth_metrics(rows, rule, float(th), hits, labels)["false_per_min"] <= limit:
            return float(th)
    return float(grid[-1])


def main():
    import longvideo as lv
    import spotbench as sb
    import ytbench as yb
    from app import config

    res = pickle.loads((CACHE / "signals.pkl").read_bytes())
    labels = res["labels"]
    occ = lv.match_vocab(lv.flat_tokens(json.loads((sb.PODCAST / "transcript.json").read_text(encoding="utf-8"))), set(labels))
    occs = {v: lv.match_vocab(lv.flat_tokens(yb.load_caption_words(v)), set(labels)) for v in yb.TALK_VIDEOS}
    tune, hold = res["synth"][0], res["synth"][1]

    def row(rule, th, hits):
        return {"threshold": th, "hits": hits, "tune": synth_metrics(tune, rule, th, hits, labels),
                "holdout": synth_metrics(hold, rule, th, hits, labels), "podcast2": podcast_metrics(res, occ, rule, th, hits, labels),
                "talk": talk_metrics(res, occs, rule, th, hits, labels), "word": word_metrics(res, rule, th, hits, labels)}

    def show(name, x):
        h, q, t, w = x["holdout"], x["podcast2"], x["talk"], x["word"]
        print(f"{name:26} 門檻{x['threshold']:.3f} 連{x['hits']}｜定 召{x['tune']['recall']:.3f} 誤{x['tune']['false_per_min']:5.1f}"
              f"｜驗 召{h['recall']:.3f} 精{h['precision']:.3f} 誤{h['false_per_min']:5.1f}"
              f"｜pod 出{q['outputs']:3} 精{q['precision']:.3f}({q['precision_base']:.3f}) 召{q['recall']:.3f}"
              f"｜對話 出{t['outputs']:3} 中{t['hits']:2} 精{t['precision']:.3f}({t['precision_base']:.3f})"
              f"｜單字 對{w['first_correct']}/{w['chapters']} 無{w['no_output']} 窗口輸出/分{w['spot_per_min']:.1f} 相符{w['matched']}/{w['outputs_in_chapter']}", flush=True)

    current = row("現行（w2000bg 信心）", config.SPOT_THRESHOLD_SINGLE, config.SPOT_MIN_HITS)
    show("現行", current)
    out = {"current": current, "targets": {}}
    limit0 = current["tune"]["false_per_min"]
    for f in FALSE_TARGETS:
        print(f"\n== 偶數半誤報 ≤ 現行的 {f:.0%}（{limit0 * f:.1f}/分）", flush=True)
        for rule in RULES:
            for hits in HITS:
                x = row(rule, pick_threshold(tune, rule, hits, limit0 * f, labels), hits)
                out["targets"].setdefault(str(f), {})[f"{rule}/連{hits}"] = x
                show(f"{rule} 連{hits}", x)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


def verify():
    """真正的解碼器（不經過上面的重播）跑前後對照，順便確認重播的數字沒有走樣。"""
    import longvideo as lv
    import oovbench as ob
    import spotbench as sb
    import ytbench as yb
    from app import config, winperf
    from app.inference import Classifier, Ensemble

    winperf.disable_power_throttling()
    single, spot = Classifier(yb.MODEL), Classifier(yb.SPOT_MODEL)
    classify = sb.Cached(Ensemble(single, spot))
    inv, oov, labels, span = sb.load_test(single.labels)
    odd = lambda recs: [(r, s) for r, s in recs if int(r["video_id"]) % 2 == 1]
    seqs = sb.build_synth(odd(inv), odd(oov), labels, span, seed=1)
    vocab = set(single.labels)
    d = np.load(sb.PODCAST_KP)
    pod_raw, pod_fps = d["raw"], float(d["fps"])
    occ = lv.match_vocab(lv.flat_tokens(json.loads((sb.PODCAST / "transcript.json").read_text(encoding="utf-8"))), vocab)
    keep = (lambda _: 1.0, False)
    res = {}
    for name, spot_clf, th in (("現行：w2000bg 0.7", spot, config.SPOT_THRESHOLD_SINGLE),
                               ("雙模型平均 0.78", Ensemble(single, spot, use_background=True), 0.78)):
        sb.SPOT["classify"] = sb.Cached(spot_clf)
        p = {"window": config.SPOT_WINDOW, "hop": config.SPOT_HOP, "hits": config.SPOT_MIN_HITS, "th": th,
             "after": config.CONTINUOUS_AFTER, "spot": True}

        def tagged(raw, fps):
            signs = sb.decode(classify, raw, fps, p)
            for s in signs:
                s.prediction.signal = {}
            return signs

        rows = [(labels[r["label"]], known, tagged(s, r.get("fps") or 25.0)) for known, recs in ((True, inv), (False, oov)) for r, s in recs]
        x = {"wlasl": ob.wlasl_metrics(rows, keep, 0.0, yb.rate), "synth": sb.synth(classify, seqs, p),
             "podcast2": sb.podcast(classify, pod_raw, pod_fps, occ, p, 2)}
        videos, teach = [], {"spot": 0, "outside": 0, "minutes": 0.0}
        for i, vid in enumerate(yb.WORD_VIDEOS):
            d = np.load(yb.DATA / vid / "kp.npz")
            signs = tagged(d["raw"], float(d["fps"]))
            gold = yb.chapters(vid, vocab)[0]
            starts = {g[0] for g in gold}
            info = json.loads((yb.DATA / vid / "info.json").read_text(encoding="utf-8"))
            ch_oov = [(float(c["start_time"]), float(c["end_time"])) for c in info["chapters"]
                      if not yb.SKIP.match(c["title"].strip()) and float(c["start_time"]) not in starts]
            videos.append((i < 2, gold, ch_oov, signs))
            spots = [(s.start + s.end) / 2 for s in signs if s.mode == "spot"]
            teach["spot"] += len(spots)
            teach["outside"] += sum(not any(a <= t < b for a, b, _ in gold) for t in spots)
            teach["minutes"] += len(d["raw"]) / float(d["fps"]) / 60
        x["youtube_word"], x["window_outputs"] = ob.yt_metrics(videos, keep, 0.0, yb.rate), teach
        outs = hits = 0
        for vid in yb.TALK_VIDEOS:
            d = np.load(yb.DATA / vid / "kp.npz")
            ev = [((s.start + s.end) / 2, s.prediction.gloss) for s in tagged(d["raw"], float(d["fps"]))]
            outs += len(ev)
            hits += round(lv.precision(ev, lv.match_vocab(lv.flat_tokens(yb.load_caption_words(vid)), vocab), 3, 3) * len(ev))
        x["talk"] = {"outputs": outs, "hits": hits}
        res[name] = x
        print(name, json.dumps(x, ensure_ascii=False), flush=True)
    (OUT.parent / "verify.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    {"cache": cmd_cache, "verify": verify}.get(sys.argv[1] if sys.argv[1:] else "", main)()
