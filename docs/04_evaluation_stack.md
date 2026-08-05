# Dataset and evaluation roles

## No training mixture is selected yet

**OPEN QUESTION.** Dataset access, licence, storage, split rules, and the RTX 3060 training profile must be checked before choosing a training/fine-tuning mixture. Therefore this repository does **not** claim that six datasets will be trained on, nor that a benchmark may be used for training.

## Benchmark role map

| Resource | FACT — cited | Intended role in this project | Boundary |
|---|---|---|---|
| TPT-Bench | 48 robot-egocentric target-person sequences; Zenodo reports 5.3 h and 571,982 target boxes [R1](../references/references.md#r1), [R2](../references/references.md#r2). | **[PROJECT DECISION] Mandatory domain validation** for person/robot/crowd failure modes. | Follow the official toolkit; do not redistribute the data. Keep detector-assisted demos separate from pure tracker evaluation. |
| VISTA | ICCV 2025 benchmark built from synchronized first- and third-person videos to disentangle viewpoint from activity-domain effects [R3](../references/references.md#r3). | **[PROJECT DECISION] Mechanism diagnostic** for moving/egocentric viewpoint effects. | Object/human-activity benchmark, not robot-person evidence; it includes occlusion/out-of-view attributes and must not be described as lacking them. |
| EgoTracks | Official long-term egocentric SOT task predicts target location and presence confidence; use its current official data documentation for the release composition and splits [R4](../references/references.md#r4). | **[PROJECT DECISION] Generic long-term egocentric transfer/recovery diagnostic.** | Not a robot-person benchmark. Access must obey Ego4D terms. |
| VOT-LT2022 | Official long-term challenge requires causal tracking, presence confidence, target-disappearance handling, and re-detection after re-entry [R6](../references/references.md#r6). | **[PROJECT DECISION] Generic bbox+presence long-term protocol check.** | It cannot substitute for robot-person validation. |

## Failure-to-test mapping

| Claimed failure / question | Primary evaluation evidence | Required result type |
|---|---|---|
| Same-person continuity in crowd, long disappearance, re-entry | TPT-Bench | Domain-specific measures from the official protocol plus an explicit wrong-person/error analysis. |
| Moving-camera / first-person viewpoint sensitivity | VISTA | Report the benchmark’s declared viewpoint-aware protocol; do not claim person tracking. |
| Generic long-term presence/recovery | EgoTracks and VOT-LT2022 | Presence-aware long-term metrics using each official evaluator. |
| Embedded feasibility | Jetson Nano replay and later small field set | Device-only latency, memory, thermal/stability, and end-to-end timing; see [edge boundary](05_edge_boundary.md). |

## Evaluation hygiene

- **[PROJECT DECISION]** Freeze the benchmark protocol before tuning on a final test set.
- **[PROJECT DECISION]** Report three seeds and confidence intervals when training variance is meaningful.
- **[PROJECT DECISION]** Report pure SOT, detector-assisted initialization/re-detection, and robot-control results as separate systems.
- **OPEN QUESTION:** Exact metrics, splits, and allowable training data must be copied from the current official evaluator before an experiment begins.
