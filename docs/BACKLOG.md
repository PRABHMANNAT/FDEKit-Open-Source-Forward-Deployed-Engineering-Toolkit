# Proposed issue backlog

These are independent work proposals, not automatically opened GitHub issues.
Open a focused issue when someone is ready to discuss or implement one.

| # | Proposed issue | Acceptance criteria | Suggested labels |
| --- | --- | --- | --- |
| 1 | Poetry dependency-table framework detection | Detect declared frameworks in Poetry fixtures without text false positives | scanner, enhancement |
| 2 | Python optional dependency groups | Cover PEP 621 optional groups and dependency-groups with fixtures | scanner, testing |
| 3 | Monorepo project boundaries | Find workspace members and produce separate scoped reports | scanner, enhancement |
| 4 | Lockfile freshness checks | Compare root direct declarations with supported lock metadata; explain uncertainty | scanner |
| 5 | Dockerfile readiness checks | Detect non-root USER and HEALTHCHECK with parser-backed fixtures | scanner, security |
| 6 | Compose environment contracts | Identify required variables and document default-value semantics | scanner, integration |
| 7 | Structured GitHub workflow checks | Parse jobs/steps, distinguish disabled tests and reusable workflows | scanner, testing |
| 8 | AST-backed Python environment references | Cover aliases and multiline expressions with fewer false positives | scanner |
| 9 | JavaScript bracket environment access | Detect literal process.env and import.meta.env bracket keys | scanner, good first issue |
| 10 | Configurable application profiles | Library/service/CLI profiles with versioned scoring and explicit applicability | enhancement |
| 11 | Expiring check exemptions | Require reasons and expiry, include exemptions in reports | enhancement, security |
| 12 | SARIF export | Map stable IDs, severity and source locations; validate against schema | integration |
| 13 | Report comparison | Explain score/findings added or removed across two JSON reports | enhancement |
| 14 | Opt-in HTTP diagnostics | Allowlist targets, enforce timeouts, never echo auth headers or bodies | integration, security |
| 15 | Observability configuration hints | Fixture-backed logging, metrics and tracing configuration evidence | scanner |
| 16 | Shell completion documentation | Verify and document Typer completions for supported shells | documentation, good first issue |
| 17 | Scan performance budgets | Reproducible generated-tree benchmarks with memory and time measurements | testing |
| 18 | Stable report JSON Schema | Export schema with compatibility tests and documented consumer guidance | integration, testing |
| 19 | Versioned GitHub Action | Install pinned package, emit annotations and preserve offline scan semantics | integration |
| 20 | Plugin isolation design | Specify check permissions, compatibility and failure boundaries before implementation | enhancement |
