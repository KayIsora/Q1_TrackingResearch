# F2 technical-preflight blocker reconciliation

**Date:** 2026-08-29  
**Status:** `F2_TECHNICAL_UNBLOCK_ONCE_AUTHORIZED`  
**Reviewed branch commits:**

- F2-A UTPTrack: `6293d07c35b7f9b9792c63aaa61262100aaf6a32` on `codex/f2a-utptrack`;
- F2-B MCITrack: `7afcec285227c6fd138d1197e662c69e9fbfb151` on `codex/f2b-mcitrack`.

## Boundary

Both workers stopped correctly under the locked one-repair rule. Neither lane produced a scientific outcome row, ran a model forward, evaluated a frozen interval, or inspected a candidate-specific effect. Therefore neither result is a scientific negative and neither candidate is promoted.

This reconciliation authorizes exactly one final **technical-unblock attempt** per lane. It does not enlarge the scientific mini-probe, add a hypothesis, change a metric, authorize another candidate, begin HG6, score, shortlist, select a baseline, or design an architecture.

## 1. F2-A UTPTrack

### Accepted evidence

- pinned source/config/checkpoint identity: PASS;
- scientific outcome rows: 0;
- model-execution hours: 0;
- first import blocker: missing legacy `torch._six`;
- one runtime-only compatibility shim was applied;
- restart then stopped on unconditional `import jpeg4py` before tracker construction.

### Manager interpretation

The pinned UTPTrack `image_loader.py` explicitly states that the default loader should fall back to OpenCV when jpeg4py is unavailable, but the module imports `jpeg4py` unconditionally before that fallback can run. The blocker is therefore a narrow release-compatibility defect, not missing scientific data or a model-resource uncertainty.

### One final authorized repair

The resumed lane may:

1. install the already documented `torch._six.string_classes=(str,)` runtime shim;
2. provide a runtime-only optional-`jpeg4py` compatibility shim that makes the released `default_image_loader` take its documented OpenCV fallback;
3. verify on a canonical frame that the tracker loader output is byte-identical to direct `cv2.imread(..., IMREAD_COLOR)` followed by BGR-to-RGB conversion;
4. perform strict load, official smoke, parity and snapshot checks;
5. only if every preflight gate passes, execute the original frozen F2-A scientific probe once.

No package installation, alternate decoder, dataset change, keep-ratio change or second scientific hypothesis is authorized.

Any new import/dependency/model/data blocker before outcomes returns UTPTrack to `HOLD`. Any failure after an outcome row stops without repair.

## 2. F2-B MCITrack

### Accepted evidence

- pinned source/config/checkpoint identity: PASS;
- all six authorized sequence directories and GT row counts: PASS;
- scientific outcome rows: 0;
- first verifier failure was a CRLF/LF byte-hash mismatch and was repaired using Git-object identity plus clean-diff verification;
- restart stopped while the official `OTBDataset.get_sequence_list()` eagerly constructed the complete OTB list and emitted the generic `Could not read file .../BlurCar1/groundtruth_rect.txt` exception.

### Manager interpretation

The canonical E2 source manifest records `BlurCar1/groundtruth_rect.txt` as present and `READY_DIRECT`. The six authorized MCITrack sequences are also complete. Thus the observed message does not establish that the selected scientific data are missing; it arises in an unrelated full-dataset bootstrap path and may mask a parser/layout issue in a sequence that is outside the F2-B allowlist.

### One final authorized repair

The resumed lane may:

1. instantiate the pinned official `OTBDataset` without constructing its complete sequence list;
2. filter `sequence_info_list` to exactly the six locked names (`Liquor`, `Car4`, `Crowds`, `Girl`, `Human3`, `Suv`) before calling `get_sequence_list()`;
3. use the unchanged official `_construct_sequence` method for those six entries;
4. verify the constructed frame/GT counts and frozen interval bounds;
5. perform strict load, official smoke, parity, snapshot and state-copy no-op checks;
6. only if every preflight gate passes, execute the original frozen F2-B scientific probe once.

No canonical-data edit, GT rewrite, full-dataset repair, model change, additional sequence or second state hypothesis is authorized.

Any new import/dependency/model/data blocker before outcomes returns MCITrack to `HOLD`. Any failure after an outcome row stops without repair.

## 3. Hard stop-loss

For each lane:

- this is the final compatibility attempt in the current cycle;
- maximum technical-unblock wall time before scientific execution: 45 minutes;
- no more than the already authorized one patch/script set;
- scientific sequence/frame/control caps remain unchanged;
- if the preflight still fails, do not probe SSTrack automatically; complete F2 reconciliation and refresh resources/universe as required by the lean plan.

## Locked state

- F2-A UTPTrack: `FINAL_TECHNICAL_UNBLOCK_AUTHORIZED`;
- F2-B MCITrack: `FINAL_TECHNICAL_UNBLOCK_AUTHORIZED`;
- scientific outcomes currently available: **NONE**;
- F3 HG6: **LOCKED**;
- S1–S7: **NOT STARTED**;
- primary shortlist: **NONE**;
- main baseline: **NONE**;
- proposed architecture: **NONE**.
