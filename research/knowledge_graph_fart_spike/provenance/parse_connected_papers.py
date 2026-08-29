#!/usr/bin/env python3
"""Parse and deduplicate the two fixed Connected Papers BibTeX exports.

This script is deliberately standard-library only.  It treats the exports as
literature inventories, not as recoverable Connected Papers edge lists.
"""

from __future__ import annotations

import csv
import difflib
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote


SOURCE_DIR = Path(r"E:\Robot_Backup\Tracker_Q1_Documents")
OUTPUT_DIR = Path(__file__).resolve().parent

INPUTS = {
    "FARTrack": SOURCE_DIR
    / "ConnectedPapers-for-FARTrack%3A-Fast-Autoregressive-Visual-Tracking-with-High-Performance.bib",
    "SpikeTrack": SOURCE_DIR
    / "ConnectedPapers-for-SpikeTrack%3A-A-Spike%20driven-Framework-for-Efficient-Visual-Tracking.bib",
}

ANCHOR_TITLES = {
    "fartrack fast autoregressive visual tracking with high performance": "FARTrack",
    "spiketrack a spike driven framework for efficient visual tracking": "SpikeTrack",
}


def squash(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def display_text(value: str | None) -> str:
    """Lightly clean BibTeX presentation without pretending to be a TeX engine."""
    value = squash(value)
    if not value or value.lower() == "null":
        return ""
    replacements = {
        r"\&": "&",
        r"\_": "_",
        r"\%": "%",
        "{": "",
        "}": "",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return squash(value)


def normalize_title(value: str | None) -> str:
    value = display_text(value)
    value = unicodedata.normalize("NFKD", value).casefold()
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)
    return squash(value)


def normalize_doi(value: str | None) -> str:
    value = display_text(value).casefold()
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value)
    return value.rstrip(".,; ")


def normalize_arxiv(value: str | None) -> str:
    value = display_text(value).casefold()
    value = re.sub(r"^(?:https?://arxiv\.org/(?:abs|pdf)/|arxiv:\s*)", "", value)
    value = value.removesuffix(".pdf")
    value = re.sub(r"v\d+$", "", value)
    match = re.search(r"(?:\d{4}\.\d{4,5}|[a-z-]+/\d{7})", value)
    return match.group(0) if match else ""


def semantic_scholar_id(key: str, url: str | None) -> str:
    url = display_text(url)
    match = re.search(r"semanticscholar\.org/paper/([0-9a-f]{40})(?:\b|/)", url, re.I)
    if match:
        return match.group(1).casefold()
    if re.fullmatch(r"[0-9a-f]{40}", key, re.I):
        return key.casefold()
    return ""


def split_entry_body(body: str) -> tuple[str, str]:
    depth = 0
    quoted = False
    escaped = False
    for index, char in enumerate(body):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"' and depth == 0:
            quoted = not quoted
        elif not quoted:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            elif char == "," and depth == 0:
                return body[:index].strip(), body[index + 1 :]
    raise ValueError("BibTeX entry has no top-level comma after its key")


def parse_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    index = 0
    size = len(text)
    while index < size:
        while index < size and (text[index].isspace() or text[index] == ","):
            index += 1
        if index >= size:
            break
        name_match = re.match(r"[A-Za-z][A-Za-z0-9_-]*", text[index:])
        if not name_match:
            raise ValueError(f"Cannot parse field name near: {text[index:index+80]!r}")
        name = name_match.group(0).casefold()
        index += len(name_match.group(0))
        while index < size and text[index].isspace():
            index += 1
        if index >= size or text[index] != "=":
            raise ValueError(f"Missing '=' after field {name!r}")
        index += 1
        while index < size and text[index].isspace():
            index += 1
        if index >= size:
            fields[name] = ""
            break

        if text[index] == "{":
            index += 1
            start = index
            depth = 1
            escaped = False
            while index < size and depth:
                char = text[index]
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                index += 1
            if depth:
                raise ValueError(f"Unclosed braced value for {name!r}")
            value = text[start : index - 1]
        elif text[index] == '"':
            index += 1
            chars: list[str] = []
            escaped = False
            while index < size:
                char = text[index]
                index += 1
                if escaped:
                    chars.extend(("\\", char))
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    break
                else:
                    chars.append(char)
            value = "".join(chars)
        else:
            start = index
            while index < size and text[index] != ",":
                index += 1
            value = text[start:index]
        fields[name] = squash(value)
    return fields


def parse_bibtex(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8-sig")
    entries: list[dict[str, object]] = []
    cursor = 0
    while True:
        at = text.find("@", cursor)
        if at < 0:
            break
        type_match = re.match(r"@([A-Za-z]+)\s*([({])", text[at:])
        if not type_match:
            cursor = at + 1
            continue
        entry_type = type_match.group(1).casefold()
        opener = type_match.group(2)
        closer = "}" if opener == "{" else ")"
        body_start = at + type_match.end()
        depth = 1
        quoted = False
        escaped = False
        index = body_start
        while index < len(text) and depth:
            char = text[index]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = not quoted
            elif not quoted:
                if char == opener:
                    depth += 1
                elif char == closer:
                    depth -= 1
            index += 1
        if depth:
            raise ValueError(f"Unclosed @{entry_type} entry at byte {at} in {path}")
        body = text[body_start : index - 1]
        key, field_text = split_entry_body(body)
        entries.append(
            {
                "entry_type": entry_type,
                "bibtex_key": key,
                "fields": parse_fields(field_text),
            }
        )
        cursor = index
    return entries


def first_author(author_field: str | None) -> str:
    author_field = display_text(author_field)
    return author_field.split(" and ", 1)[0].strip() if author_field else "UNKNOWN"


def extract_urls(text: str | None) -> list[str]:
    text = display_text(text)
    urls = re.findall(r"https?://[^\s<>]+", text)
    return [url.rstrip(".,;:)]}") for url in urls]


def code_metadata(abstract: str | None) -> tuple[str, str]:
    urls = extract_urls(abstract)
    code_urls = [url for url in urls if re.search(r"github\.com|gitlab\.com", url, re.I)]
    if code_urls:
        return "YES", code_urls[0]
    return "UNKNOWN", "UNKNOWN"


def publication_status(fields: dict[str, str]) -> str:
    journal = display_text(fields.get("journal"))
    doi = normalize_doi(fields.get("doi"))
    arxiv = normalize_arxiv(fields.get("arxivid"))
    if journal.casefold() == "arxiv" or doi.startswith("10.48550/arxiv."):
        return "ARXIV_PREPRINT"
    if re.search(r"(?:cvpr|iccv|eccv|wacv|ijcai|aaai|iros|icra)", doi, re.I):
        return "CONFERENCE_LISTED_UNVERIFIED"
    if journal:
        if re.search(r"conference|proceedings|\b(iccv|cvpr|eccv|wacv|ijcai|aaai)\b", journal, re.I):
            return "CONFERENCE_LISTED_UNVERIFIED"
        return "JOURNAL_LISTED_UNVERIFIED"
    if arxiv:
        return "ARXIV_PREPRINT"
    return "UNKNOWN"


def primary_paper_url(fields: dict[str, str]) -> str:
    doi = normalize_doi(fields.get("doi"))
    arxiv = normalize_arxiv(fields.get("arxivid"))
    if doi:
        return f"https://doi.org/{doi}"
    if arxiv:
        return f"https://arxiv.org/abs/{arxiv}"
    return "UNKNOWN"


def visual_sot_relevance(fields: dict[str, str]) -> tuple[str, str]:
    title_norm = normalize_title(fields.get("title"))
    anchor = ANCHOR_TITLES.get(title_norm)
    if anchor:
        return "PRIMARY", f"exact fixed-anchor title ({anchor})"

    text = " ".join(
        [display_text(fields.get("title")), display_text(fields.get("abstract"))]
    ).casefold()
    out_scope_terms = (
        "multi-electrode",
        "multi electrode",
        "spike sorting",
        "neuroscience",
        "electroencephal",
        "image classification datasets",
        "continual supervised contrastive learning",
    )
    if any(term in text for term in out_scope_terms):
        return "OUT_OF_SCOPE", "explicit non-visual/neuroscience term in BibTeX metadata"

    visual_terms = (
        "visual object tracking",
        "visual tracking",
        "single object tracking",
        "target tracking",
        "object tracking",
        "track objects via video transformer",
        "uav tracking",
        "transformer tracking",
        "tracker",
    )
    if any(term in text for term in visual_terms):
        year_text = display_text(fields.get("year"))
        year = int(year_text) if year_text.isdigit() else None
        if year is not None and year <= 2020:
            return "HISTORICAL", "visual-tracking metadata; year <= 2020 heuristic"
        return "SUPPORTING", "visual-tracking/tracker term in title or abstract"
    if "tracking" in text and any(
        term in text
        for term in (
            "template",
            "search region",
            "tracking benchmark",
            "video-level",
            "spatio-temporal",
            "foreground",
            "target-oriented",
        )
    ):
        return "SUPPORTING", "tracking plus visual-SOT component/benchmark term in metadata"
    if "tracking" in text:
        return "UNKNOWN", "generic tracking term only; manual scope check required"
    return "UNKNOWN", "insufficient visual-SOT evidence in available BibTeX metadata"


FAMILY_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    ("Model compression / distillation", (r"distill", r"model compression", r"teacher.student")),
    ("Token / feature / spatial sparsification", (r"spars", r"token (?:selection|elimination|reduction|condens)", r"redundant token")),
    ("Pruning", (r"prun",)),
    ("Dynamic / conditional computation", (r"dynamic", r"conditional comput", r"early.exit", r"routing", r"terminate forward")),
    ("Block / layer reduction", (r"shallow", r"layer reduction", r"depth reduction", r"fewer layers")),
    ("Width / channel reduction", (r"channel reduction", r"width reduction", r"narrow network")),
    ("Lightweight backbone design", (r"lightweight", r"efficient backbone", r"mobile", r"edge device", r"resource.constrained")),
    ("Asymmetric template-search architecture", (r"asymmetric", r"two.stream", r"siamese")),
    ("Template computation reuse", (r"template comput(?:e|ing).*once", r"reuse", r"recycl", r"cached template")),
    ("Low-resolution / adaptive-resolution processing", (r"low.resolution", r"adaptive.resolution", r"smaller input", r"across resolutions")),
    ("Autoregressive / sequence modeling", (r"auto.regress", r"autoregress", r"sequence learning", r"sequence.to.sequence", r"trajectory sequence")),
    ("Temporal context / video-level memory", (r"video.level", r"temporal context", r"historical context", r"hidden state", r"across frames", r"inter.frame")),
    ("Motion modeling", (r"motion", r"trajectory", r"spatio.temporal cue")),
    ("Template / target memory", (r"template memory", r"target memory", r"memory initialized by the template", r"memory retrieval", r"memory bank")),
    ("Relation / cross-attention modeling", (r"cross.attention", r"relation model", r"feature fusion", r"interaction mechanism")),
    ("SNN / neuromorphic computation", (r"spiking neural", r"\bsnn", r"spike.driven", r"neuromorphic")),
    ("Temporal timestep optimization", (r"timestep", r"time step", r"temporal step")),
    ("Target-aware representation", (r"target.aware", r"target cue", r"target.prior", r"object perception")),
    ("Robustness / distractor handling", (r"distractor", r"robust", r"background", r"occlusion")),
    ("Training / loss redesign", (r"training strateg", r"loss function", r"contrastive", r"self.distillation", r"knowledge distillation")),
]


def candidate_families(fields: dict[str, str]) -> tuple[list[str], list[str]]:
    text = " ".join(
        [display_text(fields.get("title")), display_text(fields.get("abstract"))]
    ).casefold()
    families: list[str] = []
    evidence: list[str] = []
    for family, patterns in FAMILY_PATTERNS:
        hits = sorted({match.group(0) for pattern in patterns for match in re.finditer(pattern, text, re.I)})
        if hits:
            families.append(family)
            evidence.append(f"{family}: {', '.join(hits[:4])}")
    return families, evidence


@dataclass
class UnionFind:
    parent: list[int]

    @classmethod
    def create(cls, size: int) -> "UnionFind":
        return cls(list(range(size)))

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        left_root, right_root = self.find(left), self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def id_sets(records: list[dict[str, object]], members: Iterable[int]) -> dict[str, set[str]]:
    result = {name: set() for name in ("doi", "arxiv_id", "semantic_scholar_id", "normalized_title")}
    for member in members:
        record = records[member]
        for name in result:
            value = str(record.get(name, ""))
            if value:
                result[name].add(value)
    return result


def conflicting_strong_ids(records: list[dict[str, object]], left: int, right: int, pass_name: str) -> bool:
    left_root_members = [index for index in range(len(records)) if records[index]["_uf"].find(index) == records[index]["_uf"].find(left)]
    right_root_members = [index for index in range(len(records)) if records[index]["_uf"].find(index) == records[index]["_uf"].find(right)]
    left_ids = id_sets(records, left_root_members)
    right_ids = id_sets(records, right_root_members)
    stronger = {
        "arxiv_id": ("doi",),
        "semantic_scholar_id": ("doi", "arxiv_id"),
        "normalized_title": ("doi", "arxiv_id", "semantic_scholar_id"),
    }.get(pass_name, ())
    for name in stronger:
        if left_ids[name] and right_ids[name] and left_ids[name].isdisjoint(right_ids[name]):
            return True
    return False


def paper_id(record: dict[str, object]) -> str:
    if record["semantic_scholar_id"]:
        return f"S2:{record['semantic_scholar_id']}"
    if record["arxiv_id"]:
        return f"ARXIV:{record['arxiv_id']}"
    if record["doi"]:
        return f"DOI:{record['doi']}"
    digest = hashlib.sha1(str(record["normalized_title"]).encode("utf-8")).hexdigest()
    return f"TITLE_SHA1:{digest}"


def richer_record_key(record: dict[str, object]) -> tuple[int, int, int]:
    fields = record["fields"]
    assert isinstance(fields, dict)
    populated = sum(1 for value in fields.values() if display_text(str(value)))
    abstract_len = len(display_text(fields.get("abstract")))
    is_anchor = int(str(record["normalized_title"]) in ANCHOR_TITLES)
    return is_anchor, populated, abstract_len


def collision_check() -> dict[str, object]:
    all_bibs = sorted(SOURCE_DIR.glob("*.bib"), key=lambda path: path.name.casefold())
    fixed = {path.resolve() for path in INPUTS.values()}
    candidates: list[str] = []
    for path in all_bibs:
        decoded = unquote(path.name).casefold()
        if path.resolve() in fixed:
            continue
        if "spiketrack" in decoded or (
            "multi-electrode" in decoded and "connectedpapers" in decoded
        ):
            candidates.append(str(path.resolve()))
    named_prefix_found = [
        str(path.resolve())
        for path in all_bibs
        if unquote(path.name).casefold().startswith(
            "connectedpapers-for-an-improved-spiketrack-an-autonomous-multi-electrode"
        )
    ]
    return {
        "checked_directory": str(SOURCE_DIR.resolve()),
        "exact_named_collision_prefix": "ConnectedPapers-for-An-improved-SpikeTrack-An-autonomous-multi-electrode",
        "named_collision_found": bool(named_prefix_found),
        "named_collision_paths": named_prefix_found,
        "other_non_input_spiketrack_or_multi_electrode_candidates": candidates,
        "excluded_graph_count": len(set(named_prefix_found + candidates)),
        "disposition": "EXCLUDED_FROM_PARSE_IF_PRESENT",
    }


def main() -> None:
    for source, path in INPUTS.items():
        if not path.is_file():
            raise FileNotFoundError(f"Required {source} input is missing: {path}")

    collision = collision_check()
    records: list[dict[str, object]] = []
    for source_graph, path in INPUTS.items():
        for sequence_index, parsed in enumerate(parse_bibtex(path), start=1):
            fields = parsed["fields"]
            assert isinstance(fields, dict)
            key = str(parsed["bibtex_key"])
            doi = normalize_doi(fields.get("doi"))
            arxiv_id = normalize_arxiv(fields.get("arxivid"))
            s2_id = semantic_scholar_id(key, fields.get("url"))
            title_norm = normalize_title(fields.get("title"))
            relevance, relevance_basis = visual_sot_relevance(fields)
            families, family_evidence = candidate_families(fields)
            code_status, code_url = code_metadata(fields.get("abstract"))
            records.append(
                {
                    "record_id": f"{source_graph}:{sequence_index:02d}:{key}",
                    "source_graph": source_graph,
                    "source_file": str(path.resolve()),
                    "source_sequence": sequence_index,
                    "bibtex_type": parsed["entry_type"],
                    "bibtex_key": key,
                    "fields": fields,
                    "title": display_text(fields.get("title")) or "UNKNOWN",
                    "normalized_title": title_norm,
                    "first_author": first_author(fields.get("author")),
                    "all_authors": display_text(fields.get("author")) or "UNKNOWN",
                    "year": display_text(fields.get("year")) or "UNKNOWN",
                    "venue": display_text(fields.get("journal")) or "UNKNOWN",
                    "doi": doi,
                    "arxiv_id": arxiv_id,
                    "semantic_scholar_id": s2_id,
                    "metadata_url": display_text(fields.get("url")) or "UNKNOWN",
                    "abstract": display_text(fields.get("abstract")) or "UNKNOWN",
                    "volume": display_text(fields.get("volume")) or "UNKNOWN",
                    "pages": display_text(fields.get("pages")) or "UNKNOWN",
                    "pmid": display_text(fields.get("pmid")) or "UNKNOWN",
                    "publication_status": publication_status(fields),
                    "visual_SOT_relevance": relevance,
                    "relevance_basis": relevance_basis,
                    "has_official_code": code_status,
                    "official_code_url": code_url,
                    "primary_paper_url": primary_paper_url(fields),
                    "candidate_solution_families": families,
                    "family_evidence_terms": family_evidence,
                }
            )

    uf = UnionFind.create(len(records))
    for record in records:
        record["_uf"] = uf
    merge_reasons: defaultdict[tuple[int, int], list[str]] = defaultdict(list)
    blocked_weaker_matches: list[dict[str, object]] = []

    for pass_name in ("doi", "arxiv_id", "semantic_scholar_id", "normalized_title"):
        buckets: defaultdict[str, list[int]] = defaultdict(list)
        for index, record in enumerate(records):
            value = str(record.get(pass_name, ""))
            if value:
                buckets[value].append(index)
        for value, indices in buckets.items():
            for index in indices[1:]:
                first = indices[0]
                if uf.find(first) == uf.find(index):
                    continue
                if conflicting_strong_ids(records, first, index, pass_name):
                    blocked_weaker_matches.append(
                        {
                            "match_type": pass_name,
                            "match_value": value,
                            "left_record_id": records[first]["record_id"],
                            "right_record_id": records[index]["record_id"],
                            "reason": "stronger identifiers conflict; not auto-merged",
                        }
                    )
                    continue
                left_root, right_root = uf.find(first), uf.find(index)
                uf.union(first, index)
                new_root = uf.find(first)
                merge_reasons[(new_root, index)].append(pass_name)

    clusters: defaultdict[int, list[int]] = defaultdict(list)
    for index in range(len(records)):
        clusters[uf.find(index)].append(index)

    # Reconstruct the decisive shared-key types for each final cluster.
    cluster_methods: dict[int, list[str]] = {}
    for root, members in clusters.items():
        methods: list[str] = []
        for name in ("doi", "arxiv_id", "semantic_scholar_id", "normalized_title"):
            counts = Counter(str(records[index].get(name, "")) for index in members)
            if any(value and count > 1 for value, count in counts.items()):
                methods.append(name)
        cluster_methods[root] = methods

    dedup_rows: list[dict[str, object]] = []
    manual_rows: list[dict[str, object]] = list(blocked_weaker_matches)
    for root, members in clusters.items():
        representative_index = max(members, key=lambda index: richer_record_key(records[index]))
        representative = records[representative_index]
        fields = representative["fields"]
        assert isinstance(fields, dict)
        identifiers = id_sets(records, members)
        conflicts = [name for name, values in identifiers.items() if len(values) > 1 and name != "normalized_title"]
        titles = sorted({str(records[index]["title"]) for index in members})
        graphs = {str(records[index]["source_graph"]) for index in members}
        source_graph = "BOTH" if len(graphs) == 2 else next(iter(graphs))
        families = sorted(
            {
                family
                for index in members
                for family in records[index]["candidate_solution_families"]
            }
        )
        family_evidence = sorted(
            {
                evidence
                for index in members
                for evidence in records[index]["family_evidence_terms"]
            }
        )
        review_flags: list[str] = []
        if conflicts:
            review_flags.append("CONFLICTING_IDENTIFIERS:" + "+".join(conflicts))
        if len(titles) > 1:
            review_flags.append("TITLE_VARIANTS")
        if representative["publication_status"] == "UNKNOWN":
            review_flags.append("PUBLICATION_STATUS_UNKNOWN")
        if representative["visual_SOT_relevance"] == "UNKNOWN":
            review_flags.append("VISUAL_SOT_RELEVANCE_UNKNOWN")
        if representative["primary_paper_url"] == "UNKNOWN":
            review_flags.append("PRIMARY_URL_UNKNOWN")

        doi_values = sorted(identifiers["doi"])
        arxiv_values = sorted(identifiers["arxiv_id"])
        s2_values = sorted(identifiers["semantic_scholar_id"])
        merged_record = dict(representative)
        merged_record["doi"] = doi_values[0] if len(doi_values) == 1 else " | ".join(doi_values) or "UNKNOWN"
        merged_record["arxiv_id"] = arxiv_values[0] if len(arxiv_values) == 1 else " | ".join(arxiv_values) or "UNKNOWN"
        merged_record["semantic_scholar_id"] = s2_values[0] if len(s2_values) == 1 else " | ".join(s2_values) or "UNKNOWN"
        merged_record["candidate_solution_families"] = families

        dedup_rows.append(
            {
                "paper_id": paper_id(representative),
                "title": representative["title"],
                "first_author": representative["first_author"],
                "year": representative["year"],
                "venue": representative["venue"],
                "doi": merged_record["doi"],
                "arxiv_id": merged_record["arxiv_id"],
                "semantic_scholar_id": merged_record["semantic_scholar_id"],
                "source_graph": source_graph,
                "publication_status": representative["publication_status"],
                "visual_SOT_relevance": representative["visual_SOT_relevance"],
                "has_official_code": representative["has_official_code"],
                "official_code_url": representative["official_code_url"],
                "primary_paper_url": representative["primary_paper_url"],
                "notes": (
                    "BibTeX-metadata-only draft; status/code/relevance require primary-source verification. "
                    + ("; ".join(review_flags) if review_flags else "No identifier conflict detected.")
                ),
                "normalized_title": representative["normalized_title"],
                "all_authors": representative["all_authors"],
                "metadata_url": representative["metadata_url"],
                "abstract": representative["abstract"],
                "candidate_solution_families": "; ".join(families) if families else "UNKNOWN",
                "family_evidence_terms": " | ".join(family_evidence) if family_evidence else "UNKNOWN",
                "relevance_basis": representative["relevance_basis"],
                "dedup_method": "; ".join(cluster_methods[root]) if len(members) > 1 else "UNIQUE",
                "dedup_record_count": len(members),
                "raw_record_ids": "; ".join(str(records[index]["record_id"]) for index in members),
                "manual_check": "YES" if review_flags else "NO",
                "review_flags": "; ".join(review_flags) if review_flags else "NONE",
            }
        )
        if review_flags:
            manual_rows.append(
                {
                    "match_type": "DEDUP_CLUSTER_REVIEW",
                    "match_value": str(dedup_rows[-1]["paper_id"]),
                    "left_record_id": str(dedup_rows[-1]["raw_record_ids"]),
                    "right_record_id": "UNKNOWN",
                    "reason": "; ".join(review_flags),
                }
            )

    dedup_rows.sort(key=lambda row: (str(row["title"]).casefold(), str(row["paper_id"])))

    # Do not auto-merge weaker fuzzy matches.  Surface likely preprint/publication
    # pairs and likely extensions for manual adjudication instead.
    for left_index, left in enumerate(dedup_rows):
        for right in dedup_rows[left_index + 1 :]:
            left_norm = str(left["normalized_title"])
            right_norm = str(right["normalized_title"])
            title_ratio = difflib.SequenceMatcher(None, left_norm, right_norm).ratio()
            left_core = left_norm.split(" ", 1)[-1] if ":" in str(left["title"]) else left_norm
            right_core = right_norm.split(" ", 1)[-1] if ":" in str(right["title"]) else right_norm
            same_first_author = str(left["first_author"]).casefold() == str(right["first_author"]).casefold()
            left_abstract = str(left["abstract"])
            right_abstract = str(right["abstract"])
            abstract_ratio = (
                difflib.SequenceMatcher(None, left_abstract, right_abstract).ratio()
                if left_abstract != "UNKNOWN" and right_abstract != "UNKNOWN"
                else 0.0
            )
            likely_pair = title_ratio >= 0.90 or (
                same_first_author and title_ratio >= 0.82 and abstract_ratio >= 0.55
            )
            if not likely_pair:
                continue
            pair_kind = (
                "POSSIBLE_PREPRINT_PUBLICATION_DUPLICATE"
                if abstract_ratio >= 0.90
                else "POSSIBLE_EXTENSION_OR_VERSION_RELATION"
            )
            manual_rows.append(
                {
                    "match_type": pair_kind,
                    "match_value": f"title_similarity={title_ratio:.3f}; abstract_similarity={abstract_ratio:.3f}",
                    "left_record_id": str(left["paper_id"]),
                    "right_record_id": str(right["paper_id"]),
                    "reason": (
                        f"same_first_author={same_first_author}; distinct strong IDs; "
                        "not auto-merged; inspect primary records"
                    ),
                }
            )

    raw_fieldnames = [
        "record_id",
        "source_graph",
        "source_file",
        "source_sequence",
        "bibtex_type",
        "bibtex_key",
        "title",
        "normalized_title",
        "first_author",
        "all_authors",
        "year",
        "venue",
        "doi",
        "arxiv_id",
        "semantic_scholar_id",
        "metadata_url",
        "primary_paper_url",
        "publication_status",
        "visual_SOT_relevance",
        "relevance_basis",
        "has_official_code",
        "official_code_url",
        "candidate_solution_families",
        "family_evidence_terms",
        "abstract",
        "volume",
        "pages",
        "pmid",
    ]
    with (OUTPUT_DIR / "01_raw_bib_inventory.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=raw_fieldnames, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            row = dict(record)
            row["candidate_solution_families"] = "; ".join(record["candidate_solution_families"]) or "UNKNOWN"
            row["family_evidence_terms"] = " | ".join(record["family_evidence_terms"]) or "UNKNOWN"
            row["doi"] = row["doi"] or "UNKNOWN"
            row["arxiv_id"] = row["arxiv_id"] or "UNKNOWN"
            row["semantic_scholar_id"] = row["semantic_scholar_id"] or "UNKNOWN"
            writer.writerow(row)

    dedup_fieldnames = list(dedup_rows[0].keys())
    with (OUTPUT_DIR / "02_deduplicated_paper_inventory_draft.csv").open(
        "w", encoding="utf-8-sig", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=dedup_fieldnames)
        writer.writeheader()
        writer.writerows(dedup_rows)

    manual_fieldnames = ["match_type", "match_value", "left_record_id", "right_record_id", "reason"]
    with (OUTPUT_DIR / "03_manual_review_flags.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=manual_fieldnames)
        writer.writeheader()
        writer.writerows(manual_rows)

    (OUTPUT_DIR / "00_neuroscience_collision_check.json").write_text(
        json.dumps(collision, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    graph_counts = Counter(str(record["source_graph"]) for record in records)
    source_counts = Counter(str(row["source_graph"]) for row in dedup_rows)
    status_counts = Counter(str(row["publication_status"]) for row in dedup_rows)
    relevance_counts = Counter(str(row["visual_SOT_relevance"]) for row in dedup_rows)
    family_counts = Counter(
        family
        for row in dedup_rows
        for family in str(row["candidate_solution_families"]).split("; ")
        if family and family != "UNKNOWN"
    )
    likely_sot_family_counts = Counter(
        family
        for row in dedup_rows
        if str(row["visual_SOT_relevance"]) in {"PRIMARY", "SUPPORTING", "HISTORICAL"}
        for family in str(row["candidate_solution_families"]).split("; ")
        if family and family != "UNKNOWN"
    )
    summary = {
        "inputs": {source: str(path.resolve()) for source, path in INPUTS.items()},
        "input_sha256": {
            source: hashlib.sha256(path.read_bytes()).hexdigest()
            for source, path in INPUTS.items()
        },
        "raw_entry_counts": dict(sorted(graph_counts.items())),
        "raw_total": len(records),
        "deduplicated_unique_total": len(dedup_rows),
        "overlap_unique_papers": source_counts.get("BOTH", 0),
        "unique_only_by_graph": {
            "FARTrack": source_counts.get("FARTrack", 0),
            "SpikeTrack": source_counts.get("SpikeTrack", 0),
        },
        "excluded_collision_graph_count": collision["excluded_graph_count"],
        "collision_graph_found": collision["named_collision_found"],
        "publication_status_counts": dict(sorted(status_counts.items())),
        "visual_SOT_relevance_counts": dict(sorted(relevance_counts.items())),
        "solution_family_counts_all_inventory": dict(family_counts.most_common()),
        "solution_family_counts_likely_visual_sot": dict(likely_sot_family_counts.most_common()),
        "dedup_cluster_size_counts": dict(
            sorted(Counter(int(row["dedup_record_count"]) for row in dedup_rows).items())
        ),
        "manual_review_row_count": len(manual_rows),
        "metadata_unknown_counts_unique_draft": {
            "doi": sum(str(row["doi"]) == "UNKNOWN" for row in dedup_rows),
            "arxiv_id": sum(str(row["arxiv_id"]) == "UNKNOWN" for row in dedup_rows),
            "semantic_scholar_id": sum(
                str(row["semantic_scholar_id"]) == "UNKNOWN" for row in dedup_rows
            ),
            "abstract": sum(str(row["abstract"]) == "UNKNOWN" for row in dedup_rows),
            "publication_status": sum(
                str(row["publication_status"]) == "UNKNOWN" for row in dedup_rows
            ),
            "primary_paper_url": sum(
                str(row["primary_paper_url"]) == "UNKNOWN" for row in dedup_rows
            ),
            "official_code_status": sum(
                str(row["has_official_code"]) == "UNKNOWN" for row in dedup_rows
            ),
        },
        "anchor_validation": {
            anchor: sum(
                1
                for record in records
                if ANCHOR_TITLES.get(str(record["normalized_title"])) == anchor
            )
            for anchor in ("FARTrack", "SpikeTrack")
        },
        "limitations": [
            "No Connected Papers edges or weights are present/reconstructed from BibTeX.",
            "Publication status, code status, relevance, and family tags are metadata-only drafts.",
            "Primary-source verification was intentionally not performed in this inventory subtask.",
        ],
    }
    (OUTPUT_DIR / "04_inventory_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
