param(
    [ValidateSet('status','capabilities','logs','start','stop','open','screen','lock','autostart','vpn','vpn-status')][string]$Action = 'status',
    [ValidateSet('800x500','960x600','1280x800')][string]$Size,
    [ValidateSet('true','false')][string]$Enabled,
    [string]$TargetHost = '127.0.0.1'
)
$pythonPath = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'python-path.txt') -Raw).Trim()
$parameters = @('-X','utf8','-B',(Join-Path $PSScriptRoot 'control_cli.py'),$Action,'--host',$TargetHost)
if($Size) { $parameters += @('--size',$Size) }
if($Enabled) { $parameters += @('--enabled',$Enabled) }
& $pythonPath @parameters
exit $LASTEXITCODE
