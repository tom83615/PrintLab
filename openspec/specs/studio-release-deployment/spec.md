# studio-release-deployment Specification

## Purpose

讓使用者在同一台電腦隔離開發測試與正式工作台，並在驗證版本後安全切換正式服務。

## Requirements

### Requirement: 開發與正式工作台隔離

工作台 SHALL 在本機 `8018` 提供原生 Windows 開發流程，並在 `10818` 提供 Docker 正式服務。開發入口 SHALL 讀寫共用正式資料，並省略建立獨立開發作品庫。

#### Scenario: 開發者存檔

- **WHEN** 開發者修改前端或 Python 程式
- **THEN** 開發工作台重新建置或重載，正式服務繼續執行其固定版本

#### Scenario: 正式容器重建

- **WHEN** 正式容器重新啟動或更新
- **THEN** 正式工作區資料仍可讀取，HTTP 連接埠僅在本機發布

#### Scenario: 開發者讀寫共用記錄

- **WHEN** 開發者開啟 `8018`
- **THEN** 開發工作台透過正式服務的 API 讀寫正式版本支援的資料，兩個入口的更新由同一個服務處理，保留來源與會話驗證

### Requirement: 正式服務版本切換

部署入口 SHALL 從固定提交建置、驗證候選服務，並提供回退。例行升級 SHALL 只使用 `tom83615` 通過 CI 的 push 提交。首次啟用可使用本機已提交且通過自動測試的版本。

#### Scenario: 例行升級

- **WHEN** 操作者指定通過 CI 的提交
- **THEN** 部署入口先驗證候選服務，再切換正式服務並驗證啟動

#### Scenario: 新版啟動失敗

- **WHEN** 正式服務切換後未通過驗證且有上一個版本
- **THEN** 部署入口還原上一個映像並驗證其服務

### Requirement: 正式資料位置可設定

正式部署 SHALL 使用本機設定指定作品、知識庫與脈絡資料的位置。Runtime、憑據與部署狀態 SHALL 留在獨立的本機資料目錄。

#### Scenario: 使用已搬移的正式資料

- **WHEN** 本機部署設定指定有效的正式資料位置
- **THEN** 目前服務及後續部署使用該資料位置，維持原有 Runtime 與版本狀態

#### Scenario: 使用預設位置

- **WHEN** 未設定正式資料位置
- **THEN** 部署沿用既有本機預設資料目錄

### Requirement: Windows CLI 與核心共用外部正式資料空間與獨立 Runtime

當本機已於 `%LOCALAPPDATA%\PrintLab\production\workspace-path.txt` 設定有效的外部正式資料目錄且呼叫端未顯式指定 `PRINTLAB_ROOT` 時，Windows CLI 入口（`Harness/bin/printlab.ps1`）SHALL 自動以該外部資料目錄作為 `PRINTLAB_ROOT`，並以 `%LOCALAPPDATA%\PrintLab\production\Runtime` 作為 `PRINTLAB_RUNTIME_ROOT`。Python 核心在資料根目錄與程式碼或 Runtime 分離時，SHALL 從程式碼根目錄回退讀取 `Templates`、`AGENTS.md` 與工具腳本，從 `PRINTLAB_RUNTIME_ROOT` 讀寫鎖、設定、憑據與執行證據，且 SHALL 於 `context`、`status` 與 `doctor` 輸出中明確回報實際生效的 `workspace_root` 與 `runtime_root`。

#### Scenario: 未覆寫 PRINTLAB_ROOT 且本機已有正式資料設定

- **WHEN** 使用者或 AI 在程式碼倉庫執行 `Harness/bin/printlab.ps1` 且未設定 `PRINTLAB_ROOT`，且 `%LOCALAPPDATA%\PrintLab\production\workspace-path.txt` 指向存在的 Windows 目錄
- **THEN** CLI 以該外部目錄讀寫 `Project`、`Context` 與 `Library`，以 `%LOCALAPPDATA%\PrintLab\production\Runtime` 讀寫 `config.json`、鎖與執行記錄，且不在外部資料目錄內建立 `Runtime`

#### Scenario: 呼叫端顯式指定 PRINTLAB_ROOT

- **WHEN** 測試或自動化腳本以環境變數顯式傳入 `PRINTLAB_ROOT`
- **THEN** CLI 保留呼叫端指定的 `PRINTLAB_ROOT`，未設定 `PRINTLAB_RUNTIME_ROOT` 時沿用該目錄底下的 `Runtime`

#### Scenario: 跨分離目錄建立新專案與讀取上下文

- **WHEN** `PRINTLAB_ROOT` 指向不含程式碼與模板的外部資料目錄，且 `PRINTLAB_RUNTIME_ROOT` 指向獨立 Runtime 目錄
- **THEN** `new` 仍能從程式碼倉庫讀取 `Templates/Project`，`context` 能從程式碼倉庫回退讀取 `AGENTS.md` 且回報 `workspace_root` 與 `runtime_root`

### Requirement: 程式碼倉庫提供指向外部正式資料空間的連結與 AI 發現指引

當正式資料目錄位於程式碼倉庫外部時，部署與本機環境 SHALL 支援在程式碼倉庫根目錄維護受 `.gitignore` 忽略的 `Workspace` 目錄聯結指向該外部正式資料目錄。工作區說明文件（`AGENTS.md`、PrintLab 技能與部署文件）SHALL 明確記錄正式資料位置的探索順序（`PRINTLAB_ROOT`、`workspace-path.txt`、`Workspace` 連結與 CLI 狀態回報），確保即使程式碼倉庫內不存在本機專案檔，AI 仍能準確定位與操作唯一正式資料空間。

#### Scenario: 程式碼倉庫不含本機作品檔時的 AI 探索

- **WHEN** AI 在程式碼倉庫啟動且倉庫的 `Project/` 內沒有作品檔
- **THEN** AI 可依指引讀取 `%LOCALAPPDATA%\PrintLab\production\workspace-path.txt`、透過倉庫根目錄 `Workspace` 連結存取，或執行 `printlab.ps1 status` / `context` 取得實際 `workspace_root`

#### Scenario: 正式部署維持外部資料連結

- **WHEN** 在外部資料目錄模式下執行 `scripts/deploy-production.ps1`
- **THEN** 腳本在程式碼倉庫根目錄建立或更新指向該外部正式資料目錄的 `Workspace` 目錄聯結，且該連結受 `.gitignore` 忽略、不影響 Git 追蹤
