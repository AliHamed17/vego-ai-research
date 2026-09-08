"""One-page Hebrew right-to-left end-to-end visual of the executed study."""

from __future__ import annotations

from pathlib import Path
from typing import Any

HEBREW_FONT = Path("C:/Windows/Fonts/david.ttf")
HEBREW_FONT_BOLD = Path("C:/Windows/Fonts/davidbd.ttf")


def he(text: str) -> str:
    from bidi.algorithm import get_display

    return get_display(text)


def build_e2e_visual(analysis: dict[str, Any], out_dir: Path) -> dict[str, Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    regular = font_manager.FontProperties(fname=str(HEBREW_FONT), size=10)
    bold = font_manager.FontProperties(fname=str(HEBREW_FONT_BOLD), size=12)
    title_font = font_manager.FontProperties(fname=str(HEBREW_FONT_BOLD), size=17)
    small = font_manager.FontProperties(fname=str(HEBREW_FONT), size=8.5)

    cond = analysis["conditions"]
    on, off = cond["VEGO_AI_ON"], cond["VEGO_AI_OFF"]
    det = analysis["detector"]
    budget = analysis["budget"]
    n = len(analysis["case_ids"])
    mode_label = "ראיות אמפיריות פרוספקטיביות" if analysis["mode"] == "LIVE" else "תוצר הנדסי בלבד (ריצת בדיקה עם ספק מדומה)"

    steps = [
        ("קורפוס ציבורי", f"Text2UML AirTravel\n{21} מודלים מועמדים כשירים\nכל תקציר SHA-256 אומת"),
        ("בחירת מקרים", f"כלל בר-ביצוע, סיד 20260908\n{n} מקרים נבחרו, {21 - n} הוצאו\nלפני כל פלט"),
        ("הקפאה", "פרה-רגיסטרציה, מניפסט חתום-עצמית,\nטביעת פקודה, תקציב, סכמת קבלה,\nמדיניות פרטיות, חוזה טענות"),
        ("שערים", f"{sum(1 for g in analysis['gates'].values() if g['passed'])}/{len(analysis['gates'])} עברו\nHEAD = CI ירוק, עץ נקי,\nרזרבציה עד 5.90$, אישור חד-פעמי"),
        ("VEGO-AI_OFF", f"קריאה ישירה אחת למקרה\n{off['requests']} בקשות, {off['completed']}/{off['planned']} פריטים\n{off['cost_usd']:.4f}$ · {off['elapsed_seconds']:.0f} שניות"),
        ("VEGO-AI_ON", f"4 סוכנים + שאלה–תשובה מתועדת\n{on['requests']} בקשות, {on['completed']}/{on['planned']} פריטים\n{on['cost_usd']:.4f}$ · {on['elapsed_seconds']:.0f} שניות"),
        ("Detector-v1", f"תווית דיווח בלבד, ON בלבד\n{det['episodes_total']} אפיזודות · {det['candidate_alerts']} מועמדות לבדיקה\nOFF: לא רלוונטי (לא אפס)"),
        ("קבלות ואגרגט", f"קבלה חתומה, יומן קריאות, מניפסט פלט\nאגרגט ציבורי מוסווה\nסה\"כ {budget['requests']} בקשות · {budget['actual_cost_usd']:.4f}$ מתוך 6.00$"),
        ("אימות", "חישוב מחדש של כל ערך מפורסם\nמתוך הראיות הפרטיות\nהתאמת תקצירים"),
        ("הערכה אנושית", "כרטיסים עיוורים לשני מעריכים\nהחלטה: ראוי לבדיקה / לא / מידע חסר\nמצב: NOT_MEASURED"),
    ]

    fig = plt.figure(figsize=(16.54, 11.69))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.text(99, 96, he("מחקר 2 — ניסוי פרוספקטיבי מזווג VEGO-AI_ON לעומת VEGO-AI_OFF: מקצה לקצה"), ha="right", va="top", fontproperties=title_font)
    ax.text(99, 92.3, he(f"ריצה {analysis['run_id']} · מודל {analysis['model']['model']} · HEAD {analysis['execution_git_sha'][:12]} · סיווג ראיות: {mode_label}"), ha="right", va="top", fontproperties=regular)

    cols = 5
    box_w, box_h = 17.5, 26
    x_positions = [99 - box_w - i * (box_w + 1.9) for i in range(cols)]
    y_positions = [60, 25]
    for index, (title, body) in enumerate(steps):
        row, col = divmod(index, cols)
        x, y = x_positions[col], y_positions[row]
        color = "#DDEBF7" if title.endswith("_ON") else "#FCE4D6" if title.endswith("_OFF") else "#F2F2F2"
        if title == "Detector-v1":
            color = "#E2EFDA"
        if title == "הערכה אנושית":
            color = "#FFF2CC"
        ax.add_patch(FancyBboxPatch((x, y), box_w, box_h, boxstyle="round,pad=0.4,rounding_size=1.2", linewidth=1.2, edgecolor="#404040", facecolor=color))
        ax.text(x + box_w - 0.9, y + box_h - 1.6, he(f"{index + 1}. {title}"), ha="right", va="top", fontproperties=bold)
        for line_index, line in enumerate(body.split("\n")):
            ax.text(x + box_w - 0.9, y + box_h - 6.2 - line_index * 4.1, he(line), ha="right", va="top", fontproperties=regular)
        if col < cols - 1 and index != len(steps) - 1:
            ax.add_patch(FancyArrowPatch((x, y + box_h / 2), (x - 1.9, y + box_h / 2), arrowstyle="-|>", mutation_scale=14, color="#404040", linewidth=1.2))
        elif row == 0 and col == cols - 1:
            ax.add_patch(FancyArrowPatch((x + box_w / 2, y), (x_positions[0] + box_w / 2, y_positions[1] + box_h), arrowstyle="-|>", mutation_scale=14, color="#404040", linewidth=1.2, connectionstyle="arc3,rad=-0.25"))

    footer = [
        "גבול טענות: השוואה תיאורית מזווגת של שני זרמי עבודה על קורפוס ציבורי אחד שנוצר על ידי מודלי שפה, מודל ספק אחד, יום אחד.",
        "אין טענת עדיפות, תועלת אנושית, נכונות התרעות, דיוק, רגישות, F1, סיבתיות, ייצוגיות או הכללה.",
        "OFF אינו \"בלי בינה מלאכותית\": אותו מודל, אותם מקרים, אותה סכמת פלט, אותה תקרת פלט, אותה מדיניות תקציב — ללא פירוק לסוכנים, ללא שאלה–תשובה וללא לולאת סבבים.",
        "Detector-v1 אינו רלוונטי ל-OFF ואינו \"אפס התרעות\".",
        f"מכנים: {n} מקרים מזווגים מתוכננים; בקשות כוללות ניסיונות חוזרים; עלות מחושבת מדיווח השימוש במחירון קפוא (0.20 / 1.20 דולר למיליון אסימונים). מקור: public-aggregate.json של הריצה.",
    ]
    for index, line in enumerate(footer):
        ax.text(99, 18.5 - index * 3.2, he(line), ha="right", va="top", fontproperties=small)
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / "study2-e2e-visual.he.png"
    pdf = out_dir / "study2-e2e-visual.he.pdf"
    fig.savefig(png, dpi=180)
    fig.savefig(pdf)
    plt.close(fig)
    return {"png": png, "pdf": pdf}
