"""Build the IS Research Seminar (214.4001) final presentation.

Course: "The Research Approach in Information Systems", Prof. Penina Soffer.
Assignment (CL7 slide 11): a 10-12 minute class presentation covering motivation,
the research question, the derived set of questions, the literature search
strategy, and initial findings (research streams, classification/analysis
framework, identified gaps).

Content sources - every one of them a real artifact in this repository:
  * literature/verified-research-corpus-2026-08-12.json  (144 verified sources)
  * reports/generated/exp006|exp007|exp008/summary.json  (measured mechanism runs)
  * docs/research/governance/vego-ai-foundation-paper-record.md (published figures)
  * docs/research/phd-proposal/three-study-contract.md   (RQ / SQ wording)
  * artifacts/meetings/2026-08-12-iris-arnon/            (supervisor directives)
  * outputs/course-presentation/findings.json            (analysis workflow output)

Evidence boundary held throughout: EXP-005 stands at 0/24 validated
generalization-safe expert labels, and the frozen searches QL-01..QL-05 have not
been executed. Therefore the deck makes no accuracy, effort-reduction,
generalization or clinical claim, and never asserts proven absence in the
literature - only what the reviewed corpus does and does not cover.
"""
from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

REPO = Path(r"C:\Users\ahamed\vego-ai")
OUT_DIR = REPO / "outputs" / "course-presentation"
FIG = OUT_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DECK = OUT_DIR / "VEGO-AI - IS Research Seminar - Final Presentation.pptx"

# ---------------------------------------------------------------- design system
NAVY = RGBColor(0x0F, 0x27, 0x40)
NAVY_SOFT = RGBColor(0x1B, 0x3A, 0x5A)
ACCENT = RGBColor(0x2A, 0x78, 0xD6)
ACCENT_L = RGBColor(0xCD, 0xE2, 0xFB)
ORANGE = RGBColor(0xEB, 0x68, 0x34)
CRIT = RGBColor(0xD0, 0x3B, 0x3B)
GOOD = RGBColor(0x0C, 0xA3, 0x0C)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SOFT = RGBColor(0xF2, 0xF5, 0xF9)
SOFT2 = RGBColor(0xE8, 0xEE, 0xF6)
INK = RGBColor(0x0B, 0x0B, 0x0B)
MUTED = RGBColor(0x5A, 0x64, 0x72)
LINE = RGBColor(0xD5, 0xDD, 0xE7)

H_FONT = "Cambria"     # safe-list serif for headings
B_FONT = "Calibri"     # safe-list sans for body

W, H = Inches(13.333), Inches(7.5)
M = Inches(0.62)                     # page margin
CONTENT_W = W - 2 * M


def new_deck() -> Presentation:
    p = Presentation()
    p.slide_width, p.slide_height = W, H
    return p


def slide(prs, dark=False):
    s = prs.slides.add_slide(prs.slide_layouts[6])   # blank
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = NAVY if dark else WHITE
    return s


def tb(slide, x, y, w, h, *, anchor=MSO_ANCHOR.TOP, wrap=True):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return box, tf


def para(tf, text, *, size=16, bold=False, color=INK, font=B_FONT, align=PP_ALIGN.LEFT,
         space_after=0, space_before=0, italic=False, line=None, first=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.space_before = Pt(space_before)
    if line:
        p.line_spacing = line
    r = p.add_run()
    r.text = text
    f = r.font
    f.size, f.bold, f.italic, f.name = Pt(size), bold, italic, font
    f.color.rgb = color
    return p


def rich(tf, chunks, *, size=16, align=PP_ALIGN.LEFT, space_after=0, space_before=0,
         line=None, first=False):
    """A paragraph made of differently-styled runs: [(text, {bold,color,...}), ...]"""
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.space_before = Pt(space_before)
    if line:
        p.line_spacing = line
    for text, st in chunks:
        r = p.add_run()
        r.text = text
        f = r.font
        f.size = Pt(st.get("size", size))
        f.bold = st.get("bold", False)
        f.italic = st.get("italic", False)
        f.name = st.get("font", B_FONT)
        f.color.rgb = st.get("color", INK)
    return p


def card(slide, x, y, w, h, *, fill=SOFT, line_col=None, radius=0.04, shadow=False):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    sh.adjustments[0] = radius
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line_col:
        sh.line.color.rgb = line_col
        sh.line.width = Pt(1.0)
    else:
        sh.line.fill.background()
    sh.shadow.inherit = shadow
    sh.text_frame.word_wrap = True
    return sh


def badge(slide, x, y, d, text, *, fill=ACCENT, color=WHITE, size=15):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, d, d)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    sh.shadow.inherit = False
    tf = sh.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    r.font.size, r.font.bold, r.font.name = Pt(size), True, B_FONT
    r.font.color.rgb = color
    return sh


# Rough advance width of Cambria bold, as a fraction of point size. Used only to
# predict how many lines a heading will wrap to, so the subtitle can be placed
# below it instead of on top of it.
_TITLE_CHAR_W = 0.47
_SUB_CHAR_W = 0.47


def _wrapped_lines(text, pt_size, width_in, char_w):
    """Estimate rendered line count for `text` at `pt_size` inside `width_in`."""
    per_line = max(12, int(width_in / (pt_size * char_w / 72.0)))
    lines, cur = 1, 0
    for word in text.split():
        add = len(word) + (1 if cur else 0)
        if cur + add > per_line:
            lines += 1
            cur = len(word)
        else:
            cur += add
    return lines


def heading(slide, title, *, eyebrow=None, dark=False, sub=None, size=31):
    y = Inches(0.46)
    if eyebrow:
        _, tf = tb(slide, M, y, CONTENT_W, Inches(0.26))
        para(tf, eyebrow.upper(), size=11.5, bold=True,
             color=ACCENT if not dark else ACCENT_L, first=True)
        y += Inches(0.32)

    w_in = CONTENT_W / 914400
    n = _wrapped_lines(title, size, w_in, _TITLE_CHAR_W)
    line_h = Inches(size / 72.0 * 1.22)
    _, tf = tb(slide, M, y, CONTENT_W, line_h * n + Inches(0.08))
    para(tf, title, size=size, bold=True, color=WHITE if dark else NAVY, font=H_FONT,
         first=True, line=1.1)
    y += line_h * n + Inches(0.16)

    if sub:
        ns = _wrapped_lines(sub, 14.5, w_in, _SUB_CHAR_W)
        sub_h = Inches(14.5 / 72.0 * 1.30) * ns
        _, tf = tb(slide, M, y, CONTENT_W, sub_h + Inches(0.06))
        para(tf, sub, size=14.5, color=ACCENT_L if dark else MUTED, first=True, line=1.18)
        y += sub_h + Inches(0.22)
    return y


def footnote(slide, text, *, dark=False, y=None):
    y = y or (H - Inches(0.62))
    _, tf = tb(slide, M, y, CONTENT_W, Inches(0.42))
    para(tf, text, size=10.5, color=RGBColor(0x8F, 0x9B, 0xA8) if dark else MUTED,
         first=True, line=1.15)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text.strip()


def picture(slide, path, x, y, w=None, h=None):
    return slide.shapes.add_picture(str(path), x, y, width=w, height=h)


def fit_picture(slide, path, box_x, box_y, box_w, box_h):
    """Insert a picture scaled to fit inside a box, centred."""
    from PIL import Image
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(box_w / iw, box_h / ih)
    w, h = int(iw * scale), int(ih * scale)
    x = box_x + (box_w - w) // 2
    y = box_y + (box_h - h) // 2
    return slide.shapes.add_picture(str(path), Emu(int(x)), Emu(int(y)),
                                    width=Emu(w), height=Emu(h))


def arrow(slide, x, y, w, h, *, color=ACCENT):
    sh = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x, y, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


# ---------------------------------------------------------------- content
F = json.loads((OUT_DIR / "findings.json").read_text(encoding="utf-8"))

U_RQ = ("How can human judgment be captured, governed, and used to support "
        "agentic-AI-driven variability exploration in guideline operationalization "
        "scenarios, enabling reliable human\u2013AI co-reasoning?")

SQS = [
    ("SQ1", "Selective intervention",
     "When and how should an agentic assessment system request human judgment, so that "
     "important uncertainties are addressed without unnecessary expert burden?",
     "Study 1 \u00b7 intervention architecture"),
    ("SQ2", "Governed knowledge reuse",
     "How should expert judgment be represented, validated, reconciled and stored so it can be "
     "reused transparently, without unsafe generalization or loss of human authority?",
     "Study 2 \u00b7 judgment lifecycle"),
    ("SQ3", "Evaluation and transfer",
     "How can reused judgment be evaluated and transferred across guideline-operationalization "
     "contexts \u2014 what generalizes, and what must adapt?",
     "Study 3 \u00b7 evaluation & transfer"),
]


def build():
    prs = new_deck()

    # ============================================================ 1 TITLE
    s = slide(prs, dark=True)
    card(s, Inches(0), Inches(0), W, Inches(0.06), fill=NAVY)
    _, tf = tb(s, M, Inches(1.02), CONTENT_W, Inches(0.3))
    para(tf, "IS RESEARCH SEMINAR  \u00b7  214.4001  \u00b7  FINAL PRESENTATION",
         size=12, bold=True, color=ACCENT_L, first=True)

    _, tf = tb(s, M, Inches(1.52), Inches(11.4), Inches(1.5))
    para(tf, "Not all differences matter.", size=42, bold=True, color=WHITE,
         font=H_FONT, first=True, line=1.06)
    para(tf, "So who decides which ones do?", size=42, bold=True, color=ACCENT_L,
         font=H_FONT, line=1.06)

    _, tf = tb(s, M, Inches(3.16), Inches(10.9), Inches(0.5))
    para(tf, "Human judgment in agentic-AI assessment of domain models \u2014 "
             "a literature review guided by a question",
         size=16.5, color=RGBColor(0xC8, 0xD6, 0xE6), first=True, line=1.2)

    c = card(s, M, Inches(3.95), Inches(11.4), Inches(1.42), fill=NAVY_SOFT)
    _, tf = tb(s, M + Inches(0.34), Inches(4.14), Inches(10.75), Inches(1.05))
    para(tf, "RESEARCH QUESTION", size=10.5, bold=True, color=ACCENT_L, first=True,
         space_after=5)
    para(tf, U_RQ, size=14.5, color=WHITE, italic=True, line=1.22)

    _, tf = tb(s, M, Inches(5.72), Inches(11.4), Inches(1.1))
    rich(tf, [("Ali Hamed", {"bold": True, "size": 15, "color": WHITE})], first=True,
         space_after=4)
    para(tf, "Supervisors: Prof. Iris Reinhartz-Berger (University of Haifa)  \u00b7  "
             "Prof. Arnon Sturm (Ben-Gurion University)",
         size=12.5, color=RGBColor(0xA9, 0xBC, 0xD0))
    para(tf, "Research-question wording is provisional, pending supervisor sign-off.",
         size=11, color=RGBColor(0x7E, 0x94, 0xAC), italic=True, space_before=5)
    notes(s, """
Open on the tension, not the tooling. Iris's own MODELS'26 paper is called "Not All
Differences Matter" - the class saw it in week 5. My question starts one step later:
once an agent has found a difference, WHO decides whether it is a legitimate
alternative or an error, and how does that decision stop being thrown away?

Say plainly: this is a literature review guided by a question. The wording of the
question is still provisional.  (~50 sec)
""")

    # ============================================================ 2 MOTIVATION
    s = slide(prs)
    y = heading(s, "An AI can find every difference \u2014 not which ones matter",
                eyebrow="Motivation \u00b7 the problem",
                sub="A deviation from a reference guideline is ambiguous by nature, "
                    "and the ambiguity is where expertise is expensive.")
    cw, gap = Inches(3.72), Inches(0.28)
    items = [
        ("A", "A legitimate alternative", GOOD,
         "A different model can express the same domain meaning. Penalising it teaches the "
         "wrong lesson."),
        ("B", "A genuine error", CRIT,
         "The model violates the domain, or encodes a misconception that should be corrected."),
        ("C", "A defect in the guideline", ORANGE,
         "The reference itself is wrong or incomplete \u2014 the deviation is evidence "
         "against the norm."),
    ]
    for i, (letter, title, col, body) in enumerate(items):
        x = M + i * (cw + gap)
        card(s, x, y, cw, Inches(2.72), fill=SOFT, line_col=LINE)
        badge(s, x + Inches(0.30), y + Inches(0.32), Inches(0.50), letter, fill=col)
        _, tf = tb(s, x + Inches(0.30), y + Inches(1.02), cw - Inches(0.60), Inches(1.5))
        para(tf, title, size=17, bold=True, color=NAVY, font=H_FONT, first=True,
             space_after=8)
        para(tf, body, size=13.5, color=MUTED, line=1.26)

    yb = y + Inches(3.06)
    card(s, M, yb, CONTENT_W, Inches(1.06), fill=NAVY)
    _, tf = tb(s, M + Inches(0.34), yb + Inches(0.2), CONTENT_W - Inches(0.68), Inches(0.72))
    para(tf, "Telling A, B and C apart is an interpretive act, not a classification.",
         size=17, bold=True, color=WHITE, font=H_FONT, first=True, space_after=5)
    para(tf, "It is exactly where automated assessment is least reliable \u2014 and where "
             "expert attention is scarcest.",
         size=13.5, color=ACCENT_L)
    notes(s, """
Ground the problem before any technology. The same structural difference can be three
completely different things, and only situated judgment separates them.

Note the asymmetry: the AI is cheap and tireless; the expert who can resolve A/B/C is
neither. That asymmetry is the whole thesis.  (~55 sec)
""")

    # ============================================================ 3 PUBLISHED EVIDENCE
    s = slide(prs)
    y = heading(s, "The published framework names its own need for a human",
                eyebrow="Motivation \u00b7 evidence from the problem world",
                sub="VEGO-AI (Reinhartz-Berger, Bragilovski & Sturm, MODELS \u201926) assesses "
                    "domain models with four coordinated LLM agents. It works \u2014 unevenly.")
    fit_picture(s, FIG / "04-published-profile-bare.png", M, y - Inches(0.04),
                Inches(8.30), Inches(4.34))
    x2 = M + Inches(8.52)
    cw2 = CONTENT_W - Inches(8.52)
    card(s, x2, y - Inches(0.04), cw2, Inches(4.34), fill=SOFT, line_col=LINE)
    _, tf = tb(s, x2 + Inches(0.26), y + Inches(0.20), cw2 - Inches(0.52), Inches(3.9))
    para(tf, "\u03c1 = 0.22", size=34, bold=True, color=CRIT, font=H_FONT, first=True)
    para(tf, "Spearman correlation between the Model Inspector's compliance scores and "
             "the human grader (p = 0.007).",
         size=12.5, color=MUTED, line=1.22, space_before=3, space_after=13)
    para(tf, "The paper's own future work:", size=12, bold=True, color=NAVY, space_after=5)
    para(tf, "\u201cincorporate human-in-the-loop oversight at key pipeline stages \u2014 "
             "guideline validation, compliance review, and variability classification\u201d",
         size=12.5, color=NAVY, italic=True, line=1.24, space_after=12)
    para(tf, "The need for human judgment is not my assumption. It is a published, "
             "peer-reviewed finding \u2014 and it names the three stages.",
         size=12.5, bold=True, color=INK, line=1.24)
    footnote(s, "Reference values reported by the paper for its own education-domain "
                "evaluation \u2014 engineering context, not a performance claim for this research.")
    notes(s, """
This is the strongest motivation slide because none of it is mine. The framework's own
authors report that uncovered-fragment auditing sits at 0.55 in both use-case settings and
say it "may require human involvement". Agreement with the human grader is rho = 0.22 -
weak.

And their future-work section names exactly the three pipeline stages where oversight is
needed. That is my SQ1 in someone else's peer-reviewed paper.

Be precise: these are THEIR numbers in THEIR setting. I am not claiming anything about my
own performance.  (~65 sec)
""")

    # ============================================================ 4 OBSERVABILITY
    s = slide(prs)
    y = heading(s, "I measured the same gap inside the system",
                eyebrow="Motivation \u00b7 evidence from my own experiments",
                sub="Replaying the assessment pipeline as an event stream shows how little "
                    "of its reasoning was ever reviewable.")
    fit_picture(s, FIG / "02-observability-gap-bare.png", M, y, Inches(7.85), Inches(3.95))
    x2 = M + Inches(8.10)
    cw2 = CONTENT_W - Inches(8.10)
    for i, (big, lbl, col) in enumerate([
        ("44\u00d7", "more lifecycle events occurred than the legacy queue could ever show", ACCENT),
        ("1.35", "guideline instability rate \u2014 references were repeatedly rewritten", ORANGE),
        ("33", "reference guidelines per setting revised with no human ever seeing them", CRIT),
    ]):
        cy = y + i * Inches(1.36)
        card(s, x2, cy, cw2, Inches(1.20), fill=SOFT, line_col=LINE)
        _, tf = tb(s, x2 + Inches(0.24), cy + Inches(0.16), cw2 - Inches(0.48), Inches(0.92))
        para(tf, big, size=27, bold=True, color=col, font=H_FONT, first=True, space_after=2)
        para(tf, lbl, size=11.5, color=MUTED, line=1.18)
    footnote(s, "EXP-006 and EXP-008 \u00b7 observability evidence only. These are heterogeneous "
                "lifecycle observations, not quality outcomes, and they support no claim about "
                "assessment accuracy.")
    notes(s, """
The published evaluation looks at outputs. I instrumented the process.

Replaying four settings produced 481 lifecycle events; the review queue a human actually
had could surface 11. Thirty-three reference guidelines per setting were revised without
any human ever seeing them - the guidelines the whole assessment is measured against.

Careful framing: this says the process was largely invisible. It does NOT say the
assessments were wrong. I have no expert labels yet.  (~60 sec)
""")

    # ============================================================ 5 DOSAGE
    s = slide(prs)
    y = heading(s, "\u2026 and simply asking the human more often does not solve it",
                eyebrow="Motivation \u00b7 why this needs research, not engineering",
                sub="Replaying five routing policies over those events maps the trade-off "
                    "between expert burden and how much of the risk gets seen.")
    fit_picture(s, FIG / "01-dosage-tradeoff-bare.png", M, y - Inches(0.06),
                Inches(8.25), Inches(4.16))
    x2 = M + Inches(8.48)
    cw2 = CONTENT_W - Inches(8.48)
    card(s, x2, y - Inches(0.06), cw2, Inches(4.16), fill=NAVY)
    _, tf = tb(s, x2 + Inches(0.26), y + Inches(0.18), cw2 - Inches(0.52), Inches(3.7))
    para(tf, "The dosage question", size=18, bold=True, color=WHITE, font=H_FONT,
         first=True, space_after=10)
    para(tf, "Review everything and automation is pointless. Review by a confidence "
             "threshold and you inherit the model's own miscalibration.",
         size=13, color=ACCENT_L, line=1.26, space_after=12)
    para(tf, "No policy reached 80% coverage of high-severity events while keeping "
             "expert burden under half.",
         size=13.5, bold=True, color=WHITE, line=1.26, space_after=12)
    para(tf, "That is SQ1, stated as a measurement rather than an opinion \u2014 and it is "
             "why \u201cadd a human in the loop\u201d is not yet an answer.",
         size=13, color=ACCENT_L, line=1.26)
    footnote(s, "EXP-007 \u00b7 design/mechanism evidence for coverage-versus-burden trade-offs "
                "only. No effort-reduction or accuracy claim is made or implied.")
    notes(s, """
This is the slide that turns a design intuition into a research question.

Five routing policies, replayed. To catch all high-severity events you must send 75-93%
of them to a person - which defeats the automation. Hold burden under 50% and coverage
falls to 0.54-0.73. The target region in the corner is empty.

So "put a human in the loop" is not an answer; WHICH cases, WHEN, and at what dose is an
open problem. Hence SQ1.  (~60 sec)
""")

    # ============================================================ 6 RESEARCH QUESTION
    s = slide(prs, dark=True)
    y = heading(s, "The research question", eyebrow="What I am asking", dark=True)
    c = card(s, M, y + Inches(0.06), CONTENT_W, Inches(1.52), fill=NAVY_SOFT)
    _, tf = tb(s, M + Inches(0.4), y + Inches(0.30), CONTENT_W - Inches(0.8), Inches(1.1))
    para(tf, U_RQ, size=20, color=WHITE, font=H_FONT, italic=True, first=True, line=1.24)

    y2 = y + Inches(1.86)
    cw3, gap3 = Inches(3.86), Inches(0.24)
    commitments = [
        ("It names the task, not the solution",
         "The object of study is variability exploration in guideline operationalization \u2014 "
         "not a particular agent architecture."),
        ("Reuse is deliberately not in the headline",
         "Whether captured judgment may be reused is a governed, testable concern for the "
         "sub-questions \u2014 not an assumption."),
        ("\u201cReliable\u201d is the retained quality target",
         "Earlier drafts also carried auditable, transferable and end-to-end; those are "
         "sub-question or artifact properties."),
    ]
    for i, (t, b) in enumerate(commitments):
        x = M + i * (cw3 + gap3)
        card(s, x, y2, cw3, Inches(1.92), fill=NAVY_SOFT)
        _, tf = tb(s, x + Inches(0.26), y2 + Inches(0.24), cw3 - Inches(0.52), Inches(1.5))
        para(tf, t, size=14.5, bold=True, color=ACCENT_L, font=H_FONT, first=True,
             space_after=7, line=1.14)
        para(tf, b, size=12.5, color=RGBColor(0xBF, 0xCE, 0xDE), line=1.24)
    footnote(s, "Wording refined with both supervisors and still provisional \u2014 two points "
                "remain open: \u201cexploration\u201d versus \u201cidentification and "
                "classification\u201d, and \u201chuman\u201d versus \u201cexpert\u201d judgment.",
             dark=True)
    notes(s, """
Read the question once, slowly.

Then the three design decisions behind its wording, because the course cares about how a
question is built. It names the task not the solution; it keeps "reuse" out of the
headline so that reuse stays something I test rather than assume; and it keeps "reliable"
as the single quality target.

Be honest that the wording is still provisional - two specific words are unresolved.
(~65 sec)
""")

    # ============================================================ 7 SUB-QUESTIONS
    s = slide(prs)
    y = heading(s, "Three derived questions \u2014 which become three studies",
                eyebrow="Derived set of questions",
                sub="Each sub-question owns one stage of the lifecycle: when to ask, "
                    "what to keep, and where it may travel.")
    ch = Inches(1.34)
    for i, (key, title, body, study) in enumerate(SQS):
        cy = y + i * (ch + Inches(0.20))
        card(s, M, cy, CONTENT_W, ch, fill=SOFT, line_col=LINE)
        badge(s, M + Inches(0.30), cy + Inches(0.30), Inches(0.62), key, size=14)
        _, tf = tb(s, M + Inches(1.14), cy + Inches(0.20), Inches(7.55), Inches(1.0))
        para(tf, title, size=17, bold=True, color=NAVY, font=H_FONT, first=True, space_after=5)
        para(tf, body, size=12.5, color=MUTED, line=1.22)
        card(s, M + Inches(8.92), cy + Inches(0.26), Inches(3.02), Inches(0.82),
             fill=ACCENT_L)
        _, tf = tb(s, M + Inches(9.06), cy + Inches(0.40), Inches(2.76), Inches(0.6),
                   anchor=MSO_ANCHOR.MIDDLE)
        para(tf, study, size=12.5, bold=True, color=NAVY, first=True, line=1.16)
    footnote(s, "The questions are deliberately domain-neutral. Software/modelling and "
                "healthcare are instantiation contexts for evaluation \u2014 they are not "
                "part of the questions themselves.")
    notes(s, """
Three sub-questions, and each one has to become a study with its own artifact and its own
method - that is the structure my supervisors asked for, and it maps onto the design-science
framing from this course.

SQ1 when to ask. SQ2 what to keep and under what governance. SQ3 how to evaluate it and
what transfers.

Stress the last line: the questions are domain-neutral. Software engineering and medicine
are where I will test them, not what they are about.  (~55 sec)
""")

    # ============================================================ 8 METHOD
    s = slide(prs)
    y = heading(s, "How the review is being done",
                eyebrow="Method",
                sub="A structured, exploratory review: protocol first, then searching, "
                    "screening, extraction and synthesis \u2014 recorded so it can be repeated.")
    body_h = (H - Inches(0.70)) - y
    left_w = Inches(7.15)
    card(s, M, y, left_w, body_h, fill=SOFT, line_col=LINE)
    _, tf = tb(s, M + Inches(0.30), y + Inches(0.24), left_w - Inches(0.60), Inches(3.5))
    para(tf, "Relevant research areas", size=15, bold=True, color=NAVY, font=H_FONT,
         first=True, space_after=8)
    for t, d in [
        ("Human involvement in agentic AI \u2014 the core",
         "any work placing human judgment inside a multi-step, tool-using AI process, "
         "whatever the domain"),
        ("Guideline-operationalization scenarios",
         "assessment against an evolving reference: modelling guidelines, clinical guidelines"),
        ("Knowledge capture, memory and reuse",
         "how a human decision is represented, stored, retrieved and governed"),
        ("Evaluation and validity",
         "how human\u2013AI assessment pipelines are evaluated, and what threatens the result"),
    ]:
        rich(tf, [(f"{t}  ", {"bold": True, "size": 12.5, "color": INK}),
                  (d, {"size": 12.5, "color": MUTED})], space_after=7, line=1.2)
    para(tf, "Deliberately excluded from the review body: enabling technologies "
             "(model architectures, local-inference tooling). They are engineering means, "
             "not the problem this review must justify.",
         size=11.5, color=MUTED, italic=True, space_before=6, line=1.2)

    rx = M + left_w + Inches(0.26)
    rw = CONTENT_W - left_w - Inches(0.26)
    rh_card = (body_h - Inches(0.20)) / 2
    card(s, rx, y, rw, rh_card, fill=WHITE, line_col=LINE)
    _, tf = tb(s, rx + Inches(0.26), y + Inches(0.20), rw - Inches(0.52), rh_card - Inches(0.36))
    para(tf, "Sources", size=15, bold=True, color=NAVY, font=H_FONT, first=True, space_after=7)
    para(tf, "Scopus \u00b7 ACM Digital Library \u00b7 IEEE Xplore \u00b7 SpringerLink",
         size=12.5, color=INK, line=1.2, space_after=4)
    para(tf, "Google Scholar and dblp for discovery, snowballing and verification.",
         size=12, color=MUTED, line=1.2)

    ry2 = y + rh_card + Inches(0.20)
    card(s, rx, ry2, rw, rh_card, fill=WHITE, line_col=LINE)
    _, tf = tb(s, rx + Inches(0.26), ry2 + Inches(0.20), rw - Inches(0.52), rh_card - Inches(0.36))
    para(tf, "Screening", size=15, bold=True, color=NAVY, font=H_FONT, first=True, space_after=7)
    rich(tf, [("Include  ", {"bold": True, "size": 12, "color": GOOD}),
              ("an explicit method, framework, artifact, empirical study or model.",
               {"size": 12, "color": MUTED})], line=1.2, space_after=5)
    rich(tf, [("Exclude  ", {"bold": True, "size": 12, "color": CRIT}),
              ("passing mentions of \u201chuman in the loop\u201d, product pieces, duplicates.",
               {"size": 12, "color": MUTED})], line=1.2, space_after=5)
    para(tf, "Every query, decision and exclusion reason is recorded.",
         size=11.5, color=MUTED, italic=True, line=1.2)
    notes(s, """
The course asks for the search process to be explicit, so this is the honest version.

Four research areas. The first is the centre of gravity, and that was a deliberate
supervisory decision: the review is organised around human involvement in agentic AI
generally, NOT around our specific application. The literature has to justify the problem,
not describe my solution.

Note what I exclude: enabling technology. Interesting, but it belongs in the methodology
chapter, not in the review that establishes the gap.  (~65 sec)
""")

    # ============================================================ 9 CORPUS
    s = slide(prs)
    y = heading(s, "What the search has produced so far",
                eyebrow="Method \u00b7 current state",
                sub="Each source was checked against an independent record before use \u2014 "
                    "132 of 144 confirmed, 11 partial, 1 quarantined.")
    fit_picture(s, FIG / "03-corpus-composition-bare.png", M, y, Inches(8.15), Inches(4.10))
    x2 = M + Inches(8.40)
    cw2 = CONTENT_W - Inches(8.40)
    card(s, x2, y, cw2, Inches(1.96), fill=SOFT, line_col=LINE)
    _, tf = tb(s, x2 + Inches(0.24), y + Inches(0.20), cw2 - Inches(0.48), Inches(1.6))
    para(tf, "Why verification came first", size=14, bold=True, color=NAVY, font=H_FONT,
         first=True, space_after=7)
    para(tf, "Generative tools invent plausible references. Every entry was checked against "
             "a publisher page, DOI, dblp or arXiv record; 1 that could not be confirmed is "
             "quarantined, not cited.",
         size=12, color=MUTED, line=1.22)

    card(s, x2, y + Inches(2.16), cw2, Inches(1.94), fill=RGBColor(0xFD, 0xF0, 0xF0),
         line_col=RGBColor(0xF0, 0xC8, 0xC8))
    _, tf = tb(s, x2 + Inches(0.24), y + Inches(2.36), cw2 - Inches(0.48), Inches(1.58))
    para(tf, "What this is not", size=14, bold=True, color=CRIT, font=H_FONT, first=True,
         space_after=7)
    para(tf, "The five frozen protocol queries have not yet been executed. This is what has "
             "been found and read \u2014 it is not evidence that nothing else exists.",
         size=12, color=MUTED, line=1.22)
    notes(s, """
144 sources, tagged to the question they serve.

Two things I want to be explicit about. First, verification: this corpus was built with
AI assistance, and the single biggest risk there is fabricated citations - so every entry
was checked against an independent record, and the one that could not be confirmed sits in
quarantine rather than in the review.

Second, and more important scientifically: the frozen protocol searches have NOT been run
yet. So I can say what I have read. I cannot yet say what does not exist. Every gap on the
next slides is stated within that limit.  (~65 sec)
""")

    # ============================================================ 10 STREAMS
    s = slide(prs)
    y = heading(s, F["streams_title"], eyebrow="Initial findings \u00b7 research streams",
                sub=F["streams_sub"])
    rows = F["streams"]
    cols, gapx, gapy = 3, Inches(0.22), Inches(0.18)
    cw4 = (CONTENT_W - gapx * (cols - 1)) / cols
    # Fill the space between the heading and the footnote rather than assuming a
    # fixed card height - the heading grows when a title or subtitle wraps.
    avail = (H - Inches(0.78)) - y
    chh = (avail - gapy) / 2
    for i, r in enumerate(rows):
        cx = M + (i % cols) * (cw4 + gapx)
        cy = y + (i // cols) * (chh + gapy)
        card(s, cx, cy, cw4, chh, fill=SOFT, line_col=LINE)
        badge(s, cx + Inches(0.22), cy + Inches(0.18), Inches(0.38), r["key"], size=11.5)
        _, tf = tb(s, cx + Inches(0.68), cy + Inches(0.18), cw4 - Inches(0.92), Inches(0.40),
                   anchor=MSO_ANCHOR.MIDDLE)
        rich(tf, [(r["name"], {"bold": True, "size": 12.5, "color": NAVY, "font": H_FONT}),
                  ("   " + r["count"], {"bold": True, "size": 11.5, "color": ACCENT})],
             first=True, line=1.06)
        _, tf = tb(s, cx + Inches(0.22), cy + Inches(0.66), cw4 - Inches(0.44), Inches(1.5))
        para(tf, r["establishes"], size=10, color=MUTED, line=1.16, first=True,
             space_after=5)
        rich(tf, [("Leaves open  ", {"bold": True, "size": 10, "color": CRIT}),
                  (r["leaves_open"], {"size": 10, "color": MUTED})], line=1.16)
    footnote(s, F["streams_foot"])
    notes(s, F["streams_notes"])

    # ============================================================ 11 FRAMEWORK
    s = slide(prs)
    y = heading(s, F["framework_name"], eyebrow="Initial findings \u00b7 analysis framework",
                sub=F["framework_sub"])
    avail_h = (H - Inches(0.86)) - y
    fig_w = Inches(8.45)
    fit_picture(s, FIG / "05-maturity-grid-bare.png", M, y, fig_w, avail_h)
    px = M + fig_w + Inches(0.22)
    pw = CONTENT_W - fig_w - Inches(0.22)
    _, tf = tb(s, px, y, pw, Inches(0.28))
    para(tf, "THREE CEILINGS", size=11, bold=True, color=CRIT, first=True)
    # Divide whatever height is left between the three cards, so a longer heading
    # never pushes their text past the card edge.
    top = y + Inches(0.36)
    gap_c = Inches(0.16)
    ch = ((H - Inches(0.86)) - top - gap_c * 2) / 3
    for i, (t, b) in enumerate(F["ceilings"]):
        cy = top + i * (ch + gap_c)
        card(s, px, cy, pw, ch, fill=SOFT, line_col=LINE)
        _, tf = tb(s, px + Inches(0.20), cy + Inches(0.14), pw - Inches(0.40), ch - Inches(0.24))
        para(tf, t, size=12.5, bold=True, color=NAVY, font=H_FONT, first=True, space_after=4)
        para(tf, b, size=10, color=MUTED, line=1.14)
    footnote(s, F["framework_foot"])
    notes(s, F["framework_notes"])

    # ============================================================ 12 GAPS
    s = slide(prs)
    y = heading(s, "What the framework makes visible",
                eyebrow="Initial findings \u00b7 identified gaps",
                sub="Each gap below is a thin or empty region of the matrix \u2014 stated as a "
                    "boundary of the reviewed corpus, not as a proven absence.")
    _, tf = tb(s, M, y, CONTENT_W, Inches(0.30))
    para(tf, F["gaps_scope"], size=13, bold=True, color=CRIT, font=H_FONT, first=True)
    y += Inches(0.38)
    gaps = F["gaps"][:4]
    gh = Inches(0.94)
    for i, g in enumerate(gaps):
        gy = y + i * (gh + Inches(0.16))
        core = g["severity"] == "core"
        card(s, M, gy, CONTENT_W, gh, fill=SOFT if not core else ACCENT_L,
             line_col=LINE if not core else ACCENT)
        badge(s, M + Inches(0.26), gy + Inches(0.22), Inches(0.50), g["id"],
              fill=ACCENT if core else MUTED, size=12)
        _, tf = tb(s, M + Inches(0.96), gy + Inches(0.15), Inches(8.6), Inches(0.68))
        para(tf, g["statement"], size=14, bold=True, color=NAVY, font=H_FONT, first=True,
             space_after=3, line=1.14)
        para(tf, g["evidence_basis"], size=11.5, color=MUTED, line=1.16)
        _, tf = tb(s, M + Inches(9.72), gy + Inches(0.28), Inches(2.3), Inches(0.42),
                   anchor=MSO_ANCHOR.MIDDLE)
        para(tf, g["which_sq"], size=12, bold=True, color=ACCENT if core else MUTED,
             first=True, align=PP_ALIGN.RIGHT)
    footnote(s, "Gaps emerge from the findings, and are stated within the reviewed corpus. "
                "Executing the frozen protocol searches is the next step, and may confirm, "
                "narrow or remove any of them.")
    notes(s, F["gaps_notes"])

    # ============================================================ 13 DIRECTION
    s = slide(prs)
    y = heading(s, "The gap this research takes on",
                eyebrow="Conclusion \u00b7 direction and contribution",
                sub=None)
    card(s, M, y, CONTENT_W, Inches(1.66), fill=NAVY)
    _, tf = tb(s, M + Inches(0.34), y + Inches(0.22), CONTENT_W - Inches(0.68), Inches(1.28))
    para(tf, F["chosen_gap"], size=17, bold=True, color=WHITE, font=H_FONT, first=True,
         line=1.2, space_after=6)
    para(tf, F["chosen_gap_why"], size=12.5, color=ACCENT_L, line=1.22)

    y2 = y + Inches(1.90)
    cw5, gap5 = Inches(3.86), Inches(0.24)
    blocks = [
        ("Environment", "Expert review is scarce; the meaning of a deviation is contextual; "
                        "and reference guidelines drift without human review.", MUTED),
        ("Artifact", "A selective-intervention policy plus a governed, provenance-preserving "
                     "judgment lifecycle around agentic assessment.", ACCENT),
        ("Evaluation", "Assessment quality, consistency, traceability, expert effort \u2014 "
                       "then what transfers to a second guideline context.", ORANGE),
    ]
    for i, (t, b, col) in enumerate(blocks):
        x = M + i * (cw5 + gap5)
        card(s, x, y2, cw5, Inches(1.80), fill=SOFT, line_col=LINE)
        _, tf = tb(s, x + Inches(0.26), y2 + Inches(0.24), cw5 - Inches(0.52), Inches(1.36))
        para(tf, t.upper(), size=11, bold=True, color=col, first=True, space_after=6)
        para(tf, b, size=12.5, color=MUTED, line=1.24)

    y3 = y2 + Inches(2.04)
    card(s, M, y3, CONTENT_W, Inches(1.02), fill=RGBColor(0xFD, 0xF0, 0xF0),
         line_col=RGBColor(0xF0, 0xC8, 0xC8))
    _, tf = tb(s, M + Inches(0.34), y3 + Inches(0.18), CONTENT_W - Inches(0.68), Inches(0.72))
    para(tf, "What I cannot claim yet", size=13, bold=True, color=CRIT, first=True,
         space_after=4)
    para(tf, "No accuracy improvement, no reduction in expert effort, no safe generalization "
             "and no clinical performance. Those require independent expert labels "
             "(currently 0 of 24) and the executed searches \u2014 both are next, not done.",
         size=12.5, color=MUTED, line=1.2)
    notes(s, """
Pull it together. The gap I take is the connected one - not "when to ask", not "what to
store", but the fact that these are studied separately and the handover between them is
where the open questions live.

Then the design-science shape this course gave me: environment, artifact, evaluation.

End on the boundary slide deliberately. Being explicit about what I cannot yet claim is
what makes the rest of it credible - and it defines exactly what the evaluation has to
deliver.  (~60 sec)
""")

    # ============================================================ 14 CLOSE
    s = slide(prs, dark=True)
    _, tf = tb(s, M, Inches(1.30), Inches(11.5), Inches(1.2))
    para(tf, "Where this goes next", size=32, bold=True, color=WHITE, font=H_FONT, first=True)
    steps = [
        ("1", "Execute the frozen searches", "Run the protocol queries per subsection, "
         "screen, and let the evidence confirm or correct these gaps."),
        ("2", "Populate the extraction matrix", "One row per included work, so the framework "
         "is filled by evidence rather than by expectation."),
        ("3", "Turn each question into a study", "Artifact and method per sub-question \u2014 "
         "the design-science structure this course sets out."),
    ]
    for i, (num, t, b) in enumerate(steps):
        cy = Inches(2.62) + i * Inches(1.26)
        badge(s, M, cy, Inches(0.52), num, fill=ACCENT)
        _, tf = tb(s, M + Inches(0.86), cy - Inches(0.02), Inches(11.0), Inches(1.0))
        para(tf, t, size=17, bold=True, color=WHITE, font=H_FONT, first=True, space_after=4)
        para(tf, b, size=13, color=RGBColor(0xBF, 0xCE, 0xDE), line=1.2)
    _, tf = tb(s, M, Inches(6.52), Inches(11.5), Inches(0.5))
    para(tf, "Thank you \u2014 questions welcome.", size=15, bold=True, color=ACCENT_L,
         first=True)
    notes(s, """
Three next steps, in order. Run the searches. Fill the matrix. Turn each question into a
study with an artifact and a method.

Close by naming the honest state: I have a verified corpus, a framework, and candidate
gaps. What I do not yet have is the executed protocol - and that is the immediate next
piece of work.  (~40 sec)
""")

    # ============================================================ BACKUP
    s = slide(prs)
    y = heading(s, "This work as design science",
                eyebrow="Backup · Hevner's three cycles",
                sub="Design science requires bidirectional grounding in a real environment "
                    "and a knowledge base, connected by an iterating design cycle (CL1–CL2).")
    body_h = (H - Inches(0.70)) - y
    cw6, gap6 = Inches(3.72), Inches(0.24)
    cycles = [
        ("RELEVANCE CYCLE", ACCENT,
         "Environment",
         "Expert review is scarce and scarce attention must be spent well; deviation "
         "meaning is contextual; reference guidelines drift unseen (EXP-006/008)."),
        ("DESIGN CYCLE", ORANGE,
         "Build → evaluate → iterate",
         "An escalation trigger conditioned on a persistent, scope-bounded judgment "
         "record (G1) — built and evaluated per sub-question, per the study contract."),
        ("RIGOR CYCLE", GOOD,
         "Knowledge base",
         "144 verified sources organised into six streams and the Judgment Lifecycle "
         "Grid — itself a candidate addition back to the knowledge base."),
    ]
    for i, (label, col, t, b) in enumerate(cycles):
        x = M + i * (cw6 + gap6)
        card(s, x, y, cw6, body_h, fill=SOFT, line_col=LINE)
        _, tf = tb(s, x + Inches(0.26), y + Inches(0.22), cw6 - Inches(0.52), body_h - Inches(0.4))
        para(tf, label, size=10.5, bold=True, color=col, first=True, space_after=10)
        para(tf, t, size=15, bold=True, color=NAVY, font=H_FONT, space_after=8, line=1.15)
        para(tf, b, size=12, color=MUTED, line=1.28)
    footnote(s, "Hevner & March (2003); Hevner et al. (2004), as presented in CL1–CL2.")
    notes(s, """
Backup slide for "how is this design science". Relevance cycle: the environment problem,
evidenced by my own measured mechanism gaps, not just asserted. Design cycle: the artifact
under construction, evaluated per the three-study contract. Rigor cycle: the verified
144-source knowledge base, with the Judgment Lifecycle Grid itself as a candidate
contribution back to that base - satisfying Guideline 4 (research contributions).
""")

    s = slide(prs)
    y = heading(s, "Design-science guidelines checklist",
                eyebrow="Backup · Hevner et al. (2004), CL2",
                sub="How the seven guidelines map onto this research, stated plainly rather "
                    "than assumed.")
    rows = [
        ("1", "Design as an artifact",
         "An escalation-trigger policy and a governed judgment lifecycle — a method "
         "and a model, in Hevner's terms."),
        ("2", "Problem relevance",
         "Motivated by the published framework's own reported need for human judgment "
         "(ρ = 0.22) and by measured mechanism gaps in this project (EXP-006–008)."),
        ("3", "Design evaluation",
         "Per-study measures already specified (SQ1–SQ3); accuracy/effort/generalization "
         "claims explicitly excluded until independently evidenced."),
        ("4", "Research contributions",
         "The Judgment Lifecycle Grid is a candidate contribution to the knowledge base, "
         "not only an analysis tool for this review."),
        ("5", "Research rigor",
         "144 sources, each independently verified against a publisher record, DOI, "
         "dblp or arXiv — zero fabricated citations."),
        ("6", "Design as a search process",
         "Six candidate gaps narrowed to one by evidence; the frozen protocol searches "
         "are the next iteration, not a one-shot search."),
        ("7", "Communication of research",
         "This seminar presentation for a technical audience; three planned "
         "publications per the study contract for the research community."),
    ]
    rh = (H - Inches(0.86) - y) / len(rows)
    for i, (num, t, b) in enumerate(rows):
        ry = y + i * rh
        badge(s, M, ry + Inches(0.04), Inches(0.34), num, size=11.5)
        _, tf = tb(s, M + Inches(0.52), ry, Inches(3.0), rh, anchor=MSO_ANCHOR.MIDDLE)
        para(tf, t, size=12.5, bold=True, color=NAVY, font=H_FONT, first=True, line=1.1)
        _, tf = tb(s, M + Inches(3.70), ry, CONTENT_W - Inches(3.70), rh,
                   anchor=MSO_ANCHOR.MIDDLE)
        para(tf, b, size=11.5, color=MUTED, first=True, line=1.2)
    notes(s, """
Use only if asked to justify this as design science against the specific Hevner
guidelines. Each row names the real artifact behind it - nothing here is generic.
""")

    s = slide(prs)
    y = heading(s, "Use of generative AI in preparing this work",
                eyebrow="Backup \u00b7 required disclosure",
                sub="Declared per the course requirement that the work state whether and how "
                    "GenAI was used, and for what.")
    left = Inches(6.0)
    card(s, M, y, left, Inches(3.7), fill=SOFT, line_col=LINE)
    _, tf = tb(s, M + Inches(0.28), y + Inches(0.22), left - Inches(0.56), Inches(3.3))
    para(tf, "Used for", size=15, bold=True, color=GOOD, font=H_FONT, first=True, space_after=8)
    for t in ["Brainstorming and refining the wording of the research questions.",
              "Discovering candidate literature and drafting search-query families.",
              "Screening support: summarising abstracts to triage relevance.",
              "Extracting structured fields from sources into the review workbook.",
              "Drafting and rephrasing slide text, and generating the figures from "
              "measured result files."]:
        para(tf, "\u2022  " + t, size=12.5, color=MUTED, line=1.22, space_after=6)

    rx = M + left + Inches(0.28)
    rw = CONTENT_W - left - Inches(0.28)
    card(s, rx, y, rw, Inches(3.7), fill=RGBColor(0xFD, 0xF0, 0xF0),
         line_col=RGBColor(0xF0, 0xC8, 0xC8))
    _, tf = tb(s, rx + Inches(0.28), y + Inches(0.22), rw - Inches(0.56), Inches(3.3))
    para(tf, "Not used for", size=15, bold=True, color=CRIT, font=H_FONT, first=True,
         space_after=8)
    for t in ["Generating citations. Every reference was verified against a publisher page, "
              "DOI, dblp or arXiv record; unverifiable entries are quarantined.",
              "Deciding the research questions or the message of the review.",
              "Designing the analysis framework \u2014 that is the conceptual work.",
              "Determining gaps. A model reports what exists, not what is missing; gaps come "
              "from the framework and remain provisional until the searches run."]:
        para(tf, "\u2022  " + t, size=12.5, color=MUTED, line=1.22, space_after=6)
    notes(s, """
Backup slide, but I am happy to show it. The course was explicit about both the disclosure
requirement and the specific danger - that models invent citations and cannot tell you what
is absent.

So: assistance with discovery, screening, extraction and drafting. Not with deciding the
message, designing the framework, or asserting gaps. And every citation independently
verified.
""")

    s = slide(prs)
    y = heading(s, "Evidence boundary held throughout",
                eyebrow="Backup \u00b7 what is and is not claimed",
                sub="Separating what the current work can demonstrate from what still "
                    "requires independent evidence.")
    lw = (CONTENT_W - Inches(0.28)) / 2
    card(s, M, y, lw, Inches(3.5), fill=SOFT, line_col=LINE)
    _, tf = tb(s, M + Inches(0.28), y + Inches(0.22), lw - Inches(0.56), Inches(3.1))
    para(tf, "Can be stated (mechanism / observability)", size=14.5, bold=True, color=GOOD,
         font=H_FONT, first=True, space_after=9)
    for t in ["481 lifecycle events reconstructed against a legacy queue of 11.",
              "Guideline instability measured at 1.35; 33 guidelines per setting never reviewed.",
              "Coverage-versus-burden frontier mapped across five routing policies.",
              "The protected baseline is unchanged \u2014 0 of 27 classifications altered."]:
        para(tf, "\u2022  " + t, size=12.5, color=MUTED, line=1.22, space_after=7)

    rx = M + lw + Inches(0.28)
    card(s, rx, y, lw, Inches(3.5), fill=RGBColor(0xFD, 0xF0, 0xF0),
         line_col=RGBColor(0xF0, 0xC8, 0xC8))
    _, tf = tb(s, rx + Inches(0.28), y + Inches(0.22), lw - Inches(0.56), Inches(3.1))
    para(tf, "Not claimed \u2014 requires evidence that does not exist yet", size=14.5,
         bold=True, color=CRIT, font=H_FONT, first=True, space_after=9)
    for t in ["No claim of improved assessment accuracy \u2014 0 of 24 generalization-safe "
              "expert labels are validated.",
              "No claim of reduced expert workload.",
              "No claim of safe generalization or transfer across contexts.",
              "No claim of any kind about clinical performance.",
              "No claim that the literature holds no prior solution \u2014 the protocol "
              "searches are not yet executed."]:
        para(tf, "\u2022  " + t, size=12.5, color=MUTED, line=1.22, space_after=7)
    notes(s, """
This is the slide I would use if someone asks "so does it work?".

The honest answer: I can show the mechanism and the observability, and I can show the
trade-off. I cannot show quality, effort or transfer, because that needs independent expert
labels and I have none validated yet.

Stating that boundary is not weakness - it is what makes the eventual evaluation meaningful.
""")

    prs.save(DECK)
    print(f"saved: {DECK}")
    print(f"slides: {len(prs.slides.__iter__.__self__._sldIdLst)}")
    return DECK


if __name__ == "__main__":
    build()
