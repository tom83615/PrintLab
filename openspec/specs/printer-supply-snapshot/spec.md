# Printer Supply Snapshot Specification

## Purpose

讓 PrintLab 從 OpenSpoolMan 取得印表機 AMS 與外掛料卷配置，同時保留快照來源和可信邊界，供材料準備及使用者核對。

## Requirements

### Requirement: Read printer supply snapshots from OpenSpoolMan
When OpenSpoolMan is configured, PrintLab SHALL use its supported printer and supply-slot data for the device supply view and identify OpenSpoolMan as the source.

#### Scenario: Show configured AMS slots
- **WHEN** the user views the device and OpenSpoolMan returns a supported slot snapshot
- **THEN** PrintLab displays printer identity, AMS groups, slot assignments, and empty slots represented by that source

#### Scenario: OpenSpoolMan is unavailable or unsupported
- **WHEN** the OpenSpoolMan service cannot be read or its response is unsupported
- **THEN** PrintLab identifies the source failure and does not silently present Bambuddy data as the OpenSpoolMan snapshot

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
