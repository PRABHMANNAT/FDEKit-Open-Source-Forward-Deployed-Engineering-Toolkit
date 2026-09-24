import re

from fdekit.checks import finding
from fdekit.models import Category as C
from fdekit.models import Check, Stack
from fdekit.utils.files import Inventory


def run(inventory: Inventory, stack: Stack, manifest_errors: list[str]) -> list[Check]:
    files = inventory.files
    python = "Python" in stack.languages
    node = "JavaScript" in stack.languages or "TypeScript" in stack.languages
    pins = []
    if python:
        pins.append(bool(re.fullmatch(r"\d+\.\d+\.\d+", inventory.read(".python-version").strip())))
    if node:
        pins.append(
            any(
                re.fullmatch(r"v?\d+\.\d+\.\d+", inventory.read(n).strip())
                for n in (".nvmrc", ".node-version")
            )
        )
    locks = []
    if python:
        requirements = [
            line.strip()
            for line in inventory.read("requirements.txt").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        locks.append(
            any(n in files for n in ("uv.lock", "poetry.lock", "Pipfile.lock"))
            or bool(
                requirements
                and all(re.match(r"[A-Za-z0-9_.-]+==[^*\s]+$", line) for line in requirements)
            )
        )
    if node:
        locks.append(any(n in files for n in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock")))
    scripts = inventory.configs.get("package.json", {}).get("scripts", {})
    test_command = scripts.get("test", "")
    tests = bool(test_command and "no test specified" not in test_command.lower()) or any(
        n.startswith("tests/") and n.endswith(".py") for n in files
    )
    python_tool = inventory.configs.get("pyproject.toml", {}).get("tool", {})
    tests = tests or "pytest" in python_tool or inventory.has("pytest.ini")
    health = any(
        re.search(r"(?:[/\"'])health(?:z|check)?\b|\bHEALTHCHECK\b", text, re.I)
        for name, text in files.items()
        if name.endswith((".py", ".js", ".ts", ".tsx")) or name == "Dockerfile"
    )
    return [
        finding(
            "project.stack",
            "Recognized project stack",
            C.DEPENDENCIES,
            bool(stack.languages),
            8,
            "Language and manifest indicators only.",
            "Add a supported project manifest or inspect the stack manually.",
            stack.languages,
        ),
        finding(
            "dependencies.manifests",
            "Manifest syntax",
            C.DEPENDENCIES,
            not manifest_errors,
            15,
            "Parse supported root manifests without executing code.",
            "Repair invalid manifests.",
            manifest_errors,
            critical=True,
        ),
        finding(
            "runtime.pinned",
            "Runtime versions pinned",
            C.RUNTIME,
            all(pins),
            5,
            "Exact x.y.z versions in .python-version, .nvmrc or .node-version.",
            "Pin each detected runtime to a tested patch version.",
            list(stack.runtimes),
            skipped=not pins,
        ),
        finding(
            "dependencies.locked",
            "Dependency reproducibility indicators",
            C.DEPENDENCIES,
            all(locks),
            8,
            "Lockfile presence or simple exact requirements; integrity not verified.",
            "Commit a lockfile and verify a clean reproducible install.",
            skipped=not locks,
        ),
        finding(
            "testing.present",
            "Test indicators",
            C.TESTING,
            tests,
            10,
            "Test command, files or pytest configuration detected; tests are not executed.",
            "Add meaningful automated tests and run them in CI.",
        ),
        finding(
            "ci.present",
            "CI configuration",
            C.CI,
            bool(stack.ci),
            8,
            "Known CI configuration files exist; workflow results are not checked.",
            "Add CI that tests and builds the project.",
            stack.ci,
        ),
        finding(
            "deployment.config",
            "Deployment configuration",
            C.DEPLOYMENT,
            bool(stack.deployment),
            8,
            "Deployment file indicators at the project root.",
            "Document deployment and add appropriate provider or container configuration.",
            stack.deployment,
        ),
        finding(
            "deployment.docker",
            "Docker indicators",
            C.DEPLOYMENT,
            bool(stack.docker),
            0,
            "Docker is optional; no score deduction when absent.",
            "Consider containers if required by your target environment.",
            stack.docker,
            skipped=not stack.docker,
        ),
        finding(
            "observability.health",
            "Health-check indicator",
            C.OBSERVABILITY,
            health,
            3,
            "Text heuristic only; no endpoint is called.",
            "For services, implement and verify a health endpoint; libraries may omit it.",
            skipped=not stack.frameworks,
        ),
    ]
