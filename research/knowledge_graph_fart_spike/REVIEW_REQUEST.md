# Manager review request — Knowledge Graph V1.1

## Requested decision

Review the desk-only repair at `KNOWLEDGE_GRAPH_V1_1_READY_FOR_MANAGER_REVIEW`. No experiment was run, no third baseline was selected, and no final SpikeTrack architecture was selected.

## Repair completed

- preserved `01_connected_papers_inventory.csv` byte-for-byte;
- retained the reproducible 82 raw -> 75 mechanical clusters -> 74 deduplicated identities path;
- replaced venue-string publication inference with a 74-row official-source/DOI/arXiv audit [E27];
- corrected the seven Manager-named errors and additional systematic year/title/venue cases found by the same audit;
- recorded the 41-record neuroscience export as `MANAGER_VERIFIED_EXTERNAL_EXCLUSION`, contributing zero visual-SOT rows [E28];
- separated the methodology flow from the curated teacher-facing tracker solution graph;
- added the Manager priority layer: P01+P02 primary family, P04 supporting donor, P06 engineering enablement, P03/P05/P09 secondary, and P07/P08/P10 plus generic dynamic routes deferred;
- retained the whole-MRM1 `DIAG_FAIL` and consumed-hold-out boundary [E08].

## Inventory and graph

| Measure | Count |
|---|---:|
| FARTrack raw records | 41 |
| SpikeTrack raw records | 41 |
| Deduplicated identities | 74 |
| Publication status | 38 conference; 32 journal; 4 arXiv/preprint only; 0 accepted/online-first; 0 unclear |
| Metadata tiers | 14 primary-verified high-relevance; 56 metadata-canonicalized; 4 arXiv-only verified |
| Machine graph | 128 nodes; 322 edges |
| Neuroscience collision contribution | 0 rows; 0 nodes; 0 edges |

The teacher-facing graph is `12b_tracker_solution_knowledge_graph_v1_1.mmd`; the complete graph remains `11_knowledge_graph_v1.graphml`.

## Remaining blockers

- no Jetson Nano latency, power, thermal, memory, or energy measurements;
- no successful ONNX/TensorRT export parity result;
- no sparse-spike kernel evaluation on conventional edge GPUs;
- unresolved FARTrack paper/public-code parity questions;
- no trained evidence for any SpikeTrack structural change.

These are deliberately outside this repair. There are zero unresolved publication-status rows, although unavailable DOI/code fields remain explicitly `UNKNOWN`.

`KNOWLEDGE_GRAPH_V1_1_READY_FOR_MANAGER_REVIEW`
