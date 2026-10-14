# ml/ 打包成 wheel，推成私有 Kaggle Dataset（yun193/wlasl-code）
# kernel 端：pip install /kaggle/input/**/wlasl-*.whl，相依（含 mediapipe==1.1.0）由 pip 依 pyproject 安裝
param(
    [string]$Message = "update"
)
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
$Slug = "yun193/wlasl-code"
$Stage = Join-Path $Root "data\kaggle_stage\wlasl-code"

if (Test-Path $Stage) { Remove-Item -Recurse -Force -Confirm:$false $Stage }
New-Item -ItemType Directory -Force $Stage | Out-Null

Push-Location (Join-Path $Root "ml")
try {
    uv build --wheel --out-dir $Stage
    if ($LASTEXITCODE -ne 0) { throw "uv build 失敗" }
} finally { Pop-Location }

@{
    title    = "wlasl-code"
    id       = $Slug
    licenses = @(@{ name = "other" })
} | ConvertTo-Json -Depth 3 | Out-File -Encoding ascii (Join-Path $Stage "dataset-metadata.json")

# 用 list 判斷是否已存在：PS 5.1 在 Stop 模式下把原生程式的 stderr 當例外，不能靠 status 的 403
$exists = kaggle datasets list --mine -s "wlasl-code" --csv | Select-String -SimpleMatch $Slug
if ($exists) {
    kaggle datasets version -p $Stage -m $Message
} else {
    kaggle datasets create -p $Stage
}
if ($LASTEXITCODE -ne 0) { throw "kaggle 上傳失敗" }
Write-Host "已推送 $Slug"
