# Stage 2B — Targeted HG5 evidence / profiling resolution plan

**Date:** 2026-08-25  
**Status:** READY; Stage 2A is closed.  
**Purpose:** resolve only the six candidates that remain `HG4=PASS, HG5=PENDING` after systematic paper+code audit.

## Guardrail

This stage is **not** official reproduction, Jetson Nano benchmarking, HG6 novelty audit, S1–S7 scoring, shortlist selection, baseline selection, or proposed-method design.

Desktop/RTX measurements may be used only to understand execution boundaries, operator behavior, relative mode cost, peak VRAM and exportability. They must **not** be converted into Jetson Nano FPS claims.

## Target set

1. CX007 — SpikeTrack
2. CX010 — UTPTrack
3. CX020 — SAMURAI
4. CX037 — SSTrack-AAAI
5. CX038 — MCITrack
6. CX053 — UncTrack

Candidates already HG5 PASS are held unchanged for later HG6. HG5 FAIL candidates are reference-only. HG3 FAIL/PENDING candidates are not reopened here.

## Decision standard

### Promote HG5 to PASS only if

The candidate has a credible bounded path to Nano-class deployment without replacing the core scientific method. Evidence should establish enough of the following to remove the specific PENDING blocker:

- reproducible lightweight/selected variant;
- bounded runtime state;
- operator graph that can plausibly be exported or implemented efficiently;
- no mandatory foundation-scale always-on path incompatible with the project boundary;
- targeted profiling shows the suspected dynamic/operator path is not a structural blocker;
- required changes are engineering-level export/runtime adaptation rather than a new tracker rewrite.

### Set HG5 to FAIL if

Targeted evidence shows that the released candidate would require major core replacement, life-support compression, or removal of a defining mechanism merely to have a credible Nano path.

### Retain PENDING if

The required evidence cannot be obtained without hardware/runtime work not available in the present environment. `PENDING` is not a soft PASS.

## Common measurement protocol

Where execution is possible:

- official pinned commit;
- official released checkpoint and selected config;
- batch size 1;
- no accuracy benchmark required;
- use a short synthetic or official-format sample only to exercise the graph;
- report initialization separately from steady-state inference;
- synchronize CUDA around latency measurements when CUDA is used;
- report median and a small distribution rather than one unsynchronized timer;
- report peak allocated/reserved GPU memory where available;
- note CPU↔GPU synchronizations and Python-controlled branches;
- do not infer Nano speed from the result.

Where export is attempted:

- first establish exact PyTorch input/output/state contract;
- attempt ONNX only when the official graph can be instantiated reliably;
- report export failure as evidence with the exact unsupported/dynamic site;
- do not rewrite the architecture merely to make export succeed during this gate;
- an engineering wrapper/shape fix is allowed to characterize the blocker but must be documented separately from the official path.

## Candidate-specific minimum evidence

### CX007 — SpikeTrack

Resolve:

- T=1 and selected deployable family variant first;
- whether dense spike/quantization operators execute through ordinary supported PyTorch ops;
- cost of Memory Retrieval Modules and template/time dimension;
- whether Python timestep/state behavior blocks static export;
- one-forward and short-sequence peak memory/latency if checkpoint can run;
- ONNX/export dry-run or exact blocker.

HG5 must remain PENDING until the dense-SNN/runtime/export concern is resolved.

### CX010 — UTPTrack

Use generic RGB `UTPTrack-O` selected released checkpoint.

Resolve:

- dynamic candidate/token elimination behavior under actual inference;
- token-length trace at pruning layers;
- export behavior of sort/top-k/gather/scatter/boolean restoration;
- peak memory and model-only latency for one short run if possible;
- whether a fixed-shape engine path is plausible without deleting the pruning mechanism.

### CX020 — SAMURAI

Do not use Base+/Large by default as the only deployment test. Characterize the smallest officially supported SAM2.1 Hiera variant available to the family.

Resolve:

- live/streaming wrapper feasibility versus offline indexed-video API;
- per-frame image-encoder/memory-attention/mask-decoder boundary;
- retained history growth and CPU-offload behavior;
- Python/NumPy Kalman overhead boundary;
- smallest host model memory/runtime on available development GPU if practical;
- export/operator blockers in SAM2.1 path.

A PASS requires a credible Nano-class host route within the released family, not merely the claim that SAMURAI additions are small.

### CX037 — SSTrack-AAAI

Resolve:

- current B256 checkpoint instantiation despite stale profiler;
- actual search-token lengths through the three CE stages;
- cost/behavior of repeated selected-template patch embedding;
- growth and selection of raw template history;
- ONNX/export behavior of sort/gather/scatter/restoration;
- corrected model-only profiling boundary if safely possible without changing the method.

### CX038 — MCITrack

Use B224, not L384, as the first deployment-plausibility probe.

Resolve:

- four hidden-state tensor inputs/outputs and their actual dtype at inference;
- effect of configured gradient-checkpoint wrappers under `no_grad`;
- per-frame cost of four Mamba blocks + Injectors + Extractors;
- repeated five-template encoding and raw template-bank memory;
- ability to express fixed-size hidden state in an export contract;
- ONNX/export dry-run or exact blocker.

### CX053 — UncTrack

Before runtime characterization, document the minimal source/resource reconciliation required to instantiate the official online tracker (full-width-parenthesis typo and checkpoint filename ordering). Do not silently patch and call the result official.

Resolve:

- Base online model first;
- ordinary reliable-frame latency/memory;
- unreliable-frame second-attempt latency/memory;
- ULD+PMN cost boundary;
- actual template-cache mode used for selected benchmark config;
- export behavior of mutable K/V, top-k, Python confidence branch and Kalman boundary;
- actual second-attempt rate is not required for HG5, but mode-specific cost must be separated.

## Required artifacts

Manager and Codex must remain separate until reconciliation.

Codex artifact:

`screening/codex/2026-08-25_stage2B_targeted_hg5_evidence.md`

Manager reconciliation artifact after Codex completes:

`screening/reconciliation/2026-08-25_stage2B_targeted_hg5_reconciliation.md`

## Stage exit

Stage 2B closes only when all six candidates are assigned one of:

- HG5 PASS;
- HG5 FAIL;
- HG5 PENDING with an explicit external/hardware blocker that cannot presently be resolved.

If any remains PENDING for lack of unavailable target hardware, it does not proceed to soft scoring as if it passed. Manager may decide whether to acquire the missing evidence or hold it outside the candidate pool.

Only after this stage is reconciled may the project start candidate-specific research-gap formulation and mechanism-level HG6 novelty audit.

## Locked non-claims

- HG6: NOT STARTED
- S1–S7: NOT STARTED
- shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
