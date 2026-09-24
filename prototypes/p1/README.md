# P1.3 · Lokalen Arbeitsstand fortsetzen

Zwischenstand zu [Issue #11](https://github.com/venomenon328/picross/issues/11)
auf eigenem Draft-PR gegen `main`. F-01 (20×20),
F-02 (40×40, vier Farben) und F-03 (100×100, ausdrücklich UI-Testdatensatz)
sind direkt zugänglich. Review R2/B-01/B-02 und D-07 bis D-27 sind in diesem Stand
technisch nachgearbeitet. Hinweise bleiben vollständige einzeilige farbige Zahlen ohne
Zusatzkennungen. Alle Zeilen beziehungsweise Spalten teilen sich je ein festes
Hinweisraster; jede konkrete Linie behält darin ihre eigene eingerastete Leseposition.
Keine Wertung oder Fehlerhilfe. Albumwechsel und echter App-Neustart erhalten den
eigenen Stand samt Undo/Redo, Rasteransicht, Werkzeug, Farbe und individuellen
Hinweis-Lesepositionen pro Blatt.

## Windows starten

Das vollständige ZIP entpacken und `picross-p1.exe` starten. Keine Godot-Installation
nötig. `picross-p1.console.exe` zeigt technische Ausgaben. Dies ist eine unsignierte
Debug-Spielprobe, kein Release/Installer. Die Quellcommitkennung steht im beigefügten
README.txt; `product-report.json` bindet Head, getesteten Checkout/Test-Merge, Basis,
CI-Lauf, Engine-/Archivhashes, EXE-Hashes und Prüfphasen. Artefaktlink im PR.

Godot löst `user://p1/saves/` im projektbezogenen User-Data-Verzeichnis auf.
Unter Windows liegt dieses standardmäßig unter
`%APPDATA%\Godot\app_userdata\picross · P1\p1\saves\` (bei benutzerdefiniertem
Godot-Datenpfad entsprechend dort). Die drei bekannten Fixture-IDs ergeben
`f01.json`, `f02.json`, `f03.json` mit gleichnamigen `f01.bak`/`f01.tmp` usw.
Tests verwenden nur eigene temporäre Profile; das ZIP enthält keine
Spielstände.

Fehlendes oder beschädigtes Primary mit gültigem Backup wird sichtbar als Recovery geladen;
normales Speichern bleibt bis zur bewussten Übernahme gesperrt.
„Backup zum Speichern übernehmen“ fragt vor dem Ersetzen des Primary nach.
Bei gültigem Primary und defektem Backup bleibt der Primärstand lesbar;
„Backup erneuern“ fragt vor dem Ersatz des beschädigten Backups nach.
Ohne gültige Fassung erscheint ein Fehler. „Arbeitsstand zurücksetzen“ fragt
ebenfalls nach und entfernt ausschließlich Primary, Backup und Temp des
ausgewählten Blatts. Die zwei anderen Blätter bleiben erhalten.
Scheitert ein verpflichtender Save, bleibt die aktuelle Ansicht offen und zeigt
den Fehler. Album, Blattwechsel und reguläres Beenden gelingen nach einem
erfolgreichen Retry.

Startziel: 1920×1080 Clientfläche, auf den verfügbaren Arbeitsbereich einschließlich Fensterrahmen
begrenzt. Unter 1280×720 erscheint eine verständliche Meldung. Vergrößern des Fensters
zeigt mehr Raster oder ruhige Ränder; es vergrößert die Arbeitszellen nicht automatisch.

## Bearbeiten und zurücknehmen

- Links: unbekannt → aktive Farbe, Füllung → unbekannt, X → aktive Farbe.
- Rechts: unbekannt → X, X → unbekannt, Füllung → X.
- Ein linker Setzstrich wandelt unbekannte/X-Zellen in die beim Start aktive Farbe;
  ein rechter Setzstrich unbekannte/gefüllte Zellen in X. Ein auf Füllung gestarteter
  linker Rücknahmestrich entfernt nur Füllungen, ein auf X gestarteter rechter nur X.
  Eine andersfarbige Füllung wird links neutralisiert, nicht direkt umgefärbt.
- Modus und Farbe stehen für die gesamte Geste fest. Achse nach erster eindeutiger
  Bewegung fest; bei diagonalem Gleichstand zunächst nur die Startzelle.
- Zurückziehen verkürzt die Vorschau. 5→12→9 übernimmt nur 5–9 als eine Aktion.
  Überqueren des Starts ändert die Achse nicht. Kein mehrfaches Umschalten.
- Ein kleiner Live-Zähler zeigt während linker/rechter Zellgesten die gesamte
  geometrische Länge inklusive beider Endfelder: 5→12 zeigt 8, zurück auf 9 zeigt 5.
  Vorbelegte oder übersprungene Zellen zählen mit; bei Abbruch/Drop verschwindet er.
- Außerhalb des sichtbaren Rasters bleibt der letzte gültige Endpunkt stehen.
  Esc, Fokusverlust oder Albumwechsel verwerfen den Strich. Kein Auto-Scrollen.
- Radierer links neutralisiert alle Markierungen; rechts gilt die Kreuzregel.
  Rückgängig/Wiederholen stellt ganze Striche mit exakten Vorzuständen wieder her.
- F-02/F-03: Farbe per Palette A–D wählen. Diese Kennungen gehören ausschließlich zur
  Bedienpalette; Lösungshinweise zeigen nur die vollständige Zahl in ihrer Farbe.
  Gleiche Farbblöcke brauchen Abstand; verschiedene dürfen angrenzen.
- Etwas größere Füllflächen bleiben durch Zwischenräume und Rasterlinien getrennt.
  Die gültige Cursorzeile und -spalte sind im Grid dezent hinterlegt. Angeschnittene
  X und Preview-X werden am sichtbaren Rasterrand geometrisch abgeschnitten.

## Navigieren und Hinweise lesen

- Mausrad: Zoom am Zeiger. Sichtbare −/+ Knöpfe: Zoom um die Ansichtsmitte.
  20 monotone Arbeitsstufen reichen von 50 bis 300 % (12 bis 72 logische Einheiten),
  rund um 100 % in Zwei-Einheiten-Schritten. Herauszoomen vergrößert nie und
  Hineinzoomen verkleinert nie, auch nicht aus einer Gesamtansicht außerhalb der Folge.
- Mittlere Taste oder Hand-Werkzeug links im Raster: Rasteransicht verschieben.
  Gesamtansicht passt das komplette Raster ein; Arbeitsgröße stellt 100 % wieder her.
- Eigene Miniatur: Klick/Ziehen versetzt den Ausschnitt. Der doppelte Rahmen markiert
  die sichtbare Fläche. Helle Flächen sind unbekannt, Punkte leer, Farben eigene Füllungen
  einschließlich möglicher Fehler und derselben Strichvorschau.
- Während Zellgesten sind Zoom und Navigation gesperrt. Navigation ändert keine Zellen
  oder Undo-Historie. Pro Blatt bleiben Bearbeitung/History und Ansicht beim
  Blattwechsel und regulären App-Neustart erhalten.
- Am Raster stehen ausschließlich die Lösungshinweise, ohne laufende Zeilen-/
  Spaltennummern oder A–D-Zusätze. „–“ ist eine leere Linie. Alle Zeilen nutzen dieselben
  waagerechten Slots, alle Spalten dieselben senkrechten Slots; das rasternächste Ende
  liegt an derselben Kante. Bei Überlauf bleibt ein zusammenhängender Ausschnitt
  vollständiger Zahlen sichtbar. `…` links/oben markiert einen verborgenen Anfang,
  rechts/unten ein verborgenes Ende; mittlere Ausschnitte dürfen beide Marker haben.
  Zahlen werden nie geteilt; bestätigte Lesepositionen liegen in ganzen Slots.
- Mittlere Taste oder Hand-Werkzeug links im oberen Hinweisbereich verschiebt nur die
  beim Start angefasste Spaltenfolge vertikal. Dieselbe Geste im linken Hinweisbereich
  verschiebt nur die angefasste Zeilenfolge horizontal. Während des Ziehens folgt
  sie der Maus flüssig zwischen den Slots. `…` zeigt dabei auf der jeweiligen Seite
  die aktuell verborgenen Zahlen an; erst beim Loslassen rastet die Folge anhand
  der zuvor sichtbaren Zahlen auf die geometrisch nächste gültige Slotlage ein.
  Ein Markerwechsel verschiebt Zahlen dabei nicht zusätzlich. Nachbarlinien
  behalten ihre eigene Position. Ziel, Linie und Achse bleiben auch beim Überqueren anderer Bereiche
  eingefroren. Raster, Miniatur, Zellen und Undo/Redo ändern sich nicht. `Esc` oder
  Fokusverlust oder ein regulärer Übergang verwirft den temporären Versatz.
  „Hinweise rasterseitig ausrichten“ stellt
  alle Linien auf ihren rasterseitigen Standardausschnitt zurück.
- Darüberfahren einer gekürzten Folge zeigt weiterhin den vollständigen farbigen
  Hinweis mit Umbruch direkt über dem Arbeitsbild. Das ist ein Zusatzweg; Anfang,
  Mitte und Ende bleiben auch durch Hinweis-Panning erreichbar. Eine separate
  Hinweisansicht gibt es nicht.
- UI 100/125 % vergrößert Oberfläche und Hinweise unabhängig vom Arbeitszoom.
  Geänderte Slotkapazitäten erhalten je konkrete Folge die semantische Leseposition:
  äußerer Anfang und rasterseitiges Ende bleiben am gewählten Rand verankert,
  mittlere Ausschnitte behalten den gelesenen Tokenbereich mit größtmöglicher
  Überdeckung. Das gilt auch bei Arbeitszoom und Resize; alle Zustände bleiben
  in ganzen Slots eingerastet.
  Bei 1280×720/125 % ist der untere Hilfetext über die Seitenleiste scrollbar;
  Werkzeuge und Hinweiszugriff bleiben erreichbar, die Miniatur bleibt fest sichtbar.

Für den Abschluss genügen alle richtigen Füllungen ohne Zusatzfüllungen.
Hintergrund muss nicht vollständig ausgekreuzt sein. Name und Ergebnisbild erscheinen
erst nach bestätigtem Abschluss. F-01 zeigt das ursprüngliche Raster neben einer
detaillierteren Illustration desselben Motivs. F-02 zeigt einen verfeinerten Leuchtturm
mit Sonne, Laterne, Turmbändern, Fenstern, Tür und Wasserlinien im klaren F-01-Stil.
F-03 bleibt auch danach als Test gekennzeichnet.

## Erneute Eigentümerprobe · offen vor Gesamt-P1-Merge

Die frühere #8-Probe ist mit Änderungsbedarf ausgewertet, keine pauschale Abnahme.
Am neuen Artefakt mit echter Maus prüfen und Ergebnisse einzeln protokollieren:

1. M-01: F-01 setzen/neutralisieren, X↔Füllung direkt umwandeln, 5→12→9 und
   Startüberquerung, typspezifische Rücknahmestriche, Radierer, Undo/Redo, Rand,
   falsche Tastenfreigabe, Esc und Fokusverlust. Tatsächlich lösen ohne Auskreuzpflicht;
   den Live-Zähler bei 5→12→9 unabhängig von Vorbelegung als 8→5 lesen und
   abgeschnittene X an Viewporträndern prüfen. Detailbild und Raster als dasselbe
   Motiv beurteilen.
2. M-02: F-02, alle Farben A–D, direkte Umwandlung und farbige Hinweise ohne
   Zusatzkennungen prüfen. Spalte 22 bei etwa 92/100 % prüfen: Beim Kürzen bleiben
   vollständige restliche Zahlen sichtbar. Je zwei benachbarte Spalten und Zeilen
   auf unterschiedliche Anfangs-/Mittel-/Endpositionen pannen; gemeinsames Raster,
   flüssige Zwischenpositionen während des Ziehens, Slot-Einrasten erst beim Drop,
   Abbruch ohne Positionsänderung, unveränderte Nachbarn, feste Linie und
   ergänzenden Hover prüfen.
   Drei angrenzende Füllungen an einer Fünfergrenze müssen einzeln erkennbar sein,
   auch in Vorschau und bei den relevanten Arbeitszoomstufen. Die dezenten
   Cursorbänder dürfen X, Farben und Rasterlinien nicht verdecken. Anschließend lösen und
   Raster/Ergebnisbild als denselben verfeinerten Leuchtturm beurteilen.
3. M-03: F-03 eine notierte Koordinate bearbeiten und bei 50/75/92/100 % echte
   Hinweiszahlen ohne Hover lesen. Mehrere konkrete Zeilen/Spalten unabhängig pannen;
   ihre Anfangs-/Endanker und mittleren Tokenbereiche anschließend bei 50↔100 %,
   UI 100↔125 % und Resize vergleichen; die Lesepositionen müssen semantisch stabil
   und eingerastet bleiben. Danach das
   Raster stark zoomen/verschieben und per Miniatur/Koordinaten wiederfinden. Die
   Linienzuordnung und einzelnen Lesepositionen dürfen sich durch reines Raster-Pan
   nicht ändern. Keine verlorenen Aktionen, Richtungsumkehr beim Zoom oder Hänger.
4. M-06: 1920×1080-Clientstart beziehungsweise begrenzten Fallback,
   Vergrößern/Maximieren, 1080p/1440p soweit verfügbar,
   UI 100/125 %, feste Zellgröße bei reinem Resize, erreichbare Werkzeuge/Hinweise.

Protokollfelder: tatsächlicher Head/Artefakt, Windows-Version, Bildschirmauflösung,
Fenster- und Clientfläche, tatsächliche Windows-Anzeigeskalierung, Maus, Szenario,
Ergebnis/Abweichung. Nicht aus Screenshotabmessungen ableiten. Referenz aus früheren
Angaben: Windows 11, 2560×1440, Ryzen 7 5800X, RTX 3070. Die reale Skalierung bleibt
unbekannt. Technische Renderflächen und synthetische Events ersetzen diese Abnahme nicht.

500-Aktionen-Gesamtintegration (#12), Wertung,
Controller/Tastatur und Release bleiben außerhalb dieser Lieferung. Escape ist
weiterhin Mausgestenabbruch. Kein Merge durch diese Übergabe.

## Technische Reproduktion

M-04 bleibt beim Eigentümer offen: Am commitgebundenen Windows-ZIP F-03 bearbeiten,
Undo ausführen, Werkzeug/Farbe und Raster-/Hinweisansicht verändern, über die
Beenden-Schaltfläche oder Alt-F4 schließen, die EXE als neuen Prozess starten und
Zellen, Redo-Zweig und Ansichten prüfen. Danach sichtbare Backup-Recovery und den
bestätigten Einzelreset mit separaten Testdaten prüfen; die anderen Blätter müssen
erhalten bleiben. Head/Artefakt, Windows-Version, Bildschirm/Clientfläche, Skalierung,
Maus und Einzelergebnis dokumentieren. Der technische Roundtrip ersetzt diese
reale Mausprobe nicht.

Godot Standard 4.7.2-stable; vollständiger isolierter Prüfweg im Repository-Root:

```powershell
$p1Cache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $p1Cache --output-dir artifacts/p1-product
```

Unter Linux benötigt die echte OpenGL-Renderprüfung `xvfb-run` und Mesa. Der Harness
nutzt nur die gepinnten offiziellen Archive, prüft deren vollständige Hashes, arbeitet
in einer temporären Projektkopie mit isolierten APPDATA-/XDG-Pfaden und installiert
nichts global. Tests einschließlich Speicher-/Recoveryfällen und echtem
Zwei-Prozess-Roundtrip, Negativtest Exit 23, Import, begrenzter Start, echte Renderbilder
mit atomaren Anfangs-/Mittel-/Endausschnitten und beiden Hinweisachsen, Windows-Export
und unter Windows exportierter Start. 300 Sekunden pro Prozess,
1200 pro Download. Die Renderfälle decken gemeinsame Slots und unabhängige
Anfangs-/Mittel-/Endausschnitte konkreter Linien auf beiden Achsen ab. Exportpreset
exakt `P1 Windows x86_64`.

```sh
godot --headless --path prototypes/p1 --import
godot --headless --path prototypes/p1 --script res://tests/run_tests.gd
godot --path prototypes/p1
```

Prüferdokumente mit Motivspoiler: [F-01](F01_PROOF.md), [F-02/F-03](F02_PROOF.md).
Technische Ergebnisse und Grenzen im [P1.3-Prüfbericht](../../docs/P1_3_VERIFICATION.md).
