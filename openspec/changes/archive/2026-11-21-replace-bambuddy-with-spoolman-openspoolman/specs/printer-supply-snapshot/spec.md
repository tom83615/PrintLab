# Spec Delta

## Purpose

讓 PrintLab 從 OpenSpoolMan 取得印表機 AMS 與外掛料卷配置，同時保留快照來源和可信邊界，供材料準備及使用者核對。

## ADDED Requirements

### Requirement: Read printer supply snapshots from OpenSpoolMan
When OpenSpoolMan is configured, PrintLab SHALL use its supported printer and supply-slot data for the device supply view and identify OpenSpoolMan as the source.

#### Scenario: Show configured AMS slots
- **WHEN** the user views the device and OpenSpoolMan returns a supported slot snapshot
- **THEN** PrintLab displays printer identity, AMS groups, slot assignments, and empty slots represented by that source

#### Scenario: OpenSpoolMan is unavailable or unsupported
- **WHEN** the OpenSpoolMan service cannot be read or its response is unsupported
- **THEN** PrintLab identifies the source failure and does not silently present Bambuddy data as the OpenSpoolMan snapshot

### Requirement: Preserve snapshot confidence boundaries
PrintLab SHALL distinguish an OpenSpoolMan snapshot from live printer telemetry and SHALL leave unreported freshness, physical spool weight, nozzle route, and printer health unknown.

#### Scenario: Snapshot lacks live telemetry metadata
- **WHEN** OpenSpoolMan supplies slot assignments without verified live status or observation time
- **THEN** PrintLab labels the data as a snapshot and does not infer online state, current weight, or a verified nozzle route

#### Scenario: User prepares a print from a snapshot
- **WHEN** a print workflow needs current device health or verified slot routing
- **THEN** PrintLab requires independent current evidence or a user-confirmed verification before approving that precondition

### Requirement: Link AMS slots to Spoolman inventory without changing stock
PrintLab SHALL treat OpenSpoolMan slot assignments as references to Spoolman spools and SHALL report ambiguous or duplicate references without mutating either service.

#### Scenario: Slot references an existing spool
- **WHEN** an OpenSpoolMan slot contains a Spoolman spool ID that resolves in the configured inventory
- **THEN** PrintLab displays the linked spool details and retains each service's source identity

#### Scenario: Multiple slots reference one spool
- **WHEN** the snapshot assigns the same Spoolman spool ID to more than one active slot
- **THEN** PrintLab surfaces the conflict for user review and does not alter assignments or inventory
