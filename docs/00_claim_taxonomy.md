# Claim taxonomy

This repository uses the claim classes below so that paper facts, code observations, project choices, hypotheses, and screening decisions cannot silently collapse into one another.

The taxonomy is subordinate to `RULE/01_EVIDENCE_AND_CITATION_POLICY.md`. The six core classes from RULE remain authoritative; the operational sublabels below only refine them for tracker screening and code audit.

## 1. Core claim classes

| Label | Meaning | Required handling |
|---|---|---|
| **FACT — cited** | Externally verifiable statement directly supported by a traceable primary/official source. | Cite the exact source and state hardware/dataset/protocol/version boundaries. |
| **INTERPRETATION — reasoned** | Reasoning derived from one or more facts. | State the supporting facts; do not rewrite the inference as an author conclusion. |
| **PROJECT DECISION — provisional** | A reversible local choice of scope, method, benchmark, or workflow. | Preserve until a documented decision changes it. |
| **PROJECT DECISION — locked scope** | A local choice explicitly frozen for the current research stage. | Do not silently change it during candidate screening; reopen only through an explicit review. |
| **HYPOTHESIS — untested** | A falsifiable statement that must be tested experimentally. | Never present as an achieved contribution or confirmed failure mechanism. |
| **PROVISIONAL TARGET** | Internal success threshold or go/no-go target. | Do not attribute it to a paper, benchmark, or standard unless independently sourced. |
| **OPEN QUESTION** | Information not yet established and capable of changing the research decision. | Seek evidence; do not fill the gap by assumption. |

## 2. Operational sublabels used during systematic screening

These are refinements of the core classes, not additional epistemic classes.

| Operational label | Parent class | Meaning / use |
|---|---|---|
| **CODE FACT — inspected** | FACT — cited | Behavior, architecture, configuration, operator, or update path directly observed in a specific released source-code version/path. Cite or record repository, commit/ref, and file/function when possible. |
| **AUTHOR-REPORTED LIMITATION — cited** | FACT — cited | A limitation explicitly stated by the paper/authors. It does not prove a broader failure mechanism beyond the wording supported by the source. |
| **RESOURCE AVAILABILITY FACT — cited** | FACT — cited | Official code/checkpoint/evaluator/release availability verified from an official repository or project page. Availability does not prove correctness or reproducibility. |
| **RESEARCH GATE — project decision** | PROJECT DECISION / PROVISIONAL TARGET | A predeclared pass/fail/PENDING rule controlling whether a candidate or claim may proceed to the next research stage. A score cannot override a failed hard gate. |

## 3. Status values for screening evidence

For hard gates and evidence checks use only:

- **PASS** — sufficient evidence currently supports the requirement;
- **FAIL** — evidence shows the requirement is not satisfied;
- **PENDING** — evidence is incomplete or not yet verified.

`PENDING` is not a soft pass. A candidate with a PENDING hard gate cannot enter the final shortlist until that gate is resolved.

## 4. Minimum claim test

Before committing a sentence that sounds factual, ask:

1. Is it external and verifiable? If yes, cite a primary/official source.
2. Does the source support this exact wording rather than merely a related topic?
3. Is the statement from the paper, from released code, or from our reasoning? Label the correct layer.
4. Is the claim conditional on hardware, precision, dataset split, evaluator, input resolution, repository version, or licence? State the condition.
5. Is it actually a local choice, target, gate, hypothesis, or unresolved question? Use the corresponding non-factual label.

## 5. Screening-specific anti-inflation rules

- Paper wording must not be promoted into a stronger claim than the authors make.
- A code path is not evidence that a failure occurs frequently; it only establishes what the implementation does.
- A benchmark weakness is not a causal explanation until an experiment isolates the mechanism.
- Official repository availability is not equivalent to successful local reproduction.
- Desktop/Orin/CPU/NPU speed is not evidence of Jetson Nano speed.
- ArXiv-only or older work may be ineligible as the main baseline while still being mandatory novelty evidence.
- A candidate score is a project ranking aid, not scientific evidence that the candidate is superior.
