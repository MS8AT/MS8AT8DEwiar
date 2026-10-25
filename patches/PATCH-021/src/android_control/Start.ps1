$ErrorActionPreference = 'Stop'
$runtimeRoot = $PSScriptRoot
$pythonPath = (Get-Content -LiteralPath (Join-Path $runtimeRoot 'python-path.txt') -Raw).Trim()
if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) { throw 'Python runtime is missing.' }
$entryPath = Join-Path $runtimeRoot 'runtime.py'
$statePath = Join-Path $runtimeRoot 'state.json'
if (Test-Path -LiteralPath $statePath) {
    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    $vm = if ([int]$state.pid -gt 0) { Get-Process -Id ([int]$state.pid) -ErrorAction SilentlyContinue } else { $null }
    if ($vm -and -not $vm.Path) {
        Write-Error 'unverified_vm: Cannot verify the old VM executable. Nothing was started.' -ErrorAction Continue
        exit 2
    }
    if ($vm -and $vm.Path -eq (Join-Path $runtimeRoot 'qemu\qemu-system-x86_64.exe')) {
        $runner = if ([int]$state.runner_pid -gt 0) { Get-CimInstance Win32_Process -Filter ('ProcessId = ' + [int]$state.runner_pid) } else { $null }
        # Match the executable and complete launcher command, as in Stop.ps1.
        $pythonPattern = [regex]::Escape($pythonPath)
        $entryPattern = [regex]::Escape($entryPath)
        $expectedCommand = '^\s*(?:"' + $pythonPattern + '"|' + $pythonPattern + ')\s+-X\s+utf8\s+-B\s+(?:"' + $entryPattern + '"|' + $entryPattern + ')\s*$'
        $ownRunner = $runner -and $runner.ExecutablePath -eq $pythonPath -and $runner.CommandLine -match $expectedCommand
        if (-not $ownRunner) {
            Write-Error 'orphan_vm: Android is still running without its verified controller. Nothing was started.' -ErrorAction Continue
            exit 2
        }
    }
}
& (Join-Path $runtimeRoot 'Start-Control.ps1')
$powershell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
Start-Process -FilePath $powershell -ArgumentList @('-NoProfile','-STA','-ExecutionPolicy','Bypass','-WindowStyle','Hidden','-File',('"'+(Join-Path $runtimeRoot 'Menu.ps1')+'"')) -WorkingDirectory $runtimeRoot -WindowStyle Hidden | Out-Null
$process = Start-Process -FilePath $pythonPath -ArgumentList @('-X', 'utf8', '-B', ('"' + $entryPath + '"')) -WorkingDirectory $runtimeRoot -WindowStyle Hidden -PassThru
[pscustomobject]@{LauncherPid=$process.Id;StatusFile=(Join-Path $runtimeRoot 'state.json')}
