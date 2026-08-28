# Post-SpikeTrack fallback protocol — reserve-gap triage before any new main-baseline attempt

**Date:** 2026-08-28  
**Status:** LOCKED AFTER `DIAG_FAIL`  
**Prerequisite:** `screening/reconciliation/2026-08-28_stage4C2_final_diagnostic_reconciliation.md`

## 1. Purpose

The first full diagnostic program ended with a valid null result: SpikeTrack passed A, B and C but failed the frozen one-shot Criterion D. The project therefore has no active main-baseline candidate.

This fallback protocol prevents two invalid reactions:

1. selecting SpikeTrack anyway because it was the last candidate standing;
2. immediately promoting the next familiar tracker without re-establishing a researchable gap.

The next cycle begins with bounded triage, not soft scoring or architecture design.

## 2. Candidate pools

### Pool R — `GAP_INCOMPLETE`, eligible for bounded missing-evidence probes

- CX009 — UETrack;
- CX010 — UTPTrack;
- CX024 — DAM4SAM;
- CX037 — SSTrack-AAAI;
- CX038 — MCITrack.

These candidates passed HG1–HG5 but did not establish a sufficiently evidenced residual robustness weakness coupled to a compute mechanism.

### Pool E — blocked by an earlier evidence gate

- CX046 — JDTrack (`HG3 PENDING`);
- CX051 — UMDATrack (`HG3 PENDING`);
- CX053 — UncTrack (`HG5 PENDING`).

They may re-enter only if the exact resource/export blocker changes. They are not substitutes for Pool-R diagnostics.

### Pool U — universe refresh

A later refresh may add newly accepted/published 2026 trackers or official resource releases. ArXiv-only work remains novelty/reference evidence, not a main baseline.

## 3. Triage question

For each Pool-R candidate, ask:

> Can a bounded, low-cost, falsifiable diagnostic establish both a residual failure signal and a candidate-specific compute/state mechanism before the project commits to another full Stage-4 program?

A candidate must not progress merely because code is available or a module looks expensive.

## 4. Required triage record

For every Pool-R candidate record:

- exact official source/ref/checkpoint/config;
- exact compute/state site;
- exact unresolved robustness claim;
- cheapest outcome-independent failure slice or official attribute source;
- exact inference-only ablation needed;
- whether state-matched forking is feasible;
- approximate execution cost on current hardware;
- data/resource requirement;
- likely novelty adversaries;
- explicit falsification condition;
- whether a positive result could still lead to a credible Nano path.

## 5. Candidate-specific missing-evidence contracts

### CX009 — UETrack

Must establish:

- a residual generic-RGB failure slice in the final tracker;
- expert/path contribution heterogeneity rather than only dense all-expert compute;
- a plausible condition signal available before expensive expert execution.

A static observation that every expert executes is insufficient.

### CX010 — UTPTrack

Must establish:

- a final-model robustness failure linked to fixed token-pruning policy;
- evidence that removed/retained token identity predicts the failure;
- a mechanism beyond generic dynamic token pruning already covered by recent work.

A lower keep rate or fixed-resolution comparison is insufficient.

### CX024 — DAM4SAM

Must establish:

- a residual distractor/memory failure after DAM is enabled;
- measurable DAM-specific compute or memory cost;
- a generic-RGB tracking formulation that remains meaningful for the Core paper;
- novelty space beyond known distractor-aware memory admission and lighter SAM hosts.

Training-free status does not remove the need for a new algorithmic gap.

### CX037 — SSTrack-AAAI

Must establish:

- template-history or candidate-elimination behavior that predicts final tracking error;
- source-frame validity/utility of selected historical templates;
- a condition-specific compute opportunity not reducible to generic template gating or token elimination.

Self-supervised performance gap alone is not the mechanism-specific weakness.

### CX038 — MCITrack

Must establish:

- a reproducible state-related failure in the released final tracker;
- causal influence of zero/stale/per-layer contextual state;
- separation of contextual-state effects from five-template encoding cost;
- a bounded state/compute mechanism with credible deployment relevance.

State size alone is not a robustness contribution.

## 6. Triage decisions

Allowed states:

- `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`;
- `TRIAGE_HOLD_MISSING_DATA_OR_RESOURCE`;
- `TRIAGE_REJECT_NO_ACTIONABLE_GAP`.

No candidate may receive `GAP_READY`, HG6 PASS, a soft score or shortlist status during triage.

## 7. Progression rule

After independent Manager and Codex triage:

1. reconcile exact missing-evidence contracts;
2. select at most two candidates for bounded diagnostics;
3. lock data, metrics, ablations and rejection thresholds before execution;
4. promote to `GAP_READY` only after the missing evidence is actually observed;
5. run a fresh mechanism-level HG6 audit before any full diagnostic program.

If no Pool-R candidate is triage-ready, perform a candidate-universe/resource refresh rather than lowering the scientific gate.

## 8. Stop-loss rule

A bounded triage diagnostic should normally require:

- no full retraining;
- no new large benchmark download unless approved;
- no more than a small number of official sequences/attributes;
- inference-only hooks/ablations first;
- an explicit stop after the predeclared question is answered.

The project must not repeat a full multi-stage diagnostic pipeline without first demonstrating a credible failure–mechanism interaction.

## 9. Locked non-claims

- SpikeTrack is not the main baseline.
- The reserve pool is not a shortlist.
- A triage-ready candidate is not selected.
- No S1–S7 score is assigned.
- No proposed architecture is authorized.
- The SpikeTrack hold-out may not be reused to tune a new SpikeTrack predictor.

## 10. Next artifacts

Codex independent triage report:

`screening/codex/2026-08-28_post_spiketrack_reserve_triage.md`

Codex machine-readable table:

`screening/codex/2026-08-28_post_spiketrack_reserve_triage.csv`

Manager independent triage and reconciliation follow before any execution authorization.

## Locked state

- active main-baseline candidate: **NONE**;
- reserve candidates under triage: **5**;
- evidence-gated candidates: **3**;
- soft scoring: **NOT STARTED**;
- primary shortlist: **NONE**;
- main baseline: **NONE**;
- proposed architecture: **NONE**.
