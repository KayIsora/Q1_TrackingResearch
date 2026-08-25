#!/usr/bin/env python3
"""Build and validate the source-only Stage 4A-S1-R2 control-rematch package.

Scientific inputs are restricted to the accepted v2 clean room and canonical
OTB JPG/GT source.  The script has no tracker/model imports and no result-path
inputs.  Deer, Crossing, and Couple are rejected before any frame access.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import math
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageDraw, ImageFont


CLEANROOM = Path(r"F:\Q1_TrackingResearch_Data\Stage4A_S1_Cleanroom_2026-08-26_v2")
SOURCE_ROOT = Path(r"F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015")
INVENTORY = CLEANROOM / "inputs" / "project" / "2026-08-25_stage4A_E2_slice_inventory.csv"
OTB_MAPPING = CLEANROOM / "inputs" / "spiketrack_contract" / "otbdataset.py"
QUARANTINE_FILE = CLEANROOM / "outputs" / "r1" / "quarantine_filter.csv"
R1_PROPOSALS = CLEANROOM / "outputs" / "r1" / "distractor_interval_proposals.csv"

REPO_ROOT = Path(__file__).resolve().parents[3]
CODEX_ROOT = REPO_ROOT / "screening" / "codex"
PAIR_ROOT = CODEX_ROOT / "artifacts" / "stage4A_S1_R2" / "pair_sheets"
PROPOSAL_CSV = CODEX_ROOT / "2026-08-26_stage4A_S1_R2_revised_distractor_intervals.csv"
CONTROL_CSV = CODEX_ROOT / "2026-08-26_stage4A_S1_R2_revised_controls.csv"
AUDIT_CSV = CODEX_ROOT / "2026-08-26_stage4A_S1_R2_pair_matching_audit.csv"
MANIFEST_CSV = CODEX_ROOT / "2026-08-26_stage4A_S1_R2_pair_sheet_manifest.csv"
REPORT_MD = CODEX_ROOT / "2026-08-26_stage4A_S1_R2_control_rematch_report.md"
COMMAND_LOG = CODEX_ROOT / "2026-08-26_stage4A_S1_R2_command_log.txt"

QUARANTINED = frozenset({"Deer", "Crossing", "Couple"})
RETAINED_IDS = (
    "R1-P01", "R1-P02", "R1-P03", "R1-P04", "R1-P05",
    "R1-P07", "R1-P09", "R1-P10", "R1-P11", "R1-P12",
)
REJECTED_IDS = frozenset({"R1-P06", "R1-P08"})
PHYSICAL_ALIASES = {
    "Human4_2": ("Human4/img", "Human4/groundtruth_rect.2.txt"),
    "Jogging_1": ("Jogging/img", "Jogging/groundtruth_rect.1.txt"),
    "Jogging_2": ("Jogging/img", "Jogging/groundtruth_rect.2.txt"),
    "Skating2_1": ("Skating2/img", "Skating2/groundtruth_rect.1.txt"),
    "Skating2_2": ("Skating2/img", "Skating2/groundtruth_rect.2.txt"),
}

SEARCH_FACTOR = 4.0
GREEN = (0, 225, 75)
BLUE = (25, 135, 255)
RED = (255, 55, 55)
WHITE = (245, 245, 245)
BLACK = (18, 18, 18)
PANEL = (31, 36, 43)
PASS_COLOR = (56, 190, 105)
EXCEPTION_COLOR = (245, 174, 55)


PROPOSAL_REVIEW = {
    "R1-P01": {
        "group": "DISCOVERY", "manager_r1_decision": "ACCEPT_PRIMARY_TIER_A",
        "corrected_tier": "TIER_A", "bounds_review_state": "NOT_REQUIRED",
        "target_visibility": "FULLY_VISIBLE", "occlusion_state": "NONE",
        "notes": "Manager-accepted primary; original bounds retained.",
    },
    "R1-P02": {
        "group": "DISCOVERY", "manager_r1_decision": "ACCEPT_PRIMARY_TIER_B",
        "corrected_tier": "TIER_B", "bounds_review_state": "NOT_REQUIRED",
        "target_visibility": "FULLY_VISIBLE", "occlusion_state": "NONE",
        "notes": "Manager-accepted primary; original bounds retained.",
    },
    "R1-P03": {
        "group": "HOLDOUT", "manager_r1_decision": "ACCEPT_PRIMARY_TIER_B_BOUNDS_TO_RECHECK",
        "corrected_tier": "TIER_B", "bounds_review_state": "BOUNDS_CONFIRMED",
        "target_visibility": "VISIBLE_WITH_EDGE_OVERLAP", "occlusion_state": "PARTIAL",
        "notes": (
            "Frames 33-37 were rescanned source-only. The same light-top adult remains lower-left "
            "of the GT target for all five frames; the GT target remains visible and the event is "
            "inside the nominal search context. Frames 32 and 38 were not added because the "
            "five-frame core is the least ambiguous continuous event."
        ),
    },
    "R1-P04": {
        "group": "DISCOVERY", "manager_r1_decision": "ACCEPT_PRIMARY_TIER_B",
        "corrected_tier": "TIER_B", "bounds_review_state": "NOT_REQUIRED",
        "target_visibility": "FULLY_VISIBLE", "occlusion_state": "NONE",
        "notes": "Manager-accepted primary; original bounds retained.",
    },
    "R1-P05": {
        "group": "HOLDOUT", "manager_r1_decision": "ACCEPT_PRIMARY_TIER_A",
        "corrected_tier": "TIER_A", "bounds_review_state": "NOT_REQUIRED",
        "target_visibility": "FULLY_VISIBLE", "occlusion_state": "NONE",
        "notes": "Manager-accepted primary; original bounds retained.",
    },
    "R1-P07": {
        "group": "DISCOVERY", "manager_r1_decision": "ACCEPT_PRIMARY_TIER_A",
        "corrected_tier": "TIER_A", "bounds_review_state": "NOT_REQUIRED",
        "target_visibility": "DISCERNIBLE_WITH_WING_CLUTTER", "occlusion_state": "PARTIAL",
        "notes": "Manager-accepted primary; original five-frame core retained.",
    },
    "R1-P09": {
        "group": "DISCOVERY", "manager_r1_decision": "ACCEPT_PRIMARY_TIER_A",
        "corrected_tier": "TIER_A", "bounds_review_state": "NOT_REQUIRED",
        "target_visibility": "FULLY_VISIBLE", "occlusion_state": "NONE",
        "notes": "Manager-accepted primary; original bounds retained.",
    },
    "R1-P10": {
        "group": "DISCOVERY", "manager_r1_decision": "ACCEPT_PRIMARY_TIER_A",
        "corrected_tier": "TIER_A", "bounds_review_state": "NOT_REQUIRED",
        "target_visibility": "HELMET_VISIBLE", "occlusion_state": "PARTIAL",
        "notes": "Manager-accepted primary; original bounds retained.",
    },
    "R1-P11": {
        "group": "HOLDOUT", "manager_r1_decision": "ACCEPT_PRIMARY_TIER_B",
        "corrected_tier": "TIER_B", "bounds_review_state": "NOT_REQUIRED",
        "target_visibility": "HEAD_DISCERNIBLE", "occlusion_state": "PARTIAL",
        "notes": "Manager-accepted primary; original bounds retained.",
    },
    "R1-P12": {
        "group": "HOLDOUT", "manager_r1_decision": "ACCEPT_PRIMARY_DOWNGRADE_TIER_B",
        "corrected_tier": "TIER_B", "bounds_review_state": "NOT_REQUIRED",
        "target_visibility": "FACE_VISIBLE_WITH_CLUTTER", "occlusion_state": "PARTIAL",
        "notes": "Manager-required Tier B correction applied; original bounds retained.",
    },
}


CONTROL_SPECS = (
    {
        "control_id": "R2-C01", "linked_proposal_id": "R1-P01", "sequence": "David3",
        "interval_start": 195, "interval_end": 233, "same_sequence": False,
        "broad_superclass": "PERSON", "visual_subtype": "real full-body adult pedestrian",
        "occlusion_state": "NONE", "subtype_match": True,
        "no_similar_distractor_evidence": (
            "EVERY_FRAME_REVIEWED 195-233; only the annotated adult pedestrian is present; "
            "co-occurring parked/moving cars are a different class."
        ),
        "matching_basis": "Same class; full-body adult target; length, area, GT motion and scale dynamics all pass.",
        "notes": "Human5 and Woman were checked as metric leads; David3 gave the cleaner full interval and stronger area match.",
    },
    {
        "control_id": "R2-C02", "linked_proposal_id": "R1-P02", "sequence": "Human8",
        "interval_start": 108, "interval_end": 126, "same_sequence": False,
        "broad_superclass": "PERSON", "visual_subtype": "real full-body upright person",
        "occlusion_state": "NONE", "subtype_match": True,
        "no_similar_distractor_evidence": (
            "EVERY_FRAME_REVIEWED 108-126; only the annotated person is resolvable; rocks, shadows "
            "and architecture are different objects."
        ),
        "matching_basis": "Same class and full-body subtype; equal length; area, GT motion and scale dynamics all pass.",
        "notes": "The scene differs from sprinting, but the target is a clean full-body real person with matched GT dynamics.",
    },
    {
        "control_id": "R2-C03", "linked_proposal_id": "R1-P03", "sequence": "Crowds",
        "interval_start": 161, "interval_end": 165, "same_sequence": True,
        "broad_superclass": "PERSON", "visual_subtype": "real overhead street pedestrian",
        "occlusion_state": "NONE", "subtype_match": True,
        "no_similar_distractor_evidence": (
            "EVERY_FRAME_REVIEWED 161-165; the annotated pedestrian is fully visible and no "
            "comparable/search-relevant pedestrian enters the nominal target context. Other people "
            "remain far across the full frame at non-comparable scale."
        ),
        "matching_basis": "Same sequence, same target/scene identity, equal length and clean nominal target context.",
        "notes": (
            "Preferred by same-sequence search order. Human6 110-114 and Human5 234-238 were "
            "rejected because a second comparably resolved pedestrian remained near the target."
        ),
    },
    {
        "control_id": "R2-C04", "linked_proposal_id": "R1-P04", "sequence": "CarScale",
        "interval_start": 143, "interval_end": 163, "same_sequence": False,
        "broad_superclass": "VEHICLE", "visual_subtype": "real passenger car in road view",
        "occlusion_state": "PARTIAL", "subtype_match": True, "declared_exception": True,
        "no_similar_distractor_evidence": (
            "EVERY_FRAME_REVIEWED 143-163; the annotated passenger car is the only comparable "
            "vehicle throughout. Foreground branches partly overlap it but never fully occlude it."
        ),
        "matching_basis": "Same VEHICLE/passenger-car subtype; equal length; area and scale dynamics pass; normalized p90 motion fails.",
        "notes": (
            "EXCEPTION_PENDING_MANAGER: normalized p90 motion factor exceeds 2. BlurCar3 216-236 "
            "passes every quantitative target and exact sedan subtype but a large dark SUV plus "
            "another car persists throughout, so its no-distractor gate fails. BlurCar1 773-793 "
            "likewise contains a large adjacent dark truck in every frame."
        ),
    },
    {
        "control_id": "R2-C05", "linked_proposal_id": "R1-P05", "sequence": "Suv",
        "interval_start": 726, "interval_end": 750, "same_sequence": False,
        "broad_superclass": "VEHICLE", "visual_subtype": "real road SUV in rear/side view",
        "occlusion_state": "NONE", "subtype_match": True,
        "no_similar_distractor_evidence": (
            "EVERY_FRAME_REVIEWED 726-750; the annotated road SUV/pickup is the only vehicle "
            "throughout the complete interval and remains free of full occlusion."
        ),
        "matching_basis": "Same car class and SUV subtype; equal length; area, GT motion and scale dynamics all pass.",
        "notes": (
            "Same-sequence BlurCar4 210-230 was rejected because adjacent cars persist. Suv "
            "651-675 is a quantitative alternate but has partial pole/tree occlusion."
        ),
    },
    {
        "control_id": "R2-C07", "linked_proposal_id": "R1-P07", "sequence": "Panda",
        "interval_start": 426, "interval_end": 430, "same_sequence": False,
        "broad_superclass": "ANIMAL", "visual_subtype": "real live terrestrial panda",
        "occlusion_state": "NONE", "subtype_match": False, "declared_exception": True,
        "no_similar_distractor_evidence": (
            "EVERY_FRAME_REVIEWED 426-430; the annotated live panda is the only panda throughout. "
            "A much larger elephant is present but is a visibly dissimilar animal subtype."
        ),
        "matching_basis": "Real animate ANIMAL control; equal length; area, GT motion and scale dynamics all pass.",
        "notes": (
            "EXCEPTION_PENDING_MANAGER: bird-to-panda visual subtype failed. Every Bird1 frame was "
            "reviewed: visible-target five-frame windows retain other birds, while low-distractor "
            "140-144 leaves the target effectively unresolved. Bird2 22-26 fails area and contains "
            "animated bird distractors; plush Dog1 remains invalid."
        ),
    },
    {
        "control_id": "R2-C09", "linked_proposal_id": "R1-P09", "sequence": "Liquor",
        "interval_start": 20, "interval_end": 40, "same_sequence": True,
        "broad_superclass": "OBJECT_OTHER", "visual_subtype": "same upright miniature liquor bottle",
        "occlusion_state": "NONE", "subtype_match": True,
        "no_similar_distractor_evidence": (
            "EVERY_FRAME_REVIEWED 20-40; only the annotated bottle is present throughout the full "
            "interval; no second bottle enters the frame."
        ),
        "matching_basis": "Source-only revalidation of R1-C09; same target, scene, class and scale before distractors appear.",
        "notes": "R1-C09 retained as the preferred source interval under an R2 control ID.",
    },
    {
        "control_id": "R2-C10", "linked_proposal_id": "R1-P10", "sequence": "Biker",
        "interval_start": 41, "interval_end": 65, "same_sequence": False,
        "broad_superclass": "FACE_HEAD", "visual_subtype": "novelty bird/chicken mask or rider headgear",
        "occlusion_state": "NONE", "subtype_match": False, "declared_exception": True,
        "no_similar_distractor_evidence": (
            "EVERY_FRAME_REVIEWED 41-65; the masked cyclist head is the only head/person target; "
            "no second cyclist, helmet, mask or comparable face occurs."
        ),
        "matching_basis": "Same broad FACE_HEAD superclass; equal length; area, GT motion and scale dynamics all pass.",
        "notes": (
            "EXCEPTION_PENDING_MANAGER: football helmet/equipment subtype failed because Biker "
            "shows novelty mask/headgear, not a football helmet. Football has no clean same-sequence "
            "interval; Ironman contains additional armored heads; Freeman1 24-48 is quantitatively "
            "viable but is a bare-face subtype."
        ),
    },
    {
        "control_id": "R2-C11", "linked_proposal_id": "R1-P11", "sequence": "Surfer",
        "interval_start": 304, "interval_end": 328, "same_sequence": False,
        "broad_superclass": "FACE_HEAD", "visual_subtype": "real bare human head in upper-body view",
        "occlusion_state": "NONE", "subtype_match": False, "declared_exception": True,
        "no_similar_distractor_evidence": (
            "EVERY_FRAME_REVIEWED 304-328; the annotated surfer is the only person/head; sea, board "
            "and spray are different objects and no second face appears."
        ),
        "matching_basis": "Same broad FACE_HEAD class; equal length; area, GT motion and scale dynamics all pass.",
        "notes": (
            "EXCEPTION_PENDING_MANAGER: helmet/equipment subtype failed. Football1 has no clean "
            "same-sequence interval; Ironman 16-40 and 66-90 contain a second armored/helmeted "
            "figure; Biker is assigned to discovery and cannot cross the split; no better clean "
            "source-only helmet control was found."
        ),
    },
    {
        "control_id": "R2-C12", "linked_proposal_id": "R1-P12", "sequence": "Man",
        "interval_start": 106, "interval_end": 116, "same_sequence": False,
        "broad_superclass": "FACE_HEAD", "visual_subtype": "real unobstructed human face/head",
        "occlusion_state": "NONE", "subtype_match": True,
        "no_similar_distractor_evidence": (
            "EVERY_FRAME_REVIEWED 106-116; one real human face/head is visible; shelves, door and "
            "room objects are different classes."
        ),
        "matching_basis": "Real face/head subtype; equal length; area, GT motion and scale dynamics all pass.",
        "notes": (
            "Partial Soccer clutter versus clean Man is disclosed; Man shares IV. The raw David "
            "180-190 lead was rejected because canonical evaluator mapping starts David at frame 300."
        ),
    },
)


SEARCH_LOG = (
    ("R1-P01", "Basketball: similar players persist", "David3; Human5; Woman", "David3 195-233", "Human5/Woman weaker scene or cleanliness leads"),
    ("R1-P02", "Bolt: adjacent runners persist", "Human8; David3; Gym", "Human8 108-126", "Gym area mismatch; David3 reserved for P01"),
    ("R1-P03", "Crowds 161-165 clean in nominal target context", "Crowds; Human3; Skiing; Human6; Human5", "Crowds 161-165", "Human6/Human5 have nearby second pedestrians; Human3 464-468 is a valid alternate"),
    ("R1-P04", "BlurCar2 330-360: comparable SUV persists", "BlurCar1; BlurCar3; CarScale", "CarScale 143-163 (exception)", "CarScale motion fails; BlurCar3/BlurCar1 quantitative leads fail no-distractor"),
    ("R1-P05", "BlurCar4 210-230: adjacent traffic persists", "Suv; CarScale; Car4", "Suv 726-750", "Suv 651-675 passes metrics but has partial pole/tree occlusion"),
    ("R1-P07", "Bird1: visible-target windows retain other birds; 140-144 target unresolved", "Bird1; Bird2; Panda; Dog; Dog1", "Panda 426-430 (exception)", "Bird2 fails area/cleanliness; Dog is bird-to-dog exception; Dog1 is plush and invalid"),
    ("R1-P09", "Liquor 20-40 clean and revalidated", "Liquor; Coke; ClifBar", "Liquor 20-40", "Cross-sequence objects are weaker than exact same-sequence control"),
    ("R1-P10", "Football: helmets/heads persist", "Biker; Ironman; Freeman1", "Biker 41-65 (exception)", "Biker is novelty mask/headgear; Ironman has extra armored heads; Freeman1 is bare face"),
    ("R1-P11", "Football1: no clean interval in 1-74", "Surfer; Ironman; Biker; Jumping", "Surfer 304-328", "Ironman not clean; Biker would cross split; bare-head exception retained"),
    ("R1-P12", "Soccer: comparable faces persist", "Man; David; Freeman1; Jumping", "Man 106-116", "David 180-190 lies before canonical evaluator startFrame=300 and is invalid"),
)


PROPOSAL_FIELDS = [
    "proposal_id", "dataset", "sequence", "group", "broad_superclass", "object_class", "official_attributes",
    "interval_start", "interval_end", "interval_length", "evidence_tier", "distractor_description",
    "similarity_basis", "search_context_status", "midpoint_distractor_bbox_or_na",
    "target_visibility", "occlusion_state", "fast_motion_from_gt", "low_resolution_from_gt",
    "scan_method", "proposed_split", "contact_sheet_path", "manager_review_status", "notes",
    "manager_r1_decision", "corrected_tier", "bounds_review_state", "final_provisional_group",
    "fast_motion_flag", "low_resolution_flag", "median_target_area_ratio", "min_target_area_ratio",
    "max_target_area_ratio", "median_center_displacement_px", "p90_center_displacement_px",
    "p90_motion_normalized", "end_to_start_area_ratio", "max_to_min_area_ratio",
    "median_abs_log_area_step", "p90_center_displacement_normalized_by_target_scale",
    "median_absolute_log_area_step", "target_visibility_category", "occlusion_category",
    "r1_evidence_tier", "r1_contact_sheet_path", "r2_pair_sheet_path",
]

CONTROL_FIELDS = [
    "control_id", "linked_proposal_id", "preferred_or_alternate", "group", "dataset", "sequence",
    "interval_start", "interval_end", "interval_length", "same_sequence", "object_class",
    "broad_superclass", "visual_subtype", "no_similar_distractor_evidence", "matching_basis",
    "median_target_area_ratio", "min_target_area_ratio", "max_target_area_ratio",
    "median_center_displacement_px", "p90_center_displacement_px", "p90_motion_normalized",
    "end_to_start_area_ratio", "max_to_min_area_ratio", "median_abs_log_area_step",
    "occlusion_state", "fast_motion_flag", "low_resolution_flag", "official_attributes",
    "control_sequence_reuse_count", "exception_state", "contact_sheet_path",
    "manager_review_status", "notes",
]

AUDIT_FIELDS = [
    "linked_proposal_id", "linked_control_id", "group", "proposal_sequence", "control_sequence",
    "proposal_length", "control_length", "length_difference", "length_match_pass",
    "proposal_median_area", "control_median_area", "median_area_ratio", "area_match_pass",
    "proposal_p90_motion_normalized", "control_p90_motion_normalized",
    "motion_ratio_or_abs_difference", "motion_match_pass", "proposal_max_to_min_area_ratio",
    "control_max_to_min_area_ratio", "scale_dynamic_ratio", "scale_match_pass", "occlusion_match",
    "fast_motion_match", "low_resolution_match", "broad_superclass_match", "visual_subtype_match",
    "official_attribute_overlap", "control_sequence_reuse_count", "cross_group_leakage",
    "no_distractor_pass", "overall_state", "notes",
]

MANIFEST_FIELDS = [
    "pair_sheet_id", "linked_proposal_id", "linked_control_id", "relative_path", "sha256",
    "byte_size", "width", "height", "proposal_sequence", "control_sequence",
    "proposal_frame_ids", "control_frame_ids", "overlays", "manager_review_status",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def verify_quarantine() -> None:
    rows = read_csv(QUARANTINE_FILE)
    if {row["sequence"] for row in rows} != QUARANTINED:
        raise RuntimeError("Quarantine must contain exactly Deer, Crossing, Couple")
    for row in rows:
        if not (
            row["candidate_pool_excluded"].lower() == "true"
            and row["control_pool_excluded"].lower() == "true"
            and row["coverage_excluded"].lower() == "true"
            and row["frames_opened"].lower() == "false"
        ):
            raise RuntimeError(f"Invalid quarantine row: {row['sequence']}")


def load_mapping() -> dict[str, dict[str, object]]:
    tree = ast.parse(OTB_MAPPING.read_text(encoding="utf-8"), filename=str(OTB_MAPPING))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "sequence_info_list" for target in node.targets
        ):
            return {str(row["name"]): row for row in ast.literal_eval(node.value)}
    raise RuntimeError("sequence_info_list missing from accepted evaluator mapping")


def load_inventory() -> dict[str, dict[str, str]]:
    verify_quarantine()
    rows = read_csv(INVENTORY)
    return {row["sequence"]: row for row in rows}


def parse_gt_line(line: str) -> list[float]:
    return [float(token) for token in re.split(r"[\s,\t]+", line.strip()) if token]


def load_sequence(
    sequence: str,
    mapping: dict[str, dict[str, object]],
) -> tuple[dict[str, object], list[int], list[list[float]]]:
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
    gt_rows = gt_all[omit : omit + len(frame_ids)]
    if len(gt_rows) != len(frame_ids):
        raise RuntimeError(f"GT/evaluator length mismatch for {sequence}")
    return meta, frame_ids, gt_rows


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
    box = gt_bbox(previous_gt)
    if box is None:
        return None
    x, y, w, h = box
    side = SEARCH_FACTOR * math.sqrt(w * h)
    cx, cy = x + w / 2.0, y + h / 2.0
    return cx - side / 2.0, cy - side / 2.0, side, side


def interval_indices(frame_ids: Sequence[int], start: int, end: int) -> list[int]:
    indices = [index for index, frame_id in enumerate(frame_ids) if start <= frame_id <= end]
    if not indices or frame_ids[indices[0]] != start or frame_ids[indices[-1]] != end:
        raise RuntimeError(f"Non-contiguous/out-of-range interval {start}-{end}")
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
    with Image.open(frame_path(meta, frame_ids[indices[0]])) as image:
        image_area = float(image.width * image.height)
    boxes = [gt_bbox(gt_rows[index]) for index in indices]
    if any(box is None for box in boxes):
        raise RuntimeError(f"Invalid GT in {sequence} {start}-{end}")
    valid = [box for box in boxes if box is not None]
    areas = [box[2] * box[3] for box in valid]
    area_ratios = [area / image_area for area in areas]
    centers = [(box[0] + box[2] / 2.0, box[1] + box[3] / 2.0) for box in valid]
    motions = [math.dist(centers[index - 1], centers[index]) for index in range(1, len(centers))]
    normalized_motion = [
        motions[index - 1] / max(1.0, math.sqrt(areas[index - 1]))
        for index in range(1, len(areas))
    ]
    log_steps = [abs(math.log(areas[index] / areas[index - 1])) for index in range(1, len(areas))]
    median_area = statistics.median(area_ratios)
    p90_normalized = percentile(normalized_motion, 0.9)
    return {
        "interval_length": len(indices),
        "median_target_area_ratio": median_area,
        "min_target_area_ratio": min(area_ratios),
        "max_target_area_ratio": max(area_ratios),
        "median_center_displacement_px": statistics.median(motions) if motions else 0.0,
        "p90_center_displacement_px": percentile(motions, 0.9),
        "p90_motion_normalized": p90_normalized,
        "end_to_start_area_ratio": areas[-1] / areas[0],
        "max_to_min_area_ratio": max(areas) / min(areas),
        "median_abs_log_area_step": statistics.median(log_steps) if log_steps else 0.0,
        "fast_motion_flag": p90_normalized > 1.0,
        "low_resolution_flag": median_area < 0.001,
        "meta": meta,
        "frame_ids": frame_ids,
        "gt_rows": gt_rows,
        "indices": indices,
    }


def factor_ratio(left: float, right: float) -> float:
    if left == 0.0 and right == 0.0:
        return 1.0
    if left <= 0.0 or right <= 0.0:
        return math.inf
    return max(left / right, right / left)


def five_indices(indices: Sequence[int]) -> list[int]:
    if len(indices) < 5:
        raise RuntimeError("Pair sheet requires at least five frames")
    return [indices[round(position * (len(indices) - 1))] for position in (0.0, 0.25, 0.5, 0.75, 1.0)]


def draw_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float] | None,
    color: tuple[int, int, int],
    width: int,
) -> None:
    if box is None:
        return
    x, y, w, h = box
    draw.rectangle((round(x), round(y), round(x + w), round(y + h)), outline=color, width=width)


def parse_bbox(value: str) -> tuple[float, float, float, float] | None:
    if not value or value.upper() == "NA":
        return None
    numbers = [float(token) for token in re.split(r"[\s,]+", value.strip()) if token]
    if len(numbers) != 4:
        raise RuntimeError(f"Invalid distractor bbox: {value}")
    return numbers[0], numbers[1], numbers[2], numbers[3]


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf"),
    ]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def render_tile(
    image_path: Path,
    gt: Sequence[float],
    previous_gt: Sequence[float],
    label: str,
    distractor: tuple[float, float, float, float] | None,
    size: tuple[int, int] = (264, 210),
) -> Image.Image:
    with Image.open(image_path) as source:
        image = source.convert("RGB")
    overlay = ImageDraw.Draw(image)
    line_width = max(2, round(max(image.size) / 300))
    draw_box(overlay, nominal_search_bbox(previous_gt), BLUE, line_width)
    draw_box(overlay, gt_bbox(gt), GREEN, line_width)
    draw_box(overlay, distractor, RED, line_width)
    tile_w, tile_h = size
    label_h = 28
    image.thumbnail((tile_w, tile_h - label_h), Image.Resampling.LANCZOS)
    tile = Image.new("RGB", size, BLACK)
    tile.paste(image, ((tile_w - image.width) // 2, label_h + (tile_h - label_h - image.height) // 2))
    ImageDraw.Draw(tile).text((6, 5), label, fill=WHITE, font=load_font(14))
    return tile


def format_value(value: object, digits: int = 6) -> str:
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def proposal_rows(mapping: dict[str, dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    source_rows = {row["proposal_id"]: row for row in read_csv(R1_PROPOSALS)}
    if not set(RETAINED_IDS).issubset(source_rows):
        raise RuntimeError("Accepted R1 source rows are incomplete")
    rows: list[dict[str, object]] = []
    by_id: dict[str, dict[str, object]] = {}
    for proposal_id in RETAINED_IDS:
        source = source_rows[proposal_id]
        review = PROPOSAL_REVIEW[proposal_id]
        start, end = int(source["interval_start"]), int(source["interval_end"])
        stats = interval_stats(source["sequence"], start, end, mapping)
        pair_name = f"R2_PAIR_{proposal_id.replace('R1-', '')}.jpg"
        pair_path = (Path("screening") / "codex" / "artifacts" / "stage4A_S1_R2" / "pair_sheets" / pair_name).as_posix()
        row: dict[str, object] = {
            "proposal_id": proposal_id,
            "dataset": "OTB100",
            "sequence": source["sequence"],
            "group": review["group"],
            "final_provisional_group": review["group"],
            "broad_superclass": source["broad_superclass"],
            "object_class": source["object_class"],
            "official_attributes": source["official_attributes"],
            "interval_start": start,
            "interval_end": end,
            "interval_length": stats["interval_length"],
            "evidence_tier": review["corrected_tier"],
            "r1_evidence_tier": source["evidence_tier"],
            "manager_r1_decision": review["manager_r1_decision"],
            "corrected_tier": review["corrected_tier"],
            "search_context_status": source["search_context_status"],
            "distractor_description": source["distractor_description"],
            "similarity_basis": source["similarity_basis"],
            "midpoint_distractor_bbox_or_na": source["midpoint_distractor_bbox_or_na"],
            "target_visibility": review["target_visibility"],
            "occlusion_state": review["occlusion_state"],
            "fast_motion_from_gt": source["fast_motion_from_gt"],
            "low_resolution_from_gt": source["low_resolution_from_gt"],
            "scan_method": source["scan_method"],
            "proposed_split": source["proposed_split"],
            "fast_motion_flag": bool_text(bool(stats["fast_motion_flag"])),
            "low_resolution_flag": bool_text(bool(stats["low_resolution_flag"])),
            "median_target_area_ratio": format_value(stats["median_target_area_ratio"]),
            "min_target_area_ratio": format_value(stats["min_target_area_ratio"]),
            "max_target_area_ratio": format_value(stats["max_target_area_ratio"]),
            "median_center_displacement_px": format_value(stats["median_center_displacement_px"], 3),
            "p90_center_displacement_px": format_value(stats["p90_center_displacement_px"], 3),
            "p90_motion_normalized": format_value(stats["p90_motion_normalized"]),
            "p90_center_displacement_normalized_by_target_scale": format_value(stats["p90_motion_normalized"]),
            "end_to_start_area_ratio": format_value(stats["end_to_start_area_ratio"], 3),
            "max_to_min_area_ratio": format_value(stats["max_to_min_area_ratio"], 3),
            "median_abs_log_area_step": format_value(stats["median_abs_log_area_step"], 4),
            "median_absolute_log_area_step": format_value(stats["median_abs_log_area_step"], 4),
            "target_visibility_category": review["target_visibility"],
            "occlusion_category": review["occlusion_state"],
            "bounds_review_state": review["bounds_review_state"],
            "contact_sheet_path": pair_path,
            "r1_contact_sheet_path": source["contact_sheet_path"],
            "r2_pair_sheet_path": pair_path,
            "manager_review_status": "PENDING_R2_REVIEW",
            "notes": review["notes"],
            "_stats": stats,
            "_manual_bbox": parse_bbox(source["midpoint_distractor_bbox_or_na"]),
        }
        rows.append(row)
        by_id[proposal_id] = row
    return rows, by_id


def build_pair_audits(
    proposals: dict[str, dict[str, object]],
    control_data: list[dict[str, object]],
) -> list[dict[str, object]]:
    discovery_sequences = {
        str(row["sequence"])
        for row in proposals.values()
        if row["group"] == "DISCOVERY"
    } | {
        str(row["sequence"])
        for row in control_data
        if row["group"] == "DISCOVERY"
    }
    holdout_sequences = {
        str(row["sequence"])
        for row in proposals.values()
        if row["group"] == "HOLDOUT"
    } | {
        str(row["sequence"])
        for row in control_data
        if row["group"] == "HOLDOUT"
    }
    leakage = discovery_sequences & holdout_sequences
    reuse = Counter(str(row["sequence"]) for row in control_data)
    audits: list[dict[str, object]] = []
    for control in control_data:
        proposal = proposals[str(control["linked_proposal_id"])]
        ps = proposal["_stats"]
        cs = control["_stats"]
        same_sequence = bool(control["_same_sequence"])
        length_difference = int(cs["interval_length"]) - int(ps["interval_length"])
        area_ratio = factor_ratio(float(ps["median_target_area_ratio"]), float(cs["median_target_area_ratio"]))
        motion_left = float(ps["p90_motion_normalized"])
        motion_right = float(cs["p90_motion_normalized"])
        if motion_left < 0.03 and motion_right < 0.03:
            motion_value = abs(motion_left - motion_right)
            motion_text = f"abs_difference={motion_value:.6f}"
            motion_pass = motion_value <= 0.03
        else:
            motion_value = factor_ratio(motion_left, motion_right)
            motion_text = f"ratio={motion_value:.6f}"
            motion_pass = motion_value <= 2.0
        scale_ratio = factor_ratio(float(ps["max_to_min_area_ratio"]), float(cs["max_to_min_area_ratio"]))
        length_pass = abs(length_difference) <= 2
        area_pass = area_ratio <= 2.0
        scale_pass = scale_ratio <= 2.0
        if same_sequence:
            length_pass = area_pass = motion_pass = scale_pass = True
        broad_match = proposal["broad_superclass"] == control["broad_superclass"]
        subtype_match = bool(control["_subtype_match"])
        full_occlusion_mismatch = (proposal["occlusion_state"] == "FULL") != (control["occlusion_state"] == "FULL")
        occlusion_match = (
            "FAIL_FULL_OCCLUSION_MISMATCH"
            if full_occlusion_mismatch
            else (
                "MATCH"
                if proposal["occlusion_state"] == control["occlusion_state"]
                else f"{proposal['occlusion_state']}_VS_{control['occlusion_state']}_DISCLOSED"
            )
        )
        fast_match = proposal["fast_motion_flag"] == control["fast_motion_flag"]
        low_match = proposal["low_resolution_flag"] == control["low_resolution_flag"]
        attribute_overlap = sorted(
            set(str(proposal["official_attributes"]).split("|"))
            & set(str(control["official_attributes"]).split("|"))
        )
        cross_leak = str(control["sequence"]) in leakage
        no_distractor = str(control["no_similar_distractor_evidence"]).startswith("EVERY_FRAME_REVIEWED")
        required_pass = all(
            (
                length_pass,
                area_pass,
                motion_pass,
                scale_pass,
                not full_occlusion_mismatch,
                broad_match,
                subtype_match,
                no_distractor,
                not cross_leak,
                reuse[str(control["sequence"])] <= 2,
            )
        )
        if required_pass:
            state = "MATCH_PASS"
        elif all(
            (
                bool(control["_declared_exception"]),
                not full_occlusion_mismatch,
                broad_match,
                no_distractor,
                not cross_leak,
                reuse[str(control["sequence"])] <= 2,
            )
        ):
            state = "EXCEPTION_PENDING_MANAGER"
        else:
            state = "MATCH_FAIL"
        note_parts = []
        if same_sequence:
            note_parts.append("same-sequence quantitative exemptions applied")
        if proposal["occlusion_state"] != control["occlusion_state"]:
            note_parts.append("partial/no-occlusion difference disclosed")
        if state == "EXCEPTION_PENDING_MANAGER":
            if str(control["linked_proposal_id"]) == "R1-P04":
                note_parts.append(f"normalized p90 motion target failed ({motion_text}; required <=2)")
            elif str(control["linked_proposal_id"]) == "R1-P07":
                note_parts.append("bird-to-live-panda subtype exception; same-sequence and bird alternatives failed")
            elif str(control["linked_proposal_id"]) == "R1-P10":
                note_parts.append("football helmet-to-novelty-mask/headgear subtype exception; failed searches recorded")
            else:
                note_parts.append("football helmet-to-bare-head subtype exception; failed searches recorded")
        audit: dict[str, object] = {
            "linked_proposal_id": proposal["proposal_id"],
            "linked_control_id": control["control_id"],
            "group": proposal["group"],
            "proposal_sequence": proposal["sequence"],
            "control_sequence": control["sequence"],
            "proposal_length": ps["interval_length"],
            "control_length": cs["interval_length"],
            "length_difference": length_difference,
            "length_match_pass": bool_text(length_pass),
            "proposal_median_area": format_value(ps["median_target_area_ratio"]),
            "control_median_area": format_value(cs["median_target_area_ratio"]),
            "median_area_ratio": format_value(area_ratio),
            "area_match_pass": bool_text(area_pass),
            "proposal_p90_motion_normalized": format_value(ps["p90_motion_normalized"]),
            "control_p90_motion_normalized": format_value(cs["p90_motion_normalized"]),
            "motion_ratio_or_abs_difference": motion_text,
            "motion_match_pass": bool_text(motion_pass),
            "proposal_max_to_min_area_ratio": format_value(ps["max_to_min_area_ratio"], 3),
            "control_max_to_min_area_ratio": format_value(cs["max_to_min_area_ratio"], 3),
            "scale_dynamic_ratio": format_value(scale_ratio),
            "scale_match_pass": bool_text(scale_pass),
            "occlusion_match": occlusion_match,
            "fast_motion_match": bool_text(fast_match),
            "low_resolution_match": bool_text(low_match),
            "broad_superclass_match": bool_text(broad_match),
            "visual_subtype_match": bool_text(subtype_match),
            "official_attribute_overlap": "|".join(attribute_overlap) if attribute_overlap else "NONE",
            "control_sequence_reuse_count": reuse[str(control["sequence"])],
            "cross_group_leakage": bool_text(cross_leak),
            "no_distractor_pass": bool_text(no_distractor),
            "overall_state": state,
            "notes": "; ".join(note_parts) if note_parts else "All locked pair requirements pass.",
        }
        audits.append(audit)
        control["exception_state"] = state
        control["control_sequence_reuse_count"] = reuse[str(control["sequence"])]
    return audits


def control_rows(
    mapping: dict[str, dict[str, object]],
    inventory: dict[str, dict[str, str]],
    proposals: dict[str, dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    for spec in CONTROL_SPECS:
        if spec["sequence"] in QUARANTINED:
            raise RuntimeError("Quarantined control sequence")
        proposal = proposals[str(spec["linked_proposal_id"])]
        stats = interval_stats(str(spec["sequence"]), int(spec["interval_start"]), int(spec["interval_end"]), mapping)
        pair_path = proposal["r2_pair_sheet_path"]
        item = inventory[str(spec["sequence"])]
        row: dict[str, object] = {
            "control_id": spec["control_id"],
            "linked_proposal_id": spec["linked_proposal_id"],
            "preferred_or_alternate": "PREFERRED",
            "group": proposal["group"],
            "dataset": "OTB100",
            "sequence": spec["sequence"],
            "interval_start": spec["interval_start"],
            "interval_end": spec["interval_end"],
            "interval_length": stats["interval_length"],
            "same_sequence": bool_text(bool(spec["same_sequence"])),
            "object_class": item["object_class"],
            "broad_superclass": spec["broad_superclass"],
            "visual_subtype": spec["visual_subtype"],
            "no_similar_distractor_evidence": spec["no_similar_distractor_evidence"],
            "matching_basis": spec["matching_basis"],
            "median_target_area_ratio": format_value(stats["median_target_area_ratio"]),
            "min_target_area_ratio": format_value(stats["min_target_area_ratio"]),
            "max_target_area_ratio": format_value(stats["max_target_area_ratio"]),
            "median_center_displacement_px": format_value(stats["median_center_displacement_px"], 3),
            "p90_center_displacement_px": format_value(stats["p90_center_displacement_px"], 3),
            "p90_motion_normalized": format_value(stats["p90_motion_normalized"]),
            "end_to_start_area_ratio": format_value(stats["end_to_start_area_ratio"], 3),
            "max_to_min_area_ratio": format_value(stats["max_to_min_area_ratio"], 3),
            "median_abs_log_area_step": format_value(stats["median_abs_log_area_step"], 4),
            "occlusion_state": spec["occlusion_state"],
            "fast_motion_flag": bool_text(bool(stats["fast_motion_flag"])),
            "low_resolution_flag": bool_text(bool(stats["low_resolution_flag"])),
            "official_attributes": item["official_attributes"],
            "control_sequence_reuse_count": 0,
            "exception_state": "PENDING_AUDIT",
            "contact_sheet_path": pair_path,
            "manager_review_status": "PENDING_R2_REVIEW",
            "notes": spec["notes"],
            "_stats": stats,
            "_same_sequence": bool(spec["same_sequence"]),
            "_subtype_match": bool(spec["subtype_match"]),
            "_declared_exception": bool(spec.get("declared_exception", False)),
        }
        rows.append(row)
    audits = build_pair_audits(proposals, rows)
    return rows, audits


def pair_sheet(
    proposal: dict[str, object],
    control: dict[str, object],
    audit: dict[str, object],
    output: Path,
) -> tuple[list[int], list[int], int, int]:
    proposal_stats = proposal["_stats"]
    control_stats = control["_stats"]
    proposal_indices = five_indices(proposal_stats["indices"])
    control_indices = five_indices(control_stats["indices"])
    canvas = Image.new("RGB", (2000, 590), (22, 25, 30))
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(24, bold=True)
    section_font = load_font(18, bold=True)
    body_font = load_font(15)
    small_font = load_font(13)
    draw.text((18, 14), f"Stage 4A-S1-R2 pair review | {proposal['proposal_id']} + {control['control_id']}", fill=WHITE, font=title_font)
    draw.text((18, 54), "PROPOSAL / DISTRACTOR SOURCE", fill=(255, 190, 190), font=section_font)
    draw.text((18, 286), "PREFERRED CONTROL SOURCE", fill=(185, 225, 255), font=section_font)
    for row_y, indices, stats, item, is_proposal in (
        (78, proposal_indices, proposal_stats, proposal, True),
        (310, control_indices, control_stats, control, False),
    ):
        meta = stats["meta"]
        frame_ids = stats["frame_ids"]
        gt_rows = stats["gt_rows"]
        for tile_no, index in enumerate(indices):
            frame_id = frame_ids[index]
            distractor = proposal["_manual_bbox"] if is_proposal and tile_no == 2 else None
            tile = render_tile(
                frame_path(meta, frame_id),
                gt_rows[index],
                gt_rows[max(0, index - 1)],
                f"{item['sequence']} f{frame_id}",
                distractor,
            )
            canvas.paste(tile, (18 + tile_no * 268, row_y))
    panel_x = 1366
    draw.rounded_rectangle((panel_x, 52, 1984, 566), radius=14, fill=PANEL, outline=(80, 90, 105), width=2)
    state = str(audit["overall_state"])
    state_color = PASS_COLOR if state == "MATCH_PASS" else EXCEPTION_COLOR
    draw.rounded_rectangle((panel_x + 18, 70, 1966, 112), radius=8, fill=state_color)
    draw.text((panel_x + 30, 78), state, fill=(10, 20, 15), font=section_font)
    lines = [
        f"Group: {proposal['group']}",
        f"P: {proposal['sequence']}  {proposal['interval_start']}-{proposal['interval_end']}",
        f"C: {control['sequence']}  {control['interval_start']}-{control['interval_end']}",
        "",
        f"Length P/C: {audit['proposal_length']} / {audit['control_length']}   pass={audit['length_match_pass']}",
        f"Median area P/C: {float(audit['proposal_median_area']):.5f} / {float(audit['control_median_area']):.5f}",
        f"Area factor: {float(audit['median_area_ratio']):.3f}   pass={audit['area_match_pass']}",
        f"Norm p90 motion P/C: {float(audit['proposal_p90_motion_normalized']):.3f} / {float(audit['control_p90_motion_normalized']):.3f}",
        f"Motion check: {audit['motion_ratio_or_abs_difference']}   pass={audit['motion_match_pass']}",
        f"Max/min area P/C: {float(audit['proposal_max_to_min_area_ratio']):.3f} / {float(audit['control_max_to_min_area_ratio']):.3f}",
        f"Scale factor: {float(audit['scale_dynamic_ratio']):.3f}   pass={audit['scale_match_pass']}",
        "",
        f"Class: {proposal['broad_superclass']} / {control['broad_superclass']}",
        f"Subtype: {control['visual_subtype']}",
        f"Subtype pass: {audit['visual_subtype_match']}",
        f"Occlusion: {audit['occlusion_match']}",
        f"No distractor: {audit['no_distractor_pass']}",
        f"Reuse: {audit['control_sequence_reuse_count']}  leakage={audit['cross_group_leakage']}",
    ]
    y = 126
    for line in lines:
        font = body_font if len(line) < 68 else small_font
        draw.text((panel_x + 20, y), line, fill=WHITE, font=font)
        y += 23 if line else 12
    draw.text(
        (18, 558),
        "Source JPG + GT target (green) + GT-derived nominal search context (blue) + proposal midpoint distractor (red). No tracker output.",
        fill=(185, 190, 200),
        font=small_font,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "JPEG", quality=88, optimize=True)
    proposal_frame_ids = [proposal_stats["frame_ids"][index] for index in proposal_indices]
    control_frame_ids = [control_stats["frame_ids"][index] for index in control_indices]
    return proposal_frame_ids, control_frame_ids, canvas.width, canvas.height


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    result = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        result.append("| " + " | ".join(str(value).replace("|", "/") for value in row) + " |")
    return "\n".join(result)


def build_report(
    proposals: list[dict[str, object]],
    controls: list[dict[str, object]],
    audits: list[dict[str, object]],
    manifest: list[dict[str, object]],
) -> str:
    discovery = sorted(
        {str(row["sequence"]) for row in proposals if row["group"] == "DISCOVERY"}
        | {str(row["sequence"]) for row in controls if row["group"] == "DISCOVERY"}
    )
    holdout = sorted(
        {str(row["sequence"]) for row in proposals if row["group"] == "HOLDOUT"}
        | {str(row["sequence"]) for row in controls if row["group"] == "HOLDOUT"}
    )
    intersection = sorted(set(discovery) & set(holdout))
    reuse = Counter(str(row["sequence"]) for row in controls)
    states = Counter(str(row["overall_state"]) for row in audits)
    payload = sum(int(row["byte_size"]) for row in manifest)
    proposal_table = markdown_table(
        ["ID", "Sequence", "Frames", "Tier", "Median area", "p90 norm motion", "Max/min area", "Occ"],
        [
            [
                row["proposal_id"], row["sequence"], f"{row['interval_start']}-{row['interval_end']}",
                row["corrected_tier"], row["median_target_area_ratio"], row["p90_motion_normalized"],
                row["max_to_min_area_ratio"], row["occlusion_state"],
            ]
            for row in proposals
        ],
    )
    preferred_table = markdown_table(
        ["Proposal", "Control", "Sequence", "Frames", "Same seq", "State"],
        [
            [
                row["linked_proposal_id"], row["control_id"], row["sequence"],
                f"{row['interval_start']}-{row['interval_end']}", row["same_sequence"], row["exception_state"],
            ]
            for row in controls
        ],
    )
    search_table = markdown_table(
        ["Proposal", "Same-sequence result", "Other source-only sequences checked", "Preferred", "Rejected/alternate result"],
        [list(row) for row in SEARCH_LOG],
    )
    audit_table = markdown_table(
        ["Proposal", "Control", "Len", "Area", "Motion", "Scale", "Subtype", "No distractor", "State"],
        [
            [
                row["linked_proposal_id"], row["linked_control_id"], row["length_match_pass"],
                row["area_match_pass"], row["motion_match_pass"], row["scale_match_pass"],
                row["visual_subtype_match"], row["no_distractor_pass"], row["overall_state"],
            ]
            for row in audits
        ],
    )
    sheet_table = markdown_table(
        ["Pair", "Proposal", "Control", "Bytes", "Path"],
        [
            [row["pair_sheet_id"], row["linked_proposal_id"], row["linked_control_id"], row["byte_size"], row["relative_path"]]
            for row in manifest
        ],
    )
    return f"""# Stage 4A-S1-R2 — Source-only proposal correction and control rematch report

**Date:** 2026-08-26  
**Status:** `S1_R2_COMPLETE_READY_FOR_MANAGER_FINAL_SLICE_REVIEW`  
**Decision scope:** revised proposals, preferred controls, metrics and pair sheets remain provisional with `manager_review_status=PENDING_R2_REVIEW`.

## 1. Outcome-independence declaration

This R2 lane used only the accepted v2 clean room, canonical OTB source JPGs and GT, the Manager R1 review/protocol, and the accepted source-only R1 proposal evidence. SpikeTrack was not run; no model or checkpoint was instantiated; no prediction, AUC, IoU, success/failure outcome, score/confidence map, divergence evidence, MRM log, ablation or tracker-derived ranking was accessed. Outcome evidence accessed: **NONE**.

## 2. Canonical source and quarantine

- canonical OTB root: `{SOURCE_ROOT}`
- accepted clean room: `{CLEANROOM}`
- quarantine: `Deer`, `Crossing`, `Couple`
- quarantine enforcement: all three remained excluded from proposal scanning, control scanning, matching, group accounting and coverage; their source frames were not opened.

## 3. R1 accepted/rejected proposal traceability

- retained exactly 10 Manager-accepted primaries: `{', '.join(RETAINED_IDS)}`
- rejected primaries: `R1-P06 Car24`, `R1-P08 Board`
- P06/P08 do not occur in the revised primary/control/audit tables and contribute no coverage or control generation.

## 4. P03 bounds decision

`R1-P03 Crowds 33-37`: **BOUNDS_CONFIRMED**. Source-only frame-by-frame review shows the same light-top adult immediately lower-left of the target in all five frames. The GT target stays visible; the distractor event stays inside the nominal search context. Frames 32 and 38 were not added because the accepted five-frame core is the least ambiguous continuous event.

## 5. P12 tier correction

`R1-P12 Soccer`: corrected from R1 Tier A to **TIER_B**. Tier A was not restored. Across frames 170-180, source-only full-frame review shows non-target real faces near/beyond the blue prior-GT crop boundary; no second face was clearly interior in the factor-4 crop render. This observation preserves the locked `NEAR_SEARCH_BOUNDARY` status and does not reclassify or reject P12.

## 6. Proposal-side GT metric summary

Exact formulas:

- rectangular GT area is `w*h`; polygon GT is converted to its enclosing axis-aligned box before the same calculation;
- target-area ratio is `(w*h)/(image_width*image_height)`;
- center is `(x+w/2, y+h/2)` and per-step pixel displacement is Euclidean center distance;
- normalized motion at step `i` is `distance(center[i-1], center[i]) / max(1, sqrt(area[i-1]))`;
- p90 uses linear interpolation at position `0.9*(n-1)` in the sorted per-step values;
- end/start area ratio is `area[last]/area[first]`;
- max/min area ratio is `max(area)/min(area)`;
- median absolute log-area step is `median(abs(log(area[i]/area[i-1])))`;
- `fast_motion_flag=true` iff normalized p90 motion is greater than `1.0`;
- `low_resolution_flag=true` iff median target-area ratio is below `0.001`.

{proposal_table}

All values above are GT-derived; no tracker output enters any formula.

## 7. Control search coverage

Search order was same sequence, non-quarantined same class, compatible subtype in the same broad superclass, then declared weaker alternatives. Every preferred interval was visually reviewed frame by frame.

{search_table}

## 8. Preferred control per primary

{preferred_table}

## 9. Rejected/alternate controls per primary

The final column of Section 7 records the strongest rejected or alternate search result for every primary. Important rejections were: unresolved/contaminated same-sequence bird windows, `Bird2 22-26` for area plus animated distractors, and plush `Dog1`; traffic-filled same-sequence windows for BlurCar2/BlurCar4; `Ironman` helmet leads containing a second armored figure; `Human6 110-114` and `Human5 234-238` containing nearby second pedestrians; and raw `David 180-190`, which lies before canonical evaluator `startFrame=300`.

## 10. Pair matching audit results

{audit_table}

- `MATCH_PASS`: **{states.get('MATCH_PASS', 0)}**
- `EXCEPTION_PENDING_MANAGER`: **{states.get('EXCEPTION_PENDING_MANAGER', 0)}**
- `MATCH_FAIL`: **{states.get('MATCH_FAIL', 0)}**

Same-sequence controls retain recorded metrics but are exempt from cross-sequence numeric gates. Fast-motion and low-resolution flag agreement is reported in the audit CSV but is not an additional locked gate.

## 11. Discovery/hold-out full-sequence disjoint validation

- DISCOVERY full sequence set ({len(discovery)}): `{', '.join(discovery)}`
- HOLDOUT full sequence set ({len(holdout)}): `{', '.join(holdout)}`
- intersection: `{'NONE' if not intersection else ', '.join(intersection)}`
- status: `{'SEQUENCE_DISJOINT_PASS' if not intersection else 'SEQUENCE_DISJOINT_FAIL'}`

These sets include both primary and control sequences.

## 12. Control reuse validation

- control-sequence reuse counts: `{', '.join(f'{name}={count}' for name, count in sorted(reuse.items()))}`
- maximum reuse: **{max(reuse.values())}**
- permitted maximum: 2
- status: `{'CONTROL_REUSE_PASS' if max(reuse.values()) <= 2 else 'CONTROL_REUSE_FAIL'}`

## 13. Exceptions and failed targets

- `R1-P04 + R2-C04`: `EXCEPTION_PENDING_MANAGER`. `CarScale 143-163` is clean for the complete interval and passes length, median area, scale dynamics, broad superclass/subtype, split and reuse checks; partial foreground branches are disclosed and never fully occlude the target. Normalized p90 motion fails at factor `9.870092` (required `<=2`). `BlurCar3 216-236` passes all quantitative targets and exact sedan subtype but contains a large adjacent SUV plus another car throughout; `BlurCar1 773-793` likewise contains a large adjacent truck in every frame. The clean control was preferred over quantitatively matched but distractor-contaminated alternatives.
- `R1-P07 + R2-C07`: `EXCEPTION_PENDING_MANAGER`. The live panda control satisfies the explicit real-animate-animal rule and all quantitative, split, reuse and no-similar-panda checks, but bird-to-panda is not a compatible visual subtype, so `visual_subtype_match=false`. Exhaustive Bird1 review found other birds in visible-target five-frame windows; frames 140-144 were rejected because the target is effectively unresolved. Bird2 fails area/cleanliness, Dog is another cross-subtype fallback, and plush Dog1 is prohibited.
- `R1-P10 + R2-C10`: `EXCEPTION_PENDING_MANAGER`. All quantitative, broad-superclass, split, reuse and no-distractor checks pass. The closest clean discovery control is a novelty bird/chicken mask or rider headgear, not a football helmet, so `visual_subtype_match=false`. Football has no clean same-sequence interval; `Ironman` contains additional armored/helmeted heads; `Freeman1 24-48` is quantitatively viable but is an isolated bare face.
- `R1-P11 + R2-C11`: `EXCEPTION_PENDING_MANAGER`. Length, area, normalized p90 motion, scale dynamics, broad superclass and no-distractor checks pass, but the control is a bare real head rather than a helmeted/equipped head. Same-sequence Football1 is not clean; two quantitatively viable Ironman intervals contain a second armored/helmeted figure; Biker is the discovery control for P10 and cannot cross the split. This is the best clean source-only hold-out control found.
- partial-versus-no-occlusion differences are explicitly disclosed in the pair audit; no pair has a full-occlusion mismatch.

## 14. Pair-sheet package

{sheet_table}

- pair-review sheets: **{len(manifest)}**
- total bytes: **{payload}** ({payload / (1024 * 1024):.2f} MiB)
- payload cap: `<25 MiB` — `{'PASS' if payload < 25 * 1024 * 1024 else 'FAIL'}`
- allowed overlays only: GT target green, nominal search region blue, proposal midpoint manual distractor red, IDs and GT metrics.

## 15. Remaining blockers

Manager final slice review remains required for the P04 motion exception, the P07 animal-subtype exception, and the P10/P11 FACE_HEAD subtype exceptions. R2 does not freeze a final slice and does not authorize downstream diagnostic work.

## 16. R2 conclusion

`S1_R2_COMPLETE_READY_FOR_MANAGER_FINAL_SLICE_REVIEW`

FROZEN DIAGNOSTIC SLICE: **NOT CREATED**  
STAGE 4B: **LOCKED**  
DIAG PASS/FAIL: **NOT ASSIGNED**  
S1-S7: **NOT STARTED**  
PRIMARY SHORTLIST: **NONE**  
MAIN BASELINE: **NONE**  
PROPOSED ARCHITECTURE: **NONE**
"""


def finalize() -> None:
    verify_quarantine()
    mapping = load_mapping()
    inventory = load_inventory()
    proposals, proposal_by_id = proposal_rows(mapping)
    controls, audits = control_rows(mapping, inventory, proposal_by_id)
    audit_by_proposal = {str(row["linked_proposal_id"]): row for row in audits}
    control_by_proposal = {str(row["linked_proposal_id"]): row for row in controls}
    manifest: list[dict[str, object]] = []
    for proposal in proposals:
        proposal_id = str(proposal["proposal_id"])
        control = control_by_proposal[proposal_id]
        audit = audit_by_proposal[proposal_id]
        output = REPO_ROOT / str(proposal["r2_pair_sheet_path"])
        proposal_frames, control_frames, width, height = pair_sheet(proposal, control, audit, output)
        manifest.append(
            {
                "pair_sheet_id": f"PAIR-{proposal_id}",
                "linked_proposal_id": proposal_id,
                "linked_control_id": control["control_id"],
                "relative_path": proposal["r2_pair_sheet_path"],
                "sha256": sha256_file(output),
                "byte_size": output.stat().st_size,
                "width": width,
                "height": height,
                "proposal_sequence": proposal["sequence"],
                "control_sequence": control["sequence"],
                "proposal_frame_ids": "|".join(str(value) for value in proposal_frames),
                "control_frame_ids": "|".join(str(value) for value in control_frames),
                "overlays": "GT_TARGET_GREEN|NOMINAL_SEARCH_BLUE|PROPOSAL_MIDPOINT_DISTRACTOR_RED|IDS|PAIR_METRICS",
                "manager_review_status": "PENDING_R2_REVIEW",
            }
        )
    write_csv(PROPOSAL_CSV, PROPOSAL_FIELDS, proposals)
    write_csv(CONTROL_CSV, CONTROL_FIELDS, controls)
    write_csv(AUDIT_CSV, AUDIT_FIELDS, audits)
    write_csv(MANIFEST_CSV, MANIFEST_FIELDS, manifest)
    REPORT_MD.write_text(build_report(proposals, controls, audits, manifest), encoding="utf-8")
    states = Counter(str(row["overall_state"]) for row in audits)
    payload = sum(int(row["byte_size"]) for row in manifest)
    print(f"proposals={len(proposals)} preferred_controls={len(controls)} pair_audits={len(audits)}")
    print(f"match_pass={states.get('MATCH_PASS', 0)} exceptions={states.get('EXCEPTION_PENDING_MANAGER', 0)} match_fail={states.get('MATCH_FAIL', 0)}")
    print(f"pair_sheets={len(manifest)} bytes={payload}")
    print("outcome_evidence=NONE stage4b=LOCKED")


def validate() -> None:
    verify_quarantine()
    required = (PROPOSAL_CSV, CONTROL_CSV, AUDIT_CSV, MANIFEST_CSV, REPORT_MD, COMMAND_LOG)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"Missing required R2 files: {missing}")
    proposals = read_csv(PROPOSAL_CSV)
    controls = read_csv(CONTROL_CSV)
    audits = read_csv(AUDIT_CSV)
    manifest = read_csv(MANIFEST_CSV)
    r1_source_rows = read_csv(R1_PROPOSALS)
    if not r1_source_rows or not set(r1_source_rows[0]).issubset(set(proposals[0])):
        raise RuntimeError("Revised proposal table does not preserve every R1 proposal field")
    if len(proposals) != 10 or tuple(row["proposal_id"] for row in proposals) != RETAINED_IDS:
        raise RuntimeError("Revised proposal set is not exactly the locked 10 IDs")
    if any(row["proposal_id"] in REJECTED_IDS for row in proposals):
        raise RuntimeError("P06/P08 leaked into revised proposals")
    p12 = next(row for row in proposals if row["proposal_id"] == "R1-P12")
    p03 = next(row for row in proposals if row["proposal_id"] == "R1-P03")
    if p12["corrected_tier"] != "TIER_B" or p12["evidence_tier"] != "TIER_B":
        raise RuntimeError("P12 is not Tier B")
    if p12["search_context_status"] != "NEAR_SEARCH_BOUNDARY":
        raise RuntimeError("P12 locked search-context status was not preserved")
    if p03["bounds_review_state"] not in {"BOUNDS_CONFIRMED", "BOUNDS_ADJUSTED"}:
        raise RuntimeError("P03 bounds unresolved")
    metric_fields = (
        "median_target_area_ratio", "min_target_area_ratio", "max_target_area_ratio",
        "median_center_displacement_px", "p90_center_displacement_px", "p90_motion_normalized",
        "end_to_start_area_ratio", "max_to_min_area_ratio", "median_abs_log_area_step",
    )
    if any(not row[field] for row in proposals + controls for field in metric_fields):
        raise RuntimeError("A GT metric is missing")
    preferred = [row for row in controls if row["preferred_or_alternate"] == "PREFERRED"]
    if len(preferred) != 10 or Counter(row["linked_proposal_id"] for row in preferred) != Counter(RETAINED_IDS):
        raise RuntimeError("Each primary must have exactly one preferred control")
    if any(row["sequence"] in QUARANTINED for row in proposals + controls):
        raise RuntimeError("Quarantined sequence leaked into R2 outputs")
    bird = next(row for row in controls if row["linked_proposal_id"] == "R1-P07")
    if (
        bird["broad_superclass"] != "ANIMAL"
        or not bird["visual_subtype"].startswith("real live")
        or bird["sequence"] in {"Dog1", "BlurOwl"}
    ):
        raise RuntimeError("Bird1 does not use a real animate-animal control")
    if any(not row["no_similar_distractor_evidence"].startswith("EVERY_FRAME_REVIEWED") for row in controls):
        raise RuntimeError("A preferred control lacks complete visual-review evidence")
    discovery = {
        row["sequence"]
        for row in proposals
        if row["final_provisional_group"] == "DISCOVERY"
    } | {
        row["sequence"] for row in controls if row["group"] == "DISCOVERY"
    }
    holdout = {
        row["sequence"]
        for row in proposals
        if row["final_provisional_group"] == "HOLDOUT"
    } | {
        row["sequence"] for row in controls if row["group"] == "HOLDOUT"
    }
    if discovery & holdout:
        raise RuntimeError(f"Cross-group sequence leakage: {sorted(discovery & holdout)}")
    reuse = Counter(row["sequence"] for row in controls)
    if max(reuse.values()) > 2:
        raise RuntimeError("Control sequence reused more than twice")
    if len(audits) != 10 or {row["linked_proposal_id"] for row in audits} != set(RETAINED_IDS):
        raise RuntimeError("Pair audit coverage failed")
    if any(row["cross_group_leakage"] != "false" for row in audits):
        raise RuntimeError("Audit reports cross-group leakage")
    allowed_states = {"MATCH_PASS", "EXCEPTION_PENDING_MANAGER", "MATCH_FAIL"}
    if any(row["overall_state"] not in allowed_states for row in audits):
        raise RuntimeError("Invalid pair state")
    if any(row["overall_state"] == "MATCH_FAIL" for row in audits):
        raise RuntimeError("Preferred control has MATCH_FAIL")
    exception_ids = {
        row["linked_proposal_id"]
        for row in audits
        if row["overall_state"] == "EXCEPTION_PENDING_MANAGER"
    }
    if exception_ids != {"R1-P04", "R1-P07", "R1-P10", "R1-P11"}:
        raise RuntimeError(f"Unexpected exception set: {sorted(exception_ids)}")
    if len(manifest) != 10:
        raise RuntimeError("Pair-sheet count is not 10")
    payload = 0
    for row in manifest:
        path = REPO_ROOT / row["relative_path"]
        if not path.is_file() or sha256_file(path) != row["sha256"]:
            raise RuntimeError(f"Pair-sheet hash/path failure: {row['relative_path']}")
        if path.stat().st_size != int(row["byte_size"]):
            raise RuntimeError("Pair-sheet size mismatch")
        payload += path.stat().st_size
    if payload >= 25 * 1024 * 1024:
        raise RuntimeError("Pair-sheet payload is not below 25 MiB")
    report = REPORT_MD.read_text(encoding="utf-8")
    locked_tokens = (
        "S1_R2_COMPLETE_READY_FOR_MANAGER_FINAL_SLICE_REVIEW",
        "FROZEN DIAGNOSTIC SLICE: **NOT CREATED**",
        "STAGE 4B: **LOCKED**",
        "DIAG PASS/FAIL: **NOT ASSIGNED**",
        "S1-S7: **NOT STARTED**",
        "PRIMARY SHORTLIST: **NONE**",
        "MAIN BASELINE: **NONE**",
        "PROPOSED ARCHITECTURE: **NONE**",
    )
    if not all(token in report for token in locked_tokens):
        raise RuntimeError("Locked downstream state is incomplete")
    states = Counter(row["overall_state"] for row in audits)
    print("proposals=10 p06_absent=PASS p08_absent=PASS p12_tier_b=PASS p03_bounds=PASS")
    print(f"preferred_controls=10 match_pass={states.get('MATCH_PASS', 0)} exceptions={states.get('EXCEPTION_PENDING_MANAGER', 0)} match_fail={states.get('MATCH_FAIL', 0)}")
    print(f"discovery={','.join(sorted(discovery))}")
    print(f"holdout={','.join(sorted(holdout))}")
    print(f"cross_group_leakage=NONE max_control_reuse={max(reuse.values())}")
    print(f"pair_sheets=10 bytes={payload} payload_cap=PASS")
    print("quarantine=PASS outcome_evidence=NONE frozen_slice=NOT_CREATED stage4b=LOCKED validation=PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("finalize", "validate"))
    args = parser.parse_args()
    if args.command == "finalize":
        finalize()
    else:
        validate()


if __name__ == "__main__":
    main()
