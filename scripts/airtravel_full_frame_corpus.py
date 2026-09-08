"""Materialise the complete eligible AirTravel case frame from the pinned upstream commit.

The accepted Study 1 run used four of the twenty-one eligible candidate models, and
``study1_case_selection`` records that the pinned inventory cannot identify *which* four.
Running the whole eligible frame removes that limitation at the root: when the population is
the sample, no selection rule needs justifying.

Every byte is verified against a hash frozen in ``airtravel-inventory.json`` long before this
module existed, so materialisation can confirm provenance but can never manufacture it. The
module refuses to write a runtime root unless the archive digest and all per-file digests match.

No provider is contacted: this reads a local archive and writes local files only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PINNED_COMMIT = "253b26dc704d523209a5cba79686f8f7fab57d63"
ARCHIVE_SHA256 = "8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701"
CORPUS_ID = "text2uml_airtravel_253b26dc"
INVENTORY = ROOT / "docs/research/phd-proposal/text2uml-airtravel/airtravel-inventory.json"
ARCHIVE_MEMBER_PREFIX = "dataset/AirTravel/"
DESCRIPTION = "description.md"
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


class ProvenanceError(RuntimeError):
    """Raised when a byte stream does not match its pre-pinned digest."""


def eligible_rows(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    """The inventory-level eligibility predicate, copied verbatim from study1_case_selection."""
    rows = [
        row
        for row in inventory["files"]
        if row.get("classification") == "GENERATED_CANDIDATE_MODEL"
        and str(row.get("path", "")).startswith("result_one_")
        and int(row.get("bytes", 0) or 0) > 0
        and row.get("syntax_validation") == "WRAPPER_PRESENT"
        and HEX64.fullmatch(str(row.get("sha256", "")))
    ]
    return sorted(rows, key=lambda row: row["path"])


def read_verified(archive: zipfile.ZipFile, members: dict[str, str], row: dict[str, Any]) -> bytes:
    path = row["path"]
    if path not in members:
        raise ProvenanceError(f"{path}: absent from the pinned archive")
    data = archive.read(members[path])
    digest = hashlib.sha256(data).hexdigest()
    if digest != row["sha256"]:
        raise ProvenanceError(f"{path}: digest {digest} does not match pinned {row['sha256']}")
    if len(data) != int(row["bytes"]):
        raise ProvenanceError(f"{path}: {len(data)} bytes, pinned {row['bytes']}")
    return data


def materialise(archive_path: Path, runtime_root: Path) -> dict[str, Any]:
    archive_digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    if archive_digest != ARCHIVE_SHA256:
        raise ProvenanceError(
            f"archive digest {archive_digest} does not match pinned {ARCHIVE_SHA256}"
        )

    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    rows = eligible_rows(inventory)
    description_row = next(row for row in inventory["files"] if row["path"] == DESCRIPTION)

    with zipfile.ZipFile(archive_path) as archive:
        members = {
            name.split(ARCHIVE_MEMBER_PREFIX, 1)[1]: name
            for name in archive.namelist()
            if ARCHIVE_MEMBER_PREFIX in name and not name.endswith("/")
        }
        description = read_verified(archive, members, description_row)
        cases = [(row, read_verified(archive, members, row)) for row in rows]

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

    return {
        "schema_version": "airtravel-full-frame-contract-v1",
        "corpus_id": CORPUS_ID,
        "pinned_commit": PINNED_COMMIT,
        "archive_sha256": ARCHIVE_SHA256,
        "archive_digest_reproduced": True,
        "eligibility_predicate": (
            "classification=GENERATED_CANDIDATE_MODEL and path starts result_one_ and bytes>0 "
            "and syntax_validation=WRAPPER_PRESENT and sha256 is 64 hex"
        ),
        "frame": "complete eligible population, not a sample",
        "case_count": len(cases),
        "runtime_files": contract,
    }


def verify(runtime_root: Path, contract: dict[str, Any]) -> list[str]:
    """Re-hash what was written, so a corrupted write cannot reach the provider."""
    problems = []
    for relative, pin in contract["runtime_files"].items():
        target = runtime_root / relative
        if not target.is_file():
            problems.append(f"{relative}: missing")
            continue
        if hashlib.sha256(target.read_bytes()).hexdigest() != pin["sha256"]:
            problems.append(f"{relative}: digest mismatch after write")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive",
        type=Path,
        default=ROOT
        / "external_data/airtravel-pr38/corpus-fullframe"
        / f"text2uml-{PINNED_COMMIT}.zip",
    )
    parser.add_argument(
        "--runtime-root",
        type=Path,
        default=ROOT / "external_data/airtravel-pr38/fullframe_runtime",
    )
    parser.add_argument(
        "--contract-out",
        type=Path,
        default=ROOT / "external_data/airtravel-pr38/fullframe_runtime/full-frame-contract.json",
    )
    args = parser.parse_args()

    contract = materialise(args.archive, args.runtime_root)
    problems = verify(args.runtime_root, contract)
    if problems:
        raise ProvenanceError("post-write verification failed:\n" + "\n".join(problems))
    contract["post_write_verification"] = "all digests re-verified after write"
    args.contract_out.parent.mkdir(parents=True, exist_ok=True)
    args.contract_out.write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": "MATERIALISED",
                "case_count": contract["case_count"],
                "archive_digest_reproduced": True,
                "post_write_verification": "PASS",
                "contract": str(args.contract_out),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
