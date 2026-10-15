---
name: wlasl-retrain
description: WLASL 專案的重訓與本機驗證 SOP：改 ml/ 程式或超參數 → 推 wheel → Kaggle 重新前處理或訓練 → 拉模型 → 本機驗證 → 判讀 → 記錄。用在使用者要重訓、調參、換模型、多跑 seed、擴充詞彙（WLASL300）、或要驗證新一版模型的時候。
---

# WLASL 重訓與驗證 SOP

分工固定：**Kaggle 負責前處理到訓練輸出，本機只做驗證**。本機沒有 torch，不要嘗試在本機訓練。
所有指令在 repo 根目錄、用 PowerShell 執行；背景執行時一律用**絕對路徑**。

## 0. 先判斷要跑哪一段

| 改了什麼 | 要跑 |
| --- | --- |
| `landmarks.py`、`preprocess.py`、詞彙量（`--subset`） | 1 → 2（preprocess）→ 2（train）→ 3 → 4 |
| `dataset.py`、`augment.py`、`model.py`、`train.py`、`export.py` | 1 → 2（train）→ 3 → 4 |
| 只改超參數 | 只改 `kaggle/train/train.py` 的 `TRAIN_ARGS`，跳過 1 → 2（train）→ 3 → 4 |
| 只想重新驗證既有模型 | 只跑 4 |

`dataset.py` 的 `prepare()` 是訓練與推論共用的唯一入口，改了它就等於改了模型的輸入定義，必須重訓。

## 1. 推程式碼

```powershell
cd ml; uv run pytest -q; cd ..          # 先過本機測試（numpy 部分）
& .\scripts\kaggle_push_code.ps1 -Message "<這次改了什麼>"
```

推完要等 Dataset 狀態變成 ready，再推 kernel，否則 kernel 會掛到舊版 wheel：

```bash
until kaggle datasets status yun193/wlasl-code | grep -qi ready; do sleep 5; done
```

## 2. 在 Kaggle 跑 kernel（用背景執行，跑完會通知）

```powershell
& "D:\code\side-project_VC\WLASL-Translator-system\scripts\kaggle_run.ps1" -Name preprocess -PollSeconds 120   # 約 40 分鐘
& "D:\code\side-project_VC\WLASL-Translator-system\scripts\kaggle_run.ps1" -Name train -PollSeconds 60 -FilePattern "\.(json|onnx|npz|log|pt)$"   # 約 5 分鐘
```

- 訓練 kernel 會先跑 2 個 epoch 的冒煙測試，再正式訓練；失敗時看 `data/kaggle_out/<Name>/*.log`。
- 本機的輪詢腳本如果中斷（例如 session 結束），kernel 會照跑；之後加上 `-NoPush` 補拉產出即可。

## 3. 拉模型

```powershell
& .\scripts\kaggle_pull_model.ps1 -Run <yyyyMMdd-說明>   # → models/<Run>/，同時補齊 test 原始關鍵點
```

如果重跑過 preprocess，要先刪掉 `data/kaggle_out/preprocess/` 裡舊的 `index.json` 和 `keypoints/`（請使用者確認後再刪），否則會拿到舊的關鍵點。

## 4. 本機驗證與判讀

```powershell
& .\scripts\validate.ps1 -Run <Run>     # 報告在 models/<Run>/report/{report.json, confusion.png}
```

判讀順序（前一項沒過，後面的數字都不可信）：

1. **前處理一致性**必須是 OK（目前是逐位元相同，差 0.0）。FAIL 代表本機和 Kaggle 的 `prepare()` 或 mediapipe 版本不一致。
2. **ONNX 一致性**必須是 OK，而且預測一致率 100%。CUDA EP 必須關閉 TF32（`evaluate.py` 已經處理）。
3. **test top-1 要連同 95% 信賴區間一起看**。test 只有 100 支，區間寬約 17 個百分點；兩版的差距落在區間內，就不能說哪一版比較好，要用多個 seed 的平均來比較。
4. 延遲只供參考。即時推論用的是 CPU 版 onnxruntime，瓶頸在 MediaPipe。

## 5. 記錄（CLAUDE.md 第 12、13 點）

- 每一個可驗證的步驟各自 commit + push；`models/`、`data/` 不進 git。
- `log.md` 追加一條，寫明 Run 名稱、改了什麼、test top-1 [CI]、top-5、val top-1；`index.md` 補上行號（用工具量，不要估）。
- `todo-list.md` 勾選完成的項目，並更新「最後更新日期」。
- 踩到新的坑，當下就寫進 `mistake.md`。

## 已知的坑

- PowerShell 5.1：在 `$ErrorActionPreference = "Stop"` 下，不要對原生指令加 `2>&1`；`.ps1` 一律存成有 BOM 的 UTF-8。
- 呼叫 kaggle CLI 之前要先設 `PYTHONUTF8=1`（腳本已經設好）。
- `onnxruntime-gpu` 鎖在 1.26.0：1.27 起的版本會拉 CUDA 13 套件，Windows 上裝不起來。
- `kernel-metadata.json` 的 `machine_shape: NvidiaTeslaT4` 就是 2×T4；資料量這麼小，DDP 不會比較快。如果要比較設定，兩張卡各跑一個設定會更划算。
