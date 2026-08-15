#!/usr/bin/env python3
"""Render the §2/§4 think-only options note (deliverable A08-04) to Markdown.

Iris's instruction was to THINK about sections 2 (literature survey) and 4
(research artifact per RQ) but NOT to start them. This renders options and
trade-offs only: no committed design, no executed search, no chosen artifact.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HEADER = """# Sections 2 and 4 — Thinking Notes (options only, nothing started)

> **Status: THINK-ONLY. Deliverable `A08-04` from the 2026-08-05 call.**
>
> Iris's instruction was explicit: *think about* sections 2 (literature survey) and 4 (research
> artifact per research question), but **do not start them**. This note therefore contains
> **options with trade-offs and open questions** — no committed chapter design, no chosen artifact,
> and no executed literature search.
>
> **Boundary facts carried into every option below.** The searches `QL-01`–`QL-05` are
> protocol-ready and **not run**, so no option may assert review completeness or novelty. EXP-005
> holds **0 of 24** required independent generalization-safe expert labels, and **0 of 6** medical
> entry gates pass, so no option may assume accuracy, generalization, clinical-performance or
> effort-reduction evidence. The RQ/SQ wording is **provisional** pending `A08-01` verification and
> logged `D-RQ-01`/`D-RQ-02` decisions — which is itself a live design constraint on §2's structure.

---

## Part 1 — §2 Literature survey: four structural options

Four genuinely different ways to organise the chapter. **None of these is a recommendation.** The
choice interacts with the wording sign-off: options that hard-code sub-question wording into headings
become expensive if the wording changes on Aug 12.

"""

S4_HEADER = """
---

## Part 2 — §4 Research artifact per research question: options

For each sub-question, the option the three-study contract already names ("contract-anchored") plus
genuine alternatives at different abstraction levels. Listed to expose the **granularity and
abstraction decisions** that have not yet been made — not to select one.

A recurring issue visible across all three: the contract's current "Core artifact" rows bundle many
components into one artifact (six for SQ1, nine for SQ2, ten for SQ3), and several of the SQ3 items
are *outputs of running the study* rather than the artifact itself. Whether a study may have a
**package** or must have exactly **one named artifact** is an open question for the supervisors.

"""

QUESTIONS_HEADER = """
---

## Part 3 — Open questions for Iris and Arnon (Aug 12)

These are the decisions that must be made before §2 or §4 can legitimately start. They are grouped so
they can be worked through quickly in the meeting.

"""

FOOTER = """
---

## What is deliberately NOT in this note

- No chapter outline committed for §2, and no section text drafted.
- No artifact selected for any study, and no component list frozen.
- No literature search executed; no screening, no inclusion decisions, no novelty statement.
- No evaluation design specified — that is Chapter 4 (methodology) and is out of scope for this pass.

*Prepared for the 2026-08-12 supervisor meeting. Options derive from the three-study contract, the
frozen search protocol, the existing taxonomy, and the offline experiment record; the boundary facts
above are unchanged by anything in this note.*
"""

QUESTION_GROUPS = [
    ("Chapter 2 shape and scope", ("Chapter 2 shape", "Sequencing", "Known holes", "RQ3 currently",
                                   "Does the design-science")),
    ("Artifact definition (§4)", ("Artifact granularity", "Abstraction level", "SQ2/SQ3 boundary")),
    ("Evidence admissibility", ("Admissible evidence", "Preliminary results", "Synthetic fixtures")),
    ("Scope, resourcing and permission", ("Plan A presence", "Study 3 resourcing", "Permission and timing")),
]


def render_s2(options: list[dict]) -> str:
    out = []
    for opt in options:
        out.append(f"### {opt.get('option_name','')}\n")
        out.append(f"**Structure.** {opt.get('structure','')}\n")
        out.append(f"**Pros.** {opt.get('pros','')}\n")
        out.append(f"**Cons.** {opt.get('cons','')}\n")
        out.append(f"**Fit to the three-question spine.** {opt.get('fit_verdict','')}\n")
        out.append("")
    return "\n".join(out)


def render_s4(options: list[dict]) -> str:
    out = []
    for sq in ("SQ1", "SQ2", "SQ3"):
        group = [o for o in options if str(o.get("sq", "")).strip().upper().startswith(sq)]
        if not group:
            continue
        titles = {
            "SQ1": "SQ1 — Selective intervention",
            "SQ2": "SQ2 — Governed knowledge reuse",
            "SQ3": "SQ3 — Evaluation and transfer",
        }
        out.append(f"### {titles[sq]}\n")
        out.append("| Option | What it would be | Evaluation shape | Risk | Hard dependency |")
        out.append("| --- | --- | --- | --- | --- |")
        for o in group:
            row = [
                f"**{o.get('artifact_option','')}**",
                o.get("what_it_would_be", ""),
                o.get("evaluation_shape", ""),
                o.get("risk", ""),
                o.get("dependency", ""),
            ]
            out.append("| " + " | ".join(c.replace("\n", " ").replace("|", "/") for c in row) + " |")
        out.append("")
    return "\n".join(out)


def render_questions(questions: list[str]) -> str:
    remaining = list(questions)
    out = []
    n = 0
    for group_name, prefixes in QUESTION_GROUPS:
        picked = [q for q in remaining if any(q.startswith(p) for p in prefixes)]
        if not picked:
            continue
        out.append(f"**{group_name}**\n")
        for q in picked:
            n += 1
            out.append(f"{n}. {q}")
            remaining.remove(q)
        out.append("")
    if remaining:
        out.append("**Other**\n")
        for q in remaining:
            n += 1
            out.append(f"{n}. {q}")
        out.append("")
    return "\n".join(out)


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Users\ahamed\AppData\Local\Temp\claude\think.json")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("docs/research/phd-proposal/sections-2-and-4-thinking-notes.md")
    data = json.loads(src.read_text(encoding="utf-8"))

    doc = (
        HEADER
        + render_s2(data.get("section2_options", []))
        + S4_HEADER
        + render_s4(data.get("section4_options", []))
        + QUESTIONS_HEADER
        + render_questions(data.get("open_questions_for_supervisors", []))
        + FOOTER
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(doc, encoding="utf-8")
    print(f"think-pass note: {len(data.get('section2_options',[]))} §2 options, "
          f"{len(data.get('section4_options',[]))} §4 options, "
          f"{len(data.get('open_questions_for_supervisors',[]))} questions -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
