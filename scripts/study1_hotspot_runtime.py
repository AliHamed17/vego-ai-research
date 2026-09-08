"""Materialise the runtime for exactly the cases the frozen manifest selected.

The manifest names six cases and pins each one's SHA-256. This module writes a runtime root
containing those cases and nothing else, verifying every byte against the manifest's pin before
and after writing. It cannot be pointed at a different set: the selection is read from the
manifest, never from an argument.

That constraint is the point. If the sample could be supplied on the command line, the frozen
draw would be advisory rather than binding, and a later run could quietly use a different six.

No provider is contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/research/phd-proposal/study1-hotspot-manifest.json"
ARCHIVE_MEMBER_PREFIX = "dataset/AirTravel/"
DESCRIPTION = "description.md"


class ProvenanceError(RuntimeError):
    """Raised when a byte stream does not match the digest the manifest froze."""


def read_verified(archive: zipfile.ZipFile, members: dict[str, str], path: str,
                  expected_sha: str, expected_bytes: int) -> bytes:
    if path not in members:
        raise ProvenanceError(f"{path}: absent from the pinned archive")
    data = archive.read(members[path])
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected_sha:
        raise ProvenanceError(f"{path}: digest {digest} does not match pinned {expected_sha}")
    if len(data) != expected_bytes:
        raise ProvenanceError(f"{path}: {len(data)} bytes, pinned {expected_bytes}")
    return data


def materialise(archive_path: Path, runtime_root: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    archive_digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    if archive_digest != manifest["corpus"]["archive_sha256"]:
        raise ProvenanceError("archive digest does not match the manifest")

    inventory = json.loads(
        (ROOT / "docs/research/phd-proposal/text2uml-airtravel/airtravel-inventory.json")
        .read_text(encoding="utf-8")
    )
    description_row = next(row for row in inventory["files"] if row["path"] == DESCRIPTION)
    selected = manifest["selection"]["selected"]

    with zipfile.ZipFile(archive_path) as archive:
        members = {
            name.split(ARCHIVE_MEMBER_PREFIX, 1)[1]: name
            for name in archive.namelist()
            if ARCHIVE_MEMBER_PREFIX in name and not name.endswith("/")
        }
        description = read_verified(
            archive, members, DESCRIPTION, description_row["sha256"], int(description_row["bytes"])
        )
        cases = [
            (row, read_verified(archive, members, row["path"], row["sha256"], int(row["bytes"])))
            for row in selected
        ]

    (runtime_root / "domain_description").mkdir(parents=True, exist_ok=True)
    (runtime_root / "candidate_models").mkdir(parents=True, exist_ok=True)
    (runtime_root / "domain_description" / DESCRIPTION).write_bytes(description)

    contract: dict[str, dict[str, Any]] = {
        f"domain_description/{DESCRIPTION}": {
            "sha256": description_row["sha256"],
            "bytes": int(description_row["bytes"]),
            "upstream_path": DESCRIPTION,
        }
    }
    for index, (row, data) in enumerate(cases, start=1):
        relative = f"candidate_models/{index:02d}_{row['path']}"
        (runtime_root / relative).write_bytes(data)
        contract[relative] = {
            "sha256": row["sha256"],
            "bytes": int(row["bytes"]),
            "upstream_path": row["path"],
        }

    for relative, pin in contract.items():
        written = runtime_root / relative
        if hashlib.sha256(written.read_bytes()).hexdigest() != pin["sha256"]:
            raise ProvenanceError(f"{relative}: digest mismatch after write")

    return {
        "schema_version": "airtravel-full-frame-contract-v1",
        "corpus_id": manifest["corpus"]["corpus_id"],
        "pinned_commit": manifest["corpus"]["pinned_commit"],
        "archive_sha256": manifest["corpus"]["archive_sha256"],
        "archive_digest_reproduced": True,
        "frame": "the six cases frozen by the hotspot manifest, not a sample drawn here",
        "manifest_sha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
        "case_count": len(cases),
        "runtime_files": contract,
        "post_write_verification": "all digests re-verified after write",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive",
        type=Path,
        default=ROOT
        / "external_data/airtravel-pr38/corpus-fullframe"
        / "text2uml-253b26dc704d523209a5cba79686f8f7fab57d63.zip",
    )
    parser.add_argument(
        "--runtime-root",
        type=Path,
        default=ROOT / "external_data/airtravel-pr38/hotspot/runtime",
    )
    args = parser.parse_args()

    contract = materialise(args.archive, args.runtime_root)
    target = args.runtime_root / "full-frame-contract.json"
    target.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "MATERIALISED",
                "case_count": contract["case_count"],
                "manifest_sha256": contract["manifest_sha256"],
                "contract": str(target),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
