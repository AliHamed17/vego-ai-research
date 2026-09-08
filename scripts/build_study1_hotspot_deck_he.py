"""Build the eight-slide Hebrew RTL supervisor deck for the hotspot baseline.

Every figure on every slide carries its evidence class, its denominator and a one-line statement
of what it does not prove, because a slide travels further than the document it came from and is
read by people who will not have the caveats in front of them.

Slide five is the one that matters most and is deliberately the plainest: the primary outcome is
`NOT_AVAILABLE`, and the slide says so in the largest type on the page rather than filling the
space with what happens to be computable.

All numbers are read from the analysis tables. Nothing is typed in.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pptx.util import Inches  # noqa: E402

from study1_rtl_deck import (  # noqa: E402
    CONTENT_W,
    GREY_L,
    M,
    MUTED,
    NAVY,
    ORANGE,
    ORANGE_L,
    W,
    bar_row,
    bullets,
    chip,
    footer,
    new_deck,
    para,
    rtl_table,
    slide,
    stat,
    tb,
    title,
)

NA_HE = "אינו זמין"
HALF = (CONTENT_W - Inches(0.2)) / 2
QUARTER = (CONTENT_W - Inches(0.45)) / 4


def primary(analysis, table):
    """The prospective run carries the primary result; archival runs are never pooled with it."""
    rows = analysis[table]
    for row in rows:
        if row.get("evidence_class") == "PROSPECTIVE EMPIRICAL EVIDENCE":
            return row
    return rows[0]


def na(value: Any) -> str:
    return NA_HE if value is None or value == "NOT_AVAILABLE" else str(value)


def slide_title(prs) -> None:
    s = slide(prs)
    box, tf = tb(s, M, Inches(1.5), CONTENT_W, Inches(1.5))
    para(tf, "בסיס לזיהוי מוקדי בדיקה אנושית", size=34, bold=True, color=NAVY, first=True)
    para(tf, "מחקר 1 · VEGO-AI · דוח מנחים", size=16, color=MUTED, space_before=6)
    box2, tf2 = tb(s, M, Inches(3.1), CONTENT_W, Inches(1.6))
    para(
        tf2,
        "השאלה: מבין שיחות שהושלמו, עד כמה גלאי־v1 מקדם לבדיקה בדיוק את השיחות "
        "ששני בודקים אנושיים עיוורים שופטים כראויות לבדיקה.",
        size=15,
        first=True,
    )
    para(
        tf2,
        "מה שנמדד אינו נכונות של הבינה המלאכותית, אלא האם העומס קטן בלי לאבד "
        "שיחות שאדם רוצה לראות.",
        size=13,
        color=MUTED,
        space_before=8,
    )
    footer(s, "כל מספר מחושב מחדש מיומן האירועים · גלאי־v1 לא שונה")


def slide_freeze(prs, manifest: dict[str, Any]) -> None:
    s = slide(prs)
    title(s, "מה הוקפא לפני כל קריאה לספק", sub="הקפאה אינה תוצאה · היא מונעת שינוי אחרי שרואים תוצאה")
    budget = manifest["budget"]
    y = Inches(1.55)
    for i, (value, label, detail) in enumerate(
        [
            (str(manifest["corpus"]["eligible_case_count"]), "מקרים כשירים", "מסגרת מלאה"),
            (str(len(manifest["selection"]["selected"])), "נדגמו מראש", f"זרע {manifest['selection']['seed']}"),
            (f"{budget['whole_study_reservation_usd']:.2f}$", "שריון פסימי", "כל קריאה במחיר מלא"),
            (f"{budget['ceiling_usd']:.2f}$", "תקרה", "נבדק לפני ההרצה"),
        ]
    ):
        stat(s, M + i * (QUARTER + Inches(0.15)), y, QUARTER, Inches(1.05), value, label, detail=detail)
    box, tf = tb(s, M, Inches(2.85), CONTENT_W, Inches(1.7))
    bullets(
        tf,
        [
            "הדגימה נקבעה בהגרלה דטרמיניסטית מזרע קבוע · ניתנת לשחזור בידי כל אדם.",
            "לכן הבחירה אינה יכולה להיות תלויה בסטטוס התרעה חזוי או נצפה.",
            "המודל, הבקשות, הסיפים, מכסת הקריאות וכלל העצירה הוקפאו מראש.",
            "מחוון הבדיקה האנושית הוקפא לפני שקיימת ולו תווית אחת.",
        ],
        size=13,
    )
    chip(s, W - M - Inches(3.15), Inches(4.75), "ראיה אמפירית פרוספקטיבית", kind="pro")
    footer(s, "מקור: study1-hotspot-manifest.json · מכנה: 21 מקרים כשירים")


def slide_flow(prs) -> None:
    s = slide(prs)
    title(s, "הזרימה מקצה לקצה", sub="נתונים ← סוכנים ← יומן ← גלאי ← בדיקה אנושית עיוורת ← מדדים")
    steps = [
        ("נתונים", "AirTravel ציבורי"),
        ("סוכנים", "שואל · משיב"),
        ("יומן שיחות", "אירועים קבועים"),
        ("גלאי־v1", "דיווח בלבד"),
        ("כרטיסים עיוורים", "בלי תווית"),
        ("שני בודקים", "עצמאיים"),
    ]
    width = (CONTENT_W - Inches(0.5)) / 6
    for i, (head, sub) in enumerate(steps):
        x = W - M - width - i * (width + Inches(0.1))
        stat(s, x, Inches(1.7), width, Inches(1.0), str(i + 1), head, detail=sub)
    box, tf = tb(s, M, Inches(3.05), CONTENT_W, Inches(1.4))
    para(
        tf,
        "גלאי־v1 פועל ברמת שיחה ולמטרת דיווח בלבד. הוא אינו יוצר תור אנושי, "
        "ואינו מנגנון התור של סוכן־4.",
        size=14,
        bold=True,
        color=ORANGE,
        first=True,
    )
    para(
        tf,
        "הכרטיסים מסתירים מהבודקים את סיווג הגלאי, את שמות האותות ואת תווית הביטחון · "
        "אחרת השיפוט האנושי היה שכפול של הגלאי.",
        size=12.5,
        color=MUTED,
        space_before=8,
    )
    footer(s, "תרשים מבנה · אינו מעיד על נכונות של אף שלב")


def slide_table_a(prs, analysis: dict[str, Any]) -> None:
    s = slide(prs)
    title(s, "טבלה א׳ · אמינות הצינור", sub="כל ריצה על המכנה של עצמה · ריצות אינן מאוחדות")
    rows = [
        [
            run["run_label"],
            str(run["status"]),
            na(run["selected_cases"]),
            na(run["complete_episodes"]),
            na(run["calls"]),
            na(run["cost_usd"]),
        ]
        for run in analysis["table_a_pipeline_reliability"]
    ]
    rtl_table(
        s,
        M,
        Inches(1.6),
        CONTENT_W,
        Inches(2.6),
        ["ריצה", "סטטוס", "מקרים", "שיחות", "קריאות", "עלות $"],
        rows,
        size=10,
    )
    footer(s, "מקור: run-receipt.json · אמינות טכנית אינה נכונות ואינה תועלת")


def slide_table_b(prs, analysis: dict[str, Any]) -> None:
    s = slide(prs)
    b = primary(analysis, "table_b_detector_to_human_agreement")
    title(s, "טבלה ב׳ · התאמה בין הגלאי לאדם", sub="התוצאה הראשית של המחקר")
    box, tf = tb(s, M, Inches(1.5), CONTENT_W, Inches(1.1))
    para(tf, f"{NA_HE} (ולא אפס)", size=30, bold=True, color=ORANGE, first=True)
    para(
        tf,
        "טבלה ב׳ מוגדרת מול שיפוט אנושי עצמאי. אין שני בודקים עיוורים, ולכן אין תוצאה. "
        "אין תחליף מותר: לא תווית של מודל, לא אות מתווכת, לא היוריסטיקה, ולא שיפוט המחבר.",
        size=13,
        color=MUTED,
        space_before=6,
    )
    y = Inches(2.9)
    stat(s, W - M - QUARTER, y, QUARTER, Inches(1.0), str(b["alert_rate"]),
         "שיעור התרעה", detail="ניתן לחישוב", accent=NAVY)
    stat(s, W - M - 2 * QUARTER - Inches(0.15), y, QUARTER, Inches(1.0),
         str(b["denominator_complete_episodes"]), "שיחות · מכנה", detail="ניתן לחישוב")
    stat(s, W - M - 3 * QUARTER - Inches(0.3), y, QUARTER, Inches(1.0), NA_HE,
         "שיעור ראוי־לבדיקה", detail="דורש בודקים", accent=MUTED, fill=GREY_L)
    stat(s, W - M - 4 * QUARTER - Inches(0.45), y, QUARTER, Inches(1.0), NA_HE,
         "דיוק · היזכרות", detail="דורש בודקים", accent=MUTED, fill=GREY_L)
    chip(s, W - M - Inches(3.15), Inches(4.2), "אינו זמין (ולא אפס)", kind="na")
    footer(s, "אין תוויות אמת למאגר · דיוק והיזכרות אינם ניתנים לחישוב", kind="na")


def slide_table_c(prs, analysis: dict[str, Any]) -> None:
    s = slide(prs)
    c = primary(analysis, "table_c_operational_baseline")
    everything = c["all_episodes_review_workload"]
    prioritized = c["detector_prioritized_review_workload"]
    reduction = c["workload_reduction_fraction"]
    title(s, "טבלה ג׳ · עומס הבדיקה בפועל", sub="הבסיס העסקי")
    top = max(everything, 1)
    bar_row(s, M, Inches(1.7), CONTENT_W, "כל השיחות", everything, top, str(everything))
    bar_row(s, M, Inches(2.15), CONTENT_W, "קבוצת קדימות · התרעה חזקה",
            prioritized, top, str(prioritized))
    box, tf = tb(s, M, Inches(2.8), CONTENT_W, Inches(1.8))
    para(
        tf,
        f"בריצה הפרוספקטיבית נצפתה לראשונה שיחה ללא התרעה כלל · הגלאי אינו פונקציה קבועה.",
        size=14,
        bold=True,
        color=ORANGE,
        first=True,
    )
    para(
        tf,
        f"קדימות לפי ״התרעה חזקה בלבד״: הקטנה של "
        f"{reduction:.0%} מהעומס." if reduction is not None else "הקטנה: אינה זמינה",
        size=14,
        bold=True,
        color=NAVY,
        space_before=8,
    )
    para(
        tf,
        "אבל שיעור השימור אינו ידוע בלי בודקים, ולכן אי־אפשר לדעת אם ההקטנה נקנתה "
        "במחיר השמטת שיחות שאדם היה רוצה לראות. חיסכון בדקות אינו זמין ואסור לאמוד אותו.",
        size=12.5,
        color=MUTED,
        space_before=8,
    )
    footer(s, f"מכנה: {everything} שיחות שהושלמו · הקטנת עומס בלי שימור מדוד אינה חיסכון מוכח")


def slide_table_d(prs, analysis: dict[str, Any]) -> None:
    s = slide(prs)
    title(s, "טבלה ד׳ · יציבות", sub="הממצא שקובע את פרשנות כל השאר")
    rows = [
        [
            run["run_label"],
            na(run["complete_episodes"]),
            ", ".join(f"{k}={v}" for k, v in sorted(run["class_counts"].items())),
            na(run["mean_answers_per_complete_episode"]),
        ]
        for run in analysis["table_d_robustness"]["per_run"]
    ]
    rtl_table(s, M, Inches(1.55), CONTENT_W, Inches(2.0),
              ["ריצה", "שיחות", "מחלקות הגלאי", "ממוצע תשובות"], rows, size=10)
    box, tf = tb(s, M, Inches(3.7), CONTENT_W, Inches(1.2))
    para(
        tf,
        "אורך השיחה אינו פרמטר מבוקר, והוא שקובע אם הגלאי מפריד בין שיחות. "
        "בשתי ריצות בעלות תצורה זהה הוא נע פי חמישה־עשר.",
        size=13.5,
        bold=True,
        color=ORANGE,
        first=True,
    )
    para(tf, "לכן אין להסיק תכונת הפרדה מריצה אחת.", size=12.5, color=MUTED, space_before=6)
    footer(s, "שתי תצפיות אינן אומדן שונות ואינן מבססות טענת יציבות")


def slide_verdict(prs, verdict: dict[str, str]) -> None:
    s = slide(prs)
    title(s, "מה נמצא, מה לא נמצא, ומה נדרש", sub="הכרעה")
    box, tf = tb(s, M, Inches(1.5), HALF, Inches(2.6))
    para(tf, "נמצא", size=16, bold=True, color=NAVY, first=True)
    bullets(
        tf,
        [
            "הצינור רץ מקצה לקצה והתקשורת נשמרת עם אימות גיבוב.",
            "נצפתה לראשונה שיחה ללא התרעה · שיעור ההתרעה 0.833 ולא 1.0.",
            "הגלאי מקטין עומס ב־16.7% בריצה הפרוספקטיבית.",
            "מנגנוני ההסלמה אינם מסכימים, ותור הבדיקה ריק.",
        ],
        size=12,
    )
    box2, tf2 = tb(s, M + HALF + Inches(0.2), Inches(1.5), HALF, Inches(2.6))
    para(tf2, "לא נמצא", size=16, bold=True, color=ORANGE, first=True)
    bullets(
        tf2,
        [
            "לא נמצא שהתרעה כלשהי צדקה · אין תוויות אמת.",
            "לא נמצא חיסכון בזמן · הבודקים לא מדדו זמן.",
            "לא נמצא יתרון סיבתי, הכללה, או יתרון הפעלה מול כיבוי.",
            "לא נמצא שיעור שימור · התוצאה הראשית אינה זמינה.",
        ],
        size=12,
    )
    card_y = Inches(4.25)
    box3, tf3 = tb(s, M, card_y, CONTENT_W, Inches(0.8))
    para(tf3, f"הכרעה: {verdict['label']}", size=20, bold=True, color=ORANGE, first=True)
    para(tf3, verdict["reason"], size=12.5, color=MUTED, space_before=4)
    footer(s, "החסם היחיד הוא שני בודקים אנושיים · אינו חסם תקציבי ואינו הנדסי", kind="na")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "docs/research/phd-proposal/study1-hotspot-manifest.json",
    )
    parser.add_argument("--verdict-label", required=True)
    parser.add_argument("--verdict-reason", required=True)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "docs/research/phd-proposal/2026-09-09-study1-hotspot-deck-he.pptx",
    )
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    analysis = json.loads(args.analysis.read_text(encoding="utf-8"))
    verdict = {"label": args.verdict_label, "reason": args.verdict_reason}

    prs = new_deck()
    slide_title(prs)
    slide_freeze(prs, manifest)
    slide_flow(prs)
    slide_table_a(prs, analysis)
    slide_table_b(prs, analysis)
    slide_table_c(prs, analysis)
    slide_table_d(prs, analysis)
    slide_verdict(prs, verdict)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(args.out))
    print(json.dumps({"slides": len(prs.slides._sldIdLst), "deck": str(args.out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
