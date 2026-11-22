# studio-release-deployment Specification

## Purpose

讓使用者在同一台電腦隔離開發測試與正式工作台，並在驗證版本後安全切換正式服務。

## Requirements

### Requirement: 開發與正式工作台隔離

工作台 SHALL 在本機 `8018` 提供開發流程，並在 `10818` 提供 Docker 正式服務。兩者各自使用程式建置、工作區資料與本機設定。

#### Scenario: 開發者存檔

- **WHEN** 開發者修改前端或 Python 程式
- **THEN** 開發工作台重新建置或重載，正式服務繼續執行其固定版本

#### Scenario: 正式容器重建

- **WHEN** 正式容器重新啟動或更新
- **THEN** 正式工作區資料仍可讀取，HTTP 連接埠僅在本機發布

### Requirement: 正式服務版本切換

部署入口 SHALL 從固定提交建置、驗證候選服務，並提供回退。例行升級 SHALL 只使用 `tom83615` 通過 CI 的 push 提交。首次啟用可使用本機已提交且通過自動測試的版本。

#### Scenario: 例行升級

- **WHEN** 操作者指定通過 CI 的提交
- **THEN** 部署入口先驗證候選服務，再切換正式服務並驗證啟動

#### Scenario: 新版啟動失敗

- **WHEN** 正式服務切換後未通過驗證且有上一個版本
- **THEN** 部署入口還原上一個映像並驗證其服務
