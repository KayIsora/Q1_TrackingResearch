#!/usr/bin/env python3
"""Deterministic Stage-4B discovery-only statistical analysis.

This script is deliberately separate from tracker execution.  Its only outcome
inputs are a discovery-only T1 baseline per-frame CSV and, after Criterion A
passes, an optional discovery-only nine-mode per-frame CSV.  The frozen slice
contains metadata, not outcomes, and is used to validate every pair, sequence,
side, and inclusive frame bound.

Input contracts (additional columns are permitted):

* baseline CSV: ``pair_id,side,sequence,frame_index,iou,failure,center_error``;
* mode CSV: ``pair_id,side,sequence,frame_index,mode,iou,physical_skip``.

``pair_id`` MUST be the first CSV column.  Outcome rows are read through a
guarded unbuffered reader: it consumes only the first field, verifies that the
ID is one of the 12 discovery IDs, and only then consumes the outcome fields.
If a sealed hold-out ID is encountered, the reader stops before consuming the
rest of that row and emits ``STAGE4B_INVALID_HOLDOUT_EXPOSURE`` metadata.

Statistical serialization and formulas
--------------------------------------

All intervals use inclusive frozen bounds.  Frames are first averaged within
each pair/side, then the 12 pair effects receive equal weight:

* A/IoU = mean_pair(mean_control(IoU) - mean_primary(IoU));
* A/failure = mean_pair(mean_primary(IoU < 0.5) -
  mean_control(IoU < 0.5));
* B/contribution(side, mode) = mean_frame(IoU_baseline - IoU_ablation);
* B/interaction(mode) = mean_pair(contribution_primary -
  contribution_control).

The primary bootstrap samples the unique primary-sequence clusters with
replacement and retains every pair in each sampled cluster.  The required
sensitivity bootstrap samples connected source components, where pair nodes
are joined transitively when they share any primary or control sequence.  Both
use exactly 10,000 percentile resamples, seed 20260826, and linear-interpolated
2.5/97.5 percentiles.  Two-sided sign/tail p-values are
``min(1, 2*min((count(theta* <= 0)+1)/(B+1),
               (count(theta* >= 0)+1)/(B+1)))``.
The +1 is a deterministic Monte-Carlo correction.  Holm adjusted p-values are
the monotone step-down values across exactly the nine locked tests.

CSV floats use 12 significant digits, booleans use lower-case JSON spelling,
missing values are empty, pair/mode/group ordering is locked below, and JSON
is sorted and rejects NaN.  Sensitivity rows are descriptive only and never
alter the complete-set decisions.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import random
import sys
from typing import Callable, Iterable, Mapping, Sequence


BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20_260_826
FAMILYWISE_ALPHA = 0.05
IOU_FAILURE_CUTOFF = 0.5
CRITERION_A_IOU_THRESHOLD = 0.05
CRITERION_A_FAILURE_THRESHOLD = 0.10
CRITERION_B_INTERACTION_THRESHOLD = 0.02

# Hash after UTF-8 decode, BOM removal, and CRLF/CR normalization to LF.  This
# permits Git's platform line-ending checkout while still sealing slice content.
EXPECTED_FROZEN_SLICE_NORMALIZED_SHA256 = (
    "bc52bd7ec6277a76e6da69346a84a8f9d801e2fee9cd92634a60cf9f119ea11a"
)
EXPECTED_DISCOVERY_IDS = tuple(f"R3-D{i:02d}" for i in range(1, 13))
EXPECTED_HOLDOUT_IDS = tuple(f"R3-H{i:02d}" for i in range(1, 9))


@dataclass(frozen=True)
class ModeSpec:
    name: str
    test_order: int
    members: tuple[int, ...]

    @property
    def group_size(self) -> int:
        return len(self.members)

    @property
    def lower_mrm_index(self) -> int:
        return min(self.members)


# Names are the exact accepted instrumentation selectors in the frozen patch.
LOCKED_MODES = (
    ModeSpec("mrm1", 1, (1,)),
    ModeSpec("mrm2", 2, (2,)),
    ModeSpec("mrm3", 3, (3,)),
    ModeSpec("mrm4", 4, (4,)),
    ModeSpec("mrm5", 5, (5,)),
    ModeSpec("mrm6", 6, (6,)),
    ModeSpec("early", 7, (1, 2)),
    ModeSpec("middle", 8, (3, 4)),
    ModeSpec("late", 9, (5, 6)),
)
MODE_BY_NAME = {spec.name: spec for spec in LOCKED_MODES}


@dataclass(frozen=True)
class PairSpec:
    pair_id: str
    primary_sequence: str
    primary_start: int
    primary_end: int
    control_sequence: str
    control_start: int
    control_end: int
    broad_superclass: str
    ambiguity_level: str
    sensitivity_stratum: str

    def side_sequence(self, side: str) -> str:
        return self.primary_sequence if side == "primary" else self.control_sequence

    def side_bounds(self, side: str) -> tuple[int, int]:
        if side == "primary":
            return self.primary_start, self.primary_end
        return self.control_start, self.control_end


@dataclass(frozen=True)
class BaselineFrame:
    pair_id: str
    side: str
    sequence: str
    frame_index: int
    iou: float
    failure: bool
    center_error: float


@dataclass(frozen=True)
class ModeFrame:
    pair_id: str
    side: str
    sequence: str
    frame_index: int
    mode: str
    iou: float


@dataclass(frozen=True)
class BootstrapSummary:
    estimate: float
    ci_low: float
    ci_high: float
    p_two_sided_sign_tail: float
    n_pairs: int
    n_clusters: int

    @property
    def ci_excludes_zero(self) -> bool:
        return self.ci_low > 0.0 or self.ci_high < 0.0

    @property
    def ci_supports_estimate_direction(self) -> bool:
        return (
            (self.estimate > 0.0 and self.ci_low > 0.0)
            or (self.estimate < 0.0 and self.ci_high < 0.0)
        )


@dataclass(frozen=True)
class SensitivitySpec:
    dimension: str
    group: str
    selection_rule: str
    predicate: Callable[[PairSpec], bool]


LOCKED_SENSITIVITY_GROUPS = (
    SensitivitySpec(
        "final_ambiguity_level", "AMBIGUITY_LEVEL_2",
        "final_ambiguity_level=2", lambda pair: pair.ambiguity_level == "2",
    ),
    SensitivitySpec(
        "final_ambiguity_level", "AMBIGUITY_LEVEL_1",
        "final_ambiguity_level=1", lambda pair: pair.ambiguity_level == "1",
    ),
    SensitivitySpec(
        "control_sequence_relation", "SAME_SEQUENCE_CONTROL",
        "primary_sequence=control_sequence",
        lambda pair: pair.primary_sequence == pair.control_sequence,
    ),
    SensitivitySpec(
        "control_sequence_relation", "CROSS_SEQUENCE_CONTROL",
        "primary_sequence!=control_sequence",
        lambda pair: pair.primary_sequence != pair.control_sequence,
    ),
    *tuple(
        SensitivitySpec(
            "sensitivity_stratum", value, f"sensitivity_stratum={value}",
            lambda pair, expected=value: pair.sensitivity_stratum == expected,
        )
        for value in (
            "STRONG_SAME_SEQUENCE",
            "CROSS_SCENE_ACTIVITY",
            "COLOR_DIFFERENCE",
            "APPEARANCE_DIFFERENCE",
            "LOW_LIGHT_MULTI_TRAFFIC",
            "CONTROL_PARTIAL_OCCLUSION",
            "MULTI_FACE_BACKGROUND",
            "COSTUME_DIFFERENCE_CLASS_RESOLVED_PERSON",
        )
    ),
    *tuple(
        SensitivitySpec(
            "broad_superclass", value, f"broad_superclass={value}",
            lambda pair, expected=value: pair.broad_superclass == expected,
        )
        for value in ("PERSON", "VEHICLE", "FACE_HEAD", "OBJECT_OTHER")
    ),
)


class InputContractError(RuntimeError):
    """The discovery analysis input is incomplete, inconsistent, or malformed."""


class HoldoutExposureError(RuntimeError):
    """A sealed hold-out pair ID was seen before its outcome fields were read."""

    def __init__(self, path: Path, pair_id: str, line_number: int):
        self.path = path
        self.pair_id = pair_id
        self.line_number = line_number
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


def _require_columns(
    fieldnames: Sequence[str] | None, required: Sequence[str], context: str
) -> None:
    if fieldnames is None:
        raise InputContractError(f"{context}: CSV has no header")
    missing = [name for name in required if name not in fieldnames]
    if missing:
        raise InputContractError(f"{context}: missing required columns {missing}")


def _parse_int(value: str, context: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise InputContractError(f"{context}: expected integer, got {value!r}") from exc
    return parsed


def _parse_float(value: str, context: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise InputContractError(f"{context}: expected float, got {value!r}") from exc
    if not math.isfinite(parsed):
        raise InputContractError(f"{context}: non-finite value {value!r}")
    return parsed


def _parse_bool(value: str, context: str) -> bool:
    normalized = value.strip().casefold()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise InputContractError(f"{context}: expected explicit boolean, got {value!r}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _normalized_text_sha256(path: Path) -> str:
    text = path.read_bytes().decode("utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def load_frozen_slice(path: Path) -> tuple[dict[str, PairSpec], frozenset[str], str]:
    """Load metadata only and verify the exact frozen 12/8 semantic boundary."""
    normalized_sha = _normalized_text_sha256(path)
    if normalized_sha != EXPECTED_FROZEN_SLICE_NORMALIZED_SHA256:
        raise InputContractError(
            "frozen slice normalized SHA-256 mismatch: "
            f"expected {EXPECTED_FROZEN_SLICE_NORMALIZED_SHA256}, got {normalized_sha}"
        )

    required = (
        "pair_id", "split", "primary_sequence", "primary_start", "primary_end",
        "control_sequence", "control_start", "control_end", "broad_superclass",
        "final_ambiguity_level", "sensitivity_stratum", "manager_status",
    )
    rows: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _require_columns(reader.fieldnames, required, "frozen slice")
        for line_number, row in enumerate(reader, start=2):
            pair_id = row["pair_id"].strip()
            if not pair_id:
                raise InputContractError(f"frozen slice:{line_number}: empty pair_id")
            if pair_id in rows:
                raise InputContractError(
                    f"frozen slice:{line_number}: duplicate pair_id {pair_id}"
                )
            rows[pair_id] = {key: (value or "").strip() for key, value in row.items()}

    expected_all = set(EXPECTED_DISCOVERY_IDS) | set(EXPECTED_HOLDOUT_IDS)
    if set(rows) != expected_all:
        raise InputContractError(
            "frozen slice pair IDs differ from locked 12 discovery/8 hold-out set; "
            f"missing={sorted(expected_all - set(rows))}, "
            f"extra={sorted(set(rows) - expected_all)}"
        )

    discovery: dict[str, PairSpec] = {}
    for pair_id in EXPECTED_DISCOVERY_IDS + EXPECTED_HOLDOUT_IDS:
        row = rows[pair_id]
        expected_split = "DISCOVERY" if pair_id in EXPECTED_DISCOVERY_IDS else "HOLDOUT"
        if row["split"] != expected_split:
            raise InputContractError(
                f"frozen slice {pair_id}: split {row['split']!r}, expected {expected_split}"
            )
        if row["manager_status"] != "FROZEN":
            raise InputContractError(
                f"frozen slice {pair_id}: manager_status must be FROZEN"
            )
        p_start = _parse_int(row["primary_start"], f"frozen slice {pair_id} primary_start")
        p_end = _parse_int(row["primary_end"], f"frozen slice {pair_id} primary_end")
        c_start = _parse_int(row["control_start"], f"frozen slice {pair_id} control_start")
        c_end = _parse_int(row["control_end"], f"frozen slice {pair_id} control_end")
        if min(p_start, c_start) < 1 or p_start > p_end or c_start > c_end:
            raise InputContractError(f"frozen slice {pair_id}: invalid inclusive bounds")
        if not row["primary_sequence"] or not row["control_sequence"]:
            raise InputContractError(f"frozen slice {pair_id}: empty sequence")
        if expected_split == "DISCOVERY":
            if row["final_ambiguity_level"] not in {"1", "2"}:
                raise InputContractError(
                    f"frozen slice {pair_id}: ambiguity must be locked 1 or 2"
                )
            discovery[pair_id] = PairSpec(
                pair_id=pair_id,
                primary_sequence=row["primary_sequence"],
                primary_start=p_start,
                primary_end=p_end,
                control_sequence=row["control_sequence"],
                control_start=c_start,
                control_end=c_end,
                broad_superclass=row["broad_superclass"],
                ambiguity_level=row["final_ambiguity_level"],
                sensitivity_stratum=row["sensitivity_stratum"],
            )

    # Fail if a locked descriptive group disappeared from the frozen discovery set.
    for group in LOCKED_SENSITIVITY_GROUPS:
        if not any(group.predicate(pair) for pair in discovery.values()):
            raise InputContractError(
                f"frozen slice has no discovery pair for locked sensitivity group {group.group}"
            )
    return discovery, frozenset(EXPECTED_HOLDOUT_IDS), normalized_sha


def _read_header_line(raw, path: Path) -> bytes:
    data = bytearray()
    while True:
        value = raw.read(1)
        if not value:
            if not data:
                raise InputContractError(f"{path}: empty CSV")
            return bytes(data)
        data.extend(value)
        # CR, LF, and CRLF are all stopped before any subsequent row bytes.
        # For CRLF the LF remains and is consumed as a harmless blank line.
        if value in {b"\r", b"\n"}:
            return bytes(data)
        if len(data) > 1024 * 1024:
            raise InputContractError(f"{path}: unreasonably large CSV header")


def _read_first_field(raw, path: Path, line_number: int) -> tuple[bytes, bool] | None:
    """Read only bytes through the first comma; bool indicates a blank line."""
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
            raise InputContractError(f"{path}:{line_number}: pair_id field is too long")


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
                f"{path}:{line_number}: row exceeds 16 MiB or contains an embedded newline"
            )


def guarded_outcome_rows(
    path: Path,
    allowed_pair_ids: frozenset[str],
    sealed_pair_ids: frozenset[str],
    required_columns: Sequence[str],
    digest,
) -> Iterable[tuple[int, dict[str, str]]]:
    """Yield discovery rows without consuming any disallowed row's outcome fields."""
    with path.open("rb", buffering=0) as raw_file:
        raw = _DigestingReader(raw_file, digest)
        header_bytes = _read_header_line(raw, path)
        try:
            header = next(csv.reader([header_bytes.decode("utf-8-sig")]))
        except (UnicodeDecodeError, csv.Error) as exc:
            raise InputContractError(f"{path}: invalid UTF-8 CSV header") from exc
        header = [value.strip() for value in header]
        _require_columns(header, required_columns, str(path))
        if not header or header[0] != "pair_id":
            raise InputContractError(
                f"{path}: pair_id must be the first column for the hold-out read guard"
            )
        if len(set(header)) != len(header):
            raise InputContractError(f"{path}: duplicate CSV header names")

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
                    "stopped before reading outcome fields"
                )

            # Only a validated discovery ID reaches the outcome read below.
            remainder = _read_row_remainder(raw, path, line_number)
            complete_row = pair_bytes + b"," + remainder
            try:
                values = next(csv.reader([complete_row.decode("utf-8")]))
            except (UnicodeDecodeError, csv.Error) as exc:
                raise InputContractError(f"{path}:{line_number}: invalid UTF-8 CSV row") from exc
            if len(values) != len(header):
                raise InputContractError(
                    f"{path}:{line_number}: {len(values)} values for {len(header)} columns; "
                    "embedded newlines are not permitted"
                )
            row = {name: value.strip() for name, value in zip(header, values)}
            if row["pair_id"] != pair_id:
                raise InputContractError(f"{path}:{line_number}: pair_id parse mismatch")
            yield line_number, row
            line_number += 1


def _expected_frame_keys(specs: Mapping[str, PairSpec]) -> set[tuple[str, str, int]]:
    expected: set[tuple[str, str, int]] = set()
    for pair_id in EXPECTED_DISCOVERY_IDS:
        pair = specs[pair_id]
        for side in ("primary", "control"):
            start, end = pair.side_bounds(side)
            expected.update((pair_id, side, frame) for frame in range(start, end + 1))
    return expected


def load_baseline_frames(
    path: Path, specs: Mapping[str, PairSpec], sealed_ids: frozenset[str]
) -> tuple[dict[tuple[str, str, int], BaselineFrame], str]:
    required = (
        "pair_id", "side", "sequence", "frame_index", "iou", "failure",
        "center_error",
    )
    allowed_ids = frozenset(specs)
    frames: dict[tuple[str, str, int], BaselineFrame] = {}
    digest = hashlib.sha256()
    for line_number, row in guarded_outcome_rows(
        path, allowed_ids, sealed_ids, required, digest
    ):
        pair_id = row["pair_id"]
        side = row["side"].casefold()
        if side not in {"primary", "control"}:
            raise InputContractError(f"{path}:{line_number}: invalid side {row['side']!r}")
        pair = specs[pair_id]
        expected_sequence = pair.side_sequence(side)
        if row["sequence"] != expected_sequence:
            raise InputContractError(
                f"{path}:{line_number}: sequence {row['sequence']!r}, "
                f"expected {expected_sequence!r} for {pair_id}/{side}"
            )
        frame_index = _parse_int(row["frame_index"], f"{path}:{line_number} frame_index")
        start, end = pair.side_bounds(side)
        if not start <= frame_index <= end:
            raise InputContractError(
                f"{path}:{line_number}: frame {frame_index} outside frozen {start}-{end}"
            )
        iou = _parse_float(row["iou"], f"{path}:{line_number} iou")
        if not 0.0 <= iou <= 1.0:
            raise InputContractError(f"{path}:{line_number}: IoU outside [0,1]")
        failure = _parse_bool(row["failure"], f"{path}:{line_number} failure")
        expected_failure = iou < IOU_FAILURE_CUTOFF
        if failure != expected_failure:
            raise InputContractError(
                f"{path}:{line_number}: failure={failure} disagrees with IoU < 0.5 "
                f"({iou} -> {expected_failure})"
            )
        center_error = _parse_float(
            row["center_error"], f"{path}:{line_number} center_error"
        )
        if center_error < 0.0:
            raise InputContractError(f"{path}:{line_number}: negative center_error")
        key = (pair_id, side, frame_index)
        if key in frames:
            raise InputContractError(f"{path}:{line_number}: duplicate frame key {key}")
        frames[key] = BaselineFrame(
            pair_id, side, expected_sequence, frame_index, iou, failure, center_error
        )

    expected = _expected_frame_keys(specs)
    actual = set(frames)
    if actual != expected:
        raise InputContractError(
            "baseline discovery coverage differs from exact frozen intervals; "
            f"missing={sorted(expected - actual)[:20]}, extra={sorted(actual - expected)[:20]}"
        )
    return frames, digest.hexdigest()


def load_mode_frames(
    path: Path,
    specs: Mapping[str, PairSpec],
    sealed_ids: frozenset[str],
    baseline: Mapping[tuple[str, str, int], BaselineFrame],
) -> tuple[dict[tuple[str, str, str, int], ModeFrame], str]:
    required = (
        "pair_id", "side", "sequence", "frame_index", "mode", "iou",
        "physical_skip",
    )
    allowed_ids = frozenset(specs)
    frames: dict[tuple[str, str, str, int], ModeFrame] = {}
    digest = hashlib.sha256()
    for line_number, row in guarded_outcome_rows(
        path, allowed_ids, sealed_ids, required, digest
    ):
        pair_id = row["pair_id"]
        side = row["side"].casefold()
        if side not in {"primary", "control"}:
            raise InputContractError(f"{path}:{line_number}: invalid side {row['side']!r}")
        mode = row["mode"].casefold()
        if mode not in MODE_BY_NAME:
            raise InputContractError(
                f"{path}:{line_number}: mode {row['mode']!r} is not one of "
                f"{list(MODE_BY_NAME)}"
            )
        if _parse_bool(row["physical_skip"], f"{path}:{line_number} physical_skip"):
            raise InputContractError(
                f"{path}:{line_number}: physical_skip must be false for Stage 4B controls"
            )
        pair = specs[pair_id]
        expected_sequence = pair.side_sequence(side)
        if row["sequence"] != expected_sequence:
            raise InputContractError(
                f"{path}:{line_number}: sequence {row['sequence']!r}, "
                f"expected {expected_sequence!r} for {pair_id}/{side}"
            )
        frame_index = _parse_int(row["frame_index"], f"{path}:{line_number} frame_index")
        baseline_key = (pair_id, side, frame_index)
        if baseline_key not in baseline:
            raise InputContractError(
                f"{path}:{line_number}: mode frame has no exact baseline key {baseline_key}"
            )
        iou = _parse_float(row["iou"], f"{path}:{line_number} iou")
        if not 0.0 <= iou <= 1.0:
            raise InputContractError(f"{path}:{line_number}: IoU outside [0,1]")
        key = (mode, pair_id, side, frame_index)
        if key in frames:
            raise InputContractError(f"{path}:{line_number}: duplicate mode frame key {key}")
        frames[key] = ModeFrame(pair_id, side, expected_sequence, frame_index, mode, iou)

    expected = {
        (mode.name, pair_id, side, frame)
        for mode in LOCKED_MODES
        for pair_id, side, frame in baseline
    }
    actual = set(frames)
    if actual != expected:
        raise InputContractError(
            "mode discovery coverage must contain every baseline frame for exactly nine modes; "
            f"missing={sorted(expected - actual)[:20]}, extra={sorted(actual - expected)[:20]}"
        )
    return frames, digest.hexdigest()


def _mean(values: Iterable[float]) -> float:
    materialized = list(values)
    if not materialized:
        raise InputContractError("attempted to average an empty locked set")
    return math.fsum(materialized) / len(materialized)


def build_pair_a_rows(
    specs: Mapping[str, PairSpec],
    baseline: Mapping[tuple[str, str, int], BaselineFrame],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for pair_id in EXPECTED_DISCOVERY_IDS:
        pair = specs[pair_id]
        side_data: dict[str, list[BaselineFrame]] = {}
        for side in ("primary", "control"):
            start, end = pair.side_bounds(side)
            side_data[side] = [baseline[(pair_id, side, frame)] for frame in range(start, end + 1)]
        p_iou = _mean(frame.iou for frame in side_data["primary"])
        c_iou = _mean(frame.iou for frame in side_data["control"])
        p_failure = _mean(float(frame.failure) for frame in side_data["primary"])
        c_failure = _mean(float(frame.failure) for frame in side_data["control"])
        p_center = _mean(frame.center_error for frame in side_data["primary"])
        c_center = _mean(frame.center_error for frame in side_data["control"])
        rows.append(
            {
                "pair_id": pair_id,
                "primary_sequence": pair.primary_sequence,
                "control_sequence": pair.control_sequence,
                "primary_start": pair.primary_start,
                "primary_end": pair.primary_end,
                "control_start": pair.control_start,
                "control_end": pair.control_end,
                "primary_frame_count": len(side_data["primary"]),
                "control_frame_count": len(side_data["control"]),
                "broad_superclass": pair.broad_superclass,
                "final_ambiguity_level": pair.ambiguity_level,
                "sensitivity_stratum": pair.sensitivity_stratum,
                "control_relation": (
                    "SAME_SEQUENCE_CONTROL"
                    if pair.primary_sequence == pair.control_sequence
                    else "CROSS_SEQUENCE_CONTROL"
                ),
                "primary_mean_iou": p_iou,
                "control_mean_iou": c_iou,
                "iou_weakness": c_iou - p_iou,
                "primary_failure_rate": p_failure,
                "control_failure_rate": c_failure,
                "failure_weakness": p_failure - c_failure,
                "primary_mean_center_error": p_center,
                "control_mean_center_error": c_center,
                "center_error_primary_minus_control": p_center - c_center,
            }
        )
    return rows


def build_pair_b_rows(
    specs: Mapping[str, PairSpec],
    baseline: Mapping[tuple[str, str, int], BaselineFrame],
    modes: Mapping[tuple[str, str, str, int], ModeFrame],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for mode in LOCKED_MODES:
        for pair_id in EXPECTED_DISCOVERY_IDS:
            pair = specs[pair_id]
            contribution: dict[str, float] = {}
            for side in ("primary", "control"):
                start, end = pair.side_bounds(side)
                contribution[side] = _mean(
                    baseline[(pair_id, side, frame)].iou
                    - modes[(mode.name, pair_id, side, frame)].iou
                    for frame in range(start, end + 1)
                )
            rows.append(
                {
                    "test_order": mode.test_order,
                    "mode": mode.name,
                    "mrm_members": ";".join(str(value) for value in mode.members),
                    "pair_id": pair_id,
                    "primary_sequence": pair.primary_sequence,
                    "control_sequence": pair.control_sequence,
                    "broad_superclass": pair.broad_superclass,
                    "final_ambiguity_level": pair.ambiguity_level,
                    "sensitivity_stratum": pair.sensitivity_stratum,
                    "contribution_distractor": contribution["primary"],
                    "contribution_control": contribution["control"],
                    "interaction": contribution["primary"] - contribution["control"],
                }
            )
    return rows


def _primary_clusters(
    specs: Mapping[str, PairSpec], pair_ids: Sequence[str]
) -> dict[str, tuple[str, ...]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for pair_id in sorted(pair_ids):
        grouped[specs[pair_id].primary_sequence].append(pair_id)
    return {key: tuple(value) for key, value in sorted(grouped.items())}


def _connected_component_clusters(
    specs: Mapping[str, PairSpec], pair_ids: Sequence[str]
) -> dict[str, tuple[str, ...]]:
    """Connected components of pair nodes sharing either source sequence."""
    ordered = sorted(pair_ids)
    parent = {pair_id: pair_id for pair_id in ordered}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: str, right: str) -> None:
        left_root, right_root = find(left), find(right)
        if left_root == right_root:
            return
        smaller, larger = sorted((left_root, right_root))
        parent[larger] = smaller

    first_for_sequence: dict[str, str] = {}
    for pair_id in ordered:
        pair = specs[pair_id]
        for sequence in {pair.primary_sequence, pair.control_sequence}:
            if sequence in first_for_sequence:
                union(pair_id, first_for_sequence[sequence])
            else:
                first_for_sequence[sequence] = pair_id

    grouped: dict[str, list[str]] = defaultdict(list)
    for pair_id in ordered:
        grouped[find(pair_id)].append(pair_id)
    components = sorted((tuple(sorted(values)) for values in grouped.values()))
    return {f"component_{index:02d}": values for index, values in enumerate(components, 1)}


def _quantile_linear(values: Sequence[float], probability: float) -> float:
    if not values:
        raise InputContractError("cannot take a quantile of zero bootstrap estimates")
    ordered = sorted(values)
    location = (len(ordered) - 1) * probability
    lower_index = math.floor(location)
    upper_index = math.ceil(location)
    if lower_index == upper_index:
        return ordered[lower_index]
    fraction = location - lower_index
    return ordered[lower_index] * (1.0 - fraction) + ordered[upper_index] * fraction


def _bootstrap_many(
    pair_values: Mapping[str, Mapping[str, float]],
    clusters: Mapping[str, Sequence[str]],
) -> dict[str, BootstrapSummary]:
    """Bootstrap multiple effects with the same locked cluster draws."""
    if not pair_values:
        raise InputContractError("bootstrap requested without effects")
    metric_names = tuple(pair_values)
    pair_sets = [set(pair_values[name]) for name in metric_names]
    if any(value_set != pair_sets[0] for value_set in pair_sets[1:]):
        raise InputContractError("bootstrap metrics do not cover identical pair sets")
    all_pairs = pair_sets[0]
    cluster_pairs = {key: tuple(value) for key, value in clusters.items()}
    flattened = [pair for values in cluster_pairs.values() for pair in values]
    if len(flattened) != len(set(flattened)) or set(flattened) != all_pairs:
        raise InputContractError("bootstrap clusters are not an exact partition of pairs")
    cluster_names = tuple(sorted(cluster_pairs))
    if not cluster_names:
        raise InputContractError("bootstrap requested without clusters")
    estimates: dict[str, list[float]] = {
        name: [] for name in metric_names
    }
    rng = random.Random(BOOTSTRAP_SEED)
    for _ in range(BOOTSTRAP_RESAMPLES):
        sampled_clusters = [
            cluster_names[rng.randrange(len(cluster_names))]
            for _ in range(len(cluster_names))
        ]
        sampled_pairs = [
            pair_id
            for cluster_name in sampled_clusters
            for pair_id in cluster_pairs[cluster_name]
        ]
        for name in metric_names:
            estimates[name].append(
                math.fsum(pair_values[name][pair_id] for pair_id in sampled_pairs)
                / len(sampled_pairs)
            )

    results: dict[str, BootstrapSummary] = {}
    ordered_pairs = sorted(all_pairs)
    for name in metric_names:
        distribution = estimates[name]
        nonpositive = sum(value <= 0.0 for value in distribution)
        nonnegative = sum(value >= 0.0 for value in distribution)
        lower_tail = (nonpositive + 1) / (BOOTSTRAP_RESAMPLES + 1)
        upper_tail = (nonnegative + 1) / (BOOTSTRAP_RESAMPLES + 1)
        p_value = min(1.0, 2.0 * min(lower_tail, upper_tail))
        results[name] = BootstrapSummary(
            estimate=_mean(pair_values[name][pair_id] for pair_id in ordered_pairs),
            ci_low=_quantile_linear(distribution, 0.025),
            ci_high=_quantile_linear(distribution, 0.975),
            p_two_sided_sign_tail=p_value,
            n_pairs=len(ordered_pairs),
            n_clusters=len(cluster_names),
        )
    return results


def _both_bootstraps(
    specs: Mapping[str, PairSpec], pair_values: Mapping[str, Mapping[str, float]]
) -> tuple[dict[str, BootstrapSummary], dict[str, BootstrapSummary], dict[str, tuple[str, ...]]]:
    pair_ids = sorted(next(iter(pair_values.values())))
    primary = _bootstrap_many(pair_values, _primary_clusters(specs, pair_ids))
    components = _connected_component_clusters(specs, pair_ids)
    component = _bootstrap_many(pair_values, components)
    return primary, component, components


def _holm_adjust_exact_nine(p_values: Mapping[str, float]) -> dict[str, float]:
    if set(p_values) != set(MODE_BY_NAME) or len(p_values) != 9:
        raise InputContractError("Holm correction requires exactly the nine locked modes")
    order_lookup = {mode.name: mode.test_order for mode in LOCKED_MODES}
    ranked = sorted(p_values.items(), key=lambda item: (item[1], order_lookup[item[0]]))
    adjusted: dict[str, float] = {}
    running_max = 0.0
    family_size = 9
    for rank_zero_based, (name, p_value) in enumerate(ranked):
        candidate = min(1.0, (family_size - rank_zero_based) * p_value)
        running_max = max(running_max, candidate)
        adjusted[name] = running_max
    return adjusted


def _fmt_csv(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if not math.isfinite(value):
            raise InputContractError("refusing to serialize non-finite float")
        # Preserve a binary64 value across the CSV round trip.  Twelve
        # significant digits can collapse values such as
        # -0.19999999999999998 to -0.2; that changes whether an otherwise
        # exact bootstrap draw is counted on the nonnegative/nonpositive
        # boundary and therefore changes the locked sign-tail p-value.
        return format(value, ".17g")
    return value


def _write_csv_atomic(
    path: Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, object]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=fieldnames, extrasaction="raise", lineterminator="\n"
            )
            writer.writeheader()
            for row in rows:
                writer.writerow({key: _fmt_csv(row.get(key)) for key in fieldnames})
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _write_json_atomic(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


PAIR_A_FIELDS = (
    "pair_id", "primary_sequence", "control_sequence", "primary_start",
    "primary_end", "control_start", "control_end", "primary_frame_count",
    "control_frame_count", "broad_superclass", "final_ambiguity_level",
    "sensitivity_stratum", "control_relation", "primary_mean_iou",
    "control_mean_iou", "iou_weakness", "primary_failure_rate",
    "control_failure_rate", "failure_weakness", "primary_mean_center_error",
    "control_mean_center_error", "center_error_primary_minus_control",
)
PAIR_B_FIELDS = (
    "test_order", "mode", "mrm_members", "pair_id", "primary_sequence",
    "control_sequence", "broad_superclass", "final_ambiguity_level",
    "sensitivity_stratum", "contribution_distractor", "contribution_control",
    "interaction",
)
CRITERION_A_FIELDS = (
    "metric", "definition", "estimate", "threshold", "threshold_relation",
    "n_pairs", "primary_cluster_unit", "n_primary_clusters", "primary_ci_low",
    "primary_ci_high", "primary_p_two_sided_sign_tail",
    "primary_ci_excludes_zero", "component_cluster_unit",
    "n_connected_components", "component_ci_low", "component_ci_high",
    "component_p_two_sided_sign_tail", "component_ci_excludes_zero",
    "metric_pass", "criterion_a_pass", "decision_role",
)
CRITERION_B_FIELDS = (
    "test_order", "mode", "mrm_members", "group_size",
    "mean_contribution_distractor", "mean_contribution_control",
    "mean_interaction", "absolute_interaction_threshold", "n_pairs",
    "n_primary_clusters", "primary_ci_low", "primary_ci_high",
    "primary_p_unadjusted", "primary_p_holm_adjusted", "holm_reject_0_05",
    "primary_ci_excludes_zero", "n_connected_components", "component_ci_low",
    "component_ci_high", "component_p_two_sided_sign_tail",
    "component_ci_excludes_zero", "direction", "direction_stable",
    "scientifically_interpretable", "test_pass", "criterion_b_pass",
    "selected_refinement_path", "physical_skip", "decision_role",
)
SENSITIVITY_FIELDS = (
    "analysis_family", "sensitivity_dimension", "sensitivity_group",
    "selection_rule", "metric_or_mode", "effect_definition", "n_pairs",
    "pair_ids", "estimate", "n_primary_clusters", "primary_ci_low",
    "primary_ci_high", "primary_p_two_sided_sign_tail",
    "n_connected_components", "component_ci_low", "component_ci_high",
    "component_p_two_sided_sign_tail", "decision_role",
)
BOOTSTRAP_FIELDS = (
    "analysis_family", "test_id", "bootstrap_scheme", "cluster_unit",
    "n_clusters", "n_pairs", "estimate", "ci_low", "ci_high",
    "p_two_sided_sign_tail", "resamples", "seed", "decision_role",
)
HOLM_FIELDS = (
    "test_order", "mode", "p_unadjusted", "holm_rank",
    "holm_multiplier", "p_holm_adjusted", "reject_familywise_0_05",
    "family_size", "familywise_alpha", "decision_role",
)


def _bootstrap_row(
    family: str, test_id: str, scheme: str, cluster_unit: str,
    summary: BootstrapSummary, decision_role: str,
) -> dict[str, object]:
    return {
        "analysis_family": family,
        "test_id": test_id,
        "bootstrap_scheme": scheme,
        "cluster_unit": cluster_unit,
        "n_clusters": summary.n_clusters,
        "n_pairs": summary.n_pairs,
        "estimate": summary.estimate,
        "ci_low": summary.ci_low,
        "ci_high": summary.ci_high,
        "p_two_sided_sign_tail": summary.p_two_sided_sign_tail,
        "resamples": BOOTSTRAP_RESAMPLES,
        "seed": BOOTSTRAP_SEED,
        "decision_role": decision_role,
    }


def _direction(estimate: float) -> str:
    if estimate > 0.0:
        return "MORE_USEFUL_UNDER_DISTRACTOR_AMBIGUITY"
    if estimate < 0.0:
        return "RELATIVE_UTILITY_LOWER_UNDER_DISTRACTOR_AMBIGUITY"
    return "NO_DIRECTION"


def analyze(
    frozen_slice: Path, baseline_csv: Path, mode_csv: Path | None, output_dir: Path
) -> dict[str, object]:
    specs, sealed_ids, slice_normalized_sha = load_frozen_slice(frozen_slice)
    baseline, baseline_sha = load_baseline_frames(baseline_csv, specs, sealed_ids)
    pair_a_rows = build_pair_a_rows(specs, baseline)
    pair_a_by_id = {str(row["pair_id"]): row for row in pair_a_rows}
    a_values = {
        "iou_weakness": {
            pair_id: float(pair_a_by_id[pair_id]["iou_weakness"])
            for pair_id in EXPECTED_DISCOVERY_IDS
        },
        "failure_weakness": {
            pair_id: float(pair_a_by_id[pair_id]["failure_weakness"])
            for pair_id in EXPECTED_DISCOVERY_IDS
        },
    }
    a_primary, a_component, complete_components = _both_bootstraps(specs, a_values)
    a_thresholds = {
        "iou_weakness": CRITERION_A_IOU_THRESHOLD,
        "failure_weakness": CRITERION_A_FAILURE_THRESHOLD,
    }
    a_metric_pass = {
        metric: a_primary[metric].estimate >= a_thresholds[metric]
        and a_primary[metric].ci_low > 0.0
        for metric in a_values
    }
    criterion_a_pass = any(a_metric_pass.values())

    criterion_a_rows: list[dict[str, object]] = []
    bootstrap_rows: list[dict[str, object]] = []
    definitions = {
        "iou_weakness": "mean_pair(control_mean_iou-primary_mean_iou)",
        "failure_weakness": (
            "mean_pair(primary_failure_rate-control_failure_rate); failure=iou<0.5"
        ),
    }
    for metric in ("iou_weakness", "failure_weakness"):
        primary, component = a_primary[metric], a_component[metric]
        criterion_a_rows.append(
            {
                "metric": metric,
                "definition": definitions[metric],
                "estimate": primary.estimate,
                "threshold": a_thresholds[metric],
                "threshold_relation": ">=",
                "n_pairs": primary.n_pairs,
                "primary_cluster_unit": "primary_sequence",
                "n_primary_clusters": primary.n_clusters,
                "primary_ci_low": primary.ci_low,
                "primary_ci_high": primary.ci_high,
                "primary_p_two_sided_sign_tail": primary.p_two_sided_sign_tail,
                "primary_ci_excludes_zero": primary.ci_excludes_zero,
                "component_cluster_unit": "connected_source_component",
                "n_connected_components": component.n_clusters,
                "component_ci_low": component.ci_low,
                "component_ci_high": component.ci_high,
                "component_p_two_sided_sign_tail": component.p_two_sided_sign_tail,
                "component_ci_excludes_zero": component.ci_excludes_zero,
                "metric_pass": a_metric_pass[metric],
                "criterion_a_pass": criterion_a_pass,
                "decision_role": "PRIMARY_COMPLETE_SET",
            }
        )
        bootstrap_rows.extend(
            (
                _bootstrap_row(
                    "CRITERION_A", metric, "PRIMARY_SEQUENCE_CLUSTERED",
                    "primary_sequence", primary, "PRIMARY_DECISION",
                ),
                _bootstrap_row(
                    "CRITERION_A", metric, "CONNECTED_SOURCE_COMPONENT",
                    "connected_source_component", component, "REQUIRED_SENSITIVITY",
                ),
            )
        )

    pair_b_rows: list[dict[str, object]] = []
    criterion_b_rows: list[dict[str, object]] = []
    holm_rows: list[dict[str, object]] = []
    b_primary: dict[str, BootstrapSummary] = {}
    b_component: dict[str, BootstrapSummary] = {}
    criterion_b_pass: bool | None = None
    selected_refinement_path: str | None = None
    modes: dict[tuple[str, str, str, int], ModeFrame] | None = None
    mode_sha: str | None = None
    mode_disposition: str

    # Locked stopping rule: do not even open the mode CSV if A failed.
    if not criterion_a_pass:
        mode_disposition = "NOT_OPENED_CRITERION_A_FAIL"
    elif mode_csv is None:
        mode_disposition = "NOT_SUPPLIED_AFTER_CRITERION_A_PASS"
    else:
        modes, mode_sha = load_mode_frames(mode_csv, specs, sealed_ids, baseline)
        mode_disposition = "OPENED_AFTER_CRITERION_A_PASS"
        pair_b_rows = build_pair_b_rows(specs, baseline, modes)
        b_lookup = {
            (str(row["mode"]), str(row["pair_id"])): row for row in pair_b_rows
        }
        b_values = {
            mode.name: {
                pair_id: float(b_lookup[(mode.name, pair_id)]["interaction"])
                for pair_id in EXPECTED_DISCOVERY_IDS
            }
            for mode in LOCKED_MODES
        }
        b_primary, b_component, _ = _both_bootstraps(specs, b_values)
        holm = _holm_adjust_exact_nine(
            {name: summary.p_two_sided_sign_tail for name, summary in b_primary.items()}
        )
        ordered_by_p = sorted(
            LOCKED_MODES,
            key=lambda mode: (b_primary[mode.name].p_two_sided_sign_tail, mode.test_order),
        )
        holm_rank = {mode.name: rank for rank, mode in enumerate(ordered_by_p, 1)}
        test_pass: dict[str, bool] = {}
        for mode in LOCKED_MODES:
            name = mode.name
            primary, component = b_primary[name], b_component[name]
            direction = _direction(primary.estimate)
            direction_stable = primary.ci_supports_estimate_direction
            # Both signs have locked interpretations in the protocol: positive
            # is greater utility under distractor ambiguity; negative is lower
            # relative utility there (potentially unnecessary/harmful).  This
            # boolean never licenses a post-hoc mechanism claim.
            interpretable = direction != "NO_DIRECTION"
            test_pass[name] = (
                abs(primary.estimate) >= CRITERION_B_INTERACTION_THRESHOLD
                and primary.ci_supports_estimate_direction
                and holm[name] <= FAMILYWISE_ALPHA
                and direction_stable
                and interpretable
            )
        criterion_b_pass = any(test_pass.values())
        if criterion_b_pass:
            passing_modes = [mode for mode in LOCKED_MODES if test_pass[mode.name]]
            selected_refinement_path = min(
                passing_modes,
                key=lambda mode: (
                    -abs(b_primary[mode.name].estimate),
                    mode.group_size,
                    mode.lower_mrm_index,
                    mode.test_order,
                ),
            ).name

        for mode in LOCKED_MODES:
            name = mode.name
            primary, component = b_primary[name], b_component[name]
            mode_pair_rows = [row for row in pair_b_rows if row["mode"] == name]
            direction = _direction(primary.estimate)
            criterion_b_rows.append(
                {
                    "test_order": mode.test_order,
                    "mode": name,
                    "mrm_members": ";".join(str(value) for value in mode.members),
                    "group_size": mode.group_size,
                    "mean_contribution_distractor": _mean(
                        float(row["contribution_distractor"]) for row in mode_pair_rows
                    ),
                    "mean_contribution_control": _mean(
                        float(row["contribution_control"]) for row in mode_pair_rows
                    ),
                    "mean_interaction": primary.estimate,
                    "absolute_interaction_threshold": CRITERION_B_INTERACTION_THRESHOLD,
                    "n_pairs": primary.n_pairs,
                    "n_primary_clusters": primary.n_clusters,
                    "primary_ci_low": primary.ci_low,
                    "primary_ci_high": primary.ci_high,
                    "primary_p_unadjusted": primary.p_two_sided_sign_tail,
                    "primary_p_holm_adjusted": holm[name],
                    "holm_reject_0_05": holm[name] <= FAMILYWISE_ALPHA,
                    "primary_ci_excludes_zero": primary.ci_excludes_zero,
                    "n_connected_components": component.n_clusters,
                    "component_ci_low": component.ci_low,
                    "component_ci_high": component.ci_high,
                    "component_p_two_sided_sign_tail": component.p_two_sided_sign_tail,
                    "component_ci_excludes_zero": component.ci_excludes_zero,
                    "direction": direction,
                    "direction_stable": primary.ci_supports_estimate_direction,
                    "scientifically_interpretable": direction != "NO_DIRECTION",
                    "test_pass": test_pass[name],
                    "criterion_b_pass": criterion_b_pass,
                    "selected_refinement_path": (
                        name == selected_refinement_path
                    ),
                    "physical_skip": False,
                    "decision_role": "PRIMARY_NINE_TEST_FAMILY",
                }
            )
            bootstrap_rows.extend(
                (
                    _bootstrap_row(
                        "CRITERION_B", name, "PRIMARY_SEQUENCE_CLUSTERED",
                        "primary_sequence", primary, "PRIMARY_DECISION",
                    ),
                    _bootstrap_row(
                        "CRITERION_B", name, "CONNECTED_SOURCE_COMPONENT",
                        "connected_source_component", component, "REQUIRED_SENSITIVITY",
                    ),
                )
            )
            rank = holm_rank[name]
            holm_rows.append(
                {
                    "test_order": mode.test_order,
                    "mode": name,
                    "p_unadjusted": primary.p_two_sided_sign_tail,
                    "holm_rank": rank,
                    "holm_multiplier": 10 - rank,
                    "p_holm_adjusted": holm[name],
                    "reject_familywise_0_05": holm[name] <= FAMILYWISE_ALPHA,
                    "family_size": 9,
                    "familywise_alpha": FAMILYWISE_ALPHA,
                    "decision_role": "PRIMARY_NINE_TEST_FAMILY",
                }
            )

    sensitivity_rows: list[dict[str, object]] = []
    for sensitivity in LOCKED_SENSITIVITY_GROUPS:
        selected_ids = [
            pair_id for pair_id in EXPECTED_DISCOVERY_IDS
            if sensitivity.predicate(specs[pair_id])
        ]
        selected_a = {
            metric: {pair_id: values[pair_id] for pair_id in selected_ids}
            for metric, values in a_values.items()
        }
        group_a_primary, group_a_component, _ = _both_bootstraps(specs, selected_a)
        for metric in ("iou_weakness", "failure_weakness"):
            primary, component = group_a_primary[metric], group_a_component[metric]
            sensitivity_rows.append(
                {
                    "analysis_family": "CRITERION_A",
                    "sensitivity_dimension": sensitivity.dimension,
                    "sensitivity_group": sensitivity.group,
                    "selection_rule": sensitivity.selection_rule,
                    "metric_or_mode": metric,
                    "effect_definition": definitions[metric],
                    "n_pairs": len(selected_ids),
                    "pair_ids": ";".join(selected_ids),
                    "estimate": primary.estimate,
                    "n_primary_clusters": primary.n_clusters,
                    "primary_ci_low": primary.ci_low,
                    "primary_ci_high": primary.ci_high,
                    "primary_p_two_sided_sign_tail": primary.p_two_sided_sign_tail,
                    "n_connected_components": component.n_clusters,
                    "component_ci_low": component.ci_low,
                    "component_ci_high": component.ci_high,
                    "component_p_two_sided_sign_tail": component.p_two_sided_sign_tail,
                    "decision_role": "LOCKED_DESCRIPTIVE_SENSITIVITY_ONLY",
                }
            )
        if modes is not None:
            b_lookup = {
                (str(row["mode"]), str(row["pair_id"])): row for row in pair_b_rows
            }
            selected_b = {
                mode.name: {
                    pair_id: float(b_lookup[(mode.name, pair_id)]["interaction"])
                    for pair_id in selected_ids
                }
                for mode in LOCKED_MODES
            }
            group_b_primary, group_b_component, _ = _both_bootstraps(specs, selected_b)
            for mode in LOCKED_MODES:
                primary, component = (
                    group_b_primary[mode.name], group_b_component[mode.name]
                )
                sensitivity_rows.append(
                    {
                        "analysis_family": "CRITERION_B",
                        "sensitivity_dimension": sensitivity.dimension,
                        "sensitivity_group": sensitivity.group,
                        "selection_rule": sensitivity.selection_rule,
                        "metric_or_mode": mode.name,
                        "effect_definition": (
                            "mean_pair(mean_primary(baseline_iou-ablation_iou)-"
                            "mean_control(baseline_iou-ablation_iou))"
                        ),
                        "n_pairs": len(selected_ids),
                        "pair_ids": ";".join(selected_ids),
                        "estimate": primary.estimate,
                        "n_primary_clusters": primary.n_clusters,
                        "primary_ci_low": primary.ci_low,
                        "primary_ci_high": primary.ci_high,
                        "primary_p_two_sided_sign_tail": primary.p_two_sided_sign_tail,
                        "n_connected_components": component.n_clusters,
                        "component_ci_low": component.ci_low,
                        "component_ci_high": component.ci_high,
                        "component_p_two_sided_sign_tail": component.p_two_sided_sign_tail,
                        "decision_role": "LOCKED_DESCRIPTIVE_SENSITIVITY_ONLY",
                    }
                )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_paths = {
        "criterion_a": output_dir / "2026-08-26_stage4B_criterionA_results.csv",
        "criterion_b": output_dir / "2026-08-26_stage4B_criterionB_results.csv",
        "sensitivity": output_dir / "2026-08-26_stage4B_sensitivity_results.csv",
        "pair_a": output_dir / "2026-08-26_stage4B_pair_level_A.csv",
        "pair_b": output_dir / "2026-08-26_stage4B_pair_level_B.csv",
        "bootstrap": output_dir / "2026-08-26_stage4B_bootstrap_results.csv",
        "holm": output_dir / "2026-08-26_stage4B_holm_adjusted_tests.csv",
        "summary": output_dir / "2026-08-26_stage4B_analysis_summary.json",
    }
    _write_csv_atomic(output_paths["criterion_a"], CRITERION_A_FIELDS, criterion_a_rows)
    _write_csv_atomic(output_paths["criterion_b"], CRITERION_B_FIELDS, criterion_b_rows)
    _write_csv_atomic(output_paths["sensitivity"], SENSITIVITY_FIELDS, sensitivity_rows)
    _write_csv_atomic(output_paths["pair_a"], PAIR_A_FIELDS, pair_a_rows)
    _write_csv_atomic(output_paths["pair_b"], PAIR_B_FIELDS, pair_b_rows)
    _write_csv_atomic(output_paths["bootstrap"], BOOTSTRAP_FIELDS, bootstrap_rows)
    _write_csv_atomic(output_paths["holm"], HOLM_FIELDS, holm_rows)

    if not criterion_a_pass:
        b_status = "NOT_RUN_CRITERION_A_FAIL"
        stage4b_conclusion: str | None = "STAGE4B_CRITERION_A_FAIL"
        next_action = "STOP_BEFORE_MRM_MINING"
    elif criterion_b_pass is None:
        b_status = "NOT_RUN_MODE_DATA_NOT_SUPPLIED"
        stage4b_conclusion = None
        next_action = "RUN_EXACTLY_NINE_PREDECLARED_CRITERION_B_MODES"
    elif criterion_b_pass:
        b_status = "PASS"
        # Bounded refinement is required by Phase B-C before the allowed final
        # AB-ready conclusion is emitted by the execution/reporting lane.
        stage4b_conclusion = None
        next_action = "RUN_BOUNDED_REFINEMENT_FOR_SELECTED_PATH_ONLY"
    else:
        b_status = "FAIL"
        stage4b_conclusion = "STAGE4B_CRITERION_B_FAIL"
        next_action = "STOP_BEFORE_RETRIEVER_MLP_OR_T3_REFINEMENT"

    summary: dict[str, object] = {
        "schema_version": "stage4b-analysis-v1",
        "analysis_contract": {
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "ci": "two-sided percentile 95%; linear interpolation",
            "primary_cluster_unit": "unique primary_sequence; retain all pairs per draw",
            "component_cluster_unit": (
                "connected components of pairs sharing any primary/control sequence"
            ),
            "pair_weighting": "equal after within-interval frame means",
            "p_value": (
                "two-sided bootstrap sign/tail with inclusive zero and +1 correction"
            ),
            "holm": "monotone Holm step-down across exactly nine tests",
            "familywise_alpha": FAMILYWISE_ALPHA,
            "criterion_a_thresholds": {
                "iou_weakness_minimum": CRITERION_A_IOU_THRESHOLD,
                "failure_weakness_minimum": CRITERION_A_FAILURE_THRESHOLD,
            },
            "criterion_b_absolute_interaction_minimum": (
                CRITERION_B_INTERACTION_THRESHOLD
            ),
            "failure_definition": "iou < 0.5",
            "locked_modes": [mode.name for mode in LOCKED_MODES],
            "locked_sensitivity_groups": [
                {
                    "dimension": group.dimension,
                    "group": group.group,
                    "selection_rule": group.selection_rule,
                }
                for group in LOCKED_SENSITIVITY_GROUPS
            ],
            "direction_stability": (
                "primary clustered percentile CI excludes zero in the point-estimate "
                "direction; no post-hoc subgroup gate"
            ),
            "selection_rule": (
                "among passing Holm-adjusted tests: largest absolute mean interaction; "
                "then smaller group; then lower MRM index"
            ),
            "physical_skip": False,
        },
        "inputs": {
            "frozen_slice": {
                "path": str(frozen_slice.resolve()),
                "sha256_raw": _sha256(frozen_slice),
                "sha256_normalized_lf": slice_normalized_sha,
            },
            "baseline_csv": {
                "path": str(baseline_csv.resolve()),
                "sha256": baseline_sha,
                "rows": len(baseline),
                "discovery_only_guard_pass": True,
            },
            "mode_csv": {
                "path": str(mode_csv.resolve()) if mode_csv is not None else None,
                "sha256": mode_sha,
                "rows": len(modes) if modes is not None else 0,
                "disposition": mode_disposition,
                "discovery_only_guard_pass": True if modes is not None else None,
            },
        },
        "frozen_boundary": {
            "validation": "PASS",
            "discovery_pair_count": len(specs),
            "holdout_pair_count_in_seal_metadata": len(sealed_ids),
            "holdout_pairs_executed": "NOT_VERIFIABLE_FROM_STATISTICAL_INPUTS",
            "holdout_pairs_present_in_outcome_inputs": 0,
            "holdout_outcomes_read": 0,
            "discovery_pair_ids": list(EXPECTED_DISCOVERY_IDS),
            "holdout_ids_used_only_as_read_guard": list(EXPECTED_HOLDOUT_IDS),
            "connected_source_components": complete_components,
        },
        "criterion_a": {
            "status": "PASS" if criterion_a_pass else "FAIL",
            "pass": criterion_a_pass,
            "pass_logic": (
                "(IoU weakness >= 0.05 and primary CI lower bound > 0) OR "
                "(failure weakness >= 0.10 and primary CI lower bound > 0)"
            ),
            "metrics": {
                metric: {
                    "estimate": a_primary[metric].estimate,
                    "primary_ci_95": [a_primary[metric].ci_low, a_primary[metric].ci_high],
                    "component_ci_95": [
                        a_component[metric].ci_low, a_component[metric].ci_high
                    ],
                    "threshold": a_thresholds[metric],
                    "metric_pass": a_metric_pass[metric],
                }
                for metric in ("iou_weakness", "failure_weakness")
            },
        },
        "criterion_b": {
            "status": b_status,
            "pass": criterion_b_pass,
            "family_size": 9 if modes is not None else 0,
            "holm_correction": "PASS_EXACTLY_NINE" if modes is not None else "NOT_RUN",
            "selected_refinement_path": selected_refinement_path,
            "tests": [
                {
                    "test_order": row["test_order"],
                    "mode": row["mode"],
                    "mean_interaction": row["mean_interaction"],
                    "primary_ci_95": [row["primary_ci_low"], row["primary_ci_high"]],
                    "p_unadjusted": row["primary_p_unadjusted"],
                    "p_holm_adjusted": row["primary_p_holm_adjusted"],
                    "test_pass": row["test_pass"],
                }
                for row in criterion_b_rows
            ],
        },
        "stage4b_conclusion": stage4b_conclusion,
        "next_action": next_action,
        "non_claims": {
            "diag_pass_fail_assigned": False,
            "stage4c_unlocked": False,
            "s1_s7_started": False,
            "primary_shortlist": None,
            "main_baseline": None,
            "proposed_architecture": None,
        },
        "outputs": {
            key: {
                "path": str(path.resolve()),
                "sha256": _sha256(path),
            }
            for key, path in output_paths.items()
            if key != "summary"
        },
    }
    _write_json_atomic(output_paths["summary"], summary)
    return summary


def _write_holdout_exposure_summary(output_dir: Path, error: HoldoutExposureError) -> None:
    output_path = output_dir / "2026-08-26_stage4B_analysis_summary.json"
    payload = {
        "schema_version": "stage4b-analysis-v1",
        "stage4b_conclusion": "STAGE4B_INVALID_HOLDOUT_EXPOSURE",
        "frozen_boundary": {
            "validation": "FAIL",
            "holdout_pair_id_detected": error.pair_id,
            "source_path": str(error.path.resolve()),
            "line_number": error.line_number,
            "offending_row_outcome_fields_read": False,
            "analysis_stopped": True,
        },
        "criterion_a": {"status": "NOT_COMPLETED"},
        "criterion_b": {"status": "NOT_RUN"},
    }
    _write_json_atomic(output_path, payload)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze the frozen Stage-4B discovery package deterministically."
    )
    parser.add_argument("--frozen-slice-csv", type=Path, required=True)
    parser.add_argument("--baseline-csv", type=Path, required=True)
    parser.add_argument(
        "--mode-csv", type=Path,
        help=(
            "Optional exact nine-mode discovery CSV. It is opened only after "
            "Criterion A passes."
        ),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = analyze(
            args.frozen_slice_csv, args.baseline_csv, args.mode_csv, args.output_dir
        )
    except HoldoutExposureError as exc:
        _write_holdout_exposure_summary(args.output_dir, exc)
        print(str(exc), file=sys.stderr)
        return 3
    except (InputContractError, FileNotFoundError, PermissionError) as exc:
        print(f"STAGE4B_ANALYSIS_INPUT_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(
        {
            "criterion_a": summary["criterion_a"]["status"],
            "criterion_b": summary["criterion_b"]["status"],
            "stage4b_conclusion": summary["stage4b_conclusion"],
            "summary": str(
                (args.output_dir / "2026-08-26_stage4B_analysis_summary.json").resolve()
            ),
        },
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
