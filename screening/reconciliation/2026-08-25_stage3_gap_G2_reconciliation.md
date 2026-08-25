# Stage 3A — Gap Batch G2 reconciliation

**Date:** 2026-08-25  
**Status:** G2 RECONCILED; Stage 3A gap formulation is complete.  
**Inputs:**

- `screening/manager/2026-08-25_stage3_gap_G2_scientific_formulation.md`
- `screening/codex/2026-08-25_stage3_gap_G2_code_formulation.md`

**Governing protocol:** `screening/manager/2026-08-25_stage3_gap_hg6_protocol.md`.

## Boundary

This reconciliation decides only **gap readiness** for G2. It does not decide HG6, assign S1–S7, rank candidates, create a shortlist, select a main baseline, or approve a proposed architecture.

Manager and Codex independently reached the same state for all five candidates. The final status is therefore based on evidence agreement, not voting.

---

## CX037 — SSTrack-AAAI

**Final status: GAP_INCOMPLETE**

### Reconciled evidence

- Every selected raw template is embedded each frame; mature execution can use multiple historical templates.
- Candidate elimination physically reduces search tokens only after attention at the scheduled blocks.
- The persistent one-token query is bounded, while the raw history controller can grow with sequence length.
- The self-supervised training branches do not add a separate inference network.

No qualifying SSTrack-specific residual robustness weakness is established. Unconditional self-predicted-template admission is a concrete reliability lead, but code behavior alone does not prove that contaminated history or candidate elimination causes final-model failures. The broad gap to supervised tracking is not an acceptable mechanism-specific signal.

### Missing evidence before HG6

- source-frame validity and utility of selected historical templates;
- retained/removed-token identity on candidate-specific failure slices;
- initial-only versus multi-template and keep-rate controls;
- evidence that template/CE/query behavior predicts both compute utility and tracking outcome.

The candidate remains held for bounded diagnostics rather than HG6 search.

---

## CX038 — MCITrack

**Final status: GAP_INCOMPLETE**

### Reconciled evidence

- Four Mamba blocks, four Injectors, six Extractors, and all configured contextual slices execute each frame.
- Five raw templates are re-encoded each frame.
- Four fixed-size hidden states total about 49 MiB FP32 for B224 and are reset after low confidence.
- The confidence reset and template admission are baseline safeguards, not evidence of a residual failure.

No accepted residual state-related robustness weakness of final MCITrack is established. The paper's training-cost limitation and configuration ablations do not prove state contamination or condition-specific harm in the released tracker.

### Missing evidence before HG6

- zero/stale/per-layer-state ablations;
- frame-level relation among state contribution, reset events and tracking error;
- a reproduced disruption condition where earlier valid context is useful or harmful;
- separation of contextual-state effects from five-template cost.

The candidate remains held for bounded state/failure diagnostics.

---

## CX043 — SUTrack

**Final status: GAP_REJECTED**

### Reconciled evidence

Visible RGB-path opportunities are:

- duplicated RGB six-channel construction;
- one zero-text CLIP token and resident CLIP object;
- inference-unused task head;
- static-template re-encoding;
- RGB specialization, exporter cleanup and ordinary compression.

No candidate-specific residual RGB robustness weakness is established, and no evidence connects the visible compute cleanup to a robustness outcome. The unified training/representation problem is already the baseline's solved scientific target.

With current evidence, the remaining work is deployment engineering or ordinary specialization rather than an algorithmic efficiency–robustness gap. SUTrack therefore does not enter HG6.

---

## CX044 — AsymTrack

**Final status: GAP_READY**

### Reconciled anchor and boundary

- Primary anchor: AsymTrack-T.
- S/B variants serve as controlled capacity/resolution references.
- Core that must remain: asymmetric template-once/search-online design, ETM, re-parameterized OPE and corner localization.

### Reconciled gap statement

AsymTrack uses one fixed operating point per deployed model and is already highly optimized. The paper reports relative gaps under low resolution, viewpoint change and fast motion.

**HYPOTHESIS — untested:** stronger family capacity/resolution may provide disproportionate benefit on those hard conditions while offering little marginal value on ordinary frames.

The hypothesis is rejected if T/S/B or matched capacity/resolution differences yield approximately uniform gains across easy and hard conditions, or if no pre-inference signal can predict oracle stronger-path benefit.

### Minimum pre-HG6 diagnostics

- paired T/S/B outputs and latency on identical frames;
- separate low-resolution, viewpoint-change and fast-motion slices;
- oracle stronger-path benefit per frame;
- predictive value of lightweight pre-inference difficulty signals.

### Collision boundary

Generic adaptive capacity, dynamic resolution, early exit and easy/hard routing are already heavily represented by HiT-DyHiT, ARTrack-AC and adjacent work. The only candidate-specific question is whether AsymTrack's reported challenge gaps create a measurable oracle allocation opportunity.

---

## CX058 — HiT-DyHiT

**Final status: GAP_READY**

### Reconciled anchor and boundary

- Primary anchor: standalone DyHiT Route1/Route2 system.
- Static HiT variants are controls.
- DyOSTrack is a separate wrapper reference.
- Core that must remain: hierarchical HiT, Bridge Module, lightweight/deep routes and easy/hard router.

### Reconciled gap statement

Partial lightweight processing precedes every route decision. The paper reports residual degradation under distractors and cluttered backgrounds.

**HYPOTHESIS — untested:** router calibration may misallocate compute under distractor/clutter ambiguity—some hard frames may exit through Route1 while some easy frames unnecessarily enter Route2.

The hypothesis is rejected if route score/decision does not predict distractor/clutter failure, forcing Route2 does not recover shallow-route failures, or oracle deep-path benefit is unrelated to the router margin.

### Minimum pre-HG6 diagnostics

- force Route1 and Route2 on identical frames;
- derive an oracle route-benefit label;
- log route score, decision, latency and outputs;
- measure false-shallow and false-deep allocation separately;
- separate static-template mismatch from router error.

### Collision boundary

Early exit, easy/hard routing, dynamic depth, fixed-threshold routing and strong-host invocation are already the family's own or recent-work contributions. The candidate-specific question concerns route calibration versus distractor/clutter residual failures and compute allocation.

---

## G2 consequence

| Candidate | Final gap readiness | Progression |
|---|---:|---|
| CX037 SSTrack-AAAI | **GAP_INCOMPLETE** | held for template/CE/failure diagnostics |
| CX038 MCITrack | **GAP_INCOMPLETE** | held for state/failure diagnostics |
| CX043 SUTrack | **GAP_REJECTED** | reference/deployment engineering only |
| CX044 AsymTrack | **GAP_READY** | eligible for mechanism-level HG6 audit |
| CX058 HiT-DyHiT | **GAP_READY** | eligible for mechanism-level HG6 audit |

These statuses are not scores and do not form a shortlist.

## Stage-3A closure pool

The complete `GAP_READY` pool is:

1. CX007 — SpikeTrack
2. CX013 — FARTrack
3. CX044 — AsymTrack
4. CX058 — HiT-DyHiT

`GAP_INCOMPLETE` candidates remain held outside HG6 until their missing diagnostic evidence is obtained. `GAP_REJECTED` candidates remain reference-only.

## Locked state

- Stage 3A G1: **COMPLETE**
- Stage 3A G2: **COMPLETE**
- Stage 3A overall: **COMPLETE**
- Stage 3B / HG6: **READY, NOT YET STARTED**
- S1–S7: **NOT STARTED**
- primary shortlist: **NONE**
- main baseline: **NONE**
- proposed architecture: **NONE**
