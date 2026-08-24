# Nhật ký truy vấn Stage 1 độc lập — 2026-08-24

**Phạm vi:** broad discovery 2025–2026 và prior-art 2023–2026 cho generic RGB bounding-box single-object tracking (SOT), cùng các boundary records về modality/task.

**Ngày khóa sổ:** 2026-08-24 (Asia/Saigon).
**Trạng thái:** nhật ký Stage 1; không phải shortlist, baseline, novelty decision hay proposed architecture.

## 1. Quy tắc ghi nhận

- Mỗi dòng ở Phần 5 là một chuỗi truy vấn đã gửi nguyên văn. Nguồn là công cụ web search, trừ 11 endpoint Crossref được ghi rõ là API.
- Search snippet, Crossref và trang tổng hợp chỉ tạo lead. Publication/task/code facts trong candidate matrix được đối chiếu lại bằng official proceedings, official paper/publisher page, official project hoặc official author repository.
- Direct URL open, mở PDF, inspect repository và lệnh read-only như `git ls-remote` không được tính là “search query”.
- Tổng lượt truy vấn thực thi: **409**.
- Số chuỗi truy vấn duy nhất theo exact-string: **405**.
- Exact-string duplicates giữa các lane: **4**. Chúng được giữ trong log vì các lane làm việc độc lập.
- “Raw discovery” trong báo cáo chính là retained title/family occurrences sau khi từng lane đã loại URL/PDF/HTML lặp nội bộ; không phải số search-engine hits mà công cụ không cung cấp ổn định.

## 2. Coverage theo venue

| Venue family | Truy vấn | Families được giữ trong universe | Nguồn xác minh/ghi chú |
|---|---|---:|---|
| CVPR 2025 | Có | 10 | CVF Open Access |
| ICCV 2025 | Có | 6 | CVF Open Access |
| WACV 2025 | Có | 1 | CVF Open Access |
| AAAI 2025 | Có | 11 | AAAI OJS |
| ICLR 2025 | Có | 1 | OpenReview; không có bài generic RGB SOT accepted được giữ, 1 submission ở Pool C |
| ICML 2025 | Có | 2 | PMLR; chỉ giữ 2 boundary records |
| NeurIPS 2025 | Có | 6 | NeurIPS Proceedings/OpenReview |
| IJCAI 2025 | Có | 4 | IJCAI Proceedings |
| ACM Multimedia 2025 | Có | 2 | ACM DOI + author paper/repository |
| CVPR + Findings 2026 | Có | 19 | CVF Open Access |
| AAAI 2026 | Có | 5 | AAAI OJS |
| ICLR 2026 | Có | 3 | OpenReview venue decision |
| WACV + Workshops 2026 | Có | 3 | CVF Open Access |
| IJCAI-ECAI 2026 | Có | 1 | Official accepted list/preprint |
| ICML 2026 | Có | 0 | PMLR sweep; 0 eligible/adjacent family retained |
| IEEE TPAMI | Có | 1 | Crossref lead → IEEE DOI/page verification |
| IEEE TIP | Có | 3 | Crossref lead → IEEE DOI/page verification |
| IEEE TMM | Có | 1 | Crossref lead → IEEE DOI/page verification |
| IEEE TCSVT | Có | 5 | Crossref lead → IEEE DOI/page verification |
| IJCV | Có | 2 | Springer official pages |
| Pattern Recognition | Có | 6 | ScienceDirect/DOI |
| Neural Networks | Có | 2 | ScienceDirect/DOI |
| Knowledge-Based Systems | Có | 4 | ScienceDirect/DOI |
| Neurocomputing | Có | 5 | ScienceDirect/DOI |
| Image and Vision Computing | Có | 2 | ScienceDirect/DOI |
| Other related journals | Có | 5 | Publisher/DOI; không tự gán quartile |

Các venue 2025 bắt buộc đều được truy vấn. Với 2026, chỉ các record có official acceptance/publication evidence trước hoặc đúng ngày khóa sổ mới có thể HG1 PASS; submission/under-review được giữ ở Pool C. Không suy diễn kết quả âm của một query thành tuyên bố venue hoàn toàn không có bài liên quan.

## 3. Coverage theo query family

| Họ truy vấn bắt buộc | Coverage |
|---|---|
| single object tracking 2025 / 2026 | Có |
| visual object tracking 2025 / 2026 | Có |
| transformer / efficient / lightweight tracking | Có |
| temporal / video-level / long-term tracking | Có |
| autoregressive tracking | Có |
| Mamba / state-space tracking | Có |
| dynamic/adaptive computation | Có |
| adaptive depth / early exit / layer pruning-bypass | Có |
| token pruning / merging / compression | Có |
| memory-efficient / template-efficient tracking | Có |
| motion-aware / occlusion-robust / distractor-robust / reliability-aware | Có |
| edge / embedded tracking | Có |
| benchmark anchors: LaSOT / GOT-10k / TrackingNet | Có |

Các named-title queries chỉ được dùng sau khi broad/mechanism search làm xuất hiện lead, nhằm xác minh publication hoặc HG3; chúng không thay thế broad discovery.

## 4. Direct-access audit không tính vào query count

- Venue-index attempts: `https://openaccess.thecvf.com/CVPR2025?day=all`, `https://openaccess.thecvf.com/ICCV2025?day=all`, `https://openaccess.thecvf.com/WACV2025?day=all`, `https://openaccess.thecvf.com/CVPR2026?day=all`.
- Các venue-index trên trả HTTP 403 trong browsing layer; fallback là site-scoped search rồi mở official paper page/PDF cụ thể.
- Một số direct OpenReview API/ACM DL requests cũng bị challenge/403. Chúng không được dùng như bằng chứng âm; official DOI, accepted-paper page, proceedings PDF hoặc author-linked repository được kiểm tra thay thế khi có.
- Repository existence không đủ cho HG3. Mỗi HG3 PASS đòi đồng thời source, trained tracker checkpoint (hoặc dependency checkpoint phù hợp với method training-free), và usable evaluation script/protocol.

## 5. Exact query ledger

### Điều phối và xác minh bổ sung — 160 lượt

| ID | Source | Exact query string |
|---|---|---|
| Q001 | Web search | `site:openaccess.thecvf.com/content/CVPR2025 "single object tracking"` |
| Q002 | Web search | `site:openaccess.thecvf.com/content/ICCV2025 "visual object tracking"` |
| Q003 | Web search | `site:openaccess.thecvf.com/content/WACV2025 "visual tracking"` |
| Q004 | Web search | `site:ojs.aaai.org/index.php/AAAI 2025 "single object tracking"` |
| Q005 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html tracker "LaSOT"` |
| Q006 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html "TrackingNet" tracker` |
| Q007 | Web search | `site:openaccess.thecvf.com/content/ICCV2025/html tracker "LaSOT"` |
| Q008 | Web search | `site:openaccess.thecvf.com/content/ICCV2025/html "single object" tracking` |
| Q009 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "single object tracking" -3D -language` |
| Q010 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html tracker LaSOT GOT-10k TrackingNet` |
| Q011 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "visual object tracking"` |
| Q012 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html efficient tracker` |
| Q013 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html ARPTrack` |
| Q014 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html SPMTrack` |
| Q015 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view MCITrack 2025` |
| Q016 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view TemTrack 2025` |
| Q017 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view 2025 "LaSOT" "GOT-10K"` |
| Q018 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view 2025 "TrackingNet" "visual tracking"` |
| Q019 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view 2025 tracker template search region` |
| Q020 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view 2025 "object tracking" Mamba` |
| Q021 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view 2026 "LaSOT" "GOT10k"` |
| Q022 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view 2026 "visual tracking" "TrackingNet"` |
| Q023 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view 2026 "single object tracking" RGB` |
| Q024 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view 2026 tracker template search` |
| Q025 | Web search | `site:openreview.net/forum ICLR 2025 "visual tracking" LaSOT` |
| Q026 | Web search | `site:openreview.net/forum ICLR 2025 "single object tracking"` |
| Q027 | Web search | `site:openreview.net/forum ICLR 2026 "visual tracking" LaSOT` |
| Q028 | Web search | `site:openreview.net/forum ICLR 2026 "single object tracking"` |
| Q029 | Web search | `site:openreview.net/forum "ICLR 2026 poster" "object tracking"` |
| Q030 | Web search | `site:openreview.net/forum "ICLR 2026 Conference" "autoregressive visual tracking"` |
| Q031 | Web search | `site:openreview.net/forum "ICLR 2026" "LaSOT" "TrackingNet"` |
| Q032 | Web search | `site:openreview.net/forum "ICLR 2026" tracker "GOT-10k"` |
| Q033 | Web search | `site:openreview.net/forum "Fast Autoregressive Visual Tracking with High Performance"` |
| Q034 | Web search | `site:openreview.net/forum "STARTrack" visual tracking ICLR 2026` |
| Q035 | Web search | `site:openreview.net/forum "Uni-MDTrack" ICLR 2026` |
| Q036 | Web search | `site:openreview.net/forum "GOT-Edit" code GitHub` |
| Q037 | Web search | `site:proceedings.mlr.press/v267 "object tracking"` |
| Q038 | Web search | `site:proceedings.mlr.press/v267 "single object" tracking` |
| Q039 | Web search | `site:openreview.net/forum "NeurIPS 2025 poster" "single object tracking"` |
| Q040 | Web search | `site:openreview.net/forum "NeurIPS 2025" "LaSOT" tracker` |
| Q041 | Web search | `site:openaccess.thecvf.com/content/WACV2025/html "single object tracking"` |
| Q042 | Web search | `site:openaccess.thecvf.com/content/WACV2025/html tracker LaSOT GOT-10k` |
| Q043 | Web search | `site:openaccess.thecvf.com/content/WACV2025/html "efficient visual tracking"` |
| Q044 | Web search | `site:openaccess.thecvf.com/content/WACV2025/html Siamese tracker` |
| Q045 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html "visual tracking" -"language" -3D` |
| Q046 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html "object tracking" "GOT-10k"` |
| Q047 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html tracking "LaSOText"` |
| Q048 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html "temporal" tracker LaSOT` |
| Q049 | Web search | `DreamTrack Dreaming the Future multimodal visual object tracking official GitHub` |
| Q050 | Web search | `ARPTrack Autoregressive Sequential Pretraining visual tracking official GitHub` |
| Q051 | Web search | `SPMTrack official GitHub checkpoint evaluation` |
| Q052 | Web search | `MCITrack Exploring Enhanced Contextual Information official GitHub` |
| Q053 | Web search | `TemTrack Robust Tracking Mamba Context-aware Token Learning GitHub` |
| Q054 | Web search | `LMTrack Less Is More Token Context-Aware Learning Object Tracking GitHub` |
| Q055 | Web search | `MambaLCT Boosting Tracking Long-term Context GitHub` |
| Q056 | Web search | `MIMTrack In-Context Tracking Masked Image Modeling GitHub` |
| Q057 | Web search | `SSTrack Decoupled Spatio-Temporal Consistency Learning official GitHub AAAI 2025` |
| Q058 | Web search | `SUTrack Towards Simple Unified Single Object Tracking official GitHub AAAI 2025` |
| Q059 | Web search | `SiamABC Improving Accuracy Generalization Efficient Visual Tracking official GitHub` |
| Q060 | Web search | `DreamTrack CVPR 2025 official code GitHub tracker` |
| Q061 | Web search | `2025 visual object tracking LaSOT GOT-10k TrackingNet official code CVPR AAAI ACM MM` |
| Q062 | Web search | `2025 tracker LaSOT GOT-10K official GitHub "visual tracking"` |
| Q063 | Web search | `2025 "single object tracking" LaSOT GOT-10K conference` |
| Q064 | Web search | `2025 efficient visual tracker AVisT LaSOT GOT-10K` |
| Q065 | Web search | `"FWTrack" visual tracking paper venue` |
| Q066 | Web search | `"DTPTrack" "Drift-Resilient Temporal Priors" CVPR 2026` |
| Q067 | Web search | `"JDTrack" "High-Performance Discriminative Tracking" ACM MM 2025` |
| Q068 | Web search | `"RSTrack" "Explicit Context Reasoning" ACM MM 2025` |
| Q069 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html tracking LaSOT GOT-10K "source code"` |
| Q070 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "visual tracking" "LaSOT"` |
| Q071 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "single object tracking"` |
| Q072 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html tracker "TrackingNet"` |
| Q073 | Web search | `"Adaptive Capacity Autoregressive Visual Tracking" CVPR 2026 GitHub` |
| Q074 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "Adaptive Capacity Autoregressive Visual Tracking"` |
| Q075 | Web search | `"UTPTrack" CVPR 2026 GitHub` |
| Q076 | Web search | `"TGTrack" CVPR 2026 GitHub` |
| Q077 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "TGTrack: Temporal Generative Learning"` |
| Q078 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "SpikeTrack: A Spike-driven Framework"` |
| Q079 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "Rethinking Occlusion Modeling for UAV Tracking"` |
| Q080 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "Toward Low-Cost yet Effective Temporal Learning"` |
| Q081 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "UTPTrack"` |
| Q082 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "Dual-branch Distilled Transformer for Efficient Asymmetric UAV Tracking"` |
| Q083 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "Adaptive Depth Lightweight RGB-T Tracking"` |
| Q084 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "Interactive Tracking: A Human-in-the-Loop"` |
| Q085 | Web search | `github ARTrackAC MIV XJTU` |
| Q086 | Web search | `github FARTrack MIV-XJTU checkpoints evaluation` |
| Q087 | Web search | `github UETrack checkpoints evaluation kangben258` |
| Q088 | Web search | `github TGTrack wtg1 checkpoints evaluation` |
| Q089 | Web search | `site:github.com/EIT-NLP/UTPTrack evaluation UTPTrack checkpoint` |
| Q090 | Web search | `site:github.com/EIT-NLP/UTPTrack "python" "evaluation"` |
| Q091 | Web search | `site:github.com/wtg1/TGTrack checkpoint evaluation` |
| Q092 | Web search | `site:github.com/PJD-WJ/ETCTrack checkpoint evaluation` |
| Q093 | Web search | `site:huggingface.co DTPTrack model checkpoint` |
| Q094 | Web search | `site:github.com/NorahGreen/DTPTrack "pretrained"` |
| Q095 | Web search | `site:github.com/NorahGreen/DTPTrack "download" "weight"` |
| Q096 | Web search | `"DTPTrack" checkpoint model` |
| Q097 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html "visual tracking" LaSOT GOT-10K` |
| Q098 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html "UAV Tracking"` |
| Q099 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html "Vision-Language Tracking"` |
| Q100 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html "object tracking" "TrackingNet"` |
| Q101 | Web search | `site:openaccess.thecvf.com/content/ICCV2025/html "LaSOT" "GOT-10k" tracking` |
| Q102 | Web search | `site:openaccess.thecvf.com/content/ICCV2025/html "visual object tracking"` |
| Q103 | Web search | `site:openaccess.thecvf.com/content/ICCV2025/html "single object tracking" -3D` |
| Q104 | Web search | `site:openaccess.thecvf.com/content/ICCV2025/html tracker TrackingNet` |
| Q105 | Web search | `UMDATrack Unified Multi-Domain Adaptive Tracking official GitHub` |
| Q106 | Web search | `RICE Region-based Cluster Discrimination visual tracking official GitHub ICCV 2025` |
| Q107 | Web search | `Learning Occlusion-Robust Vision Transformers real-time UAV tracking code GitHub` |
| Q108 | Web search | `SGLATrack official GitHub checkpoints evaluation` |
| Q109 | Web search | `site:openreview.net/forum "LoRATv2: Enabling Low-Cost Temporal Modeling"` |
| Q110 | Web search | `site:openreview.net/forum "DSATrack" NeurIPS 2025` |
| Q111 | Web search | `"LoRATv2" official GitHub checkpoint evaluation` |
| Q112 | Web search | `"Dynamic Semantic-Aware Correlation Modeling for UAV Tracking"` |
| Q113 | Web search | `site:github.com/LitingLin/LoRATv2 checkpoints evaluation` |
| Q114 | Web search | `github LitingLin LoRATv2 model weights` |
| Q115 | Web search | `site:huggingface.co LoRATv2 checkpoint` |
| Q116 | Web search | `"LoRATv2" "Evaluation" GitHub` |
| Q117 | Web search | `2025 IEEE TPAMI visual object tracking LaSOT GOT-10K tracker` |
| Q118 | Web search | `2025 IEEE TCSVT visual tracking LaSOT GOT-10K tracker` |
| Q119 | Web search | `2025 IEEE TMM visual object tracking LaSOT GOT-10K` |
| Q120 | Web search | `2026 journal visual object tracking LaSOT GOT-10K` |
| Q121 | Web search | `"Sample-interval Scheduling for Lightweight Visual Object Tracking" GitHub` |
| Q122 | Web search | `"SSTrack" "Sample-interval Scheduling" code` |
| Q123 | Web search | `site:github.com "Sample-interval Scheduling" tracker` |
| Q124 | Web search | `site:ijcai.org/proceedings/2025 "visual tracking"` |
| Q125 | Web search | `site:ijcai.org/proceedings/2025 "Exploring Efficient and Effective Sequence Learning for Visual Object Tracking"` |
| Q126 | Web search | `"Exploring Efficient and Effective Sequence Learning for Visual Object Tracking"` |
| Q127 | Web search | `site:github.com/vision4drones/FastSeqTrack checkpoint evaluation` |
| Q128 | Web search | `site:ijcai.org/proceedings/2025 tracker "GOT-10k"` |
| Q129 | Web search | `"MIMTrack" "In-Context Tracking" GitHub` |
| Q130 | Web search | `"MIMTrack: In-Context Tracking via Masked Image Modeling" code` |
| Q131 | Web search | `"DreamTrack" "Dreaming the Future" GitHub code` |
| Q132 | Web search | `"Autoregressive Sequential Pretraining" GitHub ARPTrack code` |
| Q133 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view "Two-stream Beats One-stream"` |
| Q134 | Web search | `"Two-stream Beats One-stream: Asymmetric Siamese Network for Efficient Visual Tracking" GitHub` |
| Q135 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view "Exploiting Multimodal Spatial-temporal Patterns for Video Object Tracking"` |
| Q136 | Web search | `"Exploiting Multimodal Spatial-temporal Patterns" tracking GitHub` |
| Q137 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view 2026 "visual tracking" LaSOT` |
| Q138 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view 2026 "object tracking" GOT-10K` |
| Q139 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view 2026 "single object tracking"` |
| Q140 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view 2026 tracker "TrackingNet"` |
| Q141 | Web search | `"MUTrack: A Lightweight Multi-Scale Unified Transformer" official GitHub checkpoint evaluation AAAI 2026` |
| Q142 | Web search | `"Exploring Reliable Spatiotemporal Dependencies for Efficient Visual Tracking" official GitHub checkpoint evaluation` |
| Q143 | Web search | `"SpikeTrack: A Spike-driven Framework for Efficient Visual Tracking" official GitHub checkpoint evaluation` |
| Q144 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view "MUTrack" 2026` |
| Q145 | Web search | `"MUTrack: A Memory-Aware Unified Representation Framework" GitHub` |
| Q146 | Web search | `site:github.com "MUTrack" "Memory-Aware Unified Representation"` |
| Q147 | Web search | `site:github.com "STDTrack" "Reliable Spatiotemporal Dependencies"` |
| Q148 | Web search | `"STDTrack" GitHub checkpoint GOT-10k LaSOT` |
| Q149 | Web search | `site:dl.acm.org/doi "RSTrack: Explicit Context Reasoning for Visual Tracking"` |
| Q150 | Web search | `site:dl.acm.org/doi "JDTrack" visual tracking ACM Multimedia 2025` |
| Q151 | Web search | `site:ieeexplore.ieee.org/document "FWTrack" "Visual Tracking"` |
| Q152 | Web search | `site:openreview.net/forum "DSATrack" "NeurIPS 2025"` |
| Q153 | Web search | `"JDTrack: A High-Performance Discriminative Tracker"` |
| Q154 | Web search | `"Explicit Context Reasoning with Supervision for Visual Tracking" ACM Multimedia 2025 DOI` |
| Q155 | Web search | `"Hierarchical Spatial-Temporal UAV Tracking with Three-Dimensional Wavelets" DOI` |
| Q156 | Web search | `"Dynamic Semantic-Aware Correlation Modeling for UAV Tracking" NeurIPS 2025` |
| Q157 | Web search | `"High-Performance Discriminative Tracking with Spatio-Temporal Template Fusion" DOI` |
| Q158 | Web search | `site:dl.acm.org "High-Performance Discriminative Tracking"` |
| Q159 | Web search | `site:dblp.org "High-Performance Discriminative Tracking with Spatio-Temporal"` |
| Q160 | Web search | `"JDTrack" "ACM Multimedia 2025"` |

### Rà soát venue hội nghị 2025 — 102 lượt

| ID | Source | Exact query string |
|---|---|---|
| Q161 | Web search | `site:openaccess.thecvf.com/content/CVPR2025 "single object tracking"` |
| Q162 | Web search | `site:openaccess.thecvf.com/content/CVPR2025 visual tracking LaSOT GOT-10k TrackingNet` |
| Q163 | Web search | `site:openaccess.thecvf.com/content/ICCV2025 "single object tracking"` |
| Q164 | Web search | `site:openaccess.thecvf.com/content/ICCV2025 visual tracking LaSOT GOT-10k TrackingNet` |
| Q165 | Web search | `site:openaccess.thecvf.com/content/WACV2025 "single object tracking"` |
| Q166 | Web search | `site:openaccess.thecvf.com/content/WACV2025 visual tracking LaSOT GOT-10k TrackingNet` |
| Q167 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view "single object tracking" 2025` |
| Q168 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view visual tracking LaSOT GOT-10k 2025` |
| Q169 | Web search | `site:openreview.net/forum ICLR 2025 "single object tracking"` |
| Q170 | Web search | `site:openreview.net/forum ICLR 2025 visual tracking LaSOT GOT-10k TrackingNet` |
| Q171 | Web search | `site:proceedings.mlr.press/v267 "single object tracking"` |
| Q172 | Web search | `site:proceedings.mlr.press/v267 visual tracking LaSOT GOT-10k TrackingNet` |
| Q173 | Web search | `site:proceedings.neurips.cc/paper_files/paper/2025 "single object tracking"` |
| Q174 | Web search | `site:proceedings.neurips.cc/paper_files/paper/2025 visual tracking LaSOT GOT-10k TrackingNet` |
| Q175 | Web search | `site:openreview.net/forum "NeurIPS 2025" "single object tracking"` |
| Q176 | Web search | `site:openreview.net/forum "NeurIPS 2025" visual tracking LaSOT GOT-10k` |
| Q177 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "TrackingNet" "2025" "visual tracking"` |
| Q178 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "LaSOT" "GOT-10K" "Vol. 39"` |
| Q179 | Web search | `site:openreview.net/forum?id= "ICLR 2025" "visual object tracking"` |
| Q180 | Web search | `site:proceedings.mlr.press/v267 "object tracking" video` |
| Q181 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "MambaLCT"` |
| Q182 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "TemTrack"` |
| Q183 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "MCITrack"` |
| Q184 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "visual tracking" "2025" "LaSOT"` |
| Q185 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html/ "visual object tracking"` |
| Q186 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html/ "GOT-10k" "TrackingNet"` |
| Q187 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html/ tracking "LaSOT"` |
| Q188 | Web search | `site:openaccess.thecvf.com/content/CVPR2025/html/ "single object" tracking` |
| Q189 | Web search | `site:openaccess.thecvf.com/content/CVPR2025 "SPMTrack"` |
| Q190 | Web search | `site:openaccess.thecvf.com/content/CVPR2025 "MambaVLT"` |
| Q191 | Web search | `site:openaccess.thecvf.com/content/CVPR2025 "SAM2" "visual object tracking"` |
| Q192 | Web search | `site:openaccess.thecvf.com/content/CVPR2025 "tracking" "GOT-10k" "LaSOText"` |
| Q193 | Web search | `site:openaccess.thecvf.com/content/ICCV2025/html/ "visual object tracking"` |
| Q194 | Web search | `site:openaccess.thecvf.com/content/ICCV2025/html/ "GOT-10k" "TrackingNet"` |
| Q195 | Web search | `site:openaccess.thecvf.com/content/ICCV2025/html/ tracking "LaSOT"` |
| Q196 | Web search | `site:openaccess.thecvf.com/content/ICCV2025/html/ "single object tracking"` |
| Q197 | Web search | `site:openaccess.thecvf.com/content/WACV2025/html/ "visual object tracking"` |
| Q198 | Web search | `site:openaccess.thecvf.com/content/WACV2025/html/ "GOT-10k" "TrackingNet"` |
| Q199 | Web search | `site:openaccess.thecvf.com/content/WACV2025/html/ tracking "LaSOT"` |
| Q200 | Web search | `site:openaccess.thecvf.com/content/WACV2025/html/ "single object tracking"` |
| Q201 | Web search | `site:openaccess.thecvf.com/content/WACV2025/html/ "Improving Accuracy and Generalization for Efficient Visual Tracking"` |
| Q202 | Web search | `site:openaccess.thecvf.com/content/WACV2025 "efficient visual tracking" "Jetson Nano"` |
| Q203 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "GOT-10K" "TrackingNet" "2025"` |
| Q204 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "visual object tracking" "Published" "2025-04-11"` |
| Q205 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "efficient visual tracking" "2025"` |
| Q206 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "temporal" "object tracking" "LaSOT"` |
| Q207 | Web search | `site:openreview.net/forum?id= "DeTrack: In-model Latent Denoising Learning for Visual Object Tracking"` |
| Q208 | Web search | `site:openreview.net/forum?id= "ICLR 2025" "DeTrack"` |
| Q209 | Web search | `site:openreview.net/forum?id= "ICLR 2025" tracking "LaSOT" "GOT-10K"` |
| Q210 | Web search | `site:openreview.net/forum?id= "ICLR 2025 Poster" "object tracking"` |
| Q211 | Web search | `site:openreview.net/forum?id= "General Compression Framework for Efficient Transformer Object Tracking"` |
| Q212 | Web search | `"General Compression Framework for Efficient Transformer Object Tracking" code` |
| Q213 | Web search | `site:openreview.net "ICLR 2025 Poster" "General Compression Framework"` |
| Q214 | Web search | `ARPTrack CVPR 2025 official GitHub` |
| Q215 | Web search | `DreamTrack CVPR 2025 official GitHub` |
| Q216 | Web search | `SPMTrack CVPR 2025 official GitHub` |
| Q217 | Web search | `DAM4SAM CVPR 2025 official GitHub` |
| Q218 | Web search | `"Autoregressive Sequential Pretraining for Visual Tracking" GitHub` |
| Q219 | Web search | `"Dreaming the Future for Multimodal Visual Object Tracking" GitHub` |
| Q220 | Web search | `"SUTrack: Towards Simple and Unified Single Object Tracking" GitHub` |
| Q221 | Web search | `"Decoupled Spatio-Temporal Consistency Learning for Self-Supervised Tracking" GitHub` |
| Q222 | Web search | `site:github.com "DreamTrack: Dreaming the Future"` |
| Q223 | Web search | `site:github.com "Autoregressive Sequential Pretraining" tracking` |
| Q224 | Web search | `site:github.com/GXNU-ZhongLab "Less Is More: Token Context-Aware Learning"` |
| Q225 | Web search | `site:github.com "Exploring Enhanced Contextual Information for Video-Level Object Tracking"` |
| Q226 | Web search | `"MambaLCT: Boosting Tracking" GitHub` |
| Q227 | Web search | `"Robust Tracking via Mamba-based Context-aware Token Learning" GitHub` |
| Q228 | Web search | `"Two-stream Beats One-stream" GitHub AsymTrack` |
| Q229 | Web search | `"Improving Accuracy and Generalization for Efficient Visual Tracking" GitHub SiamABC` |
| Q230 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "MIMTrack: In-Context Tracking via Masked Image Modeling"` |
| Q231 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "Exploiting Multimodal Spatial-temporal Patterns for Video Object Tracking"` |
| Q232 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "single object tracking" "AAAI-25"` |
| Q233 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ "visual tracking" "AAAI-25"` |
| Q234 | Web search | `"MIMTrack: In-Context Tracking via Masked Image Modeling" GitHub` |
| Q235 | Web search | `"Unified Multi-Domain Adaptive Tracking Under Adverse Weather Conditions" GitHub` |
| Q236 | Web search | `"LoRATv2: Enabling Low-Cost Temporal Modeling" GitHub` |
| Q237 | Web search | `"Less Is More: Token Context-Aware Learning for Object Tracking" checkpoint evaluation` |
| Q238 | Web search | `site:openreview.net/forum "Closed-loop Scaling Up for Visual Object Tracking"` |
| Q239 | Web search | `site:openreview.net "Closed-loop Scaling Up for Visual Object Tracking" ICLR 2025` |
| Q240 | Web search | `site:openreview.net/forum?id=89ZIautowR` |
| Q241 | Web search | `site:openreview.net/forum?id=fGuTN7huo5` |
| Q242 | Web search | `site:openreview.net/forum?id=FooiwsnEH9` |
| Q243 | Web search | `site:openreview.net/forum?id=vDV912fa3t` |
| Q244 | Web search | `"89ZIautowR"` |
| Q245 | Web search | `"FooiwsnEH9"` |
| Q246 | Web search | `"vDV912fa3t"` |
| Q247 | Web search | `"fGuTN7huo5"` |
| Q248 | Web search | `"89ZIautowR" NeurIPS 2025 tracking` |
| Q249 | Web search | `NeurIPS 2025 "Lattice Boltzmann" tracking` |
| Q250 | Web search | `NeurIPS 2025 pixel point open-world object tracking lattice` |
| Q251 | Web search | `NeurIPS 2025 "Opt-CWM"` |
| Q252 | Web search | `site:papers.nips.cc/paper_files/paper/2025 "Fully Spiking Neural Networks for Unified Frame-Event Object Tracking"` |
| Q253 | Web search | `site:papers.nips.cc/paper_files/paper/2025 "TrackingWorld: World-centric Monocular 3D Tracking of Almost All Pixels"` |
| Q254 | Web search | `site:papers.nips.cc/paper_files/paper/2025 "Self-Supervised Learning of Motion Concepts by Optimizing Counterfactuals"` |
| Q255 | Web search | `site:ijcai.org/proceedings/2025 "single object tracking"` |
| Q256 | Web search | `site:ijcai.org/proceedings/2025 visual tracking LaSOT GOT-10k TrackingNet` |
| Q257 | Web search | `site:ijcai.org/proceedings/2025 SSTrack` |
| Q258 | Web search | `site:ijcai.org/proceedings/2025 FastSeqTrack` |
| Q259 | Web search | `"Exploring Efficient and Effective Sequence Learning for Visual Object Tracking" GitHub` |
| Q260 | Web search | `"FastSeqTrack" GitHub model evaluation` |
| Q261 | Web search | `site:github.com/Kou-99/SSTrack checkpoint evaluation` |
| Q262 | Web search | `"Wave-wise Discriminative Tracking by Phase-Amplitude Separation" GitHub` |

### Rà soát theo họ cơ chế — 52 lượt

| ID | Source | Exact query string |
|---|---|---|
| Q263 | Web search | `"single object tracking" 2025 transformer efficient lightweight LaSOT GOT-10k TrackingNet` |
| Q264 | Web search | `site:openaccess.thecvf.com 2025 "visual tracking" LaSOT GOT-10k TrackingNet` |
| Q265 | Web search | `site:openreview.net 2025 "visual object tracking" LaSOT GOT-10k TrackingNet` |
| Q266 | Web search | `site:proceedings.mlr.press 2025 visual tracking LaSOT GOT-10k TrackingNet` |
| Q267 | Web search | `"single object tracking" "token pruning" OR "token merging" OR "token routing" 2025 2026 LaSOT` |
| Q268 | Web search | `"visual object tracking" "dynamic computation" OR "adaptive depth" OR "early exit" 2025 2026` |
| Q269 | Web search | `"visual tracking" Mamba "state space" 2025 2026 GOT-10k` |
| Q270 | Web search | `"long-term single object tracking" 2025 2026 memory template occlusion distractor` |
| Q271 | Web search | `"single object tracking" reliability-aware occlusion distractor 2025 2026 LaSOT GOT-10k` |
| Q272 | Web search | `"visual tracking" template memory efficient occlusion distractor 2025 2026` |
| Q273 | Web search | `"edge" OR "embedded" "single object tracking" 2025 2026 lightweight` |
| Q274 | Web search | `"adaptive search region" OR "conditional computation" visual tracking 2025 2026` |
| Q275 | Web search | `"autoregressive visual tracking" 2025 2026 LaSOT GOT-10k TrackingNet` |
| Q276 | Web search | `"adaptive capacity" "visual tracking" 2025 2026` |
| Q277 | Web search | `"memory efficient" "single object tracking" 2025 2026` |
| Q278 | Web search | `"video-level" temporal "single object tracking" 2025 2026` |
| Q279 | Web search | `site:openaccess.thecvf.com "token pruning" tracking LaSOT` |
| Q280 | Web search | `site:openaccess.thecvf.com/content/CVPR2026 visual tracking token compression LaSOT GOT-10k TrackingNet` |
| Q281 | Web search | `site:openaccess.thecvf.com/content/CVPR2026 "Toward Low-Cost yet Effective Temporal Learning for UAV Tracking"` |
| Q282 | Web search | `site:openaccess.thecvf.com/content/CVPR2026 "Adaptive Depth Lightweight RGB-T Tracking with Holistic Token Routing"` |
| Q283 | Web search | `site:openaccess.thecvf.com/content/CVPR2025 "Similarity-Guided Layer-Adaptive Vision Transformer for UAV Tracking"` |
| Q284 | Web search | `site:openaccess.thecvf.com/content/CVPR2025 "Spatio-Temporal Parameter-Efficient Fine-Tuning with Mixture of Experts for Scalable Visual Tracking"` |
| Q285 | Web search | `site:openaccess.thecvf.com/content/CVPR2025 "Learning Occlusion-Robust Vision Transformers for Real-Time UAV Tracking"` |
| Q286 | Web search | `site:openreview.net NeurIPS 2025 LoRATv2 temporal modeling one-stream trackers` |
| Q287 | Web search | `site:openaccess.thecvf.com/content/ICCV2025 tracking compression transformer LaSOT GOT-10k TrackingNet` |
| Q288 | Web search | `site:openreview.net ICLR 2026 generic object tracking online model editing` |
| Q289 | Web search | `"Adaptive Capacity Autoregressive Visual Tracking" official code GitHub CVPR 2026` |
| Q290 | Web search | `"Improving Accuracy and Generalization for Efficient Visual Tracking" official code GitHub WACV 2025` |
| Q291 | Web search | `"MambaLCT" official code GitHub AAAI 2025` |
| Q292 | Web search | `"Two-stream Beats One-stream" official code GitHub AAAI 2025 visual tracking` |
| Q293 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view "MambaLCT"` |
| Q294 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view "SUTrack" "single object tracking"` |
| Q295 | Web search | `"SUTrack: Towards Simple and Unified Single Object Tracking" official GitHub` |
| Q296 | Web search | `"Exploring Enhanced Contextual Information for Video-Level Object Tracking" official GitHub AAAI 2025` |
| Q297 | Web search | `"STATrack: Spatio-temporal adaptive transformer" official GitHub code` |
| Q298 | Web search | `"Combining short-term and long-term memory for robust visual tracking" code GitHub` |
| Q299 | Web search | `"A visual object tracking method based on historical prompts of Mamba" code GitHub` |
| Q300 | Web search | `"Efficient Plug-and-Play Mamba-based Selective Target State Modeling" official code GitHub` |
| Q301 | Web search | `site:github.com/Xiaochen918/TSTrack "TSTrack"` |
| Q302 | Web search | `site:github.com "STATrack" "Spatio-temporal adaptive transformer"` |
| Q303 | Web search | `site:github.com "CSLMTrack"` |
| Q304 | Web search | `site:github.com "historical prompts of Mamba" visual tracking` |
| Q305 | Web search | `"Autoregressive Sequential Pretraining for Visual Tracking" official code GitHub` |
| Q306 | Web search | `site:github.com "ARPTrack" "CVPR 2025"` |
| Q307 | Web search | `site:github.com "ETCTrack" "Efficient Token Compression"` |
| Q308 | Web search | `site:github.com "UTPTrack" "CVPR 2026"` |
| Q309 | Web search | `site:github.com "Drift-Resilient Temporal Priors for Visual Tracking"` |
| Q310 | Web search | `site:github.com "UETrack" "CVPR 2026"` |
| Q311 | Web search | `site:github.com "TGTrack" "CVPR 2026"` |
| Q312 | Web search | `site:github.com "GOT-Edit" "Geometry-Aware Generic Object Tracking"` |
| Q313 | Web search | `site:github.com "General Compression Framework for Efficient Transformer Object Tracking"` |
| Q314 | Web search | `site:github.com "Adaptive Depth Lightweight RGB-T Tracking"` |

### Rà soát hội nghị 2026 và tạp chí 2025–2026 — 95 lượt

| ID | Source | Exact query string |
|---|---|---|
| Q315 | Web search | `site:openaccess.thecvf.com/CVPR2026 "tracking" "object"` |
| Q316 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "single object tracking"` |
| Q317 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "visual object tracking"` |
| Q318 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html LaSOT GOT-10k TrackingNet` |
| Q319 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html tracker template search image` |
| Q320 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html tracking "LaSOT"` |
| Q321 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html tracking "GOT-10k"` |
| Q322 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html tracking "TrackingNet"` |
| Q323 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html tracking "LaSOText"` |
| Q324 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "Tracking" "visual" -"multi-object" -"3D"` |
| Q325 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html intitle:tracking tracker RGB` |
| Q326 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "efficient" "tracking" "template"` |
| Q327 | Web search | `site:openaccess.thecvf.com/content/CVPR2026/html "robust" "single object" tracker` |
| Q328 | Web search | `site:openreview.net ICLR 2026 "single object tracking"` |
| Q329 | Web search | `site:openreview.net ICLR 2026 "object tracking" autoregressive` |
| Q330 | Web search | `site:openreview.net ICLR 2026 tracking LaSOT GOT-10k TrackingNet` |
| Q331 | Web search | `site:openreview.net ICLR 2026 "visual object tracking"` |
| Q332 | Web search | `site:openreview.net "Published as a conference paper at ICLR 2026" "tracking" LaSOT` |
| Q333 | Web search | `site:openreview.net "ICLR 2026 Poster" "visual tracking"` |
| Q334 | Web search | `site:openreview.net "ICLR 2026 Poster" "single object tracking"` |
| Q335 | Web search | `site:openreview.net "Published: 26 Jan 2026" "Generic Object Tracking"` |
| Q336 | Web search | `site:ojs.aaai.org/index.php/AAAI 2026 "visual tracking"` |
| Q337 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ 2026 "single object tracking"` |
| Q338 | Web search | `site:ojs.aaai.org/index.php/AAAI/article/view/ 2026 LaSOT GOT-10k` |
| Q339 | Web search | `site:openaccess.thecvf.com/content/WACV2026/html "single object tracking"` |
| Q340 | Web search | `site:openaccess.thecvf.com/content/WACV2026/html "visual tracking"` |
| Q341 | Web search | `site:ijcai.org/proceedings/2026/ "visual tracking"` |
| Q342 | Web search | `site:2026.ijcai.org/accepted-papers/ "single object tracking"` |
| Q343 | Web search | `site:proceedings.mlr.press 2026 "single object tracking"` |
| Q344 | Web search | `site:proceedings.mlr.press/v*/ 2026 "visual tracking"` |
| Q345 | Web search | `2026 "transformer visual tracking" single object tracker` |
| Q346 | Web search | `2026 "efficient visual tracking" single object tracker` |
| Q347 | Web search | `2026 "lightweight visual tracking" single object tracker` |
| Q348 | Web search | `2026 "temporal visual tracking" single object tracker` |
| Q349 | Web search | `2026 "video-level" "visual tracking" tracker` |
| Q350 | Web search | `2026 "long-term visual tracking" tracker` |
| Q351 | Web search | `2026 "autoregressive visual tracking"` |
| Q352 | Web search | `2026 (Mamba OR "state-space") "visual tracking" single object` |
| Q353 | Web search | `2026 "dynamic computation" "visual tracking"` |
| Q354 | Web search | `2026 "adaptive computation" "visual tracking"` |
| Q355 | Web search | `2026 "adaptive depth" "visual tracking"` |
| Q356 | Web search | `2026 "early exit" "visual tracking"` |
| Q357 | Web search | `2026 "layer pruning" "visual tracking"` |
| Q358 | Web search | `2026 "layer bypass" "visual tracking"` |
| Q359 | Web search | `2026 "token pruning" "visual tracking"` |
| Q360 | Web search | `2026 "token merging" "visual tracking"` |
| Q361 | Web search | `2026 "token compression" "visual tracking"` |
| Q362 | Web search | `2026 "memory efficient" "visual tracking" tracker` |
| Q363 | Web search | `2026 "template efficient" "visual tracking"` |
| Q364 | Web search | `2026 "motion-aware" "visual tracking" single object` |
| Q365 | Crossref API (lead discovery only) | `https://api.crossref.org/journals/0162-8828/works?query.title=tracking&filter=from-pub-date:2025-01-01,until-pub-date:2026-08-24&rows=100&select=DOI,title,published` |
| Q366 | Crossref API (lead discovery only) | `https://api.crossref.org/journals/1057-7149/works?query.title=tracking&filter=from-pub-date:2025-01-01,until-pub-date:2026-08-24&rows=100&select=DOI,title,published` |
| Q367 | Crossref API (lead discovery only) | `https://api.crossref.org/journals/1520-9210/works?query.title=tracking&filter=from-pub-date:2025-01-01,until-pub-date:2026-08-24&rows=100&select=DOI,title,published` |
| Q368 | Crossref API (lead discovery only) | `https://api.crossref.org/journals/1051-8215/works?query.title=tracking&filter=from-pub-date:2025-01-01,until-pub-date:2026-08-24&rows=100&select=DOI,title,published` |
| Q369 | Crossref API (lead discovery only) | `https://api.crossref.org/journals/0920-5691/works?query.title=tracking&filter=from-pub-date:2025-01-01,until-pub-date:2026-08-24&rows=100&select=DOI,title,published` |
| Q370 | Crossref API (lead discovery only) | `https://api.crossref.org/journals/0031-3203/works?query.title=tracking&filter=from-pub-date:2025-01-01,until-pub-date:2026-08-24&rows=100&select=DOI,title,published` |
| Q371 | Crossref API (lead discovery only) | `https://api.crossref.org/journals/0893-6080/works?query.title=tracking&filter=from-pub-date:2025-01-01,until-pub-date:2026-08-24&rows=100&select=DOI,title,published` |
| Q372 | Crossref API (lead discovery only) | `https://api.crossref.org/journals/0950-7051/works?query.title=tracking&filter=from-pub-date:2025-01-01,until-pub-date:2026-08-24&rows=100&select=DOI,title,published` |
| Q373 | Crossref API (lead discovery only) | `https://api.crossref.org/journals/0925-2312/works?query.title=tracking&filter=from-pub-date:2025-01-01,until-pub-date:2026-08-24&rows=100&select=DOI,title,published` |
| Q374 | Crossref API (lead discovery only) | `https://api.crossref.org/journals/0262-8856/works?query.title=tracking&filter=from-pub-date:2025-01-01,until-pub-date:2026-08-24&rows=100&select=DOI,title,published` |
| Q375 | Crossref API (lead discovery only) | `https://api.crossref.org/journals/0952-1976/works?query.title=tracking&filter=from-pub-date:2025-01-01,until-pub-date:2026-08-24&rows=100&select=DOI,title,published` |
| Q376 | Web search | `site:ieeexplore.ieee.org/document/ 2026 "single object tracking"` |
| Q377 | Web search | `site:ieeexplore.ieee.org/document/ 2026 "visual object tracking" tracker` |
| Q378 | Web search | `site:ieeexplore.ieee.org/document/ "2026" tracker LaSOT GOT-10k` |
| Q379 | Web search | `site:ieeexplore.ieee.org/document/ "2025" visual tracker LaSOT TrackingNet` |
| Q380 | Web search | `2026 site:ieeexplore.ieee.org/document/ "Transactions on Circuits and Systems for Video Technology" "visual tracking"` |
| Q381 | Web search | `2025 site:ieeexplore.ieee.org/document/ "Transactions on Circuits and Systems for Video Technology" "visual tracking"` |
| Q382 | Web search | `2026 site:ieeexplore.ieee.org/document/ "Transactions on Multimedia" "visual tracking"` |
| Q383 | Web search | `2025 site:ieeexplore.ieee.org/document/ "Transactions on Image Processing" "visual tracking"` |
| Q384 | Web search | `site:link.springer.com/article/10.1007/s11263 2026 "tracking" object` |
| Q385 | Web search | `site:link.springer.com/article/10.1007/s11263 2025 "visual tracking"` |
| Q386 | Web search | `GOT-Edit official GitHub checkpoint evaluation` |
| Q387 | Web search | `"STDTrack" "github.com" Junze Shi` |
| Q388 | Web search | `"Exploring Reliable Spatiotemporal Dependencies" code` |
| Q389 | Web search | `"Variational Inference for Cyclic Learning" GitHub CycleTrack` |
| Q390 | Web search | `"CycleTrack" "source codes" github.com` |
| Q391 | Web search | `"Beyond Explicit Language" tracker code` |
| Q392 | Web search | `"Drift-Resilient Temporal Priors" code` |
| Q393 | Web search | `"Adaptive Capacity Autoregressive Visual Tracking" code` |
| Q394 | Web search | `"Efficient early exit single object tracking via general distribution" code` |
| Q395 | Web search | `"Adaptively bypassing vision transformer blocks for efficient visual tracking" GitHub` |
| Q396 | Web search | `"Exploiting Lightweight Hierarchical ViT and Dynamic Framework for Efficient Visual Tracking" GitHub` |
| Q397 | Web search | `"PCTrack: Accurate Object Tracking for Live Video Analytics on Resource-Constrained Edge Devices"` |
| Q398 | Web search | `"SMTrack" visual tracking GitHub Yinchao Ma` |
| Q399 | Web search | `"SAMURAI" visual tracking GitHub yangchris11` |
| Q400 | Web search | `"ParaTrack" visual object tracking GitHub` |
| Q401 | Web search | `"TSTrack" lightweight visual tracking GitHub Mamba` |
| Q402 | Web search | `"Distractor-Aware Memory-Based Visual Object Tracking" code GitHub` |
| Q403 | Web search | `"LoongTrack: Exploring long-sequence modeling for visual tracking" GitHub` |
| Q404 | Web search | `"EME: Out-of-view handling in visual object tracking via edge-aware motion estimation"` |
| Q405 | Web search | `"TrHelpTr: A long-term single-object tracking paradigm" GitHub` |
| Q406 | Web search | `"Joint Neural Architecture Search and Token Pruning for Efficient Visual Tracking"` |
| Q407 | Web search | `"UncTrack: Reliable Visual Object Tracking With Uncertainty-Aware Prototype Memory Network" GitHub` |
| Q408 | Web search | `"Instance-aware global re-detection for precise and efficient long-term visual tracking"` |
| Q409 | Web search | `"OmniTracker" GitHub Junke Wang Zuxuan Wu` |

## 6. Hạn chế và handoff

- Search coverage rộng nhưng không đồng nghĩa exhaustive proof; repository/publication state có thể thay đổi sau ngày khóa sổ.
- Crossref metadata không tự chứng minh peer review, online-first date hay journal quartile.
- Candidate identity được dedup theo method family/paper, không theo checkpoint variant.
- Chi tiết candidate, Pool và early gates nằm trong `2026-08-24_stage1_candidate_universe.csv`.
- HG4–HG6 không được suy diễn từ FLOPs, desktop FPS, CPU FPS, Jetson AGX/NX/Orin hoặc parameter count.
