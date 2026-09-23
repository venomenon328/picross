# P1.2 · Technischer Prüfbericht und offene Eigentümerabnahme

Stand: 23.09.2026 · [Issue #9](https://github.com/venomenon328/picross/issues/9)
auf `feat/5-p1-prototype`, gemeinsamer [Draft-PR #14](https://github.com/venomenon328/picross/pull/14).
Diese Grundlagenkorrektur D-18 bis D-22 startet auf
`b19f14e0f8c7a599bd04799872ccea3b7ceadc6c`, Basis
`7f5f945edecdad0c5b86ecbe66ab3d81c7bfedac`, und arbeitet
[Review R4](https://github.com/venomenon328/picross/pull/14#pullrequestreview-5291782095)
nach. Der endgültige Lieferhead, Test-Merge, aktuelle CI-Läufe und das commitgebundene
Windows-Artefakt werden im PR protokolliert; ältere grüne Läufe belegen diesen Stand nicht.

## Liefervertrag J-01 bis J-06

- **J-01 / D-18:** Am Raster erscheinen nur vollständige einzeilige Zahlen in ihrer
  Rätselfarbe. A–D bleiben Kennungen der Bedienpalette und interner Farbdaten, sind aber
  weder Zusatz an Hinweisen noch umschaltbare Darstellungsoption. Laufende Zeilen- oder
  Spaltennummern, gestapelte Ziffern und Kompaktkästchen bleiben ausgeschlossen.
- **J-02 / D-19:** Alle Zeilen verwenden ein gemeinsames waagerechtes Slotraster, alle
  Spalten ein gemeinsames senkrechtes. Slotgröße und rasterseitige Kante werden je
  Orientierung einmal bestimmt. Ein Überlauffenster enthält nur ganze Tokens und feste
  Randmarker; Ziehen rastet in ganzzahligen Slots ein.
- **J-03 / D-20:** Der Leseschritt wird für jede konkrete Zeile und Spalte separat
  gespeichert. Gesten frieren Orientierung, Linie und Achse am Start ein. Nur die
  angefasste Linie ändert sich; Nachbarn, Raster, Zellen, Miniatur und History bleiben
  unverändert. Reset und Blattwechsel normalisieren alle Einzelpositionen.
- **J-04 / D-21:** Die gewünschte Start-Clientfläche ist 1920×1080, sofern der gesamte
  dekorierte Rahmen in den nutzbaren Arbeitsbereich passt; sonst wird begrenzt. UI-Skalierung,
  Arbeitszoom und Fenstergröße bleiben getrennt, kleine Rätsel werden durch Resize nicht
  künstlich vergrößert.
- **J-05 / D-22:** F-02 erhält bei unverändertem 40×40-Lösungsraster ein eigenständiges
  detailliertes 800×800-Leuchtturmbild mit Sonne, Laterne, Turmbändern, Fenstern, Tür und
  Wasserlinien. Die klare Kontur- und Flächenbehandlung folgt der bestätigten F-01-Referenz.
  Nur F-02-Daten-/Proofrevision wechseln gemeinsam von 1 auf 2; die 80 Deduktionsschritte,
  1600 Zellen, Hinweise und Lösung bleiben inhaltlich gleich. F-01-Dateien und ihre 48
  Deduktionsschritte werden nicht verändert.
- **J-06:** Spezifikation 0.7, Designkonzept, Projektprofil, Anleitung, Proofhinweis,
  automatisierte Fälle, echte Renderfälle und Produktbericht bilden denselben Vertrag ab.
  #11/#12, Layout-/Zieldesignphase, neue Farbauswahl, Hintergründe und umfassende
  Sidebar-Bereinigung bleiben außerhalb des Pakets.

## Automatisierte und echte Eingabeprüfung

Die Godot-Suite umfasst 838 bestandene Prüfungen. Neben allen bisherigen
F-01/F-02-Logik-, Setz-/Rücknahme-, X↔Füllung-, Preview-, History-, Abschluss-,
Album-, Miniatur-, Pan-, Zoom- und Resize-Regressionen prüft sie insbesondere:

- vollständige ein- und mehrstellige Farbzahlen ohne Suffix-Schalter;
- identische Slotursprünge/-abstände für benachbarte Linien und exakte
  Anfangs-/Mittel-/Endfenster einschließlich Präfix-/Suffixmarker;
- unabhängige Schritte mehrerer konkreter F-02- und F-03-Zeilen/Spalten;
- echte Mittel-/Hand-Ereignisse, Subslotbewegung, Slotgrenze, Diagonalbewegung,
  Linien-/Achsenfreeze, Bereichsübertritt, richtige/falsche Freigabe, Freigabe außerhalb,
  Escape, Fokusverlust, passende kurze Linie und gleichzeitig gesperrte Zellgeste;
- F-02-Spalte 22 bei Zellabstand 22/24 sowie F-03 bei 50/75/92/100 %;
- 1920×1080-Startziel und begrenzten Fallback einschließlich Fensterdekoration;
- F-02 Schema 2 / Revision 2 / 800×800-SVG bei unverändert erfolgreichem
  Lösung-/Zertifikatsnachweis und unveränderter F-01-Referenz.

Die Python-Suite umfasst 45 Fälle: 44 bestanden lokal, nur der vorhandene
Symlinktest ist unter dieser Windows-Umgebung mangels Symlinkfähigkeit übersprungen;
Linux-CI führt ihn aus. Sie prüft Dokumentstruktur, beide Rätselzertifikate,
Produkt-/Preflight-Härtung, exakten UTF-8-Projekttitel sowie positive und bewusst
negative Werkzeugpfade. Der erwartete Produkt-Negativtest muss weiterhin mit Exit 23
aus dem beabsichtigten Grund scheitern.

## Tatsächliche Renderkontrolle

`tests/capture.gd` rendert 249 PNGs in echten Godot-SubViewports. Die Matrix enthält
1280×720, 1600×900, 1920×1080 und 2560×1440, jeweils UI 100/125 %, alle drei Fixtures,
F-02 und F-03 mit voneinander abweichenden Zeilen-/Spaltenpositionen sowie F-02/F-03
bei den relevanten Arbeitszoomstufen. Weitere Fälle zeigen Anfang/Mitte/Ende,
ein-/beidseitige Marker, vollständige Hoverhinweise, alle 20 Zellabstände 12 bis 72,
jede Farbe und Setz-/Rücknahmevorschau, Gesamtansicht, Abschlüsse und Albumansichten.
200 Pixelprüfungen bestätigen tatsächliche Füllfarbe und hellen Zwischenraum.

Der lokale echte OpenGL-Lauf meldete Godot 4.7.2-stable und eine RTX 3070. Visuell
geprüft wurden die vier Flächen in beiden UI-Skalierungen, das gemeinsame Slotraster,
unterschiedliche Positionen benachbarter F-03-Linien auch bei 1920×1080/2560×1440,
F-02-Spalte 22, F-03 bei 50/75/92/100 %, vollständige farbige Zahlen ohne
Zusatzkennung, Marker/Tooltip, getrennte Füllzellen an Fünfergrenzen, die unveränderte
F-01-Segelbootreferenz sowie F-02-Raster, verfeinertes Leuchtturmbild und Albumansicht.
Bei 1280×720/UI 125 % scrollt nur der untere Hilfebereich; Werkzeuge, Hinweise und
Miniatur bleiben erreichbar. Kleine Raster behalten ruhige Ränder.

Der native Windows-Start meldete auf dem 2560×1440-Bildschirm eine nutzbare Fläche
2560×1392, die gewünschte Clientfläche 1920×1080 und den vollständigen dekorierten
Rahmen 1936×1119 innerhalb dieses Arbeitsbereichs. Seine Position lag auf dem zweiten
Monitor bei `(2872, 132)`; aus diesen technischen Angaben wird keine physische
Windows-Anzeigeskalierung abgeleitet.

Der vollständige Produktweg arbeitet mit gepinnten, vollständig hashgeprüften offiziellen
Godot-4.7.2-Archiven in einer temporären Projektkopie und isolierten Profilpfaden. Er
umfasst Import, Godot-Suite, Negativtest, nativen begrenzten Start, echte Renderprüfung,
Windows-Export sowie exportierten Headless- und OpenGL-GUI-Start. `product-report.json`
bindet Quellhead, getesteten Checkout/Test-Merge, Basis, CI-Lauf, Engine-/Archivhashes,
EXE-Paar, Quell-/Fixture-/Artworkhashes, Renderbilder und Phasen. Das neue ZIP wird erst
nach dem Push aus dem erfolgreichen `product`-Lauf als commitgebundener Nachweis benannt.

## Selbstreview und Grenzen

Nach Implementierung und vollständigem lokalen Produktlauf wurde der gesamte Diff ab
`b19f14e0f8c7a599bd04799872ccea3b7ceadc6c` getrennt gegen J-01 bis J-06,
Scopegrenzen, F-01-Unverändertheit, F-02-Logikgleichheit, Geheimnisse, Whitespace und
Artefaktinhalt geprüft. Ergebnis: keine unbeauftragte Produktfunktion, keine Änderung
der F-01-Dateien, bei F-02 außer SVG und gemeinsamem Revisionsfeld bytegleiche
Logik-/Proofdaten, keine erkannten Geheimnismuster und ein sauberer `git diff --check`.
Tatsächlicher Lieferhead und commitgebundene Nachweise werden in #9, #5 und PR #14
protokolliert. Dieses Selbstreview ersetzt kein unabhängiges Review.

**Offen beim Eigentümer vor Gesamt-P1-Merge:** M-01/M-02/M-03/M-06 und die echte
Maus-/Layout-/Motivprüfung am neuen Artefakt. Dabei sind tatsächlicher Head/Artefakt,
Windows-Version, Bildschirmauflösung, Fenster- und Clientfläche, reale Windows-Skalierung,
Maus sowie Ergebnis/Abweichung je Szenario zu erfassen. Die positive F-01-Teilbestätigung
bleibt erhalten; alle übrigen Eigentümerabnahmen bleiben offen. Technische Screenshots
und synthetische Ereignisse ersetzen diese Probe nicht. #11/#12 bleiben separat,
PR #14 bleibt Draft; nichts wird gemergt, geschlossen oder als Release bezeichnet.
