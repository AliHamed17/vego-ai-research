"""Generate or check the canonical AirTravel v4 machine manifest.

This command is metadata-only.  It never imports the protected runtime and
never reads model content; it serializes the pure contract definition.
"""

from __future__ import annotations

import argparse
import sys

from airtravel_v4_contract import MANIFEST_PATH, ROOT, canonical, frozen_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the checked-in manifest is stale")
    parser.add_argument("--write", action="store_true", help="write the canonical manifest")
    args = parser.parse_args(argv)
    if args.check and args.write:
        parser.error("--check and --write are mutually exclusive")
    target = ROOT / MANIFEST_PATH
    expected = canonical(frozen_manifest())
    if args.write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(expected)
        print(target)
        return 0
    actual = target.read_bytes() if target.is_file() else b""
    if actual != expected:
        print("airtravel v4 manifest: STALE", file=sys.stderr)
        return 1
    print("airtravel v4 manifest: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
