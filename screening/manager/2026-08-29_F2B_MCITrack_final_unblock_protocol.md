# F2-B — MCITrack final technical-unblock and resumed mini-probe protocol

**Date:** 2026-08-29  
**Status:** `LOCKED_FINAL_ATTEMPT`  
**Branch:** `codex/f2b-mcitrack`  
**Prerequisite:** `screening/reconciliation/2026-08-29_F2_preflight_blocker_reconciliation.md`

## 1. Purpose

Avoid the unrelated full-OTB eager-construction failure while preserving the exact six-sequence scientific allowlist. If the complete preflight passes, execute the already locked F2-B contextual-state probe once. No scientific question, interval, control, metric or threshold changes.

## 2. Restricted official-dataset construction

Use the pinned official MCITrack `OTBDataset` class and exact canonical root.

Allowed compatibility adapter:

1. instantiate `OTBDataset()`;
2. before `get_sequence_list()`, filter `dataset.sequence_info_list` to exactly:
   - `Liquor`;
   - `Car4`;
   - `Crowds`;
   - `Girl`;
   - `Human3`;
   - `Suv`;
3. preserve the original official sequence-info dictionaries without field changes;
4. call the unchanged official `_construct_sequence` through `get_sequence_list()` for those six entries;
5. verify sequence names, frame counts, GT row counts and every frozen primary/control bound;
6. do not access, repair, copy, rename or parse `BlurCar1` or another non-allowlisted sequence.

No canonical dataset mutation or evaluator-metric change is permitted.

## 3. Final preflight

Required before scientific outcomes:

- source/config/checkpoint identity exact;
- strict checkpoint load;
- official deterministic one-frame smoke on an allowlisted sequence;
- diagnostics-disabled parity `<=1e-6`;
- exact snapshot/restore parity;
- state-copy no-op parity;
- all four state shapes/dtypes/devices recorded;
- five-template and current-computation call parity;
- scientific outcome row count remains zero until all gates pass.

Any new import/dependency/model/data blocker or failed parity concludes `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`. No further repair is allowed in this cycle.

## 4. Scientific execution

When and only when preflight passes, execute the unchanged protocol:

`screening/manager/2026-08-29_F2B_MCITrack_mini_probe_protocol.md`

Locked limits remain:

- exactly six same-sequence pairs and 254 primary/control rows;
- baseline, `ZERO_ALL_CARRIED_STATES`, `STALE_INTERVAL_START_STATES`;
- five-template/current-frame computation unchanged;
- one deterministic scientific execution;
- no per-layer test, threshold change, training, new dataset, predictor, full benchmark, HG6, Jetson or architecture work.

## 5. Outputs

Preserve the initial blocker report and create resumed artifacts with suffix `_R1`:

- `screening/codex/2026-08-29_F2B_MCITrack_R1_execution_report.md`;
- `screening/codex/2026-08-29_F2B_MCITrack_R1_results.csv`;
- `screening/codex/2026-08-29_F2B_MCITrack_R1_command_log.txt`;
- bounded artifacts under `screening/codex/artifacts/F2B_MCITrack_R1/`;
- exact scripts under `screening/codex/scripts/2026-08-29_F2B_MCITrack_R1_*`;
- at most one compatibility/instrumentation patch if unavoidable, under `screening/codex/patches/2026-08-29_F2B_MCITrack_R1.patch`.

## 6. Allowed conclusions

- `PROBE_POSITIVE_GAP_EVIDENCE`;
- `PROBE_NEGATIVE_REJECT_CURRENT_GAP`;
- `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`.

No HG6, scoring, shortlist, baseline selection or architecture design follows automatically.
