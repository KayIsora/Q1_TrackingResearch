# Stage 4A-E2 bounded reproduction validation

- Inventory gate: PASS — 100 unique canonical rows, all PENDING, completed before tracker output.
- Executed scope: exactly Deer, Crossing, Couple; one official-default and one deterministic process each.
- Run validation: six exit-code-0 runs; result and time files present; row counts 71/120/140.
- Source cleanup: original untracked local.py restored to SHA-256 `e76f5713bac3f31b3b587f4fe869aea25aeceeab5cb45b2800c46a76d7aff6fb`; tracked diff clean.
- Staging: F: exFAT rejected directory junctions with `Incorrect function`; authorized three-directory byte-copy fallback passed relative-file-set and every-file SHA-256 checks.
- Timing files remain external and are not used for a speed claim.
- Evidence recommendation: `E2_DATA_IDENTITY_NOT_CAUSE`.

| Sequence | Acquired default = deterministic | Acquired default = prior local | Data changed local prediction |
|---|---:|---:|---:|
| Deer | True | True | False |
| Crossing | True | True | False |
| Couple | True | True | False |

This recommendation is an E2 evidence label only. It is not DIAG_PASS/FAIL and does not authorize Stage 4B.
