"""Create metadata-only stubs required by the pinned eager OTB loader.

Only Deer, Crossing, and Couple contain real frames/annotations. The official
OTBDataset eagerly parses all 100 annotation paths before name selection, so
one-row stubs permit the unmodified loader to reach the predeclared sequence.
The stubs are never tracked and are kept outside the Q1 repository.
"""

from pathlib import Path
import sys


SOURCE = Path(r"E:\Robot_Backup\tmp\stage4A_R_official_source")
ROOT = Path(r"E:\Robot_Backup\tmp\stage4A_R_otb3")
REAL = {"Deer", "Crossing", "Couple"}

sys.path.insert(0, str(SOURCE))
from lib.test.evaluation.otbdataset import OTBDataset


for item in OTBDataset.__new__(OTBDataset)._get_sequence_info_list():
    if item["name"] in REAL:
        continue
    annotation = ROOT / item["anno_path"]
    annotation.parent.mkdir(parents=True, exist_ok=True)
    annotation.write_text("0,0,1,1\n" * 6, encoding="ascii")
