"""Historical Study 1 call graph reference; never the isolated lane's live cap.

This module only parses the protected legacy source. It never imports or runs
the orchestrator. New execution must bind its own inventory and max_calls config.
"""

from __future__ import annotations

import ast
import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path

MAX_QA_ROUNDS = 10
MIN_BASE = 4
MIN_PER_CASE = 3
WORST_BASE = 82
WORST_PER_CASE = 61
REFERENCE_SCOPE = "LEGACY_STATIC_REFERENCE_NOT_EXECUTION_BUDGET"


@dataclass(frozen=True)
class CallSite:
    phase: str
    label: str
    per_case: bool
    minimum_visits: int
    maximum_visits: int


# Each Q&A answer is a single batched request per branch/round, not per question.
CALL_SITES = (
    CallSite("phase1", "agent1/build_language_template", False, 1, 1),
    CallSite("phase2", "agent2/guidelines_round{round_n}", False, 1, MAX_QA_ROUNDS),
    CallSite("phase2", "agent1/answer_language_questions", False, 0, MAX_QA_ROUNDS),
    CallSite("phase2", "agent2/answer_domain_questions", False, 0, MAX_QA_ROUNDS),
    CallSite("phase3", "agent3/{case_id}/map", True, 1, 1),
    CallSite("phase3", "agent3/{case_id}/resolve_r{round_n}", True, 1, MAX_QA_ROUNDS),
    CallSite("phase3", "agent1/answer_language_questions", True, 0, MAX_QA_ROUNDS),
    CallSite("phase3", "agent2/answer_domain_questions", True, 0, MAX_QA_ROUNDS),
    CallSite("phase3", "agent3/{case_id}/audit_r{round_n}", True, 1, MAX_QA_ROUNDS),
    CallSite("phase3", "agent1/answer_language_questions", True, 0, MAX_QA_ROUNDS),
    CallSite("phase3", "agent2/answer_domain_questions", True, 0, MAX_QA_ROUNDS),
    CallSite("phase4", "agent4/identify_patterns", False, 1, 1),
    CallSite("phase4", "agent4/classify_r{round_n}", False, 1, MAX_QA_ROUNDS),
    CallSite("phase4", "agent1/answer_language_questions", False, 0, MAX_QA_ROUNDS),
    CallSite("phase4", "agent2/answer_domain_questions", False, 0, MAX_QA_ROUNDS),
    CallSite("phase4", "agent2/guidelines_feedback_r{round_n}", False, 0, MAX_QA_ROUNDS),
    CallSite("phase4", "agent1/answer_language_questions", False, 0, MAX_QA_ROUNDS),
)
PROTECTED_FUNCTIONS = frozenset(
    {
        "phase1_build_language_template",
        "_answer_lang_questions",
        "_answer_dom_questions",
        "phase2_build_reference_guidelines",
        "_phase3_one_case",
        "phase3_evaluate_cases",
        "phase4_variability_analysis",
    }
)
PROTECTED_AST_SHA256 = "c785b77fe31e97ece79a484b43c3ad3f85a0d2e7a3c7d7bfb174a9260839a717"


def _count(value: int) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("count must be a non-negative integer")
    return value


def _phase_totals(case_count: int, field: str) -> dict[str, int]:
    _count(case_count)
    result = dict.fromkeys(("phase1", "phase2", "phase3", "phase4"), 0)
    for site in CALL_SITES:
        result[site.phase] += getattr(site, field) * (case_count if site.per_case else 1)
    return result


def verify_legacy_call_source(source_path: Path | None = None) -> bool:
    """Fail closed on missing labels or any protected AST structural drift.

    This deliberately conservative snapshot ignores formatting/comments only;
    updating it requires reviewing the historical graph, not running that graph.
    It is not evidence about the isolated pipeline or physical SDK retry counts.
    """
    path = source_path or Path(__file__).resolve().parents[1] / "VEGO-AI/framework/orchestrator.py"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        nodes = [
            node
            for node in tree.body
            if (isinstance(node, ast.AsyncFunctionDef) and node.name in PROTECTED_FUNCTIONS)
            or (
                isinstance(node, ast.Assign)
                and any(
                    isinstance(target, ast.Name) and target.id == "MAX_QA_ROUNDS"
                    for target in node.targets
                )
            )
        ]
        fingerprint = hashlib.sha256(
            ast.dump(ast.Module(body=nodes, type_ignores=[]), include_attributes=False).encode()
        ).hexdigest()
        labels = set()
        for node in ast.walk(ast.Module(body=nodes, type_ignores=[])):
            if not isinstance(node, ast.Call):
                continue
            for keyword in node.keywords:
                if keyword.arg != "label":
                    continue
                value = keyword.value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    labels.add(value.value)
                elif isinstance(value, ast.JoinedStr):
                    labels.add(
                        "".join(
                            part.value
                            if isinstance(part, ast.Constant)
                            else "{" + ast.unparse(part.value) + "}"
                            for part in value.values
                        )
                    )
        return fingerprint == PROTECTED_AST_SHA256 and {s.label for s in CALL_SITES} <= labels
    except (OSError, SyntaxError, UnicodeError, ValueError, TypeError):
        return False


def derive_call_bounds(case_count: int, *, source_path: Path | None = None) -> dict[str, object]:
    """Derive the named legacy reference only when its protected source matches."""
    low = _phase_totals(case_count, "minimum_visits")
    high = _phase_totals(case_count, "maximum_visits")
    verified = verify_legacy_call_source(source_path)
    return {
        "status": "PASS" if verified else "BLOCKED",
        "scope": REFERENCE_SCOPE,
        "case_count": case_count,
        "minimum_formula": "4 + 3N",
        "worst_case_formula": "82 + 61N",
        "minimum_calls": sum(low.values()) if verified else None,
        "worst_case_calls": sum(high.values()) if verified else None,
        "phase_minimum_calls": low if verified else None,
        "phase_worst_case_calls": high if verified else None,
        "call_sites": [asdict(site) for site in CALL_SITES],
        "external_provider_call_count": 0,
    }


def minimum_calls(case_count: int) -> int:
    """Historical arithmetic only; use derive_call_bounds for source verification."""
    return sum(_phase_totals(case_count, "minimum_visits").values())


def worst_case_calls(case_count: int) -> int:
    """Historical arithmetic only, excluding SDK retry multiplication."""
    return sum(_phase_totals(case_count, "maximum_visits").values())


def call_bound_breakdown(case_count: int) -> dict[str, object]:
    """Compatibility breakdown of the historical graph, not a live execution cap."""
    _count(case_count)
    return {
        "case_count": case_count,
        "scope": REFERENCE_SCOPE,
        "max_qa_rounds": MAX_QA_ROUNDS,
        "fixed_calls": MIN_BASE,
        "per_case_calls": MIN_PER_CASE * case_count,
        "qa_dependent_minimum": 0,
        "qa_dependent_worst_case": 78,
        "maximum_calls_per_round": {
            "phase2": 3,
            "phase3_each_skill": 3,
            "phase4_classify": 3,
            "phase4_feedback": 2,
        },
        "minimum_formula": "4 + 3N",
        "worst_case_formula": "82 + 61N",
        "minimum_calls": minimum_calls(case_count),
        "worst_case_calls": worst_case_calls(case_count),
        "discrepancy_resolution": "6 + 3N counts optional Phase 2/4 Q&A as mandatory; 4 + 3N is the direct no-question path.",
    }


def fake_client_call_counter(case_count: int, qa_dependent_calls: int = 0) -> dict[str, int]:
    """Count deterministic baseline calls without constructing provider clients."""
    _count(case_count)
    _count(qa_dependent_calls)
    per_case = MIN_PER_CASE * case_count
    return {
        "fixed_calls": MIN_BASE,
        "per_case_calls": per_case,
        "qa_dependent_calls": qa_dependent_calls,
        "total_calls": MIN_BASE + per_case + qa_dependent_calls,
    }
