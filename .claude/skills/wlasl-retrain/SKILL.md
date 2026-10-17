---
name: wlasl-retrain
description: WLASL 專案的重訓與本機驗證 SOP：改 ml/ 程式或超參數 → 推 wheel → Kaggle 分片前處理或雙設定訓練 → 拉模型（含 testdata）→ validate + 後端端到端評估（鏡頭幀率、相位一致率）→ 判讀 → 記錄。用在使用者要重訓、調參、加增強、換模型、多跑 seed、擴充詞彙、或驗證新一版模型的時候。
---

# WLASL 重訓與驗證 SOP

分工固定：**Kaggle 負責前處理到訓練輸出，本機只做驗證**。本機沒有 torch，不要嘗試在本機訓練。
所有指令在 repo 根目錄、用 PowerShell 執行；背景執行一律用**絕對路徑**。

## 0. 先判斷要跑哪一段

| 改了什麼 | 要跑 |
| --- | --- |
| `landmarks.py`、`preprocess.py`、詞彙量（`kaggle/preprocess/preprocess.py` 的 `SUBSET`） | 1 → 2a → 2b → 3 → 4 |
| `dataset.py`、`augment.py`、`model.py`、`train.py`、`export.py`、`segmenter.py` | 1 → 2b → 3 → 4 |
| 只改超參數／加對照組 | 只改 `kaggle/train/train.py` 的 `CONFIGS`，跳過 1 → 2b → 3 → 4 |
| 只想重新驗證既有模型 | 只跑 4 |

- `dataset.py` 的 `prepare()` 是訓練與推論共用的唯一入口，改了它就等於改了模型的輸入定義，必須重訓。
- 新增的參數組合（尤其冒煙測試的 `--epochs 1 --warmup 1` 這類極端值）推上 Kaggle 前，純 Python 的部分（排程、切片、增強）先在本機用同樣參數算一次。

## 1. 推程式碼

```powershell
cd ml; uv run pytest -q; cd ..          # 先過本機測試（numpy 部分）
& .\scripts\kaggle_push_code.ps1 -Message "<這次改了什麼>"
$env:PYTHONUTF8 = "1"; kaggle datasets status yun193/wlasl-code   # 要等到 ready 再推 kernel，否則會掛到舊版 wheel
```

## 2a. 前處理（WLASL2000，4 個 CPU kernel 平行，約 2.5 小時）

```powershell
& "D:\code\side-project_VC\WLASL-Translator-system\scripts\kaggle_preprocess_shards.ps1" -PollSeconds 300   # 背景執行
```

- 推 `yun193/wlasl-prep-0..3`，每片 2,995 支；擷取**整支影片**，index 的 start/end 保留人工標註。
- 結束後索引與 log 在 `data/kaggle_out/wlasl-prep-i/`。驗收：每片 `failed.json` 是 `[]`，4 份 `labels.json` 雜湊相同。
- 輪詢中斷時加 `-NoPush` 只等待與下載。

## 2b. 訓練（2×T4，`CONFIGS` 每組佔一張卡同時跑）

```powershell
& "D:\code\side-project_VC\WLASL-Translator-system\scripts\kaggle_run.ps1" -Name train -PollSeconds 60 -FilePattern "\.(json|log)$"   # 背景執行
```

- `kaggle/train/train.py` 會合併 4 個分片 → 每組先跑 1 epoch 冒煙測試加匯出 → 正式訓練 → 匯出到 `/kaggle/working/<設定名>/`，另附 `testdata/`（前 100 類 test 的整支影片關鍵點）。
- 時間參考：w100 300 epoch 約 6 分鐘；w2000 100 epoch 約 13 分鐘。
- 對照組設計：一次只改一個變因；另一張卡拿來跑「同設定換 seed」，用來量單次訓練本身的起伏。
- 常用 `wlasl.train` 參數：`--classes`（訓練類數，匯出只留 `--eval-classes` 前 100 類）、`--noise`（關鍵點雜訊增強）、`--p-segmenter`、`--no-subsample`、`--resample`、`--seed`。
- 失敗時看 `data/kaggle_out/train/wlasl-train.log`（JSON 格式，讀取前設 `PYTHONUTF8=1`）。

## 3. 拉模型

```powershell
& .\scripts\kaggle_pull_model.ps1 -Run <yyyyMMdd-設定名> -Config <設定名>   # → models/<Run>/，含 testdata/
```

- `-Config` 對應 `CONFIGS` 的名稱。每組各拉一次。
- 注意：後端預設載入 `models/` 底下**最新**的一版，拉完後使用者重啟 `start.ps1` 就會換模型。最後決定上線哪一版，要確認它的資料夾是最新，或請使用者設定 `WLASL_MODEL_DIR`。

## 4. 本機驗證與判讀

```powershell
& .\scripts\validate.ps1 -Run <Run> -NoLatency                        # 離線：前處理與 ONNX 一致性、test top-1
& .\scripts\eval_backend_model.ps1 -Run <Run> -Fps 30,15,10 -Phases 3  # 端到端：暫開 8767 後端跑 test 影片，約 20 分鐘，建議背景執行
```

`eval_backend_model.ps1` 會覆寫 `models/<Run>/report/backend_eval.json`；要保留舊結果先另存。

判讀順序（前一項沒過，後面的數字都不可信）：

1. **前處理一致性**必須 OK（差 0.0）；**ONNX 一致性**必須 OK、預測一致 100%。
2. **正確率要連同 95% CI 一起看**。test 只有 100 支，區間寬約 17 個百分點；val（165 支）也要一起看，再和換 seed 的對照組比，差距超過 seed 起伏才算數。
3. **錯在哪一關**（eval_backend 的歸因）：模型本身／本機關鍵點／切詞／起訖邊界。「本機關鍵點」多，代表模型對小擾動太敏感。
4. **相位一致率**：30 fps（鏡頭實際約 21～22 fps）和 10 fps 都要看；也要看「信心 ≥ 門檻」那部分的一致率和正確率，後端門檻 `MIN_CONFIDENCE`（預設 0.5，可用 `WLASL_MIN_CONFIDENCE` 覆寫），低於門檻前端只顯示 `?(前 3 名)`。

基準（2026-10-16，w2000）：val 79.4%、test 75%、後端 72%；10 fps 一致 85%、30 fps 93%；信心 ≥ 0.5 涵蓋 76%、正確 91%。

## 5. 記錄（CLAUDE.md 第 12、13 點）

- 每一個可驗證的步驟各自 commit + push；`models/`、`data/` 不進 git。
- `log.md` 追加一條：Run 名稱、改了什麼、val／test top-1、相位一致率；`index.md` 補行號（用工具量，不要估）。
- `todo-list.md` 勾選完成的項目，並更新「最後更新日期」。
- 踩到新的坑，當下就寫進 `mistake.md`。

## 已知的坑

- PowerShell 5.1：在 `$ErrorActionPreference = "Stop"` 下，不要對原生指令加 `2>&1`；`.ps1` 一律存成有 BOM 的 UTF-8，內容用 Edit 改，不要用 sed 或 Python 替換（跳脫字元會被吃掉）。
- .NET regex 的 `(?m)$` 不認 CRLF，要寫成 `(?=\r?$)`。
- 呼叫 kaggle CLI 之前要先設 `PYTHONUTF8=1`（腳本已經設好）。
- `onnxruntime-gpu` 鎖在 1.26.0：1.27 起的版本會拉 CUDA 13 套件，Windows 上裝不起來。
- 背景跑的 Python 會被 Windows EcoQoS 降速；後端與評估腳本都已呼叫 `winperf.disable_power_throttling()`。
