"""Landing-page figures for a reader who knows nothing about this project.

Every chart here answers one question in one picture, with as few words as the picture allows.
Technical vocabulary is avoided inside the images: a reader meets "conversation" rather than
"episode", "flagged high" rather than `STRONG_ALERT`, and the exact terms appear once in the
glossary beside the figure instead of being scattered through axis labels.

Both languages are generated from the same data and the same code. Hebrew strings are reordered
with the bidi algorithm before matplotlib sees them, because matplotlib draws glyphs left to right
and would otherwise reverse every Hebrew label.

Colour carries one meaning throughout all four figures and never changes between them: warm is
"flagged high", blue is "flagged low", grey is "not verified" or "silent".

No provider is contacted. Inputs are the JSON reports produced by the offline instruments.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from bidi.algorithm import get_display  # noqa: E402

INK = "#14375e"
MUTED = "#6b6b76"
GRID = "#e3e3ea"
STRONG_C = "#c2410c"
WEAK_C = "#2a78d6"
GREY_C = "#b4b4bc"
GREEN_C = "#3c965a"

LABELS = {
    "en": {
        "font": "Segoe UI",
        "runs_title": "What we ran, and what came out",
        "runs_x": "conversations recorded",
        "flagged_high": "flagged HIGH",
        "flagged_low": "flagged LOW",
        "not_verified": "not verified",
        "length_title": "The main finding: conversation length decides the flag",
        "length_x": "answers in the conversation",
        "short_note": "short conversations\nboth flags appear",
        "long_note": "long conversations\nalways flagged HIGH",
        "base_title": "Do simple rules do the same thing?",
        "base_left": "(a) comparing the exact label",
        "base_right": "(b) comparing only send-to-human or not",
        "base_x": "agreement with our rule",
        "same": "identical to our rule",
        "differs": "different from our rule",
        "mech_title": "Two different checkers, two different answers",
        "mech_x": "case",
        "mech_y": "problems found by the other checker",
        "mech_spoke": "our rule also flagged this case",
        "mech_silent": "our rule said nothing (NOT proof it is fine)",
        "always": "always flag everything",
    },
    "he": {
        "font": "Segoe UI",
        "runs_title": "מה הרצנו, ומה יצא",
        "runs_x": "שיחות שנרשמו",
        "flagged_high": "סומן גבוה",
        "flagged_low": "סומן נמוך",
        "not_verified": "לא אומת",
        "length_title": "הממצא המרכזי: אורך השיחה קובע את הסימון",
        "length_x": "מספר תשובות בשיחה",
        "short_note": "שיחות קצרות\nשני הסימונים מופיעים",
        "long_note": "שיחות ארוכות\nתמיד מסומן גבוה",
        "base_title": "האם כללים פשוטים עושים אותו דבר?",
        "base_left": "(א) השוואת התווית המדויקת",
        "base_right": "(ב) השוואת שליחה לאדם בלבד",
        "base_x": "הסכמה עם הכלל שלנו",
        "same": "זהה לכלל שלנו",
        "differs": "שונה מהכלל שלנו",
        "mech_title": "שני בודקים שונים, שתי תשובות שונות",
        "mech_x": "מקרה",
        "mech_y": "בעיות שמצא הבודק האחר",
        "mech_spoke": "הכלל שלנו סימן גם את המקרה",
        "mech_silent": "הכלל שלנו שתק (אינו הוכחה שתקין)",
        "always": "תמיד לסמן הכול",
    },
}

RUN_NAMES = {
    "en": {
        "ACCEPTED_RUN_N4": "Run 0  (4 cases)",
        "FULL_FRAME_N21_RUN1": "Run 1  (21 cases)",
        "FULL_FRAME_N21_RUN2": "Run 2  (21 cases)",
        "HOTSPOT": "Pilot  (not verified)",
    },
    "he": {
        "ACCEPTED_RUN_N4": "הרצה 0  (4 מקרים)",
        "FULL_FRAME_N21_RUN1": "הרצה 1  (21 מקרים)",
        "FULL_FRAME_N21_RUN2": "הרצה 2  (21 מקרים)",
        "HOTSPOT": "פיילוט  (לא אומת)",
    },
}


BASELINE_NAMES = {
    "en": {
        "ALWAYS_ALERT": "always flag everything",
        "ANY_NON_HIGH_CONFIDENCE": "any answer not fully sure",
        "ANY_QUESTION_ASKED": "any question was asked",
        "SINGLE_S1_LOW_ANSWER_CONFIDENCE": "any answer marked low",
        "SINGLE_S2_MEDIUM_ANSWER_CONFIDENCE": "any answer marked medium",
        "SINGLE_S6_MULTIPLE_QA_ROUNDS": "more than one round",
        "ANY_EVIDENCE_SHORTER_THAN_100": "short evidence (under 100)",
        "ANY_EVIDENCE_SHORTER_THAN_200": "short evidence (under 200)",
        "ROUNDS_GT_1": "more than one round",
        "MAJORITY_LOW_CONFIDENCE": "most answers marked low",
    },
    "he": {
        "ALWAYS_ALERT": "תמיד לסמן הכול",
        "ANY_NON_HIGH_CONFIDENCE": "תשובה שאינה בטוחה לגמרי",
        "ANY_QUESTION_ASKED": "נשאלה שאלה כלשהי",
        "SINGLE_S1_LOW_ANSWER_CONFIDENCE": "תשובה בביטחון נמוך",
        "SINGLE_S2_MEDIUM_ANSWER_CONFIDENCE": "תשובה בביטחון בינוני",
        "SINGLE_S6_MULTIPLE_QA_ROUNDS": "יותר מסבב אחד",
        "ANY_EVIDENCE_SHORTER_THAN_100": "ראיה קצרה מ-100",
        "ANY_EVIDENCE_SHORTER_THAN_200": "ראיה קצרה מ-200",
        "ROUNDS_GT_1": "יותר מסבב אחד",
        "MAJORITY_LOW_CONFIDENCE": "רוב התשובות בביטחון נמוך",
    },
}


def shape(text: str, lang: str) -> str:
    return get_display(text) if lang == "he" else text


def setup(lang: str) -> None:
    plt.rcParams.update(
        {
            "font.family": LABELS[lang]["font"],
            "font.size": 10,
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


def figure_runs(recon: dict[str, Any], lang: str, out: Path) -> None:
    L, names = LABELS[lang], RUN_NAMES[lang]
    order = ["REAL-efe686a-20260905T2303Z", "FULLFRAME-01", "FULLFRAME-02", "HOTSPOT-01"]
    keys = {
        "REAL-efe686a-20260905T2303Z": "ACCEPTED_RUN_N4",
        "FULLFRAME-01": "FULL_FRAME_N21_RUN1",
        "FULLFRAME-02": "FULL_FRAME_N21_RUN2",
        "HOTSPOT-01": "HOTSPOT",
    }
    rows = {r["run_id"]: r for r in recon["runs"]}
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    for index, run_id in enumerate(reversed(order)):
        row = rows[run_id]
        y = index
        if row["execution_status"] != "EXECUTED":
            ax.barh(y, 11, color=GREY_C, height=0.6, alpha=0.45)
            ax.text(5.5, y, shape(L["not_verified"], lang), ha="center", va="center",
                    fontsize=9, color="#55555c", fontweight="bold")
            continue
        strong = row["detector_class_STRONG_ALERT"]
        weak = row["detector_class_WEAK_ALERT"]
        ax.barh(y, strong, color=STRONG_C, height=0.6)
        if weak:
            ax.barh(y, weak, left=strong, color=WEAK_C, height=0.6)
        ax.text(strong / 2, y, str(strong), ha="center", va="center",
                color="white", fontsize=10, fontweight="bold")
        if weak:
            ax.text(strong + weak / 2, y, str(weak), ha="center", va="center",
                    color="white", fontsize=10, fontweight="bold")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([shape(names[keys[r]], lang) for r in reversed(order)], fontsize=9.5)
    ax.set_xlabel(shape(L["runs_x"], lang), fontsize=10)
    ax.set_xlim(0, 12.5)
    ax.grid(axis="x", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    handles = [
        plt.Line2D([], [], color=STRONG_C, linewidth=8, label=shape(L["flagged_high"], lang)),
        plt.Line2D([], [], color=WEAK_C, linewidth=8, label=shape(L["flagged_low"], lang)),
        plt.Line2D([], [], color=GREY_C, linewidth=8, label=shape(L["not_verified"], lang)),
    ]
    ax.legend(handles=handles, frameon=False, fontsize=8.5, ncol=3,
              loc="lower center", bbox_to_anchor=(0.5, -0.52))
    ax.set_title(shape(L["runs_title"], lang), fontsize=12, fontweight="bold",
                 color=INK, loc="center", pad=10)
    fig.savefig(out)
    plt.close(fig)


def figure_length(characteristic: dict[str, Any], lang: str, out: Path) -> None:
    L, names = LABELS[lang], RUN_NAMES[lang]
    fig, ax = plt.subplots(figsize=(6.6, 2.6))
    rows = [r for r in characteristic["runs"]]
    for index, run in enumerate(reversed(rows)):
        y = index
        # Episodes of equal length would sit on top of each other and hide the count, so
        # duplicates are stacked upward within the row band.
        seen: dict[int, int] = {}
        for episode in sorted(run["observed_episodes"], key=lambda e: e["answer_count"]):
            cls = episode["classification"]
            if cls == "EXCLUDED":
                continue
            length = episode["answer_count"]
            offset = seen.get(length, 0)
            seen[length] = offset + 1
            colour = STRONG_C if cls == "STRONG_ALERT" else WEAK_C
            ax.scatter(length, y + offset * 0.135, s=62, color=colour,
                       edgecolor="white", linewidth=1.2, zorder=3)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(
        [shape(names.get(r["run_label"], r["run_label"]), lang) for r in reversed(rows)],
        fontsize=9.5,
    )
    ax.tick_params(axis="y", pad=6)
    ax.set_xscale("log")
    ax.set_xticks([1, 2, 5, 10, 20, 50])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xlabel(shape(L["length_x"], lang), fontsize=10)
    ax.set_xlim(0.8, 90)
    ax.set_ylim(-0.5, len(rows) + 0.05)
    ax.grid(axis="x", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.annotate(shape(L["short_note"], lang), xy=(1.35, len(rows) - 0.72), fontsize=8.5,
                color=WEAK_C, ha="center", va="center", fontweight="bold")
    ax.annotate(shape(L["long_note"], lang), xy=(30, len(rows) - 1.62), fontsize=8.5,
                color=STRONG_C, ha="center", va="center", fontweight="bold")
    ax.set_title(shape(L["length_title"], lang), fontsize=12, fontweight="bold",
                 color=INK, loc="center", pad=10)
    fig.savefig(out)
    plt.close(fig)


def figure_baselines(baselines: dict[str, Any], lang: str, out: Path) -> None:
    L = LABELS[lang]
    run = baselines["runs"][1]
    rows = {n: r for n, r in run["baselines"].items() if not n.startswith("V1_WITHOUT_")}
    chosen = sorted(rows, key=lambda n: rows[n]["binary_review_agreement"] or 0, reverse=True)[:7]
    chosen = list(reversed(chosen))
    fallback = lambda n: n.replace("SINGLE_", "").replace("_", " ").lower()
    pretty = [shape(BASELINE_NAMES[lang].get(n, fallback(n)), lang) for n in chosen]
    three = [rows[n]["exact_three_class_agreement"] or 0 for n in chosen]
    binary = [rows[n]["binary_review_agreement"] or 0 for n in chosen]
    same3 = [rows[n]["identical_three_class"] for n in chosen]
    same2 = [rows[n]["identical_binary_review"] for n in chosen]

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.7), sharey=True)
    # In a right-to-left document panel (a) must sit on the right, or the reader meets (b) first.
    panels = [(three, same3, L["base_left"]), (binary, same2, L["base_right"])]
    if lang == "he":
        panels.reverse()
    for ax, (values, same, title) in zip(axes, panels):
        ax.barh(range(len(chosen)), values, height=0.6,
                color=[GREEN_C if s else WEAK_C for s in same],
                edgecolor="white", linewidth=1.1)
        for i, v in enumerate(values):
            ax.text(min(v + 0.03, 1.02), i, f"{v:.0%}", va="center", fontsize=8, color=MUTED)
        ax.set_xlim(0, 1.18)
        ax.set_xticks([0, 0.5, 1.0])
        ax.set_xticklabels(["0%", "50%", "100%"], fontsize=8.5)
        ax.set_xlabel(shape(L["base_x"], lang), fontsize=9)
        ax.grid(axis="x", color=GRID, linewidth=0.7)
        ax.set_axisbelow(True)
        ax.set_title(shape(title, lang), fontsize=9.5, fontweight="bold", color=INK, pad=6)
    label_axis = axes[1] if lang == "he" else axes[0]
    label_axis.set_yticks(range(len(chosen)))
    label_axis.set_yticklabels(pretty, fontsize=8.5)
    label_axis.tick_params(labelleft=lang != "he", labelright=lang == "he")
    handles = [
        plt.Line2D([], [], color=GREEN_C, linewidth=8, label=shape(L["same"], lang)),
        plt.Line2D([], [], color=WEAK_C, linewidth=8, label=shape(L["differs"], lang)),
    ]
    fig.legend(handles=handles, frameon=False, fontsize=8.5, ncol=2,
               loc="lower center", bbox_to_anchor=(0.5, -0.20))
    fig.suptitle(shape(L["base_title"], lang), fontsize=12, fontweight="bold", color=INK, y=1.06)
    fig.savefig(out)
    plt.close(fig)


def figure_mechanisms(mechanisms: dict[str, Any], lang: str, out: Path) -> None:
    L = LABELS[lang]
    run = mechanisms["runs"][1]
    rows = [r for r in run["per_case"] if r.get("fragment_stage")]
    cases = [r["case_id"] for r in rows]
    counts = [r["fragment_stage"]["domain_mistakes"] for r in rows]
    spoke = [r["detector_v1_flags_case"] for r in rows]
    fig, ax = plt.subplots(figsize=(6.6, 2.4))
    ax.bar(cases, counts, width=0.62,
           color=[STRONG_C if s else GREY_C for s in spoke], edgecolor="white", linewidth=1.0)
    ax.set_xlabel(shape(L["mech_x"], lang), fontsize=9.5)
    ax.set_ylabel(shape(L["mech_y"], lang), fontsize=9)
    ax.set_ylim(0, max(counts + [1]) * 1.5)
    ax.tick_params(axis="x", labelsize=7)
    ax.grid(axis="y", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    handles = [
        plt.Line2D([], [], color=STRONG_C, linewidth=8, label=shape(L["mech_spoke"], lang)),
        plt.Line2D([], [], color=GREY_C, linewidth=8, label=shape(L["mech_silent"], lang)),
    ]
    ax.legend(handles=handles, frameon=False, fontsize=8, loc="upper right")
    ax.set_title(shape(L["mech_title"], lang), fontsize=12, fontweight="bold",
                 color=INK, loc="center", pad=10)
    fig.savefig(out)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    base = root / "external_data/airtravel-pr38/analysis-baselines"
    recon = load(root / "docs/research/phd-proposal/study1c-reconciliation.json")
    characteristic = load(base / "operating-characteristic.json")
    baselines = load(base / "detector-baselines.json")
    mechanisms = load(base / "escalation-mechanisms.json")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for lang in ("en", "he"):
        setup(lang)
        for name, builder, payload in (
            ("runs", figure_runs, recon),
            ("length", figure_length, characteristic),
            ("baselines", figure_baselines, baselines),
            ("mechanisms", figure_mechanisms, mechanisms),
        ):
            target = args.out_dir / f"landing-{name}-{lang}.png"
            builder(payload, lang, target)
            written.append(target.name)
    print(json.dumps({"figures": written}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
