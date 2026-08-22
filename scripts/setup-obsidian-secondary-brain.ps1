[CmdletBinding()]
param(
    [string]$VaultRoot = (Join-Path $env:USERPROFILE 'Documents\Obsidian\VEGO-AI Secondary Brain'),
    [switch]$Initialize,
    [switch]$RegisterLocalReminderTask
)

$ErrorActionPreference = 'Stop'

function Assert-VaultOutsideGitRepository {
    param([Parameter(Mandatory)][string]$Path)

    $candidate = [System.IO.Path]::GetFullPath($Path)
    $current = [System.IO.DirectoryInfo]::new($candidate)
    while ($null -ne $current) {
        if (Test-Path -LiteralPath (Join-Path $current.FullName '.git')) {
            throw 'A private vault cannot be created inside a Git repository checkout.'
        }
        $current = $current.Parent
    }
}

function Test-EfsEncryptedProbe {
    param([Parameter(Mandatory)][string]$Path)

    $probe = Join-Path $Path '.encryption-verification-probe'
    try {
        New-Item -ItemType File -Path $probe -Force | Out-Null
        $status = & cipher.exe /c $probe 2>&1 | Out-String
        return $status -match '(?m)^\s*E\s+\S+'
    }
    finally {
        if (Test-Path -LiteralPath $probe) {
            Remove-Item -LiteralPath $probe -Force
        }
    }
}

if (-not $Initialize) {
    Write-Host 'No vault was created. Re-run with -Initialize after reviewing the requested local path.'
    Write-Host "Requested vault root: $VaultRoot"
    exit 0
}

Assert-VaultOutsideGitRepository -Path $VaultRoot
New-Item -ItemType Directory -Path $VaultRoot -Force | Out-Null
& cipher.exe /e $VaultRoot | Out-Host
if (-not (Test-EfsEncryptedProbe -Path $VaultRoot)) {
    throw 'The local vault is not verifiably encrypted with Windows EFS. Initialization stopped before any personal content was imported.'
}

$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    uv run python -m obsidian_brain init --vault-root $VaultRoot
}
finally {
    Pop-Location
}

if ($RegisterLocalReminderTask) {
    $taskName = 'VEGO-AI Obsidian Secondary Brain - Local Reminder Refresh'
    $refreshScript = Join-Path $PSScriptRoot 'refresh-obsidian-secondary-brain.ps1'
    $arguments = "-NoProfile -NonInteractive -File `"$refreshScript`" -VaultRoot `"$VaultRoot`""
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $arguments
    $trigger = New-ScheduledTaskTrigger -Daily -At 09:00
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description 'Local-only Obsidian reminder refresh. No network synchronization, email, sharing, or financial action.' -Force | Out-Null
    Write-Host "Registered local-only daily task: $taskName"
}
