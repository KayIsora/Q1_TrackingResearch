# Connected Papers BibTeX inventory analysis draft

## Scope and evidence boundary

This subtask parsed only the two fixed exports named in the mission:

- `ConnectedPapers-for-FARTrack%3A-Fast-Autoregressive-Visual-Tracking-with-High-Performance.bib`
- `ConnectedPapers-for-SpikeTrack%3A-A-Spike%20driven-Framework-for-Efficient-Visual-Tracking.bib`

The BibTeX files are treated only as literature-neighborhood inventories. They do not expose the Connected Papers graph topology or weights, so no Connected Papers edge was created or inferred.

All publication-status, relevance, taxonomy, code, and donor fields in these drafts are based only on the supplied BibTeX metadata. They are screening annotations, not primary-paper verification. `UNKNOWN` is retained where the metadata is insufficient.

## Counts and overlap

| Measure | Count |
|---|---:|
| FARTrack raw BibTeX entries | 41 |
| SpikeTrack raw BibTeX entries | 41 |
| Raw records total | 82 |
| Mechanically deduplicated draft | 75 |
| Unique records present in both graphs | 7 |
| FARTrack-only unique records | 34 |
| SpikeTrack-only unique records | 34 |
| Auto-merged duplicate pairs | 7 |
| Named neuroscience collision graph found | 0 |

The seven exact overlaps are:

1. Adaptive Target-Oriented Tracking
2. Correlation-Embedded Transformer Tracking: A Single-Branch Framework
3. Exploring Dynamic Transformer for Efficient Object Tracking
4. Exploring Efficient and Effective Sequence Learning for Visual Object Tracking
5. Exploring Lightweight Hierarchical Vision Transformers for Efficient Visual Tracking
6. LoReTrack: Efficient and Accurate Low-Resolution Transformer Tracking
7. SeqTrack: Sequence to Sequence Learning for Visual Object Tracking

One additional probable version duplicate is intentionally not auto-merged: the 2024 arXiv record `LoReTrack: Efficient and Accurate Low-Resolution Transformer Tracking` and the 2025 IROS record `Efficient and Accurate Low-Resolution Transformer Tracking`. They have distinct DOI and Semantic Scholar identifiers but the same first author, 0.921 normalized-title similarity, 0.943 abstract similarity, and the conference record explicitly identifies the method and LoReTrack repository. If primary-source review confirms that they are versions of one work, the final unique-paper count becomes 74; until then, 75 is the defensible mechanical count.

## Deduplication keys and issues

Deduplication ran in the required order: normalized DOI, normalized arXiv ID, Semantic Scholar ID, then normalized title. A weaker-key match is blocked rather than merged when stronger identifiers conflict. Every one of the seven automatic two-record clusters agrees on DOI, Semantic Scholar ID, and normalized title; four also agree on arXiv ID where one is present.

Manual review currently has three rows:

- the probable LoReTrack preprint/publication pair described above;
- `Optimizing intrinsic representation for tracking`, whose sparse metadata does not establish visual-SOT relevance;
- the `VideoTrack` supplementary-material record, whose venue, DOI/arXiv ID, and primary paper URL are missing.

Metadata completeness in the 75-record draft: two DOI values are unknown, 41 arXiv IDs are unknown, all 75 Semantic Scholar IDs are present, 11 abstracts are missing, one publication status is unknown, one primary-paper URL is unknown, and 55 official-code statuses remain unknown. `UNKNOWN` code status means the BibTeX abstract did not explicitly expose a GitHub/GitLab URL; it does not mean that code does not exist.

## Neuroscience name-collision check

The directory contains only the two fixed `.bib` files. No file matching the named `ConnectedPapers-for-An-improved-SpikeTrack-An-autonomous-multi-electrode...` export, and no other non-input SpikeTrack/multi-electrode BibTeX candidate, was found. Therefore:

- collision graph found: **NO**;
- collision graph parsed: **NO**;
- excluded collision-graph count in this run: **0**.

The parser is defensive: if such a sibling file is added later, it is reported as a collision candidate and remains outside the two-input parse.

## Likely visual-SOT relevance

The metadata-only draft tags 2 anchor records as `PRIMARY`, 71 as `SUPPORTING`, 1 as `OUT_OF_SCOPE`, and 1 as `UNKNOWN`.

- `PRIMARY`: the exact FARTrack and SpikeTrack titles, one instance each.
- `OUT_OF_SCOPE`: `CSCL: Bridging the plasticity-stability gap in continuous supervised contrastive learning`; its abstract concerns continual image-classification learning, not visual tracking. It remains in the inventory for provenance rather than being silently deleted.
- `UNKNOWN`: `Optimizing intrinsic representation for tracking`; title-only metadata is not enough to establish visual single-object tracking.
- Older visual-tracking papers were not automatically discarded. This export happens not to contain a likely visual-SOT record dated 2020 or earlier, so no row received the `HISTORICAL` year-based screening tag.

## Candidate solution families

The keyword-derived family counts are multi-label incidence counts, not mutually exclusive categories. The most frequent likely-visual-SOT tags are robustness/distractor handling (31), dynamic/conditional computation (14), relation/cross-attention modeling (12), asymmetric template-search design (12), target-aware representation (11), lightweight backbone design (11), autoregressive/sequence modeling (10), training/loss redesign (9), model compression/distillation (8), temporal context/video-level memory (8), pruning (7), motion modeling (7), and token/feature/spatial sparsification (6).

Interpretation cautions:

- The robustness count is broad and can be triggered by generic abstract language such as background suppression; it should be split during paper-card review.
- Dynamic/conditional computation is a recurring neighborhood family, but it must not be used to resurrect the failed conditional whole-MRM1 skipping hypothesis.
- Width/channel reduction receives no automatic hits. This is an evidence gap in the supplied abstracts, not evidence that width reduction is unimportant.
- Template computation reuse has only three keyword hits, but the associated mechanisms are high-value for SpikeTrack because they directly concern repeated template work.
- SNN/neuromorphic and timestep families have only two hits each. Their low frequency reflects the export neighborhood, not a conclusion about their scientific importance.

## Top candidate knowledge donors

The accompanying donor CSV lists ten metadata-supported candidates. The ordering prioritizes coverage of SpikeTrack redesign dimensions rather than performance ranking or baseline selection:

1. DyTrack: dynamic routing, feature recycling, target-aware self-distillation.
2. LoReTrack: low-resolution processing with QKV and discrimination distillation.
3. AsymTrack: one-time template computation and unidirectional modulation.
4. LiteTrack: asynchronous template/search processing and layer pruning.
5. MixFormerV2: dense-to-sparse and deep-to-shallow distillation.
6. CompressTracker: stage division, replacement training, and stage-wise feature mimicking.
7. HiT: lightweight hierarchical features with a deep-to-shallow Bridge Module.
8. FastSeqTrack: parallel sequence generation and early exit as an autoregressive-latency contrast.
9. MCITrack: persistent temporal hidden state and cross-attention.
10. SpikeFET: a direct spiking neighbor, with a major frame-event versus RGB-only compatibility caveat.

These are knowledge donors only. Neither membership in a Connected Papers export nor this metadata screening establishes a semantic edge to an anchor, publication-grade evidence, transfer compatibility, or a third baseline.

## Handoff cautions

- Verify the LoReTrack arXiv/IROS pair before freezing the unique count.
- Find the primary VideoTrack paper rather than treating its supplementary record as the paper.
- Manually determine whether `Optimizing intrinsic representation for tracking` is visual SOT.
- Verify every publication-status label against a primary publisher/conference source; the draft deliberately says `*_LISTED_UNVERIFIED`.
- Verify method and code claims from primary papers/repositories before generating semantic graph edges or paper cards.
- Preserve the historical MRM1 `DIAG_FAIL` boundary; the inventory does not authorize post-hoc rescue.
- Do not infer Connected Papers edges, select a third baseline, or declare a final SpikeTrack redesign from these artifacts.
