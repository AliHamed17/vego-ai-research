#!/usr/bin/env python3
"""Generate the PhD proposal figures as SVG (and PDF/PNG via the render step).

Five figures:
  1. The VEGO-AI four-agent architecture (the published baseline).
  2. Baseline plus the doctoral governed-judgment extension.
  3. The three research questions as one cumulative programme.
  4. The evidence ladder and claim gates.
  5. The three-year, semester-aligned research plan.

Every arrowhead is explicit geometry (see figlib) so nothing is lost in
conversion, and every label position is chosen to avoid overlap.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import (AMBER, BLUE, GREEN, GREY, INK, LINE, NAVY, PANEL, PURPLE,  # noqa: E402
                    RED, RULE, Fig)

OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/research/figures"
os.makedirs(OUT, exist_ok=True)


# ---------------------------------------------------------------- figure 1
def fig1() -> None:
    f = Fig(1180, 640)
    f.rect(250, 96, 680, 452, fill=PANEL, stroke=RULE, sw=1.4, r=6)
    f.text(268, 120, "VEGO-AI FRAMEWORK", size=11.5, fill="#8a93a8", anchor="start",
           weight="700", spacing="0.08em")

    # external language inputs
    f.rect(404, 18, 176, 46, fill="#eef4fd", stroke=BLUE, sw=1.3, r=6, dash="5 3")
    f.lines(492, 38, ["Language reference", "manual"], size=12.5, fill=NAVY, lh=16)
    f.rect(600, 18, 196, 46, fill="#eef4fd", stroke=BLUE, sw=1.3, r=6, dash="5 3")
    f.lines(698, 38, ["Language definition", "(grammars, metamodels)"], size=12.5, fill=NAVY, lh=16)
    f.arrow([(492, 64), (492, 82), (592, 82), (592, 140)])
    f.arrow([(698, 64), (698, 82), (604, 82), (604, 140)])

    # agents
    f.box(470, 140, 256, 66, "Agent 1 · Language Advisor", ["produces the language template"], fill=BLUE)
    f.box(286, 300, 230, 74, "Agent 2 · Domain Advisor", ["evolving reference guidelines"], fill=GREEN)
    f.box(664, 300, 230, 74, "Agent 3 · Model Inspector", ["assesses compliance,", "refines guidelines"], fill=PURPLE)
    f.box(470, 446, 256, 72, "Agent 4 · Variability Explorer",
          ["classifies patterns as", "substantial or occasional"], fill=AMBER)

    # side inputs / outputs
    f.rect(40, 312, 180, 50, fill="#e9f6ee", stroke=GREEN, sw=1.3, r=6)
    f.text(130, 342, "Domain description", size=12.5, fill="#12603c")
    f.arrow([(220, 337), (286, 337)], color=GREEN)

    f.rect(962, 246, 180, 50, fill="#f4eefb", stroke=PURPLE, sw=1.3, r=6)
    f.text(1052, 276, "Case model", size=12.5, fill="#4a2a73")
    f.arrow([(962, 271), (898, 306)], color=PURPLE)

    f.rect(962, 376, 180, 50, fill="#f4eefb", stroke=PURPLE, sw=1.3, r=6)
    f.text(1052, 406, "Case feedback", size=12.5, fill="#4a2a73")
    f.arrow([(898, 368), (962, 401)], color=PURPLE)

    f.rect(40, 458, 180, 50, fill="#fdf4e3", stroke=AMBER, sw=1.3, r=6)
    f.text(130, 488, "Variability patterns", size=12.5, fill="#8a5c05")
    f.arrow([(470, 483), (220, 483)], color=AMBER)

    # internal edges
    f.arrow([(470, 170), (344, 170), (344, 300)])
    f.text(340, 163, "language template", size=10.5, fill=LINE, anchor="end")

    # A2 <-> A1
    f.arrow([(398, 300), (398, 226), (470, 226)])
    f.text(404, 219, "questions", size=10, fill=GREY, italic=True, anchor="start")
    f.arrow([(470, 248), (428, 248), (428, 300)])
    f.text(434, 268, "answers", size=10, fill=GREY, italic=True, anchor="start")

    # A3 <-> A1
    f.arrow([(782, 300), (782, 226), (726, 226)])
    f.text(776, 219, "questions", size=10, fill=GREY, italic=True, anchor="end")
    f.arrow([(726, 248), (752, 248), (752, 300)])
    f.text(746, 268, "answers", size=10, fill=GREY, italic=True, anchor="end")

    # A2 <-> A3
    f.arrow([(664, 324), (516, 324)])
    f.text(590, 317, "questions", size=10.5, fill=LINE)
    f.arrow([(516, 354), (664, 354)])
    f.text(590, 370, "answers", size=10.5, fill=LINE)

    # reference guidelines, routed above the pair
    f.arrow([(466, 300), (466, 276), (836, 276), (836, 300)])
    f.text(650, 269, "reference guidelines", size=10.5, fill=LINE)

    # A2 <-> A4
    f.arrow([(392, 374), (392, 468), (470, 468)])
    f.text(398, 432, "identified variability", size=10.5, fill=LINE, anchor="start")
    f.arrow([(470, 502), (356, 502), (356, 374)])
    f.text(350, 432, "answers", size=10, fill=GREY, italic=True, anchor="end")

    # A3 <-> A4  (labels separated to avoid the v0.4 collision)
    f.arrow([(788, 374), (788, 468), (726, 468)])
    f.text(794, 424, "observed variability", size=10.5, fill=LINE, anchor="start")
    f.arrow([(726, 502), (846, 502), (846, 374)])
    f.text(852, 452, "answers", size=10, fill=GREY, italic=True, anchor="start")

    f.caption(590, 590, "Figure 1. The VEGO-AI four-agent architecture.",
              "Adapted from Reinhartz-Berger, Bragilovski and Sturm (MODELS ’26). Agents exchange "
              "questions and answers through a structured protocol.")
    f.save(os.path.join(OUT, "fig1-vego-ai-architecture.svg"))


# ---------------------------------------------------------------- figure 2
def fig2() -> None:
    f = Fig(1180, 600)

    f.rect(30, 70, 470, 424, fill="#f5f8fd", stroke=BLUE, sw=1.5, r=10)
    f.text(60, 100, "VEGO-AI BASELINE (published)", size=12, fill=BLUE, anchor="start",
           weight="700", spacing="0.06em")
    f.rect(540, 70, 610, 424, fill="#fdf9f0", stroke=AMBER, sw=1.5, r=10)
    f.text(570, 100, "DOCTORAL EXTENSION — GOVERNED HUMAN JUDGMENT", size=12, fill="#8a5c05",
           anchor="start", weight="700", spacing="0.06em")

    # baseline agents
    f.box(60, 124, 190, 62, "Language Advisor", ["language template"], fill=BLUE, tsize=13, ssize=11)
    f.box(280, 124, 190, 62, "Domain Advisor", ["reference guidelines"], fill=GREEN, tsize=13, ssize=11)
    f.box(60, 214, 190, 62, "Model Inspector", ["compliance + signals"], fill=PURPLE, tsize=13, ssize=11)
    f.box(280, 214, 190, 62, "Variability Explorer", ["substantial / occasional"], fill=AMBER, tsize=13, ssize=11)
    f.arrow([(250, 155), (280, 155)], sw=1.3)
    f.arrow([(155, 186), (155, 214)], sw=1.3)
    f.arrow([(250, 245), (280, 245)], sw=1.3)
    f.arrow([(375, 186), (375, 214)], sw=1.3)

    f.rect(60, 306, 410, 76, fill="#ffffff", stroke=RULE, sw=1.2, r=6)
    f.text(80, 330, "Baseline outputs", size=12, fill=NAVY, anchor="start", weight="700")
    f.text(80, 350, "compliance vectors · uncovered fragments · deviation patterns", size=11, fill=GREY, anchor="start")
    f.text(80, 368, "confidence signals · review flags", size=11, fill=GREY, anchor="start")

    f.text(265, 424, "The baseline detects and classifies variability.", size=11.5, fill=BLUE, italic=True)
    f.text(265, 444, "It does not decide when to ask a person,", size=11.5, fill=BLUE, italic=True)
    f.text(265, 464, "nor what to keep from the answer.", size=11.5, fill=BLUE, italic=True)

    # doctoral layer
    f.box(570, 124, 250, 74, "RQ1 · Selective intervention",
          ["when should the system ask?"], fill="#ffffff", tcolor=NAVY, scolor=GREY,
          stroke=BLUE, sw=1.6, tsize=13, ssize=11)
    f.box(870, 124, 250, 74, "Expert review",
          ["decision · rationale · scope"], fill="#ffffff", tcolor=NAVY, scolor=GREY,
          stroke=RULE, sw=1.4, tsize=13, ssize=11)
    f.box(570, 236, 250, 74, "RQ2 · Judgment lifecycle",
          ["represent · validate · store"], fill="#ffffff", tcolor=NAVY, scolor=GREY,
          stroke=GREEN, sw=1.6, tsize=13, ssize=11)
    f.box(870, 236, 250, 74, "Judgment memory",
          ["scoped · contestable · revocable"], fill="#ffffff", tcolor=NAVY, scolor=GREY,
          stroke=RULE, sw=1.4, tsize=13, ssize=11)
    f.box(720, 348, 250, 74, "RQ3 · Transfer and evaluation",
          ["domain-specific vs transferable"], fill="#ffffff", tcolor=NAVY, scolor=GREY,
          stroke=PURPLE, sw=1.6, tsize=13, ssize=11)

    f.arrow([(470, 245), (570, 161)], color=AMBER, sw=1.6)
    f.text(500, 196, "uncertainty", size=10, fill="#8a5c05", anchor="start", italic=True)
    f.arrow([(820, 161), (870, 161)], color=LINE, sw=1.4)
    f.arrow([(995, 198), (995, 236)], color=LINE, sw=1.4)
    f.arrow([(870, 273), (820, 273)], color=LINE, sw=1.4)
    f.arrow([(695, 198), (695, 236)], color=LINE, sw=1.4)
    f.arrow([(695, 310), (760, 348)], color=LINE, sw=1.4)
    f.arrow([(995, 310), (930, 348)], color=LINE, sw=1.4)

    f.rect(570, 440, 550, 40, fill="#fff8e8", stroke=AMBER, sw=1.2, r=6)
    f.text(845, 465, "Safety invariant: reused judgment stays advisory unless an authorised change path is approved.",
           size=11, fill="#8a5c05")

    f.caption(590, 540, "Figure 2. The baseline and the doctoral extension.",
              "The doctorate adds the decision of when to ask, what to preserve from the answer, and where a judgment may safely apply.")
    f.save(os.path.join(OUT, "fig2-baseline-and-extension.svg"))


# ---------------------------------------------------------------- figure 3
def fig3() -> None:
    f = Fig(1180, 520)
    cols = [
        (60, BLUE, "RQ1 · Selective intervention", "Study 1",
         ["Inputs", "uncertainty · impact · novelty · workload"],
         ["Artifact", "intervention policy and review request"],
         ["Primary evidence", "critical-uncertainty coverage vs expert burden"]),
        (420, GREEN, "RQ2 · Governed judgment lifecycle", "Study 2",
         ["Inputs", "expert response · system reasoning · sources"],
         ["Artifact", "judgment record and lifecycle controls"],
         ["Primary evidence", "provenance · conflicts · scope · authority"]),
        (780, PURPLE, "RQ3 · Transfer and evaluation", "Study 3",
         ["Inputs", "frozen baseline · governed memory · new contexts"],
         ["Artifact", "transfer taxonomy and evaluation protocol"],
         ["Primary evidence", "safe reuse · failure modes · validity"]),
    ]
    for x, colour, title, study, inp, art, ev in cols:
        f.rect(x, 60, 340, 300, fill="#ffffff", stroke=colour, sw=1.8, r=10)
        f.rect(x, 60, 340, 52, fill=colour, r=10)
        f.rect(x, 96, 340, 16, fill=colour, r=0)
        f.text(x + 170, 84, title, size=13.5, fill="#ffffff", weight="700")
        f.text(x + 170, 102, study, size=11, fill="#e8edf7")
        yy = 142
        for label, value in (inp, art, ev):
            f.text(x + 20, yy, label, size=10.5, fill=colour, anchor="start", weight="700")
            f.text(x + 20, yy + 18, value, size=11, fill=INK, anchor="start")
            yy += 58
    # hand-offs
    f.arrow([(400, 210), (420, 210)], color=LINE, sw=1.8, head_size=11)
    f.text(410, 196, "captured", size=10, fill=GREY)
    f.text(410, 236, "judgments", size=10, fill=GREY)
    f.arrow([(760, 210), (780, 210)], color=LINE, sw=1.8, head_size=11)
    f.text(770, 196, "governed", size=10, fill=GREY)
    f.text(770, 236, "judgments", size=10, fill=GREY)
    # feedback
    f.arrow([(950, 360), (950, 400), (230, 400), (230, 360)], color=PURPLE, sw=1.5, dash="6 4")
    f.text(590, 394, "transfer failures and scope boundaries refine the intervention and governance policies",
           size=11, fill=PURPLE, italic=True)

    f.caption(590, 460, "Figure 3. Three questions, one cumulative programme.",
              "Each question hands a defined product to the next; results from the last refine the first two.")
    f.save(os.path.join(OUT, "fig3-research-programme.svg"))


# ---------------------------------------------------------------- figure 4
def fig4() -> None:
    f = Fig(1180, 430)
    tiers = [
        (40, "#eef4fd", BLUE, "L1 · Mechanism",
         ["implemented artifacts,", "schemas, routing,", "traceability"], "Available now", GREEN),
        (325, "#e9f6ee", GREEN, "L2 · Conformance",
         ["contract tests,", "scenario coverage,", "failure containment"], "Available with cited tests", GREEN),
        (610, "#fdf4e3", AMBER, "L3 · Human validity",
         ["independent expert labels,", "inter-rater agreement,", "adjudication"], "EXP-005 open: 0 of 24", RED),
        (895, "#fbe7e5", RED, "L4 · Transfer and impact",
         ["leakage-safe second setting,", "workload study,", "comparative outcomes"], "Not claimable yet", RED),
    ]
    for x, bg, edge, title, body, status, scol in tiers:
        f.rect(x, 60, 245, 250, fill=bg, stroke=edge, sw=1.6, r=10)
        f.text(x + 122, 96, title, size=14, fill=edge, weight="700")
        for k, line in enumerate(body):
            f.text(x + 122, 140 + k * 19, line, size=11, fill=INK)
        f.rect(x + 22, 246, 201, 34, fill="#ffffff", stroke=scol, sw=1.3, r=5)
        f.text(x + 122, 268, status, size=11, fill=scol, weight="700")
    for x in (285, 570, 855):
        f.arrow([(x, 185), (x + 40, 185)], color=LINE, sw=1.6, head_size=10)

    f.rect(40, 336, 1100, 34, fill="#f5f7fb", stroke=RULE, sw=1.2, r=6)
    f.text(590, 358, "Levels are cumulative: mechanism readiness does not imply human validity, and human validity does not imply transfer.",
           size=11.5, fill=NAVY)
    f.caption(590, 404, "Figure 4. Evidence ladder and claim gates.", None)
    f.save(os.path.join(OUT, "fig4-evidence-ladder.svg"))


# ---------------------------------------------------------------- figure 5
def fig5() -> None:
    """Semester-aligned plan. Labels sit OUTSIDE the bars, which is what fixes the
    clipping seen in the v0.4 figure."""
    blocks = [
        ("B0", "Aug–Sep 26", "Wording sign-off and RQ architecture", BLUE, 0, 1),
        ("B1", "Oct–Dec 26", "Literature execution and Study 1 design", BLUE, 1, 1),
        ("B2", "Jan–Mar 27", "Intervention signals and controlled pilot", GREEN, 2, 1),
        ("B3", "Apr–Jun 27", "Study 1 human evaluation", GREEN, 3, 1),
        ("B4", "Jul–Sep 27", "Judgment schema and governance controls", PURPLE, 4, 1),
        ("B5", "Oct–Dec 27", "Study 2 validation and expert review", PURPLE, 5, 1),
        ("B6", "Jan–Mar 28", "Lifecycle integration and hardening", PURPLE, 6, 1),
        ("B7", "Apr–Jun 28", "Transfer protocol and labelling", AMBER, 7, 1),
        ("B8", "Jul–Sep 28", "Study 3 software and modelling evaluation", AMBER, 8, 1),
        ("B9", "Oct–Dec 28", "Second-context transfer test", AMBER, 9, 1),
        ("B10", "Jan–Mar 29", "Synthesis and design principles", NAVY, 10, 1),
        ("B11", "Apr–Jul 29", "Integration, writing and defence preparation", NAVY, 11, 1),
    ]
    left, top, rowh, colw = 250, 128, 34, 62
    # Reserve room on the right for the longest label so nothing is ever clipped.
    longest = max(len(b[2]) for b in blocks)
    w = left + colw * 12 + int(longest * 5.9) + 60
    f = Fig(w, top + rowh * len(blocks) + 150)

    f.text(w / 2, 46, "Three-year, semester-aligned research plan", size=17, fill=NAVY, weight="700")
    f.text(w / 2, 70, "Blocks are approximately three months and semester-aligned.",
           size=11, fill=GREY)
    f.text(w / 2, 88, "Dates are internal working targets, not confirmed university deadlines.",
           size=11, fill=GREY)

    # year bands
    years = [("Year 1", 0, 4), ("Year 2", 4, 8), ("Year 3", 8, 12)]
    for label, a, b in years:
        x = left + a * colw
        f.rect(x, top - 26, (b - a) * colw, 20, fill="#f0f3f9", stroke=RULE, sw=1, r=4)
        f.text(x + (b - a) * colw / 2, top - 12, label, size=11, fill=NAVY, weight="700")

    for i in range(13):
        x = left + i * colw
        f.path(f"M{x},{top - 6} L{x},{top + rowh * len(blocks)}", stroke="#e4e8f0", sw=1)

    for k, (code, period, label, colour, start, span) in enumerate(blocks):
        y = top + k * rowh
        f.text(40, y + 22, code, size=11.5, fill=NAVY, anchor="start", weight="700")
        f.text(78, y + 22, period, size=11, fill=GREY, anchor="start")
        bx = left + start * colw
        f.rect(bx + 3, y + 8, span * colw - 6, 20, fill=colour, r=4)
        # Label sits outside the bar. If it would run past the canvas, flip it to
        # the left of the bar instead of letting it clip.
        est = len(label) * 5.9
        if bx + span * colw + 8 + est <= w - 24:
            f.text(bx + span * colw + 8, y + 22, label, size=11, fill=INK, anchor="start")
        else:
            f.text(bx - 8, y + 22, label, size=11, fill=INK, anchor="end")

    f.caption(w / 2, top + rowh * len(blocks) + 66,
              "Figure 5. Three-year, semester-aligned research plan.",
              "Never planned month by month. Later blocks are deliberately coarser: their content depends on results from the blocks before them.")
    f.save(os.path.join(OUT, "fig5-three-year-plan.svg"))


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5()
    print(f"wrote 5 SVG figures to {OUT}")
