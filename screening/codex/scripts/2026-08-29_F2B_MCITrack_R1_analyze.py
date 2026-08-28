#!/usr/bin/env python3
"""Apply the unchanged locked metrics to the completed F2-B R1 run."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r1 = load_module("f2b_mcitrack_r1_runtime", SCRIPT_DIR / "2026-08-29_F2B_MCITrack_R1_runtime.py")
analyze = load_module("f2b_mcitrack_base_analyze", SCRIPT_DIR / "2026-08-29_F2B_MCITrack_analyze.py")
analyze.rt = r1
analyze.RESULTS_PATH = r1.RESEARCH_ROOT / "screening/codex/2026-08-29_F2B_MCITrack_R1_results.csv"
analyze.REPORT_PATH = r1.RESEARCH_ROOT / "screening/codex/2026-08-29_F2B_MCITrack_R1_execution_report.md"


if __name__ == "__main__":
    sys.exit(analyze.main())
