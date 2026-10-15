import { useEffect, useRef, useState } from 'react';
import { Camera, Eraser, FileVideo, Hand, ScissorsLineDashed, ShieldCheck, Square } from 'lucide-react';
import CameraView from './components/CameraView';
import Transcript from './components/Transcript';
import Vocabulary from './components/Vocabulary';
import { useSignStream } from './hooks/useSignStream';
import { getHealth, type Health } from './lib/protocol';

const btn = 'inline-flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition disabled:opacity-40 disabled:cursor-not-allowed';

function App() {
    const [health, setHealth] = useState<Health | null>(null);
    const [healthError, setHealthError] = useState('');
    const videoRef = useRef<HTMLVideoElement>(null);
    const fileRef = useRef<HTMLInputElement>(null);
    const { status, error, frame, signs, stats, sourceKind, start, stop, flush, clear } = useSignStream(videoRef);

    useEffect(() => {
        getHealth().then(setHealth).catch((err: Error) => setHealthError(err.message));
    }, []);

    const live = status === 'running' || status === 'done' || status === 'starting';
    const ready = !!health?.model;

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            <header className="bg-white shadow z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <Hand className="text-blue-600" /> WLASL 即時手語辨識
                    </h1>
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-600">
                            {health?.model ? `模型 ${health.model}・${health.classes} 詞` : '僅限本機'}
                        </span>
                        <div
                            className={`w-3 h-3 rounded-full ${ready ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse' : 'bg-gray-300'}`}
                            title={ready ? '後端連線正常' : '後端未連線或沒有模型'}
                        />
                    </div>
                </div>
            </header>

            <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 grid gap-6 lg:grid-cols-5">
                <section className="lg:col-span-3 space-y-3">
                    <CameraView videoRef={videoRef} frame={frame} mirrored={sourceKind === 'camera'} live={live} />

                    <div className="flex flex-wrap gap-2">
                        <button className={`${btn} bg-blue-600 text-white hover:bg-blue-700`} disabled={!ready}
                            onClick={() => start({ kind: 'camera' })}>
                            <Camera className="w-4 h-4" /> 開啟鏡頭
                        </button>
                        <button className={`${btn} bg-white border border-gray-300 hover:bg-gray-50`} disabled={!ready}
                            onClick={() => fileRef.current?.click()}>
                            <FileVideo className="w-4 h-4" /> 播放影片檔
                        </button>
                        <input ref={fileRef} type="file" accept="video/*" className="hidden"
                            onChange={(e) => {
                                const file = e.target.files?.[0];
                                if (file) start({ kind: 'file', file });
                                e.target.value = '';
                            }} />
                        <button className={`${btn} bg-white border border-gray-300 hover:bg-gray-50`} disabled={!live}
                            onClick={stop}>
                            <Square className="w-4 h-4" /> 停止
                        </button>
                        <div className="flex-1" />
                        <button className={`${btn} bg-white border border-gray-300 hover:bg-gray-50`} disabled={status !== 'running'}
                            onClick={flush} title="不等手放下，立刻把目前的動作當成一個詞送去辨識">
                            <ScissorsLineDashed className="w-4 h-4" /> 結束這個詞
                        </button>
                        <button className={`${btn} bg-white border border-gray-300 hover:bg-gray-50`} disabled={signs.length === 0 && !live}
                            onClick={clear}>
                            <Eraser className="w-4 h-4" /> 清除字幕
                        </button>
                    </div>

                    {(error || healthError) && (
                        <div className="rounded-md bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700">{error || `後端未連線：${healthError}`}</div>
                    )}
                    {health && !health.model && (
                        <div className="rounded-md bg-amber-50 border border-amber-200 px-3 py-2 text-sm text-amber-800">
                            後端沒有載入模型：先執行 scripts/kaggle_pull_model.ps1
                        </div>
                    )}

                    <div className="text-xs text-gray-500 flex flex-wrap gap-x-4 gap-y-1">
                        <span>狀態：{{ idle: '待機', starting: '啟動中', running: '辨識中', done: '影片播完', error: '錯誤' }[status]}</span>
                        {live && <span className="tabular-nums">{stats.fps.toFixed(1)} fps</span>}
                        {live && <span className="tabular-nums">MediaPipe {stats.mpMs.toFixed(0)} ms</span>}
                        {live && <span className="tabular-nums">來回 {stats.rttMs.toFixed(0)} ms</span>}
                        {health && <span>手放下 {health.segmenter.rest} 秒就切成一個詞・單詞上限 {health.segmenter.max} 秒</span>}
                    </div>
                </section>

                <aside className="lg:col-span-2 space-y-6">
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                        <h2 className="text-sm font-semibold text-gray-700 mb-3">字幕（英文 gloss）</h2>
                        <Transcript signs={signs} />
                    </div>
                    {health && health.labels.length > 0 && (
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                            <h2 className="text-sm font-semibold text-gray-700 mb-3">可辨識的 {health.labels.length} 個詞</h2>
                            <Vocabulary labels={health.labels} />
                        </div>
                    )}
                </aside>
            </main>

            <footer className="text-xs text-gray-400 text-center py-4 flex items-center justify-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> 影像只送到本機 {window.location.host} 處理，不會上傳
            </footer>
        </div>
    );
}

export default App;
