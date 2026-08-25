#!/usr/bin/env python3
"""Fresh source-only tooling for Stage 4A-S1-R1.

The script has a positive allowlist derived from the accepted clean-room inventory,
enforces the three-sequence quarantine before opening images, and reads only the
canonical OTB JPG/GT source plus accepted v2 inputs.  It does not import or run a
tracker, checkpoint, metric, prediction, score map, or diagnostic artifact.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import math
import re
import shutil
import statistics
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageDraw, ImageFont


CLEANROOM = Path(r"F:\Q1_TrackingResearch_Data\Stage4A_S1_Cleanroom_2026-08-26_v2")
SOURCE_ROOT = Path(r"F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015")
INVENTORY = CLEANROOM / "inputs" / "project" / "2026-08-25_stage4A_E2_slice_inventory.csv"
OTB_MAPPING = CLEANROOM / "inputs" / "spiketrack_contract" / "otbdataset.py"
QUARANTINE_FILE = CLEANROOM / "outputs" / "r1" / "quarantine_filter.csv"
WORKING_ROOT = CLEANROOM / "outputs" / "r1" / "working"
CONTACT_ROOT = CLEANROOM / "outputs" / "r1" / "contact_sheets"
PROPOSAL_SPECS = WORKING_ROOT / "proposal_specs.csv"
CONTROL_SPECS = WORKING_ROOT / "control_specs.csv"
CANDIDATE_REVIEW = WORKING_ROOT / "candidate_scan_review.csv"
COMMAND_LOG = CLEANROOM / "logs" / "r1_commands.txt"
REPO_ROOT = Path(__file__).resolve().parents[3]
REPO_CODEX = REPO_ROOT / "screening" / "codex"
REPO_CONTACT_ROOT = REPO_CODEX / "artifacts" / "stage4A_S1_R1" / "contact_sheets"

QUARANTINED = frozenset({"Deer", "Crossing", "Couple"})
PHYSICAL_ALIASES = {
    # Exact non-mutating physical mappings recorded in the accepted E2 source manifest.
    "Human4_2": ("Human4/img", "Human4/groundtruth_rect.2.txt"),
    "Jogging_1": ("Jogging/img", "Jogging/groundtruth_rect.1.txt"),
    "Jogging_2": ("Jogging/img", "Jogging/groundtruth_rect.2.txt"),
    "Skating2_1": ("Skating2/img", "Skating2/groundtruth_rect.1.txt"),
    "Skating2_2": ("Skating2/img", "Skating2/groundtruth_rect.2.txt"),
}
SEARCH_FACTOR = 4.0
GREEN = (0, 230, 70)
BLUE = (20, 130, 255)
RED = (255, 45, 45)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def verify_quarantine() -> None:
    if not QUARANTINE_FILE.is_file():
        raise RuntimeError("Quarantine filter is missing; refusing all frame access")
    rows = read_csv(QUARANTINE_FILE)
    if {row["sequence"] for row in rows} != QUARANTINED:
        raise RuntimeError("Quarantine filter does not contain exactly Deer/Crossing/Couple")
    for row in rows:
        required = (
            row["candidate_pool_excluded"].lower() == "true"
            and row["control_pool_excluded"].lower() == "true"
            and row["coverage_excluded"].lower() == "true"
            and row["frames_opened"].lower() == "false"
        )
        if not required:
            raise RuntimeError(f"Invalid quarantine row: {row['sequence']}")


def load_sequence_mapping() -> dict[str, dict[str, object]]:
    tree = ast.parse(OTB_MAPPING.read_text(encoding="utf-8"), filename=str(OTB_MAPPING))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "sequence_info_list" for target in node.targets
        ):
            records = ast.literal_eval(node.value)
            return {str(record["name"]): record for record in records}
    raise RuntimeError("sequence_info_list was not found in accepted mapping")


def load_inventory_pools() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    verify_quarantine()
    inventory = read_csv(INVENTORY)
    candidates = [
        row
        for row in inventory
        if row["candidate_distractor_reason"].strip() and row["sequence"] not in QUARANTINED
    ]
    controls = [
        row
        for row in inventory
        if row["potential_control_sequence_reason"].strip() and row["sequence"] not in QUARANTINED
    ]
    if any(row["sequence"] in QUARANTINED for row in candidates + controls):
        raise RuntimeError("Quarantined sequence leaked into a scan pool")
    return candidates, controls


def parse_gt_line(line: str) -> list[float]:
    return [float(token) for token in re.split(r"[\s,\t]+", line.strip()) if token]


def load_sequence(sequence: str, mapping: dict[str, dict[str, object]]) -> tuple[dict[str, object], list[int], list[list[float]]]:
    if sequence in QUARANTINED:
        raise RuntimeError(f"Quarantined frame access refused: {sequence}")
    meta = dict(mapping[sequence])
    if sequence in PHYSICAL_ALIASES:
        meta["physical_path"], meta["physical_anno_path"] = PHYSICAL_ALIASES[sequence]
    start = int(meta["startFrame"])
    end = int(meta["endFrame"])
    omit = int(meta.get("initOmit", 0))
    frame_ids = list(range(start + omit, end + 1))
    gt_path = SOURCE_ROOT / str(meta.get("physical_anno_path", meta["anno_path"]))
    gt_all = [parse_gt_line(line) for line in gt_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    gt_rows = gt_all[omit:]
    if len(gt_rows) < len(frame_ids):
        raise RuntimeError(f"GT shorter than evaluator range for {sequence}: {len(gt_rows)} < {len(frame_ids)}")
    return meta, frame_ids, gt_rows[: len(frame_ids)]


def frame_path(meta: dict[str, object], frame_id: int) -> Path:
    width = int(meta["nz"])
    ext = str(meta["ext"])
    return SOURCE_ROOT / str(meta.get("physical_path", meta["path"])) / f"{frame_id:0{width}d}.{ext}"


def gt_bbox(row: Sequence[float]) -> tuple[float, float, float, float] | None:
    if len(row) >= 8:
        xs = row[0::2]
        ys = row[1::2]
        x, y = min(xs), min(ys)
        w, h = max(xs) - x, max(ys) - y
    elif len(row) >= 4:
        x, y, w, h = row[:4]
    else:
        return None
    if not all(math.isfinite(value) for value in (x, y, w, h)) or w <= 0 or h <= 0:
        return None
    return x, y, w, h


def nominal_search_bbox(previous_gt: Sequence[float]) -> tuple[float, float, float, float] | None:
    bbox = gt_bbox(previous_gt)
    if bbox is None:
        return None
    x, y, w, h = bbox
    side = SEARCH_FACTOR * math.sqrt(w * h)
    cx, cy = x + w / 2.0, y + h / 2.0
    return cx - side / 2.0, cy - side / 2.0, side, side


def draw_rect(draw: ImageDraw.ImageDraw, box: tuple[float, float, float, float] | None, color: tuple[int, int, int], width: int) -> None:
    if box is None:
        return
    x, y, w, h = box
    draw.rectangle((round(x), round(y), round(x + w), round(y + h)), outline=color, width=width)


def render_tile(
    image_path: Path,
    gt: Sequence[float],
    previous_gt: Sequence[float],
    label: str,
    distractor_bbox: tuple[float, float, float, float] | None = None,
    tile_size: tuple[int, int] = (320, 240),
) -> Image.Image:
    # This is the only source-frame open point.  All callers pass a positively
    # allowlisted, non-quarantined sequence after verify_quarantine().
    with Image.open(image_path) as source:
        image = source.convert("RGB")
    overlay = ImageDraw.Draw(image)
    line_width = max(2, round(max(image.size) / 300))
    draw_rect(overlay, nominal_search_bbox(previous_gt), BLUE, line_width)
    draw_rect(overlay, gt_bbox(gt), GREEN, line_width)
    draw_rect(overlay, distractor_bbox, RED, line_width)

    tile_w, tile_h = tile_size
    label_h = 24
    image.thumbnail((tile_w, tile_h - label_h), Image.Resampling.LANCZOS)
    tile = Image.new("RGB", tile_size, BLACK)
    tile.paste(image, ((tile_w - image.width) // 2, label_h + (tile_h - label_h - image.height) // 2))
    label_draw = ImageDraw.Draw(tile)
    label_draw.text((5, 5), label, fill=WHITE, font=ImageFont.load_default())
    return tile


def uniform_indices(length: int, count: int) -> list[int]:
    if length <= count:
        return list(range(length))
    return sorted({round(index * (length - 1) / (count - 1)) for index in range(count)})


def save_pages(
    sequence: str,
    meta: dict[str, object],
    frame_ids: list[int],
    gt_rows: list[list[float]],
    selected_indices: list[int],
    output_dir: Path,
    prefix: str,
    per_page: int = 25,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages: list[Path] = []
    for page_no, offset in enumerate(range(0, len(selected_indices), per_page), start=1):
        page_indices = selected_indices[offset : offset + per_page]
        tiles: list[Image.Image] = []
        for index in page_indices:
            frame_id = frame_ids[index]
            previous_gt = gt_rows[max(0, index - 1)]
            tile = render_tile(
                frame_path(meta, frame_id),
                gt_rows[index],
                previous_gt,
                f"{sequence} f{frame_id} sample {index + 1}/{len(frame_ids)}",
            )
            tiles.append(tile)
        columns = 5
        rows = math.ceil(len(tiles) / columns)
        sheet = Image.new("RGB", (columns * 320, rows * 240), (25, 25, 25))
        for tile_no, tile in enumerate(tiles):
            sheet.paste(tile, ((tile_no % columns) * 320, (tile_no // columns) * 240))
        output_path = output_dir / f"{prefix}_p{page_no:02d}.jpg"
        sheet.save(output_path, "JPEG", quality=88, optimize=True)
        pages.append(output_path)
    return pages


def command_coarse() -> None:
    candidates, _ = load_inventory_pools()
    mapping = load_sequence_mapping()
    output_dir = WORKING_ROOT / "coarse"
    coverage_rows: list[dict[str, object]] = []
    for row in candidates:
        sequence = row["sequence"]
        meta, frame_ids, gt_rows = load_sequence(sequence, mapping)
        inventory_count = int(row["frame_count"])
        if inventory_count != len(frame_ids):
            raise RuntimeError(f"Inventory/mapping frame-count mismatch for {sequence}")
        selected_indices = list(range(len(frame_ids))) if len(frame_ids) < 125 else uniform_indices(len(frame_ids), 25)
        pages = save_pages(
            sequence,
            meta,
            frame_ids,
            gt_rows,
            selected_indices,
            output_dir / sequence,
            f"{sequence}_coarse",
        )
        coverage_rows.append(
            {
                "sequence": sequence,
                "frame_count": len(frame_ids),
                "scan_rule": "EVERY_FRAME" if len(frame_ids) < 125 else "UNIFORM_25",
                "required_frame_count": len(frame_ids) if len(frame_ids) < 125 else 25,
                "generated_frame_count": len(selected_indices),
                "source_frame_ids": "|".join(str(frame_ids[index]) for index in selected_indices),
                "page_paths": "|".join(str(path.relative_to(CLEANROOM)) for path in pages),
                "quarantine_filter_verified": "true",
                "visual_review_status": "PENDING",
            }
        )
    write_csv(
        WORKING_ROOT / "candidate_scan_coverage.csv",
        [
            "sequence",
            "frame_count",
            "scan_rule",
            "required_frame_count",
            "generated_frame_count",
            "source_frame_ids",
            "page_paths",
            "quarantine_filter_verified",
            "visual_review_status",
        ],
        coverage_rows,
    )
    print(f"Generated source-only coarse scans for {len(coverage_rows)} candidates")
    print(f"Coverage: {WORKING_ROOT / 'candidate_scan_coverage.csv'}")


def command_detail(sequence: str, start_frame: int, end_frame: int) -> None:
    candidates, controls = load_inventory_pools()
    allowed_names = {row["sequence"] for row in candidates + controls}
    if sequence not in allowed_names:
        raise RuntimeError(f"Sequence is not in a positively allowlisted R1 pool: {sequence}")
    mapping = load_sequence_mapping()
    meta, frame_ids, gt_rows = load_sequence(sequence, mapping)
    selected_indices = [index for index, frame_id in enumerate(frame_ids) if start_frame <= frame_id <= end_frame]
    if not selected_indices:
        raise RuntimeError("Requested detail interval has no evaluator frames")
    output_dir = WORKING_ROOT / "detail" / f"{sequence}_{start_frame}_{end_frame}"
    pages = save_pages(sequence, meta, frame_ids, gt_rows, selected_indices, output_dir, f"{sequence}_{start_frame}_{end_frame}")
    for path in pages:
        print(path)


def command_control_coarse(sequences: Sequence[str]) -> None:
    _, controls = load_inventory_pools()
    control_names = {row["sequence"] for row in controls}
    requested = list(dict.fromkeys(sequences))
    disallowed = [sequence for sequence in requested if sequence not in control_names]
    if disallowed:
        raise RuntimeError(f"Not in the positive control allowlist: {disallowed}")
    mapping = load_sequence_mapping()
    output_dir = WORKING_ROOT / "control_coarse"
    for sequence in requested:
        meta, frame_ids, gt_rows = load_sequence(sequence, mapping)
        selected_indices = list(range(len(frame_ids))) if len(frame_ids) < 125 else uniform_indices(len(frame_ids), 25)
        pages = save_pages(
            sequence,
            meta,
            frame_ids,
            gt_rows,
            selected_indices,
            output_dir / sequence,
            f"{sequence}_control_coarse",
        )
        print(f"{sequence}: {len(selected_indices)} frames -> {len(pages)} page(s)")


def command_annotation(sequence: str, frame_id: int) -> None:
    candidates, controls = load_inventory_pools()
    allowed_names = {row["sequence"] for row in candidates + controls}
    if sequence not in allowed_names:
        raise RuntimeError(f"Sequence is not in a positively allowlisted R1 pool: {sequence}")
    mapping = load_sequence_mapping()
    meta, frame_ids, gt_rows = load_sequence(sequence, mapping)
    if frame_id not in frame_ids:
        raise RuntimeError(f"Frame {frame_id} is outside the evaluator range for {sequence}")
    index = frame_ids.index(frame_id)
    source_path = frame_path(meta, frame_id)
    with Image.open(source_path) as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image)
    line_width = max(2, round(max(image.size) / 300))
    draw_rect(draw, nominal_search_bbox(gt_rows[max(0, index - 1)]), BLUE, line_width)
    draw_rect(draw, gt_bbox(gt_rows[index]), GREEN, line_width)
    grid_step = 50 if max(image.size) <= 800 else 100
    for x in range(0, image.width, grid_step):
        draw.line((x, 0, x, image.height), fill=(150, 150, 150), width=1)
        draw.text((x + 2, 2), str(x), fill=WHITE, stroke_width=1, stroke_fill=BLACK)
    for y in range(0, image.height, grid_step):
        draw.line((0, y, image.width, y), fill=(150, 150, 150), width=1)
        draw.text((2, y + 2), str(y), fill=WHITE, stroke_width=1, stroke_fill=BLACK)
    output_dir = WORKING_ROOT / "annotation"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{sequence}_{frame_id}_grid.png"
    image.save(output_path, "PNG", optimize=True)
    print(f"path={output_path}")
    print(f"source_size={image.width}x{image.height}")
    print(f"gt_bbox={gt_bbox(gt_rows[index])}")
    print(f"nominal_search_bbox={nominal_search_bbox(gt_rows[max(0, index - 1)])}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_bbox_text(value: str) -> tuple[float, float, float, float]:
    numbers = [float(token) for token in re.split(r"[\s,]+", value.strip()) if token]
    if len(numbers) != 4 or numbers[2] <= 0 or numbers[3] <= 0:
        raise RuntimeError(f"Invalid manual distractor bbox: {value!r}")
    return numbers[0], numbers[1], numbers[2], numbers[3]


def interval_indices(frame_ids: Sequence[int], start: int, end: int) -> list[int]:
    indices = [index for index, frame_id in enumerate(frame_ids) if start <= frame_id <= end]
    if not indices or frame_ids[indices[0]] != start or frame_ids[indices[-1]] != end:
        raise RuntimeError(f"Interval {start}-{end} is not contiguous in evaluator frames")
    return indices


def percentile(values: Sequence[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = quantile * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def interval_stats(
    sequence: str,
    start: int,
    end: int,
    mapping: dict[str, dict[str, object]],
) -> dict[str, object]:
    meta, frame_ids, gt_rows = load_sequence(sequence, mapping)
    indices = interval_indices(frame_ids, start, end)
    first_image = frame_path(meta, frame_ids[indices[0]])
    with Image.open(first_image) as image:
        image_area = float(image.width * image.height)
    boxes = [gt_bbox(gt_rows[index]) for index in indices]
    if any(box is None for box in boxes):
        raise RuntimeError(f"Invalid GT in {sequence} {start}-{end}")
    valid_boxes = [box for box in boxes if box is not None]
    areas = [box[2] * box[3] for box in valid_boxes]
    area_ratios = [area / image_area for area in areas]
    centers = [(box[0] + box[2] / 2.0, box[1] + box[3] / 2.0) for box in valid_boxes]
    motions = [math.dist(centers[index - 1], centers[index]) for index in range(1, len(centers))]
    normalized_motion = [
        motions[index - 1] / max(1.0, math.sqrt(areas[index - 1])) for index in range(1, len(areas))
    ]
    log_scale_steps = [abs(math.log(areas[index] / areas[index - 1])) for index in range(1, len(areas))]
    median_area_ratio = statistics.median(area_ratios)
    p90_norm = percentile(normalized_motion, 0.9)
    return {
        "target_area_ratio_summary": (
            f"median={median_area_ratio:.6f};min={min(area_ratios):.6f};max={max(area_ratios):.6f}"
        ),
        "gt_motion_summary": (
            f"median_px={statistics.median(motions) if motions else 0.0:.3f};"
            f"p90_px={percentile(motions, 0.9):.3f};p90_target_norm={p90_norm:.3f}"
        ),
        "scale_change_summary": (
            f"end_to_start_area={areas[-1] / areas[0]:.3f};"
            f"max_to_min_area={max(areas) / min(areas):.3f};"
            f"median_abs_log_step={statistics.median(log_scale_steps) if log_scale_steps else 0.0:.4f}"
        ),
        "fast_motion_from_gt": "true" if p90_norm > 1.0 else "false",
        "low_resolution_from_gt": "true" if median_area_ratio < 0.001 else "false",
        "meta": meta,
        "frame_ids": frame_ids,
        "gt_rows": gt_rows,
        "indices": indices,
    }


def five_frame_indices(indices: Sequence[int]) -> list[int]:
    if len(indices) < 5:
        raise RuntimeError("Contact-sheet interval must contain at least five frames")
    positions = [0.0, 0.25, 0.5, 0.75, 1.0]
    return [indices[round(position * (len(indices) - 1))] for position in positions]


def build_final_sheet(
    item_id: str,
    sequence: str,
    start: int,
    end: int,
    mapping: dict[str, dict[str, object]],
    output_path: Path,
    midpoint_bbox: tuple[float, float, float, float] | None,
) -> tuple[list[int], int, int]:
    meta, frame_ids, gt_rows = load_sequence(sequence, mapping)
    selected = five_frame_indices(interval_indices(frame_ids, start, end))
    midpoint_index = selected[2]
    tiles: list[Image.Image] = []
    for index in selected:
        frame_id = frame_ids[index]
        tiles.append(
            render_tile(
                frame_path(meta, frame_id),
                gt_rows[index],
                gt_rows[max(0, index - 1)],
                f"{item_id} | {sequence} f{frame_id}",
                midpoint_bbox if index == midpoint_index else None,
                tile_size=(340, 300),
            )
        )
    sheet = Image.new("RGB", (1700, 300), (25, 25, 25))
    for tile_no, tile in enumerate(tiles):
        sheet.paste(tile, (tile_no * 340, 0))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, "JPEG", quality=90, optimize=True)
    return [frame_ids[index] for index in selected], sheet.width, sheet.height


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value).replace("|", "/") for value in row) + " |")
    return "\n".join(lines)


def command_finalize() -> None:
    verify_quarantine()
    if not all(path.is_file() for path in (PROPOSAL_SPECS, CONTROL_SPECS, CANDIDATE_REVIEW, COMMAND_LOG)):
        raise RuntimeError("Fresh proposal/control/review specs and command log are required")
    proposals = read_csv(PROPOSAL_SPECS)
    controls = read_csv(CONTROL_SPECS)
    reviews = read_csv(CANDIDATE_REVIEW)
    candidates, control_pool = load_inventory_pools()
    inventory_rows = read_csv(INVENTORY)
    inventory = {row["sequence"]: row for row in inventory_rows}
    candidate_names = {row["sequence"] for row in candidates}
    control_names = {row["sequence"] for row in control_pool}
    mapping = load_sequence_mapping()

    if len(reviews) != len(candidates) or {row["sequence"] for row in reviews} != candidate_names:
        raise RuntimeError("Candidate review must cover all and only the 44 filtered candidate leads")
    if any(row["visual_review_status"] != "REVIEWED" for row in reviews):
        raise RuntimeError("Every candidate coarse scan must be marked REVIEWED")
    proposal_ids = [row["proposal_id"] for row in proposals]
    if len(proposal_ids) != len(set(proposal_ids)):
        raise RuntimeError("Duplicate proposal IDs")
    if len({row["sequence"] for row in proposals}) < 10:
        raise RuntimeError("Fewer than 10 unique primary distractor sequences")
    if any(row["sequence"] not in candidate_names for row in proposals):
        raise RuntimeError("Proposal sequence outside positive candidate allowlist")
    if any(row["sequence"] in QUARANTINED for row in proposals + controls):
        raise RuntimeError("Quarantined sequence leaked into final specs")
    if len(controls) != len(proposals) or {row["linked_proposal_id"] for row in controls} != set(proposal_ids):
        raise RuntimeError("Every proposal must have exactly one linked control")
    if any(row["sequence"] not in candidate_names | control_names for row in controls):
        raise RuntimeError("Control sequence outside positive candidate/control allowlists")
    discovery = {row["sequence"] for row in proposals if row["proposed_split"] == "DISCOVERY_CANDIDATE"}
    holdout = {row["sequence"] for row in proposals if row["proposed_split"] == "HOLDOUT_CANDIDATE"}
    if discovery & holdout or len(discovery) < 6 or len(holdout) < 4:
        raise RuntimeError("Proposed split is not sequence-disjoint with 6/4 coverage")
    superclasses = [row["broad_superclass"] for row in proposals]
    if len(set(superclasses)) < 3:
        raise RuntimeError("Fewer than three broad superclasses")
    if max(superclasses.count(name) for name in set(superclasses)) / len(proposals) > 0.60:
        raise RuntimeError("A broad superclass exceeds 60 percent")

    proposal_output_rows: list[dict[str, object]] = []
    control_output_rows: list[dict[str, object]] = []
    manifest_rows: list[dict[str, object]] = []
    expected_sheet_paths: list[Path] = []

    for row in proposals:
        start, end = int(row["interval_start"]), int(row["interval_end"])
        length = end - start + 1
        if not 5 <= length <= 40:
            raise RuntimeError(f"Proposal interval outside 5-40 frames: {row['proposal_id']}")
        if row["evidence_tier"] not in {"TIER_A", "TIER_B"}:
            raise RuntimeError("Primary proposals must be TIER_A or TIER_B")
        if row["search_context_status"] not in {"INSIDE_NOMINAL_SEARCH", "NEAR_SEARCH_BOUNDARY"}:
            raise RuntimeError("Primary proposal is outside/unresolved nominal search context")
        stats = interval_stats(row["sequence"], start, end, mapping)
        bbox = parse_bbox_text(row["midpoint_distractor_bbox"])
        filename = f"{row['proposal_id']}_{row['sequence']}_{start}_{end}.jpg"
        external_sheet = CONTACT_ROOT / filename
        source_frames, width, height = build_final_sheet(
            row["proposal_id"], row["sequence"], start, end, mapping, external_sheet, bbox
        )
        expected_sheet_paths.append(external_sheet)
        repo_relative = Path("screening") / "codex" / "artifacts" / "stage4A_S1_R1" / "contact_sheets" / filename
        item = inventory[row["sequence"]]
        proposal_output_rows.append(
            {
                "proposal_id": row["proposal_id"],
                "dataset": "OTB100",
                "sequence": row["sequence"],
                "broad_superclass": row["broad_superclass"],
                "object_class": item["object_class"],
                "official_attributes": item["official_attributes"],
                "interval_start": start,
                "interval_end": end,
                "interval_length": length,
                "evidence_tier": row["evidence_tier"],
                "distractor_description": row["distractor_description"],
                "similarity_basis": row["similarity_basis"],
                "search_context_status": row["search_context_status"],
                "midpoint_distractor_bbox_or_na": row["midpoint_distractor_bbox"],
                "target_visibility": row["target_visibility"],
                "occlusion_state": row["occlusion_state"],
                "fast_motion_from_gt": stats["fast_motion_from_gt"],
                "low_resolution_from_gt": stats["low_resolution_from_gt"],
                "scan_method": row["scan_method"],
                "proposed_split": row["proposed_split"],
                "contact_sheet_path": repo_relative.as_posix(),
                "manager_review_status": "PENDING",
                "notes": row["notes"],
            }
        )
        manifest_rows.append(
            {
                "sheet_id": f"SHEET-{row['proposal_id']}",
                "proposal_or_control_id": row["proposal_id"],
                "relative_path": repo_relative.as_posix(),
                "sha256": sha256_file(external_sheet),
                "byte_size": external_sheet.stat().st_size,
                "width": width,
                "height": height,
                "source_sequence": row["sequence"],
                "source_frame_ids": "|".join(str(value) for value in source_frames),
                "overlays": "GT_TARGET_GREEN|NOMINAL_SEARCH_BLUE|MIDPOINT_DISTRACTOR_RED",
                "manager_review_status": "PENDING",
            }
        )

    proposal_by_id = {row["proposal_id"]: row for row in proposals}
    for row in controls:
        start, end = int(row["interval_start"]), int(row["interval_end"])
        length = end - start + 1
        if length < 5:
            raise RuntimeError(f"Control shorter than five frames: {row['control_id']}")
        stats = interval_stats(row["sequence"], start, end, mapping)
        filename = f"{row['control_id']}_{row['sequence']}_{start}_{end}.jpg"
        external_sheet = CONTACT_ROOT / filename
        source_frames, width, height = build_final_sheet(
            row["control_id"], row["sequence"], start, end, mapping, external_sheet, None
        )
        expected_sheet_paths.append(external_sheet)
        repo_relative = Path("screening") / "codex" / "artifacts" / "stage4A_S1_R1" / "contact_sheets" / filename
        item = inventory[row["sequence"]]
        linked = proposal_by_id[row["linked_proposal_id"]]
        control_output_rows.append(
            {
                "control_id": row["control_id"],
                "linked_proposal_id": row["linked_proposal_id"],
                "dataset": "OTB100",
                "sequence": row["sequence"],
                "interval_start": start,
                "interval_end": end,
                "interval_length": length,
                "same_sequence": row["same_sequence"],
                "object_class": item["object_class"],
                "broad_superclass": linked["broad_superclass"],
                "target_area_ratio_summary": stats["target_area_ratio_summary"],
                "gt_motion_summary": stats["gt_motion_summary"],
                "scale_change_summary": stats["scale_change_summary"],
                "occlusion_match": row["occlusion_match"],
                "attribute_match": row["attribute_match"],
                "no_similar_distractor_evidence": row["no_similar_distractor_evidence"],
                "matching_basis": row["matching_basis"],
                "contact_sheet_path": repo_relative.as_posix(),
                "manager_review_status": "PENDING",
                "notes": row["notes"],
            }
        )
        manifest_rows.append(
            {
                "sheet_id": f"SHEET-{row['control_id']}",
                "proposal_or_control_id": row["control_id"],
                "relative_path": repo_relative.as_posix(),
                "sha256": sha256_file(external_sheet),
                "byte_size": external_sheet.stat().st_size,
                "width": width,
                "height": height,
                "source_sequence": row["sequence"],
                "source_frame_ids": "|".join(str(value) for value in source_frames),
                "overlays": "GT_TARGET_GREEN|NOMINAL_SEARCH_BLUE",
                "manager_review_status": "PENDING",
            }
        )

    proposal_fields = [
        "proposal_id", "dataset", "sequence", "broad_superclass", "object_class", "official_attributes",
        "interval_start", "interval_end", "interval_length", "evidence_tier", "distractor_description",
        "similarity_basis", "search_context_status", "midpoint_distractor_bbox_or_na", "target_visibility",
        "occlusion_state", "fast_motion_from_gt", "low_resolution_from_gt", "scan_method", "proposed_split",
        "contact_sheet_path", "manager_review_status", "notes",
    ]
    control_fields = [
        "control_id", "linked_proposal_id", "dataset", "sequence", "interval_start", "interval_end",
        "interval_length", "same_sequence", "object_class", "broad_superclass", "target_area_ratio_summary",
        "gt_motion_summary", "scale_change_summary", "occlusion_match", "attribute_match",
        "no_similar_distractor_evidence", "matching_basis", "contact_sheet_path", "manager_review_status", "notes",
    ]
    manifest_fields = [
        "sheet_id", "proposal_or_control_id", "relative_path", "sha256", "byte_size", "width", "height",
        "source_sequence", "source_frame_ids", "overlays", "manager_review_status",
    ]
    external_proposals = CLEANROOM / "outputs" / "r1" / "distractor_interval_proposals.csv"
    external_controls = CLEANROOM / "outputs" / "r1" / "control_interval_proposals.csv"
    external_manifest = CLEANROOM / "outputs" / "r1" / "contact_sheet_manifest.csv"
    write_csv(external_proposals, proposal_fields, proposal_output_rows)
    write_csv(external_controls, control_fields, control_output_rows)
    write_csv(external_manifest, manifest_fields, manifest_rows)

    tier_a = sum(row["evidence_tier"] == "TIER_A" for row in proposals)
    tier_b = sum(row["evidence_tier"] == "TIER_B" for row in proposals)
    payload_bytes = sum(path.stat().st_size for path in expected_sheet_paths)
    if payload_bytes > 30 * 1024 * 1024:
        raise RuntimeError("Contact-sheet payload exceeds 30 MiB")
    superclass_counts = {name: superclasses.count(name) for name in sorted(set(superclasses))}
    report = f"""# Stage 4A-S1-R1 — Source-only interval proposal report

**Date:** 2026-08-26  
**Status:** `S1_R1_COMPLETE_READY_FOR_MANAGER_VISUAL_REVIEW`  
**Decision scope:** all intervals, tiers, controls, and split labels below are provisional proposals with `manager_review_status=PENDING`.

## 1. Boundary and prohibited-source declaration

This was a fresh Codex lane. No previous S1 scan, judgment, selection, script, or temporary output was reused. Scientific selection used only the accepted v2 clean-room inputs and canonical OTB JPG/GT source. SpikeTrack was not run; no checkpoint/model was instantiated; no prediction, AUC, IoU, success/failure record, score/confidence map, MRM log, ablation result, reproduction result, or tracker-derived ranking was accessed.

## 2. Outcome-exposure quarantine declaration

`Deer`, `Crossing`, and `Couple` were filtered before any frame path was opened. They were excluded from candidate, control, coverage, and split pools. Their `frames_opened` values remain `false`. The invalid v1 clean-room root was not accessed.

## 3. Source dataset and hash identity

- canonical root: `F:\\Q1_TrackingResearch_Data\\OTB100_Figshare_24427468_v1\\extracted\\OTB2015\\`
- archive SHA-256: `aad6be170d417777a5cee0b99bdd367e540b81f9020ac08b5c96d4d5d5094be5`
- extracted-file-manifest SHA-256: `a58329bea07dc96f9d35ad5d2a22785e23198f90c451da6369f7eaa985625032`
- evaluator mapping: accepted v2 copy of pinned `otbdataset.py`
- nominal context: previous-frame GT center with square side `4.0 * sqrt(GT_width * GT_height)`; source-selection aid only

## 4. Candidate-sequence scan coverage

All **{len(candidates)}** non-quarantined candidate leads were rescanned from zero. Sequences with at least 125 frames used 25 uniformly spaced frames; `Bird2`, `Football1`, and `Matrix` used every frame because they have fewer than 125. The machine coverage file records **1,298/1,298** required coarse frames, followed by frame-by-frame refinement for proposed events.

{markdown_table(['Sequence', 'Coarse assessment', 'Primary status', 'Review note'], [[row['sequence'], row['coarse_assessment'], row['primary_status'], row['review_summary']] for row in reviews])}

## 5. Tier A/B/C counts

- proposed Tier A: **{tier_a}**
- proposed Tier B: **{tier_b}**
- proposed Tier C: **0**
- Tier C/rejected/ambiguous coarse leads were retained only in the review table and do not satisfy primary coverage.

## 6. Distractor interval proposal summary

{markdown_table(['ID', 'Sequence', 'Frames', 'Tier', 'Search', 'Split'], [[row['proposal_id'], row['sequence'], f"{row['interval_start']}-{row['interval_end']}", row['evidence_tier'], row['search_context_status'], row['proposed_split']] for row in proposals])}

## 7. Control proposal summary

Every primary proposal has one visually rescanned control selected without tracker behavior. GT-derived area, center-motion, and scale summaries are in the control CSV.

{markdown_table(['Control', 'Linked', 'Sequence', 'Frames', 'Same sequence'], [[row['control_id'], row['linked_proposal_id'], row['sequence'], f"{row['interval_start']}-{row['interval_end']}", row['same_sequence']] for row in controls])}

## 8. Superclass diversity

- unique primary sequences: **{len(set(row['sequence'] for row in proposals))}**
- broad superclasses: **{len(superclass_counts)}** — {', '.join(f'{key}={value}' for key, value in superclass_counts.items())}
- maximum superclass share: **{max(superclass_counts.values()) / len(proposals):.1%}**

## 9. Proposed discovery/hold-out candidate split

- discovery candidates ({len(discovery)}): {', '.join(sorted(discovery))}
- hold-out candidates ({len(holdout)}): {', '.join(sorted(holdout))}
- intersection: empty
- status: `SEQUENCE_DISJOINT_PASS`

This is a provisional candidate grouping, not the frozen Manager split.

## 10. Contact-sheet coverage and payload size

- proposal sheets: {len(proposals)}
- control sheets: {len(controls)}
- total sheets: **{len(manifest_rows)}**
- total bytes: **{payload_bytes}** ({payload_bytes / (1024 * 1024):.2f} MiB)
- dimensions: 1700 x 300 pixels each
- overlays: source JPG + GT target (green) + GT-derived nominal search context (blue); proposal midpoint manual distractor box (red)
- forbidden overlays: none

## 11. Ambiguous/rejected cases

- `Matrix` passed visual continuity but was withheld from primary coverage because the similar opponent remained centered outside the nominal blue search region.
- `Board` remains a provisional Tier B proposal; source-only imagery cannot prove that the flat PCB is physically independent from the raised assembly, so Manager visual review may reject it.
- `Bird2`, `BlurCar1`, `BlurCar3`, `Car1`, and `Walking` were not counted because only Tier C/weak evidence remained after fresh review.
- `Car2`, `Human2`, `Human6`, `Lemming`, and `Singer2` were rejected for lack of a credible continuous similar distractor.
- `Dog 20-40` and the late portion of `Skiing 20-40` were rejected as controls after frame-by-frame review revealed additional similar non-targets. They do not appear in the control CSV.
- Additional strong coarse leads were not promoted where the 12-sequence package already met diversity and payload constraints; this is not a tracker-based ranking.

## 12. Exact remaining coverage gaps

No proposal-level minimum is missing: at least 10 unique sequences, at least 3 superclasses, 6+ discovery candidates, 4+ hold-out candidates, one control per primary proposal, and sequence disjointness all pass. Remaining work is Manager visual review and possible bound/control adjustment. No interval, tier, or split is frozen.

## 13. Files produced

- `screening/codex/2026-08-26_stage4A_S1_R1_quarantine_filter.csv`
- `screening/codex/2026-08-26_stage4A_S1_R1_distractor_interval_proposals.csv`
- `screening/codex/2026-08-26_stage4A_S1_R1_control_interval_proposals.csv`
- `screening/codex/2026-08-26_stage4A_S1_R1_contact_sheet_manifest.csv`
- `screening/codex/2026-08-26_stage4A_S1_R1_slice_proposal_report.md`
- `screening/codex/2026-08-26_stage4A_S1_R1_command_log.txt`
- `screening/codex/artifacts/stage4A_S1_R1/contact_sheets/` ({len(manifest_rows)} JPEGs)
- `screening/codex/scripts/2026-08-26_stage4A_S1_R1_build_proposals.py`

## 14. Readiness conclusion

`S1_R1_COMPLETE_READY_FOR_MANAGER_VISUAL_REVIEW`

FROZEN DIAGNOSTIC SLICE: **NOT CREATED**  
STAGE 4B: **LOCKED**  
DIAG PASS/FAIL: **NOT ASSIGNED**  
S1-S7: **NOT STARTED**  
PRIMARY SHORTLIST: **NONE**  
MAIN BASELINE: **NONE**  
PROPOSED ARCHITECTURE: **NONE**
"""
    external_report = CLEANROOM / "outputs" / "r1" / "slice_proposal_report.md"
    external_report.write_text(report, encoding="utf-8")

    REPO_CONTACT_ROOT.mkdir(parents=True, exist_ok=True)
    for path in expected_sheet_paths:
        shutil.copy2(path, REPO_CONTACT_ROOT / path.name)
    file_pairs = [
        (QUARANTINE_FILE, REPO_CODEX / "2026-08-26_stage4A_S1_R1_quarantine_filter.csv"),
        (external_proposals, REPO_CODEX / "2026-08-26_stage4A_S1_R1_distractor_interval_proposals.csv"),
        (external_controls, REPO_CODEX / "2026-08-26_stage4A_S1_R1_control_interval_proposals.csv"),
        (external_manifest, REPO_CODEX / "2026-08-26_stage4A_S1_R1_contact_sheet_manifest.csv"),
        (external_report, REPO_CODEX / "2026-08-26_stage4A_S1_R1_slice_proposal_report.md"),
        (COMMAND_LOG, REPO_CODEX / "2026-08-26_stage4A_S1_R1_command_log.txt"),
    ]
    for source, destination in file_pairs:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    print(f"proposals={len(proposals)} tier_a={tier_a} tier_b={tier_b}")
    print(f"controls={len(controls)} contact_sheets={len(manifest_rows)} bytes={payload_bytes}")
    print("split=SEQUENCE_DISJOINT_PASS")


def command_validate() -> None:
    verify_quarantine()
    external_proposals = CLEANROOM / "outputs" / "r1" / "distractor_interval_proposals.csv"
    external_controls = CLEANROOM / "outputs" / "r1" / "control_interval_proposals.csv"
    external_manifest = CLEANROOM / "outputs" / "r1" / "contact_sheet_manifest.csv"
    external_report = CLEANROOM / "outputs" / "r1" / "slice_proposal_report.md"
    coverage_path = WORKING_ROOT / "candidate_scan_coverage.csv"
    required = [external_proposals, external_controls, external_manifest, external_report, coverage_path, COMMAND_LOG]
    if not all(path.is_file() for path in required):
        raise RuntimeError("One or more external R1 outputs are missing")
    proposals = read_csv(external_proposals)
    controls = read_csv(external_controls)
    manifest = read_csv(external_manifest)
    coverage = read_csv(coverage_path)
    quarantine_names = {"Deer", "Crossing", "Couple"}
    if any(row["sequence"] in quarantine_names for row in proposals + controls):
        raise RuntimeError("Quarantined sequence appears in proposal/control output")
    if len(coverage) != 44:
        raise RuntimeError("Candidate scan coverage is not 44 sequences")
    generated = sum(int(row["generated_frame_count"]) for row in coverage)
    required_frames = sum(int(row["required_frame_count"]) for row in coverage)
    if generated != required_frames or generated != 1298:
        raise RuntimeError(f"Coarse frame coverage mismatch: {generated}/{required_frames}")
    if len(proposals) < 10 or len({row["sequence"] for row in proposals}) != len(proposals):
        raise RuntimeError("Primary sequence count/uniqueness failed")
    if any(int(row["interval_length"]) < 5 for row in proposals):
        raise RuntimeError("A primary interval is shorter than five frames")
    if len(controls) != len(proposals) or {row["linked_proposal_id"] for row in controls} != {
        row["proposal_id"] for row in proposals
    }:
        raise RuntimeError("Proposal/control linkage failed")
    discovery = {row["sequence"] for row in proposals if row["proposed_split"] == "DISCOVERY_CANDIDATE"}
    holdout = {row["sequence"] for row in proposals if row["proposed_split"] == "HOLDOUT_CANDIDATE"}
    if discovery & holdout or len(discovery) < 6 or len(holdout) < 4:
        raise RuntimeError("Proposed split validation failed")
    superclasses = {row["broad_superclass"] for row in proposals}
    if len(superclasses) < 3:
        raise RuntimeError("Superclass diversity failed")
    if any(row["manager_review_status"] != "PENDING" for row in proposals + controls + manifest):
        raise RuntimeError("Manager review status is not uniformly PENDING")
    if len(manifest) != len(proposals) + len(controls):
        raise RuntimeError("Contact-sheet manifest row count failed")
    payload = 0
    for row in manifest:
        repo_path = REPO_ROOT / Path(row["relative_path"])
        external_path = CONTACT_ROOT / repo_path.name
        if not repo_path.is_file() or not external_path.is_file():
            raise RuntimeError(f"Missing contact sheet: {repo_path.name}")
        expected_hash = row["sha256"]
        if sha256_file(repo_path) != expected_hash or sha256_file(external_path) != expected_hash:
            raise RuntimeError(f"Contact-sheet hash mismatch: {repo_path.name}")
        if repo_path.stat().st_size != int(row["byte_size"]):
            raise RuntimeError(f"Contact-sheet size mismatch: {repo_path.name}")
        if max(int(row["width"]), int(row["height"])) > 1800:
            raise RuntimeError(f"Contact-sheet dimensions exceed contract: {repo_path.name}")
        payload += repo_path.stat().st_size
    if payload > 30 * 1024 * 1024:
        raise RuntimeError("Committed contact-sheet payload exceeds 30 MiB")
    report_text = external_report.read_text(encoding="utf-8")
    locked_tokens = [
        "FROZEN DIAGNOSTIC SLICE: **NOT CREATED**",
        "STAGE 4B: **LOCKED**",
        "DIAG PASS/FAIL: **NOT ASSIGNED**",
        "S1-S7: **NOT STARTED**",
        "PRIMARY SHORTLIST: **NONE**",
        "MAIN BASELINE: **NONE**",
        "PROPOSED ARCHITECTURE: **NONE**",
    ]
    if not all(token in report_text for token in locked_tokens):
        raise RuntimeError("Locked downstream state is incomplete in report")
    file_pairs = [
        (QUARANTINE_FILE, REPO_CODEX / "2026-08-26_stage4A_S1_R1_quarantine_filter.csv"),
        (external_proposals, REPO_CODEX / "2026-08-26_stage4A_S1_R1_distractor_interval_proposals.csv"),
        (external_controls, REPO_CODEX / "2026-08-26_stage4A_S1_R1_control_interval_proposals.csv"),
        (external_manifest, REPO_CODEX / "2026-08-26_stage4A_S1_R1_contact_sheet_manifest.csv"),
        (external_report, REPO_CODEX / "2026-08-26_stage4A_S1_R1_slice_proposal_report.md"),
        (COMMAND_LOG, REPO_CODEX / "2026-08-26_stage4A_S1_R1_command_log.txt"),
    ]
    for external, repo in file_pairs:
        if not repo.is_file() or sha256_file(external) != sha256_file(repo):
            raise RuntimeError(f"External/Q1 copy mismatch: {repo.name}")
    print("quarantine_filter=PASS frames_opened=false")
    print(f"candidate_sequences_scanned={len(coverage)} coarse_frames={generated}")
    print(f"proposals={len(proposals)} controls={len(controls)} superclasses={len(superclasses)}")
    print(f"discovery={len(discovery)} holdout={len(holdout)} split=SEQUENCE_DISJOINT_PASS")
    print(f"contact_sheets={len(manifest)} bytes={payload} payload_cap=PASS")
    print("outcome_evidence=NONE stage4b=LOCKED validation=PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("coarse")
    control_coarse = subparsers.add_parser("control-coarse")
    control_coarse.add_argument("sequences", nargs="+")
    annotation = subparsers.add_parser("annotation")
    annotation.add_argument("sequence")
    annotation.add_argument("frame_id", type=int)
    subparsers.add_parser("finalize")
    subparsers.add_parser("validate")
    detail = subparsers.add_parser("detail")
    detail.add_argument("sequence")
    detail.add_argument("start_frame", type=int)
    detail.add_argument("end_frame", type=int)
    args = parser.parse_args()

    if args.command == "coarse":
        command_coarse()
    elif args.command == "control-coarse":
        command_control_coarse(args.sequences)
    elif args.command == "annotation":
        command_annotation(args.sequence, args.frame_id)
    elif args.command == "finalize":
        command_finalize()
    elif args.command == "validate":
        command_validate()
    elif args.command == "detail":
        command_detail(args.sequence, args.start_frame, args.end_frame)


if __name__ == "__main__":
    main()
