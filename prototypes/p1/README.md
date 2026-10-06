# P1 · Integrierte Windows-Spielprobe

Z2 / [#23](https://github.com/venomenon328/picross/issues/23) liefert die native
A-Bucharbeitsansicht und genau eine Informationsseite. Pfeil/Menü öffnen Einstellungen,
`?` öffnet Hilfe; der Rückpfeil führt zum selben Blatt. UI 100/125 %, Hinweisreset,
H1 und Beenden stehen dort. Neun Arbeitsaktionen bleiben direkt am Raster;
Farbwahl aktiviert Füllen auch nach Hand/Radierer. Das linke Register öffnet das
bestehende Album. Speicherfehler verhindern einen ungesicherten Wechsel; nötige
Backupübernahme bleibt auf der Arbeitsseite mit Bestätigung erreichbar.

Offline-Fonts Fraunces/Plex Sans, unverändertes A-Papier und feste C1-Kontur sind
integriert. OFL-Texte liegen im Windows-ZIP unter `licenses/`, alle Ressourcen sind
in der EXE eingebettet. Kein Fontdownload oder Godotsetup beim Spieler.
[Auswahl und Herkunft](../../docs/Z2_SELECTION.md),
[aktuelle Prüfung und sichere Eigentümeranleitung](../../docs/Z2_VERIFICATION.md).
Z2 ist nach Review und Mergefreigabe über PR #33 integriert. Z2-M01/M02/M03
wurden nicht durchgeführt; der Eigentümer hob das damalige Gate für diesen Merge
auf. RP-3/#37 ist nach unabhängigem Review R2 über PR #44 integriert.
RP-6/#40 ergänzt fünf weitere feste Pilotblätter im Draft; kombinierte unabhängige
Nachprüfung und tatsächliche Eigentümerproben bleiben offen.
[RP-3-Prüfzuordnung](../../docs/RP3_VERIFICATION.md),
[Importdateien und Herkunft](../../examples/rp3/README.md). Dies ist ein Testexport.


H1 aus [#19](https://github.com/venomenon328/picross/issues/19) ergänzt automatisch
die exakte Eindeutigkeitsanalyse der Hinweise. Die damalige Eigentümerprobe ist
nicht als bestanden dokumentiert; technische Nachweise und Schritte stehen im
[H1-Prüfbericht](../../docs/H1_VERIFICATION.md) und in PR #20; H1 ist dort integriert. Nach Review R1 hat
der Eigentümer die B-01-Nacharbeit und den anschließenden Merge ausdrücklich
beauftragt; die Probe ist für diesen Merge daher kein verbleibendes Gate. Die in
#12 bestätigte bisherige P1-Probe bleibt gültig.

„Erfüllte Hinweise markieren“ startet an und gilt für alle Blätter derselben
App-Sitzung. Album-/Blattwechsel und Reset erhalten die Auswahl; nach Neustart ist
sie wieder an. Aus zeigt normale Zahlen, erneutes Einschalten den aktuellen Stand.
GP-48 unterscheidet nun normale, leicht abgeschwächte und durchgestrichene Zahlen.
Plex Sans Gewicht 600 macht sie kräftiger; Schriftgrößen und Positionen bleiben
gleich. Abschwächung (Alpha 0,78) erhält die Hinweisfarbe und C1-Kontur. Auch
Hoverhinweise und gezogene Folgen zeigen denselben Zustand. Aus blendet beide
positiven Zustände aus; `…` und `–` werden nicht markiert.

Es zählt nur die ganze betreffende Linie einschließlich ihrer eigenen Hinweise und
deiner aktuellen Füllungen/X samt elastischer Vorschau. Ein vollständig gefüllter
Block wird bei eindeutiger Zuordnung zunächst abgeschwächt. Durchgestrichen wird
er erst, wenn beide Enden unmittelbar durch X, den tatsächlichen Rasterrand oder
eine andersfarbige Füllung begrenzt sind. Der andere Farbblock muss nicht schon
vollständig sein. Unbekannte Nachbarn, entfernte X und Viewportränder zählen nicht.
Bei Widerspruch entfallen alle positiven Zustände
dieser Linie. Das prüft nicht die hinterlegte Lösung, verändert keine Zellen und
verrät kein bestimmtes falsches Feld. Rückzug, Abbruch, Undo/Redo und Recovery führen
die Anzeige mit; Zustände und Schalter werden nicht im Spielstand gespeichert.

[GP-48-Prüfung](../../docs/GP48_VERIFICATION.md) und
[gezielte GP48-M01-Eigentümerprobe](../../docs/GP48_OWNER_TRIAL.md) dokumentieren die
integrierte Lieferung. Review R1 und GP48-M01 sind abgeschlossen; PR #49 ist als
`add7a7e6` in `main` integriert. Die Regeln bleiben für RP-6 aktiv; der neue kombinierte
Slim-Download verwendet die RP-6-Anleitung. Historische H1-Abnahmen werden nicht umgedeutet.

Im äußeren technischen Artefakt liegen `H1-PRUEFUNG.md`, `h1-owner-probe.ps1`,
`h1-owner-probe.gd` und `h1-probe-windows-x86_64.zip` für die separate künstliche
Windows-Linienprobe. Sie gehören nicht zum normalen Benutzer-ZIP und greifen nicht
auf gespeicherte Puzzles zu.

P1.3 aus [Issue #11](https://github.com/venomenon328/picross/issues/11) und
[P1.4 / #12](https://github.com/venomenon328/picross/issues/12) sind über
PR #15/#16 in `main` integriert; [P1.4-Ergebnisbericht](../../docs/P1_4_VERIFICATION.md).
G1 aus [Issue #17](https://github.com/venomenon328/picross/issues/17) ist über PR #18
integriert und ergänzt die erneute Achsenwahl nach tatsächlicher Rückkehr
zur Startzelle. H1/#19 ist über PR #20 auf diesem kombinierten Stand integriert. F-01 (20×20),
F-02 (40×40, vier Farben), F-03 (100×100, ausdrücklich UI-Testdatensatz)
und F-04 (20×20 monochrom, RP-3-Dateiimport) bleiben erhalten. RP-6 ergänzt
F-05 (100×100 Mono), F-06 (50×50 Farbe), F-07 (100×100 Farbe),
F-08/F-09 (40×40 Farbe). Alle neun sind im scrollbar erreichbaren Album zugänglich. Review R2/B-01/B-02 und D-07 bis D-27 sind in diesem Stand
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
- F-02/F-03: Farbe über die unbeschrifteten Farbfelder in den Originalfarben wählen.
  Eckmarkierungen zeigen die Auswahl; Status und Tooltip nennen „Farbe 1“ bis „Farbe 4“.
  Farbwahl aktiviert Füllen, auch nach Hand oder Radierer. Die frühere A–D-Beschriftung
  der Mauspalette entfällt; Lösungshinweise zeigen weiterhin nur die Zahl in ihrer Farbe.
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
F-03 bleibt auch danach als Test gekennzeichnet.

## Optionale G1-Nachprobe · nicht durchgeführt

Die M-01-bis-M-04- und M-06/M-07-Proben des bisherigen P1-Stands sind in
[#12](https://github.com/venomenon328/picross/issues/12) als bestanden dokumentiert.
Die folgende G1-Nachprobe wurde nicht durchgeführt und wird nicht als bestanden
behauptet; nach ausdrücklicher Eigentümerentscheidung war sie für PR #18 kein
Mergegate. Sie bleibt als optionaler realer Eindruck dokumentiert:

1. F-01: Einen linken Strich nach rechts, links, unten und oben ziehen. Jeweils bei
   gedrückter Taste exakt zur Startzelle zurückkehren und senkrecht weiterziehen;
   dann mehrfach zwischen Achsen wechseln. Am Ursprung muss nur diese Zelle mit
   Zähler 1 sichtbar sein. Danach bleibt genau der letzte gerade Abschnitt in
   Raster und Miniatur; ein Undo/Redo stellt ihn als einen Schritt wieder her.
2. F-01: Rechts/X, linker Rücknahmestrich auf einer Füllung, rechter
   Rücknahmestrich auf X und linker Radierer ebenso umorientieren. Vorbelegte
   Zellen und Farbe prüfen. Escape und Fokusverlust nach dem Wechsel müssen die
   Vorschau ohne neue Aktion verwerfen; eine falsche Tastenfreigabe darf nicht
   abschließen.
3. F-02 mit den vier Farbfeldern und F-03 bei 50 % Arbeitszoom: echte Startzelle treffen und
   die neue Achse prüfen. Zeiger ohne Startzelltreffer über den Ursprung springen
   beziehungsweise in eine andere Zeile/Spalte neben ihn bewegen: Die alte Achse
   muss gebunden bleiben. Über UI/Viewportgrenze bleibt der letzte gültige
   Endpunkt stehen. Hinweis-Pan bleibt auf seine gestartete Linie beschränkt.

Je Schritt Ergebnis/Abweichung notieren: ____ / ____ / ____.

Protokollfelder: tatsächlicher Head/Artefakt, Windows-Version, Bildschirmauflösung,
Fenster- und Clientfläche, tatsächliche Windows-Anzeigeskalierung, Maus, Szenario,
Ergebnis/Abweichung. Nicht aus Screenshotabmessungen ableiten. Referenz aus früheren
Angaben: Windows 11, 2560×1440, Ryzen 7 5800X, RTX 3070. Die reale Skalierung bleibt
unbekannt. Technische Renderflächen und synthetische Events ersetzen diese Abnahme nicht.

Die technische 500-Aktionen-Gesamtintegration wurde in #12 geprüft und läuft im
Produktprüfweg für den neuen Head erneut.
Wertung, Controller/Tastatur und Release bleiben außerhalb dieser Lieferung.
Escape ist weiterhin Mausgestenabbruch. Kein Merge durch diese Übergabe.

## Technische Reproduktion

Der technische Produktweg prüft F-01/F-02, Godot-Regressionen, den isolierten
Zwei-Prozess-Roundtrip, die 500-Aktionen-Folge samt Neustart, Renderbilder und
Windows-Export. RP-3 ergänzt den realen Dateiimport/F-04-Export, drei getrennte
Spiel-/Neustartprozesse sowie eigene Arbeits-/Abschluss-/Albumrenders.
Der Bericht bindet diese Ergebnisse an Head und Test-Merge; die kombinierte
RP-6-Nachprüfung bleibt separat offen, die reale Eigentümer-Lösung ist RP-6-Gate.

Godot Standard 4.7.2-stable und isolierte Pillow-12.3.0-Umgebung aus der
[Werkzeuganleitung](../../tools/puzzle_production/README.md); vollständiger Prüfweg
im Repository-Root mit dem dort eingerichteten Python-Interpreter:

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
Technische Ergebnisse und Grenzen im [P1.4-Ergebnisbericht](../../docs/P1_4_VERIFICATION.md);
der [P1.3-Prüfbericht](../../docs/P1_3_VERIFICATION.md) bleibt ein historischer
Nachweis seines damaligen Heads.


## RP-6-Spielprobe

Für die neue Eigentümerprobe die [neutrale Anleitung](../../docs/RP6_OWNER_TRIAL.md)
verwenden. Das Windows-ZIP enthält `rp6-owner.ps1` für einen eigenen temporären
Prüfstand und die Fortsetzung unter gleichem Commit/Prüfnamen. Technische
Motivspoiler liegen im getrennten `rp6-review`-Artefakt. Sechs Pilotproben im
Produktprüfweg ergänzen je drei Prozesse und zehn native Ansichten; kein
automatisierter Lauf ist eine reale Lösung oder Phasenentscheidung.
