"""Figure 4: the two failure modes concentrate in different settings; values recomputed here."""
from __future__ import annotations

import argparse
import collections
import json
import math
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, ORANGE = "#2a78d6", "#eb6834"
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8a86"
SETTINGS = ("ucd_ch", "ucd_pw", "cd_ch", "cd_pw")
NICE = {"ucd_ch": "Cheers\nuse case", "ucd_pw": "ParkWise\nuse case",
        "cd_ch": "Cheers\nclass", "cd_pw": "ParkWise\nclass"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5,
    "axes.edgecolor": "#d8d7d2", "axes.linewidth": 0.8, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})


def collect(root):
    import openpyxl
    out = {}
    for s in SETTINGS:
        wb = openpyxl.load_workbook(os.path.join(root, "System", "analysis", "scores_{}.xlsx".format(s)),
                                    read_only=True, data_only=True)
        rates = {}
        for ws in wb.worksheets:
            rows = list(ws.iter_rows(values_only=True))
            hdr = [str(h) for h in rows[0]]
            sc = next(i for i, h in enumerate(hdr) if h.lower().startswith("score"))
            judged = [r for r in rows[1:] if r[sc] in (0, 1)]
            rates[ws.title] = (sum(1 for r in judged if r[sc] == 1), len(judged))
        wb.close()
        diagram, domain = s.split("_")
        with open(os.path.join(root, "System", "inputs", domain,
                               "domain_base_{}.txt".format(diagram)), encoding="utf-8") as fh:
            base = [l.strip() for l in fh if l.strip() and not l.lstrip().startswith("#")]
        with open(os.path.join(root, "System", "eval_output", s, "agentB_metrics.json"), encoding="utf-8") as fh:
            metrics = json.load(fh)
        out[s] = {"compliance": rates["compliance_vectors"], "fragments": rates["uncovered_fragments"],
                  "unmatched": metrics["false_negatives"], "requirements": len(base)}
    return out


def figure4(out_dir, data):
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.5), gridspec_kw={"width_ratios": [1.15, 1.0], "wspace": 0.32})
    x = np.arange(len(SETTINGS))

    ax = axes[0]
    comp = [data[s]["compliance"][0] / data[s]["compliance"][1] * 100 for s in SETTINGS]
    frag = [data[s]["fragments"][0] / data[s]["fragments"][1] * 100 for s in SETTINGS]
    ax.bar(x - 0.19, comp, width=0.34, color=BLUE, edgecolor=SURFACE, linewidth=1.2, zorder=3,
           label="is the guideline met?")
    ax.bar(x + 0.19, frag, width=0.34, color=ORANGE, edgecolor=SURFACE, linewidth=1.2, zorder=3,
           label="alternative or mistake?")
    for xi, v in zip(x - 0.19, comp):
        ax.text(xi, v + 2, "{:.0f}".format(v), ha="center", fontsize=7.6, fontweight="bold", color=INK)
    for xi, v in zip(x + 0.19, frag):
        ax.text(xi, v + 2, "{:.0f}".format(v), ha="center", fontsize=7.6, fontweight="bold", color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels([NICE[s] for s in SETTINGS], fontsize=7.2)
    ax.set_ylabel("share of verdicts the human kept (%)", fontsize=7.8)
    ax.set_ylim(0, 118)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.legend(fontsize=6.8, frameon=False, loc="upper left", handlelength=1.0, ncol=1, borderpad=0.1)
    ax.set_title("(a) Verdicts the human kept",
                 fontsize=8.4, color=INK, fontweight="bold", loc="left", pad=5)

    ax = axes[1]
    unm = [data[s]["unmatched"] / data[s]["requirements"] * 100 for s in SETTINGS]
    ax.bar(x, unm, width=0.55, color=BLUE, edgecolor=SURFACE, linewidth=1.2, zorder=3)
    for xi, v, s in zip(x, unm, SETTINGS):
        ax.text(xi, v + 2, "{}/{}".format(data[s]["unmatched"], data[s]["requirements"]),
                ha="center", fontsize=7.4, fontweight="bold", color=INK)
    ax.set_xticks(x)
    ax.set_xticklabels([NICE[s] for s in SETTINGS], fontsize=7.2)
    ax.set_ylabel("expert requirements with no\nagent guideline (%)", fontsize=7.8)
    ax.set_ylim(0, 105)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_title("(b) Expert requirements missed",
                 fontsize=8.4, color=INK, fontweight="bold", loc="left", pad=5)

    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#eceae5", linewidth=0.7, zorder=0)
        ax.set_axisbelow(True)
    fig.savefig(os.path.join(out_dir, "figure4_settings.png"), dpi=220, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    data = collect(args.dataset_root)
    figure4(args.out, data)
    for s in SETTINGS:
        d = data[s]
        print(s, "compliance {}/{}".format(*d["compliance"]), "fragments {}/{}".format(*d["fragments"]),
              "unmatched {}/{}".format(d["unmatched"], d["requirements"]))
    print("wrote figure4_settings.png")
