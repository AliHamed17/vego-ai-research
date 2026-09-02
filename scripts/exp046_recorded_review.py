#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-046 - What the recorded human review of the VEGO-AI run already shows.

Reads the project's own analysis workbooks (delivered with the VEGO-AI dataset,
kept outside the repository because they carry student submission ids) and
reproduces every number on the 2026-09-03 one-page study design:

  Stage 2  guideline_clusters_<setting>.xlsx  Status column: Full / Partially / WRONG
  Stage 3  scores_<setting>.xlsx              compliance_vectors and uncovered_fragments
                                              sheets, Score column 1 = kept, 0 = overturned
  Model    all_scores_published.xlsx          agent score_pct beside the course grade
  Stage 2  System/inputs/<domain>/domain_base_<diagram>.txt   the course reference
  Stage 4  System/eval_output/<setting>/agentD_variability_classes*.json

CLAIM BOUNDARY: descriptive counts over the review as recorded. "Overturned" means
the reviewer disagreed with the agent on that item; it is not proof that the system
was wrong. The review is the project's own, not independent adjudication, and the
reviewed items were chosen by the reviewer, not sampled at random. No accuracy,
improvement, effort or generalization claim; EXP-005 remains 0/24 expert labels.

Usage:
  python exp046_recorded_review.py --dataset-root <dir containing System/> [--json out.json]
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import math
import os
import re
import sys

SETTINGS = ("ucd_ch", "ucd_pw", "cd_ch", "cd_pw")
STATUS_VERDICTS = {"full", "partially", "parially", "wrong", "not sure it is a uc"}


def _load_sheet(path, title=None):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        for ws in wb.worksheets:
            if title is None or ws.title == title:
                rows = list(ws.iter_rows(values_only=True))
                yield ws.title, [str(h).replace("\n", " ") for h in rows[0]], rows[1:]
    finally:
        wb.close()


def _col(header, predicate):
    return next(i for i, h in enumerate(header) if predicate(h.lower()))


def stage2_review(root):
    """Human Status verdict on each guideline the domain advisor wrote."""
    per, counts = {}, collections.Counter()
    for path in sorted(glob.glob(os.path.join(root, "System", "analysis", "guideline_clusters_*.xlsx"))):
        setting = os.path.basename(path)[len("guideline_clusters_"):-len(".xlsx")]
        for _, header, body in _load_sheet(path):
            st = _col(header, lambda h: h == "status")
            verdicts = [str(r[st]).strip().lower().replace("parially", "partially")
                        for r in body if r[st] not in (None, "")
                        and str(r[st]).strip().lower() in STATUS_VERDICTS]
            full = sum(1 for v in verdicts if v == "full")
            per[setting] = {"reviewed": len(verdicts), "accepted_in_full": full,
                            "not_accepted_in_full": len(verdicts) - full,
                            "breakdown": dict(collections.Counter(verdicts))}
            for v in verdicts:
                counts[v] += 1
    total = sum(counts.values())
    return {"per_setting": per, "reviewed": total, "accepted_in_full": counts["full"],
            "not_accepted_in_full": total - counts["full"], "breakdown": dict(counts)}


def stage3_review(root):
    """Kept/overturned marks on the inspector's output, by the agent's own verdict."""
    sheets = {"compliance_vectors": collections.Counter(), "uncovered_fragments": collections.Counter()}
    models = collections.defaultdict(set)
    for path in sorted(glob.glob(os.path.join(root, "System", "analysis", "scores_*.xlsx"))):
        setting = os.path.basename(path)[len("scores_"):-len(".xlsx")]
        for title, header, body in _load_sheet(path):
            score = _col(header, lambda h: h.startswith("score"))
            verdict = _col(header, (lambda h: "compl" in h) if title == "compliance_vectors" else (lambda h: ".la" in h))
            for row in body:
                if row[score] in (0, 1):
                    sheets[title][(str(row[verdict]), "kept" if row[score] == 1 else "overturned")] += 1
                    models[(setting, title)].add(str(row[0]).split(".")[0])
    out = {}
    for title, counter in sheets.items():
        by_verdict = {}
        for (v, outcome), n in counter.items():
            by_verdict.setdefault(v, {"kept": 0, "overturned": 0})[outcome] += n
        for v, d in by_verdict.items():
            d["reviewed"] = d["kept"] + d["overturned"]
            d["overturn_rate"] = round(d["overturned"] / d["reviewed"], 4)
        reviewed = sum(d["reviewed"] for d in by_verdict.values())
        overturned = sum(d["overturned"] for d in by_verdict.values())
        out[title] = {"reviewed": reviewed, "overturned": overturned,
                      "overturn_rate": round(overturned / reviewed, 4) if reviewed else None,
                      "by_agent_verdict": by_verdict,
                      "model_reviews": {k[0]: len(v) for k, v in models.items() if k[1] == title}}
    return out


def escalation_rule(stage3, sheet="compliance_vectors", keep_silent="Satisfied"):
    """What a rule 'ask a human whenever the agent did not say <keep_silent>' would do."""
    by = stage3[sheet]["by_agent_verdict"]
    flagged = sum(d["reviewed"] for v, d in by.items() if v != keep_silent)
    caught = sum(d["overturned"] for v, d in by.items() if v != keep_silent)
    reviewed, overturned = stage3[sheet]["reviewed"], stage3[sheet]["overturned"]
    return {"rule": f"escalate unless the agent said {keep_silent}",
            "items_flagged": flagged, "items_total": reviewed,
            "share_flagged": round(flagged / reviewed, 4),
            "overturns_covered": caught, "overturns_total": overturned,
            "share_of_overturns_covered": round(caught / overturned, 4)}


def reference_coverage(root):
    """Course requirements with no guideline the domain advisor wrote matched to them."""
    per, lines_total, unmatched_total = {}, 0, 0
    for setting in SETTINGS:
        diagram, domain = setting.split("_")
        base = os.path.join(root, "System", "inputs", domain, f"domain_base_{diagram}.txt")
        with open(base, encoding="utf-8") as fh:
            lines = [l.strip() for l in fh if l.strip() and not l.lstrip().startswith("#")]
        with open(os.path.join(root, "System", "eval_output", setting, "agentB_metrics.json"), encoding="utf-8") as fh:
            metrics = json.load(fh)
        unmatched = metrics.get("unassigned_base_guidelines") or []
        if metrics.get("false_negatives") != len(unmatched):
            raise SystemExit(f"{setting}: unmatched list ({len(unmatched)}) != false_negatives ({metrics['false_negatives']})")
        per[setting] = {"reference_lines": len(lines), "unmatched": len(unmatched)}
        lines_total += len(lines)
        unmatched_total += len(unmatched)
    return {"per_setting": per, "reference_lines": lines_total, "unmatched": unmatched_total}


def stage4_queue(root):
    """The one point where the run does ask: the classifier's review queue."""
    per, total_patterns, total_flagged = {}, 0, 0
    for setting in SETTINGS:
        hits = sorted(glob.glob(os.path.join(root, "System", "eval_output", setting, "agentD_variability_classes*.json")))
        with open(hits[0], encoding="utf-8") as fh:
            patterns = json.load(fh).get("variability_classifications", [])
        flagged = [p for p in patterns
                   if str(p.get("confidence", "")).lower() in ("low", "medium")
                   or p.get("requires_human_review") or p.get("flag_for_guidelines_update")
                   or str(p.get("classification", "")).lower().startswith("undetermined")]
        per[setting] = {"patterns": len(patterns), "queued": len(flagged)}
        total_patterns += len(patterns)
        total_flagged += len(flagged)
    return {"per_setting": per, "patterns": total_patterns, "queued": total_flagged}


def _pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
    return round(num / den, 4) if den else None


def score_versus_grade(root):
    """The agent's score beside the course grade, where both exist."""
    path = os.path.join(root, "System", "analysis", "all_scores_published.xlsx")
    _, header, body = next(_load_sheet(path, "All Scores"))
    idx = {h: i for i, h in enumerate(header)}
    rows = [r for r in body
            if isinstance(r[idx["score_pct"]], (int, float)) and isinstance(r[idx["grade"]], (int, float))]
    per = {}
    for setting in SETTINGS:
        sub = [(r[idx["score_pct"]], r[idx["grade"]]) for r in rows if str(r[idx["source"]]) == setting]
        if sub:
            per[setting] = {"rows": len(sub), "correlation": _pearson([a for a, _ in sub], [b for _, b in sub])}
    return {"rows": len(rows), "per_setting": per,
            "correlation": _pearson([r[idx["score_pct"]] for r in rows], [r[idx["grade"]] for r in rows])}


def run(root):
    s2, s3 = stage2_review(root), stage3_review(root)
    result = {
        "experiment": "EXP-046",
        "title": "What the recorded human review of the frozen run already shows",
        "claim_boundary": ("Descriptive counts over the review as recorded. Overturned means the reviewer disagreed, "
                           "not that the system was proven wrong; the review is the project's own, not independent "
                           "adjudication, and its items were chosen by the reviewer, not sampled at random. "
                           "No accuracy, improvement, effort or generalization claim; EXP-005 remains 0/24."),
        "stage2_guideline_review": s2,
        "stage2_reference_coverage": reference_coverage(root),
        "stage3_review": s3,
        "stage3_escalation_rule": escalation_rule(s3),
        "stage4_queue": stage4_queue(root),
        "score_versus_course_grade": score_versus_grade(root),
    }
    result["pooled_review"] = {
        "items_reviewed": s3["compliance_vectors"]["reviewed"] + s3["uncovered_fragments"]["reviewed"],
        "items_overturned": s3["compliance_vectors"]["overturned"] + s3["uncovered_fragments"]["overturned"],
    }
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dataset-root", required=True, help="directory that contains System/")
    ap.add_argument("--json", help="write the full result as JSON")
    args = ap.parse_args(argv)
    r = run(args.dataset_root)

    s2, cov, s3 = r["stage2_guideline_review"], r["stage2_reference_coverage"], r["stage3_review"]
    print(f"Stage 2  guidelines reviewed {s2['reviewed']}, not accepted in full {s2['not_accepted_in_full']} "
          f"({s2['not_accepted_in_full'] / s2['reviewed']:.0%}) {s2['breakdown']}")
    print(f"Stage 2  course requirements unmatched {cov['unmatched']} of {cov['reference_lines']} reference lines")
    for sheet in ("compliance_vectors", "uncovered_fragments"):
        d = s3[sheet]
        print(f"Stage 3  {sheet:20s} reviewed {d['reviewed']:4d} overturned {d['overturned']:3d} ({d['overturn_rate']:.1%})")
        for v, x in sorted(d["by_agent_verdict"].items()):
            print(f"           agent said {v:22s} n={x['reviewed']:4d} overturned {x['overturned']:3d} = {x['overturn_rate']:.1%}")
    rule = r["stage3_escalation_rule"]
    print(f"Rule     {rule['rule']}: flags {rule['items_flagged']}/{rule['items_total']} "
          f"({rule['share_flagged']:.0%}) and covers {rule['overturns_covered']}/{rule['overturns_total']} "
          f"overturns ({rule['share_of_overturns_covered']:.0%})")
    q = r["stage4_queue"]
    print(f"Stage 4  {q['queued']} of {q['patterns']} patterns queued (the only point the run asks)")
    g = r["score_versus_course_grade"]
    print(f"Grade    agent score vs course grade over {g['rows']} rows: r={g['correlation']} "
          + " ".join(f"{k}={v['correlation']}" for k, v in g["per_setting"].items()))
    p = r["pooled_review"]
    print(f"Pooled   {p['items_overturned']} of {p['items_reviewed']} reviewed items overturned")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(r, fh, indent=1, ensure_ascii=False)
        print("wrote", args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
