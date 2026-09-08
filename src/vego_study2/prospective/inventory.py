"""Eligible-case inventory, hash verification and seeded case selection.

The eligible frame is the complete Text2UML AirTravel candidate-model
population pinned by the private full-frame contract.  Only metadata (paths,
sizes, SHA-256 digests) ever leaves the private root; corpus bytes are read
solely to verify digests and to build prompts in memory.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from pathlib import Path
from typing import Any

from . import constants as c

_CASE_RE = re.compile(r"^candidate_models/(\d{2})_result_one_(.+)\.txt$")


class InventoryError(ValueError):
    """Raised when the corpus frame cannot be verified exactly."""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_full_frame_contract(runtime_root: Path) -> dict[str, Any]:
    contract_path = runtime_root / "full-frame-contract.json"
    if not contract_path.is_file():
        raise InventoryError("full-frame contract is missing from the private runtime root")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract.get("schema_version") != c.FULL_FRAME_CONTRACT_SCHEMA:
        raise InventoryError("unexpected full-frame contract schema")
    if contract.get("corpus_id") != c.CORPUS_ID or contract.get("pinned_commit") != c.CORPUS_COMMIT:
        raise InventoryError("full-frame contract does not pin the approved corpus")
    files = contract.get("runtime_files")
    if not isinstance(files, dict) or "domain_description/description.md" not in files:
        raise InventoryError("full-frame contract lacks the domain description entry")
    return contract


def build_eligible_inventory(runtime_root: Path, *, verify_bytes: bool = True) -> dict[str, Any]:
    """Return the machine-readable eligible inventory with verified digests."""
    contract = load_full_frame_contract(runtime_root)
    cases: list[dict[str, Any]] = []
    for relative, expected in sorted(contract["runtime_files"].items()):
        match = _CASE_RE.match(relative)
        if not match:
            continue
        case_id, source_model = match.groups()
        entry = {
            "case_id": case_id,
            "relative_path": relative,
            "source_generator_model": source_model,
            "bytes": int(expected["bytes"]),
            "sha256": expected["sha256"],
            "eligible": True,
            "eligibility_predicate": contract["eligibility_predicate"],
        }
        if verify_bytes:
            target = runtime_root / relative
            if not target.is_file():
                raise InventoryError(f"eligible case file missing: {relative}")
            actual = sha256_file(target)
            if actual != expected["sha256"] or target.stat().st_size != int(expected["bytes"]):
                raise InventoryError(f"eligible case digest mismatch: {relative}")
        cases.append(entry)
    if len(cases) != int(contract["case_count"]):
        raise InventoryError("eligible case count differs from the full-frame contract")
    domain = contract["runtime_files"]["domain_description/description.md"]
    if verify_bytes:
        target = runtime_root / "domain_description/description.md"
        if not target.is_file() or sha256_file(target) != domain["sha256"]:
            raise InventoryError("domain description digest mismatch")
    return {
        "schema_version": c.CASE_SELECTION_SCHEMA,
        "corpus_id": c.CORPUS_ID,
        "corpus_commit": c.CORPUS_COMMIT,
        "frame": contract["frame"],
        "archive_sha256": contract["archive_sha256"],
        "eligibility_predicate": contract["eligibility_predicate"],
        "domain_description": {"relative_path": "domain_description/description.md", **domain},
        "eligible_case_count": len(cases),
        "eligible_cases": cases,
    }


def select_cases(eligible_case_ids: list[str], sample_size: int, seed: int) -> list[str]:
    """Executable selection rule: seeded simple random sample without replacement."""
    if sample_size < c.MIN_PAIRED_CASES:
        raise InventoryError("sample size below the minimum paired-case floor")
    ordered = sorted(eligible_case_ids)
    if sample_size > len(ordered):
        raise InventoryError("sample size exceeds the eligible frame")
    return sorted(random.Random(seed).sample(ordered, sample_size))


def build_case_selection(
    inventory: dict[str, Any],
    sample_size: int,
    seed: int = c.SELECTION_SEED,
    *,
    study1_case_sha256: dict[str, str] | None = None,
) -> dict[str, Any]:
    eligible_ids = [row["case_id"] for row in inventory["eligible_cases"]]
    selected = select_cases(eligible_ids, sample_size, seed)
    by_id = {row["case_id"]: row for row in inventory["eligible_cases"]}
    overlap = {}
    if study1_case_sha256:
        reverse = {digest: cid for cid, digest in study1_case_sha256.items()}
        for cid in selected:
            digest = by_id[cid]["sha256"]
            if digest in reverse:
                overlap[cid] = reverse[digest]
    return {
        **inventory,
        "selection_rule": (
            "sorted(random.Random(seed).sample(sorted(eligible_case_ids), sample_size)); "
            "executed once before any provider output was observed; no substitution afterwards"
        ),
        "selection_seed": seed,
        "sample_size": sample_size,
        "selected_case_ids": selected,
        "excluded_case_ids": [cid for cid in eligible_ids if cid not in selected],
        "excluded_reason": "not drawn by the seeded sample under the frozen cost bound",
        "study1_overlap_by_digest": overlap,
        "selected_cases": [by_id[cid] for cid in selected],
    }


def load_case_inputs(runtime_root: Path, selection: dict[str, Any]) -> dict[str, Any]:
    """Read corpus bytes into memory after re-verifying every digest."""
    domain_path = runtime_root / selection["domain_description"]["relative_path"]
    if sha256_file(domain_path) != selection["domain_description"]["sha256"]:
        raise InventoryError("domain description digest mismatch at load time")
    cases = []
    for row in selection["selected_cases"]:
        path = runtime_root / row["relative_path"]
        if sha256_file(path) != row["sha256"]:
            raise InventoryError(f"case digest mismatch at load time: {row['case_id']}")
        cases.append({"case_id": row["case_id"], "case_model": path.read_text(encoding="utf-8")})
    return {
        "domain_description": domain_path.read_text(encoding="utf-8"),
        "case_models": cases,
        "case_input_hashes": {row["case_id"]: row["sha256"] for row in selection["selected_cases"]},
        "domain_description_sha256": selection["domain_description"]["sha256"],
    }
