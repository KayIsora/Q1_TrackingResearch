# Stage 3A — Gap Batch G1 reconciliation

**Date:** 2026-08-25  
**Status:** G1 RECONCILED; G2 may begin.  
**Inputs:**

- `screening/manager/2026-08-25_stage3_gap_G1_scientific_formulation.md`
- `screening/codex/2026-08-25_stage3_gap_G1_code_formulation.md`

**Governing protocol:** `screening/manager/2026-08-25_stage3_gap_hg6_protocol.md`.

## Boundary

This reconciliation decides only **gap readiness** for G1. It does not start HG6, claim novelty, assign S1–S7, rank candidates, form a shortlist, select a baseline, or design a proposed architecture.

Allowed states are:

- `GAP_READY` — a concrete compute observation, candidate-specific robustness signal, falsifiable coupling question, and minimum rejection test are all available;
- `GAP_INCOMPLETE` — one or more required scientific elements remain missing;
- `GAP_REJECTED` — only ordinary engineering/compression or a mechanism already solved by the baseline remains visible.

Manager and Codex independently reached the same readiness state for all five candidates. The final state below is therefore based on evidence agreement, not voting.

---

## CX007 — SpikeTrack

**Final status: GAP_READY**

### Reconciled anchor and boundary

- Primary anchor: SpikeTrack-S256-T1.
- Controlled comparison: SpikeTrack-S256-T3.
- Core that must remain: SDTV3 spike-driven tracker, cached template/search split, six Memory Retrieval Modules, and center prediction head.

### Reconciled gap statement

Six MRMs execute at fixed locations on every search frame. T3 repeats retrieval over three template/time slices and adds temporal gating. The official paper reports a residual weakness under visually similar objects and insufficient fine-grained discrimination.

**HYPOTHESIS — untested:** retrieval allocation may be unnecessarily uniform on unambiguous frames while particular scale/template retrieval contributions may become more important under target–distractor ambiguity.

The hypothesis is rejected if per-MRM/T1–T3 effects do not interact with distractor versus non-distractor conditions, or if retrieval signals do not predict target–distractor separation and tracking outcome.

### Minimum pre-HG6 diagnostics

- per-MRM residual/output hooks;
- one-MRM-at-a-time inference ablations;
- paired T1/T3 evaluation on predeclared distractor and non-distractor slices;
- target-versus-strongest-distractor score margin, box error, and mode-specific latency.

### Collision boundary

Generic SNN early exit, dynamic timestep/depth, template gating, ordinary confidence routing, export repair, quantization, and dense-kernel optimization cannot be claimed as the candidate-specific novelty.

---

## CX009 — UETrack

**Final status: GAP_INCOMPLETE**

### Reconciled evidence

The compute sites are concrete:

- dense TP-MoE soft routing;
- every expert executes on every frame;
- static-template re-encoding;
- duplicated RGB six-channel construction;
- zero-text CLIP setup and a text token carried in the sequence;
- inference-unused resident components.

However, no specific residual generic-RGB robustness weakness of the final tracker is established. TAD already addresses unreliable teacher supervision during training, and that solved problem cannot be relabeled as an inference-time residual weakness.

### Missing evidence

Before HG6, a bounded diagnostic must establish:

- a reproducible generic-RGB failure slice;
- expert disagreement/routing behavior on that slice;
- condition-specific sensitivity to controlled expert bypass;
- separation of scientific TP-MoE behavior from ordinary cleanup such as removing unused residents or duplicate decoding.

Without that evidence, conditional-expert claims remain speculative.

---

## CX010 — UTPTrack

**Final status: GAP_INCOMPLETE**

### Reconciled evidence

UTPTrack already physically compacts search, static-template, and dynamic-template tokens. Retained counts follow a fixed schedule while identities are content-dependent. Both raw templates are re-embedded each frame, and attention is computed before each scheduled pruning event.

No pruning-policy-linked residual robustness weakness of final UTPTrack has been established. The current idea that fixed retention may over-compute easy frames and remove discriminative tokens on ambiguous frames is plausible but unsupported by candidate-specific failure evidence.

### Missing evidence

Before HG6, diagnostics must establish:

- challenge/failure slices where the fixed policy is specifically implicated;
- removed-token identity and target/distractor relevance;
- retention-policy sensitivity on easy versus ambiguous frames;
- whether a confidence/entropy signal predicts both pruning need and failure.

Ordinary additional pruning, fixed keep-rate tuning, template caching, sort-to-TopK replacement, ONNX work, and quantization are not sufficient scientific gaps.

---

## CX013 — FARTrack

**Final status: GAP_READY**

### Reconciled anchor and boundary

- Primary anchor: released final-sparse FARTrack-Tiny configuration.
- Nano/Pico remain family references, but no executable final-sparse mapping is used as the diagnostic anchor unless separately established.
- Core that must remain: multi-template FARTrack formulation, trajectory/command-token prediction family, TSSD family relation, and IFAS temporal-template mechanism.

### Reconciled gap statement

The released final IFAS path masks attention but does not physically shorten the 445-token sequence; all five raw templates are re-embedded every frame, full attention shapes remain dense, mask construction executes each frame, and released histories are not explicitly capped. The paper/appendix states that prolonged disappearance or occlusion can invalidate the available template set, while template-count ablations show that more templates increase compute without monotonic accuracy gain.

**HYPOTHESIS — untested:** template validity may jointly determine compute utility and robustness. Invalid or redundant templates may continue consuming embedding/attention work while supplying harmful or confusing evidence after occlusion/disappearance.

The hypothesis is rejected if template-validity measures do not predict marginal accuracy/latency contribution, if controlled invalidation has no condition-specific effect, or if physical active-set reduction provides only generic compression gains unrelated to robustness.

### Minimum pre-HG6 diagnostics

- per-template marginal contribution and latency;
- controlled template corruption/invalidation;
- attention masking versus physical template/token compaction under equal retained evidence;
- bounded history and offline validity-conditioned active-set tests;
- separation of simple caching from validity-conditioned compute allocation.

### Collision boundary

IFAS, TSSD, multi-template tracking, generic token pruning, ordinary confidence-gated update, uncertainty-based memory selection, and generic adaptive computation already constrain the claim. The candidate-specific distinction must concern the measurable relationship among template validity, physical compute removal, and robustness.

---

## CX024 — DAM4SAM

**Final status: GAP_INCOMPLETE**

### Reconciled evidence

The heavy host dominates the full path, while DAM-specific incremental work consists primarily of multi-mask introspection, distractor tests, memory admission, and memory management. Active memory is bounded, but retained dictionaries/history can grow. The family has lighter-host evidence in the publication.

Distractor-aware memory, introspection, memory-quality admission, and drift resistance are already the baseline’s principal solved problems. No specific residual robustness weakness of final DAM4SAM is established, and current evidence does not show that DAM-specific compute rather than host compute is the relevant bottleneck.

### Missing evidence

Before HG6, the project would need:

- a same-host split of DAM incremental cost versus host cost;
- reproducible residual failures on DiDi or another distractor-heavy diagnostic;
- verified lighter-host integration evidence at the code/runtime level;
- memory-budget/introspection ablations tied to those residual failures.

Swapping to EdgeTAM/EfficientTAM, adding a streaming wrapper, or merely bounding memory is not sufficient novelty.

---

## G1 consequence

| Candidate | Final gap readiness | Progression |
|---|---:|---|
| CX007 SpikeTrack | **GAP_READY** | eligible for later mechanism-level HG6 audit |
| CX009 UETrack | **GAP_INCOMPLETE** | held for bounded residual-failure/expert diagnostics |
| CX010 UTPTrack | **GAP_INCOMPLETE** | held for pruning-policy-linked failure diagnostics |
| CX013 FARTrack | **GAP_READY** | eligible for later mechanism-level HG6 audit |
| CX024 DAM4SAM | **GAP_INCOMPLETE** | held for residual-failure and DAM-specific cost diagnostics |

These statuses are not scores and do not form a shortlist.

## Sequencing decision

**PROJECT DECISION — locked sequencing:** HG6 search for G1 is deliberately held until G2 gap formulation and reconciliation are complete. This avoids beginning novelty work on the first ready candidates before the remaining canonical candidates receive the same gap-readiness treatment.

## Locked state

- Stage 3A G1: **COMPLETE**
- Stage 3A G2: **READY**
- Stage 3B / HG6: **NOT STARTED**
- S1–S7: **NOT STARTED**
- primary shortlist: **NONE**
- main baseline: **NONE**
- proposed architecture: **NONE**
