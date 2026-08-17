# Tracker-selection boundary

## Current provisional selection

**PROJECT DECISION — provisional, 2026-08-17.** The current development backbone is **FARTrack** (ICLR 2026), with the official implementation from `MIV-XJTU/FARTrack` and the official OpenReview paper recorded as primary sources [R11](../references/references.md#r11), [R12](../references/references.md#r12).

This is a **working baseline selection**, not a claim that FARTrack is optimal, SOTA, identity-safe, long-term complete, or deployable on Jetson Nano. The selection is reversible if failure auditing or reproduction shows that the baseline is unsuitable.

The immediate working configuration is:

- **FARTrack-Nano** as the preferred research/development balance point;
- **FARTrack-Tiny** as the higher-capacity accuracy reference / possible teacher;
- **FARTrack-Pico** as the aggressive edge-deployment candidate to profile later.

The project is still problem-first: the selected problem remains identity-preserving, presence-aware target-person tracking under disappearance, re-entry, and similar-person distractors. FARTrack is the current vehicle for testing that problem, not the definition of the problem itself.

## Why FARTrack entered the main path

**SOURCE FACT.** FARTrack is a fast autoregressive visual tracker whose published method combines task-specific self-distillation, inter-frame autoregressive sparsification, multi-template appearance modeling, and autoregressive trajectory prediction [R11].

**SOURCE FACT.** The official repository releases code/checkpoints for Tiny, Nano, and Pico variants [R12].

**SOURCE FACT.** The paper reports 6.82M / 4.59M / 2.81M parameters and 2.65G / 1.78G / 1.08G MACs for Tiny / Nano / Pico respectively. Reported inference speed was measured on Titan Xp, Xeon Gold 6230R, and Ascend 310B; training used 8× RTX A6000 [R11]. These numbers must not be converted into Jetson Nano FPS without measurement.

**AUTHOR-REPORTED LIMITATION.** The supplementary/appendix discussion states that prolonged tracking failure, such as target disappearance or occlusion, can make templates invalid and degrade tracking performance [R11]. This directly motivates a failure audit around memory corruption and recovery.

## Current research opportunity — not yet an established result

**INTERPRETATION.** FARTrack is optimized primarily for efficient visual-temporal continuity, not explicit person identity preservation. Its published objective does not introduce a dedicated person-ReID loss or explicit target-presence state.

**HYPOTHESIS TO TEST.** During prolonged disappearance or a similar-person switch, one incorrect prediction may contaminate several coupled states: spatial search state, trajectory history, and appearance-template history. If confirmed, this would be an autoregressive contamination loop rather than an isolated localization error.

**HYPOTHESIS TO TEST.** Token importance for localization/sparsification may differ from token importance for identity discrimination. A small clothing/body cue could be weak for bbox localization but critical for distinguishing the designated person from a distractor.

**POSSIBLE RESEARCH OPPORTUNITY.** Study an identity- and presence-aware temporal policy that controls whether FARTrack may advance spatial state, update templates/trajectory, declare loss, expand search, and re-lock. A lightweight ReID representation may be one component, but “attach ReID to FARTrack” is not sufficient as the research contribution.

## Minimum gates before architecture changes

1. Reproduce official FARTrack inference with published checkpoints.
2. Validate Tiny/Nano/Pico on at least one standard SOT benchmark or official demo path.
3. Instrument template insertion/selection, trajectory state, search-center state, and sparsification masks.
4. Run failure episodes covering partial occlusion, full disappearance, out-of-view, near/far re-entry, and similar-person crossings.
5. Separate localization failure, absence failure, identity failure, and recovery failure.
6. Measure wrong-person lock rate, false-present rate, recovery success/latency, identity precision at relock, template contamination, and drift during absence where annotations permit.
7. Evaluate the final target-person extension primarily on TPT-Bench while keeping generic SOT benchmarks as secondary regression checks.
8. Profile Jetson Nano directly; do not infer embedded performance from Titan Xp/CPU/NPU/FLOPs.

## Non-claims to preserve

- Do not call FARTrack or the proposed extension “SOTA” without a date, benchmark, split, protocol, and primary source.
- Do not infer Jetson Nano feasibility from Orin, AGX, TX2, desktop GPU, phone, NPU, or paper FLOPs/MACs.
- Do not describe a detector as an identity verifier. The current policy allows a person detector for initialization only; external detection during normal tracking/recovery would change the declared protocol.
- Do not claim identity preservation, target absence handling, or safe re-acquisition until measured.
