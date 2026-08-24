# Stage-2 deep-audit framework — Manager preparation

**Date:** 2026-08-24  
**Status:** PREPARED ONLY — NOT YET ACTIVATED  
**Governing protocol:** `docs/11_systematic_screening_protocol.md`  
**Coordination:** `screening/00_parallel_screening_coordination.md`

## Activation gate

This Stage-2 framework MUST NOT be activated until the external Codex worker completes a true independent recheck of the six HG3 flags and Manager↔Codex reconciliation is closed with no unresolved HG3 disagreement.

Until that activation gate is closed:

- HG4/HG5/HG6 remain `PENDING`;
- S1–S7 remain blank;
- no candidate is shortlisted;
- no main baseline is selected;
- no proposed architecture is designed.

This file defines execution structure only. It contains no Stage-2 candidate conclusions.

## Stage-2 objective

For every candidate that survives the frozen HG1/HG2/HG3 queue, extract enough primary-paper and pinned-code evidence to support later decisions on:

1. **HG4 — RTX 3060 12 GB research feasibility**;
2. **HG5 — Jetson Nano B01 deployment plausibility**;
3. a candidate-specific, evidence-grounded computational-redundancy hypothesis;
4. a candidate-specific, evidence-grounded robustness-weakness hypothesis;
5. whether there is a plausible structural coupling between efficiency and robustness worth taking into HG6 novelty audit.

Stage 2A is an evidence-extraction stage. A visible expensive module is not automatically `redundancy`; a paper weakness is not automatically a causal failure mechanism.

## Parallel lane responsibilities

### Manager lane — paper/scientific audit

For each candidate, extract and label:

- exact architecture and design rationale from the paper;
- backbone and template/search structure;
- temporal/memory mechanism;
- prediction head/decoder;
- input resolution(s);
- parameters and MACs/FLOPs when directly reported or reproducibly measurable;
- reported FPS/latency **with exact hardware and runtime boundary**;
- LaSOT / GOT-10k / TrackingNet results under compatible protocols;
- training datasets, stages, original hardware and initialization;
- author-reported limitations;
- robustness observations explicitly supported by paper/benchmark evidence;
- plausible computational-redundancy hypotheses, clearly labeled `HYPOTHESIS — untested`;
- plausible robustness-weakness hypotheses, clearly labeled `HYPOTHESIS — untested`;
- possible efficiency–robustness coupling, also only as a hypothesis.

The Manager lane must not use desktop FPS to infer Jetson Nano FPS and must not treat paper claims as code facts.

### Codex lane — code/engineering audit

For each candidate, independently inspect pinned official code/config/checkpoint paths and extract:

- exact released variant/config corresponding to paper results;
- model construction path;
- backbone depth/width/stages;
- template/search sizes and token/tensor dimensions when code-visible;
- module execution frequency: initialization-only, every frame, periodic, conditional;
- memory/template update rules;
- static/dynamic branches;
- code-visible pruning/routing/merging/bypass behavior;
- prediction-head path;
- profiler/export utilities already present;
- training config: batch size, epochs, optimizer, learning rates, freeze/unfreeze settings when explicit;
- code-visible checkpoint and backbone-pretrain separation;
- dependency/build risks;
- operator/dynamic-shape/export risks relevant to TensorRT/Nano;
- code-visible likely high-cost modules, recorded only as `CODE FACT — inspected`, not as scientific redundancy conclusions.

Codex must not soft-score or decide HG4/HG5 independently unless a later Manager instruction explicitly asks for a gate recommendation after evidence extraction.

## Fixed candidate processing order

To reduce cherry-picking, Stage 2 will process the active queue by canonical candidate ID rather than by perceived promise.

The current provisional order, subject only to the final HG3 freeze, is:

1. CX007 — SpikeTrack
2. CX009 — UETrack
3. CX010 — UTPTrack
4. CX013 — FARTrack
5. CX014 — GOT-Edit
6. CX017 — GOT-JEPA
7. CX020 — SAMURAI
8. CX024 — DAM4SAM
9. CX037 — SSTrack-AAAI
10. CX038 — MCITrack
11. CX040 — MambaLCT
12. CX043 — SUTrack
13. CX044 — AsymTrack
14. CX046 — JDTrack
15. CX049 — SPMTrack
16. CX051 — UMDATrack
17. CX053 — UncTrack
18. CX058 — HiT-DyHiT
19. CX125 — MPT

SiamABC remains outside the provisional active queue under the current Manager HG3 result; the external Codex recheck can still trigger reconciliation before Stage 2 activation.

## Fixed batches

Stage 2 will run in four evidence batches to limit cross-candidate anchoring and keep reconciliation tractable.

### Batch A
- CX007 SpikeTrack
- CX009 UETrack
- CX010 UTPTrack
- CX013 FARTrack
- CX014 GOT-Edit

### Batch B
- CX017 GOT-JEPA
- CX020 SAMURAI
- CX024 DAM4SAM
- CX037 SSTrack-AAAI
- CX038 MCITrack

### Batch C
- CX040 MambaLCT
- CX043 SUTrack
- CX044 AsymTrack
- CX046 JDTrack
- CX049 SPMTrack

### Batch D
- CX051 UMDATrack
- CX053 UncTrack
- CX058 HiT-DyHiT
- CX125 MPT

Batch membership is based on canonical ID order only; it is not a scientific ranking.

## Required evidence record per candidate

Every Stage-2 candidate record must contain the following sections.

### A. Identity and provenance
- candidate ID;
- exact paper title;
- publication reference IDs;
- official repository reference ID and pinned commit/ref;
- exact released variant/config being audited.

### B. Architecture facts
- backbone;
- template/search representation;
- temporal/memory path;
- prediction head;
- input resolution;
- key code modules and paths.

### C. Efficiency facts
- parameters;
- MACs/FLOPs;
- reported speed/latency;
- reported speed hardware;
- memory evidence if available;
- per-frame vs periodic/conditional execution;
- operator/export observations.

Unknown quantities remain `PENDING`; do not estimate them from unrelated variants.

### D. Training facts
- datasets;
- training stages;
- author hardware;
- official checkpoint initialization;
- batch size/epochs/optimizer when available;
- freeze/unfreeze behavior if explicit;
- code-visible VRAM-relevant choices.

### E. Robustness evidence
Separate:

- `AUTHOR-REPORTED LIMITATION — cited`;
- benchmark/attribute evidence;
- `CODE FACT — inspected`;
- `HYPOTHESIS — untested`.

Do not convert a generic field problem such as occlusion into a candidate-specific weakness without evidence.

### F. HG4 evidence package
Record evidence relevant to single-RTX3060 research feasibility:

- checkpoint-based starting point;
- whether proposed modules could be trained without full from-scratch reproduction;
- meaningful partial/full joint fine-tuning options;
- estimated VRAM risk only when supported by configuration/profile evidence;
- AMP / gradient accumulation / checkpointing compatibility when code-supported;
- any structural blocker requiring inaccessible multi-GPU resources.

Final HG4 remains `PENDING` during extraction and is decided only after Manager↔Codex evidence reconciliation.

### G. HG5 evidence package
Record only structural deployment plausibility:

- model/operator family;
- likely TensorRT compatibility risks;
- dynamic-shape/dynamic-control-flow risks;
- memory/state growth behavior;
- token/attention/memory structure;
- whether normal FP16/TensorRT deployment is conceptually plausible;
- whether the architecture appears to require INT8 or extreme post-hoc compression merely to become viable.

Do **not** infer Nano FPS from desktop/AGX/NX/Orin/CPU/NPU measurements.

Final HG5 remains `PENDING` until evidence reconciliation.

### H. Hypotheses for later scientific judgment
Keep three separate fields:

1. `redundancy_hypothesis`;
2. `robustness_weakness`;
3. `coupled_mechanism_hypothesis`.

All three are `HYPOTHESIS — untested` until reproduction/profiling or stronger evidence supports them.

No candidate may enter HG6 mechanism-level novelty audit without at least one explicit, testable candidate-specific research-gap statement.

### I. Unresolved items
List every missing item capable of changing HG4/HG5 or the later S1/S2/S3 judgment.

## Evidence reconciliation procedure

For each batch:

1. Manager completes paper/scientific evidence in `screening/manager/`.
2. Codex independently completes code/engineering evidence in `screening/codex/`.
3. Neither lane edits the canonical matrix during independent extraction.
4. Manager compares the two records field by field.
5. Factual disagreements are resolved against primary paper/pinned official code.
6. Only after reconciliation may canonical matrix architecture/training/efficiency fields be updated.
7. HG4 and HG5 are then decided using only reconciled evidence.
8. No S1–S7 score is assigned yet unless the locked workflow explicitly reaches the soft-score stage.

## Stage-2 stopping rules

A candidate can leave active deep audit before HG6 if:

- HG4 becomes `FAIL`; or
- HG5 becomes `FAIL`.

A candidate with `PENDING` HG4 or HG5 remains unresolved and cannot move to final shortlist.

A candidate surviving HG4/HG5 is not automatically promising. It proceeds only to candidate-specific research-gap formulation and then HG6 novelty audit.

## Stage-2 non-claims

This preparation does not establish that any candidate:

- is heavy or lightweight on Jetson Nano;
- contains confirmed computational redundancy;
- has a confirmed robustness failure mechanism;
- has novelty headroom;
- is superior to another candidate;
- should be shortlisted;
- should become the main baseline.

## Prepared next action after HG3 freeze

When external Codex HG3 reconciliation is complete, activate **Batch A only** first. Manager and Codex run independent Stage-2A evidence extraction on CX007/CX009/CX010/CX013/CX014, reconcile the batch, then continue to Batch B. This provides an early process-quality check before all 19 candidates are audited.
