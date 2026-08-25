# Stage 3B — N2 HG6 source-registration plan

**Date:** 2026-08-25  
**Status:** LOCKED FOR MECHANICAL REGISTRATION BEFORE FINAL N2 RECONCILIATION  
**Inputs:** Manager N2 audit, Codex N2 audit, and both provisional N2 source-candidate tables.

## Boundary

Manager and Codex independently agree on the provisional N2 decisions:

- CX044 AsymTrack — `HG6 FAIL`
- CX058 HiT-DyHiT — `HG6 FAIL`

The final project decisions are not yet written because primary sources used in the final reconciliation must first be registered in `references/references.md` and `references/source_manifest.csv`.

This plan selects only the sources needed to support the final N2 reasoning. It does not register every discovery lead from either independent lane.

## Existing sources reused

- R39/R40 — AsymTrack paper/code
- R49/R50 — HiT-DyHiT paper/code
- R56 — Adaptive Capacity Autoregressive Visual Tracking

## Fixed new IDs

| ID | Source | Candidate use | Collision role |
|---|---|---|---|
| R66 | Learning Policies for Adaptive Tracking With Deep Feature Cascades | AsymTrack | foundational frame-difficulty-conditioned feature-depth allocation in SOT |
| R67 | Depth-Adaptive Computational Policies for Efficient Visual Tracking | AsymTrack and HiT-DyHiT | foundational cost-aware tracker-depth policy under object/frame difficulty |
| R68 | Exploring Dynamic Transformer for Efficient Object Tracking | AsymTrack and HiT-DyHiT | easy/hard dynamic route allocation and attribute-conditioned compute |
| R69 | Adaptively Bypassing Vision Transformer Blocks for Efficient Visual Tracking | AsymTrack and HiT-DyHiT | target/scene-dependent block bypassing in generic SOT |
| R70 | Learning Adaptive and View-Invariant Vision Transformer for Real-Time UAV Tracking | AsymTrack | adaptive block activation combined with viewpoint-invariant representation |
| R71 | Similarity-Guided Layer-Adaptive Vision Transformer for UAV Tracking | AsymTrack | layer-adaptive capacity and representation-redundancy control |
| R72 | Learning Motion Blur Robust Vision Transformers for Real-Time UAV Tracking | AsymTrack | dynamic early exit combined with motion-blur/fast-motion robustness |
| R73 | Efficient Early Exit Single Object Tracking via General Distribution | AsymTrack and HiT-DyHiT | clutter/object-background distinguishability conditioned early-exit depth |
| R74 | Adaptive Depth Lightweight RGB-T Tracking with Holistic Token Routing | HiT-DyHiT | confidence-calibrated tracking early exit and adaptive depth |
| R75 | Uncertainty-Guided Inference-Time Depth Adaptation for Transformer-Based Visual Tracking | HiT-DyHiT | uncertainty and temporal-feedback depth adaptation; arXiv-only novelty reference |
| R76 | MVLM: Template-Free Tracking via Vision-Language Margin Confidence and Memory-Gated Tracking | HiT-DyHiT | target-competitor margin gating of compact/global tracking modes |
| R77 | Fixing Overconfidence in Dynamic Neural Networks | HiT-DyHiT adjacent prior art | confidence calibration for dynamic-depth/early-exit decisions |

## Stable primary URLs

- R66: https://openaccess.thecvf.com/content_ICCV_2017/papers/Huang_Learning_Policies_for_ICCV_2017_paper.pdf
- R67: https://doi.org/10.1007/978-3-319-78199-0_8
- R68: https://doi.org/10.1109/TNNLS.2025.3545752
- R69: https://doi.org/10.1016/j.patcog.2024.111278
- R70: https://proceedings.mlr.press/v235/li24ax.html
- R71: https://openaccess.thecvf.com/content/CVPR2025/html/Xue_Similarity-Guided_Layer-Adaptive_Vision_Transformer_for_UAV_Tracking_CVPR_2025_paper.html
- R72: https://doi.org/10.1016/j.eswa.2025.129445
- R73: https://doi.org/10.1016/j.neucom.2025.131888
- R74: https://openaccess.thecvf.com/content/CVPR2026/html/Ding_Adaptive_Depth_Lightweight_RGB-T_Tracking_with_Holistic_Token_Routing_CVPR_2026_paper.html
- R75: https://arxiv.org/abs/2602.16160
- R76: https://openaccess.thecvf.com/content/CVPR2026/html/Park_MVLM_Template-Free_Tracking_via_Vision-Language_Margin_Confidence_and_Memory-Gated_Tracking_CVPR_2026_paper.html
- R77: https://openaccess.thecvf.com/content/WACV2024/html/Meronen_Fixing_Overconfidence_in_Dynamic_Neural_Networks_WACV_2024_paper.html

## Required limits

- R66–R69 establish generic SOT depth/route/block allocation but do not use AsymTrack's exact T/S/B family or HiT's exact route names.
- R70–R72 are UAV-oriented; they constrain adaptive-viewpoint/motion robustness claims but are not generic-benchmark equivalence evidence.
- R73 is generic SOT early exit conditioned by object/background distinguishability; it does not implement AsymTrack family switching or paired DyHiT forced-route regret.
- R74 is RGB-T, not RGB-only; it nevertheless constrains confidence-calibrated early-exit novelty language.
- R75 is arXiv-only and must never be represented as peer reviewed.
- R76 is vision-language/template-free tracking with local/global mode gating, not DyHiT depth routing.
- R77 is adjacent dynamic-classifier calibration prior art, not tracking evidence.

## Registration rules

1. Append R66–R77; do not renumber or materially alter R1–R65.
2. Use IEEE-style entries in `references/references.md`.
3. Append matching eight-column records to `references/source_manifest.csv`.
4. Access date: `2026-08-25`.
5. Do not register a repository unless needed for a final N2 claim.
6. Do not change N2 HG6 decisions, the candidate matrix, Manager/Codex audit files, or any score.
7. Validate unique IDs, sequential headings, and CSV column counts.

## State after registration

Source registration completion permits Manager to write final N2 reconciliation and mechanically update the two N2 matrix rows.

- N2 final reconciliation: PENDING
- Stage 3B final closure: PENDING
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
