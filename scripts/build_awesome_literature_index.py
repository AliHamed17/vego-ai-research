"""Generate literature/README.md as a curated, awesome-list-style index.

Format modelled on github.com/HenryPengZou/Awesome-Human-Agent-Collaboration-
Interaction-Systems (shared by Iris in the 2026-08-12 supervisor call chat, in
response to Ali sharing Zou et al. 2026's ACL Findings survey of the same
space) - dated, venue-tagged entries grouped by topic, plus a dedicated
taxonomy section.

Generated from literature/verified-research-corpus-2026-08-12.json so the
index can never drift from the underlying, individually-verified data. Do not
hand-edit literature/README.md; edit the corpus JSON and rerun this script.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(r"C:\Users\ahamed\vego-ai")
CORPUS = REPO / "literature" / "verified-research-corpus-2026-08-12.json"
OUT = REPO / "literature" / "README.md"

SECTIONS = [
    ("foundation", "Foundation", "VEGO-AI itself, and the surveys that frame the space it sits in."),
    ("RQ1", "SQ1 \u00b7 Selective Intervention",
     "When and how an agentic assessment system should request human judgment."),
    ("RQ2", "SQ2 \u00b7 Governed Knowledge Reuse",
     "Representing, validating, reconciling and storing expert judgment."),
    ("RQ3", "SQ3 \u00b7 Evaluation and Transfer",
     "Evaluating human-AI assessment and transferring judgment across contexts."),
    ("methodology", "Design-Science Methodology", "How the research itself is built and evaluated."),
    ("general", "General", "Cross-cutting or not yet assigned to a single question."),
]

BADGE = {
    "VERIFIED_ONLINE": "\u2705",
    "PARTIALLY_VERIFIED": "\u26a0\ufe0f",
    "COULD_NOT_VERIFY": "\u274c",
}


def link_or_plain(title: str, url: str) -> str:
    if not url:
        return title
    first = re.split(r"\s*[;,]\s*", url.strip())[0]
    if first.startswith("http"):
        return f"[{title}]({first})"
    return title


def year_key(s: dict) -> tuple:
    m = re.search(r"\d{4}", s.get("year", "") or "")
    return (-int(m.group()) if m else 0, s.get("title", ""))


def build():
    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    sources = data["sources"]
    by_tag = defaultdict(list)
    for s in sources:
        by_tag[s.get("rq_tag", "general")].append(s)

    lines = []
    lines.append("# VEGO-AI Human-Judgment Literature")
    lines.append("")
    lines.append(
        "A curated, individually-verified reading list for the thesis question "
        "*\"How can human judgment be captured, governed, and used to support "
        "agentic-AI-driven variability exploration in guideline operationalization "
        "scenarios, enabling reliable human\u2013AI co-reasoning?\"*"
    )
    lines.append("")
    lines.append(
        "Format inspired by "
        "[Awesome-Human-Agent-Collaboration-Interaction-Systems](https://github.com/HenryPengZou/Awesome-Human-Agent-Collaboration-Interaction-Systems), "
        "shared by Prof. Iris Reinhartz-Berger during the 2026-08-05 supervisor call, in reply to "
        "[Zou et al. 2026](https://aclanthology.org/2026.findings-acl.1811/), which Ali shared in the "
        "same chat. That survey is itself entry #1 below, tagged `foundation`."
    )
    lines.append("")
    lines.append(
        f"**Status:** {data['totalSources']} sources, individually checked against a publisher page, "
        f"DOI, dblp or arXiv record \u2014 {data['verified']} \u2705 verified online, "
        f"{data['partial']} \u26a0\ufe0f partially verified, {data['unverified']} \u274c could not be "
        "verified (quarantined below, never cited elsewhere). "
        "**The five frozen protocol searches (QL-01\u2013QL-05) have not been executed** \u2014 "
        "this index shows what has been found and read, never that nothing else exists."
    )
    lines.append("")

    lines.append("## Contents")
    lines.append("")
    for tag, title, _ in SECTIONS:
        n = len(by_tag.get(tag, []))
        anchor = title.lower().replace(" \u00b7 ", "-").replace(" ", "-")
        lines.append(f"- [{title}](#{anchor}) ({n})")
    lines.append("- [Taxonomy](#taxonomy)")
    lines.append("- [Needs checking](#needs-checking)")
    lines.append("- [Folder layout](#folder-layout)")
    lines.append("- [Contributing an entry](#contributing-an-entry)")
    lines.append("")

    for tag, title, desc in SECTIONS:
        entries = sorted(
            (s for s in by_tag.get(tag, []) if s["verification"] != "COULD_NOT_VERIFY"),
            key=year_key,
        )
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"*{desc}*")
        lines.append("")
        for s in entries:
            badge = BADGE.get(s["verification"], "")
            link = link_or_plain(s["title"], s.get("doi_or_url", ""))
            authors = s.get("authors", "")
            first_author = authors.split(",")[0].strip() if authors else ""
            et_al = " et al." if authors.count(",") >= 1 else ""
            note = s.get("what_it_establishes", "").split(". ")[0].strip()
            if note and not note.endswith((".", "!", "?")):
                note += "."
            lines.append(
                f"- {badge} **[{s.get('year', '?')}]** {link} \u2014 {first_author}{et_al}. {note}"
            )
        lines.append("")

    lines.append("## Taxonomy")
    lines.append("")
    lines.append(
        "Two taxonomies are in play, and this project uses both deliberately rather than treating "
        "one as a replacement for the other."
    )
    lines.append("")
    lines.append(
        "**The Judgment Lifecycle Grid** (this project, see the course-presentation classification "
        "framework) follows *one expert ruling* through five checkpoints: `TRIGGER \u2192 ASK \u2192 "
        "RECORD \u2192 REUSE \u2192 PROVE`. Each reviewed stream is coded F (sustained), P (partial) or "
        "A (not addressed) per checkpoint. The two weakest handoffs in the current corpus are "
        "`ASK \u2192 RECORD` and `RECORD \u2192 REUSE`."
    )
    lines.append("")
    lines.append(
        "**Zou et al. 2026's taxonomy** (the published, peer-reviewed reference point) classifies "
        "LLM-based human-agent systems along environment profiling, human-feedback mechanisms "
        "(type, granularity, phase), **interaction mode** (supervision, cooperation, coordination, "
        "delegation), orchestration strategy, and communication."
    )
    lines.append("")
    lines.append(
        "**Open reconciliation task:** the Judgment Lifecycle Grid's checkpoints and Zou et al.'s "
        "interaction modes describe overlapping ground from different angles and have not yet been "
        "cross-mapped. Doing so before the grid is presented as a novel contribution is one of the "
        "concrete next steps this index surfaces \u2014 not yet done, so no claim of novelty relative "
        "to the published taxonomy is made here."
    )
    lines.append("")

    lines.append("## Needs checking")
    lines.append("")
    needs = [s for s in sources if s["verification"] != "VERIFIED_ONLINE"]
    lines.append(
        "Entries below are `PARTIALLY_VERIFIED` or `COULD_NOT_VERIFY`. They are listed for "
        "transparency and are **not cited** anywhere else in this project until upgraded."
    )
    lines.append("")
    for s in sorted(needs, key=year_key):
        badge = BADGE.get(s["verification"], "")
        lines.append(
            f"- {badge} **[{s.get('year', '?')}]** {s['title']} \u2014 "
            f"{s.get('verification_note', '').strip()}"
        )
    lines.append("")

    lines.append("## Folder layout")
    lines.append("")
    lines.append("- `verified-research-corpus-2026-08-12.json` \u2014 the source of truth. "
                 "Edit this, then rerun `scripts/build_awesome_literature_index.py`; never "
                 "hand-edit this README.")
    lines.append("- `papers/` \u2014 PDFs or links, subject to copyright and sharing rules.")
    lines.append("- `notes/` \u2014 reading notes based on `docs/templates/reading-note.md`.")
    lines.append("- `bibliography.bib` \u2014 BibTeX entries.")
    lines.append("- `hitl-resource-pack/` \u2014 curated human-in-the-loop / human-AI "
                 "collaboration resources.")
    lines.append("- `per-rq-literature-map.md`, `researcher-relevance-2026-08-12.json` \u2014 "
                 "companion analyses over the same corpus.")
    lines.append("")
    lines.append("Do not publish copyrighted PDFs unless you have rights to do so.")
    lines.append("")

    lines.append("## Contributing an entry")
    lines.append("")
    lines.append(
        "1. Verify the source independently \u2014 publisher page, DOI, dblp or arXiv record. "
        "A generated citation is not a verified one."
    )
    lines.append(
        "2. Add a record to `verified-research-corpus-2026-08-12.json` with `verification` set "
        "honestly (`VERIFIED_ONLINE` only if you actually checked); tag it to the RQ it serves."
    )
    lines.append("3. Rerun `python scripts/build_awesome_literature_index.py` to regenerate this file.")
    lines.append(
        "4. If a source cannot be verified, it goes in the Needs Checking section and is never "
        "cited elsewhere \u2014 do not quietly drop the verification step under time pressure."
    )
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} ({len(sources)} sources, {sum(len(v) for v in by_tag.values())} tagged)")


if __name__ == "__main__":
    build()
