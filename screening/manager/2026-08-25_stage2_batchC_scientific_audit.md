# Stage 2A — Batch C Manager scientific audit

**Date:** 2026-08-25  
**Lane:** Manager — paper/scientific evidence  
**Batch:** C active candidates only — CX043, CX044, CX049  
**Status:** MANAGER EVIDENCE EXTRACTION COMPLETE; Codex code/engineering audit and batch reconciliation still required.  
**Governing protocol:** `docs/11_systematic_screening_protocol.md` and `screening/manager/2026-08-24_stage2_deep_audit_framework.md`.

## Scope and non-claims

The original Batch C also contained MambaLCT and JDTrack. They are not active here because final early-gate reconciliation left MambaLCT at HG3 FAIL and JDTrack at HG3 PENDING. This Manager audit therefore processes only the three HG3-PASS candidates in canonical-ID order:

1. CX043 — SUTrack
2. CX044 — AsymTrack
3. CX049 — SPMTrack

This file extracts paper-level scientific evidence and explicitly labeled hypotheses. It does **not** decide HG4/HG5, begin HG6, assign S1–S7, rank candidates, shortlist a baseline, or design a proposed architecture.

---

# CX043 — SUTrack

**Paper:** Xin Chen et al., *SUTrack: Towards Simple and Unified Single Object Tracking*, AAAI 2025. [R37]  
**Official repository:** `chenxin-dlut/SUTrack@d65052d1…`. [R38]

Primary publication: https://ojs.aaai.org/index.php/AAAI/article/view/32223  
Official repository: https://github.com/chenxin-dlut/SUTrack

## A. Architecture / task facts

**FACT — cited:** SUTrack unifies five SOT tasks — RGB, RGB-Depth, RGB-Thermal, RGB-Event, and RGB-Language — into one model and one training session. Its contribution is a unified representation/training framework rather than five task-specific architectures.

**FACT — cited:** The paper introduces task-recognition training and soft token-type embedding with minimal overhead. The official repository describes a Transformer-encoder-based unified tracker and releases Base/Large/Tiny-style pretrained backbones and tracker checkpoints.

**FACT / SCOPE BOUNDARY:** RGB tracking is an explicitly supported inference task, so the generic Core can be evaluated RGB-only. The existence of multimodal training/results must not be treated as a mandatory multimodal Core input.

## B. Benchmark / efficiency facts

**RESOURCE AVAILABILITY FACT:** The official repository reports RGB results of LaSOT AUC 75.2, GOT-10k AO 81.5, and TrackingNet AUC 87.7 for the high-performance family, and separately reports an efficient SUTrack-T224 variant at LaSOT 69.6 / GOT-10k 72.7 / TrackingNet 82.7 with 23 CPU FPS and 34 Jetson AGX FPS. These AGX values are not Jetson Nano evidence.

**INTERPRETATION — reasoned:** SUTrack has both strong-performance and edge-oriented variants in one method family, so the baseline family spans a wider accuracy/efficiency range than a single fixed heavy configuration.

## C. Training facts

**RESOURCE AVAILABILITY FACT:** The repository provides official pretrained Fast-iTPN backbones, four-process training for `sutrack_b224`, and a single-GPU debug path. The training data pool includes standard RGB datasets and multimodal datasets for unified training.

**OPEN QUESTION:** The Manager pass does not establish whether a controlled RGB-only fine-tuning recipe is officially provided or whether the main published model depends materially on joint multimodal training for its RGB result. Codex must separate inference modality from training-data cost.

## D. Robustness evidence

**FACT — cited:** SUTrack's scientific motivation is fragmentation across SOT modalities and duplicated task-specific designs, not a specific residual RGB failure mode such as occlusion, distractor drift, or long disappearance.

**OPEN QUESTION:** No sufficiently specific author-reported remaining RGB robustness weakness was established in the primary source inspected for this pass.

## E. Candidate-specific hypotheses

**HYPOTHESIS — untested — computational redundancy:** The unified model may execute task/modality machinery that is unnecessary for RGB-only inference, or it may already bypass most such machinery. Code inspection is required before this can be considered a real efficiency opportunity.

**HYPOTHESIS — untested — robustness weakness:** PENDING. A candidate-specific RGB failure must be established experimentally or from stronger source evidence.

**HYPOTHESIS — untested — possible coupling:** PENDING. It would be premature to claim that modality/task recognition can serve as a reliability/compute controller in generic RGB tracking.

## F. HG4 evidence package — no decision

- official checkpoints and pretrained backbones exist;
- a single-GPU debug path exists;
- the full unified training recipe may be data- and compute-heavy;
- meaningful single-3060 modification/fine-tuning remains **PENDING** pending code/config audit.

## G. HG5 evidence package — no decision

- an explicit Tiny/224 edge-oriented variant exists;
- AGX speed is not Nano speed;
- RGB-path operator execution, token count, task-recognition overhead and exportability require code inspection;
- HG5 remains **PENDING**.

---

# CX044 — AsymTrack

**Paper:** Jiawen Zhu et al., *Two-stream Beats One-stream: Asymmetric Siamese Network for Efficient Visual Tracking*, AAAI 2025. [R39]  
**Official repository:** `jiawen-zhu/AsymTrack@a7b05e0c…`. [R40]

Primary publication: https://ojs.aaai.org/index.php/AAAI/article/view/33191  
Official repository: https://github.com/jiawen-zhu/AsymTrack

## A. Architecture facts

**FACT — cited:** AsymTrack is explicitly designed around a compute inefficiency of one-stream trackers: re-computing template features every frame. It separates template and search branches so the template branch runs only once during initialization; extracted template features/modulation cues are then injected unidirectionally into the online search branch.

**FACT — cited:** The method adds Efficient Template Modulation (ETM) and Object Perception Enhancement (OPE). OPE uses re-parameterization so its training-time multi-branch representation is folded into an equivalent single convolutional branch at inference.

## B. Efficiency facts

**FACT — cited:** The paper reports three variants:

- AsymTrack-T: 3.05M parameters, 0.7G FLOPs, 224 GPU / 81 CPU / 84 AGX FPS;
- AsymTrack-S: 3.36M parameters, 0.8G FLOPs, 200 / 75 / 78 FPS;
- AsymTrack-B: 3.36M parameters, 1.8G FLOPs, 197 / 38 / 64 FPS.

GPU = RTX 2080 Ti and edge platform = Jetson AGX Xavier in the paper. None of these figures is Jetson Nano performance.

**FACT — cited:** Template/search sizes are 128/256 for T/S and 192/384 for B. The template branch is initialization-only at inference.

## C. Training facts

**FACT — cited:** The paper trains on LaSOT, TrackingNet, COCO2017 and GOT-10k for 500 epochs with AdamW on 2 NVIDIA A800 GPUs, 60,000 sampled image pairs per epoch. The official repository also exposes a single-GPU debug path.

## D. Benchmark / robustness evidence

**AUTHOR-REPORTED GAP — cited:** The paper explicitly performs a gap analysis against precision-oriented trackers. The largest average LaSOT attribute gaps are reported under **low resolution, viewpoint change, and fast motion**, which the authors link to limited representation capability in the efficient model family.

**FACT — cited:** The paper also reports strong NFS results, so “fast motion is always a failure” would be too strong. The evidence supports a relative performance gap versus stronger precision-oriented trackers, not universal failure.

## E. Candidate-specific hypotheses

**INTERPRETATION — reasoned:** The obvious template-recomputation redundancy is already the baseline's own solved problem. A contribution that merely caches the template or switches from one-stream to asymmetric Siamese would directly collide with AsymTrack.

**HYPOTHESIS — untested — computational redundancy:** Because AsymTrack is already only 3.05–3.36M parameters and 0.7–1.8G reported FLOPs, remaining large generic compute redundancy may be limited. Code audit should test whether ETM/OPE/search-stage work contains any conditional or repeated computation not already optimized.

**HYPOTHESIS — untested — robustness weakness:** Representation loss under low resolution/viewpoint change/fast motion is a concrete candidate-specific research signal supported by the authors' gap analysis.

**HYPOTHESIS — untested — possible coupling:** A useful shared efficiency–robustness mechanism is not yet obvious. Increasing representation only on difficult frames could be hypothesized, but that would collide strongly with adaptive-computation prior art and must not be promoted before code audit/HG6.

## F. HG4 evidence package — no decision

- official models/checkpoints exist;
- the architecture is extremely small by reported parameter/FLOP scale;
- official training uses 2 A800 GPUs but a single-GPU debug path exists;
- meaningful single-3060 training/fine-tuning appears structurally plausible but remains **PENDING** until code/config evidence is reconciled.

## G. HG5 evidence package — no decision

- edge-oriented design is the paper's explicit objective;
- template computation is removed from steady-state inference;
- model sizes/FLOPs are very small and AGX tests exist, but AGX cannot establish Nano speed;
- exact operator/export/runtime behavior still requires Codex inspection;
- HG5 remains **PENDING**.

---

# CX049 — SPMTrack

**Paper:** Wenrui Cai, Qingjie Liu, Yunhong Wang, *SPMTrack: Spatio-Temporal Parameter-Efficient Fine-Tuning with Mixture of Experts for Scalable Visual Tracking*, CVPR 2025. [R43]  
**Official repository:** `WenRuiCai/SPMTrack@c581fe27…`. [R44]

Primary publication: https://openaccess.thecvf.com/content/CVPR2025/html/Cai_SPMTrack_Spatio-Temporal_Parameter-Efficient_Fine-Tuning_with_Mixture_of_Experts_for_Scalable_CVPR_2025_paper.html  
Official repository: https://github.com/WenRuiCai/SPMTrack

## A. Architecture facts

**FACT — cited:** SPMTrack introduces a tracking-specific Mixture-of-Experts mechanism (TMoE) to model heterogeneous patch relations and extends relation modeling from image pairs to spatio-temporal context.

**FACT — cited:** TMoE is also used as a parameter-efficient fine-tuning mechanism: the goal is to keep large pretrained model knowledge while training only a smaller subset/adapter-style expert parameters rather than fully tuning all backbone weights.

## B. Scale / efficiency facts

**RESOURCE AVAILABILITY FACT:** The official repository reports:

- SPMTrack-B: 115.3M total / 29.2M trainable parameters;
- SPMTrack-L: 379.6M / 75.9M trainable;
- SPMTrack-G: 1339.5M / 204.0M trainable.

The repo reports B at LaSOT 74.9, GOT-10k AO 76.5, TrackingNet 86.1; larger variants improve accuracy further. At the screening snapshot only the B trained checkpoint is clearly released, while L/G release remains marked pending.

**FACT / BOUNDARY:** Parameter-efficient fine-tuning reduces trainable parameters, not necessarily inference parameters or per-frame FLOPs. A 115.3M inference model must not be called lightweight merely because only 29.2M parameters are trainable.

**RESOURCE AVAILABILITY FACT:** The repository notes that compute varies with the number of reference frames and that the code calculates FLOPs during operation. This makes temporal-reference cost an explicit audit target.

## C. Training facts

**RESOURCE AVAILABILITY FACT:** The official implementation uses PyTorch 2.3.1/CUDA12, supports multi-GPU/multi-node launch, and provides evaluation-only workflows. It reports NaN instability can occur and suggests disabling `torch.compile` when needed.

**OPEN QUESTION:** The Manager pass does not establish a verified single-GPU recipe, per-device batch, frozen/trainable layer map, or whether B can be meaningfully trained/fine-tuned within 12 GB without aggressive compromises. Codex must inspect the actual configuration.

## D. Robustness evidence

**FACT — cited:** The paper motivation is heterogeneous relation modeling across foreground/background and temporal references. It argues that a single model may not handle all relation types equally well.

**OPEN QUESTION:** No sufficiently specific remaining failure mode of the final SPMTrack system was established. The paper primarily demonstrates performance improvements rather than documenting a residual robustness limitation.

## E. Candidate-specific hypotheses

**HYPOTHESIS — untested — computational redundancy:** TMoE expert execution and the number of temporal reference frames may create substantial inference cost, but the actual expert routing/execution behavior and reference-feature reuse must be established from code. PEFT itself is a training-cost mechanism, not evidence of inference redundancy.

**HYPOTHESIS — untested — robustness weakness:** PENDING.

**HYPOTHESIS — untested — possible coupling:** If reference/expert computation is always-on while relation difficulty varies, conditional expert/reference execution could be a candidate mechanism; however MoE routing and adaptive-compute literature create a high novelty-collision risk, so this remains only a hypothesis.

## F. HG4 evidence package — no decision

- only the B checkpoint is clearly available in the pinned release;
- B has 115.3M total but 29.2M trainable parameters;
- parameter-efficient fine-tuning is favorable for research feasibility, but actual activation/optimizer memory and batch settings remain unknown;
- HG4 remains **PENDING** pending code audit.

## G. HG5 evidence package — no decision

- B is still a 115.3M inference model;
- temporal reference count changes FLOPs;
- expert execution/routing, token shapes, reference caching and exportability are unresolved;
- no Nano inference claim is made;
- HG5 remains **PENDING**.

---

## Batch-C Manager state

- CX043 SUTrack — Manager scientific evidence: **COMPLETE**
- CX044 AsymTrack — Manager scientific evidence: **COMPLETE**
- CX049 SPMTrack — Manager scientific evidence: **COMPLETE**

HG4/HG5 remain undecided until independent Codex code evidence is reconciled. Batch D remains locked. HG6 and soft scoring remain not started.
