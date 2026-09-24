import json
import subprocess

import pytest

from fdekit.models import Check, Report, Status
from fdekit.scanners.engine import scan
from fdekit.scoring import score


def by_id(report, identifier):
    return next(c for c in report.checks if c.id == identifier)


@pytest.mark.parametrize(
    "name,languages,frameworks,manager",
    [
        ("healthy-python", ["Python"], ["FastAPI"], "pip"),
        ("unhealthy-python", ["Python"], ["Flask"], "pip"),
        ("healthy-nextjs", ["JavaScript", "TypeScript"], ["Next.js", "React"], "npm"),
        ("minimal-project", [], [], None),
    ],
)
def test_fixture_detection(fixture_repo, name, languages, frameworks, manager):
    report = scan(fixture_repo(name))
    assert report.stack.languages == languages
    assert report.stack.frameworks == frameworks
    if manager:
        assert manager in report.stack.package_managers
    assert Report.model_validate_json(report.model_dump_json()) == report


def test_healthy_outscores_unhealthy(fixture_repo):
    healthy = scan(fixture_repo("healthy-python"))
    unhealthy = scan(fixture_repo("unhealthy-python"))
    assert healthy.score > unhealthy.score
    assert by_id(healthy, "configuration.env").status == Status.PASS
    assert by_id(unhealthy, "configuration.env").score_impact == 12
    assert by_id(unhealthy, "security.debug").status == Status.WARNING
    assert healthy.stack.docker == ["Dockerfile"]
    assert healthy.stack.ci == ["GitHub Actions"]
    assert healthy.stack.runtimes["Python pin"] == "3.11.9"


def test_deterministic_and_explainable(fixture_repo):
    root = fixture_repo("healthy-nextjs")
    first = scan(root)
    assert scan(root).model_dump_json() == first.model_dump_json()
    assert first.score == max(0, 100 - sum(c.score_impact for c in first.checks))
    assert len({c.id for c in first.checks}) == len(first.checks)
    assert all(
        c.score_impact == 0
        for c in first.checks
        if c.status in {Status.PASS, Status.SKIPPED, Status.INFO}
    )


def test_score_floor():
    check = Check(
        id="x",
        name="x",
        category="security",
        status="FAIL",
        severity="high",
        description="x",
        recommendation="x",
        score_impact=120,
    )
    assert score([check]) == 0
    assert score([]) == 100


@pytest.mark.parametrize(
    "filename,content",
    [
        ("package.json", "{broken"),
        ("package.json", "[]"),
        ("package.json", '{"scripts": []}'),
        ("package.json", '{"dependencies":{"next":12}}'),
        ("pyproject.toml", "broken = ["),
        ("pyproject.toml", "project = 'bad'"),
        ("pyproject.toml", "[project]\ndependencies = [42]"),
        ("Pipfile", "invalid = ["),
    ],
)
def test_bad_manifest_is_finding(tmp_path, filename, content):
    (tmp_path / filename).write_text(content)
    assert by_id(scan(tmp_path), "dependencies.manifests").status == Status.FAIL


@pytest.mark.parametrize("content", ["unknown: true", "max_files: 0", "min_score: bad", "[", "[]"])
def test_bad_config_is_error(tmp_path, content):
    (tmp_path / "fdekit.yaml").write_text(content)
    with pytest.raises(ValueError, match="Invalid fdekit.yaml"):
        scan(tmp_path)


def test_required_environment_and_exclusions(tmp_path):
    (tmp_path / "fdekit.yaml").write_text("required_env: [DATABASE_URL]\nexclude: [vendor]\n")
    (tmp_path / "vendor").mkdir()
    (tmp_path / "vendor" / "app.py").write_text('os.getenv("IGNORED_API_KEY")')
    result = scan(tmp_path)
    assert by_id(result, "configuration.env").evidence == ["Undocumented variable: DATABASE_URL"]
    assert by_id(result, "integration.configuration").status == Status.WARNING
    (tmp_path / ".env.example").write_text("DATABASE_URL=replace-me\n")
    assert by_id(scan(tmp_path), "configuration.env").status == Status.PASS


def test_git_tracks_ignored_environment_file(git_repo):
    (git_repo / ".gitignore").write_text(".env\n")
    (git_repo / ".env").write_text("EXAMPLE=placeholder\n")
    subprocess.run(["git", "-C", str(git_repo), "add", "-f", ".env", ".gitignore"], check=True)
    subprocess.run(
        ["git", "-C", str(git_repo), "commit", "-m", "fixture"], check=True, capture_output=True
    )
    report = scan(git_repo)
    assert by_id(report, "security.tracked-env").status == Status.FAIL
    assert by_id(report, "security.gitignore").status == Status.PASS
    assert by_id(report, "repository.clean").status == Status.PASS
    assert by_id(report, "repository.commit").status == Status.PASS


@pytest.mark.parametrize(
    "manifest,content,expected",
    [
        ("package.json", '{"dependencies":{"vite":"1","express":"1"}}', ["Vite", "Express"]),
        ("Pipfile", '[packages]\ndjango = "*"', ["Django"]),
        (
            "pyproject.toml",
            '[project]\ndependencies=["flask>=3", "django>=5"]',
            ["Flask", "Django"],
        ),
    ],
)
def test_more_frameworks(tmp_path, manifest, content, expected):
    (tmp_path / manifest).write_text(content)
    assert scan(tmp_path).stack.frameworks == expected


def test_other_providers(tmp_path):
    for name in (
        ".gitlab-ci.yml",
        "Jenkinsfile",
        "netlify.toml",
        "render.yaml",
        "Procfile",
        "pnpm-lock.yaml",
        "yarn.lock",
        "uv.lock",
        "poetry.lock",
        "compose.yml",
    ):
        (tmp_path / name).write_text("")
    stack = scan(tmp_path).stack
    assert stack.ci == ["GitLab CI", "Jenkins"]
    assert set(stack.package_managers) == {"pnpm", "yarn", "uv", "Poetry"}
    assert len(stack.deployment) == 4


def test_non_directory(tmp_path):
    path = tmp_path / "file"
    path.touch()
    with pytest.raises(ValueError):
        scan(path)
    with pytest.raises(OSError):
        scan(tmp_path / "missing")


def test_runtime_constraints_are_not_pins(tmp_path):
    (tmp_path / "package.json").write_text(json.dumps({"engines": {"node": ">=22"}}))
    (tmp_path / ".nvmrc").write_text("lts/*")
    assert by_id(scan(tmp_path), "runtime.pinned").status == Status.WARNING
    (tmp_path / ".nvmrc").write_text("v22.14.0")
    assert by_id(scan(tmp_path), "runtime.pinned").status == Status.PASS


def test_declared_package_manager(tmp_path):
    (tmp_path / "package.json").write_text('{"packageManager":"pnpm@10.1.0"}')
    assert scan(tmp_path).stack.package_managers == ["pnpm"]


def test_pytest_configuration_is_test_indicator(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[tool.pytest.ini_options]\ntestpaths=['tests']")
    assert by_id(scan(tmp_path), "testing.present").status == Status.PASS
