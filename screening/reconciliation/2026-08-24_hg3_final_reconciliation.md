# Final HG3 reconciliation — external blind cross-check

**Date:** 2026-08-24  
**Status:** HG3 RECONCILIATION CLOSED FOR THE SIX FLAGS; Stage 2 may activate only for candidates with HG1/HG2/HG3 = PASS.  
**Governing sources:** `RULE/01_EVIDENCE_AND_CITATION_POLICY.md`, `docs/00_claim_taxonomy.md`, `docs/11_systematic_screening_protocol.md`, Manager HG3 report, source-normalization report, and external blind Codex report `screening/codex/2026-08-24_hg3_flag_external_blind_recheck.md`.

## 1. External blind report validation

The external Codex worker reported commit `cd4febbc497ab84b2d285eccef9dbfdfc52e5f38`, push success, clean worktree, and preserved blindness. Its report inspected fresh detached checkouts at the pinned official repository refs and did not claim end-to-end reproduction.

The blind result was:

- SAMURAI — PASS
- DAM4SAM — PASS
- MambaLCT — FAIL
- JDTrack — PENDING
- UMDATrack — PENDING
- SiamABC — FAIL

The blind report is accepted as a valid independent evidence lane. It does not automatically override the Manager lane; disagreements are resolved below against the more specific official-source evidence.

## 2. Reconciliation principle

No majority vote is used. When the external blind lane introduced more specific repository evidence than the earlier Manager review, the final status follows the locked evidence rule:

- concrete contradictory code/resource evidence overrides a favorable assumption;
- missing checkpoint/resource mapping is `PENDING`, not PASS;
- a hard gate remains PASS only when the official release is sufficient for a realistic baseline-reproduction attempt.

## 3. Final six-flag decisions

| Candidate | Earlier Manager | External blind Codex | Final HG3 | Reconciliation rationale |
|---|---:|---:|---:|---|
| **SAMURAI (CX020)** | PASS | PASS | **PASS** | Agreement. Training-free method; official SAM 2.1 weights are the actual inference checkpoints and a generic bbox benchmark runner/result writer exists. |
| **DAM4SAM (CX024)** | PASS | PASS | **PASS** | Agreement. Training-free method; official SAM 2.1 weights plus GOT-10k/VOT benchmark paths are sufficient for a realistic attempt. |
| **MambaLCT (CX040)** | PASS | FAIL | **FAIL** | External blind audit found cumulative release defects not captured in the earlier Manager review: an unresolved top-level `from rope import *` import against only a sibling `rope.py`; released model files/epochs and checked-in config contracts do not align without undocumented mapping/renaming; shipped test/analysis examples remain hard-coded to `odtrack`. Under HG3 this is insufficient official checkpoint/evaluation support for realistic baseline reproduction without source/protocol repair. |
| **JDTrack (CX046)** | PASS | PENDING | **PENDING** | The code identifies the exact required checkpoint `JDTrack/ViT/JDTrack_online_target_fuse.pth.tar`, but the external blind audit enumerated the accessible author-linked Google models folder and did not find that file/folder. The alternate official Baidu bundle was not inspectable. Actual official checkpoint availability is therefore unresolved, not favorable. |
| **UMDATrack (CX051)** | PASS | PENDING | **PENDING** | Official stage-2 weights exist, but the blind audit found no unambiguous mapping from released asset names to the hard-coded evaluation checkpoint contract; it also found a documented `got10k_haze` key that is absent from the dataset registry and missing generated environment fields required by adverse-weather adapters. The remaining repair/mapping is unresolved rather than proved impossible. |
| **SiamABC (CX064)** | FAIL | FAIL | **FAIL** | Agreement. Models/source exist but the benchmark evaluator imports absent `eval_data` / `eval_toolkit` trees with no released restoration path. |

## 4. Queue consequence

From the 20-family pre-flag canonical set:

- **16 candidates currently have HG1/HG2/HG3 = PASS** and may enter Stage-2 evidence extraction;
- **2 candidates are HG3 PENDING**: JDTrack and UMDATrack. They are suspended from Stage 2 until the missing official evidence is resolved;
- **2 candidates are HG3 FAIL**: MambaLCT and SiamABC. They remain in the literature/canonical record as reference/excluded candidates.

This **16-family active scientific-audit queue is not a shortlist**.

## 5. Stage-2 activation

The prior activation blocker was unresolved Manager↔Codex disagreement. That disagreement is now reconciled into final PASS/FAIL/PENDING states.

Stage 2 is therefore activated **only for the 16 HG3-PASS candidates**, beginning with the predeclared canonical-ID Batch A:

1. CX007 — SpikeTrack
2. CX009 — UETrack
3. CX010 — UTPTrack
4. CX013 — FARTrack
5. CX014 — GOT-Edit

Manager and Codex must independently extract paper/scientific and code/engineering evidence for Batch A before any HG4/HG5 decision. No soft score is permitted yet.

## 6. Locked state after reconciliation

- HG1/HG2/HG3 reconciliation: **CLOSED**
- Active Stage-2 queue: **16**
- HG3 PENDING side queue: **2 — JDTrack, UMDATrack**
- HG3 FAIL/reference-only: **2 — MambaLCT, SiamABC**
- Stage 2A Batch A: **ACTIVATED**
- HG4/HG5: **PENDING — evidence extraction begins, no decision yet**
- HG6: **NOT STARTED**
- S1–S7 soft scoring: **NOT STARTED**
- Primary shortlist: **NONE**
- Main baseline: **NONE**
- Proposed architecture: **NONE**
