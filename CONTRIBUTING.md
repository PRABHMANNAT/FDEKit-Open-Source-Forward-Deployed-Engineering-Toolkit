# Contributing to FDEKit

Useful contributions include reproducible bugs, framework fixtures, new checks, tests,
and clearer explanations. No contribution should require customer source code or real secrets.

## Your first change

1. Open this repository on GitHub and click **Fork** to make your own copy.
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/FDEKit-Open-Source-Forward-Deployed-Engineering-Toolkit.git`.
3. Enter the directory and create a descriptive branch: `git switch -c fix/runtime-detection`.
4. Create a Python 3.11+ environment: `python -m venv .venv`. Activate it using the
   platform instructions in the README.
5. Install development dependencies: `python -m pip install -e '.[dev]'`.
6. Make one focused change and add a regression test when behavior changes.
7. Run `python -m pytest`, `python -m ruff check .`,
   `python -m ruff format --check .`, `python -m mypy`, and `python -m build`.
8. Inspect `git diff` and `git status`; never include credentials or generated reports.
9. Stage only intended paths and commit, for example:
   `git add src/fdekit/checks/runtime.py tests/test_runtime.py` (use your actual filenames),
   then `git commit -m "fix: recognize runtime version files"`.
10. Push with `git push -u origin fix/runtime-detection`. On your fork, click
    **Compare & pull request**. Explain the problem, change and tests; submit for review.

## Engineering expectations

- Keep the core offline and deterministic. Never execute scanned project code.
- Use stable check IDs, concrete evidence and actionable recommendations.
- Never return full credentials in exceptions, stdout, stderr or reports.
- Preserve report-schema compatibility or document a version change.
- Check absence is not proof of failure: label heuristics and uncertainty honestly.
- Update docs/SCORING.md for any scoring change and test the effect.
- Use synthetic fixtures and standard Python. Dependencies need a clear justification.
- Discuss large changes before implementation. See docs/BACKLOG.md for proposals.

Tests block Python socket connections and use temporary repositories. Symlink tests skip
on Windows when the host cannot create symlinks; Linux CI runs them. Fixture dependency
versions are detection samples, not deployment recommendations.

Maintainers review real contributions through feature branches and pull requests.
We do not create artificial issues, contributions or popularity metrics.
