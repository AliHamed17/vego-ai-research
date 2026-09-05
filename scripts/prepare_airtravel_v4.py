"""Prepare the versioned AirTravel v4 package without executing it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from airtravel_v4_contract import (
    MANIFEST_PATH,
    PACKET_PATH,
    ROOT,
    RUN_ROOT,
    RUNTIME_ARCHIVE_SHA256,
    RUNTIME_FILES,
    digest,
    request_template,
    resolved_command_tokens,
    validate_command_record,
    validate_manifest,
    validate_private_layout,
)
from airtravel_v4_contract import (
    prepare_only as validate_prepare_only,
)

DEFAULT_RUNTIME_ROOT = ROOT / "external_data/airtravel-pr38/runtime_input"
DEFAULT_RUNTIME_ARCHIVE = ROOT / "external_data/airtravel-pr38/cd_airtravel-runtime-v1.0.2.zip"
PRIVATE_ROOT = ROOT / RUN_ROOT
EXPECTED_MANIFEST_SHA256 = "9d39f0023cf15d0879bfb404739feefe457324a909acc66c0499f5e8afbd61ea"


class V4PreparationError(RuntimeError):
    """Raised when preparation fails closed."""


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + chr(10)).encode("utf-8")


def _write_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise V4PreparationError(f"existing private file differs: {path.name}")
        return
    with path.open("xb") as handle:
        handle.write(data)


def _load_manifest() -> tuple[dict[str, Any], str]:
    path = ROOT / MANIFEST_PATH
    if not path.is_file():
        raise V4PreparationError("machine packet manifest missing")
    observed = digest(path)
    if observed != EXPECTED_MANIFEST_SHA256:
        raise V4PreparationError("machine packet manifest hash mismatch")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    from jsonschema import Draft202012Validator

    schema = json.loads(
        (ROOT / "schemas/airtravel-v4-packet-manifest-v1.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator(schema).validate(manifest)
    validate_manifest(manifest)
    return manifest, observed


def _runtime_checks(runtime_root: Path, archive: Path) -> dict[str, Any]:
    if not archive.is_file() or digest(archive) != RUNTIME_ARCHIVE_SHA256:
        raise V4PreparationError("runtime archive unavailable or hash mismatch")
    observed: dict[str, dict[str, Any]] = {}
    for relative, frozen in RUNTIME_FILES.items():
        target = runtime_root / relative
        if not target.is_file():
            raise V4PreparationError(f"runtime file missing: {relative}")
        actual = {"sha256": digest(target), "bytes": target.stat().st_size}
        if actual != frozen:
            raise V4PreparationError(f"runtime file mismatch: {relative}")
        observed[relative] = actual
    visible = {
        path.relative_to(runtime_root).as_posix()
        for path in runtime_root.rglob("*")
        if path.is_file()
    }
    if visible - set(RUNTIME_FILES) - {"cd_airtravel.runtime-config.json"}:
        raise V4PreparationError("unexpected runtime-visible reference file")
    config_path = runtime_root / "cd_airtravel.runtime-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if (
        config.get("setting_id") != "cd_airtravel"
        or config.get("corpus_id") != "text2uml_airtravel_253b26dc"
        or config.get("provider_execution_enabled") is not False
        or config.get("description_path") != "domain_description/description.md"
        or config.get("candidate_models_dir") != "candidate_models"
        or config.get("runtime_files") != sorted(RUNTIME_FILES)
    ):
        raise V4PreparationError("runtime configuration is not the frozen five-file configuration")
    return {"archive_sha256": digest(archive), "runtime_files": observed, "reference_paths": []}


def _resolved_command(runtime_root: Path, archive: Path, output_root: Path) -> list[str]:
    return resolved_command_tokens(runtime_root, archive, output_root)


def prepare_only(
    *,
    runtime_root: Path = DEFAULT_RUNTIME_ROOT,
    runtime_archive: Path = DEFAULT_RUNTIME_ARCHIVE,
    private_root: Path = PRIVATE_ROOT,
) -> dict[str, Any]:
    """Write v4 request/command/preparation material and stop."""
    manifest, manifest_sha = _load_manifest()
    if private_root.resolve() != PRIVATE_ROOT.resolve():
        raise V4PreparationError("private run root must be the fixed v4 root")
    validate_private_layout(private_root, preparation=True)
    runtime = _runtime_checks(runtime_root, runtime_archive)
    request = request_template()
    result = validate_prepare_only(manifest=manifest, request=request)
    control = private_root / "control"
    output_root = private_root / "output"
    command = _resolved_command(runtime_root, runtime_archive, output_root)
    command_sha = hashlib.sha256(_canonical(command)).hexdigest()
    command_record = {"tokens": command, "command_sha256": command_sha, "max_invocations": 1}
    validate_command_record(command_record, manifest)
    request = {
        **request,
        "packet_manifest_sha256": manifest_sha,
        "packet_sha256": digest(ROOT / PACKET_PATH),
        "command_sha256": command_sha,
        "grant_present": False,
        "authorization_message_present": False,
    }
    receipt = {
        "schema_version": "airtravel-v4-preparation-receipt-v1",
        "status": "AUTHORIZATION_REQUESTED_NOT_GRANTED",
        "mode": "prepare_only",
        "packet_path": PACKET_PATH,
        "packet_manifest_path": MANIFEST_PATH,
        "packet_manifest_sha256": manifest_sha,
        "packet_sha256": digest(ROOT / PACKET_PATH),
        "run_root": RUN_ROOT,
        "setting_id": "cd_airtravel",
        "corpus_id": "text2uml_airtravel_253b26dc",
        "N": 4,
        "command_sha256": command_sha,
        "runtime": runtime,
        "checks": {
            "machine_manifest": "PASS",
            "runtime_archive": "PASS",
            "five_runtime_files": "PASS",
            "reference_separation": "PASS",
            "fixed_root": "PASS",
            "grant": "NOT_CREATED",
            "protected_import": "NOT_INVOKED",
            "provider_calls": 0,
            "detector_runs": 0,
            "renderer_runs": 0,
        },
        # Preparation is intentionally reproducible; execution timestamps are
        # recorded later in the exclusive attempt ledger.
        "created_at": "PREPARATION_ONLY_NOT_EXECUTED",
    }
    _write_once(control / "private-execution-request.json", _canonical(request))
    _write_once(control / "execution-command.json", _canonical(command_record))
    _write_once(control / "preparation-receipt.json", _canonical(receipt))
    return {
        **result,
        "status": "AUTHORIZATION_REQUESTED_NOT_GRANTED",
        "manifest_sha256": manifest_sha,
        "command_sha256": command_sha,
        "request_path": (control / "private-execution-request.json").relative_to(ROOT).as_posix(),
        "preparation_receipt_path": (control / "preparation-receipt.json").relative_to(ROOT).as_posix(),
        "runtime_archive_sha256": runtime["archive_sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--grant", type=Path)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--runtime-archive", type=Path, default=DEFAULT_RUNTIME_ARCHIVE)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.execute:
        try:
            if not args.packet or not args.grant or not args.output_dir or not args.receipt:
                raise V4PreparationError("execute requires packet, grant, output-dir and receipt")
            manifest, manifest_sha = _load_manifest()
            if args.packet.resolve() != (ROOT / PACKET_PATH).resolve():
                raise V4PreparationError("packet path differs from machine manifest")
            _runtime_checks(args.runtime_root, args.runtime_archive)
            from airtravel_v4_execution import execute_authorized

            receipt = execute_authorized(
                runtime_root=args.runtime_root,
                archive=args.runtime_archive,
                output=args.output_dir,
                receipt_path=args.receipt,
                packet=args.packet,
                grant=args.grant,
                root=ROOT,
            )
            return print(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2)) or 0
        except (OSError, ValueError, V4PreparationError) as exc:
            print(json.dumps({"status": "PREFLIGHT_V4_FAILED", "error": str(exc)}))
            return 2
    try:
        result = prepare_only(runtime_root=args.runtime_root, runtime_archive=args.runtime_archive)
    except (OSError, ValueError, V4PreparationError) as exc:
        print(json.dumps({"status": "PREFLIGHT_V4_NOT_READY", "error": str(exc)}))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
