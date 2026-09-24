import shutil
import socket
import subprocess
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("Tests must not use the network")

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket.socket, "connect", blocked)


@pytest.fixture
def fixture_repo(tmp_path):
    def copy(name):
        target = tmp_path / name
        shutil.copytree(Path(__file__).parent / "fixtures" / name, target)
        return target

    return copy


@pytest.fixture
def git_repo(tmp_path):
    if not shutil.which("git"):
        pytest.skip("Git not installed")
    for args in (
        ["init", "-b", "main"],
        ["config", "user.name", "Fixture"],
        ["config", "user.email", "fixture@example.invalid"],
    ):
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True)
    return tmp_path
