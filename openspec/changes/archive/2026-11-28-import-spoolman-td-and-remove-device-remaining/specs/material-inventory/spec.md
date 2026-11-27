## MODIFIED Requirements

### Requirement: Spoolman is the material inventory source
PrintLab SHALL read active filament spools, their known remaining weights, and known filament transmission distance (`filament.extra.td`) from the configured Spoolman service, SHALL expose `transmission_distance` in inventory views and project manufacturing constraints, and SHALL identify the provider in inventory views.

#### Scenario: Read active inventory
- **WHEN** the user opens materials while Spoolman is configured
- **THEN** PrintLab shows non-archived Spoolman spools with their known weights and known transmission distance (`TD`) values, and identifies Spoolman as the source

#### Scenario: Remaining weight is unknown
- **WHEN** a Spoolman spool has no remaining weight value
- **THEN** PrintLab preserves the value as unknown and does not present it as a full spool

#### Scenario: Transmission distance is valid or missing
- **WHEN** a Spoolman filament defines a finite non-negative `extra.td` value (including `0`)
- **THEN** PrintLab parses and exposes it as `transmission_distance` in inventory items, project `owned_materials` constraints, and the materials UI
- **AND** when `extra.td` is missing, blank, negative, or non-numeric, PrintLab preserves `transmission_distance` as unknown (`None`) without guessing a default
