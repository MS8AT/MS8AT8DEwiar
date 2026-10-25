$ErrorActionPreference = 'Stop'
$statePath = Join-Path $PSScriptRoot 'state.json'
$state = if (Test-Path -LiteralPath $statePath) { Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json } else { $null }
$vm = if ($state) { Get-Process -Id $state.pid -ErrorAction SilentlyContinue } else { $null }
$expectedPath = Join-Path $PSScriptRoot 'qemu\qemu-system-x86_64.exe'
if (-not $vm -or $vm.Path -ne $expectedPath) {
    & (Join-Path $PSScriptRoot 'Start.ps1') | Out-Null
    exit 0
}

# Use QEMU's native screen: this Android build has no working MediaCodec capture.
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class AndroidWindow {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr window, int command);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr window);
}
'@
$vm.Refresh()
if ($vm.MainWindowHandle -ne [IntPtr]::Zero) {
    [AndroidWindow]::ShowWindow($vm.MainWindowHandle, 9) | Out-Null
    [AndroidWindow]::SetForegroundWindow($vm.MainWindowHandle) | Out-Null
}
if ($state.phase -ne 'ready') { exit 0 }
$adbPath = Join-Path $PSScriptRoot 'platform-tools\adb.exe'
$serial = [string]$state.adb_serial
if ($serial -notmatch '^127\.0\.0\.1:\d+$') { throw 'Expected an explicit local test device.' }
& $adbPath connect $serial | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'ADB connection failed.' }
$deviceState = & $adbPath -s $serial get-state
if ($LASTEXITCODE -ne 0 -or $deviceState.Trim() -ne 'device') { throw 'The selected Android VM is not ready for control.' }
& $adbPath -s $serial shell am start --user 0 -W -n pro.dewiar.app/.MainActivity | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Dewiar could not be opened.' }
