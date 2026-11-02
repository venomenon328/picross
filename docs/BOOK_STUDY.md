# Buchstudie B-A ? gebundener Vorg?nger

Die gew?hlte N06-Fassung ist mit PR #497 auf `main@2a0d9e4` integriert.
[B-A-R08-V02](https://github.com/venomenon328/picross/pull/497#pullrequestreview-5730592686)
und [pers?nliche B-A-M01](https://github.com/venomenon328/picross/pull/497#issuecomment-6564908352)
sind abgeschlossen. B-B ?bernimmt Darstellung und Materialien in den regul?ren
Spieler: [aktueller Vertrag](BOOK_INTEGRATION.md), [B-B-T01](B_B_VERIFICATION.md).
Der gemeinsame Kern liegt jetzt unter `game/book/`; die verbleibende synthetische
Studienh?lle verwendet ihn mit isolierten Inputs. Aktive Pr?fungen binden diesen
Kern und den realen Produktlebenszyklus, keine zus?tzliche Studienexportmatrix.

Die folgenden Status-, Pfad-, Pr?f- und Exportangaben beschreiben ausdr?cklich
den damaligen B-A-Lieferstand. Seine Nachweise und Freigaben werden nicht
r?ckwirkend als B-B-Abnahme ausgegeben oder umgeschrieben.

## Historischer B-A-N06-T01-Vertrag


Stand: 01.11.2026 · isolierte visuelle Nacharbeit gemäß
[#496 / B-A-N06](https://github.com/venomenon328/picross/issues/496).
Vorab gefetchte und geprüfte Basis: `main@130a52662d59bc810fb95e08854a2b7d067fafb6`;
Branch `feat/496-book-gutter`, neuer Draft-PR gegen `main`.
Aktueller Lieferhead, CI, Originalbelege und getrenntes Selbstreview werden im PR
gebunden. Dieses Dokument beschreibt den ausführbaren Prüfvertrag. B-B bleibt
unimplementiert, #493 offen; dieser Auftrag erlaubt keinen Merge.
N01–N21, F01 und die in R03 bestätigte Behebung von R02-B01 bleiben erhalten.
N05/F01 wurden über [PR #495](https://github.com/venomenon328/picross/pull/495)
integriert. Die damaligen Eigentümerausnahmen für R06-A01/R07-A01 sind keine
nachgeholten Sichtprüfungen und gelten nicht für N06. Frühere T01 und R01–R07
bleiben historisch gebunden. N06 benötigt unabhängiges **R08**; persönliche
**B-A-M01**, B-B und Merge bleiben offen.

## N06: Buchfalz und Einbandsteg

Die Ursache des alten Schlitzes war geometrisch: beide Innenkanten lagen je
0,035 Welteinheiten neben der Mitte, entsprechend zusammen etwa 5,64 Pixeln
bei 1920×1080. Die Wölbung endete als zwei getrennte hohe Kanten; die verkürzten
Papierenden bildeten zusätzliche Einkerbungen. Der bisherige Lichtgradient
verwendete außerdem die ruhende Steigung auch während der Blattdrehung.

Die Innenkanten liegen nun je 0,004 Einheiten neben der Mitte. Zwei reale,
stetig anschließende Schultern erreichen bei Abstand 0,28 eine Höhe von 0,22;
das mittige Tal liegt auf der ebenen Papierhöhe. Ab Abstand 0,75 ist die Fläche
vollständig eben. 16 der weiterhin 64 Querspannen lösen diesen Bereich auf;
UVs bleiben an die tatsächlichen Papierkoordinaten gebunden. Lichtnormalen
folgen der Deformation einschließlich Drehung und Curl. Papierfasern und
vormultiplizierte UI-Tinte bleiben unverändert.

Ein zusammenhängender Lederdeckel enthält Rücken, Gelenkvertiefungen und beide
Deckelflächen. Seine Oberseite besteht aus passenden Streifen statt eines flachen
Fächers. Die Seitenblock-Unterkante folgt dem Gelenk mit positivem Abstand;
die inneren Lagen sind an den freien Enden enger zusammengeführt. Es gibt kein
zusätzlich aufgelegtes Band. Die Krümmung bleibt beim Blättern am inneren Tal
gebunden und landet beidseitig oberhalb des ruhenden Blocks. Zustandsautomat,
Kameras, Bewegungszeiten, Texturübergaben und UI-/Inputverträge bleiben erhalten.

`n06_cases.gd` rendert das tatsächliche Seitenmesh mit dem tatsächlichen
Vertexshader in einer kleinen separaten Szene. Nur die Fragmentausgabe wird
durch Tiefenbänder ersetzt. Ruhe und gegenüberliegende Landung müssen Tal,
angehobene Schultern und ebene Außenfläche zeigen. Wieder eingesetzter breiter
Spalt und flach gesetzte Geometrie müssen scheitern. Vier originale 640×128-PNGs
und Messwerte gehören zum bestehenden nativen Lauf. Die tatsächlichen
Leder-/Blockarrays liefern zusätzlich Gelenktiefe, Mindestabstand und Mengen.
Der Ergebnisguard verlangt diese Fälle und Dateien; acht Mutationen prüfen
fehlende Fälle, breite Lücke, flache Schulter, akzeptiertes Gegenbeispiel,
flaches Leder, Durchdringung, Budgetüberschreitung und Fokus-Reentranz. Keine neue CI-Gruppe.

Die Windowsregression legte zusätzlich einen bestehenden reentranten Fokuspfad
offen: Eine OS-Fokusmeldung während `app.reparent()` konnte `_settle()` im noch
laufenden Baumumbau auslösen. Nur diese Studienbenachrichtigung wird ans Ende
des Dispatchs verschoben und an die aktuelle Generation gebunden. Der geforderte
Zielzustand und die unmittelbare Gestenstornierung bleiben erhalten. Ein echter
`tree_exiting`-Callback prüft angehängte UI, freigegebene Capture-Ressourcen und
unveränderte Zellen/History; eine veraltete Generation darf keine spätere Bewegung
unterbrechen. Die vorherige synchrone Fassung wurde separat als Fehler reproduziert.

T01 bindet vorher/nachher die vollen Katalogbilder 1920×1080 und 1920×1200/UI100
samt unskalierten oberen/unteren Falzausschnitten, gezielte Arbeits-/Informations-
und UI125-Ansichten sowie den bestehenden echten Engine-Bewegungsfilm. Hinzu
kommen erreichbare Originalberichte und Clientbilder des finalen Windowsexports.
Der Windows-Sichtkandidat enthält nur getestete EXE/PCK, Lizenzen und kurze
Startanleitung; technische Bilder und Film bleiben getrennte befristete Belege.

## Informationsdoppelseite und Arbeitsnavigation

Einstellungen stehen links, Hilfe rechts. Beide ruhen im selben Nahmaßstab wie
die Arbeitsseite. `information.gd` ordnet die jeweils einmal vorhandenen regulären
Optionscontrols und den vollständigen Hilfetext in zwei eigene Scroll-/Clipflächen.
Schrift, Trefferflächen und Optionssignale bleiben erhalten. Der globale Titel
`Information`/`Information / ID` entfällt. Seitentitel, Umbruch und Clipgrenzen
liegen außerhalb der Falzwölbung; Navigation bleibt über dem Scrollbereich.
Die nicht gewählte Seite ist im Ruhezustand unsichtbar und erhält keinen Fokus.
Die vorhandene Auswahlliste bleibt ein natives, lesbares Popup; Übergänge schließen sie.

Der rechte Arbeitskopf lautet **Pfeil links → Katalog, Hamburger → Einstellungen,
? → Hilfe**. Der alte linke Reiter wird samt Signal/Fokus entfernt. Der Titel hat
einen eigenen Papieranker, die mittlere Menüachse samt Miniatur, Palette und
2×3-Werkzeugen bleibt geometrisch erhalten. Dieselben drei Zugänge bleiben auch
auf der stabilen Endansicht erreichbar. Im Katalog stehen Einstellungen und Hilfe
nebeneinander im Fußbereich; bei knapper Breite steht „Weiter“ in einer zweiten
Zeile. Karten-, Schrift- und Trefferbudgets bleiben erhalten.

| Route | Blatt / Dauer | Kamera |
| --- | --- | --- |
| Arbeit → Einstellungen | eins vorwärts / 0,85 s | nah, rechts → links |
| Arbeit → Hilfe | eins vorwärts / 0,85 s | nah rechts, unverändert |
| Katalog → Einstellungen | eins vorwärts / 0,85 s | weit mittig → nah links |
| Katalog → Hilfe | eins vorwärts / 0,85 s | weit mittig → nah rechts |
| Einstellungen → Hilfe | keines / 0,65 s | nur nah links → rechts |
| Hilfe → Einstellungen | keines / 0,65 s | nur nah rechts → links |
| Einstellungen → ursprüngliche Arbeit | eins zurück / 0,85 s | nah links → rechts |
| Hilfe → ursprüngliche Arbeit | eins zurück / 0,85 s | nah rechts, unverändert |
| Einstellungen → ursprünglicher Katalog | eins zurück / 0,85 s | nah links → weit mittig |
| Hilfe → ursprünglicher Katalog | eins zurück / 0,85 s | nah rechts → weit mittig |

Vorwärts dreht rechts nach links, zurück links nach rechts. Smoothstep verbindet
die gebundenen Endlagen ohne Overshoot. Die kurzen Informationstimings sind eigene
Studienparameter; 0,85/3,0/1,8 s der bisherigen Katalog-/Arbeitswege bleiben.
Seitenwechsel und beschriftetes „Zurück zum Katalog/Rätsel“ sind getrennte Aktionen.
Erneute Wahl derselben Informationsseite ist ein No-op einschließlich Scrollstand.

`information_routes.gd` bindet vor dem ersten Await genau einen Besuchsursprung:
Katalog oder tatsächlich geöffnete Arbeit/stabile Endansicht samt ID. Ein bloßes
Sessionobjekt im Katalog zählt nicht als Arbeit. Der Informationsursprung bleibt
neben `return_context` für Arbeit→Katalog bestehen. Filter, Sortierung, Richtung,
Seite, Auswahl und beide ungleichen Katalogoffsets bleiben erhalten. Eine Rückkehr
lädt keinen alten Arbeits-/Optionssnapshot: Zellen, History/Redo, Werkzeug, Farbe,
Zoomwunsch und Hinweislesestände bleiben; bewusst geänderte UI-/G/V-/Hinweis- und
Animationsoptionen gelten weiter. Jede Informationsseite behält ihren Scrollstand
während des Besuchs und begrenzt ihn bei Reflow selbst; ein neuer Besuch beginnt oben.
Es entsteht weder persistentes Informationsgedächtnis noch ein Texturcache.

Vor Eintritt aus Arbeit und vor deren Rückkehr gilt der bestehende Pflichtflush;
ein synthetisch geprüfter Schreibfehler verhindert Vorbereitung und Animation.
Katalogbesuche erzeugen keine neue Rätselsavepflicht. Gesten/Popups werden vorher
verworfen. Während Vorbereitung/Bewegung werden weitere Eingaben verworfen.
Nach gehaltenem Down braucht es Release und ein frisches Down; Fokuswiederkehr
gleicht außerhalb des Fensters erfolgte Releases mit dem tatsächlichen Tastenmask ab.

Resize/UI-Wechsel/Fokusverlust stabilisieren das gebundene Ziel. Escape während
Eintritt führt zur ursprünglichen Quelle, während Pan zur vorherigen Informationsseite
mit demselben Ursprung und während Rückkehr unmittelbar zum ursprünglichen Ziel.
Idle-Escape bekommt keine neue Rückfunktion. Jede Stabilisierung entwertet alte
Awaits und löst die Übergangsressourcen; Beenden tut dasselbe vor Prozessende.

Während Informationsbewegungen entstehen aus denselben Controls ein Quellsnapshot
und höchstens zwei native Zielseitenbilder in einem wiederverwendeten transparenten
Viewport. Links/rechts werden separat in genau ihrem Nahmaßstab aufgenommen und
auf die jeweiligen Weltseiten projiziert. Beim Pan sind beide Papierseiten mit
ihrem eigenen Inhalt sichtbar. Im Ruhezustand kehren echte Controls zurück;
alle drei Snapshots und der Viewport werden freigegeben.

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
Kleine Rätsel werden nicht künstlich vergrößert. Titel und obere
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
[Prompt, Herkunft, Rechte und Import](../game/book/leather.json) binden die
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
[Vollständiger Prompt, tatsächliches Bildwerkzeug, Rechte und Import](../game/book/table.json)
binden die unverändert kopierte imagegen-Ausgabe ohne Fremdvorlage. Die Holzfläche
mit Leinen am linken Außenrand enthält weder Buch noch UI oder Buchschatten.
Eine feste 48×32-Weltfläche erhält das Bild ohne Kachelung und ohne Verzerrung
seines Seitenverhältnisses. Die Kamera bewegt Buch und Umgebung gemeinsam;
Kontaktverschattung entsteht getrennt aus der Deckelgeometrie. Verlustloser
sRGB-Import, Mipmaps, lineare Mipmapfilterung und deaktiviertes Repeat sind gebunden.

Die Innenflächen verwenden die originale neue Bildtextur `study/book/paper.png`,
1254×1254, 2.564.246 Bytes, SHA-256
`1af9f61957619d7cea98b69021688b0b78997d84baf93698c9f02dcbb866362f`.
[Herkunft, vollständiger Prompt, Rechte und Import](../game/book/paper.json)
binden die unverändert kopierte imagegen-Ausgabe ohne Fremdvorlage. Verlustloser
Import, Mipmaps, lineare Filterung, kein Repeat; das Mischen mit 55 % hellem
Elfenbein hält Fasern und Alterung unter Hinweisen zurückhaltend. Katalogseite,
Seitenhälfte und Arbeits-ID bestimmen feste Ausschnitte. Vorder- und Rückseite
besitzen eigene Zuordnungen. Keine Spiegelung oder Zufallsvariation pro Frame;
dieselbe Seite behält nach Rückkehr ihre Papierpixel.

Die ruhende Wölbung ist seit N06 reale Schulter-/Talgeometrie: 0,22 Welteinheiten
hoch und nach 0,75 Einheiten vollständig flach. Sie verändert Normalen und die
sichtbare obere/untere Papierkontur. Die geometrische Naht ist 0,008 Einheiten breit.
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

Der linke Pfeil im rechten Arbeitskopf löst aus ruhender Arbeit oder stabiler Endansicht
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

Reguläre Save-/Recovery-Integration und #485–#487 bleiben B-B. Die oben beschriebenen
Informationswege gehören ausschließlich zur erweiterten B-A-Studie.

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

N05 ergänzt die zehn Wege mit tatsächlichen sichtbaren Buttonklicks bei
1920×1080/UI100, Kamera-/Blattspuren und getrennten Ursprungs-/Zustandswerten.
Vier gezielte Flächen prüfen beide Informationsseiten, vollständige Hilfe und
Optionen bis zum Scrollende, originale Alphahüllen und acht Pixel Papierabstand.
UI100→125→100, G/V, Hinweis-/Animationsoptionen, fehlgeschlagener Flush und stabile
Endansicht erhalten eigene Fälle. Eine günstige 24er-Entscheidungstabelle ergänzt
sechs echte Unterbrechungen vor/nach Await für Eintritt, Pan und Rückkehr; keine
zusätzliche Routen×Größen×Unterbrechungsmatrix. `native_results.py::validate_n05`
prüft Seiten, Ursprung, beide Offsets, Kameraspuren, Blattzahl, Timing und
unabhängig projizierte Hüllen; gezielte Mutationen müssen scheitern.

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
Vier zusätzliche N05-Paare binden Einstellungen links, Hilfe rechts und die
Rückkehr zu Arbeit/Katalog mit denselben Grenzen und Gegenproben: insgesamt neun.

`opening.avi` enthält echte Engineframes bei normaler 30-fps-Wiedergabe: Blättern
in beide Richtungen, volle Öffnung, echte Zellbearbeitung und Rückkehr. Der Film
zeigt zusätzlich alle zehn Informationschoreografien einschließlich beider reiner Pans und
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

N05 entfernt außerdem redundante Warteframes nach bereits abgeschlossenem Draw
und misst Alphahüllen mit der nativen Bildoperation statt einer interpretierten
Pixelschleife. Ein einzelner PNG-Schreibthread hält genau ein unveränderliches
CPU-Originalbild bis zum Schreibabschluss. Nur die verlustfreie Kompression
überlappt nachfolgende Frames; Aufnahme, UI und Rendering bleiben im Hauptthread.
Vor dem Ergebnisbericht wird der Writer verbunden und sein Ergebnis geprüft.
Zusätzlich zur laufenden Aufnahme bleibt höchstens eine RGBA-Bildkopie für diesen
Prüfwriter gebunden (14,06 MiB bei 2560×1440); der ausgelieferte Player enthält ihn
nicht. Die nativen Gruppen protokollieren ihre Zeiten im selben 300-s-Prozess.

Die eigene Sichtprüfung vergleicht A als Qualitätsreferenz sowie gebundene N03-
und N04-Originalframes. Je Katalogbild der vier Flächen entstehen sechs
unskalierte Details beider unterer Ecken, des oberen/unteren Falzes und beider Außenränder
mit dokumentiertem Quellrechteck. Vollansichten, Arbeitsränder und Film ergänzen
diese Ausschnitte. Iterationen, Korrekturen und Materialurteil stehen im PR.
Das ersetzt weder das neue B-A-R06 noch die persönliche Kandidatenwahl.

## Ressourcen, Export, CI und Gates

Höchstens drei bewegte Blätter mit je 1105 Vertices/2048 Dreiecken, zwei ruhende
Papierflächen und feste Deckel-/Seitenlagen. Kein Katalogtexturcache. Ein UI-Renderziel
plus RGBA-Snapshot benötigt 7,03/15,82/28,13 MiB bei 720p/1080p/1440p; einschließlich
konservativ vier Depthbytes je Pixel 10,55/23,73/42,19 MiB. Einfrieren benötigt kurz
zusätzlich eine CPU-Bildkopie. Das von der gemeinsamen UI referenzierte A umfasst
weiterhin konservativ 14.745.600 RGBA-Bytes; der Einbandshader sampelt es nicht.
Papier und Leder umfassen jeweils 6.290.064 RGBA-Bytes, mit Mipmaps jeweils
höchstens 8.386.752 Bytes (ca. 8 MiB). `resources.binding` zählt die tatsächlichen
statischen Flächen, Vertices und Dreiecke: N06 benötigt
5 Flächen, 8.448 Vertices, 16.026 Dreiecke; die bisherige Obergrenze bleibt
6/8.511/16.262. Historisch vor Entfernung der Zierbänder: 52/11.869/21.230.
Das Tischbild benötigt 6.291.456 RGBA-Bytes, mit Mipmaps höchstens 8.388.608 Bytes.
Bei 1920×1200 benötigen Renderziel/Snapshot 18.432.000 Bytes, mit konservativer
Depthobergrenze 27.648.000 Bytes. Tatsächliche Import-
und Paketgrößen werden gemessen. Font-/Zellatlanten, SL-Rahmen, Hauptframebuffer
und Treiberoverhead sind separat. Nach Ende/Abbruch sind Übergaberessourcen frei.
Für Informationswege beträgt die neue konservative Farbobergrenze ein Renderziel
plus drei RGBA-Snapshots, also 16 Bytes je Pixel; zuzüglich vier Depthbytes
17,58/39,55/70,31 MiB bei 720p/1080p/1440p. Bei 1920×1200 sind es 43,95 MiB
einschließlich Depth. Eine kurzlebige CPU-Bildkopie bleibt zusätzlich zu beachten.
Es werden weiterhin höchstens ein Capture-Viewport und während Informationswegen
nur ein bewegtes Blatt verwendet.

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

B-A-N06-T01 verlangt aktuelle Technik-, Sicht-, Export- und CI-Nachweise sowie
getrenntes Selbstreview. **B-A-R08 bleibt ein neues separates qualifiziertes technisches
und visuelles Review vor Merge.** Frühere Reviews nehmen N06 nicht ab. **B-A-M01** bleibt
persönliche Kandidatenwahl vor vollständigem B-A-Abschluss und vor B-B; sie darf
nach einem separat freigegebenen isolierten Merge auf main erfolgen. Der aktuelle
Auftrag enthält keine Mergefreigabe und lässt den PR als Draft.

### B-A-N05-F01 / B-A-R06-B01: Windows-Eingabe und Tooltip-Lebensdauer

Nacharbeit gemäß [B-A-V07](https://github.com/venomenon328/picross/pull/495#issuecomment-6557397651).
Am unveränderten Windows-Export von `2cd4fa1c0a602976b996115bff7a4eaa2a7e77f9`
wurden beide Symptome getrennt reproduziert: Access Violation `0xc0000005`
beim wiederholten Überfahren sichtbarer Tooltips und ausbleibende Tooltips nach
echtem Zell-Down/Up. Windows 11, Godot 4.7.2, GL Compatibility, Intel Arc Pro B390;
ursprüngliche Logs und WER-Ereignisse 1000/1001 gehören zum F01-Nachweis.

Die kontrollierte Tooltip-Variante ersetzt synchrones `hide()` am Godot-eigenen
Popup durch `queue_free()`, entsprechend dem verzögerten Abbau der Engine.
Dadurch bleibt die Liste eingebetteter Fenster während der Ereigniszustellung
stabil. Dies gilt auch für die passive `CatalogTip`-Beschriftung. Der getrennte
Commit-Fehler bleibt damit reproduzierbar: Godot bereinigt bei einem in `_input`
verbrauchten Up zwar seine Tastenmaske, behält aber den Board-Mausempfänger.
Das Board wertet seine Loslassposition weiterhin genau einmal aus und lässt
anschließend das Up durch die normale GUI-Zustellung laufen. Diese löst den
ursprünglichen Mausempfänger, einschließlich Hinweisgesten und Gegentastenbarriere;
ein Außen-Up aktiviert keinen anderen Button. Kein erhöhter Delay, globaler
Input-Reset oder Eingriff in Zell-/Saveverträge.

`f01_cases.gd` ergänzt den bestehenden nativen Studienlauf um kleine echte
GUI-Dispatchfälle: Default-BookButton, Popup-Abbau nach Ereignisende, linke/rechte
Zellaktion, Außen-Up, Hinweisroute, Gegentaste, Escape, verlorenes und späteres Up,
Resize, Kreuzlinienrückkehr sowie exaktes Undo/Redo. Zwei Gegenproben stellen
gezielt die alte Release-Verarbeitung und das synchrone Popup-Verstecken wieder
her. Der Ergebnisguard verlangt die Fälle und ihre Originalassertions.
Die Prüfprogramme sind aus beiden Spielerpaketen ausgeschlossen. Das 300-s-Limit bleibt.

Die zusätzliche Windows-Probe verwendet echte Win32-Mausereignisse in der
exportierten EXE/PCK, 32 Hin-/Rückwege mit Idle, Commit, schnellem Wechsel und
sichtbarem Tooltip sowie echte Fokus-/Resize-/Außenloslassfälle. Ein externes,
rein lesendes Beobachterskript wird in einer privaten bytegleichen EXE-/PCK-Kopie
über `override.cfg` als Autoload ergänzt und beobachtet den normalen Einstieg;
es injiziert keine Engine-Ereignisse und verändert keine Spielzustände.
Ein gewöhnlicher Exportstart ohne Beobachter ergänzt diese Instrumentierung.
Head/Basis/Checkout, Werkzeug-/Exporthashes, OS-Ereignisse, begrenzte gespülte
Engine-Spur, Clientbilder und Exitcode bilden B-A-N05-F01-T01. Arbeitsoriginale
liegen vorläufig in `artifacts/book-n05-f01-work/`; der PR bindet das kompakte
Prüfpaket und die tatsächlichen finalen Laufresultate. Keine neue permanente
Bildablage oder erneuter W05-Upload. Die zwei neuen Prüfskripte und der Windows-
Treiber dienen ausschließlich dieser reproduzierbaren Regression.

Die damaligen offenen R06-/R07-Originalprüfungen wurden für PR #495 durch
ausdrückliche Eigentümerentscheidungen erlassen, nicht tatsächlich nachgeholt.
Diese historische Lieferung nimmt weder N06 noch B-A-M01 oder B-B ab.

Start und Reproduktion: [Studienanleitung](../game/study/book/README.md).
