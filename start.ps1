# 一鍵啟動：前端沒建置過或原始碼有更新就先建置，接著啟動本機服務並開啟瀏覽器
# 用法：.\start.ps1            一般啟動
#       .\start.ps1 -NoBrowser 不自動開瀏覽器
param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$fe = Join-Path $root 'frontend'
$dist = Join-Path $fe 'dist\index.html'

if (-not (Get-ChildItem (Join-Path $root 'models') -Filter model.onnx -Recurse -ErrorAction SilentlyContinue)) {
    Write-Host '找不到模型：先執行 scripts\kaggle_pull_model.ps1 -Run <run 名稱>' -ForegroundColor Yellow
    exit 1
}

$needBuild = -not (Test-Path $dist)
if (-not $needBuild) {
    $built = (Get-Item $dist).LastWriteTime
    $sources = @(Get-ChildItem (Join-Path $fe 'src') -Recurse -File) + @(Get-Item (Join-Path $fe 'index.html'), (Join-Path $fe 'package.json'))
    $needBuild = [bool]($sources | Where-Object { $_.LastWriteTime -gt $built } | Select-Object -First 1)
}
if ($needBuild) {
    Push-Location $fe
    try {
        if (-not (Test-Path 'node_modules')) { npm install --no-fund --no-audit }
        npm run build
        if ($LASTEXITCODE -ne 0) { throw '前端建置失敗' }
    } finally {
        Pop-Location
    }
}

Push-Location (Join-Path $root 'backend')
try {
    $appArgs = @()
    if ($NoBrowser) { $appArgs += '--no-browser' }
    uv run python -m app @appArgs
} finally {
    Pop-Location
}
