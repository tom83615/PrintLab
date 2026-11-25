# Tasks

## 1. 核心路徑分離與路徑回報

- [x] 1.1 在 `Harness/printlab/core.py` 加入 `CODE_ROOT`、`code_path()` 與 `runtime_root()`（支援 `PRINTLAB_RUNTIME_ROOT` 並相容測試對 `core.ROOT` 的 monkeypatch），修正 `new_project`、`context`、`build`、`doctor`、`lock`、`config` 路徑解析，並在 `context`、`status`、`doctor` 回報 `workspace_root` 與 `runtime_root`。
- [x] 1.2 更新 `bambuddy.py`、`history.py`、`makerworld.py`、`prepared_api.py`、`queue_sender.py`、`studio_bridge.py`、`workbench.py`、`workspace.py` 統一透過 `core.runtime_root()` 讀寫 `Runtime` 檔案。

## 2. Windows CLI、外部連結與部署整合

- [x] 2.1 更新 `Harness/bin/printlab.ps1`，未指定 `PRINTLAB_ROOT` 且本機 `workspace-path.txt` 有效時，自動設定 `PRINTLAB_ROOT` 與 `PRINTLAB_RUNTIME_ROOT`。
- [x] 2.2 更新 `scripts/deploy-production.ps1` 與 `.gitignore`，於外部資料目錄模式下在程式碼倉庫根目錄維護指向外部資料空間的 `Workspace` 目錄聯結並忽略 `/Workspace/`。

## 3. AI 指引與工作區同步

- [x] 3.1 更新 `AGENTS.md`、`.agents/skills/printlab/SKILL.md` 與 `docs/LOCAL_DEPLOYMENT.md`，說明唯一外部資料空間、AI 探索順序與 `Workspace` 連結。
- [x] 3.2 將倉庫較新的 `Context/` 與 `Library/` 參考文件同步至外部正式資料空間，清理倉庫內重複的 `Project/` 專案副本，並在程式碼倉庫建立 `Workspace` 目錄聯結。

## 4. 驗證與測試

- [x] 4.1 撰寫自動化測試驗證分離資料/Runtime 根目錄、`printlab.ps1` 自動解析與顯式覆寫行為，並執行現有測試套件與實機 CLI 驗證。
