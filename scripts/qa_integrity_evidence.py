"""Evidence that the Q&A integrity suite actually guards the pipeline.

Each fix is reverted in turn and the suite re-run. A fix whose removal breaks no
test is unguarded, and the suite would not notice if that fix were lost again."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUITE = "VEGO-AI/tests/test_qa_pipeline_integrity.py"
EXTRA = "VEGO-AI/tests/test_qa_id_correlation.py"

MUTATIONS = [
    {
        "id": "M1-id-correlation",
        "guards": "the harness must ignore OUTPUT FORMAT example ids",
        "file": "VEGO-AI/framework/qa_instrumented_runner.py",
        "find": r'_ASKED_ID_RE = re\.compile\(.*?\)\n',
        "replace": '_ASKED_ID_RE = re.compile(r"(Q_(?:lang|dom)_\\d{3})")\n',
    },
    {
        "id": "M2-unanswered-reporting",
        "guards": "unanswered questions must not be dropped silently",
        "file": "VEGO-AI/framework/orchestrator.py",
        "find": r'    _report_unanswered\(questions, answers, "(?:lang|dom)"\)\n',
        "replace": "",
    },
    {
        "id": "M3-malformed-reporting",
        "guards": "answers missing confidence or evidence must be named",
        "file": "VEGO-AI/framework/orchestrator.py",
        "find": r'    _report_malformed_answers\(answers, "(?:lang|dom)"\)\n',
        "replace": "",
    },
    {
        "id": "M4-provenance",
        "guards": "the asking agent and round must be persisted with each answer",
        "file": "VEGO-AI/framework/qa_registry.py",
        "find": r'            for key, value in \(provenance or \{\}\)\.items\(\):\n                record\.setdefault\(key, value\)\n',
        "replace": "",
    },
    {
        "id": "M5-question-text",
        "guards": "the originating question text must be persisted with its answer",
        "file": "VEGO-AI/framework/qa_registry.py",
        "find": r'            if source\.get\("question"\) and not record\.get\("question"\):\n                record\["question"\] = source\["question"\]\n',
        "replace": "",
    },
    {
        "id": "M6-setting-id",
        "guards": "ids restart per setting, so each record must name its setting",
        "file": "VEGO-AI/framework/qa_registry.py",
        "find": r'            if self\.setting_id:\n                record\.setdefault\("setting_id", self\.setting_id\)\n',
        "replace": "",
    },
    {
        "id": "M7-reroute",
        "guards": "a scope-rejected question must be rerouted, not dropped",
        "file": "VEGO-AI/framework/orchestrator.py",
        "find": r'    rejected_ids = \{e\.get\("question_id"\) for e in \(result\.get\("scope_errors"\) or \[\]\)\}\n',
        "replace": "    rejected_ids = set()\n",
    },
    {
        "id": "M8-resume-seeding",
        "guards": "a resumed run must not re-issue ids from the prior run",
        "file": "VEGO-AI/framework/qa_registry.py",
        "find": r'            self\._counters\[scope\] = highest\n',
        "replace": "            pass\n",
    },
]


def run_suite(cwd: Path) -> tuple[int, int, list[str]]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", SUITE, EXTRA, "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=cwd, capture_output=True, text=True,
    )
    out = proc.stdout + proc.stderr
    if "during collection" in out:
        raise RuntimeError("suite could not be collected: "
                           + out.strip().splitlines()[-2][:200])
    failed = sorted({m.group(1) for m in re.finditer(r"^FAILED \S+::(\w+)", out, re.M)})
    m = re.search(r"(\d+) failed[,\s]+(\d+) passed", out)
    if m:
        return int(m.group(1)), int(m.group(2)), failed
    m = re.search(r"(\d+) passed", out)
    return 0, int(m.group(1)) if m else 0, failed


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    print("BASELINE: the suite against the current tree")
    nf, np_, _ = run_suite(REPO)
    print(f"  {np_} passed, {nf} failed")
    if nf:
        print("  baseline is not green; fix that before trusting the mutation results")
        sys.exit(1)

    results = []
    print(f"\nMUTATIONS: reverting each fix in turn ({len(MUTATIONS)} total)")
    for mut in MUTATIONS:
        work = Path(tempfile.mkdtemp(prefix="qa-mut-"))
        clone = work / "repo"
        (clone / "VEGO-AI").mkdir(parents=True)
        for src, dst in (("VEGO-AI/framework", "VEGO-AI/framework"),
                         ("VEGO-AI/tests", "VEGO-AI/tests"),
                         ("src", "src"), ("schemas", "schemas"),
                         ("VEGO-AI/schemas", "VEGO-AI/schemas")):
            if (REPO / src).exists():
                shutil.copytree(REPO / src, clone / dst,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for cfg in ("pyproject.toml", "conftest.py", "pytest.ini", "setup.cfg"):
            if (REPO / cfg).exists():
                shutil.copy2(REPO / cfg, clone / cfg)
        target = clone / mut["file"]
        text = target.read_text(encoding="utf-8")
        mutated, n_sub = re.subn(mut["find"], lambda _m: mut["replace"], text, flags=re.S)
        if n_sub == 0:
            print(f"  {mut['id']:24s} SKIPPED - pattern not found (fix may have moved)")
            results.append({**{k: mut[k] for k in ("id", "guards")},
                            "applied": False, "caught": None, "failing_tests": []})
            shutil.rmtree(work, ignore_errors=True)
            continue
        target.write_text(mutated, encoding="utf-8", newline="\n")
        f, p, failing = run_suite(clone)
        caught = f > 0
        mark = "CAUGHT" if caught else "*** NOT CAUGHT ***"
        print(f"  {mut['id']:24s} {mark:20s} {f} failed, {p} passed"
              + (f"  -> {', '.join(failing[:3])}" if failing else ""))
        results.append({**{k: mut[k] for k in ("id", "guards")}, "applied": True,
                        "caught": caught, "n_failed": f, "n_passed": p,
                        "failing_tests": failing})
        shutil.rmtree(work, ignore_errors=True)

    applied = [r for r in results if r["applied"]]
    caught = [r for r in applied if r["caught"]]
    print(f"\nSUMMARY: {len(caught)}/{len(applied)} reverted fixes were caught by the suite")
    unguarded = [r for r in applied if not r["caught"]]
    if unguarded:
        print("  UNGUARDED FIXES - the suite would not notice these being lost:")
        for r in unguarded:
            print(f"    {r['id']}: {r['guards']}")
    payload = {"baseline_passed": np_, "mutations": results,
               "caught": len(caught), "applied": len(applied),
               "all_guarded": len(unguarded) == 0}
    if args.out:
        args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nwritten: {args.out}")
    sys.exit(0 if not unguarded else 2)


if __name__ == "__main__":
    main()
