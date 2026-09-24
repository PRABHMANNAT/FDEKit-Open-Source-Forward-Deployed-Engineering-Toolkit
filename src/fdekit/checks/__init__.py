"""Independent static checks with stable IDs."""

from fdekit.models import Category, Check, Status


def finding(
    identifier: str,
    name: str,
    category: Category,
    passed: bool,
    deduction: int,
    description: str,
    recommendation: str,
    evidence: list[str] | None = None,
    *,
    critical: bool = False,
    skipped: bool = False,
) -> Check:
    status = (
        Status.SKIPPED
        if skipped
        else Status.PASS
        if passed
        else Status.FAIL
        if critical
        else Status.WARNING
    )
    return Check(
        id=identifier,
        name=name,
        category=category,
        status=status,
        severity="none" if passed or skipped else "high" if critical else "medium",
        description=description,
        evidence=evidence or [],
        recommendation=recommendation,
        score_impact=0 if passed or skipped else deduction,
    )
