# HZ · Handgezeichnete Bedienoberfläche

**HZ-C-Implementierungsstand · 21.10.2026:** [Lieferung und Prüfzuordnung](HZ_C_VERIFICATION.md)
setzt HZ-D07 auf `fix/294-tidy-typografie` um. Gemeinsame kleine Größe ist 15
bei UI100 und 19 bei UI125; Blattkennungen bleiben 15/19. Private gemessene
Zeilenmetriken und stabile Grundlinien erhalten Originalfontbytes und übrige
Textrollen. Die folgenden früheren Angaben „noch nicht implementiert“ und
„separater Implementierungsauftrag erforderlich“ sind durch den ausdrücklichen
HZ-C-Auftrag und diese Lieferung fortgeschrieben. Technischer Abschluss und
Originalbelege stehen im Paket-PR; R01/M01 bleiben getrennt vor Merge offen.

Stand: 21.10.2026 · Spezifikation 1.2 · **HZ-A/B integriert und abgenommen; HZ-C implementiert, Abnahmen offen**

[Issue #284](https://github.com/venomenon328/picross/issues/284) dokumentiert den
Abschluss von HZ-A und HZ-B einschließlich ihrer erfüllten T01/R01/M01-Gates.
Die [HZ-A-Lieferung](HZ_A_VERIFICATION.md) ist über PR #288, die
[HZ-B-Lieferung](HZ_B_VERIFICATION.md) über PR #289 integriert. Ihre historischen
Nachweise bleiben an die damaligen Heads gebunden.

Der Eigentümer hat am 21.10.2026 die besprochene Typografie-Nachbesserung und ihre
Übernahme in Issues und Repository-Dokumente freigegeben.
[Folgeissue #294](https://github.com/venomenon328/picross/issues/294) führt dafür
das zusammenhängende Paket HZ-C gemäß HZ-D07. Der aktuelle Auftrag liefert die
Spezifikation, keine Produktimplementierung oder Mergefreigabe.

## 1. Ziel, Ausgangsstand und gezielte Ablösung

Die normale Spieleroberfläche trägt die Handschrift des vorhandenen Rätselbuchs
durchgängig: Tidy Hand für Standardtext, erhaltene Überschriften, organischere kleine Rahmen,
vollständig gezeichnete Dropdowns und eine gemeinsame Piktogrammfamilie.
Lesbarkeit, ruhige Anordnung und präzise Bedienung gehören zum Gestaltungsergebnis.
Die Unregelmäßigkeit muss schon in tatsächlicher Einsatzgröße erkennbar sein.

Historische Ausgangsbasis der HZ-A/B-Spezifikation ist
`main@fee90adf71c7c3f82e01aa6425c6ec8799424773`. Dort sind KB/KK sowie KU-A
(PR #254) und KU-B (PR #255) integriert. Die Eigentümerscreenshots vom
20.10.2026 und die Komponentenskizze im Chat erläutern den Gestaltungswunsch;
sie sind keine gebundenen nativen Build-, DPI-, Eingabe- oder Abnahmenachweise.

| Bestehender Vertrag | Gezielte HZ-Fortschreibung |
| --- | --- |
| [KB #168](https://github.com/venomenon328/picross/issues/168), KK und bisherige GD-/VS2-Schriftrollen | Tidy Hand ersetzt Plex für normalen Standardtext. Bestehende Überschriften in Bakso/Fraunces und native Dialogtitel behalten ihre bisherigen Ressourcen. Originalfontbytes und historische Lieferbelege bleiben erhalten. |
| [Katalogdarstellung](CATALOG_PRESENTATION.md) | Metadaten, Kategorie und Status erhalten Tidy Hand; die äußere Kartenkontur wird organischer. Gemeinsamer Papierstreifen, vollständige Angaben, Kartenbereiche und Spoiler-/Reset-/Recoverygrenzen bleiben. |
| [Katalogsortierung](CATALOG_SORTING.md) | Gezeichnete geschlossene und offene Auswahlen samt Richtungs-/Seitenpfeilen; sämtliche Sortierwerte, acht Kriterium-/Richtungspaare und Präferenzen behalten ihre Bedeutung. |
| [Zeichensprache](UI_DRAWING_STYLE.md) | Stabile handgezeichnete Konturen werden gezielt für kleine Bedienelemente verstärkt. Daraus folgt keine globale Verstärkung von Raster-, Hinweis-, Zell- oder Miniaturstrichen. |
| [HC/HF](CLUE_TYPOGRAPHY.md), [HN](CLUE_INTERACTION.md) | Hinweisziffern, ihre Marker und gebundene Zähler behalten ihre Spezialrolle. Auch die bestehende Fraunces-Überschrift des Vollhinweis-Overlays bleibt unverändert. |
| [SL #65](https://github.com/venomenon328/picross/issues/65) / [SL-Lieferung](SL65_IMPLEMENTATION.md) | Die drei großen Sidebarrahmen bleiben vorhandene echte gezeichnete Rasterassets einschließlich ihrer sicheren Innenflächen. Die Freigabe ersetzt sie weder durch Laufzeitgeometrie noch beauftragt sie neue Gruppenrahmen. |
| [Z2-Ressourcenweg](Z2_SELECTION.md) | HZ-B darf die aktive Iconfamilie mit konsistent fortgeschriebenen Quellen, Provisionierung, Inventar und Export ändern. Historische BP-/SL-/KB-Belege werden nicht rückwirkend verändert. |

Frühere Mergeausnahmen oder auf `main` verlegte persönliche KU-Abnahmen aus
[#244](https://github.com/venomenon328/picross/issues/244) gelten nur für ihre
damaligen Pakete. HZ übernimmt oder erledigt diese offenen Abnahmen nicht.
Produktgrenzen stehen in [Produktdefinition](PRODUCT_DEFINITION.md),
Komposition in [Gestaltungskonzept](DESIGN_CONCEPT.md), Prüfwege und Befugnisse
in [Projektprofil](PROJECT_PROFILE.md) und [CI-Policy](CI_POLICY.md).

## HZ-D01 · Schriftrollen

**Eigentümerentscheidung HZ-A-FONT02 · 20.10.2026:** Nach dem begonnenen
Bakso-Versuch wurde die Arbeit angehalten und Tidy Hand als Standardtext
bereitgestellt. Überschriften und Hinweiszahlen sollen ausdrücklich unverändert
bleiben. Diese Entscheidung ersetzt die Schriftwahl aus Version 1.0 und HZ-A-P01;
HZ-B, Produktgrenzen und die getrennten Gates bleiben erhalten.

| Rolle | Freigegebener Sollstand |
| --- | --- |
| Normale Spielertexte | Unverändertes `game/art/drawing/TidyHand.ttf` von Sean Johnson. Kategorien, Größe, Schwierigkeit, Blatt-/Statuszeilen, Textbuttons, Auswahlen, offene Menüzeilen, Einstellungen-/Infotexte, Dialoginhalt, Bedienhilfe, Tooltips und normale Warn-/Recoverytexte; auch direkte Textzeichnung. |
| Bestehende Überschriften | Bakso für Katalog-/Arbeitsblatttitel und Kachel-Motivtitel/`???`; Fraunces 600 für bisherige übrige Überschriften einschließlich Abschlussbeschriftung und Information. Native Dialogtitel behalten ihren bisherigen Plex-Font. Die ursprünglichen Rollen, Größen und Fontbytes bleiben. |
| Hierarchie und längere Texte | Rollenbezogene Größen, Abstände und Zeilenhöhe; Absätze bleiben ruhig lesbar. Tidy Hand ist keine Vereinheitlichung sämtlicher Überschriften. |
| Vollhinweis-Überschrift | „Vollständiger Hinweis“ bleibt Fraunces 600 bei 13 × UI einschließlich bestehender Messung und sicherer Box. |
| Hinweisziffern, ihre Marker und ausdrücklich an HC gebundene Zähler | Delight Coffee und die kontrolliert gebündelten Plex-Marker gemäß [HC](CLUE_TYPOGRAPHY.md). Schrift-/Slot-/Fitgeometrie, Status, Zahlfarben und C1-Kontur bleiben unverändert. |
| Fehlende UI-Zeichen | Ausschließlich gebündeltes Plex als lokaler Fallback; keine Systemfontsuche und keine weitere allgemeine Textrolle. |

Die Fontauswahl ist abgeschlossen. Die bereitgestellte TTF bleibt byteidentisch;
[Herkunft und Nutzungshinweis](../game/art/drawing/tidy-hand/NOTICE.txt) dokumentieren
die Autorenaussage „This font is free for all use.“ auf der
[Quellseite](https://www.dafont.com/de/tidy-hand.font). ZIP und TTF sind per SHA-256
gebunden. Vorhandene Fontquellen/Nutzungshinweise bleiben erhalten und werden
weiter mitgeliefert. Die Rollen bleiben nach Ansichtswechsel, Dialogöffnung,
Resize und UI100→125→100 erhalten.

## HZ-D02 · Zeichenabdeckung und gemessenes Textlayout

Tidy Hand enthält `äöüÄÖÜß`, `·`, `%` und eine korrekte U+2026-Ellipse.
Unter anderem `×`, `„`, `‚`, `–`, `−` und Funktionspfeile kommen aus dem
kontrolliert gebündelten Plex. Die tatsächlichen Spielertexte werden inventarisiert;
native Sichtung ergänzt die Zeichentabellenprüfung. Normale Zeichenketten,
automatische Auslassung und Popup-/Tooltipdarstellung müssen übereinstimmen.
Korrekte Bedeutung und Originalfontbytes bleiben erhalten; keine Kästchen oder
Buchstaben anstelle von Auslassungspunkten.

Die unveränderten Bakso-Kacheltitel behalten ihre bisherige besondere native
Dreipunkt-Auslassung, weil Bakso U+2026 falsch zeichnet. Diese Ausnahme wird nicht
auf den neuen Standardtext übertragen; dessen echte Tidy-Hand-Ellipse genügt.

Textbreite, sichtbare Glyphenhülle einschließlich Fallback, Zeilenhöhe, Umbruch,
Auslassung und Innenabstände werden mit den tatsächlich verwendeten Ressourcen
gemessen. Erforderliche Metadaten wie „Nicht eingestuft“, „Sehr leicht“ und
„Sehr schwer“ bleiben vollständig und in der bestehenden gemeinsamen Zeile.
Für mehr Platz dürfen Karten gemeinsam breiter/höher und die Spaltenzahl kleiner
werden; gleiche Kartenbereiche, reservierter Resetplatz und der ausreichende
proportionale Bildraum bleiben verbindlich. Die Regeln für höchstens zwei
Motivtitelzeilen mit Auslassung gelten weiter und werden nicht auf notwendige
Metadaten übertragen. Keine Schriftverkleinerung oder abgeschnittene Pflichtangabe
als Ersatz für ein passendes Layout.

Lange gültige Kategorien und scrollende Listen bleiben über die vorhandenen
Wege les- und auswählbar. HZ verschärft weder die 128-Zeichen-Namensgrenze noch
die Grenze von 256 Kategorien aus [KAT-1](CATEGORIES.md). Kopfaktionen, Dialoge,
Hilfetexte und randnahe Tooltips müssen in die unterstützten Fenster passen.
Das Vollhinweis-Overlay misst seine unveränderte Fraunces-Überschrift und Delight-Token getrennt;
Umbruch und Innenränder halten Texte, Rahmen und Trefferrechtecke auseinander.
Diese UI-Textanpassung verändert keine Hinweis-/Rasterfitformel.

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

Layout, Zentrierung und Trefferflächen bleiben regelmäßig. Vorhandene Buttons
und Kartenaktionen behalten ihre rechteckigen Mindesttrefferflächen von
44×44 bei UI100 und 55×55 bei UI125. Strichüberstände, Kantenglättung und
transparente Ressourcenpolster werden bei sichtbaren Hüllen, Innenrändern und
Clipping berücksichtigt; sie dürfen weder abgeschnitten werden noch Texte,
Nachbarn oder eigene getrennte Aktionen überdecken. Keine durch Wackelkonturen
verkleinerten oder verschobenen Hitboxen.

Die gemeinsame vorhandene Buttonfamilie wird fortgeführt. Katalogkarten nutzen
am Ausgangsstand einen eigenen `content_surface`-/StyleBox-Pfad und überspringen
die `BookButton`-Zeichnung. Eine Änderung allein in `BookButton` oder eine globale
Scribble-Verstärkung beweist daher keine vollständige Kartenumsetzung. HZ verlangt
das sichtbare Gesamtergebnis, keine neue konkurrierende Controlarchitektur.
Die Rasterassetpflicht aus SL gilt gezielt für die drei großen Gruppenrahmen;
sie erzwingt kein neues Bitmap für jeden kleinen Rahmen.

## HZ-D04 · Vollständige Dropdowngestaltung

Der Scope umfasst die vorhandene Kategorienauswahl, „Sortieren nach“ und die
Rätselansicht in Einstellungen. Geschlossenes Feld und ausgeklappte Liste bilden
eine zusammengehörige Darstellung:

| Bestandteil | Gestaltung und Verhalten |
| --- | --- |
| Feld und Popup-Außenrahmen | Warmes opakes Papier und unregelmäßige Kontur; darunterliegende Karten stören die Lesbarkeit des geöffneten Menüs nicht. |
| Menüzeilen | Tidy Hand, lesbare Abstände und sichere Text-/Markierungsbudgets auch für lange Werte. |
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

| Inventar am Ausgangsstand | Umfang |
| --- | --- |
| 13 aktive SVG-IDs in `game/art/book/icons.json` | `fill`, `erase`, `undo`, `redo`, `minus`, `plus`, `help`, `menu`, `nav-album`, `nav-information`, `nav-work`, `play`, `reset` |
| Weitere sichtbare Zeichen außerhalb dieses Inventars | Sortierrichtung, Zurück-/Weiter-Pfeile der Katalogseiten, Dropdown-Chevrons/-Haken und die beiden Einstellungs-Checkboxen samt Zuständen |

Vor HZ-B wird dieses Inventar gegen den tatsächlichen Startstand und seine
Verwendungen abgeglichen. Alle aktiven Ressourcen werden stilistisch konsistent
überarbeitet; das nimmt keine entfernte Playaktion wieder in die Oberfläche auf.
Vorhandene Bedeutung, zugängliche Beschriftung, Tooltips und Aktivierbarkeit
bleiben. Undo als einzelne Rücknahme und Reset als bestätigtes Zurücksetzen des
ganzen Blatts müssen eindeutig unterscheidbar bleiben. Keine Emoji-, Systemfont-
oder nur umgefärbte geometrische Standardfamilie.

Eigene konsistente lokale SVG-/Zeichnungsressourcen sind zulässig. Die aktive
Quellen-/Provisionierungsstrecke aus [Z2](Z2_SELECTION.md), einschließlich
`tools/z2_resources.py`, der HZ-B-Quelle `tools/book_icons_hz.json`, der erzeugten
SVGs und `game/art/book/manifest.json`, wird gemeinsam fortgeschrieben.
`tools/book_icons_kb.json` bleibt historische Quelle. Ein bloßes
Überschreiben generierter Dateien erfüllt den Liefervertrag nicht. Historische
BP-/SL-/KB-Originale und ihre Hashnachweise bleiben an den damaligen Stand gebunden;
neue aktive Quellen erhalten nachvollziehbare Herkunft. Reguläres Spiel,
Windows-Spieler/PCK und Webexport müssen die tatsächlich geprüften Ressourcen nutzen.

## HZ-D06 · Erhaltene Produkt- und Datenverträge

HZ verändert die Darstellung und die dafür erforderlichen gemessenen UI-Text-/
Konturbudgets. [P1](PROTOTYPE_P1.md), [KAT-1](CATEGORIES.md),
[ZA-1](ZA1_ADAPTER.md), [KAT-2](KAT2_VERIFICATION.md) und die aktuelle
[KU-Sortierung](CATALOG_SORTING.md) behalten ihre übrigen Verträge:

- Runtimeprojektion v4 samt exakten v2/v3-Lesern, Kategorien, Sortiersemantik,
  Difficulty-/Added-Werte, Präferenzen, IDs/Slots/Pfade, Definitionen/Revisionen,
  Appidentität, Save-Schema 1 und Recovery erhalten Bedeutung und Werte.
- Kartenöffnung, Reset und Reparatur bleiben an die stabile Registry-ID gebunden;
  Dialoge binden sie beim Öffnen. Sortierung oder Seitenwechsel darf die Ziel-ID
  nicht durch eine neue Karte an derselben Position ersetzen.
- Gültiger Leerbestand, leere Kategorie, Fehler, Backup- und Recoveryzustände
  bleiben unterscheidbar und erreichbar. Ausstehende Saves werden weiterhin
  geflusht; Schreibfehler blockieren unsichere Wechsel.
- Höchstens 24 aktive Karten pro Seite und die vorhandene Ressourcenfreigabe
  bleiben. Breitere Schrift begründet keinen neuen Gesamtkatalog-/Vorschaucache.
- Motivnamen und Reveal bleiben an gültigen Abschluss gebunden. Neu zeigt das
  bestehende Fragezeichen, Begonnen nur eigene Füllungen. Revealdateien,
  Bildrevisionen, Quellen-/Freigabebindungen und eigene Miniaturen ändern sich nicht.
- Geometrisches Raster, Hint-/Fit-/Drag-/Snapverhalten, Zellrenderer, Atlanten,
  Palette und Animationstiming bleiben. Die sechs Werkzeuge behalten ihre
  2×3-Anordnung; die drei großen SL-Rahmen und ihre sicheren Innenflächen bleiben.

Keine neue Rätsel-/Bildproduktion, Solveranalyse, Bewertung, Metadatenmigration,
CI-Optimierung, Hintergrund-/Themenauswahl, Engine-, Plattform- oder Bedienfunktion.
Normale Warntexte innerhalb des Boards gehören trotzdem zur neuen Schriftrolle;
ihre Schriftanpassung ist keine Freigabe einer Rasteränderung.

## HZ-D07 · Optische Textausrichtung und kleine Schriftgröße

**Eigentümerentscheidung · 21.10.2026:** Nach der Tidy-Hand-Umstellung wirken
kleine Texte insbesondere in Dropdowns und im Rätselstatus zu hoch angeordnet.
Optisch ausgewogene vertikale Ausrichtung und eine ruhig lesbare kleine
Textrolle werden gemeinsam nachgebessert. Geprüfte Spezifikationsbasis ist
`main@1260578fde94fc7bee14efe4b6636061d36238c7` mit integriertem HZ-A/B.
Der Eigentümerscreenshot ist Gestaltungsfeedback ohne verifizierte Build-/DPI-
Bindung. Schrift-/Zeilenmetriken sind ein Untersuchungsansatz, noch keine
nachgewiesene Ursache und keine Begründung für einen ungeprüften globalen Versatz.

### Ausrichtung und stabile Grundlinien

Sichtbare Buchstaben, Symbole und die umgebende Zeile bzw. Controlfläche müssen
optisch ausgewogen zusammenstehen. Die bloße Zentrierung einer Control- oder
Zeilenbox genügt nicht als Nachweis. Am geprüften Stand sind Status-, Größen-
und Schwierigkeitslabels bereits vertikal zentriert; native Dropdowns und direkt
gezeichnete Textbuttons verwenden weitere Textpfade. Die spätere Umsetzung
untersucht deren tatsächlich verwendete Metriken, Innenränder und Textzeichnung.

Die Ausrichtung verwendet stabile Grundlinien pro Textrolle, Größenstufe und
Control. Kein individuelles vertikales Nachzentrieren jeder Zeichenkette anhand
ihrer äußersten Buchstaben: „Neu“, „Begonnen“, „Gelöst“ und wechselnde
Dropdownwerte dürfen nicht in der Höhe springen. Die tatsächlichen Glyphenhüllen
einschließlich lokaler Fallbacks bleiben gemäß HZ-D02 für vollständige Darstellung,
sichere Budgets und Clipping maßgeblich. Ein rollenbezogener optischer Ausgleich
ist zulässig; seine konkrete technische Form wird erst in HZ-C festgelegt.

Die Kartenfußzeile wird als Einheit aus Blattkennung, Statuswort und Statussymbol
ausgerichtet. Kategorien behalten ihre feste Position im reservierten, bis zu
zweizeiligen Bereich. Ein- und zweizeilige Namen werden nicht jeweils neu in
diesem Bereich zentriert. Gleichbleibende Kartenbereiche verhindern Sprünge bei
Kategorie-, Filter- und Statuswechseln.

### Größenvergleich und betroffene Rollen

Die korrigierte bestehende kleine Größe **14** wird direkt mit **15 bei UI100**
verglichen; beide folgen der vorhandenen UI-Skalierung. **15 ist der bevorzugte
erste Vergleichswert, kein bereits gemessenes oder abgenommenes Endmaß.**
Korrekt ausgerichtete 14 bleibt zulässig, wenn der Vergleich ausreichende
Lesbarkeit und stimmige Hierarchie zeigt. Wahl, Begründung und Originalbelege
werden in der späteren Lieferung dokumentiert. Keine automatische Erhöhung auf 16.

| Bereich | Verbindliche gemeinsame Betrachtung |
| --- | --- |
| Dropdowns | Kategorienauswahl, „Sortieren nach“ und Rätselansicht in Einstellungen; geschlossenes Feld und offene Menüzeilen einschließlich ihrer Symbole/Markierungen. |
| Katalogkarten | Kategorienamen, Größe, vollständiger Schwierigkeitsname und Status als kleine Textrolle. Bei Vergrößerung erhalten insbesondere Kategorie und Status dieselbe kleine Schriftgröße. |
| Fußzeile | „Blatt NN“ ist am geprüften Stand bereits 15; keine automatische zweite Vergrößerung. Blattkennung, Statuswort und Symbol müssen zusammenpassen. |
| Kleine Textbuttons | Betroffene vorhandene kleine Tidy-Hand-Textbuttons in dieselbe Größenentscheidung und Ausrichtungsprüfung einbeziehen; keine neue globale Fließtextrolle. |

Eine Vergrößerung betrifft nicht pauschal Hilfe, Dialoginhalte, Tooltips oder
alle normalen Tidy-Hand-Texte. Überschriften und Hinweisziffern bleiben gemäß
HZ-D01 unverändert. Änderungen an gemeinsamen Texthelfern müssen trotzdem die
sichere Darstellung ihrer übrigen Verwendungen erhalten.

Text-/Symbolmaße, Zeilenhöhen, Innenränder und Karten-/Popupbudgets werden gemeinsam
angepasst. Vollständige Pflichtmetadaten, lange gültige Kategorien, lokale
Fallbackzeichen, Umlaute und Unterlängen müssen passen. Die feste Kategoriefläche,
Titel-/Resetreserve und ausreichender proportionaler Bildraum bleiben; dessen
bisherige Höhe von 112 × UI wird nicht zugunsten größerer Schrift verkleinert.
Bei Bedarf werden Karten gemeinsam größer oder weniger Spalten gezeigt.
Native Auswahl-/Fokus-/Scroll-/Schließwege und Mindesttrefferflächen bleiben
gemäß HZ-D03/D04 erhalten. HZ-C verändert weder Originalfontbytes noch die
Gestaltungsregeln der HZ-B-Konturen, Iconquellen oder Produkt-/Datenverträge
aus HZ-D06.

## 2. Entwicklungspakete und Nachweise

| Paket | Eigenständig abnehmbares Ergebnis | Status und Abhängigkeit |
| --- | --- | --- |
| HZ-A · Schrift und Textlayout | HZ-D01/D02 vollständig, einschließlich aller normalen Textpfade, kontrollierter Zeichenbehandlung, gemessenem Layout, Ressourcen-/Exportnachweis und nachgeführter Anleitung | Integriert über PR #288 und separat abgenommen; Abschluss in #284. |
| HZ-B · Gezeichnete Controls und Symbole | HZ-D03/D04/D05 vollständig auf den HZ-A-Textmaßen; sämtliche Konturen, geöffneten Menüs, Zustände und Piktogramme im regulären Spiel | Nach HZ-A über PR #289 integriert und separat abgenommen; #284 abgeschlossen. |
| HZ-C · Optische Textausrichtung und kleine Schriftrolle | HZ-D07 vollständig: stabile Grundlinien, begründeter Vergleich 14/15, Kategorien und offene/geschlossene Dropdowns, passende gemeinsame Text-/Symbol-/Layoutmaße | #294: Spezifikation freigegeben, noch nicht implementiert. Auf integriertem HZ-A/B; gesonderter Implementierungsauftrag erforderlich. |

HZ-D06 gilt für alle Pakete. Ein Implementierungs-PR je Paket enthält notwendige
Regressionen und Dokumentation. HZ-B hielt Rahmen, Menüs und Icons zusammen,
weil ihre Strichhüllen, Innenabstände und Zustände gemeinsam abgenommen werden.
HZ-C hält Ausrichtung, Schriftgröße und davon abhängige Layoutmaße zusammen;
eine Trennung in Größenänderung und spätere Ausrichtung würde unvollständige
Zwischenstände erzeugen. Keine zusätzliche breite Assetstudie oder ausgelagerte
spätere Test-/Dokumentphase.

Die Paketkriterien HZ-A-A01–A05 und HZ-B-A01–A06 stehen vollständig im
[abgeschlossenen Issue #284](https://github.com/venomenon328/picross/issues/284).
HZ-C-A01–A06 stehen vollständig im
[Folgeissue #294](https://github.com/venomenon328/picross/issues/294): belegte
Ursache, stabile optische Ausrichtung, begründeter Größenvergleich, vollständiges
Layout, Zustands-/Bedienregressionen und gebundene Liefernachweise.
Die bereits erfüllten A/B-Gates bleiben historisch gebunden. HZ-C besitzt eigene
Gates; frühere Abnahmen oder Mergeausnahmen erfüllen sie nicht:

| Gate | Akteur, Nachweis und Zeitpunkt |
| --- | --- |
| HZ-A-T01 / HZ-B-T01 | Implementierer vor Übergabe und Merge: Paketkriterien, feste synthetische Glyphen-/Text-/Kontur-/Zustands-/Pointerregressionen im jeweiligen Scope, tatsächliche native Windows- und Chromium-Nachweise, geprüfte Ressourcen im Export, ausgewählte Pflicht-CI sowie vollständiger Diff und getrenntes Selbstreview. |
| HZ-A-R01 / HZ-B-R01 | Separater qualifizierter Review vor Implementierungsmerge am finalen Head: tatsächlicher Diff, Kriterien, aktive Ressourcen und technische/visuelle Originalbelege. Selbstreview ersetzt diesen Review nicht. |
| HZ-A-M01 | Eigentümer vor HZ-A-Merge am gebundenen Build: normale Texte, Sonderzeichen/Auslassung, Hierarchie, lange Werte, Dialoge und Tooltips bei UI100/125 beurteilen. |
| HZ-B-M01 | Eigentümer vor HZ-B-Merge am gebundenen Build: Konturen, offene/geschlossene Menüs, Piktogramme und Zustände in Einsatzgröße sowie Katalog-/Menü-/Werkzeugbedienung beurteilen. |
| HZ-C-T01 | Implementierer vor Übergabe und Merge: HZ-C-A01–A06, gezielte synthetische Text-/Layout-/Zustandsregressionen, tatsächliche native Windows-/Chromium-Nachweise, ausgewählte Pflicht-CI, vollständiger Diff und getrenntes Selbstreview am konkreten Head. |
| HZ-C-R01 | Separater qualifizierter Review vor Implementierungsmerge am finalen Head: tatsächlicher Diff, Kriterien und technische/visuelle Originalbelege. Selbstreview oder Spezifikationsreview ersetzt dieses Gate nicht. |
| HZ-C-M01 | Eigentümer vor HZ-C-Merge am gebundenen Build: optische Ausrichtung, begründete kleine Schriftgröße, Kategorien, Statusfußzeile, Metadaten und offene/geschlossene Dropdowns bei UI100/125 beurteilen. |

Die aktuelle [CI-Policy](CI_POLICY.md) bestimmt anhand des vollständigen
Basis-/Head-Diffs sämtliche erforderlichen Jobs. `docs`, `ci-required` und alle
ausgewählten Bereiche müssen tatsächlich erfolgreich sein. Gemeinsamer UI-/
Ressourcenbezug kann mehrere Bereiche auswählen; die Paketnamen sind keine
Ausnahme. Die Darstellungsbasis sind **1280×720/UI125, 1920×1080/UI100 und
2560×1440/UI125**, ergänzt nur um konkret nötige Text-/Popup-/Zustandsgrenzen.
HZ-C vergleicht die korrigierten 14/15 unter gleichen Bedingungen und prüft
UI100→125→100, Resize sowie Auswahl-/Status-/Ansichtswechsel; keine neue
vollständige Kreuzmatrix.
Prüfungen verwenden isolierte synthetische Eingänge und Speicherprofile, keine
echten Saves oder Bestandsproduktion. Head, Basis, tatsächlicher Checkout,
Run/Attempt und Originalartefakte werden im Paket-PR gebunden. Historische
Firefox-CI-Pflichten/-Läufe werden nicht wieder geöffnet.

Die reine Spezifikationslieferung prüft nur den laut tatsächlichem Dokumentdiff
ausgewählten Dokument-/Werkzeugpfad: schnelle Tooltests, Dokumentvalidator,
vollständiger Diffcheck und `ci-required`. Ein erfolgreicher Dokumentlauf nimmt
kein HZ-T01/R01/M01-Produktgate ab. Technische Startprüfung und Ausführungswahl
gehören erst zur späteren Vorbereitung des ausdrücklich beauftragten Pakets.
