"""Generate the canonical Hebrew task-plan Markdown from the structured JSON source."""

from pathlib import Path

from qa_task_plan_data import PLAN


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "research" / "phd-proposal" / "2026-09-03-qa-escalation-task-plan.he.md"


def build() -> Path:
    lines = [
        f"# {PLAN['metadata']['title']}",
        "",
        f"**נמען:** {PLAN['metadata']['recipient']}",
        f"**סטטוס:** {PLAN['metadata']['status']}",
        f"**בסיס פנימי:** {PLAN['metadata']['internal_basis']}",
        "",
        PLAN["opening"],
        "",
        "## תמונת מצב מאומתת",
        "",
        PLAN["evidence_boundary"],
        "",
        "| " + " | ".join(PLAN["summary_headers"]) + " |",
        "|---:|---|:---:|---|---|---|---|---:|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in PLAN["summary_table"])
    lines.extend(["", "## פירוט המשימות", ""])
    for number, task in enumerate(PLAN["tasks"], 1):
        lines.extend([f"### משימה {number} — {task['name']} **[{task['priority']}]**", ""])
        for label, value in task["fields"].items():
            lines.extend([f"**{label}:** {value}", ""])
    lines.extend([
        "## גבול טענה ושלב עתידי",
        "",
        PLAN["claim_boundary"],
        "",
        "## סיכום זמן",
        "",
        f"**זמן עבודה שלי:** {PLAN['effort']['ali']}",
        f"**זמן ריצה/API:** {PLAN['effort']['machine_api']}",
        f"**זמן חסום/המתנה:** {PLAN['effort']['blocked']}",
        f"**שלב עתידי שאינו כלול:** {PLAN['effort']['future_excluded']}",
        "## מה נדרש מאיריס וארנון",
        "",
    ])
    lines.extend(f"{index}. {request}" for index, request in enumerate(PLAN["supervisor_requests"], 1))
    lines.extend(["", "אין בקשה לתייג, לקרוא שורות, לבדוק alerts, לבצע adjudication או לאשר כעת את כללי Detector v1."])
    OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return OUT


if __name__ == "__main__":
    print(build())
