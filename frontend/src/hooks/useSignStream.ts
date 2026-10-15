import { useCallback, useEffect, useRef, useState, type RefObject } from 'react';
import { CLOSE_REASONS, packFrame, type FrameEvent, type ServerEvent, type SignEvent } from '../lib/protocol';

export type Status = 'idle' | 'starting' | 'running' | 'error';
export interface Stats { fps: number; mpMs: number; rttMs: number }

// 基準測試：480p 每幀約 74 ms，7.5～15 fps 準確率不變 → 送 640×480 以內、最多 15 fps
const MAX_W = 640;
const MAX_H = 480;
const MAX_FPS = 15;
const JPEG_QUALITY = 0.8;

function cameraError(err: unknown): string {
    const name = err instanceof DOMException ? err.name : '';
    if (name === 'NotAllowedError') return '鏡頭權限被拒絕：請在網址列左側允許使用鏡頭';
    if (name === 'NotFoundError') return '找不到鏡頭';
    if (name === 'NotReadableError') return '鏡頭被其他程式占用';
    return `無法開啟影像來源：${err instanceof Error ? err.message : String(err)}`;
}

/**
 * 前鏡頭 → WebSocket → 即時字幕（影片檔改走 useVideoAnalysis 逐幀分析）。
 * 一來一回：收到這一幀的 frame 回覆才送下一幀，送的速度自動配合後端處理速度，延遲不會越堆越長。
 */
export function useSignStream(videoRef: RefObject<HTMLVideoElement>) {
    const [status, setStatus] = useState<Status>('idle');
    const [error, setError] = useState('');
    const [frame, setFrame] = useState<FrameEvent | null>(null);
    const [signs, setSigns] = useState<SignEvent[]>([]);
    const [stats, setStats] = useState<Stats>({ fps: 0, mpMs: 0, rttMs: 0 });

    const wsRef = useRef<WebSocket | null>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const timerRef = useRef(0);
    const sentAtRef = useRef(0);
    const lastReplyRef = useRef(0);
    const fpsRef = useRef(0);

    const cleanup = useCallback(() => {
        window.clearTimeout(timerRef.current);
        const ws = wsRef.current;
        wsRef.current = null;
        if (ws) {
            ws.onclose = null;
            ws.onmessage = null;
            ws.close();
        }
        streamRef.current?.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
        const video = videoRef.current;
        if (video && video.srcObject) {
            video.pause();
            video.srcObject = null;
        }
    }, [videoRef]);

    const sendNext = useCallback(async () => {
        const ws = wsRef.current;
        const video = videoRef.current;
        if (!ws || ws.readyState !== WebSocket.OPEN || !video) return;
        if (video.readyState < 2 || !video.videoWidth) {
            timerRef.current = window.setTimeout(sendNext, 50);
            return;
        }
        const s = Math.min(1, MAX_W / video.videoWidth, MAX_H / video.videoHeight);
        const canvas = (canvasRef.current ??= document.createElement('canvas'));
        canvas.width = Math.round(video.videoWidth * s);
        canvas.height = Math.round(video.videoHeight * s);
        canvas.getContext('2d')!.drawImage(video, 0, 0, canvas.width, canvas.height);
        const ts = performance.now();
        const blob = await new Promise<Blob | null>((r) => canvas.toBlob(r, 'image/jpeg', JPEG_QUALITY));
        if (!blob || wsRef.current !== ws) return;
        const payload = packFrame(ts, await blob.arrayBuffer());
        if (wsRef.current !== ws) return;
        sentAtRef.current = performance.now();
        ws.send(payload);
    }, [videoRef]);

    const scheduleNext = useCallback(() => {
        const wait = Math.max(0, sentAtRef.current + 1000 / MAX_FPS - performance.now());
        timerRef.current = window.setTimeout(sendNext, wait);
    }, [sendNext]);

    const onMessage = useCallback((ev: MessageEvent) => {
        if (typeof ev.data !== 'string') return;
        const e = JSON.parse(ev.data) as ServerEvent;
        if (e.type === 'frame') {
            const now = performance.now();
            const dt = now - lastReplyRef.current;
            lastReplyRef.current = now;
            if (dt > 0 && dt < 2000) fpsRef.current = fpsRef.current ? fpsRef.current * 0.9 + (1000 / dt) * 0.1 : 1000 / dt;
            setFrame(e);
            setStats({ fps: fpsRef.current, mpMs: e.mp_ms, rttMs: now - sentAtRef.current });
            scheduleNext();
        } else if (e.type === 'sign') {
            setSigns((prev) => [...prev, e]);
        } else if (e.type === 'error') {
            setError(e.detail);
            scheduleNext();
        }
    }, [scheduleNext]);

    const start = useCallback(async () => {
        cleanup();
        setError('');
        setFrame(null);
        // 每次換來源都是新的一段辨識，字幕不接續上一段（否則多次播放同一支單字影片會看起來像句子）
        setSigns([]);
        setStatus('starting');
        fpsRef.current = 0;
        const video = videoRef.current;
        if (!video) return;
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: MAX_W }, height: { ideal: MAX_H }, facingMode: 'user' },
                audio: false,
            });
            streamRef.current = stream;
            video.srcObject = stream;
            await video.play();
        } catch (err) {
            cleanup();
            setStatus('error');
            setError(cameraError(err));
            return;
        }

        const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/stream`);
        ws.binaryType = 'arraybuffer';
        wsRef.current = ws;
        ws.onopen = () => {
            setStatus('running');
            lastReplyRef.current = performance.now();
            sendNext();
        };
        ws.onmessage = onMessage;
        ws.onclose = (ev) => {
            if (wsRef.current !== ws) return;
            cleanup();
            setStatus('error');
            setError(CLOSE_REASONS[ev.code] ?? `和後端的連線中斷（代碼 ${ev.code}）`);
        };
    }, [cleanup, onMessage, sendNext, videoRef]);

    const stop = useCallback(() => {
        cleanup();
        setStatus('idle');
        setFrame(null);
    }, [cleanup]);

    const send = useCallback((type: 'flush' | 'reset') => {
        const ws = wsRef.current;
        if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type }));
    }, []);

    const flush = useCallback(() => send('flush'), [send]);
    const clear = useCallback(() => {
        send('reset');
        setSigns([]);
    }, [send]);

    useEffect(() => cleanup, [cleanup]);

    return { status, error, frame, signs, stats, start, stop, flush, clear };
}
