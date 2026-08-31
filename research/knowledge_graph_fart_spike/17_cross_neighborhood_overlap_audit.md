# Cross-neighborhood overlap audit — V1.2

## Decision rule

`source_graph=BOTH` proves only that the identity occurs in both supplied BibTeX exports [E01, E02]. A semantic bridge additionally requires a mechanism that functionally connects FARTrack's lightweight-design concepts to a concrete SpikeTrack redesign concern. No Connected Papers similarity edge, weight, or topology is inferred.

| Paper | FARTrack-neighborhood concept | SpikeTrack-neighborhood concept | Exact audited mechanism | Relation test | Classification | Visible node? |
|---|---|---|---|---|---|---|
| Adaptive Target Oriented Tracking (ATOTrack) | Target-aware selection resembles IFAS's target-relevant token retention | Suppressing distractor/background evidence relates to SpikeTrack's reported fine-grained/similar-object weakness | One-stream tracker with untied positional encoding and Auto-Mask Learner that masks ineffective non-target search information to learn an adaptive target-oriented representation | Functional within target filtering, but no demonstrated structural reduction or SpikeTrack-compatible preservation signal; overlap is contextual | `CONTEXTUAL_REFERENCE` | No |
| Correlation-Embedded Transformer Tracking (SBT / SuperSBT) | Single-branch joint relation modeling provides context for one-stream efficiency design | Correlation depth and multi-level template-search relation are relevant only as an alternative to the six-MRM design | SBT is the Single-Branch Tracking baseline/framework; SuperSBT is the improved tracker with cross-image correlation embedded through multiple backbone layers | Mechanism is real, but its connection to the favored fixed reduction + task-facing preservation family is bibliographic/framework-level | `CONTEXTUAL_REFERENCE` | No |
| LoReTrack | Reduces a fixed representation axis and restores task behavior through teacher/student supervision | Asks what interaction and target/background evidence must survive a reduced SpikeTrack representation | Frozen high-resolution OSTrack teacher; low-resolution student; search-only final-layer Q/K/V MSE and target-weighted discrimination KD | Genuinely functional on both sides: explicit reduction plus tracking-facing preservation | `TRUE_SEMANTIC_BRIDGE` | Yes |
| DyTrack | Reduces average executed depth and uses self-distillation | Directly collides with the rejected whole-MRM conditional-skip direction | Input-conditioned routes, intermediate exits, feature recycling, and target-aware self-distillation | Functional dynamic-compute reference, but negative/competitive rather than a bridge into the favored static lane | `NOVELTY_COLLISION_ONLY` | Yes, marked CROWDED/DEFERRED |
| FastSeqTrack | Parallelizes coordinate-token generation and accelerates a SeqTrack/FARTrack-like sequence head | SpikeTrack already predicts center/size/offset in parallel and has no coordinate-token decoder | Four parallel tracking tokens with parameter-sharing decoder exits | Functional primarily for autoregressive sequence heads; no material SpikeTrack transfer | `ONE_SIDED_DONOR` | No |
| HiT | Demonstrates a fixed lightweight hierarchical tracker and preservation of lost detail | Stage reduction plus an explicit cross-level preservation path is analogous to a SpikeTrack stage-design question | LeViT hierarchy, deep-to-shallow Bridge Module, and dual-image positional encoding | Functional on both sides at design-principle level, though components are not portable | `TRUE_SEMANTIC_BRIDGE` | Yes |
| SeqTrack | Architectural ancestor/context for coordinate-token sequence tracking | No direct static compression, SNN, cache, or task-preservation mechanism | Encoder-decoder tracker generates discretized x/y/w/h tokens autoregressively using CE | Real ancestry for FARTrack's paradigm; relation to SpikeTrack is contextual only | `CONTEXTUAL_REFERENCE` | No |

Evidence: Adaptive Target Oriented Tracking / ATOTrack [E29]; Correlation-Embedded Transformer Tracking (SBT / SuperSBT) [E30]; LoReTrack [E15]; DyTrack [E08, E13]; FastSeqTrack [E14]; HiT [E18]; SeqTrack [E31].

## Result

- Exact mutually exclusive counts: 2 `TRUE_SEMANTIC_BRIDGE`, 1 `ONE_SIDED_DONOR`, 1 `NOVELTY_COLLISION_ONLY`, 3 `CONTEXTUAL_REFERENCE`, 0 `PRESENTATION_OMIT`.
- Co-membership is never used as an edge in `21_drawing_edge_catalog_v1_2.csv`.
- Only LoReTrack, DyTrack, and HiT remain visible; DyTrack is shown as a warning/collision, not a positive bridge.
