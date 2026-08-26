from __future__ import annotations

import csv
import io
import json
import shutil
import subprocess
from pathlib import Path

import pytest


def _libreoffice_pids() -> set[int]:
    pids: set[int] = set()
    for image_name in ("soffice.exe", "soffice.bin"):
        completed = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {image_name}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            continue
        for row in csv.reader(io.StringIO(completed.stdout)):
            if len(row) >= 2 and row[0].casefold() == image_name.casefold():
                pids.add(int(row[1]))
    return pids


@pytest.mark.slow
def test_workspace_renderer_verify_is_idempotent_and_path_free() -> None:
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell 7 is unavailable")
    root = Path(__file__).resolve().parents[2]
    runtime = root / ".cache" / "libreoffice-24.2.7.2" / "admin"
    if not (runtime / "program" / "soffice.com").is_file():
        pytest.skip("workspace-local renderer has not been bootstrapped")
    script = root / "scripts" / "bootstrap_proposal_renderer.ps1"
    command = [
        pwsh,
        "-NoProfile",
        "-NonInteractive",
        "-File",
        str(script),
        "-RuntimeRoot",
        str(runtime),
        "-VerifyOnly",
    ]
    profiles_before = set((root / ".cache").glob("renderer-version-profile-*"))
    processes_before = _libreoffice_pids()

    first = subprocess.run(command, capture_output=True, text=True, check=False, timeout=45)
    second = subprocess.run(command, capture_output=True, text=True, check=False, timeout=45)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert json.loads(first.stdout) == json.loads(second.stdout)
    payload = json.loads(first.stdout)
    assert payload["passed"] is True
    assert payload["renderer"]["version"] == "24.2.7.2"
    assert payload["renderer"]["version_output"].startswith("LibreOffice 24.2.7.2 ")
    assert payload["renderer"]["engine_contract"] == {
        "algorithm": "sha256-path-size-content-v1",
        "scope": [
            "program/* (top-level files only)",
            "program/services/** (all files)",
            "share/registry/** (all files)",
            "share/fonts/truetype/** (all files)",
        ],
        "file_count": 695,
        "total_bytes": 513_933_334,
        "tree_sha256": "48767A72AF829695A407B94A9829F5FC0B6779B4B01E585C0F1BB3A105F2EAD5",
    }
    assert payload["fonts"]["count"] == 8
    assert set((root / ".cache").glob("renderer-version-profile-*")) == profiles_before
    assert _libreoffice_pids() <= processes_before
    serialized = json.dumps(payload)
    assert str(root) not in serialized
    assert str(runtime) not in serialized
