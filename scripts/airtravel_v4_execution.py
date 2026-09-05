"""Fail-closed execution boundary for a future AirTravel v4 run.

The module contains validation and durable ledger operations only. It does
not import the protected orchestrator, construct a provider, or start a run.
The eventual executor must call consume_grant before protected imports and
must persist all receipt fields defined by receipt schema v2.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from airtravel_v4_contract import (
    GRANT_SCHEMA_PATH,
    MANIFEST_PATH,
    PACKET_PATH,
    RECEIPT_SCHEMA_PATH,
    ROOT,
    RUN_ROOT,
    assert_not_consumed,
    create_attempt_end,
    create_attempt_start,
    digest,
    frozen_manifest,
    parse_utc_timestamp,
    request_template,
    validate_command_record,
    validate_grant_bindings,
    validate_private_layout,
    validate_request_against_manifest,
    validate_safety_counters,
)


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"required v4 file missing: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_grant_file(
    grant_path: Path,
    *,
    root: Path = ROOT,
    manifest: dict[str, Any] | None = None,
    request: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Validate a future owner grant against the machine manifest and request."""
    if manifest is None:
        manifest = frozen_manifest()
    if request is None:
        request = request_template()
    grant = _read(grant_path)
    from jsonschema import Draft202012Validator, FormatChecker

    schema = _read(root / GRANT_SCHEMA_PATH)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(grant)
    validate_grant_bindings(grant, manifest, request)
    if grant.get("packet_manifest_sha256") != digest(root / MANIFEST_PATH):
        raise ValueError("grant packet-manifest hash mismatch")
    if grant.get("packet_sha256") != digest(root / PACKET_PATH):
        raise ValueError("grant packet hash mismatch")
    if grant.get("status") != "GRANTED":
        raise ValueError("fresh owner grant is required")
    reviewed_head = grant.get("reviewed_head")
    if not isinstance(reviewed_head, str) or len(reviewed_head) != 40:
        raise ValueError("reviewed head is not bound")
    evaluated_at = now or datetime.now(timezone.utc)
    grant_valid_at = validate_grant_freshness(grant, now=evaluated_at)
    return {
        "grant_sha256": digest(grant_path),
        "packet_manifest_sha256": grant["packet_manifest_sha256"],
        "authorization_message_sha256": grant["authorization_message_sha256"],
        "command_sha256": grant["command_sha256"],
        "reviewed_head": reviewed_head,
        "run_root": grant["run_root"],
        "output_root": grant["output_root"],
        "N": grant["N"],
        "nonce": grant["nonce"],
        "invocation_id": grant["invocation_id"],
        "grant_valid_at_start": grant_valid_at,
        "grant_evaluated_at": evaluated_at.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
    }


def validate_grant_freshness(
    grant: dict[str, Any], *, now: datetime | None = None
) -> bool:
    """Enforce an aware, bounded grant window at the point of consumption."""
    evaluated_at = now or datetime.now(timezone.utc)
    if not isinstance(evaluated_at, datetime):
        raise ValueError("grant evaluation time must be a datetime")
    if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
        raise ValueError("grant evaluation time must be timezone-aware")
    granted_at = parse_utc_timestamp(grant.get("granted_at"), "granted_at")
    expires_at = parse_utc_timestamp(grant.get("expires_at"), "expires_at")
    if expires_at <= granted_at:
        raise ValueError("grant expiry must be after grant time")
    if expires_at - granted_at > timedelta(hours=24):
        raise ValueError("grant validity window exceeds 24 hours")
    if not granted_at <= evaluated_at < expires_at:
        raise ValueError("grant is expired or not yet valid")
    return True


def load_private_request(*, root: Path = ROOT) -> dict[str, Any]:
    """Load and validate the request persisted by the prepare-only command."""
    manifest = frozen_manifest()
    request = _read(root / RUN_ROOT / "control/private-execution-request.json")
    validate_request_against_manifest(request, manifest)
    return request


def load_command_record(*, root: Path = ROOT) -> dict[str, Any]:
    """Load the resolved command fingerprint and validate every path binding."""
    manifest = frozen_manifest()
    record = _read(root / RUN_ROOT / "control/execution-command.json")
    validate_command_record(record, manifest)
    return record


def validate_authorization_message(grant_path: Path, grant: dict[str, Any]) -> str:
    """Require the owner message beside a future grant and verify its digest."""
    message_path = grant_path.with_name("authorization-grant.message.txt")
    if not message_path.is_file():
        raise ValueError("authorization message is missing")
    observed = digest(message_path)
    if observed != grant.get("authorization_message_sha256"):
        raise ValueError("authorization message hash mismatch")
    return observed


def consume_grant(
    grant_path: Path,
    *,
    root: Path = ROOT,
    invocation_id: str,
    nonce: str,
) -> dict[str, Any]:
    """Atomically consume a grant exactly once before protected imports."""
    validate_private_layout(root / RUN_ROOT, preparation=False)
    request = load_private_request(root=root)
    command = load_command_record(root=root)
    bindings = validate_grant_file(grant_path, root=root, request=request)
    if command["command_sha256"] != bindings["command_sha256"]:
        raise ValueError("command fingerprint differs from grant")
    grant = _read(grant_path)
    validate_authorization_message(grant_path, grant)
    control = root / RUN_ROOT / "control"
    output = root / RUN_ROOT / "output"
    assert_not_consumed(control, output)
    if invocation_id != grant["invocation_id"] or nonce != grant["nonce"]:
        raise ValueError("caller identity differs from grant")
    return create_attempt_start(
        control,
        bindings,
        invocation_id=grant["invocation_id"],
        nonce=grant["nonce"],
    )


def finish_grant(
    *,
    root: Path = ROOT,
    attempt_start: dict[str, Any],
    status: str,
    output_receipt_sha256: str | None = None,
) -> dict[str, Any]:
    """Persist the terminal attempt marker without removing the start marker."""
    return create_attempt_end(
        root / RUN_ROOT / "control",
        attempt_start,
        status=status,
        output_receipt_sha256=output_receipt_sha256,
    )


def validate_receipt_v2(receipt: dict[str, Any], *, root: Path = ROOT) -> None:
    from jsonschema import Draft202012Validator, FormatChecker

    schema = _read(root / RECEIPT_SCHEMA_PATH)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(receipt)
    required = {
        "mode",
        "invocation_id",
        "attempt_number",
        "started_at",
        "completed_at",
        "grant_consumption_status",
        "call_record_hashes",
        "safety_counters",
    }
    missing = sorted(required - receipt.keys())
    if missing:
        raise ValueError(f"receipt v2 fields missing: {missing}")
    validate_safety_counters(receipt["safety_counters"])
    parse_utc_timestamp(receipt["started_at"], "started_at")
    parse_utc_timestamp(receipt["completed_at"], "completed_at")
    parse_utc_timestamp(receipt["grant_evaluated_at"], "grant_evaluated_at")
    if type(receipt["grant_valid_at_start"]) is not bool:
        raise ValueError("grant validity result must be boolean")
    if receipt["status"] == "TECHNICAL_SUCCESS" and not receipt["grant_valid_at_start"]:
        raise ValueError("successful receipt requires a valid grant at start")
    if receipt["combined_fake_call_count"] != (
        receipt["direct_fake_call_count"] + receipt["instrumented_fake_call_count"]
    ):
        raise ValueError("combined call count is inconsistent")
    if receipt["call_count_equal"] != (
        receipt["direct_fake_call_count"] == receipt["instrumented_fake_call_count"]
    ):
        raise ValueError("call-count equality is inconsistent")
    if set(receipt["call_record_hashes"]) != {"baseline", "instrumented"}:
        raise ValueError("call-record hashes must name baseline and instrumented records")
    evidence = frozen_manifest()["required_evidence_files"]
    for relative in evidence:
        target = root / RUN_ROOT / relative
        if not target.is_file():
            raise ValueError(f"required evidence file missing: {relative}")
    expected_records = {
        "baseline": root / RUN_ROOT / "output/baseline/call-records.jsonl",
        "instrumented": root / RUN_ROOT / "output/instrumented/call-records.jsonl",
    }
    for name, target in expected_records.items():
        if receipt["call_record_hashes"][name] != digest(target):
            raise ValueError(f"call-record hash mismatch: {name}")
    event_log = root / RUN_ROOT / "output/instrumented/qa_events.jsonl"
    if receipt["event_log_sha256"] != digest(event_log):
        raise ValueError("event-log hash mismatch")
    output_inventory = root / RUN_ROOT / "verification/final-output-inventory.json"
    if receipt["output_inventory_sha256"] != digest(output_inventory):
        raise ValueError("output inventory hash mismatch")
    start = parse_utc_timestamp(receipt["started_at"], "started_at")
    end = parse_utc_timestamp(receipt["completed_at"], "completed_at")
    if end < start:
        raise ValueError("receipt completion precedes start")
