# Windows-App bauen und prüfen

Maßgeblich: [P4/K01–K08](https://github.com/venomenon328/picross/issues/588#issuecomment-6825638437).
Launcherbau und regulärer Windows-Spieler der Package-CI bleiben getrennt.
Keine neuen automatischen Trigger und kein Release/Tag. Das zusätzlich beauftragte
Nonogramm-Icon ist unter [assets](assets/README.md) gebunden.

## Gebundener Bau

Einzige Releasequelle ist [release.json](release.json): validiertes
`MAJOR.MINOR.PATCH` im MSI-Bereich (255/255/65535), feste Upgrade-GUID, neue
deterministische Product-GUID je Version. Startversion steht ausschließlich dort.
Für ein Update diese Quelle monoton erhöhen; Authoring-/Spielversion und 588-P3
sind keine Installerproduktversion. Keine inhaltsabweichende Same-Version-
Installation und kein Downgrade; nach Uninstall ist Wiederinstallation möglich.
App-/Komponentenmanifest, MSI, Dateiname und Lieferreport verwenden dieselbe
Version und den sauberen Quellcommit. Zustand und Datencheckout bleiben getrennt.

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

Für das vollständige Produkt stattdessen den Installer-Einstieg ausführen:

```powershell
E:\EigeneArbeit\pw-build-env\Scripts\python.exe -m tools.production_workspace.build_installer --output E:\EigeneArbeit\pw-installer
E:\EigeneArbeit\pw-build-env\Scripts\python.exe -m tools.production_workspace.smoke_installer --build E:\EigeneArbeit\pw-installer --output E:\EigeneArbeit\pw-installer-smoke
```

Windows 11 x64, vorhandener .NET-Framework-4.x-Compiler/Runtime; kein globaler
WiX-Setup oder Elevation für den lokalen Bau. Das offizielle WiX-3.14.1-Binärarchiv
wird nach URL/SHA-256 aus der Releasequelle geprüft; es entspricht der
CSC-Chocolatey-Paketbindung `3.14.1.20250415` (Paketrevision, keine andere Engine).
WiX-Compiler, Linker, DTF/SfxCA und eingebettete WiX-Lizenz kommen aus diesem Archiv.
Der kleine DTF-Guard läuft im per-user-MSI vor InstallInitialize, auch beim
Upgrade/Uninstall. Restart Manager wird ausschließlich lesend benutzt; MSI-
Restart/Shutdown deaktiviert. Vollständiger Austausch mit MajorUpgrade nach
InstallInitialize erlaubt transaktionalen Rollback. Kein Installer schreibt in
Checkout, PW-Zustand, Browserprofil oder portable Altordner.

Der [eigene Workflow](../../.github/workflows/pw-installer.yml) hat ausschließlich
`workflow_dispatch`, liest eine volle ausdrücklich gewählte SHA, die in `main`
integriert sein muss, baut sauber und startet genau dieselben Bau-/Smokeskripte.
Kein Aufruf aus Package CI, kein automatischer Browser-/Installationslauf dort.
Produktdownload: `Picross-Produktionsassistent-X.Y.Z-windows-x64.msi`, `.sha256`,
`START.txt`, `delivery.json`; 14 Tage Retention. Kein Release/Tag/Deployment.
Der Workflow wird erstmals nach gesondert freigegebenem Merge regulär aufrufbar.
P4-T04 bleibt bis zum echten manuellen Run und binären Rückdownload offen.

P4-T01 prüft kleine Quell-/Metadatenverträge im gewählten `tools`-Modul.
P4-T02 installiert unter nicht erhöhtem Testbenutzer ausschließlich mit synthetischem
Zustand, baut aus einem separaten sauberen synthetischen Quellcommit eine echte
Vorgängerversion, installiert und aktualisiert sie. MSI-Codes, Inventar/Lizenzen,
Startmenü/Anwendungseintrag, Zweitstart/Port, Same-Version/Downgrade, laufende App,
fremde Dateibelegung, begonnener synthetischer P2-Drain sowie Uninstall/Reinstall
werden tatsächlich geprüft. Der Drain nutzt den gleichen Source-Runtimevertrag
mit eingetretener synthetischer Transaktion; kein Testbypass im Frozen-Produkt.
Kein Test an echten Zuständen/Refs; bestehende Installation sperrt den Smoke.
Lokale Testdateien/Logs danach entfernen; kein regulärer Technik-Upload.
P4-T03 bleibt die tatsächliche Bedienung des installierten Startmenüeintrags,
nativer Fenster und Standardbrowsers mit synthetischem heutigem Job/Bild und
erhaltener Browseroption am gleichen Origin nach Upgrade. HTTP ersetzt sie nicht.
P4-A01 benötigt unabhängig vollständigen Diff/CI/T01–T03 und echte MSI-Bytes.
Im Draft-PR Commit, MSI-/EXE-Hash, Größe, Inventar, tatsächlichen Binärabruf,
Szenarien/Akteur/Windowsversion, Einschränkungen und befristeten Prüfzugang nennen.

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
Die [weiteren Runtime-Lizenzen](licenses/README.md) ergänzen OpenSSL, Expat, zlib,
bzip2, liblzma und mpdecimal; der Build prüft die aus Python abrufbaren Versionen.
Die PyInstaller-Ausnahme ersetzt keine Abhängigkeitslizenzen.

Die Lieferung bleibt **unsigniert**. Kein Zertifikat, keine neuen Secrets und
keine abgeschalteten Schutzfunktionen. SmartScreen kann warnen; auch eine Signatur
garantiert keine Warnungsfreiheit. Quellcommit/Hash vor Benutzung abgleichen.

Technische Primärquellen: [Bauoptionen](https://pyinstaller.org/en/stable/usage.html),
[Runtimepfade](https://pyinstaller.org/en/stable/runtime-information.html),
[Prozesse/DLL-Suche](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html),
[Lizenzausnahme](https://pyinstaller.org/en/stable/license.html),
[Microsoft SmartScreen](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation).
