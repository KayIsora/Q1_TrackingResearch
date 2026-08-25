# Stage 3B — HG6 Novelty Batch N1 Manager audit

**Date:** 2026-08-25  
**Lane:** Manager — primary-source scientific novelty audit  
**Batch:** N1 — CX007 SpikeTrack, CX013 FARTrack  
**Status:** MANAGER AUDIT COMPLETE; independent Codex N1 audit and source registration/reconciliation are still required.  
**Governing plan:** `screening/manager/2026-08-25_stage3B_hg6_execution_plan.md`.

## Boundary

This document independently audits whether the two reconciled G1 questions remain materially distinct after mechanism-level prior-art search. It does not assign S1–S7, rank candidates, form a shortlist, select a baseline, or design a proposed architecture.

The decisions below are **Manager-lane provisional HG6 decisions**. They are not final project decisions until Codex completes an independent audit, serious sources are canonically registered, and Manager↔Codex reconciliation is closed.

Search covered peer-reviewed tracking work from 2023–2026, arXiv-only novelty references, older generic template-update concepts where relevant, and adjacent SNN/dynamic-inference literature. Search-result snippets were used only as leads; collision judgments rely on official proceedings, official publisher pages, or the original arXiv record when no reviewed version was identified.

---

# 1. Search log

The following exact query families were executed on 2026-08-25. Named-title queries were used only after broad mechanism discovery to verify primary sources.

| # | Exact query | Search family | Main disposition |
|---:|---|---|---|
| 1 | `spiking visual tracking adaptive computation memory retrieval distractor` | SpikeTrack precision | No direct MRM+distractor allocation method found |
| 2 | `spiking neural network dynamic timestep input conditioned early exit` | SNN recall | SEENN, Adaptive Calibration and related timestep methods found |
| 3 | `spiking transformer token sparsification dynamic inference` | SNN recall | STATA and adjacent sparsification work found |
| 4 | `spiking temporal representation discriminability dynamic suppression` | SNN robustness | TRE found |
| 5 | `visual tracking adaptive capacity easy hard frame dynamic inference` | Tracking recall | ARTrack-AC and HiT-DyHiT found |
| 6 | `SpikeTrack adaptive memory retrieval MRM distractor tracking` | Candidate-name precision | No later direct SpikeTrack-MRM improvement found |
| 7 | `conditional memory retrieval visual object tracking distractor` | Retrieval recall | Template/memory selection work found, but no spike-MRM match |
| 8 | `historical template token compression visual tracking robust efficiency` | FARTrack precision | ETCTrack found |
| 9 | `template validity visual tracking physical token pruning occlusion` | FARTrack precision | ETCTrack, UTPTrack and reliability/template-update methods found |
| 10 | `reliability-aware historical state filtering visual tracking` | Temporal reliability | DTPTrack and STDTrack found |
| 11 | `adaptive template quantity quality selection object tracking` | Template-quality recall | AMST found |
| 12 | `robust template update backward tracking candidate template` | Template validation | BackTrack found |
| 13 | `search-region-guided adaptive template selection memory tracking` | Context-conditioned template selection | GTUTrack found |
| 14 | `confidence gated template update visual tracking occlusion` | Update-gating recall | Several template-update methods found; broad confidence-gating is crowded |
| 15 | `template contamination memory corruption single object tracking` | Robustness recall | Uncertainty/reliability/distractor-memory families found |
| 16 | `adaptive template number single object tracking compute` | Allocation recall | Multi-template and adaptive-memory prior art found |
| 17 | `autoregressive tracking template sparsification validity` | FARTrack-name/mechanism | FARTrack/ETCTrack/UTPTrack family overlap confirmed |
| 18 | `2025 2026 visual tracking template selection reliability compression` | Date-bounded recall | AMST, DTPTrack, ETCTrack, STDTrack and GTUTrack confirmed |

The detailed source candidates are listed in `screening/manager/2026-08-25_stage3B_hg6_N1_source_candidates.csv`. They remain provisional registry entries until N1 reconciliation.

---

# 2. CX007 — SpikeTrack

## A. Reconciled gap statement

The anchor is SpikeTrack-S256-T1, with T3 as a controlled temporal/template mode. Six Memory Retrieval Modules execute at fixed locations on every search frame. T3 repeats retrieval over three template/time slices and adds temporal gating. The official SpikeTrack paper reports a residual difficulty with visually similar objects and insufficient fine-grained discrimination.

The candidate-specific question is narrow:

> Does target–distractor ambiguity predict the marginal utility of particular SpikeTrack MRM scale/template retrieval contributions, such that retrieval allocation can be reduced on unambiguous frames while preserving or strengthening discriminative retrieval on ambiguous frames?

This is not a claim for generic SNN early exit or generic dynamic computation.

## B. Serious novelty adversaries

| Prior work | Year / venue | Mechanism | Relation to the reconciled gap | Collision class |
|---|---|---|---|---|
| **SEENN: Towards Temporal Spiking Early Exit Neural Networks** | 2023, NeurIPS | Chooses input-dependent SNN timesteps using confidence or reinforcement learning | Directly constrains any broad claim of sample-conditioned SNN latency/timestep allocation, but does not operate on visual tracking, MRMs or distractor discrimination | `ADJACENT_PRIOR_ART` |
| **Towards Efficient Spiking Transformer: a Token Sparsification Framework for Training and Inference Acceleration (STATA)** | 2024, ICML | Timestep-wise anchor-token sparsification and attention alignment | Constrains broad spiking-token sparsity claims; no tracker, MRM or target–distractor-conditioned retrieval allocation | `ADJACENT_PRIOR_ART` |
| **Adaptive Calibration: A Unified Conversion Framework of Spiking Neural Networks** | 2025, AAAI | Input-aware adaptive timesteps and spike compression | Constrains generic input-conditioned timestep/latency claims; no tracking-specific retrieval or distractor coupling | `ADJACENT_PRIOR_ART` |
| **Temporal Representation Enhancement (TRE)** | 2026, CVPR | Dynamically suppresses dominant temporal patterns to improve complementary/discriminative spiking features | Shares the fine-grained temporal-discrimination side of the question, but does not allocate tracking retrieval computation or target similar-object interference | `PARTIAL_COLLISION` |
| **Adaptive Capacity Autoregressive Visual Tracking (ARTrack-AC)** | 2026, CVPR | Predicts temporal difficulty and switches between low/high-capacity tracking modes | Shares state-conditioned accuracy/efficiency allocation in SOT, but not SNNs, MRMs or distractor-specific retrieval contribution | `PARTIAL_COLLISION` |
| **HiT-DyHiT** | 2025, IJCV | Early-exit easy/hard routing for efficient tracking | Strongly constrains generic dynamic-depth/easy–hard routing language; no SpikeTrack MRM or similar-object retrieval formulation | `PARTIAL_COLLISION` |

## C. Chronology

SEENN predates SpikeTrack by three years; STATA predates it by two years; Adaptive Calibration and HiT-DyHiT predate it by one year. TRE and ARTrack-AC are contemporaneous 2026 prior art for any future project contribution. Their presence means the project cannot claim the first adaptive SNN inference, first dynamic tracker capacity, first spiking-token sparsification, or first difficulty-conditioned computation.

No inspected source substantially implements all of the following together:

1. RGB single-object tracking;
2. a spike-driven MRM retrieval hierarchy;
3. condition-specific selection/allocation of MRM contributions;
4. a robustness objective defined by visually similar target–distractor ambiguity;
5. the same-frame relationship between retrieval compute and target–distractor separation.

## D. Surviving distinction

**INTERPRETATION — reasoned:** a narrow distinction survives. Existing SNN work adapts timesteps/tokens or improves temporal representation generally; existing tracking work adapts overall capacity/routes. The inspected prior art does not directly study whether individual MRM scale/template retrieval contributions in a spike-driven RGB tracker have condition-dependent utility under similar-object ambiguity.

Permissible future claim language, subject to diagnostics, is limited to:

> Candidate-specific investigation of ambiguity-conditioned MRM retrieval contribution in SpikeTrack, jointly measuring retrieval compute and target–distractor discrimination.

Prohibited broad claims include:

- first adaptive SNN inference;
- first dynamic timestep SNN;
- first conditional computation tracker;
- first spiking-token sparsification;
- first template gating or memory selection;
- first distractor-aware tracker;
- hardware/quantization/export novelty.

## E. Manager HG6 decision

**Manager provisional HG6: PASS**

The exact candidate-specific coupling remains materially distinguishable from the closest primary-source adversaries. This PASS does not validate the hypothesis or authorize architecture design.

### Required diagnostic consequence

Before any proposed architecture is designed, the project must reproduce the similar-object weakness and demonstrate a condition-by-MRM interaction through:

- per-MRM residual/output hooks;
- one-MRM-at-a-time controls;
- paired T1/T3 evaluation;
- target-versus-strongest-distractor score margin;
- same-frame latency and localization effects.

If those diagnostics fail, the candidate must be downgraded despite HG6 literature clearance.

---

# 3. CX013 — FARTrack

## A. Reconciled gap statement

The anchor is released final-sparse FARTrack-Tiny. The released path masks attention without physically shortening the full template/search sequence, re-embeds five raw templates each frame, and maintains uncapped released histories. The paper reports that prolonged disappearance or occlusion can invalidate templates, while its template-count ablation shows that more templates add compute without monotonic accuracy gain.

The proposed research question was:

> Can measurable template validity jointly determine physical template/token compute utility and robustness after occlusion/disappearance, so that invalid or redundant templates are physically removed rather than merely masked or retained?

## B. Serious novelty adversaries

| Prior work | Year / venue | Mechanism | Relation to the reconciled gap | Collision class |
|---|---|---|---|---|
| **BackTrack: Robust template update via Backward Tracking of candidate template** | 2023, arXiv-only novelty reference | Validates candidate templates through backward tracking and rejects unreliable updates; includes a lightweight/early-termination efficiency design | Predates FARTrack and directly covers explicit template-validity estimation plus robust rejection, though not physical multi-template token compression | `PARTIAL_COLLISION` |
| **UncTrack** | 2025, IEEE TIP | Uncertainty-aware prototype memory, reliability classification, reliable template/memory update and resampling | Covers uncertainty/reliability-based memory quality and recovery-side template control | `PARTIAL_COLLISION` |
| **AMST: Object Tracking Based on Collaborative Framework with Adaptive Multi-Strategy** | 2025, Information Sciences | Online reliability evaluation estimates tracking result and template quality/quantity; template update/selection manages reliable memory | Very close to validity/quality-driven template quantity and selection, although not token-level physical compression | `PARTIAL_COLLISION` |
| **STDTrack** | 2026, AAAI | Quality-based update in a spatiotemporal token maintainer, retaining reliable historical context in a lightweight tracker | Covers reliable temporal memory admission/maintenance under an efficiency objective | `PARTIAL_COLLISION` |
| **DTPTrack** | 2026, CVPR | Per-frame Temporal Reliability Calibrator filters noisy historical states; synthesizes compact dynamic priors | Directly covers frame-level reliability of historical states and compact temporal representation | `PARTIAL_COLLISION` |
| **ETCTrack: An Efficient Token Compression Framework for Visual Object Tracking** | 2026, CVPR | Historical templates create quadratic compute and can degrade performance; Adaptive Token Compressor filters redundant template tokens into a compact, discriminative representation, reducing template tokens and MACs | Closest collision: directly couples historical-template compression with both efficiency and tracking representation/accuracy; difference is token-level importance rather than an explicit FARTrack frame-validity variable | `DIRECT_COLLISION` at the research-gap level |
| **UTPTrack** | 2026, CVPR | Physically prunes search, static-template and dynamic-template tokens | Directly constrains claims about physical template-token removal; lacks the exact disappearance/validity coupling | `PARTIAL_COLLISION` |
| **GTUTrack** | 2026, Remote Sensing | Search-region-conditioned template selection, adaptive thresholds, structured template memory, explicit redundancy/noise control | Covers scene-conditioned template selection, quality, memory management and redundancy; multimodal UAV setting differs | `PARTIAL_COLLISION` |
| **DAM4SAM** | 2026, IJCV | Distractor-aware memory and quality/introspection-based memory management | Constrains distractor/noisy-memory and reliable-memory claims, though it is mask tracking on SAM-family hosts | `ADJACENT_PRIOR_ART` |

## C. Chronology

BackTrack, UncTrack and AMST predate the future project contribution and already establish template validity/reliability, quality/quantity estimation and adaptive selection. ETCTrack, DTPTrack, STDTrack, UTPTrack and GTUTrack are 2026 prior art available before this project proposes a method. Chronology relative to FARTrack's own publication does not preserve novelty for a later paper: these methods are all prior art for the project.

## D. Collision analysis

ETCTrack already states the same high-level coupling that motivated the FARTrack gap:

- more historical templates produce a large token/computation burden;
- historical-template content can degrade tracking performance;
- adaptive physical template-token compression is used to retain a compact discriminative target representation;
- efficiency and tracking accuracy are evaluated together.

DTPTrack then supplies per-frame reliability calibration and compact historical priors. AMST supplies template quality **and quantity** evaluation plus update/selection. BackTrack supplies explicit template validity testing. UTPTrack supplies physical template-token pruning. STDTrack, UncTrack and DAM4SAM further constrain reliable memory/update language.

**INTERPRETATION — reasoned:** no single paper uses the exact phrase “FARTrack template validity after target disappearance,” but the intended scientific mechanism is substantially occupied. The remaining distinction would largely be to combine a known template-quality/reliability signal with known physical token/template compression inside FARTrack. Renaming token importance as validity, moving from token granularity to template granularity, or specializing the combination to FARTrack is not a sufficiently material Q1-level distinction under the project's gate.

A narrowly explicit `ABSENT` state or identity-aware recovery would move toward the later long-term/person extension, not rescue the generic efficiency–robustness Core gap currently being audited.

## E. Manager HG6 decision

**Manager provisional HG6: FAIL**

The candidate-specific gap does not survive the mechanism-level novelty audit at the required ambition. The closest direct and partial collisions substantially cover:

- template/historical-state reliability;
- template quality and quantity;
- dynamic template selection;
- physical historical-template token compression;
- noisy/redundant memory suppression;
- compact robust temporal representation.

FARTrack remains a valuable implementation/reference baseline, but this gap does not progress to soft scoring or shortlist status.

### Reopening condition

FARTrack may only be reconsidered if controlled diagnostics reveal a distinct measurable causal variable that is not reducible to existing confidence, uncertainty, historical-state reliability, template quality/quantity, token importance, or distractor-memory mechanisms. Ordinary validity scoring plus compaction is insufficient.

---

# 4. Manager N1 summary

| Candidate | Manager provisional HG6 | Closest collision | Manager conclusion |
|---|---:|---|---|
| CX007 SpikeTrack | **PASS** | ARTrack-AC / HiT-DyHiT / SEENN / STATA are partial or adjacent | Narrow ambiguity-conditioned MRM retrieval question survives |
| CX013 FARTrack | **FAIL** | ETCTrack direct; DTPTrack/AMST/BackTrack/UTPTrack partial | Template-validity + physical compression gap is substantially occupied |

## Locked non-claims

- These are not final HG6 decisions until independent Codex N1 audit and reconciliation.
- No S1–S7 score is assigned.
- No candidate is ranked or shortlisted.
- No baseline is selected.
- No architecture is proposed.
- N2 remains locked until N1 reconciliation.
