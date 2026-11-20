# Proposal

## Why

使用者日常以 Spoolman 管理料卷、以 OpenSpoolMan 查看 H2C 的 AMS 配置，PrintLab 卻仍把 Bambuddy 當作主要設備與耗材後端，造成重複服務依賴與流程分裂。現在應將 PrintLab 的庫存與供料資訊流程正式改由這兩個既有服務提供，並清楚限制快照資料的可信程度。

## What Changes

- Spoolman 成為耗材目錄與料卷庫存的唯一讀寫來源，支援讀取、預覽、登記、讀回及重試對帳。
- OpenSpoolMan 成為設備和 AMS／外掛料卷配置快照來源；快照需標明來源、時間與未知欄位，不得假稱即時遙測或已驗證噴嘴路線。
- PrintLab 的 onboarding、製造條件、庫存介面與歷史入口以這兩個服務為準，不再要求設定 Bambuddy 才能完成耗材和槽位工作流。
- 移除 PrintLab 對 Bambuddy 設備、庫存、佇列與歷史 API 的必要依賴；列印發送沿用官方 Bambu Studio 工作流。缺少可信設備狀態或槽位路線時，預檢須要求補充核驗，不能以快照推定可安全發送。
- Windows 使用手動 Studio 交接：列印任務綁定本機保存的印表機名稱、機型及序號；使用者核對當下設備、料路、已裝材料與清板後才可批准。未接即時遙測的任務結果保持未知，透過綁定該任務的觀察證據對帳。
- 保留既有設定的遷移提示與清楚的服務錯誤，避免默默回退到 Bambuddy 或覆蓋使用者資料。

## Capabilities

### New Capabilities

- `material-inventory`: Spoolman 耗材目錄與料卷的讀取、登記和冪等對帳。
- `printer-supply-snapshot`: OpenSpoolMan 設備及供料槽快照的讀取、標示與核驗邊界。
- `print-dispatch`: 使用可信前置資訊，透過官方 Studio 工作流準備、核准、發送及對帳列印任務。

### Modified Capabilities

目前 `openspec/specs/` 沒有既有 capability。

## Impact

影響 `Harness/printlab/` 的供應商適配、onboarding、製造條件、庫存登記、預檢及歷史流程；Studio 庫存／歷史介面；連接、設定及列印文件；`Runtime/config.json` 的服務網址設定。實作前需核對 OpenSpoolMan 實際可提供的設備／槽位資料和更新時間；Spoolman 負責台帳庫存而非即時 AMS 余量。列印仍透過官方 Studio，不把 Spoolman 或 OpenSpoolMan 描述為列印傳輸服務。
