import io, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, KeepTogether)

OUT = r"C:\Users\ahamed\Downloads\VEGO_AI_Literature_Review_Questions_for_Supervisors_20260826.pdf"

INK   = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#5b5b5b")
RULE  = colors.HexColor("#c8c8c8")
ACC   = colors.HexColor("#1f4e79")

title = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=15, leading=19,
                       textColor=INK, spaceAfter=3)
sub = ParagraphStyle("sub", fontName="Helvetica", fontSize=9, leading=13,
                     textColor=MUTED, spaceAfter=11)
intro = ParagraphStyle("intro", fontName="Helvetica", fontSize=9.3, leading=13.6,
                       textColor=INK, spaceAfter=12)
qnum = ParagraphStyle("qnum", fontName="Helvetica-Bold", fontSize=9.6, leading=13.4,
                      textColor=ACC, spaceBefore=2, spaceAfter=3)
qtext = ParagraphStyle("qtext", fontName="Helvetica-Bold", fontSize=9.6, leading=13.6,
                       textColor=INK, spaceAfter=4)
body = ParagraphStyle("body", fontName="Helvetica", fontSize=8.8, leading=12.6,
                      textColor=INK, spaceAfter=3, leftIndent=0)
hinge = ParagraphStyle("hinge", fontName="Helvetica-Oblique", fontSize=8.5, leading=12,
                       textColor=MUTED, spaceAfter=11)

QUESTIONS = [
 ("The taxonomy's four branches do not partition its corpus. Does it still work as an organizing frame?",
  "Screening the survey's ninety papers showed that eighty-nine appear under all four branches; only one is "
  "branch-specific. The branches are four cross-classifications of a single paper set, not a partition, so "
  "branch membership carries almost no information about an individual paper. A related judgement was made "
  "in the same appendix: because no paper can be classified as <i>missing</i>, that disposition was applied "
  "one level up, to research questions, marking a concern no paper in the corpus addresses.",
  "Whether Appendix A remains a structural classification of the taxonomy or becomes purely a corpus screen "
  "— and whether the intended reading of <i>missing</i> matches the one adopted."),

 ("What breadth of search should support a novelty claim at proposal stage — and is that a proposal-stage burden at all?",
  "The strongest competing formulation to this work's central deficit is multi-expert learning-to-defer, which "
  "selects among differentiated experts using per-expert competence estimates. It could not have surfaced in "
  "the screened corpus, because machine-learning-theory deferral papers do not appear in a human-agent systems "
  "survey. The episode shows that a corpus-scoped screen cannot establish a negative, however carefully it is "
  "conducted.",
  "Whether the five registered query families must be executed before submission, or whether a bounded critical "
  "synthesis is the appropriate proposal-stage standard."),

 ("What screening reliability does a doctoral literature review require before its counts may be cited?",
  "The corpus screening was single-rater and performed at title level, while its inclusion criteria are "
  "content-level: they turn on a paper's contribution type and its primary object, which a title often does not "
  "reveal. The dispositions are disclosed as provisional, but the standard that would make them citable has not "
  "been set.",
  "Whether to recruit a second screener now, or to re-screen the decisive subset at abstract level, before these "
  "figures appear in any submitted text."),

 ("Should the literature live in the introduction, with the systematic review as a study — or as a chapter of its own?",
  "A submitted proposal from this faculty carries no standalone literature-review chapter: the literature sits in "
  "the introduction as background that funnels to a gap, the systematic review appears in the methodology as one "
  "of the research activities, and its progress is reported with the other results. This proposal now follows that "
  "shape, and its review is planned to produce an evaluated taxonomy as an artifact.",
  "Whether that structure is the expected departmental form or one supervisor's preference — and whether producing "
  "a taxonomy is a genuine contribution or an over-formalisation of background work."),

 ("Is a single, sharply falsifiable deficit strong enough to carry a doctorate?",
  "The gap was deliberately narrowed. Stated as a conjunction of everything the work requires, it was close to "
  "unfalsifiable; it now rests on one testable claim, that no reviewed formulation makes the selection of a "
  "reviewer a function of assessed competence and authority over the specific contested fragment, with a stated "
  "refutation condition. The narrowing bought testability at the cost of scope.",
  "Whether to hold the narrow claim, or re-broaden and accept weaker falsifiability, before the research questions "
  "are frozen."),

 ("Is <i>authority to decide a claim</i> a researchable construct, or an organisational notion that will resist measurement?",
  "Competence is already modelled in the deferral literature, as estimated per-expert accuracy over a task "
  "distribution. Authority is not, and it is what now distinguishes this work from its nearest predecessor. But "
  "authority is institutional rather than statistical: who may settle a question is a matter of role and mandate, "
  "not of expected accuracy.",
  "Whether the authority and competence fields in the governed-judgment contract are viable as measured constructs, "
  "or need reframing before Study 2 is designed."),

 ("Should SQ2's wording change, or is separation by ownership sufficient?",
  "SQ2 asks how judgment should be represented, validated and stored <i>so that it can be reused</i>, while SQ3 owns "
  "reuse. The overlap is currently resolved by declared ownership rather than by wording: SQ2 owns the source "
  "record, SQ3 owns target-context fit. A reader who reads the questions alone, without the ownership statement, "
  "may still see two questions claiming the same ground.",
  "Whether the question set can be frozen as written, or SQ2 is re-worded first."),

 ("What would you accept as evidence that the literature review is complete enough to stop?",
  "The protocol is frozen and its canonical queries are registered, but no stopping rule is defined. Saturation, "
  "database coverage, an inclusion count, and supervisor judgement are all defensible criteria, and they imply "
  "very different amounts of remaining work.",
  "The literature milestone in the first two semesters of the anchored plan, and when the review can be declared "
  "closed rather than ongoing."),
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

    story = []
    story.append(Paragraph("Literature review \u2014 open questions for supervisor discussion", title))
    story.append(Paragraph(
        "Ali Hamed &nbsp;\u00b7&nbsp; for Prof. Iris Reinhartz-Berger and Prof. Arnon Sturm &nbsp;\u00b7&nbsp; 26 August 2026", sub))
    story.append(Paragraph(
        "Eight questions where the literature review has reached a decision I cannot settle on my own. Each arose "
        "from work already done rather than from unfamiliarity with it, so each states the finding that prompted it "
        "and what the answer would change. They are ordered from the review's method to its claims. I am not asking "
        "whether the work is acceptable; I am asking which of several defensible standards you want applied.", intro))

    for i, (q, ctx, h) in enumerate(QUESTIONS, 1):
        block = [
            Paragraph("Question %d" % i, qnum),
            Paragraph(q, qtext),
            Paragraph("<b>Why I am asking.</b> " + ctx, body),
            Paragraph("<b>What the answer changes.</b> " + h, hinge),
        ]
        story.append(KeepTogether(block))

    doc.build(story)
    print("WROTE:", OUT, os.path.getsize(OUT), "bytes")


build()
