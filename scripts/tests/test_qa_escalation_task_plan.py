from pathlib import Path

from build_qa_escalation_task_plan import TASKS


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/research/phd-proposal/2026-09-03-qa-escalation-task-plan.he.md"


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
