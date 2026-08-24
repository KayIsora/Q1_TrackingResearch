# Báo cáo Stage 1 broad discovery độc lập — 2026-08-24

**Lane:** Codex independent worker

**Screening date:** 2026-08-24 (Asia/Saigon)

**Scope:** Stage 1 broad discovery + early HG1/HG2/HG3 only
**Không thực hiện:** HG4/HG5/HG6 deep audit, soft score S1–S7, primary shortlist, main-baseline selection, novelty decision, reproduction, proposed architecture.

Báo cáo này phải được đọc cùng [nhật ký 409 truy vấn](./2026-08-24_stage1_query_log.md) và [candidate universe 124 families](./2026-08-24_stage1_candidate_universe.csv). Mọi con số dưới đây được tính lại từ hai artifact đó; không lấy từ search snippet.

## A. Search coverage

- **409 lượt truy vấn**, gồm 405 exact strings duy nhất và 4 exact-string duplicates do các lane làm việc độc lập.
- Lane counts: điều phối/xác minh bổ sung 160; conference 2025 là 102; mechanism-first là 52; conference 2026 + journal là 95.
- Đã cover toàn bộ venue families bắt buộc: CVPR/ICCV/WACV/AAAI/ICLR/ICML/NeurIPS 2025; bổ sung IJCAI và ACM Multimedia 2025; CVPR/AAAI/ICLR/WACV/IJCAI-ECAI 2026 đã có official evidence trước cutoff; ICML/PMLR 2026 được sweep nhưng không giữ eligible generic SOT family.
- Journal sweep: TPAMI, TIP, TMM, TCSVT, IJCV, Pattern Recognition, Neural Networks, Knowledge-Based Systems, Neurocomputing, Image and Vision Computing, cùng các journal liên quan. Crossref chỉ tạo lead; publisher/DOI được dùng để xác minh.
- Đã cover các họ truy vấn bắt buộc: generic SOT/VOT; transformer; efficiency/lightweight; temporal/video-level/long-term; autoregressive; Mamba/state-space; dynamic/adaptive computation; adaptive depth/early exit/layer bypass; token pruning/merging/compression; memory/template efficiency; motion/occlusion/distractor/reliability; edge/embedded; và LaSOT/GOT-10k/TrackingNet anchors.
- Named-title search chỉ dùng sau broad discovery để xác minh publication/HG3.

**Giới hạn diễn giải:** “coverage complete” nghĩa là hoàn tất ma trận venue + mechanism đã khóa, không phải chứng minh toán học rằng toàn bộ literature đã được tìm thấy.

## B. Raw discovery

Raw retained occurrences trước cross-lane dedup: **149**.

| Nguồn độc lập | Retained occurrences |
|---|---:|
| Conference 2025 lane | 40 |
| Mechanism-first/prior-art lane | 39 |
| Conference 2026 + journals lane | 65 |
| Coordinator-only verified additions: MUTrack, RSTrack, JDTrack, FWTrack, DSATrack | 5 |
| **Tổng** | **149** |

Đây là title/family occurrences sau khi từng lane đã collapse URL HTML/PDF/repository trùng nội bộ; không phải số search-engine result hits.

## C. Deduplicated universe

- **124 method families/papers** sau hợp nhất.
- **25 duplicate occurrences** được loại qua **24 duplicate groups**.
- Tiny/Base/Large, FARTrack Tiny/Nano/Pico, các cỡ UETrack/UTPTrack/SpikeTrack và architecture variants của NASTrack không được đếm riêng.
- ArXiv + published version được gộp. Journal extension đại diện family khi có thay đổi/phiên bản chính thức mới hơn nhưng relation được ghi rõ.

Các lineage/dedup quan trọng:

| Family | Quyết định Stage 1 |
|---|---|
| DAM4SAM | CVPR 2025 + IJCV 2026 gộp một family, đại diện bằng IJCV 2026 |
| HiT/DyHiT | ICCV 2023 lineage + IJCV 2025 extension gộp một family, đại diện bằng IJCV 2025 |
| SMTrack | arXiv 2026 + TIP 2026 gộp, đại diện bằng TIP 2026 |
| ARTrack lineage | ARTrack 2023, ARTrackV2 2024, ARPTrack, FARTrack và ARTrack-AC là các papers/method changes khác nhau; giữ riêng nhưng ghi relation |
| SSTrack acronym | SSTrack-AAAI và SSTrack-IJCAI là hai methods khác nhau; không gộp |
| GOT repository | GOT-Edit và GOT-JEPA dùng chung repo nhưng là hai papers/method families; không gộp |

## D. Pool counts

| Pool | Families | Ý nghĩa |
|---|---:|---|
| A | **64** | 2025–2026, potentially generic RGB bbox-SOT |
| B | **43** | task/modality excluded hoặc borderline |
| C | **17** | novelty/prior-art: preprint, outside window hoặc mechanism reference |
| **Tổng** | **124** | — |

Pool không phải ranking. Pool A không đồng nghĩa vượt hard gates; Pool B/C không bị xóa khỏi novelty/reference audit.

## E. Early hard-gate counts

| Gate | PASS | FAIL | PENDING | Tổng |
|---|---:|---:|---:|---:|
| HG1 — publication/year | **106** | **15** | **3** | 124 |
| HG2 — generic RGB SOT fit | **71** | **37** | **16** | 124 |
| HG3 — official source + checkpoint + evaluator | **26** | **18** | **80** | 124 |
| HG4 — RTX 3060 feasibility | 0 | 0 | **124** | 124 |
| HG5 — Jetson Nano plausibility | 0 | 0 | **124** | 124 |
| HG6 — novelty collision | 0 | 0 | **124** | 124 |

Asset fields sau normalization:

- Checkpoint: 26 AVAILABLE, 18 MISSING, 80 PENDING.
- Evaluator: 31 AVAILABLE, 13 MISSING, 80 PENDING.
- HG3 PASS chỉ có 26 vì source + checkpoint + evaluator là phép hội; evaluator có sẵn một mình không đủ.
- Có **19 families** đồng thời HG1/HG2/HG3 PASS. Điều này chỉ cho phép đưa vào audit queue; HG4–HG6 vẫn chặn shortlist.

## F. Scientific-audit queue — không phải shortlist

### F1. Artifact-qualified queue

Bảng dưới đây không xếp hạng và không chọn winner. Mỗi family chỉ được ghi vì HG1/HG2/HG3 đang PASS và có một câu hỏi khoa học đáng deep-audit; không có soft score.

| ID | Candidate | Venue | Vì sao đáng audit sâu |
|---|---|---|---|
| CX007 | [SpikeTrack: A Spike-driven Framework for Efficient Visual Tracking](https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_SpikeTrack_A_Spike-driven_Framework_for_Efficient_Visual_Tracking_CVPR_2026_paper.html) | CVPR 2026 | Spike-driven RGB tracking và compact memory-retrieval; cần audit operator/runtime và tính tương thích GPU thông thường. |
| CX009 | [UETrack: A Unified and Efficient Framework for Single Object Tracking](https://openaccess.thecvf.com/content/CVPR2026/html/Kang_UETrack_A_Unified_and_Efficient_Framework_for_Single_Object_Tracking_CVPR_2026_paper.html) | CVPR 2026 | Token-pooling MoE và adaptive distillation, có RGB mode; cần pin đúng RGB config và artifact commit. |
| CX010 | [UTPTrack: Towards Simple and Unified Token Pruning for Visual Tracking](https://openaccess.thecvf.com/content/CVPR2026/html/Wu_UTPTrack_Towards_Simple_and_Unified_Token_Pruning_for_Visual_Tracking_CVPR_2026_paper.html) | CVPR 2026 | Token pruning trên static/dynamic template và search; liên quan trực tiếp computational redundancy. |
| CX013 | [FARTrack: Fast Autoregressive Visual Tracking with High Performance](https://openreview.net/forum?id=lq7Zfr8kAS) | ICLR 2026 | Autoregressive self-distillation và inter-frame sparsification; giữ như một family bình thường, không mặc định baseline. |
| CX014 | [GOT-Edit: Geometry-Aware Generic Object Tracking via Online Model Editing](https://openreview.net/forum?id=aVa7etWnwF) | ICLR 2026 | Online model editing với geometry suy ra từ RGB; liên quan occlusion/distractor nhưng chi phí geometry còn chưa biết. |
| CX017 | [GOT-JEPA: Generic Object Tracking With Model Adaptation and Occlusion Handling Using Joint-Embedding Predictive Architecture](https://ieeexplore.ieee.org/document/11436011/) | IEEE TCSVT 2026 | Model adaptation và occlusion perception; cần tách rõ relation với GOT-Edit dù dùng chung repository. |
| CX020 | [SAMURAI: Motion-Aware Memory for Training-Free Visual Object Tracking With SAM 2](https://doi.org/10.1109/TIP.2026.3651835) | IEEE TIP 2026 | Motion-aware memory selection trên SAM2; cần kiểm tra dependency/runtime và box-SOT protocol. |
| CX024 | [Distractor-Aware Memory-Based Visual Object Tracking / DAM4SAM](https://link.springer.com/article/10.1007/s11263-026-02790-7) | IJCV 2026 | Distractor-aware dual memory và re-detection; family được đại diện bởi journal extension 2026. |
| CX037 | [Decoupled Spatio-Temporal Consistency Learning for Self-Supervised Tracking (SSTrack-AAAI)](https://ojs.aaai.org/index.php/AAAI/article/view/33155) | AAAI 2025 | Self-supervised spatio-temporal consistency; không được nhầm với SSTrack-IJCAI. |
| CX038 | [Exploring Enhanced Contextual Information for Video-Level Object Tracking (MCITrack)](https://ojs.aaai.org/index.php/AAAI/article/view/32440) | AAAI 2025 | Video-level hidden-state context; phù hợp audit temporal state và memory growth. |
| CX040 | [MambaLCT: Boosting Tracking via Long-term Context State Space Model](https://ojs.aaai.org/index.php/AAAI/article/view/32528) | AAAI 2025 | Long-term state-space context; source, model links và evaluator scripts đã hiện diện nhưng chưa chạy reproduction. |
| CX043 | [SUTrack: Towards Simple and Unified Single Object Tracking](https://ojs.aaai.org/index.php/AAAI/article/view/32223) | AAAI 2025 | Unified tracker có RGB-only route; cần khóa pretraining/inference boundary để so sánh công bằng. |
| CX044 | [Two-stream Beats One-stream: Asymmetric Siamese Network for Efficient Visual Tracking (AsymTrack)](https://ojs.aaai.org/index.php/AAAI/article/view/33191) | AAAI 2025 | Asymmetric Siamese/template-side efficiency; phù hợp audit chi phí thực thi. |
| CX046 | [High-Performance Discriminative Tracking with Spatio-Temporal Template Fusion (JDTrack)](https://dl.acm.org/doi/10.1145/3746027.3755721) | ACM Multimedia 2025 | Discriminative tracking với spatio-temporal template fusion; official repo có models/raw results và evaluator. |
| CX049 | [SPMTrack: Spatio-Temporal Parameter-Efficient Fine-Tuning with Mixture of Experts for Scalable Visual Tracking](https://openaccess.thecvf.com/content/CVPR2025/html/Cai_SPMTrack_Spatio-Temporal_Parameter-Efficient_Fine-Tuning_with_Mixture_of_Experts_for_Scalable_CVPR_2025_paper.html) | CVPR 2025 | Parameter-efficient temporal MoE/fine-tuning; cần pin released model/config khớp paper. |
| CX051 | [UMDATrack: Unified Multi-Domain Adaptive Tracking Under Adverse Weather Conditions](https://openaccess.thecvf.com/content/ICCV2025/html/Yao_UMDATrack_Unified_Multi-Domain_Adaptive_Tracking_Under_Adverse_Weather_Conditions_ICCV_2025_paper.html) | ICCV 2025 | RGB inference với adverse-weather/domain adaptation; cần tách rõ offline adaptation cost. |
| CX053 | [UncTrack: Reliable Visual Object Tracking With Uncertainty-Aware Prototype Memory Network](https://ieeexplore.ieee.org/document/10967033) | IEEE TIP 2025 | Uncertainty-aware localization và prototype memory; liên quan reliability/presence. |
| CX058 | [Exploiting Lightweight Hierarchical ViT and Dynamic Framework for Efficient Visual Tracking / HiT-DyHiT](https://link.springer.com/article/10.1007/s11263-025-02500-9) | IJCV 2025 | Lightweight hierarchical ViT và dynamic routing; 2025 journal extension đại diện family. |
| CX064 | [Improving Accuracy and Generalization for Efficient Visual Tracking (SiamABC)](https://openaccess.thecvf.com/content/WACV2025/html/Zaveri_Improving_Accuracy_and_Generalization_for_Efficient_Visual_Tracking_WACV_2025_paper.html) | WACV 2025 | Efficient Siamese tracking và test-time adaptation; Stage 2 phải pin branch/commit vì repository provenance anomaly. |

### F2. Evidence-blocked/recheck queue

Các family sau **không được nâng lên artifact-qualified**. Chúng được giữ để tránh novelty blindness hoặc để recheck repository state ở Stage sau.

| ID | Candidate | HG3 hiện tại | Việc còn thiếu |
|---|---|---|---|
| CX001 | [MUTrack: A Memory-Aware Unified Representation Framework for Visual Tracking](https://ojs.aaai.org/index.php/AAAI/article/view/38052) | PENDING | Không tìm được official source + checkpoint + evaluator bundle trong pass này; memory mechanism vẫn đáng audit. |
| CX002 | [STDTrack: Exploring Reliable Spatiotemporal Dependencies for Visual Tracking](https://ojs.aaai.org/index.php/AAAI/article/view/37853) | PENDING | Official AAAI publication đã xác minh; official reproducibility bundle chưa khóa. |
| CX006 | [Drift-Resilient Temporal Priors for Visual Tracking / DTPTrack](https://openaccess.thecvf.com/content/CVPR2026/html/Huang_Drift-Resilient_Temporal_Priors_for_Visual_Tracking_CVPR_2026_paper.html) | FAIL | Official repo có code/evaluation nhưng chưa thấy trained tracker checkpoint. |
| CX003 | [Adaptive Capacity Autoregressive Visual Tracking / ARTrack-AC](https://openaccess.thecvf.com/content/CVPR2026/html/Lin_Adaptive_Capacity_Autoregressive_Visual_Tracking_CVPR_2026_paper.html) | FAIL | Paper-linked official repository trả 404 tại cutoff. |
| CX004 | [An Efficient Token Compression Framework for Visual Object Tracking / ETCTrack](https://openaccess.thecvf.com/content/CVPR2026/html/Wu_An_Efficient_Token_Compression_Framework_for_Visual_Object_Tracking_CVPR_2026_paper.html) | FAIL | Official repository mới là placeholder, chưa có full bundle. |
| CX008 | [TGTrack: Temporal Generative Learning for Unified Single Object Tracking](https://openaccess.thecvf.com/content/CVPR2026/html/Geng_TGTrack_Temporal_Generative_Learning_for_Unified_Single_Object_Tracking_CVPR_2026_paper.html) | FAIL | Official repository chỉ có README, chưa có implementation/checkpoint/evaluator. |
| CX023 | [Joint Neural Architecture Search and Token Pruning for Efficient Visual Tracking / NASTrack](https://ijcai-preprints.s3.us-west-1.amazonaws.com/2026/2992.pdf) | FAIL | Có source/evaluator nhưng chưa có trained tracker checkpoint; MAE backbone không thay thế tracker weight. |
| CX061 | [LoRATv2: Enabling Low-Cost Temporal Modeling in One-Stream Trackers](https://papers.nips.cc/paper_files/paper/2025/hash/ad7e42e7b1f638e991d822724969be45-Abstract-Conference.html) | FAIL | Repository ghi model weights/documentation còn forthcoming. |
| CX045 | [Explicit Context Reasoning with Supervision for Visual Tracking (RSTrack)](https://dl.acm.org/doi/10.1145/3746027.3755282) | FAIL | Official repository chỉ có README một commit. |
| CX029 | [LoongTrack: Exploring long-sequence modeling for visual tracking](https://www.sciencedirect.com/science/article/pii/S0893608026002868) | PENDING | Publisher record có nhưng artifact bundle chưa truy vết đủ. |
| CX032 | [EME: Out-of-view handling in visual object tracking via edge-aware motion estimation](https://doi.org/10.1016/j.patcog.2026.114671) | PENDING | EME trực tiếp liên quan OOV, nhưng artifact bundle chưa xác minh. |
| CX012 | [Object Drift Verification Network for long-term visual tracking](https://www.sciencedirect.com/science/article/pii/S1051200426002034) | PENDING | Drift verification/re-detection liên quan failure modes; artifact bundle chưa xác minh. |

## G. Exclusions và borderline

| Nhóm/candidate đại diện | Gate | Lý do | Giữ làm novelty/mechanism reference? |
|---|---|---|---|
| DUTrack, MambaVLT, MVLM, language-description tracker | HG2 FAIL | Bắt buộc language hoặc interface không phải initial bbox RGB Core | Có |
| Adaptive Depth RGB-T, MOSSTrack, STTrack, SpikeFET, MoKA-HP | HG2 FAIL | Bắt buộc thermal/event/RGB-X | Có |
| GSOT3D, TrackAny3D, ChronoTrack, CompTrack, UAWTrack | HG2 FAIL | 3D point cloud/3D box task | Có |
| MOTE, S2-Track | HG2 FAIL | MOT/3D-MOT, metrics và task khác SOT | Có |
| TTAPFormer, TrackingWorld, point/pixel tracking works | HG2 FAIL | Point/dense/world-centric tracking, output contract khác | Có |
| OA-VAT | HG2 FAIL | Active camera planning/control là task khác passive moving-camera benchmark | Có |
| CAT click-and-track | HG2 FAIL | Defining initialization là click, không phải first-frame bbox | Có |
| LVPTrack, SGLATrack, ORTrack, LETrack, EATrack, TATrack, PTDT, FWTrack, DSATrack | HG2 PENDING | RGB bbox tracking nhưng UAV/domain specialization; chưa chứng minh generic Core fit | Có |
| ARTrack/ARTrackV2/RTracker/DeTrack và 2023–2024 works | HG1 FAIL | Ngoài main-baseline window; vẫn là lineage/prior art | Có |
| STARTrack, SAMITE, Uni-MDTrack, VCoT, SOTFormer, EdgeDAM và arXiv-only leads | HG1 FAIL | Preprint/submission-only tại cutoff | Có |
| FastSeqTrack, RSTrack, ARTrack-AC, ETCTrack, TGTrack | HG3 FAIL | Official repo mismatch/empty/404/placeholder hoặc thiếu mandatory artifact | Có, nhưng không reproducible baseline hiện tại |

## H. Uncertainties

1. **Publication status:** SENTRY (proceedings chưa xác minh), một Pattern Recognition online-first record và EnTeR-Track có HG1 PENDING; không biến acceptance claim/future issue thành published paper.
2. **Official bundle chưa tìm thấy:** MUTrack, STDTrack, DreamTrack, MIMTrack, WDT và nhiều journal records giữ HG3 PENDING, không diễn giải “không tìm thấy” thành “chắc chắn không tồn tại”.
3. **Checkpoint semantics:** MAE/DeiT/SAM2 backbone weight không tự động là trained tracker checkpoint. Đây là lý do DSATrack/NASTrack không HG3 PASS nếu thiếu method checkpoint.
4. **Repository volatility:** ARTrack-AC URL 404; LoRATv2/ETCTrack/TGTrack có forthcoming/placeholder state; phải re-audit theo ngày.
5. **Repository provenance:** FastSeqTrack paper-linked repo hiện chứa unrelated Google ViT README. SiamABC implementation nằm ở `master`, trong khi current default branch trỏ nội dung AEVT khác; Stage 2 phải pin branch + commit.
6. **Unified RGB path:** SUTrack, UETrack, UTPTrack, TGTrack cần pin RGB-only config, training data và multimodal-pretraining boundary trước so sánh.
7. **Task fit:** UAV-specialized RGB methods giữ HG2 PENDING thay vì ép PASS/FAIL khi chưa có generic benchmark/config evidence.
8. **Hardware:** không có HG4/HG5 PASS. Desktop GPU/CPU FPS, FLOPs, params, Jetson AGX/NX/Orin hoặc “edge” claim không phải Jetson Nano evidence.
9. **Benchmark numbers:** Stage 1 không dùng author-reported benchmark scores để xếp hạng; evaluator/protocol presence chỉ phục vụ HG3.

## I. Git provenance

- Repository branch khi bắt đầu: `main`.
- Synced base HEAD trước Stage 1: `4a6b8e250d9f483a143eaf1efad61a35de47fdc5`.
- Chỉ tạo ba files trong `screening/codex/`:
  - `2026-08-24_stage1_query_log.md`
  - `2026-08-24_stage1_candidate_universe.csv`
  - `2026-08-24_stage1_discovery_report.md`
- Không đọc nội dung `screening/manager/` trước independent commit; không sửa canonical matrix, README, RULE, docs, references hoặc evidence ledger.
- Stage-1 commit SHA được báo trong worker handoff sau khi commit. Một file nằm trong commit không thể nhúng chính hash của commit đó mà không làm hash thay đổi; có thể resolve bằng:
  `git log -1 --format=%H -- screening/codex/2026-08-24_stage1_discovery_report.md`

## J. Final status

- **STAGE 1 BROAD DISCOVERY: COMPLETE**
- **EARLY HG1-HG2-HG3: COMPLETE**
- **SOFT SCORING: NOT STARTED**
- **PRIMARY SHORTLIST: NONE**
- **MAIN BASELINE: NONE**
- **PROPOSED ARCHITECTURE: NONE**

Điểm dừng bắt buộc: chờ Manager reconciliation instruction; không tự chuyển sang HG4/HG5/HG6 deep audit, soft scoring, shortlist, reproduction hoặc architecture design.
