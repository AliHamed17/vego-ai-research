"""Build the complete supervisor package for one Study 2 prospective run.

    uv run --with matplotlib --with python-pptx --with python-bidi \
        python scripts/study2_prospective_report.py --run-id <RUN_ID> --private-root <ROOT> [--pr-url URL]

Reads the public aggregate and the frozen manifest for every number; reads the
private root only to validate the aggregate and to build the blinded rater
cards there.  Writes public Markdown documents next to the aggregate and the
Hebrew Office deliverables to a Downloads folder.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _relative in ("src", "scripts", "VEGO-AI/framework"):
    if str(ROOT / _relative) not in sys.path:
        sys.path.insert(0, str(ROOT / _relative))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--private-root", required=True)
    parser.add_argument("--public-dir", default=None)
    parser.add_argument("--deliverables-dir", default=None)
    parser.add_argument("--pr-url", default=None)
    parser.add_argument("--skip-office", action="store_true", help="skip PDF export through Word/PowerPoint")
    args = parser.parse_args()

    from vego_study2.prospective.aggregate import validate_public
    from vego_study2.prospective.reporting.analysis import (
        DOCS_DIR,
        build_analysis,
        load_aggregate,
        load_manifest_document,
    )
    from vego_study2.prospective.reporting.cards import build_cards
    from vego_study2.prospective.reporting.charts import build_all_charts
    from vego_study2.prospective.reporting.docx_he import (
        build_cards_docx,
        build_executive_summary,
        build_report,
    )
    from vego_study2.prospective.reporting.e2e_visual import build_e2e_visual
    from vego_study2.prospective.reporting.markdown_docs import (
        budget_spend_receipt,
        case_selection_receipt,
        claims_table,
        evidence_index,
        executive_summary,
        supervisor_email_he,
        technical_appendix,
    )
    from vego_study2.prospective.reporting.pptx_he import build_presentation

    private_root = Path(args.private_root).resolve()
    output_root = private_root / "study2-prospective" / args.run_id
    public_dir = Path(args.public_dir) if args.public_dir else DOCS_DIR / "evidence" / args.run_id
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    deliverables = Path(args.deliverables_dir) if args.deliverables_dir else Path.home() / "Downloads" / f"VEGO_AI_Study2_Prospective_{stamp}_{args.run_id}"
    deliverables.mkdir(parents=True, exist_ok=True)

    aggregate = load_aggregate(args.run_id, public_dir)
    manifest = load_manifest_document()
    selection = json.loads((DOCS_DIR / "case-selection-manifest.json").read_text(encoding="utf-8"))
    budget_doc = json.loads((DOCS_DIR / "budget-reservation.json").read_text(encoding="utf-8"))
    analysis = build_analysis(aggregate, manifest)
    (public_dir / "analysis.json").write_text(json.dumps(analysis, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    validation = validate_public(output_root, public_dir / "public-aggregate.json")
    (public_dir / "validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    cards = build_cards(output_root, public_dir)
    if cards.get("cards"):
        build_cards_docx(output_root / "human-review" / "cards.json", output_root / "human-review" / "cards.he.docx")

    charts = build_all_charts(analysis, public_dir / "charts")
    for path in charts.values():
        shutil.copy2(path, deliverables / path.name)

    (public_dir / "technical-appendix.md").write_text(technical_appendix(analysis, manifest, validation, cards), encoding="utf-8")
    (public_dir / "case-selection-receipt.md").write_text(case_selection_receipt(selection, analysis), encoding="utf-8")
    (public_dir / "budget-spend-receipt.md").write_text(budget_spend_receipt(analysis, budget_doc), encoding="utf-8")
    (public_dir / "claims-and-limitations-table.md").write_text(claims_table(analysis), encoding="utf-8")
    (public_dir / "executive-summary.md").write_text(executive_summary(analysis), encoding="utf-8")
    (public_dir / "supervisor-email.he.md").write_text(supervisor_email_he(analysis, args.pr_url, deliverables), encoding="utf-8")

    produced: dict[str, Path] = {}
    base = f"VEGO_AI_Study2_Prospective_{args.run_id}"
    produced["report_docx"] = build_report(analysis, manifest, selection, budget_doc, charts, cards, deliverables / f"{base}_Report.he.docx")
    produced["summary_docx"] = build_executive_summary(analysis, deliverables / f"{base}_ExecutiveSummary.he.docx")
    produced["slides_pptx"] = build_presentation(analysis, manifest, selection, charts, deliverables / f"{base}_Slides.he.pptx")
    visual = build_e2e_visual(analysis, deliverables)
    produced["e2e_png"], produced["e2e_pdf"] = visual["png"], visual["pdf"]
    shutil.copy2(visual["png"], public_dir / "study2-e2e-visual.he.png")
    if not args.skip_office:
        from vego_study2.prospective.reporting.office import docx_to_pdf, pptx_to_pdf

        produced["report_pdf"] = docx_to_pdf(produced["report_docx"], deliverables / f"{base}_Report.he.pdf")
        produced["summary_pdf"] = docx_to_pdf(produced["summary_docx"], deliverables / f"{base}_ExecutiveSummary.he.pdf")
        produced["slides_pdf"] = pptx_to_pdf(produced["slides_pptx"], deliverables / f"{base}_Slides.he.pdf")
    for name in ("technical-appendix.md", "executive-summary.md", "supervisor-email.he.md", "claims-and-limitations-table.md",
                 "budget-spend-receipt.md", "case-selection-receipt.md"):
        shutil.copy2(public_dir / name, deliverables / name)
    shutil.copy2(DOCS_DIR / "human-rater-rubric.he.md", deliverables / "human-rater-rubric.he.md")

    receipt = json.loads((output_root / "run-receipt.json").read_text(encoding="utf-8"))
    private_bindings = {
        "run receipt binding": receipt["receipt_binding"]["sha256"],
        "call ledger": receipt["ledger_sha256"],
        "ON Q&A event log": receipt["event_log_sha256"],
        "pipeline output manifest": receipt["pipeline_output_manifest_sha256"],
        "rater cards": cards.get("cards_sha256"),
        "rater card key": cards.get("key_sha256"),
        "location": receipt["output_root_template"],
    }
    for row in aggregate["conditions"]["VEGO_AI_ON"]["cases"] + aggregate["conditions"]["VEGO_AI_OFF"]["cases"]:
        if row.get("output_sha256"):
            private_bindings[f"{row['condition']} case {row['case_id']} artifact"] = row["output_sha256"]
    (public_dir / "evidence-index.md").write_text(evidence_index(analysis, public_dir, produced, private_bindings), encoding="utf-8")
    shutil.copy2(public_dir / "evidence-index.md", deliverables / "evidence-index.md")

    summary = {
        "run_id": args.run_id,
        "validation": validation,
        "cards": cards.get("cards"),
        "deliverables_dir": str(deliverables),
        "files": sorted(p.name for p in deliverables.iterdir()),
        "public_dir_files": sorted(p.name for p in public_dir.iterdir()),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if validation["match"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
