# Buchstudie B-A · B-A-N04-T01

Stand: 01.11.2026 · ausschließlich B-A-N04 gemäß
[#493 / B-A-E04, N14–N17](https://github.com/venomenon328/picross/issues/493),
[Umsetzungsvorbereitung B-A-V05](https://github.com/venomenon328/picross/pull/495#issuecomment-6552117759).
Ausgangshead: `8b48e0cf94dc086225aa5444ea5cb253527b6d22`;
Basis: `864c4e6289df15ea7b3522b850542ece3489160f`.
Branch `feat/493-book-study`, bestehender Draft-PR #495 gegen `main`.
Aktueller Lieferhead, CI, Originalbelege und getrenntes Selbstreview werden im PR
gebunden. Dieses Dokument beschreibt den ausführbaren Prüfvertrag. B-B bleibt
unimplementiert, #493 offen; dieser Auftrag erlaubt keinen Merge.
N01–N13 und die in R03 bestätigte Behebung von R02-B01 bleiben erhalten.
Frühere T01-Lieferungen und R01–R04 bleiben an ihre damaligen Stände gebunden.

## Doppelseite und Arbeitskapazität

Der ruhende Katalog liegt auf zwei vollständigen Papierseiten mit mittiger Bindung.
Die reguläre Kataloglogik behält Filter, globale Sortierung, Metadaten, Blattnummern,
ID-Aktionen, Miniaturen und Reset. Höchstens 24 aktive Karten verteilen sich auf
beide Hälften; 27 synthetische Instanzen liefern eine volle und eine teilweise
belegte Doppelseite. Zuerst stehen bis zu zwölf Karten links, die übrigen bis zu
zwölf rechts, innerhalb jeder Hälfte zeilenweise. 3/12/13/24 Karten ergeben
3+0/12+0/12+1/12+12; die letzte Seite bei 27 enthält 3+0. Responsive Spalten
ändern diese Mitgliedschaft nicht. Jede Hälfte hat ihren eigenen Scrollbereich
und Offset. Rad, Scrollleiste und Sichtbarmachen bewegen nur ihre Hälfte; auch
ein rechter Anschlag oder eine leere rechte Seite leiten nichts nach links weiter.
Bei knapper Breite sinkt die Spaltenzahl;
Schrift, Kartengrößen und Trefferflächen werden nicht verkleinert.

Ein echter Weiterbefehl blättert rechts nach links, Zurück links nach rechts,
jeweils **0,85 s**. Randbefehle und unveränderte Ziele bewegen nichts. Filter und
Sortierung wirken sofort auf den Gesamtbestand vor der Seitenauswahl.
Eine echte Filter-/Sortieränderung setzt Seite und beide Offsets auf null;
unveränderte Auswahl erhält beide. Ein echter Blattwechsel beginnt auf dem Ziel
mit zwei Nullwerten, sein Abbruch erhält beide Quellwerte. Erneutes Anzeigen
bewahrt auch den rechten Offset trotz der geerbten linken Scrollproperty.
Nach Containerneuanordnung werden beide Werte getrennt gültig begrenzt;
Generationsprüfung verhindert verspätetes Wiederherstellen eines alten Katalogs.

Neu oder begonnen öffnet mit **drei getrennten Blättern und insgesamt 3,0 s**
Bewegung nach links. Die Kamera fährt im zweiten Teil auf die rechte Arbeitsseite
mit Bindung links. Zusätzliche Blätter bleiben neutral. Schrift wird nie gespiegelt.
Die Arbeitskamera zeigt jetzt zusätzlich die obere Buchkante samt Deckel und
Seitenblock. Breitere Deckel bleiben seitlich sichtbar. Die untere Kante liegt
weiterhin außerhalb des Arbeitsausschnitts; der Katalog zeigt das ganze Buch.

Boardfläche, Rasterfit, gewünschte Zellgröße, Hinweisfont, Slots, Reserven,
Miniatur, Originalpalette und die drei SL-Rahmen behalten ihre regulären Budgets.
Kleine Rätsel werden nicht künstlich vergrößert. Titel, Katalogreiter und obere
Navigation orientieren sich an der projizierten Papierkante. Im Katalog bestimmen
Papierkante und Falzwölbung Außenabstand, Fußzeile und Seitenabstand. Die Hüllen
der tatsächlich gerenderten Glyphen und Konturen einschließlich Antialiasing
müssen in den drei gebundenen Konfigurationen und gezielt bei 1920×1200/UI100
mindestens **acht physische Pixel** innerhalb des flachen Papierbereichs
liegen. Diese Aussage ersetzt kein Raster-/Hinweisbudget durch kleinere Controls.
N16 leitet Kopf, Kartenclip und beide Fußbereiche ausschließlich aus der bereits
in Viewportpixel projizierten Papierfläche ab. Der geerbte 16:9-Materialversatz
wird nicht nochmals addiert. Am Ausgangsstand war dieser doppelte Y-Versatz
bei 1920×1200 genau 60 Pixel; die Fußaktionen lagen dadurch auf Block/Leder.

Gelöst öffnet direkt die stabile Endansicht. Deren bestätigter Reset öffnet dasselbe
leere Blatt ohne Buchanimation. Die separate 2,15-s-Abschlussdarstellung bleibt.

## Material, Wölbung und Controls

Die bestehende A-Quelle `art/book/bp2-a-inventarband.png` bleibt bytegleich:
SHA-256 `957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a`.
Sie bleibt Qualitätsreferenz und reguläres Produktasset. Der Studien-Einbandshader
verwendet keine Ausschnitte mehr daraus: N02 dehnte schmale Streifen des fertigen
Buchbilds auf Deckel, Rücken, Lippe und Untergrund. Eingebrannte Buch-/Untergrund-
kanten und Schatten erschienen dadurch an geometrisch unpassenden Stellen.

N03 verwendet eine eigene homogene Ledertextur `study/book/leather.png`,
1254×1254, 4.089.216 Bytes, SHA-256
`58372a4329973e3ad308fde17ab5bc77148d7f724e55671e540bb5344f8e0f41`.
[Prompt, Herkunft, Rechte und Import](../game/study/book/leather.json) binden die
unverändert kopierte imagegen-Ausgabe ohne Fremdvorlage. Verlustloser Import mit
Mipmaps und wiederholbarer Weltkoordinatenzuordnung; keine Buchsilhouette,
Fremdfläche oder fertigen Schlagschatten im Material.

`binding.gd` konstruiert gerundete Deckelrollen, Fasen, Seitenblock und flexiblen
Rücken aus zusammenhängenden Ringen. Die oberste Blockkontur folgt der ruhenden
Papierwölbung einschließlich ihrer verkürzten Enden; die unteren Ringe laufen an
beiden Seiten bis zur Deckelschulter. N14 entfernt ausschließlich die 46 kleinen
dekorativen Kopf-/Fußbandmeshes: Ein nativer Vergleich desselben N03-Frames mit
und ohne diese Meshes ordnet ihnen die durchstoßenden Zacken an beiden Enden zu.
Papier, komplette Blöcke, Deckel und Rücken bleiben erhalten. Es gibt keine
Kaschierung durch Abdunkeln, Beschnitt oder überdeckende Fläche.
Der Rücken verbindet beide Deckel auch unten. Beleuchtung, Lederabrieb und
Kontaktschatten folgen der Geometrie. Sechs gefilterte sichtbare Lagen vermeiden unaufgelöste
feine Linien. Breite, flache Unregelmäßigkeiten halten auch die Blocknormalen
ruhig; hochfrequente Subpixelwellen erzeugten zuvor diagonale Moiréflecken.
Kameras und Arbeitsbudgets bleiben unverändert.

N15 ersetzt den synthetischen Untergrund durch das originale zusammenhängende
Umgebungsbild `study/book/table.png`: 1536×1024, 3.203.044 Bytes, SHA-256
`5b02fe08710efb47df7b23307f460035aebaa3fa411e846b4a06558cc79678da`.
[Vollständiger Prompt, tatsächliches Bildwerkzeug, Rechte und Import](../game/study/book/table.json)
binden die unverändert kopierte imagegen-Ausgabe ohne Fremdvorlage. Die Holzfläche
mit Leinen am linken Außenrand enthält weder Buch noch UI oder Buchschatten.
Eine feste 48×32-Weltfläche erhält das Bild ohne Kachelung und ohne Verzerrung
seines Seitenverhältnisses. Die Kamera bewegt Buch und Umgebung gemeinsam;
Kontaktverschattung entsteht getrennt aus der Deckelgeometrie. Verlustloser
sRGB-Import, Mipmaps, lineare Mipmapfilterung und deaktiviertes Repeat sind gebunden.

Die Innenflächen verwenden die originale neue Bildtextur `study/book/paper.png`,
1254×1254, 2.564.246 Bytes, SHA-256
`1af9f61957619d7cea98b69021688b0b78997d84baf93698c9f02dcbb866362f`.
[Herkunft, vollständiger Prompt, Rechte und Import](../game/study/book/paper.json)
binden die unverändert kopierte imagegen-Ausgabe ohne Fremdvorlage. Verlustloser
Import, Mipmaps, lineare Filterung, kein Repeat; das Mischen mit 55 % hellem
Elfenbein hält Fasern und Alterung unter Hinweisen zurückhaltend. Katalogseite,
Seitenhälfte und Arbeits-ID bestimmen feste Ausschnitte. Vorder- und Rückseite
besitzen eigene Zuordnungen. Keine Spiegelung oder Zufallsvariation pro Frame;
dieselbe Seite behält nach Rückkehr ihre Papierpixel.

Die ruhende Wölbung ist reale Vertexgeometrie: 0,26 Welteinheiten hoch und nach
0,75 Einheiten vollständig flach. Sie verändert Normalen und die sichtbare obere/
untere Papierkontur. Eine schmale geometrische Lücke lässt die Bindung frei.
Das Licht folgt der Wölbung. Die UI-Sicherheitsfläche liegt außerhalb dieses
Streifens, die präzise Rasterfläche bleibt eben. Bewegte Inhalte folgen den
Blattvertices; kein nachträglich über die ganze UI gelegter Verzerrungseffekt.

Studienbuttons und geschlossene Dropdowns haben transparente Füllung. Normal,
Hover, Gedrückt, Auswahl, Deaktiviert und Fokus behalten unterscheidbare Konturen.
Hover und Druck verstärken die vorhandene vollständige Kontur in zwei Stärken;
der isolierte kurze obere Hoverstrich entfällt. Auswahlunterstrich, Fokusinnenkontur
und Deaktiviertmarkierung bleiben. Native Zustandsbilder und eine Pixelgegenprobe
mit wieder eingesetztem alten Strich ergänzen die Sichtprüfung. Die native
Standardbeschriftung wird im
Opt-in unterdrückt, damit der eigene Text genau einmal erscheint. Farbproben
behalten ihre Originalpixel; Popup-, Dialog- und Fehlerflächen bleiben deckend.
Die zwei gemeinsamen Controls haben einen expliziten, standardmäßig deaktivierten
Schalter. Die reguläre Produktdarstellung bleibt unverändert.

Der leere Tooltip wurde mit echtem Mausweg und normaler 0,5-s-Verzögerung
reproduziert: Godot ruft die benutzerdefinierte Factory auch für leeren Text auf.
Das bisher stets angelegte Panel erschien als 29×46-Pixel-Rahmen allein aus
Rändern und leerem Label. `BookButton` normalisiert Whitespace und gibt vor dem
Anlegen eines leeren Panels `null` zurück. Das korrigiert auch den gemeinsamen
Defaultpfad; sinnvolle Hilfen behalten ihre Darstellung. Vollständig beschriftete
Fußaktionen erhalten keinen redundanten Text. Modus-, Reset-, Werkzeug-, Icon-
und Richtungshilfen bleiben erhalten.
Die passive Modusbeschriftung `CatalogTip` verwendet dieselbe Leervorgabe;
zwei gezielte 1920er-Fälle prüfen auch diesen Labelpfad ohne neue Größenmatrix.

## Zustände, Rückkehr und Eingabebesitz

Ruhende Ansichten verwenden direkte Controls. Während der Bewegung liegt dieselbe
UI in einem transparenten SubViewport in tatsächlicher Fensterauflösung. Ein
Snapshot bindet den Quellzustand, die aktuelle UI den Zielzustand. Beim Blättern
trägt die Rückseite die andere Zielhälfte; bei der Öffnung bleibt sie neutral.
Premultiplizierte Alphakomposition erhält geglättete Text-/Rasterkanten.

Der tatsächliche Katalogreiter löst aus ruhender Arbeit oder stabiler Endansicht
eine **1,8-s-Rückkehr** mit Herauszoomen und drei Blättern von links nach rechts aus.
Der Snapshot enthält die aktuelle Bearbeitung. Vor dem bestehenden RAM-Flush wird
eine laufende Geste abgebrochen. Danach bleiben Filter, Sortierung, Richtung,
Seite, beide Scrollpositionen und Auswahl erhalten; die Miniatur zeigt den neuen Fortschritt.
`show_album()` selbst bleibt unmittelbar für Start, Reset, Information und interne
Stabilisierung. Idle-Escape navigiert nicht. Eine aktive Endanimation nimmt noch
keinen Rückkehrbefehl an.

`CATALOG/WORK → PREPARING → OPENING → CATALOG/WORK` bindet Quelle, Ziel und IDs
vor dem ersten Await. Generationen entwerten alte Fortsetzungen. Vorbereitung,
Bewegungszeit und Frameabstände werden getrennt gemessen.

| Unterbrechung in Vorbereitung oder Bewegung | Stabile Wirkung |
| --- | --- |
| Resize, UI-Skalierung, Fokusverlust | Gebundenes Ziel: Katalog oder ausgewählte rechte Arbeitsseite; gültig neu vermessen. |
| Escape oder ausdrücklicher Abbruch | Blättern/Öffnen: erhaltener Quellkatalog. Rückkehr: gebundener Zielkatalog, jeweils mit vollständigem Kontext. |
| Weitere Eingabe | Verwerfen, keine Warteschlange, kein Durchklicken oder späteres Nachholen. |
| Normales Ende | Gebundenes Ziel; gehaltene Tasten loslassen, danach frisches Down. |
| Beenden | Generation entwerten, Ressourcen lösen, Prozess beenden. |

Die UI einschließlich globaler Board-Eingabe ist während Vorbereitung und Bewegung
deaktiviert. Gesten, Tooltips und Dropdowns werden vorher geschlossen. Radereignisse
sind keine gehaltenen Tasten. Die Eingabesperre erfasst nur ihre eigenen Ereignisse;
eine von Board konsumierte normale Release-Aktion darf keinen alten Down-Merker
hinterlassen. Zellen, History/Redo und Save-Aktionen ändern sich durch Präsentation
nicht. Bearbeitung und Sortierung bleiben im RAM; echte Profile bleiben unberührt.
Vor Abschluss erscheinen auf keiner Fläche verdiente Namen/Reveals, auch nicht
auf Rückseiten. Miniaturen zeigen eigene, auch falsche Einträge.

Reguläre Save-/Recovery-Integration und #485–#487 bleiben B-B. Informations-/Hilfswege
sind vorhandene unmittelbare UI; ihre vollständige Buchnavigation wird nicht vorgezogen.

## Gültige Instanzen und Nachweise

`inputs.gd` prüft die Registry mit dem unveränderten regulären Validator, bevor sie
den Cache erreicht. Jede der 27 IDs besitzt einen eigenen Schlüssel, Slot,
Definitionspfad und Revealpfad. 27 tatsächliche JSON-Dateien und 27 kleine eigene
SVG-Sentinels liegen unter `study/book/data` beziehungsweise `study/book/art`.
Der einzige Adapter ist der feste Studienpräfix vor den regulären relativen
`data/`-/`art/`-Pfaden. Jede Definition wird geladen, gegen ID/Pfadbindung und den
unveränderten Definitionsvalidator mit dessen vorhandener expliziter Study-Asset-
Allowlist geprüft. Auch `reveal.definition_id` gehört zur jeweiligen Instanz.
Der Generator wiederholt drei Formen; er erzeugt keine weiteren Puzzleformen.
Geprüfter Tree, Runtime und beide PCKs verwenden dieselben Dateien.

| Fenster / UI | Fall | Hauptprüfung |
| --- | --- | --- |
| 1280×720 / 125 % | T01, 20×20 Mono | Kleine Fläche, unverkleinerte Karten und Controls. |
| 1920×1080 / 100 % | T06, 50×50 Farbe | Lange Hinweise, Großfall, Material und Bewegung. |
| 2560×1440 / 125 % | T08, 40×30 Farbe | Rechteck, getrennte UI-/Rastergrößen, Übergabe. |
| 1920×1200 / 100 % | gezielter N16-Fall | Kopf/Fuß, Kartenclip, Arbeitskopf, originale Glyphenhüllen und Rückkehrübergabe. |

Die vierte Zeile dupliziert nicht die vollständige Größen-/Tooltipmatrix.
UI125 sowie 1920×1192, ×1208 und ×1088 erhalten günstige Geometriegrenzen.
`n04_cases.gd` ergänzt kleine echte Katalogbestände 0/1/12/13/24/27, getrennte
Rad-/Scrollleisteneingaben, Sichtbarmachen, leere rechte Hälfte, Anschläge,
unterschiedliche Offsets, echte Kartenklicks beider Hälften, Bearbeitung und
Rückkehr, No-ops, globale Änderungen und unabhängiges Resize-Clamping.
Die bestehende 24er-Unterbrechungsmatrix bindet beide Quell-/Zieloffsets vor
und nach Await, einschließlich tatsächlichem Resize und UI-Wechsel.

Native Prüfungen liefern Pointerrouten auf beiden Kataloghälften, Rand-/Leerfälle,
globale Sortierung, drei Einzelblätter, Popup-/Gestenabbruch, 24 Kombinationen aus
Wechselart/Phase/Unterbrechung, Ressourcenfreigabe, gehaltene Taste/frisches Down,
bearbeitete Rückkehr, direkte Endansicht und Reset. Ein kopiertes T34 auf der zweiten
Seite beweist die verdiente Revealzuordnung. Billige Gegenproben weisen doppelte
IDs/Schlüssel/Slots/Pfade sowie fremde Definitions-/Revealzuordnungen ab.

Drei Arbeitsübergaben und zwei Rückkehrübergaben (1080p und gezielt 1920×1200)
werden auf vollständigen nativen
Originalframes geprüft: höchstens vier Kanalstufen und 0,1 mittlere Kanalstufen
Differenz. Ein Pixel Versatz und eine Alphamutation müssen scheitern. Die Geometrie
bezieht sich auf das neue Layout, nicht auf alte absolute Titelpositionen.

`opening.avi` enthält echte Engineframes bei normaler 30-fps-Wiedergabe: Blättern
in beide Richtungen, volle Öffnung, echte Zellbearbeitung und Rückkehr. Der Film
endet im lebenden Katalog mit aktuellem Fortschritt. `movie.json` bindet Phasen,
Vorbereitung und Zeit-/Framefolgen. Ein ruhiger nativer Öffnungslauf misst ohne
Screenshotarbeit. Aufnahme-Wandzeit, Filmzeit und native Bewegungszeit bleiben
getrennt; daraus folgt keine Hardware-FPS-Garantie.

N03 ergänzt reale verzögerte Hoverwege in denselben drei Konfigurationen: drei
beschriftete Fußaktionen, Whitespace, Richtung, Reset einer begonnenen Karte,
Modus, Werkzeug, Hilfe und langer aktueller Randtext. Wechsel, Verlassen, Klick,
Fokusverlust, Resize, UI-Skalierung und Bewegungsbeginn/-ende prüfen Lebensdauer
und ausbleibendes Wiederaufleben. Labeltext, Mindestmaße und Popupgrenzen werden
erfasst; Originalbilder erlauben die Sichtprüfung. Gegenbeispiele stellen leeren
Panelaufbau und alten Hoverstrich wieder her. Der unabhängige Ergebnisguard
verwirft fehlende Fälle, umgangene Verzögerung, leeren/veralteten Text,
abgeschnittene Geometrie, überlebende Popups und wirkungslose Gegenproben.
Nach Fenstereintritt an einer sicheren Position und dessen abgearbeitetem
OS-Ereignis aktivieren native Viewport-Zeigerereignisse den normalen GUI-/
Verzögerungspfad wie im bestehenden KAT-Prüfer. Die logischen Testpositionen
werden nicht auf die physische Monitorbreite begrenzt. Jeder Fall verlangt auch
den tatsächlichen Hoverzustand des Controls; die Tooltipfactory wird nicht direkt
aufgerufen.
Nach dem unveränderten Tooltipdelay wird ein vollständiger Renderabschluss
abgewartet und dessen Originalframe direkt gespeichert; redundante zusätzliche
Warteframes um dieselbe Aufnahme entfallen. Fälle, Originalauflösung und das
300-s-Phasenlimit bleiben erhalten. Die Tooltipgruppe protokolliert ihre Laufzeit.

Die eigene Sichtprüfung vergleicht A als Qualitätsreferenz sowie gebundene N03-
und N04-Originalframes. Je Katalogbild der vier Flächen entstehen sechs
unskalierte Details beider unterer Ecken, des oberen/unteren Falzes und beider Außenränder
mit dokumentiertem Quellrechteck. Vollansichten, Arbeitsränder und Film ergänzen
diese Ausschnitte. Iterationen, Korrekturen und Materialurteil stehen im PR.
Das ersetzt weder B-A-R05 noch die persönliche Kandidatenwahl.

## Ressourcen, Export, CI und Gates

Höchstens drei bewegte Blätter mit je 1105 Vertices/2048 Dreiecken, zwei ruhende
Papierflächen und feste Deckel-/Seitenlagen. Kein Katalogtexturcache. Ein UI-Renderziel
plus RGBA-Snapshot benötigt 7,03/15,82/28,13 MiB bei 720p/1080p/1440p; einschließlich
konservativ vier Depthbytes je Pixel 10,55/23,73/42,19 MiB. Einfrieren benötigt kurz
zusätzlich eine CPU-Bildkopie. Das von der gemeinsamen UI referenzierte A umfasst
weiterhin konservativ 14.745.600 RGBA-Bytes; der Einbandshader sampelt es nicht.
Papier und Leder umfassen jeweils 6.290.064 RGBA-Bytes, mit Mipmaps jeweils
höchstens 8.386.752 Bytes (ca. 8 MiB). `resources.binding` zählt die tatsächlichen
statischen Flächen, Vertices und Dreiecke: nach Entfernung der Zierbänder
6 Flächen, 8.511 Vertices, 16.262 Dreiecke statt 52/11.869/21.230.
Das Tischbild benötigt 6.291.456 RGBA-Bytes, mit Mipmaps höchstens 8.388.608 Bytes.
Bei 1920×1200 benötigen Renderziel/Snapshot 18.432.000 Bytes, mit konservativer
Depthobergrenze 27.648.000 Bytes. Tatsächliche Import-
und Paketgrößen werden gemessen. Font-/Zellatlanten, SL-Rahmen, Hauptframebuffer
und Treiberoverhead sind separat. Nach Ende/Abbruch sind Übergaberessourcen frei.

Godot Standard 4.7.2, GL Compatibility, Web ohne Threads oder Erweiterungen.
Tatsächliche separate Windows-/Webstudienpakete erhalten externe PCK-Prüfungen
auf Einstieg, Quellen, Textur und alle Instanzen. Beide regulären Pakete werden
ebenfalls exportiert und auf Ausschluss geprüft. Windows startet den exportierten
Player und prüft Öffnung, echte Zellbearbeitung und Rückkehr sowie echtes
Standardfenster → Maximieren → Wiederherstellen über den nativen Fenstermanager.
`windows-native.json` trennt Desktop, Client, äußeren Rahmen, Framebuffer,
UI-Skalierung, OS-Skalierung und DPI; native Screenshots gehören dazu. Ein
1920×1200-Desktop bedeutet wegen Rahmen/Taskleiste nicht dieselbe Clientfläche.
Der deterministische 1920×1200-Framebuffer wird separat im nativen Prüfer erzeugt.
Linux behauptet
keinen Windowsstart. Chromium ist nicht beauftragt; Webexport ist kein Browser-
Darstellungsnachweis. Kein Deployment oder Release.

`report.json` bindet Quellen, Commit/Basis/Checkout/Run/Attempt, Materialhashes,
Importkosten, Originaldateien, Phasen, Pixelprüfzeit und tatsächliche Mengen/Bytes.
Die Exportgruppe führt die Studie einmal aus. Der Ergebnisguard liest originale
Einzelassertions, die feste Szenariomenge, Geometrie, Bewegung, Unterbrechungen,
Film und Dateien. Fehlende, manipulierte oder fehlgeschlagene Ergebnisse scheitern.
Der unabhängige Guard prüft N04-Fallmengen, Reihenfolge und beide Scrollwerte,
berechnet die Papierprojektion samt Tintenabstand aus Breite **und Höhe** neu
und liest tatsächliche PNG-/Ausschnittmaße. Er leitet keine Höhe mehr aus der
Breite ab. Kleine Mutationen prüfen fehlende Fälle, falsche Halbzuordnung,
gespiegelte/verlorene Offsets, falsche Höhe/Projektion und neue Bildquelle.
Der vollständige Base-/Head-Diff bestimmt alle Pflichtjobs. `docs`, ausgewählte
Jobs und `ci-required` müssen am Lieferstand erfolgreich sein. CI2-Ziele werden
gemessen; es gibt keinen neuen Erfolgsverzicht oder allgemeinen CI-Umbau.
Laufbilder, Filme und Exporte bleiben in ignorierter Arbeitsablage beziehungsweise
befristeten Technikartefakten, keine neue permanente Bildgalerie.

B-A-N04-T01 verlangt aktuelle Technik-, Sicht-, Export- und CI-Nachweise sowie
getrenntes Selbstreview. **B-A-R05 bleibt ein neues separates qualifiziertes technisches
und visuelles Review vor Merge.** R01–R04 nehmen N04 nicht ab. **B-A-M01** bleibt
persönliche Kandidatenwahl vor vollständigem B-A-Abschluss und vor B-B; sie darf
nach einem separat freigegebenen isolierten Merge auf main erfolgen. Der aktuelle
Auftrag enthält keine Mergefreigabe und lässt den PR als Draft.

Start und Reproduktion: [Studienanleitung](../game/study/book/README.md).
