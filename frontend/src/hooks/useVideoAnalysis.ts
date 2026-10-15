import { useCallback, useEffect, useRef, useState, type RefObject } from 'react';
import { analyzeVideo, type AnalyzeResult, type FrameEvent, type TrackFrame } from '../lib/protocol';

export type AnalysisStatus = 'idle' | 'analyzing' | 'ready' | 'error';

/** track 依時間排序：找最後一個 t <= time 的幀 */
function frameAt(track: TrackFrame[], time: number): number {
    let lo = 0;
    let hi = track.length - 1;
    if (hi < 0 || time < track[0].t) return -1;
    while (lo < hi) {
        const mid = (lo + hi + 1) >> 1;
        if (track[mid].t <= time) lo = mid;
        else hi = mid - 1;
    }
    return lo;
}

/**
 * 影片檔 → 後端以原生 fps 逐幀分析（結果可重現）→ 播放時依影片時間同步骨架與字幕。
 * 即時串流只能取到約 10 fps，而且每次抽到的幀不同，同一支影片會翻盤；影片檔沒有即時壓力，不必妥協。
 */
export function useVideoAnalysis(videoRef: RefObject<HTMLVideoElement>) {
    const [status, setStatus] = useState<AnalysisStatus>('idle');
    const [error, setError] = useState('');
    const [result, setResult] = useState<AnalyzeResult | null>(null);
    const [frame, setFrame] = useState<FrameEvent | null>(null);
    const [currentSign, setCurrentSign] = useState(-1);

    const urlRef = useRef<string | null>(null);
    const abortRef = useRef<AbortController | null>(null);
    const rafRef = useRef(0);

    const cleanup = useCallback(() => {
        cancelAnimationFrame(rafRef.current);
        abortRef.current?.abort();
        abortRef.current = null;
        const video = videoRef.current;
        if (video && video.getAttribute('src')) {
            // 先拿掉 onerror：移除 src 本身也會觸發 error 事件
            video.onerror = null;
            video.pause();
            video.removeAttribute('src');
            video.load();
        }
        if (urlRef.current) URL.revokeObjectURL(urlRef.current);
        urlRef.current = null;
    }, [videoRef]);

    const follow = useCallback((res: AnalyzeResult) => {
        let lastIdx = -2;
        let lastSign = -2;
        const tick = () => {
            const video = videoRef.current;
            if (!video) return;
            const time = video.currentTime;
            const idx = frameAt(res.track, time);
            if (idx !== lastIdx) {
                lastIdx = idx;
                const f = res.track[idx];
                setFrame(f ? { type: 'frame', hands: f.hands, active: f.active, mp_ms: 0, points: f.points } : null);
            }
            const s = res.signs.findIndex((x) => x.start <= time && time <= x.end);
            if (s !== lastSign) {
                lastSign = s;
                setCurrentSign(s);
            }
            rafRef.current = requestAnimationFrame(tick);
        };
        rafRef.current = requestAnimationFrame(tick);
    }, [videoRef]);

    const start = useCallback(async (file: File) => {
        cleanup();
        setError('');
        setResult(null);
        setFrame(null);
        setCurrentSign(-1);
        setStatus('analyzing');
        const video = videoRef.current;
        if (!video) return;
        urlRef.current = URL.createObjectURL(file);
        video.onerror = () => setError('瀏覽器無法播放這個格式，只能看文字結果（建議 H.264 的 mp4）');
        video.src = urlRef.current;
        video.loop = true;

        const abort = new AbortController();
        abortRef.current = abort;
        try {
            const res = await analyzeVideo(file, abort.signal);
            if (abortRef.current !== abort) return;
            setResult(res);
            setStatus('ready');
            follow(res);
            await video.play().catch(() => undefined);
        } catch (err) {
            if (abort.signal.aborted) return;
            cleanup();
            setStatus('error');
            setError(`分析失敗：${err instanceof Error ? err.message : String(err)}`);
        }
    }, [cleanup, follow, videoRef]);

    const stop = useCallback(() => {
        cleanup();
        setStatus('idle');
        setFrame(null);
        setCurrentSign(-1);
    }, [cleanup]);

    const clear = useCallback(() => {
        setResult(null);
        setCurrentSign(-1);
    }, []);

    useEffect(() => cleanup, [cleanup]);

    return { status, error, result, frame, currentSign, start, stop, clear };
}
