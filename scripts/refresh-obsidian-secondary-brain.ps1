[CmdletBinding()]
param([Parameter(Mandatory)][string]$VaultRoot)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    uv run python -m obsidian_brain refresh --vault-root $VaultRoot
}
finally {
    Pop-Location
}
