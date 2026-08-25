# Stage 3A — Gap Batch G1 Manager scientific formulation

**Date:** 2026-08-25  
**Lane:** Manager — scientific/paper evidence  
**Batch:** G1 — CX007, CX009, CX010, CX013, CX024  
**Status:** MANAGER FORMULATION COMPLETE; independent Codex formulation and reconciliation required before any HG6 search.

## Boundary

This document formulates candidate-specific research questions from already-audited evidence. It does not begin HG6, claim novelty, assign S1–S7, rank candidates, form a shortlist, select a baseline, or design the final proposed architecture.

`GAP_READY` means only that a falsifiable candidate-specific question is concrete enough for mechanism-level novelty search. It is not a statement that the gap is novel or that the method will work.

---

## CX007 — SpikeTrack

**Anchored variant:** SpikeTrack-S256-T1 as the first deployment-oriented variant; T3 is retained as a comparative temporal/template mode.  
**Scientific core that must remain:** spike-driven asymmetric tracker with Memory Retrieval Modules and template-conditioned retrieval.

### Compute observation

- Six Memory Retrieval Modules execute on every frame in the cached search path.
- T3 repeats retrieval over three template/time slices, increases cache and MRM cost, and adds temporal gating.
- The released spike path is dense conventional tensor computation rather than an event-driven sparse runtime.

### Robustness signal

The paper explicitly reports difficulty under visually similar objects and links that limitation to insufficient fine-grained representation/discrimination. This is a residual limitation of the final method rather than merely a generic tracking statement.

### Coupling hypothesis

**HYPOTHESIS — untested:** the tracker applies the same multi-scale retrieval structure regardless of whether the current frame is visually unambiguous or contains similar distractors. Easy frames may not require the full retrieval allocation, while ambiguous/distractor frames may require richer or more discriminative retrieval than the present uniform path provides.

This hypothesis is rejected if per-scale/per-template retrieval importance does not vary systematically with distractor ambiguity, or if reducing retrieval on easy frames harms tracking as much as on hard frames.

### Minimum falsification tests

1. Measure latency and outputs while bypassing or isolating each MRM scale under identical checkpoints.
2. Separate frames/sequences with similar-object distractors from ordinary frames using benchmark attributes or curated diagnostics.
3. Compare T1/T3 and selective MRM execution on the same frames.
4. Test whether MRM importance/activation predicts both compute need and distractor robustness.

These are diagnostic ablations, not a proposed dynamic-routing method.

### HG6 vocabulary

- spiking visual tracking adaptive computation;
- SNN early exit / dynamic timestep / temporal-step selection;
- selective memory retrieval network;
- distractor-aware computation allocation;
- fine-grained representation in spiking vision transformers;
- uncertainty-conditioned SNN inference;
- multi-scale retrieval gating;
- conditional template retrieval tracking.

### Known collision boundary

The project cannot claim ordinary T1/T3 scaling, generic early exit, generic confidence gating, or merely adding a distractor/ReID head as new. Recent adaptive-computation trackers and SNN dynamic-inference literature are expected novelty adversaries.

### Manager gap status

**GAP_READY** — concrete always-on compute site, author-reported residual weakness and a falsifiable coupling question are present.

---

## CX009 — UETrack

**Anchored variant:** UETrack-T/S/B RGB inference path, with T preferred for edge-oriented profiling and B retained for accuracy reference.  
**Scientific core that must remain:** unified student encoder with TP-MoE and the training-time TAD framework.

### Compute observation

- TP-MoE performs dense soft routing and executes every expert in its configured block on every frame.
- The static template is encoded again every frame.
- Even RGB inference constructs a six-channel duplicated input, runs a zero-text CLIP encoding once per sequence and carries a text token in the transformer stream.
- Several inference-unused components remain resident in the Python model construction.

### Robustness signal

No sufficiently specific residual RGB robustness weakness of final UETrack has been established. The paper primarily solves unified multimodal efficiency and unreliable teacher supervision during training. Those solved targets cannot be relabeled as remaining inference weaknesses.

### Possible but unsupported coupling question

**HYPOTHESIS — weak/unready:** expert disagreement or routing entropy might correlate with hard RGB frames, permitting conditional expert use. Current evidence does not establish that expert disagreement predicts a real tracking failure, nor that the always-on dense expert path is unnecessary on easy frames.

### Missing evidence before HG6

1. Candidate-specific RGB failure analysis across occlusion, distractor, fast motion and low-resolution attributes.
2. Expert-output disagreement/importance by frame difficulty.
3. Ablation showing that one or more experts can be skipped without uniformly reducing performance.
4. Separation of resident-memory cleanup from scientific compute reduction.

### HG6 vocabulary if the gap becomes ready

- sparse MoE visual tracking;
- conditional expert routing tracking;
- expert disagreement uncertainty;
- token-pooling MoE pruning;
- dynamic MoE inference vision transformer;
- task-conditioned expert activation;
- template feature caching unified tracker.

### Known collision boundary

TP-MoE and TAD are the baseline’s own contributions. Removing CLIP, cleaning unused modules or caching a static template alone would be engineering/standard optimization, not a Q1-level scientific contribution.

### Manager gap status

**GAP_INCOMPLETE** — compute sites are concrete, but no specific residual RGB robustness weakness or evidenced coupling is available.

---

## CX010 — UTPTrack

**Anchored variant:** generic RGB UTPTrack-O B256 with fixed 0.7 retention.  
**Scientific core that must remain:** joint physical pruning of search, static-template and dynamic-template tokens with token-type-aware selection.

### Compute observation

- The method already physically compacts all three token streams at multiple layers.
- Retained lengths follow a fixed schedule for the selected resolution and keep ratio; retained identities remain content-dependent.
- Both raw templates are re-embedded every frame, and full attention executes before each pruning event.

### Robustness signal

No candidate-specific residual robustness weakness of final UTPTrack has been established in the inspected paper evidence. The paper’s central result is accuracy preservation under aggressive token pruning; it does not report a specific distractor, occlusion or fast-motion failure caused by the final pruning policy.

### Possible but unsupported coupling question

**HYPOTHESIS — weak/unready:** a fixed retention ratio may over-compute easy frames while discarding discriminative target/template tokens in ambiguous frames. This is scientifically plausible but presently unsupported by a UTPTrack-specific failure analysis.

### Missing evidence before HG6

1. Map per-layer removed-token identity to tracking failures and challenge attributes.
2. Test fixed retention ratios on easy versus ambiguous/distractor frames.
3. Determine whether retained-token confidence/entropy predicts failure.
4. Separate ordinary further pruning from a materially different robustness-aware allocation question.

### HG6 vocabulary if the gap becomes ready

- adaptive token retention visual tracking;
- uncertainty-aware token pruning tracker;
- discriminative token preservation;
- distractor-aware template/search pruning;
- dynamic keep ratio tracking;
- token merging versus pruning in SOT;
- target-aware foreground token retention;
- robust sparse vision transformer tracking.

### Known collision boundary

Ordinary search-token pruning, template-token pruning, fixed keep-rate tuning, candidate elimination and token-type-aware selection directly collide with UTPTrack and earlier CE trackers. A new claim would need a distinct state/robustness mechanism.

### Manager gap status

**GAP_INCOMPLETE** — strong compute evidence but insufficient candidate-specific robustness evidence.

---

## CX013 — FARTrack

**Anchored variant:** FARTrack-Tiny as the scientific reference, with Nano/Pico as compressed deployment variants.  
**Scientific core that must remain:** multi-template trajectory/command-token tracking, TSSD family and IFAS temporal-template mechanism.

### Compute observation

- The released final IFAS path applies attention masking but does not physically shorten the 445-token transformer sequence; Q/K/V and full attention shapes remain dense through all 15 Tiny blocks.
- Five raw template images are patch-embedded on every frame.
- Per-frame mask generation uses accumulated attention, sorting and Python-indexed mask construction.
- Template and mask histories are appended without an explicit sequence-length cap in the released tracker.

### Robustness signal

- The paper/appendix states that prolonged disappearance or occlusion can make the available template set invalid.
- Template-count ablations show that adding more templates increases compute without monotonically improving accuracy; higher counts can provide little gain or degrade performance.

These signals are directly tied to the final template mechanism rather than generic tracking difficulty.

### Coupling hypothesis

**HYPOTHESIS — untested:** template validity is a shared cause of both wasted computation and robustness degradation. Invalid/redundant templates continue to be embedded and attended even when they add no reliable target evidence, while their presence may contaminate or confuse localization after occlusion/disappearance.

The hypothesis is rejected if template-validity measures do not predict either compute-utility or tracking robustness, or if physically reducing/isolating low-validity templates produces no benefit beyond ordinary model compression.

### Minimum falsification tests

1. Measure marginal accuracy and latency contribution of each active template by frame/sequence state.
2. Corrupt or invalidate selected templates and observe failure propagation.
3. Compare attention masking with physical template/token compaction under identical retained information.
4. Bound history and vary active template count based on offline validity labels to test whether compute and robustness change together.
5. Separate ordinary template caching from validity-conditioned active-set behavior.

These are diagnostic experiments, not the final proposed mechanism.

### HG6 vocabulary

- template validity visual tracking;
- adaptive template number SOT;
- dynamic template selection tracking;
- physical template token pruning;
- memory compression visual tracking;
- reliability-aware template bank;
- stale template suppression;
- occlusion-aware template update;
- temporal memory routing tracking;
- template contamination / memory corruption SOT;
- autoregressive tracker template sparsification.

### Known collision boundary

IFAS, TSSD, multi-template tracking, generic token pruning, quality-gated template update, uncertainty-based memory selection and adaptive computation already have substantial prior art. The surviving distinction must involve a materially specific relationship among template validity, physical compute removal and robustness—not merely “add confidence” or “use fewer templates.”

### Manager gap status

**GAP_READY** — both computation and robustness evidence point to the same template-validity subsystem and admit direct falsification.

---

## CX024 — DAM4SAM

**Anchored variant:** DAM memory mechanism as demonstrated on SAM2.1 and reported lighter EfficientTAM/EdgeTAM hosts; the pinned Hiera-L implementation remains the reproducible code reference.  
**Scientific core that must remain:** distractor-aware memory/introspection and memory-management logic.

### Compute observation

- The heavy host image encoder, memory attention and decoder dominate the full tracker path.
- DAM-specific incremental work consists mainly of multi-mask introspection, distractor tests, memory admission and memory management.
- Active memory use is bounded, but output dictionaries/object-size histories can grow with sequence length.
- The journal reports that the DAM mechanism transfers to lighter host families, although those integrations are not established as complete pinned code units in the current repository snapshot.

### Robustness signal

Distractor drift and memory-quality filtering are the baseline’s principal solved problems. No specific residual robustness weakness of final DAM4SAM has been established. Ordinary “filter bad memories,” “detect distractors” or “use lighter SAM” ideas collide directly with the method itself.

### Possible but unsupported coupling question

**HYPOTHESIS — weak/unready:** the amount/type of memory introspection may be adaptively allocated according to distractor risk, or a host-independent memory budget may preserve DAM robustness on lighter hosts. Current evidence does not establish a residual failure or show that DAM-specific compute—not the host—is the relevant bottleneck.

### Missing evidence before HG6

1. Separate DAM incremental latency/memory from host cost on the same hardware.
2. Identify residual failure cases of DAM4SAM on DiDi or other distractor-heavy data.
3. Verify code-level EfficientTAM/EdgeTAM integration or reproduce an equivalent official configuration.
4. Test memory-budget/introspection ablations against residual distractor failures.

### HG6 vocabulary if the gap becomes ready

- adaptive memory budget SAM2 tracking;
- efficient distractor-aware memory;
- SAM2 memory compression tracking;
- EdgeTAM visual tracking memory;
- EfficientTAM tracker memory management;
- conditional memory attention video segmentation;
- host-agnostic tracking memory;
- bounded long-video memory SAM2.

### Known collision boundary

Distractor-aware memory, introspection, memory-quality admission and lighter-host transplantation are already central to DAM4SAM/IJCV. Engineering a streaming wrapper or swapping to EdgeTAM alone is not sufficient novelty.

### Manager gap status

**GAP_INCOMPLETE** — deployment path exists, but a residual robustness weakness and DAM-specific shared compute/robustness gap are not yet established.

---

## G1 Manager summary

| Candidate | Manager gap status | Primary reason |
|---|---:|---|
| CX007 SpikeTrack | **GAP_READY** | Always-on multi-scale retrieval and author-reported similar-object weakness create a falsifiable coupling question. |
| CX009 UETrack | **GAP_INCOMPLETE** | Concrete dense-expert/template costs but no specific residual RGB robustness weakness. |
| CX010 UTPTrack | **GAP_INCOMPLETE** | Strong pruning evidence but no demonstrated failure of the final fixed-retention policy. |
| CX013 FARTrack | **GAP_READY** | Invalid/redundant template evidence links dense template computation and robustness. |
| CX024 DAM4SAM | **GAP_INCOMPLETE** | Baseline already solves distractor-memory failure; residual weakness and DAM-specific bottleneck remain missing. |

No HG6 decision is made here. Codex must independently formulate G1 from code evidence before reconciliation.
