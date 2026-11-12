# Kaggle CPU kernel：只是殼，邏輯在 wlasl.aslcitizen
# ASL Citizen test 中和 WLASL2000 完全同名的 1,159 詞（14,121 支、11 位沒進訓練的手語者），只給本機驗收 2000 詞版
# 產出 /kaggle/working/{keypoints.zip, index.json, labels.json, failed.json}；subset 是 aslc_test，kernel 名稱也不是 aslc-prep-*，訓練不會讀到
# 授權只限非商業研究、不得散布：kernel 必須維持私人，產出不上傳成 Dataset
# scripts/kaggle_preprocess_shards.ps1 -Template aslct_prep -Prefix aslct-prep -Shards 5
import glob
import os
import shutil
import subprocess
import sys

SHARD = 0
SHARDS = 5

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
     "--workers", str(workers), "--shard", str(SHARD), "--shards", str(SHARDS), "--splits", "test", "--subset", "aslc_test"]
)
# 本機要下載關鍵點：上萬個小檔下載很慢，打包成一個 zip 後刪掉原檔
shutil.make_archive("/kaggle/working/keypoints", "zip", "/kaggle/working", "keypoints")
shutil.rmtree("/kaggle/working/keypoints")
