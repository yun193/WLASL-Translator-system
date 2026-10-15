import { useEffect, useRef } from 'react';
import type { SignEvent } from '../lib/protocol';

function pct(p: number) {
    return `${Math.round(p * 100)}%`;
}

/** 字幕串：有把握的詞正常顯示，低於門檻的灰字加問號（仍保留，方便看模型猜了什麼） */
/** highlight：影片檔播放中、目前時間落在哪個詞（-1 表示沒有） */
export default function Transcript({ signs, highlight = -1, showTime = false }: { signs: SignEvent[]; highlight?: number; showTime?: boolean }) {
    const endRef = useRef<HTMLDivElement>(null);
    // 要用大括號：新版 Chrome 的 scrollIntoView 回傳 Promise，直接回傳會被 React 當成 cleanup 呼叫而崩潰
    useEffect(() => {
        endRef.current?.scrollIntoView({ block: 'nearest' });
    }, [signs.length]);
    const last = signs[highlight >= 0 ? highlight : signs.length - 1];

    return (
        <div className="space-y-4">
            {/* flex-wrap：詞與詞之間沒有空白字元，用一般 inline 排版不會換行 */}
            <div className="min-h-[96px] max-h-48 overflow-y-auto rounded-lg bg-gray-900 px-4 py-3 font-mono text-2xl leading-relaxed tracking-wide flex flex-wrap content-start gap-x-3">
                {signs.length === 0 ? (
                    <span className="text-gray-500 text-base font-sans">辨識到的詞會出現在這裡</span>
                ) : (
                    signs.map((s, i) => (
                        <span key={i}
                            className={`${s.confident ? 'text-white' : 'text-gray-500 italic'} ${i === highlight ? 'bg-blue-600/60 rounded px-1 -mx-1' : ''}`}
                            title={`${s.gloss} ${pct(s.prob)}（${s.frames} 幀${showTime ? `，${s.start.toFixed(2)}–${s.end.toFixed(2)} 秒` : ''}）`}>
                            {s.gloss}{s.confident ? '' : '?'}
                        </span>
                    ))
                )}
                <div ref={endRef} />
            </div>

            {last && (
                <div>
                    <div className="text-xs font-medium text-gray-500 mb-2">
                        {highlight >= 0 ? '播放中這個詞' : '最近一個詞'}的前 5 名（{last.frames} 幀
                        {showTime ? `，${last.start.toFixed(2)}–${last.end.toFixed(2)} 秒` : `，分類 ${last.infer_ms} ms`}）
                    </div>
                    <ul className="space-y-1.5">
                        {last.top5.map((t, i) => (
                            <li key={t.gloss} className="flex items-center gap-2 text-sm">
                                <span className={`w-28 truncate font-mono ${i === 0 ? 'font-semibold' : 'text-gray-600'}`}>{t.gloss}</span>
                                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                                    <div className={`h-full rounded-full ${i === 0 ? 'bg-blue-600' : 'bg-blue-300'}`}
                                        style={{ width: pct(t.prob) }} />
                                </div>
                                <span className="w-10 text-right tabular-nums text-gray-500">{pct(t.prob)}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
