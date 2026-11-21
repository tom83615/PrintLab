# Design

## Context

See `proposal.md` and the `print-dispatch` delta spec. Current checks span task readiness cards, approval, fingerprinting, prepared checks, Bambuddy dispatch, workbench start, and manual Studio handoff.

## Goals / Non-Goals

**Goals:** Missing or stale task confirmations do not block task readiness, approval, or a user-initiated dispatch. Unknown facts remain unknown.

**Non-Goals:** Do not remove file/G-code integrity, printer identity/model/plate compatibility, live telemetry and active-job checks, diagnostics, idempotency, or explicit user initiation of a send.

## Decisions

- Remove task confirmation facts from readiness and dispatch predicates rather than fabricating positive facts. This keeps evidence truthful and avoids maintaining fake confirmation timestamps.
- Remove FTS-declaration freshness from the task fingerprint. Keep the route mapping as slice metadata and retain structural validation that AMS/extruder arrays are present and well-formed.
- Treat live device state as distinct from missing user confirmation: observed offline/busy/error/awaiting-clear remains a real dispatch blocker.
- Manual Studio retains the configured local printer identity and an explicit UI Send action; no automatic send is added.
- Keep old confirmation events readable for compatibility, but they are optional metadata.

## Risks / Trade-offs

- Operators receive fewer reminders about spool/nozzle mapping and plate state → show unknown mapping as unknown and continue to block on actual live device errors and explicit firmware clear-plate requests.
- Older approvals may include confirmation fields → accept them as optional historical evidence; new receipts need not claim those facts.

## Migration Plan

No data migration. Existing task records and confirmation events remain intact. New readiness and approval calculations use the relaxed rules.
