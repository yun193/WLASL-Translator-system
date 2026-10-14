# WLASL-Translator-system

用前鏡頭比出手語，畫面即時顯示對應的英文詞（gloss），例如比出 "Hello" 就顯示 `HELLO`；連續比多個詞則串成 `HELLO ME NAME`。

學習目標：連續影像如何快速辨識（骨架關鍵點 + 輕量時序模型 + 即時切詞）。

資料集：[WLASL-processed（Kaggle）](https://www.kaggle.com/datasets/risangbaskoro/wlasl-processed)

## 架構決策（2026-10-14 定案）

| 項目 | 決定 | 理由 |
| --- | --- | --- |
| 辨識路線 | MediaPipe 骨架關鍵點 + 輕量 Transformer / GRU | 即時推論快，資料量小也比較穩 |
| 詞彙量 | 先做 WLASL100，流程打通後再擴充到 WLASL300 | WLASL2000 學術界 top-1 只有三到五成，即時使用會錯得太多 |
| 句子輸出 | 先輸出 gloss 串；LLM 改寫成通順英文留到之後 | WLASL 只有單字標註；ASL 語序和英文不同 |
| 關鍵點擷取 | 後端 Python MediaPipe，瀏覽器只送影格 | 和 Kaggle 訓練用同一套程式，前處理保證一致 |
| 訓練 | 只在 Kaggle：CPU 做前處理，2×T4 用 `torchrun` DDP 訓練 | 本機不訓練 |
| 本機 GPU | 只負責推論：分類模型匯出 ONNX，用 `onnxruntime-gpu`（CUDA） | Windows 上 Python 版 MediaPipe 沒有 GPU delegate，所以關鍵點擷取在 CPU 跑 |
| 程式碼送上 Kaggle | `kaggle` CLI 把 `ml/` 推成 Kaggle Dataset，notebook 掛載後 `pip install` | repo 是 private，Kaggle 不能直接 clone，也不把 GitHub 憑證放到雲端 |
| 前端風格 | 沿用 `side-project_VC/tools`：React 18 + Vite + Tailwind 3 + lucide-react | |
| 後端 | 沿用 `tools`：FastAPI + uv，只綁 `127.0.0.1`，`start.ps1` 一鍵啟動 | |

## 檔案結構

```
WLASL-Translator-system/
├─ ml/                         # 共用 Python 套件：Kaggle 與本機後端都 import
│  ├─ pyproject.toml
│  ├─ wlasl/
│  │  ├─ landmarks.py          # MediaPipe 擷取 + 正規化（訓練與推論的唯一來源）
│  │  ├─ dataset.py            # 讀關鍵點 .npy、切 WLASL100 / 300 split
│  │  ├─ augment.py            # 鏡像（前鏡頭）、時間縮放、抖動
│  │  ├─ model.py              # 輕量時序模型
│  │  ├─ train.py              # DDP 進入點（torchrun）
│  │  └─ export.py             # 匯出 ONNX + labels.json
│  └─ tests/
├─ kaggle/                     # 只是殼，邏輯都在 ml/
│  ├─ 01_preprocess.ipynb      # CPU：影片 → 關鍵點 .npy → 存成 Kaggle Dataset
│  ├─ 02_train.ipynb           # 2×T4：torchrun 呼叫 wlasl.train
│  └─ 03_evaluate_export.ipynb # 混淆矩陣、top-k、輸出 ONNX
├─ backend/                    # FastAPI
│  ├─ app/
│  │  ├─ main.py  config.py  security.py  applog.py
│  │  ├─ stream.py             # WebSocket 接收影格
│  │  ├─ segmenter.py          # 切詞：滑動視窗 + 手部靜止偵測
│  │  └─ inference.py          # onnxruntime-gpu 推論
│  └─ tests/
├─ frontend/                   # React + Vite + Tailwind
│  └─ src/
│     ├─ pages/LiveTranslate.tsx
│     ├─ components/CameraView.tsx
│     └─ hooks/useSignStream.ts
├─ scripts/
│  ├─ kaggle_push_code.ps1     # ml/ → Kaggle Dataset
│  └─ kaggle_pull_model.ps1    # 下載 ONNX + labels.json 到 models/
├─ models/  data/  logs/       # 不進 git
├─ .claude/statusline.js       # 讀 Obsidian todo-list.md 算進度
└─ start.ps1
```

## 資料流

```
[Kaggle CPU]  WLASL 影片 ──MediaPipe──▶ 關鍵點 .npy
[Kaggle 2×T4] 關鍵點 ──torchrun DDP──▶ 模型 ──▶ model.onnx + labels.json
[本機]        前鏡頭影格 ─WebSocket─▶ MediaPipe(CPU) ─▶ 切詞 ─▶ ONNX(GPU) ─▶ gloss 串 ─▶ 畫面
```
