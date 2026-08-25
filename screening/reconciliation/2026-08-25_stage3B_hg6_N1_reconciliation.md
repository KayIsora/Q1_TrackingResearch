# Stage 3B — HG6 Novelty Batch N1 final reconciliation

**Date:** 2026-08-25  
**Status:** N1 CLOSED; N2 may begin.  
**Inputs:**

- `screening/manager/2026-08-25_stage3B_hg6_N1_manager.md`
- `screening/codex/2026-08-25_stage3B_hg6_N1_codex.md`
- `screening/codex/2026-08-25_stage3B_hg6_N1_source_registration_report.md`
- canonical sources R52–R65, together with the already registered baseline and comparison sources.

**Governing plan:** `screening/manager/2026-08-25_stage3B_hg6_execution_plan.md`.

## Boundary

This reconciliation makes the final project HG6 decision for N1 only. It does not assign S1–S7, rank candidates, create a shortlist, select a baseline, authorize architecture design, or claim that any untested hypothesis is true.

Manager and Codex independently reached the same provisional decisions. Canonical source registration is complete with no flags. The final decisions therefore rest on primary-source evidence agreement rather than voting or familiarity.

---

## CX007 — SpikeTrack

**Final HG6: PASS**

### Exact surviving question

The anchor is SpikeTrack-S256-T1, with T3 retained only as a controlled temporal/template comparison. The candidate-specific question is:

> Does target–distractor ambiguity predict the marginal utility of identifiable SpikeTrack MRM scale and template/time retrieval paths, such that real retrieval execution can be reduced on unambiguous frames while preserving or strengthening target–distractor discrimination on ambiguous frames?

### Closest prior art and collision boundary

- SEENN establishes input-conditioned SNN timestep/early-exit policies [R52].
- STATA establishes physical token sparsification in a spiking Transformer [R53].
- Spiking Transformer with Experts Mixture establishes conditional sparse expert computation in SNNs [R54].
- TP-Spikformer establishes spatiotemporal token pruning/block stopping in a spiking-transformer family with tracking coverage [R55].
- ARTrack-AC establishes difficulty-conditioned low/high capacity in visual tracking [R56].
- RFGM establishes search-conditioned retrieval of relevant historical reference information with redundancy/compute control [R57].
- HiT-DyHiT establishes easy/hard routing and early exit in RGB SOT [R49/R50].
- DAM4SAM constrains distractor-aware memory claims [R29/R30].

These sources cumulatively prohibit broad claims about first adaptive SNN inference, first dynamic timestep/depth, first spiking-token pruning, first dynamic tracker capacity, first search-conditioned memory retrieval, first easy/hard route, or first distractor-aware tracking.

### Surviving distinction

No registered primary source tests the specific interaction among all of:

1. a spike-driven RGB bbox-SOT tracker;
2. the six identifiable SpikeTrack MRMs and T1/T3 retrieval structure;
3. an outcome-independent target–distractor ambiguity condition;
4. marginal contribution of individual MRM scale/template paths;
5. physical non-execution of retrieval work;
6. the same-frame relationship between saved compute and target–competitor separation.

The surviving distinction is therefore narrow and candidate-specific. It is not generic dynamic routing.

### Permitted claim language

Subject to future diagnostics, the project may investigate:

> ambiguity-conditioned MRM retrieval contribution in SpikeTrack, jointly measuring physical retrieval computation and target–distractor discrimination.

The project may not claim any of the prohibited broad firsts listed above.

### Diagnostic requirement before architecture design

HG6 PASS is literature clearance only. SpikeTrack cannot progress directly to architecture design. The project must first establish:

- a reproducible similar-object/distractor failure slice;
- predeclared ambiguity measurement independent of final failure labels;
- per-MRM and T1/T3 marginal contribution under identical frames/checkpoints;
- a statistically meaningful ambiguity × retrieval-path interaction;
- held-out prediction of retrieval utility;
- real path non-execution and measured latency/operation benefit;
- condition-specific accuracy preservation or improvement.

If the interaction is not observed, the research gap is falsified despite HG6 PASS.

---

## CX013 — FARTrack

**Final HG6: FAIL**

### Exact audited question

The audited question was whether measurable template validity could jointly determine physical template/token compute utility and robustness after occlusion/disappearance, so invalid or redundant templates would be physically removed rather than merely masked or retained.

### Cumulative collision

No single source necessarily reproduces every word of that sentence inside FARTrack. However the scientific mechanism is cumulatively occupied:

- ATPTrack physically prunes dynamic-template and search-region tokens for robustness and compute [R58].
- LMTrack retains high-quality autoregressive reference tokens and removes outdated/background/redundant tokens [R59].
- UTPTrack physically prunes static-, dynamic-template and search tokens [R22/R23].
- STDTrack uses quality-based reliable spatiotemporal memory maintenance and physical eviction [R60].
- DTPTrack calibrates per-frame temporal reliability and synthesizes compact priors [R61].
- ETCTrack directly couples historical-template token compression with efficiency and discriminative representation quality [R62].
- BackTrack explicitly validates candidate-template quality and rejects unreliable updates [R63].
- UncTrack covers uncertainty/reliability-aware memory and template control [R47/R48].
- DAM4SAM covers distractor-aware memory/introspection and quality-based admission [R29/R30].
- QDMN and RMem provide adjacent quality-aware frame admission/eviction and restricted-memory prior art [R64/R65].
- ARTrack-AC already provides adaptive capacity in an autoregressive tracking setting [R56].

### Why the residual distinction is insufficient

The remaining wording would place known validity/reliability estimation and known physical pruning earlier—at whole-template, pre-embedding granularity—inside FARTrack. That may produce useful engineering savings, but it is primarily a placement/granularity specialization and ordinary combination of established mechanisms.

Changing `token importance` to `template validity`, switching from token-level to whole-template-level removal, or specializing the combination to FARTrack does not create a sufficiently material algorithmic distinction under the project's Q1-oriented gate.

An explicit target-absence state, identity verification, ReID or re-entry recovery would belong to the later long-term target-person extension and does not rescue this generic Core claim.

### Consequence

FARTrack does not progress to S1–S7 scoring or shortlist consideration under this gap. It remains valuable as:

- a lightweight/autoregressive reference;
- a comparison tracker;
- a source of IFAS/TSSD design lessons;
- novelty adversary material;
- a possible later target-person extension host.

Reopening requires a qualitatively different causal variable not reducible to known confidence, uncertainty, template quality/quantity, temporal reliability, token importance, memory admission/eviction or distractor-aware memory.

---

## N1 outcome

| Candidate | Final HG6 | Progression |
|---|---:|---|
| CX007 SpikeTrack | **PASS** | eligible for later diagnostics and, only if those succeed, soft scoring |
| CX013 FARTrack | **FAIL** | excluded from main-baseline progression; reference only |

These two rows are not a shortlist and are not ranked.

## N2 activation

Novelty Batch N2 is now activated in canonical order:

1. CX044 — AsymTrack
2. CX058 — HiT-DyHiT

N2 must use independent Manager and Codex lanes, primary-source registration and reconciliation before any S1–S7 scoring.

## Locked state

- Stage 3B N1: **COMPLETE**
- CX007 SpikeTrack HG6: **PASS**
- CX013 FARTrack HG6: **FAIL**
- Stage 3B N2: **ACTIVE**
- S1–S7: **NOT STARTED**
- primary shortlist: **NONE**
- main baseline: **NONE**
- proposed architecture: **NONE**
