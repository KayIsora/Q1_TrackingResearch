# Stage 4A-S1 — SpikeTrack outcome-independent interval proposal and visual-review protocol

**Date:** 2026-08-26  
**Status:** LOCKED BEFORE INTERVAL PROPOSAL  
**Entry data:** canonical author-attributed OTB100 package acquired in Stage 4A-E2  
**Prerequisite:** `screening/reconciliation/2026-08-26_stage4A_E2_otb_reconciliation.md`

## 1. Purpose

Stage 4A-S1 converts the broad E2 sequence inventory into an auditable interval proposal package for Manager review. It uses only source frames, OTB ground truth, official attributes and direct visual inspection independent of SpikeTrack output.

Stage 4A-S1 does not freeze the diagnostic slice and does not start Stage 4B.

## 2. Locked non-use boundary

The following materials must not be opened, queried or used when proposing sequences or intervals:

- local SpikeTrack predictions;
- author-released SpikeTrack predictions;
- score maps or confidence values;
- per-frame IoU or failure records;
- MRM logs;
- ablation results;
- first-divergence reports;
- any tracker-derived hard-frame ranking.

The E2 candidate/control text inventory may be used because it was created before E2 tracker execution and from outcome-independent evidence.

## 3. Source contract

Use only the byte-verified acquired OTB source tree:

`F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015\`

Use the exact logical sequence/frame mapping of the pinned SpikeTrack `OTBDataset` at commit:

`1537db51a1cc9f6e30cce469fba3e51f5721b3d0`.

No new dataset download is permitted.

## 4. Candidate-sequence pool

Start from all E2 rows with a non-empty `candidate_distractor_reason`.

Do not accept a sequence merely because the E2 row contains a reason. Each sequence must be rescanned at interval level.

### Priority evidence tiers

- `TIER_A`: a visually similar same-class or same-role distractor co-occurs at comparable scale and is plausibly inside the target-centered search context for at least five consecutive evaluable frames.
- `TIER_B`: a same-class/similar-shape distractor co-occurs, but scale, proximity or duration is weaker or more uncertain.
- `TIER_C`: only broad clutter, background repetition, printed/depicted lookalikes or weak semantic similarity is visible.

Only Tier A and strong Tier B proposals are eligible for the final distractor slice. Tier C may be retained as contextual reference but not used to satisfy the minimum distractor count unless Manager explicitly approves it before Stage 4B.

## 5. Bounded scan procedure

For each candidate sequence:

1. inspect a uniform coarse grid of at least 25 source frames, or every frame when the sequence has fewer than 125 frames;
2. if a plausible co-occurrence is found, refine the surrounding region frame-by-frame;
3. define one or more continuous candidate intervals;
4. do not inspect more than necessary once all credible intervals for that sequence are recorded;
5. record exactly how the interval was found.

The scan may use GT only to locate the annotated target and to construct a nominal target-centered search context. It may not use tracker state or prediction.

## 6. Candidate distractor interval criteria

A proposed distractor interval must satisfy all of the following:

- the annotated target GT is valid throughout the interval;
- the target is visible enough for visual comparison, allowing partial occlusion but not a fully absent target for the whole interval;
- at least one non-target lookalike co-occurs for at least five consecutive evaluable frames;
- the lookalike is similar in class, visual form, appearance or functional role;
- the lookalike is plausibly inside or near the nominal SpikeTrack search context centered on the previous-frame GT;
- the start and end frame are chosen from source content, not tracker behavior;
- the proposal describes the distractor and why confusion is plausible.

### Interval length

Preferred core interval length: 5–40 frames.

When the event lasts longer, propose a representative core interval containing the strongest continuous co-occurrence while preserving at least two context frames before and after when available. The final Manager slice may adjust the bounds before any tracker diagnostic is run.

## 7. Nominal search-context rule

Use the official S256-T1 search-factor contract from the pinned config and GT from frame `t-1` to derive a nominal search crop for frame `t`.

This crop is a source-selection aid only. It is not a tracker prediction.

Record whether the proposed distractor is:

- `INSIDE_NOMINAL_SEARCH`;
- `NEAR_SEARCH_BOUNDARY`;
- `OUTSIDE_NOMINAL_SEARCH`;
- `UNRESOLVED`.

Intervals classified only as `OUTSIDE_NOMINAL_SEARCH` are not primary distractor candidates unless the visual event also involves abrupt motion/search enlargement that the Manager explicitly accepts later.

## 8. Control interval proposals

For every proposed distractor interval, propose at least one possible control.

Preference order:

1. another interval in the same sequence with no similar distractor;
2. another sequence of the same object class with similar target scale and motion;
3. another sequence with comparable OTB challenge attributes and target size.

Controls must not be chosen because SpikeTrack performs well on them.

Record the matching basis:

- object superclass;
- target area ratio;
- motion magnitude from GT center displacement;
- scale change from GT;
- occlusion state/attributes;
- interval length;
- same-sequence versus cross-sequence.

## 9. Diversity safeguards

The proposal package must provide enough material for a final sequence-disjoint slice with:

- at least 10 unique distractor-bearing sequences;
- at least 3 broad target superclasses across the full proposed set;
- no single broad superclass accounting for more than 60% of the proposed primary sequences unless the available source data make this impossible and the limitation is reported;
- no more than 3 proposed primary intervals from one sequence;
- at least 6 sequences suitable for discovery and 4 additional sequences suitable for hold-out.

These are proposal-level coverage requirements. Manager assigns the final split later.

## 10. Broad superclass map

Use one of:

- `PERSON`;
- `VEHICLE`;
- `ANIMAL`;
- `FACE_HEAD`;
- `OBJECT_OTHER`.

The map is for coverage accounting only and does not change generic-SOT task identity.

## 11. Contact-sheet contract

For every primary distractor proposal and every proposed control, generate one compact contact sheet containing five source frames:

- interval start;
- approximately 25%;
- midpoint;
- approximately 75%;
- interval end.

Overlay only:

- GT target box in green;
- candidate distractor box in red when manually annotated and visually clear;
- nominal search-context rectangle in blue when useful;
- frame number and sequence name.

Do not overlay tracker predictions, scores or failure markers.

### Image constraints

- JPEG or PNG;
- readable labels;
- maximum long side 1800 pixels;
- target file size preferably below 1 MiB;
- total committed contact-sheet payload no more than 30 MiB;
- no full-resolution source sequence or video committed.

If the contact-sheet payload would exceed the cap, retain Tier A sheets first and report omitted lower-tier proposals.

## 12. Manual distractor box

At minimum, annotate a distractor box on the midpoint frame of each Tier A proposal.

Where practical, annotate all five contact-sheet frames. The boxes are visual-review aids, not benchmark ground truth.

Record the annotation method and whether the distractor is fully visible, partially occluded or truncated.

## 13. Proposed split

Codex may provide a `proposed_split` field with values:

- `DISCOVERY_CANDIDATE`;
- `HOLDOUT_CANDIDATE`;
- `UNASSIGNED`.

The proposal must keep sequences disjoint across the two candidate groups. It is not the final split. Manager may change it before any diagnostic run.

No split may be selected using tracker performance.

## 14. Required CSV — distractor proposals

Create:

`screening/codex/2026-08-26_stage4A_S1_distractor_interval_proposals.csv`

Columns:

- proposal_id
- dataset
- sequence
- broad_superclass
- object_class
- official_attributes
- interval_start
- interval_end
- interval_length
- evidence_tier
- distractor_description
- similarity_basis
- search_context_status
- midpoint_distractor_bbox_or_na
- target_visibility
- occlusion_state
- fast_motion_from_gt
- low_resolution_from_gt
- scan_method
- proposed_split
- contact_sheet_path
- manager_review_status
- notes

All rows must have `manager_review_status=PENDING`.

## 15. Required CSV — control proposals

Create:

`screening/codex/2026-08-26_stage4A_S1_control_interval_proposals.csv`

Columns:

- control_id
- linked_proposal_id
- dataset
- sequence
- interval_start
- interval_end
- interval_length
- same_sequence
- object_class
- broad_superclass
- target_area_ratio_summary
- gt_motion_summary
- scale_change_summary
- occlusion_match
- attribute_match
- no_similar_distractor_evidence
- matching_basis
- contact_sheet_path
- manager_review_status
- notes

All rows must have `manager_review_status=PENDING`.

## 16. Contact-sheet manifest

Create:

`screening/codex/2026-08-26_stage4A_S1_contact_sheet_manifest.csv`

Columns:

- sheet_id
- proposal_or_control_id
- relative_path
- sha256
- byte_size
- width
- height
- source_sequence
- source_frame_ids
- overlays
- manager_review_status

## 17. Visual artifacts

Create contact sheets only under:

`screening/codex/artifacts/stage4A_S1/contact_sheets/`

Do not commit raw OTB frames separately.

## 18. Required report

Create:

`screening/codex/2026-08-26_stage4A_S1_slice_proposal_report.md`

Required sections:

1. Boundary and prohibited-source declaration
2. Source dataset and hash identity
3. Candidate-sequence scan coverage
4. Tier A/B/C counts
5. Distractor interval proposal summary
6. Control proposal summary
7. Superclass diversity
8. Proposed discovery/hold-out candidate split
9. Contact-sheet coverage and payload size
10. Ambiguous/rejected cases
11. Exact remaining coverage gaps
12. Files produced
13. Readiness conclusion

Allowed conclusion:

- `S1_COMPLETE_READY_FOR_MANAGER_VISUAL_REVIEW`;
- `S1_INCOMPLETE`;
- `S1_INSUFFICIENT_INTERVAL_COVERAGE`.

## 19. Stage restrictions

Stage 4A-S1 must not:

- run SpikeTrack;
- run T1/T3;
- apply the instrumentation patch;
- run an MRM control;
- calculate tracker IoU/AUC;
- inspect official/local raw predictions;
- freeze final intervals;
- assign final ambiguity levels;
- finalize discovery/hold-out split;
- create the Manager diagnostic-slice file;
- start Stage 4B;
- assign DIAG or soft scores.

## 20. Manager review gate

After Codex commits the S1 package, Manager will:

- inspect proposal tables;
- visually inspect the contact sheets;
- reject weak or non-search-relevant distractors;
- adjust interval bounds using source evidence only;
- choose sequence-disjoint discovery and hold-out sets;
- match controls;
- assign final ambiguity levels;
- commit the frozen Manager diagnostic slice.

Only then may Stage 4B be authorized.

## 21. Locked state

- E2 acquisition: COMPLETE
- local operational diagnostic baseline: ACCEPTED WITH RELEASE-PROVENANCE LIMIT
- Stage 4A-E3 Linux comparison: OPTIONAL / NOT AUTHORIZED
- Stage 4A-S1: READY
- frozen slice: NOT CREATED
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
