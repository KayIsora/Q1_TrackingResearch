# Stage 2A — Batch B reconciliation and HG4/HG5 gate decisions

**Date:** 2026-08-25  
**Status:** BATCH B RECONCILED; Batch C may activate only for HG1/HG2/HG3-PASS candidates in the predeclared order.  
**Inputs:** Manager scientific audit `screening/manager/2026-08-25_stage2_batchB_scientific_audit.md` and Codex code audit `screening/codex/2026-08-25_stage2_batchB_code_audit.md`.  
**Governing protocol:** `docs/11_systematic_screening_protocol.md`.

## Boundary

This reconciliation decides only **HG4 — RTX 3060 12 GB research feasibility** and **HG5 — Jetson Nano B01 deployment plausibility** where the combined paper/code evidence is sufficient. It does not start HG6, assign S1–S7, rank candidates, shortlist a baseline, or approve a proposed architecture.

A `PASS` here is a project research gate, not an experimental result. HG5 PASS means a credible structural path exists; it is **not** a Jetson Nano FPS or memory claim. `PENDING` is retained whenever device/export/profile evidence can still reverse the decision.

## CX017 — GOT-JEPA

**Final HG4: PENDING**  
**Final HG5: FAIL**

### Reconciled evidence

- The released 378 pipeline executes a DINOv2 ViT-L/14 semantic pass and ToMP/JEPA filter prediction every frame. A CoTracker2/OccuSolver path runs periodically on an eight-frame window with 128 point queries and several point-fusion modules.
- State is bounded: sample memory size 2 and the OccuSolver buffers are fixed-size. This is favorable for memory growth, but it does not remove the large always-on backbone cost.
- Training is three-stage. The final PT stage keeps DINOv2-L, ToMP/JEPA and point-tracking/fusion components resident, unrolls 16 train + 8 test frames, and is released with multi-GPU batch settings. No verified one-RTX3060 memory profile, accumulation recipe, or clean end-to-end checkpoint bootstrap is supplied.
- The official pinned release does not contain the lower-resolution 252 GOT-JEPA variant used in some paper-level speed discussion, so that variant cannot be used to rescue the released baseline path at this gate.

### Gate rationale

**HG4 PENDING:** checkpoint-based, partially frozen research may still be possible, but the released evidence is insufficient to establish meaningful single-3060 modification/training without local profiling.

**HG5 FAIL:** the reproducible deployed path retains an always-on ViT-L-class semantic backbone plus dynamic-filter tracking and periodic point-tracking/visibility computation. No released lightweight variant or edge-oriented mechanism removes this dominant path. A credible Nano route would require major core replacement rather than a bounded algorithmic reduction of the released tracker. GOT-JEPA remains literature/novelty reference material.

## CX020 — SAMURAI

**Final HG4: PASS**  
**Final HG5: PENDING**

### Reconciled evidence

- SAMURAI itself is training-free and uses official SAM 2.1 checkpoints. The method-specific additions are motion/Kalman scoring and memory-quality selection rather than a new trained network.
- The release provides Hiera Tiny/Small/Base+/Large configurations. `main_inference.py` defaults to Base+ while the chunked script defaults to Large; result-to-variant identity is not uniform across scripts.
- The image encoder runs once for each newly requested frame, followed by memory attention and the mask decoder. Active attention memory is bounded by `num_maskmem=7` and object-pointer caps, but compact per-frame output dictionaries can grow with sequence length; benchmark scripts commonly offload that history to CPU.
- The released API is offline/indexed-video oriented rather than append-one-live-frame streaming.

### Gate rationale

**HG4 PASS:** official pretrained weights give a direct starting point and the baseline requires no family-specific training. Lightweight new trainable components can plausibly be developed around a frozen host without reproducing a large original training farm. This does not claim that full SAM2 joint fine-tuning fits 12 GB.

**HG5 PENDING:** multiple Hiera sizes exist and the SAMURAI additions themselves are lightweight, so the architecture is not rejected solely from the heavy Base+/Large defaults. However 1024-scale SAM2 image/memory processing, growing retained history, Python/host Kalman logic, and the absence of an export/Nano path require targeted runtime/export profiling before a Nano plausibility PASS can be defended.

## CX024 — DAM4SAM

**Final HG4: PASS**  
**Final HG5: PASS**

### Reconciled evidence

- DAM4SAM is training-free on SAM 2.1. The pinned implementation defaults to Hiera-L and separates host SAM2.1 computation from incremental distractor-memory/introspection logic.
- The default host image encoder runs once per frame; memory selection/attention and the mask decoder then run every frame. DAM-specific incremental work is mainly alternative-mask inspection, connected-components/IoU bookkeeping, memory admission and occasional distractor-memory promotion.
- Active memory attention is bounded, although output dictionaries and object-size history can grow with sequence length.
- The peer-reviewed IJCV extension reports the same DAM memory mechanism integrated with lighter EfficientTAM and EdgeTAM hosts, including robustness gains. That provides direct mechanism-level evidence that the method is not structurally tied to Hiera-L.

### Gate rationale

**HG4 PASS:** no baseline training farm is required and official foundation weights provide a direct development start; new lightweight modules can plausibly be trained with the host frozen.

**HG5 PASS:** this is a structural plausibility decision only. The main Hiera-L release is not claimed to be Nano-ready, but the published method-level transfer to EfficientTAM/EdgeTAM provides a concrete lighter-host route rather than a speculative “compress later” story. Actual Nano runtime, memory, operator parity and the availability of a reproducible lightweight-host implementation remain mandatory later checks.

## CX037 — SSTrack-AAAI

**Final HG4: PASS**  
**Final HG5: PENDING**

### Reconciled evidence

- SSTrack's main novelty is self-supervised training; its deployed tracker remains a ViT-Base-style tracking architecture with candidate elimination. The self-supervised consistency/contrastive supervision is not an additional inference network.
- Released B256/B384 configurations use DropMAE initialization, explicit optimizer/batch/epoch settings and official checkpoints. A single-process training path exists, although no measured 12-GB peak is supplied.
- Inference physically reduces search-token sequence length at three CE stages, then restores the search grid for the center head. Selected raw templates are re-embedded every frame and multi-template raw history can grow with sequence length.
- The released profiler is stale/mismatched; dynamic sort/gather/scatter and tracker Python state have no validated ONNX/TensorRT/Nano path.

### Gate rationale

**HG4 PASS:** checkpoint-based ViT-Base development with smaller per-device batch/accumulation is structurally plausible, and there is no evidence that the research loop requires inaccessible multi-GPU resources merely to modify/train the tracker.

**HG5 PENDING:** physical token reduction provides a credible efficiency mechanism, so the candidate is not structurally rejected. However dynamic elimination operators, growing raw template history, repeated template encoding and the absence of a valid exporter/profile require targeted deployment profiling before PASS.

## CX038 — MCITrack

**Final HG4: PASS**  
**Final HG5: PENDING**

### Reconciled evidence

- MCITrack-B224 uses a Fast-iTPN Base path with five 112² templates plus a 224² search, four contextual Mamba blocks, four MHA Injectors and six MHA Extractors; all execute every frame. The active Mamba implementation is ordinary PyTorch rather than `mamba_ssm`/Triton/custom CUDA.
- Four persistent hidden states are fixed-size and reset on low confidence; at batch 1 the B224 state payload is about 49 MiB in FP32. The state does not grow with sequence length.
- A bounded raw template bank can retain hundreds of GPU crops, while five active raw templates are re-encoded every frame. No encoded-template cache exists.
- Training uses official checkpoints, activation checkpointing and explicit optimizer/configuration; a one-process launcher path exists, although no measured 3060 peak or accumulation recipe is supplied.
- The released profiler undercounts/omits important Mamba-state work and lacks synchronized end-to-end timing; no ONNX/TensorRT state-I/O path is released.

### Gate rationale

**HG4 PASS:** the B224 checkpoint path, activation checkpointing, fixed-size state and explicit training recipe make meaningful checkpoint-based single-3060 research plausible with reduced batch/accumulation, without needing to reproduce the original multi-GPU throughput.

**HG5 PENDING:** the operator family is mostly ordinary PyTorch and the temporal state is bounded, so there is no structural FAIL. But always-on contextual fusion, five-template re-encoding, a large raw GPU template bank and explicit hidden-state export requirements need profiling/export validation before Nano plausibility can be promoted to PASS.

## Batch-B consequence

| Candidate | HG4 | HG5 | Progression after Batch B |
|---|---:|---:|---|
| CX017 GOT-JEPA | PENDING | **FAIL** | excluded from main-baseline progression; reference only |
| CX020 SAMURAI | **PASS** | PENDING | targeted HG5 profiling required before HG6 |
| CX024 DAM4SAM | **PASS** | **PASS** | survives HG4/HG5; hold for later candidate-specific gap/HG6 stage |
| CX037 SSTrack-AAAI | **PASS** | PENDING | targeted HG5 profiling required before HG6 |
| CX038 MCITrack | **PASS** | PENDING | targeted HG5 profiling required before HG6 |

No candidate is shortlisted or scored.

## Next activation

Batch B is closed. The predeclared Batch C may now activate only for candidates whose early gates are PASS:

- **CX043 — SUTrack**
- **CX044 — AsymTrack**
- **CX049 — SPMTrack**

The other original Batch-C slots remain inactive:

- CX040 MambaLCT — HG3 FAIL/reference only;
- CX046 JDTrack — HG3 PENDING/suspended.

Manager and Codex must independently extract Stage-2A evidence for the three active Batch-C candidates before HG4/HG5 decisions. Batch D remains locked.

## Locked state

- Batch B reconciliation: **COMPLETE**
- HG6: **NOT STARTED**
- S1–S7 soft scoring: **NOT STARTED**
- primary shortlist: **NONE**
- main baseline: **NONE**
- proposed architecture: **NONE**
