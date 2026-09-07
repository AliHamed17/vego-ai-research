#!/usr/bin/env python3
"""Build the evidence-first Study 1 data/log/pattern transparency package.

The builder deliberately separates public source verification from private run
evidence.  Public source metadata can be reproduced from a temporary download;
private prompts, answers, event logs and run outputs are never read or copied
unless a future caller explicitly supplies a validated binding manifest.  In
the current reviewed worktree no such private accepted-run binding is mounted,
so all scientific aggregates are emitted as ``NOT_AVAILABLE_IN_WORKTREE``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import zipfile
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Any

from study1_case_selection import load_airtravel_selection
from study1_signal_contract import S6_OPERATIONAL_DEFINITION

ROOT = Path(__file__).resolve().parents[1]
NOT_AVAILABLE = "NOT_AVAILABLE_IN_WORKTREE"
AVAILABLE = "AVAILABLE_VERIFIED"
PUBLIC_RELEASE = "v2.1.5.3"
PUBLIC_RELEASE_REPOSITORY = "https://github.com/ieiris/VEGO-AI"
PUBLIC_RELEASE_URL = f"{PUBLIC_RELEASE_REPOSITORY}/releases/tag/{PUBLIC_RELEASE}"
PUBLIC_RELEASE_ARCHIVE_URL = (
    f"https://github.com/ieiris/VEGO-AI/archive/refs/tags/{PUBLIC_RELEASE}.zip"
)
PUBLIC_RELEASE_ARCHIVE_SHA256 = "f7c2f62c927f280c25ecfaec667515e6a8ef8ad8a4104f168f27a1401b4f98b6"
PUBLIC_RELEASE_COMMIT = "f7457cf1a8e7d2e6f6bdbb9991a47abf7e14e495"
AIRTRAVEL_ARCHIVE_URL = (
    "https://github.com/IlKaiser/text2uml/archive/"
    "253b26dc704d523209a5cba79686f8f7fab57d63.zip"
)
AIRTRAVEL_ARCHIVE_SHA256 = "8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701"
AIRTRAVEL_UPSTREAM_COMMIT = "253b26dc704d523209a5cba79686f8f7fab57d63"
AIRTRAVEL_CORPUS_ID = "text2uml_airtravel_253b26dc"
AIRTRAVEL_SETTING_ID = "cd_airtravel"
SOURCE_MANIFEST = ROOT / "docs" / "research" / "phd-proposal" / "text2uml-airtravel" / "source-manifest.json"
AIRTRAVEL_INVENTORY = ROOT / "docs" / "research" / "phd-proposal" / "text2uml-airtravel" / "airtravel-inventory.json"
DETECTOR_SOURCE = ROOT / "scripts" / "extract_qa_escalation_features.py"

AIRTRAVEL_RUNTIME_FILES = [
    {
        "path": "domain_description/description.md",
        "bytes": 1477,
        "sha256": "96bc8a6fbf2c2fdd93592fdbf6fac7c2b9db403494fe2d5a45e0a2bcbf0167e2",
        "role": "domain_description",
    },
    {
        "path": "candidate_models/01_result_one_claude-sonnet-4-6.txt",
        "bytes": 1248,
        "sha256": "240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91",
        "role": "candidate_model",
    },
    {
        "path": "candidate_models/02_result_one_codestral-2508.txt",
        "bytes": 1272,
        "sha256": "08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6",
        "role": "candidate_model",
    },
    {
        "path": "candidate_models/03_result_one_deepseek-chat.txt",
        "bytes": 1324,
        "sha256": "ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a",
        "role": "candidate_model",
    },
    {
        "path": "candidate_models/04_result_one_gemini-2.5-flash.txt",
        "bytes": 1231,
        "sha256": "1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a",
        "role": "candidate_model",
    },
]
PROVENANCE_SCHEMA = ROOT / "schemas" / "study1-data-provenance-v1.schema.json"

RELEASE_SOURCE_FILES = [
    {"path": "GUI/Controller/action_logger.py", "bytes": 7907, "sha256": "00c3b1556294122ffc51df1ad41e2bfa1e7a7c893276172f8d8232d84253af75"},
    {"path": "GUI/View/GUI_Common.py", "bytes": 9701, "sha256": "baae722c100a4b2d8e7b8bddf72da55719e2d7406e027a724cf005525df2debd"},
    {"path": "framework/llm_client.py", "bytes": 9769, "sha256": "0abf4d3b04449aeb4502bdb02fdbfcf0d0890410b040922ac0483a220420ed05"},
    {"path": "framework/orchestrator.py", "bytes": 30340, "sha256": "cefd98a97f6616ab056dd444920dae99a658cd3d5083b4fe1cd2cdf3a8a90281"},
    {"path": "GUI/View/Agent3Tab.py", "bytes": 146713, "sha256": "f1e3717b404b3a385e89b5f5de2c491e55ea0d4b69579d32536500f5b0170e7c"},
    {"path": "GUI/View/Agent4Tab.py", "bytes": 60081, "sha256": "4d609ec00766bfd2d2d2c7d5ecc09fb18507e174ada65af5db5367815555f32d"},
    {"path": "eval/evaluator.py", "bytes": 34681, "sha256": "132aab96daca2d7d88a3cc1d26b0d09e708acabade48928b7c60357cc8ece73d"},
    {"path": "eval/agentD_variability_evaluator.py", "bytes": 3281, "sha256": "53b2cc4aae3a3cb4a903872359bbf60c060e7c62d03a15b3834b8f7db7503c14"},
]


class TransparencyValidationError(ValueError):
    """Raised when a public binding or transparency contract is inconsistent."""


def validate_provenance_record(record: dict[str, Any]) -> list[str]:
    """Validate the public provenance envelope without inspecting private data."""

    if not PROVENANCE_SCHEMA.is_file():
        return ["provenance schema is missing"]
    try:
        import jsonschema

        jsonschema.validate(record, json.loads(PROVENANCE_SCHEMA.read_text(encoding="utf-8")))
    except Exception as exc:  # noqa: BLE001 - validation reports a safe error list
        return [f"provenance schema validation failed: {type(exc).__name__}: {exc}"]
    return []


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive_sha256(observed_sha256: str, expected_sha256: str = AIRTRAVEL_ARCHIVE_SHA256) -> str:
    """Fail closed unless an observed public archive hash matches exactly."""

    if not isinstance(observed_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", observed_sha256.lower()):
        raise TransparencyValidationError("archive SHA-256 is absent or malformed")
    if observed_sha256.lower() != expected_sha256:
        raise TransparencyValidationError("pinned public archive SHA-256 mismatch")
    return "PASS"


def verify_airtravel_archive(
    archive_path: Path,
    manifest_path: Path = SOURCE_MANIFEST,
) -> dict[str, Any]:
    """Verify the pinned public Text2UML archive without materialising its bytes.

    The archive is expected to have the GitHub codeload root directory followed
    by ``dataset/AirTravel``.  Only hashes, lengths and safe relative names are
    returned; upstream source files are never copied into the repository.
    """

    if not archive_path.is_file():
        raise TransparencyValidationError("pinned public archive is unavailable")
    if not manifest_path.is_file():
        raise TransparencyValidationError("tracked AirTravel source manifest is unavailable")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("upstream_commit") != AIRTRAVEL_UPSTREAM_COMMIT:
        raise TransparencyValidationError("source manifest commit does not match pinned commit")
    if manifest.get("archive_sha256") != AIRTRAVEL_ARCHIVE_SHA256:
        raise TransparencyValidationError("source manifest archive hash does not match frozen hash")
    observed_archive_sha256 = _sha256_file(archive_path)
    verify_archive_sha256(observed_archive_sha256)
    expected_rows = manifest.get("files")
    if not isinstance(expected_rows, list) or len(expected_rows) != 143:
        raise TransparencyValidationError("source manifest must contain exactly 143 entries")
    expected = {
        str(row["path"]): {"bytes": int(row["bytes"]), "sha256": str(row["sha256"])}
        for row in expected_rows
    }
    with zipfile.ZipFile(archive_path) as archive:
        members = archive.infolist()
        duplicate_members = sorted(
            name for name in {member.filename for member in members}
            if sum(1 for member in members if member.filename == name) > 1
        )
        candidate_members: dict[str, zipfile.ZipInfo] = {}
        for member in members:
            marker = "/dataset/AirTravel/"
            if marker not in member.filename or member.filename.endswith("/"):
                continue
            relative = member.filename.split(marker, 1)[1]
            candidate_members[relative] = member
        observed_names = set(candidate_members)
        expected_names = set(expected)
        missing = sorted(expected_names - observed_names)
        extra = sorted(observed_names - expected_names)
        mismatched: list[str] = []
        for relative in sorted(expected_names & observed_names):
            member = candidate_members[relative]
            data = archive.read(member)
            actual_sha256 = hashlib.sha256(data).hexdigest()
            if len(data) != expected[relative]["bytes"] or actual_sha256 != expected[relative]["sha256"]:
                mismatched.append(relative)
    matched = len(expected_names & observed_names) - len(mismatched)
    return {
        "status": "PASS" if not (duplicate_members or missing or extra or mismatched) else "EVIDENCE_INVALID",
        "archive_path_class": "temporary_public_codeload_archive",
        "archive_sha256": observed_archive_sha256,
        "expected_archive_sha256": AIRTRAVEL_ARCHIVE_SHA256,
        "upstream_commit": AIRTRAVEL_UPSTREAM_COMMIT,
        "manifest_path": "docs/research/phd-proposal/text2uml-airtravel/source-manifest.json",
        "manifest_sha256": _sha256_file(manifest_path),
        "expected_file_count": len(expected_names),
        "observed_file_count": len(observed_names),
        "matched_count": matched,
        "missing_count": len(missing),
        "extra_count": len(extra),
        "mismatched_count": len(mismatched),
        "duplicate_members": duplicate_members,
        "missing": missing,
        "extra": extra,
        "mismatched": mismatched,
    }


def verify_official_release_archive(archive_path: Path) -> dict[str, Any]:
    """Verify the selected source files in the public VEGO-AI release archive."""

    if not archive_path.is_file():
        raise TransparencyValidationError("official VEGO-AI release archive is unavailable")
    observed_archive_sha256 = _sha256_file(archive_path)
    if observed_archive_sha256 != PUBLIC_RELEASE_ARCHIVE_SHA256:
        raise TransparencyValidationError("official VEGO-AI release archive SHA-256 mismatch")
    missing: list[str] = []
    mismatched: list[str] = []
    duplicate_members: list[str] = []
    inspected: list[dict[str, Any]] = []
    with zipfile.ZipFile(archive_path) as archive:
        members = archive.infolist()
        for expected in RELEASE_SOURCE_FILES:
            matches = [
                member
                for member in members
                if member.filename == expected["path"]
                or member.filename.endswith("/" + expected["path"])
            ]
            if len(matches) != 1:
                if not matches:
                    missing.append(expected["path"])
                else:
                    duplicate_members.append(expected["path"])
                continue
            data = archive.read(matches[0])
            actual = {
                "path": expected["path"],
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
            inspected.append(actual)
            if actual["bytes"] != expected["bytes"] or actual["sha256"] != expected["sha256"]:
                mismatched.append(expected["path"])
    return {
        "status": "PASS" if not (missing or mismatched or duplicate_members) else "EVIDENCE_INVALID",
        "archive_path_class": "temporary_public_release_codeload_archive",
        "archive_sha256": observed_archive_sha256,
        "expected_archive_sha256": PUBLIC_RELEASE_ARCHIVE_SHA256,
        "release_commit": PUBLIC_RELEASE_COMMIT,
        "expected_file_count": len(RELEASE_SOURCE_FILES),
        "inspected_file_count": len(inspected),
        "matched_count": len(inspected) - len(mismatched),
        "missing_count": len(missing),
        "mismatched_count": len(mismatched),
        "duplicate_members": sorted(duplicate_members),
        "missing": sorted(missing),
        "mismatched": sorted(mismatched),
        "source_files": inspected,
    }


def _source_manifest_metadata() -> dict[str, Any]:
    if not SOURCE_MANIFEST.is_file():
        return {
            "status": NOT_AVAILABLE,
            "path": "docs/research/phd-proposal/text2uml-airtravel/source-manifest.json",
            "sha256": NOT_AVAILABLE,
            "entry_count": NOT_AVAILABLE,
        }
    try:
        payload = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "EVIDENCE_INVALID",
            "path": "docs/research/phd-proposal/text2uml-airtravel/source-manifest.json",
            "sha256": _sha256_file(SOURCE_MANIFEST),
            "entry_count": NOT_AVAILABLE,
            "error_type": type(exc).__name__,
        }
    entries = payload.get("files") or payload.get("entries") or payload.get("manifest")
    count = len(entries) if isinstance(entries, list) else NOT_AVAILABLE
    return {
        "status": "TRACKED_MANIFEST_PRESENT",
        "path": "docs/research/phd-proposal/text2uml-airtravel/source-manifest.json",
        "sha256": _sha256_file(SOURCE_MANIFEST),
        "entry_count": count,
        "note": "Manifest metadata is tracked; source bytes are verified separately from a temporary public codeload archive.",
    }


def airtravel_selection() -> dict[str, Any]:
    """Return inventory-derived selection provenance without reading model text."""

    return load_airtravel_selection(AIRTRAVEL_INVENTORY)


def agent4_causal_path() -> dict[str, Any]:
    """Document the observed Agent-4 path without claiming a queue artifact."""

    return {
        "status": "EXECUTED_THEN_BLOCKED",
        "review_record_created": True,
        "review_record_count": "AT_LEAST_ONE",
        "queue_status": "NOT_AVAILABLE",
        "failure_reason": "cd_airtravel absent from legacy schema enum",
        "evidence_class": "DOCUMENTED_RUNTIME_PATH",
        "causal_steps": [
            {
                "step": "Agent-4 variability classification executed",
                "source": "VEGO-AI/framework/orchestrator.py:334-388",
            },
            {
                "step": "review record construction was entered",
                "source": "VEGO-AI/framework/human_review_queue.py:226-336",
            },
            {
                "step": "legacy schema validation rejected the setting",
                "source": "VEGO-AI/schemas/human_review_item.schema.json:62-68",
            },
            {
                "step": "pipeline catches queue-builder failure and keeps queue unavailable",
                "source": "VEGO-AI/framework/orchestrator.py:613-623",
            },
        ],
        "interpretation": (
            "The causal path is documented as executed, review-record-producing, then blocked. "
            "Queue status remains NOT_AVAILABLE; absence of a validated queue artifact does not "
            "establish that the policy did or did not trigger."
        ),
    }


def case_model_availability() -> dict[str, dict[str, str]]:
    """Expose case-to-model availability without inferring from configuration."""

    base = {
        "model_availability": "UNAVAILABLE",
        "evidence_status": NOT_AVAILABLE,
        "basis": "No validated case-to-model artifact is mounted in the reviewed worktree.",
        "inference_from_model_config": "PROHIBITED",
    }
    return {
        "EP-577319bf": {
            **base,
            "canonical_episode_id": "EP-577319bf37c87",
            "case_linkage": "case 02",
        },
        "EP-81b2c98d": {
            **base,
            "canonical_episode_id": "EP-81b2c98d59125",
            "case_linkage": "cross-case episode",
        },
    }


def reporting_code_metadata() -> dict[str, Any]:
    """Describe reporting-code hashes as documentation metadata, not evidence."""

    return {
        "field": "reporting_code_sha",
        "status": "NON_EVIDENTIARY_DOCUMENTATION_METADATA",
        "used_for_scientific_binding": False,
        "stale_values": "STAMPED_SUPERSEDED",
        "historical_executed_code_sha": "efe686ac0b13c6e17695b816da7eb0cdd3eadcc1",
        "current_reporting_code": "scripts/airtravel_real_run.py",
        "current_reporting_code_status": "CHANGED_POST_RUN_FOR_RECEIPT_BINDING",
        "note": (
            "The historical executed code and current reporting code are distinct; a reporting "
            "stamp cannot establish what code produced a private result."
        ),
    }


def byte_identity_distinction() -> dict[str, Any]:
    """Return the explicit historical/current code distinction required by the report."""

    metadata = reporting_code_metadata()
    return {
        "historical_executed_code": metadata["historical_executed_code_sha"],
        "current_reporting_code_status": metadata["current_reporting_code_status"],
        "byte_identical_to_historical": False,
        "reason": "airtravel_real_run.py changed post-run for receipt-binding work.",
    }


def build_provenance_record(
    *,
    reviewed_head_sha: str,
    main_sha: str,
    airtravel_archive_sha256: str | None = None,
    airtravel_file_count: int | None = None,
    airtravel_matched_count: int | None = None,
    airtravel_verification: dict[str, Any] | None = None,
    official_release_verification: dict[str, Any] | None = None,
    verification_date: str | None = None,
) -> dict[str, Any]:
    """Return safe, machine-readable data provenance (never private run data)."""

    archive_status = NOT_AVAILABLE
    if airtravel_verification is not None:
        archive_status = str(airtravel_verification.get("status", "EVIDENCE_INVALID"))
        airtravel_archive_sha256 = str(airtravel_verification.get("archive_sha256", NOT_AVAILABLE))
        airtravel_file_count = airtravel_verification.get("observed_file_count")
        airtravel_matched_count = airtravel_verification.get("matched_count")
    elif airtravel_archive_sha256 is not None:
        archive_status = verify_archive_sha256(airtravel_archive_sha256)
    counts_ok = airtravel_file_count == 143 and airtravel_matched_count == 143
    if archive_status == "PASS" and not counts_ok:
        archive_status = "EVIDENCE_INVALID"
    if archive_status == NOT_AVAILABLE:
        observed_count: int | str = NOT_AVAILABLE
        matched_count: int | str = NOT_AVAILABLE
    else:
        observed_count = airtravel_file_count if airtravel_file_count is not None else NOT_AVAILABLE
        matched_count = airtravel_matched_count if airtravel_matched_count is not None else NOT_AVAILABLE
    selection = airtravel_selection()
    selected_paths = selection.get("selected_case_paths", [])
    candidate_labels = {
        re.sub(r"^\d+_", "", Path(str(item["path"])).stem): Path(str(item["path"])).stem
        for item in AIRTRAVEL_RUNTIME_FILES
        if item["role"] == "candidate_model"
    }
    selected_case_ids = [
        f"{index:02d}_{candidate_labels[path]}"
        for index, path in enumerate(selected_paths, start=1)
        if isinstance(path, str) and path in candidate_labels
    ]
    if not selected_case_ids:
        selected_case_ids = [
            Path(str(item["path"])).stem
            for item in AIRTRAVEL_RUNTIME_FILES
            if item["role"] == "candidate_model"
        ]
    return {
        "schema_version": "study1-data-provenance-v1",
        "record_type": "safe_public_and_evidence_boundary",
        "verification_date": verification_date or date.today().isoformat(),
        "review_context": {
            "origin_main_sha": main_sha,
            "reviewed_pr_head_sha": reviewed_head_sha,
            "pr_number": 41,
            "pr_state": "OPEN_DRAFT_UNMERGED",
        },
        "dataset": {
            "classification": "PUBLIC_EXTERNAL",
            "is_student_or_historical_vego_data": False,
            "setting_id": AIRTRAVEL_SETTING_ID,
            "corpus_id": AIRTRAVEL_CORPUS_ID,
            "upstream_repository": "https://github.com/IlKaiser/text2uml",
            "upstream_scenario_path": "dataset/AirTravel",
            "upstream_commit": AIRTRAVEL_UPSTREAM_COMMIT,
            "archive_url": AIRTRAVEL_ARCHIVE_URL,
            "archive_sha256": airtravel_archive_sha256 or NOT_AVAILABLE,
            "selection": selection,
            "selection_rule": selection["predicate"],
            "selection_status": selection["status"],
            "selection_limitation": selection["reason"],
            "selected_case_ids": selected_case_ids,
            "selected_runtime_files": AIRTRAVEL_RUNTIME_FILES,
            "source_file_count": observed_count,
            "source_manifest_entry_count": _source_manifest_metadata()["entry_count"],
            "source_manifest": _source_manifest_metadata(),
            "airtravel_source_verification": {
                "status": archive_status,
                "method": "temporary public codeload archive; file-level SHA-256; raw bytes not committed",
                "observed_file_count": observed_count,
                "matched_count": matched_count,
                "missing_count": (
                    airtravel_verification.get("missing_count", 0)
                    if airtravel_verification is not None
                    else (0 if archive_status == "PASS" else NOT_AVAILABLE)
                ),
                "extra_count": (
                    airtravel_verification.get("extra_count", 0)
                    if airtravel_verification is not None
                    else (0 if archive_status == "PASS" else NOT_AVAILABLE)
                ),
                "mismatched_count": (
                    airtravel_verification.get("mismatched_count", 0)
                    if airtravel_verification is not None
                    else (0 if archive_status == "PASS" else NOT_AVAILABLE)
                ),
            },
            "airtravel_verification_receipt": airtravel_verification or {
                "status": archive_status,
                "note": "Pass values are included only when supplied by an independently verified public archive check.",
            },
            "authorship_and_scope": {
                "student_or_historical_vego_data": False,
                "external_llm_generated_outputs_in_source": True,
                "correctness_ground_truth": False,
                "educational_representativeness": False,
                "human_intervention_effectiveness": False,
                "note": "The feasibility corpus is not Cheers/ParkWise data and is not evidence of student behavior.",
            },
            "excluded_data": [
                "private accepted-run prompts, answers, event logs and output files",
                "Cheers/ParkWise historical records",
                "student submissions and supervisor labels",
                "reference-only PlantUML and extramaterial files",
                "Detector-v1 accuracy, benefit, causal, generalization and superiority claims",
            ],
            "allowed_claims": [
                "public corpus and selection provenance",
                "code-defined logging and detector contracts",
                "descriptive Q&A observations only after a validated run artifact is mounted",
            ],
            "forbidden_claims": [
                "student or human representativeness",
                "alert correctness or accuracy",
                "human benefit, workload reduction or intervention effectiveness",
                "generalization or policy superiority",
            ],
        },
        "official_vego_release": {
            "repository": PUBLIC_RELEASE_REPOSITORY,
            "release": PUBLIC_RELEASE,
            "commit": PUBLIC_RELEASE_COMMIT,
            "release_url": PUBLIC_RELEASE_URL,
            "archive_url": PUBLIC_RELEASE_ARCHIVE_URL,
            "archive_sha256": (
                official_release_verification.get("archive_sha256", NOT_AVAILABLE)
                if official_release_verification is not None
                else NOT_AVAILABLE
            ),
            "archive_verification": (
                official_release_verification.get("status", "EVIDENCE_INVALID")
                if official_release_verification is not None
                else NOT_AVAILABLE
            ),
            "source_files_expected": RELEASE_SOURCE_FILES,
            "source_files_inspected": (
                official_release_verification.get("source_files", [])
                if official_release_verification is not None
                else []
            ),
            "source_verification_receipt": official_release_verification or {
                "status": NOT_AVAILABLE,
                "note": "Pass values require a public release archive supplied to the verifier; no source bytes are committed.",
            },
            "artifact_note": "The release ships source code, not a runtime interaction_log.json, user_actions.log or qa_events.jsonl artifact.",
        },
        "private_accepted_run_evidence": {
            "status": NOT_AVAILABLE,
            "binding_manifest": NOT_AVAILABLE,
            "reason": "No accepted private binding manifest is mounted in the reviewed worktree; no scientific aggregate is emitted.",
        },
        "canonical_project_artifacts": {
            "signal_dictionary": {
                "path": "docs/research/phd-proposal/study1-signal-dictionary-v1.json",
                "sha256": (
                    _sha256_file(ROOT / "docs" / "research" / "phd-proposal" / "study1-signal-dictionary-v1.json")
                    if (ROOT / "docs" / "research" / "phd-proposal" / "study1-signal-dictionary-v1.json").is_file()
                    else NOT_AVAILABLE
                ),
            },
            "traceability_matrix": {
                "path": "docs/research/phd-proposal/study1-signal-traceability-matrix-v1.csv",
                "sha256": (
                    _sha256_file(ROOT / "docs" / "research" / "phd-proposal" / "study1-signal-traceability-matrix-v1.csv")
                    if (ROOT / "docs" / "research" / "phd-proposal" / "study1-signal-traceability-matrix-v1.csv").is_file()
                    else NOT_AVAILABLE
                ),
            },
        },
        "verification_boundary": "READY_FOR_SUPERVISOR_TRANSPARENCY_REVIEW_NOT_A_NEW_SCIENTIFIC_RESULT",
    }


def log_contract_matrix() -> list[dict[str, Any]]:
    """Describe each candidate artifact without confusing source with runtime."""

    runtime = NOT_AVAILABLE
    return [
        {
            "artifact": "interaction_log.json",
            "produced_by": "VEGO GUI Common path / LLMClient when interaction_log is configured",
            "exists_in_official_v2_1_5_3_source": True,
            "exists_in_reviewed_run_worktree": runtime,
            "fields_available": "timestamp; agent; skill; label; model; prompt/response fields depend on configured log mode",
            "used_for_detector_v1": False,
            "q_and_a_source_of_truth": False,
            "used_only_for_ui_or_audit": True,
            "privacy_class": "PRIVATE_SENSITIVE_RAW_OR_HASHED_LLM_TRACE",
            "limitation": "A named path/function is not proof that a runtime file was produced; GUI uses JSONL content under a .json name.",
            "code_location_evidence": "GUI/View/GUI_Common.py:99-104; framework/llm_client.py:10-24,47-58,143-179",
            "version_commit": "VEGO-AI public release v2.1.5.3",
        },
        {
            "artifact": "user_actions.log",
            "produced_by": "GUI Controller action_logger.py",
            "exists_in_official_v2_1_5_3_source": True,
            "exists_in_reviewed_run_worktree": runtime,
            "fields_available": "pipe-delimited user action messages and timestamps",
            "used_for_detector_v1": False,
            "q_and_a_source_of_truth": False,
            "used_only_for_ui_or_audit": True,
            "privacy_class": "PRIVATE_UI_AUDIT",
            "limitation": "It records GUI actions, not question/answer lifecycle, episode identity, confidence, evidence presence or termination.",
            "code_location_evidence": "GUI/Controller/action_logger.py:53-55,90-121,168-207",
            "version_commit": "VEGO-AI public release v2.1.5.3",
        },
        {
            "artifact": "qa_events.jsonl",
            "produced_by": "VEGO-AI/framework/qa_communication.py recorder / local observer",
            "exists_in_official_v2_1_5_3_source": False,
            "exists_in_reviewed_run_worktree": runtime,
            "fields_available": "run_id; episode_id; event type/order; question_id; source/target; round; confidence; evidence ref; termination",
            "used_for_detector_v1": True,
            "q_and_a_source_of_truth": True,
            "used_only_for_ui_or_audit": False,
            "privacy_class": "PRIVATE_HASHED_EVENT_METADATA",
            "limitation": "Without a binding manifest and byte-verified accepted log, all metrics are NOT_AVAILABLE_IN_WORKTREE.",
            "code_location_evidence": "VEGO-AI/framework/qa_communication.py:18-23,57-117,180-299; scripts/extract_qa_escalation_features.py:342-380",
            "version_commit": "reviewed PR #41 head; protected source unchanged",
        },
        {
            "artifact": "Agent 3 structured CSV export (cases_summary.csv)",
            "produced_by": "GUI View Agent3Tab export action",
            "exists_in_official_v2_1_5_3_source": True,
            "exists_in_reviewed_run_worktree": runtime,
            "fields_available": "case/group summary, score and notes as exported by GUI",
            "used_for_detector_v1": False,
            "q_and_a_source_of_truth": False,
            "used_only_for_ui_or_audit": True,
            "privacy_class": "PRIVATE_CASE_SUMMARY",
            "limitation": "CSV export is not the append-only Q&A event stream and cannot establish one-answer-per-question lifecycle.",
            "code_location_evidence": "GUI/View/Agent3Tab.py:1067-1069,3144-3320",
            "version_commit": "VEGO-AI public release v2.1.5.3",
        },
        {
            "artifact": "Agent 4 variability classifications",
            "produced_by": "Agent 4 evaluator/orchestrator",
            "exists_in_official_v2_1_5_3_source": True,
            "exists_in_reviewed_run_worktree": runtime,
            "fields_available": "classification; confidence; flag_for_guidelines_update; requires_human_review",
            "used_for_detector_v1": False,
            "q_and_a_source_of_truth": False,
            "used_only_for_ui_or_audit": False,
            "privacy_class": "PRIVATE_MODEL_OUTPUT_METADATA",
            "limitation": "This is the separate Selective Intervention Policy input. It may feed a queue builder; absence of a queue artifact does not mean not triggered.",
            "code_location_evidence": "VEGO-AI/framework/selective_intervention_policy.py:49-88; VEGO-AI/framework/human_review_queue.py:243-334; VEGO-AI/framework/orchestrator.py:361-429",
            "version_commit": "VEGO-AI public release v2.1.5.3 / reviewed project source",
        },
        {
            "artifact": "run receipt / pipeline manifest / output hashes",
            "produced_by": "study execution and evidence-recovery tooling",
            "exists_in_official_v2_1_5_3_source": False,
            "exists_in_reviewed_run_worktree": runtime,
            "fields_available": "run identity; setting/corpus; execution/config hashes; event-log hash; output hashes; counters; status",
            "used_for_detector_v1": False,
            "q_and_a_source_of_truth": False,
            "used_only_for_ui_or_audit": True,
            "privacy_class": "PRIVATE_PROVENANCE_METADATA",
            "limitation": "Receipt numbers are cross-checks only; the event log remains primary for episode and detector counts.",
            "code_location_evidence": "scripts/study1_evidence_recovery.py:55-63,390-440; scripts/airtravel_v4_contract.py:170-190",
            "version_commit": "reviewed project source",
        },
    ]


def detector_criteria() -> list[dict[str, Any]]:
    """Return the frozen Detector-v1 rule-to-field contract."""

    common_fields = [
        "run_id",
        "episode_id",
        "event_type",
        "sequence (event ordering)",
        "event_id (answer event identifier)",
        "question_id",
        "source_agent",
        "target_agent",
        "round_index",
        "termination_reason",
        "scientific_complete",
    ]
    def fields(*extra: str) -> list[str]:
        return common_fields + [item for item in extra if item not in common_fields]
    return [
        {
            "signal": "S1",
            "signal_name": "S1_LOW_ANSWER_CONFIDENCE",
            "exact_code_rule": 'if any(row.get("answer_confidence") == "Low" for row in answers):',
            "required_log_fields": fields("answer_confidence"),
            "unit": "Q&A episode",
            "meaning": "At least one answer reports Low confidence under the frozen answer field.",
            "does_not_mean": "It does not prove an incorrect answer, poor evidence, or that a human queue was written.",
            "detector_tier": "STRONG_ALERT",
            "direct_trigger": True,
            "candidate_for_human_review": True,
            "observed_in_accepted_evidence": NOT_AVAILABLE,
        },
        {
            "signal": "S2",
            "signal_name": "S2_MEDIUM_ANSWER_CONFIDENCE",
            "exact_code_rule": 'if any(row.get("answer_confidence") == "Medium" for row in answers):',
            "required_log_fields": fields("answer_confidence"),
            "unit": "Q&A episode",
            "meaning": "At least one answer reports Medium confidence under the frozen answer field.",
            "does_not_mean": "It does not prove error, disagreement or intervention benefit.",
            "detector_tier": "WEAK_ALERT",
            "direct_trigger": True,
            "candidate_for_human_review": True,
            "observed_in_accepted_evidence": NOT_AVAILABLE,
        },
        {
            "signal": "S3",
            "signal_name": "S3_MISSING_ANSWER_EVIDENCE",
            "exact_code_rule": 'if any((ref := row.get("answer_evidence_ref")) is None or ref.get("length", 0) == 0 for row in answers):',
            "required_log_fields": fields("answer_evidence_ref"),
            "unit": "Q&A episode",
            "meaning": "At least one answer has a null or zero-length evidence reference under the frozen structural rule.",
            "does_not_mean": "It does not assess evidence quality, truth, or semantic support; it is not an observed finding without a validated log.",
            "detector_tier": "STRONG_ALERT",
            "direct_trigger": True,
            "candidate_for_human_review": True,
            "observed_in_accepted_evidence": NOT_AVAILABLE,
        },
        {
            "signal": "S6",
            "signal_name": "S6_MULTIPLE_QA_ROUNDS",
            "exact_code_rule": "if s6_fires(episode):",
            "required_log_fields": fields("round_index"),
            "unit": "Q&A episode",
            "meaning": S6_OPERATIONAL_DEFINITION["description"],
            "does_not_mean": "It does not prove unresolved disagreement, high burden, or answer quality.",
            "detector_tier": "WEAK_ALERT",
            "direct_trigger": True,
            "candidate_for_human_review": True,
            "observed_in_accepted_evidence": NOT_AVAILABLE,
        },
        {
            "signal": "S7",
            "signal_name": "S7_TERMINATED_MAX_ROUNDS",
            "exact_code_rule": 'if episode.get("termination_reason") == "TERMINATED_MAX_ROUNDS":',
            "required_log_fields": fields("termination_reason"),
            "unit": "Q&A episode",
            "meaning": "The episode ended at the frozen maximum-round termination state.",
            "does_not_mean": "It does not prove the final answer is wrong or that a human corrected it.",
            "detector_tier": "STRONG_ALERT",
            "direct_trigger": True,
            "candidate_for_human_review": True,
            "observed_in_accepted_evidence": NOT_AVAILABLE,
        },
    ]


def validate_detector_criteria(rows: Iterable[dict[str, Any]], source_text: str) -> list[str]:
    """Return contract errors; callers should fail closed when non-empty."""

    expected = {row["signal"]: row["exact_code_rule"] for row in detector_criteria()}
    errors: list[str] = []
    seen: set[str] = set()
    for row in rows:
        signal = row.get("signal")
        rule = row.get("exact_code_rule")
        if signal in seen:
            errors.append(f"duplicate signal: {signal}")
        seen.add(signal)
        if signal not in expected:
            errors.append(f"unsupported signal: {signal}")
            continue
        if rule != expected[signal]:
            errors.append(f"rule drift: {signal}")
        if rule not in source_text:
            errors.append(f"rule not found in canonical detector source: {signal}")
    errors.extend(f"missing signal: {signal}" for signal in sorted(set(expected) - seen))
    return errors


def _fallback_signal_entries() -> list[dict[str, Any]]:
    """Build a minimal field dictionary when the superseded JSON is absent.

    The release/main cleanup removed the older standalone signal dictionary.
    The transparency package must still be runnable from a clean checkout, so
    the frozen detector rows and layer names remain available without importing
    a deleted project artifact.  This fallback is descriptive metadata only;
    it never changes detector evaluation.
    """

    raw_fields = (
        ("run_id", "מזהה הריצה", "run_id", "run"),
        ("episode_id", "מזהה הפרק", "episode_id", "Q&A episode"),
        ("event_type", "סוג האירוע", "event_type", "event"),
        ("question_id", "מזהה השאלה", "question_id", "question"),
        ("source_agent", "הסוכן השואל", "source_agent", "question"),
        ("target_agent", "הסוכן המשיב", "target_agent", "question"),
        ("answer_confidence", "ביטחון התשובה", "answer_confidence", "answer"),
        ("answer_evidence_ref", "הפניה לראיות התשובה", "answer_evidence_ref", "answer"),
        ("round_index", "מספר הסבב", "round_index", "question or answer"),
        ("termination_reason", "סיבת סיום הפרק", "termination_reason", "Q&A episode"),
    )
    entries: list[dict[str, Any]] = []
    for name, hebrew, source_field, unit in raw_fields:
        entries.append(
            {
                "category": "raw_event_field",
                "english_code_name": name,
                "hebrew_name": hebrew,
                "source_artifact": "VEGO-AI/framework/qa_communication.py",
                "source_field": source_field,
                "unit_of_analysis": unit,
                "calculation_rule": "Recorded by the validated event contract; absent values remain unavailable.",
                "measurement_kind": "deterministic_event_field",
                "can_cooccur_with_other_signals": True,
                "direct_detector_v1_trigger": False,
                "detector_role": "descriptive_only",
                "candidate_for_human_review": False,
                "does_not_prove": "A raw field is provenance or structure, not correctness or human benefit.",
                "evidence_availability": "CODE_DEFINED; RUN_EVIDENCE_STATUS_SEPARATE",
            }
        )

    signal_hebrew = {
        "S1": "ביטחון תשובה נמוך",
        "S2": "ביטחון תשובה בינוני",
        "S3": "היעדר הפניית ראיות בתשובה",
        "S6": "יותר מסבב שאלות ותשובות אחד",
        "S7": "אי־התכנסות עד הגבלת הסבבים",
    }
    for row in detector_criteria():
        entries.append(
            {
                "category": "communication_process_signal",
                "english_code_name": row["signal_name"],
                "hebrew_name": signal_hebrew[row["signal"]],
                "source_artifact": row["source_artifact"]
                if "source_artifact" in row
                else "scripts/extract_qa_escalation_features.py",
                "source_field": ", ".join(row["required_log_fields"]),
                "unit_of_analysis": row["unit"],
                "calculation_rule": row["exact_code_rule"],
                "measurement_kind": "model_self_report" if row["signal"] in {"S1", "S2"} else "deterministic_derived_field",
                "can_cooccur_with_other_signals": True,
                "direct_detector_v1_trigger": True,
                "detector_role": "direct_trigger",
                "candidate_for_human_review": True,
                "does_not_prove": row["does_not_mean"],
                "evidence_availability": "CODE_DEFINED; RUN_EVIDENCE_STATUS_SEPARATE",
            }
        )

    for name, hebrew in (
        ("C1_MAPPING_CERTAINTY", "ודאות מיפוי Agent 2"),
        ("C2_AGENT4_CLASSIFICATION_CONFIDENCE", "ביטחון סיווג Agent 4"),
        ("C3_AGENT4_REVIEW_FLAGS", "דגלי בדיקה של Agent 4"),
        ("MAPPING_SATISFIED", "מיפוי מסופק"),
        ("MAPPING_PARTIALLY_SATISFIED", "מיפוי מסופק חלקית"),
        ("MAPPING_NON_SATISFIED", "מיפוי לא מסופק"),
        ("MAPPING_ALTERNATIVE", "חלופה במיפוי"),
        ("MAPPING_CERTAINTY", "ודאות המיפוי"),
        ("SOURCE_TARGET_ALIGNMENT", "התאמת מקור–יעד"),
        ("UNCOVERED_FRAGMENTS", "שברים שלא כוסו"),
    ):
        entries.append(
            {
                "category": "context_or_semantic_output",
                "english_code_name": name,
                "hebrew_name": hebrew,
                "source_artifact": "VEGO-AI pipeline outputs (when validated)",
                "source_field": name,
                "unit_of_analysis": "mapping item or variability classification",
                "calculation_rule": "Descriptive output only; no Detector-v1 predicate.",
                "measurement_kind": "semantic_model_output",
                "can_cooccur_with_other_signals": True,
                "direct_detector_v1_trigger": False,
                "detector_role": "context_only",
                "candidate_for_human_review": False,
                "does_not_prove": "It does not prove correctness, error, human need, or generalization.",
                "evidence_availability": NOT_AVAILABLE,
                "data_status": NOT_AVAILABLE,
            }
        )
    return entries


def _load_canonical_signal_entries() -> list[dict[str, Any]]:
    """Load the legacy dictionary when present, otherwise use safe metadata."""

    canonical_path = ROOT / "docs" / "research" / "phd-proposal" / "study1-signal-dictionary-v1.json"
    if canonical_path.is_file():
        try:
            payload = json.loads(canonical_path.read_text(encoding="utf-8"))
            entries = payload.get("entries", [])
            if isinstance(entries, list):
                return entries
        except (OSError, json.JSONDecodeError, AttributeError):
            pass
    return _fallback_signal_entries()


def mechanism_boundaries() -> dict[str, dict[str, Any]]:
    return {
        "detector_v1": {
            "unit": "Q&A episode",
            "output": "reporting-level candidate-for-human-review label",
            "writes_queue": False,
            "queue_status": "NOT_APPLICABLE",
            "queue_artifact": None,
            "automatic_modification": False,
        },
        "selective_intervention_agent4": {
            "unit": "Agent-4 variability classification",
            "output": "separate review item when queue builder executes",
            "writes_queue": True,
            "queue_status": "NOT_AVAILABLE",
            "queue_artifact": "human_review_queue.jsonl",
            "automatic_modification": False,
            "status_rule": "NOT_AVAILABLE unless a validated queue artifact is mounted; absence is not not-triggered.",
            "causal_path": agent4_causal_path(),
        },
    }


def transparency_data_dictionary(*, reviewed_head_sha: str, main_sha: str) -> dict[str, Any]:
    """Expose the canonical field dictionary with the current evidence boundary."""

    entries = _load_canonical_signal_entries()
    return {
        "schema_version": "study1-transparency-data-dictionary-v1",
        "evidence_status": NOT_AVAILABLE,
        "review_context": {
            "origin_main_sha": main_sha,
            "reviewed_pr_head_sha": reviewed_head_sha,
            "pr_number": 41,
            "pr_state": "OPEN_DRAFT_UNMERGED",
            "note": "The canonical legacy dictionary remains an immutable input; this wrapper records the current review context.",
        },
        "source_of_truth": "qa_events.jsonl only after a byte-verified accepted-run binding manifest",
        "layers": {
            "raw_event_fields": [
                "run_id",
                "episode_id",
                "event_type",
                "event_id",
                "sequence",
                "question_id",
                "source_agent",
                "target_agent",
                "answer_confidence",
                "answer_evidence_ref",
                "round_index",
                "termination_reason",
            ],
            "communication_process_signals": ["S1", "S2", "S3", "S6", "S7"],
            "context_only_variables": ["C1_MAPPING_CERTAINTY", "C2_AGENT4_CLASSIFICATION_CONFIDENCE", "C3_AGENT4_REVIEW_FLAGS"],
            "semantic_mapping_outputs": [
                "Satisfied",
                "Partially-Satisfied",
                "Non-Satisfied",
                "Alternative",
                "mapping certainty",
                "source/target alignment",
                "uncovered fragments",
            ],
            "operational_action": [
                "candidate_for_human_review reporting label only",
                "Agent-4 queue builder may create human_review_queue.jsonl",
                "no automatic source/target/guideline/model modification",
            ],
        },
        "mechanisms": mechanism_boundaries(),
        "agent4_causal_path": agent4_causal_path(),
        "case_model_availability": case_model_availability(),
        "reporting_code_metadata": reporting_code_metadata(),
        "canonical_signal_entries": entries,
        "canonical_dictionary_path": "docs/research/phd-proposal/study1-signal-dictionary-v1.json",
        "note": "Alternative and Non-Satisfied are semantic mapping outputs, not Detector-v1 triggers or error labels by themselves.",
    }


def safe_metrics(evidence_root: Path | None) -> dict[str, Any]:
    """Return only safe aggregate placeholders when the accepted log is absent."""

    if evidence_root is not None:
        raise TransparencyValidationError(
            "private evidence requires the canonical binding validator; this package never accepts an unbound path"
        )
    tables = {}
    table_names = (
        "episodes",
        "questions_answers_by_case",
        "route_matrix",
        "confidence_by_episode_and_round",
        "evidence_reference_distribution",
        "signal_cooccurrence",
        "confidence_evidence_termination",
        "cases_with_and_without_q_and_a",
    )
    for name in table_names:
        tables[name] = {
            "evidence_status": NOT_AVAILABLE,
            "denominator": NOT_AVAILABLE,
            "rows": [],
        }
    detector = {
        signal: {
            "rule_present": True,
            "observed": False,
            "observed_count": NOT_AVAILABLE,
            "unit": "Q&A episode",
        }
        for signal in ("S1", "S2", "S3", "S6", "S7")
    }
    return {
        "schema_version": "study1-transparency-metrics-v1",
        "evidence_status": NOT_AVAILABLE,
        "scientific_denominator": NOT_AVAILABLE,
        "private_event_log": NOT_AVAILABLE,
        "detector_v1": "rules_described_only_no_experimental_run",
        "detector_signals": detector,
        "detector_formula": {
            "strong": "STRONG_ALERT = S1 OR S3 OR S7",
            "weak": "WEAK_ALERT = no strong signal AND (S2 OR S6)",
            "none": "NO_ALERT otherwise",
        },
        "mechanisms": mechanism_boundaries(),
        "agent4_causal_path": agent4_causal_path(),
        "case_model_availability": case_model_availability(),
        "reporting_code_metadata": reporting_code_metadata(),
        "agent4_review_queue": {
            "status": "NOT_AVAILABLE",
            "artifact": "human_review_queue.jsonl",
            "note": "A missing/unmounted queue is not a count of zero and is not ‘not triggered’.",
        },
        "observed_patterns": [],
        "rules_present_not_observed": [
            "S1 low answer confidence",
            "S2 medium answer confidence",
            "S3 null/zero-length answer evidence reference",
            "S6_MULTIPLE_QA_ROUNDS: " + S6_OPERATIONAL_DEFINITION["rule"],
            "S7 maximum-round termination",
        ],
        "tables": tables,
        "claim_boundary": "Descriptive evidence only after a byte-verified accepted event log; no accuracy, benefit, causal, generalization or superiority claim.",
    }


def example_cards() -> list[dict[str, Any]]:
    banner = "המחשה הנדסית בלבד — אינה תוצאת ניסוי ואינה נתון אמפירי"
    cards = [
        {
            "card_id": "EX-01",
            "title_he": "אפיזודה מלאה ללא התראה",
            "mechanism": "Detector-v1",
            "input_case": "fixture-case-normal (engineering-only)",
            "log_fields": "episode_id; QUESTION_EMITTED; ANSWER_RECEIVED; High; non-empty evidence ref; round_index=1; CONVERGED",
            "detector_rule": "No S1/S2/S3/S6/S7",
            "detector_result": "NO_ALERT (illustrative rule application only)",
            "interpretation_he": "הדוגמה ממחישה כיצד מצב תקין עובר ללא תווית מועמד.",
            "limitation_he": "אינה מוכיחה נכונות תשובה או איכות ראיות.",
            "banner_he": banner,
            "banner": "ENGINEERING_ILLUSTRATION_ONLY",
            "evidence_class": "ENGINEERING_ILLUSTRATION_ONLY",
            "enters_scientific_metrics": False,
        },
        {
            "card_id": "EX-02",
            "title_he": "התראת חוזק עקב ביטחון נמוך",
            "mechanism": "Detector-v1",
            "input_case": "fixture-case-low-confidence (engineering-only)",
            "log_fields": "episode_id; ANSWER_RECEIVED; answer_confidence=Low; non-empty evidence ref; CONVERGED",
            "detector_rule": "S1 fires; STRONG_ALERT = S1 OR S3 OR S7",
            "detector_result": "STRONG_ALERT (illustrative rule application only)",
            "interpretation_he": "זו תווית דיווח שמצביעה על מועמד לבדיקה אנושית בלבד.",
            "limitation_he": "Low הוא דיווח עצמי של המודל ואינו תווית שגיאה.",
            "banner_he": banner,
            "banner": "ENGINEERING_ILLUSTRATION_ONLY",
            "evidence_class": "ENGINEERING_ILLUSTRATION_ONLY",
            "enters_scientific_metrics": False,
        },
        {
            "card_id": "EX-03",
            "title_he": "סיווג Agent-4 ותור נפרד",
            "mechanism": "Selective Intervention Policy / Agent-4",
            "input_case": "fixture-variability-classification (engineering-only)",
            "log_fields": "classification=Undetermined; confidence=medium; requires_human_review=true",
            "detector_rule": "Not a Detector-v1 input",
            "detector_result": "Detector-v1: NOT_APPLICABLE",
            "interpretation_he": "Queue builder נפרד עשוי ליצור human_review_queue.jsonl אם יורץ.",
            "limitation_he": "ב-AirTravel הסטטוס כרגע NOT_AVAILABLE; אין שינוי אוטומטי במקור, בהנחיה, ביעד או במודל.",
            "banner_he": banner,
            "banner": "ENGINEERING_ILLUSTRATION_ONLY",
            "evidence_class": "ENGINEERING_ILLUSTRATION_ONLY",
            "enters_scientific_metrics": False,
        },
    ]
    cards.append(
        {
            "card_id": "EP-577319bf",
            "title_he": "דוגמה אמיתית מצונזרת — שרשרת Q&A מלאה",
            "mechanism": "Detector-v1",
            "input_case": "case 02 (hash reference only)",
            "case_reference": "sha256:UNAVAILABLE_IN_WORKTREE",
            "qa_event_references": ["sha256:UNAVAILABLE_IN_WORKTREE"],
            "raw_content": "REDACTED",
            "example_kind": "REAL_REDACTED_RETROSPECTIVE_STRUCTURE_ONLY",
            "log_fields": "hash-only event references; QUESTION_EMITTED → ANSWER_RECEIVED → CONVERGED",
            "fields": {
                "case_label": "02 (archival safe label; case hash unavailable in worktree)",
                "question_id": "HASH_REF_UNAVAILABLE_IN_WORKTREE",
                "question_count": 1,
                "answer_count": 1,
                "asking_agent": "REDACTED",
                "answering_agent": "REDACTED",
                "round_index": 1,
                "answer_confidence": "Low (archival label; raw answer redacted)",
                "answer_evidence_ref": "HASH_REF_UNAVAILABLE_IN_WORKTREE",
                "termination_reason": "CONVERGED (reported historical label)",
                "signals_fired": ["S1_LOW_ANSWER_CONFIDENCE (archival label)"],
            },
            "detector_rule": "STRONG_ALERT = S1 OR S3 OR S7; WEAK_ALERT = no strong signal AND (S2 OR S6)",
            "detector_result": "STRONG_ALERT (archival classification; illustrative rule application only)",
            "interpretation_he": "הדוגמה האמיתית המצונזרת מציגה את השרשרת case → Q&A → fields → Detector rule → result; תוכן השאלה והתשובה נשאר מצונזר.",
            "limitation": "ENGINEERING_ILLUSTRATION_ONLY; archival descriptive labels only; no current event-log hash is mounted, so no scientific aggregate is recomputed and no correctness, quality, causality or human benefit is inferred.",
            "limitation_he": "תוכן השאלה והתשובה אינו זמין ב-worktree; לא ניתן לאמת את הערכים מעבר להפניה ההיסטורית.",
            "banner_he": banner,
            "banner": "ENGINEERING_ILLUSTRATION_ONLY",
            "evidence_class": "ENGINEERING_ILLUSTRATION_ONLY",
            "enters_scientific_metrics": False,
        }
    )
    return cards


def transparency_figure_manifest() -> dict[str, Any]:
    """Describe only safe rule/architecture visuals, never scientific plots."""

    return {
        "schema_version": "study1-transparency-figures-manifest-v1",
        "status": "SAFE_RULE_VISUALS_ONLY",
        "evidence_status": NOT_AVAILABLE,
        "claim_boundary": "No empirical figure or scientific chart is generated while the accepted private event log is unavailable.",
        "figures": [
            {
                "figure_id": "FIG-01",
                "title": "Detector-v1 rule flow",
                "artifact": "2026-09-07-study1-data-log-pattern-transparency-he.pdf",
                "kind": "rule_diagram",
                "source_refs": ["detector-v1-criteria-to-log-fields-v1.csv"],
                "evidence_class": "ENGINEERING_ILLUSTRATION_ONLY",
                "scientific_denominator": "NOT_APPLICABLE",
                "status": "SAFE_RULE_VISUAL",
                "does_not_show": "alert correctness, prevalence, benefit, or intervention effect",
            },
            {
                "figure_id": "FIG-02",
                "title": "Detector-v1 versus Agent-4 mechanism boundary",
                "artifact": "2026-09-07-study1-data-log-pattern-transparency-he.pdf",
                "kind": "mechanism_boundary_diagram",
                "source_refs": ["study1-transparency-data-dictionary-v1.json"],
                "evidence_class": "ENGINEERING_ILLUSTRATION_ONLY",
                "scientific_denominator": "NOT_APPLICABLE",
                "status": "SAFE_RULE_VISUAL",
                "does_not_show": "queue volume, human workload, or model quality",
            },
            {
                "figure_id": "FIG-03",
                "title": "Public provenance and private-evidence boundary",
                "artifact": "2026-09-07-study1-data-log-pattern-transparency-he.pdf",
                "kind": "provenance_diagram",
                "source_refs": ["study1-data-provenance-v1.json"],
                "evidence_class": "ENGINEERING_ILLUSTRATION_ONLY",
                "scientific_denominator": "NOT_APPLICABLE",
                "status": "SAFE_RULE_VISUAL",
                "does_not_show": "accepted-run outcomes or empirical patterns",
            },
        ],
        "privacy": {
            "raw_prompts_answers_or_corpus_bytes": False,
            "private_paths_or_credentials": False,
            "provider_calls": 0,
            "new_scientific_data": 0,
        },
    }


def write_hebrew_note(path: Path, provenance: dict[str, Any], metrics: dict[str, Any]) -> None:
    """Write the supervisor-facing RTL Markdown note from structured data."""

    rows = log_contract_matrix()
    criteria = detector_criteria()
    cards = example_cards()
    lines = [
        '<div dir="rtl">',
        "# שקיפות נתונים, לוגים ודפוסים — VEGO-AI Study 1",
        "",
        "**סטטוס:** READY FOR SUPERVISOR TRANSPARENCY REVIEW — NOT A NEW SCIENTIFIC RESULT.",
        "**מקור הנתונים הפרטי:** `NOT_AVAILABLE_IN_WORKTREE`; לא הופקו נתונים מדעיים חדשים.",
        "המסמך מתעד את מקור הנתונים הציבורי ואת חוזי הקוד. הוא אינו מחליף מניפסט binding של ההרצה שהתקבלה.",
        "",
        "## 1. מקור הנתונים ובחירת המקרים",
        "",
        f"הגדרת ההכנה היא `setting_id={AIRTRAVEL_SETTING_ID}` ו-`corpus_id={AIRTRAVEL_CORPUS_ID}`. המקור הוא Text2UML ציבורי, commit `{AIRTRAVEL_UPSTREAM_COMMIT}`, תחת `dataset/AirTravel`.",
        f"ארכיון codeload אומת ב-SHA-256 `{provenance['dataset']['archive_sha256']}`; נבדקו {provenance['dataset']['airtravel_source_verification']['matched_count']} קבצים מתוך 143, ללא שינוי בתוכן. הקבצים הגולמיים אינם נשמרים ב-Git.",
        f"הפרדיקט הקבוע במניפסט מזהה {provenance['dataset']['selection'].get('eligible_case_count')} מועמדים מתאימים. הוא אינו מייצר בחירה ייחודית של ארבעה: הסטטוס הוא `{provenance['dataset']['selection_status']}`. {provenance['dataset']['selection_limitation']}",
        "",
        "| Runtime file | תפקיד | bytes | SHA-256 |",
        "|---|---|---:|---|",
    ]
    for selected in provenance["dataset"]["selected_runtime_files"]:
        lines.append(
            f"| `{selected['path']}` | {selected['role']} | {selected['bytes']} | `{selected['sha256']}` |"
        )
    lines.extend(
        [
            "",
        "### טבלת מקור קצרה",
        "",
        "| פריט | מקור | כיצד אומת | מה ניתן להסיק | מה לא ניתן להסיק |",
        "|---|---|---|---|---|",
        "| corpus AirTravel | Text2UML ציבורי | commit, archive SHA-256 וספירת קבצים | provenance והיתכנות | התנהגות תלמידים, נכונות או תועלת אנושית |",
        "| ארבעה candidates | `result_one_*` | eligibility predicate + recorded purposive proposal + SHA-256 | הכנת N=4 מתועדת; הבחירה אינה ניתנת לשחזור מן inventory בלבד | ייצוג סטטיסטי או ranking |",
        "| references | reference-only | מופרדים מנתיב runtime | גבול קלט ברור | מקור לתווית Detector |",
        "| accepted run | מניפסט פרטי נדרש | לא מותקן ב-worktree | אין ערך מספרי כרגע | כל מסקנה ניסויית |",
        "",
        "## 2. מערכת וגרסה",
        "",
        f"נבדקה גרסת VEGO-AI הציבורית [{PUBLIC_RELEASE}]({PUBLIC_RELEASE_URL}) באמצעות ארכיון ציבורי, SHA-256 `{PUBLIC_RELEASE_ARCHIVE_SHA256}`. קבצי המקור שנבדקו כוללים את `action_logger.py`, `GUI_Common.py`, `llm_client.py`, `orchestrator.py`, יצוא Agent 3, Agent 4 וה-evaluator.",
        "נוכחות פונקציה או נתיב בקוד אינה הוכחה שקובץ נוצר בהרצה. לכן כל שורת matrix מפרידה בין source-present לבין runtime-present.",
        "",
        "## 3. איזה לוג הוא מקור האמת?",
        "",
        "`qa_events.jsonl` של ה-recorder הקנוני הוא מקור האמת ל-Q&A ול-Detector-v1, כאשר הוא קיים ומחייב מניפסט binding מאומת. `interaction_log.json` הוא תיעוד קריאות LLM אפשרי; `user_actions.log` הוא לוג פעולות GUI. אף אחד משני אלה אינו מוכיח אפיזודת Q&A.",
        "יצוא Agent 3 (`cases_summary.csv`) הוא סיכום GUI. פלט Agent 4 הוא סיווג שונות נפרד. receipts/manifests משמשים לבקרת provenance ולבדיקת hashes, ולא מחליפים event log.",
        "",
        "| Artifact | יוצר | קיים במקור v2.1.5.3 | קיים בהרצה שנבדקה | מקור ל-Detector? | מגבלה מרכזית |",
        "|---|---|---:|---|---:|---|",
    ])
    for row in rows:
        lines.append(
            f"| `{row['artifact']}` | {row['produced_by']} | {('כן' if row['exists_in_official_v2_1_5_3_source'] else 'לא')} | `{row['exists_in_reviewed_run_worktree']}` | {('כן' if row['used_for_detector_v1'] else 'לא')} | {row['limitation']} |"
        )
    lines.extend(
        [
            "",
            "## 4. Detector-v1: כלל → שדה → פרשנות",
            "",
            "יחידת הניתוח היא Q&A episode. התווית היא reporting-level candidate-for-human-review בלבד; Detector-v1 אינו כותב תור. הנוסח הקפוא:",
            "",
            '<div dir="ltr">STRONG_ALERT = S1 OR S3 OR S7</div>',
            '<div dir="ltr">WEAK_ALERT = no strong signal AND (S2 OR S6)</div>',
            '<div dir="ltr">NO_ALERT otherwise</div>',
            "",
            "| אות | כלל קוד מדויק | שדות נדרשים | מה הוא אומר | מה אינו אומר | Accepted evidence |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in criteria:
        lines.append(
            f"| `{row['signal']}` | `{row['exact_code_rule']}` | `{', '.join(row['required_log_fields'])}` | {row['meaning']} | {row['does_not_mean']} | `{row['observed_in_accepted_evidence']}` |"
        )
    lines.extend(
        [
            "",
            "S1/S2 הם דיווח עצמי של המודל. S3 בודק null/אורך אפס בלבד; אורך ההפניה אינו איכות ראיה. S6 הוא תיאור מספר הסבבים. S7 הוא מצב סיום.",
            "",
            "## 5. מהו ‘דפוס’ כאן?",
            "",
            "| סוג מידע | יחידת ניתוח | דוגמה | מפעיל Detector-v1? | יוצר תור אנושי? | משמעות |",
            "|---|---|---|---:|---:|---|",
            "| Detector pattern | Q&A episode | S1/S3/S6/S7 | כן | לא | תנאי קפוא לדיווח |",
            "| descriptive communication statistic | route/case/round/run | מספר שאלות או routes | לא בהכרח | לא | תיאור תקשורת בלבד |",
            "| Agent-4 selective-intervention classification | Agent-4 variability classification | confidence/Undetermined | לא | queue builder נפרד עשוי ליצור | מנגנון פעולה נפרד |",
            "",
            "## 6. שני מנגנוני אדם נפרדים",
            "",
            "**Detector-v1:** אפיזודת Q&A, תווית מועמד לדיווח, ללא queue וללא שינוי אוטומטי.",
            "**Selective Intervention Policy / Agent-4:** סיווג השונות של Agent 4; queue builder נפרד עשוי לכתוב `human_review_queue.jsonl`. ב-AirTravel הסטטוס הוא `NOT_AVAILABLE` עד שקובץ queue מאומת יותקן. היעדרו אינו ‘not triggered’ ואינו אפס.",
            "בשני המנגנונים אין שינוי אוטומטי במקור, ביעד, בהנחיה או במודל.",
            "נתיב Agent-4 המתועד: הסיווג בוצע, נוצרה לפחות רשומת review אחת, ולאחר מכן הכתיבה נחסמה משום ש-`cd_airtravel` חסר ב-enum של הסכמה הישנה. לכן `queue_status=NOT_AVAILABLE`; אין לכתוב ‘not triggered’.",
            "",
            "## 6א. זמינות case→model ומטא־דאטה של קוד הדיווח",
            "",
            "| אפיזודה | קישור למקרה | זמינות מודל | סטטוס ראיות |",
            "|---|---|---|---|",
        ]
    )
    for episode_id, status in case_model_availability().items():
        lines.append(
            f"| `{episode_id}` | {status['case_linkage']} | `{status['model_availability']}` | `{status['evidence_status']}` |"
        )
    lines.extend(
        [
            "אין להסיק זמינות מודל מהגדרת הקונפיגורציה. `reporting_code_sha` הוא מטא־דאטה תיעודי לא־ראייתי; הקוד שביצע היסטורית והקוד שמדווח כיום אינם byte-identical.",
            "",
            "## 7. כרטיסי דוגמה למנחים",
            "",
        ]
    )
    for card in cards:
        lines.extend(
            [
                f"### {card['card_id']} — {card['title_he']}",
                f"**{card['banner']}**",
                f"**{card['banner_he']}**",
                f"Input/case: `{card['input_case']}` → log: `{card['log_fields']}` → rule: `{card['detector_rule']}` → result: `{card['detector_result']}`.",
                f"**פירוש:** {card['interpretation_he']} **מגבלה:** {card['limitation_he']}",
                "",
            ]
        )
        if card.get("card_id") == "EP-577319bf":
            field_summary = "; ".join(
                f"{name}={value}" for name, value in card.get("fields", {}).items()
            )
            lines.insert(
                len(lines) - 2,
                f"**שדות מצונזרים/בטוחים:** `{field_summary}`",
            )
    lines.extend(
        [
            "כל ארבעת הכרטיסים הם `ENGINEERING_ILLUSTRATION_ONLY` ואינם נכנסים לטבלת מדדים מדעית. הדוגמה של EP-577319bf37c87 משתמשת בהפניות hash בלבד ובתוכן מצונזר.",
            "",
            "## 8. מה נצפה ומה לא נצפה",
            "",
            "**נצפה:** חוזי קוד ציבוריים, נתיבי יצוא ושדות Detector מוגדרים. **לא נצפה:** כל דפוס אמפירי של Study 1, משום שקובץ האירועים הפרטי וה-binding manifest של ההרצה שהתקבלה אינם מותקנים ב-worktree. לכן S1–S7 מוצגים ככללים קיימים עם observed count = `NOT_AVAILABLE_IN_WORKTREE`, ולא כממצאים.",
            "גם Agent-4 queue הוא `NOT_AVAILABLE`; אין להסיק מכך שלא הופעל.",
            "",
            "## 9. פרטיות, שחזור וגבולות טענה",
            "",
            "לא נקראו credentials, prompts, answers או raw outputs. אין להכניס אותם ל-Git. כדי לחשב מדדים בעתיד יש לספק binding manifest פרטי, לאמת SHA-256, run identity ושלמות lifecycle, ואז לחשב רק מה-event log. אין להסיק accuracy, precision/recall, correctness, human benefit, causality, generalization או superiority.",
            "מניפסט האיורים `study1-transparency-figures-manifest-v1.json` מתעד שלושה איורי כלל/גבול בטוחים; אין בו נתוני ניסוי או גרף מדעי.",
            "פקודות שחזור offline בלבד: `uv run python scripts/build_study1_transparency_package.py --output-dir <safe-output>` ולאחר מכן `uv run pytest -q scripts/tests/test_study1_transparency_package.py`. לא מופעל provider או model.",
            "",
            "## 10. שאלות לאיריס ולארנון",
            "",
            "1. האם `qa_events.jsonl` המקורי וה-binding manifest של ההרצה שהתקבלה זמינים בנתיב פרטי מאושר?",
            "2. האם תרצו לאשר ש-Detector-v1 נשאר תווית דיווח ללא queue, ו-Agent-4 הוא מנגנון queue נפרד?",
            "3. האם כלל הבחירה של ארבעת AirTravel candidates והפרדת reference-only מתאימים להצגה?",
            "4. אילו שדות תרצו לראות בדוח הבא לאחר אימות ה-event log, בלי להרחיב את טענות המחקר?",
            "",
            "*טיוטה בסיוע מכונה; המשמעות בעברית מחייבת ביקורת אנושית.*",
            "</div>",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_hebrew_pdf(path: Path, provenance: dict[str, Any], metrics: dict[str, Any]) -> None:
    """Create the concise two-page RTL meeting brief (no private evidence)."""

    try:
        from bidi.algorithm import get_display
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
    except ImportError as exc:  # pragma: no cover - exercised only in PDF runtime
        raise TransparencyValidationError(f"PDF dependencies unavailable: {exc}") from exc

    path.parent.mkdir(parents=True, exist_ok=True)
    font_name = "Helvetica"
    bold_name = "Helvetica-Bold"
    arial = Path("C:/Windows/Fonts/arial.ttf")
    arial_bold = Path("C:/Windows/Fonts/arialbd.ttf")
    if arial.is_file() and arial_bold.is_file():
        pdfmetrics.registerFont(TTFont("VegoArial", str(arial)))
        pdfmetrics.registerFont(TTFont("VegoArialBold", str(arial_bold)))
        font_name, bold_name = "VegoArial", "VegoArialBold"

    page_width, page_height = A4
    margin = 38
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle("VEGO-AI Study 1 - Data, Log and Pattern Transparency")

    def visual(text: str) -> str:
        return get_display(text) if any("\u0590" <= char <= "\u05ff" for char in text) else text

    def rtl(text: str, x: float, y: float, *, size: float = 9, bold: bool = False, color=None) -> None:
        if color is None:
            color = colors.HexColor("#17202A")
        c.setFont(bold_name if bold else font_name, size)
        c.setFillColor(color)
        c.drawRightString(page_width - x, y, visual(text))

    def ltr(text: str, x: float, y: float, *, size: float = 8, bold: bool = False, color=None) -> None:
        if color is None:
            color = colors.HexColor("#17202A")
        c.setFont(bold_name if bold else font_name, size)
        c.setFillColor(color)
        c.drawString(x, y, text)

    def box(x: float, y: float, w: float, h: float, fill: str, stroke: str = "#D7DEE8") -> None:
        c.setFillColor(colors.HexColor(fill))
        c.setStrokeColor(colors.HexColor(stroke))
        c.roundRect(x, y, w, h, 7, fill=1, stroke=1)

    def wrap(text: str, max_width: float, size: float = 8) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if pdfmetrics.stringWidth(visual(candidate), font_name, size) <= max_width or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def paragraph(text: str, x: float, y: float, width: float, *, size: float = 8, leading: float = 11, color=None) -> float:
        if color is None:
            color = colors.HexColor("#17202A")
        for line in wrap(text, width, size):
            rtl(line, x, y, size=size, color=color)
            y -= leading
        return y

    def header(page_number: int) -> None:
        c.setFillColor(colors.HexColor("#0F4C81"))
        c.rect(0, page_height - 24, page_width, 24, fill=1, stroke=0)
        ltr("VEGO-AI  |  STUDY 1 TRANSPARENCY", margin, page_height - 16, size=8, bold=True, color=colors.white)
        ltr(f"{page_number} / 2", page_width - margin - 25, page_height - 16, size=8, color=colors.white)
        c.setStrokeColor(colors.HexColor("#D7DEE8"))
        c.line(margin, 27, page_width - margin, 27)
        ltr("Evidence boundary: no private accepted-run event log mounted", margin, 16, size=7, color=colors.HexColor("#5D6D7E"))
        ltr("Provider/API/model calls: 0  |  New scientific run: 0", page_width - margin - 220, 16, size=7, color=colors.HexColor("#5D6D7E"))

    # Page 1: provenance and source-of-truth.
    header(1)
    rtl("שקיפות נתונים, לוגים ודפוסים", margin, page_height - 58, size=20, bold=True, color=colors.HexColor("#0F4C81"))
    rtl("VEGO-AI Study 1 | תקציר למפגש מנחים", margin, page_height - 79, size=10, color=colors.HexColor("#5D6D7E"))
    box(margin, page_height - 138, page_width - 2 * margin, 40, "#EAF4FB", "#9CC7E5")
    rtl("סטטוס: READY FOR SUPERVISOR TRANSPARENCY REVIEW — NOT A NEW SCIENTIFIC RESULT", margin + 12, page_height - 116, size=9, bold=True, color=colors.HexColor("#0B3D62"))
    rtl("ה-event log הפרטי ומניפסט ה-binding אינם זמינים ב-worktree; אין כאן מספרים מדעיים.", margin + 12, page_height - 131, size=8, color=colors.HexColor("#0B3D62"))

    rtl("1. מקור ובחירת מקרים", margin, page_height - 166, size=12, bold=True, color=colors.HexColor("#0F4C81"))
    y = page_height - 184
    selection = provenance["dataset"].get("selection", {})
    y = paragraph(
        f"המקור הוא Text2UML/AirTravel ציבורי, commit {AIRTRAVEL_UPSTREAM_COMMIT}, תחת dataset/AirTravel. ארכיון codeload: {provenance['dataset']['archive_sha256']}; אימות קבצים: {provenance['dataset']['airtravel_source_verification']['status']}. הפרדיקט מזהה {selection.get('eligible_case_count')} מועמדים, אך N=4 הוא בחירה purposive שאינה ניתנת לשחזור מן inventory בלבד ({selection.get('status')}); אין זה נתון תלמידים, Cheers/ParkWise או ground truth.",
        margin,
        y,
        page_width - 2 * margin,
        size=8.5,
        leading=12,
    )
    y -= 5
    c.setFillColor(colors.HexColor("#F7F9FB"))
    c.roundRect(margin, y - 119, page_width - 2 * margin, 119, 5, fill=1, stroke=0)
    rtl("קבצי runtime שנבחרו (hash-bound)", margin + 10, y - 17, size=9, bold=True, color=colors.HexColor("#0F4C81"))
    table_y = y - 34
    rtl("קובץ", margin + 10, table_y, size=7, bold=True)
    ltr("bytes", margin + 230, table_y, size=7, bold=True)
    ltr("SHA-256", margin + 275, table_y, size=7, bold=True)
    for selected in provenance["dataset"]["selected_runtime_files"]:
        table_y -= 16
        short_path = selected["path"].split("/")[-1]
        if len(short_path) > 31:
            short_path = short_path[:13] + "..." + short_path[-15:]
        rtl(short_path, margin + 10, table_y, size=6.2)
        ltr(str(selected["bytes"]), margin + 230, table_y, size=6.6)
        ltr(selected["sha256"][:20] + "...", margin + 275, table_y, size=6.6, color=colors.HexColor("#34495E"))
    y -= 134
    rtl("2. מקור האמת ללוגים", margin, y, size=12, bold=True, color=colors.HexColor("#0F4C81"))
    y -= 18
    paragraph("qa_events.jsonl הוא מקור האמת ל-Q&A ול-Detector-v1 כאשר הוא קיים ומאומת. interaction_log.json הוא לוג קריאות LLM אפשרי; user_actions.log הוא לוג פעולות GUI. יצוא Agent 3 הוא סיכום GUI; Agent 4 הוא סיווג שונות נפרד. source-present אינו runtime-present.", margin, y, page_width - 2 * margin, size=8.2, leading=11)
    c.showPage()

    # Page 2: detector, mechanisms, examples and boundaries.
    header(2)
    rtl("3. כלל ההתראה והפרדת מנגנוני האדם", margin, page_height - 58, size=15, bold=True, color=colors.HexColor("#0F4C81"))
    box(margin, page_height - 150, page_width - 2 * margin, 70, "#F2F8F2", "#A8D5B0")
    rtl("איך ההתראה החכמה עובדת", margin + 12, page_height - 102, size=10, bold=True, color=colors.HexColor("#236B35"))
    ltr("STRONG_ALERT = S1 OR S3 OR S7", margin + 14, page_height - 120, size=9, bold=True, color=colors.HexColor("#236B35"))
    ltr("WEAK_ALERT = no strong signal AND (S2 OR S6)", margin + 14, page_height - 135, size=9, bold=True, color=colors.HexColor("#236B35"))
    rtl("Detector-v1: יחידת ניתוח Q&A episode; תווית reporting בלבד; אינו כותב queue.", margin + 12, page_height - 147, size=7.8, color=colors.HexColor("#236B35"))
    rtl("Agent-4: יחידת ניתוח Agent-4 variability classification; queue builder נפרד עשוי ליצור human_review_queue.jsonl.", margin, page_height - 172, size=8.2, color=colors.HexColor("#17202A"))
    rtl("AirTravel queue status: NOT_AVAILABLE — היעדר קובץ אינו ‘not triggered’.", margin, page_height - 187, size=8.2, bold=True, color=colors.HexColor("#A04000"))

    rtl("4. ארבעה כרטיסי המחשה", margin, page_height - 217, size=12, bold=True, color=colors.HexColor("#0F4C81"))
    card_y = page_height - 240
    card_h = 50
    card_colors = ["#F7F9FB", "#FFF8E7", "#F5F0FA", "#EEF5FC"]
    card_titles = [
        "EX-01 | אפיזודה מלאה ללא התראה",
        "EX-02 | Low confidence → Strong",
        "EX-03 | Agent-4 queue נפרד",
        "EP-577319bf | דוגמה אמיתית מצונזרת",
    ]
    card_bodies = [
        "QUESTION → ANSWER High + evidence → CONVERGED → NO_ALERT; אינו מוכיח נכונות.",
        "ANSWER confidence=Low → S1 → STRONG_ALERT; דיווח עצמי, לא תווית שגיאה.",
        "classification=Undetermined → queue builder נפרד; Detector-v1 NOT_APPLICABLE.",
        "case 02 → Q&A 1/1 → S1 → STRONG_ALERT; hash refs בלבד, תוכן מצונזר.",
    ]
    for idx in range(len(card_titles)):
        box(margin, card_y - card_h, page_width - 2 * margin, card_h, card_colors[idx])
        rtl(card_titles[idx], margin + 10, card_y - 17, size=8.6, bold=True, color=colors.HexColor("#273746"))
        rtl("המחשה הנדסית בלבד — אינה תוצאת ניסוי ואינה נתון אמפירי", margin + 10, card_y - 31, size=7.4, color=colors.HexColor("#7D3C0C"))
        rtl(card_bodies[idx], margin + 10, card_y - 45, size=7.5, color=colors.HexColor("#273746"))
        card_y -= card_h + 9

    rtl("5. מה ניתן לומר עכשיו?", margin, card_y - 4, size=12, bold=True, color=colors.HexColor("#0F4C81"))
    paragraph("נצפו חוזי קוד, נתיבי export והגדרות Detector. לא נצפה דפוס אמפירי של Study 1: observed count לכל S1/S2/S3/S6/S7 הוא NOT_AVAILABLE_IN_WORKTREE. אין להסיק accuracy, correctness, human benefit, causality, generalization או superiority.", margin, card_y - 22, page_width - 2 * margin, size=8.2, leading=11)
    rtl("המשך נדרש: מניפסט binding פרטי, אימות SHA-256 ושלמות lifecycle; לאחר מכן חישוב מה-event log בלבד.", margin, 72, size=8.2, bold=True, color=colors.HexColor("#0F4C81"))
    c.showPage()
    c.save()


def _csv_write(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: json.dumps(value, ensure_ascii=False, separators=(",", ":"))
                    if isinstance(value, (list, dict))
                    else value
                    for key, value in row.items()
                }
            )


def write_package(
    output_dir: Path,
    *,
    reviewed_head_sha: str,
    main_sha: str,
    airtravel_archive_sha256: str | None = None,
    airtravel_file_count: int | None = None,
    airtravel_matched_count: int | None = None,
    airtravel_archive_path: Path | None = None,
    airtravel_source_manifest_path: Path = SOURCE_MANIFEST,
    official_release_archive_path: Path | None = None,
) -> dict[str, Path]:
    """Write all tracked transparency artifacts to ``output_dir``."""

    output_dir.mkdir(parents=True, exist_ok=True)
    if airtravel_archive_path is None and any(
        value is not None
        for value in (airtravel_archive_sha256, airtravel_file_count, airtravel_matched_count)
    ):
        raise TransparencyValidationError(
            "AirTravel file counts/hash require the actual pinned archive; pass --airtravel-archive"
        )
    verification = (
        verify_airtravel_archive(airtravel_archive_path, airtravel_source_manifest_path)
        if airtravel_archive_path is not None
        else None
    )
    if verification is not None and verification.get("status") != "PASS":
        raise TransparencyValidationError("public AirTravel archive verification failed closed")
    release_verification = (
        verify_official_release_archive(official_release_archive_path)
        if official_release_archive_path is not None
        else None
    )
    if release_verification is not None and release_verification.get("status") != "PASS":
        raise TransparencyValidationError("public VEGO-AI release verification failed closed")
    provenance = build_provenance_record(
        reviewed_head_sha=reviewed_head_sha,
        main_sha=main_sha,
        airtravel_archive_sha256=airtravel_archive_sha256,
        airtravel_file_count=airtravel_file_count,
        airtravel_matched_count=airtravel_matched_count,
        airtravel_verification=verification,
        official_release_verification=release_verification,
    )
    provenance_errors = validate_provenance_record(provenance)
    if provenance_errors:
        raise TransparencyValidationError("; ".join(provenance_errors))
    metrics = safe_metrics(None)
    source = DETECTOR_SOURCE.read_text(encoding="utf-8")
    criteria = detector_criteria()
    errors = validate_detector_criteria(criteria, source)
    if errors:
        raise TransparencyValidationError("; ".join(errors))
    paths: dict[str, Path] = {}
    paths["provenance"] = output_dir / "study1-data-provenance-v1.json"
    paths["provenance"].write_text(json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    matrix_rows = log_contract_matrix()
    paths["matrix"] = output_dir / "study1-log-contract-matrix-v1.csv"
    _csv_write(paths["matrix"], matrix_rows, list(matrix_rows[0]))
    paths["detector"] = output_dir / "detector-v1-criteria-to-log-fields-v1.csv"
    _csv_write(paths["detector"], criteria, list(criteria[0]))
    paths["metrics"] = output_dir / "study1-transparency-metrics-v1.json"
    paths["metrics"].write_text(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["data_dictionary"] = output_dir / "study1-transparency-data-dictionary-v1.json"
    paths["data_dictionary"].write_text(
        json.dumps(
            transparency_data_dictionary(reviewed_head_sha=reviewed_head_sha, main_sha=main_sha),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    paths["selection"] = output_dir / "study1-airtravel-selection-v1.json"
    paths["selection"].write_text(
        json.dumps(provenance["dataset"]["selection"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["case_model_availability"] = output_dir / "study1-case-model-availability-v1.json"
    paths["case_model_availability"].write_text(
        json.dumps(case_model_availability(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["reporting_code_metadata"] = output_dir / "study1-reporting-code-metadata-v1.json"
    paths["reporting_code_metadata"].write_text(
        json.dumps(reporting_code_metadata(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["figures_manifest"] = output_dir / "study1-transparency-figures-manifest-v1.json"
    paths["figures_manifest"].write_text(
        json.dumps(transparency_figure_manifest(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["hebrew_note"] = output_dir / "2026-09-07-study1-data-log-pattern-transparency-he.md"
    write_hebrew_note(paths["hebrew_note"], provenance, metrics)
    paths["pattern_note"] = output_dir / "detector-v1-pattern-explanation-he.md"
    paths["pattern_note"].write_text(
        '<div dir="rtl">\n# הסבר דפוסי Detector-v1\n\n'
        "האותות הם כללים קפואים על Q&A episode; ספירות route/round הן תיאורים; סיווג Agent-4 ותור human_review_queue.jsonl הם מנגנון נפרד.\n\n"
        '<div dir="ltr">STRONG_ALERT = S1 OR S3 OR S7</div>\n'
        '<div dir="ltr">WEAK_ALERT = no strong signal AND (S2 OR S6)</div>\n'
        '<div dir="ltr">NO_ALERT otherwise</div>\n\n'
        "אין נתונים פרטיים זמינים, ולכן כל observed count הוא `NOT_AVAILABLE_IN_WORKTREE`.\n</div>\n",
        encoding="utf-8",
    )
    paths["slides"] = output_dir / "2026-09-07-study1-transparency-slides.he.md"
    paths["slides"].write_text(
        '<div dir="rtl">\n# מתווה 4 שקופיות — שקיפות Study 1\n\n'
        "## שקופית 1 — מאיפה הנתונים?\nText2UML/AirTravel ציבורי, commit קפוא, ארבעה candidates, לא תלמידים ולא Cheers/ParkWise.\n\n"
        "## שקופית 2 — איזה לוג?\n`qa_events.jsonl` הוא מקור Q&A; `interaction_log.json` ו-`user_actions.log` הם audit/UI; נוכחות source אינה נוכחות runtime.\n\n"
        "## שקופית 3 — איך ההתראה עובדת?\nSTRONG=S1/S3/S7; WEAK=S2/S6; תווית מועמד לדיווח בלבד. Agent-4 queue נפרד ו-AirTravel `NOT_AVAILABLE`.\n\n"
        "## שקופית 4 — מה מותר לומר?\nאין event log פרטי מאומת ב-worktree; אין ממצא אמפירי. ארבעת הכרטיסים הם המחשה הנדסית בלבד; מניפסט האיורים מתעד רק איורי כלל/גבול; השלב הבא הוא binding manifest.\n</div>\n",
        encoding="utf-8",
    )
    paths["email"] = output_dir / "2026-09-07-study1-transparency-email-draft.he.md"
    paths["email"].write_text(
        '<div dir="rtl">\n**נושא:** עדכון שקיפות הנתונים והלוגים ב-Study 1\n\n'
        "איריס וארנון שלום,\n\nאני מסכים שההסבר הקודם לא היה שקוף מספיק. הכנתי שרשרת ברורה: נתונים → לוג → כלל → פירוש. לא אטען ש-`interaction_log.json` שימש לניתוח לפני שאאמת את קובץ ההרצה ואת מיפוי השדות.\n\n"
        "הכלל ‘אין תשובה ללא ראיות’ מוצג ככלל S3 בלבד, ולא כממצא שנצפה, משום שקובץ האירועים הפרטי אינו זמין ב-worktree שנבדק. בדקתי את VEGO-AI v2.1.5.3 ואיישרתי את ההסבר למנגנוני logging/export האמיתיים.\n\n"
        "אשמח לאישור האם 08:00 מתאים לכם.\n\nבברכה,\nעלי\n</div>\n",
        encoding="utf-8",
    )
    paths["validation_receipt"] = output_dir / "study1-transparency-validation-receipt-v1.json"
    receipt = {
        "schema_version": "study1-transparency-validation-receipt-v1",
        "status": "PASS_SAFE_PACKAGE_NO_PRIVATE_EVIDENCE",
        "provenance_status": provenance["dataset"]["airtravel_source_verification"]["status"],
        "private_evidence_status": NOT_AVAILABLE,
        "detector_criteria_status": "PASS",
        "mechanism_separation_status": "PASS",
        "provider_api_model_calls": 0,
        "paid_calls": 0,
        "credentials_read": 0,
        "new_scientific_run": 0,
        "detector_experimental_run": 0,
        "synthetic_scientific_evidence": 0,
        "protected_runtime_changes": 0,
        "claim_boundary": "READY FOR SUPERVISOR TRANSPARENCY REVIEW — NOT A NEW SCIENTIFIC RESULT",
    }
    paths["validation_receipt"].write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "research" / "phd-proposal")
    parser.add_argument("--reviewed-head-sha", default="6d7f9dcef6c033c98dc1717e973a0714034aea82")
    parser.add_argument("--main-sha", default="158714064a2ecc40f5eda8561240978ebfe1b371")
    parser.add_argument("--airtravel-archive-sha256", default=None)
    parser.add_argument("--airtravel-file-count", type=int, default=None)
    parser.add_argument("--airtravel-matched-count", type=int, default=None)
    parser.add_argument("--airtravel-archive", type=Path, default=None, help="temporary public codeload ZIP; never copied")
    parser.add_argument("--airtravel-source-manifest", type=Path, default=SOURCE_MANIFEST)
    parser.add_argument("--official-release-archive", type=Path, default=None, help="temporary public VEGO-AI release ZIP; never copied")
    parser.add_argument("--pdf", type=Path, default=None, help="optional two-page Hebrew PDF output")
    args = parser.parse_args(argv)
    paths = write_package(
        args.output_dir,
        reviewed_head_sha=args.reviewed_head_sha,
        main_sha=args.main_sha,
        airtravel_archive_sha256=args.airtravel_archive_sha256,
        airtravel_file_count=args.airtravel_file_count,
        airtravel_matched_count=args.airtravel_matched_count,
        airtravel_archive_path=args.airtravel_archive,
        airtravel_source_manifest_path=args.airtravel_source_manifest,
        official_release_archive_path=args.official_release_archive,
    )
    for key, path in paths.items():
        print(f"{key}: {path.as_posix()}")
    if args.pdf is not None:
        provenance = json.loads(paths["provenance"].read_text(encoding="utf-8"))
        metrics = json.loads(paths["metrics"].read_text(encoding="utf-8"))
        write_hebrew_pdf(args.pdf, provenance, metrics)
        print(f"pdf: {args.pdf.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
