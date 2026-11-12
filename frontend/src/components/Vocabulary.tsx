import { useMemo, useState } from 'react';
import { Search } from 'lucide-react';

/** 模型認得的詞（上線版 2000 詞），實測前先挑清單裡的詞 */
export default function Vocabulary({ labels }: { labels: string[] }) {
    const [query, setQuery] = useState('');
    const shown = useMemo(() => {
        const q = query.trim().toLowerCase();
        return [...labels].sort().filter((l) => l.toLowerCase().includes(q));
    }, [labels, query]);

    return (
        <div>
            <label className="relative block mb-3">
                <Search className="w-4 h-4 text-gray-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="搜尋單字"
                    className="w-full pl-8 pr-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </label>
            <div className="flex flex-wrap gap-1.5 max-h-56 overflow-y-auto">
                {shown.map((l) => (
                    <span key={l} className="px-2 py-0.5 rounded bg-gray-100 text-xs font-mono text-gray-700">{l}</span>
                ))}
                {shown.length === 0 && <span className="text-sm text-gray-400">沒有符合的詞</span>}
            </div>
        </div>
    );
}
