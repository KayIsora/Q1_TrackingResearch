# Post-SpikeTrack lean execution plan

**Date:** 2026-08-29  
**Status:** `LOCKED`  
**Supersedes operationally:** the open-ended execution interpretation of `2026-08-28_post_spiketrack_fallback_protocol.md` while preserving its scientific gates.

## 1. Objective

The next cycle must identify **at most one** candidate that justifies a future full diagnostic program. It must not repeat the complete SpikeTrack pipeline for every reserve tracker.

The project retains the same scientific standard but introduces an explicit stop-loss structure:

```text
5 reserve candidates
    -> paper/code triage only
    -> at most 2 bounded mini-probes
    -> fast mechanism-level HG6 audit
    -> at most 1 full-diagnostic finalist
    -> soft scoring only after that finalist passes
```

The valid terminal result remains `NO SUITABLE BASELINE`.

## 2. Candidate pools

### Active reserve pool

- CX009 — UETrack;
- CX010 — UTPTrack;
- CX024 — DAM4SAM;
- CX037 — SSTrack-AAAI;
- CX038 — MCITrack.

### Evidence-gated pool

- CX046 — JDTrack (`HG3 PENDING`);
- CX051 — UMDATrack (`HG3 PENDING`);
- CX053 — UncTrack (`HG5 PENDING`).

Evidence-gated candidates do not enter this lean cycle unless their exact blocker changes.

## 3. Lean stages

### F0 — independent reserve triage

**Purpose:** desk-based paper/code/resource assessment only.

Allowed work:

- exact source/checkpoint/config/evaluator verification;
- code-path/state-site inspection;
- definition of one candidate-specific missing-evidence question;
- estimate of the cheapest inference-only probe;
- explicit falsification condition and novelty-collision risk.

Forbidden:

- model execution;
- dataset download;
- new experiment;
- `GAP_READY`, HG6, scoring, shortlist or baseline selection.

Allowed states:

- `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`;
- `TRIAGE_HOLD_MISSING_DATA_OR_RESOURCE`;
- `TRIAGE_REJECT_NO_ACTIONABLE_GAP`.

### F1 — Manager–Codex reconciliation

Reconcile evidence, not preferences. Select **at most two** candidates for F2.

A candidate may enter F2 only when all are true:

1. one concrete residual weakness of the final released tracker is defined;
2. one exact compute/state site is identified;
3. one inference-only causal control is technically feasible;
4. failure/control data can be predeclared without broad outcome mining;
5. no full retraining or new large dataset is required;
6. a positive result would still leave credible novelty and Nano paths.

If no candidate satisfies all six, stop and refresh the 2026 candidate universe/resources.

### F2 — bounded mini-probe

**Maximum candidates:** 2.  
**Purpose:** answer one missing-evidence question, not prove the full paper contribution.

Default per-candidate caps; exceeding any cap requires new Manager authorization before outcomes are viewed:

- no training or fine-tuning;
- no new large benchmark download;
- at most **6 predeclared sequences** or **1,500 unique evaluated frames**, whichever is reached first;
- at most **one baseline plus two candidate-specific causal controls**;
- one deterministic scientific run after smoke/parity checks;
- at most **6 GPU-hours/model-execution hours** on current hardware;
- at most one small instrumentation patch;
- no full benchmark, clean-room campaign, 20-pair slice, predictor training, physical deployment or Jetson run.

The mini-probe must lock before execution:

- exact data/sequence IDs;
- exact metric/effect direction;
- exact causal control(s);
- exact stop threshold;
- exact negative/inconclusive condition.

Allowed outcomes:

- `PROBE_POSITIVE_GAP_EVIDENCE`;
- `PROBE_NEGATIVE_REJECT_CURRENT_GAP`;
- `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`.

A positive result means only that the previously missing failure–mechanism interaction exists strongly enough to justify novelty review.

### F3 — fast mechanism-level HG6 audit

Run desk-based novelty audit only for F2-positive candidates.

Rules:

- search the surviving mechanism, not merely the tracker name;
- include direct, partial and adjacent collision sources;
- no new model experiment;
- no architecture design;
- if two candidates survive, choose at most one finalist using novelty headroom, effect credibility, RTX-3060 feasibility and Nano plausibility.

Allowed outputs:

- `HG6_FAIL_REFERENCE_ONLY`;
- `HG6_PASS_FULL_DIAGNOSTIC_FINALIST`.

### F4 — one-finalist full diagnostic

At most one candidate may enter. The diagnostic protocol is designed only after F3 and may reuse SpikeTrack governance/statistical infrastructure.

Do not automatically recreate all SpikeTrack stages. Use only the minimum discovery/hold-out structure needed by the finalist’s exact hypothesis.

### F5 — soft scoring and baseline decision

S1–S7 starts only after the single finalist passes its full diagnostic. A passing diagnostic does not automatically select the baseline.

## 4. Hard stop-loss rules

1. **Maximum two mini-probes in this cycle.**
2. **Maximum one mini-probe per candidate.** No second hypothesis after a scientific negative.
3. A technical restart is permitted only when failure occurs before any scientific outcome is produced and the zero-outcome boundary is documented.
4. No adding sequences, controls, features or ablations after results are viewed.
5. `PROBE_NEGATIVE` is terminal for that candidate’s current gap.
6. `PROBE_INCONCLUSIVE` returns the candidate to hold; it is not a soft pass.
7. No reserve candidate may receive a full Stage-4-style program before F2 and F3 both pass.
8. If both authorized mini-probes fail, stop and refresh the 2026 universe/resources rather than probing candidates 3–5 automatically.

## 5. Reuse from SpikeTrack

May reuse:

- provenance and hash discipline;
- exact-prefix/state-matched branching principles;
- frozen data/metric/threshold governance;
- bootstrap/statistical utilities where appropriate;
- one-shot hold-out discipline if a later finalist needs it;
- artifact manifests and stop-boundary reporting.

May not reuse:

- SpikeTrack hold-out outcomes for tuning;
- MRM-specific instrumentation or features as generic evidence;
- SpikeTrack predictor labels;
- the assumption that every candidate needs a 20-pair OTB clean-room package.

## 6. Reporting economy

Each lean stage should produce the minimum artifacts necessary for audit:

- F0: one Markdown report and one CSV;
- F1: one reconciliation file and one authorization table;
- F2: one protocol, one execution report, one result table, one bounded patch/script set;
- F3: one novelty audit and one decision file.

Do not create duplicate summaries or visual packages unless they are required to decide the gate.

## 7. Current locked state

- SpikeTrack: `DIAG_FAIL`, reference/null result only under the tested gap;
- active main-baseline candidate: **NONE**;
- F0 independent reserve triage: **READY**;
- F1 reconciliation: **LOCKED**;
- F2 bounded mini-probes: **LOCKED; maximum 2**;
- F3 fast HG6: **LOCKED**;
- F4 full-diagnostic finalist: **LOCKED; maximum 1**;
- S1–S7: **NOT STARTED**;
- primary shortlist: **NONE**;
- main baseline: **NONE**;
- proposed architecture: **NONE**.
