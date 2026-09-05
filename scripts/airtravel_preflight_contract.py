"""Pure preflight grant, identity and receipt contracts. No runtime import."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "c34d3954b5e080d090017d2ea655d454d75a6b92"
PARENT = "3727acfe2130863ab6b737824a1718e7b3648b92"
SETTING = "cd_airtravel"
CORPUS = "text2uml_airtravel_253b26dc"
MODEL = "LOCAL_DETERMINISTIC_FAKE_V3"
TIMEOUT = 1800
MAX_FILES = 40
MAX_BYTES = 16 * 1024 * 1024
PACKET = "docs/research/phd-proposal/2026-09-05-airtravel-protected-fake-preflight-authorization-packet-v3.md"
GRANT_SCHEMA = "schemas/airtravel-fake-grant-v1.schema.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()


def git(root: Path, *args: str) -> str:
    executable = shutil.which("git")
    if not executable:
        raise ValueError("git unavailable")
    return subprocess.run(
        [executable, *args], cwd=root, check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout.strip()


def protected_hashes(root: Path) -> dict:
    policy = ast.parse(
        (root / "scripts/check_hlayer_change_authorization.py").read_text(encoding="utf-8")
    )
    prefixes = next(
        ast.literal_eval(n.value)
        for n in policy.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "PROTECTED_PREFIXES" for t in n.targets)
    )
    paths = [p for p in git(root, "ls-files").splitlines() if p.startswith(prefixes)]
    result = {}
    executable = shutil.which("git")
    for path in paths:
        no_links(root / path)
        original = subprocess.run(
            [executable, "show", f"{BASE}:{path}"], cwd=root, check=True, capture_output=True
        ).stdout
        observed = digest(root / path)
        if hashlib.sha256(original).hexdigest() != observed:
            raise ValueError("protected source differs from green main")
        result[path] = observed
    return result


def no_links(path: Path) -> None:
    absolute = path.absolute()
    for p in (absolute, *absolute.parents):
        if not p.exists() and not p.is_symlink():
            continue
        info = p.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("symlink/reparse path forbidden")


def output_path(path: Path, root: Path, *, empty: bool = True) -> Path:
    no_links(path)
    output = path.resolve()
    relative = output.relative_to((root / "external_data").resolve())
    if len(relative.parts) < 2 or any(p in {"", ".", ".."} for p in relative.parts):
        raise ValueError("dedicated external_data child required")
    if empty and output.exists() and any(output.iterdir()):
        raise ValueError("output must be empty")
    return output


def receipt_path(path: Path, output: Path) -> Path:
    no_links(path)
    if path.resolve() != output.resolve() / "preflight-receipt.json":
        raise ValueError("receipt must be the fixed child of output")
    return path


def counters() -> dict:
    return {
        "protected_orchestrator_fake_route_count": "NOT_EXECUTED",
        "provider_backed_production_route_count": 0,
        "external_provider_call_count": 0,
        "network_attempt_count": 0,
        "detector_v1_run_count": 0,
        "baseline_fake_call_count": 0,
        "instrumented_fake_call_count": 0,
        "combined_fake_call_count": 0,
    }


def check_counts(baseline: int, instrumented: int) -> dict:
    from study1_call_bound import minimum_calls, worst_case_calls

    low, high = minimum_calls(4), worst_case_calls(4)
    if any(type(n) is not int or not low <= n <= high for n in (baseline, instrumented)):
        raise ValueError("each baseline/instrumented count must be within 16..326")
    return {
        "baseline_fake_call_count": baseline,
        "instrumented_fake_call_count": instrumented,
        "combined_fake_call_count": baseline + instrumented,
        "external_provider_call_count": 0,
    }


def validate_grant(grant: dict, expected: dict, *, now=None) -> None:
    from jsonschema import Draft202012Validator, FormatChecker

    schema = json.loads((ROOT / GRANT_SCHEMA).read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(grant))
    if errors or grant.get("status") != "GRANTED":
        raise ValueError("grant schema/status rejected")
    if any(grant.get(key) != value for key, value in expected.items()):
        raise ValueError("grant binding mismatch")
    if type(grant["N"]) is not int or grant["N"] != 4:
        raise ValueError("grant N must be integer four")
    now = now or datetime.now(timezone.utc)
    start = datetime.fromisoformat(grant["granted_at"].replace("Z", "+00:00"))
    expiry = datetime.fromisoformat(grant["expires_at"].replace("Z", "+00:00"))
    if not start.tzinfo or not expiry.tzinfo or not start <= now < expiry:
        raise ValueError("grant not current")


def load_packet(path: Path, root: Path) -> dict:
    no_links(path)
    if path.resolve() != (root / PACKET).resolve():
        raise ValueError("arbitrary packet refused")
    text = path.read_text(encoding="utf-8")
    matches = re.findall(r"<!-- AIRTRAVEL_PACKET_V3\n(.*?)\n-->", text, re.S)
    if len(matches) != 1:
        raise ValueError("reviewed packet structure missing")
    packet = json.loads(matches[0])
    if packet.get("status") != "AUTHORIZATION_REQUESTED_NOT_GRANTED":
        raise ValueError("packet superseded or unrecognized")
    if packet.get("base_sha") != BASE:
        raise ValueError("packet base drift")
    for group in ("protected_hashes", "code_hashes"):
        if not packet.get(group):
            raise ValueError("packet hashes missing")
        for relative, sha in packet[group].items():
            target = root / relative
            no_links(target)
            if not target.resolve().is_relative_to(root.resolve()) or digest(target) != sha:
                raise ValueError("packet content hash drift")
    return packet


def execution_tokens(runtime_root, archive, output, packet, grant, root=ROOT) -> list[str]:
    # Interpreter path is not a secret; the exact private command records it.
    import sys

    return [
        str(Path(sys.executable).resolve()),
        str(root / "scripts/prepare_airtravel_protected_fake_preflight.py"),
        "--execute",
        "--authorization-packet",
        str(packet.resolve()),
        "--authorization-grant",
        str(grant.resolve()),
        "--runtime-root",
        str(runtime_root.resolve()),
        "--runtime-archive",
        str(archive.resolve()),
        "--output-dir",
        str(output.resolve()),
        "--receipt",
        str(output.resolve() / "preflight-receipt.json"),
    ]


def authorize(runtime_root, archive, output, packet_path, grant_path, root=ROOT) -> dict:
    if grant_path is None or not grant_path.is_file():
        raise ValueError("separate authorization grant required")
    packet = load_packet(packet_path, root)
    no_links(grant_path)
    output = output_path(output, root)
    if git(root, "rev-parse", "origin/main") != BASE or git(root, "status", "--porcelain"):
        raise ValueError("main moved or checkout not clean")
    commit = git(root, "rev-parse", "HEAD")
    if git(root, "merge-base", PARENT, commit) != PARENT:
        raise ValueError("not a PR38 descendant")
    tokens = execution_tokens(runtime_root, archive, output, packet_path, grant_path, root)
    expected = {
        "commit": commit,
        "packet_sha256": digest(packet_path),
        "harness_sha256": digest(root / "scripts/prepare_airtravel_protected_fake_preflight.py"),
        "runtime_archive_sha256": digest(archive),
        "setting_id": SETTING,
        "corpus_id": CORPUS,
        "N": 4,
        "output_dir": str(output),
        "protected_hashes": packet["protected_hashes"],
        "command_sha256": hashlib.sha256(canonical(tokens)).hexdigest(),
    }
    grant = json.loads(grant_path.read_text(encoding="utf-8"))
    validate_grant(grant, expected)
    return {**expected, "grant_sha256": digest(grant_path), "model": MODEL}
