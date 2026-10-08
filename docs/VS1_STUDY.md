# VS-1 · Vertrag der Vollsichtstudie

Umsetzung von [#57](https://github.com/venomenon328/picross/issues/57), Vorbereitung
VS-VB1. Technische Draft-Lieferung; VS-M01, unabhängiges Review und VS-D01 bleiben
offen. Keine reguläre Größenstrategie, Merge- oder Releasefreigabe.

## Gebundene Basis und Grenzen

Ausgangsbasis ist `main@985cf08e0cd7dda4186c3dd42b5eccbba1b80e3f`.
Alle Modi verwenden unverändert die Zeichenkomponenten aus `study/`: Chalkboard
mit Faktor 1,35, Zeilenslots 26 × UI, Spaltenslots 18 × UI, Stift/X und gleichzeitige
140/80-ms-Effekte. R behält die bisherige Buchaufteilung und Navigation und erhält
denselben Rechteckadapter. Die damalige reguläre Plex-Ansicht ist keine VS-Referenz.
Ungemergte Dateien aus PR #56 sind nicht übernommen; ZS2-N01–N03 gehören nicht hierher.
Bei Integration von #56 während der Arbeit muss aktuelles `main` integriert, die
Zeichenbasis neu gebunden und die betroffene Vergleichsmatrix neu erzeugt werden.

Die kleinen gemeinsamen Anschlüsse in Main/SaveStore behalten regulär genau neun
IDs, die Appidentität und Schema 1. Definition lässt nur die exakt gebundene
Studienressource zusätzlich zu den bisherigen Pfaden zu. Reveal zeichnet echte
Breite/Höhe mit quadratischen Zellen und proportionalem Artwork. Reguläre
quadratische Produktionsadapter behalten ihre Schranke.

## VS-P1: Daten und begrenzte Herstellung

[Plan](../examples/vs1/plan.json) und [leeres Eigentümerprotokoll](../examples/vs1/owner-protocol.json)
wurden mit `48d302b` vor dem ersten Import versioniert. 26 gebundene Kandidaten
wurden tatsächlich ausgewertet, 40 waren maximal erlaubt. Keine neue Reparatur,
keine KI-Aufrufe, keine zusätzlichen Illustrationen. Die neue unabhängige Prüfung
bekam pro Kandidat dieselben getrennten 30 s / 100.000 Linien wie der Solver.
Der unveränderte F-09-Bestand durchläuft seinen bestehenden vollständigen RP5-Replay.
[Produktion](../examples/vs1/production.json) enthält Zeiten und alle Varianten,
auch nicht vollständig gelöste. Menschliche Arbeitszeit ist unbekannt.

Das [Fallmanifest](../examples/vs1/manifest.json) bindet zehn spielbare Fälle,
Quellen, Nutzungsgrundlage über die bestehenden RP-Quellen, Varianten,
Matrix-/Dateihashes, unabhängige Proofs, Orientierung, Palette, Hinweise,
Reveal, Motivsichtung sowie contain-Ränder. Die Aussage „zertifiziert“ gilt nur
für vollständige Deduktion vom unbekannten Raster und den Endmatrixvergleich.
Sie ist keine Motiv-, Komfort- oder Katalogabnahme. VS05/VS06 sind ausdrücklich
kontrollierte Transponate von VS03/VS04, keine neuen natürlichen Hochkantmotive.

| Format (Spalten × Zeilen) | Mono | Farbe | Max. Hinweise Zeile/Spalte |
| --- | --- | --- | --- |
| 30 × 30 | VS01 | VS02 | 1/1; 10/14 |
| 40 × 30 | VS03 | VS04 | 7/3; 26/14 |
| 30 × 40 | VS05 | VS06 | 3/7; 14/26 |
| 40 × 40 | VS07 | VS08 | 3/2; 13/14 |
| 50 × 30 | VS09 | VS10 | 7/3; 24/15 |

Kurze und lange tatsächliche Hinweisfolgen sind vertreten; Häufigkeiten und
größte Zahlen stehen im Manifest. Mono-Beispiele sind vergleichsweise sparsam.
Die zwei reinen Reviewdiagnosen VS-D11 (50 × 30, angrenzende Farben/viele X) und
VS-D12 (40 × 40, lange Zahlen/Leerlinien/drei Hinweiszustände) sind konsistente
synthetische Matrizen, sichtbar nicht zertifiziert, keine zusätzlichen Spielslots.

## VS-P2: Native Bedienung und Fortsetzung

`full_view_study/main.tscn` verwendet Session/Player/Gesture, History,
Hinweiszustände, Miniatur, Recovery und Abschluss aus P1. Es gibt keine zweite
Spiellogik. Vor dem ersten Savezugriff wird der stabile Root
`user://vs1/revision-1` gesetzt. Die Appidentität bleibt `picross · P1`; der
reguläre Root `user://p1/saves` wird nicht verwendet. Testroot-Overrides dienen nur
isolierten Prüfungen. Direkter EXE-Start benötigt keinen Launcher und kein Godot.

Die vorhandenen zehn Blätter erhalten eigene Slots. Modus, ausgewähltes Blatt,
UI-Skalierung und gewünschter Fitwert stehen getrennt in `study-view.json`.
Normale Saves enthalten weiter nur gültige Schema-1-Arbeitszoomwerte; freie
Studien-Fitwerte werden rekonstruiert. Ungültige Ansichtsmetadaten verwerfen keine
Zelldaten. Zell-Recovery bleibt ausdrücklich zu bestätigen. Ein bestätigter
Reset oder Vergleichsstand betrifft nur das ausgewählte Studienblatt.

Der künstliche Vergleichsstand folgt einer festen arithmetischen Eingabefolge,
liest keine Lösung und gilt nicht als Lösungshilfe. Vor Abschluss bleiben Titel
neutral und Miniaturen zeigen ausschließlich eigene Einträge. Das Umschalten
verwirft laufende Gesten, erhält bestätigte Matrix/History/aktive Farbe und
erzeugt keine Zellaktion. R behält MMB-Raster-/Hinweisnavigation; G erlaubt MMB
für lange Hinweise; V benötigt keine Hinweisnavigation.

G reserviert bis zu sechs Zeilen- und fünf Spaltenslots, V den vollständigen
maximalen Hinweisbedarf. Reservierung bleibt beim Erfüllen von Hinweisen konstant.
Nach Abzug von Controls, Miniatur und Rand wird quadratischer Zellabstand berechnet.
Alle angebotenen G/V-Zoomstufen sind durch den aktuellen Fit begrenzt. Unter 16 px
steht ausdrücklich Diagnose/Komfort offen; mögliche Glyphenkollisionen werden
gemeldet. Unterhalb eines überhaupt zeichnungsfähigen Stiftinneren (>4 px) wird
kein Raster vorgetäuscht: die Ansicht zeigt „PASST NICHT“ und verweist auf R.
Solche Fälle bleiben in der Matrix, mit `geometry_rendered=false` und gemessener
Kandidatengeometrie. Sie sind keine Vollsicht-Erfolge.

## VS-P3: Messung und Lieferung

Die Hauptmatrix hat 80 G/V- und 40 R-Zeilen bei logischen Clients 1920 × 1080 und
1280 × 720, UI 100/125 %. Weitere 30 Zeilen auf 2560 × 1440 plausibilisieren.
Native SubViewport-Bilder sind ausdrücklich keine physischen Auflösungs- oder
DPI-Proben. Zellabstand, Schriftpixel, echte TextServer-Glyphen samt Statusstrich,
Clipping/Kollisionen, Hinweisrechtecke, Miniatur/Controls, Zoomgrenzen und
16/18/20-px-Vergleichspunkte werden protokolliert. Negative Fälle bleiben sichtbar.

Der Vorabplan begrenzt den Layoutversuch auf L1 plus zwei Korrekturen:
L1 brachte Messdaten und fand nicht zeichnungsfähige Kleinstzellen; L2 ergänzt
deren Fehlermeldung und die kompakte Statusposition; L3 trennt Status-/Werkzeugtexte
auch bei UI 125 %. Keine Font-, Thema- oder Hintergrundvariation.

`tools/vs1_delivery.py` läuft aus dem bestehenden Produktharness. Die regulären
P1-/ZS1-Exporte schließen `full_view_study/*` aus. VS exportiert einen getrennten
Einstieg mit eingebettetem PCK. Spieler-ZIP enthält nur EXE-Paar, Anleitung,
Metadaten, leeres Protokoll und Lizenzen. Das separate Review-ZIP enthält Matrix,
gezielte native Bilder, Galerie, Quell-/Planbindungen und Prüfprotokolle.

Weiter: [Prüfzuordnung und Entscheidungsvorlage](VS1_VERIFICATION.md),
[Eigentümerprobe](VS1_OWNER_TRIAL.md).
