$ErrorActionPreference = 'Stop'
$statePath = Join-Path $PSScriptRoot 'state.json'
if (-not (Test-Path -LiteralPath $statePath)) { Write-Output 'Not started'; exit 0 }
$state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
$pythonPath = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'python-path.txt') -Raw).Trim()
$entryPath = Join-Path $PSScriptRoot 'runtime.py'
$runner = Get-CimInstance Win32_Process -Filter ('ProcessId = ' + [int]$state.runner_pid)
# Match this launcher's complete command, not merely a reused Python PID.
$pythonPattern = [regex]::Escape($pythonPath)
$entryPattern = [regex]::Escape($entryPath)
$expectedCommand = '^\s*(?:"' + $pythonPattern + '"|' + $pythonPattern + ')\s+-X\s+utf8\s+-B\s+(?:"' + $entryPattern + '"|' + $entryPattern + ')\s*$'
$ownRunner = $runner -and $runner.ExecutablePath -eq $pythonPath -and $runner.CommandLine -match $expectedCommand
if (-not $ownRunner) {
    $vm = Get-Process -Id ([int]$state.pid) -ErrorAction SilentlyContinue
    if ($vm -and $vm.Path -eq (Join-Path $PSScriptRoot 'qemu\qemu-system-x86_64.exe')) {
        Write-Error 'orphan_vm: Android is still running, but its verified controller is unavailable. No process was terminated.' -ErrorAction Continue
        exit 2
    }
    Write-Output 'Not running'
    exit 0
}
[System.IO.File]::WriteAllText((Join-Path $PSScriptRoot 'stop.request'), [DateTimeOffset]::Now.ToString('o'))
Write-Output 'Graceful shutdown requested. Check Status.ps1.'
