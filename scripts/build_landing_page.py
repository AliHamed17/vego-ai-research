"""Build the four-page visual landing page, in English and in Hebrew.

The brief is a reader who knows nothing: no jargon without a definition beside it, no paragraph
where a picture will do, and no number without the word that says what it counts. Every page is
therefore built around one figure, with text reduced to labels, one-line captions and short
bullets.

The two language versions are the same document with the same figures and the same numbers. Only
direction and wording change, so a claim cannot drift between them.

Numbers come from the tracked reconciliation file. A run the reconciliation marks unverified is
drawn as unverified and its counts are never shown.

No provider is contacted.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "docs/research/phd-proposal/figures"
RECON = ROOT / "docs/research/phd-proposal/study1c-reconciliation.json"

CSS = """
@page { size: A4; margin: 12mm 13mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Arial, sans-serif; color: rgb(27,27,31); margin: 0;
       font-size: 9.6pt; line-height: 1.45; }
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
h1 { font-size: 17.5pt; color: rgb(20,55,94); margin: 0 0 1mm; line-height: 1.18; }
h2 { font-size: 12pt; color: rgb(20,55,94); margin: 3.4mm 0 1.6mm;
     border-bottom: 2px solid rgb(42,120,214); padding-bottom: 1mm; }
h3 { font-size: 10pt; color: rgb(20,55,94); margin: 0 0 1mm; }
p { margin: 0 0 2mm; }
.sub { color: rgb(107,107,118); font-size: 9.6pt; margin-bottom: 2.5mm; }
img { width: 100%; display: block; margin: 1mm 0; }
.cap { font-size: 8.2pt; color: rgb(82,81,78); background: rgb(246,247,249);
       border-inline-start: 3px solid rgb(42,120,214); padding: 1.6mm 2.4mm; margin: 0 0 3mm; }
.kpis { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2mm; margin: 2.2mm 0; }
.kpi { background: rgb(246,247,249); border: 1px solid rgb(227,227,234); border-radius: 2mm;
       padding: 1.8mm 1.2mm; text-align: center; }
.kpi .v { font-size: 14.5pt; font-weight: 700; color: rgb(20,55,94); line-height: 1; }
.kpi .l { font-size: 7.6pt; color: rgb(82,81,78); margin-top: 1mm; }
.flow { display: grid; grid-template-columns: repeat(6, 1fr); gap: 1.5mm; margin: 2mm 0; }
.step { background: rgb(238,244,252); border: 1px solid rgb(207,224,245); border-radius: 2mm;
        padding: 1.5mm 1.2mm; text-align: center; }
.step .n { display: inline-block; width: 5mm; height: 5mm; line-height: 5mm; border-radius: 50%;
           background: rgb(42,120,214); color: rgb(255,255,255); font-size: 8pt; font-weight: 700; }
.step .t { font-size: 8.4pt; font-weight: 700; color: rgb(20,55,94); margin-top: 1mm; }
.step .s { font-size: 7.2pt; color: rgb(82,81,78); }
.gloss { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.8mm; margin: 1.6mm 0; }
.term { background: rgb(255,255,255); border: 1px solid rgb(227,227,234); border-radius: 2mm;
        padding: 1.5mm 2mm; }
.term b { color: rgb(20,55,94); font-size: 9pt; }
.term span { display: block; font-size: 8.2pt; color: rgb(82,81,78); margin-top: 0.6mm; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 3mm; }
.good, .bad { border-radius: 2mm; padding: 2.4mm 3mm; }
.good { background: rgb(238,247,241); border: 1px solid rgb(191,224,203); }
.bad { background: rgb(253,240,234); border: 1px solid rgb(242,198,176); }
.good h3 { color: rgb(39,110,66); }
.bad h3 { color: rgb(168,67,24); }
ul { margin: 0; padding-inline-start: 4.5mm; }
li { margin-bottom: 1.2mm; font-size: 8.8pt; }
.verdict { background: rgb(20,55,94); color: rgb(255,255,255); border-radius: 2mm;
           padding: 3mm 4mm; margin-top: 3mm; }
.verdict .t { font-size: 8.4pt; opacity: .82; }
.verdict .v { font-size: 12.5pt; font-weight: 700; letter-spacing: .3px; }
.note { font-size: 8pt; color: rgb(107,107,118); margin-top: 2mm; }
table { width: 100%; border-collapse: collapse; font-size: 8.4pt; margin: 2mm 0; }
th { background: rgb(20,55,94); color: rgb(255,255,255); padding: 1.6mm 2mm; text-align: start;
     font-weight: 600; font-size: 8.2pt; }
td { padding: 1.5mm 2mm; border-bottom: 1px solid rgb(227,227,234); }
tr.grey td { color: rgb(107,107,118); background: rgb(248,248,250); font-style: italic; }
"""

TEXT = {
    "en": {
        "dir": "ltr", "lang": "en",
        "title": "Can a simple rule pick which AI conversations a person should check?",
        "sub": "VEGO-AI · Study 1 · a plain-language summary of everything we ran",
        "why_h": "Why we did this",
        "why": "Several AI agents talk to each other to build a model. Sometimes an agent is "
               "unsure. We want to know: can an automatic rule pick out the conversations a "
               "person should look at, so a person does not have to read all of them?",
        "flow_h": "How it works, end to end",
        "steps": [
            ("Public data", "21 airline cases"),
            ("AI agents", "ask and answer"),
            ("Recording", "every question saved"),
            ("The rule", "reads the recording"),
            ("A flag", "HIGH / LOW / none"),
            ("A person", "not done yet"),
        ],
        "gloss_h": "Words we use, in plain language",
        "terms": [
            ("Conversation", "One agent asks, another answers, until they stop. We recorded 25."),
            ("The rule", "A fixed check written down before we saw any result. It never changed."),
            ("Flag HIGH", "The rule says a person should look. It does <b>not</b> mean an error."),
            ("Flag LOW", "A weaker signal. Still sent to a person."),
            ("Baseline", "A very simple rule we compare against, to see if ours adds anything."),
            ("Not verified", "We cannot prove it from the published files, so we do not report it."),
        ],
        "kpis": [("21", "public cases"), ("3", "verified runs"), ("25", "conversations"),
                 ("$1.96", "total spent"), ("0", "human ratings")],
        "built_h": "What we built and what we fixed",
        "built": [
            ("Used every case, not a sample", "All 21 cases, so nobody can ask why we picked those."),
            ("Checked the data is genuine", "Re-downloaded it; every file matched its fingerprint exactly."),
            ("Logged every call", "So the cost can be checked, not just believed."),
            ("Turned off silent retries", "So the spending limit counts real calls."),
            ("Compared in two ways", "This found a claim of ours that was wrong."),
            ("Removed an unproven result", "A pilot we cannot verify was taken out of the report."),
        ],
        "table_h": "Every run, side by side",
        "table_cols": ["Run", "Status", "Conversations", "HIGH", "LOW", "Sent to a person", "Cost"],
        "table_names": ["Run 0", "Run 1", "Run 2", "Pilot", "Test data"],
        "table_cap": "We never add these rows together. Each run used a different setup, so a "
                     "combined total would describe a run that never happened.",
        "runs_h": "What we ran",
        "runs_cap": "Three runs we can verify. Each bar is one run; each block is one conversation. "
                    "The grey bar is a pilot we cannot verify from the published files, so no numbers are shown for it.",
        "length_h": "The main finding",
        "length_cap": "Each dot is one conversation. Short ones get both flags. Long ones are always "
                      "flagged HIGH. Length is not something we controlled - it came out differently in each run.",
        "base_h": "The baselines - the most important test",
        "base_cap": "We compared our rule against very simple rules. Left: does the simple rule give "
                    "the exact same label? Right: does it send the same conversations to a person?",
        "base_points": [
            "Left panel (a): <b>no</b> simple rule gives the same exact label as ours.",
            "Right panel (b): <b>&ldquo;always flag everything&rdquo;</b> sends exactly the same conversations to a person - 100%.",
            "So our rule looks different only when comparing labels, not when comparing who gets sent to a person.",
        ],
        "mech_h": "Two checkers, two answers",
        "mech_cap": "The system already has another checker that looks at single sentences. It found "
                    "problems in cases where our rule said nothing. Neither one is the truth - they look at different things.",
        "know_h": "What we can say",
        "know": [
            "The pipeline runs end to end; everything is recorded and hash-checked.",
            "Long conversations are almost always flagged HIGH. That is how the rule is built.",
            "At the &ldquo;send to a person&rdquo; level, a rule that flags everything does the same as ours.",
            "Cost is small: $1.96 for all three runs.",
        ],
        "cant_h": "What we cannot say",
        "cant": [
            "We cannot say a flag was <b>correct</b>. Nobody has judged the conversations yet.",
            "We cannot say it <b>saves work</b>. Nobody measured review time.",
            "No accuracy, no benefit, no comparison against other systems.",
            "The pilot run is <b>not verified</b>, so it is not counted anywhere.",
        ],
        "verdict_t": "Current status",
        "verdict_v": "DESCRIPTIVE RULE BEHAVIOUR ONLY - NOT READY FOR A SCIENTIFIC CONCLUSION",
        "verdict_n": "Next step: two independent people rate the conversations without seeing the "
                     "rule's flag. Everything is built and waiting for that.",
        "note": "Every number here is recomputed from the saved recordings. The rule was never changed.",
    },
    "he": {
        "dir": "rtl", "lang": "he",
        "title": "האם כלל פשוט יכול לבחור אילו שיחות של סוכני בינה מלאכותית אדם צריך לבדוק?",
        "sub": "VEGO-AI · מחקר 1 · סיכום בשפה פשוטה של כל מה שהרצנו",
        "why_h": "למה עשינו את זה",
        "why": "כמה סוכני בינה מלאכותית מדברים ביניהם כדי לבנות מודל. לפעמים סוכן אינו בטוח. "
               "אנחנו רוצים לדעת: האם כלל אוטומטי יכול לבחור את השיחות שאדם צריך להסתכל "
               "עליהן, כדי שאדם לא יצטרך לקרוא את כולן?",
        "flow_h": "איך זה עובד, מקצה לקצה",
        "steps": [
            ("נתונים ציבוריים", "21 מקרי תעופה"),
            ("סוכני בינה", "שואלים ועונים"),
            ("הקלטה", "כל שאלה נשמרת"),
            ("הכלל", "קורא את ההקלטה"),
            ("סימון", "גבוה / נמוך / אין"),
            ("אדם", "עדיין לא בוצע"),
        ],
        "gloss_h": "המילים שאנחנו משתמשים בהן, בשפה פשוטה",
        "terms": [
            ("שיחה", "סוכן אחד שואל, אחר עונה, עד שמפסיקים. הקלטנו 25."),
            ("הכלל", "בדיקה קבועה שנכתבה לפני שראינו תוצאה כלשהי. היא מעולם לא שונתה."),
            ("סימון גבוה", "הכלל אומר שאדם צריך להסתכל. זה <b>אינו</b> אומר שיש שגיאה."),
            ("סימון נמוך", "אות חלש יותר. עדיין נשלח לאדם."),
            ("קו בסיס", "כלל פשוט מאוד שמשווים אליו, כדי לראות אם שלנו מוסיף משהו."),
            ("לא אומת", "אי אפשר להוכיח מהקבצים שפורסמו, ולכן איננו מדווחים על כך."),
        ],
        "kpis": [("21", "מקרים ציבוריים"), ("3", "הרצות מאומתות"), ("25", "שיחות"),
                 ("$1.96", "עלות כוללת"), ("0", "דירוגים אנושיים")],
        "built_h": "מה בנינו ומה תיקנו",
        "built": [
            ("השתמשנו בכל המקרים", "כל 21 המקרים, כדי שאיש לא ישאל למה בחרנו דווקא אלה."),
            ("בדקנו שהנתונים אמיתיים", "הורדנו מחדש; כל קובץ התאים לטביעת האצבע שלו בדיוק."),
            ("תיעדנו כל קריאה", "כדי שאפשר יהיה לבדוק את העלות, לא רק להאמין לה."),
            ("ביטלנו ניסיונות חוזרים שקטים", "כדי שמגבלת ההוצאה תספור קריאות אמיתיות."),
            ("השווינו בשתי דרכים", "כך מצאנו טענה שלנו שהייתה שגויה."),
            ("הסרנו תוצאה לא מוכחת", "פיילוט שאי אפשר לאמת הוצא מהדוח."),
        ],
        "table_h": "כל ההרצות זו לצד זו",
        "table_cols": ["הרצה", "מצב", "שיחות", "גבוה", "נמוך", "נשלחו לאדם", "עלות"],
        "table_names": ["הרצה 0", "הרצה 1", "הרצה 2", "פיילוט", "נתוני בדיקה"],
        "table_cap": "איננו מחברים את השורות. כל הרצה השתמשה בהגדרות אחרות, ולכן סכום כולל "
                     "היה מתאר הרצה שמעולם לא בוצעה.",
        "runs_h": "מה הרצנו",
        "runs_cap": "שלוש הרצות שניתן לאמת. כל עמודה היא הרצה; כל מקטע הוא שיחה אחת. "
                    "העמודה האפורה היא פיילוט שאי אפשר לאמת מהקבצים שפורסמו, ולכן אין עבורו מספרים.",
        "length_h": "הממצא המרכזי",
        "length_cap": "כל נקודה היא שיחה אחת. שיחות קצרות מקבלות את שני הסימונים. שיחות ארוכות "
                      "תמיד מסומנות גבוה. באורך השיחה לא שלטנו - הוא יצא שונה בכל הרצה.",
        "base_h": "קווי הבסיס - הבדיקה החשובה ביותר",
        "base_cap": "השווינו את הכלל שלנו לכללים פשוטים מאוד. מימין (א): האם הכלל הפשוט נותן "
                    "בדיוק את אותה תווית? משמאל (ב): האם הוא שולח את אותן שיחות לאדם?",
        "base_points": [
            "לוח ימין (א): <b>אף</b> כלל פשוט אינו נותן את אותה תווית מדויקת כמו שלנו.",
            "לוח שמאל (ב): <b>״תמיד לסמן הכול״</b> שולח בדיוק את אותן שיחות לאדם - 100%.",
            "כלומר הכלל שלנו נראה שונה רק כשמשווים תוויות, ולא כשמשווים מי נשלח לאדם.",
        ],
        "mech_h": "שני בודקים, שתי תשובות",
        "mech_cap": "במערכת כבר יש בודק אחר שמסתכל על משפטים בודדים. הוא מצא בעיות במקרים "
                    "שבהם הכלל שלנו שתק. אף אחד מהם אינו האמת - הם מסתכלים על דברים שונים.",
        "know_h": "מה אפשר לומר",
        "know": [
            "הצינור רץ מקצה לקצה; הכול נרשם ומאומת בגיבוב.",
            "שיחות ארוכות כמעט תמיד מסומנות גבוה. כך הכלל בנוי.",
            "ברמת ״שליחה לאדם״, כלל שמסמן הכול עושה את אותו דבר כמו שלנו.",
            "העלות נמוכה: 1.96$ לשלוש ההרצות.",
        ],
        "cant_h": "מה אי אפשר לומר",
        "cant": [
            "אי אפשר לומר שסימון היה <b>נכון</b>. איש עדיין לא שפט את השיחות.",
            "אי אפשר לומר שזה <b>חוסך עבודה</b>. איש לא מדד זמן בדיקה.",
            "אין דיוק, אין תועלת, ואין השוואה למערכות אחרות.",
            "הרצת הפיילוט <b>אינה מאומתת</b>, ולכן אינה נספרת בשום מקום.",
        ],
        "verdict_t": "מעמד נוכחי",
        "verdict_v": "תיאור התנהגות הכלל בלבד - לא בשל למסקנה מדעית",
        "verdict_n": "השלב הבא: שני אנשים עצמאיים ידרגו את השיחות בלי לראות את הסימון של הכלל. "
                     "הכול בנוי וממתין לכך.",
        "note": "כל מספר כאן מחושב מחדש מההקלטות השמורות. הכלל מעולם לא שונה.",
    },
}


def esc(value: Any) -> str:
    return html.escape(str(value))


def kpi_block(items: list[tuple[str, str]]) -> str:
    cells = "".join(
        f'<div class="kpi"><div class="v">{esc(v)}</div><div class="l">{esc(l)}</div></div>'
        for v, l in items
    )
    return f'<div class="kpis">{cells}</div>'


def flow_block(steps: list[tuple[str, str]]) -> str:
    cells = "".join(
        f'<div class="step"><span class="n">{i}</span>'
        f'<div class="t">{esc(t)}</div><div class="s">{esc(s)}</div></div>'
        for i, (t, s) in enumerate(steps, 1)
    )
    return f'<div class="flow">{cells}</div>'


def gloss_block(terms: list[tuple[str, str]]) -> str:
    cells = "".join(f'<div class="term"><b>{esc(t)}</b><span>{d}</span></div>' for t, d in terms)
    return f'<div class="gloss">{cells}</div>'


def built_block(items):
    cells = "".join(
        f'<div class="term"><b>{esc(t)}</b><span>{esc(d)}</span></div>' for t, d in items
    )
    return f'<div class="gloss">{cells}</div>'


NA_TEXT = {"en": "not verified", "he": "לא אומת"}
OFFLINE_TEXT = {"en": "no AI used", "he": "בלי בינה מלאכותית"}


def run_table(recon, lang):
    """One row per run, with unverified runs showing no numbers at all."""
    T = TEXT[lang]
    head = "".join(f"<th>{esc(c)}</th>" for c in T["table_cols"])
    rows = ""
    for name, row in zip(T["table_names"], recon["runs"]):
        verified = row["execution_status"] == "EXECUTED"
        cost = row.get("cost", {})
        if verified:
            cells = [
                str(row["complete_episodes"]),
                str(row["detector_class_STRONG_ALERT"]),
                str(row["detector_class_WEAK_ALERT"]),
                str(row["episodes_selected_for_review"]),
                f'${cost.get("usd", 0):.2f}',
            ]
            status = "OK"
        else:
            dash = (
                NA_TEXT[lang]
                if row["execution_status"].startswith("PREREG")
                else OFFLINE_TEXT[lang]
            )
            cells = ["-", "-", "-", "-", "-"]
            status = dash
        body = "".join(f"<td>{esc(c)}</td>" for c in cells)
        klass = "" if verified else ' class="grey"'
        rows += f"<tr{klass}><td>{esc(name)}</td><td>{esc(status)}</td>{body}</tr>"
    return f"<table><tr>{head}</tr>{rows}</table>"


def build(lang: str, recon) -> str:
    T = TEXT[lang]
    fig = "landing/landing-%s-" + lang + ".png"
    page1 = (
        f'<div class="page"><h1>{esc(T["title"])}</h1>'
        f'<p class="sub">{esc(T["sub"])}</p>'
        f'{kpi_block(T["kpis"])}'
        f'<h2>{esc(T["why_h"])}</h2><p>{esc(T["why"])}</p>'
        f'<h2>{esc(T["flow_h"])}</h2>{flow_block(T["steps"])}'
        f'<h2>{esc(T["gloss_h"])}</h2>{gloss_block(T["terms"])}'
        f'<h2>{esc(T["runs_h"])}</h2>'
        f'<img src="{fig % "runs"}" alt="">'
        f'<p class="cap">{esc(T["runs_cap"])}</p></div>'
    )
    page2 = (
        f'<div class="page"><h2>{esc(T["length_h"])}</h2>'
        f'<img src="{fig % "length"}" alt="">'
        f'<p class="cap">{esc(T["length_cap"])}</p>'
        f'<h2>{esc(T["built_h"])}</h2>{built_block(T["built"])}'
        f'<p class="note">{esc(T["note"])}</p></div>'
    )
    points = "".join(f"<li>{p}</li>" for p in T["base_points"])
    page3 = (
        f'<div class="page"><h2>{esc(T["base_h"])}</h2>'
        f'<img src="{fig % "baselines"}" alt="">'
        f'<p class="cap">{esc(T["base_cap"])}</p>'
        f"<ul>{points}</ul>"
        f'<h2>{esc(T["mech_h"])}</h2>'
        f'<img src="{fig % "mechanisms"}" alt="">'
        f'<p class="cap">{esc(T["mech_cap"])}</p></div>'
    )
    know = "".join(f"<li>{k}</li>" for k in T["know"])
    cant = "".join(f"<li>{c}</li>" for c in T["cant"])
    page4 = (
        f'<div class="page"><h2>{esc(T["know_h"])} · {esc(T["cant_h"])}</h2>'
        f'<div class="two">'
        f'<div class="good"><h3>{esc(T["know_h"])}</h3><ul>{know}</ul></div>'
        f'<div class="bad"><h3>{esc(T["cant_h"])}</h3><ul>{cant}</ul></div></div>'
        f'<div class="verdict"><div class="t">{esc(T["verdict_t"])}</div>'
        f'<div class="v">{esc(T["verdict_v"])}</div></div>'
        f'<p class="note">{esc(T["verdict_n"])}</p>'
        f'<h2>{esc(T["table_h"])}</h2>{run_table(recon, lang)}'
        f'<p class="cap">{esc(T["table_cap"])}</p></div>'
    )
    return (
        f'<!DOCTYPE html><html lang="{T["lang"]}" dir="{T["dir"]}"><head><meta charset="utf-8">'
        f'<title>{esc(T["title"])}</title><style>{CSS}</style></head><body>'
        f"{page1}{page2}{page3}{page4}</body></html>"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=FIGURES)
    args = parser.parse_args()
    recon = json.loads(RECON.read_text(encoding="utf-8"))
    unverified = [
        row["run_id"]
        for row in recon["runs"]
        if row["execution_status"] == "PREREGISTERED_NOT_EXECUTED_OR_UNVERIFIED"
    ]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for lang in ("en", "he"):
        target = args.out_dir / f"landing-{lang}.html"
        target.write_text(build(lang, recon), encoding="utf-8")
        written.append(target.name)
    print(json.dumps({"written": written, "shown_as_unverified": unverified}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
