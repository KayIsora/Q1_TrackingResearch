# Stage 4A-E2 OTB100 acquisition evidence

Observed on 2026-08-25. This is a bounded text summary; the archive, extracted payload, `Dataset credit.docx`, images, annotations, and full per-file hash manifest remain external on `F:`.

## Source and transfer

- Public source API: `https://api.figshare.com/v2/articles/24427468`
- DOI: `10.6084/m9.figshare.24427468.v1`
- Figshare file ID: `42879853`
- Display name: `OTB2015.zip`
- Destination: `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\archive\OTB2015.zip`
- Transfer: `curl` exit `0`, HTTP `200`, `2,722,980,405` bytes, `602.911` seconds

## Archive integrity and structure

- Expected and observed MD5: `342b7dcb81142462b8ae9bb835cba6b4`
- Observed SHA-256: `aad6be170d417777a5cee0b99bdd367e540b81f9020ac08b5c96d4d5d5094be5`
- ZIP members: `58,961` (`58,764` files and `197` explicit directory entries)
- Uncompressed file bytes: `2,730,715,850`
- Top level: `OTB2015` plus `Dataset credit.docx`
- Unsafe rooted or traversal members: `0`
- Independent `bsdtar -tf` result: exit `0`, all `58,961` members listed, empty stderr
- Full ZIP CRC stream test: PASS; no bad member

## Extraction and byte preservation

Extraction used `bsdtar 3.8.4` / `libarchive 3.8.4` without renames or content transforms. The first extraction command returned exit `1` because exFAT rejected timestamp restoration for every file: `58,764` occurrences of `Can't restore time: Invalid argument`, one delayed-error summary, and no other error category. This is retained as a non-clean extraction exit and is not hidden.

Content verification subsequently established:

- extracted files: `58,764 / 58,764`;
- extracted bytes: `2,730,715,850 / 2,730,715,850`;
- missing files: `0`;
- extra files: `0`;
- size mismatches: `0`;
- CRC32 mismatches: `0`;
- byte mismatches: `0`;
- full external per-file manifest SHA-256: `a58329bea07dc96f9d35ad5d2a22785e23198f90c451da6369f7eaa985625032`.

The extraction state is therefore `CONTENT_COMPLETE_BYTE_VERIFIED_WITH_TIMESTAMP_METADATA_WARNINGS`; it is not represented as a clean extractor exit.

## Pinned evaluator layout

The acquired `OTB2015` directory contains `98` physical sequence directories and `102` ground-truth text files. All `100` entries from SpikeTrack commit `1537db51a1cc9f6e30cce469fba3e51f5721b3d0` `lib/test/evaluation/otbdataset.py` have their required source frames and ground truth.

- Direct layout matches: `95`
- Nonmutating staging aliases required: `5` (`Human4_2`, `Jogging_1`, `Jogging_2`, `Skating2_1`, `Skating2_2`)
- Evaluator frame references: `59,035`
- Unique referenced image paths: `58,255`
- Blocked evaluator entries: `0`

## Storage evidence

- `F:` filesystem: exFAT
- Planning probe before destination creation at `2026-08-25T16:13:35.9741325Z`: `984,562,270,208` free bytes
- Destination-state observation at `2026-08-25T16:13:49.8426803Z`: `984,560,697,344` free bytes
- Difference between the two time-separated observations: `1,572,864` bytes; both exceed the required `6.127 GB` reserve
- Free immediately after extraction: `966,346,670,080` bytes
- Free after full preservation audit: `966,337,495,040` bytes
- Volume total: `999,058,046,976` bytes

## External evidence retained

- `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\manifests\figshare_article_24427468.json`
- `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\manifests\download_response_headers.txt`
- `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\manifests\extracted_file_manifest.csv`
- `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\manifests\otb_evaluator_sequence_inventory.csv`
- `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\stage4a_e2_results\archive_integrity.json`
- `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\stage4a_e2_results\per_file_integrity_summary.json`
- `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\stage4a_e2_results\extraction_content_validation.json`
- `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\stage4a_e2_results\otb_evaluator_layout_summary.json`
- `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\stage4a_e2_results\pre_acquisition_space_reconciliation.json`

No second dataset, checkpoint, environment installation, tracker run, Stage 4A-E3 work, or Stage 4B work occurred in this acquisition lane.
