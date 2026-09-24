import json

import pytest
from typer.testing import CliRunner

from fdekit.cli.app import app
from fdekit.reports import as_markdown, write
from fdekit.scanners.engine import scan

runner = CliRunner()


@pytest.mark.parametrize(
    "args,expected",
    [
        (["--help"], "local-first"),
        (["--version"], "0.1.0"),
        (["doctor"], "ready"),
        (["scan", "--help"], "format"),
    ],
)
def test_help_and_doctor(args, expected):
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    assert expected in result.output


def test_init_refuses_overwrite(tmp_path):
    assert runner.invoke(app, ["init", str(tmp_path)]).exit_code == 0
    content = (tmp_path / "fdekit.yaml").read_bytes()
    assert runner.invoke(app, ["init", str(tmp_path)]).exit_code == 2
    assert (tmp_path / "fdekit.yaml").read_bytes() == content
    assert runner.invoke(app, ["init", str(tmp_path / "missing")]).exit_code == 2


@pytest.mark.parametrize("format", ["terminal", "json", "markdown"])
def test_scan_formats(fixture_repo, format):
    root = fixture_repo("unhealthy-python")
    result = runner.invoke(app, ["scan", str(root), "--format", format])
    assert result.exit_code == 0, result.output
    if format == "json":
        assert json.loads(result.stdout)["schema_version"] == "1.0"
    else:
        assert "FDEKit Deployment Readiness" in result.stdout
    assert not (root / ".fdekit").exists()


def test_report_roundtrip(fixture_repo):
    root = fixture_repo("healthy-python")
    before = scan(root)
    result = runner.invoke(app, ["report", str(root)])
    assert result.exit_code == 0, result.output
    assert json.loads((root / ".fdekit/report.json").read_text()) == before.model_dump(mode="json")
    assert (root / ".fdekit/report.md").read_text(encoding="utf-8") == as_markdown(before)
    assert scan(root) == before
    assert runner.invoke(app, ["report", str(root)]).exit_code == 0


def test_check_threshold_and_critical(tmp_path):
    assert runner.invoke(app, ["check", str(tmp_path), "--min-score", "100"]).exit_code == 1
    assert runner.invoke(app, ["check", str(tmp_path), "--min-score", "0"]).exit_code == 0
    (tmp_path / "fdekit.yaml").write_text("min_score: 100")
    assert runner.invoke(app, ["check", str(tmp_path)]).exit_code == 1
    (tmp_path / "config.json").write_text('{"PASSWORD":"' + "a" * 20 + '"}')
    result = runner.invoke(app, ["check", str(tmp_path), "--min-score", "0", "--format", "json"])
    assert result.exit_code == 1
    assert json.loads(result.stdout)["score"] >= 0


def test_errors_are_clean(tmp_path):
    result = runner.invoke(app, ["scan", str(tmp_path / "missing"), "--format", "json"])
    assert result.exit_code == 2
    assert result.stdout == ""
    (tmp_path / "fdekit.yaml").write_text("[SECRET-PARSER-INPUT")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 2
    assert "SECRET-PARSER-INPUT" not in result.output
    assert "Traceback" not in result.output


def test_markdown_escapes_project_name(tmp_path):
    result = scan(tmp_path)
    result.project = "<script>[click](https://invalid)\n# heading"
    rendered = as_markdown(result)
    assert "<script>" not in rendered
    assert "\n# heading" not in rendered


def test_report_blocked_file(tmp_path):
    (tmp_path / ".fdekit").write_text("do not overwrite")
    assert runner.invoke(app, ["report", str(tmp_path)]).exit_code == 2
    assert (tmp_path / ".fdekit").read_text() == "do not overwrite"


def test_report_rejects_directory_target(tmp_path):
    (tmp_path / ".fdekit/report.md").mkdir(parents=True)
    with pytest.raises(ValueError):
        write(scan(tmp_path), tmp_path)


def test_report_rejects_hardlink(tmp_path):
    target = tmp_path / "outside.md"
    target.write_text("original")
    (tmp_path / ".fdekit").mkdir()
    try:
        (tmp_path / ".fdekit/report.md").hardlink_to(target)
    except OSError:
        pytest.skip("Hardlinks unavailable")
    with pytest.raises(ValueError):
        write(scan(tmp_path), tmp_path)
    assert target.read_text() == "original"


def test_doctor_without_git(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: None)
    assert "unavailable" in runner.invoke(app, ["doctor"]).output
