# PrintLab · Codex 工作入口

本倉庫面向 Mac / Windows、Codex 與拓竹印表機。執行使用者當前要求，先核對事實和專案狀態，再選最簡單可行的方法。

## 首次安裝

先讀 `docs/AGENT_START.md`，按其中步驟完成接手、安裝、驗證與角色建立。具體安裝見 `docs/SETUP.md`，第三方來源見 `docs/DEPENDENCIES.md`，設備適配見 `docs/PRINTING.md`。Agent 在使用者授權範圍內從原作者渠道獨立下載和安裝第三方工具，記錄版本與驗證結果。安裝程序會從 PyPI/npm 獲取工作台的軟體依賴。

工作區根目錄為當前 checkout。CLI 是 `./Harness/bin/printlab`，每次用當前 `--help` 確認參數。已有模型、工具環境和使用者設定優先接續。

## 每次接手

1. 讀 `Context/profile.md`、`Context/workflow.md`、`Context/agent-policy.json`、`Context/taste.md` 和 `Library/Devices/X2D/device.json`。初始化後這些文件纔會齊備。
2. 目標專案讀 `project.json`、`brief.md`、`decisions.md` 和 `latest_session` 指向的交接。`printlab context 專案` 彙集同一份資料。
3. 報告專案、當前版本、已確認選擇、尚待驗證的部分與本輪下一步。
4. 收尾用 `printlab handoff` 儲存完成結果、檢查、問題和下一步。查看當前幫助確認參數。

## 分工與持久化

Sarah 負責設備、材料、故障和配件。Mike 負責工作台、工具和流程。任務小組負責具體作品。提示詞見 `docs/ROLES.md`。角色通過共同文件和命令協作，模型選擇由使用者當前可用的 Codex 環境決定。只有使用者明確要求時才建立新會話或派發子 Agent。

初始化生成 `Context/team.md`，保留實際團隊說明。可恢復的首次設定、角色入口及讀回證據儲存在 `Context/onboarding.json`。按 `docs/ONBOARDING.md` 查詢已有聊天、建立缺少的 Mike 和 Sarah，讀回實際首條介紹與共用資料。已有 Sara 入口接續為同一角色。使用者的安裝請求已經明確包含自動建隊時直接執行，宿主能力缺失時記錄真實待辦。專案分工繼續寫 `Review/team.md`。

共同文件的追加使用 `workspace note`，設備確認使用 `workspace device`，均帶當前哈希並在衝突後重讀。使用者確認的庫存通過 `material-intake` 登記到 Bambuddy。生圖前執行 `constraints capture 專案ID` 儲存本次設備材料及需求來源；CAD 和切片前通過 `context` 檢查變化，按實際影響更新設計資料。未知欄位保留待核實。

- `Context/` 存流程、偏好和經驗，偏好依據使用者明確回饋。
- `Project/` 存需求、源模型、候選、正式版本、切片、回執和實物覆盤。
- `Library/` 存使用者的設備、材料知識、靈感和來源。
- `Templates/Project/` 是新專案模板。
- `Runtime/` 存本機設定、憑據、緩存與第三方執行環境。

使用者資料與憑據始終在本機維護。修改倉庫原始碼時，檢查 Git 暫存區，避免提交真實設備資訊、聊天和個人資料。

## Git 分支與推送

- 所有開發提交一律建立在 `tom83615` 分支。
- 只可推送至 GitHub 使用者 `tom83615` 名下的倉庫。
- `git@github.com:AFangTeam/PrintLab.git` 僅作為讀取用 upstream；絕對禁止向 `github.com/AFangTeam` 推送。
- 推送前確認目前分支為 `tom83615`，且目的地是 `github.com/tom83615`。

## 設計與列印

遵循 `Context/image-to-print.md`，新外形兩次選圖後進入正式模型。真實模型按選定外形比較，介面、公差、裝入路徑、壁厚和承力分別檢查。保留可編輯源，試模與成品共用介面參數，詳見 `Context/cad-master-design.md`。

每次最終制作檢查品質、可靠性、列印總時間、支撐、材料切換和後處理。記錄實際切片比較，模板見 `Templates/Project/Review/x2d-final-review.md`。

列印授權綁定具體模型版本、切片文件、設備、材料與當次清板事實。使用 `printlab approve / submit / reconcile` 的同一任務記錄。首次設定、建模、切片、測試均保持無設備動作。準備發送時先核對已有任務，結果不明先對賬，避免重複發送。官方 Studio 路線見 `Context/official-studio-dispatch.md`。

設備完成後進入實物檢查。使用者確認配合、外觀、強度或使用體驗後，再登記驗收結果。

## 第三方來源與發佈

遵循 `docs/DEPENDENCIES.md`。第三方程式碼、技能、權重、作者模型、應用及外掛程式從原作者處獨立取得，保留作者和原許可。PrintLab 自己的非商用許可僅覆蓋原創程式碼和文件。發佈模型是使用者另外提出的任務，逐件核對來源與許可。

## 既有終端與帳號同步

安裝先記錄使用者正在使用的 Handy、Studio、Bambu Cloud 和 MakerWorld 功能，保留其帳號登入、網路模式與現有憑據權限。為 PrintLab 新建專用讀取憑據。使用者需要雲功能時，先說明 LAN Only / Developer Mode 的具體影響並確認所選路線。按 `docs/SYNC_TROUBLESHOOTING.md` 核對歷史與收藏的實際來源及覆蓋時間，核對原應用功能仍然可用。帳號舊歷史和 MakerWorld 收藏匯入已排除在本輪開發範圍外。已有檔案缺圖時，按 `docs/PREVIEW_RECOVERY.md` 使用 `printlab history-recover`，記錄來源和恢復數量。
