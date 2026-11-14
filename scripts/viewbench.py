"""虛擬鏡頭角度測試：把 ASL Citizen test 的骨架在 3D 轉一個角度再投影回 2D，量換人整段 top-1 掉多少。

不用錄影：MediaPipe 每個點有深度 z（關鍵點檔裡已存），把整副骨架繞肩膀中點轉 yaw（左右）／pitch（上下）後只取 x、y，
就等於從另一個角度的鏡頭看同一段手語。手指的 z 是相對手腕，先接到身體姿勢的手腕深度上再轉。

另外量「轉正」（--canon 那欄）：用兩肩的深度差估出身體轉了幾度（整段取中位數），轉回正面再辨識。
不必重訓，直接看轉正能不能把掉的正確率救回來。

    uv run --project backend python scripts/viewbench.py            # 預設 h2000n＋h2000bg，抽 4000 支
    VIEW_MODEL=... VIEW_SPOT_MODEL=... VIEW_N=0 （全部 14,121 支）
"""
from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

import aslcbench as ab  # noqa: E402
from wlasl.augment import rotate_view, smooth_pose_z  # noqa: E402
from wlasl.landmarks import L_SHOULDER, R_SHOULDER  # noqa: E402

MODEL = ROOT / "models" / os.environ.get("VIEW_MODEL", "20261114-h2000n")
SPOT_MODEL = ROOT / "models" / os.environ.get("VIEW_SPOT_MODEL", "20261114-h2000bg")
N = int(os.environ.get("VIEW_N", "4000"))
OUT = ROOT / "docs" / "viewbench" / f"{MODEL.name}_smooth{os.environ.get('VIEW_SMOOTH', '9')}.json"
# (yaw, pitch) 度；yaw 正＝鏡頭往受試者右手邊移
ANGLES = [(0, 0), (15, 0), (-15, 0), (30, 0), (-30, 0), (45, 0), (-45, 0), (0, 20), (0, -20)]


SMOOTH = int(os.environ.get("VIEW_SMOOTH", "9"))  # 姿勢 z 時間中位濾波的幀數（0＝不濾）


def rotate(raw: np.ndarray, yaw: float, pitch: float) -> np.ndarray:
    return rotate_view(raw, yaw, pitch, SMOOTH)


def body_yaw(raw: np.ndarray) -> float:
    """兩肩深度差估身體相對鏡頭轉了幾度，整段取中位數（單幀約有 5° 雜訊）。"""
    s = smooth_pose_z(raw, SMOOTH)
    d = s[:, L_SHOULDER] - s[:, R_SHOULDER]
    ok = ~np.isnan(d[:, 0])
    if ok.sum() < 3:
        return 0.0
    return float(np.degrees(np.median(np.arctan2(d[ok, 2], d[ok, 0]))))


def canon(raw: np.ndarray) -> np.ndarray:
    """轉正：把估出的身體轉角轉回 0。"""
    return rotate(raw, body_yaw(raw), 0.0)


def main():
    from app import winperf
    from app.inference import Classifier, Ensemble

    winperf.disable_power_throttling()
    single, bg = Classifier(MODEL), Classifier(SPOT_MODEL)
    clf = Ensemble(single, bg)
    import vocab2000 as v
    rows = v.test_rows(set(clf.labels))
    if N:
        rows = random.Random(0).sample(rows, min(N, len(rows)))
    data = []
    for r in rows:
        d = np.load(ab.DATA / "kp" / f"{Path(r['Video file']).stem}.npz")
        data.append((d["raw"], r["Gloss"].lower()))
    res = {}
    for yaw, pitch in ANGLES:
        for mode in ("plain", "canon"):
            top1 = top5 = 0
            for raw, gold in data:
                x = rotate(raw, yaw, pitch) if (yaw or pitch) else raw
                p = clf.predict(canon(x) if mode == "canon" else x)
                top1 += p.gloss == gold
                top5 += gold in [g for g, _ in p.top5]
            key = f"yaw{yaw:+d}_pitch{pitch:+d}_{mode}"
            res[key] = {"top1": top1 / len(data), "top5": top5 / len(data)}
            print(f"yaw {yaw:+3d}° pitch {pitch:+3d}°  {mode:5s}  top-1 {top1 / len(data):.1%}  top-5 {top5 / len(data):.1%}",
                  flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"model": MODEL.name, "spot_model": SPOT_MODEL.name, "n": len(data), "results": res},
                              ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
