"""Read-only inspection of the actual Windows Installer database."""
import json
import os
import subprocess

def msi_properties(msi):
    # Windows Installer COM queries the real binary, not a sidecar report.
    command = r'''$ErrorActionPreference='Stop'; $i=New-Object -ComObject WindowsInstaller.Installer; $d=$i.OpenDatabase($env:P4_MSI,0); $v=$d.OpenView('SELECT `Property`, `Value` FROM `Property`'); $v.Execute(); $p=@{}; while($r=$v.Fetch()) {$p[$r.StringData(1)]=$r.StringData(2)}; $p | ConvertTo-Json -Compress'''
    return json.loads(subprocess.check_output(['powershell.exe', '-NoProfile', '-Command', command],
                                             env={**os.environ, 'P4_MSI': str(msi)}, text=True))

