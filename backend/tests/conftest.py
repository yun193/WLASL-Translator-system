import os
import tempfile

# 必須在匯入 app 之前設定
os.environ["WLASL_LOG_DIR"] = tempfile.mkdtemp(prefix="wlasl-test-log-")
os.environ.pop("WLASL_DEV", None)
