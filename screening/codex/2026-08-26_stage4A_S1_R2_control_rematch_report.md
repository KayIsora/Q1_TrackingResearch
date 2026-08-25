# Stage 4A-S1-R2 — Source-only proposal correction and control rematch report

**Date:** 2026-08-26  
**Status:** `S1_R2_COMPLETE_READY_FOR_MANAGER_FINAL_SLICE_REVIEW`  
**Decision scope:** revised proposals, preferred controls, metrics and pair sheets remain provisional with `manager_review_status=PENDING_R2_REVIEW`.

## 1. Outcome-independence declaration

This R2 lane used only the accepted v2 clean room, canonical OTB source JPGs and GT, the Manager R1 review/protocol, and the accepted source-only R1 proposal evidence. SpikeTrack was not run; no model or checkpoint was instantiated; no prediction, AUC, IoU, success/failure outcome, score/confidence map, divergence evidence, MRM log, ablation or tracker-derived ranking was accessed. Outcome evidence accessed: **NONE**.

## 2. Canonical source and quarantine

- canonical OTB root: `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015`
- accepted clean room: `F:\Q1_TrackingResearch_Data\Stage4A_S1_Cleanroom_2026-08-26_v2`
- quarantine: `Deer`, `Crossing`, `Couple`
- quarantine enforcement: all three remained excluded from proposal scanning, control scanning, matching, group accounting and coverage; their source frames were not opened.

## 3. R1 accepted/rejected proposal traceability

- retained exactly 10 Manager-accepted primaries: `R1-P01, R1-P02, R1-P03, R1-P04, R1-P05, R1-P07, R1-P09, R1-P10, R1-P11, R1-P12`
- rejected primaries: `R1-P06 Car24`, `R1-P08 Board`
- P06/P08 do not occur in the revised primary/control/audit tables and contribute no coverage or control generation.

## 4. P03 bounds decision

`R1-P03 Crowds 33-37`: **BOUNDS_CONFIRMED**. Source-only frame-by-frame review shows the same light-top adult immediately lower-left of the target in all five frames. The GT target stays visible; the distractor event stays inside the nominal search context. Frames 32 and 38 were not added because the accepted five-frame core is the least ambiguous continuous event.

## 5. P12 tier correction

`R1-P12 Soccer`: corrected from R1 Tier A to **TIER_B**. Tier A was not restored. Across frames 170-180, source-only full-frame review shows non-target real faces near/beyond the blue prior-GT crop boundary; no second face was clearly interior in the factor-4 crop render. This observation preserves the locked `NEAR_SEARCH_BOUNDARY` status and does not reclassify or reject P12.

## 6. Proposal-side GT metric summary

Exact formulas:

- rectangular GT area is `w*h`; polygon GT is converted to its enclosing axis-aligned box before the same calculation;
- target-area ratio is `(w*h)/(image_width*image_height)`;
- center is `(x+w/2, y+h/2)` and per-step pixel displacement is Euclidean center distance;
- normalized motion at step `i` is `distance(center[i-1], center[i]) / max(1, sqrt(area[i-1]))`;
- p90 uses linear interpolation at position `0.9*(n-1)` in the sorted per-step values;
- end/start area ratio is `area[last]/area[first]`;
- max/min area ratio is `max(area)/min(area)`;
- median absolute log-area step is `median(abs(log(area[i]/area[i-1])))`;
- `fast_motion_flag=true` iff normalized p90 motion is greater than `1.0`;
- `low_resolution_flag=true` iff median target-area ratio is below `0.001`.

| ID | Sequence | Frames | Tier | Median area | p90 norm motion | Max/min area | Occ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1-P01 | Basketball | 397-435 | TIER_A | 0.011068 | 0.070960 | 1.000 | NONE |
| R1-P02 | Bolt | 31-49 | TIER_B | 0.006884 | 0.061903 | 1.000 | NONE |
| R1-P03 | Crowds | 33-37 | TIER_B | 0.003896 | 0.124516 | 1.000 | PARTIAL |
| R1-P04 | BlurCar2 | 420-440 | TIER_B | 0.027829 | 0.495366 | 1.439 | NONE |
| R1-P05 | BlurCar4 | 255-279 | TIER_A | 0.069863 | 0.228103 | 1.292 | NONE |
| R1-P07 | Bird1 | 194-198 | TIER_A | 0.003983 | 0.082675 | 1.000 | PARTIAL |
| R1-P09 | Liquor | 565-589 | TIER_A | 0.049902 | 0.000000 | 1.000 | NONE |
| R1-P10 | Football | 130-154 | TIER_A | 0.007171 | 0.140517 | 1.291 | PARTIAL |
| R1-P11 | Football1 | 26-50 | TIER_B | 0.012301 | 0.212389 | 1.346 | PARTIAL |
| R1-P12 | Soccer | 170-180 | TIER_B | 0.019913 | 0.101066 | 1.163 | PARTIAL |

All values above are GT-derived; no tracker output enters any formula.

## 7. Control search coverage

Search order was same sequence, non-quarantined same class, compatible subtype in the same broad superclass, then declared weaker alternatives. Every preferred interval was visually reviewed frame by frame.

| Proposal | Same-sequence result | Other source-only sequences checked | Preferred | Rejected/alternate result |
| --- | --- | --- | --- | --- |
| R1-P01 | Basketball: similar players persist | David3; Human5; Woman | David3 195-233 | Human5/Woman weaker scene or cleanliness leads |
| R1-P02 | Bolt: adjacent runners persist | Human8; David3; Gym | Human8 108-126 | Gym area mismatch; David3 reserved for P01 |
| R1-P03 | Crowds 161-165 clean in nominal target context | Crowds; Human3; Skiing; Human6; Human5 | Crowds 161-165 | Human6/Human5 have nearby second pedestrians; Human3 464-468 is a valid alternate |
| R1-P04 | BlurCar2 330-360: comparable SUV persists | BlurCar1; BlurCar3; CarScale | CarScale 143-163 (exception) | CarScale motion fails; BlurCar3/BlurCar1 quantitative leads fail no-distractor |
| R1-P05 | BlurCar4 210-230: adjacent traffic persists | Suv; CarScale; Car4 | Suv 726-750 | Suv 651-675 passes metrics but has partial pole/tree occlusion |
| R1-P07 | Bird1: visible-target windows retain other birds; 140-144 target unresolved | Bird1; Bird2; Panda; Dog; Dog1 | Panda 426-430 (exception) | Bird2 fails area/cleanliness; Dog is bird-to-dog exception; Dog1 is plush and invalid |
| R1-P09 | Liquor 20-40 clean and revalidated | Liquor; Coke; ClifBar | Liquor 20-40 | Cross-sequence objects are weaker than exact same-sequence control |
| R1-P10 | Football: helmets/heads persist | Biker; Ironman; Freeman1 | Biker 41-65 (exception) | Biker is novelty mask/headgear; Ironman has extra armored heads; Freeman1 is bare face |
| R1-P11 | Football1: no clean interval in 1-74 | Surfer; Ironman; Biker; Jumping | Surfer 304-328 | Ironman not clean; Biker would cross split; bare-head exception retained |
| R1-P12 | Soccer: comparable faces persist | Man; David; Freeman1; Jumping | Man 106-116 | David 180-190 lies before canonical evaluator startFrame=300 and is invalid |

## 8. Preferred control per primary

| Proposal | Control | Sequence | Frames | Same seq | State |
| --- | --- | --- | --- | --- | --- |
| R1-P01 | R2-C01 | David3 | 195-233 | false | MATCH_PASS |
| R1-P02 | R2-C02 | Human8 | 108-126 | false | MATCH_PASS |
| R1-P03 | R2-C03 | Crowds | 161-165 | true | MATCH_PASS |
| R1-P04 | R2-C04 | CarScale | 143-163 | false | EXCEPTION_PENDING_MANAGER |
| R1-P05 | R2-C05 | Suv | 726-750 | false | MATCH_PASS |
| R1-P07 | R2-C07 | Panda | 426-430 | false | EXCEPTION_PENDING_MANAGER |
| R1-P09 | R2-C09 | Liquor | 20-40 | true | MATCH_PASS |
| R1-P10 | R2-C10 | Biker | 41-65 | false | EXCEPTION_PENDING_MANAGER |
| R1-P11 | R2-C11 | Surfer | 304-328 | false | EXCEPTION_PENDING_MANAGER |
| R1-P12 | R2-C12 | Man | 106-116 | false | MATCH_PASS |

## 9. Rejected/alternate controls per primary

The final column of Section 7 records the strongest rejected or alternate search result for every primary. Important rejections were: unresolved/contaminated same-sequence bird windows, `Bird2 22-26` for area plus animated distractors, and plush `Dog1`; traffic-filled same-sequence windows for BlurCar2/BlurCar4; `Ironman` helmet leads containing a second armored figure; `Human6 110-114` and `Human5 234-238` containing nearby second pedestrians; and raw `David 180-190`, which lies before canonical evaluator `startFrame=300`.

## 10. Pair matching audit results

| Proposal | Control | Len | Area | Motion | Scale | Subtype | No distractor | State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R1-P01 | R2-C01 | true | true | true | true | true | true | MATCH_PASS |
| R1-P02 | R2-C02 | true | true | true | true | true | true | MATCH_PASS |
| R1-P03 | R2-C03 | true | true | true | true | true | true | MATCH_PASS |
| R1-P04 | R2-C04 | true | true | false | true | true | true | EXCEPTION_PENDING_MANAGER |
| R1-P05 | R2-C05 | true | true | true | true | true | true | MATCH_PASS |
| R1-P07 | R2-C07 | true | true | true | true | false | true | EXCEPTION_PENDING_MANAGER |
| R1-P09 | R2-C09 | true | true | true | true | true | true | MATCH_PASS |
| R1-P10 | R2-C10 | true | true | true | true | false | true | EXCEPTION_PENDING_MANAGER |
| R1-P11 | R2-C11 | true | true | true | true | false | true | EXCEPTION_PENDING_MANAGER |
| R1-P12 | R2-C12 | true | true | true | true | true | true | MATCH_PASS |

- `MATCH_PASS`: **6**
- `EXCEPTION_PENDING_MANAGER`: **4**
- `MATCH_FAIL`: **0**

Same-sequence controls retain recorded metrics but are exempt from cross-sequence numeric gates. Fast-motion and low-resolution flag agreement is reported in the audit CSV but is not an additional locked gate.

## 11. Discovery/hold-out full-sequence disjoint validation

- DISCOVERY full sequence set (11): `Basketball, Biker, Bird1, BlurCar2, Bolt, CarScale, David3, Football, Human8, Liquor, Panda`
- HOLDOUT full sequence set (7): `BlurCar4, Crowds, Football1, Man, Soccer, Surfer, Suv`
- intersection: `NONE`
- status: `SEQUENCE_DISJOINT_PASS`

These sets include both primary and control sequences.

## 12. Control reuse validation

- control-sequence reuse counts: `Biker=1, CarScale=1, Crowds=1, David3=1, Human8=1, Liquor=1, Man=1, Panda=1, Surfer=1, Suv=1`
- maximum reuse: **1**
- permitted maximum: 2
- status: `CONTROL_REUSE_PASS`

## 13. Exceptions and failed targets

- `R1-P04 + R2-C04`: `EXCEPTION_PENDING_MANAGER`. `CarScale 143-163` is clean for the complete interval and passes length, median area, scale dynamics, broad superclass/subtype, split and reuse checks; partial foreground branches are disclosed and never fully occlude the target. Normalized p90 motion fails at factor `9.870092` (required `<=2`). `BlurCar3 216-236` passes all quantitative targets and exact sedan subtype but contains a large adjacent SUV plus another car throughout; `BlurCar1 773-793` likewise contains a large adjacent truck in every frame. The clean control was preferred over quantitatively matched but distractor-contaminated alternatives.
- `R1-P07 + R2-C07`: `EXCEPTION_PENDING_MANAGER`. The live panda control satisfies the explicit real-animate-animal rule and all quantitative, split, reuse and no-similar-panda checks, but bird-to-panda is not a compatible visual subtype, so `visual_subtype_match=false`. Exhaustive Bird1 review found other birds in visible-target five-frame windows; frames 140-144 were rejected because the target is effectively unresolved. Bird2 fails area/cleanliness, Dog is another cross-subtype fallback, and plush Dog1 is prohibited.
- `R1-P10 + R2-C10`: `EXCEPTION_PENDING_MANAGER`. All quantitative, broad-superclass, split, reuse and no-distractor checks pass. The closest clean discovery control is a novelty bird/chicken mask or rider headgear, not a football helmet, so `visual_subtype_match=false`. Football has no clean same-sequence interval; `Ironman` contains additional armored/helmeted heads; `Freeman1 24-48` is quantitatively viable but is an isolated bare face.
- `R1-P11 + R2-C11`: `EXCEPTION_PENDING_MANAGER`. Length, area, normalized p90 motion, scale dynamics, broad superclass and no-distractor checks pass, but the control is a bare real head rather than a helmeted/equipped head. Same-sequence Football1 is not clean; two quantitatively viable Ironman intervals contain a second armored/helmeted figure; Biker is the discovery control for P10 and cannot cross the split. This is the best clean source-only hold-out control found.
- partial-versus-no-occlusion differences are explicitly disclosed in the pair audit; no pair has a full-occlusion mismatch.

## 14. Pair-sheet package

| Pair | Proposal | Control | Bytes | Path |
| --- | --- | --- | --- | --- |
| PAIR-R1-P01 | R1-P01 | R2-C01 | 282944 | screening/codex/artifacts/stage4A_S1_R2/pair_sheets/R2_PAIR_P01.jpg |
| PAIR-R1-P02 | R1-P02 | R2-C02 | 237962 | screening/codex/artifacts/stage4A_S1_R2/pair_sheets/R2_PAIR_P02.jpg |
| PAIR-R1-P03 | R1-P03 | R2-C03 | 216649 | screening/codex/artifacts/stage4A_S1_R2/pair_sheets/R2_PAIR_P03.jpg |
| PAIR-R1-P04 | R1-P04 | R2-C04 | 205030 | screening/codex/artifacts/stage4A_S1_R2/pair_sheets/R2_PAIR_P04.jpg |
| PAIR-R1-P05 | R1-P05 | R2-C05 | 178604 | screening/codex/artifacts/stage4A_S1_R2/pair_sheets/R2_PAIR_P05.jpg |
| PAIR-R1-P07 | R1-P07 | R2-C07 | 232338 | screening/codex/artifacts/stage4A_S1_R2/pair_sheets/R2_PAIR_P07.jpg |
| PAIR-R1-P09 | R1-P09 | R2-C09 | 220476 | screening/codex/artifacts/stage4A_S1_R2/pair_sheets/R2_PAIR_P09.jpg |
| PAIR-R1-P10 | R1-P10 | R2-C10 | 241203 | screening/codex/artifacts/stage4A_S1_R2/pair_sheets/R2_PAIR_P10.jpg |
| PAIR-R1-P11 | R1-P11 | R2-C11 | 208835 | screening/codex/artifacts/stage4A_S1_R2/pair_sheets/R2_PAIR_P11.jpg |
| PAIR-R1-P12 | R1-P12 | R2-C12 | 200925 | screening/codex/artifacts/stage4A_S1_R2/pair_sheets/R2_PAIR_P12.jpg |

- pair-review sheets: **10**
- total bytes: **2224966** (2.12 MiB)
- payload cap: `<25 MiB` — `PASS`
- allowed overlays only: GT target green, nominal search region blue, proposal midpoint manual distractor red, IDs and GT metrics.

## 15. Remaining blockers

Manager final slice review remains required for the P04 motion exception, the P07 animal-subtype exception, and the P10/P11 FACE_HEAD subtype exceptions. R2 does not freeze a final slice and does not authorize downstream diagnostic work.

## 16. R2 conclusion

`S1_R2_COMPLETE_READY_FOR_MANAGER_FINAL_SLICE_REVIEW`

FROZEN DIAGNOSTIC SLICE: **NOT CREATED**  
STAGE 4B: **LOCKED**  
DIAG PASS/FAIL: **NOT ASSIGNED**  
S1-S7: **NOT STARTED**  
PRIMARY SHORTLIST: **NONE**  
MAIN BASELINE: **NONE**  
PROPOSED ARCHITECTURE: **NONE**
