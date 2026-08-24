# HG3 reconciliation and canonicalization checkpoint

**Date:** 2026-08-24  
**Status:** MANAGER CANONICALIZATION COMPLETE; independent Codex cross-check required before HG4/HG5/HG6 begins.

## Inputs

- Reconciled universe: 128 families.
- Reconciled pre-flag scientific-audit queue: 20 families.
- Source normalization: complete through R51.
- Six HG3 flags: SAMURAI, DAM4SAM, MambaLCT, JDTrack, UMDATrack, SiamABC.

## Manager HG3 resolution

- SAMURAI — PASS
- DAM4SAM — PASS
- MambaLCT — PASS
- JDTrack — PASS
- UMDATrack — PASS
- SiamABC — FAIL

Detailed evidence and reasoning: `screening/manager/2026-08-24_hg3_flag_reconciliation.md`.

## Canonical matrix

`screening/candidate_screening_matrix.csv` has now been populated with the 20 reconciled early-gate candidates.

The matrix intentionally contains only early-gate/reproducibility evidence at this checkpoint:

- HG1/HG2/HG3 only;
- HG4/HG5/HG6 remain `PENDING`;
- all S1–S7 score fields remain blank;
- no total score is present;
- no shortlist or baseline decision is present.

SiamABC remains in the matrix with `HG3=FAIL` and `EARLY_GATE_EXCLUDED_HG3_REFERENCE_ONLY` so the exclusion remains auditable rather than disappearing from the record.

After Manager resolution, the active scientific-audit queue is **19 families**, pending independent Codex cross-check of the six flagged decisions.

## Parallel cross-check gate

Codex must independently inspect the six flagged official repositories and return its own PASS/FAIL/PENDING decision without first reading:

- `screening/manager/2026-08-24_hg3_flag_reconciliation.md`;
- the reconciled HG3 values in `screening/candidate_screening_matrix.csv`.

Manager and Codex results are then compared. Any disagreement is resolved against pinned official sources before the queue is frozen.

## Stop boundary

Until the independent cross-check is reconciled:

- HG4/HG5/HG6: **NOT STARTED**
- S1–S7 soft scoring: **NOT STARTED**
- primary shortlist: **NONE**
- main baseline: **NONE**
- proposed architecture: **NONE**
