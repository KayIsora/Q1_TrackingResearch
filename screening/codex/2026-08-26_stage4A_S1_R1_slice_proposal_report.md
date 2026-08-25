# Stage 4A-S1-R1 — Source-only interval proposal report

**Date:** 2026-08-26  
**Status:** `S1_R1_COMPLETE_READY_FOR_MANAGER_VISUAL_REVIEW`  
**Decision scope:** all intervals, tiers, controls, and split labels below are provisional proposals with `manager_review_status=PENDING`.

## 1. Boundary and prohibited-source declaration

This was a fresh Codex lane. No previous S1 scan, judgment, selection, script, or temporary output was reused. Scientific selection used only the accepted v2 clean-room inputs and canonical OTB JPG/GT source. SpikeTrack was not run; no checkpoint/model was instantiated; no prediction, AUC, IoU, success/failure record, score/confidence map, MRM log, ablation result, reproduction result, or tracker-derived ranking was accessed.

## 2. Outcome-exposure quarantine declaration

`Deer`, `Crossing`, and `Couple` were filtered before any frame path was opened. They were excluded from candidate, control, coverage, and split pools. Their `frames_opened` values remain `false`. The invalid v1 clean-room root was not accessed.

## 3. Source dataset and hash identity

- canonical root: `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015\`
- archive SHA-256: `aad6be170d417777a5cee0b99bdd367e540b81f9020ac08b5c96d4d5d5094be5`
- extracted-file-manifest SHA-256: `a58329bea07dc96f9d35ad5d2a22785e23198f90c451da6369f7eaa985625032`
- evaluator mapping: accepted v2 copy of pinned `otbdataset.py`
- nominal context: previous-frame GT center with square side `4.0 * sqrt(GT_width * GT_height)`; source-selection aid only

## 4. Candidate-sequence scan coverage

All **44** non-quarantined candidate leads were rescanned from zero. Sequences with at least 125 frames used 25 uniformly spaced frames; `Bird2`, `Football1`, and `Matrix` used every frame because they have fewer than 125. The machine coverage file records **1,298/1,298** required coarse frames, followed by frame-by-frame refinement for proposed events.

| Sequence | Coarse assessment | Primary status | Review note |
| --- | --- | --- | --- |
| Basketball | TIER_A | PROPOSED_PRIMARY | Multiple green-uniform players repeatedly inside search; refined 375-435 |
| Bird1 | TIER_A | PROPOSED_PRIMARY | Multiple similar black birds; refined 180-230 |
| Bird2 | TIER_C | NOT_PROPOSED_TIER_C | Different-color animated bird characters; all 99 frames reviewed |
| BlurCar1 | TIER_C | NOT_PROPOSED_TIER_C | Persistent truck dissimilar to target van; pale vehicles only marginal |
| BlurCar2 | TIER_A | PROPOSED_PRIMARY | Comparable rear-view sedans in dense traffic; refined 390-450 |
| BlurCar3 | TIER_C | NOT_PROPOSED_TIER_C | Nearby SUV and traffic not a close target match |
| BlurCar4 | TIER_A | PROPOSED_PRIMARY | Dark SUV or pickup lookalikes at comparable scale; refined 230-290 |
| Board | TIER_B | PROPOSED_PRIMARY | Flat PCB below rotating target; physical independence remains ambiguous |
| Bolt | TIER_A | PROPOSED_PRIMARY | Same-scale sprinters continuously nearby; refined 1-60 |
| Bolt2 | TIER_A | NOT_PROPOSED_REDUNDANCY | Dense runner pack credible but withheld to limit same-event redundancy |
| Car1 | TIER_C | NOT_PROPOSED_TIER_C | Neighboring vehicles usually separated and distinguishable |
| Car2 | REJECT | NOT_PROPOSED_NO_CREDIBLE_EVENT | Crane truck and late dark car are not sufficiently similar |
| Car24 | TIER_A | PROPOSED_PRIMARY | Repeated same-scale highway vehicles; refined 620-700 |
| Car4 | TIER_B | NOT_PROPOSED_REDUNDANCY | Early adjacent light sedan plausible but vehicle coverage already met |
| CarDark | TIER_B | NOT_PROPOSED_REDUNDANCY | Night rear-light silhouettes plausible but less visually resolved |
| Coupon | TIER_A | NOT_PROPOSED_PRINTED_CAVEAT | Near-duplicate printed coupon sheets; withheld under depicted/printed-lookalike caution |
| Crowds | TIER_A | PROPOSED_PRIMARY | Overhead same-class pedestrians; refined 1-60 |
| Football | TIER_A | PROPOSED_PRIMARY | Near-identical helmets throughout dense play; refined 130-190 |
| Football1 | TIER_A | PROPOSED_PRIMARY | All 74 frames show close helmet/head competitors |
| Freeman3 | TIER_B | NOT_PROPOSED_REDUNDANCY | Classroom faces plausible with scale differences |
| Freeman4 | TIER_B | NOT_PROPOSED_REDUNDANCY | Many faces and intermittent occlusion; not needed for coverage |
| Girl | TIER_A | NOT_PROPOSED_REDUNDANCY | Second head overlaps around 417-458; face coverage already sufficient |
| Girl2 | TIER_B | NOT_PROPOSED_REDUNDANCY | Children and pedestrians intermittently near target |
| Human2 | REJECT | NOT_PROPOSED_NO_CREDIBLE_EVENT | Only smaller or seated background occupants |
| Human3 | TIER_B | NOT_PROPOSED_REDUNDANCY | Crossing pedestrians early and late; person coverage already met |
| Human4_2 | TIER_B | NOT_PROPOSED_REDUNDANCY | Adjacent pedestrian intervals credible but not needed |
| Human6 | REJECT | NOT_PROPOSED_NO_CREDIBLE_EVENT | Target visually isolated; vehicles are different class |
| Ironman | TIER_A | NOT_PROPOSED_REDUNDANCY | Similar armored humanoids credible; withheld to balance real-world superclass examples |
| Jogging_1 | TIER_A | NOT_PROPOSED_REDUNDANCY | Continuous paired jogger event; person coverage already met |
| Jogging_2 | TIER_A | NOT_PROPOSED_REDUNDANCY | Same paired-jogger source with alternate target; withheld for sequence-event redundancy |
| Lemming | REJECT | NOT_PROPOSED_NO_CREDIBLE_EVENT | Orange hanging target visually unique among props |
| Liquor | TIER_A | PROPOSED_PRIMARY | Multiple similar bottles repeatedly beside target; refined 540-620 |
| Matrix | TIER_A | NOT_PROPOSED_SEARCH_CONTEXT | Opponent continuous but centered outside nominal search at refined core |
| Shaking | TIER_B | NOT_PROPOSED_REDUNDANCY | Nearby performers plausible but hairstyles remain distinguishable |
| Singer1 | TIER_B | NOT_PROPOSED_REDUNDANCY | Second singer similar scale but clothing strongly differs |
| Singer2 | REJECT | NOT_PROPOSED_NO_CREDIBLE_EVENT | Foreground singer isolated; band and audience too distant |
| Skating1 | TIER_A | NOT_PROPOSED_REDUNDANCY | Crowded similar skaters credible; withheld after coverage met |
| Skating2_1 | TIER_B | NOT_PROPOSED_REDUNDANCY | Partner overlaps target but costume and appearance differ |
| Skating2_2 | TIER_B | NOT_PROPOSED_REDUNDANCY | Partner overlaps target but costume and appearance differ |
| Soccer | TIER_A | PROPOSED_PRIMARY | Similar-scale teammate faces in heavy crowd clutter; refined 160-240 |
| Subway | TIER_A | NOT_PROPOSED_REDUNDANCY | Comparable pedestrians cross near target; person coverage already met |
| Suv | TIER_B | NOT_PROPOSED_REDUNDANCY | Early adjacent SUV plausible but weaker than selected vehicle intervals |
| Walking | TIER_C | NOT_PROPOSED_TIER_C | Second pedestrian remains separated and distinguishable |
| Walking2 | TIER_B | NOT_PROPOSED_REDUNDANCY | Corridor pedestrian plausible with perspective-scale difference |

## 5. Tier A/B/C counts

- proposed Tier A: **6**
- proposed Tier B: **6**
- proposed Tier C: **0**
- Tier C/rejected/ambiguous coarse leads were retained only in the review table and do not satisfy primary coverage.

## 6. Distractor interval proposal summary

| ID | Sequence | Frames | Tier | Search | Split |
| --- | --- | --- | --- | --- | --- |
| R1-P01 | Basketball | 397-435 | TIER_A | INSIDE_NOMINAL_SEARCH | DISCOVERY_CANDIDATE |
| R1-P02 | Bolt | 31-49 | TIER_B | INSIDE_NOMINAL_SEARCH | DISCOVERY_CANDIDATE |
| R1-P03 | Crowds | 33-37 | TIER_B | INSIDE_NOMINAL_SEARCH | HOLDOUT_CANDIDATE |
| R1-P04 | BlurCar2 | 420-440 | TIER_B | INSIDE_NOMINAL_SEARCH | DISCOVERY_CANDIDATE |
| R1-P05 | BlurCar4 | 255-279 | TIER_A | INSIDE_NOMINAL_SEARCH | HOLDOUT_CANDIDATE |
| R1-P06 | Car24 | 640-678 | TIER_B | NEAR_SEARCH_BOUNDARY | HOLDOUT_CANDIDATE |
| R1-P07 | Bird1 | 194-198 | TIER_A | NEAR_SEARCH_BOUNDARY | DISCOVERY_CANDIDATE |
| R1-P08 | Board | 493-511 | TIER_B | INSIDE_NOMINAL_SEARCH | DISCOVERY_CANDIDATE |
| R1-P09 | Liquor | 565-589 | TIER_A | INSIDE_NOMINAL_SEARCH | DISCOVERY_CANDIDATE |
| R1-P10 | Football | 130-154 | TIER_A | INSIDE_NOMINAL_SEARCH | DISCOVERY_CANDIDATE |
| R1-P11 | Football1 | 26-50 | TIER_B | INSIDE_NOMINAL_SEARCH | HOLDOUT_CANDIDATE |
| R1-P12 | Soccer | 170-180 | TIER_A | NEAR_SEARCH_BOUNDARY | HOLDOUT_CANDIDATE |

## 7. Control proposal summary

Every primary proposal has one visually rescanned control selected without tracker behavior. GT-derived area, center-motion, and scale summaries are in the control CSV.

| Control | Linked | Sequence | Frames | Same sequence |
| --- | --- | --- | --- | --- |
| R1-C01 | R1-P01 | Gym | 20-40 | false |
| R1-C02 | R1-P02 | Gym | 300-320 | false |
| R1-C03 | R1-P03 | Skiing | 20-27 | false |
| R1-C04 | R1-P04 | CarScale | 20-40 | false |
| R1-C05 | R1-P05 | CarScale | 100-120 | false |
| R1-C06 | R1-P06 | CarScale | 200-220 | false |
| R1-C07 | R1-P07 | Dog1 | 20-40 | false |
| R1-C08 | R1-P08 | Toy | 100-120 | false |
| R1-C09 | R1-P09 | Liquor | 20-40 | true |
| R1-C10 | R1-P10 | Biker | 30-50 | false |
| R1-C11 | R1-P11 | Surfer | 150-170 | false |
| R1-C12 | R1-P12 | Jumping | 120-140 | false |

## 8. Superclass diversity

- unique primary sequences: **12**
- broad superclasses: **5** — ANIMAL=1, FACE_HEAD=3, OBJECT_OTHER=2, PERSON=3, VEHICLE=3
- maximum superclass share: **25.0%**

## 9. Proposed discovery/hold-out candidate split

- discovery candidates (7): Basketball, Bird1, BlurCar2, Board, Bolt, Football, Liquor
- hold-out candidates (5): BlurCar4, Car24, Crowds, Football1, Soccer
- intersection: empty
- status: `SEQUENCE_DISJOINT_PASS`

This is a provisional candidate grouping, not the frozen Manager split.

## 10. Contact-sheet coverage and payload size

- proposal sheets: 12
- control sheets: 12
- total sheets: **24**
- total bytes: **2840818** (2.71 MiB)
- dimensions: 1700 x 300 pixels each
- overlays: source JPG + GT target (green) + GT-derived nominal search context (blue); proposal midpoint manual distractor box (red)
- forbidden overlays: none

## 11. Ambiguous/rejected cases

- `Matrix` passed visual continuity but was withheld from primary coverage because the similar opponent remained centered outside the nominal blue search region.
- `Board` remains a provisional Tier B proposal; source-only imagery cannot prove that the flat PCB is physically independent from the raised assembly, so Manager visual review may reject it.
- `Bird2`, `BlurCar1`, `BlurCar3`, `Car1`, and `Walking` were not counted because only Tier C/weak evidence remained after fresh review.
- `Car2`, `Human2`, `Human6`, `Lemming`, and `Singer2` were rejected for lack of a credible continuous similar distractor.
- `Dog 20-40` and the late portion of `Skiing 20-40` were rejected as controls after frame-by-frame review revealed additional similar non-targets. They do not appear in the control CSV.
- Additional strong coarse leads were not promoted where the 12-sequence package already met diversity and payload constraints; this is not a tracker-based ranking.

## 12. Exact remaining coverage gaps

No proposal-level minimum is missing: at least 10 unique sequences, at least 3 superclasses, 6+ discovery candidates, 4+ hold-out candidates, one control per primary proposal, and sequence disjointness all pass. Remaining work is Manager visual review and possible bound/control adjustment. No interval, tier, or split is frozen.

## 13. Files produced

- `screening/codex/2026-08-26_stage4A_S1_R1_quarantine_filter.csv`
- `screening/codex/2026-08-26_stage4A_S1_R1_distractor_interval_proposals.csv`
- `screening/codex/2026-08-26_stage4A_S1_R1_control_interval_proposals.csv`
- `screening/codex/2026-08-26_stage4A_S1_R1_contact_sheet_manifest.csv`
- `screening/codex/2026-08-26_stage4A_S1_R1_slice_proposal_report.md`
- `screening/codex/2026-08-26_stage4A_S1_R1_command_log.txt`
- `screening/codex/artifacts/stage4A_S1_R1/contact_sheets/` (24 JPEGs)
- `screening/codex/scripts/2026-08-26_stage4A_S1_R1_build_proposals.py`

## 14. Readiness conclusion

`S1_R1_COMPLETE_READY_FOR_MANAGER_VISUAL_REVIEW`

FROZEN DIAGNOSTIC SLICE: **NOT CREATED**  
STAGE 4B: **LOCKED**  
DIAG PASS/FAIL: **NOT ASSIGNED**  
S1-S7: **NOT STARTED**  
PRIMARY SHORTLIST: **NONE**  
MAIN BASELINE: **NONE**  
PROPOSED ARCHITECTURE: **NONE**
