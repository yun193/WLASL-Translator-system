# Kaggle CPU kernel：把 wlasl-train 產出的某組 best.pt 重新匯出成指定詞彙量（例如 2000 詞版）
# 輸入：wlasl-train 的產出（<設定名>/best.pt）、前處理分片（合併成一份資料夾，算 reference 用）
# 產出：/kaggle/working/<設定名>-<詞數>/{model.onnx, labels.json, reference.npz, metrics.json}
#       /kaggle/working/testdata/：前 <詞數> 類 test 的整支影片關鍵點，本機驗證用
import glob
import json
import shutil
import subprocess
import sys
from pathlib import Path

CONFIG = "w2000n"
CLASSES = 2000

whl = glob.glob("/kaggle/input/**/wlasl-*.whl", recursive=True)
assert whl, "找不到 wlasl wheel，先跑 scripts/kaggle_push_code.ps1"
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--force-reinstall", "--no-deps", whl[0]])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "onnx", "onnxruntime"])

# 合併分片（和 kaggle/train/train.py 相同）
data = Path("/tmp/data")
(data / "keypoints").mkdir(parents=True, exist_ok=True)
index, labels = [], None
for idx in sorted(glob.glob("/kaggle/input/**/index.json", recursive=True)):
    src = Path(idx).parent
    # wlasl-train 的產出也有 testdata/{index.json, keypoints}，只取前處理分片
    if not (src / "keypoints").is_dir() or "wlasl-prep" not in str(src):
        continue
    part = json.loads(Path(idx).read_text())
    index += part
    labels = labels or json.loads((src / "labels.json").read_text(encoding="utf-8"))
    for r in part:
        dst = data / "keypoints" / f"{r['video_id']}.npy"
        if not dst.exists():
            dst.symlink_to(src / "keypoints" / f"{r['video_id']}.npy")
(data / "index.json").write_text(json.dumps(index))
(data / "labels.json").write_text(json.dumps(labels, ensure_ascii=False), encoding="utf-8")
print(f"合併 {len(index)} 支、{len(labels)} 類", flush=True)

ckpt = glob.glob(f"/kaggle/input/**/{CONFIG}/best.pt", recursive=True)
assert ckpt, f"找不到 {CONFIG}/best.pt"
out = Path("/kaggle/working") / f"{CONFIG}-{CLASSES}"
out.mkdir(parents=True, exist_ok=True)
subprocess.check_call([sys.executable, "-m", "wlasl.export", "--data", str(data), "--ckpt", ckpt[0],
                       "--out", str(out), "--eval-classes", str(CLASSES)])

test = Path("/kaggle/working/testdata")
(test / "keypoints").mkdir(parents=True, exist_ok=True)
te = [r for r in index if r["subset"] == "test" and r["label"] < CLASSES]
for r in te:
    shutil.copy(data / "keypoints" / f"{r['video_id']}.npy", test / "keypoints")
(test / "index.json").write_text(json.dumps(te, indent=1))
(test / "labels.json").write_text(json.dumps(labels[:CLASSES], ensure_ascii=False, indent=1), encoding="utf-8")
print(f"testdata {len(te)} 支", flush=True)
print((out / "metrics.json").read_text(), flush=True)
