param(
    [Parameter(Mandatory)][string]$Python,
    [Parameter(Mandatory)][string]$Build,
    [Parameter(Mandatory)][string]$Output,
    [Parameter(Mandatory)][string]$Source
)
$ErrorActionPreference = 'Stop'
try {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [Security.Principal.WindowsPrincipal]::new($identity)
    if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'Installer smoke must run under the standard test account'
    }
    # LoadUserProfile loads HKCU, but Start-Process still inherits the caller's
    # environment. Never send compilers/MSI to runneradmin's profile or TEMP.
    # A first-logon profile can lack AppData directories. Create the known
    # folders as this user rather than accepting GetFolderPath's empty result.
    $env:USERPROFILE = [Environment]::GetFolderPath('UserProfile', 'Create')
    $env:LOCALAPPDATA = [Environment]::GetFolderPath('LocalApplicationData', 'Create')
    $env:APPDATA = [Environment]::GetFolderPath('ApplicationData', 'Create')
    if (-not $env:USERPROFILE -or -not $env:LOCALAPPDATA -or -not $env:APPDATA) {
        throw "Loaded test profile is incomplete: USERPROFILE=$env:USERPROFILE; LOCALAPPDATA=$env:LOCALAPPDATA; APPDATA=$env:APPDATA"
    }
    $env:HOME = $env:USERPROFILE
    $env:TEMP = $env:TMP = Join-Path $Output 'temp'
    New-Item -ItemType Directory -Path $env:TEMP | Out-Null
    $env:PYTHONIOENCODING = 'utf-8'
    Write-Output "Installer smoke user: $($identity.Name); elevated=false; TEMP=$env:TEMP; LOCALAPPDATA=$env:LOCALAPPDATA"
    Set-Location -LiteralPath $Source
    & $Python -m tools.production_workspace.smoke_installer --build $Build --output (Join-Path $Output 'lifecycle')
    $code = $LASTEXITCODE
    Set-Content -LiteralPath (Join-Path $Output 'exit.txt') -Value $code
    exit $code
} catch {
    Write-Output ($_ | Out-String)
    exit 1
}
