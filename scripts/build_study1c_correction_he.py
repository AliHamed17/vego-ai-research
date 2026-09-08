"""Build the Hebrew RTL correction report and the figure guide for Study 1C.

Both documents are generated from the reconciliation output and the claim ledger, so a number
cannot appear in Hebrew that the machine-readable record does not contain, and a claim the ledger
marks prohibited cannot be restated as permitted on its way into prose.

The correction report leads with what was wrong rather than with what was found. A correction
that opens with results invites the reader to keep the old conclusion and treat the correction as
a footnote, which is the opposite of its purpose.

No provider is contacted.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from study1_rtl_document import (  # noqa: E402
    ARCHIVAL,
    DOC_CSS,
    FIXTURE,
    UNAVAILABLE,
    caption,
    chip,
    esc,
    kpi,
    page,
    table,
)

FIGURES = ROOT / "docs/research/phd-proposal/figures"
NA_HE = "אינו זמין"


def h2(title: str, evidence_class: str | None = None) -> str:
    tail = f" {chip(evidence_class)}" if evidence_class else ""
    return f"<h2>{esc(title)}{tail}</h2>"


def build_correction(recon: dict[str, Any], ledger: dict[str, Any]) -> str:
    def cell(value):
        return NA_HE if value in (None, "NOT_AVAILABLE") else str(value)

    rows = []
    for run in recon["runs"]:
        cost = run.get("cost", {})
        rows.append(
            [
                esc(run["run_id"]),
                esc(run["execution_status"]),
                cell(run.get("complete_episodes")),
                "%s / %s / %s" % (
                    cell(run.get("detector_class_STRONG_ALERT")),
                    cell(run.get("detector_class_WEAK_ALERT")),
                    cell(run.get("detector_class_NO_ALERT")),
                ),
                cell(run.get("episodes_selected_for_review")),
                cell(run.get("unvalidated_screening_fraction")),
                esc(cost.get("status", NA_HE)) + " " + str(cost.get("usd", "")),
            ]
        )
    body = (
        "<h1>מחקר 1C — דוח תיקון ופרשנות</h1>"
        '<p class="sub">מה היה שגוי, מה מתוקן, ומה מותר לטעון מכאן ואילך</p>'
        + h2("1. שלושה תיקונים, לפני כל תוצאה")
        + "<p><b>תיקון א׳ — המילה ״התאמה״ הייתה דו־משמעית.</b> ההשוואה בין כלל בסיס לגלאי־v1 "
        "אפשרית בשתי רמות שונות, והתשובה שונה בכל אחת:</p>"
        + '<div class="two">'
        "<div><h3>רמת שלוש המחלקות</h3><p>משווים את התווית עצמה: התרעה חזקה / חלשה / ללא "
        "התרעה. בהרצה 1 <b>אף כלל בסיס אינו זהה</b> לגלאי ברמה הזו.</p></div>"
        "<div><h3>רמת ההחלטה הבינארית</h3><p>משווים רק את ההחלטה ״לשלוח לבדיקה או לא״. "
        "בהרצה 1 הגלאי שלח את <b>כל</b> 11 השיחות, ולכן הכלל ״תמיד התרעה״ <b>זהה לו "
        "לחלוטין</b> ברמה הזו.</p></div></div>"
        + "<p class=\"warn\">שתי הקביעות נכונות, והן אינן סותרות. המשפט ״אף כלל בסיס אינו "
        "מתאים״ נכתב בלי לציין את הרמה, ולכן היה <b>שגוי ברמה הבינארית</b>. מכאן ואילך כל "
        "אמירה על התאמה חייבת לנקוב ברמה.</p>"
        + "<p><b>תיקון ב׳ — ״אף שיחה מעולם לא קיבלה ללא־התרעה״ נאמר בלי היקף.</b> הקביעה "
        "נכונה עבור ההרצה המאושרת ושתי הרצות המסגרת המלאה, וזה ההיקף שיש לכתוב. המילה "
        "״מעולם״ בלי היקף חלה גם על הרצות שה-head אינו יכול לאמת, ולכן אינה ניתנת להערכה. "
        "הניסוח הנכון: <b>״בהרצה המאושרת ובשתי הרצות המסגרת המלאה, אף שיחה שהושלמה לא "
        "סווגה ללא־התרעה״</b>.</p>"
        + "<p><b>תיקון ג׳ — שבר סינון תואר כהקטנת עומס.</b> בחירה בפחות שיחות אינה עבודה "
        "אנושית שנחסכה. הכמות נקראת מעתה <code>UNVALIDATED_SCREENING_FRACTION</code>, ואינה "
        "ראיה לתועלת, לשימור, לנכונות או לבטיחות.</p>"
        + caption(
            meaning="שלושת התיקונים ומה שהם מחליפים",
            numerator="3 תיקונים",
            denominator="החבילה כפי שפורסמה קודם",
            source="study1c-reconciliation.json",
            limitation="תיקון ניסוח אינו ראיה חדשה ואינו משנה אף מספר שנמדד",
        )
        + '<div class="pb"></div>'
        + h2("2. טבלת ההתאמה — כל הרצה על המכנה של עצמה", ARCHIVAL)
        + table(
            ["הרצה", "סטטוס", "שיחות שהושלמו", "חזקה / חלשה / ללא",
             "נשלחו לבדיקה", "שבר סינון", "עלות"],
            rows,
            numeric_from=2,
        )
        + "<p class=\"warn\">אין שורת סיכום, ולא תהיה. ההרצות נבדלות במספר המקרים ובתצורה, "
        "ואיחוד המכנים היה מתאר הרצה שמעולם לא בוצעה.</p>"
        + caption(
            meaning="כל ההרצות זו לצד זו, בלי איחוד",
            numerator=f"{len(rows)} הרצות",
            denominator="כל אחת והמכנה שלה בלבד",
            source="study1c-reconciliation.json",
            limitation="שבר סינון אינו חיסכון בעבודה אנושית ואינו תועלת",
        )
        + h2("3. מעמד מחקר המוקדים ומשיכת חבילת התוצאות", UNAVAILABLE)
        + "<p>המניפסט המעקב מצהיר <code>PREREGISTERED_NOT_EXECUTED</code>, ואין קבלה, יומן "
        "אירועים או פנקס קריאות מעקב במאגר. ארטיפקטים פרטיים קיימים מקומית, אך <b>ארטיפקט "
        "פרטי הוא ראיה לבעליו ולא לאיש אחר</b>. לכן המעמד הוא "
        "<code>PREREGISTERED_NOT_EXECUTED_OR_UNVERIFIED</code>.</p>"
        "<p class=\"warn\"><b>חבילת תוצאות המוקדים נמשכה מן ה-head.</b> הדוח, המצגת, "
        "הסיכום העסקי, המפה ומפתח הראיות הוסרו. הם דיווחו על הרצה שקורא אינו יכול לאמת, "
        "וסיימו בהכרעת <code>CONDITIONAL GO</code> שאיש לא אימת. המספרים שלהם <b>אינם "
        "מפורסמים כאן מחדש</b>, משום שפרסומם היה מציג הרצה בלתי־מאומתת כהרצה שבוצעה. "
        "ההיסטוריה נשמרה; דבר לא נכתב מחדש.</p>"
        "<p>בנוסף, זרע ההגרלה נקבע <b>לאחר</b> שתוצאות המסגרת המלאה כבר היו ידועות. ההגרלה "
        "ניתנת לשחזור, אך אין רישום התחייבות שקדם לתוצאות. לכן הדגימה מסווגת "
        "<code>PILOT_INFORMED_POST_OUTCOME</code> ו<b>אינה פרוספקטיבית</b>.</p>"
        + caption(
            meaning="המעמד הניתן לאימות מן המאגר",
            numerator="1 מחקר",
            denominator="הראיות המעקב בלבד",
            source="study1-hotspot-manifest.json",
            limitation="מעמד אינו תוצאה; הוא רק קובע מה מותר לטעון",
        )
        + '<div class="pb"></div>'
        + h2("4. ההכרעה הנוכחית", UNAVAILABLE)
        + '<p class="verdict"><b>DESCRIPTIVE_RULE_BEHAVIOUR_ONLY / '
        "NOT_READY_FOR_SCIENTIFIC_CONCLUSION</b></p>"
        "<p>אין דירוגים אנושיים עיוורים ואין מדידת זמן בדיקה, ולכן אף טענה על דיוק, תועלת, "
        "עומס, שימור, סיבתיות, הכללה או תקפות מוקדים אינה ניתנת לחישוב. מה שנותר הוא "
        "התנהגות הכלל על קלטים שנרשמו.</p>"
        "<p class=\"warn\"><code>CONDITIONAL GO</code> נמשכה. הכרעה כזו מרמזת על תחום שבו "
        "הבסיס מבוסס; איש לא אימת שרשרת ראיות שלמה ואיש לא הגדיר תחום כזה.</p>"
        + h2("5. הממצא החזק ביותר שניתן להגנה", ARCHIVAL)
        + '<p class="verdict">תחת הכלל הרשום, סיווג ההתרעה רגיש מאוד לאורך שיחת השאלה־תשובה; '
        "שיחות ארוכות נוטות להיסחף אל ״התרעה חזקה״. זהו ממצא על <b>התנהגות הכלל</b>, "
        "ואינו אימות של צורך אמיתי בהתערבות אנושית.</p>"
        + "<p>מה שאינו נובע מכך: אין כאן זיהוי מוקדים, אין יעילות תיעדוף, אין דיוק או "
        "היזכרות, אין תועלת אנושית, אין סיבתיות, אין הכללה, ואין עדיפות של VEGO-AI. כל אחד "
        "מאלה דורש תוויות אנושיות עצמאיות שאינן קיימות.</p>"
        + f'<div class="kpis">{kpi(str(ledger["counts"]["permitted"]), "טענות מותרות")}'
        f'{kpi(str(ledger["counts"]["prohibited"]), "טענות אסורות")}'
        f'{kpi(NA_HE, "דיוק · היזכרות · F1")}'
        f'{kpi(NA_HE, "חיסכון בזמן בדיקה")}</div>'
        + caption(
            meaning="הממצא המותר וגבולותיו",
            numerator="1 ממצא",
            denominator="ההרצות שתועדו",
            source="study1c-claim-ledger.json",
            limitation="ממצא על התנהגות כלל אינו ממצא על העולם",
        )
    )
    return page("מחקר 1C — דוח תיקון ופרשנות", DOC_CSS, body)


def build_figure_guide() -> str:
    body = (
        "<h1>מדריך לקריאת התרשימים</h1>"
        '<p class="sub">מה כל תרשים מראה, ומה אסור להסיק ממנו</p>'
        + h2("תרשים 1 — רגישות הכלל", FIXTURE)
        + "<p><b>מה מוצג:</b> ההסתברות שהכלל יסמן ״התרעה חזקה״ כפונקציה של מספר התשובות "
        "בשיחה, תחת הנחה מפורשת שהתשובות בלתי־תלויות.</p>"
        "<p><b>מה אינו מוצג:</b> זו אינה עקומת דיוק ואינה הסתברות מן העולם האמיתי. "
        "הנתונים אינם מאמתים את הנחת אי־התלות. הציר האופקי הוא <b>מספר תשובות</b>, "
        "לא מספר סבבי שאלה־תשובה.</p>"
        + h2("תרשים 2 — כללי בסיס, שני לוחות", ARCHIVAL)
        + '<div class="two">'
        "<div><h3>לוח א׳ — שלוש מחלקות</h3><p>השוואת התווית: חזקה / חלשה / ללא. "
        "כתום = זהה לגלאי ברמה הזו.</p></div>"
        "<div><h3>לוח ב׳ — החלטה בינארית</h3><p>השוואת ההחלטה לשלוח לבדיקה בלבד. "
        "כתום = זהה לגלאי ברמה הזו.</p></div></div>"
        + "<p class=\"warn\">שני הלוחות עונים על שאלות שונות. <b>אסור לצטט מספר מלוח אחד "
        "כאילו הוא של האחר.</b> הצבע מסמן זהות <b>ברמה של אותו לוח</b> ותו לא.</p>"
        + h2("תרשים 3 — שני מנגנוני הסלמה", ARCHIVAL)
        + "<p><b>מה מוצג:</b> מספר הקטעים שסומנו ״טעות תחום״ בכל מקרה, לצד האם הגלאי בחר "
        "את המקרה לבדיקה.</p>"
        "<p><b>מה אינו מוצג:</b> שני המנגנונים פועלים על <b>יחידות ניתוח שונות</b> — הגלאי "
        "על שיחות, שלב הכיסוי על קטעים. <b>אף אחד מהם אינו אמת קרקע.</b> מקרה שהגלאי שותק "
        "לגביו <b>אינו מקרה שהוכח כבטוח</b>, ותוויות ״טעות תחום״ <b>אינן תוויות אמת</b> "
        "עבור הגלאי. מה שמוצג הוא שכיחות משותפת בלבד.</p>"
        + caption(
            meaning="כללי קריאה לשלושת התרשימים",
            numerator="3 תרשימים",
            denominator="החבילה המתוקנת",
            source="scripts/render_study1c_figures.py",
            limitation="מדריך קריאה אינו ראיה ואינו מוסיף תוקף לאף תרשים",
        )
    )
    return page("מדריך לקריאת התרשימים", DOC_CSS, body)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reconciliation",
        type=Path,
        default=ROOT / "docs/research/phd-proposal/study1c-reconciliation.json",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=ROOT / "docs/research/phd-proposal/study1c-claim-ledger.json",
    )
    args = parser.parse_args()

    recon = json.loads(args.reconciliation.read_text(encoding="utf-8"))
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    FIGURES.mkdir(parents=True, exist_ok=True)
    written = {}
    for name, html in (
        ("study1c-correction-he.html", build_correction(recon, ledger)),
        ("study1c-figure-guide-he.html", build_figure_guide()),
    ):
        target = FIGURES / name
        target.write_text(html, encoding="utf-8")
        written[name] = str(target)
    print(json.dumps({"written": written}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
