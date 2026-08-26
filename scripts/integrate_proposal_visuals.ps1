[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SourceDocx,

    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,

    [Parameter(Mandatory = $true)]
    [string]$FigureRoot,

    [string]$ContentManifest,

    [string]$QaReceipt,

    [string]$IntegrationReceipt,

    [string]$RendererManifest,

    [string]$LibreOfficeExecutable,

    [ValidateRange(10, 600)]
    [int]$LibreOfficeExportTimeoutSeconds = 120,

    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string]$ExpectedSourceSha256 = 'D73C840BD606695DAE50EE2E9304403D0ECB0518BCD43F05FE68B1DE166063DA',

    [string]$PythonExecutable = 'python',

    [switch]$PlanOnly
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
if ([string]::IsNullOrWhiteSpace($ContentManifest)) {
    $ContentManifest = Join-Path $projectRoot 'docs/research/phd-proposal/figures/content.json'
}
if ([string]::IsNullOrWhiteSpace($QaReceipt)) {
    $QaReceipt = Join-Path $projectRoot 'docs/research/phd-proposal/figures/qa/qa-receipt.json'
}
if ([string]::IsNullOrWhiteSpace($IntegrationReceipt)) {
    $IntegrationReceipt = Join-Path $projectRoot 'docs/research/phd-proposal/figures/qa/integration-receipt.json'
}
$canonicalRendererManifest = [System.IO.Path]::GetFullPath(
    (Join-Path $projectRoot 'docs/research/phd-proposal/figures/renderer-manifest.json')
)
if ([string]::IsNullOrWhiteSpace($RendererManifest)) {
    $RendererManifest = $canonicalRendererManifest
}
elseif (
    -not [System.IO.Path]::GetFullPath($RendererManifest).Equals(
        $canonicalRendererManifest,
        [System.StringComparison]::OrdinalIgnoreCase
    )
) {
    throw 'Production integration requires the tracked canonical renderer manifest.'
}
if ([string]::IsNullOrWhiteSpace($LibreOfficeExecutable)) {
    $LibreOfficeExecutable = Join-Path $projectRoot '.cache/libreoffice-24.2.7.2/admin/program/soffice.com'
}

function Resolve-ExistingFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LiteralPath,
        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    if (-not (Test-Path -LiteralPath $LiteralPath -PathType Leaf)) {
        throw "$Label does not exist as a file: $LiteralPath"
    }
    return (Resolve-Path -LiteralPath $LiteralPath).Path
}

function Get-SharedSha256 {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    $share = [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
    $stream = [System.IO.File]::Open(
        $LiteralPath,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::Read,
        $share
    )
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return [System.Convert]::ToHexString($sha.ComputeHash($stream))
    }
    finally {
        $sha.Dispose()
        $stream.Dispose()
    }
}

function Invoke-DocxLayoutMaterializer {
    param([Parameter(Mandatory = $true)][string]$Docx)

    $layoutArguments = @(
        '-m', 'proposal_visuals.docx_layout',
        '--docx', $Docx
    )
    $savedPythonPath = $env:PYTHONPATH
    if ([string]::IsNullOrWhiteSpace($savedPythonPath)) {
        $env:PYTHONPATH = $srcPath
    }
    else {
        $env:PYTHONPATH = "$srcPath$([System.IO.Path]::PathSeparator)$savedPythonPath"
    }
    try {
        $layoutLines = @(& $PythonExecutable @layoutArguments)
        $layoutExitCode = $LASTEXITCODE
    }
    finally {
        $env:PYTHONPATH = $savedPythonPath
    }
    if ($layoutExitCode -ne 0) {
        throw "Derived DOCX layout materialization was blocked with exit code $layoutExitCode."
    }
    $layoutJson = $layoutLines -join [System.Environment]::NewLine
    $layout = $layoutJson | ConvertFrom-Json -Depth 10
    if (
        $layout.passed -ne $true -or
        $layout.changed -ne $true -or
        [int]$layout.matched_paragraphs -ne 1 -or
        [int]$layout.keep_lines_count -ne 1 -or
        [string]$layout.sha256_before -eq [string]$layout.sha256_after
    ) {
        throw 'Derived DOCX did not materialize the one required keep-lines layout control.'
    }
    return $layout
}

function Remove-DerivedFile {
    param([string]$LiteralPath)

    if (-not [string]::IsNullOrWhiteSpace($LiteralPath) -and (Test-Path -LiteralPath $LiteralPath -PathType Leaf)) {
        Remove-Item -LiteralPath $LiteralPath -Force
    }
}

function New-IsolatedLibreOfficeProfile {
    param([Parameter(Mandatory = $true)][string]$ProfileRoot)

    $userDirectory = Join-Path $ProfileRoot 'user'
    [System.IO.Directory]::CreateDirectory($userDirectory) | Out-Null
    $registryPath = Join-Path $userDirectory 'registrymodifications.xcu'
    $profileXml = @'
<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <item oor:path="/org.openoffice.Office.Common/Font/Substitution/FontPairs">
    <node oor:name="_0" oor:op="replace">
      <prop oor:name="Always" oor:op="fuse"><value>true</value></prop>
      <prop oor:name="ReplaceFont" oor:op="fuse"><value>Calibri</value></prop>
      <prop oor:name="OnScreenOnly" oor:op="fuse"><value>false</value></prop>
      <prop oor:name="SubstituteFont" oor:op="fuse"><value>Carlito</value></prop>
    </node>
    <node oor:name="_1" oor:op="replace">
      <prop oor:name="Always" oor:op="fuse"><value>true</value></prop>
      <prop oor:name="ReplaceFont" oor:op="fuse"><value>Cambria</value></prop>
      <prop oor:name="OnScreenOnly" oor:op="fuse"><value>false</value></prop>
      <prop oor:name="SubstituteFont" oor:op="fuse"><value>Caladea</value></prop>
    </node>
  </item>
  <item oor:path="/org.openoffice.Office.Common/Font/Substitution">
    <prop oor:name="Replacement" oor:op="fuse"><value>true</value></prop>
  </item>
</oor:items>
'@
    [System.IO.File]::WriteAllText(
        $registryPath,
        $profileXml,
        [System.Text.UTF8Encoding]::new($false)
    )
    return $registryPath
}

function Invoke-PostIntegrationVerifier {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Figures,
        [Parameter(Mandatory = $true)][string]$Content,
        [Parameter(Mandatory = $true)][string]$Qa,
        [Parameter(Mandatory = $true)][string]$Output,
        [Parameter(Mandatory = $true)][string]$Receipt,
        [Parameter(Mandatory = $true)][string]$SourceSha256,
        [Parameter(Mandatory = $true)][string]$RendererManifestPath,
        [Parameter(Mandatory = $true)][string]$RendererRuntimeRoot,
        [Parameter(Mandatory = $true)][string]$RendererProfilePath,
        [Parameter(Mandatory = $true)][string]$RendererVersion,
        [Parameter(Mandatory = $true)][string]$RendererWorkspace,
        [Parameter(Mandatory = $true)][int]$BaselinePages,
        [Parameter(Mandatory = $true)][int]$IntegratedPages
    )

    $verifyArguments = @(
        '-m', 'proposal_visuals.document_integrity',
        '--source-docx', $Source,
        '--figure-root', $Figures,
        '--content-manifest', $Content,
        '--qa-receipt', $Qa,
        '--output-root', $Output,
        '--integration-receipt', $Receipt,
        '--expected-source-sha256', $SourceSha256,
        '--renderer-manifest', $RendererManifestPath,
        '--renderer-runtime-root', $RendererRuntimeRoot,
        '--renderer-profile', $RendererProfilePath,
        '--renderer-version-output', $RendererVersion,
        '--renderer-workspace-root', $RendererWorkspace,
        '--word-baseline-pages', [string]$BaselinePages,
        '--word-integrated-pages', [string]$IntegratedPages
    )
    $savedPythonPath = $env:PYTHONPATH
    if ([string]::IsNullOrWhiteSpace($savedPythonPath)) {
        $env:PYTHONPATH = $srcPath
    }
    else {
        $env:PYTHONPATH = "$srcPath$([System.IO.Path]::PathSeparator)$savedPythonPath"
    }
    try {
        $receiptLines = @(& $PythonExecutable @verifyArguments)
        $receiptExitCode = $LASTEXITCODE
    }
    finally {
        $env:PYTHONPATH = $savedPythonPath
    }
    if ($receiptExitCode -ne 0) {
        throw "Post-integration integrity verification was blocked with exit code $receiptExitCode."
    }
    if (-not (Test-Path -LiteralPath $Receipt -PathType Leaf)) {
        throw 'Post-integration verifier returned success without creating its durable receipt.'
    }
    $receiptJson = $receiptLines -join [System.Environment]::NewLine
    $receiptPayload = $receiptJson | ConvertFrom-Json -Depth 50
    if ($receiptPayload.passed -ne $true) {
        throw 'Post-integration verifier returned a nonpassing receipt.'
    }
    return $receiptJson
}

$sourcePath = Resolve-ExistingFile -LiteralPath $SourceDocx -Label 'Source DOCX'
$figurePath = (Resolve-Path -LiteralPath $FigureRoot).Path
$contentPath = Resolve-ExistingFile -LiteralPath $ContentManifest -Label 'Content manifest'
$qaPath = Resolve-ExistingFile -LiteralPath $QaReceipt -Label 'QA receipt'
$rendererManifestPath = Resolve-ExistingFile -LiteralPath $RendererManifest -Label 'Renderer manifest'
$outputPath = [System.IO.Path]::GetFullPath($OutputRoot)
$integrationReceiptPath = [System.IO.Path]::GetFullPath($IntegrationReceipt)

$priorPythonPath = $env:PYTHONPATH
$srcPath = Join-Path $projectRoot 'src'
if ([string]::IsNullOrWhiteSpace($priorPythonPath)) {
    $env:PYTHONPATH = $srcPath
}
else {
    $env:PYTHONPATH = "$srcPath$([System.IO.Path]::PathSeparator)$priorPythonPath"
}

$planArguments = @(
    '-m', 'proposal_visuals.integration',
    '--source-docx', $sourcePath,
    '--figure-root', $figurePath,
    '--content-manifest', $contentPath,
    '--qa-receipt', $qaPath,
    '--output-root', $outputPath,
    '--expected-source-sha256', $ExpectedSourceSha256.ToUpperInvariant()
)

try {
    $planLines = @(& $PythonExecutable @planArguments)
    $planExitCode = $LASTEXITCODE
}
finally {
    $env:PYTHONPATH = $priorPythonPath
}

if ($planExitCode -ne 0) {
    throw "Integration planning was blocked with exit code $planExitCode. Word was not started."
}
$planJson = $planLines -join [System.Environment]::NewLine
$plan = $planJson | ConvertFrom-Json -Depth 30

if ($PlanOnly) {
    [Console]::Out.Write($planJson)
    exit 0
}

$expectedHash = $plan.source.sha256.ToUpperInvariant()
$preCopyHash = Get-SharedSha256 -LiteralPath $sourcePath
if ($preCopyHash -ne $expectedHash) {
    throw "Source changed after planning: expected $expectedHash, observed $preCopyHash."
}
$derivedDocx = [System.IO.Path]::GetFullPath([string]$plan.output_docx)
$derivedPdf = [System.IO.Path]::GetFullPath([string]$plan.output_pdf)
if ($derivedDocx -eq $sourcePath -or $derivedPdf -eq $sourcePath) {
    throw 'Derived outputs must never resolve to the source DOCX.'
}
if (
    (Test-Path -LiteralPath $derivedDocx) -or
    (Test-Path -LiteralPath $derivedPdf) -or
    (Test-Path -LiteralPath $integrationReceiptPath)
) {
    throw (
        'Derived output already exists, or an integration receipt already exists. ' +
        'Move or review the controlled artifacts before a new integration run.'
    )
}

$docxDirectory = Split-Path -Parent $derivedDocx
$pdfDirectory = Split-Path -Parent $derivedPdf
[System.IO.Directory]::CreateDirectory($docxDirectory) | Out-Null
[System.IO.Directory]::CreateDirectory($pdfDirectory) | Out-Null

$rendererWorkspacePath = $projectRoot
$libreOfficePath = Resolve-ExistingFile -LiteralPath $LibreOfficeExecutable -Label 'Pinned soffice.com'
$rendererRuntimeRoot = Split-Path -Parent (Split-Path -Parent $libreOfficePath)
$rendererManifestPayload = Get-Content -Raw -LiteralPath $rendererManifestPath | ConvertFrom-Json -Depth 30
$expectedLibreOfficePath = [System.IO.Path]::GetFullPath(
    (Join-Path $rendererRuntimeRoot ([string]$rendererManifestPayload.renderer.relative_executable))
)
if (-not $libreOfficePath.Equals($expectedLibreOfficePath, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'LibreOfficeExecutable does not resolve to the manifest-pinned soffice.com location.'
}

$bootstrapScript = Join-Path $PSScriptRoot 'bootstrap_proposal_renderer.ps1'
$pwshExecutable = Join-Path $PSHOME 'pwsh.exe'
$rendererVerification = @(
    & $pwshExecutable `
        '-NoProfile' `
        '-NonInteractive' `
        '-File' $bootstrapScript `
        -ManifestPath $rendererManifestPath `
        -RuntimeRoot $rendererRuntimeRoot `
        -VerifyOnly
)
if ($LASTEXITCODE -ne 0) {
    throw "Pinned LibreOffice runtime verification failed with exit code $LASTEXITCODE."
}
$rendererVerificationPayload = ($rendererVerification -join [System.Environment]::NewLine) |
    ConvertFrom-Json -Depth 30
if ($rendererVerificationPayload.passed -ne $true) {
    throw 'Pinned LibreOffice runtime verification returned a nonpassing result.'
}
$LibreOfficeVersionOutput = [string]$rendererVerificationPayload.renderer.version_output
if ([string]::IsNullOrWhiteSpace($LibreOfficeVersionOutput)) {
    throw 'Pinned LibreOffice runtime verification omitted its validated version output.'
}

$word = $null
$document = $null
$integrationSucceeded = $false
$createdDerivedDocx = $false
$createdDerivedPdf = $false
$createdIntegrationReceipt = $false
$WordBaselinePages = 0
$WordIntegratedPages = 0
$profileRoot = Join-Path $projectRoot ('.cache/proposal-integration-profile-' + [guid]::NewGuid().ToString('N'))
$profileRegistryPath = $null
try {
    [System.IO.Directory]::CreateDirectory($profileRoot) | Out-Null
    $profileRegistryPath = New-IsolatedLibreOfficeProfile -ProfileRoot $profileRoot
    $docxPublished = $false
    try {
        Copy-ProposalSharedFileNew `
            -Source $sourcePath `
            -Destination $derivedDocx `
            -Published ([ref]$docxPublished)
    }
    finally {
        if ($docxPublished) { $createdDerivedDocx = $true }
    }
    $postCopySourceHash = Get-SharedSha256 -LiteralPath $sourcePath
    $copyHash = Get-SharedSha256 -LiteralPath $derivedDocx
    if ($postCopySourceHash -ne $expectedHash -or $copyHash -ne $expectedHash) {
        throw (
            'The source was not stable while copying. ' +
            "Expected $expectedHash; source $postCopySourceHash; copy $copyHash."
        )
    }

    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($derivedDocx, $false, $false, $false)
    if ([System.IO.Path]::GetFullPath($document.FullName) -ne $derivedDocx) {
        throw 'Word opened a document other than the controlled derived copy.'
    }
    $document.Repaginate()
    $WordBaselinePages = [int]$document.ComputeStatistics(2)
    if ($WordBaselinePages -le 0) {
        throw 'Word baseline pagination did not return a positive page count.'
    }
    if ($document.InlineShapes.Count -ne 10) {
        throw "Expected 10 inline figures before replacement; found $($document.InlineShapes.Count)."
    }

    for ($index = 10; $index -ge 1; $index--) {
        $replacement = $plan.replacements[$index - 1]
        if ([int]$replacement.inline_shape_index -ne $index) {
            throw "Plan order drift at replacement $index."
        }
        $figureFile = Resolve-ExistingFile -LiteralPath ([string]$replacement.figure_path) -Label "Figure $index SVG"
        $figureHash = Get-SharedSha256 -LiteralPath $figureFile
        if ($figureHash -ne ([string]$replacement.figure_sha256).ToUpperInvariant()) {
            throw "Figure $index changed after QA planning; Word integration is blocked."
        }
        $oldShape = $document.InlineShapes.Item($index)
        $oldRange = $null
        $newShape = $null
        try {
            $expectedWidthPoints = [double]$replacement.width_emu / 12700.0
            $oldWidthPoints = [double]$oldShape.Width
            if ([Math]::Abs($oldWidthPoints - $expectedWidthPoints) -gt 0.5) {
                throw (
                    "Inline figure $index width drift: expected $expectedWidthPoints pt, " +
                    "observed $oldWidthPoints pt."
                )
            }
            $oldRange = $oldShape.Range.Duplicate
            $oldShape.Delete()
            $newShape = $document.InlineShapes.AddPicture($figureFile, $false, $true, $oldRange)
            $newShape.LockAspectRatio = -1
            $newShape.Width = $oldWidthPoints
            $newShape.AlternativeText = [string]$replacement.alt_text
        }
        finally {
            if ($null -ne $newShape) {
                [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($newShape)
            }
            if ($null -ne $oldRange) {
                [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($oldRange)
            }
            if ($null -ne $oldShape) {
                [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($oldShape)
            }
        }
    }

    $captionMatches = @()
    for ($paragraphIndex = 1; $paragraphIndex -le $document.Paragraphs.Count; $paragraphIndex++) {
        $paragraph = $document.Paragraphs.Item($paragraphIndex)
        try {
            $paragraphText = $paragraph.Range.Text.TrimEnd([char]13, [char]7)
            if ($paragraphText -eq [string]$plan.replacements[0].caption_before) {
                $captionMatches += $paragraphIndex
            }
        }
        finally {
            [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($paragraph)
        }
    }
    if ($captionMatches.Count -ne 1) {
        throw "Expected one exact Figure 1 caption, found $($captionMatches.Count)."
    }
    $captionParagraph = $document.Paragraphs.Item($captionMatches[0])
    $captionRange = $null
    try {
        $captionRange = $captionParagraph.Range.Duplicate
        $captionRange.MoveEnd(1, -1) | Out-Null
        $captionRange.Text = [string]$plan.replacements[0].caption_after
    }
    finally {
        if ($null -ne $captionRange) {
            [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($captionRange)
        }
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($captionParagraph)
    }

    for ($index = 1; $index -le $document.Fields.Count; $index++) {
        $field = $document.Fields.Item($index)
        try {
            [void]$field.Update()
        }
        finally {
            [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($field)
        }
    }
    if ($document.TablesOfContents.Count -ne 0) {
        throw 'The controlled source uses a static TOC list; an unexpected native TOC was found.'
    }
    $document.Repaginate()

    if ($document.InlineShapes.Count -ne 10) {
        throw "Expected 10 integrated inline figures; found $($document.InlineShapes.Count)."
    }
    for ($index = 1; $index -le 10; $index++) {
        $shape = $document.InlineShapes.Item($index)
        try {
            $expectedWidthPoints = [double]$plan.replacements[$index - 1].width_emu / 12700.0
            if ([Math]::Abs([double]$shape.Width - $expectedWidthPoints) -gt 0.5) {
                throw "Integrated width drift at Figure $index."
            }
            if ([string]$shape.AlternativeText -ne [string]$plan.replacements[$index - 1].alt_text) {
                throw "Integrated alt text drift at Figure $index."
            }
        }
        finally {
            [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($shape)
        }
    }

    $expectedCaptions = @($plan.replacements | ForEach-Object { [string]$_.caption_after })
    $captionPositions = @()
    for ($index = 1; $index -le 10; $index++) {
        $matches = @()
        for ($paragraphIndex = 1; $paragraphIndex -le $document.Paragraphs.Count; $paragraphIndex++) {
            $paragraph = $document.Paragraphs.Item($paragraphIndex)
            try {
                $paragraphText = $paragraph.Range.Text.TrimEnd([char]13, [char]7)
                if ($paragraphText -eq $expectedCaptions[$index - 1]) {
                    $matches += [pscustomobject]@{
                        paragraph_index = $paragraphIndex
                        range_start = [int]$paragraph.Range.Start
                    }
                }
            }
            finally {
                [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($paragraph)
            }
        }
        if ($matches.Count -ne 1) {
            throw "Expected one exact integrated caption for Figure $index; found $($matches.Count)."
        }
        $shape = $document.InlineShapes.Item($index)
        try {
            if ([int]$shape.Range.Start -ge [int]$matches[0].range_start) {
                throw "Integrated Figure $index does not precede its caption."
            }
        }
        finally {
            [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($shape)
        }
        $captionPositions += [int]$matches[0].range_start
    }
    for ($index = 1; $index -lt $captionPositions.Count; $index++) {
        if ($captionPositions[$index] -le $captionPositions[$index - 1]) {
            throw 'Integrated figure captions are not in Figure 1 through Figure 10 order.'
        }
    }
    $WordIntegratedPages = [int]$document.ComputeStatistics(2)
    if ($WordIntegratedPages -ne $WordBaselinePages) {
        throw (
            "Integration changed Word pagination from its $WordBaselinePages-page baseline " +
            "to $WordIntegratedPages pages."
        )
    }
    if ($document.Content.Text -match 'Error! Reference source not found\.') {
        throw 'Word reports a dangling cross-reference after field updates.'
    }

    $document.Save()
    $document.Close($false)
    [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
    $document = $null
    $word.Quit()
    [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    $word = $null

    $layoutMaterialization = Invoke-DocxLayoutMaterializer -Docx $derivedDocx
    Write-Verbose (
        "Materialized keep-lines layout control in {0}; output SHA-256 {1}." -f
        $layoutMaterialization.docx,
        $layoutMaterialization.sha256_after
    )

    $pdfPublished = $false
    try {
        Invoke-ProposalLibreOfficePdfExport `
            -Executable $libreOfficePath `
            -SourceDocx $derivedDocx `
            -DestinationPdf $derivedPdf `
            -ProfileRoot $profileRoot `
            -TimeoutSeconds $LibreOfficeExportTimeoutSeconds `
            -Published ([ref]$pdfPublished)
    }
    finally {
        if ($pdfPublished) { $createdDerivedPdf = $true }
    }
    $finalSourceHash = Get-SharedSha256 -LiteralPath $sourcePath
    if ($finalSourceHash -ne $expectedHash) {
        throw "The original source changed during integration: observed $finalSourceHash."
    }

    $receiptJson = Invoke-PostIntegrationVerifier `
        -Source $sourcePath `
        -Figures $figurePath `
        -Content $contentPath `
        -Qa $qaPath `
        -Output $outputPath `
        -Receipt $integrationReceiptPath `
        -SourceSha256 $expectedHash `
        -RendererManifestPath $rendererManifestPath `
        -RendererRuntimeRoot $rendererRuntimeRoot `
        -RendererProfilePath $profileRegistryPath `
        -RendererVersion $LibreOfficeVersionOutput `
        -RendererWorkspace $rendererWorkspacePath `
        -BaselinePages $WordBaselinePages `
        -IntegratedPages $WordIntegratedPages
    $createdIntegrationReceipt = $true
    $integrationSucceeded = $true
}
finally {
    $cleanupFailures = @()
    if ($null -ne $document) {
        try {
            $document.Close($false)
        }
        catch {
            $cleanupFailures += "Word document close failed: $($_.Exception.Message)"
        }
        finally {
            try {
                [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
            }
            catch {
                $cleanupFailures += "Word document COM release failed: $($_.Exception.Message)"
            }
        }
    }
    if ($null -ne $word) {
        try {
            $word.Quit()
        }
        catch {
            $cleanupFailures += "Word application quit failed: $($_.Exception.Message)"
        }
        finally {
            try {
                [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
            }
            catch {
                $cleanupFailures += "Word application COM release failed: $($_.Exception.Message)"
            }
        }
    }
    if (-not $integrationSucceeded) {
        $ownedCleanupTargets = @()
        if ($createdIntegrationReceipt) { $ownedCleanupTargets += $integrationReceiptPath }
        if ($createdDerivedPdf) { $ownedCleanupTargets += $derivedPdf }
        if ($createdDerivedDocx) { $ownedCleanupTargets += $derivedDocx }
        foreach ($cleanupTarget in $ownedCleanupTargets) {
            try {
                Remove-DerivedFile -LiteralPath $cleanupTarget
            }
            catch {
                $cleanupFailures += "Failed to remove derived artifact $cleanupTarget`: $($_.Exception.Message)"
            }
        }
    }
    if (Test-Path -LiteralPath $profileRoot -PathType Container) {
        try {
            $resolvedProfileRoot = [System.IO.Path]::GetFullPath($profileRoot)
            $profileParent = [System.IO.Path]::GetFullPath((Join-Path $projectRoot '.cache'))
            $safeProfileLeaf = [System.IO.Path]::GetFileName($resolvedProfileRoot).StartsWith(
                'proposal-integration-profile-',
                [System.StringComparison]::Ordinal
            )
            $profilePrefix = $profileParent.TrimEnd([System.IO.Path]::DirectorySeparatorChar) +
                [System.IO.Path]::DirectorySeparatorChar
            if (
                -not $resolvedProfileRoot.StartsWith(
                    $profilePrefix,
                    [System.StringComparison]::OrdinalIgnoreCase
                ) -or
                -not $safeProfileLeaf
            ) {
                throw "Unsafe LibreOffice profile cleanup target: $resolvedProfileRoot"
            }
            Remove-Item -LiteralPath $resolvedProfileRoot -Recurse -Force
        }
        catch {
            $cleanupFailures += "LibreOffice profile cleanup failed: $($_.Exception.Message)"
        }
    }
    if ($cleanupFailures.Count -gt 0) {
        $cleanupMessage = $cleanupFailures -join [System.Environment]::NewLine
        if ($integrationSucceeded) {
            throw "Controlled Word cleanup failed: $cleanupMessage"
        }
        Write-Error -ErrorAction Continue "Controlled failure cleanup reported: $cleanupMessage"
    }
}

[Console]::Out.Write($receiptJson)
