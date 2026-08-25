# SpikeTrack Stage-4A preflight and instrumentation report

**Date:** 2026-08-25

**Candidate:** CX007 SpikeTrack

**Scope:** bounded diagnostic preflight and instrumentation only
**Readiness conclusion:** `STAGE4A_INCOMPLETE`

Stage 4B is locked. This report does not assign `DIAG_PASS`/`DIAG_FAIL`, S1-S7, a score, a rank, a shortlist, a baseline, a proposed architecture, or any Jetson Nano claim.

## Canonical N2 matrix sync (Part A)

**PROJECT DECISION — mechanically transcribed:** the final N2 decisions were copied without reinterpretation from `screening/reconciliation/2026-08-25_stage3B_hg6_N2_reconciliation.md`.

| Candidate | `hg6_novelty` | `decision_state` | Result |
|---|---|---|---|
| CX044 AsymTrack | `FAIL` | `EXCLUDED_HG6_NOVELTY_COLLISION_REFERENCE_ONLY` | PASS |
| CX058 HiT-DyHiT | `FAIL` | `EXCLUDED_HG6_NOVELTY_COLLISION_REFERENCE_ONLY` | PASS |

Mechanical validation passed: the header and all 20 data rows have 54 columns; there are 20 unique candidate IDs; only `hg6_novelty`, `decision_state`, and `evidence_notes` changed for CX044/CX058; all S1-S7 fields and `total_score` remain blank; no SpikeTrack field changed.

## 1. Repository and checkpoint provenance

**FACT — cited:** SpikeTrack is described in the CVPR 2026 paper [R18], and the official repository reference is pinned at commit `1537db51a1cc9f6e30cce469fba3e51f5721b3d0` [R19].

| Item | Resolved value | Status |
|---|---|---|
| Official repository | `https://github.com/faicaiwawa/SpikeTrack` | READY |
| Clean pinned baseline tree | `E:\Robot_Backup\tmp\q1_source_norm\efficiency\repos\SpikeTrack` | clean, exact pinned SHA |
| Isolated instrumentation worktree | `E:\Robot_Backup\tmp\stage4A_spiketrack_worktree` | detached at exact pinned SHA; changes uncommitted and never pushed upstream |
| Primary config | `experiments/spiketrack/spiketrack_s256_t1.yaml` | exact Small-256-T1 |
| Controlled-comparison config | `experiments/spiketrack/spiketrack_s256_t3.yaml` | exact Small-256-T3 |
| T1 tracker checkpoint | `E:\Robot_Backup\tmp\stage2B_spiketrack\ckpt\spiketrack_s256_t1.pth.tar` | READY |
| T3 tracker checkpoint | `E:\Robot_Backup\tmp\stage2B_spiketrack\ckpt\spiketrack_s256_t3.pth.tar` | READY |

| Variant | Bytes | SHA-256 | Checkpoint load |
|---|---:|---|---|
| S256-T1 | 47,912,371 | `cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df` | network: 0 missing, 0 unexpected |
| S256-T3 | 51,865,011 | `ccf04aa90521b21a78b12f4b978c03d8a69b5f6de3ee3498a3594e13e98aa491` | network: 0 missing, 0 unexpected |

**FACT — local verification:** both SHA-256 values match the LFS object IDs exposed by the official Hugging Face model repository linked from the pinned official source [R19]. The long template-encoder `unexpected_keys` lists (348 for T1; 492 for T3) are also present under the unmodified official loading path: search-only `mrm.*` keys are filtered from the tracker state and ignored when loading the structurally different template encoder with `strict=False`. They are not instrumentation drift.

### SDTV3 pretraining versus tracker checkpoint

The training builder at `lib/models/spiketrack/sdtv3.py` expects `pretrained_models/V3_5.1M_1x4.pth` (top-level key `model`) as Small SDTV3 backbone initialization. That file is absent locally. It is a training dependency, not the final tracker checkpoint: the pinned inference builder loads the complete released T1/T3 tracker `net` weights and does not load `V3_5.1M_1x4.pth`. Therefore its absence blocks training provenance reconstruction but does not block the released-checkpoint inference smokes. The T3 YAML's `MODEL.PRE_TRAINED` T1 hint has no consumer in the pinned training/source search; the released T3 tracker checkpoint was loaded directly. These source facts are bounded to the pinned tree [R19].

## 2. Environment

**LOCAL MEASUREMENT — development machine only:** these measurements are characterization evidence, not deployment or Jetson Nano evidence.

| Field | Value |
|---|---|
| OS | Microsoft Windows 11 Home Single Language, version/build `10.0.26200` / `26200`, 64-bit |
| CPU | Intel Core i7-1065G7 @ 1.30 GHz; 4 physical / 8 logical cores |
| RAM | 16,951,066,624 bytes (15.79 GiB) |
| GPU | NVIDIA GeForce MX250, compute capability 6.1 |
| GPU memory | 2,048 MiB |
| NVIDIA driver / driver-reported CUDA maximum | 581.83 / 13.0 |
| Python | 3.11.7 |
| PyTorch / CUDA build / cuDNN | `2.0.0+cu118` / 11.8 / 8700 |
| torchvision / timm | `0.15.1+cu118` / `0.5.4` |
| NumPy / OpenCV / PyYAML | `1.26.4` / `4.11.0` / `6.0.3` |
| yacs / easydict | `0.1.8` / `1.13` |
| Bounded evaluator additions | pandas 2.2.3; tqdm 4.67.1; tensorboardX 2.6.4; lmdb 1.7.3; jpeg4py 0.1.4 |
| Inference dtype | FP32, batch 1 |

Deterministic smoke/reproduction settings were: seed `20260825` for Python, NumPy, Torch, and all CUDA devices; `torch.use_deterministic_algorithms(True)`; `torch.backends.cudnn.deterministic=True`; `torch.backends.cudnn.benchmark=False`; and `CUBLAS_WORKSPACE_CONFIG=:4096:8`. The CuBLAS variable is set before importing Torch in the preserved smoke runner.

The bounded dependency additions were environment-only repairs; no scientific-model compatibility patch was made. After repair, `python -B tracking/test.py --help` succeeds. The accepted parser flag is `--dataset_name` (not the README spelling `--dataset`). A full CLI benchmark remains unconfigured because `lib/test/evaluation/local.py` is absent and the local OTB sequences are fragmented rather than assembled into an OTB root.

Exact evaluator/code path:

1. `tracking/test.py`
2. `lib/test/evaluation/datasets.py`
3. `lib/test/evaluation/otbdataset.py`
4. `lib/test/evaluation/running.py`
5. `lib/test/evaluation/tracker.py`
6. `lib/test/tracker/spiketrack_inf.py`
7. offline metric: `lib/test/analysis/extract_results.py` through `lib/test/analysis/plot_results.py`

## 3. Dataset/raw-result inventory

Only a locally available dataset family supported by the pinned evaluator was inventoried. No benchmark image dataset was downloaded.

| Dataset | Local path/status | Images/video | Ground truth | Official evaluator | Official raw predictions | Sequence count | Attributes/metadata | Later similar-distractor suitability |
|---|---|---|---|---|---|---|---|---|
| OTB100 | ten usable sequence-complete units scattered below `E:\Robot_Backup\TrackingResearch-master\OtherTracker\verified`; no configured OTB root | yes for the ten units | yes for the ten official frame ranges | yes, pinned OTB loader and analysis code | official S256-T1 raw archive available in temporary storage | 100 official raw-result sequences; 10 usable local units | partial official OTB attributes resolved | suitable for Manager review; inventory only |

The ten local units are Bolt, Couple, Crossing, Deer, Diving (official frames 1-215; 16 extra tail images ignored), DragonBaby, FaceOcc1, Jogging_1 (local folder `Jogging1`), MotorRolling, and Skiing. No usable complete local image root was found for LaSOT, GOT-10k, TrackingNet, UAV123, TNL2K, NFS, or LaSOT Extension.

**FACT — cited and locally verified:** the pinned repository exposes released raw results [R19]. The small official S256-T1 raw-result archive (Google Drive file ID `1QAST-IzBr2rhAteZq_vc0GZszinIOxbD`) was synchronized only after the three-sequence predeclaration; no dataset images were downloaded. Local archive evidence:

- bytes: 15,632,995;
- SHA-256: `7e9f8e40d069f73a7b33edfc9593946af478caa3206670847ebde78cbc545c25`;
- raw prediction/time pairs: GOT-10k 180, LaSOT 280, TrackingNet 511, TNL2K 700, LaSOT Extension 150, UAV123 123, OTB100 100.

The raw predictions were used only for the bounded reproduction comparison, never to select slice records or distractor reasons.

## 4. Baseline smoke/reproduction status

### Predeclaration

Before any local tracker run, three OTB sequences were fixed solely from local image/ground-truth completeness and short length:

1. Deer — 71 frames
2. Crossing — 120 frames
3. Couple — 140 frames

No SpikeTrack prediction, score, released failure frame, or raw-result value was inspected to choose these sequences.

### Exact bounded run

The clean pinned tree, exact S256-T1 config, exact T1 checkpoint, FP32/CUDA, seed `20260825`, and deterministic settings above were used. A bounded adapter called the pinned `lib/test/tracker/spiketrack_inf.py` implementation directly and then matched `lib/test/evaluation/running.py::save_bb` (`astype(int)`, `%d`) plus `lib/test/analysis/extract_results.py` semantics: inclusive-coordinate IoU, thresholds 0:0.05:1, strict `>`, and first prediction replaced by ground truth. This was exactly three sequences, not a full OTB run.

| Sequence | Released raw Success AUC | Local Success AUC | Absolute difference (pp) | <= 0.5 pp | Evaluator/config match |
|---|---:|---:|---:|---|---|
| Deer | 18.041583% | 47.954393% | 29.912810 | FAIL | exact tracker/config/checkpoint/metric/save semantics; bounded adapter |
| Crossing | 79.523810% | 80.000000% | 0.476190 | PASS | exact tracker/config/checkpoint/metric/save semantics; bounded adapter |
| Couple | 76.190476% | 77.653061% | 1.462585 | FAIL | exact tracker/config/checkpoint/metric/save semantics; bounded adapter |

**Baseline reproduction: FAIL.** Two of three predeclared sequences exceed the protocol target.

Mismatch evidence:

- Local Deer predictions repeated exactly under the declared deterministic settings (`max_abs=0` after official integer persistence), so the failure is not local repeat instability.
- The first post-initialization box already differs from released raw output: Deer maximum component difference 6 px, Crossing 1 px, Couple 2 px. Maximum later differences are 363 px at Deer frame 17, 7 px at Crossing frame 43, and 16 px at Couple frame 116.
- Checkpoint SHA, config variant, sequence length, evaluator formula, and integer save semantics were verified and therefore do not explain the remaining discrepancy.
- **OPEN QUESTION:** the released raw archive does not carry the authors' run OS/GPU/driver/Python/dependency/determinism manifest or local OTB file checksums. The exact residual source is unresolved.
- **INTERPRETATION — reasoned:** small cross-platform/kernel or source-file differences can be amplified by an autoregressive tracker, which is consistent with the observed early small differences and later Deer drift; this is not established as the unique cause.

Smallest next action: obtain the released run's environment and OTB checksums from the authors, or obtain Manager approval for an isolated Linux/Python 3.12 environment matching the pinned `install.sh`, then rerun only these same three predeclared sequences. No model rewrite is warranted.

Separately, checkpoint-backed synthetic forward smokes passed for exact T1 and T3. Both networks loaded with zero missing/unexpected final-network keys, produced finite outputs, and exercised the intended Small-256 variant. These smokes are wiring evidence, not benchmark reproduction.

## 5. MRM map

All six MRMs are in `lib/models/spiketrack/sdtv3_search_inference.py::Spiking_vit_MetaFormer_Spike_SepConv`. Public IDs are one-based while the official `ModuleList` is zero-based.

| MRM | Exact code module | Execution point | Observed S256 input/output shape | T1 cache shape | T3 cache shape |
|---|---|---|---|---|---|
| MRM1 | `mrm[0]` | after `downsample1_2`, before `ConvBlock1_2` | `1x1x32x64x64` | `1x1x8x4x16` | `3x1x8x4x16` |
| MRM2 | `mrm[1]` | after `downsample2`, before `ConvBlock2_1` | `1x1x64x32x32` | `1x1x8x8x32` | `3x1x8x8x32` |
| MRM3 | `mrm[2]` | after `downsample3`, before `block3[0]` | `1x1x128x16x16` | `1x1x8x16x64` | `3x1x8x16x64` |
| MRM4 | `mrm[3]` | after `block3[2]`, before `block3[3]` | `1x1x128x16x16` | `1x1x8x16x64` | `3x1x8x16x64` |
| MRM5 | `mrm[4]` | after `downsample4`, before `block4[0]` | `1x1x192x16x16` | `1x1x8x24x96` | `3x1x8x24x96` |
| MRM6 | `mrm[5]` | after `block4[1]`, at encoder output | `1x1x192x16x16` | `1x1x8x24x96` | `3x1x8x24x96` |

The search time dimension is 1 for both modes; the template/cache leading dimension is 1 for T1 and 3 for T3.

## 6. Instrumentation design

Instrumentation is disabled by default and introduces no state-dict keys. Opt-in configuration is exposed by:

- `SPIKETRACK_STAGE4A_DIAGNOSTICS`
- `SPIKETRACK_STAGE4A_ABLATION`
- `SPIKETRACK_STAGE4A_LOG_PATH`

For every MRM, the hook logs public ID, exact module path/index, execution order/insertion point, input/output/cache shapes, input/output/template time dimensions, residual/output/applied-output L2 norms, CUDA-synchronized module latency, instrumented search-encoder total latency, dtype/device, selected control, and `physical_skip=false`.

At tracker level, enabled JSONL logging adds frame ID, T1/T3 mode, prediction box, score-map maximum, confidence, template refresh event, template age, and CUDA-synchronized search-encoder-plus-decoder latency. A one-frame real-image T1 smoke on Deer emitted six ordered MRM records plus one tracker-frame record and preserved the official three-element `track()` return contract.

Latency semantics are explicit: MRM/module and total instrumented timings include synchronization and diagnostic record/norm overhead. Single desktop smoke timings are not baseline speed, savings, benchmark performance, or deployment evidence.

No router, predictor-training module, physical path skip, new architecture, dataset content, or checkpoint mutation is present.

## 7. Output-parity result

**Output parity: PASS.** Two independent processes were compared:

- A: unmodified clean pinned source;
- B: instrumented source with logging enabled and ablation `none`.

Both used the same pinned commit, exact config/checkpoint SHA, deterministic settings, synthetic tensor seed, FP32 dtype, and MX250 CUDA device. For both T1 and T3, the observed maximum absolute difference was `0.0` for the encoded tensor, prediction box, full score map, scalar score maximum, and every head tensor (`offset_map`, `pred_boxes`, `score_map`, `size_map`). Their full tensor fingerprints were also byte-identical. This is stricter than the declared `1e-6` tolerance.

The instrumented source's default-off path versus logging-on/no-ablation path also had maximum absolute difference `0.0`. Instrumentation parity is complete; the separate released-raw reproduction failure is not instrumentation drift.

A separate real-image tracker-level check used the same Deer initialization and second source frame in the clean and instrumented trees. Both returned `[307.44290924072266, 4.5905303955078125, 105.06944274902344, 81.77981567382812]`, giving prediction-box maximum absolute difference `0.0`; the instrumented path additionally emitted the six MRM records and tracker-frame record.

## 8. Diagnostic-control smoke result

**MRM instrumentation/control implementation: COMPLETE.** On both exact T1 and T3 checkpoint-backed synthetic smokes, all nine selectors passed:

- individual: `mrm1`, `mrm2`, `mrm3`, `mrm4`, `mrm5`, `mrm6`;
- grouped: `early={1,2}`, `middle={3,4}`, `late={5,6}`.

For a selected MRM, the full official MRM executes first; the hook computes its residual and deterministically returns the input, equivalent to zeroing the whole MRM residual. Every selector still executed all six MRMs, all head outputs were finite, and every record reported `physical_skip=false`. These controls are contribution tests only and do not represent compute savings.

No full diagnostic dataset or per-MRM ablation campaign was run.

## 9. Slice-inventory summary

`screening/codex/2026-08-25_stage4A_spiketrack_slice_inventory.csv` contains ten OTB sequence inventory rows. Every row has `manager_review_status=PENDING`; no discovery/hold-out split, final ambiguity label, interval, or frozen slice was assigned.

Candidate distractor reasons are populated only for Bolt, Couple, Deer, and Jogging_1 from direct source-frame visual inspection independent of tracker output. Blank reasons remain blank. SpikeTrack predictions, scores, failure frames, and released raw-result values were not used to select or justify any inventory row.

**Slice inventory: COMPLETE as an unfrozen inventory.** Manager review remains required.

## 10. Exact blockers

| Blocker | Classification | Exact evidence | Smallest next action |
|---|---|---|---|
| Bounded reproduction exceeds 0.5 pp on Deer and Couple | scientific reproduction / execution provenance | 29.912810 pp and 1.462585 pp differences after exact checkpoint/config/metric/save checks | obtain author run manifest and OTB checksums, or Manager-authorized matching Linux/Python 3.12 rerun of the same three sequences |
| Official full OTB CLI layout not configured | data/configuration | `lib/test/evaluation/local.py` absent; ten sequences are scattered rather than an OTB root | create temporary path configuration/staging only if Manager authorizes a further bounded rerun |
| SDTV3 Small pretraining asset absent | training provenance, not inference | `pretrained_models/V3_5.1M_1x4.pth` not found | obtain only if training provenance reconstruction is later authorized |

The first blocker prevents Stage-4A readiness. It is not a `DIAG_FAIL` assignment.

## 11. Files/patch produced

Q1 repository deliverables:

1. `screening/candidate_screening_matrix.csv`
2. `screening/codex/2026-08-25_stage4A_spiketrack_preflight.md`
3. `screening/codex/2026-08-25_stage4A_spiketrack_instrumentation_manifest.csv`
4. `screening/codex/2026-08-25_stage4A_spiketrack_slice_inventory.csv`
5. `screening/codex/patches/2026-08-25_spiketrack_stage4A_instrumentation.patch`

The unified patch contains only:

- `lib/models/spiketrack/sdtv3_search_inference.py`
- `lib/models/spiketrack/spiketrack_inf.py`
- `lib/test/parameter/spiketrack.py`
- `lib/test/tracker/spiketrack_inf.py`
- `tracking/stage4a_spiketrack_smoke.py`

`git apply --check` passed against a clean tree at `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`. The patch contains no dataset, checkpoint, physical skip, router, proposed architecture, or training code for a new module.

## 12. Stage-4A readiness conclusion

`STAGE4A_INCOMPLETE`

Source/checkpoint resolution, six-MRM instrumentation, no-ablation parity, all nine deterministic controls, patch preservation, and the independent slice inventory are complete. Readiness is withheld because the bounded three-sequence released-result reproduction failed the <=0.5 percentage-point gate on two sequences and its remaining official-run provenance difference is unresolved.

- `STAGE 4B: LOCKED`
- `DIAG PASS/FAIL: NOT ASSIGNED`
- `S1-S7: NOT STARTED`
- `PRIMARY SHORTLIST: NONE`
- `MAIN BASELINE: NONE`
- `PROPOSED ARCHITECTURE: NONE`

STOP. Wait for Manager Stage-4A reconciliation.
