# Stage 4A — SpikeTrack preflight reconciliation

**Date:** 2026-08-25  
**Status:** STAGE4A INCOMPLETE; bounded repair/reproduction-resolution step required.  
**Inputs:**

- `screening/codex/2026-08-25_stage4A_spiketrack_preflight.md`
- `screening/codex/2026-08-25_stage4A_spiketrack_instrumentation_manifest.csv`
- `screening/codex/2026-08-25_stage4A_spiketrack_slice_inventory.csv`
- `screening/codex/patches/2026-08-25_spiketrack_stage4A_instrumentation.patch`
- `screening/manager/2026-08-25_stage4_spiketrack_diagnostic_protocol.md`

## Boundary

This reconciliation reviews Stage-4A readiness only. It does not assign `DIAG_PASS` or `DIAG_FAIL`, run Stage 4B, freeze a diagnostic slice, assign S1–S7, form a shortlist, select a baseline, or authorize a proposed architecture.

## Accepted Stage-4A evidence

### Canonical matrix

The N2 mechanical matrix synchronization is accepted:

- CX044 AsymTrack — HG6 FAIL;
- CX058 HiT-DyHiT — HG6 FAIL;
- 54 columns and 20 unique candidate IDs retained;
- S1–S7 and total score remain blank.

### Source and checkpoints

The exact pinned SpikeTrack source and released Small-256 T1/T3 tracker checkpoints were resolved. Checkpoint hashes and strict final-network loading evidence are recorded. The absent SDTV3 pretraining asset is a training-provenance issue and does not block released-checkpoint inference.

### Instrumentation parity

The six MRM locations are correctly mapped. Instrumentation is opt-in and disabled by default. Clean versus instrumented/no-ablation outputs matched exactly for T1 and T3 in the bounded tests, including a real-image frame. The patch applies cleanly to the pinned source.

### Deterministic contribution controls

The six individual and three grouped whole-MRM zero-residual controls execute with finite outputs and correctly declare `physical_skip=false`. They are accepted as preliminary contribution controls, not compute-saving evidence.

## Blocking issues

### B1 — released-result reproduction is unresolved

The predeclared three-sequence check produced:

- Crossing: within 0.5 percentage points;
- Couple: 1.462585 percentage points from the released raw result;
- Deer: 29.912810 percentage points from the released raw result.

The exact source of the mismatch is unresolved. Stage 4B cannot start while the baseline-reproduction boundary remains unresolved.

### B2 — reproduction evidence is not independently auditable from the repository

The report describes a custom bounded adapter, but the exact adapter source, commands, local prediction files, corresponding released prediction files, ground-truth copies/hashes, decoded-frame hashes, metric output, and first-divergence log were not committed.

This does not invalidate the measurements, but it prevents Manager verification of:

- RGB/BGR loading parity with `Tracker._read_image`;
- exact initialization and frame-info behavior;
- direct-adapter parity with the official `Tracker.run_sequence` path;
- source-image and annotation identity;
- raw-result archive member identity.

These small text/script artifacts are required before a reproduction exception can be accepted.

### B3 — local sequence provenance is weak

The three reproduction sequences and the ten inventory sequences are scattered copies from third-party tracker repositories. Their image and annotation identity relative to a canonical OTB100 release is not established. Autoregressive divergence can amplify even small image-decoder or file-content differences, but that explanation is currently only an interpretation.

A hash comparison across duplicate local copies and, where available, a canonical OTB source is required.

### B4 — current slice inventory cannot satisfy the locked diagnostic minimum

The inventory has ten total sequences, but only four currently have an independently identified similar-distractor reason: Bolt, Couple, Deer, and Jogging_1.

The locked Stage-4 protocol calls for sequence-disjoint discovery and hold-out coverage totaling at least six discovery sequences plus four additional hold-out sequences with sufficient distractor intervals. The present inventory cannot support that requirement.

Stage 4A therefore also has a data-coverage blocker, independently of the reproduction mismatch.

### B5 — whole-MRM ablation is broader than the surviving novelty question

`MemoryRetrieval.forward` contains both:

1. the template-conditioned `Retriever`; and
2. a subsequent MLP residual.

The current control returns the MRM input after both components execute. It measures the contribution of the entire MRM, but it cannot attribute a condition-specific effect to retrieval rather than the MLP.

Before Stage 4B, the diagnostic patch must add separate controls and logs for:

- retriever-only contribution;
- MLP-only contribution;
- whole-MRM contribution.

### B6 — T3 template/time contribution is not exposed

The T3 retriever computes per-template/time responses and then applies a channel-wise gate. The current logs expose only the final MRM output and cache shape. The surviving HG6 question explicitly concerns scale and template/time retrieval paths.

Before Stage 4B, instrumentation must expose, without changing baseline behavior:

- pre-gate per-template/time response norms or equivalent contributions;
- gate weights for each template/time path;
- deterministic one-template/time-path controls for T3, if technically feasible without redesign.

## Reproduction-resolution sequence

The next bounded step is `Stage 4A-R`, not Stage 4B.

Required order:

1. preserve the exact previous reproduction adapter and all small machine-readable evidence;
2. build a temporary three-sequence OTB root and run the official `tracking/test.py` / `Tracker.run_sequence` path;
3. compare official-runner output with the custom adapter on identical files;
4. compare raw-file and decoded-RGB hashes across all local duplicate copies;
5. compare official-default runtime settings with the deterministic characterization mode;
6. if available, repeat the same three predeclared sequences in an isolated Linux environment using a Python version that can actually install the pinned Torch 2.0.0/CUDA 11.8 stack;
7. do not assume the README's Python 3.12 line is installable with the pinned Torch command—record resolver evidence and use the nearest valid official-stack environment if necessary;
8. expand only the outcome-independent dataset/slice inventory, without viewing tracker results.

## Decision

**Stage 4A final state: `STAGE4A_INCOMPLETE`.**

Accepted components are preserved. No scientific candidate failure is assigned. Stage 4B remains locked until:

- reproduction is accepted under the protocol's exact-match or documented-environment exception;
- reproduction artifacts are auditable;
- the retrieval/MLP and T3 template-time instrumentation gaps are repaired;
- a sufficient outcome-independent sequence inventory exists for the frozen slice.

## Locked downstream state

- Stage 4A-R: READY
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
