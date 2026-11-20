"""Read-only inspection of the actual Windows Installer database."""
import json
import os
import subprocess

def msi_properties(msi):
    # Windows Installer COM queries the real binary, not a sidecar report.
    command = r'''$ErrorActionPreference='Stop'; $i=New-Object -ComObject WindowsInstaller.Installer; $d=$i.OpenDatabase($env:P4_MSI,0); $v=$d.OpenView('SELECT `Property`, `Value` FROM `Property`'); $v.Execute(); $p=@{}; while($r=$v.Fetch()) {$p[$r.StringData(1)]=$r.StringData(2)}; $p | ConvertTo-Json -Compress'''
    return json.loads(subprocess.check_output(['powershell.exe', '-NoProfile', '-Command', command],
                                             env={**os.environ, 'P4_MSI': str(msi)}, text=True))


def msi_rows(msi, table, columns):
    """Read fixed columns from a real table; all values remain MSI strings."""
    if not all(name.isidentifier() for name in (table, *columns)):
        raise ValueError('Invalid MSI table/column name')
    sql = 'SELECT ' + ', '.join(f'`{name}`' for name in columns) + f' FROM `{table}`'
    command = r"""$ErrorActionPreference='Stop'
    [Console]::OutputEncoding=[Text.UTF8Encoding]::new()
    $i=New-Object -ComObject WindowsInstaller.Installer
    $d=$i.OpenDatabase($env:P4_MSI,0)
    $v=$d.OpenView($env:P4_MSI_SQL)
    $v.Execute()
    $rows=@(while($r=$v.Fetch()){
        ,@(for($n=1; $n -le [int]$env:P4_MSI_COLUMNS; $n++) { $r.StringData($n) })
    })
    ConvertTo-Json -InputObject $rows -Compress
    """
    return json.loads(subprocess.check_output(
        ['powershell.exe', '-NoProfile', '-Command', command],
        env={**os.environ, 'P4_MSI': str(msi), 'P4_MSI_SQL': sql, 'P4_MSI_COLUMNS': str(len(columns))},
        encoding='utf-8',
    ))
