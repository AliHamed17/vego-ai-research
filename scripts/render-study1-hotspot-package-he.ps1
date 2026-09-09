# Render the Hebrew hotspot package, then rasterise every page so RTL layout is inspected,
# not assumed. Chrome honours the CSS page geometry; PowerPoint COM is the only PPTX->PDF path here.
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

$root = Split-Path -Parent $PSScriptRoot
$docs = Join-Path $root "docs\research\phd-proposal"
$figures = Join-Path $docs "figures"
$render = Join-Path $env:TEMP "study1-hotspot-render"
$chromeProfile = Join-Path $env:TEMP "study1-hotspot-chrome"
New-Item -ItemType Directory -Force -Path $render, $chromeProfile | Out-Null
Get-ChildItem $render -Filter *.png -ErrorAction SilentlyContinue | Remove-Item -Force

$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $chrome)) { throw "Chrome not found at $chrome" }

$jobs = @(
    @{ Html = "study1-hotspot-report-he.html";         Pdf = "2026-09-09-study1-hotspot-report-he.pdf" },
    @{ Html = "study1-hotspot-business-he.html";       Pdf = "2026-09-09-study1-hotspot-business-he.pdf" },
    @{ Html = "study1-hotspot-map-he.html";            Pdf = "2026-09-09-study1-hotspot-map-he.pdf" },
    @{ Html = "study1-hotspot-evidence-index-he.html"; Pdf = "2026-09-09-study1-hotspot-evidence-index-he.pdf" }
)
foreach ($job in $jobs) {
    $src = Join-Path $figures $job.Html
    $out = Join-Path $docs $job.Pdf
    if (-not (Test-Path $src)) { throw "missing generated HTML: $src" }
    if (Test-Path $out) { Remove-Item $out -Force }
    Write-Output "== printing $($job.Pdf)"
    $url = "file:///" + ($src -replace '\\', '/')
    $jobProfile = Join-Path $chromeProfile ([guid]::NewGuid().ToString("N"))
    $chromeArgs = @("--headless=new", "--disable-gpu", "--no-first-run",
        "--no-default-browser-check", "--disable-extensions", "--no-pdf-header-footer",
        "--user-data-dir=$jobProfile", "--print-to-pdf=$out", $url)
    & $chrome @chromeArgs
    $deadline = (Get-Date).AddSeconds(60)
    while (-not (Test-Path $out) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 300 }
    Remove-Item $jobProfile -Recurse -Force -ErrorAction SilentlyContinue
    if (-not (Test-Path $out)) { throw "Chrome did not produce $out" }
    Write-Output "   $([math]::Round((Get-Item $out).Length / 1KB)) KB"
}

$pptx = Join-Path $docs "2026-09-09-study1-hotspot-deck-he.pptx"
$deckPdf = Join-Path $docs "2026-09-09-study1-hotspot-deck-he.pdf"
if (-not (Test-Path $pptx)) { throw "missing generated deck: $pptx" }
if (Test-Path $deckPdf) { Remove-Item $deckPdf -Force }
Write-Output "== exporting deck through PowerPoint COM"
$pp = New-Object -ComObject PowerPoint.Application
try {
    $pres = $pp.Presentations.Open($pptx, $true, $false, $false)
    $pres.SaveAs($deckPdf, 32)
    $pres.Close()
} finally {
    $pp.Quit()
}
if (-not (Test-Path $deckPdf)) { throw "PowerPoint did not produce $deckPdf" }

Write-Output "== rasterising every page for visual inspection"
& py -3.13 -c @"
import pathlib, pymupdf
docs = pathlib.Path(r'$docs')
out = pathlib.Path(r'$render')
names = (('2026-09-09-study1-hotspot-report-he.pdf', 'report'),
         ('2026-09-09-study1-hotspot-deck-he.pdf', 'slide'),
         ('2026-09-09-study1-hotspot-business-he.pdf', 'business'),
         ('2026-09-09-study1-hotspot-map-he.pdf', 'map'),
         ('2026-09-09-study1-hotspot-evidence-index-he.pdf', 'evidence'))
for name, tag in names:
    pdf = pymupdf.open(docs / name)
    for i, page in enumerate(pdf, 1):
        page.get_pixmap(dpi=96).save(out / f'{tag}-{i:02d}.png')
    print(f'{name}: {pdf.page_count} pages')
"@
if ($LASTEXITCODE -ne 0) { throw "rasterisation failed" }
Write-Output "== page images: $render"
