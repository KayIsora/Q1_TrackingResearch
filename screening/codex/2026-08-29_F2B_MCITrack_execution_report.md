# F2-B — MCITrack bounded contextual-state mini-probe execution report

**Date:** 2026-08-29

**Protocol:** `screening/manager/2026-08-29_F2B_MCITrack_mini_probe_protocol.md`

**Terminal state:** `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`

## Boundary

This report records a technical preflight blocker only. No scientific outcome row was produced, no metric gate was evaluated, and no result-dependent repair was attempted. HG6, S1–S7, scoring, shortlist selection, baseline selection, Jetson work and architecture design were not started.

## Branch and start state

- Branch: `codex/f2b-mcitrack`.
- Required start commit: `89b12d36f635b8d91f2f3587bc4c299a0d1be917` — verified.
- Local/remote branch equality before work: verified.
- Worktree before work: clean.

The plain `git pull --ff-only` reported `fatal: Cannot fast-forward to multiple branches`; the explicit equivalent `git pull --ff-only origin codex/f2b-mcitrack` completed as `Already up to date`. This branch-sync issue occurred before any scientific work.

## Pinned source/config/checkpoint checks

- Official source checkout: `E:\Robot_Backup\tmp\stage2_batchB_root_20260825_7da81ad\mcitrack`.
- Source SHA: `e667193eaec4c8a73d4bdd856a662aecdb844b43` — **PASS**.
- Source worktree: clean — **PASS**.
- Config: `experiments/mcitrack/mcitrack_b224.yaml`.
- Config worktree SHA-256: `2F498726C55601BA1B056D282E80C600F330EBDB5613ACB9B57041520EC76CC7`.
- Config Git object: `d6cae8ece8bb52bf09e2abb613781ed206bb7973`, identical to the object at the pinned source commit — **PASS**.
- Checkpoint: `E:\Robot_Backup\tmp\stage2b_checkpoints\mcitrack\MCITRACK_ep0300.pth.tar`.
- Checkpoint SHA-256: `6F28F9425FE6E7B52ECA4D1D9ADC7A59AA51558A21BE300F4F456AEBBD4EB2D9` — **PASS**.

The raw config worktree and Git-blob SHA-256 values differ because the clean Windows checkout contains CRLF line endings while the Git blob contains LF. Git object identity and a clean path diff verify pinned content.

## Canonical data check

The six authorized sequence directories exist at the locked canonical root, with these frame/ground-truth counts:

| Sequence | Frames | Ground-truth rows |
|---|---:|---:|
| Liquor | 1741 | 1741 |
| Car4 | 659 | 659 |
| Crowds | 347 | 347 |
| Girl | 500 | 500 |
| Human3 | 1698 | 1698 |
| Suv | 945 | 945 |

No dataset or checkpoint was downloaded.

## Zero-outcome preflight attempts

### Initial attempt

- Device/runtime requested: CUDA on the current NVIDIA GeForce MX250, using the existing Python 3.11 / PyTorch `2.0.0+cu118` environment that recognizes compute capability `sm_61`.
- Scientific outcome rows: **0**.
- Stop reason: the verifier compared raw worktree bytes directly to Git-blob bytes and rejected the CRLF/LF SHA-256 difference.

This was a technical verifier defect before tracker/model execution. The protocol's one permitted clean repair/restart was used to change only the config verifier: it now records both byte hashes and requires matching Git object identity plus a clean path diff. No model, evaluator, data, interval, threshold or scientific control changed.

### Permitted clean restart

- Scientific outcome rows: **0**.
- The source/config/checkpoint contract passed before official bootstrap.
- Official evaluator bootstrap called the released `lib.test.evaluation.otbdataset.OTBDataset` constructor against the locked canonical root.
- The constructor traversed its complete OTB registry and stopped with:

```text
Exception: Could not read file F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015/BlurCar1/groundtruth_rect.txt
```

The failure occurred before official tracker construction, strict checkpoint load, a clean forward, parity tests or any scientific outcome. Resolving it would require a second technical repair/restart (for example, changing the evaluator bootstrap or canonical data layout), which the locked protocol does not authorize.

## Required technical gates

| Gate | State | Reason |
|---|---:|---|
| Pinned source/config/checkpoint | **PASS** | Exact source SHA, config Git identity and checkpoint SHA-256 verified. |
| Strict load and official smoke | **FAIL** | Not reached because official dataset bootstrap failed. |
| Diagnostics-disabled baseline parity | **FAIL** | Not reached. |
| Snapshot/restore parity | **FAIL** | Not reached. |
| State-copy no-op parity | **FAIL** | Not reached. |
| Four state shapes/dtypes/devices | **FAIL** | Not reached in this execution lane. |
| Five-template/current-call parity | **FAIL** | Not reached. |

`FAIL` here means the required gate was not completed in this lane; it is not a scientific failure of MCITrack.

## Scientific execution and metrics

- Sequences scientifically executed: **0 / 6**.
- Primary/control evaluated rows: **0 / 254**.
- Baseline weakness: **NA**.
- Zero-state primary contribution: **NA**.
- Zero-state interaction: **NA**.
- Zero-state pair-sign consistency: **NA / 6**.
- Stale-state primary contribution: **NA**.
- Stale-state interaction: **NA**.
- Stale-state pair-sign consistency: **NA / 6**.
- Primary sequences meeting absolute contribution threshold: **NA / NA**.
- Passing intervention: **NONE**.
- Mini-probe result: **PROBE_INCONCLUSIVE_RESOURCE_BLOCKER**.

No partial outcome was interpreted, no locked gate was relaxed, and no interval/control/per-layer test was added.

## Locked downstream state

- HG6: **NOT STARTED**
- S1–S7: **NOT STARTED**
- PRIMARY SHORTLIST: **NONE**
- MAIN BASELINE: **NONE**
- PROPOSED ARCHITECTURE: **NONE**

STOP.
