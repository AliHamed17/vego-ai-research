from __future__ import annotations

import asyncio
import hashlib
import json
import re
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from .config import canonical_json, canonical_sha256, prompt_sha256, validate_config
from .paths import ensure_safe_output_root
from .schemas import validate_receipt, validate_result


class Study2RunError(ValueError):
    """Raised for a fail-closed Study 2 run setup error."""


class AsyncClient(Protocol):
    async def complete(self, request: Any) -> Any: ...


@dataclass(frozen=True)
class CallRequest:
    condition: str
    case_id: str
    label: str
    system_prompt: str
    user_prompt: str
    model_id: str
    temperature: float
    max_output_tokens: int
    timeout_seconds: float


_SECRET_RE = re.compile(r"(?:sk-[A-Za-z0-9_-]{8,}|AIza[A-Za-z0-9_-]{12,}|Bearer\s+\S+|(?:api[_ -]?key|password)\s*[:=])", re.I)
_ALLOWED_COMPLIANCE = {"Satisfied", "Partially-Satisfied", "Not-Satisfied"}
_ALLOWED_LABELS = {"Alternative", "Domain Mistake", "Language Mistake"}
_ALLOWED_SEVERITY = {"High", "Medium", "Low", "N/A"}
_ALLOWED_FIXTURE_MODES = {"no_questions", "two_rounds", "max_rounds"}


class Study2Runner:
    def __init__(
        self,
        *,
        config: dict[str, Any],
        cases: list[dict[str, Any]],
        client: AsyncClient,
        output_root: Path,
        code_sha: str,
        approved_root: Path | None = None,
    ) -> None:
        validate_config(config)
        self.config = config
        self.cases = self._validate_cases(cases)
        self.client = client
        self.output_root = Path(output_root)
        self.code_sha = code_sha
        self.config_sha256 = canonical_sha256(config)
        self._allowed_root = (approved_root or self.output_root.parent).resolve(strict=False)
        self.corpus_hashes = {
            row["path"]: row["sha256"] for row in self.config["corpus"]["files"]
        }

    def _validate_cases(self, cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if len(cases) != len(self.config["case_ids"]):
            raise Study2RunError("case count does not match frozen configuration")
        by_id = {str(row.get("case_id")): row for row in cases}
        if list(by_id) != self.config["case_ids"] or any(
            not isinstance(row.get("case_id"), str)
            or not isinstance(row.get("case_model"), str)
            or row.get("fixture_only") is not True
            for row in cases
        ):
            raise Study2RunError("preflight requires four ordered ENGINEERING_FIXTURE_ONLY cases")
        return [by_id[case_id] for case_id in self.config["case_ids"]]

    @property
    def _policy(self) -> dict[str, Any]:
        return self.config["execution"]

    async def _call(self, request: CallRequest, state: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
        last_code = "UNKNOWN"
        max_attempts = int(self._policy["retries"]) + 1
        for attempt in range(1, max_attempts + 1):
            async with state["semaphore"]:
                async with state["lock"]:
                    if state["attempts"] >= self._policy["call_ceiling"]:
                        raise Study2RunError("CALL_CEILING_EXCEEDED")
                    state["attempts"] += 1
                    state["attempt_markers"].append({"label": request.label, "attempt": attempt})
                try:
                    response = await asyncio.wait_for(
                        self.client.complete(request), timeout=float(self._policy["timeout_seconds"])
                    )
                except asyncio.TimeoutError:
                    last_code = "TIMEOUT"
                except Exception as exc:  # noqa: BLE001 - sanitized into a receipt
                    last_code = type(exc).__name__.upper()
                else:
                    payload = getattr(response, "payload", None)
                    if _contains_secret(payload):
                        state["privacy_counters"]["secrets_detected"] += 1
                        return None, {"valid": False, "reason_code": "SECRET_LEAK"}
                    cost = float(getattr(response, "cost_usd", -1))
                    input_tokens = int(getattr(response, "input_tokens", -1))
                    output_tokens = int(getattr(response, "output_tokens", -1))
                    if input_tokens < 0 or output_tokens < 0 or cost < 0:
                        last_code = "MISSING_USAGE"
                    elif state["cost_usd"] + cost > float(self._policy["cost_ceiling_usd"]):
                        raise Study2RunError("COST_CEILING_EXCEEDED")
                    else:
                        state["cost_usd"] += cost
                        state["input_tokens"] += input_tokens
                        state["output_tokens"] += output_tokens
                        state["successful_calls"] += 1
                        return payload, {
                            "valid": True,
                            "reason_code": None,
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                            "cost_usd": cost,
                        }
        return None, {"valid": False, "reason_code": last_code}

    def _prompt(self, condition: str, case: dict[str, Any]) -> dict[str, str]:
        if condition == "VEGO_AI_OFF":
            system = "STUDY2_OFF_DIRECT_V1: evaluate one case against the frozen guideline objective."
            user = f"case={case['case_id']}\nobjective=map guidelines and identify uncovered fragments\n"
        else:
            system = "STUDY2_ON_ORCHESTRATED_V1: use role-scoped agents and inter-agent Q&A."
            user = f"case={case['case_id']}\nobjective=map guidelines, inspect variability, and record Q&A.\n"
        return {"system": system, "user": user}

    async def _run_condition(self, condition: str, *, fixture_mode: str = "two_rounds") -> dict[str, Any]:
        if fixture_mode not in _ALLOWED_FIXTURE_MODES:
            raise Study2RunError(f"unknown fixture mode: {fixture_mode}")
        condition_dir = ensure_safe_output_root(self.output_root / condition, self._allowed_root)
        condition_dir.mkdir(parents=True, exist_ok=True)
        state: dict[str, Any] = {
            "semaphore": asyncio.Semaphore(int(self._policy["concurrency"])),
            "lock": asyncio.Lock(),
            "attempts": 0,
            "successful_calls": 0,
            "attempt_markers": [],
            "cost_usd": 0.0,
            "input_tokens": 0,
            "output_tokens": 0,
            "privacy_counters": {"secrets_detected": 0, "raw_content_persisted": 0},
        }
        started = time.perf_counter()
        rows: list[dict[str, Any]] = []
        prompt_sha_by_call: dict[str, str] = {}

        async def one(case: dict[str, Any]) -> None:
            prompt = self._prompt(condition, case)
            roles = ("agent1", "agent2", "agent3", "agent4") if condition == "VEGO_AI_ON" else ("direct",)
            payload: Any = None
            for role in roles:
                role_prompt = {
                    "system": f"{prompt['system']} role={role}",
                    "user": prompt["user"],
                }
                label = f"{condition.lower()}/{case['case_id']}/{role}"
                prompt_sha_by_call[label] = prompt_sha256(role_prompt)
                request = CallRequest(
                    condition=condition,
                    case_id=case["case_id"],
                    label=label,
                    system_prompt=role_prompt["system"],
                    user_prompt=role_prompt["user"],
                    model_id=self.config["model"]["model_id"],
                    temperature=float(self.config["model"]["temperature"]),
                    max_output_tokens=int(self.config["model"]["max_output_tokens"]),
                    timeout_seconds=float(self._policy["timeout_seconds"]),
                )
                try:
                    payload, usage = await self._call(request, state)
                except Study2RunError as exc:
                    rows.append(self._failure_row(case["case_id"], role_prompt, str(exc)))
                    return
                if not usage["valid"]:
                    rows.append(self._failure_row(case["case_id"], role_prompt, usage["reason_code"]))
                    return
                valid, reason = validate_case_output(case["case_id"], payload)
                if not valid:
                    rows.append(self._failure_row(case["case_id"], role_prompt, reason))
                    return
            rows.append(
                {
                    "case_id": case["case_id"],
                    "status": "PASS",
                    "prompt_sha256": prompt_sha_by_call[f"{condition.lower()}/{case['case_id']}/{roles[-1]}"],
                    "validation": {"valid": True, "reason_code": None},
                    "mapping_rows": len(payload["existing_mapping"]),
                    "uncovered_fragments": len(payload["uncovered_fragments"]),
                }
            )

        await asyncio.gather(*(one(case) for case in self.cases))
        ended = time.perf_counter()
        rows.sort(key=lambda row: row["case_id"])
        condition_status = "PASS" if all(row["status"] == "PASS" for row in rows) else "TECHNICAL_FAILURE"
        questions, answers, events = (0, 0, [])
        if condition == "VEGO_AI_ON" and condition_status == "PASS":
            questions, answers, events = self._qa_events(fixture_mode)
        result = {
            "schema_version": "study2-result-v1",
            "evidence_class": "ENGINEERING_FIXTURE_ONLY",
            "condition": condition,
            "run_id": self.config["run_id"],
            "setting_id": self.config["setting_id"],
            "corpus_id": self.config["corpus_id"],
            "corpus_hashes": self.corpus_hashes,
            "code_sha256": self.code_sha,
            "configuration_sha256": self.config_sha256,
            "model": self.config["model"],
            "control_policy": self._policy,
            "objective_schema": self.config["output"]["schema_id"],
            "fixture_mode": fixture_mode,
            "prompt_sha_by_case": {row["case_id"]: row["prompt_sha256"] for row in rows},
            "prompt_sha_by_call": prompt_sha_by_call,
            "cases": rows,
            "successful_cases": sum(row["status"] == "PASS" for row in rows),
            "technical_failures": sum(row["status"] != "PASS" for row in rows),
            "status": condition_status,
            "failure_code": next((row["validation"]["reason_code"] for row in rows if row["status"] != "PASS"), None),
            "agent_decomposition": condition == "VEGO_AI_ON",
            "inter_agent_qa": condition == "VEGO_AI_ON",
            "questions": questions,
            "answers": answers,
            "episodes": len({event["episode_id"] for event in events}),
            "events": events,
            "detector_v1": {
                "status": "APPLICABLE" if condition == "VEGO_AI_ON" else "NOT_APPLICABLE",
                "denominator": "EPISODES" if condition == "VEGO_AI_ON" else "NOT_APPLICABLE",
            },
            "attempts": state["attempts"],
            "attempt_markers": state["attempt_markers"],
            "calls": state["attempts"],
            "successful_calls": state["successful_calls"],
            "retries_used": max(
                0,
                state["attempts"]
                - len(self.cases) * (4 if condition == "VEGO_AI_ON" else 1),
            ),
            "input_tokens": state["input_tokens"],
            "output_tokens": state["output_tokens"],
            "cost_usd": round(state["cost_usd"], 6),
            "elapsed_seconds": round(ended - started, 6),
            "privacy_counters": state["privacy_counters"],
            "provider_calls": 0,
            "external_calls": 0,
            "lifecycle": _lifecycle_summary_raw(
                events,
                report_status=condition_status,
            ),
            "output_validation": {
                "valid_cases": sum(row["validation"]["valid"] is True for row in rows),
                "invalid_cases": sum(row["validation"]["valid"] is False for row in rows),
            },
        }
        validate_result(result)
        _write_json(condition_dir / "result.json", result)
        _write_jsonl(condition_dir / "events.jsonl", events)
        return result

    def _failure_row(self, case_id: str, prompt: dict[str, str], reason: str) -> dict[str, Any]:
        return {
            "case_id": case_id,
            "status": "TECHNICAL_FAILURE",
            "prompt_sha256": prompt_sha256(prompt),
            "validation": {"valid": False, "reason_code": reason},
            "mapping_rows": None,
            "uncovered_fragments": None,
        }

    def _qa_events(self, fixture_mode: str) -> tuple[int, int, list[dict[str, Any]]]:
        if fixture_mode not in _ALLOWED_FIXTURE_MODES:
            raise Study2RunError(f"unknown fixture mode: {fixture_mode}")
        if fixture_mode == "no_questions":
            return 0, 0, []
        rounds = 10 if fixture_mode == "max_rounds" else 2
        terminal = "TERMINATED_MAX_ROUNDS" if fixture_mode == "max_rounds" else "CONVERGED"
        events: list[dict[str, Any]] = []
        for case in self.config["case_ids"]:
            episode_id = "ep-" + hashlib.sha256(
                f"{self.config['run_id']}|{case}|agent3|agent1|case_inspection|resolve".encode()
            ).hexdigest()[:24]
            for round_index in range(1, rounds + 1):
                question_id = f"{episode_id}:q:{round_index}"
                question = {
                    "run_id": self.config["run_id"],
                    "episode_id": episode_id,
                    "event_type": "QUESTION_EMITTED",
                    "question_id": question_id,
                    "case_id": case,
                    "source_agent": "agent3",
                    "target_agent": "agent1",
                    "round_index": round_index,
                    "question_text_ref": {"sha256": hashlib.sha256(f"q:{case}:{round_index}".encode()).hexdigest(), "length": len(f"q:{case}:{round_index}")},
                }
                question["event_id"] = hashlib.sha256(canonical_json(question)).hexdigest()
                answer = {
                    **question,
                    "event_type": "ANSWER_RECEIVED",
                    "answer_to_question_id": question_id,
                    "answer_text_ref": {"sha256": hashlib.sha256(f"a:{case}:{round_index}".encode()).hexdigest(), "length": len(f"a:{case}:{round_index}")},
                    "answer_confidence": "Medium",
                }
                answer["event_id"] = hashlib.sha256(canonical_json(answer)).hexdigest()
                events.extend((question, answer))
            terminal_event = {
                "run_id": self.config["run_id"],
                "episode_id": episode_id,
                "event_type": "EPISODE_TERMINATED",
                "termination_reason": terminal,
                "round_index": rounds,
            }
            terminal_event["event_id"] = hashlib.sha256(canonical_json(terminal_event)).hexdigest()
            events.append(terminal_event)
        return rounds * len(self.config["case_ids"]), rounds * len(self.config["case_ids"]), events

    async def run_on(self, *, fixture_mode: str = "two_rounds") -> dict[str, Any]:
        return await self._run_condition("VEGO_AI_ON", fixture_mode=fixture_mode)

    async def run_off(self) -> dict[str, Any]:
        return await self._run_condition("VEGO_AI_OFF")

    async def run_both(self, *, fixture_mode: str = "two_rounds") -> dict[str, Any]:
        on = await self.run_on(fixture_mode=fixture_mode)
        off = await self.run_off()
        artifacts: dict[str, dict[str, str]] = {}
        for condition in ("VEGO_AI_ON", "VEGO_AI_OFF"):
            directory = self.output_root / condition
            result_path = directory / "result.json"
            event_path = directory / "events.jsonl"
            manifest = {
                "schema_version": "study2-pipeline-manifest-v1",
                "condition": condition,
                "files": {
                    "result.json": _file_sha256(result_path),
                    "events.jsonl": _file_sha256(event_path),
                },
            }
            manifest_path = directory / "pipeline-output-manifest.json"
            _write_json(manifest_path, manifest)
            artifacts[condition] = {
                "result_file_sha256": _file_sha256(result_path),
                "event_log_sha256": _file_sha256(event_path),
                "pipeline_manifest_sha256": _file_sha256(manifest_path),
            }
        receipt = {
            "schema_version": "study2-run-receipt-v1",
            "evidence_class": "ENGINEERING_FIXTURE_ONLY",
            "scientific_result_status": "NOT_EXECUTED",
            "study1_pooled": False,
            "run_id": self.config["run_id"],
            "setting_id": self.config["setting_id"],
            "corpus_id": self.config["corpus_id"],
            "corpus_hashes": self.corpus_hashes,
            "code_sha256": self.code_sha,
            "configuration_sha256": self.config_sha256,
            "conditions": {
                "VEGO_AI_ON": {
                    **artifacts["VEGO_AI_ON"],
                    "result_file_hashes": {"result.json": artifacts["VEGO_AI_ON"]["result_file_sha256"]},
                    "lifecycle_summary": _lifecycle_summary(on),
                    "summary": _receipt_condition_summary(on),
                },
                "VEGO_AI_OFF": {
                    **artifacts["VEGO_AI_OFF"],
                    "result_file_hashes": {"result.json": artifacts["VEGO_AI_OFF"]["result_file_sha256"]},
                    "lifecycle_summary": _lifecycle_summary(off),
                    "summary": _receipt_condition_summary(off),
                },
            },
            "privacy_counters": {
                "raw_content_persisted": 0,
                "secrets_detected": on["privacy_counters"]["secrets_detected"] + off["privacy_counters"]["secrets_detected"],
            },
            "provider_calls": 0,
            "external_calls": 0,
        }
        validate_receipt(receipt)
        _write_json(self.output_root / "run-receipt.json", receipt)
        normalized_receipt = {
            "evidence_class": receipt["evidence_class"],
            "scientific_result_status": receipt["scientific_result_status"],
            "study1_pooled": receipt["study1_pooled"],
            "run_id": receipt["run_id"],
            "setting_id": receipt["setting_id"],
            "corpus_id": receipt["corpus_id"],
            "code_sha256": receipt["code_sha256"],
            "configuration_sha256": receipt["configuration_sha256"],
            "conditions": {
                condition: receipt["conditions"][condition]["lifecycle_summary"]
                for condition in ("VEGO_AI_ON", "VEGO_AI_OFF")
            },
            "privacy_counters": receipt["privacy_counters"],
        }
        normalized = {
            "config": self.config_sha256,
            "code": self.code_sha,
            "on": _normalized_condition(on),
            "off": _normalized_condition(off),
            "receipt": normalized_receipt,
        }
        normalized_sha = canonical_sha256(normalized)
        return {
            "schema_version": "study2-on-off-comparison-v1",
            "evidence_class": "ENGINEERING_FIXTURE_ONLY",
            "conditions": {"VEGO_AI_ON": on, "VEGO_AI_OFF": off},
            "receipt": receipt,
            "normalized_sha256": normalized_sha,
        }


def validate_case_output(case_id: str, payload: Any) -> tuple[bool, str | None]:
    if not isinstance(payload, dict):
        return False, "OUTPUT_NOT_OBJECT"
    required = {"skill_version", "case_id", "existing_mapping", "coverage_summary", "uncovered_fragments"}
    if set(payload) != required:
        return False, "OUTPUT_SCHEMA_KEYS"
    if payload["case_id"] != case_id:
        return False, "CASE_ID_MISMATCH"
    if not isinstance(payload["skill_version"], str) or not payload["skill_version"]:
        return False, "SKILL_VERSION_INVALID"
    if not isinstance(payload["existing_mapping"], list) or not isinstance(payload["uncovered_fragments"], list):
        return False, "REQUIRED_ARRAY_INVALID"
    summary = payload["coverage_summary"]
    if not isinstance(summary, dict):
        return False, "COVERAGE_SUMMARY_INVALID"
    if set(summary) != {"satisfied", "partially_satisfied", "not_satisfied"} or any(
        not isinstance(summary[key], int) or isinstance(summary[key], bool) or summary[key] < 0 for key in summary
    ):
        return False, "COVERAGE_SUMMARY_INVALID"
    for row in payload["existing_mapping"]:
        if not isinstance(row, dict) or set(row) != {"guideline_id", "evidence", "compliance_status", "notes"}:
            return False, "MAPPING_ROW_INVALID"
        if any(not isinstance(row[key], str) for key in ("guideline_id", "evidence", "notes")):
            return False, "MAPPING_ROW_TYPES_INVALID"
        if not isinstance(row["compliance_status"], str) or row["compliance_status"] not in _ALLOWED_COMPLIANCE:
            return False, "MAPPING_STATUS_INVALID"
    for row in payload["uncovered_fragments"]:
        if not isinstance(row, dict) or set(row) != {"fragment", "label", "severity", "reason"}:
            return False, "FRAGMENT_ROW_INVALID"
        if any(not isinstance(row[key], str) for key in ("fragment", "reason")):
            return False, "FRAGMENT_ROW_TYPES_INVALID"
        if (
            not isinstance(row["label"], str)
            or not isinstance(row["severity"], str)
            or row["label"] not in _ALLOWED_LABELS
            or row["severity"] not in _ALLOWED_SEVERITY
        ):
            return False, "FRAGMENT_ENUM_INVALID"
    return True, None


def _contains_secret(value: Any) -> bool:
    try:
        return bool(_SECRET_RE.search(json.dumps(value, ensure_ascii=False)))
    except (TypeError, ValueError):
        return True


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_bytes(canonical_json(payload))


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(canonical_json(row).decode("utf-8") for row in rows), encoding="utf-8")


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _lifecycle_summary(report: dict[str, Any]) -> dict[str, Any]:
    reasons = Counter(event.get("termination_reason") for event in report["events"] if event["event_type"] == "EPISODE_TERMINATED")
    return {
        "episodes": report["episodes"],
        "questions": report["questions"],
        "answers": report["answers"],
        "termination_reasons": {key: value for key, value in sorted(reasons.items()) if key is not None},
        "complete": report["status"] == "PASS",
    }


def _receipt_condition_summary(report: dict[str, Any]) -> dict[str, Any]:
    """Copy only aggregate, hash-safe condition fields into the receipt."""
    return {
        "status": report["status"],
        "fixture_mode": report["fixture_mode"],
        "prompt_sha_by_case": report["prompt_sha_by_case"],
        "prompt_sha_by_call": report["prompt_sha_by_call"],
        "attempts": report["attempts"],
        "attempt_markers": report["attempt_markers"],
        "calls": report["calls"],
        "successful_calls": report["successful_calls"],
        "retries_used": report["retries_used"],
        "input_tokens": report["input_tokens"],
        "output_tokens": report["output_tokens"],
        "cost_usd": report["cost_usd"],
        "output_validation": report["output_validation"],
        "privacy_counters": report["privacy_counters"],
        "provider_calls": report["provider_calls"],
        "external_calls": report["external_calls"],
    }


def _lifecycle_summary_raw(events: list[dict[str, Any]], *, report_status: str) -> dict[str, Any]:
    reasons = Counter(
        event.get("termination_reason")
        for event in events
        if event["event_type"] == "EPISODE_TERMINATED"
    )
    return {
        "episodes": len({event["episode_id"] for event in events}),
        "questions": sum(event["event_type"] == "QUESTION_EMITTED" for event in events),
        "answers": sum(event["event_type"] == "ANSWER_RECEIVED" for event in events),
        "termination_reasons": {
            key: value for key, value in sorted(reasons.items()) if key is not None
        },
        "complete": report_status == "PASS",
    }


def _normalized_condition(report: dict[str, Any]) -> dict[str, Any]:
    return {
        key: report[key]
        for key in (
            "condition",
            "status",
            "prompt_sha_by_case",
            "prompt_sha_by_call",
            "successful_cases",
            "technical_failures",
            "agent_decomposition",
            "inter_agent_qa",
            "fixture_mode",
            "questions",
            "answers",
            "episodes",
            "detector_v1",
            "attempts",
            "attempt_markers",
            "retries_used",
            "input_tokens",
            "output_tokens",
            "cost_usd",
            "privacy_counters",
            "provider_calls",
            "external_calls",
        )
    }
