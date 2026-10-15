# 本機一鍵驗證：（可選）從 Kaggle 拉最新模型 → wlasl.evaluate → models/<Run>/report/
# 例：.\scripts\validate.ps1                 驗證 models/ 底下最新的一版
#     .\scripts\validate.ps1 -Pull -Run v2   先拉 Kaggle 最新產出成 models/v2 再驗證
param(
    [string]$Run,
    [switch]$Pull,
    [switch]$NoLatency
)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$Root = Split-Path $PSScriptRoot -Parent

if ($Pull) {
    if (-not $Run) { $Run = Get-Date -Format "yyyyMMdd-HHmm" }
    & (Join-Path $PSScriptRoot "kaggle_pull_model.ps1") -Run $Run
}
if (-not $Run) {
    $latest = Get-ChildItem (Join-Path $Root "models") -Directory |
        Where-Object { Test-Path (Join-Path $_.FullName "model.onnx") } |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $latest) { throw "models/ 底下沒有模型，先加 -Pull" }
    $Run = $latest.Name
}

$py = Join-Path $Root "ml\.venv\Scripts\python.exe"
$evalArgs = @("-m", "wlasl.evaluate", "--model", (Join-Path $Root "models\$Run"),
          "--data", (Join-Path $Root "data\kaggle_out\preprocess"))
if ($NoLatency) { $evalArgs += "--no-latency" }
& $py @evalArgs
if ($LASTEXITCODE -ne 0) { throw "驗證失敗" }
