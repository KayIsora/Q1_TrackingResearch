# Stage 4A-S1-R1 — Manager visual review and rework decision

**Date:** 2026-08-26  
**Status:** `S1_R1_REWORK_REQUIRED`  
**Source commit reviewed:** `16852b1055a45b6b9cb0e6ede6b7fc84fc79ba61`

## Boundary

This review inspects the R1 proposal tables and all 24 source-only contact sheets. It does not run SpikeTrack, inspect tracker outcomes, freeze the diagnostic slice, start Stage 4B, assign `DIAG_PASS`/`DIAG_FAIL`, assign S1-S7, select a baseline, or approve an architecture.

For visual access, Manager exported the exact review package from the source commit through a temporary non-main GitHub Actions branch. Artifact ID `9579099366` had digest `sha256:df42b98f38d3a8f146a916ce39b5a77ea11c19809398593b127b6f1caec79d27`. The image hashes and sizes were checked against `2026-08-26_stage4A_S1_R1_contact_sheet_manifest.csv`. This export changed no scientific artifact on `main`.

## 1. Process acceptance

The clean-room process is accepted:

- quarantine filter was created before frame access;
- Deer, Crossing and Couple frames were not opened;
- all 44 non-quarantined candidate leads were rescanned from zero;
- no tracker outcome or MRM evidence was accessed;
- the provisional discovery/hold-out candidate groups were sequence-disjoint;
- all contact sheets used only source frames, GT, nominal search context and manual distractor review boxes.

The R1 package is therefore scientifically usable as a proposal package. It is not yet acceptable as a frozen slice because two primary proposals are invalid/too weak and most controls are not sufficiently matched or independently distributed.

## 2. Proposal-level visual decisions

| ID | Sequence | R1 tier | Manager decision | Manager rationale |
|---|---|---:|---|---|
| R1-P01 | Basketball | TIER_A | **ACCEPT PRIMARY — TIER_A** | Multiple same-team green-uniform players co-occur at comparable scale inside the nominal search region. |
| R1-P02 | Bolt | TIER_B | **ACCEPT PRIMARY — TIER_B** | Adjacent sprinter is a credible same-class distractor, but kit/color differences justify Tier B. |
| R1-P03 | Crowds | TIER_B | **ACCEPT PRIMARY — TIER_B, BOUNDS TO RECHECK** | A nearby pedestrian is clearly inside the search context, but the five-frame minimum and tiny target make the interval fragile; R2 must confirm continuous visibility and bounds. |
| R1-P04 | BlurCar2 | TIER_B | **ACCEPT PRIMARY — TIER_B** | Nearby rear-view sedan is a credible road-scale lookalike inside the search region. |
| R1-P05 | BlurCar4 | TIER_A | **ACCEPT PRIMARY — TIER_A** | Parallel dark SUV/pickup is highly similar in silhouette and scale and remains inside the search context. |
| R1-P06 | Car24 | TIER_B | **REJECT PRIMARY — WEAK VISUAL SIMILARITY / BOUNDARY** | The white utility vehicle differs materially in color and body type from the target and sits near the search boundary; same road role alone is insufficient. Keep only as contextual reference. |
| R1-P07 | Bird1 | TIER_A | **ACCEPT PRIMARY — TIER_A** | A separate black bird with comparable silhouette/scale crosses near the nominal search boundary for the full five-frame core. |
| R1-P08 | Board | TIER_B | **REJECT PRIMARY — NON-TARGET INDEPENDENCE UNRESOLVED** | The flat PCB may be physically connected to the tracked assembly. The slice requires a genuine non-target distractor; source imagery cannot establish that here. |
| R1-P09 | Liquor | TIER_A | **ACCEPT PRIMARY — TIER_A** | A distinct, similarly sized upright bottle co-occurs beside the target; the same-sequence clean control is strong. |
| R1-P10 | Football | TIER_A | **ACCEPT PRIMARY — TIER_A** | Multiple highly similar football helmets surround the target inside the nominal search region. |
| R1-P11 | Football1 | TIER_B | **ACCEPT PRIMARY — TIER_B** | Adjacent helmet/head is comparable in scale and role but has distinguishable opponent colors. |
| R1-P12 | Soccer | TIER_A | **ACCEPT PRIMARY — DOWNGRADE TO TIER_B** | The nearby teammate face is credible but lies near/beyond the nominal search boundary and is visible amid heavy crowd/confetti clutter. This is strong Tier B rather than Tier A. |

## 3. Locked candidate set for control rework

Ten candidate intervals survive visual review.

### Discovery candidates — six sequences

1. R1-P01 — Basketball
2. R1-P02 — Bolt
3. R1-P04 — BlurCar2
4. R1-P07 — Bird1
5. R1-P09 — Liquor
6. R1-P10 — Football

### Hold-out candidates — four additional sequences

1. R1-P03 — Crowds
2. R1-P05 — BlurCar4
3. R1-P11 — Football1
4. R1-P12 — Soccer

This selection remains provisional until matched controls are approved and the Manager writes the final frozen slice. It already satisfies the minimum six/four sequence-disjoint candidate structure and retains five broad superclasses across the full set.

R1-P06 and R1-P08 must not return as primary intervals during R2 unless Manager explicitly reopens them after new source-only evidence. They do not count toward coverage.

## 4. Control-level visual review

Only R1-C09 is accepted without rework.

| Control | Linked proposal | Manager state | Reason |
|---|---|---|---|
| R1-C01 Gym 20-40 | P01 Basketball | **REMATCH / QUANTIFY** | Isolated athlete is usable in class terms, but scene, apparent target scale and motion differ substantially from basketball play. |
| R1-C02 Gym 300-320 | P02 Bolt | **REMATCH** | Gymnast pose/motion and scene are weak matches for sprinting. |
| R1-C03 Skiing 20-27 | P03 Crowds | **REMATCH** | Fast airborne skier is a poor motion/viewpoint match for a slow overhead pedestrian interval. |
| R1-C04 CarScale 20-40 | P04 BlurCar2 | **REMATCH** | Isolated side-view car is much smaller and visually/domain-wise different from urban rear-view traffic. |
| R1-C05 CarScale 100-120 | P05 BlurCar4 | **REMATCH** | Scale/viewpoint/domain mismatch remains large. |
| R1-C06 CarScale 200-220 | rejected P06 | **DROP** | Linked primary is rejected. |
| R1-C07 Dog1 20-40 | P07 Bird1 | **REJECT / REMATCH** | Plush dog is not a biologically or visually comparable control for a flying bird. Broad `ANIMAL` alone is insufficient. |
| R1-C08 Toy 100-120 | rejected P08 | **DROP** | Linked primary is rejected. |
| R1-C09 Liquor 20-40 | P09 Liquor | **ACCEPT PREFERRED CONTROL** | Same sequence, same target/scene and no similar bottle; this is the strongest matched control. |
| R1-C10 Biker 30-50 | P10 Football | **HOLD / SEARCH BETTER** | Broad head-scale control is plausible, but helmet/scrum context and motion differ. Retain only if no quantitatively better clean control exists. |
| R1-C11 Surfer 150-170 | P11 Football1 | **REMATCH** | Surfing upper-body/head motion and appearance are weak matches for a helmeted football scrum. |
| R1-C12 Jumping 120-140 | P12 Soccer | **HOLD / SEARCH BETTER** | Isolated face is plausible, but target scale, color domain, motion and clutter differ. Retain only if pair metrics pass and no better control exists. |

## 5. Structural control problems requiring correction

### 5.1 Proposal-side matching metrics are missing

The control CSV reports target-area, GT-motion and scale-change summaries for controls, but the proposal CSV does not report the same numeric summaries. Manager therefore cannot audit pair quality quantitatively.

R2 must add the same metrics to every surviving proposal and create a pair-level matching table.

### 5.2 Control-sequence reuse crosses the provisional split

`CarScale` currently supplies controls for both a discovery candidate and hold-out candidates. A control sequence must not appear in both candidate groups. All source sequences used by a pair—including controls—must remain split-disjoint.

### 5.3 Effective independent control count is too low

Twelve controls use fewer independent source sequences because Gym and CarScale are reused. After rejecting P06/P08, control reuse should be minimized. No control sequence may support more than two primaries, and a control sequence may not cross discovery/hold-out.

### 5.4 Broad-superclass matching alone is insufficient

For Bird1 in particular, an animate/visual class-compatible control is required. Plush, printed or depicted objects cannot stand in for a real moving animal when testing a distractor effect.

## 6. R2 matching boundary — locked before rework

For each surviving proposal, R2 must prefer a same-sequence clean interval. If unavailable, select a non-quarantined cross-sequence control using source/GT only.

The pair-level table must include proposal and control values plus deltas for:

- interval length;
- median target-area ratio;
- p90 GT center motion normalized by target scale;
- end-to-start area ratio;
- max-to-min area ratio;
- median absolute log scale step;
- target visibility/occlusion category;
- fast-motion flag;
- low-resolution flag;
- object class and broad superclass;
- official-attribute overlap;
- same-sequence/cross-sequence status;
- discovery/hold-out group.

### Quantitative acceptance targets

Unless a same-sequence control is used, a proposed control should satisfy:

1. interval length equal to the linked proposal where possible, otherwise within `±2` frames;
2. median target-area ratio within a factor of `2`;
3. normalized p90 motion within a factor of `2`; when both are below `0.03`, absolute difference `<=0.03` is acceptable;
4. max-to-min area ratio within a factor of `2`;
5. no full-occlusion mismatch; partial/no-occlusion difference must be disclosed;
6. same broad superclass, with stricter visual/subtype compatibility for `ANIMAL` and `FACE_HEAD`;
7. no similar distractor during the full control interval;
8. no control sequence used across discovery and hold-out;
9. no control sequence linked to more than two primaries.

A control failing a target may be retained only as `EXCEPTION_PENDING_MANAGER` with an explicit reason and no better source-only alternative found.

## 7. Decision

**R1 proposal process:** ACCEPTED  
**R1 proposal content:** PARTIALLY ACCEPTED  
**Frozen diagnostic slice:** NOT CREATED  
**Next task:** `Stage 4A-S1-R2 — proposal corrections and control rematching`  
**Stage 4B:** LOCKED

## Locked state

- accepted candidate proposals: 10
- rejected candidate proposals: R1-P06, R1-P08
- tier correction: R1-P12 -> TIER_B
- current controls accepted without rework: R1-C09 only
- Stage 4A-S1-R2: READY
- Manager final visual/control review: PENDING
- frozen slice: NOT CREATED
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1-S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
