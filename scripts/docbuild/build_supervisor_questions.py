import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                KeepTogether, Spacer)

OUT = r"C:\Users\ahamed\Downloads\VEGO_AI_Literature_Review_Questions_for_Supervisors_20260826.pdf"

INK   = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#5b5b5b")
RULE  = colors.HexColor("#c8c8c8")
ACC   = colors.HexColor("#1f4e79")
EXBG  = colors.HexColor("#f2f5f8")

title = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=15, leading=19,
                       textColor=INK, spaceAfter=3)
sub = ParagraphStyle("sub", fontName="Helvetica", fontSize=9, leading=13,
                     textColor=MUTED, spaceAfter=10)
intro = ParagraphStyle("intro", fontName="Helvetica", fontSize=9, leading=13,
                       textColor=INK, spaceAfter=12)
qtext = ParagraphStyle("qtext", fontName="Helvetica-Bold", fontSize=9.7, leading=13.4,
                       textColor=ACC, spaceBefore=3, spaceAfter=3)
body = ParagraphStyle("body", fontName="Helvetica", fontSize=8.7, leading=12.2,
                      textColor=INK, spaceAfter=3)
ex = ParagraphStyle("ex", fontName="Helvetica", fontSize=8.4, leading=11.8,
                    textColor=INK, spaceAfter=3, leftIndent=7, rightIndent=5,
                    borderPadding=(4, 5, 4, 5), backColor=EXBG,
                    borderColor=EXBG, borderWidth=0)
dec = ParagraphStyle("dec", fontName="Helvetica-Oblique", fontSize=8.3, leading=11.6,
                     textColor=MUTED, spaceAfter=10)

# (question, context, example, decision)
QUESTIONS = [
 ("1. The taxonomy's four branches do not partition its corpus. Does it still work as an organizing frame?",
  "Branch membership turns out to carry almost no information about a paper, so classifying the branches may "
  "tell us less than screening the papers did.",
  "<b>Example.</b> Of the ninety papers, eighty-nine carry all four branch labels. Exactly one \u2014 an "
  "orchestration paper \u2014 is branch-specific.",
  "Whether Appendix A stays a classification of the taxonomy, or becomes purely a corpus screen."),

 ("2. What breadth of search should support a novelty claim \u2014 and is that a proposal-stage burden at all?",
  "A corpus-scoped screen cannot establish a negative, however carefully it is run. The nearest competing work "
  "was structurally invisible to the corpus I screened.",
  "<b>Example.</b> Multi-expert learning-to-defer routes among named experts by per-expert competence \u2014 the "
  "closest published work to SQ1. It appears in no human-agent systems survey, because it sits in the "
  "machine-learning theory literature.",
  "Whether the five registered query families must run before submission."),

 ("3. What screening reliability makes the counts citable?",
  "Screening was single-rater and title-level, but the inclusion criteria are content-level: they turn on a "
  "paper's contribution type, which titles often do not reveal.",
  "<b>Example.</b> From the title <i>Learning to Ask: When LLM Agents Meet Unclear Instruction</i>, is the "
  "contribution a method, a benchmark, or a dataset? The disposition depends entirely on that, and the title "
  "does not settle it.",
  "Whether to add a second screener, or re-screen the decisive twenty-seven at abstract level."),

 ("4. Should the literature sit in the introduction, with the systematic review as a study?",
  "The faculty proposal I was given has no literature-review chapter at all, and this draft now follows it.",
  "<b>Example.</b> In that proposal the literature is background in \u00a71.1\u2013\u00a71.2, the systematic review "
  "is a research activity in \u00a73.1, its progress is reported in \u00a74.1, and its deliverable is a taxonomy.",
  "Whether that is the expected departmental form, or one supervisor's preference."),

 ("5. Is a single, sharply falsifiable deficit strong enough to carry a doctorate?",
  "Stated as a conjunction of everything the work needs, the gap was close to unfalsifiable. It now rests on one "
  "claim \u2014 bought testability at the cost of scope.",
  "<b>Example.</b> The claim is that no reviewed formulation selects a reviewer by assessed competence "
  "<i>and authority</i> over the contested fragment. One study that did would refute the whole novelty claim.",
  "Whether to hold the narrow claim or re-broaden, before the questions are frozen."),

 ("6. Is <i>authority to decide a claim</i> researchable, or an organisational notion that will resist measurement?",
  "Competence is already modelled statistically as expected per-expert accuracy. Authority is not, and it is now "
  "the only thing separating this work from its nearest predecessor.",
  "<b>Example.</b> A modelling-language specialist may read the notation correctly yet hold no mandate to change "
  "an institutional rule; the instructor who owns the rubric may hold the mandate and misread the notation.",
  "Whether the authority fields in the governed-judgment contract are measurable, before Study 2 is designed."),

 ("7. Should SQ2's wording change, or is separation by ownership enough?",
  "The overlap is currently resolved by a declared ownership boundary rather than by the wording itself.",
  "<b>Example.</b> SQ2 asks how judgment is stored <i>\u201cso that it can be reused\u201d</i>; SQ3 asks how judgment "
  "<i>\u201cis reused across contexts\u201d</i>. Read without the ownership statement, both appear to claim reuse.",
  "Whether the question set can be frozen as written."),

 ("8. What would count as evidence that the review may stop?",
  "The protocol is frozen and its queries registered, but no stopping rule is defined.",
  "<b>Example.</b> Saturation, exhausting the four primary databases, or your judgement are all defensible \u2014 "
  "and imply roughly two semesters of work, one, or none.",
  "The literature milestone in the first year of the anchored plan."),
]


def deco(canv, doc):
    canv.saveState()
    canv.setStrokeColor(RULE); canv.setLineWidth(0.5)
    canv.line(20*mm, 16*mm, A4[0]-20*mm, 16*mm)
    canv.setFont("Helvetica", 7.2); canv.setFillColor(MUTED)
    canv.drawString(20*mm, 11.5*mm, "VEGO-AI \u2014 literature-review questions for supervisor discussion \u2014 26 August 2026")
    canv.drawRightString(A4[0]-20*mm, 11.5*mm, "Page %d" % doc.page)
    canv.restoreState()


def build():
    doc = BaseDocTemplate(OUT, pagesize=A4,
                          leftMargin=20*mm, rightMargin=20*mm,
                          topMargin=18*mm, bottomMargin=22*mm,
                          title="VEGO-AI - Literature Review Questions for Supervisors",
                          author="Ali Hamed")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=deco)])

    story = [
        Paragraph("Literature review \u2014 open questions for supervisor discussion", title),
        Paragraph("Ali Hamed &nbsp;\u00b7&nbsp; for Prof. Iris Reinhartz-Berger and Prof. Arnon Sturm "
                  "&nbsp;\u00b7&nbsp; 26 August 2026", sub),
        Paragraph("Eight decisions the review has reached that I cannot settle alone. Each comes from work already "
                  "done, so each gives the finding, one example, and what the answer changes. I am not asking whether "
                  "the work is acceptable \u2014 I am asking which of several defensible standards you want applied.",
                  intro),
    ]

    for q, ctx, example, decision in QUESTIONS:
        story.append(KeepTogether([
            Paragraph(q, qtext),
            Paragraph(ctx, body),
            Paragraph(example, ex),
            Spacer(1, 2),
            Paragraph("\u2192 " + decision, dec),
        ]))

    doc.build(story)
    print("WROTE:", OUT, os.path.getsize(OUT), "bytes")


build()
