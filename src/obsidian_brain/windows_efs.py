from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

from .vault import efs_output_is_verified


def verify_windows_efs(root: Path, *, run_cipher: Callable[[Path], str] | None = None) -> bool:
    """Verify EFS from an explicit probe-file status and clean up the probe."""

    probe = root / ".encryption-verification-probe"
    probe.touch(exist_ok=True)
    try:
        if run_cipher is None:
            completed = subprocess.run(
                ["cipher.exe", "/c", str(probe)],
                capture_output=True,
                check=False,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            output = f"{completed.stdout}\n{completed.stderr}"
        else:
            output = run_cipher(probe)
        return efs_output_is_verified(output)
    finally:
        if probe.exists():
            probe.unlink()
