# Stage 4C2 — SpikeTrack one-shot frozen-predictor hold-out protocol

**Date:** 2026-08-28  
**Status:** LOCKED BEFORE HOLD-OUT EXECUTION  
**Prerequisite:** `screening/reconciliation/2026-08-28_stage4C1_reconciliation.md`

## 1. Purpose

Stage 4C2 performs the one-shot sequence-disjoint hold-out test of the exact discovery-frozen predictor and physical whole-MRM1 skip. It evaluates Criterion D only.

Stage 4C2 does not refit or reinterpret the predictor, select a probability threshold, design a routing architecture, assign final `DIAG_PASS`/`DIAG_FAIL`, assign S1–S7, select a main baseline, or make a Jetson deployment claim.

## 2. Locked Criterion-D decision

For every eligible hold-out frame:

- oracle label `y = 1` when `IoU_physical_whole_MRM1_skip - IoU_baseline > 0`;
- oracle label `y = 0` when the benefit is `<= 0`, including exact ties;
- frozen predictor probability `p` is interpreted exactly as `P(y=1)`;
- constant comparator probability is fixed at `0.49409780775716694`.

Criterion D passes only when both hold on the complete hold-out frame set:

1. frozen-predictor AUROC `>= 0.65`;
2. frozen-predictor Brier score is strictly lower than the constant-comparator Brier score.

No confidence interval or subgroup may rescue a failed complete-set point estimate.

## 3. Manager predictor seal

Read and verify:

`screening/manager/2026-08-28_stage4C2_predictor_seal.json`

Required hashes:

- source SHA: `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`;
- checkpoint SHA-256: `cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df`;
- config SHA-256: `9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8`;
- frozen-slice normalized-LF SHA-256: `bc52bd7ec6277a76e6da69346a84a8f9d801e2fee9cd92634a60cf9f119ea11a`;
- physical-skip patch SHA-256: `c2ccef6b07818ab3d08c99258f9e28abd0e6e7c56679a3573a4ca9e84f3938aa`;
- frozen predictor SHA-256: `3be9039dceb2d9db4589edcb419232ec77d45ff36f1d779ae9a617ab03a9d0f2`;
- feature-schema SHA-256: `260bdeecf5afa60bd79465863ce07ed194b6b6e327d7f32c8b5f17c75823a677`;
- Stage-4C1 hold-out-seal SHA-256: `e51ff574e99b06d098987d9e7665939f04b881608083037293fa5774171f7d55`.

Any mismatch stops execution before hold-out images are opened.

## 4. Frozen predictor contract

Use exactly:

- StandardScaler statistics in the frozen predictor JSON;
- coefficient vector and intercept in the frozen predictor JSON;
- `C = 0.01` as provenance only; no refit is permitted;
- exact 12-feature order and formulas;
- probability orientation `P(oracle_skip_benefit > 0)`.

Forbidden:

- scaler/model refit;
- feature add/drop/reorder;
- coefficient/intercept modification;
- probability inversion (`1-p`);
- label inversion;
- threshold selection;
- calibration refit;
- class weighting;
- constant-comparator modification;
- physical-skip-patch modification;
- using hold-out outcomes to reinterpret feature direction.

## 5. Manual frozen-model preflight

Before unsealing hold-out execution, reconstruct prediction from JSON using only the frozen numerical contract:

1. `z_j = (x_j - scaler_mean_j) / scaler_scale_j`;
2. `logit = intercept + Σ coefficient_j * z_j`;
3. `p = sigmoid(logit)` with numerically stable evaluation.

On discovery feature rows only, compare this manual implementation against a reconstructed `sklearn` logistic object populated from the same frozen scaler/coefficient values, without fitting.

Required maximum probability difference: `<= 1e-12`.

This preflight may not refit anything and may not access hold-out outcomes.

## 6. One-shot execution rule

The complete Stage-4C2 command, frozen hashes and expected output paths must be written to the command log before opening any hold-out image.

If a technical failure occurs:

- **before** any hold-out feature, prediction, IoU, oracle label or probability row is written, a clean restart is permitted only when the failure and zero-outcome boundary are logged;
- **after** any hold-out outcome row is written or inspected, no rerun, code fix, feature change or model change is allowed without Manager reconciliation; stop as `STAGE4C2_INCOMPLETE_AFTER_UNSEAL`.

The hold-out evaluation count is one. Repeated runs to seek a favorable result are prohibited.

## 7. Exact hold-out allowlist

Execute exactly the eight frozen `HOLDOUT` pairs:

- `R3-H01`;
- `R3-H02`;
- `R3-H03`;
- `R3-H04`;
- `R3-H05`;
- `R3-H06`;
- `R3-H07`;
- `R3-H08`.

Expected total frozen frame rows across primary and control intervals: **326**.

No discovery pair may be rerun for model selection. Discovery artifacts may be read only for sealed provenance verification and the manual frozen-model preflight.

No non-frozen OTB sequence or frame may be used.

## 8. Sequence and state execution contract

For every unique hold-out source sequence:

- initialize once from the official sequence start;
- run the official baseline prefix sequentially through the maximum frozen frame needed;
- do not reinitialize from GT at interval start;
- at `interval_start - 1`, snapshot the same complete tracker/model/RNG state contract accepted in Stage 4B/C1;
- clone the snapshot into baseline and physical whole-MRM1-skip interval branches;
- run the identical frozen interval frames.

The physical branch uses the exact sealed patch and must again show:

- MRM1 forward count = 0;
- MRM1 Retriever count = 0;
- MRM1 MLP count = 0;
- MRM1 internal operator count = 0;
- MRM2–MRM6 unchanged.

No zero-residual, MLP-only, Retriever-only, T3 or alternative-MRM branch is permitted in Stage 4C2.

## 9. Feature extraction contract

Capture exactly the frozen 12 pre-MRM1 features from the baseline pre-MRM state before MRM1 executes. Use the same history/cold-start semantics as Stage 4C1.

Features must not use:

- GT or IoU;
- manual distractor boxes;
- ambiguity/tier;
- primary/control side;
- pair/sequence/class/stratum ID;
- post-MRM values;
- hold-out aggregate statistics.

No additional network/backbone pass is allowed.

Record feature-extraction latency, but do not change feature formulas.

## 10. Oracle-label and probability generation

For each eligible hold-out frame:

- compute baseline IoU and physical-skip IoU from the two state-matched branches;
- compute exact oracle skip benefit;
- assign the binary label with the frozen `>0` rule;
- compute the frozen predictor probability by the sealed manual JSON formula;
- compute the constant comparator probability as `0.49409780775716694`.

All rows must be generated before aggregate Criterion-D metrics are inspected.

If the complete hold-out labels contain only one class, AUROC is undefined and Criterion D fails. Do not change the label threshold.

## 11. Criterion-D metrics

On the complete eligible hold-out frame set, compute:

- row count;
- positive and negative label counts;
- positive base rate;
- frozen-predictor AUROC;
- frozen-predictor Brier score;
- constant-comparator Brier score;
- Brier improvement = `constant Brier - predictor Brier`;
- calibration table using the same fixed ten equal-width bins as Stage 4C1;
- ECE as descriptive only.

Criterion D passes only if:

- `AUROC >= 0.65`; and
- `Brier improvement > 0`.

Do not flip probabilities even when AUROC is below 0.5.

## 12. Required sensitivity reporting

Sensitivity analyses are descriptive and cannot rescue the complete-set gate.

Report:

- primary versus control side;
- ambiguity level 2 versus 1;
- same-sequence versus cross-sequence controls;
- broad superclass;
- frozen sensitivity strata;
- per-pair AUROC/Brier when both labels occur;
- mean oracle skip benefit by pair and side;
- physical whole-MRM1 interaction on hold-out as descriptive generalization evidence.

Use no new subgroup created after viewing outcomes.

## 13. Statistical sensitivity

Report sequence-clustered and connected-source-component bootstrap intervals for:

- AUROC when bootstrap resample contains both classes;
- predictor Brier;
- constant Brier;
- Brier improvement;
- mean oracle skip benefit.

Use 10,000 resamples and seed `20260828`. Record valid/invalid AUROC resample counts. These intervals are descriptive; the locked Criterion-D gate uses the complete-set point estimates.

## 14. Efficiency characterization

Record on hold-out:

- physical whole-MRM1 call proof;
- model-forward baseline and skip timing as descriptive replication only;
- feature-extraction overhead;
- approximate feature-adjusted skip-path saving;
- peak memory.

Criterion C is not reselected on hold-out. No thresholded conditional policy is executed because no probability threshold is part of the frozen diagnostic predictor.

## 15. Required artifacts

Create bounded machine-readable artifacts for:

- Manager-seal verification;
- one-shot unseal manifest;
- hold-out sequence/prefix execution manifest;
- snapshot/call-path proof;
- hold-out baseline and physical-skip per-frame metrics;
- exact 12-feature rows;
- oracle labels and frozen probabilities;
- complete-set Criterion-D table;
- sensitivity and bootstrap results;
- timing/feature-overhead characterization;
- artifact hashes;
- exact command log.

Do not commit datasets, checkpoints, full images, raw tensors or video.

## 16. Required reports

Create:

- `screening/codex/2026-08-28_stage4C2_execution_report.md`;
- `screening/codex/2026-08-28_stage4C2_criterionD_results.csv`;
- `screening/codex/2026-08-28_stage4C2_sensitivity_results.csv`;
- `screening/codex/2026-08-28_stage4C2_command_log.txt`;
- bounded artifacts under `screening/codex/artifacts/stage4C2_holdout/`;
- exact scripts under `screening/codex/scripts/2026-08-28_stage4C2_*`.

No new physical patch is allowed. Use the sealed Stage-4C1 patch byte-for-byte.

## 17. Allowed Codex conclusions

- `STAGE4C2_CRITERION_D_PASS_READY_FOR_FINAL_DIAGNOSTIC_REVIEW`;
- `STAGE4C2_CRITERION_D_FAIL`;
- `STAGE4C2_INCOMPLETE_SEAL_OR_EXECUTION`;
- `STAGE4C2_INCOMPLETE_AFTER_UNSEAL`;
- `STAGE4C2_INVALID_FROZEN_PREDICTOR_MUTATION`.

Codex does not assign final `DIAG_PASS`/`DIAG_FAIL`.

## 18. Downstream gate

Manager Stage 4D will assign:

- `DIAG_PASS` only when A, B, C and D are all accepted;
- `DIAG_FAIL` when Criterion D fails under the frozen one-shot test;
- `DIAG_PENDING` only for a genuine unresolved execution blocker, not weak metrics.

Only `DIAG_PASS` permits S1–S7 scoring and main-baseline consideration.

## Locked state

- Stage 4C1: **COMPLETE / ACCEPTED**;
- Stage 4C2: **READY FOR ONE-SHOT HOLD-OUT**;
- Stage 4D: **LOCKED**;
- final diagnostic decision: **NOT ASSIGNED**;
- S1–S7: **NOT STARTED**;
- primary shortlist: **NONE**;
- main baseline: **NONE**;
- proposed architecture: **NONE**.
