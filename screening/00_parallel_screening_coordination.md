# Parallel systematic-screening coordination

**Status:** PROJECT DECISION — execution coordination only.  
**Date:** 2026-08-24.  
**Governing protocol:** `docs/11_systematic_screening_protocol.md`.

## Purpose

User + ChatGPT (research managers) and Codex (worker) will run the 2025–2026 systematic screening in parallel. The parallel run is intended to improve recall and provide an independent cross-check; it does **not** create two different screening protocols.

All lanes must use the same locked hard gates, score definitions, task/modality boundaries, evidence taxonomy, and screening date. No lane may modify the locked protocol during discovery.

## Write isolation

To prevent merge conflicts and premature consensus:

- **Manager lane** writes provisional working material only under `screening/manager/`.
- **Codex lane** writes provisional working material only under `screening/codex/`.
- Neither lane edits `screening/candidate_screening_matrix.csv` during independent Stage 1 discovery unless explicitly instructed after reconciliation.
- Neither lane changes `docs/11_systematic_screening_protocol.md`, screening weights, scope locks, or baseline decision.

## Required independent stages

Each lane must independently perform:

1. Stage 1 broad candidate discovery using multiple query families;
2. method-family deduplication;
3. early HG1/HG2/HG3 evidence checks;
4. record HG4/HG5/HG6 as `PENDING` when evidence is not yet sufficient;
5. identify a **scientific-audit queue**, not a final shortlist.

No soft scoring is performed merely from abstracts/search snippets. Soft scores begin only after the candidate survives the appropriate early hard-gate checks and sufficient evidence is extracted.

## Reconciliation gate

After both lanes finish their independent discovery:

1. union the candidate universes;
2. deduplicate method families;
3. reconcile disagreements using primary/official sources;
4. add verified sources to `references/references.md` and `references/source_manifest.csv` before committing scientific facts;
5. only then update the canonical `screening/candidate_screening_matrix.csv`;
6. proceed to deeper HG4/HG5/HG6 audit and soft scoring under the locked protocol.

## Current non-claims

- No main baseline is selected.
- No candidate is shortlisted merely because one lane flags it as promising.
- No proposed architecture is approved.
- No Jetson Nano performance is inferred from other hardware.
- Discovery frequency or familiarity is not evidence of scientific quality.
