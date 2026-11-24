# Proposal

## Why

使用者需要將正式作品搬到指定的 Windows 資料夾，後續部署仍須讀取同一份資料。憑據及部署狀態需要繼續保存在本機應用程式資料目錄。

## What Changes

- 允許正式部署從本機設定讀取資料路徑。
- 將資料目錄與本機 Runtime 掛載分開。

## Capabilities

### New Capabilities

### Modified Capabilities

- `studio-release-deployment` 支援指定正式資料路徑。

## Impact

正式版 Docker 掛載、Windows 部署腳本及部署文件。
