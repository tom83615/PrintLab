# PrintLab · Agent workspace guide

本倉庫面向 Mac / Windows、Codex 與拓竹印表機。執行使用者當前要求，先核對事實和專案狀態，再選最簡單可行的方法。

## 首次安裝

先讀 `docs/AGENT_START.md`，按其中步驟完成接手、安裝、驗證與角色建立。具體安裝見 `docs/SETUP.md`，第三方來源見 `docs/DEPENDENCIES.md`，設備適配見 `docs/PRINTING.md`。Agent 在使用者授權範圍內從原作者渠道獨立下載和安裝第三方工具，記錄版本與驗證結果。安裝程序會從 PyPI/npm 獲取工作台的軟體依賴。

工作區根目錄區分為「程式碼倉庫」（當前 checkout）與「外部設計資料空間」。CLI 是 `./Harness/bin/printlab`（Windows 為 `Harness/bin/printlab.ps1`），每次用當前 `--help` 確認參數。已有模型、工具環境和使用者設定優先接續。

### 設計資料空間定位（即使倉庫內沒有本機作品檔）

當本機已設定正式獨立資料空間時，所有設計作品與個人紀錄（`Project/`、`Context/`、`Library/`）一律存在該外部空間，程式碼倉庫內不會保留本機作品副本。AI 開始設計或查詢專案前，**必先確認實際資料根目錄**：

1. 若環境變數已設定 `PRINTLAB_ROOT`，以該目錄為準。
2. 檢查 Windows 正式資料設定檔 `%LOCALAPPDATA%\PrintLab\production\workspace-path.txt`（對應本機 Runtime 位於 `%LOCALAPPDATA%\PrintLab\production\Runtime`）。
3. 程式碼倉庫根目錄的外部連結 `Workspace/`（Windows 目錄聯結，指向同一外部資料空間；受 `.gitignore` 忽略）。
4. 執行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\Harness\bin\printlab.ps1 status` 或 `context`：`printlab.ps1` 在未覆寫 `PRINTLAB_ROOT` 時會自動解析上述正式資料空間，並在輸出 JSON 明確回報 `workspace_root` 與 `runtime_root`。

確認存在外部資料空間後，所有專案建立、模型檔、預覽、切片、交接與 `Context/`、`Library/` 讀寫皆須在 `workspace_root`（或透過 `Workspace/` 連結與 CLI）進行，不得在程式碼倉庫的 `Project/` 下建立第二份專案庫。

The code repository is this checkout. On Windows, `Harness/bin/printlab.ps1` automatically resolves the configured external design workspace from `%LOCALAPPDATA%\PrintLab\production\workspace-path.txt` (and pairs it with `%LOCALAPPDATA%\PrintLab\production\Runtime`) unless `PRINTLAB_ROOT` is explicitly overridden, and the repository root provides a git-ignored `Workspace/` link pointing to that external directory. Check `printlab status` / `printlab context` (`workspace_root`) and `--help` before acting. Continue existing models, environments and user configuration.

1. 從實際 `workspace_root` 讀 `Context/profile.md`、`Context/workflow.md`、`Context/agent-policy.json`、`Context/taste.md` 和 `Library/Devices/H2C/device.json`。初始化後這些文件纔會齊備。
2. 目標專案從實際 `workspace_root` 讀 `project.json`、`brief.md`、`decisions.md` 和 `latest_session` 指向的交接。`printlab context 專案` 彙集同一份資料並回報 `workspace_root`。
3. 報告專案、當前版本、已確認選擇、尚待驗證的部分與本輪下一步。
4. 收尾用 `printlab handoff` 儲存完成結果、檢查、問題和下一步。查看當前幫助確認參數。

## 開啟 PrintLab

- 使用者要求開啟、查看或操作 PrintLab 時，預設開啟已部署的正式版 `http://localhost:10818/`。開啟瀏覽器或預覽前，先核對正式版服務與實際綁定的埠。
- `8018` 僅用於修改、除錯或驗證 PrintLab 程式碼。正式版無法連線時，先檢查正式版部署與服務狀態，不得改開 `8018` 或啟動 `scripts/start-dev.ps1` 作為替代。

## 分工與持久化

Sarah 負責設備、材料、故障和配件。Mike 負責工作台、工具和流程。Chloe 負責 MakerWorld 等模型網站上架、生成描述文案、展示圖片規劃與適合分享的檔案形式（MakerWorld 上傳規則與限制見 `docs/ROLES.md` 與 `.agents/skills/makerworld-upload/SKILL.md`）。Leo 負責協助修圖、裁切構圖、調整光線色彩與版面設計，製作作品展示圖與視覺素材（規範見 `docs/ROLES.md`）。任務小組負責具體作品。提示詞見 `docs/ROLES.md`。角色通過共同文件和命令協作，模型選擇由使用者當前可用的 Codex 環境決定。只有使用者明確要求時才建立新會話或派發子 Agent。

初始化生成 `Context/team.md`，保留實際團隊說明。可恢復的首次設定、角色入口及讀回證據儲存在 `Context/onboarding.json`。按 `docs/ONBOARDING.md` 查詢已有聊天、建立缺少的 Mike、Sarah、Chloe 與 Leo，讀回實際首條介紹與共用資料。已有 Sara 入口接續為同一角色。使用者的安裝請求已經明確包含自動建隊時直接執行，宿主能力缺失時記錄真實待辦。專案分工繼續寫 `Review/team.md`。

共同文件的追加使用 `workspace note`，設備確認使用 `workspace device`，均帶當前哈希並在衝突後重讀。使用者確認的庫存通過 `material-intake` 登記到工作區設定的庫存來源（Spoolman 或 Bambuddy）。生圖前執行 `constraints capture 專案ID` 儲存本次設備材料及需求來源；CAD 和切片前通過 `context` 檢查變化，按實際影響更新設計資料。未知欄位保留待核實。

- `Context/` 存流程、偏好和經驗，偏好依據使用者明確回饋。
- `Project/` 存需求、源模型、候選、正式版本、切片、回執和實物覆盤。
- `Library/` 存使用者的設備、材料知識、靈感和來源。
- `Templates/Project/` 是新專案模板。
- `Runtime/` 存本機設定、憑據、緩存與第三方執行環境。

使用者資料與憑據始終在本機維護。修改倉庫原始碼時，檢查 Git 暫存區，避免提交真實設備資訊、聊天和個人資料。

## OpenSpec 開發變更流程

- 修改程式碼前，先在 `openspec/changes/` 建立一份或多份對應的 OpenSpec change，完成並檢視 proposal、specs 與 tasks；OpenSpec 文件未就緒前不得修改程式碼。
- 每個 change 對應一組範圍一致的程式修改。工作範圍彼此獨立時分開建立 change；同一範圍的後續工作沿用既有 change，不重複建立。
- 實作時依 tasks 推進，若需求或範圍改變，先更新 OpenSpec artifacts，再繼續修改程式碼。
- commit 前，所有納入該 commit 的 OpenSpec change 必須完成並 archive；archive 產生的規格更新與封存記錄，必須和對應程式碼放在同一個 commit。未完成或未 archive 的 change 不得與程式碼一同 commit。
- 純文件編輯不要求建立 OpenSpec；若文件變更伴隨程式碼修改，仍須遵循以上流程。

## Git 分支與推送

- 所有開發提交一律建立在 `tom83615` 分支。
- 只可推送至 GitHub 使用者 `tom83615` 名下的倉庫。
- `git@github.com:AFangTeam/PrintLab.git` 僅作為讀取用 upstream；絕對禁止向 `github.com/AFangTeam` 推送。
- 推送前確認目前分支為 `tom83615`，且目的地是 `github.com/tom83615`。

## 設計與列印

每一輪建立或修改模型前，先依作品的外形與配合需求，和使用者確認採用參數化 CAD 或 Blender 表面建模。本輪已明確指定時直接記錄並執行，否則等使用者選擇後才開始草模或修改幾何。選擇記入專案 `decisions.md`。詳見 [建模流程](Context/workflow.md#實際建模)。

遵循 `Context/image-to-print.md`，新外形兩次選圖後進入正式模型。真實模型按選定外形比較，介面、公差、裝入路徑、壁厚和承力分別檢查。保留可編輯源，試模與成品共用介面參數，詳見 `Context/cad-master-design.md`。

每次最終製作檢查品質、可靠性、列印總時間、支撐、材料切換和後處理。記錄實際切片比較，模板見 `Templates/Project/Review/x2d-final-review.md`。

切片完成後，提供切片檔與結果摘要，將下一步記為等待使用者回饋。本階段省略建立回執和送印；收到明確的列印要求後才進入送印流程。

Windows 無 Bambuddy 的官方 Studio 手動路線由 Agent 準備並預檢正式切片。使用者在 Studio 核對後直接按「送出」。跳過 `submit --execute`、限時預約及送印前回執。送印後取得相符的 Studio 任務名稱與結果時，再由 Agent 對帳。

列印批准綁定具體模型版本、切片文件與設備身份，使用 `printlab approve / submit / reconcile` 的同一任務記錄。材料/設備就緒/清板/列印授權的逐任務確認不是必要條件，缺少或過期不得單獨阻擋。使用者仍須主動啟動送印；實際離線、忙碌、故障、明確等待清板、檔案損壞及結果不明任務仍須處理。首次設定、建模、切片、測試均保持無設備動作。結果不明先對賬，避免重複發送。官方 Studio 路線見 `Context/official-studio-dispatch.md`。

設備完成後進入實物檢查。使用者確認配合、外觀、強度或使用體驗後，再登記驗收結果。

## 第三方來源與發佈

遵循 `docs/DEPENDENCIES.md`。第三方程式碼、技能、權重、作者模型、應用及外掛程式從原作者處獨立取得，保留作者和原許可。PrintLab 自己的非商用許可僅覆蓋原創程式碼和文件。發佈模型是使用者另外提出的任務，逐件核對來源與許可。

## 既有終端與帳號同步

安裝先記錄使用者正在使用的 Handy、Studio、Bambu Cloud 和 MakerWorld 功能，保留其帳號登入、網路模式與現有憑據權限。為 PrintLab 新建專用讀取憑據。使用者需要雲功能時，先說明 LAN Only / Developer Mode 的具體影響並確認所選路線。按 `docs/SYNC_TROUBLESHOOTING.md` 核對歷史與收藏的實際來源及覆蓋時間，核對原應用功能仍然可用。帳號舊歷史和 MakerWorld 收藏匯入已排除在本輪開發範圍外。已有檔案缺圖時，按 `docs/PREVIEW_RECOVERY.md` 使用 `printlab history-recover`，記錄來源和恢復數量。
