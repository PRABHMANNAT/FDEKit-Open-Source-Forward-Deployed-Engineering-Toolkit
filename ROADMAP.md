# Roadmap

Milestones describe direction, not delivery promises. Prioritize real deployment problems
and evidence from users over feature count.

| Version | Outcome | Exit criteria |
| --- | --- | --- |
| v0.1 | Core scanner and report engine | Offline CLI, documented scoring, redaction tests, package build |
| v0.2 | Broader frameworks and providers | Fixture-backed detection, monorepo scope, fewer false positives |
| v0.3 | Opt-in integration diagnostics | Explicit target allowlists, timeouts, safe authentication handling |
| v0.4 | Observability readiness | Structured logging, metrics and tracing evidence |
| v0.5 | GitHub Action | Versioned distribution, annotations and configurable thresholds |
| v0.6 | Plugin architecture | Versioned check contracts, isolation policy, compatibility tests |
| v1.0 | Stable extensible readiness framework | Stable schema and CLI, migration policy, cross-platform support |

v0.1 remains a static heuristic tool. Connectivity checks and AI assistance are not
implemented. Optional future AI explanations must never determine the score or be required
for scanning. See docs/BACKLOG.md for independent proposals.
