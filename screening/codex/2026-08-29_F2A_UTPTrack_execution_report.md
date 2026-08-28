# F2-A — UTPTrack bounded token-identity mini-probe execution report

**Date:** 2026-08-29

**Branch:** `codex/f2a-utptrack`

**Pinned branch start:** `89b12d36f635b8d91f2f3587bc4c299a0d1be917`

**Result:** `PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`

## Boundary

This report stops at the F2-A mini-probe boundary. No training, fine-tuning, dataset/checkpoint download, keep-ratio change, alternate pruning policy, benchmark expansion, HG6 work, scoring, shortlist selection, baseline selection, architecture design, Jetson run, or MCITrack F2-B output inspection occurred.

No scientific outcome row was created. The probe stopped during technical preflight after the one permitted clean repair/restart failed to produce a loadable official tracker runtime.

## Locked contract verification

| Item | Result | Evidence |
|---|---:|---|
| source repository | PASS | `EIT-NLP/UTPTrack` audited checkout at `E:\Robot_Backup\tmp\stage2B_utptrack_84e0f497` |
| source SHA | PASS | `84e0f49711254a44f5308faaa9a2405db1964dd7` |
| config | PASS | `UTPTrack-O/experiments/ostrackcmp/ceatetta_256_r7_all.yaml`; ViT-B/16, 128 template, 256 search, CE 3/6/9, DTE/STE 4/7/10, keep ratios 0.7 |
| checkpoint | PASS | audited official-cache file `UTPTrack-O-224/OSTrackCMP_ep0300.pth.tar`; 1,111,778,541 bytes |
| checkpoint SHA-256 | PASS | `E4EE630CD0E88E41CDBC55BD727C16CA5A4BE3756ADED65F2506B8F670ED0FEF` |
| canonical OTB root | PASS | exact Manager path exists; all six required source sequences and the `Jogging_1` ground-truth stream exist |
| strict checkpoint load | FAIL / NOT REACHED | official tracker module could not import after the single permitted repair/restart |
| official one-frame deterministic forward | FAIL / NOT REACHED | blocked before tracker construction |
| diagnostics-disabled parity `max_abs <= 1e-6` | FAIL / NOT REACHED | blocked before tracker construction |
| snapshot/restore parity | FAIL / NOT REACHED | blocked before tracker construction |
| `k=0` exact no-op | FAIL / NOT REACHED | blocked before tracker construction |
| source-to-search-token mapping | NOT EXECUTED | no model forward or scientific frame was permitted after the preflight blocker |

## Resource blocker and permitted repair

The audited CUDA environment is Python 3.12.13 with PyTorch `2.5.1+cu121`; CUDA is available on the NVIDIA GeForce MX250. Importing the released official tracker first failed because modern PyTorch no longer provides `torch._six.string_classes`.

Because no scientific outcome existed, the protocol permitted one clean technical repair/restart. A runtime-only compatibility shim supplied exactly `torch._six.string_classes = (str,)`; it did not modify source, weights, model operators, pruning identities, tracker state, or output computation.

On the clean restart, the official tracker import then failed in `lib/train/data/image_loader.py` with:

```text
ModuleNotFoundError: No module named 'jpeg4py'
```

This was the second technical failure. The locked protocol permits only one clean repair/restart before outcomes, so no package installation, second shim, source edit, or alternate loader path was attempted. The required strict load and smoke/parity gates therefore could not be reached.

## Execution accounting

| Field | Value |
|---|---:|
| scientific sequences executed | 0 |
| scientific evaluated frames | 0 |
| scientific outcome rows | 0 |
| HIGH rescue-opportunity frames | N/A |
| model-execution hours | 0 |
| training/fine-tuning | NO |
| dataset/checkpoint download | NO |
| instrumentation source patch | NONE |

The locked six-sequence/158-frame scientific run was **not executed**. Reporting `6` or `158` would fabricate work that did not occur.

## Locked scientific metrics

All scientific metrics are `N/A` because no valid frame/site outcome exists:

- target-token recall gap by CE site: `N/A`, `N/A`, `N/A`;
- baseline weakness: `N/A`;
- HIGH target-rescue gain: `N/A`;
- rescue interaction: `N/A`;
- HIGH target-specificity: `N/A`;
- HIGH sequences with positive rescue: `N/A / 3`;
- sequence-clustered bootstrap intervals: `N/A`.

## Decision

`PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`

This is not a scientific negative and not positive gap evidence. UTPTrack returns to hold under the lean stop-loss protocol.

## Downstream locked state

- HG6: **NOT STARTED**
- S1–S7: **NOT STARTED**
- PRIMARY SHORTLIST: **NONE**
- MAIN BASELINE: **NONE**
- PROPOSED ARCHITECTURE: **NONE**

**STOP.**
