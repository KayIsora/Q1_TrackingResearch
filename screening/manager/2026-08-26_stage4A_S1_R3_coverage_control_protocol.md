# Stage 4A-S1-R3 — Interval-count expansion and control-validity protocol

**Date:** 2026-08-26  
**Status:** LOCKED BEFORE R3 EXECUTION  
**Prerequisite:** `screening/reconciliation/2026-08-26_stage4A_S1_R2_final_review.md`

## 1. Purpose

R3 constructs a source/GT-only candidate package capable of satisfying the locked Stage-4 diagnostic-slice minimum:

- at least 12 discovery distractor intervals and 12 `MATCH_PASS` controls from at least 6 primary sequences;
- at least 8 hold-out distractor intervals and 8 `MATCH_PASS` controls from at least 4 additional primary sequences.

R3 also resolves or replaces the four R2 primaries that lack accepted controls.

R3 does not freeze the final slice, run SpikeTrack, inspect tracker outcomes, start Stage 4B, assign `DIAG_PASS`/`DIAG_FAIL`, score a candidate, or design an architecture.

## 2. Outcome-independent boundary

Use only:

- the accepted v2 clean room;
- canonical OTB100 source frames and GT;
- source-only R1/R2 tables and contact sheets;
- the Manager R1/R2 review decisions;
- this protocol.

Do not access:

- local or author-released tracker predictions;
- AUC, IoU, success/failure results;
- first-divergence evidence;
- score/confidence maps;
- MRM logs or ablation results;
- tracker-derived rankings;
- the invalid v1 clean room or invalidated temporary S1 work.

The quarantine remains:

- Deer
- Crossing
- Couple

Their frames may not be opened and they may not appear in any proposal, control, split or coverage count.

## 3. Accepted R2 pair anchors

R3 must preserve the source identity and group of these six pair anchors unless source-integrity revalidation fails:

### Discovery

- R1-P01 Basketball + R2-C01 David3
- R1-P02 Bolt + R2-C02 Human8
- R1-P09 Liquor + R2-C09 Liquor

### Hold-out

- R1-P03 Crowds + R2-C03 Crowds
- R1-P05 BlurCar4 + R2-C05 Suv
- R1-P12 Soccer + R2-C12 Man

R3 may adjust an anchor's interval bounds only to:

- equalize a same-sequence control length;
- correct a source-only integrity error;
- keep the same visible distractor event while improving continuous evidence.

Any adjustment requires full traceability and Manager review.

### Sensitivity notes that must remain

- P01: cross-scene/activity domain shift;
- P02: sprint versus isolated-person context;
- P05: color/rear-view versus grayscale rear/side-view domain shift;
- P12: partial crowd/clutter visibility versus clean control.

These notes do not invalidate the anchors, but they must remain machine-readable for later sensitivity analysis.

## 4. Held R2 primaries

The following source intervals remain valid distractor leads but have no accepted primary control:

- R1-P04 BlurCar2
- R1-P07 Bird1
- R1-P10 Football
- R1-P11 Football1

R3 may perform exactly one further bounded source-only rematching attempt for each.

### Acceptance requirements

A new control must satisfy all locked matching gates and receive `MATCH_PASS`.

Specific prohibitions:

- BlurCar2 may not reuse CarScale 143–163 unless a new interval brings normalized p90 motion within the locked gate;
- Bird1 may not use Panda, Dog, Dog1, plush, toy, print or another incompatible animal subtype;
- Football may not use Biker novelty mask/headgear as a primary matched control;
- Football1 may not use Surfer bare head as a primary matched control.

If no `MATCH_PASS` control is found, the primary becomes `REPLACEMENT_REQUIRED` for the final primary analysis. It may remain only as secondary exploratory material outside Criteria A/B.

## 5. Locked reserve pool

Replacement primaries may be selected only from the following source-only R1 reserve pool:

### PERSON

- Girl
- Human3
- Human4_2
- Jogging_1
- Skating1
- Subway
- Walking2

### VEHICLE

- Car4
- CarDark
- Suv

### FACE_HEAD

- Freeman3
- Freeman4
- Girl
- Shaking
- Singer1

### Conditional additional lead

- Ironman, only if target/non-target independence and broad superclass are explicitly resolved from source frames.

Excluded:

- Coupon
- Jogging_2 when it duplicates Jogging_1 source event
- Bolt2 when it duplicates the Bolt race event
- Matrix while the distractor is outside the nominal search context
- R1-P06 Car24
- R1-P08 Board

Reserve selection must be based only on source/GT evidence, matching feasibility and diversity—not tracker behavior.

## 6. Required final proposal-package size

R3 must produce a provisional package containing at least:

### Discovery

- 12 `analysis_eligible=true` distractor intervals;
- 12 preferred controls with `overall_state=MATCH_PASS`;
- at least 6 unique primary sequences.

### Hold-out

- 8 `analysis_eligible=true` distractor intervals;
- 8 preferred controls with `overall_state=MATCH_PASS`;
- at least 4 additional unique primary sequences.

No `EXCEPTION_PENDING_MANAGER` or `MATCH_FAIL` pair counts toward 12/8.

Additional exploratory intervals may be reported separately but cannot satisfy the minimum.

## 7. Distinct-event rule

Multiple intervals from the same primary sequence are allowed only when they represent distinct source events.

For every second or third interval from one sequence, record:

- `event_id`;
- overlap with other selected intervals;
- frame gap;
- source-only event-boundary explanation;
- whether the distractor identity/event changed;
- whether the target state returned to a non-event condition between intervals.

Required:

- no interval overlap;
- normally at least 10 frames between intervals;
- if the gap is below 10, an unambiguous visual event boundary must be documented;
- one long continuous distractor event may not be split into adjacent artificial intervals;
- maximum 3 analysis-eligible intervals per primary sequence.

Sequence-clustered statistics later handle within-sequence dependence; the distinct-event rule prevents artificial sample inflation.

## 8. Primary interval requirements

Every analysis-eligible distractor interval must:

- have valid target GT throughout;
- keep the target visible enough for evaluation;
- contain a genuine non-target lookalike for at least 5 consecutive frames;
- place the lookalike inside or near the nominal GT-derived search context;
- have source-content-based bounds;
- have a clear class/appearance/role similarity explanation;
- be Tier A or strong Tier B;
- have a preferred `MATCH_PASS` control.

Preferred length remains 5–40 frames.

## 9. Control search and matching gates

For every interval, search in this order:

1. same-sequence clean interval;
2. non-quarantined same-class sequence;
3. compatible visual subtype in the same broad superclass;
4. broader-class alternatives only for documented exploratory use, not analysis-eligible matching.

Every preferred control must pass:

- equal length where possible, otherwise within ±2 frames;
- median target-area ratio within factor 2;
- normalized p90 motion within factor 2, or absolute difference <=0.03 when both values are below 0.03;
- max/min area ratio within factor 2;
- no full-occlusion mismatch;
- same broad superclass and compatible visual subtype;
- no similar distractor throughout the complete control interval;
- same split as linked primary;
- no cross-group sequence leakage.

`ANIMAL` and `FACE_HEAD` subtype compatibility is mandatory for analysis eligibility.

## 10. Control reuse

- the identical control interval may not be reused;
- one control sequence may provide at most two distinct control intervals;
- all uses of a control sequence must remain within one split;
- two control intervals from one sequence must be non-overlapping and source-distinct;
- control reuse count and interval overlap must be audited.

## 11. Split rules

Group assignment is sequence-level.

- a primary sequence and all of its intervals belong to one group;
- a control sequence and all of its intervals belong to one group;
- the complete discovery and hold-out source-sequence sets must have empty intersection;
- the minimum unique primary sequence counts remain 6 and 4;
- discovery/hold-out assignment remains provisional until Manager final review.

## 12. Diversity

The analysis-eligible 20-pair package must retain:

- at least 3 broad superclasses overall;
- no broad superclass above 60% when avoidable;
- source and visual diversity documented without using tracker results.

Loss of the ANIMAL category is permitted if no scientifically matched bird/animal control exists, because the locked minimum requires three—not five—broad superclasses.

## 13. Ambiguity proposal fields

R3 may propose, but not finalize, source-only ambiguity levels:

- `2`: Tier A, comparable lookalike clearly inside search context;
- `1`: strong Tier B or near-boundary lookalike;
- `0`: control interval with no similar distractor.

Manager assigns the final level before freezing.

## 14. Manual distractor annotation

For every analysis-eligible distractor interval:

- annotate the distractor on all five review-sheet frames;
- record the midpoint distractor box;
- record visibility/truncation/occlusion;
- do not call the manual box benchmark ground truth.

Per-frame full-interval annotation remains a later freeze/annotation task unless R3 produces it safely.

## 15. Required expanded primary CSV

Create:

`screening/codex/2026-08-26_stage4A_S1_R3_expanded_distractor_intervals.csv`

Required fields:

- `r3_interval_id`
- `source_parent_id_or_new`
- `dataset`
- `sequence`
- `group`
- `event_id`
- `broad_superclass`
- `object_class`
- `official_attributes`
- `interval_start`
- `interval_end`
- `interval_length`
- `evidence_tier`
- `proposed_ambiguity_level`
- `distractor_description`
- `similarity_basis`
- `search_context_status`
- `midpoint_distractor_bbox_or_na`
- `target_visibility`
- `occlusion_state`
- all GT-derived area/motion/scale metrics
- `event_separation_evidence`
- `analysis_eligible`
- `replacement_trace`
- `sensitivity_notes`
- `pair_sheet_path`
- `manager_review_status`

Required status:

`manager_review_status=PENDING_R3_FINAL_REVIEW`.

## 16. Required expanded control CSV

Create:

`screening/codex/2026-08-26_stage4A_S1_R3_expanded_controls.csv`

Required fields:

- `r3_control_id`
- `linked_r3_interval_id`
- `group`
- `dataset`
- `sequence`
- `interval_start`
- `interval_end`
- `interval_length`
- `same_sequence`
- `object_class`
- `broad_superclass`
- `visual_subtype`
- all GT-derived area/motion/scale metrics
- `no_similar_distractor_evidence`
- `control_event_id`
- `control_sequence_reuse_count`
- `control_interval_reused`
- `exception_state`
- `analysis_eligible`
- `pair_sheet_path`
- `manager_review_status`

Every analysis-eligible primary must have exactly one preferred analysis-eligible control.

## 17. Pair audit

Create:

`screening/codex/2026-08-26_stage4A_S1_R3_pair_matching_audit.csv`

Include all R2 gate values plus:

- primary event-distinctness pass;
- control interval reuse pass;
- control sequence split pass;
- analysis eligibility;
- held/replacement trace;
- overall state.

Allowed primary-analysis state:

- `MATCH_PASS` only.

Exceptions and failures must be marked exploratory/ineligible.

## 18. Coverage and split audit

Create:

`screening/codex/2026-08-26_stage4A_S1_R3_coverage_split_audit.csv`

Report by group:

- analysis-eligible interval count;
- analysis-eligible control count;
- unique primary sequence count;
- complete primary/control source sequence set;
- cross-group intersection;
- superclass counts and shares;
- max primary intervals per sequence;
- max control intervals per sequence;
- duplicate/overlap flags;
- locked 12/8 gate pass/fail.

## 19. Pair-review sheets

Create one source-only pair sheet for every analysis-eligible pair.

- top row: five distractor frames;
- bottom row: five matched-control frames;
- allowed overlays only;
- footer/panel: IDs, group, event ID, metrics, all matching gates and analysis-eligibility state.

Store under:

`screening/codex/artifacts/stage4A_S1_R3/pair_sheets/`

Total committed payload must remain below 45 MiB.

Create a manifest with hashes, sizes and source frame IDs.

## 20. Report

Create:

`screening/codex/2026-08-26_stage4A_S1_R3_coverage_control_report.md`

Required sections:

1. Outcome-independence declaration
2. Canonical source and quarantine
3. R2 anchor traceability
4. Held-primary rematch results
5. Replacement selection trace
6. Distinct-event expansion procedure
7. Discovery 12-pair package
8. Hold-out 8-pair package
9. Control search and rejection trace
10. Pair matching gate results
11. Full sequence-disjoint audit
12. Control reuse/overlap audit
13. Superclass diversity
14. Exploratory/ineligible intervals
15. Pair-sheet package
16. Exact remaining blockers
17. R3 conclusion

Allowed conclusions:

- `S1_R3_COMPLETE_READY_FOR_MANAGER_FREEZE_REVIEW`
- `S1_R3_INTERVAL_OR_CONTROL_COVERAGE_INSUFFICIENT`
- `S1_R3_INVALID_OUTCOME_EXPOSURE`
- `S1_R3_INCOMPLETE`

## 21. Required Q1 artifacts

Create only:

- expanded primary CSV;
- expanded control CSV;
- pair audit CSV;
- coverage/split audit CSV;
- pair-sheet manifest;
- R3 report;
- exact command log;
- pair sheets;
- optional exact reproducibility script.

Do not modify R1/R2, Manager, reconciliation, candidate matrix, references, RULE or docs files.

## 22. Validation

Before commit verify:

- no tracker outcome accessed;
- quarantine respected;
- six accepted R2 anchors preserved or source-integrity adjustment disclosed;
- four held primaries rematched or replaced;
- at least 12 discovery `MATCH_PASS` pairs;
- at least 8 hold-out `MATCH_PASS` pairs;
- at least 6/4 unique primary sequences;
- all selected events source-distinct;
- no long event artificially split;
- no more than 3 intervals per primary sequence;
- no identical control interval reused;
- no control sequence used more than twice;
- no control sequence crosses groups;
- complete discovery/hold-out sequence intersection empty;
- every analysis-eligible pair passes subtype and numeric gates;
- no exception counts toward the minimum;
- no final slice frozen;
- no Stage 4B, DIAG or scoring work.

## 23. Locked downstream state

- Stage 4A-S1-R3: READY
- Manager freeze review: LOCKED PENDING R3
- frozen diagnostic slice: NOT CREATED
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
