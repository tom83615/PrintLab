[CmdletBinding(DefaultParameterSetName = 'Deploy')]
param(
    [Parameter(Mandatory, ParameterSetName = 'Deploy')]
    [ValidatePattern('^[0-9a-fA-F]{40}$')][string]$Revision,
    [Parameter(ParameterSetName = 'Deploy')][switch]$Bootstrap,
    [Parameter(Mandatory, ParameterSetName = 'Rollback')][switch]$Rollback
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
$LocalState = Join-Path $env:LOCALAPPDATA 'PrintLab/production'
$StateFile = Join-Path $LocalState 'release.json'
$LocationFile = Join-Path $LocalState 'workspace-path.txt'
$Runtime = Join-Path $LocalState 'Runtime'
$Compose = Join-Path $Root 'compose.production.yaml'

function Invoke-Docker {
    & docker @args
    if ($LASTEXITCODE -ne 0) { throw "Docker 失敗，代碼 $LASTEXITCODE。" }
}

function Test-Studio([string]$Base) {
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        try {
            $health = Invoke-RestMethod "$Base/api/health" -TimeoutSec 3
            if ($health.ok -eq $true) { break }
        } catch { }
        Start-Sleep -Seconds 1
    }
    if ($health.ok -ne $true) { throw "工作台健康檢查失敗。$Base" }
    $page = Invoke-WebRequest "$Base/" -UseBasicParsing -TimeoutSec 5
    $asset = [regex]::Match($page.Content, 'src="(/assets/[^" ]+\.js)"')
    if (!$asset.Success) { throw "工作台首頁缺少 JavaScript 資產。$Base" }
    Invoke-WebRequest ($Base + $asset.Groups[1].Value) -UseBasicParsing -TimeoutSec 5 | Out-Null
}

function Start-Release([string]$Image) {
    $env:PRINTLAB_IMAGE = $Image
    Invoke-Docker compose -f $Compose up -d --wait --wait-timeout 60
    Test-Studio 'http://127.0.0.1:10818'
}

function Sync-WorkspaceLink([string]$RepoRoot, [string]$TargetWorkspace) {
    $resolvedRepo = (Resolve-Path -LiteralPath $RepoRoot).ProviderPath.TrimEnd('\')
    $resolvedTarget = (Resolve-Path -LiteralPath $TargetWorkspace).ProviderPath.TrimEnd('\')
    if ($resolvedRepo -ieq $resolvedTarget) { return }
    $linkPath = Join-Path $resolvedRepo 'Workspace'
    if (Test-Path -LiteralPath $linkPath) {
        $item = Get-Item -LiteralPath $linkPath -Force
        if ($item.LinkType -notin @('Junction', 'SymbolicLink')) {
            Write-Warning "略過更新 $linkPath：現有項目並非目錄聯結。"
            return
        }
        $currentTarget = @($item.Target) | Select-Object -First 1
        if ($currentTarget -and ($currentTarget.TrimEnd('\') -ieq $resolvedTarget)) { return }
        [IO.Directory]::Delete($linkPath)
    }
    New-Item -ItemType Junction -Path $linkPath -Target $resolvedTarget | Out-Null
}

New-Item -ItemType Directory -Path $LocalState -Force | Out-Null
$lock = [IO.File]::Open((Join-Path $LocalState 'deployment.lock'), 'OpenOrCreate', 'ReadWrite', 'None')
Push-Location $Root
try {
    $Workspace = $LocalState
    if (Test-Path -LiteralPath $LocationFile) {
        $location = (Get-Content -LiteralPath $LocationFile -Raw -Encoding UTF8).Trim()
        if ($location -notmatch '^[A-Za-z]:[/\\]' -or !(Test-Path -LiteralPath $location -PathType Container)) {
            throw 'workspace-path.txt 必須指定存在的 Windows 絕對資料目錄。'
        }
        $Workspace = (Resolve-Path -LiteralPath $location).ProviderPath
    }
    $env:PRINTLAB_PRODUCTION_ROOT = $Workspace
    $env:PRINTLAB_PRODUCTION_RUNTIME = $Runtime
    Sync-WorkspaceLink -RepoRoot $Root -TargetWorkspace $Workspace
    $current = if (Test-Path $StateFile) { Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json }
    if ($Rollback) {
        if (!$current.previous) { throw '尚無上一個正式版本。' }
        $image = $current.previous
    } else {
        $Revision = $Revision.ToLowerInvariant()
        $recipeFiles = @('Dockerfile', '.dockerignore', 'scripts/start-container.sh')
        $recipe = Get-FileHash -LiteralPath $recipeFiles
        $recipeId = ($recipe | ForEach-Object { $_.Hash.Substring(0, 8).ToLowerInvariant() }) -join ''
        $image = "printlab-studio:$Revision-$recipeId"
        if ($Bootstrap) {
            if ($current -and $current.image -notmatch "^printlab-studio:$Revision(?:-|$)") {
                throw '首次啟用不能取代已部署的其他提交。'
            }
            & git merge-base --is-ancestor $Revision refs/heads/tom83615
            if ($LASTEXITCODE -ne 0) { throw '首次啟用必須使用 tom83615 上的本機提交。' }
        } else {
            $headers = @{ Accept = 'application/vnd.github+json' }
            if ($env:GH_TOKEN) { $headers.Authorization = "Bearer $env:GH_TOKEN" }
            $url = 'https://api.github.com/repos/tom83615/PrintLab/actions/workflows/desktop.yml/runs'
            $runs = Invoke-RestMethod "${url}?branch=tom83615&event=push&head_sha=$Revision&per_page=20" -Headers $headers -TimeoutSec 20
            $run = $runs.workflow_runs | Where-Object {
                $_.head_sha -eq $Revision -and $_.head_branch -eq 'tom83615' -and
                $_.event -eq 'push' -and $_.status -eq 'completed' -and $_.conclusion -eq 'success'
            } | Select-Object -First 1
            if (!$run) { throw '指定提交在 tom83615 沒有成功的 Desktop VM verification 紀錄。' }
            & git fetch https://github.com/tom83615/PrintLab.git refs/heads/tom83615
            if ($LASTEXITCODE -ne 0) { throw '無法讀取 tom83615 的 Git 提交。' }
            & git merge-base --is-ancestor $Revision FETCH_HEAD
            if ($LASTEXITCODE -ne 0) { throw '指定提交不在遠端 tom83615 的歷史中。' }
        }

        $imageId = Invoke-Docker image ls --filter "reference=$image" --format '{{.ID}}'
        if (!$imageId) {
            $temp = (Get-Item -LiteralPath ([IO.Path]::GetTempPath())).FullName.TrimEnd('\')
            $build = Join-Path $temp ('printlab-release-' + [guid]::NewGuid())
            New-Item -ItemType Directory -Path $build | Out-Null
            try {
                $zip = Join-Path $build 'source.zip'
                $source = Join-Path $build 'source'
                & git archive --format=zip "--output=$zip" $Revision
                if ($LASTEXITCODE -ne 0) { throw '無法匯出指定提交。' }
                Expand-Archive -LiteralPath $zip -DestinationPath $source
                foreach ($file in $recipeFiles) {
                    Copy-Item -LiteralPath $file -Destination (Join-Path $source $file) -Force
                }
                Invoke-Docker build --build-arg "PRINTLAB_REVISION=$Revision" --tag $image $source
            } finally {
                $buildPath = Get-Item -LiteralPath $build
                if ($buildPath.Parent.FullName.TrimEnd('\') -eq $temp -and $buildPath.Name -like 'printlab-release-*') {
                    Remove-Item -LiteralPath $buildPath.FullName -Recurse -Force
                }
            }
        } elseif (((Invoke-Docker image inspect $image) | ConvertFrom-Json).Config.Labels.'org.opencontainers.image.revision' -ne $Revision) {
            throw '現有映像的提交標籤與指定版本不符。'
        }
        if ($Bootstrap) {
            Invoke-Docker run --rm -e PRINTLAB_STUDIO_PORT=8018 $image python -m pytest -q `
                Harness/tests/test_api.py Harness/tests/test_supplies.py Harness/tests/test_prepared.py `
                Harness/tests/test_prepared_api.py Harness/tests/test_workflow.py Harness/tests/test_public_inspector.py `
                Harness/tests/test_onboarding_cli.py::test_project_team_is_copied_and_loaded_by_a_later_context `
                Harness/tests/test_preview_recovery.py::test_normal_cli_entry_point_with_http_archive_source `
                Harness/tests/test_public_setup.py::test_initializer_preserves_local_data_and_uses_new_root
        }
    }

    $candidate = Invoke-Docker run --detach --rm --publish '127.0.0.1::10818' $image
    try {
        $candidateAddress = Invoke-Docker port $candidate '10818/tcp'
        Test-Studio "http://$candidateAddress"
    } finally { Invoke-Docker stop $candidate | Out-Null }

    $env:PRINTLAB_IMAGE = $image
    foreach ($folder in @('Project', 'Context', 'Library')) {
        New-Item -ItemType Directory -Path (Join-Path $Workspace $folder) -Force | Out-Null
    }
    New-Item -ItemType Directory -Path $Runtime -Force | Out-Null
    Invoke-Docker compose -f $Compose run --rm --no-deps studio python scripts/init_workspace.py
    try {
        Start-Release $image
        $previous = if ($current.image -eq $image) { $current.previous } else { $current.image }
        @{ image = $image; previous = $previous } | ConvertTo-Json | Set-Content -LiteralPath "$StateFile.tmp" -Encoding UTF8
        if (Test-Path $StateFile) { [IO.File]::Replace("$StateFile.tmp", $StateFile, "$StateFile.previous") }
        else { Move-Item -LiteralPath "$StateFile.tmp" -Destination $StateFile }
    } catch {
        if ($current.image) { Start-Release $current.image }
        else { Invoke-Docker compose -f $Compose rm --stop --force studio }
        throw
    }
    Write-Host "正式版 http://127.0.0.1:10818 使用 $image"
} finally {
    Pop-Location
    $lock.Dispose()
}
