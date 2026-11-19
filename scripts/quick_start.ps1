$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
$Url = 'http://127.0.0.1:8018/'
$HealthUrl = 'http://127.0.0.1:8018/api/health'

function Get-PrintLabHealth {
    try {
        $health = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 2
        if ($health.ok -and $health.features -contains 'prepared-print-v1') { return $health }
    } catch { }
    return $null
}

if (-not (Get-PrintLabHealth)) {
    $StartScript = Join-Path $PSScriptRoot 'start.ps1'
    Start-Process -FilePath 'powershell.exe' `
        -ArgumentList ('-NoProfile -ExecutionPolicy Bypass -File "' + $StartScript + '"') `
        -WorkingDirectory $Root -WindowStyle Hidden

    $Deadline = (Get-Date).AddSeconds(45)
    while ((Get-Date) -lt $Deadline) {
        Start-Sleep -Milliseconds 500
        if (Get-PrintLabHealth) { break }
    }
}

if (Get-PrintLabHealth) {
    Start-Process $Url
} else {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show(
        'PrintLab 無法啟動。請確認安裝資料夾仍位於原位置，或手動執行 scripts\start.ps1。',
        'PrintLab 啟動失敗', 'OK', 'Error'
    ) | Out-Null
}
