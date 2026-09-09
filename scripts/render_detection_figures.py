"""Charts for the detection baseline, in English and Hebrew.

Every chart is a small multiple: one panel per run, never one axis with the runs interleaved.
That is a correctness choice as much as a style one. The runs used different case counts and
configurations, so a grouped bar chart would invite a reader to compare heights across runs and
read a trend that the design does not support.

Colour carries one meaning across every panel. A single accent blue is the ordinary bar; warm
orange marks only the detection moment; and the confidence ramp runs light to dark from "sure" to
"not sure". The two lighter ramp steps sit below the 3:1 contrast floor against the page, so every
segment carries a printed value - the sanctioned relief, not an oversight.

Hebrew strings pass through the bidi algorithm before matplotlib sees them, because matplotlib
draws glyphs left to right and would otherwise reverse every label.

No provider is contacted. The only input is the detection-baseline JSON.
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
ACCENT = "#2a78d6"
WARM = "#c2410c"
NEUTRAL = "#6e6e7a"
CONF_RAMP = {"High": "#a8cdee", "Medium": "#3d86cf", "Low": "#0f3f6b"}
CLASS_COLOUR = {"STRONG_ALERT": "#0f3f6b", "WEAK_ALERT": "#3d86cf", "NO_ALERT": NEUTRAL}
CLASS_ORDER = ["STRONG_ALERT", "WEAK_ALERT", "NO_ALERT"]

RUN_KEYS = ["run0", "run1", "run2"]

T = {
    "en": {
        "runs": {"run0": "Run 0  (4 cases)", "run1": "Run 1  (21 cases)", "run2": "Run 2  (21 cases)"},
        "conf_title": "How sure was the answering agent? Every answer, counted",
        "conf_x": "share of all answers in the run",
        "conf": {"High": "fully sure", "Medium": "partly sure", "Low": "not sure"},
        "detect_title": "When does the first not-sure answer arrive?",
        "detect_x": "round of the conversation",
        "detect_y": "conversations",
        "detect_note": "round 1",
        "cumul_title": "By which round has every conversation been detected?",
        "cumul_x": "round",
        "cumul_y": "conversations detected",
        "signals_title": "Which alarm reasons actually fired?",
        "signals_x": "conversations where this fired",
        "len_title": "How long were the conversations?",
        "len_x": "answers in the conversation",
        "len_y": "conversations",
        "ev_title": "How much evidence did answers carry?",
        "ev_x": "evidence length (characters)",
        "ev_y": "answers",
        "case_title": "Which cases produced a conversation at all?",
        "case_x": "case",
        "case_y": "conversations",
        "case_yes": "produced a conversation",
        "case_no": "produced none - the rule never sees it",
        "never": "never fired",
        "known_title": "Known and unknown: how much could be answered with full confidence?",
        "known_rows": ["single questions answered", "whole conversations"],
        "known_yes": "known - answered fully sure",
        "known_no": "unknown - not fully sure",
        "alerts_title": "What did the rule decide for each conversation?",
        "alerts_unit": "one square = one conversation",
        "alerts": {"STRONG_ALERT": "strong alert", "WEAK_ALERT": "weak alert",
                   "NO_ALERT": "no alert - no human needed"},
        "alerts_short": {"STRONG_ALERT": "strong", "WEAK_ALERT": "weak", "NO_ALERT": "none"},
    },
    "he": {
        "runs": {"run0": "הרצה 0  (4 מקרים)", "run1": "הרצה 1  (21 מקרים)", "run2": "הרצה 2  (21 מקרים)"},
        "conf_title": "כמה בטוח היה הסוכן המשיב? כל תשובה, בספירה",
        "conf_x": "חלק מכלל התשובות בהרצה",
        "conf": {"High": "בטוח לגמרי", "Medium": "בטוח חלקית", "Low": "לא בטוח"},
        "detect_title": "מתי מגיעה התשובה הראשונה שאינה בטוחה?",
        "detect_x": "סבב בשיחה",
        "detect_y": "שיחות",
        "detect_note": "סבב 1",
        "cumul_title": "עד איזה סבב כל השיחות כבר זוהו?",
        "cumul_x": "סבב",
        "cumul_y": "שיחות שזוהו",
        "signals_title": "אילו סיבות אזעקה באמת נדלקו?",
        "signals_x": "שיחות שבהן זה נדלק",
        "len_title": "כמה ארוכות היו השיחות?",
        "len_x": "מספר תשובות בשיחה",
        "len_y": "שיחות",
        "ev_title": "כמה ראיות נשאו התשובות?",
        "ev_x": "אורך הראיה (תווים)",
        "ev_y": "תשובות",
        "case_title": "אילו מקרים בכלל יצרו שיחה?",
        "case_x": "מקרה",
        "case_y": "שיחות",
        "case_yes": "יצר שיחה",
        "case_no": "לא יצר - הכלל לעולם לא רואה אותו",
        "never": "מעולם לא נדלק",
        "known_title": "ידוע ולא ידוע: כמה ניתן היה לענות בביטחון מלא?",
        "known_rows": ["שאלות בודדות שנענו", "שיחות שלמות"],
        "known_yes": "ידוע - נענה בביטחון מלא",
        "known_no": "לא ידוע - לא בטוח לגמרי",
        "alerts_title": "מה הכלל החליט לגבי כל שיחה?",
        "alerts_unit": "ריבוע אחד = שיחה אחת",
        "alerts": {"STRONG_ALERT": "אזעקה חזקה", "WEAK_ALERT": "אזעקה חלשה",
                   "NO_ALERT": "ללא אזעקה - אין צורך באדם"},
        "alerts_short": {"STRONG_ALERT": "חזקה", "WEAK_ALERT": "חלשה", "NO_ALERT": "ללא"},
    },
}

SIGNALS_PLAIN = {
    "en": {
        "S1_LOW_ANSWER_CONFIDENCE": "an answer said 'not sure'",
        "S2_MEDIUM_ANSWER_CONFIDENCE": "an answer said 'partly sure'",
        "S6_MULTIPLE_QA_ROUNDS": "took more than one round",
        "S7_TERMINATED_MAX_ROUNDS": "hit the round limit",
        "S3_MISSING_ANSWER_EVIDENCE": "an answer gave no evidence",
    },
    "he": {
        "S1_LOW_ANSWER_CONFIDENCE": "תשובה אמרה ״לא בטוח״",
        "S2_MEDIUM_ANSWER_CONFIDENCE": "תשובה אמרה ״בטוח חלקית״",
        "S6_MULTIPLE_QA_ROUNDS": "נדרש יותר מסבב אחד",
        "S7_TERMINATED_MAX_ROUNDS": "הגיע למגבלת הסבבים",
        "S3_MISSING_ANSWER_EVIDENCE": "תשובה לא נתנה ראיה",
    },
}


def shape(text: str, lang: str) -> str:
    return get_display(text) if lang == "he" else text


def setup() -> None:
    plt.rcParams.update(
        {
            "font.family": "Segoe UI",
            "font.size": 9.5,
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


def panels(count: int, height: float):
    fig, axes = plt.subplots(1, count, figsize=(7.2, height))
    return fig, list(axes) if count > 1 else [axes]


def finish(fig, ax_list, title: str, lang: str, y: float = 1.04) -> None:
    for ax in ax_list:
        ax.grid(axis="y", color=GRID, linewidth=0.7)
        ax.set_axisbelow(True)
    fig.suptitle(shape(title, lang), fontsize=11.5, fontweight="bold", color=INK,
                 x=0.02, ha="left", y=y)


def figure_confidence(runs: list[dict[str, Any]], lang: str, out: Path) -> None:
    L = T[lang]
    fig, ax = plt.subplots(figsize=(7.2, 3.05))
    for index, run in enumerate(reversed(runs)):
        left = 0.0
        for label in ("High", "Medium", "Low"):
            share = run["confidence_share"][label]
            count = run["confidence_counts"][label]
            ax.barh(index, share, left=left, height=0.6, color=CONF_RAMP[label],
                    edgecolor="white", linewidth=1.4)
            if share > 0.05:
                ax.text(left + share / 2, index, f"{count}\n{share:.0%}", ha="center",
                        va="center", fontsize=8,
                        color=INK if label == "High" else "white", fontweight="bold")
            left += share
    ax.set_yticks(range(len(runs)))
    ax.set_yticklabels([shape(L["runs"][r["run_key"]], lang) for r in reversed(runs)], fontsize=9)
    ax.set_xlabel(shape(L["conf_x"], lang), fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=8.5)
    ax.grid(axis="x", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    handles = [
        plt.Line2D([], [], color=CONF_RAMP[k], linewidth=8, label=shape(L["conf"][k], lang))
        for k in ("High", "Medium", "Low")
    ]
    ax.legend(handles=handles, frameon=False, fontsize=8.5, ncol=3,
              loc="lower center", bbox_to_anchor=(0.5, -0.30))
    ax.set_title(shape(L["conf_title"], lang), fontsize=11.5, fontweight="bold",
                 color=INK, loc="left", pad=8)
    fig.savefig(out)
    plt.close(fig)


def figure_detection(runs: list[dict[str, Any]], lang: str, out: Path) -> None:
    L = T[lang]
    fig, axes = panels(len(runs), 2.72)
    for ax, run in zip(axes, runs):
        hist = run["first_unsure_answer_round"]
        rounds = [int(r) for r in hist]
        values = [hist[str(r)] for r in rounds]
        colours = [WARM if r == 1 else ACCENT for r in rounds]
        ax.bar(rounds, values, color=colours, width=0.7, edgecolor="white", linewidth=1.0)
        for r, v in zip(rounds, values):
            if v:
                ax.text(r, v + max(values) * 0.06, str(v), ha="center", fontsize=8.5,
                        color=INK, fontweight="bold")
        ax.set_title(shape(L["runs"][run["run_key"]], lang), fontsize=9, color=INK, pad=4)
        ax.set_xlabel(shape(L["detect_x"], lang), fontsize=8.5)
        ax.set_xticks([1, 3, 5, 7, 9])
        ax.set_ylim(0, max(values) * 1.32 if max(values) else 1)
        ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        ax.tick_params(labelsize=8)
    axes[0].set_ylabel(shape(L["detect_y"], lang), fontsize=8.5)
    finish(fig, axes, L["detect_title"], lang)
    fig.savefig(out)
    plt.close(fig)


def figure_cumulative(runs: list[dict[str, Any]], lang: str, out: Path) -> None:
    L = T[lang]
    fig, axes = panels(len(runs), 2.93)
    for ax, run in zip(axes, runs):
        rows = run["cumulative_detection_by_round"]
        xs = [row["round"] for row in rows]
        ys = [row["detected_by_here"] for row in rows]
        total = run["complete_episodes"]
        ax.step(xs, ys, where="post", color=ACCENT, linewidth=2.2)
        ax.fill_between(xs, ys, step="post", color=ACCENT, alpha=0.13)
        ax.axhline(total, color=MUTED, linewidth=0.9, linestyle=(0, (4, 3)))
        ax.scatter([1], [ys[0]], s=45, color=WARM, zorder=4, edgecolor="white", linewidth=1.2)
        ax.annotate(f"{ys[0]}/{total}", (1, ys[0]), textcoords="offset points",
                    xytext=(2, 9), fontsize=8.5, color=WARM, fontweight="bold", ha="left")
        ax.set_title(shape(L["runs"][run["run_key"]], lang), fontsize=9, color=INK, pad=4)
        ax.set_xlabel(shape(L["cumul_x"], lang), fontsize=8.5)
        ax.set_xticks([1, 3, 5, 7, 9])
        ax.set_ylim(0, total * 1.32)
        ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        ax.tick_params(labelsize=8)
    axes[0].set_ylabel(shape(L["cumul_y"], lang), fontsize=8.5)
    finish(fig, axes, L["cumul_title"], lang)
    fig.savefig(out)
    plt.close(fig)


def figure_signals(runs: list[dict[str, Any]], lang: str, out: Path) -> None:
    L, names = T[lang], SIGNALS_PLAIN[lang]
    order = ["S1_LOW_ANSWER_CONFIDENCE", "S2_MEDIUM_ANSWER_CONFIDENCE",
             "S6_MULTIPLE_QA_ROUNDS", "S7_TERMINATED_MAX_ROUNDS",
             "S3_MISSING_ANSWER_EVIDENCE"]
    fig, axes = panels(len(runs), 3.0)
    for ax, run in zip(axes, runs):
        counts = [run["signal_episode_counts"][s] for s in order]
        total = run["complete_episodes"]
        ys = range(len(order))
        ax.barh(list(ys), counts, height=0.62,
                color=[NEUTRAL if c == 0 else ACCENT for c in counts],
                edgecolor="white", linewidth=1.0)
        for y, c in zip(ys, counts):
            text = str(c) if c else shape(L["never"], lang)
            ax.text(c + total * 0.04, y, text, va="center", fontsize=8,
                    color=INK if c else MUTED, fontweight="bold" if c else "normal")
        ax.set_xlim(0, total * 1.5)
        ax.set_title(shape(L["runs"][run["run_key"]], lang), fontsize=9, color=INK, pad=4)
        ax.set_xlabel(shape(L["signals_x"], lang), fontsize=8.5)
        ax.invert_yaxis()
        ax.tick_params(labelsize=8)
        ax.grid(axis="x", color=GRID, linewidth=0.7)
        ax.set_axisbelow(True)
    axes[0].set_yticks(range(len(order)))
    axes[0].set_yticklabels([shape(names[s], lang) for s in order], fontsize=8)
    for ax in axes[1:]:
        ax.set_yticks(range(len(order)))
        ax.set_yticklabels([])
    fig.suptitle(shape(L["signals_title"], lang), fontsize=11.5, fontweight="bold",
                 color=INK, x=0.02, ha="left", y=1.05)
    fig.savefig(out)
    plt.close(fig)


def _histogram(ax, values: list[int], bins, colour: str) -> None:
    ax.hist(values, bins=bins, color=colour, edgecolor="white", linewidth=1.0)


def figure_lengths(runs: list[dict[str, Any]], lang: str, out: Path) -> None:
    L = T[lang]
    fig, axes = panels(len(runs), 3.0)
    bins = [1, 2, 3, 4, 5, 10, 20, 40, 70]
    for ax, run in zip(axes, runs):
        _histogram(ax, run["episode_lengths"], bins, ACCENT)
        ax.set_xscale("log")
        ax.set_xticks([1, 3, 10, 40])
        ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.set_title(shape(L["runs"][run["run_key"]], lang), fontsize=9, color=INK, pad=4)
        ax.set_xlabel(shape(L["len_x"], lang), fontsize=8.5)
        ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        ax.tick_params(labelsize=8)
    axes[0].set_ylabel(shape(L["len_y"], lang), fontsize=8.5)
    finish(fig, axes, L["len_title"], lang)
    fig.savefig(out)
    plt.close(fig)


def figure_evidence(runs: list[dict[str, Any]], lang: str, out: Path) -> None:
    L = T[lang]
    fig, axes = panels(len(runs), 2.6)
    bins = [0, 50, 100, 150, 200, 300, 450, 650]
    for ax, run in zip(axes, runs):
        _histogram(ax, run["evidence_length_values"], bins, ACCENT)
        ax.set_title(shape(L["runs"][run["run_key"]], lang), fontsize=9, color=INK, pad=4)
        ax.set_xlabel(shape(L["ev_x"], lang), fontsize=8.5)
        ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        ax.tick_params(labelsize=8)
    axes[0].set_ylabel(shape(L["ev_y"], lang), fontsize=8.5)
    finish(fig, axes, L["ev_title"], lang)
    fig.savefig(out)
    plt.close(fig)


def figure_cases(runs: list[dict[str, Any]], lang: str, out: Path) -> None:
    L = T[lang]
    run = next(r for r in runs if r["run_key"] == "run1")
    cases = [f"{n:02d}" for n in range(1, 22)]
    counts = [run["per_case"].get(c, {}).get("episodes", 0) for c in cases]
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.bar(cases, counts, width=0.66,
           color=[ACCENT if c else NEUTRAL for c in counts],
           edgecolor="white", linewidth=1.0)
    ax.set_xlabel(shape(L["case_x"], lang), fontsize=9)
    ax.set_ylabel(shape(L["case_y"], lang), fontsize=8.5)
    ax.set_ylim(0, max(counts + [1]) * 1.6)
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.tick_params(axis="x", labelsize=7.5)
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(axis="y", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    # A case that produced nothing has a zero-height bar, which draws nothing at all. Without a
    # mark on the baseline the legend would name a colour the reader can never find, and the
    # blind spot - the point of the chart - would be invisible.
    empty = [index for index, count in enumerate(counts) if count == 0]
    ax.scatter(empty, [0] * len(empty), marker="s", s=22, color=NEUTRAL, zorder=4,
               clip_on=False)
    handles = [
        plt.Line2D([], [], color=ACCENT, linewidth=8, label=shape(L["case_yes"], lang)),
        plt.Line2D([], [], color=NEUTRAL, marker="s", markersize=6, linewidth=0,
                   label=shape(L["case_no"], lang)),
    ]
    ax.legend(handles=handles, frameon=False, fontsize=8, ncol=2, loc="upper right")
    ax.set_title(f'{shape(L["case_title"], lang)}  -  {shape(L["runs"]["run1"], lang)}',
                 fontsize=11.5, fontweight="bold", color=INK, loc="left", pad=8)
    fig.savefig(out)
    plt.close(fig)


def figure_known(runs: list[dict[str, Any]], lang: str, out: Path) -> None:
    """Known vs unknown, at both levels, because the two levels disagree.

    A quarter of individual answers came back fully sure; no conversation was fully sure from
    start to finish. Showing only one of those two rows would let a reader carry the wrong
    number away, so both rows sit in the same panel and share one axis.
    """
    L = T[lang]
    fig, axes = panels(len(runs), 2.4)
    for ax, run in zip(axes, runs):
        known_answers = run["confidence_counts"]["High"]
        total_answers = run["answers_total"]
        known_eps = run["episodes_with_no_unsure_answer"]
        total_eps = run["complete_episodes"]
        rows = [(known_answers, total_answers), (known_eps, total_eps)]
        for index, (known, total) in enumerate(rows):
            y = 1 - index
            share = known / total if total else 0.0
            for value, start, width, colour in (
                (known, 0.0, share, CONF_RAMP["High"]),
                (total - known, share, 1 - share, CONF_RAMP["Low"]),
            ):
                ax.barh(y, width, left=start, height=0.52, color=colour,
                        edgecolor="white", linewidth=1.4)
                if width > 0.13:
                    ax.text(start + width / 2, y, f"{value}\n{width:.0%}", ha="center",
                            va="center", fontsize=8,
                            color=INK if colour == CONF_RAMP["High"] else "white",
                            fontweight="bold")
            if share <= 0.13:
                ax.text(0.012, y + 0.40, str(known), ha="left", va="bottom", fontsize=8.5,
                        color=INK, fontweight="bold")
        ax.set_yticks([1, 0])
        ax.set_yticklabels([shape(r, lang) for r in L["known_rows"]], fontsize=8)
        ax.set_ylim(-0.55, 1.75)
        ax.set_xlim(0, 1)
        ax.set_xticks([0, 0.5, 1.0])
        ax.set_xticklabels(["0%", "50%", "100%"], fontsize=8)
        ax.set_title(shape(L["runs"][run["run_key"]], lang), fontsize=9, color=INK, pad=4)
        ax.grid(axis="x", color=GRID, linewidth=0.7)
        ax.set_axisbelow(True)
    for ax in axes[1:]:
        ax.set_yticklabels([])
    handles = [
        plt.Line2D([], [], color=CONF_RAMP["High"], linewidth=8, label=shape(L["known_yes"], lang)),
        plt.Line2D([], [], color=CONF_RAMP["Low"], linewidth=8, label=shape(L["known_no"], lang)),
    ]
    axes[1].legend(handles=handles, frameon=False, fontsize=8.5, ncol=2,
                   loc="upper center", bbox_to_anchor=(0.5, -0.16))
    fig.suptitle(shape(L["known_title"], lang), fontsize=11.5, fontweight="bold",
                 color=INK, x=0.02, ha="left", y=1.10)
    fig.savefig(out)
    plt.close(fig)


def figure_alerts(runs: list[dict[str, Any]], lang: str, out: Path) -> None:
    """One square per conversation, coloured by what the rule decided.

    The legend keeps the `no alert` entry even though it is empty in every run. An absent
    category drawn as an absent legend row would read as an oversight; drawn as a present row
    with nothing beside it, it reads as the finding it is.
    """
    L = T[lang]
    per_row = 4
    fig, axes = panels(len(runs), 2.6)
    # One y-range for every panel. With aspect="equal" matplotlib centres each panel's data box,
    # so panels holding fewer rows would drift downwards and read as a different scale.
    tallest = max(
        (sum(run["detector_classes"].values()) + per_row - 1) // per_row for run in runs
    )
    for ax, run in zip(axes, runs):
        classes = run["detector_classes"]
        squares = [k for k in CLASS_ORDER for _ in range(classes.get(k, 0))]
        for index, key in enumerate(squares):
            column, row = index % per_row, index // per_row
            ax.add_patch(plt.Rectangle((column, -row), 0.86, 0.86,
                                       facecolor=CLASS_COLOUR[key], edgecolor="white",
                                       linewidth=1.2))
        ax.set_xlim(-0.1, per_row + 0.05)
        ax.set_ylim(-tallest + 0.1, 1.0)
        ax.set_aspect("equal")
        ax.axis("off")
        counted = "   ".join(
            f"{classes.get(k, 0)} {L['alerts_short'][k]}" for k in CLASS_ORDER
        )
        heading = shape(L["runs"][run["run_key"]], lang)
        ax.set_title(heading + "\n" + shape(counted, lang), fontsize=9, color=INK, pad=4)
    handles = [
        plt.Line2D([], [], color=CLASS_COLOUR[k], linewidth=8, label=shape(L["alerts"][k], lang))
        for k in CLASS_ORDER
    ]
    axes[1].legend(handles=handles, frameon=False, fontsize=8.2, ncol=3,
                   loc="upper center", bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(shape(L["alerts_title"], lang), fontsize=11.5, fontweight="bold",
                 color=INK, x=0.02, ha="left", y=1.06)
    fig.text(0.98, 1.06, shape(L["alerts_unit"], lang), fontsize=8, color=MUTED, ha="right",
             va="top")
    fig.savefig(out)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.data.read_text(encoding="utf-8"))
    runs = sorted(payload["runs"], key=lambda r: RUN_KEYS.index(r["run_key"]))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    setup()
    written = []
    for lang in ("en", "he"):
        for name, builder in (
            ("known", figure_known),
            ("confidence", figure_confidence),
            ("detection", figure_detection),
            ("cumulative", figure_cumulative),
            ("alerts", figure_alerts),
            ("signals", figure_signals),
            ("lengths", figure_lengths),
            ("evidence", figure_evidence),
            ("cases", figure_cases),
        ):
            target = args.out_dir / f"detect-{name}-{lang}.png"
            builder(runs, lang, target)
            written.append(target.name)
    print(json.dumps({"figures": written}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
