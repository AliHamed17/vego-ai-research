"""Build a compact, RTL Hebrew PDF companion for the Q&A task plan."""
from pathlib import Path
import html

from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

from build_qa_escalation_task_plan import TASKS


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "VEGO-AI-qa-escalation-operational-task-plan-he.pdf"

FONT_PATH = Path("C:/Windows/Fonts/arial.ttf")
if not FONT_PATH.exists():
    FONT_PATH = Path("C:/Windows/Fonts/david.ttf")
pdfmetrics.registerFont(TTFont("Hebrew", str(FONT_PATH)))

NAVY = colors.HexColor("#17365D")
BLUE = colors.HexColor("#2E74B5")
MUTED = colors.HexColor("#5B6573")
LIGHT = colors.HexColor("#EEF3F8")
RED = colors.HexColor("#8B1E2D")


def rtl(text):
    return get_display(str(text))


def para(text, style):
    return Paragraph(html.escape(rtl(text)).replace("\n", "<br/>") , style)


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Hebrew", 7)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(A4[0] - 15 * mm, A4[1] - 10 * mm, rtl("VEGO-AI | תכנית עבודה אופרטיבית | 03.09.2026"))
    canvas.drawCentredString(A4[0] / 2, 8 * mm, rtl(f"מסמך עבודה לבחינה אנושית — עמוד {doc.page}"))
    canvas.restoreState()


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(OUT), pagesize=A4, leftMargin=10 * mm, rightMargin=10 * mm, topMargin=15 * mm, bottomMargin=12 * mm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=header_footer)])
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Normal"], fontName="Hebrew", fontSize=17, leading=19, textColor=NAVY, alignment=TA_RIGHT, spaceAfter=2)
    subtitle = ParagraphStyle("subtitle", parent=styles["Normal"], fontName="Hebrew", fontSize=10.5, leading=12.5, textColor=BLUE, alignment=TA_RIGHT, spaceAfter=3)
    meta = ParagraphStyle("meta", parent=styles["Normal"], fontName="Hebrew", fontSize=7.6, leading=9, textColor=MUTED, alignment=TA_RIGHT, spaceAfter=4)
    intro = ParagraphStyle("intro", parent=styles["Normal"], fontName="Hebrew", fontSize=8.1, leading=9.8, textColor=NAVY, alignment=TA_RIGHT, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["Normal"], fontName="Hebrew", fontSize=7.15, leading=8.45, textColor=colors.HexColor("#263238"), alignment=TA_RIGHT, spaceAfter=0)
    label = ParagraphStyle("label", parent=body, fontSize=7.0, leading=8.2, textColor=NAVY)
    task_head = ParagraphStyle("task_head", parent=styles["Normal"], fontName="Hebrew", fontSize=9.3, leading=10.8, textColor=NAVY, alignment=TA_RIGHT, spaceBefore=3, spaceAfter=2)
    foot = ParagraphStyle("foot", parent=intro, fontSize=7.8, leading=9.4, textColor=RED, spaceBefore=4)
    story = []
    story.append(para("תכנית עבודה אופרטיבית", title))
    story.append(para("זיהוי אוטומטי של צורך בהתערבות אנושית מתוך תקשורת Q&A ב-VEGO-AI", subtitle))
    story.append(para("לפרופ' Iris Reinhartz-Berger ולפרופ' Arnon Sturm | סטטוס: תכנית לביצוע ללא תיוג או בדיקה ידנית בשלב הנוכחי", meta))
    story.append(para("בהתאם להנחיה שלא יבוצעו תיוגים או בדיקות ידניות, התכנית מתמקדת בשלב זה באיסוף מלא של תקשורת ה-Q&A, בזיהוי אוטומטי של התראות ובניתוח תיאורי. בדיקת נכונות/שגיאות ההתראות תידחה לשלב שבו יהיה מקור תיוג עצמאי.", intro))
    story.append(para("בסיס ראיות: main = 0bf14f17784827042e92b0d3745bbfa09c800fef. ה-snapshot הקפוא מכיל 12 שאלות Agent 2 → Agent 1, ללא תשובה תואמת שנשמרה, ללא answer confidence/evidence וללא מידע בר-שחזור על follow-up, rounds או convergence. המונח המחייב הוא ANSWER_NOT_PERSISTED; אין להסיק שהתרחשה אי-מענה בזמן הריצה.", intro))
    story.append(para("כללי טענה: ניתן להפיק alerts אוטומטיים, ספירות, התפלגויות, reproducibility וניתוח תיאורי. לא ניתן לקבוע true/false alerts, accuracy, precision, recall או נחיצות אובייקטיבית של התערבות אנושית ללא labels עצמאיים.", foot))
    labels = ["מטרה", "מה אני אבצע", "המקור לזיהוי האוטומטי", "ה-Dataset", "הפלט", "קריטריון השלמה", "מה נדרש ממני", "מה נדרש מאיריס וארנון", "מה חסר / מאתגר", "תלויות", "הערכת זמן"]
    for idx, (name, priority, fields) in enumerate(TASKS, 1):
        story.append(Paragraph(html.escape(rtl(f"משימה {idx} — {name} [{priority}]")), task_head))
        data = []
        for key in labels:
            data.append([para(fields[key], body), para(key, label)])
        table = Table(data, colWidths=[doc.width - 34 * mm, 34 * mm], repeatRows=0, hAlign="RIGHT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (1, 0), (1, -1), LIGHT),
            ("BACKGROUND", (0, 0), (0, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9E2EC")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(KeepTogether(table))
    story.append(Spacer(1, 2))
    story.append(para("סה\"כ עבודת Ali נטו: כ-15–24 שעות לכל שמונה המשימות. מכונה/API: כ-2–6 שעות להרצות ובדיקות; עלות API תימדד לאחר בדיקת inputs. חסמים: קלטים, הרשאות runtime ועלות אפשרית. אין חסם של תיוג אנושי בשלב זה.", intro))
    story.append(para("החלטה יחידה המבוקשת מאיריס וארנון: האם תוצאה תיאורית של feasibility מקובלת לאבן-הדרך, כאשר true/false validation נדחה? אין בקשה לתייג או לבדוק אירועים.", foot))
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build()
