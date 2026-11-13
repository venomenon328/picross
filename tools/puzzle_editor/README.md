# Lokaler Picross-Bestandseditor · PE-B 0.1.0

Eigenständiges Offlinewerkzeug für bereits registrierte Rätsel. Der
[Fachvertrag §11](../../docs/PUZZLE_EDITOR.md#11-pe-b-lokaler-dienstvertrag-v1)
definiert die lokale API und ihre Grenzen; der
[Paketentscheid](https://github.com/venomenon328/picross/issues/576#issuecomment-6855913029)
führt K01–K12, T01–T03, unabhängiges Review A01 und persönliche Bedienprobe U01.

## Windowsstart

Das portable ZIP vollständig in einen eigenen Programmordner entpacken und
`Picross-Bestandseditor.exe` doppelt anklicken. Kein Administrator, Pythonsetup,
Gitdownload, Installer oder Internet erforderlich. EXE und `_internal` gemeinsam
erhalten. „Ordner wählen“ öffnet ein bestehendes Picross-Gitcheckout; Pfad und
Port bleiben im Starter sichtbar. „Editor starten“ öffnet den Standardbrowser.
Bei Portbelegung einen freien anderen Port ausdrücklich wählen. Ein weiterer
Start für dasselbe Checkout meldet die bestehende Instanz und schreibt nicht.

Das native Fenster bleibt für „Browser öffnen“ und „Geordnet beenden“ verfügbar.
Tab schließen beendet den Dienst nicht. Beenden wartet laufende Fachoperationen
ab; dabei weder Task-Manager-Kill noch Löschen von Journal-/Lockdateien verwenden.
Für einen Checkoutwechsel zuerst Browseränderungen übernehmen/verwerfen,
geordnet beenden und mit der neuen Ordnerwahl starten. Kein Import von Pythoncode
oder UI aus dem Datencheckout. Es gibt keine Netzwerk-/Git-/Releasefunktion.

Entwicklerfallback mit CPython 3.13.14 x64, Pillow 12.3.0 und Tcl/Tk 8.6.15 aus
dem vertrauenswürdigen Programmcheckout:

```powershell
python -m tools.puzzle_editor
python -m tools.puzzle_editor --root E:\Test\picross --state E:\Test\pe-state --port 0
```

`--root` belegt die sichtbare Auswahl vor; gestartet wird erst per Button.
Der separate Zustandsordner enthält nur `config.json` mit letztem Pfad/Port.
Standard: `%LOCALAPPDATA%/PicrossPuzzleEditor`. Keine Bilder, Inhalte oder Saves
in Einstellungen/Browserstorage. Temporäre Importe und Pläne außerhalb des
Checkouts verschwinden beim Verwerfen, Ablauf beziehungsweise regulären Stop.

## Bearbeiten

Links Suche/Filter verwenden und vorhandene ID öffnen. Erst dann werden Quellen
und Bilder vollständig geprüft. Rechts Name/Kategorie bearbeiten; Bilder über
Dateiauswahl oder Drop bereitstellen. Die aktuelle Vorschau ist vom noch nicht
gespeicherten Import getrennt beschriftet. PNG/SVG-Reveal höchstens 32 MiB,
8192 Pixel je Achse, 8 Mio. Pixel, mindestens zwei Pixel je Rasterzelle;
Hintergrund genau 2304×576 PNG mit sichtbaren und transparenten Pixeln.
Keine Skalierung, Konvertierung oder automatische Reparatur; Quellbytes bleiben.

Standard folgt der gewählten Kategorie, eigenes Bild und kein Hintergrund sind
eigene Präferenzen. Die bisher sourcefreie Standardzeichnung heißt „bisher ohne
eigene Zuordnung“. Für Bild-/Rasteränderungen tatsächlichen Akteur, Entscheidung,
vier Herkunftsfelder und Nutzungsbasis ausfüllen und bewusst bestätigen.
Der tatsächliche UTC-Zeitpunkt wird bei diesem Prüfantrag erfasst. Fehlende
Angaben blockieren; das Programm erfindet keine Bildfreigabe.

Rastertext steht nachgeordnet aufklappbar mit unveränderbarer Palette und
deterministischen Hinweisen bereit. 0 ist leer. Zeilen-/Zellfehler sind 1-basiert.
„Prüfen / Vorschau“ führt den bestehenden A1/A2/A3-Writerplan aus; bei neuer Logik
einschließlich Deduktion und aktuellem Rating. Paarlinien ist eine ausdrückliche
Profilwahl. Unvollständige Logiknachweise sind gesperrt. Die Vorschau nennt die
wirklich betroffenen Dateien und warnt bei neuer Revision vor dem nächsten
Spielstandneustart genau dieser ID. Kein Zugriff auf echte Spielerprofile.

Erst „Diesen Plan ausdrücklich übernehmen“ schreibt. Danach wird der echte
Bestand neu eingelesen. No-op erhält Bytes/mtimes. Stale Quellen, geänderte
Imports, fremde Locks/Journale und abgelaufene Pläne stoppen vor Mutation.
Plan höchstens zehn Minuten, Imports 15 Minuten gültig; erneuter Upload/Plan
entwertet ältere Vorschau. Unsaved-Änderungen sind markiert; Auswahl-/Refresh-
und Kategorienwechsel verlangen bewusstes Verwerfen. Kein stilles Speichern.

Kategorienverwaltung ist ein eigener Speichervorgang: Anlegen, Umbenennen,
Löschen leerer oder vollständige Neuzuordnung belegter Kategorien. Keine
Sortierungsverwaltung; neue Kategorie hängt automatisch an. Kategorieaktionen
mit ID-Änderungen nicht als gemeinsame atomare Transaktion darstellen.

## Migration und Recovery

V4/v7 ist lesbar und über A1 pflegbar. Bild-/Rasterpflege verlangt v4/v8.
„Migration prüfen / Vorschau“ erzeugt einen eigenen A2-Migrationsplan, der nur
Runtime v7→v8 ändert. Gesondert übernehmen; Wiederholung ist No-op. Anzeigen und
gewöhnliches Speichern migrieren niemals. V2/v3 brauchen zuerst den expliziten
[A1-CLI-Migrationsweg](../puzzle_production/README.md#pe-a1-aktuelle-namen-und-kategorien).
Der Editor führt keine echte Bestandsmigration automatisch aus.

Ein offenes Journal wird als „Recovery erforderlich“ angezeigt. Ausschließlich
„Gebundenen Altstand wiederherstellen“ verwendet das gemeinsame
`content_registry.recover`; wiederholbar und mit vollständiger Fremdbyteprüfung.
Bei Konflikt Journal und fremde Daten erhalten und die Ursache klären. Keine
freie Restorepfad-/Löschfunktion. Request-/Tababbruch beendet keinen Writer.

## Paketbau und Prüfgrenzen

Sauberen veröffentlichten Programmcommit in einem eigenen Checkout verwenden,
offizielles CPython 3.13.14 Windows x64 und eine frische virtuelle Umgebung:

```powershell
python -m venv E:\Test\pe-build-env
E:\Test\pe-build-env\Scripts\python -m pip install -r tools/puzzle_editor/requirements-windows.txt
E:\Test\pe-build-env\Scripts\python -m tools.puzzle_editor.build_windows --output E:\Test\pe-build
```

Der Builder verlangt die exakten Pins und Tcl/Tk-Version, prüft Frozen-Module,
UI und byteidentische Fachquellen einschließlich eingefrorener Methoden.
Ausgabe: portable ZIP, `components.json`, vollständiges Hash-/Byteinventar,
Laufzeit-/Python-/Pillow-/PyInstaller-/Tcl/Tk-Lizenzen und `START.md` im Paket.
`delivery.json` bindet Commit, Versionen, ZIP-/EXEhash. Keine Signatur, kein
Releasekanal oder automatisches Update. Der normale Windows-Spielerbuild in
Package CI ist vom separaten Editorbau und dessen tatsächlichem Start getrennt.

Ausgewählt: Projektkern und `tools`; schmale HTTP-/Sicherheits-/Instanztests in
`tools/test_puzzle_editor.py`. Echte Writer-/Browser-/Windows-T01–T03-Proben
einmalig auf synthetischen Daten, kein wachsender Echtkatalogtest. Bis zu drei
aktuelle UI-Originale und deren Produktheadbindung werden dem unabhängigen
Reviewer separat zugänglich gemacht. Kein automatisches Spiel-Chromiumprofil.
Die abschließende persönliche Eigentümerprobe U01 bleibt vor Schließung von
Issue #576 erforderlich, getrennt vom technischen Vor-Merge-Review A01.
