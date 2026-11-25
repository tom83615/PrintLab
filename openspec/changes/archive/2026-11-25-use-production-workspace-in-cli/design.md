# Design

## Context

正式版容器掛載兩個分離的宿主路徑：
- 外部資料空間（由 `%LOCALAPPDATA%\PrintLab\production\workspace-path.txt` 指定）提供 `Project`、`Context`、`Library`。
- 本機狀態目錄 `%LOCALAPPDATA%\PrintLab\production\Runtime` 提供 `config.json`、`locks/`、`private/`、`evidence/`、`workbench/`、`history/`。

但既有 `Harness/printlab` 假設單一 `core.ROOT` 同時包含程式碼（`Templates/`、`AGENTS.md`、`Harness/`）、資料（`Project/`、`Context/`、`Library/`）與 `Runtime/`。若只設定 `PRINTLAB_ROOT` 指向外部資料空間，會導致：
1. 找不到 `Templates/Project`、`AGENTS.md` 與 `Harness/build_model.py`。
2. 讀不到 `%LOCALAPPDATA%\PrintLab\production\Runtime\config.json` 與憑據，並意外在 OneDrive 資料夾內新建 `Runtime/` 與獨立檔案鎖。

## Decisions

- **分離三種根路徑並維持既有測試相容**：
  - `CODE_ROOT = Path(__file__).resolve().parents[2]`：提供程式碼資產（`Templates/Project`、`AGENTS.md`、`Harness/build_model.py` 等），以 `core.code_path(rel)` 優先讀取 `ROOT / rel`，不存在時回退到 `CODE_ROOT / rel`。
  - `ROOT`（來自 `PRINTLAB_ROOT`，預設 `CODE_ROOT`）：維持作為使用者資料根目錄（`Project/`、`Context/`、`Library/`）。
  - `core.runtime_root()`：當環境設有 `PRINTLAB_RUNTIME_ROOT` 且 `core.ROOT` 未被測試 monkeypatch 改動（`ROOT == _INITIAL_ROOT`）時，回傳 `Path(PRINTLAB_RUNTIME_ROOT).expanduser().resolve()`；否則回傳 `ROOT / "Runtime"`。所有讀取 `Runtime/` 的模組改經由 `core.runtime_root()`，確保單元測試 monkeypatch `core.ROOT` 時行為不變，且外部模式可與 Docker 容器共用同一份 `Runtime` 與檔案鎖。
- **在 CLI 輸出回報實際路徑**：
  - `core.context()`、`cli.py` 的 `status`、`core.doctor()` 皆明確輸出 `workspace_root` 與 `runtime_root`（`doctor` 保留既有 `root` 欄位並補充 `runtime_root`），讓任何 AI 執行一次 CLI 即可確認實際路徑。
- **Windows CLI 自動解析正式資料空間**：
  - `Harness/bin/printlab.ps1` 在 `$env:PRINTLAB_ROOT` 未設定時，檢查 `$env:LOCALAPPDATA\PrintLab\production\workspace-path.txt`；若存在且指向有效 Windows 資料夾，自動設定 `PRINTLAB_ROOT` 為該目錄，並在 `$env:PRINTLAB_RUNTIME_ROOT` 未設定時指向 `$env:LOCALAPPDATA\PrintLab\production\Runtime`。
  - 若外部測試或開發者顯式傳入 `PRINTLAB_ROOT`，`printlab.ps1` 不覆寫，完全保留既有隔離測試能力。
- **程式碼倉庫建立 `Workspace` 目錄聯結**：
  - 使用 Windows 目錄聯結（Directory Junction，無需管理員權限或開發人員模式）於倉庫根目錄建立 `Workspace` → 外部資料目錄，並在 `.gitignore` 加入 `/Workspace/`。
  - `scripts/deploy-production.ps1` 在 `$Workspace` 與程式碼倉庫根目錄不同時，自動建立或更新該 `Workspace` 聯結（若原有同名項目已是聯結則安全重建；若為一般實體資料夾則不誤刪）。
  - 選擇獨立的 `Workspace` 名稱而非覆蓋 `Project/`、`Context/`、`Library/`，避免與 Git 追蹤的 `Context/`、`Library/` 檔案衝突，也避免觸發 `safe_path()` 針對符號連結的跨目錄防護。

## Risks / Trade-offs

- **OneDrive 內的目錄聯結**：程式碼倉庫與外部資料空間皆位於 OneDrive 內，目錄聯結主要供本機編輯器、檔案總管與 AI 快速跳轉。已將 `/Workspace/` 加入 `.gitignore` 避免 Git 追蹤；若未來使用者將程式碼搬出 OneDrive，該聯結仍可無縫運作。
- **本機既有的過期資料**：倉庫 `Project/P001-PrintLab-小型列印驗收片` 與外部空間內容完全一致，移除倉庫副本並同步較新的 `Context/` 與參考文件至外部空間後，兩邊不再分叉。
