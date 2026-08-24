# Stage 2A — Batch D Manager scientific audit

**Date:** 2026-08-25  
**Lane:** Manager — paper/scientific evidence  
**Batch:** D active candidates only — CX053, CX058, CX125  
**Status:** MANAGER EVIDENCE EXTRACTION COMPLETE; Codex code/engineering audit and batch reconciliation still required.  
**Governing protocol:** `docs/11_systematic_screening_protocol.md` and `screening/manager/2026-08-24_stage2_deep_audit_framework.md`.

## Scope and non-claims

The original Batch D also contained UMDATrack. It is not active because final early-gate reconciliation left UMDATrack at HG3 PENDING. This Manager audit therefore processes only the three HG3-PASS candidates in canonical-ID order:

1. CX053 — UncTrack
2. CX058 — HiT-DyHiT
3. CX125 — MPT

This file extracts paper-level scientific evidence and explicitly labeled hypotheses. It does **not** decide HG4/HG5, begin HG6, assign S1–S7, rank candidates, shortlist a baseline, or design a proposed architecture.

---

# CX053 — UncTrack

**Paper:** Siyuan Yao et al., *UncTrack: Reliable Visual Object Tracking With Uncertainty-Aware Prototype Memory Network*, IEEE Transactions on Image Processing 34, 3533–3546, 2025. DOI: https://doi.org/10.1109/TIP.2025.3559796 [R47]  
**Official repository:** `ManOfStory/UncTrack@61bd4be673ac32dd8948f995ce4548855d0ab1d0`. [R48]

Author manuscript/full method description: https://arxiv.org/abs/2503.12888  
Official repository: https://github.com/ManOfStory/UncTrack

## A. Architecture / task facts

**FACT — cited:** UncTrack explicitly reframes deterministic box regression as uncertainty-aware tracking. Its transformer encoder performs template-search interaction; an Uncertainty-Aware Localization Decoder (ULD) predicts corner localization and associated uncertainty; a Prototype Memory Network (PMN) uses that uncertainty together with historical prototypes to judge whether the current target-state estimate is reliable.

**FACT — cited:** PMN stores historical target prototypes, retrieves top-k similar prototypes, performs lightweight cross-attention for reliability estimation, and updates the memory bank using reliable samples. Online inference uses a first-in-first-out memory-update policy.

**FACT — cited:** When the current estimate is judged unreliable, the paper discards the unreliable sample, resamples a reliable template from the nearest historical frame, doubles the search region and uses a Kalman filter to preserve temporal motion consistency.

## B. Efficiency / benchmark facts

**FACT / BOUNDARY:** The paper's primary contribution is reliability and uncertainty use, not edge efficiency. ULD and PMN introduce uncertainty prediction, memory read/write and prototype-attention work on top of a transformer tracker.

**RESOURCE AVAILABILITY FACT:** The official repository provides released models/raw results, benchmark scripts and a model-profile script. [R48]

**OPEN QUESTION:** The Manager source pass does not establish a Jetson-relevant parameter/MAC/runtime split between transformer encoder, ULD, PMN, online memory operations and unreliable-state search expansion. Codex must inspect the released B/L variants and actual per-frame execution path.

## C. Training facts

**FACT — cited:** UncTrack uses two-stage training. Stage 1 trains the transformer encoder and ULD with localization and uncertainty losses. Stage 2 freezes the transformer encoder and ULD and trains PMN for prototype-reliability classification.

**RESOURCE AVAILABILITY FACT:** The repository releases DDP training scripts for multiple backbone variants, but the exact per-device batch, model sizes, freezing implementation, AMP/checkpointing and realistic single-3060 path require code inspection. [R48]

## D. Robustness evidence

**FACT — cited:** The method targets concrete reliability failures: heavy occlusion and background distractors increase localization uncertainty; unreliable predictions can accumulate across a video; changing appearance can corrupt template adaptation. UncTrack uses uncertainty-guided memory and template resampling to address those problems.

**INTERPRETATION — reasoned:** These are the baseline's solved targets, not automatically remaining weaknesses of the final UncTrack system. Ordinary ideas such as “use uncertainty to gate template update,” “retrieve reliable history,” or “enlarge search when uncertain” have direct collision with the baseline itself.

**OPEN QUESTION:** No sufficiently specific author-reported residual failure of final UncTrack was established in the Manager pass. A remaining weakness must be found through code/failure analysis rather than generic claims about occlusion.

## E. Candidate-specific hypotheses

**HYPOTHESIS — untested — computational redundancy:** If ULD, top-k memory retrieval, cross-attention PMN and reliability classification execute fully on every easy frame, part of the reliability path may be conditionally avoidable. Code must establish actual frequency, memory size and whether the unreliable-state branch changes compute before this becomes a credible redundancy hypothesis.

**HYPOTHESIS — untested — robustness weakness:** PENDING. The uncertainty/memory mechanism already directly addresses reliability and drift.

**HYPOTHESIS — untested — possible coupling:** A lighter conditional reliability path could in principle preserve full PMN/search expansion only for ambiguous frames, but uncertainty-driven conditional computation is exposed to strong novelty collision with UncTrack itself and recent dynamic-tracking work. It remains only a hypothesis and HG6 is not started.

## F. HG4 evidence package — no decision

- official tracker checkpoints and a two-stage frozen-module training structure exist;
- stage 2 may provide a bounded module-training path without retraining the full encoder;
- exact model size, per-device batch, activation memory and single-RTX3060 feasibility remain **PENDING** pending code audit.

## G. HG5 evidence package — no decision

- PMN uses compact prototypes rather than full-frame feature histories, which may be favorable;
- the base transformer, ULD, PMN, template bank, search-doubling branch and Kalman/host logic still require operator and memory inspection;
- no Nano claim is made; HG5 remains **PENDING**.

---

# CX058 — HiT-DyHiT

**Paper:** Ben Kang et al., *Exploiting Lightweight Hierarchical ViT and Dynamic Framework for Efficient Visual Tracking*, International Journal of Computer Vision 133, 6689–6711, 2025. DOI: https://doi.org/10.1007/s11263-025-02500-9 [R49]  
**Official repository:** `kangben258/HiT@ca806400def2b9ab42628f7a7e941b188d89606f`. [R50]

Official article: https://link.springer.com/article/10.1007/s11263-025-02500-9  
Official repository: https://github.com/kangben258/HiT

## A. Architecture facts

**FACT — cited:** HiT is a lightweight one-stream tracker composed of a hierarchical transformer, Bridge Module and prediction head. The Bridge Module combines high-level semantic information and shallow fine-grained information, while dual-image positional encoding jointly represents template and search positions.

**FACT — cited:** DyHiT extends HiT with an early-exit dynamic router. Search features from the first backbone stage are classified as easy or difficult. Easy frames terminate early and use Route1; difficult frames continue through the deeper Route2.

**FACT — cited:** The journal extension also introduces DyTracker, a training-free acceleration wrapper for high-performance trackers. DyHiT-Route1 and the router run first; only difficult scenes invoke the expensive host tracker.

## B. Efficiency / benchmark facts

**FACT — cited:** The official paper/repository reports a family of HiT/DyHiT speed–accuracy operating points on desktop GPU, CPU, Jetson AGX and Jetson NX, and provides ONNX profiling/conversion utilities. Those device measurements do not establish Jetson Nano behavior.

**FACT — cited:** DyHiT's research contribution is already state-conditioned computation: easy and difficult scenarios receive different backbone depth, while DyTracker conditionally invokes a stronger host tracker. The router is deliberately lightweight.

**INTERPRETATION — reasoned:** Generic “easy frame → shallow path, hard frame → deep path,” early exit, threshold routing or lightweight-host-first acceleration are already the baseline's central novelty. Such ideas cannot be reclaimed as a new contribution merely by changing the confidence score or threshold name.

## C. Training facts

**FACT — cited / RESOURCE FACT:** HiT uses standard SOT training datasets; the repository provides distributed and single-GPU debug paths. DyHiT has two training stages, and the training-free DyTracker wrapper uses pretrained component weights. [R50]

**OPEN QUESTION:** Exact batch, trainable/frozen modules, router labels, route-specific losses, AMP/checkpointing and realistic 12-GB modification path require code inspection.

## D. Robustness evidence

**FACT — cited:** The journal reports that HiT handles fast motion and viewpoint change well relative to other efficient trackers. Therefore those attributes must not be casually presented as established HiT weaknesses.

**AUTHOR-REPORTED QUALITATIVE LIMITATION — cited:** The paper's qualitative analysis states that HiT performance tends to degrade in the presence of distractors and cluttered backgrounds.

**FACT — cited:** The dynamic-template ablation reports only modest average gains while reducing speed, showing an explicit accuracy–compute trade-off for extra appearance adaptation.

## E. Candidate-specific hypotheses

**HYPOTHESIS — untested — computational redundancy:** The main generic dynamic-depth redundancy has already been addressed. Remaining opportunities may lie in route misclassification, router/Route1 duplicate work, dynamic-template overhead or host invocation in DyTracker, but code-level frequency and residual cost must be established.

**HYPOTHESIS — untested — robustness weakness:** Distractor/clutter degradation is a concrete author-reported residual signal, but it must be reproduced and linked to the released routing/template behavior.

**HYPOTHESIS — untested — possible coupling:** A mechanism that improves distractor discrimination while controlling additional dynamic-template or deep-route cost might exist; however the obvious adaptive-compute concept directly collides with DyHiT. Any surviving research question must go beyond ordinary routing/early exit and is deferred to HG6.

## F. HG4 evidence package — no decision

- official checkpoints, stage-specific scripts and a single-GPU debug path exist;
- HiT is structurally lightweight and DyHiT builds on pretrained HiT stages;
- exact single-3060 router/new-module training feasibility remains **PENDING** until code evidence is reconciled.

## G. HG5 evidence package — no decision

- lightweight variants, route-based early exit, AGX/NX tests and ONNX utilities provide strong structural deployment signals;
- AGX/NX are not Nano, and actual Nano operator/memory/route behavior remains unmeasured;
- HG5 remains **PENDING** pending code/export audit.

---

# CX125 — MPT

**Paper:** Jie Zhao et al., *Efficient Motion Prompt Learning for Robust Visual Tracking*, Proceedings of the 42nd International Conference on Machine Learning, PMLR 267:77353–77370, 2025. [R13]  
**Official repository:** `zj5559/Motion-Prompt-Tracking@418eb6565038f92bf8bafa3d7dd02dc9e0426dae`. [R14]

Official publication: https://proceedings.mlr.press/v267/zhao25e.html  
Official repository: https://github.com/zj5559/Motion-Prompt-Tracking

## A. Architecture / task facts

**FACT — cited:** MPT is a lightweight plug-and-play motion-prompt module rather than a standalone tracker family. It is integrated into vision trackers so that motion and visual cues are used jointly.

**FACT — cited:** MPT includes a motion encoder with three positional encodings for long-term trajectory representation, a fusion decoder and an adaptive weighting mechanism for combining motion and visual features.

**FACT — cited:** The paper integrates MPT into three tracker families—OSTrack, SeqTrack and ARTrack—with five model combinations, and evaluates them on seven tracking benchmarks.

## B. Efficiency / benchmark facts

**FACT — cited:** The authors characterize the module as requiring minimal training cost and causing negligible speed sacrifice while improving robustness. Exact host-specific parameter/MAC/latency overhead must remain tied to each integration and cannot be treated as one standalone tracker measurement.

**SCOPE BOUNDARY:** Because MPT requires a host tracker, its main-baseline suitability depends on which host is selected and what is considered the candidate architecture. It may ultimately be more appropriate as a mechanism/reference or extension than as the main baseline, but that decision is not made in this Manager pass.

## C. Training facts

**RESOURCE AVAILABILITY FACT:** The official repository provides trajectory data, models/results and an `eval.sh`-based training/testing workflow, while environment and baseline preparation are inherited from the integrated host trackers. [R14]

**OPEN QUESTION:** Exact trajectory length, per-host frozen/trainable boundaries, batch, epochs, optimizer, memory cost and RTX3060 feasibility require code inspection. Training feasibility cannot be inferred only from the phrase “minimal training cost.”

## D. Robustness evidence

**FACT — cited:** The scientific motivation is that appearance-only trackers do not fully exploit long-term motion; motion prompts and adaptive fusion improve robustness across different host trackers.

**INTERPRETATION — reasoned:** This is primarily the problem solved by MPT. A residual failure mode of the final MPT-integrated trackers is not established by the abstract/repository evidence inspected here.

**OPEN QUESTION:** Whether the adaptive weighting fails under trajectory corruption, long disappearance, camera motion or incorrect host boxes is a testable question, not a current result.

## E. Candidate-specific hypotheses

**HYPOTHESIS — untested — computational redundancy:** If motion encoding/fusion runs every frame even when visual tracking is stable, conditional invocation may reduce overhead; however the module is already reported lightweight, so the remaining gain may be too small for a strong Core contribution.

**HYPOTHESIS — untested — robustness weakness:** PENDING. Motion-history corruption and host-error propagation must be established from code or experiments.

**HYPOTHESIS — untested — possible coupling:** Motion-reliability-aware invocation could theoretically connect compute and robustness, but adaptive weighting is already part of MPT and related conditional-compute work creates high collision risk. No novelty claim is made.

## F. HG4 evidence package — no decision

- official host-specific models and trajectory resources exist;
- the motion module is presented as lightweight and plug-and-play;
- feasibility depends on the selected host tracker and actual trainable boundary;
- HG4 remains **PENDING** pending code audit.

## G. HG5 evidence package — no decision

- MPT's incremental module may be light, but total deployment cost is dominated by the host tracker;
- no standalone Nano route can be assessed without selecting a host and measuring the integrated pipeline;
- HG5 remains **PENDING**.

---

## Batch-D Manager state

- CX053 UncTrack — Manager scientific evidence: **COMPLETE**
- CX058 HiT-DyHiT — Manager scientific evidence: **COMPLETE**
- CX125 MPT — Manager scientific evidence: **COMPLETE**

HG4/HG5 remain undecided until independent Codex code evidence is reconciled. HG6 and soft scoring remain not started. There is no further systematic evidence batch after Batch D; after reconciliation, the project must close Stage 2A and resolve targeted HG5 evidence/profile requirements before candidate-specific HG6 and soft scoring.
