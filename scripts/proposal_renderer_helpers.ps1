Set-StrictMode -Version Latest

$script:ProposalEngineContractAlgorithm = 'sha256-path-size-content-v1'
$script:ProposalEngineContractScope = @(
    'program/* (top-level files only)',
    'program/services/** (all files)',
    'share/registry/** (all files)',
    'share/fonts/truetype/** (all files)'
)

function Get-ProposalFileSha256 {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    return (Get-FileHash -LiteralPath $LiteralPath -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Get-ProposalRendererEngineContract {
    param([Parameter(Mandatory = $true)][string]$RuntimeRoot)

    $root = [System.IO.Path]::GetFullPath($RuntimeRoot)
    if (-not (Test-Path -LiteralPath $root -PathType Container)) {
        throw "Renderer runtime does not exist as a directory: $root"
    }
    $candidates = [System.Collections.Generic.Dictionary[string, System.IO.FileInfo]]::new(
        [System.StringComparer]::Ordinal
    )
    $scopeQueries = @(
        [pscustomobject]@{ Relative = 'program'; Recurse = $false },
        [pscustomobject]@{ Relative = 'program/services'; Recurse = $true },
        [pscustomobject]@{ Relative = 'share/registry'; Recurse = $true },
        [pscustomobject]@{ Relative = 'share/fonts/truetype'; Recurse = $true }
    )
    foreach ($query in $scopeQueries) {
        $scopeRoot = Join-Path $root ([string]$query.Relative)
        if (-not (Test-Path -LiteralPath $scopeRoot -PathType Container)) {
            continue
        }
        $items = if ([bool]$query.Recurse) {
            @(Get-ChildItem -LiteralPath $scopeRoot -File -Recurse -Force)
        }
        else {
            @(Get-ChildItem -LiteralPath $scopeRoot -File -Force)
        }
        foreach ($item in $items) {
            if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Renderer engine contract must not contain reparse-point files: $($item.Name)"
            }
            $relative = [System.IO.Path]::GetRelativePath($root, $item.FullName).
                Replace([System.IO.Path]::DirectorySeparatorChar, '/').
                Normalize([System.Text.NormalizationForm]::FormC)
            if ($candidates.ContainsKey($relative)) {
                continue
            }
            $candidates.Add($relative, $item)
        }
    }

    $pathsBySortKey = [System.Collections.Generic.Dictionary[string, string]]::new(
        [System.StringComparer]::Ordinal
    )
    foreach ($relative in $candidates.Keys) {
        $sortKey = [System.Convert]::ToHexString(
            [System.Text.Encoding]::UTF8.GetBytes($relative)
        )
        if ($pathsBySortKey.ContainsKey($sortKey)) {
            throw "Renderer engine contract contains duplicate normalized UTF-8 path: $relative"
        }
        $pathsBySortKey.Add($sortKey, $relative)
    }
    [string[]]$sortKeys = @($pathsBySortKey.Keys)
    [System.Array]::Sort($sortKeys, [System.StringComparer]::Ordinal)

    $digest = [System.Security.Cryptography.IncrementalHash]::CreateHash(
        [System.Security.Cryptography.HashAlgorithmName]::SHA256
    )
    $utf8 = [System.Text.UTF8Encoding]::new($false)
    [long]$totalBytes = 0
    try {
        foreach ($sortKey in $sortKeys) {
            $relative = $pathsBySortKey[$sortKey]
            $item = $candidates[$relative]
            $fileHash = Get-ProposalFileSha256 -LiteralPath $item.FullName
            $size = [long]$item.Length
            $totalBytes += $size
            $digest.AppendData($utf8.GetBytes("$relative$([char]0)$size$([char]0)$fileHash`n"))
        }
        $treeHash = [System.Convert]::ToHexString($digest.GetHashAndReset())
    }
    finally {
        $digest.Dispose()
    }

    return [ordered]@{
        algorithm = $script:ProposalEngineContractAlgorithm
        scope = @($script:ProposalEngineContractScope)
        file_count = $sortKeys.Count
        total_bytes = $totalBytes
        tree_sha256 = $treeHash
    }
}

function ConvertTo-ProposalWindowsProcessArgument {
    param([AllowEmptyString()][string]$Value)

    if ($Value.Length -gt 0 -and $Value -notmatch '[\s"]') {
        return $Value
    }
    $builder = [System.Text.StringBuilder]::new()
    [void]$builder.Append('"')
    [int]$backslashes = 0
    foreach ($character in $Value.ToCharArray()) {
        if ($character -eq '\') {
            $backslashes++
            continue
        }
        if ($character -eq '"') {
            [void]$builder.Append(('\' * (($backslashes * 2) + 1)))
            [void]$builder.Append('"')
            $backslashes = 0
            continue
        }
        if ($backslashes -gt 0) {
            [void]$builder.Append(('\' * $backslashes))
            $backslashes = 0
        }
        [void]$builder.Append($character)
    }
    if ($backslashes -gt 0) {
        [void]$builder.Append(('\' * ($backslashes * 2)))
    }
    [void]$builder.Append('"')
    return $builder.ToString()
}

function Invoke-ProposalBoundedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$ArgumentList,
        [Parameter(Mandatory = $true)][ValidateRange(1, 600)][int]$TimeoutSeconds,
        [Parameter(Mandatory = $true)][string]$ScratchRoot
    )

    $scratch = [System.IO.Path]::GetFullPath($ScratchRoot)
    [System.IO.Directory]::CreateDirectory($scratch) | Out-Null
    $processRoot = Join-Path $scratch ("proposal-process-$([guid]::NewGuid().ToString('N'))")
    $stdoutPath = Join-Path $processRoot 'stdout.txt'
    $stderrPath = Join-Path $processRoot 'stderr.txt'
    $process = $null
    [System.IO.Directory]::CreateDirectory($processRoot) | Out-Null
    try {
        $encodedArguments = @(
            $ArgumentList | ForEach-Object {
                ConvertTo-ProposalWindowsProcessArgument -Value ([string]$_)
            }
        )
        $process = Start-Process `
            -FilePath $FilePath `
            -ArgumentList $encodedArguments `
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
                throw (
                    "Process timed out after $TimeoutSeconds seconds and process-tree " +
                    "termination failed: $($_.Exception.Message)"
                )
            }
            throw "Process timed out after $TimeoutSeconds seconds."
        }
        $process.WaitForExit()
        $exitCode = $process.ExitCode
        $stdout = if (Test-Path -LiteralPath $stdoutPath -PathType Leaf) {
            $value = Get-Content -Raw -LiteralPath $stdoutPath
            if ($null -eq $value) { '' } else { $value.ToString().Trim() }
        }
        else { '' }
        $stderr = if (Test-Path -LiteralPath $stderrPath -PathType Leaf) {
            $value = Get-Content -Raw -LiteralPath $stderrPath
            if ($null -eq $value) { '' } else { $value.ToString().Trim() }
        }
        else { '' }
        return [pscustomobject]@{
            exit_code = $exitCode
            stdout = $stdout
            stderr = $stderr
        }
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
        if (Test-Path -LiteralPath $processRoot -PathType Container) {
            $resolvedProcessRoot = [System.IO.Path]::GetFullPath($processRoot)
            $scratchPrefix = $scratch.TrimEnd([System.IO.Path]::DirectorySeparatorChar) +
                [System.IO.Path]::DirectorySeparatorChar
            $safeLeaf = [System.IO.Path]::GetFileName($resolvedProcessRoot).StartsWith(
                'proposal-process-',
                [System.StringComparison]::Ordinal
            )
            if (
                -not $resolvedProcessRoot.StartsWith(
                    $scratchPrefix,
                    [System.StringComparison]::OrdinalIgnoreCase
                ) -or
                -not $safeLeaf
            ) {
                throw "Unsafe bounded-process cleanup target: $resolvedProcessRoot"
            }
            Remove-Item -LiteralPath $resolvedProcessRoot -Recurse -Force
        }
    }
}

function Copy-ProposalSharedFileNew {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination,
        [ref]$Published
    )

    $ErrorActionPreference = 'Stop'
    if ($null -ne $Published) { $Published.Value = $false }
    $destinationPath = [System.IO.Path]::GetFullPath($Destination)
    $destinationDirectory = Split-Path -Parent $destinationPath
    [System.IO.Directory]::CreateDirectory($destinationDirectory) | Out-Null
    $stage = Join-Path $destinationDirectory (
        ".$([System.IO.Path]::GetFileName($destinationPath)).copy-$([guid]::NewGuid().ToString('N')).tmp"
    )
    $input = $null
    $output = $null
    try {
        $share = [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
        $input = [System.IO.File]::Open(
            $Source,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            $share
        )
        $output = [System.IO.File]::Open(
            $stage,
            [System.IO.FileMode]::CreateNew,
            [System.IO.FileAccess]::Write,
            [System.IO.FileShare]::None
        )
        $input.CopyTo($output)
        $output.Flush($true)
        $output.Dispose()
        $output = $null
        $input.Dispose()
        $input = $null
        Move-Item -LiteralPath $stage -Destination $destinationPath -ErrorAction Stop
        if ($null -ne $Published) { $Published.Value = $true }
    }
    finally {
        if ($null -ne $output) { $output.Dispose() }
        if ($null -ne $input) { $input.Dispose() }
        if (Test-Path -LiteralPath $stage -PathType Leaf) {
            Remove-Item -LiteralPath $stage -Force
        }
    }
}

function Invoke-ProposalLibreOfficePdfExport {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][string]$SourceDocx,
        [Parameter(Mandatory = $true)][string]$DestinationPdf,
        [Parameter(Mandatory = $true)][string]$ProfileRoot,
        [Parameter(Mandatory = $true)][ValidateRange(10, 600)][int]$TimeoutSeconds,
        [ref]$Published
    )

    $ErrorActionPreference = 'Stop'
    if ($null -ne $Published) { $Published.Value = $false }
    $destinationPath = [System.IO.Path]::GetFullPath($DestinationPdf)
    $destinationDirectory = Split-Path -Parent $destinationPath
    [System.IO.Directory]::CreateDirectory($destinationDirectory) | Out-Null
    $stageRoot = Join-Path $destinationDirectory (
        ".proposal-pdf-stage-$([guid]::NewGuid().ToString('N'))"
    )
    [System.IO.Directory]::CreateDirectory($stageRoot) | Out-Null
    try {
        $profileUri = ([System.Uri]([System.IO.Path]::GetFullPath($ProfileRoot))).AbsoluteUri
        $arguments = @(
            '--headless',
            '--nologo',
            '--nodefault',
            '--nolockcheck',
            '--norestore',
            "-env:UserInstallation=$profileUri",
            '--convert-to',
            'pdf:writer_pdf_Export',
            '--outdir',
            $stageRoot,
            [System.IO.Path]::GetFullPath($SourceDocx)
        )
        $result = Invoke-ProposalBoundedProcess `
            -FilePath $Executable `
            -ArgumentList $arguments `
            -TimeoutSeconds $TimeoutSeconds `
            -ScratchRoot $ProfileRoot
        if ($result.exit_code -ne 0) {
            throw (
                "LibreOffice PDF export failed with exit code $($result.exit_code): " +
                "$($result.stderr) $($result.stdout)"
            )
        }
        $stagePdf = Join-Path $stageRoot (
            [System.IO.Path]::GetFileNameWithoutExtension($SourceDocx) + '.pdf'
        )
        if (-not (Test-Path -LiteralPath $stagePdf -PathType Leaf)) {
            throw 'LibreOffice did not create the staged PDF.'
        }
        if ((Get-Item -LiteralPath $stagePdf).Length -le 0) {
            throw 'LibreOffice created an empty staged PDF.'
        }
        Move-Item -LiteralPath $stagePdf -Destination $destinationPath -ErrorAction Stop
        if ($null -ne $Published) { $Published.Value = $true }
    }
    finally {
        if (Test-Path -LiteralPath $stageRoot -PathType Container) {
            $resolvedStage = [System.IO.Path]::GetFullPath($stageRoot)
            $destinationPrefix = $destinationDirectory.TrimEnd(
                [System.IO.Path]::DirectorySeparatorChar
            ) + [System.IO.Path]::DirectorySeparatorChar
            $safeLeaf = [System.IO.Path]::GetFileName($resolvedStage).StartsWith(
                '.proposal-pdf-stage-',
                [System.StringComparison]::Ordinal
            )
            if (
                -not $resolvedStage.StartsWith(
                    $destinationPrefix,
                    [System.StringComparison]::OrdinalIgnoreCase
                ) -or
                -not $safeLeaf
            ) {
                throw "Unsafe LibreOffice PDF staging cleanup target: $resolvedStage"
            }
            Remove-Item -LiteralPath $resolvedStage -Recurse -Force
        }
    }
}
