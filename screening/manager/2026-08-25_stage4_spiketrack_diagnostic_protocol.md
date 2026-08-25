# Stage 4 — SpikeTrack diagnostic falsification protocol

**Date:** 2026-08-25  
**Status:** LOCKED BEFORE DIAGNOSTIC EXECUTION  
**Entry candidate:** CX007 — SpikeTrack only  
**Prerequisite:** Stage 3B HG6 novelty audit is complete.

## 1. Purpose

SpikeTrack is the sole candidate that passed HG1–HG6, but it is **not** the selected baseline and is not yet eligible for soft scoring.

Stage 4 tests the falsifiable gap that survived HG6:

> Does target–distractor ambiguity predict the marginal utility of identifiable SpikeTrack Memory Retrieval Module (MRM) scale and template/time paths, such that real retrieval execution can be reduced on unambiguous frames while preserving or strengthening target–distractor discrimination on ambiguous frames?

This stage must be capable of rejecting the candidate. It does not begin proposed-architecture design.

## 2. Candidate boundary

### Primary anchor

- official SpikeTrack-S256-T1 configuration;
- exact official checkpoint corresponding to that configuration;
- pinned official repository commit `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`.

### Controlled comparison

- SpikeTrack-S256-T3 is used only as a temporal/template comparison.

### Scientific core that must remain

- SDTV3 spike-driven backbone family;
- asymmetric cached template/search execution;
- six template-to-search MRMs;
- template-conditioned retrieval;
- center prediction head.

Replacing the backbone, head or MRM retrieval family is outside Stage 4.

## 3. Locked non-claims

Stage 4 does not claim:

- any MRM is redundant;
- dynamic routing is beneficial;
- a specific ambiguity signal is deployable;
- Nano FPS or energy benefit;
- first adaptive SNN inference;
- first distractor-aware tracker;
- a proposed architecture;
- soft-score eligibility before the diagnostic gate passes.

## 4. Decision states

Allowed states:

- `DIAG_PASS` — the complete evidence chain in Section 12 is satisfied;
- `DIAG_FAIL` — the residual weakness, MRM interaction, physical saving or held-out predictability requirement is falsified;
- `DIAG_PENDING` — execution/data/environment evidence is insufficient.

`DIAG_PENDING` is not a soft pass.

## 5. Stage structure

### Stage 4A — preflight and instrumentation

- synchronize the exact pinned repository/checkpoint;
- verify environment and official configuration;
- inventory available official benchmark data and raw-result assets;
- establish a bounded baseline reproduction check;
- implement read-only hooks and deterministic inference-only ablations;
- create a proposed diagnostic-slice manifest schema;
- do not run the full diagnostic study.

### Stage 4B — discovery diagnostic

- freeze the annotated discovery slice before examining ablation results;
- reproduce the similar-object/distractor weakness;
- run per-MRM and T1/T3 paired contribution tests;
- determine whether a condition-by-retrieval interaction exists.

### Stage 4C — physical-skip and held-out validation

Only if Stage 4B supports the interaction:

- implement actual path non-execution for a predeclared MRM or MRM group;
- measure real latency/operation reduction;
- derive a low-cost offline predictor from pre-MRM information;
- evaluate on held-out sequences that were not used to select the path or signal.

### Stage 4D — reconciliation and decision

- Manager and Codex evidence are reconciled;
- assign `DIAG_PASS`, `DIAG_FAIL`, or `DIAG_PENDING`;
- only `DIAG_PASS` permits S1–S7 scoring.

## 6. Baseline-reproduction preflight

Stage 4A must record:

- exact repository SHA;
- exact config and checkpoint hash;
- Python/PyTorch/CUDA/device environment;
- deterministic settings;
- official dataset and evaluator path;
- initialization versus steady-state timing boundary.

Where official raw predictions are available, compare at least three predeclared sequences using the exact T1 configuration. A reproduction check passes when the same protocol is used and either:

1. per-sequence Success AUC differs from the released result by no more than **0.5 percentage points**, or
2. the mismatch is traced to a documented environment/evaluator difference and the Manager explicitly accepts the reproduction boundary before Stage 4B.

Failure to establish a credible baseline produces `DIAG_PENDING`, not an inferred scientific result.

## 7. Diagnostic-slice construction

### 7.1 Source universe

Use only publicly accessible generic RGB-SOT benchmark sequences supported by the official SpikeTrack evaluator and available in the project environment.

The final dataset names and sequence IDs remain `PENDING` until Stage 4A inventories local availability. They must be frozen before Stage 4B.

### 7.2 Selection rule

Frames/intervals must be selected **without viewing SpikeTrack predictions, scores or failures**.

A `similar-distractor interval` requires:

- the annotated target is visible enough for evaluation;
- at least one non-target object appears inside the tracker search context;
- the non-target has meaningful visual/category/shape similarity to the target;
- the interval includes at least five consecutive evaluable frames unless the event is shorter by dataset construction.

A matched `control interval` must have no similar distractor and should be matched as closely as practical on:

- target scale;
- motion magnitude;
- occlusion state;
- sequence source;
- interval length.

### 7.3 Annotation fields

The frozen manifest must include:

- dataset;
- sequence;
- start/end frame;
- `distractor_present`;
- `ambiguity_level` in `{0,1,2}`;
- distractor bounding box when feasible;
- target visibility/occlusion state;
- fast-motion indicator;
- low-resolution indicator;
- annotator note;
- discovery or hold-out split.

`ambiguity_level` is a human/source annotation and must not be derived from final tracker failure.

### 7.4 Split

Use sequence-disjoint discovery and hold-out sets.

Minimum target, subject to available data:

- discovery: at least 12 distractor intervals and 12 matched controls from at least 6 sequences;
- hold-out: at least 8 distractor intervals and 8 matched controls from at least 4 additional sequences.

If this minimum cannot be met, the state is `DIAG_PENDING` unless the Manager approves a revised power/coverage plan before results are inspected.

## 8. Required instrumentation

For each of the six MRMs, record per frame:

- MRM ID and stage;
- input/output tensor shape;
- residual/output norm;
- template/time dimension;
- synchronized module latency;
- total model-forward latency;
- target center-score peak;
- strongest non-target/distractor score peak when measurable;
- predicted box;
- ground-truth IoU and center error;
- T1/T3 mode;
- template-refresh event and template age for T3.

Instrumentation must not change the baseline output beyond floating-point tolerance.

## 9. Diagnostic ablations

### 9.1 Contribution ablation

Implement deterministic inference-only controls:

- baseline T1;
- baseline T3;
- one-MRM-at-a-time zero-residual/bypass-output control for MRM1–MRM6;
- predeclared grouped controls: early `{1,2}`, middle `{3,4}`, late `{5,6}` if single-MRM effects are too small/noisy.

Zero-residual controls test contribution but do **not** count as physical compute savings.

### 9.2 Paired evaluation

All modes must run on the identical frozen frames with identical checkpoint, crop, state reset and evaluator settings.

Primary outcome:

- frame IoU.

Secondary outcomes:

- center error;
- success at IoU 0.5;
- target–distractor peak margin when a distractor box/peak is available;
- recovery duration after the distractor event;
- synchronized latency.

## 10. Statistical analysis

Frames are not treated as independent samples.

Use sequence-clustered paired bootstrap with at least **2,000 resamples** and report 95% confidence intervals.

For each MRM/path, compute:

- marginal contribution on distractor intervals;
- marginal contribution on matched controls;
- difference-in-differences:

`interaction = contribution_distractor - contribution_control`.

The analysis must report effect magnitude, not only a p-value or confidence interval.

## 11. Physical-skip and predictor phase

Only paths/groups supported by Stage 4B may enter Stage 4C.

### 11.1 Physical path requirement

The implementation must actually avoid the selected MRM computation. Masking or zeroing after the computation has already executed does not satisfy this requirement.

Measure:

- median and p95 steady-state model-forward latency;
- module-level latency;
- peak memory where available;
- actual operator/path execution trace.

Desktop measurements remain development evidence, not Nano results.

### 11.2 Low-cost offline predictor

Before architecture design, an offline diagnostic predictor may use only information available before the candidate MRM path executes, for example:

- early template/search similarity statistics;
- early feature disagreement;
- previous-frame motion/state;
- pre-MRM score or feature margin if available before the skipped path.

The predictor is a diagnostic probe, not the final proposed module.

It must be trained/tuned only on discovery sequences and evaluated on held-out sequences.

## 12. Locked diagnostic decision criteria

### Criterion A — residual weakness reproduced

At least one of the following must hold on the frozen distractor versus matched-control intervals, with a sequence-clustered 95% confidence interval excluding zero:

- mean IoU is at least **0.05 lower** on distractor intervals; or
- failure rate at IoU `<0.5` is at least **10 percentage points higher** on distractor intervals.

Otherwise: `DIAG_FAIL` for the current similar-distractor premise.

### Criterion B — condition-by-retrieval interaction

At least one predeclared MRM or MRM group must show:

- an absolute difference-in-differences of at least **0.02 mean IoU**, and
- a sequence-clustered 95% confidence interval excluding zero.

The direction must be scientifically interpretable: the path is materially more useful under distractor ambiguity or materially unnecessary/harmful on controls.

Otherwise: `DIAG_FAIL`.

### Criterion C — real saving potential

A physically skipped supported path/group must reduce median steady-state model-forward latency by at least **5%** on the development GPU, with output/state handling kept otherwise equivalent.

Otherwise: `DIAG_FAIL` for the efficiency–robustness coupling, even if an accuracy interaction exists.

### Criterion D — held-out predictability

A low-cost pre-MRM diagnostic signal must predict whether the stronger retrieval path is useful on sequence-disjoint hold-out data with:

- AUROC at least **0.65**, and
- positive improvement over a constant/base-rate predictor in Brier score or another predeclared calibration metric.

The label must be derived from oracle marginal path benefit, not final failure alone.

Otherwise: `DIAG_FAIL` for actionable conditional computation.

### Final state

- `DIAG_PASS` only when A, B, C and D all pass.
- `DIAG_FAIL` when any criterion is scientifically falsified.
- `DIAG_PENDING` only for unresolved environment/data/execution blockers, not weak results.

## 13. Independent lanes

### Manager lane

- freeze slice and annotation protocol;
- ensure selection is outcome-independent;
- verify scientific metrics and statistical analysis;
- interpret whether results satisfy A–D;
- prevent post-hoc subgroup creation.

### Codex lane

- synchronize the exact code/checkpoint;
- implement hooks and deterministic controls;
- produce environment and reproduction evidence;
- run bounded diagnostics only after the manifest is frozen;
- preserve raw logs and machine-readable outputs;
- report code facts without promoting them to conclusions.

## 14. Required artifacts

### Stage 4A

- `screening/codex/2026-08-25_stage4A_spiketrack_preflight.md`
- `screening/codex/2026-08-25_stage4A_spiketrack_instrumentation_manifest.csv`
- `screening/codex/2026-08-25_stage4A_spiketrack_slice_inventory.csv`

### Frozen slice

- `screening/manager/2026-08-25_stage4_spiketrack_diagnostic_slice.csv`

### Stage 4B/C results

- raw machine-readable logs under a declared experiment-artifact path;
- Codex execution report;
- Manager analysis report;
- final reconciliation file.

Large checkpoints, datasets and raw video are not committed to this research repository.

## 15. Stopping rule

Stage 4A stops after preflight, instrumentation verification and dataset/slice inventory. It must not silently proceed to full Stage 4B ablations.

Stage 4B starts only after the Manager commits the frozen diagnostic slice.

## 16. Locked state

- Stage 3B HG6: COMPLETE
- SpikeTrack diagnostic status: READY
- Stage 4A: READY
- Stage 4B/C: LOCKED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
