# Application candidates and decision

The table separates **social importance** from **fit to the current RGB SOT project**. A high-impact domain is not automatically a good dissertation scope when the available system cannot responsibly address its full task.

| Candidate | Evidence-backed premise | Fit to current RGB moving-camera SOT | Decision |
|---|---|---|---|
| Consent-based robot guidance/accompaniment in crowded public facilities | TPT-Bench targets robot-egocentric person tracking for personalized assistance/collaboration and tests crowd/occlusion/re-identification pressure [R1](../references/references.md#r1). | Direct fit: one known person, moving robot camera, identity confusion, disappearance/re-entry. | **[PROJECT DECISION] Current recommendation.** The downstream action/control remains future work. |
| Search-and-rescue / disaster triage | DARPA’s Triage Challenge asks robotic systems to find, assess, and provide care-support information for disaster victims; NIST evaluates emergency-response robot capabilities [R7](../references/references.md#r7), [R8](../references/references.md#r8). | Partial fit only. RGB SOT may help retain a visual lock after a victim is found, but it does not cover search, navigation, communication, medical assessment, fail-safe behaviour, or required sensing. | **[NOT SELECTED for current scope]** High-value domain, but unsafe to describe RGB tracking as a standalone solution. |
| Lone-worker safety | NIOSH identifies lone-worker safety as a topic requiring systematic attention and evaluation of technology effectiveness [R9](../references/references.md#r9). | Weak fit. A RGB tracker alone cannot provide a safety-rated incident-detection or emergency-response system. | **[NOT SELECTED for current scope]** May become a future multi-sensor safety study. |

## Decision statement

**[PROJECT DECISION — provisional]** Proceed with the first candidate as a *perception research framing*:

> **Identity-preserving target-person tracking for a consent-based robot guide/accompany scenario in crowded public facilities.**

This is not a claim that the scenario has been field-validated, is commercially viable, or is more socially urgent than search-and-rescue. It is the best current match between a real embodied tracking failure, public data, the stated SOT scope, and a later embedded demo.

## Conditions that would reopen the decision

- A partner, sensor suite, and safety protocol make SAR or worker-safety evaluation genuinely feasible.
- The downstream action requires masks, multiple targets, 3D localization, or active planning, changing the task beyond box-SOT.
- Access, licence, or protocol checks invalidate the intended benchmark stack.
