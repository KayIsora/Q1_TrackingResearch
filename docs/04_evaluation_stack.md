# Dataset and evaluation roles

## Core generic benchmark stack — PROJECT DECISION

The final generic SOT baseline and proposed Core model must be evaluated on three mandatory benchmarks:

| Benchmark | Required role |
|---|---|
| **LaSOT** | Long-sequence robustness and accumulated tracking difficulty. |
| **GOT-10k** | Generalization under the official protocol and unseen-category design. |
| **TrackingNet** | Large-scale and diverse generic tracking evaluation. |

Additional generic benchmarks such as **TNL2K** and **LaSOT-ext** may be added when they directly test the proposed mechanism or align with the selected baseline literature.

The three mandatory benchmarks are intentionally complementary so the proposed method cannot be justified by improvement on a single benchmark alone.

## Target-person extension benchmark

**TPT-Bench** is reserved as a mandatory domain benchmark when the Layer-B long-term identity-sensitive target-person extension is developed.

TPT-Bench must not replace the generic Core benchmark stack. It is additional evidence for person/robot/crowd conditions, long disappearance, re-entry, and same-person recovery.

## Additional long-term / diagnostic resources

| Resource | FACT — cited | Intended role in this project | Boundary |
|---|---|---|---|
| TPT-Bench | 48 robot-egocentric target-person sequences; Zenodo reports 5.3 h and 571,982 target boxes [R1](../references/references.md#r1), [R2](../references/references.md#r2). | **Layer-B mandatory domain validation** for person/robot/crowd failure modes. | Follow the official toolkit; do not redistribute the data. Keep detector-assisted modes separate from pure tracker evaluation. |
| VISTA | ICCV 2025 benchmark built from synchronized first- and third-person videos to disentangle viewpoint from activity-domain effects [R3](../references/references.md#r3). | Optional mechanism diagnostic for moving/egocentric viewpoint effects. | Not a replacement for generic SOT or robot-person evidence. |
| EgoTracks | Official long-term egocentric SOT task predicts target location and presence confidence [R4](../references/references.md#r4). | Optional generic long-term egocentric transfer/recovery diagnostic. | Not a robot-person benchmark. Respect Ego4D access conditions. |
| VOT-LT2022 | Official long-term challenge requires causal tracking, presence confidence, target-disappearance handling, and re-detection after re-entry [R6](../references/references.md#r6). | Optional generic bbox+presence long-term protocol check. | Cannot substitute for the mandatory LaSOT/GOT-10k/TrackingNet Core stack or TPT-Bench person validation. |

## Training-data policy

The project may use the standard training resources used by the selected baseline, including LaSOT, GOT-10k, TrackingNet, COCO, and equivalent public/standard resources where licensing and official protocol allow.

Rules:

- development may use reduced sampling/subsets for fast iteration;
- final controlled experiments should scale toward the declared baseline recipe within RTX 3060/time constraints;
- the baseline and proposed model in the main controlled comparison should use the same training data and protocol wherever scientifically appropriate;
- a candidate is not rejected solely because its original recipe uses a large dataset if official pretrained checkpoints are available, but training-data cost is part of feasibility screening;
- exact dataset licenses, split restrictions, and benchmark training/test boundaries must be checked before final experiments.

## Two-layer result reporting

### A. Official baseline reproduction

Use the official checkpoint/configuration/evaluator to verify that the local implementation behaves consistently with the published method.

### B. Controlled scientific comparison

Compare baseline and proposed model under matched:

- training data;
- evaluation protocol;
- input settings where the contribution does not explicitly change them;
- hardware/precision for performance comparison;
- training budget where scientifically appropriate.

If the proposed method changes objective, resolution policy, architecture, or computation routing, declare the change and isolate it through ablation.

## Accuracy-efficiency boundary

Absolute zero accuracy loss is not mandatory.

A drop of roughly **0.3–0.5 benchmark points maximum** may be acceptable when the proposed model achieves a substantial and reproducible efficiency/deployment gain. Equal or improved accuracy remains preferable.

All accuracy losses and gains must be reported rather than hidden behind an FPS claim.

## Lightweight measurements

At minimum report:

- parameter count;
- MACs/FLOPs;
- FPS/throughput;
- per-frame latency;
- runtime memory/RAM;
- input resolution;
- numerical precision/runtime backend.

For Jetson Nano, also report long-run stability and thermal/throttling observations when measurable.

## Detector/evaluation separation

- Generic SOT benchmark: no external detector after initialization.
- Person extension: detector may initialize/select target.
- Lightweight detector assistance may be evaluated separately during LOST/recovery for the robot/person extension.
- Pure tracker, detector-assisted recovery, and robot-control results must be reported as separate system configurations.

## Evaluation hygiene

- Freeze the final benchmark protocol before test-set tuning.
- Use the official evaluators and current dataset protocols.
- Report variance/multiple seeds when training stochasticity is material.
- Do not mix official-checkpoint results with retrained/proposed results without labeling them.
- Do not infer embedded speed from theoretical compute or another hardware platform.
