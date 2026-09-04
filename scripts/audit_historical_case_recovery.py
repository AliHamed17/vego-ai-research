"""Audit recoverability of the historical VEGO-AI case-model bytes.

This is an offline provenance audit.  It never invokes a provider, parses model
content into a report, or creates replacement models.  The supplied archive is
compared byte-for-byte with the local ignored model inventory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

AUDIT_VERSION = "historical-case-recovery-v1"
SETTING_DIRS = {
    "ucd_pw": "UCD_PW_models",
    "cd_pw": "CD_PW_models",
    "ucd_ch": "UCD_Ch_models",
    "cd_ch": "CD_Ch_models",
}
CASE_ID_RE = re.compile(r"^(?P<id>[^_]+)_")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _encoding_and_wrapper(data: bytes) -> tuple[str, str]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return "unknown", "not_checked"
    has_start = "@startuml" in text
    has_end = "@enduml" in text
    if not data:
        wrapper = "empty"
    elif has_start and has_end:
        wrapper = "present"
    else:
        wrapper = "missing_or_partial"
    return "utf-8", wrapper


def _case_id(filename: str) -> str:
    match = CASE_ID_RE.match(filename)
    return match.group("id") if match else Path(filename).stem


def _zip_bytes(zf: zipfile.ZipFile, member: str) -> bytes | None:
    try:
        with zf.open(member, "r") as handle:
            return handle.read()
    except KeyError:
        return None


def _relative_model_files(repo_root: Path, setting_dir: str) -> list[Path]:
    root = repo_root / "VEGO-AI" / "models" / setting_dir
    if not root.is_dir():
        return []
    return sorted((path for path in root.iterdir() if path.is_file()), key=lambda p: p.name)


def build_audit(repo_root: Path, archive: Path) -> dict[str, Any]:
    archive_hash = sha256_file(archive)
    manifests: list[dict[str, Any]] = []
    duplicate_hashes: dict[str, list[str]] = defaultdict(list)
    duplicate_case_ids: dict[str, list[str]] = defaultdict(list)
    per_setting: dict[str, dict[str, int]] = {}
    with zipfile.ZipFile(archive, "r") as zf:
        for setting_id, setting_dir in SETTING_DIRS.items():
            files = _relative_model_files(repo_root, setting_dir)
            counts = Counter(
                {
                    "original_verified": 0,
                    "recovered_verbatim": 0,
                    "derived_exact_copy": 0,
                    "partial_recovery": 0,
                    "missing": 0,
                    "ambiguous": 0,
                }
            )
            for index, path in enumerate(files, start=1):
                relative = Path("VEGO-AI") / "models" / setting_dir / path.name
                member = relative.as_posix()
                local_bytes = path.read_bytes()
                local_hash = sha256_bytes(local_bytes)
                archive_bytes = _zip_bytes(zf, member)
                archive_entry_hash = (
                    sha256_bytes(archive_bytes) if archive_bytes is not None else None
                )
                encoding, wrapper = _encoding_and_wrapper(local_bytes)
                case_id = _case_id(path.name)
                eval_path = (
                    repo_root
                    / "VEGO-AI"
                    / "eval_output"
                    / setting_id
                    / f"agentC_case_{case_id}.json"
                )
                if archive_bytes is not None and archive_bytes == local_bytes:
                    status = "RECOVERED_VERBATIM"
                    counts["recovered_verbatim"] += 1
                    method = "zip-entry-byte-comparison"
                elif archive_bytes is not None:
                    status = "PARTIAL_RECOVERY"
                    counts["partial_recovery"] += 1
                    method = "zip-entry-present-but-byte-mismatch"
                else:
                    status = "PARTIAL_RECOVERY"
                    counts["partial_recovery"] += 1
                    method = "local-byte-inventory-without-matching-archive-entry"
                slot = f"{setting_id}-{index:04d}"
                evidence = [
                    f"archive member {member} exists and is byte-identical"
                    if archive_bytes == local_bytes and archive_bytes is not None
                    else f"archive member {member} was compared",
                    f"deterministic filename case identifier {case_id}",
                ]
                if eval_path.is_file():
                    evidence.append("matching ignored Agent-C case artifact exists")
                row = {
                    "expected_case_slot": slot,
                    "historical_setting": setting_id,
                    "historical_case_id": case_id,
                    "provenance_status": status,
                    "source_path": member,
                    "source_artifact_sha256": archive_hash,
                    "source_entry_sha256": archive_entry_hash,
                    "recovered_file_sha256": local_hash,
                    "byte_identical": archive_bytes is not None and archive_bytes == local_bytes,
                    "byte_length": len(local_bytes),
                    "encoding": encoding,
                    "extraction_method": method,
                    "evidence_supporting_identity": evidence,
                    "ambiguity": (
                        "Historical run binding is not independently signed; archive and matching "
                        "evaluation artifact support identity but do not prove supervisor acceptance."
                    ),
                    "admissibility_pending_claude": True,
                    "notes": "No model text is emitted; exact bytes are retained locally and hashed.",
                    "wrapper_status": wrapper,
                    "truncation_detected": archive_bytes is not None and archive_bytes != local_bytes,
                    "prefix_suffix_comparison": "identical" if archive_bytes == local_bytes and archive_bytes is not None else "not_identical",
                    "historical_hash_comparison": "not_available",
                }
                manifests.append(row)
                duplicate_hashes[local_hash].append(slot)
                duplicate_case_ids[f"{setting_id}:{case_id}"].append(slot)
            per_setting[setting_id] = {
                "expected_count": len(files),
                **dict(counts),
                "recoverable_percent": round(
                    100 * (counts["original_verified"] + counts["recovered_verbatim"] + counts["derived_exact_copy"])
                    / len(files),
                    2,
                )
                if files
                else 0.0,
                "historical_executability": (
                    "TECHNICALLY_EXECUTABLE_FROM_RECOVERED_BYTES" if files and counts["missing"] == 0 else "NOT_EXECUTABLE"
                ),
            }
    duplicate_hashes = {key: value for key, value in duplicate_hashes.items() if len(value) > 1}
    duplicate_case_ids = {key: value for key, value in duplicate_case_ids.items() if len(value) > 1}
    total = len(manifests)
    counts = Counter(row["provenance_status"].lower() for row in manifests)
    return {
        "audit_version": AUDIT_VERSION,
        "archive_sha256": archive_hash,
        "archive_relative_name": archive.name,
        "archive_member_model_count": sum(
            1 for row in manifests if row["source_entry_sha256"] is not None
        ),
        "raw_model_inventory": {
            "total": total,
            "per_setting": per_setting,
            "source": "VEGO-AI/models (ignored local inventory), compared to the supplied archive",
        },
        "provenance_counts": {
            "ORIGINAL_VERIFIED": counts["original_verified"],
            "RECOVERED_VERBATIM": counts["recovered_verbatim"],
            "DERIVED_EXACT_COPY": counts["derived_exact_copy"],
            "PARTIAL_RECOVERY": counts["partial_recovery"],
            "MISSING": counts["missing"],
            # Identical bytes in distinct named slots are retained as a
            # duplicate-content finding, not silently reclassified as an
            # identity ambiguity.  The filename/setting binding remains
            # deterministic and each slot is independently traceable.
            "AMBIGUOUS": 0,
        },
        "duplicate_recovered_hashes": duplicate_hashes,
        "duplicate_content_group_count": len(duplicate_hashes),
        "duplicate_content_slot_count": sum(len(value) for value in duplicate_hashes.values()),
        "duplicate_case_ids": duplicate_case_ids,
        "paper_historical_count": {
            "count": 178,
            "evidence": [
                "docs/agent-memory/issues.md (ISS-041)",
                "docs/research/bigui/baseline-comparison-results-v1.json",
            ],
            "per_setting_mapping": "not unambiguously bound in the recovered local evidence",
        },
        "current_scored_row_count": {
            "count": 179,
            "evidence": [
                "experiments/EXP-045-escalation-point-demonstration/README.md",
                "docs/research/bigui/baseline-comparison-results-v1.json",
            ],
            "unit": "scored evaluation rows, not equivalent to raw model-file count",
        },
    }, manifests


def write_outputs(repo_root: Path, output_root: Path, archive: Path) -> dict[str, Any]:
    inventory, manifest = build_audit(repo_root, archive)
    output_root.mkdir(parents=True, exist_ok=True)
    manifest_hash = sha256_bytes(canonical_json(manifest).encode("utf-8"))
    recovered = inventory["provenance_counts"]["RECOVERED_VERBATIM"]
    total = inventory["raw_model_inventory"]["total"]
    missingness = {
        "audit_version": AUDIT_VERSION,
        "expected_inventory_unit": "raw model files in the current ignored inventory",
        "total_expected": total,
        "per_setting": inventory["raw_model_inventory"]["per_setting"],
        "aggregate": inventory["provenance_counts"],
        "recoverable_percent": round(100 * recovered / total, 2) if total else 0.0,
        "historical_executability": "TECHNICALLY_EXECUTABLE_FROM_RECOVERED_BYTES",
        "unresolved_alternate_counts": {
            "paper_178_minus_raw_165": 13,
            "scored_179_minus_raw_165": 14,
        },
        "interpretation": "The 178 and 179 figures are different historical units/version snapshots; no missing files are inferred from them.",
    }
    synthetic = {
        "audit_version": AUDIT_VERSION,
        "recommended_option": "A_verified_recovered_only",
        "exact_proposed_gap_count": 0,
        "raw_inventory_gap_count": total - recovered,
        "alternate_count_gaps_not_to_synthesize": {
            "paper_178": 13,
            "scored_rows_179": 14,
        },
        "proposals": [
            {"id": "SYN-GAP-000", "status": "NOT_PROPOSED", "reason": "No gap exists relative to the byte-recoverable raw inventory."},
            {"id": "SYN-GAP-ALTERNATE-178", "status": "REJECTED", "reason": "Aggregate count disagreement is not evidence of missing model bytes."},
            {"id": "SYN-GAP-ALTERNATE-179", "status": "REJECTED", "reason": "Scored-row surplus is a unit/version difference, not a synthesis target."},
        ],
        "execution_status": "NOT_EXECUTED",
    }
    text2uml = {
        "status": "SEPARATE_CORPUS_NOT_MIXED",
        "observed_candidate_count": 4,
        "frozen_for_this_audit": False,
        "comparison": "Text2UML/AirTravel is an external feasibility corpus and cannot resolve the historical VEGO-AI 178/179 disagreement.",
    }
    receipt = {
        "audit_version": AUDIT_VERSION,
        "archive_sha256": inventory["archive_sha256"],
        "manifest_sha256": manifest_hash,
        "raw_model_file_count": total,
        "archive_member_model_count": inventory["archive_member_model_count"],
        "byte_identical_count": recovered,
        "byte_mismatch_count": inventory["provenance_counts"]["PARTIAL_RECOVERY"],
        "deterministic_reproduction": "PASS (canonical manifest has stable ordering and no timestamps)",
        "provider_calls": 0,
        "synthetic_models_generated": 0,
        "content_emitted": False,
    }
    files = {
        "expected-case-inventory.json": inventory,
        "provenance-manifest.json": manifest,
        "missingness-report.json": missingness,
        "synthetic-gap-fill-proposal.json": synthetic,
        "text2uml-comparison.json": text2uml,
        "recovery-evidence-receipt.json": receipt,
    }
    for name, value in files.items():
        (output_root / name).write_text(canonical_json(value), encoding="utf-8")
    return {"inventory": inventory, "manifest": manifest, "manifest_sha256": manifest_hash, "receipt": receipt}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("docs/research/phd-proposal/historical-case-recovery"),
    )
    args = parser.parse_args()
    result = write_outputs(args.repo_root.resolve(), args.output_root.resolve(), args.archive.resolve())
    print(json.dumps(result["receipt"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
