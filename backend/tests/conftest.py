import os
import tempfile

# 必須在匯入 app 之前設定
os.environ["WLASL_LOG_DIR"] = tempfile.mkdtemp(prefix="wlasl-test-log-")
os.environ.pop("WLASL_DEV", None)

from app.winperf import disable_power_throttling  # noqa: E402

# 背景執行的測試也會被 EcoQoS 節流，MediaPipe 慢 6 倍
disable_power_throttling()
