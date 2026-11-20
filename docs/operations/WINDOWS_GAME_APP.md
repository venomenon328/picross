# Picross als Windows-Anwendung

[GAME-APP-A / #725](https://github.com/venomenon328/picross/issues/725#game-app-a)
bindet den regulären Godot-Debugplayer an einen Windows-x64-Installer. Der
[gemeinsame Updatevertrag](../tools/PRODUCTION_UPDATES.md) regelt Releaseautorität,
signierte Metadaten, Kataloggrenzen und Draft-Recovery. Die
[Spielanleitung](../../game/README.md) beschreibt Installation und Spielen.

## Feste Identität

| Gegenstand | Wert |
| --- | --- |
| Adapter, Anwendung und Einstieg | PG, Picross, `Picross-Game.exe` |
| Programm und reservierter Updaterzustand | `%LOCALAPPDATA%/Programs/PicrossGame` und `%LOCALAPPDATA%/PicrossGame` |
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
und die optionale Desktopverknüpfung öffnen den kleinen Windows-x64-Launcher.
Dieser verwendet das mit Windows 11 ausgelieferte .NET Framework 4.x. Der
Launcher prüft die Hashes des gebauten `picross-p1.exe` und `picross-p1.pck`,
startet ausschließlich den Player im selben Programmverzeichnis und behält den
Benutzermarker bis zum Ende des tatsächlichen Kindprozesses. Der MSI-Guard
prüft den Marker und die tatsächliche Dateibelegung einschließlich direkter
Playerstarts. Blockierte Installer brechen mit einer Meldung ab. Der getrennte
Portable-Download enthält weiterhin die Konsolenhilfe.

Programm- und Verknüpfungsdaten sind die einzigen vom MSI verwalteten Dateien.
Godot behält `picross · P1`, `user://p1/saves/` und Schema 1. Portable Spielstände,
Backups, Präferenzen und Fortsetzen-Merker befinden sich weiterhin im
Godot-Benutzerverzeichnis. Die vorhandene [Revisionsregel](../tools/PUZZLE_EDITOR.md#93-sicherer-automatischer-save-neustart)
gilt beim Spielen. Der A-Launcher startet direkt. Zustimmung, Updateprüfung
und Wiederanlauf gehören zu GAME-APP-B.

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

Für die Inspektion wird `pefile==2024.8.26` benötigt. Die Diagnose prüft
regulären Exportstart, den nativen Launcher und die Guard-Entscheidungen
mit isoliertem Profil. MSI-Inspektion, automatisierte Startbeobachtung,
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
