# 從 Kaggle 拉訓練產出到 models/<Run>/，連同 test 資料（testdata/：前 100 類 test 的整支影片關鍵點與索引）
# 例：.\scripts\kaggle_pull_model.ps1 -Run 20261016-w2000 -Config w2000
#     -Config 對應 kaggle/train/train.py 的 CONFIGS 名稱；舊版單一設定的產出不加 -Config
param(
    [string]$Run = (Get-Date -Format "yyyyMMdd-HHmm"),
    [string]$Config
)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$Root = Split-Path $PSScriptRoot -Parent
$ModelDir = Join-Path $Root "models\$Run"
New-Item -ItemType Directory -Force $ModelDir | Out-Null

$files = "(model\.onnx|labels\.json|reference\.npz|metrics\.json|history\.json|train\.log)"
$prefix = if ($Config) { [regex]::Escape($Config) + "/" } else { "" }
kaggle kernels output yun193/wlasl-train -p $ModelDir -o -q --page-size 200 --file-pattern "^(${prefix}${files}|testdata/.*)$"
if ($LASTEXITCODE -ne 0) { throw "下載訓練產出失敗" }
if ($Config) {
    Get-ChildItem (Join-Path $ModelDir $Config) | Move-Item -Destination $ModelDir -Force
    Remove-Item (Join-Path $ModelDir $Config) -Recurse -Force -Confirm:$false
}
if (-not (Test-Path (Join-Path $ModelDir "model.onnx"))) { throw "沒有拉到 model.onnx（-Config 名稱對嗎？）" }
$n = (Get-ChildItem (Join-Path $ModelDir "testdata\keypoints") -Filter *.npy).Count
Write-Host "模型 → $ModelDir；test 關鍵點 $n 支 → $ModelDir\testdata"
