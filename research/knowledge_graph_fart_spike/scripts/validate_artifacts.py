#!/usr/bin/env python3
"""Fail-fast validation for Knowledge Graph V1 deliverables."""

from __future__ import annotations

import csv
import hashlib
import re
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "00_scope_and_method.md", "01_connected_papers_inventory.csv",
    "02_deduplicated_paper_inventory.csv", "03_solution_taxonomy.md",
    "04_high_relevance_paper_cards.md", "05_fartrack_architecture_and_principles.md",
    "06_spiketrack_architecture_and_bottlenecks.md", "07_transfer_matrix.csv",
    "08_spiketrack_redesign_space.md", "09_nodes.csv", "10_edges.csv",
    "11_knowledge_graph_v1.graphml", "12a_methodology_flow_v1_1.mmd",
    "12b_tracker_solution_knowledge_graph_v1_1.mmd", "13_teacher_report_v1.md",
    "14_evidence_log.csv", "15_canonical_metadata_audit_v1_1.csv",
    "16_neuroscience_collision_exclusion_v1_1.md", "README.md", "REVIEW_REQUEST.md",
]


def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    require(not missing, f"missing required files: {missing}")

    raw = rows("01_connected_papers_inventory.csv")
    papers = rows("02_deduplicated_paper_inventory.csv")
    audit = rows("15_canonical_metadata_audit_v1_1.csv")
    evidence = rows("14_evidence_log.csv")
    nodes = rows("09_nodes.csv")
    edges = rows("10_edges.csv")
    matrix = rows("07_transfer_matrix.csv")

    require(len(raw) == 82, f"raw count {len(raw)} != 82")
    raw_hash = hashlib.sha256((ROOT / "01_connected_papers_inventory.csv").read_bytes()).hexdigest().upper()
    require(raw_hash == "D29F22CA328BEDD033C9FC45CC80D430BD77165E1CB4544E5487454A9D3DACA6", "raw inventory changed")
    require(sum(r["source_graph"] == "FARTrack" for r in raw) == 41, "FARTrack raw count != 41")
    require(sum(r["source_graph"] == "SpikeTrack" for r in raw) == 41, "SpikeTrack raw count != 41")
    require(len(papers) == 74, f"unique count {len(papers)} != 74")
    require(sum(r["source_graph"] == "BOTH" for r in papers) == 7, "exact overlap count != 7")
    require(len({r["paper_id"] for r in papers}) == len(papers), "duplicate paper_id")
    require(len({re.sub(r"[^a-z0-9]", "", r["title"].casefold()) for r in papers}) == len(papers), "duplicate normalized title")
    for key in ("doi", "arxiv_id"):
        values = [r[key].casefold() for r in papers if r[key] not in {"", "UNKNOWN"}]
        require(len(values) == len(set(values)), f"duplicate {key}")

    statuses = {"peer-reviewed conference", "peer-reviewed journal", "accepted/online-first", "arXiv/preprint only", "unclear"}
    relevance = {"PRIMARY", "SUPPORTING", "HISTORICAL", "OUT_OF_SCOPE"}
    code_status = {"YES", "NO", "UNKNOWN"}
    require({r["publication_status"] for r in papers} <= statuses, "invalid publication status")
    require({r["visual_SOT_relevance"] for r in papers} <= relevance, "invalid relevance status")
    require({r["has_official_code"] for r in papers} <= code_status, "invalid code status")
    require(sum(r["visual_SOT_relevance"] == "PRIMARY" for r in papers) == 2, "anchor paper count != 2")
    require(sum(r["visual_SOT_relevance"] == "OUT_OF_SCOPE" for r in papers) == 1, "out-of-scope count != 1")
    require(len(audit) == 74 and {r["paper_id"] for r in audit} == {r["paper_id"] for r in papers}, "metadata audit coverage")
    tiers = {tier: sum(r["metadata_audit_tier"] == tier for r in papers) for tier in {
        "PRIMARY_VERIFIED_HIGH_RELEVANCE", "METADATA_CANONICALIZED", "ARXIV_ONLY_VERIFIED"
    }}
    require(tiers == {"PRIMARY_VERIFIED_HIGH_RELEVANCE": 14, "METADATA_CANONICALIZED": 56, "ARXIV_ONLY_VERIFIED": 4}, f"audit tiers {tiers}")
    require(all(r["metadata_source_url"].startswith("https://") for r in papers), "missing canonical metadata source")
    require(sum(r["publication_status"] == "peer-reviewed conference" for r in papers) == 38, "conference count")
    require(sum(r["publication_status"] == "peer-reviewed journal" for r in papers) == 32, "journal count")
    require(sum(r["publication_status"] == "arXiv/preprint only" for r in papers) == 4, "preprint count")
    require(not any(r["publication_status"] in {"accepted/online-first", "unclear"} for r in papers), "unresolved/online-first count")
    titles = {r["title"]: r for r in papers}
    require(titles["FARTrack: Fast Autoregressive Visual Tracking with High Performance"]["publication_status"] == "peer-reviewed conference", "FARTrack status")
    require(titles["SpikeTrack: A Spike-driven Framework for Efficient Visual Tracking"]["publication_status"] == "peer-reviewed conference", "SpikeTrack status")
    require(titles["Efficient and Accurate Low-Resolution Transformer Tracking"]["arxiv_id"] == "2405.17660", "LoReTrack merge missing")
    require("VideoTrack: Learning To Track Objects via Video Transformer" in titles, "VideoTrack not canonicalized")
    expected = {
        "Adaptively Bypassing Vision Transformer Blocks for Efficient Visual Tracking": ("2025", "Pattern Recognition 161, article 111278", "10.1016/j.patcog.2024.111278", "peer-reviewed journal"),
        "CATrack: Combining Convolutional and Attentional Methods for Visual Object Tracking": ("2023", "AINIT 2023", "10.1109/ainit59027.2023.10212501", "peer-reviewed conference"),
        "General Compression Framework for Efficient Transformer Object Tracking": ("2025", "ICCV 2025", "10.1109/iccv51701.2025.01247", "peer-reviewed conference"),
        "Exploring Enhanced Contextual Information for Video-Level Object Tracking": ("2025", "AAAI 2025", "10.1609/aaai.v39i4.32440", "peer-reviewed conference"),
        "LiteTrack: Layer Pruning with Asynchronous Feature Extraction for Lightweight and Efficient Visual Tracking": ("2024", "ICRA 2024", "10.1109/icra57147.2024.10610022", "peer-reviewed conference"),
        "GOT-Edit: Geometry-Aware Generic Object Tracking via Online Model Editing": ("2026", "ICLR 2026", "UNKNOWN", "peer-reviewed conference"),
        "Exploring Dynamic Transformer for Efficient Object Tracking": ("2025", "IEEE Transactions on Neural Networks and Learning Systems", "10.1109/tnnls.2025.3545752", "peer-reviewed journal"),
    }
    for title, values in expected.items():
        require(tuple(titles[title][key] for key in ("year", "venue", "doi", "publication_status")) == values, f"canonical correction failed: {title}")
    known_published = {
        "DeTrack: In-model Latent Denoising Learning for Visual Object Tracking",
        "Joint Feature Learning and Relation Modeling for Tracking: A One-Stream Framework",
        "HIPTrack: Visual Tracking with Historical Prompts",
        "RELO: Reinforcement Learning to Localize for Visual Object Tracking",
        "UETrack: A Unified and Efficient Framework for Single Object Tracking",
        "ZoomTrack: Target-aware Non-uniform Resizing for Efficient Visual Tracking",
    }
    require(all(titles[t]["publication_status"] != "arXiv/preprint only" for t in known_published), "known publication labeled preprint-only")

    evidence_ids = {r["evidence_id"] for r in evidence}
    require(len(evidence_ids) == len(evidence), "duplicate evidence id")
    require(evidence_ids == {f"E{i:02d}" for i in range(1, 29)}, "evidence log must be E01-E28")
    for record in papers + nodes + edges + matrix:
        for value in record.values():
            for item in re.findall(r"E\d{2}", value or ""):
                require(item in evidence_ids, f"unresolved evidence id {item}")
    for path in ROOT.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for item in re.findall(r"E\d{2}", text):
            require(item in evidence_ids, f"{path.name}: unresolved evidence id {item}")

    component_columns = [
        "template_backbone", "search_backbone", "stage_block_depth", "channel_width", "timestep",
        "template_memory", "MRM", "MRM_count", "MRM_dimensions", "search_memory_interaction",
        "prediction_head", "loss_training", "runtime_export_structure", "input_resolution",
    ]
    allowed = {"NONE", "POSSIBLE", "PROMISING", "INCOMPATIBLE"}
    promising: list[str] = []
    for row in matrix:
        for column in component_columns:
            require(row[column] in allowed, f"invalid matrix value {row[column]} at {row['donor_id']}/{column}")
            if row[column] == "PROMISING":
                require(row["promising_ids"], f"PROMISING cell without ID at {row['donor_id']}/{column}")
        promising.extend([p for p in row["promising_ids"].split(";") if p])
    require(len(promising) == len(set(promising)) == 10, "promising IDs must be unique P01-P10")
    require(set(promising) == {f"P{i:02d}" for i in range(1, 11)}, "promising ID set mismatch")
    redesign = (ROOT / "08_spiketrack_redesign_space.md").read_text(encoding="utf-8")
    for item in promising:
        require(len(re.findall(rf"^### {item}\b", redesign, flags=re.MULTILINE)) == 1, f"{item} explanation missing/duplicated")
        section = re.search(rf"^### {item}\b(.*?)(?=^### P\d{{2}}\b|^## Independent)", redesign, flags=re.MULTILINE | re.DOTALL)
        require(section is not None and all(f"{n}. **" in section.group(1) for n in range(1, 9)), f"{item} lacks eight-part explanation")

    node_ids = {r["node_id"] for r in nodes}
    require(len(node_ids) == len(nodes), "duplicate node id")
    require({"A_FAR", "A_SPIKE"} <= node_ids, "anchor nodes absent")
    require(all(e["source"] in node_ids and e["target"] in node_ids for e in edges), "edge references missing node")
    require({e["confidence"] for e in edges} <= {"HIGH", "MEDIUM", "LOW"}, "invalid edge confidence")
    membership = [e for e in edges if e["edge_type"] == "contains_export_entry"]
    require(len(membership) == 81, f"neighborhood membership edges {len(membership)} != 81")

    tree = ET.parse(ROOT / "11_knowledge_graph_v1.graphml")
    ns = {"g": "http://graphml.graphdrawing.org/xmlns"}
    require(len(tree.findall(".//g:node", ns)) == len(nodes), "GraphML node count mismatch")
    require(len(tree.findall(".//g:edge", ns)) == len(edges), "GraphML edge count mismatch")
    paper_nodes = {r["node_id"]: r for r in nodes if r["node_type"] == "PAPER" and r["node_id"].startswith("P_P")}
    for paper in papers:
        node = paper_nodes["P_" + paper["paper_id"]]
        require(node["label"] == paper["title"], f"node title mismatch {paper['paper_id']}")
        require(node["publication_status"] == paper["publication_status"], f"node status mismatch {paper['paper_id']}")
        require(node["description"].startswith(paper["year"] + " | "), f"node year mismatch {paper['paper_id']}")

    methodology = (ROOT / "12a_methodology_flow_v1_1.mmd").read_text(encoding="utf-8")
    curated = (ROOT / "12b_tracker_solution_knowledge_graph_v1_1.mmd").read_text(encoding="utf-8")
    require("methodology_flow" in methodology and "74 deduplicated paper identities" in methodology, "methodology flow labeling")
    for label in ("FARTrack", "SpikeTrack", "CompressTracker", "MixFormerV2", "AsymTrack", "LiteTrack", "LoReTrack", "DyTrack", "ARPTrack", "HiT", "CPDATrack", "SpikeFET", "STDTrack", "static structural compression", "task-specific knowledge preservation", "dynamic computation"):
        require(label in curated, f"curated graph reference missing: {label}")

    corpus = "\n".join((ROOT / name).read_text(encoding="utf-8", errors="replace") for name in REQUIRED if name.endswith((".md", ".mmd")))
    require("We are no longer searching for a third main tracker" in corpus, "locked two-anchor statement missing")
    require("DIAG_FAIL" in corpus and "consumed" in corpus, "historical null-result boundary missing")
    require("KNOWLEDGE_GRAPH_V1_1_READY_FOR_MANAGER_REVIEW" in corpus, "terminal state missing")
    require("MANAGER_VERIFIED_EXTERNAL_EXCLUSION" in corpus and "41 records" in corpus, "external exclusion provenance missing")
    require("74 verified unique papers" not in corpus, "overclaiming inventory wording remains")
    require("third main tracker" in corpus and "No final SpikeTrack architecture has been selected" in corpus, "scope boundary missing")
    require("whole-MRM1" in corpus and "DIAG_FAIL" in corpus, "MRM1 boundary missing")
    require("FINAL_SPIKETRACK_ARCHITECTURE_SELECTED" not in corpus, "forbidden terminal state present")
    print(
        "VALIDATION_OK "
        f"raw={len(raw)} unique={len(papers)} nodes={len(nodes)} edges={len(edges)} "
        f"evidence={len(evidence)} promising={len(promising)} unresolved=0"
    )


if __name__ == "__main__":
    main()
