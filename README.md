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
| 分工（2026-10-14 補充） | **Kaggle**：前處理 → 訓練 → 匯出 ONNX；**本機**：只做訓練後驗證（離線測試集指標 + 即時鏡頭實測） | 本機只有 RTX 3050 Ti 4GB，不跑前處理和訓練；本機不裝 torch |
| 訓練 | Kaggle：CPU 做前處理，2×T4 用 `torchrun` DDP 訓練，訓練結束直接匯出 ONNX | 匯出是訓練產出的一部分，留在有 torch 的環境 |
| 驗證 | 本機用 `onnxruntime-gpu` 跑**實際要部署的 ONNX**：top-1 / top-5、混淆矩陣、每類準確率、推論延遲，以及和 Kaggle 端 PyTorch logits 的一致性比對 | 驗的就是上線那一份模型，不是訓練框架裡的另一份 |
| Kaggle 操作 | 全部用 `kaggle` CLI 從本機驅動：`datasets version` 推程式碼、`kernels push` 跑 notebook、`kernels status` 查進度、`kernels output` 拉產出 | 不用手動開網頁，流程可重跑 |
| 本機 GPU | 只負責推論與驗證：分類模型匯出 ONNX，用 `onnxruntime-gpu`（CUDA） | Windows 上 Python 版 MediaPipe 沒有 GPU delegate，所以關鍵點擷取在 CPU 跑 |
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
│  │  ├─ train.py              # DDP 進入點（torchrun）［Kaggle］
│  │  ├─ export.py             # 匯出 ONNX + labels.json + 參考 logits［Kaggle］
│  │  └─ evaluate.py           # ONNX 測試集指標、混淆矩陣、延遲、logits 比對［本機］
│  └─ tests/
├─ kaggle/                     # 只是殼，邏輯都在 ml/；每個資料夾一份 kernel-metadata.json 給 CLI push
│  ├─ preprocess/              # CPU：影片 → 關鍵點 .npy（含 test split）
│  └─ train/                   # 2×T4：torchrun 訓練 → 匯出 model.onnx + labels.json
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
│  ├─ kaggle_push_code.ps1     # ml/ → Kaggle Dataset（datasets version）
│  ├─ kaggle_run.ps1           # kernels push → 輪詢 status → 完成後拉 log
│  ├─ kaggle_pull_model.ps1    # kernels output：ONNX + labels.json + 參考 logits → models/<run>/
│  └─ validate.ps1             # 本機驗證：下載 test 關鍵點 → wlasl.evaluate → 報告
├─ models/  data/  logs/       # 不進 git
├─ .claude/statusline.js       # 讀 Obsidian todo-list.md 算進度
└─ start.ps1
```

## 資料流

```
[Kaggle CPU]  WLASL 影片 ──MediaPipe──▶ 關鍵點 .npy
[Kaggle 2×T4] 關鍵點 ──torchrun DDP──▶ 模型 ──▶ model.onnx + labels.json + 參考 logits
                    （以上全由本機 kaggle CLI 觸發與拉取）
[本機驗證]    model.onnx + test 關鍵點 ──onnxruntime-gpu──▶ top-k / 混淆矩陣 / 延遲 / logits 一致性
[本機推論]    前鏡頭影格 ─WebSocket─▶ MediaPipe(CPU) ─▶ 切詞 ─▶ ONNX(GPU) ─▶ gloss 串 ─▶ 畫面
```
