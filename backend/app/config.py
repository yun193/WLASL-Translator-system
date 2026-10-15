"""集中管理設定。只在本機使用，HOST 不開放由環境變數覆寫。"""
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


# 分類模型：預設用 models/ 底下最新的一版（scripts/kaggle_pull_model.ps1 拉下來的）
MODEL_DIR = Path(os.environ["WLASL_MODEL_DIR"]) if os.environ.get("WLASL_MODEL_DIR") else _latest_model_dir()
# MediaPipe Holistic 模型檔，不存在時第一次啟動會自動下載
MP_MODEL = ROOT_DIR / "data" / "models" / "holistic_landmarker.task"

# 串流：前端一來一回送影格，後端處理不完就自然降速；這些是上限
MAX_SESSIONS = 1
MAX_FRAME_BYTES = 2 * 1024 * 1024
MAX_FRAME_PIXELS = 1920 * 1080

# 切詞（秒）：手出現就開始，手消失超過 REST_SECONDS 就切；單詞太短丟掉、太長強制切
REST_SECONDS = 0.5
PRE_ROLL_SECONDS = 0.3
MIN_SIGN_SECONDS = 0.4
MAX_SIGN_SECONDS = 4.0
# top-1 機率低於門檻就回報「不確定」而不是硬猜
MIN_CONFIDENCE = 0.3

# 即時紀錄檔（JSONL）
LOG_DIR = Path(os.environ.get("WLASL_LOG_DIR") or ROOT_DIR / "logs")
LOG_FILE = LOG_DIR / "log.jsonl"
