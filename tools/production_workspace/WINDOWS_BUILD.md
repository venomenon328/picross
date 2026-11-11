# Windows-App bauen und prüfen

Maßgeblich: [P3/K08](https://github.com/venomenon328/picross/issues/588#issuecomment-6809498803).
Launcherbau und regulärer Windows-Spieler der Package-CI bleiben getrennt.
Keine neuen automatischen Trigger und kein Release/Tag. Das zusätzlich beauftragte
Nonogramm-Icon ist unter [assets](assets/README.md) gebunden.

## Gebundener Bau

CPython **3.13.14 Windows x64**, pip **26.1.2**, Tcl/Tk **8.6.15** und sämtliche
Buildpakete exakt nach [requirements-windows.txt](requirements-windows.txt).
PyInstaller **6.22.3** erzeugt `onedir` + `windowed`, ohne UPX. Sauberer
gesicherter Gitstand und neuer eigener Ausgabeordner außerhalb des Checkouts:

```powershell
py -3.13 -m venv E:\EigeneArbeit\pw-build-env
E:\EigeneArbeit\pw-build-env\Scripts\python.exe -m pip install pip==26.1.2
E:\EigeneArbeit\pw-build-env\Scripts\python.exe -m pip install --only-binary=:all: -r tools/production_workspace/requirements-windows.txt
E:\EigeneArbeit\pw-build-env\Scripts\python.exe -m tools.production_workspace.build_windows --output E:\EigeneArbeit\pw-build
```

Der Build prüft Versionen und sauberen Quellstand, bündelt Python, transitiv
benötigte unveränderte Produktionsmodule einschließlich `authoring_workflow`,
Pillow, Tcl/Tk, UI und Icon aus demselben Commit. Der Datencheckout hat keine
Codeautorität. `components.json` bindet Commit, Architektur, Komponenten und
Ressourcenhashes; `inventory.json` alle übrigen Lieferdateien per Größe/SHA-256.
`delivery.json` außerhalb des App-Images enthält ZIP-/EXE-Größen und SHA-256.
Kein Versprechen bitidentischer EXEs ohne Messung.

Die ZIP enthält nur `Picross-Start/` mit Anwendung, Ressourcen, Inventar,
Start-/Updateanleitung und Lizenzen. Keine Testcheckouts, Produktionsoriginale,
Zustände, privaten Pfade oder Buildcaches. Den kompletten Ordner ausliefern.

## Nachweise und Zustellung

P3-T01: `python -m unittest tools.test_production_launcher -v` im bedarfsgewählten
`tools`-Modul. P3-T02 ist ein einmaliger manueller Windows-Frozen-Durchstich:

```powershell
python -m tools.production_workspace.smoke_windows --archive E:\EigeneArbeit\Picross-Start-windows-x64.zip --output E:\EigeneArbeit\pw-smoke
```

**Den tatsächlich zugestellten Download** verwenden. Das Skript vergleicht das
Dateiinventar, startet die Frozen-EXE mit auf Git/System beschränktem PATH,
synthetischem heutigen 0.8-Job samt Originalbild, Datencheckout ohne Code,
fremden Sentinelmodulen im CWD und Umlaut-/Leerzeichenpfaden. Geprüft werden
Konfiguration/Cache, Reader/Bildbytes, Zweitstart, Neustart, Portkonflikt,
ausdrücklicher Portwechsel, eigener synthetischer Absturz, fehlendes Git und
defekte UI. Nachlauf prüft echte Prozess-/Portbeendigung und unveränderte Datenrefs.
Nur eigene synthetische Prozesse, keine P2-Löschung. Kein Browsernachweis.
Eigene Smoke-/Builddaten anschließend gemäß Arbeitsablagevertrag bereinigen.

P3-T03 bleibt separat: zulässiger interaktiver Windowsdesktop, tatsächlicher
Doppelklick, native Einrichtung/Fehler/Stop und tatsächlich geöffneter
Standardbrowser mit synthetischem Job/Originalbild. Akteur, Windowsversion,
Download-/EXE-Hash, Szenarien und Grenzen im PR dokumentieren. Keine historische
Policyblockade umgehen und keine HTTP-/Linuxprobe als Windowsbedienung ausgeben.
P3-A01 ist das unabhängige technische Review vor Merge; kein Selbstreview und
keine zusätzliche persönliche Eigentümerabnahme.

Download und unveränderliche Commit-/Hashbindung im Draft-PR verlinken und die
Bytes tatsächlich zurückladen/prüfen. Bei befristetem Artefaktdienst 14 Tage
Produktretention; bei Reviewref dessen Zweck/Endpunkt benennen, kein automatisches
Ablaufversprechen. Kein App-Binary im Produktdiff. Technikdaten nur bei konkretem
Reviewbedarf, höchstens sieben Tage. Abgelaufenen Kandidaten gezielt neu zustellen.

## Lizenzen und Signatur

`LICENSES/Python.txt` stammt aus der verwendeten CPython-Distribution und enthält
auch deren Drittkomponenten-/Windows-DLL-Hinweise. Pillow und seine mitgelieferten
Bibliotheken sowie PyInstaller/Bootloader erhalten die vollständigen Lizenztexte
aus den gebundenen Wheels. Tk erhält `license.terms` aus der Pythoninstallation.
Einige Python-Distributionen lassen die Tcl-Lizenz aus; dafür ist die unveränderte
[Tcl-8.6.15-Lizenz](licenses/Tcl-8.6.15.txt) aus dem
[offiziellen Versionsref](https://github.com/tcltk/tcl/blob/core-8-6-15/license.terms)
versioniert. Die Ersatzquelle wird nur mit tatsächlich geprüftem Tcl 8.6.15 benutzt.
Die PyInstaller-Ausnahme ersetzt keine Abhängigkeitslizenzen.

Die Lieferung bleibt **unsigniert**. Kein Zertifikat, keine neuen Secrets und
keine abgeschalteten Schutzfunktionen. SmartScreen kann warnen; auch eine Signatur
garantiert keine Warnungsfreiheit. Quellcommit/Hash vor Benutzung abgleichen.

Technische Primärquellen: [Bauoptionen](https://pyinstaller.org/en/stable/usage.html),
[Runtimepfade](https://pyinstaller.org/en/stable/runtime-information.html),
[Prozesse/DLL-Suche](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html),
[Lizenzausnahme](https://pyinstaller.org/en/stable/license.html),
[Microsoft SmartScreen](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation).
