"""Build the supervisor-facing Hebrew Q&A escalation task plan."""
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from qa_task_plan_data import PLAN, SUMMARY_HEADERS, SUMMARY_TABLE, TASKS


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "docx" / "VEGO-AI-qa-escalation-operational-task-plan-he.docx"

NAVY = "17365D"
BLUE = "2E74B5"
MUTED = "5B6573"
LIGHT = "EEF3F8"
PALE = "F7F9FB"
RED = "8B1E2D"


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_width(cell, dxa):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(dxa))
    tc_w.set(qn("w:type"), "dxa")


def set_cell_margins(cell, top=55, start=85, bottom=55, end=85):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    margins = tc_pr.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        tc_pr.append(margins)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = margins.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            margins.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_geometry(table, widths=(1800, 7560)):
    table.alignment = WD_TABLE_ALIGNMENT.RIGHT
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(widths)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_layout = tbl_pr.find(qn("w:tblLayout"))
    if tbl_layout is None:
        tbl_layout = OxmlElement("w:tblLayout")
        tbl_pr.append(tbl_layout)
    tbl_layout.set(qn("w:type"), "fixed")
    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), "120")
    tbl_ind.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            set_cell_width(cell, widths[i])
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP


def set_bidi(paragraph, align=WD_ALIGN_PARAGRAPH.RIGHT):
    paragraph.alignment = align
    p_pr = paragraph._p.get_or_add_pPr()
    bidi = p_pr.find(qn("w:bidi"))
    if bidi is None:
        bidi = OxmlElement("w:bidi")
        p_pr.append(bidi)
    bidi.set(qn("w:val"), "1")


def set_run(run, size=8.4, bold=False, color="1F2937", font="Arial"):
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:ascii"), font)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), font)
    run._element.rPr.rFonts.set(qn("w:cs"), font)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)


def add_para(doc, text="", size=8.7, bold=False, color="1F2937", before=0, after=2.5, align=WD_ALIGN_PARAGRAPH.RIGHT, style=None):
    p = doc.add_paragraph(style=style)
    set_bidi(p, align)
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.02
    r = p.add_run(text)
    set_run(r, size=size, bold=bold, color=color)
    return p


def add_task(doc, number, name, priority, fields):
    p = doc.add_paragraph()
    set_bidi(p)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(f"משימה {number} — {name}  [{priority}]")
    set_run(r, size=10.2, bold=True, color=NAVY)
    table = doc.add_table(rows=0, cols=2)
    labels = [
        "מטרה", "מה אני אבצע", "המקור לזיהוי האוטומטי", "ה-Dataset", "הפלט",
        "קריטריון השלמה", "מה נדרש ממני", "מה נדרש מאיריס וארנון", "מה חסר / מאתגר", "תלויות", "הערכת זמן",
    ]
    for label in labels:
        row = table.add_row()
        left, right = row.cells
        set_cell_width(left, 1800)
        set_cell_width(right, 7560)
        shade(left, LIGHT)
        shade(right, "FFFFFF")
        for cell in (left, right):
            set_cell_margins(cell)
        lp = left.paragraphs[0]
        set_bidi(lp)
        lp.paragraph_format.space_after = Pt(0)
        lr = lp.add_run(label)
        set_run(lr, size=7.6, bold=True, color=NAVY)
        rp = right.paragraphs[0]
        set_bidi(rp)
        rp.paragraph_format.space_after = Pt(0)
        rp.paragraph_format.line_spacing = 1.0
        rr = rp.add_run(fields[label])
        set_run(rr, size=7.55, color="263238")
    set_table_geometry(table)
    # restrained borders
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "3")
        node.set(qn("w:color"), "D9E2EC")


def add_summary_table(doc):
    headers = SUMMARY_HEADERS
    rows = SUMMARY_TABLE
    table = doc.add_table(rows=1, cols=len(headers))
    widths = (360, 1500, 520, 1380, 1250, 1500, 1800, 1050)
    set_table_geometry(table, widths)
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        shade(cell, NAVY)
        p = cell.paragraphs[0]
        set_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(header)
        set_run(r, size=6.7, bold=True, color="FFFFFF")
    for row_values in rows:
        row = table.add_row()
        for i, value in enumerate(row_values):
            cell = row.cells[i]
            shade(cell, "F7F9FB" if len(table.rows) % 2 == 0 else "FFFFFF")
            p = cell.paragraphs[0]
            set_bidi(p, WD_ALIGN_PARAGRAPH.CENTER if i in (0, 2, 7) else WD_ALIGN_PARAGRAPH.RIGHT)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(value)
            set_run(r, size=6.45, bold=False, color="263238")
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "3")
        node.set(qn("w:color"), "D9E2EC")
    return table


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(1.05)
    sec.bottom_margin = Cm(0.9)
    sec.left_margin = Cm(1.0)
    sec.right_margin = Cm(1.0)
    sec.header_distance = Cm(0.45)
    sec.footer_distance = Cm(0.45)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:cs"), "Arial")
    normal.font.size = Pt(8.7)
    normal.paragraph_format.space_after = Pt(2.5)
    normal.paragraph_format.line_spacing = 1.02

    header = sec.header.paragraphs[0]
    set_bidi(header, WD_ALIGN_PARAGRAPH.RIGHT)
    header.paragraph_format.space_after = Pt(0)
    hr = header.add_run(PLAN["metadata"]["header"])
    set_run(hr, size=7.2, bold=True, color=MUTED)
    footer = sec.footer.paragraphs[0]
    set_bidi(footer, WD_ALIGN_PARAGRAPH.CENTER)
    fr = footer.add_run(PLAN["metadata"]["footer"])
    set_run(fr, size=7.1, color=MUTED)

    add_para(doc, PLAN["metadata"]["title"].split(" — ", 1)[0], size=18, bold=True, color=NAVY, after=1.5)
    add_para(doc, PLAN["metadata"]["title"].split(" — ", 1)[1], size=11.5, bold=True, color=BLUE, after=3)
    add_para(doc, f"{PLAN['metadata']['recipient']}  |  סטטוס: {PLAN['metadata']['status']}", size=8.2, color=MUTED, after=5)
    p = add_para(doc, PLAN["opening"], size=9.1, bold=True, color=NAVY, after=4)
    shade_box = p._p.get_or_add_pPr()
    p_bdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")
    bottom.set(qn("w:space"), "3")
    bottom.set(qn("w:color"), BLUE)
    p_bdr.append(bottom)
    shade_box.append(p_bdr)
    add_para(doc, "מצב Q&A מאומת: " + PLAN["evidence_boundary"], size=8.0, color="263238", after=3)
    add_para(doc, PLAN["limitation"], size=8.0, color=RED, bold=True, after=3)
    add_para(doc, "רמות עדיפות: " + PLAN["metadata"]["priority_legend"], size=7.8, color=MUTED, after=3)
    add_summary_table(doc)
    add_para(doc, "פירוט המשימות", size=9.2, bold=True, color=NAVY, before=4, after=1)
    for i, (name, priority, fields) in enumerate(TASKS, 1):
        add_task(doc, i, name, priority, fields)
    add_para(doc, f"סה\"כ עבודת Ali נטו: {PLAN['effort']['ali']} זמן ריצה/API: {PLAN['effort']['machine_api']} זמן חסום/המתנה: {PLAN['effort']['blocked']}", size=8.2, bold=True, color=NAVY, before=5, after=2)
    add_para(doc, "מה נדרש מאיריס וארנון: " + " ".join(PLAN["supervisor_requests"]) + " " + PLAN["supervisor_closing"], size=8.3, bold=True, color=RED, after=0)
    doc.core_properties.title = PLAN["metadata"]["title"]
    doc.core_properties.subject = "Supervisor-facing operational task list"
    doc.core_properties.author = "VEGO-AI Research"
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
