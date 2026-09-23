# P1.2 · Technischer Prüfbericht und offene Eigentümerabnahme

Stand: 23.09.2026 · [Issue #9](https://github.com/venomenon328/picross/issues/9)
auf `feat/5-p1-prototype`, gemeinsamer [Draft-PR #14](https://github.com/venomenon328/picross/pull/14).
Ausgangshead `9a68e7300c2469151638dc3751522bdb63d4c1c4`, Basis
`7f5f945edecdad0c5b86ecbe66ab3d81c7bfedac`. Endgültiger Lieferhead, zugehöriger
Test-Merge, aktuelle CI-Runs und Artefakt-ID werden im PR geführt; dieser Bericht
behauptet keine Prüfung eines noch unbekannten späteren Heads.

## Umsetzung und technische Prüfung

- D-07: begrenzter 1600×900-Start, unveränderter 24er Zellabstand bei Resize,
  getrennte UI 100/125 % und Arbeitszoom 75/100/150/200 %, Gesamtansicht und Arbeitsgröße.
- D-08: drei logische Einheiten Füll-Inset gegen maximal zwei Einheiten Linienbreite.
  Reale L-/Block-Renderfälle prüfen normale und Fünfergrenzen, jede Farbe, Setz-/Rücknahmevorschau
  und jede Arbeitsstufe. Verdichtete Gesamtansicht ist separat gekennzeichnet.
- D-09: am bestätigten Startfeld eingefrorene Setz-/Rücknahmemodi, gemischte Farben,
  geschützte Gegenmarkierungen, elastische Vorschau, atomare History ohne Wertung.
- D-10: F-01 Schema 2 / Revision 2, unabhängiges 800×800-SVG mit Segelnähten,
  Takelage, Planken, Bullaugen und dezenten Wasserlinien. Lösung und Hinweise unverändert;
  die ursprünglichen 48 Deduktionsschritte bleiben identisch, nur der Revisionsbezug folgt mit.
- F-02: eigene vierfarbige 40×40-Fixture, 80 überprüfte Farblinienschlüsse / 1600 Zellen.
  F-03: 100×100-Stressfixture, keine Rätselqualitätsbehauptung. Herkunft in
  [F-01](../prototypes/p1/F01_PROOF.md) und [F-02/F-03](../prototypes/p1/F02_PROOF.md).
- Gemeinsame Transformation für Zeichnung, Treffer, ganze Linienhinweise und Miniatur;
  begrenztes Pan, Zeigerzoom, Mitte/Hand und interaktive unkorrigierte eigene Miniatur.
  Vollständige Maus-Fokusansicht langer Hinweise lässt die Miniatur sichtbar.
- Pro Blatt eigener Zustand/History innerhalb der Sitzung, echter Abschluss und Album.
  Keine dauerhafte Speicherung, Wertung oder Controllerfunktion.

Der lokale Windows-Prüfweg lief mit den vollständig hashgeprüften offiziellen
Godot-4.7.2-Standardarchiven, isolierten Profilpfaden und temporärer Projektkopie:
Import, 524 Godot-Prüfungen, erwarteter Negativtest Exit 23, begrenzter Start mit
allen drei Fixtures, echte OpenGL-Renderprüfung, Windows-Export und exportierter
Headless- und OpenGL-GUI-Start mit Prüfung des gesamten Fensterrahmens. 43 Python-Tests; unter Windows ist nur der vorhandene Symlink-Test
wegen fehlender Symlinkfähigkeit übersprungen. Linux-CI prüft diesen zusätzlich.

Die Tests erhalten die bisherigen Regressionen; gezielt geändert wurden die
überholte pixelidentische Reveal-Bindung, der rechte Start auf vorhandenem Kreuz
und die Annahme eines stets vollständig eingepassten Rasters. Neue Tests ergänzen
alle D-09-Startzustände/Farben, echte Palette-/Viewport-Routen, Navigation ohne
Zell-/Historyänderung, Größen-/Skalierungsfälle und farbige Abschluss-Negativfälle.

## Tatsächliche Renderkontrolle

`tests/capture.gd` rendert 69 PNGs in echten Godot-SubViewports: logische Flächen
1280×720, 1600×900, 1920×1080 und 2560×1440, jeweils UI/Arbeitszoom
100/100 % und 125/150 %, alle drei Fixtures. Hinzu kommen L-/Blockausschnitte
für 18/24/36/48er Zellabstand, jede Farbe in Vorschau, Neutralisierung, vollständige
F-03-Hinweise, Gesamtansicht, drei Abschlüsse und fertige Albumansichten.
40 Pixelprüfungen bestätigen tatsächliche Füllfarbe und hellen Zwischenraum.

Zusätzlicher nativer Windows-Start: 1600×900 Clientfläche, 1616×939 inklusive
Rahmen, gemeldeter Bildschirm 2560×1440, nutzbare Fläche 2560×1392. Der gesamte
Rahmen liegt darin. Die Zentrierung berücksichtigt den ungleichen Titel-/Seitenrand
gemäß [Godot-DisplayServer](https://docs.godotengine.org/en/stable/classes/class_displayserver.html#class-displayserver-method-window-get-position-with-decorations).
Die tatsächliche Windows-Skalierung wird daraus nicht abgeleitet.

Lokal gerendert mit OpenGL auf der vom Treiber gemeldeten RTX 3070. Visuell geprüft:
Layouts aller vier Flächen, kleinste Fläche in beiden UI-Skalierungen, getrennte
Füllzellen an Fünferkreuzungen, vollständige lange Hinweise, F-01-Motivvergleich
und F-02-Farbmotiv. Bei Mindestgröße/UI 125 % scrollt der untere Hilfetext;
Werkzeuge und Hinweiszugriff bleiben zugänglich, Miniatur fest sichtbar.
Kleine Raster behalten ruhige Ränder, die Hinweise bleiben am Raster zugeordnet.

Die Renderkontrolle entdeckte und korrigierte vor Lieferung eine zu kurz gehaltene
Texturreferenz (weißes Abschlussbild) und unnötig verdichtete kurze Spaltenhinweise.
Die PNGs und `render-report.json` einschließlich Renderer, logischer Fläche und
Maßstäben liegen mit Logs und Hashes im Produktartefakt. Kein Headless-Screenshot,
kein nachgebautes Mock, keine Behauptung physischer Windows-DPI-Verhältnisse.

## Auslieferungsprüfung und Grenzen

Der Produkt-Harness führt Renderprüfung auch in Linux-CI über Xvfb/Mesa aus;
`product-report.json` bindet Quellhead, getesteten Checkout, Basis, CI-Lauf,
geprüfte Archive, EXE-Paar und Bildhashes. `product`, `docs` und `preflight` müssen
für den finalen Stand tatsächlich erfolgreich sein; konkrete Ergebnisse im PR.
ZIP enthält sämtliche Startdateien, Anleitung und Bericht. Tests/Prüfzertifikate
werden vom Spiel-Export ausgeschlossen. Kein Installer, Release, Dienst oder Merge.

Vor Übergabe erfolgt ein getrennter Selbstreview des vollständigen Diffs gegen
#9/P1 0.4. Dies ersetzt weder unabhängiges Review noch Eigentümerabnahme.

**Offen beim Eigentümer vor Gesamt-P1-Merge:** M-01/M-02/M-03/M-06, echte
Maus-/Layout-/Motivprüfung am neuen Artefakt. Tatsächlicher Head/Artefakt,
Windows-Version, Bildschirmauflösung, Fenster-/Clientfläche und reale Windows-Skalierung
sind dabei zu protokollieren. Die frühere #8-Probe war durchgeführt mit Änderungsbedarf;
keine pauschale Abnahme. Szenarien in der [Anleitung](../prototypes/p1/README.md).
#11/#12 und ihre Speicher-/Integrationsgates bleiben separat. Issues bleiben offen,
PR bleibt Draft; keine Merge-/Releasefähigkeit behauptet.
