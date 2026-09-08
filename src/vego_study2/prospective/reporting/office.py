"""PDF export through the locally installed Office applications (Windows only)."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

_WORD = r"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {{
  $doc = $word.Documents.Open("{src}", $false, $true)
  $doc.ExportAsFixedFormat("{dst}", 17)
  $doc.Close(0)
}} finally {{ $word.Quit() }}
"""

_POWERPOINT = r"""
$app = New-Object -ComObject PowerPoint.Application
try {{
  $pres = $app.Presentations.Open("{src}", $true, $false, $false)
  $pres.SaveAs("{dst}", 32)
  $pres.Close()
}} finally {{ $app.Quit() }}
"""


def _export(script: str, src: Path, dst: Path) -> Path:
    src = src.resolve()
    tmp_dir = Path(tempfile.mkdtemp(prefix="vego-office-"))
    tmp_pdf = tmp_dir / (dst.stem + ".pdf")
    command = script.format(src=str(src).replace("/", "\\"), dst=str(tmp_pdf).replace("/", "\\"))
    subprocess.run(["pwsh", "-NoProfile", "-Command", command], check=True, capture_output=True, text=True, timeout=300)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(tmp_pdf), str(dst))
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return dst


def docx_to_pdf(src: Path, dst: Path) -> Path:
    return _export(_WORD, src, dst)


def pptx_to_pdf(src: Path, dst: Path) -> Path:
    return _export(_POWERPOINT, src, dst)
