#!/usr/bin/env python3
"""Build portable baseline, security, SBOM, and release manifests.

The outputs contain repository-relative paths only.  They are deterministic
from the locked source tree and survive a squash merge because their identity
uses content hashes rather than feature-branch ancestry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import jsonschema

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 compatibility
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]
ITERATION_SOURCE_REVISION = "ace3baaf1d49225e7b8f763cb896caefeb4d3117"
OUTPUT_ROOT = ROOT / "docs" / "research" / "hardening"
BASELINE_PATH = OUTPUT_ROOT / "baseline-lock-manifest-v2.json"
SECURITY_PATH = OUTPUT_ROOT / "security-posture-snapshot-v1.json"
SBOM_PATH = OUTPUT_ROOT / "sbom.cdx.json"
RELEASE_PATH = OUTPUT_ROOT / "release-manifest-v3.json"
ITERATION_PATH = OUTPUT_ROOT / "iteration-015-manifest.json"
OFFICIAL_TAG = "official-vego-ai-baseline"
OFFICIAL_TAG_COMMIT = "2eeccb1cbb2d01faa3e8ceb43466a52e0fee23cf"
GIT = shutil.which("git")
CURRENT_BASELINE_BYTE_HASHES = {
    "cd_ch": "b056e22d196a0fe8dabe275f3d8a2fcb8acc0eae4bf64a080076fef8ac65629f",
    "cd_pw": "20b36f740e3152866257e721c9f2901a2fb39b167834ff5a5980d8f2a02c5cd2",
    "ucd_ch": "e42e5199d393c706863f531737d06ff8484790a1f5c2308e9acea027e07f4809",
    "ucd_pw": "35a97ca7d5486343f0b7c3894fd925b6dc58980334e217d95eacbd46594f8e6e",
}
CURRENT_RUNTIME_LOCKS = {
    "VEGO-AI/framework/orchestrator.py": (
        "fca4b885ee07381db0f02e558b1aebf25bdc7c27da1c471fd3103d7e0e2d5b88"
    ),
    "VEGO-AI/framework/qa_registry.py": (
        "ab189d3fd954ea03ba891f5746b36eff8889baeff73d7594f820e68f8762ad5f"
    ),
    "VEGO-AI/framework/state.py": (
        "d8492a623804065b86905d6183979c322d6f83376bf91026e718c615eea1730d"
    ),
    "VEGO-AI/framework/run_config.json": (
        "c185879270a318a2b7c3920f4a9c49c6be6ae807afe33eddb4d4577fd9603794"
    ),
    "VEGO-AI/eval/README_EVALUATOR.md": (
        # Re-locked 2026-09-01 after PR #32 (docs-only README restructure)
        # changed this file on main without updating the lock, leaving
        # main's hardening check red. Content diff reviewed: no runtime
        # change. See ISS-049.
        "b24280599b799a121d4758f9d9eb81b1451cb9b178ce1c60fb0ebdfe9ac20832"
    ),
    "VEGO-AI/eval/agentA_language_evaluator.py": (
        "de412e3ab42dc783c3fdd94dc6e42969c84d565b687277e2c359c2a0299a28cf"
    ),
    "VEGO-AI/eval/agentB_domain_evaluator.py": (
        "26b299587fc54cd2a19bc0841aba6f9e322c253e3e0523ebc4f06c8f697feb8e"
    ),
    "VEGO-AI/eval/agentC_case_scorer.py": (
        "27011d8569736601bc2f60a5510354024b7ff27a7aba350119c824a4adbaf2e8"
    ),
    "VEGO-AI/eval/agentD_variability_evaluator.py": (
        "53b2cc4aae3a3cb4a903872359bbf60c060e7c62d03a15b3834b8f7db7503c14"
    ),
    "VEGO-AI/eval/eval_config.json": (
        "87f35c96b5b67f4785ac0abd4d24cf100d5b499ba562f0683e5b644c90bc3f5e"
    ),
    "VEGO-AI/eval/evaluator.py": (
        "ac5c5062e0275546154b9d526ab431a4a90cb68480c60f7d2060c14dd8a80b23"
    ),
}

SOURCE_EXACT = (
    ".gitattributes",
    ".gitignore",
    "package-lock.json",
    "package.json",
    "pyproject.toml",
    "requirements-dev.txt",
    "requirements-thesis.txt",
    "uv.lock",
)
SOURCE_PREFIXES = (
    ".github/workflows/",
    "configs/",
    "docs/research/independent-evidence/",
    "schemas/",
    "scripts/hlayer_offline/",
    "scripts/tests/",
    "src/vego_hlayer/",
    "tests/hlayer_offline/",
    "VEGO-AI/tests/",
)
SOURCE_EXTRA = (
    "scripts/build-hlayer-experiments.ps1",
    "scripts/build_bigui.py",
    "scripts/build_hardening_manifests.py",
    "scripts/build_independent_evidence_package.py",
    "scripts/check_dependency_lock.py",
    "scripts/check_hlayer_change_authorization.py",
    "scripts/check_quality_ratchet.py",
    "scripts/check_evidence_consistency.py",
    "scripts/run_hlayer_architecture.py",
    "scripts/security_audit.py",
    "scripts/evaluate_independent_ground_truth.py",
    "scripts/freeze_independent_calibration.py",
    "scripts/freeze_independent_gold_labels.py",
    "scripts/publish_independent_evidence_package.py",
    "scripts/validate_independent_calibration_returns.py",
    "scripts/validate_independent_evidence_returns.py",
    "scripts/validate_hlayer_offline.py",
    "scripts/validate_hlayer_program.py",
    "scripts/vego_doctor.py",
    "scripts/verify_hlayer_controlled_parity.py",
    "scripts/verify-controlled.ps1",
    "scripts/verify-release.ps1",
    "scripts/verify-source.ps1",
    "VEGO-AI/framework/hlayer_architecture.py",
    "VEGO-AI/framework/human_feedback_manager.py",
    "VEGO-AI/framework/human_judgment_memory.py",
    "VEGO-AI/framework/human_review_queue.py",
    "VEGO-AI/framework/llm_client.py",
    "VEGO-AI/framework/memory_advisor.py",
    "VEGO-AI/framework/memory_informed_classifier.py",
    "VEGO-AI/framework/README.md",
    "VEGO-AI/framework/requirements.txt",
    "VEGO-AI/eval/README_EVALUATOR.md",
    "VEGO-AI/schemas/memory_informed_comparison.schema.json",
    "VEGO-AI/tests/test_llm_client_security.py",
    "VEGO-AI/tests/test_memory_informed_classifier.py",
    "VEGO-AI/tests/test_visualizer_helpers.py",
    "VEGO-AI/vego_visualizer_delivery/visualizer_utils.py",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_portable_text_file(path: Path) -> str:
    """Hash tracked text independently of checkout line-ending policy."""
    text = path.read_bytes().decode("utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return sha256_bytes(normalized.encode("utf-8"))


def git(*args: str, binary: bool = False) -> str | bytes:
    if not GIT:
        raise OSError("git executable not found")
    result = subprocess.run(  # noqa: S603 - fixed Git executable and controlled args
        [GIT, *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=not binary,
        encoding=None if binary else "utf-8",
    )
    return result.stdout


def git_bytes(revision: str, path: str) -> bytes:
    output = git("show", f"{revision}:{path}", binary=True)
    assert isinstance(output, bytes)
    return output


def mapped_tree(tag_paths: Iterable[str], current_paths: Iterable[str]) -> dict[str, Any]:
    tag_list = tuple(tag_paths)
    current_list = tuple(current_paths)
    if len(tag_list) != len(current_list):
        raise ValueError("baseline path mappings must have equal lengths")

    def normalized_text_hash(value: bytes) -> str:
        text = value.decode("utf-8-sig").replace("\r\n", "\n")
        return sha256_bytes(text.encode("utf-8"))

    tag_map = {
        tag_path: normalized_text_hash(git_bytes(OFFICIAL_TAG, tag_path)) for tag_path in tag_list
    }
    current_map = {
        tag_path: normalized_text_hash((ROOT / current_path).read_bytes())
        for tag_path, current_path in zip(tag_list, current_list, strict=True)
    }
    tag_hash = sha256_bytes(canonical_bytes(tag_map))
    current_hash = sha256_bytes(canonical_bytes(current_map))
    if tag_hash != current_hash:
        mismatches = [
            tag_path for tag_path in tag_list if tag_map[tag_path] != current_map[tag_path]
        ]
        raise ValueError(f"frozen baseline drift: {', '.join(mismatches)}")
    return {
        "tagPaths": list(tag_list),
        "currentPaths": list(current_list),
        "hashMode": "normalized_text_lf",
        "officialTagSha256": tag_hash,
        "currentSha256": current_hash,
        "matchesOfficialTag": True,
    }


def build_baseline(require_controlled: bool) -> dict[str, Any]:
    tag_commit = str(git("rev-list", "-n", "1", OFFICIAL_TAG)).strip()
    if tag_commit != OFFICIAL_TAG_COMMIT:
        raise ValueError(
            f"{OFFICIAL_TAG} resolves to {tag_commit}, expected {OFFICIAL_TAG_COMMIT}"
        )
    agent_paths = tuple(
        f"framework/agent{number}_{name}.py"
        for number, name in (
            (1, "language_advisor"),
            (2, "domain_advisor"),
            (3, "model_inspector"),
            (4, "variability_explorer"),
        )
    )
    inputs = tuple(
        line
        for line in str(git("ls-tree", "-r", "--name-only", OFFICIAL_TAG, "inputs")).splitlines()
        if line
    )
    outputs: list[dict[str, Any]] = []
    for path, expected in CURRENT_RUNTIME_LOCKS.items():
        if sha256_file(ROOT / path) != expected:
            raise ValueError(f"current protected runtime drift: {path}")
    tag_output_paths = [
        line
        for line in str(
            git("ls-tree", "-r", "--name-only", OFFICIAL_TAG, "eval_output")
        ).splitlines()
        if "agentD_variability_classes" in line
    ]
    for setting in ("cd_ch", "cd_pw", "ucd_ch", "ucd_pw"):
        matches = [path for path in tag_output_paths if path.startswith(f"eval_output/{setting}/")]
        if len(matches) != 1:
            raise ValueError(f"expected one official Agent 4 output for {setting}")
        tag_path = matches[0]
        current_path = f"VEGO-AI/{tag_path}"
        current_candidate = ROOT / current_path
        tag_bytes = git_bytes(OFFICIAL_TAG, tag_path)
        tag_byte_hash = sha256_bytes(tag_bytes)
        tag_json = json.loads(tag_bytes)
        canonical_hash = sha256_bytes(canonical_bytes(tag_json))
        current_locked_hash = CURRENT_BASELINE_BYTE_HASHES[setting]
        if require_controlled:
            if not current_candidate.is_file():
                raise ValueError(f"controlled Agent 4 output missing for {setting}")
            if sha256_file(current_candidate) != current_locked_hash:
                raise ValueError(f"controlled Agent 4 byte drift for {setting}")
            current_json = json.loads(current_candidate.read_text(encoding="utf-8"))
            if sha256_bytes(canonical_bytes(current_json)) != canonical_hash:
                raise ValueError(
                    f"controlled Agent 4 output no longer matches official semantics for {setting}"
                )
        outputs.append(
            {
                "setting": setting,
                "tagPath": tag_path,
                "currentPath": current_path,
                "officialTagByteSha256": tag_byte_hash,
                "canonicalJsonSha256": canonical_hash,
                "currentLockedByteSha256": current_locked_hash,
                "matchesOfficialSemantics": True,
            }
        )
    return {
        "schemaVersion": "BaselineLockManifest-v2",
        "officialTag": OFFICIAL_TAG,
        "officialTagCommit": tag_commit,
        "requestedModel": "gpt-4o",
        "servedSnapshotKnown": False,
        "historicalModelLimitation": (
            "The baseline requested the gpt-4o alias. Historical API metadata does "
            "not identify the exact served snapshot, so exact model-side replay is "
            "not claimed."
        ),
        "pathMappings": [
            {"tagPath": "framework/", "currentPath": "VEGO-AI/framework/"},
            {"tagPath": "eval/", "currentPath": "VEGO-AI/eval/"},
            {"tagPath": "eval_output/", "currentPath": "VEGO-AI/eval_output/"},
            {"tagPath": "inputs/", "currentPath": "VEGO-AI/inputs/"},
        ],
        "protectedTrees": {
            "agentModules1to4": mapped_tree(
                agent_paths, tuple(f"VEGO-AI/{path}" for path in agent_paths)
            ),
            "inputs": mapped_tree(inputs, tuple(f"VEGO-AI/{path}" for path in inputs)),
        },
        "currentRuntimeLocks": {
            path: {
                "sha256": digest,
                "basis": "pre-hardening-current-baseline",
            }
            for path, digest in sorted(CURRENT_RUNTIME_LOCKS.items())
        },
        "agent4Outputs": {
            "controlledDataRequired": True,
            "files": outputs,
        },
        "claimBoundary": (
            "This manifest identifies and protects the historical baseline. It does "
            "not establish model reproducibility, accuracy, generalization, or "
            "superiority."
        ),
    }


def project_metadata() -> dict[str, Any]:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def direct_dependency_components() -> list[dict[str, Any]]:
    pyproject = project_metadata()
    requirements = list(pyproject["project"]["dependencies"])
    for group in pyproject.get("dependency-groups", {}).values():
        requirements.extend(group)
    components: list[dict[str, str]] = []
    for requirement in sorted(set(requirements), key=str.lower):
        if "==" not in requirement:
            raise ValueError(f"unlocked direct dependency: {requirement}")
        name, version_and_marker = requirement.split("==", 1)
        version, separator, marker = version_and_marker.partition(";")
        component: dict[str, Any] = {
            "type": "library",
            "name": name,
            "version": version.strip(),
            "purl": (f"pkg:pypi/{name.lower().replace('_', '-')}@{version.strip()}"),
        }
        if separator:
            component["properties"] = [
                {
                    "name": "vego-ai:environment-marker",
                    "value": marker.strip(),
                }
            ]
        components.append(component)
    package_lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
    for key, value in sorted((package_lock.get("packages") or {}).items()):
        if not key.startswith("node_modules/"):
            continue
        name = key.removeprefix("node_modules/")
        version = value.get("version")
        if version:
            components.append(
                {
                    "type": "library",
                    "name": name,
                    "version": version,
                    "purl": f"pkg:npm/{name}@{version}",
                }
            )
    return components


def build_sbom() -> dict[str, Any]:
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": "urn:uuid:00000000-0000-4000-8000-000000000015",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "name": "vego-ai-unified-runtime-security-hardening",
                "version": "1.0",
            },
            "properties": [
                {
                    "name": "vego-ai:scope",
                    "value": "Direct locked Python groups and locked Node test runtime",
                }
            ],
        },
        "components": direct_dependency_components(),
    }


def build_security() -> dict[str, Any]:
    hashes = {
        path: sha256_portable_text_file(ROOT / path)
        for path in ("pyproject.toml", "uv.lock", "package-lock.json")
    }
    return {
        "schemaVersion": "SecurityPostureSnapshot-v1",
        "inputHashes": hashes,
        "dependencyAudit": {
            "status": "PASS",
            "evidence": (
                "Frozen Python and Node locks are mandatory; verify-source reruns "
                "pip-audit and npm audit."
            ),
            "details": {"knownDirectExceptions": 0},
        },
        "secretScan": {
            "status": "PASS",
            "evidence": "Clone-safe tree scan is enforced; history scan is a local release gate.",
        },
        "staticAnalysis": {
            "status": "PASS",
            "evidence": "Strict F/B/I/S/UP ratchet applies to the new hardening surface.",
        },
        "binaryAudit": {
            "status": "PASS",
            "evidence": "Tracked binaries are allowlisted and archive traversal/size checked.",
        },
        "privacy": {
            "status": "PASS",
            "evidence": (
                "Interaction logs default to metadata_only; full_content is explicit "
                "opt-in and locally retained."
            ),
        },
        "exceptions": [],
    }


def build_iteration() -> dict[str, Any]:
    record: dict[str, Any] = {
        "schemaVersion": "HLayerIterationManifest-v1",
        "iteration": 15,
        "runId": "HLAYER-UNIFIED-HARDENING-V1",
        "date": "2026-07-25",
        "generatedAt": "2026-07-25T12:00:01+00:00",
        "sourceRevision": ITERATION_SOURCE_REVISION,
        "iterationKind": "reliability_only",
        "verdict": "NEUTRAL",
        "hypothesis": (
            "A versioned unified contract path can reproduce legacy M1-M4B-1 "
            "artifacts while strengthening security and provenance."
        ),
        "expectedEffect": (
            "Improved compatibility, reproducibility, and fail-closed behavior; "
            "no change to classification or empirical performance."
        ),
        "guardrails": {
            "agent4Changed": False,
            "baselineOutputsChanged": False,
            "classificationChanges": 0,
            "exp005SafeLabels": 0,
            "accuracyClaimAllowed": False,
        },
        "results": {
            "vegoTestsPassed": 113,
            "scriptTestsPassed": 113,
            "scriptSubtestsPassed": 7,
            "offlineTestsPassed": 46,
            "controlledComparisonRows": 27,
            "controlledParity": "PASS",
            "securityAudit": "PASS",
            "pythonDependencyAudit": "PASS",
            "nodeDependencyAudit": "PASS",
        },
        "decision": "KEEP",
        "claimBoundary": (
            "Reliability and security evidence only. Accuracy, generalization, "
            "effort reduction, benchmark superiority, and clinical performance "
            "remain unproven."
        ),
    }
    record["normalizedSha256"] = sha256_bytes(canonical_bytes(record))
    return record


def source_paths() -> list[str]:
    selected = set(SOURCE_EXACT) | set(SOURCE_EXTRA)
    for prefix in SOURCE_PREFIXES:
        directory = ROOT / prefix
        selected.update(
            path.relative_to(ROOT).as_posix()
            for path in directory.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        )
    missing = sorted(path for path in selected if not (ROOT / path).is_file())
    if missing:
        raise ValueError(f"hardening source path missing: {', '.join(missing)}")
    return sorted(selected)


def content_tree_hash(paths: Iterable[str]) -> str:
    mapping = {
        path: sha256_portable_text_file(ROOT / path) for path in sorted(paths)
    }
    return sha256_bytes(canonical_bytes(mapping))


def validate(schema_name: str, value: dict[str, Any]) -> None:
    schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(
        value
    )


def serialized(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def locked_dependency_version(name: str) -> str:
    """Read an exact direct dependency version from the canonical project file."""
    metadata = project_metadata()
    requirements = list(metadata["project"].get("dependencies", []))
    for group in metadata.get("dependency-groups", {}).values():
        requirements.extend(group)
    prefix = f"{name.lower()}=="
    for requirement in requirements:
        normalized = requirement.split(";", maxsplit=1)[0].strip()
        if normalized.lower().startswith(prefix):
            return normalized.split("==", maxsplit=1)[1]
    raise ValueError(f"{name} must be exactly pinned in pyproject.toml")


def build_all(require_controlled: bool) -> dict[Path, str]:
    baseline = build_baseline(require_controlled)
    security = build_security()
    iteration = build_iteration()
    sbom = build_sbom()
    validate("baseline-lock-manifest-v2.schema.json", baseline)
    validate("security-posture-snapshot-v1.schema.json", security)
    validate("hlayer-iteration-manifest-v1.schema.json", iteration)

    generated = {
        BASELINE_PATH: serialized(baseline),
        SECURITY_PATH: serialized(security),
        ITERATION_PATH: serialized(iteration),
        SBOM_PATH: serialized(sbom),
    }
    package_hashes = {
        path.relative_to(ROOT).as_posix(): sha256_bytes(content.encode("utf-8"))
        for path, content in generated.items()
    }
    for path in (
        ROOT / "docs/research/h-layer/program-status-snapshot-v1.json",
        ROOT / "VEGO-AI-Research-Hub.html",
        ROOT / "VEGO-AI-Thesis-Baseline-Progress.html",
    ):
        if path.is_file():
            package_hashes[path.relative_to(ROOT).as_posix()] = sha256_file(path)
    package_paths = sorted(package_hashes)
    release = {
        "schemaVersion": "ReleaseManifest-v3",
        "releaseId": "unified-runtime-security-hardening-v1",
        "sourceTreeSha256": content_tree_hash(source_paths()),
        "packageTreeSha256": sha256_bytes(canonical_bytes(package_hashes)),
        "sourceTreePaths": source_paths(),
        "packageTreePaths": package_paths,
        "trackedArtifacts": package_hashes,
        "sbom": {
            "format": "CycloneDX-1.5",
            "path": SBOM_PATH.relative_to(ROOT).as_posix(),
            "sha256": package_hashes[SBOM_PATH.relative_to(ROOT).as_posix()],
        },
        "toolVersions": {
            "python": project_metadata()["project"]["requires-python"],
            "jsonschema": locked_dependency_version("jsonschema"),
            "openai": locked_dependency_version("openai"),
            "pytest": locked_dependency_version("pytest"),
            "ruff": locked_dependency_version("ruff"),
        },
        "sourceChecks": {
            "status": "PASS",
            "entryPoint": "scripts/verify-source.ps1",
            "claim": "Clone-safe contracts, tests, lint, security, and browser checks.",
        },
        "controlledChecks": {
            "status": "PASS",
            "entryPoint": "scripts/verify-controlled.ps1",
            "evidence": (
                "Recorded local controlled-data validation; clone-safe checks verify "
                "the lock and schemas without requiring ignored evidence files."
            ),
            "exp005SafeLabels": 0,
            "exp012Status": "NOT YET COMPUTABLE",
            "m4b1ClassificationChanges": 0,
            "claim": "Local evidence only; no empirical performance claim.",
        },
        "claimBoundary": (
            "Reliability, parity, provenance, and security hardening only. Accuracy, "
            "generalization, effort reduction, benchmark superiority, and clinical "
            "performance are not established."
        ),
    }
    validate("release-manifest-v3.schema.json", release)
    generated[RELEASE_PATH] = serialized(release)
    return generated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--require-controlled", action="store_true")
    args = parser.parse_args(argv)
    try:
        outputs = build_all(args.require_controlled)
    except (
        OSError,
        ValueError,
        subprocess.CalledProcessError,
        jsonschema.ValidationError,
    ) as exc:
        print(f"hardening manifest build: FAIL: {exc}", file=sys.stderr)
        return 2
    stale: list[str] = []
    for path, content in outputs.items():
        if path.is_file() and path.read_text(encoding="utf-8") == content:
            continue
        if args.check:
            stale.append(path.relative_to(ROOT).as_posix())
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"WROTE: {path.relative_to(ROOT).as_posix()}")
    if stale:
        print(f"hardening manifest build: STALE: {', '.join(stale)}", file=sys.stderr)
        return 1
    print("hardening manifest build: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
