"""Static Study 1 provider-call bounds, derived from the protected call-site inventory.

Every constant below is computed by summing ``CALL_SITES``, a machine-readable
inventory of the ten ``client.call`` sites in the protected
``VEGO-AI/framework/orchestrator.py`` (content SHA-256
``fca4b885ee07381db0f02e558b1aebf25bdc7c27da1c471fd3103d7e0e2d5b88``),
expressed as accounting rows keyed by the invoking control-flow position.  The
module refuses to import if the summed inventory disagrees with the published
formulas ("4 + 3N" minimum, "82 + 61N" worst case), so the constants cannot
silently drift from the evidence.

Accounting convention: the two shared answer helpers
(``_answer_lang_questions`` -> orchestrator.py:87,
``_answer_dom_questions`` -> orchestrator.py:110) each make exactly one
``client.call`` per invocation, so their multiplicity is attributed to the loop
that invokes them; each row's ``evidence`` cites both the invoking branch and
the underlying call site.

``FORBIDDEN_LEGACY_FORMULA`` records the arithmetically wrong statement that
earlier documentation carried ("22 + 61N = 326"; 22 + 61*4 = 266, not 326).
Tests scan the active documents for it so it cannot be reintroduced.

No provider is accessed.  Token counts and monetary cost are TO BE MEASURED.
"""

from __future__ import annotations

import hashlib
import inspect
import re
from pathlib import Path

MAX_QA_ROUNDS = 10  # VEGO-AI/framework/orchestrator.py:36

ORCHESTRATOR_PATH = "VEGO-AI/framework/orchestrator.py"
ORCHESTRATOR_SHA256 = "fca4b885ee07381db0f02e558b1aebf25bdc7c27da1c471fd3103d7e0e2d5b88"


def verify_source(path: Path | None = None) -> None:
    source = path or Path(__file__).resolve().parents[1] / ORCHESTRATOR_PATH
    if hashlib.sha256(source.read_bytes()).hexdigest() != ORCHESTRATOR_SHA256:
        raise ValueError("protected orchestrator changed; call inventory is invalid")


verify_source()
FORBIDDEN_LEGACY_FORMULA = "22 + 61N"

CALL_SITES: tuple[dict[str, object], ...] = (
    {
        "row": "P1_TEMPLATE",
        "phase": "phase1",
        "scope": "fixed",
        "label": "agent1/build_language_template",
        "conditional": False,
        "min_calls": 1,
        "max_calls": 1,
        "evidence": "orchestrator.py:59",
    },
    {
        "row": "P2_GUIDELINES_PRODUCER",
        "phase": "phase2",
        "scope": "fixed",
        "label": "agent2/guidelines_round{n}",
        "conditional": False,
        "min_calls": 1,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "loop orchestrator.py:135; call :149; break :158-160",
    },
    {
        "row": "P2_LANG_ANSWERS",
        "phase": "phase2",
        "scope": "fixed",
        "label": "agent1/answer_language_questions",
        "conditional": True,
        "min_calls": 0,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "branch orchestrator.py:162; call :87",
    },
    {
        "row": "P2_DOM_ANSWERS",
        "phase": "phase2",
        "scope": "fixed",
        "label": "agent2/answer_domain_questions",
        "conditional": True,
        "min_calls": 0,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "branch orchestrator.py:165; call :110",
    },
    {
        "row": "P4_IDENTIFY",
        "phase": "phase4",
        "scope": "fixed",
        "label": "agent4/identify_patterns",
        "conditional": False,
        "min_calls": 1,
        "max_calls": 1,
        "evidence": "orchestrator.py:356",
    },
    {
        "row": "P4_CLASSIFY_PRODUCER",
        "phase": "phase4",
        "scope": "fixed",
        "label": "agent4/classify_r{n}",
        "conditional": False,
        "min_calls": 1,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "loop orchestrator.py:362; call :372; break :377-378",
    },
    {
        "row": "P4_CLASSIFY_LANG_ANSWERS",
        "phase": "phase4",
        "scope": "fixed",
        "label": "agent1/answer_language_questions",
        "conditional": True,
        "min_calls": 0,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "branch orchestrator.py:380; call :87",
    },
    {
        "row": "P4_CLASSIFY_DOM_ANSWERS",
        "phase": "phase4",
        "scope": "fixed",
        "label": "agent2/answer_domain_questions",
        "conditional": True,
        "min_calls": 0,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "branch orchestrator.py:382; call :110",
    },
    {
        "row": "P4_FEEDBACK_PRODUCER",
        "phase": "phase4_feedback",
        "scope": "fixed",
        "label": "agent2/guidelines_feedback_r{n}",
        "conditional": True,
        "min_calls": 0,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "gate orchestrator.py:395 (if flagged); loop :408; call :419",
    },
    {
        "row": "P4_FEEDBACK_LANG_ANSWERS",
        "phase": "phase4_feedback",
        "scope": "fixed",
        "label": "agent1/answer_language_questions",
        "conditional": True,
        "min_calls": 0,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "branch orchestrator.py:425 (only q_lang); call :87 via :428",
    },
    {
        "row": "P3_MAP",
        "phase": "phase3",
        "scope": "per_case",
        "label": "agent3/{case}/map",
        "conditional": False,
        "min_calls": 1,
        "max_calls": 1,
        "evidence": "orchestrator.py:210",
    },
    {
        "row": "P3_RESOLVE_PRODUCER",
        "phase": "phase3",
        "scope": "per_case",
        "label": "agent3/{case}/resolve_r{n}",
        "conditional": False,
        "min_calls": 1,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "loop orchestrator.py:213; call :225; break :230",
    },
    {
        "row": "P3_RESOLVE_LANG_ANSWERS",
        "phase": "phase3",
        "scope": "per_case",
        "label": "agent1/answer_language_questions",
        "conditional": True,
        "min_calls": 0,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "branch orchestrator.py:234; call :87",
    },
    {
        "row": "P3_RESOLVE_DOM_ANSWERS",
        "phase": "phase3",
        "scope": "per_case",
        "label": "agent2/answer_domain_questions",
        "conditional": True,
        "min_calls": 0,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "branch orchestrator.py:237; call :110",
    },
    {
        "row": "P3_AUDIT_PRODUCER",
        "phase": "phase3",
        "scope": "per_case",
        "label": "agent3/{case}/audit_r{n}",
        "conditional": False,
        "min_calls": 1,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "loop orchestrator.py:246; call :258; break :263",
    },
    {
        "row": "P3_AUDIT_LANG_ANSWERS",
        "phase": "phase3",
        "scope": "per_case",
        "label": "agent1/answer_language_questions",
        "conditional": True,
        "min_calls": 0,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "branch orchestrator.py:266; call :87",
    },
    {
        "row": "P3_AUDIT_DOM_ANSWERS",
        "phase": "phase3",
        "scope": "per_case",
        "label": "agent2/answer_domain_questions",
        "conditional": True,
        "min_calls": 0,
        "max_calls": MAX_QA_ROUNDS,
        "evidence": "branch orchestrator.py:268; call :110",
    },
)


def _sum(scope: str, key: str) -> int:
    return sum(int(site[key]) for site in CALL_SITES if site["scope"] == scope)


MIN_BASE = _sum("fixed", "min_calls")
MIN_PER_CASE = _sum("per_case", "min_calls")
WORST_BASE = _sum("fixed", "max_calls")
WORST_PER_CASE = _sum("per_case", "max_calls")
QA_DEPENDENT_WORST_CASE = WORST_BASE - MIN_BASE

if (MIN_BASE, MIN_PER_CASE, WORST_BASE, WORST_PER_CASE) != (4, 3, 82, 61):
    raise AssertionError(
        "call-site inventory no longer sums to the published bounds: "
        f"min {MIN_BASE}+{MIN_PER_CASE}N, worst {WORST_BASE}+{WORST_PER_CASE}N"
    )


def _require_case_count(case_count: int) -> int:
    if isinstance(case_count, bool) or not isinstance(case_count, int):
        raise ValueError("case_count must be an integer")
    if case_count < 0:
        raise ValueError("case_count must be non-negative")
    return case_count


def minimum_calls(case_count: int) -> int:
    verify_source()
    return MIN_BASE + MIN_PER_CASE * _require_case_count(case_count)


def worst_case_calls(case_count: int) -> int:
    verify_source()
    return WORST_BASE + WORST_PER_CASE * _require_case_count(case_count)


def capture_call_inventory(label: str) -> dict:
    """Bind the awaited protected frame/branch to its frozen accounting row.

    Read only code position and case_id, never arbitrary frame locals or data.
    Shared answer labels alone cannot distinguish their invoking loop.
    """
    source = (Path(__file__).resolve().parents[1] / ORCHESTRATOR_PATH).resolve()
    frame = inspect.currentframe()
    frames = []
    try:
        while frame:
            if Path(frame.f_code.co_filename).resolve() == source:
                frames.append((frame.f_lineno, frame.f_locals.get("case_id")))
            frame = frame.f_back
    finally:
        del frame
    sites = {
        59: "P1_TEMPLATE",
        149: "P2_GUIDELINES_PRODUCER",
        210: "P3_MAP",
        225: "P3_RESOLVE_PRODUCER",
        258: "P3_AUDIT_PRODUCER",
        356: "P4_IDENTIFY",
        372: "P4_CLASSIFY_PRODUCER",
        419: "P4_FEEDBACK_PRODUCER",
    }
    answer_branches = {
        164: "P2_LANG_ANSWERS",
        167: "P2_DOM_ANSWERS",
        236: "P3_RESOLVE_LANG_ANSWERS",
        239: "P3_RESOLVE_DOM_ANSWERS",
        267: "P3_AUDIT_LANG_ANSWERS",
        269: "P3_AUDIT_DOM_ANSWERS",
        381: "P4_CLASSIFY_LANG_ANSWERS",
        383: "P4_CLASSIFY_DOM_ANSWERS",
        428: "P4_FEEDBACK_LANG_ANSWERS",
    }
    if not frames:
        raise ValueError("call is not on protected orchestrator path")
    line, case = frames[0]
    if line in (87, 110):
        if len(frames) < 2:
            raise ValueError("answer caller missing")
        row = answer_branches.get(frames[1][0])
        case = frames[1][1]
    else:
        row = sites.get(line)
    site = next((s for s in CALL_SITES if s["row"] == row), None)
    if site is None:
        raise ValueError("unmapped protected call branch")
    result = {"label": label, "inventory_row": row, "phase": site["phase"], "case_id": case}
    validate_call_inventory([result])
    return {k: v for k, v in result.items() if k != "label"}


def validate_call_inventory(calls: list[dict]) -> None:
    for call in calls:
        site = next((s for s in CALL_SITES if s["row"] == call.get("inventory_row")), None)
        if site is None or call.get("phase") != site["phase"]:
            raise ValueError("unknown call inventory row/phase")
        pattern = re.escape(str(site["label"])).replace(r"\{n\}", r"(?:[1-9]|10)")
        pattern = pattern.replace(r"\{case\}", re.escape(str(call.get("case_id"))))
        if not re.fullmatch(pattern, call.get("label", "")):
            raise ValueError("call label differs from frozen inventory")
        if site["scope"] == "per_case" and call.get("case_id") is None:
            raise ValueError("per-case call lacks case identity")


def call_bound_breakdown(case_count: int) -> dict[str, object]:
    """Return the control-flow accounting used by the offline authorization gate."""
    _require_case_count(case_count)
    return {
        "case_count": case_count,
        "max_qa_rounds": MAX_QA_ROUNDS,
        "call_site_count": len(CALL_SITES),
        "fixed_calls": MIN_BASE,
        "per_case_calls": MIN_PER_CASE * case_count,
        "qa_dependent_minimum": 0,
        "qa_dependent_worst_case": QA_DEPENDENT_WORST_CASE,
        "maximum_calls_per_round": {
            "phase2": 3,
            "phase3_each_skill": 3,
            "phase4_classify": 3,
            "phase4_feedback": 2,
        },
        "minimum_formula": f"{MIN_BASE} + {MIN_PER_CASE}N",
        "worst_case_formula": f"{WORST_BASE} + {WORST_PER_CASE}N",
        "minimum_calls": minimum_calls(case_count),
        "worst_case_calls": worst_case_calls(case_count),
        "discrepancy_resolution": (
            "6 + 3N counted optional Phase 2/4 Q&A answers as mandatory; 4 + 3N is the direct "
            "no-question path. 22 + 61N was arithmetically wrong (22 + 61*4 = 266, not 326); the "
            "verified fixed worst case is 82."
        ),
        "orchestrator_sha256": ORCHESTRATOR_SHA256,
    }


def fake_client_call_counter(case_count: int, qa_dependent_calls: int = 0) -> dict[str, int]:
    """Count deterministic baseline calls without constructing provider clients."""
    _require_case_count(case_count)
    if (
        isinstance(qa_dependent_calls, bool)
        or not isinstance(qa_dependent_calls, int)
        or qa_dependent_calls < 0
    ):
        raise ValueError("qa_dependent_calls must be a non-negative integer")
    per_case = MIN_PER_CASE * case_count
    return {
        "fixed_calls": MIN_BASE,
        "per_case_calls": per_case,
        "qa_dependent_calls": qa_dependent_calls,
        "total_calls": MIN_BASE + per_case + qa_dependent_calls,
    }
