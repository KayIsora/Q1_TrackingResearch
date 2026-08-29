# FARTrack architecture and design principles

## Evidence status

FARTrack is a peer-reviewed ICLR 2026 paper with an official implementation [E03, E04]. The paper architecture and pinned public code are not fully identical. This document keeps `PAPER FACT`, `CODE FACT`, and `INTERPRETATION` separate; code discrepancies are not used to erase the paper contribution.

## 1. Claimed paper path

```text
five template crops (112x112) -----> patch tokens --+
current search crop (224x224) -----> patch tokens --+--> one Transformer encoder
preceding boxes -------------------> trajectory ----+          |
four coordinate commands ----------> command tokens-+          +--> four coordinate-vocabulary distributions
                                                                    --> dequantized current box
```

**PAPER FACT.** Five template streams, the current search, prior quantized trajectory tokens, and four command tokens share an encoder. The four commands correspond to the box coordinates; autoregression is framed across the trajectory history, not as an established four-step within-box decoder [E03].

**CODE FACT.** The pinned release uses five 112x112 templates, one 224x224 search crop, stride-16 patching, embedding width 192, a 605-entry vocabulary, and four simultaneous 605-way command outputs. Five templates contribute 245 tokens, search contributes 196, and commands contribute four, for 445 active input positions in the released path [E04].

**CODE/PAPER MISMATCH.** The tracker constructs historical boxes, but the sparse backbone assigns them to `trajectory` and then replaces the encoder text input with only the four command tokens; the defined historical-position embedding is not added. The public inference path therefore does not demonstrate explicit historical-coordinate conditioning inside the encoder. Its practical recurrence instead includes previous-box cropping, template history, and persistent masks [E04].

## 2. Encoder and coordinate prediction

The release uses ViT-Tiny with 12 base blocks plus three extension blocks. A learned six-way identity embedding separates five template slots from the search stream. Output projection weights are tied to the token embedding; the four command representations are read in parallel. The tracker combines expectation- and argmax-derived coordinates before mapping the crop-relative box back to the image [E04].

This matters for transfer: FARTrack demonstrates a task-facing coordinate distribution at multiple depths, but it does not establish that SpikeTrack should replace its center head with coordinate tokens. The safe transferable object is the supervised task distribution, not the head topology.

## 3. Task-Specific Self-Distillation (TSSD)

At adjacent depths, the shallower exit is the student and the next exit is a detached teacher. KL is applied to coordinate/task logits rather than indiscriminately matching all template/search hidden features [E03, E04]. In the release:

1. coordinate-vocabulary exits are exposed from depths 5 through 15;
2. each adjacent deeper distribution supervises the previous exit;
3. KL covers the 600 coordinate entries and excludes five special symbols;
4. intermediate and final exits also receive coordinate cross-entropy and SIoU supervision;
5. one trained deep model supports shallower prefix operating points [E04].

The release objective is effectively `2 * mean(SIoU) + 2 * mean(CE) + 0.01 * mean(adjacent KL)`. The paper reports that 10- and 6-layer distilled variants beat same-depth scratch training and that adjacent-layer TSSD is more effective than manually paired deep-to-shallow distillation [E03, E04].

**Training discrepancy.** The paper describes 300 TSSD epochs, while the released distillation YAML specifies 500. Learning-rate grouping also differs. These values require author clarification before a strict reproduction claim [E03, E04].

## 4. Depth reduction and variants

All variants retain ViT-Tiny width, input sizes, and five templates; deployed depth is the principal structural difference [E03].

| Variant | Layers | Parameters | MACs | GOT-10k AO | Reported GPU / CPU / NPU FPS |
|---|---:|---:|---:|---:|---:|
| Tiny | 15 | 6.82M | 2.65G | 70.6 | 135 / 53 / 42 |
| Nano | 10 | 4.59M | 1.78G | 69.9 | 210 / 77 / 61 |
| Pico | 6 | 2.81M | 1.08G | 62.8 | 343 / 121 / 101 |

These reported speeds use Titan Xp, Xeon Gold 6230R, and Ascend 310B, not Jetson Nano [E03]. Nano is the flatter accuracy-efficiency point; Pico shows that task-specific distillation does not eliminate the information floor created by aggressive depth removal. The public main branch exposes a 15-layer sparse configuration but does not clearly expose independent Nano/Pico depth configs, so exact deployment truncation remains under-documented [E04].

## 5. Inter-frame Autoregressive Sparsification (IFAS)

**PAPER FACT.** IFAS reads template-token salience from search-to-template and command-to-template attention, retains the top tokens at a fixed ratio, saves the mask with each template, and reuses the decision in later frames. Masked tokens are excluded from valid-token normalization. The selected paper setting combines a central 3x3 search region with command attention; 75% retention is the reported operating point [E03].

**Released mask lifecycle [E04]:**

1. initialization stores five copies of the first template and an all-valid 445x445 mask;
2. old templates carry their stored 49-bit masks while the newest begins unmasked;
3. attention is averaged over heads and accumulated over encoder layers;
4. only the newest template’s 49 tokens are ranked;
5. the first candidate prunes 25%, so 75% remains;
6. the predicted crop and its mask enter template history;
7. five sampled template masks plus 196 search and four command positions form the next attention mask.

The final released tracker samples the initial template and recent templates with exponential decay, although the main text describes linear updating [E03, E04]. This stable-plus-recent policy is a useful drift-control principle.

## 6. Sparsity implementation caveats

- The selected paper mechanism is `S3x3 + C`; active code uses central `S1x1` search attention, while adding command attention is commented out [E03, E04].
- The public attention path still forms dense Q/K/V, dense attention scores, and dense attention-value products; applying a Boolean mask does not itself compact tokens or invoke sparse CUDA kernels [E04].
- The paper describes restoring ordinary LayerNorm at inference, while the public blocks are called with attention return enabled and select masked normalization [E04].
- The sequence-sparsification actor zeros its CE weight and, with the released L1 weight of zero, optimizes weighted SIoU only. This differs from a naive reading of the paper’s combined loss [E04].

Therefore the paper’s MAC/speed benefit is valid as a reported result, but exact public-code parity and the kernel-level source of that benefit remain unresolved.

## 7. Training stages and losses

The paper sequence is frame-level AR(0) pretraining (500 epochs, 76,800 pairs/epoch), TSSD, then continuous 32-frame IFAS clips (1,000 clips/epoch for 20 epochs). The paper objective is `L = L_CE + lambda1 L_SIoU + lambda2 L_KL`; code-stage weights differ as noted above [E03, E04]. TSSD is offline cost; Tiny/Nano/Pico inference does not add a teacher.

## 8. Components versus principles

| FARTrack component | Extracted design principle | SpikeTrack-safe interpretation |
|---|---|---|
| Adjacent-depth KL on coordinate logits | Preserve the distribution closest to the task when making a model shallow. | Distill SpikeTrack center/box behavior or MRM-conditioned task states; do not copy the coordinate-token head by default. |
| Task loss at every depth | Make intermediate prefixes independently predictive before truncation. | Add supervised exits only during training; evaluate static prefixes, not input-conditioned MRM skipping. |
| One-run 15->10/6 training | Make depth a selectable deployment operating point. | Train a finite static depth family with shared teacher evidence. |
| Attention-derived template masks | Reuse salience already produced by the tracker rather than adding a new selector network. | Derive conservative cache/channel compression from existing MRM signals, with retraining and parity controls. |
| Persistent per-template masks | Amortize representation reduction across frames. | Store a compact decision with each SpikeTrack template memory; refresh only on template updates. |
| Initial plus recent templates | Keep a stable identity anchor while adapting to appearance. | Preserve the fixed first template and quality-control later updates. |
| Moderate 75% retention | Remove demonstrated redundancy conservatively. | Sweep bounded static ratios; aggressive compression is an accuracy-risk hypothesis. |
| Depth plus token reduction | Reduce resident capacity and input-dependent compute on separate axes. | Measure each axis independently before any combination. |

## 9. Transfer boundary

FARTrack is a knowledge anchor, not a component library. TSSD and IFAS support principles about task-facing supervision and temporal amortization. They do not prove that coordinate tokens, transformer attention masks, or a particular update rule are compatible with NI-LIF features or SpikeTrack MRMs. Every transfer in `08_spiketrack_redesign_space.md` is therefore phrased as a SpikeTrack-specific, retrained, falsifiable test.
