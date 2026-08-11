[CmdletBinding()]
<#
.SYNOPSIS
  Publish the clean, supervisor-facing Aug-12 package to Google Drive and/or the
  Obsidian vault, and keep Ali's private prep material OUT of the shared folder.

  Two audiences, two destinations:
    * SHARED  -> "<root>\VEGO-AI PhD\2026-08-12 Supervisor Package" — numbered,
      supervisor-ready files only (Word/Excel/PDF/PowerPoint; no Markdown, no
      internal governance artifacts).
    * PRIVATE -> "<root>\VEGO-AI PhD\_Ali private (do not share)" — presenter
      script, anticipated-Q&A rebuttal prep, machine transcript, work report.

  Rebuilds the shared folder from scratch each run so removed files do not linger
  in a folder that may already be shared with the supervisors.

.EXAMPLE
  .\scripts\publish-supervisor-package.ps1 -DriveRoot "G:\My Drive"
#>
param(
  [string]$VaultRoot = "C:\Users\ahamed\OneDrive - Parallel Wireless\Documents\Obsidian Vault",
  [string]$DriveRoot = "",
  [switch]$SkipVault
)

$ErrorActionPreference = "Stop"
$repo = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$out = Join-Path $repo "outputs\aug12-supervisor-delivery-2026-08-10"
$sharedName = "VEGO-AI PhD\2026-08-12 Supervisor Package"
$privateName = "VEGO-AI PhD\_Ali private (do not share)"

# Supervisor-facing only. (repo-relative source, published name)
$shared = @(
  @("$out\VEGO-AI-00-README-2026-08-12.pdf",                              "00 - README - Start Here.pdf"),
  @("$out\VEGO-AI-00-README-2026-08-12.docx",                             "00 - README - Start Here.docx"),
  @("$out\VEGO-AI-Executive-Brief-2026-08-12.pdf",                        "01 - Executive Brief (EN + HE).pdf"),
  @("$out\VEGO-AI-Executive-Brief-2026-08-12.docx",                       "01 - Executive Brief (EN + HE).docx"),
  @("$out\VEGO-AI-Chapter-3-Gap-and-Research-Questions-2026-08-12.docx",  "02 - Chapter 3 - Gap and Research Questions.docx"),
  @("$out\VEGO-AI-Chapter-3-Gap-and-Research-Questions-2026-08-12.pdf",   "02 - Chapter 3 - Gap and Research Questions.pdf"),
  @("$out\VEGO-AI-Per-RQ-Literature-2026-08-12.xlsx",                     "03 - Literature Review - Per Research Question.xlsx"),
  @("presentations\VEGO-AI-Aug12-Progress-Review-2026-08-12.pptx",        "04 - Progress Presentation.pptx"),
  @("$out\VEGO-AI-Aug12-Progress-Review-2026-08-12.pdf",                  "04 - Progress Presentation.pdf"),
  @("$out\VEGO-AI-Requirements-and-Tracking-2026-08-12.xlsx",             "05 - Requirements and Progress Tracking.xlsx")
)

# Ali's own prep — deliberately never published to the shared folder.
$private = @(
  @("docs\research\meetings\2026-08-12-walkthrough-outline.md",           "Presenter walkthrough script.md"),
  @("$out\VEGO-AI-Anticipated-QA-2026-08-12.docx",                        "Anticipated Q&A - rebuttal prep.docx"),
  @("docs\research\meetings\2026-08-05-supervisor-meeting.md",            "Canonical meeting record (machine transcript, unreviewed).md"),
  @("docs\research\meetings\2026-08-10-work-report.md",                   "Work report (internal).md"),
  @("docs\research\meetings\2026-08-05-master-plan.md",                   "Master plan (internal).md"),
  @("docs\research\meetings\2026-08-12-delivery-index.md",                "Delivery index and hashes (internal).md")
)

function Resolve-Src([string]$p) {
  if ([System.IO.Path]::IsPathRooted($p)) { return $p }
  return (Join-Path $repo $p)
}

function Publish-Set($root, $folderName, $items, [switch]$Rebuild) {
  $dest = Join-Path $root $folderName
  if ($Rebuild -and (Test-Path -LiteralPath $dest)) {
    Remove-Item -LiteralPath $dest -Recurse -Force
  }
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  $n = 0
  foreach ($item in $items) {
    $src = Resolve-Src $item[0]
    if (Test-Path -LiteralPath $src) {
      Copy-Item -LiteralPath $src -Destination (Join-Path $dest $item[1]) -Force
      $n++
    } else {
      Write-Warning "missing (regenerate it first): $($item[0])"
    }
  }
  Write-Output "  $dest  ->  $n file(s)"
  return $dest
}

$targets = @()
if (-not $SkipVault) {
  if (Test-Path -LiteralPath $VaultRoot) { $targets += $VaultRoot }
  else { Write-Warning "vault root not found: $VaultRoot (skipping)" }
}
if ($DriveRoot) {
  if (Test-Path -LiteralPath $DriveRoot) { $targets += $DriveRoot }
  else { throw "Drive root not found: $DriveRoot. Is Google Drive for Desktop mounted?" }
}

foreach ($root in $targets) {
  Write-Output "publishing to $root"
  Publish-Set $root $sharedName $shared -Rebuild | Out-Null
  Publish-Set $root $privateName $private | Out-Null
}

Write-Output ""
Write-Output "Share ONLY the '2026-08-12 Supervisor Package' folder with Iris and Arnon (Viewer)."
Write-Output "The '_Ali private (do not share)' folder holds presenter notes and rebuttal prep - keep it unshared."
