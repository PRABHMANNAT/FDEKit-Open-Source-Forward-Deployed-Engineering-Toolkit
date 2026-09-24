import platform
import shutil
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from fdekit import __version__
from fdekit.models import Report, Status
from fdekit.reports import as_json, as_markdown, terminal, write
from fdekit.scanners.engine import scan as scan_project
from fdekit.utils.files import DEFAULT_CONFIG, load_config

app = typer.Typer(
    no_args_is_help=True,
    help=(
        "FDEKit: local-first deployment-readiness evidence. "
        "Inspect files without running project code, calling APIs or uploading source."
    ),
)
console = Console()
errors = Console(stderr=True)


class Format(StrEnum):
    terminal = "terminal"
    json = "json"
    markdown = "markdown"


def version(value: bool) -> None:
    if value:
        typer.echo(f"fdekit {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version_flag: Annotated[
        bool,
        typer.Option(
            "--version", callback=version, is_eager=True, help="Show the installed FDEKit version."
        ),
    ] = False,
) -> None:
    pass


def inspect(path: Path) -> Report:
    try:
        return scan_project(path)
    except (OSError, ValueError):
        errors.print("Cannot scan: check the directory, permissions and fdekit.yaml configuration.")
        raise typer.Exit(2) from None


def render(report: Report, format: Format) -> None:
    if format == Format.json:
        typer.echo(as_json(report), nl=False)
    elif format == Format.markdown:
        typer.echo(as_markdown(report), nl=False)
    else:
        terminal(report, console)


@app.command()
def init(path: Annotated[Path, typer.Argument(help="Project directory.")] = Path(".")) -> None:
    """Create fdekit.yaml with safe defaults. Never overwrite an existing configuration."""
    target = path / "fdekit.yaml"
    try:
        with target.open("x", encoding="utf-8") as stream:
            stream.write(DEFAULT_CONFIG)
    except FileExistsError:
        errors.print("fdekit.yaml already exists; no changes made.")
        raise typer.Exit(2) from None
    except OSError:
        errors.print("Cannot create fdekit.yaml; check the directory and write permissions.")
        raise typer.Exit(2) from None
    typer.echo("Created fdekit.yaml")


@app.command()
def doctor() -> None:
    """Check Python, CLI dependencies and optional Git availability without network access."""
    typer.echo(f"FDEKit {__version__}: ready")
    typer.echo(f"Python {platform.python_version()}: supported (requires 3.11+)")
    typer.echo("CLI dependencies: available")
    typer.echo(
        "Git: available"
        if shutil.which("git")
        else "Git: unavailable; repository checks will be limited"
    )
    typer.echo("Network: not required; source uploads: disabled")


@app.command()
def scan(
    path: Annotated[Path, typer.Argument(help="Repository or project directory.")] = Path("."),
    format: Annotated[
        Format, typer.Option(help="Output format; JSON contains no terminal styling.")
    ] = Format.terminal,
) -> None:
    """Inspect a project offline. Print evidence; use report to save files. Findings exit 0."""
    render(inspect(path), format)


@app.command()
def report(path: Annotated[Path, typer.Argument(help="Project directory.")] = Path(".")) -> None:
    """Write .fdekit/report.md and report.json under PATH, replacing previous reports."""
    result = inspect(path)
    try:
        write(result, path.resolve())
    except (OSError, ValueError):
        errors.print("Cannot write reports: check permissions and remove linked report paths.")
        raise typer.Exit(2) from None
    typer.echo("Reports written: .fdekit/report.md and .fdekit/report.json (under scan path)")


@app.command()
def check(
    path: Annotated[Path, typer.Argument(help="Project directory.")] = Path("."),
    min_score: Annotated[
        int | None,
        typer.Option(min=0, max=100, help="Override min_score from fdekit.yaml (default 70)."),
    ] = None,
    format: Annotated[Format, typer.Option(help="Output format.")] = Format.terminal,
) -> None:
    """CI gate: exit 1 for FAIL findings or score below threshold; exit 2 for input errors."""
    result = inspect(path)
    if min_score is None:
        try:
            min_score = load_config(path.resolve()).min_score
        except (OSError, ValueError):
            errors.print("Cannot reload fdekit.yaml.")
            raise typer.Exit(2) from None
    render(result, format)
    if result.score < min_score or any(c.status == Status.FAIL for c in result.checks):
        raise typer.Exit(1)
