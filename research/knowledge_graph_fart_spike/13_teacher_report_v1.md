# Teacher report — FARTrack + SpikeTrack Knowledge Graph V1.1

## Executive message

> **We stopped searching for a third main tracker. Connected Papers discovers solution neighborhoods; the other trackers are knowledge donors.**

FARTrack remains the lightweight-design knowledge anchor because its methodology is useful. SpikeTrack remains the redesign target. We transfer design principles by functional analogy, not incompatible architecture. The strongest current hypothesis family is **static structural reduction plus tracking-specific knowledge preservation/distillation**. No final SpikeTrack architecture has been selected.

## 1. Repaired inventory and provenance

| Item | V1.1 result |
|---|---:|
| FARTrack discovery export | 41 raw records |
| SpikeTrack discovery export | 41 raw records |
| Raw visual-SOT total | 82 records, unchanged |
| Mechanical clusters | 75 |
| LoReTrack version reconciliation | -1 |
| Deduplicated identities | 74 |
| Publication status | 38 conference; 32 journal; 4 arXiv/preprint only; 0 accepted/online-first; 0 unclear |
| Metadata audit tiers | 14 primary-verified high-relevance; 56 metadata-canonicalized; 4 arXiv-only verified |
| Neuroscience collision export | 41 records; Manager-inspected; 0 visual-SOT rows |

`01_connected_papers_inventory.csv` remains the untouched raw export parse. The canonical layer is `02_deduplicated_paper_inventory.csv`, with the per-identity audit in `15_canonical_metadata_audit_v1_1.csv` [E27]. Known V1 errors were repaired, and the same systematic DOI/proceedings check corrected additional year/venue/title cases rather than patching only seven named rows.

The separate neuroscience SpikeTrack export existed in the user/Manager handoff. Manager verified that its 41 records concern neural electrodes, recording, and spike sorting. It was excluded before the visual-SOT corpus and contributes zero rows, nodes, or edges. Codex did not claim to parse it [E28].

## 2. How to read the graphs

- `12a_methodology_flow_v1_1.mmd` explains discovery, evidence, and review workflow. It is not a tracker taxonomy.
- `12b_tracker_solution_knowledge_graph_v1_1.mmd` is the curated teacher-facing view: tracker -> problem -> mechanism -> principle -> FARTrack/SpikeTrack relationship.
- `11_knowledge_graph_v1.graphml`, `09_nodes.csv`, and `10_edges.csv` remain the complete machine-readable semantic graph.

Publication-frequency counts are secondary descriptive statistics. Frequency is not importance, evidence strength, novelty, or an experiment priority.

## 3. Why FARTrack remains useful

FARTrack combines two separable ideas [E03, E04]:

1. task-specific self-distillation supports static depth/capacity reduction while preserving tracker outputs;
2. inter-frame autoregressive sparsification amortizes conservative template-token decisions.

The transferable lesson is to state **what is reduced**, **what task behavior must be preserved**, and **how the reduced model is trained**. FARTrack paper/code discrepancies remain explicit; it is a methodology anchor, not a claim of reproduced parity.

## 4. Why SpikeTrack is the redesign target

SpikeTrack offers spike-driven representations, cached template memories, and analytical operation-energy advantages [E05-E07, E23-E24]. On conventional edge GPUs, however, its actual runtime still includes dense operators, six MRMs, separate resident branches, head towers, and deployment-sensitive cache interfaces. Analytical spike energy, CUDA latency, and board power remain different outcomes.

## 5. Manager priority interpretation

### Primary scientific hypothesis family

**P01 + P02 are one family:** FARTrack-inspired static structural compression of SpikeTrack plus task-facing preservation/distillation.

- **What to reduce:** fixed stage/block depth or capacity.
- **What to preserve:** tracking-specific heatmap/box or other task-facing behavior.
- **How to train:** a SpikeTrack-compatible teacher/student or stage-wise compression procedure.
- **Supporting donor:** P04/CompressTracker supplies stage-replacement and compression-training evidence; it is not automatically a separate contribution.
- **Boundary:** strongest current lane, but novelty collision remains `HIGH`; no mechanism or architecture is approved.

### Engineering enablement

P06 is parity/runtime/export work: module consolidation and typed cache boundaries under strict output parity. It supports deployment but is not the main scientific contribution.

### Secondary/exploratory

P03, P05, and P09 remain possible later studies in template-memory compression, cross-resolution distillation, and reliability-aware template updates.

### Defer / high collision / indirect compute benefit

P07, P08, P10, and generic dynamic-routing or conditional-exit routes are not equal-priority first experiments. Dynamic computation is crowded, and indirect training benefits do not establish runtime reduction.

## 6. Guardrails and unresolved work

The historical conditional whole-MRM1 skip remains `DIAG_FAIL`; its sealed hold-out is consumed and there is no post-hoc rescue [E08]. Scientific redesign and parity/runtime/export work are separate, mutually supporting lanes. V1.1 runs no experiment, trains no model, selects no baseline, and selects no final architecture.

Still unresolved are Jetson Nano measurements, successful ONNX/TensorRT export parity, sparse-spike kernels on conventional edge GPUs, FARTrack paper/code parity questions, and trained evidence for any proposed SpikeTrack reduction. These are future authorization points, not defects repaired by this desk-only pass.

**Terminal state:** `KNOWLEDGE_GRAPH_V1_1_READY_FOR_MANAGER_REVIEW`
