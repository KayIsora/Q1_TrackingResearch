# Stage 2A — Batch B Manager scientific audit

**Date:** 2026-08-25  
**Lane:** Manager — paper/scientific evidence  
**Batch:** B — CX017, CX020, CX024, CX037, CX038  
**Status:** MANAGER EVIDENCE EXTRACTION COMPLETE; Codex code/engineering audit and batch reconciliation still required.  
**Governing protocol:** `docs/11_systematic_screening_protocol.md` and `screening/manager/2026-08-24_stage2_deep_audit_framework.md`.

## Scope and non-claims

This file extracts paper-level scientific evidence and carefully labeled hypotheses. It does **not** decide HG4/HG5, does not begin HG6, does not assign S1–S7, does not rank candidates, and does not select a baseline. Hardware-specific speed is kept within its reported boundary; no desktop/A100/RTX result is converted into Jetson Nano performance.

---

# CX017 — GOT-JEPA

**Paper:** Shih-Fang Chen et al., *GOT-JEPA: Generic Object Tracking with Model Adaptation and Occlusion Handling using Joint-Embedding Predictive Architecture*, IEEE TCSVT 2026. [R26]  
**Official repository:** `chenshihfang/GOT@84e9324317e4afe62c06b2c51a97563f79730a2e`. [R25]

## A. Architecture facts

**FACT — cited:** GOT-JEPA extends joint-embedding predictive architecture from image-feature prediction to tracking-model prediction. A teacher predictor forms pseudo tracking models from a clean current frame, while a student predicts the same models from a corrupted current frame, explicitly targeting model adaptation under occlusions, distractors, and other adverse observations. Author preprint: https://arxiv.org/abs/2602.14771

**FACT — cited:** The paper adds **OccuSolver**, which adapts a point-centric point tracker for object-aware visibility estimation and fine-grained occlusion-pattern modeling. Object priors from the tracker condition iterative visibility refinement, and the resulting labels improve later model prediction.

**RESOURCE AVAILABILITY FACT:** The pinned official repository provides separate pretraining, fine-tuning, and OccuSolver-stage commands, and released models/raw results. [R25]

## B. Efficiency facts

**FACT — cited:** The paper reports approximately **3 GB GPU memory during evaluation on RTX 4090** and about **24 FPS for the L-378 variant and 50 FPS for the lower-resolution variant**. These are RTX4090 figures only and are not Nano evidence. Author paper/preprint: https://arxiv.org/abs/2602.14771

**OPEN QUESTION:** Parameters/MACs and the cost split between semantic backbone, model predictor, tracking head, and OccuSolver are not yet normalized in this Manager pass and require code evidence.

## C. Training facts

**FACT — cited:** The paper uses staged training. For L-378, stage 1 uses 8 GPUs and stage 2 uses 4; L-252 uses 4 GPUs for its training stages. Reported batch size ranges from 48 to 64 depending on resources.

**FACT — cited:** At the OccuSolver stage, the model predictor and tracking head are initialized from stage-1 weights and frozen while OccuSolver is trained on 8-frame sequences. [R25 + author paper]

## D. Benchmark / robustness evidence

**FACT — cited:** The method is explicitly designed around two weaknesses of generic tracking: limited generalization/model adaptation to unseen dynamic conditions and coarse occlusion reasoning. The paper reports GOT-JEPA improvements across seven benchmarks and gives, among others, LaSOT success 75.4 and TrackingNet success 86.4 in its main comparison.

**INTERPRETATION — reasoned:** Those weaknesses are the method's solved problem, not automatically a remaining failure mode of GOT-JEPA itself.

**OPEN QUESTION:** No sufficiently specific residual author-reported weakness of the final GOT-JEPA + OccuSolver system is established in the sources inspected here.

## E. Candidate-specific hypotheses

**HYPOTHESIS — untested — computational redundancy:** The multi-stage inference path may contain repeated or condition-insensitive occlusion/model-adaptation computation, especially if fine-grained visibility reasoning executes on ordinary easy frames. This must be established from code execution frequency before it can be treated as researchable redundancy.

**HYPOTHESIS — untested — robustness weakness:** PENDING. The paper strongly addresses occlusion rather than clearly documenting a remaining one.

**HYPOTHESIS — untested — possible coupling:** If OccuSolver or adaptation compute is always-on while only difficult/occluded states need it, a reliability-conditioned invocation hypothesis could exist; however this is vulnerable to adaptive-compute novelty collision and cannot be promoted before Codex inspection and HG6.

## F. HG4 evidence package — no decision

- Official staged checkpoints/resources exist.
- Author training uses 4–8 GPUs and batch 48–64.
- The later OccuSolver stage freezes major pretrained components, which may allow checkpoint-based research without reproducing the full farm.
- Exact single-RTX3060 memory/training path remains **PENDING** pending code audit.

## G. HG5 evidence package — no decision

- RTX4090 24/50 FPS does not imply Nano speed.
- Low-resolution variant and staged/frozen design provide some structural headroom.
- Point-tracker/visibility solver execution frequency, operator complexity, state growth, exportability, and actual model size remain unknown.
- HG5 remains **PENDING**.

---

# CX020 — SAMURAI

**Paper:** Cheng-Yen Yang et al., *SAMURAI: Motion-Aware Memory for Training-Free Visual Object Tracking With SAM 2*, IEEE TIP 2026. [R27]  
**Official repository:** `yangchris11/samurai@76ba195984892b0d1e3db5d9c9f90bb62175680a`. [R28]

## A. Architecture facts

**FACT — cited:** SAMURAI adapts SAM 2 for zero-shot visual tracking by adding motion-aware mask selection and motion-aware memory selection without additional training. Official DOI: https://doi.org/10.1109/TIP.2026.3651835 ; project: https://yangchris11.github.io/samurai/

**FACT — cited:** The motivation is concrete: SAM 2's affinity-score-only mask selection can confuse identities in crowded scenes, while fixed-window memory does not account for memory quality and can propagate errors. SAMURAI combines a Kalman-filter motion score with mask affinity for candidate selection and admits memories using mask/object/motion quality criteria.

**RESOURCE AVAILABILITY FACT:** The official release directly uses SAM 2.1 checkpoints and explicitly states that no SAMURAI training is required. [R28]

## B. Efficiency facts

**FACT — cited:** The method is training-free but inherits the SAM 2 image/video memory architecture. Training-free does not mean lightweight inference.

**OPEN QUESTION:** The TIP/official sources inspected in this Manager pass do not establish a Jetson-Nano-relevant memory footprint or operator profile. Any 'real-time' statement remains tied to the authors' hardware/software context, not Nano.

## C. Training facts

**FACT — cited:** No method-specific training/fine-tuning is required; official inference uses SAM 2.1 foundation weights. The Kalman filter and memory-selection logic are algorithmic additions rather than learned modules.

**INTERPRETATION — reasoned:** For our research program, HG4 must therefore be judged by whether a new proposed trainable module can be developed around a frozen/pretrained SAM 2 backbone on one 3060, not by an original SAMURAI training farm that does not exist.

## D. Benchmark / robustness evidence

**AUTHOR MOTIVATION — cited:** SAMURAI targets crowded scenes, fast motion, self-occlusion, identity confusion, and low-quality fixed-window memories. The paper reports improvements over SAM 2 and competitive generic-tracking results, including gains on LaSOT-ext and GOT-10k.

**OPEN QUESTION:** A residual weakness of the final SAMURAI system is not established strongly enough in the Manager source pass. The official README also states that live/streaming webcam input is not supported by the inherited SAM 2 codebase; this is an implementation limitation, not a scientific tracking-failure claim. [R28]

## E. Candidate-specific hypotheses

**HYPOTHESIS — untested — computational redundancy:** SAM 2's foundation backbone/memory attention may spend large fixed compute despite SAMURAI's lightweight decision logic. Whether any part is conditionally avoidable without destroying mask quality requires code profiling.

**HYPOTHESIS — untested — robustness weakness:** PENDING; SAMURAI already directly targets memory quality and motion consistency.

**HYPOTHESIS — untested — possible coupling:** The quality signals already used for memory admission could potentially control expensive memory/image processing, but this is only a hypothesis and is highly exposed to recent reliability-aware memory/adaptive-computation prior art.

## F. HG4 evidence package — no decision

- SAMURAI itself needs no training.
- Official SAM 2.1 checkpoints provide initialization.
- New-module research could potentially freeze the foundation model, but the feasibility of meaningful trainable additions on 12 GB depends on the exact backbone variant/activation path.
- HG4 remains **PENDING**.

## G. HG5 evidence package — no decision

- The algorithmic additions are lightweight, but the inherited SAM 2 foundation architecture is not automatically edge-lightweight.
- Streaming is not supported in the official current code.
- Exact Hiera variant used by the benchmark path, persistent memory size, image-encoder reuse, TensorRT/export risks and runtime memory require code audit.
- HG5 remains **PENDING**.

---

# CX024 — DAM4SAM

**Paper family:** Jovana Videnović et al., *Distractor-Aware Memory-Based Visual Object Tracking*, IJCV 2026, extended from *A Distractor-Aware Memory for Visual Object Tracking with SAM2*, CVPR 2025. [R29]  
**Official repository:** `jovanavidenovic/DAM4SAM@9c954504b39ebca4c412f207be0787c26bfac85a`. [R30]

## A. Architecture facts

**FACT — cited:** DAM4SAM is a training-free, drop-in distractor-aware memory and introspection-based management mechanism for SAM 2.1. It is designed to reduce drift toward visually similar distractors and improve redetection after occlusion. Official IJCV page: https://link.springer.com/article/10.1007/s11263-026-02790-7

**FACT — cited:** The IJCV extension reports that the same distractor-aware memory improves EfficientTAM and EdgeTAM as well as SAM2.1, indicating that the memory mechanism is not tied only to the heaviest SAM2 backbone.

**FACT — cited:** The IJCV paper states that Hiera-L is used for its main DAM4SAM experiments; SAM2.1/DAM4SAM evaluation was performed on A100 40 GB hardware. This is not Nano evidence.

## B. Efficiency facts

**FACT — cited:** The IJCV extension reports an **11% improvement when the DAM memory is integrated into real-time EfficientTAM**, matching the tracking quality of non-real-time SAM2.1-L on multiple benchmarks, and a **4% improvement with edge-oriented EdgeTAM**. This is important evidence that the robustness mechanism itself can transfer to lighter host trackers; it does not establish DAM4SAM-Hiera-L Nano performance.

**OPEN QUESTION:** The incremental runtime/memory overhead of DAM relative to its host model must be quantified from code/paper tables before any edge conclusion.

## C. Training facts

**FACT — cited / RESOURCE FACT:** DAM4SAM requires no additional training; SAM 2.1 checkpoints are the inference weights. [R30]

## D. Benchmark / robustness evidence

**FACT — cited:** Distractors are the paper's central failure mode. The IJCV extension reports improved drift resistance/redetection and introduces DiDi specifically to amplify distractor evaluation. It reports improvement over SAM2.1 on thirteen benchmarks and SOTA on ten in the extended version.

**INTERPRETATION — reasoned:** The final method already addresses distractor-aware memory selection; generic ideas such as “filter bad memories” or “distractor-aware update” have direct novelty collision with this baseline's own contribution.

**OPEN QUESTION:** A new residual failure mode of DAM4SAM itself remains to be established.

## E. Candidate-specific hypotheses

**HYPOTHESIS — untested — computational redundancy:** The host SAM2.1-L is heavy, and distractor-aware memory may contain repeated similarity/memory-management work. However the most scientifically interesting efficiency direction may be the host-backbone choice rather than DAM itself; code must distinguish these costs.

**HYPOTHESIS — untested — robustness weakness:** PENDING; distractor drift/redetection is already the solved target.

**HYPOTHESIS — untested — possible coupling:** Because DAM is demonstrated on EfficientTAM and EdgeTAM, host-aware memory capacity or conditional memory processing could be testable, but ordinary “use fewer memories” is unlikely to be novel without a more specific mechanism.

## F. HG4 evidence package — no decision

- Training-free baseline and official checkpoints greatly reduce baseline reproduction/training burden.
- New trainable components could in principle be added around a frozen host.
- Whether meaningful joint training with a SAM2/EdgeTAM host is possible on 12 GB remains implementation-dependent.
- HG4 remains **PENDING**.

## G. HG5 evidence package — no decision

- Main DAM4SAM experiment uses Hiera-L/A100 and should not be called Nano-friendly.
- However the paper provides unusually direct evidence that the proposed memory mechanism works when transplanted to EfficientTAM and EdgeTAM, creating a credible lighter-host deployment path.
- Exact EdgeTAM integration code availability, operator/runtime overhead, and memory footprint require Codex inspection.
- HG5 remains **PENDING**.

---

# CX037 — SSTrack-AAAI

**Paper:** Yaozong Zheng et al., *Decoupled Spatio-Temporal Consistency Learning for Self-Supervised Tracking*, AAAI 2025. [R31]  
**Official repository:** `GXNU-ZhongLab/SSTrack@5dcf04cc`. [R32]

## A. Architecture / learning facts

**FACT — cited:** SSTrack is primarily a **self-supervised training framework**, not an inference-time compression method. It replaces dense manual box supervision with decoupled spatio-temporal consistency learning: global spatial localization + local temporal association, together with an instance contrastive loss for multi-view instance correspondence. Official AAAI page: https://ojs.aaai.org/index.php/AAAI/article/view/33155

**RESOURCE AVAILABILITY FACT:** The official repo exposes B256/B384 checkpoints, training/evaluation scripts, and a profiling script. [R32]

## B. Efficiency / benchmark facts

**FACT — cited:** Official repo reports SSTrack-B256 at GOT-10k AO 67.1, LaSOT AUC 64.8, TrackingNet AUC 80.1; B384 at 72.4 / 65.9 / 80.4. The repo states its reported speed is measured on RTX2080Ti; these numbers are not Nano evidence. [R32]

**INTERPRETATION — reasoned:** Benchmark quality is strong for self-supervised tracking but materially below current top supervised 2025–2026 trackers on several generic benchmarks. This matters later for S5 but is not scored here.

## C. Training facts

**RESOURCE AVAILABILITY FACT:** Official training starts from DropMAE ViT-Base, uses two distributed processes in the published command, and provides 150-epoch / GOT-specific configurations. [R32]

**OPEN QUESTION:** Exact per-process batch, activation memory, and whether the final tracker inference graph differs materially from ODTrack-style ViT inference require code audit.

## D. Robustness evidence

**FACT — cited:** The scientific contribution concerns learning generic tracking representations from unlabeled video and simulating appearance/motion variation during self-supervised learning.

**OPEN QUESTION:** No clear candidate-specific residual inference-time robustness weakness is established. The paper's large gains are mainly relative to prior self-supervised trackers, not evidence that a particular runtime failure mechanism remains unsolved.

## E. Candidate-specific hypotheses

**HYPOTHESIS — untested — computational redundancy:** Because the primary novelty is training-time supervision rather than inference efficiency, the final ViT-Base runtime may retain conventional transformer redundancy. This is too generic until the released model path is inspected.

**HYPOTHESIS — untested — robustness weakness:** PENDING.

**HYPOTHESIS — untested — possible coupling:** PENDING. A strong shared efficiency–robustness mechanism is not yet visible from paper evidence alone.

## F. HG4 evidence package — no decision

- Official checkpoints and pretraining path exist.
- ViT-Base self-supervised training is distributed in the official recipe, but checkpoint-based fine-tuning may still be feasible.
- Exact 12-GB trainability remains **PENDING**.

## G. HG5 evidence package — no decision

- B256/B384 use ViT-Base-style tracking; no edge-specific mechanism is established in the paper.
- Desktop speed cannot establish Nano feasibility.
- HG5 remains **PENDING** pending code/operator/model-size evidence.

---

# CX038 — MCITrack

**Paper:** Ben Kang et al., *Exploring Enhanced Contextual Information for Video-Level Object Tracking*, AAAI 2025. [R33]  
**Official repository:** `kangben258/MCITrack@e667193e`. [R34]

## A. Architecture facts

**FACT — cited:** MCITrack propagates video-level context through **Mamba hidden states** rather than only dynamic templates or a few extra context tokens. Its Contextual Information Fusion (CIF) module combines a Mamba layer that stores historical context with cross-attention that injects that history into current visual features at multiple backbone levels. Official AAAI page: https://ojs.aaai.org/index.php/AAAI/article/view/32440

**FACT — cited:** The design is explicitly intended to preserve richer long-range context throughout the stream, with hidden states functioning as a persistent video-level representation.

## B. Efficiency / benchmark facts

**FACT — cited / RESOURCE FACT:** Official results report MCITrack-B224 at LaSOT AUC 75.3, LaSOT-ext 54.6, TrackingNet 86.3, GOT-10k AO 77.9; MCITrack-L384 at 76.6 / 55.7 / 87.9 / 80.0. [R34]

**RESOURCE AVAILABILITY FACT:** The repo contains an official FLOPs/params/speed profiler, but exact reconciled numbers/hardware need code inspection. [R34]

## C. Training facts

**RESOURCE AVAILABILITY FACT:** The official B224 training command uses eight distributed processes. Training datasets include LaSOT, GOT-10k, COCO, TrackingNet, and VastTrack in the released project setup. Pretrained weights and logs are provided. [R34]

## D. Robustness evidence

**FACT — cited:** The paper argues that previous video-level trackers lose context because only a few tokens/templates carry temporal information; MCITrack addresses this by maintaining richer hidden-state context and reports strong gains across generic benchmarks.

**OPEN QUESTION:** The paper evidence inspected here does not establish a final-system failure mode such as stale/corrupted hidden-state propagation. Such a failure is plausible in stateful trackers but must not be asserted without evidence.

## E. Candidate-specific hypotheses

**HYPOTHESIS — untested — computational redundancy:** CIF/Mamba + cross-attention is deeply integrated across backbone blocks and may execute continuously even when long-term context adds little. Code must establish exact insertion count and per-frame state/update cost.

**HYPOTHESIS — untested — robustness weakness:** Persistent hidden states could potentially carry stale or contaminated context after tracking errors, but there is no sufficient source evidence yet; status remains PENDING.

**HYPOTHESIS — untested — possible coupling:** A state-quality mechanism that controls temporal-context injection could theoretically couple compute and robustness, but this directly overlaps the broader reliability/adaptive-computation novelty space and must not be promoted before code reconciliation and HG6.

## F. HG4 evidence package — no decision

- Official pretrained/final checkpoints and training logs exist.
- Author recipe uses eight processes, but checkpoint-based research may avoid full from-scratch training.
- Mamba/CIF integration depth and activation memory must be code-audited before judging 12-GB fine-tuning.
- HG4 remains **PENDING**.

## G. HG5 evidence package — no decision

- B224 is smaller than L384 but long-context state and repeated CIF cross-attention may create per-frame overhead/state complexity.
- The official profiler is useful but desktop measurements alone do not settle Nano plausibility.
- Mamba/Triton/custom-operator/export requirements and hidden-state memory behavior need code inspection.
- HG5 remains **PENDING**.

---

## Batch-B Manager summary — no ranking

| Candidate | Paper-level strength signal | Main unresolved scientific issue before reconciliation |
|---|---|---|
| CX017 GOT-JEPA | strong generic benchmarks; explicit adaptation/occlusion design | residual weakness and always-on OccuSolver/adaptation cost unknown |
| CX020 SAMURAI | training-free motion-aware memory; concrete SAM2 memory-quality motivation | foundation-model inference cost and residual weakness |
| CX024 DAM4SAM | distractor/redetection robustness; mechanism transfers to EfficientTAM/EdgeTAM | host-vs-DAM cost split and residual weakness |
| CX037 SSTrack | self-supervised learning without dense labels | weaker supervised-period benchmark competitiveness; runtime opportunity unclear |
| CX038 MCITrack | very strong video-level contextual benchmark results | continuous CIF/Mamba cost and hidden-state failure behavior unresolved |

No candidate has been soft-scored or promoted. Batch B now awaits the independent Codex code/engineering audit before HG4/HG5 reconciliation.
