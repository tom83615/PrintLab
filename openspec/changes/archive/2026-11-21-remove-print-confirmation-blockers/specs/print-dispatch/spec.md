# Spec Delta

## MODIFIED Requirements

### Requirement: Block dispatch when required evidence is unknown
PrintLab SHALL NOT block solely because task-specific readiness, material, route, plate-clear, or authorization facts are missing, stale, or withdrawn. Unknown SHALL remain distinct from confirmed. FTS declaration changes alone SHALL NOT invalidate a task fingerprint. Sending SHALL be user-initiated. Live offline, active/unknown, error, or awaiting-clear device states SHALL still block sending.

#### Scenario: Required routing cannot be verified
- **WHEN** the approved task requires a slot or nozzle route that is unknown or only inferred from an unverified snapshot
- **THEN** PrintLab retains the route as unverified information and does not block dispatch solely because task-level route confirmation is absent

#### Scenario: Current device readiness is unavailable
- **WHEN** task-specific readiness or clear-plate confirmation is missing
- **THEN** PrintLab does not require those confirmation events; it still blocks when live telemetry reports an actual unsafe device state

#### Scenario: Manual Studio handoff requires current observations
- **WHEN** a task uses the no-Bambuddy manual Studio route without fresh exact-task readiness, route, loaded-material, clear-plate, or authorization facts
- **THEN** PrintLab allows the user-initiated handoff if file integrity and printer identity requirements pass, without synthesizing missing facts
