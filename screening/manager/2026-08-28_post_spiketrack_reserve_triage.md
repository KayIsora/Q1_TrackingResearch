# Post-SpikeTrack reserve-gap triage — Manager independent lane

**Date:** 2026-08-28  
**Status:** MANAGER TRIAGE COMPLETE; independent Codex triage and reconciliation pending  
**Governing protocol:** `screening/manager/2026-08-28_post_spiketrack_fallback_protocol.md`

## Boundary

This is an independent bounded-triage judgment based on the already audited paper/code evidence and the exact missing-evidence contracts. It does not run a new diagnostic, promote a candidate to `GAP_READY`, begin HG6, assign S1–S7, form a shortlist, select a baseline, or design an architecture.

The purpose is to decide whether a low-cost inference-only probe could answer the missing question before any second full diagnostic program is authorized.

## CX009 — UETrack

**Manager triage:** `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`

### Why a bounded probe is plausible

- Dense TP-MoE executes all configured experts, giving an exact contribution site.
- Official checkpoints and evaluator are available.
- Per-expert outputs can in principle be hooked and withheld without training.
- A small source-selected RGB attribute slice can test whether expert contribution/disagreement differs under occlusion, distractor, fast motion or low resolution.

### Required stop condition

Reject the gap if expert contribution is approximately uniform across conditions, if skipping any expert uniformly harms the tracker, or if no residual RGB failure slice is reproduced.

### Boundary

CLIP removal, duplicated-input cleanup, static-template caching and resident-module deletion remain engineering tasks and cannot rescue a failed expert-condition question.

## CX010 — UTPTrack

**Manager triage:** `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`

### Why a bounded probe is plausible

- The released implementation already exposes token identities and multiple physical pruning points.
- Inference-only controls can compare original selection with retained/removed-token interventions on identical frozen frames.
- A small failure/control slice can test whether fixed retention removes target-discriminative tokens disproportionately under ambiguity.

### Required stop condition

Reject the gap if retained/removed token identity does not predict error, if keep-rate effects are uniform across conditions, or if the surviving proposal is only generic dynamic keep-ratio/token pruning.

## CX024 — DAM4SAM

**Manager triage:** `TRIAGE_HOLD_MISSING_DATA_OR_RESOURCE`

### Why it is held

- The residual weakness after DAM is not established.
- DAM-specific incremental cost is not yet separated from the heavy SAM-family host.
- The pinned reproducible host is Hiera-L, while lighter EfficientTAM/EdgeTAM transfer is reported but not established as an equivalent pinned code unit for this project.
- The candidate's central solved problem already is distractor-aware memory; ordinary adaptive memory or lighter-host substitution has high collision risk.

### Re-entry evidence

A reproducible lighter official host or a bounded same-host profile plus residual DiDi-style failure evidence is required before diagnostic authorization.

## CX037 — SSTrack-AAAI

**Manager triage:** `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`

### Why a bounded probe is plausible

- Official checkpoint/evaluator and bounded active template selection are available.
- Initial-only versus selected-history controls and CE retained-token logging are inference-only.
- Source-frame validity of selected historical templates can be inspected independently of tracker outcome, then related to contribution/error on a frozen slice.

### Required stop condition

Reject the gap if history/template validity and CE identity do not predict final error, or if the only benefit is generic template caching, history bounding or keep-rate tuning.

## CX038 — MCITrack

**Manager triage:** `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`

### Why a bounded probe is plausible

- Four explicit fixed-size contextual states and confidence reset provide exact state intervention points.
- Zero-state, stale-state and per-layer-state controls can be implemented inference-only from a shared prefix state.
- The probe can separate contextual-state contribution from the five-template path on frozen disruption/control slices.

### Required stop condition

Reject the gap if state interventions have uniform effects, if no final-model state-related failure is reproduced, or if the only remaining work is state quantization/export/template caching.

## Manager triage summary

| Candidate | Manager provisional triage | Principal reason |
|---|---:|---|
| CX009 UETrack | `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC` | exact all-expert compute site and cheap per-expert controls |
| CX010 UTPTrack | `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC` | exact token-selection evidence and inference-only interventions |
| CX024 DAM4SAM | `TRIAGE_HOLD_MISSING_DATA_OR_RESOURCE` | residual weakness and DAM-specific cost not separated from host; lighter pinned unit missing |
| CX037 SSTrack-AAAI | `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC` | history/CE controls are bounded and source-validity can be audited |
| CX038 MCITrack | `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC` | explicit state interventions and state-matched forks are tractable |

No diagnostic candidate is selected in this document. After independent Codex triage, reconciliation may authorize at most two bounded probes based on scientific answerability, execution cost and collision risk—not familiarity or estimated benchmark strength.

## Locked state

- Codex independent triage: **PENDING**;
- Manager↔Codex reconciliation: **PENDING**;
- authorized bounded diagnostics: **NONE**;
- soft scoring: **NOT STARTED**;
- primary shortlist: **NONE**;
- main baseline: **NONE**;
- proposed architecture: **NONE**.
