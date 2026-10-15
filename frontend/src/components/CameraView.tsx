import { useEffect, useRef, type RefObject } from 'react';
import { Hand, VideoOff } from 'lucide-react';
import { drawSkeleton } from '../lib/skeleton';
import type { FrameEvent } from '../lib/protocol';

interface Props {
    videoRef: RefObject<HTMLVideoElement>;
    frame: FrameEvent | null;
    /** 前鏡頭只翻轉顯示，送給後端的影格維持原樣（訓練資料沒有翻轉） */
    mirrored: boolean;
    live: boolean;
    /** 蓋在畫面上的提示，例如「逐幀分析中」 */
    notice?: string;
}

export default function CameraView({ videoRef, frame, mirrored, live, notice }: Props) {
    const overlayRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = overlayRef.current;
        const video = videoRef.current;
        if (!canvas || !video) return;
        if (video.videoWidth && canvas.width !== video.videoWidth) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        }
        drawSkeleton(canvas, live ? frame?.points ?? null : null);
    }, [frame, live, videoRef]);

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
                        {frame.active ? (
                            <span className="px-2.5 py-1 rounded-full bg-red-600 text-white text-xs font-semibold flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-white animate-pulse" /> 比劃中
                            </span>
                        ) : (
                            <span className="px-2.5 py-1 rounded-full bg-black/50 text-gray-200 text-xs">等待手勢</span>
                        )}
                    </div>
                    <div className="absolute top-3 right-3 px-2.5 py-1 rounded-full bg-black/50 text-xs flex items-center gap-1.5">
                        <Hand className={`w-3.5 h-3.5 ${hands ? 'text-green-400' : 'text-gray-400'}`} />
                        <span className={hands ? 'text-green-300' : 'text-gray-300'}>{hands ? `偵測到 ${hands} 隻手` : '沒有偵測到手'}</span>
                    </div>
                </>
            )}
        </div>
    );
}
