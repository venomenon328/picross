# picross: Spiel- und Entwicklungsanleitung

**Schrift und Lesbarkeit (HZ-A):** Normale Texte, Auswahlen, Hilfen und Tooltips
verwenden Tidy Hand. Bestehende Überschriften und Delight-Coffee-Hinweiszahlen
bleiben unverändert. UI 100/125 % ändert Schrift und Textabstände gemeinsam;
bei schmalen Fenstern darf „Sortieren nach“ innerhalb der Kopfzeile umbrechen.
Lange Kategorien bleiben über vollständig umgebrochene Tooltips lesbar; die
native Auswahlliste scrollt vertikal. [HZ](../docs/HAND_DRAWN_UI.md) bindet die Schriftrollen und Nachweise;
neue Konturen, Dropdown-Grafik und Icons bleiben das separate Paket HZ-B.

Die kompakten Katalogkacheln bleiben gleich groß, auch nach Abschluss oder Reset.
Oben steht der verdiente Motivname, vorher `???`, in derselben Bakso-Schrift wie
„Rätselkatalog“. Lange Namen nutzen zwei Zeilen, danach eine Auslassung. Darunter
steht in „Alle Rätsel“ die Kategorie; bei Filterung bleibt dieser Platz reserviert.
Neue Rätsel zeigen ein gezeichnetes Fragezeichen. Begonnene zeigen nur eigene
Füllungen, auch falsche. X und unbekannte Zellen bleiben neutral. Ein begonnener
Stand ohne Füllzellen, etwa nach Undo, zeigt eine leere Vorschau ohne Fragezeichen. Erst ein
gültiger Abschluss zeigt Motivname und farbiges Abschlussbild.

Der gemeinsame Papierstreifen unter dem Bild zeigt in einer Zeile links die
Größe, in der Mitte einen gefüllten Schwierigkeitskreis mit vollständigem Namen
und rechts den Modus: einen dunklen Stift für Mono, drei gefächerte Stifte für Farbe.
Die Stufen heißen „Sehr leicht“, „Leicht“, „Mittel“, „Schwer“ und „Sehr schwer“.
Ohne Einstufung erscheint ein neutralgrauer Kreis mit „Nicht eingestuft“.
Die Schwierigkeit hat keinen Tooltip. Der Modus erklärt sich beim Darüberfahren
mit der Maus. Ein Klick auf den Streifen öffnet das zugehörige Blatt.

In der festen Fußzeile steht links „Blatt NN“, rechts der Status mit Symbol:
offener Kreis und „Neu“, kleiner Stift und „Begonnen“, Haken und „Gelöst“.
Auch die Fußzeile öffnet dasselbe Blatt. Alle Karten einer Ansicht verwenden
identische, anhand der vollständigen Metadaten gemessene Breiten. Bei wenig Platz
erscheinen weniger Spalten; Schrift und Bildraum werden dafür nicht verkleinert.
Verdiente Reveals und Stiftsymbole bleiben lokal geglättet.
Aktueller Vertrag: [Kataloggestaltung](../docs/CATALOG_PRESENTATION.md).

Die Karte öffnet oder setzt ihr Blatt fort; gelöste Blätter öffnen die Endansicht.
Oben rechts steht bei bearbeiteten Blättern der Neustartpfeil mit „Rätsel zurücksetzen“.
Er verlangt Bestätigung; Abbrechen erhält den Stand. Bei gültigem leerem Stand ist
er verborgen, bei Speicher-/Recoveryproblemen bleibt er erreichbar. Ungültige Saves
sperren Öffnen und zeigen „Ungültig“. Speicherhinweise und „Backup übernehmen“ /
„Backup erneuern“ stehen im Bildraum, bei langen Diagnosen dort scrollbar.
Die Karte selbst hat keinen Tooltip; gezielte Modus- und
Resettooltips skalieren bei UI100/125 mit.

Zusätzlich gibt es den [WEB-1-Browserentwicklungsweg](../docs/WEB_HOSTING.md):
statischer Export für Chromium/Firefox mit Maus und dauerhaftem Browserspeicher.
Die Kopfzeile zeigt Build und tatsächlichen Speicherstatus. Bei Speicherfehler
offen lassen und erneut versuchen. Nur ein schreibender Tab je Origin ist erlaubt.
Build, SSH-Update, Rollback, Hostingvoraussetzungen und Speichergrenzen stehen in
der verlinkten Anleitung. Persönliche Webprobe und Live-Deployment bleiben separat.

Die Entwicklungsfassung enthält die [Kategorienprojektion nach KAT-1](../docs/CATEGORIES.md). Das Spiel startet im Rätselkatalog mit „Alle Rätsel“. Die scrollbare Kategorienauswahl enthält auch leere Kategorien; je Seite erscheinen höchstens 24 Karten. Eine Karte öffnet oder setzt genau ihr Blatt fort. Zurückkehren erhält Kategorie, Seite und Scrollposition; ein Neustart beginnt wieder bei „Alle Rätsel“, Seite 1. Einstellungen/Info und Beenden sind direkt erreichbar.

Direkt neben der Kategorie steht „Sortieren nach“: Kategorie, Größe,
Schwierigkeit oder Hinzugefügt. Der Pfeil wechselt auf- und absteigend.
Kategorie folgt der redaktionellen Reihenfolge, Größe der Zellanzahl. Bei einem
neuen Kriterium beginnt die Richtung aufsteigend; „Hinzugefügt“ zeigt zuerst die
neuesten Rätsel. Ohne Datum oder Einstufung steht ein Blatt immer hinten.
Gleichstände behalten ihre feste Blattreihenfolge; Blattnummern ändern sich nicht.

Die Sortierung bleibt lokal nach einem Neustart erhalten. Filter, Seite und
Scrollposition gelten für die laufende Sitzung; die Rückkehr aus einem Rätsel
behält sie. Ein tatsächlicher Filter- oder Sortierwechsel beginnt auf Seite 1.
„Sortierung konnte nicht gespeichert werden“ betrifft nur diese Auswahl:
„Erneut versuchen“ wiederholt die Speicherung, ohne Spielstände zurückzusetzen.
Im Browser muss der Schreibvorgang bestätigt sein, bevor der Tab geschlossen wird.

Karten zeigen „Neu“, „Begonnen“ (auch mit ausschließlich Redohistorie) oder „Gelöst“. Begonnene Vorschauen zeigen nur eigene Füllungen, ohne Korrekturen; Name und Motivbild erscheinen erst nach gültigem Abschluss. Ein leerer automatisch angelegter Save bleibt „Neu“. Reset und Backupaktionen gehören zur jeweiligen Karte und verlangen weiterhin Bestätigung. Ein gültiger leerer Bestand und ein Katalogladefehler haben unterschiedliche Anzeigen. Kategorienänderungen verändern keine Rätseldefinition, Revision oder Spielstände.

Der reguläre Spielbestand folgt `content/registry.json` und enthält ausschließlich
freigegebene Workflow-Inhalte, aktuell elf Rätsel. Weitere Inhalte werden über den
[ZA-1-Adapter](../docs/ZA1_ADAPTER.md) registriert. Historische Prototypen F-01 bis
F-09 sind seit #114 nicht mehr Bestandteil des Spielerangebots oder Exports.

Das reguläre Projekt liegt unter `game/`. Sidebar, Vollsicht, Stift-/Atlasdarstellung
und Save/Recovery sind integriert. Dies ist eine unsignierte Entwicklungsfassung,
kein Release.

Sammlungsstart, passive eigene Füllminiatur, unabhängige lange Hinweise und sechs
Sidebaraktionen in 2×3 bleiben aktiv. Das Raster samt Rahmen bleibt innerhalb
der angebotenen Fitgrenze sichtbar. „Rätselansicht“ bietet Rasteransicht und
Gesamtansicht mit allen Hinweisen; ein Sitzungswechsel ändert keine Spielstände.
Fonts, Bilder und Spieldaten liegen offline in `picross-p1.pck`; Lizenzen/Nutzungshinweise liegen im ZIP.

## Aktuellen main-Player per GitHub Actions erzeugen

Unter [GitHub Actions](https://github.com/venomenon328/picross/actions/workflows/build-main-player.yml)
den Workflow **Build playable main (Windows x64)** öffnen und über
**Run workflow** starten. Die Action checkt immer das dann aktuelle `main`
aus, unabhängig von der im Startdialog angezeigten Branch-Auswahl.
Nach erfolgreichem Lauf unter **Artifacts** das eine
`picross-main-windows-x86_64-<Commit>`-Artefakt herunterladen. Das erhaltene
ZIP **einmal** entpacken und direkt `picross-p1.exe` starten; es enthält
kein weiteres ZIP. Die Commitkennung steht auch in `README.txt`.
Das Artefakt wird 14 Tage aufbewahrt.

Diese Action erstellt ausschließlich den unsignierten Windows-Debugplayer
aus dem regulären Spielbestand. Sie startet weder die Product-Testmatrix
noch ein Release/Deployment; ein tatsächlicher Windows-GUI-Start wird auf dem
Linux-Runner nicht geprüft. Der separate CI-Playerexport bleibt unverändert.

## Windows starten

Das vollständige ZIP entpacken und `picross-p1.exe` starten. Die EXE und
`picross-p1.pck` müssen im selben Ordner bleiben. Keine Godot-Installation
nötig. `picross-p1.console.exe` zeigt technische Ausgaben. Dies ist eine unsignierte
Debug-Spielprobe, kein Release/Installer. Die Quellcommitkennung steht im beigefügten
README.txt. Ausschließlich das **Product-CI-Artefakt** enthält zusätzlich
`product-report.json` mit Head, getestetem Checkout/Test-Merge, Basis, CI-Lauf,
Engine-/Archivhashes, EXE-Hashes und Prüfphasen (Artefaktlink im PR). Der manuelle
main-Player hat bewusst keinen solchen Prüfbericht; sein Link steht im Actions-Lauf.

Godot löst `user://p1/saves/` im projektbezogenen User-Data-Verzeichnis auf.
Unter Windows liegt dieses standardmäßig unter
`%APPDATA%\Godot\app_userdata\picross · P1\p1\saves\` (bei benutzerdefiniertem
Godot-Datenpfad entsprechend dort). Dateinamen folgen dem jeweiligen Registry-Slot:
`<slot>.json`, `<slot>.bak` und `<slot>.tmp`. Vorhandene alte `f01`…`f09`-Dateien
bleiben unbenutzt auf Datenträger; sie werden weder migriert noch gelöscht.
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
  Vorbelegte oder übersprungene Zellen zählen mit. Ab Länge 2 folgt die dunkle Zahl
  mit heller Kontur dem tatsächlichen Zeiger, auch über der Seitenleiste; bei Länge 1,
  Abbruch oder Drop verschwindet sie. Ihre UI-skalierte Größe bleibt beim Rasterzoom
  gleich. Kein Kasten; am Fensterrand bleibt die vollständige Zahl innen sichtbar.
- Begonnene Striche folgen der Maus entlang ihrer Achse bis zum gültigen Rasterrand,
  auch über anderen Bedienelementen. Spalte 5→rechts hinaus bei 30 Spalten ergibt
  26 Felder bis Spalte 30. Loslassen wertet seine eigene letzte Position aus und
  übernimmt genau einen Strich; ein darunterliegender Button wird dabei nicht geklickt.
  Der sichtbare Zeiger bleibt frei. Bei erhaltenem Spielfokus ist auch Loslassen
  außerhalb der Fensterclientfläche möglich. Technischer Windows-Nachweis und noch
  offene Eigentümerprobe sind getrennt in der [Prüfzuordnung](../docs/CELL_DRAG_VERIFICATION.md)
  und PR #145 gebunden; diese Anleitung ist keine persönliche Abnahme.
  Esc, Fokusverlust, verlorene Tastenzuordnung oder Albumwechsel verwerfen den Strich
  vollständig. Rückkehr startet keine Geste ohne frischen Tastendruck. Kein Auto-Scrollen.
- Radierer links neutralisiert alle Markierungen; rechts gilt die Kreuzregel.
  Rückgängig/Wiederholen stellt ganze Striche mit exakten Vorzuständen wieder her.
- Bei Farbrätseln: Farbe über die unbeschrifteten Farbfelder in den Originalfarben wählen.
  Eckmarkierungen zeigen die Auswahl; Status und Tooltip nennen „Farbe 1“ bis „Farbe 4“.
  Farbwahl aktiviert Füllen, auch nach Radierer. Die frühere A–D-Beschriftung
  der Mauspalette entfällt; Lösungshinweise zeigen weiterhin nur die Zahl in ihrer Farbe.
  Gleiche Farbblöcke brauchen Abstand; verschiedene dürfen angrenzen.
- Etwas größere Füllflächen bleiben durch Zwischenräume und Rasterlinien getrennt.
  Im Raster sind Cursorzeile und -spalte dezent hinterlegt. Über Zeilenhinweisen
  bleibt nur die Zeile, über Spaltenhinweisen nur die Spalte markiert, auch bei
  vollständigen Folgen und geöffnetem Vollhinweis. Während Hinweisdrag bleibt
  ausschließlich seine Quellenlinie markiert. Angeschnittene
  X und Preview-X werden am sichtbaren Rasterrand geometrisch abgeschnitten.

## Navigieren und Hinweise lesen

- Offene Hinweise bleiben kräftig. Eindeutig vollständig gesetzte Zahlen werden
  deutlich blasser; sind ihre Blöcke zusätzlich an beiden Enden abgegrenzt, bleibt
  die Zahl gleich blass und erhält ein handschriftliches X über die ganze Zahl.
  X, echter Linienrand und direkt andere Füllfarbe begrenzen; unbekannte Nachbarn
  nicht. Beide Achsen und der vollständige Tooltip zeigen dieselben Zustände.
  „Erfüllte Hinweise markieren“ gilt für die Sitzung: Aus zeigt normale Zahlen,
  An den aktuellen Stand. Nur eigene sichtbare Zellen einschließlich Vorschau und
  die vollständige Linie zählen, kein Lösungsvergleich. `…` und `–` bleiben unmarkiert.
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
- Die linke Taste im oberen Hinweisbereich verschiebt nur die
  beim Start angefasste Spaltenfolge vertikal. Dieselbe Geste im linken Hinweisbereich
  verschiebt nur die angefasste Zeilenfolge horizontal. Während des Ziehens folgt
  sie der Maus flüssig zwischen den Slots. `…` zeigt dabei auf der jeweiligen Seite
  die aktuell verborgenen Zahlen an; erst beim Loslassen rastet die Folge anhand
  der zuvor sichtbaren Zahlen auf die geometrisch nächste gültige Slotlage ein.
  Ein Markerwechsel verschiebt Zahlen dabei nicht zusätzlich. Nachbarlinien
  behalten ihre eigene Position. Ziel, Linie und Achse bleiben auch beim Überqueren anderer Bereiche
  eingefroren. Raster, Miniatur, Zellen und Undo/Redo ändern sich nicht. `Esc` oder
  Fokusverlust oder ein regulärer Übergang verwirft den temporären Versatz.
  MMB navigiert keine Hinweise. Ein Hinweisdrag wird auch über Raster oder Buttons
  nicht zur Zell- oder Buttonaktion. Verlorene Freigabe oder ein Tastenakkord
  verwirft den Versatz; nach dem Loslassen beginnt erst ein frischer Druck eine Geste.
  Weiteres Ziehen in derselben Richtung führt bis zum äußeren Anfang; zurück
  geht es durchgehend in Gegenrichtung. Am Anschlag bleibt die Folge stehen.
  Dort darf ein Platz frei bleiben, damit die Zahlen beim Einrasten nicht
  zurückspringen. Alle Zahlen bleiben über die Folge der Lesepositionen erreichbar.
  „Hinweise rasterseitig ausrichten“ stellt
  alle Linien auf ihren rasterseitigen Standardausschnitt zurück.
- Freie Breite und Höhe zeigen nach dem Fit zusätzliche vollständige Zeilen- und
  Spaltenhinweise, ohne kleinere Zellen dafür zu erzwingen. Passende Folgen haben
  keine Auslassungsmarker und lassen sich nicht in Leerraum verschieben.
- Darüberfahren einer gekürzten Folge zeigt weiterhin den vollständigen farbigen
  Hinweis mit Umbruch direkt über dem Arbeitsbild: unverändert kleine Fraunces-Überschrift,
  gut lesbare Delight-Zahlen und ruhiges Papier mit gezeichnetem Rahmen.
  Die Overlaylesegröße folgt der UI-Skalierung unabhängig vom Rasterzoom. Das ist ein Zusatzweg; Anfang,
  Mitte und Ende bleiben auch durch Hinweis-Panning erreichbar. Eine separate
  Hinweisansicht gibt es nicht.
- UI 100/125 % vergrößert die Oberfläche. Delight-Coffee-Hinweisziffern und ihre
  gemeinsamen Zeilen-/Spaltenplätze passen sich dem tatsächlichen Zellmaß an:
  kompakt bei kleinem Zoom, größer beim Hineinzoomen, innerhalb der Fitgrenze.
  Geänderte Slotkapazitäten erhalten je konkrete Folge die semantische Leseposition:
  äußerer Anfang und rasterseitiges Ende bleiben am gewählten Rand verankert,
  mittlere Ausschnitte behalten den gelesenen Tokenbereich mit größtmöglicher
  Überdeckung. Das gilt auch bei Arbeitszoom und Resize; alle Zustände bleiben
  in ganzen Slots eingerastet. Vorübergehende Vollanzeige bewahrt die Anker auch
  beim Speichern und Neustart; beim Verengen kehrt derselbe Lesebereich zurück.
  Die UI-Skalierung, Hinweisrücksetzung und H1 stehen auf der Informationsseite.
  `?` führt direkt zur dort scrollbar erreichbaren Bedienhilfe; Menü und rechter
  Pfeil zu den Einstellungen. Auch bei 1280×720/UI 125 % bleiben Werkzeuge,
  eigene Miniatur und Hinweiszugriff auf der Arbeitsseite. Der Rückpfeil führt
  zum erhaltenen Arbeitsstand zurück.

Für den Abschluss genügen alle richtigen Füllungen ohne Zusatzfüllungen.
Hintergrund muss nicht vollständig ausgekreuzt sein. Name und Ergebnisbild erscheinen
erst nach bestätigtem Abschluss. Die registrierte Definition bindet Motivname und
freigegebenes Ergebnisbild; vorher bleibt nur die eigene Füllminiatur sichtbar.
Beim neuen Abschluss treten Raster, Hinweise und Werkzeuge zurück. Deine Füllungen bewegen sich zur Papiermitte, werden zu lückenlosen Farbflächen und gehen in das fertige Bild über. Die Folge dauert etwa 2,15 Sekunden. Die Speicherung erfolgt unmittelbar beim letzten Zug; etwaige Speicherfehler bleiben sichtbar. Danach erscheinen Motivname und „Rätsel zurücksetzen“. Der Titel bleibt „Blatt NN · W × H“, der Buchreiter führt zur Sammlung.

Bereits gelöste Blätter öffnen direkt das fertige Bild. Fenster- oder UI-Größenänderung und Fokusverlust beenden eine laufende Enthüllung; sie wird danach nicht wiederholt. Bestätigtes Zurücksetzen unter dem Bild öffnet dasselbe Blatt leer. Abbrechen erhält den Stand. Der Reset einer Katalogkarte bleibt im Katalog. Nach erneutem Lösen läuft die Enthüllung wieder.

Die früheren 100×100-Blätter werden nicht mehr angeboten.

## Entwicklung und technische Prüfung

Regulärer Entwicklerstart im Repository-Root mit Godot Standard 4.7.2-stable:

```sh
godot --headless --path game --import
godot --path game
```

Direkter Entwicklerstart verwendet das normale Profil. Für isolierte technische
Tests (mit temporär erzeugtem synthetischem Katalog) und Windows-Export den Harness mit der separaten Python-/Pillow-Umgebung
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
prüft 500 Aktionen plus Neustart. Der `--pilots`-Bereich prüft vier synthetische Muster in echten
Prozessen als feste Funktionsregression; der Fachlauf zertifiziert keine
Bestandsrätsel erneut. Reine Rätselergänzungen starten keinen dieser Tests.
Visual prüft aktuelle Pixel-/Animationsverträge, PERF-B den regulären Renderer
samt Cache. Die sechs produktiven Atlanten und Importparameter werden unabhängig
über `tools/cell_atlas_reference.json` geprüft. Historische Hersteller- und
A/B-Vergleichsprogramme sind gemäß #70/N70-HIST-01 archiviert; sie sind kein
aktueller Prüfweg.
Nicht ausgeführte Bereiche sind kein erfolgreicher Nachweis.

`technical/` enthält kompakte commitgebundene Ergebnisse, Logs und notwendige
native Bilder/Fehlerdiagnostik. Größen werden gemessen, ohne feste Bytegrenzen.
Das reguläre Product-CI-ZIP enthält Spielanleitung, Commit-/Hashbericht und
notwendige Lizenzen. Historische Produktionshilfen werden nicht ausgeliefert.
Technische Motivspoiler sind separat.
Keine automatisierte Prüfung ersetzt eine persönliche Maus-/Komfortprobe.

Aktuelle Verträge und Pflichtquellen: [Projektprofil](../docs/PROJECT_PROFILE.md).
Historische Studien, alte Abnahmen und Quellenbindungen:
[Bestandsinventar](../docs/DEVELOPMENT_ARCHIVE.md). Die ursprüngliche Anleitung ist
[am Stand vor Cleanup](https://github.com/venomenon328/picross/blob/0f89f08729539bbb4a02a590cbd18e58fbbda305/prototypes/p1/README.md) erreichbar.
Historische Prüferdokumente mit Motivspoiler: [F01](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/game/F01_PROOF.md), [F02/F03](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/game/F02_PROOF.md).
