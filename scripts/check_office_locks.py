"""Report Office lock files without touching them.

Word and PowerPoint write a hidden ``~$name`` sidecar while a document is open. Those files are
owned by the user's running application, and a tool that deletes one to make its own scan pass is
deleting something it does not own while the owner is still using it.

So this module only reports. It names each lock file, the document it belongs to, and the action
the user can take, and it exits non-zero only when asked to treat locks as blocking. Nothing is
removed, renamed or rewritten, and there is no flag that makes it do so.

No provider is contacted.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOCK_PREFIX = "~$"
OFFICE_SUFFIXES = (".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls")


def find_locks(root: Path) -> list[dict[str, Any]]:
    locks = []
    for path in root.rglob(f"{LOCK_PREFIX}*"):
        if not path.is_file() or path.suffix.lower() not in OFFICE_SUFFIXES:
            continue
        owner = path.with_name(path.name[len(LOCK_PREFIX):])
        locks.append(
            {
                "lock_file": str(path.relative_to(root)).replace("\\", "/"),
                "belongs_to": str(owner.relative_to(root)).replace("\\", "/")
                if owner.exists()
                else "unknown document",
                "document_still_present": owner.exists(),
                "bytes": path.stat().st_size,
                "action_for_the_user": (
                    "close the document in Word or PowerPoint; the application removes its own "
                    "lock file on close"
                ),
            }
        )
    return sorted(locks, key=lambda row: row["lock_file"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--blocking",
        action="store_true",
        help="exit non-zero when locks are present, for callers that cannot proceed with them",
    )
    args = parser.parse_args()

    locks = find_locks(args.root)
    report = {
        "schema_version": "office-lock-report-v1",
        "locks_found": len(locks),
        "destructive_action_taken": False,
        "policy": (
            "lock files belong to the user's running Office application and are never deleted, "
            "renamed or rewritten by this repository's tooling"
        ),
        "locks": locks,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if locks:
        print(
            "\nWARNING: "
            f"{len(locks)} Office lock file(s) present. Scans that walk every file may report "
            "a permission error on them. This is expected while a document is open and is not a "
            "repository defect."
        )
    return 1 if (locks and args.blocking) else 0


if __name__ == "__main__":
    raise SystemExit(main())
