"""Fail-closed AirTravel case-selection provenance.

The inventory contains a deterministic eligibility predicate, but it does not
identify which four of the eligible candidates were selected for the N=4 run.
This module therefore makes that limitation machine-readable instead of
turning a narrative choice into a false reproducible sampling rule.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

CASE_HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
DEFAULT_PROPOSAL = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "research"
    / "phd-proposal"
    / "text2uml-airtravel"
    / "candidate-subset-proposal.json"
)


def _eligible_file(row: Mapping[str, Any]) -> bool:
    """The only inventory-level eligibility predicate used by this package."""

    return (
        row.get("classification") == "GENERATED_CANDIDATE_MODEL"
        and str(row.get("path", "")).startswith("result_one_")
        and int(row.get("bytes", 0) or 0) > 0
        and row.get("syntax_validation") == "WRAPPER_PRESENT"
        and bool(CASE_HASH_RE.fullmatch(str(row.get("sha256", ""))))
    )


def _load_recorded_selection(path: Path = DEFAULT_PROPOSAL) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    rows = payload.get("candidates")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _explicit_cases(payload: Mapping[str, Any]) -> Sequence[Mapping[str, Any]] | None:
    rows = payload.get("cases")
    if not isinstance(rows, list):
        rows = payload.get("case_models")
    if not isinstance(rows, list):
        return None
    return [row for row in rows if isinstance(row, Mapping)]


def select_airtravel_cases(
    inventory: Mapping[str, Any],
    *,
    target_count: int = 4,
    recorded_selection: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return a deterministic selection result or an explicit limitation.

    A ``cases``/``case_models`` array with valid hashes, eligibility and an
    explicit ``selection_rank`` is sufficient to produce a deterministic
    selection.  The pinned ``airtravel-inventory.json`` instead contains only a
    file manifest, so its 21 eligible rows cannot identify the four recorded
    cases.  The optional proposal is carried as a *recorded purposive choice*,
    never as evidence that the predicate selected those rows.
    """

    explicit = _explicit_cases(inventory)
    predicate = (
        "eligible iff classification=GENERATED_CANDIDATE_MODEL, path starts "
        "result_one_, bytes>0, syntax_validation=WRAPPER_PRESENT, and sha256 is 64 hex"
    )
    if explicit is not None:
        valid = [
            row
            for row in explicit
            if row.get("eligible") is True
            and CASE_HASH_RE.fullmatch(str(row.get("case_hash", "")))
            and isinstance(row.get("selection_rank"), int)
        ]
        ranks = [int(row["selection_rank"]) for row in valid]
        if len(valid) == target_count and len(set(ranks)) == target_count:
            ordered = sorted(valid, key=lambda row: (int(row["selection_rank"]), str(row["case_hash"])))
            return {
                "status": "DETERMINISTIC_PREDICATE",
                "predicate": predicate,
                "eligible_case_count": len(valid),
                "eligible_case_hashes": [str(row["case_hash"]).lower() for row in ordered],
                "selected_case_hashes": [str(row["case_hash"]).lower() for row in ordered],
                "selected_case_paths": [str(row.get("path", "")) for row in ordered],
                "selection_basis": "explicit_case_metadata_and_selection_rank",
                "reason": "Inventory supplies exactly the target number of ranked eligible cases.",
            }

    files = inventory.get("files")
    rows = [row for row in files if isinstance(row, Mapping) and _eligible_file(row)] if isinstance(files, list) else []
    eligible_hashes = [str(row["sha256"]).lower() for row in rows]
    chosen_rows = list(recorded_selection) if recorded_selection is not None else _load_recorded_selection()
    chosen_hashes = [str(row.get("sha256", "")).lower() for row in chosen_rows if CASE_HASH_RE.fullmatch(str(row.get("sha256", "")))]
    chosen_paths = [str(row.get("path")) for row in chosen_rows if row.get("path")]
    return {
        "status": "PURPOSIVE_NON_REPRODUCIBLE",
        "predicate": predicate,
        "eligible_case_count": len(rows),
        "eligible_case_hashes": eligible_hashes,
        "selected_case_hashes": chosen_hashes,
        "selected_case_paths": chosen_paths,
        "selection_basis": "recorded_purposive_choice_not_derived_by_predicate",
        "reason": (
            f"Inventory predicate identifies {len(rows)} eligible cases; it does not contain "
            f"case-level ranking/selection metadata for the four selected cases. The four-case "
            f"choice is therefore purposive and non-reproducible among {len(rows)} eligible cases."
        ),
    }


def load_airtravel_selection(
    inventory_path: Path,
    *,
    proposal_path: Path = DEFAULT_PROPOSAL,
) -> dict[str, Any]:
    """Load an inventory and its recorded proposal without reading model bytes."""

    if not inventory_path.is_file():
        return {
            "status": "INVENTORY_UNAVAILABLE",
            "predicate": "inventory file is required",
            "eligible_case_count": "NOT_AVAILABLE",
            "eligible_case_hashes": [],
            "selected_case_hashes": [],
            "reason": "airtravel-inventory.json is unavailable",
        }
    try:
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "INVENTORY_INVALID",
            "predicate": "inventory file is required",
            "eligible_case_count": "NOT_AVAILABLE",
            "eligible_case_hashes": [],
            "selected_case_hashes": [],
            "reason": f"inventory cannot be parsed: {type(exc).__name__}",
        }
    recorded = _load_recorded_selection(proposal_path)
    return select_airtravel_cases(inventory, recorded_selection=recorded)
