## MODIFIED Requirements

### Requirement: Preserve snapshot confidence boundaries
PrintLab SHALL 區分 OpenSpoolMan 快照與即時遙測，並保留未知的遙測時間、料卷重量及設備狀態。

#### Scenario: 顯示耗材槽位
- **WHEN** 使用者查看設備耗材槽位
- **THEN** PrintLab SHALL 顯示料槽及材料資料，省略噴嘴路線和相關提示

#### Scenario: Snapshot lacks live telemetry metadata
- **WHEN** OpenSpoolMan 提供缺少即時遙測的快照
- **THEN** PrintLab SHALL 標示快照來源，並保留未知的設備狀態、更新時間及料重

#### Scenario: User prepares a print from a snapshot
- **WHEN** 列印流程需要即時設備狀態
- **THEN** PrintLab SHALL 依該交接流程使用適用的設備狀態來源
