# Tasks

## 1. 重構主 CI 工作流（Docker 優先 + 輕量 Windows）

- [x] 1.1 更新 `.github/workflows/desktop.yml`，拆分為 `docker-verify`、`linux-verify` 與 `windows-host-verify` 三個並行 job，加入 Buildx / pip / npm / Playwright 快取與 artifact 保留天數限制，並驗證 YAML 語法與結構正確。
- [x] 1.2 在本機驗證 `docker-verify` 的核心指令（Docker 建置、容器 `/api/health` 與前端資產檢查、容器內 CLI `status` 與容器內 pytest 子集）以及 `windows-host-verify` 的精選 Windows 測試指令皆可通過。

## 2. 新增按需跨平台與上游完整驗證工作流

- [x] 2.1 建立 `.github/workflows/full-release-matrix.yml`（僅 `workflow_dispatch` 觸發），包含 `windows-2025` 與 `macos-latest` 完整驗證（含四個上游安裝驗證與 Playwright），並驗證 YAML 語法正確。

## 3. 更新部署與 CI 文件

- [x] 3.1 更新 `docs/LOCAL_DEPLOYMENT.md` 與 `docs/WINDOWS.md` 中對 `desktop.yml` 與手動完整驗證工作流的說明，並確認敘述與實際工作流設定一致。

## Workflow follow-up

- 完成所有任務與驗證後，將 `optimize-ci-docker-first` 封存（archive）並更新主規格 `openspec/specs/desktop-verification/spec.md`。
