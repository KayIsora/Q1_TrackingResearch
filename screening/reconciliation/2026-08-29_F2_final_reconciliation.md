# F2 — final lean mini-probe reconciliation

**Date:** 2026-08-29  
**Status:** `F2_COMPLETE_NO_SCIENTIFIC_OUTCOME_RESOURCE_HOLD`  
**Reviewed branch commits:**

- UTPTrack F2-A final attempt: `024a0463dcaf7722ab6c74174be9637dffdbc223` on `codex/f2a-utptrack`;
- MCITrack F2-B final attempt: `b8999d901e72c936853912d1fd29d10c2588640b` on `codex/f2b-mcitrack`.

## Boundary

This reconciliation closes the current two-probe F2 cycle. It does not interpret either candidate scientifically because neither lane reached tracker construction, strict checkpoint loading, model forward, a frozen sequence, or a scientific outcome row. It does not begin HG6, authorize SSTrack as a substitute, assign S1–S7, form a shortlist, select a main baseline, or design an architecture.

## 1. UTPTrack decision

### Accepted evidence

- pinned source, config and checkpoint identities: pass;
- the authorized `torch._six` and optional-`jpeg4py` runtime compatibility path was applied without changing source, model, data or weights;
- the released loader's OpenCV fallback matched direct OpenCV BGR-to-RGB decoding byte-for-byte on one canonical frame from each of the six frozen sequences;
- scientific sequences, evaluated frames and scientific outcome rows: `0`;
- after the final authorized unblock, official tracker import exposed a new missing dependency: `visdom`.

### Final state

`PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`

UTPTrack returns to **resource hold**. This is not a scientific negative. The current cycle authorizes no additional import shim, package installation, source bypass or scientific attempt.

### Re-entry condition

UTPTrack may re-enter only in a later cycle after a desk-level resource refresh establishes a reproducible, auditable environment contract that resolves the released `torch._six`, optional image-loader and `visdom` dependency chain and reaches strict checkpoint load plus an official deterministic smoke before a new scientific protocol is authorized.

## 2. MCITrack decision

### Accepted evidence

- pinned source, config and full tracker checkpoint identities: pass;
- restricted official OTB construction for exactly `Liquor`, `Car4`, `Crowds`, `Girl`, `Human3` and `Suv`: pass;
- all frozen interval bounds are inside the constructed source ranges;
- scientific sequences, evaluated rows and scientific outcome rows: `0`;
- after the final authorized unblock, official model construction stopped on the absent local bootstrap resource `pretrained/fast_itpn_base_clipl_e1600.pt` before the full tracker checkpoint could strict-load.

### Final state

`PROBE_INCONCLUSIVE_RESOURCE_BLOCKER`

MCITrack returns to **resource hold**. This is not a scientific negative. The current cycle authorizes no bootstrap bypass, substitute weight, download, source change or further scientific attempt.

### Re-entry condition

MCITrack may re-enter only after a desk-level resource refresh identifies and seals the exact official Fast-iTPN bootstrap asset, or an official documented construction path that does not require that asset before strict-loading the released full tracker checkpoint. A later protocol must first reach strict load and an official deterministic smoke without scientific outcomes.

## 3. Stop-loss decision

The lean stop-loss is enforced:

- both authorized F2 slots are consumed;
- neither candidate produced positive or negative scientific evidence;
- F3 mechanism-level HG6 does not open because there is no F2-positive candidate;
- SSTrack remains parked and is not automatically substituted;
- no additional reserve mini-probe is authorized in this cycle;
- branch evidence remains preserved at the reviewed commits; it does not need to be merged into main to support this reconciliation.

## 4. Next action

The next permitted action is a **desk-only resource and narrow 2026-universe refresh**. It may check whether the exact UTPTrack/MCITrack blockers or earlier HG3/HG5 evidence blockers have changed and whether a newly accepted/published 2026 generic RGB-SOT candidate was missed. It may not execute models, download assets, reopen F2, or select a baseline.

## Locked state

- F2-A UTPTrack: `COMPLETE / RESOURCE HOLD`;
- F2-B MCITrack: `COMPLETE / RESOURCE HOLD`;
- scientific F2 outcome rows: `0`;
- F2-positive candidates: `0`;
- F3 HG6: `NOT OPENED`;
- SSTrack substitution: `NOT AUTHORIZED`;
- active main-baseline candidate: `NONE`;
- S1–S7: `NOT STARTED`;
- primary shortlist: `NONE`;
- main baseline: `NONE`;
- proposed architecture: `NONE`.
