#!/usr/bin/env python3
"""Read-only environment and configuration health check for VEGO-AI."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PACKAGES = {
    "openai": "1.109.1",
    "chardet": "7.4.3",
    "jsonschema": "4.26.0",
    "python-docx": "1.2.0",
    "Pillow": "12.3.0",
    "pypdf": "6.15.0",
    "pytest": "9.0.3",
    "ruff": "0.15.16",
    "pip-audit": "2.10.1",
}


def _run(*command: str) -> tuple[bool, str]:
    try:
        # Commands are assembled exclusively from repository-owned constants.
        result = subprocess.run(  # noqa: S603
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=45,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    detail = (result.stdout or result.stderr).strip().splitlines()
    return result.returncode == 0, detail[-1] if detail else f"exit={result.returncode}"


def inspect(require_controlled: bool = False) -> dict[str, Any]:
    checks: dict[str, dict[str, Any]] = {}
    py_ok = sys.version_info >= (3, 10)
    checks["python"] = {
        "passed": py_ok,
        "detail": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }
    for package, expected in EXPECTED_PACKAGES.items():
        try:
            installed = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            installed = None
        checks[f"dependency:{package}"] = {
            "passed": installed == expected,
            "detail": installed or "missing",
            "expected": expected,
        }

    for tool in ("git", "node", "npm"):
        checks[f"tool:{tool}"] = {
            "passed": shutil.which(tool) is not None,
            "detail": shutil.which(tool) or "missing",
        }

    for relative in (
        "VEGO-AI/framework/run_config.json",
        "VEGO-AI/eval/eval_config.json",
    ):
        value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        key = value.get("api_key")
        checks[f"config:{relative}:api_key"] = {
            "passed": key in (None, ""),
            "detail": "environment-only" if key in (None, "") else "plaintext value rejected",
        }
        checks[f"config:{relative}:model"] = {
            "passed": value.get("model") == "gpt-4o",
            "detail": value.get("model"),
            "expected": "gpt-4o",
        }

    runtime = json.loads(
        (ROOT / "configs" / "hlayer-runtime.json").read_text(encoding="utf-8")
    )
    runtime_schema = json.loads(
        (ROOT / "schemas" / "hlayer-runtime-config-v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    runtime_schema_errors = list(
        jsonschema.Draft202012Validator(runtime_schema).iter_errors(runtime)
    )
    h_layer = runtime.get("h_layer") or {}
    checks["config:hlayer-runtime"] = {
        "passed": (
            not runtime_schema_errors
            and
            h_layer.get("architecture_mode") in {"legacy", "unified", "parity"}
            and h_layer.get("contract_version") == "1.0"
            and h_layer.get("interaction_log_mode")
            in {"off", "metadata_only", "full_content"}
            and (h_layer.get("interaction_log") or {}).get("retention_days") == 30
            and (h_layer.get("interaction_log") or {}).get("redaction_enabled") is True
            and (h_layer.get("interaction_log") or {}).get("full_content_local_only")
            is True
        ),
        "detail": (
            h_layer
            if not runtime_schema_errors
            else "; ".join(error.message for error in runtime_schema_errors)
        ),
    }

    smoke_commands = {
        "cli:orchestrator": (
            sys.executable,
            "VEGO-AI/framework/orchestrator.py",
            "--help",
        ),
        "cli:evaluator": (
            sys.executable,
            "VEGO-AI/eval/evaluator.py",
            "--help",
        ),
        "cli:review-queue": (
            sys.executable,
            "VEGO-AI/framework/human_review_queue.py",
            "--help",
        ),
        "cli:feedback": (
            sys.executable,
            "VEGO-AI/framework/human_feedback_manager.py",
            "--help",
        ),
        "cli:memory": (
            sys.executable,
            "VEGO-AI/framework/human_judgment_memory.py",
            "--help",
        ),
        "cli:advice": (
            sys.executable,
            "VEGO-AI/framework/memory_advisor.py",
            "--help",
        ),
        "cli:comparison": (
            sys.executable,
            "VEGO-AI/framework/memory_informed_classifier.py",
            "--help",
        ),
    }
    for name, command in smoke_commands.items():
        passed, detail = _run(*command)
        checks[name] = {"passed": passed, "detail": detail}
    browser_ok, browser_detail = _run(
        shutil.which("node") or "node",
        "-e",
        "require('playwright'); console.log('playwright import ok')",
    )
    checks["browser:playwright"] = {
        "passed": browser_ok,
        "detail": browser_detail,
    }

    controlled = ROOT / "VEGO-AI" / "eval_output"
    controlled_files = list(controlled.glob("*/agentD_variability_classes*.json"))
    checks["controlled:agent4-outputs"] = {
        "passed": bool(controlled_files) if require_controlled else True,
        "detail": f"{len(controlled_files)} setting output file(s)",
        "required": require_controlled,
    }
    return {
        "doctor": "vego-ai-environment-v1",
        "checks": checks,
        "passed": all(check["passed"] for check in checks.values()),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-controlled", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = inspect(require_controlled=args.require_controlled)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for name, check in result["checks"].items():
            marker = "PASS" if check["passed"] else "FAIL"
            print(f"{marker}: {name}: {check['detail']}")
        print(f"doctor_status: {'PASS' if result['passed'] else 'FAIL'}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
