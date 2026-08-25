# Stage 3A — G1 independent code-gap formulation

Date: **2026-08-25**

Lane: **Codex worker — independent code and engineering formulation**

Scope: **CX007 SpikeTrack, CX009 UETrack, CX010 UTPTrack, CX013 FARTrack, and CX024 DAM4SAM only**

## 1. Boundary and evidence discipline

This report formulates implementation-grounded, falsifiable gap questions. It does not perform a literature novelty search, decide HG6, score or rank a candidate, form a shortlist, select a baseline, or design a proposed architecture. The Manager G1 scientific-formulation artifact was not read before or during this independent formulation.

The labels below have their literal meanings:

- **CODE FACT — inspected:** visible in the exact pinned official implementation or in a bounded project characterization of that implementation.
- **FACT — cited:** stated by the registered official publication or official repository.
- **HYPOTHESIS — untested:** a proposed relationship that must survive the specified rejection test.
- **ROBUSTNESS SIGNAL NOT ESTABLISHED:** no candidate-specific residual weakness acceptable under the Stage-3 protocol was found.

Paper/repository pairs are [R18/R19] for SpikeTrack, [R20/R21] for UETrack, [R22/R23] for UTPTrack, [R11/R12] for FARTrack, and [R29/R30] for DAM4SAM. Code paths below are relative to those exact pinned repositories. The main implementation evidence was carried forward from the completed Batch-A/Batch-B audits and the bounded Stage-2B characterization; no training or full benchmark was run here.

| Candidate | Independent readiness | Missing element, if any |
|---|---|---|
| CX007 SpikeTrack | **GAP_READY** | none at Stage-3A formulation level |
| CX009 UETrack | **GAP_INCOMPLETE** | specific residual generic-RGB robustness signal |
| CX010 UTPTrack | **GAP_INCOMPLETE** | pruning-policy-linked residual robustness signal |
| CX013 FARTrack | **GAP_READY** | none at Stage-3A formulation level |
| CX024 DAM4SAM | **GAP_INCOMPLETE** | specific residual failure of final DAM4SAM |

These states are not HG6 decisions.

---

## 2. CX007 — SpikeTrack

### A. Candidate boundary

- **Exact anchor:** `experiments/spiketrack/spiketrack_s256_t1.yaml` and its released Small-256 T1 checkpoint, at `faicaiwawa/SpikeTrack@1537db51a1cc9f6e30cce469fba3e51f5721b3d0`. Small-256 T3 is retained only as the controlled template-time comparison.
- **Core mechanism that must remain:** the SDTV3 spiking backbone, cached template/search split, six template-to-search Memory Retrieval Modules (MRMs), and center head.
- **Permissible diagnostic variation:** zero or scale one retrieval residual, expose per-MRM/cache/gate state, or compare fixed T1/T3 template modes while holding weights and the rest of the tracker fixed.
- Replacing SDTV3 or the MRM retrieval path with an unrelated tracker would cross the candidate boundary.

### B. Code-visible compute observations

| Observation | Evidence |
|---|---|
| **CODE FACT — inspected:** six MRMs execute at fixed sites on every search frame. | `lib/models/spiketrack/sdtv3_search_inference.py:725-776` |
| **CODE FACT — inspected:** each MRM repeats the search query over the configured template/time dimension. T3 additionally applies a channel-wise temporal gate to reduce three template-time outputs to one search step. | `sdtv3_search_inference.py:246-287,405-437` |
| **CODE FACT — inspected:** a qualifying T3 refresh recomputes the complete template encoder and all six retrieval caches; T1 has no update. | `lib/test/tracker/spiketrack_inf.py:59-121` |
| **CODE FACT — inspected:** T1 state is bounded to six cache tensors totaling 223,232 bytes; T3 uses 669,696 bytes. No state grows with sequence length. | Stage-2B bounded characterization |
| **CODE FACT — inspected:** interleaved MX250 model-only medians were 269.740 ms for T1 and 367.390 ms for T3; template/cache medians were 200.690 ms and 413.130 ms. These numbers locate a comparative cost boundary and are not Nano estimates. | Stage-2B bounded characterization |
| **CODE FACT — inspected:** spike values feed ordinary dense clamp/round/divide, Conv1d/Conv2d, and matrix multiplication. There is no persistent membrane across video frames or event-driven sparse kernel in the released path. | `lib/models/spiketrack/ni_lif.py:5-88`; `sdtv3.py` |

None of these observations is labeled redundancy merely because it has cost.

### C. Code/source-supported robustness signal

**FACT — cited:** the official paper explicitly identifies difficulty in scenes containing visually similar objects and attributes it to insufficient fine-grained discrimination in the released formulation [R18]. Its qualitative analysis also reports that similar-object interference still affects the tracker even when the correct target is ultimately recovered.

The inspected code and current bounded characterization do not reproduce that failure or attribute it to a particular MRM. The accepted signal is therefore paper-level; the implementation coupling remains untested.

### D. Falsifiable coupling hypothesis

**HYPOTHESIS — untested:**

> Under stable frames without a visually similar distractor, the marginal contribution of some fixed MRM retrieval residuals or T3 template-time interactions may be unnecessary for preserving the target score margin. Under frames with target–distractor visual ambiguity, stronger or more selective use of particular scale/template retrieval contributions may be required to preserve target-versus-distractor separation and tracking success.

Here, path `Y` is the six-stage cached MRM retrieval path, including T3 repetition/gating; robustness outcome `W` is target-versus-strongest-distractor center-score margin plus success/precision on the same frames.

**Reject the hypothesis if:**

- one-at-a-time MRM ablation effects do not interact with distractor versus non-distractor conditions;
- per-stage residual magnitude, score-map change, or T3 gate behavior does not distinguish those conditions;
- paired T1/T3 behavior has no condition-specific accuracy interaction; or
- preserving the measured useful retrieval path fails to improve target–distractor separation on reproduced failure frames.

### E. Minimum falsification instrumentation

1. Add read-only hooks before and after each of the six retrieval residuals to record residual norm, score-map change, and synchronized module latency.
2. Add deterministic inference-only one-MRM-at-a-time zero-residual controls while retaining each block's non-retrieval path.
3. Run T1 and T3 checkpoints on the same predeclared similar-distractor and non-distractor frames; log T3 gate weights, template ages, refresh events, confidence, and steady versus refresh-frame latency.
4. Record target and strongest-distractor score peaks, predicted box, IoU/center error, success/precision, and per-MRM ablation delta.
5. Stop if no reproducible condition-by-MRM interaction appears. These hooks are diagnostics, not a proposed adaptive runtime.

### F. HG6 mechanism vocabulary

- **Precision terms:** `frame-conditioned memory retrieval tracking`, `stage-selective MRM visual tracking`, `similar-distractor template retrieval`, `adaptive multi-template fusion spiking tracker`, `conditional template-search retrieval`.
- **Recall terms:** memory retrieval gating, target–distractor discrimination, selective template interaction, stage-wise adaptive computation, query-conditioned memory access, template reliability gating.
- **Synonyms:** conditional MRM, retrieval residual selection, dynamic retrieval depth, template-time selection, fine-grained distractor discrimination, conditional memory read.
- **Adjacent-field terms:** dynamic-depth vision transformer, adaptive computation time, conditional computation SNN, spike sparsity acceleration, video-memory retrieval gating, mixture-of-depths.

No search was executed with these terms.

### G. Known collision boundary

- SpikeTrack already contributes the SDTV3 spiking tracker, six MRMs, cached template encoding, T3 temporal gating, and periodic confidence-controlled template refresh.
- Generic SNN early exit, dynamic depth, template gating, or memory selection is not presumed new and requires mechanism-level HG6 review.
- Duplicate box decoding, export repair, TensorRT porting, dense-kernel optimization, quantization, or moving host work off Python are ordinary engineering.
- The candidate-specific question is the condition-by-retrieval interaction under similar-object ambiguity, not “skip expensive modules.”

### H. Independent status

**GAP_READY**

The exact compute site, author-stated residual robustness signal, falsifiable coupling, rejection observations, and minimum hooks are concrete enough for later mechanism-level novelty search. This does not mean HG6 PASS.

---

## 3. CX009 — UETrack

### A. Candidate boundary

- **Exact anchor:** `experiments/uetrack/uetrack_base.yaml`, at `kangben258/UETrack@fd13b0eaf16d51536008295f3b27807c69eaad50`.
- **Configuration:** `fastitpnt_layer6`, stage depths `[1,1,6]`, widths `[96,192,384]`, eight experts, TP-MoE in final-stage block index 5, 112×112 template, and 224×224 search.
- **Core mechanism that must remain:** the unified six-channel Fast-iTPN student, TP-MoE representation path, center prediction, and the TAD-trained student boundary.
- **Permissible diagnostic variation:** inference-only expert-output masks, fixed expert modes, router/output logging, and isolated measurements of the template/text paths.
- Removing TP-MoE would stop testing the defining inference mechanism. Removing objects that inference never calls is deployment cleanup, not a scientific gap.

### B. Code-visible compute observations

| Observation | Evidence |
|---|---|
| **CODE FACT — inspected:** pure RGB duplicates each RGB crop into both three-channel halves; no separate depth/thermal/event encoder executes. | `lib/test/tracker/uetrack.py`; `lib/train/dataset/depth_utils.py` |
| **CODE FACT — inspected:** the no-language runtime sequence is 247 tokens: class 1, search 196, template 49, zero-text 1. | `lib/models/uetrack/fastitpn.py:1131-1214` |
| **CODE FACT — inspected:** TP-MoE pads to 248 tokens, constructs a dense 248×248 routing relation, and executes all eight experts every frame; dispatch/combine are soft and dense rather than top-k. | `fastitpn.py:478-534` |
| **CODE FACT — inspected:** the static template persists as pixels but is patch-embedded and processed through the joint encoder every frame. | `lib/test/tracker/uetrack.py:106,142-147`; `fastitpn.py:1131-1207` |
| **CODE FACT — inspected:** zero-token CLIP text encoding executes once per sequence and its projected token remains in every frame's transformer sequence. | `lib/models/uetrack/uetrack.py:175-180`; tracker path |
| **CODE FACT — inspected:** full CLIP and the task decoder remain resident although their main paths are not invoked by ordinary RGB inference; the center box is decoded twice. | `uetrack.py:346-366`; tracker/decoder path |

The resident-unused objects, one-time zero-text setup, duplicate decode, and static-template reprocessing are separable engineering observations. They do not establish a robustness contribution.

### C. Code/source-supported robustness signal

**ROBUSTNESS SIGNAL NOT ESTABLISHED**

The paper discusses unreliable teacher supervision for training samples containing blur, occlusion, distraction, or deformation, but TAD is already UETrack's training-time response to that issue [R20]. The inspected official source and current project evidence do not establish a residual generic-RGB failure, attribute deficit, or reproduced failure for UETrack-B. The expert-count ablation and the observation that excessive experts can be inefficient likewise do not prove a tracking failure caused by dense all-expert execution.

### D. Falsifiable coupling hypothesis

**HYPOTHESIS — provisional and untested:**

> Under stable RGB frames where expert outputs and routing assignments are strongly concordant, dense all-expert TP-MoE execution may be unnecessary. Under a future, separately established RGB failure condition where expert outputs diverge and localization is sensitive to expert ablation, stronger or selective expert use may be required to preserve robustness on that condition.

Robustness outcome `W` is intentionally not asserted until a reproducible residual slice exists.

**Reject the hypothesis if:**

- expert agreement, routing entropy, or output diversity does not predict localization change under controlled expert bypass;
- fixed expert ablations affect stable and difficult/error frames in the same way;
- no reproducible RGB failure slice correlates with expert-path sensitivity; or
- apparent gains come only from deleting inference-unused CLIP/task objects rather than changing TP-MoE behavior.

### E. Minimum falsification instrumentation

1. Add read-only TP-MoE hooks for routing logits, dispatch, combine weights, and per-expert outputs with frame identity.
2. Add deterministic inference-only masks after expert output, bypassing one expert or a fixed subset and renormalizing combine weights without changing the checkpoint.
3. Record full-versus-ablated boxes, score-map delta, IoU/center error, expert-output similarity, routing entropy, module latency, and workspace.
4. Attribute expert sensitivity to predeclared RGB challenge/error frames. If no specific residual failure can be reproduced, stop before HG6.
5. Profile static-template reprocessing and removal of inference-unused residents separately so engineering savings cannot be mistaken for a robustness coupling.

### F. HG6 mechanism vocabulary

- **Precision terms:** `UETrack TP-MoE conditional computation`, `token-pooling mixture of experts visual tracking`, `dense soft routing single object tracking`, `all-expert execution tracker`, `expert agreement visual tracking`.
- **Recall terms:** mixture-of-experts visual tracking, sparse MoE tracking, conditional expert activation, dynamic expert routing, adaptive-computation tracker, expert specialization.
- **Synonyms:** expert selection, expert gating, expert sparsification, top-k routing, soft routing, expert collapse, routing entropy, conditional FFN.
- **Adjacent-field terms:** efficient-ViT MoE, dynamic neural networks, mixture-of-depths, multimodal MoE, conditional computation, token/channel conditional execution.

No search was executed with these terms.

### G. Known collision boundary

- TP-MoE, local token pooling, continuous soft expert assignment, and TAD are UETrack's own contributions.
- The paper already compares a gated-MoE replacement; simply replacing soft routing with generic gating cannot be presumed novel.
- TAD already performs sample-conditioned rejection of unreliable teacher distillation.
- Plain template caching collides with template-once/asymmetric execution already represented in the project by AsymTrack.
- Removing resident-unused components, duplicate decode, hard-coded CUDA, export repair, quantization, and generic expert pruning are engineering or adjacent-field prior-art risks.

### H. Independent status

**GAP_INCOMPLETE**

The all-expert compute site and falsification hooks are concrete, but the required candidate-specific residual robustness signal is absent. A bounded failure/attribute diagnostic must establish outcome `W` before HG6.

---

## 4. CX010 — UTPTrack

### A. Candidate boundary

- **Exact anchor:** RGB `UTPTrack-O/experiments/ostrackcmp/ceatetta_256_r7_all.yaml` with the strict-matched `OSTrackCMP_ep0300.pth.tar`, at `EIT-NLP/UTPTrack@84e0f49711254a44f5308faaa9a2405db1964dd7`.
- **Configuration:** ViT-B/16, width 768, 12 blocks, 128×128 static and dynamic templates, 256×256 search, and fixed retention ratio 0.7.
- **Core mechanism that must remain:** unified physical compaction of search/static/dynamic streams through CE/DTE/STE, foreground-aware static selection, search-grid restoration, and center head.
- **Permissible diagnostic variation:** fixed keep-rate/stream controls, retained-index hooks, and controlled template-agreement perturbations while preserving the trained graph and prediction head.
- Replacing unified pruning with another tracker or merely adding more ordinary token pruning crosses or trivializes the gap boundary.

### B. Code-visible compute observations

| Observation | Evidence |
|---|---|
| **CODE FACT — inspected:** both raw templates are patch-embedded every frame; the static initial template and confidence-updated dynamic template are not feature-cached. | `UTPTrack-O/lib/models/ostrackcmp/vit_ceatetta.py:221-259`; tracker `ostrackcmp.py:66-137` |
| **CODE FACT — inspected:** each scheduled transformer block computes attention before pruning. Six block positions invoke three CE, three DTE, and three STE full-sort operations. | `vit_ceatetta.py:44-84,156-184`; `compression/ce.py`; `compression/ate.py` |
| **CODE FACT — inspected:** search CE and dynamic-template elimination are guided by static-template center queries; static-template elimination also uses center/foreground bonuses. | `compression/ce.py:75-128`; `compression/ate.py:13-135` |
| **CODE FACT — inspected:** fixed 0.7 retention physically changes the 256-path sequence from 384 input tokens to 135 compact tokens; restoring search positions yields 302 tokens before the head. Retained counts are fixed but identities are content-dependent. | inspected token ledger |
| **CODE FACT — inspected:** the static `box_mask_z` is created at initialization and is not regenerated when the dynamic template changes. | tracker `ostrackcmp.py:66-88,120-137` |
| **CODE FACT — inspected:** fixed-shape ONNX retained physical pruning/restoration and achieved ONNX Runtime parity. That is deployment evidence, not proof of a robustness benefit or defect. | Stage-2B bounded export characterization |

### C. Code/source-supported robustness signal

**ROBUSTNESS SIGNAL NOT ESTABLISHED**

The inspected official sources and current project evidence contain no author-reported residual limitation, diagnostic attribute deficit, or reproduced failure tied to the fixed 0.7 rule or the static-guided policy. Generic assertions that occlusion or appearance change are difficult do not satisfy the Stage-3 requirement. The repository's positive pruning claims cannot be inverted into a failure claim.

### D. Falsifiable coupling hypothesis

**HYPOTHESIS — provisional and untested:**

> Under high agreement between the initial static template and the current target appearance, a smaller retained budget may preserve target-token coverage and tracking accuracy. Under a future, evidenced low-agreement condition in which the static template is stale while the dynamic template/search better represent the target, the fixed static-guided allocation may remove target-supporting search or dynamic-template tokens, so greater or stream-selective retention may be required to preserve robustness.

Path `Y` is the fixed CE/DTE/STE allocation and retained identity; outcome `W` is ground-truth target-token coverage, confidence calibration, and success/precision.

**Reject the hypothesis if:**

- controlled static-template degradation does not increase removal of target-supporting tokens or tracking error;
- keep-rate and stream ablations show no interaction with static/current agreement;
- leaving the suspected stream unpruned does not change reproduced failures; or
- only condition-independent latency changes remain.

### E. Minimum falsification instrumentation

1. Capture pruning scores, `global_index_x/sz/dz`, retained/removed indices, foreground masks, and stream lengths after the six pruning block positions.
2. Map retained/removed indices back to ground-truth target patches and record per-stream target-token recall.
3. Add deterministic inference-only `1.0` versus `0.7` keep-rate controls for CE, DTE, and STE separately on identical frames.
4. Create a bounded static-template-agreement diagnostic while holding the current search/dynamic inputs fixed; record boxes, confidence, IoU/center error, success/precision, token retention, and latency.
5. Measure template patch embedding separately only as an engineering control. Feature caching parity does not establish the proposed scientific relationship.

### F. HG6 mechanism vocabulary

- **Precision terms:** `static-template-guided token pruning tracking`, `stale-template token elimination`, `adaptive CE DTE STE retention`, `template-agreement-conditioned pruning`, `target-token preservation visual tracking`.
- **Recall terms:** uncertainty-aware token pruning, dynamic token budget, confidence-adaptive retention, multi-template token selection, foreground-biased pruning, token-pruning robustness.
- **Synonyms:** adaptive keep ratio, stream-wise retention, importance misranking, token survival, target-patch recall, conditional token allocation.
- **Adjacent-field terms:** dynamic ViT pruning, distribution-shift-aware token selection, uncertainty-conditioned computation, conditional attention, token restoration, robust feature selection.

No search was executed with these terms.

### G. Known collision boundary

- UTPTrack already contributes unified search/static/dynamic pruning, foreground-aware template pruning, physical compaction, and search restoration.
- Ordinary additional token removal, a new fixed keep ratio, or generic content-aware pruning cannot be claimed as new.
- Static-template feature caching, replacing full sort with TopK, ONNX/TensorRT work, and FP16/INT8 are engineering tasks.
- Any future adaptive-budget claim must be checked against dynamic token pruning, uncertainty-conditioned retention, and multi-template-selection mechanisms during HG6.

### H. Independent status

**GAP_INCOMPLETE**

The allocation rule, code hooks, and rejection test are concrete, but a pruning-policy-linked residual robustness signal is absent. A bounded failure/reproduction experiment must establish the proposed low-agreement condition before HG6. If it does not, the remaining opportunities are ordinary engineering or compression and should be rejected.

---

## 5. CX013 — FARTrack

### A. Candidate boundary

- **Exact anchor:** released final sparse Tiny path `experiments/fartrack_sparse/fartrack_sparse_224_full.yaml`, at `MIV-XJTU/FARTrack@5d3e4b90305c2e845340a39cb1ac9bb69c0c5180`.
- **Configuration:** ViT-Tiny/16, width 192, three heads, 12 base blocks plus three extension blocks, five 112×112 templates, one 224×224 search, and four coordinate-command tokens. Executable final-sparse Nano/Pico mappings remain **NOT FOUND**.
- **Core mechanism that must remain:** the TSSD-derived shallow tracker, five-template tracking formulation, coordinate-token prediction, and inter-frame attention sparsification (IFAS) mask propagation.
- **Permissible diagnostic variation:** offline control of active template identity/count, already generated IFAS masks, or injected history corruption while keeping the backbone, head, checkpoint, and task fixed.
- Replacing FARTrack with an external ReID/re-detector or long-term tracker crosses the boundary.

### B. Code-visible compute observations

| Observation | Evidence |
|---|---|
| **CODE FACT — inspected:** every frame embeds five templates into 245 tokens, one search into 196 tokens, adds four command tokens, and processes all 445 tokens through all 15 blocks. | `lib/models/fartrack_sparse/base_backbone.py`; tracker path |
| **CODE FACT — inspected:** IFAS masks attention entries but does not physically shorten Q/K/V or the 445×445 attention shape. | `lib/models/fartrack_sparse/vit.py:39-72` |
| **CODE FACT — inspected:** after the current full pass, IFAS accumulates detached attention across all blocks, sorts it, and creates 25/50/75/90% masks; active inference consumes only the 25% mask history. | `base_backbone.py:132-217,341-365`; tracker `:126-230` |
| **CODE FACT — inspected:** all five raw template crops are patch-embedded every frame. | `fartrack_sparse.py` model/tracker path |
| **CODE FACT — inspected:** every prediction is cropped and appended without a confidence gate; template and four mask histories grow without a sequence-length cap, although exponential sampling keeps five active entries. | `lib/test/tracker/fartrack_sparse.py:126-230,392-406` |
| **CODE FACT — inspected:** the passed previous-box trajectory values do not enter the final sparse token sequence; one network call produces all coordinate distributions. | `base_backbone.py:270-388` |

### C. Code/source-supported robustness signal

**FACT — cited:** the official template-count ablation reports a coupled cost/accuracy trade-off: increasing templates from one to five raises reported AO from 66.4% to 70.6% while MACs rise from 1.70 G to 2.65 G; moving beyond five reduces AO rather than continuing the gain [R11]. This establishes sensitivity to template quantity, not that an adaptive policy is already beneficial.

**FACT — cited:** the official appendix states that after prolonged tracking failure such as disappearance or occlusion, sampled templates may all become invalid and tracking accuracy can fall [R11].

**CODE FACT — inspected with direct robustness relevance:** the released final sparse tracker unconditionally appends the crop from every prediction and samples active entries without a reliability test. These facts establish a concrete validity risk but do not prove its frequency or causally explain every reported failure.

### D. Falsifiable coupling hypothesis

**HYPOTHESIS — untested:**

> Under stable tracking where active templates are valid and mutually consistent, re-embedding all five templates and applying full 445-token attention may be unnecessary. Under disappearance/occlusion recovery where validity is mixed and at least one reliable historical appearance remains, selective use of template-processing capacity may be required for robust recovery, while indiscriminate processing of invalid templates may be harmful.

Path `Y` is template identity/count plus its IFAS-visible content; outcome `W` is post-occlusion recovery success/error and tracking accuracy.

**Reject the hypothesis if:**

- active-template count or identity has no systematic interaction with stable versus post-occlusion performance;
- controlled invalid-template injection does not change prediction or recovery;
- template validity/disagreement does not predict which fixed mode performs better; or
- changing template computation produces only condition-independent speed changes.

### E. Minimum falsification instrumentation

1. Log sampled indices, template age, active identity, per-template IFAS occupancy, coordinate-logit entropy/margin, predicted box, and ground-truth error where available.
2. Add fixed inference-only active-template count/identity modes while keeping weights and search input unchanged.
3. Expose the already generated all-visible and 25/50/75/90% masks as controlled offline modes; report separately that masking alone does not shrink the tensor shape.
4. Inject fixed off-target/distractor crops into selected history slots at predeclared frames.
5. Compare stable, disappeared/occluded, and re-entry segments under identical modes; record recovery and separate template-embedding, transformer-attention, and mask-generation cost.
6. Measure uncapped history/device-memory growth separately. Bounding history alone is engineering, not evidence for the coupling.

### F. HG6 mechanism vocabulary

- **Precision terms:** `invalid template single object tracking compute allocation`, `template validity adaptive template count tracker`, `reliability-conditioned template selection visual tracking`, `template corruption multi-template token processing`, `occlusion disappearance template contamination`.
- **Recall terms:** reliability-aware template update, quality-aware template selection, adaptive template memory, dynamic template number, target-model contamination, tracking drift, re-entry recovery.
- **Synonyms:** template validity, template confidence, corrupted template, contaminated memory, selective memory read, conditional template processing, state-conditioned compute.
- **Adjacent-field terms:** video-memory selection, key-value memory pruning, memory-bank consolidation, retrieval gating, dynamic ViT token pruning, video-segmentation memory, robust online model update.

No search was executed with these terms.

### G. Known collision boundary

- Multi-template tracking, TSSD, and attention-derived IFAS are FARTrack's own contributions.
- Generic physical token pruning collides with ordinary token-pruning work and with UTPTrack's search/static/dynamic compaction.
- Generic confidence-gated update, reliability-aware memory, template resampling, or search expansion is already represented by recent project candidates such as UncTrack.
- Distractor-aware memory is already central to DAM4SAM.
- FIFO bounding, template-feature caching, Python-loop removal, export, and reduced precision are ordinary engineering.
- The later novelty question must concern a materially distinct validity-conditioned relationship between template computation and failure/recovery, not merely “use fewer templates” or “filter memory.”

### H. Independent status

**GAP_READY**

The exact compute path, author-supported template-validity weakness and quantity trade-off, falsifiable interaction, rejection observations, and minimum hooks are concrete enough for later mechanism-level novelty search. This status does not assert novelty or decide HG6.

---

## 6. CX024 — DAM4SAM

### A. Candidate boundary

- **Exact anchor:** default `DAM4SAMTracker(tracker_name="sam21pp-L")`, `sam2/sam21pp_hiera_l.yaml`, and SAM 2.1 Hiera-L checkpoint, at `jovanavidenovic/DAM4SAM@9c954504b39ebca4c412f207be0787c26bfac85a`.
- **Core mechanism that must remain:** training-free alternative-mask introspection, fixed quality/size/cooldown gates, conditional promotion into distractor-aware conditioning memory (DRM), and coexistence with regularly sampled memory (RAM).
- **Permissible diagnostic variation:** gate bypasses, fixed inspection/admission modes, history-cap sweeps, state logging, timing, and controlled memory corruption for falsification.
- Replacing Hiera-L with EfficientTAM/EdgeTAM alone is host substitution, not a new DAM contribution. The publication reports lighter-host use [R29], but runnable lighter-host artifacts were not found at the pinned repository [R30].

### B. Code-visible compute observations

| Boundary | Observation |
|---|---|
| Host SAM 2.1 | **CODE FACT — inspected:** every new 1024-scale frame executes Hiera-L image encoding; memory attention, mask decoding, and memory encoding execute on propagated frames. |
| Host active memory | **CODE FACT — inspected:** `num_maskmem=7`; at most four conditioning/DRM frames enter attention and RAM fills remaining active slots with stride five. |
| Host retained history | **CODE FACT — inspected:** conditioning/non-conditioning output dictionaries remain frame-keyed without normal sequential eviction. Active attention is bounded, but retained compact history grows; default state offload is false. |
| DAM always-visible increment | **CODE FACT — inspected:** `return_all_masks=True` materializes all three predicted masks at original resolution before the wrapper receives them on non-initial frames. |
| DAM per-frame increment | **CODE FACT — inspected:** highest-IoU selection, pixel count, growing `object_sizes`, recent-size median, and cooldown bookkeeping execute per non-initial frame. |
| DAM conditional increment | **CODE FACT — inspected:** only after predicted IoU > 0.8, size ratio within `[0.8,1.2]`, nonempty mask, and >5-frame cooldown are two alternatives copied to CPU and processed by connected components and rectangle IoU. |
| DAM promotion | **CODE FACT — inspected:** alternative-union box IoU ≤ 0.7 promotes the current output to DRM and can trigger conditioning-output consolidation/memory encoding. |

Evidence: `dam4sam_tracker.py:178-266`; `sam2/sam2_video_predictor.py:328-352,609-639,675-790,975-990,1085-1105`; `sam2/modeling/sam2_base.py:531-708`; `sam2/sam21pp_hiera_l.yaml:88-125`.

The host cost and DAM-specific incremental cost are kept separate. Per-frame `torch.cuda.empty_cache()`, export partitioning, and host substitution are engineering sites, not a scientific robustness contribution.

### C. Code/source-supported robustness signal

**FACT — cited:** the authors motivate DAM using distractor weakness in memory-based trackers, including SAM 2, and distractor-aware memory is the method's principal contribution [R29/R30]. That motivating weakness cannot be reused as a residual weakness of final DAM4SAM.

The inspected sources contain no author-reported final-DAM failure attribute, frame-level failure evidence, or reproduced failure linked to the fixed admission gates. A non-perfect aggregate benchmark score alone is not a mechanism-specific residual weakness.

**ROBUSTNESS SIGNAL NOT ESTABLISHED**

The fact that fixed gates suppress inspection during low predicted IoU, abrupt scale change, an empty mask, or cooldown is implementation behavior; it is not evidence that final DAM4SAM fails under those conditions.

### D. Falsifiable coupling hypothesis

**HYPOTHESIS — provisional and untested:**

> Under frames without target–distractor ambiguity, materialization and inspection of alternative masks plus DRM-admission work may be unnecessary. Under a future, reproduced residual ambiguity condition, stronger or selectively enabled alternative-mask inspection and DRM admission—including frames rejected by the fixed pre-gates—may be required to preserve target identity.

**Reject the hypothesis if:**

- residual distractor failures cannot be reproduced;
- gate activation/admission has no relationship with distractor state or failure onset;
- released, DAM-disabled, forced-inspection, and oracle-timed modes show no condition-specific robustness difference;
- failure is unchanged because host segmentation, not DAM compute allocation, is limiting; or
- forced inspection only increases cost.

### E. Minimum falsification instrumentation

1. Log predicted IoU, size ratio, pixel count, cooldown, alternative-box IoUs, gate-pass reason, DRM admission, active DRM/RAM frame IDs, and retained dictionary lengths.
2. Separately time host image encoder, host memory attention/decoder/encoder, three-mask resize/materialization, CPU connected components/IoU, and DAM-triggered consolidation.
3. Add diagnostic-only released-gate, DAM-disabled, forced-inspection, and oracle/annotated-distractor inspection/admission modes.
4. Attribute overlap loss, VOT failure/reinitialization, or identity switches to annotated distractor frames on a bounded diagnostic subset.
5. Record device memory versus sequence length, separating base non-conditioning history from DRM admissions.
6. Hold the host fixed during the primary test; any Hiera-L versus lighter-host run is a separate host experiment.

### F. HG6 mechanism vocabulary

- **Precision terms:** `distractor-aware memory SAM2 tracking`, `alternative-mask disagreement memory admission`, `conditioning-frame promotion SAM2`, `DRM RAM visual object tracking`, `state-conditioned distractor introspection`.
- **Recall terms:** target–distractor ambiguity, identity-preserving memory update, memory contamination, reliable mask admission, conditional memory writing, multi-hypothesis mask selection.
- **Synonyms:** distractor introspection, ambiguity gating, conditioning-memory admission, mask-hypothesis disagreement, selective memory write, memory-promotion policy.
- **Adjacent-field terms:** video-object-segmentation memory eviction, cache admission/eviction, uncertainty-gated memory, selective inference, efficient SAM 2, EfficientTAM, EdgeTAM, adaptive video-memory computation.

No search was executed with these terms.

### G. Known collision boundary

- DAM4SAM already implements distractor-aware alternative-mask inspection, fixed confidence/size/cooldown gating, DRM promotion, RAM sampling, and bounded active memory attention.
- Generic distractor-aware or reliability-gated memory cannot be claimed as new.
- SAMURAI already supplies motion-aware SAM 2 memory selection; generic motion/confidence memory gating is collision-prone [R27/R28].
- EfficientTAM/EdgeTAM host substitution is already reported for the DAM family [R29].
- ONNX/TensorRT, FP16/INT8, removal of `empty_cache()`, CPU/GPU cleanup, ordinary history capping, and generic host compression remain engineering unless a validated robustness coupling establishes a distinct algorithmic question.

### H. Independent status

**GAP_INCOMPLETE**

The DAM-specific execution sites, host/incremental boundary, and falsification hooks are concrete. The required residual robustness signal for final DAM4SAM is not established, so a bounded distractor/failure-attribution experiment is required before HG6.

---

## 7. Completion and locked next state

All five G1 candidates have an exact anchor, core-mechanism boundary, concrete compute observation, robustness signal or explicit absence, falsifiable coupling question, rejection condition, minimum diagnostic instrumentation, HG6 vocabulary, collision boundary, and independent readiness state.

- **G1 Manager↔Codex reconciliation:** PENDING
- **G2:** NOT STARTED
- **HG6:** NOT STARTED
- **Soft scoring:** NOT STARTED
- **Primary shortlist:** NONE
- **Main baseline:** NONE
- **Proposed architecture:** NONE

No diagnostic experiment described here was executed in this task.
