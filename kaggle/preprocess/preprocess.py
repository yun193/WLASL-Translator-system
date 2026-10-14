# Kaggle CPU kernel：只是殼，邏輯在 wlasl.preprocess
# 產出 /kaggle/working/{keypoints/*.npy, index.json, labels.json, failed.json}
import glob
import os
import subprocess
import sys
from pathlib import Path

whl = glob.glob("/kaggle/input/**/wlasl-*.whl", recursive=True)
assert whl, "找不到 wlasl wheel，先跑 scripts/kaggle_push_code.ps1"
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--force-reinstall", "--no-deps", whl[0]])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "mediapipe==1.1.0"])

root = Path(glob.glob("/kaggle/input/**/nslt_100.json", recursive=True)[0]).parent
assert (root / "videos").is_dir(), f"{root} 底下沒有 videos/"
workers = os.cpu_count() or 4
print(f"root={root} workers={workers}", flush=True)
subprocess.check_call(
    [sys.executable, "-c", "import mediapipe, numpy, cv2; print('mediapipe', mediapipe.__version__, 'numpy', numpy.__version__, 'cv2', cv2.__version__)"]
)
subprocess.check_call(
    [sys.executable, "-m", "wlasl.preprocess", "--root", str(root), "--out", "/kaggle/working",
     "--subset", "100", "--workers", str(workers)]
)
