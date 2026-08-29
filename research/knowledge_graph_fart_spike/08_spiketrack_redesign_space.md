# First-pass SpikeTrack redesign space

## Boundary

This is a set of independent, falsifiable experiment families. It is **not** a final architecture, a ranked third baseline, or permission to combine all ideas. `PROMISING` means evidence justifies a controlled SpikeTrack-specific test; it does not mean expected success. The historical conditional whole-MRM1 skip remains `DIAG_FAIL`, and its sealed hold-out is unavailable [E08].

## Manager-review priority layer

The ten register IDs are not ten equal-priority scientific directions.

| Priority | Register items | Interpretation |
|---|---|---|
| **Primary scientific hypothesis family** | **P01 + P02 jointly** | FARTrack-inspired static stage/block or capacity reduction plus tracking-specific task-facing preservation/distillation. This is the strongest current lane, with `HIGH` novelty collision and no approved final mechanism. |
| **Supporting donor for the primary family** | **P04** | CompressTracker supplies stage-replacement and stage-wise training evidence; it is not automatically a separate contribution. |
| **Engineering enablement** | **P06** | parity/runtime/export structure; important deployment work, not the primary scientific claim. |
| **Secondary / exploratory** | **P03, P05, P09** | template-memory compression, cross-resolution training, and quality-controlled updates may be investigated later. |
| **Defer / high collision / indirect compute benefit** | **P07, P08, P10 and generic dynamic routes** | do not present as equal-priority first experiments. Training-only benefit or conditional routing does not itself prove practical compute reduction. |

For the primary family, **what to reduce** is fixed stage/block depth or capacity; **what to preserve** is tracking-specific/task-facing behavior; and **how to train** is a SpikeTrack-compatible teacher/student or stage-wise compression process. This prioritization does not select an architecture.

## Promising transfer register

Every `PROMISING` cell in `07_transfer_matrix.csv` is resolved exactly once below.

### P01 — FARTrack task-facing distillation -> SpikeTrack stage/block depth

1. **Source principle:** supervise shallow prefixes with the deeper adjacent task distribution rather than generic features [E03, E04].
2. **Current analogue:** SpikeTrack has staged backbone blocks, six MRM-conditioned states, and a task head [E05, E23].
3. **Plausibility:** static prefix variants can be trained without any input-conditioned skip policy.
4. **Required change:** define fixed candidate depths, retain compatible MRM sites, and attach training-only task exits.
5. **Retraining:** full teacher/student or staged fine-tuning is required.
6. **Likely benefit:** fewer resident blocks and dense kernels per frame.
7. **Accuracy risk:** removed stages may carry fine-grained semantics already weak in SpikeTrack.
8. **Novelty risk:** `HIGH`; FARTrack, MixFormerV2, CompressTracker, LiteTrack, and HiT occupy adjacent space [E03, E10-E12, E18].

### P02 — FARTrack task-facing distillation -> SpikeTrack loss/training

1. **Source principle:** preserve task-relevant output distributions during compression [E03].
2. **Current analogue:** SpikeTrack currently uses focal/GIoU/L1 but no distillation objective [E05].
3. **Plausibility:** a frozen full SpikeTrack can supervise a smaller SpikeTrack without changing inference inputs.
4. **Required change:** choose task-facing heatmap/box or MRM-conditioned logits and explicitly avoid indiscriminate hidden matching.
5. **Retraining:** yes; teacher is training-only.
6. **Likely benefit:** no direct runtime overhead and better accuracy retention for another structural reduction.
7. **Accuracy risk:** teacher errors and coarse spikes may be overfit; multiple losses can conflict.
8. **Novelty risk:** `HIGH` for generic KD, `MEDIUM` only if the SpikeTrack-specific signal and causal ablation are distinct [E10, E11].

### P03 — FARTrack temporal amortization -> SpikeTrack template memory

1. **Source principle:** store a conservative representation-reduction decision with each template and reuse it across frames [E03].
2. **Current analogue:** SpikeTrack already rebuilds and caches six K-transpose-V memories only at initialization/update [E05, E23].
3. **Plausibility:** compression metadata can be generated at update time, where template work already occurs.
4. **Required change:** learn or derive a fixed per-template channel/head/low-rank selection compatible with all six memories; no per-frame selector.
5. **Retraining:** yes, with fixed selection semantics at inference.
6. **Likely benefit:** lower cache-retrieval dimensions and possibly fewer dense MRM operations.
7. **Accuracy risk:** persistent mistakes survive many frames; fixed-first-template and quality gates are necessary.
8. **Novelty risk:** `HIGH` for generic sparsity; `MEDIUM` for a well-justified spike-memory-specific amortized representation [E19, E21].

### P04 — CompressTracker stage replacement -> SpikeTrack stage/block depth

1. **Source principle:** replace capacity stage by stage while preserving teacher predictions and stage features [E10].
2. **Current analogue:** SpikeTrack’s CNN/Transformer stages have known boundaries and paired MRM sites [E23].
3. **Plausibility:** one stage can be redesigned while other teacher stages remain frozen, limiting simultaneous interface drift.
4. **Required change:** define spike-compatible student stages and align only semantically comparable temporal/channel states.
5. **Retraining:** staged retraining followed by end-to-end fine-tuning.
6. **Likely benefit:** controlled reductions in block depth or width with attributable savings.
7. **Accuracy risk:** feature mimicking can suppress beneficial spike statistics or destabilize NI-LIF decay.
8. **Novelty risk:** `HIGH` for the compression framework; only a SpikeTrack-specific finding with careful ablation has headroom.

### P05 — LoReTrack cross-resolution distillation -> SpikeTrack input resolution

1. **Source principle:** use a same-architecture high-resolution teacher to restore Q/K/V interaction and target discrimination lost at low resolution [E15].
2. **Current analogue:** SpikeTrack has 256 and 384 families and resolution-specific MRM grids/positional embeddings [E05, E23].
3. **Plausibility:** the 384 model can provide aligned task and interaction targets for a 256 or smaller student.
4. **Required change:** define spike-compatible cross-resolution targets for MRM Q-memory outputs and center maps; rebuild positional embeddings.
5. **Retraining:** full student training/fine-tuning is required.
6. **Likely benefit:** fewer spatial tokens in backbone, MRM pooling/retrieval, and head.
7. **Accuracy risk:** small targets, deformation, and fine-grained semantics are already SpikeTrack weaknesses.
8. **Novelty risk:** `HIGH`; LoReTrack directly occupies cross-resolution tracking KD [E15].

### P06 — AsymTrack template-once principle -> SpikeTrack runtime/export structure

1. **Source principle:** separate stable template work from per-frame search work [E09].
2. **Current analogue:** SpikeTrack already computes six template memories infrequently but instantiates a second full template module [E07, E23].
3. **Plausibility:** compatible parameter storage may be shared or serialized as a template-build subgraph without changing mathematical outputs.
4. **Required change:** parity-preserving module consolidation and a flat, typed six-cache binding interface; do not copy direct modulation.
5. **Retraining:** no for pure parity cleanup; yes if computation or cache representation changes.
6. **Likely benefit:** lower resident parameter storage and a clearer ONNX/TensorRT boundary.
7. **Accuracy risk:** low only after strict checkpoint/output parity; weight aliasing and branch-specific operators can break equivalence.
8. **Novelty risk:** `LOW` scientifically and `HIGH` as prior engineering principle; treat it as deployment enabling work, not the paper contribution [E09, E24].

### P07 — ARPTrack sequential pretraining -> SpikeTrack loss/training

1. **Source principle:** learn ordered appearance and motion context offline with autoregressive/backtracking objectives [E17].
2. **Current analogue:** SpikeTrack uses independent pair training plus T3 fine-tuning and lacks an explicit motion/context objective [E05].
3. **Plausibility:** training data sequences can supervise the same inference graph.
4. **Required change:** adapt sequential objectives to NI-LIF states and define which template/search stages receive them.
5. **Retraining:** full pretraining and downstream fine-tuning.
6. **Likely benefit:** potential accuracy recovery for a smaller static model with no new inference module.
7. **Accuracy risk:** expensive training, objective mismatch, and no guaranteed compute reduction.
8. **Novelty risk:** `HIGH` for sequential pretraining, `MEDIUM` for a carefully scoped spiking adaptation.

### P08 — SpikeFET regularization -> SpikeTrack loss/training

1. **Source principle:** constrain spiking representations with spatial-temporal regularization [E20].
2. **Current analogue:** SpikeTrack has learned NI-LIF dynamics but no spike-rate/energy/sparsity regularizer [E05].
3. **Plausibility:** a training-only regularizer can act on NI-LIF outputs without requiring event input.
4. **Required change:** formulate an RGB-only objective tied to measured firing/statistical behavior and exclude frame-event fusion assumptions.
5. **Retraining:** yes.
6. **Likely benefit:** lower firing activity in the analytical model and possibly more compressible states; conventional GPU speedup is not guaranteed.
7. **Accuracy risk:** over-sparsification may worsen SpikeTrack’s fine-grained semantic deficit.
8. **Novelty risk:** `HIGH` because SpikeFET is peer-reviewed direct SNN-tracking prior art [E20].

### P09 — STDTrack quality control -> SpikeTrack template memory

1. **Source principle:** retain temporal evidence according to reliability rather than age alone [E21].
2. **Current analogue:** SpikeTrack preserves the first template but rotates later templates using localization score and fixed intervals [E05].
3. **Plausibility:** quality control can run only at template-update events and leave every-frame MRM execution fixed.
4. **Required change:** define a calibrated update-quality target and deterministic queue policy; do not gate whole MRMs.
5. **Retraining:** likely yes for a learned quality signal; no for a pre-registered deterministic policy study.
6. **Likely benefit:** fewer harmful full-template rebuilds and less drift, with small amortized overhead.
7. **Accuracy risk:** conservative updates may fail under appearance change; learned confidence can be miscalibrated.
8. **Novelty risk:** `HIGH`; quality-based memory is established, so contribution must be spike-cache-specific and empirically distinct [E21].

### P10 — HiT hierarchy -> SpikeTrack search backbone

1. **Source principle:** use a lightweight hierarchy and bridge rather than a heavy flat feature extractor [E18].
2. **Current analogue:** SpikeTrack already has a four-stage hierarchy but retains 12 blocks and six MRM injections [E23].
3. **Plausibility:** stage widths/depths and bridge-like feature transport can be redesigned around existing spatial scales.
4. **Required change:** construct a spike-native small hierarchy and remap MRM locations/dimensions; do not transplant a conventional ViT block.
5. **Retraining:** from scratch or from a carefully aligned teacher.
6. **Likely benefit:** fewer dense stage blocks, lower activations, and potentially fewer/lighter MRM sites.
7. **Accuracy risk:** losing late semantic depth may amplify similar-object and deformation failures.
8. **Novelty risk:** `HIGH`; lightweight hierarchical tracking is established [E18].

## Independent redesign dimensions

| Dimension | What FARTrack teaches | Other donor evidence | Current SpikeTrack constraint | Falsifiable first test | Retraining | Expected compute effect | Novelty risk |
|---|---|---|---|---|---|---|---|
| A. Depth | task-facing adjacent-depth supervision | CompressTracker, MixFormerV2, LiteTrack, HiT [E10-E12, E18] | 2/2/6/2 blocks with six fixed MRM sites | train one static shallower family with predeclared sites and full teacher | Yes | fewer blocks/kernels/resident weights | High |
| B. Width | separate capacity from token work | stage replacement [E10] | width changes every backbone/MRM/cache/head interface | one uniformly scaled Small student with dimension-matched teacher adapters | Yes | quadratic/linear reductions by operator | Medium-High |
| C. Timestep | preserve task evidence while reducing temporal work | SpikeFET regularization [E20] | T1/T3 changes per-timestep MRM conv/fusion; search expands inside MRM | compare trained T1 and bounded learned/regularized T variants on fresh validation | Yes | lower MRM temporal work/cache | High |
| D. Memory | amortize conservative decisions | STDTrack quality control, MCITrack context [E16, E21] | six compact caches but full rebuild and weak update confidence | quality-controlled update or fixed low-rank cache, one at a time | Likely | lower updates/cache interaction; context may increase cost | High |
| E. MRM structure | supervise the task-facing effect, not copy attention | CompressTracker stage guidance [E10] | six dense retrieval+MLP modules, early pool/upsample | statically redesign one MRM family and retrain; no conditional whole-MRM1 gate | Yes | fewer projections/retrieval/MLP ops | High |
| F. Sparsity | derive and persist salience; use moderate ratios | CPDATrack [E19] | dense tensors/kernels and compact K-transpose-V caches | fixed channel/head/low-rank cache compression at update time | Yes | only valuable if dimensions/operators actually shrink | High |
| G. Distillation | task-specific adjacent/prefix signals | CompressTracker, LoReTrack, ARPTrack [E10, E15, E17] | no KD loss | one teacher signal per structural experiment | Yes | training-only overhead; accuracy retention | High |
| H. Head | task outputs can supervise shallower states | FastSeqTrack, STDTrack [E14, E21] | three four-stage towers execute every frame | reparameterize or statically shorten towers with full output parity target | Yes unless exact fold | lower conv/head kernels | Medium-High |
| I. Loss/training | move preservation work offline | ARPTrack, SpikeFET [E17, E20] | no energy/sparsity/memory-quality objective | isolate one additional objective with predeclared metric and ablation | Yes | no direct inference cost; may enable smaller model | High |
| J. Input resolution | combine reduction with task-aware distillation | LoReTrack [E15] | fixed 16x16/24x24 position/cache grids | 384-teacher -> 256/student before any smaller-resolution claim | Yes | fewer spatial activations and head cells | High |

## Experimental guardrails

1. Change one dimension first and measure actual operator latency, resident memory, accuracy, and exportability.
2. Keep theoretical spike energy, analytical operation count, CUDA latency, and board power as separate outcomes.
3. Require retraining wherever learned dimensions, timesteps, cache semantics, MRM structure, or loss change.
4. Use fresh development/validation data for every new conditional hypothesis; never reuse the consumed MRM1 hold-out [E08].
5. Treat exact parity cleanup separately from scientific redesign.
6. Treat P01+P02 as one predeclared hypothesis family, with P04 as supporting training evidence; do not combine other register items until individual causal evidence exists and Manager authorizes a later synthesis phase.
