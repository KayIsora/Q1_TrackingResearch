# Stage 3B — HG6 mechanism-level novelty audit execution plan

**Date:** 2026-08-25  
**Status:** LOCKED BEFORE HG6 SEARCH  
**Prerequisite:** Stage 3A G1 and G2 reconciliations are complete.

## Purpose

HG6 determines whether each `GAP_READY` candidate retains a materially distinct algorithmic research opportunity after mechanism-level prior-art search.

This stage does not assign S1–S7, rank candidates, create a shortlist, select a baseline, or design the final proposed architecture.

## Entry pool

Only four candidates enter HG6:

1. CX007 — SpikeTrack
2. CX013 — FARTrack
3. CX044 — AsymTrack
4. CX058 — HiT-DyHiT

They are unranked.

## Batch order

Canonical-ID order is preserved.

### Novelty Batch N1

- CX007 — SpikeTrack
- CX013 — FARTrack

### Novelty Batch N2

- CX044 — AsymTrack
- CX058 — HiT-DyHiT

N2 does not start before N1 Manager↔Codex reconciliation.

## Independent lanes

### Manager lane

Focus:

- primary-source literature search;
- exact mechanism and claimed problem;
- same-mechanism versus adjacent-mechanism distinction;
- publication status and chronology;
- whether the candidate-specific coupling remains materially distinct;
- final HG6 scientific decision.

### Codex lane

Focus:

- exact implementation-derived query vocabulary;
- official paper/repository search and verification;
- mechanism comparison table;
- code-level overlap when official implementations exist;
- direct and indirect novelty adversaries;
- independent provisional HG6 decision.

Neither lane may read the other lane's N1/N2 HG6 artifact before committing its independent result.

## Search coverage

For every candidate, both lanes must cover:

1. tracker-name search;
2. exact mechanism phrases;
3. synonyms/recall queries;
4. robustness-problem queries;
5. adjacent-field mechanism queries;
6. cited and citing work where accessible;
7. arXiv-only 2025–2026 work;
8. peer-reviewed tracking work from 2023–2026;
9. older foundational prior art when the mechanism predates 2023.

Search is by mechanism, not tracker name alone.

## Evidence priority

1. official proceedings or journal page;
2. official paper PDF/supplement;
3. official preprint when no peer-reviewed version exists;
4. official repository/project page;
5. search snippets only as discovery leads.

Every source used in a final HG6 decision must be registered in `references/references.md` and `references/source_manifest.csv` before reconciliation.

## Comparison taxonomy

Each prior work is classified as:

- `DIRECT_COLLISION` — substantially the same mechanism, same claimed coupling and same tracking setting;
- `PARTIAL_COLLISION` — shares a major mechanism or one half of the coupling but leaves a material distinction;
- `ADJACENT_PRIOR_ART` — related mechanism in tracking or adjacent vision field, constraining novelty language;
- `NON_COLLIDING_REFERENCE` — relevant context but does not implement the candidate-specific mechanism.

A tracker cannot pass HG6 merely because no paper names that tracker.

## HG6 decisions

### PASS

The candidate-specific mechanism remains materially distinct after primary-source search. A PASS must state:

- exact surviving distinction;
- closest direct/partial adversaries;
- prohibited broad claims;
- minimum claim wording that may proceed to diagnostics.

### FAIL

Recent or foundational work substantially implements the same mechanism for the same claimed weakness, or the only surviving work is ordinary engineering/compression.

### PENDING

Coverage, source access or scientific gap evidence is insufficient. PENDING blocks scoring and shortlist progression.

## Candidate-specific N1 boundaries

### CX007 — SpikeTrack

Search the candidate-specific relationship among:

- frame-/condition-dependent MRM or memory-retrieval allocation;
- multi-scale/template retrieval selection;
- visually similar distractor discrimination;
- SNN dynamic timestep/depth/retrieval;
- conditional computation in spiking vision;
- distractor-aware compute allocation in tracking.

Broad claims that are already prohibited:

- generic SNN early exit;
- generic dynamic timestep;
- ordinary confidence gating;
- generic memory selection;
- adding a distractor head;
- quantization/export optimization.

The possible surviving distinction must involve condition-specific retrieval contribution under target–distractor ambiguity in a spike-driven tracker.

### CX013 — FARTrack

Search the candidate-specific relationship among:

- template validity and active template number;
- stale/invalid template suppression;
- physical template/token compute removal;
- robustness after occlusion/disappearance;
- reliability-aware template banks;
- memory contamination/corruption;
- multi-template adaptive computation;
- autoregressive tracker memory/template sparsification.

Broad claims that are already prohibited:

- generic template update gating;
- ordinary template selection;
- generic token pruning;
- confidence-based memory update;
- template caching;
- use fewer templates;
- identity/ReID recovery.

The possible surviving distinction must connect measurable template validity to both physical compute utility and robustness.

## Required artifact per candidate

### A. Reconciled gap statement

Restate the exact candidate-specific question without broadening it.

### B. Exact query log

Record:

- query string;
- source/database;
- date;
- candidate/mechanism family;
- result disposition.

### C. Prior-art table

For every serious adversary:

- title;
- year/venue/status;
- task/modality;
- mechanism;
- robustness target;
- efficiency target;
- relationship to candidate gap;
- collision class;
- primary source.

### D. Chronology

State whether the prior work predates, coincides with or follows the baseline paper.

### E. Surviving distinction or collision

Use narrow claim language.

### F. HG6 decision

PASS / FAIL / PENDING with evidence-based rationale.

### G. Diagnostic consequence

If PASS, state the minimum diagnostic evidence still required before any architecture design. If FAIL/PENDING, state why no scoring/shortlist progression is allowed.

## Stage artifacts

Manager N1:

`screening/manager/2026-08-25_stage3B_hg6_N1_manager.md`

Codex N1:

`screening/codex/2026-08-25_stage3B_hg6_N1_codex.md`

N1 reconciliation:

`screening/reconciliation/2026-08-25_stage3B_hg6_N1_reconciliation.md`

Equivalent N2 artifacts are created only after N1 reconciliation.

Independent query logs may be separate files when needed.

## Scoring guard

S1–S7 remain blank until all HG6 decisions are reconciled. No provisional points or ranking are allowed during novelty search.

## Locked state

- Stage 3A: COMPLETE
- Stage 3B N1: READY
- Stage 3B N2: LOCKED
- HG6 decisions: NOT STARTED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
