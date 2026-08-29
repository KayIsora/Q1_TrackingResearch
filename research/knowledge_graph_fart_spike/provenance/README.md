# Mechanical inventory provenance

This directory preserves the reproducible, metadata-only parse of the two fixed Connected Papers BibTeX exports. The final primary-source corrections and semantic graph are one level above; these files remain unchanged audit inputs.

## Files

- `parse_connected_papers.py`: standard-library parser, collision check, ordered deduplication, and screening annotations.
- `00_neuroscience_collision_check.json`: explicit check for the named neuroscience collision export.
- `01_raw_bib_inventory.csv`: 82 source records with source-file/sequence provenance and all supplied fields.
- `02_deduplicated_paper_inventory_draft.csv`: 75 mechanical clusters in the requested inventory shape plus audit columns.
- `03_manual_review_flags.csv`: unresolved record and possible-version checks.
- `04_inventory_summary.json`: counts, hashes, completeness, family incidence, and limitations.
- `05_candidate_knowledge_donors_draft.csv`: ten analyst-selected metadata candidates; not baselines and not graph edges.
- `06_inventory_analysis.md`: concise interpretation and handoff cautions.

## Reproduce

From PowerShell:

```powershell
python E:\Robot_Backup\Q1_TrackingResearch\research\knowledge_graph_fart_spike\provenance\parse_connected_papers.py
```

The script reads only the two fixed files under `E:\Robot_Backup\Tracker_Q1_Documents` and rewrites its generated CSV/JSON outputs in this directory. The two source SHA-256 values are recorded in `04_inventory_summary.json`.

## Status boundary

These metadata-only outputs do not create semantic graph edges or architectural claims. The final build resolves the LoReTrack preprint/publication pair, OiRT scope, and VideoTrack primary identity in `02_deduplicated_paper_inventory.csv` using evidence [E15, E25, E26].
