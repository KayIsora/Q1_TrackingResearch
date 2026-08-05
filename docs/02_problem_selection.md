# Problem-selection evidence

## What the primary sources establish

1. **FACT — cited.** TPT-Bench presents target-person tracking from robot-egocentric views as relevant to continuous personalized assistance/collaboration in HRI and Embodied AI. Its 48 indoor/outdoor sequences were collected in crowded, unstructured settings with frequent occlusion and many pedestrians that make re-identification necessary [R1](../references/references.md#r1).
2. **FACT — cited.** The accompanying public record describes 5.3 hours of multimodal recordings and 571,982 frame-level 2D target-person boxes; it also says the dataset record is copyrighted, so this repository links to it rather than redistributing it [R2](../references/references.md#r2).
3. **FACT — cited.** TrackVLA frames embodied visual tracking as recognition plus trajectory planning under severe occlusion and scene dynamics [R5](../references/references.md#r5). Its computation setup is not evidence for a lightweight embedded system.
4. **FACT — cited.** VISTA and EgoTracks demonstrate that there are modern public research resources for egocentric/object long-term tracking questions, while their stated domains remain distinct from robot-egocentric target-person tracking [R3](../references/references.md#r3), [R4](../references/references.md#r4).

## Reasoned interpretation

**INTERPRETATION — reasoned.** The most defensible immediate research problem is not generic “track a human,” and not merely “make a robot follow.” It is:

> preserving the identity of an already-consenting target person despite occlusion, leaving the field of view, and similar-looking distractors while the observing camera itself moves.

This is narrow enough for RGB box-SOT, directly testable with a robot-person benchmark, and still relevant to an eventual guide/accompany demonstration. It keeps the problem real without claiming that vision alone solves navigation, safety, consent, or social acceptance.

## What evidence does **not** establish

- TPT-Bench uses a human pushing a sensor-equipped cart; it is not proof of a fully autonomous mobile robot [R1](../references/references.md#r1).
- A current research benchmark does not prove that the proposed application is society’s most urgent problem.
- An embodied VLA paper does not establish feasibility on Jetson Nano [R5](../references/references.md#r5).
