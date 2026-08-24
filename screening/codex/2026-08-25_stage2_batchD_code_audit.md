# Stage 2A — Batch D code / engineering evidence audit

Date: **2026-08-25**

Lane: **Codex worker — code and engineering audit**

Stage: **Stage 2A, final systematic Batch D evidence extraction only**

## 1. Scope, evidence labels, and stopping boundary

This report records implementation evidence for the only three active Batch D candidates:

- CX053 — UncTrack
- CX058 — HiT-DyHiT
- CX125 — MPT

CX051 UMDATrack remains HG3 PENDING and was not activated or audited here. These three active candidates are not a shortlist.

Every repository was inspected in an isolated detached checkout at the exact full SHA registered in the project source manifest. File and line references below refer to those pinned trees. The Manager scientific interpretation file `screening/manager/2026-08-25_stage2_batchD_scientific_audit.md` was deliberately not read before this independent report was completed.

Evidence labels:

- **CODE FACT — inspected:** directly visible in the pinned implementation/configuration, or an exact quantity reconstructed from those constructors.
- **RESOURCE AVAILABILITY FACT:** directly visible release, checkpoint, script, or tool availability.
- **ENGINEERING TARGET TO PROFILE:** a code-visible execution site whose measured cost remains unknown.
- **OPEN QUESTION:** evidence not found or an implementation ambiguity not resolved by inspection.

No training, checkpoint reproduction, targeted HG5 profiling, model export, TensorRT build, RTX 3060 fit test, or Jetson Nano benchmark was performed. This report does not decide HG4 or HG5. It does not begin HG6, assign S1–S7, calculate a score, rank candidates, form a shortlist, select a baseline, or design an architecture. The canonical matrix was not modified. There is no Batch E, and no later stage is activated by this report.

## 2. Completion and stage guard

| Candidate | Exact pinned source inspected | Required A–K fields | Code-audit state | HG4 | HG5 |
|---|---:|---:|---:|---:|---:|
| CX053 UncTrack | yes | complete | complete | PENDING | PENDING |
| CX058 HiT-DyHiT | yes | complete | complete | PENDING | PENDING |
| CX125 MPT | yes | complete | complete | PENDING | PENDING |

“Complete” means that the requested implementation-evidence fields were inspected and unresolved items were explicitly retained. It does not mean successful reproduction, deployment feasibility, or a gate decision.

## 3. CX053 — UncTrack

### A. Provenance and released variants

- **ID:** CX053
- **Official repository:** `ManOfStory/UncTrack`
- **Pinned full SHA:** `61bd4be673ac32dd8948f995ce4548855d0ab1d0`
- **Registered official code source:** [R48](../../references/references.md#r48)
- **CODE FACT — inspected:** the isolated checkout was detached at the full SHA above and remained clean.
- **RESOURCE AVAILABILITY FACT:** the official repository identifies itself as the TIP 2025 implementation and links checkpoint/raw-result folders (`README.md:1-11,102-104`).
- **RESOURCE AVAILABILITY FACT:** the official Google Drive checkpoint folders inspected on 2026-08-25 contain `unctrack_base.pth.tar` and `unctrack_online_base.pth.tar` under `UncTrack-B`, and `unctrack_large.pth.tar` and `unctrack_online_large.pth.tar` under `UncTrack-L`, with stage logs.
- **CODE FACT — inspected:** `tracking/test_unctrack.sh:9-52` instead requests `unctrack_base_online.pth.tar` and `unctrack_large_online.pth.tar`. The word order does not match the current official Drive filenames.
- **RESOURCE AVAILABILITY FACT:** the shell additionally names `unctrack_large_online_got.pth.tar`, but no dedicated GOT-10k configuration or that checkpoint was found in the pinned tree or current official checkpoint folders. Base GOT-10k testing uses the general Base online checkpoint.

UncTrack+AR is kept separate from pure UncTrack throughout this audit. The B/L VOT wrappers instantiate UncTrackOnline and then invoke an additional 384×384 Alpha-Refine mask network after each tracker frame (`external/AR/pytracking/VOT2020_super_only_mask_384_HP/unctrack_b_alpha_seg_class.py:20-56,81-85`; Large counterpart at the same ranges). Alpha-Refine cost is therefore not attributed to pure UncTrack.

### B. Model construction and variant mapping

The online construction chain is `build_unctrack_online` → ConvMAE backbone → `Pyramid_Corner_Uncertainty_Predictor` (ULD) → `UncertaintyAwareScoreDecoder` (PMN) (`lib/models/unctrack/unctrack_online.py:587-611`; `head.py:218-375`; `uncertainty_aware_score_decoder.py:113-263`).

| Variant | Released configuration and construction | Input/features | Checkpoint state |
|---|---|---|---|
| UncTrack-B | `experiments/unctrack/baseline.yaml` and `unctrack_online/baseline.yaml`; ConvMAE-Base; widths 256/384/768, depths 2/2/11, 12 heads | template 128, search 288; template 8×8, search 18×18; ULD output 72×72 | stage-1 and stage-2 files externally available, with filename-order mismatch noted above |
| UncTrack-L | `baseline_large.yaml` in both experiment folders; ConvMAE-Large; widths 384/768/1024, depths 2/2/20, 16 heads | template 192, search 384; template 12×12, search 24×24; ULD output 96×96 | stage-1 and stage-2 files externally available, with filename-order mismatch noted above |
| GOT-10k-specific | Base shell uses general Base online checkpoint; Large shell names a GOT-specific file | no separate builder/config or changed graph found | dedicated Large artifact and recipe **NOT FOUND** |
| UncTrack+AR | pure Base/Large online tracker followed by Alpha-Refine segmentation/refinement | extra 384×384 refinement network | separate Alpha-Refine checkpoint and VOT dependencies required |

Evidence for widths, depths, resolutions and heads: four released YAMLs; `lib/models/unctrack/unctrack_online.py:396-406`; `lib/models/unctrack/head.py:410-436`.

**OPEN QUESTION:** exact total parameter constants are not recorded in the pinned source. The provided profiler derives them at runtime, but running the profiler was outside this static evidence lane.

### C. Runtime graph

| Component | Execution frequency | Input/output | Persistent state | Code evidence |
|---|---:|---|---|---|
| RGB crop/normalization | initialize and each tracking attempt | RGB NumPy crop → CUDA FP32 tensor | raw normalized template/search tensors | `lib/test/tracker/tracker_utils.py:20-29`; `unctrack_online.py:73-107,200-204,233-238` |
| Template cache setup | initialize; later at template-update intervals when `online_size>1` | static plus bounded online templates → cached per-block template K/V and initial-template feature | bounded `qkv_mem` and template feature | model `lib/models/unctrack/unctrack_online.py:97-133,353-393`; tracker `:73-92,297-307` |
| Search ConvMAE | every primary attempt; again after an unreliable result | current search → `[B,D,18,18]` or `[B,D,24,24]`; search queries attend cached template K/V | cached templates | model `:329-351`; tracker `:233-248` |
| ULD | every neural attempt | search feature → TL/BR score maps, two-channel TL/BR sigma maps, coarse `xyxy` box | none | `lib/models/unctrack/head.py:218-248,256-278,295-375` |
| Confidence embedding | every PMN-scored attempt | four sigma channels → D/2 channels at backbone resolution | none | `lib/models/unctrack/unctrack_online.py:530-568` |
| Current prototype | every PMN-scored attempt | pooled template query + confidence-augmented masked search KV → `[B,1,D]` | none | `uncertainty_aware_score_decoder.py:173-209` |
| Prototype-memory selection/fusion | every PMN-scored attempt | cosine top-k from `[1,K,D]`; current-to-memory attention | fixed prototype bank | decoder `:147-170,240-263` |
| Template fusion/reliability | every PMN-scored attempt | prototype-to-cached-template attention + three-layer MLP → one logit | cached initial template feature | decoder `:113-140,160-171,244-252` |
| Reliability decision | every primary attempt | `sigmoid(logit).item()` versus 0.8 | scalar branch result | tracker `:256-271`; parameter `lib/test/parameter/unctrack_online.py:33-42` |
| Unreliable recovery | first-pass score ≤0.8 | second full neural attempt with crop factor `1.5 × search_factor`; score chooses redetected bbox or previous state as Kalman observation | Kalman state | tracker `:200-231,266-271` |
| Kalman | one update after primary result; one additional update in unreliable recovery | bbox observation → fixed eight-dimensional state/covariance | `[cx,cy,w,h,dx,dy,dw,dh]` plus covariance | tracker `:135-198,227-231,266-271` |
| Prototype update | default every frame, only after eligible first-pass score | FIFO drop index 0 and append candidate | fixed `[1,3,D]` bank | tracker `:281-294`; parameter `:40-42` |

**CODE FACT — inspected:** the recovery crop is 1.5 times the ordinary search factor, not two times. The unreliable branch adds a second complete ConvMAE+ULD+PMN inference, preprocessing and Kalman work; it does not select a different neural architecture.

### D. Template, prototype memory, and bounded state

- **CODE FACT — inspected:** prototype memory initializes by repeating the initial prototype three times, producing `[1,3,D]`; the released model-side top-k is three (`lib/test/tracker/unctrack_online.py:104-126`; `experiments/unctrack_online/baseline.yaml:83-86`). All three stored prototypes therefore participate, ordered by cosine similarity (`uncertainty_aware_score_decoder.py:254-263`).
- **CODE FACT — inspected:** the prototype bank is bounded. FIFO slicing keeps two entries and appends one; no prototype history grows with sequence length (`tracker/unctrack_online.py:285-294`).
- **CODE FACT — inspected:** the online-template set is also bounded. Base/Large release settings use size two for LaSOT, UAV, OTB and GOT-10k; size one for TrackingNet; size five for VOT2020 and NAT2021. VOT2020-LT inherits the default size three because no YAML override exists (`experiments/unctrack_online/baseline*.yaml:92-110`; `lib/config/unctrack_online/config.py:103-124`).
- **CODE FACT — inspected:** released template-update intervals are dataset- and variant-specific. Base uses LaSOT 160, GOT10K-test 25, GOT10K-train 40, TrackingNet 25, OTB 6, UAV 30, VOT20 12, VOT20LT 200 and NAT2021 12 frames. Large uses LaSOT 160, GOT10K-test 23, GOT10K-train 40, TrackingNet 25, OTB 10, UAV 150, VOT20 8, VOT20LT 200 and NAT2021 12 (`experiments/unctrack_online/baseline.yaml:92-101`; Large counterpart `:92-101`).
- **CODE FACT — inspected:** dynamic template selection keeps the maximum reliable first-pass score in each update interval; slots fill and are then cyclically replaced. There is no nearest-template retrieval. Similarity retrieval applies to prototype memory, not raw templates (`tracker/unctrack_online.py:273-307`; decoder `:254-263`).
- **CODE FACT — inspected:** when `online_size>1`, template features and attention-block K/V are cached; ordinary frames encode only search. Update frames re-encode the static and active online templates (`model/unctrack_online.py:329-393`; tracker `:297-307`).
- **CODE FACT — inspected:** when `online_size==1`, the tracker calls the full static-template + online-template + search model each frame, re-encoding both templates (`tracker/unctrack_online.py:241-248`; model `:266-327`).
- **CODE FACT — inspected:** Base persistent neural shapes are search `[1,768,18,18]`, initial template `[1,768,8,8]`, memory `[1,3,768]`; Large uses `[1,1024,24,24]`, `[1,1024,12,12]`, `[1,3,1024]` (`unctrack_online.py:192-238,396-406`; decoder `:189-263`).
- **CODE FACT — inspected:** PMN first applies attention from current prototype `[B,1,D]` to selected memory `[B,3,D]`, then attention from the resulting `[B,1,D]` query to the cached initial-template grid `[B,64,D]` for Base or `[B,144,D]` for Large (`uncertainty_aware_score_decoder.py:147-170,244-263`).
- **CODE FACT — inspected:** stored raw templates, cached K/V, prototype bank, one maximum-score candidate and Kalman arrays are all bounded. No sequence-length-growing image, feature or trajectory history was found.

### E. Dynamic computation

- **CODE FACT — inspected:** ULD uncertainty is deterministic. TL/BR sigma maps are produced by convolution and sigmoid in the same forward; there is no Monte-Carlo sampling or repeated stochastic inference (`lib/models/unctrack/head.py:326-375`).
- **CODE FACT — inspected:** ULD has separate TL and BR pyramid branches, each with score and added `conv6`/`adjust5`/`adjust6` uncertainty paths (`head.py:218-278,326-375`).
- **CODE FACT — inspected:** PMN executes on every neural attempt. A low-reliability frame can therefore pay ConvMAE, ULD and PMN twice (`lib/test/tracker/unctrack_online.py:233-271`).
- **CODE FACT — inspected:** only the first-pass score controls prototype and template updates; the redetection result is not inserted into either update path (`tracker/unctrack_online.py:268-307`).
- **CODE FACT — inspected:** every first pass calls `kalman_update(pred_bbox)`, but the returned filtered box is discarded. A reliable first pass therefore publishes the clipped raw neural prediction. On an unreliable first pass, `redetect()` performs a second Kalman update and returns that filtered box: it observes the redetected bbox when the second score is reliable, otherwise it observes the previous tracker state (`tracker/unctrack_online.py:200-231,256-271`).
- **CODE FACT — inspected:** two large `sigma_tl`/`sigma_br` MLP objects are instantiated in ULD but their calls are commented; executed uncertainty comes from convolutional sigma maps (`head.py:250-254,280-284,346-375`). This states literal execution only and does not infer a performance weakness.
- **CODE FACT — inspected:** tracker field `params.topk` is stored but not consumed by model inference; model top-k comes from `cfg.TEST.TOPK` at construction (`tracker/unctrack_online.py:30-32`; model builder `:587-597`).
- **CODE FACT — inspected:** reliability threshold is fixed at 0.8 in the parameter file. The prototype-positive threshold is entrypoint-dependent: YAML/direct VOT construction gives 0.5, while normal `tracking/test.py` defaults `--params__ppt` to 0.8 and overrides it (`baseline*.yaml:83-86`; `tracking/test.py:49-63`; `lib/test/evaluation/tracker.py:288-301`).

### F. Training evidence

Both stages use GOT10K-vottrain, LaSOT, COCO17 and TrackingNet equally, with 60,000 training samples per epoch; validation uses GOT10K-votval with 10,000 samples.

| Stage/variant | Batch per loader process | Epochs | AMP | Accumulation | Optimizer and frozen/trainable path |
|---|---:|---:|---:|---:|---|
| Base stage 1 | 32 | 550 | false | 1 | AdamW; backbone/head train, backbone LR ×0.1; score branch excluded |
| Base stage 2 | 4 | 50 | false | 1 | AdamW; PMN/confidence modules only |
| Large stage 1 | 32 | 50 | true | 3 | AdamW; `FREEZE_BACKBONE=True`; optimizer selects box-head parameters |
| Large stage 2 | 32 | 50 | false | 1 | AdamW; PMN/confidence modules only |

Evidence: four experiment YAMLs; `lib/train/base_functions.py:243-330`; `lib/train/train_script_unctrack.py:55-100`; `lib/train/trainers/ltr_trainer.py:38-98`.

- **CODE FACT — inspected:** stage 1 builds `build_unctrack` and trains CIoU, L1 and uncertainty losses, with the score module excluded/frozen (`train_script_unctrack.py:55-67,80-97`; `base_functions.py:306-320`; `actors/unctrack.py:60-145`).
- **CODE FACT — inspected:** stage 2 builds `build_unctrack_online`, samples three memory groups with two templates and one search per group, and trains binary reliability score loss (`lib/config/unctrack_online/config.py:49,67-81`; `lib/train/data/sampler.py:179-257,383-433`; train script `:85-97`).
- **CODE FACT — inspected:** stage-2 forward separately runs the frozen backbone for each of the three sampled groups before PMN loss construction (`lib/models/unctrack/unctrack_online.py:450-480`).
- **CODE FACT — inspected:** `TRAIN_SCORE=True` freezes all names except those containing `score`, `embedder` or `conf_conv`; backbone and ULD box head are frozen, while PMN/confidence embedding train (`config.py:49`; `base_functions.py:243-260`).
- **RESOURCE AVAILABILITY FACT:** official shell examples specify eight DDP processes; an explicit `--mode single` path also exists (`tracking/train_unctrack.sh:1-15`; `tracking/train.py:15-48`). The single-GPU CLI does not prove a particular memory fit.
- **CODE FACT — inspected:** Base/Large initialization requires external ConvMAE weights. Stage 2 additionally requires a stage-1 checkpoint; Large stage 1 sets `PRETRAINED_STAGE1=True` and also expects an unspecified `stage1_model` (`train_unctrack.sh:1-15`; four YAML model blocks; builders `unctrack.py:506-528`, `unctrack_online.py:599-611`).
- **RESOURCE AVAILABILITY FACT:** no activation-checkpointing path was found. AMP and gradient accumulation exist only through the active settings recorded above.

### G. Profiling and export evidence

- **CODE FACT — inspected:** `tracking/profile_model.sh` invokes the current online builder for Base and Large with update skip 200 (`profile_model.sh:1-5`; `profile_model.py:92-139`).
- **CODE FACT — inspected:** THOP receives a full template + online-template + search + PMN forward, including ULD and PMN, but this is an initialization-style non-cached model call rather than steady-state search-only execution (`profile_model.py:53-62`).
- **CODE FACT — inspected:** speed timing performs ten full-forward warm-ups, creates the initial prototype outside the timed region, then times 1,000 search-only forwards and calls `set_online` every 200 iterations (`profile_model.py:65-82`).
- **CODE FACT — inspected:** no `torch.cuda.synchronize()` surrounds the timing boundary. Cropping, normalization, bbox mapping, `.item()`/`.tolist()`, Kalman, FIFO/template controller logic and unreliable second attempts are excluded.
- **CODE FACT — inspected:** the profiler fixes one online template and update skip 200, rather than reproducing each released dataset’s online size and update interval.
- **ENGINEERING TARGET TO PROFILE:** validate THOP coverage of raw attention matmuls; `custom_ops` is commented and attention uses `@` (`profile_model.py:29-32,55-59`; `unctrack_online.py:74-110`; score decoder `:75-90,147-170`).
- **RESOURCE AVAILABILITY FACT:** no UncTrack ONNX, TensorRT, TorchScript or `torch.compile` export pipeline was found. Installed ONNX packages and generic `PreprocessorX_onnx` do not export the model (`install.sh:94-105`; `tracker_utils.py:46-58`).
- **CODE FACT — inspected:** pure UncTrack has no custom CUDA operator. PreciseRoIPooling CUDA code is under external Alpha-Refine and applies only to UncTrack+AR.
- **ENGINEERING TARGET TO PROFILE:** export analysis must cover mutable per-block `qkv_mem`, dynamic `torch.topk`, tensor-to-Python integer slicing, confidence `.item()`, bbox `.tolist()`, NumPy Kalman state and conditional second inference (`unctrack_online.py:97-133`; decoder `:173-187,254-263`; tracker `:173-231,256-271`).
- **CODE FACT — inspected:** model/head constructors create some tensors with hard-coded `.cuda()` instead of registered buffers (`head.py:287-293`; `unctrack_online.py:439-444`).

### H. HG4 evidence package — no decision

- **RESOURCE AVAILABILITY FACT:** Base/Large configs, stage-1 and stage-2 checkpoints/logs, training code and evaluator source exist.
- **CODE FACT — inspected:** static AST parsing of the pinned official online tracker fails at `lib/test/tracker/unctrack_online.py:159` because that line contains a standalone full-width `）` (U+FF09). The model, ULD, PMN, profiler and training source files parse successfully.
- **CODE FACT — inspected:** official checkpoint filename ordering differs between the current Drive folders and evaluation shell.
- **OPEN QUESTION:** dedicated GOT-10k Large checkpoint/config provenance remains unresolved.
- **OPEN QUESTION:** execution after correcting the invalid character and reconciling filenames was not attempted in this lane.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

- **CODE FACT — inspected:** graph boundaries, template-cache modes, ULD/PMN frequency, bounded state, conditional second attempt and profiler exclusions are mapped above.
- **RESOURCE AVAILABILITY FACT:** no complete export/deployment pipeline is released.
- **ENGINEERING TARGET TO PROFILE:** measure initialization, steady state by online-template size, template-update frames and low-confidence two-attempt frames separately, with synchronization and complete pre/postprocessing.
- **OPEN QUESTION:** actual device latency, memory, second-attempt frequency, operator support and Jetson Nano behavior remain unmeasured.

**HG5 = PENDING**

### J. Code-visible cost sites

| Label | Site |
|---|---|
| CODE FACT — inspected | Base/Large fixed search resolutions are 288/384, giving 324/576 search tokens |
| CODE FACT — inspected | ULD executes separate TL/BR pyramids and score/uncertainty output paths on each attempt |
| CODE FACT — inspected | PMN executes confidence embedding, masked prototype construction, cosine top-k, memory attention, template attention and MLP on each attempt |
| CODE FACT — inspected | an unreliable first pass invokes a second full ConvMAE+ULD+PMN computation |
| CODE FACT — inspected | `online_size==1` re-encodes both templates every frame; larger sizes cache but periodically re-encode all bounded online templates |
| CODE FACT — inspected | tracker `.item()` and `.tolist()` cross the device/Python boundary on each attempt |
| ENGINEERING TARGET TO PROFILE | executed versus instantiated ULD parameters, because `sigma_tl`/`sigma_br` MLPs are present but not called |
| ENGINEERING TARGET TO PROFILE | attention cost versus online-template count and amortized `set_online` cost |

### K. Unresolved items

1. Exact official parameter/MAC values without executing the profiler: **PENDING**.
2. Hardware, CUDA/cuDNN, precision and timing boundary behind any reported FPS: **NOT FOUND**.
3. Dedicated GOT-10k-specific checkpoint availability and training recipe: **NOT FOUND**.
4. Strict checkpoint loading after filename and syntax reconciliation: **PENDING**.
5. Any external/private ONNX or TensorRT path outside the pinned official repository: **OPEN QUESTION**.
6. Actual unreliable-frame/redetection rate and complete end-to-end latency: **PENDING**.
7. Intended prototype-positive threshold across normal CLI and direct/VOT entrypoints: **OPEN QUESTION**, with the code-visible values recorded above.

## 4. CX058 — HiT, DyHiT, and DyOSTrack

### A. Provenance and released configurations

- **ID:** CX058
- **Official repository:** `kangben258/HiT`
- **Pinned full SHA:** `ca806400def2b9ab42628f7a7e941b188d89606f`
- **Registered official code source:** [R50](../../references/references.md#r50)
- **CODE FACT — inspected:** the isolated checkout was detached at the full SHA above and remained clean.
- **CODE FACT — inspected:** released configs are `experiments/HiT/HiT_Base.yaml`, `HiT_Small.yaml`, `HiT_Tiny.yaml`, `experiments/DyHiT/stage1.yaml`, `stage2.yaml`, and `experiments/DyOSTrack/dyostrack.yaml`.
- **RESOURCE AVAILABILITY FACT:** README links one shared Google Drive directory for trained models/raw results, but does not map exact downloadable filenames to each configuration (`README.md:228-230`). No checkpoint or ONNX artifact is committed.
- **OPEN QUESTION:** exact per-variant checkpoint identities and hashes inside that shared folder were not established from repository files.

HiT, standalone DyHiT, and DyOSTrack are treated as three distinct runtime graphs below. Evidence from one is not transferred to another.

### B. Model construction and variant mapping

| Variant | Backbone / stages | Input and tokens | Bridge / head |
|---|---|---|---|
| HiT-Base | LeViT-384; widths 384/512/768; depths 4/4/4; heads 6/9/12; key dimension 32 | template 128, search 256; initial 64+256 tokens; later joint counts 80 and 20 | `NECK_FB` Bridge; 256-channel two-tower CORNER head |
| HiT-Small | LeViT-128; widths 128/256/384; depths 4/4/4; heads 4/8/12; key dimension 16 | same geometry/counts | same Bridge/head family |
| HiT-Tiny | LeViT-128S; widths 128/256/384; depths 2/3/4; heads 4/6/8; key dimension 16 | same geometry/counts | same Bridge/head family |
| DyHiT | `DyHiT_384` stage 1 and `DyHiT_384_stage2_256tokens` stage 2; LeViT-384 family | template 128, search 256; Route1 stage emits `[B,320,384]` | separate Route1 bottleneck/CORNER head; Route2 Bridge plus large CORNER head |
| DyOSTrack | lightweight `LeViT_384_layer4_dytracker` plus full OSTrack ViT-B/16 host with candidate elimination at layers 3/6/9, keep 0.7/0.7/0.7 | both consume the same 128/256 raw template/search pair | lightweight CORNER head or host CENTER head |

Evidence: HiT YAMLs `MODEL` blocks; `lib/models/HiT/levit.py:17-32,1044-1075`; DyHiT YAMLs and `levit_dyhit_stage2.py:30-32,128-135`; DyOSTrack YAML `:47-77`; `levit_dytracker.py:30-35,138-144`.

- **CODE FACT — inspected:** the Bridge uses two transposed-convolution upsampling layers to add intermediate search maps, then emits a 16×16 search map and pooled global vector at width 256 (`lib/models/HiT/neck.py:35-80`).
- **CODE FACT — inspected:** the HiT prediction head has independent TL/BR convolution towers and spatial soft-argmax (`lib/models/HiT/head.py:22-90`).
- **OPEN QUESTION:** fixed Base/Small/Tiny parameter and MAC values are not stored in README/configs. The executable profilers have defects documented below and were not run in this lane.

### C. Runtime graphs

#### Static HiT

| Component | Execution frequency | Input/output | Persistent state | Code evidence |
|---|---:|---|---|---|
| Crop/preprocess | template once; search every frame | RGB crop → normalized tensor | raw template and latest bbox | `lib/test/tracker/HiT.py:40-67` |
| Patch embedding | every frame for both template and search | 128/256 images → 64+256 tokens | none encoded | `lib/models/HiT/levit.py:1015-1024` |
| Hierarchical joint encoder | every frame | joint tokens through three stages | none | `levit.py:939-991,1024-1037` |
| Dual-image relative positional bias | every attention layer | separate search grid and offset template grid → attention bias | learned bias tables/indexes | `levit.py:402-419,437-480` |
| Bridge | every frame | three feature levels → global token + 256 search tokens, width 256 | none | `neck.py:53-80` |
| CORNER head | every frame | 16×16 search feature → `[B,1,4]` | none | `lib/models/HiT/hit.py:59-89` |

**CODE FACT — inspected:** the pinned tracker calls `forward_backbone(images_list)` without `first_score` and `threshold`, while the pinned method signature requires both positional arguments (`lib/test/tracker/HiT.py:67-71`; `lib/models/HiT/hit.py:54-57`). The static PyTorch tracker path therefore requires source reconciliation before runnable status can be confirmed.

#### Standalone DyHiT

| Component | Execution frequency | Input/output | Persistent state | Code evidence |
|---|---:|---|---|---|
| Patch embed + first LeViT stage | always | both images → `[B,320,384]` | raw template | `levit_dyhit_stage2.py:1100-1113` |
| Router | every frame with released interval 1 | first-stage 256 search tokens → sigmoid `[B,256,1]` | none; tracker also keeps first-frame score | `levit_dyhit_stage2.py:149-161,1066,1113-1118`; config `:106-116` |
| Route1 | first frame unconditionally; later if route score exceeds threshold | reuse first-stage output → pooled token, small bottleneck, small CORNER head | none | `levit_dyhit_stage2.py:1123-1135`; `hit.py:159-165` |
| Route2 | if route score does not exceed threshold | continue from the same first-stage tensor → later stages `[B,80,512]`, `[B,20,768]`, Bridge, large head | none | `levit_dyhit_stage2.py:1136-1143`; `hit.py:166-172` |
| Tracker controller | every frame | route bbox → map/clip → next bbox | bbox, frame counter, raw template, first-frame route score | `lib/test/tracker/DyHiT.py:23-41,43-82` |

- **CODE FACT — inspected:** Route2 reuses Route1-stage features and does not recompute patch embedding or the first stage.
- **CODE FACT — inspected:** Route1 and Route2 have distinct heads (`box_head_small` and `model1.box_head`) but return the same final bbox-dictionary shape (`hit.py:128-133,159-172,235-257`).

#### DyOSTrack / released host integration

| Component | Execution frequency | Input/output | Persistent state | Code evidence |
|---|---:|---|---|---|
| Lightweight LeViT + router | always | same raw template/search → first-stage features and `[B,256,1]` router values | lightweight model resident | `lib/models/dyostrack/dyostrack.py:183-194`; `levit_dytracker.py:1083-1099` |
| Easy path | conditional | reuse lightweight features → lightweight CORNER head | none | `dyostrack.py:196-203` |
| Hard path | conditional | run complete OSTrack backbone and CENTER head after routing | full host model resident | `dyostrack.py:204-219` |
| Controller | every frame | selected bbox → next state | one shared bbox and raw template | `lib/test/tracker/DyOSTrack.py:49-70,76-106` |

- **CODE FACT — inspected:** the host does not run before the route decision. On hard frames, however, it receives the same raw crops and redoes its own feature extraction; lightweight features are not reused.
- **CODE FACT — inspected:** both lightweight and host parameters remain resident, and the builder loads two checkpoints (`dyostrack.py:254-322`).
- **RESOURCE AVAILABILITY FACT:** DyOSTrack is the only concrete host integration in the pinned tree; no second host configuration was found (`README.md:194-203`).

### D. Template and temporal state

- **CODE FACT — inspected:** HiT, DyHiT and DyOSTrack store a preprocessed raw template tensor at initialization, not an encoded template cache (`lib/test/tracker/HiT.py:47-53`; `DyHiT.py:50-55`; `DyOSTrack.py:49-70`).
- **CODE FACT — inspected:** each tracking frame passes `[search, self.template]` through patch embedding and the selected graph; the template is re-encoded every frame (`HiT.py:64-71`; `DyHiT.py:68-78`; `DyOSTrack.py:76-106`).
- **CODE FACT — inspected:** none of the three released tracker classes replaces or updates the template after initialization.
- **CODE FACT — inspected:** DyHiT config declares update-related keys, but the tracker consumes only route threshold, interval and token-score threshold. The released graph has no dynamic-template encoding (`lib/config/DyHiT/config.py:107-116`; `lib/test/parameter/DyHiT.py:18-28`; `lib/test/tracker/DyHiT.py:38-41`).
- **CODE FACT — inspected:** no temporal feature/history bank exists. State is limited to bbox, frame counter, raw template and, for DyHiT, a first-frame route score.
- **CODE FACT — inspected:** if `INTERVAL>1`, frames without router execution reuse `first_score`; later router results are not saved as a new persistent score (`DyHiT.py:72-82`). Released interval is one.

### E. Dynamic computation

- **CODE FACT — inspected:** the standalone router is a three-layer MLP `384→96→96→1` applied to 256 first-stage search tokens; it emits one scalar per token, not foreground/background logits (`levit_dyhit_stage2.py:149-161,1066,1113-1118`).
- **CODE FACT — inspected:** the frame route scalar is the mean of sigmoid token values greater than `SCORE_T=0.6`. Empty selection yields NaN and is replaced by 0.01 (`levit_dyhit_stage2.py:1113-1122`).
- **CODE FACT — inspected:** `score > THRESHOLD` selects Route1; otherwise Route2 (`:1130-1143`).
- **CODE FACT — inspected:** configuration default `THRESHOLD` is 0.9, but released `experiments/DyHiT/stage2.yaml:76-82` overrides it to `-9999`, explicitly commented as Route1-only. README separately discusses tuning from 0.6 to 1 (`README.md:146-149`). Thus the released Stage-2 YAML does not exercise a mixed Route1/Route2 operating point.
- **CODE FACT — inspected:** DyOSTrack uses token filter 0.6 and compares the mean to YAML threshold 0.75 (`dyostrack.py:190-205`; `experiments/DyOSTrack/dyostrack.yaml:100-106`).
- **CODE FACT — inspected:** the hard-path OSTrack performs sort/gather candidate elimination at blocks 3/6/9 and scatter restoration (`lib/models/dyostrack/layers/attn_blocks.py:9-74`; `vit_ce.py:142-177`).
- **CODE FACT — inspected:** code-visible target/distractor interaction is joint template-search attention plus learned dual-image relative bias. No explicit distractor memory, distractor identity classifier, confidence-gated template update or temporal distractor bank was found.

### F. Training evidence

| Training lane | Datasets | Batch / epochs | Optimizer / trained modules |
|---|---|---|---|
| HiT T/S/B | LaSOT, GOT10K-vottrain, COCO17, TrackingNet equally; 60k samples/epoch | 32 / 1500 | AdamW, LR 5e-4, weight decay 1e-4, drop 1200; backbone and head trained |
| DyHiT stage 1 | same four datasets | 128 / 90 | AdamW, LR 1e-4; loaded large HiT frozen; Route1 bottleneck and small head trained |
| DyHiT stage 2 | same four datasets | 128 / 60 | AdamW, LR 1e-4; only names containing `router` train |
| DyOSTrack | no new training lane | not applicable | training-free combination of released lightweight and host models |

Evidence: HiT YAML train/data blocks; `levit.py:17-32,1076-1096`; DyHiT YAMLs; `hit.py:134-138,235-258`; `lib/train/actors/HiT.py:195-230,249-272`; README `:118-142,194-203`.

- **CODE FACT — inspected:** HiT selects the official LeViT ImageNet pretrained URL according to backbone and uses backbone LR multiplier one.
- **CODE FACT — inspected:** Stage 2 router targets are 16×16 maps: predicted-box IoU is assigned to tokens inside the GT region and zero elsewhere, with summed MSE. This is not a binary easy/hard classification label (`actors/HiT.py:195-230,249-272`).
- **RESOURCE AVAILABILITY FACT:** README provides eight-process and single-GPU HiT commands and single-GPU commands for both DyHiT stages.
- **CODE FACT — inspected:** released configs do not enable AMP; training code defaults absent AMP to false. No gradient accumulation or activation-checkpointing path was found (`lib/train/train_script.py:95-101`; `ltr_trainer.py:39-43,73-90`).
- **CODE FACT — inspected:** both DyHiT YAMLs leave `TRAIN.WEIGHT` empty with a comment requiring the preceding checkpoint, while `build_dyhit()` unconditionally calls `torch.load` through `load_pretrained` (`experiments/DyHiT/stage*.yaml:55-57`; `lib/models/HiT/hit.py:210-231,235-258`). Manual path population is mandatory.
- **OPEN QUESTION:** exact single-GPU peak memory and feasibility at batch 128 remain unmeasured.

### G. Profiling and export evidence

#### Static HiT profiler

- **CODE FACT — inspected:** `tracking/profile_model_hit.py` is configurable across Base/Small/Tiny, fuses LeViT BatchNorm, applies THOP to backbone and head, and times 100 warm-ups plus 1,000 model iterations (`:18-29,48-80,86-121`).
- **CODE FACT — inspected:** it operates on already-created GPU tensors, excludes pre/postprocessing, reprocesses both images each iteration, and supplies the head with separately precomputed `xz` rather than each loop iteration’s backbone output (`:71-78,119-121`).
- **CODE FACT — inspected:** no CUDA synchronization surrounds the `time.time()` boundary. Its preliminary `forward_backbone(images_list)` also has the pinned missing-argument mismatch.
- **ENGINEERING TARGET TO PROFILE:** verify attention MAC coverage because THOP has no custom hook for the repository’s custom LeViT attention and code-local additions are commented (`profile_model_hit.py:51-63`; `levit.py:420-426`).

#### DyHiT Route1 profiler

- **CODE FACT — inspected:** `profile_model_dyhit_route1.py` passes `first_score=1`, `frame=False`, `threshold=-99999`, so the speed loop selects Route1 without executing the actual router (`:84-96`).
- **CODE FACT — inspected:** its separate helper router has width 94 instead of the model’s 96 and references global `xz1`, not its function input (`:46-67`).
- **CODE FACT — inspected:** its THOP model call sets score and threshold both to 0.9; strict `>` therefore selects Route2, while the speed loop selects Route1 (`:69-95`). It lacks CUDA synchronization and tracker pre/postprocessing.
- **ENGINEERING TARGET TO PROFILE:** re-establish valid, separate Route1, Route2, router and route-mixture boundaries before using profiler output.

#### Export paths

- **CODE FACT — inspected:** `tracking/transfer_onnx.py` builds static HiT only, with fixed search/template axes, opset 11 and bbox output; it does not contain the DyHiT router or conditional branches (`:23-28,36-75,82-133`).
- **CODE FACT — inspected:** the exporter always invokes `build_hit` despite accepting `--script`, expects `VT_ep####.pth.tar` while train/test use `HiT_ep####.pth.tar`, and its wrapper inherits the missing-argument backbone call (`transfer_onnx.py:54-57,93-101`; `lib/test/parameter/HiT.py:24-26`; base trainer `:141-146`).
- **CODE FACT — inspected:** the ONNX video demo is static HiT, hard-codes 128/256 inputs, and sends the full template on every frame (`tracking/video_demo.py:39-64`).
- **RESOURCE AVAILABILITY FACT:** no official ONNX path for DyHiT/DyOSTrack, TensorRT script, `torch.compile` pipeline, complete TorchScript export or custom CUDA operator was found.
- **ENGINEERING TARGET TO PROFILE:** DyHiT export must cover Boolean token selection, `.item()`, NumPy NaN handling and Python threshold control flow. DyOSTrack additionally needs two resident engines and route-to-host control (`levit_dyhit_stage2.py:1113-1143`).

README desktop/AGX/NX speed figures have no code-visible precision, power/clock mode, JetPack, runtime version or synchronized end-to-end boundary (`README.md:49-72`). They are not Jetson Nano measurements.

### H. HG4 evidence package — no decision

- **RESOURCE AVAILABILITY FACT:** exact configs, data recipes, optimizer paths, checkpoint dependencies and single-/multi-GPU launch commands exist.
- **CODE FACT — inspected:** HiT trains its model; DyHiT stage 1 trains the lightweight branch over frozen HiT; stage 2 trains only the router.
- **CODE FACT — inspected:** official DyHiT batch is 128 and AMP/checkpointing/accumulation are inactive.
- **OPEN QUESTION:** peak memory and exact per-checkpoint availability remain unresolved.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

- **CODE FACT — inspected:** static HiT uses standard Conv/Linear/matmul/softmax/ConvTranspose operations and has intended PyTorch/ONNX/profile/demo paths.
- **CODE FACT — inspected:** pinned static tracker, profiler and exporter contain mandatory-argument or checkpoint-name mismatches.
- **RESOURCE AVAILABILITY FACT:** dynamic DyHiT and DyOSTrack have no official export pipeline; their controller includes `.item()` and Python branches.
- **OPEN QUESTION:** route-aware end-to-end device latency, memory, route distribution, export compatibility and Nano behavior remain unmeasured.

**HG5 = PENDING**

### J. Code-visible cost sites

| Label | Site |
|---|---|
| CODE FACT — inspected | static HiT, standalone DyHiT and DyOSTrack re-encode the raw template each frame |
| CODE FACT — inspected | HiT executes all three stages, Bridge upsampling/addition, feature projection and two corner towers each frame |
| CODE FACT — inspected | standalone DyHiT always pays patch embedding and the first stage; with interval one it also executes the router every frame |
| CODE FACT — inspected | Route2 reuses the first stage, then adds later stages, Bridge and its distinct head |
| CODE FACT — inspected | DyOSTrack always runs the lightweight model/router; hard frames additionally run the full host without feature reuse |
| CODE FACT — inspected | router `.item()` crosses from device tensor to Python control flow |
| ENGINEERING TARGET TO PROFILE | synchronized per-route latency, route proportions, dual-model residency and common end-to-end pre/postprocessing |

### K. Unresolved items

1. Exact per-variant checkpoint filenames/hashes inside the official shared folder: **OPEN QUESTION**.
2. Numerical Base/Small/Tiny parameter and MAC values under a corrected profiler: **PENDING**.
3. Whether static call-signature mismatches are branch drift or an unreconciled regression: **OPEN QUESTION**.
4. Intended standalone DyHiT operating point, because released Stage-2 YAML is Route1-only while README describes mixed thresholds: **OPEN QUESTION**.
5. Exact software, precision and power conditions behind reported device speed: **NOT FOUND**.
6. Reproducible DyHiT/DyOSTrack export and complete route-aware profiling: **NOT FOUND**.

## 5. CX125 — Motion Prompt Tracking (MPT)

### A. Provenance and released integrations

- **ID:** CX125
- **Official repository:** `zj5559/Motion-Prompt-Tracking`
- **Pinned full SHA:** `418eb6565038f92bf8bafa3d7dd02dc9e0426dae`
- **Registered official code source:** [R14](../../references/references.md#r14)
- **CODE FACT — inspected:** the isolated checkout was detached at the full SHA above and remained clean.
- **RESOURCE AVAILABILITY FACT:** README and the two result figures report five combinations: OSTrack-B256+MPT, SeqTrack-B256+MPT, ARTrack-B256+MPT, OSTrack-B384+MPT and SeqTrack-L384+MPT (`README.md:7-10,49`; `Results1.png`; `Results2.png`).
- **RESOURCE AVAILABILITY FACT:** the pinned tree contains source/configuration only for OSTrack: two `experiments/ostrack` YAMLs, `lib/models/ostrack`, the OSTrack test wrapper, and `train_script_prompt.py`. No SeqTrack or ARTrack source, configuration, training script or evaluation script was found. The official repository exposes only `main`, with no alternate implementation branch/tag.
- **RESOURCE AVAILABILITY FACT:** one generic Baidu “Models and Results” link exists, but no `.pth`, `.pt`, `.tar`, `.onnx` or engine artifact is committed, and the link is not mapped to exact filenames/hashes for the five combinations (`README.md:45`).
- **RESOURCE AVAILABILITY FACT:** `eval.sh:3-9` selects `MPT_MAE256` with script `ostrack`, making it the command-selected integration in this checkout. This does not select a research baseline.

### B. Model construction and candidate unit

| Released config | Complete host + MPT graph | Input/tokens | Head and checkpoint conventions |
|---|---|---|---|
| `MPT_MAE256.yaml` | OSTrack ViT-Base/16, width 768, depth 12, 12 heads + prompt encoder/decoder | template 128 → 64 host tokens; search 256 → 256 host tokens | 256-channel CENTER head; host pretrain `OSTrack_mae256_ep0300.pth.tar`; tester expects `OSTrack_prompt_ep0060.pth.tar` |
| `MPT_MAE384.yaml` | same ViT-Base construction + same prompt modules | template 192 → 144 tokens; search 384 → 576 tokens | same head; host pretrain `OSTrack_mae384_ep0300.pth.tar`; tester expects `OSTrack_prompt_ep0060.pth.tar` |

Evidence: both YAMLs’ model/test blocks; `lib/models/ostrack/vit.py:103-149`; `lib/test/parameter/ostrack.py:7-29`.

- **CODE FACT — inspected:** `build_ostrack_traj` constructs the complete OSTrack backbone, CENTER head, prompt encoder and prompt decoder. During training it loads the named full OSTrack checkpoint with `strict=False` (`lib/models/ostrack/ostrack_prompt.py:173-230`).
- **CODE FACT — inspected:** the CENTER head retains three convolution towers for center score, size and offset (`lib/models/layers/head.py:98-201,224-246`).
- **CODE FACT — inspected:** both configs set prompt width 768, trajectory length 30, training sparse maximum 5, `FREEZE='full'`, `PELOG=-5`, and encoder/decoder type `rep_token_weight` (YAML lines 1-18).
- **CODE FACT — inspected:** exact constructor-derived MPT parameter subtotal is 13,057,027: prompt encoder 49,920 plus decoder/heads 13,007,107. This excludes the entire OSTrack host. The learned 30×768 `tpe` table contributes 23,040 parameters and is instantiated/checkpoint-resident although the active `PELOG=-5` forward branch bypasses it.
- **OPEN QUESTION:** exact full host+MPT parameter/MAC totals are not supplied by a working pinned profiler configuration.

The reproducible code unit is therefore OSTrack+MPT, not a standalone tracker module and not the five reported integrations collectively. The SeqTrack/ARTrack graph boundaries remain unavailable.

### C. Runtime graph

| Component | Execution frequency | Input/output | Persistent state | Code evidence |
|---|---:|---|---|---|
| Search crop/preprocess | every frame | RGB frame + previous xywh → normalized search | latest `self.state` | `lib/test/tracker/ostrack.py:107-113` |
| Host OSTrack backbone | every frame | raw initial-template tensor + search tensor → joint ViT tokens | raw preprocessed initial template | tracker `:127-153`; `ostrack_prompt.py:52-67`; `vit.py:205-241` |
| Trajectory conversion | every frame | fixed 30-box CPU list → crop-relative normalized xyxy `[1,30,4]` on device | bounded `self.traj` | tracker `:99-100,129-147` |
| Prompt encoder | every frame | `[B,30,4]` → three representative + 60 corner tokens = `[B,63,768]`, plus PE | learned embeddings/PE | `prompt.py:136-147,183-228` |
| Two-way fusion decoder | every frame | 63 motion tokens + host search feature (16×16 or 24×24) → modified image tokens, scalar weight, corner-token prediction | none across frames | `prompt.py:230-300,384-393`; `transformer_prompt_weight.py:29-196` |
| Adaptive fusion | every frame | original `src0`, decoded `src`, scalar `w` → `(1-w)src0 + w src` | none | `ostrack_prompt.py:69-100` |
| CENTER head | once per inference frame | fused search map → center/size/offset/bbox | none | `ostrack_prompt.py:100,113-126,140-166` |
| Hann/postprocess/state | every frame | maps → full-image bbox | next bbox and FIFO trajectory | tracker `:154-172,252-269` |

- **CODE FACT — inspected:** the full visual host finishes before MPT fusion. MPT is inserted after final host search tokens and before the existing CENTER head.
- **CODE FACT — inspected:** `FREEZE='full'` changes optimizer participation only; the complete host backbone and head remain present and execute at inference.
- **CODE FACT — inspected:** inference makes one host backbone call and one MPT decoder call, not a second host inference.
- **CODE FACT — inspected:** the template tensor is stored once but its feature is not cached. It is patch-embedded and jointly processed with search tokens every frame (`tracker/ostrack.py:77-85,141-153`; `vit.py:205-236`).
- **CODE FACT — inspected:** MPT does not alter the current search crop. It changes the final search embedding before prediction; that bbox influences only the next crop through tracker state.

### D. Template, trajectory, and memory behavior

- **CODE FACT — inspected:** online trajectory is a Python list of exactly 30 xywh boxes, initialized by repeating the first bbox (`lib/test/tracker/ostrack.py:93-100`).
- **CODE FACT — inspected:** every frame transforms all 30 boxes relative to the current crop, normalizes them, converts xywh→xyxy, stacks them, and transfers a new tensor to the search device (`tracker/ostrack.py:129-147`; `processing_utils.py:82-105`).
- **CODE FACT — inspected:** the controller uses FIFO `pop(0)`/`append`. Both released YAMLs inherit `TEST.SPARSE=1`, so online history updates every frame; YAML `PROMPT.SPARSE=5` controls training sampling, not inference update frequency (`tracker/ostrack.py:252-256`; `lib/config/ostrack/config.py:116-125`).
- **CODE FACT — inspected:** online boxes are CPU-side. There is no confidence filter, missing-frame rule, presence state or visibility gate on updates.
- **CODE FACT — inspected:** state is bounded at 30 boxes and does not grow with sequence length. No historic images or encoded features are stored.
- **CODE FACT — inspected:** training trajectory data are separate external per-sequence `.txt` files under `traj_data/{lasot,got10k,tn}` (`README.md:24-32`; `lib/train/dataset/lasot.py:38-40,106-119`; `got10k.py:108-112`; `tracking_net.py:111-115`).
- **CODE FACT — inspected:** training selects a sparse stride uniformly from one through five, can use a reversed future window or preceding window, and left-pads short histories with the earliest available box (`sampler_prompt.py:151-174`; `lasot.py:169-217`; analogous GOT-10k `:181-228` and TrackingNet `:143-187`).
- **RESOURCE AVAILABILITY FACT:** trajectory files are external and absent from the repository; no trajectory-generation script was found.

### E. Motion encoder, fusion, and dynamic computation

- **CODE FACT — inspected:** the 30 xyxy boxes become 60 corner tokens. Three learned representative tokens (weight, top-left, bottom-right) are prepended, yielding 63 tokens at width 768 (`lib/models/ostrack/prompt.py:108-119,203-228`).
- **CODE FACT — inspected:** code instantiates random-Fourier spatial coordinate encoding, learned TL/BR type embeddings, a learned temporal table `tpe`, and a sinusoid-initialized 30-position parameter (`prompt.py:36-79,108-132,136-147`). Under released `PELOG=-5`, executed box encoding adds spatial, type and sinusoidal position terms; the learned `tpe` table is instantiated but not added (`:203-228`).
- **CODE FACT — inspected:** each of two decoder blocks runs prompt self-attention, prompt-to-image cross-attention, a 768→1024→768 MLP, and image-to-token cross-attention using only the first three representative tokens (`transformer_prompt_weight.py:57-67,164-196`). Search-side sequence is 256 tokens for MAE256 and 576 for MAE384.
- **CODE FACT — inspected:** the adaptive scalar comes from an unsquashed 768→256→1 MLP. It is expanded spatially and used exactly as `(1-w) * original + w * decoded`; it is not a binary route (`prompt.py:261-263`; `ostrack_prompt.py:81-86`).
- **CODE FACT — inspected:** the 768→256→2 token head executes during inference, but its `token_pred` does not affect the final inference bbox. The inference return instead exposes `token_feats` from `w_value`; the fused feature goes to the CENTER head (`prompt.py:258-300`; `ostrack_prompt.py:100-126`).
- **CODE FACT — inspected:** no conditional skip/routing branch exists in released OSTrack+MPT inference. Host, prompt encoder, both two-way blocks, token head, weight head and CENTER head execute every frame.
- **ENGINEERING TARGET TO PROFILE:** measure 63-token self-attention, cross-attention against 256/576 search tokens, 30 CPU transforms/transfer and the always-executed token head independently. This identifies sites only.

### F. Training evidence

| Property | Both released OSTrack+MPT configs |
|---|---|
| Training datasets | LaSOT, GOT10K-vottrain, TrackingNet at ratios 1:0.5:0.5; 60,000 samples/epoch |
| Validation | LaSOT test; 10,000 samples |
| Epochs / batch / workers | 60 / 128 per loader process / 10 |
| Optimizer | AdamW; LR 4e-4; weight decay 1e-4; StepLR drop 40; gradient clip 0.1 |
| Precision/memory helpers | AMP false; no BF16, activation checkpointing or accumulation found |
| Host policy | full OSTrack host frozen; optimizer selects parameter names containing `prompt` |

Evidence: both YAML train/data blocks; `lib/train/base_functions.py:156-235,253-317`; `lib/train/train_script_prompt.py:47-89`.

- **RESOURCE AVAILABILITY FACT:** `eval.sh:3-5` launches two distributed processes. A `--mode single` branch also exists and uses CUDA 0 without DDP (`tracking/train.py:15-17,39-60`; `train_script_prompt.py:59-66`). Neither establishes single-GPU memory fit at batch 128.
- **CODE FACT — inspected:** training still runs the frozen host. It runs the fused head and additionally runs the unfused visual head under `torch.no_grad()` for training targets/logging (`ostrack_prompt.py:100-112`).
- **CODE FACT — inspected:** the actor uses GIoU, L1, focal and MSE prompt-confidence losses; both released YAMLs enable token loss (`train_script_prompt.py:70-76`; `actors/ostrack_prompt.py:94-196`).
- **CODE FACT — inspected:** precomputed trajectory quality is compared with ground truth; low-quality/invisible trajectory samples are masked in prompt-box losses at `traj_filter=0.5` (`processing_prompt.py:249-267`; actor `:141-196`).
- **CODE FACT — inspected:** training data depend on external predicted trajectory files and an external pretrained OSTrack host checkpoint.

### G. Profiling and export evidence

- **RESOURCE AVAILABILITY FACT:** `tracking/profile_model.py` exists but ignores its defined parser and hard-codes configuration `prompt_reptoken_weight_384_3data_v4-log-5`, whose YAML is absent (`:18-28,123-133`). It is not runnable against a released config without source editing.
- **CODE FACT — inspected:** the intended prompt path feeds template, search and synthetic 30-box prompt into the complete host+MPT model for THOP and timing (`:63-86,138-158`). It includes repeated template encoding, host, MPT and CENTER head.
- **CODE FACT — inspected:** it is model-only: crop/normalization, Python trajectory conversion/FIFO, device transfer, Hann window, map-back and clipping are excluded.
- **CODE FACT — inspected:** timing synchronizes before warm-up and after the timed loop, but not between completion of warm-up and `start=time.time()` (`:71-84`). It neither calls `model.eval()` nor loads a trained checkpoint.
- **ENGINEERING TARGET TO PROFILE:** confirm THOP coverage of raw `@` attention matmuls and softmax because `custom_ops=None` (`profile_model.py:63-69`).
- **RESOURCE AVAILABILITY FACT:** no MPT ONNX, TensorRT, TorchScript or `torch.compile` exporter and no `.cu`/`.cpp` custom extension were found. Generic inherited ONNX/JIT helpers do not constitute an MPT export path.
- **CODE FACT — inspected:** model operations are standard PyTorch Linear, LayerNorm, activation, matmul, softmax, reshape, repeat/expand, sin/cos and convolutional CENTER-head operations. End-to-end control still includes a Python list comprehension, FIFO mutation, CPU→GPU trajectory copy and output `.tolist()` (`tracker/ostrack.py:129-147,169-172,254-256`).
- **ENGINEERING TARGET TO PROFILE:** deployment cost must include the full OSTrack host and controller, not only the 13.057M MPT subtotal.

### H. HG4 evidence package — no decision

- **RESOURCE AVAILABILITY FACT:** exact pinned source, two OSTrack configs, training actor/evaluator and external data/model links exist.
- **RESOURCE AVAILABILITY FACT:** SeqTrack/ARTrack implementations and exact per-model checkpoint identities are absent.
- **CODE FACT — inspected:** MPT_MAE256 is the explicit example integration; MPT_MAE384 has a config but no separate command wrapper.
- **CODE FACT — inspected:** `eval.sh:8` passes `--dataset`, while the pinned `tracking/test.py:43` accepts `--dataset_name`; the supplied evaluation command therefore needs reconciliation.
- **OPEN QUESTION:** identities and availability of the five trained checkpoints behind the undifferentiated external link remain unverified.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

- **CODE FACT — inspected:** total inference retains complete ViT-B OSTrack, CENTER head and 13.057M MPT parameters.
- **CODE FACT — inspected:** raw template encoding, fixed 30-box controller and both fusion blocks run every frame; state does not grow and there is no conditional compute.
- **RESOURCE AVAILABILITY FACT:** no working released profiler configuration and no deployment export pipeline exist.
- **ENGINEERING TARGET TO PROFILE:** measure full host+MPT model, preprocessing, trajectory conversion/update/transfer and postprocessing under one synchronized device boundary.

**HG5 = PENDING**

### J. Code-visible cost sites

| Label | Site |
|---|---|
| CODE FACT — inspected | full OSTrack ViT-B processes raw template and search every frame |
| CODE FACT — inspected | two MPT attention blocks execute over 63 prompt tokens and 256/576 search tokens every frame |
| CODE FACT — inspected | token and weight heads both execute although final inference does not consume `token_pred` |
| CODE FACT — inspected | 30 CPU bbox transforms, stacking and device transfer occur every frame |
| CODE FACT — inspected | output `.tolist()` and Python FIFO mutation occur every frame |
| ENGINEERING TARGET TO PROFILE | isolate host, prompt encoder/decoder, token/weight heads, CENTER head, trajectory controller and complete pre/postprocessing without interpreting a site as confirmed redundancy |

### K. Unresolved items

1. SeqTrack-B256, SeqTrack-L384 and ARTrack-B256 integration boundaries, recipes and checkpoints: **NOT FOUND**.
2. Exact checkpoint filenames, hashes and contents behind the generic external link: **OPEN QUESTION**.
3. Exact total host+MPT parameters/MACs and measured speed under a working profiler: **PENDING**.
4. Paper terminology for “three positional encodings” versus the active `PELOG=-5` code branch: **OPEN QUESTION**; instantiated and executed terms are mapped above without guessing terminology.
5. ONNX/TensorRT compatibility of complete model plus controller: **PENDING**.
6. Single-GPU peak training memory and batch-128 feasibility: **PENDING**.
7. Intended correction for the supplied evaluation CLI option: **OPEN QUESTION**.

## 6. Cross-candidate repository anomalies and locked next state

This section records availability/code anomalies only. It does not compare candidate promise or make a gate decision.

| Candidate | Evidence item |
|---|---|
| CX053 UncTrack | **CODE FACT — inspected:** active online tracker has invalid U+FF09 syntax at line 159; official shell and Drive checkpoint filenames differ; named Large GOT artifact/config was not found |
| CX058 HiT-DyHiT | **CODE FACT — inspected:** static tracker/profiler/export calls omit mandatory routing arguments; ONNX checkpoint prefix conflicts with train/test; DyHiT weight paths are empty; released Stage-2 threshold is Route1-only |
| CX125 MPT | **RESOURCE AVAILABILITY FACT:** pinned code covers OSTrack only despite five reported integrations; profiler hard-codes an absent YAML; example evaluator uses an unsupported CLI option |

Final locked state:

- CX053 UncTrack code audit: **COMPLETE**
- CX058 HiT-DyHiT code audit: **COMPLETE**
- CX125 MPT code audit: **COMPLETE**
- Batch D code evidence extraction: **COMPLETE**
- HG4 decisions: **NOT MADE**; every candidate remains **PENDING**
- HG5 decisions: **NOT MADE**; every candidate remains **PENDING**
- HG6: **NOT STARTED**
- Soft scoring: **NOT STARTED**
- Primary shortlist: **NONE**
- Main baseline: **NONE**
- Proposed architecture: **NONE**

This is the final systematic evidence batch. No targeted profiling, reproduction, scoring, or later-stage work is activated by this report.
