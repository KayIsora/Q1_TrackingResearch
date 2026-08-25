# Stage 4A-S1-R0 — Clean-room contamination reconciliation

**Date:** 2026-08-26  
**Status:** FIRST R0 BUNDLE INVALIDATED; CORRECTED R0V2 REQUIRED  
**Last valid repository commit before the stopped Codex lane:** `6ac470f63d132acf253e18af1c0ccca065be90c6`

## Incident

The first clean-room setup protocol required Codex to copy:

`screening/reconciliation/2026-08-26_stage4A_E2_otb_reconciliation.md`

into the clean-room bundle. That file contains actual tracker-outcome values from the bounded reproduction review, including sequence-level Success-AUC differences for Deer, Crossing and Couple.

The same clean-room protocol prohibited outcome-evidence payloads. These two requirements were contradictory.

Codex detected the contradiction during the clean-room-only contamination check, stopped immediately, created no Q1 commit, pushed nothing and verified that the Q1 worktree remained clean. No OTB frame was scanned and no interval, tier, control, split or contact sheet was created.

## Manager responsibility

This contamination was caused by the Manager whitelist, not by an unauthorized Codex operation. Codex followed the protocol correctly by stopping.

The first external clean-room root:

`F:\Q1_TrackingResearch_Data\Stage4A_S1_Cleanroom_2026-08-26\`

is permanently invalid for scientific use and must not be reused as an input to any later lane. It should be retained only as an incident artifact until the project no longer needs it; it must not be merged into, copied into or compared for selection with the corrected clean room.

## Scientific-integrity consequence

- First S1 interval-proposal attempt: already invalidated.
- First R0 clean-room bundle: invalidated.
- No sequence-level evidence from either stopped lane may be reused.
- No new sequence quarantine is created because R0 inspected no source frames and produced no selection.
- Existing outcome-exposure quarantine remains exactly: Deer, Crossing and Couple.
- Stage 4B remains locked.

## Corrective action

A manually sanitized Manager source summary will replace the full E2 reconciliation inside the clean room. The sanitized summary contains only source-selection facts:

- canonical OTB source identity and hashes;
- canonical source path;
- source/evaluator readiness;
- outcome-independent sequence-inventory counts and provenance;
- the existing quarantine names;
- stage boundaries.

It contains no tracker predictions, Success AUC, sequence-level performance values, divergence evidence, local-versus-released comparison or MRM result.

A new protocol, `Stage 4A-S1-R0V2`, will use a new external root and a smaller exact whitelist. The full E2 reconciliation and both contamination-incident files are prohibited from the corrected clean-room bundle.

## Locked state

- Stage 4A-E2: COMPLETE / ACCEPTED
- Stage 4A-S1 first interval lane: INVALIDATED
- Stage 4A-S1-R0 first bundle: INVALIDATED
- Stage 4A-S1-R0V2 corrected setup: READY
- Stage 4A-S1-R1 scanning: LOCKED PENDING R0V2 REVIEW
- frozen diagnostic slice: NOT CREATED
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
