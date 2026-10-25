$ErrorActionPreference = 'Stop'
$statePath = Join-Path $PSScriptRoot 'state.json'
if (-not (Test-Path -LiteralPath $statePath)) { @{status='NOT_STARTED'} | ConvertTo-Json; exit 0 }
$state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
$vm = Get-Process -Id $state.pid -ErrorAction SilentlyContinue
$runner = Get-Process -Id $state.runner_pid -ErrorAction SilentlyContinue
$pythonPath = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'python-path.txt') -Raw).Trim()
$running = [bool]($vm -and $vm.Path -eq (Join-Path $PSScriptRoot 'qemu\qemu-system-x86_64.exe') -and $runner -and $runner.Path -eq $pythonPath)
[pscustomobject]@{status=$(if ($running) {$state.status} else {'STOPPED'});phase=$(if ($running) {$state.phase} else {'stopped'});ramMiB=$state.ram_mib;androidBoot=($running -and $state.android_boot_completed);appAlive=($running -and $state.app_process_alive);health=$(if ($running) {$state.health} else {'STOPPED'});vmRunning=$running;vmPid=$state.pid;logs=$state.run_dir;updated=$state.updated_at} | ConvertTo-Json
