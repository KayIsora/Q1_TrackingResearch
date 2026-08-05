# Scope and terminology

## Task contract

**[PROJECT DECISION — provisional]** The core problem is **moving-camera RGB box-SOT**:

```text
initial target bounding box
        ↓
robot-mounted moving RGB camera
        ↓
tracker output per frame: box + presence/confidence
        ↓
same-instance recovery after target disappearance
```

The default robot-demo target is a person, initialized by a detector only after the tracking model is ready. The core tracker is still class-agnostic: it should be usable for a person or an object manipulated in egocentric activity.

## Terms that must not be conflated

| Term | Meaning in this dossier | Not automatically included |
|---|---|---|
| SOT | One initialized target is propagated over time. | Multi-person identity assignment, segmentation masks, or navigation. |
| Long-term SOT | A SOT setting in which target disappearance and re-detection matter. VOT-LT explicitly requires presence confidence and re-detection after disappearance [R6](../references/references.md#r6). | A detector-assisted or ReID system unless that assistance is separately declared. |
| Moving-camera / egocentric SOT | Camera motion is part of the visual difficulty. VISTA was designed to separate first-person-viewpoint effects from human-object activity domain effects [R3](../references/references.md#r3). | Proof of robot-person tracking. |
| Target-person tracking (TPT) | Tracking a specific person from robot-egocentric views. TPT-Bench supplies this domain evidence [R1](../references/references.md#r1). | A social-impact or safety result. |
| Active embodied tracking | Perception and control are jointly evaluated. TrackVLA is an example of this broader direction [R5](../references/references.md#r5). | The present moving-camera perception scope. |

## Scope locks

- **[PROJECT DECISION]** Benchmark/model work comes before robot control.
- **[PROJECT DECISION]** Current input is RGB; planned LiDAR is not a current input modality.
- **[PROJECT DECISION]** Failure modes of interest are long occlusion, out-of-view re-entry, and similar-person distractors.
- **[PROJECT DECISION]** Detector initialization, tracker propagation, re-detection, and control must be timed and evaluated separately.
