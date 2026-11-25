$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$Python = Join-Path $Root 'Runtime/venv/Scripts/python.exe'
if (!(Test-Path $Python)) { throw 'Run scripts/setup.ps1 first.' }
if ([string]::IsNullOrWhiteSpace($env:PRINTLAB_ROOT) -and $env:LOCALAPPDATA) {
    $ProdState = Join-Path $env:LOCALAPPDATA 'PrintLab/production'
    $LocationFile = Join-Path $ProdState 'workspace-path.txt'
    if (Test-Path -LiteralPath $LocationFile -PathType Leaf) {
        $Configured = (Get-Content -LiteralPath $LocationFile -Raw -Encoding UTF8).Trim()
        if ($Configured -match '^[A-Za-z]:[/\\]' -and (Test-Path -LiteralPath $Configured -PathType Container)) {
            $env:PRINTLAB_ROOT = (Resolve-Path -LiteralPath $Configured).ProviderPath
            if ([string]::IsNullOrWhiteSpace($env:PRINTLAB_RUNTIME_ROOT)) {
                $env:PRINTLAB_RUNTIME_ROOT = Join-Path $ProdState 'Runtime'
            }
        }
    }
}
$env:PYTHONPATH = Join-Path $Root 'Harness'
& $Python -X utf8 -m printlab.cli @args
exit $LASTEXITCODE
