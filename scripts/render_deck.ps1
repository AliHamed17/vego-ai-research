# Rebuild the course deck, export it to PDF via PowerPoint COM, and rasterise
# every slide for visual QA. LibreOffice is not installed on this machine, so
# COM automation is the only reliable PPTX -> PDF path here.
#
# Paths are derived from this script's own location, not hard-coded - the repo
# runs from multiple worktrees on this machine, and a fixed path would rebuild
# and overwrite a different checkout's copy of the deck.
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

$repoRoot = Split-Path -Parent $PSScriptRoot
$root = Join-Path $repoRoot "outputs\course-presentation"
$pptx = Join-Path $root "VEGO-AI - IS Research Seminar - Final Presentation.pptx"
$pdf = Join-Path $root "deck.pdf"

python (Join-Path $PSScriptRoot "build_course_presentation.py")

if (Test-Path $pdf) { Remove-Item $pdf -Force }
$pp = New-Object -ComObject PowerPoint.Application
try {
    $pres = $pp.Presentations.Open($pptx, $true, $false, $false)
    $pres.SaveAs($pdf, 32)
    $pres.Close()
} finally {
    $pp.Quit()
}

$renderScript = @'
import pathlib, pymupdf, sys
p = pathlib.Path(sys.argv[1])
out = p / "render"; out.mkdir(exist_ok=True)
for f in out.glob("*.png"): f.unlink()
doc = pymupdf.open(p / "deck.pdf")
for i, page in enumerate(doc, 1):
    page.get_pixmap(dpi=110).save(out / f"slide-{i:02d}.png")
print(f"rendered {doc.page_count} slides -> {out}")
'@
python -c $renderScript $root
