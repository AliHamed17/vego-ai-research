# Publish a folder to Google Drive for Desktop and VERIFY the bytes landed.
#
# Why this exists: a plain Copy-Item into G:\ can be silently reverted by Google
# Drive's conflict resolution when the cloud already holds a copy of the same
# name - the cloud version wins and the newer local file is lost. On 2026-08-12
# that reverted 10 of 16 files in the Aug-12 supervisor package, including
# Chapter 3 and the literature workbook.
#
# Strategy: remove the destination file first, let Drive register the delete,
# copy, then re-verify size + hash after a settle delay. Report any file that
# did not stick.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Source,
    [Parameter(Mandatory)][string]$Destination,
    [int]$SettleSeconds = 6,
    [int]$MaxAttempts = 3
)

$ErrorActionPreference = "Stop"
$src = (Resolve-Path -LiteralPath $Source).Path
if (-not (Test-Path -LiteralPath $Destination)) { throw "Destination not found: $Destination" }
$dst = (Resolve-Path -LiteralPath $Destination).Path

$files = Get-ChildItem -LiteralPath $src -File | Sort-Object Name
Write-Host "publishing $($files.Count) file(s)"
Write-Host "  from: $src"
Write-Host "  to  : $dst"
Write-Host ""

$results = [System.Collections.Generic.List[object]]::new()

foreach ($f in $files) {
    $target = Join-Path $dst $f.Name
    $expectHash = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash
    $ok = $false
    $attempt = 0

    while (-not $ok -and $attempt -lt $MaxAttempts) {
        $attempt++
        if (Test-Path -LiteralPath $target) {
            Remove-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
        }
        Copy-Item -LiteralPath $f.FullName -Destination $target -Force
        Start-Sleep -Seconds $SettleSeconds

        if (Test-Path -LiteralPath $target) {
            $actual = Get-Item -LiteralPath $target
            if ($actual.Length -eq $f.Length) {
                $actualHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
                if ($actualHash -eq $expectHash) { $ok = $true }
            }
        }
    }

    $results.Add([pscustomobject]@{
        File     = $f.Name
        Bytes    = $f.Length
        Attempts = $attempt
        Verified = if ($ok) { "OK" } else { "FAILED" }
    })
    Write-Host ("  {0,-8} {1,-58} {2} byte(s), {3} attempt(s)" -f $(if($ok){"OK"}else{"FAILED"}), $f.Name, $f.Length, $attempt)
}

Write-Host ""
$failed = @($results | Where-Object { $_.Verified -ne "OK" })
if ($failed.Count -gt 0) {
    Write-Host "VERIFICATION FAILED for $($failed.Count) file(s):" -ForegroundColor Red
    $failed | ForEach-Object { Write-Host "   - $($_.File)" -ForegroundColor Red }
    Write-Host "Drive may still be syncing, or the cloud copy is winning. Re-run, or resolve in the Drive UI." -ForegroundColor Yellow
    exit 1
}
Write-Host "ALL $($results.Count) FILE(S) VERIFIED ON DRIVE" -ForegroundColor Green
exit 0
