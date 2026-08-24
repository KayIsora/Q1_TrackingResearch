# Scope and terminology

## Research task contract

**[PROJECT DECISION — locked 2026-08-24]** The research program has two layers.

### Layer A — Core generic RGB box-SOT

```text
initial target bounding box
        ↓
RGB image/video
        ↓
generic class-agnostic SOT tracker
        ↓
per-frame target bounding box
        ↓
generic benchmark + efficiency/robustness evaluation
```

The Core must remain valid for people, vehicles, animals, and arbitrary objects. It must not require a person detector, ReID, language, depth, thermal, or event-camera input.

Moving-camera/robot footage is an important deployment condition, but the Core scientific contribution must stand on generic SOT benchmarks before robot-specific extensions.

### Layer B — long-term identity-sensitive target-person extension

When `target_type = person`, the validated Core may be extended with:

- identity verification;
- person memory;
- lightweight ReID;
- presence/recovery logic;
- optional lightweight detector assistance only during LOST/recovery for the person/robot extension.

The extension targets long-term target-person tracking under disappearance, re-entry, and wrong-person relock risk.

## Terms that must not be conflated

| Term | Meaning in this dossier | Not automatically included |
|---|---|---|
| SOT | One initialized target is propagated over time from an initial bounding box. | Multi-person identity assignment, segmentation, navigation, or ReID. |
| Generic/Core SOT | Class-agnostic RGB SOT evaluated independently of person-specific modules. | Person memory, identity verification, detector-assisted recovery. |
| Long-term SOT | A SOT setting in which target disappearance and re-detection matter. VOT-LT explicitly requires presence confidence and re-detection after disappearance [R6](../references/references.md#r6). | A person-specific ReID system unless separately declared. |
| Moving-camera / egocentric SOT | Camera motion is part of the visual difficulty. VISTA was designed to separate first-person-viewpoint effects from human-object activity domain effects [R3](../references/references.md#r3). | Proof of robot-person identity tracking. |
| Target-person tracking (TPT) | Tracking a specific designated person from robot-egocentric views. TPT-Bench supplies domain evidence [R1](../references/references.md#r1). | A generic SOT result, social-impact claim, or safety certification. |
| ReID | Re-identification: comparing person appearance representations to decide whether a candidate is likely the same person. | Localization, target presence, or recovery policy by itself. |
| Identity verification | Decision process for accepting/rejecting a candidate as the original designated person. | Generic object tracking unless a class-agnostic equivalent is explicitly designed. |
| Active embodied tracking | Perception and control are jointly evaluated. TrackVLA is an example of this broader direction [R5](../references/references.md#r5). | The present Core SOT scope. |
| Lightweight | A multi-dimensional deployment property involving parameters, computation, latency/FPS, memory, and runtime behavior. | Merely having few parameters or low theoretical FLOPs. |
| Researchable redundancy | Computation that is structurally identifiable and may be removed, reduced, routed, or made conditional by a scientific mechanism. | Arbitrary model size or post-hoc compression alone. |

## Core scope locks

- **[PROJECT DECISION]** Main baseline is selected from peer-reviewed/officially accepted 2025–2026 work; ArXiv-only and older work remain novelty/reference material.
- **[PROJECT DECISION]** Core input is RGB image/video + initial bounding box only.
- **[PROJECT DECISION]** LaSOT + GOT-10k + TrackingNet are mandatory final generic benchmarks.
- **[PROJECT DECISION]** The primary contribution should be algorithmic, ideally linking efficiency and robustness.
- **[PROJECT DECISION]** Fixed lower resolution is an efficiency baseline/ablation, not sufficient novelty.
- **[PROJECT DECISION]** Standard pruning/distillation/quantization may support deployment but are not automatically the main contribution.
- **[PROJECT DECISION]** RTX 3060 12 GB is the development constraint; proposed modules must be genuinely trainable.
- **[PROJECT DECISION]** Jetson Nano B01 4 GB is the primary embedded benchmark target.
- **[PROJECT DECISION]** Benchmark/model work comes before robot control.

## Person-extension scope locks

- **[PROJECT DECISION]** Person detector may initialize/select the target.
- **[PROJECT DECISION]** No detector is used every frame during normal tracking.
- **[PROJECT DECISION]** A lightweight detector may be tested separately as LOST/recovery assistance in the person/robot extension.
- **[PROJECT DECISION]** TPT-Bench is added for identity-sensitive target-person evaluation.
- **[PROJECT DECISION]** Identity consistency, long person disappearance/re-entry, and wrong-person relock belong primarily to Layer B rather than defining the Core baseline choice.

For the full operational specification, see [Research program scope and baseline-screening specification](10_research_program_scope_and_baseline_screening.md).
