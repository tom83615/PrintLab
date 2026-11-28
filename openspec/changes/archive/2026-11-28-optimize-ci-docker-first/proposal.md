# Proposal

## Why

目前 GitHub Actions 工作流（`.github/workflows/desktop.yml`）每次 push 都在三台 VM（`windows-2022`、`windows-2025`、`macos-latest`）上從頭安裝依賴、執行 Playwright 與四個重型上游工具下載驗證（ZIP 封包重裝、Text-to-CAD、Bambuddy、Bambu Studio），不僅耗時且容易因外部下載或 macOS 環境拖慢部署，還完全缺少對實際正式執行環境（`Dockerfile` Linux 容器）的驗證。

## What Changes

- 重新設計 `.github/workflows/desktop.yml` 為 Docker 優先的快速並行驗證流水線，並維持工作流檔名以相容 `scripts/deploy-production.ps1` 的部署前置檢查：
  - `docker-verify`（`ubuntu-latest`）：使用 Buildx 與 GHA 層快取建置正式 `Dockerfile` 映像，驗證容器健康檢查、首頁前端資產、容器內 CLI 與容器執行期 pytest 子集。
  - `linux-verify`（`ubuntu-latest`）：搭配 pip、npm 與 Playwright 快取執行完整 `Harness/tests`、`verify_onboarding.py`（跳過重型上游下載）、`native-inspection.test.mjs` 與 Playwright 實測瀏覽器驗收。
  - `windows-host-verify`（`windows-2025`、Python `3.13`）：搭配 pip 與 npm 快取驗證 `scripts/setup.ps1`、Windows 宿主機專屬測試（PowerShell 入口、外部正式資料空間解析、ACL/UTF-8、備份與恢復）及輕量 `verify_onboarding.py`。
- 移除每次 push 常駐執行的 `windows-2022`（Python `3.11`）、`macos-latest` 與四個重型上游安裝下載檢查。
- 新增手動觸發工作流 `.github/workflows/full-release-matrix.yml`（`workflow_dispatch`），保留在升級第三方依賴或發送上游 PR 前按需執行完整 Windows / macOS 與重型上游安裝驗證的能力。
- 同步更新 `docs/LOCAL_DEPLOYMENT.md` 與 `docs/WINDOWS.md` 說明新版 CI 驗證結構。

## Capabilities

### New Capabilities

<!-- 無新增獨立 capability；由既有 desktop-verification 納入快取與 Docker 優先 CI 驗證要求 -->

### Modified Capabilities

- `desktop-verification`: 新增 Docker 優先快速 CI 驗證與手動跨平台／上游完整驗證分工的規範要求。

## Impact

- `.github/workflows/desktop.yml`
- `.github/workflows/full-release-matrix.yml`
- `docs/LOCAL_DEPLOYMENT.md`、`docs/WINDOWS.md`
- `scripts/deploy-production.ps1` 維持讀取 `desktop.yml` 成功紀錄，不需改動部署指令或破壞既有相容性。
