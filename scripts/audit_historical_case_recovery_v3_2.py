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
import posixpath
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


def _normalized_collisions(paths: list[str]) -> list[list[str]]:
    """Return case-insensitive POSIX path collisions without changing inputs."""
    groups: dict[str, list[str]] = {}
    for path in paths:
        key = posixpath.normpath(path).casefold()
        groups.setdefault(key, []).append(path)
    return sorted((sorted(values) for values in groups.values() if len(values) > 1), key=lambda v: v[0])


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
            all_names = zf.namelist()
            names = set(all_names)
            prefix = next((n[: n.rfind("dataset/AirTravel/") + len("dataset/AirTravel/")] for n in names if "dataset/AirTravel/" in n), "")
            source_rows = [item for item in source.get("files", []) if isinstance(item, dict) and isinstance(item.get("path"), str)]
            manifest_path_collisions = _normalized_collisions([item["path"] for item in source_rows])
            expected = {item["path"]: item for item in source_rows}
            observed_paths = {n[len(prefix):]: n for n in names if prefix and n.startswith(prefix) and not n.endswith("/")}
            archive_path_collisions = _normalized_collisions(list(observed_paths))
            missing = sorted(set(expected) - set(observed_paths))
            extra = sorted(set(observed_paths) - set(expected))
            mismatched = sorted(path for path, item in expected.items() if path in observed_paths and sha256_bytes(zf.read(observed_paths[path])) != item.get("sha256", "").lower())
            duplicate_members = sorted(name for name in set(all_names) if all_names.count(name) > 1)
            archive_sha = sha256_bytes(archive.read_bytes())
            commit_identity = prefix.startswith(f"text2uml-{UPSTREAM_COMMIT}/")
            result.update({"status": "PASS" if len(expected) == 143 and len(observed_paths) == 143 and commit_identity and not duplicate_members and not manifest_path_collisions and not archive_path_collisions and not missing and not extra and not mismatched and archive_sha == UPSTREAM_SHA256 else "FAIL", "archive_sha256": archive_sha, "archive_url": f"https://github.com/IlKaiser/text2uml/archive/{UPSTREAM_COMMIT}.zip", "upstream_repository": "https://github.com/IlKaiser/text2uml", "commit_identity_status": "PASS" if commit_identity else "FAIL", "manifest_sha256": sha256_bytes(source_manifest.read_bytes()), "expected_file_count": 143, "observed_file_count": len(observed_paths), "matched_count": len(expected) - len(missing) - len(mismatched), "missing_count": len(missing), "extra_count": len(extra), "mismatched_count": len(mismatched), "duplicate_members": duplicate_members, "manifest_path_collisions": manifest_path_collisions, "archive_path_collisions": archive_path_collisions, "missing": missing, "extra": extra, "mismatched": mismatched, "archive_members": sorted(observed_paths.values()), "archive_bytes": {name: sha256_bytes(zf.read(name)) for name in observed_paths.values()}})
    except (OSError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        result["reason"] = str(exc)
    return result


def verify_mapping(upstream: dict[str, Any], amendment: dict[str, Any], runtime_archive: Path | None) -> dict[str, Any]:
    if upstream.get("status") != "PASS" or runtime_archive is None or not runtime_archive.is_file():
        return {"status": "BLOCKED", "reason": "upstream bytes and runtime archive are required for source-to-runtime mapping"}
    mapping = amendment.get("source_to_runtime_mapping") or amendment.get("source_runtime_mapping")
    if not mapping:
        return {"status": "BLOCKED", "reason": "amendment manifest has no source_path/runtime_path mapping"}
    if len(mapping) != 5:
        return {"status": "FAIL", "reason": "mapping count must be exactly five", "mapping_count": len(mapping)}
    source_paths = [str(item.get("source_path", "")) for item in mapping]
    runtime_paths = [str(item.get("runtime_path", "")) for item in mapping]
    if len(set(source_paths)) != 5 or len(set(runtime_paths)) != 5:
        return {"status": "FAIL", "reason": "duplicate source or runtime mapping path", "mapping_count": len(mapping)}
    if source_paths.count("description.md") != 1 or sum(path.startswith("result_one_") for path in source_paths) != 4:
        return {"status": "FAIL", "reason": "mapping requires description.md plus four result_one candidate sources", "mapping_count": len(mapping)}
    if sum(path == "domain_description/description.md" for path in runtime_paths) != 1 or sum(path.startswith("candidate_models/") for path in runtime_paths) != 4:
        return {"status": "FAIL", "reason": "mapping requires one domain description and four candidate runtime paths", "mapping_count": len(mapping)}
    roles = [str(item.get("role", "")) for item in amendment.get("runtime_files", [])]
    expected_transforms = {"BYTE_IDENTICAL_RELOCATION", "BYTE_IDENTICAL_RELOCATION_AND_CASE_ID_PREFIX"}
    for item in mapping:
        if str(item.get("transformation", "")) not in expected_transforms or item.get("byte_transformation") != "NONE":
            return {"status": "FAIL", "reason": "unexpected mapping transformation", "mapping_count": len(mapping)}
    if roles.count("domain_description") != 1 or roles.count("candidate_model") != 4:
        return {"status": "FAIL", "reason": "mapping requires one domain description and four candidate models", "mapping_count": len(mapping)}
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
                if source_hash != target_hash or target_hash != str(item.get("sha256", "")).lower() or len(runtime_zip.read(target_name)) != int(item.get("bytes", -1)):
                    mismatched.append(source)
            source_collisions = _normalized_collisions(source_paths)
            runtime_collisions = _normalized_collisions(runtime_paths)
            status = "PASS" if len(mapping) == 5 and len(set(source_paths)) == 5 and len(set(runtime_paths)) == 5 and not source_collisions and not runtime_collisions and not missing and not mismatched else "FAIL"
            return {"status": status, "mapping_count": len(mapping), "source_path_count": len(set(source_paths)), "runtime_path_count": len(set(runtime_paths)), "source_path_collisions": source_collisions, "runtime_path_collisions": runtime_collisions, "missing": sorted(missing), "mismatched": sorted(mismatched), "byte_identical": status == "PASS"}
    except (OSError, zipfile.BadZipFile, KeyError, TypeError) as exc:
        return {"status": "FAIL", "reason": str(exc)}


def verify_runtime_pack(runtime_archive: Path | None, amendment: dict[str, Any], config: Path | None = None) -> dict[str, Any]:
    if runtime_archive is None or not runtime_archive.is_file():
        return {"status": "BLOCKED", "reason": "exact runtime archive unavailable", "expected_count": len(amendment.get("runtime_files", []))}
    if not amendment:
        return {"status": "BLOCKED", "reason": "verified amendment manifest unavailable"}
    if config is None or not config.is_file():
        return {"status": "BLOCKED", "reason": "mandatory cd_airtravel runtime configuration unavailable", "expected_count": len(amendment.get("runtime_files", []))}
    try:
        with zipfile.ZipFile(runtime_archive) as zf:
            all_names = [name for name in zf.namelist() if not name.endswith("/")]
            names = set(all_names)
            expected = {item["path"]: item for item in amendment.get("runtime_files", [])}
            observed = {name.split("runtime_input/", 1)[-1]: name for name in all_names}
            observed_collisions = _normalized_collisions(list(observed))
            missing = sorted(set(expected) - set(observed))
            extra = sorted(set(observed) - set(expected))
            duplicate_members = sorted(name for name in set(all_names) if all_names.count(name) > 1)
            mismatched = sorted(path for path, item in expected.items() if path in observed and (len(zf.read(observed[path])) != int(item.get("bytes", -1)) or sha256_bytes(zf.read(observed[path])) != str(item.get("sha256", "")).lower()))
            references_visible = sorted(name for name in names if "reference_only/" in name)
            cfg = json.loads(config.read_text(encoding="utf-8"))
            config_status = "PASS" if (
                cfg.get("setting_id") == "cd_airtravel"
                and cfg.get("corpus_id") == "text2uml_airtravel_253b26dc"
                and cfg.get("provider_execution_enabled") is False
                and cfg.get("description_path") == "domain_description/description.md"
                and cfg.get("candidate_models_dir") == "candidate_models"
                and "reference_only" not in json.dumps(cfg)
                and sorted(cfg.get("runtime_files", [])) == sorted(expected)
                and not any(str(path).startswith("reference_only/") for path in cfg.get("runtime_files", []))
            ) else "FAIL"
            status = "PASS" if len(expected) == 5 and len(observed) == 5 and not observed_collisions and not missing and not extra and not duplicate_members and not mismatched and not references_visible and config_status == "PASS" else "FAIL"
            return {"status": status, "expected_count": len(expected), "observed_runtime_count": len(observed), "matched_count": len(expected) - len(missing) - len(mismatched), "missing": missing, "extra": extra, "duplicate_members": duplicate_members, "normalized_path_collisions": observed_collisions, "mismatched": mismatched, "reference_files_visible": references_visible, "configuration_status": config_status}
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "reason": str(exc)}


def fake_preflight(runtime_status: str) -> dict[str, Any]:
    if runtime_status != "PASS":
        return {"status": "BLOCKED_NOT_RUN", "reason": "exact five-file runtime verification did not pass", "provider_calls": 0}
    return {"status": "BLOCKED_PROTECTED_CONFIG", "reason": "exact cd_airtravel orchestration requires protected runtime authorization", "provider_calls": 0}


def historical_only(backup: Path, v2_manifest: Path | None, audit_base_sha: str) -> dict[str, Any]:
    """Build the historical evidence layer without invoking v3.1's AirTravel path."""
    v31 = _load_v31()
    v3 = v31._load_v3()
    result = v3.audit(backup, v2_manifest)
    result["audit_version"] = "historical-case-recovery-v3.2.1-erratum"
    result["audit_base_sha"] = audit_base_sha
    result["evidence_parent_sha"] = "36602e41a3a7ccec52a300d9244f3afe4702153f"
    result.pop("airtravel", None)
    result.pop("published_count_reference", None)
    result["duplicate_id_excess"] = v31._duplicate_correction(result)
    for row in result["per_setting"].values():
        row["duplicate_id_excess_rows"] = row.pop("duplicate_version_rows")
    result["executability_by_setting"] = v31._executability(backup)
    result["instrumentation"] = v31._instrumentation_receipt()
    result["call_bound"] = {"N": 4, "minimum": 16, "retained_worst_case": 326, "status": "STATIC_ONLY"}
    result["api_cost"] = "TO BE MEASURED"
    result["protected_authorization"] = "NOT_SELF_AUTHORIZED"
    return result


def audit_v32(backup: Path, v2_manifest: Path | None, *, amendment_ref: str, amendment_manifest_path: str, amendment_sha256: str, upstream_archive: Path | None, source_manifest: Path | None, runtime_archive: Path | None, runtime_config: Path | None, audit_base_sha: str) -> dict[str, Any]:
    result = historical_only(backup, v2_manifest, audit_base_sha)
    manifest_receipt = resolve_manifest(amendment_ref, amendment_manifest_path, amendment_sha256)
    amendment = manifest_receipt.get("manifest", {}) if manifest_receipt.get("status") == "PASS" else {}
    upstream = verify_upstream(upstream_archive, source_manifest)
    mapping = verify_mapping(upstream, amendment, runtime_archive)
    runtime = verify_runtime_pack(runtime_archive, amendment, runtime_config)
    result["airtravel_manifest_verification"] = {k: v for k, v in manifest_receipt.items() if k != "manifest"}
    result["airtravel_source_verification"] = upstream
    result["airtravel_source_runtime_mapping"] = mapping
    result["airtravel_runtime_pack_verification"] = runtime
    result["airtravel_fake_preflight"] = fake_preflight(runtime.get("status", "BLOCKED"))
    result["airtravel_materialization"] = {
        "upstream_archive_sha256": upstream.get("archive_sha256", UPSTREAM_SHA256),
        "runtime_archive_sha256": sha256_bytes(runtime_archive.read_bytes()) if runtime_archive and runtime_archive.is_file() else None,
        "runtime_config_sha256": sha256_bytes(runtime_config.read_bytes()) if runtime_config and runtime_config.is_file() else None,
        "classification": "DERIVED_BYTE_IDENTICAL_RUNTIME_PREPARATION" if runtime.get("status") == "PASS" and mapping.get("byte_identical") else "BLOCKED",
    }
    result["gate_tracks"] = {"historical_cheers_parkwise": "DATA_NO_GO", "synthetic_gap_fill": "ZERO_AUTHORIZED", "airtravel_public_external": "BLOCKED"}
    result["paid_run_authorization"] = "ABSENT"
    return result


def write_outputs(result: dict[str, Any], output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    safe_keys = ("audit_version", "audit_base_sha", "evidence_parent_sha", "backup_sha256", "archive_entry_count", "normalized_model_count", "file_level_match", "duplicate_id_excess", "airtravel_manifest_verification", "airtravel_source_verification", "airtravel_source_runtime_mapping", "airtravel_runtime_pack_verification", "airtravel_fake_preflight", "gate_tracks", "paid_run_authorization", "provider_calls", "experiment_calls", "detector_v1_runs")
    (output_root / "backup-evidence-receipt.json").write_text(json.dumps({k: result[k] for k in safe_keys if k in result}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_root / "historical-load-universe.json").write_text(json.dumps({"per_setting": result["per_setting"], "ranking_lengths": result["ranking_lengths"], "duplicate_id_excess": result["duplicate_id_excess"]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_root / "airtravel-materialization-receipt.json").write_text(json.dumps(result["airtravel_materialization"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Strip obsolete v3.1 AirTravel receipts (including the superseded
    # branch/commit) from the successor output.  The v3.2 receipts above are
    # the only AirTravel authority consumed by this audit.
    binding = dict(result)
    binding.pop("airtravel_manifest_provenance", None)
    binding.pop("airtravel_runtime_verification", None)
    (output_root / "provenance-binding-summary.json").write_text(json.dumps(binding, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def gate_exit_code(result: dict[str, Any]) -> int:
    """Non-zero for any failed/blocked preflight gate; never authorizes execution."""
    required = ("airtravel_manifest_verification", "airtravel_source_verification", "airtravel_source_runtime_mapping", "airtravel_runtime_pack_verification", "airtravel_fake_preflight")
    return 0 if all(result.get(key, {}).get("status") == "PASS" for key in required) else 2


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
    parser.add_argument("--runtime-config", type=Path)
    parser.add_argument("--audit-base-sha", required=True)
    args = parser.parse_args()
    result = audit_v32(args.backup, args.v2_manifest, amendment_ref=args.amendment_ref, amendment_manifest_path=args.amendment_manifest_path, amendment_sha256=args.amendment_manifest_sha256, upstream_archive=args.upstream_archive, source_manifest=args.source_manifest, runtime_archive=args.runtime_archive, runtime_config=args.runtime_config, audit_base_sha=args.audit_base_sha)
    write_outputs(result, args.output_root)
    print(json.dumps({"audit_version": result["audit_version"], "file_level_match": result["file_level_match"], "manifest_status": result["airtravel_manifest_verification"]["status"], "source_status": result["airtravel_source_verification"]["status"], "runtime_status": result["airtravel_runtime_pack_verification"]["status"]}, sort_keys=True))
    return gate_exit_code(result)


if __name__ == "__main__":
    raise SystemExit(main())
