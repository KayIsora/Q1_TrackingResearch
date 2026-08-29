# Manager review request

## Requested decision

Review Knowledge Graph V1 at the boundary `KNOWLEDGE_GRAPH_V1_READY_FOR_MANAGER_REVIEW`. No third baseline or final SpikeTrack architecture has been selected.

## Completed

- parsed both supplied Connected Papers BibTeX exports;
- excluded the named neuroscience SpikeTrack collision by scope (the file was absent, so it supplied zero rows);
- mechanically deduplicated by DOI, arXiv ID, Semantic Scholar ID, and normalized title, then manually reconciled the LoReTrack version pair;
- verified the two anchors and high-relevance donor publication status with primary sources;
- built taxonomy, 15 paper cards, deep FARTrack and SpikeTrack decompositions, transfer matrix, redesign space, teacher report, evidence log, and CSV/GraphML/Mermaid graphs;
- preserved the historical whole-MRM1 `DIAG_FAIL` and consumed-hold-out boundary [E08].

## Inventory numbers

| Measure | Count |
|---|---:|
| FARTrack input graph | 41 |
| SpikeTrack input graph | 41 |
| Raw records | 82 |
| Exact cross-graph overlaps | 7 |
| Mechanical unique clusters | 75 |
| Final unique papers after LoReTrack version merge | 74 |
| Named neuroscience collision rows parsed | 0 |
| Retained but out-of-scope visual-SOT records | 1 (CSCL) |

The three initial manual-review flags are resolved: LoReTrack is one arXiv/IROS work [E15], OiRT is visual SOT [E25], and VideoTrack is canonicalized to its CVPR 2023 paper [E26]. There are no remaining `unclear` publication-status or `UNKNOWN` relevance rows in the final deduplicated inventory.

## Top recurring families

1. robustness/distractor handling — 30;
2. dynamic/conditional computation — 14;
3. asymmetric template-search architecture — 12;
4. relation/cross-attention modeling — 12;
5. lightweight backbone design — 11;
6. autoregressive/sequence modeling — 11;
7. target-aware representation — 11;
8. training/loss redesign — 10;
9. temporal/video memory — 9;
10. compression/distillation, pruning, and motion — 7 each.

These are abstract/title-screening incidences and need not correlate with quality.

## Highest-value donor/collision papers

- CompressTracker [E10]
- MixFormerV2 [E11]
- AsymTrack [E09]
- LiteTrack [E12]
- LoReTrack [E15]
- ARPTrack [E17]
- HiT [E18]
- SpikeFET [E20]
- STDTrack [E21]
- DyTrack as a conditional-computation collision/negative-control reference [E13]

All remain knowledge donors; none is promoted to an anchor or baseline.

## Factual blockers

- no verified Jetson Nano FPS, board power, thermal, or energy measurement;
- no successful ONNX/TensorRT export and parity result;
- no conventional-edge sparse-spike kernel evaluation;
- FARTrack public code diverges from the paper on historical trajectory use, salience inputs, sparse execution, normalization, and parts of training [E03, E04];
- no retrained SpikeTrack evidence for changed depth, width, timestep, memory, MRM count/dimensions, head, loss, or resolution;
- official-code status remains `UNKNOWN` for part of the long tail; absence of a found URL is not a `NO` claim.

## Claims needing manual review

1. Accept the manual LoReTrack preprint-to-IROS merge and final count of 74.
2. Accept use of title/abstract-derived low-confidence family tags for the long tail while restricting architectural conclusions to primary-verified cards.
3. Decide whether future work should first authorize a **parity/runtime lane** (module consolidation and flat cache bindings) or one **scientific retraining lane** from P01-P10. Version 1 does not choose between them.
4. Seek author clarification before claiming FARTrack public-code reproduction parity.

## Guarded next boundary

Do not begin combined architecture design, new hold-out use, or baseline selection until Manager review. The redesign entries are individually testable hypotheses only.

`KNOWLEDGE_GRAPH_V1_READY_FOR_MANAGER_REVIEW`
