# F6 — Desk-only resource delta and narrow 2026 candidate-universe refresh

Date: 2026-08-29

Branch: `codex/f6-refresh`

Required starting HEAD: `3394789c55a9136b83be912aaed993fb862837ea`

## 1. Boundary and no-execution declaration

This is the independent lean F6 desk lane authorized by the Manager protocol. It inspected only author-controlled repositories and asset indexes, official publication pages, repository metadata, and the two authorized historical F2 reports. It did not merge either F2 branch.

- Models/checkpoints instantiated: **0**
- Trackers imported or executed: **0**
- Packages/environments installed or created: **0**
- Checkpoints, pretrained assets, or datasets downloaded: **0**
- Official repositories modified: **0**
- Benchmarks/profilers executed: **0**

No tracker was repaired. F2 remains closed. F3 HG6 was not opened. No score, rank, shortlist, main baseline, architecture, or scientific outcome was produced. A ready state below means only that a Manager may consider a new desk F0; it is not execution authorization.

## 2. Search/time/record cap declaration

The active refresh remained within the **90-minute** cap and stopped at the record caps: **12 total records**, comprising **5 resource records** and **7 new-family records**. No full Stage-1 broad search was repeated.

The bounded search used these surfaces only:

| Surface | Narrow purpose |
|---|---|
| Exact author repositories and their README/install/requirements/config/builder/evaluator/release metadata | Resolve F6-R01 through F6-R05 and validate first-party resource contracts |
| Author-linked Google Drive/Baidu/OneDrive folder or file indexes | Check exact identity/mapping without downloading an asset |
| [CVF Open Access CVPR 2026](https://openaccess.thecvf.com/CVPR2026) | Exact-title 2026 SOT delta |
| [ECCV 2026 accepted-paper surface](https://eccv.ecva.net/virtual/2026/papers.html) | Exact-title 2026 SOT delta |
| Official OpenReview/AAAI/PMLR 2026 venue surfaces and exact-title follow-ups | Confirm that re-encountered families were already represented or lacked a new eligible first-party release |

The search ended once the seven-new-family ceiling was filled. Community indexes were used only as discovery hints; no community mapping was accepted as evidence.

## 3. UTPTrack resource delta

**Record:** F6-R01 / CX010

**Official source:** [EIT-NLP/UTPTrack at the pinned/current head](https://github.com/EIT-NLP/UTPTrack/tree/84e0f49711254a44f5308faaa9a2405db1964dd7/UTPTrack-O)

**Head/release delta:** current default-branch head is still `84e0f49711254a44f5308faaa9a2405db1964dd7`; no GitHub release was present.

1. **Is `visdom` officially documented? — Yes.** The official README describes Visdom visualization, and the repository's `UTPTrack-O/install.sh` installs `visdom`; `requirements.txt` pins `visdom==0.2.4`.
2. **Is `jpeg4py` required or optional? — Required by the released construction import path.** Both official dependency recipes install it, and `lib/train/data/image_loader.py` imports it at module import time. The later decode fallback does not make the package import optional.
3. **Is legacy `torch._six` compatibility documented? — Not as a separate compatibility note.** The pinned source imports `torch._six`; the official README installation route calls `install.sh`, which pins legacy PyTorch 1.9/torchvision 0.10. The separate `requirements.txt` freezes a different legacy pair, so a later F0 must seal one recipe rather than combine them.
4. **Is there an official environment/container/lock covering the complete known path? — There is no `environment.yml`, container, or lock file, but there is an official auditable install recipe.** The README-to-`install.sh` route accounts for all three dependencies encountered by F2 before strict load: legacy `torch._six`, `jpeg4py`, and `visdom`.
5. **Has checkpoint/config/evaluator mapping changed? — No.** The head is identical to the pin and no release delta was found.
6. **Does an official delta remove every known pre-strict-load blocker? — No source-code delta occurred; however, desk reconciliation verified that the existing first-party README/install contract accounts for every currently known blocker.** This is sufficient for resource reentry, not proof that construction or strict load succeeds.

**State: `RESOURCE_REENTRY_READY_FOR_F0`.** The minimum next action is a Manager-opened desk F0 that seals the README plus `install.sh` as one dependency contract. Any install, import, model construction, or strict-load attempt needs later explicit authorization.

## 4. MCITrack resource delta

**Record:** F6-R02 / CX038

**Official source:** [kangben258/MCITrack at the pinned/current head](https://github.com/kangben258/MCITrack/tree/e667193eaec4c8a73d4bdd856a662aecdb844b43), [author-linked pretrained folder](https://drive.google.com/drive/folders/1qDAMcU3JpahV7MriEOl4KfjKvAAFXd3E), [exact file ID](https://drive.google.com/file/d/1hxth6RWiJ-3rY21CClZqjl2xsL07Kt17/view)

**Head/release delta:** current default-branch head is still `e667193eaec4c8a73d4bdd856a662aecdb844b43`; no GitHub release was present.

1. **Is `fast_itpn_base_clipl_e1600.pt` publicly linked? — Yes.** The exact filename is visible in the pretrained-weight folder linked by the official README.
2. **Is there a stable ID or checksum? — Stable folder and file IDs are available; no checksum is exposed.** The exact file ID is `1hxth6RWiJ-3rY21CClZqjl2xsL07Kt17`.
3. **Is it required even with the full `MCITRACK_ep0300.pth.tar`? — Yes on the released main-process path.** The B224 config names `/pretrained/fast_itpn_base_clipl_e1600.pt`; the encoder enables pretraining on the main process; Fast-iTPN calls `torch.load` during network construction before the tracker applies the full released checkpoint.
4. **Is there an official bypass? — No.** No documented construction path disables the bootstrap load before the full checkpoint strict load.
5. **Has checkpoint/config/evaluator mapping changed? — No.** The code head and release surface are unchanged. The official Models folder still organizes released full checkpoints by config family.

**State: `RESOURCE_REENTRY_READY_FOR_F0`.** The exact author-controlled bootstrap asset, stable identity, required path, and relation to the full checkpoint are now coherent enough for a new desk resource seal. No asset was downloaded. A later Manager authorization would be required to acquire it, record its hash, construct the model, or attempt strict load.

## 5. JDTrack resource delta

**Record:** F6-R03 / CX046

**Official source:** [hexdjx/VisTrack at the pinned/current head](https://github.com/hexdjx/VisTrack/tree/f07acc942dfdc0bf78f437955a3ae1fc5e62b7fc), [author-linked Drive root](https://drive.google.com/drive/folders/182NbsBrVR9PICR9aSkb2IhUDvrlSsTDT)

**Head/release delta:** head remains `f07acc942dfdc0bf78f437955a3ae1fc5e62b7fc`; no GitHub release was present.

The official model hierarchy still does not expose the exact evaluator-required `JDTrack_online_target_fuse.pth.tar` filename or a JDTrack-specific checkpoint/config mapping. Other family weights in the same umbrella repository are not substitutes.

**State: `RESOURCE_HOLD_NO_CHANGE`.** Minimum next evidence remains an author-controlled exact JDTrack checkpoint link plus its config/evaluator mapping.

## 6. UMDATrack resource delta

**Record:** F6-R04 / CX051

**Official source:** [Z-Z188/UMDATrack at the pinned/current head](https://github.com/Z-Z188/UMDATrack/tree/5d609bfcfb3a27161f9f4bd23bda518d6656909c), [author-linked Drive root](https://drive.google.com/drive/folders/1fondgxHRdglg9JZkg_UkfqqSUmhqLUA9)

**Head/release delta:** head remains `5d609bfcfb3a27161f9f4bd23bda518d6656909c`; no GitHub release was present.

The official stage-2 folder exposes `UMDATrack_dark_prompt_ep0050.pth.tar`, `UMDATrack_haze_prompt_ep0050.pth.tar`, and `UMDATrack_rainy_prompt_ep0050.pth.tar`. That availability does not repair the prior incoherence: the documented `got10k_haze` registry resolution and the generated adverse-dataset evaluator paths remain unaddressed by an official delta.

**State: `RESOURCE_HOLD_NO_CHANGE`.** Minimum next evidence is one author-controlled checkpoint-to-config-to-dataset-registry evaluator mapping. No inferred manual repair is accepted.

## 7. UncTrack resource delta

**Record:** F6-R05 / CX053

**Official source:** [ManOfStory/UncTrack at the pinned/current head](https://github.com/ManOfStory/UncTrack/tree/61bd4be673ac32dd8948f995ce4548855d0ab1d0)

**Head/release delta:** head remains `61bd4be673ac32dd8948f995ce4548855d0ab1d0`; no GitHub release was present.

No author-controlled code or release documentation resolves the precise PMN mask and mutable K/V bounded-state export/runtime contract. The previous deep audit was not repeated.

**State: `RESOURCE_HOLD_NO_CHANGE`.** Minimum next evidence is an official bounded-state export/runtime contract. No repair or runtime probe is authorized.

## 8. Narrow 2026 candidate delta

All seven paper families below are accepted 2026 works on official venue surfaces and were absent by exact family/title search from `screening/candidate_screening_matrix.csv`, `references/source_manifest.csv`, and `references/references.md`. Resource readiness was judged only from author-controlled releases.

| Record | Method | Official acceptance/resource evidence | Desk finding | State |
|---|---|---|---|---|
| F6-N01 | TGTrack: Temporal Generative Learning for Unified Single Object Tracking | [CVPR 2026 paper](https://openaccess.thecvf.com/content/CVPR2026/html/Geng_TGTrack_Temporal_Generative_Learning_for_Unified_Single_Object_Tracking_CVPR_2026_paper.html); [author repository at `797d971c`](https://github.com/wtg1/TGTrack/tree/797d971c073488c4708c6b12cd58dfb74d07f4c6) | The repository is a minimal placeholder with no code, trained checkpoint, or evaluator. | `NEW_CANDIDATE_REFERENCE_ONLY` |
| F6-N02 | ODONet: Online Dynamic Offset Network for Visual Object Tracking | [ECCV 2026 poster 4749](https://eccv.ecva.net/virtual/2026/poster/4749); [author repository at `5e9469d7`](https://github.com/WhiteButterflies/ODONet/tree/5e9469d7dc85924192687eaa2f919bef39518f50) | Code/config/evaluator and a linked model bundle exist, but exact checkpoint-to-config identity is unsealed and the documented Fast-iTPN pretrain link is TODO. | `NEW_CANDIDATE_REFERENCE_ONLY` |
| F6-N03 | MaST: Motion-aware Sparse Pipeline for Lightweight Object Tracking | [ECCV 2026 poster 5707](https://eccv.ecva.net/virtual/2026/poster/5707); [author repository at `3d507e92`](https://github.com/TsingWei/MaST/tree/3d507e9285efd6661efb5e3fe7b388b46ee041e8) | Code, exact model registry, pinned requirements, evaluator, and three committed trained ONNX tracker files (`MaST-nano.onnx`, `MaST-small.onnx`, `MaST-tiny.onnx`) are present. | `NEW_CANDIDATE_F0_READY` |
| F6-N04 | SENTRY: SAM2-Enhanced Neighbor-Aware and Temporally Reasoned Memory for Visual Tracking | [ECCV 2026 poster 4693](https://eccv.ecva.net/virtual/2026/poster/4693); [author repository at `dd4486c7`](https://github.com/HamadYA/SENTRY/tree/dd4486c7eeadd7e7022854e29e95e3101390ce65) | The training-free release includes code/config/environment metadata, bbox benchmark evaluators, and an exact official SAM2.1 base-checkpoint download contract for four scales. | `NEW_CANDIDATE_F0_READY` |
| F6-N05 | DASTrack: Rethinking Temporal Modeling in Visual Object Tracking via Decoupled Auxiliary Supervision | [ECCV 2026 poster 4704](https://eccv.ecva.net/virtual/2026/poster/4704) | The bounded exact-title/author search found no first-party code, trained tracker checkpoint, or evaluator. | `NEW_CANDIDATE_REFERENCE_ONLY` |
| F6-N06 | TR-MoE: Temporal Reliability-Aware Mixture-of-Experts for Robust Tracking | [ECCV 2026 poster 4745](https://eccv.ecva.net/virtual/2026/poster/4745) | The bounded exact-title/author search found no first-party code, trained tracker checkpoint, or evaluator. | `NEW_CANDIDATE_REFERENCE_ONLY` |
| F6-N07 | SFDATrack: Generalized Source-Free Domain Adaptive Tracking Under Adverse Weather Conditions | [ECCV 2026 poster 4723](https://eccv.ecva.net/virtual/2026/poster/4723); [author repository at `048d337c`](https://github.com/watcherBR0/sfdatrack/tree/048d337ca1d0bc4a0e9550fa9b14b19b6ba4bc5e) | Code, environment instructions, evaluator, and an author-linked evaluation-weight bundle exist, but the asset identity is not exactly mapped to the `baseline_vit` checkpoint path expected by the parameter code. | `NEW_CANDIDATE_REFERENCE_ONLY` |

`NEW_CANDIDATE_F0_READY` means only that the first-party desk contract is complete enough for a Manager-opened resource seal. It does not establish compatibility, performance, deployability, or scientific priority.

## 9. Deduplication summary

- Exact family/title searches found none of the seven records in the canonical matrix, Stage-1 source manifest, or canonical references.
- 2026 works already represented in those files—including UTPTrack, FARTrack, SpikeTrack, UETrack, and other Stage-1 families encountered on the official venue surfaces—were not added again.
- UAV-only, segmentation-only, multimodal-only-without-generic-core, ordinary compression/porting, and arXiv-only discovery hits were excluded rather than consuming records.
- SFDATrack is related to the UMDATrack adverse-weather lineage, but it is a distinct accepted source-free adaptation method with a new first-party resource release. It is retained conservatively as reference-only, not promoted as a generic deployment candidate.
- New-family count after deduplication: **7**. Duplicate/out-of-scope rows created: **0**.

## 10. Actionable records

Actionable here means eligible only for Manager consideration of a new desk F0.

| Record | State | Minimum next action |
|---|---|---|
| F6-R01 UTPTrack | `RESOURCE_REENTRY_READY_FOR_F0` | Seal README + `install.sh` as one dependency recipe; preserve the separate requirements-file conflict for explicit reconciliation. |
| F6-R02 MCITrack | `RESOURCE_REENTRY_READY_FOR_F0` | Seal exact Drive folder/file IDs, config path, builder order, and full-checkpoint mapping; do not acquire the asset without later authorization. |
| F6-N03 MaST | `NEW_CANDIDATE_F0_READY` | Seal exact commit/blob identities, model registry, license, initialization, and evaluator protocol. |
| F6-N04 SENTRY | `NEW_CANDIDATE_F0_READY` | Seal one host/scale, exact base-checkpoint URL, dependency/license boundary, and bbox evaluator protocol. |

## 11. Non-actionable records

| Record | State | Blocking evidence still required |
|---|---|---|
| F6-R03 JDTrack | `RESOURCE_HOLD_NO_CHANGE` | Exact first-party final tracker checkpoint and mapping |
| F6-R04 UMDATrack | `RESOURCE_HOLD_NO_CHANGE` | Coherent first-party stage-2/config/dataset/evaluator contract |
| F6-R05 UncTrack | `RESOURCE_HOLD_NO_CHANGE` | First-party bounded PMN mask and mutable K/V export/runtime contract |
| F6-N01 TGTrack | `NEW_CANDIDATE_REFERENCE_ONLY` | Substantive code, trained checkpoint, and evaluator release |
| F6-N02 ODONet | `NEW_CANDIDATE_REFERENCE_ONLY` | Exact checkpoint/pretrain identity and config mapping |
| F6-N05 DASTrack | `NEW_CANDIDATE_REFERENCE_ONLY` | First-party code, trained checkpoint, and evaluator |
| F6-N06 TR-MoE | `NEW_CANDIDATE_REFERENCE_ONLY` | First-party code, trained checkpoint, and evaluator |
| F6-N07 SFDATrack | `NEW_CANDIDATE_REFERENCE_ONLY` | Exact released weight identity and `baseline_vit` evaluator mapping |

## 12. Final refresh decision

**`ACTIONABLE_RESOURCE_AND_NEW_CANDIDATE_FOUND`**

- Resource reentry ready: **2** — UTPTrack, MCITrack.
- Resource hold/no change: **3** — JDTrack, UMDATrack, UncTrack.
- New 2026 F0-ready: **2** — MaST, SENTRY.
- New 2026 reference-only: **5** — TGTrack, ODONet, DASTrack, TR-MoE, SFDATrack.
- Total records: **12**; new-family records: **7**.

This decision does not reopen F2, open F3 HG6, authorize model execution, start S1–S7, create a primary shortlist, select a main baseline, or propose an architecture. Stop at Manager F6 reconciliation.
