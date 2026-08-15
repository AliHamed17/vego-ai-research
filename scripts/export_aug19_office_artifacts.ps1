param(
    [Parameter(Mandatory = $true)] [string]$PackageDirectory,
    [Parameter(Mandatory = $true)] [string]$BuildWorkDirectory,
    [Parameter(Mandatory = $true)] [string]$ReceiptPath,
    [ValidateRange(30, 600)] [int]$TimeoutSeconds = 120,
    [ValidateRange(1, 2)] [int]$MaxAttempts = 2
)

$ErrorActionPreference = 'Stop'

function Assert-ChildPath {
    param([string]$Parent, [string]$Child)
    $parentFull = [System.IO.Path]::GetFullPath($Parent).TrimEnd('\') + '\'
    $childFull = [System.IO.Path]::GetFullPath($Child)
    if (-not $childFull.StartsWith($parentFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Unsafe path outside build work directory: $childFull"
    }
    return $childFull
}

function Stop-ScopedAutomationProcess {
    param(
        [string]$PidFile,
        [string]$ExpectedProcessName,
        [int[]]$BaselinePids
    )
    if (-not (Test-Path -LiteralPath $PidFile -PathType Leaf)) { return }
    $record = Get-Content -Raw -LiteralPath $PidFile | ConvertFrom-Json
    $automationPid = [int]$record.process_id
    if ($BaselinePids -contains $automationPid) {
        throw "Refusing to stop baseline Office PID $automationPid"
    }
    $process = Get-Process -Id $automationPid -ErrorAction SilentlyContinue
    if ($null -ne $process) {
        if ($process.ProcessName -ine $ExpectedProcessName) {
            throw "PID $automationPid is $($process.ProcessName), not $ExpectedProcessName"
        }
        Stop-Process -Id $automationPid -Force -ErrorAction Stop
        $process.WaitForExit(10000)
    }
}

function ConvertTo-ProcessArgument {
    param([string]$Value)
    if ($Value -notmatch '[\s"]') { return $Value }
    return '"' + ($Value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
}

$packagePath = [System.IO.Path]::GetFullPath($PackageDirectory)
$workPath = [System.IO.Path]::GetFullPath($BuildWorkDirectory)
$receiptFullPath = [System.IO.Path]::GetFullPath($ReceiptPath)
$workerPath = Join-Path $PSScriptRoot 'export_aug19_office_worker.ps1'

foreach ($requiredDirectory in @($packagePath, $workPath)) {
    if (-not (Test-Path -LiteralPath $requiredDirectory -PathType Container)) {
        throw "Required directory does not exist: $requiredDirectory"
    }
}
if (-not (Test-Path -LiteralPath $workerPath -PathType Leaf)) {
    throw "Office worker is missing: $workerPath"
}

$jobs = @(
    [ordered]@{ Mode='Word'; Source=(Join-Path $packagePath 'Chapter_2_Literature_Review_EN.docx'); Target=(Join-Path $packagePath 'Chapter_2_Literature_Review_EN.pdf'); Process='WINWORD' },
    [ordered]@{ Mode='Word'; Source=(Join-Path $packagePath 'Chapter_2_Literature_Review_HE.docx'); Target=(Join-Path $packagePath 'Chapter_2_Literature_Review_HE.pdf'); Process='WINWORD' },
    [ordered]@{ Mode='Word'; Source=(Join-Path $workPath 'Supervisor_PreRead_EN.docx'); Target=(Join-Path $packagePath 'Supervisor_PreRead_EN.pdf'); Process='WINWORD' },
    [ordered]@{ Mode='Word'; Source=(Join-Path $workPath 'Supervisor_PreRead_HE.docx'); Target=(Join-Path $packagePath 'Supervisor_PreRead_HE.pdf'); Process='WINWORD' },
    [ordered]@{ Mode='Word'; Source=(Join-Path $workPath 'Supervisor_Tracker_and_Decisions_Bilingual.docx'); Target=(Join-Path $packagePath 'Supervisor_Tracker_and_Decisions_Bilingual.pdf'); Process='WINWORD' }
)

foreach ($job in $jobs) {
    if (-not (Test-Path -LiteralPath $job.Source -PathType Leaf)) {
        throw "Office source missing: $($job.Source)"
    }
}

$baselinePids = @(
    Get-Process -Name 'WINWORD' -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty Id
)
$runRoot = Assert-ChildPath $workPath (Join-Path $workPath ("office-export-" + $PID + '-' + [guid]::NewGuid().ToString('N')))
New-Item -ItemType Directory -Path $runRoot | Out-Null
$rows = @()
$staged = @()
$powershellExe = (Get-Process -Id $PID).Path
if (-not (Test-Path -LiteralPath $powershellExe -PathType Leaf)) {
    throw "Current PowerShell host executable is unavailable: $powershellExe"
}

try {
    foreach ($job in $jobs) {
        $safeName = ([System.IO.Path]::GetFileNameWithoutExtension($job.Target) -replace '[^A-Za-z0-9_-]', '_')
        $success = $false
        $attemptRows = @()
        for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
            $attemptRoot = Assert-ChildPath $runRoot (Join-Path $runRoot ("$safeName-attempt-$attempt"))
            New-Item -ItemType Directory -Path $attemptRoot | Out-Null
            $tempTarget = Join-Path $attemptRoot ([System.IO.Path]::GetFileName($job.Target))
            $workerReceipt = Join-Path $attemptRoot 'worker-receipt.json'
            $automationPidPath = Join-Path $attemptRoot 'automation-pid.json'
            $stdoutPath = Join-Path $attemptRoot 'stdout.log'
            $stderrPath = Join-Path $attemptRoot 'stderr.log'
            $arguments = @(
                '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
                '-File', $workerPath,
                '-Mode', $job.Mode,
                '-SourcePath', $job.Source,
                '-TempTargetPath', $tempTarget,
                '-ReceiptPath', $workerReceipt,
                '-AutomationPidPath', $automationPidPath
            )
            $argumentLine = ($arguments | ForEach-Object { ConvertTo-ProcessArgument ([string]$_) }) -join ' '
            $process = Start-Process -FilePath $powershellExe -ArgumentList $argumentLine `
                -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdoutPath `
                -RedirectStandardError $stderrPath
            $completed = $process.WaitForExit($TimeoutSeconds * 1000)
            if (-not $completed) {
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                $process.WaitForExit(10000)
                Stop-ScopedAutomationProcess -PidFile $automationPidPath `
                    -ExpectedProcessName $job.Process -BaselinePids $baselinePids
                $attemptRows += [ordered]@{
                    attempt=$attempt
                    outcome='Timeout'
                    worker_exit=$null
                    stderr=if (Test-Path -LiteralPath $stderrPath) { Get-Content -Raw -LiteralPath $stderrPath } else { '' }
                }
                continue
            }
            Stop-ScopedAutomationProcess -PidFile $automationPidPath `
                -ExpectedProcessName $job.Process -BaselinePids $baselinePids
            if ($process.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $tempTarget -PathType Leaf)) {
                $attemptRows += [ordered]@{
                    attempt=$attempt
                    outcome='Failed'
                    worker_exit=$process.ExitCode
                    stderr=if (Test-Path -LiteralPath $stderrPath) { Get-Content -Raw -LiteralPath $stderrPath } else { '' }
                }
                continue
            }
            if ((Get-Item -LiteralPath $tempTarget).Length -le 0) {
                $attemptRows += [ordered]@{ attempt=$attempt; outcome='Empty output'; worker_exit=$process.ExitCode }
                continue
            }
            if (-not (Test-Path -LiteralPath $workerReceipt -PathType Leaf)) {
                $attemptRows += [ordered]@{ attempt=$attempt; outcome='Missing receipt'; worker_exit=$process.ExitCode }
                continue
            }

            $attemptRows += [ordered]@{ attempt=$attempt; outcome='Succeeded'; worker_exit=$process.ExitCode }
            $workerResult = Get-Content -Raw -LiteralPath $workerReceipt | ConvertFrom-Json
            $staged += [ordered]@{
                temporary = $tempTarget
                target = $job.Target
                backup = Join-Path $runRoot ("backup-" + [System.IO.Path]::GetFileName($job.Target))
            }
            $rows += [ordered]@{
                mode = $job.Mode
                source = [System.IO.Path]::GetFileName($job.Source)
                target = [System.IO.Path]::GetFileName($job.Target)
                attempts = $attemptRows
                automation_process = $job.Process
                office_version = [string]$workerResult.office_version
                pages_or_slides = [int]$workerResult.pages_or_slides
                printer = [string]$workerResult.printer
                update_fields_at_print = [bool]$workerResult.update_fields_at_print
            }
            $success = $true
            break
        }
        if (-not $success) {
            [ordered]@{
                schema_version='vego-ai.office-export-failure.v1'
                mode=$job.Mode
                source=[System.IO.Path]::GetFileName($job.Source)
                target=[System.IO.Path]::GetFileName($job.Target)
                attempts=$attemptRows
            } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath `
                (Join-Path $workPath 'office-export-last-failure.json') -Encoding utf8
            throw "Office export failed after $MaxAttempts attempts: $($job.Source)"
        }
    }

    $promoted = @()
    try {
        foreach ($item in $staged) {
            if (Test-Path -LiteralPath $item.target -PathType Leaf) {
                [System.IO.File]::Replace($item.temporary, $item.target, $item.backup, $true)
                $promoted += [ordered]@{ target=$item.target; backup=$item.backup; existed=$true }
            }
            else {
                [System.IO.File]::Move($item.temporary, $item.target)
                $promoted += [ordered]@{ target=$item.target; backup=$null; existed=$false }
            }
        }
    }
    catch {
        foreach ($item in @($promoted | Select-Object -Reverse)) {
            if ($item.existed -and (Test-Path -LiteralPath $item.backup -PathType Leaf)) {
                [System.IO.File]::Replace($item.backup, $item.target, $null, $true)
            }
            elseif (-not $item.existed -and (Test-Path -LiteralPath $item.target -PathType Leaf)) {
                [System.IO.File]::Delete($item.target)
            }
        }
        throw
    }
    foreach ($item in $promoted) {
        if ($item.existed -and (Test-Path -LiteralPath $item.backup -PathType Leaf)) {
            [System.IO.File]::Delete($item.backup)
        }
    }

    $combinedReceipt = [ordered]@{
        schema_version = 'vego-ai.office-export-receipt.v2'
        timeout_seconds = $TimeoutSeconds
        max_attempts = $MaxAttempts
        atomic_batch_promote = $true
        exact_pid_cleanup_only = $true
        exports = $rows
    }
    $receiptDirectory = Split-Path -Parent $receiptFullPath
    if (-not (Test-Path -LiteralPath $receiptDirectory)) {
        New-Item -ItemType Directory -Path $receiptDirectory | Out-Null
    }
    $combinedReceipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receiptFullPath -Encoding utf8
}
finally {
    if (Test-Path -LiteralPath $runRoot -PathType Container) {
        $verifiedRunRoot = Assert-ChildPath $workPath $runRoot
        Remove-Item -LiteralPath $verifiedRunRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}
