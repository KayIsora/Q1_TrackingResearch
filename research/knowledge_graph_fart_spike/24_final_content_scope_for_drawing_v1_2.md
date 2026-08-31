# Final content scope for manual drawing — V1.2

## Recommended research story

Draw 17 tracker/paper nodes: two fixed anchors, four primary donors, two semantic bridges, five secondary donors, and four visible novelty collisions. Keep FARTrack as the methodology anchor and SpikeTrack as the sole redesign target. Do not promote any third tracker to anchor/baseline status. The arithmetic is `2 + 4 + 2 + 5 + 4 = 17`.

The graph should read left-to-right:

1. **Known efficiency mechanisms** grouped by branch.
2. **Reduction + preservation family** converging on SpikeTrack.
3. **Collision/deferred band** showing what is crowded or unsafe to claim.
4. **SpikeTrack-native unresolved question**, explicitly marked “hypothesis family; architecture not selected.”

## Eight-branch taxonomy decision

The proposed eight branches are sufficient and should remain separate. They differ by the resource/action being changed, not only terminology.

| Branch | Scientific boundary | Visible exemplars | Drawing instruction |
|---|---|---|---|
| 1. STATIC STRUCTURAL COMPRESSION | Always-executed stage/depth/width/backbone is physically smaller | FARTrack, MixFormerV2, LiteTrack, HiT | Main reduction side of primary lane |
| 2. KNOWLEDGE PRESERVATION | Training-only transfer preserves task/intermediate behavior | CompressTracker, UETrack; FARTrack also contributes | Main preservation side; visually join with Branch 1 as one family |
| 3. SPARSIFICATION / PRUNING | Tokens/features/blocks/channels/representations are selected or removed | CPDATrack, HKDT; ABTrack has a static lesson | Keep distinct because granularity/selection evidence differs from choosing a shallower architecture |
| 4. TEMPLATE-SEARCH ASYMMETRY & REUSE | Initialization-only evidence is separated from per-frame work | AsymTrack, LiteTrack, SpikeTrack | Mark “already present in SpikeTrack” |
| 5. SPATIAL EFFICIENCY | Input sampling/resolution is reduced | LoReTrack, ZoomTrack | Orthogonal secondary path |
| 6. TEMPORAL MEMORY & ROBUSTNESS | Persistent evidence quality/update is changed | MCITrack, STDTrack, SpikeTrack | Supporting robustness lane, not primary compute claim |
| 7. SNN-SPECIFIC REPRESENTATION & TRAINING | Spike dynamics/timestep/state/regularization define the mechanism | SpikeTrack, SpikeFET | Required novelty-headroom context |
| 8. DYNAMIC COMPUTATION | Execution path varies by input | DyTrack, ABTrack | Red/caution band: `CROWDED / DEFERRED`; not primary lane |

Branch 1 and Branch 2 should be visually coupled, but not merged: one states **what is reduced**, the other **what is preserved/how it is trained**. Branch 3 remains distinct because pruning may act within a fixed depth and has its own selectors/criteria/collisions. Branch 8 remains distinct because conditional execution has control overhead and a locked negative result.

## Visible node scope (17)

- **Anchors (2):** FARTrack, SpikeTrack.
- **Primary donors (4):** CompressTracker, MixFormerV2, LiteTrack, UETrack.
- **Semantic bridges (2):** LoReTrack, HiT.
- **Secondary donors (5):** AsymTrack, MCITrack, ZoomTrack, STDTrack, SpikeFET.
- **Novelty collisions (4):** HKDT — Hybrid-KD Pruning Tracker, ABTrack, CPDATrack, DyTrack.

Omit FastSeqTrack and ARPTrack from the drawing. Also omit the cross-neighborhood contextual papers Adaptive Target Oriented Tracking (ATOTrack), Correlation-Embedded Transformer Tracking (SBT / SuperSBT), and SeqTrack. Their audit remains in text so omission is evidence-based, not accidental.

## Visual semantics

- Use solid arrows only for `knowledge_donor_to`, `semantic_bridge_to`, `demonstrates_principle`, or `supports_training_strategy`.
- Use red/dashed arrows for `novelty_collision_with` and `negative_transfer_warning`.
- Label DyTrack/ABTrack's dynamic aspect `CROWDED / DEFERRED`.
- Label HKDT `HIGHEST GENERIC-FAMILY NOVELTY COLLISION` and clarify that this concerns static structural pruning + tracking-specific multi-level KD, not every possible SpikeTrack-native mechanism.
- Label the primary family `static structural reduction + tracking-specific/task-facing preservation`.
- Label the endpoint `unresolved SpikeTrack-native scientific question — no final architecture`.
- Do not draw Connected Papers proximity/similarity edges.

## Content-level validation

- Raw inventory remains 82 rows and its locked hash is unchanged; 74 deduplicated identities and seven exact co-memberships remain unchanged.
- Anchors remain FARTrack and SpikeTrack; no third baseline is introduced.
- All 17 visible nodes have primary/project evidence identifiers.
- Every catalog edge states a semantic mechanism; no Connected Papers topology is fabricated.
- ABTrack, UETrack, ZoomTrack, and P027 HKDT are explicitly audited.
- P027 is present in the collision audit with abstract-only limitations.
- Whole-MRM1 conditional skipping remains `DIAG_FAIL`; the consumed hold-out is not reused.
- No experiment, training, profiling, graph drawing, or final architecture selection was performed.
