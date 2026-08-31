[CmdletBinding()]
param(
    [string]$MarkdownOutputPath = "docs\dashboards\progress-visualizations.generated.md",
    [string]$HtmlOutputPath = "docs\dashboards\progress-visualizations.generated.html"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$markdownFullPath = Join-Path $repoRoot $MarkdownOutputPath
$htmlFullPath = Join-Path $repoRoot $HtmlOutputPath
$generated = Get-Date -Format "yyyy-MM-dd HH:mm zzz"
$fence = '```'

function Read-TextOrEmpty {
    param([Parameter(Mandatory = $true)][string]$RelativePath)

    $path = Join-Path $repoRoot $RelativePath
    if (Test-Path -LiteralPath $path) {
        return (Get-Content -Raw -LiteralPath $path)
    }
    return ""
}

function Get-MarkdownSection {
    param(
        [Parameter(Mandatory = $true)][string]$Markdown,
        [Parameter(Mandatory = $true)][string]$Heading
    )

    $pattern = "(?ms)^##\s+$([regex]::Escape($Heading))\s*(.+?)(?=^##\s+|\z)"
    $match = [regex]::Match($Markdown, $pattern)
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return ""
}

function Split-MarkdownTableLine {
    param([Parameter(Mandatory = $true)][string]$Line)

    $trimmed = $Line.Trim()
    if ($trimmed.StartsWith("|")) {
        $trimmed = $trimmed.Substring(1)
    }
    if ($trimmed.EndsWith("|")) {
        $trimmed = $trimmed.Substring(0, $trimmed.Length - 1)
    }
    return @($trimmed -split "\|" | ForEach-Object { $_.Trim() })
}

function Get-MarkdownTableRows {
    param(
        [Parameter(Mandatory = $true)][string]$Markdown,
        [Parameter(Mandatory = $true)][string]$HeaderName
    )

    $rows = @()
    $headers = $null
    $capturing = $false

    foreach ($line in ($Markdown -split "`r?`n")) {
        if ($line -notmatch '^\s*\|') {
            if ($capturing -and $rows.Count -gt 0) {
                break
            }
            continue
        }

        if (-not $headers) {
            if ($line -match [regex]::Escape($HeaderName)) {
                $headers = Split-MarkdownTableLine -Line $line
                $capturing = $true
            }
            continue
        }

        if ($line -match '^\s*\|\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$') {
            continue
        }

        $columns = Split-MarkdownTableLine -Line $line
        if ($columns.Count -lt $headers.Count) {
            continue
        }

        $object = [ordered]@{}
        for ($i = 0; $i -lt $headers.Count; $i++) {
            $object[$headers[$i]] = $columns[$i]
        }
        $rows += [pscustomobject]$object
    }

    return @($rows)
}

function Get-Cell {
    param(
        [Parameter(Mandatory = $true)]$Row,
        [Parameter(Mandatory = $true)][string]$ColumnName
    )

    $property = $Row.PSObject.Properties[$ColumnName]
    if ($property) {
        return [string]$property.Value
    }
    return ""
}

function ConvertTo-StatusBucket {
    param([string]$Status)

    $statusText = ""
    if ($null -ne $Status) {
        $statusText = $Status.Trim()
    }
    if ($statusText -match '^(Green|Done|Passed|Available|Active rule)\b') { return "Done/Green" }
    if ($statusText -match '^(Yellow|Open|In progress|In review|Next)\b') { return "In progress/Yellow" }
    if ($statusText -match '^(Red|At risk)\b') { return "Risk/Red" }
    if ($statusText -match '^(Blocked|Deferred)\b') { return "Blocked" }
    if ($statusText -match '^(Planned)\b') { return "Planned" }
    return "Other"
}

function New-StatusCounts {
    return [ordered]@{
        "Done/Green" = 0
        "In progress/Yellow" = 0
        "Risk/Red" = 0
        "Blocked" = 0
        "Planned" = 0
        "Other" = 0
    }
}

function Get-StatusCounts {
    param(
        [Parameter(Mandatory = $true)]$Rows,
        [Parameter(Mandatory = $true)][string]$StatusColumn
    )

    $counts = New-StatusCounts
    foreach ($row in $Rows) {
        $bucket = ConvertTo-StatusBucket -Status (Get-Cell -Row $row -ColumnName $StatusColumn)
        $counts[$bucket] += 1
    }
    return $counts
}

function Get-CountTotal {
    param([Parameter(Mandatory = $true)]$Counts)

    $total = 0
    foreach ($key in $Counts.Keys) {
        $total += [int]$Counts[$key]
    }
    return $total
}

function Get-Percent {
    param(
        [int]$Part,
        [int]$Total
    )

    if ($Total -le 0) {
        return 0
    }
    return [int][Math]::Round(($Part / $Total) * 100)
}

function New-AsciiBar {
    param(
        [int]$Percent,
        [int]$Width = 20
    )

    $bounded = [Math]::Max(0, [Math]::Min(100, $Percent))
    $filled = [int][Math]::Round(($bounded / 100) * $Width)
    $empty = $Width - $filled
    return "[" + ("#" * $filled) + ("-" * $empty) + "] $bounded%"
}

function New-MermaidPie {
    param(
        [Parameter(Mandatory = $true)][string]$Title,
        [Parameter(Mandatory = $true)]$Counts
    )

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add($fence + "mermaid")
    $lines.Add("pie showData")
    $lines.Add("    title $Title")
    $hasData = $false
    foreach ($key in $Counts.Keys) {
        if ([int]$Counts[$key] -gt 0) {
            $lines.Add("    ""$key"" : $($Counts[$key])")
            $hasData = $true
        }
    }
    if (-not $hasData) {
        $lines.Add('    "No rows" : 1')
    }
    $lines.Add($fence)
    return $lines.ToArray()
}

function Format-MermaidLabel {
    param([string]$Text)

    $label = ""
    if ($null -ne $Text) {
        $label = $Text
    }
    return ($label.Replace('"', "'").Replace('|', '/').Trim())
}

function New-MilestoneFlow {
    param($Rows)

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add($fence + "mermaid")
    $lines.Add("flowchart LR")
    $lines.Add("    classDef done fill:#e6f4ea,stroke:#2f855a,color:#1f2933;")
    $lines.Add("    classDef wait fill:#fff8e1,stroke:#b7791f,color:#1f2933;")
    $lines.Add("    classDef blocked fill:#fde8e8,stroke:#c53030,color:#1f2933;")
    $lines.Add("    classDef planned fill:#eef2ff,stroke:#5a67d8,color:#1f2933;")

    $index = 0
    $nodeIds = @()
    foreach ($row in $Rows) {
        $nodeId = "m$index"
        $nodeIds += $nodeId
        $milestone = Format-MermaidLabel (Get-Cell -Row $row -ColumnName "Milestone")
        $state = Format-MermaidLabel (Get-Cell -Row $row -ColumnName "State")
        $bucket = ConvertTo-StatusBucket -Status $state
        $className = if ($bucket -eq "Done/Green") { "done" } elseif ($bucket -eq "Blocked") { "blocked" } elseif ($bucket -eq "Planned") { "planned" } else { "wait" }
        $lines.Add("    $nodeId[""$milestone`n$state""]:::$className")
        $index += 1
    }

    for ($i = 0; $i -lt ($nodeIds.Count - 1); $i++) {
        $lines.Add("    $($nodeIds[$i]) --> $($nodeIds[$i + 1])")
    }

    if ($nodeIds.Count -eq 0) {
        $lines.Add('    none["No milestone rows found"]:::wait')
    }

    $lines.Add($fence)
    return $lines.ToArray()
}

function Get-OpenRows {
    param($Rows)

    return @($Rows | Where-Object {
        $bucket = ConvertTo-StatusBucket -Status (Get-Cell -Row $_ -ColumnName "Status")
        $bucket -ne "Done/Green"
    })
}

function ConvertTo-HtmlText {
    param([string]$Text)

    $value = ""
    if ($null -ne $Text) {
        $value = $Text
    }
    return [System.Net.WebUtility]::HtmlEncode($value)
}

function Get-BucketColorRole {
    param([string]$Bucket)

    switch ($Bucket) {
        "Done/Green" { return "good" }
        "In progress/Yellow" { return "warning" }
        "Risk/Red" { return "critical" }
        "Blocked" { return "blocked" }
        "Planned" { return "planned" }
        default { return "other" }
    }
}

function New-StackedBar {
    param(
        [Parameter(Mandatory = $true)][string]$Title,
        [Parameter(Mandatory = $true)]$Counts,
        [Parameter(Mandatory = $true)][int]$Total
    )

    $segments = New-Object System.Collections.Generic.List[string]
    $legendItems = New-Object System.Collections.Generic.List[string]

    foreach ($bucket in $Counts.Keys) {
        $count = [int]$Counts[$bucket]
        if ($count -le 0) { continue }
        $percent = Get-Percent -Part $count -Total $Total
        $role = Get-BucketColorRole -Bucket $bucket
        $safeLabel = ConvertTo-HtmlText $bucket
        $titleAttr = ConvertTo-HtmlText "$bucket`: $count of $Total ($percent%)"
        $inline = if ($percent -ge 12) { "<span class=""seg-label"">$percent%</span>" } else { "" }
        $segments.Add("<div class=""seg seg-$role"" style=""flex-basis:$percent%"" title=""$titleAttr"">$inline</div>")
        $legendItems.Add("<li><span class=""swatch swatch-$role""></span>$safeLabel <strong>$count</strong><span class=""muted"">($percent%)</span></li>")
    }

    if ($segments.Count -eq 0) {
        $segments.Add("<div class=""seg seg-other"" style=""flex-basis:100%"" title=""No rows found"">No rows found</div>")
    }

    $safeTitle = ConvertTo-HtmlText $Title
    $segmentsHtml = $segments -join ""
    $legendHtml = if ($legendItems.Count -gt 0) { "<ul class=""legend-list"">" + ($legendItems -join "") + "</ul>" } else { "" }

    return @"
<div class="viz-block">
  <h3>$safeTitle</h3>
  <div class="stacked-bar" role="img" aria-label="$safeTitle status mix">$segmentsHtml</div>
  $legendHtml
</div>
"@
}

$progressMarkdown = Read-TextOrEmpty "docs/agent-memory/progress.md"
$progressDashboardMarkdown = Read-TextOrEmpty "docs/dashboards/progress-dashboard.md"
$kpiMarkdown = Read-TextOrEmpty "docs/dashboards/kpi-register.md"

$milestoneRows = Get-MarkdownTableRows -Markdown (Get-MarkdownSection -Markdown $progressMarkdown -Heading "Milestones") -HeaderName "Date"
$activeRows = Get-MarkdownTableRows -Markdown (Get-MarkdownSection -Markdown $progressMarkdown -Heading "Active Work") -HeaderName "ID"
$kpiRows = Get-MarkdownTableRows -Markdown (Get-MarkdownSection -Markdown $kpiMarkdown -Heading "KPI Snapshot") -HeaderName "KPI"
$executiveRows = Get-MarkdownTableRows -Markdown (Get-MarkdownSection -Markdown $progressDashboardMarkdown -Heading "Executive Snapshot") -HeaderName "Area"
$flowRows = Get-MarkdownTableRows -Markdown (Get-MarkdownSection -Markdown $progressDashboardMarkdown -Heading "Milestone Flow") -HeaderName "Milestone"

$milestoneCounts = Get-StatusCounts -Rows $milestoneRows -StatusColumn "Status"
$activeCounts = Get-StatusCounts -Rows $activeRows -StatusColumn "Status"
$kpiCounts = Get-StatusCounts -Rows $kpiRows -StatusColumn "Status"
$executiveCounts = Get-StatusCounts -Rows $executiveRows -StatusColumn "Status"

$milestoneTotal = Get-CountTotal -Counts $milestoneCounts
$activeTotal = Get-CountTotal -Counts $activeCounts
$kpiTotal = Get-CountTotal -Counts $kpiCounts
$executiveTotal = Get-CountTotal -Counts $executiveCounts

$milestoneDonePercent = Get-Percent -Part $milestoneCounts["Done/Green"] -Total $milestoneTotal
$kpiGreenPercent = Get-Percent -Part $kpiCounts["Done/Green"] -Total $kpiTotal
$activeClosedPercent = Get-Percent -Part $activeCounts["Done/Green"] -Total $activeTotal
$executiveGreenPercent = Get-Percent -Part $executiveCounts["Done/Green"] -Total $executiveTotal

$attentionRows = Get-OpenRows -Rows $activeRows | Select-Object -First 10
$exp005Row = $kpiRows | Where-Object { (Get-Cell -Row $_ -ColumnName "KPI") -match '^EXP-005 evidence gate$' } | Select-Object -First 1
$exp005Value = if ($exp005Row) { Get-Cell -Row $exp005Row -ColumnName "Current Value" } else { "EXP-005 evidence gate row not found." }

$markdownLines = New-Object System.Collections.Generic.List[string]
$markdownLines.Add("# Progress Visualizations")
$markdownLines.Add("")
$markdownLines.Add("Generated: $generated.")
$markdownLines.Add("")
$markdownLines.Add('This generated dashboard summarizes docs/agent-memory/progress.md, docs/dashboards/progress-dashboard.md, and docs/dashboards/kpi-register.md. Regenerate it with .\scripts\build-progress-visualizations.ps1.')
$markdownLines.Add("")
$markdownLines.Add("## Summary Cards")
$markdownLines.Add("")
$markdownLines.Add("| Signal | Value | Visual |")
$markdownLines.Add("| --- | --- | --- |")
$markdownLines.Add("| Milestone completion | $($milestoneCounts["Done/Green"]) of $milestoneTotal done/green | $(New-AsciiBar -Percent $milestoneDonePercent) |")
$markdownLines.Add("| KPI green rate | $($kpiCounts["Done/Green"]) of $kpiTotal green | $(New-AsciiBar -Percent $kpiGreenPercent) |")
$markdownLines.Add("| Active work closed | $($activeCounts["Done/Green"]) of $activeTotal done | $(New-AsciiBar -Percent $activeClosedPercent) |")
$markdownLines.Add("| Executive snapshot green | $($executiveCounts["Done/Green"]) of $executiveTotal green | $(New-AsciiBar -Percent $executiveGreenPercent) |")
$markdownLines.Add("")
$markdownLines.Add("## KPI Status Mix")
$markdownLines.Add("")
foreach ($line in (New-MermaidPie -Title "KPI status mix" -Counts $kpiCounts)) {
    $markdownLines.Add($line)
}
$markdownLines.Add("")
$markdownLines.Add("## Active Work Status Mix")
$markdownLines.Add("")
foreach ($line in (New-MermaidPie -Title "Active work status mix" -Counts $activeCounts)) {
    $markdownLines.Add($line)
}
$markdownLines.Add("")
$markdownLines.Add("## Milestone Status Mix")
$markdownLines.Add("")
foreach ($line in (New-MermaidPie -Title "Milestone status mix" -Counts $milestoneCounts)) {
    $markdownLines.Add($line)
}
$markdownLines.Add("")
$markdownLines.Add("## Executive Snapshot Mix")
$markdownLines.Add("")
foreach ($line in (New-MermaidPie -Title "Executive snapshot mix" -Counts $executiveCounts)) {
    $markdownLines.Add($line)
}
$markdownLines.Add("")
$markdownLines.Add("## Milestone Timeline")
$markdownLines.Add("")
foreach ($line in (New-MilestoneFlow -Rows $flowRows)) {
    $markdownLines.Add($line)
}
$markdownLines.Add("")
$markdownLines.Add("## Evidence Gate Flow")
$markdownLines.Add("")
$markdownLines.Add($fence + "mermaid")
$markdownLines.Add("flowchart TD")
$markdownLines.Add("    classDef done fill:#e6f4ea,stroke:#2f855a,color:#1f2933;")
$markdownLines.Add("    classDef wait fill:#fff8e1,stroke:#b7791f,color:#1f2933;")
$markdownLines.Add("    classDef blocked fill:#fde8e8,stroke:#c53030,color:#1f2933;")
$markdownLines.Add("    m4b[""M4B-1 baseline`nimplemented / parallel-only""]:::done")
$markdownLines.Add("    exp005[""EXP-005 real labels`n0 valid labels in current gate""]:::blocked")
$markdownLines.Add("    eval[""EXP-003 / EXP-005 rerun`nrequires real labels""]:::blocked")
$markdownLines.Add("    policy[""Policy refinement / M4B-2`nblocked until evidence and approval""]:::blocked")
$markdownLines.Add("    thesis[""Thesis evidence`nmechanism readiness now; accuracy later""]:::wait")
$markdownLines.Add("    m4b --> exp005 --> eval --> policy")
$markdownLines.Add("    exp005 --> thesis")
$markdownLines.Add($fence)
$markdownLines.Add("")
$markdownLines.Add("## EXP-005 Gate")
$markdownLines.Add("")
$markdownLines.Add("> $exp005Value")
$markdownLines.Add("")
$markdownLines.Add("## Open Active Work")
$markdownLines.Add("")
if ($attentionRows.Count -eq 0) {
    $markdownLines.Add("_No open active work rows found._")
}
else {
    $markdownLines.Add("| ID | Status | Summary | Next Step |")
    $markdownLines.Add("| --- | --- | --- | --- |")
    foreach ($row in $attentionRows) {
        $markdownLines.Add("| $(Get-Cell -Row $row -ColumnName "ID") | $(Get-Cell -Row $row -ColumnName "Status") | $(Get-Cell -Row $row -ColumnName "Summary") | $(Get-Cell -Row $row -ColumnName "Next Step") |")
    }
}
$markdownLines.Add("")
$markdownLines.Add("## Generated HTML")
$markdownLines.Add("")
$markdownLines.Add('Open docs/dashboards/progress-visualizations.generated.html locally for the card-and-bar version.')

New-Item -ItemType Directory -Path (Split-Path -Parent $markdownFullPath) -Force | Out-Null
Set-Content -LiteralPath $markdownFullPath -Value ($markdownLines -join "`r`n") -Encoding UTF8

$kpiStackedBar = New-StackedBar -Title "KPI Status Mix" -Counts $kpiCounts -Total $kpiTotal
$activeStackedBar = New-StackedBar -Title "Active Work Status Mix" -Counts $activeCounts -Total $activeTotal
$milestoneStackedBar = New-StackedBar -Title "Milestone Status Mix" -Counts $milestoneCounts -Total $milestoneTotal
$executiveStackedBar = New-StackedBar -Title "Executive Snapshot Mix" -Counts $executiveCounts -Total $executiveTotal

$activeItemsHtml = if ($attentionRows.Count -eq 0) {
    "<li>No open active work rows found.</li>"
}
else {
    ($attentionRows | ForEach-Object {
        $id = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "ID")
        $status = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Status")
        $summary = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Summary")
        $next = ConvertTo-HtmlText (Get-Cell -Row $_ -ColumnName "Next Step")
        "<li><strong>$id</strong><span class=""pill"">$status</span><p>$summary</p><small>$next</small></li>"
    }) -join "`n"
}

$safeExp005 = ConvertTo-HtmlText $exp005Value
$html = @"
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VEGO-AI Progress Visualizations</title>
  <style>
    :root, .viz-root {
      color-scheme: light;
      --surface-1: #fcfcfb;
      --page-plane: #f9f9f7;
      --text-primary: #0b0b0b;
      --text-secondary: #52514e;
      --text-muted: #898781;
      --gridline: #e1e0d9;
      --baseline: #c3c2b7;
      --border: rgba(11,11,11,0.10);
      --status-good: #0ca30c;
      --status-warning: #fab219;
      --status-blocked: #4a3aa7;
      --status-critical: #d03b3b;
      --status-planned: #2a78d6;
      --on-dark-fill: #ffffff;
      --on-light-fill: #17202a;
    }
    @media (prefers-color-scheme: dark) {
      :root:where(:not([data-theme="light"])), .viz-root {
        color-scheme: dark;
        --surface-1: #1a1a19;
        --page-plane: #0d0d0d;
        --text-primary: #ffffff;
        --text-secondary: #c3c2b7;
        --text-muted: #898781;
        --gridline: #2c2c2a;
        --baseline: #383835;
        --border: rgba(255,255,255,0.10);
        --status-good: #0ca30c;
        --status-warning: #fab219;
        --status-blocked: #9085e9;
        --status-critical: #d03b3b;
        --status-planned: #3987e5;
      }
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
      color: var(--text-primary);
      background: var(--page-plane);
    }
    header, main {
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
    }
    header { padding: 28px 0 16px; }
    h1 { margin: 0 0 8px; font-size: 32px; line-height: 1.15; font-weight: 700; }
    h2 { margin: 0 0 14px; font-size: 18px; line-height: 1.25; }
    h3 { margin: 0 0 10px; font-size: 14px; font-weight: 600; color: var(--text-secondary); }
    p, small { color: var(--text-secondary); }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
      margin: 14px 0;
    }
    .card, .panel {
      background: var(--surface-1);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }
    .card strong {
      display: block;
      font-size: 28px;
      line-height: 1;
      margin-bottom: 8px;
      font-variant-numeric: proportional-nums;
    }
    .panel { margin: 14px 0; }
    .viz-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      align-items: start;
      gap: 16px;
    }
    .stacked-bar {
      display: flex;
      gap: 2px;
      height: 20px;
      border-radius: 4px;
      overflow: hidden;
      background: var(--gridline);
      margin-bottom: 10px;
    }
    .seg {
      flex-shrink: 0;
      flex-grow: 1;
      flex-basis: 0%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
    }
    .seg-good { background: var(--status-good); color: var(--on-dark-fill); }
    .seg-warning { background: var(--status-warning); color: var(--on-light-fill); }
    .seg-blocked { background: var(--status-blocked); color: var(--on-dark-fill); }
    .seg-critical { background: var(--status-critical); color: var(--on-dark-fill); }
    .seg-planned { background: var(--status-planned); color: var(--on-dark-fill); }
    .seg-other { background: var(--text-muted); color: var(--on-light-fill); }
    .seg-label { padding: 0 4px; }
    .legend-list {
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 6px 16px;
      margin: 0;
      padding: 0;
      font-size: 13px;
      color: var(--text-secondary);
    }
    .legend-list li { display: flex; align-items: center; gap: 6px; }
    .legend-list strong { color: var(--text-primary); font-weight: 600; }
    .legend-list .muted { color: var(--text-muted); font-size: 12px; }
    .swatch {
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 3px;
      flex-shrink: 0;
    }
    .swatch-good { background: var(--status-good); }
    .swatch-warning { background: var(--status-warning); }
    .swatch-blocked { background: var(--status-blocked); }
    .swatch-critical { background: var(--status-critical); }
    .swatch-planned { background: var(--status-planned); }
    .swatch-other { background: var(--text-muted); }
    .gate { border-left: 5px solid var(--status-critical); }
    ol { padding-left: 22px; }
    li { margin: 12px 0; }
    .pill {
      display: inline-block;
      margin-left: 8px;
      padding: 2px 8px;
      border: 1px solid var(--border);
      border-radius: 999px;
      color: var(--text-secondary);
      font-size: 12px;
    }
    code {
      background: var(--gridline);
      padding: 2px 5px;
      border-radius: 4px;
    }
    @media (max-width: 620px) {
      header, main { width: min(100% - 20px, 1180px); }
      h1 { font-size: 26px; }
    }
  </style>
</head>
<body>
  <header>
    <h1>VEGO-AI Progress Visualizations</h1>
    <p>Generated $generated from tracked progress, dashboard, and KPI Markdown.</p>
  </header>
  <main>
    <section class="grid" aria-label="Summary cards">
      <div class="card"><strong>$milestoneDonePercent%</strong><span>Milestones done or green</span></div>
      <div class="card"><strong>$kpiGreenPercent%</strong><span>KPIs green</span></div>
      <div class="card"><strong>$activeClosedPercent%</strong><span>Active work closed</span></div>
      <div class="card"><strong>$executiveGreenPercent%</strong><span>Executive snapshot green</span></div>
    </section>

    <section class="panel">
      <h2>Status Mix</h2>
      <div class="viz-grid">
        $kpiStackedBar
        $activeStackedBar
        $milestoneStackedBar
        $executiveStackedBar
      </div>
    </section>

    <section class="panel gate">
      <h2>Current Evidence Gate</h2>
      <p>$safeExp005</p>
    </section>

    <section class="panel">
      <h2>Open Active Work</h2>
      <ol>
        $activeItemsHtml
      </ol>
    </section>

    <section class="panel">
      <h2>Refresh Command</h2>
      <p><code>.\scripts\build-progress-visualizations.ps1</code></p>
    </section>
  </main>
</body>
</html>
"@

New-Item -ItemType Directory -Path (Split-Path -Parent $htmlFullPath) -Force | Out-Null
Set-Content -LiteralPath $htmlFullPath -Value $html -Encoding UTF8

Write-Host "Progress visualizations generated:"
Write-Host "- $markdownFullPath"
Write-Host "- $htmlFullPath"
