# F6 — resource and 2026 universe refresh reconciliation

**Date:** 2026-08-29  
**Status:** `F6_COMPLETE_MCI_REENTRY_SELECTED_USER_AUTHORIZATION_PENDING`  
**Reviewed Codex commit:** `a752e974549ff4eb1261a206094b398093401b62` on `codex/f6-refresh`

## Boundary

This reconciliation accepts or rejects F6 desk findings and selects the minimum next action. It does not execute a model, download an asset, reopen UTPTrack/MCITrack F2 automatically, insert a new family into the canonical matrix, begin HG6, assign S1–S7, form a shortlist, select a main baseline, or design an architecture.

## 1. F6 process acceptance

The F6 lane is accepted:

- no model/checkpoint was instantiated;
- no tracker was imported or executed;
- no package/environment was installed;
- no checkpoint, pretrain or dataset was downloaded;
- exactly 12 records were produced under the locked cap;
- the search was a bounded official-source delta rather than a repeat of Stage-1 broad discovery.

## 2. Existing-resource decisions

### CX010 — UTPTrack

**F6 finding accepted:** the official README-to-`install.sh` route accounts for every dependency exposed by the failed local preflight: legacy PyTorch supplies `torch._six`; the script installs `jpeg4py`; and it installs `visdom`.

**Manager state:** `RESOURCE_REENTRY_READY_NOT_SELECTED_CURRENT_CYCLE`.

UTPTrack is not scientifically rejected. It is not selected for the next execution because:

1. reproducing the legacy PyTorch 1.9/CUDA 10.2 stack would require another environment-construction cycle after two zero-outcome attempts;
2. the newly surfaced MaST family directly occupies motion-aware early token retention and sparse token-to-box processing, increasing collision risk for the most plausible UTPTrack improvement relation;
3. the current lean objective permits one highest-value continuation rather than reopening multiple candidates.

Re-entry remains possible after a later strategic decision; no environment installation or mini-probe is authorized now.

### CX038 — MCITrack

**F6 finding accepted:** the exact author-linked asset `fast_itpn_base_clipl_e1600.pt` is visible under stable Google Drive file ID `1hxth6RWiJ-3rY21CClZqjl2xsL07Kt17`; the released B224 config and builder require it during construction before the final `MCITRACK_ep0300.pth.tar` strict load.

**Manager state:** `RESOURCE_REENTRY_SELECTED_AWAITING_USER_AUTHORIZATION`.

MCITrack is selected as the sole continuation because:

- the exact blocker is now author-controlled and narrowly resolved;
- the existing Python 3.11 / PyTorch 2.0 environment already progressed through dataset construction;
- the scientific intervention remains a bounded four-state zero/stale-state test with same-sequence controls;
- no scientific outcome from the earlier attempts exists, so the original frozen question remains uncontaminated;
- its mechanism is less directly collided by the newly surfaced MaST/SENTRY families than UTPTrack's token-pruning relation.

Asset acquisition, hashing, strict load, smoke and scientific execution remain unauthorized until the User explicitly approves the download.

### CX046 / CX051 / CX053

The no-change findings for JDTrack, UMDATrack and UncTrack are accepted. All three remain on their earlier evidence/resource holds.

## 3. New-family decisions

### NEW-2026-MAST — MaST

**Resource finding accepted:** the repository contains a usable ONNX inference/evaluation release and exact committed `nano`, `tiny` and `small` models.

**Manager state:** `HIGH_PRIORITY_WATCH_TRAINING_SOURCE_MISSING`.

MaST is highly relevant to the project's edge objective, but it is not activated as a main-baseline candidate now because:

- the repository explicitly says training code is forthcoming;
- the current release exposes ONNX inference rather than the trainable PyTorch architecture needed to add and jointly train a scientific module;
- MaST is already aggressively optimized end-to-end for sparsity and edge throughput, so ordinary further lightweight work would have little novelty leverage;
- a plausible robustness question around motion-prior failure cannot become a development baseline until source/training code is released.

MaST should be monitored for training-code release and retained immediately as a novelty adversary/reference for UTPTrack-style motion-aware pruning.

### NEW-2026-SENTRY — SENTRY

**Resource finding accepted:** the training-free code, host integrations, SAM2.1 checkpoint contract and bbox evaluators are substantive.

**Manager state:** `REFERENCE_ONLY_CURRENT_GENERIC_LIGHTWEIGHT_CORE`.

SENTRY is not activated for the present Core because:

- its scientific contribution is already a strong neighbor-aware, consistency-validated memory-write mechanism—the exact distractor/memory area the project would otherwise try to claim;
- its released runtime remains a SAM2-hosted segmentation pipeline with candidate generation and reverse temporal verification;
- reported real-time evidence is on A100 and the large configuration adds material runtime/VRAM overhead;
- a credible Jetson Nano B01 path would require major host/runtime replacement rather than a bounded extension.

SENTRY remains an important novelty reference and may later inform the identity-sensitive/person-memory extension.

### Other new families

TGTrack, ODONet, DASTrack, TR-MoE and SFDATrack remain reference/resource-watch records under the exact blockers identified by F6. They are not opened for F0 or execution.

## 4. Next action

Open exactly one continuation:

> **F7 — MCITrack official bootstrap acquisition, strict-load preflight and, only after all technical gates pass, one execution of the unchanged six-pair contextual-state mini-probe.**

The User must explicitly authorize downloading the exact author-linked bootstrap asset. No UTPTrack environment rebuild, MaST/SENTRY execution or SSTrack substitution is authorized.

If MCITrack F7 is technically blocked again before outcomes, return it to hold and stop for strategic review. If the mini-probe is scientifically negative, the current MCITrack gap is terminal. If positive, run fast mechanism-level HG6 before any full diagnostic.

## Locked state

- F6: **COMPLETE / ACCEPTED**;
- UTPTrack: **resource-reentry ready, not selected**;
- MCITrack: **selected, awaiting User download authorization**;
- MaST: **high-priority watch, training source missing**;
- SENTRY: **reference-only for current Core**;
- authorized model execution: **NONE**;
- active main-baseline candidate: **NONE**;
- S1–S7: **NOT STARTED**;
- primary shortlist: **NONE**;
- main baseline: **NONE**;
- proposed architecture: **NONE**.
