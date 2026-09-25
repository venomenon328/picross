# Z1 · Zwei ausführbare Zieldesign-Entwürfe

Stand: 25.09.2026 · [#22](https://github.com/venomenon328/picross/issues/22) zu
[#21](https://github.com/venomenon328/picross/issues/21).
**V1 und V2 sind nicht gewählt.** Diese Unterlage empfiehlt eine Richtung für die
Eigentümerentscheidung; sie autorisiert weder #23/#24 noch Merge oder Release.

## Ausgangslage und Ergebnisgrenze

Startbasis ist der erneut abgerufene `main@831b46f9e373e8691c18088efc9f2495fe3defb8`.
Die Pflichtquellen und vollständigen #21/#22-Bodies wurden gelesen; beim Start
gab es dort keine Kommentare und keine offene parallele PR-Arbeit. #5 ist gemäß
seinem Abschlusskommentar geschlossen. Alte P1-/G1-/H1-Abnahmen werden nicht zu
einer Abnahme der neuen Entwürfe erklärt.

Separater Einstieg: `prototypes/p1/design/main.tscn`. Er erzeugt ausschließlich
Arbeitssitzungen im Speicher, ohne `Main`, `SaveStore`, Autosave oder Recoverypfad.
Die reguläre Hauptszene und ihr Startvertrag bleiben erhalten. Board, Session,
Gesture, Player, GridView, ClueLayout, H1 und Miniature werden wiederverwendet.
Ein optionaler `frame_style` am Board verändert ausschließlich dessen äußere Fläche;
`null` erhält die bisherige Darstellung. Kein zweiter Spielkern.

## E-01 · Inventar und Informationshierarchie

Inventar des bisherigen Arbeitsbildschirms aus `ui/main.gd` einschließlich seiner
kontextuellen Zustände. Entwurfsgeometrie ist in beiden Varianten identisch.

| Bisheriges Element | Einordnung und neue Position | Begründung / Grenze |
| --- | --- | --- |
| Titel / Blattkennung, Maße | Dauerhaft, flache Kopfzeile | Neutrales Blatt, kein Motivname. |
| Raster, Lösungshinweise, Fünferlinien | Dauerhaft, dominante linke Arbeitsfläche | Ein gemeinsamer präziser Arbeitsverbund; unveränderte Originaldaten. |
| Eigene Miniatur / Ausschnittrahmen | Dauerhaft, oben rechts | Sichtbar auch bei geöffnetem Werkzeugbereich; keine Lösungskorrektur. |
| Zeile / Spalte | Dauerhaft, unter Miniatur | Separat von Lösungshinweisen; beim Zeigen aktualisiert. |
| Werkzeugstatus / Farbe A–D | Dauerhaft, rechte Spalte | Wort für Werkzeug; echte Farbflächen mit Rahmen und zweifarbigem Punkt; keine A–D-Knöpfe. Monochrom hat eine Farbfläche. |
| Füllen / Radierer / Hand | Dauerhaft, unter Farbflächen | Ein eingerasteter Knopf kennzeichnet das Werkzeug unabhängig von Farbe. |
| Undo / Redo | Dauerhaft, rechte Kopfzeile | Häufige kurze Aktionen; getrennte Tooltips und sichtbarer deaktivierter Zustand. |
| Zoomwert, −/+, Gesamtansicht, Arbeitsgröße | Dauerhaft, rechte Spalte | Bewusst vom Fenstermaß und UI 100/125 % getrennt. |
| UI-Skalierung | Auf Abruf, Menü | Gut erreichbare seltenere Einstellung. |
| Hinweise rasterseitig ausrichten | Auf Abruf, Menü | Bewusster Reset aller individuellen Lesepositionen. |
| H1-Schalter | Auf Abruf, Menü | Sitzungsweit, standardmäßig an; keine Persistenz. |
| Mehrzeilige Mausbedienung | Auf Abruf, sichtbarer Hilfe-Knopf und kurze Tooltips | Tatsächlich öffnende/schließende, eingabesichere Hilfe. |
| Vollständige Hinweise bei Überlauf | Kontextuell, vorhandener Board-Tooltip | Individueller Hinweisdrag bleibt der primäre Navigationsweg. |
| Hoverbänder, Vorschau, Live-Zähler, H1-Strich | Kontextuell, unverändert am Board | Orientierung/Arbeitsfeedback bleiben erhalten. |
| F-03-Warnung | Dauerhaft am unteren Rand | Kein Hilfetext: unkuratierter UI-Stresstest bleibt ausdrücklich erkennbar. |
| P1-Statusfuß / Speicherhinweis | Unterer Rand: „Beispiel · nur im Speicher“ | Wahrheitsgemäßer Sitzungsstatus. Keine fingierte Speicherung. |
| Speicher-/Recoveryfehler und Reparaturknopf | In Z1 nicht anwendbar; im regulären P1 unverändert | Kein Speicherpfad in Z1. Reale Fehler werden nicht ins Hilfemenü verschoben; die spätere Integration muss sie weiterhin sichtbar führen. |
| Album / Blattöffnung / bestätigter Einzelreset | Albumablauf erst Z2; separate Z1-Prüfleiste für Fixture/Reset | Keine entfernte Produktfunktion: reguläres P1 bleibt vollständig startbar. Z1-Reset setzt nur die Beispielsitzung zurück. |
| Beenden | Auf Abruf, Menü oder Fensterschließen | Bricht die Vorschau ab, beendet ohne Savezugriff. |
| Abschluss / Reveal | Z1 meldet Abschluss nur im Beispielstatus | Kein vorzeitiger Motivname und keine fingierte Abnahme des Gesamtprodukts. |

Die schmale rechte Spalte wird als gemeinsame Annahme beibehalten. Undo/Redo wandern
in die Kopfzeile, damit häufige Werkzeuge und Navigation auch bei 720p/125 % sichtbar
bleiben. Im engen Fall schrumpft nur die Miniatur auf 90×90 logische Einheiten;
Rasterzellen behalten ihre gewählte Größe. Der getrennte dunkle Prüfbereich unten
gehört ausdrücklich nicht zur vorgeschlagenen Spieloberfläche.

## Layoutmaße und verbleibende Fläche

Bei UI 100 %: Außenrand 32, Kopf-/Arbeitsbeginn y=110, rechte Spalte 252,
Zwischenraum 20, unterer Bereich 82 logische Einheiten. Das Board reserviert
156×126 für Hinweise plus 12 rechts/unten; kleine Raster werden darin zentriert.
Die tatsächlich genutzten Hinweisflächen reichen bei kleinen Rastern bis an deren
Kanten. Beide Varianten verwenden denselben Ziffernfont und dieselbe Slotkapazität.

| Logische Fläche / UI | Board einschließlich Hinweise | Rasterviewport | Standard-Demozoom |
| --- | --- | --- | --- |
| 1920×1080 / 100 % | 1584×888, Ursprung 32/110 | 1416×750 | F-02: 18; F-01/F-03: 24 Einheiten/Zelle |
| 2560×1440 / 100 % | 2224×1248, Ursprung 32/110 | 2056×1110 | Unverändert; keine automatische Zellvergrößerung |
| 1600×900 / 100 % | 1264×708 | 1096×570 | Unverändert |
| 1600×900 / 125 % | 1180×660 | 973×490,5 | Unverändert |
| 1280×720 / 125 % | 860×480, Ursprung 40/137,5 | 653×310,5 | Unverändert; Navigation erschließt den übrigen Ausschnitt |

F-02 startet bewusst bei 75 % Arbeitszoom, damit sein 720×720-Raster auf 1080p
vollständig bleibt. Das ist ein Z1-Demostart, keine Änderung des normalen P1-Zooms.
F-01 bleibt 480×480; F-03 zeigt bei 24 Einheiten/Zelle rund 59×31 Zellen im
1080p-Ausschnitt. 1440p gibt mehr Ausschnitt beziehungsweise ruhige Ränder.
Keine dieser Angaben belegt physische Windows-DPI.

## E-02/E-03 · Richtungen, Tokens und Zustände

| Token / Wirkung | V1: hell und redaktionell | V2: ruhig und atmosphärisch |
| --- | --- | --- |
| Hintergrund | `#e9ece7`, sehr feine horizontale Materiallinien, schmaler Albumstrich | `#526d60`, geschichtete dunklere Flächen und gezeichnetes Blattwerk mit Konturen/Adern |
| Arbeitsrahmen / Seitenfläche | `#fcfcf7`, fast rechteckig, Radius 3, feine Grenze | `#f4efdf`, Radius 10, weicher Schatten, wärmere Materialität |
| Rasterpapier / Tinte | Gemeinsam `#faf6ec` / `#343f42`; unveränderter Board-Kern | Gleich |
| UI-Schrift | Open Sans SemiBold, 15; Titel 30, zusätzliche Laufweite/Embolden, Versalien | Gleiche präzise Grundschrift; Titel leicht geneigt, Satzschreibung, weichere Hierarchie |
| Kleine Hierarchie | Blattzeile 14, Rubrik 12, Status 13 | Gleiches Größenraster, natürlichere Rubrikschreibung |
| Aktives Werkzeug | `#a8452e`, weiße Schrift | `#38594c`, weiße Schrift |
| Hover | `#e0e9dd`, dunkle Schrift | Gleich; Farbe bleibt als echte Farbfläche unverändert |
| Deaktivierte History | Gedämpfte Schrift `#788277`, native Buttons nicht auslösbar | Gleich |
| Auswahl einer Rätselfarbe | Originalfläche, dicker dunkler Rand/Schlagschatten, weißer Punkt mit dunkler Kontur | Gleich; Werkzeug bleibt separat sichtbar |
| Hilfe/Menü | Helle abgegrenzte Karte mit Titel/Schließen, vollflächiger Eingabeschutz | Wärmere Karte vor abgedunkelter Illustration |
| Strich / H1 / Überlauf | Bestehende Vorschau, Live-Zähler, dezenter farbiger H1-Strich, originale Tokens und `…` | Unveränderte Daten und Mechanik |

Die V2-Illustration ist prozedural gezeichnet und fixtureunabhängig. Sie besteht aus
gebogenen Blattflächen, dunklen Konturen/Mitteladern und gestaffelten Farbflächen;
sie ist kein leeres Ersatzrechteck. Alle Arbeitsflächen bleiben opak. Weder
Geografie noch neue Kapitel, Objektmotive oder eine Album-Themenwahl werden daraus
abgeleitet. Herkunft/Lizenzen: [Assetnachweis](../../prototypes/p1/design/ASSETS.md).

### Kontrastprüfung an den tatsächlichen Flächen

Relative sRGB-Luminanzverhältnisse, auf zwei Stellen gerundet; die Capture-Metadaten
berechnen die Rätselfarben direkt aus der Fixture und der tatsächlichen Framefarbe.
Keine Behauptung einer umfassenden Accessibility-Zertifizierung.

| Vordergrund | V1 `#fcfcf7` | V2 `#f4efdf` | Gemeinsames Raster `#faf6ec` |
| --- | ---: | ---: | ---: |
| UI-Tinte `#293e3d` | 11,03 | 9,87 | 10,51 |
| Rätselfarbe 1 `#343f42` | 10,54 | 9,43 | 10,05 |
| Rätselfarbe 2 `#edca78` | 1,53 | 1,37 | 1,46 |
| Rätselfarbe 3 `#bd604a` | 4,13 | 3,70 | 3,94 |
| Rätselfarbe 4 `#6c9aab` | 2,98 | 2,67 | 2,84 |

UI-Tinte auf Hoverfläche erreicht 9,11:1; weiße V2-Kopfschrift auf dem freien
Hintergrund 5,65:1. Deaktivierte Schrift erreicht 3,88:1 beziehungsweise 3,47:1
und ist zusätzlich durch die nicht auslösbare Aktion unterscheidbar.
Die hellen originalen Hinweisfarben, besonders Gelb, haben begrenzten Textkontrast.
V1 bietet ihnen etwas mehr Kontrast als V2. Die Entwürfe verändern dafür weder
Rätselfarben noch Hinweiszahlen oder H1-Zuordnung. Auswahl und Werkzeugstatus sind
durch Punkt/Rand beziehungsweise Beschriftung unabhängig von der Farberkennung.
Eine spätere zusätzliche Kontrasthilfe für Hinweisziffern wäre konkret vor Z2 zu
entscheiden; sie wird hier nicht als bereits gelöste Barrierefreiheit ausgegeben.

## E-04/E-05 · Vergleichsdaten, Interaktion und Renderzuordnung

`design/demo.gd`, Revision `z1-demo-1`, definiert explizite Striche durch das
bestehende Session-/Gestenmodell. Keine Lösungsmatrix, Proofs oder Revealressourcen
werden zur Erzeugung der Demo-Eingaben gelesen. F-02 enthält einen langen blauen
Strich, kleinere gelbe/rote/dunkle Teilflächen, X und unbekannte Zellen. Das ist
ein Beispielspielerstand, keine Startbelegung oder als korrekt behauptete Lösung.
Ein abschließender echter Strich mit anschließendem Undo erzeugt den Redo-Zweig.
Die Original-Fixtures samt Proofs werden byteweise gegen die Startbasis geprüft.

Ein Variantenwechsel behält Session, History, Pan, Zoom und Hinweislesepositionen;
er verwirft zuerst die laufende Vorschau. Fixturewechsel/Reset stellt den jeweiligen
Demo-Zustand wieder her. H1-Schalter/UI-Skalierung bleiben sitzungsweit. Board und
Miniatur beziehen identische `visible_cells()` einschließlich Vorschau. Öffnen
einer Hilfe-/Menükarte bricht laufende Gesten ab; der Schild fängt Mausaktionen ab.

Die PNGs werden direkt aus echten Godot-SubViewports gespeichert, nicht nachgemalt.
Im technischen Product-Artefakt liegen sie unter `z1/renders/`. Diese Tabelle ist
die reproduzierbare Artefaktzuordnung; `v1` und `v2` bezeichnen stets denselben Fall.

| Zweck | Dateinamen je Variante |
| --- | --- |
| F-02 / 1080p, Hauptvergleich | `v1-f02-1920x1080.png`, `v2-f02-1920x1080.png` |
| F-02 / 1440p | `v1-f02-2560x1440.png`, `v2-f02-2560x1440.png` |
| F-01 / 1080p | `v1-f01-1920x1080.png`, `v2-f01-1920x1080.png` |
| F-03 / 1080p, Stress | `v1-f03-1920x1080.png`, `v2-f03-1920x1080.png` |
| Enger Fall 1280×720/UI 125 % | `v1-tight-ui125.png`, `v2-tight-ui125.png` |
| Geöffnete Hilfe im engen Fall | `v1-help-ui125.png`, `v2-help-ui125.png` |
| Menü, Hover, deaktivierte Aktionen | Je `v1`/`v2` plus `-menu.png`, `-hover.png`, `-undo-disabled.png`, `-redo-disabled.png` |
| Erfüllte Hinweise, tatsächliches On/Off-Paar | Je `v1`/`v2` plus `-h1-on.png`, `-h1-off.png` |
| Vollständige überlaufende Hinweise | `v1-full-hint.png`, `v2-full-hint.png` |
| Laufender Strich/Zähler 8 | `v1-stroke-8.png`, `v2-stroke-8.png` |

`z1-render-report.json` nennt pro PNG Quellcommit, Fixture, Demo-Revision,
Zell-/History-/Hinweishashes, Palette, Viewzustand, Board-/Rasterviewport, Zoom,
UI-Skalierung, logische Fläche, Miniaturgleichheit, Zustand und Kontrastwerte.
`z1-report.json` bindet zusätzlich Checkout/Test-Merge, Basis, Baumzustand, Run,
Quell-/Fixture-/PNG-/EXE-Hashes und Engineversion. Der Python-Prüfer vergleicht
sämtliche Kerndaten/Geometrien zwischen den vier Variantenpaaren. Die größere
Fläche verändert keine Arbeitszellen. Das vollständige P1-Rendering bleibt separat.

## E-06 · Windows-Probe, Empfehlung und Entscheidung

`z1/picross-z1-windows-x86_64.zip` ist ein eigenständiges vollständiges ZIP mit
`picross-z1.exe`, Konsolen-EXE, START.txt, Prüfreport und Asset-/Schriftlizenzhinweis.
Keine Godot-Installation nötig. Die Z1-Hauptszene wird ausschließlich in der
temporären Exportkopie gewählt. Reguläres `picross-p1-windows-x86_64.zip` und
bestehende H1-Probe bleiben eigene Exporte. Keine Enginearchive, Builds oder Saves
werden eingecheckt. [Start-/Prüfanleitung](../../prototypes/p1/design/README.md).

| Bewertung | V1 | V2 |
| --- | --- | --- |
| Längere Rasterarbeit | Sehr ruhige Ränder, stärkere Flächentrennung und etwas höherer Hinweistextkontrast | Gleichwertige Geometrie; dunkler Außenraum rahmt die Arbeit stärker ein |
| Identität | Redaktionelles Albumgefühl durch Satz, Weißraum und Akzent; eher sachlich | Deutlich wärmere, illustrierte Atmosphäre; prägnantere eigenständige Außenansicht |
| Kleine Raster | Viel bewusst ruhiger Weißraum | Ruhiger Papierbereich, Illustration bleibt am Rand |
| Großraster / enge Fläche | Klare Konzentration; wenig visuelle Konkurrenz | Illustration tritt zurück, kann bei voller Rasterfläche nur am Rand wirken |
| Schwäche | Weniger erzählerische Atmosphäre; große freie Flächen können nüchtern wirken | Gelbe/blaue Originalhinweise kontrastieren schwächer; Ornament kann auf Dauer Aufmerksamkeit binden |

**Empfehlung:** V1 als Grundlage für lange Großrastersitzungen bevorzugen, vor einer
Übernahme aber beide am gelieferten Windows-Artefakt vergleichen. V2 ist die konkrete
Alternative, wenn die stärkere ruhige Illustration höher gewichtet wird. Eine
Kombination aus V1-Arbeitsfläche und zurückhaltender V2-Randillustration ist denkbar,
wird jedoch nicht eigenmächtig umgesetzt oder zur gewählten Richtung erklärt.

Offene Eigentümerentscheidungen **vor Z2**: V1/V2 oder konkret bezeichnete Kombination;
gewünschte Material-/Titel-/Hintergrundänderungen anhand benannter PNGs und Commit;
Bewertung der schmalen Spalte samt kleiner Miniatur im engen Fall; eventuelle
Kontrasthilfe bei unveränderten Rätselfarben. Sammelalbum/Reisealbum bleibt eine
eigene Themenfrage. Das Ergebnis wird erst durch ausdrückliche Entscheidung im
#23-Body verbindlich. Z1 schließt #21 nicht.

## Prüfnachweise und Abnahmegrenzen

Neue Szene tatsächlich ausgeführt: Layoutmatrix aus drei Fixtures × vier Flächen ×
zwei UI-Skalierungen, Variantenidentität, Undo/Redo, Farbauswahl, Werkzeugwahl,
Board-/Miniaturnavigation, Einzelhinweisnavigation, Vorschauabbruch beim Stilwechsel,
Hilfe/Menü samt Eingabesperre, Save-Sentinel im eigenen isolierten Profil und
statischer vollständiger Abhängigkeitsabschluss ohne normalen Savepfad.
Der Capture-Test verweigert vor Dateizugriffen den Start, wenn `user://` nicht
unter dem vom Harness benannten temporären Profil liegt. Der Negativpfad ohne
Profilbindung muss mit Exit 2 und `Z1_ISOLATION_REQUIRED` enden.
Echte Renderprüfungen prüfen unveränderte Farbpixel, Board/Miniatur und H1-On/Off.

Die technische Abschlussbindung liegt im Draft-PR: finaler Head, Test-Merge,
erfolgreiche `product`/`docs`/`preflight`, vollständiger Diffcheck, heruntergeladenes
Windows-Artefakt, Hashprüfung, tatsächlich ausgeführter Windows-Start und getrennter
Selbstreview. Der Produktweg enthält weiterhin alle G1-/H1-, History-, Save-/Recovery-,
500-Aktionen-/Neustart- und regulären Renderregressionen. Lokale Entwicklungsläufe
auf verändertem Arbeitsbaum werden nicht als finale CI ausgegeben.

**Vor Übergabe:** Implementierer kontrolliert die acht Kernbilder und die zusätzlichen
Zustände visuell und dokumentiert den konkreten Bildstand im PR. Synthetische
Viewporteingaben sind keine reale Mausprobe. **Vor Merge:** unabhängiges Review und
passende Mergefreigabe bleiben separat. **Vor Z2:** Eigentümerentscheidung zur
Gestaltung; vor Abschluss der Gesamtphase die längere reale Probe gemäß #21/#24.
Kein abgeschlossenes Stil-, Produkt-, DPI- oder Release-Abnahmeurteil durch Z1.
