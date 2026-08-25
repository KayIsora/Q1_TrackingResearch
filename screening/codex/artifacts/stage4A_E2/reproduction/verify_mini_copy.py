"""Verify the three authorized E2 sequence copies before stub creation."""

from __future__ import annotations

import csv
import hashlib
import os
from pathlib import Path


SOURCE = Path(os.environ["SPIKETRACK_STAGE4A_E2_ACQUIRED_ROOT"])
MINI = Path(os.environ["SPIKETRACK_STAGE4A_E2_OTB_ROOT"])
OUTPUT = Path(os.environ["SPIKETRACK_STAGE4A_E2_SUPPORT_ROOT"])
EXPECTED = {"Deer": 71, "Crossing": 120, "Couple": 140}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


file_rows = []
summary_rows = []
for sequence, expected_rows in EXPECTED.items():
    source_root = SOURCE / sequence
    staged_root = MINI / sequence
    source_files = {
        path.relative_to(source_root).as_posix(): path
        for path in source_root.rglob("*")
        if path.is_file()
    }
    staged_files = {
        path.relative_to(staged_root).as_posix(): path
        for path in staged_root.rglob("*")
        if path.is_file()
    }
    if set(source_files) != set(staged_files):
        raise RuntimeError(f"{sequence}: relative file sets differ")

    all_equal = True
    for relative_path in sorted(source_files):
        source_path = source_files[relative_path]
        staged_path = staged_files[relative_path]
        source_hash = sha256(source_path)
        staged_hash = sha256(staged_path)
        identical = (
            source_path.stat().st_size == staged_path.stat().st_size
            and source_hash == staged_hash
        )
        all_equal = all_equal and identical
        file_rows.append(
            {
                "sequence": sequence,
                "relative_path": relative_path,
                "source_bytes": source_path.stat().st_size,
                "staged_bytes": staged_path.stat().st_size,
                "source_sha256": source_hash,
                "staged_sha256": staged_hash,
                "byte_identical": identical,
            }
        )

    frame_count = len(list((staged_root / "img").glob("*.jpg")))
    gt_path = staged_root / "groundtruth_rect.txt"
    gt_rows = len([line for line in gt_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()])
    if frame_count != expected_rows or gt_rows != expected_rows or not all_equal:
        raise RuntimeError(
            f"{sequence}: frames={frame_count}, gt={gt_rows}, identical={all_equal}"
        )
    summary_rows.append(
        {
            "sequence": sequence,
            "staging_method": "BYTE_COPY_FALLBACK_EXFAT_NO_REPARSE_POINTS",
            "source_path": str(source_root),
            "staged_path": str(staged_root),
            "source_file_count": len(source_files),
            "staged_file_count": len(staged_files),
            "source_total_bytes": sum(path.stat().st_size for path in source_files.values()),
            "staged_total_bytes": sum(path.stat().st_size for path in staged_files.values()),
            "relative_file_set_identical": True,
            "all_file_sha256_identical": all_equal,
            "frame_count": frame_count,
            "ground_truth_rows": gt_rows,
            "ground_truth_sha256": sha256(gt_path),
            "verification_status": "PASS",
        }
    )

write_csv(
    OUTPUT / "real_copy_file_hashes.csv",
    file_rows,
    [
        "sequence",
        "relative_path",
        "source_bytes",
        "staged_bytes",
        "source_sha256",
        "staged_sha256",
        "byte_identical",
    ],
)
write_csv(
    OUTPUT / "real_copy_verification.csv",
    summary_rows,
    [
        "sequence",
        "staging_method",
        "source_path",
        "staged_path",
        "source_file_count",
        "staged_file_count",
        "source_total_bytes",
        "staged_total_bytes",
        "relative_file_set_identical",
        "all_file_sha256_identical",
        "frame_count",
        "ground_truth_rows",
        "ground_truth_sha256",
        "verification_status",
    ],
)
print("REAL_COPY_VERIFICATION=PASS")
