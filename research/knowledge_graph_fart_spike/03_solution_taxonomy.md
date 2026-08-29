# Problem -> solution -> mechanism taxonomy

This taxonomy is multi-label. A paper may contribute to several families, and a family tag does not imply that its mechanism can be transplanted into SpikeTrack. Counts are metadata-screening incidences across the 74-paper deduplicated inventory, not performance rankings or recovered Connected Papers edges [E01, E02].

## Taxonomy

| Problem | Solution family | Mechanisms represented in the neighborhoods | Inventory incidence | Transfer caution |
|---|---|---|---:|---|
| Preserve accuracy while reducing capacity | Model compression / distillation | task-logit self-distillation, stage-wise feature mimicking, cross-resolution QKV/discrimination distillation | 7 | Teacher signals must be adapted to spike-valued states; generic hidden matching may erase temporal behavior [E03, E10, E15]. |
| Reduce input-dependent work | Token / feature / spatial sparsification | attention-derived template masks, target-probability pruning, sparse sequence tokens | 6 | Paper-level token-count savings do not guarantee sparse CUDA kernels [E03, E04, E19]. |
| Remove structural work | Structural pruning | layer pruning, block bypass, foreground-guided token pruning | 7 | Static pruning and input-conditioned skipping are separate mechanisms; the failed MRM1 conditional predictor does not authorize either [E08, E12]. |
| Adapt work to the input | Dynamic / conditional computation | route selection, intermediate exit, adaptive block bypass | 14 | High novelty collision and control overhead; no reuse of the consumed MRM1 hold-out [E08, E13]. |
| Reduce sequential model depth | Block / layer reduction | shallow prefixes, stage replacement, bridge modules | 5 | Depth affects every downstream SpikeTrack MRM injection point and requires retraining [E03, E10, E18]. |
| Reduce tensor dimensions | Width/channel reduction | narrower stage widths, smaller Q/K/V and head channels | 0 direct metadata hits | This is an explicit evidence gap, not evidence of irrelevance. Width changes require end-to-end interface redesign in SpikeTrack [E23]. |
| Reduce backbone overhead | Lightweight backbone design | hierarchical lightweight ViTs, compressed stages, small/base families | 11 | Conventional-transformer results do not establish spiking-backbone compatibility [E10, E18]. |
| Avoid redundant template work | Asymmetric template-search architecture | template-once processing, separate branches, unidirectional modulation | 12 | SpikeTrack already has asymmetric execution and compact cached memory; direct modulation performed poorly in its ablation [E05, E09]. |
| Reuse stable target evidence | Template computation reuse | cached template features/matrices, asynchronous processing | 3 | Reuse saves recomputation but runtime modules may remain resident [E05, E07, E12]. |
| Reduce spatial work | Low/adaptive-resolution processing | smaller crops, target-aware resizing, cross-resolution distillation | 3 | Low resolution risks losing small-target detail and requires retraining [E15]. |
| Model ordered outputs/history | Autoregressive / sequence modeling | coordinate tokens, parallel sequence generation, sequential pretraining | 11 | “Autoregressive” covers distinct inter-frame and within-output semantics; it is not a single transferable block [E03, E14, E17]. |
| Use longer context | Temporal context / video-level memory | hidden-state context, historical prompts, template queues | 9 | Richer state may raise rather than lower latency and memory [E16]. |
| Exploit target dynamics | Motion modeling | appearance-motion pretraining, motion prompts, implicit state | 7 | Offline pretraining is more compatible than adding per-frame recurrent compute [E17]. |
| Maintain target identity | Template / target memory | FIFO templates, calibrated/quality-controlled memory, compact K-transpose-V cache | 2 | Update quality and drift control matter as much as cache size [E05, E21]. |
| Couple template and search | Relation / cross-attention modeling | Q-memory retrieval, cross-attention, direction-controlled attention | 12 | Interaction topology is representation-specific; SpikeTrack’s coarse spike representation rejected simple modulation [E05, E19]. |
| Exploit event-like computation | SNN / neuromorphic computation | NI-LIF, spike attention, spike regularization | 2 | Analytical sparse-add energy is not measured GPU/Jetson power [E05, E20]. |
| Shorten temporal execution | Temporal timestep optimization | T1/T3 template settings, learned decay/fusion | 2 | T changes MRM operators and fusion, so it is a trained architecture choice [E05, E23]. |
| Improve foreground discrimination | Target-aware representation | auto masks, discriminative distillation, object perception | 11 | Discrimination improvements can add selectors, language models, or dense attention that conflict with edge goals. |
| Resist drift and distractors | Robustness / distractor handling | foreground/background modeling, selective attention, quality-based memory | 30 | This broad count is abstract-language sensitive and is not the main efficiency signal. |
| Move cost into training | Training/loss redesign | task-specific KL, cross-resolution KD, autoregressive pretraining, spike regularization | 10 | A promising direction when inference structure stays fixed, but each proposed loss needs a clean validation plan [E03, E15, E17, E20]. |

## Refined hierarchy

The initial candidate list is retained but interpreted through four higher-level branches:

1. **Static structural reduction:** depth, width, backbone, pruning and resolution.
2. **Input- or time-dependent reduction:** sparsification, conditional computation, template reuse and timestep.
3. **Information preservation:** distillation, target-aware representation, robustness, memory and interaction.
4. **Representation/training change:** autoregression, temporal/motion modeling, SNN computation and loss redesign.

This split prevents three common category errors: equating pruning with conditional execution, equating a cached template with a small resident model, and equating spike-valued tensors with sparse hardware execution.

## Evidence and uncertainty

- The 30-paper robustness incidence and other long-tail mappings come from supplied titles/abstracts and remain `LOW`-confidence screening edges [E01, E02].
- High-relevance mechanisms are checked against primary papers and official code in the paper cards and anchor decompositions [E03-E21].
- No paper was promoted to a third anchor. The two neighborhood nodes record discovery provenance only.
