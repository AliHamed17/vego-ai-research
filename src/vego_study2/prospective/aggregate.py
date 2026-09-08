"""Redacted public aggregate builder and recomputing validator.

The public aggregate may contain counts, enumerations, hashes, identifiers,
timestamps and numbers.  It may never contain corpus bytes, prompt text,
model answers, evidence strings, fragment text or absolute private paths.
:func:`assert_redacted` enforces the allowlist; :func:`validate_public`
recomputes the aggregate from the private evidence and compares digests.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from . import constants as c
from .contract import canonical_sha256

_SAFE_STRING = re.compile(r"^[A-Za-z0-9_.:+/${}\-\s,()<>]{0,160}$")
_PATH_LIKE = re.compile(r"(?i)(?:[a-z]:\\|[a-z]:/|/users/|/home/|\\\\)")
_LONG_PROSE = re.compile(r"(?:\S+\s+){12,}")
_PROSE_KEYS = frozenset({"claim_boundary", "detail", "credential_source", "algorithm"})


class RedactionError(ValueError):
    pass


def _walk_strings(value: Any, path: str = "$", key: str = ""):
    if isinstance(value, dict):
        for name, item in value.items():
            yield from _walk_strings(item, f"{path}.{name}", name)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk_strings(item, f"{path}[{index}]", key)
    elif isinstance(value, str):
        yield path, key, value


def assert_redacted(aggregate: dict[str, Any], *, forbidden_fragments: list[str] | None = None) -> None:
    """Allowlist check: identifiers, enums, hashes, numbers and short labels only.

    Keys in ``_PROSE_KEYS`` hold harness-authored sentences and are exempt from
    the prose and character rules but never from the path and fragment rules.
    """
    dump = json.dumps(aggregate, ensure_ascii=False)
    for path, key, text in _walk_strings(aggregate):
        if _PATH_LIKE.search(text) and c.PRIVATE_ROOT_TOKEN not in text:
            raise RedactionError(f"absolute path-like value at {path}")
        if key in _PROSE_KEYS:
            continue
        if _LONG_PROSE.search(text):
            raise RedactionError(f"prose-like value at {path}")
        if not _SAFE_STRING.match(text):
            raise RedactionError(f"disallowed characters at {path}")
    for fragment in forbidden_fragments or []:
        if fragment and fragment in dump:
            raise RedactionError("public aggregate contains private text")


def _strip_row(row: dict[str, Any]) -> dict[str, Any]:
    keep = {
        "case_id", "condition", "status", "failure_code", "output_sha256", "output_valid", "metrics",
        "elapsed_seconds", "requests", "prompt_tokens", "completion_tokens", "cost_usd", "episodes",
        "questions", "answers", "detector_v1", "prompt_sha256", "skill_version_reported", "label_counts",
        "first_request_at", "last_request_at", "started_at", "completed_at",
    }
    return {k: v for k, v in row.items() if k in keep}


def build_public_aggregate(receipt: dict[str, Any], ledger: list[dict[str, Any]]) -> dict[str, Any]:
    conditions = {}
    for name, block in receipt["conditions"].items():
        rows = [_strip_row(r) for r in block["cases"]]
        cond_ledger = [e for e in ledger if e.get("condition") == name]
        ok = [e for e in cond_ledger if e.get("status") == "OK"]
        for row in rows:
            if name == c.CONDITION_OFF:
                mine = [e for e in cond_ledger if e.get("case_id") == row["case_id"]]
                row["requests"] = len(mine)
                row["prompt_tokens"] = sum(e.get("prompt_tokens") or 0 for e in mine)
                row["completion_tokens"] = sum(e.get("completion_tokens") or 0 for e in mine)
                row["cost_usd"] = round(sum(e.get("cost_usd") or 0.0 for e in mine), 6)
        conditions[name] = {
            "status": block["status"],
            "planned_cases": block["planned_cases"],
            "completed_cases": block["completed_cases"],
            "schema_invalid_cases": sum(1 for r in rows if r["status"] == "SCHEMA_INVALID"),
            "technical_failure_cases": sum(1 for r in rows if r["status"] in {"TECHNICAL_FAILURE", "STOPPED_AT_CAP", "NOT_PRODUCED"}),
            "elapsed_seconds": block["elapsed_seconds"],
            "requests": len(cond_ledger),
            "successful_requests": len(ok),
            "transport_errors": sum(1 for e in cond_ledger if e.get("status") == "TRANSPORT_ERROR"),
            "provider_errors": sum(1 for e in cond_ledger if e.get("status") == "PROVIDER_ERROR"),
            "retried_requests": sum(1 for e in cond_ledger if e.get("retry_of_seq")),
            "prompt_tokens": sum(e.get("prompt_tokens") or 0 for e in cond_ledger),
            "completion_tokens": sum(e.get("completion_tokens") or 0 for e in cond_ledger),
            "cost_usd": round(sum(e.get("cost_usd") or 0.0 for e in cond_ledger), 6),
            "finish_reasons": _count(e.get("finish_reason") for e in ok),
            "response_models": _count(e.get("response_model") for e in ok),
            "agent_decomposition": block["agent_decomposition"],
            "inter_agent_qa": block["inter_agent_qa"],
            "detector_v1": block["detector_v1"],
            "cases": rows,
        }
        if name == c.CONDITION_ON:
            conditions[name].update({
                "setting_level_requests": block["setting_level_requests"],
                "setting_level_cost_usd": block["setting_level_cost_usd"],
                "setting_level_label_counts": block["setting_level_label_counts"],
                "episode_summary": block["episode_summary"],
                "episodes": [
                    {k: v for k, v in ep.items() if k in {
                        "episode_id", "case_id", "classification", "candidate_alert", "reason_codes",
                        "all_signals_fired", "round_count", "question_count", "answer_count",
                        "termination_reason", "exclusion_reason", "source_target_pairs"}}
                    for ep in block["episodes"]
                ],
                "routes": block["routes"],
                "event_log_sha256": block["event_log_sha256"],
                "event_count": block["event_count"],
                "event_stream_valid": block["event_stream_valid"],
                "detector_v1_sha256": block["detector_v1_sha256"],
                "protected_runtime_sha256": block["protected_runtime_sha256"],
            })
    aggregate = {
        "schema_version": c.AGGREGATE_SCHEMA,
        "study_id": receipt["study_id"],
        "run_id": receipt["run_id"],
        "mode": receipt["mode"],
        "evidence_class": receipt["evidence_class"],
        "execution_git_sha": receipt["execution_git_sha"],
        "manifest_sha256": receipt["manifest_sha256"],
        "case_selection_sha256": receipt["case_selection_sha256"],
        "receipt_binding_sha256": receipt["receipt_binding"]["sha256"],
        "started_at": receipt["started_at"],
        "completed_at": receipt["completed_at"],
        "model": receipt["model"],
        "budget": receipt["budget"],
        "gates": receipt["gates"],
        "case_ids": receipt["case_ids"],
        "conditions": conditions,
        "paired": _paired(conditions),
        "claim_boundary": receipt["claim_boundary"],
    }
    aggregate["aggregate_sha256"] = canonical_sha256(aggregate)
    return aggregate


def _count(values) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        key = str(value)
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))


def _paired(conditions: dict[str, Any]) -> list[dict[str, Any]]:
    on = {r["case_id"]: r for r in conditions.get(c.CONDITION_ON, {}).get("cases", [])}
    off = {r["case_id"]: r for r in conditions.get(c.CONDITION_OFF, {}).get("cases", [])}
    rows = []
    for case_id in sorted(set(on) | set(off)):
        a, b = on.get(case_id, {}), off.get(case_id, {})
        rows.append({
            "case_id": case_id,
            "both_completed": a.get("status") == "COMPLETED" and b.get("status") == "COMPLETED",
            "on_status": a.get("status"),
            "off_status": b.get("status"),
            "on_mapping_rows": (a.get("metrics") or {}).get("mapping_rows"),
            "off_mapping_rows": (b.get("metrics") or {}).get("mapping_rows"),
            "on_uncovered": (a.get("metrics") or {}).get("uncovered_fragments"),
            "off_uncovered": (b.get("metrics") or {}).get("uncovered_fragments"),
            "on_summary_consistent": (a.get("metrics") or {}).get("coverage_summary_consistent"),
            "off_summary_consistent": (b.get("metrics") or {}).get("coverage_summary_consistent"),
            "on_requests_attributed": a.get("requests"),
            "off_requests": b.get("requests"),
            "on_cost_attributed_usd": a.get("cost_usd"),
            "off_cost_usd": b.get("cost_usd"),
            "on_episodes": a.get("episodes"),
            "on_detector_v1": a.get("detector_v1"),
            "off_detector_v1": "NOT_APPLICABLE",
        })
    return rows


def load_private(output_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    receipt = json.loads((output_root / "run-receipt.json").read_text(encoding="utf-8"))
    ledger_path = output_root / "call-ledger.jsonl"
    ledger = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return receipt, ledger


def validate_public(output_root: Path, public_path: Path) -> dict[str, Any]:
    """Recompute every published value from the private evidence."""
    receipt, ledger = load_private(output_root)
    body = {k: v for k, v in receipt.items() if k != "receipt_binding"}
    binding_ok = receipt["receipt_binding"]["sha256"] == canonical_sha256(body)
    recomputed = build_public_aggregate(receipt, ledger)
    published = json.loads(public_path.read_text(encoding="utf-8"))
    return {
        "receipt_binding_valid": binding_ok,
        "published_sha256": published.get("aggregate_sha256"),
        "recomputed_sha256": recomputed["aggregate_sha256"],
        "match": published == recomputed,
        "ledger_requests": len(ledger),
        "receipt_requests": receipt["budget"]["requests"],
        "ledger_matches_receipt": len(ledger) == receipt["budget"]["requests"],
        "ledger_cost_usd": round(sum(e.get("cost_usd") or 0.0 for e in ledger), 6),
        "receipt_cost_usd": receipt["budget"]["actual_cost_usd"],
    }
