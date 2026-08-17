# Embodied Tracking Problem Research

> An evidence-first research dossier for choosing a real problem before choosing and improving a tracker.

**Language:** Vietnamese with English technical terms.  
**Status:** problem framing is established; **FARTrack is the current provisional development backbone**. No proposed improvement, benchmark gain, identity-preservation result, or embedded deployment claim has yet been demonstrated.

## What this repository is for

This repository records the current reasoning for an embodied visual-tracking research direction so that a person or an AI can clone it and distinguish:

- what a primary source actually establishes;
- what released code directly shows;
- what is an interpretation of that evidence;
- what is merely a project decision, hypothesis, provisional target, or open question.

It remains deliberately **problem-first**. FARTrack is now selected provisionally because it is a strong vehicle for testing the chosen failure mode; it does not define the research problem and can be replaced if reproduction/failure auditing rejects it.

## Current project recommendation — not a research result

**[PROJECT DECISION — provisional]** The best present framing for the available scope is:

> **Identity-preserving visual continuity for a consenting user that a robot guides or accompanies in a crowded public facility.**

The proposed perception output is a target bounding box, target-presence/confidence state, and recovery of the same instance after disappearance. It is not the former “robot following an elderly person” application, surveillance, a safety-certified system, or autonomous robot control.

Why this is the current recommendation:

- TPT-Bench directly studies robot-egocentric target-person tracking in crowded, unstructured indoor/outdoor scenes with occlusion and re-identification pressure [R1](references/references.md#r1), [R2](references/references.md#r2).
- Embodied visual tracking is an active research direction, but work such as TrackVLA joins perception and trajectory planning; that is a **scope boundary**, not a Nano baseline [R5](references/references.md#r5).
- The recommendation matches the fixed constraints: robot-mounted moving RGB camera, box-SOT, identity preservation, long occlusion/out-of-view re-entry, and later embedded evaluation.

This does **not** establish that it is the most urgent social problem, that it improves safety, or that it will be deployable on Jetson Nano. Those are separate questions requiring their own evidence and measurements.

## Current provisional tracker baseline

**[PROJECT DECISION — 2026-08-17]** The current development family is **FARTrack (ICLR 2026)** [R11](references/references.md#r11), using the official released implementation [R12](references/references.md#r12).

Working roles:

- **FARTrack-Nano** — main development candidate;
- **FARTrack-Tiny** — higher-capacity accuracy reference / possible teacher;
- **FARTrack-Pico** — later aggressive edge-deployment candidate.

The immediate scientific focus is not “make FARTrack faster.” FARTrack already targets efficiency through self-distillation and inter-frame sparsification. The present audit focuses on whether prolonged disappearance and similar-person interference can corrupt autoregressive temporal/appearance state, and whether identity/presence evidence can control memory update and safe re-acquisition.

See [FARTrack deep audit](docs/09_fartrack_deep_audit.md).

## Start here (mandatory reading order)

1. [RULE/01_EVIDENCE_AND_CITATION_POLICY.md](RULE/01_EVIDENCE_AND_CITATION_POLICY.md)
2. [Claim taxonomy](docs/00_claim_taxonomy.md)
3. [Scope and terminology](docs/01_scope_and_terminology.md)
4. [Problem-selection evidence](docs/02_problem_selection.md)
5. [Application candidates and decision](docs/03_application_candidates.md)
6. [Dataset and evaluation roles](docs/04_evaluation_stack.md)
7. [Edge-deployment claim boundary](docs/05_edge_boundary.md)
8. [Open research questions and gates](docs/06_research_questions.md)
9. [Tracker-selection boundary](docs/07_tracker_selection_boundary.md)
10. [Consensus input boundary](docs/08_consensus_input.md)
11. [FARTrack deep audit](docs/09_fartrack_deep_audit.md)
12. [References](references/references.md), the [evidence ledger](references/evidence_ledger.md), and the machine-readable [source manifest](references/source_manifest.csv)

## Fixed scope at this stage

| Item | Current status |
|---|---|
| Core task | **[PROJECT DECISION]** RGB, class-agnostic, box single-object tracking (SOT) from a robot-mounted moving camera. |
| Default robot-demo target | **[PROJECT DECISION]** A person detector may provide an initial box. The core tracker remains class-agnostic and can later be initialized on another egocentric object. |
| Required output | **[PROJECT DECISION]** Bounding box + presence/confidence + same-instance re-detection. |
| Headline failures | **[PROJECT DECISION]** Long occlusion, out-of-view re-entry, and visually similar-person distractors. Blur/camera shake are deployment stresses. |
| Current tracker family | **[PROJECT DECISION — provisional]** FARTrack; Nano is the primary development candidate, Tiny/Pico are reference variants. |
| Training | **[PROJECT DECISION]** Offline development on RTX 3060-class hardware; full reproduction of the paper's 8×A6000 recipe is not assumed. Official checkpoints + focused fine-tuning are the preferred first path. |
| Edge target | **[PROJECT DECISION]** Jetson Nano remains a hard deployment target; feasibility has not been measured. A stronger Jetson-class board may be used if the original Nano cannot meet a defensible runtime target. |
| Robot control | **[OUT OF SCOPE FOR NOW]** Active control is only a later demonstration after tracking and benchmark work. |
| Sensors | **[PROJECT DECISION]** RGB now. LiDAR is a future possibility, not current model input. |

## Immediate research gates

Before proposing a final architecture:

1. reproduce FARTrack inference from official checkpoints;
2. instrument template/trajectory/search-state updates and IFAS masks;
3. audit failures under long disappearance, out-of-view, and similar-person crossings;
4. test whether wrong predictions cause appearance + trajectory + spatial-state contamination;
5. evaluate target-person behavior primarily on TPT-Bench and preserve generic SOT regression checks;
6. only then design identity-/presence-aware update, loss, and recovery logic;
7. profile Jetson hardware directly rather than inferring FPS from Titan Xp, CPU, NPU, MACs, or parameter count.

## What is intentionally absent

- No claim of SOTA, novelty, Nano FPS, accuracy gain, power use, social impact, or safety certification.
- No copied benchmark datasets, checkpoints, videos, or the user-supplied Consensus PDF.
- No claim that FARTrack already solves identity preservation, target absence, or safe re-acquisition.
- No automatic conversion from moving-camera SOT into MOT, VOS, RGB-D tracking, or closed-loop navigation.

## Working division of labor

The intended workflow is:

- **ChatGPT:** research manager / evidence controller — verify claims, maintain research framing, novelty boundaries, experiment gates, and repository state;
- **Codex:** implementation executor — translate/read local papers, modify code, run scripts/experiments, and produce artifacts under explicit instructions;
- **GitHub:** shared state — decisions, evidence, experiment plans, implementation notes, and reproducible results should be committed so both workflows stay synchronized.

Implementation output from Codex must not be promoted to a scientific claim until it is checked against source code, logs, and evaluation results.

## Reuse and contributions

Read [CONTRIBUTING.md](CONTRIBUTING.md) before changing a claim or adding a source. The clone contains a rule snapshot; the working source of truth in the original workspace is `E:\Robot_Backup\RULE`.
