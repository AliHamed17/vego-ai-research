"""Versioned, fail-closed contracts for the future AirTravel preflight.

This module is deliberately independent of the protected VEGO runtime. It
binds one machine-readable packet, one fixed private run root, one durable
attempt marker, and privacy-safe call-level parity records. It does not run
the orchestrator or any provider.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKET_VERSION = "v4"
RUN_ROOT = "external_data/airtravel-pr38/v4-authorized-fake-run"
PACKET_PATH = "docs/research/phd-proposal/2026-09-05-airtravel-protected-fake-preflight-authorization-packet-v4.md"
MANIFEST_PATH = (
    "docs/research/phd-proposal/airtravel-pr38-correction/"
    "airtravel-v4-packet-manifest.json"
)
REQUEST_PATH = RUN_ROOT + "/control/private-execution-request.json"
GRANT_SCHEMA_PATH = "schemas/airtravel-fake-grant-v2.schema.json"
RECEIPT_SCHEMA_PATH = "schemas/airtravel-technical-receipt-v2.schema.json"
PROTECTED_MANIFEST_PATH = (
    "docs/research/phd-proposal/airtravel-pr38-correction/protected-hashes.json"
)
HARNESS_CODE_PATHS = (
    "scripts/airtravel_v4_contract.py",
    "scripts/airtravel_v4_execution.py",
)
SCHEMA_PATHS = (
    "schemas/airtravel-v4-packet-manifest-v1.schema.json",
    "schemas/airtravel-fake-grant-v2.schema.json",
    "schemas/airtravel-technical-receipt-v2.schema.json",
)
BASE_SHA = "c34d3954b5e080d090017d2ea655d454d75a6b92"
IMPLEMENTATION_ANCESTOR = "28a1d95f39058e5b9dd3e7601584e2393311d405"
SETTING_ID = "cd_airtravel"
CORPUS_ID = "text2uml_airtravel_253b26dc"
N = 4
TIMEOUT_SECONDS = 1800
MIN_CALLS = 16
MAX_CALLS = 326
MAX_INVOCATIONS = 1
RUNTIME_ARCHIVE_SHA256 = "e37baecd20a0c84eb1d9b87b3b78a23bc4b4eb8a9824ad3086dc30aa35fdd31f"
RUNTIME_FILES = {
    "domain_description/description.md": {
        "sha256": "96bc8a6fbf2c2fdd93592fdbf6fac7c2b9db403494fe2d5a45e0a2bcbf0167e2",
        "bytes": 1477,
    },
    "candidate_models/01_result_one_claude-sonnet-4-6.txt": {
        "sha256": "240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91",
        "bytes": 1248,
    },
    "candidate_models/02_result_one_codestral-2508.txt": {
        "sha256": "08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6",
        "bytes": 1272,
    },
    "candidate_models/03_result_one_deepseek-chat.txt": {
        "sha256": "ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a",
        "bytes": 1324,
    },
    "candidate_models/04_result_one_gemini-2.5-flash.txt": {
        "sha256": "1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a",
        "bytes": 1231,
    },
}
SAFETY_COUNTERS = (
    "external_provider_call_count",
    "paid_provider_call_count",
    "provider_constructor_attempt_count",
    "provider_import_attempt_count",
    "network_socket_attempt_count",
    "DNS_attempt_count",
    "credential_access_attempt_count",
    "subprocess_attempt_count",
    "native_escape_attempt_count",
    "detector_v1_run_count",
    "renderer_run_count",
    "provider_backed_production_route_pair_count",
)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
        "utf-8"
    )


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _path(value: str, field: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty relative path")
    if "\\" in value or re.match(r"^[A-Za-z]:", value) or value.startswith(("/", "//")):
        raise ValueError(f"{field} must use a repository-relative POSIX path")
    # PurePosixPath normalizes repeated separators and dot segments.  Check
    # the lexical representation first so identity cannot change silently.
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"{field} contains traversal or normalization")
    parsed = PurePosixPath(value)
    return parsed


def _under(value: str, root: str, field: str) -> None:
    parsed = _path(value, field)
    root_path = _path(root, "run_root")
    if parsed != root_path and root_path not in parsed.parents:
        raise ValueError(f"{field} escapes run_root")


def _layout() -> dict[str, list[str]]:
    return {
        "control": [
            "private-execution-request.json",
            "authorization-grant.message.txt",
            "authorization-grant.json",
            "execution-command.json",
            "preparation-receipt.json",
            "attempt-start.json",
            "attempt-end.json",
        ],
        "output": ["baseline", "instrumented", "preflight-receipt.json"],
        "verification": [
            "final-output-inventory.json",
            "parity-verification.json",
            "lifecycle-verification.json",
            "post-verification-receipt.json",
        ],
    }


def _evidence_files() -> list[str]:
    return [
        "output/baseline/call-records.jsonl",
        "output/instrumented/call-records.jsonl",
        "output/instrumented/qa_events.jsonl",
        "output/preflight-receipt.json",
        "verification/final-output-inventory.json",
        "verification/parity-verification.json",
        "verification/lifecycle-verification.json",
        "verification/post-verification-receipt.json",
        "control/attempt-start.json",
        "control/attempt-end.json",
    ]


def frozen_manifest() -> dict[str, Any]:
    """Return the deterministic machine constraints for packet v4."""
    protected_manifest = ROOT / PROTECTED_MANIFEST_PATH
    harness_hashes = {
        path: digest(ROOT / path) for path in HARNESS_CODE_PATHS
    }
    schema_hashes = {path: digest(ROOT / path) for path in SCHEMA_PATHS}
    return {
        "manifest_version": "airtravel-v4-packet-manifest-v1",
        "packet_version": PACKET_VERSION,
        "packet_path": PACKET_PATH,
        "base_sha": BASE_SHA,
        "implementation_commit_ancestor": IMPLEMENTATION_ANCESTOR,
        "reviewed_head": "GRANT_BOUND_REVIEWED_HEAD",
        "setting_id": SETTING_ID,
        "corpus_id": CORPUS_ID,
        "N": N,
        "runtime_archive_sha256": RUNTIME_ARCHIVE_SHA256,
        "runtime_files": RUNTIME_FILES,
        "protected_manifest_path": PROTECTED_MANIFEST_PATH,
        "protected_manifest_sha256": digest(protected_manifest),
        "harness_code_hashes": harness_hashes,
        "schema_hashes": schema_hashes,
        "run_root": RUN_ROOT,
        "control_root": RUN_ROOT + "/control",
        "output_root": RUN_ROOT + "/output",
        "verification_root": RUN_ROOT + "/verification",
        "required_layout": _layout(),
        "required_evidence_files": _evidence_files(),
        "command_template": [
            "python",
            "scripts/prepare_airtravel_v4.py",
            "--execute",
            "--packet",
            PACKET_PATH,
            "--grant",
            RUN_ROOT + "/control/authorization-grant.json",
            "--runtime-root",
            "external_data/airtravel-pr38/runtime_input",
            "--runtime-archive",
            "external_data/airtravel-pr38/cd_airtravel-runtime-v1.0.2.zip",
            "--output-dir",
            RUN_ROOT + "/output",
            "--receipt",
            RUN_ROOT + "/output/preflight-receipt.json",
        ],
        "timeout_seconds": TIMEOUT_SECONDS,
        "minimum_calls_per_pass": MIN_CALLS,
        "maximum_calls_per_pass": MAX_CALLS,
        "maximum_invocations": MAX_INVOCATIONS,
        "network_forbidden": True,
        "external_provider_calls_allowed": 0,
        "detector_v1_forbidden": True,
        "renderer_forbidden": True,
        "allowed_write_roots": [RUN_ROOT],
        "prohibited_write_roots": [
            "VEGO-AI/",
            "scripts/",
            "schemas/",
            "docs/research/",
            "reports/",
        ],
        "provider_execution_enabled": False,
    }


def request_template() -> dict[str, Any]:
    manifest = frozen_manifest()
    return {
        "schema_version": "airtravel-v4-execution-request-v1",
        "status": "AUTHORIZATION_REQUESTED_NOT_GRANTED",
        "packet_version": PACKET_VERSION,
        "packet_manifest_path": MANIFEST_PATH,
        "run_root": manifest["run_root"],
        "control_root": manifest["control_root"],
        "output_root": manifest["output_root"],
        "verification_root": manifest["verification_root"],
        "receipt_path": manifest["output_root"] + "/preflight-receipt.json",
        "attempt_start_path": manifest["control_root"] + "/attempt-start.json",
        "attempt_end_path": manifest["control_root"] + "/attempt-end.json",
        "setting_id": SETTING_ID,
        "corpus_id": CORPUS_ID,
        "N": N,
        "maximum_invocations": MAX_INVOCATIONS,
        "timeout_seconds": TIMEOUT_SECONDS,
        "minimum_calls_per_pass": MIN_CALLS,
        "maximum_calls_per_pass": MAX_CALLS,
        "runtime_archive_sha256": manifest["runtime_archive_sha256"],
        "runtime_file_hashes": {key: value["sha256"] for key, value in manifest["runtime_files"].items()},
        "network_forbidden": manifest["network_forbidden"],
        "external_provider_calls_allowed": manifest["external_provider_calls_allowed"],
        "provider_execution_enabled": manifest["provider_execution_enabled"],
        "detector_v1_forbidden": manifest["detector_v1_forbidden"],
        "renderer_forbidden": manifest["renderer_forbidden"],
        "command_template": manifest["command_template"],
        "allowed_write_roots": manifest["allowed_write_roots"],
        "prohibited_write_roots": manifest["prohibited_write_roots"],
        "required_evidence_files": manifest["required_evidence_files"],
        "protected_manifest_path": manifest["protected_manifest_path"],
        "protected_manifest_sha256": manifest["protected_manifest_sha256"],
        "harness_code_hashes": manifest["harness_code_hashes"],
        "schema_hashes": manifest["schema_hashes"],
    }


def grant_template() -> dict[str, Any]:
    """A non-authorizing template; owner grant creation is a later human gate."""
    manifest = frozen_manifest()
    request = request_template()
    return {
        "schema_version": "airtravel-fake-grant-v2",
        "status": "AUTHORIZATION_REQUESTED_NOT_GRANTED",
        "grant_type": "OFFLINE_FAKE_PREFLIGHT_ONLY",
        "granted_by": "Ali Hamed",
        "reviewed_head": "GRANT_BOUND_REVIEWED_HEAD",
        "implementation_commit_ancestor": IMPLEMENTATION_ANCESTOR,
        "packet_manifest_sha256": "0" * 64,
        "authorization_message_sha256": "0" * 64,
        "grant_sha256": "GRANT_SELF_HASH_EXCLUDED",
        "command_sha256": "0" * 64,
        "run_root": manifest["run_root"],
        "control_root": request["control_root"],
        "output_root": request["output_root"],
        "verification_root": request["verification_root"],
        "setting_id": SETTING_ID,
        "corpus_id": CORPUS_ID,
        "N": N,
        "runtime_archive_sha256": RUNTIME_ARCHIVE_SHA256,
        "runtime_file_hashes": {key: value["sha256"] for key, value in RUNTIME_FILES.items()},
        "command_template": manifest["command_template"],
        "protected_manifest_path": manifest["protected_manifest_path"],
        "protected_manifest_sha256": manifest["protected_manifest_sha256"],
        "harness_code_hashes": manifest["harness_code_hashes"],
        "schema_hashes": manifest["schema_hashes"],
        "timeout_seconds": TIMEOUT_SECONDS,
        "minimum_calls_per_pass": MIN_CALLS,
        "maximum_calls_per_pass": MAX_CALLS,
        "maximum_invocations": MAX_INVOCATIONS,
        "network_forbidden": True,
        "external_provider_calls_allowed": 0,
        "paid_execution_authorized": False,
        "provider_execution_enabled": False,
        "detector_v1_forbidden": True,
        "renderer_forbidden": True,
        "allowed_write_roots": manifest["allowed_write_roots"],
        "prohibited_write_roots": manifest["prohibited_write_roots"],
        "required_evidence_files": manifest["required_evidence_files"],
    }


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("manifest_version") != "airtravel-v4-packet-manifest-v1":
        raise ValueError("machine packet manifest version rejected")
    if manifest.get("packet_version") != PACKET_VERSION:
        raise ValueError("packet version rejected")
    if manifest.get("run_root") != RUN_ROOT:
        raise ValueError("run_root is not the fixed v4 root")
    if manifest.get("required_layout") != _layout():
        raise ValueError("required layout differs")
    required = manifest.get("required_evidence_files")
    if not isinstance(required, list) or not required:
        raise ValueError("required evidence list missing")
    normalized = [_path(value, "required_evidence_file").as_posix().casefold() for value in required]
    if len(normalized) != len(set(normalized)):
        raise ValueError("case-fold collision in required evidence files")
    for value in required:
        _under(RUN_ROOT + "/" + value, RUN_ROOT, "required_evidence_file")
    if manifest.get("setting_id") != SETTING_ID or manifest.get("corpus_id") != CORPUS_ID:
        raise ValueError("setting/corpus binding differs")
    if type(manifest.get("N")) is not int or manifest["N"] != N:
        raise ValueError("N binding differs")
    if manifest.get("runtime_files") != RUNTIME_FILES:
        raise ValueError("runtime file manifest differs")
    if manifest.get("runtime_archive_sha256") != RUNTIME_ARCHIVE_SHA256:
        raise ValueError("runtime archive binding differs")
    if manifest.get("timeout_seconds") != TIMEOUT_SECONDS:
        raise ValueError("timeout binding differs")
    if manifest.get("minimum_calls_per_pass") != MIN_CALLS or manifest.get("maximum_calls_per_pass") != MAX_CALLS:
        raise ValueError("call-bound binding differs")
    if manifest.get("network_forbidden") is not True or manifest.get("external_provider_calls_allowed") != 0:
        raise ValueError("provider/network prohibition differs")
    if manifest.get("provider_execution_enabled") is not False:
        raise ValueError("provider execution must be disabled")
    if manifest.get("detector_v1_forbidden") is not True or manifest.get("renderer_forbidden") is not True:
        raise ValueError("analysis/renderer prohibition differs")
    if manifest.get("protected_manifest_path") != PROTECTED_MANIFEST_PATH:
        raise ValueError("protected manifest path differs")
    protected_manifest = ROOT / PROTECTED_MANIFEST_PATH
    if not protected_manifest.is_file() or manifest.get("protected_manifest_sha256") != digest(protected_manifest):
        raise ValueError("protected manifest hash differs")
    for field, paths in (("harness_code_hashes", HARNESS_CODE_PATHS), ("schema_hashes", SCHEMA_PATHS)):
        observed = manifest.get(field)
        if not isinstance(observed, dict) or set(observed) != set(paths):
            raise ValueError(f"{field} binding differs")
        for path in paths:
            target = ROOT / path
            if not target.is_file() or observed[path] != digest(target):
                raise ValueError(f"{field} hash differs: {path}")
    for field in ("control_root", "output_root", "verification_root"):
        _under(manifest[field], RUN_ROOT, field)
    if manifest.get("maximum_invocations") != MAX_INVOCATIONS:
        raise ValueError("maximum invocation binding differs")


def validate_request_against_manifest(
    request: dict[str, Any], manifest: dict[str, Any]
) -> None:
    validate_manifest(manifest)
    if request.get("status") != "AUTHORIZATION_REQUESTED_NOT_GRANTED":
        raise ValueError("request is already authorizing or executed")
    if request.get("packet_manifest_path") != MANIFEST_PATH:
        raise ValueError("packet manifest path differs")
    for field in ("run_root", "control_root", "output_root", "verification_root"):
        expected = manifest[field]
        if request.get(field) != expected:
            raise ValueError(f"{field} differs from machine manifest")
        _under(request[field], manifest["run_root"], field)
    expected_paths = {
        "receipt_path": manifest["output_root"] + "/preflight-receipt.json",
        "attempt_start_path": manifest["control_root"] + "/attempt-start.json",
        "attempt_end_path": manifest["control_root"] + "/attempt-end.json",
    }
    for field, expected in expected_paths.items():
        if request.get(field) != expected:
            raise ValueError(f"{field} differs from machine manifest")
        _under(request[field], manifest["run_root"], field)
    for field in (
        "setting_id",
        "corpus_id",
        "N",
        "timeout_seconds",
        "minimum_calls_per_pass",
        "maximum_calls_per_pass",
        "maximum_invocations",
        "runtime_archive_sha256",
        "runtime_file_hashes",
        "network_forbidden",
        "external_provider_calls_allowed",
        "provider_execution_enabled",
        "detector_v1_forbidden",
        "renderer_forbidden",
    ):
        expected = (
            {key: value["sha256"] for key, value in manifest["runtime_files"].items()}
            if field == "runtime_file_hashes"
            else manifest[field]
        )
        if request.get(field) != expected:
            raise ValueError(f"{field} differs from machine manifest")
    if request.get("command_template") != manifest["command_template"]:
        raise ValueError("command template differs from machine manifest")
    if request.get("required_evidence_files") != manifest["required_evidence_files"]:
        raise ValueError("required evidence differs from machine manifest")
    if request.get("allowed_write_roots") != manifest["allowed_write_roots"]:
        raise ValueError("allowed write roots differ from machine manifest")
    if request.get("prohibited_write_roots") != manifest["prohibited_write_roots"]:
        raise ValueError("prohibited write roots differ from machine manifest")
    for field in ("protected_manifest_path", "protected_manifest_sha256", "harness_code_hashes", "schema_hashes"):
        if field in request and request[field] != manifest[field]:
            raise ValueError(f"{field} differs from machine manifest")


def validate_grant_bindings(
    grant: dict[str, Any], manifest: dict[str, Any], request: dict[str, Any]
) -> None:
    validate_request_against_manifest(request, manifest)
    if grant.get("grant_type") != "OFFLINE_FAKE_PREFLIGHT_ONLY":
        raise ValueError("grant type differs")
    for field in (
        "run_root",
        "control_root",
        "output_root",
        "verification_root",
        "setting_id",
        "corpus_id",
        "N",
        "timeout_seconds",
        "minimum_calls_per_pass",
        "maximum_calls_per_pass",
        "maximum_invocations",
        "allowed_write_roots",
        "prohibited_write_roots",
        "required_evidence_files",
        "runtime_archive_sha256",
        "runtime_file_hashes",
        "command_template",
        "protected_manifest_path",
        "protected_manifest_sha256",
        "harness_code_hashes",
        "schema_hashes",
    ):
        expected = request.get(field, manifest.get(field))
        if grant.get(field) != expected:
            raise ValueError(f"{field} differs from request/manifest")
    for field in ("command_sha256", "packet_manifest_sha256"):
        if field in request and grant.get(field) != request[field]:
            raise ValueError(f"{field} differs from request")
    if grant.get("network_forbidden") is not True:
        raise ValueError("network must be forbidden")
    if grant.get("external_provider_calls_allowed") != 0:
        raise ValueError("external providers must be forbidden")
    if grant.get("paid_execution_authorized") is not False:
        raise ValueError("paid execution must be false")
    if grant.get("provider_execution_enabled") is not False:
        raise ValueError("provider execution must be disabled")
    if grant.get("detector_v1_forbidden") is not True or grant.get("renderer_forbidden") is not True:
        raise ValueError("analysis/renderer permissions must be forbidden")


def validate_command_record(record: dict[str, Any], manifest: dict[str, Any]) -> None:
    """Validate a resolved command fingerprint before any protected import."""
    validate_manifest(manifest)
    tokens = record.get("tokens")
    if not isinstance(tokens, list) or not tokens or not all(isinstance(token, str) for token in tokens):
        raise ValueError("command tokens are missing")
    if record.get("command_sha256") != hashlib.sha256(canonical(tokens)).hexdigest():
        raise ValueError("command fingerprint mismatch")
    if record.get("max_invocations") != MAX_INVOCATIONS:
        raise ValueError("maximum invocation binding differs")
    expected_flags = {"--packet", "--grant", "--runtime-root", "--runtime-archive", "--output-dir", "--receipt"}
    if not expected_flags.issubset(set(tokens)):
        raise ValueError("command is missing a required binding")
    values = {tokens[index]: tokens[index + 1] for index, token in enumerate(tokens[:-1]) if token in expected_flags}
    packet = Path(values["--packet"]).resolve()
    grant = Path(values["--grant"]).resolve()
    runtime_root = Path(values["--runtime-root"]).resolve()
    runtime_archive = Path(values["--runtime-archive"]).resolve()
    output = Path(values["--output-dir"]).resolve()
    receipt = Path(values["--receipt"]).resolve()
    if packet != (ROOT / PACKET_PATH).resolve():
        raise ValueError("command packet path differs")
    if grant.parent != (ROOT / RUN_ROOT / "control").resolve() or grant.name != "authorization-grant.json":
        raise ValueError("command grant path differs")
    if runtime_root != (ROOT / "external_data/airtravel-pr38/runtime_input").resolve():
        raise ValueError("command runtime root differs")
    if runtime_archive != (ROOT / "external_data/airtravel-pr38/cd_airtravel-runtime-v1.0.2.zip").resolve():
        raise ValueError("command runtime archive differs")
    if output != (ROOT / RUN_ROOT / "output").resolve() or receipt != output / "preflight-receipt.json":
        raise ValueError("command output binding differs")


def validate_private_layout(root: Path, *, preparation: bool = True) -> None:
    """Reject siblings, links, and undeclared files under the fixed v4 root."""
    if root.exists():
        root_stat = root.lstat()
        if root.is_symlink() or getattr(root_stat, "st_file_attributes", 0) & 0x400:
            raise ValueError("private root is a symlink/reparse point")
    expected_root = (ROOT / RUN_ROOT).resolve()
    if root.resolve() != expected_root:
        raise ValueError("private root is not the fixed v4 root")
    if not root.exists():
        return
    for path in root.rglob("*"):
        stat = path.lstat()
        if path.is_symlink() or getattr(stat, "st_file_attributes", 0) & 0x400:
            raise ValueError("symlink/reparse point in private root")
        relative = path.relative_to(root).as_posix()
        if preparation and path.is_dir():
            if relative not in {"control"}:
                raise ValueError("undeclared pre-authorization directory in private root")
            continue
        if preparation and relative not in {
            "control/private-execution-request.json",
            "control/execution-command.json",
            "control/preparation-receipt.json",
        }:
            raise ValueError("undeclared pre-authorization file in private root")


def _exclusive_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(canonical(value).decode("utf-8"))
    except FileExistsError as exc:
        raise ValueError(f"{path.name} already exists") from exc


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def create_attempt_start(
    control_dir: Path,
    bindings: dict[str, Any],
    *,
    invocation_id: str,
    nonce: str | None = None,
) -> dict[str, Any]:
    """Create the one-time consumption marker using exclusive creation."""
    if not invocation_id or not isinstance(invocation_id, str):
        raise ValueError("invocation_id required")
    start = {
        "schema_version": "airtravel-v4-attempt-start-v1",
        "attempt_number": 1,
        "invocation_id": invocation_id,
        "nonce": nonce or secrets.token_urlsafe(24),
        "grant_sha256": bindings.get("grant_sha256"),
        "authorization_message_sha256": bindings.get("authorization_message_sha256"),
        "command_sha256": bindings.get("command_sha256"),
        "reviewed_head": bindings.get("reviewed_head"),
        "started_at": _utc_now(),
        "monotonic_start": time.monotonic(),
        "process_id": os.getpid(),
    }
    if not all(start.get(key) for key in ("grant_sha256", "command_sha256", "reviewed_head")):
        raise ValueError("attempt binding incomplete")
    _exclusive_json(control_dir / "attempt-start.json", start)
    return start


def assert_not_consumed(control_dir: Path, output_dir: Path) -> None:
    if (control_dir / "attempt-start.json").exists():
        raise ValueError("attempt-start already exists; invocation consumed")
    if (control_dir / "attempt-end.json").exists():
        raise ValueError("attempt-end already exists; invocation consumed")
    if (output_dir / "preflight-receipt.json").exists():
        raise ValueError("receipt already exists; invocation consumed")


def create_attempt_end(
    control_dir: Path,
    start: dict[str, Any],
    *,
    status: str,
    output_receipt_sha256: str | None = None,
) -> dict[str, Any]:
    if not (control_dir / "attempt-start.json").is_file():
        raise ValueError("attempt-start is required")
    if (control_dir / "attempt-end.json").exists():
        raise ValueError("attempt-end already exists")
    if start.get("attempt_number") != 1 or not start.get("invocation_id"):
        raise ValueError("invalid attempt-start binding")
    end = {
        "schema_version": "airtravel-v4-attempt-end-v1",
        "attempt_number": 1,
        "invocation_id": start["invocation_id"],
        "completed_at": _utc_now(),
        "status": status,
        "exit_classification": "SUCCESS" if status == "TECHNICAL_SUCCESS" else "FAILURE",
        "grant_consumption_status": "CONSUMED",
        "retry_count": 0,
        "replay_count": 0,
        "output_receipt_sha256": output_receipt_sha256,
    }
    _exclusive_json(control_dir / "attempt-end.json", end)
    return end


CALL_FIELDS = {
    "sequence",
    "phase",
    "case_id",
    "label",
    "source_agent",
    "target_agent",
    "prompt_sha256",
    "prompt_length",
    "answer_sha256",
    "answer_length",
    "decision_sha256",
    "fake_client_identity",
}
RAW_CALL_FIELDS = {"prompt", "answer", "credential", "api_key"}


def _validate_call(row: dict[str, Any], expected_sequence: int) -> None:
    if RAW_CALL_FIELDS & row.keys():
        raise ValueError("raw prompt/answer or credential field in call record")
    if set(row) != CALL_FIELDS:
        raise ValueError("call record fields differ")
    if row["sequence"] != expected_sequence:
        raise ValueError("call record sequence is not append-only")
    for field in ("prompt_sha256", "answer_sha256", "decision_sha256"):
        if not isinstance(row[field], str) or not re.fullmatch(r"[0-9a-f]{64}", row[field]):
            raise ValueError(f"invalid {field}")
    for field in ("prompt_length", "answer_length"):
        if type(row[field]) is not int or row[field] < 0:
            raise ValueError(f"invalid {field}")


def append_call_record(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_call_records(path) if path.exists() else []
    _validate_call(row, len(existing) + 1)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def load_call_records(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError("call-record file missing")
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            raise ValueError("blank call-record line")
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError("call record must be an object")
        _validate_call(row, len(rows) + 1)
        rows.append(row)
    return rows


def compare_call_records(left: Path, right: Path) -> dict[str, Any]:
    a, b = load_call_records(left), load_call_records(right)
    if len(a) != len(b):
        raise ValueError("parity mismatch: call counts differ")
    comparisons = {
        "direct_count": len(a),
        "instrumented_count": len(b),
        "call_count_equal": len(a) == len(b),
        "ordered_label_parity": [row["label"] for row in a] == [row["label"] for row in b],
        "ordered_prompt_parity": [row["prompt_sha256"] for row in a]
        == [row["prompt_sha256"] for row in b],
        "ordered_answer_parity": [row["answer_sha256"] for row in a]
        == [row["answer_sha256"] for row in b],
        "decision_parity": [row["decision_sha256"] for row in a]
        == [row["decision_sha256"] for row in b],
        "phase_case_coverage_equal": [
            (row["phase"], row["case_id"]) for row in a
        ]
        == [(row["phase"], row["case_id"]) for row in b],
    }
    if not all(
        comparisons[key]
        for key in comparisons
        if key.endswith("parity") or key.endswith("equal")
    ):
        raise ValueError("parity mismatch in persisted call records")
    return comparisons


def zero_safety_counters() -> dict[str, int]:
    return {name: 0 for name in SAFETY_COUNTERS}


def validate_safety_counters(counters: dict[str, Any]) -> None:
    if set(counters) != set(SAFETY_COUNTERS) or any(
        type(counters[name]) is not int or counters[name] != 0 for name in SAFETY_COUNTERS
    ):
        raise ValueError("safety counters must be present and zero")


def receipt_v2_required_fields() -> tuple[str, ...]:
    return (
        "schema_version",
        "mode",
        "status",
        "reviewed_head",
        "packet_manifest_sha256",
        "request_sha256",
        "authorization_message_sha256",
        "grant_sha256",
        "command_sha256",
        "invocation_id",
        "nonce",
        "attempt_number",
        "started_at",
        "completed_at",
        "grant_valid_at_start",
        "timeout",
        "retry_count",
        "replay_count",
        "direct_fake_call_count",
        "instrumented_fake_call_count",
        "combined_fake_call_count",
        "call_count_equal",
        "prompt_parity",
        "answer_parity",
        "decision_parity",
        "pipeline_state_parity",
        "scientific_artifact_parity",
        "completed_cases",
        "completed_phases",
        "event_log_sha256",
        "event_count",
        "question_count",
        "answer_count",
        "termination_count",
        "termination_counts",
        "route_pairs",
        "protected_manifest_hash_before",
        "protected_manifest_hash_after",
        "tracked_manifest_hash_before",
        "tracked_manifest_hash_after",
        "output_inventory_sha256",
        "containment_status",
        "privacy_status",
        "call_record_hashes",
        "safety_counters",
        "grant_consumption_status",
    )


def prepare_only(
    *, manifest: dict[str, Any] | None = None, request: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Validate the v4 packet/request shape without a grant or execution."""
    manifest = manifest or frozen_manifest()
    request = request or request_template()
    validate_request_against_manifest(request, manifest)
    return {
        "status": "AUTHORIZATION_REQUESTED_NOT_GRANTED",
        "mode": "prepare_only",
        "packet_version": PACKET_VERSION,
        "run_root": RUN_ROOT,
        "setting_id": SETTING_ID,
        "corpus_id": CORPUS_ID,
        "N": N,
        "execute_invoked": False,
        "provider_calls": 0,
        "detector_runs": 0,
    }
