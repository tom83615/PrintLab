# Print Dispatch Specification

## Purpose

讓 PrintLab 在不依賴 Bambuddy 佇列服務的情況下延續已批准列印任務，並在設備或供料證據不足時安全阻止發送。

## Requirements

### Requirement: Use the official Studio path without Bambuddy
PrintLab SHALL support its official Bambu Studio handoff for an approved print task without requiring Bambuddy configuration or queue access.

#### Scenario: Prepare an approved Studio handoff
- **WHEN** a task has a valid model and slice binding, current required device and material evidence, and user approval
- **THEN** PrintLab prepares the official Studio handoff with the approved task identity and does not submit it to a Bambuddy queue

#### Scenario: Bambuddy is not configured
- **WHEN** the user uses the supported official Studio handoff and has not configured Bambuddy
- **THEN** PrintLab does not block the handoff solely because Bambuddy is absent

### Requirement: Bind manual Studio tasks to a local printer identity
When Bambuddy is not configured, PrintLab SHALL bind each prepared task to the locally configured Studio printer name, model, and serial number, and SHALL include that identity in task approval validation.

#### Scenario: Studio printer identity is missing
- **WHEN** a user prepares or approves a task without a complete local Studio printer identity
- **THEN** PrintLab identifies the missing identity and does not approve or reserve the task for dispatch

#### Scenario: Studio printer identity changes
- **WHEN** the configured Studio printer identity changes after a task was prepared or approved
- **THEN** the existing approval becomes invalid and PrintLab requires a newly bound task

### Requirement: Block dispatch when required evidence is unknown
PrintLab SHALL NOT treat a Spoolman inventory record or an OpenSpoolMan supply snapshot alone as proof of current printer readiness, verified routing, or a cleared build plate.

#### Scenario: Required routing cannot be verified
- **WHEN** the approved task requires a slot or nozzle route that is unknown or only inferred from an unverified snapshot
- **THEN** PrintLab blocks dispatch until the route is independently verified and recorded for that task

#### Scenario: Current device readiness is unavailable
- **WHEN** current device readiness or the required clear-plate fact cannot be confirmed
- **THEN** PrintLab keeps the task unsubmitted and identifies the missing precondition

#### Scenario: Manual Studio handoff requires current observations
- **WHEN** a task uses the no-Bambuddy manual Studio route
- **THEN** PrintLab requires fresh exact-task confirmation of printer readiness, verified material routing, loaded material, cleared build plate, and authorization

### Requirement: Reconcile the same approved task without a Bambuddy queue
PrintLab SHALL preserve task identity and report dispatch outcome as unknown until the official Studio handoff has an observable result; it SHALL NOT retry an uncertain dispatch automatically.

#### Scenario: Studio handoff outcome is uncertain
- **WHEN** PrintLab cannot determine whether the official Studio handoff reached the printer
- **THEN** PrintLab records an unresolved outcome and requires reconciliation before another submission

#### Scenario: User records a manual observation
- **WHEN** the user reconciles a no-Bambuddy Studio task with the exact expected task name and an observation source
- **THEN** PrintLab records the observation against the same task without contacting a printer service or creating a new dispatch
