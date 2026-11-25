# Proposal

## Why

目前正式版 Docker 工作台已改為透過 `%LOCALAPPDATA%\PrintLab\production\workspace-path.txt` 指向獨立的外部資料空間，但 Windows 本機 CLI（`Harness/bin/printlab.ps1`）與 Python 核心仍預設把程式碼倉庫根目錄當作資料與 Runtime 位置。這會導致設計與交接檔案寫進程式碼倉庫，與正式版網頁看到的資料分裂，也讓沒有在倉庫內看到本機作品檔的 AI 無法自動定位正式資料空間。

## What Changes

- 讓 `Harness/printlab` 支援分離程式碼根目錄、資料根目錄（`PRINTLAB_ROOT`）與本機 Runtime 根目錄（`PRINTLAB_RUNTIME_ROOT`），並在 `context`、`status`、`doctor` 回報實際生效的 `workspace_root` 與 `runtime_root`。
- 讓 Windows CLI 入口 `Harness/bin/printlab.ps1` 在未顯式指定 `PRINTLAB_ROOT` 且本機已設定有效的正式 `workspace-path.txt` 時，預設指向該外部正式資料空間，並共用 `%LOCALAPPDATA%\PrintLab\production\Runtime`。
- 在正式部署腳本 `scripts/deploy-production.ps1` 中維護程式碼倉庫內的外部連結 `Workspace`（Windows 目錄聯結，指向外部正式資料目錄）並將 `/Workspace/` 加入 `.gitignore`。
- 更新 `AGENTS.md`、`.agents/skills/printlab/SKILL.md` 與 `docs/LOCAL_DEPLOYMENT.md`，明確說明即使程式碼倉庫內沒有本機作品檔，AI 應如何定位外部正式資料空間、使用 `Workspace` 連結與 CLI 自動解析結果。

## Capabilities

### New Capabilities

### Modified Capabilities

- `studio-release-deployment`：新增 Windows CLI 預設解析正式資料位置與獨立 Runtime、回報生效路徑，以及在程式碼倉庫維護指向外部正式資料空間的連結。

## Impact

- `Harness/printlab/core.py`、`Harness/printlab/cli.py` 及相關讀取 `Runtime` 路徑的模組。
- `Harness/bin/printlab.ps1`、`scripts/deploy-production.ps1`、`.gitignore`。
- `AGENTS.md`、`.agents/skills/printlab/SKILL.md`、`docs/LOCAL_DEPLOYMENT.md`。
- 自動化測試（`Harness/tests/`）。
