# Lokaler Picross-Bestandseditor · PE-EDIT2 0.2.0

Eigenständiges Offlinewerkzeug für bereits registrierte Rätsel. Der
[Fachvertrag §13](../../docs/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung)
definiert die lokale API und ihre Grenzen; der
[Paketentscheid](https://github.com/venomenon328/picross/issues/640)
führt K01–K08, T01–T03, unabhängiges Review A01 und persönliche Bedienprobe U01.

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
Der separate Zustandsordner enthält nur `config.json` mit letztem Pfad/Port und Hell/Dunkel-Auswahl.
Standard: `%LOCALAPPDATA%/PicrossPuzzleEditor`. Keine Bilder, Inhalte oder Saves
in Einstellungen/Browserstorage. Temporäre Importe und Pläne außerhalb des
Checkouts verschwinden beim Verwerfen, Ablauf beziehungsweise regulären Stop.

## Bearbeiten

Links stehen Suche, Kategorie und Sortierung dauerhaft über einer eigenen
scrollbaren Liste. Name A–Z/Z–A und Kategorie/Name sind rein visuell. Pfeil-,
Bild-, Pos1-/Ende-Tasten verschieben den Fokus, Enter/Leertaste öffnen die Auswahl.
Auch bei 1.000 Einträgen werden nur sichtbare Zeilen und ein kleiner Puffer
angelegt. Namen und knappe Kategorien sind sichtbar, technische IDs nicht.

Öffnen liest nur die ausgewählte Definition und ihre aktuellen kleinen
Referenzen; sichtbare Bilder werden erst bei Bedarf geladen. Rechts
Name/Kategorie bearbeiten und Bilder über Dateiauswahl oder Drop bereitstellen.
PNG/SVG-Reveal: höchstens 32 MiB, 8192 Pixel je Achse, 8 Mio. Pixel und
mindestens zwei Pixel je Rasterzelle. Hintergrund: 2304×576 PNG mit sichtbaren
und transparenten Pixeln. Importbytes werden nicht umgerechnet.

Standard folgt der gewählten Kategorie, eigenes Bild und kein Hintergrund sind
eigene Präferenzen. Die zusammengesetzte Vorschau zeigt das Abschlussbild
proportional mit Alpha auf dem echten Spielpapier und der gewählten Zeichnung.
Ungespeicherte Importe erscheinen sofort. Herkunfts-, Rechte-, Akteur- oder
Erklärungsfelder sind nicht erforderlich.

Die grafische Rastervorschau zeigt die tatsächliche Palette, Leerzellen und
Gitter; Zoom/Einpassen und gültiger Rastertext wirken unmittelbar lokal.
Fehler nennen Zeile/Spalte und leeren die Grafik statt falsche Daten zu zeigen.
Hell/Dunkel oben im Fenster gilt für die gesamte Oberfläche und bleibt nach
Neustart und Portwechsel erhalten. Motivfarben und Spielpapier bleiben original.

Rastertext steht nachgeordnet aufklappbar mit unveränderbarer Palette und
deterministischen Hinweisen bereit. 0 ist leer. Zeilen-/Zellfehler sind 1-basiert.
„Prüfen / Vorschau“ führt den gezielten aktuellen Editorplan aus; bei neuer Logik
einschließlich Deduktion und aktuellem Rating. Paarlinien ist eine ausdrückliche
Profilwahl. Unvollständige Logiknachweise sind gesperrt. Die Vorschau nennt die
wirklich betroffenen Dateien und warnt bei neuer Revision vor dem nächsten
Spielstandneustart genau dieser ID. Kein Zugriff auf echte Spielerprofile.

Erst „Diesen Plan ausdrücklich übernehmen“ schreibt. Danach werden nur die geänderten Ergebnisse frisch
zurückgelesen. No-op erhält Bytes/mtimes. Stale Quellen, geänderte
Imports, fremde Locks/Journale und abgelaufene Pläne stoppen vor Mutation.
Plan höchstens zehn Minuten, Imports 15 Minuten gültig; erneuter Upload/Plan
entwertet ältere Vorschau. Unsaved-Änderungen sind markiert; Auswahl-/Refresh-
und Kategorienwechsel verlangen bewusstes Verwerfen. Kein stilles Speichern.

Kategorienverwaltung ist ein eigener Speichervorgang: Anlegen, Umbenennen,
Löschen leerer oder vollständige Neuzuordnung belegter Kategorien. Die visuelle
Listensortierung ist davon unabhängig; neue Kategorien hängen im Spiel an. Kategorieaktionen
mit ID-Änderungen nicht als gemeinsame atomare Transaktion darstellen.

## Versionen und Recovery

Der Editor ist kein Migrationswerkzeug. Schreiben verlangt Runtime v8;
Bild-/Rasterpflege zusätzlich bereits extern migrierte aktuelle Bildquellen.
Bei Altversionen erscheint ein unverändernder Hinweis auf die
[Codex-Anweisung #641](https://github.com/venomenon328/picross/issues/641).
Keine Migration im UI/API, beim Öffnen oder im Hintergrund. Die alten
Repository-Migrationsbefehle werden nicht mit der portablen App ausgeliefert.

Normale Editoraktionen prüfen ihre Eingaben und Änderungen, nicht den ganzen
Bestand oder historische Produktionsbelege. Liste/Metadaten lesen nur die drei
kleinen Indizes. Bildwechsel benötigen keinen Solver; unveränderte Rasterlogik
erzeugt weder neue Analyse noch Revision. Explizite Produktionsdiagnosen bleiben
separate Werkzeuge und werden vom Editor nicht automatisch gestartet.

Ein offenes Journal sperrt neue Arbeit. „Gebundenen Altstand wiederherstellen“
stellt nur nachweislich eigene Zustände der betroffenen Dateien wieder her,
wiederholbar und mit Runtime zuletzt. Bei fremden Bytes bleiben Journal und
Daten erhalten. Alte Journale behalten ihren expliziten gemeinsamen Recoveryweg.
Request-/Tababbruch beendet keinen Writer. Bei verlorener Browserquittung erst
neu laden und den tatsächlichen Zustand prüfen, dann gegebenenfalls neu planen.
Keine freie Restorepfad- oder Löschfunktion.

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
Der portable Starter prüft vor Bereitschaft zusätzlich alle Programmdateien
gegen das vollständige Byte-/Hashinventar; fehlende/geänderte Teile sperren den Start.
Ausgabe: portable ZIP, `components.json`, vollständiges Hash-/Byteinventar,
Laufzeit-/Python-/Pillow-/PyInstaller-/Tcl/Tk-Lizenzen und `START.md` im Paket.
`delivery.json` bindet Commit, Versionen, ZIP-/EXEhash. Keine Signatur, kein
Releasekanal oder automatisches Update. Der normale Windows-Spielerbuild in
Package CI ist vom separaten Editorbau und dessen tatsächlichem Start getrennt.

Für PE-EDIT2 ausgewählt: Projektkern, `tools` und `production.catalog`.
T01–T03 sind einmalige Datei-/Zeit-, Konflikt-/Recovery- und echte
Windows-/Browserproben an eigenen Kopien mit 56/1.000 Einträgen. Genau zwei
UI-Originale (hell/dunkel) und die getestete portable Ausgabe werden dem
unabhängigen Reviewer für höchstens sieben Tage zugestellt. Kein automatisches
Spiel-Chromiumprofil. PE-EDIT2-A01 vor Merge und die persönliche PE-B-U01 aus
#576 vor Release bleiben offen bis zur jeweiligen unabhängigen Abnahme.
