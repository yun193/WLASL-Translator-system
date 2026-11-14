import { FilesetResolver, HandLandmarker, PoseLandmarker, type NormalizedLandmark } from '@mediapipe/tasks-vision';
import type { Point } from './protocol';

/**
 * 瀏覽器端 MediaPipe（走顯示卡 WebGL），只用來即時畫骨架，讓骨架跟得上鏡頭畫面。
 * 辨識仍由後端 Python Holistic 做（和訓練同一套），這裡的點不送後端。
 * 不用網頁版 Holistic：它連臉部網格和人像分割都算，實測每幀約 1 秒；改用 Pose lite + Hand 兩個輕量模型。
 * 模型檔由後端 /api/mp/ 提供（data/models/），wasm 在 /mediapipe-wasm/（建置時從 node_modules 複製）。
 */

// 和 ml/wlasl/landmarks.py 的 POSE_IDX 相同：鼻、眼、耳、嘴角、肩、肘、腕
const POSE_IDX = [0, 2, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16];

export interface Tracker { pose: PoseLandmarker; hand: HandLandmarker }

let pending: Promise<Tracker> | null = null;

async function create(delegate: 'GPU' | 'CPU'): Promise<Tracker> {
    const fileset = await FilesetResolver.forVisionTasks('/mediapipe-wasm');
    const [pose, hand] = await Promise.all([
        PoseLandmarker.createFromOptions(fileset, {
            baseOptions: { modelAssetPath: '/api/mp/pose_landmarker_lite.task', delegate }, runningMode: 'VIDEO', numPoses: 1,
        }),
        HandLandmarker.createFromOptions(fileset, {
            baseOptions: { modelAssetPath: '/api/mp/hand_landmarker.task', delegate }, runningMode: 'VIDEO', numHands: 2,
        }),
    ]);
    return { pose, hand };
}

/** 第一次呼叫才載入；顯示卡不能用就退回 CPU。 */
export function loadTracker(): Promise<Tracker> {
    pending ??= create('GPU').catch(() => create('CPU'));
    pending.catch(() => { pending = null; });
    return pending;
}

const empty = (n: number): Point[] => Array(n).fill(null);
const xy = (list: NormalizedLandmark[]): Point[] => list.map((p) => [p.x, p.y]);

/** 一幀 → 和後端 frame.points 同樣排列的 55 點（上半身 13、手 21、手 21），座標是 0～1 的畫面比例。只拿來畫，不分左右手。 */
export function track(t: Tracker, video: HTMLVideoElement, tsMs: number): Point[] {
    const pose = t.pose.detectForVideo(video, tsMs).landmarks[0];
    const hands = t.hand.detectForVideo(video, tsMs).landmarks;
    return [
        ...(pose ? POSE_IDX.map((i) => [pose[i].x, pose[i].y] as Point) : empty(13)),
        ...(hands[0] ? xy(hands[0]) : empty(21)),
        ...(hands[1] ? xy(hands[1]) : empty(21)),
    ];
}
