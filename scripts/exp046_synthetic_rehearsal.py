"""Synthetic expert review over the 27 variability patterns - INSTRUMENT REHEARSAL ONLY.

Every record is stamped reviewerId = SYNTHETIC_NOT_HUMAN and evidenceClass =
SYNTHETIC_NOT_EXPERT_EVIDENCE, per the project's standing decision that synthetic
EXP-005 labels may exist only in a separate ignored trial and are never ground truth.
Its purpose is to rehearse the H1/H2/H3 measurement end to end before real labels
exist, so that the analysis code is exercised and the reporting shape is fixed.

The labelling rule is deterministic and stated, not sampled: it reproduces the
behaviour the real reviewer showed in the project workbooks, where corrections
overwhelmingly strengthened a verdict the agent had made too strict, and where
construct misplacement was the second-largest correction class. Nothing about it
is evidence that a human would label this way.

Usage: python synthetic_expert_review.py --dataset-root <dir> --out <dir>
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os

SETTINGS = ("ucd_ch", "ucd_pw", "cd_ch", "cd_pw")
PROTOCOL = "synthetic-rehearsal-v1"
REVIEW_DATE = "2026-09-03"

RULES = [
    ("R1", "A pattern the agent marked Undetermined, or asked review for, is labelled Undetermined and "
           "routed to adjudication; the instrument must show it does not silently resolve these."),
    ("R2", "A pattern whose recorded label distribution is dominated by Partially-Satisfied is labelled "
           "Substantial Variability, mirroring the reviewer's observed tendency to read partial compliance "
           "as a real alternative rather than an error."),
    ("R3", "A pattern the agent classified with Medium confidence and flagged for a guideline update is "
           "labelled Substantial Variability, since the reviewer's corrections at this stage were "
           "predominantly upgrades of an over-strict verdict."),
    ("R4", "A pattern that turns on where a requirement is modelled rather than whether it is present is "
           "labelled Occasional Variability with a construct-placement rationale, mirroring the second "
           "largest correction class in the workbooks."),
    ("R5", "Everything else keeps the agent's classification, so the rehearsal does not manufacture "
           "disagreement it cannot justify."),
]

PLACEMENT = ("operation", "attribute", "association", "enumeration", "actor", "boundary", "inheritance")


def load_patterns(root):
    out = []
    for setting in SETTINGS:
        cls_path = sorted(glob.glob(os.path.join(root, "System", "eval_output", setting,
                                                 "agentD_variability_classes*.json")))[0]
        with open(cls_path, encoding="utf-8") as fh:
            classifications = json.load(fh).get("variability_classifications", [])
        dev_path = sorted(glob.glob(os.path.join(root, "System", "eval_output", setting,
                                                 "agentD_deviation_patterns*.json")))[0]
        with open(dev_path, encoding="utf-8") as fh:
            raw = json.load(fh)
        deviations = raw if isinstance(raw, list) else next(
            (v for v in raw.values() if isinstance(v, list)), [])
        by_id = {str(d.get("pattern_id")): d for d in deviations}
        for c in classifications:
            out.append((setting, c, by_id.get(str(c.get("pattern_id")), {})))
    return out


def distribution(deviation):
    raw = deviation.get("label_distribution")
    if isinstance(raw, dict):
        return {str(k): v for k, v in raw.items()}
    if isinstance(raw, str):
        try:
            return json.loads(raw.replace("'", '"'))
        except Exception:
            return {}
    return {}


def decide(setting, agent, deviation):
    dist = distribution(deviation)
    partial = dist.get("Partially-Satisfied", 0)
    total = sum(v for v in dist.values() if isinstance(v, (int, float))) or 1
    text = " ".join(str(agent.get(k, "")) for k in ("justification", "evidence")).lower()
    agent_label = str(agent.get("classification", ""))
    confidence = str(agent.get("confidence", ""))

    if agent.get("requires_human_review") or agent_label.lower().startswith("undetermined"):
        return "Undetermined", "R1", ("The agent did not resolve this pattern, so the rehearsal routes it to "
                                      "adjudication rather than inventing a verdict.")
    if partial / total >= 0.34:
        return "Substantial Variability", "R2", (
            "Partial compliance dominates the recorded distribution ({} of {} judgments), which the reviewer "
            "read as a legitimate alternative rather than a defect.".format(partial, total))
    if confidence.lower() == "medium" and agent.get("flag_for_guidelines_update"):
        return "Substantial Variability", "R3", (
            "Medium confidence together with a proposed guideline change is where the reviewer most often "
            "strengthened the agent's verdict.")
    if any(word in text for word in PLACEMENT):
        return "Occasional Variability", "R4", (
            "The pattern turns on where the requirement is modelled rather than whether it is present, which "
            "the reviewer treated as a construct-placement matter.")
    return agent_label or "Occasional Variability", "R5", (
        "No rule fires, so the rehearsal keeps the agent classification rather than manufacturing a "
        "disagreement it cannot justify.")


def build(root):
    records, agree, disagree = [], 0, 0
    for setting, agent, deviation in load_patterns(root):
        label, rule, rationale = decide(setting, agent, deviation)
        pattern_id = str(agent.get("pattern_id"))
        item = "{}:{}".format(setting, pattern_id)
        digest = hashlib.sha256(item.encode("utf-8")).hexdigest()
        same = label == str(agent.get("classification", ""))
        agree += 1 if same else 0
        disagree += 0 if same else 1
        records.append({
            "schemaVersion": "gold-label-record-v2",
            "recordType": "SyntheticRehearsalLabel",
            "recordId": "SYN-{}".format(digest[:12]),
            "anonymousItemId": digest[:16],
            "partition": setting,
            "reviewerId": "SYNTHETIC_NOT_HUMAN",
            "reviewerRole": "synthetic-rehearsal",
            "expertLabel": label,
            "expertRationale": rationale,
            "confidence": "not-applicable-synthetic",
            "reviewDate": REVIEW_DATE,
            "leakageClass": "synthetic",
            "generalizationSafe": False,
            "sourceSheetSha256": digest,
            "annotationProtocolVersion": PROTOCOL,
            "adjudicationStatus": "not-adjudicated",
            "immutable": True,
            "evidenceClass": "SYNTHETIC_NOT_EXPERT_EVIDENCE",
            "appliedRule": rule,
            "agentClassification": agent.get("classification"),
            "agentConfidence": agent.get("confidence"),
            "agreesWithAgent": same,
        })
    return {
        "instrument": "synthetic expert review, rehearsal only",
        "protocolVersion": PROTOCOL,
        "claimBoundary": ("Not expert evidence and not ground truth. Every record is synthetic and marked "
                          "SYNTHETIC_NOT_HUMAN. It exists to rehearse the measurement before real labels are "
                          "collected; EXP-005 remains at 0 of 24 generalization-safe expert labels, and no "
                          "accuracy, agreement or improvement result may be reported from these rows."),
        "rules": [{"id": rid, "statement": text} for rid, text in RULES],
        "counts": {"records": len(records), "keeps_agent_label": agree, "differs_from_agent": disagree},
        "records": records,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    result = build(args.dataset_root)
    path = os.path.join(args.out, "synthetic_expert_review.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, ensure_ascii=False)
    counts = result["counts"]
    print("records {} | keeps the agent label {} | differs {}".format(
        counts["records"], counts["keeps_agent_label"], counts["differs_from_agent"]))
    by_rule = {}
    for r in result["records"]:
        by_rule[r["appliedRule"]] = by_rule.get(r["appliedRule"], 0) + 1
    print("rule application:", dict(sorted(by_rule.items())))
    print("every record marked synthetic:",
          all(r["reviewerId"] == "SYNTHETIC_NOT_HUMAN" for r in result["records"]))
    print("wrote", path)


if __name__ == "__main__":
    main()
