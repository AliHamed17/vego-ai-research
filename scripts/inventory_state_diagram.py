"""Write a blocked, aggregate-only local StateDiagram inventory receipt."""

from __future__ import annotations

import argparse
from pathlib import Path

from vego_study1.state_diagram_inventory import (
    StateDiagramInventoryError,
    write_state_diagram_inventory,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", required=True, type=Path)
    parser.add_argument("--private-output-root", required=True, type=Path)
    arguments = parser.parse_args()
    try:
        receipt = write_state_diagram_inventory(arguments.state_root, arguments.private_output_root)
    except StateDiagramInventoryError as error:
        parser.error(str(error))
    print(f"inventory status: {receipt['status']}; files: {receipt['file_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
