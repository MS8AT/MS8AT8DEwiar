$ErrorActionPreference = 'Stop'
$pythonPath = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'python-path.txt') -Raw).Trim()
Start-Process -FilePath $pythonPath -ArgumentList @('-X','utf8','-B',('"'+(Join-Path $PSScriptRoot 'control.py')+'"')) -WorkingDirectory $PSScriptRoot -WindowStyle Hidden | Out-Null
