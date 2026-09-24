# Adding a check

1. Choose a stable category-prefixed ID and a narrowly defined static signal.
2. Implement a function in src/fdekit/checks that consumes Inventory and returns Check values.
3. Explain exactly what the evidence proves and what it cannot establish.
4. Use the finding helper to keep statuses and deductions consistent. Use SKIPPED
   when the check does not apply, rather than claiming PASS.
5. Return filenames and safe summaries, never secret values or parser exception content.
6. Register the check in scanners/engine.py. Add synthetic healthy and unhealthy tests.
7. If the rule affects scoring, update docs/SCORING.md and test the deduction and score floor.
8. Update README support claims and CHANGELOG.md.

Checks must not execute project code, perform network calls, mutate scanned files, read
outside scan boundaries or silently bypass file limits. A future network diagnostic must
be explicitly opt-in and use a separate execution contract.
