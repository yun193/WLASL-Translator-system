// 和 backend/app/stream.py 的協定一一對應

export type Point = [number, number] | null;

export interface FrameEvent {
    type: 'frame';
    hands: [boolean, boolean];
    active: boolean;
    mp_ms: number;
    /** 55 點，0～1 影像座標（未鏡像）；偵測不到為 null */
    points: Point[];
}

export interface SignEvent {
    type: 'sign';
    gloss: string;
    prob: number;
    confident: boolean;
    top5: { gloss: string; prob: number }[];
    frames: number;
    infer_ms: number;
}

export type ServerEvent = FrameEvent | SignEvent | { type: 'error'; detail: string } | { type: 'reset' };

export interface Health {
    model: string | null;
    classes: number;
    labels: string[];
    mediapipe_model: boolean;
    segmenter: { rest: number; min: number; max: number };
    min_confidence: number;
}

/** 前 8 bytes 是 little-endian float64 的擷取時間（ms），後面接 JPEG */
export function packFrame(tsMs: number, jpeg: ArrayBuffer): ArrayBuffer {
    const out = new Uint8Array(8 + jpeg.byteLength);
    new DataView(out.buffer).setFloat64(0, tsMs, true);
    out.set(new Uint8Array(jpeg), 8);
    return out.buffer;
}

export const CLOSE_REASONS: Record<number, string> = {
    1008: '連線被拒：來源不在允許清單（開發模式請用 WLASL_DEV=1 啟動後端）',
    1011: '後端沒有載入模型：先執行 scripts/kaggle_pull_model.ps1',
    1013: '已有另一個分頁在使用辨識，請先關閉它',
};

export async function getHealth(): Promise<Health> {
    const res = await fetch('/api/health');
    if (!res.ok) throw new Error(`後端回應 ${res.status}`);
    return res.json();
}
