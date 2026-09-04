"""Fail-closed verification for the frozen Text2UML/AirTravel runtime pack.

This verifier never runs VEGO-AI and never contacts a provider.  It requires an
explicit amendment manifest (the byte-level authority for v1.0.2); without one
it returns a blocking result instead of guessing from the observed pack.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _runtime_files(runtime_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not runtime_root.is_dir():
        return rows
    for path in sorted(p for p in runtime_root.rglob("*") if p.is_file()):
        rel = path.relative_to(runtime_root).as_posix()
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256(path)})
    return rows


def verify_pack(config_path: Path, stage_root: Path, amendment_manifest: Path) -> dict[str, Any]:
    """Verify a pack against the supplied amendment, or fail closed."""
    result: dict[str, Any] = {
        "status": "BLOCKED",
        "provider_call_made": False,
        "checks": [],
    }
    if not amendment_manifest.is_file():
        result["checks"].append({
            "name": "v1.0.2_amendment_manifest",
            "status": "BLOCKED",
            "reason": "Claude v1.0.2 byte-level amendment manifest was not supplied",
        })
        return result
    try:
        amendment = json.loads(amendment_manifest.read_text(encoding="utf-8"))
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result["checks"].append({"name": "manifest_parse", "status": "FAIL", "reason": str(exc)})
        return result

    settings = config.get("settings", [])
    if len(settings) != 1:
        result["checks"].append({"name": "single_setting", "status": "FAIL", "reason": f"expected one setting, got {len(settings)}"})
        return result
    setting = settings[0]
    expected_setting = amendment.get("setting_id")
    expected_corpus = amendment.get("corpus_id")
    ids_ok = setting.get("setting_id") == expected_setting and setting.get("corpus_id") == expected_corpus
    distinct_ok = setting.get("setting_id") != setting.get("corpus_id")
    result["checks"].append({"name": "setting_and_corpus_identity", "status": "PASS" if ids_ok and distinct_ok else "FAIL"})

    runtime_root = stage_root / "prepared" / "AirTravel" / "runtime_input"
    observed = _runtime_files(runtime_root)
    expected = amendment.get("runtime_files", [])
    def normalise(rows: list[dict[str, Any]]) -> list[tuple[str, int, str]]:
        return sorted(
            (str(row.get("path")), int(row.get("bytes", -1)), str(row.get("sha256", "")).lower())
            for row in rows
        )
    bytes_ok = normalise(observed) == normalise(expected)
    result["checks"].append({"name": "runtime_bytes", "status": "PASS" if bytes_ok else "FAIL", "observed_count": len(observed), "expected_count": len(expected)})

    runtime_resolved = runtime_root.resolve()
    references = stage_root / "prepared" / "AirTravel" / "reference_only"
    refs_ok = references.is_dir() and runtime_resolved not in references.resolve().parents
    refs_ok = refs_ok and not any(path.is_file() for path in runtime_root.rglob("plantuml*.txt"))
    result["checks"].append({"name": "reference_separation", "status": "PASS" if refs_ok else "FAIL"})

    provider_ok = config.get("provider_run_permitted") is False and setting.get("provider_run_permitted") is False
    result["checks"].append({"name": "provider_disabled", "status": "PASS" if provider_ok else "FAIL"})
    result["status"] = "PASS" if all(check["status"] == "PASS" for check in result["checks"]) else "BLOCKED"
    result["amendment_version"] = amendment.get("amendment_version")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--stage-root", type=Path, required=True)
    parser.add_argument("--amendment-manifest", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = verify_pack(args.config, args.stage_root, args.amendment_manifest)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
