"""Descriptive paired analysis computed from the public aggregate only."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .. import constants as c

ROOT = Path(__file__).resolve().parents[4]
DOCS_DIR = ROOT / "docs" / "research" / "phd-proposal" / "study2-prospective"

FAILURE_STATES = {"TECHNICAL_FAILURE", "STOPPED_AT_CAP", "NOT_PRODUCED", "SCHEMA_INVALID"}


def load_aggregate(run_id: str, public_dir: Path | None = None) -> dict[str, Any]:
    path = (public_dir or DOCS_DIR / "evidence" / run_id) / "public-aggregate.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest_document() -> dict[str, Any]:
    return json.loads((DOCS_DIR / "experiment-manifest.json").read_text(encoding="utf-8"))


def fmt_counts(mapping: Any, empty: str = "none") -> str:
    """Render a {label: count} mapping as 'LABEL n, LABEL n' for prose and slides."""
    if not isinstance(mapping, dict) or not mapping:
        return empty
    return ", ".join(f"{key} {value}" for key, value in sorted(mapping.items(), key=lambda kv: (-kv[1], kv[0])))


def _metric(row: dict[str, Any] | None, key: str) -> Any:
    if not row or not row.get("metrics"):
        return None
    return row["metrics"].get(key)


def _elapsed_on(row: dict[str, Any]) -> float | None:
    first, last = row.get("first_request_at"), row.get("last_request_at")
    if not first or not last:
        return None
    from datetime import datetime

    parse = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))  # noqa: E731
    return round((parse(last) - parse(first)).total_seconds(), 3)


def paired_table(aggregate: dict[str, Any]) -> list[dict[str, Any]]:
    on = {r["case_id"]: r for r in aggregate["conditions"][c.CONDITION_ON]["cases"]}
    off = {r["case_id"]: r for r in aggregate["conditions"][c.CONDITION_OFF]["cases"]}
    rows = []
    for case_id in aggregate["case_ids"]:
        a, b = on.get(case_id, {}), off.get(case_id, {})
        rows.append({
            "case_id": case_id,
            "on_status": a.get("status", "NOT_PRODUCED"),
            "off_status": b.get("status", "NOT_PRODUCED"),
            "on_valid": bool(a.get("output_valid")),
            "off_valid": bool(b.get("output_valid")),
            "on_summary_consistent": _metric(a, "coverage_summary_consistent"),
            "off_summary_consistent": _metric(b, "coverage_summary_consistent"),
            "on_mapping_rows": _metric(a, "mapping_rows"),
            "off_mapping_rows": _metric(b, "mapping_rows"),
            "on_uncovered": _metric(a, "uncovered_fragments"),
            "off_uncovered": _metric(b, "uncovered_fragments"),
            "on_requests": a.get("requests"),
            "off_requests": b.get("requests"),
            "on_cost_usd": a.get("cost_usd"),
            "off_cost_usd": b.get("cost_usd"),
            "on_elapsed_span_s": _elapsed_on(a) if a else None,
            "off_elapsed_s": b.get("elapsed_seconds"),
            "on_episodes": a.get("episodes"),
            "on_questions": a.get("questions"),
            "on_answers": a.get("answers"),
            "on_detector_v1": a.get("detector_v1"),
            "off_detector_v1": "NOT_APPLICABLE",
            "on_prompt_tokens": a.get("prompt_tokens"),
            "off_prompt_tokens": b.get("prompt_tokens"),
            "on_completion_tokens": a.get("completion_tokens"),
            "off_completion_tokens": b.get("completion_tokens"),
        })
    return rows


def condition_summary(aggregate: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out = {}
    for name in (c.CONDITION_ON, c.CONDITION_OFF):
        block = aggregate["conditions"][name]
        rows = block["cases"]
        completed = [r for r in rows if r["status"] == "COMPLETED"]
        out[name] = {
            "status": block["status"],
            "planned": block["planned_cases"],
            "completed": block["completed_cases"],
            "schema_invalid": block["schema_invalid_cases"],
            "technical_failures": block["technical_failure_cases"],
            "failure_rate": round((block["planned_cases"] - block["completed_cases"]) / block["planned_cases"], 3) if block["planned_cases"] else None,
            "requests": block["requests"],
            "successful_requests": block["successful_requests"],
            "transport_errors": block["transport_errors"],
            "provider_errors": block["provider_errors"],
            "retried_requests": block["retried_requests"],
            "prompt_tokens": block["prompt_tokens"],
            "completion_tokens": block["completion_tokens"],
            "cost_usd": block["cost_usd"],
            "elapsed_seconds": block["elapsed_seconds"],
            "cost_per_completed_artifact_usd": round(block["cost_usd"] / len(completed), 6) if completed else None,
            "requests_per_completed_artifact": round(block["requests"] / len(completed), 2) if completed else None,
            "finish_reasons": block["finish_reasons"],
            "response_models": block["response_models"],
            "detector_v1": block["detector_v1"],
            "mapping_rows_total": sum((r.get("metrics") or {}).get("mapping_rows", 0) for r in completed),
            "uncovered_total": sum((r.get("metrics") or {}).get("uncovered_fragments", 0) for r in completed),
            "summary_consistent_count": sum(1 for r in completed if (r.get("metrics") or {}).get("coverage_summary_consistent")),
            "mapping_rows_per_case": [(r.get("metrics") or {}).get("mapping_rows", 0) for r in completed],
            "uncovered_per_case": [(r.get("metrics") or {}).get("uncovered_fragments", 0) for r in completed],
            "fragment_labels_total": _sum_counters((r.get("metrics") or {}).get("fragment_labels", {}) for r in completed),
            "compliance_status_total": _sum_counters((r.get("metrics") or {}).get("coverage_summary_recomputed", {}) for r in completed),
        }
        if name == c.CONDITION_ON:
            out[name].update({
                "setting_level_requests": block["setting_level_requests"],
                "setting_level_cost_usd": block["setting_level_cost_usd"],
                "case_attributed_cost_usd": round(sum(r.get("cost_usd") or 0.0 for r in rows), 6),
                "case_attributed_requests": sum(r.get("requests") or 0 for r in rows),
                "episode_summary": block["episode_summary"],
                "routes": block["routes"],
            })
    return out


def _sum_counters(mappings) -> dict[str, int]:
    total: Counter = Counter()
    for mapping in mappings:
        for key, value in (mapping or {}).items():
            total[key] += int(value or 0)
    return dict(sorted(total.items()))


def paired_differences(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def diff(key_on: str, key_off: str) -> dict[str, Any]:
        pairs = [(r[key_on], r[key_off]) for r in rows if r[key_on] is not None and r[key_off] is not None]
        deltas = [a - b for a, b in pairs]
        return {
            "pairs": len(pairs),
            "on_higher": sum(1 for d in deltas if d > 0),
            "off_higher": sum(1 for d in deltas if d < 0),
            "equal": sum(1 for d in deltas if d == 0),
            "median_delta_on_minus_off": _median(deltas),
            "mean_delta_on_minus_off": round(sum(deltas) / len(deltas), 4) if deltas else None,
        }

    return {
        "mapping_rows": diff("on_mapping_rows", "off_mapping_rows"),
        "uncovered_fragments": diff("on_uncovered", "off_uncovered"),
        "requests": diff("on_requests", "off_requests"),
        "cost_usd": diff("on_cost_usd", "off_cost_usd"),
        "elapsed_seconds": diff("on_elapsed_span_s", "off_elapsed_s"),
        "both_completed": sum(1 for r in rows if r["on_status"] == "COMPLETED" and r["off_status"] == "COMPLETED"),
        "only_on_completed": sum(1 for r in rows if r["on_status"] == "COMPLETED" and r["off_status"] != "COMPLETED"),
        "only_off_completed": sum(1 for r in rows if r["off_status"] == "COMPLETED" and r["on_status"] != "COMPLETED"),
        "neither_completed": sum(1 for r in rows if r["on_status"] != "COMPLETED" and r["off_status"] != "COMPLETED"),
    }


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    return round(ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2, 4)


def detector_section(aggregate: dict[str, Any]) -> dict[str, Any]:
    on = aggregate["conditions"][c.CONDITION_ON]
    episodes = on.get("episodes", [])
    per_case = Counter()
    for episode in episodes:
        per_case[episode["case_id"]] += 1
    cases_without = [r["case_id"] for r in on["cases"] if not r.get("episodes")]
    classifications = Counter(e["classification"] for e in episodes)
    return {
        "applies_to": {c.CONDITION_ON: "APPLICABLE", c.CONDITION_OFF: "NOT_APPLICABLE"},
        "episodes_total": len(episodes),
        "scientific_complete": on.get("episode_summary", {}).get("scientific_complete"),
        "classifications": dict(classifications),
        "reason_codes": on.get("episode_summary", {}).get("detector_v1_reason_codes", {}),
        "candidate_alerts": sum(1 for e in episodes if e.get("candidate_alert")),
        "episodes_per_case": dict(sorted(per_case.items())),
        "cases_with_no_episode": cases_without,
        "setting_level_episodes": per_case.get("SETTING_LEVEL", 0),
        "termination_reasons": on.get("episode_summary", {}).get("termination_reasons", {}),
        "share_of_cases_with_any_candidate": round(
            sum(1 for r in on["cases"] if any(k in {"STRONG_ALERT", "WEAK_ALERT"} for k in (r.get("detector_v1") or {})))
            / len(on["cases"]), 3) if on["cases"] else None,
        "human_labels": "NONE; correctness, precision, recall and F1 are NOT_MEASURED",
    }


def human_section() -> dict[str, Any]:
    return {
        "status": "NOT_MEASURED",
        "raters_scored": 0,
        "raters_required": 2,
        "agreement": "NOT_MEASURED", "correctness": "NOT_MEASURED", "precision": "NOT_MEASURED",
        "recall": "NOT_MEASURED", "f1": "NOT_MEASURED", "workload": "NOT_MEASURED", "benefit": "NOT_MEASURED",
        "decisions": ["REVIEW_WORTHY", "NOT_REVIEW_WORTHY", "INSUFFICIENT_INFORMATION"],
        "actions": ["verify", "clarify", "revise guideline", "no action"],
    }


def accounting(aggregate: dict[str, Any]) -> dict[str, Any]:
    """Reconcile guard-counted requests with ledger rows; charge any gap at full reserve."""
    budget = aggregate["budget"]
    ledger_rows = sum(block["requests"] for block in aggregate["conditions"].values())
    unrecorded = max(0, budget["requests"] - ledger_rows)
    return {
        "receipt_requests": budget["requests"],
        "ledger_requests": ledger_rows,
        "unrecorded_in_flight_requests": unrecorded,
        "recorded_cost_usd": budget["actual_cost_usd"],
        "spend_upper_bound_usd": round(budget["actual_cost_usd"] + unrecorded * budget["per_request_reserve_usd"], 6),
        "note": (
            "a request reserved by the guard but cancelled in flight when a cap stopped the condition returns no usage; "
            "it is counted as issued and charged at the full per-request reservation in the upper bound"
            if unrecorded else "every issued request has a ledger row"
        ),
    }


def build_analysis(aggregate: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    rows = paired_table(aggregate)
    return {
        "accounting": accounting(aggregate),
        "run_id": aggregate["run_id"],
        "mode": aggregate["mode"],
        "evidence_class": aggregate["evidence_class"],
        "execution_git_sha": aggregate["execution_git_sha"],
        "manifest_sha256": aggregate["manifest_sha256"],
        "model": aggregate["model"],
        "budget": aggregate["budget"],
        "caps": manifest["caps"],
        "whole_study_reservation_usd": manifest["budget"]["whole_study_reservation_usd"],
        "case_ids": aggregate["case_ids"],
        "paired": rows,
        "conditions": condition_summary(aggregate),
        "differences": paired_differences(rows),
        "detector": detector_section(aggregate),
        "human": human_section(),
        "gates": aggregate["gates"],
        "claim_boundary": aggregate["claim_boundary"],
        "started_at": aggregate["started_at"],
        "completed_at": aggregate["completed_at"],
    }
