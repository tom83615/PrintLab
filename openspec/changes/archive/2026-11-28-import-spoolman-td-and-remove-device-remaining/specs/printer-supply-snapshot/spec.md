## MODIFIED Requirements

### Requirement: Preserve snapshot confidence boundaries
PrintLab SHALL 區分 OpenSpoolMan 快照與即時遙測，並保留未知的遙測時間、料卷重量及設備狀態。

#### Scenario: 顯示耗材槽位
- **WHEN** 使用者查看設備耗材槽位
- **THEN** PrintLab SHALL 顯示料槽、材料資料與已知的線材透光值（`TD`），並省略噴嘴路線、設備餘量欄位和相關提示

#### Scenario: Snapshot lacks live telemetry metadata
- **WHEN** OpenSpoolMan 提供缺少即時遙測的快照
- **THEN** PrintLab SHALL 標示快照來源，並保留未知的設備狀態、更新時間及料重

#### Scenario: User prepares a print from a snapshot
- **WHEN** 列印流程需要即時設備狀態
- **THEN** PrintLab SHALL 依該交接流程使用適用的設備狀態來源

### Requirement: Link AMS slots to Spoolman inventory without changing stock
PrintLab SHALL treat OpenSpoolMan slot assignments as references to Spoolman spools and SHALL report ambiguous or duplicate references without mutating either service.

#### Scenario: Slot references an existing spool
- **WHEN** an OpenSpoolMan slot contains a Spoolman spool ID that resolves in the configured inventory
- **THEN** PrintLab displays the linked spool details including known `transmission_distance` and retains each service's source identity

#### Scenario: Multiple slots reference one spool
- **WHEN** the snapshot assigns the same Spoolman spool ID to more than one active slot
- **THEN** PrintLab surfaces the conflict for user review and does not alter assignments or inventory
