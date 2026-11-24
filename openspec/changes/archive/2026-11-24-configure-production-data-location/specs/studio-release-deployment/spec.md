## ADDED Requirements

### Requirement: 正式資料位置可設定

正式部署 SHALL 使用本機設定指定作品、知識庫與脈絡資料的位置。Runtime、憑據與部署狀態 SHALL 留在獨立的本機資料目錄。

#### Scenario: 使用已搬移的正式資料

- **WHEN** 本機部署設定指定有效的正式資料位置
- **THEN** 目前服務及後續部署使用該資料位置，維持原有 Runtime 與版本狀態

#### Scenario: 使用預設位置

- **WHEN** 未設定正式資料位置
- **THEN** 部署沿用既有本機預設資料目錄
