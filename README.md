# FDEKit

**Diagnose customer environments, inspect integration configuration, and generate deployment-readiness evidence before shipping AI/software systems.**

FDEKit is a local-first Python CLI for Forward Deployed Engineers, Solutions Engineers,
AI engineers and deployment teams. Run it against a checkout to find missing runtime pins,
undocumented environment variables, risky credentials, and missing deployment evidence.
It works offline, requires no API key, and uploads no source code.

## Why FDEKit

Deployment handoffs often depend on scattered assumptions: which runtime is needed,
which variables must be set, whether tests exist, and how the application is deployed.
FDEKit turns those assumptions into a repeatable checklist with evidence, recommendations
and a deterministic score. It does not execute your application or certify its security.

## Installation

Python 3.11+ is required; Git is optional for scanning and required for repository checks.
This initial version is installed from source; no PyPI release is claimed.

```sh
git clone https://github.com/PRABHMANNAT/FDEKit-Open-Source-Forward-Deployed-Engineering-Toolkit.git
cd FDEKit-Open-Source-Forward-Deployed-Engineering-Toolkit
python -m venv .venv
```

Activate with `source .venv/bin/activate` on macOS/Linux, or
`.venv\Scripts\Activate.ps1` in Windows PowerShell. Then:

```sh
python -m pip install -e .
fdekit --help
fdekit doctor
```

FDEKit also provides shell completion for commands and options. See the
[shell completion guide](docs/SHELL_COMPLETION.md) for temporary activation, persistent
installation, removal, and verified shell-specific behavior.

## Quick start and demo

```sh
fdekit init /path/to/customer-project
fdekit scan /path/to/customer-project
fdekit scan /path/to/customer-project --format json
fdekit scan /path/to/customer-project --format markdown
fdekit report /path/to/customer-project
fdekit check /path/to/customer-project --min-score 70
```

Or run a bundled, sanitized example:

```sh
fdekit scan examples/fastapi-service
fdekit report examples/fastapi-service
```

Abbreviated illustrative output (the actual score depends on Git state and detected files):

```text
FDEKit Deployment Readiness
Project: fastapi-service
Stack: FastAPI + Python
Readiness Score: 74/100
PASS: Runtime versions pinned
PASS: Environment variable documentation
WARNING: Dependency reproducibility indicators
  Commit a lockfile and verify a clean reproducible install.
WARNING: Test indicators
  Add meaningful automated tests and run them in CI.
WARNING: CI configuration
  Add CI that tests and builds the project.
```

Read the [generated example Markdown report](docs/SAMPLE_REPORT.md) or
[JSON evidence](docs/SAMPLE_REPORT.json).

`scan` prints evidence without writing files. `report` writes `.fdekit/report.md` and
`.fdekit/report.json` under the scanned directory. `init` refuses to overwrite configuration.
`check` exits 1 for any FAIL finding or a score below the threshold. Input/output errors
exit 2; a completed `scan` exits 0 even when it finds risks.

## Features

- Stack, language, framework, package-manager and runtime indicators.
- Docker, CI and deployment configuration detection.
- Static environment reference checks against sanitized environment examples.
- Credential-risk heuristics with values redacted; tracked `.env` and debug checks.
- Git working tree and commit checks, dependency lock and test indicators.
- Static integration configuration and service health-check hints.
- Terminal, versioned JSON and Markdown evidence with per-check recommendations.
- Explainable scoring and a CI-friendly gate; bounded file inspection and exclusions.

## How it works

FDEKit inventories bounded UTF-8 files, parses root manifests, runs independent checks,
then sums documented deductions. It invokes only read-only local Git commands. It never
installs project dependencies, runs scripts, calls integration endpoints or uses an LLM.
Presence checks describe evidence, not successful tests or working deployments.

## Supported stacks

| Area | Initial indicators |
| --- | --- |
| Python | `pyproject.toml`, `requirements.txt`, `Pipfile`, `.py` |
| JavaScript / TypeScript | `package.json`, `.js`, `.ts`, `.tsx`, `tsconfig.json` |
| Frameworks | Next.js, React, Vite, Express, FastAPI, Flask, Django |
| Packages | npm, pnpm, Yarn, pip, uv, Poetry, Pipenv |
| Containers | Dockerfile, Compose YAML files |
| CI | GitHub Actions, GitLab CI, CircleCI, Jenkins |
| Deployment | Vercel, Netlify, Render, Procfile, Docker |

Root manifests are inspected as one project. Full monorepo aggregation, dependency
resolution, Docker validation and connectivity checks are future work. Framework
detection is heuristic; dynamic declarations may not be recognized.

## Scoring model

`score = max(0, 100 - sum(check.score_impact))`. Every finding reports its deduction;
PASS and SKIPPED findings deduct zero. Some advisory checks have no deduction.
The score is deterministic for the same files, configuration, Git state and tool version.
It is a checklist score, not a probability of deployment success. A score of 100 is not
a security guarantee. See [the complete scoring table](docs/SCORING.md).

## Configuration and privacy

Run `fdekit init` and edit `fdekit.yaml`; see [fdekit.example.yaml](fdekit.example.yaml).
Defaults exclude fixtures, examples, dependency folders, build outputs and reports.
Files larger than 256 KiB are skipped; the inventory stops after 10,000 eligible files or a 16 MiB aggregate read budget.
Links and Windows junctions are not followed. Skipped access/size limits generate a
completeness warning. Binary and non-UTF-8 files are not inspected.

The FDEKit repository itself excludes its tests because they contain synthetic secret patterns.
Secret-risk checks inspect selected source/config files in the working tree, not Git history.
Matched values are fully redacted. Heuristics can miss credentials or flag safe examples.
Reports contain filenames, variable names and project metadata: review before sharing.
Scan a stable, trusted checkout; this CLI is not a sandbox for a concurrently modified
hostile filesystem. No telemetry, source uploads or API keys are used.

## Architecture

```text
src/fdekit/
  cli/        commands and exit codes
  scanners/   inventory orchestration and stack detection
  checks/     independent evidence producers with stable IDs
  models/     validated config and versioned report schema
  scoring/    deterministic deduction calculation
  reports/    terminal, JSON and Markdown output
  utils/      bounded filesystem and read-only Git helpers
```

See [architecture](docs/ARCHITECTURE.md) and [adding a check](docs/ADDING_CHECKS.md).
The core has no AI dependency. A future optional assistant can consume reports without
changing how checks or scores are calculated.

## Development

```sh
python -m pip install -e '.[dev]'
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m build
```

Tests use local fixtures and make no network requests. Installing development dependencies
and isolated build dependencies may require network access.

## Roadmap and contributing

Start with [ROADMAP.md](ROADMAP.md) and the independently actionable
[proposed backlog](docs/BACKLOG.md). These are proposals, not manufactured GitHub issues.
Read [CONTRIBUTING.md](CONTRIBUTING.md) to fork, develop and submit a real change.
We welcome reproducible detector failures, framework fixtures and clearer documentation.
Community participation follows [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Security

Do not paste real credentials into public issues or reports. Read [SECURITY.md](SECURITY.md)
for reporting guidance and scanner limitations.

## License

MIT. See [LICENSE](LICENSE).
