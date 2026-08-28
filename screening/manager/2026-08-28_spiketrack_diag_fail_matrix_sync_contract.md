# SpikeTrack final diagnostic matrix-sync contract

**Date:** 2026-08-28  
**Status:** MECHANICAL UPDATE REQUIRED

Apply only to `CX007` in `screening/candidate_screening_matrix.csv`.

Keep:

- `hg1_publication = PASS`;
- `hg2_task_modality = PASS`;
- `hg3_reproducibility = PASS`;
- `hg4_rtx3060 = PASS`;
- `hg5_nano_plausibility = PASS`;
- `hg6_novelty = PASS`.

HG6 is a literature/mechanism novelty gate and is not rewritten by the later empirical diagnostic failure.

Keep all S1–S7 and total-score fields blank.

Set:

`decision_state = EXCLUDED_DIAGNOSTIC_CRITERION_D_FAIL_REFERENCE_ONLY`

Set `evidence_notes` to a concise statement containing:

- Stage-4D final reconciliation;
- A/B/C passed under their locked contracts;
- frozen one-shot D failed;
- hold-out AUROC `0.48153585544889893 < 0.65`;
- predictor Brier `0.2575449361739645` was worse than constant Brier `0.24996241633654945`;
- no soft scoring;
- reference/null-result only under the current gap.

Set:

`last_verified = 2026-08-28`

Do not change any other candidate or matrix field.

Validation:

- 54 columns in every row;
- 20 unique candidate IDs;
- all S1–S7 and total-score fields blank;
- only the three intended CX007 cells change.
