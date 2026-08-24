# Manager lane — Stage 1 discovery query log

**Screening date:** 2026-08-24  
**Status:** Stage 1 broad discovery in progress.  
**Governing files:** `RULE/01_EVIDENCE_AND_CITATION_POLICY.md`, `docs/11_systematic_screening_protocol.md`, `screening/00_parallel_screening_coordination.md`.

This file records discovery coverage only. It intentionally does not promote candidate facts, scores, shortlist decisions, or scientific claims. Candidate facts will be reconciled against primary/official sources before entering the canonical matrix.

## Search families executed by the manager lane

### Venue/year discovery

- `site:openaccess.thecvf.com/content/CVPR2025 visual tracking single object`
- `site:openaccess.thecvf.com/content/ICCV2025 visual tracking single object`
- `site:ojs.aaai.org 2025 visual tracking single object`
- `site:proceedings.neurips.cc 2025 visual tracking single object`
- `site:proceedings.mlr.press 2025 visual tracking single object`
- `site:openreview.net 2025 visual tracking single object ICLR`
- `site:openaccess.thecvf.com/content/CVPR2026 visual tracking tracker`
- `site:ojs.aaai.org 2026 visual tracking`
- `site:openreview.net 2026 visual tracking ICLR`
- `site:openaccess.thecvf.com/content/WACV2025 visual tracking tracker`
- `site:link.springer.com 2025 visual tracking efficient tracker IJCV`
- `site:sciencedirect.com 2025 visual tracking Pattern Recognition tracker`
- `site:sciencedirect.com 2026 visual tracking Pattern Recognition tracker`
- `site:ieeexplore.ieee.org 2025 visual object tracking efficient tracker`
- `site:ieeexplore.ieee.org 2026 visual object tracking tracker`

### Benchmark-anchored recall queries

- `2025 visual tracking GOT-10k TrackingNet LaSOT`
- `2026 visual tracking GOT-10k TrackingNet LaSOT`
- `2025 single object tracking LaSOT GOT-10k`
- `2026 single object tracking LaSOT GOT-10k`

### Mechanism-family recall queries

- `efficient lightweight visual tracking 2025 2026`
- `dynamic adaptive computation visual tracking 2025 2026`
- `token pruning token compression visual tracking 2025 2026`
- `memory template efficient visual tracking 2025 2026`
- `long-term temporal visual tracking 2025 2026`
- `autoregressive visual tracking 2025 2026`
- `Mamba state space visual tracking 2025 2026`
- `occlusion distractor reliability visual tracking 2025 2026`

### Official-asset verification queries begun

- exact-title / method-name + `official github`
- exact-title / method-name + official venue page
- exact-title / method-name + checkpoint/evaluation/model zoo terms

## Discovery handling

- Search results are discovery leads only until verified against primary/official sources.
- Method variants are deduplicated by paper/family.
- HG1/HG2/HG3 are the only gates considered during early Stage 2.
- HG4/HG5/HG6 remain `PENDING` unless enough direct evidence exists; no final gate decision is inferred from model size, reported desktop FPS, or paper abstract alone.
- No soft score is assigned during broad discovery.
- Ineligible modality/task papers may be retained as novelty/reference material rather than silently discarded.

## Next manager-lane action

Finish method-family deduplication and early HG1/HG2/HG3 verification, then produce a provisional scientific-audit queue for later reconciliation with the independent Codex lane. This is not a shortlist.
