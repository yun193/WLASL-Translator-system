"""長影片泛化測試：整支影片 → 關鍵點 → 用和後端相同的切詞器與分類器重播 → 和逐字稿比對。

  uv run --project backend python scripts/longvideo.py extract  <影片> data/podcast/ep3_kp.npz
  uv run --project backend python scripts/longvideo.py transcript data/podcast/ep3.en-orig.json3 docs/podcast-ep3/transcript.md
  uv run --project backend python scripts/longvideo.py predict  data/podcast/ep3_kp.npz models/<run> docs/podcast-ep3/model_<名稱>.md
  uv run --project backend python scripts/longvideo.py compare  docs/podcast-ep3 <名稱1> <名稱2> ...

extract 和後端 /api/analyze 一樣：原生 fps 逐幀解碼、高度縮到 MAX_VIDEO_HEIGHT、VIDEO 模式時間戳 i*1000/fps。
關鍵點只擷取一次，之後換模型、換切詞參數都只重播，不必再跑 MediaPipe。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))


def fmt(t: float) -> str:
    return f"{int(t // 60):02d}:{t % 60:05.2f}"


# ---------- extract ----------
def extract(video: Path, out: Path) -> None:
    import cv2

    from app import config, winperf
    from wlasl.landmarks import LandmarkExtractor

    winperf.disable_power_throttling()
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames, i, t0 = [], 0, time.time()
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
            if i % 3000 == 0:
                el = time.time() - t0
                print(f"{i}/{n} 幀  {el:.0f}s  剩約 {el / i * (n - i) / 60:.0f} 分", flush=True)
    cap.release()
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, raw=np.stack(frames).astype(np.float32), fps=fps)
    print(f"完成：{i} 幀、{fps:.3f} fps → {out}")


# ---------- transcript ----------
def load_words(json3: Path) -> list[dict]:
    """YouTube 自動字幕（json3）→ 逐字 [{t, w}]，t 是秒。"""
    ev = json.loads(json3.read_text(encoding="utf-8"))["events"]
    words = []
    for e in ev:
        for s in e.get("segs") or []:
            w = s.get("utf8", "").strip()
            if w and w != "\n":
                words.append({"t": (e["tStartMs"] + s.get("tOffsetMs", 0)) / 1000, "w": w})
    return words


def sentences(words: list[dict], gap=1.2, max_words=25) -> list[dict]:
    """自動字幕沒有標點：停頓超過 gap 秒或滿 max_words 字就斷一行。"""
    out, cur = [], []
    for i, w in enumerate(words):
        if cur and (w["t"] - cur[-1]["t"] > gap or len(cur) >= max_words):
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return [{"start": c[0]["t"], "end": c[-1]["t"], "text": " ".join(x["w"] for x in c)} for c in out]


def transcript(json3: Path, out: Path) -> None:
    words = load_words(json3)
    lines = sentences(words)
    out.parent.mkdir(parents=True, exist_ok=True)
    md = ["# 逐字稿：'Dereliction of duty' – ASL Video Podcast | Breakdown Ep. 3（FRONTLINE PBS）", "",
          "- 來源：YouTube n2wtX8c5gnU 的自動字幕（en-orig，英文配音的語音辨識），逐字有時間戳",
          "- 注意：這是英文口譯配音，不是 ASL gloss；配音通常比手語慢 1～3 秒，語序也和 ASL 不同",
          f"- 共 {len(words)} 字、{len(lines)} 行（停頓 > 1.2 秒或滿 25 字斷行）", "",
          "| 開始 | 結束 | 內容 |", "| --- | --- | --- |"]
    md += [f"| {fmt(s['start'])} | {fmt(s['end'])} | {s['text']} |" for s in lines]
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    (out.with_suffix(".json")).write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    print(f"{len(words)} 字、{len(lines)} 行 → {out}")


# ---------- predict ----------
WINDOWS = (0.6, 1.0, 1.5)
def predict(kp: Path, model_dir: Path, out: Path, name: str) -> None:
    from app import config
    from app.inference import Classifier
    from wlasl.segmenter import Segmenter

    d = np.load(kp)
    raw, fps = d["raw"], float(d["fps"])
    clf = Classifier(model_dir)
    seg = Segmenter(rest=config.REST_SECONDS, pre_roll=config.PRE_ROLL_SECONDS,
                    min_len=config.MIN_SIGN_SECONDS, max_len=config.MAX_SIGN_SECONDS)
    signs = []

    def emit(segment):
        p = clf.predict(segment)
        a, b = seg.last_span
        signs.append({"start": round(a, 3), "end": round(b, 3), "gloss": p.gloss, "prob": round(p.prob, 4),
                      "top5": [[g, round(pr, 4)] for g, pr in p.top5]})

    for i, f in enumerate(raw):
        s = seg.push(i / fps, f)
        if s is not None:
            emit(s)
    s = seg.flush()
    if s is not None:
        emit(s)

    # 滑動窗口（不靠切詞器）：每 0.25 秒取固定長度窗口直接分類，用來和切詞器版本比，分開「切詞」和「辨識」兩個問題；
    # 試三種窗口長度：會話手語一個詞常只有 0.3～0.6 秒，訓練資料的單字影片則是 1～2 秒
    from wlasl.segmenter import hands_visible
    hop = round(fps * 0.25)
    windows = {}
    for size in WINDOWS:
        win, out_w = round(fps * size), []
        for a in range(0, len(raw) - win, hop):
            w = raw[a:a + win]
            if sum(hands_visible(x) for x in w) < win * 0.5:
                continue
            p = clf.predict(w)
            out_w.append({"t": round((a + win / 2) / fps, 3), "top": [g for g, _ in p.top5],
                          "p": [round(pr, 4) for _, pr in p.top5]})
        windows[str(size)] = out_w

    hand = np.array([hands_visible(x) for x in raw])
    res = {"model": model_dir.name, "classes": len(clf.labels), "fps": fps, "frames": len(raw),
           "hands_visible_ratio": float(hand.mean()), "min_confidence": config.MIN_CONFIDENCE,
           "signs": signs, "windows": windows}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")

    th = config.MIN_CONFIDENCE
    lens = np.array([s["end"] - s["start"] for s in signs]) if signs else np.zeros(1)
    md = [f"# 模型輸出：{name}（{model_dir.name}，{len(clf.labels)} 詞）", "",
          "- 流程和後端影片檔模式相同：原生 fps 逐幀關鍵點 → 切詞器（手放下 0.5 秒切詞、單詞上限 4 秒）→ 分類",
          f"- 影片 {len(raw)} 幀（{fps:.2f} fps、{fmt(len(raw) / fps)}），有手的幀 {hand.mean():.0%}",
          f"- 切出 {len(signs)} 個詞；長度中位 {np.median(lens):.2f} 秒，碰到 4 秒上限的 {np.mean(lens >= config.MAX_SIGN_SECONDS - 0.05):.0%}",
          f"- 信心 ≥ {th} 的 {sum(s['prob'] >= th for s in signs)} 個；低於門檻顯示成 ?(前 3 名)", "",
          "## 切詞器輸出（和網頁上看到的一樣）", "",
          "| 開始 | 結束 | 長度 | 輸出 | 信心 | 前 3 名 |", "| --- | --- | --- | --- | --- | --- |"]
    for s in signs:
        shown = s["gloss"] if s["prob"] >= th else "?"
        top3 = " / ".join(f"{g} {p:.0%}" for g, p in s["top5"][:3])
        md.append(f"| {fmt(s['start'])} | {fmt(s['end'])} | {s['end'] - s['start']:.1f}s | {shown} | {s['prob']:.0%} | {top3} |")
    # 滑動窗口 1 秒、信心 ≥ 門檻的輸出，相鄰同詞合併：不靠切詞器時模型「看到」的詞串
    merged = []
    for w in windows["1.0"]:
        if w["p"][0] < th:
            continue
        if merged and merged[-1]["gloss"] == w["top"][0] and w["t"] - merged[-1]["end"] <= 0.5:
            merged[-1]["end"] = w["t"]
            merged[-1]["prob"] = max(merged[-1]["prob"], w["p"][0])
        else:
            merged.append({"start": w["t"], "end": w["t"], "gloss": w["top"][0], "prob": w["p"][0]})
    md += ["", f"## 不經切詞器：1 秒滑動窗口、信心 ≥ {th}（相鄰同詞合併，共 {len(merged)} 個）", "",
           "| 時間 | 輸出 | 最高信心 |", "| --- | --- | --- |"]
    md += [f"| {fmt(m['start'])}–{fmt(m['end'])} | {m['gloss']} | {m['prob']:.0%} |" for m in merged]
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{len(signs)} 個詞、{len(merged)} 個窗口輸出 → {out}")


# ---------- compare ----------
IRREGULAR = {"said": "say", "says": "say", "went": "go", "goes": "go", "gone": "go", "saw": "see", "seen": "see",
             "told": "tell", "knew": "know", "known": "know", "thought": "think", "came": "come", "got": "get",
             "gave": "give", "given": "give", "took": "take", "taken": "take", "made": "make", "felt": "feel",
             "left": "leave", "found": "find", "kept": "keep", "was": "be", "were": "be", "is": "be", "are": "be",
             "am": "be", "been": "be", "children": "child", "men": "man", "women": "woman", "did": "do",
             "does": "do", "done": "do", "had": "have", "has": "have", "heard": "hear", "lost": "lose",
             "paid": "pay", "met": "meet", "ate": "eat", "bought": "buy", "brought": "bring", "began": "begin",
             "died": "die", "shot": "shoot", "wrote": "write", "spoke": "speak", "won": "win", "ran": "run",
             "sat": "sit", "stood": "stand", "understood": "understand", "fell": "fall", "held": "hold",
             "i": "me", "my": "my", "i'm": "me", "us": "we", "him": "he", "his": "his", "them": "they"}
# 這些字在 ASL 通常沒有對應的手勢（冠詞、be 動詞、介系詞等），算覆蓋率時排除
FUNCTION = set("a an the of to in on at by for with from and or but if as so than that this these those "
               "be do have will would could should can may might must shall it its it's there here "
               "uh um oh okay yeah just very really also then".split())


def norm_tokens(text: str) -> list[str]:
    return [re.sub(r"[^a-z']", "", w.lower()).strip("'") for w in text.split()]


def variants(w: str) -> list[str]:
    out = [w, IRREGULAR.get(w, w)]
    for suf, rep in (("ies", "y"), ("es", ""), ("s", ""), ("ing", ""), ("ing", "e"), ("ed", ""), ("ed", "e"),
                     ("ly", ""), ("er", ""), ("est", "")):
        if w.endswith(suf) and len(w) - len(suf) >= 2:
            stem = w[: len(w) - len(suf)] + rep
            out.append(stem)
            if len(stem) > 2 and stem[-1] == stem[-2] and rep == "":
                out.append(stem[:-1])  # running → run、stopped → stop
    return out


def flat_tokens(words: list[dict]) -> list[dict]:
    """字幕片段攤平成逐字 [{t, tok, proper}]。proper：句中大寫開頭（人名、地名、機構），ASL 多半用指拼，不算在詞彙比對裡。"""
    out, prev = [], "."
    for w in words:
        for raw in w["w"].split():
            tok = norm_tokens(raw)[0] if norm_tokens(raw) else ""
            if tok:
                proper = raw[0].isupper() and tok != "i" and not tok.startswith("i'") and prev[-1:] not in ".?!"
                out.append({"t": w["t"], "tok": tok, "proper": proper})
            prev = raw
    return out


def is_function(tok: str) -> bool:
    return tok in FUNCTION or IRREGULAR.get(tok) in FUNCTION


def match_vocab(flat: list[dict], vocab: set[str]) -> list[dict]:
    """逐字 → 詞彙表內的實詞出現 [{t, gloss}]；先比 3、2 個字的片語（ice cream、give up），再比單字。
    虛詞（a、the、to、is…）和專有名詞（Card、Keller…）不算：前者 ASL 通常不打，後者用指拼，都不是這個模型該認的。"""
    hits, i = [], 0
    while i < len(flat):
        for n in (3, 2, 1):
            seg = flat[i:i + n]
            if len(seg) < n or any(x["proper"] for x in seg):
                continue
            if n > 1:
                cand = [" ".join(x["tok"] for x in seg)]
            elif is_function(seg[0]["tok"]):
                continue
            else:
                cand = variants(seg[0]["tok"])
            g = next((c for c in cand if c in vocab), None)
            if g:
                hits.append({"t": seg[0]["t"], "gloss": g})
                i += n
                break
        else:
            i += 1
    return hits


def _index(pairs):
    by = {}
    for t, g in pairs:
        by.setdefault(g, []).append(t)
    return {g: np.array(v) for g, v in by.items()}


def recall(events, occ, before, after):
    """逐字稿出現中，[t − before, t + after] 內模型有輸出同一個詞的比例。events：[(t, gloss)]。"""
    by = _index(events)
    ok = [g in by and bool(np.any((by[g] >= o["t"] - before) & (by[g] <= o["t"] + after)))
          for o in occ for g in [o["gloss"]]]
    return float(np.mean(ok)) if ok else 0.0


def precision(events, occ, before, after):
    """模型輸出中，[t − after, t + before] 內逐字稿真的出現同一個詞的比例。"""
    by = _index([(o["t"], o["gloss"]) for o in occ])
    ok = [g in by and bool(np.any((by[g] >= t - after) & (by[g] <= t + before))) for t, g in events]
    return float(np.mean(ok)) if ok else 0.0


def with_baseline(fn, events, occ, duration, before, after, k=20):
    """實際值與機率基準：把模型輸出整條時間軸循環平移 k 次（保留詞頻、打亂時間對應）取平均。"""
    rng = np.random.default_rng(0)
    real = fn(events, occ, before, after)
    base = []
    for _ in range(k):
        d = rng.uniform(0.2 * duration, 0.8 * duration)
        base.append(fn([((t + d) % duration, g) for t, g in events], occ, before, after))
    return real, float(np.mean(base))


def compare(folder: Path, names: list[str], before=4.0, after=2.0) -> None:
    words = json.loads((folder / "transcript.json").read_text(encoding="utf-8"))
    flat = flat_tokens(words)
    content = [x for x in flat if not x["proper"] and not is_function(x["tok"])]
    proper = [x for x in flat if x["proper"]]
    md = ["# 對比資料：逐字稿 vs 手語模型（Breakdown Ep. 3）", "",
          "由 `scripts/longvideo.py compare` 產生；解讀見 report.md。", "",
          f"- 逐字稿 {len(flat)} 字：實詞 {len(content)}、虛詞（冠詞、be 動詞、介系詞等）{len(flat) - len(content) - len(proper)}、"
          f"專有名詞（指拼）{len(proper)}",
          f"- 時間對齊：逐字稿某字在 t 秒，模型在 [t − {before:.0f}, t + {after:.0f}] 秒內輸出同一個詞就算對上（英文配音比手語晚）",
          "- 機率基準（括號）：模型輸出整條時間軸循環平移 20 次的平均。高出基準才代表模型真的看懂了那一段，而不是常見詞剛好撞上", ""]
    rows = []
    for name in names:
        res = json.loads((folder / f"model_{name}.json").read_text(encoding="utf-8"))
        labels = json.loads((ROOT / "models" / res["model"] / "labels.json").read_text(encoding="utf-8"))
        vocab = set(labels)
        occ = match_vocab(flat, vocab)
        dur = res["frames"] / res["fps"]
        th = res["min_confidence"]
        lens = np.array([s["end"] - s["start"] for s in res["signs"]])
        r = {"name": name, "classes": len(labels), "occ": len(occ),
             "cov_tok": sum(any(v in vocab for v in variants(x["tok"])) for x in content) / len(content),
             "cov_uniq": (lambda u: sum(any(v in vocab for v in variants(t)) for t in u) / len(u))({x["tok"] for x in content}),
             "hands": res["hands_visible_ratio"], "n_seg": len(res["signs"]),
             "seg_med": float(np.median(lens)), "seg_cap": float(np.mean(lens >= 3.95)),
             "seg": {"recall": with_baseline(recall, [(s["start"], s["gloss"]) for s in res["signs"]], occ, dur, before, after),
                     "precision": with_baseline(precision, [(s["start"], s["gloss"]) for s in res["signs"] if s["prob"] >= th],
                                                occ, dur, before, after),
                     "n_conf": sum(s["prob"] >= th for s in res["signs"])},
             "win": {}}
        for size, ws in res["windows"].items():
            conf = [(w["t"], w["top"][0]) for w in ws if w["p"][0] >= th]
            r["win"][size] = {
                "n": len(ws), "n_conf": len(conf),
                "recall_top1": with_baseline(recall, [(w["t"], w["top"][0]) for w in ws], occ, dur, before, after),
                "recall_top5": with_baseline(recall, [(w["t"], g) for w in ws for g in w["top"]], occ, dur, before, after),
                "precision_conf": with_baseline(precision, conf, occ, dur, before, after),
            }
        # 1 秒窗口信心 ≥ 門檻、對得上的詞（看是哪些詞認得出來）
        conf1 = _index([(w["t"], w["top"][0]) for w in res["windows"]["1.0"] if w["p"][0] >= th])
        found = [o for o in occ if o["gloss"] in conf1
                 and np.any((conf1[o["gloss"]] >= o["t"] - before) & (conf1[o["gloss"]] <= o["t"] + after))]
        freq = {}
        for o in occ:
            freq[o["gloss"]] = freq.get(o["gloss"], 0) + 1
        r["top_occ"] = sorted(freq.items(), key=lambda x: -x[1])[:20]
        r["found"] = [[o["gloss"], fmt(o["t"])] for o in found]
        rows.append(r)

    def pp(x):
        return f"{x[0]:.0%}（{x[1]:.0%}）"

    md += ["## 1. 詞彙覆蓋", "", "| 模型 | 詞數 | 實詞覆蓋（出現次數） | 實詞覆蓋（不重複字） | 可比對的出現 |",
           "| --- | --- | --- | --- | --- |"]
    md += [f"| {r['name']} | {r['classes']} | {r['cov_tok']:.0%} | {r['cov_uniq']:.0%} | {r['occ']} 次 |" for r in rows]
    md += ["", "## 2. 切詞器", "", "| 模型 | 有手的幀 | 切出詞數 | 長度中位 | 碰到 4 秒上限 | 召回 | 精確（信心≥門檻） |",
           "| --- | --- | --- | --- | --- | --- | --- |"]
    md += [f"| {r['name']} | {r['hands']:.0%} | {r['n_seg']} | {r['seg_med']:.1f} 秒 | {r['seg_cap']:.0%} | "
           f"{pp(r['seg']['recall'])} | {pp(r['seg']['precision'])}，{r['seg']['n_conf']} 個 |" for r in rows]
    md += ["", "## 3. 不經切詞器：滑動窗口（每 0.25 秒）", "",
           "召回 top-1／top-5：逐字稿的出現有多少在時間窗內被模型列為第 1 名／前 5 名。精確：信心 ≥ 門檻的輸出有多少對得上逐字稿。", "",
           "| 模型 | 窗口 | 召回 top-1 | 召回 top-5 | 精確（信心≥門檻） | 信心≥門檻的窗口 |", "| --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        for size, w in r["win"].items():
            md.append(f"| {r['name']} | {size} 秒 | {pp(w['recall_top1'])} | {pp(w['recall_top5'])} | "
                      f"{pp(w['precision_conf'])} | {w['n_conf']}／{w['n']} |")
    for r in rows:
        md += ["", f"### {r['name']}：逐字稿最常出現的可比對詞", "", ", ".join(f"{g}×{n}" for g, n in r["top_occ"]),
               "", f"1 秒窗口（信心≥門檻）對上的出現（{len(r['found'])} 個）：" +
               (", ".join(f"{g}@{t}" for g, t in r["found"][:40]) or "無")]
    (folder / "comparison_data.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (folder / "comparison_data.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("extract"); a.add_argument("video", type=Path); a.add_argument("out", type=Path)
    a = sub.add_parser("transcript"); a.add_argument("json3", type=Path); a.add_argument("out", type=Path)
    a = sub.add_parser("predict"); a.add_argument("kp", type=Path); a.add_argument("model", type=Path)
    a.add_argument("out", type=Path); a.add_argument("--name", default="")
    a = sub.add_parser("compare"); a.add_argument("folder", type=Path); a.add_argument("names", nargs="+")
    args = ap.parse_args()
    if args.cmd == "extract":
        extract(args.video, args.out)
    elif args.cmd == "transcript":
        transcript(args.json3, args.out)
    elif args.cmd == "predict":
        predict(args.kp, args.model, args.out, args.name or args.model.name)
    elif args.cmd == "compare":
        compare(args.folder, args.names)
