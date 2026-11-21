# Katalogdarstellung · Karten, Filter und Fortsetzen

## Geltung und Zuständigkeit

Dieses Dokument besitzt sichtbare Kataloginhalte, Karten-/Seitenlayout,
Sitzungsfilter, Fortsetzen-Panel und lokale Revealglättung. Die Regeln im
aktuellen Git-Stand sind der Fachvertrag; technische Lieferungen, Review und
persönliche Abnahme werden am jeweiligen Head im Issue/PR nachgewiesen.

| Detail | Maßgebliche Quelle |
| --- | --- |
| Sortierung, Präferenz und Hinzugefügt-Metadaten | [CATALOG_SORTING](CATALOG_SORTING.md) |
| Navigation, Capture und Besuchsrückkehr | [BOOK_INTEGRATION](BOOK_INTEGRATION.md) |
| Schrift, kleine Controls und Piktogrammfamilie | [HAND_DRAWN_UI](HAND_DRAWN_UI.md) |
| Registry und exakte Runtimeversionen | [RI-ONE](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md) |
| Kategorien und Zuordnung | [CATEGORIES](CATEGORIES.md) |
| Schwierigkeit und aktuelle Metadatenquelle | [SD_CATALOG](../difficulty/SD_CATALOG.md), [SD2_INTEGRATION](../difficulty/SD2_INTEGRATION.md) |
| Spielzustand, Abschluss, Reset und Fortsetzen-Merker | [PROTOTYPE_P1](PROTOTYPE_P1.md) |
| Produktionsstil und Alpharegeln | [REVEAL_TRANSPARENCY](../production/REVEAL_TRANSPARENCY.md) und dort zugeordnete Bildquellen |

## NAV-A · Katalogkopf und Blättern (#549)

Position, Reihenfolge, Rückwege und Seitenpfeile sind ausschließlich in
[BOOK_INTEGRATION · NAV-A](BOOK_INTEGRATION.md#nav-a--kopf-und-katalogfuß)
festgelegt. Exakte Symbolhilfen stehen in HZ/NAV-A. Karten-, Filter-, Fehler-
und Fortsetzen-Budgets unten halten diese Navigation kollisionsfrei.

## K-B: zuletzt bearbeitetes Rätsel

[Paketentscheidung #485](https://github.com/venomenon328/picross/issues/485#issuecomment-6705799391).
Die rechte Buchkopfzone oberhalb von Sortierung und Filter enthält ein reduziertes,
als Ganzes anklickbares Panel: links „Zuletzt bearbeitetes Rätsel fortsetzen“ und
neutrale Blattkennung/Dimensionen, rechts eine 56 × UI große eigene Fortschrittsminiatur.
Die Textzeilen sind gemeinsam vertikal zentriert, links um 12 × UI eingerückt.
Der Kasten sitzt mit 8 × UI Abstand unmittelbar über Sortierung/Filter;
Zusammenfassung und der feste scrollbare Meldungsbereich stehen darüber.
Sie ist kleiner als die reguläre Kartenvorschau und verrät weder Lösung noch Motivname.
Ohne gültigen begonnenen, unvollständigen Stand bleibt das Panel verborgen. Abschluss
oder Reset entfernt das Angebot sofort; es gibt keinen Rückfall auf ältere Rätsel.
Die feste Kopfzone hält Zusammenfassung, Panel und scrollbare Fehlermeldungen getrennt;
Kartenmaße, Filter und Sortiercontrols werden durch Fehler nicht verschoben.
Die ID-gebundene Fortsetzungsroute und Rückkehr folgen
[BOOK_INTEGRATION](BOOK_INTEGRATION.md). Merkerformat und zulässige
Schreibanlässe stehen in [P1](PROTOTYPE_P1.md). Ein Merkerfehler hat einen eigenen
nichtmodalen Retry im Meldungsbereich; er sperrt andere Rätsel oder das Beenden nicht.
Der feste Meldungsclip reserviert 48 × UI Höhe für vollständige 44/55-px-Retryziele
einschließlich Kontur. Die zusätzliche Kopfreserve gilt auch ohne Fehlermeldung;
lange Meldungen und beide Retrywege scrollen darin, ohne Panel oder Controls zu versetzen.

**RF-A / #541:** Die eigene Miniatur zeigt den bestätigten Zellstand;
Rückkehr, erneute Anzeige, Zielwechsel und Aktualisierung im offenen Katalog
benötigen keinen Hover. Die synchrone Bindung vor dem Buchcapture folgt BOOK_INTEGRATION. Eine gültige Redo-History ohne Füllungen bleibt als leere
Miniatur sichtbar. X und unbekannt bleiben neutral.
Der Kasten ist genau halb oder ganz so breit wie die tatsächlich nutzbare rechte
Kopfzone nach Papierprojektion und Innenrändern. Die Halbbreite wird nur gewählt,
wenn die mit aktueller Pangolin-Rolle gemessenen, gegebenenfalls umgebrochenen
Texte samt Innenabständen und vollständiger 56×UI-Miniatur in die feste Höhe
passen; sonst unmittelbar volle Breite. Bei 2560×1440/UI100 gilt Halbbreite.
Linker Rand, y-Position und 8×UI-Abstand zu Sortierung/Filter bleiben erhalten.
Resize und UI100→125→100 messen neu.

## K-A · Kombinierbare Sitzungsfilter (#485)

Der Katalog führt einen gemeinsamen
angewendeten Sitzungszustand: Kategorie, Status (Alle/Noch offen/Neu/Begonnen/Gelöst),
Modus (Alle/Monochrom/Farbe), optionale inklusive Schwierigkeit von/bis L1–L5 und
optionale maximale Breite/Höhe von je 1–99 Zellen. Alle Achsen gelten gemeinsam mit UND für den
vollständigen sichtbaren validierten Bestand. Danach folgen das unveränderte
Sortierpaar, 24er-Seiten und die unveränderte 12/12-Zuordnung mit KL-Raster.

Status verwendet dieselbe geprüfte Session und Ableitung wie KE-D04.
Ungültige Saves zählen zu keinem spezifischen Status, auch nicht Noch offen.
Alle erhält ihre Diagnose-/Resetwege bei passenden Metadaten; gültige rekonstruierte
Stände behalten ihren Status und ihre Recoveryaktion. Ein Savefehler bleibt auch
außerhalb der Treffer sichtbar. Modus bezeichnet das Rätsel. Schwierigkeit verwendet
nur vorhandene validierte Werte: ohne Grenzen einschließlich fehlender Stufe,
mit mindestens einer Grenze ausschließlich eingestufte passende Rätsel. Breite und Höhe
werden separat einschließlich ihrer Grenzen geprüft, ohne die Orientierung zu
vertauschen. Leere Felder sind jeweils unbeschränkt; beide Maßgrenzen gelten
bei gemeinsamer Auswahl mit UND.

Der Button **Filter** steht rechts neben Sortierauswahl und Richtungspfeil,
mit 16×UI horizontalem Textinnenraum je Seite auch unter Fokus/Druck. Er
öffnet ein handgezeichnetes Papierpanel mit den zusätzlichen
Achsen. Die Schwierigkeitsfelder **Von/Bis** stehen nebeneinander und zeigen nur
die Bezeichnungen Sehr leicht bis Sehr schwer ohne L-Präfix. Die Dropdowns begrenzen einander auf auswählbare Stufen
mit Minimum ≤ Maximum. Bei Bedarf folgt die Gegengrenze der zuletzt geänderten;
gleiche Stufen und je ein unbeschränktes Ende bleiben möglich. Eine widersprüchliche
Spanne kann nicht ausgewählt werden und erzeugt keine Fehlermeldung.
Die Größenzeile enthält **Breite** und **Höhe** mit schmalen, auf zwei Stellen
begrenzten Eingabefeldern nebeneinander. Labels und Auswahlen sind in gemeinsamen
Spalten ausgerichtet. Jedes Maßfeld schließt rechtsbündig unter seinem
Schwierigkeitsdropdown ab und behält seine schmale Breite. Die Filtergrenze 99 erweitert nicht die Rätselgrenze 50×50.
**Übernehmen** wendet den gesamten gültigen Entwurf an. Andere als leere oder
positive ganzzahlige Breiten/Höhen bis 99 erhalten eine sichtbare Fehlermeldung;
die letzte gültige Auswahl und Trefferliste bleiben bestehen. Schließen verwirft den Entwurf. Bei knapper Höhe
scrollt der Panelinhalt. Die Höhe folgt dem tatsächlichen Inhalt statt einer
festen Leerfläche; nur nötiger Platzbedarf vergrößert sie. Übernehmen /
Zurücksetzen / Schließen bilden eine Zeile mit drei gleich großen Buttons. Kartenminimum,
Bildhöhe, Schriftrollen, Kopf/Fuß und Falzabstände bleiben erhalten.

Echte Filteränderungen setzen Seite und beide Scrollstände auf null; dieselbe
Auswahl ist ein No-op. Rückkehr aus Arbeits-/End-/Informationsansicht erhält den
angewendeten Zustand, Sortierung, Seite, beide Offsets und passende Auswahl-ID.
Abschluss/Reset aktualisieren die Treffer vor Seiten-/Offsetbegrenzung; entfällt
die letzte Seite, beginnt die begrenzte Seite oben. **Zurücksetzen**
neutralisiert Kategorie und alle zusätzlichen Achsen, erhält das Sortierpaar.
Diese Aktion steht ausschließlich im Filterpanel. Katalog-/Speicher- und
Sortierfehlermeldungen stehen im festen freien Kopfbereich der rechten Buchseite
über Sortieren/Filter. Bei Überlänge scrollt nur diese Meldungsfläche; Ein-/Ausblenden
verschiebt weder Kacheln noch Katalogcontrols. Entwurfsfehler stehen oben
im Filterpanel.
Trefferzahl, leerer Trefferbestand, gültiger leerer Katalog und Ladefehler sind
unterscheidbar. Ein neuer Prozess startet ohne Filter, bei Alle/Seite 1/oben.
Es gibt keine Filterpersistenz oder zusätzliche Einstellungsoption.

## KL-D01 · Responsives Katalograster (#523)

Maßgeblich ist die *tatsächlich
nutzbare Breite pro Buchhälfte* nach Papierprojektion, Falz- und sicheren
Innenrändern, vorhandenen Kopf-/Fußaktionen, Scrollbereich und UI-Skalierung;
eine feste 1440p-Auflösungsabfrage ist unzulässig.

Pro physischer Buchseite bleiben **höchstens zwölf Karten**, mit globaler
Filterung/Sortierung vor der unveränderten 24er-Paginierung und Zuordnung
zuerst links, danach rechts. Beide Hälften haben dieselbe aus **gemessenen**
Kartenmindestbreiten und jeweiligen Innenbreiten sicher bestimmte Spaltenzahl:
**höchstens drei**, bei genügend Platz drei, sonst zwei oder im engen Grenzfall
eine. Normalerweise entspricht dies bei drei Spalten **4×3** und bei zwei
Spalten **6×2** Kartenpositionen je Buchhälfte. Diese Reihen sind logisch
angeordnet; die vorhandene unabhängige vertikale Scrollmöglichkeit bleibt bei
geringer sichtbarer Höhe bestehen. Es werden weder Karten hinzugefügt noch
Seitenmitgliedschaften oder IDs durch den Umbruch geändert.

**Jede belegte Zeile wird innerhalb ihrer Buchhälfte eigenständig horizontal
zentriert**, auch eine letzte Zeile mit weniger Karten als Spalten. Ein nur
insgesamt zentriertes Grid mit linksbündiger Teilzeile erfüllt dies nicht;
leere unsichtbare Karten-/Hitbox-Platzhalter sind ebenfalls kein Ersatz.
Gleich große Karten, ruhige symmetrische Abstände und stabile Konturen bleiben.
Vorhandener Freiraum darf durch **behutsame Verringerung des Überschusses**
zwischen Mindestkartenbreite und Wunschkartenbreite sowie maßvolle äußere
Karten-/Zwischenabstände besser genutzt werden; es gibt kein pauschales
Schrumpfen unter die Mindestbreite.

Die vollständigen Inhalts-, Text-, Bild-, Reset- und Fehlerbudgets aus KE-D01
sowie HZ-D02/D03/D07 bleiben erhalten. Ein engerer Umbruch verkleinert keine
Pflichttexte, Trefferflächen oder Vorschauen und ersetzt Volltext nicht durch
Metadatentooltips.

**Angestrebte sichtbare Geometrie:** Im regulären nativen 3D-Buch soll
2560×1440/UI100 mit zwölf Karten **drei Spalten und vier Zeilen** je Hälfte
erreichen. Bei 1920×1080/UI100 sind normalerweise **zwei Spalten/sechs Zeilen**
sinnvoll. UI125, 1920×1200 und enge Größen dürfen entsprechend gemessener
Grenzen zurückfallen. Eine unlesbare Dreispaltenansicht ist kein Erfolg;
1440p/UI125 ist keine pauschale Drei-Spalten-Garantie. 720p ist ein
Fallbackfall. Verifikation muss tatsächliche Buchprojektion, Scroll-/Clip-
und Kartenmaße nachweisen; Setup/Quellinspektion allein genügt nicht.

Bestehende ID-gebundene Öffnung, Reset und Backup-/Recovery, beide
Scrollpositionen, ausgewählte Karte, Filter/Sortierung, Fokus, Scroll-Restore
und Capture/Seitenanimation bleiben beim Umbruch, Resize und UI100→125→100
erhalten. Der Inhalt bleibt spoilerfrei: neue Karten zeigen das Fragezeichen,
begonnene nur eigene Füllungen und abgeschlossene ihr verdientes Reveal.
Weder Rätsel-/Save-/Registry-/Präferenzdaten noch Buchkörper, Falz, Fonts,
Bildassets oder bestehende Animationszeiten werden geändert.
[BOOK_INTEGRATION](BOOK_INTEGRATION.md) bindet die doppelseitige Präsentation;
das konkrete Paket, seine Akzeptanz A01–A07 und die maßvolle Modulprüfung
stehen in [#523](https://github.com/venomenon328/picross/issues/523).
[Zusätzliche Katalogfilter und Wiedereinstieg](https://github.com/venomenon328/picross/issues/485)
bleiben ausdrücklich unabhängig.

**KL-A-Ausführung:** `ui/catalog_grid.gd` ordnet die vorhandenen Kartenwrapper
direkt an; eine Teilzeile reserviert nur ihre tatsächlichen Karten. Beide
Scrollflächen reservieren die jeweilige reale Balkenbreite plus 2×UI, auch bei
verborgenem Balken. Kapazität und gemeinsame Kartenbreite folgen der schmaleren
Fläche; jede Zeile zentriert sich in ihrer eigenen sicheren Kartenfläche.
Die Wunschbreite beträgt gemessenes Minimum plus höchstens 8×UI statt zuvor
16×UI; Innenränder, Schrift, Titel/Reset, Metadaten und Bildhöhe bleiben gleich.

## KE-D01 · Feste Kartenaufteilung

Alle Karten und Grid-Zellen
haben innerhalb derselben Konfiguration identische Maße:

1. Links liegt ein fester proportionaler Bildraum mit 112×UI Höhe und im
   seitlichen Layout 112×UI Breite: Fragezeichen, eigene Füllminiatur,
   verdientes Reveal oder scrollbare Diagnose mit separater Reparaturaktion.
2. Rechts stehen Überschrift, reservierte bis zu zweizeilige Kategorie und
   ausgeschriebener Status mit dem bisherigen Symbol. Neu/Begonnen tragen
   die neutrale Bakso-Überschrift **Blatt NN**; nach gültigem Abschluss steht
   dort der Motivtitel und neben **Gelöst** zusätzlich **· Blatt NN**.
   Titel behalten zwei Zeilen mit der bestehenden Auslassungsregel. Der
   obere rechte Resetplatz bleibt auch bei verborgenem Reset reserviert.
3. Die Kategorie bleibt auch bei Kategorienfilter sichtbar, an einer festen
   oberen Grundlinie innerhalb ihrer zwei reservierten Zeilen.
4. Unten läuft genau ein passiver Papierstreifen über die innere Kartenbreite,
   mit genau einer vollständigen gemeinsamen Metadatenzeile.

Die gemeinsame Spaltenzahl folgt KL-D01. Für die
seitliche Anordnung werden alle Kategorien und neutralen Blattkennungen des
Katalogs mit den aktuellen Fontrollen gemessen, einschließlich Statussymbol,
Titel-/Resetreserve, Innenrändern und Abständen. Reicht die jeweilige Zellenbreite
nicht, wechseln **beide Hälften synchron** zur gestapelten Anordnung: derselbe
Textblock, darunter der vollbreite proportionale Bildraum, zuletzt der Streifen.
Die gemeinsame Breite darf für den gemessenen seitlichen Fit über die bisherige
Wunschbreite Minimum+8×UI hinaus wachsen. Titel, Motivformat, Status, Diagnose
und Reset ändern die gemeinsame Geometrie nicht. Keine Bildschirmauflösung
entscheidet den Wechsel. NAV-A-Kopf, Fortsetzen, Filter/Sortierung und
Blätteraktionen bleiben außerhalb der Karten.

Schriftrollen und Größen, 10×UI Innenrand, 8×UI Inhaltsabstände,
12×UI Zeilen-/Spaltengap und 44/55-px-Trefferrechtecke bleiben erhalten.
Einmalige K2-Messungen zählen vollständig sichtbare Reihen in derselben echten
nativen Buchprojektion bei 1080p/1440p und gleicher UI100/Seite/Scrollposition.
Ziel sind 12 bzw. 24 sichtbare Karten; der tatsächliche Vorher-Fit und
Abweichungen werden mit Karten-/Clipmaßen im Produkt-PR dokumentiert.

| Papierstreifen | Inhalt |
| --- | --- |
| Links | Breite × Höhe, etwa `20 × 15` |
| Mitte | Gefüllter Schwierigkeitskreis und vollständige Bezeichnung |
| Rechts | Gezeichnetes Mono-/Farbpiktogramm |

Die drei Angaben stehen vertikal ausgewogen in derselben Zeile mit klaren
Abständen; keine drei Einzelkästchen und keine zweite Metadatenzeile.
Der Status steht im festen Textblock neben beziehungsweise über dem Bild. Größe und Modus werden nicht
zusätzlich sichtbar an anderer Stelle derselben Karte wiederholt. Das Etikett bleibt
passiv: Klick öffnet dieselbe Karte; Reset und Recoveryaktionen behalten ihre
eigenen vorhandenen Aktionen. Filter und Sortierung stehen in ihren eigenen Verträgen;
sie verändern diese Kartenregel nicht.

Entwurfswerte von 260–280 logischen Pixeln Kartenbreite, 28–32 für Modus-
piktogramme und 12–14 für Schwierigkeitskreise sind keine starren Grenzwerte
oder gemessene Fit-Zusage.
Die gemeinsame Mindestbreite wird aus tatsächlichen Volltextmaßen, Symbolhüllen,
Innenrändern und Abständen bestimmt. „Nicht eingestuft“, „Sehr leicht“ und
„Sehr schwer“ müssen mit Größe und Modus bei UI 100/125 % vollständig und
einzeilig lesbar bleiben. Keine kleinere Metadatenschrift, Abkürzung oder
Auslassung als Ersatz für ausreichende Breite; bei Bedarf sinkt die Spaltenzahl.

Bei gleichem Viewport und UI-Faktor bleiben alle Karten gleich groß, unabhängig
von Text, Modus und Status. Der feste proportionale Bildraum behält ausreichend
Platz; die bisherige Bildhöhe von 112 × UI darf nicht zur Unterbringung der
Metadaten verkleinert werden. Eine gemeinsam angepasste Kartenhöhe ist erlaubt.
Kategorie, mehrzeiliger Titel, Status, Reset und Fehlertexte funktionieren ohne
Überlappung und ohne zustandsabhängige Layoutsprünge. Der bestehende
Titelauslassungsvertrag bleibt von den vollständigen Metadaten getrennt.

Aktive Schriftrollen, optische Grundlinien und stabile ID-gebundene
Kartenkonturen stehen in [HZ-D01–D03/D07](HAND_DRAWN_UI.md). Gemessene
Text- und Konturhüllen einschließlich Antialiasing passen in dieselben sicheren
Karten-/Trefferbudgets; Sortierung oder Neuaufbau ändern bei gleicher ID und
Größe nicht die gezeichnete Grundform.

## KE-D02 · Papieretikett und Moduspiktogramm

Der gemeinsame Streifen wirkt wie ein ruhiges Papieretikett des Rätselbuchs:
warmes Papier, leicht dunkler als die Kartenfläche, dünne subtil unregelmäßige
Kontur, höchstens ein sehr zurückhaltender Schatten. Keine drei gerahmten
Einzelfelder und kein schwerer Schmuckrahmen. Aktive Schriftrollen, gemessene Textmaße und lokale Fallbacks stehen in
[HAND_DRAWN_UI](HAND_DRAWN_UI.md). Charakter entsteht gemeinsam durch Schrift, Kontur, Zeichnungen und Abstände. Streifen,
Kreise und Stifte bleiben statisch.

| Rätselmodus | Zeichnung | Erklärung im gezielten Tooltip |
| --- | --- | --- |
| Monochrom | Ein einzelner dunkler Stift ohne Farbprobe | Monochromes Rätsel |
| Farbe | Drei aufgefächerte Stifte in gedecktem Rot, Blau und Gelb | Farbiges Rätsel |

Die Silhouette beziehungsweise Anzahl der Stifte unterscheidet die Modi auch ohne
Farbwahrnehmung. Alle Farbrätsel verwenden dasselbe Symbol; keine tatsächliche
Palette und keine Motivinformation. Der Modus beschreibt das Rätsel, nicht das
Abschlussbild: Auch ein monochromes Rätsel erhält sein farbiges Reveal.
Der Monostift steht im eigenen Symbolraum zentriert. Beide Modussymbole
werden nach ihren tatsächlichen sichtbaren Hüllen mit der Kartenzeile ausgerichtet;
Entwurfsgrößen stehen in KE-D01.

## KE-D03 · Schwierigkeit ohne neue Bewertung

| Vorhandene Stufe | Sichtbare Bezeichnung | Gefüllter Kreis |
| --- | --- | --- |
| L1 | Sehr leicht | Gedecktes Grün, `#52734e` |
| L2 | Leicht | Oliv, `#74713e` |
| L3 | Mittel | Ocker, `#997337` |
| L4 | Schwer | Rost, `#a36342` |
| L5 | Sehr schwer | Gedecktes Rot, `#9b514b` |
| Keine Einstufung | Nicht eingestuft | Neutralgrau, ohne Stufenzuordnung |

Die Schwierigkeit erscheint als gefüllter Kreis in der bestehenden Stufenfarbe.
Der vollständige Name steht unmittelbar
dahinter in dunkler UI-Schrift gemäß HZ-D01 und trägt die Bedeutung auch ohne
Farbwahrnehmung. Kein sichtbarer Zahlenwert, keine Sterne und keine
Schätzkennzeichnung `≈`. Alle Kreise haben dieselbe Größe; eine dezent gezeichnete
Kontur darf die klar gefüllte Kreisform nicht auflösen. Lesbarkeit und gemeinsame Zeilengeometrie bestimmen das Endmaß;
Entwurfsgrößen stehen in KE-D01.

„Nicht eingestuft“ bleibt neutral, erhält weder Null noch eine der fünf
Stufenfarben und wird nicht als sehr leicht behandelt. Die genaue neutrale
Graunuance folgt dem vorhandenen Papier-/Textkontrast. Redaktionelle und
instrumentierte Werte verwenden dieselbe unveränderte Fünferskala.
Über Kreis und Schwierigkeitstext erscheint kein Tooltip, einschließlich nativer
Ersatztooltips. Die bisherigen Methoden-/Unsicherheitstexte werden dort nicht
mehr angezeigt. Das entfernt nur die Erklärung aus der Katalogoberfläche;
Bewertungsquelle, Metadaten und Aussagegrenzen bleiben unverändert.
Keine neue Solveranalyse, menschliche Kalibrierung oder Ableitung aus Format,
Farbzahl oder Spielstand; fehlende Informationen werden nicht erfunden.

## SD · Aktuelle Quelle der Schwierigkeit

Quelle, Priorität historischer Schätzung und aktueller Rating-Sidecars,
Methodenversionen und Aussagegrenzen stehen in SD_CATALOG und SD2_INTEGRATION;
die exakte Projektion steht in RI-ONE. Fehlende zulässige Werte sind von ungültigen
vorhandenen Metadaten zu unterscheiden. Die Oberfläche liest validierte Stufen;
sie berechnet keine Schwierigkeit aus Größe, Farbe oder Spielstand und startet
keinen Solver. Ein Methodenwechsel oder neues Rätsel bewertet Altwerte nicht
stillschweigend neu. Die Darstellung steht in KE-D03.

## KE-N1 · Lokale Bildglättung

Verdiente Reveals werden in Katalog und Abschluss mit Lanczos auf das tatsächliche
Anzeigemaß verkleinert und dann linear gezeichnet. Dies glättet starke Verkleinerungen auch
gegenüber der bisher schon linearen Abschlussanzeige. Vollständiger Bildausschnitt,
Proportion, Zentrierung und bestehender Bildraum bleiben gleich. Die Anzeige
verändert die PNG-/SVG-Quelldatei nicht; abgeleitete Texturen entstehen erst nach
der Spoilerfreigabe und werden mit dem jeweiligen Reveal freigegeben; je Anzeige bleibt nur die
zuletzt benötigte Zieltextur erhalten. Keine globale Glättung, kein
zusätzlicher persistenter Bildcache; eigene Füllminiaturen bleiben unverändert.

**KAT-2: Ressourcenlebensdauer.** Eine 24er-Katalogseite hält höchstens 24 aktive
Karten und deren Revealreferenzen. Seitenneuaufbau gibt die bisherigen Controls
und Bildreferenzen synchron frei. Beim Öffnen eines Rätsels werden die Reveals
des verborgenen Katalogs freigegeben; die Abschlussansicht gibt ihre eigenen
Referenzen vor der Katalogrückkehr frei. Es gibt keine zweite globale
Auswahlvorschau. Bilder stammen ausschließlich aus dem freigegebenen
`Session.reveal()`-Pfad.

Lokale Polygonkantenglättung gilt auch für Holzspitze, Modusstifte und den
Begonnen-Stift. Sie verändert keine Zell-/Hinweisrenderer oder EA-Zeitfolge.

Beim regulären Blättern wandert der vorbereitete Zielbestand aus dem Capture
direkt in den Katalog. Seite, Filter, Reihenfolge, Kartengeneration und
Geometrie binden die Übernahme. Dadurch behalten höchstens 24 Karten ihre
lokalen Revealreferenzen. Der bestehende Kartenhover wird auch unter einem
ruhenden Zeiger wiederhergestellt.

Die Dimensionsstudie für [#735](https://github.com/venomenon328/picross/issues/735)
ergab seitlich 112 × 112 bzw. 140 × 140 Pixel. Gestapelt begrenzen die
Wunschkartenbreite und beide Innenränder den Bildraum im vermessenen Bestand
auf 264 × 112 bzw. 329 × 140 Pixel (UI100/125). Die Textur passt proportional
in diesen Raum. Die Profile für die Folgeintegration stehen im
[Bildvertrag](../production/REVEAL_TRANSPARENCY.md).

## AT · Transparente verdiente Bilder

Die Katalogkarte verwendet dasselbe freigegebene farbige Reveal wie die
Abschlussansicht. Alphadurchsicht zeigt das bestehende Kartenpapier; kein
zusätzliches weißes Rechteck oder dynamischer Weißfilter. Vollständiger
Ausschnitt, Proportion, Zentrierung und lokale Glättung folgen KE-D01/KE-N1.
Bildproduktion, Alphaqualität und revisionsgebundene Freigabe stehen ausschließlich
in [REVEAL_TRANSPARENCY](../production/REVEAL_TRANSPARENCY.md) und dessen Bildquellen.
Fragezeichen, eigene Füllminiatur, Fehlerdarstellung und Spoilergrenze behalten
KE-D04/D05.

## KE-D04 · Status und Vorschau

| Gültiger Spielzustand | Anzeige | Bildraum |
| --- | --- | --- |
| Neu | Offener Kreis, neutral, „Neu“ | Gemeinsames gezeichnetes Fragezeichen |
| Begonnen | Stift, gedecktes Ocker, „Begonnen“ | Ausschließlich eigene Füllzellen |
| Abgeschlossen | Gezeichneter Haken, gedecktes Grün, „Gelöst“ | Verdientes farbiges Reveal |

Symbol und Text erscheinen gemeinsam linksbündig im festen Textblock neben
beziehungsweise über dem Bild. Bei Gelöst ergänzt „· Blatt NN“ die Motivüberschrift;
sonst führt die neutrale Überschrift die Blattkennung. Farbe allein trägt keine Bedeutung. „Gelöst“ ist Katalog-Anzeigetext; interne Statuswerte bleiben unverändert.
Statusermittlung: gültiger Abschluss
hat Vorrang; vorhandene History einschließlich Redo oder nicht unbekannte
Zellwerte bedeuten Begonnen, sonst Neu.

Das Fragezeichen ist eine eigene Zeichnung in warmem Graphit mit leicht
unregelmäßiger Kontur und dezenter Bleistiftschraffur, kein Zeichen einer normalen
Schrift. Es steht mit großzügigem Freiraum auf warmem Papier und nimmt ungefähr
die halbe Bildhöhe ein. Es bleibt statisch und identisch für alle neuen Rätsel,
ohne Leuchten, Pulsieren, Schattenmotiv oder andere Lösungshinweise.

Begonnene Vorschauen zeigen auch falsche eigene Füllungen unverändert. X und
unbekannte Zellen bleiben neutral. Ein begonnener Stand ohne Füllzellen, etwa nur
X oder nach Undo mit verbleibender History/Redo, zeigt eine leere Füllminiatur
und ausdrücklich kein Fragezeichen. Motivname und Reveal bleiben vor gültigem
Abschluss verborgen; kein vorzeitiges Laden des Reveals für den Platzhalter.

## KE-D05 · Fehler, Bedienung und Tooltips

Ein ungültiger Speicherstand darf nicht als Neu dargestellt werden. Vorhandene
Fehlerkennzeichnung, Diagnose, Backup-/Recoveryaktionen und Reset bleiben
erreichbar; Diagnose/Recovery nutzt weiterhin den festen Bildraum und wird nicht
vom Fragezeichen verdeckt. Die Reparaturbeschriftung darf innerhalb ihres
eigenen nativen Buttons umbrechen; dessen vollständiger 44/55-px-Treffer bleibt
nach innerem Scrollen erreichbar, ohne die Karte zu verbreitern. Kein neuer Statusautomat. Reset bleibt bei gültigem,
fehlerfreiem Neu verborgen und in den bisher vorgesehenen Bearbeitungs-/Fehler-
und Recoveryzuständen verfügbar; vorhandene Bestätigung und Ursprungsbindung bleiben.

**KK: Eingabebesitz der Diagnosefläche.** Innere Diagnoseflächen besitzen
Mausrad, Scrollbar und Textdrag. Diese Aktionen scrollen weder den äußeren
Katalog noch öffnen sie die Karte. Nur ein neutraler Linksklick ohne Zieh- oder
Scrollaktion darf den vorhandenen Registry-ID-Öffnungsweg auslösen; Reparatur
bleibt eine eigene Aktion. Auch Zurückscrollen zur ursprünglichen Position bei
noch gehaltener Linkstaste reaktiviert die verworfene Kartenöffnung nicht.

**B-B: Erfolgreicher Speicher-Retry.** Nach erfolgreichem erneuten Speichern
verschwinden die zugehörige Fehlermeldung in der Zusammenfassung und die
Kartendiagnose sofort, auch wenn das Zielrätsel außerhalb des aktuellen Filters
liegt. Angewendeter Filter, Seite und beide Scrollpositionen bleiben erhalten.
Dies ist vom eigenen Retry für den Fortsetzen-Merker aus K-B getrennt.

Kein Tooltip über der ganzen Karte und kein Tooltip über der Schwierigkeit,
auch nicht als nativer Ersatz für abgeschnittene Metadaten. Der gezielte
Modustooltip und der vorhandene Resettooltip bleiben. Bestehende zugängliche
Beschriftungen führen Größe, Modus, Schwierigkeit und Status spoilerfrei mit. Kein umfangreicher
Accessibility-Umbau, keine Änderung der bestehenden Fokus-/Öffnungsbedienung.

## KE-D06 · Minimaler Metadatenvertrag

Writer, Loader und Validator teilen die exakten Registry-/Runtimeverträge aus
[RI-ONE](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md). Die Runtime
enthält nur die dort zugelassenen typisierten Katalogmetadaten. Produktions-
objekte, Freitexte, Motiverklärungen, Quellen, Proofs oder Pakete gelangen nicht
in den Spieler. Hinzugefügt-Sidecar und Sortierung gehören zu CATALOG_SORTING.

Ältere Runtimeformate behalten ausschließlich die reine
[Spieler-Lesekompatibilität](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md#22-spieler-lesekompatibilität).
Registrierung, Update und Recovery verwenden die aktuelle geschlossene Projektion.
Fehlende zulässige Werte und ungültige vorhandene Metadaten bleiben unterscheidbar;
Darstellungsfolgen stehen in KE-D03. Projektion und kanonische Byteprüfung bleiben
deterministisch. Metadatenpflege erhält die zuständigen Definitions-/Revisions-/Savegrenzen;
sie verlangt keine erneute Produktion oder Wiederherstellung gelöschter Produktionsdaten.

## Prüfzuordnung und Herkunft

Aktuelle risikobasierte Auswahl steht in [CI_C_NATIVE_GROUPS](../ci/CI_C_NATIVE_GROUPS.md)
und dem [Paketvertrag](../ci/CI_WORKFLOW_V2.md). Synthetische Fälle decken im gewählten
Scope Stufen/fehlende Werte, Modi, Status-/Fehlerzustände, vollständige Metadaten,
Filter/Seiten, ID-Bindung, Reset/Recovery und Spoilergrenzen ab. Keine pro realem
Produktionsrätsel wiederholten Replays und keine automatisch wiedereröffnete
historische Darstellungs-Vollmatrix. Native Buchbedienung und persönliche
Sichtabnahme bleiben von Komponentenprüfungen getrennt.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#233](https://github.com/venomenon328/picross/issues/233), [#244](https://github.com/venomenon328/picross/issues/244), [#485](https://github.com/venomenon328/picross/issues/485), [#523](https://github.com/venomenon328/picross/issues/523), [#541](https://github.com/venomenon328/picross/issues/541) und [#547](https://github.com/venomenon328/picross/issues/547).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CATALOG_PRESENTATION.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
