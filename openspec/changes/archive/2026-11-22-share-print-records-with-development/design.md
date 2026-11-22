# Design

## Context

正式 Docker 服務已將本機資料掛載為可寫。開發服務需要用相同作品與列印記錄測試介面，正式更新仍依原部署流程。

## Decisions

- `8018` 沿用 Windows Python 虛擬環境及 Vite 建置。正式 `Project`、`Library` 和 `Runtime` 繼續由 `10818` 的容器掛載。
- Windows 和 Linux 容器的檔案鎖實測不互斥。共用模式停用開發 API 的背景寫入，由 Windows 入口將 API 讀寫轉送至本機 `10818`，使用正式服務的同一組檔案鎖。開發入口與正式入口均保留各自的本機同源、瀏覽器會話及 CSRF 驗證。
- `start-dev.ps1 -SharedRecords` 使用相同的開發 URL 和自動重載功能。既有 `start-dev.ps1` 保留獨立資料與可寫測試能力。

## Trade-offs

共用模式支援正式版本提供的資料操作。新 API 與資料格式變更使用獨立開發工作區測試，通過驗證後再進入正式版本。
