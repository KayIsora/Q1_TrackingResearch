# I1A — SpikeTrack bounded ONNX export, parity, and T1 template-lifecycle protocol

**Date:** 2026-08-29  
**Status:** `LOCKED_BEFORE_EXECUTION`  
**Prerequisite:** `screening/reconciliation/2026-08-29_I0_spiketrack_runtime_reconciliation.md`

## 1. Purpose

I1A determines whether the frozen SpikeTrack-S256-T1 eager implementation can be represented as two fixed-shape ONNX graphs with verifiable output parity, while also testing a T1-only initialization-lifecycle memory cleanup. It is a technical deployment gate, not a scientific contribution or Jetson benchmark.

## 2. Exact baseline contract

- source SHA: `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`;
- config: `experiments/spiketrack/spiketrack_s256_t1.yaml`;
- checkpoint SHA-256: `cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df`;
- BS1 FP32;
- template count: 1;
- template/search crop: 256x256;
- decoder grid: 16x16;
- accepted local eager outputs and I0 wrapper are the parity reference.

## 3. Export decomposition

Create two export-only adapters without changing trained modules:

### Template adapter

Input:

`template [1,1,3,256,256]`

Outputs:

six ordered tensors named:

- `cross_block_0`;
- `cross_block_1`;
- `cross_block_2`;
- `cross_block_3`;
- `cross_block_4`;
- `cross_block_5`.

### Search-decoder adapter

Inputs:

- `search [1,3,256,256]`;
- the six ordered cache tensors with exact eager shapes.

Outputs:

- `pred_boxes`;
- `score_map`;
- `size_map`;
- `offset_map`.

No dynamic axes are required in I1A.

## 4. Export rules

- use the already installed PyTorch and ONNX packages;
- opset 17 unless the exporter proves a lower exact requirement;
- no ONNX Runtime or TensorRT installation;
- no graph simplifier;
- no quantization;
- no trained-weight rewrite;
- no architecture change;
- retain ONNX files externally, not in Git.

One export-only functional repair is permitted if the unmodified adapters fail due to `Quant.apply`, fixed temporal control flow, or indexed write. The repair must:

- be mathematically equivalent for the frozen T1 fixed-shape path;
- pass eager original-versus-export-formulation tensor parity before ONNX export;
- remain isolated in the deployment adapter/patch;
- not alter official source or checkpoint.

A second repair is not permitted.

## 5. Parity gates

Use one frozen canonical initialization/search pair and at least one additional search frame.

Required:

1. ONNX checker passes for both graphs;
2. template cache shape/name/order matches exactly;
3. original eager versus export-adapter eager max absolute difference `<=1e-6`;
4. when ONNX `ReferenceEvaluator` supports the graph, ONNX versus eager:
   - cache tensors `<=1e-4`;
   - all four decoder outputs `<=1e-4`;
   - final bbox absolute difference `<=1e-3`;
5. if ReferenceEvaluator cannot execute because of an unsupported operator, record the exact node/op and conclude runtime parity is blocked; checker-only success is not enough for TensorRT readiness.

## 6. T1 template-encoder lifecycle

Because `NUM_TEMPLATES=1`, the official update branch is inactive.

Test:

1. compute the initialization cache using the official template encoder;
2. preserve the cache unchanged;
3. remove the template encoder from CUDA and then release it entirely for the run;
4. synchronize and clear unused CUDA cache;
5. run Crossing and one profile population using the unchanged search network/decoder.

Required:

- integer and floating prediction parity against the I0 eager reference;
- cache tensor hashes unchanged;
- measured CUDA allocated/reserved memory before and after release;
- no claim that this applies to T3 or multi-template configurations.

## 7. Runtime-wrapper smoke

Use canonical source frames externally to execute:

- one real folder-mode run;
- one temporary MP4 video-mode run;
- identical initial bbox and ordered frames.

Required:

- folder/video boxes identical;
- outputs parse correctly;
- temporary media remains external and uncommitted.

## 8. Stop-loss

- no package installation;
- no dataset/model download;
- no Jetson;
- no TensorRT engine;
- no FP16/INT8;
- no benchmark expansion;
- no training;
- maximum one export-only repair;
- maximum four active technical hours;
- stop after the export/parity and lifecycle questions are answered.

## 9. Allowed outcomes

- `I1A_ONNX_PARITY_PASS_READY_FOR_I1B`;
- `I1A_EXPORT_OR_RUNTIME_PARITY_BLOCKED`;
- `I1A_INCOMPLETE_TECHNICAL_BLOCKER`.

Only the first outcome permits a TensorRT/Jetson protocol.

## 10. Required artifacts

Create bounded text/CSV/JSON/scripts/patches only:

- `screening/codex/2026-08-29_I1A_spiketrack_report.md`;
- `screening/codex/2026-08-29_I1A_spiketrack_results.csv`;
- `screening/codex/2026-08-29_I1A_spiketrack_command_log.txt`;
- `screening/codex/artifacts/I1A_spiketrack/**`;
- `screening/codex/scripts/2026-08-29_I1A_spiketrack_*`;
- at most one `screening/codex/patches/2026-08-29_I1A_spiketrack_export.patch`.

Do not commit ONNX binaries, checkpoints, dataset images, videos, or large tensors.

## Locked state

- I0: **ACCEPTED**;
- I1A: **READY**;
- I1B TensorRT/Jetson: **LOCKED**;
- publication-grade main baseline: **NONE**;
- implementation baseline: **SpikeTrack-S256-T1**;
- proposed Q1 architecture: **NONE**.
