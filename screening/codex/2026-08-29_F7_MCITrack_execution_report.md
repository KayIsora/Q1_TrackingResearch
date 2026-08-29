# F7 — MCITrack resource-sealed re-entry and unchanged mini-probe

**Date:** 2026-08-29

**Branch:** `codex/f7-mcitrack`

**Manager protocol:** `screening/manager/2026-08-29_F7_MCITrack_resource_reentry_protocol.md`

**Final result:** `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`

## 1. Boundary

The User explicitly authorized one download of `fast_itpn_base_clipl_e1600.pt` from the official author-linked Google Drive file ID `1hxth6RWiJ-3rY21CClZqjl2xsL07Kt17`, followed by strict-load preflight and the unchanged six-pair mini-probe only if every gate passed.

Exactly one asset was downloaded. No package or environment was installed or created. No other asset or dataset was downloaded. No source, model, checkpoint bytes, config, data, sequence, interval, intervention, metric, threshold, hypothesis, or benchmark was changed. The preflight was not retried and the scientific mini-probe was not started.

## 2. Official asset acquisition and seal

- Official folder ID: `1qDAMcU3JpahV7MriEOl4KfjKvAAFXd3E`.
- Official file ID: `1hxth6RWiJ-3rY21CClZqjl2xsL07Kt17`.
- Provider display name: `fast_itpn_base_clipl_e1600.pt` — **PASS**.
- Download started: `2026-08-29T03:45:24.4629497Z`.
- Download completed: `2026-08-29T03:45:38.4384309Z`.
- External destination: `F:\Q1_TrackingResearch_Data\MCITrack_F7_2026-08-29\official_asset\fast_itpn_base_clipl_e1600.pt`.
- Byte count: `180830695`.
- SHA-256: `626FD426DD89B2681D8B3942FA00E05FFFB467AF111C7BBD6A0A4B8BC0AFC388`.
- Config-required copy: `E:\Robot_Backup\tmp\stage2_batchB_root_20260825_7da81ad\mcitrack\pretrained\fast_itpn_base_clipl_e1600.pt`.
- External/copy byte and SHA-256 equality: **PASS**.
- Asset download count: **1**.

The independently computed seal is retained in `F:\Q1_TrackingResearch_Data\MCITrack_F7_2026-08-29\manifests\official_asset_manifest.json`. The asset and its config-path copy are excluded from the Git commit.

## 3. Locked identity preflight

| Identity | Required | Observed | State |
|---|---|---|---:|
| Official source | `kangben258/MCITrack` at `e667193eaec4c8a73d4bdd856a662aecdb844b43` | Exact detached HEAD; clean worktree | **PASS** |
| B224 config | `experiments/mcitrack/mcitrack_b224.yaml` | SHA-256 `2F498726C55601BA1B056D282E80C600F330EBDB5613ACB9B57041520EC76CC7` | **PASS** |
| Final checkpoint | `MCITRACK_ep0300.pth.tar` | `428943566` bytes; SHA-256 `6F28F9425FE6E7B52ECA4D1D9ADC7A59AA51558A21BE300F4F456AEBBD4EB2D9` | **PASS** |
| Bootstrap | Exact official file/name/ID | `180830695` bytes; SHA-256 `626FD426DD89B2681D8B3942FA00E05FFFB467AF111C7BBD6A0A4B8BC0AFC388` | **PASS** |
| Environment | Existing Python 3.11 / PyTorch 2.0 CUDA | Python 3.11.7; PyTorch 2.0.0+cu118; NVIDIA GeForce MX250 | **PASS** |
| Restricted OTB set | Liquor, Car4, Crowds, Girl, Human3, Suv only | Exact six metadata entries and in-range frame/GT counts | **PASS** |

## 4. Construction, strict load, and smoke

The official B224 builder loaded the newly sealed Fast-iTPN bootstrap without a bypass. The official tracker constructor then returned successfully after its `strict=True` load of the full `MCITRACK_ep0300.pth.tar`. Control reached `tracker.track(...)` in the preflight, which is downstream of both model construction and strict load.

The first deterministic frame smoke stopped before returning any bbox, confidence, carried state, or scientific outcome. PyTorch raised:

```text
RuntimeError: Deterministic behavior was enabled ... but this operation is not
deterministic because it uses CuBLAS and you have CUDA >= 10.2. To enable
deterministic behavior ... set CUBLAS_WORKSPACE_CONFIG=:4096:8 or :16:8.
```

The failure occurred in the current-frame Mamba/context path at a CUDA linear operation. `CUBLAS_WORKSPACE_CONFIG` must be set before the Python process begins; changing it and rerunning would be a compatibility repair and second preflight. F7 explicitly forbids both. Therefore the variable was not changed and no retry occurred.

## 5. Final technical gates

| Gate | State | Evidence |
|---|---:|---|
| Source/config/final-checkpoint identities | **PASS** | Exact SHA/hash contract verified before construction |
| Exact official bootstrap identity and copy | **PASS** | Name, file ID, bytes, SHA-256, and copy equality verified |
| Official B224 construction | **PASS** | Control returned from official builder/constructor |
| Full checkpoint strict load | **PASS** | `lib/test/tracker/mcitrack.py` completed `strict=True` before `tracker.track` was reached |
| Official deterministic frame smoke | **FAIL** | CuBLAS deterministic-workspace requirement stopped the first forward before output |
| Diagnostics-disabled parity `max_abs <= 1e-6` | **NOT REACHED** | Smoke did not return |
| Snapshot/restore parity | **NOT REACHED** | Smoke did not return |
| State-copy no-op parity | **NOT REACHED** | Smoke did not return |
| Four carried-state shapes/dtypes/devices | **NOT REACHED** | Smoke did not return carried state |
| Five-template/current-frame call parity | **NOT REACHED** | Smoke did not complete |
| Within four-hour stop-loss | **PASS** | Preflight stopped at `2026-08-29T03:51:57.776675Z` |

## 6. Scientific execution

- Mini-probe started: **NO**.
- Scientific sequences executed: **0**.
- Scientific primary/control rows: **0 / 254**.
- Baseline weakness: **NA**.
- Zero-state contribution/interaction: **NA**.
- Stale-state contribution/interaction: **NA**.
- Passing intervention: **NONE**.

No scientific conclusion about MCITrack's carried-state mechanism can be made from this run.

## 7. Decision

**`PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`**

The exact asset blocker is resolved and strict load passes, but the locked deterministic smoke gate is blocked by the pre-process CuBLAS workspace contract. Because F7 permits no compatibility repair or retry, the cycle stops before outcomes.

## 8. Locked downstream state

- F6: **COMPLETE / ACCEPTED**
- F7 scientific mini-probe: **NOT STARTED**
- HG6: **NOT STARTED**
- S1-S7: **NOT STARTED**
- PRIMARY SHORTLIST: **NONE**
- MAIN BASELINE: **NONE**
- PROPOSED ARCHITECTURE: **NONE**

STOP.
