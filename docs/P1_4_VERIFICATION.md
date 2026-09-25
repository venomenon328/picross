# P1.4 · Integrierte technische Prüfung und Eigentümerprobe

Stand: 25.09.2026 · [Issue #12](https://github.com/venomenon328/picross/issues/12),
Paketrevision 1.0 · Branch `chore/12-p1-integration-verification` ab
`main@efada37100ddfded50c432e70823b3f0dd446436`.

## Urteil und Nachweisgrenze

Die technische Folge prüft Korrektheit und Fortsetzung des F-03-Stands. Die
Bedienfrage aus #12 bleibt bis zur realen Eigentümerprobe **offen**. Synthetische
Ereignisse, Headless-Zeiten, OpenGL-Bilder und ein exportierter Windows-Start
belegen weder physische Maus-zu-Bildschirm-Latenz noch subjektive Lesbarkeit oder
Hänger auf der Referenzhardware. M-01 bis M-04 und M-06/M-07 sind deshalb hier
ausdrücklich nicht als bestanden markiert. M-05 bleibt nach D-06 nicht anwendbar.

Der konkrete Lieferhead, PR-Test-Merge, `product`-/`docs`-/`preflight`-Runs und das
Windows-Artefakt stehen im Draft-PR zu #12. `product-report.json` im Artefakt
bindet Source-Head, getesteten Checkout, Basis, Run, Baumzustand, relevante
Dateihashes und die separate Integrationsmessung. Der frühere
[P1.3-Bericht](P1_3_VERIFICATION.md) und PR #15/R8 bleiben historische
Nachweise ihrer jeweiligen Stände, keine #12-Abnahme.

## Reproduktion und 500er-Vertrag

Im Repository-Root auf Windows mit Python 3.11+ und dem gepinnten offiziellen
Godot-Cache (oder dessen überprüftem Download):

```powershell
$p1Cache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $p1Cache --output-dir artifacts/p1-product
```

`tools/p14_integration.py` erzeugt die versionierte deterministische Folge ohne
Zufallsquelle. Zehn Besuche liegen um `(2,2)`, `(45,2)`, `(88,2)`, `(2,45)`,
`(45,45)`, `(88,45)`, `(2,88)`, `(45,88)`, `(88,88)` und `(45,65)` in nullbasierten
Rasterkoordinaten. Jeder Besuch hat 50 nummerierte Aktionen. Enthalten sind 409
wirksame Zellgesten, 21 Undo, 10 Redo, 10 Miniatur-Navigationen, 10 Raster-Pans,
20 Zoom-Befehle und 20 individuelle Zeilen-/Spaltenhinweis-Drags. Die letzte
Aktion ist Undo, damit ein echter Redo-Zweig den Neustart überlebt. Ein
Zellstrich zählt genau einmal, gleich wie viele Pointerereignisse/Zellen er hat.
Werkzeug-/Farbauswahl, Aufbau, Assertions, Frames und Neustarts zählen nicht
als weitere Bedienaktionen. Jede Zelleingabe muss wirksam sein; No-ops und
Abbrüche bleiben in den bestehenden gezielten Regressionen außerhalb der 500.

Die Zellen werden über `Viewport.push_input` in der realen `Main`-/`Board`-Szene
mit Down/Move/Up, Achsenbindung und elastischem Weg bearbeitet. Raster-Pan,
Zoom und beide Hinweisachsen verwenden denselben Viewportweg. Die Miniatur
erhält synthetische lokale `_gui_input`-Ereignisse ihres tatsächlichen Controls,
Undo/Redo die `pressed`-Signale ihrer tatsächlichen UI-Buttons. Dies sind
bewusst synthetische UI-Eingaben, keine echte Windows-Mausprobe. Nach jeder
logischen Aktion läuft mindestens ein Prozess-/Renderframe. Die fünf
100er-Abschnitte schließen regulär über `leave_app()` und starten mit demselben
isolierten Profil als echte neue Godot-Prozesse. Ein zusätzlicher letzter Prozess
prüft den gesamten nichttrivialen Stand und den Redo-Befehl. Der bisherige
P1.3-Zwei-Prozess-Roundtrip bleibt separat im Produktweg erhalten.

Der unabhängige Python-Sollrechner wendet die in P1 §5.1 beschriebenen
Startzellmodi auf ganzzahlige Koordinaten an. Er ruft keine Godot-Geste oder
History-Produktionsmethode auf. Für jede Aktionsnummer vergleicht er
Zelldifferenz, Historyende, Cursor, Redo-Element und bleibendes `undo_used`;
am Ende auch vollständige 10.000-Zellen-Matrix und History. Navigation muss
die Zellen und alle nicht adressierten semantischen Hinweispositionen erhalten.
Miniaturziel, Raster-Pan, Zoomrichtung, gültige Ansicht und nur die gestartete
Hinweislinie werden an jedem relevanten Schritt geprüft. Ein absichtlich
verändertes Soll bei einer Aktion und eine auf 499 Einträge verkürzte Spur
müssen beide fehlschlagen. Bei Abweichung nennt der Oracle-Fehler die Nummer,
Aktion und Soll/Ist; `integration/plan.json` und `integration/trace.jsonl` im
technischen Artefakt erlauben die Reproduktion.

## Messung

`integration/summary.json` protokolliert den tatsächlichen Host, OS, verfügbare
CPU-/Engine-/Rendererangaben, logische 1600×900-Fensterfläche, UI 100 %, Zoom
24/26 logische Einheiten, isoliertes Saveprofil und den Eingabetakt. Aufbau und
vier Warmupframes sind getrennt. `dispatch_us` summiert nur synchrone
Event-/Befehlsaufrufe der Aktion; bei Zell-/History-Aktionen sind normale
synchrone Save-Dateizugriffe darin enthalten. `frame_wait_us` weist die
geplanten Frames separat aus. Traceschreiben und Sollassertions sind nicht in
`dispatch_us` enthalten. Median, P95, Maximum und zehn auffällige Dispatches
werden pro Kategorie beziehungsweise gesamt mit Aktionsnummer angegeben.
Das sind keine erfundenen Schwellen, keine GPU-Kennwerte der Referenzhardware,
keine physische Eingabelatenz und kein Ersatz für M-07.

**Lokaler Windows-Vorlauf auf verändertem Arbeitsbaum** (noch keine
commitgebundene CI): Windows 11/AMD64, offizielles Godot 4.7.2,
Headless-Anzeige und isoliertes Profil. Alle 500 Aktionen, zehn entfernte
Bereiche, 809 verschiedene geänderte Zellen, 689 belegte Endzellen,
History 399/Cursor 398 samt Redo bestanden den unabhängigen Vergleich. Der
letzte neue Prozess bestätigte Matrix, History, Redo, View und individuelle
Hinweispositionen. Beide Negativkontrollen schlugen wie vorgesehen fehl.
409 Zellaktionen: Dispatch-Median/P95/Maximum **61,3/83,2/159,3 ms**;
21 Undo **66,2/80,2/81,0 ms**; 10 Redo **66,7/79,6/79,6 ms**.
Zell-Frame-Wartezeit separat **30,3/34,6/54,9 ms**. Die stärksten
Dispatch-Ausreißer sind Aktion 447 mit 159,3 ms und 381 mit 151,9 ms.
Der normale synchrone Save-Pfad ist in diesen Dispatch-Werten enthalten;
physische Eingabe, GPU-Present und menschliches Reaktionsgefühl sind es nicht.

Bei der Voruntersuchung benötigten fünf wiederholte F-03-Redraws auf demselben
Windows-Rechner mit OpenGL ungefähr **591–658 ms**; das Ausblenden des Boards
senkte die gemessenen Frames auf ungefähr **4–17 ms**. Wiederholte Messung
derselben Zeilen-Slotbreite über alle F-03-Reihen war die Ursache; 20
Breitenabfragen kosteten ungefähr **110 ms**. Die eng begrenzte Korrektur
cacht diese immutable Breite pro Session, UI-Skalierung und Schriftgröße.
Der nachfolgende reproduzierbare Headless-Diagnoselauf meldete fünf
Board-Frames von **27,9–28,7 ms**, 20 Breitenabfragen in **44 µs** und fünf
Frames ohne Board zwischen **1,1 und 6,9 ms**. Dieser gezielte Vorher/Nachher-
Befund belegt die behobene technische Redraw-Verletzung; die Besitzerprobe
entscheidet weiterhin über wahrnehmbare Hänger.
Der eingecheckte Nachlauf lässt sich mit der oben genannten gepinnten Godot-
Konsole und einem frischen `P1_TEST_SAVE_ROOT` als
`--headless --path prototypes/p1 --script res://tests/p14_profile.gd`
wiederholen; `P1_PROFILE_OK` enthält die Einzelwerte. Die Voruntersuchung
war eine lokale Diagnose auf der unveränderten Basis, kein CI-Benchmark.

## Technische Nachweismatrix

| Bereich | Prüfweg und erforderliches Ergebnis |
| --- | --- |
| P1/A-01 | F-01/F-02-Definitionen und unveränderte 48/80 Deduktionsschritte, F-03-Stressfixture; bestehende Python-/Godot-Fälle. |
| P1/A-02/A-03 | Gesten, direkte X↔Füllung, typspezifische Neutralisierung, Radierer, elastische Vorschau, atomare History/Redo/Verzweigung; bestehende Regression plus Aktionsoracle. |
| P1/A-04 | Raster-/Miniatur-/Hinweisnavigation, Variante-A-Zeile 12 samt Spaltengegenprobe, semantische Leseposition, Layoutmatrix und echte OpenGL-Bilder; Aktionsfolge prüft Isolation. |
| P1/A-05 | Bestehende Recovery-/Flush-/Resetfälle, alter Zwei-Prozess-Roundtrip und neuer echter Prozessneustart des 500er-Endstands. |
| P1/A-06 | Bestehende Miniatur-/Spoiler-/Abschlussfälle und Renderbilder; F-03 bleibt unkuratierter UI-Testdatensatz. |
| P1/A-07 | Import, erwarteter Negativpfad Exit 23, kontrollierter Start, Export und tatsächlicher exportierter Windows-Start mit Headless und OpenGL. |
| Dokumentation | Python-Tests, `tools/check_docs.py`, vollständiger Basis-zu-Head-`git diff --check`. |

Die vorhandene Render-/Layoutmatrix 1280×720, 1600×900, 1920×1080 und
2560×1440 bei UI 100/125 %, kleinen/großen Arbeitszoomstufen und beiden
Hinweisachsen bleibt Bestandteil von `render-capture`. Technische logische
Flächen sind von realen Windows-DPI-Werten getrennt. Produktcode wird nur bei
einem tatsächlich nachgewiesenen Vertragsbruch korrigiert.

## Windows-Artefakt und Eigentümerprobe

Das technische GitHub-Artefakt enthält ein normales
`picross-p1-windows-x86_64.zip` mit `picross-p1.exe`,
`picross-p1.console.exe`, gegebenenfalls PCK, README und identischem
Produktbericht. Es enthält keine Testsaves, Traces oder Lösungshilfen.
`integration/` und `owner-probe.ps1` liegen **außerhalb** dieses Benutzer-ZIPs
im technischen Artefakt. Aufbewahrung derzeit 14 Tage; Verfügbarkeit bei der
realen Probe erneut prüfen. Hashes/Identität/Start des heruntergeladenen
Lieferartefakts sind im Draft-PR separat zu protokollieren.

Die Probe verwendet ein eigenes TEMP-Profil. Vom Artefaktordner aus nach
Entpacken des Benutzer-ZIPs in PowerShell ausführen; `$probe` während aller
Schritte beibehalten:

```powershell
$exe = (Resolve-Path .\picross-p1.exe).Path
$probe = Join-Path $env:TEMP ('picross-p14-owner-' + [guid]::NewGuid().ToString('N'))
.\owner-probe.ps1 -Exe $exe -Profile $probe -Action Start
```

`-Action Start` startet die sichtbare EXE im isolierten Profil, wartet auf deren
reguläres Schließen und stellt die Prozessumgebung danach wieder her. Dasselbe
Kommando mit demselben `$probe` ist ein **echter neuer EXE-Prozess** für die
Fortsetzung. `-Action Status` zeigt nur die drei F-03-Dateiarten dieses
Testprofils. Für die Recovery-/Fehlerprobe ausschließlich dieses Profil nutzen:

1. **M-01, F-01:** Links setzen und auf Füllung neutralisieren; rechts X setzen
   und neutralisieren; X↔Füllung, 5→12→9 mit Zähler 8→5, Radierer,
   Undo/Redo, Esc, Rand und Abschluss ohne vollständiges Auskreuzen testen.
   Erwartet: nur eingefrorener Zieltyp wird im Strich geändert, ein Strich ist
   ein Undo-Schritt, keine frühe Motivvorschau; F-01-Bild bleibt das bestätigte
   detailliertere Segelboot. Ergebnis: ____ / Abweichung: ____.
2. **M-02, F-02:** A–D, getrennte Nachbarzellen, farbige unnummerierte
   Hinweise und Spalte 22 bei 92/100 % prüfen. Zwei Nachbarzeilen und
   Nachbarspalten unabhängig ziehen; Zeile 12 mit sechs Slots und +1,8
   Slot testen, am Außenanschlag weiter und ohne Richtungswechsel zurück.
   Erwartet: keine Zusatzkennungen, nur Zielreihe bewegt sich, dieselbe `4`
   snappt geometrisch nächst, alle Zahlen erreichbar; X und Cursorbänder
   verdecken nichts. Leuchtturmabschluss beurteilen. Ergebnis: ____ / ____.
3. **M-03, F-03:** Bearbeitete Koordinate notieren: ____; bei 50/75/92/100 %
   echte Hinweise lesen, mehrere Linien getrennt pannen, stark zoomen und
   über Miniatur zur Koordinate zurückkehren. UI 100↔125 % und Resize prüfen.
   Erwartet: Zelle wiedergefunden, Hinweispositionen semantisch stabil,
   Navigation ändert keine Zellen. Ergebnis: ____ / ____.
4. **M-04, Fortsetzung:** In F-03 mehrere unterschiedliche Zellen bearbeiten,
   Undo ausführen, Farbe/Werkzeug, Zoom, Rasterausschnitt und je eine
   Zeilen-/Spaltenleseposition notieren. Über „Beenden“ schließen, obiges
   `Start`-Kommando erneut ausführen. Erwartet: Zellen/Redo/View/Hinweise
   erhalten. Für Recovery nach zwei wirksamen gespeicherten F-03-Aktionen die
   EXE schließen und `-Action HidePrimary` ausführen; neuer `Start` zeigt
   „Backup geladen“, bis zur bestätigten Übernahme bleibt Speichern gesperrt.
   Für Pflicht-Flush/Retry nach erneutem regulärem Schließen `-Action
   BlockSave`, `Start`, F-03 bearbeiten und Album/Beenden versuchen: sichtbarer
   Fehler und gesperrter Übergang. Bei noch offener App in **zweiter PowerShell**
   mit demselben `$probe` `-Action UnblockSave` ausführen, dann Übergang
   wiederholen: Erfolg. Einzelreset in der App bestätigen; andere Blätter
   bleiben erhalten. Ergebnis je Teil: ____ / ____ / ____ / ____.
5. **M-06:** Start-Client/äußeren Rahmen und verfügbaren Arbeitsbereich bei
   1080p/1440p soweit vorhanden messen; Resize/Maximieren, UI 100/125 %,
   Werkzeug-/Hinweis-/Miniaturzugriff prüfen. Erwartet: 1920×1080-Ziel oder
   begrenzter Fallback, stabile Zellen bei reinem Resize. Ergebnis: ____ / ____.
6. **M-07:** F-03 wiederholt an entfernten Stellen bearbeiten, Raster/Hinweise
   pannen, Zoom/Miniatur verwenden. Erwartet: keine verlorenen/falschen
   Aktionen oder wahrnehmbaren Hänger auf der Referenzhardware. Reaktionsgefühl
   und konkrete Abweichung getrennt notieren. Ergebnis: ____ / ____.

**Protokoll vor der Probe:** Head/Artefakt/ZIP-Hash: ____; Windows-Version: ____;
Bildschirmauflösung: ____; Arbeitsbereich: ____; Client-/Rahmenfläche: ____;
tatsächliche Windows-Anzeigeskalierung: ____; UI-Skalierung: ____;
Arbeitszoom: ____; Maus: ____; Startzeit/Ende: ____.
Keine dieser Angaben wird aus Screenshotmaßen oder CI geschätzt. Die frühere
positive F-01-Stil-/Abstraktionsrückmeldung bleibt erhalten, ist aber keine
pauschale M-01-Abnahme.

## Offene Gates

E-01/E-02/E-03 brauchen die commitgebundenen erfolgreichen product/docs/preflight-
Läufe, den geprüften Download und den tatsächlichen Windows-Start. E-04 bleibt
bis zu den obigen Eigentümerfeldern offen. E-05 kann erst danach die zentrale
Bedienfrage abschließend beantworten. E-06 verlangt einen gesonderten
Integrationsreview; dieser Bericht oder ein Selbstreview ist keine unabhängige
Zweitprüfung. Ohne passende Abnahme und Freigabe kein Merge, Issueschluss oder
Release.
