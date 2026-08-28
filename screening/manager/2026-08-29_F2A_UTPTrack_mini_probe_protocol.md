# F2-A — UTPTrack bounded token-identity mini-probe

**Date:** 2026-08-29  
**Status:** `LOCKED_BEFORE_EXECUTION`  
**Candidate:** CX010 — UTPTrack  
**Purpose:** answer one missing-evidence question only.

## 1. Question

> Under source-defined ambiguity, does the released fixed 0.7 pruning path remove target-overlapping search tokens in a way that causes localization loss, and does a same-cardinality target-token rescue improve localization more than a size-matched non-target swap?

This is not a keep-ratio sweep, a proposed routing method, HG6, soft scoring or baseline selection.

## 2. Exact model contract

- official repo: `EIT-NLP/UTPTrack`;
- pinned SHA: `84e0f49711254a44f5308faaa9a2405db1964dd7`;
- config: `UTPTrack-O/experiments/ostrackcmp/ceatetta_256_r7_all.yaml`;
- checkpoint: `UTPTrack-O-224/OSTrackCMP_ep0300.pth.tar` from official HF snapshot `4372a928e4bf58615ecb217fe5010d2e3212e627`;
- checkpoint SHA-256: `E4EE630CD0E88E41CDBC55BD727C16CA5A4BE3756ADED65F2506B8F670ED0FEF`;
- scientific intervention site: **search candidate elimination only** at configured blocks 3, 6 and 9;
- DTE/STE template pruning, keep count, templates, head and checkpoint remain unchanged.

If the exact contract cannot strict-load and reproduce a deterministic one-frame official forward before outcome collection, conclude `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`.

## 3. Canonical data and exact allowlist

Use the accepted canonical OTB source:

`F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015\`

Execute only these six source sequences and frozen source-selected intervals:

| Probe interval | Sequence | Start–end | Source ambiguity group |
|---|---|---:|---:|
| UTP-P01 | Basketball | 397–435 | HIGH (`2`) |
| UTP-P02 | Bolt | 31–49 | LOWER (`1`) |
| UTP-P03 | Liquor | 565–589 | HIGH (`2`) |
| UTP-P04 | Car4 | 113–137 | LOWER (`1`) |
| UTP-P05 | Jogging_1 | 150–174 | HIGH (`2`) |
| UTP-P06 | Shaking | 1–25 | LOWER (`1`) |

Total evaluated source frames: **158**. Selection derives from source-only annotations frozen before any UTPTrack execution. Do not add or replace frames after outcomes are viewed.

## 4. Execution contract

For every sequence:

1. initialize once from the official sequence start;
2. advance the released baseline sequentially to each evaluated frame;
3. before the frame, snapshot the exact tracker/model/template/RNG state;
4. create three one-frame branches from the identical snapshot and identical image/crop contract;
5. commit only the official baseline state for continuation.

Branches:

- `BASELINE_RELEASED`;
- `TARGET_TOKEN_RESCUE`;
- `NON_TARGET_SWAP_CONTROL`.

This frame-local fork isolates token-selection causality and prevents counterfactual drift from changing later source states.

## 5. Target-token mapping

At each search-CE site, map the current GT box into the branch search-crop patch grid solely for offline oracle intervention and measurement.

A search token is `GT_TARGET_TOKEN` when its patch center lies inside the mapped current GT box.

Record before and after pruning:

- number of target tokens;
- retained target tokens;
- removed target tokens;
- target-token recall;
- selected token identities and keep scores.

GT is allowed only for the oracle control and metric; it is not a deployable input or proposed method.

## 6. Causal controls

### TARGET_TOKEN_RESCUE

At every configured search-CE site:

- begin from the released selected/removed identities;
- reinsert every removed `GT_TARGET_TOKEN`;
- evict the same number of currently retained non-target tokens with the lowest released keep scores;
- preserve exactly the released search-token cardinality;
- preserve token order/restoration semantics deterministically.

### NON_TARGET_SWAP_CONTROL

Use the same swap count `k` that TARGET_TOKEN_RESCUE would use at that site:

- reinsert the `k` highest-scored removed non-target tokens;
- evict the `k` lowest-scored retained non-target tokens;
- never reinsert a target token;
- preserve the same cardinality and perturbation size.

When `k=0`, both controls are no-ops and the frame is recorded as having no rescue opportunity.

No other keep ratio, token budget, template intervention or layer combination is permitted.

## 7. Parity and smoke gates

Before scientific execution:

- diagnostics disabled must match the clean released forward within `max_abs <= 1e-6`;
- a no-op rescue (`k=0`) must match baseline within the same tolerance;
- snapshot restore must reproduce the baseline branch exactly;
- the patch must record physical selected identities and cannot merely modify post-head output.

Failure before any scientific row is written permits one clean technical repair/restart. Failure after outcome rows exist stops as `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`; no outcome-dependent repair is allowed.

## 8. Locked metrics

Per frame and per CE site record:

- baseline IoU and center error;
- target-token recall;
- rescue opportunity `k`;
- target-rescue IoU gain: `IoU_target_rescue - IoU_baseline`;
- non-target-swap IoU gain: `IoU_non_target_swap - IoU_baseline`;
- target-specific gain: `IoU_target_rescue - IoU_non_target_swap`.

Aggregate separately for HIGH and LOWER ambiguity.

Define:

- `recall_gap = mean_recall_LOWER - mean_recall_HIGH`, using the CE site with the largest predeclared absolute gap, but report all three sites;
- `baseline_weakness = mean_IoU_LOWER - mean_IoU_HIGH`;
- `rescue_gain_HIGH = mean target-rescue gain on HIGH`;
- `rescue_interaction = rescue_gain_HIGH - rescue_gain_LOWER`;
- `target_specificity_HIGH = mean target-specific gain on HIGH`.

Report sequence-clustered bootstrap intervals descriptively with 10,000 resamples and seed `20260829`; point estimates and consistency control the mini-probe gate.

## 9. Positive/negative decision

`PROBE_POSITIVE_GAP_EVIDENCE` requires **all**:

1. at least **20 HIGH-ambiguity frames** have `k >= 1` at one or more CE sites;
2. `recall_gap >= 0.10` at at least one CE site;
3. `baseline_weakness >= 0.03`;
4. `rescue_gain_HIGH >= 0.02`;
5. `rescue_interaction >= 0.015`;
6. `target_specificity_HIGH >= 0.015`;
7. target-rescue mean gain is positive in at least **2 of the 3 HIGH sequences**.

If any scientific gate fails after valid execution, conclude:

`PROBE_NEGATIVE_REJECT_CURRENT_GAP`.

A scientific negative is terminal for the current UTPTrack gap in this cycle. Do not try a second keep ratio, another condition or another rescue rule.

## 10. Stop-loss limits

- no training/fine-tuning;
- no new dataset/checkpoint download unless the exact sealed checkpoint is already part of the audited official resource cache;
- six sequences, 158 evaluated frames;
- one baseline plus two controls;
- one deterministic scientific run;
- at most six model-execution hours;
- one small instrumentation patch;
- no full benchmark, predictor, HG6, Jetson run or architecture design.

## 11. Required outputs

Create only bounded artifacts:

- `screening/codex/2026-08-29_F2A_UTPTrack_execution_report.md`;
- `screening/codex/2026-08-29_F2A_UTPTrack_results.csv`;
- `screening/codex/2026-08-29_F2A_UTPTrack_command_log.txt`;
- bounded per-frame/site data under `screening/codex/artifacts/F2A_UTPTrack/`;
- exact scripts under `screening/codex/scripts/2026-08-29_F2A_UTPTrack_*`;
- at most one patch under `screening/codex/patches/2026-08-29_F2A_UTPTrack.patch`.

Allowed conclusions:

- `PROBE_POSITIVE_GAP_EVIDENCE`;
- `PROBE_NEGATIVE_REJECT_CURRENT_GAP`;
- `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`.

Codex must stop after the mini-probe. No HG6, score, shortlist, main baseline or proposed architecture is authorized.
