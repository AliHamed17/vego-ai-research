# Convert .docx / .pptx in a folder to PDF using the installed Office applications.
# Word/PowerPoint COM is used because neither pandoc nor LibreOffice is available on this machine.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Folder,
    [string]$Filter = "*"
)

$ErrorActionPreference = "Stop"
$folder = (Resolve-Path -LiteralPath $Folder).Path
$wdFormatPDF = 17
$ppSaveAsPDF = 32

$docs = @(Get-ChildItem -LiteralPath $folder -Filter "$Filter.docx" -File | Where-Object { $_.Name -notlike '~$*' })
$ppts = @(Get-ChildItem -LiteralPath $folder -Filter "$Filter.pptx" -File | Where-Object { $_.Name -notlike '~$*' })

if ($docs.Count -gt 0) {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    try {
        foreach ($d in $docs) {
            $pdf = [System.IO.Path]::ChangeExtension($d.FullName, ".pdf")
            $doc = $word.Documents.Open($d.FullName, $false, $true)
            try {
                $doc.SaveAs([ref]$pdf, [ref]$wdFormatPDF)
                Write-Host "pdf <- $($d.Name)"
            } finally { $doc.Close($false) }
        }
    } finally {
        $word.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    }
}

if ($ppts.Count -gt 0) {
    $pp = New-Object -ComObject PowerPoint.Application
    try {
        foreach ($p in $ppts) {
            $pdf = [System.IO.Path]::ChangeExtension($p.FullName, ".pdf")
            $pres = $pp.Presentations.Open($p.FullName, $true, $false, $false)
            try {
                $pres.SaveAs($pdf, $ppSaveAsPDF)
                Write-Host "pdf <- $($p.Name)"
            } finally { $pres.Close() }
        }
    } finally {
        $pp.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pp) | Out-Null
    }
}

Write-Host "converted: $($docs.Count) docx, $($ppts.Count) pptx"
