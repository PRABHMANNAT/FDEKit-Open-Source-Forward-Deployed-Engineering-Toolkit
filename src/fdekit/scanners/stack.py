import re
from pathlib import PurePosixPath

from fdekit.models import Stack
from fdekit.utils.files import Inventory


def detect(inventory: Inventory) -> Stack:
    files = inventory.files
    stack = Stack()
    suffixes = {PurePosixPath(name).suffix for name in files}
    python = any(name in files for name in ("pyproject.toml", "requirements.txt", "Pipfile"))
    if python or ".py" in suffixes:
        stack.languages.append("Python")
    if "package.json" in files or suffixes & {".js", ".jsx", ".mjs"}:
        stack.languages.append("JavaScript")
    if "tsconfig.json" in files or suffixes & {".ts", ".tsx"}:
        stack.languages.append("TypeScript")
    managers = {
        "package-lock.json": "npm",
        "pnpm-lock.yaml": "pnpm",
        "yarn.lock": "yarn",
        "uv.lock": "uv",
        "poetry.lock": "Poetry",
        "Pipfile": "Pipenv",
        "requirements.txt": "pip",
    }
    stack.package_managers = sorted({v for k, v in managers.items() if k in files})
    if python and not set(stack.package_managers) & {"uv", "Poetry", "Pipenv", "pip"}:
        stack.package_managers.append("pip/build backend (inferred)")
    package = inventory.configs.get("package.json", {})
    manager = package.get("packageManager")
    if isinstance(manager, str):
        match = re.fullmatch(r"(npm|pnpm|yarn)@[0-9][A-Za-z0-9.+_-]*", manager)
        if match and match.group(1) not in stack.package_managers:
            stack.package_managers.append(match.group(1))
            stack.package_managers.sort()
    dependencies = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
    for dependency, framework in {
        "next": "Next.js",
        "react": "React",
        "vite": "Vite",
        "express": "Express",
    }.items():
        if dependency in dependencies:
            stack.frameworks.append(framework)
    declared = (
        inventory.configs.get("pyproject.toml", {}).get("project", {}).get("dependencies", [])
    )
    python_text = (
        "\n".join(declared)
        + "\n"
        + "\n".join(inventory.read(n) for n in ("pyproject.toml", "requirements.txt", "Pipfile"))
    )
    for dependency, framework in {
        "fastapi": "FastAPI",
        "flask": "Flask",
        "django": "Django",
    }.items():
        if re.search(rf"(?im)^\s*[\"']?{dependency}(?:\b|\[)", python_text):
            stack.frameworks.append(framework)
    project = inventory.configs.get("pyproject.toml", {}).get("project", {})
    requirement = project.get("requires-python")
    if isinstance(requirement, str):
        stack.runtimes["Python constraint"] = requirement
    engines = package.get("engines", {})
    if isinstance(engines.get("node"), str):
        stack.runtimes["Node constraint"] = engines["node"]
    for name, runtime in (
        (".python-version", "Python pin"),
        (".nvmrc", "Node pin"),
        (".node-version", "Node pin"),
    ):
        if inventory.has(name):
            stack.runtimes[runtime] = inventory.read(name).strip()[:80]
    stack.docker = [
        name
        for name in (
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.yaml",
            "compose.yml",
            "compose.yaml",
        )
        if name in files
    ]
    if any(
        name.startswith(".github/workflows/") and name.endswith((".yml", ".yaml")) for name in files
    ):
        stack.ci.append("GitHub Actions")
    for name, provider in (
        (".gitlab-ci.yml", "GitLab CI"),
        ("Jenkinsfile", "Jenkins"),
        (".circleci/config.yml", "CircleCI"),
    ):
        if name in files:
            stack.ci.append(provider)
    stack.deployment = [
        name for name in ("vercel.json", "netlify.toml", "render.yaml", "Procfile") if name in files
    ] + stack.docker
    return stack
