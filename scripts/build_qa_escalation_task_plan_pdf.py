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

from qa_task_plan_data import PLAN, SUMMARY_HEADERS, SUMMARY_TABLE, TASKS


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
    canvas.drawRightString(A4[0] - 15 * mm, A4[1] - 10 * mm, rtl(PLAN["metadata"]["header"]))
    canvas.drawCentredString(A4[0] / 2, 8 * mm, rtl(f"מסמך עבודה לבחינה אנושית — עמוד {doc.page}"))
    canvas.restoreState()


def summary_table(styles):
    headers = SUMMARY_HEADERS
    rows = SUMMARY_TABLE
    data = [[para(h, styles["table_header"]) for h in headers]]
    data.extend([[para(v, styles["table_cell"]) for v in row] for row in rows])
    table = Table(data, colWidths=[8 * mm, 33 * mm, 13 * mm, 29 * mm, 27 * mm, 28 * mm, 38 * mm, 19 * mm], hAlign="RIGHT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9E2EC")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return table


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
    table_header = ParagraphStyle("table_header", parent=body, fontSize=5.65, leading=6.3, textColor=colors.white, alignment=TA_CENTER)
    table_cell = ParagraphStyle("table_cell", parent=body, fontSize=5.45, leading=6.15, alignment=TA_RIGHT)
    table_styles = {"table_header": table_header, "table_cell": table_cell}
    story = []
    title_text, subtitle_text = PLAN["metadata"]["title"].split(" — ", 1)
    story.append(para(title_text, title))
    story.append(para(subtitle_text, subtitle))
    story.append(para(f"{PLAN['metadata']['recipient']} | סטטוס: {PLAN['metadata']['status']}", meta))
    story.append(para(PLAN["opening"], intro))
    story.append(para("מצב Q&A מאומת: " + PLAN["evidence_boundary"], intro))
    story.append(para(PLAN["limitation"], foot))
    story.append(summary_table(table_styles))
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
    story.append(para(f"סה\"כ עבודת Ali נטו: {PLAN['effort']['ali']} זמן ריצה/API: {PLAN['effort']['machine_api']} זמן חסום/המתנה: {PLAN['effort']['blocked']}", intro))
    story.append(para("מה נדרש מאיריס וארנון: " + " ".join(PLAN["supervisor_requests"]) + " " + PLAN["supervisor_closing"], foot))
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build()
