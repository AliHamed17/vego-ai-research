"""Charts C1 to C7 with the mandatory seven-field caption block.

English axis labels; Hebrew prose lives in the documents that embed them.
Requires matplotlib (installed ad hoc with ``uv run --with matplotlib``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

ON_COLOR = "#1F4E79"
OFF_COLOR = "#C55A11"
NEUTRAL = "#7F7F7F"
GREEN = "#548235"
RED = "#A6291F"


def _caption(fig, *, title: str, source: str, condition: str, denominator: str, evidence: str, metric: str, limitation: str) -> None:
    text = (
        f"Source: {source} | Condition: {condition} | Denominator: {denominator}\n"
        f"Evidence class: {evidence} | Metric: {metric}\n"
        f"Limitation: {limitation}"
    )
    fig.suptitle(title, fontsize=12, fontweight="bold", y=0.99)
    fig.text(0.01, 0.005, text, fontsize=7, ha="left", va="bottom", color="#333333", wrap=True)


def _save(fig, path: Path) -> Path:
    fig.tight_layout(rect=(0, 0.12, 1, 0.95))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200)
    import matplotlib.pyplot as plt

    plt.close(fig)
    return path


def chart_c1_completion(analysis: dict[str, Any], out: Path) -> Path:
    import matplotlib.pyplot as plt

    rows = analysis["paired"]
    ids = [r["case_id"] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4.2))
    x = range(len(ids))
    for offset, key, color, label in ((-0.2, "on", ON_COLOR, "VEGO_AI_ON"), (0.2, "off", OFF_COLOR, "VEGO_AI_OFF")):
        heights = [1 if r[f"{key}_status"] == "COMPLETED" else 0 for r in rows]
        valid = [r[f"{key}_valid"] for r in rows]
        bars = ax.bar([i + offset for i in x], heights, width=0.38, color=color, label=label)
        for bar, ok, status in zip(bars, valid, [r[f"{key}_status"] for r in rows], strict=True):
            mark = "valid" if ok else status.replace("_", " ").lower()
            ax.text(bar.get_x() + bar.get_width() / 2, 0.05 if heights else 0.05, mark, ha="center", va="bottom",
                    rotation=90, fontsize=6.5, color="white" if ok else RED)
    ax.set_xticks(list(x))
    ax.set_xticklabels(ids)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["not produced", "produced"])
    ax.set_xlabel("case id (Text2UML AirTravel full-frame numbering)")
    ax.legend(loc="upper right", fontsize=8)
    _caption(fig, title="C1  Paired artifact completion and structural validity per case",
             source=f"public-aggregate.json, run {analysis['run_id']}", condition="VEGO_AI_ON and VEGO_AI_OFF",
             denominator=f"{len(ids)} planned paired cases", evidence=analysis["evidence_class"],
             metric="M1 completion (artifact produced) and M2 structural validity (shared contract satisfied)",
             limitation="one corpus, one model, no ground truth; completion is not correctness")
    return _save(fig, out / "C1_completion_validity.png")


def chart_c2_cost(analysis: dict[str, Any], out: Path) -> Path:
    import matplotlib.pyplot as plt

    cond = analysis["conditions"]
    on, off = cond["VEGO_AI_ON"], cond["VEGO_AI_OFF"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    axes[0].bar(["ON setting-level", "ON case-attributed", "OFF"],
                [on["setting_level_requests"], on["case_attributed_requests"], off["requests"]],
                color=[NEUTRAL, ON_COLOR, OFF_COLOR])
    axes[0].set_ylabel("provider requests (incl. retries)")
    axes[0].set_title("Requests", fontsize=10)
    axes[1].bar(["ON setting-level", "ON case-attributed", "OFF"],
                [on["setting_level_cost_usd"], on["case_attributed_cost_usd"], off["cost_usd"]],
                color=[NEUTRAL, ON_COLOR, OFF_COLOR])
    axes[1].set_ylabel("priced cost, USD")
    axes[1].set_title(f"Cost (total {analysis['budget']['actual_cost_usd']:.4f} USD of {analysis['budget']['hard_ceiling_usd']:.2f} ceiling)", fontsize=10)
    for ax in axes:
        for tick in ax.get_xticklabels():
            tick.set_fontsize(8)
    _caption(fig, title="C2  Provider requests and priced cost per condition",
             source=f"public-aggregate.json, run {analysis['run_id']}", condition="VEGO_AI_ON (split) and VEGO_AI_OFF",
             denominator="all recorded requests including retries and parse re-attempts", evidence=analysis["evidence_class"],
             metric="M3 execution cost from recorded usage at frozen list prices (0.20 / 1.20 USD per 1M tokens)",
             limitation="cost is a descriptor of this run, not a superiority claim; setting-level ON cost is shared across cases")
    return _save(fig, out / "C2_requests_cost.png")


def chart_c3_time(analysis: dict[str, Any], out: Path) -> Path:
    import matplotlib.pyplot as plt

    rows = analysis["paired"]
    cond = analysis["conditions"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={"width_ratios": [1, 2.2]})
    axes[0].bar(["ON", "OFF"], [cond["VEGO_AI_ON"]["elapsed_seconds"], cond["VEGO_AI_OFF"]["elapsed_seconds"]], color=[ON_COLOR, OFF_COLOR])
    axes[0].set_ylabel("condition wall-clock, seconds")
    axes[0].set_title("Per condition (exact)", fontsize=10)
    ids = [r["case_id"] for r in rows]
    x = range(len(ids))
    axes[1].bar([i - 0.2 for i in x], [r["on_elapsed_span_s"] or 0 for r in rows], width=0.38, color=ON_COLOR, label="ON attributed span (approx.)")
    axes[1].bar([i + 0.2 for i in x], [r["off_elapsed_s"] or 0 for r in rows], width=0.38, color=OFF_COLOR, label="OFF per case (exact)")
    axes[1].set_xticks(list(x))
    axes[1].set_xticklabels(ids)
    axes[1].set_ylabel("seconds")
    axes[1].set_title("Per case", fontsize=10)
    axes[1].legend(fontsize=7)
    _caption(fig, title="C3  Elapsed time per condition and per case",
             source=f"public-aggregate.json, run {analysis['run_id']}", condition="VEGO_AI_ON and VEGO_AI_OFF",
             denominator="per condition exact; ON per case = first-to-last attributed request under concurrency 2",
             evidence=analysis["evidence_class"], metric="M4 elapsed wall-clock seconds",
             limitation="includes provider latency variance on one day; ON per-case spans overlap and are approximate")
    return _save(fig, out / "C3_elapsed_time.png")


def chart_c4_qa(analysis: dict[str, Any], out: Path) -> Path:
    import matplotlib.pyplot as plt

    rows = analysis["paired"]
    ids = [r["case_id"] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4.2))
    x = range(len(ids))
    ax.bar([i - 0.27 for i in x], [r["on_episodes"] or 0 for r in rows], width=0.26, color=ON_COLOR, label="episodes")
    ax.bar([i for i in x], [r["on_questions"] or 0 for r in rows], width=0.26, color="#2E75B6", label="questions")
    ax.bar([i + 0.27 for i in x], [r["on_answers"] or 0 for r in rows], width=0.26, color="#9DC3E6", label="answers")
    ax.set_xticks(list(x))
    ax.set_xticklabels(ids)
    ax.set_ylabel("count (ON only)")
    setting = analysis["detector"]["setting_level_episodes"]
    ax.set_title(f"Case-attributed episodes; {setting} additional setting-level episode(s) not shown per case", fontsize=9)
    ax.legend(fontsize=8)
    _caption(fig, title="C4  Inter-agent Q&A episodes, questions and answers per case (ON only)",
             source=f"public-aggregate.json, run {analysis['run_id']}", condition="VEGO_AI_ON",
             denominator="recorded episodes attributed to a case", evidence=analysis["evidence_class"],
             metric="M6 availability of communication evidence; M7 communication metrics",
             limitation="OFF has no episodes by design (NOT_AVAILABLE); zero episodes under ON is a valid observation")
    return _save(fig, out / "C4_qa_episodes.png")


def chart_c5_detector(analysis: dict[str, Any], out: Path) -> Path:
    import matplotlib.pyplot as plt

    det = analysis["detector"]
    order = ["STRONG_ALERT", "WEAK_ALERT", "NO_ALERT", "EXCLUDED"]
    colors = [RED, "#E9A23B", GREEN, NEUTRAL]
    values = [det["classifications"].get(k, 0) for k in order]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    axes[0].bar(order, values, color=colors)
    axes[0].set_ylabel("episodes")
    axes[0].set_title(f"Classification of {det['episodes_total']} episode(s)", fontsize=10)
    for tick in axes[0].get_xticklabels():
        tick.set_fontsize(7)
    codes = det["reason_codes"]
    axes[1].barh(list(codes.keys()) or ["none"], list(codes.values()) or [0], color=ON_COLOR)
    axes[1].set_title("Signals fired (an episode may fire several)", fontsize=10)
    for tick in axes[1].get_yticklabels():
        tick.set_fontsize(7)
    _caption(fig, title="C5  Detector-v1 candidate labels per episode (ON only, reporting-only)",
             source=f"public-aggregate.json, run {analysis['run_id']}", condition="VEGO_AI_ON; OFF = NOT_APPLICABLE",
             denominator=f"{det['scientific_complete']} scientifically complete episodes", evidence=analysis["evidence_class"],
             metric="M8 Detector-v1 classification (STRONG = S1 low confidence or S3 missing evidence or S7 max rounds; WEAK = S2 or S6)",
             limitation="no human labels exist; a label is a candidate for inspection, not a confirmed problem")
    return _save(fig, out / "C5_detector_v1.png")


def chart_c6_structure(analysis: dict[str, Any], out: Path) -> Path:
    import matplotlib.pyplot as plt

    rows = analysis["paired"]
    ids = [r["case_id"] for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    x = range(len(ids))
    for ax, key, title in ((axes[0], "mapping_rows", "Mapping rows"), (axes[1], "uncovered", "Uncovered fragments")):
        ax.bar([i - 0.2 for i in x], [r[f"on_{key}"] or 0 for r in rows], width=0.38, color=ON_COLOR, label="ON")
        ax.bar([i + 0.2 for i in x], [r[f"off_{key}"] or 0 for r in rows], width=0.38, color=OFF_COLOR, label="OFF")
        ax.set_xticks(list(x))
        ax.set_xticklabels(ids, fontsize=7)
        ax.set_title(title, fontsize=10)
        ax.legend(fontsize=7)
    _caption(fig, title="C6  Mapping rows and uncovered fragments per paired case",
             source=f"public-aggregate.json, run {analysis['run_id']}", condition="VEGO_AI_ON and VEGO_AI_OFF",
             denominator="completed artifacts (cases without an artifact show zero)", evidence=analysis["evidence_class"],
             metric="M1/M9 structural descriptors of the shared output contract",
             limitation="counts are structural descriptors, not quality judgements; more rows is not better")
    return _save(fig, out / "C6_structure.png")


def chart_c7_human_placeholder(analysis: dict[str, Any], out: Path) -> Path:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 3.2))
    ax.axis("off")
    ax.text(0.5, 0.6, "NOT_MEASURED", ha="center", va="center", fontsize=28, color=NEUTRAL, fontweight="bold")
    ax.text(0.5, 0.25, "No rater has scored. Agreement, correctness, precision, recall, F1, workload and benefit\n"
                       "will appear here only after two independent raters return the blinded cards.",
            ha="center", va="center", fontsize=9)
    _caption(fig, title="C7  Human assessment (Section E)", source="human-rater-rubric.he.md; cards in the private root",
             condition="VEGO_AI_ON episodes", denominator="cards scored by two independent raters (0 so far)",
             evidence="NOT_MEASURED", metric="M10 blinded decisions REVIEW_WORTHY / NOT_REVIEW_WORTHY / INSUFFICIENT_INFORMATION",
             limitation="nothing is plotted until real human ratings exist; no AI judgement stands in for a human")
    return _save(fig, out / "C7_human_placeholder.png")


def build_all_charts(analysis: dict[str, Any], out: Path) -> dict[str, Path]:
    import matplotlib

    matplotlib.use("Agg")
    return {
        "C1": chart_c1_completion(analysis, out),
        "C2": chart_c2_cost(analysis, out),
        "C3": chart_c3_time(analysis, out),
        "C4": chart_c4_qa(analysis, out),
        "C5": chart_c5_detector(analysis, out),
        "C6": chart_c6_structure(analysis, out),
        "C7": chart_c7_human_placeholder(analysis, out),
    }
