# Stage 4B — SpikeTrack discovery diagnostic protocol

**Date:** 2026-08-26  
**Status:** LOCKED BEFORE TRACKER EXECUTION  
**Entry condition:** the 20-pair diagnostic slice is frozen; only the 12 discovery pairs may be executed in Stage 4B.

## 1. Purpose

Stage 4B tests the first two locked diagnostic criteria:

- **Criterion A:** SpikeTrack-S256-T1 is measurably weaker on the frozen similar-distractor intervals than on their matched controls.
- **Criterion B:** at least one predeclared MRM or MRM group has condition-dependent marginal utility between distractor and control intervals.

Stage 4B does not perform physical MRM skipping, train a router/predictor, execute the hold-out split, assign final `DIAG_PASS`, score S1–S7, select a baseline, or design a proposed architecture.

## 2. Exact scientific contract

Repository:

- `faicaiwawa/SpikeTrack`
- pinned SHA: `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`

Primary model:

- SpikeTrack-S256-T1;
- exact official checkpoint previously verified by SHA-256;
- official OTB evaluator and canonical OTB source already accepted in Stage 4A.

Controlled comparison:

- SpikeTrack-S256-T3 baseline may be run only as a secondary discovery diagnostic;
- T3 does not replace T1 for the locked Criterion A/B decision.

Instrumentation:

- use the accepted Stage-4A refined patch;
- no-ablation instrumentation must retain output parity;
- all contribution controls in Stage 4B remain `physical_skip=false`.

## 3. Frozen execution allowlist

Read:

`screening/manager/2026-08-25_stage4_spiketrack_diagnostic_slice.csv`

Execute only rows where:

`split = DISCOVERY`.

The 12 allowed pair IDs are:

- R3-D01
- R3-D02
- R3-D03
- R3-D04
- R3-D05
- R3-D06
- R3-D07
- R3-D08
- R3-D09
- R3-D10
- R3-D11
- R3-D12

No interval, bound, control, tier, ambiguity value or sensitivity stratum may be changed.

## 4. Hold-out seal

The eight hold-out pairs are frozen but sealed.

Stage 4B must not:

- run the tracker on their primary or control intervals for diagnostic analysis;
- calculate held-out IoU, failure rate, score, MRM contribution or route utility;
- use held-out observations for mode selection, threshold tuning, subgroup selection or interpretation.

Create a hold-out seal manifest containing only:

- pair IDs;
- sequence/bound hashes;
- frozen-slice file SHA-256;
- statement `NOT_EXECUTED_STAGE4B`.

## 5. Sequence execution and state boundary

### 5.1 Baseline sequence run

For every unique discovery source sequence:

- initialize through the official tracker path at the official sequence start;
- run SpikeTrack-S256-T1 sequentially through the maximum frozen frame required for that sequence;
- persist integer predictions, floating outputs needed for audit, timing boundaries and state events;
- extract metrics only for frozen primary/control intervals.

Do not initialize independently at each interval start.

### 5.2 State-matched interval fork

MRM contribution tests must begin from the same tracker state.

For each frozen interval:

1. run the exact baseline prefix through frame `interval_start - 1`;
2. snapshot all tracker/model state required for deterministic continuation, including current target state, cached template/search state, spike state and any T3 template history where applicable;
3. clone the snapshot into baseline and ablation branches;
4. run every branch on the identical interval frames.

The baseline fork must match the uninterrupted baseline interval prediction within the accepted parity tolerance. If a faithful snapshot/restore cannot be established, Stage 4B is `INCOMPLETE`; reinitializing from GT at the interval start is not an accepted substitute.

## 6. Execution phases and stopping rule

### Phase B-A — Criterion A baseline weakness

Run T1 baseline only on all frozen discovery primary/control intervals.

Compute the predeclared Criterion A analysis in Section 10.

If Criterion A fails:

- stop before MRM ablation mining;
- report `STAGE4B_CRITERION_A_FAIL`;
- Manager will reconcile `DIAG_FAIL` for the current similar-distractor premise.

If Criterion A passes, proceed to Phase B-B.

### Phase B-B — Criterion B primary retrieval screen

Run the following state-matched T1 modes:

- baseline;
- whole-MRM control for MRM1;
- whole-MRM control for MRM2;
- whole-MRM control for MRM3;
- whole-MRM control for MRM4;
- whole-MRM control for MRM5;
- whole-MRM control for MRM6;
- grouped early control `{MRM1, MRM2}`;
- grouped middle control `{MRM3, MRM4}`;
- grouped late control `{MRM5, MRM6}`.

These nine ablation families are the primary Criterion B family.

If Criterion B fails after the locked multiplicity treatment:

- stop;
- report `STAGE4B_CRITERION_B_FAIL`.

If Criterion B passes, proceed to Phase B-C.

### Phase B-C — bounded mechanism refinement

Select one primary passing MRM/group using this locked rule:

1. largest absolute adjusted interaction effect among passing tests;
2. tie: smaller group size;
3. tie: lower MRM index.

For only the selected MRM/group:

- run Retriever-only bypass;
- run MLP-only bypass;
- report which component explains the whole-MRM interaction.

Also run:

- T3 baseline on all discovery intervals;
- when technically valid, the three T3 template/time-path zero-contribution controls for the selected MRM only.

These refinement results do not create a new Criterion B family and may not rescue a failed primary family.

## 7. Metrics

### Primary per-frame outcomes

- target IoU against OTB GT;
- failure indicator `IoU < 0.5`.

### Secondary outcomes

- center error;
- success at IoU 0.5;
- MRM/Retriever/MLP residual norms;
- synchronized model and module latency as characterization only;
- target-versus-manually annotated distractor score/peak margin on the five frozen review frames where mapping is technically valid;
- recovery duration after the frozen event, reported only when an unambiguous recovery definition is available.

Desktop latency is not Jetson Nano evidence and does not satisfy Criterion C.

## 8. Contribution definitions

For mode `m`:

`contribution_m(frame) = IoU_baseline(frame) - IoU_ablation_m(frame)`.

Positive contribution means the removed path helped localization on that frame.

For each frozen pair:

- `contribution_distractor_m` = mean contribution over the primary interval;
- `contribution_control_m` = mean contribution over the matched control interval;
- `interaction_m` = `contribution_distractor_m - contribution_control_m`.

A positive interaction means the retrieval path is more useful under distractor ambiguity. A negative interaction may be reported as a condition-specific harmful path only when stable and scientifically interpretable; it does not authorize post-hoc claim broadening.

## 9. Statistical unit and bootstrap

Frames are not independent samples.

### Primary cluster unit

Use primary-sequence clustered paired bootstrap over pair-level effects:

- resample unique frozen primary sequences with replacement;
- retain all discovery pairs belonging to a sampled primary sequence;
- at least 10,000 bootstrap resamples;
- two-sided 95% confidence intervals.

### Dependency sensitivity

Because a small number of control sequences are reused within discovery, additionally report a conservative connected-source-component bootstrap where pairs sharing any primary/control sequence belong to the same dependency component.

The primary locked decision uses the primary-sequence clustered result; the component result is a required sensitivity report.

## 10. Criterion A — locked decision

Define:

- `IoU weakness = mean(control IoU - distractor IoU)`;
- `failure weakness = failure_rate_distractor - failure_rate_control`.

Criterion A passes when at least one of the following holds on the complete 12-pair discovery package and its 95% clustered confidence interval excludes zero:

- `IoU weakness >= 0.05`; or
- `failure weakness >= 0.10`.

Do not declare Criterion A from a favorable sensitivity stratum alone.

Report sensitivity results for the frozen source-design strata, but they may only explain the complete-set result.

## 11. Criterion B — locked decision

For the nine predeclared whole/group controls:

- report mean interaction and clustered 95% CI;
- apply Holm correction at familywise alpha 0.05 across the nine primary tests;
- report adjusted and unadjusted values.

Criterion B passes when at least one predeclared MRM/group has:

- absolute mean interaction `>= 0.02 mean IoU`;
- clustered 95% CI excluding zero;
- Holm-adjusted significance at 0.05;
- a stable, scientifically interpretable direction.

No Retriever/MLP or T3 template-path refinement may rescue a failed nine-test primary family.

## 12. Frozen sensitivity analyses

Report, without changing the primary decision:

- ambiguity level 2 versus level 1;
- same-sequence control versus cross-sequence control;
- `STRONG_SAME_SEQUENCE` subset;
- cross-scene/activity flagged subset;
- color/appearance-difference flagged subset;
- low-light/multi-traffic flagged subset;
- FACE_HEAD, PERSON, VEHICLE and OBJECT_OTHER descriptive effects.

No sensitivity subgroup may be created after viewing outcome patterns.

## 13. Reproducibility and environment

Record:

- source SHA;
- patch SHA-256;
- config/checkpoint SHA-256;
- canonical frozen-slice SHA-256;
- OS, CPU, RAM, GPU and VRAM;
- Python, PyTorch, CUDA/cuDNN and dependency versions;
- deterministic settings and seeds;
- exact commands;
- initialization, prefix, snapshot, interval and timing boundaries.

Use the scoped local operational baseline accepted in Stage 4A. Do not claim parity with author-released OTB raw predictions.

## 14. Required machine-readable artifacts

Create under:

`screening/codex/artifacts/stage4B_discovery/`

At minimum:

- provenance/environment manifest;
- discovery execution manifest;
- hold-out seal manifest;
- state-snapshot parity results;
- baseline per-frame predictions/metrics for frozen discovery intervals;
- mode-level per-frame metrics;
- MRM/Retriever/MLP logs;
- pair-level Criterion A table;
- pair/mode-level Criterion B table;
- bootstrap results;
- multiplicity-adjusted test table;
- timing characterization;
- exact command log.

Do not commit datasets, checkpoints, full source video or large binary tensors.

## 15. Required reports

Create:

- `screening/codex/2026-08-26_stage4B_discovery_execution_report.md`
- `screening/codex/2026-08-26_stage4B_criterionA_results.csv`
- `screening/codex/2026-08-26_stage4B_criterionB_results.csv`
- `screening/codex/2026-08-26_stage4B_sensitivity_results.csv`
- `screening/codex/2026-08-26_stage4B_command_log.txt`
- exact reproducibility scripts;
- unified execution patch if additional diagnostic-only changes are required.

## 16. Allowed Stage 4B conclusions

- `STAGE4B_CRITERION_A_FAIL`
- `STAGE4B_CRITERION_B_FAIL`
- `STAGE4B_AB_PASS_READY_FOR_MANAGER_REVIEW`
- `STAGE4B_INCOMPLETE_ENVIRONMENT_OR_STATE_SNAPSHOT`
- `STAGE4B_INVALID_HOLDOUT_EXPOSURE`

Codex does not assign final `DIAG_PASS` or `DIAG_FAIL`.

## 17. Downstream gate

Only a Manager reconciliation accepting both Criteria A and B may unlock Stage 4C.

Stage 4C remains responsible for:

- actual physical non-execution;
- at least 5% median model-forward latency saving;
- pre-MRM low-cost predictor;
- sequence-disjoint held-out validation with AUROC at least 0.65 and calibration improvement.

## Locked state

- frozen discovery pairs: 12;
- frozen hold-out pairs: 8 and sealed;
- Stage 4B: READY;
- Stage 4C: LOCKED;
- diagnostic decision: NOT ASSIGNED;
- S1–S7: NOT STARTED;
- primary shortlist: NONE;
- main baseline: NONE;
- proposed architecture: NONE.
