# FDEKit Deployment Readiness

Project: fastapi-service

**Readiness score: 74/100**

Stack: FastAPI + Python

Package managers: pip

## Findings

### PASS: Recognized project stack

ID: `project.stack` | Category: dependencies | Severity: none | Deduction: 0

Language and manifest indicators only.

- Python

Recommendation: Add a supported project manifest or inspect the stack manually.

### PASS: Manifest syntax

ID: `dependencies.manifests` | Category: dependencies | Severity: none | Deduction: 0

Parse supported root manifests without executing code.

Recommendation: Repair invalid manifests.

### PASS: Runtime versions pinned

ID: `runtime.pinned` | Category: runtime | Severity: none | Deduction: 0

Exact x.y.z versions in .python-version, .nvmrc or .node-version.

- Python pin

Recommendation: Pin each detected runtime to a tested patch version.

### WARNING: Dependency reproducibility indicators

ID: `dependencies.locked` | Category: dependencies | Severity: medium | Deduction: 8

Lockfile presence or simple exact requirements; integrity not verified.

Recommendation: Commit a lockfile and verify a clean reproducible install.

### WARNING: Test indicators

ID: `testing.present` | Category: testing | Severity: medium | Deduction: 10

Test command, files or pytest configuration detected; tests are not executed.

Recommendation: Add meaningful automated tests and run them in CI.

### WARNING: CI configuration

ID: `ci.present` | Category: ci | Severity: medium | Deduction: 8

Known CI configuration files exist; workflow results are not checked.

Recommendation: Add CI that tests and builds the project.

### PASS: Deployment configuration

ID: `deployment.config` | Category: deployment | Severity: none | Deduction: 0

Deployment file indicators at the project root.

- Dockerfile

Recommendation: Document deployment and add appropriate provider or container configuration.

### PASS: Docker indicators

ID: `deployment.docker` | Category: deployment | Severity: none | Deduction: 0

Docker is optional; no score deduction when absent.

- Dockerfile

Recommendation: Consider containers if required by your target environment.

### PASS: Health-check indicator

ID: `observability.health` | Category: observability | Severity: none | Deduction: 0

Text heuristic only; no endpoint is called.

Recommendation: For services, implement and verify a health endpoint; libraries may omit it.

### PASS: Environment variable documentation

ID: `configuration.env` | Category: configuration | Severity: none | Deduction: 0

Compare static references and required\_env with example keys.

Recommendation: Document required variables using safe placeholders in .env.example.

### PASS: Integration configuration contract

ID: `integration.configuration` | Category: integration | Severity: none | Deduction: 0

Only configuration names are checked; credentials and connectivity are unverified.

- SERVICE\_API\_KEY

Recommendation: Validate auth, timeouts, retries and connectivity in the target environment.

### PASS: Credential-risk patterns

ID: `security.secrets` | Category: security | Severity: none | Deduction: 0

Heuristics over selected working-tree files; no history scan or security guarantee.

Recommendation: Review locally. Rotate exposed credentials and remove them from tracked content.

### PASS: Environment files tracked by Git

ID: `security.tracked-env` | Category: security | Severity: none | Deduction: 0

Inspect the current Git index, including ignored tracked files.

Recommendation: Untrack private environment files and rotate any exposed credentials.

### PASS: Private environment ignore rule

ID: `security.gitignore` | Category: security | Severity: none | Deduction: 0

Check whether the root .env path is ignored; other filenames need review.

Recommendation: Ignore .env and private variants; explicitly allow sanitized examples.

### PASS: Debug configuration risk

ID: `security.debug` | Category: security | Severity: none | Deduction: 0

Detect literal DEBUG=true or FLASK\_DEBUG=1 assignments.

Recommendation: Disable debug mode in production configuration.

### PASS: Git worktree

ID: `repository.git` | Category: repository | Severity: none | Deduction: 0

Read-only local Git inspection; remote access is not tested.

Recommendation: Initialize Git or run from a checked-out repository.

### PASS: Commit history exists

ID: `repository.commit` | Category: repository | Severity: none | Deduction: 0

A local HEAD commit exists; commit content and history are not audited.

Recommendation: Commit a reviewed baseline before deployment.

### PASS: Working tree state

ID: `repository.clean` | Category: repository | Severity: none | Deduction: 0

Uncommitted changes can affect reproducibility.

Recommendation: Review and commit intended deployment changes.

### PASS: Inspection completeness

ID: `scan.complete` | Category: configuration | Severity: none | Deduction: 0

Report file limits and filesystem access failures.

Recommendation: Review skipped paths or adjust limits and rescan.

## Scoring

v1: max(0, 100 - sum(score\_impact)); see docs/SCORING.md

## Limits and privacy

- Static heuristics only; presence does not prove correct or working configuration.
- No network calls, dependency installation, project execution, or Git history scan.
- No security guarantee. Exclusions and read limits can hide risks.
