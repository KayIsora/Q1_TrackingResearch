# Manager review request — Knowledge Graph content audit V1.2

## Requested decision

Please review whether the **scientific content** is ready for the user's manual drawing. This supplement does not draw the final graph and does not select a final SpikeTrack architecture.

## Review focus

1. Confirm the seven cross-neighborhood classifications in `17_cross_neighborhood_overlap_audit.md`.
2. Confirm that the 19 normalized cards distinguish design principles from non-transferable components.
3. Confirm the recommended 17 visible nodes and one primary presentation role per audited paper.
4. Confirm the eight branches and the semantic edge catalog.
5. Confirm that P027 Hybrid-KD is treated as the highest-risk collision and that its inaccessible full-text details remain `UNKNOWN`.
6. Confirm that the residual question is SNN-native and causal, not merely “apply pruning/KD to SpikeTrack.”

## Evidence limitations requiring Manager awareness

- P027's publisher abstract was available, but its full text was not openly retrievable. Exact pruning criterion/layers, teacher/student architectures, loss weights, retraining pipeline, parameter/FLOP/FPS tables, and edge-device protocol remain unresolved [E35].
- Device results across Titan Xp, V100, RTX 2080Ti/3090, CPU, Jetson AGX/Orin NX, MX250, analytical 45-nm energy, and any future target cannot be treated as interchangeable.
- Primary-source inspection supports mechanism descriptions; it does not validate transfer to SpikeTrack.

## Locked boundaries preserved

- Two anchors only: FARTrack (methodology) and SpikeTrack (redesign target).
- P01 + P02 remain one hypothesis family; P04 supports compression training; P06 remains engineering enablement.
- Generic dynamic computation is crowded/deferred.
- Whole-MRM1 conditional skip remains `DIAG_FAIL`; its hold-out is consumed and was not reused [E08].
- No tracker experiment, training, fine-tuning, runtime profiling, baseline reopening, final graph drawing, or final architecture selection occurred.

## Terminal state

`KNOWLEDGE_GRAPH_CONTENT_AUDIT_V1_2_READY_FOR_MANAGER_REVIEW`
