# Rebuild the course deck, export it to PDF via PowerPoint COM, and rasterise
# every slide for visual QA. LibreOffice is not installed on this machine, so
# COM automation is the only reliable PPTX -> PDF path here.
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

$root = "C:\Users\ahamed\vego-ai\outputs\course-presentation"
$pptx = Join-Path $root "VEGO-AI - IS Research Seminar - Final Presentation.pptx"
$pdf = Join-Path $root "deck.pdf"

python "C:\Users\ahamed\vego-ai\scripts\build_course_presentation.py"

if (Test-Path $pdf) { Remove-Item $pdf -Force }
$pp = New-Object -ComObject PowerPoint.Application
try {
    $pres = $pp.Presentations.Open($pptx, $true, $false, $false)
    $pres.SaveAs($pdf, 32)
    $pres.Close()
} finally {
    $pp.Quit()
}

python -c @'
import pathlib, pymupdf
p = pathlib.Path(r"C:\Users\ahamed\vego-ai\outputs\course-presentation")
out = p / "render"; out.mkdir(exist_ok=True)
for f in out.glob("*.png"): f.unlink()
doc = pymupdf.open(p / "deck.pdf")
for i, page in enumerate(doc, 1):
    page.get_pixmap(dpi=110).save(out / f"slide-{i:02d}.png")
print(f"rendered {doc.page_count} slides -> {out}")
'@
