# Run every Study 1C offline instrument over the available runs and render the figures.
# Each run keeps its own denominator; nothing here pools them.
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

$root = Split-Path -Parent $PSScriptRoot
$accepted = Join-Path $root "external_data\airtravel-pr38\v4-real-run\output"
$frame = Join-Path $root "external_data\airtravel-pr38\full-frame-run\output"
$out = Join-Path $root "external_data\airtravel-pr38\analysis-baselines"
New-Item -ItemType Directory -Force -Path $out | Out-Null

$runs = @(@{ Label = "ACCEPTED_RUN_N4"; Dir = $accepted })
if (Test-Path (Join-Path $frame "qa_events.jsonl")) {
    $runs += @{ Label = "FULL_FRAME_N21"; Dir = $frame }
} else {
    Write-Output "!! full-frame event log absent; reporting the accepted run only"
}

$eventArgs = @()
$dirArgs = @()
$analysisArgs = @()
foreach ($r in $runs) {
    $events = Join-Path $r.Dir "qa_events.jsonl"
    $receipt = Join-Path $r.Dir "run-receipt.json"
    $eventArgs += @("--run", "$($r.Label)=$events")
    $dirArgs += @("--run", "$($r.Label)=$($r.Dir)")
    $analysisArgs += @("--run", "$($r.Label)=$events,$receipt")
}

Write-Output "== consolidated descriptive analysis"
& py -3.13 (Join-Path $PSScriptRoot "study1_full_frame_analysis.py") @analysisArgs `
    --runtime-root (Join-Path $root "external_data\airtravel-pr38\fullframe_runtime") `
    --out (Join-Path $out "full-frame-analysis.json") | Out-Null

Write-Output "== detector baselines"
& py -3.13 (Join-Path $PSScriptRoot "study1_detector_baselines.py") @eventArgs `
    --out (Join-Path $out "detector-baselines.json") | Out-Null

Write-Output "== operating characteristic"
& py -3.13 (Join-Path $PSScriptRoot "study1_detector_operating_characteristic.py") @eventArgs `
    --out (Join-Path $out "operating-characteristic.json") | Out-Null

Write-Output "== round-bound load sensitivity"
& py -3.13 (Join-Path $PSScriptRoot "study1_round_bound_sensitivity.py") @eventArgs `
    --out (Join-Path $out "round-bound-sensitivity.json") | Out-Null

Write-Output "== escalation mechanism comparison"
& py -3.13 (Join-Path $PSScriptRoot "study1_escalation_mechanism_comparison.py") @dirArgs `
    --out (Join-Path $out "escalation-mechanisms.json") | Out-Null

$index = if ($runs.Count -gt 1) { 1 } else { 0 }
Write-Output "== figures (run index $index)"
& py -3.13 (Join-Path $PSScriptRoot "render_study1c_figures.py") `
    --characteristic (Join-Path $out "operating-characteristic.json") `
    --baselines (Join-Path $out "detector-baselines.json") `
    --mechanisms (Join-Path $out "escalation-mechanisms.json") `
    --run-index $index `
    --out-dir (Join-Path $out "figures") | Out-Null

Write-Output "== done: $out"
