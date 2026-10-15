"""即時紀錄檔：一行一筆 JSON（JSONL），只往檔尾追加。

不記影格內容與關鍵點座標，只記事件、數量、延遲與辨識結果。
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

from . import config

_logger = logging.getLogger("wlasl.events")
_logger.setLevel(logging.INFO)
_logger.propagate = False


def _setup() -> None:
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    # 單檔 2 MB，保留 3 份舊檔，不會無限長大
    handler = RotatingFileHandler(config.LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(handler)


_setup()


def event(name: str, level: str = "info", **fields) -> None:
    record = {"ts": datetime.now().astimezone().isoformat(timespec="milliseconds"), "level": level, "event": name}
    record.update({k: v for k, v in fields.items() if v is not None})
    _logger.info(json.dumps(record, ensure_ascii=False, default=str))
