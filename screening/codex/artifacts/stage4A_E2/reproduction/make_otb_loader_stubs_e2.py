"""Create metadata-only stubs for the bounded Stage-4A-E2 OTB mini-root.

The pinned OTBDataset eagerly parses all 100 annotations before selecting a
requested sequence.  Only Deer, Crossing, and Couple may have real frames in
the E2 mini-root.  Six one-box rows keep even the Tiger1 initOmit=5 metadata
path parseable.  No tracker is imported or executed by this helper.
"""

import os
import sys
from pathlib import Path


SOURCE = Path(os.environ["SPIKETRACK_STAGE4A_E2_SOURCE_ROOT"])
ROOT = Path(os.environ["SPIKETRACK_STAGE4A_E2_OTB_ROOT"])
REAL = {"Deer", "Crossing", "Couple"}

sys.path.insert(0, str(SOURCE))
from lib.test.evaluation.otbdataset import OTBDataset  # noqa: E402


if not ROOT.is_dir():
    raise SystemExit(f"E2 mini-root does not exist: {ROOT}")

for item in OTBDataset.__new__(OTBDataset)._get_sequence_info_list():
    if item["name"] in REAL:
        continue
    annotation = ROOT / item["anno_path"]
    annotation.parent.mkdir(parents=True, exist_ok=True)
    if annotation.exists():
        raise SystemExit(f"Refusing to overwrite existing annotation: {annotation}")
    annotation.write_text("0,0,1,1\n" * 6, encoding="ascii", newline="\n")
