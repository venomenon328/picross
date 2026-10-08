# VS-1 · technische Nachweise und Entscheidungsvorlage

Status: Implementierung und technische Prüfstrecke für die Draft-Lieferung vorhanden.
Maßgebliche Head-/Run-/Artefaktbindung
steht im zugehörigen Draft-PR zu [#57](https://github.com/venomenon328/picross/issues/57)
und in `vs1-report.json`. VS-M01 und VS-D01 bleiben offen; keine Behauptung
unabhängiger Abnahme, Mergefähigkeit oder Releasefähigkeit.

## Prüfzuordnung

| Akzeptanz | Ausgeführter Anschluss / Beleg |
| --- | --- |
| VS-A01 | Vorabplan `48d302b`; zehn Manifestfälle mit Verteilungen, Quellen, Hashes, Orientierung und contain-Rändern; 26 Produktionsvarianten ohne Reparatur |
| VS-A02 | `vs1_tests.gd`: echte InputEvents für Ecken/Linien/Umwandeln/Neutralisieren/Zurückziehen/Wechsel/History; isolierter Root vor Lesen; `vs1_roundtrip.gd` in getrennten Prozessen |
| VS-A03 | `vs1_capture.gd`: alle angebotenen G/V-Zoomstufen, Resize/UI-Matrix, explizite Fehlfälle, Clipping/Kollisionen und 16/18/20-px-Vergleich |
| VS-A04 | `test_vs1.py` im Fachjob: komplette Quellenrekonstruktion, unabhängige Proofs und Enddomains; manipulierte Maße/Orientierung/Matrix/Hinweise/Palette/Pfade/Proofs, doppelte IDs, Revealbindung, Diagnosezertifizierung und unvollständiger Reparaturreplay abgewiesen |
| VS-A05 | `vs1-matrix.json`: aktuell 80 G/V-Hauptzeilen und 20 größere Kontrollen, reale Glyphen-/Statusstrichgrenzen; gezielte Arbeits-/Diagnosebilder; Erstmatrix historisch 120 + 30 |
| VS-A06 | Gemeinsame reguläre P1-/ZS1-Tests und unveränderte Pixelbaselines im product-Job; VS-Save-Recovery, Spoilergrenze, Miniatur und rechteckiger Abschluss zusätzlich |
| VS-A07 | Zwei getrennte ZIPs mit Quellhead/Basis/Test-Checkout/Run sowie EXE-/Bild-/Matrixhashes; tatsächlicher Downloadstart auf Windows separat im PR gebunden |
| VS-A08 | Nachstehende vorläufige technische Einordnung, vollständige Fehlfälle im Bericht und unausgefülltes Eigentümerprotokoll |

Die sechs Pflichtjobs `docs`, `product`, `preflight`, `puzzle-production`,
`rp4-windows`, `rp5-repair` müssen am Lieferhead/Test-Merge erfolgreich sein.
`tools/p1_product.py` ruft die VS-Tests, sechs Neustartprozesse, native Messung und
separaten Export tatsächlich auf. Der Linux-product-Job belegt allein keinen
Windows-EXE-Start. Die implementierende Windows-Prüfung muss das heruntergeladene
ZIP verwenden und dessen Hashes sowie normalen/maximierten Client protokollieren.

## Aktiver Nachweisvertrag VS-E1-R2

| Anforderung | Gebundener Anschluss |
| --- | --- |
| N01 | vs1_capture.gd: Board-/Papier-/Controlrechtecke, 100 Matrixzeilen, Glyphen und Statusstrich; obere Fläche durch Modusleiste unten frei |
| N02 | vs1_tests.gd, vs1_window.gd: keine Hand/Miniatur-/Rasternavigation, echte Ecken-/MMB-/Rad-/Werkzeugeingaben, Fit, UI100/125, echte Fenster-Resize/Abbruch und G/V-Wechsel |
| N03 | vs1_e1_cases.gd / vs1_e1_tests.gd: sechs begrenzte Diagnosen, vollständige Tokens an allen Glyphen-/Markerübergängen und Zwischenintervallen; 1–5, 5/6/7/lang, Transponate, unveränderte farbige Korpusfälle und drei Hinweiszustände |
| N04 | vs1_roundtrip.gd: sechs getrennte Schreib-/Leseprozesse für G, V und Legacy R/Hand/Zoom/Zentrum; Zellen, History, Farbe, Auswahl und semantische Lesepositionen; Recovery/Isolation/Spoilerprüfungen |

tools/vs1_delivery.py registriert E1-Prüfung und sämtliche Roundtrips im Produktlauf.
Unter Windows folgt die tatsächliche OS-Fensterprobe; CI-Linux behält die native
SubViewport-Matrix. Neue Matrix, Bilder und Logs sind im separaten Review-ZIP.
minimum_surplus misst je Folge die kleinste Differenz der tatsächlich gezeichneten
Tokens zu min(5,n). Negative Fälle werden nicht aus der Gesamtmatrix entfernt.
Der aktuelle Lieferhead und die neuen Download-/Windowsbindungen stehen im Draft-PR.
Selbstreview ist Implementierungsprüfung; unabhängiges Review und VS-M01 bleiben offen.

Die historischen Produktions-/Manifestbindungen bleiben unverändert und prüfen die
bytegleiche Kopie [plan-vb1.json](../examples/vs1/plan-vb1.json). Der aktuelle Plan
muss ohne seinen E1-Abschnitt genau diesen historischen Inhalt behalten. Negative
Prüfungen weisen geänderte Altslots, fehlenden E1-Abschnitt und andere Archivbytes ab.

Die Windows-Downloadprobe ist mit [vs1_windows_probe.py](../tools/vs1_windows_probe.py)
reproduzierbar: sauberer Lieferhead, Run-ID, frischer Ausgabepfad und gepinnter
Godot-Editor/Cache. Sie startet beide entpackten EXEs direkt und führt native
Bearbeitungs-/Neustart-/Legacy-/Fensterprüfungen gegen deren eingebetteten PCK aus.


Aktive Windows-Messung E1-correction-1, maximaler Fit in V bei 1920 × 1080.
Keine Komfortabnahme; G und sämtliche Fehlfälle bleiben in der vollständigen Matrix.

| Fall | UI 100 % | UI 125 % |
| --- | --- | --- |
| VS01 | 29.29 px | 28.07 px |
| VS02 | 21.49 px | 18.32 px |
| VS07 | 21.52 px | 20.49 px |
| VS08 | 16.12 px | 13.74 px |
| VS09 | 27.48 px | 24.81 px |
| VS10 | 18.64 px | 13.76 px |

## Historische Ergebnisse der Erstlieferung bbc91821

Die folgenden Zahlen und Einordnungen gelten ausschließlich für den historischen
Erststand, nicht für VS-E1-R2. [Dateibindung](../examples/vs1/historical-reference.json).
Zellabstände bei maximalem Fit in V, logischer Client 1920 × 1080. Werte sind
geometrische Messwerte, keine menschlich bestätigten Komfortgrenzen:

| Fall/Format | Hinweise Z/S max. | UI 100 % | UI 125 % |
| --- | --- | --- | --- |
| VS01 · 30 × 30 Mono | 1/1 | 26,86 px | 24,68 px |
| VS02 · 30 × 30 Farbe | 10/14 | 19,06 px | 14,93 px |
| VS03 · 40 × 30 Mono | 7/3 | 25,66 px | 23,18 px |
| VS04 · 40 × 30 Farbe | 26/14 | 19,06 px | 14,93 px |
| VS05 · 30 × 40 Mono | 3/7 | 17,45 px | 15,13 px |
| VS06 · 30 × 40 Farbe | 14/26 | 8,90 px | 4,45 px |
| VS07 · 40 × 40 Mono | 3/2 | 19,70 px | 17,95 px |
| VS08 · 40 × 40 Farbe | 13/14 | 14,30 px | 11,20 px |
| VS09 · 50 × 30 Mono | 7/3 | 25,66 px | 23,18 px |
| VS10 · 50 × 30 Farbe | 24/15 | 18,46 px | 13,76 px |

**40 × 40:** Das kurze Monobeispiel erreicht den ersten 18–20-px-Prüfbereich.
Der belastete Farbfall erreicht ihn bei 1080p in V nicht. Eine allgemeine
40×40-Vollsichtzusage ist daher nicht belegt. Begrenzend ist vor allem die Höhe
nach Reservierung der oberen Hinweise; UI 125 % verschärft dies.

**Rechtecke:** 40 × 30 und 50 × 30 sind bei UI 100 % auch in den ausgewählten
Farbbeispielen geometrisch aussichtsreich. 30 × 40 mit 26 oberen Hinweisen zeigt
einen klaren Problemfall: starke Verkleinerung und Glyphenkollisionen. Das ist
eine Aussage über Format plus Hinweislast, kein unabhängiges Breiten-/Höhenmaximum.

**30 × 30:** Beide Beispiele liegen bei UI 100 % geometrisch oberhalb 18 px;
damit existiert ein technischer Kandidat für die geforderte Mindestkapazität.
UI 125 % drückt das Farbblatt bereits unter 16 px. Die Bedienbarkeit bleibt offen.

**720p:** Schon VS01 fällt in V auf 14,86 / 12,68 px. Lange Farbhinweise führen
zu sehr kleinen Zellen, Kollisionen oder explizitem Nichtpassen. Diese Aufteilung
stützt keine komfortable 30×30-Vollsichtstrategie für 720p. Sie ändert weder den
regulären Mindestclient noch den Inhaltskatalog. **2560 × 1440** verbessert die
Passform erwartungsgemäß; daraus folgt keine neue Mindestauflösung.

**G:** Bietet zusätzliche Rasterfläche durch begrenzte Hinweisreservierung.
Versteckte Hinweisteile bleiben ausdrücklich als Navigationserfordernis
protokolliert. G ist keine vollständige Rätselblattsicht und beweist V nicht.

## Historisches Hinweisbudget und offene Entscheidung

Für die konkret gelieferte Aufteilung beträgt bei 1080p/UI100 die nutzbare Höhe
vor oberen Hinweisen 824 px. Ein 40×40-Raster mit 18 px lässt rechnerisch etwa
fünf 18-px-Spaltenslots zu; 20 px nur einen. Für 30 Zeilen bleiben bei 18 px etwa
15 Slots. Zusätzlich müssen linke Hinweislast, echte Ziffernbreite, Statusstriche
und Controlabstände passen. UI125 reduziert diese Budgets weiter. Diese Formel
ist eine Planungsgrenze; die gemessenen Glyphen und tatsächliche Bedienung bleiben
zusätzliche Kriterien. Erfüllte Hinweise geben keinen Raum frei.

Vorläufig technisch sinnvoll zu erproben: 1080p/UI100, formatabhängiges Hinweisbudget,
40×40 mit kurzen oberen Folgen und breite Rechtecke mit 30 Zeilen. Die vorhandene
Miniatur ist in allen Messungen enthalten. Ihre Entfernung oder andere Layouts
sind nicht geprüft und keine stillen Voraussetzungen dieser Empfehlung.

Nicht untersucht: allgemeine Katalogrepräsentativität, 50×40, Langzeitkomfort,
physische 720p-/1080p-Displays mit allen DPI-Werten. SubViewport-Messungen ersetzen
diese Proben nicht. Motivation/Motivqualität der Transponate bleibt eingeschränkt.
Das leere [Eigentümerprotokoll](../examples/vs1/owner-protocol.json) bleibt maßgeblich:
VS-M01 durch tatsächliche Probe grundsätzlich vor Studienabschluss/Merge;
VS-D01 durch Eigentümerentscheidung vor regulärer Produktumstellung.

Vor Merge außerdem: getrennter Selbstreview, unabhängiges technisches/visuelles
Review des konkreten Heads und passende ausdrückliche Mergefreigabe.
