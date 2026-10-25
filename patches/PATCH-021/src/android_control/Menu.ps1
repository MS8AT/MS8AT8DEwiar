$ErrorActionPreference = 'Stop'
$created = $false
$mutex = New-Object System.Threading.Mutex($true, 'Local\MS8AT.DewiarAndroid.Menu', [ref]$created)
if(-not $created) { $mutex.Dispose(); exit 0 }
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$script:root = $PSScriptRoot
$icon = New-Object System.Windows.Forms.NotifyIcon
$icon.Icon = [System.Drawing.SystemIcons]::Application
$icon.Text = 'MS8AT Android - Dewiar'
$menu = New-Object System.Windows.Forms.ContextMenuStrip
$script:command = $null

function Invoke-Control([string[]]$arguments) {
    if ($script:command) {
        $icon.ShowBalloonTip(4000, 'MS8AT Android', 'Предыдущая команда ещё выполняется.', [System.Windows.Forms.ToolTipIcon]::Info)
        return
    }
    $process = New-Object System.Diagnostics.Process
    try {
        $process.StartInfo.FileName = (Get-Content -LiteralPath (Join-Path $script:root 'python-path.txt') -Raw).Trim()
        $process.StartInfo.Arguments = '-X utf8 -B "' + (Join-Path $script:root 'control_cli.py') + '" ' + ($arguments -join ' ')
        $process.StartInfo.WorkingDirectory = $script:root
        $process.StartInfo.UseShellExecute = $false
        $process.StartInfo.CreateNoWindow = $true
        $process.StartInfo.RedirectStandardOutput = $true
        $process.StartInfo.RedirectStandardError = $true
        $process.StartInfo.StandardOutputEncoding = [System.Text.Encoding]::UTF8
        $process.StartInfo.StandardErrorEncoding = [System.Text.Encoding]::UTF8
        [void]$process.Start()
        $script:command = [pscustomobject]@{
            Process = $process
            Output = New-ControlReader $process.StandardOutput
            Error = New-ControlReader $process.StandardError
        }
    }
    catch {
        $process.Dispose()
        $icon.ShowBalloonTip(6000, 'MS8AT Android', 'Не удалось запустить команду. Проверьте установку CLI.', [System.Windows.Forms.ToolTipIcon]::Error)
    }
}
function New-ControlReader($reader) {
    $buffer = New-Object char[] 1024
    [pscustomobject]@{ Reader=$reader; Buffer=$buffer; Task=$reader.ReadAsync($buffer, 0, $buffer.Length); Text=(New-Object System.Text.StringBuilder); Done=$false }
}
function Read-ControlOutput($stream) {
    # Drain both pipes asynchronously; retain at most 4096 characters per pipe.
    for ($i=0; $i -lt 4 -and -not $stream.Done -and $stream.Task.IsCompleted; $i++) {
        if ($stream.Task.IsFaulted -or $stream.Task.IsCanceled) { $stream.Done=$true; break }
        $count = $stream.Task.Result
        if ($count -eq 0) { $stream.Done=$true; break }
        $keep = [Math]::Min($count, 4096 - $stream.Text.Length)
        if ($keep -gt 0) { [void]$stream.Text.Append($stream.Buffer, 0, $keep) }
        $stream.Task = $stream.Reader.ReadAsync($stream.Buffer, 0, $stream.Buffer.Length)
    }
}
function Add-Choice([string]$label, [string[]]$arguments) {
    $item = New-Object System.Windows.Forms.ToolStripMenuItem($label)
    $item.Tag = $arguments
    $item.Add_Click({ param($sender,$event) Invoke-Control $sender.Tag })
    [void]$menu.Items.Add($item)
}
Add-Choice 'Открыть агента / Open' @('open')
Add-Choice 'Запустить Android / Start' @('start')
[void]$menu.Items.Add((New-Object System.Windows.Forms.ToolStripSeparator))
Add-Choice 'Размер: 800 x 500' @('screen','--size','800x500')
Add-Choice 'Размер: 960 x 600' @('screen','--size','960x600')
Add-Choice 'Размер: 1280 x 800' @('screen','--size','1280x800')
Add-Choice 'Отключить блокировку Android' @('lock','--enabled','false')
Add-Choice 'Включить блокировку Android' @('lock','--enabled','true')
Add-Choice 'Включить WireGuard Android' @('vpn','--enabled','true')
Add-Choice 'Отключить интернет Android' @('vpn','--enabled','false')
[void]$menu.Items.Add((New-Object System.Windows.Forms.ToolStripSeparator))
Add-Choice 'Включить автозапуск Windows' @('autostart','--enabled','true')
Add-Choice 'Отключить автозапуск Windows' @('autostart','--enabled','false')
Add-Choice 'Сохранить и остановить Android' @('stop')
$quit = New-Object System.Windows.Forms.ToolStripMenuItem('Закрыть только меню')
$quit.Add_Click({ [System.Windows.Forms.Application]::ExitThread() })
[void]$menu.Items.Add($quit)
$icon.ContextMenuStrip = $menu
$icon.Add_DoubleClick({ Invoke-Control @('open') })
$icon.Visible = $true
$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 250
$timer.Add_Tick({
    if (-not $script:command) { return }
    $current = $script:command
    Read-ControlOutput $current.Output
    Read-ControlOutput $current.Error
    if (-not $current.Process.HasExited -or -not $current.Output.Done -or -not $current.Error.Done) { return }
    $code = $current.Process.ExitCode
    $message = 'Команда выполнена.'
    $kind = [System.Windows.Forms.ToolTipIcon]::Info
    if ($code -eq 3) {
        $message = 'Команда ещё выполняется. Проверьте состояние Android; не повторяйте запуск.'
        $kind = [System.Windows.Forms.ToolTipIcon]::Warning
    }
    elseif ($code -ne 0) {
        $message = 'Команда не выполнена. Проверьте состояние контроллера Android.'
        $kind = [System.Windows.Forms.ToolTipIcon]::Error
        try {
            $result = $current.Output.Text.ToString() | ConvertFrom-Json
            # Only show a short machine code. Never display raw output or stderr.
            if ($result.error -is [string] -and $result.error -cmatch '^[a-z][a-z0-9_]{0,63}$') { $message += ' Код: ' + $result.error }
        } catch { }
    }
    $current.Process.Dispose()
    $script:command = $null
    $icon.ShowBalloonTip(6000, 'MS8AT Android', $message, $kind)
})
$timer.Start()
try { [System.Windows.Forms.Application]::Run() }
finally {
    $timer.Stop(); $timer.Dispose()
    if ($script:command) { $script:command.Process.Dispose() }
    $icon.Dispose(); $menu.Dispose(); $mutex.ReleaseMutex(); $mutex.Dispose()
}
