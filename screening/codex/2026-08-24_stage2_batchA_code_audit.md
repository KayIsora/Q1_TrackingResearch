# Stage 2A — Batch A code / engineering evidence audit

Date: **2026-08-24**

Lane: **Codex worker — code and engineering audit**

Stage: **Stage 2A, Batch A evidence extraction only**

## 1. Scope, labels, and stopping boundary

This report records implementation evidence for the five active Batch A candidates:

- CX007 — SpikeTrack
- CX009 — UETrack
- CX010 — UTPTrack
- CX013 — FARTrack
- CX014 — GOT-Edit

The candidates remain members of the 16-family scientific-audit queue. They are **not a shortlist**.

Every repository was inspected in an isolated checkout at the exact reference registered in the project source manifest. File and line references below refer to those pinned trees. No training, benchmark reproduction, ONNX export, TensorRT build, or Jetson Nano run was performed.

Evidence labels:

- **CODE FACT — inspected:** directly visible in the pinned implementation or configuration.
- **RESOURCE AVAILABILITY FACT:** directly visible release, checkpoint, script, or tool availability.
- **ENGINEERING TARGET TO PROFILE:** a code-visible execution site whose measured cost remains unknown.
- **OPEN QUESTION:** evidence not found or an implementation ambiguity that was not resolved by inspection.

This report does not decide HG4 or HG5. It does not begin HG6, soft scoring, ranking, shortlist selection, baseline selection, or architecture design. The canonical candidate matrix was not modified.

## 2. Completion and stage guard

| Candidate | Pinned source inspected | Code audit state |
|---|---:|---:|
| CX007 SpikeTrack | yes | complete |
| CX009 UETrack | yes | complete |
| CX010 UTPTrack | yes | complete |
| CX013 FARTrack | yes | complete |
| CX014 GOT-Edit | yes | complete |

The completion labels above mean that the required code-evidence fields were inspected. They do not mean successful reproduction or a gate decision.

## 3. CX007 — SpikeTrack

### A. Provenance and audited variants

- **Repository:** `faicaiwawa/SpikeTrack`
- **Pinned ref:** `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`
- **Registered source:** [R19](../../references/references.md#r19)
- **Audited configurations:** Base 256 T1/T3, Base 384 T1/T3, and Small 256 T1/T3 under `experiments/spiketrack/`.

**CODE FACT — inspected:** no Small-384 YAML exists in the pinned tree.

| Axis | Audited mapping | Evidence |
|---|---|---|
| Base | `Efficient_Spiking_Transformer_l`; widths `[64,128,256,360]`; 360-dimensional final encoder output; 256-channel head | `experiments/spiketrack/spiketrack_b256_t1.yaml:35-45`; `lib/models/spiketrack/sdtv3.py:828-845` |
| Small | `Efficient_Spiking_Transformer_s`; widths `[32,64,128,192]`; 192-dimensional final encoder/head input | `experiments/spiketrack/spiketrack_s256_t1.yaml:35-45`; `lib/models/spiketrack/sdtv3.py:868-885` |
| 256 | Template and search are 256×256; stride-16 head grid is 16×16 | `experiments/spiketrack/spiketrack_b256_t1.yaml:7-22,61-66`; `lib/models/spiketrack/decoder.py:319-329` |
| 384 | Template and search are 384×384; stride-16 head grid is 24×24 | `experiments/spiketrack/spiketrack_b384_t1.yaml:7-22,61-66`; `lib/models/spiketrack/decoder.py:319-329` |
| T1 | one template in data and inference configuration | `experiments/spiketrack/spiketrack_b256_t1.yaml:17-22,68` |
| T3 | three templates in data and inference configuration | `experiments/spiketrack/spiketrack_b256_t3.yaml:17-22,69` |

**CODE FACT — inspected:** T=1/T=3 denotes the template/time dimension presented to spike and retrieval modules. It is not a persistent one-step/three-step neuron clock across video frames.

### B. Model construction

The model entry path builds a shared template/search spiking MetaFormer and a center-based prediction head:

- Both Base and Small instantiate five downsampling stages, four early convolutional blocks, six stage-3 blocks, and two stage-4 blocks. Base versus Small changes width, not those block counts (`lib/models/spiketrack/sdtv3.py:681-729`).
- A block applies spike separable convolution, spike linear attention, and an MLP through residual connections (`lib/models/spiketrack/sdtv3.py:285-294`).
- Linear attention evaluates `k^T @ v` and then `q @ (k^T v)`; it does not construct a full token-by-token attention matrix (`lib/models/spiketrack/sdtv3.py:206-244`).
- Six Memory Retrieval Modules (MRMs) update only the search branch. They occur after `downsample1_2`, `downsample2`, `downsample3`, stage-3 block 2, `downsample4`, and the final stage-4 block (`lib/models/spiketrack/sdtv3.py:765,774,787,794-795,800,806`).
- The selected `CenterPredictor` has separate five-convolution center-score, size, and offset branches. Base uses 360 input/256 branch channels; Small uses 192/192 (`lib/models/spiketrack/decoder.py:82-119,319-329`).

### C. Runtime graph and execution frequency

`tracking/test.py` defaults `inference_mode=True`; the evaluation wrapper therefore selects the split, cached tracker `spiketrack_inf.py` (`tracking/test.py:40-52`; `lib/test/evaluation/tracker.py:37-62`).

| Component | Frequency | Main input/output | State dependency |
|---|---|---|---|
| CPU crop, pad, resize, normalization | initialization and every frame | RGB image → 256² or 384² tensor | current box |
| Template encoder | initialization; T3 qualifying updates only | T templates → six `k^T v` cache tensors | template list |
| Search encoder | every frame | one search crop + six caches → search feature | cached template retrieval tensors |
| Six MRMs | every frame | one-step search query repeated over T; cached `k^T v` | T1 or T3 cache |
| Center head | every frame | 16² or 24² feature map → center/size/offset maps | none beyond current features |
| Template refresh | only T3, periodic and confidence-controlled | current predicted crop → replacement template and recomputed six-cache set | frame number and max score |

Evidence: `lib/test/tracker/spiketrack_inf.py:59-121`; `lib/models/spiketrack/sdtv3_temp_inference.py:651-716`; `lib/models/spiketrack/sdtv3_search_inference.py:725-776`.

Within every MRM:

- template features form key and value tensors;
- the single-step search query is explicitly repeated T times;
- cached `k^T v` is used for an initial query and one hard-coded recurrent refinement;
- when T>1, a channel-wise softmax gate reduces the temporal dimension back to one search step.

Evidence: `lib/models/spiketrack/sdtv3.py:390-401,421-438,478-496,519-584`; cached equivalent at `lib/models/spiketrack/sdtv3_search_inference.py:246-287,405-437`.

The retrieval grid is 16×16 at 256 input and 24×24 at 384 input. Adaptive pooling establishes that grid and bilinear interpolation restores the branch resolution (`lib/models/spiketrack/sdtv3.py:466-476,586-594`; `lib/models/spiketrack/fuc.py:88-111`).

### D. Temporal, template, and memory behavior

- Initialization constructs `[template] * num_template`; T3 therefore begins with three references to the same initial crop (`lib/test/tracker/spiketrack_inf.py:65-70`).
- Template index 0 remains fixed. A qualifying T3 update removes index 1 and appends the latest crop (`lib/test/tracker/spiketrack_inf.py:115-121`).
- The update rule is hard-coded in the tracker: dataset names containing LaSOT use interval 40 and threshold 0.8; other datasets use interval 25 and threshold 0.7 (`lib/test/tracker/spiketrack_inf.py:44-51`).
- YAML `TEST.UPDATE_INTERVALS` and `UPDATE_THRESHOLD` are not consumed by this cached path.
- Persistent state consists of box state, frame counter, a fixed-length template list, and six fixed-shape retrieval-cache tensors. No feature-history list grows with sequence length.
- The non-cached tracker instead concatenates template images with every search image and recomputes both branches every frame (`lib/test/tracker/spiketrack.py:52-66,95-104`).

### E. Dynamic computation and spike operators

**CODE FACT — inspected:**

- `Quant` clamps to [0,4], rounds, and `MultiSpike` divides by four, yielding dense floating values in `{0,0.25,0.5,0.75,1}` (`lib/models/spiketrack/ni_lif.py:5-46`).
- The custom autograd backward passes gradients inside the clamp range and zeroes them outside (`lib/models/spiketrack/ni_lif.py:14-21`).
- Every `mem_update` is constructed with four decay logits, but execution loops over `x.shape[0]`, rejects a temporal size greater than three, and creates membrane variables locally on each forward (`lib/models/spiketrack/ni_lif.py:49-88`).
- T1 performs no temporal decay transition; T3 uses the first two decay entries. There is no persistent membrane buffer across video frames.
- Spikes feed standard dense Conv1d/Conv2d and matrix multiplication. No custom CUDA kernel, sparse tensor kernel, or event-driven runtime was found.
- The center head decodes a box before the tracker applies its Hann window; the tracker then decodes again and discards the first decoded box (`lib/models/spiketrack/decoder.py:133-161`; `lib/test/tracker/spiketrack_inf.py:87-103`).

### F. Training evidence

| Field | Base/Small T1 | Base/Small T3 | Evidence |
|---|---:|---:|---|
| Datasets | LaSOT, GOT10K-vottrain, COCO17, TrackingNet; equal ratios | same | representative YAML `:23-34` |
| Samples/epoch | 60,000 | 60,000 | representative YAML `:23-34` |
| Batch | 16 per process | 16 per process | representative YAML `:46-60` |
| Epochs | 320 | 60 | six experiment YAMLs |
| LR / optimizer | 4e-4, AdamW, weight decay 1e-4 | same | YAML and `lib/train/base_functions.py:195-205` |
| LR drop | epoch 240 | epoch 30 | six experiment YAMLs |
| Backbone multiplier | 0.1 | 0.1 | six experiment YAMLs |
| AMP | absent → false | absent → false | `lib/train/train_script.py:84-88` |
| Activation checkpointing | not consumed | not consumed | repository-wide inspection |

The README launches eight DDP processes, so its exact command has aggregate batch 128 (`readme.md:57-64`; `tracking/train.py:24-39`).

Training-source anomalies:

- T3 YAMLs record a T1 checkpoint in `MODEL.PRE_TRAINED`, but no model/trainer path consumes that field. The as-shipped path therefore does not implement the recorded T1→T3 initialization.
- `TRAIN.FREEZE_ENCODER`, `ENCODER_OPEN`, and `MODEL.ENCODER.USE_CHECKPOINT` are configuration-only; no consuming path was found.
- T1 gives base LR to names containing `mrm`, `decay`, `pos_embed`, or `decoder`; T3 omits `decoder` from that group. Remaining parameters use 0.1× LR (`lib/train/base_functions.py:152-197`).
- The classification backbone source is a relative path for Small but the literal root path `/pretrained_models/V3_19.0M_1x4.pth` for Base (`lib/models/spiketrack/sdtv3.py:907-943`).
- Validation construction/execution is commented out; only the training loader reaches the trainer (`lib/train/train_script.py:47-53,87-90`).

### G. Profiling and export evidence

- Dataset FPS uses wall-clock `time.time()`; there are no warm-ups or CUDA Events in that evaluator (`lib/test/evaluation/tracker.py:122-161`; `lib/test/evaluation/running.py:143-150`).
- SFR hooks attach to every `mem_update`, compute means, and call `.cpu().tolist()`; instrumented SFR timing is therefore not an unmodified runtime path (`lib/models/spiketrack/spiketrack_inf.py:29-45`; `lib/models/spiketrack/sdtv3_temp_inference.py:622-639`).
- THOP is installed by `install.sh`, but no SpikeTrack FLOP-count entrypoint or THOP import was found.
- No end-to-end ONNX exporter, TensorRT/Torch-TensorRT builder, TorchScript exporter, CUDA-Event profiler, or Jetson runtime was found.
- A generic ONNX-oriented NestedTensor helper exists in `lib/utils/misc.py:307-355`, but the audited tracker does not call it and it is not an exporter.

### H. HG4 evidence package — no decision

Evidence relevant to a single RTX 3060 12 GB:

- The cached inference path separates template work from steady-state search work and has six explicit fixed-shape cache tensors.
- Training configs and optimizer groups are present, but the documented command uses eight processes and no verified single-12-GB recipe is supplied.
- T1→T3 initialization and several freeze/checkpoint configuration fields are not implemented by the inspected path.
- No reproduction or peak-memory measurement was run.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

Structural evidence relevant to Jetson Nano:

- The neural path uses dense standard convolution/matmul plus custom autograd clamp/round spike quantization.
- `mem_update` contains Python shape branches, a Python timestep loop, tensor mutation, clone, and detach.
- The cached interface passes a Python dictionary of six tensors between template and search modules.
- Preprocessing is OpenCV/CPU followed by `torch.tensor(...).cuda()`; output mapping calls CUDA tensor `.tolist()` each frame.
- Tracker state, confidence thresholding, periodic replacement, Hann post-processing, and coordinate mapping are Python-side.
- No Nano package, engine, operator-parity test, latency, power, or sustained-thermal evidence was found.

**HG5 = PENDING**

### J. Code-visible cost sites

| Label | Site |
|---|---|
| CODE FACT — inspected | six cached MRMs execute on every frame; T3 repeats each search query over three template slices |
| CODE FACT — inspected | 384 uses 24² rather than 16² retrieval/head grids and larger native feature maps |
| CODE FACT — inspected | a qualifying T3 update reruns the full template encoder and all six cache extractors |
| CODE FACT — inspected | the center-box decode is executed twice per frame |
| ENGINEERING TARGET TO PROFILE | CPU crop/resize, host-to-device creation, search stages, six MRMs, head, duplicate decode, and host output conversion separately |
| ENGINEERING TARGET TO PROFILE | steady-state versus template-refresh frames |
| ENGINEERING TARGET TO PROFILE | T1 versus T3 and 256 versus 384 under the same timing protocol |
| ENGINEERING TARGET TO PROFILE | export/parity of clamp-round-divide and the Python timestep loop under FP32/FP16/INT8 |

### K. Unresolved items

- Exact ONNX graph and export success: **NOT FOUND / PENDING**.
- TensorRT parser/plugin needs and numerical parity: **PENDING**.
- Missing/unexpected keys from split `strict=False` checkpoint loading are not validated.
- T1→T3 initialization: intended by YAML, not consumed by code.
- Published-checkpoint provenance and successful end-to-end reproduction: **NOT RUN**.
- Small-384 configuration: **NOT FOUND**.
- SFR README output directory and executed output directory disagree.

## 4. CX009 — UETrack

### A. Provenance and audited variants

- **Repository:** `kangben258/UETrack`
- **Pinned ref:** `fd13b0eaf16d51536008295f3b27807c69eaad50`
- **Registered source:** [R21](../../references/references.md#r21)
- **Audited configurations:** `uetrack_tiny.yaml`, `uetrack_small.yaml`, and `uetrack_base.yaml`.

| Variant | Factory | Pyramid block depths | Stage widths | Heads | Experts | TP-MoE block, zero-based |
|---|---|---:|---:|---:|---:|---:|
| UETrack-T | `fastitpnt_layer2` | [1,1,2] | [96,192,384] | 6 | 2 | 1 |
| UETrack-S | `fastitpnt_layer4` | [1,1,4] | [96,192,384] | 6 | 4 | 3 |
| UETrack-B | `fastitpnt_layer6` | [1,1,6] | [96,192,384] | 6 | 8 | 5 |

Evidence: `experiments/uetrack/uetrack_{tiny,small,base}.yaml:53-61`; `lib/models/uetrack/fastitpn.py:814-925,945-1077,1302-1357`.

All three configs use six-channel student input, 112×112 template, 224×224 search, final width 384, and stride 16. A 4×4 stride-4 patch convolution and two stride-2 merges produce 49 template tokens and 196 search tokens (`lib/models/uetrack/fastitpn.py:649-696,718-728`).

**OPEN QUESTION — parameter identity:** the README lists 6/9/13 M parameters (`README.md:63-69`), while a read-only count of the declared source modules gives encoder-only totals of 6.23/13.04/22.80 M and encoder+center-head totals of 10.05/16.86/26.62 M for T/S/B. These totals exclude the task decoder, text adapters, and external CLIP model. The README figures cannot be treated as the complete resident Python inference object size without a reconciled counting protocol.

### B. Model construction and RGB inference object

The inference builder constructs:

- the selected Fast-iTPN student encoder;
- a center-based tracking decoder;
- a task decoder;
- a full CLIP `ViT-L/14` object wrapped by `TextEncoder`;
- student text-interface projection;
- a transient teacher encoder used only to obtain a channel dimension.

Evidence: `lib/models/uetrack/uetrack.py:346-366`; `lib/models/uetrack/clip.py:6-26`.

**CODE FACT — inspected:** the returned deployed model excludes the TAD teacher and Adaptive Net, but it retains CLIP and the task decoder even though the tracker does not call the CLIP vision tower or task decoder.

The supplied configs keep multimodal vision/language enabled while `TEST.USE_NLP.DEFAULT=False` (`experiments/uetrack/*.yaml:1-4,108-122`).

### C. Pure RGB runtime graph

| Component | Frequency | Input/output | State |
|---|---|---|---|
| Template crop and six-channel construction | initialization | RGB template concatenated with itself → 6×112×112 | cached template pixels |
| CLIP text encoding | once per sequence | 77 zero token IDs → cached projected text token | cached text token |
| Search six-channel construction | every frame | RGB search concatenated with itself → 6×224×224 | none |
| Fast-iTPN encoder | every frame | class + search + template + text tokens → encoded search/template stream | cached template pixels/text, both reprocessed |
| TP-MoE | every frame, last main block | 247 tokens padded to 248 → dense expert routing → 247 tokens | expert weights |
| Center decoder | every frame | search features → center/size/offset maps and one decoded box | none |
| Hann post-process and second decode | every frame | center map → final box | previous box for crop mapping |

Evidence: `lib/test/tracker/uetrack.py:101-170,203-210`; `lib/models/uetrack/fastitpn.py:1183-1214`.

Default no-NLP sequence order and size are:

`[class:1, search:196, template:49, zero-text:1] = 247 tokens`.

Important modality boundaries:

- Ordinary RGB is duplicated into both three-channel halves. There is no separately instantiated depth, thermal, or event branch.
- RGB-D/RGB-T/RGB-E use different content in the second three-channel half, not a different encoder module (`lib/train/dataset/depth_utils.py:7-132`).
- Even without an NLP description, the full CLIP text encoder runs once on zero IDs and the resulting student token remains in every frame’s transformer sequence.
- `TextEncoder.text_proj` executes, but its teacher-oriented output is discarded in student inference; the student interface projection supplies the used token (`lib/models/uetrack/uetrack.py:175-180`).
- `task_index` is threaded through the API but the student block forward does not read it (`lib/models/uetrack/fastitpn.py:443-537`).

### D. TP-MoE dynamic computation

TP-MoE replaces the ordinary SwiGLU only in the last final-stage block of each released model (`lib/models/uetrack/fastitpn.py:374-402`).

**CODE FACT — inspected runtime sequence** (`lib/models/uetrack/fastitpn.py:478-534`):

1. normalize tokens;
2. pad the token count to a multiple of expert count E;
3. reshape and average each contiguous group of E tokens;
4. project every pooled token into E slot embeddings;
5. construct dense similarity logits;
6. softmax-dispatch every input token to all expert slots;
7. run every expert’s stacked SwiGLU;
8. dense softmax-combine every expert-slot output for every token;
9. remove pad tokens and add the residual.

| Variant | E | Padded tokens | Pooled groups | Dense routing matrix |
|---|---:|---:|---:|---:|
| T | 2 | 248 | 124 | 248×248 |
| S | 4 | 248 | 62 | 248×248 |
| B | 8 | 248 | 31 | 248×248 |

This is dense soft routing, not top-k/sparse routing. Every expert executes on every frame. No `sort`, `argsort`, `topk`, `gather`, `scatter`, expert-capacity drop, or task-index branch occurs inside TP-MoE. Expert compute uses stacked per-expert `einsum` (`lib/models/uetrack/fastitpn.py:133-177`).

Dynamic/export-sensitive operations include runtime padding, Python `if pad_len`, shape-derived views, runtime `arange`, masks, and truncation. Optional text changes token count.

### E. TAD boundary

Training construction includes a 24-final-block, width-512 Fast-iTPN-B teacher; the T/S/B student; shared CLIP; teacher/student decoders; an optional 384→512 feature alignment; and Adaptive Net (`lib/models/uetrack/uetrack.py:283-344`; `lib/models/uetrack/fastitpn_teacher.py:1150-1161`).

**CODE FACT — inspected:**

- The external teacher checkpoint is mandatory, loaded strictly, frozen, and kept in eval mode during training (`lib/models/uetrack/uetrack.py:309-314`; `lib/train/train_script.py:53-63`).
- Adaptive Net pools detached teacher/student search features and emits two logits. A hard straight-through Gumbel decision at temperature 5 selects whether a sample receives teacher-based distillation (`lib/models/uetrack/uetrack.py:251-280`; `lib/train/actors/uetrack.py:83-103`; `lib/utils/gs.py:15-26`).
- Supervised student loss still applies to all samples; KD and feature MSE apply only where the detached adaptive decision selects the teacher (`lib/train/actors/uetrack.py:107-167,188-225`).
- Student and Adaptive Net have separate optimizers and sequential backward passes (`lib/train/trainers/ltr_trainer.py:471-519`).
- `build_uetrack_inference` returns only the student object; teacher, Adaptive Net, and feature-alignment layer are absent at inference (`lib/models/uetrack/uetrack.py:346-366`).

TAD is therefore training-only in the audited deployment path.

### F. Temporal/template/memory behavior

- The initial RGB template and projected text token persist for the sequence.
- Template pixels, template mask, patch embedding, pyramid stages, and final blocks are recomputed every frame; no encoded-template cache is present (`lib/test/tracker/uetrack.py:106,142-147`; `lib/models/uetrack/fastitpn.py:1131-1207`).
- There is no online template replacement or growing reference bank in the audited tracker.
- The center decoder calculates a box internally, but the tracker ignores that box, applies a Hann window, and calls `cal_bbox` again (`lib/models/uetrack/decoder.py:175-201`; `lib/test/tracker/uetrack.py:151-166`).

### G. Training evidence

All three released configs specify:

- datasets: LaSOT, GOT10K-vottrain, COCO17, TrackingNet, VastTrack, TNL2K-train, OTB99-train, DepthTrack-train, VisEvent, and LasHeR-train;
- sampling ratios `[4,4,4,4,4,3,1,2,2,2]`;
- 100,000 samples/epoch and maximum gap 400;
- batch 64 per process, 500 epochs;
- AdamW, LR 1e-4, encoder multiplier 0.1, weight decay 1e-4;
- StepLR at epoch 400 and gradient clip 0.1;
- KD temperature 3, KD weight 5, and feature weight 0.002.

Evidence: `experiments/uetrack/*.yaml:25-48,84-107`.

The README’s distributed command uses two processes, giving nominal aggregate batch 128; no gradient accumulation exists (`README.md:198-205`; `lib/train/base_functions.py:241-254`).

Training-boundary facts:

- No released RGB-only YAML exists. Ordinary RGB frames are duplicated to six channels; language-missing samples receive 77 zero IDs.
- Student encoder is unfrozen. The shared CLIP object is frozen with the teacher; the separately constructed student text interface remains trainable.
- Released configs do not define AMP, so AMP is false. Config schema rejects unknown keys (`lib/train/train_script.py:82-85`; `lib/config/uetrack/config.py:182-191`).
- Activation checkpointing is disabled by config and hard-coded `grad_ckpt=False` in both encoder builders (`lib/config/uetrack/config.py:38`; `lib/models/uetrack/encoder.py:46-99`).

**Repository execution anomaly:** released YAMLs set `MODEL.ENCODER.PRETRAIN_TYPE: ''`. The inference builder nevertheless treats the normal process as main and each student factory calls `torch.load(pretrain_type)` before the tracker checkpoint is loaded (`lib/models/uetrack/encoder.py:46-66`; `lib/models/uetrack/fastitpn.py:1316-1357`). A valid backbone path must therefore be supplied for the unmodified startup path.

### H. Profiling and export evidence

`tracking/profile_model_uetrack.py`:

- uses batch 1 and random six-channel tensors;
- profiles text encoder, encoder, tracking decoder, and task decoder separately;
- reports “overall” as encoder + tracking decoder, excluding CLIP/text and task decoder;
- warms 100 and times 1,000 iterations without CUDA synchronization immediately around the measured interval;
- uses a precomputed decoder input rather than the encoder output from the timed call;
- excludes crop, normalization, template indication, Hann weighting, second decode, and text initialization;
- registers a custom count only for `nn.MultiheadAttention`, while UETrack uses functional matmuls and TP-MoE `einsum`.

Evidence: `tracking/profile_model_uetrack.py:25-90,106-127`; `lib/models/uetrack/fastitpn.py:277-325`.

No ONNX exporter, TensorRT builder/plugin, TorchScript path, or Jetson package was found. README AGX figures do not identify precision, software stack, synchronization protocol, resident memory, or TensorRT engine (`README.md:63-69`).

### I. HG4 evidence package — no decision

Evidence relevant to a single RTX 3060 12 GB:

- Student, teacher, unified datasets, losses, and optimizer paths are present.
- The released recipe uses a teacher plus student, per-process batch 64, two-process example, 500 epochs, and no activation checkpointing or gradient accumulation.
- No verified single-GPU/12-GB recipe or peak-memory record is supplied.
- Empty student-pretrain path and source-count/checkpoint identity remain unresolved.

**HG4 = PENDING**

### J. HG5 evidence package — no decision

Structural evidence relevant to Jetson Nano:

- The student’s core operations are dense convolution, attention matmul, softmax, reshape, and dense expert `einsum`.
- TP-MoE executes all experts and materializes a dense 248×248 routing tensor.
- Full CLIP, its unused vision tower, the task decoder, and a transient teacher encoder are instantiated by the Python setup even though several do not run per frame.
- Tracker/preprocessor paths contain hard-coded `.cuda()`; list inputs, string mode dispatch, runtime MoE padding, masked softmax, integer box decoding, and `gather` require an explicit export wrapper and compatibility validation.
- No Nano runtime, latency, memory, power, thermal, or parity evidence exists.

**HG5 = PENDING**

### K. Code-visible cost sites and unresolved items

| Label | Site |
|---|---|
| CODE FACT — inspected | every frame recomputes the static template encoder path |
| CODE FACT — inspected | TP-MoE runs every expert and dense dispatch/combine on a 248-token padded sequence |
| CODE FACT — inspected | center-box decoding occurs twice |
| CODE FACT — inspected | zero-text CLIP runs once per sequence, and one returned text projection is discarded |
| CODE FACT — inspected | full CLIP/task decoder remain resident; a teacher encoder is transiently built only to obtain a channel number |
| ENGINEERING TARGET TO PROFILE | TP-MoE logits, dispatch/combine, expert `einsum`, and peak workspace |
| ENGINEERING TARGET TO PROFILE | template recomputation, text initialization, encoder, decoder, post-processing, and host/device boundaries separately |
| ENGINEERING TARGET TO PROFILE | resident/startup memory before and after excluding unused inference modules |

Unresolved:

1. README versus source parameter counts.
2. Exact student, teacher, and backbone artifact checksums and `strict=False` missing/unexpected keys.
3. Clean inference launch after resolving empty `PRETRAIN_TYPE`.
4. Fixed-signature ONNX/TensorRT export and numerical parity.
5. Whether a deployed RGB signature retains zero-text and the full CLIP dependency.
6. Target-device latency, memory, power, thermals, and sustained behavior.

## 5. CX010 — UTPTrack

### A. Provenance and audited variants

- **Repository:** `EIT-NLP/UTPTrack`
- **Pinned ref:** `84e0f49711254a44f5308faaa9a2405db1964dd7`
- **Registered source:** [R23](../../references/references.md#r23)
- **Deep audit scope:** `UTPTrack-O`, the generic RGB path. `UTPTrack-S` was inspected only to delimit the method family.
- **Representative full configs:** `UTPTrack-O/experiments/ostrackcmp/ceatetta_256_r7_all.yaml` and `utptrack_384_r7_all.yaml`.

Both full O variants use ViT-B/16 with 12 blocks, width 768, and 12 heads (`UTPTrack-O/lib/models/ostrackcmp/vit_ceatetta.py:396-401`).

| Full config | Search | Static template | Dynamic template | Initial tokens | Batch |
|---|---:|---:|---:|---:|---:|
| `ceatetta_256_r7_all` | 256² → 256 | 128² → 64 | 128² → 64 | 384 | 32 |
| `utptrack_384_r7_all` | 384² → 576 | 192² → 144 | 192² → 144 | 864 | 16 |

Both set search CE at block indices [3,6,9], dynamic-template elimination and static-template elimination at [4,7,10], retention 0.7, and `ALL_FOREGROUND` token-type score bias (`UTPTrack-O/experiments/ostrackcmp/ceatetta_256_r7_all.yaml:40-48`; 384 counterpart `:40-48`).

The repository also provides baseline, CE-only, CE+dynamic-template, and CE+separate-static/dynamic comparison YAMLs. The builder selects the corresponding backbone implementation from the configured type (`UTPTrack-O/lib/models/ostrackcmp/ostrackcmp.py:101-157`).

### B. Model construction and RGB runtime graph

1. Parameter loading resolves `experiments/ostrackcmp/<name>.yaml` and checkpoint `checkpoints/train/ostrackcmp/<name>/OSTrackCMP_epNNNN.pth.tar` (`UTPTrack-O/lib/test/parameter/ostrackcmp.py:7-25`).
2. Tracker construction builds OSTrackCMP, strictly loads the checkpoint, moves it to CUDA, and creates a dense Hann grid (`UTPTrack-O/lib/test/tracker/ostrackcmp.py:20-34`).
3. Initialization creates `template_list = [initial_template] * 2`; the static and dynamic slots therefore begin with identical pixels (`UTPTrack-O/lib/test/tracker/ostrackcmp.py:66-73`).
4. Token preparation patch-embeds search and both templates every frame and orders them `[search, static, dynamic]` (`UTPTrack-O/lib/models/ostrackcmp/vit_ceatetta.py:221-259`).
5. Twelve attention/MLP blocks run, with physical pruning at configured blocks (`UTPTrack-O/lib/models/ostrackcmp/vit_ceatetta.py:44-86,301-323`).
6. Only search tokens are restored to the original dense grid; template streams remain compact (`UTPTrack-O/lib/models/ostrackcmp/vit_ceatetta.py:332-358`).
7. The center head consumes the dense search grid and emits center, size, and offset maps; maximum raw center score is returned as confidence (`UTPTrack-O/lib/models/ostrackcmp/ostrackcmp.py:66-96`; `UTPTrack-O/lib/models/layers/head.py:130-201`).

### C. Pruning mechanisms and operator flow

Configuration indices are compared directly with the zero-based block index. CE therefore executes in transformer layers 4, 7, and 10; DTE/STE execute in layers 5, 8, and 11. Each block computes full attention first, prunes after its attention residual, and runs the MLP on the shortened sequence (`UTPTrack-O/lib/models/ostrackcmp/vit_ceatetta.py:44-84,156-184`).

| Mechanism | Score source | Retention | Main operators | Physical result |
|---|---|---|---|---|
| Search CE | static-template center queries → search keys | `ceil(keep × current search length)` | attention mean, full descending `torch.sort`, `gather`, `cat` | search sequence shrinks |
| DTE | static-template center queries → dynamic-template keys | same rule | mean, sort, gather, cat | dynamic sequence shrinks |
| STE | static-template self-attention; +1 center bonus; +1 foreground bonus | same rule | mean, sort, boolean/index operations, gather, cat | static sequence shrinks and is reordered |

Evidence: `UTPTrack-O/lib/models/compression/ce.py:75-128`; `UTPTrack-O/lib/models/compression/ate.py:13-56,68-135`.

Token-type awareness:

- a normalized target box is rasterized, unfolded into 16×16 patches, and reduced to foreground fractions;
- `ALL_FOREGROUND` marks every patch with nonzero overlap;
- the resulting mask adds a score bonus before static-template sort;
- the center and foreground masks are gathered in the same order as retained static features.

Evidence: `UTPTrack-O/lib/models/ostrackcmp/vit_ceatetta.py:194-219,234-238,272-300`; `UTPTrack-O/lib/models/compression/ate.py:83-135`.

**CODE FACT — inspected:** the primary path uses full `sort`, tensor `gather`, boolean indexing, `where`, concatenation, and final in-place `scatter_`. `topk` and `index_select` were not found in the audited O model/test path. Variables named `topk_idx` are slices of the full sort result.

### D. Token-size ledger

The following counts are exact applications of `ceil(0.7 × current length)`; they are derived from code/config and are not runtime measurements.

#### Full 256 path

| Stage | Search | Static | Dynamic | Compact total |
|---|---:|---:|---:|---:|
| input / through layer 3 | 256 | 64 | 64 | 384 |
| after layer 4 CE | 180 | 64 | 64 | 308 |
| after layer 5 DTE+STE | 180 | 45 | 45 | 270 |
| after layer 7 CE | 126 | 45 | 45 | 216 |
| after layer 8 DTE+STE | 126 | 32 | 32 | 190 |
| after layer 10 CE | 89 | 32 | 32 | 153 |
| after layer 11 DTE+STE | 89 | 23 | 23 | 135 |
| after search restoration | 256 | 23 | 23 | 302 |

#### Full 384 path

| Stage | Search | Static | Dynamic | Compact total |
|---|---:|---:|---:|---:|
| input / through layer 3 | 576 | 144 | 144 | 864 |
| after layer 4 CE | 404 | 144 | 144 | 692 |
| after layer 5 DTE+STE | 404 | 101 | 101 | 606 |
| after layer 7 CE | 283 | 101 | 101 | 485 |
| after layer 8 DTE+STE | 283 | 71 | 71 | 425 |
| after layer 10 CE | 199 | 71 | 71 | 341 |
| after layer 11 DTE+STE | 199 | 50 | 50 | 299 |
| after search restoration | 576 | 50 | 50 | 676 |

Removed search positions become zero vectors through pad plus `scatter_`. The dense center head has no pruning mask and runs on the restored 16×16 or 24×24 grid. Static and dynamic template streams are never restored (`UTPTrack-O/lib/models/ostrackcmp/vit_ceatetta.py:332-353`).

### E. Template and memory policy

- Static index 0 remains the initial template.
- Full released configs default to update interval 25 and raw-center-score threshold 0.70 (`ceatetta_256_r7_all.yaml:75-84`; 384 counterpart `:75-84`).
- Update condition is exactly `frame_id % interval == 0` and `conf_score > threshold`; a failed scheduled update waits until the next interval multiple (`UTPTrack-O/lib/test/tracker/ostrackcmp.py:120-123`).
- The accepted crop replaces index 1 after the current prediction; it affects subsequent frames (`UTPTrack-O/lib/test/tracker/ostrackcmp.py:123-137`).
- The static center/foreground mask is created at initialization and is not regenerated on a dynamic-template update.
- Storage is fixed at two image templates. No growing template-history list is present.
- Both templates are patch-embedded on every frame; no encoded-template cache exists.

### F. Training evidence

Common full-O recipe:

- datasets: LaSOT, GOT10K-vottrain, COCO17, TrackingNet at equal ratios;
- 60,000 samples/epoch; two templates plus one search;
- 300 epochs, AdamW, LR 4e-4, backbone multiplier 0.1, weight decay 1e-4;
- StepLR at epoch 240;
- batch 32 for 256 and 16 for 384;
- MAE initialization from `mae_pretrain_vit_base.pth`;
- AMP false and gradient clip 0.1.

Evidence: both full YAMLs `:11-36,50-72`; `UTPTrack-O/lib/train/base_functions.py:154-193`; `UTPTrack-O/lib/train/trainers/ltr_trainer.py:91-105`.

Pruning training schedule:

- configured start epoch 20 and warm duration 80;
- `adjust_keep_rate` remains 1 before/at epoch 20, cosine-decreases to 0.7 through epoch 100, then remains 0.7;
- one instantaneous rate is supplied to all scheduled blocks of each stream;
- loss is only 2×GIoU + 5×L1 + focal location; no selector/pruning-specific loss exists.

Evidence: `UTPTrack-O/lib/train/actors/ostrackcmp.py:45-123`; `UTPTrack-O/lib/utils/ce_utils.py:37-49`.

Training-source anomalies:

- `FREEZE_LAYERS=[0]` has no consumer in the normal O library; full configs train all otherwise trainable backbone parameters.
- README instructs `pretrained_models`, while the builder resolves the MAE file under `pretrained_networks`.
- Validation construction/execution is commented out.
- Saved state omits scheduler, AMP scaler, and RNG state.
- A single-process path reaches `dist.get_rank()` while distributed initialization is skipped for `local_rank=-1`; single-process behavior is unresolved (`UTPTrack-O/lib/train/run_training.py:42,54-65,99-108`).

### G. Profiling and export evidence

- `tracking/profile_model.py` accepts only `--script ostrack`; it cannot select `ostrackcmp`.
- Its example config names do not exist at the pinned commit.
- It passes raw template/search tensors, while the current model requires lists and template annotations.
- THOP is invoked with `custom_ops=None`; functional attention matmuls have no registered handler.
- Timing uses 500 warm-ups and 1,000 forwards but omits tracker preprocessing, Hann decoding, mapping, and update logic.

Evidence: `UTPTrack-O/tracking/profile_model.py:17-54,92-126`.

Therefore a runnable pinned `ostrackcmp` MAC/FLOP/speed profiler was **NOT FOUND**. No ONNX exporter, TensorRT builder/engine wrapper, or Jetson runtime was found.

Environment records conflict: `install.sh` names PyTorch 1.9/CUDA 10.2, `requirements.txt` pins PyTorch 1.10.1 while listing CUDA 12.1 packages, and several entries are machine-specific `file:///` paths.

### H. HG4 evidence package — no decision

Evidence relevant to a single RTX 3060 12 GB:

- Full 256/384 recipes, batches, optimizer, data, and pruning schedule are explicit.
- YAML batch is per loader/process; aggregate memory depends on launch process count.
- No validated single-3060 run, peak-memory record, or working current profiler is supplied.
- MAE path/documentation and single-process distributed behavior are unresolved.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

Structural evidence relevant to Jetson Nano:

- For fixed resolution, retained counts are fixed but token identities are content-dependent.
- The graph contains full sort, boolean advanced indexing, runtime `where`, gather, dynamic concatenation, and in-place scatter restoration.
- Model inputs are Python lists plus annotations; outputs include a dictionary and auxiliary list.
- Tracker/preprocessor uses hard-coded `.cuda()` and mutable Python template state.
- No export, parser, engine, numerical-parity, Nano latency, memory, power, or thermal result exists.

**HG5 = PENDING**

### J. Code-visible cost sites

| Label | Site |
|---|---|
| CODE FACT — inspected | attention is fully computed before each pruning operation |
| CODE FACT — inspected | six full-sort pruning sites execute in the full model |
| CODE FACT — inspected | content-dependent gather/cat physically shortens all three streams |
| CODE FACT — inspected | search pad/scatter restores the dense grid before the head |
| CODE FACT — inspected | static and dynamic template patch embeddings are recomputed every frame |
| ENGINEERING TARGET TO PROFILE | attention matmuls before and after each token-count reduction |
| ENGINEERING TARGET TO PROFILE | sort, boolean reduction, gather/cat, foreground-mask construction, and scatter separately |
| ENGINEERING TARGET TO PROFILE | full 256 and 384 end-to-end tracker paths with preprocessing/update included |

### K. Unresolved items and family boundary

- Exact paper-table/checkpoint label mapping beyond repository filenames: **PENDING**.
- Checkpoint content, strict-load result, and numerical evaluation: **NOT RUN**.
- Working current `ostrackcmp` profiler: **NOT FOUND**.
- ONNX/TensorRT/Jetson path: **NOT FOUND**.
- TensorRT behavior for the exact sort/index/gather/scatter graph: **PENDING**.
- README training/evaluation commands and config names are stale relative to the pinned tree.

`UTPTrack-S` is a separate SUTrack/Fast-iTPN multimodal implementation. Its full 224/384 configurations use CE [6,12,18], DTE/STE [9,15,21], modality-aware pruning, multilingual/multimodal datasets, and separate absolute pretrained paths. Those facts delimit the family; they were not converted into conclusions about the audited O RGB runtime.

## 6. CX013 — FARTrack

### A. Provenance and variant/config mapping

- **Repository:** `MIV-XJTU/FARTrack`
- **Pinned ref:** `5d3e4b90305c2e845340a39cb1ac9bb69c0c5180`
- **Registered source:** [R12](../../references/references.md#r12)
- **Deep audited path:** final `fartrack_sparse/fartrack_sparse_224_full` inference and its three training stages.

The README declares:

| Variant | README architecture |
|---|---|
| FARTrack-Tiny | ViT-Tiny, 224², 15 layers |
| FARTrack-Nano | ViT-Tiny, 224², 10 layers |
| FARTrack-Pico | ViT-Tiny, 224², 6 layers |

Evidence: `README.md:27-34`.

**CODE FACT — inspected:** the checked-in final sparse config constructs ViT-Tiny/16 with width 192, 3 heads, 12 base blocks, and 3 extension blocks—15 blocks total (`lib/models/fartrack_sparse/vit.py:142-202,433-439`; `experiments/fartrack_sparse/fartrack_sparse_224_full.yaml:41-60`).

**OPEN QUESTION:** no separate Nano/Pico sparse YAML, builder, layer-stop setting, or unambiguous Nano/Pico checkpoint filename was found. The README variant hyperlinks are literal `link` placeholders. The exact 10-layer and 6-layer code/checkpoint mappings remain **NOT FOUND**.

The README separately links frame-level FARTrack, FARTrackDistill, and FARTrackSparse checkpoint resources; these are stage resources, not an explicit Tiny/Nano/Pico filename map (`README.md:20-25`).

**RESOURCE AVAILABILITY FACT — inspected artifact metadata:** the three officially linked checkpoint files all contain 12 base plus 3 extension layers, positional tensors `pos_z=(1,49,192)` and `pos_x=(1,196,192)`, and six identity embeddings. Their stored metadata does not supply Nano/Pico mappings:

| Official file | Stored epoch/config metadata | Released-config relation |
|---|---|---|
| `FARTrack_ep0500.pth.tar` | frame-level; `fartrack_tiny_224` | released YAML is `fartrack_tiny_224_full` |
| `FARTrackDistill_ep0435.pth.tar` | self-distillation; `fartrack_distill_256_full` | released YAML is `fartrack_distill_224_full` |
| `FARTrackSparse_ep0015.pth.tar` | sparse; internal epoch 14; `fartrack_sparse_256_full_435_4` | released YAML is `fartrack_sparse_224_full` |

Thus the linked artifacts are structurally consistent with the 15-layer Tiny path, while exact config-name correspondence and executable Nano/Pico artifacts remain **OPEN QUESTION**.

### B. Model construction and token layout

`build_fartrack_sparse`:

- selects ViT-Tiny/16 from config;
- uses a hard-coded author pretrain directory `/home/caoanjia/wgj/FARTrack-main/pretrained_models/`;
- unconditionally loads `MODEL.PRETRAIN_PTH`, clones standard norm weights into masked-norm keys, and loads with `strict=False`;
- at tracker construction, a second final sparse checkpoint is loaded with `strict=True`.

Evidence: `lib/models/fartrack_sparse/fartrack_sparse.py:66-119`; `lib/test/tracker/fartrack_sparse.py:72-82`.

The audited per-frame token sequence is:

- five 112×112 templates at patch 16: `5 × 49 = 245` tokens;
- one 224×224 search: `196` tokens;
- four coordinate-command tokens;
- total: `445` tokens, width 192.

The six identity embeddings correspond to five templates plus one search (`lib/models/fartrack_sparse/fartrack_sparse.py:24-40`). The coordinate vocabulary has `bins × range + 5 = 605` embeddings, with four command IDs for x0/y0/x1/y1 (`lib/models/fartrack_sparse/vit.py:173-181`; `lib/models/fartrack_sparse/base_backbone.py:270-286`).

### C. Runtime graph and coordinate-generation trace

| Component | Frequency | Input/output | State |
|---|---|---|---|
| Crop and GPU preprocessing | initialization and every frame | NumPy RGB → CUDA template/search tensor | previous box |
| Five-template patch embedding | every frame | five image templates → 245 tokens | active image-template bank |
| Search patch embedding | every frame | one search crop → 196 tokens | current frame |
| 15 full transformer blocks | every frame | 445×192 → 445×192 | prior-frame mask |
| Coordinate logits | every frame | final four command tokens → four 605-way logits | current transformer features |
| IFAS mask generation | every frame, after all blocks | accumulated attention → four candidate masks | current attention |
| Box decode and template crop | every frame | four logits → bbox → new template | prior/current box |
| Template/mask history append and resampling | every frame, unconditional | new CUDA template and four masks → active five templates | full history |

Evidence: `lib/test/tracker/fartrack_sparse.py:232-265,271-406`; `lib/models/fartrack_sparse/base_backbone.py:264-390`.

#### Audited autoregressive boundary

The tracker converts the preceding three boxes into a 12-value `seq_input` and passes it into the model (`lib/test/tracker/fartrack_sparse.py:331-355`).

Inside `fartrack_sparse.forward_features`:

- `trajectory = seqs_input` is assigned;
- the trajectory tensor is used only to choose the command tensor’s type/device;
- `seqs_input_ = command`;
- the four command tokens alone are embedded and concatenated;
- `prev_position_embeddings` is read into a local variable but never added or concatenated.

Evidence: `lib/models/fartrack_sparse/base_backbone.py:270-286,318-336`; repository-wide uses at `lib/models/fartrack_sparse/vit.py:181`.

**CODE FACT — inspected:** in this final sparse path, the supplied previous-box trajectory does not enter the transformer token sequence. One model forward produces all four coordinate distributions in parallel. The Python loop over four coordinates only performs top-1 extraction from already-computed logits (`lib/models/fartrack_sparse/base_backbone.py:367-388`). Therefore the audited path has **one network call and zero recurrent coordinate-generation model steps per frame**.

### D. IFAS behavior: masking versus physical shrink

The attention implementation always forms Q/K/V for all N=445 tokens and a full attention tensor. A boolean padding mask is expanded per head and applied with `masked_fill`; sequence length does not change (`lib/models/fartrack_sparse/vit.py:39-72`).

Mask generation:

- sums detached attention across all 12 base and 3 extension blocks, then averages heads;
- reads center-search-to-template attention;
- at inference, slices the last 49 template tokens and creates four candidate masks removing 25%, 50%, 75%, and 90% by `argsort` plus nested Python loops;
- returns the new mask only after the current frame’s full transformer execution.

Evidence: `lib/models/fartrack_sparse/base_backbone.py:132-217,341-365`.

The tracker stores all four ratios, but active mask construction reads only `store_mask`, the 25% list (`lib/test/tracker/fartrack_sparse.py:126-142,164-176,222-230`). The 50/75/90 lists are not consumed by the active template-selection path.

For 49 patches, integer truncation masks 12/24/36/44 positions at the 25/50/75/90 settings, leaving 37/25/13/5 visible positions in the selected template. The tracker expands the one-dimensional visibility vector into identical rows of a 445×445 attention mask (`lib/models/fartrack_sparse/base_backbone.py:169-217`; `lib/test/tracker/fartrack_sparse.py:147-176`).

During sparse training, the fixed 25% rule masks the first four template streams and leaves the last template unpruned; 200 search+command positions are appended as active mask entries (`lib/models/fartrack_sparse/base_backbone.py:219-262`).

Sparse rollout begins all-visible, generates a detached/discrete mask after its first forward step, and then reuses that mask because regeneration is conditional on `torch.all(mask).item()` remaining true. The sparse losses contain coordinate CE and SIoU terms but no separate sparsity objective (`lib/train/actors/fartrack_sparse.py:302-361,434-444,646-708`; `lib/models/fartrack_sparse/base_backbone.py:359-365`).

**CODE FACT — inspected:** IFAS changes attention masking but does not physically gather/remove tokens in the released final path. QKV projection and the `q @ k^T` tensor retain length 445. This is a structural implementation fact, not a measured performance conclusion.

### E. Multi-template and persistent-memory behavior

- Initialization creates five references to the first template, a CUDA `445×445` all-true mask, and a fixed three-box trajectory buffer (`lib/test/tracker/fartrack_sparse.py:232-265`).
- Every frame crops a new template from the predicted box and calls `template_update_sampling(..., "exponential")` without a confidence gate (`lib/test/tracker/fartrack_sparse.py:392-406`).
- Before five frames, the active five slots duplicate available history. Thereafter exponential sampling keeps the first, latest, and three formula-selected historical indices (`lib/test/tracker/fartrack_sparse.py:145-191`).
- The active bank stays at five templates, but `stored_templates` and four mask-history lists append every frame and have no cap (`lib/test/tracker/fartrack_sparse.py:126-142`).
- Preprocessing creates templates and masks on CUDA (`lib/test/tracker/data_utils.py:6-17`); those histories therefore retain device tensors and grow with sequence length.
- The three-box buffer remains fixed length, although the final sparse model does not consume its values as trajectory tokens.

### F. TSSD and three-stage training evidence

#### Task-Specific Self-Distillation

The distillation model emits intermediate coordinate logits after base blocks 4–11 and extension blocks 0–1, plus the final output (`lib/models/fartrack_distill/base_backbone.py:189-229`). Adjacent deeper output is detached as teacher; the shallower output is trained with KL, while every intermediate/final output receives coordinate cross-entropy and SIoU-based loss (`lib/train/actors/fartrack_distill.py:273-393`).

**CODE FACT — inspected:** TSSD has no separate teacher model. Its intermediate losses/heads execute during distillation training; they are absent from `fartrack_sparse.forward_features` at final inference. The sparse builder only consumes a distillation checkpoint.

#### Stage recipes

| Stage | Data/config | Batch / epochs | Optimizer |
|---|---|---|---|
| Frame-level | LaSOT, GOT10K-vottrain, COCO17, TrackingNet; 1 search, 5 templates; 76,800 samples/epoch | 32 / 500 | AdamW, LR 4e-4, WD 1e-4, AMP false |
| Self-distillation | same four datasets and frame counts; 76,800 samples/epoch | 32 / 500 | AdamW, LR 4e-5, WD 1e-4, AMP false |
| Sparse sequence | LaSOT, GOT10K-vottrain, TrackingNet; 32 search frames, 5 templates; 1,000 samples/epoch | 8 / 20 | AdamW, LR 4e-6, WD 0.05, AMP false |

Evidence: `experiments/fartrack/fartrack_tiny_224_full.yaml:7-74`; `experiments/fartrack_distill/fartrack_distill_224_full.yaml:7-75`; `experiments/fartrack_sparse/fartrack_sparse_224_full.yaml:7-84`.

Additional training facts:

- README commands launch four processes for all three stages (`README.md:101-124`).
- Frame-level initializes from MAE ViT-Tiny. Distillation YAML points to an author-local frame checkpoint; sparse YAML points to an author-local distillation checkpoint.
- Unless `TRAIN_CLS` is enabled, no module is explicitly frozen. Optimizer groups normal backbone parameters at multiplied LR and output/embedding/extension parameters at base LR (`lib/train/base_functions.py:250-294`).
- Sparse training explores sequences under `no_grad`, then iterates one sequence at a time for backward. It enables anomaly detection and hard-codes gradient clipping at 100 although YAML records 0.1 (`lib/train/trainers/ltr_seq_trainer_sparse.py:57-143`).
- No activation-checkpoint call was found. AMP support exists elsewhere but all released stage YAMLs disable it; the sparse trainer’s declared scaler/autocast imports are not used in its backward loop.

### G. Profiling and export evidence

- `tracking/profile_model.py` defaults to `fartrack_seq/fartrack_tiny_seq_224_full`, imports `lib.models.fartrack_seq`, and only constructs that model when the script is `fartrack_seq`; it is not a final sparse profiler (`tracking/profile_model.py:18-29,73-142`).
- Its synthetic input uses one template and four random sequence tokens rather than the final five-template, 445-token masked state.
- It uses THOP and wall-clock CUDA timing without explicit synchronization around each measurement.
- No end-to-end ONNX exporter, TensorRT/Torch-TensorRT builder, engine wrapper, or Jetson path was found.
- `PreprocessorX_onnx` supplies NumPy normalization only; no exporter consumes it (`lib/test/tracker/data_utils.py:34-46`).
- Core final-sparse modules use standard PyTorch operations. A vendored PreciseRoIPooling CUDA extension exists elsewhere in the repository but is not referenced by the audited FARTrackSparse path.
- Export-sensitive runtime structure includes a Python list/`try` template stack, string-valued stage branches, tensor `.item()` control flow, `argsort` with nested indexed writes, external mutable history, direct `.cuda()`, deprecated `np.bool` in the unused ONNX preprocessor, and deprecated `torch.range` in coordinate expectation (`lib/models/fartrack_sparse/base_backbone.py:169-214,288-365`; `lib/test/tracker/data_utils.py:6-46`; `lib/test/tracker/fartrack_sparse.py:368-373`).
- README says to use a CUDA 12.2 environment, while `FARTrack_env_cuda122.yaml` pins CUDA toolkit 11.3.1 and PyTorch 1.11 CUDA 11.3 (`README.md:55-60`; env file `:70,301-302`).

### H. HG4 evidence package — no decision

Evidence relevant to a single RTX 3060 12 GB:

- The final audited network has explicit small dimensions and released stage/checkpoint resources.
- The documented research path is three stages, uses four-process commands, includes two 500-epoch stages, and provides no single-3060 memory result.
- Sparse training uses 32-frame sequences, batch 8, exploration storage, and sequential backward; author-local prerequisite checkpoint paths require normalization.
- No single-GPU run, memory peak, or reproduction was performed.

**HG4 = PENDING**

### I. HG5 evidence package — no decision

Structural evidence relevant to Jetson Nano:

- All 15 blocks retain a full 445-token dense attention shape; IFAS is masking rather than physical sequence shrink.
- Per-frame mask generation uses `argsort`, nested Python loops, and four candidate mask allocations.
- Every frame re-embeds all five template images.
- Template and mask histories retain uncapped CUDA tensors.
- Direct `.cuda()`, CPU/NumPy cropping, GPU tensor construction, host `.tolist()`, and Python tracker state form an end-to-end boundary outside the model.
- No export, engine, Nano latency, memory, power, thermal, or numerical-parity evidence exists.

**HG5 = PENDING**

### J. Code-visible cost sites

| Label | Site |
|---|---|
| CODE FACT — inspected | 15 blocks each compute QKV and full 445×445 attention |
| CODE FACT — inspected | detached attention is accumulated from every block to generate the next mask |
| CODE FACT — inspected | per-frame IFAS performs argsort plus nested Python writes for 25/50/75/90 masks |
| CODE FACT — inspected | five template images are patch-embedded on every frame |
| CODE FACT — inspected | four CUDA history lists and template history grow without a cap |
| ENGINEERING TARGET TO PROFILE | attention projection/matmul versus mask generation separately |
| ENGINEERING TARGET TO PROFILE | steady-state memory growth over long sequences |
| ENGINEERING TARGET TO PROFILE | CPU crop, CUDA allocation/copy, model, decoding, template crop, and host output separately |
| ENGINEERING TARGET TO PROFILE | a fixed 15/10/6 implementation only after exact Nano/Pico graphs are located |

### K. Unresolved items

1. Exact Nano/Pico config, layer-stop mechanism, and checkpoint mapping: **NOT FOUND**.
2. Intended role of prior bbox trajectory versus its unconsumed final-sparse implementation.
3. Intended use of 50/75/90% masks, which are stored but not selected by active inference.
4. Official checkpoint metadata/config names disagree with the checked-in `*_224_full` YAML names; clean mapping and prerequisite bootstrap remain unresolved.
5. Working final-sparse profiler and end-to-end export: **NOT FOUND**.
6. CUDA/PyTorch environment identity: README and environment file disagree.

## 7. CX014 — GOT-Edit

### A. Provenance and audited configuration

- **Repository:** `chenshihfang/GOT`
- **Pinned ref:** `b2ee0b9792db634a880189e8189542953af0d223`
- **Registered source:** [R25](../../references/references.md#r25)
- **Audited released parameter:** `pytracking/pytracking/parameter/tomp/got_edit_378_dino_da3.py`
- **Audited training setting:** `pytracking/ltr/train_settings/tomp/GOT-Edit_DA3_378.py`

The public `GOT_Edit()` experiment selects this parameter directly (`pytracking/pytracking/experiments/myexperiments_gotedit.py:11-18`).

**RESOURCE AVAILABILITY FACT:** the official README provides model/result download links, while the parameter file retains the placeholder checkpoint path `/path_to/GOT_Edit_378_Vast_DA3.tar`; a checkpoint was not bundled in the Git tree (`README.md`; `pytracking/pytracking/parameter/tomp/got_edit_378_dino_da3.py:44-49`).

**CODE FACT — inspected:** the released 378 parameter selects the DA3 geometry path. The model header describes 252 as source-edit guidance—change `DinoPatch`, matching tracker constants, and the semantic projection—not as a separate released parameter/configuration (`pytracking/ltr/models/tracking/tompnet_JEPAp_vggt.py:1-12,53-60,111-130`).

### B. Model construction

The inspected construction combines two foundation-model feature paths with a ToMP prediction head:

| Component | Pinned implementation | Audited shape/configuration |
|---|---|---|
| Semantic feature extractor | DINOv2 ViT-L/14 loaded through Torch Hub | layers 4, 11, 17, and 23 are averaged; 1,024 channels are projected to 1,024 and pooled to 27×27 |
| Geometry extractor | `depth-anything/da3-large` | vendored DA3-L uses a DINOv2 ViT-L encoder and DPT head; the returned 128-channel feature is projected to 256 |
| Semantic/geometry fusion | `DiNO_VGGT_Gate` | local convolutional gate over 256-channel inputs |
| ToMP head | filter predictor, classifier, and bbox regressor | width 256; six encoder and six decoder layers; eight heads; FFN width 2,048; filter size 1 |

The model entry is the decorated `tompnet50(...)` constructor in `pytracking/ltr/models/tracking/tompnet_JEPAp_vggt.py:683-770`.

Evidence: `pytracking/ltr/models/tracking/tompnet_JEPAp_vggt.py:162-202,254-282,683-770`; `pytracking/ltr/models/transformer/heads.py:510-597,2138-2182,2485-2524`; `pytracking/ltr/Depth-Anything-3/src/depth_anything_3/configs/da3-large.yaml:1-28`; `pytracking/ltr/train_settings/tomp/GOT-Edit_DA3_378.py:86-99,330-340`.

**CODE FACT — inspected:** DA3-L itself contains a large DINOv2 feature encoder. The audited runtime therefore loads one DINOv2 ViT-L semantic extractor and another ViT-L-class encoder inside the geometry model; this is not one shared backbone.

### C. Runtime graph and execution frequency

The parameter records a 27×27 tracking feature grid, stride 16, nominal 432-pixel sample crop, sample-memory size 2, and update-confidence threshold 0.9 (`pytracking/pytracking/parameter/tomp/got_edit_378_dino_da3.py:20-40,52-65`). Before feature extraction, the tracker resizes model inputs to 378×378, equal to 27 DINO patches of size 14 (`pytracking/pytracking/tracker/tomp/tomp.py:474-565,569-629`).

| Stage | Initialization | Each tracked frame |
|---|---:|---:|
| CPU crop/resize and host-to-device movement | yes | yes |
| Semantic DINOv2 ViT-L | initial reference | current frame |
| DA3-L geometry | no | concatenated initial reference, dynamic reference, and current frame |
| Semantic/geometry fusion and JEPA predictor | no | yes |
| ToMP filter prediction | initial semantic state | twice: semantic and fused paths |
| AlphaEdit covariance/SVD/projector | no | yes |
| Classifier, localization, and bbox regressor | no | yes |
| Conditional sample/reference update | initializes state | confidence/status dependent |

**CODE FACT — inspected:** two CUDA streams launch the current-frame semantic path and the three-frame geometry path concurrently. The default tracker calls the non-cache DA3 extraction path, so geometry for the two reference frames is recomputed along with the current frame on every tracked frame (`pytracking/pytracking/tracker/tomp/tomp.py:218-231,497-563`).

At the model boundary, the current semantic input is a 3×378×378 tensor and yields a 1,024×27×27 semantic feature before the 256-channel ToMP-head projection. Geometry receives `[B,3,3,378,378]`, takes DA3's final 128-channel DPT feature for each of the three frames, and maps it to 256 channels (`pytracking/ltr/models/tracking/tompnet_JEPAp_vggt.py:161-202,254-282`).

The classifier path predicts filters for the semantic and fused features, obtains a JEPA-predicted geometry delta, applies AlphaEdit, and then evaluates classification and bbox heads (`pytracking/pytracking/tracker/tomp/tomp.py:327-390`). Localization and output conversion include `.cpu()` and `.item()` synchronization points before the optional memory update.

### D. AlphaEdit operator trace

The code names the online-editing helper `Head.AlphaEditRefiner_mix`; it is implemented in `pytracking/ltr/models/transformer/heads.py:188-349` and is invoked per frame in `pytracking/pytracking/tracker/tomp/tomp.py:377-383`.

**CODE FACT — inspected:** the active steps are:

1. whiten the encoded feature;
2. form a 256×256 channel covariance with batched matrix multiplication;
3. add adaptive ridge regularization;
4. call `torch.linalg.svd`;
5. select null-space directions with a normalized-energy threshold;
6. construct `U diag(mask) U^T` using batched matrix multiplications;
7. project the geometry delta and apply a fixed trust factor of 0.2 to a local filter.

The active settings enable adaptive covariance regularization with normalized-energy threshold 0.02, `gamma=0.003`, and trust 0.2 (`pytracking/ltr/models/transformer/heads.py:65-106`).

No inverse, linear solve, eigendecomposition, QR decomposition, optimizer step, or persistent `nn.Parameter` mutation was found in this runtime path. The refined filter is local to the current frame and is recomputed rather than stored as model state.

**ENGINEERING TARGET TO PROFILE:** separate covariance construction, SVD, projector formation, and projected-filter application. Their measured share of frame latency and workspace memory is unknown.

### E. Temporal, template, and memory behavior

- The ToMP sample memory stores semantic features, labels, boxes, and weights in fixed tensors of size 2.
- Semantic reference features are cached in that sample memory; the DINOv2 semantic backbone therefore processes the current frame, not the reference images, during ordinary tracking.
- The geometry image buffer is allocated with three slots. Geometry extraction reads the initial reference, the current dynamic reference, and the current frame.
- Slot 0 remains the initial reference; slot 1 is replaced by the latest accepted high-confidence reference. The update also writes slot 2, but the geometry slice used by extraction does not read that slot (`pytracking/pytracking/tracker/tomp/tomp.py:167,249-256,487,519-523,623-625`).
- The update requires a state other than `not_found`/`uncertain` and a raw maximum score above 0.9.
- `train_skipping`, `net_opt_iter`, `net_opt_update_iter`, and `net_opt_hn_iter` are declared in the parameter but no corresponding online-optimization call was found in this tracker.
- `target_scales` appends on every found frame without a cap; later use slices recent history. `second_ref_history` and `confidence_history` are declared but not consumed.
- `num_stored_samples` can grow beyond nominal capacity, although tensor slices remain bounded by the fixed tensors.

**CODE FACT — inspected:** persistent tracker state changes the samples/reference images supplied to later frames. AlphaEdit itself does not persist a refined network/filter parameter between frames.

### F. Training evidence and gradient boundary

The released DA3-378 training setting records:

| Item | Released setting |
|---|---|
| Data | VastTrack, LaSOT, GOT10K, TrackingNet, COCO |
| Temporal sampling | two training references and one test frame |
| Global samples | 200,000 per epoch; validation 10,000 |
| Schedule | 20 epochs; milestones 10, 15, 20, 25; gamma 0.2 |
| Hardware command/config | four GPUs; per-GPU batch 16; nominal global batch 64 |
| Optimizer | AdamW; most trainable groups LR 1e-4; DoRA default LR 2e-5; WD 1e-4 |
| Precision | DeepSpeed FP16 false; BF16 false; `GradScaler` false |
| Checkpointing | transformer-encoder activation checkpointing enabled when gradients are present |

Evidence: `pytracking/ltr/train_settings/tomp/GOT-Edit_DA3_378.py:37-99,126-191,260-340`; `pytracking/ltr/models/transformer/transformer.py:237-368`; README training command.

The script freezes the base model, re-enables JEPA predictors, geometry/semantic adapters, fusion, projections, and head modules, and injects DoRA adapters into DA3. The optimizer includes those adapter parameters.

**CODE FACT — inspected:** the audited model wraps DA3 feature extraction in `torch.no_grad()` (`pytracking/ltr/models/tracking/tompnet_JEPAp_vggt.py:254-263`). The public DA3 API and underlying `forward_dpt_features` path are also decorated with `torch.no_grad()` (`pytracking/ltr/Depth-Anything-3/src/depth_anything_3/api.py:100-126`; `pytracking/ltr/Depth-Anything-3/src/depth_anything_3/model/da3.py:100-140`). Thus the inspected forward path does not carry an autograd graph from the loss into the DA3/DoRA modules even though the training setting registers those adapter parameters with the optimizer. The trainable `DA3_bkMlp` executes after this boundary and can still receive gradients from its detached DA3 input.

**OPEN QUESTION:** whether the released DA3 training setting intentionally freezes the injected DoRA path, expects a different forward implementation, or contains a training integration defect was not resolved by source inspection. No training run was performed.

Additional training/runtime facts:

- geometry extraction locally uses BF16 autocast on Ampere-class devices while the semantic path remains FP32; the DeepSpeed training precision switches remain false;
- only the ToMP transformer encoder is covered by the active checkpointing branch;
- the released setting contains a placeholder pretrained path and no one-GPU/RTX-3060-12-GB recipe.
- the 200,000 training samples are divided by distributed world size before each rank's sampler is constructed, so 200,000 is the nominal global per-epoch count (`pytracking/ltr/train_settings/tomp/GOT-Edit_DA3_378.py:81-84,208-219`).

### G. Geometry variants and repository anomalies

**CODE FACT — inspected:** the default constructor enables DA3. VGGT and StreamVGGT construction lines are commented in the same builder; switching geometry backbones requires source edits rather than a configuration-only selection (`pytracking/ltr/models/tracking/tompnet_JEPAp_vggt.py:111-130,683-724`).

- Separate DA3, VGGT, and StreamVGGT training-setting files exist, but they call the same default constructor; several variant-specific attributes referenced by non-DA3 settings correspond to commented construction lines.
- The tracker has a special extraction branch only for the literal `VGGT`; other values, including `StreamVGGT`, follow the DA3 branch unless code is changed.
- The repository's lowercase `pytracking/ltr/streamvggt` entry is a Git symbolic link whose target is the absolute placeholder `/home/your_path/GOT/pytracking/ltr/StreamVGGT/src/streamvggt/`. A separate uppercase `StreamVGGT` tree is present. This causes portability and case-collision ambiguity on Windows.
- `pytracking/cotracker2` is another absolute Git symbolic link, targeting an author-local path.
- StreamVGGT code contains an author-local default checkpoint path.
- The installation script pins a PyTorch/CUDA context that differs from requirements inside vendored geometry projects.

**OPEN QUESTION:** a directly executable mapping from each named geometry variant to its intended constructor, checkpoint, and tracker extraction branch was not established. This report therefore treats only the released DA3-378 parameter as the audited runnable target.

### H. Profiling and export evidence

- `pytracking/ltr/profiling/profile_tomp_components.py` contains fvcore/THOP/ptflops component accounting with fixed 27×27/378 dimensions; its latency block is commented and the script ends at a blocking `input()`.
- The profiler targets VGGT-oriented component wrappers rather than the active DA3 runtime, and the inspected DA3 training setting does not invoke it.
- The component profiler does not cover AlphaEdit's per-frame SVD or the complete tracker lifecycle.
- No end-to-end GOT-Edit ONNX exporter, TensorRT/Torch-TensorRT builder, Jetson wrapper, or numerical-parity script was found.
- ONNX references inside vendored geometry code concern an auxiliary sky-segmentation model, not the tracking graph.
- Runtime setup attempts DeepSpeed inference with hard-coded BF16 if DeepSpeed imports; otherwise it calls `torch.compile(fullgraph=False)` (`pytracking/pytracking/tracker/tomp/tomp.py:39-55,107-136`). Direct CUDA streams and host-side tracker control remain outside a single tensor-only graph.
- DINO Torch Hub and DA3 model identifiers are not accompanied by revision pins or weight checksums in the audited source.

**RESOURCE AVAILABILITY FACT:** component profiling code exists. **OPEN QUESTION:** it does not establish end-to-end DA3-378 latency, memory, exportability, or Jetson Nano behavior.

### I. HG4 evidence package — no decision

Evidence relevant to a single RTX 3060 12 GB:

- The official setting uses two ViT-L-class foundation paths, four GPUs, batch 16 per GPU, 200,000 samples per epoch, and 20 epochs.
- Base freezing, local reduced-precision geometry execution, and partial transformer activation checkpointing are present.
- No one-GPU batch/accumulation recipe, measured memory peak, clean checkpoint bootstrap, or RTX 3060 reproduction is provided.
- The `no_grad()`/DoRA boundary must be resolved before the intended trainable set can be treated as established.

**HG4 = PENDING**

### J. HG5 evidence package — no decision

Structural evidence relevant to Jetson Nano:

- one semantic ViT-L pass runs on the current frame;
- DA3-L processes a three-frame stack on every frame, including both reference images;
- the prediction path includes two filter-prediction passes plus fusion and JEPA computation;
- a 256×256 channel covariance/SVD/projector is formed on every frame;
- CUDA streams, `.cuda()` placement, host crop/control flow, CPU synchronization, and either DeepSpeed-BF16 or `torch.compile` startup are built into the Python runtime;
- no complete fixed-shape exporter, TensorRT engine, Nano result, or precision-parity evidence exists.

**HG5 = PENDING**

### K. Code-visible cost sites and unresolved items

| Label | Site |
|---|---|
| CODE FACT — inspected | current-frame semantic DINOv2 ViT-L inference |
| CODE FACT — inspected | DA3-L geometry inference over initial reference, dynamic reference, and current frame on every frame |
| CODE FACT — inspected | two ToMP filter-prediction paths plus fusion/JEPA computation |
| CODE FACT — inspected | per-frame 256×256 covariance, SVD, null-space projector, and projected update |
| CODE FACT — inspected | reference geometry is recomputed rather than read from the available DA3 cache helpers |
| CODE FACT — inspected | CPU crop/control and `.cpu()`/`.item()` synchronization remain in the tracker loop |
| ENGINEERING TARGET TO PROFILE | synchronized per-component and end-to-end latency, peak/steady memory, and sustained behavior |
| ENGINEERING TARGET TO PROFILE | cache-versus-recompute behavior for reference geometry, subject to numerical equivalence |
| ENGINEERING TARGET TO PROFILE | fixed-signature export boundary and numerical parity for supported operators/precision |

Unresolved items:

1. Intended gradient path and effective trainable status of DA3 DoRA adapters.
2. Directly executable VGGT/StreamVGGT variant mapping without manual source edits.
3. Checkpoint checksum, exact missing/unexpected-key state, and clean-machine bootstrap.
4. A profiler covering the released DA3-378 tracker including AlphaEdit SVD and host-side work.
5. End-to-end export, TensorRT operator/precision validation, and target-device measurements.
6. Purpose of geometry-buffer slot 2 and uncapped Python histories.

## 8. Batch completion and locked next state

| Candidate | Final code-audit state | HG4 | HG5 |
|---|---|---|---|
| CX007 SpikeTrack | CODE AUDIT COMPLETE | PENDING | PENDING |
| CX009 UETrack | CODE AUDIT COMPLETE | PENDING | PENDING |
| CX010 UTPTrack | CODE AUDIT COMPLETE | PENDING | PENDING |
| CX013 FARTrack | CODE AUDIT COMPLETE | PENDING | PENDING |
| CX014 GOT-Edit | CODE AUDIT COMPLETE | PENDING | PENDING |

Batch B was not activated. No scientific-audit conclusion or candidate-gate value was changed.

BATCH A CODE EVIDENCE EXTRACTION:
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
