[CmdletBinding()]
<#
.SYNOPSIS
  Populate the canonical private PhD working Drive ("VEGO-AI PhD Working 2026")
  from the repository, folder by folder, per the intended content defined in
  docs/research/phd-proposal/drive-workspace-manifest.md.

  Closes the outstanding half of action A-04 ("create the separate shared PhD
  working area, UPLOAD CURRENT OUTPUTS, and confirm access"): the nine-folder
  skeleton was created on 2026-07-30 and the native literature Sheet was made,
  but no working outputs were ever uploaded.

  Boundary rules enforced here (from the manifest and phd-data-boundary.md):
    * no patient rows, MIMIC/Clalit extracts, or restricted clinical derivatives;
    * the supplied MIMIC source folder is LINKED, never copied;
    * 05_Medical_Feasibility_Gated carries non-sensitive governance material only;
    * 07_Submission_Package stays empty until Ali approves a submission candidate.

  Existing native Google files (.gsheet/.gdoc) are never touched: this script only
  adds/overwrites the specific repo-derived files it manages.

.EXAMPLE
  .\scripts\publish-working-drive.ps1 -WorkingRoot "G:\My Drive\VEGO-AI PhD Working 2026"
#>
param(
  [string]$WorkingRoot = "G:\My Drive\VEGO-AI PhD Working 2026",
  [switch]$WhatIfOnly
)

$ErrorActionPreference = "Stop"
$repo = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$out = Join-Path $repo "outputs\aug12-supervisor-delivery-2026-08-10"

if (-not (Test-Path -LiteralPath $WorkingRoot)) {
  throw "Working Drive root not found: $WorkingRoot. Is Google Drive for Desktop mounted?"
}

# folder -> list of (source, published name). Sources may be repo-relative or absolute.
$plan = [ordered]@{
  "00_Admin_and_Decisions" = @(
    @("$out\VEGO-AI-Requirements-and-Tracking-2026-08-12.xlsx", "Requirements and Progress Tracking.xlsx"),
    @("docs\research\phd-proposal\master-traceability-register.md", "Master traceability register (44 controls).md"),
    @("docs\research\phd-proposal\decision-change-log.md", "Decision and change log.md"),
    @("docs\research\phd-proposal\resource-raci-raid-register.md", "RACI and RAID register.md"),
    @("docs\research\phd-proposal\university-process-verification-checklist.md", "University process verification checklist.md"),
    @("docs\research\phd-proposal\university-process-inquiry-draft.md", "University process inquiry (DRAFT - not sent).md"),
    @("docs\research\phd-proposal\external-fact-register.md", "External fact register.md"),
    @("docs\research\phd-proposal\claim-register.md", "Claim register.md"),
    @("docs\research\phd-proposal\iris-closure-governance-control.md", "Closure governance control.md")
  )
  "01_Research_Questions" = @(
    @("docs\research\phd-proposal\three-study-contract.md", "Three-study contract.md"),
    @("docs\research\phd-proposal\2026-08-05-rq-decision-pack.md", "RQ decision pack (2026-08-05).md"),
    @("docs\research\phd-proposal\legacy-rq-crosswalk.md", "Legacy RQ crosswalk.md"),
    @("docs\research\phd-proposal\artifact-per-rq-brainstorm-2026-08-10.md", "Artifact per RQ - thinking notes only.md")
  )
  "02_PhD_Proposal" = @(
    @("$out\VEGO-AI-Chapter-3-Gap-and-Research-Questions-2026-08-12.docx", "Chapter 3 - Gap and Research Questions.docx"),
    @("$out\VEGO-AI-Chapter-3-Gap-and-Research-Questions-2026-08-12.pdf", "Chapter 3 - Gap and Research Questions.pdf"),
    @("$out\VEGO-AI-Executive-Brief-2026-08-12.docx", "Executive Brief (EN + HE).docx"),
    @("$out\VEGO-AI-Executive-Brief-2026-08-12.pdf", "Executive Brief (EN + HE).pdf"),
    @("docs\research\phd-proposal\proposal-v0.1.md", "Proposal v0.1.md"),
    @("docs\research\phd-proposal\proposal-v0.2-working-draft.md", "Proposal v0.2 working delta.md"),
    @("docs\research\phd-proposal\2026-07-29-doctoral-execution-plan.md", "Doctoral execution plan (2026-07-29).md")
  )
  "03_Literature_Review" = @(
    @("$out\VEGO-AI-Per-RQ-Literature-2026-08-12.xlsx", "Literature Review - Per Research Question.xlsx"),
    @("literature\per-rq-literature-map.md", "Per-RQ coverage gap map.md"),
    @("docs\research\phd-proposal\literature-review-protocol.md", "Literature review protocol.md"),
    @("docs\research\phd-proposal\literature-search-execution-register.md", "Search execution register (QL-01..05, NOT RUN).md"),
    @("docs\research\literature-review-taxonomy.md", "Literature review taxonomy.md")
  )
  "04_SE_Modeling_Studies" = @(
    @("docs\research\baseline-characterization.md", "Baseline characterization.md"),
    @("docs\research\evaluation-report.md", "Evaluation report.md"),
    @("docs\research\expert-labeling-protocol.md", "Expert labeling protocol (EXP-005).md"),
    @("docs\research\bigui\EXPERIMENT_BENCHMARK_ANALYTICS_REPORT.md", "Experiment benchmark analytics report.md"),
    @("docs\research\phd-proposal\iris-alignment-experiment-register.md", "IRIS-EXP alignment experiment register.md"),
    @("docs\research\phd-proposal\scientific-experiment-crosswalk.md", "Scientific experiment crosswalk.md")
  )
  "05_Medical_Feasibility_Gated" = @(
    @("docs\research\governance\medical-readiness-scorecard.md", "Medical readiness scorecard (0 of 6 gates).md"),
    @("docs\research\governance\medivaria-medical-extension-overview.md", "MediVARIA - medical extension overview.md"),
    @("docs\research\governance\mimic-metadata-audit-2026-07-30.md", "MIMIC metadata-only audit (2026-07-30).md"),
    @("docs\research\governance\clalit-research-request-template.md", "Clalit research request template.md"),
    @("docs\research\governance\phd-data-boundary.md", "PhD data boundary (three zones).md"),
    @("docs\research\governance\medical-derived-artifact-provenance-template.md", "Medical derived-artifact provenance template.md")
  )
  "06_Weekly_Meetings" = @(
    @("docs\research\meetings\2026-08-05-supervisor-meeting.md", "2026-08-05 meeting record (machine transcript, unreviewed).md"),
    @("docs\research\meetings\2026-08-05-execution-plan.md", "2026-08-05 execution plan.md"),
    @("docs\research\meetings\2026-08-05-tracking.md", "2026-08-05 step tracking.md"),
    @("docs\research\meetings\2026-07-29-iris-supervisor-call-report.md", "2026-07-29 call report.md"),
    @("docs\research\meetings\2026-07-29-iris-requirements-register.md", "2026-07-29 requirements register.md"),
    @("docs\research\meetings\2026-07-29-iris-supervisor-action-register.md", "2026-07-29 action register.md"),
    @("docs\templates\weekly-supervisor-pre-read.md", "TEMPLATE - weekly supervisor pre-read.md")
  )
}

# The Aug-12 supervisor package is published as a subfolder of 06_Weekly_Meetings.
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

# Per-folder README text. These state honestly what is and is not in each folder.
$readmes = @{
  "00_Admin_and_Decisions" = @"
# 00 - Admin and Decisions

Decision/change log, the 44-control master register, RACI/RAID, claim register, and
the university-process verification material.

Current state: the ten supervisor decisions requested for 12 August (D-RQ-01..10)
are all still Pending - see the Decisions Requested sheet in Requirements and
Progress Tracking. The university-process inquiry is drafted but NOT SENT; it needs
a recipient, Ali's program details, and Ali's send-approval.
"@
  "01_Research_Questions" = @"
# 01 - Research Questions

The umbrella research question, SQ1-SQ3, their mapping to three studies, and the
crosswalk from the retired multi-question set.

Current state: the wording here reflects the live edits from the 5 August working
call. It is Ali's reconstruction and remains PROVISIONAL pending D-RQ-01 (umbrella)
and D-RQ-02 (SQ1-SQ3) sign-off. Do not treat it as approved.
"@
  "02_PhD_Proposal" = @"
# 02 - PhD Proposal

Proposal versions plus the written Chapter 3 (Gap and Research Questions) and the
bilingual executive brief.

Current state: Chapter 3 is drafted in full and incorporates every correction from
the 5 August call. Proposal v0.2 is a controlled delta over v0.1, not yet integrated
into a single supervisor-facing document; its own release checklist is unmet. No
section claims an accuracy, generalization, or clinical result.
"@
  "03_Literature_Review" = @"
# 03 - Literature Review

The native Google Sheet workbook (workbook of record), the per-question coverage-gap
analysis, the review protocol, and the frozen search register.

Current state: searches QL-01 through QL-05 are "Protocol ready / NOT RUN" - they are
deliberately unexecuted per the 5 August instruction to think about the survey without
executing it. Coverage today is honestly uneven: RQ1 thin, RQ2 tool-heavy and
research-light, RQ3 currently empty. No novelty or completeness claim is supported.
"@
  "04_SE_Modeling_Studies" = @"
# 04 - SE and Modeling Studies

Software/modeling study material and aggregate evidence: baseline characterization,
evaluation report, the EXP-005 expert-labeling protocol, benchmark analytics, and the
experiment registers.

Current state: evidence here is mechanism and architecture readiness only. EXP-005
stands at 0 supplied expert labels out of 24 generalization-safe candidate rows,
against a required minimum of 20 - so no accuracy, generalization, or effort-reduction
figure is computable yet. Synthetic and same-pattern outputs are screening material,
never accuracy evidence.
"@
  "05_Medical_Feasibility_Gated" = @"
# 05 - Medical Feasibility (GATED)

Non-sensitive feasibility governance only: the readiness scorecard, the MediVARIA
medical-extension overview, the metadata-only MIMIC audit, the Clalit request
template, the data-boundary rules, and the derived-artifact provenance template.

HARD BOUNDARY - this folder must never contain patient rows, MIMIC or Clalit extracts,
clinical derivatives, or credentials. The supplied MIMIC source folder is linked from
the workspace manifest, never copied here.

Current state: medical readiness is 0 of 6 mandatory entry gates (use-case, people,
authorization, ethics/privacy, environment, protocol) - all open. No row-level work,
pilot, export, or medical claim is authorized. A 26 August control date decides whether
the non-medical Plan B becomes the committed route.
"@
  "06_Weekly_Meetings" = @"
# 06 - Weekly Meetings

Meeting records, execution plans, step tracking, and the weekly pre-read template.
The "2026-08-12 Supervisor Package" subfolder holds the numbered, supervisor-facing
set for that meeting.

Current state: the Wednesday 09:00 series is confirmed, but no full weekly cycle has
yet produced pre-read to decision to propagated-delta minutes. The 2026-08-05 record
is a machine transcript with inferred (undiarized) speakers - not human-reviewed, and
not quotable as verbatim.
"@
}

$submissionReadme = @"
# 07 - Submission Package

INTENTIONALLY EMPTY.

Per the workspace manifest, this folder holds Ali-approved submission candidates only.
Nothing has been approved for submission, and no official submission deadline has been
confirmed by Graduate Studies - the September/October dates in the plan are internal
working targets, not verified university deadlines.

This folder stays empty until (a) a candidate is complete, (b) Ali explicitly approves
that exact package, and (c) the authorized submission route and receipt requirements
are confirmed in writing.
"@

$archiveReadme = @"
# 99 - Archive

Superseded reviewed working material.

Currently empty by design: nothing has yet been superseded AND reviewed. Earlier
supervisor packages (1, 15, 21 July) remain live historical records in the repository
rather than archived material, and the retired multi-question RQ set is preserved
inside the legacy crosswalk in 01_Research_Questions rather than moved here.
"@

function Resolve-Src([string]$p) {
  if ([System.IO.Path]::IsPathRooted($p)) { return $p }
  return (Join-Path $repo $p)
}

function Copy-Set($destDir, $items) {
  New-Item -ItemType Directory -Force -Path $destDir | Out-Null
  $n = 0; $miss = 0
  foreach ($item in $items) {
    $src = Resolve-Src $item[0]
    if (Test-Path -LiteralPath $src) {
      if (-not $WhatIfOnly) { Copy-Item -LiteralPath $src -Destination (Join-Path $destDir $item[1]) -Force }
      $n++
    } else { Write-Warning "missing: $($item[0])"; $miss++ }
  }
  return @($n, $miss)
}

$total = 0
foreach ($folder in $plan.Keys) {
  $dest = Join-Path $WorkingRoot $folder
  $res = Copy-Set $dest $plan[$folder]
  if ($readmes.ContainsKey($folder) -and -not $WhatIfOnly) {
    Set-Content -LiteralPath (Join-Path $dest "_README.md") -Value $readmes[$folder] -Encoding UTF8
  }
  Write-Output ("{0,-32} {1,2} file(s){2}" -f $folder, $res[0], $(if ($res[1]) { " ($($res[1]) missing)" } else { "" }))
  $total += $res[0]
}

# Aug-12 package as a subfolder of 06
$pkgDir = Join-Path $WorkingRoot "06_Weekly_Meetings\2026-08-12 Supervisor Package"
$res = Copy-Set $pkgDir $aug12
Write-Output ("{0,-32} {1,2} file(s)" -f "  06/2026-08-12 Package", $res[0])
$total += $res[0]

if (-not $WhatIfOnly) {
  Set-Content -LiteralPath (Join-Path $WorkingRoot "07_Submission_Package\_README.md") -Value $submissionReadme -Encoding UTF8
  Set-Content -LiteralPath (Join-Path $WorkingRoot "99_Archive\_README.md") -Value $archiveReadme -Encoding UTF8
}

Write-Output ""
Write-Output "total repo-derived files published: $total"
Write-Output "07_Submission_Package and 99_Archive intentionally hold only a _README.md."
Write-Output "Native Google files (e.g. the literature .gsheet) were not touched."
