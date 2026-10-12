# picross: Spiel- und Entwicklungsanleitung

Die Entwicklungsfassung enthält die [Kategorienprojektion nach KAT-1](../docs/CATEGORIES.md). Auswahl und Bearbeitung bleiben bis zur separaten Katalogoberfläche #79 wie beschrieben. Kategorienänderungen verändern keine Rätseldefinition, Revision oder Spielstände.

Weitere freigegebene Workflow-Inhalte können über den [ZA-1-Adapter](../docs/ZA1_ADAPTER.md)
registriert werden. Die Adapterlieferung ergänzt ausschließlich technische
Fähigkeiten; das aktuelle Spielerangebot bleibt bei den folgenden sechs Rätseln.

Das reguläre Projekt liegt unter `game/`. Der integrierte Stand umfasst Sidebar,
Vollsicht, Stift-/Atlasdarstellung, Save/Recovery und genau sechs Katalogrätsel:
F01 (20×20), F02 (40×40, vier Farben), F04 (20×20), F06 (50×50), F08/F09 (40×40).
F03/F05/F07 werden nicht angeboten; vorhandene Dateien und Speicherplätze bleiben.
Dies ist eine unsignierte Entwicklungsfassung, kein Release.

Sammlungsstart, passive eigene Füllminiatur, unabhängige lange Hinweise und sechs
Sidebaraktionen in 2×3 bleiben aktiv. Das Raster samt Rahmen bleibt innerhalb
der angebotenen Fitgrenze sichtbar. „Rätselansicht“ bietet Rasteransicht und
Gesamtansicht mit allen Hinweisen; ein Sitzungswechsel ändert keine Spielstände.
Fonts und Bilder sind offline eingebettet; Lizenzen/Nutzungshinweise liegen im ZIP.

## Windows starten

Das vollständige ZIP entpacken und `picross-p1.exe` starten. Keine Godot-Installation
nötig. `picross-p1.console.exe` zeigt technische Ausgaben. Dies ist eine unsignierte
Debug-Spielprobe, kein Release/Installer. Die Quellcommitkennung steht im beigefügten
README.txt; `product-report.json` bindet Head, getesteten Checkout/Test-Merge, Basis,
CI-Lauf, Engine-/Archivhashes, EXE-Hashes und Prüfphasen. Artefaktlink im PR.

Godot löst `user://p1/saves/` im projektbezogenen User-Data-Verzeichnis auf.
Unter Windows liegt dieses standardmäßig unter
`%APPDATA%\Godot\app_userdata\picross · P1\p1\saves\` (bei benutzerdefiniertem
Godot-Datenpfad entsprechend dort). Die neun bekannten Inhalts-IDs ergeben
`f01.json` bis `f09.json` mit gleichnamigen `f01.bak`/`f01.tmp` usw.
Tests verwenden nur eigene temporäre Profile; das ZIP enthält keine
Spielstände.

Fehlendes oder beschädigtes Primary mit gültigem Backup wird sichtbar als Recovery geladen;
normales Speichern bleibt bis zur bewussten Übernahme gesperrt.
„Backup zum Speichern übernehmen“ fragt vor dem Ersetzen des Primary nach.
Bei gültigem Primary und defektem Backup bleibt der Primärstand lesbar;
„Backup erneuern“ fragt vor dem Ersatz des beschädigten Backups nach.
Ohne gültige Fassung erscheint ein Fehler. „Arbeitsstand zurücksetzen“ fragt
ebenfalls nach und entfernt ausschließlich Primary, Backup und Temp des
ausgewählten Blatts. Die anderen Blätter bleiben erhalten.
Scheitert ein verpflichtender Save, bleibt die aktuelle Ansicht offen und zeigt
den Fehler. Album, Blattwechsel und reguläres Beenden gelingen nach einem
erfolgreichen Retry.

Startziel: 1920×1080 Clientfläche, auf den verfügbaren Arbeitsbereich einschließlich Fensterrahmen
begrenzt. Unter 1280×720 erscheint eine verständliche Meldung. Vergrößern des Fensters
zeigt mehr Raster oder ruhige Ränder; es vergrößert die Arbeitszellen nicht automatisch.
Die angebotenen Zoomstufen halten das gesamte Raster samt Rahmen innerhalb
der tatsächlichen Fenster-/Hinweis-/UI-Grenzen.

## Bearbeiten und zurücknehmen

- Links: unbekannt → aktive Farbe, Füllung → unbekannt, X → aktive Farbe.
- Rechts: unbekannt → X, X → unbekannt, Füllung → X.
- Auf unbekannt gestartete Setzstriche verändern nur unbekannte Zellen und schützen
  alle vorhandenen Füllungen und X. Links setzt die aktive Farbe, rechts X.
  Nur ein auf X gestarteter linker Strich wandelt unbekannte/X-Zellen in Farbe;
  nur ein auf Füllung gestarteter rechter Strich unbekannte/Füllungen in X.
  Ein auf Füllung gestarteter
  linker Rücknahmestrich entfernt nur Füllungen, ein auf X gestarteter rechter nur X.
  Eine andersfarbige Füllung wird links neutralisiert, nicht direkt umgefärbt.
- Ursprünglicher Startzustand, Modus und Farbe stehen für die gesamte Geste fest. Die erste eindeutige Bewegung
  bindet die Achse; bei diagonalem Gleichstand bleibt zunächst nur die Startzelle.
- Zurückziehen verkürzt die Vorschau. 5→12→9 übernimmt nur 5–9 als eine Aktion.
  Trifft der Zeiger die Startzelle tatsächlich wieder, zeigt die Vorschau nur diese
  Zelle und die nächste eindeutige Bewegung darf eine neue Achse wählen, auch mehrfach
  ohne Loslassen. Ohne diesen Treffer bleibt die Achse beim Überqueren gebunden;
  eine bloße Projektion oder ein Eingabesprung reicht nicht.
- Ein kleiner Live-Zähler zeigt während linker/rechter Zellgesten die gesamte
  geometrische Länge inklusive beider Endfelder: 5→12 zeigt 8, zurück auf 9 zeigt 5.
  Vorbelegte oder übersprungene Zellen zählen mit; am Ursprung zeigt er 1, danach
  die Länge des neuen geraden Abschnitts. Bei Abbruch/Drop verschwindet er.
- Außerhalb des sichtbaren Rasters bleibt der letzte gültige Endpunkt stehen.
  Esc, Fokusverlust oder Albumwechsel verwerfen den Strich. Kein Auto-Scrollen.
- Radierer links neutralisiert alle Markierungen; rechts gilt die Kreuzregel.
  Rückgängig/Wiederholen stellt ganze Striche mit exakten Vorzuständen wieder her.
- F-02/F-06: Farbe über die unbeschrifteten Farbfelder in den Originalfarben wählen.
  Eckmarkierungen zeigen die Auswahl; Status und Tooltip nennen „Farbe 1“ bis „Farbe 4“.
  Farbwahl aktiviert Füllen, auch nach Radierer. Die frühere A–D-Beschriftung
  der Mauspalette entfällt; Lösungshinweise zeigen weiterhin nur die Zahl in ihrer Farbe.
  Gleiche Farbblöcke brauchen Abstand; verschiedene dürfen angrenzen.
- Etwas größere Füllflächen bleiben durch Zwischenräume und Rasterlinien getrennt.
  Die gültige Cursorzeile und -spalte sind im Grid dezent hinterlegt. Angeschnittene
  X und Preview-X werden am sichtbaren Rasterrand geometrisch abgeschnitten.

## Navigieren und Hinweise lesen

- Mausrad und −/+ zoomen monoton bis zur vollständigen Raster-Fitgrenze samt Rahmen.
  Die gewünschte gültige Arbeitsstufe bleibt separat vom berechneten Fitwert erhalten.
  Minus/Plus und Mausrad ändern die benannte Rätselansicht nicht.
- Raster-MMB und frühere Handrouten verschieben oder bearbeiten nichts.
- Die eigene Miniatur bleibt passiv: nur eigene Füllungen in Originalfarben,
  einschließlich Fehlern und statischer Strichvorschau. X und unbekannt erscheinen
  gleich neutral, auch in vorhandenen ungelösten Albumminiaturen.
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
- Nur die mittlere Taste im oberen Hinweisbereich verschiebt nur die
  beim Start angefasste Spaltenfolge vertikal. Dieselbe Geste im linken Hinweisbereich
  verschiebt nur die angefasste Zeilenfolge horizontal. Während des Ziehens folgt
  sie der Maus flüssig zwischen den Slots. `…` zeigt dabei auf der jeweiligen Seite
  die aktuell verborgenen Zahlen an; erst beim Loslassen rastet die Folge anhand
  der zuvor sichtbaren Zahlen auf die geometrisch nächste gültige Slotlage ein.
  Ein Markerwechsel verschiebt Zahlen dabei nicht zusätzlich. Nachbarlinien
  behalten ihre eigene Position. Ziel, Linie und Achse bleiben auch beim Überqueren anderer Bereiche
  eingefroren. Raster, Miniatur, Zellen und Undo/Redo ändern sich nicht. `Esc` oder
  Fokusverlust oder ein regulärer Übergang verwirft den temporären Versatz.
  Weiteres Ziehen in derselben Richtung führt bis zum äußeren Anfang; zurück
  geht es durchgehend in Gegenrichtung. Am Anschlag bleibt die Folge stehen.
  Dort darf ein Platz frei bleiben, damit die Zahlen beim Einrasten nicht
  zurückspringen. Alle Zahlen bleiben über die Folge der Lesepositionen erreichbar.
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
  Die UI-Skalierung, Hinweisrücksetzung und H1 stehen auf der Informationsseite.
  `?` führt direkt zur dort scrollbar erreichbaren Bedienhilfe; Menü und rechter
  Pfeil zu den Einstellungen. Auch bei 1280×720/UI 125 % bleiben Werkzeuge,
  eigene Miniatur und Hinweiszugriff auf der Arbeitsseite. Der Rückpfeil führt
  zum erhaltenen Arbeitsstand zurück.

Für den Abschluss genügen alle richtigen Füllungen ohne Zusatzfüllungen.
Hintergrund muss nicht vollständig ausgekreuzt sein. Name und Ergebnisbild erscheinen
erst nach bestätigtem Abschluss. F-01 zeigt das ursprüngliche Raster neben einer
detaillierteren Illustration desselben Motivs. F-02 zeigt einen verfeinerten Leuchtturm
mit Sonne, Laterne, Turmbändern, Fenstern, Tür und Wasserlinien im klaren F-01-Stil.
Die früheren 100×100-Blätter werden nicht mehr angeboten.

## Entwicklung und technische Prüfung

Im Repository-Root mit Godot Standard 4.7.2-stable:

```sh
godot --headless --path game --import
godot --headless --path game --script res://tests/run_tests.gd
godot --path game
```

Direkter Entwicklerstart verwendet das normale Profil. Für isolierte technische
Tests und Windows-Export den Harness mit der separaten Python-/Pillow-Umgebung
nach der [Werkzeuganleitung](../tools/puzzle_production/README.md) verwenden:

```powershell
$gameCache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $gameCache --output-dir artifacts/p1-product
```

Der Harness prüft offizielle Archive und Hashes, importiert eine temporäre Kopie,
isoliert Benutzerpfade und führt Kern-/Save-/Recoverytests, echten Prozess-
Roundtrip, Negativtest Exit 23, Start und Windows-Export aus. Unter Windows startet
er zusätzlich die exportierte Fassung headless und mit nativer Oberfläche.
Linux benötigt für die OpenGL-Prüfung Xvfb/Mesa. Preset und Appname bleiben
`P1 Windows x86_64` und `picross · P1`, ebenso Schema 1 und Speicherort.

`--integration`, `--pilots`, `--visual` und `--perf-b` sind lokal an.
Die jeweiligen `--no-*`-Formen schalten sie ausdrücklich aus; CI wählt gemäß
[CI-Policy](../docs/CI_POLICY.md) nach vollständigem Änderungsumfang. Integration
prüft 500 Aktionen plus Neustart. Piloten prüfen F04/F06/F08/F09 in echten
Prozessen; der Fachlauf erhält die ursprünglichen sechs Produktionsnachweise.
Visual prüft aktuelle Pixel-/Animationsverträge, PERF-B den regulären Renderer
samt Cache. Die sechs produktiven Atlanten und Importparameter werden unabhängig
über `tools/cell_atlas_reference.json` geprüft. Historische Hersteller- und
A/B-Vergleichsprogramme sind gemäß #70/N70-HIST-01 archiviert; sie sind kein
aktueller Prüfweg.
Nicht ausgeführte Bereiche sind kein erfolgreicher Nachweis.

`technical/` enthält kompakte commitgebundene Ergebnisse, Logs und notwendige
native Bilder/Fehlerdiagnostik; Budget 30 MB, mit Spieler-ZIP 75 MB. Das ZIP
enthält Spielanleitung, Commit-/Hashbericht, `rp6-owner.ps1` für isolierte persönliche
Proben und notwendige Lizenzen. Technische Motivspoiler sind separat.
Keine automatisierte Prüfung ersetzt eine persönliche Maus-/Komfortprobe.

Aktuelle Verträge und Pflichtquellen: [Projektprofil](../docs/PROJECT_PROFILE.md).
Historische Studien, alte Abnahmen und Quellenbindungen:
[Bestandsinventar](../docs/DEVELOPMENT_ARCHIVE.md). Die ursprüngliche Anleitung ist
[am Stand vor Cleanup](https://github.com/venomenon328/picross/blob/0f89f08729539bbb4a02a590cbd18e58fbbda305/prototypes/p1/README.md) erreichbar.
Prüferdokumente mit Motivspoiler: [F01](F01_PROOF.md), [F02/F03](F02_PROOF.md).
