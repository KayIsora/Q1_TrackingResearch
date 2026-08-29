# Scope and method - FARTrack/SpikeTrack Knowledge Graph V1.1

**Terminal state:** `KNOWLEDGE_GRAPH_V1_1_READY_FOR_MANAGER_REVIEW`

**Cut-off:** 2026-08-29
**Claim labels:** `EVIDENCE-BACKED FACT`, `CODE FACT`, `PROJECT DECISION`, `INTERPRETATION`, `HYPOTHESIS`, `OPEN QUESTION`

## 1. Locked scope

**PROJECT DECISION.** FARTrack and SpikeTrack are the only two anchor trackers in Version 1. Other trackers are knowledge donors, historical references, evaluation references, or possible novelty collisions. Version 1 does not search for, score, or select a third baseline.

The two discovery inputs are the supplied Connected Papers BibTeX exports [E01, E02]. Connected Papers is used only as a literature-neighborhood discovery layer. The exports do not contain the original Connected Papers edge topology or edge weights, so this project does not reconstruct or imply either. The semantic edges in `10_edges.csv` are manually or mechanically derived project relationships and are labelled with evidence and confidence.

The similarly named neuroscience graph, `ConnectedPapers-for-An-improved-SpikeTrack-An-autonomous-multi-electrode...`, existed in the user/Manager handoff. Manager inspected its 41 neural-electrode-control/recording/spike-sorting records and verified that it is outside RGB visual SOT. It was intentionally excluded before corpus construction and contributes zero inventory rows and zero graph nodes or edges. Codex did not possess or parse that external export; the provenance status is `MANAGER_VERIFIED_EXTERNAL_EXCLUSION` [E28].

## 2. Anchor roles

- **FARTrack:** knowledge/reference anchor for shallow-yet-accurate distillation, autoregressive sequence modeling, multi-template processing, and inter-frame template-token sparsification [E03, E04].
- **SpikeTrack:** redesign anchor for testing whether spike-driven theoretical efficiency can become practical lightweight inference on conventional edge hardware. The paper is a peer-reviewed CVPR 2026 publication and the official implementation is available [E05, E06].

The prior conditional whole-MRM1 skip experiment is historical/null-result context only. Its frozen pre-MRM predictor failed the one-shot hold-out criterion; it must not be rescued post hoc, presented as an active contribution, or tuned with the consumed hold-out [E08]. The redesign space may consider other structural changes, but it may not silently reuse that hypothesis or validation set.

## 3. Inventory and deduplication

`01_connected_papers_inventory.csv` preserves one row per BibTeX entry per source graph. `02_deduplicated_paper_inventory.csv` preserves one row per unique paper.

Deduplication order:

1. normalized DOI;
2. normalized arXiv identifier;
3. Semantic Scholar paper identifier from the export URL;
4. normalized title;
5. manual verification for unresolved candidates.

Normalization lower-cases identifiers, strips DOI URL prefixes and trailing punctuation, collapses title whitespace, removes outer braces, and normalizes punctuation for comparison. A match at a later tier is not used to override a conflicting earlier identifier. Duplicate records retain merged provenance as `FARTrack`, `SpikeTrack`, or `BOTH`.

Publication status in the complete inventory is conservative:

- a verified official proceedings/journal record becomes `peer-reviewed conference/journal`;
- an arXiv-only record becomes `arXiv/preprint only`;
- a credible accepted/online-first record becomes `accepted/online-first` only when an official source supports it;
- all unresolved cases remain `unclear`.

All 74 identities received a status audit that did not use venue-string inference [E27]. The inventory distinguishes 14 `PRIMARY_VERIFIED_HIGH_RELEVANCE` identities, 56 `METADATA_CANONICALIZED` identities verified through publisher DOI metadata or official proceedings, and four `ARXIV_ONLY_VERIFIED` identities. No publication-status row remains unresolved; `UNKNOWN` can still appear for genuinely unavailable DOI or code fields, and absence of a discovered code URL is not evidence that no code exists.

## 4. Relevance and taxonomy

Every unique paper is tagged:

- `PRIMARY`: one of the two anchors or a directly transferable/high-collision mechanism paper;
- `SUPPORTING`: useful evidence for a solution family, mechanism, evaluation, or design constraint;
- `HISTORICAL`: a genuine conceptual ancestor whose date does not make it a current baseline candidate;
- `OUT_OF_SCOPE`: not relevant to generic RGB visual SOT after manual review.

Papers may map to multiple solution families. The taxonomy is problem -> solution family -> mechanism, not tracker-name -> category. Mechanically suggested mappings were manually reviewed for the high-relevance set; low-confidence long-tail mappings remain broad rather than inventing architecture details.

## 5. Evidence protocol

All non-trivial architectural and mechanism claims in the narrative artifacts use evidence IDs from `14_evidence_log.csv`. Primary papers, official proceedings, and official repositories are preferred. Local project measurements are cited only for the exact pinned source/config/hardware and are never generalized to Jetson Nano [E07, E22].

The following distinctions are mandatory:

- paper statement vs. project interpretation;
- analytical operation-energy estimate vs. measured device power;
- paper parameter count vs. total resident runtime modules;
- arXiv-only knowledge donor vs. peer-reviewed publication evidence;
- transferable design principle vs. directly copied component;
- redesign hypothesis vs. selected final architecture.

## 6. Confidence convention

- `HIGH`: directly stated in a primary paper, official repository, or pinned project artifact.
- `MEDIUM`: a transparent functional relationship inferred from two or more cited facts.
- `LOW`: an exploratory association retained for review; it is not used as a central conclusion.

## 7. Non-claims and stopping boundary

This version does not claim:

- original Connected Papers similarity edges or weights;
- a third main tracker;
- measured Jetson Nano FPS, energy, thermals, or TensorRT compatibility;
- that SpikeTrack's analytical SNN energy advantage automatically appears on CUDA hardware;
- that the failed whole-MRM1 conditional skip is viable;
- a final new SpikeTrack architecture.

The redesign hypotheses are falsifiable candidates for future controlled training and ablation. Version 1.1 stops after the metadata/provenance/presentation repair, graph, transfer matrix, redesign space, teacher report, and review request are complete.
