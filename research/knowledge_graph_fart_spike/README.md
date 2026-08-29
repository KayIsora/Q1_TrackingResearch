# FARTrack + SpikeTrack Knowledge Graph V1

This directory turns two Connected Papers literature neighborhoods into an evidence-backed semantic knowledge graph centered on two fixed anchors:

- FARTrack - lightweight/autoregressive design knowledge anchor;
- SpikeTrack - architecture redesign anchor.

**We are no longer searching for a third main tracker. Other trackers are knowledge donors.**

FARTrack is not discarded because it is already strong. Its successful lightweight-design methodology is retained as an important knowledge source for redesigning SpikeTrack.

## Inventory at a glance

- 41 FARTrack-neighborhood records + 41 SpikeTrack-neighborhood records;
- seven exact cross-graph overlaps;
- 75 mechanical clusters, then 74 papers after primary verification merged LoReTrack’s preprint/proceedings versions;
- the named neuroscience collision export was absent and contributed zero rows;
- one out-of-scope continual-classification record is retained only for provenance.

## Reading order

1. `00_scope_and_method.md`
2. `02_deduplicated_paper_inventory.csv`
3. `03_solution_taxonomy.md`
4. `04_high_relevance_paper_cards.md`
5. `05_fartrack_architecture_and_principles.md`
6. `06_spiketrack_architecture_and_bottlenecks.md`
7. `07_transfer_matrix.csv`
8. `08_spiketrack_redesign_space.md`
9. `13_teacher_report_v1.md`
10. `REVIEW_REQUEST.md`

Machine-readable files are `09_nodes.csv`, `10_edges.csv`, and `11_knowledge_graph_v1.graphml`. `12_knowledge_graph_v1.mmd` is the intentionally compact, high-level Mermaid view. Source details and claim limits are in `14_evidence_log.csv`.

`provenance/` preserves the exact mechanical parser, raw/draft inventories, collision check, hashes, and manual-review flags. `scripts/build_machine_artifacts.py` applies the documented primary-source corrections and regenerates the final deduplicated inventory and graph files.

## Boundary

The graph records evidence-derived semantic relationships. It does not reproduce Connected Papers similarity edges or weights. The redesign space contains testable hypotheses, not a selected final architecture. The failed conditional whole-MRM1 skip remains historical/null-result context only.

## Status

`KNOWLEDGE_GRAPH_V1_READY_FOR_MANAGER_REVIEW`
