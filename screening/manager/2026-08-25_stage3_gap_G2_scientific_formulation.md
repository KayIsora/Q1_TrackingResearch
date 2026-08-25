# Stage 3A — Gap Batch G2 Manager scientific formulation

**Date:** 2026-08-25  
**Lane:** Manager — scientific/paper evidence  
**Batch:** G2 — CX037, CX038, CX043, CX044, CX058  
**Status:** MANAGER FORMULATION COMPLETE; independent Codex formulation and reconciliation required before any HG6 search.  
**Governing protocol:** `screening/manager/2026-08-25_stage3_gap_hg6_protocol.md`.

## Boundary

This document formulates candidate-specific research questions from already-audited evidence. It does not begin HG6, claim novelty, assign S1–S7, rank candidates, form a shortlist, select a baseline, or design a proposed architecture.

`GAP_READY` means only that a concrete and falsifiable question is ready for mechanism-level novelty search. It does not mean that the gap is novel, important enough for publication, or experimentally validated.

---

## CX037 — SSTrack-AAAI

**Anchored variant:** SSTrack-B256 with the released 150-epoch checkpoint.  
**Scientific core that must remain:** self-supervised decoupled spatio-temporal consistency learning, instance-level contrastive supervision, and the deployed ViT/candidate-elimination tracking formulation.

### Compute observation

- The deployed tracker remains a ViT-Base-style model with 12 transformer blocks.
- Candidate elimination physically reduces search tokens only after attention has already executed at its scheduled blocks.
- The released tracker re-embeds every selected raw template on each frame.
- The Python controller appends raw predicted templates throughout the sequence and later selects only a bounded active subset.
- A one-token query state remains bounded and is not the main memory cost.

### Robustness signal

No sufficiently specific residual inference-time robustness weakness of the final SSTrack tracker has been established.

The paper's scientific target is self-supervised representation learning without dense box annotation. Its benchmark gap relative to strong supervised trackers is broad, but the current evidence does not isolate a particular occlusion, distractor, fast-motion, or template-history failure caused by the final candidate-elimination/runtime policy.

### Possible but unsupported coupling question

**HYPOTHESIS — weak/unready:** candidate elimination and multi-template selection may interact differently with well-learned versus weak self-supervised target representations. Easy frames may not require all active templates, while difficult frames may be disproportionately sensitive to removed search tokens or stale selected templates.

This question is not ready because no SSTrack-specific failure slice or mechanism-linked attribute deficit has been established.

### Missing evidence before HG6

1. Attribute-level failure analysis for the released B256 checkpoint.
2. Per-frame retained-token and selected-template identity on success versus failure frames.
3. Controlled one-template versus multi-template and keep-rate ablations under the same checkpoint.
4. Separation of self-supervised representation weakness from ordinary runtime/template inefficiency.
5. Evidence that the same condition predicts both compute need and robustness outcome.

### HG6 vocabulary if the gap becomes ready

- self-supervised tracker token pruning;
- representation-aware candidate elimination;
- robust self-supervised visual tracking;
- template selection self-supervised SOT;
- uncertainty-aware candidate elimination;
- discriminative token retention under weak supervision;
- self-supervised temporal template reliability;
- adaptive compute for self-supervised trackers.

### Known collision boundary

Self-supervised spatio-temporal consistency, instance contrastive learning, candidate elimination, fixed keep-rate pruning, and multi-template tracking already have substantial prior art. Bounding raw history, caching template features, repairing the profiler/exporter, or replacing sort operations are engineering tasks rather than a scientific gap.

### Manager gap status

**GAP_INCOMPLETE** — compute/state observations are concrete, but a candidate-specific residual robustness signal and falsifiable coupling are not yet established.

---

## CX038 — MCITrack

**Anchored variant:** MCITrack-B224.  
**Scientific core that must remain:** Fast-iTPN visual encoder, four-layer Mamba contextual state, Injector/Extractor interaction blocks, and center prediction head.

### Compute observation

- Four Mamba blocks, four Injectors, six Extractors, and the configured Fast-iTPN slices execute on every frame.
- Five raw templates are re-encoded every frame; no encoded-template cache is used.
- Four hidden states are carried across frames. They are fixed-size rather than sequence-growing, but total about 49 MiB in FP32 for B224.
- The raw template bank may retain hundreds of GPU crops, while only five active templates enter each frame.
- Low confidence resets all four hidden states, but it does not conditionally skip contextual computation on the current frame.

### Robustness signal

No sufficiently specific residual weakness of the final MCITrack tracker has been established.

The confidence-based hidden-state reset is evidence that the implementation treats low-confidence context as potentially unreliable, but it is an existing safeguard, not proof that the final tracker still suffers state contamination or that the fixed threshold is wrong.

### Possible but unsupported coupling question

**HYPOTHESIS — weak/unready:** contextual state and cross-attention may be unnecessary on stable frames, while context may be valuable under genuine temporal ambiguity and harmful when stale or target-corrupted. The present always-on fusion plus hard confidence reset may allocate the same contextual compute before those conditions are distinguished.

The hypothesis remains unsupported until state usefulness/harm is observed on a candidate-specific failure slice.

### Missing evidence before HG6

1. Controlled zero-state, stale-state, and per-layer-state ablations on the same sequences.
2. Frame-level relation between hidden-state contribution, confidence reset, and tracking error.
3. Separate easy/stable, appearance-change, occlusion, and distractor diagnostics.
4. Per-block/context contribution versus five-template contribution.
5. Evidence that reducing contextual processing on easy frames does not uniformly damage performance.

### HG6 vocabulary if the gap becomes ready

- state-conditioned Mamba visual tracking;
- selective temporal context tracking;
- hidden-state reliability SOT;
- context contamination state-space tracker;
- adaptive Mamba depth tracking;
- conditional cross-attention temporal tracker;
- confidence-gated state-space inference;
- temporal-state reset and reuse;
- efficient video-level tracking context.

### Known collision boundary

Long-context tracking, Mamba/state-space tracking, confidence-based state reset, dynamic memory update, generic adaptive depth, template caching, and memory compression are already crowded areas. Disabling inference checkpoint wrappers, converting FP32 states, bounding the raw bank, or exporting explicit states is engineering unless tied to a reproducible robustness mechanism.

### Manager gap status

**GAP_INCOMPLETE** — a substantial always-on contextual path exists, but no accepted residual robustness signal or demonstrated state–failure coupling is available.

---

## CX043 — SUTrack

**Anchored variant:** SUTrack-T224 as the deployment-oriented RGB path, with B224 retained only as an accuracy reference.  
**Scientific core that must remain:** unified six-channel Fast-iTPN representation, token-role embeddings, unified-training family, and center decoder.

### Compute observation

- RGB inference duplicates RGB into the two three-channel halves of the six-channel input.
- A zero-text CLIP encoding is produced once and one text token remains in each frame's transformer sequence.
- The complete CLIP object and task-recognition head remain resident, although the task head does not execute during released inference.
- The raw template is re-encoded each frame.
- T224 otherwise has a fixed, bounded graph and no dynamic task/modality routing during RGB inference.

### Robustness signal

No specific residual RGB robustness weakness of the final SUTrack family has been established.

The paper's solved problem is unified representation across modalities and tasks. Current visible inefficiencies—resident unused objects, RGB duplication, zero-text handling, and static-template re-encoding—do not themselves identify a robustness failure or a single mechanism connecting efficiency and tracking quality.

### Scientific-gap assessment

The presently visible opportunity is dominated by:

- removing inference-unused residents;
- simplifying the RGB-only input path;
- caching a static template;
- exporter/runtime cleanup;
- standard compression of an already available Tiny variant.

Those are valuable deployment tasks but do not presently form an algorithmic efficiency–robustness contribution.

### What would be required to reopen the candidate

A future bounded study would need to establish both:

1. a residual RGB failure specifically linked to the unified representation or token-role mechanism; and
2. a nontrivial computation-allocation mechanism whose change addresses that failure rather than merely deleting unused components.

No such evidence is available now.

### HG6 vocabulary retained only for reference

- unified multimodal tracker RGB specialization;
- modality-token redundancy visual tracking;
- task-aware versus task-free SOT inference;
- RGB-only specialization of unified tracker;
- cross-modal representation pruning;
- token-type embedding visual tracking.

### Known collision boundary

Unified multimodal training, token-type embeddings, RGB duplication, text-token use, template caching, branch removal, pruning and lightweight backbones all have direct prior art. Engineering an RGB-only runtime is not a Q1-level scientific gap by itself.

### Manager gap status

**GAP_REJECTED** — with current evidence, only engineering cleanup or ordinary specialization/compression remains visible; no candidate-specific robustness coupling is established.

---

## CX044 — AsymTrack

**Anchored variant:** AsymTrack-T as the deployment anchor, with S/B variants used as controlled capacity/resolution references.  
**Scientific core that must remain:** asymmetric template-once/search-online framework, Efficient Template Modulation, re-parameterized Object Perception Enhancement, and corner-based localization.

### Compute observation

- Template neural processing is initialization-only; the released tracker caches template modulation signals/features.
- Steady-state inference follows one fixed low-capacity search path with ETM relation modeling and a fused OPE/search graph.
- The family exposes T/S/B operating points with different input resolution/capacity, but a selected tracker does not adapt capacity or resolution by frame state.
- The final models are already very small, so ordinary pruning/backbone compression has limited scientific leverage.

### Robustness signal

The paper reports a relative gap to precision-oriented trackers under:

- low resolution;
- viewpoint change;
- fast motion.

This is a candidate-specific residual signal. It is a relative limitation rather than proof of universal failure, and it must be reproduced under compatible protocols.

### Coupling hypothesis

**HYPOTHESIS — untested:** the fixed low-capacity operating point may be sufficient on ordinary frames but insufficient when low resolution, viewpoint change, or fast motion requires richer spatial/contextual representation. A stronger family configuration may deliver disproportionate benefit on those hard frames while providing little benefit on easy frames.

The hypothesis is rejected if T/S/B or resolution/capacity differences yield approximately uniform gains across easy and hard conditions, or if the reported challenge gaps do not correlate with the marginal value of stronger processing.

### Minimum falsification tests

1. Run T/S/B and matched-resolution/capacity controls on the same predeclared frame/sequence slices.
2. Measure per-frame localization improvement and latency difference of the stronger operating point.
3. Test whether simple difficulty signals available before full inference predict the oracle stronger-path benefit.
4. Separate low resolution, viewpoint change, and fast motion rather than merging them into a generic hard-frame label.
5. Reject the candidate if no condition-specific capacity benefit exists.

These are diagnostic tests, not a proposed adaptive-capacity architecture.

### HG6 vocabulary

- adaptive capacity asymmetric tracker;
- dynamic resolution visual tracking;
- conditional enhancement efficient Siamese tracking;
- difficulty-aware tracker capacity;
- low-resolution adaptive visual tracking;
- fast-motion conditional computation tracker;
- viewpoint-change dynamic inference;
- multi-capacity tracker routing;
- early exit / late expansion SOT;
- elastic lightweight visual tracking.

### Known collision boundary

Template-once execution, asymmetric Siamese tracking, ETM/OPE, generic early exit, dynamic depth/resolution, easy–hard routing, and strong-host invocation are already represented by AsymTrack, HiT-DyHiT, ARTrack-AC and adjacent dynamic-inference work. The only defensible candidate-specific question is whether AsymTrack's reported challenge gaps map to a measurable oracle capacity-allocation opportunity.

### Manager gap status

**GAP_READY** — a specific residual challenge gap and a falsifiable capacity-allocation question are available, although novelty collision risk is expected to be high.

---

## CX058 — HiT-DyHiT

**Anchored variant:** standalone DyHiT with its Route1/Route2 router; static HiT variants provide controls, while DyOSTrack remains a separate host-wrapper reference.  
**Scientific core that must remain:** hierarchical HiT backbone, Bridge Module, lightweight route, deeper route, and easy/hard dynamic routing.

### Compute observation

- DyHiT performs partial lightweight processing before every route decision.
- Easy frames terminate through Route1; difficult frames continue through deeper Route2.
- The initial raw template is re-encoded every frame; the released standalone tracker does not update it.
- Routing uses a fixed learned router/threshold scheme and Python-controlled branch selection.
- Generic early exit and easy–hard allocation are already the family’s central contribution.

### Robustness signal

The journal's qualitative analysis reports degradation in scenes with distractors and cluttered backgrounds. This is a candidate-specific residual signal of the final family.

### Coupling hypothesis

**HYPOTHESIS — untested:** first-stage routing evidence may be insufficiently calibrated for distractor/clutter ambiguity. Some genuinely hard distractor frames may exit through the shallow route, while some easy frames may enter the deep route without benefit. Route misallocation may therefore explain both wasted compute and residual robustness loss.

The hypothesis is rejected if route score/decision has no relationship to distractor/clutter failures, if forcing Route2 does not recover shallow-route failures, or if deep-route invocation benefit is unrelated to the router's confidence/margin.

### Minimum falsification tests

1. Log route score, selected path, per-route latency, and outputs for every frame.
2. Force Route1 and Route2 on the same frames to obtain an oracle route-benefit label.
3. Compare router decisions with oracle labels on distractor/clutter and ordinary slices.
4. Measure false-deep invocations and false-shallow exits separately.
5. Test whether static-template age/appearance mismatch explains failures independently of the router.
6. Reject the coupling if the deeper path cannot improve the reported residual failures.

### HG6 vocabulary

- route calibration visual tracking;
- distractor-aware early exit tracker;
- uncertainty-aware dynamic routing SOT;
- oracle routing gap visual tracking;
- hard-frame misrouting tracker;
- conditional depth under clutter;
- adaptive inference router calibration;
- dynamic tracker route confidence;
- selective deep path visual tracking;
- early-exit robustness calibration.

### Known collision boundary

Easy/hard routing, early exit, dynamic depth, lightweight-first acceleration, fixed-threshold routing, and host invocation are already central to HiT-DyHiT or recent dynamic trackers. A surviving claim must concern the measurable relationship between route calibration, distractor/clutter residual failures, and compute allocation—not merely replacing the threshold or adding uncertainty terminology.

### Manager gap status

**GAP_READY** — the candidate has a direct allocation rule, an author-reported residual weakness, and a route-oracle falsification experiment.

---

## G2 Manager summary

| Candidate | Manager gap status | Primary reason |
|---|---:|---|
| CX037 SSTrack-AAAI | **GAP_INCOMPLETE** | Runtime/template costs are concrete, but no mechanism-specific residual robustness signal is established. |
| CX038 MCITrack | **GAP_INCOMPLETE** | Always-on contextual state is concrete, but state-related residual failure evidence is missing. |
| CX043 SUTrack | **GAP_REJECTED** | Visible opportunities are engineering cleanup/RGB specialization without robustness coupling. |
| CX044 AsymTrack | **GAP_READY** | Author-reported low-resolution/viewpoint/fast-motion gaps create a falsifiable capacity-allocation question. |
| CX058 HiT-DyHiT | **GAP_READY** | Dynamic route allocation and distractor/clutter residual weakness support an oracle-routing test. |

No HG6 decision is made here. Codex must independently formulate G2 from code evidence before reconciliation.
