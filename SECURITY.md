# Security policy

## Scope and supported versions

Security fixes currently target the latest 0.1.x development code on main. There is no
long-term support guarantee. Do not rely on FDEKit as a secret-scanning or vulnerability
management system.

FDEKit inspects a bounded snapshot of a working tree. It does not scan Git history,
resolve dependencies, verify signatures, execute tests, validate credentials or call
endpoints. Filename exclusions, encodings, size limits and dynamic configuration can
hide risks. False positives and false negatives are expected. A PASS means only that
a particular static heuristic did not find a problem.

## Reporting a vulnerability

Use **Security → Advisories → Report a vulnerability** on the repository if private
vulnerability reporting is enabled. Otherwise use a private contact explicitly published
on the owner's GitHub profile. If neither is available, ask for a private reporting
channel without disclosing the vulnerability publicly.

Include the affected version, expected and observed behavior, and a minimal synthetic
reproduction. Never include live tokens, customer repositories, personal data or exploit
details in a public issue. Maintainers will coordinate disclosure when a fix is available;
no response-time commitment is implied.

## Handling findings

Review potential secret findings locally. If a credential was exposed, revoke or rotate
it through its provider and remove it from tracked files and, where necessary, history.
FDEKit never edits, deletes, revokes or rotates credentials.

Matched values are fully redacted. Reports still contain file paths, variable names,
runtime metadata and project names; inspect them before sharing.

Run against a stable checkout you control. Symbolic links, junctions and special files are
skipped, but scanning is not designed to resist concurrent malicious filesystem changes.
Do not run with elevated privileges. Git inspection disables fsmonitor; no Git hooks or
project commands are intentionally run. CI uses read-only repository permissions.
