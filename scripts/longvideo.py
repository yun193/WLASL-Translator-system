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

    # 滑動窗口（不靠切詞器）：每 0.25 秒取 1 秒窗口直接分類，用來和切詞器版本比，分開「切詞」和「辨識」兩個問題
    win, hop = round(fps * 1.0), round(fps * 0.25)
    from wlasl.segmenter import hands_visible
    windows = []
    for a in range(0, len(raw) - win, hop):
        w = raw[a:a + win]
        if sum(hands_visible(x) for x in w) < win * 0.5:
            continue
        p = clf.predict(w)
        windows.append({"t": round((a + win / 2) / fps, 3), "gloss": p.gloss, "prob": round(p.prob, 4)})

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
          "| 開始 | 結束 | 長度 | 輸出 | 信心 | 前 3 名 |", "| --- | --- | --- | --- | --- | --- |"]
    for s in signs:
        shown = s["gloss"] if s["prob"] >= th else "?"
        top3 = " / ".join(f"{g} {p:.0%}" for g, p in s["top5"][:3])
        md.append(f"| {fmt(s['start'])} | {fmt(s['end'])} | {s['end'] - s['start']:.1f}s | {shown} | {s['prob']:.0%} | {top3} |")
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{len(signs)} 個詞、{len(windows)} 個窗口 → {out}")


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
                     ("d", ""), ("ly", ""), ("er", ""), ("est", "")):
        if w.endswith(suf) and len(w) - len(suf) >= 2:
            stem = w[: len(w) - len(suf)] + rep
            out.append(stem)
            if len(stem) > 2 and stem[-1] == stem[-2] and rep == "":
                out.append(stem[:-1])  # running → run、stopped → stop
    return out


def match_vocab(words: list[dict], vocab: set[str]) -> list[dict]:
    """逐字稿 → 詞彙表內的出現 [{t, gloss, word}]；先比 3、2 個字的片語（ice cream、give up），再比單字。"""
    toks = norm_tokens(" ".join(w["w"] for w in words))
    hits, i = [], 0
    while i < len(toks):
        for n in (3, 2, 1):
            if i + n > len(toks):
                continue
            if n > 1:
                cand = [" ".join(toks[i:i + n])]
            else:
                cand = variants(toks[i])
            g = next((c for c in cand if c in vocab), None)
            if g:
                hits.append({"t": words[i]["t"], "gloss": g, "word": " ".join(toks[i:i + n])})
                i += n
                break
        else:
            i += 1
    return hits


def hit_rate(events, occ, before, after):
    """events：[(t, gloss)]；occ：逐字稿出現 [{t, gloss}]。回傳逐字稿出現中，前 before 秒～後 after 秒內有同一個詞被輸出的比例。"""
    by = {}
    for t, g in events:
        by.setdefault(g, []).append(t)
    for g in by:
        by[g] = np.array(by[g])
    ok = [bool(len(by.get(o["gloss"], [])) and np.any((by[o["gloss"]] >= o["t"] - before) & (by[o["gloss"]] <= o["t"] + after)))
          for o in occ]
    return float(np.mean(ok)) if ok else 0.0


def precision(events, occ, before, after):
    """模型輸出的詞中，在 [t - after, t + before] 內逐字稿出現同一個詞的比例（配音比手語晚）。"""
    by = {}
    for o in occ:
        by.setdefault(o["gloss"], []).append(o["t"])
    by = {g: np.array(v) for g, v in by.items()}
    ok = [bool(g in by and np.any((by[g] >= t - after) & (by[g] <= t + before))) for t, g in events]
    return float(np.mean(ok)) if ok else 0.0


def shifted(events, duration, rng, k=20):
    """時間循環平移 k 次：保留詞頻，打亂和時間的對應，當作「純靠猜」的基準。"""
    for _ in range(k):
        d = rng.uniform(0.2 * duration, 0.8 * duration)
        yield [((t + d) % duration, g) for t, g in events]


def compare(folder: Path, names: list[str], before=4.0, after=2.0) -> None:
    words = json.loads((folder / "transcript.json").read_text(encoding="utf-8"))
    toks = [t for t in norm_tokens(" ".join(w["w"] for w in words)) if t]
    content = [t for t in toks if t not in FUNCTION and not any(v in FUNCTION for v in variants(t)[:2])]
    rng = np.random.default_rng(0)
    md = ["# 對比報告：逐字稿 vs 手語模型（Breakdown Ep. 3）", "",
          f"- 逐字稿 {len(toks)} 字，其中實詞（去掉冠詞、be 動詞、介系詞等 ASL 通常不打的字）{len(content)} 字",
          f"- 時間對齊：逐字稿某字在 t 秒，模型在 [t − {before:.0f}, t + {after:.0f}] 秒內輸出同一個詞就算對上（英文配音比手語晚）",
          "- 機率基準：把模型輸出整條時間軸循環平移 20 次後的平均。高出基準才代表模型真的在看手語，而不是常見詞剛好撞上", ""]
    rows, notes = [], []
    for name in names:
        res = json.loads((folder / f"model_{name}.json").read_text(encoding="utf-8"))
        labels = json.loads((ROOT / "models" / res["model"] / "labels.json").read_text(encoding="utf-8"))
        vocab = set(labels)
        occ = match_vocab(words, vocab)
        dur = res["frames"] / res["fps"]
        th = res["min_confidence"]
        segs = [(s["start"], s["gloss"]) for s in res["signs"]]
        segs_conf = [(s["start"], s["gloss"]) for s in res["signs"] if s["prob"] >= th]
        wins = [(w["t"], w["gloss"]) for w in res["windows"]]
        wins_conf = [(w["t"], w["gloss"]) for w in res["windows"] if w["prob"] >= th]
        lens = np.array([s["end"] - s["start"] for s in res["signs"]])
        cov_tok = sum(1 for t in content if any(v in vocab for v in variants(t))) / max(len(content), 1)
        uniq = {t for t in content}
        cov_uniq = sum(1 for t in uniq if any(v in vocab for v in variants(t))) / max(len(uniq), 1)

        def both(fn, ev):
            real = fn(ev, occ, before, after)
            base = np.mean([fn(s, occ, before, after) for s in shifted(ev, dur, rng)])
            return real, base

        r = {"name": name, "classes": len(labels), "cov_tok": cov_tok, "cov_uniq": cov_uniq, "occ": len(occ),
             "n_seg": len(segs), "seg_med": float(np.median(lens)), "seg_cap": float(np.mean(lens >= 3.95)),
             "hands": res["hands_visible_ratio"],
             "seg_rec": both(hit_rate, segs), "win_rec": both(hit_rate, wins),
             "segc_prec": both(precision, segs_conf), "winc_prec": both(precision, wins_conf),
             "n_segc": len(segs_conf), "n_winc": len(wins_conf)}
        rows.append(r)
        # 對上的例子
        by = {}
        for t, g in wins_conf:
            by.setdefault(g, []).append(t)
        found = [o for o in occ if any(o["t"] - before <= t <= o["t"] + after for t in by.get(o["gloss"], []))]
        top = {}
        for o in occ:
            top[o["gloss"]] = top.get(o["gloss"], 0) + 1
        notes.append((name, found, sorted(top.items(), key=lambda x: -x[1])[:15]))

    def pp(x):
        return f"{x[0]:.0%}（基準 {x[1]:.0%}）"

    md += ["## 1. 詞彙覆蓋（模型「認得」逐字稿裡多少字）", "",
           "| 模型 | 詞數 | 實詞覆蓋（出現次數） | 實詞覆蓋（不重複字） | 逐字稿中可比對的出現 |", "| --- | --- | --- | --- | --- |"]
    md += [f"| {r['name']} | {r['classes']} | {r['cov_tok']:.0%} | {r['cov_uniq']:.0%} | {r['occ']} 次 |" for r in rows]
    md += ["", "## 2. 切詞（連續手語能不能切成一個一個詞）", "",
           "| 模型 | 有手的幀 | 切出詞數 | 長度中位 | 碰到 4 秒上限 |", "| --- | --- | --- | --- | --- |"]
    md += [f"| {r['name']} | {r['hands']:.0%} | {r['n_seg']} | {r['seg_med']:.1f} 秒 | {r['seg_cap']:.0%} |" for r in rows]
    md += ["", "## 3. 辨識（對得上逐字稿的比例，括號是機率基準）", "",
           "召回：逐字稿裡可比對的出現，有多少被模型在時間窗內輸出。精確：模型輸出（信心 ≥ 門檻）中有多少在時間窗內真的出現在逐字稿。",
           "滑動窗口不經過切詞器：每 0.25 秒取 1 秒直接分類，用來把「切詞」和「辨識」兩個問題分開。", "",
           "| 模型 | 切詞器 召回 | 切詞器 精確（信心≥門檻） | 滑動窗口 召回 | 滑動窗口 精確（信心≥門檻） |",
           "| --- | --- | --- | --- | --- |"]
    md += [f"| {r['name']} | {pp(r['seg_rec'])} | {pp(r['segc_prec'])}，{r['n_segc']} 個 | {pp(r['win_rec'])} | {pp(r['winc_prec'])}，{r['n_winc']} 個 |"
           for r in rows]
    for name, found, top in notes:
        md += ["", f"### {name}：逐字稿最常出現的可比對詞", "", ", ".join(f"{g}×{n}" for g, n in top)]
        ex = ", ".join(f"{o['gloss']}@{fmt(o['t'])}" for o in found[:30])
        md += ["", f"滑動窗口（信心≥門檻）對上的例子（{len(found)} 個）：{ex or '無'}"]
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
