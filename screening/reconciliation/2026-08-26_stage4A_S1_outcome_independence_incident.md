# Stage 4A-S1 — Outcome-independence incident and restart decision

**Date:** 2026-08-26  
**Status:** PRIOR S1 LANE INVALIDATED; CLEAN-ROOM RESTART REQUIRED  
**Last valid repository commit before incident:** `75ffd92515bde478b657d77c622516dbc07f51d1`

## Incident

During the first Stage 4A-S1 attempt, Codex issued a broad repository search while trying to locate canonical-source hash text. The search traversed file paths that the locked S1 protocol explicitly prohibited, including E2 reproduction evidence paths.

Codex stopped immediately, interrupted ongoing review work, did not commit any S1 artifact, did not push, and verified that the Q1 repository worktree remained clean and synchronized with `origin/main`.

Reported state at stop:

- no new commit;
- no proposal CSV;
- no contact sheet;
- no frozen split or interval;
- no Stage 4B execution;
- no diagnostic or soft-score decision;
- 33 sequence scans had begun, but none can be certified as outcome-independent after the prohibited search.

## Scientific-integrity decision

The stop was correct and is accepted.

The complete first S1 attempt is invalid for scientific use. In particular:

- the 33 partially scanned sequences and any uncommitted notes or mental selections from that lane must not be reused;
- no sequence, interval, tier, control or split from the failed lane may be carried forward;
- the failed lane does not create a new sequence-level quarantine because no proposal was committed and Codex states that exposed material was not used for selection;
- the existing outcome-exposure quarantine remains `Deer`, `Crossing`, and `Couple`;
- a new Codex window/session must restart from zero.

This is a process contamination, not evidence that OTB100, SpikeTrack or any candidate sequence is scientifically invalid.

## Restart architecture

Stage 4A-S1 will restart through an external clean-room bundle that contains only explicitly allowed source-selection inputs. The new worker lane must not conduct any repository-wide search, recursive repository enumeration, history search or IDE global search.

The restart is split into two gates:

1. `Stage 4A-S1-R0` — create and verify the clean-room input bundle; no sequence scanning.
2. `Stage 4A-S1-R1` — scan canonical OTB source frames and produce proposals entirely from the verified clean room; starts only after Manager review of R0.

## Locked state

- Stage 4A-E2: COMPLETE / ACCEPTED
- Stage 4A-S1 first attempt: INVALIDATED
- Stage 4A-S1-R0 clean-room setup: READY
- Stage 4A-S1-R1 interval proposal: LOCKED PENDING R0 REVIEW
- frozen diagnostic slice: NOT CREATED
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
