param(
    [string]$Exe = (Join-Path $PSScriptRoot 'picross-p1.exe'),
    [Parameter(Mandatory = $true)][string]$Profile
)

$ErrorActionPreference = 'Stop'
$resolvedExe = (Resolve-Path -LiteralPath $Exe).Path
if ([System.IO.Path]::GetFileName($resolvedExe) -ne 'picross-p1.exe') {
    throw 'Erwartet wird picross-p1.exe aus dem benannten GP-48-Spielerpaket.'
}
$reportPath = Join-Path (Split-Path -Parent $resolvedExe) 'product-report.json'
$report = Get-Content -Raw -Encoding UTF8 -LiteralPath $reportPath | ConvertFrom-Json
if ($report.source_tree_dirty -or $report.source_commit -notmatch '^[0-9a-f]{40}$') {
    throw 'Die Probe braucht ein sauberes, commitgebundenes Spielerpaket.'
}
$actualHash = (Get-FileHash -LiteralPath $resolvedExe -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualHash -ne $report.export_files.'picross-p1.exe') {
    throw 'EXE-Hash stimmt nicht mit dem beigefügten Bericht überein.'
}
$tempRoot = [System.IO.Path]::GetFullPath($env:TEMP).TrimEnd('\')
$profileRoot = [System.IO.Path]::GetFullPath($Profile).TrimEnd('\')
if (-not $profileRoot.StartsWith($tempRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Das Prüfprofil muss ein eigener Unterordner von TEMP sein.'
}
$marker = Join-Path $profileRoot '.picross-gp48-profile'
if (Test-Path -LiteralPath $profileRoot) {
    if (-not (Test-Path -LiteralPath $marker -PathType Leaf) -or
        [System.IO.File]::ReadAllText($marker) -ne $report.source_commit) {
        throw 'Vorhandener Ordner gehört nicht zu diesem GP-48-Head. Einen neuen Profilpfad wählen.'
    }
}
foreach ($folder in @($profileRoot, (Join-Path $profileRoot 'appdata'), (Join-Path $profileRoot 'localappdata'))) {
    [void](New-Item -ItemType Directory -Path $folder -Force)
}
if (-not (Test-Path -LiteralPath $marker)) {
    [System.IO.File]::WriteAllText($marker, $report.source_commit)
}
$priorAppData = $env:APPDATA
$priorLocalAppData = $env:LOCALAPPDATA
try {
    $env:APPDATA = Join-Path $profileRoot 'appdata'
    $env:LOCALAPPDATA = Join-Path $profileRoot 'localappdata'
    Write-Host "GP-48-Head: $($report.source_commit)"
    Write-Host "Isoliertes Prüfprofil: $profileRoot"
    # Interactive owner trial: the owner needs the visible game window.
    $process = Start-Process -FilePath $resolvedExe -WorkingDirectory (Split-Path -Parent $resolvedExe) -PassThru -Wait
    exit $process.ExitCode
} finally {
    $env:APPDATA = $priorAppData
    $env:LOCALAPPDATA = $priorLocalAppData
}
