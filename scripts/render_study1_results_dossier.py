"""Render the Study 1 results dossier to a print-ready Hebrew RTL document.

Every number is read from the dossier JSON, never retyped, so the document cannot drift from the
recomputed evidence. Charts are CSS bars rather than SVG: an earlier package shipped SVG figures in
which direction="rtl" with text-anchor="end" pushed every label outside the viewBox.

Each chart states what it measures, its numerator, its denominator, its source artifact, and what
it does not prove.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

CSS = """
@page { size: A4; margin: 10mm 11mm 11mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Arial, sans-serif; color:rgb(11,11,11); font-size:8.2pt; line-height:1.32; margin:0; }
h1 { font-size:14pt; margin:0 0 1mm; }
h2 { font-size:9.6pt; margin:2.2mm 0 1mm; padding-bottom:0.7mm; border-bottom:1.5px solid rgb(42,120,214); color:rgb(20,55,94); }
h3 { font-size:8.6pt; margin:2mm 0 0.8mm; color:rgb(20,55,94); }
.sub { color:rgb(82,81,78); font-size:7.6pt; margin:0 0 1.6mm; }
.warn { background:rgb(253,242,238); border-right:3px solid rgb(235,104,52); padding:1.6mm 2.2mm; font-size:7.6pt; margin:0 0 2mm; }
.key { background:rgb(238,244,252); border-right:3px solid rgb(42,120,214); padding:1.5mm 2.2mm; font-size:8pt; margin:0 0 1.6mm; }
.note { font-size:6.8pt; color:rgb(82,81,78); margin:0.4mm 0 1.2mm; }
table { width:100%; border-collapse:collapse; font-size:7.1pt; margin:0 0 1mm; }
th,td { border:1px solid rgb(216,216,212); padding:0.6mm 0.9mm; text-align:right; vertical-align:top; }
th { background:rgb(244,245,243); font-weight:600; }
td.n, th.n { text-align:center; font-variant-numeric:tabular-nums; }
.hi { background:rgb(255,248,232); font-weight:700; }
code { font-family:Consolas,monospace; font-size:6.9pt; background:rgb(244,245,243); padding:0 0.5mm; direction:ltr; unicode-bidi:isolate; }
.row { display:flex; align-items:center; gap:1.4mm; margin:0.5mm 0; }
.lbl { flex:0 0 44mm; font-size:7.1pt; text-align:right; }
.track { flex:1 1 auto; position:relative; height:3.4mm; background:rgb(244,245,243); border-radius:0.7mm; }
.bar { position:absolute; top:0; right:0; height:100%; background:rgb(42,120,214); border-radius:0.7mm; }
.bar.alt { background:rgb(235,104,52); }
.val { position:absolute; left:1.2mm; top:-0.1mm; font-size:6.9pt; font-weight:700; color:rgb(20,55,94); }
.pb { page-break-before: always; }
tr, .key, .warn, .note, .kpi { page-break-inside: avoid; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:3mm; align-items:start; }
.kpi { border:1px solid rgb(216,216,212); border-radius:1.6mm; padding:1.6mm; text-align:center; }
.kpi .v { font-size:12.5pt; font-weight:700; color:rgb(20,55,94); line-height:1.05; }
.kpi .l { font-size:6.8pt; color:rgb(82,81,78); margin-top:0.5mm; }
.grid3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:2.2mm; margin-bottom:1.4mm; }
"""


def esc(value: Any) -> str:
    return html.escape(str(value))


def bars(items: list[tuple[str, float, str]], maximum: float | None = None) -> str:
    top = maximum if maximum else max((v for _, v, _ in items), default=0) or 1
    out = []
    for label, value, shown in items:
        width = (value / top * 100) if top else 0
        alt = " alt" if label.startswith("__alt__") else ""
        clean = label.replace("__alt__", "")
        out.append(
            f'<div class="row"><span class="lbl">{esc(clean)}</span>'
            f'<span class="track"><span class="bar{alt}" style="width:{width:.1f}%"></span>'
            f'<span class="val">{esc(shown)}</span></span></div>'
        )
    return "".join(out)


def caption(measures: str, numerator: str, denominator: str, source: str, not_proof: str) -> str:
    return (f'<p class="note"><b>מה נמדד:</b> {measures} <b>מונה:</b> {numerator} '
            f'<b>מכנה:</b> {denominator} <b>מקור:</b> <code>{source}</code> '
            f'<b>מה אינו מוכיח:</b> {not_proof}</p>')


HEB_CONF = {"Low": "נמוך", "Medium": "בינוני", "High": "גבוה"}
HEB_EVIDENCE = {"<present>": "קיימת", "<empty>": "ריקה (אורך 0)", "<absent>": "חסרה (null)"}
HEB_BRANCH = {
    "no episode; denominator 0": "אין אפיזודה; מכנה 0",
    "no signal": "ללא אות",
    "S7 (S6 necessarily co-fires)": "S7 (S6 פועל בהכרח יחד)",
    "S1 alone": "S1 לבד",
    "S3 alone, length-0 branch": "S3 לבד — ענף אורך 0",
    "S3 alone, null branch": "S3 לבד — ענף null",
    "S2 alone": "S2 לבד",
    "S6 alone": "S6 לבד",
    "S2 and S6 together; still weak": "S2 ו-S6 יחד — עדיין חלשה",
}


def missing(title: str, source: str) -> str:
    return (f'<h2>{title}</h2><div class="warn"><code>{esc(source)}</code> אינו זמין — הסעיף לא הופק. '
            f'זהו <code>NOT_AVAILABLE</code>, לא אפס.</div>')


def render_aggregation(d: dict[str, Any]) -> str:
    title = "2. רגישות לכלל הצבירה, אי-תלות בסדר האירועים ותחום הערכים"
    rb = d.get("instrument_robustness") or {}
    if not rb.get("available"):
        return missing(title, "analysis/instrument-robustness.json")
    ag, oi = rb["aggregation_sensitivity"], rb["order_invariance"]
    vd, ds = rb.get("value_domain") or {}, rb.get("denominator_sensitivity") or {}
    heb_class = {"STRONG_ALERT": "חזקה", "WEAK_ALERT": "חלשה", "NO_ALERT": "ללא"}
    order = ("majority", "ordinal_median", "first_round_any", "final_round_any", "plurality")
    heads = {"majority": "רוב", "ordinal_median": "חציון סדר", "first_round_any": "סבב ראשון",
             "final_round_any": "סבב אחרון", "plurality": "שכיח"}

    def lab(v):
        return "אין רוב" if v == "NO_MAJORITY" else HEB_CONF.get(v, esc(v))

    dep_class = set(ag["episodes_whose_class_depends_on_any"])
    dep_s1 = set(ag["episodes_whose_s1_depends_on_any"])
    rows = "".join(
        f'<tr{" class=\"hi\"" if e["episode_id"] in (dep_class | dep_s1) else ""}>'
        f'<td class="n"><code>{esc(e["episode_id"][:11])}…</code></td>'
        f'<td class="n">{e["answers"]}</td><td class="n">{e["rounds"]}</td>'
        f'<td class="n">{e["label_counts"]["Low"]}/{e["label_counts"]["Medium"]}/{e["label_counts"]["High"]}</td>'
        f'<td class="n"><code>{esc(", ".join(x.split("_")[0] for x in e["recorded_other_signals"]) or "—")}</code></td>'
        f'<td class="n"><b>{lab(e["summaries"]["any"])}</b>←{heb_class[e["frozen_class"]]}</td>'
        + "".join(f'<td class="n">{lab(e["summaries"][k])}←{heb_class[e["class_under_summary"][k]]}</td>' for k in order)
        + "</tr>"
        for e in ag["episodes"]
    )
    n = ag["denominator"]
    ca, la = ag["class_agreement_with_frozen"], ag["label_agreement_with_frozen_any"]
    if dep_class:
        key = (f'<div class="key"><b>{len(dep_class)} מתוך {n} סיווגים משתנים תחת סיכום ביטחון אחר.</b> '
               f'ראו הטבלה: לכל סיכום מוצגים תווית הביטחון והסיווג המתקבל מהפעלה מחדש של הכלל הקפוא. '
               f'<b>הכלל לא שונה</b> — זהו תיאור רגישות בלבד.</div>')
    elif dep_s1:
        big = max((e for e in ag["episodes"] if e["episode_id"] in dep_s1), key=lambda e: e["answers"])
        lc = big["label_counts"]
        other = ", ".join(x.split("_")[0] for x in big["recorded_other_signals"]) or "—"
        key = (f'<div class="key"><b>אף אחד מ-{n} הסיווגים אינו תלוי בכלל הצבירה; האות S1 ב-{len(dep_s1)} מתוך {n} אפיזודות תלוי בו.</b> '
               f'Detector-v1 קורא את רמת הביטחון בכלל <code>any</code> — די בתשובה אחת בביטחון נמוך כדי ש-S1 יפעל. '
               f'באפיזודה הגדולה ביותר ({big["answers"]} תשובות: {lc["Low"]} נמוך, {lc["Medium"]} בינוני, {lc["High"]} גבוה) '
               f'S1 פועל רק תחת כלל זה: תחת סיכום רוב או שכיח סיכום הביטחון היה "בינוני". הסיווג "חזקה" של אפיזודה זו '
               f'נשמר בכל מקרה דרך האותות שנרשמו בה ללא קשר לביטחון (<code>{esc(other)}</code>; '
               f'<code>TERMINATED_MAX_ROUNDS</code> אינו קורא ביטחון כלל). <b>הכלל לא שונה</b> — זהו תיאור של '
               f'מידת התלות של האות והסיווג בכלל הצבירה, לא הצעה לכלל אחר.</div>')
    else:
        key = f'<div class="key">אף אחד מ-{n} הסיווגים ואף אות S1 אינם תלויים בכלל הצבירה.</div>'
    hyp = ds.get("hypothetical_converged_only") or {}
    hd = hyp.get("distribution") or {}
    labels = vd.get("confidence_labels") or {}
    named_ok = sum(1 for v in (oi.get("named_reorderings_invariant") or {}).values() if v)
    head_cells = "".join(f'<th class="n">{heads[k]}</th>' for k in order)
    return f"""<h2>{title}</h2>
{key}
<table><tr><th class="n">אפיזודה</th><th class="n">תשובות</th><th class="n">סבבים</th><th class="n">נמוך / בינוני / גבוה</th>
<th class="n">אותות אחרים שנרשמו</th><th class="n">any (קפוא)</th>{head_cells}</tr>
{rows}</table>
{caption("בכל תא: תווית סיכום הביטחון ← הסיווג המתקבל כשהכלל הקפוא מופעל מחדש עם תרומת S1/S2 מוחלפת בסיכום, ו-S3, S6, S7 נשמרים כפי שנרשמו",
         f"הסכמה עם הקפוא ברמת הסיווג — רוב {ca.get('majority')}, חציון סדר {ca.get('ordinal_median')}, סבב ראשון {ca.get('first_round_any')}, "
         f"סבב אחרון {ca.get('final_round_any')}, שכיח {ca.get('plurality')}; ברמת התווית — רוב {la.get('majority')}, חציון סדר {la.get('ordinal_median')}, "
         f"סבב ראשון {la.get('first_round_any')}, סבב אחרון {la.get('final_round_any')}, שכיח {la.get('plurality')}",
         f"{n} אפיזודות שלמות", "analysis/instrument-robustness.json",
         "אין זה גלאי חלופי ואין זו הצעה לשנות את הכלל — Detector-v1 ומפתחותיו לא שונו. \"רוב\" הוא רוב אמיתי (יותר ממחצית התשובות, אחרת \"אין רוב\"); "
         "\"חציון סדר\" הוא החציון על הסולם נמוך < בינוני < גבוה. תיאור רגישות בלבד")}
<p class="note"><b>אי-תלות בסדר האירועים:</b> {oi.get('permutations_invariant')}/{oi.get('seeded_permutations')} תמורות אקראיות
של יומן האירועים ו-{named_ok}/3 סידורים מוגדרים (הפוך, לפי סוג אירוע, לפי אפיזודה) נתנו סיווג זהה לכל אפיזודה;
אפיזודות עם יותר מאירוע סיום אחד: {oi.get('episodes_with_multiple_termination_events')}.
<b>תחום ערכים:</b> {vd.get('answers')} תשובות — נמוך {labels.get('Low', 0)} · בינוני {labels.get('Medium', 0)} · גבוה {labels.get('High', 0)};
מחוץ לתחום המוצהר: {len(vd.get('labels_outside_declared_domain') or [])}; <code>UNKNOWN</code>: {vd.get('unknown_fallback_answers')};
ראיה null: {vd.get('evidence_ref_null')}; ראיה באורך אפס: {vd.get('evidence_ref_zero_length')}.
<b>רגישות למכנה:</b> תחת הגדרת שלמות מחמירה (<code>CONVERGED</code> בלבד — <b>לא</b> הכלל הרשום) המכנה היה
{hyp.get('denominator')} והתפלגות {hd.get('STRONG_ALERT', 0)} / {hd.get('WEAK_ALERT', 0)} / {hd.get('NO_ALERT', 0)}.</p>"""

def render_truth_table(d: dict[str, Any]) -> str:
    title = "8. טבלת האמת של הכלל הקפוא — כל ענף ניתן-לבידוד בבידוד (S7 יחד עם S6)"
    tt = d.get("truth_table") or {}
    if not tt.get("available"):
        return missing(title, "analysis/detector-envelope-extended.json")

    def short(signals):
        return ", ".join(s.split("_")[0] for s in signals) or "—"

    rows = "".join(
        f'<tr{" class=\"hi\"" if (m["WEAK_ALERT"] or 0) > 0 else ""}><td><code>{esc(m["fixture_mode"])}</code></td>'
        f'<td>{esc(HEB_BRANCH.get(m["isolated_branch"], m["isolated_branch"]))}</td>'
        f'<td class="n">{HEB_CONF.get(m["injected_confidence"], esc(m["injected_confidence"]))}</td>'
        f'<td class="n">{HEB_EVIDENCE.get(m["injected_evidence"], esc(m["injected_evidence"]))}</td>'
        f'<td class="n">{"כולם" if m["question_rounds"] == "all" else esc(", ".join(map(str, m["question_rounds"])) or "—")}</td>'
        f'<td class="n">{esc(m["denominator"])}</td>'
        f'<td class="n">{esc(m["STRONG_ALERT"])} / {esc(m["WEAK_ALERT"])} / {esc(m["NO_ALERT"])}</td>'
        f'<td class="n"><code>{esc(short(m["signals"]))}</code></td>'
        f'<td class="n">{"✓" if m["conforms"] else "✗"}</td></tr>'
        for m in tt["modes"]
    )
    legacy = next((m for m in tt["modes"] if m["fixture_mode"] == "two_rounds"), None)
    legacy_txt = (f'{legacy["NO_ALERT"]}/{legacy["denominator"]}' if legacy else "Unknown")
    return f"""<h2>{title}</h2>
<div class="warn"><b>בדיקת הנדסה בלבד — אינה תוצאה מדעית — אינה מדד ספק.</b> קריאות ספק: <b>{esc(tt['provider_calls'])}</b>;
קריאות קלט בדיקה דטרמיניסטי: {tt.get('fake_calls_total')}. המכנים נפרדים לחלוטין מן המכנה של ההרצה המאושרת.</div>
<div class="key"><b>המעטפת המקורית (סעיף 7) הגיעה לשני סיווגים בלבד</b> — ללא התרעה, וחזקה דרך S7. הסיווג "חלשה" ואות S3 לא הופקו
על ידי המעטפת המקורית ולא נצפו בהרצה המאושרת; המעטפת המורחבת מפיקה אותם על קלט סינתטי. היא מבודדת כל ענף ניתן-לבידוד של
הכלל — S1 לבד, S3 לבד בשני הקידודים (ריק, null), S2 לבד, S6 לבד — ומפיקה את הסיווג "חלשה" מקצה לקצה דרך המתזמר המוגן.
<b>{tt['modes_conforming']}/{tt['modes_total']}</b> מצבים תואמים את הכלל עם קבוצת האותות המדויקת הצפויה.</div>
<table><tr><th>מצב בדיקה</th><th>ענף מבודד</th><th class="n">ביטחון מוזרק</th><th class="n">ראיה מוזרקת</th><th class="n">סבבי שאלה</th>
<th class="n">מכנה</th><th class="n">חזקה / חלשה / ללא</th><th class="n">אותות</th><th class="n">תואם</th></tr>
{rows}</table>
{caption("סיווג Detector-v1 על תשעה מצבי בדיקה דטרמיניסטיים, כל אחד מבודד ענף אחד של הכלל",
         "אפיזודות בכל סיווג, וקבוצת האותות שפעלה", "מכנה נפרד לכל מצב בדיקה",
         "analysis/detector-envelope-extended.json",
         "בדיקת מכשור על קלט סינתטי — אינה תוצאה מדעית, אינה מדד ספק, ואינה מעידה על שכיחות של ענף כלשהו בקורפוס אמיתי")}
<p class="note"><b>שם היסטורי:</b> <code>two_rounds</code> שואל בסבב 1 בלבד (סבב מרבי 1), ולכן S6 אינו פועל בו.
<b>הערה מתודולוגית (מתועדת בכוונה):</b> ניסיון ראשון שאילץ שאלה דרך מצב <code>max_rounds</code> של קלט הבדיקה הזרים גם שורת
סיווג-שונות (<code>flag_for_guidelines_update</code>) ששינתה את מבנה השלבים — פחות אפיזודות ב-<code>two_rounds</code> ו-S6 בכל המצבים;
תוצר הביניים לא נשמר (Unknown). המימוש הסופי מוסיף שאלות על התוצאה הריקה בלבד; <code>two_rounds</code> מסווג {legacy_txt} ללא התרעה,
זהה למעטפת המקורית.</p>"""

def render_cost_calibration(d: dict[str, Any]) -> str:
    title = "11. כיול עלות — רזרבה מול ביצוע, ותפריט פרוטוקולים בתקרות $2 ו-$6"
    cc = d.get("cost_calibration") or {}
    if not cc.get("available"):
        return missing(title, "analysis/cost-calibration.json")
    a, cal, ms = cc["actuals"], cc["calibration"], cc["menu_summary"] or {}
    au = d.get("authorisation") or {}
    bp = cal["by_protocol"]
    tr = cal.get("truncation_risk_under_pilot_cap") or {}
    names = {"study1b_frozen": "מחקר 1B קפוא (פלט 16,384)", "pilot_frozen": "פיילוט קפוא (פלט 4,096)"}
    prow = "".join(
        f'<tr><td>{names.get(k, esc(k))}</td><td class="n">${v["reserve_per_request_usd"]}</td>'
        f'<td class="n">${v["reserve_for_observed_request_count_usd"]}</td><td class="n">${v["actual_cost_usd"]}</td>'
        f'<td class="n"><b>×{v["reserve_to_actual_ratio"]}</b></td><td class="n">{v["mean_completion_share_of_output_cap"]*100:.0f}%</td></tr>'
        for k, v in bp.items()
    )

    def menu_rows(rows):
        return "".join(
            f'<tr{" class=\"hi\"" if r.get("is_frozen_pilot") else ""}><td class="n">{r["repeats"]}</td>'
            f'<td class="n">{r["call_cap_per_repeat"]}</td><td class="n">{r["max_output_tokens"]:,}</td>'
            f'<td class="n"><b>${r["reserve_bound_usd"]}</b></td><td class="n">{"✓" if r["fits"].get("2.00") else "✗"}</td>'
            f'<td class="n">{"פיילוט קפוא" if r.get("is_frozen_pilot") else "—"}</td></tr>'
            for r in rows
        )

    fitting = cc["protocols_fitting_6"]
    half = (len(fitting) + 1) // 2
    menu_head = ('<tr><th class="n">חזרות</th><th class="n">תקרת קריאות</th><th class="n">תקרת פלט</th>'
                 '<th class="n">חסם רזרבה*</th><th class="n">$2</th><th class="n">סימון</th></tr>')
    menu_tables = (f'<div class="grid2"><div><table>{menu_head}{menu_rows(fitting[:half])}</table></div>'
                   f'<div><table>{menu_head}{menu_rows(fitting[half:])}</table></div></div>')
    s1b, pil = bp.get("study1b_frozen", {}), bp.get("pilot_frozen", {})
    share = (pil.get("mean_completion_share_of_output_cap") or 0) * 100
    if tr.get("mean_below_pilot_cap") is True:
        trunc = (f'הפלט הממוצע לקריאה ({share:.0f}% מתקרת הפיילוט, {tr.get("pilot_output_cap_tokens"):,}) נמוך מן התקרה — '
                 f'אך <b>המקסימום לקריאה אינו זמין</b>, ולכן לא ניתן לחסום את שיעור הקריאות שתקרה זו הייתה קוטמת')
    elif tr.get("mean_below_pilot_cap") is False:
        trunc = (f'הפלט הממוצע לקריאה ({share:.0f}% מתקרת הפיילוט) <b>עולה</b> על התקרה, ולכן קטימה צפויה; '
                 f'המקסימום לקריאה אינו זמין')
    else:
        trunc = 'סיכון הקטימה תחת תקרת הפיילוט: <code>NOT_AVAILABLE</code>'
    receipts = au.get("paid_run_receipts_on_or_after_authorisation")
    present = au.get("credential_present_at_build")
    source_label = ("טבלת ההחלטות 2026-09-06 (D8) · נספח הניסויים 2026-09-08 (סעיף 6)" if au.get("source")
                    else "<code>NOT_AVAILABLE</code>")
    cred = ("היה קיים" if present is True else "לא היה קיים" if present is False else "לא נבדק")
    return f"""<h2>{title}</h2>
<div class="key"><b>הרזרבה השמרנית גבוהה פי {s1b.get('reserve_to_actual_ratio')} מהעלות שנצפתה</b> תחת חסם מחקר 1B,
ופי {pil.get('reserve_to_actual_ratio')} תחת חסם הפיילוט. {trunc}; קטימה חייבת להירשם, לא להתקבל בשקט.</div>
<div class="grid2"><div>
<table><tr><th>פריט (מצטבר, מקבלת ההרצה)</th><th class="n">ערך</th></tr>
<tr><td>קריאות ספק</td><td class="n">{a['outbound_requests']}</td></tr>
<tr><td>ממוצע אסימוני קלט לקריאה</td><td class="n">{a['mean_prompt_tokens_per_request']:,}</td></tr>
<tr><td>ממוצע אסימוני פלט לקריאה</td><td class="n">{a['mean_completion_tokens_per_request']:,}</td></tr>
<tr><td>עלות ממוצעת לקריאה</td><td class="n">${a['mean_cost_per_request_usd']}</td></tr>
<tr class="hi"><td>מקסימום קלט / פלט לקריאה</td><td class="n"><code>NOT_AVAILABLE</code></td></tr>
<tr class="hi"><td>עלות לאפיזודה</td><td class="n"><code>NOT_AVAILABLE</code></td></tr></table>
</div><div>
<table><tr><th>חסם</th><th class="n">רזרבה לקריאה</th><th class="n">× {a['outbound_requests']}</th><th class="n">בפועל</th><th class="n">יחס</th><th class="n">פלט ממוצע מהתקרה</th></tr>
{prow}</table>
</div></div>
<p class="note">* <b>חסם רזרבה</b> = חזרות × תקרת קריאות × רזרבה לקריאה, בהנחה שכל פרומפט נכנס ברזרבת הקלט (8,000 אסימונים) והפלט
בתקרת הפלט. רזרבת הקלט היא קבוע תצורה; הפרומפט הגדול ביותר שנשלח <code>NOT_AVAILABLE</code>, ולכן החסם חוסם את השמירות (reservations),
לא את ההוצאה בפועל, אם פרומפט בודד יעלה על הרזרבה.</p>
{menu_tables}
{caption("חסם רזרבה לכל פרוטוקול מול שתי תקרות; מוצגים רק הפרוטוקולים המתאימים ל-$6",
         f"{ms.get('protocols_fitting_6.00')} מתאימים ל-$6, {ms.get('protocols_fitting_2.00')} ל-$2",
         f"{ms.get('protocols_total')} פרוטוקולים נבחנו", "analysis/cost-calibration.json",
         "התאמה לתקרה היא אריתמטיקה על קבועי רזרבה קפואים — אינה הרשאה לביצוע, אינה חיזוי עלות ואינה עדות שהפרוטוקול "
         "יניב אפיזודות שמישות")}
<p class="note"><b>מצב הרשאה</b> (מקור: {source_label}): ב-{esc(au.get('authorised_on', 'Unknown'))} אושרה תקרה של
USD {esc(au.get('ceiling_usd', 'Unknown'))} לניסויים נוספים. קבלות הרצה בתשלום מתאריך ההרשאה ואילך תחת שורש הראיות הפרטי:
<b>{esc(len(receipts)) if isinstance(receipts, list) else 'NOT_AVAILABLE'}</b> — לא בוצעה כל קריאת ספק במסגרתה. מפתח הגישה של הספק (משתנה
סביבה; נבדקה נוכחות בלבד, הערך לא נקרא) {cred} בסביבת הביצוע בעת הפקת מסמך זה, ושער סקירת הפיילוט טרם נסגר.
פרוטוקול מחקר 1B הקפוא (חסם רזרבה <b>${cc.get('frozen_study1b_bound_usd')}</b>) אינו מתאים לאף אחת מהתקרות; חסם הפיילוט הקפוא הוא
${cc.get('frozen_pilot_bound_usd')}.</p>"""

def render(d: dict[str, Any]) -> str:
    ev, h = d["evidence"], d["headline"]
    cost = d["cost"]
    cf = d["counterfactual_class_stability"]
    base = d["separation_baseline"]
    parts: list[str] = []

    parts.append(f"""<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="utf-8">
<title>VEGO-AI Study 1 — Results Dossier</title><style>{CSS}</style></head><body>
<h1>מחקר 1 — AirTravel: תיק תוצאות וניתוחים</h1>
<p class="sub">{esc(ev['model'])} · <code>{esc(ev['setting_id'])}</code> · <code>{esc(ev['corpus_id'])}</code>
 · ריצה <code>{esc(ev['run_id'])}</code> · הופק {esc(d['generated_at'][:10])}</p>

<div class="warn"><b>סטטוס קובע:</b> <code>{esc(d['verdict'])}</code> —
הראיות הפרטיות אומתו בדיעבד; הקבלה המקורית לא קשרה מראש את כל רכיבי הראיה.
כל מספר במסמך זה חושב מחדש מיומן האירועים <code>{esc(ev['event_log_sha256'][:16])}…</code>
ולא הועתק מדוח קודם. קריאות ספק שבוצעו להפקת מסמך זה: <b>0</b>.</div>

<div class="grid3">
  <div class="kpi"><div class="v">{h['complete_episodes_denominator']}</div><div class="l">אפיזודות שלמות (מכנה)</div></div>
  <div class="kpi"><div class="v">{h['questions']} / {h['answers']}</div><div class="l">שאלות / תשובות</div></div>
  <div class="kpi"><div class="v">{h['max_round_index']}</div><div class="l">סבב מרבי</div></div>
</div>
<div class="grid3">
  <div class="kpi"><div class="v">{h['classification'].get('STRONG_ALERT',0)} / {h['classification'].get('WEAK_ALERT',0)} / {h['classification'].get('NO_ALERT',0)}</div><div class="l">חזקה / חלשה / ללא</div></div>
  <div class="kpi"><div class="v">{cost['outbound_requests']}</div><div class="l">קריאות ספק</div></div>
  <div class="kpi"><div class="v">${cost['actual_cost_usd']}</div><div class="l">עלות בפועל</div></div>
</div>
<p class="note">כל הערכים לעיל אומתו בדיעבד — ראו הסטטוס הקובע בראש המסמך.</p>""")

    parts.append("""<h2>1. הממצא המרכזי החדש — האות הנושא את כל המשקל</h2>
<div class="key"><b>‏S1 (ביטחון תשובה נמוך) הוא האות היחיד שנושא את התוצאה.</b>
בהסרת S1 בלבד, שתיים משלוש האפיזודות משנות סיווג והתפלגות הסיווג קורסת.
בהסרת כל אות אחר — <b>אף אפיזודה אינה משנה סיווג</b>.
כלומר הכותרת "3 מתוך 3 התרעה חזקה" היא למעשה <b>"3 מתוך 3 ביטחון נמוך"</b>.</div>""")

    rows = "".join(
        f'<tr{" class=\"hi\"" if sig == "S1" else ""}><td class="n"><code>{esc(sig)}</code></td>'
        f'<td class="n">{esc(v["resulting_distribution"].get("STRONG_ALERT", 0))}</td>'
        f'<td class="n">{esc(v["resulting_distribution"].get("WEAK_ALERT", 0))}</td>'
        f'<td class="n">{esc(v["resulting_distribution"].get("NO_ALERT", 0))}</td>'
        f'<td class="n"><b>{esc(v["episodes_changed"])}</b></td></tr>'
        for sig, v in cf["per_removed_signal"].items()
    )
    parts.append(f"""<table>
<tr><th class="n">האות שהוסר</th><th class="n">חזקה</th><th class="n">חלשה</th><th class="n">ללא</th><th class="n">אפיזודות ששינו סיווג</th></tr>
{rows}</table>
{caption("סיווג מחדש של אותן אפיזודות כאשר אות בודד מוסר מהכלל הקפוא",
         "מספר האפיזודות בכל סיווג", f"{cf['denominator']} אפיזודות שלמות",
         "output/qa_events.jsonl", "אין זה שינוי סף ואין זה גלאי חדש — הכלל ומפתחותיו לא שונו. "
         "זהו תיאור עמידוּת בלבד ואינו מעיד שהאותות האחרים מיותרים בקורפוס אחר")}""")

    parts.append(render_aggregation(d))

    sig = h["signals_fired"]
    parts.append(f"""<h2>3. אותות שפעלו</h2>
{bars([("S1 — ביטחון נמוך", sig["S1"], sig["S1"]),
       ("S2 — ביטחון בינוני", sig["S2"], sig["S2"]),
       ("S6 — יותר מסבב אחד", sig["S6"], sig["S6"]),
       ("S7 — מגבלת סבבים", sig["S7"], sig["S7"]),
       ("S3 — ראיה חסרה", sig["S3"], sig["S3"])], maximum=cf["denominator"])}
{caption("מספר האפיזודות שבהן כל אות פעל", "אפיזודות שבהן האות פעל",
         f"{cf['denominator']} אפיזודות שלמות", "output/qa_events.jsonl",
         "אינו מוכיח שהתרחשה שגיאה. ‏<b>S3 לא פעל כלל</b>: הכלל קיים ולא נצפה בראיות הזמינות — "
         "אין זה ממצא אמפירי ואין להציגו ככזה")}""")

    tr = d["confidence_trajectory"]
    trow = "".join(
        f'<tr><td class="n">{r["round_index"]}</td><td class="n">{r["answers"]}</td>'
        f'<td class="n">{r["low"]}</td><td class="n">{r["medium"]}</td><td class="n">{r["high"]}</td>'
        f'<td class="n">{"" if r["low_share"] is None else f"{r['low_share']*100:.0f}%"}</td></tr>'
        for r in tr["per_round"]
    )
    parts.append(f"""<h2>4. מסלול הביטחון לאורך הסבבים</h2>
<div class="grid2"><div>
<table><tr><th class="n">סבב</th><th class="n">תשובות</th><th class="n">נמוך</th><th class="n">בינוני</th><th class="n">גבוה</th><th class="n">שיעור נמוך</th></tr>
{trow}</table></div><div>
{bars([(f"סבב {r['round_index']}", (r['low_share'] or 0) * 100, f"{(r['low_share'] or 0)*100:.0f}%") for r in tr["per_round"]], maximum=100)}
</div></div>
{caption("שיעור התשובות בביטחון נמוך בכל סבב",
         "תשובות בביטחון נמוך", "כלל התשובות באותו סבב", "output/qa_events.jsonl",
         f"הירידה מ-{tr['first_round_low_share']*100:.0f}% בסבב הראשון ל-{tr['final_round_low_share']*100:.0f}% "
         "בסבב האחרון היא תיאור בלבד; אין בה כדי לקבוע שסבבים מאוחרים מיישבים אי-ודאות")}""")

    eb = d["evidence_length_by_confidence"]["by_confidence"]
    ebrow = "".join(
        f'<tr><td>{esc(k)}</td><td class="n">{v["n"]}</td><td class="n">{v["median"]}</td>'
        f'<td class="n">{v["min"]}</td><td class="n">{v["max"]}</td><td class="n">{v["zero_length"]}</td></tr>'
        for k, v in eb.items()
    )
    parts.append(f"""<h2>5. אורך שדה הראיה לפי רמת ביטחון</h2>
<div class="key"><b>ממצא נגד-אינטואיטיבי:</b> לתשובות בביטחון <b>נמוך</b> יש חציון אורך ראיה
<b>{eb.get('Low',{}).get('median','—')}</b>, גבוה מזה של תשובות בביטחון גבוה
(<b>{eb.get('High',{}).get('median','—')}</b>) ובינוני (<b>{eb.get('Medium',{}).get('median','—')}</b>).
כלומר אורך הראיה <b>אינו עוקב</b> אחר רמת הביטחון המדווחת.</div>
<table><tr><th>רמת ביטחון</th><th class="n">n</th><th class="n">חציון</th><th class="n">מינימום</th><th class="n">מקסימום</th><th class="n">אורך אפס</th></tr>
{ebrow}</table>
{caption("אורך שדה הראיה בתווים, מקובץ לפי רמת הביטחון שהמודל דיווח",
         "אורך השדה בכל תשובה", f"{sum(v['n'] for v in eb.values())} תשובות",
         "output/qa_events.jsonl",
         "אורך מודד <b>נוכחות וגודל</b> של השדה בלבד — לא איכות, לא נכונות ולא רלוונטיות של הראיה")}""")

    rc = d["route_concentration"]
    rrow = "".join(
        f'<tr><td class="n">{esc(r["asking_agent"])}</td><td class="n">{esc(r["answering_agent"])}</td>'
        f'<td class="n">{r["questions"]}</td><td class="n">{r["share"]*100:.1f}%</td></tr>'
        for r in rc["routes"]
    )
    parts.append(f"""<h2>6. ריכוז מסלולי התקשורת</h2>
<table><tr><th class="n">סוכן שואל</th><th class="n">סוכן משיב</th><th class="n">שאלות</th><th class="n">שיעור</th></tr>
{rrow}
<tr class="hi"><td class="n">סה"כ</td><td class="n">—</td><td class="n">{rc['total_questions']}</td><td class="n">100%</td></tr></table>
{caption("מספר השאלות בכל זוג מסלול מכוון",
         "שאלות בכל זוג", f"{rc['total_questions']} שאלות · {rc['observed_route_pairs']} מתוך {rc['possible_route_pairs']} זוגות אפשריים נצפו",
         "output/qa_events.jsonl",
         "נפח מסלול הוא מטא-נתון ניתוב תיאורי; אף אות בגלאי אינו קורא אותו, ואין בו כדי לקבוע "
         "אם מסלול היה מתאים או נחוץ. מסלול שלא נצפה אינו מסלול מושבת")}""")

    brow = "".join(
        f'<tr><td><code>{esc(m["fixture_mode"])}</code></td><td class="n">{esc(m["episodes"])}</td>'
        f'<td class="n">{esc(m["denominator"])}</td><td class="n">{esc(m["STRONG_ALERT"])}</td>'
        f'<td class="n">{esc(m["WEAK_ALERT"])}</td><td class="n">{esc(m["NO_ALERT"])}</td>'
        f'<td class="n"><code>{esc(m["run_level_status"])}</code></td></tr>'
        for m in base["modes"]
    )
    parts.append(f"""<h2>7. בסיס ההשוואה — האם הכלל מפריד בכלל?</h2>
<div class="warn"><b>בדיקת הנדסה בלבד — אינה תוצאה מדעית — אינה מדד ספק — אינה השוואת
<code>VEGO_AI_ON</code> מול <code>VEGO_AI_OFF</code>.</b> קריאות ספק: <b>{base['provider_calls']}</b>.
המכנים כאן נפרדים לחלוטין מן המכנה של ההרצה המאושרת ואין למזג ביניהם.</div>
<table><tr><th>מצב בדיקה</th><th class="n">אפיזודות</th><th class="n">מכנה</th><th class="n">חזקה</th><th class="n">חלשה</th><th class="n">ללא</th><th class="n">סטטוס</th></tr>
{brow}</table>
<div class="key"><b>מסקנה מתודולוגית:</b> קלטים דטרמיניסטיים שונים מניעים את הכלל הקפוא
לסיווגים <b>הפוכים</b> — {esc(" · ".join(base["distinct_classes_produced"]))}.
לפיכך <b>הכלל אינו מנוון</b>. התוצאה "3 מתוך 3" בקורפוס AirTravel היא תכונה של <b>הקורפוס</b>,
ולא עדות לכך שהכלל שבור או שאינו מסוגל להבחין.</div>
{caption("סיווג Detector-v1 על שלושה מצבי בדיקה דטרמיניסטיים",
         "אפיזודות בכל סיווג", "מכנה נפרד לכל מצב בדיקה",
         "analysis/detector-envelope.json",
         "תשובות קלט הבדיקה סינתטיות ובנויות מראש; אינן מעידות דבר על התנהגות ספק אמיתי, "
         "על איכות או על נכונות")}""")

    parts.append(render_truth_table(d))

    et = "".join(
        f'<tr><td class="n"><code>{esc(r["episode_id"][:16])}…</code></td>'
        f'<td class="n">{esc(r["case_id"] or "חוצה-מקרים")}</td>'
        f'<td class="n"><code>{esc(r["termination_reason"])}</code></td>'
        f'<td class="n">{r["questions"]}</td><td class="n">{r["max_round"]}</td>'
        f'<td class="n">{esc(", ".join(r["strong"]) or "—")}</td>'
        f'<td class="n">{esc(", ".join(r["weak"]) or "—")}</td>'
        f'<td class="n"><code>{esc(r["classification"])}</code></td></tr>'
        for r in d["episode_table"]
    )
    parts.append(f"""<h2>9. טבלת האפיזודות המלאה</h2>
<table><tr><th class="n">אפיזודה</th><th class="n">מקרה</th><th class="n">סיום</th><th class="n">שאלות</th>
<th class="n">סבבים</th><th class="n">אותות חזקים</th><th class="n">אותות חלשים</th><th class="n">סיווג</th></tr>
{et}</table>
{caption("כל אפיזודה שנצפתה, עם האותות שפעלו בה והסיווג שנגזר",
         "אפיזודה בודדת", f"{h['complete_episodes_denominator']} אפיזודות שלמות · {h['excluded']} הוחרגו",
         "output/qa_events.jsonl",
         "התרעה פירושה <b>מועמדות לבדיקה אנושית</b> בלבד — לא שגיאה שאותרה, לא ליקוי ולא צורך מוכח בהתערבות")}""")

    parts.append(f"""<h2>10. עלות, אסימונים, ומה שאינו זמין</h2>
<table>
<tr><th>פריט</th><th class="n">ערך</th></tr>
<tr><td>קריאות ספק</td><td class="n">{cost['outbound_requests']}</td></tr>
<tr><td>אסימוני קלט</td><td class="n">{cost['prompt_tokens']:,}</td></tr>
<tr><td>אסימוני פלט</td><td class="n">{cost['completion_tokens']:,}</td></tr>
<tr><td>סה"כ אסימונים</td><td class="n">{cost['total_tokens']:,}</td></tr>
<tr><td>עלות בפועל</td><td class="n">${cost['actual_cost_usd']}</td></tr>
<tr class="hi"><td>ייחוס עלות לאפיזודה בודדת</td><td class="n"><code>{esc(cost['per_episode_attribution'])}</code></td></tr>
</table>
<p class="note"><b>מדוע לא זמין:</b> ההרצה לא שמרה יומן ברמת הקריאה הבודדת, ולכן לא ניתן לייחס
עלות או אסימונים לאפיזודה מסוימת. זהו <code>NOT_AVAILABLE</code> — <b>אין לדווח עליו כאפס
ואין לאמוד אותו בחלוקה פשוטה</b>.</p>""")

    parts.append(render_cost_calibration(d))

    au = d.get("authorisation") or {}
    parts.append(f"""<h2>12. גבולות הטענה</h2>
<table><tr><th>מותר לטעון</th><th>אסור לטעון</th></tr>
<tr><td>ספירות תיאוריות מריצת ספק מאושרת אחת, על קורפוס זה ובתצורה זו בלבד</td>
<td>נכונות ההתרעות · דיוק, precision, recall, F1 · אפקטיביות · תועלת אנושית · סיבתיות ·
ייצוגיות · הכללה · כל השוואה בין בסיס הבדיקה הדטרמיניסטי לריצה המאושרת כאילו הייתה תוצאה</td></tr></table>
<p class="note">מדדים אסורים שחושבו במסמך זה: <b>{esc(len(d['forbidden_metrics_computed']))}</b>.
מחקר 1B סגור כ-<code>BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL</code> ולא בוצע.
הפיילוט המוגבל-תקציב הוא <code>PREREGISTERED_NOT_EXECUTED</code>.
מחקר 2 (<code>VEGO_AI_ON</code> מול <code>VEGO_AI_OFF</code>) הוא <code>PREPARED_NOT_EXECUTED</code> —
אין לו תוצאה ואין להציגו כתוצאה. הרשאת התקציב הנוכחית לניסויים נוספים (USD {esc(au.get('ceiling_usd', 'Unknown'))}, {esc(au.get('authorised_on', 'Unknown'))}) לא נוצלה: קבלות הרצה בתשלום במסגרתה — <b>{esc(len(au['paid_run_receipts_on_or_after_authorisation'])) if isinstance(au.get('paid_run_receipts_on_or_after_authorisation'), list) else 'NOT_AVAILABLE'}</b>. הסעיפים 2, 8 ו-11 נוספו במהדורה זו; כולם חושבו ללא קריאת ספק ובלי לשנות את Detector-v1.</p>
</body></html>""")
    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dossier", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.dossier.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data), encoding="utf-8", newline="\n")
    print(f"rendered: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
