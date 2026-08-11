#!/usr/bin/env python3
"""Generate a professional 'Folder Overview' document for each working-Drive folder."""
import os
import subprocess
import sys

S = sys.argv[1]
sys.path.insert(0, os.path.join(S, "aug12-deliverables"))
from doc_catalog import CATALOG  # noqa: E402

FOLDER_INFO = {
    "00_Admin_and_Decisions": (
        "Administration and Decisions",
        "Decision and change log, the 44-control master register, RACI and RAID, the claim register, and the university-process material.",
        [
            "The ten supervisor decisions requested for 12 August (D-RQ-01 to D-RQ-10) are all still **Pending**. None has a logged outcome.",
            "Requirement acceptance across the 44-control register stands at **0 of 19** requirements formally accepted.",
            "The university-process inquiry is **drafted but not sent** - it needs a named recipient, the programme details, and an explicit send-approval.",
            "The Requirements and Progress Tracking workbook in this folder is the single tracking document requested on 5 August (action A08-06).",
        ],
    ),
    "01_Research_Questions": (
        "Research Questions",
        "The umbrella research question, SQ1 to SQ3, their mapping to three studies, and the crosswalk from the retired multi-question set.",
        [
            "The wording in these documents reflects the live edits from the 5 August working call. It is a **reconstruction** and remains **provisional** pending D-RQ-01 (umbrella) and D-RQ-02 (SQ1 to SQ3) sign-off.",
            "Do not treat any wording here as approved or final.",
            "The artifact-per-question notes are **thinking notes only** - formal artifact design is deliberately deferred per the 5 August instruction.",
        ],
    ),
    "02_PhD_Proposal": (
        "PhD Proposal",
        "Proposal versions plus the written Chapter 3 (Gap and Research Questions) and the bilingual executive brief.",
        [
            "Chapter 3 is **drafted in full** and incorporates every correction recorded from the 5 August call.",
            "Proposal v0.2 is a **controlled delta** over v0.1, not yet integrated into a single supervisor-facing document; its own release checklist is unmet.",
            "No section claims an accuracy, generalization, effort-reduction, or clinical result.",
            "Dates in the execution plan are **internal working targets**, not confirmed university deadlines.",
        ],
    ),
    "03_Literature_Review": (
        "Literature Review",
        "The native Google Sheet workbook (the workbook of record), the per-question coverage-gap analysis, the review protocol, and the frozen search register.",
        [
            "Searches QL-01 through QL-05 are **protocol ready / NOT RUN** - deliberately unexecuted per the 5 August instruction to think about the survey without executing it.",
            "Coverage today is honestly uneven: **RQ1 thin, RQ2 tool-heavy and research-light, RQ3 currently empty**.",
            "No novelty, coverage-completeness, or review-completeness claim is supported by anything in this folder.",
        ],
    ),
    "04_SE_Modeling_Studies": (
        "Software and Modeling Studies",
        "Software and modeling study material and aggregate evidence: baseline characterization, evaluation report, the EXP-005 expert-labeling protocol, benchmark analytics, and the experiment registers.",
        [
            "Evidence here is **mechanism and architecture readiness only**.",
            "EXP-005 stands at **0 supplied expert labels out of 24 generalization-safe candidate rows**, against a required minimum of 20 - so no accuracy, generalization, or effort-reduction figure is computable yet.",
            "Synthetic outputs and same-pattern rows are screening and mechanism-validation material, never accuracy evidence.",
        ],
    ),
    "05_Medical_Feasibility_Gated": (
        "Medical Feasibility (Gated)",
        "Non-sensitive feasibility governance only: the readiness scorecard, the MediVARIA medical-extension overview, the metadata-only MIMIC audit, the Clalit request template, the data-boundary rules, and the derived-artifact provenance template.",
        [
            "**Hard boundary.** This folder must never contain patient rows, MIMIC or Clalit extracts, clinical derivatives, or credentials. The supplied MIMIC source folder is linked from the workspace manifest, never copied here.",
            "Medical readiness is **0 of 6 mandatory entry gates** (use-case, people, authorization, ethics and privacy, environment, protocol) - all open.",
            "No row-level work, bounded pilot, export, or medical claim of any kind is authorized.",
            "A **26 August** internal control date decides whether the non-medical Plan B becomes the committed route.",
        ],
    ),
    "06_Weekly_Meetings": (
        "Weekly Meetings",
        "Meeting records, execution plans, step tracking, and the weekly pre-read template. The 2026-08-12 Supervisor Package subfolder holds the numbered, supervisor-facing set for that meeting.",
        [
            "The Wednesday 09:00 series is confirmed, but **no full weekly cycle** has yet produced pre-read to decision to propagated-delta minutes.",
            "The 2026-08-05 record is a **machine transcript with inferred (undiarized) speakers** - not human-reviewed, and not quotable as verbatim.",
            "Human review of the 1,195 transcript segments stands at **0 reviewed**; dual bilingual review and adjudication have not started.",
        ],
    ),
    "07_Submission_Package": (
        "Submission Package",
        "This folder is intentionally empty.",
        [
            "Per the workspace manifest, this folder holds **approved submission candidates only**.",
            "Nothing has been approved for submission, and **no official submission deadline has been confirmed** by Graduate Studies - the September and October dates in the plan are internal working targets.",
            "This folder stays empty until a candidate is complete, that exact package is explicitly approved, and the authorized submission route and receipt requirements are confirmed in writing.",
        ],
    ),
    "99_Archive": (
        "Archive",
        "Superseded reviewed working material. Currently empty by design.",
        [
            "Nothing has yet been both **superseded and reviewed**.",
            "Earlier supervisor packages (1, 15 and 21 July) remain live historical records in the project repository rather than archived material.",
            "The retired multi-question research-question set is preserved inside the legacy crosswalk in 01_Research_Questions rather than moved here.",
        ],
    ),
}

OUT = os.path.join(S, "prodocs")
BUILDER = os.path.join(S, "aug12-deliverables", "build_pro_docx.py")
PY = r".venv\Scripts\python.exe"
TMP = os.path.join(S, "_ov.md")

by_folder: dict[str, list[tuple[str, str, str]]] = {}
for src, folder, base, title, status in CATALOG:
    by_folder.setdefault(folder, []).append((base, title, status))

built = 0
for folder, (nice, purpose, points) in FOLDER_INFO.items():
    lines = [f"# {nice}", "", purpose, "", "## Current state", ""]
    lines += [f"- {p}" for p in points]
    docs = by_folder.get(folder, [])
    if docs:
        lines += ["", "## Documents in this folder", "", "| Document | Status |", "| --- | --- |"]
        for base, _title, status in sorted(docs):
            lines.append(f"| {base} | {status} |")
    lines += [
        "", "---", "",
        "*Every document in this folder is provided in both Word and PDF. The Markdown sources of "
        "record live in the project repository. Status lines are quoted from the tracked records; "
        "no status is upgraded or inferred here.*",
    ]
    with open(TMP, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    dest_dir = os.path.join(OUT, folder)
    os.makedirs(dest_dir, exist_ok=True)
    dst = os.path.join(dest_dir, "00 - Folder Overview.docx")
    res = subprocess.run(
        [PY, BUILDER, TMP, dst, f"{folder[:2]} - {nice}",
         "Folder overview - VEGO-AI PhD working Drive. Working material; not supervisor-approved."],
        capture_output=True, text=True,
    )
    if res.returncode == 0 and os.path.isfile(dst):
        built += 1
    else:
        print("FAIL", folder, res.stderr.strip()[:200])

if os.path.isfile(TMP):
    os.remove(TMP)
print(f"folder overviews built: {built}")
