# Spec Delta

## Purpose

讓 PrintLab 以 Spoolman 作為材料目錄與實體料卷台帳，並讓庫存讀取、登記及中斷恢復遵循同一資料來源與可追溯行為。

## ADDED Requirements

### Requirement: Spoolman is the material inventory source
PrintLab SHALL read active filament spools and their known remaining weights from the configured Spoolman service, and SHALL identify the provider in inventory views.

#### Scenario: Read active inventory
- **WHEN** the user opens materials while Spoolman is configured
- **THEN** PrintLab shows non-archived Spoolman spools with their known weights and identifies Spoolman as the source

#### Scenario: Remaining weight is unknown
- **WHEN** a Spoolman spool has no remaining weight value
- **THEN** PrintLab preserves the value as unknown and does not present it as a full spool

### Requirement: Register a confirmed spool safely
PrintLab SHALL provide a preview and an idempotent registration flow for one user-confirmed physical spool at a time, without silently changing the filament catalog or spool consumption.

#### Scenario: Preview a valid spool registration
- **WHEN** a user previews a spool with a valid Spoolman filament ID and required confirmed weights
- **THEN** PrintLab displays the target filament and registration details without writing to Spoolman

#### Scenario: Register and read back a spool
- **WHEN** a user confirms registration and submits a stable request ID
- **THEN** PrintLab creates one spool, reads it back, and records the observed Spoolman ID for retry reconciliation

#### Scenario: Recover an interrupted registration
- **WHEN** the same request ID is retried after an uncertain write result
- **THEN** PrintLab finds and returns the matching existing spool, or reports an unresolved result without creating a duplicate

#### Scenario: Spoolman would assume a full spool
- **WHEN** the selected filament has a known initial weight but the remaining weight is not confirmed
- **THEN** PrintLab refuses the write and asks for the confirmed remaining weight

### Requirement: Report inventory service failures clearly
PrintLab SHALL report when the configured Spoolman service is unavailable or returns unsupported data, and SHALL NOT silently substitute Bambuddy inventory.

#### Scenario: Spoolman is unavailable
- **WHEN** a materials read or registration cannot reach Spoolman
- **THEN** PrintLab identifies the Spoolman failure and preserves any pending registration for reconciliation
