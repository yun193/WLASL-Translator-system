# 推送 kaggle/<Name>/ 的 kernel → 輪詢狀態 → 完成後下載 log 與指定產出到 data/kaggle_out/<Name>/
# 例：.\scripts\kaggle_run.ps1 -Name preprocess -FilePattern "\.(json|log)$"
param(
    [Parameter(Mandatory)][string]$Name,
    [string]$FilePattern = "\.(json|log|txt)$",
    [int]$PollSeconds = 60,
    [switch]$NoPush
)
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
$Dir = Join-Path $Root "kaggle\$Name"
$Meta = Get-Content (Join-Path $Dir "kernel-metadata.json") -Raw | ConvertFrom-Json
$Id = $Meta.id
$Out = Join-Path $Root "data\kaggle_out\$Name"

if (-not $NoPush) {
    kaggle kernels push -p $Dir
    if ($LASTEXITCODE -ne 0) { throw "kernels push 失敗" }
}

$start = Get-Date
while ($true) {
    Start-Sleep -Seconds $PollSeconds
    $status = (kaggle kernels status $Id) -join " "
    $elapsed = [int]((Get-Date) - $start).TotalMinutes
    Write-Host "[$elapsed min] $status"
    if ($status -match "COMPLETE|ERROR|CANCEL") { break }
}

New-Item -ItemType Directory -Force $Out | Out-Null
kaggle kernels output $Id -p $Out -o --file-pattern $FilePattern
if ($status -notmatch "COMPLETE") { throw "kernel 未成功完成：$status（log 已下載到 $Out）" }
Write-Host "完成，產出在 $Out"
