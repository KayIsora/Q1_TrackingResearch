# Systematic screening protocol for 2025–2026 tracker candidates

**Status:** PROJECT DECISION — locked screening protocol.  
**Date:** 2026-08-24.  
**Purpose:** select the next main scientific baseline without choosing a tracker first and reverse-justifying a contribution.

This protocol must be applied before committing to a new baseline architecture. It operationalizes the scope defined in `10_research_program_scope_and_baseline_screening.md`.

No candidate receives preferential treatment because it is familiar, fashionable, already downloaded, or previously discussed.

---

## 1. Screening question

The screening asks:

> Which peer-reviewed/officially accepted 2025–2026 generic RGB SOT tracker provides the strongest combination of reproducibility, benchmark strength, **researchable computational redundancy**, a meaningful **robustness weakness**, feasible RTX 3060 research, credible Jetson Nano headroom, and novelty space for a new algorithmic mechanism?

The desired opportunity is not simply a large model that can be compressed. Preference is given to a baseline where unnecessary computation and tracking weakness are structurally related so that one mechanism may improve **efficiency and robustness together**.

---

## 2. Screening time boundary

For the first screening round, eligible baseline publications must have official peer-reviewed acceptance/publication status from:

- **2025-01-01 through the screening date** for 2025–2026 work;
- current 2026 papers are included only when official acceptance/publication can be established.

Future screening updates may extend the end date, but the screening date must always be recorded.

ArXiv-only work is not eligible as the main baseline, regardless of date, but remains mandatory for novelty auditing.

---

## 3. Discovery coverage

### 3.1 Primary discovery targets

Search peer-reviewed/officially accepted 2025–2026 work in:

- top computer-vision / machine-learning conferences;
- strong robotics venues when the method is still generic RGB SOT;
- Q1 journals and officially published online-first journal articles;
- other peer-reviewed venues only when the tracker has uniquely relevant lightweight, long-term, embedded, or architectural value.

### 3.2 Source priority

Candidate facts must ultimately be grounded in:

1. official paper/proceedings/journal page;
2. official project/repository;
3. official checkpoint/config/evaluator documentation;
4. official benchmark/toolkit documentation when needed.

Search-engine snippets, blogs, secondary tables, AI summaries, and community posts may provide discovery leads but cannot be the sole evidence for a scientific or eligibility claim.

### 3.3 Query families for the later search stage

The systematic search should cover multiple query families rather than only “lightweight tracker”:

- single object tracking 2025 / 2026;
- visual object tracking transformer 2025 / 2026;
- efficient / lightweight visual tracking;
- dynamic / adaptive computation tracking;
- token pruning / token merging / token routing tracking;
- memory / template efficient tracking;
- long-term single object tracking;
- autoregressive visual tracking;
- state-space / sequence-model visual tracking;
- edge / embedded visual tracking;
- tracker robustness under occlusion, distractors, fast motion, deformation, or camera motion.

The exact executed queries and discovery sources must be logged during the screening run.

---

## 4. Candidate unit and deduplication

The screening unit is a **method family / paper**, not every checkpoint variant.

Examples:

- Tiny/Nano/Base variants from one paper are one candidate family;
- journal extension and conference version are linked and treated as one family unless the journal introduces a materially different method;
- renamed repositories or mirrored repositories are not separate candidates.

Each candidate receives a stable local ID such as `C001`, `C002`, ... and one row in the candidate matrix.

---

## 5. HARD GATES — fixed eligibility rules

A candidate cannot enter the final shortlist unless **all hard gates are PASS**.

Allowed states: `PASS`, `FAIL`, `PENDING`.

A high soft score can never override a failed or unresolved hard gate.

### HG1 — Publication status and year

**PASS when:**

- officially peer-reviewed/accepted/published in 2025 or 2026;
- online-first journal article is allowed when official publication/acceptance status is established.

**FAIL when:**

- ArXiv-only / preprint-only;
- publication year outside the main-baseline window.

Older and ArXiv-only work is retained for novelty/reference search, not discarded from the literature audit.

### HG2 — Core task and modality fit

**PASS when:**

- method is generic RGB SOT or a directly extensible generic long-term SOT;
- initialization is compatible with an initial target box;
- the Core method does not require language, depth, thermal, event-camera, or person-specific identity input.

**FAIL when:**

- method fundamentally depends on another modality for its main result;
- it is person-only, MOT-only, segmentation-only, or active-control-only in a way that cannot provide the generic RGB box-SOT Core.

### HG3 — Official reproducibility assets

**PASS when all are available from the official authors/project:**

- source code;
- pretrained checkpoint(s);
- usable evaluation script/protocol or official integration sufficient to reproduce benchmark evaluation.

**FAIL when:**

- the main implementation is unavailable or only an unofficial third-party reimplementation exists;
- checkpoint/evaluation support is insufficient to make baseline reproduction realistic.

### HG4 — RTX 3060 12 GB research feasibility

This is a research-feasibility gate, not a requirement to reproduce the authors’ original full training farm.

**PASS when:**

- official checkpoints allow a credible initialization path;
- new modules can realistically be trained;
- meaningful partial or full-network fine-tuning is plausible on one RTX 3060 12 GB using reasonable techniques such as AMP, gradient accumulation, or checkpointing;
- the main hypothesis does not require inaccessible hardware merely to test it.

**FAIL when:**

- even the proposed research loop is structurally dependent on unavailable large multi-GPU resources;
- the only plausible workflow would freeze almost everything because the architecture is otherwise impossible to study.

**PENDING when:** the paper/code is insufficient to estimate VRAM/training feasibility before local profiling.

### HG5 — Jetson Nano B01 deployment plausibility

The candidate need not already run at 20–25 FPS on Nano.

**PASS when:**

- architecture has a credible mechanism-based path toward significant computation/runtime reduction;
- model/operator/memory structure is not obviously incompatible with the Nano target;
- deployment does not rely exclusively on future INT8 or desperate post-hoc pruning.

**FAIL when:**

- the baseline is so large/slow that the proposed contribution would have no plausible Nano path;
- the only imaginable deployment story is “compress later and hope.”

**PENDING when:** operator/export/runtime characteristics require code or device profiling.

### HG6 — Novelty non-collision gate

This gate is intentionally resolved late, after the candidate’s proposed research gap is specified.

**PASS when:**

- a 2023–2026 novelty audit, including ArXiv-only relevant work, does not show that the intended contribution has already been substantially solved;
- remaining differences are algorithmically meaningful rather than wording changes.

**FAIL when:**

- recent work already implements essentially the same mechanism for essentially the same claimed weakness;
- the only remaining change would be standard compression/porting or a trivial module replacement.

**PENDING during broad discovery:** expected. PENDING blocks final shortlist status.

---

## 6. SOFT SCORE — fixed 100-point ranking

Only candidates that survive the early hard gates are scored. Ratings are assigned from **0 to 5** for each dimension and converted to the fixed weight below.

Weighted contribution:

`weighted points = rating / 5 × dimension weight`

Total maximum = **100 points**.

| ID | Dimension | Weight |
|---|---|---:|
| S1 | Researchable computational redundancy | **20** |
| S2 | Meaningful robustness weakness | **15** |
| S3 | Shared efficiency–robustness mechanism potential | **20** |
| S4 | Novelty headroom after recent-work audit | **15** |
| S5 | Generic benchmark competitiveness | **10** |
| S6 | RTX 3060 research/training headroom | **10** |
| S7 | Jetson Nano deployment headroom | **10** |
|  | **Total** | **100** |

Venue prestige is **not added as a separate numeric score** because it would double-count scientific visibility and could overpower the actual research opportunity. Top conference/Q1 remains a strong baseline-selection preference and a tie-breaker; a lower-tier candidate requires an explicit written justification.

---

## 7. Soft-score anchors

### General 0–5 evidence scale

- **0 — absent/contradicted:** no credible opportunity or evidence argues against it;
- **1 — very weak/speculative:** mostly intuition, little source/code support;
- **2 — limited:** some evidence exists but scope or gain is small;
- **3 — credible:** clear enough to justify deeper reproduction/audit;
- **4 — strong:** multiple supporting signals and a well-defined experiment path;
- **5 — exceptional:** unusually strong, directly evidenced opportunity with high scientific leverage.

Scores of `4` or `5` require explicit evidence notes. Unknown information is recorded as `PENDING`, not silently assigned a favorable score.

### S1 — Researchable computational redundancy — 20 points

Ask: **Where is computation being spent unnecessarily, and can that computation be made smaller or conditional by a new mechanism?**

- **0:** no identifiable redundancy; architecture already aggressively optimized or every expensive component appears essential;
- **3:** at least one substantial component/path/token/memory/search cost is structurally identifiable and testable;
- **5:** clear large redundancy exists, is measurable, and admits a principled algorithmic intervention rather than only standard compression.

### S2 — Meaningful robustness weakness — 15 points

Ask: **What does the tracker fail on, specifically?**

- **0:** no specific scientifically relevant weakness can be established;
- **3:** a concrete weakness is supported by author limitation, benchmark attributes, code behavior, or reproducible failure evidence;
- **5:** weakness is important, repeatable, mechanism-linked, and inadequately addressed by current work.

Generic statements such as “occlusion is hard for trackers” do not justify a high score.

### S3 — Shared efficiency–robustness mechanism potential — 20 points

Ask: **Can one algorithmic mechanism improve compute allocation and difficult-case tracking together?**

- **0:** only unrelated “compression module + robustness module” ideas are visible;
- **3:** plausible shared state/reliability mechanism can reduce easy-frame cost while preserving stronger processing for hard frames;
- **5:** architecture exposes a direct, testable structural coupling between wasted computation and the failure mode.

This is one of the two highest-weight dimensions.

### S4 — Novelty headroom — 15 points

Ask: **After auditing 2023–2026 work, how much meaningful algorithmic space remains?**

- **0:** clear novelty collision; intended mechanism already substantially exists;
- **3:** related work exists but a material mechanism/gap remains;
- **5:** gap survives broad recent-work audit with a clearly differentiated proposed research question.

This score is PENDING until the novelty audit is sufficiently complete.

### S5 — Generic benchmark competitiveness — 10 points

Ask: **Is the baseline scientifically strong enough that improving it matters?**

- **0:** weak or unconvincing generic SOT performance for its publication period;
- **3:** competitive modern baseline with credible results;
- **5:** strong across multiple relevant generic benchmarks and/or clearly competitive with contemporary methods.

Do not mix incompatible benchmark protocols when assigning this score.

### S6 — RTX 3060 research/training headroom — 10 points

Ask: **Can the model be modified and genuinely trained, not merely run?**

- **0:** research loop is infeasible;
- **3:** checkpoint-based development plus meaningful partial fine-tuning is realistic;
- **5:** new modules and substantial/full joint fine-tuning appear comfortably feasible with reproducible single-3060 techniques.

Original author training on many GPUs does not automatically make this score low if checkpoint-based research is genuinely feasible.

### S7 — Jetson Nano deployment headroom — 10 points

Ask: **After adding the contribution, is there still a credible route to the Nano target?**

- **0:** structurally implausible;
- **3:** plausible after the proposed algorithmic efficiency gain plus normal FP16/TensorRT optimization;
- **5:** architecture already has strong edge-friendly characteristics and meaningful additional headroom without relying on INT8 as a rescue mechanism.

Desktop FPS alone cannot justify this score.

---

## 8. Shortlist rule

A candidate is eligible for the **primary 2–3 candidate shortlist** only when:

1. **HG1–HG6 are all PASS**;
2. total soft score is **>= 75/100**;
3. `S1 >= 3/5`;
4. `S2 >= 3/5`;
5. `S3 >= 3/5`;
6. `S4 >= 3/5`;
7. there is no unresolved evidence item that could plausibly reverse the selection.

Interpretation:

- **>= 85:** exceptional priority candidate;
- **75–84:** shortlist candidate;
- **65–74:** reserve / deeper audit only if uniquely promising;
- **< 65:** do not prioritize as the main baseline.

A candidate from a lower-tier venue should normally require **>= 80/100** plus a written exceptional-value rationale to compete with top-conference/Q1 candidates.

---

## 9. Tie-break rules

If two candidates have similar total scores, apply tie-breakers in this order:

1. higher **S3 shared efficiency–robustness opportunity**;
2. higher **S4 novelty headroom**;
3. higher **S1 researchable redundancy**;
4. higher **S7 Jetson Nano headroom**;
5. stronger official reproducibility assets;
6. stronger venue/publication quality;
7. lower implementation/research risk.

Do not break ties using desktop FPS alone.

---

## 10. Evidence extraction required for every candidate

For every candidate surviving initial discovery, record at least:

### Publication / reproducibility

- title;
- authors;
- year;
- venue;
- official acceptance/publication status;
- official paper URL/DOI;
- official repository;
- checkpoint availability;
- evaluator/config availability;
- repository commit/ref used for audit.

### Task / model

- SOT formulation;
- modality;
- initialization input;
- backbone;
- template/search structure;
- temporal/memory mechanism;
- prediction head/decoder;
- input resolution(s).

### Efficiency

- parameters;
- MACs/FLOPs if reported or reproducibly measured;
- reported FPS/latency;
- exact reported speed hardware;
- memory evidence if available;
- likely major compute modules;
- edge-unfriendly operators or dynamic-shape risks.

### Training

- training datasets;
- original training hardware;
- training stages;
- checkpoint initialization availability;
- expected RTX 3060 VRAM/time feasibility;
- feasible freeze/unfreeze options.

### Accuracy / robustness

- LaSOT / GOT-10k / TrackingNet results when available;
- other relevant benchmarks;
- author-reported limitations;
- failure attributes;
- code-visible reliability/template/search behavior;
- targeted weakness hypothesis.

### Research opportunity

- specific computational redundancy hypothesis;
- specific robustness weakness;
- possible single mechanism linking both;
- expected ablations;
- novelty-adversary papers 2023–2026;
- likely contribution strength;
- implementation risk;
- Nano deployment headroom.

---

## 11. Novelty audit rule

For each candidate that reaches serious consideration, novelty search must include:

- the baseline paper’s related work and citing/closely related recent methods;
- 2025–2026 peer-reviewed work;
- relevant 2023–2024 prior art;
- ArXiv-only 2025–2026 work that could collide with the mechanism;
- methods outside the exact baseline family when they solve the same computational/robustness idea.

Novelty is audited at the **mechanism level**, not only by tracker name.

Example:

> If the idea is “uncertainty-driven adaptive depth,” search adaptive-depth, early-exit, dynamic-compute, reliability-aware routing, and state-conditioned computation in tracking—not only papers that cite the chosen baseline.

“Not eligible as baseline” never means “ignorable for novelty.”

---

## 12. Reproduction gate after shortlist

The screening score selects what to reproduce; it does not approve the final architecture.

For the top 2–3 candidates:

1. reproduce official checkpoint/config/evaluator;
2. verify output/metric consistency;
3. profile module-level compute and memory where possible;
4. instrument the suspected redundancy;
5. reproduce or induce the suspected robustness failure;
6. profile RTX 3060 training feasibility;
7. perform preliminary export/operator audit for Jetson;
8. revisit HG4–HG6 and soft scores using measured evidence.

A candidate may be rejected after reproduction even if it initially scored highly.

---

## 13. Anti-bias rules

- Do not change weights after seeing which candidate wins. Any weight change requires a documented protocol revision before re-scoring all candidates.
- Do not assign a favorable score to missing information; use PENDING.
- Do not use paper self-reported desktop FPS as Jetson evidence.
- Do not reward parameter reduction twice through both “redundancy” and “Nano headroom” without separate justification.
- Do not equate an author-reported limitation with a confirmed causal mechanism.
- Do not prefer a candidate because code is already familiar.
- Do not design the final proposed architecture before reproduction verifies the targeted redundancy/weakness.
- Do not use Layer-B person identity/ReID features to rescue a weak Core score.

---

## 14. Decision record

Each candidate ends a screening round with exactly one state:

- `DISCOVERED`;
- `EXCLUDED_HARD_GATE`;
- `PENDING_EVIDENCE`;
- `RESERVE`;
- `SHORTLIST`;
- `REPRODUCE`;
- `REJECT_AFTER_REPRODUCTION`;
- `SELECTED_BASELINE`.

The reason must be recorded in the candidate matrix.

---

## 15. Machine-readable candidate matrix

Use:

`screening/candidate_screening_matrix.csv`

The file begins as a schema/template and is populated only when the systematic search starts.

---

## 16. Protocol lock

**RESEARCH GATE — project decision.** This protocol is frozen before candidate search begins.

A later revision is allowed only when:

- a criterion proves impossible to evaluate consistently;
- a newly discovered methodological issue makes the protocol unfair;
- the project scope itself is explicitly reopened.

Any revision must:

1. record the date and reason;
2. occur before using the new rule to select a favored candidate;
3. re-score all active candidates under the same revised rules.

The next action after this file is locked is **systematic discovery of 2025–2026 candidates**, not proposed-architecture design.
