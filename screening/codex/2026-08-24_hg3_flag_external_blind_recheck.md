# External blind HG3 flag recheck

Date: **2026-08-24**

Lane: **Codex independent verification lane**

Scope: **six HG3-flagged families in the 20-family pre-flag scientific-audit queue**

## Decision rule and evidence boundary

This recheck applies the locked HG3 rule in the [systematic screening protocol](../../docs/11_systematic_screening_protocol.md#hg3--official-reproducibility-assets): `PASS` requires official source code, the checkpoint actually required by the method, and a usable official evaluation script/protocol or integration sufficient for a realistic baseline-reproduction attempt. Repository availability alone is not successful reproduction. Missing or unresolved evidence is not interpreted favorably.

The six official repositories were inspected in fresh detached checkouts at the pinned commits registered in [R28, R30, R36, R42, R46, and R51](../../references/references.md). Author-linked model resources were inspected directly where accessible. No blog, PapersWithCode entry, search snippet, AI summary, or unofficial implementation was used as primary evidence. No end-to-end benchmark reproduction is claimed.

## CX020 — SAMURAI

Decision: **PASS**

### Source-code evidence

- **CODE FACT:** The official source is pinned at `yangchris11/samurai@76ba195984892b0d1e3db5d9c9f90bb62175680a` ([R28](../../references/references.md#r28)). Method-specific behavior is implemented in code: the official configuration enables `samurai_mode` and its thresholds ([configuration](https://github.com/yangchris11/samurai/blob/76ba195984892b0d1e3db5d9c9f90bb62175680a/sam2/sam2/configs/samurai/sam2.1_hiera_b%2B.yaml#L117-L125)); the model initializes the motion state and SAMURAI parameters, combines mask and motion IoU for candidate selection, and filters memory using mask/object/motion scores ([initialization](https://github.com/yangchris11/samurai/blob/76ba195984892b0d1e3db5d9c9f90bb62175680a/sam2/sam2/modeling/sam2_base.py#L198-L218), [selection](https://github.com/yangchris11/samurai/blob/76ba195984892b0d1e3db5d9c9f90bb62175680a/sam2/sam2/modeling/sam2_base.py#L420-L498), [memory filtering](https://github.com/yangchris11/samurai/blob/76ba195984892b0d1e3db5d9c9f90bb62175680a/sam2/sam2/modeling/sam2_base.py#L663-L680)).

### Checkpoint evidence

- **RESOURCE AVAILABILITY FACT:** SAMURAI is explicitly training-free and directly uses SAM 2.1 weights; it does not require a family-trained SAMURAI checkpoint ([official explanation](https://github.com/yangchris11/samurai/blob/76ba195984892b0d1e3db5d9c9f90bb62175680a/README.md#L108-L110)).
- **RESOURCE AVAILABILITY FACT:** The pinned repository provides direct official download commands for SAM 2.1 tiny, small, base-plus, and large checkpoints ([downloader](https://github.com/yangchris11/samurai/blob/76ba195984892b0d1e3db5d9c9f90bb62175680a/sam2/checkpoints/download_ckpts.sh#L39-L57)). The checked-in inference runner selects the corresponding SAM 2.1 checkpoint, using base-plus by default ([runner configuration](https://github.com/yangchris11/samurai/blob/76ba195984892b0d1e3db5d9c9f90bb62175680a/scripts/main_inference.py#L30-L44)).

### Evaluation evidence

- **CODE FACT:** `scripts/main_inference.py` loads the LaSOT test list, initializes the tracker from the first-frame benchmark box, propagates through the sequence, and writes per-sequence `x,y,w,h` result files ([setup](https://github.com/yangchris11/samurai/blob/76ba195984892b0d1e3db5d9c9f90bb62175680a/scripts/main_inference.py#L30-L44), [initialization/inference](https://github.com/yangchris11/samurai/blob/76ba195984892b0d1e3db5d9c9f90bb62175680a/scripts/main_inference.py#L67-L84), [result writer](https://github.com/yangchris11/samurai/blob/76ba195984892b0d1e3db5d9c9f90bb62175680a/scripts/main_inference.py#L122-L126)). `scripts/main_inference_chunk.py` provides a parameterized/chunked LaSOT-ext path ([CLI and test-list path](https://github.com/yangchris11/samurai/blob/76ba195984892b0d1e3db5d9c9f90bb62175680a/scripts/main_inference_chunk.py#L120-L140)). `scripts/demo.py` separately supports first-frame bounding-box initialization for user videos/frame folders ([demo path](https://github.com/yangchris11/samurai/blob/76ba195984892b0d1e3db5d9c9f90bb62175680a/scripts/demo.py#L42-L77)).

### Blocking issue / residual risk

- **CODE FACT:** The pinned, directly verified benchmark runners cover LaSOT/LaSOT-ext result generation. The README routes some metric computation and other benchmark details to an issue or official submission portals, and VOT-toolkit integration was not established as a complete generic path in the pinned tree ([evaluation note](https://github.com/yangchris11/samurai/blob/76ba195984892b0d1e3db5d9c9f90bb62175680a/README.md#L120-L128)).
- **INTERPRETATION:** This is a scope/reproduction risk, not an HG3 blocker: the verified LaSOT result-generation protocol is already sufficient for a realistic generic benchmark attempt. The absent family-trained checkpoint is expected under the verified training-free design.

### Final HG3 rationale

Official method source, the actual official SAM 2.1 inference weights, and a usable official generic benchmark runner/result writer are all present. **HG3 PASS.**

## CX024 — DAM4SAM

Decision: **PASS**

### Source-code evidence

- **CODE FACT:** The official source is pinned at `jovanavidenovic/DAM4SAM@9c954504b39ebca4c412f207be0787c26bfac85a` ([R30](../../references/references.md#r30)). The distractor-aware method behavior is implemented in the tracker and memory code: alternative-mask selection and distractor tests are applied before adding frames to distractor-aware memory ([tracker logic](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/dam4sam_tracker.py#L197-L261)); the video predictor exposes the memory-add operation ([predictor](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/sam2/sam2_video_predictor.py#L328-L347)); and the model combines distractor-aware conditioning memory with recent-appearance memory ([memory logic](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/sam2/modeling/sam2_base.py#L537-L617)).

### Checkpoint evidence

- **RESOURCE AVAILABILITY FACT:** The authors describe DAM4SAM as operating without additional training ([README](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/README.md#L39-L40)). Its method-specific behavior is therefore code, while actual inference uses SAM 2.1 foundation checkpoints.
- **RESOURCE AVAILABILITY FACT:** Direct official download commands for all four SAM 2.1 checkpoints are included ([downloader](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/checkpoints/download_ckpts.sh#L39-L57)). The default `sam21pp-L` variant resolves to the downloaded large checkpoint; base-plus is also mapped coherently ([variant mapping](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/utils/utils.py#L27-L34)).

### Evaluation evidence

- **CODE FACT:** The official box-dataset runner enumerates sequences, loads precomputed SAM2 initialization masks, runs all frames, and writes standard bounding-box results; it exposes GOT-10k, LaSOT, and LaSOT-ext through its CLI ([sequence/result path](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/run_on_box_dataset.py#L25-L73), [CLI](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/run_on_box_dataset.py#L77-L102)). The README identifies an official archive of these masks and states that they were obtained from the ground-truth initialization boxes using the SAM2 image predictor ([mask protocol](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/README.md#L136-L146)). The GOT-10k adapter is self-contained in the pinned tree ([dataset adapter](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/utils/dataset_utils.py#L77-L112)).
- **CODE FACT:** A concrete VOT integration is present: the wrapper receives the initialization mask, tracks frames, and reports results ([wrapper](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/vot_wrapper_dam4sam.py#L55-L85)); the README supplies initialize/evaluate/analyze/report commands ([protocol](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/README.md#L117-L134)). Separately from the precomputed-mask benchmark runner, the official interactive example passes a bounding box to tracker initialization ([example](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/run_bbox_example.py#L23-L59)), and tracker code converts that box to a SAM 2 prompt and initialization mask ([bbox-to-mask path](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/dam4sam_tracker.py#L269-L338)).

### Blocking issue / residual risk

- **CODE FACT:** The pinned LaSOT adapters refer to sequence-list files absent from the repository, while the GOT-10k adapter does not ([LaSOT list dependency](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/utils/dataset_utils.py#L115-L172)). Small/tiny and SAM 2.0 variant paths omit the `checkpoints/` directory, whereas the default SAM 2.1 large path is coherent ([variant paths](https://github.com/jovanavidenovic/DAM4SAM/blob/9c954504b39ebca4c412f207be0787c26bfac85a/utils/utils.py#L27-L52)).
- **INTERPRETATION:** These are variant/dataset-specific residual risks. The verified default checkpoint path plus GOT-10k and VOT workflows are sufficient for a realistic baseline attempt.

### Final HG3 rationale

Official method source, the actual official SAM 2.1 weights used by this training-free design, and usable official GOT-10k/VOT evaluation paths are present. **HG3 PASS.**

## CX040 — MambaLCT

Decision: **FAIL**

### Source-code evidence

- **CODE FACT:** The official source is pinned at `GXNU-ZhongLab/MambaLCT@0457044f67a0a033b85c0447376fc4bde0cfc10d` ([R36](../../references/references.md#r36)). A nominal chain exists from `tracking/test.py` through the MambaLCT parameter and tracker modules to model construction and strict `checkpoint['net']` loading.
- **CODE FACT:** The normal project-root import chain is defective: `lib/models/mambalct/mamba.py` uses the top-level import `from rope import *`, while the repository's only `rope.py` is the sibling file `lib/models/mambalct/rope.py` ([faulting import](https://github.com/GXNU-ZhongLab/MambaLCT/blob/0457044f67a0a033b85c0447376fc4bde0cfc10d/lib/models/mambalct/mamba.py#L21-L24)). A clean import therefore requires an undocumented path workaround or source correction.

### Checkpoint evidence

- **RESOURCE AVAILABILITY FACT:** The README links an official [Models folder](https://drive.google.com/drive/folders/1PtpomZNItT6B7gdf4hnH3nGdnRJPVVT0) and a separate Raw Results folder ([official links](https://github.com/GXNU-ZhongLab/MambaLCT/blob/0457044f67a0a033b85c0447376fc4bde0cfc10d/README.md#L3-L6)). Direct metadata listing on 2026-08-24 exposed [`256_full/MambaLCT_ep0280.pth.tar`](https://drive.google.com/file/d/16n0mHOZAQNxntyvSuhEo6G6P8z7UK8sy/view), [`256_got/MambaLCT_ep0096.pth.tar`](https://drive.google.com/file/d/1F_7uHjUd2Aj-Uva15ek6EYNwbEzeQmtT/view), and [`384_full/MambaLCT_ep0291.pth.tar`](https://drive.google.com/file/d/1BFwYlPOCYeSNnZNA22qWRsKOCxRmUTNA/view); the released `384_got` folder (ID `1p4LROiWB3N_vliIrDp-dAVT-8_Hr-Cjl`) contained no file in that listing. These object IDs record the inspected mutable-resource snapshot; file contents were not downloaded or executed.
- **CODE FACT:** The official parameter code resolves the final model to `<save_dir>/checkpoints/train/mambalct/<yaml_name>/MambaLCT_ep<epoch>.pth.tar` ([resolution code](https://github.com/GXNU-ZhongLab/MambaLCT/blob/0457044f67a0a033b85c0447376fc4bde0cfc10d/lib/test/parameter/mambalct.py#L7-L29)). The four checked-in evaluation configurations require `baseline_256` epoch 300, `baseline_384` epoch 140, `baseline_got_256` epoch 280, and `baseline_got_384` epoch 100 ([configuration directory](https://github.com/GXNU-ZhongLab/MambaLCT/tree/0457044f67a0a033b85c0447376fc4bde0cfc10d/experiments/mambalct)). The names/directories in the official Models folder do not satisfy these contracts without undocumented selection, renaming, and placement.

### Evaluation evidence

- **CODE FACT:** Dataset runner and evaluator infrastructure exists, but all bundled command examples invoke `odtrack`, not MambaLCT ([examples](https://github.com/GXNU-ZhongLab/MambaLCT/blob/0457044f67a0a033b85c0447376fc4bde0cfc10d/tracking/test.py#L62-L70)). The bundled analysis script is likewise hard-coded to `odtrack`, parameter `baseline`, run 300 ([analysis script](https://github.com/GXNU-ZhongLab/MambaLCT/blob/0457044f67a0a033b85c0447376fc4bde0cfc10d/tracking/analysis_results.py#L9-L21)). No dependency/setup file or official MambaLCT end-to-end invocation accompanies the pinned repository.

### Blocking issue / residual risk

- **INTERPRETATION:** Poor documentation alone would not force failure if the official code formed a coherent path. Here it does not: a realistic attempt requires source/import repair, inference-checkpoint mapping and renaming, local path configuration, and replacement of unrelated shipped examples/analysis settings. These are cumulative official-release gaps, not merely proof that runtime reproduction has not yet been attempted.

### Final HG3 rationale

Source is available, but official checkpoint/evaluation support is insufficient to make baseline reproduction realistic under the locked HG3 rule. **HG3 FAIL.**

## CX046 — JDTrack

Decision: **PENDING**

### Source-code evidence

- **CODE FACT:** The official umbrella source is pinned at `hexdjx/VisTrack@f07acc942dfdc0bf78f437955a3ae1fc5e62b7fc` ([R42](../../references/references.md#r42)). JDTrack tracker, parameter, target-fusion model, dataset runner, and evaluator infrastructure are present. `pytracking/run_tracker.py` defaults directly to `jdtrack/jdtrack_vit` ([runner defaults](https://github.com/hexdjx/VisTrack/blob/f07acc942dfdc0bf78f437955a3ae1fc5e62b7fc/pytracking/run_tracker.py#L17-L69)).

### Checkpoint evidence

- **CODE FACT:** The exact model contract exists in official code: `JDTrack/ViT/JDTrack_online_target_fuse.pth.tar`, resolved beneath the user-configured `network_path` ([parameter](https://github.com/hexdjx/VisTrack/blob/f07acc942dfdc0bf78f437955a3ae1fc5e62b7fc/pytracking/parameter/jdtrack/jdtrack_vit.py#L51-L58), [path resolution](https://github.com/hexdjx/VisTrack/blob/f07acc942dfdc0bf78f437955a3ae1fc5e62b7fc/pytracking/utils/loading.py#L6-L31)). Evaluation disables separate backbone pretraining, so this final JDTrack archive is the method checkpoint required by the runner.
- **RESOURCE AVAILABILITY FACT:** The authors link Google Drive and Baidu `Models & Raw Results` resources ([README](https://github.com/hexdjx/VisTrack/blob/f07acc942dfdc0bf78f437955a3ae1fc5e62b7fc/README.md#L7-L10)). Direct listing of the official Google Drive [`models` folder](https://drive.google.com/drive/folders/1V-i0NN7q_H7J2lc0O1SnLas7WvLCjg3b) on 2026-08-24 found exactly 14 archives: `EnDiMP`, three `FuDiMP` variants, four `ProbDiMP` variants, `ProDiMP_prob`, `ProToMP_prob`, `ToMP_fu`, and three `Verify_Net` variants. It contained neither `JDTrack_online_target_fuse.pth.tar` nor a `JDTrack/ViT` folder. The official Baidu mirror could not be enumerated in this audit. This dated folder ID and inventory record the inspected mutable-resource snapshot; the link's existence does not establish actual availability of the checkpoint required by code.

### Evaluation evidence

- **CODE FACT:** The runner supplies dataset loading, tracker instantiation, result writing, and OTB/GOT-10k/PySOT-family evaluation infrastructure. A one-sequence validation path is directly available after configuring local dataset/model paths. Full-dataset CLI use needs overriding the shipped `Basketball` sequence and `debug=1` defaults ([CLI defaults](https://github.com/hexdjx/VisTrack/blob/f07acc942dfdc0bf78f437955a3ae1fc5e62b7fc/pytracking/run_tracker.py#L44-L65)).

### Blocking issue / residual risk

- **PENDING:** Source and evaluation integration are sufficient, but actual official availability of `JDTrack/ViT/JDTrack_online_target_fuse.pth.tar` remains unverified. The accessible author-linked Google bundle does not contain it, while the alternate Baidu bundle was not inspectable. Bundle ambiguity is therefore an HG3 blocker at present, not a favorable reproduction-risk assumption.

### Final HG3 rationale

The exact required checkpoint is known, but evidence that the official project actually supplies it is insufficient. Per the rule “missing information is `PENDING`, not favorable,” **HG3 PENDING.**

## CX051 — UMDATrack

Decision: **PENDING**

### Source-code evidence

- **CODE FACT:** The official source is pinned at `Z-Z188/UMDATrack@5d609bfcfb3a27161f9f4bd23bda518d6656909c` ([R46](../../references/references.md#r46)). Model/tracker code, four UMDATrack configurations, a dataset runner, adverse-weather dataset adapters, result writing, and offline analysis utilities are present.

### Checkpoint evidence

- **RESOURCE AVAILABILITY FACT:** The README links the same official Baidu/Google resource for the pretrained foundation model, pseudo-labels, and authors' training weights, and instructs users to place evaluation weights under `output/checkpoints/train/UMDATrack` ([pretraining placement](https://github.com/Z-Z188/UMDATrack/blob/5d609bfcfb3a27161f9f4bd23bda518d6656909c/README.md#L97-L108), [evaluation-weight placement](https://github.com/Z-Z188/UMDATrack/blob/5d609bfcfb3a27161f9f4bd23bda518d6656909c/README.md#L114-L120)).
- **RESOURCE AVAILABILITY FACT:** Direct listing of the author-linked [Google Drive folder](https://drive.google.com/drive/folders/1fondgxHRdglg9JZkg_UkfqqSUmhqLUA9) on 2026-08-24 exposed `pretrained_models/UMDATrack_pretrain.pth.tar`, two stage-1 files, three stage-2 files ([dark](https://drive.google.com/file/d/1UWuICiLiSTRcH98bbIR_0UaslxOlo8ra/view), [haze](https://drive.google.com/file/d/1z2B5DjvjQUD0O-5wNnERImEiRirtEIP7/view), and [rainy](https://drive.google.com/file/d/1p9bTbcKuQgiCQBw9xhnqj3b-Rc4biDg2/view)), and `pseudo_label.tar.gz`. These folder/file IDs record the inspected mutable-resource snapshot; file contents were not downloaded or executed. The listing distinguishes pretraining assets from domain-specific evaluation candidates.
- **CODE FACT:** The evaluation parameter code instead hard-codes `<save_dir>/checkpoints/train/UMDATrack/<config>/UMDATrack_extreme_prompt_dark_ep<epoch>.pth.tar` for every non-pseudo-label configuration, including haze and rainy ([checkpoint resolution](https://github.com/Z-Z188/UMDATrack/blob/5d609bfcfb3a27161f9f4bd23bda518d6656909c/lib/test/parameter/UMDATrack.py#L27-L34)). Neither README nor code maps the three released stage-2 names to this hard-coded basename/directory contract.

### Evaluation evidence

- **CODE FACT:** The README gives dark and haze commands with config and epoch selection ([commands](https://github.com/Z-Z188/UMDATrack/blob/5d609bfcfb3a27161f9f4bd23bda518d6656909c/README.md#L125-L135)); `--runid 0001` controls result identity, while `--ep 50` controls checkpoint selection in the official runner ([argument path](https://github.com/Z-Z188/UMDATrack/blob/5d609bfcfb3a27161f9f4bd23bda518d6656909c/tracking/test.py#L38-L68)).
- **CODE FACT:** The documented haze key `got10k_haze` is absent from the registry; the included key is `got10k_train_haze` ([dataset registry](https://github.com/Z-Z188/UMDATrack/blob/5d609bfcfb3a27161f9f4bd23bda518d6656909c/lib/test/evaluation/datasets.py#L40-L52)). The generated local environment omits adverse-dataset fields ([generated settings](https://github.com/Z-Z188/UMDATrack/blob/5d609bfcfb3a27161f9f4bd23bda518d6656909c/lib/test/evaluation/environment.py#L56-L85)) that included adapters access directly, such as `dtb70_path` ([dark adapter](https://github.com/Z-Z188/UMDATrack/blob/5d609bfcfb3a27161f9f4bd23bda518d6656909c/lib/test/evaluation/dtb70_darkdataset.py#L14-L22)). The documented dark/haze workflows therefore require undocumented local-file repair in addition to dataset paths.

### Blocking issue / residual risk

- **PENDING:** Actual official stage-2 weights exist, but official evidence does not unambiguously map them to the checkpoint names and locations loaded by code. The documented haze dataset key is invalid, and required adverse-dataset environment fields are not generated. A user can infer manual renames/path additions, but inference is not an official usable protocol.

### Final HG3 rationale

Source, domain weights, and evaluation components are present, but the official weight-to-config mapping and end-to-end evaluation commands are not sufficiently coherent to establish a realistic attempt without undocumented repair. Because the needed assets are present and the remaining mapping is unresolved rather than proved impossible, **HG3 PENDING.**

## CX064 — SiamABC

Decision: **FAIL**

### Source-code evidence

- **CODE FACT:** The official SiamABC source is pinned to the repository's `master` state at `wvuvl/SiamABC@b1c94e06fdf2dd3cb14ed07b05e38aa4601ece03`; the separate `main` state is unrelated AEVT material ([R51](../../references/references.md#r51)). Tracker source and a documented single-video runner are present ([demo command](https://github.com/wvuvl/SiamABC/blob/b1c94e06fdf2dd3cb14ed07b05e38aa4601ece03/README.md#L54-L64)).

### Checkpoint evidence

- **RESOURCE AVAILABILITY FACT:** Ten real model archives are committed in the pinned tree: five S-Tiny and five S-Small variants ([S-Tiny](https://github.com/wvuvl/SiamABC/tree/b1c94e06fdf2dd3cb14ed07b05e38aa4601ece03/assets/S_Tiny), [S-Small](https://github.com/wvuvl/SiamABC/tree/b1c94e06fdf2dd3cb14ed07b05e38aa4601ece03/assets/S_Small)). The README identifies these model populations for use by the demo ([model note](https://github.com/wvuvl/SiamABC/blob/b1c94e06fdf2dd3cb14ed07b05e38aa4601ece03/README.md#L62-L64)). Checkpoint availability itself is not the blocker.

### Evaluation evidence

- **CODE FACT:** `eval_SiamABC.py` imports `eval_data.*` and `eval_toolkit.pysot.*` ([imports](https://github.com/wvuvl/SiamABC/blob/b1c94e06fdf2dd3cb14ed07b05e38aa4601ece03/eval_SiamABC.py#L1-L9)). Both directories are absent from the pinned tree and explicitly ignored by `.gitignore` ([ignore rules](https://github.com/wvuvl/SiamABC/blob/b1c94e06fdf2dd3cb14ed07b05e38aa4601ece03/.gitignore#L1-L6)). There is no `.gitmodules` file or gitlink. The requirements do not name either missing module ([requirements](https://github.com/wvuvl/SiamABC/blob/b1c94e06fdf2dd3cb14ed07b05e38aa4601ece03/requirements.txt)); their sole Git dependency was additionally inspected at commit `936093173a89ac9b4bc63f2de8a182cae5a8825b`, whose package is `got10k`, not `eval_data` or `eval_toolkit` ([dependency setup](https://github.com/KupynOrest/toolkit/blob/936093173a89ac9b4bc63f2de8a182cae5a8825b/setup.py#L1-L13)). The dependency is unpinned in SiamABC, and the README gives no official restoration instructions for the absent trees.
- **CODE FACT:** `eval_SiamABC.py` contains benchmark helper functions but no CLI/main orchestration, tracker construction, checkpoint selection, or documented invocation. The single-video demo processes one manually initialized video and writes boxes/video; it does not enumerate benchmark sequences, load benchmark ground truth, compute benchmark metrics, or package standard submissions.

### Blocking issue / residual risk

- **INTERPRETATION:** The missing evaluator trees are not an ordinary local dataset-path edit. They are absent code dependencies with no official restoration path, and the demo is not a substitute for benchmark evaluation. Thus official evaluation support is insufficient for a realistic baseline-reproduction attempt.

### Final HG3 rationale

Official source and actual tracker checkpoints exist, but the required official benchmark evaluation integration is incomplete and unusable from a clean checkout. **HG3 FAIL.**

## Independent-result summary

SAMURAI: **PASS**

DAM4SAM: **PASS**

MambaLCT: **FAIL**

JDTrack: **PENDING**

UMDATrack: **PENDING**

SiamABC: **FAIL**

PASS count: **2**

FAIL count: **2**

PENDING count: **2**

If this independent result is applied to the 20-family pre-flag scientific-audit queue:

**ACTIVE SCIENTIFIC-AUDIT QUEUE SIZE = 16**

Arithmetic: 14 non-flagged families + 2 independent HG3 `PASS` families. The two `FAIL` and two unresolved `PENDING` families are not counted as active for later hard-gate progression. This is a scientific-audit queue count, **not a shortlist**.

## BLINDNESS DECLARATION

Before this report was completed, the independent verification lane:

- did **not** read `screening/manager/2026-08-24_hg3_flag_reconciliation.md`;
- did **not** read `screening/reconciliation/2026-08-24_hg3_canonicalization_checkpoint.md`;
- did **not** read `screening/candidate_screening_matrix.csv`;
- did **not** read `screening/codex/2026-08-24_hg3_flag_independent_recheck.md`;
- did **not** grep/search those files or use Git diff/history to inspect their conclusions.

The required initial Git synchronization displayed repository change metadata, including filenames, but no content or conclusion from any forbidden artifact was opened or inspected. The decisions above were derived from the allowed protocol/source-registration files and direct inspection of the official pinned repositories and author-linked resources.

**BLINDNESS STATUS: PRESERVED**

## Scope guards

- CANONICAL MATRIX: **NOT MODIFIED**
- HG4-HG5-HG6: **NOT STARTED**
- SOFT SCORING: **NOT STARTED**
- PRIMARY SHORTLIST: **NONE**
- MAIN BASELINE: **NONE**
- PROPOSED ARCHITECTURE: **NONE**
