[CmdletBinding()]
<#
.SYNOPSIS
  Copy the Aug-12 supervisor delivery package to an Obsidian vault folder and/or a
  Google Drive (Drive-for-Desktop) mount. No cloud API or credentials are used — this
  just copies files into folders the user has already connected (OneDrive-backed vault,
  or a mounted Drive letter). See docs/research/meetings/2026-08-12-delivery-index.md.

.EXAMPLE
  .\scripts\push-supervisor-package.ps1
  # refreshes the Obsidian vault folder only (default vault path)

.EXAMPLE
  .\scripts\push-supervisor-package.ps1 -DriveRoot "G:\My Drive"
  # also copies the deliverables into Google Drive (Drive for Desktop mounted at G:)
#>
param(
  [string]$VaultRoot = "C:\Users\ahamed\OneDrive - Parallel Wireless\Documents\Obsidian Vault",
  [string]$DriveRoot = "",
  [switch]$SkipVault
)

$ErrorActionPreference = "Stop"
$repo = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$folderName = "VEGO-AI PhD\2026-08-12 Supervisor Package"

# (repo-relative source, destination filename)
$notes = @(
  @("docs\research\meetings\2026-08-12-delivery-index.md", "Delivery Index.md"),
  @("docs\research\phd-proposal\chapter-3-gap-and-research-questions-draft.md", "Chapter 3 - Gap and Research Questions.md"),
  @("docs\research\meetings\2026-08-05-master-plan.md", "Master Plan (bilingual).md"),
  @("literature\per-rq-literature-map.md", "Per-RQ Literature Map.md"),
  @("docs\research\meetings\2026-08-12-walkthrough-outline.md", "Aug-12 Walkthrough Script.md"),
  @("docs\research\meetings\2026-08-10-work-report.md", "Work Report (bilingual).md"),
  @("docs\research\meetings\2026-08-05-supervisor-meeting.md", "Canonical Meeting Record (Aug 5).md")
)
$binaries = @(
  "presentations\VEGO-AI-Aug12-Progress-Review-2026-08-12.pptx",
  "outputs\aug12-supervisor-delivery-2026-08-10\VEGO-AI-Aug12-Progress-Review-2026-08-12.pdf",
  "outputs\aug12-supervisor-delivery-2026-08-10\VEGO-AI-Per-RQ-Literature-2026-08-12.xlsx",
  "outputs\aug12-supervisor-delivery-2026-08-10\VEGO-AI-Chapter-3-Gap-and-Research-Questions-2026-08-12.docx"
)

function Publish-To($root, [switch]$IncludeNotes) {
  $dest = Join-Path $root $folderName
  $att = Join-Path $dest "attachments"
  New-Item -ItemType Directory -Force -Path $att | Out-Null
  if ($IncludeNotes) {
    foreach ($n in $notes) {
      $src = Join-Path $repo $n[0]
      if (Test-Path -LiteralPath $src) { Copy-Item -LiteralPath $src -Destination (Join-Path $dest $n[1]) -Force }
      else { Write-Warning "missing note source: $($n[0])" }
    }
  }
  foreach ($b in $binaries) {
    $src = Join-Path $repo $b
    if (Test-Path -LiteralPath $src) { Copy-Item -LiteralPath $src -Destination $att -Force }
    else { Write-Warning "missing binary (regenerate it first): $b" }
  }
  Write-Output "published to: $dest"
}

if (-not $SkipVault) {
  if (Test-Path -LiteralPath $VaultRoot) { Publish-To $VaultRoot -IncludeNotes }
  else { Write-Warning "vault root not found: $VaultRoot (skipping vault)" }
}

if ($DriveRoot) {
  if (Test-Path -LiteralPath $DriveRoot) { Publish-To $DriveRoot -IncludeNotes }
  else { throw "Drive root not found: $DriveRoot. Is Google Drive for Desktop mounted? See docs/research/meetings/2026-08-12-delivery-index.md." }
}

Write-Output "done. Share the Drive folder with Iris and Arnon (viewer access) from the Drive UI."
