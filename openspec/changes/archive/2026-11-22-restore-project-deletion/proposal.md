## Why

分支已包含專案刪除功能的歷史提交，但目前的版本缺少該功能。恢復既有實作，讓使用者能從工作台移除已確認的專案。

## What Changes

- 恢復工作台的專案刪除對話框與本機清理 API。
- 檢查列印與工作台任務狀態，保護專案外的資料與來源。

## Capabilities

### New Capabilities

- `workspace-project-deletion`：從工作台確認並清理指定的本機專案。

## Impact

涵蓋專案圖冊、工作台 API、專案與列印記錄的關聯、購物需求，以及安裝與瀏覽器驗證。
