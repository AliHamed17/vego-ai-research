# Render the Study 1C correction report and figure guide, then rasterise every page so the
# right-to-left layout is inspected rather than assumed.
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

$root = Split-Path -Parent $PSScriptRoot
$docs = Join-Path $root "docs\research\phd-proposal"
$figures = Join-Path $docs "figures"
$render = Join-Path $env:TEMP "study1c-correction-render"
$profileRoot = Join-Path $env:TEMP "study1c-correction-chrome"
New-Item -ItemType Directory -Force -Path $render, $profileRoot | Out-Null
Get-ChildItem $render -Filter *.png -ErrorAction SilentlyContinue | Remove-Item -Force

$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $chrome)) { throw "Chrome not found at $chrome" }

$jobs = @(
    @{ Html = "study1c-correction-he.html";   Pdf = "2026-09-09-study1c-correction-he.pdf" },
    @{ Html = "study1c-figure-guide-he.html"; Pdf = "2026-09-09-study1c-figure-guide-he.pdf" }
)
foreach ($job in $jobs) {
    $src = Join-Path $figures $job.Html
    $out = Join-Path $docs $job.Pdf
    if (-not (Test-Path $src)) { throw "missing generated HTML: $src" }
    if (Test-Path $out) { Remove-Item -LiteralPath $out -Force }
    Write-Output "== printing $($job.Pdf)"
    $url = "file:///" + ($src -replace '\\', '/')
    $jobProfile = Join-Path $profileRoot ([guid]::NewGuid().ToString("N"))
    $chromeArgs = @("--headless=new", "--disable-gpu", "--no-first-run",
        "--no-default-browser-check", "--disable-extensions", "--no-pdf-header-footer",
        "--user-data-dir=$jobProfile", "--print-to-pdf=$out", $url)
    & $chrome @chromeArgs
    $deadline = (Get-Date).AddSeconds(60)
    while (-not (Test-Path $out) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 300 }
    Remove-Item -LiteralPath $jobProfile -Recurse -Force -ErrorAction SilentlyContinue
    if (-not (Test-Path $out)) { throw "Chrome did not produce $out" }
    Write-Output "   $([math]::Round((Get-Item $out).Length / 1KB)) KB"
}

Write-Output "== rasterising every page for visual inspection"
& py -3.13 -c @"
import pathlib, pymupdf
docs = pathlib.Path(r'$docs')
out = pathlib.Path(r'$render')
for name, tag in (('2026-09-09-study1c-correction-he.pdf', 'correction'),
                  ('2026-09-09-study1c-figure-guide-he.pdf', 'guide')):
    pdf = pymupdf.open(docs / name)
    for i, page in enumerate(pdf, 1):
        page.get_pixmap(dpi=96).save(out / f'{tag}-{i:02d}.png')
    print(f'{name}: {pdf.page_count} pages')
"@
if ($LASTEXITCODE -ne 0) { throw "rasterisation failed" }
Write-Output "== page images: $render"
