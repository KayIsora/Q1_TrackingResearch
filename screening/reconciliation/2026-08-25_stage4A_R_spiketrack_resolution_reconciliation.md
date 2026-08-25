# Stage 4A-R — SpikeTrack reproduction-resolution reconciliation

**Date:** 2026-08-25  
**Status:** `STAGE4A_R_PENDING_ENVIRONMENT_OR_DATA`; Stage 4B remains locked.  
**Inputs:**

- `screening/codex/2026-08-25_stage4A_R_spiketrack_resolution.md`
- `screening/codex/2026-08-25_stage4A_spiketrack_instrumentation_manifest_v2.csv`
- `screening/codex/2026-08-25_stage4A_spiketrack_slice_inventory_v2.csv`
- `screening/codex/patches/2026-08-25_spiketrack_stage4A_repair.patch`
- `screening/codex/scripts/2026-08-25_stage4A_spiketrack_reproduce3.py`
- machine-readable evidence under `screening/codex/artifacts/stage4A_reproduction/`
- `screening/manager/2026-08-25_stage4_spiketrack_diagnostic_protocol.md`
- `screening/reconciliation/2026-08-25_stage4A_spiketrack_preflight_reconciliation.md`

## Boundary

This reconciliation reviews Stage-4A-R only. It does not assign `DIAG_PASS` or `DIAG_FAIL`, start Stage 4B, freeze a diagnostic slice, assign S1–S7, create a shortlist, select a main baseline, or authorize a proposed architecture.

## Accepted evidence

### R1 — reproduction procedure is now auditable

The previous bounded adapter was preserved rather than reconstructed. Its source, command log, environment, prediction files, released-result copies, metrics, first-divergence records, raw-file hashes, decoded-frame hashes and annotation hashes are now stored as small text artifacts in the project repository.

This resolves the Stage-4A auditability blocker.

### R2 — adapter and official runner are equivalent locally

On the same source files, exact checkpoint/configuration and declared mode:

- the custom adapter and official `Tracker.run_sequence` path produce identical predictions;
- adapter-decoded RGB and official `Tracker._read_image` RGB hashes agree;
- official-default local repetitions are identical;
- deterministic local repetitions are identical.

Therefore the released-result mismatch is not attributable to the preserved adapter or to local run nondeterminism.

### R3 — retrieval-specific instrumentation is complete

The refined instrumentation now separates:

- template-conditioned Retriever contribution;
- MLP contribution;
- whole-MRM contribution.

It also exposes T3 pre-gate per-template/time response norms, gate statistics/fingerprints and deterministic one-template/time-path controls. All controls remain contribution probes with `physical_skip=false`.

Clean versus refined/no-ablation parity is accepted at maximum absolute difference `0.0` for the declared T1/T3 synthetic and real-image checks.

### R4 — local data inventory is more auditable

Duplicate local copies were compared by raw-file and decoded-pixel hashes where available. The selected local copies are internally consistent, and tracker outputs were not used to select candidate distractor sequences.

## Unresolved blockers

### E1 — released raw-result provenance remains unresolved

The same exact local run still differs materially from the released raw predictions on Deer and Couple, while Crossing is within the locked 0.5-percentage-point tolerance.

The released archive does not contain a sufficient commit, environment, dataset-checksum or unambiguous configuration manifest. The raw member path alone does not establish which exact released model/configuration generated the file.

Final reproduction label remains:

`REPRO_UNRESOLVED`

This is not a scientific failure of SpikeTrack.

### E2 — canonical OTB identity is not established

Local duplicate copies agree where duplicates exist, but no canonical OTB release hash or author-provided OTB checksum is available for comparison. Dataset identity therefore remains `PARTIAL`.

### E3 — environment comparison is incomplete

A GPU-visible WSL/Linux route exists on the same MX250 host, but a valid isolated Linux environment matching the nearest installable official stack has not yet been completed. The README's Python 3.12 request is incompatible with the pinned Torch 2.0.0 wheel contract; a bounded Python 3.10/3.11 Linux run remains an unresolved environment experiment.

A Linux rerun may help characterize platform sensitivity, but cannot by itself prove identity with the authors' unpublished run environment.

### E4 — diagnostic data coverage is insufficient

Only ten locally complete OTB sequences are currently inventoried, with four independently justified similar-distractor candidates. This cannot satisfy the locked discovery/hold-out minimum.

Stage 4B therefore cannot begin even if reproduction is accepted.

## Management interpretation

The current evidence narrows the problem substantially:

- instrumentation is not causing the released-result mismatch;
- adapter versus official-runner behavior is not causing the mismatch;
- local nondeterminism is not causing the mismatch;
- the remaining uncertainty is external provenance: released raw-result identity, canonical dataset identity and/or author platform/runtime details.

The correct next step is not another unrestricted debugging cycle. It is a bounded external-evidence checkpoint requiring explicit resource authorization.

## Required next checkpoint — Stage 4A-E

Stage 4A-E may perform only:

1. official raw-result/model resource attribution and cloud metadata verification;
2. bounded canonical dataset acquisition after Manager/User approval;
3. bounded Linux official-stack comparison on already available hardware;
4. outcome-independent expansion of the candidate sequence inventory.

No MRM diagnostic ablation, physical skip, ambiguity labeling or soft scoring is permitted in Stage 4A-E.

## Decision

**Final Stage-4A-R state: `STAGE4A_R_PENDING_ENVIRONMENT_OR_DATA`.**

Accepted code and instrumentation artifacts remain valid. No `DIAG_PASS`/`DIAG_FAIL` is assigned.

## Locked downstream state

- Stage 4A-E: `AWAITING_RESOURCE_AUTHORIZATION`
- Stage 4B: `LOCKED`
- diagnostic decision: `NOT_ASSIGNED`
- S1–S7: `NOT_STARTED`
- primary shortlist: `NONE`
- main baseline: `NONE`
- proposed architecture: `NONE`
