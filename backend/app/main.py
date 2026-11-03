from __future__ import annotations

import asyncio
import json
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import applog, config, security
from .analyze import VideoError, analyze_video
from .inference import Classifier, Ensemble
from .stream import FrameError, SignSession

app = FastAPI(title="WLASL 即時手語辨識", docs_url=None, redoc_url=None, openapi_url=None)
classifier = Classifier(config.MODEL_DIR) if config.MODEL_DIR else None
spot_classifier = None
if classifier and config.SPOT_MODEL_DIR and config.SPOT_MODEL_DIR != config.MODEL_DIR:
    spot_classifier = Classifier(config.SPOT_MODEL_DIR)
    if spot_classifier.labels != classifier.labels:  # 兩個模型的詞彙不同就不能混用
        spot_classifier = None
    elif config.ENSEMBLE:
        # 整段分類和窗口偵測都用兩個模型平均，減少亂認；窗口偵測另外看背景類
        classifier, spot_classifier = (Ensemble(classifier, spot_classifier),
                                       Ensemble(classifier, spot_classifier, use_background=True))
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
        "labels": list(classifier.labels) if classifier else [],
        "mediapipe_model": config.MP_MODEL.is_file(),
        "segmenter": {"rest": config.REST_SECONDS, "min": config.MIN_SIGN_SECONDS, "max": config.MAX_SIGN_SECONDS},
        "min_confidence": config.MIN_CONFIDENCE,
        "spotting": {"model": (spot_classifier or classifier).run_name if classifier else None,
                     "after": config.CONTINUOUS_AFTER, "window": config.SPOT_WINDOW, "hits": config.SPOT_MIN_HITS,
                     "threshold": config.SPOT_THRESHOLD} if config.SPOTTING else None,
    }


@app.post("/api/analyze")
async def analyze(request: Request):
    """影片檔逐幀分析（body 直接是影片位元組）。和即時串流共用同一個名額，避免兩邊搶 CPU。"""
    if classifier is None:
        return JSONResponse({"detail": "後端沒有載入模型"}, status_code=503)
    ctype = request.headers.get("content-type", "")
    if not (ctype.startswith("video/") or ctype == "application/octet-stream"):
        return JSONResponse({"detail": "只接受影片檔"}, status_code=415)
    if int(request.headers.get("content-length") or 0) > config.MAX_VIDEO_BYTES:
        return JSONResponse({"detail": "影片檔太大"}, status_code=413)
    if _sessions.locked():
        return JSONResponse({"detail": "辨識正在使用中，請先停止另一邊"}, status_code=503)
    async with _sessions:
        fd, name = tempfile.mkstemp(suffix=".video")
        path = Path(name)
        try:
            size = 0
            with os.fdopen(fd, "wb") as f:
                async for chunk in request.stream():
                    size += len(chunk)
                    if size > config.MAX_VIDEO_BYTES:
                        return JSONResponse({"detail": "影片檔太大"}, status_code=413)
                    f.write(chunk)
            try:
                result = await asyncio.to_thread(analyze_video, path, classifier, spot_classifier)
            except VideoError as exc:
                return JSONResponse({"detail": str(exc)}, status_code=422)
        finally:
            path.unlink(missing_ok=True)
    applog.event("analyze", bytes=size, frames=result["frames"], elapsed_s=result["elapsed_s"],
                 signs=[x["gloss"] for x in result["signs"]])
    return result


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
        session = await asyncio.to_thread(SignSession, classifier, None, spot_classifier)
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
