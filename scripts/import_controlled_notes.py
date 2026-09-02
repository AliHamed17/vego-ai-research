"""Validate local controlled-notes provenance and write a private redacted receipt."""

from __future__ import annotations

import argparse
from pathlib import Path

from vego_study1.controlled_notes import ControlledNotesError, import_controlled_notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notes-source", required=True)
    parser.add_argument("--provenance-manifest", required=True)
    parser.add_argument("--private-output-root", required=True, type=Path)
    parser.add_argument("--intended-use", required=True, choices=["development_only"])
    arguments = parser.parse_args()
    try:
        receipt = import_controlled_notes(
            arguments.notes_source,
            arguments.provenance_manifest,
            arguments.private_output_root,
            intended_use=arguments.intended_use,
        )
    except ControlledNotesError as error:
        parser.error(str(error))
    print(f"controlled notes import status: {receipt['status']}; records: {receipt['record_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
