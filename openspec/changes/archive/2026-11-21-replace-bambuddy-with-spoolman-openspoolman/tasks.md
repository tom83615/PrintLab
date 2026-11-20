# Tasks

## 1. 完成 Spoolman 庫存適配

- [x] 1.1 核對既有 Spoolman 讀取與本機服務設定，補齊錯誤、未知餘量及來源標示；以服務回應和單元測試驗證 active spool 對映，並更新連接說明。
- [x] 1.2 完成料卷預覽、重量驗證、冪等寫入與讀回對帳；以 mock/API 測試驗證不會重複新增或修改目錄/耗用量，更新材料登記 CLI 說明。

## 2. 完成 OpenSpoolMan 快照適配

- [x] 2.1 核對部署版本是否提供穩定的唯讀 API 與觀察時間；若無，固定支援的頁面資料形狀並拒絕未知格式，以實際唯讀回應和解析測試驗證結果。
- [x] 2.2 將設備、AMS 槽位、空槽及 Spoolman ID 連結整理成具來源與可信邊界的快照；以重複 ID、未知欄位及來源不可用案例測試，更新 onboarding 和狀態說明。

## 3. 移除 Bambuddy 的材料與設備流程必要性

- [x] 3.1 將 inventory、onboarding、製造條件與工作台來源選擇統一到 Spoolman/OpenSpoolMan；以設定單一或兩個來源的整合測試驗證不會靜默讀取 Bambuddy，更新設定文件。
- [x] 3.2 將材料、設備與列印歷史介面標出實際來源和資料新鮮度，保留 OpenSpoolMan 原生歷史入口；以工作台建置與 API 回應驗證來源標籤和錯誤狀態。

## 4. 解除列印流程對 Bambuddy 佇列的依賴

- [x] 4.1 加入本機 Studio 印表機名稱、機型與序號綁定，讓無 Bambuddy 的官方 Studio 任務使用該穩定身份；以身份缺漏、變更和無服務設定案例驗證任務不會錯綁。
- [x] 4.2 將 Windows 官方 Studio 定為手動交接；批准前要求當次任務的設備就緒、料路已核驗、材料已裝、清板及列印授權證據。以只有 OpenSpoolMan 快照或缺任一事實案例驗證被阻擋。
- [x] 4.3 為無 Bambuddy 任務提供只記錄使用者觀察的對帳入口；保留既有 Bambuddy 任務回執，不自動轉換或重送。以未知發送結果和錯誤任務名案例驗證不會建立第二次發送，更新 Windows 列印說明。

## 5. 全流程整合驗收

- [x] 5.1 以 Spoolman 與 OpenSpoolMan 設定執行 onboarding、庫存讀取、料卷 preview 和任務預檢整合驗收；確認沒有任何列印或庫存寫入動作。
- [x] 5.2 搜尋程式、CLI 和文件中殘留的 Bambuddy 必要依賴，逐項確認只作為既有任務相容／遷移資訊或已移除；執行 OpenSpec 驗證並記錄結果。

## 驗收記錄

- 2026-11-21：本機唯讀整合讀到 Spoolman 33 卷、OpenSpoolMan H2C 10 槽快照（來源標為 stale）；onboarding 仍提示設備/料路及 Studio 身份待核實。以未提供實際餘量的 Spoolman preview 驗證安全阻擋；拒絕原因為必須提供已確認餘量。沒有新增料卷或發送列印。
- 手動 Studio 合成預檢無 Bambuddy 網路呼叫，缺少任務級事實時保持 blocked；材料讀取、preview 與預檢回歸組合共 62 項測試通過。前端 `npm run build` 通過。
- Bambuddy 仍供既有 `bambuddy_queue`/原生任務回執、可選舊服務相容路徑與歷史來源使用；已設定 Spoolman/OpenSpoolMan 時庫存/槽位讀取不靜默回退。無 Bambuddy 的新官方 Studio 手動任務不呼叫服務。
- 全測試結果：428 passed、33 skipped、7 failed、1 deselected；失敗為 6 項 Windows symlink 權限限制與 1 項簡繁字串比對不一致，均非本 change 的測試。
- `openspec validate <change> --strict` 與 `openspec validate --specs --strict` 均通過；`git diff --check` 無空白錯誤。

## Workflow follow-up

- 實作完成並經使用者檢視後，封存本 change，讓主規格記錄兩個服務的資料責任及列印安全邊界。
