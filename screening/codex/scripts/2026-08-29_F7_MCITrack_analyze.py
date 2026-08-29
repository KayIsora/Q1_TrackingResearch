#!/usr/bin/env python3
"""Apply only the locked F7/F2-B metrics, bootstrap, and six positive gates."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

import numpy as np


RUNTIME_PATH = Path(__file__).with_name("2026-08-29_F7_MCITrack_runtime.py")
RUNTIME_SPEC = importlib.util.spec_from_file_location("f7_mcitrack_runtime", RUNTIME_PATH)
if RUNTIME_SPEC is None or RUNTIME_SPEC.loader is None:
    raise RuntimeError(f"Unable to load runtime module: {RUNTIME_PATH}")
rt = importlib.util.module_from_spec(RUNTIME_SPEC)
RUNTIME_SPEC.loader.exec_module(rt)

RESULTS_PATH = rt.RESEARCH_ROOT / "screening/codex/2026-08-29_F7_MCITrack_results.csv"
REPORT_PATH = rt.RESEARCH_ROOT / "screening/codex/2026-08-29_F7_MCITrack_execution_report.md"


def mean(rows: Iterable[Dict[str, Any]], field: str) -> float:
    return float(np.mean([float(row[field]) for row in rows]))


def sign(value: float) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def summarize_rows(rows: List[Dict[str, Any]]) -> Dict[str, float]:
    primary = [row for row in rows if row["condition"] == "primary"]
    control = [row for row in rows if row["condition"] == "control"]
    return {
        "baseline_iou_primary": mean(primary, "baseline_iou"),
        "baseline_iou_control": mean(control, "baseline_iou"),
        "baseline_weakness": mean(control, "baseline_iou") - mean(primary, "baseline_iou"),
        "zero_contribution_primary": mean(primary, "zero_contribution"),
        "zero_contribution_control": mean(control, "zero_contribution"),
        "zero_interaction": mean(primary, "zero_contribution") - mean(control, "zero_contribution"),
        "stale_contribution_primary": mean(primary, "stale_contribution"),
        "stale_contribution_control": mean(control, "stale_contribution"),
        "stale_interaction": mean(primary, "stale_contribution") - mean(control, "stale_contribution"),
    }


def bootstrap(rows_by_pair: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, float]]:
    rng = np.random.default_rng(rt.SEED)
    pair_ids = [pair["pair_id"] for pair in rt.PAIR_SPECS]
    samples: Dict[str, List[float]] = defaultdict(list)
    for _ in range(10_000):
        selected = rng.choice(pair_ids, size=len(pair_ids), replace=True)
        sampled_rows: List[Dict[str, Any]] = []
        for pair_id in selected:
            sampled_rows.extend(rows_by_pair[str(pair_id)])
        summary = summarize_rows(sampled_rows)
        for key in (
            "baseline_weakness", "zero_contribution_primary", "zero_interaction",
            "stale_contribution_primary", "stale_interaction",
        ):
            samples[key].append(summary[key])
    return {
        key: {
            "p2_5": float(np.percentile(values, 2.5)),
            "p50": float(np.percentile(values, 50.0)),
            "p97_5": float(np.percentile(values, 97.5)),
        }
        for key, values in samples.items()
    }


def intervention_gates(
    label: str,
    complete: Dict[str, float],
    pair_summaries: List[Dict[str, Any]],
    call_parity: bool,
) -> Dict[str, Any]:
    prefix = "zero" if label == "ZERO_STATE" else "stale"
    interaction = complete[f"{prefix}_interaction"]
    primary = complete[f"{prefix}_contribution_primary"]
    interaction_sign = sign(interaction)
    pair_consistency = sum(
        sign(float(pair[f"{prefix}_interaction"])) == interaction_sign for pair in pair_summaries
    )
    primary_threshold_count = sum(
        abs(float(pair[f"{prefix}_contribution_primary"])) >= 0.01
        and sign(float(pair[f"{prefix}_contribution_primary"])) == interaction_sign
        for pair in pair_summaries
    )
    gates = {
        "gate_1_baseline_weakness": complete["baseline_weakness"] >= 0.03,
        "gate_2_abs_interaction": abs(interaction) >= 0.02,
        "gate_3_abs_primary_contribution": abs(primary) >= 0.02,
        "gate_4_pair_sign_consistency": pair_consistency >= 4,
        "gate_5_primary_sequence_threshold": primary_threshold_count >= 4,
        "gate_6_call_parity": call_parity,
    }
    return {
        "label": label,
        "interaction": interaction,
        "primary_contribution": primary,
        "pair_sign_consistency": pair_consistency,
        "primary_sequence_threshold_count": primary_threshold_count,
        "gates": gates,
        "passes": all(gates.values()),
    }


def bool_cell(value: Any) -> str:
    return "PASS" if bool(value) else "FAIL"


def fmt(value: float) -> str:
    return f"{value:.9f}"


def main() -> int:
    rt.enforce_deadline()
    status = json.loads((rt.ARTIFACT_ROOT / "execution_status.json").read_text(encoding="utf-8"))
    preflight = json.loads((rt.ARTIFACT_ROOT / "preflight.json").read_text(encoding="utf-8"))
    if status.get("status") != "COMPLETE":
        raise RuntimeError("Locked analysis is permitted only after a complete 254-row execution")

    with (rt.ARTIFACT_ROOT / "per_frame_results.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 254:
        raise RuntimeError(f"Expected 254 per-frame rows, found {len(rows)}")
    if len({row["sequence"] for row in rows}) != 6:
        raise RuntimeError("Expected exactly six executed sequences")
    if not all(row["call_parity"].lower() == "true" for row in rows):
        raise RuntimeError("Call parity is not true on every scientific row")

    rows_by_pair: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        rows_by_pair[row["pair_id"]].append(row)
    pair_summaries: List[Dict[str, Any]] = []
    for pair in rt.PAIR_SPECS:
        summary = summarize_rows(rows_by_pair[pair["pair_id"]])
        summary.update({
            "row_type": "PAIR",
            "pair_id": pair["pair_id"],
            "sequence": pair["sequence"],
            "evaluated_rows": len(rows_by_pair[pair["pair_id"]]),
        })
        pair_summaries.append(summary)

    complete = summarize_rows(rows)
    zero = intervention_gates("ZERO_STATE", complete, pair_summaries, True)
    stale = intervention_gates("STALE_STATE", complete, pair_summaries, True)
    passing = [item for item in (zero, stale) if item["passes"]]
    if passing:
        passing_intervention = sorted(
            passing,
            key=lambda item: (-abs(float(item["interaction"])), 0 if item["label"] == "ZERO_STATE" else 1),
        )[0]["label"]
        mini_probe_result = "PROBE_POSITIVE_GAP_EVIDENCE"
    else:
        passing_intervention = "NONE"
        mini_probe_result = "PROBE_NEGATIVE_REJECT_CURRENT_GAP"

    bootstrap_ci = bootstrap(rows_by_pair)
    rt.write_json(rt.ARTIFACT_ROOT / "bootstrap_10000_seed_20260829.json", bootstrap_ci)
    analysis = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "complete_set": complete,
        "pair_summaries": pair_summaries,
        "zero_state_gate": zero,
        "stale_state_gate": stale,
        "passing_intervention": passing_intervention,
        "mini_probe_result": mini_probe_result,
        "bootstrap": bootstrap_ci,
    }
    rt.write_json(rt.ARTIFACT_ROOT / "analysis_summary.json", analysis)
    rt.write_json(rt.EXTERNAL_RESULTS_ROOT / "analysis_summary.json", analysis)

    result_fields = [
        "row_type", "pair_id", "sequence", "evaluated_rows",
        "baseline_iou_primary", "baseline_iou_control", "baseline_weakness",
        "zero_contribution_primary", "zero_contribution_control", "zero_interaction",
        "stale_contribution_primary", "stale_contribution_control", "stale_interaction",
        "zero_pair_sign_consistency", "stale_pair_sign_consistency",
        "zero_primary_abs_threshold_count", "stale_primary_abs_threshold_count",
        "zero_gate_result", "stale_gate_result", "passing_intervention", "mini_probe_result",
    ]
    with RESULTS_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=result_fields)
        writer.writeheader()
        for summary in pair_summaries:
            writer.writerow({key: summary.get(key, "") for key in result_fields})
        complete_row = {
            "row_type": "COMPLETE_SET",
            "pair_id": "ALL_6_PAIRS",
            "sequence": "ALL_6_SEQUENCES",
            "evaluated_rows": 254,
            **complete,
            "zero_pair_sign_consistency": zero["pair_sign_consistency"],
            "stale_pair_sign_consistency": stale["pair_sign_consistency"],
            "zero_primary_abs_threshold_count": zero["primary_sequence_threshold_count"],
            "stale_primary_abs_threshold_count": stale["primary_sequence_threshold_count"],
            "zero_gate_result": bool_cell(zero["passes"]),
            "stale_gate_result": bool_cell(stale["passes"]),
            "passing_intervention": passing_intervention,
            "mini_probe_result": mini_probe_result,
        }
        writer.writerow({key: complete_row.get(key, "") for key in result_fields})

    state_lines = [
        f"- `{state['identity']}`: shape `{state['shape']}`, dtype `{state['dtype']}`, device `{state['device']}`, finite `{state['finite']}`."
        for state in preflight["state_contract"].values()
    ]
    pair_table = "\n".join(
        "| {pair_id} | {sequence} | {baseline_weakness:.6f} | {zero_contribution_primary:.6f} | {zero_interaction:.6f} | {stale_contribution_primary:.6f} | {stale_interaction:.6f} |".format(**pair)
        for pair in pair_summaries
    )
    zero_gates = "\n".join(f"- {name}: **{bool_cell(value)}**" for name, value in zero["gates"].items())
    stale_gates = "\n".join(f"- {name}: **{bool_cell(value)}**" for name, value in stale["gates"].items())
    contract = preflight["contract"]
    runtime = preflight["runtime"]
    report = f"""# F7 — MCITrack resource-sealed re-entry and unchanged mini-probe

**Date:** 2026-08-29

**Protocol:** `screening/manager/2026-08-29_F7_MCITrack_resource_reentry_protocol.md`

**Status:** `{mini_probe_result}`

## Boundary

This report covers one authorized download, the locked technical preflight, and one execution of the unchanged six-pair mini-probe. No package was installed; no other asset or dataset was downloaded; no source, model, data, interval, intervention, metric, threshold, hypothesis, or benchmark was changed. HG6 and all later stages remain unopened.

## Official bootstrap seal

- Google Drive file ID: `{rt.EXPECTED_BOOTSTRAP_FILE_ID}`; folder ID: `{rt.EXPECTED_BOOTSTRAP_FOLDER_ID}`.
- Display name: `fast_itpn_base_clipl_e1600.pt`.
- External path: `{contract['bootstrap_external_path']}`.
- Byte count: `{contract['bootstrap_external_bytes']}`.
- SHA-256: `{contract['bootstrap_external_sha256']}`.
- Config-required copy: `{contract['bootstrap_required_path']}`; byte/hash equality: `{contract['bootstrap_copy_exact']}`.
- Total asset downloads in F7: `1`.

## Provenance and technical preflight

- Official source: `kangben258/MCITrack` at `{contract['source_sha']}`; source worktree clean: `{contract['source_clean']}`.
- Config: `{contract['config_path']}`; SHA-256 `{contract['config_sha256']}`; pinned Git-blob match: `{contract['config_hash_matches_pinned_blob']}`.
- Full checkpoint: `{contract['checkpoint_path']}`; byte count `{contract['checkpoint_bytes']}`; SHA-256 `{contract['checkpoint_sha256']}`.
- Official Fast-iTPN bootstrap bypassed: `{runtime['pretrained_bootstrap_bypassed']}`.
- Full checkpoint strict-load: `{runtime['strict_checkpoint_load']}` (`{runtime['strict_load_source_line']}`).
- Official evaluator/dataset: `{runtime['official_evaluator_class']}` / `{runtime['official_dataset_class']}`.
- Runtime: PyTorch `{runtime['torch_version']}`, device `{runtime['model_parameter_device']}` (`{runtime['cuda_device']}`).
- Diagnostics-disabled max absolute bbox/score difference: `{preflight['diagnostics_disabled']['max_abs']}`; continuation exact: `{preflight['diagnostics_disabled']['continuation_equal']}`.
- Snapshot/restore max absolute bbox/score difference: `{preflight['snapshot_restore']['bbox_score_max_abs']}`; continuation exact: `{preflight['snapshot_restore']['continuation_exact']}`.
- State-copy no-op max absolute bbox/score difference: `{preflight['state_copy_noop']['bbox_score_max_abs']}`.
- Five-template parity: `{bool_cell(preflight['gates']['five_template_parity'])}`; current-compute parity: `{bool_cell(preflight['gates']['current_compute_call_parity'])}`.

### Four carried states

{chr(10).join(state_lines)}

## Locked execution

- Sequences: exactly 6 (`Liquor`, `Car4`, `Crowds`, `Girl`, `Human3`, `Suv`).
- Evaluated primary/control rows: exactly 254.
- Branch order: released baseline, all-zero carried states, stale interval-start states.
- All three branches used the identical pre-frame tracker/template/state/RNG snapshot and frame; only baseline continuation was committed.
- Model execution time: `{status['model_execution_seconds']:.3f}` seconds.
- Scientific executions: `1`; call parity passed on all rows.
- F7 completed before the four-hour deadline `{rt.F7_DEADLINE_UTC.isoformat()}`.

## Pair results

| Pair | Sequence | Baseline weakness | Zero primary contribution | Zero interaction | Stale primary contribution | Stale interaction |
|---|---|---:|---:|---:|---:|---:|
{pair_table}

## Complete-set locked estimates

- Baseline weakness: `{fmt(complete['baseline_weakness'])}`.
- Zero-state primary contribution: `{fmt(complete['zero_contribution_primary'])}`.
- Zero-state interaction: `{fmt(complete['zero_interaction'])}`.
- Zero-state pair-sign consistency: `{zero['pair_sign_consistency']} / 6`.
- Zero-state primary-sequence threshold count: `{zero['primary_sequence_threshold_count']} / 6`.
- Stale-state primary contribution: `{fmt(complete['stale_contribution_primary'])}`.
- Stale-state interaction: `{fmt(complete['stale_interaction'])}`.
- Stale-state pair-sign consistency: `{stale['pair_sign_consistency']} / 6`.
- Stale-state primary-sequence threshold count: `{stale['primary_sequence_threshold_count']} / 6`.

The pair-clustered bootstrap used 10,000 resamples and seed `20260829`; intervals are descriptive only.

### ZERO_STATE gates

{zero_gates}

### STALE_STATE gates

{stale_gates}

## Decision

- Passing intervention: **{passing_intervention}**.
- Mini-probe result: **{mini_probe_result}**.

A positive result authorizes only Manager consideration of a fast mechanism-level HG6 audit. It does not make MCITrack GAP_READY, shortlisted, or selected. A negative result is terminal for the current state-coupling gap.

## Locked downstream state

- HG6: **NOT STARTED**
- S1-S7: **NOT STARTED**
- PRIMARY SHORTLIST: **NONE**
- MAIN BASELINE: **NONE**
- PROPOSED ARCHITECTURE: **NONE**

STOP.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    rt.enforce_deadline()
    print(f"ANALYSIS_STATUS=COMPLETE RESULT={mini_probe_result} PASSING={passing_intervention} REPORT={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
