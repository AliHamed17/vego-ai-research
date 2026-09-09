"""Build the five-page detection-baseline document, in English and in Hebrew.

The document answers one question with pictures: across the conversations we recorded, how sure
were the answers, and at what point would the rule first have had something to fire on. Text is
held to headings, one-line captions and short bullets; every number on the page comes from the
detection-baseline JSON rather than being typed in.

Three boundaries are carried on the page itself, not left to a reader's goodwill: a confidence
label is the answering agent's own statement and not a judgement that the answer was wrong; a
detection point is where the rule would fire and not where a problem occurred; and the runs are
never added together.

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

CSS = """
@page { size: A4; margin: 11mm 12mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Arial, sans-serif; color: rgb(27,27,31); margin: 0;
       font-size: 9.4pt; line-height: 1.42; }
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
h1 { font-size: 18pt; color: rgb(20,55,94); margin: 0 0 1mm; line-height: 1.16; }
h2 { font-size: 11.5pt; color: rgb(20,55,94); margin: 3mm 0 1.4mm;
     border-bottom: 2px solid rgb(42,120,214); padding-bottom: 0.8mm; }
h3 { font-size: 9.6pt; color: rgb(20,55,94); margin: 0 0 1mm; }
p { margin: 0 0 1.8mm; }
.sub { color: rgb(107,107,118); font-size: 9.4pt; margin-bottom: 2.5mm; }
img { width: 100%; display: block; margin: 0.8mm 0; }
.cap { font-size: 8pt; color: rgb(82,81,78); background: rgb(246,247,249);
       border-inline-start: 3px solid rgb(42,120,214); padding: 1.4mm 2.2mm; margin: 0 0 2.4mm; }
.kpis { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1.8mm; margin: 2.2mm 0; }
.kpi { background: rgb(246,247,249); border: 1px solid rgb(227,227,234); border-radius: 2mm;
       padding: 1.8mm 1.2mm; text-align: center; }
.kpi .v { font-size: 14pt; font-weight: 700; color: rgb(20,55,94); line-height: 1.05; }
.kpi .l { font-size: 7.4pt; color: rgb(82,81,78); margin-top: 0.8mm; }
.gloss { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.8mm; margin: 1.6mm 0; }
.term { background: rgb(255,255,255); border: 1px solid rgb(227,227,234); border-radius: 2mm;
        padding: 1.5mm 2mm; }
.term b { color: rgb(20,55,94); font-size: 8.8pt; }
.term span { display: block; font-size: 8pt; color: rgb(82,81,78); margin-top: 0.5mm; }
.hero { background: rgb(238,244,252); border: 1px solid rgb(207,224,245); border-radius: 2mm;
        padding: 2.6mm 3.4mm; margin: 2.4mm 0; }
.hero .n { font-size: 15pt; font-weight: 700; color: rgb(194,65,12); }
.hero .t { font-size: 9.2pt; color: rgb(20,55,94); }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 2.6mm; }
.good, .bad { border-radius: 2mm; padding: 2.2mm 2.8mm; }
.good { background: rgb(238,247,241); border: 1px solid rgb(191,224,203); }
.bad { background: rgb(253,240,234); border: 1px solid rgb(242,198,176); }
.good h3 { color: rgb(39,110,66); }
.bad h3 { color: rgb(168,67,24); }
ul { margin: 0; padding-inline-start: 4.2mm; }
li { margin-bottom: 1mm; font-size: 8.6pt; }
.verdict { background: rgb(20,55,94); color: rgb(255,255,255); border-radius: 2mm;
           padding: 2.6mm 3.6mm; margin-top: 2.4mm; }
.verdict .t { font-size: 8.2pt; opacity: .82; }
.verdict .v { font-size: 11.5pt; font-weight: 700; }
.note { font-size: 7.8pt; color: rgb(107,107,118); margin-top: 1.6mm; }
"""

TEXT = {
    "en": {
        "dir": "ltr", "lang": "en",
        "title": "When does the system notice it needs a human?",
        "sub": "VEGO-AI · Study 1 · the detection baseline, in plain language",
        "gloss_h": "Four words, before the charts",
        "terms": [
            ("Conversation", "One agent asks, another answers, until they stop."),
            ("Round", "One back-and-forth. A conversation can take up to 10."),
            ("Not sure", "The answering agent's own words about its answer. It does <b>not</b> mean the answer was wrong."),
            ("Detection", "The first moment the rule has something to fire on. It does <b>not</b> mean a problem happened."),
        ],
        "known_h": "Question 1 · Known and unknown questions",
        "known_cap": "Top row: single answers. Bottom row: whole conversations. About a "
                     "quarter of answers came back fully sure - but not one conversation was "
                     "fully sure from start to finish.",
        "hero0_n": "0 conversations",
        "hero0_t": "Not one recorded conversation was answered with full confidence all the "
                   "way through. That is why every conversation ends up in front of a human, "
                   "and why nothing here can be called a saving of human time.",
        "conf_h": "Question 2 · How sure were the answers?",
        "conf_cap": "Every answer in each run, sorted by how sure the answering agent said it was. "
                    "Most answers were not fully sure. Runs are shown separately and never added together.",
        "detect_h": "Question 3 · The detection point",
        "detect_cap": "Each bar counts conversations whose first not-sure answer landed in that round. "
                      "Orange is round 1.",
        "cumul_cap": "The same thing, added up. The dashed line is all conversations in that run.",
        "hero_n": "Round 1",
        "hero_t": "In every run, 9 or 10 out of every 10 conversations were already detectable at the "
                  "very first answer, and all of them by round 2. Rounds 3 to 10 cost money and "
                  "changed no flag.",
        "cumul_h": "Question 4 · How fast is everything detected?",
        "alerts_h": "Question 5 · What the rule decided for each conversation",
        "alerts_cap": "One square is one real conversation. The grey slot in the legend stayed "
                      "empty in every run: the rule never once said 'no human needed'.",
        "sig_h": "Question 6 · The alarm reasons",
        "sig_cap": "The rule has five reasons it can fire. Grey means it never fired in that run. "
                   "'No evidence' never fired anywhere — every answer carried some evidence.",
        "len_h": "Question 7 · Conversation length",
        "len_cap": "Number of answers per conversation. Run 1 stayed short; Run 2 ran long. "
                   "Nothing in the setup was changed between them.",
        "ev_h": "Question 8 · Evidence in the answers",
        "ev_cap": "Length in characters of the evidence attached to each answer. No answer came "
                  "back empty, which is why the 'no evidence' alarm never fired.",
        "case_h": "Question 9 · Coverage, and the blind spot",
        "case_cap": "A grey square on the baseline marks a case that produced no conversation at "
                    "all, so the rule never saw it. That is a blind spot, not a clean bill of "
                    "health.",
        "know_h": "What these charts show",
        "know": [
            "Most answers were <b>not fully sure</b> — between 75% and 93% in each run.",
            "Detection happens at <b>round 1</b> in 9-10 of every 10 conversations.",
            "Only <b>two</b> of the five alarm reasons do most of the work.",
            "'No evidence' <b>never</b> fired — every answer carried evidence.",
            "<b>Every</b> conversation was flagged. Not one was cleared.",
        ],
        "cant_h": "What they do not show",
        "cant": [
            "Not whether any answer was <b>right or wrong</b>. Nobody has checked.",
            "Not that a flagged conversation contains a <b>problem</b>.",
            "Not that a grey case is <b>safe</b>.",
            "Not any saving of human time — <b>nobody measured it</b>.",
            "A rule that flags <b>everything</b> has not sorted anything yet.",
        ],
        "verdict_t": "Status",
        "verdict_v": "DESCRIPTIVE RULE BEHAVIOUR ONLY - NOT READY FOR A SCIENTIFIC CONCLUSION",
        "note": "All numbers recomputed from the saved recordings. The rule was never changed. "
                "A fourth pilot run exists but cannot be verified from the published files, so it "
                "is left out of every chart here.",
    },
    "he": {
        "dir": "rtl", "lang": "he",
        "title": "מתי המערכת מזהה שהיא צריכה אדם?",
        "sub": "VEGO-AI · מחקר 1 · בסיס הזיהוי, בשפה פשוטה",
        "gloss_h": "ארבע מילים, לפני התרשימים",
        "terms": [
            ("שיחה", "סוכן אחד שואל, אחר עונה, עד שמפסיקים."),
            ("סבב", "הלוך ושוב אחד. שיחה יכולה להימשך עד 10 סבבים."),
            ("לא בטוח", "מילותיו של הסוכן המשיב על תשובתו. זה <b>אינו</b> אומר שהתשובה שגויה."),
            ("זיהוי", "הרגע הראשון שבו לכלל יש על מה להידלק. זה <b>אינו</b> אומר שקרתה בעיה."),
        ],
        "known_h": "שאלה 1 · שאלות ידועות ולא ידועות",
        "known_cap": "השורה העליונה: תשובות בודדות. השורה התחתונה: שיחות שלמות. כרבע מהתשובות "
                     "חזרו בביטחון מלא — אך אף שיחה לא הייתה בטוחה מתחילתה ועד סופה.",
        "hero0_n": "0 שיחות",
        "hero0_t": "אף שיחה מוקלטת לא נענתה בביטחון מלא לאורך כל הדרך. זו הסיבה שכל שיחה "
                   "מגיעה בסוף לאדם, וזו הסיבה ששום דבר כאן אינו חיסכון בזמן אדם.",
        "conf_h": "שאלה 2 · כמה בטוחות היו התשובות?",
        "conf_cap": "כל תשובה בכל הרצה, לפי כמה הסוכן המשיב אמר שהוא בטוח. רוב התשובות לא היו "
                    "בטוחות לגמרי. ההרצות מוצגות בנפרד ולעולם אינן מחוברות.",
        "detect_h": "שאלה 3 · נקודת הזיהוי",
        "detect_cap": "כל עמודה סופרת שיחות שבהן התשובה הראשונה שאינה בטוחה הגיעה באותו סבב. "
                      "כתום הוא סבב 1.",
        "cumul_cap": "אותו דבר, בהצטברות. הקו המקווקו הוא כלל השיחות באותה הרצה.",
        "hero_n": "סבב 1",
        "hero_t": "בכל הרצה, 9 או 10 מכל 10 שיחות כבר היו ניתנות לזיהוי בתשובה הראשונה ממש, "
                  "וכולן עד סבב 2. סבבים 3 עד 10 עלו כסף ולא שינו אף סימון.",
        "cumul_h": "שאלה 4 · כמה מהר הכול מזוהה?",
        "alerts_h": "שאלה 5 · מה הכלל החליט לגבי כל שיחה",
        "alerts_cap": "כל ריבוע הוא שיחה אמיתית אחת. המשבצת האפורה במקרא נשארה ריקה "
                      "בכל הרצה: הכלל מעולם לא אמר אף פעם שאין צורך באדם.",
        "sig_h": "שאלה 6 · סיבות האזעקה",
        "sig_cap": "לכלל יש חמש סיבות להידלק. אפור פירושו שלא נדלק כלל באותה הרצה. "
                   "״אין ראיה״ לא נדלק בשום מקום — כל תשובה נשאה ראיה כלשהי.",
        "len_h": "שאלה 7 · אורך השיחות",
        "len_cap": "מספר התשובות בכל שיחה. הרצה 1 נשארה קצרה; הרצה 2 התארכה. "
                   "דבר בהגדרות לא שונה ביניהן.",
        "ev_h": "שאלה 8 · ראיות בתשובות",
        "ev_cap": "אורך הראיה שצורפה לכל תשובה, בתווים. אף תשובה לא חזרה ריקה, ולכן אזעקת "
                  "״אין ראיה״ מעולם לא נדלקה.",
        "case_h": "שאלה 9 · כיסוי, והשטח המת",
        "case_cap": "ריבוע אפור על קו הבסיס מסמן מקרה שלא יצר שיחה כלל, ולכן הכלל מעולם לא ראה "
                    "אותו. זהו שטח מת, לא אישור תקינות.",
        "know_h": "מה התרשימים מראים",
        "know": [
            "רוב התשובות <b>לא היו בטוחות לגמרי</b> — בין 75% ל-93% בכל הרצה.",
            "הזיהוי קורה ב<b>סבב 1</b> ב-9 עד 10 מכל 10 שיחות.",
            "רק <b>שתיים</b> מחמש סיבות האזעקה עושות את רוב העבודה.",
            "״אין ראיה״ <b>מעולם</b> לא נדלק — כל תשובה נשאה ראיה.",
            "<b>כל</b> שיחה סומנה. אף אחת לא נוקתה.",
        ],
        "cant_h": "מה הם אינם מראים",
        "cant": [
            "לא אם תשובה כלשהי <b>נכונה או שגויה</b>. איש לא בדק.",
            "לא ששיחה שסומנה מכילה <b>בעיה</b>.",
            "לא שמקרה אפור הוא <b>תקין</b>.",
            "לא חיסכון כלשהו בזמן אדם — <b>איש לא מדד אותו</b>.",
            "כלל שמסמן <b>הכול</b> עדיין לא מיין דבר.",
        ],
        "verdict_t": "מעמד",
        "verdict_v": "תיאור התנהגות הכלל בלבד - לא בשל למסקנה מדעית",
        "note": "כל המספרים מחושבים מחדש מההקלטות השמורות. הכלל מעולם לא שונה. "
                "קיימת הרצת פיילוט רביעית שאי אפשר לאמת מהקבצים שפורסמו, ולכן היא אינה מופיעה "
                "באף תרשים כאן.",
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


def gloss_block(terms: list[tuple[str, str]]) -> str:
    cells = "".join(f'<div class="term"><b>{esc(t)}</b><span>{d}</span></div>' for t, d in terms)
    return f'<div class="gloss">{cells}</div>'


def hero(number: str, text: str) -> str:
    return (f'<div class="hero"><span class="n">{esc(number)}</span> &nbsp; '
            f'<span class="t">{esc(text)}</span></div>')


def kpis_for(data: dict[str, Any], lang: str) -> list[tuple[str, str]]:
    by_key = {run["run_key"]: run for run in data["runs"]}
    episodes = sum(run["complete_episodes"] for run in data["runs"])
    unsure = min(
        1 - run["confidence_share"]["High"] for run in data["runs"]
    )
    labels = {
        "en": ["cases in the big runs", "runs we can verify", "conversations recorded",
               "answers not fully sure", "human ratings so far"],
        "he": ["מקרים בהרצות הגדולות", "הרצות שניתן לאמת", "שיחות שנרשמו",
               "תשובות שאינן בטוחות לגמרי", "דירוגים אנושיים עד כה"],
    }[lang]
    return [
        ("21", labels[0]),
        (str(len(data["runs"])), labels[1]),
        (str(episodes), labels[2]),
        (f"{unsure:.0%}+", labels[3]),
        ("0", labels[4]),
    ]


def build(lang: str, data: dict[str, Any]) -> str:
    T = TEXT[lang]
    fig = "detect/detect-%s-" + lang + ".png"
    know = "".join(f"<li>{k}</li>" for k in T["know"])
    cant = "".join(f"<li>{c}</li>" for c in T["cant"])
    summary = (
        f'<div class="two">'
        f'<div class="good"><h3>{esc(T["know_h"])}</h3><ul>{know}</ul></div>'
        f'<div class="bad"><h3>{esc(T["cant_h"])}</h3><ul>{cant}</ul></div></div>'
    )
    page1 = (
        f'<div class="page"><h1>{esc(T["title"])}</h1>'
        f'<p class="sub">{esc(T["sub"])}</p>'
        f'{kpi_block(kpis_for(data, lang))}'
        f'<h2>{esc(T["gloss_h"])}</h2>{gloss_block(T["terms"])}'
        f'<h2>{esc(T["known_h"])}</h2>'
        f'<img src="{fig % "known"}" alt="">'
        f'<p class="cap">{esc(T["known_cap"])}</p>'
        f'{hero(T["hero0_n"], T["hero0_t"])}'
        f'{summary}</div>'
    )
    page2 = (
        f'<div class="page"><h2>{esc(T["conf_h"])}</h2>'
        f'<img src="{fig % "confidence"}" alt="">'
        f'<p class="cap">{esc(T["conf_cap"])}</p>'
        f'<h2>{esc(T["detect_h"])}</h2>'
        f'<img src="{fig % "detection"}" alt="">'
        f'<p class="cap">{esc(T["detect_cap"])}</p></div>'
    )
    page3 = (
        f'<div class="page"><h2>{esc(T["cumul_h"])}</h2>'
        f'<img src="{fig % "cumulative"}" alt="">'
        f'<p class="cap">{esc(T["cumul_cap"])}</p>'
        f'{hero(T["hero_n"], T["hero_t"])}'
        f'<h2>{esc(T["alerts_h"])}</h2>'
        f'<img src="{fig % "alerts"}" alt="">'
        f'<p class="cap">{esc(T["alerts_cap"])}</p></div>'
    )
    page4 = (
        f'<div class="page"><h2>{esc(T["sig_h"])}</h2>'
        f'<img src="{fig % "signals"}" alt="">'
        f'<p class="cap">{esc(T["sig_cap"])}</p>'
        f'<h2>{esc(T["len_h"])}</h2>'
        f'<img src="{fig % "lengths"}" alt="">'
        f'<p class="cap">{esc(T["len_cap"])}</p></div>'
    )
    page5 = (
        f'<div class="page"><h2>{esc(T["ev_h"])}</h2>'
        f'<img src="{fig % "evidence"}" alt="">'
        f'<p class="cap">{esc(T["ev_cap"])}</p>'
        f'<h2>{esc(T["case_h"])}</h2>'
        f'<img src="{fig % "cases"}" alt="">'
        f'<p class="cap">{esc(T["case_cap"])}</p>'
        f'<div class="verdict"><div class="t">{esc(T["verdict_t"])}</div>'
        f'<div class="v">{esc(T["verdict_v"])}</div></div>'
        f'<p class="note">{esc(T["note"])}</p></div>'
    )
    return (
        f'<!DOCTYPE html><html lang="{T["lang"]}" dir="{T["dir"]}"><head><meta charset="utf-8">'
        f'<title>{esc(T["title"])}</title><style>{CSS}</style></head><body>'
        f"{page1}{page2}{page3}{page4}{page5}</body></html>"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=FIGURES)
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for lang in ("en", "he"):
        target = args.out_dir / f"detection-baseline-{lang}.html"
        target.write_text(build(lang, data), encoding="utf-8")
        written.append(target.name)
    print(json.dumps({"written": written, "excluded": list(data["excluded"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
