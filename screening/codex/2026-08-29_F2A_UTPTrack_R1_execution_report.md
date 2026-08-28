# F2-A R1 — UTPTrack final technical-unblock execution report

**Date:** 2026-08-29

**Branch:** `codex/f2a-utptrack`

**Required starting HEAD:** `6293d07c35b7f9b9792c63aaa61262100aaf6a32`

**Final result:** `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`

## Boundary

This R1 run used only the two runtime compatibility modules authorized by the Manager final-unblock protocol. It preserved the original blocker artifacts and did not modify the pinned source, config, checkpoint, canonical images, or initial F2-A report.

The OpenCV fallback contract passed on one canonical frame from each of the six locked sequences. A new dependency blocker then occurred while importing the official tracker. Under the final-attempt stop rule, execution stopped before strict checkpoint load, model construction, any model forward, or any scientific outcome row.

No package was installed. No alternate decoder, extra import shim, source patch, model change, data change, keep-ratio change, or scientific repair was attempted.

## Sync and Manager authorization

- branch HEAD before R1: `6293d07c35b7f9b9792c63aaa61262100aaf6a32` — PASS;
- worktree before R1: clean — PASS;
- Manager reconciliation read from `origin/main` without merging main — PASS;
- final-unblock protocol read from `origin/main` — PASS;
- original locked mini-probe protocol read from `origin/main` — PASS;
- initial blocker report and command log read and preserved — PASS.

## Compatibility unblock

Before importing official UTPTrack modules, the harness registered exactly:

1. runtime-only `torch._six.string_classes = (str,)`;
2. a runtime-only optional `jpeg4py` module whose `JPEG(...).decode()` raises the controlled exception `F2A_R1_CONTROLLED_JPEG4PY_UNAVAILABLE`.

The pinned `jpeg4py_loader()` caught that controlled exception and returned `None`, after which the released `default_image_loader()` set `use_jpeg4py=False` and used its documented OpenCV fallback.

Compatibility unblock result: **FAIL overall**. The two authorized blockers were cleared, but importing `lib.test.tracker.ostrackcmp` exposed a new dependency blocker:

```text
ModuleNotFoundError: No module named 'visdom'
```

The import path was `lib.test.tracker.ostrackcmp` → `lib.test.tracker.basetracker` → `lib.vis.visdom_cus`. No `visdom` package installation, runtime shim, or source bypass is authorized, so the lane stopped.

## Image-loader OpenCV parity

Official `default_image_loader(path)` was compared byte-for-byte against:

```text
cv2.imread(path, cv2.IMREAD_COLOR)
→ cv2.cvtColor(BGR, RGB)
```

| Locked sequence | Canonical frame | Shape | Dtype | Max absolute difference | `use_jpeg4py` |
|---|---|---:|---:|---:|---:|
| Basketball | `0001.jpg` | equal | equal | 0 | `False` |
| Bolt | `0001.jpg` | equal | equal | 0 | `False` |
| Liquor | `0001.jpg` | equal | equal | 0 | `False` |
| Car4 | `0001.jpg` | equal | equal | 0 | `False` |
| Jogging_1 | `Jogging/img/0001.jpg` | equal | equal | 0 | `False` |
| Shaking | `0001.jpg` | equal | equal | 0 | `False` |

Image-loader OpenCV parity: **PASS**.

## Final model preflight

| Gate | Result | Detail |
|---|---:|---|
| source SHA | PASS | `84e0f49711254a44f5308faaa9a2405db1964dd7` |
| locked config identity | PASS | `UTPTrack-O/experiments/ostrackcmp/ceatetta_256_r7_all.yaml`; SHA-256 `081829E597BE8C02D2ED05A1B339784313F2F133B96F79283AD40D08EC42948C` |
| checkpoint SHA-256 | PASS | `E4EE630CD0E88E41CDBC55BD727C16CA5A4BE3756ADED65F2506B8F670ED0FEF` |
| compatibility unblock | FAIL | new unauthorized dependency blocker: missing `visdom` |
| strict checkpoint load | FAIL / NOT REACHED | tracker import failed first |
| official deterministic one-frame forward | FAIL / NOT REACHED | tracker import failed first |
| diagnostics-disabled parity `<=1e-6` | FAIL / NOT REACHED | tracker import failed first |
| snapshot/restore parity | FAIL / NOT REACHED | tracker import failed first |
| `k=0` target-rescue parity | FAIL / NOT REACHED | tracker import failed first |
| `k=0` non-target-swap parity | FAIL / NOT REACHED | tracker import failed first |
| physical search-token identity mapping | FAIL / NOT RECORDED BY EXECUTION | no model forward was reached |

## Scientific execution accounting

| Field | Value |
|---|---:|
| scientific sequences executed | 0 |
| scientific evaluated frames | 0 |
| scientific outcome rows | 0 |
| HIGH rescue-opportunity frames | N/A |
| model-execution hours | 0 |
| source/config/checkpoint modification | NO |
| dataset/checkpoint download | NO |
| R1 source patch | NONE |

The locked six-sequence/158-frame mini-probe was not executed. All scientific metrics, gate values, and bootstrap intervals are `N/A`.

## Decision

`PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`

This result is neither positive gap evidence nor a scientific negative. The candidate returns to hold under the final technical-attempt protocol.

## Downstream locked state

- HG6: **NOT STARTED**
- MAIN BASELINE: **NONE**

**STOP.**
