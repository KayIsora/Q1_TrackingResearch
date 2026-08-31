# Donor mechanism audit — V1.2

This supplement records the four mandatory new audits. The 15 re-opened cards and these four additions are normalized in `04_high_relevance_paper_cards.md`. No model was run, trained, profiled, or selected.

## ABTrack — static lesson inside a deferred dynamic paper

ABTrack combines two different reduction mechanisms [E32]. Its **ViT Pruning (VTP)** is static: trainable diagonal selectors are placed in attention and MLP latent dimensions, optimized with L1 sparsity, locally ranked per block, binarized at a fixed pruning ratio, physically removed, and fine-tuned. Its **Bypass Decision Module (BDM)** is dynamic: blocks after an always-executed prefix receive a bypass token, a linear/sigmoid score, and a thresholded execute/bypass choice. The adaptive block-sparsity target is adjusted using tracking difficulty derived from GIoU relative to the batch/average difficulty. The full objective adds the block-sparsity term to focal, GIoU, and L1 tracking losses.

The BDM exists because deciding at every block has overhead; VTP reduces that overhead by shrinking the blocks that remain. This makes ABTrack a strong collision for adaptive block routing and a useful engineering lesson for physical latent-dimension reduction. It is **not** evidence for SpikeTrack MRM skipping. The dynamic path remains deferred; only the static “train selectors, materialize a smaller graph, then measure the real artifact” principle transfers.

## UETrack — what “adaptive” distillation actually means

UETrack targets unified RGB/depth/thermal/event/language tracking, using a Fast-iTPN-T student and SUTrack-B teacher [E33]. Selected FFNs are replaced by **Token-Pooling-based Mixture-of-Experts**: local token aggregation creates compact token evidence, token/expert similarity produces soft parallel assignments, and there is no hard one-expert inference gate. This adds representational capacity and is not automatically aligned with a minimal RGB edge objective.

**Target-aware Adaptive Distillation (TAD)** is training-sample adaptation, not inference-time routing. An adaptive network observes teacher/student evidence and produces a binary decision through Gumbel sampling; output KL and feature MSE supervision are enabled only when the teacher signal is judged beneficial. The paper's stated loss uses focal + 2 GIoU + 5 L1, KL KD weight 5, and feature MSE weight 0.002. Teacher, adaptive controller, and KD targets are removed at inference; TP-MoE remains.

Transfer to RGB-only SpikeTrack is therefore at the principle level: do not force uniform teacher imitation when the teacher is unreliable or mismatched; preserve task outputs and selected internal behavior. Copying RGB-X tokenization, CLIP, TP-MoE, or SUTrack features would change the problem and likely conflict with the edge objective.

## ZoomTrack — spatial reduction without shrinking the field of view

ZoomTrack leaves the base tracker unchanged and reduces search-image sampling [E34]. A temporal prior from the previous box defines likely target location; a quadratic program determines a non-uniform deformation, implemented by bilinear sampling on a 17x17 control grid. Likely target regions receive more output samples while other regions are compressed, and predicted boxes are mapped back to source coordinates. The transform is used in training and inference.

The paper reports roughly 21.5G versus 41.5G MACs, 50–52% faster execution, and OSTrack-Zoom at 73.5 GOT-10k AO, 70.2 LaSOT AUC, and 100 FPS on V100. These are primary-paper results, not SpikeTrack/device estimates. The QP/sampling cost is reported small in that setup, but integration cost and target-prior failure must be measured on the actual deployment path. The distinct transferable lesson is: reduce spatial work while explicitly protecting likely target detail and the original field of view.

## P027 HKDT — Hybrid-KD Pruning Tracker — highest-priority collision

The accessible publisher abstract names the tracker **HKDT** and establishes the following [E35]: lightweight tracking backbones are argued to retain structural redundancy; the method combines **static backbone pruning** with **Hybrid Knowledge Distillation**; Token Distillation separately aligns Q/K/V; Local Distillation uses spatial foreground/background masks; Global Distillation uses Vision Mamba for long-range/semantic alignment. It reports GOT-10k AO 67.6, +3.6 over HiT-Base, 64% lower computational cost, and 115% faster CPU tracking.

The full paper was not openly retrievable during this audit. Consequently, these requested details remain `UNKNOWN`: exact backbone, teacher/student identities, pruned layer names/indices, pruning criterion/schedule, whether width is also changed, formulas and weights, retraining phases, parameter/FLOP/FPS tables, CPU protocol, and any edge-device measurement. Abstract wording supports static pruning, not adaptive inference routing.

### Collision answer

This paper is the **highest generic-family novelty collision** because it is extremely close at the conceptual level: **static structural pruning + tracking-specific multi-level KD**. That classification does not prove that every SpikeTrack-native mechanism is occupied. A future claim stated only as “prune SpikeTrack and use tracking-specific KD” would be weak and potentially too close. Plausible novelty headroom requires a SpikeTrack-native scientific question, for example whether a fixed structural reduction can preserve:

- NI-LIF temporal/state dynamics and spike-distribution behavior;
- the six template K-transpose-V memory interfaces and retrieval behavior;
- target-facing center/size/offset behavior under spike-specific representation loss;
- useful sparse/event-like computation after the reduced graph is materialized.

Those are unresolved questions, not a selected architecture. A contribution would need causal evidence that the SNN-native preservation target matters beyond ordinary logits/features/masks, plus a physical smaller artifact and honest target-device measurement.

## Optional candidates

The HiT/DyHiT extension and “enhanced two-stream” variants do not add a distinct presentation mechanism beyond HiT + DyTrack and AsymTrack/LiteTrack for this drawing. They are not promoted merely to enlarge the graph.
