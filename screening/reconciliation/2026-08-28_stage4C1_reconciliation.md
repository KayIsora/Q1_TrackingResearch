# Stage 4C1 — SpikeTrack physical-skip and predictor-freeze reconciliation

**Date:** 2026-08-28  
**Status:** `STAGE4C1_ACCEPTED_STAGE4C2_READY_WITH_HIGH_CRITERION_D_RISK`  
**Source commit reviewed:** `c6c9bd16371591d6966063552801479b34581ba4`

## Boundary

This reconciliation decides whether Stage 4C1 validly establishes Criterion C and a frozen discovery-only predictor artifact for a one-shot Stage 4C2 hold-out test. It does not execute hold-out outcomes, assign final `DIAG_PASS`/`DIAG_FAIL`, assign S1–S7, select a main baseline, or approve a proposed architecture.

## 1. Repository and execution acceptance

Manager accepts the Stage-4C1 execution package:

- exactly 12 discovery pairs and 24 discovery intervals were executed;
- zero hold-out pairs/outcomes were executed or read;
- the eight-row hold-out seal binds the frozen row hashes, frozen-slice hash, physical-skip patch hash, predictor hash and feature-schema hash;
- the source, config, checkpoint, frozen slice and patch hashes match the locked contract;
- whole-MRM1 physical non-execution returns before the MRM1 Retriever and MLP calls;
- under physical whole-MRM1 skip, MRM1 forward, Retriever, MLP and internal-operator counts are all zero while MRM2–MRM6 remain unchanged;
- physical whole-MRM1 output and continuation state match the accepted Stage-4B zero-residual semantics exactly;
- optional MLP-only physical skip also matches the accepted MLP-only diagnostic semantics exactly;
- no direct SpikeTrack source modification was committed to the Q1 repository; the scientific code change is preserved as a unified diagnostic patch plus execution scripts/artifacts.

## 2. Criterion C decision — ACCEPTED PASS

The locked Criterion-C point estimate is:

- baseline median model-forward latency: `261.1527999979444 ms`;
- physical whole-MRM1 skip median: `246.88769999920623 ms`;
- saving: `5.462357669092743%`;
- locked minimum: `5%`.

Physical semantics and call-path proof pass, so Criterion C passes under the predeclared rule.

### Required caution

The result is positive but marginal:

- sequence-clustered 95% CI: `[2.493581%, 8.461938%]`;
- the lower confidence limit is below the 5% gate;
- the result was measured on an NVIDIA GeForce MX250 in FP32, not on the RTX 3060 development target or Jetson Nano;
- the measured median pre-MRM feature-extraction overhead is `1.698 ms`.

A simple additive characterization gives approximately:

`1 - (246.8877 + 1.6980) / 261.1528 = 4.812%`

saving on a frame that is actually skipped. This is a derived warning, not a replacement Criterion-C gate, because the locked gate measures physical path saving and treats feature overhead separately. An eventual conditional policy will pay feature overhead on all routed frames and will skip only a subset, so its average end-to-end saving may be materially lower.

No Jetson or deployment-speed claim is authorized from Criterion C.

## 3. Predictor artifact acceptance

Manager accepts that the discovery predictor was created exactly under the locked family:

- 12 pre-MRM scalar features in the prescribed order;
- no GT, IoU, ambiguity labels, side, pair ID, sequence ID, class, post-MRM values or hold-out statistics as model inputs;
- no additional backbone/network pass;
- StandardScaler plus L2 logistic regression only;
- `C ∈ {0.01, 0.1, 1, 10, 100}`;
- leave-one-connected-component-out discovery validation;
- no class weighting, feature selection, nonlinear model or probability threshold;
- 293 positive and 300 negative discovery labels;
- selected `C = 0.01` under the locked selection rule;
- final scaler/model fitted once on all discovery rows and frozen by SHA-256.

The following artifacts are sealed:

- frozen predictor SHA-256: `3be9039dceb2d9db4589edcb419232ec77d45ff36f1d779ae9a617ab03a9d0f2`;
- feature schema SHA-256: `260bdeecf5afa60bd79465863ce07ed194b6b6e327d7f32c8b5f17c75823a677`;
- physical-skip patch SHA-256: `c2ccef6b07818ab3d08c99258f9e28abd0e6e7c56679a3573a4ca9e84f3938aa`;
- frozen slice SHA-256: `bc52bd7ec6277a76e6da69346a84a8f9d801e2fee9cd92634a60cf9f119ea11a`;
- frozen constant comparator probability: `0.49409780775716694`.

## 4. Predictor-risk finding

The frozen predictor has weak discovery generalization:

- pooled grouped OOF AUROC: `0.47187713310580204`;
- pooled grouped OOF Brier score: `0.25791968644449575`;
- constant discovery-base-rate Brier score: `0.24996516412672865`;
- discovery Brier improvement over the constant comparator: `-0.00795452231776711`.

Thus, on grouped discovery OOF predictions, the model ranks below chance and is worse calibrated in Brier loss than the constant base-rate comparator.

This is a serious scientific warning, but it was explicitly not a Stage-4C1 pass/fail gate. Manager therefore does not add a new post-hoc gate after seeing the result. The only valid next action is the predeclared one-shot hold-out test using the predictor exactly as frozen.

The following are prohibited before or after hold-out unsealing:

- refitting the scaler/model;
- adding, removing or reordering features;
- changing `C`;
- flipping labels or replacing probability `p` with `1-p`;
- selecting a probability threshold;
- changing the constant comparator;
- changing the physical skip patch;
- using hold-out observations to reinterpret feature direction.

## 5. Stage-4C2 decision

Stage 4C2 is unlocked for exactly one frozen hold-out evaluation.

Criterion D will pass only if both hold on the complete sealed hold-out frame set:

1. frozen-predictor AUROC `>= 0.65`;
2. frozen-predictor Brier score is strictly lower than the Brier score of the constant probability `0.49409780775716694`.

Discovery OOF performance suggests a high risk of Criterion-D failure. That risk does not authorize cancellation, inversion or tuning because the hold-out gate was predeclared to provide the definitive falsification test.

## 6. Locked state

- Stage 4C1: **COMPLETE / ACCEPTED**;
- Criterion C: **PASS with narrow-margin and feature-overhead warnings**;
- predictor artifact: **FROZEN**;
- hold-out seal: **INTACT**;
- Stage 4C2: **READY FOR ONE-SHOT EXECUTION**;
- final diagnostic decision: **NOT ASSIGNED**;
- S1–S7: **NOT STARTED**;
- primary shortlist: **NONE**;
- main baseline: **NONE**;
- proposed architecture: **NONE**.
