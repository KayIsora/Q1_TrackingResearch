# FARTrack + SpikeTrack Knowledge Graph — V1.1 base + V1.2 content audit

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

## V1.1 base reading order

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

## V1.2 drawing-content supplement

The V1.2 supplement does **not** redraw or replace the V1.1 machine graph. It prepares defensible content for the user's later manual drawing:

1. `17_cross_neighborhood_overlap_audit.md` — seven exact co-memberships classified by semantic function;
2. `18_donor_mechanism_audit_v1_2.md` — ABTrack, UETrack, ZoomTrack, and P027 HKDT mechanism audits;
3. `19_presentation_role_catalog.csv` — one primary role for each of 19 audited papers and the 17-node recommendation;
4. `20_drawing_node_content_v1_2.md` — concise callout text for visible nodes;
5. `21_drawing_edge_catalog_v1_2.csv` — defensible semantic edges only;
6. `22_fartrack_principle_spiketrack_analogy_v1_2.md` — strict component → principle → functional-analogue table;
7. `23_primary_lane_novelty_collision_audit_v1_2.md` — direct prior-art collision and residual novelty question;
8. `24_final_content_scope_for_drawing_v1_2.md` — final eight-branch taxonomy and drawing scope;
9. `REVIEW_REQUEST_V1_2.md` — Manager decision boundary and unresolved evidence.

`04_high_relevance_paper_cards.md` now normalizes all 15 prior cards plus the four mandatory additions into the same 22 drawing-ready fields. `14_evidence_log.csv` adds primary sources E29-E35. The raw 82-record inventory, 74-identity corpus, V1.1 nodes/edges/GraphML, and original Connected Papers exports are unchanged.

Machine-readable files are `09_nodes.csv`, `10_edges.csv`, and `11_knowledge_graph_v1.graphml`. `12a_methodology_flow_v1_1.mmd` is the workflow view; `12b_tracker_solution_knowledge_graph_v1_1.mmd` is the curated teacher-facing tracker/problem/mechanism/principle graph. Source details and claim limits are in `14_evidence_log.csv`.

`provenance/` preserves the exact mechanical parser, raw/draft inventories, collision check, hashes, and manual-review flags. `scripts/build_machine_artifacts.py` applies the documented primary-source corrections and regenerates the final deduplicated inventory and graph files.

## Boundary

The graph records evidence-derived semantic relationships. It does not reproduce Connected Papers similarity edges or weights. Cross-neighborhood co-membership is not treated as a semantic bridge without a functional mechanism. The redesign space contains testable hypotheses, not a selected final architecture. The failed conditional whole-MRM1 skip remains `DIAG_FAIL`; its hold-out is consumed and was not reused.

## Status

Accepted base: `KNOWLEDGE_GRAPH_V1_1_READY_FOR_MANAGER_REVIEW`

Accepted content audit: `KNOWLEDGE_GRAPH_CONTENT_AUDIT_V1_2_READY_FOR_MANAGER_REVIEW`

Current source-integrity repair: `KNOWLEDGE_GRAPH_CONTENT_V1_2_1_SOURCE_INTEGRITY_READY_FOR_MANAGER_REVIEW`
