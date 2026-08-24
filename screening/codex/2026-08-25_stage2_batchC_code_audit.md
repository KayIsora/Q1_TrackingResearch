# Stage 2A — Batch C code / engineering evidence audit

Date: **2026-08-25**

Lane: **Codex worker — code and engineering audit**

Stage: **Stage 2A, Batch C evidence extraction only**

## 1. Scope, evidence labels, and stopping boundary

This report records implementation evidence for the only three active Batch C candidates:

- CX043 — SUTrack
- CX044 — AsymTrack
- CX049 — SPMTrack

CX040 MambaLCT remains HG3 FAIL. CX046 JDTrack remains HG3 PENDING. Neither was audited or activated here. These three active candidates remain members of the reconciled scientific-audit queue; they are **not a shortlist**.

Every repository was inspected in an isolated checkout at the exact full SHA registered in the project source manifest. File and line references below refer to those pinned trees. The Manager scientific interpretation file `screening/manager/2026-08-25_stage2_batchC_scientific_audit.md` was deliberately not read before this independent report was completed.

Evidence labels:

- **CODE FACT — inspected:** directly visible in the pinned implementation/configuration, or an exact quantity reconstructed from those constructors.
- **RESOURCE AVAILABILITY FACT:** directly visible release, checkpoint, script, or tool availability.
- **ENGINEERING TARGET TO PROFILE:** a code-visible execution site whose measured cost remains unknown.
- **OPEN QUESTION:** evidence not found or an implementation ambiguity not resolved by inspection.

No training, benchmark reproduction, checkpoint execution, model export, TensorRT build, RTX 3060 fit test, or Jetson Nano benchmark was performed. This report does not decide HG4 or HG5. It does not begin HG6, assign S1–S7, calculate a score, rank candidates, form a shortlist, select a baseline, or design an architecture. The canonical matrix was not modified, and Batch D was not activated.

## 2. Completion and stage guard

| Candidate | Exact pinned source inspected | Required A–K fields | Code-audit state | HG4 | HG5 |
|---|---:|---:|---:|---:|---:|
| CX043 SUTrack | yes | complete | complete | PENDING | PENDING |
| CX044 AsymTrack | yes | complete | complete | PENDING | PENDING |
| CX049 SPMTrack | yes | complete | complete | PENDING | PENDING |

“Complete” means that the requested code-evidence fields were inspected and unresolved items were explicitly retained. It does not mean successful reproduction, deployment feasibility, or a gate decision.

## 3. CX043 — SUTrack

### A. Provenance and audited variants

- **ID:** CX043
- **Official repository:** `chenxin-dlut/SUTrack`
- **Pinned full SHA:** `d65052d1ba3fcf55010e1fb3665ee6616c139a2c`
- **Registered official code source:** [R38](../../references/references.md#r38)
- **Released configurations:** `experiments/sutrack/sutrack_t224.yaml`, `sutrack_b224.yaml`, `sutrack_b384.yaml`, `sutrack_l224.yaml`, and `sutrack_l384.yaml`.
- **Checkpoint convention used by the tester:** `checkpoints/train/sutrack/<yaml-name>/SUTRACK_ep0180.pth.tar` (`lib/test/parameter/sutrack.py:7-26`).

**RESOURCE AVAILABILITY FACT:** the official Hugging Face release linked by the repository contains all five corresponding checkpoint paths. `MODEL_ZOO.md:111-125`, however, documents `b256/l256` directories and omits T224. The released YAML names, tester convention, and external checkpoint tree agree on `b224/l224`, not `b256/l256`. This is a repository-documentation anomaly, not a new checkpoint family.

### B. Model construction and variant mapping

The construction chain is `build_sutrack` → Fast-iTPN encoder → CENTER decoder, with a complete CLIP model and a three-layer task-recognition MLP also instantiated (`lib/models/sutrack/sutrack.py:123-140`; `encoder.py:46-73`; `decoder.py:327-356`; `task_decoder.py:6-24`). All released Fast-iTPN factories use a six-channel input projection and patch size 16 (`fastitpn.py:1114-1178`).

| Variant | Encoder construction | Input geometry | Templates at test | Main-attention tokens | Fast-iTPN pretrain | Tracker checkpoint |
|---|---|---|---:|---:|---|---|
| T224 | `fastitpnt`; width 384; stage depths 1/1/12; 6 heads | template 112, search 224 | 1 | 247 = class 1 + search 196 + template 49 + text 1 | `pretrained/itpn/fast_itpn_tiny_1600e_1k.pt` | `.../sutrack_t224/SUTRACK_ep0180.pth.tar` |
| B224 | `fastitpnb`; width 512; depths 3/3/24; 8 heads | 112 / 224 | 2 | 296 = 1 + 196 + 2×49 + 1 | `pretrained/itpn/fast_itpn_base_clipl_e1600.pt` | `.../sutrack_b224/SUTRACK_ep0180.pth.tar` |
| B384 | same B encoder | 192 / 384 | 2 | 866 = 1 + 576 + 2×144 + 1 | same | `.../sutrack_b384/SUTRACK_ep0180.pth.tar` |
| L224 | `fastitpnl`; width 768; depths 2/2/40; 12 heads | 112 / 224 | 2 | 296 | `pretrained/itpn/fast_itpn_large_1600e_1k.pt` | `.../sutrack_l224/SUTRACK_ep0180.pth.tar` |
| L384 | same L encoder | 192 / 384 | 2 | 866 | same | `.../sutrack_l384/SUTRACK_ep0180.pth.tar` |

Evidence: `fastitpn.py:1000-1029,1114-1179`; the five YAMLs’ `DATA.TEMPLATE` and `DATA.SEARCH` fields; B/L YAML test-template overrides; and the T224 inherited `TEST.NUM_TEMPLATES=1` default at `lib/config/sutrack/config.py:130`.

**CODE FACT — inspected:** exact constructor-derived parameter subtotals for the Fast-iTPN encoder, CENTER head, and task head are 27,845,482 (T224), 89,248,522 (B224), 89,491,722 (B384), 318,036,298 (L224), and 318,401,098 (L384). These are deliberately **not** labeled full deployed-model totals: every released build also instantiates the external `clip.load('ViT-L/14')` object, whose parameters are not included in those subtotals (`lib/models/sutrack/clip.py:6-30`).

The CENTER head has independent center-score, offset, and size Conv/BN/ReLU towers at channel width 256 (`decoder.py:132-168,214-240`). The task head maps encoder width → 256 → 256 → five classes (`task_decoder.py:6-24`).

### C. Pure-RGB runtime graph

| Component | Execution frequency | Main input/output | Persistent state | Code evidence |
|---|---:|---|---|---|
| Model/checkpoint construction | once per tracker | config + checkpoint → complete SUTrack, CLIP, task head, Hann window | resident model and window | `lib/test/tracker/sutrack.py:14-29` |
| Initial RGB template crop | once | RGB frame+bbox → normalized 3-channel crop → literal RGB∥RGB six-channel tensor | one template for T; two references to initial template for B/L | `tracker/sutrack.py:80-99` |
| Text encoding | once at initialization | 77 zero token IDs for ordinary RGB datasets → one projected text token | cached `text_src` | `tracker/sutrack.py:100-111,208-215`; `clip.py:20-26` |
| Search crop and RGB duplication | every frame | prior-box-centered RGB crop → normalized RGB∥RGB six-channel tensor | latest bbox | `tracker/sutrack.py:114-122` |
| Template/search early encoding | every frame | every raw template plus search → patch tokens through early Fast-iTPN stages | none encoded | `fastitpn.py:963-1018` |
| Token indicators and joint encoder | every frame | search/template foreground/background indicators + cached text + class token → joint attention sequence | fixed learned embeddings | `fastitpn.py:975-1049` |
| CENTER prediction | every frame | search tokens → center, size, offset maps and decoded box | none | `sutrack.py:66-97`; `decoder.py:175-201` |
| Tracker postprocess | every frame | Hann-window score and box maps → Python bbox, map/clip | new bbox/frame counter | `tracker/sutrack.py:132-175` |

#### Pure-RGB modality behavior

**CODE FACT — inspected:** all released YAMLs set multimodal vision on by default, while the visual patch projection is fixed at six channels. The normal RGB tracker therefore constructs its second visual input by literal channel duplication, `torch.cat((rgb, rgb), axis=1)`, for template and search (`tracker/sutrack.py:87-89,120-122`). The pretrained three-channel patch kernel is copied into both halves and divided by two (`fastitpn.py:1097-1111`). This statement describes the executed channel construction; it does not label it redundant.

Depth, Thermal, and Event dataset loaders are separate and are not invoked by an RGB dataset run. There are no separate sensor-specific encoders in the active model path; the unified visual representation enters one six-channel patch projection.

**CODE FACT — inspected:** all released YAMLs also enable multimodal language construction. For an RGB dataset whose `USE_NLP` flag is false, initialization still creates 77 zero token IDs and runs the CLIP text encoder once. Its projected one-token result is cached and concatenated into every frame’s main attention sequence. The complete CLIP model remains resident even though `encode_text` is only used at initialization.

#### Task-recognition mechanism

**CODE FACT — inspected:** task recognition is a training path, not an executed released-tracker inference path.

- The task feature is the mean of encoder tokens and the task MLP produces five logits (`sutrack.py:110-121`; `task_decoder.py:6-24`).
- The training actor calls both the tracking decoder and task decoder and applies cross-entropy task loss on every batch (`lib/train/actors/sutrack.py:47-68,96-109`).
- The released tracker calls `network.forward_decoder(feature=enc_opt)` directly and never calls `forward_task_decoder` (`lib/test/tracker/sutrack.py:132-135`).
- `task_index_batch=None` is passed into inference encoding, but the active Fast-iTPN body does not consume `task_index` (`fastitpn.py:963-1049`).

Therefore the task classifier is instantiated and resident, but no task classifier, task token, task routing, or task-conditioned branch executes during released tracker inference. Token-type embeddings do execute, but they mark search and template foreground/background roles, not the recognized task or sensor modality.

### D. Template, temporal, and memory behavior

**CODE FACT — inspected:** SUTrack does not cache encoded template features. On every tracked frame it stacks the active raw template tensors, repeats their patch embedding and early Fast-iTPN blocks, and then includes their tokens in the joint encoder (`tracker/sutrack.py:126-130`; `fastitpn.py:969-1049`).

- T224 keeps one static initial template. The update block is bypassed because its test template count is one.
- B224/B384/L224/L384 keep exactly two active templates: the fixed initial template and one replaceable dynamic slot.
- Every 25 frames, the dynamic slot is replaced only if the Hann-window-derived confidence exceeds 0.70. The list update appends the new crop and removes index 1, preserving a constant list length (`tracker/sutrack.py:155-175`; B/L YAML test settings).
- Persistent state is bounded: template tensor/annotation lists, one cached text token, the latest bbox, and a frame counter. No growing feature history or unbounded temporal memory is present.

### E. Dynamic computation

**CODE FACT — inspected:** there is no MoE, sparse expert routing, task routing, confidence-controlled backbone block, or conditional modality branch in released RGB inference. Joint token count is fixed by variant and template count. The input-dependent operations are box-map argmax/gather and the interval-plus-confidence decision that replaces the dynamic raw template.

The second visual input is not cleanly bypassed for RGB because the six-channel patch projection remains active on duplicated RGB channels. CLIP text encoding is one-time; the cached text token participates every frame. Task recognition is cleanly bypassed at inference even though its parameters remain instantiated.

### F. Training evidence

All five released YAMLs use the same unified nine-dataset recipe:

| Dataset group | Released names | Sampling ratios |
|---|---|---:|
| RGB/general tracking | LaSOT, GOT10K_vottrain, COCO17, TrackingNet, VastTrack, TNL2K_train | 4 each |
| multimodal tracking | DepthTrack_train, VisEvent, LasHeR_train | 2 each |

The recipe uses 100,000 samples per epoch. No released RGB-only YAML or RGB-only recipe was found.

| Training property | Released value / path |
|---|---|
| Epochs | 180 |
| Batch | 32 per loader process; README launches four processes, nominal aggregate 128 |
| Frames/sample | T: one template + one search; B/L: two templates + one search |
| Optimizer | AdamW, LR `1e-4`, weight decay `1e-4` |
| Encoder LR | multiplier 0.1 |
| Schedule | StepLR drop at epoch 144 |
| Gradient clipping | 0.1 |
| Launch paths | README four-process launcher and explicit single-GPU launcher (`README.md:179-198`; `tracking/train.py:28-40`) |

**CODE FACT — inspected:** the Fast-iTPN encoder is not frozen. `TRAIN.TYPE=text_frozen` excludes CLIP/BERT weights from training, while Fast-iTPN, tracking decoder, task decoder, token/text projection parameters, and their configured optimizer groups remain active (`config.py:55-79`; `base_functions.py:288-320`).

The encoder builder passes the configured pretrain type and enables pretrained loading on the main process, after which distributed synchronization supplies the remaining processes (`encoder.py:46-63`; `fastitpn.py:1125-1127,1159-1161,1176-1178`). YAML comments saying the pretrain type is “not activated for now” conflict with the executed builder and are treated as stale documentation.

Training normalizes each three-channel half of the six-channel tensor with the same RGB mean/std and concatenates them again (`lib/train/data/transforms.py:243-262`). The task MLP and task cross-entropy are active during training; `task_index` does not select conditional encoder computation.

AMP infrastructure exists, but the released YAMLs do not set `TRAIN.AMP`; the trainer default is false (`train_script.py:77-80`; `ltr_trainer.py:40-92`). Fast-iTPN contains checkpointing support, but the active builder hard-codes `grad_ckpt=False` (`encoder.py:46-63`; `fastitpn.py:996-1037`). No gradient-accumulation path was found; the trainer zeros, backpropagates, and steps each batch.

### G. Profiling and export evidence

**RESOURCE AVAILABILITY FACT:** no dedicated SUTrack profiling/FLOPs script was found. `install.sh` installs THOP, but no `thop.profile` invocation occurs in the pinned tree.

The generic evaluator uses `time.time()` around `initialize()` and `track()` after image disk read (`lib/test/evaluation/tracker.py:75-88,118-145`). This boundary includes crop/preprocessing, model execution, postprocessing, and any template update; model/checkpoint construction is outside. Initialization timing includes one-time CLIP text encoding. There is no explicit CUDA synchronization. GPU scalar comparison and `.tolist()` may introduce implicit synchronization, but they do not establish a controlled timing protocol.

**RESOURCE AVAILABILITY FACT:** README reports 23 CPU FPS and 34 AGX FPS for T224 (`README.md:45-52`), but the pinned release provides no matching AGX script, precision setting, device mode, synchronization method, or indication whether that number is PyTorch or TensorRT. Desktop/AGX FPS is not Jetson Nano FPS.

No SUTrack ONNX, TensorRT/Torch-TensorRT, TorchScript, or `torch.compile` exporter was found. A generic ONNX helper in `lib/utils/misc.py` is not wired to SUTrack. No SUTrack `.cu`/`.cpp` custom extension was found. The released tracker uses hard-CUDA PyTorch placement.

**RESOURCE AVAILABILITY FACT:** `install.sh:1-2,86-87,106-107` pins PyTorch 1.11.0+cu113 and timm 0.5.4, but installs OpenAI CLIP directly from GitHub without a commit pin. This records dependency provenance only; compatibility with a current environment was not tested.

### H. HG4 evidence package — no decision

Evidence available for Manager reconciliation:

- five exact configs and five matching external checkpoints are available;
- the unified nine-dataset recipe, 180 epochs, process batch, optimizer, pretrains, and a single-GPU command are code-visible;
- no RGB-only training recipe, peak-memory trace, or single-RTX-3060 reproduction is released;
- the complete CLIP-L/14 object is resident and the full model total was not established by the local subtotal;
- checkpoint directory documentation and pretrain comments contain inconsistencies.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

Evidence available for Manager reconciliation:

- T224 is the smallest released graph, but its RGB input remains six-channel and its complete CLIP object remains resident;
- raw templates are re-encoded every frame, and B/L jointly attend over two templates;
- task-recognition compute is absent at inference, while language encoding is once per initialization;
- the release is hard-CUDA PyTorch and contains no validated export/TensorRT path;
- the README AGX figure lacks an executable measurement protocol and does not establish Nano behavior.

**HG5 = PENDING**

### J. Code-visible cost sites

| Label | Site |
|---|---|
| CODE FACT — inspected | full CLIP-L/14 object is resident; zero-text encoding executes once and its projected token is used every frame |
| CODE FACT — inspected | RGB template/search are literally duplicated to six channels and processed by a six-channel patch projection |
| CODE FACT — inspected | every active raw template repeats patch embedding and early Fast-iTPN processing every frame |
| CODE FACT — inspected | joint attention lengths are 247 (T224), 296 (B/L224), and 866 (B/L384) |
| ENGINEERING TARGET TO PROFILE | model residency with exact external CLIP revision and tracker checkpoint |
| ENGINEERING TARGET TO PROFILE | repeated template early stages versus joint main blocks, separately |
| ENGINEERING TARGET TO PROFILE | three CENTER towers and the head/tracker’s repeated box decoding |
| ENGINEERING TARGET TO PROFILE | RGB duplication, token-mask construction, periodic template crop, scalar branch, and `.tolist()` host synchronization |

### K. Unresolved items

1. Exact full parameter count and residency including the externally instantiated CLIP model: **PENDING**.
2. Exact OpenAI CLIP package revision: **NOT PINNED** by the installer.
3. Official AGX/CPU timing boundary, precision, power mode, synchronization, and PyTorch-versus-TensorRT basis: **NOT FOUND**.
4. Whether reported speed includes initialization/text encoding and tracker pre/postprocessing: **OPEN QUESTION**.
5. Successful checkpoint reproduction and dependency compatibility: **NOT TESTED**.
6. Intended correction for the `MODEL_ZOO.md` b256/l256 paths and missing T entry: **OPEN QUESTION**.
7. End-to-end export, target-device latency, memory, power, and thermal behavior: **PENDING**.

## 4. CX044 — AsymTrack

### A. Provenance and audited variants

- **ID:** CX044
- **Official repository:** `jiawen-zhu/AsymTrack`
- **Pinned full SHA:** `a7b05e0c0d6116ccd7fa72270aa19053b7777204`
- **Registered official code source:** [R40](../../references/references.md#r40)
- **Released configurations:** `experiments/AsymTrack/tiny.yaml`, `small.yaml`, and `base.yaml`.
- **Checkpoint convention:** `checkpoints/train/AsymTrack/<config>/AsymTrack_ep%04d.pth.tar` (`lib/test/parameter/AsymTrack.py:24-27`).

**RESOURCE AVAILABILITY FACT:** README links official external Google Drive/Baidu folders for models/raw results and for the pretrained backbone. No tracker checkpoint is committed at the pinned SHA; `pretrained_model/.gitkeep` is the only tracked pretrained-model artifact. External checkpoint contents and hashes were not inspected in this audit.

### B. Model construction and variant mapping

`build_asymtrack` constructs EfficientMod-XXS, a `Linear(256,256)` neck, and a convolutional CORNER head (`lib/models/AsymTrack/asymtrack.py:104-125`; `neck.py:393-407`; `head.py:415-439`).

| Variant | Released config | Basic-block depths | Stage widths | Template / search | Final head map | Code-derived train graph | Fused inference graph |
|---|---|---:|---|---|---|---:|---:|
| AsymTrack-T | `tiny.yaml`, `3stage1` | 2/2/1 | 32/64/128, final downsample to 256 | 128 / 256 | 8×8×256 | 3,626,079 | 3,239,004 |
| AsymTrack-S | `small.yaml`, `3stage3` | 2/2/3 | same | 128 / 256 | 8×8×256 | 3,936,223 | 3,549,148 |
| AsymTrack-B | `base.yaml`, `3stage3` | 2/2/3 | same | 192 / 384 | 12×12×256 | 3,936,223 | 3,549,148 |

**CODE FACT — inspected:** widths, patch/downsample strides, and depth selection are in `lib/models/AsymTrack/EfficientMod.py:637-689,903-968`. An initial 7×7 stride-4 convolution followed by three stride-2 downsamples gives total stride 32. Small and Base have identical model parameters; Base changes spatial input size, not model depth/width. Counts above were reproduced from the exact constructors and again after the released OPE conversion; buffers are excluded and no tracker checkpoint is needed for the count.

Each of the three stages appends one OPE. Stages 1 and 2 append an ETM, and stage 2 also appends one relation AttentionBlock (`EfficientMod.py:398-418`). The CORNER head uses independent top-left and bottom-right convolution towers followed by spatial soft-argmax (`head.py:23-96`).

#### Checkpoint-epoch anomaly

Tiny and Base YAMLs specify test epoch 500; Small specifies 499. The parameter loader overwrites that field with its `num_epoch` argument, while the normal test CLI defaults to 500 (`lib/test/parameter/AsymTrack.py:24-27`; `tracking/test.py:15-16,49-50`). Therefore the normal Small command attempts epoch 500 unless `--num_epoch 499` is passed. Which external Small checkpoint produced the reported results remains an open artifact question.

### C. Runtime graph

| Component | Execution frequency | Main input/output | Persistent state | Code evidence |
|---|---:|---|---|---|
| Template crop/normalization | once in `initialize()` | RGB+bbox → `[1,3,128,128]` T/S or `[1,3,192,192]` B | raw normalized `self.template` | `lib/test/tracker/AsymTrack.py:34-46` |
| Template neural branch | once, on first `track()` | template through patch/stages | two ETM kernels + one attention-token cache | `AsymTrack.py:52-63`; `EfficientMod.py:702-726` |
| Search crop/normalization | every frame | prior-box-centered crop → 256 or 384 square | previous bbox | `lib/test/tracker/AsymTrack.py:52-58` |
| Search stages | every frame | search → intermediate/final maps | fixed template caches | `EfficientMod.py:702-727` |
| ETM stage 1 | every frame | search 32×32×64 T/S or 48×48×64 B + cached prototype | `[B,2,64]` kernel | `EfficientMod.py:455-472`; `tem_kernel.py:65-117` |
| ETM stage 2 | every frame | search 16×16×128 T/S or 24×24×128 B + cached prototype | `[B,4,128]` kernel | same |
| Relation attention | every frame | T/S 256 search + 64 template tokens, or B 576 + 144, width 128 | cached template tokens | `EfficientMod.py:155-185,446-476` |
| Linear neck + CORNER head | every frame | final 8×8 or 12×12 map → one normalized bbox | none | `asymtrack.py:52-93` |
| Map-back/clip | every frame | bbox tensor → Python list/full-image bbox | new `self.state` | `lib/test/tracker/AsymTrack.py:65-69,94-108` |

**CODE FACT — inspected:** the tracker’s `initialize()` comment says “forward the template once,” but that function only crops and stores the tensor. Template neural execution actually occurs with the first search frame. On that first network call, `tempinit=False` causes both template and search branches to execute; the backbone then sets `tempinit=True` (`EfficientMod.py:621-622,702-726`).

On later calls, template patch embedding, downsampling, ordinary blocks, OPE, and template self-attention are skipped. The tracker still places `self.template` in `images_list`, but the steady-state backbone does not consume its branch. Search processing, two ETMs using cached kernels, one relation-attention block using cached template tokens, neck, and head still execute every frame.

### D. Template, temporal, and memory behavior

Exact batch-1 persistent state after the first tracked frame:

| State | T/S shape | B shape | Nominal FP32 payload |
|---|---:|---:|---:|
| Raw normalized template | `[1,3,128,128]` | `[1,3,192,192]` | 192 KiB / 432 KiB |
| Stage-1 ETM kernels | `[1,2,64]` | `[1,2,64]` | 0.5 KiB |
| Stage-2 ETM kernels | `[1,4,128]` | `[1,4,128]` | 2 KiB |
| Relation-attention `fuselist[0]` | `[1,64,128]` | `[1,144,128]` | 32 KiB / 72 KiB |

ETM stores `kernels.detach().clone()` (`tem_kernel.py:98-104`), and the relation block stores flattened template tokens once (`EfficientMod.py:168-180`). Cache size is constant with sequence length.

No template update, confidence admission, frame-history list, temporal feature bank, motion model, presence output, or re-detection path was found. Persistent tracking state is the initial-template tensor/caches plus the immediately previous bbox.

**OPEN QUESTION:** calling `initialize()` again on the same live tracker object does not reset `backbone.tempinit`, `fuselist`, or ETM kernels. The benchmark path creates a fresh tracker/network for each sequence (`lib/test/evaluation/tracker.py:71-96`), but same-instance application reinitialization requires validation.

### E. Dynamic computation, ETM, and OPE

#### ETM

**CODE FACT — inspected:** two ETMs execute on every search frame after their one-time template-prototype initialization. Each ETM:

1. on the first tracked frame, projects the template from C to C/32, aggregates it with `einsum`, and caches `[B,C/32,C]` kernels;
2. on every frame, projects and spatially aggregates the current search feature;
3. generates input-dependent depthwise and pointwise 1-D convolution weights using the cached template kernels;
4. runs two functional `conv1d` operations inside a Python loop over batch;
5. correlates the result with the search projection;
6. forms a sigmoid prototype-attention vector; and
7. injects the normalized activated result into the search feature.

Evidence: `lib/models/AsymTrack/tem_kernel.py:45-62,96-117`.

The stage-2 relation block concatenates current search tokens with cached initial-template tokens, performs ordinary attention and MLP processing, then retains only the search positions (`EfficientMod.py:155-185`). This is input-dependent computation, but it is not MoE: there is no expert routing, sparse top-k dispatch, confidence gate, template-update route, or conditional block skipping. The graph-level phase branch is first-frame initialization versus steady-state search.

#### OPE re-parameterization

Training-form OPE contains three parallel bias-free 3×3 convolutions plus learned `theta`; its response subtracts a kernel-sum difference term before LayerNorm/ReLU/residual scaling (`lib/models/AsymTrack/ibe.py:47-79,115-141`). `switch_to_deploy()` folds those three branches and the difference term into one 3×3 convolution, then removes the training branches and `theta` (`ibe.py:91-114`).

The released inference sequence is precise:

1. test parameters set `TEST_MODE=True`;
2. the builder marks OPE as deploy mode, but its constructor’s literal `if False` still creates training-form branch keys;
3. the tracker strictly loads the unreparameterized checkpoint; and
4. only after loading, `network.backbone.switch_to_deploy()` fuses OPE in memory (`lib/test/parameter/AsymTrack.py:32-33`; `backbone.py:104-113`; `lib/test/tracker/AsymTrack.py:17-24`).

Thus the released runtime expects a training-form checkpoint and executes fused OPE afterward. An already-fused checkpoint would not match the pre-conversion strict-load object. `switch_to_deploy()` does not set `self.deploy=True` itself and relies on the test-mode constructor; using it on a training-built model is not established as a supported conversion path.

### F. Training evidence

| Property | AsymTrack-T | AsymTrack-S | AsymTrack-B |
|---|---|---|---|
| Training datasets | LaSOT only; other three entries are commented out | LaSOT, GOT10K_vottrain, COCO17, TrackingNet | same four |
| Ratios | 1 | 1/1/1/1 | 1/1/1/1 |
| Samples/epoch | 60,000 | 60,000 | 60,000 |
| Epochs | 500 | 500 | 500 |
| Batch/process | 64 | 64 | 4 |
| Backbone LR multiplier | 0.1 | 1.0 | 0.1 |
| Template/search | 128/256 | 128/256 | 192/384 |

All variant configs and dataloader construction define GOT10K_votval with 10,000 validation samples, one template and one search frame, causal sampling, and maximum interval 200 (`lib/config/AsymTrack/config.py:60-85`; `base_functions.py:83-148`). The active training script nevertheless passes only `[loader_train]` into `LTRTrainer`; the constructed validation loader is not executed by that trainer path (`lib/train/train_script.py:45-50,91-97`).

The optimizer is AdamW at LR `4e-4`, weight decay `1e-4`, StepLR at epoch 400, and gradient clip 0.1. README demonstrates a two-process launcher for Base, yielding nominal Base aggregate batch 8, and an explicit single-GPU path with batch 4. Applying the same two-process pattern to T/S would arithmetically yield 128, but variant-specific T/S launch commands are not separately documented (`README.md:90-100`).

The external EfficientMod-XXS pretrain is expected at `pretrained_model/efficientMod/xxs/model_best.pth.tar`. Tiny performs partial loading; Small/Base perform partial then general non-strict loading (`EfficientMod.py:943-967`). All active model parameters default to trainable, and optimizer groups cover backbone and non-backbone parameters (`base_functions.py:222-239`).

`FREEZE_BACKBONE_BN: true` exists in the YAMLs, but no active use of that setting was found in the actual EfficientMod construction/training path. AMP support exists but the released YAMLs omit `TRAIN.AMP`, so it defaults false (`train_script.py:91-94`; `ltr_trainer.py:41-90`). No activation checkpointing or gradient accumulation was found; optimization steps every iteration. The single-GPU entrypoint is explicitly documented and implemented.

### G. Profiling and export evidence

`tracking/profile_model_asymtrack.py` can select any released config; README only demonstrates `tiny` (`README.md:119-122`). It builds random tensors without a tracker checkpoint, switches OPE to deploy, uses batch 1, and runs on CUDA (`profile_model_asymtrack.py:102-149`).

Profiler boundaries and anomalies:

- The explicit call before `evaluate()` initializes the template caches. Timed loops then pass `train=False`, so reported speed is steady-state model-only search+head and excludes first-frame template encoding.
- Crop/resize, normalization, transfer, bbox map-back/clip, and evaluator overhead are excluded.
- Timing uses 100 warmups and 1,000 loops but `time.time()` without `torch.cuda.synchronize()` before/after measured regions (`profile_model_asymtrack.py:67-100`). It is not a synchronized GPU latency protocol.
- THOP’s backbone call omits the sixth `train` argument. `AsymTrack.forward` therefore uses its default `train=True`, causing MAC profiling to process both search and template even though speed timing uses steady-state `train=False` (`profile_model_asymtrack.py:50-58`; `asymtrack.py:39-43`). MAC and speed do not represent the same graph.
- A MultiheadAttention handler is defined but never supplied to THOP. Active attention is custom; ETM uses functional `einsum` and `conv1d`. Their coverage requires validation.
- `overall params` adds outputs from separate backbone/head THOP calls rather than directly counting unique parameters.

No AsymTrack ONNX exporter, TensorRT path, TorchScript exporter, `torch.compile`, custom CUDA extension, Triton, explicit Flash-Attention integration, or xFormers path was found. Under the pinned PyTorch 1.12.1 environment, the active attention implementation uses its explicit QK-matmul/softmax/value-matmul fallback. The same source can conditionally call `scaled_dot_product_attention` on a newer PyTorch (`EfficientMod.py:81,96-106`), whose backend selection would require separate validation. `tracking/video_demo.py` is inherited HiT code that consumes an existing ONNX file, imports the absent `lib.models.HiT`, and hard-codes 128/256 inputs; it is not an AsymTrack exporter or validated AsymTrack runtime at this SHA.

The active graph uses Conv/Linear/LayerNorm/softmax, concatenation/slicing, `einsum`, input-dependent functional `conv1d`, and a Python loop over batch. Tracker/preprocessor/head code contains hard `.cuda()` placement and `.tolist()` synchronization.

### H. HG4 evidence package — no decision

Evidence available for Manager reconciliation:

- exact datasets, 500 epochs, process batches, optimizer, pretrain, and single-GPU entrypoint are visible;
- Tiny uses LaSOT only, whereas Small/Base use four datasets;
- the complete model is trainable; released configs disable AMP by omission and expose no checkpointing/accumulation;
- the official external artifacts, memory logs, and RTX 3060 fit were not reproduced;
- the published speed/FLOPs path is not a synchronized, graph-consistent end-to-end measurement.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

Evidence available for Manager reconciliation:

- fused graphs contain 3.239M parameters (T) or 3.549M (S/B), and template neural processing is once per sequence with bounded caches;
- every steady-state frame still executes two ETMs, dynamic functional convolutions/einsums, relation attention over 320 tokens (T/S) or 720 tokens (B), and a dual-tower head;
- hard CUDA placement and no validated AsymTrack export path remain;
- no synchronized end-to-end device measurement or Jetson Nano result is released.

**HG5 = PENDING**

### J. Code-visible cost and attribute sites

| Label | Site |
|---|---|
| CODE FACT — inspected | template neural processing occurs on first `track()`, then bounded ETM/attention caches are reused |
| CODE FACT — inspected | final response maps are 8×8 for T/S and 12×12 for B at total stride 32 |
| ENGINEERING TARGET TO PROFILE | two ETMs’ `einsum`, dynamically generated functional `conv1d`, and Python batch loop |
| ENGINEERING TARGET TO PROFILE | final attention over 320 tokens for T/S and 720 for B |
| ENGINEERING TARGET TO PROFILE | two CORNER towers and spatial soft-argmax |
| ENGINEERING TARGET TO PROFILE | CPU OpenCV crop/resize, tensor construction/transfer, map-back/clip, and `.tolist()` |

Attribute-stratification observations, without a causal claim:

- low-resolution target: code produces an 8×8 head map for T/S and 12×12 for B;
- viewpoint-change target: the initial-template caches remain fixed and there is no template update or appearance history;
- fast-motion target: the factor-4 search crop is centered on the previous predicted bbox, with no motion predictor, enlarged recovery search, confidence gate, or re-detection branch.

These are code-visible mechanisms to test; they are not established explanations of a measured benchmark weakness.

### K. Unresolved items

1. External T/S/B tracker checkpoint filenames, keys, hashes, and continued availability: **NOT VERIFIED**.
2. Small YAML epoch 499 versus ordinary CLI epoch 500: **OPEN QUESTION**.
3. Published T/S/B speed/FLOP numbers’ exact invocation, hardware, software, and synchronization: **NOT FOUND**.
4. THOP coverage for custom attention, ETM `einsum`, and dynamic functional convolution: **PENDING**.
5. Same-instance reinitialization and template-cache reset behavior: **OPEN QUESTION**.
6. Stateful/dynamic graph exportability: **NOT VALIDATED**.
7. End-to-end RTX 3060 training fit and Jetson behavior: **NOT ESTABLISHED**.

## 5. CX049 — SPMTrack

### A. Provenance and audited variant

- **ID:** CX049
- **Official repository:** `WenRuiCai/SPMTrack`
- **Pinned full SHA:** `c581fe27231f3e16c38578e47daddadfaf6ffd7d`
- **Registered official code source:** [R44](../../references/references.md#r44)
- **Primary reproducible configuration:** `config/SPMTrack/dinov2/config.yaml`, named `DINOv2/B-378`.
- **Primary tracker checkpoint:** external SPMTrack-B weight; `eval.sh` expects `./spmtrack_base.bin`.

**RESOURCE AVAILABILITY FACT:** the repository does not contain tracker weights. README links an official external folder and marks only SPMTrack-B weights/training logs uploaded; L and G weights remain TODO (`README.md:27-37`). Training saves `.../checkpoint/epoch_{last}/model.bin` (`README.md:93-101`).

**CODE FACT — inspected:** the training model’s overridden `state_dict()` removes frozen parameters (`trackit/models/methods/SPMTrack/SPMTrack.py:114-123`). A tracker adapter checkpoint is therefore not a standalone copy of the complete DINOv2 backbone; the exact pretrained foundation weights remain part of reconstruction.

### B. Model construction and family mapping

`build_SPMTrack_model()` creates `SPMTrack_DINOv2` for training. With `optimize_for_inference=True`, it creates `SPMTrackBaseline_DINOv2` and later installs TMoE wrappers while loading state (`trackit/models/methods/SPMTrack/builder.py:14-40`; `SPMTrack_full_finetune.py:164-171`).

| Variant | Foundation backbone | Depth / width / heads | Released 378 checkpoint state |
|---|---|---|---|
| SPMTrack-B | DINOv2 ViT-B/14 | 12 / 768 / 12 | released externally |
| SPMTrack-L | DINOv2 ViT-L/14 | 24 / 1024 / 16 | not released at pinned README state |
| SPMTrack-G | DINOv2 ViT-g/14 with SwiGLU | 40 / 1536 / 24 | not released at pinned README state |

Evidence: `trackit/models/backbone/dinov2/builder.py:22-55`; `dinov2/__init__.py:358-398`; `config/SPMTrack/dinov2/mixin/{large,giant}.yaml`.

SPMTrack-B uses Meta’s exact `dinov2_vitb14_pretrain.pth` URL (`dinov2/builder.py:22-34`), template size 196×196, search size 378×378, and feature maps 14×14 and 27×27 (`config/SPMTrack/dinov2/config.yaml:1-18,24-43`). Per inference frame the concatenated transformer sequence is:

`one query + three × (14×14 = 196) template tokens + 729 search tokens = 1,318 tokens at width 768`.

The prediction head has independent three-layer MLP classification and four-coordinate regression branches over the 729 search tokens (`modules/head/mlp.py:37-83`).

**CODE FACT — inspected:** exact reconstruction from released constructors gives 115,330,565 total model parameters and 29,243,909 training parameters, leaving 86,086,656 frozen during training (25.36% trainable). This matches README’s rounded 115.3M/29.2M. The trainable total comprises 26,873,856 TMoE parameters, 2,366,213 head parameters, and 3,840 query/type embeddings. The arithmetic follows B’s depth/width (`dinov2/__init__.py:358-367`), rank/expert configuration (`config/SPMTrack/dinov2/config.yaml:33-41`), TMoE constructors (`modules/tmoe/__init__.py:9-39,93-143`), and head constructors (`modules/head/mlp.py:9-55`). The 29.2M figure is a training boundary, not an inference footprint.

### C. Runtime graph

| Component | Execution frequency | Main input/output | Persistent state | Code evidence |
|---|---:|---|---|---|
| Sequence initialization | once | initial curated 196×196 RGB template | initial CPU history entry and template cache | `one_stream/__init__.py:85-99` |
| Search crop/normalize | every frame | full RGB frame → 378×378 search | crop buffers and prior-box provider | `one_stream/__init__.py:101-136` |
| Reference selection/transfer | every frame | full CPU history → exactly three template tensors on device | growing CPU history | `one_stream/__init__.py:138-184` |
| Template/search patch embedding | every frame | three 196×196 references + one 378×378 search → 588 + 729 tokens | no encoded-template cache | `SPMTrack_full_finetune.py:73-85,144-155` |
| Query assembly | every frame | previous detached query + learned query + template/search tokens → `[B,1318,768]` | one `[1,768]` query per sequence | `SPMTrack_full_finetune.py:87-105` |
| DINOv2 + TMoE | every frame | all 1,318 tokens through 12 blocks | weights only | `SPMTrack_full_finetune.py:96-99,164-171` |
| Query/search modulation + head | every frame | 729 search tokens + query → score/box maps | updated detached query | `SPMTrack_full_finetune.py:101-110` |
| Postprocess and reference admission | every frame | score/box → confidence/full-image bbox and a new 196 crop | appended image/mask histories | `one_stream/__init__.py:186-285`; mask plugin `:108-117` |

**CODE FACT — inspected:** initialization stores image state but does not encode reusable template features. All three selected references are patch-embedded again on every tracking call. `init_eval()` allocates a per-sequence query dictionary; every forward replaces the query without a confidence gate (`SPMTrack_full_finetune.py:61-67,87-105`).

### D. Spatio-temporal reference and memory behavior

The released evaluator always supplies exactly three reference tensors:

- history length 1: initial/initial/initial;
- history length 2: initial/second/second;
- history length 3: all three;
- history length >3: initial plus two selected temporal positions.

Normally the two later positions are segment midpoints. For LaSOT with B-378, selection instead uses approximately one-third and two-thirds of the elapsed sequence (`one_stream/__init__.py:138-184`). The foreground-mask plugin mirrors the same reference choices (`template_foreground_indicating_mask_generation.py:90-106`).

**CODE FACT — inspected:** after every prediction, regardless of confidence or reference quality, the pipeline crops a new 196×196 template from the predicted box, normalizes it, and appends it to CPU history. The corresponding foreground mask is also appended (`one_stream/__init__.py:255-285`; mask plugin `:108-117`).

Active model input is bounded at three references, but stored image and mask histories grow linearly with sequence length. One float32 RGB 196×196 image is about 0.44 MiB before list/runtime overhead. Selected histories are copied back to the search tensor’s device every frame; mask history uses explicit `.cuda()`.

Per-sequence finalization deletes tensor-cache entries and local tracking context but does not remove that task’s `memory_frames` or mask-history list. The whole dictionaries are deleted only when the pipeline stops (`one_stream/__init__.py:67-77,299-304`; mask plugin `:121-124`).

**CODE FACT — inspected:** README says reference count can be adjusted, but the pinned model signatures, evaluator input dictionaries, and dummy generator are structurally fixed to `z_0`, `z_1`, and `z_2`. No released reference-count configuration key was found.

If source were changed to add references, concatenated sequence length would grow linearly in the number of template tokens, while dense self-attention performs pairwise token interactions. Therefore the active attention structure does not scale purely linearly with reference count (`dinov2/layers/attention.py:36-55`). The released path itself remains fixed at three.

### E. Dynamic computation and TMoE

The B config uses rank 64, alpha 64, four experts, zero dropout, no shared expert, and no route compression (`config/SPMTrack/dinov2/config.yaml:33-41`).

**CODE FACT — inspected:** TMoE is installed on every frozen `nn.Linear` in every DINOv2 block (`SPMTrack.py:47-49`; `modules/tmoe/apply.py:7-37`). In each standard B block the targeted linears are attention qkv, attention projection, MLP fc1, and MLP fc2. The qkv wrapper splits into separate q, k, and v TMoE layers. This yields six TMoE layers per block and **72 TMoE layers across 12 blocks**.

For input `x` shaped `[B,N,D]`, each TMoE layer executes:

1. a bias-free gate producing `[B,N,4]`;
2. softmax across four experts;
3. one shared rank-64 compression because `route_compression=false`;
4. all four routed output matrix products;
5. multiplication of each result by its token-wise routing weight; and
6. summation with the original frozen linear output.

Evidence: `modules/tmoe/__init__.py:9-39,76-103,105-143`.

Routing is dense, token-wise computation. The code loops over and executes every expert. There is no top-k, expert capacity, token drop, dispatch, gather/scatter, or sparse conditional execution. At B steady state every targeted layer receives routing values for 1,318 tokens.

**CODE FACT — inspected:** although the inference build string has suffix `_merged`, no TMoE merge executes. `tmoe_merge_state_dict` is imported but not called. Inference `load_state_dict()` installs TMoE wrappers, and each wrapper remains `linear(x) + tmoe(x)` (`builder.py:43-51`; `SPMTrack_full_finetune.py:8,164-171`; `tmoe/__init__.py:93-103`). The checkpoint-loaded inference graph therefore retains the full frozen DINOv2 linear operations plus all gates and expert operations.

Unused adapter/IA3/VPT sources exist in the repository, but the released SPMTrack-B config/builder does not activate them. No LoRA or DoRA module is active in this path.

### F. Training evidence

| Property | Released full-data B configuration |
|---|---|
| Datasets | LaSOT-train, TrackingNet-train, COCO-2017-train, GOT10k-train with `got10k_vot_train_split` |
| Sampling | equal dataset weights; 131,072 samples/epoch |
| Frames/sample | three templates + two searches; max gap 200 |
| Epochs | 170 |
| Global batch | 128 |
| Optimizer | AdamW, LR `1e-4`, weight decay `0.1`, non-fused |
| Schedule | cosine to `1e-6`, two warmup epochs |
| Precision | FP16 autocast/GradScaler |
| Gradient behavior | clip 1.0; accumulation steps 1 |
| Compile | `torch.compile` enabled by default on Linux |

Evidence: `config/_dataset/train.yaml:19-42`; `config/SPMTrack/run.yaml:3,75-149,256-288`.

The training forward performs two complete transformer passes per sample; the second uses the detached query from the first (`SPMTrack.py:53-106`). The DINOv2 patch embed, blocks, norm, and positional embedding are frozen. Query/type embeddings, TMoE matrices/gates, and the MLP head are created after freezing and remain trainable (`SPMTrack.py:23-51`).

No activation/gradient-checkpoint call is active in the inspected SPMTrack/DINOv2 forward. The DINOv2 file imports `torch.utils.checkpoint`, but the active path never invokes it. The provided disable-compile mixin turns training compilation off. README warns that NaN loss can occur and recommends retrying or disabling compilation (`README.md:122-126`). A non-finite loss triggers a diagnostic dump then raises and stops; it is not automatically skipped/retried (`runner/training/default/__init__.py:148-157`; `runner/training/common/nan_dump.py:11-32`).

`boot.sh` detects available GPUs and spawns distributed workers only when more than one GPU is found; one GPU follows a non-distributed path (`boot.sh:104-112,185-193,206-211`). Batch-size mixins from 1 to 128 exist. However, under the default global-batch setting a one-GPU run receives local batch 128; no official 12-GB reproduction log was found.

**Repository recipe anomaly:** README calls `bash train.sh` the convenience command for SPMTrack-B, but `train.sh` always adds the GOT10k-only mixin. That mixin changes the data paths and duration to 100 epochs. Whether the external `spmtrack_base.bin` came from the full four-dataset/170-epoch recipe or the convenience GOT10k/100-epoch command is not established by the shell script alone.

### G. Profiling and export evidence

Automatic efficiency assessment is enabled in `run.yaml`. Its latency implementation uses 10 warmups, 100 timed loops, CUDA events, and `torch.cuda.synchronize()` on every timed iteration (`models/utils/efficiency_assessment/latency.py:28-51`). This timing mechanism is synchronized, but its graph and boundary require qualification.

**CODE FACT — inspected:** the profiler is model-only. Dummy input contains three templates and **two** searches and invokes ordinary `forward`, which performs two transformer passes (`sample_data_generator.py:7-21`). It excludes cropping/normalization, temporal selection, CPU→GPU reference movement, postprocessing, reference admission, query-dictionary orchestration, and result submission. It is not the one-search-per-video-frame `forward_tracking` path.

**Profiler-before-weight anomaly:** efficiency assessment runs before external tracker weights are loaded (`core/runtime/application/default/__init__.py:106-112`). The optimized inference constructor initially has no TMoE and installs it only in its `load_state_dict()` (`SPMTrack_full_finetune.py:164-171`). At model-manager version zero, a newly created alternate build does not copy state from the first build (`trackit/models/__init__.py:87-102`). Therefore the automatic profiler’s `eval` path omits TMoE and does not represent checkpoint-loaded SPMTrack inference. The profiler’s `train` path contains TMoE, but it is the two-search training-style forward.

FLOPs use `fvcore.nn.FlopCountAnalysis`, print unsupported operators, and define no SPMTrack/TMoE-specific handlers (`flop_count_analysis.py:20-50`; `model_efficiency_assessment.py:48-56`). The reported reference graph always contains exactly three dummy templates; memory-history selection and transfer are outside it.

Released evaluation uses plain PyTorch, FP16 autocast enabled, and `torch.compile` disabled (`config/SPMTrack/run.yaml:301-308`). DINOv2 uses PyTorch scaled-dot-product attention under `acc: default`; optional flash-attn/xFormers implementations exist but are not selected. No SPMTrack-specific ONNX or TensorRT exporter was found.

Generic TorchScript tracing infrastructure exists but is not selected by SPMTrack’s released config. It traces the ordinary dummy-data `forward`, not the stateful `forward_tracking(ids, z_0, x, ...)` interface, and therefore does not establish deployment parity. No SPMTrack-specific custom CUDA or Triton kernel was found; TMoE uses ordinary PyTorch Linear/softmax/matmul/Python-loop operations.

### H. HG4 evidence package — no decision

Evidence available for Manager reconciliation:

- the exact B training graph has 115,330,565 total parameters, of which 29,243,909 are trainable;
- training uses three templates, two searches, two full transformer passes, global batch 128, FP16, compilation, and no active gradient checkpointing;
- a single-GPU control path and smaller batch mixins exist, but the default one-GPU local batch is 128;
- no official 12-GB fit or peak-memory trace was found;
- the released adapter checkpoint omits frozen DINOv2 parameters and requires exact foundation reconstruction;
- parameter-efficient training does not establish a small inference graph or 12-GB feasibility.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

Evidence available for Manager reconciliation:

- checkpoint-loaded inference executes the full DINOv2-B backbone and all 72 TMoE layers; all four experts execute at every TMoE site;
- every frame transfers and re-encodes three 196×196 references, then performs dense attention over 1,318 tokens;
- image and mask histories grow with sequence length and survive task finalization until pipeline stop;
- surrounding evaluation uses Python dictionaries/lists, dataset-dependent history selection, CPU histories, host conversions, and per-sequence query state;
- no dedicated ONNX/TensorRT export or actual `forward_tracking` tracing path was found;
- the automatic profiler does not represent checkpoint-loaded steady-state inference.

**HG5 = PENDING**

### J. Code-visible cost sites

| Label | Site |
|---|---|
| CODE FACT — inspected | three 196×196 references and one 378×378 search are patch-embedded every frame; encoded references are not cached |
| CODE FACT — inspected | 12 dense attention blocks operate on 1,318 tokens at width 768 |
| CODE FACT — inspected | 72 token-wise TMoE layers execute all four experts, with no sparse dispatch |
| CODE FACT — inspected | selected references move from growing CPU history to GPU each frame |
| CODE FACT — inspected | image and mask histories append each frame without confidence admission and are not removed per completed task |
| ENGINEERING TARGET TO PROFILE | checkpoint-loaded batch-1 residency and peak inference allocation |
| ENGINEERING TARGET TO PROFILE | patch embedding, attention, frozen linear, gate, compression, and four expert outputs separately |
| ENGINEERING TARGET TO PROFILE | long-sequence CPU memory, transfer traffic, selection `lru_cache`, and task-finalization retention |
| ENGINEERING TARGET TO PROFILE | GPU-to-CPU confidence/box conversion and full postprocess/update path |

### K. Unresolved items

1. Exact external B checkpoint filename/hash and successful strict load: **NOT VERIFIED**.
2. Whether `spmtrack_base.bin` used the full 170-epoch recipe or GOT10k-only 100-epoch convenience command: **OPEN QUESTION**.
3. L/G tracker checkpoints: **NOT AVAILABLE** at the pinned release state.
4. README’s adjustable reference-count statement versus code fixed at three: **OPEN QUESTION / NO RELEASED CONFIG FOUND**.
5. Correct checkpoint-loaded steady-state FLOPs/FPS: **UNKNOWN** because automatic assessment precedes weight load and profiles the two-search `forward`.
6. Generic TorchScript parity with actual stateful `forward_tracking`: **NOT DEMONSTRATED**.
7. Long multi-sequence memory retention and cleanup: **RUNTIME MEASUREMENT REQUIRED**.
8. Single-GPU 12-GB training feasibility: **UNVERIFIED**.
9. End-to-end export/operator support and target-device latency/memory/power/thermal behavior: **PENDING**.

## 6. Cross-candidate implementation observations without gate decisions

| Candidate | Template/reference execution | Dynamic mechanism | Profiler boundary/anomaly | Export/deployment resource state |
|---|---|---|---|---|
| SUTrack | active raw template(s) re-encoded every frame; B/L bounded fixed+dynamic pair | no routing; confidence/interval template replacement | generic evaluator; no explicit CUDA synchronization, while host reads induce implicit synchronization; AGX methodology absent | hard-CUDA PyTorch; no dedicated exporter |
| AsymTrack | template encoded on first tracked frame; bounded ETM/attention caches reused | two input-dependent ETMs; OPE fused before inference | THOP MAC path processes template while speed path is steady-state; speed unsynchronized | no AsymTrack exporter; legacy HiT ONNX consumer is unrelated |
| SPMTrack | three raw references transferred and re-encoded every frame; stored histories grow | 72 dense token-wise TMoEs; all four experts execute | synchronized model-only profiler uses two-search `forward`; eval path before weight omits TMoE | generic tracing exists but does not cover actual stateful tracking interface; no ONNX/TensorRT path |

This table is a mapping of inspected execution behavior. It is not a comparison score, redundancy conclusion, feasibility decision, rank, or baseline recommendation.

## 7. Batch completion and locked next state

| Candidate | Final code-audit state | HG4 | HG5 |
|---|---|---|---|
| CX043 SUTrack | CODE AUDIT COMPLETE | PENDING | PENDING |
| CX044 AsymTrack | CODE AUDIT COMPLETE | PENDING | PENDING |
| CX049 SPMTrack | CODE AUDIT COMPLETE | PENDING | PENDING |

No candidate gate, canonical-matrix field, scientific interpretation, score, rank, shortlist, baseline, or architecture was changed. Batch D was not activated.

BATCH C CODE EVIDENCE EXTRACTION:
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
