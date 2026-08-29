# I0 — Frozen reproducible SpikeTrack-S256-T1 implementation runtime

Date: 2026-08-29

Branch: `codex/i0-spiketrack-runtime`

Required starting HEAD: `8281cc53d670886fa5bbf9a3482ae70317b0693f`

Final state: `I0_COMPLETE_READY_FOR_I1`

## Decision and boundary

SpikeTrack-S256-T1 is frozen as the project implementation/thesis-engineering baseline. This result does not reopen the failed MRM1 hypothesis, does not reverse `DIAG_FAIL`, and does not create a publication-grade main baseline. I0 used only the three locked OTB sequences and did not train, download an asset, modify the architecture, apply Stage-4/research instrumentation, export a model, run the full OTB100 benchmark, or begin any other tracker/dataset/Jetson/person-extension lane.

## Frozen identities

| Item | Frozen value | Result |
|---|---|---|
| Official source | `https://github.com/faicaiwawa/SpikeTrack.git` | PASS |
| Source commit | `1537db51a1cc9f6e30cce469fba3e51f5721b3d0` | PASS |
| Fresh source worktree | `E:\Robot_Backup\tmp\i0_spiketrack_runtime_20260829` | clean at every wrapper invocation |
| Config | `experiments/spiketrack/spiketrack_s256_t1.yaml` | PASS |
| Config SHA-256 | `9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8` | PASS |
| Checkpoint | `E:\Robot_Backup\tmp\stage2B_spiketrack\ckpt\spiketrack_s256_t1.pth.tar` | PASS |
| Checkpoint SHA-256 | `cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df` | PASS |
| Checkpoint size | 47,912,371 bytes (45.693 MiB) | recorded |
| Canonical OTB root | `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015` | PASS |

The source worktree was created detached at the pinned commit from an existing local official clone. Its source SHA, clean status, config hash, and checkpoint hash are rechecked inside every wrapper invocation before model construction.

## Strict checkpoint load

Strict load is `PASS`.

- The complete official network accepted all 1,215 checkpoint state entries with `strict=True`: zero missing keys and zero unexpected keys.
- The official runtime separately constructs a template encoder. Its exact 764-key target keyspace was selected from the checkpoint's `encoder.*` entries and accepted with `strict=True`: zero missing keys and zero unexpected keys.
- The remaining 348 `encoder.mrm.*` entries are search-only MRM state absent by design from the official template encoder. They were not silently ignored: the sorted list is retained in each run's `provenance.json`.
- The pinned source itself calls `strict=False`; the I0 wrapper adds a fail-closed strict preflight before invoking that unchanged official tracker class.

No checkpoint tensor was changed, renamed, synthesized, or downloaded.

## Runtime wrapper

The wrapper is `screening/codex/scripts/2026-08-29_I0_spiketrack_runtime.py`. It calls the official `lib.test.tracker.spiketrack_inf.SpikeTrack`, forces diagnostics off, and exposes:

- `--mode otb --sequence <exact-name>` with the official OTB metadata and initialization;
- `--mode folder --input <folder> --init-bbox x y w h`;
- `--mode video --input <video> --init-bbox x y w h`;
- optional synchronized model-forward measurement via `--measure-model-forward --warmup-forwards 30`.

Each invocation emits `boxes.txt`, `per_frame_timing.csv`, and `provenance.json`. `boxes.txt` uses the accepted local operational baseline's tab-separated integer/CRLF serialization. The provenance includes identities, environment, strict-load audit, parameter counts, memory, timing, and integer/floating prediction hashes.

Example OTB command:

```powershell
& 'E:\Robot_Backup\tmp\stage2B_spiketrack_env\Scripts\python.exe' `
  'screening\codex\scripts\2026-08-29_I0_spiketrack_runtime.py' `
  --mode otb --sequence Crossing `
  --output-dir 'screening\codex\artifacts\I0_spiketrack\example_crossing'
```

The OTB path was execution-tested by all parity/profile runs. Folder/video input enumeration and explicit-bbox paths are implemented and parser-validated; no image or video was copied into the repository merely to create an additional smoke asset.

## Locked parity smoke

Comparison target: committed local official-runner predictions at `screening/codex/artifacts/stage4A_E2/reproduction/predictions/acquired_default/`. Author raw predictions were not used as an I0 gate.

| Sequence | Rows | Accepted/local integer SHA-256 | Run1 | Run2 | Float repeat hash | Result |
|---|---:|---|---|---|---|---|
| Crossing | 120 | `039d9ca9…f65f` | exact | exact | `e41892f6…cbd5` both runs | PASS |
| Deer | 71 | `88a49dcd…fdf5` | exact | exact | `eeb23a7c…3e51` both runs | PASS |
| Couple | 140 | `ced31cb5…fe38` | exact | exact | `783d9c32…316f` both runs | PASS |

All six runs used a fresh sequential tracker instance, the exact checkpoint, official first-frame ground truth, and diagnostics disabled. Integer parity and repeat-run floating-output equality are both `PASS` for every sequence.

## Runtime characterization

Environment: NVIDIA GeForce MX250 (2,048 MiB), driver 581.83, Python 3.11.7, PyTorch 2.0.0+cu118, CUDA 11.8, cuDNN 8700, BS1 FP32. Deterministic algorithms were enabled; cuDNN benchmarking was disabled. Model and E2E timing use CUDA synchronization.

Each of the three locked sequences used 30 warm-up forwards. The measured populations are 89 Crossing + 40 Deer + 109 Couple = 238 model forwards. Warmups were excluded from latency distributions, and CUDA peak-memory counters were reset immediately before the first measured forward of each profile.

| Scope | Measured | Model median / p90 / p95 (ms) | Model FPS | E2E median / p90 / p95 (ms) | E2E FPS |
|---|---:|---|---:|---|---:|
| Crossing | 89 | 342.561 / 589.899 / 669.169 | 2.919 | 346.552 / 596.572 / 694.709 | 2.886 |
| Deer | 40 | 321.339 / 441.005 / 463.083 | 3.112 | 326.211 / 444.869 / 469.201 | 3.066 |
| Couple | 109 | 300.935 / 364.990 / 394.465 | 3.323 | 305.562 / 370.032 / 401.354 | 3.273 |
| Pooled locked population | 238 | **307.987 / 486.822 / 582.735** | **3.247** | **312.460 / 492.228 / 591.067** | **3.200** |

These numbers characterize only the current available GPU and the frozen I0 software state; they are not Jetson, TensorRT, FP16, INT8, or publication benchmark claims.

## Parameters, model size, and memory

| Quantity | Actual value |
|---|---:|
| Official network (search encoder + decoder) | 11,760,130 parameters |
| Separate official template encoder | 7,663,086 parameters |
| Total resident runtime modules | 19,423,216 parameters |
| Resident FP32 parameter bytes | 77,692,864 bytes (74.094 MiB) |
| Checkpoint | 47,912,371 bytes (45.693 MiB) |
| Peak CUDA allocated | 137,489,920 bytes (131.121 MiB) |
| Peak CUDA reserved | 161,480,704 bytes (154.000 MiB) |
| Peak host process RAM | 707,620,864 bytes (674.840 MiB) |

The 19.42M resident total includes the separately instantiated template encoder. Its weights are loaded from the corresponding checkpoint encoder subset, so the runtime holds a duplicate template-side module even though the checkpoint stores the full network once.

## ONNX/TensorRT source-only inventory

No export was attempted. The complete inventory is in `artifacts/I0_spiketrack/onnx_tensorrt_blockers.json`.

The frozen graph is naturally two-stage: a fixed BS1/256 template encoder produces six stage-dependent cache tensors, then a fixed BS1/256 search encoder consumes those caches and emits a temporal feature tensor for a decoder producing `pred_boxes`, `score_map`, `size_map`, and `offset_map`. Source frame size and sequence length remain host-side; the tracker also retains the previous bbox in Python state.

Confirmed blockers for a direct export are the unusable direct `SPIKETRACK.forward(mode='encoder')` signature, a Python dict cache interface that cannot be a stable TensorRT binding set, tracker-side Python crop/state/postprocessing, and the absence of ONNX Runtime/TensorRT from the frozen environment. Likely exporter/parser risks include `Quant(torch.autograd.Function)`, `Quant.apply`, temporal Python loops, shape-dependent branches, indexed tensor assignment, and the eventual handling of round/gather/mod/scatter-like forms. No custom compiled C++/CUDA extension was found.

The minimum I1 experiment is therefore an export-only two-adapter test with flat named cache tensors, fixed BS1 FP32/256 shapes, eager reference tensors, ONNX checker/parity first, and only then one FP32 TensorRT parse/build and output parity check. No performance work should precede tensor/bbox parity.

## Artifact map and conclusion

- Frozen summary provenance: `artifacts/I0_spiketrack/provenance.json`
- Six-run parity table: `artifacts/I0_spiketrack/parity_results.csv`
- Per-sequence and pooled runtime table: `artifacts/I0_spiketrack/runtime_measurements.csv`
- Environment and exact package freeze: `artifacts/I0_spiketrack/environment.json`, `environment_pip_freeze.txt`
- Memory: `artifacts/I0_spiketrack/memory.json`
- ONNX/TensorRT source inventory: `artifacts/I0_spiketrack/onnx_tensorrt_blockers.json`
- Raw bounded run outputs: `artifacts/I0_spiketrack/parity/` and `profile/`
- File hashes/sizes: `2026-08-29_I0_spiketrack_runtime_manifest.csv` and `artifacts/I0_spiketrack/artifact_manifest.csv`

All I0 identity, strict-load, parity, repeatability, runtime, wrapper, memory, and source-only deployment-inventory gates are satisfied. The allowed final state is:

`I0_COMPLETE_READY_FOR_I1`

`I1 EDGE CHARACTERIZATION: LOCKED PENDING MANAGER REVIEW`

`PUBLICATION-GRADE MAIN BASELINE: NONE`

`IMPLEMENTATION BASELINE: SPIKETRACK-S256-T1`

`NEW SCREENING: CLOSED`

`PROPOSED Q1 ARCHITECTURE: NONE`
