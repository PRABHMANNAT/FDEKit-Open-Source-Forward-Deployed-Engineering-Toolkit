"""Deterministic scoring with explicit deductions."""

from fdekit.models import Check


def score(checks: list[Check]) -> int:
    return max(0, 100 - sum(check.score_impact for check in checks))
