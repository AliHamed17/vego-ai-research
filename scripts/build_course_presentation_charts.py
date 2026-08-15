"""Build the figures for the IS Research Seminar final presentation.

Every number here is read from, or traceable to, a real artifact:
  - EXP-006/007/008 summaries under reports/generated/
  - literature/verified-research-corpus-2026-08-12.json
  - the published VEGO-AI paper figures recorded in
    docs/research/governance/vego-ai-foundation-paper-record.md

No figure asserts an accuracy, generalization, effort-reduction, or clinical
claim: EXP-005 stands at 0/24 validated generalization-safe expert labels.

Palette: the validated dataviz reference instance (light mode). Categorical
slots are used in fixed order and every series is direct-labeled, which is the
relief required for the sub-3:1 slots (aqua, yellow).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

REPO = Path(r"C:\Users\ahamed\vego-ai")
OUT = REPO / "outputs" / "course-presentation" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# --- validated light-mode palette -------------------------------------------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASE = "#c3c2b7"
S1, S2, S3, S4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
CRITICAL, GOOD, WARNING = "#d03b3b", "#0ca30c", "#fab219"
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#256abf", "#184f95"]

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"],
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "text.color": INK,
    "axes.labelcolor": INK2,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": BASE,
    "axes.linewidth": 1.0,
    "grid.color": GRID,
    "grid.linewidth": 1.0,
})
DPI = 200

# When a figure is placed on a slide the slide already carries the title and the
# subtitle, so repeating them inside the image is redundant and wastes plot area.
# BARE=True suppresses in-figure titles; the caveat footnotes are always kept,
# because they travel with the data rather than with the layout.
BARE = False
SUFFIX = ""


def style(ax, *, xlab="", ylab="", title="", sub=""):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(BASE)
    if BARE:
        title = sub = ""
    # Title sits clear of the subtitle: the subtitle is pinned just above the
    # axes and the title pad is large enough to clear it at any figure height.
    if title:
        ax.set_title(title, fontsize=17, weight="bold", color=INK, loc="left",
                     pad=38 if sub else 12)
    if sub:
        ax.text(0, 1.022, sub, transform=ax.transAxes, fontsize=11.5, color=INK2,
                ha="left", va="bottom")
    if xlab:
        ax.set_xlabel(xlab, fontsize=12, color=INK2, labelpad=9)
    if ylab:
        ax.set_ylabel(ylab, fontsize=12, color=INK2, labelpad=9)
    ax.tick_params(labelsize=11, length=0)


def save(fig, name):
    if SUFFIX:
        stem, ext = name.rsplit(".", 1)
        name = f"{stem}{SUFFIX}.{ext}"
    p = OUT / name
    fig.savefig(p, dpi=DPI, bbox_inches="tight", pad_inches=0.30)
    plt.close(fig)
    print(f"  {name}")
    return p


# ---------------------------------------------------------------- figure 1
def fig_dosage_tradeoff():
    """EXP-007: no intervention dosage mode reaches coverage>=.8 at load<=.5."""
    d = json.loads((REPO / "reports/generated/exp007/summary.json").read_text(encoding="utf-8"))
    pf = d["pareto_frontiers"]
    settings = [
        ("cd_ch", "Class diagrams · Cheers", S1),
        ("cd_pw", "Class diagrams · ParkWise", S2),
        ("ucd_ch", "Use-case diagrams · Cheers", S3),
        ("ucd_pw", "Use-case diagrams · ParkWise", S4),
    ]
    fig, ax = plt.subplots(figsize=(11.2, 6.0))

    # the target region the architecture was asked to hit - and never does
    ax.add_patch(Rectangle((0, 0.8), 0.5, 0.22, facecolor=GOOD, alpha=0.09, zorder=0))
    ax.plot([0.5, 0.5], [0, 1.02], color=BASE, lw=1.2, ls=(0, (5, 4)), zorder=1)
    ax.text(0.245, 0.905, "TARGET\ncoverage \u2265 0.80  at  load \u2264 0.50",
            ha="center", va="center", fontsize=11.5, color=INK2, weight="bold", zorder=3)
    ax.text(0.245, 0.845, "no mode reaches this region", ha="center", va="center",
            fontsize=11, color=CRITICAL, style="italic", weight="bold", zorder=3)

    # All four curves converge on (~0.85, 1.0), so endpoint direct labels would
    # collide into unreadable overlap. Identity is carried by a legend placed in
    # the empty lower-right instead - still never colour-alone.
    for key, label, colr in settings:
        pts = sorted(pf[key], key=lambda r: r["event_load"])
        xs = [p["event_load"] for p in pts]
        ys = [p["high_severity_coverage"] for p in pts]
        ax.plot(xs, ys, color=colr, lw=2.0, marker="o", ms=8, label=label,
                markeredgecolor=SURFACE, markeredgewidth=2, zorder=4)

    leg = ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.02), frameon=False,
                    fontsize=11.5, handlelength=1.6, labelspacing=0.75,
                    borderpad=0.8, title="Evaluation setting")
    leg.get_title().set_fontsize(11.5)
    leg.get_title().set_color(INK2)
    leg.get_title().set_weight("bold")
    for t in leg.get_texts():
        t.set_color(INK2)

    style(ax,
          xlab="Share of assessment events routed to a human  (expert burden)",
          ylab="High-severity coverage",
          title="The intervention-dosage problem is real, and unsolved",
          sub="EXP-007 \u00b7 replay of five routing policies over 481 lifecycle events, four settings")
    ax.set_xlim(-0.03, 1.05)
    ax.set_ylim(-0.03, 1.06)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.grid(axis="both", alpha=0.55)
    ax.set_axisbelow(True)
    fig.text(0.008, -0.045,
             "Full high-severity coverage costs 75\u201393% of events going to a human; "
             "holding burden under 50% drops coverage to 0.54\u20130.73.\n"
             "Mechanism/design evidence only \u2014 no accuracy or effort-reduction claim "
             "(EXP-005: 0/24 validated expert labels).",
             fontsize=10, color=MUTED, ha="left")
    return save(fig, "01-dosage-tradeoff.png")


# ---------------------------------------------------------------- figure 2
def fig_observability_gap():
    """EXP-006/008: what a human could actually see, versus what happened."""
    fig, ax = plt.subplots(figsize=(11.2, 5.4))
    labels = ["Items a human could review\n(legacy post-hoc queue)",
              "Assessment lifecycle events\nthat actually occurred"]
    vals = [11, 481]
    bars = ax.barh(labels, vals, height=0.46, color=[MUTED, S1], zorder=3)
    for b in bars:
        b.set_capstyle("round")
    for b, v in zip(bars, vals):
        ax.text(v + 9, b.get_y() + b.get_height() / 2, f"{v:,}", va="center",
                fontsize=19, weight="bold", color=INK)
    style(ax, xlab="Count (four settings combined)",
          title="Most of the reasoning was never visible to a human",
          sub="EXP-006 \u00b7 event replay against the legacy review queue")
    ax.set_xlim(0, 560)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.55)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=12)
    fig.text(0.008, -0.10,
             "Alongside this, EXP-008 measured a guideline instability rate of 1.35 \u2014 33 reference "
             "guidelines per setting were revised and never seen by a human.\n"
             "Observability evidence only; these are heterogeneous lifecycle observations, not quality outcomes.",
             fontsize=10, color=MUTED, ha="left")
    return save(fig, "02-observability-gap.png")


# ---------------------------------------------------------------- figure 3
def fig_corpus():
    """Composition of the reviewed corpus, honestly labelled as not-exhaustive."""
    d = json.loads((REPO / "literature/verified-research-corpus-2026-08-12.json").read_text(encoding="utf-8"))
    from collections import Counter
    c = Counter(s.get("rq_tag") for s in d["sources"])
    order = [
        ("RQ1", "SQ1 \u00b7 selective intervention"),
        ("RQ2", "SQ2 \u00b7 governed knowledge reuse"),
        ("methodology", "Design-science methodology"),
        ("RQ3", "SQ3 \u00b7 evaluation & transfer"),
        ("foundation", "Variability / VEGO-AI foundation"),
        ("general", "General"),
    ]
    labels = [lbl for k, lbl in order]
    vals = [c.get(k, 0) for k, _ in order]
    cols = [SEQ[5], SEQ[4], SEQ[3], SEQ[2], SEQ[1], SEQ[0]]

    fig, ax = plt.subplots(figsize=(11.2, 5.8))
    bars = ax.barh(labels, vals, height=0.62, color=cols, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(v + 0.7, b.get_y() + b.get_height() / 2, str(v), va="center",
                fontsize=14, weight="bold", color=INK)
    # mark the thinnest question
    ax.annotate("thinnest coverage \u2014\nthe review must test whether\nthis is a gap or a search limit",
                xy=(vals[3] + 0.4, 3), xytext=(vals[0] * 0.52, 3.95),
                fontsize=10.5, color=CRITICAL, weight="bold", va="center",
                arrowprops=dict(arrowstyle="->", color=CRITICAL, lw=1.6,
                                connectionstyle="arc3,rad=-0.25"))
    style(ax, xlab="Verified sources",
          title=f"A {d['totalSources']}-source corpus, verified before it was used",
          sub=f"{d['verified']} confirmed against an independent online record \u00b7 "
              f"{d['partial']} partial \u00b7 {d['unverified']} unverifiable and quarantined")
    ax.set_xlim(0, max(vals) * 1.20)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.55)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=11.5)
    fig.text(0.008, -0.085,
             "Assembled by targeted per-question searching plus reference snowballing from the "
             "published VEGO-AI bibliography.\n"
             "The five frozen protocol queries (QL-01\u2013QL-05) have NOT yet been executed \u2014 this "
             "shows what has been found and read, never that nothing else exists.",
             fontsize=10, color=MUTED, ha="left")
    return save(fig, "03-corpus-composition.png")


# ---------------------------------------------------------------- figure 4
def fig_published_profile():
    """Where the published framework is strong, and where it asks for a human.

    Ranges are the published VEGO-AI (MODELS '26) figures, verified in
    docs/research/governance/vego-ai-foundation-paper-record.md.
    Spearman rho is deliberately NOT plotted on this axis - different measure,
    different scale - it is stated separately in the caption.
    """
    rows = [
        ("Language template agreement", 0.75, 1.00, S1, False),
        ("Compliance scoring vs expert review", 0.80, 0.96, S1, False),
        ("Reference-guideline alignment", 0.70, 0.88, S1, False),
        ("Uncovered-fragment audit", 0.55, 0.88, CRITICAL, True),
    ]
    fig, ax = plt.subplots(figsize=(11.2, 5.6))
    ys = list(range(len(rows)))[::-1]
    for y, (label, lo, hi, colr, weak) in zip(ys, rows):
        ax.plot([lo, hi], [y, y], color=colr, lw=7, solid_capstyle="round",
                alpha=0.30 if not weak else 0.38, zorder=3)
        ax.plot([lo, hi], [y, y], color=colr, lw=2.2, solid_capstyle="round", zorder=4)
        for x in (lo, hi):
            ax.plot([x], [y], "o", ms=11, color=colr, markeredgecolor=SURFACE,
                    markeredgewidth=2.5, zorder=5)
        ax.text(lo - 0.018, y, f"{lo:.2f}", ha="right", va="center", fontsize=12,
                color=colr, weight="bold")
        ax.text(hi + 0.018, y, f"{hi:.2f}", ha="left", va="center", fontsize=12,
                color=colr, weight="bold")
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows], fontsize=12.5)
    # Highlight the weak measure. get_yticklabels() follows the order the ticks
    # were set in, which is the same order as `rows` - match on the flag rather
    # than a hard-coded index so the two can never drift apart.
    for lbl, row in zip(ax.get_yticklabels(), rows):
        if row[4]:
            lbl.set_color(CRITICAL)
            lbl.set_weight("bold")

    ax.annotate("both use-case-diagram settings sit at 0.55 \u2014\n"
                "the paper's own reading: this \u201cmay require human involvement\u201d",
                xy=(0.556, 0.0), xytext=(0.66, 0.72),
                fontsize=11, color=CRITICAL, weight="bold", va="center",
                arrowprops=dict(arrowstyle="->", color=CRITICAL, lw=1.6,
                                connectionstyle="arc3,rad=0.28"))

    style(ax, xlab="Reported score range across the four evaluation settings",
          title="The published framework names its own need for human judgment",
          sub="VEGO-AI \u00b7 Reinhartz-Berger, Bragilovski & Sturm, MODELS \u201926 \u00b7 178 student models, 2 domains \u00d7 2 UML languages")
    ax.set_xlim(0.40, 1.10)
    ax.set_ylim(-0.9, 3.7)
    ax.grid(axis="x", alpha=0.55)
    ax.set_axisbelow(True)
    fig.text(0.008, -0.075,
             "Separately, and on a different scale so it is not plotted here: agreement between "
             "Model-Inspector scores and the human grader was weak, Spearman \u03c1 = 0.22 (p = 0.007).\n"
             "Reference values reported by the paper for its own education-domain setting \u2014 "
             "engineering context only, not a performance claim for this research.",
             fontsize=10, color=MUTED, ha="left")
    return save(fig, "04-published-profile.png")


# ---------------------------------------------------------------- figure 5
def fig_maturity_grid():
    """The analysis framework: where each research stream stops on each checkpoint.

    Levels are ordinal (L0..L4), so the ramp uses the ordinal-safe steps - nothing
    lighter than step 250 on a light surface. "absent" is a distinct category (the
    stream has no construct for that checkpoint at all), not a low level, so it
    gets a neutral treatment rather than a ramp step.
    """
    ORD = {0: "#86b6ef", 1: "#5598e7", 2: "#2a78d6", 3: "#1c5cab", 4: "#104281"}
    ABSENT = "#efe6e6"

    cols = ["TRIGGER\nwhat makes it\nstop and ask",
            "ASK\nhow the request\nis composed",
            "RECORD\nwhat survives the\nexpert's answer",
            "REUSE\nwhat licenses\napplying it again",
            "PROVE\nwhat evidence,\nobtained where"]
    rows = [
        ("A · Escalation triggering, oversight & burden", "~34", [3, 2, 1, 0, 2]),
        ("B · Judgment internalised in parameters (RLHF)", "7", [-1, 1, 1, 0, 1]),
        ("C · Externalised records: provenance, rationale", "~17", [-1, 3, 3, 2, 1]),
        ("D · Runtime agent memory & retrieval reuse", "~8", [0, -1, 2, 1, 1]),
        ("E · Model assessment & variability engineering", "~33", [1, 2, 1, 1, 1]),
        ("F · Transfer, shift & design-science validity", "~43", [-1, -1, -1, 2, 3]),
    ]

    fig, ax = plt.subplots(figsize=(12.6, 6.4))
    n_r, n_c = len(rows), len(cols)
    for i, (_, _, lv) in enumerate(rows):
        for j, v in enumerate(lv):
            y = n_r - 1 - i
            face = ABSENT if v < 0 else ORD[v]
            ax.add_patch(Rectangle((j + 0.045, y + 0.06), 0.91, 0.88,
                                   facecolor=face, edgecolor=SURFACE, lw=2.5, zorder=3))
            txt = "absent" if v < 0 else f"L{v}"
            ax.text(j + 0.5, y + 0.5, txt, ha="center", va="center", zorder=4,
                    fontsize=15 if v >= 0 else 11.5,
                    weight="bold",
                    color=CRITICAL if v < 0 else (SURFACE if v >= 2 else INK),
                    style="normal" if v >= 0 else "italic")

    # the empty top rung - the headline finding
    ax.add_patch(Rectangle((0.045, n_r + 0.14), n_c - 0.09, 0.62, facecolor="#fbf3f3",
                           edgecolor=CRITICAL, lw=1.6, ls=(0, (6, 4)), zorder=3))
    ax.text(n_c / 2, n_r + 0.45,
            "L4  —  not reached by any stream, on any checkpoint",
            ha="center", va="center", fontsize=13.5, weight="bold", color=CRITICAL, zorder=4)

    ax.set_xlim(0, n_c)
    ax.set_ylim(0, n_r + 0.90)
    ax.set_xticks([j + 0.5 for j in range(n_c)])
    ax.set_xticklabels(cols, fontsize=10.5, color=INK2, linespacing=1.5)
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")
    ax.set_yticks([n_r - 1 - i + 0.5 for i in range(n_r)])
    ax.set_yticklabels([f"{nm}    ({c})" for nm, c, _ in rows], fontsize=11, color=INK)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    # Column headers sit ON TOP of the axes, so title and subtitle are placed in
    # figure coordinates above a reserved top margin rather than with a title pad -
    # otherwise the subtitle lands on the headers.
    fig.subplots_adjust(top=0.74 if not BARE else 0.90, left=0.30, right=0.985, bottom=0.02)
    if not BARE:
        fig.text(0.008, 0.955, "The Judgment Lifecycle Grid — where each research stream stops",
                 fontsize=17, weight="bold", color=INK, ha="left", va="top")
        fig.text(0.008, 0.885,
                 "Rows: the six streams in the reviewed corpus (source counts in brackets).  "
                 "Columns: the five checkpoints one expert ruling must pass.",
                 fontsize=11.5, color=INK2, ha="left", va="top")

    fig.text(0.008, -0.055,
             "Reading down a column shows the ceiling for that checkpoint. "
             "REUSE never passes L2 — no stream applies a machine-checkable, per-record scope "
             "gate before a stored ruling is reused.\n"
             "“absent” means the stream has no construct for that checkpoint at all. "
             "Positions describe the reviewed corpus only; the frozen searches are not yet executed.",
             fontsize=10, color=MUTED, ha="left")
    return save(fig, "05-maturity-grid.png")


def build_all():
    fig_dosage_tradeoff()
    fig_observability_gap()
    fig_corpus()
    fig_published_profile()
    fig_maturity_grid()


if __name__ == "__main__":
    print("building figures ->", OUT)
    print(" standalone (titled):")
    build_all()
    print(" slide variants (untitled - the slide supplies the title):")
    BARE, SUFFIX = True, "-bare"
    build_all()
    print("done")
