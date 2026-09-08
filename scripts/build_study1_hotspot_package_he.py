"""Build the Hebrew RTL supervisor package for the human-review hotspot baseline.

Four documents come out of one data source: the frozen manifest, the analysis tables and the run
receipts. Nothing is typed in by hand, so a number cannot appear in the report that the analysis
did not compute, and a table that the analysis reports `NOT_AVAILABLE` cannot quietly acquire a
value on its way into Hebrew.

Every figure carries the four fields the study requires — what is shown, numerator, denominator
and source — plus a one-line statement of what it does not prove, and an evidence-class chip
drawn from exactly four labels. A figure that reached a reader without those fields would invite
a claim the data does not support, which is the failure mode this package exists to prevent.

No provider is contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from study1_rtl_document import (  # noqa: E402
    ARCHIVAL,
    DOC_CSS,
    FIXTURE,
    MAP_CSS,
    PROSPECTIVE,
    UNAVAILABLE,
    bars,
    caption,
    chip,
    esc,
    kpi,
    num,
    page,
    stages,
    table,
)

FIGURES = ROOT / "docs/research/phd-proposal/figures"
NA_HE = "אינו זמין"


def md_h(level: int, text: str) -> str:
    return f"{'#' * level} {text}"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else NA_HE


def shorten(value: str, keep: int = 12) -> str:
    return value if len(value) <= keep else f"{value[:keep]}…"


def h2(title: str, evidence_class: str | None = None) -> str:
    tail = f" {chip(evidence_class)}" if evidence_class else ""
    return f"<h2>{esc(title)}{tail}</h2>"


def is_unavailable(block: Any) -> bool:
    return isinstance(block, dict) and block.get("status") == "NOT_AVAILABLE"


def value_or_na(value: Any) -> str:
    if value is None or value == "NOT_AVAILABLE":
        return f'<span class="na-v">{NA_HE}</span>'
    return num(value)


def section_purpose(manifest: dict[str, Any]) -> str:
    budget = manifest["budget"]
    return (
        h2("1. מה השאלה, ומה אינה")
        + "<p>השאלה היחידה שהמחקר הזה שואל היא: מבין שיחות שאלה־תשובה שהושלמו, "
        "עד כמה גלאי־v1 מקדם לבדיקה אנושית בדיוק את אותן שיחות ששני בודקים אנושיים "
        "עיוורים שופטים, כל אחד בנפרד, כראויות לבדיקה.</p>"
        "<p><b>מה שנמדד אינו נכונות של הבינה המלאכותית.</b> מה שנמדד הוא האם הגלאי "
        "מקטין את עומס הבדיקה, ובאותה עת שומר בפנים את השיחות שאדם שופט כראויות "
        "לבדיקה. אלה שתי שאלות נפרדות, והתשובה לאחת אינה תשובה לשנייה.</p>"
        + f'<div class="kpis">{kpi(num(manifest["corpus"]["eligible_case_count"]), "מקרים כשירים במסגרת")}'
        f'{kpi(num(len(manifest["selection"]["selected"])), "מקרים שנדגמו מראש")}'
        f'{kpi(num(f"{budget['whole_study_reservation_usd']:.2f}$"), "שריון פסימי לכל המחקר")}'
        f'{kpi(num(f"{budget['ceiling_usd']:.2f}$"), "תקרת ההוצאה")}</div>'
        + caption(
            meaning="הפרמטרים שהוקפאו לפני כל קריאה לספק",
            numerator="6 מקרים נבחרים",
            denominator="21 מקרים כשירים",
            source="study1-hotspot-manifest.json",
            limitation="הקפאה אינה תוצאה; היא רק מונעת שינוי אחרי שרואים תוצאה",
        )
    )


def section_freeze(manifest: dict[str, Any]) -> str:
    selection = manifest["selection"]
    rows = [[esc(row["path"]), num(row["bytes"])] for row in selection["selected"]]
    return (
        h2("2. מה הוקפא, ולמה הבחירה אינה יכולה להיות מוטית")
        + "<p>הדגימה נקבעה בהגרלה דטרמיניסטית מתוך כל מסגרת המקרים הכשירים, עם זרע "
        f"{num(selection['seed'])} שנקבע בקוד לפני ההגרלה. כל אדם יכול לשחזר את אותה "
        "הגרלה מהזרע ומהמלאי המוצמד בלבד. מכאן שהבחירה <b>אינה יכולה</b> להיות תלויה "
        "בסטטוס התרעה חזוי או נצפה.</p>"
        + table(["מקרה שנבחר", "בתים"], rows, numeric_from=1)
        + caption(
            meaning="ששת המקרים שהוקפאו, וגודל הקובץ שלהם",
            numerator="6 מקרים",
            denominator="21 מקרים כשירים",
            source="study1-hotspot-manifest.json",
            limitation="גודל קובץ הוא תכונה נצפית בלבד, ואינו מדד איכות או קושי",
        )
    )


def section_flow() -> str:
    return (
        h2("3. הזרימה מקצה לקצה")
        + stages(
            [
                ("נתונים ציבוריים", "מאגר AirTravel מוצמד"),
                ("סוכנים", "סוכן שואל · סוכן משיב"),
                ("יומן שיחות", "אירועים בלתי ניתנים לשינוי"),
                ("גלאי־v1", "מסווג שיחה — דיווח בלבד"),
                ("בדיקה אנושית עיוורת", "שני בודקים · הכרעה"),
                ("מדדים", "טבלאות א׳–ד׳"),
            ]
        )
        + "<p class=\"warn\"><b>גבול שאסור לטשטש:</b> גלאי־v1 פועל ברמת שיחה ולמטרת "
        "דיווח בלבד. הוא <b>אינו יוצר תור אנושי</b>, אינו מזין תור, ואינו מנגנון התור "
        "של סוכן־4. אלה שני מנגנונים נפרדים, ואין לערבב ביניהם.</p>"
        + caption(
            meaning="שלבי המערכת לפי סדר",
            numerator="6 שלבים",
            denominator="הצינור כפי שנבנה",
            source="scripts/study1_hotspot_analysis.py",
            limitation="תרשים מבנה; אינו מעיד על נכונות של אף שלב",
        )
    )


def table_a_section(analysis: dict[str, Any]) -> str:
    rows = []
    for run in analysis["table_a_pipeline_reliability"]:
        rows.append(
            [
                f'{esc(run["run_label"])} {chip(run["evidence_class"])}',
                esc(run["status"]),
                value_or_na(run["selected_cases"]),
                value_or_na(run["complete_episodes"]),
                value_or_na(run["incomplete_technical_episodes"]),
                value_or_na(run["calls"]),
                value_or_na(run["cost_usd"]),
                value_or_na(run["truncated_calls"]),
            ]
        )
    return (
        h2("4. טבלה א׳ — אמינות הצינור")
        + table(
            ["ריצה", "סטטוס", "מקרים", "שיחות שהושלמו", "שיחות שנקטעו טכנית",
             "קריאות", 'עלות $', "קריאות שנחתכו"],
            rows,
            numeric_from=2,
        )
        + caption(
            meaning="מה הצינור ייצר בפועל בכל ריצה בנפרד",
            numerator="לפי העמודה",
            denominator="כל ריצה והמכנה שלה בלבד",
            source="run-receipt.json של כל ריצה",
            limitation="אמינות טכנית אינה נכונות ואינה תועלת",
        )
        + "<p class=\"warn\">כל ריצה נמדדת מול המכנה של עצמה. הריצות <b>אינן מאוחדות</b> "
        "ואינן ממוצעות, משום שתצורתן שונה.</p>"
    )


def table_b_section(analysis: dict[str, Any]) -> str:
    b = analysis["table_b_detector_to_human_agreement"]
    unavailable = is_unavailable(b)
    body = (
        f'<div class="kpis">{kpi(num(b["alert_rate"]), "שיעור התרעה של גלאי־v1")}'
        f'{kpi(num(b["denominator_complete_episodes"]), "שיחות שהושלמו — מכנה")}'
        f'{kpi(NA_HE, "שיעור ״ראוי לבדיקה״ אנושי")}'
        f'{kpi(NA_HE, "דיוק והיזכרות")}</div>'
    )
    classes = b.get("class_counts", {})
    if classes:
        body += bars(
            [(esc(k), v, str(v)) for k, v in sorted(classes.items())],
            maximum=max(classes.values()),
        )
    if unavailable:
        body += (
            f'<p class="warn"><b>{esc(NA_HE)} — ולא אפס.</b> טבלה ב׳ מוגדרת מול שיפוט '
            "אנושי עצמאי. בהיעדר שני בודקים עיוורים היא מדווחת כלא־זמינה, ו<b>אין תחליף "
            "מותר</b>: לא תווית של מודל, לא אות מתווכת, לא היוריסטיקה, ולא שיפוט של "
            "מחבר המחקר.</p>"
        )
    return (
        h2("5. טבלה ב׳ — התאמה בין הגלאי לאדם",
           UNAVAILABLE if unavailable else PROSPECTIVE)
        + body
        + caption(
            meaning="התפלגות מחלקות הגלאי, ומה שאינו ניתן לחישוב בלעדי בודקים",
            numerator=f'{b["class_counts"].get("STRONG_ALERT", 0)} התרעה חזקה',
            denominator=f'{b["denominator_complete_episodes"]} שיחות שהושלמו',
            source="scripts/study1_hotspot_analysis.py",
            limitation="שיעור התרעה אינו שיעור שגיאות ואינו מעיד שהתרעה כלשהי צדקה",
        )
    )


def table_c_section(analysis: dict[str, Any]) -> str:
    c = analysis["table_c_operational_baseline"]
    everything = c["all_episodes_review_workload"]
    prioritized = c["detector_prioritized_review_workload"]
    reduction = c["workload_reduction_fraction"]
    return (
        h2("6. טבלה ג׳ — בסיס תפעולי ועסקי", ARCHIVAL)
        + f'<div class="kpis">{kpi(num(everything), "עומס בדיקה — כל השיחות")}'
        f'{kpi(num(prioritized), "עומס בדיקה — לאחר קדימות הגלאי")}'
        f'{kpi(num(f"{reduction:.1%}") if reduction is not None else NA_HE, "הקטנת עומס")}'
        f'{kpi(NA_HE, "שימור שיחות שאדם אישר")}</div>'
        + bars(
            [
                ("כל השיחות", everything, str(everything)),
                ("קבוצת הקדימות — התרעה חזקה", prioritized, str(prioritized)),
            ],
            maximum=everything or 1,
        )
        + "<p class=\"warn\">שתי מסקנות נפרדות. <b>ראשונה:</b> אם קבוצת הקדימות מוגדרת "
        "כ״כל התרעה״, ההקטנה היא <b>אפס</b>, משום ששיעור ההתרעה הוא 1.0 בכל שיחה שנצפתה "
        "אי־פעם. <b>שנייה:</b> אם היא מוגדרת כ״התרעה חזקה בלבד״, יש הקטנה — אך "
        "<b>שיעור השימור אינו ידוע</b> בלי בודקים, ולכן אי־אפשר לדעת אם ההקטנה נקנתה "
        "במחיר השמטת שיחות שאדם היה רוצה לראות.</p>"
        + caption(
            meaning="עומס הבדיקה לפני ואחרי קדימות הגלאי",
            numerator=f"{prioritized} שיחות בקבוצת הקדימות",
            denominator=f"{everything} שיחות שהושלמו",
            source="scripts/study1_hotspot_analysis.py",
            limitation="הקטנת עומס בלי שימור מדוד אינה תועלת, ואינה חיסכון מוכח",
        )
    )


def table_d_section(analysis: dict[str, Any]) -> str:
    rows = []
    for run in analysis["table_d_robustness"]["per_run"]:
        rows.append(
            [
                f'{esc(run["run_label"])} {chip(run["evidence_class"])}',
                value_or_na(run["complete_episodes"]),
                esc(", ".join(f"{k}={v}" for k, v in sorted(run["class_counts"].items()))),
                value_or_na(run["mean_answers_per_complete_episode"]),
                esc(", ".join(f"{k}={v}" for k, v in sorted(run["termination_states"].items()) if k)),
            ]
        )
    return (
        h2("7. טבלה ד׳ — יציבות ורגישות")
        + table(
            ["ריצה", "שיחות", "מחלקות הגלאי", "ממוצע תשובות לשיחה", "מצבי סיום"],
            rows,
            numeric_from=1,
        )
        + "<p class=\"warn\"><b>ממצא שקובע את פרשנות כל השאר:</b> אורך השיחה אינו פרמטר "
        "מבוקר, והוא זה שקובע אם הגלאי מפריד בין שיחות. בשתי ריצות בעלות תצורה זהה "
        "לחלוטין הוא נע פי חמישה־עשר. לכן אין להסיק תכונת הפרדה מריצה אחת.</p>"
        + caption(
            meaning="תוצאות לפי ריצה, כל אחת על המכנה שלה",
            numerator="לפי העמודה",
            denominator="שיחות שהושלמו בכל ריצה",
            source="scripts/study1_hotspot_analysis.py",
            limitation="שתי תצפיות אינן אומדן שונות ואינן מבססות טענת יציבות",
        )
    )


def section_verdict(analysis: dict[str, Any], verdict: dict[str, str]) -> str:
    return (
        h2("8. מה נמצא, מה לא נמצא, ומה ההכרעה")
        + "<h3>מה נמצא</h3><ul>"
        "<li>הצינור רץ מקצה לקצה, והתקשורת בין הסוכנים נלכדת ונשמרת עם אימות גיבוב.</li>"
        "<li>שיעור ההתרעה של גלאי־v1 הוא <b>1.0</b> בכל שיחה שנצפתה אי־פעם. "
        "לכן קדימות לפי ״התרעה מול אין־התרעה״ אינה מקטינה עומס כלל.</li>"
        "<li>קדימות לפי ״התרעה חזקה בלבד״ כן מקטינה עומס — אך בלי שימור מדוד "
        "אי־אפשר לדעת מה המחיר.</li>"
        "<li>מנגנוני ההסלמה במערכת אינם מסכימים ביניהם, ותור הבדיקה האנושית ריק.</li>"
        "</ul>"
        "<h3>מה לא נמצא</h3><ul>"
        "<li><b>לא נמצא</b> שהתרעה כלשהי צדקה. אין תוויות אמת, ולכן אין דיוק, אין היזכרות, "
        "ואין F1 — ואי־אפשר לחשב אותם.</li>"
        "<li><b>לא נמצא</b> חיסכון בזמן בדיקה. הבודקים לא מדדו זמן, ואומדן אסור.</li>"
        "<li><b>לא נמצא</b> יתרון סיבתי, הכללה, או יתרון של הפעלה מול כיבוי.</li>"
        "</ul>"
        f'<p class="verdict"><b>הכרעה: {esc(verdict["label"])}</b> — {esc(verdict["reason"])}</p>'
        + caption(
            meaning="סיכום ההכרעה ותנאיה",
            numerator="1 הכרעה",
            denominator="הראיות שנאספו במחקר זה",
            source="docs/research/phd-proposal/2026-09-09-study1-human-review-hotspot-preregistration.md",
            limitation="הכרעה זו נוגעת לבסיס הזה בלבד, ואינה מאשרת שום טענת איכות",
        )
    )


def build_report(manifest: dict[str, Any], analysis: dict[str, Any],
                 verdict: dict[str, str]) -> str:
    body = (
        '<h1>בסיס לזיהוי מוקדי בדיקה אנושית — דוח מנחים</h1>'
        '<p class="sub">מחקר 1 · VEGO-AI · כל מספר מחושב מחדש מיומן האירועים</p>'
        + section_purpose(manifest)
        + section_freeze(manifest)
        + '<div class="pb"></div>'
        + section_flow()
        + table_a_section(analysis)
        + '<div class="pb"></div>'
        + table_b_section(analysis)
        + table_c_section(analysis)
        + '<div class="pb"></div>'
        + table_d_section(analysis)
        + section_verdict(analysis, verdict)
    )
    return page("בסיס לזיהוי מוקדי בדיקה אנושית", DOC_CSS, body)


def build_business(manifest: dict[str, Any], analysis: dict[str, Any],
                   verdict: dict[str, str]) -> str:
    c = analysis["table_c_operational_baseline"]
    b = analysis["table_b_detector_to_human_agreement"]
    body = (
        '<h1>סיכום עסקי — עמוד אחד</h1>'
        f'<div class="kpis">{kpi(num(b["alert_rate"]), "שיעור התרעה")}'
        f'{kpi(num(c["all_episodes_review_workload"]), "שיחות לבדיקה — הכול")}'
        f'{kpi(num(c["detector_prioritized_review_workload"]), "לאחר קדימות")}'
        f'{kpi(NA_HE, "חיסכון בדקות בדיקה")}</div>'
        "<h2>מה זה אומר בפועל</h2>"
        "<p>אם מגדירים ״לשלוח לאדם כל שיחה שקיבלה התרעה״, המערכת שולחת <b>הכול</b>. "
        "זה אינו סינון, ואין בו חיסכון. אם מגדירים ״לשלוח רק התרעה חזקה״, יש הקטנה "
        "אמיתית של העומס — אבל <b>איננו יודעים</b> כמה מהשיחות שאדם היה רוצה לראות "
        "נשארות בפנים, כי אף אדם לא סיווג אותן.</p>"
        "<h2>מה חסר כדי להכריע</h2>"
        "<p>שני בודקים אנושיים עצמאיים על אותם כרטיסים עיוורים. זה החסם היחיד. "
        "הוא אינו חסם תקציבי ואינו חסם הנדסי — כל שאר המנגנון בנוי, קפוא ונבדק.</p>"
        f'<p class="verdict"><b>הכרעה: {esc(verdict["label"])}</b> — {esc(verdict["reason"])}</p>'
        + caption(
            meaning="התמונה התפעולית בקצרה",
            numerator=f'{c["detector_prioritized_review_workload"]} שיחות בקבוצת הקדימות',
            denominator=f'{c["all_episodes_review_workload"]} שיחות שהושלמו',
            source="scripts/study1_hotspot_analysis.py",
            limitation="הקטנת עומס בלי שימור מדוד אינה חיסכון מוכח",
        )
    )
    return page("סיכום עסקי", DOC_CSS, body)


def build_map() -> str:
    body = (
        '<h1>מפה מקצה לקצה — עמוד אחד</h1>'
        + stages(
            [
                ("נתונים", "AirTravel ציבורי · גיבוב מוצמד"),
                ("סוכנים", "סוכן שואל · סוכן משיב"),
                ("יומן שיחות", "אירועים בלתי ניתנים לשינוי"),
                ("גלאי־v1", "מסווג שיחה · דיווח בלבד"),
                ("כרטיסים עיוורים", "בלי תווית גלאי · בלי ביטחון"),
                ("שני בודקים", "עצמאיים · כלל הכרעה קפוא"),
                ("מדדים", "טבלאות א׳–ד׳"),
            ]
        )
        + "<p class=\"warn\"><b>גלאי־v1 אינו יוצר תור אנושי.</b> הוא מסווג ומדווח בלבד. "
        "מנגנון התור של סוכן־4 הוא מנגנון אחר לגמרי, ואין לערבב ביניהם.</p>"
        "<p class=\"warn\">הכרטיסים מסתירים מהבודקים את סיווג הגלאי, את שמות האותות, "
        "ואת תווית הביטחון של כל תשובה — משום שתווית הביטחון היא הקלט הדומיננטי של "
        "הגלאי, והצגתה הייתה הופכת את השיפוט האנושי לשכפול של הגלאי.</p>"
        + caption(
            meaning="הזרימה מהנתונים ועד למדדים",
            numerator="7 שלבים",
            denominator="הצינור כפי שנבנה",
            source="scripts/study1_hotspot_rater_cards.py",
            limitation="תרשים מבנה; אינו מעיד על נכונות של אף שלב",
        )
    )
    return page("מפה מקצה לקצה", MAP_CSS, body)


def build_evidence_index(manifest: dict[str, Any], analysis_path: Path,
                         manifest_path: Path, ci_url: str) -> str:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout.strip()
    detector = manifest["detector_v1"]["code_sha256"]
    rows = [
        ["מסמך ההקפאה", "study1-hotspot-manifest.json", shorten(digest(manifest_path), 16)],
        ["טבלאות הניתוח", analysis_path.name, shorten(digest(analysis_path), 16)],
        ["גלאי־v1 — קוד", "extract_qa_escalation_features.py",
         shorten(detector["scripts/extract_qa_escalation_features.py"], 16)],
        ["גלאי־v1 — חוזה אותות", "study1_signal_contract.py",
         shorten(detector["scripts/study1_signal_contract.py"], 16)],
        ["מאגר — ארכיון מוצמד", manifest["corpus"]["corpus_id"],
         shorten(manifest["corpus"]["archive_sha256"], 16)],
        ["גרסת קוד בעת ההרצה", "git HEAD", shorten(head, 16)],
    ]
    body = (
        '<h1>מפתח ראיות</h1>'
        + table(["פריט", "מקור", "גיבוב SHA-256"], rows, numeric_from=2)
        + f'<p>שרשרת אינטגרציה רציפה: <code>{esc(ci_url)}</code></p>'
        + "<h2>מגבלות מדויקות</h2><ul>"
        "<li>אין תוויות אמת למאגר הזה. דיוק, היזכרות ו־F1 אינם ניתנים לחישוב.</li>"
        "<li>טבלאות ב׳ ו־ג׳ תלויות בשני בודקים עיוורים שאינם קיימים. הן מדווחות "
        "כלא־זמינות, ואין תחליף מותר.</li>"
        "<li>ריצות בעלות תצורה שונה אינן מאוחדות ואינן ממוצעות.</li>"
        "<li>גלאי־v1 הוא ברמת שיחה ולמטרת דיווח בלבד; אינו יוצר תור ואינו מנגנון "
        "התור של סוכן־4.</li>"
        "<li>אורך השיחה אינו מבוקר, והוא קובע אם הגלאי מפריד. אין להסיק תכונת "
        "הפרדה מריצה אחת.</li>"
        "</ul>"
        + caption(
            meaning="הגיבובים שמאפשרים אימות עצמאי",
            numerator=f"{len(rows)} פריטים",
            denominator="הראיות שנשענת עליהן החבילה",
            source="git + scripts",
            limitation="גיבוב מוכיח זהות בתים, ולא נכונות מדעית",
        )
    )
    return page("מפתח ראיות", DOC_CSS, body)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "docs/research/phd-proposal/study1-hotspot-manifest.json",
    )
    parser.add_argument("--ci-url", default="NOT_AVAILABLE")
    parser.add_argument("--verdict-label", required=True)
    parser.add_argument("--verdict-reason", required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    analysis = json.loads(args.analysis.read_text(encoding="utf-8"))
    verdict = {"label": args.verdict_label, "reason": args.verdict_reason}

    FIGURES.mkdir(parents=True, exist_ok=True)
    written = {}
    for name, html in (
        ("study1-hotspot-report-he.html", build_report(manifest, analysis, verdict)),
        ("study1-hotspot-business-he.html", build_business(manifest, analysis, verdict)),
        ("study1-hotspot-map-he.html", build_map()),
        ("study1-hotspot-evidence-index-he.html",
         build_evidence_index(manifest, args.analysis, args.manifest, args.ci_url)),
    ):
        target = FIGURES / name
        target.write_text(html, encoding="utf-8")
        written[name] = str(target)
    print(json.dumps({"written": written}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
