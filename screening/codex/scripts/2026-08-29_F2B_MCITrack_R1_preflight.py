#!/usr/bin/env python3
"""Final F2-B R1 preflight with the authorized restricted OTB adapter."""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
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
preflight = load_module("f2b_mcitrack_base_preflight", SCRIPT_DIR / "2026-08-29_F2B_MCITrack_preflight.py")
preflight.ARTIFACT_ROOT = r1.ARTIFACT_ROOT
preflight.bootstrap_official = r1.bootstrap_official

FINAL_UNBLOCK_STARTED_UTC = datetime.fromisoformat("2026-08-28T19:05:00+00:00")
FINAL_UNBLOCK_DEADLINE_UTC = FINAL_UNBLOCK_STARTED_UTC.replace(minute=50)


def main() -> int:
    result_code = preflight.main()
    result_path = r1.ARTIFACT_ROOT / "preflight.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    completed = datetime.now(timezone.utc)
    result["final_unblock_started_utc"] = FINAL_UNBLOCK_STARTED_UTC.isoformat()
    result["final_unblock_deadline_utc"] = FINAL_UNBLOCK_DEADLINE_UTC.isoformat()
    result["technical_unblock_wall_seconds"] = (completed - FINAL_UNBLOCK_STARTED_UTC).total_seconds()
    result["within_45_minute_unblock_cap"] = completed <= FINAL_UNBLOCK_DEADLINE_UTC
    if not result["within_45_minute_unblock_cap"]:
        result["status"] = "FAIL"
        result["error_type"] = "TechnicalUnblockWallTimeExceeded"
        result["error"] = "Final technical-unblock wall time exceeded 45 minutes before scientific execution"
        result_code = 2
    r1.write_json(result_path, result)
    print(
        f"R1_PRECHECK_STATUS={result['status']} WITHIN_45_MIN={result['within_45_minute_unblock_cap']}",
        flush=True,
    )
    return result_code


if __name__ == "__main__":
    sys.exit(main())
