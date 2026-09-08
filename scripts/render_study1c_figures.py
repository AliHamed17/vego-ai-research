"""Print figures for the Study 1C package: operating characteristic, baselines, mechanisms.

Three static figures sized for a print thesis chapter. Each carries its own denominator and
evidence class in the caption area, because a figure separated from its document must still be
readable without inviting a claim the data does not support.

Design constraints followed: one axis per panel and never two scales; a colour-blind-safe
categorical order assigned by entity and never by rank; sequential shading for the one ordered
family; direct labels where a legend would force a lookup; recessive grid and axes.

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
SEQUENTIAL = ("#cfe3f5", "#9dc7ec", "#5aa3dc", "#2a7fc4", "#0f5a92")

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


def figure_operating_characteristic(report: dict[str, Any], out: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    grid = sorted(report["analytic_grid"], key=lambda row: row["low_rate"])
    for shade, row in zip(SEQUENTIAL, grid):
        rate = row["low_rate"]
        lengths = sorted(int(k) for k in row["p_strong_by_length"])
        values = [row["p_strong_by_length"][str(k)] for k in lengths]
        note = "  (observed)" if abs(rate - 0.364) < 1e-9 else ""
        ax.plot(
            lengths,
            values,
            color=shade,
            linewidth=2.4 if note else 2,
            solid_capstyle="round",
            label=f"p(Low) = {rate:g}{note}",
        )

    observed = report["runs"][0]["observed_episodes"]
    for row in observed:
        ax.plot(
            [row["answer_count"], row["answer_count"]],
            [1.05, 1.10],
            color=WARM,
            linewidth=1.6,
            solid_capstyle="butt",
        )
    ax.plot([], [], color=WARM, linewidth=1.6, label="observed episode lengths")
    ax.axhline(0.95, color=MUTED, linewidth=0.8, linestyle=(0, (4, 3)))
    ax.annotate("0.95", (1.05, 0.965), fontsize=7, color=MUTED)

    ax.set_xscale("log")
    ax.set_xlabel("answers in the episode")
    ax.set_ylabel("P(STRONG_ALERT)")
    ax.set_ylim(0, 1.14)
    ax.set_xticks([1, 2, 5, 10, 20, 50])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    handles, texts = ax.get_legend_handles_labels()
    order = list(reversed(range(len(handles) - 1))) + [len(handles) - 1]
    ax.legend(
        [handles[i] for i in order],
        [texts[i] for i in order],
        frameon=False,
        fontsize=7,
        loc="lower right",
        handlelength=1.6,
        labelspacing=0.35,
    )
    ax.set_title(
        "Detector-v1 fires more readily on longer episodes\n"
        "analytic property of the rule; not an empirical result",
        fontsize=9,
        loc="left",
        color=INK,
        pad=8,
    )
    fig.savefig(out)
    plt.close(fig)


def figure_baselines(report: dict[str, Any], out: Path, run_index: int = 0) -> None:
    run = report["runs"][run_index]
    reference = run["detector_v1_review_load"] if "detector_v1_review_load" in run else run[
        "detector_v1_flag_rate"
    ]
    interesting = [
        name
        for name in run["baselines"]
        if not name.startswith("V1_WITHOUT_") and not name.startswith("ANY_EVIDENCE_SHORTER")
    ]
    rows = sorted(
        ((name, run["baselines"][name]) for name in interesting),
        key=lambda kv: kv[1]["flag_rate"] or 0,
    )
    labels = [name.replace("SINGLE_", "").replace("_", " ").lower() for name, _ in rows]
    values = [row["flag_rate"] or 0 for _, row in rows]
    identical = [row["identical_to_detector_v1"] for _, row in rows]

    fig, ax = plt.subplots(figsize=(5.4, 0.24 * len(rows) + 1.4))
    positions = range(len(rows))
    ax.barh(
        list(positions),
        values,
        height=0.62,
        color=[WARM if same else ACCENT for same in identical],
        edgecolor="white",
        linewidth=1.2,
    )
    ax.axvline(reference, color=INK, linewidth=1.1, linestyle=(0, (3, 2)))
    ax.annotate(
        f"Detector-v1 = {reference:g}",
        (reference, len(rows) - 0.35),
        textcoords="offset points",
        xytext=(-4, 0),
        fontsize=7,
        color=INK,
        ha="right",
        va="center",
    )
    ax.set_yticks(list(positions))
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel("share of complete episodes flagged (review load)")
    ax.set_xlim(0, 1.08)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    handles = [
        plt.Line2D([], [], color=WARM, linewidth=6, label="identical to Detector-v1"),
        plt.Line2D([], [], color=ACCENT, linewidth=6, label="differs from Detector-v1"),
    ]
    ax.legend(handles=handles, frameon=False, fontsize=7, loc="lower left")
    ax.set_title(
        f"Baselines against the frozen rule — {run['run_label']}, "
        f"denominator {run['denominator_complete_episodes']} episodes\n"
        "selection agreement only; no ground truth exists, so no accuracy is shown",
        fontsize=9,
        loc="left",
        color=INK,
        pad=8,
    )
    fig.savefig(out)
    plt.close(fig)


def figure_mechanisms(report: dict[str, Any], out: Path, run_index: int = 0) -> None:
    run = report["runs"][run_index]
    rows = [row for row in run["per_case"] if row.get("fragment_stage")]
    cases = [row["case_id"] for row in rows]
    mistakes = [row["fragment_stage"]["domain_mistakes"] for row in rows]
    flagged = [row["detector_v1_flags_case"] for row in rows]

    fig, ax = plt.subplots(figsize=(5.4, min(3.3, 0.2 * len(rows) + 1.6)))
    ax.bar(
        cases,
        mistakes,
        width=0.62,
        color=[WARM if flag else ACCENT for flag in flagged],
        edgecolor="white",
        linewidth=1.2,
    )
    ax.set_xlabel("case")
    ax.set_ylabel("fragments labelled Domain Mistake")
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    if len(cases) > 12:
        ax.tick_params(axis="x", labelsize=6, rotation=90)
    handles = [
        plt.Line2D([], [], color=WARM, linewidth=6, label="Detector-v1 also flags this case"),
        plt.Line2D([], [], color=ACCENT, linewidth=6, label="Detector-v1 silent on this case"),
    ]
    ax.legend(handles=handles, frameon=False, fontsize=7, loc="upper right")
    ax.set_title(
        f"Two escalation mechanisms disagree — {run['run_label']}\n"
        "different units of analysis; neither is ground truth",
        fontsize=9,
        loc="left",
        color=INK,
        pad=8,
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
    written = []
    for name, builder, source in (
        ("study1c-operating-characteristic.png", figure_operating_characteristic, args.characteristic),
        ("study1c-baselines.png", figure_baselines, args.baselines),
        ("study1c-escalation-mechanisms.png", figure_mechanisms, args.mechanisms),
    ):
        target = args.out_dir / name
        if builder is figure_operating_characteristic:
            builder(load(source), target)
        else:
            builder(load(source), target, args.run_index)
        written.append(str(target))
    print(json.dumps({"figures": written}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
