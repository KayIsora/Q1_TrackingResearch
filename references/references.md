# References and source notes

Citation style: IEEE. Links were checked on **2026-08-17**. A link is evidence only for the claim explicitly attributed to it; it is not blanket support for a broader conclusion.

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

R. Zaveri, S. Patel, Y. Gu, and G. Doretto, “Improving Accuracy and Generalization for Efficient Visual Tracking,” in *Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision (WACV)*, 2025, pp. 9450–9460. [Official CVF paper](https://openaccess.thecvf.com/content/WACV2025/html/Zaveri_Improving_Accuracy_and_Generalization_for_Efficient_Visual_Tracking_WACV_2025_paper.html). Accessed: 2026-08-17.

Use: example of an efficient visual-tracking research candidate audited before the current baseline decision. Limit: no claim here of original Jetson Nano feasibility.

## R11

G. Wang *et al.*, “FARTrack: Fast Autoregressive Visual Tracking with High Performance,” *International Conference on Learning Representations (ICLR)*, 2026. [Official OpenReview forum](https://openreview.net/forum?id=lq7Zfr8kAS). [Official OpenReview PDF](https://openreview.net/pdf?id=lq7Zfr8kAS). Accessed: 2026-08-17.

Use: primary source for FARTrack architecture, Task-Specific Self-Distillation, Inter-frame Autoregressive Sparsification, multi-template experiments, model sizes/MACs, reported benchmark values, training hardware/procedure, speed-test hardware, and author-reported limitations. Limit: generic SOT evaluation does not prove target-person identity preservation or Jetson Nano feasibility.

## R12

MIV-XJTU, “FARTrack — official PyTorch implementation,” GitHub repository, 2026. [Official repository](https://github.com/MIV-XJTU/FARTrack). Accessed: 2026-08-17.

Use: source code, released checkpoints/configurations, implementation-level audit, and reproduction path for Tiny/Nano/Pico. Limit: repository behavior must be cited as CODE FACT and kept distinct from claims in the paper.
