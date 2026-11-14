import { useEffect, useMemo, useRef, useState } from 'react';
import { Loader2, Search, SkipForward, X } from 'lucide-react';

type DemoItem = { index: number; start: number; end: number | null };

/** 模型認得的詞（上線版 2000 詞）；點一個詞，下方播放它的示範影片（後端點詞時才從 Kaggle 抓） */
export default function Vocabulary({ labels }: { labels: string[] }) {
    const [query, setQuery] = useState('');
    const [selected, setSelected] = useState<string | null>(null);
    const shown = useMemo(() => {
        const q = query.trim().toLowerCase();
        return [...labels].filter((l) => l !== '_bg').sort().filter((l) => l.toLowerCase().includes(q));
    }, [labels, query]);

    return (
        <div>
            <label className="relative block mb-3">
                <Search className="w-4 h-4 text-gray-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="搜尋單字，點一下看示範"
                    className="w-full pl-8 pr-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </label>
            <div className="flex flex-wrap gap-1.5 max-h-56 overflow-y-auto">
                {shown.map((l) => (
                    <button key={l} type="button" onClick={() => setSelected(l === selected ? null : l)}
                        className={`px-2 py-0.5 rounded text-xs font-mono ${l === selected ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-blue-50'}`}>
                        {l}
                    </button>
                ))}
                {shown.length === 0 && <span className="text-sm text-gray-400">沒有符合的詞</span>}
            </div>
            {selected && <DemoPlayer key={selected} gloss={selected} onClose={() => setSelected(null)} />}
        </div>
    );
}

function DemoPlayer({ gloss, onClose }: { gloss: string; onClose: () => void }) {
    const [items, setItems] = useState<DemoItem[]>([]);
    const [i, setI] = useState(0);
    const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading');
    const [error, setError] = useState('');
    const video = useRef<HTMLVideoElement>(null);
    const item = items[i];

    useEffect(() => {
        fetch(`/api/demo/${encodeURIComponent(gloss)}`)
            .then(async (r) => (r.ok ? r.json() : Promise.reject(new Error((await r.json()).detail))))
            .then((d) => setItems(d.items))
            .catch((e) => {
                setState('error');
                // fetch 本身失敗（TypeError）＝連不到後端，不是 Kaggle 的問題
                setError(e instanceof TypeError ? '連不到後端：請確認 start.ps1 的視窗還開著' : String(e.message || e));
            });
    }, [gloss]);

    // 只播這個詞的片段（有些原始影片前後還有別的內容），播完從起點重播
    const onTime = () => {
        const v = video.current;
        if (v && item && ((item.end !== null && v.currentTime >= item.end) || v.currentTime < item.start - 0.05)) {
            v.currentTime = item.start;
        }
    };

    return (
        <div className="mt-3 border border-gray-200 rounded-md p-3">
            <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold font-mono text-gray-800">{gloss}</span>
                <div className="flex items-center gap-2">
                    {items.length > 1 && (
                        <button type="button" onClick={() => { setState('loading'); setI((i + 1) % items.length); }}
                            className="flex items-center gap-1 text-xs text-blue-600 hover:underline">
                            <SkipForward className="w-3.5 h-3.5" />換一支（{i + 1}/{items.length}）
                        </button>
                    )}
                    <button type="button" onClick={onClose} aria-label="關閉示範" className="text-gray-400 hover:text-gray-600">
                        <X className="w-4 h-4" />
                    </button>
                </div>
            </div>
            {state === 'loading' && (
                <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />第一次看這支要從 Kaggle 下載，約數秒
                </div>
            )}
            {state === 'error' && <p className="text-xs text-red-600 mb-2">{error || '示範影片載入失敗'}</p>}
            {item && (
                <video ref={video} key={item.index} src={`/api/demo/${encodeURIComponent(gloss)}/${item.index}`}
                    className={`w-full max-h-72 rounded bg-black ${state === 'ready' ? '' : 'hidden'}`}
                    autoPlay muted loop playsInline controls
                    onLoadedMetadata={(e) => { e.currentTarget.currentTime = item.start; }}
                    onCanPlay={() => setState('ready')} onTimeUpdate={onTime}
                    onError={() => { setState('error'); setError('無法從 Kaggle 取得影片（網路或 Kaggle 登入有問題）'); }} />
            )}
            <p className="text-[11px] text-gray-400 mt-1">影片來源：WLASL（僅供個人研究測試）</p>
        </div>
    );
}
