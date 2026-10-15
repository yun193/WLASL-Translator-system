# WLASL2000 前處理拆成 N 個 Kaggle CPU kernel 平行跑（單一 kernel 約 8 小時，逼近 12 小時上限）
# 以 kaggle/preprocess/ 為範本，改寫 SHARD 推成 yun193/wlasl-prep-<i> → 輪詢到全部結束 → 下載 index / log
# 例：.\scripts\kaggle_preprocess_shards.ps1               推送並等待
#     .\scripts\kaggle_preprocess_shards.ps1 -NoPush       只等待與下載（例如輪詢中斷後）
param(
    [int]$Shards = 4,
    [int]$PollSeconds = 300,
    [switch]$NoPush
)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$Root = Split-Path $PSScriptRoot -Parent
$Template = Join-Path $Root "kaggle\preprocess"
$code = Get-Content (Join-Path $Template "preprocess.py") -Raw -Encoding UTF8
$meta = Get-Content (Join-Path $Template "kernel-metadata.json") -Raw | ConvertFrom-Json
# 範本是 CRLF：.NET 的 (?m)$ 只認 LF，所以用 (?=\r?$) 允許前面的 CR
if ($code -notmatch "(?m)^SHARDS = $Shards(?=\r?$)") { throw "kaggle/preprocess/preprocess.py 的 SHARDS 不是 $Shards" }

$ids = @()
for ($i = 0; $i -lt $Shards; $i++) {
    $id = "yun193/wlasl-prep-$i"
    $ids += $id
    if ($NoPush) { continue }
    $stage = Join-Path $Root "data\kaggle_stage\prep-$i"
    New-Item -ItemType Directory -Force $stage | Out-Null
    $utf8 = New-Object System.Text.UTF8Encoding $false
    $shardCode = $code -replace "(?m)^SHARD = \d+(?=\r?$)", "SHARD = $i"
    if ($shardCode -notmatch "(?m)^SHARD = $i(?=\r?$)") { throw "改寫 SHARD 失敗" }
    [IO.File]::WriteAllText((Join-Path $stage "preprocess.py"), $shardCode, $utf8)
    $meta.id = $id
    $meta.title = "wlasl-prep-$i"
    [IO.File]::WriteAllText((Join-Path $stage "kernel-metadata.json"), ($meta | ConvertTo-Json -Depth 3), $utf8)
    kaggle kernels push -p $stage
    if ($LASTEXITCODE -ne 0) { throw "推送 $id 失敗" }
}

$start = Get-Date
$done = @{}
while ($done.Count -lt $ids.Count) {
    Start-Sleep -Seconds $PollSeconds
    $elapsed = [int]((Get-Date) - $start).TotalMinutes
    foreach ($id in $ids) {
        if ($done.ContainsKey($id)) { continue }
        $status = (kaggle kernels status $id) -join " "
        Write-Host "[$elapsed min] $status"
        if ($status -match "COMPLETE|ERROR|CANCEL") { $done[$id] = $status }
    }
}

# 只拉索引與 log（上千個 .npy 留在 Kaggle，訓練 kernel 直接掛載）
foreach ($id in $ids) {
    $out = Join-Path $Root ("data\kaggle_out\" + ($id -split "/")[1])
    New-Item -ItemType Directory -Force $out | Out-Null
    kaggle kernels output $id -p $out -o -q --page-size 200 --file-pattern "^[^/]+\.(json|log)$"
}
$bad = $done.GetEnumerator() | Where-Object { $_.Value -notmatch "COMPLETE" }
if ($bad) { throw "有分片沒有成功：$($bad | ForEach-Object { $_.Key })" }
Write-Host "全部完成，索引在 data\kaggle_out\wlasl-prep-*"
