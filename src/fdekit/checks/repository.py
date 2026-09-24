from fdekit.checks import finding
from fdekit.models import Category as C
from fdekit.models import Check
from fdekit.utils.files import Inventory, git


def run(inventory: Inventory) -> list[Check]:
    ok, result = git(inventory.root, "rev-parse", "--is-inside-work-tree")
    repository = ok and result.strip() == "true"
    status_ok, status = git(
        inventory.root, "status", "--porcelain", "--untracked-files=normal", "--", "."
    )
    head_ok, _ = git(inventory.root, "rev-parse", "--verify", "HEAD")
    return [
        finding(
            "repository.git",
            "Git worktree",
            C.REPOSITORY,
            repository,
            3,
            "Read-only local Git inspection; remote access is not tested.",
            "Initialize Git or run from a checked-out repository.",
        ),
        finding(
            "repository.commit",
            "Commit history exists",
            C.REPOSITORY,
            head_ok,
            2,
            "A local HEAD commit exists; commit content and history are not audited.",
            "Commit a reviewed baseline before deployment.",
            skipped=not repository,
        ),
        finding(
            "repository.clean",
            "Working tree state",
            C.REPOSITORY,
            status_ok and not status.strip(),
            2,
            "Uncommitted changes can affect reproducibility.",
            "Review and commit intended deployment changes.",
            skipped=not repository,
        ),
        finding(
            "scan.complete",
            "Inspection completeness",
            C.CONFIGURATION,
            not inventory.problems,
            10,
            "Report file limits and filesystem access failures.",
            "Review skipped paths or adjust limits and rescan.",
            inventory.problems,
        ),
    ]
