# Kaggle CPU kernel：只是殼，邏輯在 wlasl.aslcitizen
# ASL Citizen train+val 中和 WLASL2000 完全同名的 1,159 詞（約 2.1 萬支）→ /kaggle/working/{keypoints, index.json, labels.json, failed.json}
# 授權只限非商業研究、不得散布：kernel 必須維持私人，產出不上傳成 Dataset
# scripts/kaggle_preprocess_shards.ps1 -Template aslc_prep -Prefix aslc-prep -Shards 6 會改寫 SHARD 推成 aslc-prep-<i>
import glob
import os
import subprocess
import sys

SHARD = 0
SHARDS = 6

whl = glob.glob("/kaggle/input/**/wlasl-*.whl", recursive=True)
assert whl, "找不到 wlasl wheel，先跑 scripts/kaggle_push_code.ps1"
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--force-reinstall", "--no-deps", whl[0]])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "mediapipe==1.1.0"])

labels = [p for p in glob.glob("/kaggle/input/**/labels.json", recursive=True) if "wlasl-prep-0" in p]
assert labels, "找不到 wlasl-prep-0 的 labels.json"
workers = os.cpu_count() or 4
print(f"labels={labels[0]} workers={workers} shard={SHARD}/{SHARDS}", flush=True)
subprocess.check_call(
    [sys.executable, "-m", "wlasl.aslcitizen", "--labels", labels[0], "--out", "/kaggle/working",
     "--workers", str(workers), "--shard", str(SHARD), "--shards", str(SHARDS)]
)
