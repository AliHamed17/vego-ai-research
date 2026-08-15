param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Word')]
    [string]$Mode,
    [Parameter(Mandatory = $true)] [string]$SourcePath,
    [Parameter(Mandatory = $true)] [string]$TempTargetPath,
    [Parameter(Mandatory = $true)] [string]$ReceiptPath,
    [Parameter(Mandatory = $true)] [string]$AutomationPidPath
)

$ErrorActionPreference = 'Stop'

Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class WindowProcessLookup {
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
}
'@

function Resolve-AutomationPid {
    param(
        [int]$Hwnd,
        [string]$ProcessName,
        [int[]]$BaselinePids
    )
    [uint32]$processId = 0
    if ($Hwnd -gt 0) {
        [void][WindowProcessLookup]::GetWindowThreadProcessId([IntPtr]$Hwnd, [ref]$processId)
    }
    if ($processId -gt 0 -and -not ($BaselinePids -contains [int]$processId)) {
        return [int]$processId
    }
    for ($poll = 0; $poll -lt 20; $poll++) {
        $newPids = @(
            Get-Process -Name $ProcessName -ErrorAction SilentlyContinue |
                Where-Object { $BaselinePids -notcontains $_.Id } |
                Select-Object -ExpandProperty Id
        )
        if ($newPids.Count -eq 1) { return [int]$newPids[0] }
        if ($newPids.Count -gt 1) {
            throw "Unable to identify exactly one new $ProcessName automation PID"
        }
        Start-Sleep -Milliseconds 250
    }
    throw "Unable to identify exactly one new $ProcessName automation PID"
}

function Write-AutomationPid {
    param([int]$Hwnd, [string]$ProcessName, [int[]]$BaselinePids)
    $processId = Resolve-AutomationPid -Hwnd $Hwnd -ProcessName $ProcessName -BaselinePids $BaselinePids
    [ordered]@{ process_id=[int]$processId; process_name=$ProcessName; hwnd=$Hwnd } |
        ConvertTo-Json | Set-Content -LiteralPath $AutomationPidPath -Encoding utf8
}

$sourceFull = [System.IO.Path]::GetFullPath($SourcePath)
$targetFull = [System.IO.Path]::GetFullPath($TempTargetPath)
if (-not (Test-Path -LiteralPath $sourceFull -PathType Leaf)) {
    throw "Source is missing: $sourceFull"
}
if (Test-Path -LiteralPath $targetFull) {
    [System.IO.File]::Delete($targetFull)
}

$receipt = [ordered]@{
    schema_version = 'vego-ai.office-export-worker.v2'
    mode = $Mode
    source = [System.IO.Path]::GetFileName($sourceFull)
    target = [System.IO.Path]::GetFileName($targetFull)
    office_version = ''
    pages_or_slides = 0
    printer = 'Not applicable'
    update_fields_at_print = $false
}

$officeBaselinePids = @(Get-Process -Name 'WINWORD' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    Write-AutomationPid -Hwnd ([int]$word.Hwnd) -ProcessName 'WINWORD' -BaselinePids $officeBaselinePids
    $word.Options.UpdateFieldsAtPrint = $false
    $word.Options.PrintBackground = $false
    $word.ActivePrinter = 'Microsoft Print to PDF'
    $receipt.office_version = [string]$word.Version
    $receipt.printer = [string]$word.ActivePrinter
    $receipt.update_fields_at_print = [bool]$word.Options.UpdateFieldsAtPrint
    $document = $word.Documents.Open($sourceFull, $false, $true, $false)
    $receipt.pages_or_slides = [int]$document.ComputeStatistics(2)
    $document.ExportAsFixedFormat($targetFull, 17)
}
finally {
    if ($null -ne $document) {
        $document.Close($false)
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
    }
    if ($null -ne $word) {
        $word.Quit()
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
}

if (-not (Test-Path -LiteralPath $targetFull -PathType Leaf) -or (Get-Item -LiteralPath $targetFull).Length -le 0) {
    throw "Office export produced no usable file: $targetFull"
}
$receipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ReceiptPath -Encoding utf8
