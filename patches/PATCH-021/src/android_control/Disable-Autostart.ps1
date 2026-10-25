$ErrorActionPreference = 'Stop'
$shortcutPath = Join-Path ([Environment]::GetFolderPath('Startup')) 'MS8AT Dewiar Android.lnk'
if (-not (Test-Path -LiteralPath $shortcutPath)) { Write-Output 'Autostart is already disabled.'; exit 0 }
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$expected = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + (Join-Path $PSScriptRoot 'Start.ps1') + '"'
if ($shortcut.Arguments -ne $expected) { throw 'Shortcut belongs to another configuration.' }
Remove-Item -LiteralPath $shortcutPath
Write-Output 'Autostart disabled. The data disk and current VM are preserved.'
