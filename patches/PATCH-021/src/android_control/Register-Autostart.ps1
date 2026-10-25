$ErrorActionPreference = 'Stop'
$runtimeRoot = $PSScriptRoot
$startupDir = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startupDir 'MS8AT Dewiar Android.lnk'
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$powershell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + (Join-Path $runtimeRoot 'Start.ps1') + '"'
if ((Test-Path -LiteralPath $shortcutPath) -and ($shortcut.TargetPath -ne $powershell -or $shortcut.Arguments -ne $arguments)) { throw 'An unrelated shortcut already has this name.' }
$shortcut.TargetPath = $powershell
$shortcut.Arguments = $arguments
$shortcut.WorkingDirectory = $runtimeRoot
$shortcut.WindowStyle = 7
$shortcut.Description = 'Start the verified local 8 GiB Android test VM after Windows sign-in.'
$shortcut.Save()
$readback = $shell.CreateShortcut($shortcutPath)
if ($readback.TargetPath -ne $powershell -or $readback.Arguments -ne $arguments) { throw 'Startup shortcut readback failed.' }
$desktopPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'MS8AT Android - Dewiar.lnk'
if (-not (Test-Path -LiteralPath $desktopPath)) {
    $openShortcut = $shell.CreateShortcut($desktopPath)
    $openShortcut.TargetPath = $powershell
    $openShortcut.Arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + (Join-Path $runtimeRoot 'Open.ps1') + '"'
    $openShortcut.WorkingDirectory = $runtimeRoot
    $openShortcut.Save()
}
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class PackageState { [DllImport("kernel32.dll", CharSet=CharSet.Unicode)] public static extern int GetCurrentPackageFullName(ref uint length, System.Text.StringBuilder name); }'
$stopPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'MS8AT Android - Stop.lnk'
$stopArguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + (Join-Path $runtimeRoot 'Stop.ps1') + '"'
$stopShortcut = $shell.CreateShortcut($stopPath)
if ((Test-Path -LiteralPath $stopPath) -and ($stopShortcut.TargetPath -ne $powershell -or $stopShortcut.Arguments -ne $stopArguments)) { throw 'An unrelated stop shortcut already has this name.' }
$stopShortcut.TargetPath = $powershell
$stopShortcut.Arguments = $stopArguments
$stopShortcut.WorkingDirectory = $runtimeRoot
$stopShortcut.Description = 'Save Android data and shut down this local VM.'
$stopShortcut.Save()
$length = [uint32]0
$packageResult = [PackageState]::GetCurrentPackageFullName([ref]$length, $null)
$receipt = [ordered]@{registeredAt=[DateTimeOffset]::Now.ToString('o');startup=$shortcutPath;desktop=$desktopPath;target=$readback.TargetPath;arguments=$readback.Arguments;packageApiResult=$packageResult;runtimeRoot=$runtimeRoot;user=[Environment]::UserName}
$receipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runtimeRoot 'autostart-receipt.json') -Encoding UTF8
