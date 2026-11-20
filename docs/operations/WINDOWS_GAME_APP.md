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

[GAME-APP-B](https://github.com/venomenon328/picross/issues/725#game-app-b)
verwaltet die Erstentscheidung in der privaten
`%LOCALAPPDATA%/PicrossGame/.updates/app-updates.json`. Dort liegen auch Stage,
Pending und Ergebnis. **Picross – Update-Einstellungen** öffnet allein die
Zustimmungsverwaltung. Ohne sicher gespeichertes Opt-in folgt der Spielstart
direkt auf die Entscheidung.

Mit Opt-in prüft das Fenster einmal nebenläufig den festen anonymen PG-Kanal.
**Ohne Update spielen** behält die Zustimmung und startet die vorhandene
Fassung. Ausschalten speichert Aus und verwirft die laufende Prüfung.
Schließen vor Helferübernahme beendet den Start. Kanal-, Netz- und Prüffehler
zeigen einen Status mit anschließendem Spielstart. Eine passende signierte
Gleichversion wird frisch lokal geprüft und benötigt keine Nutzdateien.

Nur eine vollständig verifizierte höhere Version gelangt in die
noncegebundene READY/GO-Übergabe. Der fest kompilierte PG-Helfer prüft den
Elternprozess, die Zustimmung, Kandidaten und MSI-Identität. Er wartet auf
das tatsächliche Ende des Launchers. Laufender Player und Dateibelegung
sperren den Austausch. Nach bestätigtem MSI-Erfolg prüft der Helfer die neue
installierte Identität. Die private PG-Pipe authentisiert erst den wartenden
Launcher und erlaubt danach einmal den Start. Eine zweite authentisierte
Antwort bindet den laufenden Player und dessen sichtbares Fenster. Bei
unbestätigtem Ergebnis bleibt der manuelle Start. Pending löst keine
Wiederholung aus.

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
python -m tools.game_app.diagnose --build <build> --output <diagnose>
```

Bau und Inspektion verwenden die [gebundene Windows-Bauumgebung](../../tools/production_workspace/WINDOWS_BUILD.md#gebundener-bau-und-version).
Die Startdiagnose prüft den regulären Export, den nativen Launcher und
die Guard-Entscheidungen mit isoliertem Profil. Der Diagnosedispatch prüft
außerdem den konkreten Kandidaten mit flüchtiger synthetischer Signatur,
den PG-Helfer und die private Startfreigabe mit einem echten Playerfenster.
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
