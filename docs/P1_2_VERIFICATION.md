# P1.2 · Technischer Prüfbericht und offene Eigentümerabnahme

Stand: 23.09.2026 · [Issue #9](https://github.com/venomenon328/picross/issues/9)
auf `feat/5-p1-prototype`, gemeinsamer [Draft-PR #14](https://github.com/venomenon328/picross/pull/14).
Ausgangshead `9a68e7300c2469151638dc3751522bdb63d4c1c4`, Basis
`7f5f945edecdad0c5b86ecbe66ab3d81c7bfedac`. Endgültiger Lieferhead, zugehöriger
Test-Merge, aktuelle CI-Runs und Artefakt-ID werden im PR geführt; dieser Bericht
behauptet keine Prüfung eines noch unbekannten späteren Heads.

Die erste Nacharbeit startete auf `267df8cdb264070ed1f81e500475657be6f27f9d` und behob
[Review R2](https://github.com/venomenon328/picross/pull/14#pullrequestreview-5289320370)
B-01/B-02 sowie D-11 bis D-15. Die Folgearbeit D-16/D-17 startet auf dem durch
[Review R3](https://github.com/venomenon328/picross/pull/14#pullrequestreview-5290145666)
geprüften Head `bd6730d3c0952d8ae74437cd0da9235f2ab0e116`. Alte grüne Läufe beider
Ausgangsstände sind kein Nachweis des neuen Lieferheads.

## Umsetzung und technische Prüfung

- D-07: begrenzter 1600×900-Start, unveränderter 24er Zellabstand bei Resize,
  getrennte UI 100/125 % und Arbeitszoom, Gesamtansicht und Arbeitsgröße.
- D-08: drei logische Einheiten Füll-Inset gegen maximal zwei Einheiten Linienbreite.
  Reale L-/Block-Renderfälle prüfen normale und Fünfergrenzen, jede Farbe, Setz-/Rücknahmevorschau
  und jede Arbeitsstufe. Verdichtete Gesamtansicht ist separat gekennzeichnet.
- D-09: am bestätigten Startfeld eingefrorene Setz-/Rücknahmemodi, gemischte Farben,
  elastische Vorschau und atomare History ohne Wertung. D-15 ersetzt den früheren
  allgemeinen Gegenmarkierungsschutz: linke Setzstriche wandeln X in die aktive Farbe,
  rechte Setzstriche Füllungen in X; Rücknahmestriche bleiben typspezifisch.
- D-10: F-01 Schema 2 / Revision 2, unabhängiges 800×800-SVG mit Segelnähten,
  Takelage, Planken, Bullaugen und dezenten Wasserlinien. Lösung und Hinweise unverändert;
  die ursprünglichen 48 Deduktionsschritte bleiben identisch, nur der Revisionsbezug folgt mit.
- F-02: eigene vierfarbige 40×40-Fixture, 80 überprüfte Farblinienschlüsse / 1600 Zellen.
  F-03: 100×100-Stressfixture, keine Rätselqualitätsbehauptung. Herkunft in
  [F-01](../prototypes/p1/F01_PROOF.md) und [F-02/F-03](../prototypes/p1/F02_PROOF.md).
- D-11/D-12/D-14: keine laufenden Randnummern und keine separate Hinweisansicht.
  Passende Folgen stehen vollständig im Arbeitsbild; der Tooltip bleibt ergänzend.
  Farbzahlen sind Standard, A–D-Suffixe eine sichtbare optionale Darstellung.
- D-16: gemeinsame tokenbasierte Fensterberechnung. Bei Überlauf bleiben vollständige
  zusammenhängende Hinweisabschnitte sichtbar; Markerplatz wird mitberechnet und
  kennzeichnet exakt verborgene Präfixe/Suffixe. Leere/kurze Folgen bleiben direkt
  lesbar. Kleine Spaltenbreiten nutzen kompakte, umrandete Einheiten statt einer
  pauschalen Ausblendung.
- D-17: getrennte normierte Lesepositionen für den horizontalen Zeilen- und vertikalen
  Spaltenhinweisbereich. Mittlere Taste und Hand-Werkzeug werden über echte
  Viewport-Ereignisse geroutet; Ziel/Achse bleiben über Bereichsgrenzen eingefroren.
  Ein sichtbarer Rücksetzknopf stellt beide rasterseitigen Ausschnitte wieder her.
  Raster-Pan/Zoom, Miniatur, Matrix, Preview, History und Abschluss bleiben unabhängig.
- D-13/R2-B-01: 20 streng steigende Arbeitsstufen von 12 bis 72 logischen Einheiten.
  Richtungsregressionen unterhalb/oberhalb der Folge sind automatisiert abgedeckt;
  Zeigeranker, Gesamtansicht und Arbeitsgröße bleiben getrennt.
- R2-B-02: Projekttitel exakt `picross · P1`; UTF-8-/Mojibake-Regressionstest und
  gebundener `project_name`-Eintrag im Produktbericht.
- Gemeinsame Transformation für Zeichnung, Treffer, Hinweise und Miniatur; begrenztes
  Pan, Zeigerzoom, Mitte/Hand und interaktive unkorrigierte eigene Miniatur.
- Pro Blatt eigener Zustand/History innerhalb der Sitzung, echter Abschluss und Album.
  Keine dauerhafte Speicherung, Wertung oder Controllerfunktion.

Der lokale Windows-Prüfweg für D-16/D-17 lief mit den vollständig hashgeprüften offiziellen
Godot-4.7.2-Standardarchiven, isolierten Profilpfaden und temporärer Projektkopie:
Import, 703 Godot-Prüfungen, erwarteter Negativtest Exit 23, begrenzter Start mit
allen drei Fixtures, echte OpenGL-Renderprüfung, Windows-Export und exportierter
Headless- und OpenGL-GUI-Start mit Prüfung des gesamten Fensterrahmens. Der neue Stand
umfasst 45 Python-Tests; unter Windows ist nur der vorhandene Symlink-Test wegen
fehlender Symlinkfähigkeit übersprungen. Linux-CI prüft den Symlinkfall zusätzlich.
Die endgültige commitgebundene Zuordnung
steht im PR.

Die Tests erhalten die bisherigen Regressionen einschließlich F-01/F-02-Logiknachweis.
Die bisherigen Fälle erhalten die vollständige D-15-Startzustandsmatrix, echte direkte
X↔Füllung-UI-Routen, typspezifische Rücknahme/History, monotone Zoomgrenzen und den
exakten UTF-8-Projekttitel. H-01 bis H-04 ergänzen passende/gerade überlaufende/sehr
lange/leere Folgen, mehrstellige Einheiten, beide Marker, vollständige Erreichbarkeit,
F-02-Spalte 22 bei Zellabstand 22/24, F-03 bei 12/18/22/24, A–D aus/an sowie echte
Mausrouten für Mitte/Hand, Bereichswechsel, Freigabe außerhalb, falsche Freigabe,
Escape/Fokusverlust, Grenzanschläge und Zellgestensperre. Zustands-, History-,
Rasterzentrum-/Zoom- und Miniaturinvarianten werden dabei gemeinsam geprüft.

## Tatsächliche Renderkontrolle

`tests/capture.gd` rendert 242 PNGs in echten Godot-SubViewports: logische Flächen
1280×720, 1600×900, 1920×1080 und 2560×1440, jeweils UI/Arbeitszoom
100/100 % und 125/108 %, alle drei Fixtures. Hinzu kommen L-/Blockausschnitte
für alle 20 Zellabstände 12 bis 72, jede Farbe in Vorschau, Neutralisierung,
farbige Hinweise ohne und mit Accessibility-Suffixen, vollständiger F-03-Hover-
Tooltip im Arbeitsbild, Gesamtansicht, drei Abschlüsse und fertige Albumansichten.
Neu sind F-02-Ausschnitte bei 22/24 mit Anfang/Mitte/Ende, unabhängige Achspositionen,
50-%-Accessibility und F-03-Arbeitszoom 50/75/92/100 mit echten Zahlen sowie
Anfang/Mitte/Ende und erhaltener Leseposition nach Raster-Pan. Die Layoutmatrix enthält
zusätzlich F-02 mit A–D und mittleren beidseitigen Markern in allen Flächen/UI-Stufen.
200 Pixelprüfungen bestätigen tatsächliche Füllfarbe und hellen Zwischenraum.

Zusätzlicher nativer Windows-Start: 1600×900 Clientfläche, 1616×939 inklusive
Rahmen, gemeldeter Bildschirm 2560×1440, nutzbare Fläche 2560×1392. Der gesamte
Rahmen liegt darin. Die Zentrierung berücksichtigt den ungleichen Titel-/Seitenrand
gemäß [Godot-DisplayServer](https://docs.godotengine.org/en/stable/classes/class_displayserver.html#class-displayserver-method-window-get-position-with-decorations).
Die tatsächliche Windows-Skalierung wird daraus nicht abgeleitet.

Lokal gerendert mit OpenGL auf der vom Treiber gemeldeten RTX 3070. Für D-16/D-17 visuell geprüft:
Layouts aller vier Flächen, kleinste Fläche in beiden UI-Skalierungen, getrennte
Füllzellen an Fünferkreuzungen, unnummerierte farbige Hinweise, A–D-Umschaltung,
ein-/beidseitige Marker, Anfangs-/Mittel-/Endausschnitte, F-02 bei 92/100 %, F-03 bei
50/75/92/100 %, kompakte A–D-Spalten bei 50 %, erhaltener Zuordnung nach Raster-Pan,
vollständiger F-03-Überlauf-Tooltip im Arbeitsbild sowie relevante große Zoomstufen,
F-01-Motivvergleich und F-02-Farbmotiv. Bei Mindestgröße/UI 125 % scrollt der untere Hilfetext;
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

Vor Übergabe erfolgt ein getrennter Selbstreview des vollständigen Folgediffs gegen
#9/P1 0.6, H-01 bis H-06 und Review R3; R2/B-01/B-02 bleiben Regressionen. Dies
ersetzt weder unabhängiges Review noch Eigentümerabnahme.

**Offen beim Eigentümer vor Gesamt-P1-Merge:** M-01/M-02/M-03/M-06, echte
Maus-/Layout-/Motivprüfung am neuen Artefakt, einschließlich Teilhinweisen, beider
Hinweis-Panachsen und fester Zuordnung bei Raster-Pan/Zoom. Tatsächlicher Head/Artefakt,
Windows-Version, Bildschirmauflösung, Fenster-/Clientfläche und reale Windows-Skalierung
sind dabei zu protokollieren. Die frühere #8-Probe war durchgeführt mit Änderungsbedarf;
keine pauschale Abnahme. Szenarien in der [Anleitung](../prototypes/p1/README.md).
#11/#12 und ihre Speicher-/Integrationsgates bleiben separat. Issues bleiben offen,
PR bleibt Draft; keine Merge-/Releasefähigkeit behauptet.
