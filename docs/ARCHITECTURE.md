# Architecture

The CLI loads validated fdekit.yaml configuration, inventories files, parses supported
root manifests, detects stack hints, executes independent checks, calculates deductions,
then renders one Report model. Pydantic validates configuration and report contracts.
Standard-library dataclasses hold the internal inventory. Typer/Rich handle CLI output;
PyYAML reads configuration without object construction.

Checks receive an inventory and produce Check objects. IDs are stable machine-facing
identifiers. Categories and statuses are enums. Every finding provides a description,
evidence, recommendation, severity and explicit score_impact. Renderers share the same
model so JSON, Markdown and terminal output cannot calculate different scores.

File traversal is sorted and prunes built-in/external exclusions before reading. The
scanner skips links, reparse points, binary and oversized files. Git commands use an
argument list, timeout, no shell, no optional locks and disabled fsmonitor. No project
code, package manager or network integration is executed.

Reports intentionally omit timestamps and absolute paths for reproducibility and privacy.
Report files are replaced individually through sibling temporary files; the pair is not
transactional if a write fails between them. Reports are excluded from future inventories.

Tests cover real temporary Git repositories, malformed manifests/configuration, synthetic
credential patterns, deterministic output, bounds, links and report protection. Git and
filesystem failure paths are exercised without requiring network access.

v0.1 treats the selected root as one project. Future monorepo and plugin work must preserve
clear scan boundaries. Optional AI can consume an exported report but must not alter
check results or core scoring.
