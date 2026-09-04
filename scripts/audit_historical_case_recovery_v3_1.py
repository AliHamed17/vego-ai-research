"""Offline v3.1 successor/erratum for the historical project-backup audit.

The implementation deliberately leaves v3 intact.  It reuses v3's byte-safe
inventory, then adds corrected duplicate terminology, measured read/wrapper
status, fail-closed AirTravel verification, and a local fake-provider observer
receipt.  No provider, Detector-v1, experiment, or synthetic generation is
performed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "scripts" / "audit_historical_case_recovery_v3.py"
EXPECTED_BACKUP_SHA256 = "8d37f3adb28e70b09bd095e7cf27b055c8488369aecd3628960a148d11b5b384"
CLAUDE_BRANCH = "origin/review/study1-airtravel-v102"
CLAUDE_COMMIT = "8561aa0b9e241255f0f2346ac85180758f3ccb53"
CLAUDE_MANIFEST_PATH = "docs/research/phd-proposal/text2uml-airtravel/amendment-manifest-v1.0.2.json"
CLAUDE_MANIFEST_SHA256 = "a4097902494f313594ab0b24e843280f6a1041889d72ddd2c53412353191c791"
SETTING_DIRS = {"ucd_pw": "UCD_PW_models", "cd_pw": "CD_PW_models", "ucd_ch": "UCD_Ch_models", "cd_ch": "CD_Ch_models"}


def _load_v3():
    spec = importlib.util.spec_from_file_location("audit_v3", V3)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v3 audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalized(path: str) -> tuple[str, str] | None:
    parts = path.replace("\\", "/").split("/")
    for setting, directory in SETTING_DIRS.items():
        if len(parts) >= 5 and parts[:3] == ["VEGO-AI", "System", "models"] and parts[3] == directory and not path.endswith("/"):
            return setting, (Path("VEGO-AI") / "models" / directory / Path(*parts[4:])).as_posix()
    return None


def _read_runtime_bytes(raw: bytes) -> tuple[str, str, str]:
    """Mirror evaluator._read_text's actual decoding contract without parsing PlantUML."""
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            text = raw.decode(encoding).strip()
            break
        except UnicodeDecodeError:
            text = None
    if text is None:
        try:
            import chardet
            encoding = chardet.detect(raw).get("encoding") or "windows-1252"
            text = raw.decode(encoding, errors="replace").strip()
        except Exception:
            return "FAIL", "NOT_CHECKED", "FAIL"
    wrapper = "PASS" if text.startswith("@startuml") and text.endswith("@enduml") else "FAIL"
    loader = "PASS" if text else "FAIL"
    return "PASS", wrapper, loader


def _executability(backup: Path) -> dict[str, Any]:
    by_setting: dict[str, Counter[str]] = {setting: Counter() for setting in SETTING_DIRS}
    with zipfile.ZipFile(backup) as zf:
        for name in zf.namelist():
            normalized = _normalized(name)
            if normalized is None:
                continue
            setting, _ = normalized
            decode, wrapper, loader = _read_runtime_bytes(zf.read(name))
            by_setting[setting]["files"] += 1
            by_setting[setting]["decode_read_pass"] += decode == "PASS"
            by_setting[setting]["wrapper_pass"] += wrapper == "PASS"
            by_setting[setting]["offline_loader_pass"] += loader == "PASS"
    return {
        setting: {
            "decode_read_status": "PASS" if counts["decode_read_pass"] == counts["files"] else "PARTIAL",
            "decode_read_pass_files": counts["decode_read_pass"],
            "plantuml_wrapper_status": "PASS" if counts["wrapper_pass"] == counts["files"] else "PARTIAL",
            "plantuml_wrapper_pass_files": counts["wrapper_pass"],
            "offline_input_loader_acceptance": "PASS" if counts["offline_loader_pass"] == counts["files"] else "PARTIAL",
            "offline_input_loader_pass_files": counts["offline_loader_pass"],
            "syntactic_validation_status": "NOT_INVOKED",
            "scientific_admissibility": "NO",
        }
        for setting, counts in by_setting.items()
    }


def _duplicate_correction(result: dict[str, Any]) -> dict[str, Any]:
    totals = Counter()
    groups: dict[str, list[dict[str, Any]]] = {}
    for setting, rows in result["duplicate_id_groups"].items():
        corrected = []
        for row in rows:
            lengths = row["logged_lengths"]
            excess = len(lengths) - 1
            kind = "same_length_excess" if len(set(lengths)) == 1 else "differing_length_excess"
            totals[kind] += excess
            corrected.append({**row, "duplicate_id_excess_rows": excess, "length_observation": kind})
        groups[setting] = corrected
    return {"groups": groups, "totals": dict(totals), "total_duplicate_id_excess_rows": sum(totals.values())}


def verify_airtravel_archive(archive: Path | None, manifest: Path | None) -> dict[str, Any]:
    result: dict[str, Any] = {"status": "BLOCKED", "provider_call_made": False, "matched_count": 0, "mismatch_count": 0}
    if archive is None or manifest is None or not archive.is_file() or not manifest.is_file():
        result["reason"] = "pinned AirTravel archive or v1.0.2 amendment manifest unavailable"
        return result
    try:
        amendment = json.loads(manifest.read_text(encoding="utf-8"))
        with zipfile.ZipFile(archive) as zf:
            names = set(zf.namelist())
            mismatches = []
            for item in amendment.get("runtime_files", []):
                candidates = [item["path"], f"runtime_input/{item['path']}"]
                name = next((candidate for candidate in candidates if candidate in names), None)
                if name is None or _sha(zf.read(name)) != str(item.get("sha256", "")).lower():
                    mismatches.append(item["path"])
            result["archive_sha256"] = _sha(archive.read_bytes())
            result["manifest_sha256"] = _sha(manifest.read_bytes())
            result["expected_runtime_count"] = len(amendment.get("runtime_files", []))
            result["matched_count"] = result["expected_runtime_count"] - len(mismatches)
            result["mismatch_count"] = len(mismatches)
            result["mismatches"] = mismatches
            result["status"] = "PASS" if not mismatches else "FAIL"
    except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        result["reason"] = str(exc)
    return result


def _instrumentation_receipt() -> dict[str, Any]:
    code = "from qa_instrumented_runner import run_parity_fixture; import json; r=run_parity_fixture(); ev=r['on']['events']; print(json.dumps({'prompt_parity':r['prompt_label_parity'],'scientific_state_parity':r['scientific_state_parity'],'event_count':len(ev),'route_pairs':sorted({(e['source_agent'],e['target_agent']) for e in ev if e.get('source_agent') and e.get('target_agent')}),'terminal_count':sum(e['event_type']=='EPISODE_TERMINATED' for e in ev),'termination_reasons':sorted({e.get('termination_reason') for e in ev if e['event_type']=='EPISODE_TERMINATED'}),'question_count':sum(e['event_type']=='QUESTION_EMITTED' for e in ev),'answer_count':sum(e['event_type']=='ANSWER_RECEIVED' for e in ev)}))"
    env = dict(**__import__("os").environ, PYTHONPATH=str(ROOT / "VEGO-AI" / "framework"))
    try:
        output = subprocess.check_output([sys.executable, "-c", code], env=env, text=True)
        return {"status": "FIXTURE_ONLY_PASS", "airtravel_exact_config": "NOT_EXERCISED_ARCHIVE_UNAVAILABLE", **json.loads(output.strip().splitlines()[-1])}
    except Exception as exc:
        return {"status": "BLOCKED", "reason": str(exc)}


def audit_v31(backup: Path, v2_manifest: Path | None, *, airtravel_archive: Path | None = None, airtravel_manifest: Path | None = None, audit_base_sha: str = "cbc2fb5e3c05471cf37c0eef55a48857e2066403") -> dict[str, Any]:
    v3 = _load_v3()
    result = v3.audit(backup, v2_manifest)
    result["audit_version"] = "historical-case-recovery-v3.1-erratum"
    result["audit_base_sha"] = audit_base_sha
    result["evidence_parent_sha"] = "36602e41a3a7ccec52a300d9244f3afe4702153f"
    result.pop("published_count_reference", None)
    result["duplicate_id_excess"] = _duplicate_correction(result)
    for _setting, row in result["per_setting"].items():
        row["duplicate_id_excess_rows"] = row.pop("duplicate_version_rows")
    result["executability_by_setting"] = _executability(backup)
    result["airtravel_manifest_provenance"] = {"branch": CLAUDE_BRANCH, "commit": CLAUDE_COMMIT, "path": CLAUDE_MANIFEST_PATH, "manifest_sha256": CLAUDE_MANIFEST_SHA256}
    result["airtravel_runtime_verification"] = verify_airtravel_archive(airtravel_archive, airtravel_manifest)
    result["instrumentation"] = _instrumentation_receipt()
    result["call_bound"] = {"N": 4, "minimum": 16, "retained_worst_case": 326, "status": "STATIC_ONLY"}
    result["api_cost"] = "TO BE MEASURED"
    result["protected_authorization"] = "NOT_SELF_AUTHORIZED"
    return result


def write_outputs(result: dict[str, Any], output_root: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    safe_receipt = {k: result[k] for k in ("audit_version", "audit_base_sha", "evidence_parent_sha", "backup_sha256", "archive_entry_count", "normalized_model_count", "file_level_match", "provider_calls", "experiment_calls", "detector_v1_runs", "airtravel_manifest_provenance", "airtravel_runtime_verification", "instrumentation", "call_bound", "api_cost", "protected_authorization")}
    (output_root / "backup-evidence-receipt.json").write_text(json.dumps(safe_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_root / "historical-load-universe.json").write_text(json.dumps({"per_setting": result["per_setting"], "ranking_lengths": result["ranking_lengths"], "duplicate_id_excess": result["duplicate_id_excess"]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_root / "provenance-binding-summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", type=Path, required=True)
    parser.add_argument("--v2-manifest", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--airtravel-archive", type=Path)
    parser.add_argument("--airtravel-manifest", type=Path)
    args = parser.parse_args()
    result = audit_v31(args.backup, args.v2_manifest, airtravel_archive=args.airtravel_archive, airtravel_manifest=args.airtravel_manifest)
    write_outputs(result, args.output_root)
    print(json.dumps({"audit_version": result["audit_version"], "backup_sha256": result["backup_sha256"], "file_level_match": result["file_level_match"], "duplicate_id_excess": result["duplicate_id_excess"], "airtravel_status": result["airtravel_runtime_verification"]["status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
