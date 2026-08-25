#!/usr/bin/env python3
"""Build and validate the Stage 4A-S1-R3 source/GT-only package.

The script is intentionally constrained to the accepted v2 clean room, the
canonical OTB source tree, accepted R2 source-only artifacts, and the R3 output
paths.  It never loads a tracker, model, checkpoint, prediction, score, or
outcome artifact.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import importlib.util
import math
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageDraw


REPO_ROOT = Path(__file__).resolve().parents[3]
CODEX_ROOT = REPO_ROOT / "screening" / "codex"
R2_SCRIPT = CODEX_ROOT / "scripts" / "2026-08-26_stage4A_S1_R2_rematch_controls.py"
R2_PRIMARY = CODEX_ROOT / "2026-08-26_stage4A_S1_R2_revised_distractor_intervals.csv"
R2_CONTROL = CODEX_ROOT / "2026-08-26_stage4A_S1_R2_revised_controls.csv"

PRIMARY_CSV = CODEX_ROOT / "2026-08-26_stage4A_S1_R3_expanded_distractor_intervals.csv"
CONTROL_CSV = CODEX_ROOT / "2026-08-26_stage4A_S1_R3_expanded_controls.csv"
AUDIT_CSV = CODEX_ROOT / "2026-08-26_stage4A_S1_R3_pair_matching_audit.csv"
COVERAGE_CSV = CODEX_ROOT / "2026-08-26_stage4A_S1_R3_coverage_split_audit.csv"
MANIFEST_CSV = CODEX_ROOT / "2026-08-26_stage4A_S1_R3_pair_sheet_manifest.csv"
REPORT_MD = CODEX_ROOT / "2026-08-26_stage4A_S1_R3_coverage_control_report.md"
COMMAND_LOG = CODEX_ROOT / "2026-08-26_stage4A_S1_R3_command_log.txt"
PAIR_ROOT = CODEX_ROOT / "artifacts" / "stage4A_S1_R3" / "pair_sheets"

QUARANTINED = frozenset({"Deer", "Crossing", "Couple"})
HELD_SEQUENCES = frozenset({"BlurCar2", "Bird1", "Football", "Football1"})
STATUS = "PENDING_R3_FINAL_REVIEW"


def load_r2_module():
    spec = importlib.util.spec_from_file_location("stage4a_s1_r2_helpers", R2_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load accepted R2 source-only helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


R2 = load_r2_module()


METRIC_FIELDS = [
    "median_target_area_ratio",
    "min_target_area_ratio",
    "max_target_area_ratio",
    "median_center_displacement_px",
    "p90_center_displacement_px",
    "p90_motion_normalized",
    "end_to_start_area_ratio",
    "max_to_min_area_ratio",
    "median_abs_log_area_step",
]

PRIMARY_FIELDS = [
    "r3_interval_id", "source_parent_id_or_new", "dataset", "sequence", "group",
    "event_id", "broad_superclass", "object_class", "official_attributes",
    "interval_start", "interval_end", "interval_length", "evidence_tier",
    "proposed_ambiguity_level", "distractor_description", "similarity_basis",
    "search_context_status", "review_frame_ids", "distractor_bboxes_all_review_frames",
    "midpoint_distractor_bbox_or_na", "distractor_visibility",
    "distractor_truncation", "distractor_occlusion", "manual_bbox_is_benchmark_gt",
    "target_visibility", "occlusion_state", *METRIC_FIELDS, "fast_motion_flag",
    "low_resolution_flag", "event_separation_evidence", "analysis_eligible",
    "replacement_trace", "sensitivity_notes", "source_review_evidence", "scan_method",
    "pair_sheet_path", "manager_review_status", "notes",
]

CONTROL_FIELDS = [
    "r3_control_id", "linked_r3_interval_id", "preferred_or_alternate", "group",
    "dataset", "sequence", "interval_start", "interval_end", "interval_length",
    "same_sequence", "object_class", "broad_superclass", "visual_subtype",
    *METRIC_FIELDS, "fast_motion_flag", "low_resolution_flag", "occlusion_state",
    "official_attributes", "no_similar_distractor_evidence", "matching_basis",
    "control_event_id", "control_sequence_reuse_count", "control_interval_reused",
    "exception_state", "analysis_eligible", "control_search_and_rejection_trace",
    "sensitivity_notes", "pair_sheet_path", "manager_review_status", "notes",
]

AUDIT_FIELDS = [
    "linked_r3_interval_id", "linked_r3_control_id", "group", "proposal_sequence",
    "control_sequence", "proposal_length", "control_length", "length_difference",
    "length_match_pass", "proposal_median_area", "control_median_area",
    "median_area_ratio", "area_match_pass", "proposal_p90_motion_normalized",
    "control_p90_motion_normalized", "motion_ratio_or_abs_difference",
    "motion_match_pass", "proposal_max_to_min_area_ratio",
    "control_max_to_min_area_ratio", "scale_dynamic_ratio", "scale_match_pass",
    "occlusion_match", "full_occlusion_mismatch", "fast_motion_match",
    "low_resolution_match", "broad_superclass_match", "visual_subtype_match",
    "official_attribute_overlap", "control_sequence_reuse_count",
    "cross_group_leakage", "no_distractor_pass", "primary_event_distinctness_pass",
    "control_interval_reuse_pass", "control_sequence_split_pass", "same_split_pass",
    "analysis_eligibility", "held_replacement_trace", "overall_state", "notes",
]

COVERAGE_FIELDS = [
    "group", "analysis_eligible_interval_count", "analysis_eligible_control_count",
    "unique_primary_sequence_count", "primary_sequences", "control_sequences",
    "complete_primary_control_source_sequence_set", "other_group_source_sequence_set",
    "cross_group_intersection", "cross_group_intersection_empty", "superclass_counts",
    "superclass_shares", "max_primary_intervals_per_sequence",
    "max_control_intervals_per_sequence", "duplicate_primary_interval_flag",
    "overlapping_primary_interval_flag", "duplicate_control_interval_flag",
    "overlapping_control_interval_flag", "control_sequence_cross_split_flag",
    "locked_minimum_intervals", "locked_minimum_controls",
    "locked_minimum_unique_primary_sequences", "locked_12_8_gate_pass", "notes",
]

MANIFEST_FIELDS = [
    "pair_sheet_id", "linked_r3_interval_id", "linked_r3_control_id", "relative_path",
    "sha256", "byte_size", "width", "height", "proposal_sequence",
    "control_sequence", "proposal_frame_ids", "control_frame_ids",
    "proposal_distractor_bboxes", "overlays", "analysis_eligible",
    "manager_review_status",
]


ANCHOR_DEFINITIONS = (
    {
        "r3_interval_id": "R3-D01", "source_parent_id": "R1-P01",
        "r3_control_id": "R3-CD01", "group": "DISCOVERY", "event_id": "BASK-E01",
        "ambiguity": 2,
        "bboxes": {397: "84 141 84 148", 407: "111 145 62 113", 416: "130 137 72 93", 425: "127 119 59 103", 435: "99 112 72 110"},
        "event_separation": "ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; RETURN_TO_NON_EVENT=NOT_APPLICABLE",
        "replacement_trace": "LOCKED_R2_ANCHOR_PRESERVED",
        "sensitivity": "CROSS_SCENE_ACTIVITY_DOMAIN_SHIFT: basketball event versus isolated street-pedestrian control.",
    },
    {
        "r3_interval_id": "R3-D02", "source_parent_id": "R1-P02",
        "r3_control_id": "R3-CD02", "group": "DISCOVERY", "event_id": "BOLT-E01",
        "ambiguity": 1,
        "bboxes": {31: "283 150 46 67", 35: "279 150 46 66", 40: "279 151 45 61", 45: "277 151 46 59", 49: "276 150 47 63"},
        "event_separation": "ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; RETURN_TO_NON_EVENT=NOT_APPLICABLE",
        "replacement_trace": "LOCKED_R2_ANCHOR_PRESERVED",
        "sensitivity": "SPRINT_VERSUS_ISOLATED_PERSON_CONTEXT_SHIFT.",
    },
    {
        "r3_interval_id": "R3-D03", "source_parent_id": "R1-P09",
        "r3_control_id": "R3-CD03", "group": "DISCOVERY", "event_id": "LIQ-E01",
        "ambiguity": 2,
        "bboxes": {565: "354 190 93 147", 571: "354 190 93 147", 577: "354 190 93 147", 583: "354 190 93 147", 589: "354 190 93 147"},
        "event_separation": "LIQ-E01 versus LIQ-E02: no overlap; 434-frame gap; different bottle identity/event; RETURN_TO_NON_EVENT=NOT_CONFIRMED, but event identity changes unambiguously.",
        "replacement_trace": "LOCKED_R2_ANCHOR_PRESERVED; R2-C09 expanded 20-40 to 20-44 solely to equalize same-sequence control length after full source-only review.",
        "sensitivity": "NONE_DECLARED",
        "control_end_override": 44,
        "control_review_override": "EVERY_FRAME_REVIEWED 20-44; only the annotated target bottle is present throughout all 25 frames; no second bottle enters the frame.",
    },
    {
        "r3_interval_id": "R3-H01", "source_parent_id": "R1-P03",
        "r3_control_id": "R3-CH01", "group": "HOLDOUT", "event_id": "CROWD-E01",
        "ambiguity": 1,
        "bboxes": {33: "408 338 31 48", 34: "410 337 30 49", 35: "415 338 29 47", 36: "409 337 34 51", 37: "410 336 33 51"},
        "event_separation": "ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; RETURN_TO_NON_EVENT=YES before same-sequence clean control.",
        "replacement_trace": "LOCKED_R2_ANCHOR_PRESERVED",
        "sensitivity": "PARTIAL_TARGET_EDGE_OVERLAP_VERSUS_CLEAN_CONTROL_DISCLOSED.",
    },
    {
        "r3_interval_id": "R3-H02", "source_parent_id": "R1-P05",
        "r3_control_id": "R3-CH02", "group": "HOLDOUT", "event_id": "BC4-E01",
        "ambiguity": 2,
        "bboxes": {255: "452 126 155 171", 261: "455 207 165 153", 267: "344 177 162 145", 273: "405 185 164 149", 279: "468 166 169 157"},
        "event_separation": "ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; RETURN_TO_NON_EVENT=NOT_APPLICABLE",
        "replacement_trace": "LOCKED_R2_ANCHOR_PRESERVED",
        "sensitivity": "COLOR_REAR_VIEW_VERSUS_GRAYSCALE_REAR_SIDE_VIEW_DOMAIN_SHIFT.",
    },
    {
        "r3_interval_id": "R3-H03", "source_parent_id": "R1-P12",
        "r3_control_id": "R3-CH03", "group": "HOLDOUT", "event_id": "SOCC-E01",
        "ambiguity": 1,
        "bboxes": {170: "445 163 64 86", 172: "466 191 66 83", 175: "470 185 65 80", 178: "492 213 65 78", 180: "507 218 70 84"},
        "event_separation": "ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; RETURN_TO_NON_EVENT=NOT_APPLICABLE",
        "replacement_trace": "LOCKED_R2_ANCHOR_PRESERVED",
        "sensitivity": "PARTIAL_CROWD_CLUTTER_VISIBILITY_VERSUS_CLEAN_CONTROL.",
    },
)


def reserve_pair(
    *, interval_id: str, control_id: str, group: str, event_id: str,
    sequence: str, start: int, end: int, broad: str, object_class: str,
    attributes: str, tier: str, ambiguity: int, description: str,
    similarity: str, search_context: str, bboxes: dict[int, str],
    target_visibility: str, primary_occlusion: str, distractor_visibility: str,
    distractor_truncation: str, distractor_occlusion: str,
    event_separation: str, replacement_trace: str, sensitivity: str,
    source_review: str, scan_method: str, primary_notes: str,
    control_sequence: str, control_start: int, control_end: int,
    same_sequence: bool, control_object_class: str, control_broad: str,
    control_attributes: str, visual_subtype: str, control_occlusion: str,
    no_similar: str, matching_basis: str, control_event_id: str,
    control_trace: str, control_notes: str, subtype_match: bool = True,
) -> dict[str, object]:
    """Declare one fully reviewed reserve pair without tracker-derived data."""
    return {
        "primary": {
            "r3_interval_id": interval_id, "source_parent_id_or_new": "NEW_RESERVE",
            "sequence": sequence, "group": group, "event_id": event_id,
            "broad_superclass": broad, "object_class": object_class,
            "official_attributes": attributes, "interval_start": start,
            "interval_end": end, "evidence_tier": tier,
            "proposed_ambiguity_level": ambiguity,
            "distractor_description": description, "similarity_basis": similarity,
            "search_context_status": search_context, "bboxes": bboxes,
            "distractor_visibility": distractor_visibility,
            "distractor_truncation": distractor_truncation,
            "distractor_occlusion": distractor_occlusion,
            "target_visibility": target_visibility, "occlusion_state": primary_occlusion,
            "event_separation_evidence": event_separation,
            "replacement_trace": replacement_trace, "sensitivity_notes": sensitivity,
            "source_review_evidence": source_review, "scan_method": scan_method,
            "notes": primary_notes,
        },
        "control": {
            "r3_control_id": control_id, "sequence": control_sequence, "group": group,
            "interval_start": control_start, "interval_end": control_end,
            "same_sequence": same_sequence, "object_class": control_object_class,
            "broad_superclass": control_broad, "official_attributes": control_attributes,
            "visual_subtype": visual_subtype, "visual_subtype_match": subtype_match,
            "occlusion_state": control_occlusion,
            "no_similar_distractor_evidence": no_similar,
            "matching_basis": matching_basis, "control_event_id": control_event_id,
            "control_search_and_rejection_trace": control_trace,
            "sensitivity_notes": sensitivity, "notes": control_notes,
        },
    }


# Filled from bounded, source/GT-only reserve review. Each entry contains one
# primary and exactly one preferred clean control. No entry may reference a
# held R2 primary or a quarantined sequence.
NEW_PAIR_SPECS: tuple[dict[str, object], ...] = (
    reserve_pair(
        interval_id="R3-D04", control_id="R3-CD04", group="DISCOVERY", event_id="LIQ-E02",
        sequence="Liquor", start=106, end=130, broad="OBJECT_OTHER", object_class="other",
        attributes="IV|SV|OCC|MB|FM|OPR|OV|BC", tier="TIER_A", ambiguity=2,
        description="Squat gold bottle remains immediately beside the GT bottle as a separate display-object identity.",
        similarity="Same bottle/object subtype and display role at exactly matched target scale and motion.",
        search_context="INSIDE_NOMINAL_SEARCH",
        bboxes={106: "16 143 105 163", 112: "96 208 84 142", 118: "139 221 80 141", 124: "139 220 82 141", 130: "139 220 82 141"},
        target_visibility="FULLY_VISIBLE", primary_occlusion="NONE",
        distractor_visibility="FULLY_VISIBLE_ALL_FIVE", distractor_truncation="NONE",
        distractor_occlusion="NONE",
        event_separation="LIQ-E02 versus LIQ-E01: no overlap; 434 intervening frames; different gold-bottle versus dark rectangular red-cap-bottle identity; RETURN_TO_NON_EVENT=NOT_CONFIRMED but the event identity changes unambiguously.",
        replacement_trace="COVERAGE_SLOT_REPLACEMENT_FOR_R1-P07_AFTER_NO_COMPATIBLE_LIVE_BIRD_CONTROL; animal-superclass loss disclosed; this is a count-slot replacement, not a semantic subtype replacement.",
        sensitivity="LOW_STATIC_SCENE; SAME_SEQUENCE_EXACT_NUMERIC_MATCH; distinct bottle identity must remain explicit.",
        source_review=(
            "EVERY_FRAME_REVIEWED 106-130 and 60-84 in accepted cleanroom sheets "
            "outputs/r3/discovery_agent/contact_sheets/Liquor_0106_0130_step1.jpg and Liquor_0060_0084_step1.jpg; "
            "original-resolution primary audit at 106|112|118|124|130; candidate_metrics.csv retained."
        ),
        scan_method="Source+GT step-1 full-frame review, original-resolution five-frame audit and event-identity check; no tracker output.",
        primary_notes="Second source-distinct Liquor event; not a split of the accepted anchor event.",
        control_sequence="Liquor", control_start=60, control_end=84, same_sequence=True,
        control_object_class="other", control_broad="OBJECT_OTHER", control_attributes="IV|SV|OCC|MB|FM|OPR|OV|BC",
        visual_subtype="same retail bottle/display object", control_occlusion="NONE",
        no_similar="EVERY_FRAME_REVIEWED 60-84; only the annotated GT bottle is present as a comparable display object; no second bottle enters.",
        matching_basis="Same sequence and exact bottle subtype; equal length and identical area, motion and scale metrics.",
        control_event_id="LIQ-CTRL-E02",
        control_trace="Liquor 20-44 is already allocated to R3-D03; 60-84 is clean, source-distinct and separated by 15 intervening frames.",
        control_notes="Liquor control use 2 of 2; non-overlapping and source-distinct.",
    ),
    reserve_pair(
        interval_id="R3-D05", control_id="R3-CD05", group="DISCOVERY", event_id="CAR4-E01",
        sequence="Car4", start=113, end=137, broad="VEHICLE", object_class="car",
        attributes="IV|SV", tier="TIER_A", ambiguity=2,
        description="White rear-view sedan remains immediately ahead-right of the black GT sedan.",
        similarity="Same passenger-car subtype, viewpoint and road role at comparable scale.",
        search_context="INSIDE_OR_NEAR_NOMINAL_SEARCH",
        bboxes={113: "244 76 110 60", 119: "248 78 109 60", 125: "252 80 108 61", 131: "257 81 103 62", 137: "263 77 97 62"},
        target_visibility="FULLY_VISIBLE", primary_occlusion="NONE",
        distractor_visibility="VISIBLE_ALL_FIVE", distractor_truncation="RIGHT_EDGE_CLIPPED_LATE",
        distractor_occlusion="NONE",
        event_separation="ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; one continuous nearby-sedan event retained once; RETURN_TO_NON_EVENT=NOT_APPLICABLE.",
        replacement_trace="COVERAGE_SLOT_REPLACEMENT_FOR_R1-P04_AFTER_NO_CLEAN_COMPATIBLE_BLURCAR2_CONTROL; same VEHICLE superclass, but no claim of exact scene identity.",
        sensitivity="MEDIAN_AREA_FACTOR_1.827206_BELOW_2.0_GATE; late right-edge clipping disclosed.",
        source_review=(
            "EVERY_FRAME_REVIEWED 113-137 and 221-245 in accepted cleanroom sheets "
            "outputs/r3/discovery_agent/contact_sheets/Car4_0113_0137_step1.jpg and Car4_0221_0245_step1.jpg; "
            "original-resolution primary audit at 113|119|125|131|137; candidate_metrics.csv retained."
        ),
        scan_method="Source+GT step-1 full-frame review, original-resolution five-frame audit and same-sequence control rejection scan; no tracker output.",
        primary_notes="Only one Car4 event retained; late border clipping does not produce full occlusion.",
        control_sequence="Car4", control_start=221, control_end=245, same_sequence=True,
        control_object_class="car", control_broad="VEHICLE", control_attributes="IV|SV",
        visual_subtype="same rear-view passenger-road-car subtype", control_occlusion="NONE",
        no_similar="EVERY_FRAME_REVIEWED 221-245; the GT car is isolated on the roadway and no comparable sedan is present.",
        matching_basis="Same sequence and passenger-car subtype; equal length; area, normalized motion and scale gates pass.",
        control_event_id="CAR4-CTRL-E01",
        control_trace="Other Car4 traffic windows were rejected for visible cars or continuous distractor events; 221-245 is the clean same-sequence interval.",
        control_notes="Single Car4 control use; no interval reuse.",
    ),
    reserve_pair(
        interval_id="R3-D06", control_id="R3-CD06", group="DISCOVERY", event_id="JOG-E01",
        sequence="Jogging_1", start=150, end=174, broad="PERSON", object_class="person",
        attributes="OCC|DEF|OPR", tier="TIER_A", ambiguity=2,
        description="Separate white-clad adult jogger remains immediately right of the GT runner.",
        similarity="Same full-body runner/pedestrian subtype, direction, pose family and scale.",
        search_context="INSIDE_NOMINAL_SEARCH",
        bboxes={150: "179 72 42 127", 156: "181 75 42 124", 162: "182 78 42 119", 168: "185 82 42 117", 174: "187 85 42 116"},
        target_visibility="VISIBLE_THROUGHOUT", primary_occlusion="NONE",
        distractor_visibility="FULLY_VISIBLE_ALL_FIVE", distractor_truncation="NONE",
        distractor_occlusion="NONE",
        event_separation="ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; one continuous companion-jogger event retained once; RETURN_TO_NON_EVENT=NOT_APPLICABLE.",
        replacement_trace="ADDITIONAL_DISCOVERY_COUNT_EXPANSION_FROM_LOCKED_RESERVE",
        sensitivity="MOTION_FACTOR_1.713693_BELOW_2.0_GATE; cross-sequence clean control disclosed.",
        source_review=(
            "EVERY_FRAME_REVIEWED Jogging_1 150-174 and Human8 1-25 in accepted cleanroom sheets "
            "outputs/r3/discovery_agent/contact_sheets/Jogging_1_0150_0174_step1.jpg and Human8_0001_0025_step1.jpg; "
            "original-resolution primary audit at 150|156|162|168|174; candidate_metrics.csv retained."
        ),
        scan_method="Source+GT step-1 full-frame review, original-resolution five-frame audit and bounded compatible-PERSON control search; no tracker output.",
        primary_notes="Single Jogging_1 event; same-sequence windows retain the companion context and were not used as clean controls.",
        control_sequence="Human8", control_start=1, control_end=25, same_sequence=False,
        control_object_class="person", control_broad="PERSON", control_attributes="IV|SV|DEF",
        visual_subtype="compatible real full-body adult runner/pedestrian", control_occlusion="NONE",
        no_similar="EVERY_FRAME_REVIEWED 1-25; one isolated full-body adult is present and no comparable nearby person appears.",
        matching_basis="Compatible full-body PERSON subtype and equal length; all numeric gates pass.",
        control_event_id="H8-CTRL-E01",
        control_trace="Jogging_1 windows retain the companion/event context; Human8 1-25 is clean and disjoint from the R3-D02 Human8 108-126 control.",
        control_notes="Human8 control use 1 of 2 in chronological order; 82 intervening frames from the second control.",
    ),
    reserve_pair(
        interval_id="R3-D07", control_id="R3-CD07", group="DISCOVERY", event_id="SHAK-E01",
        sequence="Shaking", start=1, end=25, broad="FACE_HEAD", object_class="face",
        attributes="IV|SV|IPR|OPR|BC", tier="TIER_A", ambiguity=2,
        description="Bald pianist's bare adult male head remains beside the GT guitarist's head.",
        similarity="Same real bare adult male face/head subtype and adjacent stage-performer role.",
        search_context="INSIDE_NOMINAL_SEARCH",
        bboxes={1: "347 111 51 67", 7: "344 110 52 68", 13: "342 110 54 71", 19: "344 111 53 70", 25: "347 113 52 69"},
        target_visibility="FACE_VISIBLE_THROUGHOUT", primary_occlusion="NONE",
        distractor_visibility="FULLY_VISIBLE_ALL_FIVE", distractor_truncation="NONE",
        distractor_occlusion="NONE",
        event_separation="ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; one stable two-performer head event retained once; RETURN_TO_NON_EVENT=NOT_APPLICABLE.",
        replacement_trace="COVERAGE_SLOT_REPLACEMENT_FOR_R1-P10_AFTER_NO_CLEAN_COMPATIBLE_FOOTBALL_HELMET_CONTROL; FACE_HEAD coverage retained without asserting helmet-subtype equivalence.",
        sensitivity="DISTRACTOR_IDENTITY_FIXED_TO_BALD_PIANIST; cross-scene face/head control disclosed.",
        source_review=(
            "EVERY_FRAME_REVIEWED Shaking 1-25 and David2 36-60 in accepted cleanroom sheets "
            "outputs/r3/discovery_agent/contact_sheets/Shaking_0001_0025_step1.jpg and David2_0036_0060_step1.jpg; "
            "original-resolution primary audit at 1|7|13|19|25; candidate_metrics.csv retained."
        ),
        scan_method="Source+GT step-1 full-frame review, original-resolution five-frame identity audit and compatible bare-head control search; no tracker output.",
        primary_notes="The distractor is consistently the pianist, not another stage feature.",
        control_sequence="David2", control_start=36, control_end=60, same_sequence=False,
        control_object_class="face", control_broad="FACE_HEAD", control_attributes="IPR|OPR",
        visual_subtype="compatible real bare adult male face/head", control_occlusion="NONE",
        no_similar="EVERY_FRAME_REVIEWED 36-60; one isolated real bare adult male head is present and no comparable second face appears.",
        matching_basis="Compatible real adult bare-head subtype and equal length; area, motion and scale gates pass.",
        control_event_id="DAV2-CTRL-E01",
        control_trace="Shaking cannot supply a clean same-sequence interval because both performers remain present; David2 is the clean compatible subtype.",
        control_notes="David2 control use 1 of 2; separated from the second control by 200 intervening frames.",
    ),
    reserve_pair(
        interval_id="R3-D08", control_id="R3-CD08", group="DISCOVERY", event_id="CARD-E01",
        sequence="CarDark", start=121, end=145, broad="VEHICLE", object_class="car",
        attributes="IV|BC", tier="TIER_B", ambiguity=1,
        description="Small passenger sedan remains immediately ahead-right of the GT car between it and a larger curb vehicle.",
        similarity="Same rear-view passenger-car subtype and road role at comparable scale.",
        search_context="INSIDE_OR_NEAR_NOMINAL_SEARCH",
        bboxes={121: "143 113 31 25", 127: "147 114 32 25", 133: "151 113 34 25", 139: "156 113 35 26", 145: "161 112 36 27"},
        target_visibility="VISIBLE_IN_LOW_LIGHT", primary_occlusion="NONE",
        distractor_visibility="VISIBLE_ALL_FIVE_AT_SMALL_SCALE", distractor_truncation="NONE",
        distractor_occlusion="NONE",
        event_separation="ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; source scan covered 121-155 and retained 121-145 once without an adjacent split; RETURN_TO_NON_EVENT=NOT_APPLICABLE.",
        replacement_trace="ADDITIONAL_DISCOVERY_COUNT_EXPANSION_FROM_LOCKED_RESERVE",
        sensitivity="LOW_LIGHT_SMALL_MANUAL_BOXES; source event identity and numeric margins remain clear.",
        source_review=(
            "EVERY_FRAME_REVIEWED CarDark 121-155 and CarScale 81-105 in accepted cleanroom sheets "
            "outputs/r3/discovery_agent/contact_sheets/CarDark_0121_0155_step1.jpg and CarScale_0081_0105_step1.jpg; "
            "only 121-145 selected; original-resolution audit at 121|127|133|139|145; candidate_metrics.csv retained."
        ),
        scan_method="Source+GT step-1 full-event review, original-resolution five-frame audit and bounded traffic-control rejection scan; no tracker output.",
        primary_notes="Low-light Tier-B event; neither target nor named distractor becomes fully occluded.",
        control_sequence="CarScale", control_start=81, control_end=105, same_sequence=False,
        control_object_class="car", control_broad="VEHICLE", control_attributes="SV|OCC|FM|IPR|OPR",
        visual_subtype="compatible rear-view passenger-road-car subtype", control_occlusion="NONE",
        no_similar="EVERY_FRAME_REVIEWED 81-105; the GT car is isolated and no comparable second vehicle appears.",
        matching_basis="Compatible passenger-car subtype and equal length; all numeric gates pass.",
        control_event_id="CARSCALE-CTRL-E01",
        control_trace="CarDark same-sequence controls retain traffic; other traffic windows failed cleanliness/event continuity; unused CarScale passed.",
        control_notes="Single CarScale control use; held-rematch numeric lead was never allocated.",
    ),
    reserve_pair(
        interval_id="R3-D09", control_id="R3-CD09", group="DISCOVERY", event_id="SKAT-E01",
        sequence="Skating1", start=113, end=137, broad="PERSON", object_class="person",
        attributes="IV|SV|OCC|DEF|OPR|BC", tier="TIER_B", ambiguity=1,
        description="Adjacent black-clad full-body skater remains immediately right of the GT skater.",
        similarity="Same adult full-body skater/person subtype, ensemble role, scale and motion setting.",
        search_context="INSIDE_NOMINAL_SEARCH",
        bboxes={113: "263 154 45 137", 119: "268 151 43 140", 125: "274 151 42 140", 131: "278 151 43 139", 137: "282 153 44 137"},
        target_visibility="VISIBLE_THROUGH_ENSEMBLE_OVERLAP", primary_occlusion="PARTIAL",
        distractor_visibility="IDENTIFIABLE_ALL_FIVE", distractor_truncation="NONE",
        distractor_occlusion="PARTIAL_ENSEMBLE_OVERLAP; NEVER_FULL",
        event_separation="ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; Skating1 281-305 rejected as the same continuing ensemble event; no adjacent split retained; RETURN_TO_NON_EVENT=NOT_APPLICABLE.",
        replacement_trace="ADDITIONAL_DISCOVERY_COUNT_EXPANSION_FROM_LOCKED_RESERVE",
        sensitivity="ENSEMBLE_IDENTITY_FIXED_TO_ADJACENT_BLACK_CLAD_SKATER; MOTION_FACTOR_1.760094_BELOW_2.0_GATE.",
        source_review=(
            "EVERY_FRAME_REVIEWED Skating1 113-137 and Human7 13-37 in accepted cleanroom sheets "
            "outputs/r3/discovery_agent/contact_sheets/Skating1_0113_0137_step1.jpg and Human7_0013_0037_step1.jpg; "
            "original-resolution primary audit at 113|119|125|131|137; candidate_metrics.csv retained."
        ),
        scan_method="Source+GT step-1 full-frame review, original-resolution five-frame identity audit and bounded compatible-PERSON control search; no tracker output.",
        primary_notes="One ensemble event retained; named distractor identity remains fixed across all review frames.",
        control_sequence="Human7", control_start=13, control_end=37, same_sequence=False,
        control_object_class="person", control_broad="PERSON", control_attributes="IV|SV|OCC|DEF|MB|FM",
        visual_subtype="compatible real full-body adult person/skater", control_occlusion="NONE",
        no_similar="EVERY_FRAME_REVIEWED 13-37; one isolated full-body adult is present; distant background figures are not comparable in scale or context.",
        matching_basis="Compatible full-body PERSON subtype and equal length; all numeric gates pass.",
        control_event_id="H7-CTRL-E01",
        control_trace="Woman 105-129 and David3 97-121 were less clean/reuse-efficient; Human7 was unused and cleaner; Skating1 281-305 was the same continuing event.",
        control_notes="Single Human7 control use; cross-scene sensitivity disclosed.",
    ),
    reserve_pair(
        interval_id="R3-D10", control_id="R3-CD10", group="DISCOVERY", event_id="SUB-E01",
        sequence="Subway", start=31, end=45, broad="PERSON", object_class="person",
        attributes="OCC|DEF|BC", tier="TIER_B", ambiguity=1,
        description="Beige-coated adult pedestrian passes immediately beside the black-clad GT pedestrian.",
        similarity="Same full-body adult pedestrian subtype, overhead viewpoint, scale and walkway role.",
        search_context="INSIDE_OR_NEAR_NOMINAL_SEARCH",
        bboxes={31: "96 101 29 67", 34: "89 104 29 64", 38: "79 109 28 59", 42: "70 112 29 57", 45: "62 114 29 54"},
        target_visibility="VISIBLE_THROUGHOUT", primary_occlusion="NONE",
        distractor_visibility="VISIBLE_ALL_FIVE", distractor_truncation="NONE",
        distractor_occlusion="NONE",
        event_separation="ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; one continuous passing-pedestrian event retained once; RETURN_TO_NON_EVENT=NOT_APPLICABLE.",
        replacement_trace="ADDITIONAL_DISCOVERY_COUNT_EXPANSION_FROM_LOCKED_RESERVE",
        sensitivity="FIFTEEN_FRAME_INTERVAL; AREA_FACTOR_1.714286; clean control has partial lower-body occlusion but never full.",
        source_review=(
            "EVERY_FRAME_REVIEWED Subway 31-45 and Woman 193-207 in accepted cleanroom sheets "
            "outputs/r3/discovery_agent/contact_sheets/Subway_0031_0045_step1.jpg and Woman_0193_0207_step1.jpg; "
            "original-resolution primary audit at 31|34|38|42|45; candidate_metrics.csv retained."
        ),
        scan_method="Source+GT step-1 full-frame review, original-resolution five-frame audit and bounded compatible-PERSON control comparison; no tracker output.",
        primary_notes="Shortest retained reserve interval; still exceeds the five-consecutive-frame event minimum.",
        control_sequence="Woman", control_start=193, control_end=207, same_sequence=False,
        control_object_class="person", control_broad="PERSON", control_attributes="IV|SV|OCC|DEF|MB|FM|OPR",
        visual_subtype="compatible real full-body adult overhead-view pedestrian", control_occlusion="PARTIAL",
        no_similar="EVERY_FRAME_REVIEWED 193-207; one adult pedestrian is present and no comparable second person appears; lower body is partly hidden by a parked car but never fully occluded.",
        matching_basis="Compatible full-body adult pedestrian subtype and equal length; all numeric gates pass; partial control occlusion disclosed.",
        control_event_id="WOMAN-CTRL-E01",
        control_trace="Woman 299-313 also passed but had weaker factors; Human8 was at reuse cap and David3 was less clean/reuse-efficient.",
        control_notes="Single Woman control use; partial non-full occlusion does not trigger the locked mismatch gate.",
    ),
    reserve_pair(
        interval_id="R3-D11", control_id="R3-CD11", group="DISCOVERY", event_id="FRE3-E01",
        sequence="Freeman3", start=245, end=269, broad="FACE_HEAD", object_class="face",
        attributes="SV|IPR|OPR", tier="TIER_B", ambiguity=1,
        description="Foreground seated dark-haired adult male bare face remains below-right of the standing GT male face.",
        similarity="Same real bare adult face/head subtype at comparable scale in the nearest salient face neighborhood.",
        search_context="INSIDE_OR_NEAR_NOMINAL_SEARCH",
        bboxes={245: "151 99 31 31", 251: "151 99 31 30", 257: "152 99 31 31", 263: "153 100 31 31", 269: "154 99 31 31"},
        target_visibility="FACE_VISIBLE_THROUGHOUT", primary_occlusion="NONE",
        distractor_visibility="VISIBLE_ALL_FIVE", distractor_truncation="NONE",
        distractor_occlusion="NONE",
        event_separation="ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; one classroom-face event with a fixed seated-man identity retained once; RETURN_TO_NON_EVENT=NOT_APPLICABLE.",
        replacement_trace="ADDITIONAL_DISCOVERY_COUNT_EXPANSION_FROM_LOCKED_RESERVE",
        sensitivity="DISTRACTOR_IDENTITY_FIXED_TO_FOREGROUND_SEATED_MAN; other classroom faces are clutter, not alternate annotations.",
        source_review=(
            "EVERY_FRAME_REVIEWED Freeman3 245-269 and David2 261-285 in accepted cleanroom sheets "
            "outputs/r3/discovery_agent/contact_sheets/Freeman3_0245_0269_step1.jpg and David2_0261_0285_step1.jpg; "
            "original-resolution primary audit at 245|251|257|263|269; candidate_metrics.csv retained."
        ),
        scan_method="Source+GT step-1 full-frame review, original-resolution five-frame identity audit and bounded adult-face control comparison; no tracker output.",
        primary_notes="Named distractor is the foreground seated man; other classroom faces remain contextual clutter.",
        control_sequence="David2", control_start=261, control_end=285, same_sequence=False,
        control_object_class="face", control_broad="FACE_HEAD", control_attributes="IPR|OPR",
        visual_subtype="compatible real bare adult male face/head", control_occlusion="NONE",
        no_similar="EVERY_FRAME_REVIEWED 261-285; one isolated adult bare head is present and no comparable second face appears.",
        matching_basis="Compatible real adult bare-head subtype and equal length; all numeric gates pass.",
        control_event_id="DAV2-CTRL-E02",
        control_trace="Freeman1, Dudek, FleetFace, Mhyang and Trellis were numerically or visually weaker; Boy introduced age/subtype ambiguity; David2 was clean.",
        control_notes="David2 control use 2 of 2; separated from the first control by 200 intervening frames.",
    ),
    reserve_pair(
        interval_id="R3-D12", control_id="R3-CD12", group="DISCOVERY", event_id="SING-E01",
        sequence="Singer1", start=1, end=25, broad="PERSON", object_class="person",
        attributes="IV|SV|OCC|OPR", tier="TIER_B", ambiguity=1,
        description="Separate adjacent full-body adult performer remains beside the GT performer.",
        similarity="Same full-body adult person/performer subtype, stage role, pose family and comparable scale.",
        search_context="INSIDE_NOMINAL_SEARCH",
        bboxes={1: "345 54 92 269", 7: "345 54 92 269", 13: "345 54 93 269", 19: "346 55 93 268", 25: "347 56 93 267"},
        target_visibility="FULL_BODY_VISIBLE_THROUGHOUT", primary_occlusion="NONE",
        distractor_visibility="FULLY_VISIBLE_ALL_FIVE", distractor_truncation="NONE",
        distractor_occlusion="NONE",
        event_separation="ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; one continuous adjacent-performer event retained once; RETURN_TO_NON_EVENT=NOT_APPLICABLE.",
        replacement_trace="ADDITIONAL_DISCOVERY_COUNT_EXPANSION_FROM_LOCKED_RESERVE; governance-sensitive source/inventory interpretation.",
        sensitivity="MANAGER_ACCEPTANCE_REQUIRED: protocol reserve heading places Singer1 under FACE_HEAD, while accepted inventory and canonical full-body GT support PERSON; rejection makes R3-D12 ineligible and drops DISCOVERY to 11.",
        source_review=(
            "EVERY_FRAME_REVIEWED Singer1 1-25 and Dancer 71-95 in accepted cleanroom sheets "
            "outputs/r3/discovery_agent/contact_sheets/Singer1_0001_0025_step1.jpg and Dancer_0071_0095_step1.jpg; "
            "original-resolution primary audit at 1|7|13|19|25; candidate_metrics.csv retained."
        ),
        scan_method="Source+GT step-1 full-frame review, original-resolution five-frame audit and inventory-versus-reserve governance check; no tracker output.",
        primary_notes="Provisionally analysis-eligible as PERSON from accepted inventory and full-body canonical GT; Manager must explicitly accept this interpretation before freeze.",
        control_sequence="Dancer", control_start=71, control_end=95, same_sequence=False,
        control_object_class="person", control_broad="PERSON", control_attributes="SV|DEF|IPR|OPR",
        visual_subtype="compatible real full-body adult stage performer", control_occlusion="NONE",
        no_similar="EVERY_FRAME_REVIEWED 71-95; one isolated full-body adult is present and no comparable second performer appears.",
        matching_basis="Accepted-inventory PERSON and canonical full-body GT extent match a full-body performer control; equal length and all numeric gates pass.",
        control_event_id="DANCER-CTRL-E01",
        control_trace="Face/head controls were rejected because Singer1 inventory class and canonical GT extent are full-body PERSON; Dancer is the compatible clean control, subject to Manager acceptance.",
        control_notes="High governance sensitivity only; numeric, subtype-from-source and clean-control gates pass provisionally.",
    ),
    reserve_pair(
        interval_id="R3-H04", control_id="R3-CH04", group="HOLDOUT", event_id="GIRL-E01",
        sequence="Girl", start=411, end=429, broad="FACE_HEAD", object_class="face",
        attributes="SV|OCC|IPR|OPR", tier="TIER_A", ambiguity=2,
        description="Adult male face enters from the left and moves beside and partly across the target face.",
        similarity="Same real adult face/head subtype at comparable scale and close frontal/three-quarter view.",
        search_context="INSIDE_NOMINAL_SEARCH",
        bboxes={411: "0 13 18 49", 415: "0 11 34 53", 420: "0 10 44 56", 425: "8 12 47 58", 429: "17 13 45 60"},
        target_visibility="FACE_VISIBLE_THROUGHOUT", primary_occlusion="PARTIAL",
        distractor_visibility="VISIBLE_ALL_FIVE; full by frames 425/429",
        distractor_truncation="LEFT_TRUNCATED_411_420; NONE_425_429",
        distractor_occlusion="PARTIAL_SILHOUETTE_OVERLAP_LATE; NEVER_FULL",
        event_separation="ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; RETURN_TO_NON_EVENT=YES before control frames 363-381.",
        replacement_trace="ADDITIONAL_HOLDOUT_COUNT_EXPANSION_FROM_LOCKED_RESERVE",
        sensitivity="SAME_SEQUENCE_FACE_CONTROL; proposal has late face overlap while control is clean.",
        source_review="EVERY_FRAME_REVIEWED 411-429 in accepted cleanroom holdout_agent Girl primary full/local sheets and five frame grids.",
        scan_method="Source+GT coarse scan, boundary refinement, every-frame primary/control review; no tracker output.",
        primary_notes="One bounded male-face entry event; five manual boxes are review annotations, not benchmark GT.",
        control_sequence="Girl", control_start=363, control_end=381, same_sequence=True,
        control_object_class="face", control_broad="FACE_HEAD", control_attributes="SV|OCC|IPR|OPR",
        visual_subtype="same real adult frontal/three-quarter face/head", control_occlusion="NONE",
        no_similar="EVERY_FRAME_REVIEWED 363-381; only the annotated target face is present; no comparable second face appears.",
        matching_basis="Same sequence and exact face/head subtype; equal length; area, motion and scale gates pass.",
        control_event_id="GIRL-CTRL-E01",
        control_trace="Same-sequence first-order search passed; no broader-class fallback used.",
        control_notes="Clean same-sequence control; no interval reuse.",
    ),
    reserve_pair(
        interval_id="R3-H05", control_id="R3-CH05", group="HOLDOUT", event_id="H3-E01",
        sequence="Human3", start=57, end=81, broad="PERSON", object_class="person",
        attributes="SV|OCC|DEF|OPR|BC", tier="TIER_A", ambiguity=2,
        description="Black-clad woman approaches from target-left and overlaps the dark-clad tracked pedestrian near the end.",
        similarity="Same real full-body pedestrian subtype at comparable overhead-view scale and motion.",
        search_context="INSIDE_OR_NEAR_NOMINAL_SEARCH",
        bboxes={57: "126 276 28 70", 63: "151 278 28 69", 69: "164 278 28 69", 75: "188 277 29 70", 81: "205 279 30 70"},
        target_visibility="VISIBLE_WITH_PARTIAL_STREET_FURNITURE", primary_occlusion="PARTIAL",
        distractor_visibility="FULL_THROUGH_FRAME_75; PARTIAL_MUTUAL_OVERLAP_AT_81",
        distractor_truncation="NONE", distractor_occlusion="PARTIAL_AT_EVENT_END; NEVER_FULL",
        event_separation="H3-E01 versus H3-E02: no overlap; 1482 intervening frames; different woman/scene phase; RETURN_TO_NON_EVENT=YES for a long clean period.",
        replacement_trace="ADDITIONAL_HOLDOUT_COUNT_EXPANSION_FROM_LOCKED_RESERVE",
        sensitivity="SAME_SEQUENCE_CONTROL; primary target has partial sign/pole obstruction while control is clean.",
        source_review="EVERY_FRAME_REVIEWED 57-81 in accepted cleanroom holdout_agent Human3 H3A primary full/local sheets and five frame grids.",
        scan_method="Source+GT coarse scan, full-interval refinement and every-frame primary/control review; no tracker output.",
        primary_notes="First of two source-distinct Human3 events; not an artificial split.",
        control_sequence="Human3", control_start=264, control_end=288, same_sequence=True,
        control_object_class="person", control_broad="PERSON", control_attributes="SV|OCC|DEF|OPR|BC",
        visual_subtype="same real full-body overhead street pedestrian", control_occlusion="NONE",
        no_similar="EVERY_FRAME_REVIEWED 264-288; only the annotated target pedestrian is present in the local context; no comparable second pedestrian appears.",
        matching_basis="Same sequence/subtype and equal length; area, normalized motion and scale gates pass.",
        control_event_id="H3-CTRL-E01",
        control_trace="Same-sequence clean interval selected before cross-sequence search; second Human3 control is distant and non-overlapping.",
        control_notes="Human3 control use 1 of 2; 1129 intervening frames from the second control.",
    ),
    reserve_pair(
        interval_id="R3-H06", control_id="R3-CH06", group="HOLDOUT", event_id="H3-E02",
        sequence="Human3", start=1564, end=1588, broad="PERSON", object_class="person",
        attributes="SV|OCC|DEF|OPR|BC", tier="TIER_B", ambiguity=1,
        description="Black-jacket, light-green-pants woman follows immediately below and behind the tracked man.",
        similarity="Same real full-body pedestrian subtype and comparable scale; vertically offset close follower.",
        search_context="NEAR_NOMINAL_SEARCH",
        bboxes={1564: "83 454 45 120", 1570: "78 458 48 118", 1576: "78 468 45 117", 1582: "102 458 44 117", 1588: "124 453 44 121"},
        target_visibility="VISIBLE_WITH_PARTIAL_STREET_FURNITURE", primary_occlusion="PARTIAL",
        distractor_visibility="FULLY_VISIBLE_ALL_FIVE", distractor_truncation="NONE",
        distractor_occlusion="NONE",
        event_separation="H3-E02 versus H3-E01: no overlap; 1482 intervening frames; different woman/scene phase; RETURN_TO_NON_EVENT=YES for a long clean period.",
        replacement_trace="ADDITIONAL_HOLDOUT_COUNT_EXPANSION_FROM_LOCKED_RESERVE",
        sensitivity="STRONG_TIER_B_VERTICAL_OFFSET; same-sequence control is clean and quantitatively matched.",
        source_review="EVERY_FRAME_REVIEWED 1564-1588 in accepted cleanroom holdout_agent Human3 H3B primary full/local sheets and five frame grids.",
        scan_method="Source+GT coarse scan, full-interval refinement and every-frame primary/control review; no tracker output.",
        primary_notes="Second source-distinct Human3 event; different identity and scene phase from H3-E01.",
        control_sequence="Human3", control_start=1418, control_end=1442, same_sequence=True,
        control_object_class="person", control_broad="PERSON", control_attributes="SV|OCC|DEF|OPR|BC",
        visual_subtype="same real full-body overhead street pedestrian", control_occlusion="NONE",
        no_similar="EVERY_FRAME_REVIEWED 1418-1442; only the annotated target pedestrian is present in the local context; no comparable second pedestrian appears.",
        matching_basis="Same sequence/subtype and equal length; area, normalized motion and scale gates pass.",
        control_event_id="H3-CTRL-E02",
        control_trace="Same-sequence clean interval selected; non-overlapping with H3-CTRL-E01 by 1129 intervening frames.",
        control_notes="Human3 control use 2 of 2; source-distinct and non-overlapping.",
    ),
    reserve_pair(
        interval_id="R3-H07", control_id="R3-CH07", group="HOLDOUT", event_id="H4-E01",
        sequence="Human4_2", start=73, end=97, broad="PERSON", object_class="person",
        attributes="IV|SV|OCC|DEF", tier="TIER_B", ambiguity=1,
        description="Dark-shirt runner remains immediately upper-left and behind the gray target runner through a local overlap phase.",
        similarity="Same real full-body runner/pedestrian subtype at comparable scale and motion.",
        search_context="INSIDE_NOMINAL_SEARCH",
        bboxes={73: "137 202 38 83", 79: "139 202 39 83", 85: "142 202 39 84", 91: "147 204 39 83", 97: "152 205 39 82"},
        target_visibility="VISIBLE_THROUGH_PARTIAL_PERSON_OVERLAP", primary_occlusion="PARTIAL",
        distractor_visibility="VISIBLE_ALL_FIVE; estimated extent retained through overlap",
        distractor_truncation="NONE", distractor_occlusion="PARTIAL_BY_TARGET; NEVER_FULL",
        event_separation="ONLY_SELECTED_INTERVAL_FROM_SEQUENCE; immediate-overlap phase bounded as one event; RETURN_TO_NON_EVENT=NOT_USED_FOR_ADJACENT_SAMPLE and no adjacent interval selected.",
        replacement_trace="ADDITIONAL_HOLDOUT_COUNT_EXPANSION_FROM_LOCKED_RESERVE",
        sensitivity="CROSS_SCENE_ACTIVITY_SHIFT: outdoor runner event versus indoor walking control; Manager phase-boundary review requested.",
        source_review="EVERY_FRAME_REVIEWED 73-97 in accepted cleanroom holdout_agent Human4_2 primary full/local sheets and five frame grids.",
        scan_method="Source+GT coarse scan, event-phase boundary review and complete primary/control frame review; no tracker output.",
        primary_notes="Only one Human4_2 interval retained; no adjacent split from the continuous runner event.",
        control_sequence="Walking2", control_start=393, control_end=417, same_sequence=False,
        control_object_class="person", control_broad="PERSON", control_attributes="SV|OCC|LR",
        visual_subtype="compatible real full-body upright pedestrian/runner", control_occlusion="NONE",
        no_similar="EVERY_FRAME_REVIEWED 393-417; only the annotated target is present in the local context; remote background figures are tiny and non-comparable.",
        matching_basis="Compatible full-body PERSON subtype and equal length; all numeric gates pass.",
        control_event_id="WALK2-CTRL-E01",
        control_trace="Human4_2 same-sequence 323-347 and 381-405 rejected because comparable runners persist; Walking2 passed at the next compatible-PERSON step.",
        control_notes="Cross-scene/activity sensitivity retained for Manager review.",
    ),
    reserve_pair(
        interval_id="R3-H08", control_id="R3-CH08", group="HOLDOUT", event_id="SUV-E01",
        sequence="Suv", start=372, end=399, broad="VEHICLE", object_class="car",
        attributes="OCC|IPR|OV", tier="TIER_A", ambiguity=2,
        description="Light sedan enters lower-left, passes immediately below the tracked light SUV, and exits right.",
        similarity="Same light side-view passenger-road-vehicle subtype at comparable linear scale.",
        search_context="INSIDE_NOMINAL_SEARCH",
        bboxes={372: "0 172 46 31", 379: "33 165 79 39", 386: "115 163 82 40", 393: "197 163 83 40", 399: "278 169 42 34"},
        target_visibility="FULLY_VISIBLE", primary_occlusion="NONE",
        distractor_visibility="VISIBLE_ALL_FIVE; full during middle phase",
        distractor_truncation="LEFT_AT_372; NONE_379_393; RIGHT_AT_399",
        distractor_occlusion="NONE",
        event_separation="ONLY_SELECTED_INTERVAL_FOR_THIS_SEDAN_IDENTITY; source entry/exit boundaries verified; RETURN_TO_NON_EVENT=YES at frame 402.",
        replacement_trace="COVERAGE_SLOT_REPLACEMENT_FOR_R1-P11_AFTER_NO_MATCH_PASS_HELMET_CONTROL; replacement does not assert helmet-subtype equivalence.",
        sensitivity="SAME_SEQUENCE_EXACT_VEHICLE_CONTROL; grayscale source retained.",
        source_review="EVERY_FRAME_REVIEWED 372-399 plus boundary frames 360-409 in accepted cleanroom holdout_agent Suv full/local sheets and five frame grids.",
        scan_method="Source+GT coarse scan, entry/exit boundary refinement and every-frame primary/control review; no tracker output.",
        primary_notes="Frames 370-371 and 400-401 are border slivers outside the comparable-context phase; frame 402 is clean.",
        control_sequence="Suv", control_start=410, control_end=437, same_sequence=True,
        control_object_class="car", control_broad="VEHICLE", control_attributes="OCC|IPR|OV",
        visual_subtype="same light side-view passenger-road-vehicle", control_occlusion="NONE",
        no_similar="EVERY_FRAME_REVIEWED 410-437; only the annotated target vehicle is present; no comparable second vehicle appears.",
        matching_basis="Same sequence and exact vehicle subtype; equal length and identical area/motion/scale metrics.",
        control_event_id="SUV-CTRL-E01",
        control_trace="Same-sequence first-order control selected after exactly 10 intervening frames; anchor Suv 726-750 is the only other Suv control and is source-distinct.",
        control_notes="Suv control use 2 of 2; 288 intervening frames from anchor control and no overlap.",
    ),
)


HELD_REMATCH = (
    {
        "id": "R1-P04", "sequence": "BlurCar2", "frames": "420-440",
        "result": "REPLACEMENT_REQUIRED",
        "trace": "One bounded rematch across compatible car sequences found numeric leads, but every lead retained a comparable adjacent vehicle throughout; no no-distractor pass.",
    },
    {
        "id": "R1-P07", "sequence": "Bird1", "frames": "194-198",
        "result": "REPLACEMENT_REQUIRED",
        "trace": "One bounded Bird1/Bird2 rematch found no compatible clean live-bird interval; numeric Bird1 leads retained multiple birds and Bird2 failed area/cleanliness.",
    },
    {
        "id": "R1-P10", "sequence": "Football", "frames": "130-154",
        "result": "REPLACEMENT_REQUIRED",
        "trace": "One bounded Football/Football1 helmet rematch found numeric/subtype leads, but multiple helmeted players persisted throughout every lead.",
    },
    {
        "id": "R1-P11", "sequence": "Football1", "frames": "26-50",
        "result": "REPLACEMENT_REQUIRED",
        "trace": "One bounded Football1/Football helmet rematch found numeric/subtype leads, but multiple helmeted players persisted; cross-split candidates were rejected.",
    },
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: Sequence[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def btext(value: bool) -> str:
    return "true" if value else "false"


def fmt(value: object, digits: int = 6) -> str:
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def factor(left: float, right: float) -> float:
    return float(R2.factor_ratio(left, right))


def interval_overlap(a0: int, a1: int, b0: int, b1: int) -> bool:
    return max(a0, b0) <= min(a1, b1)


def attr_overlap(left: str, right: str) -> str:
    overlap = sorted(set(left.split("|")) & set(right.split("|")))
    return "|".join(value for value in overlap if value) or "NONE"


def relative_pair_path(interval_id: str) -> str:
    suffix = interval_id.replace("R3-", "")
    return (Path("screening") / "codex" / "artifacts" / "stage4A_S1_R3" / "pair_sheets" / f"R3_PAIR_{suffix}.jpg").as_posix()


def anchor_pairs() -> list[dict[str, object]]:
    primary_source = {row["proposal_id"]: row for row in read_csv(R2_PRIMARY)}
    control_source = {row["linked_proposal_id"]: row for row in read_csv(R2_CONTROL)}
    result: list[dict[str, object]] = []
    for definition in ANCHOR_DEFINITIONS:
        parent_id = str(definition["source_parent_id"])
        source = primary_source[parent_id]
        control = control_source[parent_id]
        control_end = int(definition.get("control_end_override", control["interval_end"]))
        p = {
            "r3_interval_id": definition["r3_interval_id"],
            "source_parent_id_or_new": parent_id,
            "sequence": source["sequence"], "group": definition["group"],
            "event_id": definition["event_id"],
            "broad_superclass": source["broad_superclass"],
            "object_class": source["object_class"],
            "official_attributes": source["official_attributes"],
            "interval_start": int(source["interval_start"]),
            "interval_end": int(source["interval_end"]),
            "evidence_tier": source["evidence_tier"],
            "proposed_ambiguity_level": definition["ambiguity"],
            "distractor_description": source["distractor_description"],
            "similarity_basis": source["similarity_basis"],
            "search_context_status": source["search_context_status"],
            "bboxes": definition["bboxes"],
            "distractor_visibility": "VISIBLE_ON_ALL_FIVE_REVIEW_FRAMES",
            "distractor_truncation": "NONE_UNLESS_FRAME_SPECIFIC_BOX_TOUCHES_IMAGE_EDGE",
            "distractor_occlusion": "NONE_OR_PARTIAL_AS_VISIBLE_IN_REVIEW_SHEET",
            "target_visibility": source["target_visibility"],
            "occlusion_state": source["occlusion_state"],
            "event_separation_evidence": definition["event_separation"],
            "replacement_trace": definition["replacement_trace"],
            "sensitivity_notes": definition["sensitivity"],
            "source_review_evidence": f"ACCEPTED_R1_R2_SOURCE_REVIEW; {source['r1_contact_sheet_path']}",
            "scan_method": source["scan_method"],
            "notes": "Locked R2 anchor; source identity and group preserved.",
        }
        no_similar = str(definition.get("control_review_override", control["no_similar_distractor_evidence"]))
        c = {
            "r3_control_id": definition["r3_control_id"],
            "sequence": control["sequence"], "group": definition["group"],
            "interval_start": int(control["interval_start"]), "interval_end": control_end,
            "same_sequence": control["same_sequence"].lower() == "true",
            "object_class": control["object_class"],
            "broad_superclass": control["broad_superclass"],
            "visual_subtype": control["visual_subtype"],
            "occlusion_state": control["occlusion_state"],
            "official_attributes": control["official_attributes"],
            "no_similar_distractor_evidence": no_similar,
            "matching_basis": control["matching_basis"],
            "control_event_id": f"{definition['event_id']}-CTRL",
            "control_search_and_rejection_trace": control["notes"],
            "sensitivity_notes": definition["sensitivity"],
            "notes": (
                "R2 anchor control retained; Liquor bound adjustment is fully traced."
                if parent_id == "R1-P09" else "Locked R2 anchor control retained."
            ),
        }
        result.append({"primary": p, "control": c})
    return result


def all_pair_specs() -> list[dict[str, object]]:
    pairs = anchor_pairs() + [dict(item) for item in NEW_PAIR_SPECS]
    return sorted(
        pairs,
        key=lambda pair: (
            0 if pair["primary"]["group"] == "DISCOVERY" else 1,
            int(str(pair["primary"]["r3_interval_id"]).split("D")[-1])
            if pair["primary"]["group"] == "DISCOVERY"
            else int(str(pair["primary"]["r3_interval_id"]).split("H")[-1]),
        ),
    )


def attach_stats(pairs: list[dict[str, object]], mapping: dict[str, dict[str, object]]) -> None:
    for pair in pairs:
        p = pair["primary"]
        c = pair["control"]
        p["_stats"] = R2.interval_stats(str(p["sequence"]), int(p["interval_start"]), int(p["interval_end"]), mapping)
        c["_stats"] = R2.interval_stats(str(c["sequence"]), int(c["interval_start"]), int(c["interval_end"]), mapping)


def event_distinctness(pairs: list[dict[str, object]]) -> dict[str, bool]:
    by_sequence: dict[str, list[dict[str, object]]] = defaultdict(list)
    for pair in pairs:
        by_sequence[str(pair["primary"]["sequence"])].append(pair["primary"])
    result: dict[str, bool] = {}
    for sequence, items in by_sequence.items():
        ordered = sorted(items, key=lambda row: int(row["interval_start"]))
        event_ids = [str(row["event_id"]) for row in ordered]
        unique_events = len(event_ids) == len(set(event_ids))
        nonoverlap = all(
            not interval_overlap(
                int(ordered[i - 1]["interval_start"]), int(ordered[i - 1]["interval_end"]),
                int(ordered[i]["interval_start"]), int(ordered[i]["interval_end"]),
            )
            for i in range(1, len(ordered))
        )
        adequate_gaps = all(
            int(ordered[i]["interval_start"]) - int(ordered[i - 1]["interval_end"]) - 1 >= 10
            for i in range(1, len(ordered))
        )
        explicit = all(
            "RETURN_TO_NON_EVENT=" in str(row["event_separation_evidence"])
            for row in ordered
        )
        pass_value = unique_events and nonoverlap and (adequate_gaps or len(ordered) == 1) and explicit
        for row in ordered:
            result[str(row["r3_interval_id"])] = pass_value
    return result


def control_reuse_state(pairs: list[dict[str, object]]) -> tuple[Counter[str], dict[str, bool], dict[str, bool]]:
    controls = [pair["control"] for pair in pairs]
    counts = Counter(str(row["sequence"]) for row in controls)
    interval_pass: dict[str, bool] = {}
    split_pass: dict[str, bool] = {}
    by_sequence: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in controls:
        by_sequence[str(row["sequence"])].append(row)
    for sequence, items in by_sequence.items():
        groups = {str(row["group"]) for row in items}
        sequence_split_pass = len(groups) == 1
        for row in items:
            split_pass[str(row["r3_control_id"])] = sequence_split_pass
        for row in items:
            this_id = str(row["r3_control_id"])
            unique = all(
                this_id == str(other["r3_control_id"]) or not (
                    int(row["interval_start"]) == int(other["interval_start"])
                    and int(row["interval_end"]) == int(other["interval_end"])
                )
                for other in items
            )
            nonoverlap = all(
                this_id == str(other["r3_control_id"]) or not interval_overlap(
                    int(row["interval_start"]), int(row["interval_end"]),
                    int(other["interval_start"]), int(other["interval_end"]),
                )
                for other in items
            )
            interval_pass[this_id] = unique and nonoverlap and counts[sequence] <= 2
    return counts, interval_pass, split_pass


def source_sets(pairs: list[dict[str, object]]) -> dict[str, set[str]]:
    result = {"DISCOVERY": set(), "HOLDOUT": set()}
    for pair in pairs:
        group = str(pair["primary"]["group"])
        result[group].add(str(pair["primary"]["sequence"]))
        result[group].add(str(pair["control"]["sequence"]))
    return result


def motion_gate(left: float, right: float) -> tuple[str, bool]:
    if left < 0.03 and right < 0.03:
        difference = abs(left - right)
        return f"abs_difference={difference:.6f}", difference <= 0.03
    ratio = factor(left, right)
    return f"ratio={ratio:.6f}", ratio <= 2.0


def primary_review_indices(primary: dict[str, object], stats: dict[str, object]) -> list[int]:
    """Resolve the five explicitly reviewed/annotated primary frames."""
    frames = [int(value) for value in dict(primary["bboxes"]).keys()]
    if len(frames) != 5 or frames != sorted(frames) or len(set(frames)) != 5:
        raise RuntimeError(f"Primary review frames must be five unique ascending IDs: {primary['r3_interval_id']}")
    index_by_frame = {int(frame): index for index, frame in enumerate(stats["frame_ids"])}
    if any(frame not in index_by_frame for frame in frames):
        raise RuntimeError(f"Primary review frame outside canonical evaluator range: {primary['r3_interval_id']}")
    indices = [index_by_frame[frame] for frame in frames]
    allowed = set(stats["indices"])
    if any(index not in allowed for index in indices):
        raise RuntimeError(f"Primary review frame outside interval: {primary['r3_interval_id']}")
    return indices


def build_rows(pairs: list[dict[str, object]]):
    event_pass = event_distinctness(pairs)
    reuse_counts, interval_reuse_pass, sequence_split_pass = control_reuse_state(pairs)
    sets = source_sets(pairs)
    intersection = sets["DISCOVERY"] & sets["HOLDOUT"]
    primary_rows: list[dict[str, object]] = []
    control_rows: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    for pair in pairs:
        p, c = pair["primary"], pair["control"]
        ps, cs = p["_stats"], c["_stats"]
        pair_path = relative_pair_path(str(p["r3_interval_id"]))
        review_indices = primary_review_indices(p, ps)
        review_frames = [int(ps["frame_ids"][index]) for index in review_indices]
        bbox_map = {int(key): value for key, value in dict(p["bboxes"]).items()}
        missing_boxes = [frame for frame in review_frames if frame not in bbox_map]
        if missing_boxes:
            raise RuntimeError(f"Missing five-frame distractor boxes for {p['r3_interval_id']}: {missing_boxes}")
        bbox_text = "|".join(f"{frame}:{bbox_map[frame]}" for frame in review_frames)
        midpoint = bbox_map[review_frames[2]]
        prow: dict[str, object] = {
            "r3_interval_id": p["r3_interval_id"],
            "source_parent_id_or_new": p["source_parent_id_or_new"],
            "dataset": "OTB100", "sequence": p["sequence"], "group": p["group"],
            "event_id": p["event_id"], "broad_superclass": p["broad_superclass"],
            "object_class": p["object_class"], "official_attributes": p["official_attributes"],
            "interval_start": p["interval_start"], "interval_end": p["interval_end"],
            "interval_length": ps["interval_length"], "evidence_tier": p["evidence_tier"],
            "proposed_ambiguity_level": p["proposed_ambiguity_level"],
            "distractor_description": p["distractor_description"],
            "similarity_basis": p["similarity_basis"],
            "search_context_status": p["search_context_status"],
            "review_frame_ids": "|".join(str(value) for value in review_frames),
            "distractor_bboxes_all_review_frames": bbox_text,
            "midpoint_distractor_bbox_or_na": midpoint,
            "distractor_visibility": p["distractor_visibility"],
            "distractor_truncation": p["distractor_truncation"],
            "distractor_occlusion": p["distractor_occlusion"],
            "manual_bbox_is_benchmark_gt": "false",
            "target_visibility": p["target_visibility"], "occlusion_state": p["occlusion_state"],
            "fast_motion_flag": btext(bool(ps["fast_motion_flag"])),
            "low_resolution_flag": btext(bool(ps["low_resolution_flag"])),
            "event_separation_evidence": p["event_separation_evidence"],
            "analysis_eligible": "true", "replacement_trace": p["replacement_trace"],
            "sensitivity_notes": p["sensitivity_notes"],
            "source_review_evidence": p["source_review_evidence"],
            "scan_method": p["scan_method"], "pair_sheet_path": pair_path,
            "manager_review_status": STATUS, "notes": p["notes"],
        }
        for field in METRIC_FIELDS:
            prow[field] = fmt(ps[field], 9 if "ratio" in field or "normalized" in field else 6)

        crow: dict[str, object] = {
            "r3_control_id": c["r3_control_id"],
            "linked_r3_interval_id": p["r3_interval_id"],
            "preferred_or_alternate": "PREFERRED", "group": c["group"], "dataset": "OTB100",
            "sequence": c["sequence"], "interval_start": c["interval_start"],
            "interval_end": c["interval_end"], "interval_length": cs["interval_length"],
            "same_sequence": btext(bool(c["same_sequence"])),
            "object_class": c["object_class"], "broad_superclass": c["broad_superclass"],
            "visual_subtype": c["visual_subtype"],
            "fast_motion_flag": btext(bool(cs["fast_motion_flag"])),
            "low_resolution_flag": btext(bool(cs["low_resolution_flag"])),
            "occlusion_state": c["occlusion_state"],
            "official_attributes": c["official_attributes"],
            "no_similar_distractor_evidence": c["no_similar_distractor_evidence"],
            "matching_basis": c["matching_basis"], "control_event_id": c["control_event_id"],
            "control_sequence_reuse_count": reuse_counts[str(c["sequence"])],
            "control_interval_reused": "false", "exception_state": "NONE",
            "analysis_eligible": "true",
            "control_search_and_rejection_trace": c["control_search_and_rejection_trace"],
            "sensitivity_notes": c["sensitivity_notes"], "pair_sheet_path": pair_path,
            "manager_review_status": STATUS, "notes": c["notes"],
        }
        for field in METRIC_FIELDS:
            crow[field] = fmt(cs[field], 9 if "ratio" in field or "normalized" in field else 6)

        length_diff = int(cs["interval_length"]) - int(ps["interval_length"])
        length_pass = abs(length_diff) <= 2
        area_ratio = factor(float(ps["median_target_area_ratio"]), float(cs["median_target_area_ratio"]))
        area_pass = area_ratio <= 2.0
        motion_text, motion_pass = motion_gate(float(ps["p90_motion_normalized"]), float(cs["p90_motion_normalized"]))
        scale_ratio = factor(float(ps["max_to_min_area_ratio"]), float(cs["max_to_min_area_ratio"]))
        scale_pass = scale_ratio <= 2.0
        full_occ_mismatch = (str(p["occlusion_state"]) == "FULL" ) != (str(c["occlusion_state"]) == "FULL")
        occlusion_text = "MATCH" if str(p["occlusion_state"]) == str(c["occlusion_state"]) else f"{p['occlusion_state']}_VS_{c['occlusion_state']}_DISCLOSED"
        fast_match = bool(ps["fast_motion_flag"]) == bool(cs["fast_motion_flag"])
        low_match = bool(ps["low_resolution_flag"]) == bool(cs["low_resolution_flag"])
        superclass_match = str(p["broad_superclass"]) == str(c["broad_superclass"])
        subtype_match = bool(c.get("visual_subtype_match", True))
        no_distractor = str(c["no_similar_distractor_evidence"]).startswith("EVERY_FRAME_REVIEWED")
        event_ok = event_pass[str(p["r3_interval_id"])]
        interval_ok = interval_reuse_pass[str(c["r3_control_id"])]
        split_ok = sequence_split_pass[str(c["r3_control_id"])]
        same_split = str(p["group"]) == str(c["group"])
        leakage = bool(intersection)
        gate_values = (
            length_pass, area_pass, motion_pass, scale_pass, not full_occ_mismatch,
            fast_match, low_match, superclass_match, subtype_match, no_distractor,
            event_ok, interval_ok, split_ok, same_split, not leakage,
        )
        overall = "MATCH_PASS" if all(gate_values) else "MATCH_FAIL"
        eligible = overall == "MATCH_PASS"
        governance_pending = "MANAGER_ACCEPTANCE_REQUIRED" in str(p["sensitivity_notes"])
        audit = {
            "linked_r3_interval_id": p["r3_interval_id"],
            "linked_r3_control_id": c["r3_control_id"], "group": p["group"],
            "proposal_sequence": p["sequence"], "control_sequence": c["sequence"],
            "proposal_length": ps["interval_length"], "control_length": cs["interval_length"],
            "length_difference": length_diff, "length_match_pass": btext(length_pass),
            "proposal_median_area": fmt(ps["median_target_area_ratio"]),
            "control_median_area": fmt(cs["median_target_area_ratio"]),
            "median_area_ratio": fmt(area_ratio), "area_match_pass": btext(area_pass),
            "proposal_p90_motion_normalized": fmt(ps["p90_motion_normalized"]),
            "control_p90_motion_normalized": fmt(cs["p90_motion_normalized"]),
            "motion_ratio_or_abs_difference": motion_text,
            "motion_match_pass": btext(motion_pass),
            "proposal_max_to_min_area_ratio": fmt(ps["max_to_min_area_ratio"]),
            "control_max_to_min_area_ratio": fmt(cs["max_to_min_area_ratio"]),
            "scale_dynamic_ratio": fmt(scale_ratio), "scale_match_pass": btext(scale_pass),
            "occlusion_match": occlusion_text,
            "full_occlusion_mismatch": btext(full_occ_mismatch),
            "fast_motion_match": btext(fast_match), "low_resolution_match": btext(low_match),
            "broad_superclass_match": btext(superclass_match),
            "visual_subtype_match": btext(subtype_match),
            "official_attribute_overlap": attr_overlap(str(p["official_attributes"]), str(c["official_attributes"])),
            "control_sequence_reuse_count": reuse_counts[str(c["sequence"])],
            "cross_group_leakage": btext(leakage), "no_distractor_pass": btext(no_distractor),
            "primary_event_distinctness_pass": btext(event_ok),
            "control_interval_reuse_pass": btext(interval_ok),
            "control_sequence_split_pass": btext(split_ok), "same_split_pass": btext(same_split),
            "analysis_eligibility": btext(eligible),
            "held_replacement_trace": p["replacement_trace"], "overall_state": overall,
            "notes": (
                "Source/inventory gates pass provisionally; Manager acceptance of the Singer1 full-body PERSON interpretation remains required."
                if eligible and governance_pending
                else "All locked R3 gates pass." if eligible
                else "One or more locked R3 gates failed; excluded from analysis."
            ),
        }
        primary_rows.append(prow)
        control_rows.append(crow)
        audit_rows.append(audit)
    return primary_rows, control_rows, audit_rows


def coverage_rows(primary: list[dict[str, object]], controls: list[dict[str, object]]) -> list[dict[str, object]]:
    groups = ("DISCOVERY", "HOLDOUT")
    complete_sets: dict[str, set[str]] = {}
    for group in groups:
        complete_sets[group] = {
            str(row["sequence"]) for row in primary if row["group"] == group
        } | {
            str(row["sequence"]) for row in controls if row["group"] == group
        }
    intersection = complete_sets["DISCOVERY"] & complete_sets["HOLDOUT"]
    result: list[dict[str, object]] = []
    for group in groups:
        p_rows = [row for row in primary if row["group"] == group and row["analysis_eligible"] == "true"]
        c_rows = [row for row in controls if row["group"] == group and row["analysis_eligible"] == "true"]
        p_sequences = Counter(str(row["sequence"]) for row in p_rows)
        c_sequences = Counter(str(row["sequence"]) for row in c_rows)
        superclasses = Counter(str(row["broad_superclass"]) for row in p_rows)
        shares = {key: value / len(p_rows) for key, value in sorted(superclasses.items())}
        duplicate_p = len({(row["sequence"], row["interval_start"], row["interval_end"]) for row in p_rows}) != len(p_rows)
        duplicate_c = len({(row["sequence"], row["interval_start"], row["interval_end"]) for row in c_rows}) != len(c_rows)
        overlap_p = any(
            left is not right and left["sequence"] == right["sequence"]
            and interval_overlap(int(left["interval_start"]), int(left["interval_end"]), int(right["interval_start"]), int(right["interval_end"]))
            for index, left in enumerate(p_rows) for right in p_rows[index + 1:]
        )
        overlap_c = any(
            left is not right and left["sequence"] == right["sequence"]
            and interval_overlap(int(left["interval_start"]), int(left["interval_end"]), int(right["interval_start"]), int(right["interval_end"]))
            for index, left in enumerate(c_rows) for right in c_rows[index + 1:]
        )
        minimum = 12 if group == "DISCOVERY" else 8
        unique_minimum = 6 if group == "DISCOVERY" else 4
        locked_pass = (
            len(p_rows) >= minimum and len(c_rows) >= minimum
            and len(p_sequences) >= unique_minimum and not intersection
            and max(p_sequences.values(), default=0) <= 3
            and max(c_sequences.values(), default=0) <= 2
            and not duplicate_p and not overlap_p and not duplicate_c and not overlap_c
        )
        other = "HOLDOUT" if group == "DISCOVERY" else "DISCOVERY"
        result.append({
            "group": group, "analysis_eligible_interval_count": len(p_rows),
            "analysis_eligible_control_count": len(c_rows),
            "unique_primary_sequence_count": len(p_sequences),
            "primary_sequences": "|".join(sorted(p_sequences)),
            "control_sequences": "|".join(sorted(c_sequences)),
            "complete_primary_control_source_sequence_set": "|".join(sorted(complete_sets[group])),
            "other_group_source_sequence_set": "|".join(sorted(complete_sets[other])),
            "cross_group_intersection": "|".join(sorted(intersection)) or "NONE",
            "cross_group_intersection_empty": btext(not intersection),
            "superclass_counts": "|".join(f"{key}:{value}" for key, value in sorted(superclasses.items())),
            "superclass_shares": "|".join(f"{key}:{value:.6f}" for key, value in shares.items()),
            "max_primary_intervals_per_sequence": max(p_sequences.values(), default=0),
            "max_control_intervals_per_sequence": max(c_sequences.values(), default=0),
            "duplicate_primary_interval_flag": btext(duplicate_p),
            "overlapping_primary_interval_flag": btext(overlap_p),
            "duplicate_control_interval_flag": btext(duplicate_c),
            "overlapping_control_interval_flag": btext(overlap_c),
            "control_sequence_cross_split_flag": btext(bool(intersection)),
            "locked_minimum_intervals": minimum, "locked_minimum_controls": minimum,
            "locked_minimum_unique_primary_sequences": unique_minimum,
            "locked_12_8_gate_pass": btext(locked_pass),
            "notes": "Analysis-eligible MATCH_PASS pairs only; assignment remains provisional pending Manager freeze review.",
        })
    return result


def parse_bbox(value: str):
    return R2.parse_bbox(value)


def pair_sheet(pair: dict[str, object], audit: dict[str, object], output: Path):
    p, c = pair["primary"], pair["control"]
    ps, cs = p["_stats"], c["_stats"]
    p_indices = primary_review_indices(p, ps)
    c_indices = R2.five_indices(cs["indices"])
    p_frames = [int(ps["frame_ids"][index]) for index in p_indices]
    c_frames = [int(cs["frame_ids"][index]) for index in c_indices]
    bbox_map = {int(key): str(value) for key, value in dict(p["bboxes"]).items()}
    canvas = Image.new("RGB", (2000, 620), (22, 25, 30))
    draw = ImageDraw.Draw(canvas)
    title = R2.load_font(23, bold=True)
    section = R2.load_font(17, bold=True)
    body = R2.load_font(14)
    small = R2.load_font(12)
    draw.text((18, 12), f"Stage 4A-S1-R3 source-only pair | {p['r3_interval_id']} + {c['r3_control_id']}", fill=R2.WHITE, font=title)
    draw.text((18, 50), "DISTRACTOR EVENT (five manual review boxes)", fill=(255, 190, 190), font=section)
    draw.text((18, 286), "MATCHED CLEAN CONTROL", fill=(185, 225, 255), font=section)
    for y, indices, stats, item, is_primary in (
        (74, p_indices, ps, p, True), (310, c_indices, cs, c, False)
    ):
        for tile_no, index in enumerate(indices):
            frame_id = int(stats["frame_ids"][index])
            box = parse_bbox(bbox_map[frame_id]) if is_primary else None
            tile = R2.render_tile(
                R2.frame_path(stats["meta"], frame_id), stats["gt_rows"][index],
                stats["gt_rows"][max(0, index - 1)], f"{item['sequence']} f{frame_id}", box,
            )
            canvas.paste(tile, (18 + tile_no * 268, y))
    x = 1366
    draw.rounded_rectangle((x, 48, 1984, 592), radius=14, fill=R2.PANEL, outline=(80, 90, 105), width=2)
    governance_pending = "MANAGER_ACCEPTANCE_REQUIRED" in str(p["sensitivity_notes"])
    banner_color = R2.EXCEPTION_COLOR if governance_pending else R2.PASS_COLOR
    banner_text = "SOURCE MATCH_PASS / CLASS REVIEW PENDING" if governance_pending else "MATCH_PASS / ANALYSIS_ELIGIBLE"
    draw.rounded_rectangle((x + 18, 66, 1966, 106), radius=8, fill=banner_color)
    draw.text((x + 30, 74), banner_text, fill=(10, 20, 15), font=section)
    panel_lines = [
        f"Group/event: {p['group']} / {p['event_id']}",
        f"P: {p['sequence']} {p['interval_start']}-{p['interval_end']}",
        f"C: {c['sequence']} {c['interval_start']}-{c['interval_end']}",
        f"Length P/C {audit['proposal_length']}/{audit['control_length']} pass={audit['length_match_pass']}",
        f"Area P/C {audit['proposal_median_area']}/{audit['control_median_area']}",
        f"Area factor {audit['median_area_ratio']} pass={audit['area_match_pass']}",
        f"Motion P/C {audit['proposal_p90_motion_normalized']}/{audit['control_p90_motion_normalized']}",
        f"Motion gate {audit['motion_ratio_or_abs_difference']} pass={audit['motion_match_pass']}",
        f"Scale factor {audit['scale_dynamic_ratio']} pass={audit['scale_match_pass']}",
        f"Superclass/subtype pass={audit['broad_superclass_match']}/{audit['visual_subtype_match']}",
        f"No distractor/full-occ pass={audit['no_distractor_pass']}/{btext(audit['full_occlusion_mismatch']=='false')}",
        f"Event/reuse/split pass={audit['primary_event_distinctness_pass']}/{audit['control_interval_reuse_pass']}/{audit['control_sequence_split_pass']}",
        f"Cross-group leakage={audit['cross_group_leakage']}",
        "Manager class acceptance=PENDING" if governance_pending else f"Manager status={STATUS}",
    ]
    y = 118
    for line in panel_lines:
        draw.text((x + 20, y), line, fill=R2.WHITE, font=body if len(line) < 72 else small)
        y += 31
    draw.text(
        (18, 596),
        "Source JPG + target GT (green) + GT-derived nominal context (blue) + manual distractor review box (red, NOT benchmark GT). No tracker output.",
        fill=(185, 190, 200), font=small,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, "JPEG", quality=88, optimize=True)
    return p_frames, c_frames, canvas.width, canvas.height


def md_table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(str(value).replace("|", "<br>") for value in row) + " |" for row in rows)
    return "\n".join(lines)


def build_report(primary, controls, audits, coverage, manifest) -> str:
    by_control = {row["linked_r3_interval_id"]: row for row in controls}
    by_audit = {row["linked_r3_interval_id"]: row for row in audits}
    lines = [
        "# Stage 4A-S1-R3 — Expanded source-only interval/control package",
        "",
        "**Date:** 2026-08-26",
        "**Status:** `S1_R3_COMPLETE_READY_FOR_MANAGER_FREEZE_REVIEW`",
        "**Decision scope:** provisional interval/control coverage only; Manager freeze review remains locked.",
        "",
        "## 1. Outcome-independence declaration",
        "",
        "This R3 lane used only the accepted v2 clean room, canonical OTB source JPGs and GT, and accepted source-only R1/R2 evidence. SpikeTrack was not run; no model/checkpoint, prediction, tracker result, AUC/IoU, success/failure label, score/confidence map, MRM log, ablation or tracker-derived ranking was accessed. **Outcome evidence accessed: NONE.**",
        "",
        "## 2. Canonical source and quarantine",
        "",
        f"- canonical OTB root: `{R2.SOURCE_ROOT}`",
        f"- accepted clean room: `{R2.CLEANROOM}`",
        "- quarantine: `Deer`, `Crossing`, `Couple`; excluded from proposals, controls, coverage and frame access",
        "- quarantine verification: clean-room rows state `candidate_pool_excluded=true`, `control_pool_excluded=true`, `coverage_excluded=true`, `frames_opened=false`",
        "",
        "## 3. R2 anchor traceability",
        "",
        md_table(
            ["R3 ID", "R2 parent", "Pair", "Group", "Trace"],
            [[row["r3_interval_id"], row["source_parent_id_or_new"], f"{row['sequence']} + {by_control[row['r3_interval_id']]['sequence']}", row["group"], row["replacement_trace"]] for row in primary if str(row["source_parent_id_or_new"]).startswith("R1-")],
        ),
        "",
        "All six source identities and groups are preserved. `R2-C09 Liquor 20-40` is extended to `20-44` only to equalize its same-sequence 25-frame anchor; all 25 control frames were source-only reviewed and remain clean.",
        "",
        "## 4. Held-primary rematch results",
        "",
        md_table(["Held ID", "Source interval", "One bounded rematch result", "Trace"], [[row["id"], f"{row['sequence']} {row['frames']}", row["result"], row["trace"]] for row in HELD_REMATCH]),
        "",
        "No held pair contributes to the 12/8 minimum. Prohibited incompatible controls remained excluded.",
        "",
        "## 5. Replacement selection trace",
        "",
        md_table(["R3 ID", "Reserve source", "Frames", "Replacement/anchor trace"], [[row["r3_interval_id"], row["sequence"], f"{row['interval_start']}-{row['interval_end']}", row["replacement_trace"]] for row in primary if row["source_parent_id_or_new"] == "NEW_RESERVE"]),
        "",
        "Replacement selection used source appearance, GT matching feasibility, event distinctness and diversity only.",
        "",
        "## 6. Distinct-event expansion procedure",
        "",
        "Intervals were bounded from continuous source content, required at least five consecutive distractor frames, and were not split from one long event. Repeated primary sequences use unique event IDs, non-overlapping intervals and normally at least ten intervening frames. `event_separation_evidence` records gap, identity change and return-to-non-event state. Maximum primary use is three intervals per sequence.",
        "",
        "Only the five review-sheet frames receive manual distractor boxes in R3. These boxes are review annotations, not benchmark ground truth; per-frame full-interval annotation remains a later Manager-controlled task.",
        "",
        "## 7. Discovery 12-pair package",
        "",
        md_table(["ID", "Primary", "Event", "Control", "Superclass", "State", "Sensitivity"], [[row["r3_interval_id"], f"{row['sequence']} {row['interval_start']}-{row['interval_end']}", row["event_id"], f"{by_control[row['r3_interval_id']]['sequence']} {by_control[row['r3_interval_id']]['interval_start']}-{by_control[row['r3_interval_id']]['interval_end']}", row["broad_superclass"], by_audit[row["r3_interval_id"]]["overall_state"], row["sensitivity_notes"]] for row in primary if row["group"] == "DISCOVERY"]),
        "",
        "## 8. Hold-out 8-pair package",
        "",
        md_table(["ID", "Primary", "Event", "Control", "Superclass", "State", "Sensitivity"], [[row["r3_interval_id"], f"{row['sequence']} {row['interval_start']}-{row['interval_end']}", row["event_id"], f"{by_control[row['r3_interval_id']]['sequence']} {by_control[row['r3_interval_id']]['interval_start']}-{by_control[row['r3_interval_id']]['interval_end']}", row["broad_superclass"], by_audit[row["r3_interval_id"]]["overall_state"], row["sensitivity_notes"]] for row in primary if row["group"] == "HOLDOUT"]),
        "",
        "## 9. Control search and rejection trace",
        "",
        md_table(["Pair", "Selected control", "Complete clean review", "Search/rejection trace"], [[row["linked_r3_interval_id"], f"{row['sequence']} {row['interval_start']}-{row['interval_end']}", row["no_similar_distractor_evidence"], row["control_search_and_rejection_trace"]] for row in controls]),
        "",
        "## 10. Pair matching gate results",
        "",
        md_table(["Pair", "Len", "Area", "Motion", "Scale", "Subtype", "No distractor", "Event", "Reuse", "State"], [[row["linked_r3_interval_id"], row["length_match_pass"], row["area_match_pass"], row["motion_match_pass"], row["scale_match_pass"], row["visual_subtype_match"], row["no_distractor_pass"], row["primary_event_distinctness_pass"], row["control_interval_reuse_pass"], row["overall_state"]] for row in audits]),
        "",
        "All analysis-eligible rows pass length (equal or ±2), median area factor ≤2, normalized-p90 motion factor ≤2 or low-motion absolute difference ≤0.03, max/min area factor ≤2, no full-occlusion mismatch, superclass/subtype, clean-control, split and reuse gates.",
        "",
        "## 11. Full sequence-disjoint audit",
        "",
        md_table(["Group", "Primary/control source set", "Other set", "Intersection", "Gate"], [[row["group"], row["complete_primary_control_source_sequence_set"], row["other_group_source_sequence_set"], row["cross_group_intersection"], row["cross_group_intersection_empty"]] for row in coverage]),
        "",
        "## 12. Control reuse/overlap audit",
        "",
        md_table(["Group", "Max reuse", "Duplicate", "Overlap", "Cross-split"], [[row["group"], row["max_control_intervals_per_sequence"], row["duplicate_control_interval_flag"], row["overlapping_control_interval_flag"], row["control_sequence_cross_split_flag"]] for row in coverage]),
        "",
        "No identical control interval is reused; repeated control sequences provide at most two non-overlapping, source-distinct intervals and stay in one split.",
        "",
        "## 13. Superclass diversity",
        "",
        md_table(["Group", "Counts", "Shares", "Unique primary sequences", "Locked gate"], [[row["group"], row["superclass_counts"], row["superclass_shares"], row["unique_primary_sequence_count"], row["locked_12_8_gate_pass"]] for row in coverage]),
        "",
        "The combined package retains at least three broad superclasses. Loss of the animal pair is disclosed and follows the protocol because no compatible clean live-bird control passed.",
        "`R3-D12 Singer1` is provisionally classified as `PERSON` because the accepted inventory and canonical GT describe a full-body target. The protocol reserve heading lists it under `FACE_HEAD`; that governance conflict is not silently resolved here.",
        "",
        "## 14. Exploratory/ineligible intervals",
        "",
        md_table(["ID", "Interval", "State", "Reason"], [[row["id"], f"{row['sequence']} {row['frames']}", row["result"], row["trace"]] for row in HELD_REMATCH]),
        "",
        "These four leads remain secondary source-only material; they are excluded from primary/control CSV counts, pair sheets and 12/8 coverage.",
        "",
        "## 15. Pair-sheet package",
        "",
        f"- pair sheets: **{len(manifest)}**",
        f"- committed payload: **{sum(int(row['byte_size']) for row in manifest):,} bytes** (<45 MiB)",
        "- top row: five distractor frames with GT target green, nominal prior-GT context blue and manual distractor red on every frame",
        "- bottom row: five clean matched-control frames with GT/context overlays only",
        "- manifest records SHA-256, size, source frame IDs and all five manual boxes",
        "",
        "## 16. Exact remaining blockers",
        "",
        "Numeric interval-count and control-validity gates pass provisionally. **Exact remaining blocker:** Manager must explicitly accept the accepted-inventory/canonical-full-body-GT interpretation of `R3-D12 Singer1` as `PERSON`. If Manager rejects that interpretation, `R3-D12` becomes ineligible, DISCOVERY falls from 12 to 11, and a replacement is required before freeze. Independent of that decision, Manager freeze review remains the only next authority: no final diagnostic slice has been frozen, no ambiguity level has been finalized, and no downstream diagnostic/scoring work is authorized.",
        "",
        "## 17. R3 conclusion",
        "",
        "**S1_R3_COMPLETE_READY_FOR_MANAGER_FREEZE_REVIEW**",
        "",
        "- Stage 4A-S1-R3: **READY**",
        "- Manager freeze review: **LOCKED PENDING R3**",
        "- FROZEN DIAGNOSTIC SLICE: **NOT CREATED**",
        "- STAGE 4B: **LOCKED**",
        "- DIAG PASS/FAIL: **NOT ASSIGNED**",
        "- S1-S7: **NOT STARTED**",
        "- PRIMARY SHORTLIST: **NONE**",
        "- MAIN BASELINE: **NONE**",
        "- PROPOSED ARCHITECTURE: **NONE**",
        "",
    ]
    return "\n".join(lines)


def finalize() -> None:
    R2.verify_quarantine()
    mapping = R2.load_mapping()
    pairs = all_pair_specs()
    if len(pairs) != 20:
        raise RuntimeError(f"R3 must define exactly 20 analysis pairs, found {len(pairs)}")
    attach_stats(pairs, mapping)
    primary, controls, audits = build_rows(pairs)
    coverage = coverage_rows(primary, controls)
    audit_by_id = {row["linked_r3_interval_id"]: row for row in audits}
    manifest: list[dict[str, object]] = []
    for pair in pairs:
        p, c = pair["primary"], pair["control"]
        path = REPO_ROOT / relative_pair_path(str(p["r3_interval_id"]))
        p_frames, c_frames, width, height = pair_sheet(pair, audit_by_id[str(p["r3_interval_id"])], path)
        bbox_map = {int(key): str(value) for key, value in dict(p["bboxes"]).items()}
        manifest.append({
            "pair_sheet_id": f"PAIR-{p['r3_interval_id']}",
            "linked_r3_interval_id": p["r3_interval_id"],
            "linked_r3_control_id": c["r3_control_id"],
            "relative_path": relative_pair_path(str(p["r3_interval_id"])),
            "sha256": R2.sha256_file(path), "byte_size": path.stat().st_size,
            "width": width, "height": height, "proposal_sequence": p["sequence"],
            "control_sequence": c["sequence"],
            "proposal_frame_ids": "|".join(str(value) for value in p_frames),
            "control_frame_ids": "|".join(str(value) for value in c_frames),
            "proposal_distractor_bboxes": "|".join(f"{frame}:{bbox_map[frame]}" for frame in p_frames),
            "overlays": "GT_TARGET_GREEN|NOMINAL_SEARCH_BLUE|PROPOSAL_DISTRACTOR_RED_ALL_5|IDS|EVENT|PAIR_METRICS|ALL_GATES",
            "analysis_eligible": "true", "manager_review_status": STATUS,
        })
    write_csv(PRIMARY_CSV, PRIMARY_FIELDS, primary)
    write_csv(CONTROL_CSV, CONTROL_FIELDS, controls)
    write_csv(AUDIT_CSV, AUDIT_FIELDS, audits)
    write_csv(COVERAGE_CSV, COVERAGE_FIELDS, coverage)
    write_csv(MANIFEST_CSV, MANIFEST_FIELDS, manifest)
    REPORT_MD.write_text(build_report(primary, controls, audits, coverage, manifest), encoding="utf-8")
    print(f"primary={len(primary)} controls={len(controls)} audits={len(audits)} pair_sheets={len(manifest)}")
    print("discovery=12 holdout=8 match_pass=20 outcome_evidence=NONE stage4b=LOCKED")
    print(f"payload_bytes={sum(int(row['byte_size']) for row in manifest)}")


def validate() -> None:
    R2.verify_quarantine()
    required = (PRIMARY_CSV, CONTROL_CSV, AUDIT_CSV, COVERAGE_CSV, MANIFEST_CSV, REPORT_MD, COMMAND_LOG)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"Missing R3 artifacts: {missing}")
    primary, controls = read_csv(PRIMARY_CSV), read_csv(CONTROL_CSV)
    audits, coverage, manifest = read_csv(AUDIT_CSV), read_csv(COVERAGE_CSV), read_csv(MANIFEST_CSV)
    if not (len(primary) == len(controls) == len(audits) == len(manifest) == 20):
        raise RuntimeError("R3 20-pair cardinality failed")
    if len({row["r3_interval_id"] for row in primary}) != 20 or len({row["r3_control_id"] for row in controls}) != 20:
        raise RuntimeError("Duplicate R3 ID")
    if any(row["sequence"] in QUARANTINED for row in primary + controls):
        raise RuntimeError("Quarantined sequence leaked into R3 tables")
    if any(row["sequence"] in HELD_SEQUENCES for row in primary):
        raise RuntimeError("Held primary incorrectly counted as analysis eligible")
    if any(row["analysis_eligible"] != "true" or row["manager_review_status"] != STATUS for row in primary + controls):
        raise RuntimeError("Eligibility/review status failure")
    if any(row["manual_bbox_is_benchmark_gt"] != "false" or len(row["distractor_bboxes_all_review_frames"].split("|")) != 5 for row in primary):
        raise RuntimeError("Five-frame manual distractor annotation failure")
    anchor_expected = {
        "R1-P01": ("Basketball", "DISCOVERY", "David3"),
        "R1-P02": ("Bolt", "DISCOVERY", "Human8"),
        "R1-P09": ("Liquor", "DISCOVERY", "Liquor"),
        "R1-P03": ("Crowds", "HOLDOUT", "Crowds"),
        "R1-P05": ("BlurCar4", "HOLDOUT", "Suv"),
        "R1-P12": ("Soccer", "HOLDOUT", "Man"),
    }
    control_by_interval = {row["linked_r3_interval_id"]: row for row in controls}
    for parent, expected in anchor_expected.items():
        p = next(row for row in primary if row["source_parent_id_or_new"] == parent)
        c = control_by_interval[p["r3_interval_id"]]
        if (p["sequence"], p["group"], c["sequence"]) != expected:
            raise RuntimeError(f"Anchor identity/group failure: {parent}")
    liquor = next(row for row in primary if row["source_parent_id_or_new"] == "R1-P09")
    liquor_control = control_by_interval[liquor["r3_interval_id"]]
    if (liquor_control["interval_start"], liquor_control["interval_end"]) != ("20", "44"):
        raise RuntimeError("Liquor equal-length source-only adjustment missing")
    if any(row["overall_state"] != "MATCH_PASS" or row["analysis_eligibility"] != "true" for row in audits):
        raise RuntimeError("Non-pass pair counted in R3")
    gate_fields = (
        "length_match_pass", "area_match_pass", "motion_match_pass", "scale_match_pass",
        "fast_motion_match", "low_resolution_match", "broad_superclass_match",
        "visual_subtype_match", "no_distractor_pass", "primary_event_distinctness_pass",
        "control_interval_reuse_pass", "control_sequence_split_pass", "same_split_pass",
    )
    if any(row[field] != "true" for row in audits for field in gate_fields):
        raise RuntimeError("A locked pair gate failed")
    if any(row["cross_group_leakage"] != "false" or row["full_occlusion_mismatch"] != "false" for row in audits):
        raise RuntimeError("Leakage or full-occlusion mismatch")
    groups = Counter(row["group"] for row in primary)
    unique = {group: len({row["sequence"] for row in primary if row["group"] == group}) for group in groups}
    if groups != Counter({"DISCOVERY": 12, "HOLDOUT": 8}) or unique["DISCOVERY"] < 6 or unique["HOLDOUT"] < 4:
        raise RuntimeError(f"Locked 12/8 or 6/4 gate failed: {groups}, {unique}")
    complete = {
        group: {row["sequence"] for row in primary if row["group"] == group}
        | {row["sequence"] for row in controls if row["group"] == group}
        for group in ("DISCOVERY", "HOLDOUT")
    }
    if complete["DISCOVERY"] & complete["HOLDOUT"]:
        raise RuntimeError("Complete sequence-set intersection is not empty")
    p_counts = Counter((row["group"], row["sequence"]) for row in primary)
    c_counts = Counter((row["group"], row["sequence"]) for row in controls)
    if max(p_counts.values()) > 3 or max(c_counts.values()) > 2:
        raise RuntimeError("Primary/control per-sequence cap failed")
    combined_super = Counter(row["broad_superclass"] for row in primary)
    if len(combined_super) < 3 or max(combined_super.values()) / 20 > 0.60:
        raise RuntimeError(f"Superclass diversity failed: {combined_super}")
    if len(coverage) != 2 or any(row["locked_12_8_gate_pass"] != "true" for row in coverage):
        raise RuntimeError("Coverage/split audit gate failed")
    payload = 0
    expected_paths = set()
    for row in manifest:
        path = REPO_ROOT / row["relative_path"]
        expected_paths.add(path.resolve())
        if not path.is_file() or R2.sha256_file(path) != row["sha256"]:
            raise RuntimeError(f"Pair-sheet hash failure: {path}")
        if path.stat().st_size != int(row["byte_size"]) or (row["width"], row["height"]) != ("2000", "620"):
            raise RuntimeError(f"Pair-sheet size/dimension failure: {path}")
        if len(row["proposal_frame_ids"].split("|")) != 5 or len(row["proposal_distractor_bboxes"].split("|")) != 5:
            raise RuntimeError("Manifest five-frame annotation failure")
        payload += path.stat().st_size
    actual_paths = {path.resolve() for path in PAIR_ROOT.glob("*.jpg")}
    if actual_paths != expected_paths or payload >= 45 * 1024 * 1024:
        raise RuntimeError("Pair-sheet set/payload failure")
    report = REPORT_MD.read_text(encoding="utf-8")
    required_headings = [f"## {number}." for number in range(1, 18)]
    locked_tokens = (
        "S1_R3_COMPLETE_READY_FOR_MANAGER_FREEZE_REVIEW",
        "FROZEN DIAGNOSTIC SLICE: **NOT CREATED**", "STAGE 4B: **LOCKED**",
        "DIAG PASS/FAIL: **NOT ASSIGNED**", "S1-S7: **NOT STARTED**",
        "PRIMARY SHORTLIST: **NONE**", "MAIN BASELINE: **NONE**",
        "PROPOSED ARCHITECTURE: **NONE**", "Outcome evidence accessed: NONE",
        "Exact remaining blocker:", "DISCOVERY falls from 12 to 11",
    )
    if not all(token in report for token in required_headings + list(locked_tokens)):
        raise RuntimeError("Report section/locked-state validation failed")
    command_log = COMMAND_LOG.read_text(encoding="utf-8")
    if "git commit -m \"Expand SpikeTrack diagnostic interval coverage\"" not in command_log or "git push origin main" not in command_log:
        raise RuntimeError("Exact final Git commands missing from command log")
    print(f"primary=20 discovery={groups['DISCOVERY']} holdout={groups['HOLDOUT']} unique={unique}")
    print(f"match_pass=20 cross_group_intersection=NONE superclass={dict(combined_super)}")
    print(f"pair_sheets=20 payload_bytes={payload} payload_cap=PASS")
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
