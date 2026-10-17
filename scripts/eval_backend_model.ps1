# 對指定模型開一個暫時的後端（預設 8767，不動使用者 8766 的服務），跑 eval_backend.py 後關掉
# 例：.\scripts\eval_backend_model.ps1 -Run 20261018-w2000n
#     .\scripts\eval_backend_model.ps1 -Run 20261018-w2000n -Fps 30,15,10 -Phases 3
param(
    [Parameter(Mandatory = $true)][string]$Run,
    [double[]]$Fps = @(30, 15, 10),
    [int]$Phases = 3,
    [int]$Port = 8767,
    [switch]$NoLocal
)
$ErrorActionPreference = "Continue"
$env:PYTHONUTF8 = "1"
$Root = Split-Path $PSScriptRoot -Parent
$ModelDir = Join-Path $Root "models\$Run"
if (-not (Test-Path (Join-Path $ModelDir "model.onnx"))) { throw "找不到 $ModelDir\model.onnx" }

$env:WLASL_PORT = "$Port"
$env:WLASL_MODEL_DIR = $ModelDir
$server = Start-Process -FilePath "uv" -ArgumentList "run", "python", "-m", "app", "--no-browser" `
    -WorkingDirectory (Join-Path $Root "backend") -PassThru -WindowStyle Hidden
try {
    $ready = $false
    for ($i = 0; $i -lt 60 -and -not $ready; $i++) {
        try { Invoke-WebRequest "http://127.0.0.1:$Port/api/health" -UseBasicParsing -TimeoutSec 2 | Out-Null; $ready = $true }
        catch { Start-Sleep 2 }
    }
    if (-not $ready) { throw "後端 $Port 沒有起來" }
    $evalArgs = @("run", "--project", (Join-Path $Root "backend"), "python", (Join-Path $Root "scripts\eval_backend.py"),
        "--url", "http://127.0.0.1:$Port", "--phases", "$Phases", "--stream-fps") + ($Fps | ForEach-Object { "$_" })
    if ($NoLocal) { $evalArgs += "--no-local" }
    & uv @evalArgs
    $code = $LASTEXITCODE
} finally {
    # 只關這次啟動的 uv 與其子孫
    taskkill /PID $server.Id /T /F | Out-Null
}
if ($code -ne 0) { throw "eval_backend.py 失敗（exit $code）" }
