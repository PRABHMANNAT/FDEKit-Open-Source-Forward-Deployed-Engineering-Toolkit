"""Conservative secret-risk heuristics. Evidence never includes matched values."""

import re

from fdekit.checks import finding
from fdekit.models import Category as C
from fdekit.models import Check
from fdekit.utils.files import Inventory, git

TOKEN = re.compile(
    r"(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|"
    r"AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"
)
ASSIGNMENT = re.compile(
    r"(?im)[\"']?([A-Z0-9_]*(?:SECRET|TOKEN|PASSWORD|API_KEY|PRIVATE_KEY)[A-Z0-9_]*)"
    r"[\"']?\s*[:=]\s*[\"']?([^\s\"',;}]+)"
)
PLACEHOLDERS = {
    "",
    "changeme",
    "replace-me",
    "your-key-here",
    "example",
    "placeholder",
    "null",
    "none",
    "xxx",
    "...",
}


def redact(text: str) -> str:
    text = TOKEN.sub("[REDACTED]", text)
    return ASSIGNMENT.sub(lambda match: f"{match.group(1)}=[REDACTED]", text)


def risk(content: str) -> bool:
    if TOKEN.search(content):
        return True
    for match in ASSIGNMENT.finditer(content):
        value = match.group(2)
        if value.lower() in PLACEHOLDERS or value.startswith(("${", "{{", "<", "os.", "process.")):
            continue
        if re.match(r"[A-Za-z_][A-Za-z0-9_.]*\(", value):
            continue  # A function expression is not a literal credential.
        if len(value) >= 8 or value.lower() in {"admin", "password", "123456", "root"}:
            return True
    return False


def run(inventory: Inventory) -> list[Check]:
    suspects = []
    debug = []
    for name, content in inventory.files.items():
        # Source and common configuration files only; not prose, lockfiles or binary assets.
        if name.endswith(
            (
                ".py",
                ".js",
                ".ts",
                ".tsx",
                ".json",
                ".toml",
                ".yaml",
                ".yml",
                ".ini",
                ".cfg",
                ".conf",
            )
        ) or name.rsplit("/", 1)[-1].startswith(".env"):
            if risk(content):
                suspects.append(f"Potential credential in {name}; value [REDACTED]")
            if re.search(r"(?im)^\s*(?:DEBUG|FLASK_DEBUG)\s*[:=]\s*(?:true|1)\b", content):
                debug.append(f"Debug enabled in {name}")
    ok, tracked = git(inventory.root, "ls-files", "-z", "--", ".")
    env_files = [
        name
        for name in tracked.split("\0")
        if name
        and name.rsplit("/", 1)[-1].startswith(".env")
        and not name.endswith((".example", ".sample", ".template"))
    ]
    ignore_ok, _ = git(inventory.root, "check-ignore", "--no-index", "--quiet", ".env")
    if not ok:
        ignore_ok = ".env" in inventory.read(".gitignore").splitlines()
    return [
        finding(
            "security.secrets",
            "Credential-risk patterns",
            C.SECURITY,
            not suspects,
            25,
            "Heuristics over selected working-tree files; no history scan or security guarantee.",
            "Review locally. Rotate exposed credentials and remove them from tracked content.",
            suspects,
            critical=True,
        ),
        finding(
            "security.tracked-env",
            "Environment files tracked by Git",
            C.SECURITY,
            not env_files,
            20,
            "Inspect the current Git index, including ignored tracked files.",
            "Untrack private environment files and rotate any exposed credentials.",
            [f"Tracked environment file: {name}" for name in env_files],
            critical=True,
            skipped=not ok,
        ),
        finding(
            "security.gitignore",
            "Private environment ignore rule",
            C.SECURITY,
            ignore_ok,
            5,
            "Check whether the root .env path is ignored; other filenames need review.",
            "Ignore .env and private variants; explicitly allow sanitized examples.",
        ),
        finding(
            "security.debug",
            "Debug configuration risk",
            C.SECURITY,
            not debug,
            10,
            "Detect literal DEBUG=true or FLASK_DEBUG=1 assignments.",
            "Disable debug mode in production configuration.",
            debug,
        ),
    ]
