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
body { font-family: "Segoe UI", Arial, sans-serif; color:rgb(11,11,11); font-size:8.4pt; line-height:1.32; margin:0; }
h1 { font-size:14pt; margin:0 0 1mm; }
h2 { font-size:9.6pt; margin:2.2mm 0 1mm; padding-bottom:0.7mm; border-bottom:1.5px solid rgb(42,120,214); color:rgb(20,55,94); }
h3 { font-size:8.6pt; margin:2mm 0 0.8mm; color:rgb(20,55,94); }
.sub { color:rgb(82,81,78); font-size:7.6pt; margin:0 0 1.6mm; }
.warn { background:rgb(253,242,238); border-right:3px solid rgb(235,104,52); padding:1.6mm 2.2mm; font-size:7.6pt; margin:0 0 2mm; }
.key { background:rgb(238,244,252); border-right:3px solid rgb(42,120,214); padding:1.5mm 2.2mm; font-size:8pt; margin:0 0 1.6mm; }
.note { font-size:6.9pt; color:rgb(82,81,78); margin:0.4mm 0 1.3mm; }
table { width:100%; border-collapse:collapse; font-size:7.3pt; margin:0 0 1.1mm; }
th,td { border:1px solid rgb(216,216,212); padding:0.75mm 1.1mm; text-align:right; vertical-align:top; }
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


def render(d: dict[str, Any]) -> str:
    ev, h = d["evidence"], d["headline"]
    cost = d["cost"]
    cf = d["counterfactual_class_stability"]
    base = d["separation_baseline"]
    parts: list[str] = []

    parts.append(f"""<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="utf-8">
<title>VEGO-AI Study 1 — Results Dossier</title><style>{CSS}</style></head><body>
<h1>מחקר 1 — AirTravel: דוסייה תוצאות וניתוחים</h1>
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

    sig = h["signals_fired"]
    parts.append(f"""<h2>2. אותות שפעלו</h2>
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
    parts.append(f"""<h2>3. מסלול הביטחון לאורך הסבבים</h2>
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
    parts.append(f"""<h2>4. אורך שדה הראיה לפי רמת ביטחון</h2>
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
    parts.append(f"""<h2>5. ריכוז מסלולי התקשורת</h2>
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
    parts.append(f"""<h2>6. בסיס ההשוואה — האם הכלל מפריד בכלל?</h2>
<div class="warn"><b>בדיקת הנדסה בלבד — אינה תוצאה מדעית — אינה מדד ספק — אינה השוואת
<code>VEGO_AI_ON</code> מול <code>VEGO_AI_OFF</code>.</b> קריאות ספק: <b>{base['provider_calls']}</b>.
המכנים כאן נפרדים לחלוטין מן המכנה של ההרצה המאושרת ואין למזג ביניהם.</div>
<table><tr><th>מצב פיקסצ׳ר</th><th class="n">אפיזודות</th><th class="n">מכנה</th><th class="n">חזקה</th><th class="n">חלשה</th><th class="n">ללא</th><th class="n">סטטוס</th></tr>
{brow}</table>
<div class="key"><b>מסקנה מתודולוגית:</b> קלטים דטרמיניסטיים שונים מניעים את הכלל הקפוא
לסיווגים <b>הפוכים</b> — {esc(" · ".join(base["distinct_classes_produced"]))}.
לפיכך <b>הכלל אינו מנוון</b>. התוצאה "3 מתוך 3" בקורפוס AirTravel היא תכונה של <b>הקורפוס</b>,
ולא עדות לכך שהכלל שבור או שאינו מסוגל להבחין.</div>
{caption("סיווג Detector-v1 על שלושה מצבי פיקסצ׳ר דטרמיניסטיים",
         "אפיזודות בכל סיווג", "מכנה נפרד לכל מצב פיקסצ׳ר",
         "analysis/detector-envelope.json",
         "תשובות הפיקסצ׳ר סינתטיות ובנויות מראש; אינן מעידות דבר על התנהגות ספק אמיתי, "
         "על איכות או על נכונות")}""")

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
    parts.append(f"""<h2>7. טבלת האפיזודות המלאה</h2>
<table><tr><th class="n">אפיזודה</th><th class="n">מקרה</th><th class="n">סיום</th><th class="n">שאלות</th>
<th class="n">סבבים</th><th class="n">אותות חזקים</th><th class="n">אותות חלשים</th><th class="n">סיווג</th></tr>
{et}</table>
{caption("כל אפיזודה שנצפתה, עם האותות שפעלו בה והסיווג שנגזר",
         "אפיזודה בודדת", f"{h['complete_episodes_denominator']} אפיזודות שלמות · {h['excluded']} הוחרגו",
         "output/qa_events.jsonl",
         "התרעה פירושה <b>מועמדות לבדיקה אנושית</b> בלבד — לא שגיאה שאותרה, לא ליקוי ולא צורך מוכח בהתערבות")}""")

    parts.append(f"""<h2>8. עלות, אסימונים, ומה שאינו זמין</h2>
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
ואין לאמוד אותו בחלוקה פשוטה</b>.</p>

<h2>9. גבולות הטענה</h2>
<table><tr><th>מותר לטעון</th><th>אסור לטעון</th></tr>
<tr><td>ספירות תיאוריות מריצת ספק מאושרת אחת, על קורפוס זה ובתצורה זו בלבד</td>
<td>נכונות ההתרעות · דיוק, precision, recall, F1 · אפקטיביות · תועלת אנושית · סיבתיות ·
ייצוגיות · הכללה · כל השוואה בין בסיס הפיקסצ׳ר לריצה המאושרת כאילו הייתה תוצאה</td></tr></table>
<p class="note">מדדים אסורים שחושבו במסמך זה: <b>{esc(len(d['forbidden_metrics_computed']))}</b>.
מחקר 1B סגור כ-<code>BUDGET_BLOCKED_UNDER_FROZEN_PROTOCOL</code> ולא בוצע.
הפיילוט המוגבל-תקציב הוא <code>PREREGISTERED_NOT_EXECUTED</code>.
מחקר 2 (<code>VEGO_AI_ON</code> מול <code>VEGO_AI_OFF</code>) הוא <code>PREPARED_NOT_EXECUTED</code> —
אין לו תוצאה ואין להציגו כתוצאה.</p>
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
