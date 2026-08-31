# Drawing-ready node content — V1.2

The catalog recommends **17 visible tracker/paper nodes**. Text is deliberately callout-sized. `19_presentation_role_catalog.csv` is the authority for visibility and one primary role per paper.

## N_FAR

- **NODE ID:** N_FAR
- **DISPLAY NAME:** FARTrack
- **YEAR/VENUE:** 2026 / ICLR
- **PRIMARY ROLE:** ANCHOR
- **PROBLEM:** Fast high-accuracy autoregressive tracking.
- **CORE ARCHITECTURE:** ViT-Tiny one-stream encoder with template/search/command tokens.
- **KEY MECHANISM:** Adjacent-depth TSSD + persistent IFAS template mask.
- **EFFICIENCY ACTION:** Fixed 15→10→6 layer options; retain 75% template tokens.
- **TRAINING/LOSS:** CE + SIoU + adjacent KL; staged sparsification.
- **MAIN LESSON:** Preserve task outputs while reducing a fixed structure; amortize stable decisions.
- **RELATION TO FARTRACK:** Fixed methodology anchor.
- **RELATION TO SPIKETRACK:** Principle donor, not component blueprint.
- **CAUTION / NOVELTY COLLISION:** Shallow task-KD and temporal sparsity already claimed.
- **EVIDENCE:** [E03, E04].

## N_SPIKE

- **NODE ID:** N_SPIKE
- **DISPLAY NAME:** SpikeTrack
- **YEAR/VENUE:** 2026 / CVPR
- **PRIMARY ROLE:** ANCHOR
- **PROBLEM:** Efficient RGB tracking through spike-driven computation.
- **CORE ARCHITECTURE:** Separate spiking template/search encoders, six K-transpose-V caches/MRMs, center-size-offset head.
- **KEY MECHANISM:** NI-LIF, linear spike attention, asymmetric cached template memory.
- **EFFICIENCY ACTION:** Reuse compact template memory; multiplication-light spike computation.
- **TRAINING/LOSS:** T1 training/T3 fine-tuning; focal + 2 GIoU + 5 L1.
- **MAIN LESSON:** Reduction must preserve target behavior and spike/state/cache function.
- **RELATION TO FARTRACK:** Receives general lightweight-design principles.
- **RELATION TO SPIKETRACK:** Fixed redesign target.
- **CAUTION / NOVELTY COLLISION:** Analytical energy is not device power; MRM1 skip is `DIAG_FAIL`, hold-out consumed.
- **EVIDENCE:** [E05-E08, E23, E24].

## N_COMPRESS

- **NODE ID:** N_COMPRESS
- **DISPLAY NAME:** CompressTracker
- **YEAR/VENUE:** 2025 / ICCV
- **PRIMARY ROLE:** PRIMARY_DONOR
- **PROBLEM:** Heterogeneous tracker compression without tying student structure to teacher.
- **CORE ARCHITECTURE:** Teacher divided into stages matched to cheaper student stages.
- **KEY MECHANISM:** Random teacher/student stage replacement, prediction guidance, stage feature mimic.
- **EFFICIENCY ACTION:** Assemble fewer/cheaper student stages for inference.
- **TRAINING/LOSS:** Original task loss + prediction and stage-feature supervision.
- **MAIN LESSON:** Make compression stage-local and task-facing.
- **RELATION TO FARTRACK:** Extends adjacent-depth distillation.
- **RELATION TO SPIKETRACK:** Supporting training donor for a fixed reduced graph.
- **CAUTION / NOVELTY COLLISION:** Conventional feature equality may not respect spike state.
- **EVIDENCE:** [E10].

## N_MIX

- **NODE ID:** N_MIX
- **DISPLAY NAME:** MixFormerV2
- **YEAR/VENUE:** 2023 / NeurIPS
- **PRIMARY ROLE:** PRIMARY_DONOR
- **PROBLEM:** Efficient fully transformer tracking.
- **CORE ARCHITECTURE:** One-stream MixViT with four sparse prediction tokens.
- **KEY MECHANISM:** Dense-to-sparse head distillation + progressive deep-to-shallow distillation.
- **EFFICIENCY ACTION:** Remove dense corner head, backbone layers, optional MLP width.
- **TRAINING/LOSS:** Task loss plus teacher logit/depth supervision.
- **MAIN LESSON:** Progressive fixed-depth reduction can preserve task distributions.
- **RELATION TO FARTRACK:** Direct methodological precursor/collision.
- **RELATION TO SPIKETRACK:** Strong static student-training donor.
- **CAUTION / NOVELTY COLLISION:** Generic deep-to-shallow KD is occupied.
- **EVIDENCE:** [E11].

## N_LITE

- **NODE ID:** N_LITE
- **DISPLAY NAME:** LiteTrack
- **YEAR/VENUE:** 2024 / ICRA
- **PRIMARY ROLE:** PRIMARY_DONOR
- **PROBLEM:** Repeated template work and excess ViT depth.
- **CORE ARCHITECTURE:** Pruned FE stage + asynchronous interaction stage.
- **KEY MECHANISM:** Top-down layer pruning and template-once caching.
- **EFFICIENCY ACTION:** Remove upper layers and repeated template extraction.
- **TRAINING/LOSS:** End-to-end; focal + GIoU + L1.
- **MAIN LESSON:** Separate initialization-only and per-frame workloads in a fixed smaller graph.
- **RELATION TO FARTRACK:** Supports fixed depth and amortization.
- **RELATION TO SPIKETRACK:** Structural donor; cache reuse itself is already present.
- **CAUTION / NOVELTY COLLISION:** Asynchronous template extraction is not new for SpikeTrack.
- **EVIDENCE:** [E12].

## N_UE

- **NODE ID:** N_UE
- **DISPLAY NAME:** UETrack
- **YEAR/VENUE:** 2026 / CVPR
- **PRIMARY ROLE:** PRIMARY_DONOR
- **PROBLEM:** Efficient unified RGB-X tracking.
- **CORE ARCHITECTURE:** Fast-iTPN-T student, SUTrack-B teacher, TP-MoE.
- **KEY MECHANISM:** TAD gates output/feature KD per training sample using a binary adaptive decision.
- **EFFICIENCY ACTION:** One compact unified student; teacher/TAD controller removed at inference.
- **TRAINING/LOSS:** Focal + 2 GIoU + 5 L1; gated KL (5) + feature MSE (0.002).
- **MAIN LESSON:** Teacher imitation can be task/sample aware rather than uniform.
- **RELATION TO FARTRACK:** Generalizes task-facing distillation.
- **RELATION TO SPIKETRACK:** Training donor if signals are redefined for spike behavior.
- **CAUTION / NOVELTY COLLISION:** TP-MoE/multimodal paths add edge complexity and do not transfer.
- **EVIDENCE:** [E33].

## N_LORE

- **NODE ID:** N_LORE
- **DISPLAY NAME:** LoReTrack
- **YEAR/VENUE:** 2025 / IROS
- **PRIMARY ROLE:** SEMANTIC_BRIDGE
- **PROBLEM:** Recover information lost by lower-resolution tracking.
- **CORE ARCHITECTURE:** Frozen high-resolution OSTrack teacher + low-resolution student.
- **KEY MECHANISM:** Search-only Q/K/V MSE + target-weighted discrimination KD.
- **EFFICIENCY ACTION:** Reduce spatial tokens/MACs.
- **TRAINING/LOSS:** Classification/regression + QKV-KD + Disc-KD.
- **MAIN LESSON:** A reduced representation needs interaction-level and target/background preservation.
- **RELATION TO FARTRACK:** Reduction + task-facing preservation.
- **RELATION TO SPIKETRACK:** Functional bridge to representation-preserving SNN reduction.
- **CAUTION / NOVELTY COLLISION:** Generic low-resolution tracking KD is occupied.
- **EVIDENCE:** [E15].

## N_HIT

- **NODE ID:** N_HIT
- **DISPLAY NAME:** HiT
- **YEAR/VENUE:** 2023 / ICCV
- **PRIMARY ROLE:** SEMANTIC_BRIDGE
- **PROBLEM:** Preserve tracking detail in a cheap hierarchical backbone.
- **CORE ARCHITECTURE:** LeViT hierarchy + deep-to-shallow Bridge Module.
- **KEY MECHANISM:** Fuse deep semantics into shallow high-resolution features; dual-image position encoding.
- **EFFICIENCY ACTION:** Replace a heavy flat backbone.
- **TRAINING/LOSS:** End-to-end tracking loss.
- **MAIN LESSON:** Pair structural reduction with explicit information repair.
- **RELATION TO FARTRACK:** Fixed lightweight structure reference.
- **RELATION TO SPIKETRACK:** Functional stage-design bridge at principle level.
- **CAUTION / NOVELTY COLLISION:** LeViT/Bridge transplant is not SNN evidence.
- **EVIDENCE:** [E18].

## N_ASYM

- **NODE ID:** N_ASYM
- **DISPLAY NAME:** AsymTrack
- **YEAR/VENUE:** 2025 / AAAI
- **PRIMARY ROLE:** SECONDARY_DONOR
- **PROBLEM:** Remove per-frame template/interaction redundancy.
- **CORE ARCHITECTURE:** Initialization-only template branch + per-frame search branch.
- **KEY MECHANISM:** Efficient Template Modulation + reparameterized Object Perception Enhancement.
- **EFFICIENCY ACTION:** Reuse template modulation; remove repeated template branch.
- **TRAINING/LOSS:** End-to-end; OPE branches folded for inference.
- **MAIN LESSON:** Stable template evidence should not dominate per-frame work.
- **RELATION TO FARTRACK:** Supports persistent template decisions.
- **RELATION TO SPIKETRACK:** Confirms asymmetry but warns against direct modulation.
- **CAUTION / NOVELTY COLLISION:** SpikeTrack paper reports simple modulation unsuitable for coarse spikes.
- **EVIDENCE:** [E05, E09].

## N_ZOOM

- **NODE ID:** N_ZOOM
- **DISPLAY NAME:** ZoomTrack
- **YEAR/VENUE:** 2023 / NeurIPS
- **PRIMARY ROLE:** SECONDARY_DONOR
- **PROBLEM:** Lower input cost without losing target detail/field of view.
- **CORE ARCHITECTURE:** Model-agnostic search-warp wrapper.
- **KEY MECHANISM:** Previous-box prior + QP non-uniform resize + 17x17 bilinear grid.
- **EFFICIENCY ACTION:** Reduce search samples/MACs, not model layers.
- **TRAINING/LOSS:** Warp in train/test; source-coordinate regression.
- **MAIN LESSON:** Protect likely target density when reducing spatial work.
- **RELATION TO FARTRACK:** Secondary representation-reduction reference.
- **RELATION TO SPIKETRACK:** Orthogonal spatial direction.
- **CAUTION / NOVELTY COLLISION:** Prior error and integration cost need target-device evidence.
- **EVIDENCE:** [E34].

## N_MCI

- **NODE ID:** N_MCI
- **DISPLAY NAME:** MCITrack
- **YEAR/VENUE:** 2025 / AAAI
- **PRIMARY ROLE:** SECONDARY_DONOR
- **PROBLEM:** Insufficient video-level context.
- **CORE ARCHITECTURE:** Mamba contextual state + cross-attention.
- **KEY MECHANISM:** Compact recurrent state carries historical evidence.
- **EFFICIENCY ACTION:** Reuse summarized history instead of raw frames; adds a module.
- **TRAINING/LOSS:** End-to-end contextual-state training.
- **MAIN LESSON:** Compact memory quality can matter more than memory volume.
- **RELATION TO FARTRACK:** Context-memory reference.
- **RELATION TO SPIKETRACK:** Cache-quality donor.
- **CAUTION / NOVELTY COLLISION:** Added state/attention may increase latency.
- **EVIDENCE:** [E16].

## N_STD

- **NODE ID:** N_STD
- **DISPLAY NAME:** STDTrack
- **YEAR/VENUE:** 2026 / AAAI
- **PRIMARY ROLE:** SECONDARY_DONOR
- **PROBLEM:** Unreliable temporal evidence.
- **CORE ARCHITECTURE:** Quality-filtered temporal tokens + reparameterized head.
- **KEY MECHANISM:** Maintain reliable memory; fold training branches for inference.
- **EFFICIENCY ACTION:** Reuse selected state and simplify head graph.
- **TRAINING/LOSS:** Tracking/reliability objectives; structural reparameterization.
- **MAIN LESSON:** Validate state quality before persistent reuse.
- **RELATION TO FARTRACK:** Caution for persistent mask/template decisions.
- **RELATION TO SPIKETRACK:** Cache-update quality donor without MRM skipping.
- **CAUTION / NOVELTY COLLISION:** External to both exports; dense mechanism not directly portable.
- **EVIDENCE:** [E21].

## N_SPIKEFET

- **NODE ID:** N_SPIKEFET
- **DISPLAY NAME:** SpikeFET
- **YEAR/VENUE:** 2025 / NeurIPS
- **PRIMARY ROLE:** SECONDARY_DONOR
- **PROBLEM:** Fully spiking frame-event tracking.
- **CORE ARCHITECTURE:** Multimodal spiking feature/fusion tracker.
- **KEY MECHANISM:** Spike spatial-temporal regularization.
- **EFFICIENCY ACTION:** Exploit spike/event sparsity.
- **TRAINING/LOSS:** Tracker loss + SNN spatial-temporal regularizer.
- **MAIN LESSON:** Compression supervision may need to preserve spike dynamics.
- **RELATION TO FARTRACK:** Minimal.
- **RELATION TO SPIKETRACK:** SNN-native training donor.
- **CAUTION / NOVELTY COLLISION:** Event modality changes the problem.
- **EVIDENCE:** [E20].

## N_CPDA

- **NODE ID:** N_CPDA
- **DISPLAY NAME:** CPDATrack
- **YEAR/VENUE:** 2026 / JVCIR
- **PRIMARY ROLE:** NOVELTY_COLLISION
- **PROBLEM:** Background/distractor token waste.
- **CORE ARCHITECTURE:** One-stream tracker with token selector and directional attention.
- **KEY MECHANISM:** Target-probability pruning + discriminative selective attention.
- **EFFICIENCY ACTION:** Conditionally remove search tokens/attention.
- **TRAINING/LOSS:** Joint selector/tracker training; exact weights UNKNOWN.
- **MAIN LESSON:** Target evidence must survive pruning.
- **RELATION TO FARTRACK:** Collision on attention-derived sparsity.
- **RELATION TO SPIKETRACK:** Principle only; not MRM-skip evidence.
- **CAUTION / NOVELTY COLLISION:** Selector overhead and topology mismatch.
- **EVIDENCE:** [E19].

## N_AB

- **NODE ID:** N_AB
- **DISPLAY NAME:** ABTrack
- **YEAR/VENUE:** 2025 / Pattern Recognition
- **PRIMARY ROLE:** NOVELTY_COLLISION
- **PROBLEM:** Redundant ViT blocks and routing overhead.
- **CORE ARCHITECTURE:** Static latent-dimension pruning + dynamic block BDMs.
- **KEY MECHANISM:** GIoU-difficulty sparsity target; local-rank physical Q/K/V/MLP pruning.
- **EFFICIENCY ACTION:** Shrink blocks, then conditionally bypass later blocks.
- **TRAINING/LOSS:** Selector L1, prune/fine-tune, then focal + 2 GIoU + 5 L1 + 5 sparsity.
- **MAIN LESSON:** Materialize static reductions and count controller overhead.
- **RELATION TO FARTRACK:** Collision on variable depth/static latent reduction.
- **RELATION TO SPIKETRACK:** Static lesson only; dynamic route deferred.
- **CAUTION / NOVELTY COLLISION:** Not evidence for whole-MRM skipping.
- **EVIDENCE:** [E32].

## N_DY

- **NODE ID:** N_DY
- **DISPLAY NAME:** DyTrack — CROWDED / DEFERRED
- **YEAR/VENUE:** 2025 / IEEE TNNLS
- **PRIMARY ROLE:** NOVELTY_COLLISION
- **PROBLEM:** Input-dependent compute allocation.
- **CORE ARCHITECTURE:** Dynamic transformer with routes, exits, and feature recycling.
- **KEY MECHANISM:** Target-aware self-distilled path selection.
- **EFFICIENCY ACTION:** Skip deeper blocks per input.
- **TRAINING/LOSS:** Multi-route task supervision + self-distillation.
- **MAIN LESSON:** Dynamic depth is established and has control overhead.
- **RELATION TO FARTRACK:** Dynamic alternative to fixed depth.
- **RELATION TO SPIKETRACK:** Negative control for rejected MRM1 skip.
- **CAUTION / NOVELTY COLLISION:** MRM1 remains `DIAG_FAIL`; hold-out consumed.
- **EVIDENCE:** [E08, E13].

## N_HKD

- **NODE ID:** N_HKD
- **DISPLAY NAME:** Hybrid-KD pruning tracker
- **YEAR/VENUE:** 2026 / IEEE TCSVT
- **PRIMARY ROLE:** NOVELTY_COLLISION
- **PROBLEM:** Structural redundancy in lightweight tracker backbones.
- **CORE ARCHITECTURE:** Static pruned tracker + Hybrid KD; full structure UNKNOWN.
- **KEY MECHANISM:** Q/K/V Token KD + masked Local KD + Vision-Mamba Global KD.
- **EFFICIENCY ACTION:** Static backbone pruning.
- **TRAINING/LOSS:** Prune/retrain with three-level HKD; formulas/weights UNKNOWN.
- **MAIN LESSON:** Generic pruning + tracking-specific KD is already a direct prior.
- **RELATION TO FARTRACK:** Near-direct collision with reduction + task preservation.
- **RELATION TO SPIKETRACK:** Forces an SNN-native causal question, not a generic application claim.
- **CAUTION / NOVELTY COLLISION:** Highest risk; abstract-only details must not be overstated.
- **EVIDENCE:** [E27, E35].
