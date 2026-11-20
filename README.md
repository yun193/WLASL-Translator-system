# WLASL Translator

> 對著電腦鏡頭比美國手語（ASL），畫面即時顯示對應的英文詞（gloss）。

比出 "Hello" 就顯示 `HELLO`；連續比多個詞則串成 `HELLO ME NAME`。支援 **2,000 個單字**，全程在本機 CPU 上即時執行，不需上傳到雲端。

```
前鏡頭 ──▶ MediaPipe 骨架關鍵點 ──▶ 自動切詞 ──▶ 輕量 Transformer ──▶ HELLO  ME  NAME
```

---

## 特色

- **即時辨識**：瀏覽器送影格、本機後端回字幕，約 10–15 fps，單次往返 30–90 ms。
- **2,000 詞詞彙表**：在 WLASL2000＋ASL Citizen 上訓練，詞彙表可在畫面上瀏覽。
- **看示範影片**：點詞彙表中的任一詞，就播放該詞的真人示範（可「換一支」看不同人比）。
- **影片檔分析**：上傳影片逐幀分析，同一支影片每次結果相同，播放時同步標亮目前的詞。
- **寧缺勿錯**：信心不足的詞不顯示或以灰字 `?` 標示；門檻依「顯示出來的詞 ≥ 90% 正確」調整。
- **全 CPU 推論**：分類器單次 ≈ 1 ms；不需要獨立顯示卡。

## 成效

驗收資料是 **模型完全沒見過的手語者**（ASL Citizen test，5 位、6,426 支單字影片，家用鏡頭拍攝）：

| 指標 | 數值 |
| --- | --- |
| 單字 top-1／top-5 | **82.9%**／95.8% |
| 顯示出來的詞正確率 | **91.8%** |
| 第一個詞就正確 | 73.1% |
| 不輸出（信心不足） | 20.3% |

常見錯誤多半是 ASL 本身就相近的手勢或同義詞，例如 brave↔health、hug↔love、murder↔kill。

### 已知限制（請先看這裡）

- **只做單字，不做連續句子**：在 39 分鐘的 ASL podcast 與 YouTube vlog 上測試，連續對話的切詞與辨識都還接近失效（精確率約 4%）。目前適合「一次比一個詞、比完放下手」的用法。
- **鏡頭角度**：上線模型以正面訓練，偏 15° 以上準確率明顯下降；已有角度增強版（偏 45° 仍有 ~75%），尚未換上線。
- **輸出是 gloss 串**：ASL 語序與英文不同，目前不改寫成通順英文。

詳細數據與實驗紀錄見 [`docs/`](#實驗報告)。

---

## 系統架構

```
[Kaggle CPU]   WLASL / ASL Citizen 影片 ──MediaPipe──▶ 關鍵點 .npy
[Kaggle GPU]   關鍵點 ──PyTorch 訓練──▶ model.onnx + labels.json
                      （全部由本機 kaggle CLI 觸發與拉取）
[本機驗證]     model.onnx + 測試關鍵點 ──onnxruntime──▶ top-k、混淆矩陣、延遲、換人準確率
[本機服務]     前鏡頭影格 ─WebSocket─▶ MediaPipe ─▶ 切詞 ─▶ ONNX 分類 ─▶ 字幕
```

| 層 | 技術 |
| --- | --- |
| 關鍵點 | MediaPipe `HolisticLandmarker`（Tasks API）：每幀上半身 13 點＋雙手各 21 點 |
| 模型 | 輕量時序 Transformer；肩膀中點正規化、慣用手統一（左撇子鏡像成右手）、手部局部座標 |
| 切詞 | 手放下 0.5 秒切詞、超過 4 秒強制切；另有「不是詞」背景類模型過濾雜訊 |
| 後端 | Python 3.12、FastAPI、uv、onnxruntime（CPU）；只綁 `127.0.0.1` |
| 前端 | React 18、Vite、Tailwind CSS、lucide-react |
| 訓練 | Kaggle Notebook（PyTorch）→ 匯出 ONNX；本機不需安裝 torch |

**為什麼關鍵點在後端擷取？** 訓練與推論共用同一份 `ml/wlasl/landmarks.py`，前處理保證一致；本機與 Kaggle 擷取同一支影片，80% 逐位元相同。

---

## 快速開始

### 需求

- Windows 10/11（`start.ps1` 為 PowerShell；後端本身跨平台）
- Python 3.12＋[uv](https://docs.astral.sh/uv/)
- Node.js 18+
- 網路攝影機
- （選用）[Kaggle CLI](https://github.com/Kaggle/kaggle-api) 與帳號憑證：用於下載示範影片、重新訓練

### 1. 取得模型

模型權重**不在 repo 內**（見[授權](#資料與授權)）。可自行訓練，或將已有的模型放到：

```
models/<run 名稱>/model.onnx
models/<run 名稱>/labels.json
models/<run 名稱>/serving.json   # 選用：顯示門檻
```

從 Kaggle 訓練 notebook 拉取：

```powershell
.\scripts\kaggle_pull_model.ps1 -Run <run 名稱>
```

後端預設使用 `models/` 下最新的一版，也可用環境變數 `WLASL_MODEL_DIR` 指定。

### 2. 啟動

```powershell
.\start.ps1
```

首次會自動 `npm install` 與建置前端，接著啟動 <http://127.0.0.1:8766> 並開啟瀏覽器。加上 `-NoBrowser` 則不開瀏覽器。

### 3. 使用

1. 按「開啟鏡頭」，上半身與雙手入鏡。
2. 比一個詞，比完把手放下 —— 0.5 秒後字幕出現；也可按「結束這個詞」立刻送出。
3. 想知道某個詞怎麼比？在詞彙表點它看示範影片。

### 開發模式

```powershell
cd backend; $env:WLASL_DEV=1; uv run python -m app
```

```powershell
cd frontend; npm run dev
```

Vite（5173）會代理 `/api` 與 `/ws` 到後端。

---

## 訓練與驗證

所有訓練都在 Kaggle 上執行，由本機腳本驅動：

| 步驟 | 腳本 |
| --- | --- |
| 把 `ml/` 程式碼推成 Kaggle Dataset | `scripts/kaggle_push_code.ps1` |
| 分片前處理（影片 → 關鍵點） | `scripts/kaggle_preprocess_shards.ps1` |
| 推送 notebook、輪詢狀態、拉 log | `scripts/kaggle_run.ps1` |
| 下載 ONNX 與參考 logits | `scripts/kaggle_pull_model.ps1` |
| 本機驗證（測試集指標、ONNX 與 PyTorch 一致性） | `scripts/validate.ps1` |
| 後端端到端評估（含幀率、抽幀相位穩定度） | `scripts/eval_backend_model.ps1` |
| 換人、角度、詞彙表外、長影片等基準測試 | `scripts/*bench.py` |

單元測試：

```powershell
cd ml; uv run pytest
```

```powershell
cd backend; uv run pytest
```

---

## 專案結構

```
WLASL-Translator-system/
├─ ml/          # 共用 Python 套件 wlasl：關鍵點、資料集、增強、模型、訓練、匯出、評估、切詞
├─ kaggle/      # Kaggle notebook 外殼（前處理、訓練、匯出、交叉驗證），邏輯都在 ml/
├─ backend/     # FastAPI：WebSocket 串流、影片分析、ONNX 推論、示範影片快取
├─ frontend/    # React 介面：鏡頭＋骨架疊圖、字幕、top-5、詞彙表
├─ scripts/     # Kaggle 驅動、驗證與各種基準測試
├─ docs/        # 實驗報告與數據
└─ start.ps1    # 一鍵啟動
```

`models/`、`data/`、`logs/` 不進版控。

## 實驗報告

| 主題 | 報告 |
| --- | --- |
| 2,000 詞版本與門檻調整 | [docs/vocab2000/report.md](docs/vocab2000/report.md) |
| 慣用手統一＋手部局部座標（目前上線） | [docs/vocab2000/h2000/report.md](docs/vocab2000/h2000/report.md) |
| 鏡頭角度增強 | [docs/vocab2000/v2000/report.md](docs/vocab2000/v2000/report.md)、[docs/viewbench/report.md](docs/viewbench/report.md) |
| 分部位 GCN 編碼器（未採用） | [docs/vocab2000/p2000/report.md](docs/vocab2000/p2000/report.md) |
| 加入 ASL Citizen 訓練 | [docs/asl-citizen/a2000/report.md](docs/asl-citizen/a2000/report.md) |
| 依手語者交叉驗證 | [docs/signer-cv/report.md](docs/signer-cv/report.md) |
| 詞彙表外亂認、窗口偵測門檻 | [docs/open-set/report.md](docs/open-set/report.md)、[docs/spot-gate/report.md](docs/spot-gate/report.md) |
| YouTube 影片泛化 | [docs/yt-generalization/report.md](docs/yt-generalization/report.md) |
| 39 分鐘 podcast 長對話測試 | [docs/podcast-ep3/report.md](docs/podcast-ep3/report.md) |
| 文獻與下一步評估 | [docs/research/islr-sota.md](docs/research/islr-sota.md)、[docs/next-step-eval/report.md](docs/next-step-eval/report.md) |

## 資料與授權

- **WLASL**：[Li et al., WACV 2020](https://dxli94.github.io/WLASL/)；本專案使用 Kaggle 上的 [WLASL-processed](https://www.kaggle.com/datasets/risangbaskoro/wlasl-processed)。僅供學術研究。
- **ASL Citizen**：[Desai et al., NeurIPS 2023](https://www.microsoft.com/en-us/research/project/asl-citizen/)，Microsoft Research License，**僅限非商業研究**。

上線模型混有 ASL Citizen 訓練資料，因此**模型權重不公開、不得商用**；本 repo 只包含程式碼與實驗數據。

## 致謝

[MediaPipe](https://ai.google.dev/edge/mediapipe)、WLASL 與 ASL Citizen 的作者與參與錄製的手語者。
