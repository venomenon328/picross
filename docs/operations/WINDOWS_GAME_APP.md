# Picross als Windows-Anwendung

[GAME-APP-A / #725](https://github.com/venomenon328/picross/issues/725#game-app-a)
bindet den regulären Godot-Debugplayer an einen Windows-x64-Installer. Der
[gemeinsame Updatevertrag](../tools/PRODUCTION_UPDATES.md) regelt den gemeinsamen Client, Releaseautorität,
signierte Metadaten, Kataloggrenzen und Draft-Recovery. Die
[Spielanleitung](../../game/README.md) beschreibt Installation und Spielen.

## Feste Identität

| Gegenstand | Wert |
| --- | --- |
| Adapter, Anwendung und Einstieg | PG, Picross, `Picross-Game.exe` |
| Programm und Updaterzustand | `%LOCALAPPDATA%/Programs/PicrossGame` und `%LOCALAPPDATA%/PicrossGame` |
| MSI, Versionslinie und Tag | `Picross-Spiel-X.Y.Z-windows-x64.msi`, `0.1.x`, `pg-vX.Y.Z` |
| Anker und erster Kandidat | `0.1.0` und `0.1.1` |
| UpgradeCode | `C1DB6F47-0935-41B8-978E-627D4015B360` |
| ProductCode | UUIDv5 aus UpgradeCode und Appversion |
| Registry und Laufschutz | `HKCU/Software/PicrossGame/Installer` und `Global/PicrossGame.Running.<Benutzer-SID>` (Windows-Pfadtrennzeichen) |
| Wireform und Signaturdomäne | `picross-pg-release-v1/v2`, `picross-pg-signature-v1`, `picross-pg-trust-v1`, `picross-pg-release-v2` plus NUL |
| Vertrauen | Öffentlich freigegebener fester PW-/PE-Root, in eigener PG-Trustform |
| Betriebsparameter | `pg-app-release` (ausschließlich Branch `main`), `PG_RELEASE_ENABLED`, `PG_UPDATE_SIGNING_ENABLED`, `PG_UPDATE_SIGNING_KEY` |

## Installation und Start

Das MSI installiert für den aktuellen Benutzer. Der Startmenüeintrag **Picross**
und die optionale Desktopverknüpfung öffnen den eigenständigen Windows-x64-Launcher. Seine Python-, Tk- und
Kryptografielaufzeiten liegen im MSI. Der Launcher prüft die Hashes des gebauten `picross-p1.exe` und `picross-p1.pck`,
startet ausschließlich den Player im selben Programmverzeichnis und behält den
Benutzermarker bis zum Ende des tatsächlichen Kindprozesses. Der MSI-Guard
prüft den Marker und die tatsächliche Dateibelegung einschließlich direkter
Playerstarts. Blockierte Installer brechen mit einer Meldung ab. Der getrennte
Portable-Download enthält weiterhin die Konsolenhilfe.

Programm- und Verknüpfungsdaten sind die einzigen vom MSI verwalteten Dateien.
Godot behält `picross · P1`, `user://p1/saves/` und Schema 1. Portable Spielstände,
Backups, Präferenzen und Fortsetzen-Merker befinden sich weiterhin im
Godot-Benutzerverzeichnis. Die vorhandene [Revisionsregel](../tools/PUZZLE_EDITOR.md#93-sicherer-automatischer-save-neustart)
gilt beim Spielen.

## Zustimmung, Update und Wiederanlauf

[GAME-APP-D / #731](https://github.com/venomenon328/picross/issues/731)
ersetzt den normalen Startablauf aus GAME-APP-B. **Picross** öffnet bei jedem
normalen Start den Launcher mit fester, Windows-skalierter Breite,
Appversion und integrierter Update-Einstellung. Bei Neuinstallation und
regulärem Upgrade ist **Picross** der einzige Startmenüeintrag. Das Upgrade
entfernt die frühere Einstellungen-Verknüpfung über die MSI-Komponenten
der alten Version. Die optionale Desktopverknüpfung öffnet denselben Launcher.

[GAME-APP-E / #733](https://github.com/venomenon328/picross/issues/733) trennt
Update-Suche, Installation und Spielstart. Die Einstellung **Automatische
Update-Suche** liegt in `%LOCALAPPDATA%/PicrossGame/.updates/app-updates.json`.
Nach sichtbarer Fensteröffnung und gültigem Opt-in sucht der Launcher einmal
nebenläufig im festen anonymen PG-Kanal. Auch das erste Aktivieren kann diese
Suche auslösen. Ohne gültige Entscheidung speichert **Ohne Updates spielen**
die Ablehnung. Speicherfehler lassen den Offline-Spielweg offen.

Eine authentisierte höhere Version erscheint mit Versionsnummer und **Update
installieren**. Erst dieser Klick lädt die fünf gebundenen Nutzassets, zeigt
ihren Bytefortschritt und verifiziert alle Dateien vor der Helferübergabe.
Gleichversion und Fehler erhalten ihren eigenen Status im offenen Launcher.
**Spielen** verwirft einen offenen Versuch und startet einmal die installierte
Fassung. Ausschalten oder Schließen bricht vor der atomaren READY-Übernahme ab.
Nach Übernahme sperrt der Launcher weitere Aktionen. Der PG-Helfer prüft
Identität und Zustimmung, wartet nach GO auf das echte Prozessende und
verwendet die passive MSI-Anzeige.

Nach MSI-Erfolg startet der Helfer genau einen neuen Launcher. Die private
PG-Pipe authentisiert den gestarteten Prozess und dessen sichtbares
Launcherfenster mit frischer Challenge, eigener HMAC-Domäne, Benutzer-,
EXE-, Versions-, Source-, Fingerprint- und Präferenzbindung. Der Launcher
wartet außerhalb des GUI-Threads begrenzt auf das Ende des gebundenen Helfers.
Erst dessen passendes bestätigtes Ergebnis und sichere Bereinigung erlauben
eine neue einmalige Suche. Das gilt auch beim ersten normalen Öffnen nach
einem erfolgreichen Update. Fehler, ausstehender Neustart und unbestätigte
Übergaben autorisieren keine Wiederholung. Der frühere private Spielpfad
`--update-restart` erfüllt ausschließlich den Spielwunsch ausgelieferter Helfer.

## Diagnose und Veröffentlichung

`tools.game_app.build` startet den gebundenen regulären Windows-Debugexport
separat von Package CI. Der Fingerprint umfasst die committeten Runtime-
und Importquellen, Toolchain-/Verpackungsinputs und ausgelieferte Texte.
Godot importiert in einem eigenen leeren Projektverzeichnis. Der Exportaudit
bindet diese Eingänge, die Pins und die tatsächlich erzeugten Bytes. Das
MSI-Inventar und `--compare-build` binden alle entpackten Dateien an den Build.
Die Engineversion steht getrennt von der Appversion im Baubericht.

Der [Installerworkflow](../../.github/workflows/game-installer.yml) kann
diagnostisch am fixierten Branchcommit bauen. Alternativ führt Windows lokal
dieselben Schritte am sauberen PR-Head aus:

```powershell
python -m tools.game_app.build --output <build>
python -m tools.game_app.inspect --build <build> --output <inspection> --expected-commit <sha> --compare-build
python -m tools.game_app.launcher_smoke --build <build> --inspection <inspection>/result.json --output <smoke> --expected-commit <sha> --negative-control
python -m tools.game_app.diagnose --build <build> --output <diagnose>
```

Bau und Inspektion verwenden die [gebundene Windows-Bauumgebung](../../tools/production_workspace/WINDOWS_BUILD.md#gebundener-bau-und-version).
[PG-START-FIX](https://github.com/venomenon328/picross/issues/817#issuecomment-7082659950)
verlangt für jeden neu gebauten Kandidaten nach `--compare-build` und vor
Kandidatenabschluss und Upload den normalen Start der unveränderten
`Picross-Game.exe`. Die Probe verwendet die tatsächlichen Windows-Pfade für
Programm und Zustand auf einem frischen Runner und beansprucht beide exklusiv.
Der Start erfolgt ohne Argumente aus einem Arbeitsverzeichnis außerhalb des
Checkouts. Ohne MSI-Registrierung zeigt der reagierende Tk-Launcher die
Kandidatenversion, **Nicht verfügbar**, **Suche aktivieren** und **Spielen**.
Die Probe erkennt diese sichtbaren Elemente aus dem Fenster des gestarteten
Prozesses und schließt es mit `WM_CLOSE`. Erfolg verlangt Exit 0, ein
unverändertes Dateiinventar und genau einen Prozess im Diagnosejob. Ein
fehlendes oder ungebundenes Ergebnis stoppt den Kandidatenabschluss.
Die Probe verwendet Windows-OCR und räumt ausschließlich ihre Laufdaten auf.
Der Dispatch führt zusätzlich eine Negativkontrolle mit vorzeitigem Prozessende
aus und stellt die gebundenen Originale bis zu sieben Tage für das Review bereit.

Die zusätzliche Diagnose prüft den regulären Export, den nativen Launcher und
die Guard-Entscheidungen mit isoliertem Profil. Der Diagnosedispatch prüft
außerdem den konkreten Kandidaten mit flüchtiger synthetischer Signatur,
den PG-Helfer und die Bestätigung des sichtbaren neuen Launcherfensters.
Die Einführungsprobe für #733 prüft zusätzlich den alten Spielpfad mit dem
Helfer aus dem veröffentlichten 0.1.3-MSI und einem echten Playerfenster.
Der ausgeschlossene Diagnosetreiber liefert dafür den isolierten Kontext
nach einem simulierten MSI-Erfolg. MSI-Inspektion, automatisierte Startbeobachtung,
persönliche Sicht-/Bedienprobe und echte Installation sind eigene Belege.
Die persönliche nicht erhöhte Installations-/Update-/Fortsetzenprobe
[GAME-APP-R01](https://github.com/venomenon328/picross/issues/725#game-app-c-und-abschlussgate-game-app-r01)
gehört zu C.

Für Veröffentlichungen akzeptiert der Publisher ausschließlich eine tatsächliche
erfolgreiche Package CI eines Main-Pushs. Die eigene PG-Auswahl erkennt auch
geänderte Runtime-Inhalte ohne reguläres Playerartefakt. Identische Eingaben
erzeugen keinen Bau. Patch +1 folgt aus der verifizierten eigenen signierten
Releaseautorität. Der Kandidat wird als Draft geschrieben, vollständig binär
zurückgeladen und nach erneuter Quell-, Autoritäts-, Trust- und Katalogprüfung
sichtbar gemacht. Die Inbetriebnahme der PG-Parameter gehört zu GAME-APP-C.
Gemeinsame Kernänderungen können reguläre PW-/PE-Publisher bei einem späteren
Merge auslösen.
