# Design

## Context

目前正式資料與 Runtime 都位於 `%LOCALAPPDATA%/PrintLab/production` 下。

## Decisions

- 在本機正式狀態目錄的 `workspace-path.txt` 記錄資料位置。未設定時沿用原路徑。
- Compose 以資料路徑掛載 `Project`、`Library` 和 `Context`，以固定的本機路徑掛載 `Runtime`。部署鎖與版本記錄留在本機。
- 搬移採複製、驗證、切換，保留舊資料副本。正式容器繼續運行原有映像。
