# FARTrack deep audit — working research dossier

**Status:** active baseline audit; not a novelty claim and not a benchmark result.

**Primary sources:** official ICLR/OpenReview paper [R11](../references/references.md#r11) and official source repository [R12](../references/references.md#r12).

## 1. Paper identity and purpose

FARTrack: *Fast Autoregressive Visual Tracking with High Performance* was published at ICLR 2026. The paper targets the efficiency–accuracy trade-off in autoregressive visual tracking. Its central design combines:

- autoregressive trajectory prediction;
- multi-template appearance modeling;
- Task-Specific Self-Distillation (TSSD);
- Inter-frame Autoregressive Sparsification (IFAS).

The paper is not framed as a person-ReID or explicit long-term target-absence/re-acquisition method.

## 2. Core autoregressive formulation

The tracker represents the target trajectory as quantized coordinate tokens corresponding to the bounding box coordinates. Visual tokens from templates/search and trajectory/command tokens are processed jointly by a Transformer. Four command tokens correspond to the four coordinates to be predicted.

Practical interpretation for this project:

> FARTrack models both **what the target looks like** and **where its trajectory has been going**.

This temporal continuity is useful for tracking, but continuity alone is not equivalent to same-person identity verification.

## 3. Multi-template appearance memory

The published configuration uses five templates. The paper studies template count and shows that more templates are not monotonically better: five provides a strong balance, while larger template sets can disperse attention and increase cost.

A key distinction for the present project is:

- **redundant memory:** many similar but correct templates;
- **corrupted memory:** templates representing the wrong object/person.

IFAS directly addresses redundancy/computation. Whether it prevents corrupted identity memory is a separate question to test.

## 4. Task-Specific Self-Distillation (TSSD)

FARTrack avoids manually mapping distant teacher/student layers. Deeper adjacent layers progressively supervise shallower layers, and the distillation target is task-specific trajectory information rather than a blanket copy of the full visual hierarchy.

Published model variants:

| Variant | Encoder layers | Parameters | MACs |
|---|---:|---:|---:|
| FARTrack-Tiny | 15 | 6.82M | 2.65G |
| FARTrack-Nano | 10 | 4.59M | 1.78G |
| FARTrack-Pico | 6 | 2.81M | 1.08G |

The distillation mechanism is therefore relevant both as a paper contribution and as a possible later route for transferring any new robustness mechanism from a stronger model toward an edge model.

## 5. Inter-frame Autoregressive Sparsification (IFAS)

IFAS estimates template-token importance using attention relationships and removes lower-importance template tokens. The sparsification state can be propagated between frames, reducing the need to perform a separate heavy pruning decision at every frame.

The paper reports an effective operating point around retaining 75% of template tokens for FARTrack-Tiny: moderate pruning can reduce computation while maintaining or slightly improving reported accuracy, whereas aggressive pruning reduces accuracy substantially.

### Research hypothesis: localization importance vs identity importance

**HYPOTHESIS TO TEST.** A token that contributes little to bounding-box localization may still encode a discriminative identity cue (e.g., a small clothing logo, local texture, accessory, or body-region pattern). Therefore the IFAS importance criterion may not be optimal for identity-preserving target-person tracking in crowds.

This is not an author claim. It requires direct experiments with token masks and same-person/distractor episodes.

## 6. Published losses and what they do not establish

The paper optimizes coordinate/trajectory tracking using classification/regression-style objectives and KL-based distillation. The published method does not introduce a dedicated person identity objective or an explicit target-presence probability head.

Therefore the paper by itself does not establish that a high tracking score or temporally consistent prediction means that the candidate is the originally designated person.

## 7. Hardware and efficiency facts

The paper reports training with **8× NVIDIA RTX A6000** GPUs.

Reported inference speed is measured on:

- NVIDIA Titan Xp GPU;
- Intel Xeon Gold 6230R CPU;
- Ascend 310B NPU.

Reported speeds:

| Variant | Titan Xp GPU | Xeon CPU | Ascend NPU |
|---|---:|---:|---:|
| Tiny | 135 FPS | 53 FPS | 42 FPS |
| Nano | 210 FPS | 77 FPS | 61 FPS |
| Pico | 343 FPS | 121 FPS | 101 FPS |

**Boundary:** none of these values is a Jetson Nano benchmark. Jetson Nano feasibility must be profiled directly.

## 8. Published benchmark snapshot

The paper reports the following representative values:

| Variant | GOT-10k AO | TrackingNet AUC | LaSOT AUC |
|---|---:|---:|---:|
| Pico | 62.8 | 75.6 | 58.6 |
| Nano | 69.9 | 79.1 | 61.3 |
| Tiny | 70.6 | 80.7 | 63.2 |

These numbers are generic SOT results. They must not be presented as evidence of correct target-person identity recovery.

## 9. Training pipeline

The paper uses multiple training stages, including frame-level pretraining, task-specific self-distillation, and sequence-level sparsification training. The sequence-level stage uses finite video slices rather than arbitrarily long disappearance episodes.

For this project, reproduction from scratch on a single RTX 3060 is not assumed. The preferred path is:

1. official checkpoints;
2. baseline inference reproduction;
3. focused fine-tuning / module training;
4. mixed precision, smaller batches, and gradient accumulation as required;
5. only later attempt broader retraining if evidence demands it.

## 10. Author-reported limitation most relevant to this project

**AUTHOR-REPORTED LIMITATION.** In the paper appendix/supplementary discussion, prolonged tracking failure caused by target disappearance or occlusion can make the maintained templates invalid and degrade tracking performance [R11].

This is the strongest source-grounded entry point for the present problem because it connects directly to:

- long target disappearance;
- corrupted or invalid appearance history;
- temporal propagation after failure;
- the need for safe recovery.

## 11. Failure mechanism to test

The following is a project hypothesis, not yet a result:

```text
correct target A
    ↓
long occlusion / disappearance
    ↓
uncertain or wrong prediction
    ↓
wrong spatial state
    +
wrong trajectory history
    +
wrong appearance template
    ↓
autoregressive self-confirmation
    ↓
wrong-person lock / failed recovery
```

We call this tentative mechanism **autoregressive contamination** until experiments either confirm or reject it.

## 12. Why ordinary ReID attachment is insufficient

A person-ReID embedding can answer whether two person crops are similar, but a strong research contribution must determine **when and how identity evidence controls the tracker**.

The relevant control points are:

- advance/freeze spatial state;
- accept/reject a new template;
- update/freeze trajectory history;
- switch TRACKING → UNCERTAIN → LOST;
- decide when to expand the internal search area;
- accept/reject a re-entry candidate;
- re-lock only after sufficient same-person evidence.

Therefore the working direction is **identity- and presence-aware autoregressive tracking**, not “FARTrack + ReID”.

## 13. Required failure-audit experiment before proposing the final architecture

Instrument FARTrack-Tiny/Nano first, with Nano as the preferred development balance point.

Record per frame where possible:

- predicted bbox;
- predicted coordinate-token confidence if exposed;
- spatial/search center;
- templates inserted, retained, and selected;
- trajectory tokens/history;
- IFAS masks/token retention;
- target visibility/absence from ground truth;
- whether the prediction belongs to the correct target identity.

Create episode categories:

- partial occlusion;
- full occlusion;
- target leaves view;
- near re-entry;
- far re-entry;
- similar-person crossing;
- prolonged distractor lock.

Diagnostic metrics should include:

- wrong-person lock rate;
- false-present rate during absence;
- recovery success rate;
- recovery latency;
- identity precision at re-lock;
- template contamination rate;
- spatial drift distance during absence.

Official TPT-Bench long-term metrics remain primary for domain evaluation; generic SOT benchmarks are regression checks.

## 14. Current baseline role decision

**PROJECT DECISION — provisional.**

- **FARTrack-Nano:** main development candidate.
- **FARTrack-Tiny:** accuracy reference / possible teacher.
- **FARTrack-Pico:** later deployment candidate for very constrained hardware.

This role assignment can change after actual reproduction and profiling.

## 15. Open questions

1. Does a wrong prediction get inserted into the released inference template memory without a sufficiently strong reliability/identity gate?
2. How quickly does a single wrong template propagate into subsequent autoregressive predictions?
3. Can trajectory continuity remain high while target identity is wrong?
4. Does IFAS prune cues that are weak for localization but useful for identity discrimination?
5. How far can the current local search recover after out-of-view re-entry?
6. What minimal presence/identity mechanism improves TPT-Bench without materially degrading generic SOT accuracy?
7. Can the resulting method be distilled to Nano/Pico-class compute and remain feasible on a Jetson-class device?

## 16. Evidence discipline

Every future FARTrack statement should be tagged mentally or explicitly as one of:

- **SOURCE FACT** — paper or official repository;
- **CODE FACT** — directly observed in released source;
- **AUTHOR-REPORTED LIMITATION**;
- **INTERPRETATION**;
- **HYPOTHESIS TO TEST**;
- **POSSIBLE RESEARCH OPPORTUNITY**;
- **PROJECT DECISION**.

Do not promote a hypothesis into a paper claim until an experiment supports it.
