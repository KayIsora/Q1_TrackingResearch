# Stage 3B — N1 HG6 source-registration plan

**Date:** 2026-08-25  
**Status:** LOCKED FOR MECHANICAL REGISTRATION BEFORE FINAL N1 RECONCILIATION  
**Inputs:** Manager N1 audit, Codex N1 audit, and both provisional source-candidate tables.

## Boundary

Manager and Codex independently agree on the provisional N1 decisions:

- CX007 SpikeTrack — `HG6 PASS`
- CX013 FARTrack — `HG6 FAIL`

The final project decisions are not yet written because every source used in the final reconciliation must first be registered in `references/references.md` and `references/source_manifest.csv`.

This plan selects only the primary sources needed to support the final N1 reasoning. It does not attempt to register every discovery lead from either lane.

## Agreed source set and fixed IDs

Existing project sources remain reused where applicable:

- R18/R19 — SpikeTrack paper/code
- R11/R12 — FARTrack paper/code
- R22/R23 — UTPTrack paper/code
- R29/R30 — DAM4SAM paper/code
- R47/R48 — UncTrack paper/code
- R49/R50 — HiT-DyHiT paper/code

The following new IDs are fixed for mechanical registration:

| ID | Source | Candidate use | Collision role |
|---|---|---|---|
| R52 | SEENN: Towards Temporal Spiking Early Exit Neural Networks | SpikeTrack | input-conditioned SNN timestep/early-exit boundary |
| R53 | Towards Efficient Spiking Transformer: a Token Sparsification Framework for Training and Inference Acceleration | SpikeTrack | spiking-transformer token sparsification boundary |
| R54 | Spiking Transformer with Experts Mixture | SpikeTrack | conditional sparse expert computation in SNNs |
| R55 | TP-Spikformer: Token Pruned Spiking Transformer | SpikeTrack | closest spiking-token/block pruning adversary, including tracking coverage |
| R56 | Adaptive Capacity Autoregressive Visual Tracking | SpikeTrack and FARTrack | difficulty-conditioned high/low tracking capacity |
| R57 | Reading Relevant Feature from Global Representation Memory for Visual Object Tracking | SpikeTrack | search-conditioned historical retrieval and redundancy control |
| R58 | ATPTrack: Visual Tracking with Alternating Token Pruning of Dynamic Templates and Search Region | FARTrack | physical dynamic-template/search pruning for robustness and compute |
| R59 | Less Is More: Token Context-Aware Learning for Object Tracking | FARTrack | autoregressive high-quality reference-token retention and redundant-token removal |
| R60 | Exploring Reliable Spatiotemporal Dependencies for Efficient Visual Tracking | FARTrack | quality-based reliable spatiotemporal memory maintenance |
| R61 | Drift-Resilient Temporal Priors for Visual Tracking | FARTrack | per-frame temporal reliability calibration and compact priors |
| R62 | An Efficient Token Compression Framework for Visual Object Tracking | FARTrack | historical-template token compression coupling efficiency and representation quality |
| R63 | BackTrack: Robust Template Update via Backward Tracking of Candidate Template | FARTrack | explicit candidate-template validity/rejection; arXiv-only novelty reference |
| R64 | Learning Quality-Aware Dynamic Memory for Video Object Segmentation | FARTrack adjacent prior art | quality-aware frame admission/eviction and bounded memory |
| R65 | RMem: Restricted Memory Banks Improve Video Object Segmentation | FARTrack adjacent prior art | physical restricted-memory selection under redundant history |

## Stable primary URLs

- R52: https://proceedings.neurips.cc/paper_files/paper/2023/hash/c801e68207da477bbc44182b9fac1129-Abstract.html
- R53: https://proceedings.mlr.press/v235/zhuge24b.html
- R54: https://proceedings.neurips.cc/paper_files/paper/2024/hash/137101016144540ed3191dc2b02f09a5-Abstract-Conference.html
- R55: https://openreview.net/forum?id=L5llQD0nMf
- R56: https://openaccess.thecvf.com/content/CVPR2026/html/Lin_Adaptive_Capacity_Autoregressive_Visual_Tracking_CVPR_2026_paper.html
- R57: https://proceedings.neurips.cc/paper_files/paper/2023/hash/2349293cb1bf2ce36d5c566f660f957e-Abstract-Conference.html
- R58: https://doi.org/10.1016/j.neucom.2025.129534
- R59: https://doi.org/10.1609/aaai.v39i8.32954
- R60: https://doi.org/10.1609/aaai.v40i11.37853
- R61: https://openaccess.thecvf.com/content/CVPR2026/html/Huang_Drift-Resilient_Temporal_Priors_for_Visual_Tracking_CVPR_2026_paper.html
- R62: https://openaccess.thecvf.com/content/CVPR2026/html/Wu_An_Efficient_Token_Compression_Framework_for_Visual_Object_Tracking_CVPR_2026_paper.html
- R63: https://arxiv.org/abs/2308.10604
- R64: https://www.ecva.net/papers/eccv_2022/papers_ECCV/html/4636_ECCV_2022_paper.php
- R65: https://openaccess.thecvf.com/content/CVPR2024/html/Zhou_RMem_Restricted_Memory_Banks_Improve_Video_Object_Segmentation_CVPR_2024_paper.html

## Required limits

- R52–R55 are not RGB-SOT MRM methods; they constrain broad SNN-adaptive-compute language.
- R56 is same-setting adaptive capacity but not MRM- or template-validity-specific.
- R57 uses fixed/quota-style historical reference selection rather than SpikeTrack MRM ambiguity allocation.
- R58–R62 substantially occupy physical reference/template pruning, reliability and compact historical representation, but differ in granularity or exact state variable.
- R63 is arXiv-only and must never be represented as peer reviewed.
- R64–R65 are adjacent VOS prior art, not generic bbox-SOT baseline evidence.

## Registration rules

1. Append R52–R65; do not renumber or alter R1–R51.
2. Use IEEE-style entries in `references/references.md`.
3. Add matching one-row records to `references/source_manifest.csv`.
4. Access date: `2026-08-25`.
5. Do not register a repository unless required for a final N1 claim.
6. Do not alter HG6 decisions, canonical matrix, Manager/Codex audit files, or batch order.
7. Validate unique IDs and CSV column counts.

## State after mechanical registration

Source registration completion permits Manager to write the final N1 reconciliation. It does not itself activate N2.

- N1 final reconciliation: PENDING
- N2: LOCKED
- S1–S7: NOT STARTED
- shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
