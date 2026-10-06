param([string]$Trial = 'rp6-first', [switch]$Status)
$ErrorActionPreference = 'Stop'
if ($Trial -notmatch '^[a-zA-Z0-9_-]{1,48}$') { throw 'Trial: nur Buchstaben, Ziffern, _ und -.' }
$rp6Exe = Join-Path $PSScriptRoot 'picross-p1.exe'
$rp6Report = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'product-report.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$rp6Hash = (Get-FileHash -LiteralPath $rp6Exe -Algorithm SHA256).Hash.ToLowerInvariant()
if ($rp6Hash -ne $rp6Report.export_files.'picross-p1.exe') { throw 'EXE stimmt nicht mit Produktreport überein.' }
$rp6Root = Join-Path ([IO.Path]::GetTempPath()) ('picross-rp6-owner-' + $rp6Report.source_commit.Substring(0,12) + '-' + $Trial)
$rp6Save = Join-Path $rp6Root 'roaming\Godot\app_userdata\picross · P1\p1\saves'
Write-Output ('Quellcommit: ' + $rp6Report.source_commit)
Write-Output ('EXE SHA-256: ' + $rp6Hash)
Write-Output ('Isolierter Prüfstand: ' + $rp6Root)
Write-Output ('Spielstände: ' + $rp6Save)
if ($Status) {
    if (Test-Path -LiteralPath $rp6Save) { Get-ChildItem -LiteralPath $rp6Save -File | Select-Object Name,Length,LastWriteTime }
    return
}
$rp6PreviousRoaming = $env:APPDATA
$rp6PreviousLocal = $env:LOCALAPPDATA
try {
    $env:APPDATA = Join-Path $rp6Root 'roaming'
    $env:LOCALAPPDATA = Join-Path $rp6Root 'local'
    New-Item -ItemType Directory -Force -Path $env:APPDATA,$env:LOCALAPPDATA | Out-Null
    # This is the interactive owner game window, intentionally visible.
    Start-Process -FilePath $rp6Exe -WorkingDirectory $PSScriptRoot -Wait
} finally {
    $env:APPDATA = $rp6PreviousRoaming
    $env:LOCALAPPDATA = $rp6PreviousLocal
}
