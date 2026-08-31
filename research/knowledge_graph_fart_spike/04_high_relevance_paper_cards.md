# High-relevance paper knowledge cards — V1.2 content audit

## Selection and evidence rule

These 19 cards cover the two fixed anchors, the 13 existing donors/collision references, and the four Manager-required additions. Inclusion means **knowledge source**, never third-baseline candidacy. Every card uses the same 22 fields. `UNKNOWN` means the inspected primary evidence did not establish the detail; it is not filled from analogy. Evidence IDs resolve through `14_evidence_log.csv`.

## 1. FARTrack: Fast Autoregressive Visual Tracking with High Performance

- **Canonical tracker/paper name:** FARTrack: Fast Autoregressive Visual Tracking with High Performance.
- **Year / venue:** 2026 / ICLR.
- **Research problem:** retain high accuracy while removing the latency of a deep autoregressive visual tracker.
- **Architectural paradigm:** one-stream autoregressive tracking with command-token coordinate prediction.
- **Backbone:** ViT-Tiny encoder; reported 15-, 10-, and 6-layer operating points.
- **Template path:** five 112x112 template crops are tokenized; template-token salience masks are selected once and persisted.
- **Search path:** a 224x224 search crop is tokenized on every frame.
- **Template-search interaction:** template, search, and four command tokens share self-attention in the encoder.
- **Temporal/cross-frame state:** previous box, historical template crops, and their persistent masks; public sparse inference does not add the trajectory tokens described in the paper.
- **Prediction head:** four command outputs produce parallel coordinate-vocabulary distributions.
- **Exact efficiency mechanism:** Task-Specific Self-Distillation (TSSD) transfers adjacent-depth task logits; IFAS retains 75% of template tokens and reuses the decision across frames.
- **Exact structure removed/reduced/reused:** fixed encoder depth is reduced; 25% of template-token work is removed; template-mask decisions are reused.
- **Training strategy:** staged single-frame training, adjacent-depth self-distillation, then 32-frame sparsification training.
- **Important losses/distillation objectives:** coordinate CE, SIoU, and adjacent-model KL; paper/code stage-weight discrepancies are recorded.
- **Reported efficiency-accuracy evidence:** Nano (10 layers) is reported with a small accuracy loss relative to the 15-layer model; Pico (6 layers) loses materially more; hardware is Titan Xp/Xeon/Ascend, not the target edge device.
- **Main limitation:** paper/code divergence on trajectory use, salience inputs, sparse execution, and schedule; no SpikeTrack/SNN evidence.
- **Transferable DESIGN PRINCIPLE:** preserve task-facing outputs when making fixed structural reductions; decide stable reductions once and amortize them.
- **Non-transferable COMPONENTS:** autoregressive vocabulary head, ViT token mask implementation, and FARTrack-specific template schedule.
- **Relationship to FARTrack:** fixed lightweight-design/methodology anchor.
- **Relationship to SpikeTrack:** principle donor for static stage/depth reduction plus tracking-facing preservation, not a component blueprint.
- **Novelty-collision role:** high collision for generic shallow self-distillation and temporal token sparsity claims.
- **Final presentation role:** `ANCHOR`. Evidence [E03, E04].

## 2. SpikeTrack: A Spike-driven Framework for Efficient Visual Tracking

- **Canonical tracker/paper name:** SpikeTrack: A Spike-driven Framework for Efficient Visual Tracking.
- **Year / venue:** 2026 / CVPR.
- **Research problem:** efficient RGB SOT using spike-driven representation and asymmetric template/search computation.
- **Architectural paradigm:** separate spiking template and search encoders plus six Memory Retrieval Modules (MRMs).
- **Backbone:** SDT-v3 small/base spike CNN and spike Transformer stages with NI-LIF neurons.
- **Template path:** T1/T3 template encoder constructs six compact K-transpose-V memory matrices.
- **Search path:** one-timestep search encoder processes every frame.
- **Template-search interaction:** six MRMs retrieve template information into search features through softmax-free linear spike attention.
- **Temporal/cross-frame state:** six caches, temporary timestep expansion inside MRMs, learned NI-LIF state/decay, and fixed-first-template FIFO update.
- **Prediction head:** three towers for center score, size, and offset.
- **Exact efficiency mechanism:** normalized-integer spikes, multiplication-light linear attention, template amortization, and compact reusable memories.
- **Exact structure removed/reduced/reused:** spatial template tokens are collapsed into six compact matrices and template compute is reused; released variants change stage depth/width/timestep.
- **Training strategy:** full T1 training followed by T3 fine-tuning for multi-timestep variants.
- **Important losses/distillation objectives:** focal classification + 2 GIoU + 5 L1; no explicit KD, sparsity, energy, or template-quality loss.
- **Reported efficiency-accuracy evidence:** paper energy is an analytical 45-nm operation model using spike firing rate; local I0 measures strict-load S256-T1 parity/runtime on MX250 only, not Jetson/TensorRT.
- **Main limitation:** fine-grained semantics, similar objects, fast motion, deformation, cache-update quality, dense GPU operators, and export structure remain open; analytical energy is not measured device power.
- **Transferable DESIGN PRINCIPLE:** recipient-specific reductions must preserve spike temporal/state behavior and target-facing output behavior.
- **Non-transferable COMPONENTS:** none; this is the redesign target, not a donor.
- **Relationship to FARTrack:** receives only general methodology analogies.
- **Relationship to SpikeTrack:** fixed redesign anchor.
- **Novelty-collision role:** generic “spiking tracker” novelty is already occupied; SNN-native causal questions remain open.
- **Final presentation role:** `ANCHOR`. Evidence [E05-E08, E23, E24].

## 3. AsymTrack — Two-stream Beats One-stream

- **Canonical tracker/paper name:** Two-stream Beats One-stream: Asymmetric Siamese Network for Efficient Visual Tracking (AsymTrack).
- **Year / venue:** 2025 / AAAI.
- **Research problem:** eliminate template recomputation and pervasive one-stream interaction on resource-constrained devices.
- **Architectural paradigm:** asymmetric Siamese template-once/search-per-frame tracker.
- **Backbone:** lightweight hierarchical tracker family; exact per-variant block inventory is `UNKNOWN` here.
- **Template path:** initialization-only branch produces a stored modulation signal.
- **Search path:** independent per-frame lightweight branch.
- **Template-search interaction:** Efficient Template Modulation injects template cues unidirectionally; Object Perception Enhancement merges abstract semantics and local detail and is reparameterized for inference.
- **Temporal/cross-frame state:** cached template modulation only.
- **Prediction head:** lightweight box head; exact tower inventory is `UNKNOWN` here.
- **Exact efficiency mechanism:** asymmetric workload and inference-time reparameterization.
- **Exact structure removed/reduced/reused:** per-frame template branch and repeated bidirectional relation modeling are removed; initialization signal is reused.
- **Training strategy:** end-to-end tracker training with training-time OPE branches folded for inference.
- **Important losses/distillation objectives:** standard tracking objectives; exact scalar composition is `UNKNOWN` in inspected evidence.
- **Reported efficiency-accuracy evidence:** AsymTrack-T reports 60.8 LaSOT AUC and 224/81/84 FPS on GPU/CPU/Jetson AGX, 6.0 AUC above HiT-Tiny.
- **Main limitation:** simple modulation loses rich relation modeling; SpikeTrack reports direct AsymTrack-style modulation unsuitable for coarse spikes.
- **Transferable DESIGN PRINCIPLE:** compute stable template evidence once and keep the per-frame path dominant.
- **Non-transferable COMPONENTS:** ETM/OPE transplant and conventional-feature modulation.
- **Relationship to FARTrack:** supports amortized template decisions.
- **Relationship to SpikeTrack:** confirms asymmetry already present and supplies a negative-transfer warning.
- **Novelty-collision role:** high for template-once asymmetry.
- **Final presentation role:** `SECONDARY_DONOR`. Evidence [E05, E09].

## 4. CompressTracker — General Compression Framework for Efficient Transformer Object Tracking

- **Canonical tracker/paper name:** General Compression Framework for Efficient Transformer Object Tracking (CompressTracker).
- **Year / venue:** 2025 / ICCV.
- **Research problem:** compress transformer trackers without binding the student to the teacher structure or a complex multi-stage pipeline.
- **Architectural paradigm:** heterogeneous stage-wise teacher/student compression framework.
- **Backbone:** tracker-dependent transformer teacher and cheaper student; demonstrated on OSTrack/SUTrack families.
- **Template path:** inherited from the selected tracker.
- **Search path:** inherited from the selected tracker.
- **Template-search interaction:** inherited, while each student stage learns the corresponding teacher-stage function.
- **Temporal/cross-frame state:** no new persistent state.
- **Prediction head:** original student prediction head with teacher prediction guidance during training.
- **Exact efficiency mechanism:** divide the teacher into as many stages as student layers; randomly replace student stages with corresponding teacher stages during training; add stage feature mimic and prediction guidance.
- **Exact structure removed/reduced/reused:** teacher depth/capacity is replaced by fewer or heterogeneous student stages; teacher stages are training-only.
- **Training strategy:** one replacement-training process; assemble only student stages for inference.
- **Important losses/distillation objectives:** original tracking loss, teacher prediction guidance, and per-stage feature mimicking; exact scalar weights are `UNKNOWN` here.
- **Reported efficiency-accuracy evidence:** CompressTracker-SUTrack reports 72.2 LaSOT AUC (about 99% retained) with 2.42x speedup; a 4-layer OSTrack variant reports about 96% accuracy with 2.17x speedup.
- **Main limitation:** evidence is conventional transformer compression; stage/interface compatibility with spiking state is untested.
- **Transferable DESIGN PRINCIPLE:** replace structure stage-wise while preserving intermediate and task-facing teacher behavior.
- **Non-transferable COMPONENTS:** random conventional-transformer stage interchange and feature-space equality assumptions.
- **Relationship to FARTrack:** strengthens adjacent-depth TSSD with heterogeneous, stage-local supervision.
- **Relationship to SpikeTrack:** supporting donor for training a fixed smaller stage structure.
- **Novelty-collision role:** medium-high; a generic stage-wise KD claim is occupied.
- **Final presentation role:** `PRIMARY_DONOR`. Evidence [E10].

## 5. MixFormerV2: Efficient Fully Transformer Tracking

- **Canonical tracker/paper name:** MixFormerV2: Efficient Fully Transformer Tracking.
- **Year / venue:** 2023 / NeurIPS.
- **Research problem:** eliminate dense prediction machinery and reduce transformer depth while retaining tracking accuracy.
- **Architectural paradigm:** one-stream fully transformer tracker with sparse prediction tokens.
- **Backbone:** MixViT-derived transformer, progressively pruned deep-to-shallow.
- **Template path:** template tokens enter the shared backbone.
- **Search path:** search tokens enter the shared backbone.
- **Template-search interaction:** shared mixed attention; four learned prediction tokens collect task evidence.
- **Temporal/cross-frame state:** no central new persistent state.
- **Prediction head:** four coordinate-distribution MLP outputs plus score MLP, replacing the dense convolutional corner head.
- **Exact efficiency mechanism:** dense-to-sparse head distillation and progressive deep-to-shallow backbone distillation; optional hidden-dimension pruning.
- **Exact structure removed/reduced/reused:** dense feature-map head, backbone layers, and optionally MLP width are reduced; teacher outputs supervise the sparse student.
- **Training strategy:** initialize from a deep teacher, progressively drop layers, optionally use intermediate teachers, and distill dense logits.
- **Important losses/distillation objectives:** normal tracking objectives plus dense-head logit distillation and depth-reduction supervision; exact full weighting is `UNKNOWN` here.
- **Reported efficiency-accuracy evidence:** MixFormerV2-B reports 70.6 LaSOT AUC, 56.7 TNL2K AUC, and 165 GPU FPS; V2-S reports real-time CPU speed.
- **Main limitation:** conventional dense/softmax transformer evidence; no SNN temporal/state preservation.
- **Transferable DESIGN PRINCIPLE:** progressively shorten a tracker while preserving task distributions; compress head communication.
- **Non-transferable COMPONENTS:** MixViT attention, coordinate MLP head, and dense teacher/student feature geometry.
- **Relationship to FARTrack:** strong methodological precursor/collision for shallow distillation.
- **Relationship to SpikeTrack:** donor for a fixed smaller student and target-facing preservation, subject to SNN-native signals.
- **Novelty-collision role:** high for generic deep-to-shallow KD.
- **Final presentation role:** `PRIMARY_DONOR`. Evidence [E11].

## 6. LiteTrack

- **Canonical tracker/paper name:** LiteTrack: Layer Pruning with Asynchronous Feature Extraction for Lightweight and Efficient Visual Tracking.
- **Year / venue:** 2024 / ICRA.
- **Research problem:** remove one-stream template redundancy and excess encoder depth.
- **Architectural paradigm:** feature-extraction stage followed by asynchronous template/search interaction.
- **Backbone:** pruned ViT encoder variants B4/B6/B9.
- **Template path:** computed once by the FE stage and cached.
- **Search path:** FE runs each frame; cached template and search enter AI layers.
- **Template-search interaction:** asynchronous interaction layers jointly process stored template and current search tokens.
- **Temporal/cross-frame state:** cached template feature.
- **Prediction head:** center-style tracking head; exact sub-towers are `UNKNOWN` here.
- **Exact efficiency mechanism:** top-down layer pruning plus asynchronous feature extraction.
- **Exact structure removed/reduced/reused:** upper encoder layers are pruned; template FE is removed from repeated inference and reused.
- **Training strategy:** train the pruned FE/AI allocation end to end.
- **Important losses/distillation objectives:** focal + GIoU + L1; no central KD contribution.
- **Reported efficiency-accuracy evidence:** B6 reports 72.2 TrackingNet AUC at 171 FPS on RTX 2080Ti; B4 exceeds 300 FPS on that GPU and reports 100 FPS ONNX on Orin NX.
- **Main limitation:** direct layer deletion can hurt accuracy; Orin NX is not Jetson Nano and asynchronous caching is already present in SpikeTrack.
- **Transferable DESIGN PRINCIPLE:** fix a smaller depth and separate initialization-only from per-frame work.
- **Non-transferable COMPONENTS:** ViT layer indices and token-concatenation AI implementation.
- **Relationship to FARTrack:** corroborates fixed depth and template amortization.
- **Relationship to SpikeTrack:** structural donor, but not novel merely for caching the template.
- **Novelty-collision role:** high for layer pruning/asynchronous extraction.
- **Final presentation role:** `PRIMARY_DONOR`. Evidence [E12].

## 7. DyTrack — Exploring Dynamic Transformer for Efficient Object Tracking

- **Canonical tracker/paper name:** Exploring Dynamic Transformer for Efficient Object Tracking (DyTrack).
- **Year / venue:** 2025 / IEEE TNNLS.
- **Research problem:** allocate transformer depth according to per-input difficulty.
- **Architectural paradigm:** one-stream dynamic transformer with multiple reasoning routes/early exits.
- **Backbone:** transformer tracker with nested execution paths; exact variant inventory is paper-specific.
- **Template path:** template and search share the dynamic tracker.
- **Search path:** current input drives route/exit decisions.
- **Template-search interaction:** target-aware features support route selection and feature recycling.
- **Temporal/cross-frame state:** no central long-term memory; intermediate features are recycled within an inference pass.
- **Prediction head:** intermediate exits emit tracking predictions.
- **Exact efficiency mechanism:** input-conditioned routes, early termination, feature reuse, and target-aware self-distillation.
- **Exact structure removed/reduced/reused:** deeper blocks are skipped only for selected inputs; earlier features are reused.
- **Training strategy:** jointly train routes/exits with target-aware self-distillation.
- **Important losses/distillation objectives:** per-route tracking supervision and self-distillation; exact scalar weights are `UNKNOWN` here.
- **Reported efficiency-accuracy evidence:** reports improved average speed/accuracy from conditional execution; values are hardware/path-policy dependent and are not used as SpikeTrack estimates.
- **Main limitation:** decision overhead and path variance; the mechanism does not validate SpikeTrack whole-MRM1 skipping.
- **Transferable DESIGN PRINCIPLE:** difficulty-aware computation is a known category, not the favored lane.
- **Non-transferable COMPONENTS:** route controller, intermediate exits, and conventional transformer feature recycling.
- **Relationship to FARTrack:** overlaps efficiency-by-depth but is dynamic rather than fixed.
- **Relationship to SpikeTrack:** novelty collision/negative control; historical whole-MRM1 route remains `DIAG_FAIL` with consumed hold-out.
- **Novelty-collision role:** high; generic dynamic routing is crowded/deferred.
- **Final presentation role:** `NOVELTY_COLLISION`. Evidence [E08, E13].

## 8. FastSeqTrack

- **Canonical tracker/paper name:** Exploring Efficient and Effective Sequence Learning for Visual Object Tracking (FastSeqTrack).
- **Year / venue:** 2025 / IJCAI.
- **Research problem:** remove serial coordinate decoding and overthinking in SeqTrack-like heads.
- **Architectural paradigm:** encoder-decoder sequence tracker with parallel tracking tokens and decoder exits.
- **Backbone:** SeqTrack-style ViT encoder and transformer decoder.
- **Template path:** template tokens contribute to encoder visual features.
- **Search path:** search tokens contribute to the same encoder.
- **Template-search interaction:** global encoder attention; four track tokens cross-attend in the decoder.
- **Temporal/cross-frame state:** none central; “sequence” refers primarily to output coordinates.
- **Prediction head:** four parallel coordinate tokens with parameter-sharing exits after decoder layers.
- **Exact efficiency mechanism:** one-pass coordinate generation and confidence-triggered decoder early exit.
- **Exact structure removed/reduced/reused:** four serial autoregressive decoding steps are removed; later decoder layers may be skipped; exit word networks share parameters.
- **Training strategy:** supervise predictions at every decoder layer.
- **Important losses/distillation objectives:** summed coordinate CE and IoU losses over decoder layers.
- **Reported efficiency-accuracy evidence:** reports 125 FPS and almost no extra parameters over SeqTrack; encoder FLOPs increase about 1.5% from four tracking tokens.
- **Main limitation:** benefit is head-specific; SpikeTrack already has a parallel center/size/offset head.
- **Transferable DESIGN PRINCIPLE:** remove avoidable serial prediction dependencies.
- **Non-transferable COMPONENTS:** coordinate vocabulary, decoder exits, and exit threshold.
- **Relationship to FARTrack:** one-sided donor to its autoregressive head family.
- **Relationship to SpikeTrack:** little direct value beyond a “do not add serial decoding” warning.
- **Novelty-collision role:** high for parallelized sequence/early-exit claims.
- **Final presentation role:** `OMIT_FROM_DRAWING`. Evidence [E14].

## 9. LoReTrack

- **Canonical tracker/paper name:** Efficient and Accurate Low-Resolution Transformer Tracking (LoReTrack).
- **Year / venue:** 2025 / IROS.
- **Research problem:** preserve fine-grained and target-discriminative information after lowering tracker input resolution.
- **Architectural paradigm:** frozen high-resolution teacher and same-architecture low-resolution OSTrack student.
- **Backbone:** one-stream ViT/OSTrack.
- **Template path:** low-resolution template is processed by the student; teacher provides high-resolution training targets.
- **Search path:** low-resolution search features are the main distillation target.
- **Template-search interaction:** Q/K/V projections in the final search encoder layer are aligned across resolutions.
- **Temporal/cross-frame state:** no new persistent state.
- **Prediction head:** retained OSTrack head.
- **Exact efficiency mechanism:** lower spatial resolution plus QKV-KD and target/background Discrimination-KD.
- **Exact structure removed/reduced/reused:** spatial token count/MACs are reduced; frozen high-resolution teacher is training-only.
- **Training strategy:** train high-resolution tracker, freeze it, then retrain low-resolution counterpart.
- **Important losses/distillation objectives:** classification + regression + beta1 QKV-MSE + beta2 Disc-KD; QKV-KD is search-only and target regions receive higher weight.
- **Reported efficiency-accuracy evidence:** 256-resolution model reports 52% faster/56% fewer MACs than 384; 128-resolution reports 25 CPU FPS with 64.9/46.4 LaSOT/LaSOText success; full model reports 70.3 LaSOT success.
- **Main limitation:** fine detail/small targets remain vulnerable; feature geometry and soft attention differ from spikes.
- **Transferable DESIGN PRINCIPLE:** preserve interaction and target/background discrimination when reducing representation density.
- **Non-transferable COMPONENTS:** interpolated dense Q/K/V tensors and OSTrack-specific discrimination masks.
- **Relationship to FARTrack:** connects reduction plus task-facing preservation.
- **Relationship to SpikeTrack:** functional bridge to a SpikeTrack-specific representation-preservation question.
- **Novelty-collision role:** high for generic low-resolution plus tracking KD.
- **Final presentation role:** `SEMANTIC_BRIDGE`. Evidence [E15].

## 10. MCITrack

- **Canonical tracker/paper name:** Exploring Enhanced Contextual Information for Video-Level Object Tracking (MCITrack).
- **Year / venue:** 2025 / AAAI.
- **Research problem:** compensate for insufficient video-level context in frame-pair tracking.
- **Architectural paradigm:** tracker augmented by a Mamba contextual hidden state and cross-attention.
- **Backbone:** base tracker plus state-space context module; exact base variant is paper-specific.
- **Template path:** baseline template evidence is retained.
- **Search path:** current search feature interacts with stored context.
- **Template-search interaction:** current features cross-attend to a Mamba-derived hidden state.
- **Temporal/cross-frame state:** explicit recurrent contextual hidden state.
- **Prediction head:** retained base tracker head; exact tower details are `UNKNOWN` here.
- **Exact efficiency mechanism:** not primarily a reducer; reuses compressed historical context instead of adding raw frames.
- **Exact structure removed/reduced/reused:** historical information is summarized/reused; extra state and attention are added.
- **Training strategy:** end-to-end contextual-state training.
- **Important losses/distillation objectives:** tracker objectives plus contextual modeling; exact scalar losses are `UNKNOWN` here.
- **Reported efficiency-accuracy evidence:** paper reports accuracy gains with an efficient state-space context module; no target-device evidence used here.
- **Main limitation:** can increase operators, state, and latency.
- **Transferable DESIGN PRINCIPLE:** improve quality of compact persistent state rather than simply expanding memory.
- **Non-transferable COMPONENTS:** Mamba block and dense cross-attention.
- **Relationship to FARTrack:** contextual memory reference.
- **Relationship to SpikeTrack:** cache-quality donor, not a primary compression donor.
- **Novelty-collision role:** medium.
- **Final presentation role:** `SECONDARY_DONOR`. Evidence [E16].

## 11. ARPTrack

- **Canonical tracker/paper name:** Autoregressive Sequential Pretraining for Visual Tracking (ARPTrack).
- **Year / venue:** 2025 / CVPR.
- **Research problem:** learn appearance/motion progression before downstream tracking.
- **Architectural paradigm:** autoregressive video pretraining followed by a standard tracker.
- **Backbone:** downstream-compatible visual encoder; exact selected tracker is experiment-dependent.
- **Template path:** learned through ordered target sequences during pretraining.
- **Search path:** downstream tracker path is retained.
- **Template-search interaction:** not redesigned at inference.
- **Temporal/cross-frame state:** temporal knowledge is moved into weights; no mandatory extra runtime state.
- **Prediction head:** downstream tracker head retained.
- **Exact efficiency mechanism:** training-only knowledge enrichment; no direct inference reduction.
- **Exact structure removed/reduced/reused:** none necessarily removed; temporal modeling is offline.
- **Training strategy:** autoregressive appearance/motion sequential pretraining with backtracking, then downstream training.
- **Important losses/distillation objectives:** autoregressive sequence objective and backtracking objective; exact downstream loss depends on tracker.
- **Reported efficiency-accuracy evidence:** improves downstream tracking without requiring its pretraining decoder at inference; it is not an inference-FLOP result.
- **Main limitation:** costly pretraining and unverified transfer to NI-LIF/spike dynamics.
- **Transferable DESIGN PRINCIPLE:** spend training capacity to help a smaller inference model.
- **Non-transferable COMPONENTS:** autoregressive pretraining decoder/data pipeline.
- **Relationship to FARTrack:** contextual relation through autoregressive supervision.
- **Relationship to SpikeTrack:** optional training donor, not core lane.
- **Novelty-collision role:** medium-high for training-only temporal claims.
- **Final presentation role:** `CONTEXTUAL_REFERENCE`. Evidence [E17].

## 12. HiT

- **Canonical tracker/paper name:** Exploring Lightweight Hierarchical Vision Transformers for Efficient Visual Tracking (HiT).
- **Year / venue:** 2023 / ICCV.
- **Research problem:** reconcile low-cost hierarchical downsampling with detail-sensitive tracking.
- **Architectural paradigm:** one-stream tracker using lightweight hierarchical transformer features.
- **Backbone:** LeViT-based HiT family.
- **Template path:** hierarchical template features enter the one-stream backbone.
- **Search path:** hierarchical search features enter the same backbone.
- **Template-search interaction:** dual-image positional encoding plus Bridge Module combines deep semantics with shallow high-resolution detail.
- **Temporal/cross-frame state:** none central.
- **Prediction head:** consumes bridged features; exact tower details are `UNKNOWN` here.
- **Exact efficiency mechanism:** lightweight hierarchical backbone and large-stride reduction repaired by cross-level bridging.
- **Exact structure removed/reduced/reused:** heavy flat backbone is replaced; deep semantic features are reused to enrich shallow features.
- **Training strategy:** end-to-end tracking training.
- **Important losses/distillation objectives:** standard tracker objectives; exact weights are `UNKNOWN` here.
- **Reported efficiency-accuracy evidence:** HiT reports 64.6 LaSOT AUC and 61 FPS on Jetson AGX; 4.7x faster than STARK-ST50 at similar performance in the paper comparison.
- **Main limitation:** AGX is not Nano; direct hierarchical SNN transplant is untested.
- **Transferable DESIGN PRINCIPLE:** pair structural reduction with an explicit mechanism for preserving tracking detail.
- **Non-transferable COMPONENTS:** LeViT, Bridge Module implementation, and dual-image positional encoding.
- **Relationship to FARTrack:** structural lightweight-design reference.
- **Relationship to SpikeTrack:** functional bridge for stage redesign plus information preservation.
- **Novelty-collision role:** high for lightweight hierarchical tracker claims.
- **Final presentation role:** `SEMANTIC_BRIDGE`. Evidence [E18].

## 13. CPDATrack

- **Canonical tracker/paper name:** Context-Aware Token Pruning and Discriminative Selective Attention for Transformer Tracking (CPDATrack).
- **Year / venue:** 2026 / Journal of Visual Communication and Image Representation.
- **Research problem:** suppress background/distractor tokens while preserving target context.
- **Architectural paradigm:** one-stream transformer with learned token pruning and directional attention.
- **Backbone:** one-stream transformer tracker; exact variant is in the primary paper.
- **Template path:** template tokens guide target probability and selective interaction.
- **Search path:** search tokens receive target probabilities and pruning.
- **Template-search interaction:** direction-controlled attention limits information flow after context-aware selection.
- **Temporal/cross-frame state:** none central.
- **Prediction head:** retained tracker head; exact tower details are `UNKNOWN` here.
- **Exact efficiency mechanism:** learned target-probability token pruning plus discriminative selective attention.
- **Exact structure removed/reduced/reused:** background search tokens/attention work are conditionally removed; a selector is added.
- **Training strategy:** jointly train selector and tracker.
- **Important losses/distillation objectives:** tracker and selector supervision; exact formula/weights are `UNKNOWN` in accessible evidence.
- **Reported efficiency-accuracy evidence:** publisher reports improved efficiency/accuracy; exact device-normalized figures are not used here.
- **Main limitation:** added selector and one-stream topology conflict with SpikeTrack's six-cache MRM structure.
- **Transferable DESIGN PRINCIPLE:** preserve target context when pruning representations.
- **Non-transferable COMPONENTS:** target-probability module and direction-controlled soft attention.
- **Relationship to FARTrack:** collision for attention-derived token sparsity.
- **Relationship to SpikeTrack:** possible principle only; not evidence for MRM skipping.
- **Novelty-collision role:** high.
- **Final presentation role:** `NOVELTY_COLLISION`. Evidence [E19].

## 14. SpikeFET

- **Canonical tracker/paper name:** Fully Spiking Neural Networks for Unified Frame-Event Object Tracking (SpikeFET).
- **Year / venue:** 2025 / NeurIPS.
- **Research problem:** unify frame and event tracking in a fully spiking network.
- **Architectural paradigm:** multimodal fully spiking tracker.
- **Backbone:** spike-driven frame/event feature network; exact RGB-only analogue is not applicable.
- **Template path:** multimodal target representation; RGB-only template decomposition is `UNKNOWN/not applicable`.
- **Search path:** frame/event input streams are encoded in spikes.
- **Template-search interaction:** multimodal spiking fusion; exact SpikeTrack-cache equivalence does not exist.
- **Temporal/cross-frame state:** event timing and neuron state are central.
- **Prediction head:** unified tracking head; exact sub-towers are `UNKNOWN` here.
- **Exact efficiency mechanism:** spike/event sparsity plus fully spiking computation.
- **Exact structure removed/reduced/reused:** dense frame-only processing is replaced by spike/event representation; this changes modality.
- **Training strategy:** end-to-end SNN training with spatial-temporal regularization.
- **Important losses/distillation objectives:** tracker losses plus spike spatial-temporal regularization; exact weights are `UNKNOWN` here.
- **Reported efficiency-accuracy evidence:** paper reports frame-event tracking performance/efficiency; it is not RGB-only SpikeTrack target-device evidence.
- **Main limitation:** different modalities/task assumptions.
- **Transferable DESIGN PRINCIPLE:** preserve and regularize spike spatial-temporal behavior during compression.
- **Non-transferable COMPONENTS:** event stream, frame-event fusion, and task-specific head.
- **Relationship to FARTrack:** little direct architectural relation.
- **Relationship to SpikeTrack:** SNN-native training donor/collision check.
- **Novelty-collision role:** high for generic SNN regularization claims.
- **Final presentation role:** `SECONDARY_DONOR`. Evidence [E20].

## 15. STDTrack

- **Canonical tracker/paper name:** Exploring Reliable Spatiotemporal Dependencies for Efficient Visual Tracking (STDTrack).
- **Year / venue:** 2026 / AAAI.
- **Research problem:** prevent unreliable temporal evidence from corrupting efficient tracking.
- **Architectural paradigm:** tracker with reliability-filtered temporal tokens and a reparameterized head.
- **Backbone:** efficient tracker backbone; exact variant details are in the local primary paper.
- **Template path:** template/temporal evidence is quality filtered.
- **Search path:** current search integrates reliable stored tokens.
- **Template-search interaction:** current features consume selected temporal dependencies.
- **Temporal/cross-frame state:** quality-maintained temporal-token memory.
- **Prediction head:** training-time multi-branch structure folded into a simpler inference head.
- **Exact efficiency mechanism:** memory quality control plus inference-time reparameterization.
- **Exact structure removed/reduced/reused:** unreliable tokens are excluded; head branches are fused; selected state is reused.
- **Training strategy:** end-to-end memory reliability training and structural reparameterization.
- **Important losses/distillation objectives:** tracking and reliability objectives; exact scalar weights are `UNKNOWN` here.
- **Reported efficiency-accuracy evidence:** paper reports accuracy/efficiency gains; it is outside both supplied exports and no target-device projection is made.
- **Main limitation:** selection/reparameterization is conventional dense tracking evidence.
- **Transferable DESIGN PRINCIPLE:** preserve state quality before reusing compressed temporal evidence.
- **Non-transferable COMPONENTS:** temporal-token selector and dense reparameterized head.
- **Relationship to FARTrack:** supports cautious persistence of masks/templates.
- **Relationship to SpikeTrack:** directly motivates cache-quality questions without conditional MRM skipping.
- **Novelty-collision role:** high for quality-gated temporal memory.
- **Final presentation role:** `SECONDARY_DONOR`. Evidence [E21].

## 16. ABTrack

- **Canonical tracker/paper name:** Adaptively Bypassing Vision Transformer Blocks for Efficient Visual Tracking (ABTrack).
- **Year / venue:** 2025 / Pattern Recognition 161, article 111278.
- **Research problem:** avoid executing redundant ViT blocks and reduce the overhead introduced by per-block bypass decisions.
- **Architectural paradigm:** one-stream ViT tracker with static dimension pruning followed by input-adaptive block bypass.
- **Backbone:** ViT encoder; a Bypass Decision Module (BDM) is attached to blocks except an initial always-executed prefix.
- **Template path:** template tokens remain in the one-stream sequence.
- **Search path:** search tokens drive target difficulty and block decisions.
- **Template-search interaction:** shared self-attention; bypass applies to the whole token sequence at a block.
- **Temporal/cross-frame state:** no central cross-frame memory.
- **Prediction head:** center/size/offset convolutional head.
- **Exact efficiency mechanism:** BDM maps a bypass token through linear+sigmoid and thresholds a block probability; adaptive sparsity target depends on GIoU difficulty. ViT Pruning (VTP) ranks trainable diagonal MSA/MLP dimensions locally per block and physically removes low-ranked dimensions.
- **Exact structure removed/reduced/reused:** static Q/K/V and MLP latent dimensions are pruned; whole later transformer blocks are conditionally bypassed.
- **Training strategy:** train pruning selectors with L1 sparsity, binarize to a fixed ratio and physically prune/fine-tune; then add/train BDM with task and sparsity objectives.
- **Important losses/distillation objectives:** focal + 2 GIoU + 5 L1 plus block sparsity loss (reported weight 5); the target bypass rate adapts to sample difficulty.
- **Reported efficiency-accuracy evidence:** paper reports better speed/accuracy trade-offs from VTP+BDM; exact hardware table values are not treated as SpikeTrack estimates.
- **Main limitation:** routing adds decision overhead/path variance; block bypass is conventional ViT behavior.
- **Transferable DESIGN PRINCIPLE:** dimension reduction should become a physical static model; account for controller overhead explicitly.
- **Non-transferable COMPONENTS:** BDM, GIoU-based route target, bypass token, and ViT diagonal selectors.
- **Relationship to FARTrack:** collision on variable depth and static latent reduction.
- **Relationship to SpikeTrack:** dynamic route is deferred; static dimension-pruning lesson is secondary and requires SNN-native constraints.
- **Novelty-collision role:** high for adaptive block bypass and local-rank latent pruning.
- **Final presentation role:** `NOVELTY_COLLISION`. Evidence [E32].

## 17. UETrack

- **Canonical tracker/paper name:** UETrack: A Unified and Efficient Framework for Single Object Tracking.
- **Year / venue:** 2026 / CVPR.
- **Research problem:** one efficient tracker for RGB plus depth/thermal/event/language modalities without losing task-specific capacity.
- **Architectural paradigm:** unified one-stream RGB-X student with Token-Pooling-based Mixture-of-Experts (TP-MoE) and teacher-gated distillation.
- **Backbone:** Fast-iTPN-T student; SUTrack-B teacher.
- **Template path:** RGB-X template patches are unified as six-channel tokens; language uses CLIP features.
- **Search path:** RGB-X search patches use the same student.
- **Template-search interaction:** one-stream attention; selected FFNs are replaced by TP-MoE using local token aggregation, token/expert similarity, and soft parallel assignment.
- **Temporal/cross-frame state:** none central.
- **Prediction head:** unified box prediction head; exact tower inventory is `UNKNOWN` here.
- **Exact efficiency mechanism:** compact shared student; TP-MoE adds conditional capacity without hard expert routing. Target-aware Adaptive Distillation (TAD) uses an adaptive network and binary Gumbel decision to enable teacher supervision only for samples where it is judged useful.
- **Exact structure removed/reduced/reused:** multiple modality-specific trackers are replaced by one student; teacher and TAD controller are training-only; MoE experts remain at inference.
- **Training strategy:** train the unified student with task losses, teacher output/feature losses gated per sample by TAD.
- **Important losses/distillation objectives:** focal + 2 GIoU + 5 L1, KL output KD (weight 5), MSE feature KD (weight 0.002), gated by binary adaptive decision.
- **Reported efficiency-accuracy evidence:** UETrack-B reports 69.2 LaSOT AUC and 163/56/60 FPS on GPU/CPU/Jetson AGX; GOT-10k AO 72.6.
- **Main limitation:** “adaptive” means training-sample teacher gating, not inference routing; multimodal MoE capacity/soft assignments conflict with a minimal RGB edge objective.
- **Transferable DESIGN PRINCIPLE:** apply distillation where teacher evidence is beneficial and align both task outputs and features.
- **Non-transferable COMPONENTS:** RGB-X tokenization, TP-MoE, CLIP language path, and SUTrack teacher.
- **Relationship to FARTrack:** expands task-aware distillation beyond uniform adjacent-depth KL.
- **Relationship to SpikeTrack:** strong training-principle donor if redefined around SpikeTrack-native teacher/student signals; not a reason to add MoE.
- **Novelty-collision role:** high for target-aware/adaptive tracking distillation.
- **Final presentation role:** `PRIMARY_DONOR`. Evidence [E33].

## 18. ZoomTrack

- **Canonical tracker/paper name:** ZoomTrack: Target-aware Non-uniform Resizing for Efficient Visual Tracking.
- **Year / venue:** 2023 / NeurIPS.
- **Research problem:** reduce search input size without discarding likely target detail or shrinking the visual field uniformly.
- **Architectural paradigm:** model-agnostic preprocessing wrapper around a base tracker.
- **Backbone:** demonstrated with OSTrack and TransT; base backbone is unchanged.
- **Template path:** unchanged.
- **Search path:** previous-box prior drives a quadratic-program non-uniform warp; a 17x17 control grid is bilinearly sampled into a smaller fixed input.
- **Template-search interaction:** unchanged inside the base tracker; predicted boxes are mapped back to source coordinates.
- **Temporal/cross-frame state:** previous prediction provides the target-location prior.
- **Prediction head:** base tracker head retained.
- **Exact efficiency mechanism:** allocate more output pixels near the likely target and fewer in low-probability regions while retaining the original field of view.
- **Exact structure removed/reduced/reused:** search spatial samples and backbone MACs are reduced; no network layer is pruned.
- **Training strategy:** apply the same warp during training/testing and compute regression in source coordinates.
- **Important losses/distillation objectives:** base tracker losses plus coordinate mapping; no KD is central.
- **Reported efficiency-accuracy evidence:** reports about 21.5G vs 41.5G MACs, 50-52% faster execution, and OSTrack-Zoom 73.5 GOT-10k AO/70.2 LaSOT AUC/100 V100 FPS.
- **Main limitation:** previous-box error can distort or miscenter the target; QP/sampling integration is extra and device cost is not established for SpikeTrack.
- **Transferable DESIGN PRINCIPLE:** reduce spatial work while preserving target-relevant sampling density and field of view.
- **Non-transferable COMPONENTS:** quadratic program, 17x17 warp grid, and prior-to-resize mapping.
- **Relationship to FARTrack:** secondary representation-reduction reference.
- **Relationship to SpikeTrack:** orthogonal secondary spatial direction, not the primary depth+KD lane.
- **Novelty-collision role:** high for target-aware non-uniform resizing.
- **Final presentation role:** `SECONDARY_DONOR`. Evidence [E34].

## 19. Exploring Pruning-Based Efficient Object Tracking via Hybrid Knowledge Distillation (P027)

- **Canonical tracker/paper name:** Exploring Pruning-Based Efficient Object Tracking via Hybrid Knowledge Distillation (tracker: HKDT).
- **Year / venue:** 2026 / IEEE TCSVT 36(2), 2433-2448; DOI 10.1109/TCSVT.2025.3609410.
- **Research problem:** remove structurally redundant layers/capacity from lightweight tracking backbones while preserving tracking knowledge.
- **Architectural paradigm:** HKDT, a pruned transformer tracker trained by Hybrid Knowledge Distillation (HKD).
- **Backbone:** lightweight tracking backbone; exact model identity in full text is `UNKNOWN` in this audit.
- **Template path:** `UNKNOWN` from accessible publisher abstract.
- **Search path:** `UNKNOWN` from accessible publisher abstract.
- **Template-search interaction:** tracking interaction is preserved through token/local/global distillation; exact tensors are `UNKNOWN`.
- **Temporal/cross-frame state:** no such contribution is established by the abstract.
- **Prediction head:** `UNKNOWN`.
- **Exact efficiency mechanism:** static backbone pruning combined with three-level HKD: Token Distillation separately aligns Q/K/V; Local Distillation uses spatial foreground/background masks; Global Distillation uses Vision Mamba for long-range semantic alignment.
- **Exact structure removed/reduced/reused:** publisher abstract establishes backbone pruning and redundant-layer motivation; exact pruned layers, indices, widths, and criterion are `UNKNOWN`.
- **Training strategy:** prune and retrain with HKD; exact ordering/phases are `UNKNOWN`.
- **Important losses/distillation objectives:** token Q/K/V, local masked foreground/background, and global semantic alignment; formulas/weights are `UNKNOWN`.
- **Reported efficiency-accuracy evidence:** abstract reports GOT-10k AO 67.6 (+3.6 over HiT-Base), 64% lower computational cost, and 115% faster CPU tracking; parameter/FLOP/FPS tables and edge-device protocol are `UNKNOWN`.
- **Main limitation:** full text was not openly retrievable, so criterion/teacher/student/pipeline/device details cannot be claimed.
- **Transferable DESIGN PRINCIPLE:** static structural pruning should be paired with tracking-specific preservation at token, local target/background, and global semantic levels.
- **Non-transferable COMPONENTS:** specific pruning rule, Vision Mamba global distiller, masks, teacher/student pair, and weights until verified.
- **Relationship to FARTrack:** very close collision on structural reduction plus task-facing preservation.
- **Relationship to SpikeTrack:** the favored family is too close if phrased only as “prune SpikeTrack and add tracking KD”; novelty must be tied to spike temporal/state/cache behavior and causally tested.
- **Novelty-collision role:** highest generic-family collision at static structural pruning + tracking-specific multi-level KD; this does not establish that every SpikeTrack-native mechanism is occupied.
- **Final presentation role:** `NOVELTY_COLLISION`. Evidence [E27, E35].
