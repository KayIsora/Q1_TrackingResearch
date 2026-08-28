# Stage 4B — SpikeTrack discovery diagnostic reconciliation

**Date:** 2026-08-28  
**Status:** `STAGE4B_AB_ACCEPTED_STAGE4C1_READY`  
**Source commit reviewed:** `f5c6fdc617036af8a5c0ca59a2a96367debe4f5c`

## Boundary

This reconciliation decides whether the locked discovery evidence satisfies Stage-4 Criteria A and B. It does not assign final `DIAG_PASS`/`DIAG_FAIL`, execute or expose hold-out outcomes, assign S1–S7, select a main baseline, or approve a proposed architecture.

The final diagnostic decision still requires:

- Criterion C — real physical non-execution with at least 5% median model-forward latency saving;
- Criterion D — a frozen low-cost pre-MRM predictor validated once on the sequence-disjoint hold-out set with AUROC at least 0.65 and calibration improvement over the frozen base-rate predictor.

## 1. Execution and provenance acceptance

Manager accepts the Stage-4B execution package:

- frozen-slice hash matched the Manager-locked source;
- all 12 discovery pairs and 24 discovery intervals were represented;
- hold-out outcome rows consumed/executed were zero and the eight-row seal was preserved;
- source SHA, config, checkpoints and diagnostic patch hashes were recorded;
- the local operational baseline boundary was respected; no author-raw-result parity claim was made;
- no-ablation parity was exact (`max_abs_diff=0.0`);
- every unique discovery source sequence initialized once from the official sequence start;
- interval branches restored the exact prefix snapshot rather than reinitializing from GT;
- state-snapshot parity passed for integer predictions, float predictions, score maps and confidence;
- the nine Criterion-B modes were exactly the predeclared six individual MRMs and three groups;
- Holm correction covered exactly nine tests;
- all Stage-4B controls remained `physical_skip=false`;
- Retriever/MLP and T3 refinements were executed only after the primary Criterion-B family passed.

The temporary Manager review export used a non-main branch and did not change scientific artifacts on `main`.

## 2. Criterion A decision — ACCEPTED PASS

### Locked result

- IoU weakness: `0.1369987845343785`;
- primary-sequence clustered 95% CI: `[0.0018879570501517985, 0.3171168981269434]`;
- locked minimum: `0.05`;
- primary p-value: `0.04739526047395261`.

The IoU metric therefore satisfies the predeclared Criterion-A rule.

Failure-rate weakness was `0.15333333333333335`, but its primary 95% CI `[-0.03, 0.41818181818181815]` included zero, so that metric did not independently pass.

### Required caution

Criterion A is accepted according to the locked primary decision rule, but the evidence is not broad or uniformly strong:

- the connected-source-component IoU CI `[-0.013529223122019495, 0.3073738587768596]` includes zero;
- same-sequence controls show only `0.018108` mean IoU weakness;
- the complete-set estimate is strongly influenced by cross-scene/activity pairs, particularly Basketball and Bolt;
- removing both Basketball and Bolt from a descriptive, non-gating check reduces mean IoU weakness to approximately `0.030655`, below the locked effect threshold.

These observations do not retroactively change the predeclared gate. They narrow the interpretation:

> On the frozen discovery package, SpikeTrack-S256-T1 exhibits a statistically positive complete-set IoU weakness under the locked primary clustering rule, but the size and generality of the effect remain source-design-sensitive and require hold-out scrutiny.

No claim of a universal similar-distractor weakness is authorized from Stage 4B alone.

## 3. Criterion B decision — ACCEPTED PASS

Only `MRM1` passed the locked nine-test family:

- mean whole-MRM1 interaction: `-0.027883963367728869`;
- primary 95% CI: `[-0.056569693436362728, -0.00807008117216532]`;
- component 95% CI: `[-0.056923559634947808, -0.0075929622434032836]`;
- unadjusted p: `0.0013998600139986002`;
- Holm-adjusted p: `0.012598740125987402`;
- absolute effect exceeds the locked `0.02` minimum.

The direction is negative under the locked contribution definition:

`contribution = IoU_baseline - IoU_ablation`.

Therefore:

- distractor mean contribution: `-0.025588031535712052` — bypassing MRM1 improved IoU on average by about 0.0256 on discovery distractor intervals;
- control mean contribution: `0.002295931832016818` — MRM1 was approximately neutral/slightly beneficial on controls;
- the accepted interpretation is **condition-specific harmful utility**, not “more retrieval is needed under ambiguity.”

The selected Stage-4C path is consequently:

> physically bypass whole MRM1 on frames where a pre-MRM signal predicts that MRM1 is harmful or unnecessary.

This remains a diagnostic hypothesis, not an approved architecture.

## 4. Component refinement and mechanism boundary

Manager recomputed the bounded refinements from the committed per-frame CSV using the same 10,000-resample primary-sequence and connected-component bootstrap. The machine-readable result is recorded in:

`screening/manager/2026-08-28_stage4B_component_refinement_audit.csv`.

### MLP-only bypass

- mean interaction: `-0.02870421443065085`;
- primary 95% CI: `[-0.06625292629624764, -0.006317930771934768]`;
- component 95% CI: `[-0.06637128130804014, -0.005893451833787825]`.

### Retriever-only bypass

- mean interaction: `-0.001405613288193877`;
- primary 95% CI: `[-0.016121911727856493, 0.01641288107655163]`;
- component 95% CI: `[-0.016315097126560898, 0.01922767943523202]`.

### T3 template/time paths

All three selected T3 MRM1 template-path interactions were small (`0.0043–0.0060`) and their primary and component confidence intervals included zero.

### Scientific consequence

The discovery interaction localizes to the **MRM1 MLP residual**, not to the template-conditioned Retriever or an individual T3 template/time path.

This materially narrows the surviving scientific language:

- Stage 4B supports **ambiguity-conditioned MRM1 block/MLP utility**;
- Stage 4B does **not** support a claim that template-memory retrieval itself is the responsible interaction;
- before any proposed method or final baseline selection, novelty headroom must be reconsidered against generic dynamic MLP/block gating and conditional residual suppression;
- Stage 4C may still test whole-MRM1 physical non-execution because whole MRM1 was the predeclared primary passing path and is the only variant likely to yield the required compute saving.

## 5. Robustness sensitivity of the selected interaction

MRM1's direction is negative in most frozen discovery pairs, but the effect size is influenced by Basketball:

- full mean interaction: `-0.027884`;
- descriptive leave-Basketball-out mean: approximately `-0.016200`, below the locked `0.02` magnitude threshold.

This leave-one-sequence-out value was not a predeclared gate and cannot overturn the locked result. It is retained as a fragility warning for Stage 4C hold-out validation.

## 6. Stage-4B decision

- Criterion A: **PASS — accepted with fragility/source-design warning**;
- Criterion B: **PASS — MRM1 only**;
- selected primary physical path: **whole MRM1**;
- component explanation: **MRM1 MLP residual**, not Retriever;
- hold-out status: **SEALED / NOT EXECUTED**;
- Stage 4B: **COMPLETE**;
- Stage 4C1: **READY**;
- Stage 4C2 hold-out execution: **LOCKED pending Manager review of frozen physical-skip and predictor artifacts**.

## 7. Stage-4C sequencing decision

To prevent hold-out leakage, Stage 4C is split:

### Stage 4C1 — discovery-only physical skip and predictor freeze

- implement actual whole-MRM1 non-execution;
- prove semantic parity with the accepted whole-MRM1 zero-residual control;
- test Criterion C on discovery only;
- characterize optional MLP-only physical skip as secondary mechanism evidence;
- extract only pre-MRM, inference-available features;
- derive oracle skip-benefit labels from discovery baseline versus physical-skip branches;
- train/tune a fixed simple diagnostic predictor using grouped discovery validation;
- freeze the feature schema, preprocessing, coefficients, threshold-free probability output, hyperparameter and discovery base rate;
- do not access any hold-out outcome.

### Stage 4C2 — one-shot hold-out validation

Only after Manager accepts Stage 4C1 and commits the predictor seal:

- execute baseline and the frozen whole-MRM1 physical skip on the eight held-out pairs;
- calculate oracle labels without tuning;
- evaluate the already frozen predictor once;
- apply the locked Criterion-D thresholds.

## Locked state

- Stage 4B: **COMPLETE / A+B ACCEPTED**;
- Stage 4C1: **READY**;
- Stage 4C2: **LOCKED**;
- final diagnostic decision: **NOT ASSIGNED**;
- S1–S7: **NOT STARTED**;
- primary shortlist: **NONE**;
- main baseline: **NONE**;
- proposed architecture: **NONE**.
