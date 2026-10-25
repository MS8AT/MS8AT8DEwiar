param(
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9.-]*$')][string]$TargetHost = '127.0.0.1',
    [string]$Command
)
$ErrorActionPreference = 'Stop'
$allowedHosts = @('localhost', '127.0.0.1')
$deploymentPath = Join-Path $PSScriptRoot 'control-deployment.json'
if (Test-Path -LiteralPath $deploymentPath) {
    $allowedHosts = @((Get-Content -LiteralPath $deploymentPath -Raw | ConvertFrom-Json).certificate_hosts)
}
if ($TargetHost -notin $allowedHosts) { throw 'Host is not in the local deployment allowlist.' }
$ssh = (Get-Command ssh.exe -ErrorAction Stop).Source
$parameters = @('-p','2222','-l','android','-o','BatchMode=yes','-o','IdentitiesOnly=yes',
    '-o','StrictHostKeyChecking=yes','-o',('UserKnownHostsFile='+(Join-Path $PSScriptRoot 'credentials\known_hosts')),
    '-i',(Join-Path $PSScriptRoot 'credentials\android_ed25519'),$TargetHost)
if($Command) { $parameters += $Command }
& $ssh @parameters
exit $LASTEXITCODE
