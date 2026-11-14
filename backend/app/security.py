"""本機服務的防護：擋跨站請求與 DNS rebinding。

HTTP 由 main.py 的 middleware 檢查；WebSocket 握手不經過 HTTP middleware，
所以 stream 端點在 accept 之前要另外呼叫 check_websocket。
"""
from __future__ import annotations

from . import config

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Content-Security-Policy": (
        # wasm-unsafe-eval：瀏覽器端 MediaPipe（只畫骨架）要編譯 WebAssembly，不開放一般 eval
        "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; img-src 'self' blob: data:; style-src 'self' 'unsafe-inline'; "
        "media-src 'self' blob:; connect-src 'self'; "
        "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
    ),
    # 只有本頁可以開鏡頭
    "Permissions-Policy": "camera=(self), microphone=(), geolocation=()",
}


def allowed_hosts() -> set[str]:
    return {f"127.0.0.1:{config.PORT}", f"localhost:{config.PORT}"}


def allowed_origins() -> set[str]:
    origins = {f"http://{host}" for host in allowed_hosts()}
    if config.DEV:
        origins.update(config.DEV_ORIGINS)
    return origins


def check_request(method: str, headers) -> str | None:
    """回傳拒絕原因；None 代表放行。

    Host 檢查擋 DNS rebinding（惡意網域解析到 127.0.0.1 時 Host 會是對方的網域）。
    Origin / Sec-Fetch-Site 檢查擋別的網站用瀏覽器對本機 API 發請求。
    """
    if headers.get("host", "").lower() not in allowed_hosts():
        return "Host 不在允許清單"
    origin = headers.get("origin")
    if origin is not None and origin not in allowed_origins():
        return "來源不在允許清單"
    if method not in ("GET", "HEAD", "OPTIONS") and origin is None:
        if headers.get("sec-fetch-site", "same-origin") not in ("same-origin", "none"):
            return "跨站請求"
    return None


def check_websocket(headers) -> str | None:
    """WebSocket 不受同源政策保護，任何網站都能對 ws://127.0.0.1 發起連線，所以 Origin 必須存在且在白名單。"""
    if headers.get("host", "").lower() not in allowed_hosts():
        return "Host 不在允許清單"
    origin = headers.get("origin")
    if origin is None or origin not in allowed_origins():
        return "來源不在允許清單"
    return None
