"""Read only bounded regular files; never follow symlinks or junctions."""

import fnmatch
import json
import os
import stat
import subprocess
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from fdekit.models import Config

DEFAULT_CONFIG = """schema_version: 1
exclude:
  - tests/fixtures
  - examples
max_file_bytes: 262144
max_files: 10000
max_total_bytes: 16777216
required_env: []
min_score: 70
"""
IGNORED = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".fdekit",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".next",
}


def linked(path: Path) -> bool:
    metadata = path.lstat()
    return stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0) & 0x400
    )


def load_config(root: Path) -> Config:
    path = root / "fdekit.yaml"
    if not path.exists() and not path.is_symlink():
        return Config()
    if linked(path) or not path.is_file() or path.stat().st_size > 65536:
        raise ValueError("fdekit.yaml must be a regular file smaller than 64 KiB")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return Config.model_validate(data if data is not None else {})
    except (yaml.YAMLError, ValueError, UnicodeError, RecursionError) as exc:
        # Do not include parser messages: they may contain secrets from the input.
        raise ValueError(
            "Invalid fdekit.yaml; check keys and types against fdekit.example.yaml"
        ) from exc


@dataclass
class Inventory:
    root: Path
    config: Config
    files: dict[str, str] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)
    configs: dict[str, dict[str, Any]] = field(default_factory=dict)

    def read(self, name: str) -> str:
        return self.files.get(name, "")

    def has(self, name: str) -> bool:
        return name in self.files


def collect(root: Path, config: Config) -> Inventory:
    inventory = Inventory(root, config)
    seen = 0
    total_bytes = 0

    def excluded(relative: str) -> bool:
        return any(
            fnmatch.fnmatchcase(relative, pattern) or relative.startswith(pattern.rstrip("/") + "/")
            for pattern in config.exclude
        )

    def walk_error(error: OSError) -> None:
        inventory.problems.append("A directory could not be read")

    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        base = Path(directory)
        kept = []
        for name in sorted(dirs):
            path = base / name
            relative = path.relative_to(root).as_posix()
            if name in IGNORED or excluded(relative):
                continue
            try:
                if linked(path):
                    inventory.problems.append(f"Linked directory skipped: {relative}")
                else:
                    kept.append(name)
            except OSError:
                inventory.problems.append(f"Unreadable directory: {relative}")
        dirs[:] = kept
        for name in sorted(files):
            path = base / name
            relative = path.relative_to(root).as_posix()
            if excluded(relative):
                continue
            seen += 1
            if seen > config.max_files:
                inventory.problems.append("File count limit reached; scan is incomplete")
                return inventory
            try:
                if linked(path) or not stat.S_ISREG(path.lstat().st_mode):
                    inventory.problems.append(f"Non-regular file skipped: {relative}")
                    continue
                with path.open("rb") as stream:
                    raw = stream.read(config.max_file_bytes + 1)
                if len(raw) > config.max_file_bytes:
                    inventory.problems.append(f"Oversized file skipped: {relative}")
                    continue
                total_bytes += len(raw)
                if total_bytes > config.max_total_bytes:
                    inventory.problems.append("Total byte limit reached; scan is incomplete")
                    return inventory
                if b"\0" in raw:
                    continue
                inventory.files[relative] = raw.decode("utf-8-sig")
            except UnicodeError:
                continue
            except OSError:
                inventory.problems.append(f"Unreadable file: {relative}")
    return inventory


def parse_manifests(inventory: Inventory) -> list[str]:
    errors = []
    for name in ("package.json", "pyproject.toml", "Pipfile"):
        if not inventory.has(name):
            continue
        try:
            data = (
                json.loads(inventory.read(name))
                if name.endswith(".json")
                else tomllib.loads(inventory.read(name))
            )
            if not isinstance(data, dict):
                raise ValueError("Expected an object")
            if name == "package.json":
                for key in ("dependencies", "devDependencies", "scripts", "engines"):
                    if key in data and (
                        not isinstance(data[key], dict)
                        or not all(isinstance(v, str) for v in data[key].values())
                    ):
                        raise ValueError("Invalid package metadata")
            if name == "pyproject.toml":
                project = data.get("project", {})
                if not isinstance(project, dict) or not isinstance(data.get("tool", {}), dict):
                    raise ValueError("Invalid Python metadata")
                deps = project.get("dependencies", [])
                if not isinstance(deps, list) or not all(isinstance(v, str) for v in deps):
                    raise ValueError("Invalid Python dependencies")
            inventory.configs[name] = data
        except (ValueError, TypeError, RecursionError):
            errors.append(f"Invalid manifest: {name}")
    return errors


def git(root: Path, *args: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-C", str(root), *args],
            capture_output=True,
            timeout=10,
            check=False,
        )
        return result.returncode == 0, result.stdout.decode("utf-8", errors="replace")
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
