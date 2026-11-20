# Design

## Context

See `proposal.md` for motivation. Existing uncommitted work already adds a Spoolman adapter and intake path plus an OpenSpoolMan slot snapshot parser. The current configuration can still fall back to Bambuddy, and queue dispatch, reconciliation, and some history behavior remain Bambuddy-specific. The repository has no main specs yet. OpenSpoolMan currently exposes a web view; the available data does not establish live printer telemetry, freshness, or nozzle routing.

## Goals / Non-Goals

**Goals:**

- Make Spoolman authoritative for material catalog and spool ledger, and OpenSpoolMan authoritative for the available printer supply snapshot.
- Make provider provenance, freshness, unknown fields, and service errors visible throughout onboarding, manufacturing context, and the Studio UI.
- Allow the existing official Studio print handoff without Bambuddy; require independent evidence for readiness and routing before a task can be dispatched.
- On Windows, bind manual Studio handoffs to a local name/model/serial identity and reconcile only explicit observations tied to the reserved task.
- Keep service credentials and local journals in the existing private/runtime storage boundaries.

**Non-Goals:**

- Implement direct printer control or assume OpenSpoolMan is a dispatch API.
- Import historical print records from OpenSpoolMan or Spoolman.
- Automatically merge, repair, or rewrite ambiguous spool-to-slot assignments.
- Migrate or resend an in-flight Bambuddy queue task without explicit reconciliation.

## Decisions

1. **Separate provider responsibilities.** Spoolman owns catalog references and spool ledger; OpenSpoolMan owns the printer/AMS snapshot. The supply adapter returns source-labelled domain data instead of blending providers into an apparent single live device object. This matches the services' distinct responsibilities. A single Bambuddy replacement API was considered but neither named service supplies that contract.

2. **Do not silently fall back across providers.** A configured provider failure is shown as an error for its domain; a missing provider may use a legacy source only during an explicit migration period and must show that source. The target configuration and onboarding must not require Bambuddy. Silent fallback would make stale or unrelated data look authoritative.

3. **Keep OpenSpoolMan ingestion read-only and schema-guarded.** Prefer a documented API if the deployed instance exposes one; otherwise keep a small, isolated parser for the supported page representation. Reject unsupported markup, do not follow action links, and never write slot assignments through page controls. A future supported API can replace the parser without changing the snapshot contract.

4. **Treat snapshots as planning evidence, not live readiness.** Carry observed-at/freshness only when supplied by the source; otherwise label the snapshot time as unknown. Keep actual weight, printer online state, nozzle route, and build-plate state unknown unless independently confirmed. A slot reference can enrich from Spoolman by ID, but duplicate references remain a surfaced conflict.

5. **Use official Studio for dispatch and remove Bambuddy queue as a required path.** Keep task-bound approval and dispatch records. For a new task, dispatch only through the existing official Studio handoff after all required current facts are verified. Existing Bambuddy queue tasks remain readable for reconciliation and must not be silently converted or resubmitted. This avoids inventing unsupported write capabilities in either Spoolman or OpenSpoolMan.

6. **Use manual, task-bound evidence on Windows.** The installed host capability reports that the automated Studio helper is unsupported on Windows. Store the exact Studio printer display name, model, and serial in local configuration; bind those values into the task fingerprint. Before a no-Bambuddy task is approved, require fresh exact-task facts for device readiness, verified routing, loaded material, plate clearance, and print authorization. If live telemetry is absent, reconciliation remains unknown until the user records an observation of the exact task; recording an observation does not send or retry it.

7. **Make Spoolman intake preview-first and idempotent.** Preserve a local request journal, stable request marker, pre-write weight validation, and remote readback. Do not write the catalog or consumed weight. An uncertain write is reconciled by the same request ID before any new create attempt.

## Risks / Trade-offs

- [OpenSpoolMan page markup changes] → Isolate parsing, return a clear unsupported-source state, and keep unknown fields unknown.
- [Spoolman inventory is an estimate and may diverge from physical stock] → Show provider and known/unknown weights; require user confirmation before adding a physical spool or using stock assumptions.
- [Removing the Bambuddy queue path reduces automated dispatch options] → Retain the official Studio workflow, preserve old queue task records, and report unsupported automation instead of simulating it.
- [Existing local configuration may select mixed providers] → Migrate by reading old settings first, keep local backups, show effective provider per domain, and never overwrite user credentials or pending task data.

## Migration Plan

1. Read and validate existing provider configuration; recognize the supplied Spoolman and OpenSpoolMan roots without placing credentials in tracked files.
2. Route inventory, intake, onboarding, constraints, and history links to their appropriate services, and expose source and unknown metadata.
3. Remove Bambuddy as a prerequisite for official Studio handoff; gate dispatch on task-specific current evidence and retain legacy queue records for explicit reconciliation.
4. Update setup/onboarding documentation and CLI help; provide a clear notice when a legacy Bambuddy configuration is present but no longer selected.
5. Verify read-only provider behavior, preview-only intake, unsupported/stale data handling, and dispatch gates before any live write or print action.

Rollback consists of restoring the prior local provider configuration and previous application version. Do not roll back by deleting Spoolman entries or rewriting task journals.

## Open Questions

- Whether the deployed OpenSpoolMan instance has a documented API that provides stable slot IDs and an observation timestamp; the current page-derived snapshot lacks verified live telemetry metadata.
