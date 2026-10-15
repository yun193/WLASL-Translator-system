import type { Point } from './protocol';

// 點的排列和 ml/wlasl/landmarks.py 相同：上半身 13 點、左手 21 點、右手 21 點
const N_POSE = 13;
const N_HAND = 21;
const LEFT = N_POSE;
const RIGHT = N_POSE + N_HAND;

// POSE_IDX 內的位置：0 鼻、1/2 眼、3/4 耳、5/6 嘴角、7/8 肩、9/10 肘、11/12 腕
const POSE_EDGES: [number, number][] = [
    [0, 1], [1, 3], [0, 2], [2, 4], [5, 6],
    [7, 8], [7, 9], [9, 11], [8, 10], [10, 12],
];

const HAND_EDGES: [number, number][] = [
    [0, 1], [1, 2], [2, 3], [3, 4],
    [0, 5], [5, 6], [6, 7], [7, 8],
    [5, 9], [9, 10], [10, 11], [11, 12],
    [9, 13], [13, 14], [14, 15], [15, 16],
    [13, 17], [0, 17], [17, 18], [18, 19], [19, 20],
];

function drawPart(ctx: CanvasRenderingContext2D, pts: Point[], offset: number, n: number,
    edges: [number, number][], color: string, w: number, h: number) {
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.beginPath();
    for (const [a, b] of edges) {
        const p = pts[offset + a];
        const q = pts[offset + b];
        if (!p || !q) continue;
        ctx.moveTo(p[0] * w, p[1] * h);
        ctx.lineTo(q[0] * w, q[1] * h);
    }
    ctx.stroke();
    for (let i = 0; i < n; i++) {
        const p = pts[offset + i];
        if (!p) continue;
        ctx.beginPath();
        ctx.arc(p[0] * w, p[1] * h, 3, 0, Math.PI * 2);
        ctx.fill();
    }
}

/** 在 canvas 上畫骨架；座標是原始（未鏡像）影像的 0～1，鏡像交給 CSS */
export function drawSkeleton(canvas: HTMLCanvasElement, points: Point[] | null) {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const { width: w, height: h } = canvas;
    ctx.clearRect(0, 0, w, h);
    if (!points) return;
    ctx.lineWidth = Math.max(2, w / 320);
    drawPart(ctx, points, 0, N_POSE, POSE_EDGES, 'rgba(255,255,255,0.85)', w, h);
    drawPart(ctx, points, LEFT, N_HAND, HAND_EDGES, 'rgba(34,197,94,0.95)', w, h);
    drawPart(ctx, points, RIGHT, N_HAND, HAND_EDGES, 'rgba(59,130,246,0.95)', w, h);
}
