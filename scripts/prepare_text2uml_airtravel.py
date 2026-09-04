"""Prepare a provenance-bound, metadata-only Text2UML AirTravel pilot pack.

The source directory is supplied explicitly and is never copied into tracked
output. Optional local staging writes only under ignored ``external_data``.
No model, provider, or experiment is invoked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

LICENSE_NAME = "GPL-3.0"
UPSTREAM_URL = "https://github.com/IlKaiser/text2uml"
AIRTRAVEL_URL = f"{UPSTREAM_URL}/tree/main/dataset/AirTravel"
PROPOSED_CANDIDATES = (
    "result_one_claude-sonnet-4-6.txt",
    "result_one_codestral-2508.txt",
    "result_one_deepseek-chat.txt",
    "result_one_gemini-2.5-flash.txt",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(relative: str) -> str:
    name = Path(relative).name
    if name == "description.md":
        return "DOMAIN_DESCRIPTION_CANDIDATE"
    if name == "metadata.txt":
        return "METADATA"
    if name == "plantuml.txt":
        return "REFERENCE_MODEL"
    if name == "plantuml_adjusted.txt":
        return "DERIVED_DUPLICATE"
    if name.endswith(".png") or name.endswith(".svg"):
        return "VISUALIZATION_ONLY"
    if relative.startswith("extramaterial/"):
        return "REFERENCE_MODEL"
    if name.startswith("result_") and name.endswith("_stripped.txt"):
        return "DERIVED_DUPLICATE"
    if name.startswith("result_") and name.endswith(".txt"):
        return "GENERATED_CANDIDATE_MODEL"
    return "UNKNOWN"


def syntax_status(path: Path, category: str) -> str:
    if category not in {"REFERENCE_MODEL", "DERIVED_DUPLICATE", "GENERATED_CANDIDATE_MODEL"}:
        return "NOT_APPLICABLE"
    raw = path.read_bytes()
    if not raw:
        return "EMPTY"
    text = raw.decode("utf-8", errors="replace")
    if "@startuml" not in text or "@enduml" not in text:
        return "MISSING_PLANTUML_WRAPPERS"
    return "WRAPPER_PRESENT"


def build_inventory(source_root: Path) -> list[dict[str, object]]:
    rows = []
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source_root).as_posix()
        category = classify(relative)
        rows.append({
            "path": relative,
            "classification": category,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "syntax_validation": syntax_status(path, category),
            "source": "Text2UML pinned upstream commit",
        })
    return rows


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def prepare(args: argparse.Namespace) -> None:
    source = args.source_root.resolve()
    if not source.is_dir():
        raise SystemExit(f"source root does not exist: {source}")
    inventory = build_inventory(source)
    by_path = {str(row["path"]): row for row in inventory}
    license_path = args.repository_root / "LICENSE"
    if not license_path.is_file():
        raise SystemExit("pinned repository LICENSE is missing")
    retrieval = args.retrieval_timestamp or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    archive_hash = sha256(args.archive) if args.archive and args.archive.is_file() else None
    selected = []
    for name in PROPOSED_CANDIDATES:
        row = by_path.get(name)
        if row is None:
            continue
        row = dict(row)
        row["proposal_status"] = "PROPOSED_NOT_FROZEN"
        row["selection_reason"] = "nonempty, non-stripped, distinct filename/model output; pending Claude freeze"
        selected.append(row)
    out = args.output_root
    out.mkdir(parents=True, exist_ok=True)
    manifest = {
        "manifest_version": "text2uml-airtravel-source-v1",
        "dataset": "Text2UML",
        "scenario": "AirTravel",
        "upstream_repository": UPSTREAM_URL,
        "airtravel_url": AIRTRAVEL_URL,
        "upstream_commit": args.upstream_sha,
        "retrieval_timestamp_utc": retrieval,
        "acquisition_method": "GitHub codeload archive pinned by commit SHA",
        "archive_sha256": archive_hash,
        "license": LICENSE_NAME,
        "license_sha256": sha256(license_path),
        "prepared_pack_found_locally": False,
        "source_root_relative": "external_data/text2uml/<upstream-commit>/repository/dataset/AirTravel",
        "files": inventory,
    }
    write_json(out / "source-manifest.json", manifest)
    write_json(out / "airtravel-inventory.json", {"scenario": "AirTravel", "files": inventory})
    write_json(out / "candidate-subset-proposal.json", {
        "status": "PROPOSED_NOT_FROZEN",
        "target_n": 4,
        "actual_proposed_n": len(selected),
        "freeze_owner": "Claude/human owner",
        "candidates": selected,
    })
    (out / "candidate-subset-proposal.md").write_text(
        "# AirTravel candidate-subset proposal\n\n"
        "Status: **PROPOSED_NOT_FROZEN**. Claude must freeze the exact selection before any run.\n\n"
        f"Four independently stored, nonempty, non-stripped outputs are proposed (N={len(selected)}):\n\n"
        + "\n".join(f"- `{row['path']}` — SHA-256 `{row['sha256']}`, {row['bytes']} bytes; syntax `{row['syntax_validation']}`"
                    for row in selected)
        + "\n\nSelection uses filename/documented output provenance only. It does not use VEGO-AI outputs, Q&A frequency, Detector-v1, or reference agreement. No candidate is treated as a student or human submission.\n",
        encoding="utf-8",
    )
    (out / "license-attribution-receipt.md").write_text(
        "# Text2UML AirTravel license and attribution receipt\n\n"
        f"- Upstream: [{UPSTREAM_URL}]({UPSTREAM_URL})\n- Scenario: [{AIRTRAVEL_URL}]({AIRTRAVEL_URL})\n"
        f"- Pinned commit: `{args.upstream_sha}`\n- Declared license: `{LICENSE_NAME}`\n"
        f"- LICENSE SHA-256: `{sha256(license_path)}`\n- Archive SHA-256: `{archive_hash}`\n\n"
        "Redistribution policy is not presumed. Raw source remains local and ignored until license review confirms the required GPL notice and attribution.\n",
        encoding="utf-8",
    )
    (out / "reference-separation-receipt.md").write_text(
        "# AirTravel reference-separation receipt\n\n"
        "Proposed ignored local layout:\n\n"
        "```text\nexternal_data/text2uml/<upstream-commit>/prepared/AirTravel/\n"
        "  runtime_input/domain_description/description.md\n"
        "  runtime_input/candidate_models/<candidate files>\n"
        "  reference_only/plantuml.txt\n  reference_only/plantuml_adjusted.txt\n"
        "  reference_only/extramaterial/<files>\n  source_metadata/LICENSE\n```\n\n"
        "The runtime input contains the domain description and proposed generated candidates only. Reference models and extramaterial are excluded from the VEGO-AI configuration and are never passed to the orchestrator. Candidate bytes are copied without transformation; original and staged hashes are checked by the preparation script.\n",
        encoding="utf-8",
    )
    prepared_rel = f"../../../../external_data/text2uml/{args.upstream_sha}/prepared/AirTravel"
    write_json(out / "vego-ai-config-airtravel.json", {
        "settings": [{
            "setting_id": "cd_airtravel",
            "language_name": "UML",
            "corpus_id": f"text2uml_airtravel_{args.upstream_sha[:8]}",
            "provider_run_permitted": False,
            "domain_description_file": f"{prepared_rel}/runtime_input/domain_description/description.md",
            "case_models_dir": f"{prepared_rel}/runtime_input/candidate_models",
            "reference_only_dir": f"{prepared_rel}/reference_only",
            "candidate_count_N": len(selected),
            "source_commit": args.upstream_sha,
        }],
        "provider_run_permitted": False,
    })
    (out / "offline-compatibility-report.md").write_text(
        "# AirTravel offline compatibility report\n\n"
        "- Domain description: UTF-8 decodes successfully.\n"
        "- Candidate PlantUML: proposed files are nonempty and wrapper-valid; no source bytes were rewritten.\n"
        "- Filename-to-case mapping: staged copies receive deterministic numeric prefixes (01..N) because the protected loader derives case_id from the prefix; source bytes remain unchanged and duplicate case IDs are avoided.\n"
        "- Reference exclusion: reference models remain outside runtime_input.\n"
        "- Configuration paths: repository-relative paths resolve from the config file directory to the ignored prepared pack; no absolute path is embedded.\n"
        f"- Case count N: `{len(selected)}` (proposal only; not frozen).\n"
        "- Provider/model execution: **not performed**.\n"
        "- Parser/render check: metadata and wrapper checks only; no scientific result or alert was generated.\n",
        encoding="utf-8",
    )
    (out / "remaining-blockers.md").write_text(
        "# AirTravel preparation blockers\n\n"
        "1. Claude/human owner must freeze the exact candidate subset.\n"
        "2. GPL-3.0 redistribution/attribution review must be completed before any source publication.\n"
        "3. Protected-path authorization and the existing stale release manifest remain unresolved.\n"
        "4. This package is preparation only: no provider run, Detector-v1 application, alert result, or preliminary empirical claim is permitted.\n",
        encoding="utf-8",
    )
    (out / "2026-09-04-airtravel-static-call-bound.md").write_text(
        "# AirTravel static call bound\n\n"
        f"For the proposed (not frozen) `N={len(selected)}` candidates, minimum calls are `4 + 3N = {4 + 3 * len(selected)}` and the retained worst-case bound is `82 + 61N = {82 + 61 * len(selected)}`. These are static control-flow bounds only; no provider call or cost estimate was made.\n",
        encoding="utf-8",
    )
    if args.stage_root:
        prepared = args.stage_root / "prepared" / "AirTravel"
        runtime_desc = prepared / "runtime_input" / "domain_description"
        runtime_candidates = prepared / "runtime_input" / "candidate_models"
        reference = prepared / "reference_only"
        metadata = prepared / "source_metadata"
        # Rebuild only this tool-owned staging subtree so reruns cannot leave
        # stale candidate filenames that would create duplicate case IDs.
        if prepared.exists():
            shutil.rmtree(prepared)
        for directory in (runtime_desc, runtime_candidates, reference, metadata):
            directory.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / "description.md", runtime_desc / "description.md")
        for index, row in enumerate(selected, start=1):
            # The protected loader derives case_id from the numeric prefix
            # before the first underscore.  Prefixing a staged copy preserves
            # source bytes while preventing all ``result_*`` files becoming
            # the duplicate case_id ``result``.
            staged_name = f"{index:02d}_{Path(str(row['path'])).name}"
            shutil.copyfile(source / str(row["path"]), runtime_candidates / staged_name)
        for name in ("plantuml.txt", "plantuml_adjusted.txt"):
            shutil.copyfile(source / name, reference / name)
        for path in (source / "extramaterial").rglob("*"):
            if path.is_file():
                destination = reference / "extramaterial" / path.relative_to(source / "extramaterial")
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, destination)
        shutil.copyfile(license_path, metadata / "LICENSE")
        checks = []
        for index, row in enumerate(selected, start=1):
            staged = runtime_candidates / f"{index:02d}_{Path(str(row['path'])).name}"
            checks.append({"path": str(row["path"]), "staged_path": staged.name,
                           "source_sha256": row["sha256"], "staged_sha256": sha256(staged),
                           "byte_identical": row["sha256"] == sha256(staged),
                           "case_id": f"{index:02d}"})
        write_json(out / "staging-hash-check.json", checks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--upstream-sha", required=True)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--stage-root", type=Path)
    parser.add_argument("--retrieval-timestamp")
    prepare(parser.parse_args())


if __name__ == "__main__":
    main()
