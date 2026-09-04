"""Fail-closed slot audit for the historical Cheers/ParkWise corpus.

The paper's per-setting counts establish an ordinal expected-slot universe, but
do not identify which local file belongs to which historical slot.  This module
therefore keeps expected slots and discovered byte candidates as separate
records.  It never generates models or emits model content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

AUDIT_VERSION = "historical-slot-audit-v2"
SEARCH_DATE = "2026-09-04"
PAPER_EXPECTED = {"ucd_pw": 44, "cd_pw": 41, "ucd_ch": 46, "cd_ch": 47}
SETTING_DIRS = {
    "ucd_pw": "UCD_PW_models",
    "cd_pw": "CD_PW_models",
    "ucd_ch": "UCD_Ch_models",
    "cd_ch": "CD_Ch_models",
}
CASE_ID_RE = re.compile(r"^(?P<id>[^_]+)_")
SEARCH_SCOPE = [
    "VEGO-AI/models/<setting-directory>",
    "VEGO-AI/eval_output/<setting-id>",
    "VEGO-AI-20260611T112722Z-3-001.zip (all members)",
    "docs/research/governance/vego-ai-foundation-paper-record.md",
    "docs/agent-memory/issues.md (ISS-041)",
    "study1/synthetic-corpus worktree metadata only",
]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _case_id(name: str) -> str:
    match = CASE_ID_RE.match(name)
    return match.group("id") if match else Path(name).stem


def _encoding(path: Path) -> str:
    try:
        path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return "unknown"
    return "utf-8"


def _worktree_for_branch(repo_root: Path, branch: str) -> Path | None:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(repo_root), "worktree", "list", "--porcelain"],
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    blocks = output.split("\n\n")
    needle = f"branch refs/heads/{branch}"
    for block in blocks:
        if needle in block:
            first = next((line for line in block.splitlines() if line.startswith("worktree ")), "")
            if first:
                return Path(first.removeprefix("worktree "))
    return None


def _git_blob(repo_root: Path, branch: str, path: str) -> str | None:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", f"{branch}:{path}"],
            text=True,
            encoding="utf-8",
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return output.strip()


def _archive_member_hashes(archive: Path) -> tuple[str, dict[str, tuple[int, str]]]:
    import zipfile

    archive_hash = _file_sha256(archive)
    members: dict[str, tuple[int, str]] = {}
    with zipfile.ZipFile(archive, "r") as zf:
        for name in zf.namelist():
            if name.startswith("VEGO-AI/models/") and not name.endswith("/"):
                with zf.open(name, "r") as handle:
                    data = handle.read()
                members[name] = (len(data), _sha256(data))
    return archive_hash, members


def audit(repo_root: Path, archive: Path, synthetic_branch: str = "study1/synthetic-corpus") -> dict[str, Any]:
    archive_hash, archive_members = _archive_member_hashes(archive)
    expected_slots: list[dict[str, Any]] = []
    discovered_files: list[dict[str, Any]] = []
    per_setting: dict[str, dict[str, Any]] = {}
    for setting_id, directory in SETTING_DIRS.items():
        expected_count = PAPER_EXPECTED[setting_id]
        for index in range(1, expected_count + 1):
            expected_slots.append({
                "record_type": "expected_slot",
                "setting": setting_id,
                "expected_case_slot": f"{setting_id}-paper-{index:04d}",
                "authoritative_expectation_source": "docs/research/governance/vego-ai-foundation-paper-record.md § evaluation",
                "provenance_status": "NOT_YET_SEARCHED",
                "discovered_path": None,
                "source_artifact_sha256": None,
                "recovered_file_sha256": None,
                "byte_size": None,
                "provenance_source": "paper per-setting count; slot identity not supplied",
                "verification_evidence": "Ordinal slot is established by the paper count only; no file-to-slot identity is asserted.",
                "search_scope": SEARCH_SCOPE,
                "search_date": SEARCH_DATE,
                "synthesis_eligibility": "NO",
                "ambiguity": "Expected existence is known, but historical file identity/content is not mapped.",
                "admissibility_pending_claude": True,
            })
        local_root = repo_root / "VEGO-AI" / "models" / directory
        files = sorted((p for p in local_root.iterdir() if p.is_file()), key=lambda p: p.name) if local_root.is_dir() else []
        rows: list[dict[str, Any]] = []
        for path in files:
            relative = (Path("VEGO-AI") / "models" / directory / path.name).as_posix()
            data_hash = _file_sha256(path)
            entry = archive_members.get(relative)
            exact = entry is not None and entry[1] == data_hash and entry[0] == path.stat().st_size
            status = "RECOVERY_CANDIDATE_UNVERIFIED" if exact else "PARTIAL_RECOVERY"
            row = {
                "record_type": "discovered_file",
                "setting": setting_id,
                "expected_case_slot": None,
                "historical_case_id": _case_id(path.name),
                "authoritative_expectation_source": None,
                "provenance_status": status,
                "discovered_path": relative,
                "source_artifact_sha256": archive_hash if entry else None,
                "source_entry_sha256": entry[1] if entry else None,
                "recovered_file_sha256": data_hash,
                "byte_size": path.stat().st_size,
                "encoding": _encoding(path),
                "provenance_source": "local ignored inventory + supplied archive" if entry else "local ignored inventory only",
                "verification_evidence": "Byte-identical archive member; historical evaluated-set binding is not independently signed." if exact else "No byte-identical archive member; do not use.",
                "search_scope": SEARCH_SCOPE,
                "search_date": SEARCH_DATE,
                "synthesis_eligibility": "NO",
                "ambiguity": "Candidate is not assigned to an authoritative paper slot.",
                "admissibility_pending_claude": True,
            }
            rows.append(row)
            discovered_files.append(row)
        per_setting[setting_id] = {
            "authoritative_expected_slot_count": expected_count,
            "discovered_file_count": len(rows),
            "recovery_candidate_unverified_count": sum(r["provenance_status"] == "RECOVERY_CANDIDATE_UNVERIFIED" for r in rows),
            "partial_recovery_count": sum(r["provenance_status"] == "PARTIAL_RECOVERY" for r in rows),
            "searched_not_found_within_declared_scope_count": 0,
            "not_yet_searched_slot_count": expected_count,
            "expected_slot_universe_status": "ESTABLISHED_BY_AUTHORITATIVE_COUNT; IDENTITY_MAPPING_OPEN",
            "synthesis_eligible_count": 0,
        }

    synthetic_root = _worktree_for_branch(repo_root, synthetic_branch)
    quarantine: list[dict[str, Any]] = []
    if synthetic_root:
        root = synthetic_root / "Dataset1_ModelEval_SYNTHETIC"
        for path in sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.as_posix()) if root.is_dir() else []:
            quarantine.append({
                "relative_path": path.relative_to(synthetic_root).as_posix(),
                "sha256": _file_sha256(path),
                "byte_size": path.stat().st_size,
                "provenance_status": "QUARANTINED_UNADJUDICATED_SYNTHETIC",
                "synthesis_eligibility": "NO",
                "source_branch": synthetic_branch,
                "content_inspected": False,
                "notes": "Metadata only; do not merge, rename, delete, execute, or use.",
            })
    else:
        for path in ("Dataset1_ModelEval_SYNTHETIC/SYNTHETIC_DATASET_MANIFEST.json", "Dataset1_ModelEval_SYNTHETIC/SYNTHETIC_FILE_HASHES.csv"):
            blob = _git_blob(repo_root, synthetic_branch, path)
            if blob:
                quarantine.append({
                    "relative_path": path,
                    "blob_sha": blob,
                    "provenance_status": "QUARANTINED_UNADJUDICATED_SYNTHETIC",
                    "synthesis_eligibility": "NO",
                    "source_branch": synthetic_branch,
                    "content_inspected": False,
                })

    return {
        "audit_version": AUDIT_VERSION,
        "audit_date": SEARCH_DATE,
        "archive_sha256": archive_hash,
        "expected_slot_records": expected_slots,
        "discovered_file_records": discovered_files,
        "per_setting": per_setting,
        "aggregate": {
            "authoritative_expected_slots": sum(PAPER_EXPECTED.values()),
            "discovered_files": len(discovered_files),
            "recovery_candidate_unverified": sum(r["provenance_status"] == "RECOVERY_CANDIDATE_UNVERIFIED" for r in discovered_files),
            "partial_recovery": sum(r["provenance_status"] == "PARTIAL_RECOVERY" for r in discovered_files),
            "searched_not_found_within_declared_scope": 0,
            "not_yet_searched": len(expected_slots),
            "synthesis_eligible": 0,
        },
        "search_scope": SEARCH_SCOPE,
        "slot_identity_rule": "Counts establish ordinal expected slots; a discovered file is not assigned to a slot without authoritative identity evidence.",
        "synthetic_quarantine": {
            "branch": synthetic_branch,
            "records": quarantine,
            "record_count": len(quarantine),
            "raw_content_inspected": False,
        },
        "provider_calls": 0,
        "synthetic_generation": 0,
    }


def write_outputs(repo_root: Path, archive: Path, output_root: Path, synthetic_branch: str = "study1/synthetic-corpus") -> dict[str, Any]:
    result = audit(repo_root.resolve(), archive.resolve(), synthetic_branch)
    output_root.mkdir(parents=True, exist_ok=True)
    slot_report = {
        "audit_version": result["audit_version"],
        "audit_date": result["audit_date"],
        "archive_sha256": result["archive_sha256"],
        "search_scope": result["search_scope"],
        "slot_identity_rule": result["slot_identity_rule"],
        "per_setting": result["per_setting"],
        "aggregate": result["aggregate"],
        "expected_slot_records": result["expected_slot_records"],
        "discovered_file_records": result["discovered_file_records"],
    }
    quarantine = result["synthetic_quarantine"]
    scope = {
        "audit_version": result["audit_version"],
        "audit_date": result["audit_date"],
        "historical_expected_count": result["aggregate"]["authoritative_expected_slots"],
        "raw_discovered_count": result["aggregate"]["discovered_files"],
        "scoped_not_found_count": result["aggregate"]["searched_not_found_within_declared_scope"],
        "not_yet_searched_count": result["aggregate"]["not_yet_searched"],
        "synthesis_eligible_count": result["aggregate"]["synthesis_eligible"],
        "search_closed": False,
        "search_closure_owner": "human owner / Claude review required",
        "interpretation": "No slot is eligible for gap-fill until identity is established, the declared scope is closed, and the owner accepts closure.",
    }
    (output_root / "historical-recovery-slot-audit.json").write_text(_canonical(slot_report), encoding="utf-8")
    (output_root / "synthetic-branch-quarantine.json").write_text(_canonical(quarantine), encoding="utf-8")
    (output_root / "recovery-scope-report.json").write_text(_canonical(scope), encoding="utf-8")
    return {"slot_report": slot_report, "quarantine": quarantine, "scope": scope}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("docs/research/phd-proposal/historical-case-recovery-v2"))
    parser.add_argument("--synthetic-branch", default="study1/synthetic-corpus")
    args = parser.parse_args()
    result = write_outputs(args.repo_root, args.archive, args.output_root, args.synthetic_branch)
    print(json.dumps({"aggregate": result["slot_report"]["aggregate"], "quarantine_count": result["quarantine"]["record_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
