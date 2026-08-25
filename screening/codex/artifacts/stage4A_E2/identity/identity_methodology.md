# Stage 4A-E2 acquired-versus-local identity method

This comparison uses exactly the `31` rows marked `include_in_comparison=TRUE` in the external allowlist. No tracker prediction, score, raw-result quality, or diagnostic output is an input.

Runtime used only for the identity computation:

- Python `3.13.3`
- OpenCV `4.11.0`
- NumPy `2.2.6`

## Hash definitions

- Raw image stream: SHA-256 over concatenated JPEG file bytes in numeric pinned-evaluator order, with no path names or separators.
- Decoded BGR stream: `cv2.imread(..., cv2.IMREAD_COLOR)` followed by concatenated C-contiguous `uint8` BGR bytes in the same order.
- Decoded RGB stream: `cv2.cvtColor(BGR, cv2.COLOR_BGR2RGB)` followed by concatenated C-contiguous `uint8` RGB bytes.
- Raw ground truth: SHA-256 over the complete annotation-file bytes.
- Normalized ground truth: parse every numeric row; emit each value with Python `.17g`; comma-separate values; terminate every row with LF; SHA-256 the resulting ASCII bytes.
- First and last boxes: acquired-source normalized numeric JSON using the same `.17g` representation.

`duplicate_copy_identity` is a stable group ID derived from sequence name, local raw ordered-image hash, local raw-GT hash, and local numeric-JPEG count. `duplicate_group_size` in `notes` gives the number of included copies in that exact byte-identity group.

## Classification precedence

For a complete evaluator range:

1. `BYTE_IDENTICAL_TO_ACQUIRED` when the ordered raw-image stream and complete raw-GT bytes match.
2. `PIXEL_IDENTICAL_GT_IDENTICAL` when decoded pixels and normalized GT match.
3. `IMAGE_DIFFERENT_GT_IDENTICAL` when decoded pixels differ but normalized GT matches.
4. `IMAGE_IDENTICAL_GT_DIFFERENT` when decoded pixels match but normalized GT differs.
5. `DIFFERENT` otherwise.

`NO_EXISTING_COMPARISON` is reserved for a no-copy row; none is present because this manifest contains one row per included copy.

## Locked range handling

- Diving hashes use evaluator frames `1-215`; physical local frames `216-231` are excluded and disclosed in row notes. The acquired package also physically contains `231` Diving JPEGs, while the pinned evaluator uses `215`.
- Human3 local copies contain only frames/GT `1-199`, versus the acquired canonical `1-1698`. Shared image-prefix hashes are recorded for diagnostic identity, but both rows are forced to `DIFFERENT` and retain acquired/local frame counts `1698/199`.

## Result summary

- Rows: `31`
- Sequences represented: `11`
- `BYTE_IDENTICAL_TO_ACQUIRED`: `11`
- `PIXEL_IDENTICAL_GT_IDENTICAL`: `18`
- `DIFFERENT`: `2` (the two partial Human3 copies)
- Raw ordered-image stream matches: `31/31`
- Decoded BGR stream matches: `31/31`
- Decoded RGB stream matches: `31/31`
- Raw GT byte matches: `11/31`
- Normalized GT matches: `29/31`

The full external working comparison is retained at `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\manifests\acquired_vs_local_hash_comparison.csv`.
