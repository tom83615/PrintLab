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
& $Python (Join-Path $PSScriptRoot 'init_workspace.py')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
foreach ($path in @('AGENTS.md', 'Templates', 'Context/workflow.md')) {
    $destination = Join-Path $Workspace $path
    if (!(Test-Path $destination)) { Copy-Item -LiteralPath (Join-Path $Root $path) -Destination $destination -Recurse }
}

Push-Location $Studio
try {
    & node $Vite build --outDir $Dist --emptyOutDir
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }

$logs = Join-Path $Workspace 'Runtime/logs'
$watcher = Start-Process -FilePath (Get-Command node).Source -WorkingDirectory $Studio `
    -ArgumentList @("`"$Vite`"", 'build', '--watch', '--outDir', "`"$Dist`"", '--emptyOutDir') `
    -RedirectStandardOutput (Join-Path $logs 'frontend.log') `
    -RedirectStandardError (Join-Path $logs 'frontend-error.log') -WindowStyle Hidden -PassThru
try {
    Write-Host '開發版 http://localhost:8018。前端建置後重新整理頁面。'
    & $Python -m uvicorn printlab.api:app --host 127.0.0.1 --port 8018 --reload --reload-dir (Join-Path $Root 'Harness') --no-proxy-headers
    exit $LASTEXITCODE
} finally {
    if (!$watcher.HasExited) { Stop-Process -Id $watcher.Id }
}
