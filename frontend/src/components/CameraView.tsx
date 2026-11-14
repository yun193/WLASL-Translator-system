import { useEffect, useRef, useState, type RefObject } from 'react';
import { Hand, VideoOff } from 'lucide-react';
import { drawSkeleton } from '../lib/skeleton';
import { loadTracker, track } from '../lib/localTracker';
import type { FrameEvent } from '../lib/protocol';

interface Props {
    videoRef: RefObject<HTMLVideoElement>;
    frame: FrameEvent | null;
    /** 前鏡頭只翻轉顯示，送給後端的影格維持原樣（訓練資料沒有翻轉） */
    mirrored: boolean;
    live: boolean;
    /** 蓋在畫面上的提示，例如「逐幀分析中」 */
    notice?: string;
    /** 鏡頭模式：骨架改由瀏覽器端 MediaPipe 每個鏡頭幀即時畫（辨識仍用後端的點） */
    localTrack?: boolean;
}

const SLOW_MS = 60;

export default function CameraView({ videoRef, frame, mirrored, live, notice, localTrack }: Props) {
    const overlayRef = useRef<HTMLCanvasElement>(null);
    const [localFps, setLocalFps] = useState(0);  // >0 表示瀏覽器端骨架正在跑
    const [localMs, setLocalMs] = useState(0);  // 每幀偵測耗時
    const local = localTrack && live;

    const fitCanvas = () => {
        const canvas = overlayRef.current;
        const video = videoRef.current;
        if (canvas && video?.videoWidth && canvas.width !== video.videoWidth) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        }
        return canvas;
    };

    // 後端的點：影片檔模式，或瀏覽器端骨架還沒載好／載入失敗時
    useEffect(() => {
        if (local && localFps > 0) return;
        const canvas = fitCanvas();
        if (canvas) drawSkeleton(canvas, live ? frame?.points ?? null : null);
    }, [frame, live, local, localFps, videoRef]);

    // 瀏覽器端：每個鏡頭新幀畫一次
    useEffect(() => {
        if (!local) { setLocalFps(0); return; }
        let stop = false;
        let handle = 0;
        let last = 0;
        let fps = 0;
        let lastShown = 0;
        let ms = 0;
        let frames = 0;
        loadTracker().then((tracker) => {
            const step = () => {
                const video = videoRef.current;
                const canvas = fitCanvas();
                if (stop || !video) return;
                if (canvas && video.readyState >= 2) {
                    const now = performance.now();
                    drawSkeleton(canvas, track(tracker, video, now));
                    const cost = performance.now() - now;
                    frames++;
                    if (frames > 3) ms = ms ? ms * 0.8 + cost * 0.2 : cost;  // 前 3 幀含顯示卡暖機，不算
                    if (last) fps = fps ? fps * 0.9 + (1000 / (now - last)) * 0.1 : 1000 / (now - last);
                    last = now;
                    if (now - lastShown > 500) { setLocalFps(fps); setLocalMs(ms); lastShown = now; }
                    // 太慢會拖到送給後端的影格（同一條主執行緒）→ 放棄，改畫後端的點
                    if (frames > 8 && ms > SLOW_MS) {
                        console.warn(`瀏覽器端骨架每幀 ${ms.toFixed(0)} ms，太慢，改用後端的點`);
                        stop = true; setLocalFps(0); return;
                    }
                }
                handle = video.requestVideoFrameCallback(step);
            };
            step();
        }).catch((e) => console.warn('瀏覽器端骨架載入失敗，改用後端的點', e));
        return () => { stop = true; videoRef.current?.cancelVideoFrameCallback(handle); setLocalFps(0); };
    }, [local, videoRef]);

    const hands = frame ? frame.hands.filter(Boolean).length : 0;

    return (
        <div className="relative bg-gray-900 rounded-xl overflow-hidden min-h-[240px] flex items-center justify-center">
            <div className={`relative w-full ${live ? '' : 'hidden'}`} style={mirrored ? { transform: 'scaleX(-1)' } : undefined}>
                <video ref={videoRef} className="block w-full h-auto" playsInline muted />
                <canvas ref={overlayRef} className="absolute inset-0 w-full h-full pointer-events-none" />
            </div>
            {!live && (
                <div className="text-gray-400 flex flex-col items-center gap-2 py-16">
                    <VideoOff className="w-10 h-10" />
                    <span className="text-sm">按「開啟鏡頭」或選一支影片檔開始</span>
                </div>
            )}
            {live && notice && (
                <div className="absolute inset-0 bg-black/60 flex items-center justify-center text-white text-sm gap-2">
                    <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" /> {notice}
                </div>
            )}
            {live && frame && (
                <>
                    <div className="absolute top-3 left-3 flex gap-2">
                        {frame.active && frame.continuous ? (
                            <span className="px-2.5 py-1 rounded-full bg-orange-600 text-white text-xs font-semibold flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-white animate-pulse" /> 連續比劃・逐詞偵測
                            </span>
                        ) : frame.active ? (
                            <span className="px-2.5 py-1 rounded-full bg-red-600 text-white text-xs font-semibold flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-white animate-pulse" /> 比劃中
                            </span>
                        ) : (
                            <span className="px-2.5 py-1 rounded-full bg-black/50 text-gray-200 text-xs">等待手勢</span>
                        )}
                    </div>
                    {localFps > 0 && (
                        <div className="absolute bottom-3 right-3 px-2 py-0.5 rounded-full bg-black/50 text-[11px] text-gray-200">
                            骨架 {localFps.toFixed(0)} fps・每幀 {localMs.toFixed(0)} ms（瀏覽器）
                        </div>
                    )}
                    <div className="absolute top-3 right-3 px-2.5 py-1 rounded-full bg-black/50 text-xs flex items-center gap-1.5">
                        <Hand className={`w-3.5 h-3.5 ${hands ? 'text-green-400' : 'text-gray-400'}`} />
                        <span className={hands ? 'text-green-300' : 'text-gray-300'}>{hands ? `偵測到 ${hands} 隻手` : '沒有偵測到手'}</span>
                    </div>
                </>
            )}
        </div>
    );
}
