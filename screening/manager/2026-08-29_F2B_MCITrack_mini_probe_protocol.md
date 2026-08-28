# F2-B — MCITrack bounded contextual-state mini-probe

**Date:** 2026-08-29  
**Status:** `LOCKED_BEFORE_EXECUTION`  
**Candidate:** CX038 — MCITrack  
**Purpose:** answer one missing-evidence question only.

## 1. Question

> With the five-template path held fixed, does MCITrack's carried four-state contextual memory have condition-specific benefit or harm on source-defined ambiguity intervals relative to matched same-sequence controls?

This is not adaptive Mamba design, state compression, HG6, soft scoring or baseline selection.

## 2. Exact model contract

- official repo: `kangben258/MCITrack`;
- pinned SHA: `e667193eaec4c8a73d4bdd856a662aecdb844b43`;
- config: `experiments/mcitrack/mcitrack_b224.yaml`;
- checkpoint: `mcitrack_b224/MCITRACK_ep0300.pth.tar`, official Drive ID `1F179L7zP2v8dj8at6c-agXo1fQjQEFt8`;
- checkpoint SHA-256: `6F28F9425FE6E7B52ECA4D1D9ADC7A59AA51558A21BE300F4F456AEBBD4EB2D9`;
- intervention site: the four carried contextual state tensors entering the current-frame Mamba/context path;
- five active templates, current-frame computation, confidence logic, checkpoint and prediction head remain unchanged.

The exact official evaluator/data/bootstrap construction must strict-load and reproduce a deterministic one-frame official forward before outcome collection. Failure before outcomes yields `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`.

## 3. Canonical data and exact allowlist

Use the accepted canonical OTB source:

`F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015\`

Execute exactly these six same-sequence source-selected primary/control pairs:

| Pair | Sequence | Primary interval | Same-sequence control |
|---|---|---:|---:|
| MCI-P01 | Liquor | 565–589 | 20–44 |
| MCI-P02 | Car4 | 113–137 | 221–245 |
| MCI-P03 | Crowds | 33–37 | 161–165 |
| MCI-P04 | Girl | 411–429 | 363–381 |
| MCI-P05 | Human3 | 57–81 | 264–288 |
| MCI-P06 | Suv | 372–399 | 410–437 |

Total evaluated primary/control frame rows: **254** across six unique sequences. These intervals were selected from source content before any MCITrack outcome existed. No interval may be added, replaced or resized after outcomes are viewed.

## 4. Execution contract

For every sequence:

1. initialize once at the official sequence start;
2. run the released baseline sequentially;
3. before every evaluated frame, snapshot the exact tracker/model/template/state/RNG contract;
4. create three one-frame branches from the identical snapshot and identical frame/crop;
5. commit only the official baseline state for continuation.

Branches:

- `BASELINE_RELEASED_STATE`;
- `ZERO_ALL_CARRIED_STATES`;
- `STALE_INTERVAL_START_STATES`.

Frame-local intervention isolates marginal carried-state utility and avoids counterfactual drift from changing later template/controller state.

## 5. Causal controls

### ZERO_ALL_CARRIED_STATES

Immediately before current-frame contextual computation:

- replace all four incoming carried state tensors with exact-shape, dtype and device zeros;
- execute the complete current Mamba/contextual path normally;
- retain all five templates and all current-frame Injector/Extractor/backbone/head operations;
- do not disable the wrapper or reset unrelated controller state.

### STALE_INTERVAL_START_STATES

For each primary/control interval:

- capture the four baseline carried states at `interval_start - 1`;
- on every evaluated frame in that interval, replace the current incoming carried states with those frozen start-state tensors;
- execute current contextual computation normally;
- retain all templates and current-frame operations.

No per-layer cherry-picking, state quantization, template intervention or confidence-threshold change is permitted.

## 6. Parity and smoke gates

Before scientific execution:

- instrumentation disabled must match the clean released forward within `max_abs <= 1e-6`;
- snapshot/restore must reproduce baseline bbox, score/confidence and continuation state exactly;
- a state-copy no-op must match baseline within the same tolerance;
- all four state shapes, dtypes, devices and layer identities must be recorded;
- the five-template input and current compute call counts must match baseline in both controls.

A technical repair/restart is allowed only before any scientific outcome row exists. After outcomes exist, stop as `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`; no outcome-dependent repair is allowed.

## 7. Locked metrics

Per frame record:

- baseline, zero-state and stale-state IoU/center error;
- four incoming-state norms and finite-value checks;
- confidence and whether the released controller would reset state;
- `zero_contribution = IoU_baseline - IoU_zero`;
- `stale_contribution = IoU_baseline - IoU_stale`.

For each pair compute primary minus same-sequence control effects:

- `baseline_weakness = mean_IoU_control - mean_IoU_primary`;
- `zero_interaction = mean_zero_contribution_primary - mean_zero_contribution_control`;
- `stale_interaction = mean_stale_contribution_primary - mean_stale_contribution_control`.

For each intervention report:

- complete-set mean interaction;
- absolute primary-condition contribution;
- number of pair interactions sharing the complete-set sign;
- state-norm and reset-proximity summaries as descriptive mechanism evidence.

Use pair-clustered bootstrap descriptively with 10,000 resamples and seed `20260829`. The locked point estimates and pair consistency control the F2 gate.

## 8. Positive/negative decision

`PROBE_POSITIVE_GAP_EVIDENCE` requires:

1. complete-set `baseline_weakness >= 0.03`;
2. at least one of `ZERO_ALL_CARRIED_STATES` or `STALE_INTERVAL_START_STATES` has absolute mean interaction `>= 0.02`;
3. the same intervention has absolute mean contribution on primary intervals `>= 0.02`;
4. at least **4 of 6 pair interactions** share the complete-set interaction sign;
5. at least **4 of 6 primary sequences** show absolute intervention contribution `>= 0.01` in that same direction;
6. five-template/current-frame call-count parity passes, so the effect cannot be attributed to template removal or wrapper disablement.

Either positive direction is allowed:

- positive interaction: carried state helps more under ambiguity;
- negative interaction: carried state is more harmful under ambiguity.

If no intervention satisfies all gates after valid execution, conclude:

`PROBE_NEGATIVE_REJECT_CURRENT_GAP`.

A scientific negative is terminal for the current MCITrack gap in this cycle. Do not try per-layer state selection, another reset threshold or a new condition.

## 9. Stop-loss limits

- no training/fine-tuning;
- no new dataset/checkpoint download unless the exact audited checkpoint already exists in the official resource cache;
- six sequences and 254 evaluated rows;
- one baseline plus two controls;
- one deterministic scientific run;
- at most six model-execution hours;
- one small instrumentation patch;
- no full benchmark, predictor training, HG6, Jetson run or architecture design.

## 10. Required outputs

Create only bounded artifacts:

- `screening/codex/2026-08-29_F2B_MCITrack_execution_report.md`;
- `screening/codex/2026-08-29_F2B_MCITrack_results.csv`;
- `screening/codex/2026-08-29_F2B_MCITrack_command_log.txt`;
- bounded per-frame/pair data under `screening/codex/artifacts/F2B_MCITrack/`;
- exact scripts under `screening/codex/scripts/2026-08-29_F2B_MCITrack_*`;
- at most one patch under `screening/codex/patches/2026-08-29_F2B_MCITrack.patch`.

Allowed conclusions:

- `PROBE_POSITIVE_GAP_EVIDENCE`;
- `PROBE_NEGATIVE_REJECT_CURRENT_GAP`;
- `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`.

Codex must stop after the mini-probe. No HG6, score, shortlist, main baseline or proposed architecture is authorized.
