# F1 — lean reserve-triage reconciliation

**Date:** 2026-08-29  
**Status:** `F1_COMPLETE_TWO_F2_PROBES_AUTHORIZED`  
**Inputs:** Manager independent triage, Codex F0 report/CSV at commit `9241e6cd58062a73f8cbf6ee3663a24d99981a7d`, and the locked lean execution plan.

## Boundary

This reconciliation selects at most two candidates for bounded F2 mini-probes. It does not assign `GAP_READY`, begin HG6, score or rank candidates, form a shortlist, select a main baseline, or design an architecture.

## 1. F0 process acceptance

Codex blindness was preserved. The CX007 canonical row was synchronized correctly: HG1–HG6 remain unchanged, all score fields remain blank, and SpikeTrack is reference/null-result only under the failed tested gap.

No model was run, no dataset/checkpoint was downloaded, and exactly five reserve candidates were triaged.

## 2. Candidate reconciliation

### CX009 — UETrack

- Manager provisional state: `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`.
- Codex state: `TRIAGE_HOLD_MISSING_DATA_OR_RESOURCE`.
- Final F1 state: **HOLD**.

The compute site is exact—dense eight-expert TP-MoE—but the exact tracker artifact/evaluator startup and, more importantly, a candidate-specific final RGB failure slice are not sealed. A generic challenge slice would risk converting the paper's training motivation into an assumed residual weakness. UETrack is not authorized in this cycle.

### CX010 — UTPTrack

- Manager state: `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`.
- Codex state: `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`.
- Final F1 state: **AUTHORIZED F2-A**.

The released model exposes exact physical pruning identities, the official checkpoint contract is strong, a same-cardinality target-token rescue is a causal inference-only control rather than another keep-ratio sweep, and the estimated execution cost is far below the F2 cap. Positive evidence would still require HG6 because adaptive token pruning is collision-prone.

### CX024 — DAM4SAM

- Manager state: `TRIAGE_HOLD_MISSING_DATA_OR_RESOURCE`.
- Codex state: `TRIAGE_HOLD_MISSING_DATA_OR_RESOURCE`.
- Final F1 state: **HOLD**.

The exact annotated failure/evaluator/initialization contract and DAM-only cost remain unresolved, while the pinned Hiera-L host makes the six-hour resource bound uncertain. No probe is authorized.

### CX037 — SSTrack-AAAI

- Manager state: `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`.
- Codex state: `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`.
- Final F1 state: **READY BUT NOT SELECTED THIS CYCLE**.

The template-history control is feasible, but expected information value is lower than the selected probes: historical-template validity, reliability gating and template selection are already crowded and substantially overlap the FARTrack novelty-collision boundary. SSTrack remains a reserve candidate; it is not rejected and may not be probed automatically if either selected probe fails.

### CX038 — MCITrack

- Manager state: `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`.
- Codex state: `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`.
- Final F1 state: **AUTHORIZED F2-B**.

Four explicit carried states provide exact causal intervention points. Zero-state and stale-state controls can isolate contextual-state utility while retaining the five-template path. Same-sequence source-selected ambiguity/control intervals already exist, keeping the probe small and reducing cross-scene confounding. Positive evidence would still face Mamba/state-gating novelty audit.

## 3. Authorized probes

Exactly two F2 probes are authorized:

1. **F2-A — UTPTrack:** same-cardinality target-token rescue versus deterministic non-target swap on six predeclared OTB source intervals.
2. **F2-B — MCITrack:** released carried state versus zero-state and stale-state controls on six predeclared same-sequence OTB primary/control pairs.

The two probes may run in separate fresh Codex windows. They are independent and neither is ranked above the other.

## 4. Stop-loss enforcement

For each candidate:

- no training/fine-tuning;
- no new dataset download;
- at most six source sequences and fewer than 1,500 evaluated frames;
- one baseline plus at most two controls;
- one deterministic scientific execution after smoke/parity;
- at most six model-execution hours;
- one small patch;
- no full benchmark, predictor training, clean-room campaign, Jetson run or architecture design.

A scientific negative is terminal for that candidate's current gap. A technical failure before any outcome may produce `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`; no outcome-dependent repair is permitted.

## 5. Downstream rule

- If both probes are negative: stop and refresh the 2026 candidate universe/resources.
- If one or both are positive: run F3 mechanism-level HG6 only for positive candidates and nominate at most one full-diagnostic finalist.
- SSTrack is not automatically substituted after a negative result.

## Locked state

- F0: **COMPLETE**;
- F1: **COMPLETE**;
- F2-A UTPTrack: **AUTHORIZED / READY**;
- F2-B MCITrack: **AUTHORIZED / READY**;
- authorized mini-probes: **2 of 2 maximum**;
- F3 HG6: **LOCKED**;
- full-diagnostic finalist: **NONE**;
- S1–S7: **NOT STARTED**;
- primary shortlist: **NONE**;
- main baseline: **NONE**;
- proposed architecture: **NONE**.
