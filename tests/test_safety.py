import subprocess
from pathlib import Path

import pytest

from fdekit.checks.security import redact, risk
from fdekit.models import Config
from fdekit.scanners.engine import scan
from fdekit.utils.files import collect, git, load_config


@pytest.mark.parametrize(
    "secret",
    ["sk-" + "a" * 30, "ghp_" + "Z" * 30, "AKIA" + "A" * 16, "-----BEGIN PRIVATE KEY-----"],
)
def test_token_redaction(tmp_path, secret):
    (tmp_path / "config.json").write_text('{"value": "' + secret + '"}')
    result = scan(tmp_path)
    assert secret not in result.model_dump_json()
    assert any(c.id == "security.secrets" and c.score_impact == 25 for c in result.checks)
    assert secret not in redact(secret)


@pytest.mark.parametrize("value", ["replace-me", "changeme", "<your-secret>", "${MY_TOKEN}"])
def test_safe_placeholders(value):
    assert not risk("API_KEY=" + value)


@pytest.mark.parametrize("value", ["admin", "password", "abcdef0123456789"])
def test_unsafe_example_password(value):
    assert risk("PASSWORD=" + value)
    assert value not in redact("PASSWORD=" + value)


def test_untrusted_runtime_pin_redacted(tmp_path):
    secret = "sk-" + "b" * 30
    (tmp_path / ".nvmrc").write_text(secret)
    assert secret not in scan(tmp_path).model_dump_json()


def test_limits_and_binary(tmp_path):
    (tmp_path / "big.py").write_text("x" * 1025)
    (tmp_path / "binary").write_bytes(b"\x00\xff")
    (tmp_path / "invalid").write_bytes(b"\xff")
    (tmp_path / "small.py").write_text("pass")
    inventory = collect(tmp_path, Config(max_file_bytes=1024))
    assert inventory.files == {"small.py": "pass"}
    assert inventory.problems == ["Oversized file skipped: big.py"]
    assert "File count limit reached" in collect(tmp_path, Config(max_files=1)).problems[-1]


def test_prunes_dependencies_and_examples(tmp_path):
    for name in ("node_modules", ".git", ".venv", "examples", ".fdekit"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "secret.py").write_text("PASSWORD=abcdef012345")
    assert collect(tmp_path, Config()).files == {}


def make_link(path, target, directory=False):
    try:
        path.symlink_to(target, target_is_directory=directory)
    except OSError:
        pytest.skip("Symlink creation unavailable on this host")


def test_no_symlink_escape(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.py").write_text("PASSWORD=abcdef012345")
    root = tmp_path / "project"
    root.mkdir()
    make_link(root / "linked", outside, True)
    make_link(root / "file.py", outside / "secret.py")
    inventory = collect(root, Config())
    assert not inventory.files
    assert len(inventory.problems) == 2


def test_config_link_rejected(tmp_path):
    target = tmp_path / "other.yaml"
    target.write_text("{}")
    make_link(tmp_path / "fdekit.yaml", target)
    with pytest.raises(ValueError):
        load_config(tmp_path)


def test_large_and_empty_config(tmp_path):
    (tmp_path / "fdekit.yaml").write_text("")
    assert load_config(tmp_path) == Config()
    (tmp_path / "fdekit.yaml").write_text(" " * 65537)
    with pytest.raises(ValueError):
        load_config(tmp_path)


@pytest.mark.parametrize("error", [FileNotFoundError(), subprocess.TimeoutExpired("git", 10)])
def test_git_unavailable(monkeypatch, tmp_path, error):
    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(subprocess, "run", fail)
    assert git(tmp_path, "status") == (False, "")
    assert scan(tmp_path).score < 100


def test_unreadable_file_is_warning(monkeypatch, tmp_path):
    target = tmp_path / "private.py"
    target.touch()
    original = Path.open

    def fail(self, *args, **kwargs):
        if self == target:
            raise PermissionError()
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail)
    assert collect(tmp_path, Config()).problems == ["Unreadable file: private.py"]


def test_total_byte_budget(tmp_path):
    for name in ("a.py", "b.py"):
        (tmp_path / name).write_text("x" * 800)
    inventory = collect(tmp_path, Config(max_total_bytes=1024))
    assert list(inventory.files) == ["a.py"]
    assert inventory.problems == ["Total byte limit reached; scan is incomplete"]


def test_function_expressions_are_not_literal_credentials():
    assert not risk("TOKEN = re.compile('pattern')")
    assert not risk("API_KEY = get_secret()")


def test_deep_json_is_reported_not_crashed(tmp_path):
    (tmp_path / "package.json").write_text("[" * 2000 + "]" * 2000)
    report = scan(tmp_path)
    assert any(c.id == "dependencies.manifests" and c.score_impact == 15 for c in report.checks)


def test_link_flags_without_windows_symlink_privilege(monkeypatch, tmp_path):
    import stat
    from types import SimpleNamespace

    from fdekit.utils.files import linked

    monkeypatch.setattr(
        Path, "lstat", lambda self: SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
    )
    assert linked(tmp_path)


def test_scan_skips_mocked_file_and_directory_links(monkeypatch, tmp_path):
    import fdekit.utils.files as files

    (tmp_path / "linkdir").mkdir()
    (tmp_path / "linkdir" / "secret.py").write_text("PASSWORD=unsafeexample")
    (tmp_path / "link.py").write_text("PASSWORD=unsafeexample")
    monkeypatch.setattr(files, "linked", lambda path: path.name.startswith("link"))
    inventory = collect(tmp_path, Config())
    assert not inventory.files
    assert len(inventory.problems) == 2
