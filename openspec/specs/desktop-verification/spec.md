# desktop-verification Specification

## Purpose

桌面驗證以可重現的合成資料檢查送印核准、設備檢查、一次性啟動及結果不明時的行為，涵蓋現行工作流程和仍受支援的歷史記錄。

## Requirements

### Requirement: 桌面送印回歸驗證

桌面回歸測試 SHALL 依目前的核准及送印契約驗證一般工作流程、實際設備的阻擋訊號與歷史清板證據，並使用模擬傳輸。

#### Scenario: 缺少一般逐任務確認
- **WHEN** 合法的核准或啟動請求缺少逐任務清板確認
- **THEN** 測試驗證請求可繼續並保留檔案綁定及一次性啟動驗證

#### Scenario: 設備待清板或舊任務狀態不明
- **WHEN** 模擬設備回報待清板或存在未完成對帳的狀態
- **THEN** 測試驗證工作流程保持阻擋，且沒有送出新指令

#### Scenario: 既有核准含清板證據
- **WHEN** 測試取消後重印或具有明確簽名拒絕證據的歷史任務
- **THEN** 測試以既有記錄格式提供清板證據，並驗證檔案、時效、身份與原回執

### Requirement: Docker 優先快速 CI 驗證

例行 push 與 pull request 的 CI 工作流（`.github/workflows/desktop.yml`）SHALL 以並行方式驗證正式 `Dockerfile` 容器映像、Linux 全套自動化與瀏覽器測試，以及 Windows 宿主機工具鏈，且 SHALL 使用依賴與容器層快取縮短執行時間。工作流檔名 SHALL 維持 `desktop.yml` 以相容既有正式部署檢查。

#### Scenario: 例行 push 驗證正式 Docker 映像
- **WHEN** 開發者推送提交或建立 pull request 觸發 `desktop.yml`
- **THEN** `docker-verify` 在 `ubuntu-latest` 上使用 Buildx 與 GHA 快取建置正式 `Dockerfile` 映像，啟動容器驗證 `/api/health`、首頁前端 JavaScript 資產、容器內 CLI `status` 與容器執行期 pytest 子集

#### Scenario: 例行 push 驗證 Linux 完整測試與瀏覽器介面
- **WHEN** `desktop.yml` 在 `ubuntu-latest` 執行 `linux-verify`
- **THEN** 工作流使用 pip、npm 與 Playwright 快取安裝依賴，執行完整 `Harness/tests`、跳過重型上游下載的 `verify_onboarding.py`、`native-inspection.test.mjs` 及真實 Chromium 瀏覽器驗收

#### Scenario: 例行 push 驗證 Windows 宿主機核心工具鏈
- **WHEN** `desktop.yml` 在 `windows-2025`（Python `3.13`）執行 `windows-host-verify`
- **THEN** 工作流使用 pip 與 npm 快取執行 `scripts/setup.ps1`、Windows 宿主機專屬測試（PowerShell 入口、外部正式資料空間解析、ACL、UTF-8 與備份恢復）及跳過重型上游下載的 `verify_onboarding.py`，且不在例行 push 重複執行 macOS、`windows-2022` 或上游第三方安裝下載

### Requirement: 按需跨平台與上游完整安裝驗證

倉庫 SHALL 提供獨立的手動觸發工作流（`.github/workflows/full-release-matrix.yml`），讓維護者在升級第三方依賴或向上游提交變更前按需執行完整跨平台（Windows 與 macOS）及上游工具安裝驗證。

#### Scenario: 維護者手動觸發完整跨平台驗證
- **WHEN** 維護者透過 `workflow_dispatch` 觸發 `full-release-matrix.yml`
- **THEN** 工作流於 Windows 與 macOS 執行完整安裝、pytest、含上游工具下載（ZIP 封包重裝、Text-to-CAD、Bambuddy、Bambu Studio 與 macOS StudioBridge）的 `verify_onboarding.py`、Node 檢查測試與瀏覽器驗收
