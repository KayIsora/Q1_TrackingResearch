# Stage 2A — Batch A Manager scientific audit

**Date:** 2026-08-24  
**Lane:** Manager — paper/scientific evidence  
**Batch:** A — CX007, CX009, CX010, CX013, CX014  
**Status:** MANAGER EVIDENCE EXTRACTION COMPLETE; Codex code/engineering audit and batch reconciliation still required.  
**Governing protocol:** `docs/11_systematic_screening_protocol.md` and `screening/manager/2026-08-24_stage2_deep_audit_framework.md`.

## Scope and non-claims

This file extracts paper-level scientific evidence and carefully labeled hypotheses for Batch A. It does **not** decide HG4 or HG5, does not start HG6, does not assign S1–S7, and does not rank candidates. Desktop/AGX/CPU/NPU measurements are recorded only with their hardware boundary and are never converted into Jetson Nano claims.

The five candidates are processed in predeclared canonical-ID order, not by perceived promise.

---

# CX007 — SpikeTrack

**Paper:** Qiuyang Zhang et al., *SpikeTrack: A Spike-driven Framework for Efficient Visual Tracking*, CVPR 2026. [R18]  
**Official repository:** `faicaiwawa/SpikeTrack@1537db51a1cc9f6e30cce469fba3e51f5721b3d0`. [R19]

## A. Architecture facts

**FACT — cited:** SpikeTrack is a spike-driven RGB tracker based on an asymmetric SNN design. The paper identifies two central ideas: asymmetric timestep expansion / unidirectional information flow and a memory-retrieval module (MRM) that repeatedly queries compact template-initialized memory to recover target cues. Official CVPR source: https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_SpikeTrack_A_Spike-driven_Framework_for_Efficient_Visual_Tracking_CVPR_2026_paper.html

**FACT — cited:** The paper uses Spike-Driven Transformer V3 backbones: SDTV3-19M for the Base family and SDTV3-5.1M for Small. Six variants combine base/small backbone, 256/384 input resolution, and timestep count T=1/3. The prediction head follows a center-head formulation with classification/center, offset, and size branches. Official paper PDF: https://openaccess.thecvf.com/content/CVPR2026/papers/Zhang_SpikeTrack_A_Spike-driven_Framework_for_Efficient_Visual_Tracking_CVPR_2026_paper.pdf

**RESOURCE AVAILABILITY FACT — cited:** The pinned official repository contains 256/384 and T=1/T=3 configurations and publishes models, raw results, training logs, and spike-firing-rate tooling. [R19]

## B. Efficiency facts

**FACT — cited:** The paper's energy claim is SNN-specific: it reports that SpikeTrack can surpass TransT on LaSOT while consuming 1/26 of TransT's estimated energy under the authors' SNN/ANN energy model. This is not a Jetson Nano energy or latency measurement.

**FACT — cited:** The official paper states that all SpikeTrack models were trained on eight NVIDIA RTX 4090 GPUs. The official repository exposes SFR (spike firing rate) measurement as an implementation-level efficiency diagnostic.

**OPEN QUESTION:** Exact standard-GPU latency, operator efficiency, memory footprint, and TensorRT behavior of the spiking operators on Maxwell CUDA hardware are not established by the paper evidence extracted here.

## C. Training facts

**FACT — cited:** Training data are COCO, LaSOT, TrackingNet, and GOT-10k. T=1 models are trained for 320 epochs; T>1 models start from pretrained T=1 SpikeTrack weights and train for 60 additional epochs. Paper total batch size is 128. AdamW is used.

**CODE FACT — inspected:** The pinned `spiketrack_b256_t3.yaml` uses search 256, three 256-pixel templates, batch size 16 in the config, 60 epochs for the T=3 stage, and initializes from a trained T=1 model. The discrepancy between per-process/config batch and paper total batch must be handled during later training-feasibility analysis, not guessed away.

## D. Benchmark / robustness evidence

**AUTHOR-REPORTED LIMITATION — cited:** The CVPR paper explicitly states that SpikeTrack has difficulty handling scenes with similar objects because it lacks an explicit module for distinguishing them and spike information is insufficient for fine-grained representations. The paper's visualization notes interference from similar objects even when the final target is recovered.

**FACT — cited:** The paper reports competitive ANN-level tracking while emphasizing energy efficiency; exact cross-method comparisons must retain protocol/hardware boundaries.

## E. Candidate-specific hypotheses

**HYPOTHESIS — untested — robustness weakness:** Fine-grained discrimination against similar distractors may be a real weakness worth reproducing because it is explicitly acknowledged by the authors.

**HYPOTHESIS — untested — computational redundancy:** The multi-timestep and recurrent memory-retrieval path may contain frame/state-dependent computation that is unnecessary in easy frames, but no redundancy is established yet. Code-level execution frequency and actual standard-GPU cost must be inspected by Codex.

**HYPOTHESIS — untested — possible coupling:** A state-dependent mechanism that preserves richer/fine-grained processing only when distractor ambiguity is high could theoretically target both compute and similar-object robustness. This is only a research hypothesis; it is especially vulnerable to collision with recent adaptive-computation work and must not enter HG6 before evidence reconciliation.

## F. HG4 evidence package — no decision

- Official checkpoints exist.
- Author training used 8× RTX 4090 and paper total batch 128.
- T>1 training is initialized from T=1 weights rather than necessarily requiring full random-from-scratch training.
- Exact single-RTX3060 VRAM feasibility for meaningful fine-tuning remains **PENDING** pending code audit/profile evidence.

## G. HG5 evidence package — no decision

- SNN arithmetic/energy advantages are hardware-model dependent.
- The target Jetson Nano B01 is a conventional Maxwell CUDA GPU, not a neuromorphic accelerator.
- Whether the released spike operators map efficiently to TensorRT/CUDA on Nano is **PENDING**.
- No Nano FPS/latency inference is made from the paper's energy model.

## H. Unresolved items

- exact parameters/MAC-equivalent cost for the candidate variant most appropriate to our controlled comparison;
- execution frequency/cost of MRM and T>1 timestep expansion;
- standard CUDA memory/runtime profile;
- export/operator compatibility;
- single-3060 train/fine-tune profile.

---

# CX009 — UETrack

**Paper:** Ben Kang et al., *UETrack: A Unified and Efficient Framework for Single Object Tracking*, CVPR 2026. [R20]  
**Official repository:** `kangben258/UETrack@fd13b0eaf16d51536008295f3b27807c69eaad50`. [R21]

## A. Architecture facts

**FACT — cited:** UETrack is a unified tracker covering RGB, Depth, Thermal, Event, and Language. The paper introduces Token-Pooling-based Mixture-of-Experts (TP-MoE) and Target-aware Adaptive Distillation (TAD). TP-MoE increases modeling capacity through feature aggregation/expert specialization; TAD selectively distills based on sample characteristics to reduce unreliable/redundant supervision. Official CVPR source: https://openaccess.thecvf.com/content/CVPR2026/html/Kang_UETrack_A_Unified_and_Efficient_Framework_for_Single_Object_Tracking_CVPR_2026_paper.html

**CODE FACT — inspected:** The pinned `uetrack_base.yaml` uses search 224 and template 112, a six-layer `fastitpnt` encoder, eight experts with the configured MoE layer at layer 5, a center decoder, and a frozen ViT-L/14 text encoder for language use. RGB remains a supported inference task; multi-modal training must not be conflated with a mandatory multimodal Core input.

## B. Efficiency facts

**FACT — cited:** Official RGB results report UETrack-B/S/T at 13M/9M/6M parameters and 3.2G/2.5G/1.8G FLOPs. Reported speeds are B: 163 GPU / 56 CPU / 60 AGX FPS; S: 183 / 68 / 67; T: 221 / 83 / 77. Exact paper hardware boundaries must be retained; AGX is not Nano.

**FACT — cited:** UETrack-B reports LaSOT AUC 69.2, TrackingNet AUC 82.7, GOT-10k AO 72.6. S and T trade accuracy for further efficiency. [R21]

## C. Training facts

**CODE FACT — inspected:** The official base configuration is a joint multi-modal training recipe: LaSOT, GOT-10k, COCO, TrackingNet, VASTTrack, TNL2K, OTB99, DepthTrack, VisEvent, and LasHeR; 100k samples/epoch; batch 64; 500 epochs; AdamW.

**RESOURCE AVAILABILITY FACT — cited:** Official backbone and teacher checkpoints are released. The repository documents distributed training with two processes and separately provides a single-GPU debug training command.

**FACT / CODE BOUNDARY:** TAD uses a teacher during training. The paper/repo presents the deployed student as the inference tracker; teacher cost must therefore be treated as training cost, not inference cost.

## D. Benchmark / robustness evidence

**FACT — cited:** UETrack's paper motivation emphasizes that conventional efficient trackers are often RGB-only while multimodal trackers are often too complex for resource-constrained deployment. The paper's main scientific weakness target is thus modality-efficient representation, not a demonstrated generic long-term failure mode.

**OPEN QUESTION:** No sufficiently specific author-reported generic RGB robustness limitation was established in the primary sources inspected for this Manager pass. A candidate-specific failure mode must not be invented from generic tracking difficulty.

## E. Candidate-specific hypotheses

**HYPOTHESIS — untested — computational redundancy:** Because UETrack is already aggressively lightweight (6–13M, 1.8–3.2G reported), remaining generic-RGB redundancy may be limited. A possible remaining area is fixed expert computation/routing, but code audit must establish whether experts are all evaluated, pooled, or conditionally used before this can be treated as a credible hypothesis.

**HYPOTHESIS — untested — robustness weakness:** PENDING. TAD addresses unreliable teacher supervision during training, but that does not by itself establish an inference-time robustness weakness.

**HYPOTHESIS — untested — possible coupling:** PENDING until code execution and a candidate-specific inference weakness are established.

## F. HG4 evidence package — no decision

- Official checkpoints/backbone/teacher are available.
- Single-GPU debug path exists.
- Official full base recipe is long (500 epochs, 100k samples/epoch, batch 64, broad multimodal data), so full reproduction cost and meaningful single-3060 fine-tuning must be distinguished.
- Single-3060 meaningful modification/fine-tuning feasibility remains **PENDING**.

## G. HG5 evidence package — no decision

- Base/S/T variants are structurally small by reported params/FLOPs.
- AGX FPS is evidence only for AGX, not Nano.
- TP-MoE operator implementation and TensorRT/export behavior require code inspection.
- Nano plausibility remains **PENDING**.

## H. Unresolved items

- actual RGB-only execution path and whether text/multimodal branches are bypassed cleanly;
- expert execution/routing cost;
- memory footprint;
- export support/operator risks;
- exact trainable subset and VRAM requirements on 3060.

---

# CX010 — UTPTrack

**Paper:** Hao Wu et al., *UTPTrack: Towards Simple and Unified Token Pruning for Visual Tracking*, CVPR 2026. [R22]  
**Official repository:** `EIT-NLP/UTPTrack@84e0f49711254a44f5308faaa9a2405db1964dd7`. [R23]

## A. Architecture facts

**FACT — cited:** UTPTrack jointly prunes tokens from three components: search region, dynamic template, and static template. It uses attention-guided, token-type-aware pruning and provides both an OSTrack-derived RGB family (`UTPTrack-O`) and a SUTrack-derived unified family (`UTPTrack-S`). Official CVPR source: https://openaccess.thecvf.com/content/CVPR2026/html/Wu_UTPTrack_Towards_Simple_and_Unified_Token_Pruning_for_Visual_Tracking_CVPR_2026_paper.html

**FACT — cited:** The authors report pruning 65.4% of vision tokens for RGB tracking and 67.5% for unified tracking while preserving 99.7% and 100.5% of baseline performance, respectively.

## B. Efficiency facts

**FACT — cited:** The supplementary material exposes explicit token/MAC ablations. For an OSTrack256 baseline with 384 tokens and 34.5G MACs, pruning configurations reduce average/remaining token counts and MACs while keeping average benchmark performance close to baseline; one reported configuration reaches 23.9G MACs with average performance 99.5% of baseline. Official supplement: https://openaccess.thecvf.com/content/CVPR2026/supplemental/Wu_UTPTrack_Towards_Simple_CVPR_2026_supplemental.pdf

**RESOURCE AVAILABILITY FACT — cited:** UTPTrack-O provides profiling commands and states that paper speed numbers were measured on a single RTX 2080 Ti. These numbers are not Nano evidence. [R23]

## C. Training facts

**RESOURCE AVAILABILITY FACT — cited:** UTPTrack-O is built around a ViT-Base/OSTrack path and provides official training/evaluation commands plus checkpoints. The official RGB training example uses four distributed processes; MAE ViT-Base pretraining is the initialization.

**FACT — cited:** The paper/repository uses standard RGB training data (TrackingNet, LaSOT, GOT-10k, COCO) for the RGB branch. Exact single-GPU training cost remains to be extracted from code/configs.

## D. Benchmark / robustness evidence

**FACT — cited:** The paper's central empirical claim is an accuracy-efficiency trade-off from token pruning; it does not establish a distinct generic robustness failure mechanism of UTPTrack itself.

**OPEN QUESTION:** A candidate-specific robustness weakness is not yet established in this Manager pass.

## E. Candidate-specific hypotheses

**INTERPRETATION — reasoned:** UTPTrack is an important novelty adversary for any future proposal based on generic token pruning because it already jointly removes search/static-template/dynamic-template redundancy at high pruning ratios.

**HYPOTHESIS — untested — computational redundancy:** Additional ordinary token pruning may have limited novelty/headroom because the baseline's main contribution already attacks this exact resource. Remaining redundancy must be demonstrated outside or beyond the authors' unified pruning mechanism rather than assumed.

**HYPOTHESIS — untested — robustness weakness:** PENDING.

**HYPOTHESIS — untested — possible coupling:** PENDING; no scientific basis yet to claim a shared efficiency–robustness mechanism beyond the existing pruning framework.

## F. HG4 evidence package — no decision

- Official checkpoints and training path exist.
- RGB family uses ViT-Base and a four-process official command.
- Whether meaningful joint fine-tuning or new-module training is realistic on 12GB depends on actual memory profile/config and remains **PENDING**.

## G. HG5 evidence package — no decision

- Token count/MAC reduction is directly evidenced.
- Paper speed is RTX2080Ti only.
- Dynamic indexing/pruning/gather/scatter behavior and TensorRT compatibility must be inspected before Nano plausibility can be decided.
- HG5 remains **PENDING**.

## H. Unresolved items

- exact representative UTPTrack-O variant/config and its params/MAC/FPS table row;
- dynamic-token tensor shapes and operator pattern;
- runtime memory;
- 3060 training profile;
- candidate-specific robustness weakness.

---

# CX013 — FARTrack

**Paper:** Guijie Wang et al., *FARTrack: Fast Autoregressive Visual Tracking with High Performance*, ICLR 2026. [R11]  
**Official repository:** `MIV-XJTU/FARTrack@5d3e4b90305c2e845340a39cb1ac9bb69c0c5180`. [R12]

## A. Architecture facts

**FACT — cited:** FARTrack is a multi-template autoregressive tracker. Its two main mechanisms are Task-Specific Self-Distillation (TSSD) for shallower models and Inter-frame Autoregressive Sparsification (IFAS) for template-token sparsification across frames. Official ICLR/OpenReview paper: https://openreview.net/forum?id=lq7Zfr8kAS

**FACT — cited:** The released family uses ViT-Tiny at 224² with 15/10/6 layers for Tiny/Nano/Pico. Bounding boxes are represented through autoregressive coordinate/trajectory tokens.

## B. Efficiency facts

**FACT — cited:** Official repository/paper reports Tiny/Nano/Pico speed on Titan Xp at 135/210/343 FPS, Xeon Gold 6230R CPU at 53/77/121 FPS, and Ascend 310B at 42/61/101 FPS. These hardware results are not Jetson Nano measurements.

**FACT — cited:** Tiny/Nano/Pico benchmark results are GOT-10k AO 70.6/69.9/62.8, TrackingNet AUC 80.7/79.1/75.6, and LaSOT AUC 63.2/61.3/58.6. [R12]

**FACT — cited:** The appendix reports a template-count efficiency trade-off for Tiny: one template 1.70G MACs / AO 66.4; five templates 2.65G / AO 70.6; nine templates 3.61G / AO 70.0. Above five templates accuracy no longer improves and can decline, which the authors attribute to redundant templates dispersing attention and interfering with key features.

## C. Training facts

**FACT — cited:** The paper uses 8 NVIDIA RTX A6000 GPUs. Training proceeds through frame-level training, task-specific self-distillation, and inter-frame sparsification. The sparse stage uses continuous video slices; due to author GPU-memory limits each slice contains 32 frames.

**RESOURCE AVAILABILITY FACT — cited:** The official repository provides training/evaluation code and FARTrack / Distill / Sparse checkpoints. [R12]

## D. Benchmark / robustness evidence

**AUTHOR-REPORTED LIMITATION — cited:** The appendix states that after a long tracking failure such as disappearance or occlusion, all templates may become invalid and tracking accuracy can decline. This is a direct author statement, not our inferred failure frequency.

## E. Candidate-specific hypotheses

**HYPOTHESIS — untested — computational redundancy:** FARTrack has already aggressively optimized depth and template tokens. Therefore generic “make it shallower” or “prune more tokens” is unlikely to be sufficient research space. Remaining overhead, if any, must be measured rather than assumed.

**HYPOTHESIS — untested — robustness weakness:** Invalid-template accumulation after prolonged failure/disappearance is a concrete candidate-specific weakness grounded in the authors' appendix.

**HYPOTHESIS — untested — possible coupling:** A mechanism that avoids processing/committing low-value or invalid templates could potentially reduce template computation while mitigating contamination after difficult periods. This is not yet novel and is especially exposed to recent memory-quality/reliability and adaptive-computation prior art; HG6 is not started.

## F. HG4 evidence package — no decision

- Official checkpoints support checkpoint-based research.
- Full author training used 8×A6000 and multi-stage recipes.
- Small final models do not by themselves establish training feasibility; sparse sequence training may be memory-intensive.
- Single-3060 meaningful fine-tuning remains **PENDING** pending code-level batch/sequence and memory evidence.

## G. HG5 evidence package — no decision

- Final models are small and low-MAC relative to many Transformer trackers.
- Existing speed data are Titan Xp/CPU/Ascend, not Nano.
- Autoregressive token operations and IFAS export/operator behavior need code inspection.
- Nano plausibility remains **PENDING**.

## H. Unresolved items

- exact training-memory footprint under reduced batch/sequence length;
- IFAS dynamic operation/export behavior;
- module-level runtime share;
- whether invalid-template weakness occurs often enough and can be reproduced under generic benchmarks.

---

# CX014 — GOT-Edit

**Paper:** Shih-Fang Chen et al., *GOT-Edit: Geometry-Aware Generic Object Tracking via Online Model Editing*, ICLR 2026. [R24]  
**Official repository:** `chenshihfang/GOT@b2ee0b9792db634a880189e8189542953af0d223`. [R25]

## A. Architecture facts

**FACT — cited:** GOT-Edit combines semantic features with geometry inferred from 2D streaming frames through a pretrained Visual Geometry Grounded Transformer (VGGT), then performs online cross-modality model editing with null-space constraints to incorporate geometry while preserving semantic discrimination. Official ICLR proceedings: https://proceedings.iclr.cc/paper_files/paper/2026/hash/519c51529c3544b3430bd8b17d400365-Abstract-Conference.html

**FACT — cited:** The paper uses DINOv2 ViT-L for semantic image features and VGGT geometric features in the primary version. Both semantic and geometry feature extractors are frozen during tracker training. The model predictors/localization head initialize from ToMP-L weights. GOT-Edit-252 and GOT-Edit-378 use 252² and 378² frame resolutions.

## B. Efficiency facts

**FACT — cited:** The paper explicitly reports that the dominant computation is geometric feature extraction. At 252²: VGGT 65.6 ms / 1000G FLOPs, DINO 8.7 ms / 105G, tracker excluding VGGT+DINO 9.8 ms / 32G. At 378²: VGGT 91.9 ms / 2253G, DINO 17.6 ms / 251G, tracker excluding both 17.9 ms / 73G. The authors state the online editing core itself is much lighter than the geometry backbone. Official published PDF: https://chenshihfang.github.io/GOT-EDIT/static/pdfs/ICLR_2026_GOT_Edit.pdf

**FACT — cited:** Primary evaluation on a single RTX 4090 consumes approximately 9 GB GPU memory. The authors additionally evaluate StreamVGGT and fixed less-frequent geometry extraction. For GOT-Edit-252, replacing VGGT and applying geometry every three frames can reduce runtime to roughly 53.9–56.2 ms in reported configurations while retaining competitive accuracy; the 378² table similarly reports fixed every-2/every-3-frame variants. Thus fixed frequency reduction is already author-explored prior art within the same paper.

## C. Training facts

**FACT — cited:** Training uses LaSOT, GOT-10k, TrackingNet, and COCO, with an optional VastTrack variant. The authors train on 8× RTX 4090 24GB; activation checkpointing permits 378² tracker training on four 24GB GPUs. They sample 200k subsequences per epoch for 25 epochs; each subsequence has two reference frames and one current frame; AdamW is used. DINOv2-L and VGGT remain frozen during tracker training.

## D. Benchmark / robustness evidence

**FACT — cited:** GOT-Edit-378 reports strong generic benchmark numbers including LaSOT Success around 75 and TrackingNet Success/AUC 86+ depending on the training variant; protocol details must be preserved when later comparing to other candidates.

**AUTHOR-REPORTED LIMITATION — cited:** The paper states that geometry becomes less effective under fast motion and significant viewpoint change. It reports that the tracker still needs improvement for moving objects/scenes and notes further opportunity under out-of-distribution AVisT conditions.

## E. Candidate-specific hypotheses

**FACT — cited / research-opportunity observation:** Geometry extraction is not merely a suspected bottleneck; the paper directly measures it as the dominant runtime/FLOP component.

**HYPOTHESIS — untested — computational redundancy:** Per-frame full geometry extraction may be unnecessarily expensive in frames where geometry contributes little. However, the authors already evaluate fixed lower-frequency geometry extraction, so “run geometry every N frames” by itself cannot be treated as a new contribution.

**HYPOTHESIS — untested — robustness weakness:** Fast motion/viewpoint change is a concrete author-reported weakness because the geometry signal becomes less effective there.

**HYPOTHESIS — untested — possible coupling:** A state/reliability-conditioned geometry path could in principle spend geometry computation only when geometry is expected to be informative and avoid over-relying on it when fast motion/viewpoint change makes it unreliable. This is stronger than a fixed-frequency idea but remains only a hypothesis and must later survive mechanism-level novelty audit against adaptive computation, reliability routing, and selective geometry/model-update work.

## F. HG4 evidence package — no decision

- Official models and code exist.
- Backbone feature extractors are frozen in the authors' tracker training, which may reduce trainable-memory cost relative to full end-to-end tuning.
- Author training still uses 8×4090; even activation-checkpointed 378² training is reported on four 24GB GPUs.
- Single-RTX3060 meaningful research feasibility depends on whether new modules can be trained/fine-tuned without reproducing full author-scale geometry processing and remains **PENDING**.

## G. HG5 evidence package — no decision

- Reported inference uses ~9GB on RTX4090, already above Nano's total 4GB shared memory if taken at face value, but cross-device memory behavior is not directly comparable and no Nano failure claim is made from this number alone.
- Geometry path has 1000–2253G FLOPs per frame in the primary configurations and dominates runtime.
- The authors already demonstrate StreamVGGT/frequency reduction, giving evidence that geometry frequency is an explicit efficiency control variable.
- Actual TensorRT/operator/memory feasibility on Nano remains **PENDING** pending code audit; structural risk is high enough to require special scrutiny.

## H. Unresolved items

- exact deployable dependency graph for DINOv2-L + VGGT/Depth-Anything-3 + tracker;
- whether geometry can be cached/exported without unsupported dynamic behavior;
- actual memory peak by component;
- feasible 3060 research loop with frozen/unfrozen choices;
- whether a reliability-conditioned geometry mechanism is distinct enough from the paper's own fixed-frequency StreamVGGT ablation and 2023–2026 adaptive-computation work.

---

# Batch A Manager summary — no ranking

| Candidate | Evidence-grounded strength | Evidence-grounded concern | Candidate-specific hypothesis status |
|---|---|---|---|
| SpikeTrack | SNN efficiency + explicit memory retrieval; author identifies similar-object weakness | SNN efficiency may not map efficiently to conventional Maxwell CUDA; author training 8×4090 | Similar-distractor robustness + possible state-dependent fine-grained compute — **HYPOTHESIS** |
| UETrack | Very small reported model/FLOPs; RGB + multimodal support; teacher absent at inference | Already highly optimized; no specific generic RGB failure established yet | Redundancy/weakness/coupling still weak — **PENDING/HYPOTHESIS** |
| UTPTrack | Directly measured large token pruning with near-baseline accuracy | Main contribution already consumes much of obvious token-redundancy headroom | Further ordinary pruning likely weak as research space — **INTERPRETATION/HYPOTHESIS** |
| FARTrack | Tiny/Nano/Pico efficiency; template-count ablations; author limitation on invalid templates | Already optimized by depth distillation + temporal token sparsification | Invalid-template validity/compute coupling is testable but novelty-risky — **HYPOTHESIS** |
| GOT-Edit | Strong generic accuracy; measured geometry bottleneck; author-reported fast-motion/viewpoint weakness | Extremely large primary geometry cost; fixed-frequency geometry reduction already explored | Reliability-conditioned selective geometry is testable but unproven and novelty-sensitive — **HYPOTHESIS** |

This table is **not a score or preference ranking**.

## Batch A handoff boundary

Manager evidence extraction is complete. Next required step is the independent Codex code/engineering audit of these same five pinned candidates. After that, Manager must reconcile paper facts and code facts field by field. Only reconciled evidence may be used to decide HG4/HG5. HG6 and S1–S7 remain out of scope.
