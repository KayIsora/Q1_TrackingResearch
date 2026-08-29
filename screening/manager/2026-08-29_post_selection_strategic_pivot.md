# Post-selection strategic pivot — implementation first under limited research time

**Date:** 2026-08-29  
**Status:** `LOCKED_IMPLEMENTATION_PIVOT`  
**Prerequisite:** `screening/reconciliation/2026-08-29_F7_MCITrack_final_reconciliation.md`

## 1. Decision

The current baseline-selection cycle is closed. The project will not spend additional time on tracker search, dependency repair, reserve mini-probes or a new full diagnostic before implementation milestones are reached.

Two roles are separated explicitly.

### Publication-grade main baseline

```text
NONE
```

No candidate has completed the full evidence chain required for the intended algorithmic efficiency–robustness contribution.

### Project implementation / thesis engineering baseline

```text
SpikeTrack-S256-T1
```

This choice is operational, not a reversal of SpikeTrack `DIAG_FAIL`.

## 2. Why SpikeTrack is the implementation baseline

- official peer-reviewed 2026 method;
- official source, checkpoint and evaluator are available;
- exact source/checkpoint/config contracts have already been audited;
- approximately 11.2M parameters for the selected S256-T1 variant;
- generic RGB bounding-box SOT core;
- model behavior, MRM structure, timing and failure evidence are deeply understood;
- an auditable local operational baseline exists;
- Jetson/edge deployment is more credible than the remaining heavy or resource-blocked candidates;
- using the already understood tracker avoids another long startup cycle.

## 3. Locked non-claims

The project must not claim that:

- SpikeTrack passed the tested research hypothesis;
- conditional MRM1 skipping is a validated proposed contribution;
- the project reproduced every author-released OTB raw trajectory;
- TensorRT, FP16, INT8 or Jetson porting alone is a Q1-level algorithmic contribution;
- the current implementation baseline is the publication-grade main baseline.

SpikeTrack remains `DIAG_FAIL` under the tested ambiguity-conditioned MRM1-skip hypothesis.

## 4. Immediate implementation workstreams

### I0 — baseline freeze and reproducible runtime

- freeze source SHA, config, checkpoint and local environment;
- provide one-command evaluation and single-video execution;
- record parameters, model size, latency, peak RAM and end-to-end FPS;
- remove only non-scientific instrumentation overhead from the deployment build;
- preserve the research/audit branch separately.

### I1 — edge deployment characterization

- export or reconstruct an inference-compatible graph where technically feasible;
- test ONNX/TensorRT support and operator blockers;
- evaluate FP32 and FP16 first;
- use INT8 only as a later ablation;
- measure batch-size-1 latency, FPS, peak RAM, thermals and long-run stability;
- benchmark Jetson Nano B01 as the primary target and Orin Nano only as a secondary reference.

### I2 — minimal generic robustness characterization

- report official/checkpoint baseline on the mandatory generic benchmark plan as resources allow;
- prioritize LaSOT, GOT-10k and TrackingNet in that order of practical readiness;
- do not create a new adaptive-MRM research claim from the consumed SpikeTrack hold-out;
- retain OTB100 only for controlled debugging and previously frozen diagnostic reference.

### I3 — person-following extension

After the generic runtime is stable:

- detector only for initial person selection;
- lightweight person embedding / identity verification;
- target-presence estimation;
- conservative memory update;
- lost-state and same-person recovery;
- wrong-person relock prevention;
- robot safety gating and stop behavior.

This extension must be presented separately from the generic Core.

### I4 — thesis/report deliverables

- architecture and data-flow figures;
- baseline reproduction table;
- desktop/RTX and Jetson performance table;
- deployment optimization ablations;
- robot demonstration protocol;
- limitations and honest publication-status discussion.

## 5. Research-watch queue

No execution is authorized, but monitor:

- MaST training-source release;
- official resolution of MCITrack/UTPTrack resource contracts;
- new 2026 accepted generic RGB-SOT releases with complete trainable source.

A watch item may reopen research selection only after the implementation baseline reaches the first Jetson runtime milestone or after an explicit User strategic reset.

## 6. Time-allocation rule

Until the first Jetson milestone:

- at least 80% of project effort goes to implementation, deployment, measurement and robot integration;
- at most 20% goes to paper reading, novelty monitoring and documentation;
- no new candidate mini-probe is permitted;
- no new large search campaign is permitted.

## 7. Success criteria for the pivot

The pivot is successful when the project has:

1. a reproducible SpikeTrack-S256-T1 baseline runtime;
2. measured desktop and Jetson batch-size-1 performance;
3. a documented deployment optimization path;
4. a working generic tracker demonstration;
5. a person-following extension prototype with identity/presence safeguards;
6. a report that clearly separates algorithmic evidence, engineering contribution and future Q1 work.

## Locked state

- publication-grade main baseline: **NONE**;
- implementation baseline: **SpikeTrack-S256-T1**;
- new screening/model probes: **CLOSED**;
- next active stage: **I0 — baseline freeze and reproducible runtime**;
- proposed Q1 architecture: **NONE**;
- thesis/deployment implementation: **AUTHORIZED TO PLAN**.
