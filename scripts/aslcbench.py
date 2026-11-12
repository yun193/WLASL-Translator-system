"""ASL Citizen test 評估：11 位沒進訓練的手語者、在家用網路攝影機自己錄，最接近「新使用者」的單字測試。

  uv run --project backend python scripts/aslcbench.py fetch   從官方 zip 用 HTTP Range 只抽需要的影片，再擷取關鍵點
  uv run --project backend python scripts/aslcbench.py eval    用上線設定評估，不針對這批影片調參

範圍：ASL Citizen test 中和 WLASL100 完全同名的詞（變體詞如 DRINK1／DRINK2 不算，論文的重疊表也是這樣定）。
授權：Microsoft Research License，只限非商業研究、不得散布；影片與關鍵點留在 data/aslcitizen/（不進 git）。
"""

from __future__ import annotations

import csv
import io
import json
import sys
import time
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

URL = "https://download.microsoft.com/download/b/8/8/b88c0bae-e6c1-43e1-8726-98cf5af36ca4/ASL_Citizen.zip"
DATA = ROOT / "data" / "aslcitizen"
OUT = ROOT / "docs" / "asl-citizen"
MODEL = ROOT / "models" / "20261018-w2000n"
SPOT_MODEL = ROOT / "models" / "20261019-w2000bg"


class HttpFile(io.RawIOBase):
    """唯讀、可 seek 的遠端檔案（每次 read 發一個 Range 請求），給 zipfile 用。"""

    def __init__(self, url):
        self.url, self.pos = url, 0
        self.size = int(urllib.request.urlopen(urllib.request.Request(url, method="HEAD")).headers["Content-Length"])

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = {0: off, 1: self.pos + off, 2: self.size + off}[whence]
        return self.pos

    def readinto(self, b):
        if self.pos >= self.size or len(b) == 0:
            return 0
        end = min(self.pos + len(b), self.size) - 1
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{end}"})
        for attempt in range(6):  # 微軟下載站偶爾讀取逾時
            try:
                data = urllib.request.urlopen(req, timeout=60).read()
                break
            except (TimeoutError, OSError):
                if attempt == 5:
                    raise
                time.sleep(2 ** attempt)
        b[: len(data)] = data
        self.pos += len(data)
        return len(data)


def selected(labels: list[str]) -> list[dict]:
    vocab = set(labels)
    rows = list(csv.DictReader(open(DATA / "splits" / "test.csv", encoding="utf-8")))
    return [r for r in rows if r["Gloss"].lower() in vocab]


def cmd_fetch():
    import longvideo as lv

    labels = json.loads((MODEL / "labels.json").read_text(encoding="utf-8"))
    z = zipfile.ZipFile(io.BufferedReader(HttpFile(URL), 1 << 20))
    (DATA / "splits").mkdir(parents=True, exist_ok=True)
    for sp in ("train", "val", "test"):
        p = DATA / "splits" / f"{sp}.csv"
        if not p.exists():
            p.write_bytes(z.read(f"ASL_Citizen/splits/{sp}.csv"))
    if not (DATA / "use.txt").exists():
        (DATA / "use.txt").write_bytes(z.read("ASL_Citizen/use.txt"))
    rows = selected(labels)
    print(f"{len(rows)} 支、{len({r['Gloss'] for r in rows})} 詞、{len({r['Participant ID'] for r in rows})} 位手語者", flush=True)
    vids, kps = DATA / "videos", DATA / "kp"
    vids.mkdir(exist_ok=True)
    for i, r in enumerate(rows):
        name = r["Video file"]
        kp = kps / f"{Path(name).stem}.npz"
        if kp.exists():
            continue
        v = vids / name
        if not v.exists():
            v.write_bytes(z.read(f"ASL_Citizen/videos/{name}"))
        lv.extract(v, kp)
        if i % 50 == 0:
            print(f"[{i + 1}/{len(rows)}]", flush=True)


def wilson(k, n, z=1.96):
    if n == 0:
        return [0.0, 0.0]
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [float(c - h), float(c + h)]


def rate(k, n):
    return {"k": int(k), "n": int(n), "rate": k / n if n else None, "ci95": wilson(k, n)}


def online_cfg():
    from app import config

    return {"window": config.SPOT_WINDOW, "hop": config.SPOT_HOP, "hits": config.SPOT_MIN_HITS,
            "th": config.SPOT_THRESHOLD, "after": config.CONTINUOUS_AFTER, "spot": config.SPOTTING}


def wlasl_same_words(clfs, words):
    """同一批詞在 WLASL test（手語者幾乎都看過）的整段正確率，當對照。"""
    from wlasl.dataset import labeled_span

    td = MODEL / "testdata"
    idx = json.loads((td / "index.json").read_text())
    labels = json.loads((td / "labels.json").read_text(encoding="utf-8"))
    out = {}
    for name, clf in clfs.items():
        h1 = h5 = n = conf = conf_ok = 0
        for r in idx:
            g = labels[r["label"]]
            if g not in words:
                continue
            s = np.load(td / "keypoints" / f"{r['video_id']}.npy")
            p = clf.predict(s[slice(*labeled_span(r, len(s)))])
            top5 = [x for x, _ in p.top5]
            n += 1
            h1 += top5[0] == g
            h5 += g in top5
            conf += p.prob >= 0.5
            conf_ok += p.prob >= 0.5 and top5[0] == g
        out[name] = {"top1": rate(h1, n), "top5": rate(h5, n), "coverage": rate(conf, n), "confident_top1": rate(conf_ok, conf)}
    return out


def cmd_eval():
    import spotbench as sb
    from app import config, winperf
    from app.inference import Classifier, Ensemble

    winperf.disable_power_throttling()
    single, bg = Classifier(MODEL), Classifier(SPOT_MODEL)
    clfs = {"w2000n": single, "雙模型平均（上線）": Ensemble(single, bg)}
    rows = selected(single.labels)
    sb.SPOT["classify"] = sb.Cached(Ensemble(single, bg, use_background=True))
    online_classify = sb.Cached(clfs["雙模型平均（上線）"])
    cfg = online_cfg()
    th = config.MIN_CONFIDENCE
    per_video = []
    for r in rows:
        d = np.load(DATA / "kp" / f"{Path(r['Video file']).stem}.npz")
        raw, fps = d["raw"], float(d["fps"])
        gold = r["Gloss"].lower()
        rec = {"video": r["Video file"], "signer": r["Participant ID"], "gold": gold, "frames": len(raw), "fps": fps,
               "hands": float(np.mean([np.isfinite(f[-42:, 0]).any() for f in raw]))}
        for name, clf in clfs.items():
            p = clf.predict(raw)  # 整支影片（ASL Citizen 一支一個詞，前後有少量靜止）
            rec[name] = {"top5": [x for x, _ in p.top5], "prob": p.prob}
        signs = sb.decode(online_classify, raw, fps, cfg)
        rec["online"] = [s.prediction.gloss for s in signs]
        per_video.append(rec)

    res = {"videos": len(rows), "glosses": len({r["gold"] for r in per_video}), "signers": len({r["signer"] for r in per_video}),
           "threshold": th, "whole": {}, "online": {}, "per_signer": {}, "confusions": {}}
    for name in clfs:
        top1 = [r[name]["top5"][0] == r["gold"] for r in per_video]
        conf = [r[name]["prob"] >= th for r in per_video]
        res["whole"][name] = {"top1": rate(sum(top1), len(top1)),
                              "top5": rate(sum(r["gold"] in r[name]["top5"] for r in per_video), len(per_video)),
                              "coverage": rate(sum(conf), len(conf)),
                              "confident_top1": rate(sum(a and b for a, b in zip(top1, conf)), sum(conf))}
        res["confusions"][name] = Counter(f"{r['gold']}→{r[name]['top5'][0]}" for r in per_video
                                          if r[name]["top5"][0] != r["gold"]).most_common(15)
    first = [bool(r["online"]) and r["online"][0] == r["gold"] for r in per_video]
    res["online"] = {"first_correct": rate(sum(first), len(first)),
                     "no_output": rate(sum(not r["online"] for r in per_video), len(per_video)),
                     "shown_correct": rate(sum(first), sum(bool(r["online"]) for r in per_video)),
                     "multi_output": rate(sum(len(r["online"]) > 1 for r in per_video), len(per_video))}
    by = defaultdict(list)
    for r in per_video:
        by[r["signer"]].append(r)
    main = "雙模型平均（上線）"
    for s, rs in sorted(by.items()):
        res["per_signer"][s] = {"whole_top1": rate(sum(r[main]["top5"][0] == r["gold"] for r in rs), len(rs)),
                                "online_first": rate(sum(bool(r["online"]) and r["online"][0] == r["gold"] for r in rs), len(rs)),
                                "hands": float(np.mean([r["hands"] for r in rs]))}
    res["wlasl_same_words"] = wlasl_same_words(clfs, {r["gold"] for r in per_video})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metrics.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (DATA / "per_video.json").write_text(json.dumps(per_video, ensure_ascii=False), encoding="utf-8")
    f = lambda a: f"{a['k']}/{a['n']}={a['rate']:.1%} [{a['ci95'][0]:.0%},{a['ci95'][1]:.0%}]"  # noqa: E731
    for name in clfs:
        w, b = res["whole"][name], res["wlasl_same_words"][name]
        print(f"{name}: ASLC top1 {f(w['top1'])} top5 {f(w['top5'])} 涵蓋 {f(w['coverage'])} 高信心 {f(w['confident_top1'])}")
        print(f"   WLASL 同詞 top1 {f(b['top1'])} top5 {f(b['top5'])} 涵蓋 {f(b['coverage'])} 高信心 {f(b['confident_top1'])}")
    print("上線解碼", {k: f(v) for k, v in res["online"].items()})
    print("每位手語者", {s: (f(v["whole_top1"]), round(v["hands"], 2)) for s, v in res["per_signer"].items()})
    print("常見混淆", res["confusions"][main][:10])


if __name__ == "__main__":
    {"fetch": cmd_fetch, "eval": cmd_eval}[sys.argv[1]]()
