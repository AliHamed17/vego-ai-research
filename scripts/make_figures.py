"""Figures for the VEGO-AI human-involvement paper; every value recomputed by figdata."""
from __future__ import annotations

import argparse
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import figdata

BLUE, ORANGE, VIOLET = "#2a78d6", "#eb6834", "#4a3aa7"
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8a86"
NL = chr(10)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5,
    "axes.edgecolor": "#d8d7d2", "axes.linewidth": 0.8, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})

STAGES = [
    ("Agent 1" + NL + "language advisor", "writes the modelling-" + NL + "language guidelines"),
    ("Agent 2" + NL + "domain advisor", "writes the domain" + NL + "guidelines for the case"),
    ("Agent 3" + NL + "model inspector", "judges each guideline" + NL + "against each model"),
    ("Agent 4" + NL + "variability explorer", "classifies the recurring" + NL + "deviation patterns"),
]


def box(ax, x, y, w, h, label, sub, edge=BLUE, face="#eef4fc", lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.010,rounding_size=0.02",
                                linewidth=lw, edgecolor=edge, facecolor=face))
    ax.text(x + w / 2, y + h * 0.72, label, ha="center", va="center", fontsize=7.4,
            color=INK, fontweight="bold", linespacing=1.3)
    ax.text(x + w / 2, y + h * 0.24, sub, ha="center", va="center", fontsize=6.9,
            color=INK2, linespacing=1.3)


def arrow(ax, x1, y1, x2, y2, color=MUTED, lw=1.1, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=10,
                                 linewidth=lw, color=color, linestyle=ls, shrinkA=1, shrinkB=1))


def blank(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")


def figure1(out, s3, s2):
    fig, ax = plt.subplots(figsize=(6.9, 2.45))
    blank(ax)
    w, h, y = 0.215, 0.36, 0.50
    for i, (name, does) in enumerate(STAGES):
        x = 0.012 + i * 0.249
        box(ax, x, y, w, h, name, does)
        if i < 3:
            arrow(ax, x + w, y + h / 2, x + w + 0.030, y + h / 2)
    silent = [
        "{} of {} guidelines{}rejected on review, plus{}{} required ones missing".format(
            s2["rejected"], s2["reviewed"], NL, NL, s2["absent"]),
        "{} of {} judgments{}overturned on review".format(s3["overturned"], s3["reviewed"], NL),
    ]
    for i, txt in enumerate(silent):
        x = 0.012 + (1 + i) * 0.249 + w / 2
        arrow(ax, x, y, x, y - 0.09, color=ORANGE, lw=1.1, ls=(0, (3, 2)))
        ax.text(x, y - 0.215, txt, ha="center", va="center", fontsize=7.0, color=ORANGE, linespacing=1.35)
        ax.text(x, y - 0.40, "the run asked no one", ha="center", va="center", fontsize=7.2, color=INK2)
    x4 = 0.012 + 3 * 0.249 + w / 2
    arrow(ax, x4, y, x4, y - 0.09, color=VIOLET, lw=1.4)
    ax.text(x4, y - 0.185, "review queue:" + NL + "11 of 27 patterns", ha="center", va="center",
            fontsize=7.4, color=VIOLET, fontweight="bold", linespacing=1.35)
    ax.text(x4, y - 0.40, "the only point it asks", ha="center", va="center", fontsize=7.2, color=INK2)
    fig.savefig(os.path.join(out, "figure1_pipeline.png"), dpi=220, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def figure2(out, verdicts, by_support, certainty):
    fig, axes = plt.subplots(1, 3, figsize=(6.9, 2.45),
                             gridspec_kw={"width_ratios": [1.0, 0.8, 1.0], "wspace": 0.5})

    ax = axes[0]
    order = ["Satisfied", "Partially-Satisfied", "Not-Satisfied"]
    vals = [verdicts[v]["rate"] * 100 for v in order]
    bars = ax.bar(range(3), vals, width=0.6, color=BLUE, edgecolor=SURFACE, linewidth=1.2, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.8, "{:.0f}%".format(v), ha="center",
                fontsize=8.6, fontweight="bold", color=INK)
    ax.set_xticks(range(3))
    ax.set_xticklabels(["Satisfied" + NL + "n={}".format(verdicts["Satisfied"]["n"]),
                        "Partially-" + NL + "Satisfied" + NL + "n={}".format(verdicts["Partially-Satisfied"]["n"]),
                        "Not-" + NL + "Satisfied" + NL + "n={}".format(verdicts["Not-Satisfied"]["n"])],
                       fontsize=7.3)
    ax.set_ylabel("share the human overturned", fontsize=7.9)
    ax.set_ylim(0, 58)
    ax.set_title("(a) Stage 3 verdict", fontsize=8.4, color=INK, fontweight="bold", loc="left", pad=5)

    ax = axes[1]
    ks = sorted(by_support)
    vals = [by_support[k]["rate"] * 100 for k in ks]
    bars = ax.bar(range(len(ks)), vals, width=0.6, color=BLUE, edgecolor=SURFACE, linewidth=1.2, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.8, "{:.0f}%".format(v), ha="center",
                fontsize=8.6, fontweight="bold", color=INK)
    ax.set_xticks(range(len(ks)))
    ax.set_xticklabels(["{} of 3".format(k) + NL + "n={}".format(by_support[k]["n"]) for k in ks], fontsize=7.3)
    ax.set_ylabel("share the human rejected", fontsize=7.9)
    ax.set_ylim(0, 58)
    ax.set_title("(b) Stage 2 run agreement", fontsize=8.4, color=INK, fontweight="bold", loc="left", pad=5)

    ax = axes[2]
    bins = np.array([0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.05])
    for i, (lab, color) in enumerate(zip(["accepted in full", "not accepted in full"], [BLUE, ORANGE])):
        xs = certainty[lab]
        counts, _ = np.histogram(xs, bins=bins)
        ax.bar(bins[:-1] + 0.05 + (i - 0.5) * 0.042, counts / counts.sum() * 100, width=0.040,
               color=color, edgecolor=SURFACE, linewidth=1.0, zorder=3,
               label="{} (n={})".format(lab, len(xs)))
    ax.set_xlabel("certainty the agent stated", fontsize=7.6)
    ax.set_ylabel("share of guidelines", fontsize=7.9)
    ax.set_xticks([0.5, 0.7, 0.9])
    ax.set_xticklabels(["0.5", "0.7", "0.9"], fontsize=7.3)
    ax.set_ylim(0, 62)
    ax.legend(fontsize=6.6, frameon=False, loc="upper left", handlelength=1.0, borderpad=0.1)
    ax.set_title("(c) Stage 2 stated certainty", fontsize=8.4, color=INK, fontweight="bold", loc="left", pad=5)

    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#eceae5", linewidth=0.7, zorder=0)
        ax.set_axisbelow(True)
    fig.savefig(os.path.join(out, "figure2_signals.png"), dpi=220, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def figure3(out, rule):
    fig, ax = plt.subplots(figsize=(6.9, 2.55))
    blank(ax)
    w, h, y = 0.215, 0.34, 0.58
    marks = [
        None,
        ("H1  review every" + NL + "guideline once",
         "119 guidelines govern" + NL + "4,853 later judgments", VIOLET),
        ("H2  ask when a verdict" + NL + "is not Satisfied",
         "{:.0%} of items reach".format(rule["share_flagged"]) + NL
         + "a person, covering {:.0%}".format(rule["share_of_overturns_covered"]) + NL
         + "of the changes", VIOLET),
        ("H3  keep the" + NL + "existing queue", "11 of 27 patterns", MUTED),
    ]
    for i, (name, does) in enumerate(STAGES):
        x = 0.012 + i * 0.249
        m = marks[i]
        box(ax, x, y, w, h, name, does, edge=BLUE if m is None else VIOLET,
            face="#eef4fc" if m is None else "#f1effa", lw=1.2 if m is None else 1.7)
        if i < 3:
            arrow(ax, x + w, y + h / 2, x + w + 0.030, y + h / 2)
        if m:
            arrow(ax, x + w / 2, y, x + w / 2, y - 0.08, color=m[2], lw=1.4)
            ax.text(x + w / 2, y - 0.19, m[0], ha="center", va="center", fontsize=7.3,
                    color=m[2], fontweight="bold", linespacing=1.35)
            ax.text(x + w / 2, y - 0.41, m[1], ha="center", va="center", fontsize=7.0,
                    color=INK2, linespacing=1.35)
    fig.savefig(os.path.join(out, "figure3_decision.png"), dpi=220, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    verdicts = figdata.stage3_overturn_by_verdict(args.dataset_root)
    by_support, certainty = figdata.stage2_by_run_support_and_certainty(args.dataset_root)
    agent_written = {k: v for k, v in by_support.items() if k > 0}
    s3 = {"reviewed": sum(v["n"] for v in verdicts.values()),
          "overturned": sum(v["overturned"] for v in verdicts.values())}
    s2 = {"reviewed": sum(v["n"] for v in agent_written.values()),
          "rejected": sum(v["rejected"] for v in agent_written.values()),
          "absent": by_support.get(0, {"n": 0})["n"]}
    flagged = sum(v["n"] for k, v in verdicts.items() if k != "Satisfied")
    caught = sum(v["overturned"] for k, v in verdicts.items() if k != "Satisfied")
    rule = {"share_flagged": flagged / s3["reviewed"], "share_of_overturns_covered": caught / s3["overturned"]}
    figure1(args.out, s3, s2)
    figure2(args.out, verdicts, agent_written, certainty)
    figure3(args.out, rule)
    print("stage3", s3, "| stage2", s2, "| rule", {k: round(v, 3) for k, v in rule.items()},
          "| flagged", flagged, "caught", caught)
    print("wrote 3 figures to", args.out)


if __name__ == "__main__":
    main()
