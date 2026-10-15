from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import applog, config, security
from .inference import Classifier
from .stream import FrameError, SignSession

app = FastAPI(title="WLASL 即時手語辨識", docs_url=None, redoc_url=None, openapi_url=None)
classifier = Classifier(config.MODEL_DIR) if config.MODEL_DIR else None
_sessions = asyncio.Semaphore(config.MAX_SESSIONS)
applog.event("startup", port=config.PORT, dev=config.DEV, model=classifier.run_name if classifier else None)


@app.middleware("http")
async def guard(request: Request, call_next):
    reason = security.check_request(request.method, request.headers)
    if reason:
        applog.event("request_blocked", "warning", reason=reason, method=request.method, path=request.url.path,
                     host=request.headers.get("host"), origin=request.headers.get("origin"))
        return JSONResponse({"detail": reason}, status_code=403)
    response = await call_next(request)
    for name, value in security.SECURITY_HEADERS.items():
        response.headers.setdefault(name, value)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/api/health")
def health():
    return {
        "model": classifier.run_name if classifier else None,
        "classes": len(classifier.labels) if classifier else 0,
        "mediapipe_model": config.MP_MODEL.is_file(),
        "segmenter": {"rest": config.REST_SECONDS, "min": config.MIN_SIGN_SECONDS, "max": config.MAX_SIGN_SECONDS},
        "min_confidence": config.MIN_CONFIDENCE,
    }


def _parse_command(text: str) -> str | None:
    try:
        data = json.loads(text)
    except ValueError:
        return None
    return data.get("type") if isinstance(data, dict) else None


@app.websocket("/ws/stream")
async def stream(ws: WebSocket):
    # WebSocket 握手不經過 HTTP middleware，要在 accept 前自己檢查
    reason = security.check_websocket(ws.headers)
    if reason:
        applog.event("ws_blocked", "warning", reason=reason, origin=ws.headers.get("origin"))
        await ws.close(code=1008)
        return
    if classifier is None:
        await ws.close(code=1011, reason="no model")
        return
    if _sessions.locked():
        await ws.close(code=1013, reason="busy")
        return
    async with _sessions:
        await ws.accept()
        session = await asyncio.to_thread(SignSession, classifier)
        applog.event("stream_open")
        frames = signs = 0
        try:
            while True:
                msg = await ws.receive()
                if msg["type"] == "websocket.disconnect":
                    break
                if msg.get("bytes") is not None:
                    try:
                        events = await asyncio.to_thread(session.handle_frame, msg["bytes"])
                    except FrameError as exc:
                        events = [{"type": "error", "detail": str(exc)}]
                    frames += 1
                elif msg.get("text") is not None:
                    kind = _parse_command(msg["text"])
                    if kind == "flush":
                        events = await asyncio.to_thread(session.flush)
                    elif kind == "reset":
                        session.reset()
                        events = [{"type": "reset"}]
                    else:
                        events = [{"type": "error", "detail": "未知的指令"}]
                else:
                    continue
                for e in events:
                    if e["type"] == "sign":
                        signs += 1
                        applog.event("sign", gloss=e["gloss"], prob=e["prob"], frames=e["frames"])
                    await ws.send_json(e)
        except WebSocketDisconnect:
            pass
        finally:
            await asyncio.to_thread(session.close)
            applog.event("stream_close", frames=frames, signs=signs)


if config.FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=config.FRONTEND_DIST, html=True), name="frontend")
