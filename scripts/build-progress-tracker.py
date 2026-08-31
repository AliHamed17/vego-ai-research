#!/usr/bin/env python3
"""Refresh the AUTO regions of docs/PROGRESS_TRACKER.md from live sources.

Read-only over project data (it only writes the tracker). No API/LLM. Replaces marked regions
(<!-- AUTO:NAME:start --> ... <!-- AUTO:NAME:end -->) so the hand-written prose/architecture stays intact.

Sources: git, dashboard metrics_snapshot, EXP-001 summary, the deterministic classifier, the annotation
package sheets, the session log, plus live runs of the evidence-consistency guard and (optional) pytest.

Run:  python scripts/build-progress-tracker.py             (fast; skips pytest)
      python scripts/build-progress-tracker.py --run-tests (also runs pytest for an exact pass count)
      python scripts/build-progress-tracker.py --check     (fail if generated regions are stale)
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VEGO = ROOT / "VEGO-AI"
TRACKER = ROOT / "docs" / "PROGRESS_TRACKER.md"


def jload(rel):
    p = ROOT / rel
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def run(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:  # noqa: BLE001
        return 1, str(e)


def git(*args):
    _, out = run(["git", *args], timeout=20)
    return out.strip()


def count_filled(path, col="expert_label"):
    p = ROOT / path
    if not p.exists():
        return 0, 0
    with p.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    filled = sum(1 for r in rows if (r.get(col) or "").strip())
    return filled, len(rows)


def replace_region(text, name, body):
    pat = re.compile(rf"(<!-- AUTO:{name}:start -->).*?(<!-- AUTO:{name}:end -->)", re.DOTALL)
    repl = rf"\1\n{body}\n\2"
    new, n = pat.subn(lambda m: m.group(1) + "\n" + body + "\n" + m.group(2), text)
    return new, n


def recent_activity_lines(log_path: Path, limit: int = 6) -> list[str]:
    """Return the newest retained session headings first."""
    if not log_path.exists():
        return []
    headings = [
        line[3:].strip()
        for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.startswith("## ")
    ]
    return [f"- {heading}" for heading in reversed(headings[-limit:])]


def snapshot_lines(program_status: dict) -> str:
    """Render the iteration summary from ProgramStatusSnapshot-v1."""
    history = program_status.get("iterationHistory", {})
    latest = program_status.get("latestAcceptedIteration", {})
    accepted = history.get("acceptedCount")
    historical = history.get("historicalPreManifest", [])
    manifested = history.get("manifestBacked", [])
    iteration = latest.get("iteration")
    verdict = latest.get("verdict")
    kind = latest.get("iterationKind")
    if not (
        isinstance(accepted, int)
        and accepted > 0
        and historical
        and manifested
        and isinstance(iteration, int)
        and verdict
        and kind
    ):
        raise ValueError("ProgramStatusSnapshot-v1 lacks accepted-iteration metadata")
    historical_range = f"{min(historical):03d}-{max(historical):03d}"
    manifest_range = f"{min(manifested):03d}-{max(manifested):03d}"
    return (
        "> **Two tracks are active:** offline H-layer architecture/experiment advancement "
        "and the human-gated evaluation\n"
        f"> preparation. {accepted} H-layer iterations are accepted; "
        f"{historical_range} are historical/pre-manifest and {manifest_range} are "
        f"manifest-backed. Iteration {iteration:03d} is the latest `{verdict}` "
        f"{kind.replace('_', '-') } snapshot. None selects a default.\n"
        "> Until at least 20 generalization-safe labels exist, accuracy improvement "
        "cannot be evaluated."
    )


def snapshot_generated_at(program_status: dict) -> str:
    """Return the canonical snapshot timestamp in UTC for deterministic output."""
    raw = program_status.get("generatedAt")
    if not isinstance(raw, str):
        raise ValueError("ProgramStatusSnapshot-v1 lacks generatedAt")
    parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    return parsed.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-tests", action="store_true", help="run pytest for an exact pass count")
    ap.add_argument("--check", action="store_true", help="fail instead of writing when stale")
    args = ap.parse_args(argv)
    if args.check and args.run_tests:
        ap.error("--check and --run-tests cannot be combined")

    head = git("rev-parse", "--short", "HEAD") or "unknown"
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "unknown"

    snap = jload("VEGO-AI/reports/results_dashboard/metrics_snapshot.json") or {}
    ov = snap.get("overview", {})
    rp = snap.get("reproducibility", {})
    dash_commit = rp.get("git_commit", "unknown")
    program_status = (
        jload("docs/research/h-layer/program-status-snapshot-v1.json") or {}
    )
    now = snapshot_generated_at(program_status)

    e1 = (jload("reports/generated/exp001/exp001_summary.json") or {}).get("totals", {})
    safe_labels_eval = e1.get("generalization_safe_expert_labeled_count", 0)
    differs = e1.get("changed_count", ov.get("ai_classification_changed_count", 0))

    # Thesis chapter count excludes front matter such as 00-abstract.md.
    chapters_dir = ROOT / "thesis" / "chapters"
    chapters = []
    if chapters_dir.exists():
        chapter_file_pattern = re.compile(r"^(0[1-9]|10)-.+\.md$")
        chapters = sorted(p for p in chapters_dir.glob("*.md") if chapter_file_pattern.match(p.name))
    n_chap = len(chapters)

    # label collection (annotation package)
    g_filled, _ = count_filled("reports/generated/exp003/annotation_package/gold_labels.csv", "gold_label")
    r1_filled, r1_total = count_filled("reports/generated/exp003/annotation_package/blind_sheet_reviewer1.csv")
    r2_filled, _ = count_filled("reports/generated/exp003/annotation_package/blind_sheet_reviewer2.csv")
    safe_total = r1_total or 24
    safe_filled = max(g_filled, min(r1_filled, r2_filled))  # adjudicated, else both-reviewed

    # policy frozen?
    clf = (VEGO / "framework" / "memory_informed_classifier.py")
    clf_txt = clf.read_text(encoding="utf-8", errors="ignore") if clf.exists() else ""
    policy_v1 = ('POLICY_VERSION = "memory-informed-classifier-v1"' in clf_txt
                 and "memory-informed-classifier-v1.1" not in clf_txt)

    # evidence guard (live)
    gcode, gout = run([sys.executable, "scripts/check_evidence_consistency.py"], timeout=120)
    gm = re.search(r"(\d+)/(\d+) present checks passed", gout)
    guard_str = f"{gm.group(0)}" if gm else ("PASS" if gcode == 0 else "see guard")
    guard_state = "PASS" if gcode == 0 else "FAIL"

    # pytest (optional)
    if args.run_tests:
        _, pout = run([sys.executable, "-m", "pytest", "VEGO-AI/tests", "-q"], timeout=600)
        pm = re.search(r"(\d+) passed", pout)
        tests_str = f"{pm.group(1)} passed" if pm else "see pytest"
    else:
        recorded_tests = (
            program_status.get("verificationRecord", {})
            .get("tests", {})
            .get("VEGO-AI/tests", {})
            .get("passed")
        )
        tests_str = (
            f"{recorded_tests} passed _(dated verification record)_"
            if recorded_tests is not None
            else "not recorded _(rerun with --run-tests to refresh)_"
        )

    # ---- build region bodies --------------------------------------------------
    stamp = (
        f"H-layer track state as of {now} (from "
        "`docs/research/h-layer/program-status-snapshot-v1.json`; this date does not move unless that "
        "snapshot is regenerated, and does not reflect the separate PhD-proposal track - for overall "
        "current project status see `docs/agent-memory/current-state.md`) · "
        "live branch, revision, and worktree state intentionally omitted · "
        "generated by `scripts/build-progress-tracker.py`"
    )
    snapshot = snapshot_lines(program_status)

    thesis_pct = round(n_chap / 10 * 100)
    f_status = ("🟥 Blocked on human labeling | 0%" if safe_filled == 0
                else f"🟧 Pilot ({safe_filled} safe labels) | {min(95, round(safe_filled/20*100))}%")
    phases = "\n".join([
        "| Phase | Status | % |",
        "| --- | --- | ---: |",
        "| A. Artifact build (M1→M4B-1) | ✅ Complete, merged, tagged | 100% |",
        "| B. Inspection (dashboard + visualizer) | ✅ Complete, merged | 100% |",
        "| C. Evaluation tooling (EXP-001…005 + harness + guard) | ✅ Complete | 100% |",
        "| D. Annotation package (bias/leakage-controlled) | ✅ Ready to send | 100% |",
        f"| E. Thesis write-up | 🟦 {n_chap} / 10 chapters drafted | ~{thesis_pct}% |",
        f"| F. Empirical evidence (expert labels → results) | {f_status} |",
    ])

    if safe_filled == 0:
        labels = (f"`safe labels filled: 0 / {safe_total}` — need **≥20** before any quantitative claim "
                  f"(pilot at 1–19; blocked at 0). reviewer-1 {r1_filled}, reviewer-2 {r2_filled}, adjudicated {g_filled}.")
    else:
        labels = (f"`safe labels filled: {safe_filled} / {safe_total}` (reviewer-1 {r1_filled}, reviewer-2 "
                  f"{r2_filled}, adjudicated {g_filled}) — {'pilot' if safe_filled < 20 else 'quantitative allowed'}.")

    invariants = "\n".join([
        "| Invariant | Value | Checked by |",
        "| --- | --- | --- |",
        f"| Tests passing | **{tests_str}** | `pytest VEGO-AI/tests` |",
        f"| `ai_classification_changed` | **{ov.get('ai_classification_changed_count', '?')}** | dashboard / guard |",
        f"| baseline `eval_output` modified | **{str(rp.get('baseline_eval_outputs_modified', '?')).lower()}** | guard |",
        f"| memory-informed differs from original | **{differs} / {ov.get('variability_pattern_count','?')}** | guard |",
        f"| generalization-safe expert labels | **{safe_labels_eval}** | guard |",
        f"| deterministic policy | **{'v1 (no M4B-1.1 in code)' if policy_v1 else 'CHANGED — verify!'}** | guard |",
        f"| evidence consistency | **{guard_str} {guard_state}** | `scripts/check_evidence_consistency.py` |",
        "",
        (f"Scale figures: **{ov.get('case_count','?')}** models · **{ov.get('variability_pattern_count','?')}** "
         f"patterns · **{ov.get('human_review_queue_count','?')}** review items · "
         f"**{ov.get('judgment_memory_count','?')}** reusable judgments · "
         f"**{ov.get('memory_advice_count','?')}** advice items."),
    ])

    # recent activity from session log
    slog = (ROOT / "docs" / "agent-memory" / "session-log.md")
    acts = recent_activity_lines(slog)
    activity = "\n".join(acts) if acts else "- _(no session-log entries found)_"

    # ---- apply ---------------------------------------------------------------
    text = TRACKER.read_text(encoding="utf-8")
    total = 0
    for name, body in [
        ("stamp", stamp),
        ("snapshot", snapshot),
        ("phases", phases),
        ("labels", labels),
        ("invariants", invariants),
        ("activity", activity),
    ]:
        text, n = replace_region(text, name, body)
        if n == 0:
            print(f"WARNING: region AUTO:{name} not found")
        total += n
    current = TRACKER.read_text(encoding="utf-8")
    if args.check:
        if text != current:
            print("progress tracker: STALE", file=sys.stderr)
            return 1
        print("progress tracker: PASS")
        return 0
    TRACKER.write_text(text, encoding="utf-8", newline="\n")

    print(f"updated {total} AUTO regions in docs/PROGRESS_TRACKER.md")
    print(f"  head={head} branch={branch} dash_commit={dash_commit} chapters={n_chap}")
    print(f"  safe_labels_filled={safe_filled}/{safe_total} guard={guard_state} ({guard_str}) tests={tests_str}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
