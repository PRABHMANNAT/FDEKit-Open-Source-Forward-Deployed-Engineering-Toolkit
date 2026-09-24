# Scoring model v1

The initial score is 100. Subtract every reported score_impact, then clamp at zero.
No weighting, randomness, timestamps, remote state or LLM is involved. The same file
contents, configuration, Git state and tool version produce identical report content.

## Interpreting a report

Treat the score as a deterministic prioritization signal for the checks FDEKit could
apply, not as a probability that deployment will succeed. Start with the individual
findings, their evidence, and their recommendations; use the number as a compact summary
after understanding those details.

A score of 100 means that the applicable scored checks produced no deductions in this
scan. It does not prove that the application is secure, correct, observable, or ready for
every target environment. FDEKit performs bounded static inspection: it does not execute
tests, resolve dependencies, inspect Git history, validate credentials, or call deployment
and integration endpoints.

Finding statuses have distinct meanings:

| Status | Interpretation |
| --- | --- |
| PASS | The check's documented static condition was observed. This is evidence for that condition only, not an end-to-end guarantee. |
| WARNING | A readiness gap or review item was found. A warning may deduct points; advisory warnings can have zero impact. |
| FAIL | A critical rule was triggered. `fdekit check` exits 1 for any FAIL even when the numerical score meets the configured threshold. |
| INFO | Context was reported without a deduction or pass/fail conclusion. |
| SKIPPED | The check did not apply or could not produce a conclusion. It deducts no points and must not be treated as verified. |

Evidence explains what FDEKit observed, such as a file, configuration key, or omitted
artifact. Recommendations describe the next review or remediation step. A finding can be
important even when its `score_impact` is zero, and several pieces of evidence within one
check still produce only that check's documented deduction.

Use a report in this order:

1. Confirm the `scan.complete` finding does not identify unreadable, linked, oversized,
   or truncated input.
2. Investigate every FAIL and decide whether the detected evidence is valid for the target
   environment.
3. Review WARNING findings and their recommendations, including zero-impact advisories.
4. Treat PASS findings as scoped evidence and separately validate runtime behavior,
   connectivity, security controls, and deployment procedures.
5. Compare scores only when the FDEKit version, configuration, project contents, and Git
   state are equivalent.

For example, a report scoring 86 with a FAIL still fails the `fdekit check` gate. A report
scoring 100 can still contain SKIPPED checks and cannot replace testing, security review,
or deployment validation.

| Check ID | Deduction when unmet | Applicability |
| --- | ---: | --- |
| project.stack | 8 | All projects |
| dependencies.manifests | 15 (FAIL) | Malformed supported root manifests |
| runtime.pinned | 5 | Detected Python/JS/TS; all relevant runtimes need exact pins |
| dependencies.locked | 8 | Detected Python/JS/TS; all need reproducibility indicators |
| testing.present | 10 | All projects |
| ci.present | 8 | All projects |
| deployment.config | 8 | All projects |
| deployment.docker | 0 | Advisory; skipped when absent |
| observability.health | 3 | Recognized frameworks only |
| configuration.env | 12 | Static variable references or required_env configured |
| integration.configuration | 0 | Integration-like variable names; no live validation |
| security.secrets | 25 (FAIL) | Selected source/config files |
| security.tracked-env | 20 (FAIL) | Git index available |
| security.gitignore | 5 | Root .env ignore rule |
| security.debug | 10 | Literal debug assignments |
| repository.git | 3 | All projects |
| repository.commit | 2 | Git worktrees |
| repository.clean | 2 | Git worktrees |
| scan.complete | 10 | Unreadable/linked/oversized paths or file-count/byte-budget truncation |

Each rule deducts once regardless of evidence count. PASS and SKIPPED deduct zero.
The two integration/environment findings can share evidence, but only environment
documentation deducts points. Security findings may overlap because exposure and
tracking are independent risks.

A runtime constraint such as >=3.11 is reported but is not an exact pin. Lockfile presence
does not prove freshness, transitive pinning or installability. Tests and CI are detected,
not executed. An unknown or incomplete project must be reviewed manually regardless of score.

`fdekit check` exits 1 if score < min_score (default 70) OR any check is FAIL.
Operational/configuration errors exit 2. Other completed commands exit 0.
Minimal libraries may legitimately lack deployment/health artifacts; interpret recommendations
in context. Check profiles and justified exemptions are proposed in the backlog.

Reports use schema_version 1.0 and include the scoring model identifier. Changes to
deductions require changelog notes, updated tests and this table.
