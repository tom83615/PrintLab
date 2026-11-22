# Proposal

## Why

目前使用中的工作台直接讀取開發目錄，重建前端或重新啟動後可能載入尚未驗證的改動。需要在同一台 Windows 電腦提供隔離的開發與正式服務。

## What Changes

- 使用 `8018` 執行可自動重載的開發版，資料與正式版隔離。
- 使用 Docker Compose 在 `10818` 提供正式版，從固定提交建置並將工作區資料保存在宿主機。
- 正式更新由操作者啟動，檢查 `tom83615` 的既有 CI，驗證候選版並在啟動失敗時還原上一個映像。

## Capabilities

### New Capabilities

- `studio-release-deployment` 提供隔離的工作台環境、版本切換與回退。

### Modified Capabilities

## Impact

新增 Docker、Windows 開發與部署入口。Bambu Studio、Blender 和 CAD 工具使用 Windows 的安裝環境，正式服務在本機監聽。
