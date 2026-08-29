# SpikeTrack architecture, costs, and deployment bottlenecks

## Evidence status

SpikeTrack is a peer-reviewed CVPR 2026 paper with official code [E05, E06]. Exact released structure below is pinned to commit `1537db51a1cc9f6e30cce469fba3e51f5721b3d0` [E23]. Project measurements are limited to the accepted S256-T1 MX250 runtime; there is no Jetson Nano measurement [E07].

## 1. End-to-end state path

```text
initial bbox -> factor-4 template crop -> T=1 or T=3 template stack
            -> template SDT-v3 encoder -> six K^T V memory matrices -> persistent cache

each frame: previous bbox -> factor-4 search crop -> one-timestep search SDT-v3 encoder
           -> MRM1 -> MRM2 -> MRM3 -> MRM4 -> MRM5 -> MRM6
           -> three-tower spike center head -> score/size/offset maps
           -> windowed decode -> image-space bbox -> next-frame state
```

Released variants are S256-T1, S256-T3, B256-T1, B256-T3, B384-T1, and B384-T3. At T3 initialization the first template is repeated; index zero remains fixed while later positions rotate during updates. The search crop enters with temporal length one [E05, E06, E23].

## 2. Spiking backbone

Template and search use logically shared-weight asymmetric SDT-v3 branches. Early stages are spike CNN blocks; later stages are spike Transformer blocks [E05].

| Region | Small channels | Base channels | Released blocks | 256-grid progression |
|---|---:|---:|---:|---|
| 7x7 stride-2 stem | 16 | 32 | stem + 1 CNN SNN block | 256 -> 128 |
| Stage 1 | 32 | 64 | 1 CNN SNN block | 128 -> 64 |
| Stage 2 | 64 | 128 | 2 CNN SNN blocks | 64 -> 32 |
| Stage 3 | 128 | 256 | 6 Transformer SNN blocks | 32 -> 16 |
| Stage 4 | 192 | 360 | 2 Transformer SNN blocks | 16 -> 16 |

For 384 inputs, the final grid is 24x24. Efficient spike-driven self-attention computes `Q(K^T V)` without softmax and has linear token-length complexity in its analytical formulation. The released PyTorch path still uses dense convolution, linear, and matrix-multiplication kernels [E05, E23].

## 3. NI-LIF temporal representation

The normalized integer LIF neuron uses learned decay and quantizes spikes to `{0, 0.25, 0.5, 0.75, 1}` with `D=4` [E05, E23]. The custom autograd forward performs clamp, round and divide; the implementation loops over temporal indices, writes into a dense output tensor, and resets membrane state on every module forward. It does not preserve membrane state across video frames. Cross-frame state is the template cache and previous box, not neuron membrane [E23].

This distinction is central: discrete spike values can support neuromorphic operation accounting, but they are stored and processed as dense FP32 tensors in the released CUDA implementation.

## 4. Six exact MRM sites

Every released variant contains six MRMs with channel indices `[0, 1, 2, 2, 3, 3]` [E23].

| MRM | Location | External grid (256 / 384) | Small C | Base C | Small cache `[T,B,H,C/H,4C/H]` | Base cache |
|---|---|---:|---:|---:|---|---|
| 1 | after first stage downsample, before Stage 1 block | 64 / 96 | 32 | 64 | `[T,B,8,4,16]` | `[T,B,8,8,32]` |
| 2 | after Stage 2 downsample, before its blocks | 32 / 48 | 64 | 128 | `[T,B,8,8,32]` | `[T,B,8,16,64]` |
| 3 | after Stage 3 downsample, before block 1 | 16 / 24 | 128 | 256 | `[T,B,8,16,64]` | `[T,B,8,32,128]` |
| 4 | after Stage 3 block 3 | 16 / 24 | 128 | 256 | `[T,B,8,16,64]` | `[T,B,8,32,128]` |
| 5 | after stride-1 Stage 4 downsample | 16 / 24 | 192 | 360 | `[T,B,8,24,96]` | `[T,B,8,45,180]` |
| 6 | after both Stage 4 blocks | 16 / 24 | 192 | 360 | `[T,B,8,24,96]` | `[T,B,8,45,180]` |

MRM1 and MRM2 pool to the final grid before retrieval and bilinearly restore the stage grid afterward. MRM3-6 already operate at the final grid [E23].

## 5. Template memory construction

At each MRM site, template features receive timestep-specific position information, NI-LIF activation, and K/V projections. V expands channels fourfold. Across eight heads the template branch precomputes `M = K^T V`, removing spatial token length from persistent memory. It caches the matrix, not raw K and V [E05, E23].

For batch one, all six FP32 caches total approximately 0.213 MiB for Small-T1, 0.639 MiB for Small-T3, 0.783 MiB for Base-T1, and 2.350 MiB for Base-T3. The cache is therefore compact; model modules and activations dominate residency [E23].

## 6. Search-memory interaction

Each MRM applies a Retriever residual and then a two-layer channel-MLP residual. The Retriever pools when needed, forms a Q projection, temporarily repeats Q across template timesteps, performs `Q @ M`, applies timestep-specific spatial convolution and feedback, performs a second retrieval, fuses T slots with learned channel weights, projects `4C -> C`, and restores the original stage grid [E05, E23].

T3 does not run the complete search backbone three times. It does increase work and parameters inside all six MRMs because the query is expanded and fused there. The released recurrent retrieval count is one; the paper reports that more loops can accumulate error and over-concentrate attention [E05, E23].

## 7. Head, loss, training, and online update

The final feature enters three parallel Conv-BN-NI-LIF towers for center, size, and offset. Temporal maps are averaged; the center argmax indexes size and offset [E05, E23]. Training uses:

`L = L_focal + 2 L_GIoU + 5 L1`.

There is no explicit spike-rate, energy, sparsity, memory-compression, distillation, or template-quality loss [E05, E23]. T1 trains 320 epochs; T3 initializes from T1 and trains 60 more epochs. Changing width, timestep, MRM count/location/dimension, cache format, or head interfaces is therefore a retraining problem, not an inference toggle [E05].

Online update preserves the first template. Non-LaSOT defaults use interval 25 and score threshold 0.7; the localization score doubles as confidence. An update reruns the entire template encoder and rebuilds all six memories for the queue rather than incrementally updating one cache [E05, E23].

## 8. Theoretical energy efficiency

The paper’s analytical model counts conventional ANN MAC energy and SNN accumulate energy using 45 nm constants (`4.6 pJ` per MAC and `0.9 pJ` per AC), spike firing rate, timestep, and quantization depth. Template cost is amortized over the update interval [E05]. The theoretical case rests on:

- spike-driven operations that can become sparse additions on suitable hardware;
- softmax-free linear self-attention;
- one-timestep search backbone outside MRM expansion;
- compact precomputed template memories;
- infrequent template recomputation.

These are analytical operation-energy arguments, not measured board power, battery energy, temperature, or Jetson latency.

## 9. Ordinary GPU / Jetson-style costs

| Theoretical property | Released conventional-runtime consequence |
|---|---|
| spike-valued activation | dense FP32 tensors and dense CUDA Conv/Linear/matmul |
| low firing rate | no automatic sparse-add kernel selection |
| T1 search | Python temporal loops and six MRM calls still execute |
| compact cache | separate template encoder remains resident |
| cached template | full queue/template path reruns on an update |
| softmax-free backbone attention | MRM fusion still contains softmax and ordinary dense operators |
| operation-energy estimate | no corresponding Jetson board-power measurement |

The accepted S256-T1 project trace measured 11,760,130 search+head parameters plus 7,663,086 template-encoder parameters, for 19,423,216 resident parameters and 74.094 MiB FP32 parameter storage. The paper’s logical weight sharing does not translate to shared storage in the released two-module inference construction [E07, E23].

On the exact MX250 BS1 FP32 test, pooled model median was 307.987 ms (3.247 FPS) and end-to-end median was 312.460 ms (3.200 FPS) [E07]. These are not Jetson, TensorRT, FP16, or publication benchmark results.

## 10. Deployment-sensitive structure

Confirmed source/runtime blockers are the six-tensor Python dictionary cache boundary, a mode-dispatch signature defect, and host-side crop/state/window/decode/map-back logic. Likely exporter risks include custom autograd quantization, round/clamp, Python time loops, clone/detach, indexed tensor writes, shape branches, repeat/stack, adaptive pooling, bilinear interpolation, gather/modulo, and fixed-resolution positional embeddings [E07, E24]. No successful ONNX export, TensorRT build, or parity test exists.

Several branch-unused structures are resident in the pinned code (for example search-side K/V projections and T1 temporal gates). Removing them is a parity-sensitive engineering cleanup candidate, not by itself a scientific contribution [E23].

## 11. Accuracy constraints

The paper identifies deformation, fast motion, similar-object interference, insufficient fine-grained spike semantics, and template-update quality as weaknesses. Ablations warn that vanilla spike cross-attention reduces energy but also accuracy; direct AsymTrack-style modulation collapses performance more severely; fixed decay and mean fusion are worse; excessive retrieval loops accumulate errors [E05]. A redesign must therefore preserve target information while reducing cost.

## 12. Historical null-result boundary

The prior frozen conditional whole-MRM1 predictor failed its sealed sequence-disjoint hold-out: AUROC 0.4815 was below 0.65, Brier 0.2575 was worse than the 0.2500 constant baseline, and the hold-out is consumed [E08]. Conditional whole-MRM1 skipping is not an active proposal. No inversion, refit, new threshold, subgroup selection, or post-hoc feature rescue is permitted on that data. This null result also does not prove that MRM1 should be removed or that its Retriever caused the observed failures.

## 13. Factual blockers

- no Jetson Nano FPS, board power, temperature, or energy measurement;
- no ONNX/TensorRT export and parity evidence;
- no specialized sparse-spike CUDA kernel evaluation;
- no parity-tested runtime-module consolidation;
- no trained evidence for altered width, timestep, MRM count/dimension, head, memory, or loss.
