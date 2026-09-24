import re

from fdekit.checks import finding
from fdekit.models import Category as C
from fdekit.models import Check
from fdekit.utils.files import Inventory

ENV_ASSIGNMENT = re.compile(r"(?m)^\s*(?:export\s+)?([A-Z][A-Z0-9_]*)\s*=")
ENV_REFERENCE = re.compile(
    r"process\.env\.([A-Z][A-Z0-9_]*)|"
    r"(?:process\.env|import\.meta\.env)\[\s*(?:"
    r'"([A-Z][A-Z0-9_]*)"|\'([A-Z][A-Z0-9_]*)\')\s*\]|'
    r"(?:os\.getenv|os\.environ\.get)\(\s*[\"']([A-Z][A-Z0-9_]*)[\"']|"
    r"os\.environ\[\s*[\"']([A-Z][A-Z0-9_]*)[\"']"
)


def run(inventory: Inventory) -> list[Check]:
    required = set(inventory.config.required_env)
    for name, content in inventory.files.items():
        if name.endswith((".py", ".js", ".jsx", ".ts", ".tsx")):
            required.update(
                next(group for group in match.groups() if group)
                for match in ENV_REFERENCE.finditer(content)
            )
    examples = [
        name
        for name in inventory.files
        if name.rsplit("/", 1)[-1] in {".env.example", ".env.production.example", ".env.sample"}
    ]
    documented = set().union(*(set(ENV_ASSIGNMENT.findall(inventory.read(n))) for n in examples))
    missing = sorted(required - documented)
    integration_names = sorted(
        name
        for name in required
        if re.search(r"(?:API|TOKEN|DATABASE|ENDPOINT|DSN|URL|SECRET|KEY)", name)
    )
    return [
        finding(
            "configuration.env",
            "Environment variable documentation",
            C.CONFIGURATION,
            not missing,
            12,
            "Compare static references and required_env with example keys.",
            "Document required variables using safe placeholders in .env.example.",
            [f"Undocumented variable: {name}" for name in missing],
            skipped=not required,
        ),
        finding(
            "integration.configuration",
            "Integration configuration contract",
            C.INTEGRATION,
            not (set(integration_names) - documented),
            0,
            "Only configuration names are checked; credentials and connectivity are unverified.",
            "Validate auth, timeouts, retries and connectivity in the target environment.",
            integration_names,
            skipped=not integration_names,
        ),
    ]
