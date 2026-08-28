# F2-B R1 — final restricted-dataset unblock execution report

**Date:** 2026-08-29

**Protocol source:** `origin/main:screening/manager/2026-08-29_F2B_MCITrack_final_unblock_protocol.md`

**Final result:** `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`

## Boundary

This was the final authorized compatibility attempt. The restricted official-dataset construction succeeded, but official model construction encountered a new resource blocker before strict checkpoint load or any scientific outcome. The protocol permits no further repair, so the original six-pair probe was not started.

No canonical file, ground truth, evaluator metric, model weight, scientific interval, threshold, control or non-allowlisted sequence was changed or accessed.

## Branch and Manager inputs

- Branch: `codex/f2b-mcitrack`.
- Required starting HEAD: `7afcec285227c6fd138d1197e662c69e9fbfb151` — **PASS**.
- Worktree before R1: clean.
- Branch synchronized with `origin/codex/f2b-mcitrack` without merging main.
- The blocker reconciliation, final-unblock protocol and original mini-probe protocol were read directly from `origin/main` with `git show`.

## Restricted official-dataset construction

**State: PASS**

The R1 adapter:

1. instantiated the pinned official `lib.test.evaluation.otbdataset.OTBDataset` against the canonical root;
2. retained the original official sequence-info dictionary objects for exactly `Liquor`, `Car4`, `Crowds`, `Girl`, `Human3` and `Suv`;
3. assigned only those six original objects to `dataset.sequence_info_list`;
4. called the unchanged official `get_sequence_list()` and `_construct_sequence()` implementations;
5. did not access or repair `BlurCar1` or any other non-allowlisted sequence.

The call progressed past six-sequence construction into official tracker construction. The accepted Manager reconciliation and the initial branch evidence record these exact constructed-source counts:

| Sequence | Frames | Ground-truth rows | Maximum locked interval end | In range |
|---|---:|---:|---:|---:|
| Liquor | 1741 | 1741 | 589 | PASS |
| Car4 | 659 | 659 | 245 | PASS |
| Crowds | 347 | 347 | 165 | PASS |
| Girl | 500 | 500 | 429 | PASS |
| Human3 | 1698 | 1698 | 288 | PASS |
| Suv | 945 | 945 | 437 | PASS |

All twelve frozen primary/control interval bounds are inside their official constructed sequence ranges.

## Final preflight blocker

- Final-unblock window start: `2026-08-28T19:05:00Z`.
- Preflight completion: `2026-08-28T19:09:10.758980Z`.
- Technical-unblock wall time: `250.814764` seconds.
- 45-minute cap: **PASS**.
- Scientific outcome rows at stop: **0**.

After dataset construction and official parameter loading, official tracker construction entered `fastitpnb` and attempted:

```text
torch.load(.../mcitrack/pretrained/fast_itpn_base_clipl_e1600.pt)
```

It stopped with:

```text
FileNotFoundError: [Errno 2] No such file or directory:
E:\Robot_Backup\tmp\stage2_batchB_root_20260825_7da81ad\mcitrack/pretrained/fast_itpn_base_clipl_e1600.pt
```

The failure occurred before the complete official tracker checkpoint could strict-load. The final-unblock protocol says any new import/dependency/model/data blocker returns `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER` and allows no repair. Consequently no bootstrap bypass, alternate file, download, source patch or second attempt was used.

## Preflight gates

| Gate | State | Evidence |
|---|---:|---|
| Restricted dataset construction | **PASS** | Official six-entry metadata filter and unchanged sequence construction completed. |
| Source/config/checkpoint identity | **PASS** | Accepted exact identities from the initial blocker commit and Manager reconciliation; unchanged in R1. |
| Strict checkpoint load | **FAIL** | Not reached because Fast-iTPN bootstrap file was absent. |
| Official deterministic smoke | **FAIL** | Not reached. |
| Diagnostics-disabled baseline parity | **FAIL** | Not reached. |
| Snapshot/restore parity | **FAIL** | Not reached. |
| State-copy no-op parity | **FAIL** | Not reached. |
| Four state shapes/dtypes/devices | **FAIL** | Not reached in R1. |
| Five-template/current-call parity | **FAIL** | Not reached. |

These `FAIL` values mean mandatory gates were not completed; they are not scientific evidence against MCITrack.

## Scientific execution and locked metrics

- Sequences executed: **0**.
- Primary/control rows: **0**.
- Baseline weakness: **NA**.
- Zero-state primary contribution: **NA**.
- Zero-state interaction: **NA**.
- Zero-state pair-sign consistency: **NA**.
- Stale-state primary contribution: **NA**.
- Stale-state interaction: **NA**.
- Stale-state pair-sign consistency: **NA**.
- Passing intervention: **NONE**.
- Final result: **PROBE_INCONCLUSIVE_RESOURCE_BLOCKER**.

## Locked downstream state

- HG6: **NOT STARTED**
- MAIN BASELINE: **NONE**

STOP.
