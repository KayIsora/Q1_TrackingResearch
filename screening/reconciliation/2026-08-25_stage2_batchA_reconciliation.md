# Stage 2A — Batch A Manager↔Codex evidence reconciliation

**Date:** 2026-08-25  
**Status:** BATCH A RECONCILIATION COMPLETE; HG4/HG5 resolved where the locked evidence threshold is met.  
**Batch:** CX007 SpikeTrack, CX009 UETrack, CX010 UTPTrack, CX013 FARTrack, CX014 GOT-Edit.  
**Governing protocol:** `docs/11_systematic_screening_protocol.md`.  
**Input lanes:** `screening/manager/2026-08-24_stage2_batchA_scientific_audit.md` and `screening/codex/2026-08-24_stage2_batchA_code_audit.md`.

## 1. Reconciliation rule

The two independent evidence lanes are reconciled field by field. Paper claims do not override contradictory code facts, and code-visible cost does not automatically become scientific redundancy. `PASS`, `FAIL`, and `PENDING` follow the frozen HG4/HG5 definitions in `docs/11_systematic_screening_protocol.md`.

No Nano FPS is inferred from FLOPs, desktop GPU, AGX, CPU, NPU, parameter count, or energy estimates. No S1–S7 score is assigned. HG6 remains unstarted.

## 2. Key factual reconciliations

### CX007 — SpikeTrack

Manager paper evidence established the SNN/SDTV3 family, Base/Small variants, T=1/T=3 variants, eight-RTX4090 author training, and the author-reported weakness on visually similar distractors.

Codex code inspection materially refines the implementation interpretation:

- T=1/T=3 is the template/time dimension exposed to the spike/retrieval modules; it is not a persistent neuron clock across video frames.
- The cached inference path runs six Memory Retrieval Modules on every frame; T3 repeats the search query over three template slices.
- Template encoding is cached and recomputed only on qualifying T3 template refreshes.
- The released inference arithmetic is dense Conv/MatMul plus clamp/round spike quantization; no sparse/event-driven CUDA kernel was found.
- The center-box decode occurs twice per frame.
- The T3 YAML records a T1 pretrained checkpoint, but the inspected training path does not consume that field.

The author-reported similar-object weakness remains valid, but any future compute hypothesis must target the actual cached MRM/template-time execution rather than an assumed cross-frame spiking recurrence.

### CX009 — UETrack

Manager evidence established the compact B/S/T family, TP-MoE, training-time TAD, and strong reported edge-oriented efficiency.

Codex establishes that:

- the RGB path still runs a CLIP text encoding once per sequence using zero token IDs and keeps one projected text token in the per-frame sequence;
- the full CLIP object and other unused inference-side modules remain resident in the Python model construction;
- TP-MoE is dense soft routing: every expert executes every frame and a dense padded routing matrix is materialized;
- TAD/teacher functionality is training-side rather than a per-frame deployed-teacher cost;
- the static template is reprocessed through the encoder on every frame rather than cached as encoded features.

Thus the earlier possibility of conditionally executed experts is rejected as a code fact; a future hypothesis, if any, must start from the observed dense all-expert execution.

### CX010 — UTPTrack

Manager evidence established that UTPTrack already jointly prunes search, static-template, and dynamic-template tokens at high reported pruning ratios.

Codex establishes that the generic RGB `UTPTrack-O` path:

- uses ViT-B/16, 12 blocks, width 768;
- performs content-dependent physical sequence shrink after the attention residual at configured CE/DTE/STE layers;
- uses full sort, gather, boolean/index operations, concatenation, and final scatter restoration;
- re-embeds both static and dynamic image templates on every frame; there is no encoded-template cache;
- restores only the search stream to a dense grid for the center head;
- has no working pinned `ostrackcmp` profiler/export path in the released tree.

This strengthens UTPTrack's role as a novelty adversary for ordinary token pruning while leaving deployment-runtime behavior unresolved.

### CX013 — FARTrack

Manager paper evidence established the TSSD + IFAS design, small Tiny/Nano/Pico family, and the author-reported long-failure/template-invalidity limitation.

Codex materially changes the implementation picture:

- the released final sparse tracker makes one network call per frame and predicts all four coordinate distributions in parallel; there are not four recurrent coordinate-generation model calls;
- IFAS in the released final path masks attention positions but does not physically remove tokens: all 15 blocks retain the full 445-token Q/K/V and attention shape;
- five template images are patch-embedded every frame;
- mask generation executes every frame using `argsort`, nested Python writes, and multiple candidate masks;
- new templates and mask histories are appended without an explicit sequence-length cap while only five templates are selected as the active model input.

These code facts make the paper-level phrase “sparsification” insufficient evidence of actual reduced dense-attention shape in the released runtime. They also expose concrete profiling targets, but they are not yet promoted to confirmed scientific redundancy.

### CX014 — GOT-Edit

Manager paper evidence established that geometry extraction dominates reported compute and that the paper already explores StreamVGGT / lower fixed geometry frequency; it also reports weaker geometry usefulness under fast motion/viewpoint change.

Codex confirms an even heavier released runtime:

- one DINOv2 ViT-L semantic path runs on the current frame;
- DA3-L contains another ViT-L-class encoder and processes the initial reference, dynamic reference, and current frame on every tracked frame;
- two ToMP filter-prediction paths plus fusion/JEPA execute;
- a 256×256 covariance, SVD, null-space projector, and projected online update execute every frame;
- reference geometry is recomputed rather than consumed from the available cache helpers;
- the audited DA3 feature path is under `torch.no_grad()`, creating an unresolved mismatch with DoRA parameters that the training setting places in the optimizer.

The structural cost is therefore not merely a paper FLOP estimate; the released graph contains two large foundation-model paths plus per-frame online linear algebra.

## 3. HG4 — RTX 3060 12 GB research feasibility

### CX007 SpikeTrack — **PASS**

Reasoning under the locked gate:

- official final checkpoints exist;
- released Small/Base models are bounded-size architectures rather than structurally multi-GPU-only systems;
- meaningful checkpoint-based fine-tuning or new-module training can plausibly reduce per-process batch and use accumulation/AMP if needed;
- the eight-GPU author recipe is not itself a hard-gate failure.

Residual risk: the released T1→T3 initialization path is inconsistent and no 12-GB peak-memory run exists. This is reproduction/training-engineering risk, not evidence that the research loop structurally requires unavailable hardware.

### CX009 UETrack — **PASS**

- official student/backbone/teacher resources exist;
- B/S/T students are compact;
- a single-GPU debug path is documented;
- the teacher and broad multi-modal full recipe make full author-recipe reproduction expensive, but checkpoint-based meaningful student/new-module fine-tuning is plausible on one 12-GB GPU.

The gate does not require reproducing 500 epochs × 100k samples/epoch on the author's exact distributed budget.

### CX010 UTPTrack — **PASS**

- official RGB checkpoint/training paths exist;
- the model is a conventional ViT-B/16 tracker with explicit 256/384 recipes;
- meaningful checkpoint-based fine-tuning with reduced batch and normal memory-saving techniques is plausible on 12 GB even though the released single-process launcher has unresolved distributed-code behavior.

This is a feasibility PASS, not a statement that the full official 300-epoch multi-process recipe is cheap.

### CX013 FARTrack — **PASS**

- released final checkpoints and small Tiny/Nano/Pico models give a credible initialization path;
- although official training is three-stage and sparse training uses 32-frame sequences, research on a new module can begin from the final checkpoint and use reduced batch/accumulation rather than repeating the entire farm;
- no structural dependence on inaccessible model scale is present.

### CX014 GOT-Edit — **PENDING**

The released training setting freezes large base components and uses no-grad geometry execution plus partial activation checkpointing, which is favorable. However the actual single-GPU memory requirement is not established, the runtime contains two ViT-L-class paths, and the no-grad/DoRA trainability mismatch leaves the intended trainable set unresolved. Under the locked protocol this is insufficient to certify single-3060 research feasibility without a local profile or a clarified training path.

## 4. HG5 — Jetson Nano B01 deployment plausibility

### CX007 SpikeTrack — **PENDING**

The model family is small enough to merit further examination, but its released SNN implementation uses dense Conv/MatMul plus Python timestep/control logic and no TensorRT/ONNX path. Whether these operators and the six-MRM cached path are efficient enough on Maxwell CUDA requires export/runtime profiling. The paper's SNN energy model is not Nano evidence.

### CX009 UETrack — **PASS**

The deployed student family is explicitly compact (reported 6–13M parameters, 1.8–3.2G FLOPs) and the per-frame neural operations are standard dense conv/attention/softmax/einsum rather than a structurally huge foundation-model path. Unused resident CLIP/task modules and zero-text initialization can be separated from the steady-state RGB student path by normal deployment engineering. No INT8 rescue is structurally required for plausibility.

This PASS means only that a credible Nano path exists; it does not claim any Nano FPS.

### CX010 UTPTrack — **PENDING**

The paper demonstrates substantial token/MAC reduction, but the audited RGB runtime remains a ViT-B/16 path and uses content-dependent sort/gather/boolean/scatter operations with shortened intermediate sequences. The exact TensorRT behavior and actual runtime benefit of these dynamic operations on Nano cannot be inferred from MAC counts or RTX2080Ti speed. Code/device profiling is required before PASS or FAIL.

### CX013 FARTrack — **PASS**

The final family is structurally small and does not require a large backbone/foundation model. Although the released IFAS implementation retains full dense attention shape and its Python mask/history handling is deployment-unfriendly, there is a concrete mechanism-level path to bounded state and more efficient sparse/template execution without relying solely on INT8 or generic post-hoc pruning. The present PASS is deployment plausibility only; actual Nano throughput and long-run memory remain mandatory measurements later.

### CX014 GOT-Edit — **FAIL**

The released runtime depends on two ViT-L-class feature paths, DA3-L over a three-frame stack every frame, two filter-prediction paths, and per-frame covariance/SVD/projector operations. Paper-level geometry compute is already orders of magnitude larger than the tracker-only path, and the paper itself explores reduced geometry frequency. Reaching the Nano objective would require replacing or removing a core heavy geometry/foundation-model dependency rather than a credible incremental mechanism-based reduction. Under the locked HG5 rule this is beyond “plausible deployment headroom” and falls into the “compress later and hope / major replacement” regime.

No Nano FPS is inferred in making this structural FAIL decision.

## 5. Batch-A gate state after reconciliation

| Candidate | HG4 | HG5 | Batch-A status |
|---|---:|---:|---|
| CX007 SpikeTrack | PASS | PENDING | REMAINS UNRESOLVED; targeted deployment/export profile required before HG6 |
| CX009 UETrack | PASS | PASS | SURVIVES HG4/HG5; hold for later candidate-specific gap/HG6 stage after systematic batch audit |
| CX010 UTPTrack | PASS | PENDING | REMAINS UNRESOLVED; targeted deployment/export profile required before HG6 |
| CX013 FARTrack | PASS | PASS | SURVIVES HG4/HG5; hold for later candidate-specific gap/HG6 stage after systematic batch audit |
| CX014 GOT-Edit | PENDING | FAIL | EXCLUDED FROM MAIN-BASELINE PROGRESSION BY HG5; retained as literature/novelty reference |

No candidate is shortlisted and no ranking is implied.

## 6. Batch-A hypotheses retained for later, without promotion

- **SpikeTrack:** author-supported similar-distractor weakness plus always-on six-MRM/template-time processing is a testable research direction, but the actual cost and any shared mechanism remain unproven.
- **UETrack:** dense all-expert TP-MoE and repeated static-template processing are measurable engineering cost sites, but no candidate-specific generic RGB robustness weakness is established yet.
- **UTPTrack:** static/dynamic/search pruning is already the method's contribution; further ordinary pruning has poor novelty premise. Static-template re-embedding and dynamic operator overhead are profile targets, not yet a research gap.
- **FARTrack:** invalid-template risk after prolonged failure is author-supported; released IFAS does not physically shrink dense attention and history grows without a cap. A potential reliability/efficiency coupling remains a hypothesis and must face later mechanism-level novelty audit.
- **GOT-Edit:** geometry cost and geometry unreliability under fast motion/viewpoint change are structurally related signals, but the Nano hard gate fails before this can become a main-baseline path. GOT-Edit remains valuable as a novelty/reference adversary.

## 7. Next locked action

Batch A reconciliation is complete. Per the predeclared batch plan, **Batch B may now activate** for independent evidence extraction:

- CX017 GOT-JEPA
- CX020 SAMURAI
- CX024 DAM4SAM
- CX037 SSTrack-AAAI
- CX038 MCITrack

Batch B must repeat the same two-lane process: Manager paper/scientific audit + Codex code/engineering audit → reconciliation → HG4/HG5 decisions. Batch C and HG6 remain locked until their scheduled point.

## 8. State

- Batch A Manager audit: **COMPLETE**
- Batch A Codex audit: **COMPLETE**
- Batch A reconciliation: **COMPLETE**
- Batch A HG4/HG5: **RESOLVED where evidence permits; two HG5 and one HG4 remain PENDING**
- Batch B: **AUTHORIZED TO ACTIVATE**
- HG6: **NOT STARTED**
- S1–S7 soft scoring: **NOT STARTED**
- Primary shortlist: **NONE**
- Main baseline: **NONE**
- Proposed architecture: **NONE**
