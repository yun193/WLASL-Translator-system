"""單字亂認（詞彙表外）評估：比較不同訊號，在相同誤報率下誰保留最多正確輸出。

  uv run --project backend python scripts/oovbench.py          比較各種訊號
  uv run --project backend python scripts/oovbench.py verify   後端實際路徑的前後對照

訊號來源：w2000n 其實訓練了 2000 類，上線版只留前 100 類再 softmax，「不是這 100 詞」的訊號被丟掉了；
另外 w2000bg 是獨立訓練的第二個模型，可以看兩者是否同意。

用和後端相同的解碼器重播，看使用者實際看到的輸出：
  WLASL test：依 video_id 奇偶分兩半。偶數半只用詞彙表外的詞定門檻（誤報率達到目標），奇數半驗證。
  YouTube：沒拿來定門檻，當獨立驗證。快速影片的章節才算得出詞彙表外的誤報。
限制：這 1900 詞模型都學過，完全沒學過的詞的拒絕效果可能比較差。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "docs" / "open-set" / "metrics.json"
K = 100
TARGETS = (0.20, 0.15, 0.10, 0.05)


class Full:
    """回傳和上線相同的 100 類預測，另外附上各種拒絕訊號。"""

    def __init__(self, model_dir, second_dir):
        from app.inference import Classifier

        self.clf, self.second = Classifier(model_dir), Classifier(second_dir)

    def predict(self, frames):
        from app.inference import softmax
        from wlasl.dataset import prepare
        from wlasl.spotter import Prediction

        logits = self.clf.session.run(None, {"keypoints": prepare(frames, mode=self.clf.mode)[None]})[0][0]
        other = self.second.session.run(None, {"keypoints": prepare(frames, mode=self.second.mode)[None]})[0][0]
        cond, full, cond2 = softmax(logits[:K]), softmax(logits), softmax(other[:K])
        order = np.argsort(-cond)[:5]
        top = order[0]
        ens = (cond + cond2) / 2
        p = Prediction(gloss=self.clf.labels[top], prob=float(cond[top]), top5=[(self.clf.labels[i], float(cond[i])) for i in order])
        p.signal = {"cond": float(cond[top]), "full": float(full[top]), "mass": float(full[:K].sum()),
                    "maxlogit": float(logits[top]), "energy": float(np.logaddexp.reduce(logits[:K])),
                    "margin": float(cond[top] - cond[order[1]]), "agree": bool(cond2.argmax() == top),
                    "second": float(cond2[top]), "bg": float(softmax(other)[-1]),
                    "ens": float(ens.max()), "ens_gloss": self.clf.labels[int(ens.argmax())]}
        return p


# 分數越高越保留；ens_gloss 為 True 時輸出兩個模型平均後的第一名
SCORES = {
    "現行信心": (lambda s: s["cond"], False),
    "2000 類機率": (lambda s: s["full"], False),
    "詞彙表機率和×信心": (lambda s: s["mass"] * s["cond"], False),
    "最大 logit": (lambda s: s["maxlogit"], False),
    "energy": (lambda s: s["energy"], False),
    "前兩名差距": (lambda s: s["margin"], False),
    "雙模型同意×信心": (lambda s: s["agree"] * s["cond"], False),
    "雙模型同意×2000 類機率": (lambda s: s["agree"] * s["full"], False),
    "第二模型對同詞的信心×信心": (lambda s: s["second"] * s["cond"], False),
    "雙模型平均（換輸出）": (lambda s: s["ens"], True),
}


def shown(signs, score, th):
    """[(中點秒, gloss)]。窗口偵測的輸出不受影響（只有整段分類有這些訊號）。"""
    fn, use_ens = score
    out = []
    for s in signs:
        mid = (s.start + s.end) / 2
        if s.mode == "spot":
            out.append((mid, s.prediction.gloss))
        elif fn(s.prediction.signal) >= th:
            out.append((mid, s.prediction.signal["ens_gloss"] if use_ens else s.prediction.gloss))
    return out


def wlasl_metrics(rows, score, th, rate):
    inv = [(g, shown(sg, score, th)) for g, known, sg in rows if known]
    oov = [shown(sg, score, th) for _, known, sg in rows if not known]
    return {"first_correct": rate(sum(bool(x) and x[0][1] == g for g, x in inv), len(inv)),
            "no_output": rate(sum(not x for _, x in inv), len(inv)),
            "oov_false": rate(sum(bool(x) for x in oov), len(oov))}


def yt_metrics(videos, score, th, rate):
    first = silent = n = oov_false = oov = correct = total = 0
    for fast, rows, chapters_oov, signs in videos:
        out = shown(signs, score, th)
        for a, b, gold in rows:
            inside = [g for t, g in out if a <= t < b]
            n += 1
            silent += not inside
            first += bool(inside) and inside[0] in gold
            if fast and inside:
                total += 1
                correct += inside[0] in gold
        if fast:
            for a, b in chapters_oov:
                oov += 1
                hit = any(a <= t < b for t, _ in out)
                oov_false += hit
                total += hit
    return {"first_correct": rate(first, n), "no_output": rate(silent, n), "oov_false": rate(oov_false, oov),
            "shown_correct": rate(correct, total)}


def pick_threshold(rows, score, target, rate):
    """詞彙表外誤報率不超過目標的最低門檻（只看詞彙表外的詞，不看正確率）。"""
    values = [score[0](s.prediction.signal) for _, known, sg in rows if not known for s in sg if s.mode != "spot"]
    for th in np.unique(np.quantile(values, np.linspace(0, 1, 401))):
        if wlasl_metrics(rows, score, float(th), rate)["oov_false"]["rate"] <= target:
            return float(th)
    return float(max(values))


def main():
    from app import config, winperf
    import spotbench as sb
    import ytbench as yb

    winperf.disable_power_throttling()
    config.MIN_CONFIDENCE = 0.0  # 規則在這裡才套用，解碼器先全部留下
    full = Full(yb.MODEL_2000, yb.SPOT_MODEL)
    classify = sb.Cached(full)
    sb.SPOT["classify"] = sb.Cached(full.second)
    p = {"window": config.SPOT_WINDOW, "hop": config.SPOT_HOP, "hits": config.SPOT_MIN_HITS, "th": config.SPOT_THRESHOLD,
         "after": config.CONTINUOUS_AFTER, "spot": True}
    vocab = full.clf.labels[:K]
    inv, oov, labels, _ = sb.load_test(vocab)
    rows = {0: [], 1: []}
    for known, recs in ((True, inv), (False, oov)):
        for r, s in recs:
            rows[int(r["video_id"]) % 2].append((labels[r["label"]], known, sb.decode(classify, s, r.get("fps") or 25.0, p)))
    print("WLASL 解碼完成", len(inv), len(oov), flush=True)

    videos = []
    for i, vid in enumerate(yb.WORD_VIDEOS):
        d = np.load(yb.DATA / vid / "kp.npz")
        signs = sb.decode(classify, d["raw"], float(d["fps"]), p)
        gold_rows = yb.chapters(vid, set(vocab))[0]
        starts = {r[0] for r in gold_rows}
        info = json.loads((yb.DATA / vid / "info.json").read_text(encoding="utf-8"))
        chapters_oov = [(float(c["start_time"]), float(c["end_time"])) for c in info["chapters"]
                        if not yb.SKIP.match(c["title"].strip()) and float(c["start_time"]) not in starts]
        videos.append((i < 2, gold_rows, chapters_oov, signs))
    print("YouTube 解碼完成", flush=True)

    res = {}
    for target in TARGETS:
        print(f"\n== 詞彙表外誤報目標 {target:.0%}（門檻只用偶數半定）", flush=True)
        for name, score in SCORES.items():
            th = pick_threshold(rows[0], score, target, yb.rate)
            h, y = wlasl_metrics(rows[1], score, th, yb.rate), yt_metrics(videos, score, th, yb.rate)
            res.setdefault(str(target), {})[name] = {"threshold": th, "holdout": h, "youtube": y}
            print(f"{name:20} 門檻{th:7.3f}｜驗證 對{h['first_correct']['k']:2}/{h['first_correct']['n']} 無{h['no_output']['rate']:.2f} 亂{h['oov_false']['rate']:.3f}"
                  f"｜YT 對{y['first_correct']['k']:2}/{y['first_correct']['n']} 無{y['no_output']['rate']:.2f} 亂{y['oov_false']['rate']:.2f} 輸出正確{y['shown_correct']['rate']:.2f}",
                  flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


def verify():
    """後端實際的路徑（Classifier／Ensemble、信心門檻 config.MIN_CONFIDENCE）前後對照。"""
    from app import config, winperf
    from app.inference import Classifier, Ensemble
    import spotbench as sb
    import ytbench as yb

    winperf.disable_power_throttling()
    single, spot = Classifier(yb.MODEL), Classifier(yb.SPOT_MODEL)
    sb.SPOT["classify"] = sb.Cached(spot)
    p = {"window": config.SPOT_WINDOW, "hop": config.SPOT_HOP, "hits": config.SPOT_MIN_HITS, "th": config.SPOT_THRESHOLD,
         "after": config.CONTINUOUS_AFTER, "spot": True}
    inv, oov, labels, _ = sb.load_test(single.labels)
    keep = (lambda _: 1.0, False)

    def tagged(classify, raw, fps):
        signs = sb.decode(classify, raw, fps, p)
        for s in signs:
            s.prediction.signal = {}
        return signs

    res = {}
    for name, clf in (("現行：w2000n", single), ("雙模型平均", Ensemble(single, spot))):
        classify = sb.Cached(clf)
        rows = {0: [], 1: []}
        for known, recs in ((True, inv), (False, oov)):
            for r, s in recs:
                rows[int(r["video_id"]) % 2].append((labels[r["label"]], known, tagged(classify, s, r.get("fps") or 25.0)))
        videos = []
        for i, vid in enumerate(yb.WORD_VIDEOS):
            d = np.load(yb.DATA / vid / "kp.npz")
            gold_rows = yb.chapters(vid, set(single.labels))[0]
            starts = {r[0] for r in gold_rows}
            info = json.loads((yb.DATA / vid / "info.json").read_text(encoding="utf-8"))
            chapters_oov = [(float(c["start_time"]), float(c["end_time"])) for c in info["chapters"]
                            if not yb.SKIP.match(c["title"].strip()) and float(c["start_time"]) not in starts]
            videos.append((i < 2, gold_rows, chapters_oov, tagged(classify, d["raw"], float(d["fps"]))))
        res[name] = {"wlasl_all": wlasl_metrics(rows[0] + rows[1], keep, 0.0, yb.rate),
                     "wlasl_holdout": wlasl_metrics(rows[1], keep, 0.0, yb.rate), "youtube": yt_metrics(videos, keep, 0.0, yb.rate)}
        print(name, json.dumps({k: {m: (x["k"], x["n"], round(x["ci95"][0], 3), round(x["ci95"][1], 3)) for m, x in v.items()}
                                for k, v in res[name].items()}, ensure_ascii=False), flush=True)
    (OUT.parent / "verify.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    verify() if sys.argv[1:] == ["verify"] else main()
