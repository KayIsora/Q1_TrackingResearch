# Tracker-selection boundary

## Current selection state

**PROJECT DECISION — 2026-08-24.** Baseline selection is **reopened**. FARTrack is no longer the assumed main development backbone.

The next main baseline must be selected through systematic screening rather than tracker-first commitment. The target is a recent, reproducible generic RGB SOT tracker with both:

1. **researchable computational redundancy** — identifiable computation that can plausibly be removed, routed, reduced, or made conditional through a scientific mechanism; and
2. **a meaningful robustness weakness** — a failure mode that remains relevant after recent prior-art auditing and can potentially be improved without sacrificing the tracker’s main strengths.

The preferred research opportunity is a mechanism that improves **efficiency and robustness together**, rather than an independent compression stage followed by an unrelated robustness module.

See the locked scope in [Research program scope and baseline-screening specification](10_research_program_scope_and_baseline_screening.md).

## Main baseline eligibility

A main baseline should normally satisfy all of the following:

- peer-reviewed / officially accepted or published in **2025 or 2026**;
- top conference or Q1 journal strongly preferred;
- online-first work is eligible when peer review and official publication/acceptance status are established;
- generic RGB SOT or directly extensible long-term SOT;
- official source code;
- official checkpoint(s);
- usable evaluation script/protocol;
- realistic training/fine-tuning workflow on a **single RTX 3060 12 GB**;
- plausible path to **Jetson Nano B01 4 GB** after the proposed method and reasonable deployment optimization.

ArXiv-only papers and 2023–2024 trackers remain mandatory novelty-audit/reference material but are not the preferred main baseline.

## What “heavy” means for this project

The project does not seek the largest model. A good baseline is “heavy enough to improve” because it contains **structured computational inefficiency**, not because it is simply too large for the hardware.

Examples:

- excessive template/search tokens;
- global attention applied to every frame;
- identical compute for easy and hard frames;
- redundant temporal/memory processing;
- expensive template–search fusion;
- fixed large search region/input resolution;
- over-provisioned backbone stages;
- repeated computation despite low temporal change;
- edge-unfriendly operators.

Strongly penalize a candidate if future INT8/pruning is the only reason it might become deployable.

## Allowed design freedom

Allowed scientific design space includes:

- backbone replacement/redesign;
- adaptive/dynamic computation;
- token pruning/routing/merging;
- memory/template reduction;
- knowledge distillation;
- low-rank approximation;
- pruning;
- quantization;
- adaptive search region/resolution;
- new lightweight or reliability-aware modules;
- substantial architecture redesign.

Fixed lower input resolution may be used as a baseline/ablation but is not sufficient primary novelty. Adaptive resolution or computation may be part of the primary contribution.

If the backbone or architecture changes so substantially that the result is effectively a new tracker, describe it as a **new tracker derived from / motivated by the baseline** and use stepwise ablation. Do not mislabel it as a minor improvement.

## RTX 3060 research-feasibility gate

- Official pretrained checkpoints may initialize training.
- Training from random initialization is not mandatory.
- Proposed modules must be genuinely trained.
- Joint fine-tuning of a meaningful part or all of the proposed model is preferred when feasible.
- Freezing/unfreezing must be treated as an experimental choice and ablated.
- Larger teacher models are allowed only during training/offline supervision if they disappear at inference and the workflow remains reproducible.

A candidate should not require inaccessible hardware merely to test the main hypothesis.

## Jetson Nano selection gate

Jetson Nano B01 4 GB is the mandatory primary embedded benchmark target.

Target end-to-end batch-size-1 performance:

- >=25 FPS desired;
- >=20 FPS acceptable near-real-time;
- <10 FPS fails the lightweight objective;
- >=30 FPS very strong but not required.

Candidate selection should consider **deployment headroom**, not only reported desktop FPS. The proposed contribution will normally add some cost before final optimization, so a baseline already at the edge of infeasibility is a poor choice.

Do not infer Nano runtime from desktop GPU, Orin, CPU/NPU, parameter count, or FLOPs.

## FARTrack status

FARTrack remains an important **reference/case study**, not a rejected or weak method.

Why it is no longer the default baseline:

- its efficiency side is already highly optimized through TSSD and IFAS;
- its Tiny/Nano/Pico design demonstrates an unusually mature lightweight path;
- its remaining disappearance/identity/recovery gaps are scientifically interesting but may push the project too quickly toward a person/long-term extension instead of the broader Core goal of finding researchable redundancy plus robustness weakness.

The existing [FARTrack deep audit](09_fartrack_deep_audit.md) remains useful for:

- efficient autoregressive design;
- distillation and sparsification reference;
- failure-audit methodology;
- later comparison;
- novelty collision checks.

Previously recorded FARTrack hypotheses remain hypotheses; reopening baseline selection does not prove or disprove them.

## Systematic screening stages

### Stage 1 — broad discovery

Collect peer-reviewed 2025–2026 RGB SOT/long-term-SOT candidates and relevant recent novelty adversaries.

### Stage 2 — eligibility filter

Filter by:

- publication status;
- modality;
- official code/checkpoint/evaluator;
- hardware/training feasibility;
- edge-deployment plausibility.

### Stage 3 — scientific audit

For each surviving tracker record:

- benchmark strength;
- architecture and compute distribution;
- parameters/MACs/FLOPs/runtime;
- training hardware/data recipe;
- author-reported limitations;
- code-visible bottlenecks;
- robustness weaknesses;
- researchable redundancy;
- possible shared efficiency+robustness mechanism;
- 2023–2026 novelty collisions;
- RTX 3060 feasibility;
- Jetson Nano headroom;
- research risk.

### Stage 4 — shortlist

Shortlist approximately 2–3 candidates with the best combined evidence.

### Stage 5 — reproduce before proposing

Reproduce the chosen candidate and empirically verify the hypothesized weakness/redundancy before committing to a final proposed architecture.

## Rejection rules

Strongly reject or penalize a candidate when:

- code/checkpoint/evaluator is incomplete;
- it needs inaccessible compute merely to conduct the research;
- the only apparent improvement is fixed resolution reduction or a standard backbone swap;
- recent work already substantially solves the intended weakness;
- no measurable computational redundancy can be identified;
- the final deployment depends entirely on post-hoc INT8/pruning;
- adding the proposed method leaves no plausible path to Jetson Nano;
- the Core novelty only appears after person-specific identity/ReID modules are attached.
