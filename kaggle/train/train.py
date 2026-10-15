# Kaggle 2×T4 kernel：只是殼，邏輯在 wlasl.train / wlasl.export
# 產出 /kaggle/working/{best.pt, history.json, model.onnx, labels.json, reference.npz, metrics.json}
import glob
import subprocess
import sys
from pathlib import Path

import torch

# 重訓時只改這一行（傳給 wlasl.train 的超參數，例：["--seed", "1", "--d", "160"]）
TRAIN_ARGS: list[str] = []

whl = glob.glob("/kaggle/input/**/wlasl-*.whl", recursive=True)
assert whl, "找不到 wlasl wheel，先跑 scripts/kaggle_push_code.ps1"
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--force-reinstall", "--no-deps", whl[0]])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "onnx", "onnxruntime"])

data = Path(glob.glob("/kaggle/input/**/index.json", recursive=True)[0]).parent
out = Path("/kaggle/working")
ngpu = torch.cuda.device_count()
print(f"data={data} gpus={ngpu} {[torch.cuda.get_device_name(i) for i in range(ngpu)]}", flush=True)

def run(*args):
    subprocess.check_call(["torchrun", f"--nproc_per_node={max(ngpu, 1)}", "-m", "wlasl.train",
                           "--data", str(data), *args])

# 冒煙測試：2 個 epoch 跑通 DDP 與匯出，有錯在幾分鐘內就失敗
smoke = Path("/tmp/smoke")
run("--out", str(smoke), "--epochs", "2", "--warmup", "1")
subprocess.check_call([sys.executable, "-m", "wlasl.export", "--data", str(data),
                       "--ckpt", str(smoke / "best.pt"), "--out", str(smoke)])
print("冒煙測試通過", flush=True)

run("--out", str(out), *TRAIN_ARGS)
subprocess.check_call([sys.executable, "-m", "wlasl.export", "--data", str(data),
                       "--ckpt", str(out / "best.pt"), "--out", str(out)])
