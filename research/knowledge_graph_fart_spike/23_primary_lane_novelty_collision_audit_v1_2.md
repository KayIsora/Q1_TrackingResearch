# Primary research-lane novelty collision audit — V1.2

## Audited family

The strongest **hypothesis family**, not a final architecture, remains:

> fixed/static structural reduction of SpikeTrack + tracking-specific/task-facing knowledge preservation.

P01 + P02 are one family. CompressTracker supports the training strategy; P06 remains engineering enablement only. Generic dynamic routing is deferred, and the historical whole-MRM1 conditional skip remains `DIAG_FAIL` with consumed hold-out [E08].

## Collision map

| Prior work | Already occupies | Residual SpikeTrack question | Risk |
|---|---|---|---|
| FARTrack | Fixed depth variants, adjacent task-logit self-distillation, persistent template-token sparsity | Whether those principles can be made meaningful for spike stage/state/cache behavior | HIGH |
| CompressTracker | Heterogeneous stage replacement, stage feature mimic, prediction guidance | Whether SpikeTrack stage interfaces can be compressed without destroying temporal/cache semantics | MEDIUM-HIGH |
| MixFormerV2 | Progressive deep-to-shallow and dense-to-sparse distillation | Which SNN-native preservation targets matter beyond ordinary dense logits/features | HIGH |
| LiteTrack | Top-down layer pruning and asynchronous template extraction | Physical SpikeTrack structural reduction beyond already-present template caching | HIGH |
| HiT | Lightweight hierarchy with explicit detail repair | Whether fixed SNN stage reduction requires spike-specific information repair | HIGH |
| P027 Hybrid-KD | Static tracker-backbone pruning + token/local/global tracking KD | Causal value of spike/state/cache preservation beyond its Q/K/V, mask, and global semantic targets | **HIGHEST** |
| UETrack | Per-sample target-aware output/feature KD | When a SpikeTrack teacher is beneficial and what SNN-native evidence should control/define that training supervision | HIGH |
| ABTrack | Static ViT latent-dimension pruning + adaptive whole-block bypass | Static SNN-aware dimension materialization; dynamic route is deferred | HIGH |
| CPDATrack | Target-aware search-token pruning/attention control | Any SpikeTrack representation reduction must be topology- and spike-specific | HIGH |
| LoReTrack | Fixed spatial reduction + Q/K/V and discrimination KD | Whether lower density/resolution changes spike dynamics/cache retrieval in a distinct way | HIGH |
| SpikeFET | SNN spatial-temporal regularization | RGB-only SpikeTrack-specific preservation under structural compression | MEDIUM-HIGH |

## 1. What is already known?

- Transformer trackers can be made shallower, narrower, hierarchically cheaper, spatially smaller, or token-sparser.
- Accuracy can be preserved with task logits, prediction guidance, stage features, Q/K/V, target/background masks, or global semantic distillation.
- Template-once/asynchronous computation and persistent decisions are established.
- Dynamic block routes and early exits are established and carry controller/path overhead.
- SNN tracking and SNN spatial-temporal regularization are established.

Therefore neither “pruning,” “KD,” “tracking-specific KD,” “template caching,” nor “SNN tracker” is independently novel.

## 2. What remains genuinely unresolved for SpikeTrack?

- Which fixed SpikeTrack structural capacity is redundant **after** accounting for NI-LIF temporal/state dynamics rather than dense activation magnitude alone?
- Which task-facing signals are necessary to preserve center/size/offset behavior as capacity is removed?
- Whether conventional feature/logit KD preserves the six K-transpose-V cache interfaces and MRM retrieval behavior.
- Whether a smaller materialized SNN graph retains useful spike sparsity/state behavior and actual target-device benefit.
- How fixed-first/FIFO cache quality interacts with compression without conditional whole-MRM skipping.

These are scientific questions, not an architecture choice.

## 3. What would be merely “apply KD/pruning to an SNN” and therefore weak?

- Delete arbitrary SpikeTrack layers, then add standard feature MSE or output KL.
- Reuse Hybrid-KD's Q/K/V + foreground/background + global alignment and change only the backbone name to SpikeTrack.
- Claim novelty because the student uses spikes while the pruning criterion and supervision ignore spike state/timestep/cache behavior.
- Report only parameters/FLOPs or analytical energy without a physical graph and target-device measurement.
- Rebrand template caching or a whole-MRM gate as a new efficiency mechanism.

## 4. What SpikeTrack-native scientific question has plausible novelty?

A defensible question is whether **fixed structural reduction can preserve SpikeTrack's causal spike/state/cache function using SNN-native preservation evidence, and whether that evidence is necessary beyond conventional task/logit/feature KD**. Candidate observables include NI-LIF temporal/state response, spike distribution across stage/timestep, six cache-interface behavior, MRM retrieval response, and center/size/offset behavior. Which observables and structure matter is unresolved and must be tested later under a new authorized protocol.

## 5. Claims that should NOT be made

- “First pruned tracker,” “first efficient transformer tracker,” or “first tracking KD.”
- “First pruning + tracking-specific KD” or “novel hybrid KD.”
- “First SNN tracker” or “first spiking regularization.”
- “Dynamic MRM skipping works” or any reuse of the consumed hold-out.
- “Energy efficient on Jetson/device” from 45-nm analytical energy, FLOPs, CPU/GPU/AGX results, or MX250 runtime.
- “Final SpikeTrack architecture selected.”
- Any exact P027 pruning criterion, layer list, teacher/student identity, loss weights, or edge-device result until the full paper is verified.

## Decision

The family remains scientifically plausible only if narrowed to an SNN-native causal preservation question. It is **not** yet novel as “static prune + tracking KD,” and no final architecture is selected.
