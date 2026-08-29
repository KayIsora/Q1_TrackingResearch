# I0 — SpikeTrack implementation-runtime reconciliation

**Date:** 2026-08-29  
**Status:** `I0_ACCEPTED_I1A_EXPORT_GATE_READY`  
**Reviewed Codex commit:** `adde77b7df9aa8f4a59ecdf1f1cb57240d11d10d`

## Boundary

This reconciliation accepts SpikeTrack-S256-T1 only as the project implementation/thesis-engineering baseline. It does not reverse the earlier `DIAG_FAIL`, create a publication-grade main baseline, claim a new algorithmic contribution, or authorize benchmark expansion, Jetson execution, training, person-extension work, or renewed tracker screening.

## 1. Accepted identity and parity evidence

The following frozen contract is accepted:

- official source: `faicaiwawa/SpikeTrack`;
- source SHA: `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`;
- config: `experiments/spiketrack/spiketrack_s256_t1.yaml`;
- config SHA-256: `9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8`;
- checkpoint SHA-256: `cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df`;
- checkpoint size: `47,912,371` bytes;
- complete network strict-load: pass;
- exact template-encoder target-keyspace strict-load: pass;
- Crossing, Deer and Couple integer parity against the accepted local operational baseline: pass;
- repeat-run integer and floating prediction hashes: pass.

The clean runtime wrapper is accepted for OTB execution. Folder/video modes are implemented but still require a real input smoke before robot integration.

## 2. Accepted measured runtime

Current available-device characterization:

- GPU: NVIDIA GeForce MX250 2 GiB;
- BS1 FP32 deterministic mode;
- 238 measured forwards after 90 total warmups;
- pooled median model-forward latency: `307.987 ms` (`3.247 FPS`);
- pooled median end-to-end latency: `312.460 ms` (`3.200 FPS`);
- peak CUDA allocated/reserved: `131.121 / 154.000 MiB`;
- peak host process RAM: `674.840 MiB`.

These values are accepted only as the current eager-runtime reference. They are not Jetson, TensorRT, FP16, INT8, or publication benchmark results.

The current E2E median would require approximately:

- `6.25x` acceleration to reach 20 FPS (`50 ms/frame`);
- `7.81x` acceleration to reach 25 FPS (`40 ms/frame`).

This arithmetic is a deployment-risk indicator, not a prediction of Jetson performance.

## 3. Parameter reporting rule

Three values must remain distinct:

1. author/paper-scale model report: approximately `11.2M`;
2. exact official network instantiated in I0: `11,760,130` parameters;
3. exact resident official runtime including the separately instantiated template encoder: `19,423,216` parameters.

The resident total is the deployment-memory quantity. It must not be presented as the unique scientific model parameter count in benchmark comparisons.

## 4. Immediate deployment observation

The selected T1 config has `TEST.NUM_TEMPLATES: 1`. In the official tracker, online template re-encoding is guarded by `if self.num_template > 1`; therefore the separate template encoder is used for initialization only in S256-T1.

The separate template encoder contains `7,663,086` parameters, or about `30.65 MiB` of FP32 parameter storage. I1A may test an initialization-only lifecycle in which the cache is produced exactly once and the template encoder is then moved off GPU or released. This is an engineering memory optimization only and requires exact output parity.

## 5. ONNX/TensorRT decision

The source-only inventory is accepted. A direct export is not yet established because:

- the model lacks a clean single export signature;
- template/search interaction uses a six-entry Python dictionary cache;
- tracker crop/state/postprocessing remains in Python;
- `Quant.apply`, temporal loops and indexed writes may create exporter/parser risks;
- ONNX Runtime and TensorRT were not used in I0.

The minimum next step is a bounded export/parity gate, not immediate Jetson benchmarking or performance optimization.

## 6. I1A authorization boundary

I1A may:

- create flat fixed-shape template and search-decoder export adapters;
- export BS1 FP32 256x256 ONNX graphs;
- run ONNX checker and the already installed ONNX reference evaluator when technically supported;
- perform one functionally equivalent export-only repair if required before any deployment claim;
- verify tensor/map/bbox parity;
- test initialization-only template-encoder release with exact prediction parity and memory measurement;
- execute one real folder-mode and one temporary-video-mode wrapper smoke using canonical frames.

I1A may not:

- install ONNX Runtime or TensorRT;
- build a TensorRT engine;
- run Jetson;
- use FP16/INT8;
- change trained architecture or weights;
- run full benchmarks;
- train/fine-tune;
- begin person extension.

## Locked state

- I0: **COMPLETE / ACCEPTED**;
- publication-grade main baseline: **NONE**;
- implementation baseline: **SpikeTrack-S256-T1**;
- I1A export/parity gate: **READY**;
- I1B TensorRT/Jetson: **LOCKED**;
- new screening: **CLOSED**;
- proposed Q1 architecture: **NONE**.
