# HZ · Handgezeichnete Bedienoberfläche

## Geltung und Zuständigkeit

Dieser Vertrag besitzt normale UI-Schriftrollen, Zeichenbehandlung, gemessene
Textbudgets, kleine Controls, Dropdowns, Scrollbars und Piktogramme. Die Regeln
im aktuellen Git-Stand sind der Fachvertrag. Paketlieferung, unabhängiges Review
und persönliche Abnahme werden am jeweiligen Head im Issue/PR nachgewiesen.

| Abgrenzung | Maßgebliche Quelle |
| --- | --- |
| Komposition und Navigation | [Buchdarstellung](BOOK_INTEGRATION.md) |
| Drei große gezeichnete Rasterrahmen | [Sidebar](SIDEBAR.md) |
| Katalogkarten und Filter / Sortierung | [Darstellung](CATALOG_PRESENTATION.md), [Sortierung](CATALOG_SORTING.md) |
| Raster, Zellen, Miniatur und Animation | [Zeichensprache](UI_DRAWING_STYLE.md) |
| Hinweisziffern, Slots und Interaktion | [Typografie](CLUE_TYPOGRAPHY.md), [Interaktion](CLUE_INTERACTION.md) |
| Aktive Ressourcen und Export | [Z2](Z2_SELECTION.md) |
| Bildhaupttitel | [VIEW_TITLE_ART](VIEW_TITLE_ART.md) |

## HZ-D01 · Schriftrollen

Die eigene Abschlussrolle in Dancing Script und ihre Layoutregeln sind
freigegebenes Soll aus [VIS-A / #728](https://github.com/venomenon328/picross/issues/728).
Die Abschlussrolle verwendet 50 logische Pixel bei UI100 und Gewicht 600. Die unabhängige Sichtung wird in VIS-A-R01 geführt.

| Rolle | Vertrag |
| --- | --- |
| Normale Spielertexte | Pangolin Regular auf sämtlichen normalen Textpfaden, auch direkter Zeichnung: Hilfe, Legenden, Katalogkategorien/-metadaten, Blatt-/Statuszeilen, Textbuttons, geschlossene/offene Auswahlen, Einstellungen, Dialoginhalt, Tooltips, Warn- und Recoverytexte. Kein Hilfe-only-Font und keine wählbare Schriftoption. |
| Bildhaupttitel | „Rätselkatalog“, „Hilfe“ und „Einstellungen“ verwenden die Bildschriftzüge aus [VIEW_TITLE_ART](VIEW_TITLE_ART.md). Die zugehörigen Fontrollen bleiben Ressourcenfallbacks. |
| Bakso Daging | Arbeits-Blatttitel und Kachelüberschriften (Motivtitel oder neutrale Blattkennung); Einstellungsgruppen „Anzeige“, „Rätselansicht“ und „Spielerkonto“ bei 20 × UI; Hilfe-Abschnitts- und Werkzeugüberschriften gemäß [HIL-TYPO-D01](https://github.com/venomenon328/picross/issues/535). |
| Fraunces 600 | Bestehende übrige Informationsüberschriften sowie „Vollständiger Hinweis“ bei 13 × UI. |
| Motivname im Abschluss | Dancing Script als eigene, sichtbar größere kalligrafische Rolle während der Namenseinblendung und im stabilen Bild-/Rasterabschluss. Arbeits-Blatttitel, Katalogtitel und übrige Rollen bleiben ihren vorhandenen Verträgen zugeordnet. Lokale Originalressource und Lizenz nach [Z2](Z2_SELECTION.md#freigegebene-erweiterung-dancing-script). |
| Hinweisziffern und ausdrücklich daran gebundene Zähler | Delight Coffee und kontrolliert gebündelte Plex-Marker gemäß [CLUE_TYPOGRAPHY](CLUE_TYPOGRAPHY.md). |
| Native Dialogtitel und lokale fehlende Zeichen | Gebündeltes Plex; keine Systemfontsuche und keine zweite allgemeine Textrolle. |

Rollen, Größen, Fallbacks und Originalbytes bleiben über Ansichtswechsel,
Dialogöffnung, Resize und UI100→125→100 konsistent. HZ-D08 bindet das aktive
Pangolin-Original. Historische Tidy-Hand-Auswahl und -Nachweise begründen keine
parallele aktive Standardtextrolle.

Die Abschlussrolle muss bei gleicher UI-Skalierung erkennbar größere sichtbare
Buchstaben als der bisherige Motivname ergeben. Ein größerer nominaler Fontwert
allein genügt wegen abweichender Glyphenproportionen nicht. Reversible Startwerte
und die konkrete Sichtprüfung stehen im Umsetzungspaket.

## HZ-D02 · Zeichenabdeckung und gemessenes Textlayout

Pangolin enthält die geprüften Umlaute, `ß`, `·`, `%`, U+2026 (`…`) sowie
`× „ ‚ – −`. Die geprüften Funktionspfeile `← → ↑ ↓` verwenden den lokalen
Plex-Fallback. Weitere tatsächlich verwendete Zeichen werden gegen die
Originalressourcen geprüft; vorhandene Pangolin-Zeichen bleiben Pangolin.
Fehlglyphen, zufällige Ersatzzeichen und Systemfallback sind ausgeschlossen.
Normale Zeichenketten, automatische Auslassung, Popup und Tooltip stimmen überein.

Bakso-Kacheltitel nutzen gemessene Anzeigezeilen und drei Punkte als
Auslassungszeichen. Bakso zeichnet U+2026 falsch. Andere gekürzte Pangolin-Texte
verwenden die Pangolin-Ellipse. Die Katalogaktionen **Backup übernehmen** und
**Backup erneuern** behalten hingegen die vollständige sichtbare Bezeichnung.
Zeilen und Trefferhöhe werden mit der tatsächlichen kleinen Pangolin-Rolle
an derselben Breite gemessen. Beide Beschriftungen verwenden die belegten
Trennstellen aus der [lokalen Wortliste](CATALOG_HYPHENATION.md).

Die Abschlussrolle wird mit deutschen Umlauten und `ß`, verwendeten lateinischen
Akzenten sowie vietnamesischen Motivnamen geprüft. Vorhandene Zeichen bleiben
in Dancing Script; fehlende tatsächlich benötigte Zeichen verwenden ausschließlich
einen gebündelten kontrollierten Fallback. Originalglyphen, kombinierende Zeichen
und Akzenthüllen dürfen beim Umbruch oder Clipping nicht abgeschnitten werden.
Dies ist keine Zusage einer vollständigen Abdeckung sämtlicher Schriftsysteme.

Das Abschlusslayout misst die tatsächliche Dancing-Script-Glyphenhülle samt
Ober-/Unterlängen und Akzenten. Name, Bild-/Rasterumschalter und Reset bleiben
kollisionsfrei und vollständig bedienbar. Der Bild-/Rasterbereich berücksichtigt
den realen Titelbedarf; keine pauschale Fontverkleinerung ersetzt passende Budgets.

Textbreite, sichtbare Glyphenhülle samt Fallback, Kerning, Zeilenhöhe, Umbruch,
Auslassung, Innenabstände und Scrollenden werden mit der tatsächlich verwendeten
Schrift gemessen. Pflichtmetadaten bleiben vollständig; keine Kürzung oder
Schriftverkleinerung ersetzt passende Layoutbudgets. Motivtitel dürfen nach dem
[Kartenvertrag](CATALOG_PRESENTATION.md) begrenzt werden. Lange gültige Kategorien
bleiben über vorhandene Wege lesbar und auswählbar; die 128-Zeichen-Namensgrenze
und 256-Kategorien-Grenze aus [CATEGORIES](CATEGORIES.md) werden nicht verschärft.

Kopfaktionen, Dialoge, Hilfe und randnahe Tooltips passen in die unterstützten
Fenster. Das Vollhinweis-Overlay misst Fraunces-Überschrift und Delight-Token
getrennt. Text-/Rahmen-/Trefferhüllen dürfen sich nicht überdecken. Diese Regeln
ändern keine Hinweis-/Rasterfitformel.

## HZ-D03 · Konturen, Zustände und Trefferflächen

Katalogkarten, kleine Papierbuttons und geschlossene Dropdowns erhalten leicht
gebogene, ungleichmäßige Kanten mit kleinen Eckversätzen, kurzen Überständen und
sparsamen zweiten Strichen. Wenige bewusst variierte Züge ergeben die Handschrift;
ein nahezu gerades Rechteck mit nur anderer Farbe erfüllt den Auftrag nicht.
Stärke und Abweichung passen zur Elementgröße und UI-Skalierung. Die vorhandenen
gezeichneten Papierstreifen, Stifte und großen Gruppenrahmen dienen als Stilbezug.

Die Variation ist an stabile Elementidentitäten gebunden. Dieselbe Karte wird
anhand ihrer Registry-ID wiedererkannt, nicht anhand ihrer aktuellen Listenposition.
Bei identischen Maßen bleibt die Form über Redraw, Hover, Zustandswechsel,
Sortierung, Seitenwechsel, Neuaufbau und Neustart identisch. Größenwechsel
skalieren oder vermessen dieselbe Form deterministisch; die Rückkehr zu denselben
Maßen liefert dieselbe Kontur. Zeit- oder Redraw-Zufallswerte sind ausgeschlossen.
Die stärkere Kontur erhält keine eigene Wackel- oder Zeichenanimation.

Die jeweils unterstützten Zustände Normal, Hover, gedrückt, ausgewählt,
deaktiviert und Fokus bleiben klar erkennbar. Eine Auswahl besitzt auch eine
Form-/Markierungsunterscheidung. Die dekorative Grundform bleibt beim Zustandswechsel
stabil; vorhandene Zustandsflächen und zusätzliche Markierungen dürfen wechseln.
Gezeichnete Fokus- und Auswahlmarkierungen gehören zur gemeinsamen Stilfamilie.
Für Katalogkarten gilt die Ausnahme aus KAT-HOVER-C: Auswahl und nativer
Fokus bleiben funktional, während die Karte ausschließlich ihre Normal-,
Hover-, Druck- oder deaktivierte Kontur zeigt. Auswahlunterstrich,
Auswahlfarbe und Fokusinnenkontur entfallen für die Karte.

Layout, Zentrierung und Trefferflächen bleiben regelmäßig. Vorhandene Buttons
und Kartenaktionen behalten ihre rechteckigen Mindesttrefferflächen von
44×44 bei UI100 und 55×55 bei UI125. Strichüberstände, Kantenglättung und
transparente Ressourcenpolster werden bei sichtbaren Hüllen, Innenrändern und
Clipping berücksichtigt; sie dürfen weder abgeschnitten werden noch Texte,
Nachbarn oder eigene getrennte Aktionen überdecken. Keine durch Wackelkonturen
verkleinerten oder verschobenen Hitboxen.

Die gebundene HZ-B-Ausarbeitung begrenzt die Biegung großer Grundkonturen auf
5×UI bei 7×UI Innenabstand. `book_style.gd` behandelt ein Control als groß,
wenn seine längste Seite mehr als 200×UI misst. Diese konkreten Werte dokumentieren
den aktuellen Zeichenpfad; die getrennte Fokusinnenkontur bleibt weiter innen.

Die gemeinsame Buttonfamilie verwendet im regulären Buch transparente Füllung.
Hover und Druck verstärken die vorhandene vollständige Kontur in zwei Stärken;
kein isolierter oberer Hoverstrich. In der äußeren oberen Buchnavigation
verstärkt auch nativer Fokus die Außenkontur. Druck hat Vorrang. Die stabile
Innenkontur markiert dort die offene Informationsansicht in allen Zeiger- und
Fokuszuständen. Für die Kopfgruppe entfallen die Auswahlunterstriche. Andere
Buttonrollen behalten ihre bisherigen Auswahl-, Fokus- und Deaktiviertzeichen.
Eigener Text wird genau einmal gezeichnet;
Farbproben behalten ihre Originalpixel. Popup-, Dialog- und Fehlerflächen bleiben
opak. Die gemeinsame vorhandene Buttonfamilie wird fortgeführt. Katalogkarten nutzen
einen eigenen `content_surface`-/StyleBox-Pfad und überspringen
die `BookButton`-Zeichnung. Eine Änderung allein in `BookButton` oder eine globale
Scribble-Verstärkung beweist daher keine vollständige Kartenumsetzung. HZ verlangt
das sichtbare Gesamtergebnis, keine neue konkurrierende Controlarchitektur.
Die Rasterassetpflicht aus SL gilt gezielt für die drei großen Gruppenrahmen;
sie erzwingt kein neues Bitmap für jeden kleinen Rahmen.

## HZ-D04 · Vollständige Dropdowngestaltung

Der Scope umfasst die vorhandene Kategorienauswahl, „Sortieren nach“ und die
Rätselansicht in Einstellungen. Kontoeingaben und Codefeld haben gezeichnete
Umrisse auf dem sichtbaren Papier; Checkboxzeilen der Rätselansicht zeigen
Symbol, Text und Fokusrahmen auf demselben Papier. Geschlossenes Auswahlfeld
und ausgeklappte Liste bilden
eine zusammengehörige Darstellung:

| Bestandteil | Gestaltung und Verhalten |
| --- | --- |
| Geschlossenes Feld | Unregelmäßige Kontur; im regulären Buch transparente Füllung gemäß gemeinsamer Controldarstellung. |
| Popup-Außenrahmen | Warmes opakes Papier und unregelmäßige Kontur; darunterliegende Karten stören die Lesbarkeit des geöffneten Menüs nicht. |
| Menüzeilen | Standardtext gemäß HZ-D01, lesbare Abstände und sichere Text-/Markierungsbudgets auch für lange Werte. |
| Aktuelle Auswahl | Gezeichneter Haken, sichtbar von der gerade angefahrenen Zeile unterschieden. |
| Hover beziehungsweise vorhandener Fokus | Zurückhaltende unregelmäßige Hervorhebungsfläche, ohne Text oder Auswahlhaken zu verschlucken. |
| Chevron, Markierungen und lange Listen | Zur Piktogrammfamilie passende Zeichen und benötigte Scrollbestandteile; vorhandene Auswahl- und Scrollwege bleiben vollständig nutzbar. |

„Native Controls“ meint die vorhandenen Godot-Controls mit ihren Signalen und
Eingabe-/Fokusmechanismen, keine Pflicht zur Standardoptik oder zu einem
betriebssystemeigenen Menü. Auswahl, vorhandene Tastatur-/Fokusbedienung,
Abbruch, Außenklick und Mausrad bleiben erhalten. Die Darstellung berücksichtigt
auch programmatische Auswahländerungen.

Popupereignisse dürfen keine darunterliegende Karte oder Rasteraktion auslösen.
Schließen, Resize, UI-/Ansichtswechsel und Neuaufbau hinterlassen keine veralteten
Popups, Tooltips oder unsichtbaren Trefferbereiche. Es entstehen keine neuen
Optionen, Einstellungen, Sortierregeln oder Speicherpflichten.

## HZ-D05 · Vollständige Piktogrammfamilie

Alle auf Buttons verwendeten Piktogramme wirken erkennbar handgezeichnet: leicht asymmetrische
Kurven, variierende Strichwirkung und Enden, kontrollierte kleine Versätze und
zurückhaltendes Nachziehen. Plus/Minus bleiben einfache verständliche Striche;
Buch, Stift, Radierer und übrige Bildzeichen dürfen mehr Eigenart zeigen.
Optische Größe und Gewicht passen im tatsächlichen Button zusammen; die
Ausgangsgröße von etwa 26 logischen Pixeln ist kein ungeprüftes Endmaß.

Das vollständige aktive Ressourceninventar und seine reproduzierbare
Provisionierung stehen in [Z2](Z2_SELECTION.md). Verwendungen umfassen Buttons,
Sortier-/Seitenpfeile, Dropdown-Chevrons/-Haken, Einstellungscheckboxen,
Scrollpfeile und das Beenden-X. Ein Ressourceninventar nimmt keine entfernte
Playaktion wieder in die Oberfläche auf.

Vorhandene Bedeutung, zugängliche Beschriftung, Tooltips und Aktivierbarkeit
bleiben. Undo als einzelne Rücknahme und Reset als bestätigtes Zurücksetzen des
ganzen Blatts müssen eindeutig unterscheidbar bleiben. Keine Emoji-, Systemfont-
oder nur umgefärbte geometrische Standardfamilie.

Eigene konsistente lokale SVG-/Zeichnungsressourcen sind zulässig. Quelle,
Generator, Inventar, SVGs, Herkunft und Exportbindung werden nach dem
[Z2-Ressourcenvertrag](Z2_SELECTION.md) gemeinsam fortgeschrieben.

## HZ-D06 · Fachliche Grenzen

HZ besitzt Darstellung und die dafür erforderlichen Text-/Konturbudgets.
Spielzustand, atomare Eingabe, Save-/Recoverygrenzen und Spoilerfreigabe folgen
[P1](PROTOTYPE_P1.md); Registry, Runtime und Kategorien folgen
[CATEGORIES](CATEGORIES.md). Katalogidentitäten, Dialogzielbindung,
Ressourcenlebenszyklus und Kartengrenzen folgen dem
[Kartenvertrag](CATALOG_PRESENTATION.md), Sortierpräferenzen dem
[Sortiervertrag](CATALOG_SORTING.md). Raster, Zellen, Hinweise und große
Sidebarrahmen werden nicht durch die Regeln für kleine Controls ersetzt.

## HZ-D07 · Optische Textausrichtung und kleine Schriftgröße

Sichtbare Buchstaben, Symbole und umgebende Zeile bzw. Controlfläche stehen
optisch ausgewogen zusammen. Eine zentrierte Controlbox allein genügt nicht.
Es gelten stabile Grundlinien pro Rolle, Größenstufe und Control. „Neu“,
„Begonnen“, „Gelöst“ und wechselnde Dropdownwerte dürfen nicht wortabhängig
in der Höhe springen. Gemessene Glyphenhüllen einschließlich lokaler Fallbacks
bestimmen sichere Budgets und Clipping. Ein rollenbezogener optischer Ausgleich
ist zulässig; Originalfontbytes bleiben unverändert.

Die kleine Rolle verwendet 15 bei UI100 und 19 bei UI125. Dazu gehören
Katalogkategorie, Größe, Schwierigkeitsname, Status, Blattkennung, die drei
Dropdownarten einschließlich offener Zeilen und die zugehörigen kleinen
Textbuttons. Diese Rolle vergrößert nicht pauschal Hilfe, Dialoge, Tooltips
oder Überschriften. Die spezifische Hilfetypografie steht im
[Buchvertrag](BOOK_INTEGRATION.md).

Blattkennung, Statuswort und Statussymbol werden gemeinsam ausgerichtet.
Kategorien behalten ihre feste Position im reservierten bis zu zweizeiligen
Bereich; ein- und zweizeilige Namen werden dort nicht jeweils neu zentriert.
Text-/Symbolmaße, Zeilenhöhen, Innenränder und Karten-/Popupbudgets werden mit
der aktiven Schrift gemeinsam gemessen. Pflichttexte, lange Kategorien,
Fallbackzeichen, Umlaute und Unterlängen müssen vollständig passen. Bildraum,
Titel-/Resetreserve und Mindesttrefferflächen bleiben gemäß ihren Fachverträgen.

## HZ-D08 · Pangolin-Original · PANG-A / #531

Die [Eigentümerentscheidung #531](https://github.com/venomenon328/picross/issues/531)
bindet Pangolin Regular für die normale Rolle aus HZ-D01. Zeichen-/Layoutregeln
stehen in HZ-D02/D07; sie werden hier nicht nochmals abgeschrieben.

Ausgewählte Quelle ist der **Eigentümeranhang** `font_candidates.zip`,
`Pangolin/Pangolin-Regular.ttf`: **589884 Byte**, SHA-256
`a48db64eadc589c2e9f14a4ba79eed82a438c7f620f929dd19e352c20b2a922e`.
Mitgegeben: `Pangolin/OFL.txt`, **SIL Open Font License 1.1**, SHA-256
`414e35e9875605ea0dfe549a6bdad6d1f1f3d5427c97af2060213adb6709484c`;
Copyright 2016 The Pangolin Project Authors. Die Originale liegen unter
`game/art/drawing/Pangolin-Regular.ttf` und `game/art/drawing/pangolin/OFL.txt`
bytegleich gespeichert; [Herkunft](../../game/art/drawing/pangolin/NOTICE.txt).
Die konkreten Bytes sind vor ihrer Einbindung zu verifizieren;
die öffentlich verfügbare namensgleiche TTF darf nicht ohne Hashprüfung
als byteidentische Alternative gelten. Aktive Offline-Schrift und korrekte
Copyright-/OFL-Hinweise gehören in Windows- und Webexport; bisherige Tidy-Hand-Datei, NOTICE, HZ-Nachweise und Hashbindungen
bleiben historisch intakt, ohne einen unbenutzten zweiten Standardfont zu
aktivieren.


## NAV-A · Navigation und Symbolhilfen (#549)

Das Zahnrad mit offener Mitte und acht erkennbaren Zähnen ersetzt das Menüzeichen.
Es verwendet dieselbe stabile Strichfamilie, optische Größe und quadratische
44/55-px-Fassung wie Rückpfeil und Hilfe. Der interne Ressourcenname `menu`
bleibt erhalten; seine aktive Quelle `tools/book_icons_hz.json`, der Generator
`tools/z2_resources.py`, SVG, Inventar, Herkunft und Manifest sind gemeinsam
gebunden. Historische BP-/KB-Symbolquellen bleiben unverändert.
Gemäß Eigentümerpräzisierung in #549 ersetzt ein handgezeichnetes X den
Beenden-Textbutton im Katalog. Das neue `quit`-SVG verwendet zwei leicht gebogene,
sparsam nachgezogene Stiftzüge derselben Familie und dieselbe quadratische
44/55-px-Fassung. Aktive Quelle, Generatorinventar, SVG und Manifest umfassen es.
Im Katalog stehen Zahnrad, Hilfe und Beenden-X von links nach rechts.
In Hilfe und Einstellungen kennzeichnet die Innenkontur die offene Ansicht.
Außenkontur und Innenkontur folgen HZ-D03. Positionen und Rückwege stehen im
[Buchvertrag](BOOK_INTEGRATION.md), Titelvorrang in [BTI-D04](VIEW_TITLE_ART.md).

Der folgende Vertrag umfasst die reinen Symbolbuttons des regulären Spiels. Jeder besitzt auch im deaktivierten Zustand
einen nichtleeren deutschen Tooltip und einen passenden zugänglichen Namen:

| Verwendung | Tooltip / zugänglicher Funktionsname |
| --- | --- |
| Katalogpfeile | Exakt „Vorherige Seite“ / „Nächste Seite“ |
| Sortierrichtung | Aktuelle Kategorienfolge/umgekehrte Folge, Kleinste/Größte, Sehr leichte/Sehr schwere oder Älteste/Neueste zuerst; Name ergänzt Kriterium |
| Katalog-/Rätselkopf | „Einstellungen öffnen“, „Hilfe öffnen“, Rückpfeil „Zurück zum Katalog“ |
| Katalog-Beenden-X | Exakt „Beenden“ als Tooltip und zugänglicher Name |
| Informationskopf | „Zurück zum Katalog“ bzw. „Zurück zum Rätsel“; Gegenansicht öffnen oder „Einstellungen (aktuelle Ansicht)“ / „Hilfe (aktuelle Ansicht)“ |
| Füllen / Radieren | „Füllen · links Farbe setzen, rechts leer markieren“ / „Radierer · Markierungen entfernen“ |
| Undo / Redo | „Letzten Strich rückgängig machen“ / „Zurückgenommenen Strich wiederholen“ |
| Minus / Plus | „Raster verkleinern“ / „Raster vergrößern“ |
| Dynamische Farbfelder | „Farbe n wählen · aktiviert Füllen“ |
| Katalog-/Abschlussreset | „Rätsel zurücksetzen“; Katalogname ergänzt gebundenes Blatt und Status |
| Lokale Fragezeichen in Einstellungen | Vorhandene konkrete Erklärung für Fenstergröße bzw. Rätselansicht; Name nennt das erklärte Feld |

Textbuttons, Checkboxen mit Text, Dropdowndekoration, passive Status-/Moduszeichen
und Lehrsymbole werden dadurch nicht pauschal umgebaut. Keine Ganzkarten- oder
Schwierigkeitstooltips; KE-D05 und bestehende gezielte Modushilfen bleiben.
Native Scrollbarteile sind keine eigenen Button-Controls. Positionen und
Rückwege stehen im [Buchvertrag](BOOK_INTEGRATION.md); der Titelvorrang steht
in [BTI-D04](VIEW_TITLE_ART.md).

## SBR-A · gemeinsame Scrollbars (#539)

[SBR-D01–D06 / Paket SBR-A](https://github.com/venomenon328/picross/issues/539)
ergänzt die bestehende Controlfamilie: graphitgrauer Track mit offener,
deterministisch variierter diagonaler Handschraffur, heller Thumb mit ruhender
gezeichneter Kante und Griffstrich, helle geschlossene Dreieckspfeile.
`book_controls.gd::scrollbars()` liefert denselben Themeweg an den gemeinsamen
Spielroot und die expliziten Popup-Themes, einschließlich dynamischer Filter-,
Meldungs-, Recovery- und Werkzeugscrollflächen. HScrollBar erhält die gedrehte
Familie, ohne einen horizontalen Scrollweg hinzuzufügen.

Die native Breite/Pfeilhöhe beträgt 22/28 px bei UI100/125, die minimale
Thumblänge 28/35 px. Alle Zustände teilen dieselben Maße und Konturen; Hover
hellt auf, Druck ergänzt einen zweiten Griffstrich, Fokus einen hellen Randzug.
Godot bietet für ScrollBar keine eigenen Disabled-Theme-Slots: unveränderte
native Bereichsgrenzen und bedarfsabhängige Sichtbarkeit gelten weiter.
Für die nun sichtbaren nativen Pfeile wird `custom_step` auf 32×UI gesetzt;
der interne Godot-Default `step=0` würde Pfeilklicks wirkungslos lassen.
Drag-/Radwerte werden dadurch nicht quantisiert. Keine eigene Input-/Scrollsteuerung.
Die tatsächliche Balkenbreite bleibt
die Grundlage der Katalogreserve, auch bei verborgenem Balken.

Die vier lokalen SVG-Dreiecke stehen in `tools/book_icons_hz.json`; Generator,
Inventar, Herkunft und Manifest sind gemeinsam fortgeschrieben. Der schmale
StyleBox-Pfad verwendet nur die stabile Identitätsfunktion aus `scribble.gd`,
keine für große Papierflächen ausgelegten Kantenbögen. Buchmaterialien, Schriftrollen und übrige Icons behalten ihre jeweils
zuständigen Fachverträge. Herkunft und Exportbindung folgen [Z2](Z2_SELECTION.md).

## Katalogkarten · KAT-HOVER-C / #735

Die isolierte native Studie verglich die Verstärkung der vollständigen Buchkontur
(A) mit inneren Graphit-Eckklammern (B). Für das Spiel wurde
[Variante A gewählt](https://github.com/venomenon328/picross/issues/735#issuecomment-7061354953).
Hover und Druck verstärken dieselben vier Konturseiten samt Ecken bei stabiler
ID-Geometrie. Die Kartenfläche behält in jedem Zustand warmes Papier
(#fff8e8). Für deaktivierte Karten bleibt die Kontur gedämpft. Das gezeichnete
Fragezeichen liegt direkt auf dem Kartenpapier.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#284](https://github.com/venomenon328/picross/issues/284), [#294](https://github.com/venomenon328/picross/issues/294), [#531 / PR #532](https://github.com/venomenon328/picross/pull/532), [#539](https://github.com/venomenon328/picross/issues/539) und [#549](https://github.com/venomenon328/picross/issues/549).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/HAND_DRAWN_UI.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
