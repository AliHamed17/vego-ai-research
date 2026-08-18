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

# Relative to this script's own location, not a hard-coded absolute path - this
# repo runs from multiple checkouts/worktrees on the same machine, and a fixed
# path silently writes into whichever one happens to sit at that location.
REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "literature" / "verified-research-corpus-2026-08-12.json"
OUT = REPO / "literature" / "README.md"
BIB_OUT = REPO / "literature" / "bibliography.bib"

# Curated by title match against the corpus (not every "dataset"-mentioning entry
# names an actual benchmark), so this stays traceable to a checkable source.
BENCHMARKS = [
    ("KnowNo",
     "Robots That Ask For Help: Uncertainty Alignment for Large Language Model Planners",
     "Conformal-prediction-calibrated help requests for an LLM robot planner",
     "SQ1 \u2014 the closest existing benchmark for a calibrated ask-for-help policy"),
    ("Noisy ToolBench",
     "Learning to Ask: When LLM Agents Meet Unclear Instruction",
     "Tool-use tasks with deliberately underspecified instructions, scored on both "
     "accuracy and interaction efficiency",
     "SQ1 \u2014 measures whether an agent asks instead of fabricating missing arguments"),
    ("WILDS",
     "WILDS: A Benchmark of in-the-Wild Distribution Shifts",
     "Real, naturally-occurring domain-generalization and subpopulation shifts across "
     "multiple application domains",
     "SQ3 \u2014 the reference design for a leakage-safe, real-shift transfer evaluation"),
    ("VEGO-AI evaluation setting (Cheers / ParkWise)",
     "Not All Differences Matter: Variability Exploration of Domain Models via Agentic AI",
     "2 domains \u00d7 2 UML languages, 178 case models, from a university modelling course",
     "This project's own baseline setting \u2014 see "
     "`docs/research/governance/vego-ai-foundation-paper-record.md` for the verified figures"),
]

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
    lines.append("- [Datasets & benchmarks](#datasets--benchmarks)")
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

    lines.append("## Datasets & Benchmarks")
    lines.append("")
    lines.append(
        "Named benchmarks actually introduced or used by a reviewed source — not every "
        "entry that mentions \"dataset\" proposes one. Compiled from the corpus, not invented."
    )
    lines.append("")
    lines.append("| Benchmark | Introduced / used by | What it covers | Relevance |")
    lines.append("| --- | --- | --- | --- |")
    by_title = {s["title"]: s for s in sources}
    for name, title, covers, rel in BENCHMARKS:
        src = by_title.get(title)
        link = link_or_plain(title, src.get("doi_or_url", "")) if src else title
        lines.append(f"| **{name}** | {link} | {covers} | {rel} |")
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
    lines.append("- `bibliography.bib` \u2014 generated alongside this file, same source of truth. "
                 "Do not hand-edit.")
    lines.append("- `hitl-resource-pack/` \u2014 a separate, smaller pack of *tools and "
                 "guideline documents* (Label Studio, Argilla, NIST AI RMF), not academic "
                 "papers. Not superseded by the corpus above; different purpose.")
    lines.append("- `per-rq-literature-map.md` \u2014 **historical**, superseded by this file "
                 "as the coverage snapshot (see the notice at its top); kept for the original "
                 "2026-08-05 requirement and reasoning.")
    lines.append("- `researcher-relevance-2026-08-12.json` \u2014 a people-level companion "
                 "analysis (82 researchers), distinct from the paper-level corpus above.")
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

    build_bibliography(sources)


def bib_key(s: dict, used: set) -> str:
    first = re.sub(r"[^A-Za-z]", "", (s.get("authors", "").split(",")[0] or "Anon").split()[-1] or "Anon")
    year = re.search(r"\d{4}", s.get("year", "") or "")
    base = f"{first}{year.group() if year else ''}"
    key, n = base, 1
    while key in used:
        n += 1
        key = f"{base}{chr(ord('a') + n - 2)}"
    used.add(key)
    return key


def bib_authors(authors: str) -> str:
    """'First Last, First Last' -> 'Last, First and Last, First' (BibTeX's
    expected author syntax) - the corpus stores comma-joined display names,
    which is not itself valid BibTeX and would misparse as one long name."""
    names = [n.strip() for n in authors.split(",") if n.strip()]
    out = []
    for n in names:
        if n.lower() in ("et al.", "et al"):
            out.append("others")
            continue
        parts = n.split()
        out.append(f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1 else n)
    return " and ".join(out)


def bib_entry(s: dict, key: str) -> str:
    doi_url = re.split(r"\s*[;,]\s*", s.get("doi_or_url", "").strip())[0]
    fields = {
        "author": bib_authors(s.get("authors", "")),
        "title": "{" + s.get("title", "") + "}",
        "year": re.search(r"\d{4}", s.get("year", "") or "").group()
        if re.search(r"\d{4}", s.get("year", "") or "") else s.get("year", ""),
        "howpublished": s.get("venue", ""),
        "note": f"Verification: {s['verification']}",
    }
    if doi_url.startswith("http"):
        fields["url"] = doi_url
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields.items() if v)
    return f"@misc{{{key},\n{body}\n}}"


def build_bibliography(sources: list[dict]) -> None:
    """BibTeX export of the corpus - promised by the folder-layout note in the
    README since the corpus existed, never actually generated until now."""
    used_keys: set = set()
    verified = [s for s in sources if s["verification"] != "COULD_NOT_VERIFY"]
    entries = [bib_entry(s, bib_key(s, used_keys)) for s in sorted(verified, key=year_key, reverse=True)]
    header = (
        "% Generated by scripts/build_awesome_literature_index.py from\n"
        "% verified-research-corpus-2026-08-12.json - do not hand-edit.\n"
        f"% {len(entries)} entries (COULD_NOT_VERIFY sources excluded).\n\n"
    )
    BIB_OUT.write_text(header + "\n\n".join(entries) + "\n", encoding="utf-8")
    print(f"wrote {BIB_OUT} ({len(entries)} entries)")


if __name__ == "__main__":
    build()
