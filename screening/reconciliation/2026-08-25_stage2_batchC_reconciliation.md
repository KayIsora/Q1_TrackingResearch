# Stage 2A — Batch C reconciliation and HG4/HG5 gate decisions

**Date:** 2026-08-25  
**Status:** BATCH C RECONCILED; Batch D may activate only for HG1/HG2/HG3-PASS candidates in the predeclared order.  
**Inputs:** Manager scientific audit `screening/manager/2026-08-25_stage2_batchC_scientific_audit.md` and Codex code audit `screening/codex/2026-08-25_stage2_batchC_code_audit.md`.  
**Governing protocol:** `docs/11_systematic_screening_protocol.md`.

## Boundary

This reconciliation decides only **HG4 — RTX 3060 12 GB research feasibility** and **HG5 — Jetson Nano B01 deployment plausibility** where the combined paper/code evidence is sufficient. It does not begin HG6, assign S1–S7, rank candidates, shortlist a baseline, or approve a proposed architecture.

A `PASS` is a project research gate, not an experimental result. HG5 PASS means that a credible structural path exists; it is **not** a Jetson Nano FPS, latency, RAM, power, or thermal claim. Actual device profiling remains mandatory later.

## CX043 — SUTrack

**Final HG4: PASS**  
**Final HG5: PASS**

### Reconciled evidence

- The family supplies five exact released configurations/checkpoints, including the small T224 operating point. T224 uses one 112-pixel template, one 224-pixel search, 247 main-attention tokens, and a Fast-iTPN Tiny path. The exact code-derived encoder/head/task subtotal is about 27.85M parameters, excluding the separately instantiated CLIP model.
- The official release provides a single-GPU training entry point. The full unified recipe is long and uses nine datasets, 180 epochs, batch 32 per process, no released AMP/checkpointing/accumulation configuration, and no RGB-only recipe; however checkpoint-based research does not require reproducing the full original multi-process throughput.
- In pure RGB inference, the RGB image is duplicated into a six-channel input. The CLIP text encoder runs once on zero token IDs and its projected token is cached; the full CLIP object remains resident. Task-recognition loss/head is active during training but the released tracker does not execute the task classifier at inference.
- T224 has bounded state and one static template. B/L variants use a bounded fixed-plus-dynamic two-template list. Raw templates are re-encoded every frame. No custom CUDA extension, growing temporal history, or mandatory sensor-specific branch appears in the RGB path.
- No official ONNX/TensorRT path or controlled Nano timing protocol is released; the reported AGX result cannot establish Nano speed.

### Gate rationale

**HG4 PASS:** official checkpoints, a single-GPU path, the T224/B224 operating points, and ordinary checkpoint-based fine-tuning provide a credible RTX 3060 research loop using reduced batch, AMP and/or accumulation if needed. This does not claim that the full nine-dataset recipe at its published batch fits 12 GB unchanged.

**HG5 PASS:** T224 provides a bounded, fixed-size, comparatively small RGB tracker graph with standard dense operators and no structurally mandatory multimodal sensor branch. The one-time zero-text/CLIP setup and resident unused inference components are engineering cleanup targets rather than evidence that the whole core must be replaced. Export and Nano profiling remain required before any deployment claim.

## CX044 — AsymTrack

**Final HG4: PASS**  
**Final HG5: PASS**

### Reconciled evidence

- The released fused inference graphs contain approximately 3.239M parameters for Tiny and 3.549M for Small/Base. Tiny/Small use 128/256 template/search inputs; Base changes spatial resolution to 192/384 without increasing model depth/width over Small.
- Template neural processing occurs once on the first tracking call. The tracker then reuses bounded ETM kernels and cached template tokens. Steady-state inference executes the search branch, two ETMs, one relation-attention block, a linear neck and a CORNER head.
- OPE is genuinely re-parameterized in the released inference sequence: the training-form checkpoint is loaded first, then three convolution branches are fused in memory into one 3×3 convolution.
- The official repository exposes a single-GPU training path. The model is fully trainable, small, and uses conventional AdamW training; released recipes omit AMP/checkpointing/accumulation but do not structurally depend on multi-GPU memory merely to modify the tracker.
- The steady-state graph contains standard convolution/linear/normalization/attention operations plus ETM `einsum`, input-dependent functional `conv1d`, and Python batch control. No official AsymTrack ONNX/TensorRT exporter or synchronized end-to-end Nano measurement is released.
- Paper and code evidence identify concrete diagnostic targets rather than a proven cause: T/S produce an 8×8 response map, the initial template remains fixed, and the search crop follows the previous box without a motion/recovery path. These observations are retained for later failure testing, not promoted to a causal result.

### Gate rationale

**HG4 PASS:** a 3–4M-parameter fully trainable architecture with an explicit single-GPU path is structurally compatible with meaningful RTX 3060 development. The 500-epoch schedule affects time cost but does not make the research loop memory-infeasible by construction.

**HG5 PASS:** the small fused graph, initialization-only template encoding, bounded caches and absence of large foundation backbones provide a credible Nano path without relying on emergency INT8 compression. Dynamic functional convolution/einsum and Python-side tracker logic still require export/operator profiling, so PASS is only structural plausibility—not a speed claim.

## CX049 — SPMTrack

**Final HG4: PASS**  
**Final HG5: FAIL**

### Reconciled evidence

- The reproducible released operating point is SPMTrack-B: DINOv2 ViT-B/14, 12 blocks, width 768, 115,330,565 total parameters and 29,243,909 trainable parameters. The released checkpoint contains the trainable tracking state and requires exact reconstruction of the frozen DINOv2 foundation weights.
- Parameter-efficient fine-tuning is real rather than a head-only update: TMoE, query/type embeddings and the prediction head remain trainable across the backbone. A single-GPU code path and smaller batch mixins exist; training uses FP16. The default one-GPU configuration is still too large, and no 12-GB trace is released, but reduced-batch checkpoint-based module training is a credible research path.
- Inference is not lightweight merely because only 29.2M parameters are trainable. Each frame processes one query, three 196-token templates and 729 search tokens: 1,318 tokens through all 12 dense DINOv2 blocks.
- TMoE is installed at 72 linear sites. Routing is dense and token-wise; all four experts execute at every TMoE site. The frozen base linear operation and TMoE additions both remain active at inference—there is no top-k sparse dispatch or merged lightweight graph.
- Three raw reference images are transferred and re-encoded every frame. Image/mask histories append without confidence admission and grow with sequence length. No released lightweight B/Tiny inference family, stateful tracking ONNX/TensorRT path, or credible edge-oriented graph is provided.
- The automatic profiler does not represent checkpoint-loaded steady-state tracking: its evaluation graph is assessed before TMoE is installed and its ordinary forward uses two searches rather than the actual stateful one-search tracking call.

### Gate rationale

**HG4 PASS:** the official B checkpoint/foundation reconstruction, genuine PEFT boundary, FP16 path, one-GPU control flow and configurable smaller batch provide a credible way to train new modules or fine-tune the 29.2M trainable portion on RTX 3060, subject to a later measured fit. Original full-throughput reproduction is not required by HG4.

**HG5 FAIL:** the released inference graph remains a 115M-parameter DINOv2-B tracker with a 1,318-token dense sequence, 72 all-expert TMoE layers, repeated three-reference encoding and growing histories. Reaching Nano would require replacing or radically redesigning the core foundation/TMoE path, or depending on compression as a condition of survival. That violates the baseline-selection boundary requiring a credible mechanism-based Nano route before the proposed contribution.

## Batch-C consequence

| Candidate | HG4 | HG5 | Progression after Batch C |
|---|---:|---:|---|
| CX043 SUTrack | **PASS** | **PASS** | survives HG4/HG5; hold for later candidate-specific gap/HG6 stage |
| CX044 AsymTrack | **PASS** | **PASS** | survives HG4/HG5; hold for later candidate-specific gap/HG6 stage |
| CX049 SPMTrack | **PASS** | **FAIL** | excluded from main-baseline progression; retained as literature/novelty reference |

No candidate is scored or shortlisted.

## Next activation

Batch C is closed. The predeclared Batch D may now activate only for candidates whose early gates are PASS:

- **CX053 — UncTrack**
- **CX058 — HiT-DyHiT**
- **CX125 — MPT**

The remaining original candidate is inactive:

- CX051 UMDATrack — HG3 PENDING/suspended.

Manager and Codex must independently extract Stage-2A evidence for the three active Batch-D candidates before HG4/HG5 decisions. HG6 remains locked until the systematic evidence batches and required targeted HG5 profiling are completed sufficiently to define candidate-specific research gaps.

## Locked state

- Batch C reconciliation: **COMPLETE**
- HG6: **NOT STARTED**
- S1–S7 soft scoring: **NOT STARTED**
- primary shortlist: **NONE**
- main baseline: **NONE**
- proposed architecture: **NONE**
