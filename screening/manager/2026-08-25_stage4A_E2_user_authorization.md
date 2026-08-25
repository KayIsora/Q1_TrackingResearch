# Stage 4A-E2 — User authorization record

**Date:** 2026-08-25  
**Project:** Q1_TrackingResearch  
**Authorization status:** GRANTED  
**Authorized executor:** Codex worker lane

## Exact authorized scope

The User explicitly authorized:

> “Đồng ý Stage 4A-E2: cho phép Codex tải package OTB100 Figshare file ID 42879853, dung lượng khoảng 2.723 GB, lưu riêng trên ổ F:, kiểm tra MD5/SHA-256, giải nén và thực hiện đúng protocol đã khóa; chưa cho phép setup Linux hoặc chạy Stage 4B.”

## Authorized actions

Codex may:

1. Download exactly the author-attributed OTB100/OTB2015 package from Figshare file ID `42879853` under DOI record `https://doi.org/10.6084/m9.figshare.24427468.v1`.
2. Store the archive and extracted data only under the isolated external path:
   `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\`.
3. Verify the expected archive byte count `2,722,980,405`.
4. Verify provider MD5 `342b7dcb81142462b8ae9bb835cba6b4` and compute SHA-256.
5. Extract without rewriting source JPEG or annotation bytes.
6. Compare acquired OTB files/ground truth against existing local copies by raw and decoded hashes.
7. Rerun only the predeclared `Deer`, `Crossing`, and `Couple` sequences through the exact official SpikeTrack S256-T1 runner contract.
8. Expand the outcome-independent OTB candidate-sequence inventory according to the locked E2 protocol.
9. Commit only small text/checksum/result manifests to the Q1 repository; the archive and dataset payload remain external.

## Explicitly not authorized

Codex may not:

- set up or install the Linux/WSL PyTorch environment;
- run Stage 4A-E3;
- run Stage 4B;
- run a full OTB100 benchmark;
- run per-MRM diagnostic ablations;
- use SpikeTrack predictions, score maps, failures or raw-result quality to select diagnostic sequence candidates;
- freeze frame intervals, ambiguity labels, discovery/hold-out splits or the final diagnostic slice;
- assign `DIAG_PASS` or `DIAG_FAIL`;
- assign S1–S7, score, rank, shortlist, select a main baseline or design an architecture;
- download UAV123, TNL2K, LaSOT or any additional benchmark package.

## Governing protocol

Execution must follow:

`screening/manager/2026-08-25_stage4A_E2_otb_acquisition_protocol.md`

Any integrity mismatch, insufficient disk space, inaccessible provider file, extraction failure or protocol ambiguity requires stopping and reporting evidence rather than substituting a different source.

## Locked downstream state

- Stage 4A-E2: AUTHORIZED FOR EXECUTION
- Stage 4A-E3: NOT AUTHORIZED / DEFERRED PENDING E2 REVIEW
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
