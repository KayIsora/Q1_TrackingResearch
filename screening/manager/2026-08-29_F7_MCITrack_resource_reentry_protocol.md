# F7 — MCITrack resource-sealed re-entry and unchanged mini-probe

**Date:** 2026-08-29  
**Status:** `LOCKED_AWAITING_USER_DOWNLOAD_AUTHORIZATION`  
**Prerequisite:** `screening/reconciliation/2026-08-29_F6_resource_universe_reconciliation.md`

## 1. Purpose

F7 resolves one exact official MCITrack bootstrap resource, performs one strict technical preflight and, only if every gate passes, executes the already frozen six-pair contextual-state mini-probe once.

F7 does not create a new hypothesis, change the data, begin HG6, score candidates, select a baseline, design an architecture or run deployment tests.

## 2. User authorization boundary

Before execution the User must explicitly authorize download of exactly:

- filename: `fast_itpn_base_clipl_e1600.pt`;
- official author-linked Google Drive file ID: `1hxth6RWiJ-3rY21CClZqjl2xsL07Kt17`;
- official folder ID: `1qDAMcU3JpahV7MriEOl4KfjKvAAFXd3E`.

No other checkpoint, dataset, package bundle or model asset may be downloaded.

The provider does not expose an accepted project checksum in the current desk evidence. Therefore the acquired file must be retained externally and assigned an independently computed SHA-256 before model construction.

## 3. External storage

Use a dedicated external root:

`F:\Q1_TrackingResearch_Data\MCITrack_F7_2026-08-29\`

Create:

- `official_asset\`;
- `manifests\`;
- `results\`.

Do not commit the pretrained asset to GitHub.

Record:

- resolved URL/file ID;
- display name;
- byte count;
- download timestamps;
- SHA-256;
- destination path.

If the display name differs from the exact required filename, stop before construction.

## 4. Exact model/data contract

- official repo: `kangben258/MCITrack`;
- pinned SHA: `e667193eaec4c8a73d4bdd856a662aecdb844b43`;
- config: `experiments/mcitrack/mcitrack_b224.yaml`;
- final tracker checkpoint: `mcitrack_b224/MCITRACK_ep0300.pth.tar`;
- final checkpoint SHA-256: `6F28F9425FE6E7B52ECA4D1D9ADC7A59AA51558A21BE300F4F456AEBBD4EB2D9`;
- canonical OTB root: `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015\`.

Use the already accepted restricted official OTB construction for exactly:

- Liquor;
- Car4;
- Crowds;
- Girl;
- Human3;
- Suv.

Do not construct, repair or evaluate unrelated OTB entries.

## 5. Final technical preflight

Use the existing authorized Python 3.11 / PyTorch 2.0 CUDA environment and pinned source.

Before any scientific outcome row:

1. verify source/config/final-checkpoint identities;
2. copy or link the exact downloaded bootstrap asset into the config-required `pretrained/` path without modifying its bytes;
3. construct the official B224 model;
4. strict-load the released full tracker checkpoint;
5. run one official deterministic frame smoke;
6. verify diagnostics-disabled parity `max_abs <= 1e-6`;
7. verify snapshot/restore parity;
8. verify state-copy no-op parity;
9. record all four carried-state shapes, dtypes and devices;
10. verify five-template and current-frame call parity.

No compatibility repair, alternate bootstrap file, source bypass or model change is allowed in F7. Any new blocker before outcomes returns:

`PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`

and stops the cycle.

## 6. Scientific execution

Only when all preflight gates pass, execute the original frozen MCITrack mini-probe exactly as locked in:

`screening/manager/2026-08-29_F2B_MCITrack_mini_probe_protocol.md`

The frozen pairs remain:

| Pair | Sequence | Primary | Same-sequence control |
|---|---|---:|---:|
| MCI-P01 | Liquor | 565–589 | 20–44 |
| MCI-P02 | Car4 | 113–137 | 221–245 |
| MCI-P03 | Crowds | 33–37 | 161–165 |
| MCI-P04 | Girl | 411–429 | 363–381 |
| MCI-P05 | Human3 | 57–81 | 264–288 |
| MCI-P06 | Suv | 372–399 | 410–437 |

Branches:

- `BASELINE_RELEASED_STATE`;
- `ZERO_ALL_CARRIED_STATES`;
- `STALE_INTERVAL_START_STATES`.

Do not change a sequence, frame bound, state intervention, metric or positive threshold.

## 7. Stop-loss

- one official asset download;
- no package/environment installation;
- no training or fine-tuning;
- no new dataset;
- six sequences and 254 evaluated primary/control rows;
- one baseline plus two controls;
- one deterministic scientific execution;
- maximum four hours from completed asset verification through final result;
- no second repair or second scientific hypothesis;
- no full benchmark, predictor, HG6, Jetson or architecture work.

A scientific negative is terminal for the current MCITrack state-coupling gap.

## 8. Allowed outcomes

- `PROBE_POSITIVE_GAP_EVIDENCE`;
- `PROBE_NEGATIVE_REJECT_CURRENT_GAP`;
- `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`.

A positive mini-probe authorizes only a fast mechanism-level HG6 audit. It does not make MCITrack `GAP_READY`, shortlisted or selected.

## 9. Required artifacts

Create only bounded artifacts:

- `screening/codex/2026-08-29_F7_MCITrack_execution_report.md`;
- `screening/codex/2026-08-29_F7_MCITrack_results.csv`;
- `screening/codex/2026-08-29_F7_MCITrack_command_log.txt`;
- bounded data under `screening/codex/artifacts/F7_MCITrack/`;
- exact scripts under `screening/codex/scripts/2026-08-29_F7_MCITrack_*`;
- at most one instrumentation patch under `screening/codex/patches/2026-08-29_F7_MCITrack.patch`.

Do not commit the bootstrap asset, final checkpoint, dataset images or large tensors.

## 10. Locked state

- F6: **COMPLETE / ACCEPTED**;
- F7 user authorization: **PENDING**;
- asset download: **NOT AUTHORIZED**;
- model execution: **NOT AUTHORIZED**;
- HG6: **NOT STARTED**;
- S1–S7: **NOT STARTED**;
- primary shortlist: **NONE**;
- main baseline: **NONE**;
- proposed architecture: **NONE**.
