# Proposal

## Why

在開發版驗證工作台時，需要讀取與正式版相同的作品、切片與列印記錄。正式環境仍需保護使用中的資料。

## What Changes

- 保留原生 Windows 開發服務，兩個入口可查詢與修改同一份作品及記錄。
- 開發版使用開發中的前端，共用資料操作交給正式 API 處理，避免跨作業系統的檔案鎖衝突。
- 保留具備可寫獨立資料的開發模式，供測試寫入流程。

## Capabilities

### New Capabilities

### Modified Capabilities

- `studio-release-deployment` 增加唯讀共用正式作品與列印記錄的模式。

## Impact

影響 Windows 開發啟動腳本、共用記錄入口與本機部署文件。
