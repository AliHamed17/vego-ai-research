[CmdletBinding()]
param(
    [string]$ManifestPath,

    [string]$RuntimeRoot,

    [switch]$VerifyOnly,

    [ValidateRange(1, 120)]
    [int]$VersionProbeTimeoutSeconds = 30
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$helperScript = Join-Path $PSScriptRoot 'proposal_renderer_helpers.ps1'
if (-not (Test-Path -LiteralPath $helperScript -PathType Leaf)) {
    throw "Renderer helper script does not exist: $helperScript"
}
. $helperScript
if ([string]::IsNullOrWhiteSpace($ManifestPath)) {
    $ManifestPath = Join-Path $projectRoot 'docs/research/phd-proposal/figures/renderer-manifest.json'
}
if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
    throw "Renderer manifest does not exist: $ManifestPath"
}
$manifestPathResolved = (Resolve-Path -LiteralPath $ManifestPath).Path
$manifest = Get-Content -Raw -LiteralPath $manifestPathResolved | ConvertFrom-Json -Depth 30
if ([int]$manifest.schema_version -ne 1) {
    throw 'Renderer manifest schema_version must be 1.'
}
if ([string]::IsNullOrWhiteSpace($RuntimeRoot)) {
    $RuntimeRoot = Join-Path $projectRoot '.cache/libreoffice-24.2.7.2/admin'
}
$runtimePath = [System.IO.Path]::GetFullPath($RuntimeRoot)
$cacheRoot = [System.IO.Path]::GetFullPath((Join-Path $projectRoot '.cache'))
$cachePrefix = $cacheRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
if (-not $runtimePath.StartsWith($cachePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Renderer runtime must be workspace-local under the ignored .cache directory.'
}

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    return (Get-FileHash -LiteralPath $LiteralPath -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Invoke-BoundedLibreOfficeVersionProbe {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds
    )

    $profileRoot = Join-Path $cacheRoot ("renderer-version-profile-$([guid]::NewGuid().ToString('N'))")
    $stdoutPath = Join-Path $profileRoot 'stdout.txt'
    $stderrPath = Join-Path $profileRoot 'stderr.txt'
    $process = $null
    [System.IO.Directory]::CreateDirectory($profileRoot) | Out-Null
    try {
        $profileUri = ([System.Uri]$profileRoot).AbsoluteUri
        $arguments = @(
            '--headless',
            '--nologo',
            '--nodefault',
            '--nolockcheck',
            '--norestore',
            "-env:UserInstallation=$profileUri",
            '--version'
        )
        $process = Start-Process `
            -FilePath $Executable `
            -ArgumentList $arguments `
            -WindowStyle Hidden `
            -PassThru `
            -RedirectStandardOutput $stdoutPath `
            -RedirectStandardError $stderrPath
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            try {
                $process.Kill($true)
                $process.WaitForExit()
            }
            catch {
                throw "Renderer version probe timed out and process-tree termination failed: $($_.Exception.Message)"
            }
            throw "Renderer version probe timed out after $TimeoutSeconds seconds."
        }
        $process.WaitForExit()
        $exitCode = $process.ExitCode
        $stdout = if (Test-Path -LiteralPath $stdoutPath -PathType Leaf) {
            $stdoutRaw = Get-Content -Raw -LiteralPath $stdoutPath
            if ($null -eq $stdoutRaw) { '' } else { $stdoutRaw.ToString().Trim() }
        }
        else {
            ''
        }
        $stderr = if (Test-Path -LiteralPath $stderrPath -PathType Leaf) {
            $stderrRaw = Get-Content -Raw -LiteralPath $stderrPath
            if ($null -eq $stderrRaw) { '' } else { $stderrRaw.ToString().Trim() }
        }
        else {
            ''
        }
        if ($exitCode -ne 0) {
            throw "Pinned soffice.com version probe failed with exit code $exitCode`: $stderr"
        }
        if ([string]::IsNullOrWhiteSpace($stdout)) {
            throw 'Pinned soffice.com version probe returned no version output.'
        }
        return $stdout
    }
    catch {
        throw "Renderer version probe failed at line $($_.InvocationInfo.ScriptLineNumber): $($_.Exception.Message)"
    }
    finally {
        if ($null -ne $process) {
            try {
                if (-not $process.HasExited) {
                    $process.Kill($true)
                    $process.WaitForExit()
                }
            }
            finally {
                $process.Dispose()
            }
        }
        if (Test-Path -LiteralPath $profileRoot -PathType Container) {
            $resolvedProfile = [System.IO.Path]::GetFullPath($profileRoot)
            $safeLeaf = [System.IO.Path]::GetFileName($resolvedProfile).StartsWith(
                'renderer-version-profile-',
                [System.StringComparison]::Ordinal
            )
            if (
                -not $resolvedProfile.StartsWith(
                    $cachePrefix,
                    [System.StringComparison]::OrdinalIgnoreCase
                ) -or
                -not $safeLeaf
            ) {
                throw "Unsafe renderer version-profile cleanup target: $resolvedProfile"
            }
            Remove-Item -LiteralPath $resolvedProfile -Recurse -Force
        }
    }
}

function Assert-Download {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $true)][long]$ExpectedBytes,
        [Parameter(Mandatory = $true)][string]$ExpectedSha256,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if (Test-Path -LiteralPath $Destination -PathType Leaf) {
        $item = Get-Item -LiteralPath $Destination
        $actualHash = Get-Sha256 -LiteralPath $Destination
        if ($item.Length -ne $ExpectedBytes -or $actualHash -ne $ExpectedSha256.ToUpperInvariant()) {
            throw "Cached download drifted and will not be replaced automatically: $($item.Name)"
        }
        return
    }
    $directory = Split-Path -Parent $Destination
    [System.IO.Directory]::CreateDirectory($directory) | Out-Null
    $partial = Join-Path $directory (".$([System.IO.Path]::GetFileName($Destination)).$([guid]::NewGuid().ToString('N')).partial")
    try {
        Invoke-WebRequest -Uri $Url -OutFile $partial
        $item = Get-Item -LiteralPath $partial
        $actualHash = Get-Sha256 -LiteralPath $partial
        if ($item.Length -ne $ExpectedBytes -or $actualHash -ne $ExpectedSha256.ToUpperInvariant()) {
            throw "Downloaded artifact failed its pinned size/hash gate: $($item.Name)"
        }
        Move-Item -LiteralPath $partial -Destination $Destination
    }
    finally {
        if (Test-Path -LiteralPath $partial -PathType Leaf) {
            Remove-Item -LiteralPath $partial -Force
        }
    }
}

function Get-RendererEvidence {
    param([Parameter(Mandatory = $true)][string]$Root)

    $executable = Join-Path $Root ([string]$manifest.renderer.relative_executable)
    if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
        throw 'Pinned soffice.com is missing from the workspace runtime.'
    }
    $executableHash = Get-Sha256 -LiteralPath $executable
    $expectedExecutableHash = ([string]$manifest.renderer.executable_sha256).ToUpperInvariant()
    if ($executableHash -ne $expectedExecutableHash) {
        throw "Renderer executable hash drift: expected $expectedExecutableHash, got $executableHash."
    }
    $versionOutput = Invoke-BoundedLibreOfficeVersionProbe `
        -Executable $executable `
        -TimeoutSeconds $VersionProbeTimeoutSeconds
    if ($versionOutput -ne [string]$manifest.renderer.version_output) {
        throw "Renderer version drift: expected '$($manifest.renderer.version_output)', got '$versionOutput'."
    }

    $fontHashes = [ordered]@{}
    foreach ($font in @($manifest.fonts)) {
        $fontPath = Join-Path $Root ([string]$font.relative_path)
        if (-not (Test-Path -LiteralPath $fontPath -PathType Leaf)) {
            throw "Pinned renderer font is missing: $([System.IO.Path]::GetFileName($fontPath))"
        }
        $actualHash = Get-Sha256 -LiteralPath $fontPath
        $expectedHash = ([string]$font.sha256).ToUpperInvariant()
        if ($actualHash -ne $expectedHash) {
            throw (
                "Renderer font hash drift for $([System.IO.Path]::GetFileName($fontPath)): " +
                "expected $expectedHash, got $actualHash."
            )
        }
        $fontHashes[[System.IO.Path]::GetFileName($fontPath)] = $actualHash
    }

    $engineContract = Get-ProposalRendererEngineContract -RuntimeRoot $Root
    $expectedEngineContract = $manifest.renderer.engine_contract
    if ($null -eq $expectedEngineContract) {
        throw 'Renderer manifest must declare renderer.engine_contract.'
    }
    $expectedScope = @($expectedEngineContract.scope)
    $actualScope = @($engineContract.scope)
    $scopeMatches = $expectedScope.Count -eq $actualScope.Count
    if ($scopeMatches) {
        for ($index = 0; $index -lt $expectedScope.Count; $index++) {
            if ([string]$expectedScope[$index] -cne [string]$actualScope[$index]) {
                $scopeMatches = $false
                break
            }
        }
    }
    if (
        [string]$expectedEngineContract.algorithm -cne [string]$engineContract.algorithm -or
        -not $scopeMatches -or
        [long]$expectedEngineContract.file_count -ne [long]$engineContract.file_count -or
        [long]$expectedEngineContract.total_bytes -ne [long]$engineContract.total_bytes -or
        ([string]$expectedEngineContract.tree_sha256).ToUpperInvariant() -cne
            [string]$engineContract.tree_sha256
    ) {
        throw (
            'Renderer engine contract drift: expected ' +
            ($expectedEngineContract | ConvertTo-Json -Depth 10 -Compress) +
            ', got ' +
            ($engineContract | ConvertTo-Json -Depth 10 -Compress) +
            '.'
        )
    }

    return [ordered]@{
        passed = $true
        renderer = [ordered]@{
            name = [string]$manifest.renderer.name
            version = [string]$manifest.renderer.version
            build_id = [string]$manifest.renderer.build_id
            executable_sha256 = $executableHash
            manifest_sha256 = Get-Sha256 -LiteralPath $manifestPathResolved
            pdf_export_filter = [string]$manifest.renderer.pdf_export_filter
            workspace_local = $true
            version_output = $versionOutput
            engine_contract = $engineContract
        }
        fonts = [ordered]@{
            count = $fontHashes.Count
            sha256 = $fontHashes
        }
    }
}

if (Test-Path -LiteralPath $runtimePath -PathType Container) {
    $evidence = Get-RendererEvidence -Root $runtimePath
    [Console]::Out.Write(($evidence | ConvertTo-Json -Depth 10))
    exit 0
}
if ($VerifyOnly) {
    throw "Workspace-local renderer has not been bootstrapped: $runtimePath"
}

$runtimeParent = Split-Path -Parent $runtimePath
[System.IO.Directory]::CreateDirectory($runtimeParent) | Out-Null
$archive = $manifest.renderer.archive
$msiPath = Join-Path $runtimeParent 'LibreOffice_24.2.7.2_Win_x86-64.msi'
Assert-Download `
    -Url ([string]$archive.url) `
    -ExpectedBytes ([long]$archive.bytes) `
    -ExpectedSha256 ([string]$archive.sha256) `
    -Destination $msiPath

$caladeaSource = @($manifest.font_sources | Where-Object { [string]$_.family -eq 'Caladea' })
if ($caladeaSource.Count -ne 1) {
    throw 'Renderer manifest must declare exactly one Caladea source archive.'
}
$caladeaRoot = Join-Path $projectRoot '.cache/debian-caladea-20200211'
$caladeaArchive = Join-Path $caladeaRoot 'fonts-crosextra-caladea_20200211.orig.tar.gz'
Assert-Download `
    -Url ([string]$caladeaSource[0].url) `
    -ExpectedBytes ([long]$caladeaSource[0].bytes) `
    -ExpectedSha256 ([string]$caladeaSource[0].sha256) `
    -Destination $caladeaArchive

$stagingBase = Join-Path $runtimeParent ("renderer-bootstrap-$([guid]::NewGuid().ToString('N'))")
$administrativeRoot = Join-Path $stagingBase 'runtime'
$fontExtractRoot = Join-Path $stagingBase 'caladea'
[System.IO.Directory]::CreateDirectory($administrativeRoot) | Out-Null
[System.IO.Directory]::CreateDirectory($fontExtractRoot) | Out-Null
try {
    $logPath = Join-Path $stagingBase 'administrative-extract.log'
    & msiexec.exe '/a' $msiPath '/qn' "TARGETDIR=$administrativeRoot" '/L*v' $logPath
    if ($LASTEXITCODE -ne 0) {
        throw "LibreOffice administrative extraction failed with exit code $LASTEXITCODE."
    }
    $sofficeCandidates = @(Get-ChildItem -LiteralPath $administrativeRoot -Recurse -File -Filter 'soffice.com')
    if ($sofficeCandidates.Count -ne 1) {
        throw "Expected exactly one soffice.com in extracted MSI; found $($sofficeCandidates.Count)."
    }
    $candidateRoot = Split-Path -Parent (Split-Path -Parent $sofficeCandidates[0].FullName)

    & tar.exe '-xzf' $caladeaArchive '-C' $fontExtractRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Caladea source extraction failed with exit code $LASTEXITCODE."
    }
    $runtimeFonts = Join-Path $candidateRoot 'share/fonts/truetype'
    [System.IO.Directory]::CreateDirectory($runtimeFonts) | Out-Null
    foreach ($font in @($manifest.fonts)) {
        $name = [System.IO.Path]::GetFileName([string]$font.relative_path)
        if ($name.StartsWith('Carlito-', [System.StringComparison]::Ordinal)) {
            $sourceFont = Join-Path $candidateRoot "Fonts/$name"
        }
        else {
            $matches = @(Get-ChildItem -LiteralPath $fontExtractRoot -Recurse -File -Filter $name)
            if ($matches.Count -ne 1) {
                throw "Expected exactly one $name in the Caladea source; found $($matches.Count)."
            }
            $sourceFont = $matches[0].FullName
        }
        if (-not (Test-Path -LiteralPath $sourceFont -PathType Leaf)) {
            throw "Renderer font source is missing: $name"
        }
        [System.IO.File]::Copy($sourceFont, (Join-Path $runtimeFonts $name), $false)
    }

    $null = Get-RendererEvidence -Root $candidateRoot
    if (Test-Path -LiteralPath $runtimePath) {
        throw 'Renderer runtime appeared during bootstrap; refusing to overwrite it.'
    }
    Move-Item -LiteralPath $candidateRoot -Destination $runtimePath
    $evidence = Get-RendererEvidence -Root $runtimePath
}
finally {
    if (Test-Path -LiteralPath $stagingBase -PathType Container) {
        $resolvedStage = [System.IO.Path]::GetFullPath($stagingBase)
        $safeLeaf = [System.IO.Path]::GetFileName($resolvedStage).StartsWith(
            'renderer-bootstrap-',
            [System.StringComparison]::Ordinal
        )
        if (-not $resolvedStage.StartsWith($runtimeParent, [System.StringComparison]::OrdinalIgnoreCase) -or -not $safeLeaf) {
            throw "Unsafe renderer staging cleanup target: $resolvedStage"
        }
        Remove-Item -LiteralPath $resolvedStage -Recurse -Force
    }
}

[Console]::Out.Write(($evidence | ConvertTo-Json -Depth 10))
