# Scoring model v1

The initial score is 100. Subtract every reported score_impact, then clamp at zero.
No weighting, randomness, timestamps, remote state or LLM is involved. The same file
contents, configuration, Git state and tool version produce identical report content.

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
