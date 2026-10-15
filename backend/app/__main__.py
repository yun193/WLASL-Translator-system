import socket
import sys
import threading
import webbrowser

import uvicorn

from . import config


def _port_in_use() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind((config.HOST, config.PORT))
        except OSError:
            return True
    return False


def main() -> None:
    url = f"http://{config.HOST}:{config.PORT}"
    open_browser = "--no-browser" not in sys.argv
    if _port_in_use():
        print(f"WLASL 即時辨識已經在執行（{url}），不重複啟動。", file=sys.stderr)
        if open_browser:
            webbrowser.open(url)
        sys.exit(1)
    if config.MODEL_DIR is None:
        print("找不到模型：先執行 scripts/kaggle_pull_model.ps1，或設定 WLASL_MODEL_DIR", file=sys.stderr)
        sys.exit(1)
    if not config.FRONTEND_DIST.is_dir():
        print("尚未建置前端：請先在 frontend 執行 npm install && npm run build", file=sys.stderr)
    elif open_browser:
        threading.Timer(1.0, webbrowser.open, args=(url,)).start()
    print(f"WLASL 即時辨識：{url}（模型 {config.MODEL_DIR.name}，只接受本機連線，Ctrl+C 結束）")
    uvicorn.run("app.main:app", host=config.HOST, port=config.PORT, log_level="warning", server_header=False)


if __name__ == "__main__":
    main()
