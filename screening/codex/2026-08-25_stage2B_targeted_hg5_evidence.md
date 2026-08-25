# Stage 2B — targeted HG5 evidence / profiling

**Date:** 2026-08-25

**Lane:** Codex worker — code and engineering evidence

**Scope:** CX007 SpikeTrack, CX010 UTPTrack, CX020 SAMURAI, CX037 SSTrack-AAAI, CX038 MCITrack, and CX053 UncTrack only
**Decision boundary:** this report records evidence; it does not decide HG5.

## 1. Guardrail and evidence vocabulary

This is a bounded characterization exercise, not an official accuracy reproduction, a Jetson Nano benchmark, an HG6 novelty audit, scoring, ranking, shortlist selection, baseline selection, or proposed-method design. All six final statuses in this independent report remain `HG5 = PENDING` for Manager reconciliation.

Only these claim-evidence labels are used:

- **CODE FACT — inspected:** direct source inspection or a measured result from the exact pinned checkout and identified artifact;
- **RESOURCE AVAILABILITY FACT:** an official config, checkpoint, script, or documented capability that was directly located;
- **ENGINEERING TARGET TO PROFILE:** a measurement or implementation boundary that remains to be resolved;
- **OPEN QUESTION:** evidence not established by the bounded run.

Two non-claim qualifiers are also used: **PATCHED FOR CHARACTERIZATION — NOT OFFICIAL RELEASE** or **CHARACTERIZATION HARNESS — NOT OFFICIAL RELEASE** identifies a documented execution deviation/harness, while **LIMIT** narrows the boundary of an otherwise labeled fact. Neither qualifier is an evidence claim or an HG5 decision.

CPU timing, process RSS, desktop operator behavior, and ONNX Runtime results below must not be converted into Jetson Nano FPS, latency, VRAM, power, or thermal claims.

## 2. Common audit environment and measurement boundary

### 2.1 Host

| Field | Inspected value |
|---|---|
| OS | Windows 11 Home Single Language, `10.0.26200`, build 26200 |
| CPU | Intel Core i7-1065G7 @ 1.30 GHz |
| system RAM | 15.79 GiB |
| physical GPU | NVIDIA GeForce MX250, 2,048 MiB, compute capability 6.1 |
| NVIDIA driver | 581.83; `nvidia-smi` reports driver CUDA 13.0 |
| primary characterization runtime | Python 3.13.3; PyTorch `2.12.0+cpu`; torchvision `0.27.0+cpu`; timm `0.9.2`; ONNX `1.21.0`; ONNX Runtime `1.29.0` |

**CODE FACT — inspected:** the pre-existing CUDA-enabled environment used PyTorch `2.11.0+cu128`, whose compiled architecture list is `sm_75 sm_80 sm_86 sm_90 sm_100 sm_120`. It detects the MX250 (`sm_61`) but a one-element CUDA tensor plus synchronization fails with `AcceleratorError: CUDA error: no kernel image is available for execution on the device`.

**CODE FACT — inspected:** the independent SpikeTrack and UTPTrack lanes subsequently created candidate-specific CUDA environments whose wheels support the MX250: Python 3.11/PyTorch `2.0.0+cu118` for CX007 and Python 3.12/PyTorch `2.5.1+cu121` for CX010. Only CX007 and CX010 have CUDA-synchronized latency and PyTorch allocator peaks below. CUDA results remain unavailable for the other four candidates, and no missing GPU result is silently replaced with CPU RSS.

### 2.2 Bounded protocol

- **CODE FACT — inspected:** neural smoke tests used batch size one and exact released configs/checkpoints. Synthetic tensors were used only to exercise declared model contracts; SAMURAI additionally used four consecutive official-demo-video frames, and UncTrack additionally used synthetic RGB frames through the complete tracker controller.
- **CODE FACT — inspected:** CPU model timings use `time.perf_counter`; the SSTrack, MCITrack, and UncTrack distributions contain three bounded observations per reported mode, with total process RSS sampled approximately every 5 ms. SAMURAI instead has three sequential propagation observations and event-boundary RSS snapshots. None of these RSS values is incremental tensor memory or GPU VRAM.
- **CODE FACT — inspected:** initialization/build/checkpoint load was kept outside steady-state timing where the implementation allowed it.
- **CODE FACT — inspected:** ONNX dry-runs used opset 17. The four common-CPU lanes used the legacy TorchScript-based exporter and removed their temporary ONNX files after the stated checks; SpikeTrack and UTPTrack used their separately identified candidate-specific stacks and kept artifacts only in isolated checkouts outside the research repository. No selected candidate shipped a complete official exporter for its deployed graph.
- **OPEN QUESTION:** CPU scheduling, page cache, allocator reuse, newer dependency versions, and characterization shims prevent these small samples from being official performance measurements.

### 2.3 Characterization-only changes

The main research repository was not modified for model execution. The following bounded deviations are explicitly separated from official release behavior.

- **PATCHED FOR CHARACTERIZATION — NOT OFFICIAL RELEASE (SSTrack):** the center-head coordinate tensors are created with hard `.cuda()` calls. A runtime-only `Tensor.cuda → identity` shim enabled CPU construction; no SSTrack source file was edited.
- **PATCHED FOR CHARACTERIZATION — NOT OFFICIAL RELEASE (MCITrack):** the center-head coordinate tensors use hard `.cuda()`. A runtime-only no-op shim was used. The builder's external Fast-iTPN-pretrain bootstrap was skipped only during construction, after which the complete released tracker checkpoint loaded with `strict=True`.
- **PATCHED FOR CHARACTERIZATION — NOT OFFICIAL RELEASE (UncTrack):** the isolated pinned checkout deleted the standalone full-width `）` (U+FF09) at `lib/test/tracker/unctrack_online.py:159`. Runtime compatibility shims were also required for hard `.cuda()`, the removed `np.float` alias, the repository's incorrect `float(torchvision.__version__[:3])` version test, removed `torch._six`, and modern `torch.load(weights_only=...)` behavior. These shims do not establish official compatibility with modern PyTorch.
- **PATCHED FOR CHARACTERIZATION — NOT OFFICIAL RELEASE (SAMURAI):** SAM2 was installed with `SAM2_BUILD_CUDA=0` in an isolated environment, so the optional connected-components CUDA extension was not built; the builder was also called with `apply_postprocessing=False`, explicitly disabling that runtime postprocessing path instead of exercising the builder default.
- **CHARACTERIZATION HARNESS — NOT OFFICIAL RELEASE (UTPTrack):** untracked harnesses monkeypatched functions only to observe shapes and timing. A tensor-I/O export wrapper converted official list inputs to five tensors and selected five output tensors; it did not remove the pruning, restoration, backbone, or prediction-head graph. No tracked source file was edited.

## 3. CX037 — SSTrack-AAAI

### A. Provenance

- **CODE FACT — inspected:** repository `GXNU-ZhongLab/SSTrack`, detached at `5dcf04ccb04f10ca4d78035373c8b8684bb8c4f5` with no tracked-file modifications; characterization artifacts remained isolated/untracked.
- **CODE FACT — inspected:** selected config `experiments/sstrack/dropmae_256_150ep.yaml` (B256: 128 template, 256 search, ViT-B width 768/depth 12, CE blocks 3/6/9, keep ratio 0.7).
- **RESOURCE AVAILABILITY FACT:** the official Drive folder exposes `Models/Full_Data/SSTrack_256_ep0150.pth.tar`, file ID `1_lUg8saCyHQk83ni5CANoDzAe3yt95_y`.
- **CODE FACT — inspected:** downloaded checkpoint size `370,179,863` bytes; SHA-256 `4C39C1F695F3F02521E90A3B169796399AF78F5E43CF649A614ADDACA0C4006D`; 245 state tensors with `370,094,964` payload bytes.

### B. Environment

- **CODE FACT — inspected:** characterization used the common CPU runtime in §2 plus the SSTrack `.cuda()` no-op described in §2.3. The official install script instead names PyTorch 1.9.0/torchvision 0.10.0.
- **CODE FACT — inspected:** checkpoint construction did not require the external DropMAE initialization because `training=False`; the complete released tracker checkpoint then loaded with `strict=True` and zero missing/unexpected keys.

### C. Bounded smoke result

**Status: SUCCESS**

| Check | Result |
|---|---|
| build | success, 7.987 s |
| strict checkpoint load | success, all keys matched |
| parameter count | `92,520,837`; FP32 payload `370,083,348` bytes |
| one-template forward | success; `pred_boxes [1,1,4]`, persistent query `[1,1,768]` |
| four-template forward | success with the same output/state contract |

**LIMIT:** this is checkpoint-level functional execution under a CPU characterization shim, not the unmodified official CUDA tracker entrypoint.

### D. Runtime modes

| Mode | Model input and work | Persistent state | Inspected behavior |
|---|---|---|---|
| early/one-template | one raw 128² template + one 256² search | query `[1,1,768]` | all raw inputs patch-embedded; 12 ViT blocks; CE at 3/6/9; center head |
| mature/four-template | four raw 128² templates + one 256² search | same one-token query | every selected template is re-embedded every frame; search CE lengths are unchanged |
| host history | tracker appends a raw predicted template each frame | unbounded raw history; first 1,000 entries remain on CUDA in official path | active selector keeps the initial template plus sampled history entries; this Python controller was outside the model-only timing |

### E. Latency evidence

CPU FP32, model-only, three sequential observations; the first observation is retained rather than discarded.

| Mode | Observations (ms) | Median (ms) |
|---|---:|---:|
| one template | 911.679, 822.805, 801.175 | 822.805 |
| four templates | 1423.985, 1376.530, 1669.865 | 1423.985 |

**CODE FACT — inspected:** the four-template mode executes the same CE search lengths but more template patch embedding and attention tokens. The timing difference is a CPU-local characterization, not a device speed claim.

### F. Peak-memory evidence

| Mode | Sampled total process peak RSS | End RSS |
|---|---:|---:|
| one template | `1,100,038,144` bytes | `1,081,163,776` bytes |
| four templates | `1,116,278,784` bytes | `1,071,435,776` bytes |

**LIMIT:** total RSS includes Python, loaded weights, allocator pools, dependencies, and transient activations. It is neither incremental model memory nor peak VRAM.

### G. Token, state, and history evidence

- **CODE FACT — inspected:** runtime hooks at the three CE blocks observed exact search transitions `256→180`, `180→126`, and `126→89`; removed counts were 76, 54, and 37. CE runs after each block's full attention and only reduces later-block search tokens.
- **CODE FACT — inspected:** the returned persistent query is one FP32 token `[1,1,768]` (3,072 bytes); it is overwritten each frame and does not grow with sequence length.
- **CODE FACT — inspected:** one raw FP32 template crop `[1,3,128,128]` is 196,608 bytes. Official tracker history is not truncated, while only a bounded selected subset enters each neural forward.
- **ENGINEERING TARGET TO PROFILE:** long-sequence GPU/CPU history slope, selector transfer cost after the 1,000-entry threshold, and an explicit bounded-history deployment policy remain outside this run.

### H. Export result

**Result: SUCCESS for the fixed-shape neural wrapper; full Python controller NOT ATTEMPTED.**

- **CODE FACT — inspected:** a fixed four-template + explicit query-in/query-out wrapper exported successfully to full-parameter ONNX opset 17. Artifact size was `371,031,088` bytes; SHA-256 `C58475DF58797CA4D0788A0D03E99A3F4B7C831D8A810B395083C633C9F80069`.
- **CODE FACT — inspected:** ONNX Runtime CPU returned `pred_boxes [1,1,4]` and `query_out [1,1,768]`; maximum absolute differences versus PyTorch were `2.6822e-7` and `2.8610e-6`.
- **CODE FACT — inspected:** the operator inventory of the same fixed-four-template graph contained three `TopK` nodes plus `GatherElements` and `ScatterElements`; thus CE operators were present rather than removed for the export dry-run.
- **LIMIT:** the successful wrapper fixes B256 and four templates. It does not export the Python raw-history selector, variable active-template count, crop/preprocessing, confidence/box controller, or CPU↔GPU history moves. It is not an official exporter or TensorRT parity result.

### I. Structural HG5 evidence

- **CODE FACT — inspected:** the exact released B256 checkpoint executes under the documented CPU characterization shim, and its defining three-stage CE path survives a fixed-shape ONNX graph.
- **CODE FACT — inspected:** an explicit fixed-size query state is expressible as ONNX input/output without deleting CE.
- **CODE FACT — inspected:** the complete runtime still re-encodes multiple raw templates and retains sequence-length-growing host/device history outside that graph.
- **OPEN QUESTION:** CUDA/TensorRT operator support, peak VRAM, latency, controller integration, and Jetson Nano behavior remain unmeasured.

**HG5 = PENDING**

### J. Unresolved blocker

1. **OPEN QUESTION:** fixed-maximum-template export with numerical parity across history maturity and template counts.
2. **OPEN QUESTION:** bounded history/controller implementation without changing the scientific CE/query mechanism.
3. **OPEN QUESTION:** synchronized CUDA FP16/FP32 latency and peak memory on a compatible development GPU.
4. **OPEN QUESTION:** TensorRT handling/parity for `TopK`, gather, scatter restoration, and explicit query state.
5. **OPEN QUESTION:** stable per-module latency attribution for raw-template embedding, CE scoring/sort/gather/scatter, and the center head; this run measured complete one-/four-template modes and token transitions only.

## 4. CX038 — MCITrack

### A. Provenance

- **CODE FACT — inspected:** repository `kangben258/MCITrack`, detached at `e667193eaec4c8a73d4bdd856a662aecdb844b43` with no tracked-file modifications; characterization artifacts remained isolated/untracked.
- **CODE FACT — inspected:** selected released config `experiments/mcitrack/mcitrack_b224.yaml`: five 112² templates, one 224² search, Fast-iTPN-B width 512, four Mamba layers (`d_inner=1024`, `d_state=16`), and center head.
- **RESOURCE AVAILABILITY FACT:** official Drive folder exposes `mcitrack_b224/MCITRACK_ep0300.pth.tar`, file ID `1F179L7zP2v8dj8at6c-agXo1fQjQEFt8`.
- **CODE FACT — inspected:** checkpoint size `428,943,566` bytes; SHA-256 `6F28F9425FE6E7B52ECA4D1D9ADC7A59AA51558A21BE300F4F456AEBBD4EB2D9`; 830 state tensors with `428,624,244` payload bytes.

### B. Environment

- **CODE FACT — inspected:** characterization used the common CPU runtime, hard-`.cuda()` no-op, and pretrain-bootstrap bypass described in §2.3. The official install script specifies PyTorch 2.1.2/torchvision 0.16.2 with CUDA 12.1.
- **CODE FACT — inspected:** the complete released checkpoint loaded `strict=True` with no missing/unexpected keys after construction.

### C. Bounded smoke result

**Status: SUCCESS**

| Check | Result |
|---|---|
| build | success, 2.520 s |
| strict checkpoint load | success, all keys matched |
| parameter count | `107,153,157`; FP32 payload `428,612,628` bytes |
| sequential forward | three frames succeeded through encoder → four interaction/Mamba stages → center decoder |
| output | encoder `[1,441,512]`; search feature `[1,196,512]`; box `[1,1,4]`; four returned hidden tensors |

### D. Runtime modes and checkpoint-wrapper behavior

| Mode | Per-frame execution | Observed wrapper calls | Output comparison |
|---|---|---:|---|
| released `GRAD_CKPT=True` | five-template Fast-iTPN, four Mamba blocks, four Injectors, six Extractors, four backbone slices, decoder | 50 `torch.utils.checkpoint.checkpoint` calls | reference |
| characterization `GRAD_CKPT=False` | identical modules and weights, wrappers bypassed only | 0 | frame-0 `pred_boxes` max absolute difference `0.0` |

**CODE FACT — inspected:** checkpoint wrappers execute under `torch.inference_mode()` because the release does not guard them with `self.training`. The bounded CPU sample does not show a stable latency or RSS advantage either way; it only confirms the execution boundary and identical tested output.

### E. Latency evidence

CPU FP32, complete model-only frame, five templates and carried hidden state.

| Mode | Observations (ms) | Median (ms) |
|---|---:|---:|
| released checkpoint wrappers enabled | 3706.953, 2179.706, 1891.972 | 2179.706 |
| wrappers disabled for characterization | 1759.550, 2184.557, 2433.169 | 2184.557 |

**LIMIT:** three noisy CPU observations cannot establish a checkpoint-wrapper speed effect or any deployment latency.

### F. Peak-memory evidence

| Mode | Sampled total process peak RSS | End RSS |
|---|---:|---:|
| wrappers enabled | `1,214,173,184` bytes | `1,165,303,808` bytes |
| wrappers disabled | `1,208,918,016` bytes | `1,165,414,400` bytes |

**LIMIT:** these nearly overlapping total-RSS samples do not establish activation-memory equivalence and are not GPU peaks.

### G. Hidden-state and template evidence

- **CODE FACT — inspected:** all four actual state inputs/outputs are FP32 `[1,196,1024,16]`; each contains `3,211,264` elements and `12,845,056` bytes. Total state payload is `51,380,224` bytes (49.0 MiB).
- **CODE FACT — inspected:** state size is fixed and each state is replaced every frame. Tracker confidence can reset all four entries to `None`; no sequence-length state growth occurs.
- **CODE FACT — inspected:** every frame re-encodes five raw templates. A separate confidence-controlled raw template bank is bounded by dataset-specific capacities 200–500 and remains outside the neural export contract.
- **CODE FACT — inspected:** the active Mamba code uses ordinary PyTorch Linear, grouped Conv1d, exponential, elementwise products, and matmul; no mandatory custom selective-scan CUDA extension was invoked.

### H. Export result

**Result: SUCCESS for the fixed-shape explicit-state wrapper; full Python controller NOT ATTEMPTED.**

- **CODE FACT — inspected:** a fixed B224 wrapper exposed five templates, five template boxes, one search, and four FP32 hidden-state inputs, and returned `pred_boxes` plus four hidden states. Full-parameter ONNX opset 17 export succeeded; artifact size `429,470,321` bytes; SHA-256 `B757617348B9843E544968445CD243D6BBD15E79F896E3A7D938E2FDB40DF5C8`.
- **CODE FACT — inspected:** ONNX Runtime CPU executed the graph. Maximum absolute errors versus PyTorch were `1.1921e-7` for boxes and `6.72e-7`, `1.89e-7`, `1.67e-6`, and `6.12e-7` for h0–h3.
- **CODE FACT — inspected:** the exporter warned that `int(N**0.5)` in `neck.py` becomes a constant; the dry-run therefore supports the selected fixed 14×14 B224 search grid, not dynamic spatial shapes.
- **LIMIT:** Python template-bank management, confidence `.item()` reset, crop/decoder selection, variable spatial shapes, long-sequence state parity, TensorRT, and reduced precision were not validated.

### I. Structural HG5 evidence

- **CODE FACT — inspected:** exact B224 checkpoint execution under the documented construction/CPU shims and a fixed four-state ONNX contract are demonstrated without removing the Mamba/Injector/Extractor path.
- **CODE FACT — inspected:** the four state payloads alone total 49.0 MiB FP32, while every frame also executes five-template encoding and all interaction blocks.
- **OPEN QUESTION:** reduced-precision state behavior, compatible-engine memory, full controller export, and target-device latency remain unmeasured.

**HG5 = PENDING**

### J. Unresolved blocker

1. **OPEN QUESTION:** CUDA FP16/BF16 state dtype, numerical stability, and long-sequence parity.
2. **OPEN QUESTION:** TensorRT/ONNX Runtime target support and peak memory for four large state tensors plus five-template encoding.
3. **OPEN QUESTION:** whether inference checkpoint wrappers should be bypassed in an official deployment path and whether that affects other outputs over sequences.
4. **OPEN QUESTION:** bounded template-bank/controller integration and host synchronization cost.
5. **OPEN QUESTION:** stable separate timings for five-template encoding, Mamba groups, Injectors, Extractors, and decoder; this run measured complete-frame modes and wrapper-call behavior only.

## 5. CX053 — UncTrack

### A. Provenance

- **CODE FACT — inspected:** repository `ManOfStory/UncTrack`, detached at `61bd4be673ac32dd8948f995ce4548855d0ab1d0` before the explicitly documented one-character characterization patch.
- **CODE FACT — inspected:** selected `experiments/unctrack_online/baseline.yaml`: ConvMAE-Base, 128 template, 288 search, ULD, and PMN with three prototypes/top-k three.
- **RESOURCE AVAILABILITY FACT:** official Drive checkpoint is `checkpoints/UncTrack-B/unctrack_online_base.pth.tar`, file ID `1Dz_F3MJ5kz2EKvBCO38cnDfdFA-hZ9tl`; the release shell instead requests `unctrack_base_online.pth.tar`.
- **CODE FACT — inspected:** checkpoint size `648,196,813` bytes; SHA-256 `650E6ADC6DD3A33E9C4EC48E926E3E8AC2F2327255853D5557B431739DAE52EA`; 486 network tensors with `545,889,068` payload bytes.

### B. Environment and source/resource reconciliation

- **CODE FACT — inspected:** unmodified `python -m py_compile lib/test/tracker/unctrack_online.py` fails at line 159 with `SyntaxError: invalid character '）' (U+FF09)`.
- **PATCHED FOR CHARACTERIZATION — NOT OFFICIAL RELEASE:** deleting only that standalone character makes the tracker source parse. The official filename was mapped explicitly to the downloaded artifact rather than silently renamed.
- **CODE FACT — inspected:** additional modern-runtime compatibility shims are enumerated in §2.3. The exact network checkpoint then loaded with `strict=True` and all keys matched.

### C. Bounded smoke result

**Status: SUCCESS under the documented characterization patch/shims**

| Check | Result |
|---|---|
| model build | success, 2.961 s |
| strict checkpoint load | success, all keys matched |
| parameter count | `136,456,239`; FP32 payload `545,824,956` bytes |
| cached Base-online model forward | success; search `[1,768,18,18]`, template `[1,768,8,8]`, ULD sigma `[1,2,72,72]`, score `[1]` |
| patched full tracker build/load | success, 2.163 s |
| patched tracker initialization | success on a 480×640 RGB array, 1.659 s |
| forced reliable track | success, one `forward_test` call, 1.018 s end-to-end CPU |
| forced unreliable track | success, two `forward_test` calls, 2.272 s end-to-end CPU |

**LIMIT:** threshold values `-1` and `2` were used only to deterministically exercise one- and two-attempt controller branches. The resulting random-frame boxes/scores are not accuracy evidence.

### D. Runtime modes

| Mode | Neural calls | Template behavior | Controller work |
|---|---:|---|---|
| LaSOT Base ordinary frame | one cached `forward_test` | `ONLINE_SIZE=2`; K/V cache established; official update interval 160 | score `.item()`, bbox `.tolist()`, one Kalman update, memory/template eligibility |
| forced unreliable frame | two cached `forward_test` calls | same cache; second crop uses `1.5 × search_factor` | second crop/preprocess, second ULD+PMN, second Kalman update and bbox selection |
| template refresh | no search inference | static + online templates re-encoded and all 11 K/V caches replaced | interval-based selected-template update |
| `online_size==1` datasets | full template + online template + search model call each frame | no steady cached-search-only path | same reliability controller |

### E. Latency evidence

CPU FP32, model-only synthetic tensors unless marked controller.

| Mode | Observations (ms) | Median (ms) |
|---|---:|---:|
| cached reliable one attempt | 1280.507, 1202.276, 1258.454 | 1258.454 |
| cached backbone + ULD, score/PMN disabled | 1164.424, 1184.863, 1287.931 | 1184.863 |
| forced two attempts | 2718.454, 3265.893, 2634.100 | 2718.454 |
| template refresh `set_online` | 431.693, 445.186, 492.386 | 445.186 |

One decomposed cached attempt measured backbone 1074.380 ms, ULD 158.661 ms, confidence embedding 14.023 ms, and PMN 25.630 ms. This single decomposition is a boundary check, not a stable module benchmark.

### F. Peak-memory evidence

| Mode | Sampled total process peak RSS | End RSS |
|---|---:|---:|
| one attempt | `1,565,896,704` bytes | `1,558,048,768` bytes |
| backbone + ULD without PMN | `1,559,859,200` bytes | `1,558,986,752` bytes |
| two attempts | `1,561,374,720` bytes | `1,560,743,936` bytes |
| template refresh | `1,560,903,680` bytes | `1,547,911,168` bytes |

**LIMIT:** allocator reuse makes the one- versus two-attempt total-RSS peaks non-additive. No peak GPU allocation was measured.

### G. K/V, prototype, and controller state

- **CODE FACT — inspected:** `set_online` creates 11 per-block FP32 K/V tensors. Each is `[3,1,12,128,64]` and `1,179,648` bytes; combined cache payload is `12,976,128` bytes.
- **CODE FACT — inspected:** the cached initial template feature is `[1,768,8,8]`. Prototype memory is fixed `[1,3,768]` FP32, 9,216 bytes.
- **CODE FACT — inspected:** raw online-template count, prototype bank, K/V caches, best candidate, and Kalman arrays are bounded for the selected configuration; no sequence-length-growing history was observed in the tracker.
- **CODE FACT — inspected:** ULD and PMN execute on every attempt. The unreliable branch therefore performs both twice rather than selecting a cheaper neural route.

### H. Export result

**Result: SUCCESS for traced-example graph creation; FAIL for a generalizable PMN/cached-state contract.**

- **CODE FACT — inspected:** an explicit-template full-attempt wrapper (template, online template, search, prototype memory) exported to ONNX opset 17; artifact size `438,654,582` bytes; SHA-256 `1159F68C33A76BE1EDB6D4F08E2624E235C789EC1787805A628A79C1A177CE25`. Initializer coverage was not established, so this is not labeled a full-parameter export.
- **CODE FACT — inspected:** ONNX Runtime matched the traced example closely: coordinate, score, and prototype maximum errors were `1.7881e-7`, `1.4007e-6`, and `2.0862e-6`.
- **CODE FACT — inspected:** the exporter warned at `uncertainty_aware_score_decoder.py:184` that `int(box[...])` becomes a Python constant. On a second search tensor, coordinates still matched (`1.7881e-7`) but score/prototype errors increased to `0.0280878` and `0.1128315`. The syntactically successful graph therefore does not generalize the box-indexed PMN mask.
- **CODE FACT — inspected:** cached-search export succeeded only after K/V creation under `no_grad`; the graph exposed `search` and `prototype_memory` but no K/V-state input, and its parameter-free graph was about 13.45 MB because the mutable K/V cache was captured as constants.
- **LIMIT:** the Python reliability branch, conditional second inference, bbox `.item()`/`.tolist()`, NumPy Kalman controller, and template/prototype FIFO were not exported.

### I. Structural HG5 evidence

- **CODE FACT — inspected:** the exact Base-online model and patched tracker controller execute both cost modes with bounded persistent state.
- **CODE FACT — inspected:** a naive ONNX export can report success while freezing both PMN box slicing and cached template K/V; export success alone is therefore insufficient deployment evidence.
- **OPEN QUESTION:** an explicit, numerically validated state contract for 11 K/V caches plus dynamic PMN masking and the host reliability controller is not supplied by the release.

**HG5 = PENDING**

### J. Unresolved blocker

1. **OPEN QUESTION:** official correction of the U+FF09 syntax defect and checkpoint filename mapping.
2. **OPEN QUESTION:** export-safe tensorized PMN mask construction without freezing predicted box coordinates.
3. **OPEN QUESTION:** explicit cached K/V input/output contract and parity across template refreshes.
4. **OPEN QUESTION:** CUDA/TensorRT latency and peak memory for one attempt, two attempts, and refresh frames.
5. **OPEN QUESTION:** complete controller integration with conditional second inference and Kalman state on the deployment runtime.

## 6. CX020 — SAMURAI

### A. Provenance

- **CODE FACT — inspected:** official repository `yangchris11/samurai`, detached at `76ba195984892b0d1e3db5d9c9f90bb62175680a` with no tracked-file modifications; characterization artifacts remained isolated/untracked.
- **CODE FACT — inspected:** selected smallest released integration: config `sam2/sam2/configs/samurai/sam2.1_hiera_t.yaml` plus official SAM2.1 Hiera Tiny checkpoint.
- **CODE FACT — inspected:** checkpoint size `156,008,466` bytes; SHA-256 `7402E0D864FA82708A20FBD15BC84245C2F26DFF0EB43A4B5B93452DEB34BE69`.
- **RESOURCE AVAILABILITY FACT:** the official downloader maps Tiny/Small/Base+/Large checkpoints, and the SAMURAI demo maps filenames containing `tiny` to the Tiny config. The root benchmark script defaults to Base+, not Tiny.

### B. Environment

- **CODE FACT — inspected:** isolated CPU runtime used PyTorch `2.12.0+cpu`, torchvision `0.27.0+cpu`, and `SAM2_BUILD_CUDA=0`. Official installation guidance prefers Linux, Python ≥3.10, PyTorch ≥2.3.1, and CUDA; it recommends WSL on Windows.
- **CODE FACT — inspected:** `compileall` passed for `sam2/sam2`; checkpoint loading is strict and the exact Tiny model built with `38,962,498` parameters.

### C. Bounded smoke result

**Status: SUCCESS under the documented CPU/postprocessing deviation**

Official Tiny checkpoint, four consecutive frames extracted from `assets/samurai_demo.mp4`, source resolution 1920×554, `offload_video_to_cpu=True`, `offload_state_to_cpu=True`, CPU FP32/BF16 state behavior as implemented, optional CUDA postprocessing disabled through both `SAM2_BUILD_CUDA=0` and `apply_postprocessing=False`.

| Event | Result |
|---|---|
| build/load after warm filesystem cache | success, 2.230 s; RSS 199.6→538.4 MiB |
| `init_state` | success, 4.295 s; RSS 702.0 MiB |
| add initial bbox prompt | success, 0.264 s; RSS 701.0 MiB |
| propagate frame 1 | success, 6.800 s; output `[1,1,554,1920]` |
| propagate frame 2 | success, 7.648 s |
| propagate frame 3 | success, 7.356 s |

### D. Runtime modes

| Component | Frequency | Inspected boundary |
|---|---:|---|
| full-frame resize and Hiera+FPN encoder | every newly visited frame | source frame is resized to 1024×1024; there is no tracker search crop |
| memory selection/attention | every non-initial frame | conditioning memories, selected historical mask memories, and object pointers |
| SAM decoder | every frame | initial bbox-prompt frame is single-mask; each unprompted propagated frame produces three candidates under the released Tiny config |
| SAMURAI Kalman/mask selection | each unprompted propagated frame | initial bbox-prompt frame does not enter this branch; later selection uses predicted IoU before the stable period and motion weighting after 15 stable frames |
| memory encoder and state append | every propagated frame | compact per-frame mask memory plus output dictionaries |

**CODE FACT — inspected:** Kalman/reliability logic does not skip the full neural frame path.

### E. Latency evidence

- **CODE FACT — inspected:** unprofiled CPU propagation observations were 6.800, 7.648, and 7.356 s; mean 7.268 s/frame.
- **CODE FACT — inspected:** a one-frame PyTorch CPU operator profile took 15.417 s wall time and 9.190 s self-CPU. Highest self-CPU sites were `aten::addmm` 3.213 s (149 calls), `aten::bmm` 1.779 s (31), and CPU scaled-dot-product flash attention 1.305 s (12).
- **LIMIT:** profiler overhead is substantial; neither number is a CUDA, streaming end-to-end, or target-device result.

### F. Memory/state snapshots

| Boundary | RSS | Unique tensors reachable from inference state |
|---|---:|---:|
| after `init_state` | 702.0 MiB | 148.0 MiB |
| after frame 1 | 1,038.7 MiB | 150.5 MiB |
| after frame 2 | 1,403.2 MiB | 151.3 MiB |
| after frame 3 | 1,428.2 MiB | 152.0 MiB |

**LIMIT:** RSS values are event-boundary snapshots, not sampled peaks, and include intermediate working set and allocator state. The reachable-tensor walk avoids double-counting shared tensor views but is not GPU memory.

### G. State, history, and streaming evidence

- **CODE FACT — inspected:** synchronous JPEG loading allocates `[N,3,1024,1024]` FP32, exactly 12 MiB/frame. MP4 loading decodes and stacks the complete video before inference; four test frames therefore occupied 48 MiB.
- **CODE FACT — inspected:** one compact stored frame includes `maskmem_features [1,64,64,64]` BF16 (524,288 bytes), `pred_masks [1,1,256,256]` FP32 (262,144 bytes), object pointer `[1,256]` (1,024 bytes), scores, and shared positional encoding.
- **CODE FACT — inspected:** `num_maskmem=7` bounds non-conditioning mask-memory slots consumed per frame; it does not bound stored `non_cond_frame_outputs`, conditioning-frame attention, or object-pointer history. A new output entry is appended for every processed frame.
- **RESOURCE AVAILABILITY FACT:** the official README explicitly says live/streaming input is unsupported. `init_state` accepts a fixed MP4 or pre-existing JPEG folder and fixes `num_frames`.
- **CODE FACT — inspected:** the released async JPEG loader's background assignment is commented out; a four-frame probe left every cache slot `None` and repeated frame access decoded a new tensor.
- **CODE FACT — inspected:** Kalman state belongs to the model, while `reset_state` clears tracking dictionaries without resetting Kalman mean/covariance/stability/frame count. Official scripts avoid reuse by creating a predictor per video.

### H. Export result

**Result: NOT ATTEMPTED for the full predictor because the release exposes no tensor-only full-predictor forward/export contract.**

- **RESOURCE AVAILABILITY FACT:** no official SAMURAI/SAM2 video-predictor ONNX, TensorRT, or full TorchScript exporter was found.
- **CODE FACT — inspected:** `SAM2Base.forward()` raises `NotImplementedError`; stateful predictor methods are mandatory. Tiny explicitly disables `torch.compile`; the available compile hook covers only the image encoder.
- **CODE FACT — inspected:** the stateful predictor uses Python dictionaries keyed by frame, a generator, threshold branches, `.item()`, NumPy/SciPy Kalman state, and a backward history scan. TorchScript in the release covers only a stateless resize/normalize transform.
- **CODE FACT — inspected:** custom CUDA is confined to connected-components mask postprocessing, which the bounded CPU installation disabled.

### I. Structural HG5 evidence

- **CODE FACT — inspected:** exact Tiny config/checkpoint completes a bounded four-frame propagation under the documented CPU/postprocessing characterization deviation.
- **CODE FACT — inspected:** even the smallest released host processes full 1024² frames, retains sequence-length-growing output state, and has no live-stream API or complete export contract.
- **OPEN QUESTION:** no released or validated explicit neural-engine/host-state export contract was found.

**HG5 = PENDING**

### J. Unresolved blocker

1. **OPEN QUESTION:** CUDA FP16 loadability, synchronized latency, and peak GPU memory for exact Tiny + SAMURAI.
2. **OPEN QUESTION:** long-sequence output-state growth and reliability backward-scan latency.
3. **OPEN QUESTION:** live-frame adapter semantics, bounded output eviction, and explicit Kalman session reset.
4. **OPEN QUESTION:** decomposition/export parity for image encoder, memory attention, decoder, memory encoder, and host controller.
5. **OPEN QUESTION:** effect of disabling connected-components postprocessing on intended behavior.
6. **OPEN QUESTION:** separate stable timings for image encoder, memory attention, mask decoder, and SAMURAI Kalman/mask selection; the bounded run produced full-propagation timing and aggregate operator evidence only.

## 7. CX007 — SpikeTrack

### A. Provenance

- **CODE FACT — inspected:** official repository `faicaiwawa/SpikeTrack`, detached at `1537db51a1cc9f6e30cce469fba3e51f5721b3d0` with no tracked-file modifications; characterization artifacts remained isolated/untracked.
- **CODE FACT — inspected:** primary variant `experiments/spiketrack/spiketrack_s256_t1.yaml`; comparison variant `spiketrack_s256_t3.yaml`. Both use 256² template/search inputs and Small widths `[32,64,128,192]`; T1 requests one template and T3 requests three.
- **RESOURCE AVAILABILITY FACT:** the official Hugging Face repository linked by the release supplies `spiketrack_s256_t1.pth.tar` and `spiketrack_s256_t3.pth.tar`.
- **CODE FACT — inspected:** T1 checkpoint size `47,912,371` bytes, SHA-256 `CF5C078EF7741109B8DB8F8DD66B322B0814BF787AD56A5CDD5594DD2A8B85DF`; T3 size `51,865,011` bytes, SHA-256 `CCF04AA90521B21A78B12F4B978C03D8A69B5F6DE3EE3498A3594E13E98AA491`. Both hashes match the official LFS object identifiers.

### B. Environment

- **CODE FACT — inspected:** candidate-specific environment: Windows 11 build 26200, Python 3.11.7, PyTorch `2.0.0+cu118`, CUDA runtime 11.8, cuDNN 8700, MX250 2 GiB, FP32, batch one.
- **CODE FACT — inspected:** the README requests Python 3.12 while `install.sh` pins PyTorch 2.0.0; Python 3.11 was used because an official PyTorch 2.0.0 CUDA 11.8 wheel was available.
- **CHARACTERIZATION HARNESS — NOT OFFICIAL RELEASE:** local untracked harnesses only exposed timing and tensor I/O. No scientific module or operator was changed.

### C. Bounded smoke result

**Status: SUCCESS**

- **CODE FACT — inspected:** T1 and T3 complete cached-search checkpoints loaded with zero missing/unexpected keys. The release's separate template encoder loads extracted `encoder.*` keys with `strict=False`; it reported zero missing keys and ignored 348 T1 / 492 T3 search-only keys.
- **CODE FACT — inspected:** both variants completed template-cache creation, search encoder, six Memory Retrieval Modules (MRMs), and center head. Output contract: encoded feature `[1,1,192,16,16]`, boxes `[1,1,4]`, score `[1,1,16,16]`, and size/offset maps `[1,2,16,16]`.
- **CODE FACT — inspected:** the official cached T1 tracker completed 20 frames from bundled `video_demo/bell.mp4`, including crop/resize, normalization/host-to-device transfer, network, Hann window, bbox decode/remap, and `.tolist()` output.

### D. Runtime modes

| Mode | Boundary | Persistent state |
|---|---|---|
| construction | build split template/search networks, load checkpoint, move to CUDA | resident weights |
| initialization | encode fixed template list and construct six caches | one or three raw templates + six cache tensors |
| cached steady state | search encoder + all six MRMs + center head | caches reused each frame |
| full tracker | crop/preprocess + cached neural path + Hann/decode/remap | bbox/frame plus template/cache state |
| T3 update | replace template index 1 and rerun complete template/cache path | bounded three-template state |

### E. Latency evidence

Every CUDA measurement synchronized immediately before and after the call.

#### Interleaved T1/T3 comparison

Thirty alternating warm-ups followed by 60 observations per mode; order reversed each iteration.

| Mode | Median (ms) | Min | Max | P95 |
|---|---:|---:|---:|---:|
| cached model T1 | 269.740 | 185.100 | 553.120 | 329.820 |
| cached model T3 | 367.390 | 250.580 | 610.750 | 463.590 |
| template/cache T1 | 200.690 | 140.380 | 383.210 | 302.130 |
| template/cache T3 | 413.130 | 272.540 | 594.140 | 489.050 |

**LIMIT:** variance reflects a Windows WDDM/MX250 development environment. These measurements are not Jetson Nano FPS.

#### Official full-tracker T1 sequence

- **CODE FACT — inspected:** cold constructor 1829.390 ms; cold initialization 1226.490 ms.
- **CODE FACT — inspected:** after five warm-up frames, 15 full-tracker observations had median 225.487 ms, min 203.972 ms, max/P95 251.304 ms.
- **LIMIT:** the interleaved model and short full-tracker tests are separate runs; subtracting them would not isolate preprocessing overhead.

#### Six isolated MRMs

| MRM | Search input | Cache input | T1 median/P95 (ms) | T3 median/P95 (ms) |
|---:|---|---|---:|---:|
| 0 | `[1,1,32,64,64]` | `[T,1,8,4,16]` | 4.800 / 7.000 | 25.380 / 32.200 |
| 1 | `[1,1,64,32,32]` | `[T,1,8,8,32]` | 4.330 / 6.910 | 26.170 / 34.080 |
| 2 | `[1,1,128,16,16]` | `[T,1,8,16,64]` | 3.900 / 6.000 | 23.050 / 29.800 |
| 3 | `[1,1,128,16,16]` | `[T,1,8,16,64]` | 6.280 / 7.490 | 24.060 / 30.180 |
| 4 | `[1,1,192,16,16]` | `[T,1,8,24,96]` | 7.570 / 15.910 | 30.070 / 35.340 |
| 5 | `[1,1,192,16,16]` | `[T,1,8,24,96]` | 6.040 / 9.470 | 26.020 / 31.400 |

**LIMIT:** isolated MRM values are approximate and are not summed as an exact decomposition.

### F. Peak-memory evidence

| Boundary | T1 allocated/reserved peak | T3 allocated/reserved peak |
|---|---:|---:|
| template initialization | 98.906 / 120 MiB | 132.897 / 150 MiB |
| cached steady forward | 108.687 / 124 MiB | 114.275 / 166 MiB |

- **CODE FACT — inspected:** resident split models before input/cache used T1 75.203 MiB allocated/92 MiB reserved and T3 78.944/96 MiB.
- **CODE FACT — inspected:** full-tracker T1 steady peak was 107.121 MiB allocated and 122 MiB reserved.
- **LIMIT:** PyTorch allocator peaks exclude driver/context memory. Separate RSS snapshots were T1 459.551→590.168→629.312 MiB and T3 462.379→595.285→652.910 MiB after models, cache, and steady forward; snapshots are not allocator peaks.

### G. State and dense spike-operator evidence

| Cache | T1 shape | T3 shape |
|---|---|---|
| 0 | `[1,1,8,4,16]` | `[3,1,8,4,16]` |
| 1 | `[1,1,8,8,32]` | `[3,1,8,8,32]` |
| 2/3 | `[1,1,8,16,64]` | `[3,1,8,16,64]` |
| 4/5 | `[1,1,8,24,96]` | `[3,1,8,24,96]` |

- **CODE FACT — inspected:** six-cache payload is 223,232 bytes for T1 and 669,696 bytes for T3. Tracker state is bounded; T3 periodically replaces one dynamic template and nothing grows with video length.
- **CODE FACT — inspected:** template retrieval forms `kᵀv` cache tensors; search queries repeat over the configured template dimension and multiply by those caches. T3 additionally applies a temporal gate; MRM output returns to a single search step.
- **CODE FACT — inspected:** search model contains 189 `mem_update` modules, zero registered membrane buffers, and 567 decay parameters. Membrane/output tensors are local to each forward; no neuron membrane persists across video frames.
- **CODE FACT — inspected:** an actual steady forward observed T1/T3 `Quant` calls 171/267, convolution 126/150, `round` 171/267, `clamp` 173/269, and temporal softmax 0/6. Repository search found no custom CUDA/C++ extension; spike operations decompose into ordinary dense PyTorch clamp/round/divide, convolution, and matmul kernels.

### H. Export result

**Result: SUCCESS for the fixed-T1 template encoder; FAIL for the defining search encoder + head under the pinned exporter stack.**

- **CODE FACT — inspected:** fixed-T1 template encoder exported to ONNX opset 17; checker passed; size `76,870,531` bytes; 3,840 nodes including Round, Clip, ScatterND, MatMul, Conv, and AveragePool.
- **LIMIT:** the template export emitted 250 tensor-to-Python-boolean and 20 tensor-to-Python-integer warnings and is specialized to the tested T1 shapes.
- **CODE FACT — inspected:** the defining search encoder + head export failed unchanged in the repository-pinned PyTorch 2.0.0 stack with `Unsupported: ONNX export of operator adaptive_avg_pool2d, input size not accessible.` The identified path is `MemoryRetrieval::mrm.1` at `lib/models/spiketrack/fuc.py:96`, where a Python timestep loop indexes `x[i]`, applies adaptive pooling, and stacks results.
- **CODE FACT — inspected:** a local wrapper flattened the official six-entry cache dictionary into six tensor inputs without removing a model component. No source rewrite was attempted after the exact failure.
- **LIMIT:** this failure under the pinned stack does not prove all newer exporters fail. Python template updates, tracker controller, crop/resize, Hann window, bbox remap, and `.tolist()` remain outside both graphs.

### I. Structural HG5 evidence

- **CODE FACT — inspected:** exact Small T1/T3 official checkpoints run FP32 on a 2 GiB MX250 with bounded caches and no persistent membrane state.
- **CODE FACT — inspected:** all six MRMs execute every frame; T3 triples cache payload and adds temporal convolution/gating work.
- **CODE FACT — inspected:** the spike path uses dense standard kernels, not an event-driven sparse runtime.
- **CODE FACT — inspected:** fixed T1 template export succeeds, but the unchanged defining search path does not export under the official PyTorch 2.0.0 stack.
- **OPEN QUESTION:** a supported engine path and target-device behavior remain unresolved.

**HG5 = PENDING**

### J. Unresolved blocker

1. **OPEN QUESTION:** unchanged cached-search export using a newer supported exporter without replacing MRM/timestep behavior.
2. **OPEN QUESTION:** TensorRT support/parity for Round, ScatterND, temporal specialization, adaptive pooling, and six-cache state.
3. **OPEN QUESTION:** Jetson Nano latency, peak device memory, power, and sustained thermal behavior.
4. **OPEN QUESTION:** FP16/INT8 numerical and tracking-accuracy parity.

## 8. CX010 — UTPTrack

### A. Provenance

- **CODE FACT — inspected:** official repository `EIT-NLP/UTPTrack`, detached at `84e0f49711254a44f5308faaa9a2405db1964dd7` with no tracked-file modifications; untracked characterization artifacts remained isolated.
- **CODE FACT — inspected:** selected released RGB unit `UTPTrack-O/experiments/ostrackcmp/ceatetta_256_r7_all.yaml` with official Hugging Face snapshot `4372a928e4bf58615ecb217fe5010d2e3212e627`, file `UTPTrack-O-224/OSTrackCMP_ep0300.pth.tar` (`UTPTrack-O/README.md:1-3,60-62`).
- **CODE FACT — inspected:** checkpoint size `1,111,778,541` bytes, SHA-256 `E4EE630CD0E88E41CDBC55BD727C16CA5A4BE3756ADED65F2506B8F670ED0FEF`, epoch 300, network type `OSTrackCMP`; strict load reported all keys matched.
- **CODE FACT — inspected:** the model has 92,518,533 parameters (`370,074,132` FP32 parameter bytes). Checkpoint positional embeddings `[1,64,768]` and `[1,256,768]` corroborate the 128²-template/256²-search mapping; the selected config declares the same template/search sizes (`ceatetta_256_r7_all.yaml:7-22,74-84`).
- **RESOURCE AVAILABILITY FACT:** the release supplies the config, source, and checkpoint. The Hugging Face folder says `UTPTrack-O-224`, while the strict-matched config filename says `ceatetta_256_r7_all`; README commands still mention `ostrack`, but the released implementation and parameter path are `ostrackcmp`.

### B. Environment

- **CODE FACT — inspected:** candidate-specific environment: Windows 11 build 26200, Python 3.12.13, PyTorch `2.5.1+cu121`, CUDA build 12.1, ONNX 1.17.0, ONNX Runtime 1.21.0, MX250 2 GiB (`sm_61`), FP32, batch one.
- **CODE FACT — inspected:** the PyTorch wheel's architecture list includes `sm_61`; CUDA execution and synchronization completed successfully.
- **CHARACTERIZATION HARNESS — NOT OFFICIAL RELEASE:** local untracked timing/hooks and tensor-I/O wrappers only; the scientific graph and all tracked release files remained unchanged.

### C. Bounded smoke result

**Status: SUCCESS**

- **CODE FACT — inspected:** the exact checkpoint completed a strict-loaded CUDA forward with static template `[1,3,128,128]`, dynamic template `[1,3,128,128]`, search `[1,3,256,256]`, annotation `[1,4]`, and CE mask `[1,128]`; the released tracker performs the same hard-CUDA build/load path (`lib/test/tracker/ostrackcmp.py:19-32`).
- **CODE FACT — inspected:** outputs were boxes `[1,1,4]`, score map `[1,1,16,16]`, size/offset maps `[1,2,16,16]`, confidence `[1,1]`, last attention `[1,12,135,135]`, and restored backbone feature `[1,302,768]`.
- **CODE FACT — inspected:** the config uses ViT-B/16 width 768, depth 12, 12 heads (`vit_ceatetta.py:396-401`); search CE at blocks 3/6/9, dynamic/static template elimination at 4/7/10, keep ratio 0.7, and a CENTER head (`ceatetta_256_r7_all.yaml:35-51`).

### D. Runtime modes and physical token trace

| Point | Search | Static template | Dynamic template | Total sequence |
|---|---:|---:|---:|---:|
| input | 256 | 64 | 64 | 384 |
| after block-3 CE | 180 | 64 | 64 | 308 |
| after block-4 DTE + STE | 180 | 45 | 45 | 270 |
| after block-6 CE | 126 | 45 | 45 | 216 |
| after block-7 DTE + STE | 126 | 32 | 32 | 190 |
| after block-9 CE | 89 | 32 | 32 | 153 |
| after block-10 DTE + STE | 89 | 23 | 23 | 135 |
| after search restoration | 256 | 23 | 23 | 302 |

- **CODE FACT — inspected:** these are physical sequence-tensor reductions. Attention runs before each selected pruning step, while subsequent MLP/blocks receive the compacted tensor (`vit_ceatetta.py:44-86,301-323`); final padding/scatter restores the search grid for the head (`vit_ceatetta.py:332-358`).
- **CODE FACT — inspected:** retained lengths are deterministic for the strict-matched 128²-template/256²-search config and 0.7 keep ratios, but selected identities and foreground cardinality are input-dependent. Active PyTorch code uses full `torch.sort`, slicing, gather/indexing, and final `scatter_`, not `torch.topk` (`compression/ce.py:75-128`; `compression/ate.py:5-137`).
- **CODE FACT — inspected:** both raw templates are patch-embedded every frame. Tracker state is bounded at two slots; the dynamic slot is considered every 25 frames and updated only when confidence exceeds 0.70 (`lib/test/tracker/ostrackcmp.py:66-88,98-137`).

### E. Latency evidence

All CUDA measurements synchronized before and after each model-only call; input tensors were preallocated on device. Crop, normalization, Hann decoding, bbox mapping, and template-update preprocessing were excluded.

| Trial | Warm-up / observations | Min (ms) | Median | P95 | Max |
|---|---:|---:|---:|---:|---:|
| primary | 10 / 30 | 167.940 | 174.167 | 313.143 | 318.647 |
| independent | 5 / 20 | 160.468 | 165.584 | 214.425 | 216.453 |
| resource-control | 5 / 10 | 162.610 | 164.222 | 169.221 | 170.261 |

- **CODE FACT — inspected:** instrumented primary-run medians for attention immediately before pruning were 6.449/6.177/6.080/3.486/3.600/3.546 ms at blocks 3/4/6/7/9/10. Search-pruner medians were 1.405/1.585/1.312 ms; dynamic-template pruner 1.657/1.330/1.489 ms; static-template pruner 2.100/2.287/2.319 ms; center head 6.454 ms; isolated exact-shape restoration 0.501 ms (`n=50`).
- **LIMIT:** hooks and synchronization perturb component timings, so those values are not additive. Trial variation reflects a Windows WDDM development laptop and is not a Jetson Nano extrapolation.

### F. Peak-memory evidence

- **CODE FACT — inspected:** after strict checkpoint load and model move, PyTorch CUDA allocated `372,856,320` bytes and reserved `423,624,704` bytes.
- **CODE FACT — inspected:** across seven separate model forwards, per-forward peaks were consistently `420,163,584` allocated and `480,247,808` reserved bytes.
- **CODE FACT — inspected:** 1 ms process sampling over the same seven-forward resource run gave peak-RSS median `2,441,498,624` bytes and max `2,441,588,736` bytes.
- **LIMIT:** allocator values exclude driver/context memory. RSS includes Python, dependencies, checkpoint/training state, and allocators; none is total Nano memory or a feasibility result.

### G. Operator and profiler evidence

- **CODE FACT — inspected:** one CPU operator profile observed nine `aten::sort`, 35 gather, nine index, 15 nonzero, six where, six index-put, one scatter, and zero `aten::topk` calls. Profile overhead means these durations are not a latency decomposition.
- **CODE FACT — inspected:** active pruning applies full sorts, slices kept/non-kept indices, physically gathers tokens, uses annotation-dependent foreground indexing, and restores the search grid with scatter.
- **RESOURCE AVAILABILITY FACT:** shipped `tracking/profile_model.py` is stale for this full unit: it exposes only `ostrack`, calls `build_ostrack`, and invokes a two-input raw model rather than `ostrackcmp` with two templates, annotation, and mask (`tracking/profile_model.py:17-54,92-123`).
- **RESOURCE AVAILABILITY FACT:** no official full UTPTrack-O ONNX, TensorRT, or TorchScript exporter was found. The generic ONNX preprocessor is not a model exporter.

### H. Export result

**Result: SUCCESS for the fixed 128²-template/256²-search unit; FAIL for batch-dynamic and spatial+batch-dynamic export under the tested stack.**

- **CODE FACT — inspected:** the complete fixed 128²-template/256²-search neural graph exported to ONNX opset 17. Checker and shape inference passed; size `369,864,392` bytes; SHA-256 `42685F5284CC0E2CBDC6AA65D914929CA432F565264FB1DCAB7B1616A54AC73E`; 2,420 nodes.
- **CODE FACT — inspected:** the exported graph retained the mechanism: TopK 9 (lowering of fixed-length PyTorch sorts), Gather 105, GatherElements 27, GatherND 9, ScatterElements 1, ScatterND 6, NonZero 15, Where 38, If 2, Slice 89, and Reshape 68.
- **CODE FACT — inspected:** ONNX Runtime CPU parity passed for three annotations with different foreground cardinalities. All five outputs were within `atol=1e-4`, `rtol=1e-3`; maximum observed absolute error was `3.933906555175781e-06`.
- **CODE FACT — inspected:** batch-dynamic and spatial+batch-dynamic exports failed before graph creation with `Unsupported: ONNX export of operator Unfold, input size not accessible`, at foreground-mask creation in `vit_ceatetta.py:237`.
- **LIMIT:** fixed tracing specializes shape-dependent keep lengths. Annotation can change retained identities, but arbitrary batch/resolution/keep-rate export is not established. TensorRT was unavailable, so no engine or engine parity result exists; the Python tracker controller remains outside the graph.

### I. Structural HG5 evidence

- **CODE FACT — inspected:** the exact checkpoint for the strict-matched 128²-template/256²-search unit strict-loads; CE, DTE, and STE physically compact tensors; the complete fixed-shape neural graph retains pruning/restoration in ONNX and executes with ORT parity.
- **CODE FACT — inspected:** state is bounded at two raw templates, but both templates are re-embedded and the ViT-B backbone, pruning stages, and head execute every frame.
- **CODE FACT — inspected:** FP32 model-only CUDA peaks and latency were measured on the MX250 only; they do not establish Jetson Nano feasibility.
- **OPEN QUESTION:** TensorRT engine support/parity, reduced precision, workspace/peak memory, controller integration, and target-device behavior remain unresolved.

**HG5 = PENDING**

### J. Unresolved blocker

1. **OPEN QUESTION:** fixed-ONNX TensorRT support/performance/parity for TopK-as-sort, NonZero, GatherND, ScatterND/ScatterElements, If, and annotation-dependent index counts.
2. **OPEN QUESTION:** variable-batch/resolution export beyond the observed `Tensor.unfold` blocker and fixed keep-length specialization.
3. **OPEN QUESTION:** end-to-end integration of crop/preprocessing, Hann decode/bbox mapping, confidence branch, and dynamic-template update.
4. **OPEN QUESTION:** FP16/INT8 numerical and tracking-accuracy parity.
5. **OPEN QUESTION:** Jetson Nano latency, peak memory, engine workspace, power, and sustained thermal behavior.
6. **OPEN QUESTION:** deployment packaging needed to resolve stale README/profiler paths against the strict-loaded `ostrackcmp` unit.

## 9. Completeness check

“Complete” below means the bounded targeted evidence package is populated; it is not an HG5 decision or a deployability claim.

| Candidate | Exact pin/artifact | Smoke | Latency/memory | State/operators | Export/deployment blocker | Evidence package | HG5 |
|---|---|---|---|---|---|---|---|
| CX007 SpikeTrack | recorded | recorded | recorded | recorded | recorded | **COMPLETE** | PENDING |
| CX010 UTPTrack | recorded | recorded | recorded | recorded | recorded | **COMPLETE** | PENDING |
| CX020 SAMURAI | recorded | recorded | recorded | recorded | recorded | **COMPLETE** | PENDING |
| CX037 SSTrack-AAAI | recorded | recorded | recorded | recorded | recorded | **COMPLETE** | PENDING |
| CX038 MCITrack | recorded | recorded | recorded | recorded | recorded | **COMPLETE** | PENDING |
| CX053 UncTrack | recorded | recorded | recorded | recorded | recorded | **COMPLETE** | PENDING |

## 10. Locked stage state

- HG5 decisions: **NOT MADE**
- HG6: **NOT STARTED**
- S1–S7 / soft scoring: **NOT STARTED**
- primary shortlist: **NONE**
- main baseline: **NONE**
- proposed architecture: **NONE**
