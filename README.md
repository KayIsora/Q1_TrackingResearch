# Embodied Tracking Problem Research

> An evidence-first research dossier for choosing a real problem before choosing a tracker.

**Language:** Vietnamese with English technical terms.
**Status:** research framing; no tracker, model, benchmark result, or embedded deployment claim has been selected or demonstrated.

## What this repository is for

This repository records the current reasoning for an embodied visual-tracking research direction so that a person or an AI can clone it and distinguish:

- what a primary source actually establishes;
- what is an interpretation of that evidence;
- what is merely a project decision, hypothesis, provisional target, or open question.

It is deliberately **problem-first**. A popular tracker is not an application, and a benchmark score is not proof that a robot solves a real-world problem.

## Current project recommendation — not a research result

**[PROJECT DECISION — provisional]** The best present framing for the available scope is:

> **Identity-preserving visual continuity for a consenting user that a robot guides or accompanies in a crowded public facility.**

The proposed perception output is a target bounding box, target-presence/confidence state, and recovery of the same instance after disappearance. It is not the former “robot following an elderly person” application, surveillance, a safety-certified system, or autonomous robot control.

Why this is the current recommendation:

- TPT-Bench directly studies robot-egocentric target-person tracking in crowded, unstructured indoor/outdoor scenes with occlusion and re-identification pressure [R1](references/references.md#r1), [R2](references/references.md#r2).
- Embodied visual tracking is an active research direction, but work such as TrackVLA joins perception and trajectory planning; that is a **scope boundary**, not a Nano baseline [R5](references/references.md#r5).
- The recommendation matches the fixed constraints: robot-mounted moving RGB camera, box-SOT, identity preservation, long occlusion/out-of-view re-entry, and later embedded evaluation.

This does **not** establish that it is the most urgent social problem, that it improves safety, or that it will be deployable on Jetson Nano. Those are separate questions requiring their own evidence and measurements.

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
10. [References](references/references.md), the [evidence ledger](references/evidence_ledger.md), and the machine-readable [source manifest](references/source_manifest.csv)

## Fixed scope at this stage

| Item | Current status |
|---|---|
| Core task | **[PROJECT DECISION]** RGB, class-agnostic, box single-object tracking (SOT) from a robot-mounted moving camera. |
| Default robot-demo target | **[PROJECT DECISION]** A person detector may provide an initial box. The core tracker remains class-agnostic and can later be initialized on another egocentric object. |
| Required output | **[PROJECT DECISION]** Bounding box + presence/confidence + same-instance re-detection. |
| Headline failures | **[PROJECT DECISION]** Long occlusion, out-of-view re-entry, and visually similar-person distractors. Blur/camera shake are deployment stresses. |
| Training | **[PROJECT DECISION]** Offline server with RTX 3060; its precise VRAM/software profile remains open. |
| Edge target | **[PROJECT DECISION]** Jetson Nano. Feasibility has not been measured. |
| Robot control | **[OUT OF SCOPE FOR NOW]** Active control is only a later demonstration after tracking and benchmark work. |
| Sensors | **[PROJECT DECISION]** RGB now. LiDAR is a future possibility, not current model input. |

## What is intentionally absent

- No claim of SOTA, novelty, Nano FPS, accuracy, power use, social impact, or safety certification.
- No copied benchmark data, checkpoints, videos, or the user-supplied Consensus PDF.
- No claim that one tracker family is already selected.
- No automatic conversion from moving-camera SOT into MOT, VOS, RGB-D tracking, or closed-loop navigation.

## Reuse and contributions

Read [CONTRIBUTING.md](CONTRIBUTING.md) before changing a claim or adding a source. The clone contains a rule snapshot; the working source of truth in the original workspace is `E:\Robot_Backup\RULE`.
