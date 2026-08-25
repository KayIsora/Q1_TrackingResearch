"""Build and verify the bounded Stage-4A-E2 evaluator mini-root manifest."""

from __future__ import annotations

import csv
import hashlib
import os
import sys
from pathlib import Path


SOURCE = Path(os.environ["SPIKETRACK_STAGE4A_E2_SOURCE_ROOT"])
ACQUIRED = Path(os.environ["SPIKETRACK_STAGE4A_E2_ACQUIRED_ROOT"])
MINI = Path(os.environ["SPIKETRACK_STAGE4A_E2_OTB_ROOT"])
OUTPUT = Path(os.environ["SPIKETRACK_STAGE4A_E2_SUPPORT_ROOT"])
REAL = {"Deer": 71, "Crossing": 120, "Couple": 140}

sys.path.insert(0, str(SOURCE))
from lib.test.evaluation.otbdataset import OTBDataset  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


rows = []
items = OTBDataset.__new__(OTBDataset)._get_sequence_info_list()
if len(items) != 100 or len({item["name"] for item in items}) != 100:
    raise RuntimeError("Pinned evaluator is not the expected 100 unique records")

for order, item in enumerate(items, 1):
    sequence = item["name"]
    annotation = MINI / item["anno_path"]
    if not annotation.is_file():
        raise RuntimeError(f"Missing annotation for {sequence}: {annotation}")
    gt_rows = len(
        [line for line in annotation.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    )
    image_root = MINI / item["path"]
    image_files = sorted(image_root.glob(f"*.{item['ext']}"))
    is_real = sequence in REAL
    expected_images = REAL.get(sequence, 0)
    if len(image_files) != expected_images:
        raise RuntimeError(
            f"{sequence}: found {len(image_files)} real images; expected {expected_images}"
        )
    expected_gt = REAL.get(sequence, 6)
    if gt_rows != expected_gt:
        raise RuntimeError(f"{sequence}: GT rows {gt_rows}; expected {expected_gt}")
    rows.append(
        {
            "canonical_order": order,
            "sequence": sequence,
            "entry_type": (
                "REAL_ACQUIRED_BYTE_COPY" if is_real else "METADATA_ONLY_GT_STUB"
            ),
            "loader_frame_path": item["path"],
            "loader_annotation_path": item["anno_path"],
            "staged_sequence_root": str(MINI / item["path"].split("/", 1)[0]),
            "acquired_source_root_or_na": (
                str(ACQUIRED / sequence) if is_real else "NA"
            ),
            "real_image_count": len(image_files),
            "ground_truth_rows": gt_rows,
            "ground_truth_sha256": sha256(annotation),
            "authorized_tracker_execution": is_real,
            "notes": (
                "F: is exFAT and rejected New-Item -ItemType Junction with "
                "Incorrect function; Manager authorized a verified byte-copy fallback."
                if is_real
                else "Eager-loader annotation stub only; no source image is present."
            ),
        }
    )

path = OUTPUT / "mini_root_manifest.csv"
with path.open("w", encoding="utf-8", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

print("MINI_ROOT_MANIFEST=PASS")
print("CANONICAL_RECORDS=100")
print("REAL_IMAGE_SEQUENCES=Deer|Crossing|Couple")
