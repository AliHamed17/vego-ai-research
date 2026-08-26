from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HELPERS = ROOT / "scripts" / "proposal_renderer_helpers.ps1"


def _pwsh() -> str:
    executable = shutil.which("pwsh")
    if executable is None:
        pytest.skip("PowerShell 7 is unavailable")
    return executable


def _driver(tmp_path: Path, body: str, name: str = "driver.ps1") -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def _engine_contract(root: Path) -> dict[str, object]:
    rows: list[tuple[str, int, str]] = []
    candidates = set(path for path in (root / "program").iterdir() if path.is_file())
    for relative in (
        Path("program/services"),
        Path("share/registry"),
        Path("share/fonts/truetype"),
    ):
        scope_root = root / relative
        if scope_root.is_dir():
            candidates.update(path for path in scope_root.rglob("*") if path.is_file())
    for path in candidates:
        payload = path.read_bytes()
        rows.append((path.relative_to(root).as_posix(), len(payload), _sha256(payload)))
    rows.sort(key=lambda item: item[0].encode())
    digest = hashlib.sha256()
    for relative, size, file_hash in rows:
        digest.update(f"{relative}\0{size}\0{file_hash}\n".encode())
    return {
        "algorithm": "sha256-path-size-content-v1",
        "scope": [
            "program/* (top-level files only)",
            "program/services/** (all files)",
            "share/registry/** (all files)",
            "share/fonts/truetype/** (all files)",
        ],
        "file_count": len(rows),
        "total_bytes": sum(row[1] for row in rows),
        "tree_sha256": digest.hexdigest().upper(),
    }


def test_powershell_engine_contract_matches_independent_python_contract(
    tmp_path: Path,
) -> None:
    runtime = tmp_path / "runtime"
    files = {
        "program/soffice.com": b"launcher",
        "program/soffice.bin": b"engine",
        "program/services/scriptframe.dll": b"service",
        "share/registry/writer.xcd": b"writer-pdf-filter-registry",
        "share/fonts/truetype/Carlito-Regular.ttf": b"font",
        "share/config/images.zip": b"excluded-resource",
    }
    for relative, payload in files.items():
        path = runtime / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    driver = _driver(
        tmp_path,
        """param([string]$Helpers, [string]$Runtime)
. $Helpers
Get-ProposalRendererEngineContract -RuntimeRoot $Runtime | ConvertTo-Json -Depth 10
""",
    )

    completed = subprocess.run(
        [
            _pwsh(),
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(driver),
            str(HELPERS),
            str(runtime),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == _engine_contract(runtime)


def test_bounded_process_timeout_kills_process_and_cleans_scratch(tmp_path: Path) -> None:
    spaced = tmp_path / "path with spaces"
    spaced.mkdir()
    marker = spaced / "should-not-exist.txt"
    scratch = spaced / "scratch files"
    target = _driver(
        spaced,
        """param([string]$Marker)
Start-Sleep -Seconds 4
[System.IO.File]::WriteAllText($Marker, 'orphaned')
""",
        "slow-target.ps1",
    )
    driver = _driver(
        tmp_path,
        """param(
    [string]$Helpers,
    [string]$Executable,
    [string]$Target,
    [string]$Marker,
    [string]$Scratch
)
. $Helpers
$arguments = @('-NoProfile', '-NonInteractive', '-File', $Target, $Marker)
Invoke-ProposalBoundedProcess `
    -FilePath $Executable `
    -ArgumentList $arguments `
    -TimeoutSeconds 1 `
    -ScratchRoot $Scratch | Out-Null
""",
    )

    completed = subprocess.run(
        [
            _pwsh(),
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(driver),
            str(HELPERS),
            _pwsh(),
            str(target),
            str(marker),
            str(scratch),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=12,
    )

    assert completed.returncode != 0
    assert "timed out" in completed.stderr.casefold()
    time.sleep(4.5)
    assert not marker.exists()
    assert not list(scratch.glob("proposal-process-*"))


def test_atomic_copy_is_concurrency_safe_and_cleans_losing_stage(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    payload = (b"atomic-copy-contract" * 512_000) + b"end"
    source.write_bytes(payload)
    destination = tmp_path / "output" / "proposal.docx"
    destination.parent.mkdir()
    driver = _driver(
        tmp_path,
        """param([string]$Helpers, [string]$Source, [string]$Destination)
. $Helpers
Copy-ProposalSharedFileNew -Source $Source -Destination $Destination
""",
    )
    command = [
        _pwsh(),
        "-NoProfile",
        "-NonInteractive",
        "-File",
        str(driver),
        str(HELPERS),
        str(source),
        str(destination),
    ]

    processes = [
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for _ in range(2)
    ]
    results = [process.communicate(timeout=30) + (process.returncode,) for process in processes]

    assert sorted(result[2] for result in results) == [0, 1]
    assert destination.read_bytes() == payload
    assert not list(destination.parent.glob(f".{destination.name}.copy-*.tmp"))


def test_atomic_copy_never_removes_or_changes_preexisting_destination(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    destination = tmp_path / "proposal.docx"
    source.write_bytes(b"new")
    destination.write_bytes(b"owned-by-another-run")
    driver = _driver(
        tmp_path,
        """param([string]$Helpers, [string]$Source, [string]$Destination)
. $Helpers
Copy-ProposalSharedFileNew -Source $Source -Destination $Destination
""",
    )

    completed = subprocess.run(
        [
            _pwsh(),
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(driver),
            str(HELPERS),
            str(source),
            str(destination),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )

    assert completed.returncode != 0
    assert destination.read_bytes() == b"owned-by-another-run"
    assert not list(tmp_path.glob(f".{destination.name}.copy-*.tmp"))


def test_production_integration_uses_bounded_atomic_libreoffice_boundary() -> None:
    script = (ROOT / "scripts" / "integrate_proposal_visuals.ps1").read_text(
        encoding="utf-8"
    )
    helpers = HELPERS.read_text(encoding="utf-8")

    assert "Invoke-ProposalLibreOfficePdfExport" in script
    assert "LibreOfficeExportTimeoutSeconds" in script
    assert "& $libreOfficePath" not in script
    assert "$createdDerivedDocx" in script
    assert "$createdDerivedPdf" in script
    assert "$createdIntegrationReceipt" in script
    assert "Start-Process" in helpers
    assert "-WindowStyle Hidden" in helpers
    assert "$process.Kill($true)" in helpers
    assert ".proposal-pdf-stage-" in helpers
    assert "Move-Item -LiteralPath $stagePdf -Destination $destinationPath" in helpers
