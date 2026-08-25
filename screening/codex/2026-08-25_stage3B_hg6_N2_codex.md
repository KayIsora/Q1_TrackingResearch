# Stage 3B — HG6 Novelty Batch N2 — Independent Codex Audit

Audit date and search cutoff: **2026-08-25**. Web sources were accessed on 2026-08-25 unless identified as an already registered project source.

## 1. Boundary and blindness

This is the independent Codex HG6 N2 lane for only:

- **CX044 — AsymTrack.** Exact question: whether the stronger AsymTrack family points help low-resolution (LR), viewpoint-change (VC), and fast-motion (FM) frames disproportionately, while adding little on ordinary frames, thereby producing condition-specific capacity allocation. The AsymTrack core remains fixed: template-once/search-online asymmetry, efficient template modulation (ETM), reparameterized object perception enhancement (OPE), and corner localization.
- **CX058 — standalone HiT-DyHiT Route1/Route2.** Exact question: whether router calibration, rather than more backbone capacity, separates correct shallow/deep allocation from distractor- or clutter-induced misallocation: hard/distractor frames wrongly sent to Route1 versus easy/ordinary frames unnecessarily sent to Route2, jointly measuring robustness and wasted computation. The HiT hierarchy, Bridge, Route1, Route2, and router remain fixed; the separate DyOSTrack wrapper is outside scope.

The audit uses the authorized project policies, screening protocol, Stage-3 gap/HG6 protocol, Stage-3B execution plan, G2 reconciliation, the independent G2 formulation, implementation-evidence audits, the candidate matrix, and canonical references. Before and during this report I **did not read, search, grep, open, diff, inspect a patch for, or inspect the contents or history of**:

- screening/manager/2026-08-25_stage3B_hg6_N2_manager.md
- screening/manager/2026-08-25_stage3B_hg6_N2_source_candidates.csv
- screening/manager/2026-08-25_stage3B_hg6_plan.csv

The mandatory repository synchronization displayed incoming filenames and a commit summary, but no prohibited file content was opened or inspected. No Manager N2 conclusion informed this audit.

The project collision classes are applied as follows: the same mechanism, coupling, and task setting is a **direct collision**; a major mechanism or one coupling half with a material remaining distinction is a **partial collision**; work that constrains language or calibration without implementing the tracker relation is **adjacent prior art**; background-only work is non-colliding. Directness is evaluated at the proposed scientific relation, not reuse of the named tracker core: a different backbone, route name, or unrun candidate-specific diagnostic does not by itself create a material distinction. Evidence below is separated from inference and unknowns. This report does not assign S1–S7, calculate totals, rank, shortlist, choose a baseline, propose an architecture, run diagnostics, or register canonical references.

## 2. Search coverage

Candidate-name and mechanism-first searches were both run. Search snippets, citation indexes, and aggregators were used only for discovery. Serious claims were checked against official proceedings, publisher records, arXiv/OpenReview records, or author repositories. Accessible cited/citing neighborhoods were followed from the baseline papers and the strongest adaptive-tracking sources.

| Required coverage | CX044 AsymTrack | CX058 HiT-DyHiT |
|---|---|---|
| Candidate and exact-gap terms | AsymTrack; T/S/B; LR, VC, FM; family-point gain; ordinary/easy frames | DyHiT; HiT; Route1/Route2; Bridge; router threshold; calibration; forced-route regret |
| Mechanism synonyms | adaptive capacity, dynamic depth, early exit, family switching, block bypass, layer adaptation, resolution adaptation | early exit, shallow/deep routing, confidence calibration, uncertainty routing, false-shallow/false-deep, oracle route, conditional computation |
| Robustness conditions | low resolution, viewpoint change, fast motion, motion blur, UAV viewpoint, search-region regulation | distractor, clutter, background similarity, target-competitor margin, target absence, local/global search, temporal uncertainty |
| Same-task peer-reviewed work | EAST, SiamEE, POST, DyTrack, AVTrack, ABTrack, SGLATrack, BDTrack, SRRT, SGDViT | Depth-Adaptive Policies, SiamEE, DyTrack, Aba-ViTrack, ABTrack, DiffusionTrack, FastSeqTrack, ELGLT, UAST |
| 2026/post-baseline adversaries | ARTrack-AC and GD early-exit SOT; BDTrack's journal version is post-baseline but its arXiv v1 predates AsymTrack | ARTrack-AC, GD early-exit SOT, adaptive-depth RGB-T, MVLM |
| ArXiv-only boundary | version chronology and exact pre-publication text; UncL-STARK | UncL-STARK and exact-version checks |
| Adjacent fields | resolution-adaptive inference and coarse/fine temporal gating | dynamic-network calibration, jointly learned exits, nested prediction sets, risk-controlled early exit |
| Repository verification | AsymTrack, AVTrack, ABTrack, SGLATrack, BDTrack, SGDViT; DyTrack version chronology was verified from arXiv because no author-official repository was located | HiT/DyHiT, ABTrack, DiffusionTrack, ELGLT, MVLM, calibration repositories |

Negative-search coverage included literal searches for an AsymTrack-preserving T/S/B LR/VC/FM oracle factorial and a HiT-preserving distractor-conditioned paired Route1/Route2 regret/calibration study. No serious source reproducing either exact implementation-specific experiment was located. That absence is not treated as novelty by itself.

## 3. Exact query log

Disposition labels: **BROAD** means high-recall discovery; **PRECISION** means an exact mechanism/gap search; **TITLE_VERIFY**, **METADATA_VERIFY**, and **REPOSITORY_VERIFY** mean primary-source identity checks; **CITED/CITING** means a related-work or citation-neighborhood check. Repeated literal retries against the same endpoint and direct URL opens are consolidated into their unique meaningful query; no substantive query family is omitted.

| query_id | candidate | date | exact_query | source_or_database | result_disposition | serious_sources_found |
|---|---|---|---|---|---|---|
| Q001 | CX044 | 2026-08-25 | <code>"AsymTrack" "visual tracking"</code> | Web/AAAI/GitHub | TITLE/REPOSITORY_VERIFY | AsymTrack R39/R40 |
| Q002 | CX044 | 2026-08-25 | <code>"AsymTrack" "dynamic" tracker</code> | Web/arXiv/IEEE | PRECISION | DyTrack; DyHiT |
| Q003 | CX044 | 2026-08-25 | <code>"AsymTrack" low resolution viewpoint change fast motion</code> | Web/AAAI | PRECISION | AsymTrack attribute results only |
| Q004 | CX044 | 2026-08-25 | <code>"AsymTrack" T S B tracker resolution depth</code> | Web/AAAI/GitHub | PRECISION | AsymTrack variants only |
| Q005 | CX044 | 2026-08-25 | <code>"adaptive capacity" "visual tracking" tracker</code> | Web/CVF | BROAD | ARTrack-AC |
| Q006 | CX044 | 2026-08-25 | <code>"dynamic depth" "visual tracking" tracker</code> | Web/arXiv/Springer | BROAD | Depth-Adaptive Policies; DyTrack; DyHiT |
| Q007 | CX044 | 2026-08-25 | <code>"early exit" "visual object tracking"</code> | Web/IEEE/IJCAI/Elsevier | BROAD | EAST; SiamEE; DyTrack; FastSeqTrack; GD early exit |
| Q008 | CX044 | 2026-08-25 | <code>"block bypass" "visual tracking"</code> | Web/ScienceDirect/arXiv | PRECISION | ABTrack |
| Q009 | CX044 | 2026-08-25 | <code>"layer-adaptive" vision transformer tracking</code> | Web/CVF | PRECISION | SGLATrack |
| Q010 | CX044 | 2026-08-25 | <code>"family switching" visual object tracking capacity</code> | Web/AAAI/CVF | PRECISION | POST; ARTrack-AC |
| Q011 | CX044 | 2026-08-25 | <code>"Learning Policies for Adaptive Tracking With Deep Feature Cascades"</code> | CVF/DOI | TITLE/METADATA_VERIFY | EAST |
| Q012 | CX044 | 2026-08-25 | <code>"Early Exiting-Enabled Siamese Tracking for Edge Intelligence Applications"</code> | IEEE/DOI | TITLE/METADATA_VERIFY | SiamEE |
| Q013 | CX044 | 2026-08-25 | <code>"POST: POlicy-Based Switch Tracking"</code> | AAAI | TITLE_VERIFY | POST |
| Q014 | CX044 | 2026-08-25 | <code>"Exploring Dynamic Transformer for Efficient Object Tracking" venue</code> | IEEE/arXiv | TITLE/METADATA_VERIFY | DyTrack |
| Q015 | CX044 | 2026-08-25 | <code>site:arxiv.org/abs/2403.17651 "Exploring Dynamic Transformer for Efficient Object Tracking"</code> | arXiv | METADATA/CHRONOLOGY_VERIFY | DyTrack v1 |
| Q016 | CX044 | 2026-08-25 | <code>("low resolution" OR "viewpoint change" OR "fast motion") ("early exit" OR "dynamic depth" OR "adaptive computation") "visual tracking"</code> | arXiv/Web | PRECISION | DyTrack; AVTrack; BDTrack |
| Q017 | CX044 | 2026-08-25 | <code>"low-resolution" "adaptive computation" tracking</code> | Web/CVF/arXiv | PRECISION | no exact LR-specific SOT router |
| Q018 | CX044 | 2026-08-25 | <code>"viewpoint change" "adaptive computation" visual tracking</code> | Web/PMLR/CVF | PRECISION | AVTrack; DyTrack |
| Q019 | CX044 | 2026-08-25 | <code>"fast motion" "dynamic depth" visual tracking</code> | Web/arXiv/IEEE | PRECISION | DyTrack; BDTrack; SRRT |
| Q020 | CX044 | 2026-08-25 | <code>"Learning Adaptive and View-Invariant Vision Transformer" tracking</code> | PMLR/GitHub | TITLE/REPOSITORY_VERIFY | AVTrack |
| Q021 | CX044 | 2026-08-25 | <code>"Adaptively Bypassing Vision Transformer Blocks for Efficient Visual Tracking"</code> | ScienceDirect/arXiv/GitHub | TITLE/REPOSITORY_VERIFY | ABTrack |
| Q022 | CX044 | 2026-08-25 | <code>"Similarity-Guided Layer-Adaptive Vision Transformer for UAV Tracking"</code> | CVF/GitHub | TITLE/REPOSITORY_VERIFY | SGLATrack |
| Q023 | CX044 | 2026-08-25 | <code>"Learning motion blur robust vision transformers for real-time UAV tracking"</code> | ScienceDirect/arXiv/GitHub | TITLE/REPOSITORY_VERIFY | BDTrack |
| Q024 | CX044 | 2026-08-25 | <code>"adaptive search region" "fast motion" visual tracking</code> | Web/IEEE/arXiv | PRECISION | SRRT |
| Q025 | CX044 | 2026-08-25 | <code>"SRRT: Exploring Search Region Regulation for Visual Object Tracking"</code> | IEEE/arXiv | TITLE_VERIFY | SRRT |
| Q026 | CX044 | 2026-08-25 | <code>"SGDViT: Saliency-Guided Dynamic Vision Transformer for UAV Tracking"</code> | ICRA/author site/GitHub | TITLE/REPOSITORY_VERIFY | SGDViT |
| Q027 | CX044 | 2026-08-25 | <code>"dynamic resolution" "visual object tracking"</code> | Web/CVF | PRECISION | no same-task exact mechanism |
| Q028 | CX044 | 2026-08-25 | <code>"Resolution Adaptive Networks for Efficient Inference"</code> | CVF | ADJACENT_VERIFY | Resolution Adaptive Networks |
| Q029 | CX044 | 2026-08-25 | <code>"LiteEval" coarse-to-fine video recognition</code> | NeurIPS | ADJACENT_VERIFY | LiteEval |
| Q030 | CX044 | 2026-08-25 | <code>("oracle routing" OR "oracle route") "visual object tracking" capacity</code> | Web/arXiv | PRECISION | no exact SOT source |
| Q031 | CX044 | 2026-08-25 | <code>"AsymTrack" "oracle" route family T S B</code> | Web/AAAI/GitHub | PRECISION | no non-baseline source |
| Q032 | CX044 | 2026-08-25 | <code>site:github.com "Adaptive Capacity Autoregressive Visual Tracking"</code> | GitHub/Web | REPOSITORY_VERIFY | announced ARTrack-AC URL unavailable at audit |
| Q033 | CX044 | 2026-08-25 | <code>site:openaccess.thecvf.com "Adaptive Capacity Autoregressive Visual Tracking"</code> | CVF | TITLE_VERIFY | ARTrack-AC R56 |
| Q034 | CX044 | 2026-08-25 | <code>site:openaccess.thecvf.com AsymTrack adaptive capacity tracking</code> | CVF/Web | CITED/CITING | ARTrack-AC; adaptive-tracking neighborhood |
| Q035 | CX058 | 2026-08-25 | <code>"DyHiT" visual tracking Route1 Route2</code> | Web/Springer/arXiv/GitHub | TITLE/REPOSITORY_VERIFY | HiT-DyHiT R49/R50 |
| Q036 | CX058 | 2026-08-25 | <code>"Exploiting Lightweight Hierarchical ViT and Dynamic Framework for Efficient Visual Tracking"</code> | Springer/arXiv | TITLE/METADATA_VERIFY | DyHiT |
| Q037 | CX058 | 2026-08-25 | <code>site:github.com/kangben258/HiT DyHiT threshold router</code> | GitHub | REPOSITORY_VERIFY | DyHiT router/configuration |
| Q038 | CX058 | 2026-08-25 | <code>HiT DyHiT Route1 Route2 Bridge threshold foreground background IoU</code> | Web/arXiv/GitHub | PRECISION | DyHiT baseline mechanism |
| Q039 | CX058 | 2026-08-25 | <code>"visual tracking" "dynamic depth" tracker</code> | Web/Springer/arXiv | BROAD | Depth-Adaptive Policies; DyTrack; DyHiT |
| Q040 | CX058 | 2026-08-25 | <code>"single object tracking" "early exit"</code> | Web/IEEE/IJCAI/Elsevier | BROAD | SiamEE; DyTrack; FastSeqTrack; GD early exit |
| Q041 | CX058 | 2026-08-25 | <code>"visual tracking" "adaptive computation" tracker</code> | Web/CVF/PMLR | BROAD | AVTrack; ABTrack; ARTrack-AC |
| Q042 | CX058 | 2026-08-25 | <code>"Depth-Adaptive Computational Policies for Efficient Visual Tracking"</code> | Springer/author PDF/arXiv | TITLE/METADATA_VERIFY | Depth-Adaptive Policies |
| Q043 | CX058 | 2026-08-25 | <code>"Exploring Dynamic Transformer for Efficient Object Tracking"</code> | IEEE/arXiv | TITLE_VERIFY | DyTrack |
| Q044 | CX058 | 2026-08-25 | <code>"Efficient early exit single object tracking via general distribution"</code> | ScienceDirect/DOI | TITLE/METADATA_VERIFY | GD early-exit SOT |
| Q045 | CX058 | 2026-08-25 | <code>"Adaptively Bypassing Vision Transformer Blocks for Efficient Visual Tracking"</code> | ScienceDirect/arXiv/GitHub | TITLE/REPOSITORY_VERIFY | ABTrack |
| Q046 | CX058 | 2026-08-25 | <code>"Adaptive and Background-Aware Vision Transformer for Real-Time UAV Tracking"</code> | CVF/GitHub | TITLE/REPOSITORY_VERIFY | Aba-ViTrack |
| Q047 | CX058 | 2026-08-25 | <code>"DiffusionTrack" early exit confidence distractor</code> | CVF/supplement/GitHub | PRECISION/REPOSITORY_VERIFY | DiffusionTrack |
| Q048 | CX058 | 2026-08-25 | <code>"Exploring Efficient and Effective Sequence Learning for Visual Object Tracking"</code> | IJCAI/GitHub | TITLE/REPOSITORY_VERIFY | FastSeqTrack |
| Q049 | CX058 | 2026-08-25 | <code>"Effective Local and Global Search for Fast Long-Term Tracking"</code> | IEEE/GitHub | TITLE/REPOSITORY_VERIFY | ELGLT |
| Q050 | CX058 | 2026-08-25 | <code>"UAST: Uncertainty-Aware Siamese Tracking"</code> | PMLR | TITLE_VERIFY | UAST |
| Q051 | CX058 | 2026-08-25 | <code>visual tracking router calibration</code> | Web/arXiv/IEEE | PRECISION | no exact HiT calibration paper |
| Q052 | CX058 | 2026-08-25 | <code>"confidence-calibrated" tracking depth</code> | Web/CVF | PRECISION | adaptive-depth RGB-T tracker |
| Q053 | CX058 | 2026-08-25 | <code>"uncertainty-aware" "dynamic depth" "single object tracking"</code> | Web/arXiv/PMLR | PRECISION | UncL-STARK; UAST |
| Q054 | CX058 | 2026-08-25 | <code>"uncertainty-guided" "early exit" tracking</code> | Web/arXiv | PRECISION | UncL-STARK; generic early-exit calibration |
| Q055 | CX058 | 2026-08-25 | <code>"temporal-feedback" depth adaptation visual tracking</code> | Web/arXiv | PRECISION | UncL-STARK |
| Q056 | CX058 | 2026-08-25 | <code>"distractor-aware" route selection visual tracking</code> | Web/CVF | PRECISION | DAM4SAM; DaSiamRPN; no HiT forced-route study |
| Q057 | CX058 | 2026-08-25 | <code>"competitor-margin" tracking confidence</code> | Web/CVF | PRECISION | MVLM |
| Q058 | CX058 | 2026-08-25 | <code>"target-distractor margin" dynamic inference tracking</code> | Web/CVF | PRECISION | MVLM; distractor-aware tracking family |
| Q059 | CX058 | 2026-08-25 | <code>"ambiguity-conditioned" tracking mode</code> | Web/arXiv | PRECISION | no exact HiT route paper |
| Q060 | CX058 | 2026-08-25 | <code>"clutter-aware" "early exit" tracking</code> | Web/Elsevier/Springer | PRECISION | Depth-Adaptive Policies; GD early exit |
| Q061 | CX058 | 2026-08-25 | <code>"hard-frame" misrouting visual tracking</code> | Web/arXiv | PRECISION | no exact terminology; dynamic trackers only |
| Q062 | CX058 | 2026-08-25 | <code>"oracle route benefit" visual tracking</code> | Web/arXiv | PRECISION | no exact HiT study |
| Q063 | CX058 | 2026-08-25 | <code>"false-shallow" "false-deep" routing</code> | Web/arXiv | PRECISION | no serious exact-phrase source |
| Q064 | CX058 | 2026-08-25 | <code>"selective deep path" tracking</code> | Web/arXiv | PRECISION | adaptive-depth trackers |
| Q065 | CX058 | 2026-08-25 | <code>"confidence-based branch routing" visual tracking</code> | Web/CVF/IJCAI | PRECISION | DyTrack; FastSeqTrack; RGB-T adaptive depth |
| Q066 | CX058 | 2026-08-25 | <code>"local global search" gating visual tracking</code> | Web/IEEE/CVF | PRECISION | ELGLT; MVLM |
| Q067 | CX058 | 2026-08-25 | <code>"risk-aware conditional computation" tracking</code> | Web/NeurIPS | PRECISION/ADJACENT | Fast yet Safe; no same-task exact source |
| Q068 | CX058 | 2026-08-25 | <code>site:proceedings.neurips.cc early exit failure prediction calibration</code> | NeurIPS | ADJACENT_VERIFY | Fast yet Safe |
| Q069 | CX058 | 2026-08-25 | <code>"Fixing Overconfidence in Dynamic Neural Networks"</code> | CVF/GitHub | TITLE/REPOSITORY_VERIFY | Meronen et al. |
| Q070 | CX058 | 2026-08-25 | <code>"Jointly-Learned Exit and Inference for a Dynamic Neural Network"</code> | ICLR | TITLE_VERIFY | Regol et al. |
| Q071 | CX058 | 2026-08-25 | <code>"Early-Exit Neural Networks with Nested Prediction Sets"</code> | PMLR | TITLE_VERIFY | Jazbec et al. |
| Q072 | CX058 | 2026-08-25 | <code>"Fast Yet Safe: Early-Exiting with Risk Control"</code> | NeurIPS/GitHub | TITLE/REPOSITORY_VERIFY | Jazbec et al. |
| Q073 | CX058 | 2026-08-25 | <code>"Uncertainty-Guided Inference-Time Depth Adaptation for Transformer-Based Visual Tracking"</code> | arXiv | TITLE_VERIFY | UncL-STARK |
| Q074 | CX058 | 2026-08-25 | <code>"Adaptive Depth Lightweight RGB-T Tracking with Holistic Token Routing"</code> | CVF | TITLE_VERIFY | adaptive-depth RGB-T tracker |
| Q075 | CX058 | 2026-08-25 | <code>"MVLM: Template-Free Tracking via Vision-Language Margin Confidence and Memory-Gated Tracking"</code> | CVF/GitHub | TITLE/REPOSITORY_VERIFY | MVLM |
| Q076 | BOTH | 2026-08-25 | <code>site:openaccess.thecvf.com visual tracking uncertainty-guided early exit confidence threshold distractor</code> | CVF | BROAD | DiffusionTrack; RGB-T adaptive depth; ARTrack-AC |
| Q077 | BOTH | 2026-08-25 | <code>site:openaccess.thecvf.com visual tracking adaptive capacity difficulty routing</code> | CVF | BROAD/CITED-CITING | EAST neighborhood; ARTrack-AC |
| Q078 | BOTH | 2026-08-25 | <code>early exit oracle routing correctness labels dynamic neural network official paper</code> | Web/ICLR/NeurIPS | ADJACENT | Regol; Fast yet Safe |
| Q079 | BOTH | 2026-08-25 | <code>site:proceedings.mlr.press early-exit uncertainty calibration dynamic inference</code> | PMLR | ADJACENT | nested prediction sets |
| Q080 | BOTH | 2026-08-25 | <code>site:ojs.aaai.org "POST: POlicy-Based Switch Tracking"</code> | AAAI | TITLE/CITED-CITING | POST |
| Q081 | CX044 | 2026-08-25 | <code>"Two-stream Beats One-stream" adaptive tracking</code> | Web/AAAI/GitHub | TITLE/PRECISION | AsymTrack; dynamic-tracking neighborhood |
| Q082 | CX058 | 2026-08-25 | <code>site:link.springer.com/article "Exploiting Lightweight Hierarchical ViT and Dynamic Framework for Efficient Visual Tracking"</code> | Springer | TITLE/METADATA_VERIFY | DyHiT |

## 4. AsymTrack prior-art table

The anchor is canonical **R39/R40**. Evidence from the G2 reconciliation establishes that the T/S/B comparison is not a clean single-axis ladder: T→S changes late search depth, while S→B changes search resolution and relation-token count; checkpoints also differ in training data or optimization. Therefore, a raw per-attribute result cannot be interpreted as a causal capacity-allocation effect without controls.

| source | chronology relative to AsymTrack | primary-source evidence | collision | exact-gap boundary |
|---|---|---|---|---|
| [EAST, ICCV 2017](https://openaccess.thecvf.com/content_ICCV_2017/papers/Huang_Learning_Policies_for_ICCV_2017_paper.pdf) | pre-baseline | A policy exits on easy/confident frames and invokes deeper features on challenging frames in SOT. | **DIRECT** to condition-specific tracking capacity | CNN feature cascade; no AsymTrack core or LR/VC/FM factorial. |
| [SiamEE, IEEE Access 2021](https://doi.org/10.1109/ACCESS.2021.3119604) | pre-baseline | Side exits and confidence thresholds avoid deeper Siamese processing for easy samples. | **PARTIAL** easy/ordinary versus hard-frame allocation | No LR/VC/FM coupling or AsymTrack family points; the paper reports a robustness trade-off. |
| [POST, AAAI 2020](https://ojs.aaai.org/index.php/AAAI/article/view/6899) | pre-baseline | A learned policy selects one complementary tracker expert per frame. | **PARTIAL** family/expert switching | Switches complete trackers, not depth/resolution inside AsymTrack. |
| [DyTrack, arXiv v1 2024 / TNNLS 2025](https://arxiv.org/abs/2403.17651v1) | **pre-baseline public v1** | Learned intermediate confidence routes easy versus hard frames; v1 attribute analysis reports FM benefiting from complex routes while VC often exits early. | **DIRECT and closest collision** | Not AsymTrack T/S/B; its VC evidence also warns against assuming the candidate premise. |
| [AVTrack, ICML 2024](https://proceedings.mlr.press/v235/li24ax.html) | pre-baseline | The tracker combines input-conditioned block activation with separately learned view-invariant representations. | **PARTIAL** adaptive depth plus VC robustness ingredients | UAV tracker; no evidence that viewpoint change controls depth and no LR/FM/ordinary AsymTrack factorial. |
| [ABTrack, arXiv v1 2024 / Pattern Recognition 2025](https://doi.org/10.1016/j.patcog.2024.111278) | **pre-baseline arXiv v1 (2024-06-12); journal May 2025** | Target/scene-conditioned bypass probabilities allocate Transformer blocks, with clutter motivating deeper semantics. | **DIRECT** dynamic depth and scene condition in RGB SOT | Per-block bypass rather than the exact T/S/B factorial; repository was README-only at audit. |
| [Aba-ViTrack, ICCV 2023](https://openaccess.thecvf.com/content/ICCV2023/html/Li_Adaptive_and_Background-Aware_Vision_Transformer_for_Real-Time_UAV_Tracking_ICCV_2023_paper.html) | pre-baseline | Learned halting probabilities have a higher prior for background tokens than target tokens. | **PARTIAL** background-token-aware compute | Token-level halting, not whole-family capacity or exact attributes. |
| [SGDViT, ICRA 2023](https://vision4robotics.github.io/publication/2023_icra_sgdvit/) | pre-baseline | Saliency-guided dynamic tokens reduce tracker computation in UAV conditions. | **PARTIAL** dynamic computation | Token selection rather than depth/resolution family allocation. |
| [SGLATrack, CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Xue_Similarity-Guided_Layer-Adaptive_Vision_Transformer_for_UAV_Tracking_CVPR_2025_paper.html) | post-baseline publication | Inter-layer similarity between saturated search features and candidate subsequent-layer features selects a later layer. | **PARTIAL** layer allocation | No AsymTrack core or T/S/B attribute oracle. |
| [FastSeqTrack, IJCAI 2025](https://doi.org/10.24963/ijcai.2025/153) | post-baseline publication | Softmax confidence exits decoder layers on easy tracking frames. | **PARTIAL overall; direct to the easy-frame exit subrelation** | No LR/VC/FM family-point coupling; announced repository was not a verifiable implementation at audit. |
| [BDTrack, arXiv v1 2024 / ESWA 2026](https://arxiv.org/abs/2407.05383v1) | **pre-baseline arXiv v1 (2024-07-07); journal post-baseline** | Dynamic early exit is paired with motion-blur-robust tracking. | **PARTIAL** FM/motion-blur plus conditional depth | Robustness and exit modules are separately learned; announced repository contained no released implementation at audit. |
| [GD early-exit SOT, Neurocomputing 2026](https://doi.org/10.1016/j.neucom.2025.131888) | post-baseline publication | Object-background distinguishability sends easy cases to shallow exits and cluttered/challenging cases deeper. | **DIRECT post-baseline adversary** | Different tracker core; no AsymTrack factorial. |
| [SRRT, TCSVT 2024](https://doi.org/10.1109/TCSVT.2024.3409898) | pre-baseline | Search-region size is regulated under fast motion and distractor risk. | **ADJACENT** condition-specific compute axis | Allocates spatial extent, not backbone capacity. |
| [ARTrack-AC, CVPR 2026; canonical R56](https://openaccess.thecvf.com/content/CVPR2026/html/Lin_Adaptive_Capacity_Autoregressive_Visual_Tracking_CVPR_2026_paper.html) | post-baseline | A temporal difficulty estimator switches low- and high-capacity modes. | **DIRECT/PARTIAL cumulative collision** | Different autoregressive tracker; does not run AsymTrack factorial. |

### Evidence, inference, and unknowns

- **Evidence:** The AsymTrack paper identifies comparatively large LR/VC/FM precision gaps, but does not report paired T→S/B attribute repair or family-point marginal utility. G2 code reconciliation shows T→S and S→B alter different compute axes and are checkpoint/training-confounded.
- **Evidence:** EAST, SiamEE, and DyTrack already implement the general relation “easy frames use less tracking computation; difficult conditions receive more.”
- **Evidence:** DyTrack v1 predates AsymTrack and specifically places FM toward complex routes while VC often remains easy. This directly prevents treating all three proposed attributes as automatically “hard.”
- **Inference:** A controlled AsymTrack experiment could locate where its fixed family points help, but that would be tracker-specific empirical placement inside an occupied mechanism family.
- **Unknown:** The causal gain of search depth alone, search resolution alone, or their interaction on LR/VC/FM versus ordinary frames is not established by the released AsymTrack checkpoints.

## 5. AsymTrack chronology

| date | event | novelty significance |
|---|---|---|
| 2017 | EAST publishes adaptive SOT feature-depth policies. | General conditional-capacity relation is established. |
| 2020–2021 | POST and SiamEE publish per-frame expert switching and Siamese early exits. | Tracker family switching and easy-frame shallow execution are established. |
| 2023 | Aba-ViTrack and SGDViT publish background-aware halting and dynamic token computation. | Condition-aware Transformer computation is established before AsymTrack. |
| 2024-03-26 | DyTrack arXiv v1 becomes public. | Closest pre-baseline collision, including FM/VC route evidence. |
| 2024-06-12 to 2024-07-07 | ABTrack and BDTrack arXiv v1 releases add scene-conditioned block bypass and motion-blur robustness plus dynamic early exit. | Both mechanisms are public before AsymTrack acceptance, although their journal issues are later. |
| 2024 | AVTrack and SRRT add view robustness and fast-motion spatial regulation. | The proposed attributes and allocation axes are already crowded. |
| 2024-12-10 | AsymTrack acceptance date recorded by the official repository News entry. | Baseline comparison point. |
| 2025-03-01 | AsymTrack repository release date recorded in the project evidence. | Public implementation point. |
| 2025-04-11 | AsymTrack formal AAAI publication. | Baseline publication point. |
| 2025–2026 | SGLATrack, FastSeqTrack, GD early-exit SOT, and ARTrack-AC appear; ABTrack/BDTrack receive later peer-reviewed publication. | Post-baseline publications reinforce cumulative collision, while the earlier ABTrack/BDTrack preprints remain labeled separately. |

## 6. AsymTrack surviving distinction and collision

The narrow surviving distinction is an **AsymTrack-preserving measurement**. Raw aligned T/S/B outputs could estimate descriptive family-point interactions separately for LR, VC, FM, and ordinary frames. They cannot identify causal depth or resolution effects because the released variants change multiple axes. Such causal claims would require newly matched factorial variants that separately control search depth, input resolution, relation-token count, head-grid size, training data, and optimization. No located source reports either exact AsymTrack-specific design.

That distinction does not survive HG6 as a material mechanism. Dynamic depth, early exit, adaptive block activation, family switching, and stronger-capacity-on-hard-frames are already direct or cumulative collisions. Adding the AsymTrack name, its asymmetric template cache, or its family checkpoints is architectural placement. Moreover, released T/S/B differences are confounded, and DyTrack's VC result makes the proposed condition grouping itself an empirical hypothesis rather than evidence.

## 7. AsymTrack provisional decision

**CX044 — HG6 FAIL.**

Reason: cumulative/direct novelty collision, led by EAST, pre-baseline DyTrack, and ABTrack, with further collision from SiamEE, POST, AVTrack, Aba-ViTrack, SGLATrack, FastSeqTrack, BDTrack, GD early-exit SOT, SGDViT, and the existing canonical ARTrack-AC source. The exact AsymTrack T/S/B LR/VC/FM factorial remains unmeasured, but its only surviving contribution is tracker-specific empirical placement and diagnostic granularity, not a materially distinct mechanism or coupling. S1–S7, scoring, and shortlist progression remain blocked.

## 8. HiT-DyHiT prior-art table

The anchor is canonical **R49/R50**. G2 establishes that standalone DyHiT shares the first LeViT stage, executes its router every frame, sends Route1 through the small head, and sends Route2 through deeper stages, Bridge, and the large head. The pinned project YAML with THRESHOLD = -9999 forces Route1; it is not evidence that released evaluation calibrates both routes. The router is trained from token-IoU maps rather than paired binary “easy/hard” route regret.

| source | chronology relative to DyHiT | primary-source evidence | collision | exact-gap boundary |
|---|---|---|---|---|
| [Depth-Adaptive Policies, EMMCVPR 2017 / revised proceedings 2018](https://doi.org/10.1007/978-3-319-78199-0_8) | pre-baseline | Learned gates choose tracker depth under tracking-error/computation loss; clutter, scene complexity, motion, and target distinctiveness motivate depth. | **DIRECT** to robustness-conditioned depth | CNN/Siamese core; no HiT Bridge or named routes. |
| [SiamEE, IEEE Access 2021](https://doi.org/10.1109/ACCESS.2021.3119604) | pre-baseline | Fixed score-map thresholds determine early exit in a Siamese tracker. | **PARTIAL** shallow/deep confidence routing | No clutter/distractor conditioning or calibrated robustness; robustness-preserving thresholds remain unresolved. |
| [DyTrack, arXiv v1 2024 / TNNLS 2025](https://arxiv.org/abs/2403.17651v1) | pre-baseline | Learned IoU confidence controls intermediate exits; background and distractors are treated as difficulty factors. | **DIRECT and closest collision** | Different backbone and exits, but same scientific relation. |
| [Aba-ViTrack, ICCV 2023](https://openaccess.thecvf.com/content/ICCV2023/html/Li_Adaptive_and_Background-Aware_Vision_Transformer_for_Real-Time_UAV_Tracking_ICCV_2023_paper.html) | pre-baseline | Learned halting probabilities have a higher prior for background tokens than target tokens. | **PARTIAL** background-token-aware allocation | Does not establish distractor-triggered route selection; token halting is not two-route calibration. |
| [AVTrack, ICML 2024](https://proceedings.mlr.press/v235/li24ax.html) | pre-baseline | The tracker combines adaptive block activation with separately learned view-invariant representations. | **PARTIAL** condition-aware depth and robustness ingredients | No evidence that viewpoint change controls block depth and no HiT route-regret supervision. |
| [ABTrack, arXiv v1 2024 / Pattern Recognition 2025](https://doi.org/10.1016/j.patcog.2024.111278) | pre-baseline arXiv v1; journal May 2025 | Scene-conditioned block bypass differentiates simple backgrounds and clutter. | **DIRECT** scene-conditioned dynamic depth in RGB SOT | Per-block bypass rather than named HiT routes; exact paired-route regret remains absent. |
| [DiffusionTrack, CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Xie_DiffusionTrack_Point_Set_Diffusion_Model_for_Visual_Object_Tracking_CVPR_2024_paper.html) | pre-baseline | The supplement proposes multistage early exit for easy cases; separately, confidence-based hypothesis renewal/voting supports distractor robustness. | **PARTIAL** early exit plus confidence/distractor ingredients | Confidence is not specified as the exit trigger, and released code inspected during audit does not establish executable early stopping. |
| [FastSeqTrack, IJCAI 2025](https://doi.org/10.24963/ijcai.2025/153) | post-baseline | Softmax confidence exits decoder layers on easier frames. | **PARTIAL** confidence early exit | Different sequence decoder and no clutter calibration. |
| [ELGLT, TPAMI 2023](https://doi.org/10.1109/TPAMI.2022.3153645) | pre-baseline | Verification confidence switches next-frame local versus global search. | **PARTIAL** temporal confidence-to-compute coupling | Spatial search mode, not same-frame network depth. |
| [UAST, ICML 2022](https://proceedings.mlr.press/v162/zhang22g.html) | pre-baseline | Estimates tracking uncertainty under ambiguous localization. | **ADJACENT** signal prior | No conditional depth or route selection. |
| UncTrack, canonical **R47/R48** | post-DyHiT receipt; arXiv v1 2025-03-17 | Uncertainty-aware prototype memory supplies a reliability mechanism in tracking. | **ADJACENT** reliability signal | Memory reliability, not HiT route calibration. |
| DAM4SAM, canonical **R29/R30** | pre-receipt; arXiv v1 2024-11-26 | Distractor-aware memory establishes explicit distractor handling in SOT. | **ADJACENT cumulative** | No early-exit router. |
| [Fixing Overconfidence, WACV 2024](https://openaccess.thecvf.com/content/WACV2024/html/Meronen_Fixing_Overconfidence_in_Dynamic_Neural_Networks_WACV_2024_paper.html) | pre-baseline | Calibrates overconfident dynamic-network exit decisions. | **ADJACENT** calibration prior | Classification, not tracking. |
| [Fast yet Safe, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/ea5a63f7ddb82e58623693fd1f4933f7-Abstract-Conference.html) | pre-baseline | Selects exit thresholds with distribution-free risk control against full-model behavior. | **ADJACENT** route-risk prior | Classification; no temporal tracker dependency. |
| [GD early-exit SOT, Neurocomputing 2026](https://doi.org/10.1016/j.neucom.2025.131888) | post-baseline | Object-background distinguishability/entropy sends cluttered cases deeper. | **DIRECT post-baseline adversary** | Different tracker; no HiT paired regret. |
| [UncL-STARK, arXiv 2026](https://arxiv.org/abs/2602.16160) | post-baseline preprint | Uncertainty and temporal feedback select next-frame inference depth. | **PARTIAL post-baseline** | STARK-based; not peer reviewed at cutoff. |
| [Adaptive-depth RGB-T tracking, CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Ding_Adaptive_Depth_Lightweight_RGB-T_Tracking_with_Holistic_Token_Routing_CVPR_2026_paper.html) | post-baseline | Confidence-calibrated early exit halts at the earliest reliable layer. | **PARTIAL post-baseline**; near-direct mechanism | RGB-T modality and different route topology. |
| [MVLM, CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Park_MVLM_Template-Free_Tracking_via_Vision-Language_Margin_Confidence_and_Memory-Gated_Tracking_CVPR_2026_paper.html) | post-baseline | Target-competitor margin and memory gate compact ROI versus global relocalization. | **PARTIAL post-baseline** | Vision-language spatial mode, not depth. |
| [ARTrack-AC, CVPR 2026; canonical R56](https://openaccess.thecvf.com/content/CVPR2026/html/Lin_Adaptive_Capacity_Autoregressive_Visual_Tracking_CVPR_2026_paper.html) | post-baseline | Temporal difficulty controls low/high-capacity execution. | **PARTIAL post-baseline**; near-direct mechanism | Autoregressive tracker; no HiT routes. |

### Evidence, inference, and unknowns

- **Evidence:** DyHiT already contains a learned per-frame router and a tunable threshold controlling Route1 versus Route2.
- **Evidence:** The training target is derived from token-IoU maps; it is not a paired label measuring whether Route2 would correct Route1 on the same frame.
- **Evidence:** Depth-Adaptive Policies and DyTrack predate DyHiT and directly couple tracking difficulty—including clutter/distractors—to shallow/deep compute. Generic calibration and risk-control work predates the baseline as well.
- **Evidence:** The HiT/DyHiT author limitation discusses degradation with distractors/clutter for HiT. It does not establish that DyHiT router errors cause that degradation.
- **Inference:** Forced Route1/Route2 counterfactuals could distinguish false-shallow from wasteful false-deep decisions, but they would diagnose or recalibrate an existing router.
- **Unknown:** The frequency and causal performance cost of distractor/clutter-induced DyHiT misallocation are not established by the pinned release configuration or by the searched literature.

## 9. HiT-DyHiT chronology

| date | event | novelty significance |
|---|---|---|
| 2017 / revised proceedings 2018 | Depth-Adaptive Policies links clutter, motion, distinctiveness, depth, tracking error, and computation. | Exact scientific relation is established before HiT. |
| 2021–2023 | SiamEE, UAST, ELGLT, and Aba-ViTrack add early exits, uncertainty, confidence-switched search, and background-aware halting. | All major signal and allocation ingredients predate DyHiT. |
| 2023 | Static HiT appears at ICCV. | Architectural hierarchy/Bridge baseline exists; not yet the dynamic-route novelty date. |
| 2024-03-26 | DyTrack arXiv v1 becomes public. | Closest direct pre-DyHiT collision: IoU confidence and distractor/background-dependent route difficulty. |
| 2024 | AVTrack, DiffusionTrack, ABTrack preprint, and generic exit-calibration/risk-control papers appear. | Robustness-conditioned allocation and router calibration are crowded before DyHiT's reported submission. |
| 2024-12-27 | IJCV record reports receipt of the DyHiT manuscript. | Conservative baseline manuscript point. |
| 2025-06-23 | DyHiT IJCV article is published online. | Public journal point; the paper itself cites DyTrack. |
| 2025–2026 | FastSeqTrack, GD early-exit SOT, ARTrack-AC, UncL-STARK, adaptive-depth RGB-T tracking, and MVLM appear. | Post-baseline adversaries reinforce cumulative collision without being mislabeled as strict pre-baseline prior art. |

## 10. HiT-DyHiT surviving distinction and collision

The narrow surviving distinction is a **HiT-preserving paired-route measurement**. For a lower-is-better tracking loss L, define descriptive route benefit on frame t as B_t = L(Route1,t) − L(Route2,t): B_t > 0 means Route2 helps, so selecting Route1 is false-shallow; selecting Route2 when B_t ≤ ε is wasteful false-deep. Stratifying those outcomes by independently defined distractor/clutter evidence could audit calibration without replacing the hierarchy, Bridge, routes, or router. This is a definition of the unrun distinction, not a started diagnostic. No located source publishes that exact named experiment.

The scientific mechanism does not survive HG6. Difficulty/reliability-conditioned depth is direct prior art; distractor/clutter difficulty in adaptive tracking is direct or cumulative prior art; uncertainty, target-competitor margins, calibration, and risk-controlled thresholds are occupied ingredients. Swapping the DyHiT router score, recalibrating its threshold, or training it against paired route regret is ordinary tracker-specific placement/combination around a router the baseline already contains. The searched evidence does not support promoting the measurement granularity itself into a new mechanism.

## 11. HiT-DyHiT provisional decision

**CX058 — HG6 FAIL.**

Reason: direct/cumulative collision led by Depth-Adaptive Policies and pre-baseline DyTrack, reinforced by SiamEE, Aba-ViTrack, AVTrack, ABTrack, DiffusionTrack, ELGLT, FastSeqTrack, uncertainty-aware tracking, generic calibration/risk-control, and post-baseline GD early-exit SOT, ARTrack-AC, adaptive-depth RGB-T tracking, UncL-STARK, and MVLM. No single source implements distractor-conditioned paired regret for the named HiT routes, but that surviving difference is diagnostic supervision and implementation placement rather than a materially new coupling. S1–S7, scoring, and shortlist progression remain blocked.

## 12. Proposed source-registration summary

The companion file **screening/codex/2026-08-25_stage3B_hg6_N2_source_candidates.csv** proposes 24 serious sources for Manager review. It deliberately does not edit **references/references.md** or **references/source_manifest.csv**.

| proposed range | focus | registration status |
|---|---|---|
| HG6N2-P01–P06 | foundational adaptive SOT, early exit, expert switching, DyTrack, and ABTrack | proposed only |
| HG6N2-P07–P13 | view/background/layer/motion robustness, sequence exit, and GD early-exit SOT | proposed only |
| HG6N2-P14–P16 | post-baseline uncertainty, calibrated RGB-T depth, and margin/memory gating | proposed only |
| HG6N2-P17–P20 | generic calibration, nested-set uncertainty, joint gates, and risk control | proposed only |
| HG6N2-P21–P24 | local/global confidence, tracking uncertainty, search-region regulation, and dynamic tokens | proposed only |

Already canonical AsymTrack R39/R40, HiT-DyHiT R49/R50, ARTrack-AC R56, UncTrack R47/R48, and DAM4SAM R29/R30 are cited in this report but are not duplicated as proposed registration rows. Source registration remains a Manager action after lane reconciliation.

## 13. Locked non-claims

- The audit does **not** claim that the AsymTrack T/S/B checkpoints form a controlled one-dimensional capacity ladder.
- It does **not** claim LR, VC, and FM are uniformly hard; DyTrack supplies contrary VC evidence.
- It does **not** claim the AsymTrack attribute factorial or HiT forced-route counterfactual has been run.
- It does **not** claim distractors or clutter have been proven to cause DyHiT router misallocation.
- It does **not** conflate DiffusionTrack's confidence-based hypothesis renewal with its separate multistage early-exit proposal, and it does **not** infer executable early stopping from the current repository.
- It does **not** turn post-baseline 2025–2026 sources into strict chronological prior art; they are labeled post-baseline novelty adversaries.
- It does **not** register sources, change canonical references, modify architecture, run diagnostics, assign S1–S7, calculate totals, rank candidates, choose a shortlist, or choose a baseline.
- Manager↔Codex N2 reconciliation and Manager source registration remain pending.

**Independent Codex N2 outcome: CX044 HG6 FAIL; CX058 HG6 FAIL.**
