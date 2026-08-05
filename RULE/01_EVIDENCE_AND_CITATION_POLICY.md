# RULE 01 — Evidence and Citation Policy

**Effective date:** 2026-08-05
**Scope:** This public research dossier and all work derived from it.

> This is a clone-readable snapshot of the workspace rule at `E:\Robot_Backup\RULE\01_EVIDENCE_AND_CITATION_POLICY.md`. In the original workspace, the external `RULE` folder is the source of truth and must be read before research or publishing work.

## Mandatory session gate

Before making a research claim, changing a research document, selecting a method, or publishing material, read every current file in the applicable `RULE` folder. If a required rule is unavailable, state that limitation; do not infer it.

## Evidence requirements

1. Do not invent facts, measurements, benchmark rankings, hardware compatibility, dataset licences, publication status, or research gaps.
2. Every externally verifiable factual claim needs an inline citation to a traceable source. Prefer the original paper, official proceedings, dataset card/repository, standards body, manufacturer documentation, or official benchmark toolkit.
3. A reference must give authors or organisation, title, venue/publisher, year, DOI or stable URL, and an access date for a web resource.
4. A blog, search-result snippet, generated summary, or uncited comparison table cannot be the sole evidence for a scientific claim.
5. Recheck volatile facts (release status, data access/licence, repository state, hardware/software support, leaderboards, and prices) immediately before publishing them.

## Claim labels

- **FACT — cited:** directly supported by the cited source.
- **INTERPRETATION — reasoned:** a transparent inference from cited facts.
- **PROJECT DECISION — provisional:** a chosen scope or design, not a result.
- **HYPOTHESIS — untested:** falsifiable proposition, not a result.
- **PROVISIONAL TARGET:** internal gate, not claimed to come from the literature.
- **OPEN QUESTION:** unresolved; no implied answer.

## Comparison and deployment discipline

1. Compare accuracy only under compatible datasets, splits, protocols, metrics, inputs, and configurations.
2. Compare speed, latency, memory, energy, and thermal behaviour only under compatible hardware and measurement procedures.
3. Do not infer Jetson Nano feasibility or FPS from desktop GPUs, Jetson Orin/AGX/TX2, phones, or other devices. Measure on the target device before making a deployment claim.
4. Keep tracker-only, detector-assisted system, and robot-control measurements separate unless a declared protocol evaluates the complete system.
