$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
$Workspace = Join-Path $env:LOCALAPPDATA 'PrintLab/development'
$Python = Join-Path $Root 'Runtime/venv/Scripts/python.exe'
$Studio = Join-Path $Root 'Harness/studio'
$Vite = Join-Path $Studio 'node_modules/vite/bin/vite.js'
$Dist = Join-Path $Workspace 'Harness/studio/dist'
if (!(Test-Path $Python) -or !(Test-Path $Vite)) { throw '先執行 scripts/setup.ps1。' }

$env:PYTHONUTF8 = '1'
$env:PYTHONPATH = Join-Path $Root 'Harness'
$env:PRINTLAB_ROOT = $Workspace
$env:PRINTLAB_STUDIO_PORT = '8018'

Push-Location $Studio
try {
    & node $Vite build --outDir $Dist --emptyOutDir
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }

$logs = Join-Path $Workspace 'Runtime/logs'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$watcher = Start-Process -FilePath (Get-Command node).Source -WorkingDirectory $Studio `
    -ArgumentList @("`"$Vite`"", 'build', '--watch', '--outDir', "`"$Dist`"", '--emptyOutDir') `
    -RedirectStandardOutput (Join-Path $logs 'frontend.log') `
    -RedirectStandardError (Join-Path $logs 'frontend-error.log') -WindowStyle Hidden -PassThru
try {
    $serverArgs = @('--host', '127.0.0.1', '--port', '8018', '--reload', '--reload-dir', (Join-Path $Root 'Harness'), '--no-proxy-headers')
    Write-Host '開發版 http://localhost:8018。資料操作由正式版處理。'
    & $Python -m uvicorn serve_shared_preview:app --app-dir $PSScriptRoot --reload-dir $PSScriptRoot --lifespan off @serverArgs
    exit $LASTEXITCODE
} finally {
    if (!$watcher.HasExited) { Stop-Process -Id $watcher.Id }
}
