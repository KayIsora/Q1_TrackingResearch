# Stage 2A — Batch B code / engineering evidence audit

Date: **2026-08-25**

Lane: **Codex worker — code and engineering audit**

Stage: **Stage 2A, Batch B evidence extraction only**

## 1. Scope, labels, and stopping boundary

This report records implementation evidence for the five active Batch B candidates:

- CX017 — GOT-JEPA
- CX020 — SAMURAI
- CX024 — DAM4SAM
- CX037 — SSTrack-AAAI
- CX038 — MCITrack

These candidates remain members of the scientific-audit queue. They are **not a shortlist**.

Every repository was inspected in an isolated checkout at the exact full SHA registered in the project source manifest. File and line references below refer to those pinned trees. No training, benchmark reproduction, model export, TensorRT build, or Jetson Nano benchmark was performed.

Evidence labels:

- **CODE FACT — inspected:** directly visible in the pinned implementation or released configuration.
- **RESOURCE AVAILABILITY FACT:** directly visible release, checkpoint, script, or tool availability.
- **ENGINEERING TARGET TO PROFILE:** a code-visible execution site whose measured cost remains unknown.
- **OPEN QUESTION:** evidence not found or an implementation ambiguity not resolved by inspection.

This report does not decide HG4 or HG5. It does not begin HG6, S1–S7 assignment, soft scoring, ranking, shortlist selection, baseline selection, or architecture design. The canonical candidate matrix was not modified. Batch C was not activated.

## 2. Completion and stage guard

| Candidate | Pinned source inspected | Code-audit state |
|---|---:|---:|
| CX017 GOT-JEPA | yes | complete |
| CX020 SAMURAI | yes | complete |
| CX024 DAM4SAM | yes | complete |
| CX037 SSTrack-AAAI | yes | complete |
| CX038 MCITrack | yes | complete |

The completion labels mean only that the required code-evidence fields were inspected. They do not mean successful reproduction or an HG4/HG5 decision.

## 3. CX017 — GOT-JEPA

### A. Provenance and audited variant

- **Repository:** `chenshihfang/GOT`
- **Pinned ref:** `84e9324317e4afe62c06b2c51a97563f79730a2e`
- **Registered source:** [R25](../../references/references.md#r25)
- **Released evaluation entry:** `pytracking/pytracking/experiments/myexperiments_gotjepa.py` selects tracker `tomp`, parameter set `got_jepa_378`, and the AVIST dataset by default (`myexperiments_gotjepa.py:11-21`).
- **Released inference parameter set:** `pytracking/pytracking/parameter/tomp/got_jepa_378.py` loads `GOT_JEPA_378.tar` (`got_jepa_378.py:11-76`).

**RESOURCE AVAILABILITY FACT:** the pinned repository supplies the 378 experiment, parameter file, three-stage training settings, tracker, model builders, and a component profiler. The main GOT-JEPA checkpoint and the CoTracker2 checkpoint are external and are not committed in the pinned tree.

**OPEN QUESTION — 252 variant:** repository-wide inspection found no GOT-JEPA 252 experiment, parameter file, training setting, or builder. Generic profiler mentions of `252` belong to other experiment names and do not establish a released GOT-JEPA-252 implementation.

**Repository checkout note:** the isolated Windows checkout reported deletions inside an unrelated `StreamVGGT` subtree because the multi-family repository contains paths that do not fully materialize cleanly on this filesystem. All GOT-JEPA paths cited here were present. This is a checkout-portability observation, not a GOT-JEPA model fact.

### B. Model construction

The deployed 378 builder is `tompnet50_PT` in `pytracking/ltr/models/tracking/tompnet_PT.py:537-626`.

| Element | Audited construction | Evidence |
|---|---|---|
| Input/crop | tracker sample size 432 from feature size 27 × stride 16; DINO input is resized to 378 | `got_jepa_378.py:11-18`; `tompnet_PT.py:382-390,537-556` |
| Semantic backbone | DINOv2 ViT-L/14 loaded through Torch Hub; width 1024; intermediate layers `[4,11,17,23]` are averaged | `tompnet_PT.py:382-390,537-556` |
| Feature adapter | `bkMlp` residual convolution path; output feature map pooled to 27×27 | `tompnet_PT.py:382-410,537-556` |
| Tracking head | ToMP filter predictor with six encoder and six decoder layers, model width 256, eight heads, FFN width 2048, filter size 1; linear classifier plus dense box regressor | `GOT_JEPA_378_PT.py:137-142`; `tompnet_PT.py:580-612` |
| JEPA deployment modules | `JEPA_predictor_cls` and `JEPA_predictor_breg` remain instantiated in the final PT network | `tompnet_PT.py:77-100,560-571,610-623` |
| Point/occlusion modules | CoTracker2, `SideNetwork_D`, `SideNetwork_U`, `PTrackAttentionModel`, `PointEmbeddingNetwork`, and `TFEcatmlp` | `tompnet_PT.py:77-100,322-376,556-623` |

**CODE FACT — inspected:** the final inference object contains a single deployed tracking head plus the two JEPA filter predictors and point-tracking/fusion modules. The frozen target/teacher head used by the pretraining builder is not separately instantiated in the final PT builder.

### C. Runtime graph

| Component | Execution frequency | Main input/output | Persistent state | Code evidence |
|---|---|---|---|---|
| CPU crop and normalization | every tracked frame | RGB frame and prior box → 432×432 search crop | previous box | `pytracking/pytracking/tracker/tomp/tomp.py:206-228` |
| DINOv2 feature extraction and `bkMlp` | every tracked frame | crop resized to 378 → 27×27, 256-channel head feature | none beyond current feature | `tomp.py:225-230,362-380`; `tompnet_PT.py:382-410` |
| ToMP filter prediction | every tracked frame | bounded training memory plus current feature → classification and box-regression filters | sample memory of size 2 | `tomp.py:362-380,580-643,851-907`; `got_jepa_378.py:21` |
| JEPA predictor path | every deployed tracking-head call | predicted filters → transformed classifier/box filters | model weights only | `tompnet_PT.py:77-100,499-507` |
| Base localization and direct box regression | every tracked frame | score and box maps → target state | previous state and localization flags | `tomp.py:366-430,519-746` |
| Eight-frame point buffer update | every eighth frame after the initial window | crop, score label, box → rolling buffers | fixed 8-frame tensors | `tomp.py:89-136,230-257,419-474` |
| CoTracker/OccuSolver branch | conditional: after the required history, on an eight-frame schedule, and only when buffer/visibility gates permit | eight-frame video and 128 queries → tracks and visibility | fixed buffers plus padded point/visibility state | `tomp.py:257-366`; `tompnet_PT.py:300-376` |
| Point-conditioned fusion and final prediction | when the CoTracker branch executes | visible last-frame points → Gaussian label, point embedding, attention/fusion → score and box maps | current point output | `tomp.py:323-370`; `tompnet_PT.py:376-507` |
| Tracking-memory admission | accepted localization and score gate | current feature/label/box → replacement in size-2 memory | bounded sample memory | `tomp.py:415-474,851-954` |

The effective inference path is therefore:

`frame → crop → DINOv2/feature adapter → ToMP dynamic filters → JEPA filter predictors → base score/box prediction → periodic OccuSolver/CoTracker visibility branch → optional point-conditioned score/box prediction → localization and bounded-memory update`.

### D. Temporal, memory, and template behavior

**CODE FACT — inspected:**

- `sample_memory_size=2`; `update_memory` replaces entries through learned sample weights rather than appending an unbounded feature history (`got_jepa_378.py:21`; `tomp.py:851-954`).
- OccuSolver allocates fixed tensors for eight images, eight score labels, and eight boxes. With `TrackS="Last"`, point/visibility outputs are padded to 15 temporal slots, but those tensors remain fixed-size (`tomp.py:89-136,334-357`).
- The buffers advance every `frames_step=8`; the point branch is not invoked on every frame (`got_jepa_378.py:57-64`; `tomp.py:230-366`).
- CoTracker queries total 128 points: 64 are sampled from the initial box at time 0 and 64 from the midpoint box at time 4; previously visible points can replace the first 64 (`tomp.py:257-323`).
- The CoTracker model is configured for an eight-frame window and four refinement iterations. The call supplies explicit queries, so a nominal support-grid setting is not the active query source (`pytracking/ltr/cotracker2/cotracker/models/core/cotracker/cotracker.py`; `tompnet_PT.py:300-376`).
- Visibility is reduced to a last-frame visible-point ratio with `.item()`, then used by the tracker to gate later update behavior (`tomp.py:317-366,419-474`).
- No list or tensor in the inspected GOT-JEPA tracker grows with total sequence length. Box state, size-2 feature memory, eight-frame image/label/box buffers, and padded point state are bounded.

**OPEN QUESTION:** the effect of visibility-gated memory suppression after a tracking error is not established by code inspection.

### E. Dynamic computation and online adaptation

- **CODE FACT — inspected:** online adaptation is dynamic filter/model prediction. The ToMP head predicts classification and box-regression filters from the bounded training samples and current search feature; the JEPA modules transform those filters before prediction (`tomp.py:580-643`; `tompnet_PT.py:499-507`).
- **CODE FACT — inspected:** the tracker updates feature/label/box memory but performs no `optimizer.step()`, backward pass, or deployed parameter update. Legacy `net_opt_iter`, `net_opt_update_iter`, and `net_opt_hn_iter` parameters remain in the parameter file, but no optimizer loop consumes them in the audited GOT-JEPA tracker (`got_jepa_378.py:28-30`; `tomp.py`).
- **CODE FACT — inspected:** the pretraining-only student/teacher boundary uses a corrupted/relocated context branch and a frozen clean-feature target branch. The final PT inference builder retains the student/head and JEPA predictors but not a separate target teacher (`tompnet_JEPA.py:256-276`; `tompnet_PT.py:537-626`).
- **CODE FACT — inspected:** the clean/corrupted view construction and target-head supervision belong to training, not the deployed tracker loop.
- **CODE FACT — inspected:** no AlphaEdit covariance/SVD/projector path from the separate GOT-Edit family appears in `tomp.py` or the GOT-JEPA final builder.

### F. Training evidence

All three released stages construct LaSOT, GOT10K-vottrain, TrackingNet, and COCO sequence datasets with equal sampling weights; GOT10K-votval supplies validation (`GOT_JEPA_378_{pretrain,finetune,PT}.py`).

| Stage | Frames and sampling | Batch/process declaration | Epochs | Initialization and trainable boundary | Optimizer/schedule |
|---|---|---:|---:|---|---|
| 378 pretrain | 2 train + 1 test; max gap 200; 200,000 train samples/epoch | 56; `multi_gpu=True` | 40 | initializes from external ToMP-L checkpoint; DINO/`bkMlp`/target head frozen; context head, JEPA predictors, and VICReg path trained | AdamW; context/VICReg 1e-4, predictors 1e-3, weight decay 1e-4; milestones 25/35 |
| 378 finetune | 2 train + 1 test; max gap 200; 200,000 train samples/epoch | 56; `multi_gpu=True` | 75 | initializes from external GOT-JEPA-pretrain checkpoint; DINO frozen; head, `bkMlp`, and JEPA predictors trained | AdamW; head/`bkMlp` 1e-4, predictors 2e-4; milestones 30/50/65 |
| 378 PT | 16 train + 8 test; max gap 1; 100,000 train samples/epoch | 52; `multi_gpu=True` | 60 | initializes from external finetune checkpoint; prior tracking modules and CoTracker frozen; side networks, point embedding/attention, and fusion modules trained | AdamW at 1e-4 for newly trained groups; milestone 50 |

Evidence: `GOT_JEPA_378_pretrain.py:19-57,60-179`; `GOT_JEPA_378_finetune.py:20-58,61-174`; `GOT_JEPA_378_PT.py:18-54,67-204`.

- **CODE FACT — inspected:** `LTRTrainer` supports a scaler but these settings do not enable AMP/BF16. No activation checkpointing or gradient accumulation is configured for the three released stages.
- **RESOURCE AVAILABILITY FACT:** `run_training_dsA.py` supplies distributed launch behavior, and the README presents eight-device pretrain/finetune commands and a four-device PT command.
- **OPEN QUESTION — effective batch semantics:** the launcher sets visible devices and spawns distributed workers while the settings also use the project `MultiGPU`/DataParallel wrapper and declare batch 56/52. A clean run was not performed, so the effective per-process/global batch and double-wrapping behavior are not established here.

### G. Profiling, export, and dependency evidence

- **RESOURCE AVAILABILITY FACT:** `pytracking/ltr/profiling/profile_tomp_components_PT.py` contains THOP component calls for the feature extractor, tracking-head parts, `bkMlp`, side networks, and CoTracker.
- **CODE FACT — inspected:** no import or invocation of that profiler was found in the released GOT-JEPA evaluation/training entrypoints. It omits `PTrackAttentionModel`, `TFEcatmlp`, the point-label path, JEPA predictors, tracker scheduling, preprocessing, memory management, and host synchronization. Its commented totals are not end-to-end latency or memory measurements.
- **CODE FACT — inspected:** the general repository profiler is wired to VGGT/GOT-Edit settings rather than the GOT-JEPA release and cannot be relabeled as a GOT-JEPA profiler.
- **RESOURCE AVAILABILITY FACT:** no GOT-JEPA end-to-end ONNX, TensorRT/Torch-TensorRT, TorchScript, or `torch.compile` exporter was found.
- **CODE FACT — inspected:** DINOv2 is loaded through Torch Hub without a revision pin. The main model and CoTracker2 weights are external, and the expected CoTracker2 checkpoint is absent from the Git tree.
- **CODE FACT — inspected:** the tracker uses hard CUDA placement, Python lists and conditionals, `.item()`/`.tolist()` host synchronization, and variable control flow around OccuSolver. No GOT-JEPA-specific custom CUDA kernel was identified; unrelated extensions elsewhere in the multi-family repository are not attributed to GOT-JEPA.

### H. HG4 evidence package — no decision

Evidence relevant to a single RTX 3060 12 GB:

- three sequential training stages and their declared datasets, batches, frame counts, frozen groups, and optimizers are present;
- DINOv2-L, ToMP, JEPA, and the point-tracking/fusion stack are jointly resident in the final PT stage;
- the PT stage unrolls 16 train and 8 test frames with declared batch 52 and documents a four-device launch;
- no verified single-GPU batch, gradient-accumulation recipe, peak-memory trace, or RTX 3060 reproduction is supplied;
- the distributed launcher/batch interpretation and external-checkpoint bootstrap remain unresolved.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

Structural evidence relevant to Jetson Nano:

- a DINOv2 ViT-L/14 semantic pass and ToMP filter prediction execute every frame;
- CoTracker2 and multiple point-fusion modules execute periodically over an eight-frame window;
- tracker state is bounded, but the implementation uses CUDA-specific placement and host-controlled periodic branches;
- Torch Hub and two external checkpoint dependencies are not revision/checksum pinned by the release;
- no complete exporter, TensorRT engine, operator-parity test, Jetson wrapper, Nano latency, memory, power, or thermal evidence was found.

**HG5 = PENDING**

### J. Code-visible cost sites

| Label | Site |
|---|---|
| CODE FACT — inspected | DINOv2 ViT-L/14 feature extraction and `bkMlp` execute on every frame |
| CODE FACT — inspected | ToMP filter prediction, JEPA filter transforms, classification, and box regression execute on every frame |
| CODE FACT — inspected | CoTracker2 and point-conditioned fusion execute conditionally on the eight-frame schedule, not every frame |
| CODE FACT — inspected | CoTracker uses 128 queries over an eight-frame window with four refinement iterations |
| CODE FACT — inspected | `.item()`, `.cpu()`, visualization/debug-capable branches, and Python gating cross the tensor/host boundary |
| ENGINEERING TARGET TO PROFILE | synchronized steady-state frame latency versus OccuSolver frames |
| ENGINEERING TARGET TO PROFILE | peak/steady memory for DINO, ToMP memory, CoTracker window, and PT fusion separately |
| ENGINEERING TARGET TO PROFILE | fixed-signature export boundary and precision/operator parity for the neural subgraphs |

### K. Unresolved items

1. GOT-JEPA-252 implementation/config/checkpoint: **NOT FOUND IN PINNED RELEASE**.
2. Clean bootstrap and checksum/provenance of `GOT_JEPA_378.tar` and `cotracker2.pth`: **PENDING**.
3. Effective distributed batch semantics for the three released training stages: **PENDING**.
4. Complete end-to-end profiler including OccuSolver scheduling and host work: **NOT FOUND**.
5. ONNX/TensorRT/TorchScript export and numerical parity: **PENDING**.
6. Effect of reusing one tracker object across sequence reinitialization: **OPEN QUESTION**.

## 4. CX020 — SAMURAI

### A. Provenance and audited variants

- **Repository:** `yangchris11/samurai`
- **Pinned ref:** `76ba195984892b0d1e3db5d9c9f90bb62175680a`
- **Registered source:** [R28](../../references/references.md#r28)
- **Released family:** SAM 2.1 Hiera Tiny, Small, Base+, and Large configurations under `sam2/sam2/configs/samurai/`.

The release has more than one script default:

| Entry | Default | Evidence |
|---|---|---|
| `scripts/main_inference.py` | SAM 2.1 Hiera Base+ and `sam2.1_hiera_base_plus.pt` | `main_inference.py:34-41` |
| `scripts/demo.py` | Base+ checkpoint by default; config selected from checkpoint name | `demo.py:24-44,114-121` |
| `scripts/main_inference_chunk.py` | tracker `samurai`; model argument defaults to Large | `main_inference_chunk.py:37-50,120-140` |

**OPEN QUESTION — benchmark variant identity:** the pinned scripts do not establish that every released result used one universal default. A result-to-script/config/checkpoint mapping is required before assigning a raw benchmark result to Base+ or Large.

**RESOURCE AVAILABILITY FACT:** checkpoint download support points to the official SAM 2.1 Tiny/Small/Base+/Large weights. There is no separate SAMURAI-trained checkpoint in the release.

### B. Model construction

| Variant | Hiera construction | Common deployed stack | Evidence |
|---|---|---|---|
| Base+ | input 1024; initial width 112; stages `[2,3,16,3]`; final width 896 | 256-dimensional FPN/memory path, four-layer memory attention, two-layer memory encoder, SAM prompt/mask decoder | `sam2/sam2/configs/samurai/sam2.1_hiera_b+.yaml` |
| Large | input 1024; initial width 144; stages `[2,6,36,4]`; final width 1152 | same 256-dimensional memory/mask stack | `sam2/sam2/configs/samurai/sam2.1_hiera_l.yaml` |
| Tiny/Small | released SAM 2.1 Hiera configs; initial width 96; depths 12/16 respectively | same tracker-level SAMURAI motion/memory logic | `sam2/sam2/configs/samurai/sam2.1_hiera_{t,s}.yaml` |

The SAMURAI modification lives inside the SAM 2 video model/predictor rather than in a new standalone backbone. The mask decoder produces three candidate masks in tracking mode, after which the SAMURAI branch selects with predicted-mask IoU alone during stabilization or with a Kalman/SAM weighted score after stabilization (`sam2/sam2/modeling/sam2_base.py:301-532`).

### C. Runtime graph

| Component | Execution frequency | Main input/output | Persistent state | Code evidence |
|---|---|---|---|---|
| Video/frame loading | once at `init_state` | frame folder/video → indexed image container and known frame count | all source frames or enumerated paths | `sam2_video_predictor.py:44-110` |
| Image encoder | once per newly requested sequential frame | 1024-preprocessed frame → multi-scale vision features | one-frame `cached_features` dictionary | `sam2_video_predictor.py:879-900` |
| Memory selection and attention | every tracked frame after initialization | current features + selected mask memories/object pointers → memory-conditioned pixel feature | conditioning/non-conditioning output dictionaries | `sam2_base.py:620-819` |
| Prompt/mask decoder | every tracked frame | conditioned feature and prompt state → three tracking masks, predicted IoUs, object score | current-frame tensors | `sam2_base.py:301-419` |
| Kalman/mask selection | every non-initial multi-mask tracking frame | three mask boxes + predicted IoUs → selected mask | 8-D mean, 8×8 covariance, stable-frame count | `sam2_base.py:419-532`; `utils/kalman_filter.py:26-225` |
| Memory encoder | every newly propagated frame | selected mask + current image feature → compact memory feature and object pointer | current compact output | `sam2_base.py:826-867,908-1017` |
| Output registration | every tracked frame | compact current output → dictionaries keyed by frame index | history dictionaries | `sam2_video_predictor.py:673-774` |

**CODE FACT — inspected:** the image encoder is not run separately for each of the three mask candidates. `_get_image_feature` caches the most recently requested frame and all candidates share that frame feature.

### D. Temporal, memory, template, and streaming behavior

- The SAMURAI configs set `num_maskmem=7`: one conditioning slot plus up to six non-conditioning mask memories in the normal single-object case. Object pointers are capped at 16 in memory attention (`sam2_base.py:30-71,636-795`).
- The modified memory-quality path admits a prior non-conditioning output when predicted mask IoU is above 0.5, object score is above 0, and a present Kalman score is above 0. The immediately previous frame remains eligible independently of that scan (`sam2_base.py:647-717`).
- Active memory attention is bounded by `num_maskmem` and the object-pointer cap. However, `output_dict` and per-object dictionaries retain a compact output for every propagated frame; no normal sequential eviction was found. This history therefore grows with sequence length (`sam2_video_predictor.py:91-104,673-774`).
- `main_inference.py` and `main_inference_chunk.py` use `offload_state_to_cpu=True`, so their growing compact history is CPU-resident. `demo.py` uses the predictor default and does not request that offload (`main_inference.py:67-77`; `main_inference_chunk.py:75-81`; `demo.py:43-60`).
- `init_state` calls `load_video_frames`, establishes `num_frames`, and preloads or enumerates the complete source. Even asynchronous folder loading still requires the folder and its full frame index. The released API is therefore an offline indexed-video interface, not a live append-one-camera-frame interface (`sam2_video_predictor.py:44-110`).
- `reset_state` clears inference dictionaries but does not reset the model-level Kalman mean/covariance/stable-frame attributes. The scripts construct a predictor per sequence; behavior when repeatedly reinitializing one predictor is an **OPEN QUESTION** (`sam2_video_predictor.py:848-879`; `sam2_base.py:202-218`).

### E. Dynamic computation and motion logic

- The Kalman state is `[x,y,a,h,vx,vy,va,vh]` with an 8-vector mean and 8×8 covariance (`utils/kalman_filter.py:26-85`).
- On the first tracked multi-mask frame, or after stability resets, selection uses the highest SAM-predicted IoU and initializes the Kalman state (`sam2_base.py:419-437`).
- Until 15 stable frames, Kalman prediction runs but mask selection still uses the highest SAM-predicted IoU; the state is updated only when that IoU exceeds 0.3, otherwise stability resets (`sam2_base.py:438-457`).
- After 15 stable frames, boxes are extracted for all three masks. Selection uses `kf_score_weight × KF-IoU + (1-kf_score_weight) × SAM-IoU`; Base+/Tiny/Small configs use 0.25 Kalman weight and Large uses 0.15. A selected SAM-IoU below 0.3 resets stability; otherwise Kalman update runs (`sam2_base.py:460-498`; SAMURAI YAMLs).
- Kalman work is Python/NumPy/SciPy-based, and the neural path crosses to host-visible values through `.item()` and CPU tensors.

### F. Training evidence

- **RESOURCE AVAILABILITY FACT:** the SAMURAI README presents the method as zero-shot/training-free on released SAM 2.1 weights.
- **CODE FACT — inspected:** no SAMURAI-specific optimizer, dataset recipe, training config, learned adapter, or family-specific checkpoint exists in the pinned release.
- **CODE FACT — inspected:** the repository vendors upstream SAM 2 training infrastructure and a SAM 2.1 MOSE finetuning config. Those files are not a released SAMURAI training recipe and are not attributed to this family audit.
- **OPEN QUESTION:** if a future trainable module were added around frozen SAM 2.1, dataset, batch, unroll length, optimizer, AMP, activation checkpointing, and single-GPU memory requirements are unspecified by the SAMURAI release.

### G. Profiling, export, and custom-operator evidence

- Scripts use CUDA device 0 and FP16 autocast. Scaled-dot-product attention can use Flash Attention on supported Ampere-or-newer devices and falls back to the math implementation otherwise.
- The build path enables `fill_hole_area=8`. `setup.py` defines a CUDA connected-components extension; import/build failure is caught by the utility path and hole filling can be skipped rather than proving the entire tracker impossible (`sam2/build_sam.py:121-122`; `sam2/setup.py:89-105`; `sam2/sam2/utils/misc.py`).
- `compile_image_encoder` exists but is false in the SAMURAI configurations; `torch.compile` is therefore not the released default (`sam2_base.py:99,223-232`; SAMURAI YAMLs).
- No SAMURAI end-to-end ONNX, TensorRT/Torch-TensorRT, TorchScript exporter, CUDA-Event profiler, or Jetson runtime was found.
- Python dictionaries keyed by frame, dynamic memory selection, NumPy/SciPy Kalman operations, per-candidate loops, `.item()` calls, and CPU mask/box construction remain outside a simple fixed-signature tensor graph.

### H. HG4 evidence package — no decision

SAMURAI itself has no training job to reproduce. If a new trainable module were introduced around a frozen host:

- the released host options range from Tiny to Large, all at 1024 input;
- host feature, mask-memory, and multi-frame state would coexist with the new trainable path;
- the release supplies no family-specific training batch, unroll, checkpointing, AMP, or one-GPU memory recipe;
- no RTX 3060 training measurement was run.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

Structural evidence relevant to Jetson Nano:

- Base+ is the main single-process default, while a separate multi-GPU script defaults to Large; the exact target variant must be fixed before profiling;
- 1024-resolution Hiera, memory attention, a mask decoder producing three candidates, memory encoding, and host-side Kalman selection form the per-frame path;
- the active attention window is bounded, but indexed video loading and retained output history are not a released live-camera streaming design;
- Flash Attention is not required because a math fallback exists, while connected-components hole filling is optional on extension failure;
- no target-device exporter, engine, parity test, sustained latency, memory, power, or thermal evidence exists.

**HG5 = PENDING**

### J. Code-visible cost sites

| Label | Site |
|---|---|
| CODE FACT — inspected | one Hiera image-encoder pass per newly requested frame, shared across all mask candidates |
| CODE FACT — inspected | memory attention, mask decoder, three-mask selection, and memory encoder execute on every tracked frame |
| CODE FACT — inspected | Kalman selection converts mask boxes/scores through host-side NumPy/SciPy logic |
| CODE FACT — inspected | active mask-memory attention is bounded, while compact output history grows with the number of propagated frames |
| ENGINEERING TARGET TO PROFILE | synchronized image encoder, memory attention, mask decoder, Kalman selection, and memory encoder latency separately |
| ENGINEERING TARGET TO PROFILE | Base+/Tiny/Small/Large peak memory and sustained sequence-length behavior under identical state-offload settings |
| ENGINEERING TARGET TO PROFILE | live-frame adapter boundary, end-to-end export partition, and operator/precision parity |

### K. Unresolved items

1. Exact script/config/checkpoint used for each released raw benchmark result: **PENDING**.
2. A released live-camera append-frame interface: **NOT FOUND**.
3. History-memory slope with and without state offload: **PENDING MEASUREMENT**.
4. Reinitializing the same predictor without explicitly resetting model-level Kalman state: **OPEN QUESTION**.
5. SAMURAI-specific training recipe/weights: **NOT FOUND; RELEASE IS TRAINING-FREE**.
6. End-to-end export, TensorRT support, and target-device parity: **PENDING**.

## 5. CX024 — DAM4SAM

### A. Provenance and audited variants

- **Repository:** `jovanavidenovic/DAM4SAM`
- **Pinned ref:** `9c954504b39ebca4c412f207be0787c26bfac85a`
- **Registered source:** [R30](../../references/references.md#r30)
- **Default tracker:** `DAM4SAMTracker(tracker_name="sam21pp-L")` (`dam4sam_tracker.py:28-50`).
- **Default host:** SAM 2.1 Hiera Large, checkpoint `checkpoints/sam2.1_hiera_large.pt`, config `sam21pp_hiera_l.yaml` (`utils/utils.py:27-40`).

**RESOURCE AVAILABILITY FACT:** the repository supplies SAM 2/SAM 2.1 Tiny, Small, Base+, and Large configuration mappings. The default SAM 2.1 Large checkpoint is external and is not committed.

**Repository anomaly:** `determine_tracker` places SAM 2.1 Large/Base+ under `checkpoints/`, but Small/Tiny paths omit that directory; classic SAM 2 paths also require weights not enabled by the current download path (`utils/utils.py:27-52`). Non-default clean bootstrap remains an **OPEN QUESTION**.

### B. Model construction

The default configuration uses:

- SAM 2.1 Hiera Large, input 1024, initial width 144, stages `[2,6,36,4]`, and final width 1152;
- the 256-dimensional SAM 2.1 feature pyramid, prompt/mask decoder, four-layer memory attention, and two-layer memory encoder;
- `num_maskmem=7`, memory stride 5, and at most four conditioning frames in attention;
- tracking multi-mask output with three candidates.

Evidence: `sam2/sam21pp_hiera_l.yaml:8-125`; `sam2/modeling/sam2_base.py`.

The code does not define separate Python classes named “DAM”, “RAM”, or “introspection module.” The released mapping is:

- **DRM terminology in code:** conditioning-frame outputs; `add_to_drm` promotes a frame to `cond_frame_outputs` (`sam2/sam2_video_predictor.py:328-352`).
- **RAM terminology in config/code comments:** sampled non-conditioning outputs selected with temporal stride 5 (`sam21pp_hiera_l.yaml:123`; `sam2/modeling/sam2_base.py:531-617`).
- **Distractor/introspection logic:** inline Python logic in `DAM4SAMTracker.track`, not a separately named neural module (`dam4sam_tracker.py:178-266`).

### C. Runtime graph

| Component | Execution frequency | Main input/output | Persistent state | Code evidence |
|---|---|---|---|---|
| Incremental frame insertion | every call | one RGB frame → current indexed image tensor | frame index/count only; current image removed after tracking | `dam4sam_tracker.py:62-142,178-199` |
| Image encoder | once for each new frame | current 1024 frame → Hiera feature pyramid | one-frame feature cache | `sam2_video_predictor.py:975-990` |
| Memory selection/attention | every tracked frame | current features + selected DRM/RAM memories/object pointers → conditioned feature | output dictionaries | `sam2/modeling/sam2_base.py:531-708` |
| Mask decoder | every tracked frame | conditioned feature → three masks and predicted IoUs | current outputs | `sam2/modeling/sam2_base.py`; `dam4sam_tracker.py:198-214` |
| DAM distractor test | on frames passing quality/size/spacing pre-gates | two alternative masks → CPU connected components and box IoUs | object-size history and last DRM frame | `dam4sam_tracker.py:216-257`; `utils/utils.py:8-24` |
| DRM promotion | only when an alternative test has box IoU ≤ 0.7 | current compact output → conditioning frame | growing `cond_frame_outputs` dictionary | `dam4sam_tracker.py:249-260`; `sam2_video_predictor.py:328-352` |
| Memory encoder | every propagated new frame; repeated when a promoted temporary conditioning output is consolidated | selected mask + image feature → compact memory | current/retained output | `sam2_video_predictor.py:609-639,1085-1105` |
| Output storage | every tracked frame | compact output → non-conditioning or conditioning dictionary | frame-keyed histories | `sam2_video_predictor.py:675-790` |

**CODE FACT — inspected:** `init_state_tw` begins with an empty video state. `track` inserts only the current preprocessed frame, calls `propagate_in_video(..., max_frame_num_to_track=0)` for that frame, and removes the current image afterward. This is a frame-by-frame interface and differs from SAMURAI's released whole-folder initialization (`dam4sam_tracker.py:62-142,178-205`).

### D. Temporal and memory behavior

| Memory/state | Stored content | Active cap and selection | Stored-history behavior |
|---|---|---|---|
| DRM / conditioning outputs | compact SAM output for admitted frames, including mask memory and object pointer | up to four closest conditioning frames enter attention | no normal eviction found; dictionary can grow with admitted frames |
| RAM / non-conditioning outputs | compact output for ordinary tracked frames | fills the remaining slots up to total `num_maskmem=7`; stride 5 plus immediate recent frame; empty masks skipped | ordinary outputs remain keyed by frame; no normal sequential eviction found |
| Object pointers | compact per-frame object pointer | up to 16 visible past pointers | active cap fixed; source dictionaries can grow |
| Object-size history | one pixel count per frame | calculation looks at recent windows (up to 300, then recent positive sizes) | Python list grows with sequence length |
| Image-feature cache | current frame feature | one frame | replaced on the next frame |

Evidence: `dam4sam_tracker.py:137-138,216-231`; `sam21pp_hiera_l.yaml:88-125`; `sam2/modeling/sam2_base.py:531-708`; `sam2_video_predictor.py:97-115,675-790,975-990`.

**CODE FACT — inspected:** active attention is bounded, while the stored DRM/RAM dictionaries and `object_sizes` list are not capped by the normal incremental tracking loop. With the default `offload_state_to_cpu=False`, compact output history remains device-resident.

### E. Dynamic computation and distractor logic

1. The SAM decoder returns three masks; the wrapper selects the highest predicted-IoU mask and retains the other two as alternatives (`dam4sam_tracker.py:198-214`).
2. The distractor test proceeds only when selected predicted IoU is above 0.8, current size divided by the recent positive-size median is within `[0.8,1.2]`, the selected mask has at least one pixel, and more than five frames have passed since the last DRM admission (`dam4sam_tracker.py:216-231`).
3. Each alternative is converted to CPU/VOT mask form, subtracts overlap with the selected mask, retains its largest connected component, is unioned back with the selected mask, and is converted to a rectangle (`dam4sam_tracker.py:232-248`; `utils/utils.py:8-24`).
4. The selected rectangle and alternative-union rectangles are compared. If any box IoU is at most 0.7, the current frame is promoted to DRM (`dam4sam_tracker.py:249-260`).
5. No direct object-score threshold is applied by this wrapper. Object disappearance can affect the host-selected mask, but no separate DAM recovery/re-detection branch was found.

The cost boundary is explicit:

- **HOST SAM 2.1 cost:** image encoder, memory selection/attention, prompt/mask decoder, memory encoder, and base output storage.
- **DAM-specific incremental cost:** returning/copying all three masks, selected/alternative mask conversion, CPU connected-components and rectangle-IoU gates, object-size bookkeeping, and occasional DRM promotion/consolidation.

### F. Training and initialization evidence

- **RESOURCE AVAILABILITY FACT:** DAM4SAM is released as training-free; no DAM-specific optimizer, dataset recipe, learned module, or checkpoint was found.
- The repository includes upstream SAM 2 training files, but they are not a DAM4SAM family-specific training recipe.
- The box-dataset benchmark path requests downloaded precomputed SAM 2 initialization masks, converts each mask to a box for reporting, and initializes from the mask (`run_on_box_dataset.py:27-56`).
- The direct bbox example passes the first RGB frame and box. The tracker runs the image feature and prompt/mask decoder to obtain the initial mask (`run_bbox_example.py:47-54`; `dam4sam_tracker.py:269-338`).
- VOT/DiDi integration accepts an externally supplied first-frame mask. These initialization paths are not interchangeable evidence and are kept separate.

**RESOURCE AVAILABILITY FACT — EfficientTAM/EdgeTAM:** runnable EfficientTAM or EdgeTAM integration, configs, and checkpoints were **NOT FOUND IN PINNED RELEASE**. Paper-level host compatibility is not promoted to code fact here.

### G. Profiling, export, and dependency evidence

- The host inherits SAM 2's optional CUDA connected-components extension for hole filling. DAM's distractor test separately uses CPU OpenCV connected components (`setup.py:89-105`; `utils/utils.py:18-24`).
- Scaled-dot-product/Flash-attention paths and a math fallback are inherited from SAM 2. `triton==2.1.0` appears as a dependency, but no DAM-specific Triton kernel was found.
- `compile_image_encoder` is false in the released DAM4SAM configs; the available `torch.compile` hook is inactive by default (`sam21pp_hiera_l.yaml:120`; `sam2/modeling/sam2_base.py:180-192`).
- No end-to-end DAM4SAM ONNX, TensorRT/Torch-TensorRT, TorchScript exporter, CUDA-Event profiler, or Jetson runtime was found.
- Hard CUDA placement, frame-keyed dictionaries, dynamic Python list/state operations, CPU VOT/NumPy/OpenCV conversion, and conditional DRM admission remain outside a single static tensor graph.

### H. HG4 evidence package — no decision

DAM4SAM itself has no released training task. If a new trainable module were added:

- the default host is SAM 2.1 Hiera Large at 1024 input;
- no frozen-host training recipe, batch, temporal unroll, optimizer, AMP, activation-checkpointing, or gradient-accumulation setting is released for DAM4SAM;
- no RTX 3060 memory/run evidence was generated.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

Structural evidence relevant to Jetson Nano:

- the default host is the Large SAM 2.1 configuration, while lighter host integrations reported elsewhere are absent from the pinned release;
- the released wrapper supports incremental frames, but default device-resident compact histories grow with sequence length;
- per-frame host cost and conditional CPU distractor logic must be measured separately;
- optional custom connected-components code is not the only boundary: dynamic dictionaries, host conversions, and the 1024-resolution host graph also require export/runtime treatment;
- no target-device engine, operator parity, latency, memory, power, or sustained-thermal evidence exists.

**HG5 = PENDING**

### J. Code-visible cost sites

| Label | Site |
|---|---|
| CODE FACT — inspected | default host performs Hiera-L image encoding, memory attention, three-mask decoding, and memory encoding per frame |
| CODE FACT — inspected | DAM-specific logic copies two alternative masks to CPU and performs connected-components and rectangle IoUs only after pre-gates pass |
| CODE FACT — inspected | DRM admission can trigger conditioning-output consolidation and memory encoding using the cached current image feature |
| CODE FACT — inspected | active memory attention is capped but compact output dictionaries and object-size history grow with video length |
| ENGINEERING TARGET TO PROFILE | host SAM 2.1 latency versus DAM-only incremental latency with admission rate reported separately |
| ENGINEERING TARGET TO PROFILE | device-memory slope over long sequences and effect of safe state offload/eviction policies without changing semantics |
| ENGINEERING TARGET TO PROFILE | fixed-signature export partition, mask-transfer cost, operator support, and precision parity |

### K. Unresolved items

1. EfficientTAM/EdgeTAM runnable integration: **NOT FOUND IN PINNED RELEASE**.
2. Non-default Small/Tiny/classic-SAM checkpoint path consistency and clean bootstrap: **PENDING**.
3. End-to-end profiler and measured separation of host versus DAM-only work: **NOT FOUND**.
4. Long-sequence device-memory slope: **PENDING MEASUREMENT**.
5. Explicit recovery/re-detection branch beyond host mask prediction and memory selection: **NOT FOUND**.
6. ONNX/TensorRT/TorchScript export and numerical parity: **PENDING**.

## 6. CX037 — SSTrack-AAAI

### A. Provenance and audited variants

- **Repository:** `GXNU-ZhongLab/SSTrack`
- **Pinned ref:** `5dcf04ccb04f10ca4d78035373c8b8684bb8c4f5`
- **Registered source:** [R32](../../references/references.md#r32)
- **Audited configs:** `dropmae_256_150ep.yaml`, `dropmae_384_150ep.yaml`, `dropmae_256_got_60ep.yaml`, and `dropmae_384_got_60ep.yaml` under `experiments/sstrack/`.

**RESOURCE AVAILABILITY FACT:** model checkpoints and the DropMAE initialization are external; the tracker expects `checkpoints/train/sstrack/<config>/SSTrack_ep%04d.pth.tar` (`lib/test/parameter/sstrack.py`; README).

### B. Model construction

All four configs select `vit_base_dropmae_ce`; `build_sstrack` maps that type to the DropMAE ViT and a center head (`lib/models/sstrack/sstrack.py:291-348`).

| Element | B256 | B384 | Evidence |
|---|---:|---:|---|
| Template/search input | 128 / 256 | 192 / 384 | experiment YAMLs |
| Patch/token size | 16 | 16 | `vit_dropmae.py:31-104,260-266` |
| Tokens per raw template | 64 | 144 | input divided by patch size |
| Search tokens before CE | 256 | 576 | input divided by patch size |
| Backbone | ViT-B, width 768, depth 12, 12 heads | same | `vit_dropmae.py:31-104,260-266` |
| Candidate-elimination blocks | zero-based blocks 3, 6, 9; keep ratio 0.7 each | same | experiment YAMLs; `vit_dropmae.py:86-97` |
| Head | center head with 256 branch channels | same | `sstrack.py:324-348` |
| Persistent query | one detached 768-D token | same | `sstrack.py:67,239-249` |

**CODE FACT — inspected:** candidate elimination physically reduces the search-token sequence after attention through sort/gather/concatenation, then the model scatters zeros back to the full search grid for the prediction head (`attn_blocks.py:9-75,95-116`; `vit_dropmae.py:172-224`). At configured 0.7 keep ratios, the search sequence is approximately 256→180→126→89 for B256 and 576→404→283→199 for B384 before restoration.

### C. Runtime graph

| Component | Execution frequency | Main input/output | Persistent state | Code evidence |
|---|---|---|---|---|
| CPU crop/preprocess | initialization and every frame | image/box → template or search tensor | predicted box | `lib/test/tracker/sstrack.py:60-102` |
| Active template selection | every frame | raw template-history list → selected template list/masks | full raw history | `sstrack.py:94-102,169-198` |
| Patch embedding | every frame | all selected raw templates and current search → tokens | no encoded-template cache | `vit_dropmae.py:105-156` |
| ViT + three CE stages | every frame | template/search/query tokens → reduced/restored feature sequence | previous one-token query | `vit_dropmae.py:172-224`; `sstrack.py:225-252` |
| Center head | every frame | restored search grid → score/size/offset maps | none beyond current features | `sstrack.py:255-286` |
| Box decode and Hann selection | every frame | prediction maps → box/confidence | current box | `lib/test/tracker/sstrack.py:102-117` |
| History append | every frame when multi-template mode is enabled | predicted crop/mask → raw history lists | sequence-length history | `lib/test/tracker/sstrack.py:119-130` |

The standard configs set `TEST.TEMPLATE_NUMBER=3` and GOT variants set 4. The selector keeps the initial template and samples segment midpoints from subsequent history, so the later active list can contain four/five templates respectively; early frames can supply fewer (`lib/test/tracker/sstrack.py:169-198`). Each selected raw template is patch-embedded again on every frame.

### D. Temporal, memory, template, and training-only behavior

- The initial raw template is retained. A new predicted template is appended every frame in multi-template mode; there is no confidence gate for admission (`lib/test/tracker/sstrack.py:60-78,119-130`).
- Histories are not truncated. The first 1,000 appended template tensors remain on CUDA; after `TEST.MEMORY_THRESHOLD=1000`, new history tensors are stored on CPU and selected entries are moved back to CUDA (`lib/test/tracker/sstrack.py:119-130,169-198`). Stored raw history therefore grows with sequence length even though the active set is small.
- The backbone has no encoded-template cache. Raw selected templates are stacked and patch-embedded every frame (`vit_dropmae.py:105-156`).
- `track_query` is one detached token overwritten on every forward and reused on the next frame (`sstrack.py:67,239-249`). `initialize` does not reset it; normal evaluation constructs a new tracker per sequence, while repeated initialization of one tracker instance is an **OPEN QUESTION**.
- Global-spatial localization, local-temporal association, template-processing/multi-view branches, and optional instance-contrastive loss are reached only through `train_forward` when `training=True`. They are **TRAINING-ONLY** and are not executed by the tracker call (`sstrack.py:90-220`).
- The final tracker is not an unchanged dense ODTrack/ViT runtime: candidate elimination, the persistent tracking query, and multi-template selection remain active at inference.

### E. Dynamic computation

- Candidate elimination runs after attention at blocks 3/6/9. It sorts attention scores, gathers retained search tokens, shortens later transformer inputs, records removed indices, and later restores the full spatial ordering with zeros (`attn_blocks.py:9-75`; `vit_dropmae.py:172-224`).
- Template tokens are not candidate-eliminated. Compute changes with B256/B384 and with the number of selected templates/history maturity.
- Search tokens are multiplied/modulated using the current tracking-query attention before the center head; the new query becomes detached persistent state (`sstrack.py:225-252`).
- Tracker code uses hard `.cuda()`, Python list selection, `.tolist()` box transfer, and CPU↔GPU moves for late history entries.

### F. Training evidence

| Field | 150-epoch B256/B384 | GOT-only B256/B384 | Evidence |
|---|---|---|---|
| Training datasets | LaSOT, GOT10K-vottrain, COCO17, TrackingNet, equal ratios | GOT10K full only | experiment YAMLs |
| Samples/epoch | 10,000 | 10,000 | YAMLs |
| Validation | GOT10K-votval, 2,000/epoch | GOT10K validation, 2,000/epoch | YAMLs |
| Training views | 1 template, 3 search, 2 grounding views | configured release setting | YAMLs |
| Batch/process | B256 32; B384 8 | B256 16; B384 8 | YAMLs |
| Epochs / LR drop | 150 / 120 | 60 / 40 | YAMLs |
| Optimizer | AdamW, LR 2.5e-4, weight decay 1e-4, backbone multiplier 0.1, clip 0.1 | same family defaults | YAMLs; `lib/train/base_functions.py` |
| CE schedule | start 20, warm 80 | start 20, warm 40 | YAMLs |
| Initialization | `dropmae_k700_800E.pth` | same | YAMLs |
| AMP | false | false | YAMLs |

The README launches two processes. Its nominal aggregate batches are therefore 64/16 for the 150-epoch B256/B384 configs and 32/16 for the GOT B256/B384 configs. This arithmetic does not establish measured memory or successful reproduction.

- No explicit frozen-module setting or consumed activation-checkpoint option was found in the released SSTrack path.
- A single-process training CLI path exists, but no measured one-GPU batch/peak-memory recipe is provided.
- **CODE FACT — inspected:** sampler/processing/actor code consumes bounding boxes: boxes drive crops and synthetic copy-paste; template boxes create CE masks; grounding views receive direct box/focal supervision; search ground truth participates in preprocessing and IoU reporting (`lib/train/data/sampler.py`; `processing.py`; `actors/sstrack.py`). The code inspection does not establish a fully annotation-free released recipe merely from the self-supervised mechanism name.

### G. Profiling and export evidence

- `tracking/profile_model.py` defaults to script `augtrack` while argparse choices contain only `odtrack`; the later builder branch handles `build_augtrack`, not `build_sstrack` (`profile_model.py:21-24,132-145`). The README command using `--script sstrack` is rejected by this parser. The script is therefore stale/mismatched for the pinned SSTrack builder.
- No validated current SSTrack FLOP/parameter result can be registered from that profiler.
- No end-to-end SSTrack ONNX, TensorRT/Torch-TensorRT, or TorchScript exporter was found. A generic unused ONNX-oriented preprocessor helper does not export this tracker.
- The neural graph contains dynamic template lists/counts and CE sort/gather/scatter. Tracker logic contains Python history selection, hard `.cuda()`, `.tolist()`, and conditional CPU↔GPU transfers.
- No SSTrack-specific custom CUDA kernel was found; unrelated compiled code in vendored tracker dependencies is not attributed to SSTrack.

### H. HG4 evidence package — no decision

Evidence relevant to a single RTX 3060 12 GB:

- both resolutions have explicit datasets, batches, epochs, optimizer, CE schedule, and DropMAE initialization;
- the documented launch uses two processes, while a one-process launcher path exists;
- B384 increases per-template/search tokens from 144/576 versus 64/256 for B256;
- no consumed activation checkpointing, AMP, measured peak memory, or verified one-GPU recipe is supplied;
- external initialization/checkpoint bootstrap and actual reproduction were not tested.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

Structural evidence relevant to Jetson Nano:

- the deployed neural path is a 12-layer ViT-B with three candidate-elimination stages, a persistent token, multi-template re-encoding, and a center head;
- B384 has substantially more tokens than B256; candidate elimination reduces later search tokens but does not cache templates;
- raw history grows, the first 1,000 appended templates remain on CUDA, and later selected templates incur CPU→GPU transfer;
- the supplied profiler does not build SSTrack and no complete exporter/engine/parity result exists;
- no Nano latency, peak memory, power, or thermal evidence was produced.

**HG5 = PENDING**

### J. Code-visible cost sites

| Label | Site |
|---|---|
| CODE FACT — inspected | all selected raw templates and the search crop are patch-embedded on every frame |
| CODE FACT — inspected | CE performs full attention before sort/gather reduction at three layers, then scatters zeros to restore the search grid |
| CODE FACT — inspected | B256 search tokens reduce 256→180→126→89; B384 reduces 576→404→283→199 under configured keep ratios |
| CODE FACT — inspected | raw history admission occurs every frame without a confidence gate and history is not truncated |
| ENGINEERING TARGET TO PROFILE | synchronized patch embedding, each ViT/CE segment, query update, head, and host transfer separately |
| ENGINEERING TARGET TO PROFILE | B256 versus B384 and active-template count versus sequence age |
| ENGINEERING TARGET TO PROFILE | long-sequence CUDA/CPU history growth and CPU→GPU selected-template transfer |
| ENGINEERING TARGET TO PROFILE | CE export/operator parity and fixed maximum-template export boundary |

### K. Unresolved items

1. Correct current SSTrack FLOP/parameter profiler: **NOT FOUND; RELEASED SCRIPT IS MISMATCHED**.
2. Intended annotation-free versus bbox-consuming training recipe boundary: **OPEN QUESTION**.
3. Repeated `initialize` on one tracker and persistent `track_query`: **OPEN QUESTION**.
4. Long-sequence memory slope and cost of the 1,000-GPU-entry threshold: **PENDING MEASUREMENT**.
5. End-to-end ONNX/TensorRT/TorchScript export and numerical parity: **PENDING**.
6. Successful single-RTX-3060 and Jetson Nano reproduction: **NOT RUN**.

## 7. CX038 — MCITrack

### A. Provenance and audited variants

- **Repository:** `kangben258/MCITrack`
- **Pinned ref:** `e667193eaec4c8a73d4bdd856a662aecdb844b43`
- **Registered source:** [R34](../../references/references.md#r34)
- **Audited configs:** `mcitrack_b224.yaml`, `mcitrack_l384.yaml`, and their GOT-only variants.

**RESOURCE AVAILABILITY FACT:** pretrained Fast-iTPN weights and trained tracker checkpoints are external. The tracker expects `checkpoints/train/mcitrack/<config>/MCITRACK_ep%04d.pth.tar`.

### B. Model construction and variant mapping

| Element | MCITrack-B224 | MCITrack-L384 | Evidence |
|---|---|---|---|
| Config/backbone | `mcitrack_b224.yaml`; `fastitpnb` | `mcitrack_l384.yaml`; `fastitpnl` | YAMLs |
| Template/search | five 112² templates / one 224² search | five 192² templates / one 384² search | YAMLs |
| Tokens | 49 per template + 196 search = 441 combined | 144 per template + 576 search = 1,296 combined | `fastitpn.py:496-524,969-1031` |
| Fast-iTPN width/depth | width 512; stage depths 3 + merge, 3 + merge, 24 attention blocks; eight heads | width 768; stage depths 2 + merge, 2 + merge, 40 attention blocks; 12 heads | `fastitpn.py:661-914,1121-1151` |
| Interaction ranges | `[[8,14],[14,20],[20,26],[26,32]]` | `[[6,16],[16,26],[26,36],[36,46]]` | YAMLs |
| Mamba neck | four layers; `d_model=512`, `d_inner=1024`, `d_state=16` | four layers; `d_model=768`, `d_inner=1536`, `d_state=16` | YAMLs; `neck.py:118-148` |
| Head | center head, 256 channels | center head, 256 channels | YAMLs; `mcitrack.py:109-120` |
| Pretrain | `/pretrained/fast_itpn_base_clipl_e1600.pt` | `/pretrained/fast_itpn_large_1600e_1k.pt` | YAMLs |

The top-level builder creates an encoder, four-layer Mamba neck with interaction blocks, and center decoder (`lib/models/mcitrack/mcitrack.py:42-70,109-120`). No class named `CIF` exists in the implementation; the code realization of contextual fusion is `Mamba_Neck` plus `InteractionBlock`.

### C. Runtime graph

| Component | Execution frequency | Main input/output | Persistent state | Code evidence |
|---|---|---|---|---|
| CPU crop/preprocess | initialization and every frame | image/box → five-template list and one search crop | current box/template banks | `lib/test/tracker/mcitrack.py:67-100` |
| Fast-iTPN patch/stage-1/2 encoding | every frame | five raw templates + search + template boxes → combined tokens | no encoded-template cache | `fastitpn.py:969-1031` |
| Four Mamba residual blocks | every frame | search stream → context-updated search stream | four hidden tensors | `neck.py:138-167` |
| Four Injectors | every frame | combined Fast-iTPN tokens query search/context through MHA | current tokens | `neck.py:69-86,89-148` |
| Fast-iTPN stage-3 slices | every frame | combined token stream through four configured layer ranges | none across frames | `neck.py:89-148` |
| Six Extractors | every frame | search stream cross-attends to combined stream; final interaction has two extra extractors | current tokens | `neck.py:41-66,89-116` |
| Center decoder | every frame | final search feature → score/size/offset maps and confidence | none beyond current feature | `mcitrack.py:70-104`; tracker `:109-127` |
| Hidden-state update/reset | every frame | four new states retained; confidence below UPH replaces all with `None` | fixed four-state list | `lib/test/tracker/mcitrack.py:104-133` |
| Template-bank admission/refresh | confidence-controlled admission; periodic active-list refresh | predicted crop/box → bounded raw bank → five active templates | raw template/box bank | `lib/test/tracker/mcitrack.py:135-164` |

The actual contextual-fusion sequence per insertion is: Mamba update on the search stream, Injector cross-attention into the combined backbone stream, execution of the configured Fast-iTPN block slice, and Extractor cross-attention back into the search stream. The final insertion applies two additional Extractors (`neck.py:41-148`).

### D. Hidden state, temporal memory, and template policy

- Each of four Mamba layers carries one hidden tensor shaped `[B,L,d_inner,d_state]` (`neck.py:159-167,222-278`).
- B224 uses `[B,196,1024,16]`; at batch 1 FP32 this is approximately 12.25 MiB per layer and 49 MiB for four state payloads.
- L384 uses `[B,576,1536,16]`; at batch 1 FP32 this is approximately 54 MiB per layer and 216 MiB for four state payloads.
- These figures are tensor-payload arithmetic only; they exclude weights, activations, allocator overhead, templates, and host/runtime memory.
- A state is initialized with `torch.zeros(..., device=deltaA.device)` when `None`. The computation explicitly casts state parameters to FP32 and creates no lower-precision state override (`neck.py:248-278`).
- The previous hidden tensor participates in `h = deltaA * h + BX`; the new state replaces the old one on every frame. If confidence `.item()` is below the dataset-specific UPH threshold, all four entries become `None` for the next frame (`neck.py:268-278`; tracker `:130-133`). State size is fixed and does not grow with video length.
- Inference runs under `torch.no_grad()`, so retained states do not keep autograd graphs. In training, the actor processes two search frames through the state path without an explicit detach between them; this is a short configured unroll, not sequence-length growth.
- Initialization repeats the first template five times. Confidence above UPT admits a new raw GPU template; the bank is capped at dataset-specific `MB` values of 200–500 and pops the oldest entry. Every `INTER` frames, active slots 1–4 are refreshed at evenly spaced bank indices while slot 0 remains the initial template (`lib/test/tracker/mcitrack.py:67-89,135-164`; YAMLs).
- The encoder reprocesses all five raw templates every frame; there is no encoded-template cache.
- Nominal FP32 raw-image tensor payload at the maximum 500-template bank is about 72 MiB for 112² and 211 MiB for 192², excluding tensor/object/allocator overhead and stored template-box tensors.

### E. Dynamic computation and Mamba operators

- All four Mamba blocks, four Injectors, six Extractors, and four Fast-iTPN layer slices execute every frame; the runtime does not conditionally skip them on confidence (`neck.py:89-148`; tracker `:100-110`).
- The Mamba implementation uses ordinary PyTorch `Linear`, grouped depthwise `Conv1d`, SiLU, `exp`, elementwise products, and batched matrix multiplication (`neck.py:171-278`).
- No import or use of `mamba_ssm`, `selective_scan`, a causal-conv extension, Triton kernel, custom CUDA kernel, or fused RMSNorm/layernorm was found in the active MCITrack model.
- `GRAD_CKPT=True` wraps Mamba blocks, Fast-iTPN blocks, and Extractors. The wrapper has no `self.training` guard, so the configured checkpoint calls remain in the inference code path even under `no_grad`; Injectors are not checkpoint-wrapped (`neck.py:41-116,151-167`; `fastitpn.py:969-1031`).
- `.item()` for confidence and `.tolist()` for box output create per-frame host synchronization. Template-bank selection is Python-list logic.

### F. Training evidence

| Field | MCITrack-B224 | MCITrack-L384 | Evidence |
|---|---:|---:|---|
| Datasets | LaSOT, GOT10K-vottrain, COCO17, TrackingNet, VastTrack; equal ratios | same | YAMLs |
| Samples/epoch | 60,000 | 60,000 | YAMLs |
| Training frames | 5 templates + 2 search | same | YAMLs/training actor |
| Batch/process | 64 | 16 | YAMLs |
| Epochs / LR drop | 300 / 240 | 300 / 240 | YAMLs |
| Optimizer | AdamW, LR 4e-4, weight decay 1e-4, encoder multiplier 0.1, clip 0.1 | same | YAMLs; `lib/train/base_functions.py` |
| Activation checkpointing | configured true | configured true | YAMLs; `neck.py`; `fastitpn.py` |
| AMP | absent from released YAML → project default false | same | YAML/config path |

The README launches eight processes. Nominal arithmetic gives aggregate batches 512 for B224 and 128 for L384; no successful run or peak-memory measurement was made in this audit.

- No encoder freeze is configured; pretrained Fast-iTPN weights initialize the encoder.
- The project exposes a distributed launcher using `LOCAL_RANK`. A one-process `torchrun` launch may be structurally possible, but a verified plain/single-RTX-3060 recipe is not released.
- No gradient-accumulation setting was found.

### G. Profiling and export evidence

- `tracking/profile_model.py` profiles the same complete model object separately in encoder, neck, and decoder modes, then sums parameter counts. Because each THOP call sees the same resident module object, the summed parameter figure repeats parameters and is not a valid unique-parameter total (`profile_model.py:46-60`).
- Its only custom operation handler is `nn.MultiheadAttention`. The pure-PyTorch Mamba state expansion, exponentials, elementwise state updates, and state matrix product are not given a custom counting rule and may be incompletely represented (`profile_model.py:28-60`; `neck.py:248-278`).
- The speed path uses precomputed inputs/state and excludes crop/preprocessing, template-bank admission/selection, confidence synchronization, and tracker bookkeeping. No CUDA synchronization was found around the timing loop.
- No MCITrack ONNX, TensorRT/Torch-TensorRT, TorchScript exporter, custom plugin, or dynamic-state parity script was found.
- Export must account for four explicit hidden-state inputs/outputs, fixed active template count, cross-attention, grouped Conv1d, large elementwise state tensors, Python bank management, `.item()`, and `.tolist()`.

### H. HG4 evidence package — no decision

Evidence relevant to a single RTX 3060 12 GB:

- complete datasets, batches, epochs, optimizer, pretrained initialization, and activation-checkpoint settings are present;
- released commands use eight processes and large declared batches, especially B224 batch 64/process;
- L384 has four nominal FP32 hidden-state payloads totaling about 216 MiB per sample at inference shape before weights/activations; training retains additional activations and a two-search-frame unroll;
- no verified one-GPU batch/accumulation setting, peak-memory trace, or RTX 3060 reproduction is supplied;
- profiler parameter aggregation is invalid and cannot substitute for a memory run.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

Structural evidence relevant to Jetson Nano:

- every frame re-encodes five raw templates and one search, then executes four Mamba state expansions, four Injectors, six Extractors, Fast-iTPN slices, and the center head;
- pure-PyTorch Mamba avoids a required custom selective-scan plugin, but it explicitly materializes large `[B,L,d_inner,d_state]` tensors;
- the active hidden state is fixed-size, while the raw GPU template bank is bounded but can reach 200–500 entries;
- the released profiler omits tracker work and unsynchronized timing cannot establish device latency;
- no complete exporter, TensorRT engine, state-I/O parity test, Nano latency, memory, power, or thermal evidence exists.

**HG5 = PENDING**

### J. Code-visible cost sites

| Label | Site |
|---|---|
| CODE FACT — inspected | five raw templates and one search are encoded on every frame; there is no template-feature cache |
| CODE FACT — inspected | four Mamba blocks, four MHA Injectors, six MHA Extractors, and all configured Fast-iTPN slices execute every frame |
| CODE FACT — inspected | B224 has about 49 MiB and L384 about 216 MiB of nominal FP32 four-layer hidden-state payload at batch 1 |
| CODE FACT — inspected | hidden state is replaced every frame and reset to `None` below UPH; it does not grow with sequence length |
| CODE FACT — inspected | the bounded raw GPU template bank can retain 200–500 crops and active templates are periodically resampled |
| ENGINEERING TARGET TO PROFILE | synchronized encoder, each fusion insertion, Mamba state update, decoder, and host bookkeeping separately |
| ENGINEERING TARGET TO PROFILE | activation/allocator peak of the four expanded Mamba states for B224 versus L384 and FP32 versus supported reduced precision |
| ENGINEERING TARGET TO PROFILE | effect of configured checkpoint wrappers during `no_grad` inference |
| ENGINEERING TARGET TO PROFILE | explicit hidden-state export I/O, TensorRT/operator support, and numerical parity over long sequences |

### K. Unresolved items

1. Valid unique parameter/MAC count for both variants: **PENDING; RELEASED PROFILER AGGREGATION IS NOT VALID**.
2. CUDA-synchronized end-to-end tracker latency including template/state initialization: **NOT FOUND**.
3. Verified single-RTX-3060 training batch/accumulation and peak memory: **NOT FOUND**.
4. Reduced-precision hidden-state dtype and long-sequence numerical parity: **OPEN QUESTION**.
5. Repeated `initialize` on one tracker does not explicitly reset `h_state`: **OPEN QUESTION**.
6. End-to-end ONNX/TensorRT/TorchScript export with four dynamic states: **PENDING**.

## 8. Batch completion and locked next state

| Candidate | Final code-audit state | HG4 | HG5 |
|---|---|---|---|
| CX017 GOT-JEPA | CODE AUDIT COMPLETE | PENDING | PENDING |
| CX020 SAMURAI | CODE AUDIT COMPLETE | PENDING | PENDING |
| CX024 DAM4SAM | CODE AUDIT COMPLETE | PENDING | PENDING |
| CX037 SSTrack-AAAI | CODE AUDIT COMPLETE | PENDING | PENDING |
| CX038 MCITrack | CODE AUDIT COMPLETE | PENDING | PENDING |

Batch C was not activated. No scientific-audit conclusion, hard-gate value, score, rank, shortlist, baseline, architecture, or canonical-matrix field was changed.

BATCH B CODE EVIDENCE EXTRACTION:
COMPLETE

HG4 DECISIONS:
NOT MADE

HG5 DECISIONS:
NOT MADE

HG6:
NOT STARTED

SOFT SCORING:
NOT STARTED

PRIMARY SHORTLIST:
NONE

MAIN BASELINE:
NONE

PROPOSED ARCHITECTURE:
NONE
