# Edge-deployment claim boundary

## Fixed deployment decisions

- **Primary embedded target:** Jetson Nano B01 4 GB.
- **Research/training hardware:** single RTX 3060 12 GB.
- **Secondary platform:** Jetson Orin Nano may be reported if useful, but it cannot justify selecting an over-heavy baseline.
- **Core modality:** RGB-only SOT from an initial bounding box.

Jetson Nano is not merely a demonstration device; it is a required benchmark target that constrains baseline selection. However, candidate selection must consider **deployment headroom**, not only a guessed current FPS.

## Runtime targets

End-to-end, batch-size-1 target:

- **>= 25 FPS:** desired project target;
- **>= 20 FPS:** acceptable near-real-time operating range;
- **< 10 FPS:** fails the project lightweight objective;
- **>= 30 FPS:** very strong result but not mandatory.

These are project targets, not claims about any currently selected tracker.

## Candidate-selection implication

Do not choose a baseline that is so computationally heavy that future pruning/INT8 is the only imaginable path to deployment.

A good candidate should have:

- feasible research/training on RTX 3060 12 GB;
- identifiable computation that can be reduced by a scientific mechanism;
- enough speed/memory headroom that adding the proposed contribution does not make Nano feasibility structurally implausible;
- operators/runtime paths that can reasonably be exported/profiled on Jetson.

A candidate need not already achieve 20–25 FPS on Nano before research, but there must be a credible mechanism-based route toward that range.

## Allowed deployment optimization

Allowed:

- TensorRT;
- FP16;
- INT8 as an additional optimization/ablation;
- implementation-level kernel/operator cleanup consistent with the declared algorithm.

Preferred deployment configuration: **TensorRT FP16**.

INT8 is allowed only when accuracy loss and speed gain are both reported. It must not be used to hide the fact that an architecture was impractically heavy from the start.

Fixed lower input resolution is allowed as an efficiency baseline/ablation but is not sufficient algorithmic novelty. Adaptive resolution or state-dependent computation may be part of the proposed scientific mechanism.

## Precision fairness

Algorithmic baseline-versus-proposed comparisons should use matched precision/runtime protocol, preferably FP32 or FP16.

Deployment results may report additional TensorRT/INT8 variants, but they must be clearly separated from the main algorithmic comparison.

## Required Nano measurements

All deployment claims must be measured directly on the actual target device with frozen configuration.

Report at minimum:

1. device/software/runtime version;
2. input resolution;
3. numerical precision;
4. batch size = 1;
5. warm-up procedure;
6. tracker-only latency where measurable;
7. end-to-end camera/video-to-output latency;
8. FPS / stable throughput;
9. latency distribution (p50/p95/p99 where practical);
10. peak RAM/shared-memory use;
11. long-run stability;
12. thermal/throttling observations where measurable;
13. accuracy consistency between exported engine and reference model.

If power is reported, the measurement source/method must be stated.

## Prohibited inference

Never infer Jetson Nano feasibility or FPS from:

- desktop GPU FPS;
- Jetson Orin/AGX/TX2 results;
- CPU/NPU results;
- parameter count alone;
- MACs/FLOPs alone;
- theoretical throughput.

A reduction in FLOPs that does not produce target-device speed/memory improvement is not sufficient evidence of embedded success.

## Claim language before profiling

Until direct measurements exist, use only language such as:

> **candidate for Jetson Nano profiling**

or

> **architecture with a plausible Nano deployment path**

Never write “real-time on Jetson Nano” before actual measurement.
