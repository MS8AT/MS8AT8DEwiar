$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class AndroidPlacement {
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hwnd, IntPtr after, int x, int y, int width, int height, uint flags);
}
'@
$state = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'state.json') -Raw | ConvertFrom-Json
$size = '960x600'
$configPath = Join-Path $PSScriptRoot 'control-settings.json'
if(Test-Path -LiteralPath $configPath) { $size = (Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json).size }
if($size -notin @('800x500','960x600','1280x800')) { throw 'Unsupported window size' }
$dimensions = $size.Split('x')
$area = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$width = [Math]::Min([int]$dimensions[0], $area.Width - 40)
$height = [Math]::Min([int]$dimensions[1] + 32, $area.Height - 40)
for($attempt=0; $attempt -lt 40; $attempt++) {
    $vm = Get-Process -Id $state.pid -ErrorAction SilentlyContinue
    if(-not $vm -or $vm.Path -ne (Join-Path $PSScriptRoot 'qemu\qemu-system-x86_64.exe')) { exit 0 }
    if($vm.MainWindowHandle -ne [IntPtr]::Zero) {
        [AndroidPlacement]::SetWindowPos($vm.MainWindowHandle, [IntPtr]::Zero, ($area.Right-$width-20), ($area.Top+20), $width, $height, 0x14) | Out-Null
        exit 0
    }
    Start-Sleep -Milliseconds 200
}
