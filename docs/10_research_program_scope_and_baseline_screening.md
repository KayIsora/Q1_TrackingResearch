# Research program scope and baseline-screening specification

**Status:** PROJECT DECISION — locked scope for the next systematic screening stage.  
**Date:** 2026-08-24.

This document is the current operational specification for selecting the next scientific baseline. It supersedes the earlier assumption that FARTrack is the main development backbone. FARTrack remains a useful reference/case study for efficient tracker design, but the baseline search is reopened.

## 1. Research program structure

The project has two research layers.

### Layer A — Core generic SOT

The scientific core must be a **generic RGB single-object tracker (SOT)**. It must work for arbitrary target categories such as people, vehicles, animals, and objects from an initial bounding box.

The core contribution must stand on its own without person-specific components. The desired research pattern is:

1. select a strong recent tracker with a reproducible implementation;
2. identify a real computational inefficiency and a real robustness weakness;
3. propose a new algorithmic mechanism that reduces unnecessary computation and preferably also improves or preserves robustness;
4. benchmark the baseline and proposed model under matched protocols;
5. demonstrate a feasible path to embedded deployment;
6. only after the generic contribution is established, extend the system to target-person tracking.

Occlusion, distractors, localization reliability, temporal reliability, and generic recovery are valid Core topics. Person identity consistency, long person disappearance/re-entry, and wrong-person relock belong primarily to Layer B.

### Layer B — Long-term target-person extension

When `target_type = person`, the generic tracker may activate person-specific capabilities such as:

- identity verification;
- person memory;
- lightweight person ReID;
- presence estimation and recovery;
- optional lightweight person detector assistance only in LOST/recovery mode for the robot/person extension.

The person extension is intended for long-term identity-sensitive target-person tracking and later robot demonstration. It must not be required to make the generic SOT contribution scientifically meaningful.

## 2. Publication ambition

The project is not being scoped only as a thesis implementation. It is designed to preserve a credible path toward a **Q1-journal-level research contribution**.

Therefore:

- deployment alone is not sufficient novelty;
- standard compression alone is not sufficient novelty;
- a baseline replacement such as “replace heavy backbone X with lightweight backbone Y” is not sufficient by itself;
- the Core should contain at least one genuine algorithmic contribution tied to an observed weakness;
- embedded deployment is a design constraint and practical validation layer, not the sole scientific contribution.

The preferred contribution is a mechanism that links **efficiency and robustness**, e.g. reducing computation because easy states do not require the same processing as hard/uncertain states while preserving or improving hard-case tracking.

## 3. Baseline publication boundary

### Main baseline eligibility

The main scientific baseline should normally satisfy all of the following:

- peer-reviewed / officially accepted or published in **2025 or 2026**;
- top conference or Q1 journal is strongly preferred;
- online-first journal publication is eligible if peer review and official publication/acceptance status are established;
- generic RGB SOT or a directly extensible long-term SOT formulation;
- official code;
- official checkpoint(s);
- usable evaluation script/protocol.

### ArXiv-only and older work

- **ArXiv-only work is not eligible as the main baseline.**
- ArXiv-only work must still be searched during novelty auditing and may be used as a technical reference or collision warning.
- 2023–2024 work is not the preferred main baseline, but must be reviewed as prior art, idea source, and novelty adversary.
- “Not eligible as baseline” never means “safe to ignore during novelty search.”

Lower-tier venues may be retained as references or exceptional candidates only when they provide a uniquely relevant result (for example lightweight, long-term, embedded, or Jetson evidence) and the reason for keeping them is explicitly recorded.

## 4. What “heavy enough to improve” means

The project does **not** seek the heaviest tracker possible.

The target is a tracker with **researchable computational redundancy**: computation that is substantial, structurally identifiable, and plausibly removable or made conditional without relying on desperate post-hoc compression.

Examples of researchable redundancy include:

- too many template/search tokens processed in every frame;
- global attention used even when local reasoning is sufficient;
- fixed computation for both easy and difficult frames;
- excessive or stale memory/template processing;
- expensive template–search fusion;
- unnecessarily large search regions or fixed high input resolution;
- backbone depth/width that is not equally useful for every tracking state;
- temporal computation repeated despite low scene/target change;
- operators that are poorly matched to edge hardware.

A candidate should be rejected or strongly penalized if it is so large that the project depends on future pruning/quantization simply to make research possible.

## 5. Desired relation between efficiency and robustness

The strongest candidate has a weakness where computation and tracking quality are causally or structurally connected.

Preferred research pattern:

```text
Easy / reliable state
        -> cheaper computation path

Hard / uncertain state
        -> stronger computation path
```

The goal is not merely “compress first, add robustness module later.” A more valuable direction is one mechanism that can achieve both:

- lower average computation;
- equal or improved robustness on difficult conditions.

Possible robustness axes for Core include:

- occlusion;
- distractors;
- fast motion;
- deformation;
- camera motion;
- scale change;
- search uncertainty;
- generic short/long-term recovery;
- unreliable template or memory updates.

Person identity is deliberately deferred to Layer B unless the mechanism is genuinely class-agnostic.

## 6. Allowed improvement space

The project may consider the full design space:

- backbone redesign/replacement;
- pruning;
- knowledge distillation;
- quantization;
- low-rank approximation;
- adaptive/dynamic computation;
- token reduction, pruning, routing, or merging;
- memory/template reduction;
- conditional search resolution or search-region adaptation;
- new lightweight modules;
- reliability-aware computation;
- architecture redesign.

### Contribution boundary

Standard deployment techniques such as fixed pruning, FP16/INT8 conversion, TensorRT export, or a fixed lower input resolution are useful tools but are **not sufficient as the primary novelty**.

Fixed lower resolution may be used as an efficiency baseline/ablation. Adaptive resolution or computation that is selected by model state/difficulty may be part of a primary contribution.

A backbone may be replaced completely if the scientific mechanism remains clear. If the resulting architecture is substantially new, it must be described honestly as a **new tracker derived from / motivated by the baseline**, not as a minor baseline modification. Stepwise ablation must connect each change to the final design.

## 7. Training feasibility boundary

### Development hardware

- Primary research hardware: **single RTX 3060 12 GB**.
- Official pretrained checkpoints may be used for initialization.
- Training the original baseline from random initialization is not mandatory.
- Proposed modules must be genuinely trained.
- The project should allow joint fine-tuning of a meaningful part or all of the proposed network when feasible.
- The amount of freezing/unfreezing should be decided experimentally and reported through ablation rather than assumed in advance.

### Teacher models / offline supervision

A larger teacher model may be used during training or offline feature/label generation if:

- it is absent at inference;
- the training cost is reported;
- the pipeline remains reproducible;
- the project does not depend on inaccessible compute resources;
- the main student/proposed training workflow remains feasible on the RTX 3060-class setup.

### Training data

The full standard training datasets used by the baseline are allowed, including LaSOT, GOT-10k, TrackingNet, COCO, and equivalent standard resources where licensing/protocol permits.

Development may use reduced sampling/subsets. Final controlled comparisons should use matched training data and protocol between baseline and proposed models.

## 8. Evaluation protocol

### Mandatory generic benchmarks

The final baseline and proposed Core model must be evaluated on:

1. **LaSOT** — long-sequence robustness;
2. **GOT-10k** — generalization to unseen object classes/protocol;
3. **TrackingNet** — large-scale and diverse tracking performance.

Additional benchmarks such as TNL2K and LaSOT-ext may be used when relevant.

For Layer B, **TPT-Bench** is added for long-term target-person / identity-sensitive evaluation.

### Reproduction versus controlled comparison

Keep two result layers separate:

1. **Official-baseline reproduction:** use official checkpoint/configuration to verify implementation and evaluator consistency.
2. **Controlled comparison:** train/fine-tune baseline and proposed model under the same data/protocol/budget wherever scientifically appropriate so gains are attributable to the proposed mechanism rather than unequal training.

### Accuracy-efficiency target

The proposed model does not need absolute zero accuracy loss. A generic benchmark decrease of approximately **0.3–0.5 points maximum** can be acceptable when accompanied by a clear, substantial efficiency/deployment gain. Equal or higher accuracy remains preferable.

A paper-quality claim must report the full trade-off rather than hiding a small accuracy loss behind FPS.

## 9. Lightweight metrics

“Lightweight” is multi-dimensional and must not be reduced to parameter count.

At minimum report:

- parameter count;
- MACs/FLOPs;
- FPS/throughput;
- per-frame latency;
- peak runtime memory/RAM;
- input resolution;
- precision/runtime backend.

Where relevant also report model size and hardware utilization/operator bottlenecks.

A theoretical FLOPs reduction that does not improve target-device speed must not be presented as a deployment success.

## 10. Embedded deployment boundary

### Main target

**Jetson Nano B01 4 GB** is the required primary embedded benchmark target.

Desired end-to-end performance at batch size 1:

- **>= 25 FPS:** target;
- **>= 20 FPS:** acceptable near-real-time deployment range;
- **< 10 FPS:** does not meet the project lightweight objective;
- **>= 30 FPS:** very strong but not mandatory.

Candidate selection must leave enough speed headroom that the proposed contribution can be added without making 20–25 FPS structurally implausible.

Jetson Orin Nano may be reported as a secondary platform, but it must not be used to justify choosing an obviously over-heavy baseline.

### Deployment optimization

Allowed:

- TensorRT;
- FP16;
- INT8 as an additional optimization/ablation.

Primary algorithm comparisons should use matched precision/protocol, preferably FP32 or FP16. TensorRT FP16 is the preferred deployment path. INT8 must report both speed gain and accuracy loss and should not be the only mechanism that makes the architecture deployable.

### Device measurements

Jetson results must be measured directly. Report at least:

- end-to-end FPS;
- tracker-only and end-to-end latency where possible;
- batch size 1;
- peak RAM;
- long-run stability;
- thermal/throttling observations where measurable.

Never infer Jetson Nano FPS from desktop GPU, Orin, FLOPs, parameter count, CPU, or NPU figures.

## 11. RGB-only modality boundary

The Core uses only:

- RGB image/video;
- an initial bounding box.

No language prompt, depth, thermal, or event-camera input is allowed in the main Core comparison.

Features computed from RGB, including trajectory, optical flow, appearance embeddings, or person ReID for Layer B, are allowed, but their full inference cost must be included in deployment measurements.

## 12. Detector boundary

Generic SOT benchmark:

- no external detector is used after initialization.

Person/robot extension:

- a person detector may initialize/select the target;
- no detector is used every frame during normal tracking;
- a lightweight person detector may be evaluated separately as a LOST/recovery aid;
- detector-assisted results must remain clearly separated from pure tracker results.

## 13. FARTrack status after scope reset

**PROJECT DECISION — 2026-08-24:** FARTrack is no longer the assumed main baseline.

Reason:

- FARTrack already solves the lightweight/efficiency side unusually well through TSSD and IFAS;
- the remaining disappearance/identity/recovery opportunities are scientifically interesting but risk collapsing the Core into a narrower identity/presence extension rather than the intended “researchable redundancy + robustness weakness” program;
- therefore FARTrack is retained as a reference for efficient autoregressive design, distillation, sparsification, failure-audit methodology, and later comparison, but baseline selection is reopened.

This does **not** mean FARTrack is weak or that its previously identified failure hypotheses are rejected. They simply no longer define the Core baseline-selection strategy.

## 14. Systematic screening pipeline — next stage

The next stage must be systematic rather than tracker-first.

### Stage 1 — broad discovery

Collect peer-reviewed 2025–2026 RGB SOT/long-term-SOT candidates plus recent novelty-adversary work.

### Stage 2 — eligibility filter

Reject main-baseline candidates lacking reproducible official code/checkpoint/evaluation, unacceptable hardware dependence, incompatible modality, or no credible path to the target compute envelope.

### Stage 3 — scientific audit

For each surviving tracker, record:

- published strength and benchmark competitiveness;
- architecture and compute distribution;
- parameter/MAC/FLOP/runtime evidence;
- training hardware and recipe;
- author-reported limitations;
- code-visible bottlenecks;
- robustness weaknesses;
- computational redundancy;
- whether computation and weakness can be addressed by one mechanism;
- 2023–2026 novelty collisions;
- RTX 3060 training feasibility;
- Jetson Nano deployment headroom;
- estimated research risk.

### Stage 4 — shortlist

Select approximately 2–3 candidates with the strongest combination of:

**recent + reproducible + competitive + researchable redundancy + robustness weakness + RTX3060 feasibility + Jetson headroom + novelty space.**

### Stage 5 — reproduce before architecture commitment

Do not commit to a final proposed architecture until the chosen candidate is reproduced and the hypothesized redundancy/weakness is demonstrated empirically.

## 15. Baseline-selection rejection rules

Strongly reject or penalize a candidate when:

- it requires inaccessible compute merely to conduct the research;
- source/checkpoint/evaluator is incomplete;
- deployment viability depends entirely on future INT8/pruning;
- the only obvious contribution is fixed resolution reduction or backbone replacement;
- the weakness has already been substantially solved by recent prior art;
- no measurable computational redundancy can be located;
- its reported speed cannot be meaningfully profiled or exported;
- adding the proposed contribution would leave no plausible path to Jetson Nano;
- the Core novelty only exists after adding person-specific ReID/identity logic.

## 16. Current one-sentence target

> **Find a strong, peer-reviewed 2025–2026 generic RGB SOT tracker with reproducible code, a real and researchable source of computational redundancy, and a meaningful robustness weakness; design a new mechanism that reduces unnecessary computation while preserving or improving tracking quality, validate it on LaSOT/GOT-10k/TrackingNet, then prove embedded feasibility on Jetson Nano before extending it to long-term identity-sensitive target-person tracking.**
