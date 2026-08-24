# Embodied Tracking Problem Research

> Evidence-first research program for improving recent generic SOT trackers under edge-compute constraints, then extending the strongest Core toward long-term identity-sensitive target-person tracking.

**Language:** Vietnamese with English technical terms.  
**Status:** research scope is locked; **baseline selection is reopened**. FARTrack is retained as a reference/case study, not the assumed main development backbone.

## What this repository is for

This repository records the scientific reasoning, source evidence, baseline-selection rules, experiment gates, implementation notes, and deployment boundaries for a two-layer tracking research program.

The repository is deliberately **problem-first and evidence-first**. A tracker is not selected first and justified later. The main baseline must survive systematic screening for:

- recent peer-reviewed publication;
- reproducibility;
- benchmark strength;
- researchable computational redundancy;
- meaningful robustness weakness;
- RTX 3060 12 GB research feasibility;
- credible path to Jetson Nano B01 4 GB;
- novelty space after recent prior-art auditing.

## Current research program — PROJECT DECISION

### Layer A — Core generic RGB SOT

The Core must be a class-agnostic RGB single-object tracker initialized from a bounding box. The desired contribution is **not merely compression**. The target pattern is:

> identify a strong 2025–2026 tracker with a real computational inefficiency and a real robustness weakness, then design a new algorithmic mechanism that reduces unnecessary computation while preserving or improving tracking quality.

Occlusion, distractors, reliability, generic recovery, temporal/memory inefficiency, token redundancy, adaptive computation, and search/fusion inefficiency are valid Core topics.

The Core contribution must remain scientifically meaningful even if all person-specific modules are removed.

### Layer B — Long-term target-person extension

After the generic Core is established, `target_type = person` may activate:

- identity verification;
- person memory;
- lightweight person ReID;
- presence/recovery logic;
- optional lightweight person detector assistance only in LOST/recovery mode for the person/robot extension.

This layer targets long-term identity-sensitive target-person tracking and later robot demonstration.

See the full locked scope: [Research program scope and baseline-screening specification](docs/10_research_program_scope_and_baseline_screening.md).

## Baseline status reset

**PROJECT DECISION — 2026-08-24:** FARTrack is **no longer the assumed main baseline**.

FARTrack remains scientifically useful because it is a strong reference for efficient autoregressive tracking, self-distillation, token sparsification, and failure-audit design. However, its lightweight side is already unusually well optimized, and the remaining disappearance/identity/recovery gaps risk narrowing the Core contribution too early.

Therefore the project has reopened baseline selection and will systematically screen recent trackers for the stronger combination:

> **researchable redundancy + robustness weakness + reproducibility + edge headroom.**

See [Tracker-selection boundary](docs/07_tracker_selection_boundary.md) and [FARTrack deep audit](docs/09_fartrack_deep_audit.md).

## Mandatory baseline eligibility

The main scientific baseline should normally satisfy:

- peer-reviewed / officially accepted or published in **2025 or 2026**;
- top conference or Q1 journal strongly preferred;
- online-first accepted/published journal work allowed;
- RGB generic SOT or directly extensible long-term SOT;
- **official code + checkpoint + evaluation script/protocol**;
- realistic research workflow on a **single RTX 3060 12 GB**;
- credible path to **Jetson Nano B01 4 GB** after the proposed contribution and reasonable deployment optimization.

ArXiv-only work and 2023–2024 papers remain mandatory novelty-audit/reference material but are not the preferred main baseline.

## Evaluation stack

### Mandatory generic benchmarks

- **LaSOT** — long-sequence robustness;
- **GOT-10k** — generalization;
- **TrackingNet** — large-scale/diverse tracking performance.

TNL2K and LaSOT-ext may be added when relevant. **TPT-Bench** is added for the later target-person extension.

Keep two result layers separate:

1. official-checkpoint baseline reproduction;
2. controlled baseline-versus-proposed comparison under matched training data/protocol/budget where scientifically appropriate.

A generic accuracy decrease of roughly **0.3–0.5 points maximum** may be acceptable only when accompanied by a substantial efficiency/deployment gain and fully reported trade-off.

See [Dataset and evaluation roles](docs/04_evaluation_stack.md).

## Training boundary

- Development hardware: **RTX 3060 12 GB**.
- Official pretrained checkpoints may initialize training.
- Random-from-scratch baseline training is not mandatory.
- Proposed modules must be genuinely trained.
- Joint fine-tuning of a meaningful part or all of the proposed network is preferred when feasible.
- Freezing/unfreezing is an ablation decision, not a default assumption.
- Larger teacher models may be used only during training/offline supervision if they disappear at inference and the workflow remains reproducible.
- Development may use reduced sampling; final controlled training should scale toward the declared baseline recipe within resource limits.

## Lightweight and edge boundary

“Lightweight” is multi-dimensional. Final claims must report at least:

- parameters;
- MACs/FLOPs;
- FPS;
- per-frame latency;
- runtime RAM/memory;
- input resolution;
- precision/runtime backend.

**Primary embedded target:** Jetson Nano B01 4 GB.

End-to-end batch-size-1 runtime targets:

- **>= 25 FPS:** desired;
- **>= 20 FPS:** acceptable near-real-time;
- **< 10 FPS:** does not meet the lightweight objective;
- **>= 30 FPS:** very strong but not mandatory.

TensorRT FP16 is the preferred deployment path. INT8 may be an additional optimization/ablation but must not be the sole reason an otherwise over-heavy baseline becomes deployable.

No Jetson FPS may be inferred from desktop GPU, Orin, CPU/NPU, parameter count, or FLOPs.

See [Edge-deployment claim boundary](docs/05_edge_boundary.md).

## RGB and detector boundaries

Core generic SOT input:

- RGB image/video;
- initial bounding box only.

No language, depth, thermal, or event-camera input is used in the main Core comparison.

Generic SOT benchmark uses no external detector after initialization.

For the later person/robot extension, a person detector may initialize/select the target and may optionally be evaluated as a separate LOST/recovery aid. Detector-assisted results must remain separate from pure tracker results.

## Next stage — systematic screening

The next research stage is **not architecture design**. It is systematic screening of 2025–2026 trackers.

For every surviving candidate, record:

- publication/venue/status;
- official code/checkpoint/evaluator availability;
- benchmark competitiveness;
- parameters/MACs/FLOPs/runtime evidence;
- training hardware and data recipe;
- architecture compute distribution;
- author-reported limitations;
- code-visible bottlenecks;
- robustness weaknesses;
- computational redundancy;
- whether one mechanism could improve both efficiency and robustness;
- recent novelty collisions;
- RTX 3060 feasibility;
- Jetson Nano deployment headroom;
- research risk.

Only after this audit should approximately 2–3 candidates be shortlisted and reproduced before a proposed architecture is committed.

## Start here (mandatory reading order)

1. [RULE/01_EVIDENCE_AND_CITATION_POLICY.md](RULE/01_EVIDENCE_AND_CITATION_POLICY.md)
2. [Claim taxonomy](docs/00_claim_taxonomy.md)
3. [Scope and terminology](docs/01_scope_and_terminology.md)
4. [Problem-selection evidence](docs/02_problem_selection.md)
5. [Application candidates and decision](docs/03_application_candidates.md)
6. [Dataset and evaluation roles](docs/04_evaluation_stack.md)
7. [Edge-deployment claim boundary](docs/05_edge_boundary.md)
8. [Open research questions and gates](docs/06_research_questions.md)
9. [Tracker-selection boundary](docs/07_tracker_selection_boundary.md)
10. [Consensus input boundary](docs/08_consensus_input.md)
11. [FARTrack deep audit](docs/09_fartrack_deep_audit.md)
12. [Research program scope and baseline screening](docs/10_research_program_scope_and_baseline_screening.md)
13. [References](references/references.md), [evidence ledger](references/evidence_ledger.md), and [source manifest](references/source_manifest.csv)

## What is intentionally absent

- No claim that a final baseline has been selected.
- No claim of SOTA, novelty, Jetson Nano FPS, accuracy gain, power efficiency, or Q1 acceptance.
- No assumption that standard pruning/quantization or fixed resolution reduction is sufficient novelty.
- No claim that FARTrack’s earlier hypotheses are disproved; they are retained as reference hypotheses outside the newly reopened Core baseline decision.

## Working division of labor

- **ChatGPT:** research manager / evidence controller — maintain framing, source verification, novelty boundaries, experiment gates, and repository state.
- **Codex:** implementation executor — clone/build/instrument/train/evaluate/profile under explicit instructions.
- **GitHub:** shared source of truth for decisions, evidence, experiment plans, implementation notes, and validated results.

Implementation output must not be promoted to a scientific claim until it is checked against source code, logs, and evaluation results.

## Reuse and contributions

Read [CONTRIBUTING.md](CONTRIBUTING.md) before changing a claim or adding a source. The clone contains a rule snapshot; the working source of truth in the original workspace is `E:\Robot_Backup\RULE`.
