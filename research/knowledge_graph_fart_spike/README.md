# FARTrack + SpikeTrack Knowledge Graph V1.1

This directory turns two Connected Papers literature neighborhoods into an evidence-backed semantic knowledge graph centered on two fixed anchors:

- FARTrack - lightweight/autoregressive design knowledge anchor;
- SpikeTrack - architecture redesign anchor.

**We are no longer searching for a third main tracker. Other trackers are knowledge donors.**

FARTrack is not discarded because it is already strong. Its successful lightweight-design methodology is retained as an important knowledge source for redesigning SpikeTrack.

## Inventory at a glance

- 41 FARTrack-neighborhood records + 41 SpikeTrack-neighborhood records;
- seven exact cross-graph overlaps;
- 75 mechanical clusters, then 74 deduplicated paper identities after reconciling LoReTrack’s preprint/proceedings versions;
- the Manager-inspected 41-record neuroscience collision export was intentionally excluded before visual-SOT corpus construction and contributed zero rows;
- one out-of-scope continual-classification record is retained only for provenance.

The 74 identities are divided into 14 primary-verified high-relevance records, 56 metadata-canonicalized records, and four verified arXiv/preprint-only records. Publication status has zero unresolved rows; missing code or DOI fields remain explicit rather than guessed.

## Reading order

1. `00_scope_and_method.md`
2. `02_deduplicated_paper_inventory.csv`
3. `03_solution_taxonomy.md`
4. `04_high_relevance_paper_cards.md`
5. `05_fartrack_architecture_and_principles.md`
6. `06_spiketrack_architecture_and_bottlenecks.md`
7. `07_transfer_matrix.csv`
8. `08_spiketrack_redesign_space.md`
9. `12a_methodology_flow_v1_1.mmd`
10. `12b_tracker_solution_knowledge_graph_v1_1.mmd`
11. `13_teacher_report_v1.md`
12. `15_canonical_metadata_audit_v1_1.csv`
13. `16_neuroscience_collision_exclusion_v1_1.md`
14. `REVIEW_REQUEST.md`

Machine-readable files are `09_nodes.csv`, `10_edges.csv`, and `11_knowledge_graph_v1.graphml`. `12a_methodology_flow_v1_1.mmd` is the workflow view; `12b_tracker_solution_knowledge_graph_v1_1.mmd` is the curated teacher-facing tracker/problem/mechanism/principle graph. Source details and claim limits are in `14_evidence_log.csv`.

`provenance/` preserves the exact mechanical parser, raw/draft inventories, collision check, hashes, and manual-review flags. `scripts/build_machine_artifacts.py` applies the documented primary-source corrections and regenerates the final deduplicated inventory and graph files.

## Boundary

The graph records evidence-derived semantic relationships. It does not reproduce Connected Papers similarity edges or weights. The redesign space contains testable hypotheses, not a selected final architecture. The failed conditional whole-MRM1 skip remains historical/null-result context only.

## Status

`KNOWLEDGE_GRAPH_V1_1_READY_FOR_MANAGER_REVIEW`
