// 把 MediaPipe 網頁版的 wasm 從 node_modules 複製到 public/mediapipe-wasm（不進 git，建置／開發前自動執行）
import { cpSync, mkdirSync } from 'node:fs';
const src = 'node_modules/@mediapipe/tasks-vision/wasm';
const dst = 'public/mediapipe-wasm';
mkdirSync(dst, { recursive: true });
for (const f of ['vision_wasm_internal.js', 'vision_wasm_internal.wasm', 'vision_wasm_nosimd_internal.js', 'vision_wasm_nosimd_internal.wasm']) {
    cpSync(`${src}/${f}`, `${dst}/${f}`);
}
