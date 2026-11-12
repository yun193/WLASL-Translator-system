# WLASL2000 前處理拆成 N 個 Kaggle CPU kernel 平行跑（單一 kernel 約 8 小時，逼近 12 小時上限）
# 以 kaggle/preprocess/ 為範本，改寫 SHARD 推成 yun193/wlasl-prep-<i> → 輪詢到全部結束 → 下載 index / log
# 例：.\scripts\kaggle_preprocess_shards.ps1               推送並等待
#     .\scripts\kaggle_preprocess_shards.ps1 -NoPush       只等待與下載（例如輪詢中斷後）
#     .\scripts\kaggle_preprocess_shards.ps1 -Template aslc_prep -Prefix aslc-prep -Shards 6   ASL Citizen
param(
    [int]$Shards = 4,
    [int]$PollSeconds = 300,
    [string]$Template = "preprocess",
    [string]$Prefix = "wlasl-prep",
    [switch]$NoPush
)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$Root = Split-Path $PSScriptRoot -Parent
$TemplateDir = Join-Path $Root "kaggle\$Template"
$meta = Get-Content (Join-Path $TemplateDir "kernel-metadata.json") -Raw | ConvertFrom-Json
$codeFile = $meta.code_file
$code = Get-Content (Join-Path $TemplateDir $codeFile) -Raw -Encoding UTF8
# 範本可能是 CRLF：.NET 的 (?m)$ 只認 LF，所以用 (?=\r?$) 允許前面的 CR
if ($code -notmatch "(?m)^SHARDS = $Shards(?=\r?$)") { throw "kaggle/$Template/$codeFile 的 SHARDS 不是 $Shards" }

$ids = @()
for ($i = 0; $i -lt $Shards; $i++) {
    $id = "yun193/$Prefix-$i"
    $ids += $id
    if ($NoPush) { continue }
    $stage = Join-Path $Root "data\kaggle_stage\$Prefix-$i"
    New-Item -ItemType Directory -Force $stage | Out-Null
    $utf8 = New-Object System.Text.UTF8Encoding $false
    $shardCode = $code -replace "(?m)^SHARD = \d+(?=\r?$)", "SHARD = $i"
    if ($shardCode -notmatch "(?m)^SHARD = $i(?=\r?$)") { throw "改寫 SHARD 失敗" }
    [IO.File]::WriteAllText((Join-Path $stage $codeFile), $shardCode, $utf8)
    $meta.id = $id
    $meta.title = "$Prefix-$i"
    [IO.File]::WriteAllText((Join-Path $stage "kernel-metadata.json"), ($meta | ConvertTo-Json -Depth 3), $utf8)
    # 超過同時 5 個 CPU session 時 push 只印錯誤、exit code 仍是 0
    $msg = (kaggle kernels push -p $stage) -join " "
    Write-Host $msg
    if ($LASTEXITCODE -ne 0 -or $msg -match "error") { throw "推送 $id 失敗：$msg" }
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
Write-Host "全部完成，索引在 data\kaggle_out\$Prefix-*"
