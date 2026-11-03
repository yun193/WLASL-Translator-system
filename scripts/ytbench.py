"""YouTube ASL 影片泛化測試：換人、換鏡頭、換拍攝環境，看現行模型還剩多少。用來部分取代鏡頭實測（測不到即時幀率與延遲）。

  uv run --project backend python scripts/ytbench.py fetch     下載影片（只要畫面）、章節、人工字幕，並擷取關鍵點
  uv run --project backend python scripts/ytbench.py eval      用上線設定評估，不針對這批影片調參
  uv run --project backend python scripts/ytbench.py summary   合併各影片的數字，寫回 metrics.json

單字影片：章節逐詞標好時間，答案已知。整段分類只算短章節（快速版），教學章節裡還有解說，看窗口與解碼器輸出；
  同一批詞的 WLASL test 正確率當對照，機率基準是把答案換到同一支影片的其他章節。
連續影片：人工字幕和手語大致同步，對齊容許前後 3 秒；字幕是英文翻譯，不是 ASL gloss，要和機率基準一起看。
影片與字幕都留在 data/ytasl/（不進 git）。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

DATA = ROOT / "data" / "ytasl"
OUT = ROOT / "docs" / "yt-generalization"
WORD_VIDEOS = {
    "stCwx6SXgSA": "Learn How to Sign（快速）",
    "G6hVRVG74lc": "Learn How to Sign（快速 2）",
    "0FcwzMq4iWg": "Learn How to Sign（教學）",
    "4Ll3OtqAzyw": "Learn How to Sign（教學 2）",
    "Whr6gdjUEnM": "Signing With Omar（教學）",
    "qa9qSPsj840": "Chris Gorges（教學）",
}
TALK_VIDEOS = {
    "zwSenYyboaw": "Rikki Poynter（vlog）",
    "9BJ9to5o2cs": "Rogan Shannon（vlog）",
    "HR6ZPhkxJ3c": "Sign Duo（雙人對話）",
}
MODEL = ROOT / "models" / "20261018-w2000n"
MODEL_2000 = ROOT / "models" / "20261018-w2000n-2000"
SPOT_MODEL = ROOT / "models" / "20261019-w2000bg"
SHORT_CHAPTER = 6.0
SKIP = re.compile(r"^(\*|<|intro|outro|review|teaching|asl structure|tornado)", re.I)


# ---------- fetch ----------
def cmd_fetch(_):
    import longvideo as lv

    for vid in {**WORD_VIDEOS, **TALK_VIDEOS}:
        d = DATA / vid
        d.mkdir(parents=True, exist_ok=True)
        kp = d / "kp.npz"
        if kp.exists():
            continue
        url = f"https://youtu.be/{vid}"
        info = json.loads(subprocess.run(["yt-dlp", "--no-warnings", "--skip-download", "-j", url], capture_output=True,
                                         text=True, encoding="utf-8", check=True).stdout)
        (d / "info.json").write_text(json.dumps({k: info.get(k) for k in ("id", "title", "channel", "duration", "chapters")},
                                                ensure_ascii=False), encoding="utf-8")
        if vid in TALK_VIDEOS:
            subprocess.run(["yt-dlp", "--no-warnings", "--skip-download", "--write-subs", "--sub-langs", "en",
                            "--sub-format", "vtt", "-o", str(d / "subs"), url], check=True, capture_output=True)
        video = d / "video.mp4"
        if not video.exists():
            subprocess.run(["yt-dlp", "--no-warnings", "-f", "bv*[height<=720][vcodec^=avc1]", "-o", str(video), url],
                           check=True, capture_output=True)
        print(f"{vid} {video.stat().st_size / 1e6:.0f} MB", flush=True)
        lv.extract(video, kp)


# ---------- labels ----------
def parse_chapter(title):
    """'12. It/She/Him' → ['it', 'she', 'him']；'Not, Don't or Doesn't' → 三個替代答案。"""
    t = re.sub(r"^\d+\.\s*", "", title).strip().lower().replace("thank-you", "thank you").rstrip("?!.")
    return [x.strip() for x in re.split(r"/|,| or ", t) if x.strip()]


def chapters(vid, vocab):
    """回傳 [(起, 迄, 答案集合)]，只留答案在詞彙表內的章節，另回傳章節總數。"""
    import longvideo as lv

    info = json.loads((DATA / vid / "info.json").read_text(encoding="utf-8"))
    rows, total = [], 0
    for c in info["chapters"]:
        if SKIP.match(c["title"].strip()):
            continue
        total += 1
        gold = set()
        for alt in parse_chapter(c["title"]):
            gold |= {alt} if alt in vocab else {v for v in lv.variants(alt) if v in vocab}
        if gold:
            rows.append((float(c["start_time"]), float(c["end_time"]), gold))
    return rows, total


def load_caption_words(vid):
    """人工字幕 VTT → [{t, w}]，一行裡的字平均分配到字幕的時間範圍。"""
    def sec(s):
        h, m, r = s.split(":")
        return int(h) * 3600 + int(m) * 60 + float(r)

    words = []
    for block in re.split(r"\n\s*\n", (DATA / vid / "subs.en.vtt").read_text(encoding="utf-8")):
        lines = block.strip().splitlines()
        cue = next((i for i, x in enumerate(lines) if "-->" in x), None)
        if cue is None:
            continue
        a, b = (sec(x.split()[0]) for x in lines[cue].split("-->"))
        text = re.sub(r"\[[^\]]*\]|<[^>]*>", " ", " ".join(lines[cue + 1:])).replace("’", "'")
        toks = text.split()
        words += [{"t": a + (b - a) * (i + 0.5) / len(toks), "w": w} for i, w in enumerate(toks)]
    return words


# ---------- eval ----------
def wilson(k, n, z=1.96):
    if not n:
        return [0.0, 0.0]
    p = k / n
    c, h = (p + z * z / (2 * n)) / (1 + z * z / n), z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [float(c - h), float(c + h)]


def rate(k, n):
    return {"k": int(k), "n": int(n), "rate": k / n if n else 0.0, "ci95": wilson(k, n)}


def window_probs(clf, raw, fps, size=1.0):
    from wlasl.segmenter import hands_visible

    win, hop = round(fps * size), max(1, round(fps * 0.25))
    t, p = [], []
    for a in range(0, len(raw) - win, hop):
        w = raw[a:a + win]
        if sum(hands_visible(x) for x in w) < win * 0.5:
            continue
        x = clf.predict_probs(w)
        t.append((a + win / 2) / fps)
        p.append(x)
    return np.array(t, np.float32), np.stack(p).astype(np.float32) if p else np.zeros((0, len(clf.labels)), np.float32)


class Probs:
    """Classifier 加上完整機率輸出（只評估用，不動後端介面）。"""

    def __init__(self, clf):
        self.clf, self.labels = clf, clf.labels

    def predict_probs(self, raw):
        from app.inference import softmax
        from wlasl.dataset import prepare

        p = softmax(self.clf.session.run(None, {"keypoints": prepare(raw, mode=self.clf.mode)[None]})[0][0])
        return p[:len(self.labels)]


def eval_word_video(vid, models, decoded):
    d = np.load(DATA / vid / "kp.npz")
    raw, fps = d["raw"], float(d["fps"])
    res = {"fps": fps, "minutes": len(raw) / fps / 60}
    for name, m in models.items():
        vocab = set(m.labels)
        rows, total = chapters(vid, vocab)
        t, P = window_probs(m, raw, fps)
        idx = {g: i for i, g in enumerate(m.labels)}
        top1 = whole1 = whole5 = whole_n = peak = base_hits = base_n = 0
        rng = np.random.default_rng(0)
        for i, (a, b, gold) in enumerate(rows):
            g = [idx[x] for x in gold]
            mask = (t >= a) & (t < b)
            if mask.any():
                top = P[mask].argmax(1)
                top1 += bool(np.isin(top, g).any())
                peak += int(top[P[mask].max(1).argmax()] in g)
            if b - a <= SHORT_CHAPTER:
                seg = raw[int(a * fps):int(b * fps)]
                if len(seg) >= 4:
                    order = np.argsort(-m.predict_probs(seg))[:5]
                    whole_n += 1
                    whole1 += order[0] in g
                    whole5 += bool(np.isin(order, g).any())
            # 機率基準：同樣的答案換到同一支影片的其他章節，任一窗口命中的比例
            others = [r for j, r in enumerate(rows) if j != i]
            for oa, ob, _ in [others[k] for k in rng.integers(len(others), size=min(5, len(others)))] if others else []:
                mo = (t >= oa) & (t < ob)
                if mo.any():
                    base_n += 1
                    base_hits += bool(np.isin(P[mo].argmax(1), g).any())
        n = len(rows)
        res[name] = {"chapters": total, "in_vocab": n, "any_window": rate(top1, n), "any_window_base": rate(base_hits, base_n),
                     "peak_window": rate(peak, n), "whole_top1": rate(whole1, whole_n), "whole_top5": rate(whole5, whole_n)}
    # 上線解碼器（100 詞）：使用者在這一章實際看到什麼
    rows, _ = chapters(vid, set(models["w100"].labels))
    first = anyhit = silent = 0
    for a, b, gold in rows:
        inside = [g for t0, g in decoded if a <= t0 < b]
        silent += not inside
        first += bool(inside) and inside[0] in gold
        anyhit += any(g in gold for g in inside)
    res["online"] = {"chapters": len(rows), "first_correct": rate(first, len(rows)), "any_correct": rate(anyhit, len(rows)),
                     "no_output": rate(silent, len(rows)), "outputs_per_min": len(decoded) / res["minutes"]}
    return res


def eval_talk_video(vid, models, decoded):
    import contextbench as cb
    import longvideo as lv

    d = np.load(DATA / vid / "kp.npz")
    raw, fps = d["raw"], float(d["fps"])
    dur = len(raw) / fps
    flat = lv.flat_tokens(load_caption_words(vid))
    cb.BEFORE, cb.AFTER = 3.0, 3.0
    res = {"fps": fps, "minutes": dur / 60, "words": len(flat), "hands": cb.motion(raw, fps)["any_hand"]}
    occ100 = lv.match_vocab(flat, set(models["w100"].labels))
    p, pb = lv.with_baseline(lv.precision, decoded, occ100, dur, 3, 3)
    r, rb = lv.with_baseline(lv.recall, decoded, occ100, dur, 3, 3)
    hits = round(p * len(decoded))
    res["online"] = {"outputs": len(decoded), "hits": hits, "occurrences": len(occ100), "precision": p, "precision_base": pb,
                     "recall": r, "recall_base": rb}
    for name, m in models.items():
        occ = lv.match_vocab(flat, set(m.labels))
        t, P = window_probs(m, raw, fps)
        res[name] = {"occurrences": len(occ), "evidence": cb.evidence_auc(t, np.log(P + cb.EPS), [str(x) for x in m.labels], occ, 0.0, dur)}
    return res


def decode_online(raw, fps, clf, spot):
    import spotbench as sb
    from app import config

    sb.SPOT["classify"] = sb.Cached(spot)
    p = {"window": config.SPOT_WINDOW, "hop": config.SPOT_HOP, "hits": config.SPOT_MIN_HITS, "th": config.SPOT_THRESHOLD_SINGLE,
         "after": config.CONTINUOUS_AFTER, "spot": True}
    return [(float((s.start + s.end) / 2), s.prediction.gloss) for s in sb.decode(sb.Cached(clf), raw, fps, p)]


def same_word_baseline(models, words):
    """同一批詞在 WLASL test 的正確率：同詞比同詞，才分得出是換領域還是這批詞本來就難。"""
    from wlasl.dataset import labeled_span

    testdata = ROOT / "data" / "kaggle_out" / "export" / "testdata"
    idx = json.loads((testdata / "index.json").read_text())
    labels = json.loads((testdata / "labels.json").read_text(encoding="utf-8"))
    out = {}
    for name, m in models.items():
        ix = {g: i for i, g in enumerate(m.labels)}
        h1 = h5 = n = 0
        for r in idx:
            g = labels[r["label"]]
            if g not in words[name] or g not in ix:
                continue
            s = np.load(testdata / "keypoints" / f"{r['video_id']}.npy")
            a, b = labeled_span(r, len(s))
            if b - a < 4:
                continue
            order = np.argsort(-m.predict_probs(s[a:b]))[:5]
            n += 1
            h1 += order[0] == ix[g]
            h5 += ix[g] in order
        out[name] = {"top1": rate(h1, n), "top5": rate(h5, n)}
    return out


def cmd_eval(_):
    from app import winperf
    from app.inference import Classifier

    winperf.disable_power_throttling()
    clf100 = Classifier(MODEL)
    models = {"w100": Probs(clf100), "w2000": Probs(Classifier(MODEL_2000))}
    spot = Classifier(SPOT_MODEL)
    res = {"word": {}, "talk": {}}
    words = {k: set() for k in models}
    outputs = {}
    for vid, name in {**WORD_VIDEOS, **TALK_VIDEOS}.items():
        d = np.load(DATA / vid / "kp.npz")
        decoded = decode_online(d["raw"], float(d["fps"]), clf100, spot)
        outputs[vid] = decoded
        if vid in WORD_VIDEOS:
            res["word"][vid] = {"name": name, **eval_word_video(vid, models, decoded)}
            for k, m in models.items():
                for _, _, gold in chapters(vid, set(m.labels))[0]:
                    words[k] |= gold
        else:
            res["talk"][vid] = {"name": name, **eval_talk_video(vid, models, decoded)}
        print(json.dumps({vid: res["word" if vid in WORD_VIDEOS else "talk"][vid]}, ensure_ascii=False), flush=True)
    res["same_words_wlasl_test"] = same_word_baseline(models, words)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (DATA / "online_outputs.json").write_text(json.dumps(outputs, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res["same_words_wlasl_test"], ensure_ascii=False))


def cmd_summary(_):
    """合併各影片：單字與對話的合計、Learn How to Sign 和其他手語者分開看、詞彙表外的章節會不會亂輸出。"""
    res = json.loads((OUT / "metrics.json").read_text(encoding="utf-8"))
    outputs = json.loads((DATA / "online_outputs.json").read_text(encoding="utf-8"))
    vocab = {str(x) for x in json.loads((MODEL / "labels.json").read_text(encoding="utf-8"))}

    def total(vids, *path):
        k = n = 0
        for v in vids:
            x = res["word"][v]
            for p in path:
                x = x[p]
            k, n = k + x["k"], n + x["n"]
        return rate(k, n)

    fast, meredith = list(WORD_VIDEOS)[:2], list(WORD_VIDEOS)[:4]
    others = list(WORD_VIDEOS)[4:]
    s = {"online_first_correct": {"all": total(WORD_VIDEOS, "online", "first_correct"), "meredith": total(meredith, "online", "first_correct"),
                                  "others": total(others, "online", "first_correct")},
         "online_no_output": total(WORD_VIDEOS, "online", "no_output"),
         "whole_short": {m: {"top1": total(fast, m, "whole_top1"), "top5": total(fast, m, "whole_top5")} for m in ("w100", "w2000")},
         "w2000_any_window": {"meredith": total(meredith, "w2000", "any_window"), "others": total(others, "w2000", "any_window")},
         "w2000_any_window_base": {"meredith": total(meredith, "w2000", "any_window_base"), "others": total(others, "w2000", "any_window_base")}}
    oov = oov_out = wrong_in = in_out = 0
    errors = []
    for vid in fast:
        info = json.loads((DATA / vid / "info.json").read_text(encoding="utf-8"))
        rows = chapters(vid, vocab)[0]
        for c in info["chapters"]:
            if SKIP.match(c["title"].strip()):
                continue
            a, b = float(c["start_time"]), float(c["end_time"])
            inside = [g for t0, g in outputs[vid] if a <= t0 < b]
            gold = next((r[2] for r in rows if r[0] == a), None)
            if gold is None:
                oov += 1
                oov_out += bool(inside)
            elif inside:
                in_out += 1
                if inside[0] not in gold:
                    wrong_in += 1
                    errors.append((sorted(gold)[0], inside[0]))
    s["fast_oov"] = {"chapters": rate(oov_out, oov), "wrong_when_in_vocab": rate(wrong_in, in_out), "errors": errors}
    talk = res["talk"].values()
    hits = sum(t["online"]["hits"] for t in talk)
    outs = sum(t["online"]["outputs"] for t in talk)
    s["talk_precision"] = {**rate(hits, outs), "base": sum(t["online"]["precision_base"] * t["online"]["outputs"] for t in talk) / outs}
    occ = sum(t["online"]["occurrences"] for t in talk)
    s["talk_recall"] = {"rate": sum(t["online"]["recall"] * t["online"]["occurrences"] for t in talk) / occ, "occurrences": occ,
                        "base": sum(t["online"]["recall_base"] * t["online"]["occurrences"] for t in talk) / occ}
    res["summary"] = s
    (OUT / "metrics.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(s, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch").set_defaults(fn=cmd_fetch)
    sub.add_parser("eval").set_defaults(fn=cmd_eval)
    sub.add_parser("summary").set_defaults(fn=cmd_summary)
    args = ap.parse_args()
    args.fn(args)
