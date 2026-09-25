param([Parameter(Mandatory = $true)][string]$Exe)
$ErrorActionPreference = 'Stop'
$h1Exe = (Resolve-Path -LiteralPath $Exe).Path
$h1Script = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot 'h1-owner-probe.gd')).Path
$h1Profile = Join-Path $env:TEMP ('picross-h1-owner-' + [guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory -Path $h1Profile)
$h1PriorApp = $env:APPDATA
$h1PriorLocal = $env:LOCALAPPDATA
try {
    $env:APPDATA = Join-Path $h1Profile 'appdata'
    $env:LOCALAPPDATA = Join-Path $h1Profile 'localappdata'
    Write-Host "Künstliche H1-Linienprobe ohne Speicherung; isoliertes Profil: $h1Profile"
    & $h1Exe --script $h1Script
} finally {
    $env:APPDATA = $h1PriorApp
    $env:LOCALAPPDATA = $h1PriorLocal
}
