# References and source notes

Citation style: IEEE. Links were checked on **2026-08-17** unless otherwise stated. A link is evidence only for the claim explicitly attributed to it; it is not blanket support for a broader conclusion.

## R1

H. Ye *et al.*, “TPT-Bench: A large-scale, long-term and robot-egocentric dataset for benchmarking target person tracking,” *The International Journal of Robotics Research*, OnlineFirst, Jun. 8, 2026, doi: [10.1177/02783649261447308](https://doi.org/10.1177/02783649261447308). [Official journal page](https://journals.sagepub.com/doi/10.1177/02783649261447308). Accessed: 2026-08-17.

Use: robot-egocentric target-person context, 48 sequences, crowded/unstructured settings, long occlusion and re-identification. Limit: collection used a human pushing a sensor-equipped cart; it is not proof of autonomous robot deployment.

## R2

H. Ye *et al.*, “TPT-Bench: A Large-Scale, Long-Term and Robot-Egocentric Dataset for Benchmarking Target Person Tracking,” Zenodo, version 1.0, Nov. 2025, doi: [10.5281/zenodo.17718188](https://doi.org/10.5281/zenodo.17718188). [Dataset record](https://zenodo.org/records/17718188). Accessed: 2026-08-17.

Use: 5.3 h, 571,982 boxes, 48 sequences, data components, toolkit link, and record rights. Limit: the record lists Copyright; do not redistribute the data through this repository.

## R3

M. Dunnhofer, Z. Manigrasso, and C. Micheloni, “Is Tracking Really More Challenging in First Person Egocentric Vision?,” in *Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)*, 2025, pp. 5879–5889. [Official CVF paper](https://openaccess.thecvf.com/content/ICCV2025/papers/Dunnhofer_Is_Tracking_Really_More_Challenging_in_First_Person_Egocentric_Vision_ICCV_2025_paper.pdf). [Official VISTA project page](https://machinelearning.uniud.it/datasets/vista/). Accessed: 2026-08-17.

Use: synchronized FPV–TPV benchmark study and viewpoint/activity-domain separation. Limit: object tracking in human activity, not robot-person tracking.

## R4

H. Tang *et al.*, “EgoTracks: A Long-Term Egocentric Visual Object Tracking Dataset,” in *Advances in Neural Information Processing Systems*, vol. 36, 2023, pp. 75716–75739. [Official proceedings page](https://proceedings.neurips.cc/paper_files/paper/2023/hash/ef01d91aa87e7701aa9c8dc66a2d5bdb-Abstract-Datasets_and_Benchmarks.html). [Official data documentation](https://ego4d-data.org/docs/data/egotracks/). Accessed: 2026-08-17.

Use: long-term egocentric object tracking, per-frame localization and presence confidence. Limit: access is governed by Ego4D terms; it is not robot-person data.

## R5

S. Wang *et al.*, “TrackVLA: Embodied Visual Tracking in the Wild,” in *Proceedings of the 9th Conference on Robot Learning*, *Proceedings of Machine Learning Research*, vol. 305, 2025, pp. 4139–4164. [Official PMLR page](https://proceedings.mlr.press/v305/wang25f.html). Accessed: 2026-08-17.

Use: active embodied-tracking research direction and perception-planning scope boundary. Limit: not a Jetson Nano baseline.

## R6

Visual Object Tracking Challenge, “VOT long-term subchallenge (VOT-LT2022),” 2022. [Official participation/protocol page](https://www.votchallenge.net/vot2022/participation.html). Accessed: 2026-08-17.

Use: causal long-term tracking, disappearance, re-detection, and presence-confidence requirements. Limit: generic benchmark, not robot-person validation.

## R7

Defense Advanced Research Projects Agency, “DARPA Triage Challenge,” 2026. [Official challenge page](https://www.darpa.mil/research/challenges/darpa-triage-challenge/about). Accessed: 2026-08-17.

Use: evidence that disaster triage is a multi-capability robotic mission, not merely RGB tracking.

## R8

National Institute of Standards and Technology, “Performance of Emergency Response Robots,” 2026. [Official program page](https://www.nist.gov/programs-projects/performance-emergency-response-robots). Accessed: 2026-08-17.

Use: official emergency-response robot performance-evaluation context.

## R9

National Institute for Occupational Safety and Health, “Lone Workers,” 2024. [Official NIOSH bulletin](https://www.cdc.gov/niosh/bulletin/2024/lone-workers.html). Accessed: 2026-08-17.

Use: worker-safety context and the need to evaluate technology effectiveness. Limit: not an endorsement of RGB SOT as a safety system.

## R10

R. J. Zaveri, S. Patel, Y. Gu, and G. Doretto, “Improving Accuracy and Generalization for Efficient Visual Tracking,” in *Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision (WACV)*, 2025, pp. 9450–9460. [Official CVF page](https://openaccess.thecvf.com/content/WACV2025/html/Zaveri_Improving_Accuracy_and_Generalization_for_Efficient_Visual_Tracking_WACV_2025_paper.html). [Official CVF PDF](https://openaccess.thecvf.com/content/WACV2025/papers/Zaveri_Improving_Accuracy_and_Generalization_for_Efficient_Visual_Tracking_WACV_2025_paper.pdf). Accessed: 2026-08-24.

Use: primary publication source for the SiamABC family. Limit: the inspected official CVF source does not display a DOI; reported desktop/embedded-platform results do not establish Jetson Nano performance.

## R11

G. Wang, T. Lin, Y. Bai, A. Cao, S. Liang, W. Zhao, and X. Wei, “FARTrack: Fast Autoregressive Visual Tracking with High Performance,” in *International Conference on Learning Representations (ICLR)*, 2026. [Official OpenReview forum](https://openreview.net/forum?id=lq7Zfr8kAS). [Official OpenReview PDF](https://openreview.net/pdf?id=lq7Zfr8kAS). Accessed: 2026-08-24.

Use: primary source for FARTrack architecture, Task-Specific Self-Distillation, Inter-frame Autoregressive Sparsification, multi-template experiments, model sizes/MACs, reported benchmark values, training hardware/procedure, speed-test hardware, and author-reported limitations. Limit: generic SOT evaluation does not prove target-person identity preservation or Jetson Nano feasibility.

## R12

MIV-XJTU, “FARTrack — official PyTorch implementation,” GitHub repository, `main` at commit `5d3e4b90305c2e845340a39cb1ac9bb69c0c5180`, 2026. [Official repository](https://github.com/MIV-XJTU/FARTrack). [Pinned source](https://github.com/MIV-XJTU/FARTrack/tree/5d3e4b90305c2e845340a39cb1ac9bb69c0c5180). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — source, FARTrack/FARTrackDistill/FARTrackSparse checkpoints, configurations, and documented LaSOT/GOT-10k/TrackingNet evaluation workflow. Limit: the MAE ViT-Tiny backbone weight is separate from trained tracker checkpoints; availability is not successful reproduction, and the reported Titan Xp/Xeon/Ascend speeds are not Jetson Nano results.

## R13

J. Zhao, X. Chen, Y. Yuan, M. Felsberg, D. Wang, and H. Lu, “Efficient Motion Prompt Learning for Robust Visual Tracking,” in *Proceedings of the 42nd International Conference on Machine Learning (ICML)*, PMLR, vol. 267, pp. 77353–77370, 2025. [Official PMLR page](https://proceedings.mlr.press/v267/zhao25e.html). Accessed: 2026-08-24.

Use: manager-lane Stage-1 reconciliation addition; establishes a peer-reviewed 2025 lightweight plug-and-play motion-prompt method for generic visual tracking. Limit: it is a plug-in method integrated into existing trackers, so suitability as a standalone main baseline remains a later audit question.

## R14

J. Zhao *et al.*, “Motion-Prompt-Tracking — official PyTorch implementation,” GitHub repository, 2025. [Official repository](https://github.com/zj5559/Motion-Prompt-Tracking). Accessed: 2026-08-24.

Use: source, training/testing instructions, released models/results, and early HG3 verification for MPT. Limit: repository availability is not equivalent to successful local reproduction.

## R15

J. Tao, S. Chan, Z. Shi, C. Bai, and S. Chen, “FocTrack: Focus attention for visual tracking,” *Pattern Recognition*, vol. 160, Art. no. 111128, 2025, doi: [10.1016/j.patcog.2024.111128](https://doi.org/10.1016/j.patcog.2024.111128). [Official publisher page](https://www.sciencedirect.com/science/article/abs/pii/S0031320324008793). Accessed: 2026-08-24.

Use: manager-lane Stage-1 reconciliation addition; establishes a 2025 generic visual tracker with focus attention and a lightweight local-template-update strategy. Limit: a complete official source+checkpoint+evaluator bundle has not yet been verified.

## R16

Z. Wang, K. Wang, C. Tang, X. Li, J. Zhang, and L. Gao, “DSTrack: Diffusion-based sequence learning for visual object tracking,” *Pattern Recognition*, vol. 168, Art. no. 111694, 2025, doi: [10.1016/j.patcog.2025.111694](https://doi.org/10.1016/j.patcog.2025.111694). [Official publisher page](https://www.sciencedirect.com/science/article/pii/S0031320325003541). Accessed: 2026-08-24.

Use: manager-lane Stage-1 reconciliation addition; establishes a 2025 generic RGB bbox-SOT family based on diffusion-style continuous coordinate sequence prediction. Limit: a complete official source+checkpoint+evaluator bundle has not yet been verified.

## R17

H. Guo, X. Du, and W. Wang, “Motion Deep Association for spatio-temporal object tracking,” *Pattern Recognition*, vol. 168, Art. no. 111787, 2025, doi: [10.1016/j.patcog.2025.111787](https://doi.org/10.1016/j.patcog.2025.111787). [Official publisher page](https://www.sciencedirect.com/science/article/pii/S0031320325004479). Accessed: 2026-08-24.

Use: manager-lane Stage-1 reconciliation addition; establishes a 2025 generic RGB spatio-temporal tracker combining visual feature fusion and historical motion association. Limit: a complete official source+checkpoint+evaluator bundle has not yet been verified.

## R18

Q. Zhang, J. Cheng, Q. Mao, C. Liu, Y. Fang, Y. Li, M. Ge, and S. Gao, “SpikeTrack: A Spike-driven Framework for Efficient Visual Tracking,” in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2026, pp. 6802–6811. [Official CVF page](https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_SpikeTrack_A_Spike-driven_Framework_for_Efficient_Visual_Tracking_CVPR_2026_paper.html). [Official CVF PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Zhang_SpikeTrack_A_Spike-driven_Framework_for_Efficient_Visual_Tracking_CVPR_2026_paper.pdf). Accessed: 2026-08-24.

Use: primary publication source for SpikeTrack. Limit: the inspected official CVF source does not display a DOI; reported efficiency does not establish Jetson Nano performance.

## R19

faicaiwawa, “SpikeTrack — official implementation,” GitHub repository, `main` at commit `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`, 2026. [Official repository](https://github.com/faicaiwawa/SpikeTrack). [Pinned source](https://github.com/faicaiwawa/SpikeTrack/tree/1537db51a1cc9f6e30cce469fba3e51f5721b3d0). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — code, six trained tracker checkpoints, raw results, and documented LaSOT/GOT-10k/TrackingNet test and analysis commands. Limit: the SDTV3 backbone-pretraining asset is separate; availability is not reproduction. Repository owner `faicaiwawa` and its linked Hugging Face owner `facaiwawa` use different spellings.

## R20

B. Kang, J. Zhao, X. Chen, W. Geng, B. Zhang, L. Zhang, D. Wang, and H. Lu, “UETrack: A Unified and Efficient Framework for Single Object Tracking,” in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2026, pp. 20890–20901. [Official CVF page](https://openaccess.thecvf.com/content/CVPR2026/html/Kang_UETrack_A_Unified_and_Efficient_Framework_for_Single_Object_Tracking_CVPR_2026_paper.html). [Official CVF PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Kang_UETrack_A_Unified_and_Efficient_Framework_for_Single_Object_Tracking_CVPR_2026_paper.pdf). Accessed: 2026-08-24.

Use: primary publication source for UETrack. Limit: the inspected official CVF source does not display a DOI; multimodal results must not be represented as RGB-only evidence.

## R21

kangben258, “UETrack — official implementation,” GitHub repository, `main` at commit `fd13b0eaf16d51536008295f3b27807c69eaad50`, 2026. [Official repository](https://github.com/kangben258/UETrack). [Pinned source](https://github.com/kangben258/UETrack/tree/fd13b0eaf16d51536008295f3b27807c69eaad50). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — source, Base/Small/Tiny tracker checkpoints, raw results, and documented RGB/multimodal benchmark and VOT evaluation workflows. Limit: backbone and teacher weights are separate from tracker checkpoints; RGB inference is supported within a unified multimodal framework, and reported AGX speed is not Jetson Nano speed.

## R22

H. Wu, X. Wang, J. Zhang, J. Tong, X. Chen, J. Lin, Y. Ma, and X. Shen, “UTPTrack: Towards Simple and Unified Token Pruning for Visual Tracking,” in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2026, pp. 20963–20972. [Official CVF page](https://openaccess.thecvf.com/content/CVPR2026/html/Wu_UTPTrack_Towards_Simple_and_Unified_Token_Pruning_for_Visual_Tracking_CVPR_2026_paper.html). [Official CVF PDF](https://openaccess.thecvf.com/content/CVPR2026/papers/Wu_UTPTrack_Towards_Simple_and_Unified_Token_Pruning_for_Visual_Tracking_CVPR_2026_paper.pdf). Accessed: 2026-08-24.

Use: primary publication source for UTPTrack. Limit: the inspected official CVF source does not display a DOI; paper results do not establish successful reproduction or Jetson Nano performance.

## R23

EIT-NLP, “UTPTrack — official implementation,” GitHub repository, `main` at commit `84e0f49711254a44f5308faaa9a2405db1964dd7`, 2026. [Official repository](https://github.com/EIT-NLP/UTPTrack). [Pinned source](https://github.com/EIT-NLP/UTPTrack/tree/84e0f49711254a44f5308faaa9a2405db1964dd7). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — two code subtrees, four O/S tracker checkpoints, and documented LaSOT/GOT-10k/TrackingNet/VOT evaluation workflows. Limit: `UTPTrack-O` is OSTrack-derived and `UTPTrack-S` is SUTrack-derived; implementation, model, and configuration must be pinned together, and MAE/SUTrack pretraining assets are not trained UTPTrack checkpoints.

## R24

S.-F. Chen, J.-C. Chen, I.-H. Jhuo, and Y.-Y. Lin, “GOT-Edit: Geometry-Aware Generic Object Tracking via Online Model Editing,” in *International Conference on Learning Representations (ICLR)*, 2026. [Official ICLR proceedings page](https://proceedings.iclr.cc/paper_files/paper/2026/hash/519c51529c3544b3430bd8b17d400365-Abstract-Conference.html). [Official OpenReview forum](https://openreview.net/forum?id=aVa7etWnwF). Accessed: 2026-08-24.

Use: primary publication source for GOT-Edit. Limit: the official sources inspected do not display a DOI; geometry cues are inferred from RGB, while the implementation has a separate geometry-backbone dependency.

## R25

chenshihfang, “GOT — official implementation for GOT-Edit and GOT-JEPA,” GitHub repository, current `main` at commit `b2ee0b9792db634a880189e8189542953af0d223`; GOT-JEPA-relevant historical commit `84e9324317e4afe62c06b2c51a97563f79730a2e`, 2026. [Official repository](https://github.com/chenshihfang/GOT). [Current pinned source](https://github.com/chenshihfang/GOT/tree/b2ee0b9792db634a880189e8189542953af0d223). [GOT-JEPA pinned source](https://github.com/chenshihfang/GOT/tree/84e9324317e4afe62c06b2c51a97563f79730a2e). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — source, model/raw-result links, training/run commands, and family-specific evaluation scripts for GOT-Edit and GOT-JEPA. Limit: this is a mutable, shared multi-paper repository; GOT-JEPA requires its historical commit, geometry-backbone assets are separate dependencies, and resource availability is not reproduction.

## R26

S.-F. Chen, J.-C. Chen, I.-H. Jhuo, and Y.-Y. Lin, “GOT-JEPA: Generic Object Tracking With Model Adaptation and Occlusion Handling Using Joint-Embedding Predictive Architecture,” *IEEE Transactions on Circuits and Systems for Video Technology*, vol. 36, no. 7, pp. 10836–10851, 2026, doi: [10.1109/TCSVT.2026.3675005](https://doi.org/10.1109/TCSVT.2026.3675005). [Official IEEE record](https://ieeexplore.ieee.org/document/11436011/). Accessed: 2026-08-24.

Use: primary publication source for GOT-JEPA. Limit: publication evidence does not resolve the official repository's current-versus-historical-commit ambiguity.

## R27

C.-Y. Yang, H.-W. Huang, W. Chai, Z. Jiang, and J.-N. Hwang, “SAMURAI: Motion-Aware Memory for Training-Free Visual Object Tracking With SAM 2,” *IEEE Transactions on Image Processing*, vol. 35, pp. 970–982, 2026, doi: [10.1109/TIP.2026.3651835](https://doi.org/10.1109/TIP.2026.3651835). [Official IEEE record](https://ieeexplore.ieee.org/document/11351313/). Accessed: 2026-08-24.

Use: primary publication source for SAMURAI. Limit: it is a training-free SAM 2 method; foundation-model weights must not be registered as a family-trained checkpoint.

## R28

yangchris11, “SAMURAI — official implementation,” GitHub repository, `master` at commit `76ba195984892b0d1e3db5d9c9f90bb62175680a`, 2026. [Official repository](https://github.com/yangchris11/samurai). [Pinned source](https://github.com/yangchris11/samurai/tree/76ba195984892b0d1e3db5d9c9f90bb62175680a). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — source, raw results, SAM 2.1 checkpoint downloader, and dataset inference scripts. Limit: no SAMURAI-trained tracker checkpoint exists because the method is training-free; the downloaded weights are SAM 2.1 base weights, VOT-toolkit integration is marked incoming, and live/streaming input is unsupported by the inspected README.

## R29

J. Videnović, M. Kristan, and A. Lukežič, “Distractor-Aware Memory-Based Visual Object Tracking,” *International Journal of Computer Vision*, vol. 134, Art. no. 211, 2026, doi: [10.1007/s11263-026-02790-7](https://doi.org/10.1007/s11263-026-02790-7). [Official Springer article](https://link.springer.com/article/10.1007/s11263-026-02790-7). Accessed: 2026-08-24.

Use: primary journal source for the DAM4SAM family. Limit: the journal family extends the CVPR 2025 work, and DAM4SAM is a training-free modification of SAM 2.1 rather than a separately trained tracker.

## R30

jovanavidenovic, “DAM4SAM — official implementation,” GitHub repository, `master` at commit `9c954504b39ebca4c412f207be0787c26bfac85a`, 2026. [Official repository](https://github.com/jovanavidenovic/DAM4SAM). [Pinned source](https://github.com/jovanavidenovic/DAM4SAM/tree/9c954504b39ebca4c412f207be0787c26bfac85a). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — source, SAM 2.1 checkpoint downloader, VOT workspaces, DiDi analysis, and bounding-box-dataset runners. Limit: downloaded checkpoints are SAM 2.1 foundation weights, not family-trained DAM4SAM checkpoints; bbox evaluation first derives masks from the initial ground-truth box, and availability is not reproduction.

## R31

Y. Zheng, B. Zhong, Q. Liang, N. Li, and S. Song, “Decoupled Spatio-Temporal Consistency Learning for Self-Supervised Tracking,” *Proceedings of the AAAI Conference on Artificial Intelligence*, vol. 39, no. 10, pp. 10635–10643, 2025, doi: [10.1609/aaai.v39i10.33155](https://doi.org/10.1609/aaai.v39i10.33155). [Official AAAI article](https://ojs.aaai.org/index.php/AAAI/article/view/33155). Accessed: 2026-08-24.

Use: primary publication source for SSTrack-AAAI. Limit: self-supervised tracker training still begins from a separate pretrained backbone.

## R32

GXNU-ZhongLab, “SSTrack — official implementation,” GitHub repository, `main` at commit `5dcf04ccb04f10ca4d78035373c8b8684bb8c4f5`, 2025. [Official repository](https://github.com/GXNU-ZhongLab/SSTrack). [Pinned source](https://github.com/GXNU-ZhongLab/SSTrack/tree/5dcf04ccb04f10ca4d78035373c8b8684bb8c4f5). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — training/test code, trained models/raw results, and documented LaSOT/GOT-10k/TrackingNet/VOT/OTB evaluation workflows. Limit: the DropMAE ViT-Base weight is backbone pretraining, not the trained tracker checkpoint; repository availability is not reproduction, and RTX 2080 Ti speed is not Jetson Nano speed.

## R33

B. Kang, X. Chen, S. Lai, Y. Liu, Y. Liu, and D. Wang, “Exploring Enhanced Contextual Information for Video-Level Object Tracking,” *Proceedings of the AAAI Conference on Artificial Intelligence*, vol. 39, no. 4, pp. 4194–4202, 2025, doi: [10.1609/aaai.v39i4.32440](https://doi.org/10.1609/aaai.v39i4.32440). [Official AAAI article](https://ojs.aaai.org/index.php/AAAI/article/view/32440). Accessed: 2026-08-24.

Use: primary publication source for MCITrack. Limit: publication evidence is distinct from code/resource availability and successful reproduction.

## R34

kangben258, “MCITrack — official implementation,” GitHub repository, `main` at commit `e667193eaec4c8a73d4bdd856a662aecdb844b43`, 2025. [Official repository](https://github.com/kangben258/MCITrack). [Pinned source](https://github.com/kangben258/MCITrack/tree/e667193eaec4c8a73d4bdd856a662aecdb844b43). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — source, distinctly linked trained models, raw results/training logs, and documented test/analysis commands for major RGB benchmarks. Limit: backbone pretraining is linked separately from trained tracker models; remote assets do not establish successful reproduction.

## R35

X. Li, B. Zhong, Q. Liang, G. Li, Z. Mo, and S. Song, “MambaLCT: Boosting Tracking via Long-term Context State Space Model,” *Proceedings of the AAAI Conference on Artificial Intelligence*, vol. 39, no. 5, pp. 4986–4994, 2025, doi: [10.1609/aaai.v39i5.32528](https://doi.org/10.1609/aaai.v39i5.32528). [Official AAAI article](https://ojs.aaai.org/index.php/AAAI/article/view/32528). Accessed: 2026-08-24.

Use: primary publication source for MambaLCT. Limit: the paper does not by itself establish a usable repository evaluation protocol.

## R36

GXNU-ZhongLab, “MambaLCT — official implementation,” GitHub repository, `main` at commit `0457044f67a0a033b85c0447376fc4bde0cfc10d`, 2025. [Official repository](https://github.com/GXNU-ZhongLab/MambaLCT). [Pinned source](https://github.com/GXNU-ZhongLab/MambaLCT/tree/0457044f67a0a033b85c0447376fc4bde0cfc10d). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — source, a trained-model link, raw-result link, `tracking/test.py`, and result-analysis scripts. Limit: the inspected README does not document installation, checkpoint placement, test invocation, or an end-to-end evaluation protocol; code presence is not successful reproduction.

## R37

X. Chen, B. Kang, W. Geng, J. Zhu, Y. Liu, D. Wang, and H. Lu, “SUTrack: Towards Simple and Unified Single Object Tracking,” *Proceedings of the AAAI Conference on Artificial Intelligence*, vol. 39, no. 2, pp. 2239–2247, 2025, doi: [10.1609/aaai.v39i2.32223](https://doi.org/10.1609/aaai.v39i2.32223). [Official AAAI article](https://ojs.aaai.org/index.php/AAAI/article/view/32223). Accessed: 2026-08-24.

Use: primary publication source for SUTrack. Limit: unified training covers multiple modalities even though the repository exposes RGB-only inference/evaluation routes.

## R38

chenxin-dlut, “SUTrack — official implementation,” GitHub repository, `main` at commit `d65052d1ba3fcf55010e1fb3665ee6616c139a2c`, 2025. [Official repository](https://github.com/chenxin-dlut/SUTrack). [Pinned source](https://github.com/chenxin-dlut/SUTrack/tree/d65052d1ba3fcf55010e1fb3665ee6616c139a2c). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — source, five explicit trained tracker checkpoints, and documented RGB and multimodal benchmark workflows. Limit: iTPN assets are backbone pretraining rather than tracker checkpoints; raw results were still marked in preparation, unified multimodal training is distinct from RGB inference, and AGX speed is not Jetson Nano speed.

## R39

J. Zhu, H. Tang, X. Chen, X. Wang, D. Wang, and H. Lu, “Two-stream Beats One-stream: Asymmetric Siamese Network for Efficient Visual Tracking,” *Proceedings of the AAAI Conference on Artificial Intelligence*, vol. 39, no. 10, pp. 10959–10967, 2025, doi: [10.1609/aaai.v39i10.33191](https://doi.org/10.1609/aaai.v39i10.33191). [Official AAAI article](https://ojs.aaai.org/index.php/AAAI/article/view/33191). Accessed: 2026-08-24.

Use: primary publication source for AsymTrack. Limit: publisher-reported hardware results do not establish Jetson Nano performance.

## R40

jiawen-zhu, “AsymTrack — official implementation,” GitHub repository, `main` at commit `a7b05e0c0d6116ccd7fa72270aa19053b7777204`, 2025. [Official repository](https://github.com/jiawen-zhu/AsymTrack). [Pinned source](https://github.com/jiawen-zhu/AsymTrack/tree/a7b05e0c0d6116ccd7fa72270aa19053b7777204). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — training/testing code, model/raw-result assets, and documented GOT-10k/LaSOT/TrackingNet evaluation workflow. Limit: backbone assets are linked separately; external model-folder availability is not successful reproduction.

## R41

X. He, H. Xu, X. Zhu, and H. Li, “High-Performance Discriminative Tracking with Spatio-Temporal Template Fusion,” in *Proceedings of the 33rd ACM International Conference on Multimedia (MM '25)*, 2025, pp. 709–718, doi: [10.1145/3746027.3755721](https://doi.org/10.1145/3746027.3755721). [Official ACM page](https://dl.acm.org/doi/10.1145/3746027.3755721). Accessed: 2026-08-24.

Use: primary publication source for the JDTrack family. Limit: publication evidence does not identify the checkpoint file in the umbrella implementation repository.

## R42

hexdjx, “VisTrack — official umbrella implementation including JDTrack,” GitHub repository, `master` at commit `f07acc942dfdc0bf78f437955a3ae1fc5e62b7fc`, 2025. [Official repository](https://github.com/hexdjx/VisTrack). [Pinned source](https://github.com/hexdjx/VisTrack/tree/f07acc942dfdc0bf78f437955a3ae1fc5e62b7fc). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — JDTrack code and integrated GOT-10k/PySOT evaluation infrastructure are present; the README links a shared models/raw-results folder. Limit: this is a multi-method umbrella repository, and the inspected README does not identify a JDTrack-specific checkpoint filename in the shared asset folder.

## R43

W. Cai, Q. Liu, and Y. Wang, “SPMTrack: Spatio-Temporal Parameter-Efficient Fine-Tuning with Mixture of Experts for Scalable Visual Tracking,” in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2025, pp. 16871–16881. [Official CVF page](https://openaccess.thecvf.com/content/CVPR2025/html/Cai_SPMTrack_Spatio-Temporal_Parameter-Efficient_Fine-Tuning_with_Mixture_of_Experts_for_Scalable_CVPR_2025_paper.html). [Official CVF PDF](https://openaccess.thecvf.com/content/CVPR2025/papers/Cai_SPMTrack_Spatio-Temporal_Parameter-Efficient_Fine-Tuning_with_Mixture_of_Experts_for_Scalable_CVPR_2025_paper.pdf). Accessed: 2026-08-24.

Use: primary publication source for SPMTrack. Limit: the inspected official CVF source does not display a DOI; paper variants do not imply that all corresponding checkpoints are released.

## R44

WenRuiCai, “SPMTrack — official implementation,” GitHub repository, `main` at commit `c581fe27231f3e16c38578e47daddadfaf6ffd7d`, 2025. [Official repository](https://github.com/WenRuiCai/SPMTrack). [Pinned source](https://github.com/WenRuiCai/SPMTrack/tree/c581fe27231f3e16c38578e47daddadfaf6ffd7d). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — source, an SPMTrack-B trained checkpoint/log bundle, and documented evaluation-only, TrackingNet, and three-run GOT-10k workflows. Limit: only the B variant checkpoint is confirmed; the README marks release of all versions as pending, so L/G checkpoints are not verified.

## R45

S. Yao, R. Zhu, Z. Wang, W. Ren, Y. Yan, and X. Cao, “UMDATrack: Unified Multi-Domain Adaptive Tracking Under Adverse Weather Conditions,” in *Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)*, 2025, pp. 6466–6475. [Official CVF page](https://openaccess.thecvf.com/content/ICCV2025/html/Yao_UMDATrack_Unified_Multi-Domain_Adaptive_Tracking_Under_Adverse_Weather_Conditions_ICCV_2025_paper.html). [Official CVF PDF](https://openaccess.thecvf.com/content/ICCV2025/papers/Yao_UMDATrack_Unified_Multi-Domain_Adaptive_Tracking_Under_Adverse_Weather_Conditions_ICCV_2025_paper.pdf). Accessed: 2026-08-24.

Use: primary publication source for UMDATrack. Limit: the inspected official CVF source does not display a DOI; RGB inference follows an offline two-stage adverse-weather adaptation process.

## R46

Z-Z188, “UMDATrack — official implementation,” GitHub repository, `main` at commit `5d609bfcfb3a27161f9f4bd23bda518d6656909c`, 2025. [Official repository](https://github.com/Z-Z188/UMDATrack). [Pinned source](https://github.com/Z-Z188/UMDATrack/tree/5d609bfcfb3a27161f9f4bd23bda518d6656909c). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — two-stage source and domain-specific test/analysis/conversion commands; the linked bundle exposes pretraining, pseudo-label, stage-1, and stage-2 resources. Limit: the README does not identify a specific final evaluation-checkpoint filename in that mixed bundle; RGB inference must be distinguished from offline adaptation cost.

## R47

S. Yao, Y. Guo, Y. Yan, W. Ren, and X. Cao, “UncTrack: Reliable Visual Object Tracking With Uncertainty-Aware Prototype Memory Network,” *IEEE Transactions on Image Processing*, vol. 34, pp. 3533–3546, 2025, doi: [10.1109/TIP.2025.3559796](https://doi.org/10.1109/TIP.2025.3559796). [Official IEEE record](https://ieeexplore.ieee.org/document/10967033/). Accessed: 2026-08-24.

Use: primary publication source for UncTrack. Limit: publication evidence is separate from repository availability and successful reproduction.

## R48

ManOfStory, “UncTrack — official implementation,” GitHub repository, `main` at commit `61bd4be673ac32dd8948f995ce4548855d0ab1d0`, 2025. [Official repository](https://github.com/ManOfStory/UncTrack). [Pinned source](https://github.com/ManOfStory/UncTrack/tree/61bd4be673ac32dd8948f995ce4548855d0ab1d0). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — source, trained models/raw results, benchmark test scripts, VOT2020 workspace/analysis instructions, and profiling support. Limit: the `UncTrack+AR` path additionally depends on Alpha-Refine and the VOT toolkit; availability is not successful reproduction.

## R49

B. Kang, X. Chen, J. Zhao, C. Bo, D. Wang, and H. Lu, “Exploiting Lightweight Hierarchical ViT and Dynamic Framework for Efficient Visual Tracking,” *International Journal of Computer Vision*, vol. 133, pp. 6689–6711, 2025, doi: [10.1007/s11263-025-02500-9](https://doi.org/10.1007/s11263-025-02500-9). [Official Springer article](https://link.springer.com/article/10.1007/s11263-025-02500-9). Accessed: 2026-08-24.

Use: primary journal source for the HiT–DyHiT family. Limit: dynamic-threshold settings define different speed–accuracy operating points, and reported Jetson AGX/NX results are not Jetson Nano results.

## R50

kangben258, “HiT/DyHiT — official implementation,” GitHub repository, `main` at commit `ca806400def2b9ab42628f7a7e941b188d89606f`, 2025. [Official repository](https://github.com/kangben258/HiT). [Pinned source](https://github.com/kangben258/HiT/tree/ca806400def2b9ab42628f7a7e941b188d89606f). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — HiT/DyHiT source, linked trained-model/raw-result bundle, documented major-benchmark workflows, and ONNX/profile utilities. Limit: the external folder combines model variants and raw results, so the exact variant must be pinned; availability and AGX/NX results do not establish reproduction or Jetson Nano performance.

## R51

wvuvl, “SiamABC — official implementation,” GitHub repository, current default `master` at commit `b1c94e06fdf2dd3cb14ed07b05e38aa4601ece03`; separate `main` at commit `ba22faeec24344f4d43622eddf10e1d181d43922`, 2025. [Official repository](https://github.com/wvuvl/SiamABC). [Pinned SiamABC source](https://github.com/wvuvl/SiamABC/tree/b1c94e06fdf2dd3cb14ed07b05e38aa4601ece03). [Unrelated `main` branch state](https://github.com/wvuvl/SiamABC/tree/ba22faeec24344f4d43622eddf10e1d181d43922). Accessed: 2026-08-24.

Use: RESOURCE AVAILABILITY FACT / CODE FACT — SiamABC source and ten committed tracker-model files are available on `master`; a single-video demo is documented. Limit: `main` contains unrelated AEVT material, and `eval_SiamABC.py` imports absent `eval_data` and `eval_toolkit` trees that are neither submodules nor requirements; a usable benchmark evaluation protocol is therefore not verified from the official repository.

## R52

Y. Li, T. Geller, Y. Kim, and P. Panda, “SEENN: Towards Temporal Spiking Early Exit Neural Networks,” in *Advances in Neural Information Processing Systems*, vol. 36, 2023, pp. 63327–63342, doi: [10.52202/075280-2764](https://doi.org/10.52202/075280-2764). [Official proceedings page](https://proceedings.neurips.cc/paper_files/paper/2023/hash/c801e68207da477bbc44182b9fac1129-Abstract.html). Accessed: 2026-08-25.

Use: input-conditioned SNN timestep allocation and temporal early exit as a boundary on broad adaptive-SNN novelty language. Limit: classification/general SNN rather than RGB-SOT; no visual-tracking MRM or distractor-conditioned retrieval allocation.

## R53

Z. Zhuge, P. Wang, X. Yao, and J. Cheng, “Towards Efficient Spiking Transformer: a Token Sparsification Framework for Training and Inference Acceleration,” in *Proceedings of the 41st International Conference on Machine Learning (ICML)*, *Proceedings of Machine Learning Research*, vol. 235, 2024, pp. 62768–62778. [Official PMLR page](https://proceedings.mlr.press/v235/zhuge24b.html). Accessed: 2026-08-25.

Use: spiking-transformer token sparsification and temporal importance as a boundary on broad adaptive-SNN novelty language. Limit: not visual tracking or an RGB-SOT MRM method; its token-sparsification objective does not allocate retrieval from distractor ambiguity.

## R54

Z. Zhou, Y. Lu, Y. Jia, K. Che, J. Niu, L. Huang, X. Shi, Y. Zhu, G. Li, Z. Yu, and L. Yuan, “Spiking Transformer with Experts Mixture,” in *Advances in Neural Information Processing Systems*, vol. 37, 2024, pp. 10036–10059, doi: [10.52202/079017-0322](https://doi.org/10.52202/079017-0322). [Official proceedings page](https://proceedings.neurips.cc/paper_files/paper/2024/hash/137101016144540ed3191dc2b02f09a5-Abstract-Conference.html). Accessed: 2026-08-25.

Use: conditional sparse expert computation in spiking transformers as a boundary on broad adaptive-SNN novelty language. Limit: not visual tracking or an RGB-SOT MRM method; capacity routing is not template retrieval conditioned on distractor ambiguity.

## R55

W. Wei, X. Zhou, M. Zhang, A. Belatreche, Q. Sun, Y. Shan, D. Zhang, Z. Zhou, Z. Ma, Y. Yang, and H. Li, “TP-Spikformer: Token Pruned Spiking Transformer,” in *International Conference on Learning Representations (ICLR)*, 2026. [Official OpenReview forum](https://openreview.net/forum?id=L5llQD0nMf). [Official OpenReview PDF](https://openreview.net/pdf?id=L5llQD0nMf). Accessed: 2026-08-25.

Use: closest spiking-token/block-pruning adversary, including event-based object-tracking coverage, for broad adaptive-SNN novelty language. Limit: event-based tracking is not generic RGB bbox-SOT MRM evidence; the fixed spatiotemporal token criterion is not MRM-scale/template allocation conditioned on distractor ambiguity.

## R56

T. Lin, Y. Bai, S. Liang, R. Niu, and X. Wei, “Adaptive Capacity Autoregressive Visual Tracking,” in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2026, pp. 13574–13583. [Official CVF page](https://openaccess.thecvf.com/content/CVPR2026/html/Lin_Adaptive_Capacity_Autoregressive_Visual_Tracking_CVPR_2026_paper.html). Accessed: 2026-08-25.

Use: difficulty-conditioned high/low tracker capacity in the same autoregressive tracking setting. Limit: adaptive capacity is not MRM-specific and supplies no template-validity signal or SpikeTrack MRM allocation mechanism.

## R57

X. Zhou, P. Guo, L. Hong, J. Li, W. Zhang, W. Ge, and W. Zhang, “Reading Relevant Feature from Global Representation Memory for Visual Object Tracking,” in *Advances in Neural Information Processing Systems*, vol. 36, 2023, pp. 10814–10827, doi: [10.52202/075280-0476](https://doi.org/10.52202/075280-0476). [Official proceedings page](https://proceedings.neurips.cc/paper_files/paper/2023/hash/2349293cb1bf2ce36d5c566f660f957e-Abstract-Conference.html). Accessed: 2026-08-25.

Use: search-conditioned selection of relevant historical reference features with redundancy and compute control. Limit: fixed memory/token quotas do not provide SpikeTrack MRM ambiguity allocation or a calibrated whole-template active count.

## R58

S. Zhang, D. Zhang, and Q. Zou, “ATPTrack: Visual tracking with alternating token pruning of dynamic templates and search region,” *Neurocomputing*, vol. 625, Art. no. 129534, 2025, doi: [10.1016/j.neucom.2025.129534](https://doi.org/10.1016/j.neucom.2025.129534). Accessed: 2026-08-25.

Use: physical dynamic-template and search-region token pruning that couples robustness with compute reduction. Limit: fixed template inventory and pruning schedule; no calibrated whole-template validity or post-disappearance variable active-template count.

## R59

C. Xu, B. Zhong, Q. Liang, Y. Zheng, G. Li, and S. Song, “Less Is More: Token Context-Aware Learning for Object Tracking,” *Proceedings of the AAAI Conference on Artificial Intelligence*, vol. 39, no. 8, pp. 8824–8832, 2025, doi: [10.1609/aaai.v39i8.32954](https://doi.org/10.1609/aaai.v39i8.32954). Accessed: 2026-08-25.

Use: autoregressive high-quality reference-token retention and redundant-token removal for robustness and compute. Limit: fixed top-k token retention does not calibrate whole-template validity or vary the active template count.

## R60

J. Shi, Y. Yu, J. Shi, and H. Luo, “Exploring Reliable Spatiotemporal Dependencies for Efficient Visual Tracking,” *Proceedings of the AAAI Conference on Artificial Intelligence*, vol. 40, no. 11, pp. 8978–8987, 2026, doi: [10.1609/aaai.v40i11.37853](https://doi.org/10.1609/aaai.v40i11.37853). Accessed: 2026-08-25.

Use: quality-based reliable spatiotemporal memory maintenance with physical eviction of the lowest-quality historical token. Limit: the memory capacity is fixed, and the mechanism does not supply FARTrack whole-template absence validity or a variable active-template compute policy.

## R61

Y. Huang, L. Lin, W. Zhuang, Z. He, and X. Li, “Drift-Resilient Temporal Priors for Visual Tracking,” in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2026, pp. 6847–6856. [Official CVF page](https://openaccess.thecvf.com/content/CVPR2026/html/Huang_Drift-Resilient_Temporal_Priors_for_Visual_Tracking_CVPR_2026_paper.html). Accessed: 2026-08-25.

Use: per-frame temporal reliability calibration and compact dynamic priors. Limit: fixed historical slots and compact priors do not physically remove raw templates before embedding or define a variable FARTrack active-template compute policy.

## R62

W. Wu, Q. Liang, B. Zhong, H. Xia, Z. Mo, and S. Song, “An Efficient Token Compression Framework for Visual Object Tracking,” in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2026, pp. 6857–6867. [Official CVF page](https://openaccess.thecvf.com/content/CVPR2026/html/Wu_An_Efficient_Token_Compression_Framework_for_Visual_Object_Tracking_CVPR_2026_paper.html). Accessed: 2026-08-25.

Use: physical compression of historical-template tokens coupling efficiency and representation quality. Limit: token-level compression uses a fixed compression level; it does not expose an explicit whole-template validity variable or scenario-dynamic active count.

## R63

D. Lee, W. Choi, S. Lee, B. Yoo, E. Yang, and S. Hwang, “BackTrack: Robust template update via Backward Tracking of candidate template,” arXiv:2308.10604 [cs.CV], Aug. 2023, doi: [10.48550/arXiv.2308.10604](https://doi.org/10.48550/arXiv.2308.10604). [Official arXiv record](https://arxiv.org/abs/2308.10604). Accessed: 2026-08-25.

Use: explicit backward/cycle validation of candidate-template quality and rejection of unreliable updates. Limit: ARXIV-ONLY preprint, not peer reviewed; rejecting a write does not physically vary multi-template inference compute.

## R64

Y. Liu, R. Yu, F. Yin, X. Zhao, W. Zhao, W. Xia, and Y. Yang, “Learning Quality-aware Dynamic Memory for Video Object Segmentation,” in *Computer Vision – ECCV 2022*, Lecture Notes in Computer Science, vol. 13689, 2022, pp. 468–486, doi: [10.1007/978-3-031-19818-2_27](https://doi.org/10.1007/978-3-031-19818-2_27). [Official ECVA page](https://www.ecva.net/papers/eccv_2022/papers_ECCV/html/4636_ECCV_2022_paper.php). Accessed: 2026-08-25.

Use: adjacent VOS prior art for quality-aware frame admission/eviction and bounded memory. Limit: video object segmentation, not generic bbox-SOT baseline evidence; it does not establish FARTrack-style template-attention compute or active-template latency.

## R65

J. Zhou, Z. Pang, and Y.-X. Wang, “RMem: Restricted Memory Banks Improve Video Object Segmentation,” in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2024, pp. 18602–18611, doi: [10.1109/CVPR52733.2024.01760](https://doi.org/10.1109/CVPR52733.2024.01760). [Official CVF page](https://openaccess.thecvf.com/content/CVPR2024/html/Zhou_RMem_Restricted_Memory_Banks_Improve_Video_Object_Segmentation_CVPR_2024_paper.html). Accessed: 2026-08-25.

Use: adjacent VOS prior art for physical restricted-memory selection under redundant history. Limit: video object segmentation, not generic bbox-SOT baseline evidence; its fixed bank bound does not provide validity-calibrated variable template compute.

## R66

C. Huang, S. Lucey, and D. Ramanan, “Learning Policies for Adaptive Tracking With Deep Feature Cascades,” in *Proceedings of the IEEE International Conference on Computer Vision (ICCV)*, 2017, pp. 105–114, doi: [10.1109/ICCV.2017.21](https://doi.org/10.1109/ICCV.2017.21). [Official CVF PDF](https://openaccess.thecvf.com/content_ICCV_2017/papers/Huang_Learning_Policies_for_ICCV_2017_paper.pdf). Accessed: 2026-08-25.

Use: foundational frame-difficulty-conditioned feature-depth allocation in single-object tracking. Limit: generic SOT feature-cascade policy; it does not use AsymTrack’s T/S/B family or HiT-DyHiT’s named routes.

## R67

C. Ying and K. Fragkiadaki, “Depth-Adaptive Computational Policies for Efficient Visual Tracking,” in *Energy Minimization Methods in Computer Vision and Pattern Recognition*, M. Pelillo and E. R. Hancock, Eds., Lecture Notes in Computer Science, vol. 10746. Cham, Switzerland: Springer, 2018, pp. 109–122, doi: [10.1007/978-3-319-78199-0_8](https://doi.org/10.1007/978-3-319-78199-0_8). Accessed: 2026-08-25.

Use: foundational cost-aware tracker-depth policy under object and frame difficulty. Limit: generic SOT adaptive depth from the revised EMMCVPR 2017 proceedings; it does not use AsymTrack’s T/S/B family or HiT-DyHiT’s named routes.

## R68

J. Zhu, X. Chen, H. Diao, S. Li, J.-Y. He, C. Li, B. Luo, D. Wang, and H. Lu, “Exploring Dynamic Transformer for Efficient Object Tracking,” *IEEE Transactions on Neural Networks and Learning Systems*, vol. 36, no. 8, pp. 15502–15514, Aug. 2025, doi: [10.1109/TNNLS.2025.3545752](https://doi.org/10.1109/TNNLS.2025.3545752). Accessed: 2026-08-25.

Use: easy/hard dynamic route allocation and attribute-conditioned compute in single-object tracking. Limit: generic RGB SOT dynamic routing; it does not use AsymTrack’s T/S/B family or HiT-DyHiT’s named routes.

## R69

X. Yang, D. Zeng, X. Wang, Y. Wu, H. Ye, Q. Zhao, and S. Li, “Adaptively Bypassing Vision Transformer Blocks for Efficient Visual Tracking,” *Pattern Recognition*, vol. 161, Art. no. 111278, May 2025, doi: [10.1016/j.patcog.2024.111278](https://doi.org/10.1016/j.patcog.2024.111278). Accessed: 2026-08-25.

Use: target- and scene-dependent transformer-block bypassing in generic single-object tracking. Limit: generic RGB SOT block routing; it does not use AsymTrack’s T/S/B family or HiT-DyHiT’s named routes.

## R70

Y. Li, M. Liu, Y. Wu, X. Wang, X. Yang, and S. Li, “Learning Adaptive and View-Invariant Vision Transformer for Real-Time UAV Tracking,” in *Proceedings of the 41st International Conference on Machine Learning (ICML)*, Proceedings of Machine Learning Research, vol. 235, 2024, pp. 28403–28420. [Official PMLR page](https://proceedings.mlr.press/v235/li24ax.html). Accessed: 2026-08-25.

Use: adaptive block activation combined with view-invariant representation for UAV tracking. Limit: UAV-oriented mechanism and novelty-boundary evidence only; its benchmark results are not generic RGB-SOT equivalence evidence.

## R71

C. Xue, B. Zhong, Q. Liang, Y. Zheng, N. Li, Y. Xue, and S. Song, “Similarity-Guided Layer-Adaptive Vision Transformer for UAV Tracking,” in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2025, pp. 6730–6740. [Official CVF page](https://openaccess.thecvf.com/content/CVPR2025/html/Xue_Similarity-Guided_Layer-Adaptive_Vision_Transformer_for_UAV_Tracking_CVPR_2025_paper.html). Accessed: 2026-08-25.

Use: similarity-guided layer-adaptive capacity and representation-redundancy control for UAV tracking. Limit: UAV-oriented mechanism and novelty-boundary evidence only; its benchmark results are not generic RGB-SOT equivalence evidence.

## R72

Y. Wu, X. Wang, D. Zeng, H. Ye, X. Xie, Q. Zhao, and S. Li, “Learning Motion Blur Robust Vision Transformers for Real-Time UAV Tracking,” *Expert Systems with Applications*, vol. 297, Part B, Art. no. 129445, Feb. 2026, doi: [10.1016/j.eswa.2025.129445](https://doi.org/10.1016/j.eswa.2025.129445). Accessed: 2026-08-25.

Use: dynamic early exit combined with motion-blur and fast-motion robustness for UAV tracking. Limit: UAV-oriented mechanism and novelty-boundary evidence only; its benchmark results are not generic RGB-SOT equivalence evidence.

## R73

Y. Feng, D. Yuan, J. Song, H. Liu, Y. Yang, and T. Zhang, “Efficient Early Exit Single Object Tracking via General Distribution,” *Neurocomputing*, vol. 661, Art. no. 131888, Jan. 2026, doi: [10.1016/j.neucom.2025.131888](https://doi.org/10.1016/j.neucom.2025.131888). Accessed: 2026-08-25.

Use: generic SOT early exit conditioned by object/background distinguishability. Limit: it does not implement AsymTrack family switching or paired HiT-DyHiT forced-route regret measurement.

## R74

T. Ding, H. Yang, L. Shi, J. Li, X. Hu, J. Yang, and Y. Tai, “Adaptive Depth Lightweight RGB-T Tracking with Holistic Token Routing,” in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2026, pp. 20942–20952. [Official CVF page](https://openaccess.thecvf.com/content/CVPR2026/html/Ding_Adaptive_Depth_Lightweight_RGB-T_Tracking_with_Holistic_Token_Routing_CVPR_2026_paper.html). Accessed: 2026-08-25.

Use: confidence-calibrated tracking early exit and adaptive depth. Limit: RGB-T tracking, not RGB-only; its route topology is not HiT-DyHiT’s named depth routing.

## R75

P. Poggi, D. Kumar, T. Tulabandhula, and A. R. Trivedi, “Uncertainty-Guided Inference-Time Depth Adaptation for Transformer-Based Visual Tracking,” arXiv:2602.16160 [cs.CV], Feb. 2026, doi: [10.48550/arXiv.2602.16160](https://doi.org/10.48550/arXiv.2602.16160). [Official arXiv record](https://arxiv.org/abs/2602.16160). Accessed: 2026-08-25.

Use: uncertainty- and temporal-feedback-guided inference-depth adaptation in visual tracking. Limit: ARXIV-ONLY preprint, not peer reviewed; it does not establish HiT-DyHiT’s named route mechanism.

## R76

D.-H. Park, M. Baek, J.-H. Ha, C.-S. Park, J. Ganiev, and S.-H. Bae, “MVLM: Template-Free Tracking via Vision-Language Margin Confidence and Memory-Gated Tracking,” in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 2026, pp. 35156–35165. [Official CVF page](https://openaccess.thecvf.com/content/CVPR2026/html/Park_MVLM_Template-Free_Tracking_via_Vision-Language_Margin_Confidence_and_Memory-Gated_Tracking_CVPR_2026_paper.html). Accessed: 2026-08-25.

Use: target-competitor margin and memory gating of compact local versus global re-localization modes. Limit: vision-language/template-free tracking; local/global spatial mode gating is not HiT-DyHiT depth routing.

## R77

L. Meronen, M. Trapp, A. Pilzer, L. Yang, and A. Solin, “Fixing Overconfidence in Dynamic Neural Networks,” in *Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision (WACV)*, 2024, pp. 2680–2690. [Official CVF page](https://openaccess.thecvf.com/content/WACV2024/html/Meronen_Fixing_Overconfidence_in_Dynamic_Neural_Networks_WACV_2024_paper.html). Accessed: 2026-08-25.

Use: adjacent prior art for calibrating overconfident dynamic-network exit decisions. Limit: dynamic image classification, not visual-tracking evidence.
