# Stage 1 reconciliation report — Manager + Codex

**Date:** 2026-08-24  
**Status:** RECONCILIATION IN PROGRESS — candidate-universe union and early-gate reconciliation complete; canonical matrix population is intentionally deferred until source registration for the reconciled scientific-audit queue is complete.  
**Governing files:** `RULE/01_EVIDENCE_AND_CITATION_POLICY.md`, `docs/11_systematic_screening_protocol.md`, `screening/00_parallel_screening_coordination.md`.

## 1. Inputs

Independent Codex lane:

- `screening/codex/2026-08-24_stage1_query_log.md`
- `screening/codex/2026-08-24_stage1_candidate_universe.csv`
- `screening/codex/2026-08-24_stage1_discovery_report.md`
- Codex Stage-1 commit: `e8d318199424774c0e2000758496aac0e98ad579`

Manager lane:

- `screening/manager/2026-08-24_stage1_query_log.md`
- `screening/manager/2026-08-24_stage1_discovery_status.md`
- `screening/manager/2026-08-24_stage1_manager_additions.csv`

The Codex lane was completed and committed before its worker had access to manager-lane results, preserving the intended independent-discovery check.

## 2. Codex Stage-1 validation

The worker report and CSV are internally consistent:

- 149 retained raw occurrences;
- 124 method families after deduplication;
- Pool A/B/C = 64 / 43 / 17;
- HG1 PASS/FAIL/PENDING = 106 / 15 / 3;
- HG2 PASS/FAIL/PENDING = 71 / 37 / 16;
- HG3 PASS/FAIL/PENDING = 26 / 18 / 80;
- 19 families simultaneously PASS HG1/HG2/HG3;
- HG4/HG5/HG6 remain PENDING;
- no soft scoring, shortlist, baseline selection, or architecture decision was performed.

This satisfies the required Stage-1 stopping rule.

## 3. Manager-only additions found during reconciliation

Four manager-lane leads were not present as method families in the Codex 124-family universe and were independently rechecked against primary/official sources before addition:

| ID | Family | Early gates | Source status |
|---|---|---|---|
| CX125 | Efficient Motion Prompt Learning for Robust Visual Tracking (MPT) | HG1 PASS / HG2 PASS / HG3 PASS | [R13][R14] official ICML/PMLR publication plus official source/models/testing repository |
| CX126 | FocTrack: Focus attention for visual tracking | HG1 PASS / HG2 PASS / HG3 PENDING | [R15] official Pattern Recognition publication; full reproducibility bundle not yet verified |
| CX127 | DSTrack: Diffusion-based sequence learning for visual object tracking | HG1 PASS / HG2 PASS / HG3 PENDING | [R16] official Pattern Recognition publication; full reproducibility bundle not yet verified |
| CX128 | Motion Deep Association for spatio-temporal object tracking (MDATrack) | HG1 PASS / HG2 PASS / HG3 PENDING | [R17] official Pattern Recognition publication; full reproducibility bundle not yet verified |

A previous manager shorthand lead named `MoDTrack` was not added: reconciliation did not establish a primary source corresponding to a generic RGB bbox-SOT method under that name. It remains an unresolved lead rather than being converted into a candidate by assumption.

## 4. Reconciled universe counts

Union operation:

`Codex 124 families + 4 verified manager-only additions = 128 reconciled method families`.

No added manager family duplicates a Codex family under a different paper title according to the current title/method-family reconciliation.

Reconciled provisional counts:

| Item | PASS | FAIL | PENDING | Total |
|---|---:|---:|---:|---:|
| HG1 | 110 | 15 | 3 | 128 |
| HG2 | 75 | 37 | 16 | 128 |
| HG3 | 27 | 18 | 83 | 128 |
| HG4 | 0 | 0 | 128 | 128 |
| HG5 | 0 | 0 | 128 | 128 |
| HG6 | 0 | 0 | 128 | 128 |

Pool counts after reconciliation:

- Pool A: 68
- Pool B: 43
- Pool C: 17
- Total: 128

These are discovery/early-gate counts, not rankings.

## 5. Reconciled scientific-audit queue — NOT A SHORTLIST

After adding MPT, **20 families** currently PASS HG1/HG2/HG3 and may proceed to deeper evidence preparation. The queue is unranked:

1. SpikeTrack
2. UETrack
3. UTPTrack
4. FARTrack
5. GOT-Edit
6. GOT-JEPA
7. SAMURAI
8. DAM4SAM
9. SSTrack-AAAI — Decoupled Spatio-Temporal Consistency Learning
10. MCITrack
11. MambaLCT
12. SUTrack
13. AsymTrack
14. JDTrack
15. SPMTrack
16. UMDATrack
17. UncTrack
18. HiT-DyHiT
19. SiamABC
20. MPT — Efficient Motion Prompt Learning for Robust Visual Tracking

Queue membership means only that publication year/status, Core task fit, and reproducibility assets currently satisfy the early gates. It does **not** imply HG4/HG5/HG6 PASS, high soft score, shortlist status, or baseline preference.

## 6. Evidence-blocked candidates remain scientifically important

Methods such as MUTrack, STDTrack, DTPTrack, ARTrack-AC, ETCTrack, TGTrack, NASTrack, LoRATv2 and other HG3-PENDING/FAIL records remain in the reconciled literature universe as novelty/mechanism references. HG3 ineligibility does not permit ignoring them during later novelty audit.

## 7. Why the canonical matrix is not populated yet

`screening/candidate_screening_matrix.csv` remains untouched at this point.

The coordination protocol requires verified sources to be registered before externally verifiable scientific facts are promoted into the canonical matrix. The four manager additions have now been registered as [R13]–[R17]. The 19 Codex-origin families in the scientific-audit queue still need their primary publication and official reproducibility sources normalized into `references/references.md` and `references/source_manifest.csv` before canonicalization.

This is an evidence-discipline step, not a new screening stage.

## 8. Next mandatory action

Before HG4/HG5/HG6 deep audit or any S1–S7 score:

1. normalize/register the primary publication and official code/checkpoint/evaluator sources for the reconciled 20-family scientific-audit queue;
2. populate the canonical `screening/candidate_screening_matrix.csv` with early-gate evidence only;
3. freeze the reconciled Stage-1 universe/queue;
4. then begin HG4/HG5/HG6 deep audit under `docs/11_systematic_screening_protocol.md`.

No soft score may be assigned before that transition.

## 9. Current project state

- Stage 1 broad discovery: **COMPLETE in both lanes**
- Independent cross-check: **COMPLETE**
- Candidate-universe reconciliation: **COMPLETE — 128 families**
- Early HG1/HG2/HG3 reconciliation: **COMPLETE**
- Central source registration for audit queue: **IN PROGRESS**
- Canonical candidate matrix: **NOT YET POPULATED**
- HG4/HG5/HG6 deep audit: **NOT STARTED**
- Soft scoring: **NOT STARTED**
- Primary shortlist: **NONE**
- Main baseline: **NONE**
- Proposed architecture: **NONE**
