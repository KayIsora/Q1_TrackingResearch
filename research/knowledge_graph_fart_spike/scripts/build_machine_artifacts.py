#!/usr/bin/env python3
"""Build the final inventory and semantic graph from the preserved BibTeX parse.

Connected Papers provenance is represented only by neighborhood-membership
edges.  Semantic edges below are explicitly project-derived and carry evidence
and confidence; no Connected Papers topology is reconstructed.
"""

from __future__ import annotations

import csv
import re
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "provenance" / "02_deduplicated_paper_inventory_draft.csv"


STATUS_OVERRIDES = {
    "FARTrack: Fast Autoregressive Visual Tracking with High Performance": "peer-reviewed conference",
    "SpikeTrack: A Spike-driven Framework for Efficient Visual Tracking": "peer-reviewed conference",
    "Two-stream Beats One-stream: Asymmetric Siamese Network for Efficient Visual Tracking": "peer-reviewed conference",
    "General Compression Framework for Efficient Transformer Object Tracking": "peer-reviewed conference",
    "MixFormerV2: Efficient Fully Transformer Tracking": "peer-reviewed conference",
    "LiteTrack: Layer Pruning with Asynchronous Feature Extraction for Lightweight and Efficient Visual Tracking": "peer-reviewed conference",
    "Exploring Dynamic Transformer for Efficient Object Tracking": "peer-reviewed journal",
    "Exploring Efficient and Effective Sequence Learning for Visual Object Tracking": "peer-reviewed conference",
    "Exploring Enhanced Contextual Information for Video-Level Object Tracking": "peer-reviewed conference",
    "Autoregressive Sequential Pretraining for Visual Tracking": "peer-reviewed conference",
    "Exploring Lightweight Hierarchical Vision Transformers for Efficient Visual Tracking": "peer-reviewed conference",
    "Context-Aware Token Pruning and Discriminative Selective Attention for Transformer Tracking": "peer-reviewed journal",
    "Fully Spiking Neural Networks for Unified Frame-Event Object Tracking": "peer-reviewed conference",
    "Optimizing intrinsic representation for tracking": "peer-reviewed journal",
}

CODE_OVERRIDES = {
    "FARTrack: Fast Autoregressive Visual Tracking with High Performance": ("YES", "https://github.com/MIV-XJTU/FARTrack"),
    "SpikeTrack: A Spike-driven Framework for Efficient Visual Tracking": ("YES", "https://github.com/faicaiwawa/SpikeTrack"),
    "Two-stream Beats One-stream: Asymmetric Siamese Network for Efficient Visual Tracking": ("YES", "https://github.com/jiawen-zhu/AsymTrack"),
    "General Compression Framework for Efficient Transformer Object Tracking": ("YES", "https://github.com/LingyiHongfd/CompressTracker"),
    "MixFormerV2: Efficient Fully Transformer Tracking": ("YES", "https://github.com/MCG-NJU/MixFormerV2"),
    "LiteTrack: Layer Pruning with Asynchronous Feature Extraction for Lightweight and Efficient Visual Tracking": ("YES", "https://github.com/TsingWei/LiteTrack"),
    "Exploring Dynamic Transformer for Efficient Object Tracking": ("UNKNOWN", "UNKNOWN"),
    "Exploring Efficient and Effective Sequence Learning for Visual Object Tracking": ("NO", "UNKNOWN"),
    "Efficient and Accurate Low-Resolution Transformer Tracking": ("YES", "https://github.com/ShaohuaDong2021/LoReTrack"),
    "Exploring Enhanced Contextual Information for Video-Level Object Tracking": ("YES", "https://github.com/kangben258/MCITrack"),
    "Autoregressive Sequential Pretraining for Visual Tracking": ("NO", "UNKNOWN"),
    "Exploring Lightweight Hierarchical Vision Transformers for Efficient Visual Tracking": ("YES", "https://github.com/kangben258/HiT"),
    "Context-Aware Token Pruning and Discriminative Selective Attention for Transformer Tracking": ("YES", "https://github.com/JananiKugaa/CPDATrack"),
    "Fully Spiking Neural Networks for Unified Frame-Event Object Tracking": ("YES", "https://github.com/Noctis-A/SpikeFET"),
}

URL_OVERRIDES = {
    "FARTrack: Fast Autoregressive Visual Tracking with High Performance": "https://openreview.net/forum?id=lq7Zfr8kAS",
    "SpikeTrack: A Spike-driven Framework for Efficient Visual Tracking": "https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_SpikeTrack_A_Spike-driven_Framework_for_Efficient_Visual_Tracking_CVPR_2026_paper.html",
    "Two-stream Beats One-stream: Asymmetric Siamese Network for Efficient Visual Tracking": "https://ojs.aaai.org/index.php/AAAI/article/view/33191",
    "General Compression Framework for Efficient Transformer Object Tracking": "https://openaccess.thecvf.com/content/ICCV2025/html/Hong_General_Compression_Framework_for_Efficient_Transformer_Object_Tracking_ICCV_2025_paper.html",
    "MixFormerV2: Efficient Fully Transformer Tracking": "https://proceedings.neurips.cc/paper_files/paper/2023/hash/b7870bd43b2d133a1ed95582ae5d82a4-Abstract.html",
    "LiteTrack: Layer Pruning with Asynchronous Feature Extraction for Lightweight and Efficient Visual Tracking": "https://ieeexplore.ieee.org/document/10610022/",
    "Exploring Dynamic Transformer for Efficient Object Tracking": "https://doi.org/10.1109/TNNLS.2025.3545752",
    "Exploring Efficient and Effective Sequence Learning for Visual Object Tracking": "https://www.ijcai.org/proceedings/2025/153",
    "Efficient and Accurate Low-Resolution Transformer Tracking": "https://doi.org/10.1109/IROS60139.2025.11247730",
    "Exploring Enhanced Contextual Information for Video-Level Object Tracking": "https://ojs.aaai.org/index.php/AAAI/article/view/32440",
    "Autoregressive Sequential Pretraining for Visual Tracking": "https://openaccess.thecvf.com/content/CVPR2025/html/Liang_Autoregressive_Sequential_Pretraining_for_Visual_Tracking_CVPR_2025_paper.html",
    "Exploring Lightweight Hierarchical Vision Transformers for Efficient Visual Tracking": "https://openaccess.thecvf.com/content/ICCV2023/html/Kang_Exploring_Lightweight_Hierarchical_Vision_Transformers_for_Efficient_Visual_Tracking_ICCV_2023_paper.html",
    "Context-Aware Token Pruning and Discriminative Selective Attention for Transformer Tracking": "https://www.sciencedirect.com/science/article/pii/S1047320326001793",
    "Fully Spiking Neural Networks for Unified Frame-Event Object Tracking": "https://proceedings.neurips.cc/paper_files/paper/2025/hash/af752cfbdcc6fd3e4cd0eea9f1ad0fab-Abstract-Conference.html",
    "Optimizing intrinsic representation for tracking": "https://www.sciencedirect.com/science/article/pii/S0950705124005896",
}


FAMILY_IDS = {
    "Model compression / distillation": "F01",
    "Token / feature / spatial sparsification": "F02",
    "Pruning": "F03",
    "Dynamic / conditional computation": "F04",
    "Block / layer reduction": "F05",
    "Width/channel reduction": "F06",
    "Lightweight backbone design": "F07",
    "Asymmetric template-search architecture": "F08",
    "Template computation reuse": "F09",
    "Low-resolution / adaptive-resolution processing": "F10",
    "Autoregressive / sequence modeling": "F11",
    "Temporal context / video-level memory": "F12",
    "Motion modeling": "F13",
    "Template / target memory": "F14",
    "Relation / cross-attention modeling": "F15",
    "SNN / neuromorphic computation": "F16",
    "Temporal timestep optimization": "F17",
    "Target-aware representation": "F18",
    "Robustness / distractor handling": "F19",
    "Training / loss redesign": "F20",
}


def normalize_status(row: dict[str, str]) -> str:
    if row["title"] in STATUS_OVERRIDES:
        return STATUS_OVERRIDES[row["title"]]
    old = row["publication_status"]
    venue = row["venue"].casefold()
    if old == "ARXIV_PREPRINT":
        return "arXiv/preprint only"
    if old == "CONFERENCE_LISTED_UNVERIFIED":
        return "peer-reviewed conference"
    if old == "JOURNAL_LISTED_UNVERIFIED":
        return "peer-reviewed journal"
    if "conference" in venue or "cvpr" in venue or "iccv" in venue:
        return "peer-reviewed conference"
    return "unclear"


def build_inventory() -> list[dict[str, str]]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    # Primary verification established that these are preprint and proceedings
    # versions of the same LoReTrack work.  Preserve both identifiers in one row.
    arxiv_title = "LoReTrack: Efficient and Accurate Low-Resolution Transformer Tracking"
    final_title = "Efficient and Accurate Low-Resolution Transformer Tracking"
    preprint = next(r for r in rows if r["title"] == arxiv_title)
    proceedings = next(r for r in rows if r["title"] == final_title)
    merged = dict(proceedings)
    merged.update(
        {
            "source_graph": "BOTH",
            "publication_status": "CONFERENCE_LISTED_UNVERIFIED",
            "arxiv_id": preprint["arxiv_id"],
            "semantic_scholar_id": proceedings["semantic_scholar_id"] + ";" + preprint["semantic_scholar_id"],
            "raw_record_ids": proceedings["raw_record_ids"] + "; " + preprint["raw_record_ids"],
            "dedup_record_count": "3",
            "dedup_method": "manual preprint-to-proceedings verification",
            "notes": "Manually merged arXiv:2405.17660 and IROS 2025 versions; both strong IDs retained.",
        }
    )
    rows = [r for r in rows if r["title"] not in {arxiv_title, final_title}] + [merged]

    oirt = next(r for r in rows if r["title"] == "Optimizing intrinsic representation for tracking")
    oirt.update({
        "venue": "Knowledge-Based Systems 297",
        "doi": "10.1016/j.knosys.2024.111955",
        "publication_status": "JOURNAL_LISTED_UNVERIFIED",
        "visual_SOT_relevance": "SUPPORTING",
        "candidate_solution_families": "Target-aware representation; Training / loss redesign",
    })
    video = next(r for r in rows if r["title"] == "VideoTrack: Learning to Track Objects via Video Transformer -Supplementary Materials-In")
    video.update({
        "title": "VideoTrack: Learning To Track Objects via Video Transformer",
        "normalized_title": "videotrack learning to track objects via video transformer",
        "first_author": "Fei Xie",
        "all_authors": "Fei Xie and Lei Chu and Jiahao Li and Yan Lu and Chao Ma",
        "year": "2023",
        "venue": "CVPR 2023",
        "doi": "10.1109/CVPR52729.2023.02186",
        "publication_status": "CONFERENCE_LISTED_UNVERIFIED",
        "has_official_code": "YES",
        "official_code_url": "https://github.com/phiphiphi31/VideoTrack",
        "primary_paper_url": "https://openaccess.thecvf.com/content/CVPR2023/html/Xie_VideoTrack_Learning_To_Track_Objects_via_Video_Transformer_CVPR_2023_paper.html",
        "candidate_solution_families": "Temporal context / video-level memory; Autoregressive / sequence modeling",
        "notes": "Connected Papers exported a supplementary-material record; canonicalized to the CVPR 2023 primary paper.",
    })
    published_metadata = {
        "MixFormerV2: Efficient Fully Transformer Tracking": {
            "venue": "NeurIPS 2023", "publication_status": "CONFERENCE_LISTED_UNVERIFIED",
        },
        "Context-Aware Token Pruning and Discriminative Selective Attention for Transformer Tracking": {
            "year": "2026", "venue": "Journal of Visual Communication and Image Representation 119",
            "doi": "10.1016/j.jvcir.2026.104884", "publication_status": "JOURNAL_LISTED_UNVERIFIED",
        },
        "Fully Spiking Neural Networks for Unified Frame-Event Object Tracking": {
            "venue": "NeurIPS 2025", "publication_status": "CONFERENCE_LISTED_UNVERIFIED",
        },
    }
    for row in rows:
        row.update(published_metadata.get(row["title"], {}))
    rows.sort(key=lambda r: r["normalized_title"])

    fields = [
        "paper_id", "title", "first_author", "year", "venue", "doi", "arxiv_id",
        "semantic_scholar_id", "source_graph", "publication_status", "visual_SOT_relevance",
        "has_official_code", "official_code_url", "primary_paper_url", "solution_families",
        "dedup_basis", "raw_record_ids", "evidence_source", "notes",
    ]
    final = []
    for index, row in enumerate(rows, 1):
        title = row["title"]
        code, code_url = CODE_OVERRIDES.get(title, (row["has_official_code"], row["official_code_url"]))
        status = normalize_status(row)
        relevance = row["visual_SOT_relevance"]
        if title in {"Joint Feature Learning and Relation Modeling for Tracking: A One-Stream Framework"}:
            relevance = "HISTORICAL"
        source_evidence = "E01;E02" if row["source_graph"] == "BOTH" else ("E01" if row["source_graph"] == "FARTrack" else "E02")
        if title == "Optimizing intrinsic representation for tracking":
            source_evidence += ";E25"
        if title == "VideoTrack: Learning To Track Objects via Video Transformer":
            source_evidence += ";E26"
        note_parts = [
            "Long-tail status/family annotations derive from supplied metadata unless a primary evidence override is named.",
        ]
        if title == final_title:
            note_parts.insert(0, merged["notes"])
        if title == "VideoTrack: Learning To Track Objects via Video Transformer":
            note_parts.insert(0, "Canonicalized from a supplementary-only export record to the CVPR 2023 paper.")
        if title == "Exploring Efficient and Effective Sequence Learning for Visual Object Tracking":
            note_parts.append("An author-designated repository was checked but contains no FastSeqTrack implementation.")
        if title == "Autoregressive Sequential Pretraining for Visual Tracking":
            note_parts.append("The official project page states that code will be released; no implementation was located.")
        if status == "unclear" or relevance == "UNKNOWN":
            note_parts.append("Manual review remains required.")
        final.append(
            {
                "paper_id": f"P{index:03d}",
                "title": title,
                "first_author": row["first_author"],
                "year": row["year"],
                "venue": row["venue"],
                "doi": row["doi"],
                "arxiv_id": row["arxiv_id"],
                "semantic_scholar_id": row["semantic_scholar_id"],
                "source_graph": row["source_graph"],
                "publication_status": status,
                "visual_SOT_relevance": relevance,
                "has_official_code": code,
                "official_code_url": code_url,
                "primary_paper_url": URL_OVERRIDES.get(title, row["primary_paper_url"]),
                "solution_families": row["candidate_solution_families"],
                "dedup_basis": row["dedup_method"],
                "raw_record_ids": row["raw_record_ids"],
                "evidence_source": source_evidence,
                "notes": " ".join(note_parts),
            }
        )

    with (ROOT / "02_deduplicated_paper_inventory.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(final)
    return final


def add_node(nodes: dict[str, dict[str, str]], node_id: str, label: str, node_type: str,
             anchor: str = "NO", status: str = "N/A", source_graph: str = "N/A",
             description: str = "", evidence: str = "") -> None:
    nodes[node_id] = {
        "node_id": node_id, "label": label, "node_type": node_type, "anchor": anchor,
        "publication_status": status, "source_graph": source_graph,
        "description": description, "evidence_source": evidence,
    }


def add_edge(edges: list[dict[str, str]], source: str, target: str, edge_type: str,
             confidence: str, evidence: str, notes: str) -> None:
    edges.append({
        "source": source, "target": target, "edge_type": edge_type,
        "confidence": confidence, "evidence_source": evidence, "notes": notes,
    })


def build_graph(papers: list[dict[str, str]]) -> None:
    nodes: dict[str, dict[str, str]] = {}
    edges: list[dict[str, str]] = []

    add_node(nodes, "NBR_FAR", "FARTrack Connected Papers neighborhood", "LITERATURE_NEIGHBORHOOD", description="Discovery provenance only; topology unavailable.", evidence="E01")
    add_node(nodes, "NBR_SPIKE", "SpikeTrack Connected Papers neighborhood", "LITERATURE_NEIGHBORHOOD", description="Discovery provenance only; topology unavailable.", evidence="E02")
    add_node(nodes, "A_FAR", "FARTrack", "ANCHOR_TRACKER", "YES", description="Lightweight/autoregressive knowledge anchor.", evidence="E03;E04")
    add_node(nodes, "A_SPIKE", "SpikeTrack", "ANCHOR_TRACKER", "YES", description="Spike-driven redesign anchor.", evidence="E05;E06;E07")

    title_to_id: dict[str, str] = {}
    for paper in papers:
        node_id = "P_" + paper["paper_id"]
        title_to_id[paper["title"]] = node_id
        add_node(nodes, node_id, paper["title"], "PAPER", status=paper["publication_status"], source_graph=paper["source_graph"], description=f"{paper['year']} | {paper['visual_SOT_relevance']}", evidence=paper["evidence_source"])
        if paper["source_graph"] in {"FARTrack", "BOTH"}:
            add_edge(edges, "NBR_FAR", node_id, "contains_export_entry", "HIGH", "E01", "Neighborhood membership only; not a Connected Papers similarity edge.")
        if paper["source_graph"] in {"SpikeTrack", "BOTH"}:
            add_edge(edges, "NBR_SPIKE", node_id, "contains_export_entry", "HIGH", "E02", "Neighborhood membership only; not a Connected Papers similarity edge.")

    for family, family_id in FAMILY_IDS.items():
        add_node(nodes, family_id, family, "SOLUTION_FAMILY", description="Multi-label taxonomy family.", evidence="E01;E02")
    for paper in papers:
        if paper["solution_families"] in {"", "UNKNOWN"}:
            continue
        for family in paper["solution_families"].split("; "):
            if family in FAMILY_IDS:
                add_edge(edges, "P_" + paper["paper_id"], FAMILY_IDS[family], "addresses_within", "LOW", paper["evidence_source"], "Title/abstract metadata screening; high-relevance mechanisms are separately primary-verified.")

    problems = {
        "PR_EDGE": ("Practical conventional-edge efficiency", "Reduce latency/residency without assuming neuromorphic hardware."),
        "PR_ACCURACY": ("Accuracy retention under compression", "Preserve tracking evidence while reducing depth, width, tokens or resolution."),
        "PR_REDUNDANCY": ("Repeated template and token computation", "Avoid recomputing stable target information."),
        "PR_TEMPORAL": ("Temporal target evolution", "Use history without uncontrolled drift or excessive state."),
        "PR_DEPLOY": ("Export and runtime mismatch", "Bridge dense framework operators and edge deployment constraints."),
    }
    for node_id, (label, description) in problems.items():
        add_node(nodes, node_id, label, "PROBLEM", description=description, evidence="E03;E05;E07")

    components = {
        "C_FAR_ENCODER": ("FARTrack shared Transformer encoder", "ARCHITECTURAL_COMPONENT", "E03;E04"),
        "C_FAR_COMMAND": ("FARTrack four command-token outputs", "ARCHITECTURAL_COMPONENT", "E03;E04"),
        "C_FAR_TSSD": ("Task-Specific Self-Distillation", "TRAINING_STRATEGY", "E03;E04"),
        "C_FAR_IFAS": ("Inter-frame Autoregressive Sparsification", "MECHANISM", "E03;E04"),
        "C_FAR_MASK": ("Per-template persistent token mask", "ARCHITECTURAL_COMPONENT", "E03;E04"),
        "C_FAR_CE": ("Coordinate cross-entropy", "LOSS", "E03;E04"),
        "C_FAR_SIOU": ("SIoU box loss", "LOSS", "E03;E04"),
        "C_FAR_KL": ("Adjacent-depth task-logit KL", "LOSS", "E03;E04"),
        "C_SPIKE_TEMPLATE": ("SpikeTrack template SDT-v3 encoder", "ARCHITECTURAL_COMPONENT", "E05;E23"),
        "C_SPIKE_SEARCH": ("SpikeTrack search SDT-v3 encoder", "ARCHITECTURAL_COMPONENT", "E05;E23"),
        "C_SPIKE_NILIF": ("Normalized integer LIF", "MECHANISM", "E05;E23"),
        "C_SPIKE_CACHE": ("Six persistent K-transpose-V memories", "ARCHITECTURAL_COMPONENT", "E05;E23"),
        "C_SPIKE_MRM": ("Six Memory Retrieval Modules", "ARCHITECTURAL_COMPONENT", "E05;E23"),
        "C_SPIKE_HEAD": ("Three-tower spike center head", "ARCHITECTURAL_COMPONENT", "E05;E23"),
        "C_SPIKE_FOCAL": ("Weighted focal center loss", "LOSS", "E05"),
        "C_SPIKE_GIOU": ("GIoU box loss", "LOSS", "E05"),
        "C_SPIKE_L1": ("L1 box loss", "LOSS", "E05"),
        "C_SPIKE_RUNTIME": ("Two-stage Python cache/runtime interface", "ARCHITECTURAL_COMPONENT", "E07;E24"),
    }
    for node_id, (label, node_type, evidence) in components.items():
        add_node(nodes, node_id, label, node_type, evidence=evidence)

    principles = {
        "D_TASK_DISTILL": "Preserve task-facing distributions when reducing depth",
        "D_PREFIX": "Condition intermediate prefixes to be predictive",
        "D_TEMP_AMORT": "Amortize stable representation decisions across frames",
        "D_MODERATE": "Use conservative evidence-preserving sparsity",
        "D_ORTHOGONAL": "Treat model-size and token-compute reduction as orthogonal axes",
        "D_SPIKE_SPECIFIC": "Adapt transfer mechanisms to spike-valued representations",
    }
    for node_id, label in principles.items():
        add_node(nodes, node_id, label, "DESIGN_PRINCIPLE", evidence="E03;E04;E05")

    far_paper = title_to_id["FARTrack: Fast Autoregressive Visual Tracking with High Performance"]
    spike_paper = title_to_id["SpikeTrack: A Spike-driven Framework for Efficient Visual Tracking"]
    add_edge(edges, far_paper, "A_FAR", "describes", "HIGH", "E03;E04", "Fixed anchor identity.")
    add_edge(edges, spike_paper, "A_SPIKE", "describes", "HIGH", "E05;E06", "Fixed anchor identity.")
    for component in ["C_FAR_ENCODER", "C_FAR_COMMAND", "C_FAR_TSSD", "C_FAR_IFAS", "C_FAR_MASK", "C_FAR_CE", "C_FAR_SIOU", "C_FAR_KL"]:
        add_edge(edges, "A_FAR", component, "uses_mechanism", "HIGH", "E03;E04", "Paper/code distinction documented in the FARTrack analysis.")
    for component in ["C_SPIKE_TEMPLATE", "C_SPIKE_SEARCH", "C_SPIKE_NILIF", "C_SPIKE_CACHE", "C_SPIKE_MRM", "C_SPIKE_HEAD", "C_SPIKE_FOCAL", "C_SPIKE_GIOU", "C_SPIKE_L1", "C_SPIKE_RUNTIME"]:
        add_edge(edges, "A_SPIKE", component, "uses_mechanism", "HIGH", "E05;E07;E23;E24", "Released architecture/runtime evidence.")

    principle_edges = [
        ("C_FAR_TSSD", "D_TASK_DISTILL"), ("C_FAR_TSSD", "D_PREFIX"),
        ("C_FAR_IFAS", "D_TEMP_AMORT"), ("C_FAR_IFAS", "D_MODERATE"),
        ("C_FAR_TSSD", "D_ORTHOGONAL"), ("C_FAR_IFAS", "D_ORTHOGONAL"),
        ("A_SPIKE", "D_SPIKE_SPECIFIC"),
    ]
    for source, target in principle_edges:
        add_edge(edges, source, target, "instantiates_principle", "MEDIUM", nodes[source]["evidence_source"], "Analyst extraction from primary mechanism evidence.")

    family_problem = {
        "F01": "PR_ACCURACY", "F02": "PR_REDUNDANCY", "F03": "PR_EDGE",
        "F04": "PR_EDGE", "F05": "PR_EDGE", "F06": "PR_EDGE", "F07": "PR_EDGE",
        "F08": "PR_REDUNDANCY", "F09": "PR_REDUNDANCY", "F10": "PR_EDGE",
        "F11": "PR_TEMPORAL", "F12": "PR_TEMPORAL", "F13": "PR_TEMPORAL",
        "F14": "PR_TEMPORAL", "F15": "PR_ACCURACY", "F16": "PR_EDGE",
        "F17": "PR_EDGE", "F18": "PR_ACCURACY", "F19": "PR_ACCURACY", "F20": "PR_ACCURACY",
    }
    for family, problem in family_problem.items():
        add_edge(edges, family, problem, "solves_problem", "MEDIUM", "E01;E02", "Taxonomy-level relationship, not a paper performance claim.")
    add_edge(edges, "C_SPIKE_RUNTIME", "PR_DEPLOY", "contributes_to", "HIGH", "E07;E24", "Pinned-runtime/export evidence.")

    donor_map = {
        "FARTrack: Fast Autoregressive Visual Tracking with High Performance": ("E03;E04", "HIGH", "task-specific depth reduction and temporal mask reuse"),
        "Two-stream Beats One-stream: Asymmetric Siamese Network for Efficient Visual Tracking": ("E09", "HIGH", "template-once asymmetry; direct modulation is incompatible with SpikeTrack paper ablation"),
        "General Compression Framework for Efficient Transformer Object Tracking": ("E10", "MEDIUM", "stage replacement and stage-wise feature mimicking"),
        "MixFormerV2: Efficient Fully Transformer Tracking": ("E11", "MEDIUM", "deep-to-shallow and dense-to-sparse distillation; preprint only"),
        "LiteTrack: Layer Pruning with Asynchronous Feature Extraction for Lightweight and Efficient Visual Tracking": ("E12", "MEDIUM", "asynchronous feature extraction and layer pruning"),
        "Exploring Dynamic Transformer for Efficient Object Tracking": ("E13", "MEDIUM", "adaptive routes and target-aware self-distillation; strong collision"),
        "Exploring Efficient and Effective Sequence Learning for Visual Object Tracking": ("E14", "MEDIUM", "parallel decoding and confidence exit; collision-prone"),
        "Efficient and Accurate Low-Resolution Transformer Tracking": ("E15", "HIGH", "cross-resolution distillation"),
        "Exploring Enhanced Contextual Information for Video-Level Object Tracking": ("E16", "LOW", "persistent temporal state; likely cost increase"),
        "Autoregressive Sequential Pretraining for Visual Tracking": ("E17", "MEDIUM", "video-level appearance/motion pretraining"),
        "Exploring Lightweight Hierarchical Vision Transformers for Efficient Visual Tracking": ("E18", "MEDIUM", "lightweight hierarchy and bridge module"),
        "Context-Aware Token Pruning and Discriminative Selective Attention for Transformer Tracking": ("E19", "LOW", "target-aware token pruning; preprint and structural mismatch"),
        "Fully Spiking Neural Networks for Unified Frame-Event Object Tracking": ("E20", "LOW", "spike-specific regularization; multimodal task mismatch"),
    }
    for title, (evidence, confidence, note) in donor_map.items():
        add_edge(edges, title_to_id[title], "A_SPIKE", "knowledge_donor_to_SpikeTrack", confidence, evidence, note)

    far_donor_map = {
        "MixFormerV2: Efficient Fully Transformer Tracking": ("E11", "HIGH", "deep-to-shallow and dense-to-sparse distillation collision/reference"),
        "General Compression Framework for Efficient Transformer Object Tracking": ("E10", "MEDIUM", "stage-wise compression contrast to adjacent-depth TSSD"),
        "LiteTrack: Layer Pruning with Asynchronous Feature Extraction for Lightweight and Efficient Visual Tracking": ("E12", "MEDIUM", "static layer reduction and template-reuse contrast"),
        "Exploring Efficient and Effective Sequence Learning for Visual Object Tracking": ("E14", "MEDIUM", "parallel sequence-generation latency contrast"),
        "Efficient and Accurate Low-Resolution Transformer Tracking": ("E15", "MEDIUM", "orthogonal input-resolution reduction and distillation"),
        "Autoregressive Sequential Pretraining for Visual Tracking": ("E17", "HIGH", "autoregressive appearance-motion training reference"),
    }
    for title, (evidence, confidence, note) in far_donor_map.items():
        add_edge(edges, title_to_id[title], "A_FAR", "knowledge_donor_to_FARTrack", confidence, evidence, note)
    add_edge(edges, title_to_id["SeqTrack: Sequence to Sequence Learning for Visual Object Tracking"], "A_FAR", "architectural_ancestor", "MEDIUM", "E03", "Sequence-to-sequence tracking is a documented autoregressive paradigm reference; this edge does not assert code inheritance.")
    add_edge(edges, "A_FAR", "A_SPIKE", "shares_design_principle", "MEDIUM", "E03;E05", "Both reduce repeated tracking work, but representations and mechanisms are not directly compatible.")

    collision_titles = {
        "Two-stream Beats One-stream: Asymmetric Siamese Network for Efficient Visual Tracking": "asymmetric/template-once architecture",
        "MixFormerV2: Efficient Fully Transformer Tracking": "deep-to-shallow and dense-to-sparse distillation",
        "Exploring Dynamic Transformer for Efficient Object Tracking": "conditional depth/route selection",
        "Context-Aware Token Pruning and Discriminative Selective Attention for Transformer Tracking": "target-aware token sparsity",
        "Fully Spiking Neural Networks for Unified Frame-Event Object Tracking": "spiking tracking and SNN regularization",
    }
    for title, note in collision_titles.items():
        evidence = donor_map[title][0]
        add_edge(edges, title_to_id[title], "A_SPIKE", "possible_novelty_collision", "HIGH", evidence, note)

    add_node(nodes, "P_EXT_STD", "Exploring Reliable Spatiotemporal Dependencies for Efficient Visual Tracking", "PAPER", status="peer-reviewed conference", source_graph="EXTERNAL", description="External donor/collision check; not in either supplied export.", evidence="E21")
    add_edge(edges, "P_EXT_STD", "A_SPIKE", "knowledge_donor_to_SpikeTrack", "MEDIUM", "E21", "Quality-based temporal memory maintenance; external to supplied neighborhoods.")
    add_edge(edges, "P_EXT_STD", "A_FAR", "knowledge_donor_to_FARTrack", "LOW", "E21", "Reliability-aware temporal memory is a drift-control comparison for persistent template masks.")
    add_edge(edges, "P_EXT_STD", "F14", "addresses_within", "HIGH", "E21", "Primary-paper verified memory mechanism.")

    node_fields = ["node_id", "label", "node_type", "anchor", "publication_status", "source_graph", "description", "evidence_source"]
    with (ROOT / "09_nodes.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=node_fields)
        writer.writeheader(); writer.writerows(nodes.values())
    edge_fields = ["source", "target", "edge_type", "confidence", "evidence_source", "notes"]
    with (ROOT / "10_edges.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=edge_fields)
        writer.writeheader(); writer.writerows(edges)

    ns = "http://graphml.graphdrawing.org/xmlns"
    ET.register_namespace("", ns)
    graphml = ET.Element(f"{{{ns}}}graphml")
    node_keys = node_fields[1:]
    edge_keys = edge_fields[2:]
    for key in node_keys:
        ET.SubElement(graphml, f"{{{ns}}}key", id=f"n_{key}", attrib={"for": "node", "attr.name": key, "attr.type": "string"})
    for key in edge_keys:
        ET.SubElement(graphml, f"{{{ns}}}key", id=f"e_{key}", attrib={"for": "edge", "attr.name": key, "attr.type": "string"})
    graph = ET.SubElement(graphml, f"{{{ns}}}graph", id="KG_FAR_SPIKE_V1", edgedefault="directed")
    for node in nodes.values():
        element = ET.SubElement(graph, f"{{{ns}}}node", id=node["node_id"])
        for key in node_keys:
            data = ET.SubElement(element, f"{{{ns}}}data", key=f"n_{key}")
            data.text = node[key]
    for index, edge in enumerate(edges, 1):
        element = ET.SubElement(graph, f"{{{ns}}}edge", id=f"E{index:04d}", source=edge["source"], target=edge["target"])
        for key in edge_keys:
            data = ET.SubElement(element, f"{{{ns}}}data", key=f"e_{key}")
            data.text = edge[key]
    ET.indent(graphml, space="  ")
    ET.ElementTree(graphml).write(ROOT / "11_knowledge_graph_v1.graphml", encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    inventory = build_inventory()
    build_graph(inventory)
    print(f"built unique_papers={len(inventory)}")
