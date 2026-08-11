[CmdletBinding()]
<#
.SYNOPSIS
  Publish the professionally formatted (Word + PDF + Excel) document set into the
  canonical private PhD working Drive, "VEGO-AI PhD Working 2026".

  Supersedes publish-working-drive.ps1, which copied raw Markdown. Markdown renders
  as unformatted text with # and | symbols in Drive - unsuitable for a research
  workspace that supervisors may be given access to. Every document is now published
  in Word (editable) and PDF (universally openable); wide registers stay in Excel.

  Each folder receives a "00 - Folder Overview" document stating that folder's honest
  current state. Any legacy _README.md and *.md files this project previously
  published are removed from the destination folders.

  Boundary rules (workspace manifest + phd-data-boundary.md) are unchanged: no patient
  rows, no MIMIC/Clalit extracts, no clinical derivatives, no credentials; the supplied
  MIMIC source folder is linked, never copied; native Google files are never touched.

.PARAMETER ProDocsRoot
  Directory holding the built <folder>\<name>.docx/.pdf tree.

.EXAMPLE
  .\scripts\publish-working-drive-pro.ps1 -WorkingRoot "G:\My Drive\VEGO-AI PhD Working 2026" -ProDocsRoot "<scratch>\prodocs"
#>
param(
  [Parameter(Mandatory = $true)][string]$WorkingRoot,
  [Parameter(Mandatory = $true)][string]$ProDocsRoot,
  [switch]$KeepMarkdown
)

$ErrorActionPreference = "Stop"
$repo = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$out = Join-Path $repo "outputs\aug12-supervisor-delivery-2026-08-10"

foreach ($p in @($WorkingRoot, $ProDocsRoot)) {
  if (-not (Test-Path -LiteralPath $p)) { throw "path not found: $p" }
}

# Excel workbooks and the supervisor package keep their existing homes.
# Objects, not nested arrays: PowerShell unrolls a single-element array of arrays,
# which silently turns @("path","name") into its first character.
function New-Extra([string]$Src, [string]$Name) {
  [pscustomobject]@{ Src = $Src; Name = $Name }
}
$extras = @{
  "00_Admin_and_Decisions"  = @(
    (New-Extra "$out\VEGO-AI-Requirements-and-Tracking-2026-08-12.xlsx" "Requirements and Progress Tracking.xlsx")
  )
  "02_PhD_Proposal"         = @(
    (New-Extra "$out\VEGO-AI-Chapter-3-Gap-and-Research-Questions-2026-08-12.docx" "Chapter 3 - Gap and Research Questions.docx"),
    (New-Extra "$out\VEGO-AI-Chapter-3-Gap-and-Research-Questions-2026-08-12.pdf" "Chapter 3 - Gap and Research Questions.pdf"),
    (New-Extra "$out\VEGO-AI-Executive-Brief-2026-08-12.docx" "Executive Brief (EN + HE).docx"),
    (New-Extra "$out\VEGO-AI-Executive-Brief-2026-08-12.pdf" "Executive Brief (EN + HE).pdf")
  )
  "03_Literature_Review"    = @(
    (New-Extra "$out\VEGO-AI-Per-RQ-Literature-2026-08-12.xlsx" "Literature Review - Per Research Question.xlsx")
  )
}

$aug12 = @(
  @("$out\VEGO-AI-00-README-2026-08-12.pdf", "00 - README - Start Here.pdf"),
  @("$out\VEGO-AI-00-README-2026-08-12.docx", "00 - README - Start Here.docx"),
  @("$out\VEGO-AI-Executive-Brief-2026-08-12.pdf", "01 - Executive Brief (EN + HE).pdf"),
  @("$out\VEGO-AI-Executive-Brief-2026-08-12.docx", "01 - Executive Brief (EN + HE).docx"),
  @("$out\VEGO-AI-Chapter-3-Gap-and-Research-Questions-2026-08-12.docx", "02 - Chapter 3 - Gap and Research Questions.docx"),
  @("$out\VEGO-AI-Chapter-3-Gap-and-Research-Questions-2026-08-12.pdf", "02 - Chapter 3 - Gap and Research Questions.pdf"),
  @("$out\VEGO-AI-Per-RQ-Literature-2026-08-12.xlsx", "03 - Literature Review - Per Research Question.xlsx"),
  @("presentations\VEGO-AI-Aug12-Progress-Review-2026-08-12.pptx", "04 - Progress Presentation.pptx"),
  @("$out\VEGO-AI-Aug12-Progress-Review-2026-08-12.pdf", "04 - Progress Presentation.pdf"),
  @("$out\VEGO-AI-Requirements-and-Tracking-2026-08-12.xlsx", "05 - Requirements and Progress Tracking.xlsx")
)

function Resolve-Src([string]$p) {
  if ([System.IO.Path]::IsPathRooted($p)) { return $p }
  return (Join-Path $repo $p)
}

$folders = @("00_Admin_and_Decisions", "01_Research_Questions", "02_PhD_Proposal",
  "03_Literature_Review", "04_SE_Modeling_Studies", "05_Medical_Feasibility_Gated",
  "06_Weekly_Meetings", "07_Submission_Package", "99_Archive")

$totalDocs = 0
foreach ($folder in $folders) {
  $dest = Join-Path $WorkingRoot $folder
  New-Item -ItemType Directory -Force -Path $dest | Out-Null

  # Clear previously published Markdown so the folder shows Office documents only.
  if (-not $KeepMarkdown) {
    Get-ChildItem -LiteralPath $dest -Filter *.md -File -ErrorAction SilentlyContinue |
      Remove-Item -Force -ErrorAction SilentlyContinue
  }

  $srcDir = Join-Path $ProDocsRoot $folder
  $n = 0
  if (Test-Path -LiteralPath $srcDir) {
    Get-ChildItem -LiteralPath $srcDir -File | Where-Object { $_.Extension -in ".docx", ".pdf" } | ForEach-Object {
      Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $dest $_.Name) -Force
      $n++
    }
  }
  if ($extras.ContainsKey($folder)) {
    foreach ($item in @($extras[$folder])) {
      $src = Resolve-Src $item.Src
      if (Test-Path -LiteralPath $src) {
        Copy-Item -LiteralPath $src -Destination (Join-Path $dest $item.Name) -Force
        $n++
      } else { Write-Warning "missing: $($item.Src)" }
    }
  }
  Write-Output ("{0,-32} {1,3} file(s)" -f $folder, $n)
  $totalDocs += $n
}

# Supervisor package subfolder
$pkg = Join-Path $WorkingRoot "06_Weekly_Meetings\2026-08-12 Supervisor Package"
New-Item -ItemType Directory -Force -Path $pkg | Out-Null
$p = 0
foreach ($item in $aug12) {
  $src = Resolve-Src $item[0]
  if (Test-Path -LiteralPath $src) { Copy-Item -LiteralPath $src -Destination (Join-Path $pkg $item[1]) -Force; $p++ }
  else { Write-Warning "missing: $($item[0])" }
}
Write-Output ("{0,-32} {1,3} file(s)" -f "  06/2026-08-12 Package", $p)
$totalDocs += $p

Write-Output ""
Write-Output "total files published: $totalDocs"
Write-Output "Every document is provided in Word and PDF; registers stay in Excel."
Write-Output "Native Google files (e.g. the literature .gsheet) were not touched."
