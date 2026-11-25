---
name: printlab
description: 安裝或使用 PrintLab 3D 列印工作台，接續作品的設計、材料、切片、待列印任務和實物回饋。用於使用者要求設定 PrintLab、讓 Agent 設計可列印作品或接續已有 PrintLab 專案時。
license: PolyForm Noncommercial 1.0.0; see the PrintLab repository LICENSE.md and NOTICE.txt.
---

需要本機文件與終端能力；工作台支援 macOS 和 Windows。CAD、設備連接及發送支援按實際安裝和機型核驗。

找到使用者實際的 PrintLab 程式碼根目錄，特徵為 AGENTS.md、Harness/printlab 和 Context/workflow.md。若本機已設定外部正式資料空間（Windows 見 `%LOCALAPPDATA%\PrintLab\production\workspace-path.txt`，程式碼根目錄亦設有 `Workspace/` 聯結指向該處），即使程式碼倉庫的 `Project/` 內沒有本機作品檔，也必須以該外部空間作為唯一設計資料空間；不要在程式碼倉庫內建立第二份專案庫。Windows CLI（`Harness/bin/printlab.ps1`）未顯式覆寫 `PRINTLAB_ROOT` 時會自動解析該外部資料空間與 `%LOCALAPPDATA%\PrintLab\production\Runtime`，並於 `status` / `context` / `doctor` 回報 `workspace_root` 與 `runtime_root`。若技能單獨安裝而工作台尚未安裝，從 https://github.com/AFangTeam/PrintLab 的明確 Release 開始，記錄版本，按其 README 安裝。

程式碼與規則文件路徑相對程式碼根目錄；使用者專案、脈絡與設備知識（`Project/`、`Context/`、`Library/`）一律相對 `workspace_root`（未設定外部空間時即為程式碼根目錄）。

- 首次安裝：讀取 README.md、AGENTS.md、docs/AGENT_START.md、docs/ONBOARDING.md。先識別系統和缺少的前提，執行對應 setup/start 腳本；外部工具從原作者獨立安裝。不要假定 ChatGPT 有本機執行或聊天管理能力。
- 自動建隊與首次訪談：使用者的安裝請求包含建立角色時，按 docs/ONBOARDING.md 執行宿主工具探測、已有入口查詢、預留與真實建立、首條介紹讀回。新角色使用 Mike、Sarah 與 Chloe，已有 Sara 接續。主 Agent 讀取設備、已裝材料和庫存，只問真實缺項。
- 開始設計或接續：讀取 Context/profile.md、Context/workflow.md、設備檔案；執行當前 CLI 的 --help 和 context，按 project.json 的 latest_session 繼續原專案。新作品先了解用途、尺寸、設備、材料和驗收標準。生圖前用 constraints capture 儲存實際來源，進入 CAD/切片前從 context 核對設備材料或需求變化。
- 外形、CAD、切片：按 Context/image-to-print.md 和 Context/cad-master-design.md 繼承已選方案；真實源模型匯出預覽，關鍵介面與實測獨立核對。依據當前機器比較列印方向、材料、支撐、分盤及完整工時。
- 切片交付：提供切片檔、版本、分盤、預估時間和用量，在交接記錄等待使用者回饋。此階段省略建立回執、加入待列印列表和送印。
- 列印：收到使用者明確要求後，先讀 docs/PRINTING.md，經工作台/CLI 的統一批准和發送入口綁定具體模型版本、切片文件與設備。結果未知先對賬，不自動重發；不借第三方外掛程式繞過 PrintLab 檢查。
- Windows 無 Bambuddy 的官方 Studio 手動列印由 Agent 準備和預檢正式檔案。使用者在 Studio 直接按「送出」，跳過 `submit --execute` 和送印前回執。送印後由 Agent 依相符的 Studio 任務名稱與實際結果對帳。
- 共同記錄：使用 workspace 命令的哈希檢查追加偏好、事實與經驗，衝突後重讀。使用者確認擁有的其他耗材通過 material-intake 寫入已設定的庫存來源；Spoolman 可用 --preview 先核對品項，超時後使用相同請求標識對賬。
- 交接：用 CLI handoff 儲存完成項、當前版本、證據、未知項與下一步，再通過 context 讀回。設備已結束不等於實物合格。

Mac CLI：`./Harness/bin/printlab`。Windows CLI：`powershell -NoProfile -ExecutionPolicy Bypass -File .\Harness\bin\printlab.ps1`。先查當前幫助再選擇參數。

報告實際工作區、啟動地址、工具版本、已驗證能力和下一步。區分軟體實測、模擬設備測試、實機驗證；缺少能力應報告具體安裝或設定步驟，不寫成已完成。

## 既有終端與帳號同步

安裝先記錄使用者正在使用的 Handy、Studio、Bambu Cloud 和 MakerWorld 功能，保留其帳號登入、網路模式與現有憑據權限。為 PrintLab 新建專用讀取憑據。使用者需要雲功能時，先說明 LAN Only / Developer Mode 的具體影響並確認所選路線。按 `docs/SYNC_TROUBLESHOOTING.md` 核對歷史與收藏的實際來源及覆蓋時間，核對原應用功能仍然可用。帳號舊歷史和 MakerWorld 收藏匯入已排除在本輪開發範圍外。已有檔案缺圖時，按 `docs/PREVIEW_RECOVERY.md` 使用 `printlab history-recover`，記錄來源和恢復數量。
