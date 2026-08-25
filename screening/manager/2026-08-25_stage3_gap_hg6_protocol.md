# Stage 3 — Candidate-specific research-gap formulation and HG6 novelty audit protocol

**Date:** 2026-08-25  
**Status:** LOCKED BEFORE HG6 SEARCH  
**Prerequisite:** Stage 2B targeted HG5 reconciliation is closed.

## 1. Purpose

Stage 3 determines whether each surviving tracker has a **specific research opportunity** that:

1. identifies a measurable computation site or allocation rule;
2. identifies a specific remaining robustness weakness;
3. gives a falsifiable reason those two may be structurally related;
4. survives a mechanism-level 2023–2026 novelty audit, including relevant arXiv-only work.

This stage does **not** select a baseline by familiarity, venue, benchmark score or desktop FPS. It does not yet design the final proposed architecture.

## 2. Entry pool

Only candidates with HG1–HG5 PASS enter Stage 3:

1. CX007 — SpikeTrack
2. CX009 — UETrack
3. CX010 — UTPTrack
4. CX013 — FARTrack
5. CX024 — DAM4SAM
6. CX037 — SSTrack-AAAI
7. CX038 — MCITrack
8. CX043 — SUTrack
9. CX044 — AsymTrack
10. CX058 — HiT-DyHiT

These ten candidates are **unranked** and are not a shortlist.

CX053 UncTrack remains HG5 PENDING and does not enter Stage 3. HG5 FAIL and HG3 FAIL/PENDING candidates remain reference/novelty-adversary material only.

## 3. Two-step structure

### Stage 3A — Research-gap formulation

No broad novelty decision is allowed yet.

For every candidate, Manager and Codex independently produce:

- **compute observation:** exact module/path/state that consumes computation;
- **robustness signal:** author limitation, benchmark attribute, failure evidence or explicit unresolved weakness;
- **coupling hypothesis:** falsifiable relationship between the compute observation and robustness signal;
- **minimum falsification experiment:** what result would reject the hypothesis;
- **mechanism vocabulary:** search terms needed for HG6;
- **direct novelty adversaries already known:** baseline’s own contributions and known recent methods that constrain the gap;
- **gap readiness status:** `GAP_READY`, `GAP_INCOMPLETE`, or `GAP_REJECTED`.

Definitions:

- `GAP_READY`: compute site, robustness signal and a falsifiable coupling question are all concrete enough for mechanism-level novelty search.
- `GAP_INCOMPLETE`: at least one required element is still missing or speculative; the candidate may require a bounded failure/reproduction experiment before HG6.
- `GAP_REJECTED`: the only visible opportunity is ordinary compression, engineering cleanup, or a mechanism already solved by the baseline itself.

A gap-readiness status is **not a soft score** and does not decide HG6.

### Stage 3B — HG6 mechanism-level novelty audit

Only `GAP_READY` candidates enter a full HG6 search. `GAP_INCOMPLETE` candidates remain held until the missing scientific evidence is obtained. `GAP_REJECTED` candidates remain reference-only.

HG6 search must cover:

- peer-reviewed 2023–2026 tracking work;
- relevant arXiv-only 2025–2026 work;
- older foundational prior art when the mechanism predates the screening window;
- adjacent fields when they implement the same mechanism, including efficient vision transformers, video memory, dynamic inference, SNN computation, state-space models and SAM-family memory systems.

Novelty is searched by **mechanism**, not by tracker name alone.

## 4. Independent lanes

### Manager lane

Focus:

- paper-level scientific claim and limitation;
- benchmark/attribute evidence;
- distinction between solved problem and residual weakness;
- scientific coupling hypothesis;
- mechanism-level literature search and source quality.

### Codex lane

Focus:

- code-visible execution site and frequency;
- tensor/state/template behavior;
- branch/control-flow boundaries;
- candidate-specific falsification instrumentation;
- exact mechanism vocabulary derived from implementation;
- official-repository evidence.

Neither lane may read the other lane’s Stage-3A candidate report before committing its independent artifact.

## 5. Batch order

Candidates are processed in canonical-ID order, not perceived promise.

### Gap Batch G1

- CX007 — SpikeTrack
- CX009 — UETrack
- CX010 — UTPTrack
- CX013 — FARTrack
- CX024 — DAM4SAM

### Gap Batch G2

- CX037 — SSTrack-AAAI
- CX038 — MCITrack
- CX043 — SUTrack
- CX044 — AsymTrack
- CX058 — HiT-DyHiT

G2 does not start before G1 Manager↔Codex gap reconciliation.

## 6. Required gap record

For each candidate:

### A. Candidate boundary

- exact variant/config that anchors the question;
- what scientific mechanism must remain intact;
- what may be changed without turning it into an unrelated new tracker.

### B. Compute observation

State only evidence-backed facts, for example:

- module executes every frame;
- token sequence remains dense despite masking;
- all experts execute;
- templates are re-encoded;
- state/history grows;
- a second full inference occurs in a condition.

Do not call a code site “redundant” before an experiment establishes unnecessary work.

### C. Robustness signal

Acceptable evidence:

- author-reported residual limitation;
- diagnostic benchmark/attribute gap;
- reproducible failure evidence;
- mechanism-specific source evidence.

Not acceptable:

- generic statements such as “occlusion is difficult”;
- a weakness already solved by the baseline’s principal contribution;
- speculation based only on module size.

### D. Coupling hypothesis

Use a falsifiable form:

> Under condition X, compute path Y is unnecessary or harmful; under condition Z, stronger/selective use of Y is required for robustness outcome W.

The hypothesis must be rejected if its predicted compute/robustness relation is not observed.

### E. Minimum tests

List the minimum controlled evidence needed before architecture design, such as:

- bypass/ablate one path by frame state;
- measure accuracy by challenge attribute;
- measure mode-specific latency;
- corrupt or filter memory/template inputs;
- compare fixed versus state-conditioned compute;
- inspect whether the same frames drive both added compute and failures.

These are diagnostic tests, not a proposed method.

### F. HG6 query vocabulary

Record exact mechanism terms, synonyms and adjacent-field terms. Queries must include both precision and recall families.

### G. Known collision boundary

State what cannot be claimed because the baseline or known work already does it.

## 7. HG6 decision

Allowed states: `PASS`, `FAIL`, `PENDING`.

### PASS

The candidate-specific intended mechanism remains materially distinct after primary-source novelty audit.

### FAIL

Recent work substantially implements the same mechanism for the same claimed weakness, or only standard compression/porting remains.

### PENDING

Gap evidence or literature coverage is insufficient. PENDING blocks soft scoring and shortlist status.

## 8. Source discipline

Scientific novelty facts require primary sources:

1. official proceedings/journal paper;
2. official preprint when peer-reviewed version is unavailable;
3. official repository for code behavior;
4. official supplementary material.

Search snippets, blogs, generated summaries and PapersWithCode may provide leads only.

Every source must be registered before it is used for a final HG6 decision.

## 9. No scoring yet

S1–S7 remain blank throughout Stage 3A and until HG6 is reconciled.

No candidate receives a provisional numerical score, rank or shortlist label during gap formulation.

## 10. Stage artifacts

Manager G1:

`screening/manager/2026-08-25_stage3_gap_G1_scientific_formulation.md`

Codex G1:

`screening/codex/2026-08-25_stage3_gap_G1_code_formulation.md`

G1 reconciliation:

`screening/reconciliation/2026-08-25_stage3_gap_G1_reconciliation.md`

Equivalent G2 artifacts are created only after G1 closes.

HG6 query logs and candidate reports are created after the corresponding gap statement is reconciled and marked `GAP_READY`.

## 11. Locked state

- Stage 2A: COMPLETE
- Stage 2B: COMPLETE
- Stage 3A G1: READY
- Stage 3B / HG6: NOT STARTED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
