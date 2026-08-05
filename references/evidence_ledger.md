# Evidence ledger

This ledger constrains how each source may be used. It is intentionally shorter than a literature review: a source is not cited for claims beyond its stated scope.

| Claim ID | Label | Permitted statement | Source | Scope / caveat |
|---|---|---|---|---|
| E1 | FACT — cited | TPT-Bench contains 48 robot-egocentric target-person sequences collected in crowded/unstructured indoor/outdoor settings, with long occlusion and re-identification challenges. | [R1](references.md#r1) | The data collection used a pushed sensor cart; no autonomous-robot success claim follows. |
| E2 | FACT — cited | The public TPT record reports 5.3 h of recordings and 571,982 target-person boxes. | [R2](references.md#r2) | Copyright is listed in the record; do not re-host data. |
| E3 | FACT — cited | VISTA uses synchronized first- and third-person video to separate viewpoint effects from activity-domain effects. | [R3](references.md#r3) | It is not a robot-person-tracking benchmark. |
| E4 | FACT — cited | EgoTracks is a long-term egocentric tracking resource with per-frame location and presence confidence. | [R4](references.md#r4) | Respect Ego4D access conditions; do not turn it into person/robot evidence. |
| E5 | FACT — cited | TrackVLA represents a broader embodied-tracking direction that joins recognition and trajectory planning. | [R5](references.md#r5) | Not an embedded Nano baseline. |
| E6 | FACT — cited | VOT-LT2022 requires disappearance handling, re-detection, and confidence reporting. | [R6](references.md#r6) | Generic long-term tracking only. |
| I1 | INTERPRETATION — reasoned | Identity continuity after disappearance and similar-person distraction is the right immediate perception problem for this project. | E1–E6 | A project framing, not a publication result or social-impact ranking. |
| D1 | PROJECT DECISION — provisional | Use a consent-based guide/accompany scenario as the current application framing. | I1 | Must be reopened if the task, data, sensor, or field partner changes. |
| D2 | PROJECT DECISION — provisional | Treat TPT-Bench as domain validation and keep detector-assisted modes separate from pure SOT. | E1–E2 | Final protocol must be copied from the current official toolkit before experiments. |
| G1 | PROVISIONAL MEASUREMENT GATE | No Nano deployment claim before target-device profiling. | RULE 01 | Not a literature result or performance threshold. |
