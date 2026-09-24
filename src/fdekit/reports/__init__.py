"""Render the same versioned evidence as JSON, Markdown or terminal text."""

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from fdekit.models import Report
from fdekit.utils.files import linked


def as_json(report: Report) -> str:
    return json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=True) + "\n"


def escape(text: str) -> str:
    for char in ("\\", "`", "*", "_", "[", "]", "<", ">", "|", "#"):
        text = text.replace(char, "\\" + char)
    return text.replace("\n", " ").replace("\r", " ")


def as_markdown(report: Report) -> str:
    lines = [
        "# FDEKit Deployment Readiness",
        "",
        f"Project: {escape(report.project)}",
        "",
        f"**Readiness score: {report.score}/100**",
        "",
        "Stack: "
        + escape(" + ".join(report.stack.frameworks + report.stack.languages) or "Unknown"),
        "",
        "Package managers: " + escape(", ".join(report.stack.package_managers) or "Not detected"),
        "",
        "## Findings",
        "",
    ]
    for check in report.checks:
        lines += [
            f"### {check.status.value}: {escape(check.name)}",
            "",
            f"ID: `{check.id}` | Category: {check.category.value} | "
            f"Severity: {check.severity} | Deduction: {check.score_impact}",
            "",
            escape(check.description),
            "",
        ]
        lines += [f"- {escape(item)}" for item in check.evidence]
        if check.evidence:
            lines.append("")
        lines += ["Recommendation: " + escape(check.recommendation), ""]
    lines += ["## Scoring", "", escape(report.scoring_model), "", "## Limits and privacy", ""]
    lines += [f"- {escape(item)}" for item in report.limitations]
    return "\n".join(lines) + "\n"


def terminal(report: Report, console: Console) -> None:
    console.print("FDEKit Deployment Readiness", style="bold cyan")
    console.print(f"Project: {report.project}", markup=False)
    console.print(
        "Stack: " + (" + ".join(report.stack.frameworks + report.stack.languages) or "Unknown"),
        markup=False,
    )
    console.print(
        "Package managers: " + (", ".join(report.stack.package_managers) or "Not detected"),
        markup=False,
    )
    console.print("Docker: " + (", ".join(report.stack.docker) or "Not detected"), markup=False)
    console.print("CI: " + (", ".join(report.stack.ci) or "Not detected"), markup=False)
    console.print(f"Readiness Score: {report.score}/100", style="bold")
    table = Table("Status", "Check", "Deduction")
    for check in report.checks:
        table.add_row(check.status.value, check.name, str(check.score_impact))
    console.print(table)
    for check in report.checks:
        if check.status.value in {"FAIL", "WARNING"}:
            console.print(f"{check.status.value}: {check.name}", markup=False, style="yellow")
            for evidence in check.evidence:
                console.print(f"  {evidence}", markup=False)
            console.print(f"  {check.recommendation}", markup=False)
    console.print("Static evidence only. See report limitations before deployment.", style="dim")


def write(report: Report, root: Path) -> tuple[Path, Path]:
    directory = root / ".fdekit"
    if directory.exists() or directory.is_symlink():
        if linked(directory) or not directory.is_dir():
            raise ValueError("Report directory must be a regular directory, not a link")
    directory.mkdir(exist_ok=True)
    targets = (directory / "report.md", directory / "report.json")
    for path in targets:
        if path.exists() or path.is_symlink():
            if linked(path) or not path.is_file() or path.stat().st_nlink > 1:
                raise ValueError("Report targets must be regular files without links")
    for path, content in zip(targets, (as_markdown(report), as_json(report)), strict=True):
        # Replace a sibling temporary file so interrupted writes do not truncate reports.
        import os
        import tempfile

        fd, name = tempfile.mkstemp(prefix=".report-", dir=directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
            os.replace(name, path)
        finally:
            Path(name).unlink(missing_ok=True)
    return targets
