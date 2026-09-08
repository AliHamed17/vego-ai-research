"""Build the frozen Study 2 prospective documents from constants and the private frame.

Writes four machine-readable freeze documents under
``docs/research/phd-proposal/study2-prospective/``: the case-selection
manifest, the budget-reservation record, the self-bound experiment manifest and
the command fingerprint.  Only metadata leaves the private root.  Re-running
after any code or document change rebinds the manifest; the runner refuses a
manifest whose digests no longer match.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _relative in ("src", "scripts", "VEGO-AI/framework"):
    if str(ROOT / _relative) not in sys.path:
        sys.path.insert(0, str(ROOT / _relative))

STUDY1_CASE_SHA256 = {
    "01": "240b034834e383b9844e9a3e9796f6be9b3d47fc95de6606ed022d278d751f91",
    "02": "08399ca9432c1399f3f9784d34741314e4d39e40307a6efb14fa92a1c138b1d6",
    "03": "ee4d689d59c9ce3a5e8ff385747641954bd4821f2efeb18e581dcd1d5441d20a",
    "04": "1c3d15eac71fcaab138857dbbc7153833b3df55ab57925ac756a79dc28dc847a",
}
STUDY1_CALIBRATION = {
    "source": "Study 1 real run receipt (private), figures already published in the Hebrew Study 1 readout",
    "requests": 43,
    "cases": 4,
    "requests_per_case_all_in": 10.75,
    "actual_cost_usd": 0.134972,
    "role": "calibration reference for the operational ON cap only; never the upper bound",
}
DOCUMENTS = {
    "preregistration": "preregistration.md",
    "redaction_privacy_policy": "redaction-privacy-policy.md",
    "claims_and_limitations_contract": "claims-and-limitations-contract.md",
    "human_rater_rubric_he": "human-rater-rubric.he.md",
    "receipt_schema": "../../../../schemas/study2-prospective-receipt-v1.schema.json",
    "manifest_schema": "../../../../schemas/study2-prospective-manifest-v1.schema.json",
    "public_aggregate_schema": "../../../../schemas/study2-prospective-public-aggregate-v1.schema.json",
}

METRICS = [
    {"id": "M1", "section": "A", "definition": "output completeness: per-case shared-contract artifact produced (COMPLETED) versus NOT_PRODUCED/SCHEMA_INVALID/TECHNICAL_FAILURE", "denominator": "planned paired cases", "conditions": ["VEGO_AI_ON", "VEGO_AI_OFF"], "evidence_class": "PROSPECTIVE EMPIRICAL EVIDENCE"},
    {"id": "M2", "section": "A", "definition": "structural validity: artifact validates against study2-condition-output-v1 with consistent coverage summary", "denominator": "produced artifacts per condition", "conditions": ["VEGO_AI_ON", "VEGO_AI_OFF"], "evidence_class": "PROSPECTIVE EMPIRICAL EVIDENCE"},
    {"id": "M3", "section": "A", "definition": "execution cost: provider requests, prompt and completion tokens, priced USD from recorded usage", "denominator": "per condition, with ON setting-level cost shown separately and per case attributed", "conditions": ["VEGO_AI_ON", "VEGO_AI_OFF"], "evidence_class": "PROSPECTIVE EMPIRICAL EVIDENCE"},
    {"id": "M4", "section": "A", "definition": "elapsed wall-clock seconds per condition; OFF per case exact, ON per case as first-to-last attributed request span under concurrency 2", "denominator": "per condition and per case", "conditions": ["VEGO_AI_ON", "VEGO_AI_OFF"], "evidence_class": "PROSPECTIVE EMPIRICAL EVIDENCE"},
    {"id": "M5", "section": "A", "definition": "technical failure rate: cases with TECHNICAL_FAILURE, STOPPED_AT_CAP or NOT_PRODUCED; retried requests counted", "denominator": "planned paired cases", "conditions": ["VEGO_AI_ON", "VEGO_AI_OFF"], "evidence_class": "PROSPECTIVE EMPIRICAL EVIDENCE"},
    {"id": "M6", "section": "A", "definition": "availability of explainable communication evidence: recorded inter-agent Q&A episodes, questions, answers per case", "denominator": "paired cases; OFF is structurally zero by design, reported as NOT_AVAILABLE not as a deficit", "conditions": ["VEGO_AI_ON", "VEGO_AI_OFF"], "evidence_class": "PROSPECTIVE EMPIRICAL EVIDENCE"},
    {"id": "M7", "section": "B", "definition": "communication metrics: episodes, rounds, termination reasons, source-target routes, answer confidence distribution", "denominator": "scientifically complete ON episodes", "conditions": ["VEGO_AI_ON"], "evidence_class": "PROSPECTIVE EMPIRICAL EVIDENCE"},
    {"id": "M8", "section": "C", "definition": "Detector-v1 candidate labels: STRONG_ALERT, WEAK_ALERT, NO_ALERT, EXCLUDED per episode; NO_EPISODE per case without episodes", "denominator": "scientifically complete ON episodes; NOT_APPLICABLE under OFF", "conditions": ["VEGO_AI_ON"], "evidence_class": "PROSPECTIVE EMPIRICAL EVIDENCE"},
    {"id": "M9", "section": "D", "definition": "business-relevance descriptors: cost per completed artifact, requests per completed artifact, share of cases with any candidate-for-review label", "denominator": "completed artifacts per condition", "conditions": ["VEGO_AI_ON", "VEGO_AI_OFF"], "evidence_class": "PROSPECTIVE EMPIRICAL EVIDENCE"},
    {"id": "M10", "section": "E", "definition": "blinded human assessment: REVIEW_WORTHY / NOT_REVIEW_WORTHY / INSUFFICIENT_INFORMATION per redacted card; agreement, correctness, precision, recall, F1, workload, benefit", "denominator": "cards scored by two independent raters", "conditions": ["VEGO_AI_ON"], "evidence_class": "NOT_MEASURED"},
]
PLANNED_CHARTS = [
    {"id": "C1", "title": "Paired artifact completion and structural validity per case", "metric_ids": ["M1", "M2"], "conditions": ["VEGO_AI_ON", "VEGO_AI_OFF"], "denominator": "12 planned paired cases", "limitation": "one corpus, one model, no ground truth; completion is not correctness"},
    {"id": "C2", "title": "Provider requests and priced cost per condition, ON split into setting-level and case-attributed", "metric_ids": ["M3"], "conditions": ["VEGO_AI_ON", "VEGO_AI_OFF"], "denominator": "all recorded requests including retries", "limitation": "cost from recorded usage at frozen list prices; not a superiority claim"},
    {"id": "C3", "title": "Elapsed time per condition and per case", "metric_ids": ["M4"], "conditions": ["VEGO_AI_ON", "VEGO_AI_OFF"], "denominator": "per condition; ON per case approximate under concurrency", "limitation": "wall-clock includes provider latency variance on one day"},
    {"id": "C4", "title": "Inter-agent Q&A episodes, questions and answers per case (ON only)", "metric_ids": ["M6", "M7"], "conditions": ["VEGO_AI_ON"], "denominator": "recorded episodes", "limitation": "OFF has no episodes by design; absence is structural, not a measured deficit"},
    {"id": "C5", "title": "Detector-v1 candidate labels per episode (ON only, reporting-only)", "metric_ids": ["M8"], "conditions": ["VEGO_AI_ON"], "denominator": "scientifically complete episodes", "limitation": "no human labels; a label is a candidate for inspection, not a confirmed problem"},
    {"id": "C6", "title": "Mapping rows and uncovered fragments per paired case", "metric_ids": ["M1", "M9"], "conditions": ["VEGO_AI_ON", "VEGO_AI_OFF"], "denominator": "completed artifacts", "limitation": "counts are structural descriptors, not quality judgements"},
    {"id": "C7", "title": "Human assessment placeholder", "metric_ids": ["M10"], "conditions": ["VEGO_AI_ON"], "denominator": "NOT_MEASURED", "limitation": "no rater has scored; nothing is plotted until two raters return"},
]
FORBIDDEN_CONCLUSIONS = [
    "Detector-v1 alerts are correct (no human labels exist).",
    "VEGO-AI is universally better, or better on quality (no ground truth, no rated quality yet).",
    "One condition is superior because of cost alone.",
    "OFF produced zero alerts (Detector-v1 is NOT_APPLICABLE under OFF).",
    "Fixture or preflight output is empirical evidence.",
    "A model judgement is a human judgement.",
    "Results generalise beyond this corpus, model, day and configuration.",
]


def build(private_root: Path, sample_size: int) -> dict[str, Path]:
    from vego_study2.prospective import constants as c
    from vego_study2.prospective.budget import (
        design_menu,
        per_request_reserve_usd,
        total_request_cap,
    )
    from vego_study2.prospective.contract import OUTPUT_SCHEMA_PATH, OUTPUT_SCHEMA_SHA256
    from vego_study2.prospective.inventory import build_case_selection, build_eligible_inventory
    from vego_study2.prospective.manifest import (
        BUDGET_PATH,
        CASE_SELECTION_PATH,
        DOCS_DIR,
        FINGERPRINT_PATH,
        MANIFEST_PATH,
        command_fingerprint,
        file_sha256,
        self_bound,
    )
    from vego_study2.prospective.off_runner import off_prompt_template_sha256
    from vego_study2.prospective.on_runner import detector_v1_sha256, protected_runtime_sha256

    def doc_entry(relative: str) -> dict[str, object] | None:
        path = (DOCS_DIR / relative).resolve()
        if not path.is_file():
            return None
        return {"path": path.relative_to(ROOT).as_posix(), "sha256": file_sha256(path)}

    runtime_root = private_root / "fullframe_runtime"
    inventory = build_eligible_inventory(runtime_root, verify_bytes=True)
    selection = build_case_selection(inventory, sample_size, c.SELECTION_SEED, study1_case_sha256=STUDY1_CASE_SHA256)
    selection["frozen_at"] = _now()
    selection["runtime_root_template"] = f"{c.PRIVATE_ROOT_TOKEN}/fullframe_runtime"
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    _write(CASE_SELECTION_PATH, selection)

    menu = design_menu(inventory["eligible_case_count"])
    chosen = next(o for o in menu["options"] if o["option"] == "A_HIGHEST_COVERAGE")
    reserve = per_request_reserve_usd()
    budget = {
        "schema_version": c.BUDGET_SCHEMA,
        "frozen_at": selection["frozen_at"],
        "hard_ceiling_usd": c.HARD_CEILING_USD,
        "guard_ceiling_usd": c.GUARD_CEILING_USD,
        "safety_margin_usd": round(c.HARD_CEILING_USD - c.GUARD_CEILING_USD, 2),
        "safety_margin_reason": "covers any input-token overshoot above the per-request input reserve on the final admitted request",
        "pricing_usd_per_1m_tokens": {"input": c.PRICE_IN_PER_M, "output": c.PRICE_OUT_PER_M, "model": c.MODEL},
        "per_request_reserve": {
            "reserve_input_tokens": c.RESERVE_INPUT_TOKENS,
            "max_output_tokens": c.MAX_OUTPUT_TOKENS,
            "formula": "(reserve_input_tokens x price_in + max_output_tokens x price_out) / 1e6",
            "usd": round(reserve, 7),
        },
        "total_request_cap": {"formula": "floor(guard_ceiling_usd / per_request_reserve_usd)", "value": total_request_cap()},
        "operational_caps_per_case": {
            "VEGO_AI_ON": c.ON_REQUEST_CAP_PER_CASE,
            "VEGO_AI_OFF": c.OFF_REQUEST_CAP_PER_CASE,
            "on_rationale": "1.77x the Study 1 all-in request rate per case (10.75), covering setting-level phases, Q&A rounds, parse re-attempts and transport retries; exceeding it stops ON with STOPPED_AT_CAP",
            "off_rationale": "one logical call with the protected client's full parse re-attempt allowance (3 attempts); transport retries count inside the cap",
        },
        "theoretical_on_bound": {
            "formula": "82 + 61 x N logical calls at MAX_QA_ROUNDS=10 with every answer route taken, each up to 3 parse attempts",
            "note": "exceeds the ceiling at any N >= 4 under full-output reservation; therefore the enforced ceiling is the per-request guard, and the operational caps decide admission",
        },
        "menu": menu,
        "chosen_option": chosen,
        "decision": "A_HIGHEST_COVERAGE: the primary question is a paired per-case comparison, so distinct paired units are worth more than repeats of a default-temperature stochastic system; B has the same reservation with half the distinct cases; C leaves two thirds of the affordable sample unused",
        "whole_study_reservation_usd": chosen["reservation_usd"],
        "study1_calibration_reference": STUDY1_CALIBRATION,
        "rules": [
            "never start a paired unit unless its full ON+OFF reservation fits; all twelve units are reserved before the first request",
            "one transport retry per request, only for a documented transport/provider failure before valid output; a valid but undesirable result is never retried",
            "every retry, failed call and parse re-attempt counts against the caps and the ceiling",
            "a failed or incomplete case remains in the evidence and is reported",
            "never stop early because results are favourable or unfavourable",
        ],
    }
    _write(BUDGET_PATH, budget)

    docs = {name: entry for name, rel in DOCUMENTS.items() if (entry := doc_entry(rel))}
    manifest = {
        "schema_version": c.MANIFEST_SCHEMA,
        "study_id": c.STUDY_ID,
        "protocol_option": "A_HIGHEST_COVERAGE",
        "frozen_at": selection["frozen_at"],
        "setting_id": c.SETTING_ID,
        "corpus_id": c.CORPUS_ID,
        "corpus_commit": c.CORPUS_COMMIT,
        "language_name": c.LANGUAGE_NAME,
        "case_selection": {
            "path": CASE_SELECTION_PATH.relative_to(ROOT).as_posix(),
            "sha256": file_sha256(CASE_SELECTION_PATH),
            "seed": c.SELECTION_SEED,
            "sample_size": sample_size,
            "eligible_case_count": inventory["eligible_case_count"],
            "selected_case_ids": selection["selected_case_ids"],
            "rule": selection["selection_rule"],
        },
        "corpus_hashes": {
            "domain_description": selection["domain_description"]["sha256"],
            "cases": {row["case_id"]: row["sha256"] for row in selection["selected_cases"]},
        },
        "provider": {
            "name": c.PROVIDER, "model": c.MODEL, "api_mode": c.API_MODE, "allowed_hosts": sorted(c.ALLOWED_HOSTS),
            "credential_env": c.CREDENTIAL_ENV, "fallback_model": None, "model_switching": "FORBIDDEN",
        },
        "request_parameters": {
            "max_completion_tokens": c.MAX_OUTPUT_TOKENS,
            "temperature": "PROVIDER_DEFAULT_NOT_SENT",
            "seed": "NOT_SENT",
            "response_format": "NOT_SENT",
            "tools": "NOT_SENT",
            "message_roles": ["system", "user"],
            "request_timeout_seconds": c.REQUEST_TIMEOUT_SECONDS,
            "identical_for_both_conditions": True,
        },
        "conditions": {
            c.CONDITION_ON: {
                "workflow": "unmodified four-agent VEGO-AI pipeline: Language Advisor, Domain Advisor, Model Inspector, Variability Explorer",
                "agent_decomposition": True,
                "inter_agent_qa": True,
                "round_loop": "MAX_QA_ROUNDS as shipped in the protected orchestrator",
                "detector_v1": "APPLICABLE",
                "protected_runtime_sha256": protected_runtime_sha256(),
                "detector_v1_sha256": detector_v1_sha256(),
                "prompts": "protected agent prompt templates, bound by the runtime digests above",
            },
            c.CONDITION_OFF: {
                "workflow": "one direct per-case call with the same model, domain description, candidate model, output schema and ceiling",
                "agent_decomposition": False,
                "inter_agent_qa": False,
                "round_loop": "NONE",
                "detector_v1": "NOT_APPLICABLE",
                "prompt_template_sha256": off_prompt_template_sha256(),
                "skill_version": "off-baseline-v1",
                "forbidden_modules": list(c.OFF_FORBIDDEN_MODULES),
            },
        },
        "execution_order": list(c.CONDITION_ORDER),
        "concurrency": {c.CONDITION_ON: c.MAX_CONCURRENT_CASES, c.CONDITION_OFF: c.MAX_CONCURRENT_CASES},
        "run_timeouts_seconds": {c.CONDITION_ON: c.ON_RUN_TIMEOUT_SECONDS, c.CONDITION_OFF: c.OFF_RUN_TIMEOUT_SECONDS},
        "retry_policy": {
            "transport_retries_per_request": c.TRANSPORT_RETRIES_PER_REQUEST,
            "retry_condition": "APIConnectionError, APITimeoutError, RateLimitError, InternalServerError, asyncio timeout; never on a valid response",
            "valid_but_undesirable_result": "NEVER_RETRIED",
            "parse_reattempts": "protected LLMClient MAX_PARSE_RETRIES=2 applies identically to both conditions; each re-attempt is a metered request",
            "counts_against_caps_and_budget": True,
        },
        "caps": {
            "total_requests": total_request_cap(),
            c.CONDITION_ON: c.ON_REQUEST_CAP_PER_CASE * sample_size,
            c.CONDITION_OFF: c.OFF_REQUEST_CAP_PER_CASE * sample_size,
            "on_requests_per_case": c.ON_REQUEST_CAP_PER_CASE,
            "off_requests_per_case": c.OFF_REQUEST_CAP_PER_CASE,
        },
        "budget": {
            "hard_ceiling_usd": c.HARD_CEILING_USD,
            "guard_ceiling_usd": c.GUARD_CEILING_USD,
            "safety_margin_usd": budget["safety_margin_usd"],
            "per_request_reserve_usd": round(reserve, 7),
            "reserve_input_tokens": c.RESERVE_INPUT_TOKENS,
            "max_output_tokens": c.MAX_OUTPUT_TOKENS,
            "price_in_per_1m_usd": c.PRICE_IN_PER_M,
            "price_out_per_1m_usd": c.PRICE_OUT_PER_M,
            "whole_study_reservation_usd": chosen["reservation_usd"],
            "reservation_path": BUDGET_PATH.relative_to(ROOT).as_posix(),
            "reservation_sha256": file_sha256(BUDGET_PATH),
            "includes": ["successful calls", "failed calls", "transport retries", "parse re-attempts", "both conditions", "preflight fake runs cost nothing and share no budget"],
        },
        "output_root_template": f"{c.PRIVATE_ROOT_TOKEN}/study2-prospective/<run_id>",
        "runtime_root_template": f"{c.PRIVATE_ROOT_TOKEN}/fullframe_runtime",
        "output_schema": {"name": c.CONDITION_OUTPUT_SCHEMA, "path": OUTPUT_SCHEMA_PATH.relative_to(ROOT).as_posix(), "sha256": OUTPUT_SCHEMA_SHA256},
        "detector_v1": {
            "path": "scripts/extract_qa_escalation_features.py",
            "sha256": detector_v1_sha256(),
            "applies_to": {c.CONDITION_ON: "APPLICABLE", c.CONDITION_OFF: "NOT_APPLICABLE"},
            "role": "reporting-only candidate-for-human-review label on recorded ON episodes; never writes a human queue, never alters an answer or model, never causes a retry",
            "thresholds_modified": False,
        },
        "metrics": METRICS,
        "planned_charts": PLANNED_CHARTS,
        "technical_failure_policy": {
            "NOT_PRODUCED": "no artifact for that case and condition; stays in the denominator of M1 and M5",
            "SCHEMA_INVALID": "artifact fails the shared contract; counted in M2, excluded from structural descriptors, never repaired",
            "TECHNICAL_FAILURE": "provider, parse, model-mismatch or secret-detection failure; reported per case with request count",
            "STOPPED_AT_CAP": "a cap or the ceiling was reached; remaining cases reported as not produced",
            "ZERO_EPISODES_UNDER_ON": "valid observation, Detector-v1 contribution NO_EPISODE, distinct from NO_ALERT and NOT_APPLICABLE",
        },
        "stopping_rule": "run every planned unit once; stop only on cap, ceiling, run timeout, model mismatch, credential absence or gate failure; never on observed results",
        "evidence_class": c.EVIDENCE_PROSPECTIVE,
        "documents": docs,
        "human_assessment": {
            "status": "NOT_MEASURED",
            "rubric_path": "docs/research/phd-proposal/study2-prospective/human-rater-rubric.he.md",
            "raters_required": 2,
            "decisions": ["REVIEW_WORTHY", "NOT_REVIEW_WORTHY", "INSUFFICIENT_INFORMATION"],
            "actions": ["verify", "clarify", "revise guideline", "no action"],
            "cards": "blinded redacted cards generated into the private root; only their count and digests are published",
            "not_measured_until_two_raters": ["agreement", "correctness", "precision", "recall", "F1", "workload", "benefit"],
        },
        "forbidden_conclusions": FORBIDDEN_CONCLUSIONS,
    }
    manifest = self_bound(manifest)
    _write(MANIFEST_PATH, manifest)

    planned = ["execute", "--private-root", c.PRIVATE_ROOT_TOKEN, "--expected-head", "<CI_GREEN_HEAD>", "--authorize-live-provider"]
    fingerprint = {
        "schema_version": "study2-prospective-command-fingerprint-v1",
        "frozen_at": selection["frozen_at"],
        "manifest_sha256": manifest["manifest_sha256"],
        "planned_command": command_fingerprint(planned),
        "preflight_command": command_fingerprint(["preflight", "--private-root", c.PRIVATE_ROOT_TOKEN, "--fake-mode", "two_rounds"]),
        "note": "the private root is substituted by the placeholder token; <CI_GREEN_HEAD> is replaced by the exact CI-green commit at execution and recorded in the receipt",
    }
    _write(FINGERPRINT_PATH, fingerprint)
    return {"case_selection": CASE_SELECTION_PATH, "budget": BUDGET_PATH, "manifest": MANIFEST_PATH, "fingerprint": FINGERPRINT_PATH}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-root", required=True)
    parser.add_argument("--sample-size", type=int, default=12)
    args = parser.parse_args()
    written = build(Path(args.private_root).resolve(), args.sample_size)
    for name, path in written.items():
        print(f"{name}: {path.relative_to(ROOT).as_posix()} sha256={hashlib.sha256(path.read_bytes()).hexdigest()[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
