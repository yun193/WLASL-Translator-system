# WLASL-Translator-system

用前鏡頭比出手語，畫面即時顯示對應的英文詞（gloss），例如比出 "Hello" 就顯示 `HELLO`；連續比多個詞則串成 `HELLO ME NAME`。

學習目標：連續影像如何快速辨識（骨架關鍵點 + 輕量時序模型 + 即時切詞）。

資料集：[WLASL-processed（Kaggle）](https://www.kaggle.com/datasets/risangbaskoro/wlasl-processed)

## 架構決策（2026-10-14 定案）

| 項目 | 決定 | 理由 |
| --- | --- | --- |
| 辨識路線 | MediaPipe 骨架關鍵點 + 輕量 Transformer / GRU | 即時推論快，資料量小也比較穩 |
| 詞彙量 | 先做 WLASL100；**2026-11-13 起上線 2000 詞**（`docs/vocab2000/report.md`）；2026-11-14 換成 h2000（慣用手統一＋手部局部座標，`docs/vocab2000/h2000/report.md`） | 加入 ASL Citizen 後，新使用者單字 top-1 從 WLASL2000 的四到五成提升到 81%；門檻依手語者對半調到「顯示的詞 ≥90% 正確」 |
| 句子輸出 | 先輸出 gloss 串；LLM 改寫成通順英文留到之後 | WLASL 只有單字標註；ASL 語序和英文不同 |
| 關鍵點擷取 | 後端 Python MediaPipe，瀏覽器只送影格 | 和 Kaggle 訓練用同一套程式，前處理保證一致 |
| 分工（2026-10-14 補充） | **Kaggle**：前處理 → 訓練 → 匯出 ONNX；**本機**：只做訓練後驗證（離線測試集指標 + 即時鏡頭實測） | 本機只有 RTX 3050 Ti 4GB，不跑前處理和訓練；本機不裝 torch |
| 訓練 | Kaggle：CPU 做前處理，2×T4 用 `torchrun` DDP 訓練，訓練結束直接匯出 ONNX | 匯出是訓練產出的一部分，留在有 torch 的環境 |
| 驗證 | 本機用 `onnxruntime-gpu` 跑**實際要部署的 ONNX**：top-1 / top-5、混淆矩陣、每類準確率、推論延遲，以及和 Kaggle 端 PyTorch logits 的一致性比對 | 驗的就是上線那一份模型，不是訓練框架裡的另一份 |
| Kaggle 操作 | 全部用 `kaggle` CLI 從本機驅動：`datasets version` 推程式碼、`kernels push` 跑 notebook、`kernels status` 查進度、`kernels output` 拉產出 | 不用手動開網頁，流程可重跑 |
| 即時推論（2026-10-15 改） | **全部 CPU**：MediaPipe 與分類器都在 CPU；後端只裝 `onnxruntime`（CPU 版） | 實測分類器 batch 1：CPU 1.16 ms、CUDA 1.57 ms，模型太小 GPU 反而慢；瓶頸是 MediaPipe 約 95 ms/幀（佔 99%），Windows 上 MediaPipe 也沒有 GPU delegate |
| 本機 GPU | 只在驗證時用（`ml` 的 `eval` extra：`onnxruntime-gpu==1.26.0`，CUDA EP 關 TF32） | 1.27 起 CUDA 13 套件沒有 Windows wheel；TF32 會讓 logits 差到 7e-3 |
| 程式碼送上 Kaggle | `kaggle` CLI 把 `ml/` 推成 Kaggle Dataset，notebook 掛載後 `pip install` | repo 是 private，Kaggle 不能直接 clone，也不把 GitHub 憑證放到雲端 |
| 前端風格 | 沿用 `side-project_VC/tools`：React 18 + Vite + Tailwind 3 + lucide-react | |
| 後端 | 沿用 `tools`：FastAPI + uv，只綁 `127.0.0.1`，`start.ps1` 一鍵啟動 | |

## 資料現況（2026-10-14 實測）

Kaggle `wlasl-processed` 只有 11980 支影片，WLASL100 的 2038 支中只存在 **1013 支**（缺的剛好是 `missing.txt` 列的那些）：

| split | 影片數 | 涵蓋類別 | 每類支數 |
| --- | --- | --- | --- |
| train | 748 | 100 | 4–12 |
| val | 165 | 89 | 1–4 |
| test | 100 | 72 | 1–3 |

test 只有 100 支，top-1 的 95% 信賴區間約 ±10 個百分點；本機驗證報告須一併標註，不能只看單一數字。

## 關鍵點擷取（2026-10-14 實測）

- mediapipe 鎖定 `1.1.0`：舊版 `mp.solutions` 已移除，只能用 Tasks API。
- 採用 `HolisticLandmarker`：本機 CPU 約 95 ms/幀；Pose + Hand 分開跑反而約 105–135 ms，而且分不出左右手。
- 每幀 55 點 × (x, y, z)：上半身姿勢 13 點 + 左手 21 + 右手 21；x 乘上寬高比，缺點填 NaN。
- `.npy` 存原始座標，正規化（肩膀中點為原點、肩寬為單位）在讀取時做。

## 即時串流（2026-10-15 實測）

`scripts/bench_mediapipe.py`，test 100 支，本機 CPU：

| 取樣 | test top-1 | top-5 | 平均幀數 |
| --- | --- | --- | --- |
| 全幀 | 70% | 87% | 60 |
| 15 fps | 70% | 89% | 32 |
| 10 fps | 70% | 88% | 21 |
| 7.5 fps | 70% | 87% | 16 |

- 每幀擷取延遲（720p 影片）：原尺寸 113 ms、480p 74 ms、360p 80 ms → 前端送 **640×480 JPEG**。
- 本機與 Kaggle 擷取同一支影片：80/100 支逐位元相同，其餘 20 支只差在門檻邊緣的手部偵測，準確率 70% vs 71%。
- 協定：前端送 `float64 時間戳(ms) + JPEG`，後端回 `frame`（手部狀態、骨架點），切出詞時多回一則 `sign`；前端收到回覆才送下一幀（一來一回 = 背壓，不會堆積延遲）。
- 安全：WebSocket 握手不經過 HTTP middleware，`/ws/stream` 在 accept 前另外檢查 Host 與 Origin（Origin 必填）；同時只允許一條串流。
- 切詞 v1：手出現就開始、手消失 0.5 秒切詞、超過 4 秒強制切；連續比劃不放手時只能靠強制切，之後可改用手速低谷切詞。

## 使用方式

```powershell
.\start.ps1              # 缺前端建置或原始碼有更新會先 npm build，再啟動 http://127.0.0.1:8766 並開瀏覽器
.\start.ps1 -NoBrowser
```

- 「開啟鏡頭」：前鏡頭畫面鏡像顯示（像照鏡子），送給後端的影格不翻轉（訓練資料沒翻轉，左右手差異已由鏡像增強處理）。
- 「分析影片檔」：影片上傳給後端 `POST /api/analyze`，cv2 以原生 fps 逐幀解碼分析（和 Kaggle 前處理同一路徑），同一支影片每次結果相同；播放時依時間戳同步骨架並標亮目前的詞。
  即時串流只能取到 10～15 fps，每次抽到的幀不同：10 fps 下 20% 影片會隨抽幀相位翻盤（15 fps 為 6%），所以影片檔不走串流。
- 手放下 0.5 秒自動切詞；「結束這個詞」不等手放下立刻送出；信心低於 0.3 的詞以灰字加 `?` 顯示。
- 後端啟動時關閉 Windows EcoQoS：主控台變背景視窗後 CPU 會被節流到 1/6（MediaPipe 25 → 170 ms/幀）。
- 開發模式：後端 `WLASL_DEV=1 uv run python -m app`，前端 `npm run dev`（Vite 5173 代理 `/api`、`/ws`）。

端到端實測（2026-10-15，headless Chrome 假鏡頭餵 test 影片 birthday → candy → change 循環）：鏡頭與影片檔兩條路徑都切出 `birthday candy change`，約 10–13 fps、來回 30–90 ms。

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
│  │  └─ inference.py          # onnxruntime（CPU）推論
│  └─ tests/
├─ frontend/                   # React + Vite + Tailwind
│  └─ src/
│     ├─ App.tsx               # 版面：影像 + 控制列 + 字幕 + 詞彙表
│     ├─ components/           # CameraView（骨架疊圖）、Transcript（字幕 + top-5）、Vocabulary
│     ├─ hooks/useSignStream.ts# 鏡頭/影片檔 → 一來一回 WebSocket → 字幕
│     └─ lib/                  # protocol.ts（和 stream.py 對應）、skeleton.ts
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
[本機推論]    前鏡頭影格 ─WebSocket─▶ MediaPipe(CPU) ─▶ 切詞 ─▶ ONNX(CPU) ─▶ gloss 串 ─▶ 畫面
```
