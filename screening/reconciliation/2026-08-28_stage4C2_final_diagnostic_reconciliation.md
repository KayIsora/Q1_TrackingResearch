# Stage 4C2 / Stage 4D — SpikeTrack final diagnostic reconciliation

**Date:** 2026-08-28  
**Status:** `DIAG_FAIL`  
**Source commit reviewed:** `ef78ee1ad54611932f30051447c0c6a67b80e358`

## Boundary

This reconciliation closes the locked SpikeTrack diagnostic program. It decides whether the complete evidence chain A+B+C+D permits soft scoring and main-baseline consideration under the current research gap.

It does not declare SpikeTrack a weak published tracker, erase the valid positive findings from discovery, authorize a new post-hoc predictor, assign S1–S7, select another baseline, or design a proposed architecture.

## 1. Stage-4C2 execution acceptance

Manager accepts the one-shot hold-out execution package:

- every Manager-seal hash matched before hold-out images were opened;
- the frozen predictor numerical preflight passed with maximum probability difference `1.1102230246251565e-16` against the reconstructed, never-fit sklearn object;
- exactly one hold-out execution occurred;
- all eight frozen hold-out pairs and the expected 326 frame rows were executed;
- no discovery refit, feature change, coefficient change, probability inversion, threshold selection, recalibration or physical-patch change occurred;
- every sequence was initialized once from the official sequence start, advanced sequentially and forked from the exact frozen prefix state;
- whole-MRM1 physical call proof passed on all 326 rows;
- MRM1 forward, Retriever, MLP and internal-operator counts were zero in the physical branch while MRM2–MRM6 remained unchanged;
- all required bounded machine-readable artifacts and hashes were committed;
- no technical failure occurred after unsealing and no second attempt was made.

The scientific result is therefore a valid one-shot falsification result, not an execution blocker or `DIAG_PENDING` case.

## 2. Criterion D decision — ACCEPTED FAIL

### Locked complete-set results

- hold-out rows: `326`;
- positive oracle labels: `161`;
- negative oracle labels: `165`;
- frozen-predictor AUROC: `0.48153585544889893`;
- locked AUROC minimum: `0.65`;
- frozen-predictor Brier score: `0.2575449361739645`;
- constant-comparator Brier score: `0.24996241633654945`;
- Brier improvement (`constant - predictor`): `-0.007582519837415064`.

Criterion D required both:

1. AUROC at least `0.65`; and
2. strictly positive Brier improvement.

The frozen predictor satisfies neither condition. Criterion D therefore fails.

### Bootstrap sensitivity

The failure is not a narrow point-estimate accident:

- primary-sequence AUROC 95% CI: `[0.395854462474645, 0.5365867077464789]`;
- connected-component AUROC 95% CI: `[0.3520137784843667, 0.5314812367864693]`;
- primary-sequence Brier-improvement 95% CI: `[-0.013718306169805239, -0.0009802549977089002]`;
- connected-component Brier-improvement 95% CI: `[-0.015918241679176937, -0.002365210620350915]`.

Both Brier-improvement intervals remain strictly negative. No predeclared sensitivity subgroup reaches the complete-set Criterion-D gate, and no subgroup is permitted to rescue it.

## 3. Hold-out behavior of physical MRM1 skip

Across the complete hold-out rows:

- mean baseline IoU: `0.6966660323287523`;
- mean physical-skip IoU: `0.6903059898208668`;
- mean oracle skip benefit: `-0.006360042507885561`.

Thus, always skipping MRM1 is slightly harmful on average in hold-out, although individual frames are nearly balanced between positive and non-positive benefit. This reinforces the need for a genuinely predictive conditional signal—the exact requirement that failed.

The hold-out timing characterization is descriptive only:

- baseline median model-forward with feature capture: `232.05159999633906 ms`;
- physical-skip median with counters: `232.83005000121193 ms`;
- median feature-extraction overhead: `6.138349999673665 ms`;
- approximate feature-adjusted skip-path saving: `-2.9807163599197883%`.

These numbers do not reselect Criterion C, which remains passed under its locked discovery timing contract. They show that the tested conditional-computation route is not presently actionable as an end-to-end policy.

## 4. Final A+B+C+D state

| Criterion | Final state | Narrow interpretation |
|---|---:|---|
| A | PASS with fragility warning | frozen discovery package showed positive IoU weakness under the locked primary clustering rule; generality was source-design-sensitive |
| B | PASS for whole MRM1 only | MRM1 had condition-dependent harmful utility in discovery; refinement localized the effect to the MRM1 MLP residual rather than Retriever |
| C | PASS with narrow margin | actual whole-MRM1 non-execution saved `5.462%` median model-forward latency on the discovery environment |
| D | **FAIL** | the exact frozen pre-MRM predictor did not generalize to sequence-disjoint hold-out and was worse than a constant comparator |

The diagnostic protocol requires all A, B, C and D to pass. Therefore:

`DIAG_FAIL`.

## 5. Scientific interpretation

The current evidence supports the following null-result package:

1. SpikeTrack can be weaker on selected similar-distractor intervals, but the measured complete-set effect is sensitive to source/control design.
2. Whole MRM1, specifically its MLP residual, can become conditionally harmful in discovery.
3. Physically removing whole MRM1 produces a small but measurable model-forward saving.
4. The fixed, inference-available pre-MRM signals tested here do **not** predict skip benefit out of sample.
5. Therefore the intended actionable coupling—predict when MRM1 should be skipped to jointly improve robustness and efficiency—was not established.

The result does **not** support a claim that template-memory retrieval is the cause; Retriever-only and T3 template/time-path refinements did not establish such an effect.

## 6. Prohibited post-hoc rescue

The sealed hold-out has now been consumed. Under the current diagnostic program, it is prohibited to:

- invert predictor probabilities or labels;
- refit on hold-out;
- add/drop/reorder features after inspecting hold-out;
- switch to a nonlinear model and report the same hold-out as validation;
- select a new MRM, threshold or subgroup from these outcomes;
- relabel ties or tune an oracle-benefit margin;
- present the discovery-only `5.462%` saving as a deployable conditional policy result.

A materially new predictor/hypothesis would require a new, independently frozen development/validation design and a new novelty audit. It cannot continue as if Stage 4D had passed.

## 7. Candidate consequence

For the current research gap:

- SpikeTrack does not proceed to S1–S7 soft scoring;
- SpikeTrack is not selected as the main baseline;
- SpikeTrack remains a useful scientific reference, lightweight SNN tracker, diagnostic null-result case and possible host for a future materially different hypothesis;
- the active main-baseline candidate count returns to zero.

HG6 remains historically `PASS` for the narrow literature question that entered diagnostics. `DIAG_FAIL` is a later empirical gate and does not rewrite the literature audit.

## 8. Program consequence

The project must not select the last remaining candidate by default. The next valid action is a separately locked fallback cycle:

1. preserve the SpikeTrack null result;
2. mechanically synchronize the canonical matrix and Stage-4 plan;
3. reopen only held candidates with explicit missing-evidence contracts, or refresh the 2026 candidate universe;
4. require a new candidate to pass the same gap, novelty and falsification standards.

## Final locked state

- Stage 4A: **COMPLETE**;
- Stage 4B: **COMPLETE / A+B ACCEPTED**;
- Stage 4C1: **COMPLETE / C ACCEPTED**;
- Stage 4C2: **COMPLETE / D FAIL ACCEPTED**;
- Stage 4D: **COMPLETE**;
- final diagnostic state: **DIAG_FAIL**;
- SpikeTrack soft scoring: **NOT APPLICABLE under current gap**;
- primary shortlist: **NONE**;
- main baseline: **NONE**;
- proposed architecture: **NONE**.
