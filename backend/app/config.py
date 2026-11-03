"""集中管理設定。只在本機使用，HOST 不開放由環境變數覆寫。"""
import json
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"

HOST = "127.0.0.1"
PORT = int(os.environ.get("WLASL_PORT", "8766"))
# 開發模式才放行 Vite dev server 的來源
DEV = os.environ.get("WLASL_DEV") == "1"
DEV_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


def _latest_model_dir() -> Path | None:
    runs = [p for p in (ROOT_DIR / "models").glob("*") if (p / "model.onnx").is_file()]
    return max(runs, key=lambda p: p.stat().st_mtime) if runs else None


def _latest_background_model_dir() -> Path | None:
    runs = [p for p in (ROOT_DIR / "models").glob("*") if (p / "model.onnx").is_file()
            and json.loads((p / "labels.json").read_text(encoding="utf-8"))[-1] == "_bg"]
    return max(runs, key=lambda p: p.stat().st_mtime) if runs else None


# 分類模型：預設用 models/ 底下最新的一版（scripts/kaggle_pull_model.ps1 拉下來的）
MODEL_DIR = Path(os.environ["WLASL_MODEL_DIR"]) if os.environ.get("WLASL_MODEL_DIR") else _latest_model_dir()
# 連續比劃的窗口偵測用的模型：預設用最新一版有背景類（不是詞）的模型；沒有就和 MODEL_DIR 同一個。
# 2026-10-19 spotbench：單字整段分類 w2000n 較好（第一個詞正確 70% vs 64%），連續偵測 w2000bg 較好（合成召回 59% vs 51%，誤報相同）
SPOT_MODEL_DIR = (Path(os.environ["WLASL_SPOT_MODEL_DIR"]) if os.environ.get("WLASL_SPOT_MODEL_DIR")
                  else _latest_background_model_dir() or MODEL_DIR)
# 整段分類用兩個模型（MODEL_DIR＋SPOT_MODEL_DIR）平均；設 0 只用 MODEL_DIR
ENSEMBLE = os.environ.get("WLASL_ENSEMBLE", "1") != "0"
# MediaPipe Holistic 模型檔，不存在時第一次啟動會自動下載
MP_MODEL = ROOT_DIR / "data" / "models" / "holistic_landmarker.task"

# 串流：前端一來一回送影格，後端處理不完就自然降速；這些是上限
MAX_SESSIONS = 1
MAX_FRAME_BYTES = 2 * 1024 * 1024
MAX_FRAME_PIXELS = 1920 * 1080

# 影片檔逐幀分析：上傳大小、長度上限；高度超過就縮到 720p（每幀成本和解析度成正比）
MAX_VIDEO_BYTES = 100 * 1024 * 1024
MAX_VIDEO_SECONDS = 60
MAX_VIDEO_HEIGHT = 720

# 切詞（秒）：手出現就開始，手消失超過 REST_SECONDS 就切；單詞太短丟掉、太長強制切
REST_SECONDS = 0.5
PRE_ROLL_SECONDS = 0.3
MIN_SIGN_SECONDS = 0.4
MAX_SIGN_SECONDS = 4.0
# top-1 機率低於門檻就回報「不確定」而不是硬猜
# 0.5：w2000 test 上涵蓋 76%、其中正確 91%；鏡頭模式的相位翻盤幾乎都落在門檻以下
MIN_CONFIDENCE = float(os.environ.get("WLASL_MIN_CONFIDENCE", "0.5"))

# 連續比劃（對話）：同一段比超過 CONTINUOUS_AFTER 秒就改用滑動窗口偵測，
# 每 SPOT_HOP 秒分類最近 SPOT_WINDOW 秒，連續 SPOT_MIN_HITS 個窗口同一個詞、信心 ≥ SPOT_THRESHOLD 才輸出
SPOTTING = os.environ.get("WLASL_SPOTTING", "1") == "1"
CONTINUOUS_AFTER = 3.5  # WLASL test 的單字段落（含 pre-roll 與段尾靜止）中位 2.0 秒、超過 3.5 秒的只有 3%
# 在合成連續手語與 podcast 前半掃 window × hits × th，誤報 ≤ 5 次/分鐘時 w2000bg 召回最高的組合
SPOT_WINDOW = 1.3
SPOT_HOP = 0.25
SPOT_MIN_HITS = 1
SPOT_THRESHOLD_SINGLE = 0.7
# 雙模型平均：scripts/spotgate.py 在合成連續的偶數半，誤報降到單模型一半時的門檻
SPOT_THRESHOLD = float(os.environ.get("WLASL_SPOT_THRESHOLD", "0.78" if ENSEMBLE else SPOT_THRESHOLD_SINGLE))

# 即時紀錄檔（JSONL）
LOG_DIR = Path(os.environ.get("WLASL_LOG_DIR") or ROOT_DIR / "logs")
LOG_FILE = LOG_DIR / "log.jsonl"
