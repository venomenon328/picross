param([Parameter(Mandatory = $true)][string]$Exe)
$ErrorActionPreference = 'Stop'
$h1Exe = (Resolve-Path -LiteralPath $Exe).Path
if ((Split-Path -Leaf $h1Exe) -ne 'picross-h1-probe.exe') {
    throw 'Bitte die separate picross-h1-probe.exe aus h1-probe-windows-x86_64.zip angeben.'
}
$h1Profile = Join-Path $env:TEMP ('picross-h1-owner-' + [guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory -Path $h1Profile)
$h1PriorApp = $env:APPDATA
$h1PriorLocal = $env:LOCALAPPDATA
try {
    $env:APPDATA = Join-Path $h1Profile 'appdata'
    $env:LOCALAPPDATA = Join-Path $h1Profile 'localappdata'
    Write-Host "Künstliche H1-Linienprobe ohne Speicherung; isoliertes Profil: $h1Profile"
    & $h1Exe
} finally {
    $env:APPDATA = $h1PriorApp
    $env:LOCALAPPDATA = $h1PriorLocal
}
