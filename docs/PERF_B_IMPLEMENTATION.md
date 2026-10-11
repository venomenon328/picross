# PERF-B · Regulärer Atlaszeichner und begrenzte Caches

Issue [#68](https://github.com/venomenon328/picross/issues/68), bestehender
Draft-[PR #66](https://github.com/venomenon328/picross/pull/66) gegen `main`.
Vertrag: [CELL_RENDERING](CELL_RENDERING.md), einschließlich PERF-B-E1/S1–S6.
Technische Prüfung läuft; unabhängiges Review PERF-B-R01, persönliche
PERF-M01/SL-M01 und gesonderte Mergefreigabe bleiben vor Merge offen.

## Herkunft und Ressourcen

PERF-A-Lieferhead bleibt `2bbc28eecb0c15276ebcd52b473c4fdb5ee10781`,
Herstellerquelle bleibt `a83ecf5db0800d198bb870932bf0365341aabb28`.
Pläne, Originalbilder, sechs Atlanten, Manifest und historische Berichte in
[PERF-A](PERF_A_IMPLEMENTATION.md) bleiben unverändert. Das neue
[B-Messprotokoll](../examples/perf_b/plan.json) wurde vor der Messung festgelegt.

`examples/perf_b/a-source.zip` bewahrt die sieben ursprünglich im A-Manifest
gebundenen Hersteller-/Quell-/Consumerdateien. Prüfung von Containerhash,
vollständigem Inventar und ursprünglichen Einzelhashes erfolgt vor Verwendung.
`tools/perf_a_atlas.py generate` führt tatsächlich das archivierte Herstellerscript
aus; der neue Adapter wird nicht als alter Hersteller ausgegeben. Native
A-Proben erhalten in temporären Projekten die alten drei UI-Quellen unter
`perf_a/original/`; nur ihre Ressourcenpfade werden nachvollziehbar umgebunden.
Original- und Adapterhashes stehen getrennt im Produktbericht. Falsche Quellen
werden auch nach absichtlicher Neubindung des Containerhashs zurückgewiesen.

Die aktiven PNGs unter `art/cells/` sind bytegleich zu A. Ihr Importvertrag wird
separat geprüft. `ui/cell_atlas.gd` übernimmt Variante, Zeitbild, Detailstufe und
Innenflächenabbildung. Ein gemeinsames Material benutzt je Zeichenbefehl die
Palettenfarbe; sechs gemeinsame Texturen benötigen 48.906.240 dekodierte Bytes.
GPU-Zeichenarbeit bleibt bestehen, auch wenn Canvasbefehle wiederverwendet werden.
Im Spieler fehlen `perf_a/`, historische `pencil_marks` und alle Probescripte.

## Aktualisierung und Lebensdauer

`ui/atlas_marks.gd` besitzt höchstens `ceil(Zellzahl/64)` ruhende Chunkebenen,
eine Übergangsebene und eine Cursorebene. Keine Timer oder Materialinstanzen pro
Zelle und kein Gesamtrasterbitmap. Texturen und Material leben gemeinsam im
SceneTree; Varianten werden getrennt von der Farbe für Blatt-ID, Revision und
Koordinate berechnet. Cacheinhalte sind ausschließlich Darstellung, keine Saves.

Reine Mausbewegung aktualisiert Cursor und Koordinatentext. Animationstakte
aktualisieren die aktiven Zellen; Hinweis-/H1-/Miniatur-/UI-Refresh bleibt am
logischen Ereignis. Beim Eintritt/Austritt einer Vorschau oder eines Effekts
werden betroffene Ruhechunks invalidiert. Unterdrückte Zellen fehlen vollständig
im ruhenden Bestand. Tatsächliche Modelländerungen aktualisieren betroffene
Chunks; Session, Geometrie, Palette und Stil invalidieren den passenden Bestand.
Neue wirksame Vorschau beendet alte Effekte dauerhaft. Vorhandene Commit-,
Undo-/Redo-, Abbruch-, Fit-, Reset-/Restore- und Schalterwege bleiben unmittelbar.

210/120 ms, 56-%-Vorschau und begrenzte Mehrzellwelle bleiben unverändert.
Das Atlasbild folgt verstrichener Zeit, nicht der Anzahl gezeichneter Frames.
Nach Ablauf stoppt der Effekttakt. Die Endform stammt auch im Ruhezustand aus
Frame 23 derselben Variante. Bei Innenflächen bis null Pixel bleibt Füllung
entsprechend der festen Zwei-Pixel-Fuge leer; X wird weiter maßstäblich gezeichnet.

## Prüfwege und Lieferbudget

Der neue native `tests/perf_b_probe.gd` prüft die reguläre Szene und separat das
tatsächlich heruntergeladene PCK. Importierte Pixelhashes, aktiver Shader,
unabhängige A-Farb-/Zeit-/Variantenreferenz, Cachegrenzen und Ressourcenplateau
werden am Laufzeitpfad geprüft. Absichtlich falsche Variante, veralteter
Cachewert und gekoppelte Vollinvalidierung müssen dieselben Oracles auslösen.
Bestehende P1/G1/H1/Save/Recovery/Spoiler/Sidebar- und Echtzeit-Bildprüfungen
bleiben erhalten. Der abgelöste V3-Geometriefingerprint prüft nun importierte
Atlas-Endpixel und stabile Zellauswahl, weiterhin über zwei Prozesse.

`tools/perf_b.py` führt beide Quellrollen frisch unter Windows aus: die zehn
A-Kontexte mit sechs Warm-up-Frames, drei Wiederholungen und 36 Intervallen je
Fall sowie F03/F07 bei realem Fit. Rohdaten zählen CPU-Zeichenaufbau aller Ebenen
einschließlich Synchronisierung und Nullarbeitsframes; Wall-Frameabstände,
Dispatch, Zeichenaufrufe/Objekte und Speicher bleiben getrennte Größen.
GPU-Dauer, Präsentationszeit und physische Eingabelatenz werden nicht gemessen.
Gewünschte Zoomstufe und tatsächliche Größe stehen beide im Bericht.

PERF-B-E1 erhöht ausschließlich das technische Budget auf **30.000.000 Bytes**;
**75.000.000 Bytes gesamt** bleiben. Der Bildanteil erhält 18 MB für zwölf
verpflichtende SL-Bilder und kompakte B-Belege. Positiv-/Negativtests prüfen beide
exakten Grenzen. Endgrößen werden nach Verpackung kontrolliert. Allgemeine
CI-/Artefaktbereinigung gehört nicht zu dieser Änderung.

Commitgebundene Ergebnisse, vollständige CI-Auswahl, frischer Windows-Download
und getrennter Selbstreview werden im bestehenden Issue und PR nachgeführt.
Historische SL-R02/PERF-A-R01 sind keine Abnahme dieses neuen Gesamtstands.
