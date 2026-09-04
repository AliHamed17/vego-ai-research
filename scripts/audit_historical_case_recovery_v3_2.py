"""AirTravel evidence reconciliation and technical preflight v3.2.

This successor does not rewrite v3/v3.1.  The amendment ref, manifest path,
and manifest hash are explicit inputs; upstream/runtime verification fails
closed when bytes are unavailable.  No provider or real experiment is called.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
V31 = ROOT / "scripts" / "audit_historical_case_recovery_v3_1.py"
UPSTREAM_SHA256 = "8cf82e2ab2d2ce3da9a7ec4165e760ae1e0d9af14468f5aa2a3883037d8da701"
UPSTREAM_COMMIT = "253b26dc704d523209a5cba79686f8f7fab57d63"


def _load_v31():
    spec = importlib.util.spec_from_file_location("audit_v31", V31)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v3.1 audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve_manifest(ref: str, manifest_path: str, expected_sha256: str) -> dict[str, Any]:
    try:
        resolved = subprocess.check_output(["git", "rev-parse", ref], text=True).strip()
        raw = subprocess.check_output(["git", "show", f"{resolved}:{manifest_path}"])
    except (OSError, subprocess.CalledProcessError) as exc:
        return {"status": "BLOCKED", "reason": str(exc), "ref": ref, "manifest_path": manifest_path}
    observed = sha256_bytes(raw)
    if observed.lower() != expected_sha256.lower():
        return {"status": "FAIL", "reason": "manifest SHA-256 mismatch", "resolved_commit": resolved, "observed_sha256": observed, "expected_sha256": expected_sha256}
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "reason": str(exc), "resolved_commit": resolved, "observed_sha256": observed}
    return {"status": "PASS", "resolved_commit": resolved, "manifest_sha256": observed, "manifest": payload}


def verify_upstream(archive: Path | None, source_manifest: Path | None) -> dict[str, Any]:
    result: dict[str, Any] = {"status": "BLOCKED", "expected_archive_sha256": UPSTREAM_SHA256, "expected_upstream_commit": UPSTREAM_COMMIT}
    if archive is None or source_manifest is None or not archive.is_file() or not source_manifest.is_file():
        result["reason"] = "pinned Text2UML archive or source manifest unavailable"
        return result
    try:
        source = json.loads(source_manifest.read_text(encoding="utf-8"))
        with zipfile.ZipFile(archive) as zf:
            names = set(zf.namelist())
            prefix = next((n[: n.rfind("dataset/AirTravel/") + len("dataset/AirTravel/")] for n in names if "dataset/AirTravel/" in n), "")
            expected = {item["path"]: item for item in source.get("files", [])}
            observed_paths = {n[len(prefix):]: n for n in names if prefix and n.startswith(prefix) and not n.endswith("/")}
            missing = sorted(set(expected) - set(observed_paths))
            extra = sorted(set(observed_paths) - set(expected))
            mismatched = sorted(path for path, item in expected.items() if path in observed_paths and sha256_bytes(zf.read(observed_paths[path])) != item.get("sha256", "").lower())
            result.update({"status": "PASS" if not missing and not extra and not mismatched and sha256_bytes(archive.read_bytes()) == UPSTREAM_SHA256 else "FAIL", "archive_sha256": sha256_bytes(archive.read_bytes()), "manifest_sha256": sha256_bytes(source_manifest.read_bytes()), "matched_count": len(expected) - len(missing) - len(mismatched), "missing_count": len(missing), "extra_count": len(extra), "mismatched_count": len(mismatched), "missing": missing, "extra": extra, "mismatched": mismatched, "archive_members": sorted(observed_paths.values()), "archive_bytes": {name: sha256_bytes(zf.read(name)) for name in observed_paths.values()}})
    except (OSError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        result["reason"] = str(exc)
    return result


def verify_mapping(upstream: dict[str, Any], amendment: dict[str, Any], runtime_archive: Path | None) -> dict[str, Any]:
    if upstream.get("status") != "PASS" or runtime_archive is None or not runtime_archive.is_file():
        return {"status": "BLOCKED", "reason": "upstream bytes and runtime archive are required for source-to-runtime mapping"}
    mapping = amendment.get("source_to_runtime_mapping") or amendment.get("source_runtime_mapping")
    if not mapping:
        return {"status": "BLOCKED", "reason": "amendment manifest has no source_path/runtime_path mapping"}
    try:
        with zipfile.ZipFile(runtime_archive) as runtime_zip:
            runtime_names = [n for n in runtime_zip.namelist() if not n.endswith("/")]
            missing: list[str] = []
            mismatched: list[str] = []
            for item in mapping:
                source = str(item["source_path"])
                target = str(item["runtime_path"])
                source_name = next((n for n in upstream.get("archive_members", []) if n.endswith("/" + source) or n == source), None)
                if source_name is None:
                    missing.append(source)
                    continue
                target_name = next((n for n in runtime_names if n == target or n.endswith("/" + target)), None)
                if target_name is None:
                    missing.append(target)
                    continue
                source_hash = upstream["archive_bytes"][source_name]
                target_hash = sha256_bytes(runtime_zip.read(target_name))
                if source_hash != target_hash or target_hash != str(item.get("sha256", "")).lower():
                    mismatched.append(source)
            return {"status": "PASS" if not missing and not mismatched else "FAIL", "mapping_count": len(mapping), "missing": sorted(missing), "mismatched": sorted(mismatched), "byte_identical": not mismatched}
    except (OSError, zipfile.BadZipFile, KeyError, TypeError) as exc:
        return {"status": "FAIL", "reason": str(exc)}


def verify_runtime_pack(runtime_archive: Path | None, amendment: dict[str, Any], config: Path | None = None) -> dict[str, Any]:
    if runtime_archive is None or not runtime_archive.is_file():
        return {"status": "BLOCKED", "reason": "exact runtime archive unavailable", "expected_count": len(amendment.get("runtime_files", []))}
    if not amendment:
        return {"status": "BLOCKED", "reason": "verified amendment manifest unavailable"}
    try:
        with zipfile.ZipFile(runtime_archive) as zf:
            names = {name for name in zf.namelist() if not name.endswith("/")}
            expected = {item["path"]: item for item in amendment.get("runtime_files", [])}
            observed = {name.split("runtime_input/", 1)[-1]: name for name in names if "runtime_input/" in name or name in {item["path"] for item in amendment.get("runtime_files", [])}}
            missing = sorted(set(expected) - set(observed))
            extra = sorted(set(observed) - set(expected))
            mismatched = sorted(path for path, item in expected.items() if path in observed and sha256_bytes(zf.read(observed[path])) != str(item.get("sha256", "")).lower())
            references_visible = sorted(name for name in names if "reference_only/" in name and "runtime_input/" in name)
            config_status = "NOT_CHECKED"
            if config is not None and config.is_file():
                cfg = json.loads(config.read_text(encoding="utf-8"))
                text = json.dumps(cfg)
                config_status = "PASS" if "reference_only" not in text and "description.md" in text and "candidate_models" in text else "FAIL"
            return {"status": "PASS" if not missing and not extra and not mismatched and not references_visible else "FAIL", "expected_count": len(expected), "observed_runtime_count": len(observed), "matched_count": len(expected) - len(missing) - len(mismatched), "missing": missing, "extra": extra, "mismatched": mismatched, "reference_files_visible": references_visible, "configuration_status": config_status}
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "reason": str(exc)}


def fake_preflight(runtime_status: str) -> dict[str, Any]:
    if runtime_status != "PASS":
        return {"status": "BLOCKED_NOT_RUN", "reason": "exact five-file runtime verification did not pass", "provider_calls": 0}
    return {"status": "BLOCKED_PROTECTED_CONFIG", "reason": "exact cd_airtravel orchestration requires protected runtime authorization", "provider_calls": 0}


def audit_v32(backup: Path, v2_manifest: Path | None, *, amendment_ref: str, amendment_manifest_path: str, amendment_sha256: str, upstream_archive: Path | None, source_manifest: Path | None, runtime_archive: Path | None, audit_base_sha: str) -> dict[str, Any]:
    v31 = _load_v31()
    result = v31.audit_v31(backup, v2_manifest, audit_base_sha=audit_base_sha)
    result["audit_version"] = "historical-case-recovery-v3.2-airtravel-erratum"
    # Remove the inherited v3/v3.1 hard-coded AirTravel object entirely.
    result.pop("airtravel", None)
    manifest_receipt = resolve_manifest(amendment_ref, amendment_manifest_path, amendment_sha256)
    amendment = manifest_receipt.get("manifest", {}) if manifest_receipt.get("status") == "PASS" else {}
    upstream = verify_upstream(upstream_archive, source_manifest)
    mapping = verify_mapping(upstream, amendment, runtime_archive)
    runtime = verify_runtime_pack(runtime_archive, amendment)
    result["airtravel_manifest_verification"] = {k: v for k, v in manifest_receipt.items() if k != "manifest"}
    result["airtravel_source_verification"] = upstream
    result["airtravel_source_runtime_mapping"] = mapping
    result["airtravel_runtime_pack_verification"] = runtime
    result["airtravel_fake_preflight"] = fake_preflight(runtime.get("status", "BLOCKED"))
    result["gate_tracks"] = {"historical_cheers_parkwise": "DATA_NO_GO", "synthetic_gap_fill": "ZERO_AUTHORIZED", "airtravel_public_external": "BLOCKED"}
    result["paid_run_authorization"] = "ABSENT"
    return result


def write_outputs(result: dict[str, Any], output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    safe_keys = ("audit_version", "audit_base_sha", "evidence_parent_sha", "backup_sha256", "archive_entry_count", "normalized_model_count", "file_level_match", "duplicate_id_excess", "airtravel_manifest_verification", "airtravel_source_verification", "airtravel_source_runtime_mapping", "airtravel_runtime_pack_verification", "airtravel_fake_preflight", "gate_tracks", "paid_run_authorization", "provider_calls", "experiment_calls", "detector_v1_runs")
    (output_root / "backup-evidence-receipt.json").write_text(json.dumps({k: result[k] for k in safe_keys if k in result}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_root / "historical-load-universe.json").write_text(json.dumps({"per_setting": result["per_setting"], "ranking_lengths": result["ranking_lengths"], "duplicate_id_excess": result["duplicate_id_excess"]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Strip obsolete v3.1 AirTravel receipts (including the superseded
    # branch/commit) from the successor output.  The v3.2 receipts above are
    # the only AirTravel authority consumed by this audit.
    binding = dict(result)
    binding.pop("airtravel_manifest_provenance", None)
    binding.pop("airtravel_runtime_verification", None)
    (output_root / "provenance-binding-summary.json").write_text(json.dumps(binding, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", type=Path, required=True)
    parser.add_argument("--v2-manifest", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--amendment-ref", required=True)
    parser.add_argument("--amendment-manifest-path", required=True)
    parser.add_argument("--amendment-manifest-sha256", required=True)
    parser.add_argument("--upstream-archive", type=Path)
    parser.add_argument("--source-manifest", type=Path)
    parser.add_argument("--runtime-archive", type=Path)
    parser.add_argument("--audit-base-sha", required=True)
    args = parser.parse_args()
    result = audit_v32(args.backup, args.v2_manifest, amendment_ref=args.amendment_ref, amendment_manifest_path=args.amendment_manifest_path, amendment_sha256=args.amendment_manifest_sha256, upstream_archive=args.upstream_archive, source_manifest=args.source_manifest, runtime_archive=args.runtime_archive, audit_base_sha=args.audit_base_sha)
    write_outputs(result, args.output_root)
    print(json.dumps({"audit_version": result["audit_version"], "file_level_match": result["file_level_match"], "manifest_status": result["airtravel_manifest_verification"]["status"], "source_status": result["airtravel_source_verification"]["status"], "runtime_status": result["airtravel_runtime_pack_verification"]["status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
