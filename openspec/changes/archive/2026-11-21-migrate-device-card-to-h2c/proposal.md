# Proposal

## Why

目前設備卡內容記錄的是 Bambu Lab H2C，資料夾卻沿用 X2D 歷史名稱，讓使用者與維護者誤以為該設備卡屬於 X2D。現在將單一設備卡路徑改為 H2C，降低日常操作中的身分混淆。

## What Changes

- 將設備卡與本機設備說明從 `Library/Devices/X2D/` 遷移至 `Library/Devices/H2C/`。
- 更新讀取、初始化、工作台文件入口、測試及文件中的設備卡路徑。
- 保留 X2D 作為實際切片／發送機型的既有支援名稱與限制。

## Capabilities

### New Capabilities

無。

### Modified Capabilities

無；這是內部資料路徑遷移，不改變使用者可見的設備或列印行為。依此變更設定 `skip_specs: true`。

## Impact

影響 PrintLab Harness、工作台設備文件連結、首次初始化範本、測試和設定文件。既有工作區的 H2C 設備卡資料需原樣搬移並保留；X2D 切片設定與發送相容性不在本次遷移範圍。
