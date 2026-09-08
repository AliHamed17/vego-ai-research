"""Create the short, evidence-bounded Hebrew Study 1 supervisor readout.

The script is intentionally self-contained: it uses only already published,
aggregate Study 1 values.  It neither reads private run artifacts nor invokes
a model, provider, or experiment.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "research" / "phd-proposal" / "2026-09-08-study1-e2e-supervisor-readout-he.pdf"

FONT_PATHS = (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/david.ttf"))
FONT_PATH = next((path for path in FONT_PATHS if path.exists()), None)
if FONT_PATH is None:
    raise RuntimeError("A Hebrew-capable Arial or David font is required to build the supervisor readout.")
pdfmetrics.registerFont(TTFont("Hebrew", str(FONT_PATH)))

W, H = A4
MARGIN = 17 * mm

NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#1864AB")
TEAL = colors.HexColor("#0B7285")
GREEN = colors.HexColor("#2B8A3E")
ORANGE = colors.HexColor("#D9480F")
RED = colors.HexColor("#C92A2A")
PURPLE = colors.HexColor("#7048E8")
INK = colors.HexColor("#243B53")
MUTED = colors.HexColor("#627D98")
PALE = colors.HexColor("#F7FAFC")
BLUE_PALE = colors.HexColor("#E7F5FF")
TEAL_PALE = colors.HexColor("#E3FAFC")
GREEN_PALE = colors.HexColor("#EBFBEE")
ORANGE_PALE = colors.HexColor("#FFF4E6")
PURPLE_PALE = colors.HexColor("#F3F0FF")
GRID = colors.HexColor("#D9E2EC")


def rtl(value: object) -> str:
    """Return visually ordered Hebrew for ReportLab's LTR drawing primitives."""
    return get_display(str(value))


def ltr_box(canvas_obj: canvas.Canvas, text: str, x: float, y: float, width: float, height: float,
            *, fill: colors.Color, text_color: colors.Color = colors.white, size: float = 7.3) -> None:
    canvas_obj.setFillColor(fill)
    canvas_obj.roundRect(x, y, width, height, 3.5, fill=1, stroke=0)
    canvas_obj.setFillColor(text_color)
    canvas_obj.setFont("Helvetica-Bold", size)
    canvas_obj.drawCentredString(x + width / 2, y + height / 2 - size * 0.33, text)


def draw_rtl(canvas_obj: canvas.Canvas, text: str, right: float, y: float, *, size: float = 10,
             color: colors.Color = INK, font: str = "Hebrew") -> None:
    canvas_obj.setFillColor(color)
    canvas_obj.setFont(font, size)
    canvas_obj.drawRightString(right, y, rtl(text))


def draw_ltr(canvas_obj: canvas.Canvas, text: str, left: float, y: float, *, size: float = 8,
             color: colors.Color = INK, font: str = "Helvetica") -> None:
    canvas_obj.setFillColor(color)
    canvas_obj.setFont(font, size)
    canvas_obj.drawString(left, y, text)


def split_rtl(canvas_obj: canvas.Canvas, text: str, max_width: float, size: float, font: str = "Hebrew") -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        if current and canvas_obj.stringWidth(rtl(candidate), font, size) > max_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def paragraph(canvas_obj: canvas.Canvas, text: str, right: float, y: float, width: float, *,
              size: float = 9, leading: float | None = None, color: colors.Color = INK,
              max_lines: int | None = None) -> float:
    leading = leading or size * 1.45
    lines = split_rtl(canvas_obj, text, width, size)
    if max_lines is not None:
        lines = lines[:max_lines]
    for index, line in enumerate(lines):
        draw_rtl(canvas_obj, line, right, y - index * leading, size=size, color=color)
    return y - len(lines) * leading


def header(canvas_obj: canvas.Canvas, page: int, title: str, subtitle: str) -> None:
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, H - 15 * mm, W, 15 * mm, fill=1, stroke=0)
    draw_rtl(canvas_obj, title, W - MARGIN, H - 10.2 * mm, size=13, color=colors.white)
    draw_rtl(canvas_obj, subtitle, W - MARGIN, H - 14.1 * mm, size=7.5, color=colors.HexColor("#D9EAF7"))
    canvas_obj.setStrokeColor(GRID)
    canvas_obj.line(MARGIN, 13 * mm, W - MARGIN, 13 * mm)
    draw_rtl(canvas_obj, f"מחקר 1 | AirTravel | עמוד {page} מתוך 6", W - MARGIN, 8.2 * mm, size=7.2, color=MUTED)


def rounded_card(canvas_obj: canvas.Canvas, x: float, y: float, width: float, height: float, *,
                 fill: colors.Color = colors.white, stroke: colors.Color = GRID,
                 radius: float = 10) -> None:
    canvas_obj.setFillColor(fill)
    canvas_obj.setStrokeColor(stroke)
    canvas_obj.setLineWidth(0.8)
    canvas_obj.roundRect(x, y, width, height, radius, fill=1, stroke=1)


def card(canvas_obj: canvas.Canvas, x: float, y: float, width: float, height: float, title: str,
         body: str, accent: colors.Color, *, token: str | None = None) -> None:
    rounded_card(canvas_obj, x, y, width, height, fill=colors.white)
    canvas_obj.setFillColor(accent)
    canvas_obj.roundRect(x + width - 8, y + 8, 5, height - 16, 2.5, fill=1, stroke=0)
    draw_rtl(canvas_obj, title, x + width - 16, y + height - 22, size=11.1, color=NAVY)
    paragraph(canvas_obj, body, x + width - 16, y + height - 42, width - 32, size=8.8, leading=12.1, max_lines=3)
    if token:
        ltr_box(canvas_obj, token, x + 16, y + 12, min(width - 40, 146), 15, fill=accent, size=6.6)


def bullet(canvas_obj: canvas.Canvas, right: float, y: float, text: str, *, color: colors.Color = BLUE,
           size: float = 9.2) -> float:
    canvas_obj.setFillColor(color)
    canvas_obj.circle(right - 3, y + 2.2, 2.2, fill=1, stroke=0)
    return paragraph(canvas_obj, text, right - 11, y, 470, size=size, leading=12, max_lines=2)


def archive_banner(canvas_obj: canvas.Canvas, x: float, y: float, width: float) -> None:
    ltr_box(canvas_obj, "ARCHIVAL / RETROSPECTIVE DESCRIPTIVE EVIDENCE", x, y, width, 16,
            fill=PURPLE, size=6.4)


def fixture_banner(canvas_obj: canvas.Canvas, x: float, y: float, width: float) -> None:
    ltr_box(canvas_obj, "ENGINEERING_FIXTURE_NOT_SCIENTIFIC", x, y, width, 15,
            fill=ORANGE, size=6.3)


def draw_arrow(canvas_obj: canvas.Canvas, x1: float, y1: float, x2: float, y2: float,
               *, color: colors.Color = BLUE) -> None:
    canvas_obj.setStrokeColor(color)
    canvas_obj.setFillColor(color)
    canvas_obj.setLineWidth(2)
    canvas_obj.line(x1, y1, x2, y2)
    direction = -1 if x2 < x1 else 1
    canvas_obj.setLineWidth(1)
    canvas_obj.line(x2, y2, x2 + 7 * direction, y2 + 4)
    canvas_obj.line(x2, y2, x2 + 7 * direction, y2 - 4)


def flow_box(canvas_obj: canvas.Canvas, x: float, y: float, width: float, title: str, token: str,
             color: colors.Color) -> None:
    rounded_card(canvas_obj, x, y, width, 86, fill=colors.white, stroke=color)
    canvas_obj.setFillColor(color)
    canvas_obj.circle(x + width / 2, y + 61, 13, fill=1, stroke=0)
    draw_ltr(canvas_obj, token, x + width / 2 - canvas_obj.stringWidth(token, "Helvetica-Bold", 6.5) / 2,
             y + 58.5, size=6.5, color=colors.white, font="Helvetica-Bold")
    draw_rtl(canvas_obj, title, x + width - 9, y + 28, size=9.2, color=NAVY)


def table_row(canvas_obj: canvas.Canvas, y: float, x: float, widths: Iterable[float], values: list[str], *,
              header_row: bool = False, ltr_columns: set[int] | None = None, height: float = 33) -> None:
    current = x
    ltr_columns = ltr_columns or set()
    for index, (width, value) in enumerate(zip(widths, values, strict=True)):
        canvas_obj.setFillColor(NAVY if header_row else colors.white)
        canvas_obj.setStrokeColor(GRID)
        canvas_obj.rect(current, y, width, height, fill=1, stroke=1)
        if index in ltr_columns:
            draw_ltr(canvas_obj, value, current + 5, y + height / 2 - 3, size=7.1 if not header_row else 7.3,
                     color=colors.white if header_row else INK, font="Helvetica-Bold" if header_row else "Helvetica")
        else:
            draw_rtl(canvas_obj, value, current + width - 5, y + height / 2 - 3,
                     size=7.6 if not header_row else 7.8, color=colors.white if header_row else INK,
                     font="Hebrew")
        current += width


def page_one(c: canvas.Canvas) -> None:
    header(c, 1, "מחקר 1: קריאה קצרה על תהליך ה־E2E", "חבילת מנחים בעברית | 8 בספטמבר 2026")
    draw_rtl(c, "AirTravel: תיעוד שיח בין סוכנים ותווית דיווח", W - MARGIN, H - 31 * mm, size=18, color=NAVY)
    draw_rtl(c, "החבילה מסבירה מה קרה בתהליך, ומה עדיין אי אפשר להסיק ממנו.", W - MARGIN,
             H - 39 * mm, size=10.5, color=MUTED)

    y = H - 87 * mm
    card(c, W - MARGIN - 164, y, 164, 108, "מה נבדק", "קורפוס AirTravel ציבורי חיצוני. נלכדה תקשורת שאלות ותשובות בין סוכני VEGO-AI.", BLUE,
         token="PUBLIC_EXTERNAL")
    card(c, W - MARGIN - 336, y, 164, 108, "המדגם", "ארבעה מקרים שנבחרו באופן מכוון. הבחירה אינה מייצגת ואינה ניתנת לשחזור אוטומטי.", TEAL,
         token="N = 4 | PURPOSIVE")
    card(c, W - MARGIN - 508, y, 164, 108, "גבול המדגם", "אין כאן נתוני סטודנטים, Cheers/ParkWise, מדגם מייצג או מילוי פער סינתטי.", ORANGE,
         token="NOT STUDENT DATA")

    boundary_y = H - 167 * mm
    rounded_card(c, MARGIN, boundary_y, W - 2 * MARGIN, 80, fill=BLUE_PALE, stroke=BLUE)
    draw_rtl(c, "מה אפשר לומר", W - MARGIN - 12, boundary_y + 56, size=12.3, color=NAVY)
    paragraph(c, "הבדיקה מראה שאפשר לתעד Q&A ולתת תווית דיווח לפי כלל קפוא. היא אינה בוחנת נכונות, איכות, תועלת או עדיפות של VEGO-AI.",
              W - MARGIN - 12, boundary_y + 37, W - 2 * MARGIN - 24, size=10.3, leading=14.5, max_lines=3)
    draw_rtl(c, "בדפים הבאים כל מספר מסומן לפי סוג הראיה והמכנה שלו.", W - MARGIN - 12, boundary_y + 10,
             size=8.5, color=BLUE)

    draw_rtl(c, "שלוש שכבות בדוח", W - MARGIN, 285, size=13, color=NAVY)
    for x, number, title, text, color in [
        (W - MARGIN - 158, "1", "ראיה ארכיונית", "תיאור בדיעבד של הריצה שכבר פורסמה", PURPLE),
        (W - MARGIN - 326, "2", "בדיקות הנדסיות", "בדיקת התנהגות המכשור ללא מודל", ORANGE),
        (W - MARGIN - 494, "3", "מידע פתוח", "פריטים שדורשים ראיה פרטית או בדיקה אנושית", RED),
    ]:
        layer_y = 155
        rounded_card(c, x, layer_y, 152, 60, fill=colors.white, stroke=color)
        c.setFillColor(color)
        c.circle(x + 18, layer_y + 39, 10, fill=1, stroke=0)
        draw_ltr(c, number, x + 15.5, layer_y + 36.5, size=7.5, color=colors.white, font="Helvetica-Bold")
        draw_rtl(c, title, x + 142, layer_y + 41, size=8.7, color=NAVY)
        paragraph(c, text, x + 142, layer_y + 24, 120, size=6.9, leading=8.4, color=MUTED, max_lines=2)


def page_two(c: canvas.Canvas) -> None:
    header(c, 2, "הזרימה מקצה לקצה", "אותו מסלול מוצג ללא שינוי או תיקון אוטומטי")
    draw_rtl(c, "הנתונים עוברים בסוכנים, מתועדים, ומקבלים תווית בדוח.", W - MARGIN, H - 31 * mm,
             size=12.5, color=NAVY)

    widths = 93
    y = H - 116 * mm
    boxes = [
        (W - MARGIN - widths, "נתוני AirTravel", "DATA", BLUE),
        (W - MARGIN - widths * 2 - 18, "סוכני VEGO-AI", "AGENTS", TEAL),
        (W - MARGIN - widths * 3 - 36, "יומן Q&A", "LOG", PURPLE),
        (W - MARGIN - widths * 4 - 54, "Detector-v1", "RULE", ORANGE),
        (W - MARGIN - widths * 5 - 72, "תווית בדוח", "LABEL", GREEN),
    ]
    shapes = []
    for x, title, token, color in boxes:
        flow_box(c, x, y, widths, title, token, color)
        shapes.append((x, y, widths))
    for index in range(len(shapes) - 1):
        x, _, _ = shapes[index]
        next_x, _, next_width = shapes[index + 1]
        draw_arrow(c, x - 4, y + 43, next_x + next_width + 4, y + 43, color=BLUE)

    detail_y = H - 169 * mm
    rounded_card(c, MARGIN, detail_y, W - 2 * MARGIN, 87, fill=TEAL_PALE, stroke=TEAL)
    draw_rtl(c, "מה נשמר בדרך", W - MARGIN - 12, detail_y + 65, size=12, color=NAVY)
    bullets = [
        "שאלה, תשובה, סוכן שואל, סוכן משיב, סבב וסיום אפיזודה.",
        "הכלל משתמש רק באותות Q&A שהוגדרו מראש.",
        "התוצאה נשארת תווית בדוח. אין שינוי אוטומטי במודל או במסמך.",
    ]
    current_y = detail_y + 46
    for text in bullets:
        current_y = bullet(c, W - MARGIN - 16, current_y, text, color=TEAL, size=9.2) - 3

    boundary_y = H - 224 * mm
    rounded_card(c, MARGIN, boundary_y, W - 2 * MARGIN, 35, fill=ORANGE_PALE, stroke=ORANGE)
    draw_rtl(c, "המסלול מתאר תהליך. הוא אינו משווה בין VEGO-AI למערכת אחרת.", W - MARGIN - 12, boundary_y + 14,
             size=10.2, color=ORANGE)


def page_three(c: canvas.Canvas) -> None:
    header(c, 3, "היומנים ותווית ההתראה", "מקור, שימוש וגבול לכל סוג תיעוד")
    draw_rtl(c, "איזה יומן משמש למה", W - MARGIN, H - 31 * mm, size=13, color=NAVY)

    x = MARGIN
    widths = [130, 245, W - 2 * MARGIN - 375]
    top = H - 56 * mm
    table_row(c, top, x, widths, ["שימוש בדוח", "מה הוא מתעד", "יומן"], header_row=True)
    rows = [
        (["מקור Q&A כאשר הוא מאומת", "שאלות, תשובות, סבבים וסיום אפיזודה", "qa_events.jsonl"], {2}),
        (["אפשרות לעקבת LLM בלבד", "עקבת LLM אפשרית. אינה ראיית Detector", "interaction_log.json"], {2}),
        (["ביקורת ממשק בלבד", "פעולות GUI. אינו מקור Q&A", "user_actions.log"], {2}),
        (["מנגנון שונות נפרד", "סיווג Agent-4. אינו קלט Detector", "Agent-4 output"], {2}),
    ]
    y = top - 33
    for values, ltr_columns in rows:
        table_row(c, y, x, widths, values, ltr_columns=ltr_columns)
        y -= 33

    alert_y = H - 222 * mm
    rounded_card(c, MARGIN, alert_y, W - 2 * MARGIN, 66, fill=GREEN_PALE, stroke=GREEN)
    draw_rtl(c, "מה פירוש התראה", W - MARGIN - 12, alert_y + 46, size=12.2, color=NAVY)
    draw_rtl(c, "התראה = מועמד לבדיקה אנושית בדוח.", W - MARGIN - 12, alert_y + 29, size=15, color=GREEN)
    draw_rtl(c, "היא אינה שגיאה, אינה תשובה שגויה, אינה תועלת מוכחת, ואינה תיקון אוטומטי.", W - MARGIN - 12,
             alert_y + 12, size=8.7, color=INK)

    draw_rtl(c, "כלל Detector-v1 הקפוא", W - MARGIN, H - 242 * mm, size=12.5, color=NAVY)
    ltr_box(c, "STRONG_ALERT = S1 OR S3 OR S7", MARGIN, H - 264 * mm, 240, 19, fill=RED, size=7.6)
    ltr_box(c, "WEAK_ALERT = no strong AND (S2 OR S6)", MARGIN + 252, H - 264 * mm, 240, 19, fill=ORANGE, size=6.7)
    ltr_box(c, "NO_ALERT = otherwise", MARGIN + 135, H - 290 * mm, 220, 19, fill=MUTED, size=7.5)
    draw_rtl(c, "S3 מציין רק ראיה ריקה או חסרה לפי הכלל הקפוא. הוא אינו בודק איכות ראיה.", W - MARGIN,
             H - 304 * mm, size=8.2, color=MUTED)


def page_four(c: canvas.Canvas) -> None:
    header(c, 4, "שני מנגנונים נפרדים", "Detector-v1 אינו מנגנון Agent-4")
    draw_rtl(c, "לא מערבבים בין תווית דיווח על Q&A לבין סיווג שונות.", W - MARGIN, H - 31 * mm, size=12.7, color=NAVY)

    card_width = (W - 2 * MARGIN - 20) / 2
    right_x = W - MARGIN - card_width
    left_x = MARGIN
    bottom = H - 190 * mm
    height = 255

    rounded_card(c, right_x, bottom, card_width, height, fill=BLUE_PALE, stroke=BLUE)
    draw_rtl(c, "Detector-v1", right_x + card_width - 14, bottom + height - 28, size=17, color=NAVY)
    ltr_box(c, "Q&A EPISODE", right_x + 15, bottom + height - 54, 100, 16, fill=BLUE, size=6.7)
    labels = [
        ("יחידת ניתוח", "אפיזודת Q&A"),
        ("פעולה", "תווית מועמד לבדיקה בדוח"),
        ("תור", "לא נוצר תור"),
        ("שינוי אוטומטי", "לא מבוצע"),
    ]
    y = bottom + height - 82
    for label, value in labels:
        draw_rtl(c, label, right_x + card_width - 14, y, size=8.3, color=MUTED)
        draw_rtl(c, value, right_x + card_width - 14, y - 13, size=10.0, color=INK)
        c.setStrokeColor(colors.HexColor("#B6D9F5"))
        c.line(right_x + 14, y - 21, right_x + card_width - 14, y - 21)
        y -= 47
    draw_rtl(c, "תווית הדיווח אינה קובעת מי צודק.", right_x + card_width - 14, bottom + 18, size=8.7, color=BLUE)

    rounded_card(c, left_x, bottom, card_width, height, fill=PURPLE_PALE, stroke=PURPLE)
    draw_rtl(c, "Agent-4", left_x + card_width - 14, bottom + height - 28, size=17, color=NAVY)
    ltr_box(c, "VARIABILITY CLASSIFICATION", left_x + 15, bottom + height - 54, 146, 16, fill=PURPLE, size=5.6)
    labels = [
        ("יחידת ניתוח", "סיווג שונות"),
        ("פעולה", "בונה תור נפרד רק אם המנגנון מצליח"),
        ("מצב AirTravel", "EXECUTED_THEN_BLOCKED"),
        ("מצב תור", "NOT_AVAILABLE"),
    ]
    y = bottom + height - 82
    for index, (label, value) in enumerate(labels):
        draw_rtl(c, label, left_x + card_width - 14, y, size=8.3, color=MUTED)
        if index >= 2:
            draw_ltr(c, value, left_x + 15, y - 13, size=8.4 if index == 2 else 10.0,
                     color=PURPLE, font="Helvetica-Bold")
        else:
            paragraph(c, value, left_x + card_width - 14, y - 13, card_width - 28, size=9.2, leading=11.2, max_lines=2)
        c.setStrokeColor(colors.HexColor("#D5C8FF"))
        c.line(left_x + 14, y - (29 if index == 1 else 21), left_x + card_width - 14, y - (29 if index == 1 else 21))
        y -= 55 if index == 1 else 47
    paragraph(c, "נבנתה רשומת ביקורת. הכתיבה נחסמה כי ערך הקורפוס אינו מתקבל בסכמת המורשת.",
              left_x + card_width - 14, bottom + 34, card_width - 28, size=7.3, leading=8.8, color=PURPLE, max_lines=2)


def bar(c: canvas.Canvas, x: float, y: float, width: float, height: float, label: str, value: int,
        maximum: int, color: colors.Color) -> None:
    c.setFillColor(colors.HexColor("#EDF2F7"))
    c.roundRect(x, y, width, height, 3, fill=1, stroke=0)
    c.setFillColor(color)
    c.roundRect(x, y, width * value / maximum, height, 3, fill=1, stroke=0)
    draw_rtl(c, label, x + width + 112, y + 2.2, size=7.9, color=INK)
    draw_ltr(c, str(value), x + 2, y + 2.2, size=7.3, color=colors.white if value > 0 else INK, font="Helvetica-Bold")


def page_five(c: canvas.Canvas) -> None:
    header(c, 5, "תמונה תיאורית של הריצה הארכיונית", "המספרים בעמוד זה אינם תוצאה פרוספקטיבית או הערכת ביצועים")
    archive_banner(c, MARGIN, H - 40 * mm, W - 2 * MARGIN)
    draw_rtl(c, "מקור: קבלה ודוח Study 1 שפורסמו. מכנה מדעי: 3 אפיזודות שלמות. ארבעת המקרים אינם מדגם מייצג.",
             W - MARGIN, H - 50 * mm, size=8.3, color=MUTED)

    metrics = [
        ("4", "מקרים שנבחרו", "מכנה: 4 מקרים", BLUE),
        ("3", "אפיזודות שלמות", "2 CONVERGED, 1 MAX", TEAL),
        ("44", "שאלות ותשובות", "44 שאלות + 44 תשובות", PURPLE),
        ("3/3", "STRONG_ALERT", "מכנה: 3 אפיזודות", RED),
    ]
    x = MARGIN
    y = H - 90 * mm
    width = (W - 2 * MARGIN - 24) / 4
    for value, label, source, color in metrics:
        rounded_card(c, x, y, width, 53, fill=colors.white, stroke=color)
        draw_ltr(c, value, x + 12, y + 25, size=18, color=color, font="Helvetica-Bold")
        draw_rtl(c, label, x + width - 10, y + 29, size=8.2, color=NAVY)
        draw_rtl(c, source, x + width - 10, y + 15, size=6.6, color=MUTED)
        x += width + 8

    archive_banner(c, MARGIN, H - 119 * mm, 258)
    draw_rtl(c, "מצב אפיזודות", MARGIN + 258, H - 129 * mm, size=9.8, color=NAVY)
    bar(c, MARGIN + 5, H - 143 * mm, 155, 12, "CONVERGED", 2, 3, TEAL)
    bar(c, MARGIN + 5, H - 160 * mm, 155, 12, "TERMINATED_MAX_ROUNDS", 1, 3, ORANGE)
    draw_rtl(c, "מכנה: 3 אפיזודות שלמות", MARGIN + 258, H - 169 * mm, size=6.9, color=MUTED)

    chart_x = MARGIN + 280
    archive_banner(c, chart_x, H - 119 * mm, 258)
    draw_rtl(c, "ביטחון תשובות מדווח עצמי", chart_x + 258, H - 129 * mm, size=9.4, color=NAVY)
    # Confidence is model self-report; show the denominator directly under its chart.
    for index, (label, value, color) in enumerate([("נמוך", 16, RED), ("בינוני", 25, ORANGE), ("גבוה", 3, GREEN)]):
        bx = chart_x + 18 + index * 74
        c.setFillColor(colors.HexColor("#EDF2F7"))
        c.roundRect(bx, H - 173 * mm, 39, 40, 4, fill=1, stroke=0)
        c.setFillColor(color)
        c.roundRect(bx, H - 173 * mm, 39, 40 * value / 25, 4, fill=1, stroke=0)
        draw_ltr(c, str(value), bx + 13, H - 178 * mm, size=8.2, color=NAVY, font="Helvetica-Bold")
        draw_rtl(c, label, bx + 34, H - 185 * mm, size=6.5, color=MUTED)
    draw_rtl(c, "מכנה: 44 תשובות. ביטחון אינו מדד נכונות.", chart_x + 258, H - 194 * mm, size=6.9, color=MUTED)

    archive_banner(c, MARGIN, H - 214 * mm, W - 2 * MARGIN)
    draw_rtl(c, "מסלולי Q&A שנצפו", W - MARGIN, H - 225 * mm, size=10.5, color=NAVY)
    widths = [132, 150, W - 2 * MARGIN - 282]
    y = H - 241 * mm
    table_row(c, y, MARGIN, widths, ["מספר שאלות", "סוכן משיב", "סוכן שואל"], header_row=True)
    table_row(c, y - 29, MARGIN, widths, ["39", "agent2", "agent4"], ltr_columns={0, 1, 2}, height=29)
    table_row(c, y - 58, MARGIN, widths, ["4", "agent2", "agent3"], ltr_columns={0, 1, 2}, height=29)
    table_row(c, y - 87, MARGIN, widths, ["1", "agent1", "agent3"], ltr_columns={0, 1, 2}, height=29)
    draw_rtl(c, "מקור ומכנה: 44 שאלות. נפח מסלול אינו מדד לתועלת או לנכונות.", W - MARGIN, H - 287 * mm,
             size=7.3, color=MUTED)


def engineering_card(c: canvas.Canvas, x: float, y: float, width: float, title: str, metric: str,
                     evidence: str, limitation: str, color: colors.Color, *, fixture: bool) -> None:
    rounded_card(c, x, y, width, 123, fill=colors.white, stroke=color)
    if fixture:
        fixture_banner(c, x + 12, y + 95, width - 24)
    else:
        ltr_box(c, "ENGINEERING_ONLY_NOT_SCIENTIFIC", x + 12, y + 95, width - 24, 15,
                fill=TEAL, size=6.3)
    draw_rtl(c, title, x + width - 12, y + 78, size=10.5, color=NAVY)
    draw_rtl(c, metric, x + width - 12, y + 59, size=15.0, color=color)
    draw_rtl(c, evidence, x + width - 12, y + 43, size=7.0, color=MUTED)
    paragraph(c, limitation, x + width - 12, y + 29, width - 24, size=7.3, leading=9.2, color=INK, max_lines=2)


def page_six(c: canvas.Canvas) -> None:
    header(c, 6, "בדיקות הנדסיות והשלבים הבאים", "בדיקות המכשור אינן מדע על איכות מודל או נכונות התראות")
    draw_rtl(c, "שלוש בדיקות נוספו כדי לבדוק את המכשור, ללא קריאת ספק או מודל.", W - MARGIN,
             H - 31 * mm, size=12.2, color=NAVY)

    width = W - 2 * MARGIN
    engineering_card(c, MARGIN, H - 93 * mm, width, "מעטפת Detector", "9/9 מצבי fixture תאמו לכלל",
                     "מקור ומכנה: 9 מצבי fixture.", "מוכיח שמסלולים ידועים מגיעים לפלטים. אינו מוכיח שההתראות נכונות או שכיחות.", ORANGE,
                     fixture=True)
    engineering_card(c, MARGIN, H - 141 * mm, width, "חוסן סדר אירועים", "500/500 ערבובים שמרו על הסיווג",
                     "מקור ומכנה: 500 ערבובים של היומן הארכיוני.", "מוכיח אי-תלות בסדר אירועים במכשור. אינו מודד ביצועי מודל.", TEAL,
                     fixture=False)
    engineering_card(c, MARGIN, H - 189 * mm, width, "כיול שמירת עלות", "43 בקשות | USD 0.134972",
                     "מקור ומכנה: קבלה ארכיונית אחת של הריצה שהתקבלה.", "מוכיח אריתמטיקת שמירת תקציב בלבד. אינו תחזית עלות או איכות עתידית.", PURPLE,
                     fixture=False)

    open_y = 75
    rounded_card(c, MARGIN, open_y, width, 170, fill=ORANGE_PALE, stroke=ORANGE)
    draw_rtl(c, "מה נשאר פתוח", W - MARGIN - 12, open_y + 145, size=12, color=NAVY)
    open_items = [
        "קישור מלא של הראיות הפרטיות לקבלה המאומתת.",
        "אמת־מידה ובוחנים אנושיים בלתי תלויים.",
        "תוצאת ON/OFF. אין כרגע תוצאת השוואה.",
        "טענה על דיוק, תועלת או הכללה. אין טענה כזאת בחבילה.",
    ]
    y = open_y + 120
    for item in open_items:
        y = bullet(c, W - MARGIN - 15, y, item, color=ORANGE, size=8.5) - 2


def build() -> Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
    c.setTitle("VEGO-AI Study 1 E2E Supervisor Readout - Hebrew")
    c.setAuthor("VEGO-AI")
    for page in (page_one, page_two, page_three, page_four, page_five, page_six):
        page(c)
        c.showPage()
    c.save()
    return OUT


if __name__ == "__main__":
    print(build())
