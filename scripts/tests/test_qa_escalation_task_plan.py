import json
import re
from pathlib import Path

from build_qa_escalation_task_plan import TASKS
from qa_task_plan_data import PLAN, SUMMARY_TABLE, TASKS as CANONICAL_TASKS
from qa_task_plan_send_gate import scan_patterns, strip_bidi_controls


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/research/phd-proposal/2026-09-03-qa-escalation-task-plan.he.md"
CANONICAL = ROOT / "scripts/data/qa_task_plan.json"

FIELDS = (
    "מטרה",
    "מה אני אבצע",
    "המקור לזיהוי האוטומטי",
    "ה-Dataset",
    "הפלט",
    "קריטריון השלמה",
    "מה נדרש ממני",
    "מה נדרש מאיריס וארנון",
    "מה חסר / מאתגר",
    "תלויות",
    "הערכת זמן",
)


def test_operational_plan_has_eight_filled_tasks_and_required_fields():
    text = SOURCE.read_text(encoding="utf-8")
    assert len(TASKS) == 8
    assert TASKS[0][0] == "איתור ושחזור לוג האינטראקציות מההרצה המקורית"
    assert "הרצה מבוקרת של setting אחד" in text
    for label in (
        "מטרה",
        "מה אני אבצע",
        "המקור לזיהוי האוטומטי",
        "ה-Dataset",
        "הפלט",
        "קריטריון השלמה",
        "מה נדרש ממני",
        "מה נדרש מאיריס וארנון",
        "מה חסר / מאתגר",
        "תלויות",
        "הערכת זמן",
    ):
        assert text.count(f"**{label}:**") == 8


def test_plan_uses_correct_evidence_boundary_and_defers_manual_validation():
    text = SOURCE.read_text(encoding="utf-8")
    assert "ANSWER_NOT_PERSISTED" in text
    assert "לא נמצאה תשובת Q&A תואמת שנשמרה" in text
    assert "לא ניתן לקבוע באופן אמפירי בשלב זה אילו מהן True/False" in text
    assert "ללא תיוג או בדיקה ידנית" in text
    assert "true/false validation" in text
    assert "main מסונכרן" in text


def test_canonical_json_is_the_structured_source():
    assert CANONICAL.exists()
    data = json.loads(CANONICAL.read_text(encoding="utf-8"))
    assert set(data) >= {
        "metadata",
        "opening",
        "evidence_boundary",
        "interaction_log_guard",
        "tasks",
        "summary_table",
        "effort",
        "supervisor_requests",
    }
    assert len(data["tasks"]) == 8
    assert len(data["summary_table"]) == 8
    assert data["tasks"][0]["name"] == "איתור ושחזור לוג האינטראקציות מההרצה המקורית"
    assert data["tasks"][0]["priority"] == "P0"
    assert data["effort"]["ali"] == "כ-14–23 שעות לכל שמונה המשימות."


def _markdown_task_blocks(text):
    blocks = re.findall(r"### משימה (\d+) — (.+?) \*\*\[(.+?)\]\*\*(.*?)(?=\n### משימה |\n## גבול טענה)", text, flags=re.S)
    parsed = []
    for number, name, priority, body in blocks:
        fields = {}
        for field in FIELDS:
            match = re.search(rf"\*\*{re.escape(field)}:\*\* (.*?)(?=\n\n\*\*|\Z)", body, flags=re.S)
            assert match, f"missing field {field} in task {number}"
            fields[field] = match.group(1).strip()
        parsed.append({"number": int(number), "name": name.strip(), "priority": priority.strip(), "fields": fields})
    return parsed


def test_generated_markdown_matches_every_canonical_task_field():
    text = SOURCE.read_text(encoding="utf-8")
    markdown_tasks = _markdown_task_blocks(text)
    assert len(markdown_tasks) == len(CANONICAL_TASKS) == 8
    for actual, expected in zip(markdown_tasks, PLAN["tasks"]):
        assert actual["name"] == expected["name"]
        assert actual["priority"] == expected["priority"]
        assert actual["fields"] == expected["fields"]


def test_markdown_summary_table_matches_canonical_summary_rows():
    text = SOURCE.read_text(encoding="utf-8")
    table_lines = [line for line in text.splitlines() if line.startswith("| ") and line.endswith(" |")]
    body_rows = table_lines[1:]
    assert len(body_rows) == len(SUMMARY_TABLE) == 8
    for line, expected in zip(body_rows, SUMMARY_TABLE):
        actual = [cell.strip() for cell in line.strip("|").split("|")]
        assert actual == expected


def test_pdf_summary_uses_canonical_rows_without_literal_duplicate_data():
    pdf_builder = (ROOT / "scripts/build_qa_escalation_task_plan_pdf.py").read_text(encoding="utf-8")
    assert "headers = SUMMARY_HEADERS" in pdf_builder
    assert "rows = SUMMARY_TABLE" in pdf_builder
    assert "rows = [" not in pdf_builder


def test_docx_builder_has_no_second_task_list_literal():
    docx_builder = (ROOT / "scripts/build_qa_escalation_task_plan.py").read_text(encoding="utf-8")
    assert "from qa_task_plan_data import PLAN, SUMMARY_HEADERS, SUMMARY_TABLE, TASKS" in docx_builder
    assert "TASKS = [" not in docx_builder


def test_bidi_scanner_normalizes_controls_before_matching():
    text = "A\u200fN\u200bS\u202aWER_NOT_PERSISTED\u202c"
    result = scan_patterns(text, ["ANSWER_NOT_PERSISTED", "missing-pattern"])
    assert result["ANSWER_NOT_PERSISTED"]["found"] is True
    assert result["missing-pattern"]["found"] is False
    assert strip_bidi_controls(text) == "ANSWER_NOT_PERSISTED"


def test_interaction_log_semantic_guard_is_preserved():
    guard = PLAN["interaction_log_guard"]
    assert "only calls that actually occurred" in guard
    assert "metadata_only" in guard
    assert "full-content" in guard
    assert "cannot reconstruct Q&A advisor answers that were never generated" in guard
