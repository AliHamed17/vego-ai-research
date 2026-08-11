[CmdletBinding()]
<#
.SYNOPSIS
  Reduce the PhD working Drive to only the files needed to do the work.

  The Drive had grown to 145 files, mostly because every document was published in
  BOTH Word and PDF and each folder carried an overview document. This applies an
  explicit keep-list: one format per document (Word, because the proposal is written
  in Word), no folder-overview files, no superseded versions, no internal governance
  artifacts that are never opened while writing, and no empty placeholder folders.

  SAFETY. Every file removed here is regenerable from the repository by
  publish-working-drive-pro.ps1. The only files that are NOT reproducible are
  protected explicitly below and are never touched:
    * the native Google Sheet (.gsheet) - the literature workbook of record;
    * the original MediVARIA one-pager supplied by Iris;
    * the 2026-08-12 Supervisor Package (kept complete, both formats, as it is the
      set that gets shared with the supervisors);
    * the _Ali private folder.

  Removed files go to the Recycle Bin path semantics of the Drive client, i.e. Drive
  trash, where they remain recoverable for 30 days; and in any case can be
  republished from the repo in one command.

.EXAMPLE
  .\scripts\filter-working-drive.ps1 -WhatIfOnly     # show what would go
  .\scripts\filter-working-drive.ps1                # apply
#>
param(
  [string]$WorkingRoot = "G:\My Drive\VEGO-AI PhD Working 2026",
  [switch]$WhatIfOnly
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $WorkingRoot)) { throw "not found: $WorkingRoot" }

# Files to keep, per folder. Word only; the Excel workbooks and the native Sheet stay.
$keep = @{
  "00_Admin_and_Decisions" = @(
    "Requirements and Progress Tracking.xlsx",
    "Master Traceability Register (44 controls).docx",
    "Decision and Change Log.docx",
    "University Process Inquiry (DRAFT - NOT SENT).docx"
  )
  "01_Research_Questions" = @(
    "Research Questions and Answering Plan.docx",
    "Three-Study Contract.docx",
    "Research Question Decision Pack (2026-08-05).docx",
    "Artifact per Research Question (thinking notes only).docx"
  )
  "02_PhD_Proposal" = @(
    "Proposal v0.3 (current).docx",
    "Chapter 1 - Introduction (early draft).docx",
    "Chapter 3 - Gap and Research Questions.docx",
    "Chapter 6 - Work Plan.docx",
    "Executive Brief (EN + HE).docx"
  )
  "03_Literature_Review" = @(
    "Research Literature Workbook (139 verified sources).xlsx",
    "Researchers Related To This Research (95, tiered).xlsx",
    "Search Execution Register (QL-01 to QL-05, NOT RUN).docx",
    "VEGO-AI PhD Literature Workbook v0.1.gsheet"
  )
  "04_SE_Modeling_Studies" = @(
    "Evaluation Report.docx",
    "Expert Labeling Protocol (EXP-005).docx",
    "Baseline Characterization.docx"
  )
  "05_Medical_Feasibility_Gated" = @(
    "Medical Readiness Scorecard (0 of 6 gates).docx",
    "MediVARIA - Medical Extension Overview.docx",
    "MediVARIA_OnePage_v1 (original source document).docx",
    "VEGO-AI Foundation Paper - Record and Claim Verification.docx",
    "PhD Data Boundary (three zones).docx"
  )
  "06_Weekly_Meetings" = @(
    "2026-08-05 Meeting Record (machine transcript, unreviewed).docx",
    "2026-08-05 Step Tracking.docx"
  )
}

# Folders removed entirely: they held nothing but an auto-generated overview.
$dropFolders = @("07_Submission_Package", "99_Archive")

# Subfolders kept intact regardless of the keep-list.
$protectedSubfolders = @("2026-08-12 Supervisor Package", "compliance-reports")

$removed = New-Object System.Collections.Generic.List[string]
$kept = 0

foreach ($folder in (Get-ChildItem -LiteralPath $WorkingRoot -Directory)) {
  $name = $folder.Name

  if ($name -eq "_Ali private (do not share)") { $kept += (Get-ChildItem -LiteralPath $folder.FullName -File).Count; continue }

  if ($dropFolders -contains $name) {
    foreach ($f in Get-ChildItem -LiteralPath $folder.FullName -File -Recurse) { $removed.Add("$name\$($f.Name)") }
    if (-not $WhatIfOnly) { Remove-Item -LiteralPath $folder.FullName -Recurse -Force }
    continue
  }

  $allow = $keep[$name]
  if ($null -eq $allow) { $allow = @() }

  foreach ($f in Get-ChildItem -LiteralPath $folder.FullName -File) {
    if ($allow -contains $f.Name) { $kept++ }
    else {
      $removed.Add("$name\$($f.Name)")
      if (-not $WhatIfOnly) { Remove-Item -LiteralPath $f.FullName -Force }
    }
  }

  # keep protected subfolders whole; drop any other empty leftovers
  foreach ($sub in Get-ChildItem -LiteralPath $folder.FullName -Directory) {
    if ($protectedSubfolders -contains $sub.Name) {
      $kept += (Get-ChildItem -LiteralPath $sub.FullName -File -Recurse).Count
    }
  }
}

Write-Output ("removed : {0}" -f $removed.Count)
Write-Output ("kept    : {0}" -f $kept)
if ($WhatIfOnly) {
  Write-Output ""
  Write-Output "--- would remove ---"
  $removed | Sort-Object | ForEach-Object { Write-Output "  $_" }
}
