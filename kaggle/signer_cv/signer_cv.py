# Kaggle 2×T4 kernel：依手語者 k 折交叉驗證（換人泛化）
# 每折留出一組手語者，其餘手語者照原 train/val 訓練（設定同上線的 w2000n），
# 在「沒看過的人」（test）與「看過的人的原 test」（test_seen）上評估同一個模型。
# 產出：/kaggle/working/cv_results.json（每支影片的 top-5）、/kaggle/working/fold<k>/{train.log, metrics.json, history.json}
import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch

K = 4
EVAL_CLASSES = 100
ARGS = ["--classes", "2000", "--epochs", "100", "--warmup", "5", "--noise"]  # 同 w2000n

whl = glob.glob("/kaggle/input/**/wlasl-*.whl", recursive=True)
assert whl, "找不到 wlasl wheel，先跑 scripts/kaggle_push_code.ps1"
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--force-reinstall", "--no-deps", whl[0]])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "onnx", "onnxruntime"])

from wlasl.dataset import labeled_span, load_raw, prepare  # noqa: E402
from wlasl.evaluate import make_session, run  # noqa: E402
from wlasl.signers import assign_folds, load_signers, resplit  # noqa: E402

# 合併分片（同 kaggle/train）
data = Path("/tmp/data")
(data / "keypoints").mkdir(parents=True, exist_ok=True)
index, labels = [], None
for idx in sorted(glob.glob("/kaggle/input/**/index.json", recursive=True)):
    src = Path(idx).parent
    if not (src / "keypoints").is_dir():
        continue
    part = json.loads(Path(idx).read_text())
    index += part
    labels = labels or json.loads((src / "labels.json").read_text(encoding="utf-8"))
    for r in part:
        dst = data / "keypoints" / f"{r['video_id']}.npy"
        if not dst.exists():
            dst.symlink_to(src / "keypoints" / f"{r['video_id']}.npy")
assert len({r["video_id"] for r in index}) == len(index) == 11980, len(index)
print(f"合併 {len(index)} 支、{len(labels)} 類", flush=True)

signer_of = load_signers()
folds = assign_folds(index, signer_of, K, EVAL_CLASSES)
fold_dirs = []
for k, holdout in enumerate(folds):
    d = Path(f"/tmp/fold{k}")
    d.mkdir(exist_ok=True)
    if not (d / "keypoints").exists():
        (d / "keypoints").symlink_to(data / "keypoints")
    (d / "index.json").write_text(json.dumps(resplit(index, signer_of, set(holdout))))
    (d / "labels.json").write_text(json.dumps(labels, ensure_ascii=False), encoding="utf-8")
    fold_dirs.append(d)
    print(f"fold{k} 留出手語者 {holdout}", flush=True)

out = Path("/kaggle/working")
ngpu = torch.cuda.device_count()
print(f"gpus={ngpu}", flush=True)


def train_cmd(d, dst, extra=()):
    return [sys.executable, "-m", "wlasl.train", "--data", str(d), "--out", str(dst),
            "--eval-classes", str(EVAL_CLASSES), *ARGS, *extra]


def export(d, dst):
    subprocess.check_call([sys.executable, "-m", "wlasl.export", "--data", str(d),
                           "--ckpt", str(dst / "best.pt"), "--out", str(dst)])


def evaluate_fold(k, d, dst):
    sess, _ = make_session(dst / "model.onnx", "cpu")
    recs = [r for r in json.loads((d / "index.json").read_text())
            if r["subset"] in ("test", "test_seen") and r["label"] < EVAL_CLASSES]
    raw = load_raw(d, recs)
    x = np.stack([prepare(s[slice(*labeled_span(r, len(s)))], mode="linear") for r, s in zip(recs, raw)])
    logits = run(sess, x)
    p = np.exp(logits - logits.max(1, keepdims=True))
    p /= p.sum(1, keepdims=True)
    top5 = np.argsort(-p, 1)[:, :5]
    return [{"fold": k, "video_id": r["video_id"], "label": r["label"], "signer": signer_of[r["video_id"]],
             "subset": r["subset"], "orig_test": r["video_id"] in orig_test,
             "top5": top5[i].tolist(), "p1": float(p[i, top5[i, 0]])} for i, r in enumerate(recs)]


orig_test = {r["video_id"] for r in index if r["subset"] == "test"}

# 冒煙測試：fold0 跑 1 epoch，訓練、匯出、評估全部跑通
smoke = Path("/tmp/smoke")
subprocess.check_call(train_cmd(fold_dirs[0], smoke, ["--epochs", "1", "--warmup", "1"]))
export(fold_dirs[0], smoke)
assert evaluate_fold(0, fold_dirs[0], smoke)
print("冒煙測試通過", flush=True)

# 每張 GPU 依序跑分到的折（同卡同時跑兩組會搶 CPU 的資料載入）
gpu_jobs = {g: [k for k in range(K) if k % max(ngpu, 1) == g] for g in range(max(ngpu, 1))}
# 子行程依序跑；某折失敗不影響同卡的下一折，最後統一檢查
script = ("import subprocess,sys,json\nrc=0\nfor c,log in json.loads(sys.argv[1]):\n"
          "    with open(log,'w') as f: rc|=subprocess.call(c,stdout=f,stderr=subprocess.STDOUT)\nsys.exit(rc)")
procs = []
for g, ks in gpu_jobs.items():
    jobs = []
    for k in ks:
        dst = out / f"fold{k}"
        dst.mkdir(exist_ok=True)
        jobs.append([train_cmd(fold_dirs[k], dst), str(dst / "train.log")])
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": str(g)}
    procs.append(subprocess.Popen([sys.executable, "-c", script, json.dumps(jobs)], env=env))
codes = [p.wait() for p in procs]

results, failed = [], []
for k, d in enumerate(fold_dirs):
    dst = out / f"fold{k}"
    print(f"===== fold{k} =====\n" + (dst / "train.log").read_text()[-1500:], flush=True)
    if not (dst / "best.pt").exists():
        failed.append(k)
        continue
    export(d, dst)
    results += evaluate_fold(k, d, dst)
    (dst / "best.pt").unlink()  # 只留匯出結果，省輸出空間
(out / "cv_results.json").write_text(json.dumps({"folds": folds, "args": ARGS, "labels": labels[:EVAL_CLASSES],
                                                 "results": results}))
print(f"評估 {len(results)} 筆", flush=True)
assert not failed and not any(codes), f"失敗的折：{failed} {codes}"
