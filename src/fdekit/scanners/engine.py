from pathlib import Path

from fdekit.checks import configuration, project, repository, security
from fdekit.models import Report
from fdekit.scanners.stack import detect
from fdekit.scoring import score
from fdekit.utils.files import collect, load_config, parse_manifests


def scan(path: Path) -> Report:
    root = path.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Scan path must be a directory")
    inventory = collect(root, load_config(root))
    errors = parse_manifests(inventory)
    stack = detect(inventory)
    checks = (
        project.run(inventory, stack, errors)
        + configuration.run(inventory)
        + security.run(inventory)
        + repository.run(inventory)
    )
    report = Report(project=root.name, stack=stack, checks=checks, score=score(checks))

    # Sanitize every dynamic string, including malformed runtime pins and hostile filenames.
    def sanitize(value: object) -> object:
        if isinstance(value, str):
            return security.redact("".join(c if c >= " " or c == "\n" else "?" for c in value))
        if isinstance(value, dict):
            return {str(k): sanitize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [sanitize(v) for v in value]
        return value

    return Report.model_validate(sanitize(report.model_dump(mode="json")))
