"""External, fail-closed gate for a future Study 1 provider run.

The protected orchestrator is not edited.  This entry point validates all
preconditions before a client factory can be called.  In the current review
state it necessarily blocks because no human authorization, exact model, or
green CI receipt exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # Script execution (``python scripts/...``) and package-style tests.
    from verify_text2uml_airtravel_runtime import verify_pack
except ModuleNotFoundError:  # pragma: no cover - import mode dependent
    from scripts.verify_text2uml_airtravel_runtime import verify_pack


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evaluate_gate(
    *,
    config_path: Path,
    stage_root: Path,
    amendment_manifest: Path,
    current_commit: str,
    authorization_path: Path | None,
    exact_model: str | None,
    max_concurrent_cases: int | None,
    call_cap: int | None,
    ci_green: bool,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    pack = verify_pack(config_path, stage_root, amendment_manifest)
    checks.extend(pack.get("checks", []))
    checks.append({"name": "runtime_pack", "status": "PASS" if pack.get("status") == "PASS" else "BLOCKED"})
    checks.append({"name": "exact_model_configured", "status": "PASS" if exact_model else "BLOCKED"})
    checks.append({"name": "max_concurrent_cases_frozen", "status": "PASS" if max_concurrent_cases and max_concurrent_cases > 0 else "BLOCKED"})
    checks.append({"name": "provider_call_cap_configured", "status": "PASS" if call_cap and call_cap > 0 else "BLOCKED"})
    checks.append({"name": "ci_green", "status": "PASS" if ci_green else "BLOCKED"})
    authorization: dict[str, Any] | None = None
    if authorization_path and authorization_path.is_file():
        try:
            authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            authorization = None
    expires_at = authorization.get("expires_at") if authorization else None
    try:
        expiry = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00")) if expires_at else None
        expiry_ok = bool(expiry and expiry > datetime.now(timezone.utc))
    except ValueError:
        expiry_ok = False
    auth_ok = bool(authorization and authorization.get("authorized") is True
                   and authorization.get("commit_sha") == current_commit
                   and expiry_ok)
    checks.append({"name": "hash_bound_human_authorization", "status": "PASS" if auth_ok else "BLOCKED"})
    checks.append({"name": "current_code_commit", "status": "PASS" if len(current_commit) == 40 else "BLOCKED"})
    return {
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "BLOCKED",
        "provider_call_permitted": False,
        "provider_client_constructed": False,
        "current_commit": current_commit,
        "authorization_sha256": _sha256(authorization_path) if authorization_path and authorization_path.is_file() else None,
        "checks": checks,
    }


def run_if_authorized(gate: dict[str, Any], client_factory: Callable[[], Any]) -> Any:
    """Construct a provider client only after every gate check passes."""
    if gate.get("status") != "PASS":
        raise RuntimeError("Study 1 execution blocked before provider-client construction")
    return client_factory()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--stage-root", type=Path, required=True)
    parser.add_argument("--amendment-manifest", type=Path, required=True)
    parser.add_argument("--current-commit", required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--exact-model")
    parser.add_argument("--max-concurrent-cases", type=int)
    parser.add_argument("--call-cap", type=int)
    parser.add_argument("--ci-green", action="store_true")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = evaluate_gate(
        config_path=args.config,
        stage_root=args.stage_root,
        amendment_manifest=args.amendment_manifest,
        current_commit=args.current_commit,
        authorization_path=args.authorization,
        exact_model=args.exact_model,
        max_concurrent_cases=args.max_concurrent_cases,
        call_cap=args.call_cap,
        ci_green=args.ci_green,
    )
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
