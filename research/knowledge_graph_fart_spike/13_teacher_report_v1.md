# Teacher report — FARTrack + SpikeTrack Knowledge Graph V1

## Executive message

> **We are no longer searching for a third main tracker. Other trackers are knowledge donors.**

> **FARTrack is not discarded because it is already strong. Its successful lightweight-design methodology becomes an important knowledge source for redesigning SpikeTrack.**

Version 1 converts two Connected Papers discovery neighborhoods into a manually/evidence-derived semantic graph. The graph separates bibliographic neighborhood membership from architectural meaning; it never reconstructs unavailable Connected Papers edges or weights [E01, E02].

```text
Connected Papers exports
        -> 82 raw literature records
        -> 74 verified unique papers
        -> multi-label solution families
        -> primary-paper mechanism evidence
        -> FARTrack and SpikeTrack anchor decompositions
        -> evidence-scoped transfer matrix
        -> independent SpikeTrack redesign dimensions
        -> Manager review
```

## 1. Inventory result

| Item | Result |
|---|---:|
| FARTrack export | 41 records |
| SpikeTrack export | 41 records |
| Raw total | 82 records |
| Exact cross-export overlaps | 7 papers |
| Mechanical unique clusters | 75 |
| Manual LoReTrack preprint/proceedings merge | -1 |
| Final unique inventory | 74 papers |
| Final publication statuses | 30 conference, 32 journal, 12 arXiv/preprint only |
| Relevance | 2 primary, 70 supporting, 1 historical, 1 out of scope |
| Named neuroscience collision graph | absent; 0 rows parsed |

LoReTrack’s two arXiv records and IROS record are versions of one work and are represented by one canonical IROS paper with the arXiv ID retained [E15]. The previously ambiguous OiRT item was verified as visual SOT [E25], and the VideoTrack supplementary record was canonicalized to its CVPR 2023 paper [E26]. The unrelated CSCL continual-classification paper remains in the inventory for provenance but has no donor role.

## 2. Recurring solution families

The most frequent metadata-screened families are robustness/distractor handling (30), dynamic/conditional computation (14), asymmetric template-search design (12), relation/cross-attention modeling (12), lightweight backbones (11), autoregressive/sequence modeling (11), target-aware representation (11), training/loss redesign (10), temporal/video memory (9), and motion modeling, compression/distillation, and pruning (7 each) [E01, E02]. These are multi-label incidences, not quality scores.

Three conclusions follow:

1. Efficiency literature repeatedly attacks **structure**, **input-dependent work**, and **information preservation** together; a single “lightweight tracker” category is too coarse.
2. Asymmetry/template reuse is already mature prior art, so simply separating branches is weak novelty headroom [E09, E12].
3. Dynamic skipping is crowded and must not be used to reframe the failed MRM1 predictor [E08, E13].

## 3. RQ1 — Why FARTrack reaches its speed-accuracy trade-off

FARTrack combines two orthogonal reductions [E03]:

- **Task-Specific Self-Distillation** conditions intermediate task-logit exits so shallower prefixes preserve coordinate behavior. It reduces static depth and resident capacity.
- **Inter-frame Autoregressive Sparsification** derives template salience from existing attention, stores a conservative token mask with each template, and reuses that decision. It targets repeated token work.

The Tiny/Nano/Pico family changes depth from 15 to 10 to 6 layers while holding ViT-Tiny width and input shape; Nano preserves much more reported accuracy than Pico [E03]. The main design lesson is not “copy TSSD”: supervise the task-facing information whose loss causes tracker failure, and separate model-size reduction from token/activation reduction.

The public code introduces important uncertainty: historical trajectory tokens are not actually added in the sparse inference encoder; the selected paper salience formula, normalization path, training schedule, and dense execution do not fully match the public implementation [E04]. FARTrack therefore remains a strong method/principle anchor, but strict paper-code parity needs author clarification.

## 4. RQ2 — What determines SpikeTrack cost

SpikeTrack’s theoretical SNN efficiency comes from normalized-integer spikes, analytical replacement of MACs by sparse accumulates, softmax-free linear spike attention, one-timestep search outside MRM expansion, compact `K^T V` memories, and amortized template processing [E05].

Practical conventional-GPU cost comes from a different layer of reality:

- dense FP32 Conv/Linear/matmul on spike-valued tensors;
- six MRMs, each with Q projection, repeated retrieval, temporal processing, fusion, projection, and an outer MLP;
- physically separate resident template and search modules;
- three multi-stage head towers;
- custom quantization, Python temporal loops, dictionary cache boundaries, and host-side tracking state [E07, E23, E24].

The six cache tensors are small; the larger memory problem is resident modules and activations. The accepted S256-T1 trace contains 19,423,216 resident parameters and measured about 3.2 end-to-end FPS on an MX250 under the exact frozen FP32 setup [E07]. This is **not** a Jetson result. Paper mJ values are analytical operation-energy estimates, not measured board power [E05].

## 5. RQ3/RQ4 — Repeated families and safe transfer

The highest-value donor papers are not replacement baselines:

| Donor | What it contributes | Main caution |
|---|---|---|
| CompressTracker [E10] | stage replacement and stage-wise teacher guidance | conventional transformer evidence |
| MixFormerV2 [E11] | deep-to-shallow and dense-to-sparse distillation | high collision with generic KD claims |
| AsymTrack [E09] | template-once runtime separation | direct modulation is incompatible with SpikeTrack ablation |
| LiteTrack [E12] | asynchronous template reuse and static layer pruning | SpikeTrack already has cache asymmetry |
| LoReTrack [E15] | cross-resolution interaction/discrimination KD | high collision and small-target risk |
| ARPTrack [E17] | offline appearance-motion sequential pretraining | no guaranteed inference reduction |
| HiT [E18] | lightweight hierarchy and bridge principle | full SNN redesign/retraining required |
| SpikeFET [E20] | spike-specific spatial-temporal regularization | different frame-event modality |
| STDTrack [E21] | reliability-aware memory update and reparameterized head | external to the supplied neighborhoods |
| DyTrack [E13] | adaptive-computation collision/negative control | does not validate MRM skipping |

The transfer rule is functional analogy: FARTrack or another donor demonstrates a principle; SpikeTrack has a component serving an analogous tracking function; a new test must be expressed in SpikeTrack’s spike/cache/MRM representation and retrained when learned structure changes.

## 6. RQ5 — First-pass redesign dimensions

Ten independent dimensions remain open: depth, width, timestep, memory, MRM structure, sparsity, distillation, head, loss/training, and input resolution. The most defensible first tests are static task-distilled depth, staged spike-compatible compression, cross-resolution teacher/student training, quality-controlled template updates, and parity-preserving runtime/module consolidation. Each has explicit benefit, accuracy risk, retraining need, and novelty collision in `08_spiketrack_redesign_space.md`.

No evidence yet supports combining these into one model. Exact parity cleanup should be evaluated separately from a scientific redesign.

## 7. RQ6 — Novelty headroom warnings

Novelty collision is strongest for generic depth/KD, low-resolution KD, asymmetric template-once tracking, target-aware token pruning, dynamic exits/routes, and generic SNN regularization [E09-E15, E18-E20]. A future claim needs a SpikeTrack-specific mechanism, causal ablation, and practical edge outcome rather than a renaming of established ideas.

## 8. Historical null result

The frozen conditional whole-MRM1 predictor failed its sealed hold-out, and the hold-out is consumed [E08]. It is retained only as a null-result boundary. It cannot be rescued, retuned, inverted, or used to justify MRM removal. Any genuinely new conditional hypothesis requires new development and validation data.

## 9. What Version 1 establishes

- two fixed anchor trackers and 74-paper inventory;
- explicit discovery-vs-semantic graph separation;
- primary-evidence architecture decompositions with paper/code mismatches;
- a multi-label solution taxonomy and 15 high-relevance cards;
- a component-level transfer matrix;
- ten non-combined, falsifiable redesign dimensions;
- CSV, GraphML, and Mermaid graph views.

## 10. What remains unresolved

- Jetson Nano latency, power, temperature, memory, and energy;
- successful ONNX/TensorRT export and output parity;
- sparse-spike kernels on conventional edge GPUs;
- FARTrack paper/public-code parity questions;
- trained accuracy/efficiency results for any SpikeTrack structural change;
- manual primary-source spot checks for long-tail publication/code metadata.

**Terminal state:** `KNOWLEDGE_GRAPH_V1_READY_FOR_MANAGER_REVIEW`
