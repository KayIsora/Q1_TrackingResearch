# Stage 2B — Targeted HG5 evidence reconciliation

**Date:** 2026-08-25  
**Status:** STAGE 2B CLOSED; candidate-specific research-gap formulation may begin only for candidates with HG1–HG5 PASS.  
**Inputs:** `screening/manager/2026-08-25_stage2B_targeted_hg5_resolution_plan.md` and `screening/codex/2026-08-25_stage2B_targeted_hg5_evidence.md`.  
**Governing protocol:** `docs/11_systematic_screening_protocol.md`.

## Boundary

This reconciliation decides only **HG5 — Jetson Nano B01 deployment plausibility** for the six candidates that remained `HG4=PASS, HG5=PENDING` after Stage 2A.

A `PASS` is a project gate, not a Jetson Nano benchmark result. It means the released scientific mechanism has a credible bounded path toward Nano-class deployment without replacing the core tracker. A `FAIL` means the released candidate would require major core replacement or life-support compression merely to create a plausible Nano path. `PENDING` is retained when the targeted evidence still cannot distinguish those cases.

No desktop/MX250/CPU latency is converted into Nano FPS. This file does not begin HG6, assign S1–S7, rank candidates, form a shortlist, select a main baseline, or approve a proposed architecture.

---

## CX007 — SpikeTrack

**Final HG5: PASS**

### Reconciled evidence

- The exact official Small T1 and T3 checkpoints loaded and ran on a 2 GiB development GPU. The T1 steady path used roughly 107 MiB PyTorch allocated peak in the bounded run; the six retrieval-cache payloads were small and bounded.
- The spike implementation uses ordinary dense PyTorch clamp/round/divide, convolution and matrix-multiplication kernels. It does not require a neuromorphic/event-driven runtime or custom sparse CUDA extension.
- All six Memory Retrieval Modules execute every frame; T3 adds substantial temporal/template work. This identifies a concrete engineering cost boundary but is not itself a redundancy result.
- The fixed T1 template encoder exported. The defining cached-search path failed under the pinned PyTorch 2.0 exporter at a known adaptive-pooling/Python-timestep site. The failure is localized to graph/export construction rather than evidence that the scientific tracker requires unsupported hardware or unbounded state.

### Gate rationale

The released Small/T1 path is compact, bounded, executable on a low-memory conventional CUDA GPU and built from standard dense operators. Reaching Nano still requires an export wrapper or supported newer exporter plus TensorRT/operator validation, but it does not require replacing the tracker’s scientific core. Therefore the structural deployment path is credible enough for HG5 PASS.

This is not a Nano speed, power, thermal, FP16 or INT8 claim.

---

## CX010 — UTPTrack

**Final HG5: PASS**

### Reconciled evidence

- The exact UTPTrack-O checkpoint strict-loaded and ran with physical token compaction across search, static-template and dynamic-template streams.
- The defining pruning/restoration mechanism survived a complete fixed-shape ONNX export. ONNX Runtime preserved numerical parity across multiple foreground annotations; the exported graph retained TopK/sort-lowered, gather, scatter, nonzero and conditional operations.
- Runtime state is bounded to two raw templates. The ViT-B model remains substantial and both templates are re-embedded every frame, but no foundation-scale mandatory side model or sequence-length-growing state is required.
- Dynamic batch/spatial export and TensorRT support remain unresolved. Those are deployment-engineering questions, not evidence that the core pruning method must be removed.

### Gate rationale

UTPTrack has a reproducible fixed-shape neural graph in which its core pruning mechanism remains intact. A credible Nano path can use a fixed deployed resolution and fixed retention schedule while preserving content-dependent retained identities. TensorRT and reduced-precision validation remain mandatory, but core replacement is not required. HG5 is therefore PASS.

No Nano latency or FPS is claimed.

---

## CX020 — SAMURAI

**Final HG5: FAIL**

### Reconciled evidence

- The smallest released SAMURAI host, SAM 2.1 Hiera Tiny, still processes every frame at 1024×1024 through a full-frame image encoder, memory attention, mask decoder and memory encoder. Kalman/mask-selection logic does not skip that neural path.
- The exact Tiny checkpoint completed a four-frame CPU characterization, but process RSS rose from about 702 MiB after initialization to more than 1.4 GiB after only three propagated frames. The scientific inference state stores an output entry for every processed frame; `num_maskmem=7` limits active memory selection, not total retained output history.
- The release is offline/indexed-video oriented. It requires a fixed video/frame folder, does not provide append-one-live-frame streaming, and does not expose a tensor-only full-predictor export contract.
- The stateful controller uses frame-keyed Python dictionaries, a generator, host thresholds, NumPy/SciPy Kalman state and backward history scans. No complete SAMURAI/SAM2 video-predictor ONNX/TensorRT path is released.

### Gate rationale

Even the smallest official host retains full-frame 1024-scale SAM2 processing plus sequence-length-growing state and an offline stateful API. A Nano-class path would require replacing or materially redesigning the host execution/state architecture, not merely ordinary export adaptation or a bounded optimization of SAMURAI. HG5 is therefore FAIL.

SAMURAI remains important as a motion/memory and identity-confusion reference, but it no longer progresses as the main baseline candidate.

---

## CX037 — SSTrack-AAAI

**Final HG5: PASS**

### Reconciled evidence

- The exact B256 checkpoint strict-loaded and executed. Its defining three candidate-elimination stages physically reduced search tokens `256→180→126→89`.
- A fixed four-template neural wrapper exported successfully to ONNX with explicit query state. ONNX Runtime closely matched PyTorch, and the graph retained TopK, gather and scatter operators rather than deleting candidate elimination.
- The neural state is bounded to a one-token persistent query. The released Python tracker keeps an unbounded raw-template history and re-embeds selected templates, but only a bounded selected subset enters a forward.
- The missing bounded-history/controller integration and TensorRT parity are engineering work. They do not require replacement of the self-supervised training framework or the deployed candidate-elimination tracker.

### Gate rationale

The core B256 neural graph is reproducible, fixed-shape exportable and preserves its efficiency mechanism. A bounded-history deployment controller can be implemented without changing the central CE/query formulation, although it must later be validated for benchmark parity. This provides a credible structural Nano path, so HG5 is PASS.

No Nano runtime or accuracy-after-controller-bounding claim is made.

---

## CX038 — MCITrack

**Final HG5: PASS**

### Reconciled evidence

- The exact B224 checkpoint strict-loaded and completed sequential inference. The four hidden states are fixed-size FP32 tensors totaling about 49 MiB and are replaced each frame rather than growing with video length.
- The active Mamba/context implementation uses ordinary PyTorch linear layers, grouped Conv1d, exponentials, elementwise state updates, attention and matrix multiplication; no mandatory Triton/selective-scan/custom-CUDA extension is required.
- A fixed-shape ONNX graph with five templates and four explicit hidden-state inputs/outputs exported successfully and matched PyTorch in ONNX Runtime. The scientific Mamba/Injector/Extractor path remained present.
- Five raw templates are re-encoded every frame and the Python template bank/controller remains outside the graph. Those are major efficiency/profile targets, but they are bounded and can be addressed without replacing the temporal-context core.

### Gate rationale

MCITrack-B224 has an explicit bounded state contract and an exportable standard-operator neural graph. The current model is not claimed Nano-ready, but the remaining barriers are fixed-shape state/controller integration, template processing and reduced-precision/runtime validation rather than core architectural incompatibility. HG5 is therefore PASS.

No Nano FPS, memory or long-sequence parity claim is made.

---

## CX053 — UncTrack

**Final HG5: PENDING**

### Reconciled evidence

- The Base online model and full controller ran only after a one-character source correction and several compatibility shims. The checkpoint filename also differs from the released shell convention.
- Persistent state is bounded: a three-prototype memory, bounded online templates, eleven K/V caches, a best candidate and Kalman arrays. Reliable and forced-unreliable modes were both exercised; the unreliable mode performs a second complete ConvMAE+ULD+PMN inference.
- A traced ONNX graph matched the example input but failed to generalize the PMN score/prototype path because box-indexed mask construction was frozen through Python integer conversion. Cached-search export captured mutable K/V state as constants rather than exposing a valid state input/output contract.
- The Python reliability branch, conditional second inference, FIFO updates and NumPy Kalman controller remain outside export. No compatible CUDA/TensorRT characterization was obtained for the complete path.

### Gate rationale

The candidate is not structurally rejected: state is bounded and the scientific method may be expressible with tensorized PMN masking plus explicit K/V state. However the targeted run did not establish that those changes are merely routine export adaptation rather than a significant rewrite of the released execution contract. HG5 therefore remains PENDING.

UncTrack does not proceed to HG6 or soft scoring as though it passed. It is held outside the active HG6 pool unless additional evidence resolves the explicit-state and dynamic-mask deployment contract.

---

## Stage-2B consequence

### HG1–HG5 PASS — eligible for candidate-specific gap formulation and later HG6 audit

1. CX007 — SpikeTrack
2. CX009 — UETrack
3. CX010 — UTPTrack
4. CX013 — FARTrack
5. CX024 — DAM4SAM
6. CX037 — SSTrack-AAAI
7. CX038 — MCITrack
8. CX043 — SUTrack
9. CX044 — AsymTrack
10. CX058 — HiT-DyHiT

These ten candidates are **not a shortlist**. HG6 is still PENDING and no S1–S7 score has been assigned.

### HG5 PENDING — held outside HG6

- CX053 — UncTrack

### HG5 FAIL / reference-only

- CX014 — GOT-Edit
- CX017 — GOT-JEPA
- CX020 — SAMURAI
- CX049 — SPMTrack
- CX125 — MPT

### Early-gate exclusions/suspensions

- CX040 — MambaLCT — HG3 FAIL
- CX064 — SiamABC — HG3 FAIL
- CX046 — JDTrack — HG3 PENDING
- CX051 — UMDATrack — HG3 PENDING

## Stage closure

- Stage 2A systematic paper/code audit: **COMPLETE**
- Stage 2B targeted HG5 resolution: **COMPLETE**
- Active candidate-specific gap/HG6 pool: **10, UNRANKED**
- HG6: **NOT STARTED**
- S1–S7 soft scoring: **NOT STARTED**
- Primary shortlist: **NONE**
- Main baseline: **NONE**
- Proposed architecture: **NONE**
