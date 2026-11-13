# Windows-App bauen und prüfen

Aktuell maßgeblich: [APP-A-K01–K10 / #612](https://github.com/venomenon328/picross/issues/612#issuecomment-6834815644)
und der [App-Releasevertrag](../../docs/PRODUCTION_UPDATES.md).
APP-A ist im Arbeitsbranch implementiert; technisches Review, Mainintegration und
Erstaktivierung stehen aus. APP-B ist nicht implementiert. Die historischen
[P4/K01–K08](https://github.com/venomenon328/picross/issues/588#issuecomment-6825638437),
[P4-N1](https://github.com/venomenon328/picross/issues/588#issuecomment-6828896451)
und dessen [Prüfzuschnitt](https://github.com/venomenon328/picross/issues/588#issuecomment-6829590335)
behalten ihre damalige Bindung, einschließlich des gelieferten 0.1.0-Installers.
Launcherbau und regulärer Windows-Spieler der Package-CI bleiben getrennt.
Das Nonogramm-Icon ist unter [assets](assets/README.md) gebunden.

## Gebundener Bau und Version

[release.json](release.json) hält die feste Upgrade-GUID, WiX-Pins und den
0.1.0-Startanker. [release_channel.py](release_channel.py) plant aus der letzten
vollständig geprüften veröffentlichten PW-Version bei geändertem Appfingerprint
Patch +1, zuerst 0.1.1; gleicher Fingerprint bleibt ohne neuen Bau/Release.
Keine fortlaufenden Versionscommits auf main. Der explizite Builderparameter
`--version` verwendet ausschließlich die geplante 0.1.x-Version und verändert
keine Quelldatei. MSI-Version, ProductCode, EXE-Versionsressource, eingebettete
Manifeste, MSI-Dateiname und Deliveryreport erhalten denselben Wert. UpgradeCode
bleibt gleich, ProductCode ist deterministisch neu je Version. Ungültige Version,
Downgrade und inhaltsabweichende Same-Version-Installation bleiben gesperrt.
Ohne Parameter bleibt der frühere lokale 0.1.0-Diagnosebau möglich; er ist keine
Veröffentlichung und keine neue Versionsautorität.

CPython **3.13.14 Windows x64**, pip **26.1.2**, Tcl/Tk **8.6.15** und sämtliche
Buildpakete exakt nach [requirements-windows.txt](requirements-windows.txt).
PyInstaller **6.22.3** erzeugt `onedir` + `windowed`, ohne UPX. Sauberer gesicherter
Gitstand und neuer eigener Ausgabeordner außerhalb des Checkouts:

```powershell
py -3.13 -m venv E:\EigeneArbeit\pw-build-env
E:\EigeneArbeit\pw-build-env\Scripts\python.exe -m pip install pip==26.1.2
E:\EigeneArbeit\pw-build-env\Scripts\python.exe -m pip install --only-binary=:all: -r tools/production_workspace/requirements-windows.txt
E:\EigeneArbeit\pw-build-env\Scripts\python.exe -m tools.production_workspace.build_installer --output E:\EigeneArbeit\pw-installer --version 0.1.1
E:\EigeneArbeit\pw-build-env\Scripts\python.exe -m tools.production_workspace.verify_installer --build E:\EigeneArbeit\pw-installer --output E:\EigeneArbeit\pw-inspection --expected-commit <volle-SHA> --version 0.1.1 --compare-build
```

`0.1.1` ist hier ein Diagnosebeispiel; die Pipeline verwendet den tatsächlichen
Planwert. Der Bau erzeugt `inputs.json` und prüft die echte PyInstaller-Analysis
gegen dieses committete Fingerprintinventar. Die isolierte private Umgebung
liefert die gepinnten Python-/Wheel-/Runtimeinputs. Der Builder bündelt die
benötigten Reader einschließlich `authoring_workflow`, Pillow, Tcl/Tk, UI und Icon;
der Datencheckout hat keine Codeautorität. `components.json` bindet Commit,
Fingerprint, Architektur, Komponenten und Ressourcenhashes, `inventory.json`
die übrigen Appdateien. Kein Versprechen bitidentischer EXEs ohne Messung.

WiX **3.14.1** kommt ausschließlich aus dem SHA-256-geprüften offiziellen
Binärarchiv laut Releasequelle (CSC-Paketbindung `3.14.1.20250415`). Kein globales
WiX oder Elevation für den Bau; .NET-Framework-4.x-Compiler aus Windows.
Der eigenständige C#-Guard läuft vor InstallInitialize auch bei Upgrade/Uninstall.
Restart Manager wird ausschließlich lesend genutzt, automatischer MSI-Restart/
Shutdown ist deaktiviert. MajorUpgrade nach InstallInitialize erlaubt
transaktionalen Rollback. Installer schreiben weder in Datencheckout noch Zustand,
Browserprofil oder portable Altordner.

## Separater Workflow, Diagnose und Aktivierung

[Production assistant release](../../.github/workflows/pw-installer.yml) ist kein
Job/Modul/Gate der Package CI. Sein automatischer Folgetrigger akzeptiert nur
eine erfolgreiche abgeschlossene Package-CI-Pushquelle von `venomenon328/picross`
auf main und prüft deren SHA, Repository, Versuch und beide Pflichtjobs frisch.
Der Checkout bleibt auf dieser vollen SHA. Bei neuem Main vor Veröffentlichung
wird der Kandidat verworfen; der nächste erfolgreiche Mainlauf plant neu.

Actions → **Production assistant release** → **Run workflow** ist immer eine
nicht veröffentlichende Diagnose des ausgewählten fixierten Workflowbranchcommits.
Vor Merge damit ausdrücklich den Implementierungsbranch wählen; diesen Ursprung
im PR nennen. Keine frei eingegebenen Download-/Repository-/Buildpfade oder SHA.
Die Diagnose umgeht keine Veröffentlichungschecks, sondern besitzt keinen
Publikationspfad. Der Publisher wird nur im automatischen Mainfolgelauf und mit
der nach separat beauftragter Aktivierung gesetzten Repositoryvariable
`PW_RELEASE_ENABLED=true` gestartet. Hier werden keine Variablen/Secrets geändert.

Ein frischer Plan verifiziert die letzte veröffentlichte PW-Autorität inklusive
binärer Assets; unvollständige veröffentlichte PW-Einträge sperren. Der Publisher
hat als einziger Job `contents:write`. Er lädt zuerst in einen gebundenen Draft,
prüft sämtliche Uploads per binärem Rückdownload und prüft Quelle/Autorität/Main
unmittelbar vor Freigabe erneut. Erst dann wird der Release sichtbar. Re-Runs
ergänzen nur fehlende Dateien im identischen Draft, niemals abweichende Assets.
Fremde Tags/Drafts stoppen ohne Force-Push, Overwrite oder Löschung. Die globale
serielle Gruppe verhindert gegenseitiges Überholen von Pipelinebuilds.

Produktdateien: `Picross-Produktionsassistent-X.Y.Z-windows-x64.msi`, `.sha256`,
`START.txt`, `delivery.json`, `inputs.json`, kanonisches `manifest.json`.
Letzteres bindet Schema, Repository, Produktionsstatus, Version, Source-SHA,
Fingerprint, Produktidentitäten, MSI-Inspektion und Hash/Bytes jeder anderen Datei.
Actions-Kandidat vierzehn Tage, Plan sieben Tage für den aktuellen Reviewer;
Original-Serverbefunde stehen im Joblog. Produktdiff enthält keine Binärbelege.
Nach gesonderter Erstaktivierung bleiben geprüfte Releases unter `pw-vX.Y.Z`
langlebig abrufbar. Der erste echte Release mit Rückdownload/Hashprüfung und die
echte Windows-11-Upgradeprobe sind eigene nachgelagerte Releasegates.

Hosted Windows Server sperrt per-user MSI für Standardbenutzer (1625). Keine
Installation oder Änderung dieser Policy im Serverlauf. Der vorhandene Inspector
liest stattdessen die tatsächliche MSI-Datenbank und alle per gebundenem WiX
`dark.exe` entpackten Bytes: Quelle, Fingerprint, Version in MSI/EXE,
Product-/Upgradecode, x64/limited/HKCU, Prüfsumme, vollständiges Payloadinventar,
Guard und Lizenzbytes. `--compare-build` vergleicht jede Datei zusätzlich mit dem
ursprünglichen `dist`-App-Image und prüft den ZIP-Hash. Technische Extrakte werden
laufzeitintern entfernt. Erfolgreiche Inspektion ist keine Clientinstallation.
Eine unabhängige spätere Rückdownloadprüfung verwendet `--expected-commit`, die
geplante `--version` und ein hashgebundenes `--wix-archive`.

Die vorhandenen manuellen P4-T02-/T03- und P3-Smokes unten sind bedarfsbezogene
Client-/Lebenszykluswerkzeuge; APP-A führt sie nicht automatisch aus und behauptet
keine neue Windows-11-Upgradeabnahme. Bereits gelieferte P4-Nachweise werden durch
APP-A nicht rückwirkend neu definiert.

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
