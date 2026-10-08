# VS-1 · Vertrag der Vollsichtstudie

Aktiver Nacharbeitsvertrag VS-E1-R2 aus [#57 §11](https://github.com/venomenon328/picross/issues/57).
VS-VB1 und die ursprüngliche Produktionsvorbereitung bleiben historisch. Technische Draft-Lieferung; VS-M01, unabhängiges Review und VS-D01 bleiben
offen. Keine reguläre Größenstrategie, Merge- oder Releasefreigabe.

## Gebundene Basis und Grenzen

Ausgangsbasis ist `main@985cf08e0cd7dda4186c3dd42b5eccbba1b80e3f`.
Alle Modi verwenden unverändert die Zeichenkomponenten aus `study/`: Chalkboard
mit Faktor 1,35, Zeilenslots 26 × UI, Spaltenslots 18 × UI, Stift/X und gleichzeitige
140/80-ms-Effekte. Spielbar sind ausschließlich G/V ohne Hand oder Rasterpanning.
R gehört nur zum historischen Erststand; die reguläre Plex-Ansicht ist keine VS-Referenz.
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
erzeugt keine Zellaktion. G erlaubt MMB für einzelne lange Hinweisfolgen; V zeigt
alle. Miniatur und MMB im Raster verschieben das Raster nicht. Alte R-Auswahl wird
auf G mit Einpasszoom normalisiert. Schema-1-Hand, Zentrum und Zoom werden beim
Ansichtsladen bereinigt; bestätigte Zellen/History/Farbe und semantische Lesepositionen
bleiben erhalten. Reguläre P1-Saves und ihr Schema ändern sich nicht.

G reserviert je Achse den tatsächlichen vollständigen Bedarf bei M ≤ 5, ohne alten
Dreiermindestwert oder Fünferpadding. Bei M > 5 wird die kleinste geeignete Reserve
anhand realer Glyphen, C1/AA, Statusstrich, Marker und kontinuierlicher Bewegung
ermittelt. Alle Sichtbarkeitsübergänge und die offenen Intervalle dazwischen werden
geprüft, für sämtliche angebotenen Schriftpixelgrößen. Mindestens min(5,n)
zusammenhängende ganze Zahlen bleiben sichtbar. Sechs/sieben passen gegebenenfalls
vollständig; mehrstellige Zahlen zählen als eine. Leere Linien behalten „–“.
V reserviert den vollständigen tatsächlichen Bedarf. Kein Spielfortschritt und
kein kleinerer Benutzerzoom verändert diese Reservierung.

Moduswahl liegt neben den acht Werkzeugen unten; die obere Boardgrenze folgt dem
realen Titel. Die Miniatur und Texte liegen in einer eigenen Seitenleiste mit
kompakterem Umfang bei wenig Höhe. Nach Controls/Rändern und beiden Hinweisreserven
bleibt je Seite 1 px für die halbe Breite der 2-px-Rasterlinien frei. Der Fit berechnet
min(verbleibende Breite/Spalten, verbleibende Höhe/Zeilen) und umfasst den vollständig
gezeichneten äußeren Rahmen einschließlich der unteren Abschlusslinie. Einpassen erreicht diese
Grenze; bewusst kleinere Zoomwerte bleiben kleiner. Jeder Zoom-/Resize-/UI-/Blatt-/
Ansichtsweg wird begrenzt. Semantische Lesepositionen werden neu eingerahmt;
outer_start und geometrisches Einrasten erst beim Loslassen bleiben.

Unter 16 px oder bei Glyphenkollisionen bleibt die Ansicht ausdrücklich eingeschränkt.
Unterhalb des zeichnungsfähigen Stiftinneren (>4 px) wird kein Raster vorgegeben:
„PASST NICHT“. Fenster vergrößern/UI verkleinern; kein R-Ausweg und kein positiver
Komfortnachweis. Fehlfälle bleiben vollständig in der Matrix.

## VS-P3 / VS-E1-R2: Messung und Lieferung

Die neue Hauptmatrix enthält 80 G/V-Zeilen bei logischen Clients 1920 × 1080 und
1280 × 720, UI 100/125 %, sowie 20 größere Kontrollen auf 2560 × 1440. Native
SubViewport-Bilder sind keine physische Display-/DPI-Abnahme. Die zusätzliche
OS-Fensterprobe erfasst tatsächliche Clientgrößen mit echten InputEvents.
TextServer-Glyphen samt Statusstrich, Clipping/Kollision, Hinweisrechtecke,
Controls, Zoomgrenzen und 16/18/20-px-Vergleichspunkte werden protokolliert.

Der gesonderte Planabschnitt VS-E1-R2 wurde vor dem Vergleich gebunden: E1-initial
plus höchstens zwei Korrekturen. E1-initial fand Status-/Modusüberdeckung bei
720p/UI125; E1-correction-1 verkürzt die Beschriftungen und verbreitert den Abstand
zur Seitenleiste. E1-correction-2 ergänzt ausschließlich den Rahmenzeichenraum und
prüft die Linien gegen den Viewport, damit Rundung an der Zellflächengrenze keine
Abschlusslinie auslässt. Native Pixelchecks prüfen alle vier Rahmenkanten zwischen
den Kreuzungen, einschließlich VS09/50×30/G und V am maximalen Zoom sowie VS08/40×40
bei 720p/UI125. Keine neue Produktion, Artwork-, Font- oder Hintergrundvariation.
Historische Produktionsdaten und L1–L3 bleiben unverändert.

Sechs Reviewdiagnose-Familien VS-E13–E18 decken Maxima 1–5 sowie parametrisierte
5/6/7/Langfolge und Transponat ab. Sie sind keine neuen Spielslots oder Zertifikate.
VS04/VS06, VS08 und VS10 ergänzen reale farbige Folgen; VS-D11/D12 bleiben die
ursprünglichen zwei Status-/Farbdiagnosen. Die Fünfergarantie zählt dieselben ganzen
Tokens, die der Zeichenpfad verwendet, einschließlich aller kritischen Dragübergänge.
Historische R-/Erststanddateien sind in
[historical-reference.json](../examples/vs1/historical-reference.json) mit Head,
Reviewarchiv, konkreten Dateihashes und Download gebunden; keine neuen R-Messungen.

Historisch begrenzte der Erstplan den Layoutversuch auf L1 plus zwei Korrekturen:
L1 brachte Messdaten und fand nicht zeichnungsfähige Kleinstzellen; L2 ergänzt
deren Fehlermeldung und die kompakte Statusposition; L3 trennt Status-/Werkzeugtexte
auch bei UI 125 %. Keine Font-, Thema- oder Hintergrundvariation.
Diese R-/Kopfaufteilung gilt ausschließlich für die historische Erstlieferung.

`tools/vs1_delivery.py` läuft aus dem bestehenden Produktharness. Die regulären
P1-/ZS1-Exporte schließen `full_view_study/*` aus. VS exportiert einen getrennten
Einstieg mit eingebettetem PCK. Spieler-ZIP enthält nur EXE-Paar, Anleitung,
Metadaten, leeres Protokoll und Lizenzen. Das separate Review-ZIP enthält Matrix,
gezielte native Bilder, Galerie, Quell-/Planbindungen und Prüfprotokolle.

Weiter: [Prüfzuordnung und Entscheidungsvorlage](VS1_VERIFICATION.md),
[Eigentümerprobe](VS1_OWNER_TRIAL.md).
