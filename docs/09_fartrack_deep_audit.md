# FARTrack deep audit — reference case study

**Status:** retained reference/case study after the 2026-08-24 baseline reset; **not the assumed main development backbone**.  
**Primary sources:** official ICLR/OpenReview paper [R11](../references/references.md#r11) and official source repository [R12](../references/references.md#r12).

This document preserves the technical audit already completed for FARTrack. Reopening baseline selection does not invalidate these facts or hypotheses; it only changes FARTrack's role in the research program.

## 1. Paper identity and purpose

FARTrack: *Fast Autoregressive Visual Tracking with High Performance* was published at ICLR 2026. The paper targets the efficiency–accuracy trade-off in autoregressive visual tracking. Its central design combines:

- autoregressive trajectory prediction;
- multi-template appearance modeling;
- Task-Specific Self-Distillation (TSSD);
- Inter-frame Autoregressive Sparsification (IFAS).

The paper is not framed as a person-ReID or explicit long-term target-absence/re-acquisition method.

## 2. Core autoregressive formulation

The tracker represents target trajectory as quantized coordinate tokens corresponding to bounding-box coordinates. Visual template/search tokens and trajectory/command tokens are processed jointly by a Transformer. Four command tokens correspond to the four coordinates to be predicted.

Practical interpretation:

> FARTrack models both **what the target looks like** and **where its trajectory has been going**.

Temporal continuity is useful for tracking, but continuity alone is not equivalent to same-person identity verification.

## 3. Multi-template appearance memory

The published configuration uses five templates. The paper shows that increasing template count is not monotonically beneficial: five provides a strong balance, while larger sets can disperse attention and increase cost.

Important distinction:

- **redundant memory:** many similar but correct templates;
- **corrupted memory:** templates representing the wrong object/person.

IFAS directly addresses redundancy/computation. Whether it prevents corrupted identity memory is a separate question.

## 4. Task-Specific Self-Distillation (TSSD)

FARTrack uses task-specific, progressive deep-to-shallow distillation rather than a conventional fixed teacher/student layer mapping.

Published variants:

| Variant | Encoder layers | Parameters | MACs |
|---|---:|---:|---:|
| FARTrack-Tiny | 15 | 6.82M | 2.65G |
| FARTrack-Nano | 10 | 4.59M | 1.78G |
| FARTrack-Pico | 6 | 2.81M | 1.08G |

These variants make FARTrack a valuable reference for how a modern tracker can be designed with an explicit lightweight path.

## 5. Inter-frame Autoregressive Sparsification (IFAS)

IFAS estimates template-token importance using attention relationships and removes lower-importance template tokens. The sparsification state can be propagated between frames.

The paper reports an effective operating point around retaining 75% of template tokens for FARTrack-Tiny: moderate pruning reduces compute while maintaining or slightly improving reported accuracy; aggressive pruning degrades accuracy.

### Retained research hypothesis

**HYPOTHESIS — untested.** A token that contributes little to bounding-box localization may still encode a discriminative identity cue. Therefore IFAS token importance may not be optimal for identity-preserving target-person tracking.

This remains a possible Layer-B research question, not an author claim and not the current Core hypothesis.

## 6. Published losses and scope boundary

The published method optimizes coordinate/trajectory tracking and distillation. It does not introduce a dedicated person-identity objective or explicit target-presence probability head.

Therefore the paper by itself does not establish that a high tracking score or temporally consistent prediction corresponds to the originally designated person.

## 7. Hardware and efficiency facts

The paper reports training with **8× NVIDIA RTX A6000** GPUs.

Reported inference hardware:

- NVIDIA Titan Xp GPU;
- Intel Xeon Gold 6230R CPU;
- Ascend 310B NPU.

Reported speeds:

| Variant | Titan Xp GPU | Xeon CPU | Ascend NPU |
|---|---:|---:|---:|
| Tiny | 135 FPS | 53 FPS | 42 FPS |
| Nano | 210 FPS | 77 FPS | 61 FPS |
| Pico | 343 FPS | 121 FPS | 101 FPS |

**Boundary:** none of these is a Jetson Nano benchmark. No Jetson FPS may be inferred from them.

## 8. Published benchmark snapshot

| Variant | GOT-10k AO | TrackingNet AUC | LaSOT AUC |
|---|---:|---:|---:|
| Pico | 62.8 | 75.6 | 58.6 |
| Nano | 69.9 | 79.1 | 61.3 |
| Tiny | 70.6 | 80.7 | 63.2 |

These are generic SOT results and are not evidence of identity-safe recovery.

## 9. Training pipeline

The paper uses multiple stages including frame-level pretraining, task-specific self-distillation, and sequence-level sparsification training.

For this project, full reproduction of the original 8×A6000 training recipe on a single RTX 3060 is not assumed. FARTrack nevertheless remains useful as a reference for checkpoint-based reproduction, focused fine-tuning, distillation design, and edge-oriented model variants.

## 10. Author-reported limitation

**AUTHOR-REPORTED LIMITATION — cited.** The paper appendix/supplementary discussion states that prolonged tracking failure caused by target disappearance or occlusion can make maintained templates invalid and degrade tracking performance [R11].

This remains important evidence for long-term failure analysis, but it no longer by itself justifies FARTrack as the Core baseline.

## 11. Retained failure hypothesis

The following remains a project hypothesis, not a result:

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

**HYPOTHESIS — untested.** This tentative **autoregressive contamination** mechanism may still be tested later as a reference study or Layer-B mechanism question.

## 12. Why ordinary ReID attachment is insufficient

A person-ReID embedding can estimate whether two person crops look similar, but a strong method must decide when identity evidence controls state, memory, search, and recovery.

Relevant control points include:

- advance/freeze spatial state;
- accept/reject template update;
- update/freeze trajectory history;
- switch TRACKING → UNCERTAIN → LOST;
- expand search;
- accept/reject re-entry candidate;
- re-lock only after sufficient evidence.

This remains relevant to the later target-person extension, but **it is no longer the primary Core baseline-selection problem**.

## 13. Why FARTrack is now a reference rather than the default baseline

**PROJECT DECISION — locked scope, 2026-08-24.** FARTrack is no longer the assumed main development tracker.

Reasoning:

1. FARTrack already solves much of the lightweight/efficiency problem unusually well through TSSD, IFAS, and Tiny/Nano/Pico variants.
2. The strongest remaining gaps identified in this audit are concentrated around disappearance, identity, and recovery.
3. Those gaps are valuable but risk making the Core contribution depend too heavily on the later person/long-term extension.
4. The revised program instead searches for a 2025–2026 generic RGB SOT tracker with **researchable computational redundancy + a meaningful robustness weakness**, preferably addressable by one new mechanism.

FARTrack remains a high-value reference for:

- lightweight tracker design;
- autoregressive modeling;
- self-distillation;
- token sparsification;
- failure-audit methodology;
- future benchmarking/ablation comparisons;
- novelty auditing.

## 14. Current project role

- **FARTrack-Tiny:** high-capacity reference for the FARTrack family.
- **FARTrack-Nano:** balanced reference implementation.
- **FARTrack-Pico:** important edge-oriented reference because of its very small parameter/MAC footprint.

None is currently designated as the main baseline for the revised Core research program.

## 15. Open FARTrack-specific questions retained for later

1. Does a wrong prediction enter template memory without a sufficiently strong reliability/identity gate?
2. How quickly can a wrong template propagate into subsequent autoregressive predictions?
3. Can trajectory continuity remain high while target identity is wrong?
4. Does IFAS prune cues weak for localization but strong for identity discrimination?
5. How far can local search recover after out-of-view re-entry?
6. Can identity/presence control improve target-person behavior without materially degrading generic SOT?

These questions are deferred until they become relevant to Layer B or comparative analysis.

## 16. Evidence discipline

Use the repository taxonomy in `docs/00_claim_taxonomy.md`:

- **FACT — cited** for paper/official-source facts;
- **CODE FACT — inspected** for behavior directly observed in a specific code version/path;
- **AUTHOR-REPORTED LIMITATION — cited** for limitations explicitly stated by the authors;
- **INTERPRETATION — reasoned** for project reasoning from evidence;
- **HYPOTHESIS — untested** for falsifiable mechanisms not yet demonstrated;
- **PROJECT DECISION** for local scope/role choices;
- **OPEN QUESTION** where evidence is not yet sufficient.

Do not promote a retained FARTrack hypothesis into a result without experiment evidence.
