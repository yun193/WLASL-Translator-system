# Kaggle 2×T4 kernel：只是殼，邏輯在 wlasl.train / wlasl.export
# 輸入：前處理分片 kernel（wlasl-prep-*）的產出，合併成一份資料夾
# 產出：/kaggle/working/<設定名>/{best.pt, history.json, model.onnx, labels.json, reference.npz, metrics.json}
#       /kaggle/working/testdata/{index.json, labels.json, keypoints/*.npy}：前 100 類 test，本機驗證用
import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import torch

# 重訓時只改這裡：每個設定佔一張 GPU 同時跑（傳給 wlasl.train 的超參數）
# 2026-11-12：上線雙模型（w2000n＋w2000bg）兩個成員都加入 ASL Citizen train+val（WLASL2000 同名 1,159 詞、41 人），
#   設定和原本完全相同，只多了資料；驗收看本機 ASL Citizen test（11 位沒看過的人）與 WLASL test
# 設定比 GPU 多時兩組共用一張卡
CONFIGS: dict[str, list[str]] = {
    "a2000n": ["--classes", "2000", "--epochs", "100", "--warmup", "5", "--noise"],
    "a2000bg": ["--classes", "2000", "--epochs", "100", "--warmup", "5", "--noise", "--bg", "0.3", "--p-context", "0.3"],
}
# 掛載的前處理產出裡要合併哪些（aslc-prep-* 只限非商業研究，訓練出來的模型不公開、不商用）
SOURCES = ("wlasl-prep-", "aslc-prep-")
EVAL_CLASSES = 100

whl = glob.glob("/kaggle/input/**/wlasl-*.whl", recursive=True)
assert whl, "找不到 wlasl wheel，先跑 scripts/kaggle_push_code.ps1"
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--force-reinstall", "--no-deps", whl[0]])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "onnx", "onnxruntime"])

# 合併分片：index 串起來，關鍵點用符號連結集中到同一個資料夾
data = Path("/tmp/data")
(data / "keypoints").mkdir(parents=True, exist_ok=True)
index, labels = [], None
for idx in sorted(glob.glob("/kaggle/input/**/index.json", recursive=True)):
    src = Path(idx).parent
    if not (src / "keypoints").is_dir() or not any(k in str(src) for k in SOURCES):
        continue
    part = json.loads(Path(idx).read_text())
    index += part
    labels = labels or json.loads((src / "labels.json").read_text(encoding="utf-8"))
    for r in part:
        dst = data / "keypoints" / f"{r['video_id']}.npy"
        if not dst.exists():
            dst.symlink_to(src / "keypoints" / f"{r['video_id']}.npy")
    print(f"{src}: {len(part)} 支", flush=True)
assert len({r["video_id"] for r in index}) == len(index), "分片之間有重複的影片"
(data / "index.json").write_text(json.dumps(index))
(data / "labels.json").write_text(json.dumps(labels, ensure_ascii=False), encoding="utf-8")
print(f"合併 {len(index)} 支、{len(labels)} 類；ASL Citizen {sum(r['video_id'].startswith('aslc-') for r in index)} 支", flush=True)

out = Path("/kaggle/working")
test = out / "testdata"
(test / "keypoints").mkdir(parents=True, exist_ok=True)
te = [r for r in index if r["subset"] == "test" and r["label"] < EVAL_CLASSES]
for r in te:
    shutil.copy(data / "keypoints" / f"{r['video_id']}.npy", test / "keypoints")
(test / "index.json").write_text(json.dumps(te, indent=1))
(test / "labels.json").write_text(json.dumps(labels[:EVAL_CLASSES], ensure_ascii=False, indent=1), encoding="utf-8")

ngpu = torch.cuda.device_count()
print(f"gpus={ngpu} {[torch.cuda.get_device_name(i) for i in range(ngpu)]}", flush=True)


def train_cmd(dst, args):
    return [sys.executable, "-m", "wlasl.train", "--data", str(data), "--out", str(dst),
            "--eval-classes", str(EVAL_CLASSES), *args]


def export(dst):
    subprocess.check_call([sys.executable, "-m", "wlasl.export", "--data", str(data),
                           "--ckpt", str(dst / "best.pt"), "--out", str(dst)])


# 冒煙測試：每個設定 1 個 epoch 跑通訓練與匯出，有錯在幾分鐘內就失敗
for name, args in CONFIGS.items():
    smoke = Path("/tmp/smoke") / name
    subprocess.check_call(train_cmd(smoke, [*args, "--epochs", "1", "--warmup", "1"]))
    export(smoke)
print("冒煙測試通過", flush=True)

procs = {}
for gpu, (name, args) in enumerate(CONFIGS.items()):
    dst = out / name
    dst.mkdir(exist_ok=True)
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": str(gpu % max(ngpu, 1))}
    log = open(dst / "train.log", "w")
    procs[name] = (subprocess.Popen(train_cmd(dst, args), env=env, stdout=log, stderr=subprocess.STDOUT), dst)
failed = []
for name, (p, dst) in procs.items():
    if p.wait() != 0:
        failed.append(name)
        continue
    export(dst)
for name, (_, dst) in procs.items():
    print(f"===== {name} =====\n" + (dst / "train.log").read_text()[-3000:], flush=True)
assert not failed, f"訓練失敗：{failed}"
