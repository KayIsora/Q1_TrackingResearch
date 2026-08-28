# F2-A — UTPTrack final technical-unblock and resumed mini-probe protocol

**Date:** 2026-08-29  
**Status:** `LOCKED_FINAL_ATTEMPT`  
**Branch:** `codex/f2a-utptrack`  
**Prerequisite:** `screening/reconciliation/2026-08-29_F2_preflight_blocker_reconciliation.md`

## 1. Purpose

Resolve only the two pre-outcome compatibility blockers already observed (`torch._six`, unconditional `jpeg4py` import). If the full preflight then passes, execute the already locked F2-A token-identity probe once. This protocol does not change its scientific question, data, controls, thresholds or stop conditions.

## 2. Compatibility contract

Before importing the official tracker:

1. register a runtime-only `torch._six` module with `string_classes=(str,)`;
2. register a runtime-only `jpeg4py` compatibility module whose `JPEG(...).decode()` raises a controlled exception, allowing the pinned released `default_image_loader` to enter its documented OpenCV fallback;
3. do not install a package and do not alter the canonical images;
4. verify the released loader returns exactly the same RGB array as direct OpenCV BGR-to-RGB conversion for at least one frame from each of the six authorized sequences;
5. verify `default_image_loader.use_jpeg4py` becomes `False` after the first fallback.

No other import shim or dependency repair is permitted.

## 3. Final preflight

Required before scientific outcomes:

- source/config/checkpoint hashes exact;
- strict checkpoint load;
- official deterministic one-frame smoke;
- diagnostics-disabled parity `<=1e-6`;
- state snapshot/restore parity;
- `k=0` target-rescue and non-target control parity;
- source-to-search-token identity mapping recorded;
- scientific outcome row count remains zero until all gates pass.

A new blocker or failed parity concludes `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER` and returns the candidate to hold. No further repair is allowed in this cycle.

## 4. Scientific execution

When and only when preflight passes, execute the unchanged protocol:

`screening/manager/2026-08-29_F2A_UTPTrack_mini_probe_protocol.md`

Locked limits remain:

- exactly six sequences and 158 evaluated frames;
- baseline plus `TARGET_TOKEN_RESCUE` and `NON_TARGET_SWAP_CONTROL`;
- fixed keep ratio and same-cardinality intervention;
- one deterministic scientific execution;
- no training, new dataset, predictor, full benchmark, HG6, Jetson or architecture work.

## 5. Outputs

Preserve the initial blocker report and create resumed artifacts with suffix `_R1`:

- `screening/codex/2026-08-29_F2A_UTPTrack_R1_execution_report.md`;
- `screening/codex/2026-08-29_F2A_UTPTrack_R1_results.csv`;
- `screening/codex/2026-08-29_F2A_UTPTrack_R1_command_log.txt`;
- bounded artifacts under `screening/codex/artifacts/F2A_UTPTrack_R1/`;
- exact scripts under `screening/codex/scripts/2026-08-29_F2A_UTPTrack_R1_*`;
- at most one compatibility/instrumentation patch if unavoidable, under `screening/codex/patches/2026-08-29_F2A_UTPTrack_R1.patch`.

## 6. Allowed conclusions

- `PROBE_POSITIVE_GAP_EVIDENCE`;
- `PROBE_NEGATIVE_REJECT_CURRENT_GAP`;
- `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`.

No HG6, scoring, shortlist, baseline selection or architecture design follows automatically.
