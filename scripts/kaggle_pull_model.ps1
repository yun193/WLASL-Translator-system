# 從 Kaggle 拉訓練產出到 models/<Run>/，並拉 test split 的原始關鍵點（本機驗證前處理一致性用）
# 例：.\scripts\kaggle_pull_model.ps1 -Run 20261014-v1
param(
    [string]$Run = (Get-Date -Format "yyyyMMdd-HHmm")
)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$Root = Split-Path $PSScriptRoot -Parent
$ModelDir = Join-Path $Root "models\$Run"
$Pre = Join-Path $Root "data\kaggle_out\preprocess"

New-Item -ItemType Directory -Force $ModelDir, $Pre | Out-Null
kaggle kernels output yun193/wlasl-train -p $ModelDir -o -q --page-size 200 `
    --file-pattern "^(model\.onnx|labels\.json|reference\.npz|metrics\.json|history\.json)$"
if ($LASTEXITCODE -ne 0) { throw "下載訓練產出失敗" }

if (-not (Test-Path (Join-Path $Pre "index.json"))) {
    kaggle kernels output yun193/wlasl-preprocess -p $Pre -o -q --page-size 200 --file-pattern "^(index|labels)\.json$"
}
$ids = (Get-Content (Join-Path $Pre "index.json") -Raw | ConvertFrom-Json) |
    Where-Object { $_.subset -eq "test" } | ForEach-Object { $_.video_id }
$pattern = "keypoints/(" + ($ids -join "|") + ")\.npy$"
kaggle kernels output yun193/wlasl-preprocess -p $Pre -q --page-size 200 --file-pattern $pattern
if ($LASTEXITCODE -ne 0) { throw "下載 test 關鍵點失敗" }

$n = (Get-ChildItem (Join-Path $Pre "keypoints") -Filter *.npy).Count
Write-Host "模型 → $ModelDir；test 關鍵點 $n / $($ids.Count) 支 → $Pre\keypoints"
