# High-relevance paper knowledge cards

## Selection rule

The cards cover the two anchors plus papers that provide a directly relevant efficiency mechanism, a SpikeTrack-relevant training/memory mechanism, or a strong novelty-collision warning. Inclusion means **knowledge donor**, not third-baseline candidacy. `UNKNOWN` is used where the inspected primary source did not establish a requested detail.

## 1. FARTrack: Fast Autoregressive Visual Tracking with High Performance

- **Status / problem / paradigm / backbone:** peer-reviewed ICLR 2026; speed-accuracy reduction for autoregressive SOT; one ViT-Tiny encoder with 15/10/6-layer operating points [E03, E04].
- **Template / search / interaction:** five 112x112 template token sets plus a 224x224 search set and four command tokens share the encoder. The paper describes trajectory tokens, but the public sparse inference path does not actually add historical-coordinate tokens [E03, E04].
- **Temporal / memory / head:** previous-box tracker state, historical template crops, and per-template masks persist. Four command outputs produce coordinate-vocabulary distributions in parallel [E04].
- **Novelty / efficiency / structural change:** adjacent-depth task-logit self-distillation reduces depth; attention-derived masks retain 75% of template tokens and persist across frames [E03].
- **Training / losses:** staged frame training, TSSD, and 32-frame sparsification training; CE, SIoU, and adjacent KL, with paper/code stage-weight discrepancies [E03, E04].
- **Removed/reused / reported trade-off / weakness:** depth and template-token work are reduced; Nano loses little reported AO while Pico loses substantially more. Public code differs on trajectory use, selected salience inputs, sparse execution, and training schedule [E03, E04].
- **Why it matters:** it is the fixed lightweight-design anchor; for SpikeTrack it motivates task-facing static depth/representation distillation and temporally amortized compression, not component copying.
- **Transfer / collision / evidence:** `HIGH` transferability at principle level; `HIGH` collision for generic task-specific distillation or temporal sparsity claims. Evidence [E03, E04].

## 2. SpikeTrack: A Spike-driven Framework for Efficient Visual Tracking

- **Status / problem / paradigm / backbone:** peer-reviewed CVPR 2026; spike-driven RGB SOT; asymmetric SDT-v3 small/base spike CNN + spike Transformer backbone [E05, E06].
- **Template / search / interaction:** T1/T3 template encoder creates six compact K-transpose-V memories; one-timestep search features interact through six MRMs [E05, E23].
- **Temporal / memory / head:** learned NI-LIF decay, temporary T expansion inside MRMs, fixed-first-template FIFO update, and three-tower center/size/offset head [E05, E23].
- **Novelty / efficiency / structural change:** normalized-integer spikes, softmax-free linear spike attention, asymmetric template amortization, and reusable memory. Released inference physically instantiates separate template and search modules [E05, E07].
- **Training / losses:** T1 full training then T3 fine-tuning; focal + 2 GIoU + 5 L1; no explicit energy, sparsity, distillation, or template-quality objective [E05].
- **Removed/reused / reported trade-off / weakness:** spatial template tokens collapse into compact matrices and template compute is amortized. Analytical energy is not measured device energy; fine-grained semantics, similar objects, fast motion, deformation, update quality, dense GPU operators, and export structure remain constraints [E05, E07, E24].
- **Why it matters:** it is the fixed redesign anchor. FARTrack principles must be expressed through SpikeTrack-specific stages, MRMs, cache, head, and loss.
- **Transfer / collision / evidence:** recipient anchor, not scored as a donor; `HIGH` collision for generic spiking-tracker novelty. Evidence [E05-E08, E23, E24].

## 3. AsymTrack — Two-stream Beats One-stream

- **Status / problem / paradigm / backbone:** peer-reviewed AAAI 2025; eliminates repeated template work through an asymmetric Siamese design. Exact backbone block inventory is `UNKNOWN` in this card [E09].
- **Template / search / interaction:** template runs once and emits modulation signals; search runs per frame; information flows unidirectionally into search features [E09].
- **Temporal / memory / head:** cached modulation is the persistent template state. Prediction-head and loss details are `UNKNOWN` here.
- **Novelty / efficiency / structural change:** separates template and search computation and adds object-perception enhancement to a lightweight tracker [E09].
- **Training / losses:** joint training is reported; exact loss composition is `UNKNOWN` here.
- **Removed/reused / trade-off / weakness:** removes per-frame template recomputation and reports cross-platform speed-accuracy gains. SpikeTrack’s own ablation finds simple AsymTrack-style modulation unsuitable for its coarse spike representation [E05, E09].
- **Why it matters:** it is an asymmetry/template-reuse reference for FARTrack and a close collision/negative-transfer warning for SpikeTrack.
- **Transfer / collision / evidence:** `MEDIUM` for runtime/module-sharing principles, `LOW/INCOMPATIBLE` for direct modulation; collision `HIGH`. Evidence [E05, E09].

## 4. CompressTracker — General Compression Framework for Efficient Transformer Object Tracking

- **Status / problem / paradigm / backbone:** peer-reviewed ICCV 2025; compresses transformer trackers through a general teacher/student framework; supported backbones vary [E10].
- **Template / search / interaction:** preserves the selected tracker’s template/search representation and interaction; exact representation depends on the compressed baseline.
- **Temporal / memory / head:** no new persistent temporal memory is central; the original head is guided during stage replacement [E10].
- **Novelty / efficiency / structural change:** divides a teacher into stages, replaces stages progressively, uses prediction guidance and stage-wise feature mimicking [E10].
- **Training / losses:** replacement training plus stage-wise feature mimic and prediction guidance; exact scalar weights are `UNKNOWN` in this card.
- **Removed/reused / trade-off / weakness:** substitutes cheaper stages while transferring teacher behavior; the evidence is conventional-transformer, not spiking-backbone compatibility [E10].
- **Why it matters:** complements FARTrack’s adjacent-depth distillation and offers a staged way to change SpikeTrack depth/width interfaces.
- **Transfer / collision / evidence:** `HIGH` conceptual transfer, retraining required; collision `MEDIUM-HIGH`. Evidence [E10].

## 5. MixFormerV2

- **Status / problem / paradigm / backbone:** peer-reviewed NeurIPS 2023; efficient fully Transformer tracking [E11].
- **Template / search / interaction:** prediction tokens compress task communication; exact per-branch token layout and head details are `UNKNOWN` here.
- **Temporal / memory / head:** no central cross-frame memory contribution established in this card; prediction tokens feed the tracker output.
- **Novelty / efficiency / structural change:** dense-to-sparse representation transfer and deep-to-shallow distillation [E11].
- **Training / losses:** teacher/student distillation; exact task-loss weights are `UNKNOWN` here.
- **Removed/reused / trade-off / weakness:** reduces layers and token density while preserving teacher behavior; transfer remains conventional-transformer evidence rather than SNN evidence [E11].
- **Why it matters:** a strong collision/reference for FARTrack’s shallow distillation and a donor for SpikeTrack static prefix training.
- **Transfer / collision / evidence:** `MEDIUM`; retraining required; collision `HIGH`. Evidence [E11].

## 6. LiteTrack

- **Status / problem / paradigm / backbone:** peer-reviewed ICRA 2024; lightweight transformer tracking with asynchronous template/search feature extraction [E12].
- **Template / search / interaction:** template features are computed separately and reused; search processing is pruned and interacts with stored template evidence [E12].
- **Temporal / memory / head:** cached template feature is the relevant state; head/loss details are `UNKNOWN` here.
- **Novelty / efficiency / structural change:** removes layers and avoids synchronized repeated template extraction [E12].
- **Training / losses:** retrains the pruned/asynchronous tracker; detailed scalar loss is `UNKNOWN` here.
- **Removed/reused / trade-off / weakness:** saves template and layer work; reported Orin NX results cannot be projected to Jetson Nano [E12].
- **Why it matters:** template-computation reuse relates to both anchors; SpikeTrack already caches templates, so the remaining opportunity is module/runtime consolidation rather than rediscovering asymmetry.
- **Transfer / collision / evidence:** `MEDIUM` for static pruning/runtime organization; collision `HIGH`. Evidence [E12].

## 7. DyTrack — Exploring Dynamic Transformer for Efficient Object Tracking

- **Status / problem / paradigm / backbone:** peer-reviewed IEEE TNNLS 2025; efficient transformer tracking via input-conditioned paths [E13].
- **Template / search / interaction:** target-aware features feed alternative reasoning routes; exact template/search tensor layout is `UNKNOWN` here.
- **Temporal / memory / head:** intermediate exits and feature recycling provide state within inference; no central long-term template memory is established here.
- **Novelty / efficiency / structural change:** dynamic routing, intermediate exit, feature recycling, and target-aware self-distillation [E13].
- **Training / losses:** trains route/exit behavior with self-distillation; exact scalar objective is `UNKNOWN` here.
- **Removed/reused / trade-off / weakness:** conditionally avoids deeper transformer work but adds decision logic; this is not evidence for MRM1 skipping [E08, E13].
- **Why it matters:** it is a major novelty collision around conditional depth and a useful negative-control reference for SpikeTrack.
- **Transfer / collision / evidence:** `LOW-MEDIUM` because the sealed MRM1 route failed and a new dataset would be required; collision `HIGH`. Evidence [E08, E13].

## 8. FastSeqTrack — Exploring Efficient and Effective Sequence Learning

- **Status / problem / paradigm / backbone:** peer-reviewed IJCAI 2025; reduces autoregressive decoding latency in sequence-learning trackers [E14].
- **Template / search / interaction:** transformer features support tracking-token prediction; detailed template/search backbone is `UNKNOWN` here.
- **Temporal / memory / head:** parallel token generation plus confidence-based early exit changes the sequence head, not cross-frame memory [E14].
- **Novelty / efficiency / structural change:** removes serial coordinate-token decoding steps and can stop decoding early [E14].
- **Training / losses:** sequence training with exit supervision; exact losses are `UNKNOWN` here.
- **Removed/reused / trade-off / weakness:** cuts sequential head latency; SpikeTrack already uses a parallel dense center head, so direct benefit is limited.
- **Why it matters:** it clarifies that FARTrack’s inter-frame autoregression and head-level sequence acceleration are different; it is mostly a collision/comparison reference for SpikeTrack.
- **Transfer / collision / evidence:** `LOW`; collision `HIGH` for early-exit sequence claims. Evidence [E14].

## 9. LoReTrack

- **Status / problem / paradigm / backbone:** peer-reviewed IROS 2025, manually merged with arXiv:2405.17660; low-resolution transformer tracking [E15].
- **Template / search / interaction:** frozen high-resolution teacher and low-resolution student align Q/K/V interactions and target-discriminative regions [E15].
- **Temporal / memory / head:** no new temporal memory is central; baseline head is retained. Exact head architecture is `UNKNOWN` here.
- **Novelty / efficiency / structural change:** reduces input resolution and uses QKV-KD plus discrimination-KD to repair information loss [E15].
- **Training / losses:** cross-resolution distillation plus original tracker losses; retraining is required.
- **Removed/reused / trade-off / weakness:** reported 256-resolution configuration saves 56% MACs and runs 52% faster than the compared 384-resolution tracker while recovering accuracy; small targets/fine details remain the core risk [E15].
- **Why it matters:** it complements FARTrack’s depth axis and directly motivates a SpikeTrack resolution-specific teacher/student study.
- **Transfer / collision / evidence:** `HIGH` principle transfer; collision `HIGH`. Evidence [E15].

## 10. MCITrack — Enhanced Contextual Information for Video-Level Tracking

- **Status / problem / paradigm / backbone:** peer-reviewed AAAI 2025; addresses insufficient video-level context with a temporal state model [E16].
- **Template / search / interaction:** current tracking features interact with a persistent Mamba-derived hidden state through cross-attention [E16].
- **Temporal / memory / head:** explicit hidden state carries contextual information; exact head and loss details are `UNKNOWN` here.
- **Novelty / efficiency / structural change:** adds recurrent contextual memory rather than primarily removing computation [E16].
- **Training / losses:** trains state and cross-attention end to end; exact scalar losses are `UNKNOWN` here.
- **Removed/reused / trade-off / weakness:** reuses history but may increase state, operators, and latency.
- **Why it matters:** it is a memory-quality donor to both anchors but a cost warning for SpikeTrack’s edge objective.
- **Transfer / collision / evidence:** `LOW-MEDIUM`; collision `MEDIUM`; retraining required. Evidence [E16].

## 11. ARPTrack — Autoregressive Sequential Pretraining for Visual Tracking

- **Status / problem / paradigm / backbone:** peer-reviewed CVPR 2025; improves video-level appearance/motion learning through autoregressive pretraining [E17].
- **Template / search / interaction:** pretraining sequences condition target representation on ordered video evidence; downstream tracker architecture is retained [E17].
- **Temporal / memory / head:** motion/appearance sequence and backtracking objective affect learned representation; no required extra inference memory is central.
- **Novelty / efficiency / structural change:** moves temporal modeling cost into offline pretraining [E17].
- **Training / losses:** autoregressive sequential pretraining with a backtracking objective, followed by tracker training [E17].
- **Removed/reused / trade-off / weakness:** does not directly reduce inference FLOPs; transfer to NI-LIF representations is unverified.
- **Why it matters:** it is a training-only donor that can complement FARTrack task supervision and potentially improve a smaller SpikeTrack without adding runtime blocks.
- **Transfer / collision / evidence:** `MEDIUM-HIGH`; collision `MEDIUM-HIGH`; full retraining required. Evidence [E17].

## 12. HiT — Lightweight Hierarchical Vision Transformers

- **Status / problem / paradigm / backbone:** peer-reviewed ICCV 2023; lightweight hierarchical vision transformer for efficient tracking [E18].
- **Template / search / interaction:** hierarchical template/search features are connected by a deep-to-shallow Bridge Module and dual-image positional encoding [E18].
- **Temporal / memory / head:** no primary cross-frame memory contribution; head/loss details are `UNKNOWN` here.
- **Novelty / efficiency / structural change:** replaces a heavy flat backbone with hierarchical multi-scale features and a bridge [E18].
- **Training / losses:** end-to-end tracker training; exact loss weights are `UNKNOWN` here.
- **Removed/reused / trade-off / weakness:** reduces backbone cost; reported AGX evidence is not Jetson Nano evidence, and direct transplant into an SNN is untested [E18].
- **Why it matters:** a structural backbone donor and collision reference for both anchors.
- **Transfer / collision / evidence:** `MEDIUM`; collision `HIGH`; requires redesign/retraining. Evidence [E18].

## 13. CPDATrack — Context-Aware Token Pruning and Selective Attention

- **Status / problem / paradigm / backbone:** peer-reviewed JVCIR 2026; one-stream transformer tracking with background/distractor suppression [E19].
- **Template / search / interaction:** a learned target-probability module prunes search tokens; direction-controlled attention changes search-template information flow [E19].
- **Temporal / memory / head:** no central cross-frame memory; head/loss details are `UNKNOWN` here.
- **Novelty / efficiency / structural change:** preserves target context while pruning background and selectively exposes template attention [E19].
- **Training / losses:** learned selector plus tracker training; exact objective is `UNKNOWN` here.
- **Removed/reused / trade-off / weakness:** removes search tokens but adds a selector; one-stream topology conflicts with SpikeTrack’s six-cache MRM design.
- **Why it matters:** a publication-grade sparsity and novelty-collision reference, still only a knowledge donor.
- **Transfer / collision / evidence:** `LOW-MEDIUM`; collision `HIGH`; retraining required. Evidence [E19].

## 14. SpikeFET — Fully Spiking Neural Networks for Unified Frame-Event Tracking

- **Status / problem / paradigm / backbone:** peer-reviewed NeurIPS 2025; fully spiking frame-event tracking [E20].
- **Template / search / interaction:** frame and event representations are fused in an SNN; exact RGB-only template/search decomposition is not applicable/`UNKNOWN`.
- **Temporal / memory / head:** event timing and spike dynamics are central; memory and head specifics are `UNKNOWN` here.
- **Novelty / efficiency / structural change:** spike-specific spatial-temporal regularization and multimodal fusion [E20].
- **Training / losses:** includes spike spatial-temporal regularization; exact weights are `UNKNOWN` here.
- **Removed/reused / trade-off / weakness:** exploits event sparsity but changes modality and task assumptions; it does not establish RGB-only edge efficiency.
- **Why it matters:** direct SNN training donor and high collision check for SpikeTrack.
- **Transfer / collision / evidence:** `MEDIUM` for loss ideas, `LOW` for architecture; collision `HIGH`. Evidence [E20].

## 15. STDTrack — Reliable Spatiotemporal Dependencies

- **Status / problem / paradigm / backbone:** peer-reviewed AAAI 2026; external to both supplied exports; efficient temporal tracking with reliability-aware state [E21].
- **Template / search / interaction:** maintains quality-filtered temporal tokens and integrates reliable state with current features [E21].
- **Temporal / memory / head:** quality-based memory maintenance plus an inference-time reparameterized head [E21].
- **Novelty / efficiency / structural change:** controls memory quality and folds training-time head structure for inference [E21].
- **Training / losses:** exact loss weights are `UNKNOWN` in this card.
- **Removed/reused / trade-off / weakness:** reuses selected temporal evidence and reduces head-time structure; external status means it is a donor/collision check only.
- **Why it matters:** quality-gated memory is relevant to FARTrack mask persistence and SpikeTrack FIFO updates without reviving MRM skipping.
- **Transfer / collision / evidence:** `HIGH` for the memory-quality principle, `MEDIUM` for head reparameterization; collision `HIGH`. Evidence [E21].
