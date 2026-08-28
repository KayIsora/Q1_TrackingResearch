#!/usr/bin/env python3
"""Execute the locked Stage-4B Criterion-B discovery controls.

This runner is deliberately discovery-only.  It requires an already completed
and statistically passing Criterion-A summary, replays each unique discovery
source sequence once from its official first frame, and creates state-matched
forks only at the 24 non-overlapping frozen discovery intervals.  A clean
``none`` branch is checked frame-by-frame against the saved uninterrupted
Criterion-A prediction, score-map maximum, and confidence before any of the
nine registered controls is accepted.

The controls are contribution characterizations, not compute-saving paths:
``physical_skip`` is required to remain false.  HOLDOUT rows are used only as
sealed IDs for the guarded baseline reader.  No hold-out dataset path is ever
constructed, resolved, opened, or evaluated.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import random
import statistics
import subprocess
import sys
import time
from types import SimpleNamespace
from typing import Iterable, Sequence

import cv2
import numpy as np


PINNED_SOURCE_SHA = "1537db51a1cc9f6e30cce469fba3e51f5721b3d0"
T1_CONFIG_SHA256 = "9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8"
T1_CHECKPOINT_SHA256 = "cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df"
PATCH_SHA256_CANONICAL_LF = "d4a1065a32ef6da6132e4f9f7980f727e9109bb00e2e2370398b1e90de5a713a"
FROZEN_SLICE_SHA256_NORMALIZED_LF = (
    "bc52bd7ec6277a76e6da69346a84a8f9d801e2fee9cd92634a60cf9f119ea11a"
)
EXPECTED_DISCOVERY_IDS = tuple(f"R3-D{i:02d}" for i in range(1, 13))
EXPECTED_HOLDOUT_IDS = tuple(f"R3-H{i:02d}" for i in range(1, 9))
SEED = 20260826
PARITY_TOLERANCE = 1e-6

PATCHED_FILE_SHA256 = {
    "lib/models/spiketrack/sdtv3_search_inference.py": (
        "77b01cb252919c5a9e50500cc567f8c2766ac86ccd343dfcc7d3af7e95b72931"
    ),
    "lib/models/spiketrack/spiketrack_inf.py": (
        "01a1f891ff10542ce32cbffafd820e0338c5ea4ff67f59065ea3a7e044aa71f8"
    ),
    "lib/test/parameter/spiketrack.py": (
        "fcd53eb2f88e38f673dbb81d6b5c2e83b7b2b2f956d1105f4980a7890aa5af81"
    ),
    "lib/test/tracker/spiketrack_inf.py": (
        "56c0a985cdf5905e7e1c16383b4e9ad41406c3718e066bdf4a6f0701dc427471"
    ),
    "tracking/stage4a_spiketrack_smoke.py": (
        "477730db506c43e31cf8161b770c9479c1e611fc825affe85dfdee5ed947c002"
    ),
}
PATCHED_PATHS = tuple(PATCHED_FILE_SHA256)

# These names are both the analyzer's exact locked mode names and the accepted
# patch's exact diagnostic selectors.  No data-selected combination is allowed.
LOCKED_MODES = (
    ("mrm1", (1,)),
    ("mrm2", (2,)),
    ("mrm3", (3,)),
    ("mrm4", (4,)),
    ("mrm5", (5,)),
    ("mrm6", (6,)),
    ("early", (1, 2)),
    ("middle", (3, 4)),
    ("late", (5, 6)),
)
MODE_ORDER = {name: index for index, (name, _) in enumerate(LOCKED_MODES, start=1)}
MODE_MEMBERS = {name: members for name, members in LOCKED_MODES}

# Accepted Stage-4A-E2 non-mutating alias for the Figshare physical layout.
DISCOVERY_SOURCE_ALIASES = {
    "Jogging_1": {
        "path": "Jogging/img",
        "anno_path": "Jogging/groundtruth_rect.1.txt",
        "evidence": "2026-08-25_stage4A_E2_otb_source_manifest.csv row E2-OTB-062",
    }
}

REPO_OUTPUT_NAMES = (
    "state_snapshot_parity.csv",
    "mode_per_frame_metrics.csv",
    "mode_execution_manifest.csv",
    "mode_module_timing_characterization.csv",
    "criterionB_execution_summary.json",
)

SNAPSHOT_CAPTURE_DESCRIPTION = (
    "tracker.state;tracker.frame_id;tracker.template_list;tracker.cache;"
    "tracker.spike_rate_dict_temp;tracker.last_template_refresh_frame;"
    "tracker.window_penalty;tracker.stage4a flags/records;"
    "network.current_image_idx;network.spike_rate_dict;"
    "encoder._stage4a flags/forward_id/current+completed records;"
    "MRM retriever capture flags/buffers;"
    "template_encoder.current_image_idx+spike_rate_dict_temp;"
    "Python+NumPy+Torch CPU+all CUDA RNG"
)


@dataclass(frozen=True)
class IntervalSpec:
    pair_id: str
    side: str
    sequence: str
    start: int
    end: int
    source_row_sha256: str


class InputContractError(RuntimeError):
    """The frozen discovery execution input is malformed or inconsistent."""


class HoldoutExposureError(RuntimeError):
    """A sealed hold-out pair ID was seen before its outcome fields were read."""

    def __init__(self, path: Path, pair_id: str, line_number: int):
        super().__init__(
            f"STAGE4B_INVALID_HOLDOUT_EXPOSURE: sealed pair {pair_id!r} "
            f"at {path}:{line_number}; stopped before outcome fields"
        )


class _DigestingReader:
    """Hash exactly the bytes consumed by the guarded unbuffered reader."""

    def __init__(self, raw, digest) -> None:
        self.raw = raw
        self.digest = digest

    def read(self, size: int) -> bytes:
        value = self.raw.read(size)
        self.digest.update(value)
        return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--slice-csv", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--baseline-csv", type=Path, required=True)
    parser.add_argument("--criterion-a-summary", type=Path, required=True)
    parser.add_argument("--external-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=SEED)
    return parser.parse_args()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_output(source_root: Path, *arguments: str) -> str:
    command = [
        "git", "-c", f"safe.directory={source_root.as_posix()}",
        "-C", str(source_root), *arguments,
    ]
    return subprocess.check_output(command, text=True).rstrip()


def parse_bool(value: object, context: str) -> bool:
    normalized = str(value).strip().casefold()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise InputContractError(f"{context}: expected boolean, got {value!r}")


def parse_int(value: object, context: str) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise InputContractError(f"{context}: expected integer, got {value!r}") from exc


def parse_float(value: object, context: str) -> float:
    try:
        result = float(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise InputContractError(f"{context}: expected float, got {value!r}") from exc
    if not math.isfinite(result):
        raise InputContractError(f"{context}: non-finite float {value!r}")
    return result


def require_columns(fieldnames: Sequence[str] | None, required: Sequence[str], context: str) -> None:
    if fieldnames is None:
        raise InputContractError(f"{context}: CSV has no header")
    missing = [name for name in required if name not in fieldnames]
    if missing:
        raise InputContractError(f"{context}: missing required columns {missing}")


def _read_header_line(raw, path: Path) -> bytes:
    data = bytearray()
    while True:
        value = raw.read(1)
        if not value:
            if not data:
                raise InputContractError(f"{path}: empty CSV")
            return bytes(data)
        data.extend(value)
        if value in {b"\r", b"\n"}:
            return bytes(data)
        if len(data) > 1024 * 1024:
            raise InputContractError(f"{path}: unreasonably large CSV header")


def _read_first_field(raw, path: Path, line_number: int) -> tuple[bytes, bool] | None:
    """Read only through the first comma; bool indicates a blank line."""
    data = bytearray()
    while True:
        value = raw.read(1)
        if not value:
            if not data:
                return None
            raise InputContractError(
                f"{path}:{line_number}: row ended before first comma; pair_id must be first"
            )
        if value == b",":
            return bytes(data), False
        if value in {b"\r", b"\n"}:
            if bytes(data).strip() == b"":
                return b"", True
            raise InputContractError(
                f"{path}:{line_number}: row has no comma; pair_id must be first"
            )
        data.extend(value)
        if len(data) > 256:
            raise InputContractError(f"{path}:{line_number}: pair_id is too long")


def _read_row_remainder(raw, path: Path, line_number: int) -> bytes:
    data = bytearray()
    while True:
        value = raw.read(1)
        if not value:
            return bytes(data)
        data.extend(value)
        if value in {b"\r", b"\n"}:
            return bytes(data)
        if len(data) > 16 * 1024 * 1024:
            raise InputContractError(
                f"{path}:{line_number}: row exceeds 16 MiB or has an embedded newline"
            )


def guarded_outcome_rows(
    path: Path,
    allowed_pair_ids: frozenset[str],
    sealed_pair_ids: frozenset[str],
    required_columns: Sequence[str],
    digest,
) -> Iterable[tuple[int, dict[str, str]]]:
    """Yield discovery rows without reading a disallowed row's outcome fields."""
    with path.open("rb", buffering=0) as raw_file:
        raw = _DigestingReader(raw_file, digest)
        header_bytes = _read_header_line(raw, path)
        try:
            header = next(csv.reader([header_bytes.decode("utf-8-sig")]))
        except (UnicodeDecodeError, csv.Error) as exc:
            raise InputContractError(f"{path}: invalid UTF-8 CSV header") from exc
        header = [value.strip() for value in header]
        require_columns(header, required_columns, str(path))
        if not header or header[0] != "pair_id":
            raise InputContractError(
                f"{path}: pair_id must be first for the hard hold-out read guard"
            )
        if len(set(header)) != len(header):
            raise InputContractError(f"{path}: duplicate header names")

        line_number = 2
        while True:
            first = _read_first_field(raw, path, line_number)
            if first is None:
                break
            pair_bytes, blank = first
            if blank:
                line_number += 1
                continue
            try:
                pair_id = pair_bytes.decode("ascii").strip()
            except UnicodeDecodeError as exc:
                raise InputContractError(
                    f"{path}:{line_number}: pair_id must be unquoted ASCII"
                ) from exc
            if not pair_id or pair_id.startswith(('"', "'")):
                raise InputContractError(
                    f"{path}:{line_number}: pair_id must be an unquoted first field"
                )
            if pair_id not in allowed_pair_ids:
                if pair_id in sealed_pair_ids:
                    raise HoldoutExposureError(path, pair_id, line_number)
                raise InputContractError(
                    f"{path}:{line_number}: non-discovery pair {pair_id!r}; "
                    "stopped before outcome fields"
                )
            remainder = _read_row_remainder(raw, path, line_number)
            try:
                values = next(csv.reader([(pair_bytes + b"," + remainder).decode("utf-8")]))
            except (UnicodeDecodeError, csv.Error) as exc:
                raise InputContractError(f"{path}:{line_number}: invalid UTF-8 CSV row") from exc
            if len(values) != len(header):
                raise InputContractError(
                    f"{path}:{line_number}: {len(values)} values for {len(header)} columns"
                )
            row = {name: value.strip() for name, value in zip(header, values)}
            if row["pair_id"] != pair_id:
                raise InputContractError(f"{path}:{line_number}: pair_id parse mismatch")
            yield line_number, row
            line_number += 1


def parse_and_validate_slice(path: Path) -> tuple[list[dict], dict[str, list[IntervalSpec]], dict]:
    raw = path.read_bytes()
    normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    normalized_sha = sha256_bytes(normalized)
    if normalized_sha != FROZEN_SLICE_SHA256_NORMALIZED_LF:
        raise InputContractError(
            f"Frozen-slice normalized SHA-256 mismatch: {normalized_sha}"
        )
    try:
        rows = list(csv.DictReader(normalized.decode("utf-8-sig").splitlines()))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise InputContractError(f"Invalid frozen slice: {path}") from exc
    discovery = [row for row in rows if row.get("split") == "DISCOVERY"]
    holdout = [row for row in rows if row.get("split") == "HOLDOUT"]
    if tuple(row["pair_id"] for row in discovery) != EXPECTED_DISCOVERY_IDS:
        raise InputContractError("Frozen discovery IDs/order differ from the exact allowlist")
    if tuple(row["pair_id"] for row in holdout) != EXPECTED_HOLDOUT_IDS:
        raise InputContractError("Frozen hold-out IDs/order differ from the exact seal")
    if len(rows) != 20 or any(row.get("manager_status") != "FROZEN" for row in rows):
        raise InputContractError("Frozen slice must contain exactly 20 FROZEN rows")
    discovery_sequences = {
        row[f"{side}_sequence"] for row in discovery for side in ("primary", "control")
    }
    sealed_sequences = {
        row[f"{side}_sequence"] for row in holdout for side in ("primary", "control")
    }
    if discovery_sequences & sealed_sequences:
        raise InputContractError("Discovery and sealed hold-out source sets are not disjoint")

    canonical_lines = normalized.splitlines(keepends=True)
    if len(canonical_lines) != len(rows) + 1:
        raise InputContractError("Frozen slice contains unsupported multiline CSV fields")
    row_hashes = {
        row["pair_id"]: sha256_bytes(canonical_lines[index + 1])
        for index, row in enumerate(rows)
    }

    intervals_by_sequence: dict[str, list[IntervalSpec]] = defaultdict(list)
    for row in discovery:
        for side in ("primary", "control"):
            start = parse_int(row[f"{side}_start"], f"{row['pair_id']} {side} start")
            end = parse_int(row[f"{side}_end"], f"{row['pair_id']} {side} end")
            if start < 1 or end < start:
                raise InputContractError(f"Invalid frozen bounds for {row['pair_id']}/{side}")
            sequence = row[f"{side}_sequence"]
            if not sequence:
                raise InputContractError(f"Empty frozen sequence for {row['pair_id']}/{side}")
            intervals_by_sequence[sequence].append(
                IntervalSpec(
                    pair_id=row["pair_id"],
                    side=side,
                    sequence=sequence,
                    start=start,
                    end=end,
                    source_row_sha256=row_hashes[row["pair_id"]],
                )
            )
        if int(row["primary_end"]) - int(row["primary_start"]) != (
            int(row["control_end"]) - int(row["control_start"])
        ):
            raise InputContractError(f"Unequal frozen interval lengths in {row['pair_id']}")

    # State forks are unambiguous only when one frozen label owns each source
    # frame.  Adjacency is allowed; sharing even one frame is not.
    for sequence, intervals in intervals_by_sequence.items():
        intervals.sort(key=lambda item: (item.start, item.end, item.pair_id, item.side))
        for previous, current in zip(intervals, intervals[1:]):
            if current.start <= previous.end:
                raise InputContractError(
                    "Frozen discovery intervals overlap within source sequence: "
                    f"{sequence} {previous.pair_id}/{previous.side}={previous.start}-{previous.end} "
                    f"and {current.pair_id}/{current.side}={current.start}-{current.end}"
                )

    hashes = {
        "normalized_lf_sha256": normalized_sha,
        "working_tree_byte_sha256": sha256_bytes(raw),
        "row_hashes": row_hashes,
    }
    return discovery, dict(intervals_by_sequence), hashes


def expected_baseline_keys(discovery: list[dict]) -> set[tuple[str, str, int]]:
    expected: set[tuple[str, str, int]] = set()
    for row in discovery:
        for side in ("primary", "control"):
            start = int(row[f"{side}_start"])
            end = int(row[f"{side}_end"])
            expected.update((row["pair_id"], side, frame) for frame in range(start, end + 1))
    return expected


def load_baseline_frames(
    path: Path, discovery: list[dict]
) -> tuple[dict[tuple[str, str, int], dict], str]:
    required = (
        "pair_id", "side", "sequence", "frame_index",
        "pred_x_float", "pred_y_float", "pred_w_float", "pred_h_float",
        "pred_x_int", "pred_y_int", "pred_w_int", "pred_h_int",
        "gt_x", "gt_y", "gt_w", "gt_h", "iou", "iou_float",
        "failure", "success_at_0_5", "center_error", "score_map_max",
        "confidence_score", "initialization_frame", "tracker_mode",
        "ablation_control", "physical_skip",
    )
    pair_rows = {row["pair_id"]: row for row in discovery}
    frames: dict[tuple[str, str, int], dict] = {}
    digest = hashlib.sha256()
    for line_number, raw in guarded_outcome_rows(
        path,
        frozenset(EXPECTED_DISCOVERY_IDS),
        frozenset(EXPECTED_HOLDOUT_IDS),
        required,
        digest,
    ):
        pair_id = raw["pair_id"]
        side = raw["side"].casefold()
        if side not in {"primary", "control"}:
            raise InputContractError(f"{path}:{line_number}: invalid side {raw['side']!r}")
        frozen = pair_rows[pair_id]
        sequence = frozen[f"{side}_sequence"]
        if raw["sequence"] != sequence:
            raise InputContractError(
                f"{path}:{line_number}: sequence mismatch for {pair_id}/{side}"
            )
        frame = parse_int(raw["frame_index"], f"{path}:{line_number} frame_index")
        start = int(frozen[f"{side}_start"])
        end = int(frozen[f"{side}_end"])
        if not start <= frame <= end:
            raise InputContractError(
                f"{path}:{line_number}: frame {frame} outside frozen {start}-{end}"
            )
        key = (pair_id, side, frame)
        if key in frames:
            raise InputContractError(f"{path}:{line_number}: duplicate baseline key {key}")

        float_box = np.asarray(
            [parse_float(raw[f"pred_{axis}_float"], f"{path}:{line_number}") for axis in "xywh"],
            dtype=np.float64,
        )
        int_box = np.asarray(
            [parse_int(raw[f"pred_{axis}_int"], f"{path}:{line_number}") for axis in "xywh"],
            dtype=np.int64,
        )
        if not np.array_equal(float_box.astype(np.int64), int_box):
            raise InputContractError(f"{path}:{line_number}: integer box is not float truncation")
        gt_box = np.asarray(
            [parse_float(raw[f"gt_{axis}"], f"{path}:{line_number}") for axis in "xywh"],
            dtype=np.float64,
        )
        iou = parse_float(raw["iou"], f"{path}:{line_number} iou")
        iou_float = parse_float(raw["iou_float"], f"{path}:{line_number} iou_float")
        failure = parse_bool(raw["failure"], f"{path}:{line_number} failure")
        success = parse_bool(raw["success_at_0_5"], f"{path}:{line_number} success")
        if failure != (iou < 0.5) or success != (iou >= 0.5):
            raise InputContractError(f"{path}:{line_number}: baseline threshold flags disagree")
        initialization = parse_bool(
            raw["initialization_frame"], f"{path}:{line_number} initialization_frame"
        )
        if initialization != (frame == 1):
            raise InputContractError(
                f"{path}:{line_number}: initialization flag disagrees with official frame 1"
            )
        score = None if raw["score_map_max"] == "" else parse_float(
            raw["score_map_max"], f"{path}:{line_number} score_map_max"
        )
        confidence = None if raw["confidence_score"] == "" else parse_float(
            raw["confidence_score"], f"{path}:{line_number} confidence_score"
        )
        if (initialization and (score is not None or confidence is not None)) or (
            not initialization and (score is None or confidence is None)
        ):
            raise InputContractError(
                f"{path}:{line_number}: only initialization rows may omit score/confidence"
            )
        if raw["tracker_mode"] != "T1" or raw["ablation_control"].casefold() != "none":
            raise InputContractError(f"{path}:{line_number}: baseline is not exact T1/none")
        if parse_bool(raw["physical_skip"], f"{path}:{line_number} physical_skip"):
            raise InputContractError(f"{path}:{line_number}: baseline physical_skip is true")
        frames[key] = {
            "pair_id": pair_id,
            "side": side,
            "sequence": sequence,
            "frame_index": frame,
            "float_box": float_box,
            "int_box": int_box,
            "gt_box": gt_box,
            "iou": iou,
            "iou_float": iou_float,
            "failure": failure,
            "success_at_0_5": success,
            "center_error": parse_float(
                raw["center_error"], f"{path}:{line_number} center_error"
            ),
            "score_map_max": score,
            "confidence_score": confidence,
            "initialization_frame": initialization,
        }

    expected = expected_baseline_keys(discovery)
    if set(frames) != expected:
        raise InputContractError(
            "Baseline coverage differs from exact frozen discovery intervals; "
            f"missing={sorted(expected - set(frames))[:10]}, "
            f"extra={sorted(set(frames) - expected)[:10]}"
        )
    return frames, digest.hexdigest()


def validate_criterion_a_gate(
    summary_path: Path,
    execution_summary_path: Path,
    provenance_path: Path,
    baseline_path: Path,
    baseline_sha256: str,
    slice_path: Path,
    slice_sha256: str,
) -> tuple[dict, dict]:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    criterion_a = summary.get("criterion_a", {})
    if criterion_a.get("status") != "PASS" or criterion_a.get("pass") is not True:
        raise InputContractError("Criterion B is forbidden unless Criterion A summary is PASS")
    if summary.get("next_action") != "RUN_EXACTLY_NINE_PREDECLARED_CRITERION_B_MODES":
        raise InputContractError("Criterion-A summary does not authorize the nine Criterion-B modes")
    boundary = summary.get("frozen_boundary", {})
    if (
        boundary.get("validation") != "PASS"
        or boundary.get("discovery_pair_count") != 12
        or boundary.get("holdout_outcomes_read") != 0
        or boundary.get("holdout_pairs_present_in_outcome_inputs") != 0
    ):
        raise InputContractError("Criterion-A frozen/hold-out boundary did not pass")
    baseline_input = summary.get("inputs", {}).get("baseline_csv", {})
    if Path(baseline_input.get("path", "")).resolve() != baseline_path.resolve():
        raise InputContractError("Criterion-A summary references a different baseline CSV")
    if baseline_input.get("sha256") != baseline_sha256 or baseline_input.get("rows") != 596:
        raise InputContractError("Criterion-A summary baseline hash/row count mismatch")
    slice_input = summary.get("inputs", {}).get("frozen_slice", {})
    if (
        Path(slice_input.get("path", "")).resolve() != slice_path.resolve()
        or slice_input.get("sha256_normalized_lf") != slice_sha256
    ):
        raise InputContractError("Criterion-A summary references a different frozen slice")

    execution = json.loads(execution_summary_path.read_text(encoding="utf-8"))
    if (
        execution.get("status") != "CRITERION_A_BASELINE_EXECUTION_COMPLETE_ANALYSIS_PENDING"
        or execution.get("discovery_pairs_executed") != 12
        or execution.get("holdout_pairs_executed") != 0
        or execution.get("frozen_interval_frames") != 596
    ):
        raise InputContractError("Criterion-A execution summary is absent or incomplete")

    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if (
        provenance.get("source_sha") != PINNED_SOURCE_SHA
        or provenance.get("config_sha256") != T1_CONFIG_SHA256
        or provenance.get("checkpoint_sha256") != T1_CHECKPOINT_SHA256
        or provenance.get("patch_sha256_canonical_lf") != PATCH_SHA256_CANONICAL_LF
        or provenance.get("holdout_pairs_executed") != 0
    ):
        raise InputContractError("Criterion-A provenance differs from the exact model contract")
    if provenance.get("patched_file_sha256") != PATCHED_FILE_SHA256:
        raise InputContractError("Criterion-A patched-file hashes differ from accepted instrumentation")
    return summary, provenance


def read_boxes(path: Path) -> np.ndarray:
    rows = []
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        fields = line.replace("\t", ",").split(",")
        if len(fields) < 4:
            fields = line.split()
        rows.append([float(value) for value in fields[:4]])
    result = np.asarray(rows, dtype=np.float64)
    if result.ndim != 2 or result.shape[1] != 4:
        raise InputContractError(f"Invalid discovery GT at {path}: {result.shape}")
    return result


def read_rgb(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise InputContractError(f"Could not read discovery image: {path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def inclusive_iou(prediction: np.ndarray, ground_truth: np.ndarray) -> float:
    pred = np.asarray(prediction, dtype=np.float64)
    gt = np.asarray(ground_truth, dtype=np.float64)
    top_left = np.maximum(pred[:2], gt[:2])
    bottom_right = np.minimum(pred[:2] + pred[2:] - 1.0, gt[:2] + gt[2:] - 1.0)
    size = np.maximum(bottom_right - top_left + 1.0, 0.0)
    intersection = float(size[0] * size[1])
    union = float(pred[2] * pred[3] + gt[2] * gt[3] - intersection)
    if union <= 0.0:
        raise InputContractError(f"Non-positive IoU union: pred={pred} gt={gt}")
    return intersection / union


def inclusive_center_error(prediction: np.ndarray, ground_truth: np.ndarray) -> float:
    pred = np.asarray(prediction, dtype=np.float64)
    gt = np.asarray(ground_truth, dtype=np.float64)
    pred_center = pred[:2] + 0.5 * (pred[2:] - 1.0)
    gt_center = gt[:2] + 0.5 * (gt[2:] - 1.0)
    return float(np.sqrt(np.square(pred_center - gt_center).sum()))


def configure_diagnostics(tracker, enabled: bool, ablation: str = "none") -> None:
    tracker.stage4a_diagnostics_enabled = bool(enabled)
    tracker.stage4a_ablation = ablation
    tracker.stage4a_diagnostic_records = []
    tracker.network.configure_stage4a_diagnostics(enabled=enabled, ablation=ablation)


def find_tracker_record(records: list[dict]) -> dict:
    matches = [record for record in records if record.get("record_type") == "tracker_frame"]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one tracker_frame diagnostic record, got {len(matches)}")
    return matches[0]


def validate_diagnostic_records(records: list[dict], mode: str) -> tuple[list[dict], dict]:
    tracker_record = find_tracker_record(records)
    mrm_records = [record for record in records if record.get("record_type") == "mrm"]
    if [record.get("mrm_id") for record in mrm_records] != [f"MRM{i}" for i in range(1, 7)]:
        raise RuntimeError(f"Diagnostic MRM order/count mismatch for {mode}")
    if tracker_record.get("ablation_control") != mode:
        raise RuntimeError(f"Tracker diagnostic selector mismatch for {mode}")
    expected_selected = set(MODE_MEMBERS.get(mode, ()))
    for index, record in enumerate(mrm_records, start=1):
        if record.get("ablation_control") != mode:
            raise RuntimeError(f"MRM diagnostic selector mismatch for {mode}/MRM{index}")
        if record.get("physical_skip") is not False:
            raise RuntimeError(f"physical_skip must remain false for {mode}/MRM{index}")
        if record.get("all_retriever_and_mlp_compute_executed") is not True:
            raise RuntimeError(f"MRM compute was not fully executed for {mode}/MRM{index}")
        expected_bypass = index in expected_selected
        if bool(record.get("whole_mrm_bypass_applied")) != expected_bypass:
            raise RuntimeError(f"Whole-MRM control mismatch for {mode}/MRM{index}")
        if bool(record.get("zero_residual_applied")) != expected_bypass:
            raise RuntimeError(f"Residual-control marker mismatch for {mode}/MRM{index}")
    return mrm_records, tracker_record


def clone_state_value(value):
    if isinstance(value, torch.Tensor):
        return value.detach().clone()
    if isinstance(value, np.ndarray):
        return value.copy()
    if isinstance(value, dict):
        return {key: clone_state_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clone_state_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(clone_state_value(item) for item in value)
    if isinstance(value, frozenset):
        return frozenset(clone_state_value(item) for item in value)
    if isinstance(value, set):
        return {clone_state_value(item) for item in value}
    if value is None or isinstance(value, (bool, int, float, str, bytes)):
        return value
    raise TypeError(f"Unsupported transient state type: {type(value)!r}")


def capture_tracker_state(tracker) -> dict:
    encoder = tracker.network.encoder
    retriever_state = []
    for mrm in encoder.mrm:
        retriever = mrm.retriever
        retriever_state.append(
            {
                "capture_enabled": clone_state_value(retriever._stage4a_capture_enabled),
                "zero_template_index": clone_state_value(retriever._stage4a_zero_template_index),
                "capture": clone_state_value(retriever._stage4a_capture),
            }
        )
    return {
        "tracker": {
            "state": clone_state_value(tracker.state),
            "frame_id": int(tracker.frame_id),
            "template_list": clone_state_value(tracker.template_list),
            "cache": clone_state_value(tracker.cache),
            "spike_rate_dict_temp": clone_state_value(tracker.spike_rate_dict_temp),
            "last_template_refresh_frame": int(tracker.last_template_refresh_frame),
            "window_penalty": bool(tracker.window_penalty),
            "stage4a_diagnostics_enabled": bool(tracker.stage4a_diagnostics_enabled),
            "stage4a_ablation": str(tracker.stage4a_ablation),
            "stage4a_log_path": str(tracker.stage4a_log_path),
            "stage4a_diagnostic_records": clone_state_value(
                tracker.stage4a_diagnostic_records
            ),
        },
        "network": {
            "training": bool(tracker.network.training),
            "current_image_idx": int(tracker.network.current_image_idx),
            # Captured even when save_sfr=False; it is explicit model frame state.
            "spike_rate_dict": clone_state_value(tracker.network.spike_rate_dict),
        },
        "encoder": {
            "training": bool(encoder.training),
            "diagnostics_enabled": bool(encoder._stage4a_diagnostics_enabled),
            "ablation": str(encoder._stage4a_ablation),
            "ablation_indices": clone_state_value(encoder._stage4a_ablation_indices),
            "control_kind": str(encoder._stage4a_control_kind),
            "template_index": clone_state_value(encoder._stage4a_template_index),
            "forward_id": int(encoder._stage4a_forward_id),
            "current_records": clone_state_value(encoder._stage4a_current_records),
            "diagnostic_records": clone_state_value(encoder._stage4a_diagnostic_records),
            "retrievers": retriever_state,
        },
        "template_encoder": {
            "training": bool(tracker.encoder_temp.training),
            "current_image_idx": int(tracker.encoder_temp.current_image_idx),
            "spike_rate_dict_temp": clone_state_value(
                tracker.encoder_temp.spike_rate_dict_temp
            ),
        },
        "rng": {
            "python": clone_state_value(random.getstate()),
            "numpy": clone_state_value(np.random.get_state()),
            "torch_cpu": torch.get_rng_state().clone(),
            "torch_cuda_all": [state.clone() for state in torch.cuda.get_rng_state_all()],
        },
    }


def restore_tracker_state(tracker, snapshot: dict) -> None:
    state = clone_state_value(snapshot)
    tracker_state = state["tracker"]
    tracker.state = tracker_state["state"]
    tracker.frame_id = tracker_state["frame_id"]
    tracker.template_list = tracker_state["template_list"]
    tracker.cache = tracker_state["cache"]
    tracker.spike_rate_dict_temp = tracker_state["spike_rate_dict_temp"]
    tracker.last_template_refresh_frame = tracker_state["last_template_refresh_frame"]
    tracker.window_penalty = tracker_state["window_penalty"]
    tracker.stage4a_diagnostics_enabled = tracker_state["stage4a_diagnostics_enabled"]
    tracker.stage4a_ablation = tracker_state["stage4a_ablation"]
    tracker.stage4a_log_path = tracker_state["stage4a_log_path"]
    tracker.stage4a_diagnostic_records = tracker_state["stage4a_diagnostic_records"]

    network_state = state["network"]
    tracker.network.train(network_state["training"])
    tracker.network.current_image_idx = network_state["current_image_idx"]
    tracker.network.spike_rate_dict = network_state["spike_rate_dict"]

    encoder = tracker.network.encoder
    encoder_state = state["encoder"]
    encoder.train(encoder_state["training"])
    encoder._stage4a_diagnostics_enabled = encoder_state["diagnostics_enabled"]
    encoder._stage4a_ablation = encoder_state["ablation"]
    encoder._stage4a_ablation_indices = encoder_state["ablation_indices"]
    encoder._stage4a_control_kind = encoder_state["control_kind"]
    encoder._stage4a_template_index = encoder_state["template_index"]
    encoder._stage4a_forward_id = encoder_state["forward_id"]
    encoder._stage4a_current_records = encoder_state["current_records"]
    encoder._stage4a_diagnostic_records = encoder_state["diagnostic_records"]
    for mrm, retriever_state in zip(encoder.mrm, encoder_state["retrievers"]):
        retriever = mrm.retriever
        retriever._stage4a_capture_enabled = retriever_state["capture_enabled"]
        retriever._stage4a_zero_template_index = retriever_state["zero_template_index"]
        retriever._stage4a_capture = retriever_state["capture"]

    template_state = state["template_encoder"]
    tracker.encoder_temp.train(template_state["training"])
    tracker.encoder_temp.current_image_idx = template_state["current_image_idx"]
    tracker.encoder_temp.spike_rate_dict_temp = template_state["spike_rate_dict_temp"]

    random.setstate(state["rng"]["python"])
    np.random.set_state(state["rng"]["numpy"])
    torch.set_rng_state(state["rng"]["torch_cpu"])
    torch.cuda.set_rng_state_all(state["rng"]["torch_cuda_all"])


def _hash_state_value(digest, value) -> None:
    if isinstance(value, torch.Tensor):
        tensor = value.detach().cpu().contiguous()
        digest.update(b"torch|")
        digest.update(str(tensor.dtype).encode("ascii"))
        digest.update(json.dumps(list(tensor.shape), separators=(",", ":")).encode("ascii"))
        digest.update(tensor.numpy().tobytes())
    elif isinstance(value, np.ndarray):
        array = np.ascontiguousarray(value)
        digest.update(b"numpy|")
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode("ascii"))
        digest.update(array.tobytes())
    elif isinstance(value, dict):
        digest.update(b"dict{")
        for key in sorted(value, key=lambda item: str(item)):
            _hash_state_value(digest, key)
            _hash_state_value(digest, value[key])
        digest.update(b"}")
    elif isinstance(value, list):
        digest.update(b"list[")
        for item in value:
            _hash_state_value(digest, item)
        digest.update(b"]")
    elif isinstance(value, tuple):
        digest.update(b"tuple(")
        for item in value:
            _hash_state_value(digest, item)
        digest.update(b")")
    elif isinstance(value, (set, frozenset)):
        digest.update(b"set{")
        for item in sorted(value, key=repr):
            _hash_state_value(digest, item)
        digest.update(b"}")
    elif isinstance(value, bytes):
        digest.update(b"bytes|")
        digest.update(value)
    elif value is None:
        digest.update(b"none")
    elif isinstance(value, bool):
        digest.update(b"bool|1" if value else b"bool|0")
    elif isinstance(value, int):
        digest.update(f"int|{value}".encode("ascii"))
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise RuntimeError("Non-finite value in tracker snapshot")
        digest.update(f"float|{value.hex()}".encode("ascii"))
    elif isinstance(value, str):
        encoded = value.encode("utf-8")
        digest.update(f"str|{len(encoded)}|".encode("ascii"))
        digest.update(encoded)
    else:
        raise TypeError(f"Unsupported snapshot hash type: {type(value)!r}")


def snapshot_sha256(snapshot: dict) -> str:
    digest = hashlib.sha256(b"stage4b-tracker-state-snapshot-v1|")
    _hash_state_value(digest, snapshot)
    return digest.hexdigest()


def restore_and_verify(tracker, snapshot: dict, expected_sha256: str, context: str) -> str:
    restore_tracker_state(tracker, snapshot)
    observed = snapshot_sha256(capture_tracker_state(tracker))
    if observed != expected_sha256:
        raise RuntimeError(
            "STAGE4B_INCOMPLETE_ENVIRONMENT_OR_STATE_SNAPSHOT: "
            f"restore hash mismatch for {context}: {observed} != {expected_sha256}"
        )
    return observed


def atomic_temp_path(final_path: Path) -> Path:
    return final_path.with_name(final_path.name + f".partial.{os.getpid()}")


def prepare_csv(final_path: Path, fieldnames: list[str], rows: list[dict]) -> Path:
    temp_path = atomic_temp_path(final_path)
    if temp_path.exists():
        raise FileExistsError(f"Current-process partial output exists: {temp_path}")
    with temp_path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        stream.flush()
        os.fsync(stream.fileno())
    return temp_path


def prepare_json(final_path: Path, payload: object) -> Path:
    temp_path = atomic_temp_path(final_path)
    if temp_path.exists():
        raise FileExistsError(f"Current-process partial output exists: {temp_path}")
    serialized = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with temp_path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(serialized)
        stream.flush()
        os.fsync(stream.fileno())
    return temp_path


def timing_aggregate_rows(timing_values: dict[tuple[str, str], dict[str, list[float]]]) -> list[dict]:
    metrics = (
        "retriever_latency_ms",
        "mlp_latency_ms",
        "total_mrm_compute_latency_ms",
        "diagnostic_norm_fingerprint_overhead_ms",
        "total_instrumented_mrm_latency_ms",
        "total_tracker_model_forward_ms",
    )
    rows = []
    for mode, _ in LOCKED_MODES:
        for mrm_number in range(1, 7):
            mrm_id = f"MRM{mrm_number}"
            values_by_metric = timing_values[(mode, mrm_id)]
            row = {
                "mode": mode,
                "test_order": MODE_ORDER[mode],
                "mrm_id": mrm_id,
                "mrm_code_index": mrm_number - 1,
                "mrm_members_controlled": ";".join(str(value) for value in MODE_MEMBERS[mode]),
                "frame_records": len(values_by_metric[metrics[0]]),
                "physical_skip": False,
                "timing_role": "SYNCHRONIZED_CHARACTERIZATION_ONLY",
            }
            for metric in metrics:
                values = values_by_metric[metric]
                if not values:
                    raise RuntimeError(f"No timing records for {mode}/{mrm_id}/{metric}")
                prefix = metric.removesuffix("_ms")
                row[f"{prefix}_mean_ms"] = statistics.fmean(values)
                row[f"{prefix}_median_ms"] = statistics.median(values)
                row[f"{prefix}_std_population_ms"] = statistics.pstdev(values)
                row[f"{prefix}_min_ms"] = min(values)
                row[f"{prefix}_max_ms"] = max(values)
            rows.append(row)
    return rows


def main() -> None:
    args = parse_args()
    for name in (
        "source_root", "dataset_root", "slice_csv", "config", "checkpoint",
        "baseline_csv", "criterion_a_summary", "external_root", "artifact_root",
    ):
        setattr(args, name, getattr(args, name).resolve())
    for path in (
        args.source_root, args.dataset_root, args.slice_csv, args.config,
        args.checkpoint, args.baseline_csv, args.criterion_a_summary,
        args.external_root, args.artifact_root,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    if not args.artifact_root.is_dir() or not args.external_root.is_dir():
        raise NotADirectoryError("Artifact and external roots must already exist")

    repo_outputs = {name: args.artifact_root / name for name in REPO_OUTPUT_NAMES}
    external_phase_root = args.external_root / "criterionB"
    raw_mrm_path = external_phase_root / "criterionB_raw_mrm.jsonl"
    preexisting = [path for path in [*repo_outputs.values(), raw_mrm_path] if path.exists()]
    if preexisting:
        raise FileExistsError(f"Criterion-B output already exists; refusing reuse: {preexisting}")

    discovery, intervals_by_sequence, slice_hashes = parse_and_validate_slice(args.slice_csv)
    baseline, baseline_sha = load_baseline_frames(args.baseline_csv, discovery)
    criterion_a_execution_summary = args.artifact_root / "criterionA_execution_summary.json"
    provenance_path = args.artifact_root / "provenance_environment.json"
    for path in (criterion_a_execution_summary, provenance_path):
        if not path.is_file():
            raise FileNotFoundError(path)
    criterion_a_summary, criterion_a_provenance = validate_criterion_a_gate(
        args.criterion_a_summary,
        criterion_a_execution_summary,
        provenance_path,
        args.baseline_csv,
        baseline_sha,
        args.slice_csv,
        slice_hashes["normalized_lf_sha256"],
    )

    source_sha = git_output(args.source_root, "rev-parse", "HEAD")
    if source_sha != PINNED_SOURCE_SHA:
        raise InputContractError(f"Wrong SpikeTrack source SHA: {source_sha}")
    status_lines = [
        line for line in git_output(args.source_root, "status", "--porcelain").splitlines() if line
    ]
    changed_paths = sorted(line[3:].replace("\\", "/") for line in status_lines)
    if changed_paths != sorted(PATCHED_PATHS):
        raise InputContractError(f"Patched SpikeTrack worktree has unexpected paths: {changed_paths}")
    observed_patched_hashes = {
        path: sha256_file(args.source_root / path) for path in PATCHED_PATHS
    }
    if observed_patched_hashes != PATCHED_FILE_SHA256:
        raise InputContractError("Accepted diagnostic patched-file SHA-256 mismatch")
    if sha256_file(args.config) != T1_CONFIG_SHA256:
        raise InputContractError("T1 config SHA-256 mismatch")
    if sha256_file(args.checkpoint) != T1_CHECKPOINT_SHA256:
        raise InputContractError("T1 checkpoint SHA-256 mismatch")

    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    os.chdir(args.source_root)
    sys.path.insert(0, str(args.source_root))
    global torch
    import torch

    from lib.config.spiketrack.config import cfg, update_config_from_file
    from lib.test.evaluation.otbdataset import OTBDataset
    from lib.test.tracker.spiketrack_inf import SpikeTrack

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)
    if not torch.cuda.is_available():
        raise RuntimeError("Authorized local CUDA GPU is unavailable")
    if (
        os.environ.get("CUBLAS_WORKSPACE_CONFIG") != ":4096:8"
        or not torch.are_deterministic_algorithms_enabled()
        or not torch.backends.cudnn.deterministic
        or torch.backends.cudnn.benchmark
    ):
        raise RuntimeError("Exact deterministic settings were not established")

    update_config_from_file(str(args.config))
    if (
        cfg.MODEL.ENCODER.TYPE != "Efficient_Spiking_Transformer_s"
        or cfg.TEST.SEARCH_SIZE != 256
        or cfg.TEST.NUM_TEMPLATES != 1
    ):
        raise InputContractError("Resolved model is not exact SpikeTrack-S256-T1")
    params = SimpleNamespace(
        cfg=cfg,
        template_factor=cfg.TEST.TEMPLATE_FACTOR,
        template_size=cfg.TEST.TEMPLATE_SIZE,
        search_factor=cfg.TEST.SEARCH_FACTOR,
        search_size=cfg.TEST.SEARCH_SIZE,
        save_all_boxes=False,
        debug=0,
        yaml_name=args.config.stem,
        stage4a_diagnostics=False,
        stage4a_ablation="none",
        stage4a_log_path="",
    )

    official_info = {item["name"]: item for item in OTBDataset._get_sequence_info_list(None)}
    discovery_sequences = frozenset(intervals_by_sequence)
    missing_metadata = sorted(discovery_sequences - set(official_info))
    if missing_metadata:
        raise InputContractError(
            f"Discovery sequences absent from pinned OTB metadata: {missing_metadata}"
        )

    tracker = SpikeTrack(params, dataset_name="otb", checkpoint_path=str(args.checkpoint), save_sfr=False)
    if tracker.num_template != 1:
        raise InputContractError("Tracker runtime is not T1")

    # A prior interrupted run may have left only a uniquely named partial file;
    # final named outputs were checked above and are still refused.
    external_phase_root.mkdir(parents=True, exist_ok=True)
    raw_temp_path = atomic_temp_path(raw_mrm_path)
    if raw_temp_path.exists():
        raise FileExistsError(f"Current-process raw partial output exists: {raw_temp_path}")

    mode_rows: list[dict] = []
    parity_rows: list[dict] = []
    manifest_rows: list[dict] = []
    timing_values: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    raw_line_count = 0
    total_started = time.perf_counter()
    max_float_diff = 0.0
    max_score_diff = 0.0
    max_confidence_diff = 0.0
    baseline_integer_exact = True
    interval_number = 0
    total_intervals = sum(len(items) for items in intervals_by_sequence.values())

    def write_raw_records(
        raw_stream,
        records: list[dict],
        interval: IntervalSpec,
        frame_index: int,
        branch_kind: str,
        mode: str,
    ) -> None:
        nonlocal raw_line_count
        for record in records:
            enriched = dict(record)
            enriched.update(
                {
                    "pair_id": interval.pair_id,
                    "side": interval.side,
                    "sequence": interval.sequence,
                    "evaluator_frame_index": frame_index,
                    "branch_kind": branch_kind,
                    "criterion_b_mode": mode,
                    "frozen_interval_start": interval.start,
                    "frozen_interval_end": interval.end,
                }
            )
            raw_stream.write(json.dumps(enriched, sort_keys=True, allow_nan=False) + "\n")
            raw_line_count += 1

    def run_tracked_branch(
        raw_stream,
        interval: IntervalSpec,
        frame_paths: list[Path],
        ground_truth: np.ndarray,
        mode: str,
        branch_kind: str,
    ) -> tuple[list[dict], dict, tuple[int, int]]:
        nonlocal max_float_diff, max_score_diff, max_confidence_diff, baseline_integer_exact
        configure_diagnostics(tracker, True, mode)
        produced_rows: list[dict] = []
        branch_float_max = 0.0
        branch_score_max = 0.0
        branch_confidence_max = 0.0
        branch_integer_exact = True
        raw_start = raw_line_count + 1
        first_tracked_frame = max(interval.start, 2)
        for frame_index in range(first_tracked_frame, interval.end + 1):
            output, _, _ = tracker.track(read_rgb(frame_paths[frame_index - 1]), {})
            records = tracker.consume_stage4a_diagnostic_records()
            mrm_records, tracker_record = validate_diagnostic_records(records, mode)
            write_raw_records(
                raw_stream, records, interval, frame_index, branch_kind, mode
            )
            float_box = np.asarray(output["target_bbox"], dtype=np.float64)
            int_box = float_box.astype(np.int64)
            gt_box = ground_truth[frame_index - 1]
            baseline_frame = baseline[(interval.pair_id, interval.side, frame_index)]
            gt_diff = float(np.max(np.abs(gt_box - baseline_frame["gt_box"])))
            if gt_diff > PARITY_TOLERANCE:
                raise RuntimeError(
                    f"Discovery GT differs from Criterion-A row at {interval.pair_id}/"
                    f"{interval.side}/{frame_index}: {gt_diff}"
                )
            if branch_kind == "baseline":
                float_diff = float(np.max(np.abs(float_box - baseline_frame["float_box"])))
                integer_exact = bool(np.array_equal(int_box, baseline_frame["int_box"]))
                score_diff = abs(
                    float(tracker_record["score_map_max"]) - baseline_frame["score_map_max"]
                )
                confidence_diff = abs(
                    float(tracker_record["confidence_score"])
                    - baseline_frame["confidence_score"]
                )
                branch_float_max = max(branch_float_max, float_diff)
                branch_score_max = max(branch_score_max, score_diff)
                branch_confidence_max = max(branch_confidence_max, confidence_diff)
                branch_integer_exact = branch_integer_exact and integer_exact
                max_float_diff = max(max_float_diff, float_diff)
                max_score_diff = max(max_score_diff, score_diff)
                max_confidence_diff = max(max_confidence_diff, confidence_diff)
                baseline_integer_exact = baseline_integer_exact and integer_exact
                # Fail immediately.  In particular, the first interval's clean
                # branch gates every mode branch in the run.
                if (
                    float_diff > PARITY_TOLERANCE
                    or score_diff > PARITY_TOLERANCE
                    or confidence_diff > PARITY_TOLERANCE
                    or not integer_exact
                ):
                    raise RuntimeError(
                        "STAGE4B_INCOMPLETE_ENVIRONMENT_OR_STATE_SNAPSHOT: "
                        f"baseline fork parity failed at {interval.pair_id}/{interval.side}/"
                        f"{frame_index}: float={float_diff}, score={score_diff}, "
                        f"confidence={confidence_diff}, integer_exact={integer_exact}"
                    )
            else:
                mode_iou = inclusive_iou(int_box, gt_box)
                produced_rows.append(
                    {
                        "pair_id": interval.pair_id,
                        "side": interval.side,
                        "sequence": interval.sequence,
                        "frame_index": frame_index,
                        "mode": mode,
                        "iou": mode_iou,
                        "physical_skip": False,
                        "baseline_iou": baseline_frame["iou"],
                        "contribution": baseline_frame["iou"] - mode_iou,
                        "pred_x_float": float_box[0],
                        "pred_y_float": float_box[1],
                        "pred_w_float": float_box[2],
                        "pred_h_float": float_box[3],
                        "pred_x_int": int_box[0],
                        "pred_y_int": int_box[1],
                        "pred_w_int": int_box[2],
                        "pred_h_int": int_box[3],
                        "gt_x": gt_box[0],
                        "gt_y": gt_box[1],
                        "gt_w": gt_box[2],
                        "gt_h": gt_box[3],
                        "iou_float": inclusive_iou(float_box, gt_box),
                        "failure": int(mode_iou < 0.5),
                        "success_at_0_5": int(mode_iou >= 0.5),
                        "center_error": inclusive_center_error(int_box, gt_box),
                        "score_map_max": tracker_record["score_map_max"],
                        "confidence_score": tracker_record["confidence_score"],
                        "model_forward_ms": tracker_record["total_tracker_model_forward_ms"],
                        "initialization_frame": False,
                        "evaluator_first_frame_override": False,
                        "branch_frame_executed": True,
                        "tracker_mode": "T1",
                        "ablation_control": mode,
                    }
                )
                for record in mrm_records:
                    key = (mode, record["mrm_id"])
                    for metric in (
                        "retriever_latency_ms", "mlp_latency_ms",
                        "total_mrm_compute_latency_ms",
                        "diagnostic_norm_fingerprint_overhead_ms",
                        "total_instrumented_mrm_latency_ms",
                        "total_tracker_model_forward_ms",
                    ):
                        timing_values[key][metric].append(float(record[metric]))

        return produced_rows, {
            "maximum_float_prediction_abs_diff": branch_float_max,
            "maximum_score_map_abs_diff": branch_score_max,
            "maximum_confidence_abs_diff": branch_confidence_max,
            "integer_prediction_exact": branch_integer_exact,
        }, (raw_start, raw_line_count)

    with raw_temp_path.open("x", encoding="utf-8", newline="\n") as raw_stream:
        sequence_names = sorted(intervals_by_sequence)
        for sequence_index, sequence_name in enumerate(sequence_names, start=1):
            if sequence_name not in discovery_sequences:
                raise HoldoutExposureError(args.slice_csv, sequence_name, 0)
            info = official_info[sequence_name]
            official_start = int(info["startFrame"])
            official_end = int(info["endFrame"])
            if official_start != 1:
                raise InputContractError(
                    f"Unsupported non-1 official start for {sequence_name}: {official_start}"
                )
            intervals = intervals_by_sequence[sequence_name]
            max_frame = max(item.end for item in intervals)
            if max_frame > official_end:
                raise InputContractError(f"Frozen frame exceeds official end for {sequence_name}")
            effective_info = dict(info)
            effective_info.update(DISCOVERY_SOURCE_ALIASES.get(sequence_name, {}))
            image_dir = args.dataset_root / effective_info["path"]
            gt_path = args.dataset_root / effective_info["anno_path"]
            # Only a positively allowlisted discovery sequence reaches these
            # path constructions; no HOLDOUT sequence is represented here.
            ground_truth = read_boxes(gt_path)
            if len(ground_truth) < max_frame:
                raise InputContractError(
                    f"Discovery GT truncated for {sequence_name}: {len(ground_truth)} < {max_frame}"
                )
            frame_paths = [
                image_dir / f"{frame_index:0{int(info['nz'])}d}.{info['ext']}"
                for frame_index in range(1, max_frame + 1)
            ]
            missing = [str(path) for path in frame_paths if not path.is_file()]
            if missing:
                raise InputContractError(
                    f"Discovery source-integrity defect {sequence_name}: {missing[:3]}"
                )

            configure_diagnostics(tracker, False, "none")
            tracker.initialize(read_rgb(frame_paths[0]), {"init_bbox": ground_truth[0].tolist()})
            current_frame = 1
            print(
                f"PROGRESS sequence {sequence_index}/{len(sequence_names)} {sequence_name} "
                f"intervals={len(intervals)} through={max_frame}",
                flush=True,
            )

            for interval in intervals:
                interval_number += 1
                while current_frame < interval.start - 1:
                    if tracker.stage4a_diagnostics_enabled:
                        configure_diagnostics(tracker, False, "none")
                    current_frame += 1
                    tracker.track(read_rgb(frame_paths[current_frame - 1]), {})
                if current_frame != max(1, interval.start - 1):
                    raise RuntimeError(
                        f"Prefix position mismatch for {interval.pair_id}/{interval.side}: "
                        f"at {current_frame}, need {interval.start - 1}"
                    )

                baseline_init = baseline.get((interval.pair_id, interval.side, 1))
                initialization_float_diff = 0.0
                initialization_integer_exact = True
                if interval.start == 1:
                    if baseline_init is None:
                        raise RuntimeError(f"Missing initialization baseline for {interval}")
                    initialization_gt_diff = float(
                        np.max(np.abs(ground_truth[0] - baseline_init["gt_box"]))
                    )
                    if initialization_gt_diff > PARITY_TOLERANCE:
                        raise RuntimeError(
                            f"Discovery initialization GT differs from Criterion A for {interval}"
                        )
                    tracker_init = np.asarray(tracker.state, dtype=np.float64)
                    initialization_float_diff = float(
                        np.max(np.abs(tracker_init - baseline_init["float_box"]))
                    )
                    initialization_integer_exact = bool(
                        np.array_equal(tracker_init.astype(np.int64), baseline_init["int_box"])
                    )
                    if (
                        initialization_float_diff > PARITY_TOLERANCE
                        or not initialization_integer_exact
                    ):
                        raise RuntimeError(
                            "STAGE4B_INCOMPLETE_ENVIRONMENT_OR_STATE_SNAPSHOT: "
                            f"official initialization parity failed for {interval.pair_id}/"
                            f"{interval.side}"
                        )
                    max_float_diff = max(max_float_diff, initialization_float_diff)
                    baseline_integer_exact = baseline_integer_exact and initialization_integer_exact

                start_snapshot = capture_tracker_state(tracker)
                start_hash = snapshot_sha256(start_snapshot)
                restored_hash = restore_and_verify(
                    tracker, start_snapshot, start_hash,
                    f"{interval.pair_id}/{interval.side}/baseline",
                )
                baseline_rows, baseline_parity, _ = run_tracked_branch(
                    raw_stream, interval, frame_paths, ground_truth, "none", "baseline"
                )
                if baseline_rows:
                    raise RuntimeError("Baseline branch unexpectedly emitted mode rows")
                baseline_parity["maximum_float_prediction_abs_diff"] = max(
                    baseline_parity["maximum_float_prediction_abs_diff"],
                    initialization_float_diff,
                )
                baseline_parity["integer_prediction_exact"] = (
                    baseline_parity["integer_prediction_exact"]
                    and initialization_integer_exact
                )
                baseline_end_snapshot = capture_tracker_state(tracker)
                baseline_end_hash = snapshot_sha256(baseline_end_snapshot)
                interval_parity_rows: list[dict] = [
                    {
                        "pair_id": interval.pair_id,
                        "side": interval.side,
                        "sequence": sequence_name,
                        "interval_start": interval.start,
                        "interval_end": interval.end,
                        "branch_kind": "baseline",
                        "mode": "none",
                        "snapshot_frame": max(1, interval.start - 1),
                        "start_snapshot_sha256": start_hash,
                        "restored_start_snapshot_sha256": restored_hash,
                        "start_restore_exact": True,
                        "baseline_end_snapshot_sha256": baseline_end_hash,
                        "continuation_restored_snapshot_sha256": "",
                        "continuation_restore_exact": "",
                        "maximum_float_prediction_abs_diff": baseline_parity[
                            "maximum_float_prediction_abs_diff"
                        ],
                        "maximum_score_map_abs_diff": baseline_parity[
                            "maximum_score_map_abs_diff"
                        ],
                        "maximum_confidence_abs_diff": baseline_parity[
                            "maximum_confidence_abs_diff"
                        ],
                        "integer_prediction_exact": baseline_parity[
                            "integer_prediction_exact"
                        ],
                        "tolerance": PARITY_TOLERANCE,
                        "official_initialization_zero_contribution": interval.start == 1,
                        "captured_state": SNAPSHOT_CAPTURE_DESCRIPTION,
                        "status": "PASS",
                    }
                ]
                print(
                    f"PROGRESS interval {interval_number}/{total_intervals} "
                    f"{interval.pair_id}/{interval.side} {sequence_name} "
                    f"{interval.start}-{interval.end} baseline_parity=PASS",
                    flush=True,
                )

                for mode_index, (mode, members) in enumerate(LOCKED_MODES, start=1):
                    mode_restore_hash = restore_and_verify(
                        tracker, start_snapshot, start_hash,
                        f"{interval.pair_id}/{interval.side}/{mode}",
                    )
                    raw_start = raw_line_count + 1
                    branch_rows, _, raw_bounds = run_tracked_branch(
                        raw_stream, interval, frame_paths, ground_truth, mode, "mode"
                    )
                    if interval.start == 1:
                        init = baseline[(interval.pair_id, interval.side, 1)]
                        init_row = {
                            "pair_id": interval.pair_id,
                            "side": interval.side,
                            "sequence": interval.sequence,
                            "frame_index": 1,
                            "mode": mode,
                            "iou": init["iou"],
                            "physical_skip": False,
                            "baseline_iou": init["iou"],
                            "contribution": 0.0,
                            "pred_x_float": init["float_box"][0],
                            "pred_y_float": init["float_box"][1],
                            "pred_w_float": init["float_box"][2],
                            "pred_h_float": init["float_box"][3],
                            "pred_x_int": init["int_box"][0],
                            "pred_y_int": init["int_box"][1],
                            "pred_w_int": init["int_box"][2],
                            "pred_h_int": init["int_box"][3],
                            "gt_x": init["gt_box"][0],
                            "gt_y": init["gt_box"][1],
                            "gt_w": init["gt_box"][2],
                            "gt_h": init["gt_box"][3],
                            "iou_float": init["iou_float"],
                            "failure": int(init["failure"]),
                            "success_at_0_5": int(init["success_at_0_5"]),
                            "center_error": init["center_error"],
                            "score_map_max": "",
                            "confidence_score": "",
                            "model_forward_ms": "",
                            "initialization_frame": True,
                            "evaluator_first_frame_override": True,
                            "branch_frame_executed": False,
                            "tracker_mode": "T1",
                            "ablation_control": mode,
                        }
                        branch_rows.insert(0, init_row)
                    expected_count = interval.end - interval.start + 1
                    if len(branch_rows) != expected_count:
                        raise RuntimeError(
                            f"Mode coverage mismatch for {interval.pair_id}/{interval.side}/{mode}"
                        )
                    mode_rows.extend(branch_rows)
                    interval_parity_rows.append(
                        {
                            "pair_id": interval.pair_id,
                            "side": interval.side,
                            "sequence": sequence_name,
                            "interval_start": interval.start,
                            "interval_end": interval.end,
                            "branch_kind": "mode",
                            "mode": mode,
                            "snapshot_frame": max(1, interval.start - 1),
                            "start_snapshot_sha256": start_hash,
                            "restored_start_snapshot_sha256": mode_restore_hash,
                            "start_restore_exact": True,
                            "baseline_end_snapshot_sha256": baseline_end_hash,
                            "continuation_restored_snapshot_sha256": "",
                            "continuation_restore_exact": "",
                            "maximum_float_prediction_abs_diff": "",
                            "maximum_score_map_abs_diff": "",
                            "maximum_confidence_abs_diff": "",
                            "integer_prediction_exact": "",
                            "tolerance": PARITY_TOLERANCE,
                            "official_initialization_zero_contribution": interval.start == 1,
                            "captured_state": SNAPSHOT_CAPTURE_DESCRIPTION,
                            "status": "PASS",
                        }
                    )
                    manifest_rows.append(
                        {
                            "pair_id": interval.pair_id,
                            "side": interval.side,
                            "sequence": sequence_name,
                            "interval_start": interval.start,
                            "interval_end": interval.end,
                            "mode": mode,
                            "test_order": MODE_ORDER[mode],
                            "mrm_members": ";".join(str(value) for value in members),
                            "physical_skip": False,
                            "source_row_sha256_canonical_lf": interval.source_row_sha256,
                            "start_snapshot_sha256": start_hash,
                            "restored_start_snapshot_sha256": mode_restore_hash,
                            "start_restore_exact": True,
                            "interval_output_frames": len(branch_rows),
                            "tracked_branch_frames": interval.end - max(interval.start, 2) + 1,
                            "official_initialization_frames_zero_contribution": int(
                                interval.start == 1
                            ),
                            "raw_jsonl_first_line": raw_start,
                            "raw_jsonl_last_line": raw_bounds[1],
                            "raw_jsonl_external_path": str(raw_mrm_path),
                            "status": "EXECUTED_STAGE4B_CRITERION_B",
                        }
                    )
                    print(
                        f"PROGRESS interval {interval_number}/{total_intervals} "
                        f"mode {mode_index}/9 {interval.pair_id}/{interval.side}/{mode} complete",
                        flush=True,
                    )

                continuation_hash = restore_and_verify(
                    tracker,
                    baseline_end_snapshot,
                    baseline_end_hash,
                    f"{interval.pair_id}/{interval.side}/continuation",
                )
                for row in interval_parity_rows:
                    row["continuation_restored_snapshot_sha256"] = continuation_hash
                    row["continuation_restore_exact"] = True
                parity_rows.extend(interval_parity_rows)
                current_frame = interval.end

            configure_diagnostics(tracker, False, "none")
            if current_frame != max_frame:
                raise RuntimeError(
                    f"Sequence prefix did not finish at maximum frozen frame for {sequence_name}"
                )
            print(
                f"PROGRESS sequence {sequence_index}/{len(sequence_names)} {sequence_name} complete",
                flush=True,
            )
        raw_stream.flush()
        os.fsync(raw_stream.fileno())

    expected_mode_rows = len(baseline) * len(LOCKED_MODES)
    if len(mode_rows) != expected_mode_rows:
        raise RuntimeError(f"Mode row count {len(mode_rows)} != expected {expected_mode_rows}")
    actual_mode_keys = {
        (row["mode"], row["pair_id"], row["side"], int(row["frame_index"]))
        for row in mode_rows
    }
    expected_mode_keys = {
        (mode, pair_id, side, frame)
        for mode, _ in LOCKED_MODES
        for pair_id, side, frame in baseline
    }
    if actual_mode_keys != expected_mode_keys:
        raise RuntimeError("Mode rows do not cover exactly nine modes over every baseline frame")
    if any(bool(row["physical_skip"]) for row in mode_rows):
        raise RuntimeError("A mode row reported physical_skip=true")
    if len(parity_rows) != total_intervals * (1 + len(LOCKED_MODES)):
        raise RuntimeError("State-snapshot parity branch count mismatch")
    if len(manifest_rows) != total_intervals * len(LOCKED_MODES):
        raise RuntimeError("Mode execution manifest branch count mismatch")

    mode_rows.sort(
        key=lambda row: (
            MODE_ORDER[row["mode"]], row["pair_id"], row["side"], int(row["frame_index"])
        )
    )
    parity_rows.sort(
        key=lambda row: (
            row["pair_id"], row["side"],
            0 if row["branch_kind"] == "baseline" else MODE_ORDER[row["mode"]],
        )
    )
    manifest_rows.sort(
        key=lambda row: (MODE_ORDER[row["mode"]], row["pair_id"], row["side"])
    )
    aggregate_rows = timing_aggregate_rows(timing_values)
    raw_sha = sha256_file(raw_temp_path)

    mode_fields = [
        "pair_id", "side", "sequence", "frame_index", "mode", "iou", "physical_skip",
        "baseline_iou", "contribution",
        "pred_x_float", "pred_y_float", "pred_w_float", "pred_h_float",
        "pred_x_int", "pred_y_int", "pred_w_int", "pred_h_int",
        "gt_x", "gt_y", "gt_w", "gt_h", "iou_float", "failure",
        "success_at_0_5", "center_error", "score_map_max", "confidence_score",
        "model_forward_ms", "initialization_frame", "evaluator_first_frame_override",
        "branch_frame_executed", "tracker_mode", "ablation_control",
    ]
    parity_fields = list(parity_rows[0])
    manifest_fields = list(manifest_rows[0])
    aggregate_fields = list(aggregate_rows[0])

    prepared: dict[Path, Path] = {}
    prepared[repo_outputs["state_snapshot_parity.csv"]] = prepare_csv(
        repo_outputs["state_snapshot_parity.csv"], parity_fields, parity_rows
    )
    prepared[repo_outputs["mode_per_frame_metrics.csv"]] = prepare_csv(
        repo_outputs["mode_per_frame_metrics.csv"], mode_fields, mode_rows
    )
    prepared[repo_outputs["mode_execution_manifest.csv"]] = prepare_csv(
        repo_outputs["mode_execution_manifest.csv"], manifest_fields, manifest_rows
    )
    prepared[repo_outputs["mode_module_timing_characterization.csv"]] = prepare_csv(
        repo_outputs["mode_module_timing_characterization.csv"], aggregate_fields, aggregate_rows
    )
    output_hashes = {
        final.name: sha256_file(temp) for final, temp in prepared.items()
    }
    elapsed = time.perf_counter() - total_started
    summary = {
        "status": "CRITERION_B_NINE_MODE_EXECUTION_COMPLETE_ANALYSIS_PENDING",
        "scope": "STAGE4B_DISCOVERY_CRITERION_B_ONLY",
        "criterion_a_gate": {
            "status": "PASS",
            "summary_path": str(args.criterion_a_summary),
            "summary_sha256": sha256_file(args.criterion_a_summary),
            "criterion_a_estimates": criterion_a_summary["criterion_a"].get("metrics"),
        },
        "discovery_pairs_executed": 12,
        "discovery_intervals_executed": total_intervals,
        "holdout_pairs_executed": 0,
        "holdout_outcomes_read": 0,
        "modes": [name for name, _ in LOCKED_MODES],
        "physical_skip": False,
        "state_snapshot_parity": {
            "status": "PASS",
            "hash_algorithm": "SHA-256 over stage4b-tracker-state-snapshot-v1 canonical type stream",
            "captured_state": SNAPSHOT_CAPTURE_DESCRIPTION,
            "start_restore_branches": len(parity_rows),
            "continuation_restore_intervals": total_intervals,
        },
        "baseline_branch_parity": {
            "status": "PASS",
            "tolerance": PARITY_TOLERANCE,
            "maximum_float_prediction_abs_diff": max_float_diff,
            "maximum_score_map_abs_diff": max_score_diff,
            "maximum_confidence_abs_diff": max_confidence_diff,
            "integer_prediction_exact": baseline_integer_exact,
            "reference": "Criterion-A uninterrupted baseline_per_frame_metrics.csv",
        },
        "row_counts": {
            "baseline_reference_frames": len(baseline),
            "mode_per_frame_metrics": len(mode_rows),
            "state_snapshot_parity": len(parity_rows),
            "mode_execution_manifest": len(manifest_rows),
            "mode_module_timing_characterization": len(aggregate_rows),
            "external_raw_jsonl_records": raw_line_count,
        },
        "input_hashes": {
            "source_sha": source_sha,
            "patch_sha256_canonical_lf": PATCH_SHA256_CANONICAL_LF,
            "patched_file_sha256": observed_patched_hashes,
            "config_sha256": sha256_file(args.config),
            "checkpoint_sha256": sha256_file(args.checkpoint),
            "frozen_slice_sha256_normalized_lf": slice_hashes["normalized_lf_sha256"],
            "baseline_csv_sha256": baseline_sha,
            "criterion_a_provenance_sha256": sha256_file(provenance_path),
        },
        "determinism": {
            "seed": args.seed,
            "CUBLAS_WORKSPACE_CONFIG": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
            "torch_deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
            "cudnn_deterministic": bool(torch.backends.cudnn.deterministic),
            "cudnn_benchmark": bool(torch.backends.cudnn.benchmark),
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "cudnn": torch.backends.cudnn.version(),
            "gpu": torch.cuda.get_device_name(torch.cuda.current_device()),
        },
        "accepted_nonmutating_discovery_aliases": DISCOVERY_SOURCE_ALIASES,
        "external_raw_mrm": {
            "path": str(raw_mrm_path),
            "sha256": raw_sha,
            "records": raw_line_count,
        },
        "output_hashes": output_hashes,
        "elapsed_seconds": elapsed,
        "next_action": "RUN_LOCKED_CRITERION_B_ANALYSIS_BEFORE_ANY_REFINEMENT",
        "refinement_executed": False,
        "stage4b_conclusion": None,
    }
    prepared[repo_outputs["criterionB_execution_summary.json"]] = prepare_json(
        repo_outputs["criterionB_execution_summary.json"], summary
    )

    # All scientific work and serialization succeeded before any final path is
    # published.  Each individual publication is atomic on its filesystem.
    os.replace(raw_temp_path, raw_mrm_path)
    for final_path in (
        repo_outputs["state_snapshot_parity.csv"],
        repo_outputs["mode_per_frame_metrics.csv"],
        repo_outputs["mode_execution_manifest.csv"],
        repo_outputs["mode_module_timing_characterization.csv"],
        repo_outputs["criterionB_execution_summary.json"],
    ):
        os.replace(prepared[final_path], final_path)
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
