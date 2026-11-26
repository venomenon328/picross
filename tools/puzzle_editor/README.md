# Lokaler Picross-Bestandseditor · PE-APP-B

Eigenständiges Offlinewerkzeug für bereits registrierte Rätsel. Der
[Fachvertrag §13](../../docs/tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung)
definiert die lokale API und ihre Grenzen; der
[Paketentscheid](https://github.com/venomenon328/picross/issues/640)
führt K01–K08, T01–T03, unabhängiges Review A01 und persönliche Bedienprobe U01.

## Windowsstart

Den MSI-Kandidaten installieren: per-user ohne Administrator unter
`%LOCALAPPDATA%/Programs/PicrossPuzzleEditor`. Startmenü und optionale
Desktopverknüpfung starten die private Laufzeit. Vor Upgrade oder Deinstallation
alle PE-Instanzen geordnet beenden, auch mit anderem Checkout/Zustandsordner.
Ein laufender oder unklarer Zustand sperrt MSI; es gibt keinen Hardkill.
Checkout, Port, Theme, Inhaltsdateien, portable Ordner und PW bleiben erhalten.

Alternativ das portable Diagnose-ZIP vollständig in einen eigenen Programmordner entpacken und
`Picross-Bestandseditor.exe` doppelt anklicken. Kein Administrator, Pythonsetup,
Gitdownload oder Internet zur Bedienung erforderlich. EXE und `_internal` gemeinsam
erhalten. „Ordner wählen“ öffnet ein bestehendes Picross-Gitcheckout; Pfad und
Port bleiben im Starter sichtbar. „Editor starten“ öffnet den Standardbrowser.
Bei Portbelegung einen freien anderen Port ausdrücklich wählen. Ein weiterer
Start für dasselbe Checkout meldet die bestehende Instanz und schreibt nicht.

Das native Fenster bleibt für „Browser öffnen“ und „Geordnet beenden“ verfügbar.
Tab schließen beendet den Dienst nicht. Beenden wartet laufende Fachoperationen
ab; dabei weder Task-Manager-Kill noch Löschen von Journal-/Lockdateien verwenden.
Für einen Checkoutwechsel zuerst Browseränderungen übernehmen/verwerfen,
geordnet beenden und mit der neuen Ordnerwahl starten. Kein Import von Pythoncode
oder UI aus dem Datencheckout. Git und Inhaltsveröffentlichung bleiben extern; App-Updates verwenden ausschließlich den getrennten signierten PE-Kanal.

Entwicklerfallback mit CPython 3.13.14 x64, Pillow 12.3.0 und Tcl/Tk 8.6.15 aus
dem vertrauenswürdigen Programmcheckout:

```powershell
python -m tools.puzzle_editor
python -m tools.puzzle_editor --root E:\Test\picross --state E:\Test\pe-state --port 0
```

`--root` belegt die sichtbare Auswahl vor; gestartet wird erst per Button.
Der separate Zustandsordner enthält `config.json` mit letztem Pfad/Port und Hell/Dunkel-Auswahl; eigene Updateentscheidungen und temporäre Übergaben stehen getrennt in `.updates/`.
Standard: `%LOCALAPPDATA%/PicrossPuzzleEditor`. Keine Bilder, Inhalte oder Saves
in Einstellungen/Browserstorage. Temporäre Importe und Pläne außerhalb des
Checkouts verschwinden beim Verwerfen, Ablauf beziehungsweise regulären Stop.

## App-Updates beim Start

Nur die installierte, nicht erhöhte Windows-App bietet eine eigene ausdrückliche
Zustimmung. Ohne Aktivieren erfolgt kein Update-Netzabruf. Ablehnen beziehungsweise
Ausschalten bleibt gespeichert. Portable Ausgabe, Entwickler und Worker installieren
keine Updates. Erstinstallation und der erste updaterfähige MSI bleiben manuell;
ein noch nicht veröffentlichter PE-Kanal wird ehrlich als nicht verfügbar gemeldet.

Bei Zustimmung prüft die App einmal vor der ersten Editoröffnung. Das native
Fenster bleibt bedienbar; „Ohne Update fortfahren“ verwirft den aktuellen Versuch
und erhält die Zustimmung. Offline-, Signatur- und Downloadfehler geben die
vorhandene App frei. Eine signiert bestätigte Gleichversion meldet „Keine neuere
Appversion veröffentlicht.“; Downgrades und abweichende Gleichversionen werden
abgewiesen. „Editor starten“ bleibt die ausdrückliche Handlung für Server/Browser.

Nach sicherer Helferübernahme sind Skip und Opt-out gesperrt. Laufende Arbeit
wird vollständig abgewartet. Weitere PE-Instanzen, auch mit anderem Checkout
oder --state, verhindern Installation. Nach erfolgreichem MSI und bestätigtem
Wiederanlauf erscheint wieder das Auswahlfenster mit unverändertem Zustand;
der Editorserver startet erst per Button. Fehler oder unbestätigter Wiederanlauf
verlangen die angezeigte manuelle Prüfung. Es gibt keinen automatischen Retry,
Hardkill, erzwungenen Neustart oder allgemeines Rollbackversprechen. Eigene noch
belegte Updateablage bleibt erhalten und wird als solche gemeldet.

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
mindestens zwei Pixel je Rasterzelle. Hintergrund: 2304×768 PNG (neues Profil) oder 2304×576 PNG (Legacy) mit sichtbaren
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

Der Editor nutzt den [RI-ONE-Bestand](../../docs/production/PUZZLE_INTEGRATION_SINGLE_PATH.md)
mit einem führenden Record je Rätsel unter `content/puzzles/<id>.json`, dem
gemeinsamen Kategorienkatalog und der erzeugten Runtime v9. Ungültige Quellen
führen zu einem gezielten Fehler.

Start und Liste prüfen Kategorien, Runtime v9 und Recordnamen. Detailansicht
und Pflege lesen zusätzlich die betroffenen Records und Definitionen. Bildwechsel
benötigen keinen Solver. Unveränderte Rasterlogik
erzeugt weder neue Analyse noch Revision. Explizite Produktionsdiagnosen bleiben
separate Werkzeuge und werden vom Editor nicht automatisch gestartet.

Ein offenes Journal sperrt neue Arbeit. „Gebundenen Altstand wiederherstellen“
stellt nur nachweislich eigene Zustände der betroffenen Dateien wieder her,
wiederholbar und mit Runtime zuletzt. Bei fremden Bytes bleiben Journal und
Daten erhalten. Recovery verarbeitet das aktuelle Editorjournal. Abweichende
oder unklare Journale bleiben zur Klärung erhalten.
Request-/Tababbruch beendet keinen Writer. Bei verlorener Browserquittung erst
neu laden und den tatsächlichen Zustand prüfen, dann gegebenenfalls neu planen.
Keine freie Restorepfad- oder Löschfunktion.

## Paketbau und Prüfgrenzen

Sauberen veröffentlichten Programmcommit in einem eigenen Checkout verwenden,
offizielles CPython 3.13.14 Windows x64 und eine frische virtuelle Umgebung:

```powershell
python -m venv E:\Test\pe-build-env
E:\Test\pe-build-env\Scripts\python -m pip install pip==26.1.2
E:\Test\pe-build-env\Scripts\python -m pip install --only-binary=:all: -r tools/puzzle_editor/requirements-windows.txt
E:\Test\pe-build-env\Scripts\python -m tools.puzzle_editor.build_installer --output E:\Test\pe-build --version 0.2.1
E:\Test\pe-build-env\Scripts\python -m tools.puzzle_editor.verify_installer --build E:\Test\pe-build --output E:\Test\pe-inspection --expected-commit <volle-SHA> --version 0.2.1 --compare-build
```

Der gemeinsame PW-/PE-Bauer prüft exakte Pins, Runtime-/Wheellizenzen,
reale Analysis-/PYZ-Inputs, aktuelle Editorreader und bytegleiche Methodenquellen.
`tests` und `za1_fixtures` fehlen im Produkt. Der portable Builder bleibt unter
`tools.puzzle_editor.build_windows` verfügbar. Das vollständige Inventar wird vor
Bereitschaft geprüft. MSI, EXE, UI, Komponenten und Delivery verwenden dieselbe
injizierte Version ohne Quelländerung. 0.2.0 ist nur Portable-Startanker; erster
MSI-Kandidat 0.2.1. Feste PE-Upgradeidentität, neuer ProductCode je Version;
Gleichversion und Downgrade sind gesperrt. EXE/MSI haben kein Authenticode.

Der eigene Workflow `Puzzle editor release` folgt erfolgreicher Main-Push-CI.
Tatsächliche Paketinputs bestimmen den Fingerprint; identische Bytes ergeben
keinen neuen Installer. Nur der gegatete Publisher signiert PE-Metadaten und
veröffentlicht nach Rückdownloadprüfung unter `pe-vX.Y.Z`. Diagnose-Dispatch
veröffentlicht nie. Ohne gesonderten Betriebsauftrag und PE-Environment/Flags/
Signierbereitstellung bleibt Publikation gesperrt. B ergänzt den standardmäßig ausgeschalteten Selbstupdateclient. Keine private Laufzeit aus dem Datencheckout.

Maßgeblich sind [PE §14](../../docs/tools/PUZZLE_EDITOR.md#14-pe-app-a--feste-windows-produkt--und-releasebindung)
sowie [PE §15](../../docs/tools/PUZZLE_EDITOR.md#15-pe-app-b--startgate-und-sicherer-wiederanlauf)
und [#691 / PE-APP-B](https://github.com/venomenon328/picross/issues/691#umsetzungsvorbereitung-pe-app-b--startgate-selbstupdate-und-sicherer-wiederanlauf).
Projektkern plus tools, `evidence.mode=none`; separate einmalige Windows-MSI-/
Frozen-/Releaseproben T02/T03. Tatsächliche Originale und Ergebnisse stehen im
Draft-PR. MSI-Inspektion ist keine Installation. Unabhängiges A01 vor Merge,
reale Windows-11-Installation/Upgrade/Uninstall und Browserbedienung R01/U01 vor
Release bleiben getrennt. Keine automatische Chromiumprüfung.

## HG31: explizite Profilwahl

Neue Einzelkompositionen sind exakt 3:1. HP-W2: `describe --profile-id
picross-background-png2304x768-v1` (in einer Zeile aufrufen), dann dessen
vollständiges Profil/Hash in Request v2 und Entscheidung binden. Ausgabe
2304×768 RGBA8; verify prüft dieselbe Bindung. Altes Profil bleibt unverändert.
Fertigimport erkennt 2304×768 bzw. 2304×576 aus validierten PNG-Bytes und
übernimmt unverändert. V1-Capability erlaubt ausschließlich das alte Profil.
[Geschlossener Vertrag](../../docs/production/PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile).
Keine Kandidatenintegration vor geprüftem Mainmerge oder neue WIP-Migration.
