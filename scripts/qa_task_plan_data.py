"""Load the single canonical supervisor-facing task-plan source."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PATH = ROOT / "scripts" / "data" / "qa_task_plan.json"


def load_plan():
    with CANONICAL_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


PLAN = load_plan()
TASKS = [(task["name"], task["priority"], task["fields"]) for task in PLAN["tasks"]]
SUMMARY_HEADERS = PLAN["summary_headers"]
SUMMARY_TABLE = PLAN["summary_table"]
