# Contributing evidence

Before making a change:

1. Read [RULE/01_EVIDENCE_AND_CITATION_POLICY.md](RULE/01_EVIDENCE_AND_CITATION_POLICY.md).
2. Read the existing claim label and preserve its status unless the change itself is a documented decision.
3. Add a primary/official source to `references/references.md` and `references/source_manifest.csv` before adding a new externally verifiable fact.
4. State the source’s scope and limit next to the claim. A paper about another device or task does not prove a claim for Jetson Nano or box-SOT.
5. Do not commit benchmark media, datasets, user videos, checkpoints, access tokens, or material without verified redistribution rights.

## Pull-request checklist

- [ ] New facts have an inline `[R#]` citation.
- [ ] The exact source is in both the bibliography and source manifest.
- [ ] Project choices/hypotheses are labelled instead of phrased as published facts.
- [ ] Cross-device speed or deployment claims are not inferred.
- [ ] The change does not quietly alter SOT into detection-assisted tracking, MOT, VOS, multimodal tracking, or active control.
