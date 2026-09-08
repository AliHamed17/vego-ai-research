"""Markdown deliverables: appendix, evidence index, receipts, claims table, summary, email."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .. import constants as c
from .analysis import fmt_counts


def _fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NOT_AVAILABLE"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def technical_appendix(analysis: dict[str, Any], manifest: dict[str, Any], validation: dict[str, Any] | None, cards: dict[str, Any]) -> str:
    cond = analysis["conditions"]
    on, off = cond[c.CONDITION_ON], cond[c.CONDITION_OFF]
    lines = [
        f"# Technical Appendix: Study 2 Prospective Run `{analysis['run_id']}`",
        "",
        f"Evidence class: **{analysis['evidence_class']}**. Mode: {analysis['mode']}. Execution head `{analysis['execution_git_sha']}`. Manifest `{analysis['manifest_sha256']}`.",
        "",
        "## 1. Frozen configuration",
        "",
        "| Item | Value |",
        "|---|---|",
        f"| Provider / model | {analysis['model']['provider']} / {analysis['model']['model']} ({analysis['model']['api_mode']}) |",
        f"| Request parameters | max_completion_tokens {analysis['model']['request_parameters']['max_completion_tokens']}; temperature {analysis['model']['request_parameters']['temperature']}; seed {analysis['model']['request_parameters']['seed']}; roles {analysis['model']['request_parameters']['message_roles']} |",
        f"| Allowed host | {', '.join(analysis['model']['allowed_hosts'])} |",
        f"| Caps | total {analysis['caps']['total_requests']}; ON {analysis['caps'][c.CONDITION_ON]} ({analysis['caps']['on_requests_per_case']}/case); OFF {analysis['caps'][c.CONDITION_OFF]} ({analysis['caps']['off_requests_per_case']}/case) |",
        f"| Budget | hard ceiling {analysis['budget']['hard_ceiling_usd']:.2f} USD; guard {analysis['budget']['guard_ceiling_usd']:.2f}; per-request reserve {analysis['budget']['per_request_reserve_usd']:.7f}; whole-study reservation {analysis['whole_study_reservation_usd']:.4f} |",
        f"| Case ids | {', '.join(analysis['case_ids'])} |",
        f"| Started / completed (UTC) | {analysis['started_at']} / {analysis['completed_at']} |",
        "",
        "## 2. Gates",
        "",
        "| Gate | Passed | Detail |",
        "|---|---|---|",
    ]
    for name, gate in analysis["gates"].items():
        lines.append(f"| {name} | {'yes' if gate['passed'] else 'NO'} | {gate['detail']} |")
    lines += [
        "",
        "## 3. Spend and requests",
        "",
        "| Quantity | VEGO_AI_ON | VEGO_AI_OFF | Total |",
        "|---|---|---|---|",
        f"| Requests (incl. retries) | {on['requests']} | {off['requests']} | {analysis['budget']['requests']} |",
        f"| Successful requests | {on['successful_requests']} | {off['successful_requests']} | |",
        f"| Transport errors / retried | {on['transport_errors']} / {on['retried_requests']} | {off['transport_errors']} / {off['retried_requests']} | |",
        f"| Provider errors | {on['provider_errors']} | {off['provider_errors']} | |",
        f"| Prompt tokens | {on['prompt_tokens']} | {off['prompt_tokens']} | {analysis['budget']['prompt_tokens']} |",
        f"| Completion tokens | {on['completion_tokens']} | {off['completion_tokens']} | {analysis['budget']['completion_tokens']} |",
        f"| Cost USD | {on['cost_usd']:.6f} | {off['cost_usd']:.6f} | {analysis['budget']['actual_cost_usd']:.6f} |",
        f"| Elapsed seconds | {on['elapsed_seconds']} | {off['elapsed_seconds']} | |",
        f"| ON setting-level requests / cost | {on['setting_level_requests']} / {on['setting_level_cost_usd']:.6f} | | |",
        f"| ON case-attributed requests / cost | {on['case_attributed_requests']} / {on['case_attributed_cost_usd']:.6f} | | |",
        f"| Finish reasons | {on['finish_reasons']} | {off['finish_reasons']} | |",
        f"| Response models | {on['response_models']} | {off['response_models']} | |",
        f"| Guard refusals | | | {len(analysis['budget']['refusals'])} |",
        "",
        "## 4. Communication and Detector-v1 (ON only)",
        "",
        f"Episodes {analysis['detector']['episodes_total']} (scientifically complete {analysis['detector']['scientific_complete']}); classifications {analysis['detector']['classifications']}; signals {analysis['detector']['reason_codes']}; termination {analysis['detector']['termination_reasons']}; episodes per case {analysis['detector']['episodes_per_case']}; cases with no episode {analysis['detector']['cases_with_no_episode'] or 'none'}.",
        "",
        f"Routes: {json.dumps(on['routes'].get('routes', []))}",
        "",
        "## 5. Integrity bindings",
        "",
        "| Artifact | SHA-256 |",
        "|---|---|",
        f"| Frozen manifest | {analysis['manifest_sha256']} |",
        f"| Detector-v1 source | {manifest['detector_v1']['sha256']} |",
    ]
    for name, digest in manifest["conditions"][c.CONDITION_ON]["protected_runtime_sha256"].items():
        lines.append(f"| protected runtime {name} | {digest} |")
    lines.append(f"| OFF prompt template | {manifest['conditions'][c.CONDITION_OFF]['prompt_template_sha256']} |")
    lines += ["", "## 6. Validation of published values", ""]
    if validation:
        for key, value in validation.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- validation not run")
    lines += ["", "## 7. Human-review cards (private)", "", f"- {json.dumps(cards, sort_keys=True)}", ""]
    return "\n".join(lines)


def evidence_index(analysis: dict[str, Any], public_dir: Path, deliverables: dict[str, Path], private_bindings: dict[str, Any]) -> str:
    lines = [
        f"# Reproducibility and Evidence Index: `{analysis['run_id']}`",
        "",
        "Every published number is recomputable from the private evidence with",
        "`python scripts/study2_prospective_run.py validate --output-root <RUN_DIR> --public-aggregate <public-aggregate.json>`.",
        "",
        "## Public artifacts (committed)",
        "",
        "| Path | SHA-256 | Evidence class |",
        "|---|---|---|",
    ]
    for path in sorted(public_dir.glob("*")):
        if path.is_file():
            lines.append(f"| {path.as_posix().split('docs/')[-1] if 'docs/' in path.as_posix() else path.name} | {_sha(path)} | {analysis['evidence_class']} |")
    lines += ["", "## Deliverables (Downloads, not committed)", "", "| File | SHA-256 |", "|---|---|"]
    for _name, path in sorted(deliverables.items()):
        if path.is_file():
            lines.append(f"| {path.name} | {_sha(path)} |")
    lines += ["", "## Private evidence (never committed; digests bound in the receipt)", "", "| Item | Digest or location |", "|---|---|"]
    for key, value in private_bindings.items():
        lines.append(f"| {key} | {value} |")
    lines += ["", "## Frozen inputs", "", "| Item | Value |", "|---|---|",
              f"| Execution head | {analysis['execution_git_sha']} |",
              f"| Manifest SHA-256 | {analysis['manifest_sha256']} |",
              f"| Case ids | {', '.join(analysis['case_ids'])} |",
              "| Corpus | text2uml_airtravel_253b26dc @ 253b26dc704d523209a5cba79686f8f7fab57d63 |", ""]
    return "\n".join(lines)


def case_selection_receipt(selection: dict[str, Any], analysis: dict[str, Any]) -> str:
    lines = [
        "# Case-Selection Receipt",
        "",
        f"Run `{analysis['run_id']}`. Frame: {selection['frame']}. Corpus `{selection['corpus_id']}` @ `{selection['corpus_commit']}`; archive SHA-256 `{selection['archive_sha256']}`.",
        "",
        f"- Eligibility predicate: {selection['eligibility_predicate']}",
        f"- Eligible cases: {selection['eligible_case_count']}",
        f"- Selection rule: `{selection['selection_rule']}`",
        f"- Seed: {selection['selection_seed']}; sample size: {selection['sample_size']}",
        f"- Selected: {', '.join(selection['selected_case_ids'])}",
        f"- Excluded ({selection['excluded_reason']}): {', '.join(selection['excluded_case_ids'])}",
        f"- Overlap with Study 1 by digest (full-frame id -> Study 1 id): {selection['study1_overlap_by_digest'] or 'none'}",
        f"- Gate `selection_reproduced_from_seed`: {analysis['gates'].get('selection_reproduced_from_seed', {}).get('passed')}",
        f"- Gate `corpus_hashes_verified_at_load`: {analysis['gates'].get('corpus_hashes_verified_at_load', {}).get('passed')}",
        "",
        "| Case | Source generator model | Bytes | SHA-256 | Selected |",
        "|---|---|---|---|---|",
    ]
    selected = set(selection["selected_case_ids"])
    for row in selection["eligible_cases"]:
        lines.append(f"| {row['case_id']} | {row['source_generator_model']} | {row['bytes']} | {row['sha256']} | {'yes' if row['case_id'] in selected else 'no'} |")
    lines.append("")
    return "\n".join(lines)


def budget_spend_receipt(analysis: dict[str, Any], budget_doc: dict[str, Any]) -> str:
    b = analysis["budget"]
    cond = analysis["conditions"]
    lines = [
        "# Budget and Spend Receipt",
        "",
        f"Run `{analysis['run_id']}`, mode {analysis['mode']}.",
        "",
        "| Item | Reserved / frozen | Actual |",
        "|---|---|---|",
        f"| Hard ceiling (USD) | {b['hard_ceiling_usd']:.2f} | within: {b['within_hard_ceiling']} |",
        f"| Guard ceiling (USD) | {b['guard_ceiling_usd']:.2f} | spent {b['actual_cost_usd']:.6f} |",
        f"| Per-request reserve (USD) | {b['per_request_reserve_usd']:.7f} | |",
        f"| Whole-study reservation (USD) | {analysis['whole_study_reservation_usd']:.4f} | {b['actual_cost_usd']:.6f} ({(b['actual_cost_usd'] / analysis['whole_study_reservation_usd'] * 100) if analysis['whole_study_reservation_usd'] else 0:.1f}% of reservation) |",
        f"| Total request cap | {b['total_request_cap']} | {b['requests']} |",
        f"| VEGO_AI_ON request cap | {b['condition_request_caps'].get(c.CONDITION_ON)} | {b['requests_by_condition'].get(c.CONDITION_ON, 0)} |",
        f"| VEGO_AI_OFF request cap | {b['condition_request_caps'].get(c.CONDITION_OFF)} | {b['requests_by_condition'].get(c.CONDITION_OFF, 0)} |",
        f"| Prompt tokens | | {b['prompt_tokens']} |",
        f"| Completion tokens | | {b['completion_tokens']} |",
        f"| Transport errors (ON / OFF) | | {cond[c.CONDITION_ON]['transport_errors']} / {cond[c.CONDITION_OFF]['transport_errors']} |",
        f"| Retried requests (ON / OFF) | | {cond[c.CONDITION_ON]['retried_requests']} / {cond[c.CONDITION_OFF]['retried_requests']} |",
        f"| Guard refusals | | {len(b['refusals'])} {b['refusals'] if b['refusals'] else ''} |",
        f"| Pricing (USD per 1M tokens) | in {b['price_input_per_1m_usd']} / out {b['price_output_per_1m_usd']} | |",
        "",
        f"Chosen protocol: {budget_doc['chosen_option']['option']} — {budget_doc['decision']}",
        "",
        "Rules applied: " + "; ".join(budget_doc["rules"]) + ".",
        "",
    ]
    return "\n".join(lines)


def claims_table(analysis: dict[str, Any]) -> str:
    cond = analysis["conditions"]
    on, off = cond[c.CONDITION_ON], cond[c.CONDITION_OFF]
    det = analysis["detector"]
    rows = [
        ("Artifact completion", f"ON {on['completed']}/{on['planned']}, OFF {off['completed']}/{off['planned']}", analysis["evidence_class"], "PERMITTED (descriptive)"),
        ("Structural validity", f"ON {on['summary_consistent_count']} consistent of {on['completed']}; OFF {off['summary_consistent_count']} of {off['completed']}", analysis["evidence_class"], "PERMITTED (descriptive)"),
        ("Requests and cost", f"ON {on['requests']} req / {on['cost_usd']:.4f} USD; OFF {off['requests']} req / {off['cost_usd']:.4f} USD", analysis["evidence_class"], "PERMITTED (descriptive; not superiority)"),
        ("Elapsed time", f"ON {on['elapsed_seconds']} s; OFF {off['elapsed_seconds']} s", analysis["evidence_class"], "PERMITTED (descriptive; one day)"),
        ("Technical failures", f"ON {on['technical_failures']}, OFF {off['technical_failures']}", analysis["evidence_class"], "PERMITTED"),
        ("Communication evidence", f"ON {det['episodes_total']} episodes; OFF none by design", analysis["evidence_class"] + " / NOT_AVAILABLE (OFF)", "PERMITTED as availability, not as deficit"),
        ("Detector-v1 labels", f"{fmt_counts(det['classifications'])}", analysis["evidence_class"], "PERMITTED as candidate labels only"),
        ("Detector-v1 under OFF", "NOT_APPLICABLE", "NOT_APPLICABLE", "FORBIDDEN to report as zero alerts"),
        ("Alert correctness / precision / recall / F1", "no human labels", "NOT_MEASURED", "FORBIDDEN"),
        ("Human benefit / workload", "no raters yet", "NOT_MEASURED", "FORBIDDEN"),
        ("Quality superiority of either condition", "no ground truth, no rated quality", "NOT_MEASURED", "FORBIDDEN"),
        ("Generalisation beyond corpus/model/day", "single corpus, model, day", "NOT_AVAILABLE", "FORBIDDEN"),
        ("Preflight fixture behaviour", "harness exercised with fake provider", "ENGINEERING-ONLY FIXTURE", "PERMITTED as engineering evidence only"),
    ]
    lines = ["# Claims and Limitations Table", "", f"Run `{analysis['run_id']}`.", "", "| Claim | Observation | Evidence class | Status |", "|---|---|---|---|"]
    for claim, observation, evidence, status in rows:
        lines.append(f"| {claim} | {observation} | {evidence} | {status} |")
    lines += ["", "Limitations attached to every row: one public LLM-generated corpus; 12 seeded paired cases of 21; one model at the provider default temperature on one day; ON per-case cost and time are attributions under concurrency; structural metrics are not quality judgements; Detector-v1 labels are candidates, not confirmed problems.", ""]
    return "\n".join(lines)


def executive_summary(analysis: dict[str, Any]) -> str:
    cond = analysis["conditions"]
    on, off = cond[c.CONDITION_ON], cond[c.CONDITION_OFF]
    det = analysis["detector"]
    diff = analysis["differences"]
    return "\n".join([
        f"# Executive Summary: Study 2 Prospective Paired Run `{analysis['run_id']}`",
        "",
        f"**Evidence class:** {analysis['evidence_class']}. One prospective paired run of the VEGO-AI four-agent workflow (ON) against a matched direct single-model workflow (OFF) on {len(analysis['case_ids'])} seeded cases of the public Text2UML AirTravel frame (21 eligible), model {analysis['model']['model']}, hard ceiling 6.00 USD.",
        "",
        "## What happened",
        "",
        f"- Completion: ON {on['completed']}/{on['planned']} artifacts, OFF {off['completed']}/{off['planned']}; both completed in {diff['both_completed']} cases.",
        f"- Structural validity: ON {on['summary_consistent_count']}/{on['completed']} artifacts with a self-consistent coverage summary; OFF {off['summary_consistent_count']}/{off['completed']}.",
        f"- Requests: ON {on['requests']} (of which {on['setting_level_requests']} setting-level), OFF {off['requests']}; total {analysis['budget']['requests']} of cap {analysis['budget']['total_request_cap']}.",
        f"- Cost: ON {on['cost_usd']:.4f} USD, OFF {off['cost_usd']:.4f} USD; total {analysis['budget']['actual_cost_usd']:.4f} USD against a 5.8241 USD reservation and a 6.00 USD ceiling.",
        f"- Time: ON {on['elapsed_seconds']} s, OFF {off['elapsed_seconds']} s for the whole condition.",
        f"- Technical failures: ON {on['technical_failures']}, OFF {off['technical_failures']}; transport retries ON {on['retried_requests']}, OFF {off['retried_requests']}.",
        f"- Communication evidence: ON produced {det['episodes_total']} recorded Q&A episodes ({det['scientific_complete']} scientifically complete); OFF has none by design.",
        f"- Detector-v1 (ON only, reporting-only): {fmt_counts(det['classifications'])}; cases with any candidate label: {det['share_of_cases_with_any_candidate']}. Under OFF: NOT_APPLICABLE.",
        "",
        "## What this does and does not show",
        "",
        "It shows how the two workflows behaved operationally on the same inputs under identical request policy. It does not show which produced better analyses, whether any Detector-v1 label is correct, or anything about human benefit; those are NOT_MEASURED until two independent raters score the blinded cards.",
        "",
        "## Next step",
        "",
        f"Two raters score the {det['scientific_complete']} blinded cards with the Hebrew rubric; only then can agreement and any correctness-type statement be computed.",
        "",
    ])


def supervisor_email_he(analysis: dict[str, Any], pr_url: str | None, deliverable_dir: Path) -> str:
    cond = analysis["conditions"]
    on, off = cond[c.CONDITION_ON], cond[c.CONDITION_OFF]
    det = analysis["detector"]
    return "\n".join([
        "<div dir=\"rtl\" lang=\"he\">",
        "",
        "**נושא:** מחקר 2 — הושלמה ריצה פרוספקטיבית מזווגת ON/OFF (12 מקרים, תקרה 6$)",
        "",
        "שלום איריס וארנון,",
        "",
        f"הושלמה ריצה אחת, מאושרת מראש, של הניסוי המזווג VEGO-AI_ON לעומת VEGO-AI_OFF על {len(analysis['case_ids'])} מקרים שנבחרו בסיד קבוע מתוך 21 המודלים הכשירים בקורפוס הציבורי Text2UML AirTravel, עם המודל {analysis['model']['model']} ותקרת הוצאה קשיחה של 6.00 דולר.",
        "",
        "תמצית התוצאות (תיאוריות בלבד):",
        "",
        f"- שלמות פלט: ON {on['completed']} מתוך {on['planned']}, OFF {off['completed']} מתוך {off['planned']}.",
        f"- בקשות ועלות: ON {on['requests']} בקשות, {on['cost_usd']:.4f}$; OFF {off['requests']} בקשות, {off['cost_usd']:.4f}$. סה\"כ {analysis['budget']['actual_cost_usd']:.4f}$ מתוך 6.00$.",
        f"- זמן: ON {on['elapsed_seconds']:.0f} שניות, OFF {off['elapsed_seconds']:.0f} שניות לכל התנאי.",
        f"- ראיות תקשורת: ב-ON נרשמו {det['episodes_total']} אפיזודות שאלה–תשובה; ב-OFF אין כאלה מבנית.",
        f"- Detector-v1 (תווית דיווח בלבד, ON בלבד): {fmt_counts(det['classifications'])}. ב-OFF: לא רלוונטי (לא \"אפס התרעות\").",
        "",
        "מה אין כאן: אין טענת עדיפות, אין טענת נכונות של התרעות, ואין הערכת איכות — כל אלה במצב NOT_MEASURED עד שני מעריכים יסמנו את הכרטיסים העיוורים.",
        "",
        f"הצעד הבא המבוקש מכם: ניקוד עיוור של {det['scientific_complete']} כרטיסים לפי המחוון בעברית (כ-30–45 דקות לכל מעריך). לאחר מכן אחשב הסכמה ואציג את הממצאים.",
        "",
        f"החומרים: דוח עברי (8–10 עמודים), מצגת, תרשים מקצה לקצה, תקציר מנהלים ונספח טכני נמצאים בתיקייה `{deliverable_dir.name}`. " + (f"ה-PR (טיוטה, ללא מיזוג): {pr_url}" if pr_url else "ה-PR ייפתח כטיוטה ללא מיזוג."),
        "",
        "בברכה,",
        "עלי",
        "",
        "</div>",
        "",
    ])
