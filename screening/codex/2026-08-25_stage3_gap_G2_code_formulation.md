# Stage 3A — G2 independent code-gap formulation

Date: **2026-08-25**

Lane: **Codex worker — independent code and engineering formulation**

Scope: **CX037 SSTrack-AAAI, CX038 MCITrack, CX043 SUTrack, CX044 AsymTrack, and CX058 HiT-DyHiT only**

## 1. Boundary and evidence discipline

This report formulates implementation-grounded, falsifiable gap questions. It does not execute a literature novelty search, decide HG6, score or rank a candidate, form a shortlist, select a baseline, design a proposed architecture, run training, reproduce a full benchmark, or start a diagnostic experiment.

The Manager G2 scientific-formulation artifact and the Manager G2 plan were not read, searched, grepped, or inspected before or during this independent formulation. Only the already-registered primary publications were consulted to verify the robustness statements predeclared in the task; that verification did not expand into novelty search.

The labels below have their literal meanings:

- **CODE FACT — inspected:** visible in the exact pinned official implementation or in a completed bounded project characterization of that implementation.
- **FACT — cited:** stated by a registered official publication or official repository.
- **HYPOTHESIS — untested:** a proposed relationship that must survive the specified rejection test.
- **ROBUSTNESS SIGNAL NOT ESTABLISHED:** no candidate-specific residual weakness acceptable under the Stage-3 protocol was found.

Paper/repository pairs are [R31/R32] for SSTrack-AAAI, [R33/R34] for MCITrack, [R37/R38] for SUTrack, [R39/R40] for AsymTrack, and [R49/R50] for HiT-DyHiT. Code paths below are relative to those exact pinned repositories. Implementation evidence is carried forward from the completed Batch-B/Batch-C/Batch-D audits and the bounded Stage-2B characterization. No experiment described below was executed in this task.

| Candidate | Independent readiness | Missing element, if any |
|---|---:|---|
| CX037 SSTrack-AAAI | **GAP_INCOMPLETE** | SSTrack-specific residual robustness signal linked to CE, representation, or template selection |
| CX038 MCITrack | **GAP_INCOMPLETE** | residual failure of final B224 linked to contextual state or fusion |
| CX043 SUTrack | **GAP_REJECTED** | only engineering cleanup/caching remains visible; no residual RGB coupling is established |
| CX044 AsymTrack | **GAP_READY** | none at Stage-3A formulation level |
| CX058 HiT-DyHiT | **GAP_READY** | none at Stage-3A formulation level; HiT-family signal still requires DyHiT transfer testing |

These states are gap-readiness states only. They are not HG6 decisions or scores.

---

## 2. CX037 — SSTrack-AAAI

### A. Candidate boundary

- **Exact anchor:** `experiments/sstrack/dropmae_256_150ep.yaml` / SSTrack-B256 at `GXNU-ZhongLab/SSTrack@5dcf04ccb04f10ca4d78035373c8b8684bb8c4f5`.
- **Core mechanism that must remain:** SSTrack's self-supervised decoupled spatial/temporal consistency identity; the deployed ViT-B tracker; candidate elimination at blocks 3/6/9; the one-token persistent tracking query; the multi-template controller; and the center head.
- **Permissible diagnostic variation:** control active-template identity/count, bypass one historical template slot, expose CE retained/removed identities and query state, or vary a fixed CE keep rate while holding checkpoint, crops, backbone, head, and evaluator fixed.
- Replacing the backbone/head, supervised retraining into a different tracker, deleting the persistent-query/CE/template mechanisms wholesale, or changing the tracking task would leave this candidate boundary.

The paper family also introduces instance-contrastive supervision, but the exact B256 YAML sets `TRAIN.CONTRASTIVE_LOSS: False`; it is therefore a paper-level family contribution/collision boundary, not a mandatory executed component of this anchor. The self-supervised training branches do not form an additional inference graph. The present question concerns the released deployed graph, not a generic self-supervised-versus-supervised score gap.

### B. Code-visible compute observations

| Observation | Evidence |
|---|---|
| **CODE FACT — inspected:** every frame patch-embeds the current 256×256 search and every selected raw 128×128 template; no encoded-template cache exists. | `lib/test/tracker/sstrack.py:91-130,169-198`; `lib/models/sstrack/vit_dropmae.py:105-123` |
| **CODE FACT — inspected:** mature execution can use four active templates: the initial template plus midpoint samples from three history segments, although `TEST.TEMPLATE_NUMBER` is three. | `lib/test/tracker/sstrack.py:169-198` |
| **CODE FACT — inspected:** all selected templates enter the transformer sequence. CE first pays the block attention, then applies fixed 0.7 physical elimination at blocks 3/6/9. Observed search lengths are `256→180→126→89`, followed by scatter restoration to the 16×16 search grid. | `lib/models/layers/attn_blocks.py:9-75,95-116`; `vit_dropmae.py:172-227`; Stage-2B characterization |
| **CODE FACT — inspected:** one self-predicted raw template crop is appended each frame without a confidence gate. The list is not truncated; the first 1,000 appended tensors remain on CUDA, and later selected entries are copied from CPU to the active device. | `lib/test/tracker/sstrack.py:91-130,169-198` |
| **CODE FACT — inspected:** the persistent query is one FP32 token `[1,1,768]`, is replaced every frame, and does not grow with sequence length. | `lib/models/sstrack/sstrack.py:225-252`; Stage-2B characterization |
| **CODE FACT — inspected:** bounded CPU model-only medians were 822.805 ms for one template and 1423.985 ms for four templates. This locates a comparative mode cost and is not a device-speed or redundancy claim. | Stage-2B bounded characterization |
| **CODE FACT — inspected:** a fixed four-template neural wrapper exported with CE `TopK`, gather, and scatter operators plus explicit query input/output, while the sequence-growing Python history/controller remained outside that graph. | Stage-2B bounded characterization |

The global-spatial, local-temporal, multi-view, and instance-contrastive supervision branches are training-only. The deployed cost sites are the raw-template embeddings, joint ViT attention, CE scoring/sort/gather/scatter, persistent query, and controller history.

### C. Code/source-supported robustness signal

**ROBUSTNESS SIGNAL NOT ESTABLISHED**

The unconditional admission of self-predicted templates is a concrete reliability lead, but code behavior alone does not show that contaminated history causes a reproducible SSTrack failure. The registered paper reports aggregate self-supervised tracking results and its training contribution [R31]; it does not establish a residual failure of final SSTrack tied to candidate elimination, representation quality, or template selection. The generic remaining performance gap between self-supervised and fully supervised tracking is excluded by the task and cannot serve as the robustness mechanism.

### D. Falsifiable coupling hypothesis

**HYPOTHESIS — provisional and untested:**

> Under stable frames where noninitial selected templates are source-frame-invalid or add no distinct valid appearance evidence, their raw embedding and transformer participation may be unnecessary or harmful. Under reappearance or substantial appearance-change frames where at least one historical template is valid and more representative than the initial template, selective use of that historical evidence may be required to preserve target-versus-distractor separation and recovery.

- **X:** stable frames with invalid, off-target, or appearance-redundant noninitial selections.
- **Y:** patch embedding and transformer participation of noninitial raw-history templates, including their interaction with CE and the persistent query.
- **Z:** reappearance or substantial appearance change where a selected historical template is independently verified as valid and more current than the initial template.
- **W:** current-frame IoU/center error, recovery duration, and target-versus-strongest-distractor response margin.

**Reject the hypothesis if:**

- source-frame validity/redundancy does not interact with a template slot's marginal contribution;
- initial-only, released-active-set, and leave-one-template-out effects are condition-independent;
- controlled corruption or duplication changes only latency, not condition-specific tracking outcome;
- CE/query behavior does not change with the presence of valid versus invalid historical evidence; or
- any apparent result reduces to generic feature caching or history capping.

Because Section C is absent, this hypothesis is not ready for HG6 even though it is falsifiable.

### E. Minimum falsification instrumentation

1. In `select_memory_frames`, record selected indices, source-frame age, source device, and source-crop validity against offline ground truth.
2. At history admission, retain frame ID, predicted/source box, score-map peak and target-versus-strongest-off-target margin.
3. Hook patch embedding and CE blocks 3/6/9 for call shape, synchronized duration, pre/post search-token counts, and retained/removed identities.
4. Record persistent-query input/output norm, direction change, and sensitivity to each selected historical slot.
5. Compare, with identical checkpoint and frames: released active set; initial template only; four duplicated initial templates; one-history-slot-at-a-time removal; and controlled corruption of one selected slot.
6. Report accuracy and latency separately on predeclared X/Z slices. Stop before HG6 if no condition-by-template interaction is reproduced.

These are minimum future diagnostics, not experiments executed here and not a proposed run-time policy.

### F. HG6 mechanism vocabulary

- **Precision terms:** `SSTrack multi-template re-encoding template validity compute`, `candidate elimination template validity tracking`, `tracking history contamination selective template computation`, `persistent tracking query template allocation`, `self-supervised tracker historical-template utility`.
- **Recall terms:** confidence-gated template update, template-memory quality selection, online template drift, dynamic template number, adaptive token pruning, conditional inference, query-conditioned memory access.
- **Synonyms:** active template set, history-slot utility, template contamination, template validity, conditional memory read, adaptive keep ratio, target-token survival.
- **Adjacent-field terms:** video-memory eviction, adaptive-computation transformer, conditional token routing, robust online model update, physical token compaction versus attention masking.

No query was executed with these terms.

### G. Known collision boundary

- SSTrack already contributes decoupled self-supervised spatial/temporal learning, instance contrastive supervision, CE, a persistent query, and multi-template selection. None can be claimed generically as new.
- Feature caching, FIFO/history bounding, replacing full sort with TopK, exporter repair, fixed keep-rate tuning, and quantization are ordinary engineering/compression.
- UTPTrack already constrains content-dependent physical token pruning questions.
- The reconciled FARTrack gap already frames template validity, physical template-compute removal, and robustness. Any SSTrack claim must later be distinguished from that formulation rather than restating it.
- A future claim must remain specific to measured SSTrack template/CE/query interaction, not merely “process fewer templates.”

### H. Independent gap state

**GAP_INCOMPLETE**

The compute path, provisional X/Y/Z/W relationship, rejection conditions, and instrumentation are concrete, but no qualifying SSTrack-specific residual robustness signal is established. A bounded history-validity/failure diagnostic must first show that template validity predicts both marginal compute utility and tracking outcome. The state is not `GAP_REJECTED` yet because the candidate-specific interaction is testable and is not limited to caching/export work.

---

## 3. CX038 — MCITrack

### A. Candidate boundary

- **Exact anchor:** `experiments/mcitrack/mcitrack_b224.yaml` / MCITrack-B224 at `kangben258/MCITrack@e667193eaec4c8a73d4bdd856a662aecdb844b43`.
- **Core mechanism that must remain:** Fast-iTPN-B; five-template formulation; four contextual Mamba stages with explicit carried hidden state; four Injectors; six Extractors; contextual fusion through the configured backbone slices; and the center head.
- **Permissible diagnostic variation:** zero/freeze one carried state, bypass one contextual insertion, control active-template evidence, or bypass inference checkpoint wrappers solely as an engineering control while holding weights, inputs, remaining modules, and evaluator fixed.
- Replacing the encoder, deleting contextual propagation wholesale, substituting another recurrent/transformer tracker, or treating the raw template manager alone as MCITrack would leave the candidate boundary.

The confidence-triggered reset and confidence-gated template admission are already baseline mechanisms and are not candidate weaknesses by themselves.

### B. Code-visible compute observations

| Observation | Evidence |
|---|---|
| **CODE FACT — inspected:** each frame encodes five raw 112×112 templates and one 224×224 search; no encoded-template cache exists. The combined visual sequence contains `5×49 + 196 = 441` tokens. | `lib/models/mcitrack/fastitpn.py:969-1023`; tracker path |
| **CODE FACT — inspected:** four Mamba contextual blocks, four MHA Injectors, six MHA Extractors, and four configured Fast-iTPN slices execute on every frame without confidence-conditioned layer skipping. | `lib/models/mcitrack/neck.py:89-167,222-278`; `lib/models/mcitrack/mcitrack.py:58-68` |
| **CODE FACT — inspected:** each carried state is FP32 `[1,196,1024,16]` and contains 12,845,056 bytes. Four states total 51,380,224 bytes, or 49.0 MiB. They are fixed-size, replaced every frame, and reset to `None` after low confidence. | Stage-2B bounded characterization; `lib/test/tracker/mcitrack.py:100-164` |
| **CODE FACT — inspected:** the raw template bank is confidence-gated and bounded at dataset-specific capacities of 200–500 crops; five active raw templates are periodically refreshed and all five are re-encoded every frame. | `lib/test/tracker/mcitrack.py:100-164` |
| **CODE FACT — inspected:** `GRAD_CKPT=True` causes checkpoint-wrapper calls even under inference because the wrappers are not guarded by `self.training`. Disabling them produced identical tested frame-0 boxes, but noisy CPU samples did not establish a stable latency effect. | Stage-2B bounded characterization |
| **CODE FACT — inspected:** a fixed B224 ONNX wrapper carried all four hidden states explicitly and achieved CPU-runtime parity, while Python confidence/reset/template-bank control remained outside the graph. | Stage-2B bounded characterization |

The ordinary PyTorch Mamba implementation uses Linear, grouped Conv1d, exponentials, elementwise operations, and matrix multiplication; no mandatory custom selective-scan CUDA extension was invoked in the active path. That operator fact does not make the four states or contextual interactions lightweight on a target device.

### C. Code/source-supported robustness signal

**ROBUSTNESS SIGNAL NOT ESTABLISHED**

The low-confidence state reset and confidence-gated template admission are safeguards implemented by final MCITrack, not evidence that final B224 still suffers state contamination. The registered paper's final limitation concerns slow video-level training and the additional computation of video clips [R33, p. 4200]. Its ablations show that six CIF blocks or a six-frame training clip can reduce aggregate performance relative to the chosen four-block/five-frame configuration [R33, pp. 4199-4200, Tables 4-5]. Those ablations do not establish a residual state-related failure of the final tracker.

No author-reported residual attribute, reproduced failure slice, or final-model diagnostic currently shows that always-on contextual fusion is harmful on stable frames or insufficient after disruption.

### D. Falsifiable coupling hypothesis

**HYPOTHESIS — provisional and untested:**

> Under ground-truth-defined stable frames with little appearance/motion change, redundant active templates, and no recent failure, some carried-state/contextual-fusion work may be unnecessary. Under a separately reproduced disruption condition where earlier valid context remains useful, selective carried state and particular contextual insertions may be required to preserve localization and recovery.

- **X:** stable target appearance/motion with no recent occlusion, re-entry, or distractor ambiguity.
- **Y:** four carried states plus the four always-on Mamba→Injector→Fast-iTPN-slice→Extractor contextual insertions.
- **Z:** a future, independently established failure condition such as occlusion/reappearance, abrupt appearance/motion change, or distractor ambiguity where earlier valid context exists.
- **W:** current/next-frame IoU and center error, recovery duration, and target-versus-distractor response margin.

**Reject the hypothesis if:**

- per-state or per-insertion ablation effects do not interact with X versus Z;
- hidden-state change, norm, reset timing, or contextual residuals do not predict marginal contribution;
- zeroing previous state changes all conditions uniformly;
- the released reset already removes the suspected harmful state with no residual failure; or
- the only remaining savings are FP16 conversion, template caching, wrapper removal, bank bounding, or export plumbing.

Because condition Z and evidence that Y affects the defined outcome W in a condition-specific way are not currently established, this coupling is not ready for HG6.

### E. Minimum falsification instrumentation

1. Record confidence, state-reset events, template-bank admissions, active-template refresh indices/ages, and source-crop validity at the tracker boundary.
2. Hook Fast-iTPN token preparation to separate five-template and search costs.
3. At every contextual stage, record input/output residual norm, synchronized duration, hidden-state norm/change/dtype, and output sensitivity.
4. Separately expose each Injector/Extractor and decoder boundary; retain summary statistics rather than copying the four large states unnecessarily.
5. Compare identical recorded inputs under: released full path; previous state set to zero while retaining current Mamba work; one-layer state zeroing; one contextual insertion bypass at a time; and five duplicated initial templates versus released active templates.
6. Treat checkpoint-wrapper on/off only as an engineering control. Evaluate the scientific controls on predeclared X/Z slices, including next-frame effects after reset.

No diagnostic was run here.

### F. HG6 mechanism vocabulary

- **Precision terms:** `MCITrack adaptive contextual fusion`, `visual tracking state-conditioned Mamba computation`, `conditional Mamba layer execution tracking`, `selective hidden-state propagation Injector Extractor`, `confidence-conditioned contextual computation tracker`.
- **Recall terms:** dynamic-depth state-space model, SSM layer skipping, event-triggered recurrent state update, uncertainty-gated temporal memory, conditional cross-attention video memory, adaptive temporal-context inference.
- **Synonyms:** state utility, state contamination, contextual residual selection, selective state update, hidden-state reset reliability, conditional recurrence, state sparsification.
- **Adjacent-field terms:** recurrent adaptive computation, video state-space modeling, mixture of depths, dynamic neural networks, temporal memory routing, conditional video inference.

No query was executed with these terms.

### G. Known collision boundary

- MCITrack already contributes contextual hidden-state propagation through Mamba plus Injector/Extractor fusion. Generic “add temporal context,” “use Mamba,” or “fuse multi-frame information” claims collide with the baseline.
- It already implements confidence-triggered hidden-state reset, confidence-gated template admission, a bounded raw bank, and periodic five-template refresh. These cannot be relabeled as new.
- MambaLCT is already registered in the project as a direct long-term-context/SSM mechanism adversary; no HG6 decision is made here.
- Removing inference checkpoint wrappers, caching templates, reducing state precision, bounding the already bounded bank, fixed layer pruning, and explicit-state export are ordinary engineering unless a condition-specific robustness relationship is first demonstrated.

### H. Independent gap state

**GAP_INCOMPLETE**

The always-on contextual path, outcome W, and a falsifiable conditional-use question are concrete, but no qualifying residual robustness signal establishes condition Z or a condition-specific Y→W effect. Candidate-specific failure/state-contribution diagnostics are required before HG6. It is not `GAP_REJECTED` yet because per-state/per-insertion conditional contribution is a candidate-specific testable relationship, not merely exporter cleanup.

---

## 4. CX043 — SUTrack

### A. Candidate boundary

- **Exact anchor:** RGB `experiments/sutrack/sutrack_t224.yaml` / SUTrack-T224 at `chenxin-dlut/SUTrack@d65052d1ba3fcf55010e1fb3665ee6616c139a2c`.
- **Accuracy reference only:** `experiments/sutrack/sutrack_b224.yaml` / SUTrack-B224.
- **Core mechanism that must remain:** unified six-channel visual representation, unified training-family identity, Fast-iTPN Tiny at the anchor, joint template/search/text-token processing, token-role embeddings, and center decoder.
- **Permissible diagnostic variation:** isolate or bypass an inference-resident component, verify cached-versus-recomputed tensors, and compare released T224/B224 behavior while keeping each checkpoint/config intact.
- RGB-only retraining that removes the unified representation, replacement of Fast-iTPN/head, or addition of a new memory/re-detection system would create a different scientific unit.

B224 is not a clean single-axis control: relative to T224, it changes encoder width/depth and changes one static template into a bounded fixed-plus-dynamic pair.

### B. Code-visible compute observations

| Observation | Evidence |
|---|---|
| **CODE FACT — inspected:** every T224 RGB crop is duplicated along channels to construct a six-channel tensor. The pretrained three-channel patch kernel is copied into both halves with half scaling. | `lib/test/tracker/sutrack.py:80-175`; `lib/models/sutrack/fastitpn.py:1097-1111` |
| **CODE FACT — inspected:** the unchanged raw static template and current search are re-patch-embedded and processed every frame; T224 then carries a fixed 247-token joint sequence: one class token, 196 search tokens, 49 template tokens, and one text token. | same paths; Batch-C audit |
| **CODE FACT — inspected:** a zero-text CLIP feature is generated once and its projected token is reused in every frame's joint sequence; the complete CLIP object remains resident. | `lib/models/sutrack/sutrack.py`; tracker initialization path |
| **CODE FACT — inspected:** the task-recognition head is present for training but is not called by the released RGB inference path. | `lib/models/sutrack/sutrack.py`; Batch-C audit |
| **CODE FACT — inspected:** token-role embeddings execute every frame and identify search/template foreground/background roles; they are not an inference task/modality router. | `lib/models/sutrack/fastitpn.py:963-1049` |
| **CODE FACT — inspected:** T224 has one static template and bounded state. B224 carries 296 joint tokens, re-encodes two raw templates every frame, and already updates its second template every 25 frames when confidence exceeds 0.70. | `lib/test/tracker/sutrack.py:80-175`; released YAMLs |
| **CODE FACT — inspected:** no inference-time task/modality routing, conditional block skipping, sparse expert path, or growing temporal memory exists in T224. | Batch-C audit |

The code-visible opportunities are duplicate-channel projection, zero-text/token handling, resident unused inference objects, repeated static-template encoding, and export/profile cleanup. None is a robustness result.

### C. Code/source-supported robustness signal

**ROBUSTNESS SIGNAL NOT ESTABLISHED**

Neither the registered publication nor the pinned RGB implementation establishes a T224-specific residual challenge attribute or reproducible RGB failure tied to the unified six-channel representation, zero-text token, or token-role mechanism [R37/R38]. The paper's multi-task/unified-training contribution and aggregate RGB results cannot be inverted into a residual RGB weakness. Six-channel duplication, unused residents, and static-template recomputation are compute observations only.

### D. Falsifiable coupling assessment

No admissible efficiency–robustness coupling can currently be completed:

- **X:** RGB frames after initialization, where T224's raw static template remains unchanged.
- **Y:** repeated static-template embedding/early processing, duplicated-channel projection, zero-text token handling, or resident unused inference components.
- **Z:** **NOT ESTABLISHED** — no source-supported residual RGB condition linked to the unified representation/token mechanism.
- **W:** **NOT ESTABLISHED** — no corresponding condition-specific robustness outcome.

Cached-versus-recomputed static-template parity is an engineering caching test. Removing unused residents, eliminating a zero token, specializing the patch input to RGB, or simplifying channels remains engineering/model specialization unless a candidate-specific robustness interaction is first demonstrated.

An appearance-change/template-update formulation is not available as a new SUTrack-family gap: T224 supplies no update path, while B224 already implements a bounded confidence/interval dynamic-template replacement.

**Reject any attempt to reopen this coupling if:**

- caching or resident cleanup changes only latency/residency and not challenge-conditioned accuracy;
- T224/B224 differences cannot be separated from simultaneous backbone, template-count, and training changes;
- no T224-specific RGB failure and B224 recovery interaction is reproduced; or
- the proposed work is ordinary compression, exporter repair, or an already existing SUTrack-family update mechanism.

### E. Minimum reopening instrumentation

No diagnostic is authorized in this task. The minimum evidence required to reopen the scientific question would be:

1. Time patch projection, template early blocks, joint blocks, and center head separately.
2. Compare cached versus recomputed static-template tensors and final boxes within predeclared numerical tolerances.
3. Log paired T224/B224 per-frame IoU, challenge labels, and disagreement while preserving each released checkpoint/config.
4. For B224, log confidence, update frame, selected crop, and whether an update repairs a T224-only failure.
5. Explicitly separate a latency-only result from a condition-specific robustness interaction.

If these controls produce only parity and latency savings, the `GAP_REJECTED` state remains.

### F. HG6 mechanism vocabulary

- **Precision terms:** `SUTrack unified representation RGB duplication`, `six-channel patch projection RGB tracking`, `zero-text token unified tracker`, `soft token type embedding RGB tracking`, `SUTrack static-template feature reuse`.
- **Recall terms:** encoded-template reuse, template-branch memoization, RGB-only specialization, multimodal negative transfer, unified tracking representation, task-token removal, token-type embedding.
- **Synonyms:** channel duplication, dummy modality, null language token, modality-neutral token, template caching, resident-module removal.
- **Adjacent-field terms:** multimodal unified model, modality dropout, missing-modality inference, conditional modality routing, unified token pruning, representation specialization.

No query was executed with these terms.

### G. Known collision boundary

- SUTrack already contributes unified multi-task/multimodal training, six-channel representation, task-recognition supervision, soft token-role embeddings, and the common tracking head.
- SUTrack B/L already includes bounded fixed-plus-dynamic confidence/interval template update.
- UTPTrack-S is SUTrack-derived and already occupies unified physical token-compaction territory in this project.
- Generic template caching, unused-module removal, null-token removal, RGB-only specialization, exporter repair, quantization, or pruning is engineering/compression and cannot support a Stage-3 gap by itself.

### H. Independent gap state

**GAP_REJECTED**

The only currently evidenced T224 opportunities are engineering cleanup, specialization, caching, export, or compression. The obvious robustness-related template-update mechanism already exists within the SUTrack family, and no residual RGB signal supports a distinct compute–robustness coupling. Inventing condition Z/W would violate the evidence policy.

---

## 5. CX044 — AsymTrack

### A. Candidate boundary

- **Exact anchor:** `experiments/AsymTrack/tiny.yaml` / AsymTrack-T at `jiawen-zhu/AsymTrack@a7b05e0c0d6116ccd7fa72270aa19053b7777204`.
- **Confounded capacity references:** AsymTrack-S (`small.yaml`) and AsymTrack-B (`base.yaml`).
- **Core mechanism that must remain:** asymmetric initialization-only template processing, cached ETM kernels and template tokens, two steady-state ETMs, relation attention, re-parameterized OPE, linear neck, and CORNER localization head.
- **Permissible diagnostic variation:** aligned T/S/B inference, forced fixed family operating points, tensor hooks, and attribute-stratified oracle analysis while retaining each released checkpoint and graph.
- Adding online template memory, a motion/recovery subsystem, an external host tracker, or a new early-exit/router architecture would change the candidate rather than diagnose it.

The released family exposes two useful but confounded axes:

- T→S keeps 128/256 template/search geometry but increases the final-stage depth from one to three blocks.
- S→B keeps depth, widths, and approximately 3.549M fused parameters fixed while increasing template/search to 192/384, relation tokens from 320 to 720, and the head map from 8×8 to 12×12.

Released T/S/B checkpoints also differ in training data and optimization settings. Their results are variant associations unless matched controls later isolate depth or resolution.

### B. Code-visible compute observations

| Observation | Evidence |
|---|---|
| **CODE FACT — inspected:** template neural processing occurs once on the first tracking call. Two ETM kernels and relation-attention template tokens are then reused with bounded size. | `lib/models/AsymTrack/EfficientMod.py:621-622,702-726`; `tem_kernel.py:98-104` |
| **CODE FACT — inspected:** every steady-state frame executes the complete fixed search path, two ETMs, one relation-attention block, linear neck, and two-tower CORNER head. | `EfficientMod.py:155-185,398-476`; `lib/models/AsymTrack/asymtrack.py:52-93` |
| **CODE FACT — inspected:** T has stage depths 2/2/1, approximately 3.239M fused parameters, a 256 search, 320 relation tokens, and an 8×8 head map. | released Tiny config; Batch-C audit |
| **CODE FACT — inspected:** S has depths 2/2/3, approximately 3.549M fused parameters, the same 256 search/320 relation tokens, and an 8×8 head map. | released Small config; Batch-C audit |
| **CODE FACT — inspected:** B has the same depth/width/parameter count as S but a 384 search, 720 relation tokens, and a 12×12 head map. | released Base config; Batch-C audit |
| **CODE FACT — inspected:** there is no per-frame depth, resolution, ETM, relation-attention, confidence, or route decision. The initial template/caches remain fixed. | `lib/test/tracker/AsymTrack.py`; `EfficientMod.py` |
| **CODE FACT — inspected:** the factor-4 search crop is centered on the previous predicted box; no motion predictor, enlarged recovery search, template update, history, or re-detection path exists. | `lib/test/tracker/AsymTrack.py:52-69,94-108` |

OPE's training branches are fused after the training-form checkpoint is loaded, so the released inference graph already contains the re-parameterized single-convolution form. Template caching and OPE fusion therefore cannot be proposed as missing mechanisms.

### C. Code/source-supported robustness signal

**FACT — cited:** the registered official AAAI paper's “Gap Analysis with Precision-Oriented Trackers” reports a significant AsymTrack-family gap against precision-oriented trackers across 14 LaSOT attributes. The three largest gaps are **low resolution, viewpoint change, and fast motion**, which the paper associates with challenged representation capability [R39, p. 6].

Boundary of that fact:

- it is a family-level relative gap, not proof that T alone is weak;
- it does not establish that S/B repair the gap;
- it does not prove that the 8×8 map, fixed initial template, previous-box crop, ETM, or any other code site causes the measured gap; and
- it is not a Jetson or deployment result.

The code-visible 8×8 versus 12×12 map, fixed template, and previous-box-centered crop are therefore diagnostic sites only.

### D. Falsifiable coupling hypothesis

**HYPOTHESIS — untested:**

> Under frames from ordinary sequences, or from attribute-labeled sequences where T/S/B already agree, the higher fixed representation cost of S/B may be unnecessary. Within sequences labeled low resolution, viewpoint change, or fast motion, frames where T fails and a stronger released family point succeeds may require additional depth or spatial processing to improve localization outcome.

- **X:** frames from sequences without the LR/VC/FM labels, or frames within LR/VC/FM-labeled sequences where paired T/S/B localization agrees.
- **Y:** S's two additional final-stage blocks and B's higher-resolution token/grid processing.
- **Z:** frames within predeclared LR/VC/FM-labeled sequences where T fails but paired S or B succeeds. R39 supplies sequence-level attribute labels; any stronger frame-level challenge annotation requires a separately predeclared annotation rule.
- **W:** IoU/center precision and avoidance/recovery of the same localization failures.

This is strictly an offline **oracle-capacity question**. It does not posit a router, early exit, adaptive resolution method, or proposed architecture.

**Reject the hypothesis if:**

- S/B do not preferentially repair T errors within LR/VC/FM-labeled sequence slices;
- their gains are uniform rather than condition/failure-specific;
- one fixed variant dominates the oracle accuracy–cost frontier;
- oracle-selected cost versus accuracy offers no improvement over fixed T/S/B at the same evaluated budget;
- the apparent interaction disappears under matched training/data/optimization controls; or
- extra capacity raises aggregate accuracy without repairing the frames that instantiate the registered relative gap.

### E. Minimum falsification instrumentation

1. Run exact T/S/B checkpoints through one evaluator and retain aligned sequence/frame IDs plus the 14 LaSOT sequence-level attribute labels. Predeclare a separate annotation rule before making any frame-level challenge claim.
2. Record per-frame IoU, center error, normalized precision, T-failure/S-or-B-recovery indicators, and variant disagreement.
3. Hook final-stage block inputs/outputs, ETM outputs, relation-attention token counts, and 8×8/12×12 head maps.
4. Measure synchronized per-mode neural latency and full tracker latency separately.
5. Compute offline oracle benefit and oracle-selected cost; do not count the sum of all three diagnostic forwards as the hypothetical selected-mode cost.
6. Use matched-training controls before attributing T→S effects to depth or S→B effects to resolution. Until then, label findings as released-variant associations.

These diagnostics are not executed here and do not define a final adaptive mechanism.

### F. HG6 mechanism vocabulary

- **Precision terms:** `AsymTrack attribute-conditioned capacity`, `AsymTrack low-resolution representation gap`, `AsymTrack viewpoint-change capacity utility`, `AsymTrack fast-motion oracle routing`, `relation-attention token budget AsymTrack`.
- **Recall terms:** dynamic-depth visual tracking, adaptive-resolution tracking, multi-resolution inference, difficulty-aware computation, conditional capacity, hard-frame routing, budgeted visual tracking.
- **Synonyms:** stage-3 block gating, selective deepening, oracle route benefit, capacity-on-demand, coarse-to-fine tracking, anytime tracking, conditional resolution.
- **Adjacent-field terms:** dynamic neural network, adaptive computation time, early-exit vision transformer, mixture of depths, multi-exit localization, budgeted inference.

No query was executed with these terms.

### G. Known collision boundary

- AsymTrack already contributes the asymmetric template-once/search-online framework, ETM, cached modulation/tokens, OPE, OPE re-parameterization, and its Tiny/Small/Base family.
- Generic early exit, easy/hard routing, hard-frame deeper execution, or dynamic route selection collides directly with HiT-DyHiT.
- ARTrack-AC was supplied in the task as a collision lead but is not registered in the current source manifest; it is retained only as a future HG6 lead, not as a source-backed collision finding. Generic dynamic-depth/resolution trackers also require later mechanism review; no novelty decision is made here.
- Fixed template caches, 8×8 maps, or previous-box crops cannot be claimed as causes without isolation.
- Export repair, operator substitution, pruning, fixed model selection, and quantization are ordinary engineering.
- The only retained candidate-specific question is measured attribute-conditioned marginal utility of AsymTrack's released depth/resolution axes.

### H. Independent gap state

**GAP_READY**

The fixed compute axes, official LR/VC/FM residual signal, oracle-only X/Y/Z/W question, matched-control requirement, minimum hooks, and explicit rejection observations are concrete enough for later mechanism-level novelty search. This state does not show that S/B repair the gap, establish causality, or decide HG6.

---

## 6. CX058 — HiT-DyHiT

### A. Candidate boundary

- **Exact anchor:** standalone DyHiT `experiments/DyHiT/stage2.yaml`, backbone `DyHiT_384_stage2_256tokens`, at `kangben258/HiT@ca806400def2b9ab42628f7a7e941b188d89606f`.
- **Released operating-point caveat:** the pinned Stage-2 YAML sets `THRESHOLD=-9999`, explicitly selecting Route1 only. It anchors the released graph/checkpoint lane, not a demonstrated mixed-route default.
- **Forced-path paper controls:** R49 defines `DyHiT_0` as Route1 only and `DyHiT_1` as Route2/full pipeline only; `DyHiT_0.6` and `DyHiT_0.7` are intermediate route mixtures. Their reported speeds are paper-specific controls and are not transferred to Nano or another device.
- **Fixed-compute controls:** static HiT-Tiny/Small/Base use the same 128-template/256-search geometry. Their pinned tracker/profiler mismatches require reconciliation before executable claims.
- **Core mechanism that must remain:** the shared first LeViT stage, existing feature-driven router boundary, Route1 small bottleneck/CORNER head, and Route2 later hierarchical stages/Bridge/large CORNER head.
- Route forcing and read-only instrumentation stay within the candidate. Replacing a branch with an unrelated host, adding external memory/detection, or using OSTrack as Route2 changes the scientific unit.

DyOSTrack is retained only as a separate wrapper reference. It keeps a lightweight model and OSTrack resident and invokes the full host after a hard decision without feature reuse. Its runtime graph is not merged into standalone DyHiT.

### B. Code-visible compute observations

| Observation | Evidence |
|---|---|
| **CODE FACT — inspected:** every frame re-encodes the current 256×256 search and stored 128×128 raw template. Patch embedding yields 256 search plus 64 template tokens. | `lib/test/tracker/DyHiT.py:43-82`; `lib/models/HiT/levit_dyhit_stage2.py:1100-1113` |
| **CODE FACT — inspected:** the common first LeViT stage always processes `[B,320,384]`. With configured interval one, the router then executes every frame on the 256 first-stage search tokens. | `levit_dyhit_stage2.py:1066-1068,1083-1118`; `lib/config/DyHiT/config.py:107` |
| **CODE FACT — inspected:** the router is `384→96→96→1`, applies sigmoid per token, and averages token scores greater than `SCORE_T=0.6`; empty selection becomes 0.01. | `levit_dyhit_stage2.py:149-161,1113-1122` |
| **CODE FACT — inspected:** the first tracked frame uses Route1. Later, `score > threshold` selects Route1; otherwise Route2. The Python `.item()`/threshold branch controls which continuation executes. | `levit_dyhit_stage2.py:1123-1143`; `lib/test/tracker/DyHiT.py:68-82` |
| **CODE FACT — inspected:** Route1 reuses the shared tensor, adds its global/mean token, runs a `384→256` bottleneck and its own 16×16 two-tower CORNER head. | `lib/models/HiT/hit.py:128-165`; `levit_dyhit_stage2.py:1123-1135` |
| **CODE FACT — inspected:** Route2 reuses the same shared tensor, continues through `[B,80,512]` and `[B,20,768]`, then runs multiscale Bridge fusion and its distinct large CORNER head. It does not recompute the shared prefix or run the Route1 head. | `levit_dyhit_stage2.py:1136-1143`; `lib/models/HiT/hit.py:166-172` |
| **CODE FACT — inspected:** state is bounded to the initial raw template, current box, frame counter, and first-frame route score. The released standalone tracker has no dynamic-template update or temporal feature bank. | `lib/test/tracker/DyHiT.py:38-82` |

The measurable allocation site is therefore the **incremental Route2 continuation after the already-paid shared prefix and router**. It is not labeled redundant before testing. The released Route1 profiler bypasses or mixes route boundaries and lacks CUDA synchronization, so it cannot establish that incremental cost.

### C. Code/source-supported robustness signal

**FACT — cited:** R49's official IJCV paper reports that HiT tends to degrade in the presence of distractions and cluttered backgrounds and explicitly identifies distractors/background clutter as a limitation [R49, p. 20].

Boundary of that fact:

- the wording explicitly names **HiT**, not final standalone DyHiT;
- it is a candidate-family diagnostic signal, not proof that DyHiT retains the same failure;
- DyHiT is built over HiT components, making paired route testing concrete, but transfer must be established empirically;
- absence of an explicit distractor memory/classifier in code does not prove a failure; and
- aggregate DyHiT/HiT accuracy differences do not prove route misallocation.

R49 Table 13 also supplies forced-route semantics: `DyHiT_0` is Route1 only and `DyHiT_1` is Route2/full pipeline only. This supports the control design but does not by itself show that the router is wrong on any frame.

### D. Falsifiable coupling hypothesis

**HYPOTHESIS — untested:**

> Under matched frames without target-like distractors or strong background clutter, the incremental Route2 continuation may provide negligible marginal benefit. Under predeclared distractor/clutter frames, selective use of Route2 may be required to preserve target–distractor separation and tracking outcome.

- **X:** matched non-distractor/non-clutter frames.
- **Y:** incremental Route2 work after the shared first stage/router: later LeViT stages, Bridge, and large head.
- **Z:** predeclared distractor or cluttered-background frames corresponding to the R49 family limitation.
- **W:** box IoU/center error, failure avoidance/recovery, and a predeclared target-versus-distractor separation measure. For frames with annotated distractor boxes/regions, define `M = IoU(predicted_box, target_box) - max_j IoU(predicted_box, distractor_box_j)`. If no distractor region is annotated, do not invent a margin; retain target IoU/center error only.

For the same pre-frame tracker state `s_t`, define the counterfactual route benefit:

`B_t = loss(Route1 | s_t) - loss(Route2 | s_t)`.

Positive `B_t` means Route2 is the better counterfactual route. The prediction is that `B_t` and Route2's improvement in the predeclared separation measure are materially larger under Z than X.

Define diagnostic route errors only after paired outcomes are available and report policies separately:

- **false-shallow:** the evaluated policy selects Route1 while Route2 has a predeclared material positive `B_t`; this is the only route-error type possible under the pinned `THRESHOLD=-9999` all-Route1 configuration.
- **false-deep:** a predeclared mixed-threshold control selects Route2 while Route1 remains within the outcome tolerance; this is not applicable to the pinned all-Route1 configuration.

**Reject the hypothesis if:**

- the HiT distractor/clutter signal does not transfer to standalone DyHiT;
- Route2 oracle benefit does not interact with distractor/clutter condition;
- Route2 fails to improve separation or localization on Z;
- Route2 benefits all conditions uniformly, leaving only a fixed capacity trade-off;
- an oracle selector gives negligible benefit over fixed/released routing at a matched Route2 budget; or
- a predeclared mixed-threshold policy from the R49 controls already captures essentially all condition-specific oracle benefit.

### E. Minimum falsification instrumentation

1. Snapshot one canonical pre-frame state and run forced Route1 and Route2 without committing divergent state.
2. Hook the shared `[320,384]` tensor, 256-token router sigmoid map, selected-token count, aggregate route score, threshold, and chosen route.
3. Hook Route2's `[80,512]` and `[20,768]` tensors and both branches' pre-softmax top-left/bottom-right corner maps. If a corner-map margin is additionally reported, predeclare target/distractor corner neighborhoods and define the exact TL/BR pairing rule.
4. Record synchronized latency separately for preprocessing, common prefix, router, Route1 increment, Route2 increment, and full tracker boundary.
5. Record predicted box, IoU, center error/failure, annotated distractor boxes/regions, and the exact box-overlap separation measure defined in Section D. Do not infer a “strongest distractor” from an unannotated corner peak.
6. Compare R49's forced endpoints, intermediate route controls, and fixed HiT family controls on aligned frames.
7. Stratify predeclared distractor/clutter versus matched non-distractor frames; report first-frame forced Route1 separately.
8. Compute oracle upper bound and policy regret separately for the pinned all-Route1 configuration and each predeclared R49 mixed-threshold control. Report false-shallow/false-deep counts only where the policy can emit the corresponding route.

These are diagnostics only. They do not define a replacement router or proposed architecture.

### F. HG6 mechanism vocabulary

- **Precision terms:** `single object tracking distractor-aware route utility`, `background clutter conditional depth tracker`, `target-distractor margin adaptive computation tracking`, `DyHiT Route1 Route2 oracle routing`, `counterfactual branch utility visual tracking`.
- **Recall terms:** dynamic inference, adaptive computation, conditional computation, dynamic depth, layer skipping, early exit, branch routing, selective deepening, learned halting, anytime prediction.
- **Synonyms:** scene-complexity routing, route regret, false-shallow routing, false-deep routing, route oracle, conditional continuation, hard-frame compute.
- **Robustness terms:** target ambiguity, similar objects, background clutter, distractor suppression, multi-peak response, response-map margin, confidence, uncertainty, entropy.
- **Adjacent-field terms:** content-adaptive vision transformer, conditional-depth object detection, budgeted video inference, difficulty-aware classification, counterfactual expert routing, mixture of depths.

No query was executed with these terms.

### G. Known collision boundary

- DyHiT already contributes shared-prefix two-route processing, Route1/Route2 conditional depth, a feature-driven router, adjustable threshold, and easy/hard speed–accuracy operating points.
- R49 already reports forced Route1/Route2 endpoints and intermediate route mixtures.
- Basic early exit, threshold routing, scene-difficulty routing, generic stronger-path invocation, or learned IoU-related router supervision cannot be claimed as new.
- DyOSTrack already implements lightweight-first routing to a stronger OSTrack host. A generic lightweight-to-heavy cascade is outside the retained question.
- Static HiT Tiny/Small/Base already provide fixed compute levels.
- Ordinary threshold tuning/calibration, template caching, pruning, quantization, distillation, exporter/profiler repair, and device porting are engineering.
- The only candidate-specific question retained is whether measured Route2 marginal utility is coupled to the author-identified distractor/clutter condition and is misallocated by a predeclared evaluated policy. The pinned all-Route1 configuration and R49 mixed-threshold controls must be reported separately.

### H. Independent gap state

**GAP_READY**

The shared-prefix/Route2 compute boundary is exact, R49 supplies a family-specific distractor/clutter signal, and paired forced-route oracle analysis gives a falsifiable coupling, minimum hooks, and explicit rejection observations. This readiness is narrow: it does not establish that final DyHiT fails under clutter, that Route2 fixes the limitation, that any evaluated route policy is deficient, or that any mechanism is novel. Failure of either signal transfer or condition-specific Route2 benefit rejects the formulation.

---

## 7. Completion and locked next state

All five G2 candidates have an exact anchor, scientific-core boundary, concrete compute observations, a residual robustness signal or its explicit absence, a falsifiable coupling assessment, rejection observations, minimum diagnostic instrumentation, HG6 vocabulary, a collision boundary, and an independent gap-readiness state.

- **Stage 3A G2 code formulation:** COMPLETE
- **G2 Manager↔Codex reconciliation:** PENDING
- **HG6:** NOT STARTED
- **Soft scoring:** NOT STARTED
- **Primary shortlist:** NONE
- **Main baseline:** NONE
- **Proposed architecture:** NONE

No diagnostic experiment described in this report was executed.
