#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXP-045 - Descriptive escalation-point inventory over the frozen VEGO-AI run.

Reads ONLY existing, immutable artifacts (no LLM call, no pipeline change) and lays
out, per pipeline stage and per setting, the points at which an automatic signal
already present in the artifacts would have suggested asking a human, together with
the reference material that exists for that stage.  It answers the descriptive
question "WHERE and BY WHICH SIGNAL could a human have been asked" for the frozen
baseline (no escalation was performed at Stages 1-3; Stage 4 has the M1 queue).

Stage map (Iris, 2026-09-02: "template guidelines, inspector, domain guidelines"):
  Stage 1  Agent 1 language advisor  -> eval Agent A mapping vs the language base
  Stage 2  Agent 2 domain advisor    -> eval Agent B mapping vs the domain base
  Stage 3  Agent 3 model inspector   -> eval Agent C per-case scoring (uncovered fragments)
  Stage 4  Agent 4 variability       -> Agent D classes + M1 human review queue

CLAIM BOUNDARY: descriptive counts only.  Nothing here says that asking a human at
any point would have improved anything; EXP-005 remains 0/24 generalization-safe
labels.  A "candidate escalation point" is a signal value, not a verified error.

Usage:
  python scripts/exp045_escalation_points.py [--vego-root VEGO-AI] [--out reports/generated/exp045]
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys

SETTINGS = ("ucd_ch", "ucd_pw", "cd_ch", "cd_pw")
STAGE_NAMES = {
    1: "Agent 1 language advisor (template guidelines)",
    2: "Agent 2 domain advisor (domain guidelines)",
    3: "Agent 3 model inspector (per-case compliance)",
    4: "Agent 4 variability explorer (pattern classification)",
}
LOW_CERTAINTY = 0.8  # mapping_certainty below this is read as a low-confidence signal


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _first(pattern):
    hits = sorted(glob.glob(pattern))
    return hits[0] if hits else None


def _base_constructs(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return [ln.strip() for ln in fh if ln.strip() and not ln.lstrip().startswith("#")]


def stage1(root, setting, diagram):
    ev = os.path.join(root, "eval_output", setting)
    mapping = _load(os.path.join(ev, "agentA_guideline_mapping.json"))
    metrics = _load(os.path.join(ev, "agentA_metrics.json"))
    base = _base_constructs(os.path.join(root, "inputs", f"language_base_{diagram}.txt"))
    clusters = mapping.get("clusters", [])
    points = []
    for c in clusters:
        conf = str(c.get("match_confidence", "")).strip()
        if c.get("base_assignment") in (None, "", "null") or conf.lower() not in ("high",):
            points.append({
                "signal": "language_cluster_unassigned_or_not_high_confidence",
                "cluster_id": c.get("cluster_id"),
                "canonical_description": c.get("canonical_description"),
                "base_assignment": c.get("base_assignment"),
                "match_confidence": conf,
            })
    assigned = {c.get("base_assignment") for c in clusters if c.get("base_assignment")}
    unreached = [b for b in (base or []) if b not in assigned]
    return {
        "stage": 1,
        "reference_exists": True,
        "reference": f"inputs/language_base_{diagram}.txt",
        "denominators": {
            "agent_clusters": len(clusters),
            "base_constructs": len(base) if base is not None else None,
            "reachable_base_count_reported": metrics.get("reachable_base_count"),
        },
        "metrics": {"overall_agreement": metrics.get("overall_agreement")},
        "candidate_points": points,
        "unreached_base_constructs": unreached,
        "counts": {"candidate_points": len(points), "unreached_base_constructs": len(unreached)},
    }


def stage2(root, setting):
    ev = os.path.join(root, "eval_output", setting)
    mapping = _load(os.path.join(ev, "agentB_guideline_mapping.json"))
    metrics = _load(os.path.join(ev, "agentB_metrics.json"))
    clusters = mapping.get("clusters", [])
    points = []
    for c in clusters:
        certs = [c.get(f"run{i}_guideline", {}).get("mapping_certainty") for i in (1, 2, 3)]
        certs = [x for x in certs if isinstance(x, (int, float))]
        low = bool(certs) and min(certs) < LOW_CERTAINTY
        unassigned = c.get("base_assignment") in (None, "", "null")
        if low or unassigned:
            points.append({
                "signal": "+".join(s for s, f in (("domain_cluster_no_base_match", unassigned), ("low_mapping_certainty", low)) if f),
                "cluster_id": c.get("cluster_id"),
                "guideline_name": c.get("run1_guideline_name"),
                "min_mapping_certainty": min(certs) if certs else None,
                "match_confidence": c.get("match_confidence"),
            })
    # The evaluator metric file is authoritative; the mapping file may list fewer entries
    # (cd_ch: 20 in the mapping vs 22 false negatives in the metrics).
    missed = metrics.get("unassigned_base_guidelines") or mapping.get("unassigned_base_guidelines") or []
    fn = metrics.get("false_negatives")
    if isinstance(fn, int) and fn != len(missed):
        raise SystemExit(f"{setting}: unassigned_base_guidelines ({len(missed)}) != false_negatives ({fn})")
    best_path = os.path.join(ev, "agentB_best_guidelines.json")
    best = _load(best_path) if os.path.exists(best_path) else {}
    open_questions = best.get("questions_to_language_advisor", []) if isinstance(best, dict) else []
    best_guidelines = best.get("reference_guidelines", []) if isinstance(best, dict) else []
    diagram, domain = setting.split("_")
    ref_rel = f"inputs/{domain}/domain_base_{diagram}.txt"
    ref_in_repo = os.path.exists(os.path.join(root, ref_rel))
    return {
        "stage": 2,
        "reference_exists": True,
        "reference_file_in_repo": ref_in_repo,
        "reference": ref_rel if ref_in_repo else f"{ref_rel} NOT in repository; reference read from the evaluator record (agentB_metrics.json unassigned_base_guidelines, agentB_guideline_mapping.json base_assignment)",
        "denominators": {"agent_clusters": len(clusters),
                         "best_run_guidelines": len(best_guidelines),
                         "reference_guidelines": (metrics.get("true_positives") or 0) + (metrics.get("false_negatives") or 0)},
        "metrics": {k: metrics.get(k) for k in ("precision", "recall", "f1", "true_positives", "false_positives", "false_negatives")},
        "candidate_points": points,
        "reference_guidelines_missed": missed,
        "open_questions_to_language_advisor": open_questions,
        "counts": {"candidate_points": len(points), "reference_guidelines_missed": len(missed),
                   "open_questions_to_language_advisor": len(open_questions)},
    }


def stage3(root, setting):
    ev = os.path.join(root, "eval_output", setting)
    files = sorted(glob.glob(os.path.join(ev, "agentC_case_*.json")))
    label_counts = collections.Counter()
    severity_counts = collections.Counter()
    partial = 0
    points = []
    files_with_alternative = 0
    for f in files:
        case = _load(f)
        if any(fr.get("label") == "Alternative" for fr in case.get("uncovered_fragments", [])):
            files_with_alternative += 1
        for frag in case.get("uncovered_fragments", []):
            label = frag.get("label")
            label_counts[label] += 1
            if label in ("Domain Mistake", "Language Mistake"):
                severity_counts[str(frag.get("severity"))] += 1
            if label == "Alternative" or str(frag.get("severity")).lower() == "high":
                points.append({
                    "signal": "alternative_reading" if label == "Alternative" else "high_severity_mistake",
                    "case_id": case.get("case_id"),
                    "label": label,
                    "severity": frag.get("severity"),
                    "fragment": (frag.get("fragment") or "")[:160],
                })
        partial += sum(1 for p in case.get("potential_found", []) if p.get("compliance_status") == "Partially-Satisfied")
    return {
        "stage": 3,
        "reference_exists": False,
        "reference": "inputs/scoring_schema.txt labels only; no reference verdict per fragment",
        "denominators": {"case_files": len(files), "uncovered_fragments": sum(label_counts.values())},
        "metrics": {"fragment_labels": dict(label_counts), "mistake_severities": dict(severity_counts),
                    "partially_satisfied_potential_matches": partial},
        "candidate_points": points,
        "counts": {"candidate_points": len(points),
                   "alternative_readings": label_counts.get("Alternative", 0),
                   "case_files_with_alternative": files_with_alternative,
                   "high_severity_mistakes": severity_counts.get("High", 0)},
    }


def stage4(root, setting):
    ev = os.path.join(root, "eval_output", setting)
    classes_path = _first(os.path.join(ev, "agentD_variability_classes*.json"))
    classes = _load(classes_path) if classes_path else {}
    plist = classes.get("variability_classifications", [])
    conf = collections.Counter(str(p.get("confidence")) for p in plist)
    cls = collections.Counter(str(p.get("classification")) for p in plist)
    points = []
    for p in plist:
        flags = []
        if str(p.get("confidence", "")).lower() in ("low", "medium"):
            flags.append(f"{str(p.get('confidence')).lower()}_confidence")
        if p.get("requires_human_review"):
            flags.append("agent_requested_human_review")
        if p.get("flag_for_guidelines_update"):
            flags.append("guideline_update_proposed")
        if str(p.get("classification", "")).lower().startswith("undetermined"):
            flags.append("undetermined_classification")
        if flags:
            points.append({"signal": "+".join(flags), "pattern_id": p.get("pattern_id"),
                           "classification": p.get("classification"), "confidence": p.get("confidence")})
    queue = _jsonl(os.path.join(root, "human_review_output", setting, "human_review_queue.jsonl"))
    triggers = collections.Counter(t for it in queue for t in it.get("trigger_reasons", []))
    upstream_q = len(classes.get("questions_to_language_advisor", [])) + len(classes.get("questions_to_domain_advisor", []))
    return {
        "stage": 4,
        "reference_exists": False,
        "reference": "author-reviewed classes are byte-identical to Agent 4 output (agreement, not ground truth)",
        "denominators": {"patterns": len(plist), "queue_items": len(queue)},
        "metrics": {"confidence": dict(conf), "classes": dict(cls), "queue_trigger_reasons": dict(triggers),
                    "questions_to_upstream_agents": upstream_q},
        "candidate_points": points,
        "queue_items": [{"review_id": it.get("review_id"), "pattern_id": it.get("pattern_id"),
                         "trigger_reasons": it.get("trigger_reasons")} for it in queue],
        "counts": {"candidate_points": len(points), "queue_items": len(queue)},
    }


def run(root, out):
    os.makedirs(out, exist_ok=True)
    summary = {"experiment": "EXP-045", "title": "Descriptive escalation-point inventory over the frozen run",
               "claim_boundary": "Descriptive counts of signal values only; no improvement, accuracy, effort, or generalization claim (EXP-005 0/24).",
               "stage_names": STAGE_NAMES, "settings": {}}
    for s in SETTINGS:
        diagram = s.split("_")[0]
        per = {"stage1": stage1(root, s, diagram), "stage2": stage2(root, s), "stage3": stage3(root, s), "stage4": stage4(root, s)}
        with open(os.path.join(out, f"escalation_points_{s}.json"), "w", encoding="utf-8") as fh:
            json.dump(per, fh, indent=1, ensure_ascii=False)
        summary["settings"][s] = {k: {"counts": v["counts"], "denominators": v["denominators"], "metrics": v["metrics"],
                                      "reference_exists": v["reference_exists"]} for k, v in per.items()}
    totals = collections.defaultdict(int)
    for s, stages in summary["settings"].items():
        for st, v in stages.items():
            for k, n in v["counts"].items():
                totals[f"{st}.{k}"] += n
            for k, n in v["denominators"].items():
                if isinstance(n, int):
                    totals[f"{st}.denominator.{k}"] += n
    summary["totals"] = dict(sorted(totals.items()))
    with open(os.path.join(out, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1, ensure_ascii=False)
    lines = ["# EXP-045 escalation-point inventory (descriptive)", "",
             "Counts of existing signal values per stage and setting over the frozen run. No claim of improvement.", "",
             "| Stage | Signal / denominator | ucd_ch | ucd_pw | cd_ch | cd_pw | Total |", "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    rows = [
        ("1", "language clusters not High-confidence or unassigned / clusters", "stage1", "candidate_points", "agent_clusters"),
        ("1", "language-base constructs not reached / base constructs", "stage1", "unreached_base_constructs", "base_constructs"),
        ("2", "domain clusters low-certainty or no base match / clusters", "stage2", "candidate_points", "agent_clusters"),
        ("2", "guidelines with an open question to the language advisor / best-run guidelines", "stage2", "open_questions_to_language_advisor", "best_run_guidelines"),
        ("2", "reference domain guidelines with no Agent 2 match / reference guidelines (as recorded by the evaluator)", "stage2", "reference_guidelines_missed", "reference_guidelines"),
        ("3", "case files with at least one Alternative fragment / case files", "stage3", "case_files_with_alternative", "case_files"),
        ("3", "fragments labelled Alternative (count) / case files", "stage3", "alternative_readings", "case_files"),
        ("3", "High-severity mistakes / case files", "stage3", "high_severity_mistakes", "case_files"),
        ("4", "patterns with a queue-trigger signal / patterns", "stage4", "candidate_points", "patterns"),
        ("4", "M1 queue items actually created / patterns", "stage4", "queue_items", "patterns"),
    ]
    for stage, label, st, ck, dk in rows:
        cells, tot_n, tot_d = [], 0, 0
        for s in SETTINGS:
            v = summary["settings"][s][st]
            n, d = v["counts"].get(ck, 0), v["denominators"].get(dk)
            cells.append(f"{n}/{d}" if isinstance(d, int) else str(n))
            tot_n += n
            tot_d += d if isinstance(d, int) else 0
        lines.append(f"| {stage} | {label} | " + " | ".join(cells) + f" | {tot_n}/{tot_d} |")
    lines += ["", "Stage 1 and Stage 2 have a reference (language base, domain base); Stages 3 and 4 do not, so their points are signal values awaiting human marks.", ""]
    with open(os.path.join(out, "summary.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--vego-root", default="VEGO-AI")
    ap.add_argument("--out", default=os.path.join("reports", "generated", "exp045"))
    args = ap.parse_args(argv)
    summary = run(args.vego_root, args.out)
    print(json.dumps(summary["totals"], indent=1))
    print("wrote", os.path.join(args.out, "summary.md"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
