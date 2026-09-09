"""Print figures for the Study 1C package: rule sensitivity, baselines, escalation mechanisms.

Three figures, each repaired against a specific way the earlier versions misled a reader:

  * the baseline chart compared **three-class** labels but was captioned as if it compared the
    review decision. Those are different questions with different answers: a rule that emits
    STRONG for every episode differs from Detector-v1 whenever Detector-v1 emits any WEAK, yet is
    *identical* to it whenever Detector-v1 sends every episode for review. It is now two panels
    that name their level, and neither may be read as the other;
  * the operating-characteristic chart looked like a measured accuracy curve. It is an analytic
    property of the rule under an independence assumption the data does not verify, and it now
    says so in its own title;
  * the escalation-mechanisms chart implied that a Detector-v1-silent case was a case with
    nothing wrong. Silence is not a safety finding, and the other mechanism's labels are not
    ground truth for the detector.

Design constraints: one axis per panel, never two scales; colour assigned by meaning and fixed
across panels; direct labels where a legend would force a lookup; recessive grid and axes.

No provider is contacted. Every input is a JSON report produced by the offline instruments.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

INK = "#1b1b1f"
MUTED = "#6b6b76"
GRID = "#dcdce4"
ACCENT = "#0f6fc4"
WARM = "#c2410c"
TEAL = "#0f766e"
SEQUENTIAL = ("#cfe3f5", "#9dc7ec", "#5aa3dc", "#2a7fc4", "#0f5a92")

IDENTICAL_COLOUR = WARM
DIFFERS_COLOUR = ACCENT
IDENTICAL_LABEL = "identical to Detector-v1 at this level"
DIFFERS_LABEL = "differs from Detector-v1 at this level"

plt.rcParams.update(
    {
        "font.size": 8.5,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 200,
        "savefig.bbox": "tight",
    }
)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def pretty(name: str) -> str:
    return name.replace("SINGLE_", "").replace("_", " ").lower()


def figure_operating_characteristic(report: dict[str, Any], out: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.9, 3.7))
    grid = sorted(report["analytic_grid"], key=lambda row: row["low_rate"])
    for shade, row in zip(SEQUENTIAL, grid):
        rate = row["low_rate"]
        lengths = sorted(int(k) for k in row["p_strong_by_length"])
        values = [row["p_strong_by_length"][str(k)] for k in lengths]
        note = "  (rate seen in the accepted run)" if abs(rate - 0.364) < 1e-9 else ""
        ax.plot(lengths, values, color=shade, linewidth=2.4 if note else 2,
                solid_capstyle="round", label=f"assumed p(Low per answer) = {rate:g}{note}")

    rug_colours = (WARM, "#7a3fb5", TEAL)
    for index, run in enumerate(report["runs"]):
        base = 1.02 + index * 0.045
        colour = rug_colours[index % len(rug_colours)]
        for row in run["observed_episodes"]:
            ax.plot([row["answer_count"], row["answer_count"]], [base, base + 0.035],
                    color=colour, linewidth=1.7, solid_capstyle="butt")
        ax.plot([], [], color=colour, linewidth=1.7,
                label=f"observed answer counts: {run['run_label']}")

    ax.axhline(0.95, color=MUTED, linewidth=0.8, linestyle=(0, (4, 3)))
    ax.annotate("0.95", (1.05, 0.965), fontsize=7, color=MUTED)
    ax.set_xscale("log")
    ax.set_xlabel("answers in the episode  (answer count, NOT Q&A rounds)")
    ax.set_ylabel("P(STRONG_ALERT) under the stated assumption")
    ax.set_ylim(0, 1.02 + 0.045 * max(1, len(report["runs"])) + 0.05)
    ax.set_xticks([1, 2, 5, 10, 20, 50])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    handles, texts = ax.get_legend_handles_labels()
    curves = len(grid)
    order = list(reversed(range(curves))) + list(range(curves, len(handles)))
    ax.legend([handles[i] for i in order], [texts[i] for i in order], frameon=False,
              fontsize=6.6, loc="lower right", handlelength=1.6, labelspacing=0.3)
    ax.set_title(
        "ANALYTIC RULE-SENSITIVITY, NOT EMPIRICAL ACCURACY\n"
        "P(any answer is Low) = 1-(1-p)^k, assuming answers are independent within an episode.\n"
        "The data does not verify that assumption. This is not a real-world or causal probability.",
        fontsize=8, loc="left", color=INK, pad=8,
    )
    fig.savefig(out)
    plt.close(fig)


def _baseline_panel(ax, rows, values, identical, reference, xlabel, title) -> None:
    positions = range(len(rows))
    ax.barh(list(positions), values, height=0.62,
            color=[IDENTICAL_COLOUR if same else DIFFERS_COLOUR for same in identical],
            edgecolor="white", linewidth=1.2)
    ax.axvline(reference, color=INK, linewidth=1.1, linestyle=(0, (3, 2)))
    ax.annotate(f"Detector-v1 = {reference:g}", (reference, len(rows) - 0.35),
                textcoords="offset points", xytext=(-4, 0), fontsize=7,
                color=INK, ha="right", va="center")
    ax.set_yticks(list(positions))
    ax.set_yticklabels([pretty(name) for name in rows], fontsize=6.6)
    ax.set_xlabel(xlabel, fontsize=7.5)
    ax.set_xlim(0, 1.08)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_title(title, fontsize=8, loc="left", color=INK, pad=6)


def figure_baselines(report: dict[str, Any], out: Path, run_index: int = 0) -> None:
    run = report["runs"][run_index]
    baselines = {
        name: row for name, row in run["baselines"].items() if not name.startswith("V1_WITHOUT_")
    }
    order = sorted(baselines, key=lambda name: baselines[name]["exact_three_class_agreement"] or 0)
    three = [baselines[name]["exact_three_class_agreement"] or 0 for name in order]
    binary = [baselines[name]["binary_review_agreement"] or 0 for name in order]
    identical_three = [baselines[name]["identical_three_class"] for name in order]
    identical_binary = [baselines[name]["identical_binary_review"] for name in order]

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 0.23 * len(order) + 2.0), sharey=True)
    _baseline_panel(
        axes[0], order, three, identical_three, 1.0,
        "exact three-class agreement with Detector-v1",
        "(a) THREE-CLASS level: STRONG / WEAK / NO_ALERT\n"
        f"{sum(identical_three)} of {len(order)} baselines identical",
    )
    _baseline_panel(
        axes[1], order, binary, identical_binary, 1.0,
        "binary review-selection agreement with Detector-v1",
        "(b) BINARY REVIEW level: sent for review, or not\n"
        f"{sum(identical_binary)} of {len(order)} baselines identical",
    )
    axes[1].tick_params(labelleft=False)
    handles = [
        plt.Line2D([], [], color=IDENTICAL_COLOUR, linewidth=6, label=IDENTICAL_LABEL),
        plt.Line2D([], [], color=DIFFERS_COLOUR, linewidth=6, label=DIFFERS_LABEL),
    ]
    fig.legend(handles=handles, frameon=False, fontsize=7.2, loc="lower center",
               ncol=2, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(
        f"Baselines against the frozen rule - {run['run_label']}, denominator "
        f"{run['denominator_complete_episodes']} complete episodes.  "
        "Selection agreement only; no ground truth exists, so no accuracy is shown.\n"
        "The two panels answer different questions and must not be quoted as one number.",
        fontsize=8.4, x=0.01, ha="left", y=1.02,
    )
    fig.savefig(out)
    plt.close(fig)


def figure_mechanisms(report: dict[str, Any], out: Path, run_index: int = 0) -> None:
    run = report["runs"][run_index]
    rows = [row for row in run["per_case"] if row.get("fragment_stage")]
    cases = [row["case_id"] for row in rows]
    mistakes = [row["fragment_stage"]["domain_mistakes"] for row in rows]
    flagged = [row["detector_v1_flags_case"] for row in rows]

    fig, ax = plt.subplots(figsize=(6.2, min(3.6, 0.2 * len(rows) + 1.9)))
    ax.bar(cases, mistakes, width=0.62,
           color=[WARM if flag else ACCENT for flag in flagged],
           edgecolor="white", linewidth=1.2)
    ax.set_xlabel("case")
    ax.set_ylabel("fragments labelled Domain Mistake\n(coverage stage, per fragment)", fontsize=7.5)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    if len(cases) > 12:
        ax.tick_params(axis="x", labelsize=6, rotation=90)
    cross = run["case_level_crosstab"]
    handles = [
        plt.Line2D([], [], color=WARM, linewidth=6,
                   label="Detector-v1 also selected this case for review"),
        plt.Line2D([], [], color=ACCENT, linewidth=6,
                   label="Detector-v1 silent - NOT a finding that the case is safe"),
    ]
    ax.set_ylim(0, max(mistakes + [1]) * 1.42)
    ax.legend(handles=handles, frameon=False, fontsize=6.8, loc="upper right")
    ax.set_title(
        "TWO MECHANISMS, DIFFERENT UNITS OF ANALYSIS - NEITHER IS GROUND TRUTH\n"
        "Detector-v1 judges Q&A episodes from conversation state; the coverage stage judges "
        "individual fragments.\n"
        "Domain-Mistake labels are that stage's own output, not truth labels for Detector-v1. "
        "Co-occurrence only.\n"
        f"both {cross['detector_flags_and_fragment_stage_flags']} - "
        f"detector only {cross['detector_flags_only']} - "
        f"fragment stage only {cross['fragment_stage_flags_only']} - "
        f"neither {cross['neither_flags']}",
        fontsize=7.6, loc="left", color=INK, pad=8,
    )
    fig.savefig(out)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--characteristic", type=Path, required=True)
    parser.add_argument("--baselines", type=Path, required=True)
    parser.add_argument("--mechanisms", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--run-index", type=int, default=0)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    figure_operating_characteristic(load(args.characteristic),
                                    args.out_dir / "study1c-operating-characteristic.png")
    figure_baselines(load(args.baselines), args.out_dir / "study1c-baselines.png", args.run_index)
    figure_mechanisms(load(args.mechanisms), args.out_dir / "study1c-escalation-mechanisms.png",
                      args.run_index)
    print(json.dumps({"figures": sorted(str(p) for p in args.out_dir.glob("study1c-*.png"))},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
