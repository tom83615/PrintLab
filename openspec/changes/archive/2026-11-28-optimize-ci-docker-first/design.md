# Design

## Context

目前正式版 PrintLab Web 工作台以 [`Dockerfile`](../../../Dockerfile)（`python:3.13-slim-bookworm` + `node:22-bookworm-slim`）在 Docker 執行，而日常 CLI（`Harness/bin/printlab.ps1`）、開發腳本（`scripts/start-dev.ps1`）與部署腳本（`scripts/deploy-production.ps1`）在 Windows 宿主機執行。部署腳本寫死了查詢 `tom83615/PrintLab` 的 `desktop.yml` 在 `tom83615` 分支 push 事件的成功紀錄。見 `proposal.md` 的 Why。

## Goals / Non-Goals

**Goals:**
- 讓例行 push / PR CI 在維持正式部署與 Windows 宿主機可用性的前提下盡可能快速完成。
- 直接在 CI 驗證實際上線的 `Dockerfile` 映像建置與容器執行期行為。
- 全面啟用 Docker Buildx、pip、npm 與 Playwright 快取，減少重複下載與建置時間。
- 保留完整 Windows / macOS 與重型上游工具安裝驗證作為手動觸發工作流，避免失去回溯能力。

**Non-Goals:**
- 不修改 `scripts/deploy-production.ps1` 查詢 `desktop.yml` 的既定部署門檻。
- 不修改核心應用程式邏輯、測試斷言或 `Dockerfile` 基底映像。
- 不為例行 push 保留 `macos-latest` 或 `windows-2022`（Python `3.11`）。

## Decisions

### 1. 保留 `.github/workflows/desktop.yml` 檔名並拆分為三個並行 job
- **決策**：保留 `desktop.yml` 作為 push / PR 主驗證工作流，內含 `docker-verify`、`linux-verify`、`windows-host-verify` 三個並行 job。
- **理由**：`scripts/deploy-production.ps1` 直接以 GitHub API 查詢 `actions/workflows/desktop.yml/runs`。維持檔名可零中斷銜接既有部署流程，三個 job 並行讓總耗時取決於最慢的單一 job（約 1.5–3 分鐘）而非串行疊加。
- **替代方案**：改名為 `ci.yml` 並同步改 `deploy-production.ps1` —— 會造成舊版部署腳本或文件參照失效，收益為零，故不採用。

### 2. 以 `docker-verify` + `linux-verify` 取代跨平台重複跑全套測試與 Playwright
- **決策**：
  - `docker-verify` 使用 `docker/setup-buildx-action@v3` + `docker/build-push-action@v6`（`cache-from: type=gha`、`cache-to: type=gha,mode=max`、`load: true`）建置 `Dockerfile`，啟動容器檢驗 `/api/health`、首頁 `/assets/*.js` 載入、`docker exec ... python -m printlab.cli status`，並於容器內執行不含倉庫 `docs/` 依賴的執行期 pytest 子集（104 項測試）。
  - `linux-verify` 在 `ubuntu-latest`（Python `3.13` + Node `22`）執行 `bash scripts/setup.sh`、完整 `pytest Harness/tests`、`PRINTLAB_SKIP_RELEASE_CHECK=1 python scripts/verify_onboarding.py`、`node --test Harness/tests/native-inspection.test.mjs` 及 Playwright Chromium 實測（`scripts/verify_browser.py`）。
- **理由**：`Dockerfile` 不含 `docs/` 與 `.agents/`，無法直接於映像內跑完所有仰賴倉庫檔案的測試（例如 `test_onboarding_cli.py` 讀取 `docs/ROLES.md`）。拆成 `docker-verify` 驗映像本身 + `linux-verify` 驗完整 repo 測試與瀏覽器，既能並行加速，又 100% 覆蓋正式 Linux 執行環境與所有測試。

### 3. Windows 宿主機改為單一輕量 `windows-host-verify`（`windows-2025` + Python `3.13`）
- **決策**：移除 `windows-2022`（Python `3.11`），僅保留 `windows-2025`（Python `3.13`）搭配 pip/npm 快取執行 `scripts/setup.ps1`、Windows 宿主機關鍵測試檔案（`test_platform_runtime.py`、`test_windows_private_acl.py`、`test_external_workspace.py`、`test_public_setup.py`、`test_workbench_recovery.py`、`test_backup.py`）與 `PRINTLAB_SKIP_RELEASE_CHECK=1` 的 `verify_onboarding.py`，且不於 Windows 安裝 Playwright / Chromium。
- **理由**：瀏覽器 UI 行為已在 `linux-verify` 以真實 Chromium 驗收；Windows 宿主機真正獨有的風險集中在 PowerShell 入口（`printlab.ps1`、`start.ps1`、`text2cad.ps1`）、`workspace-path.txt` 外部資料空間解析、Windows ACL（`SeSecurityPrivilege`）與非 UTF-8 預設語系。只跑這些測試可將 Windows job 從十幾分鐘壓縮到約 1.5–2 分鐘。

### 4. 抽離四個重型上游工具安裝測試與 macOS 至手動工作流
- **決策**：例行 CI 一律設定 `PRINTLAB_SKIP_RELEASE_CHECK=1`，跳過 `verify_onboarding.py` 末尾串接的 `verify_release_install.py`、`verify_cad_install.py`、`verify_bambuddy_install.py`、`verify_studio_install.py`；另建 `.github/workflows/full-release-matrix.yml`（僅 `workflow_dispatch`）提供完整 `windows-2025` + `macos-latest` 矩陣驗證。
- **理由**：這四個腳本每次都會重新下載數百 MB 上游封包（Bambu Studio、cad-server/Python 3.14、Bambuddy 與二次完整 ZIP 安裝），與日常應用程式修改無直接關聯，是原 CI 最耗時且最容易因網路波動失敗的來源。

### 5. Artifact 保留期限制
- **決策**：所有 `actions/upload-artifact@v4` 步驟加上 `retention-days: 7`，並使用 `if-no-files-found: ignore` 避免尚未產出目錄時報錯。

## Risks / Trade-offs

- [macOS 專屬程式碼（如 `StudioBridge.swift`）在例行 push 不再自動編譯檢查] → 保留 `full-release-matrix.yml` 手動工作流，於修改 macOS 相關檔案或準備上游 PR 前手動觸發驗證。
- [上游第三方安裝腳本（CAD / Bambuddy / Studio）若上游連結失效不會在例行 push 立刻發現] → 升級 `verify_*_install.py` 鎖定版本或準備發佈 ZIP 時手動執行 `full-release-matrix.yml`。
- [Windows 上部分純跨平台單元測試未重複執行] → 已於 `linux-verify` 跑完整 `Harness/tests`，且 `windows-host-verify` 涵蓋全部 `sys.platform == 'win32'` 專屬測試與 `verify_onboarding.py`。
