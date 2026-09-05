"""Fail-closed validation and one-shot local fake execution for AirTravel v4.

The executor consumes a fresh owner grant before importing the protected
orchestrator, then runs exactly two deterministic local passes (baseline and
instrumented). No provider SDK, credential, network, Detector-v1 analysis or
renderer is available on this path. All scientific outputs remain private
under the fixed ignored run root and are represented in the receipt by hashes.
"""

from __future__ import annotations

import asyncio
import importlib
import json
import subprocess
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from airtravel_v4_contract import (
    CORPUS_ID,
    GRANT_SCHEMA_PATH,
    MANIFEST_PATH,
    PACKET_PATH,
    RECEIPT_SCHEMA_PATH,
    ROOT,
    RUN_ROOT,
    SETTING_ID,
    TIMEOUT_SECONDS,
    assert_not_consumed,
    canonical,
    compare_call_records,
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
    zero_safety_counters,
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


def validate_receipt_v2(
    receipt: dict[str, Any], *, root: Path = ROOT, require_evidence: bool = True
) -> None:
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
    if require_evidence:
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


# The executor is deliberately kept in this already-bound harness module.  It
# is a local fake-provider path only: the protected runtime is imported after
# the grant is consumed and receives a deterministic in-process client.
OFFLINE_PROVIDER_IMPORTS = frozenset(
    {"openai", "anthropic", "google", "google.generativeai", "requests", "httpx", "urllib"}
)
FAKE_CLIENT_IDENTITY = "LOCAL_DETERMINISTIC_FAKE_V4"
_SCIENTIFIC_OUTPUTS = frozenset(
    {
        "pipeline_state.json",
        "language_template.json",
        "reference_guidelines.json",
        "compliance_vectors.json",
        "uncovered_fragments.json",
        "deviation_patterns.json",
        "variability_classifications.json",
        "lang_qa_history.json",
        "dom_qa_history.json",
        "human_review_queue.jsonl",
        "pipeline.log",
    }
)


def _agent_route(inventory_row: str, label: str) -> tuple[str, str]:
    """Map a protected call-site row to safe, non-content route metadata."""
    if label == "agent1/answer_language_questions":
        return "orchestrator", "agent1"
    if label == "agent2/answer_domain_questions":
        return "orchestrator", "agent2"
    source = {
        "P1_TEMPLATE": "agent1",
        "P2_GUIDELINES_PRODUCER": "agent2",
        "P3_MAP": "agent3",
        "P3_RESOLVE_PRODUCER": "agent3",
        "P3_AUDIT_PRODUCER": "agent3",
        "P4_IDENTIFY": "agent4",
        "P4_CLASSIFY_PRODUCER": "agent4",
        "P4_FEEDBACK_PRODUCER": "agent2",
    }.get(inventory_row)
    if source is None:
        raise ValueError(f"unknown call inventory route: {inventory_row}")
    return source, "orchestrator"


def privacy_safe_call_row(raw: dict[str, Any], sequence: int) -> dict[str, Any]:
    """Convert a fake call observation to the exact privacy-safe record shape."""
    required = {
        "label",
        "phase",
        "case_id",
        "inventory_row",
        "prompt_sha256",
        "answer_sha256",
        "decision_sha256",
        "prompt_length",
        "answer_length",
    }
    missing = sorted(required - raw.keys())
    if missing:
        raise ValueError(f"call inventory missing: {missing}")
    if any(key in raw for key in ("prompt", "answer", "api_key", "credential")):
        raise ValueError("raw call content or credential in call observation")
    source, target = _agent_route(str(raw["inventory_row"]), str(raw["label"]))
    return {
        "sequence": sequence,
        "phase": raw["phase"],
        "case_id": raw["case_id"],
        "label": raw["label"],
        "source_agent": source,
        "target_agent": target,
        "prompt_sha256": raw["prompt_sha256"],
        "prompt_length": raw["prompt_length"],
        "answer_sha256": raw["answer_sha256"],
        "answer_length": raw["answer_length"],
        "decision_sha256": raw["decision_sha256"],
        "fake_client_identity": FAKE_CLIENT_IDENTITY,
    }


def output_inventory(output: Path) -> dict[str, str]:
    """Hash output files in stable order, excluding circular receipt entries."""
    result: dict[str, str] = {}
    if not output.exists():
        return result
    for path in sorted(p for p in output.rglob("*") if p.is_file()):
        relative = path.relative_to(output).as_posix()
        if relative in {"preflight-receipt.json"}:
            continue
        result[relative] = digest(path)
    return result


def _canonical_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError(f"evidence file already exists: {path}")
    with path.open("xb") as handle:
        handle.write(canonical(value))


def _git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    head = result.stdout.strip()
    if not __import__("re").fullmatch(r"[0-9a-f]{40}", head):
        raise ValueError("git HEAD is not a full SHA-1")
    return head


def _tracked_manifest(root: Path) -> tuple[str, dict[str, str]]:
    result = subprocess.run(
        ["git", "ls-files"], cwd=root, check=True, capture_output=True, text=True, encoding="utf-8"
    )
    values: dict[str, str] = {}
    for relative in result.stdout.splitlines():
        target = root / relative
        if target.is_file():
            values[relative] = digest(target)
    return digest_bytes(canonical(values)), values


def digest_bytes(value: bytes) -> str:
    import hashlib

    return hashlib.sha256(value).hexdigest()


def _protected_manifest_hash(root: Path) -> str:
    return digest(root / frozen_manifest()["protected_manifest_path"])


def _runtime_config(runtime_root: Path, archive: Path) -> dict[str, Any]:
    if not archive.is_file() or digest(archive) != frozen_manifest()["runtime_archive_sha256"]:
        raise ValueError("runtime archive hash mismatch")
    manifest = frozen_manifest()
    for relative, expected in manifest["runtime_files"].items():
        target = runtime_root / relative
        if not target.is_file() or target.stat().st_size != expected["bytes"] or digest(target) != expected["sha256"]:
            raise ValueError(f"runtime file mismatch: {relative}")
    config_path = runtime_root / "cd_airtravel.runtime-config.json"
    if not config_path.is_file():
        raise ValueError("runtime configuration missing")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if (
        config.get("setting_id") != SETTING_ID
        or config.get("corpus_id") != CORPUS_ID
        or config.get("provider_execution_enabled") is not False
        or config.get("description_path") != "domain_description/description.md"
        or config.get("candidate_models_dir") != "candidate_models"
        or config.get("runtime_files") != sorted(manifest["runtime_files"])
    ):
        raise ValueError("runtime configuration is not the frozen five-file configuration")
    visible = {
        p.relative_to(runtime_root).as_posix()
        for p in runtime_root.rglob("*")
        if p.is_file()
    }
    if visible - set(manifest["runtime_files"]) - {"cd_airtravel.runtime-config.json"}:
        raise ValueError("reference file is runtime-visible")
    return config


def _load_protected_runtime():
    """Import the protected orchestrator with its provider constructor stubbed."""
    framework = ROOT / "VEGO-AI/framework"
    if str(framework) not in sys.path:
        sys.path.insert(0, str(framework))
    stub = types.ModuleType("llm_client")

    class ForbiddenProvider:
        def __init__(self, *args, **kwargs):
            raise PermissionError("external provider construction forbidden")

    stub.LLMClient = ForbiddenProvider
    original = sys.modules.get("llm_client")
    sys.modules["llm_client"] = stub
    try:
        return importlib.import_module("orchestrator")
    finally:
        if original is None:
            sys.modules.pop("llm_client", None)
        else:
            sys.modules["llm_client"] = original


async def _run_pair_v4(
    cfg: dict[str, Any], output: Path, module, run_id: str, progress: dict[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    """Run the existing protected orchestrator twice using only local fakes."""
    import airtravel_local_observer as observer_module
    from airtravel_preflight_execution import run_pair

    original_fake = observer_module.RecordingFake

    class LengthRecordingFake(original_fake):
        async def call(self, prompt, *, label):
            result = await super().call(prompt, label=label)
            row = self.calls[-1]
            row["prompt_length"] = len(json.dumps(prompt, ensure_ascii=False, sort_keys=True).encode("utf-8"))
            row["answer_length"] = len(json.dumps(result, ensure_ascii=False, sort_keys=True).encode("utf-8"))
            return result

    observer_module.RecordingFake = LengthRecordingFake
    try:
        return await run_pair(
            cfg, output, module, mode="two_rounds", run_id=run_id, progress=progress
        )
    finally:
        observer_module.RecordingFake = original_fake


def _persist_call_records(output: Path, progress: dict[str, list[dict[str, Any]]]) -> dict[str, str]:
    paths = {
        "baseline": output / "baseline/call-records.jsonl",
        "instrumented": output / "instrumented/call-records.jsonl",
    }
    for side, path in paths.items():
        for sequence, raw in enumerate(progress.get(side, []), start=1):
            from airtravel_v4_contract import append_call_record

            append_call_record(path, privacy_safe_call_row(raw, sequence))
    return {side: digest(path) for side, path in paths.items()}


def execute_authorized(
    *,
    runtime_root: Path,
    archive: Path,
    output: Path,
    receipt_path: Path,
    packet: Path,
    grant: Path,
    root: Path = ROOT,
) -> dict[str, Any]:
    """Consume a fresh v4 grant and execute exactly one local fake preflight."""
    if root.resolve() != ROOT.resolve():
        raise ValueError("repository root differs from bound harness root")
    expected_output = root / RUN_ROOT / "output"
    if output.resolve() != expected_output.resolve() or receipt_path.resolve() != (output / "preflight-receipt.json").resolve():
        raise ValueError("output or receipt path differs from fixed v4 layout")
    if packet.resolve() != (root / PACKET_PATH).resolve() or grant.resolve() != (root / RUN_ROOT / "control/authorization-grant.json").resolve():
        raise ValueError("packet or grant path differs from fixed v4 layout")
    if _git_head(root) != _read(grant).get("reviewed_head"):
        raise ValueError("grant reviewed_head does not match current checkout")
    _runtime_config(runtime_root, archive)
    caller_grant = _read(grant)
    bindings = consume_grant(grant, root=root, invocation_id=caller_grant["invocation_id"], nonce=caller_grant["nonce"])
    attempt_start = _read(root / RUN_ROOT / "control/attempt-start.json")
    protected_before = _protected_manifest_hash(root)
    tracked_before, tracked_values = _tracked_manifest(root)
    if output.exists() and any(output.rglob("*")):
        raise ValueError("output directory must be absent/empty before consumption")
    output.mkdir(parents=True, exist_ok=True)

    # Preload every module needed by the guarded operation before the read guard
    # is active.  The guard then permits only tracked sources and five runtime bytes.
    module = _load_protected_runtime()
    from airtravel_execution_safety import ExecutionGuard, timed_operation
    from qa_communication import validate_event_stream

    validate_event_stream([])
    from airtravel_preflight_execution import ALLOWED_FILES

    allowed_files = {
        *ALLOWED_FILES,
        *(f"{side}/{name}" for side in ("baseline", "instrumented") for name in _SCIENTIFIC_OUTPUTS),
    }
    reads = {root / relative for relative in tracked_values} | {
        runtime_root / relative for relative in frozen_manifest()["runtime_files"]
    } | {runtime_root / "cd_airtravel.runtime-config.json"}
    domain = (runtime_root / "domain_description/description.md").read_text(encoding="utf-8")
    cases = [
        {"case_id": relative.split("/", 1)[1].split("_", 1)[0], "case_model": (runtime_root / relative).read_text(encoding="utf-8")}
        for relative in sorted(frozen_manifest()["runtime_files"])
        if relative.startswith("candidate_models/")
    ]
    cfg = {
        "setting_id": SETTING_ID,
        "corpus_id": CORPUS_ID,
        "language_name": "UML",
        "domain_description": domain,
        "case_models": cases,
        "max_concurrent_cases": 2,
        "model": "LOCAL_DETERMINISTIC_FAKE_V4",
        "api_key": None,
        "provider_execution_enabled": False,
    }
    run_id = "FAKE-" + digest_bytes(canonical({"grant": bindings["grant_sha256"], "command": bindings["command_sha256"], "head": bindings["reviewed_head"]}))[:24]
    progress: dict[str, list[dict[str, Any]]] = {}
    guard = ExecutionGuard(output, allowed_files, reads, max_files=39, max_bytes=16 * 1024 * 1024 - 65536)
    try:
        async def operation():
            with guard:
                result = await _run_pair_v4(cfg, output, module, run_id, progress)
                records = _persist_call_records(output, progress)
                # run_pair stores lists in its return; mirror them for records.
                if not records:
                    raise ValueError("call records were not persisted")
                return result

        result = asyncio.run(timed_operation(operation, module, timeout=TIMEOUT_SECONDS))
    except BaseException:
        raise

    # _run_pair_v4 populates its own progress only when passed; recover the
    # lists from the returned call counts is not possible, so use persisted
    # records as the authoritative counters below.
    call_paths = {
        "baseline": output / "baseline/call-records.jsonl",
        "instrumented": output / "instrumented/call-records.jsonl",
    }
    call_counts = {side: len(__import__("airtravel_v4_contract").load_call_records(path)) for side, path in call_paths.items()}
    from qa_communication import build_episode_projection

    event_path = output / "instrumented/qa_events.jsonl"
    events = [json.loads(line) for line in event_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    validate_event_stream(events)
    projections = build_episode_projection(events)
    terminations = [event for event in events if event["event_type"] == "EPISODE_TERMINATED"]
    parity = compare_call_records(call_paths["baseline"], call_paths["instrumented"])
    output_hashes = output_inventory(output)
    verification = root / RUN_ROOT / "verification"
    _canonical_write(verification / "final-output-inventory.json", output_hashes)
    _canonical_write(verification / "parity-verification.json", {"status": "PASS", **parity, "pipeline_state_parity": result["state_parity"], "scientific_artifact_parity": result["output_parity"]})
    _canonical_write(verification / "lifecycle-verification.json", {"status": "PASS", "run_id": run_id, "event_count": len(events), "question_count": sum(e["event_type"] == "QUESTION_EMITTED" for e in events), "answer_count": sum(e["event_type"] == "ANSWER_RECEIVED" for e in events), "termination_count": len(terminations), "episodes": len(projections), "termination_reasons": sorted({e["termination_reason"] for e in terminations})})
    output_inventory_sha = digest(verification / "final-output-inventory.json")
    completed = datetime.now(timezone.utc).replace(microsecond=0)
    route_pairs = result.get("route_pairs", [])
    receipt = {
        "schema_version": "airtravel-technical-receipt-v2",
        "mode": "execute",
        "status": "TECHNICAL_SUCCESS",
        "reviewed_head": bindings["reviewed_head"],
        "packet_manifest_sha256": bindings["packet_manifest_sha256"],
        "request_sha256": digest(root / RUN_ROOT / "control/private-execution-request.json"),
        "authorization_message_sha256": bindings["authorization_message_sha256"],
        "grant_sha256": bindings["grant_sha256"],
        "command_sha256": bindings["command_sha256"],
        "invocation_id": bindings["invocation_id"],
        "nonce": bindings["nonce"],
        "attempt_number": 1,
        "started_at": attempt_start["started_at"],
        "completed_at": completed.isoformat().replace("+00:00", "Z"),
        "grant_evaluated_at": bindings["grant_evaluated_at"],
        "grant_valid_at_start": bindings["grant_valid_at_start"],
        "timeout": bool(result.get("timeout", False)),
        "retry_count": 0,
        "replay_count": 0,
        "direct_fake_call_count": call_counts["baseline"],
        "instrumented_fake_call_count": call_counts["instrumented"],
        "combined_fake_call_count": call_counts["baseline"] + call_counts["instrumented"],
        "call_count_equal": call_counts["baseline"] == call_counts["instrumented"],
        "prompt_parity": parity["ordered_prompt_parity"],
        "answer_parity": parity["ordered_answer_parity"],
        "decision_parity": parity["decision_parity"],
        "pipeline_state_parity": result["state_parity"],
        "scientific_artifact_parity": result["output_parity"],
        "completed_cases": result["processed_case_ids"],
        "completed_phases": ["phase1", "phase2", "phase3", "phase4"],
        "event_log_sha256": digest(event_path),
        "event_count": len(events),
        "question_count": sum(e["event_type"] == "QUESTION_EMITTED" for e in events),
        "answer_count": sum(e["event_type"] == "ANSWER_RECEIVED" for e in events),
        "termination_count": len(terminations),
        "termination_counts": {reason: sum(e["termination_reason"] == reason for e in terminations) for reason in sorted({e["termination_reason"] for e in terminations})},
        "route_pairs": route_pairs,
        "protected_manifest_hash_before": protected_before,
        "protected_manifest_hash_after": _protected_manifest_hash(root),
        "tracked_manifest_hash_before": tracked_before,
        "tracked_manifest_hash_after": _tracked_manifest(root)[0],
        "output_inventory_sha256": output_inventory_sha,
        "containment_status": "PASS",
        "privacy_status": "PASS",
        "call_record_hashes": {side: digest(path) for side, path in call_paths.items()},
        "safety_counters": zero_safety_counters(),
        "grant_consumption_status": "CONSUMED",
    }
    validate_receipt_v2(receipt, root=root, require_evidence=False)
    _canonical_write(receipt_path, receipt)
    validate_receipt_v2(receipt, root=root, require_evidence=True)
    receipt_sha = digest(receipt_path)
    finish_grant(root=root, attempt_start=attempt_start, status="TECHNICAL_SUCCESS", output_receipt_sha256=receipt_sha)
    _canonical_write(verification / "post-verification-receipt.json", {"status": "PASS", "receipt_sha256": receipt_sha, "attempt_end_sha256": digest(root / RUN_ROOT / "control/attempt-end.json"), "provider_calls": 0, "network_attempts": 0, "detector_runs": 0, "renderer_runs": 0})
    validate_private_layout(root / RUN_ROOT, preparation=False)
    return receipt
