# Tracker-selection boundary

## No tracker is selected

**PROJECT DECISION.** The project is deliberately not “SiamABC-Tiny research,” “Transformer tracking,” or a porting exercise. The problem and evaluation contract must be locked before selecting a base tracker.

SiamABC is an efficient visual-tracking paper that can later be audited as a possible reproducibility candidate [R10](../references/references.md#r10). That citation does **not** prove it is appropriate for the selected application, that it runs on original Jetson Nano, or that it should be the base model.

## Minimum selection criteria

A candidate tracker can enter the shortlist only when all items below have a recorded source or experiment:

1. Correct task output: box and a usable presence/confidence policy for long-term tracking.
2. Public code, weights, licence, and reproducible evaluation path.
3. Compatible data/training recipe for the available RTX 3060 budget, or an explicitly limited fine-tuning plan.
4. A clear baseline relation to the selected failure mode (identity, occlusion/re-entry, distractor), not only generic SOT popularity.
5. A realistic Jetson Nano profiling path with no unverified cross-device FPS inference.
6. A method improvement that survives a novelty audit and can be ablated against matched baselines.

## Non-claims to preserve

- Do not call a model “SOTA” without a date, benchmark, split, protocol, and primary source.
- Do not infer Nano feasibility from Orin, AGX, TX2, desktop GPU, phone, or paper FLOPs.
- Do not turn detection-assisted re-identification into pure SOT without declaring the task change.
