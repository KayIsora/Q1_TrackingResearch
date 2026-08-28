# Stage 4C1 — SpikeTrack physical MRM1 skip and discovery predictor-freeze protocol

**Date:** 2026-08-28  
**Status:** LOCKED BEFORE STAGE-4C EXECUTION  
**Prerequisite:** `screening/reconciliation/2026-08-28_stage4B_discovery_reconciliation.md`

## 1. Purpose

Stage 4C1 performs two discovery-only tasks:

1. test **Criterion C** by implementing real non-execution of whole MRM1 and measuring actual model-forward latency saving;
2. construct and freeze a simple diagnostic predictor, using discovery data only, for later one-shot **Criterion D** evaluation on the sealed hold-out set.

Stage 4C1 does not execute hold-out outcomes, assign final `DIAG_PASS`/`DIAG_FAIL`, assign S1–S7, select a main baseline, or approve a proposed architecture.

## 2. Accepted Stage-4B result

The Stage-4B primary path is locked to **whole MRM1**:

- whole-MRM1 interaction: `-0.027883963367728869`;
- discovery interpretation: MRM1 is conditionally harmful under distractor ambiguity;
- selected physical action: bypass whole MRM1 when a pre-MRM signal predicts that bypass is useful.

The bounded component refinement shows that the discovery interaction is associated with the MRM1 MLP residual, not the Retriever. Therefore:

- whole-MRM1 physical skip is the **only Criterion-C primary**;
- MRM1-MLP physical skip is permitted as secondary mechanism characterization;
- Retriever-only physical skip is not a Criterion-C candidate;
- no other MRM/group may be introduced.

## 3. Exact source contract

- official repository: `faicaiwawa/SpikeTrack`;
- pinned source SHA: `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`;
- primary config: `experiments/spiketrack/spiketrack_s256_t1.yaml`;
- checkpoint SHA-256: `cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df`;
- accepted Stage-4A diagnostic patch SHA-256: `d4a1065a32ef6da6132e4f9f7980f727e9109bb00e2e2370398b1e90de5a713a`;
- frozen slice normalized-LF SHA-256: `bc52bd7ec6277a76e6da69346a84a8f9d801e2fee9cd92634a60cf9f119ea11a`;
- canonical OTB root remains the accepted Figshare package.

Use the same local operational baseline boundary as Stage 4B. No claim of exact author-raw-result reproduction is permitted.

## 4. Discovery-only execution allowlist

Stage 4C1 may execute only the 12 frozen `DISCOVERY` pairs:

- R3-D01 through R3-D12.

The eight `HOLDOUT` pairs remain sealed. Stage 4C1 may read only their IDs, row hashes and frozen bounds for seal verification. It must not run baseline, physical skip, feature extraction, IoU, label generation, predictor inference or timing on any hold-out interval.

Any hold-out outcome access yields:

`STAGE4C1_INVALID_HOLDOUT_EXPOSURE`.

## 5. Physical whole-MRM1 skip semantics

Implement a diagnostic selector that returns the MRM1 input **before** invoking either:

- MRM1 Retriever;
- MRM1 MLP.

Required:

- Retriever call count = 0 under physical whole-MRM1 skip;
- MLP call count = 0 under physical whole-MRM1 skip;
- no MRM1 internal operator executes;
- MRM2–MRM6 remain unchanged;
- model/tracker state handling is otherwise identical.

This is a diagnostic physical path, not a proposed router architecture.

## 6. Physical-skip semantic parity

On every frozen discovery interval, from the exact same prefix snapshot:

- run the accepted Stage-4B whole-MRM1 zero-residual control;
- run physical whole-MRM1 skip;
- compare integer prediction, floating prediction, score map, confidence and complete continuation state.

Required tolerance:

`max_abs <= 1e-6`, preferably exact `0.0`.

If physical skip does not reproduce the accepted whole-MRM1 diagnostic semantics, Stage 4C1 is incomplete.

### Secondary MLP path

A physical MRM1-MLP skip may be implemented after the Retriever output, before the MLP call. It must match the accepted MLP-only diagnostic control within the same tolerance. It is descriptive and cannot rescue a failed whole-MRM1 Criterion C.

## 7. Operator and call-path proof

Record for baseline, whole-MRM1 physical skip and optional MLP physical skip:

- forward-hook call counts;
- Retriever call counts;
- MLP call counts;
- CUDA-profiler/operator trace or equivalent bounded execution evidence;
- output/state parity hash;
- `physical_skip=true/false`.

Masking or zeroing after an operator has executed does not count as physical skip.

## 8. Criterion-C timing contract

### Environment

Primary Criterion-C timing uses the same available GPU/software environment as Stage 4B unless an already available RTX 3060 environment can be used without provisioning new hardware. The exact device is recorded; desktop evidence is not Jetson evidence.

### Timing boundary

Primary metric:

- steady-state neural model-forward latency only;
- batch size 1;
- FP32;
- diagnostics/norm logging disabled;
- CUDA synchronization immediately before and after the measured forward;
- snapshot creation/restore, image decoding, crop preparation and result persistence excluded.

Secondary metrics:

- end-to-end tracker interval latency;
- MRM1 call-path time;
- peak allocated/reserved GPU memory.

### Warm-up and repetitions

- at least 30 unmeasured warm-up forwards;
- three complete repetitions of baseline and whole-MRM1 physical skip over the same 24 frozen discovery intervals;
- use the same state-matched interval forks;
- execution order alternates by pair and repetition according to fixed seed `20260828` to reduce order/thermal bias;
- persist per-frame CUDA timing rows.

### Criterion-C estimate

`latency_saving = 1 - median(skip_model_forward_ms) / median(baseline_model_forward_ms)`.

Criterion C passes when:

- whole-MRM1 physical semantics and call-path proof pass; and
- median model-forward latency saving is at least `0.05` (5%).

Report a sequence-clustered paired bootstrap 95% CI and first-versus-last-quartile timing sensitivity, but the prelocked gate remains the 5% point estimate.

If whole-MRM1 saving is below 5%, conclude:

`STAGE4C1_CRITERION_C_FAIL`.

Do not substitute MLP-only physical skip or another MRM to rescue the gate.

## 9. Discovery oracle skip-benefit label

For every discovery frame represented in a frozen primary/control interval:

`oracle_skip_benefit = IoU_physical_whole_MRM1_skip - IoU_baseline`.

Binary diagnostic label:

- `1` when `oracle_skip_benefit > 0`;
- `0` when `oracle_skip_benefit <= 0`.

Exact numerical ties are negative. No margin threshold may be tuned from outcomes.

The label is offline diagnostic supervision only. It is not available at deployment and must never be used as an input feature.

## 10. Fixed pre-MRM feature schema

Extract only values available immediately before MRM1 executes. The predictor receives the following fixed scalar features in this exact order:

1. `previous_confidence`;
2. `previous_center_displacement_normalized_by_predicted_scale`;
3. `previous_log_area_ratio`;
4. `mrm1_input_abs_mean`;
5. `mrm1_input_std`;
6. `mrm1_input_rms`;
7. `mrm1_input_nonzero_ratio`;
8. `template_memory_abs_mean`;
9. `template_memory_std`;
10. `template_memory_rms`;
11. `template_memory_nonzero_ratio`;
12. `search_to_template_rms_ratio`.

Definitions:

- previous motion/scale use only tracker predictions, never GT;
- tensor statistics use the current pre-MRM1 input and already cached template memory;
- RMS is `sqrt(mean(x^2))`;
- nonzero ratio is the fraction of elements not equal to zero under the actual inference tensor;
- division uses a fixed epsilon `1e-12`.

Forbidden inputs:

- GT boxes or IoU;
- manual distractor boxes;
- frozen ambiguity level/tier;
- primary/control side;
- pair ID or sequence ID;
- source class/sensitivity stratum;
- future confidence or post-MRM values;
- MRM1 Retriever/MLP output;
- any hold-out-derived statistic.

If a mandatory feature cannot be obtained before MRM1 without an additional backbone/network pass, Stage 4C1 must stop and request Manager reconciliation; it may not silently replace or drop features.

Feature-extraction latency and memory overhead must be measured. The diagnostic probe is not yet a deployable module, but it may not invoke another neural network or repeat the backbone.

## 11. Fixed predictor family

Use only:

- `StandardScaler` fitted on training folds;
- L2-regularized logistic regression;
- deterministic solver and `random_state=20260828` where supported;
- hyperparameter grid `C ∈ {0.01, 0.1, 1.0, 10.0, 100.0}`;
- no class weighting;
- no feature selection;
- no nonlinear model;
- no manual ambiguity label.

### Discovery grouped validation

- group by the connected source components already locked in Stage 4B;
- use leave-one-connected-component-out folds;
- fit scaler/model on training components only;
- pool all out-of-fold probabilities;
- choose `C` by highest pooled OOF AUROC;
- tie-break by lower pooled OOF Brier score;
- final tie-break by smaller `C`.

If discovery labels contain fewer than 20 positive or fewer than 20 negative frames, report `PREDICTOR_LABEL_SUPPORT_INSUFFICIENT` and stop before hold-out.

Discovery OOF performance is descriptive; it is not Criterion D and does not create a new pass/fail threshold.

## 12. Frozen predictor artifact

After selecting `C`, fit the scaler and logistic regression once on all discovery rows and freeze:

- exact feature order and formulas;
- scaler mean/scale;
- coefficient vector and intercept;
- chosen `C`;
- discovery positive base rate;
- source/config/checkpoint/physical-skip patch hashes;
- code and dependency versions;
- training row count and group membership;
- OOF AUROC, Brier score and calibration summary;
- feature-extraction overhead;
- SHA-256 of every predictor artifact.

No probability threshold is selected because Criterion D uses AUROC and Brier score.

The frozen base-rate comparator for Stage 4C2 is the constant probability equal to the **discovery positive base rate**.

## 13. Hold-out seal package

Create a Stage-4C1 hold-out seal containing only:

- the eight pair IDs and row hashes;
- frozen-slice SHA-256;
- physical-skip patch SHA-256;
- predictor artifact SHA-256;
- feature-schema SHA-256;
- status `NOT_EXECUTED_STAGE4C1`.

Stage 4C2 cannot begin until Manager verifies and commits this seal.

## 14. Allowed Stage-4C1 conclusions

- `STAGE4C1_CRITERION_C_FAIL`;
- `STAGE4C1_PREDICTOR_FREEZE_READY_FOR_MANAGER_REVIEW`;
- `STAGE4C1_INCOMPLETE_PHYSICAL_SKIP_OR_PREDICTOR`;
- `STAGE4C1_INVALID_HOLDOUT_EXPOSURE`.

Codex does not assign final `DIAG_PASS`/`DIAG_FAIL`.

## 15. Required artifacts

Create bounded text/CSV/JSON artifacts for:

- physical-skip patch and call-path proof;
- semantic parity against Stage-4B zero-residual controls;
- discovery timing rows and Criterion-C summary;
- baseline/physical-skip discovery per-frame metrics;
- pre-MRM feature rows and oracle labels;
- connected-component OOF predictions;
- hyperparameter audit;
- frozen scaler/model coefficients;
- predictor manifest and hashes;
- hold-out seal;
- exact command log;
- execution report;
- exact reproducibility scripts.

Large datasets, checkpoints and raw tensors remain external.

## 16. Downstream gate

Only when Manager accepts:

- Criterion C PASS;
- physical-skip semantic parity;
- call-path proof;
- predictor/feature freeze;
- intact hold-out seal;

may Stage 4C2 execute the frozen hold-out once.

## Locked state

- Stage 4B: **COMPLETE / A+B ACCEPTED**;
- Stage 4C1: **READY**;
- Stage 4C2: **LOCKED**;
- final diagnostic decision: **NOT ASSIGNED**;
- S1–S7: **NOT STARTED**;
- primary shortlist: **NONE**;
- main baseline: **NONE**;
- proposed architecture: **NONE**.
