"""Fail-closed, independent inventory of historical VEGO-AI model bytes.

The audit compares three separately enumerated units (local files, archive
members, and evaluation case identifiers).  A matching archive entry proves
only byte identity with that named archive; it does not prove historical-run
consumption or completeness of the historical corpus.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter, defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

AUDIT_VERSION = "historical-case-recovery-v2"
SETTING_DIRS = {
    "ucd_pw": "UCD_PW_models",
    "cd_pw": "CD_PW_models",
    "ucd_ch": "UCD_Ch_models",
    "cd_ch": "CD_Ch_models",
}
PAPER_HISTORICAL_COUNT = {"ucd_ch": 46, "cd_ch": 47, "ucd_pw": 44, "cd_pw": 41}
CASE_ID_RE = re.compile(r"^(?P<id>[^_]+)_")
EVAL_CASE_RE = re.compile(r"(?:agentC_)?case_(?P<id>[^.]+)\.json$")
SETTING_HINT_RE = re.compile(r"_(?P<setting>UCD_PW|CD_PW|UCD_Ch|CD_Ch)(?:\.[^.]+)?$", re.IGNORECASE)


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


def _case_id(filename: str) -> str:
    match = CASE_ID_RE.match(filename)
    return match.group("id") if match else Path(filename).stem


def _setting_hint(filename: str) -> str | None:
    match = SETTING_HINT_RE.search(Path(filename).stem)
    if not match:
        return None
    token = match.group("setting").lower()
    return next((setting for setting, directory in SETTING_DIRS.items() if directory.lower().replace("_models", "") == token.replace("_models", "")), None)


def _validate(data: bytes, setting_id: str, filename: str) -> str:
    if not data:
        return "EMPTY_MODEL"
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return "NON_UTF8_INPUT"
    if "@startuml" not in text or "@enduml" not in text:
        return "MISSING_PLANTUML_WRAPPER"
    hint = _setting_hint(filename)
    if hint is not None and hint != setting_id:
        return "SETTING_DIRECTORY_MISMATCH"
    return "VALID"


def _relative_model_files(repo_root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for _setting_id, setting_dir in SETTING_DIRS.items():
        root = repo_root / "VEGO-AI" / "models" / setting_dir
        if not root.is_dir():
            continue
        for path in sorted((p for p in root.iterdir() if p.is_file()), key=lambda p: p.name):
            result[(Path("VEGO-AI") / "models" / setting_dir / path.name).as_posix()] = path
    return result


def _archive_model_members(archive: Path) -> tuple[str, dict[str, bytes], list[str], int]:
    archive_hash = sha256_file(archive)
    members: dict[str, bytes] = {}
    duplicate_names: list[str] = []
    unrelated = 0
    with zipfile.ZipFile(archive, "r") as zf:
        names = zf.namelist()
        for name in names:
            normalized = name.replace("\\", "/")
            parts = normalized.split("/")
            is_model = len(parts) == 4 and parts[:2] == ["VEGO-AI", "models"] and parts[2] in SETTING_DIRS.values() and parts[3] and not normalized.endswith("/")
            if not is_model:
                if not normalized.endswith("/"):
                    unrelated += 1
                continue
            if normalized in members:
                duplicate_names.append(normalized)
                continue
            members[normalized] = zf.read(name)
    return archive_hash, members, sorted(duplicate_names), unrelated


def _evaluation_ids(repo_root: Path) -> dict[str, set[str]]:
    result = {setting: set() for setting in SETTING_DIRS}
    for setting_id in SETTING_DIRS:
        root = repo_root / "VEGO-AI" / "eval_output" / setting_id
        if not root.is_dir():
            continue
        for path in root.rglob("*.json"):
            match = EVAL_CASE_RE.search(path.name)
            if match:
                result[setting_id].add(match.group("id"))
    return result


def _setting_from_path(relative: str) -> str:
    parts = Path(relative).parts
    directory = parts[2] if len(parts) >= 4 else ""
    return next((setting for setting, value in SETTING_DIRS.items() if value == directory), "unknown")


def _expected_members(expected_universe: Mapping[str, list[str]] | None) -> set[str] | None:
    if expected_universe is None:
        return None
    return {path.replace("\\", "/") for paths in expected_universe.values() for path in paths}


def build_audit(
    repo_root: Path,
    archive: Path,
    *,
    expected_universe: Mapping[str, list[str]] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    archive_hash, archive_members, duplicate_archive_names, unrelated_archive_count = _archive_model_members(archive)
    local_members = _relative_model_files(repo_root)
    local_paths = set(local_members)
    archive_paths = set(archive_members)
    intersection = sorted(local_paths & archive_paths)
    archive_only = sorted(archive_paths - local_paths)
    local_only = sorted(local_paths - archive_paths)
    expected_paths = _expected_members(expected_universe)

    duplicate_case_ids: dict[str, list[str]] = defaultdict(list)
    content_slots: dict[str, list[str]] = defaultdict(list)
    rows: list[dict[str, Any]] = []

    for relative in sorted(local_paths | archive_paths):
        setting_id = _setting_from_path(relative)
        filename = Path(relative).name
        local_data = local_members[relative].read_bytes() if relative in local_members else None
        archive_data = archive_members.get(relative)
        selected = local_data if local_data is not None else archive_data
        local_hash = sha256_bytes(local_data) if local_data is not None else None
        archive_entry_hash = sha256_bytes(archive_data) if archive_data is not None else None
        byte_identical = local_data is not None and archive_data is not None and local_data == archive_data
        if relative in local_members and relative in archive_members:
            status = "RECOVERED_VERBATIM" if byte_identical else "BYTE_MISMATCH"
        elif relative in local_members:
            status = "LOCAL_ONLY"
        else:
            status = "ARCHIVE_ONLY"
        validation = _validate(selected or b"", setting_id, filename)
        case_id = _case_id(filename)
        if relative in local_members:
            duplicate_case_ids[f"{setting_id}:{case_id}"].append(f"{setting_id}:{filename}")
            content_slots[local_hash or ""].append(f"{setting_id}:{filename}")
        rows.append({
            "expected_case_slot": None,
            "historical_setting": setting_id,
            "historical_case_id": case_id,
            "provenance_status": status,
            "source_path": relative,
            "source_artifact_sha256": archive_hash if archive_data is not None else None,
            "source_entry_sha256": archive_entry_hash,
            "recovered_file_sha256": local_hash,
            "byte_identical": byte_identical,
            "byte_length": len(selected or b""),
            "encoding": "utf-8" if validation not in {"NON_UTF8_INPUT"} else "unknown",
            "validation_status": validation,
            "extraction_method": "zip-entry-byte-comparison" if archive_data is not None else "local-byte-inventory-only",
            "evidence_supporting_identity": [
                "named archive member is byte-identical to local file" if byte_identical else "archive/local membership was independently enumerated",
                "filename-derived case identifier is descriptive only",
            ],
            "ambiguity": "Archive byte identity does not prove historical-run consumption or slot identity.",
            "admissibility_pending_claude": True,
            "notes": "Metadata only; no model text is emitted.",
        })

    duplicate_case_ids = {key: sorted(value) for key, value in duplicate_case_ids.items() if len(value) > 1}
    duplicate_content = {key: sorted(value) for key, value in content_slots.items() if key and len(value) > 1}
    recovered_ids = {f"{_setting_from_path(path)}:{_case_id(Path(path).name)}" for path in intersection}
    eval_ids = {f"{setting}:{case}" for setting, cases in _evaluation_ids(repo_root).items() for case in cases}
    expected_minus_recovered = sorted((expected_paths or set()) - set(intersection)) if expected_paths is not None else []
    recovered_minus_expected = sorted(set(intersection) - (expected_paths or set())) if expected_paths is not None else []
    completeness = (
        "COMPLETENESS_UNRESOLVED" if expected_paths is None else
        "COMPLETE_EXPECTED_UNIVERSE_BUT_HISTORICAL_BINDING_UNPROVEN" if not expected_minus_recovered and not local_only and not archive_only else
        "INCOMPLETE_EXPECTED_UNIVERSE"
    )
    evaluation_ids_by_setting = _evaluation_ids(repo_root)
    per_setting: dict[str, dict[str, Any]] = {}
    for setting_id, _setting_dir in SETTING_DIRS.items():
        local_count = sum(_setting_from_path(path) == setting_id for path in local_paths)
        archive_count = sum(_setting_from_path(path) == setting_id for path in archive_paths)
        exact_count = sum(_setting_from_path(path) == setting_id for path in intersection)
        invalid_count = sum(row["validation_status"] != "VALID" and row["historical_setting"] == setting_id for row in rows)
        per_setting[setting_id] = {
            "documented_historical_count": PAPER_HISTORICAL_COUNT[setting_id],
            "observed_local_count": local_count,
            "observed_archive_member_count": archive_count,
            "byte_identical_intersection_count": exact_count,
            "evaluation_case_id_count": len(evaluation_ids_by_setting[setting_id]),
            "invalid_or_unsafe_record_count": invalid_count,
            "readiness": "NOT_EXECUTABLE_HISTORICAL_BINDING_UNRESOLVED",
        }
    inventory = {
        "audit_version": AUDIT_VERSION,
        "archive_sha256": archive_hash,
        "archive_relative_name": archive.name,
        "observed_local_count": len(local_paths),
        "archive_model_member_count": len(archive_paths),
        "unrelated_archive_member_count": unrelated_archive_count,
        "duplicate_archive_member_names": duplicate_archive_names,
        "raw_model_inventory": {"total": len(local_paths), "per_setting": per_setting, "source": "ignored local model inventory"},
        "archive_inventory": {"total": len(archive_paths), "source": "all archive members under VEGO-AI/models/<setting-directory>"},
        "configuration_evaluation_inventory": {
            "configuration_case_ids": [],
            "configuration_source": "No independent configuration-bound case-ID manifest was supplied",
            "evaluation_case_ids_total": len(eval_ids),
            "per_setting": {setting: sorted(cases) for setting, cases in evaluation_ids_by_setting.items()},
        },
        "set_differences": {
            "archive_intersection_local": intersection,
            "archive_minus_local": archive_only,
            "local_minus_archive": local_only,
            "expected_minus_recovered": expected_minus_recovered,
            "recovered_minus_expected": recovered_minus_expected,
            "evaluation_ids_minus_recovered_ids": sorted(eval_ids - recovered_ids),
            "recovered_ids_minus_evaluation_ids": sorted(recovered_ids - eval_ids),
        },
        "duplicate_case_ids": duplicate_case_ids,
        "duplicate_content_groups": duplicate_content,
        "duplicate_content_group_count": len(duplicate_content),
        "provenance_counts": dict(Counter(row["provenance_status"] for row in rows)),
        "paper_historical_count": {"count": 178, "per_setting": PAPER_HISTORICAL_COUNT, "unit": "documented aggregate records; not file identity"},
        "current_scored_row_count": {"count": 179, "unit": "scored evaluation rows; not raw model-file count"},
        "completeness_verdict": completeness,
        "historical_executability": "NOT_EXECUTABLE",
        "scientifically_admissible_settings": [],
        "interpretation": "RECOVERED_VERBATIM is limited to byte identity with the named archive entry. No historical-run, expected-universe, or supervisor binding is inferred.",
        "provider_calls": 0,
        "synthetic_models_generated": 0,
    }
    return inventory, rows


def write_outputs(
    repo_root: Path,
    output_root: Path,
    archive: Path,
    *,
    expected_universe: Mapping[str, list[str]] | None = None,
) -> dict[str, Any]:
    inventory, manifest = build_audit(repo_root, archive, expected_universe=expected_universe)
    output_root.mkdir(parents=True, exist_ok=True)
    manifest_hash = sha256_bytes(canonical_json(manifest).encode("utf-8"))
    missingness = {
        "audit_version": AUDIT_VERSION,
        "expected_inventory_unit": "independently enumerated members; no local count is called expected",
        "observed_local_count": inventory["observed_local_count"],
        "archive_model_member_count": inventory["archive_model_member_count"],
        "set_differences": inventory["set_differences"],
        "completeness_verdict": inventory["completeness_verdict"],
        "historical_executability": inventory["historical_executability"],
        "interpretation": inventory["interpretation"],
    }
    receipt = {
        "audit_version": AUDIT_VERSION,
        "archive_sha256": inventory["archive_sha256"],
        "manifest_sha256": manifest_hash,
        "observed_local_count": inventory["observed_local_count"],
        "archive_model_member_count": inventory["archive_model_member_count"],
        "provider_calls": 0,
        "synthetic_models_generated": 0,
        "content_emitted": False,
        "completeness_verdict": inventory["completeness_verdict"],
    }
    files = {
        "expected-case-inventory.json": inventory,
        "provenance-manifest.json": manifest,
        "missingness-report.json": missingness,
        "recovery-evidence-receipt.json": receipt,
    }
    for name, value in files.items():
        (output_root / name).write_text(canonical_json(value), encoding="utf-8")
    return {"inventory": inventory, "manifest": manifest, "manifest_sha256": manifest_hash, "receipt": receipt}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("docs/research/phd-proposal/historical-case-recovery-v2"))
    parser.add_argument("--expected-universe", type=Path, help="Optional JSON mapping setting IDs to independently documented member paths")
    args = parser.parse_args()
    expected = json.loads(args.expected_universe.read_text(encoding="utf-8")) if args.expected_universe else None
    result = write_outputs(args.repo_root.resolve(), args.output_root.resolve(), args.archive.resolve(), expected_universe=expected)
    print(json.dumps(result["receipt"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
