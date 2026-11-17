# Buchdarstellung · Navigation, Materialien und Capture

## Geltung und Zuständigkeit

Dieses Dokument besitzt den regulären Buchroot, Material-/Papiergeometrie,
Navigation, Übergänge, Eingabebarrieren und Informationsbesuche. Es enthält
außerdem die Struktur und Typografie der Spielerhilfe. Regeln im aktuellen
Git-Stand sind der Fachvertrag; technische Lieferung, Review und persönliche
Abnahme stehen getrennt am jeweiligen Head im Issue/PR.

| Detail | Maßgebliche Quelle |
| --- | --- |
| Spiel, Save/Recovery und Abschluss | [P1](PROTOTYPE_P1.md) |
| Karten, Seitenmitgliedschaft, Filter und Fortsetzen-Panel | [Katalogdarstellung](CATALOG_PRESENTATION.md) |
| Sortierung und Sortierpräferenz | [Katalogsortierung](CATALOG_SORTING.md) |
| Schrift, kleine Controls und exakte Symbolhilfen | [HZ](HAND_DRAWN_UI.md) |
| Sidebar und Arbeitsflächenverteilung | [Sidebar](SIDEBAR.md), [Zeichensprache](UI_DRAWING_STYLE.md) |
| Native Anzeigeoptionen und Einstellungscontrols | [DISPLAY_SETTINGS](DISPLAY_SETTINGS.md) |
| Bildhaupttitel | [VIEW_TITLE_ART](VIEW_TITLE_ART.md) |
| Rätselgebundene Hintergründe und Besuchspublikation | [PUZZLE_BACKGROUNDS](../production/PUZZLE_BACKGROUNDS.md) |
| Browserpersistenz | [WEB_HOSTING](../operations/WEB_HOSTING.md) |

## Einstieg und gemeinsame Quellen

`game/main.tscn` startet ohne Zusatzargument den regulären 3D-Buchroot
`game/book/main.gd`. Windows und Web verwenden dieselbe Szene. `book/content.gd`
ergänzt die Darstellung von `ui/main.gd`; Registry, Definitionen, Session,
SaveStore, Sortierpräferenz, Recovery und Webstorage bleiben gemeinsam.
`game/data/registry.json` ist die Projektion der autoritativen Inhaltsregistry;
der Spieler enthält keine festen Studienrätsel.

`game/book/` enthält Buchkörper, Seiten, Informationsnavigation und die
Materialbilder Papier/Leder/Tisch samt Import-/Herkunftsdaten. Die Belege liegen
auch unter `licenses/Book-{paper,leather,table}.json` im Export. Das A-Original
bleibt bytegleich als Referenz und geerbte Ressourcenabhängigkeit nach
[Z2](Z2_SELECTION.md). Fonts, Hinweis-/Zellgrafik und Sidebarrahmen behalten
ihre eigenen Quellen-/Rechtebindungen.

Der tatsächliche PCK-Entrypoint und benötigte gemeinsame Ressourcen werden
geprüft. Studieninputs, Prüfprogramme und technische Berichte gehören nicht in
reguläre Pakete. `--p1-smoke` bestätigt Ressourcen, Fenster und Katalog; es
spielt keine echten Katalogrätsel nach.

## Material, Wölbung und sichere Papierflächen

| Material | Original und Importbindung | Aktive Darstellung |
| --- | --- | --- |
| Leder | [leather.json](../../game/book/leather.json) und zugehörige Original-PNG | Homogenes Material ohne eingebrannte Buchsilhouette, Fremdfläche oder fertige Schlagschatten; verlustlos, Mipmaps und wiederholbare Weltkoordinaten. |
| Umgebung | [table.json](../../game/book/table.json) und zugehörige Original-PNG | Holz mit Leinen am linken Außenrand; feste 48×32-Weltfläche ohne Kachelung oder Seitenverhältnisverzerrung. Kamera bewegt Buch/Umgebung gemeinsam; Kontaktschatten entstehen aus Deckelgeometrie. Verlustloser sRGB-Import, Mipmaps, lineare Mipmapfilterung, Repeat aus. |
| Papier | [paper.json](../../game/book/paper.json) und zugehörige Original-PNG | Verlustlos, Mipmaps, lineare Filterung, kein Repeat; Mischung mit 55 % hellem Elfenbein. Katalogseite, Seitenhälfte und Arbeits-ID bestimmen stabile Ausschnitte; Vorder-/Rückseite haben eigene Zuordnungen. Keine Spiegelung oder Zufallsvariation je Frame. |

Die Buchfalz besitzt zwei stetig anschließende reale Schultern. Innenkanten
liegen je 0,004 Welteinheiten neben der Mitte; bei Abstand 0,28 erreichen die
Schultern Höhe 0,22. Das mittige Tal liegt auf ebener Papierhöhe, ab Abstand
0,75 ist die Fläche eben. 16 von 64 Querspannen bilden diesen Bereich ab.
UVs bleiben an tatsächliche Papierkoordinaten gebunden; Lichtnormalen folgen
Deformation, Drehung und Curl. Bewegte Inhalte folgen Blattvertices, nicht
einem nachträglich über die ganze UI gelegten Verzerrungseffekt.

Ein zusammenhängender Lederdeckel enthält Rücken, Gelenkvertiefungen und
Deckelflächen. Oberseite aus passenden Streifen; Seitenblock-Unterkante mit
positivem Gelenkabstand, innere Lagen an freien Enden enger zusammengeführt.
Kein zusätzlich aufgelegtes Band oder dekorative durchstoßende Kopf-/Fußmeshes.
Der Rücken verbindet die Deckel auch unten. Beleuchtung, Abrieb und Kontakt-
schatten folgen der Geometrie. Sechs gefilterte sichtbare Lagen und breite,
flache Unregelmäßigkeiten vermeiden unaufgelöste Linien/Subpixelwellen.
Blattkrümmung bleibt am inneren Tal gebunden und landet über dem ruhenden Block.

Kopf, Kartenclip und Fußbereiche werden ausschließlich aus der projizierten
Papierfläche abgeleitet; ein geerbter Materialversatz wird nicht nochmals
addiert. Tatsächliche Glyphen-/Konturhüllen samt Antialiasing liegen mindestens
acht physische Pixel innerhalb des flachen Papierbereichs. Raster-/Hinweisfläche
bleibt eben. Dieser Sicherheitsrand verkleinert keine funktionalen Budgets.

## Navigation und Darstellung

### NAV-A · Kopf und Katalogfuß

Auf der sicheren sichtbaren Papierseite steht eine ortsfeste Kopfgruppe:

| Ansicht | Gruppe und Lage |
| --- | --- |
| Katalog | Beenden-X, Zahnrad, Hilfe am oberen rechten Rand der rechten Seite. |
| Rätsel und stabiler Abschluss | Katalog-Rückpfeil, Zahnrad, Hilfe im rechten Arbeitskopf. |
| Hilfe | Rückpfeil, Zahnrad, Hilfe am oberen rechten Rand der rechten Seite. |
| Einstellungen | Rückpfeil, Zahnrad, Hilfe am oberen rechten Rand der linken Seite. |

Der aktive Informationsort ist unterstrichen; erneute Wahl ist ein No-op für
Abschnitt, Lesestelle und Bewegung. Rückweg und zugänglicher Name beziehen sich
auf den tatsächlichen Besuchsursprung. Exakte Symboltooltips stehen in HZ/NAV-A.
Hilfe, Einstellungen und Beenden bleiben auch ohne Session erreichbar.

Der Katalogfuß enthält links nur den Rückpfeil, daneben „Seite n von m“, rechts
nur den Vorwärtspfeil. Pfeile blättern vollständige Doppelseiten; unmögliche
Richtungen sind inaktiv sichtbar, bei einer Seite beide. Die gemeinsame
Control-/Trefferfamilie folgt HZ. Die Symbolgruppe und Trefferzahl beginnen auf
derselben Höhe ohne zusätzliche Höhenzeile. Seitlicher Textbedarf wird gemessen
und bei Bedarf umbrochen. Fehlerclip, Fortsetzen-Panel, Sortierung/Filter,
Titel und Controls bleiben kollisionsfrei.

### Seiten und Bewegungen

Katalogmitgliedschaft, unabhängige Scrollflächen, responsive Spalten und
Karteninhalt folgen CATALOG_PRESENTATION; Filter-/Sortierreihenfolge folgt
CATALOG_SORTING. Nur echte Seitenwechsel animieren. Unveränderte Ziele oder
Randbefehle bewegen nichts.

| Route | Dauer | Gebundene Darstellung |
| --- | ---: | --- |
| Katalogseite wechseln | 0,85 s | Vorwärts rechts→links, rückwärts umgekehrt. Ziel beginnt mit beiden Offsets null; Abbruch erhält beide Quellwerte. |
| Neues/begonnenes Rätsel öffnen | 3,0 s | Drei getrennte Blätter nach links; Kamera fährt im zweiten Teil nah auf die rechte Arbeitsseite. Zusätzliche Blätter bleiben neutral. |
| Arbeit/stabiler Abschluss → Katalog | 1,8 s | Herauszoomen mit drei Blättern links→rechts; Quellsnapshot enthält aktuelle Bearbeitung. |
| Katalog/Arbeit → Information oder zurück | 0,85 s | Ein Blatt; nah links für Einstellungen, nah rechts für Hilfe, weit mittig für Katalog. |
| Einstellungen ↔ Hilfe | 0,65 s | Reiner Kamerapan zwischen den beiden nahen Seiten. |

Smoothstep verbindet gebundene Endlagen ohne Overshoot. Schrift wird nie
gespiegelt. Die Arbeitskamera zeigt obere Buchkante, Deckel und Seitenblock;
untere Kante bleibt außerhalb des Arbeitsausschnitts, der Katalog zeigt das
ganze Buch. Raster-, Hinweis-, Schrift-, Sidebar- und Trefferbudgets bleiben.
Kleine Rätsel werden nicht künstlich vergrößert.

Gelöste Blätter öffnen unmittelbar den stabilen Abschluss nach P1 §5.4.
Bestätigter Reset dort öffnet dasselbe leere Blatt ohne Buchanimation. Die
aktive Abschlusspräsentation nimmt noch keinen Rückkehrbefehl an.
`show_album()` bleibt für Start, Reset, Information und interne Stabilisierung
unmittelbar. Idle-Escape führt nicht zum Katalog.

### Informationsbesuch

Vor dem ersten Await wird genau ein Ursprung gebunden: Katalog oder tatsächlich
geöffnete Arbeit/stabiler Abschluss samt ID. Ein Sessionobjekt im Katalog zählt
nicht als Arbeitsansicht. Der Informationsursprung bleibt getrennt vom
Arbeit→Katalog-Rückkehrkontext. Filter, Sortierpaar, Seite, Auswahl und beide
Katalogoffsets bleiben erhalten.

Rückkehr lädt keinen alten Arbeits-/Optionssnapshot. Zellen, History/Redo,
Werkzeug/Farbe, Zoomwunsch und Hinweisanker bleiben; bewusst geänderte Optionen
gelten weiter. Jede Informationsseite behält im Besuch ihren eigenen Scrollstand
und begrenzt ihn bei Reflow. Ein neuer Besuch beginnt oben. Die ungewählte
Informationsseite ist im Ruhezustand unsichtbar und unfokussierbar.

Vor Eintritt aus Arbeit und vor Rückkehr dorthin gilt der Pflichtflush.
Katalogbesuche erzeugen keine zusätzliche Rätselsavepflicht. Informationen
verwenden dieselben regulären Controls und Optionssignale in eigenen Scroll-/
Clipflächen. Bildhaupttitel und Kopfgruppe liegen außerhalb der Scrollflächen.
Kein persistentes Informationsgedächtnis und kein Verlaufstexturcache.

## K-B: direkte Fortsetzung

Das Fortsetzen-Panel verwendet dieselbe kanonische ID-Route wie eine Karte.
Beim Klick wird das Ziel neu aufgelöst; fallibler Flush, PREPARING-/Capture-/
Releasebarriere und Generationen bleiben verbindlich. Kategorie, Filter, Seite
und beide Scrollstände bleiben im Rückkehrkontext. Es wird nicht zur eventuell
ausgefilterten Zielkarte gescrollt. Ein gültiger rekonstruierter begonnener
Stand kann angeboten werden, behält aber seine Repair-/Recoverygrenzen.
Panelgeometrie und Sichtbarkeit stehen in CATALOG_PRESENTATION; Merkerformat
und Schreibanlass in P1.

Die eigene Fortschrittsminiatur muss schon vor dem gesperrten Katalog-Zielcapture
synchron zum bestätigten Stand gebunden sein. Der offene Katalog aktualisiert sie
auch nach Zelländerungen ohne Hover. Diese Captureanforderung verändert keine
Karten-/Kopfgeometrie.

## Hintergrundbilder und passive Dekoration

Aktive Bildprofile, Hintergrundzustände, Quellenbindung, Besuchstoken,
Publikationspunkt und begrenzte Bildreferenzen folgen ausschließlich
PUZZLE_BACKGROUNDS. Die Darstellung ist Teil der tatsächlichen Seiten-/
Capturehierarchie; Layout, Trefferflächen und Übergangsdauer bleiben unverändert.
Legacy-/Hilfepilot und deren Platzierungsgrenzen stehen in UI_DRAWING_STYLE/ZS-D04.
Die Ebene ignoriert Pointer, Fokus und Scrollen.

## Capture, Eingabebesitz und Unterbrechungen

Ruhende Ansichten verwenden echte Controls. Während Vorbereitung/Bewegung liegt
dieselbe UI in einem transparenten SubViewport mit tatsächlicher Fensterauflösung.
Quelle wird einmal aufgenommen, Zielpräsentation verwendet denselben angenommenen
Zustand. Beim Katalogblättern trägt die Rückseite die andere Zielhälfte; beim
Rätselöffnen bleibt sie neutral. Premultiplizierte Alpha-Komposition erhält
Text-/Rasterkanten. Auf keiner Fläche werden unverdiente Namen/Reveals sichtbar.

Maximal drei bewegte Blätter, ein wiederverwendeter Capture-Viewport und drei
Informationssnapshots (Quelle plus höchstens zwei Zielseiten) sind gleichzeitig
aktiv. Beide Informationsseiten werden getrennt in ihrem Nahmaßstab aufgenommen;
beim Pan sind beide mit eigenem Inhalt sichtbar. Ende/Abbruch gibt alle transienten
Texturen und Capture frei. Die neun Textur-/Direktübergaben behalten höchstens
vier Kanalstufen Abweichung und mittlere Abweichung ≤0,1; Einpixel-/Alpha-
Gegenproben gehören zum betroffenen Nachweis.

Quelle, Ziel, IDs, Sessionbindung und Generation werden vor dem ersten Await
fixiert. Vorbereitung, Bewegungszeit und Frameabstände sind getrennte Größen.
Gesten, Popups und Tooltips werden vor Beginn geschlossen. Weitere Eingaben
werden verworfen, ohne Queue oder späteres Nachholen. Gehaltene Tasten müssen
losgelassen werden, danach ist ein frisches Down nötig. Radereignisse sind
keine gehaltenen Tasten. Fokuswiederkehr gleicht außerhalb erfolgte Releases
mit der tatsächlichen Tastenmaske ab.

| Unterbrechung | Stabile Wirkung |
| --- | --- |
| Resize, UI-Wechsel, Fokusverlust | Gebundenes Ziel stabilisieren und neu vermessen. |
| Escape/Abbruch beim Blättern oder Rätselöffnen | Erhaltenen Quellkatalog samt beiden Offsets zeigen. |
| Escape/Abbruch bei Arbeit→Katalog | Gebundenen Zielkatalog samt vollständigem Kontext zeigen. |
| Escape beim Informationseintritt | Ursprüngliche Quelle zeigen. |
| Escape beim Informationspan | Vorherige Informationsseite mit demselben Besuchsursprung zeigen. |
| Escape bei Informationsrückkehr | Ursprüngliches Ziel sofort zeigen. |
| Normales Ende | Gebundenes Ziel; Releasebarriere bleibt bis zum Loslassen bestehen. |
| Beenden | Generation entwerten und Ressourcen lösen, anschließend Pflichtflush/Schließvertrag ausführen. |

Jede Stabilisierung entwertet alte Awaits. Fokusmeldungen während Reparenting
werden außerhalb des reentranten Baumumbaus generationsgebunden behandelt;
Gesten werden unmittelbar storniert. Alte Fortsetzungen dürfen weder neue
Navigation noch verlorene Eingaben erzeugen.

Das Board wertet die Loslassposition genau einmal aus und lässt das Up danach
durch die normale GUI-Zustellung laufen, damit der ursprüngliche Mausempfänger
freigegeben wird. Das gilt auch für Hinweise und Gegentastenbarriere. Außen-Up
aktiviert keinen anderen Button. Die Übergangssperre konsumiert nur eigene
Ereignisse; kein globaler Input-Reset oder hängender Down-Merker.

Leere bzw. nur aus Whitespace bestehende Tooltips erzeugen kein Panel. Geöffnete
benutzerdefinierte Tooltips werden per `queue_free()` verzögert abgebaut; kein
synchrones `hide()` am Godot-eigenen Popup während der Ereigniszustellung.
Dies gilt auch für passive `CatalogTip`-Beschriftungen. Sinnvolle verzögerte
Hilfen behalten ihre Darstellung nach dem HZ-Vertrag.

## Bildhaupttitel · BTI-C / #533

Ressourcen, optische Zentrierung, Titelvorrang und Fallbacks stehen ausschließlich
in [VIEW_TITLE_ART](VIEW_TITLE_ART.md). Navigation folgt NAV-A oben; historische
untere Informationsbuttons werden nicht zusätzlich gezeichnet.

## Spielerhilfe · HIL-1 / #500

Der gemeinsame `help_panel` enthält vier direkt anwählbare Kapitel, kurze
Absätze und passive Lehrdiagramme aus `ui/help_panel.gd`, `help_examples.gd`
und `help_example.gd`. Die rechte eigene Scroll-/Clipfläche, Papier-/Falzränder,
obere Rücknavigation und der Meldungsraum aus `information.gd` bleiben Grundlage.
Ein neuer Informationsbesuch setzt Hilfe auf Spielprinzip zurück. Die Kapitelwahl
zeigt dessen Anfang; ein Pan zu Einstellungen und zurück erhält Kapitel und
Scrollstand. Das ist transienter Besuchskontext, kein Saveformat oder neue Option.

**HIL-REG-A / #548:** Die vier Kapitelzugänge stehen außerhalb des Artikelclips
in einem festen, linksbündigen Register. Bei ausreichend gemessener Papierbreite
liegt es links vom Artikel; andernfalls bilden dieselben Controls eine kompakte,
bei Bedarf mehrzeilige Leiste darüber. Schriftmetrik, UI-Skala, vollständige
44/55-px-Trefferflächen, Diagramme und Scrollbarreserve bestimmen den Wechsel.
Der aktive Eintrag erhält eine stabile leicht unregelmäßige Unterstreichung;
Hover und Tastaturfokus auf einem anderen Kapitel erhalten denselben
Unterstrich mit geringerer Deckkraft statt Fläche, Umrandung oder seitlichen
Fokusstrichen. Nur der Artikel scrollt.
Die erste vorhandene Abschnittsüberschrift beginnt den Artikel. Pangolin-Absätze
verwenden 20/25 px bei UI100/125 und sind bei hinreichender Breite auf 75
mittlere Zeichenbreiten begrenzt (mit Wortumbruch Richtwert 60–75 Zeichen); Lehrbilder dürfen den weiteren Artikelraum nutzen.
Kapitelwechsel beginnt oben, Einstellungenpan und Reflow erhalten die Lesestelle
innerhalb des Besuchs. Register, Text und Diagramme bleiben in derselben
Capturehierarchie. Bildhaupttitel, äußere obere Navigation, Papier/Falz und
Status-/Retryraum haben Vorrang. Inhalte, Regeln und Besuchsursprung bleiben.
Alle verschachtelten Labels tragen `base_font` und werden rekursiv skaliert;
Überschriften erhalten ausdrücklich die in [HZ](HAND_DRAWN_UI.md)
zugeordnete Sonderrolle. Auch Kapitelbuttons
tragen transparente Papierdarstellung und skalierte HZ-Trefferflächen. Die
Diagramme besitzen keine Session, Eingabe- oder Effektsteuerung. Zellmasken
liegen auf einer eigenen Shader-Ebene, Zahlen und Raster außerhalb davon.
Die aktiven Zahlen-/X- und Rasterzeichenhelfer werden gemeinsam verwendet.
Captures nehmen die vollständige Controls-Hierarchie mit; kein eigenes Overlay
oder stehenbleibendes Lehrbild während eines Übergangs.

## Einstellungsseite · ANZ-A-N03 / #527

Anordnung, Gruppen, Felder und Erklärungen folgen DISPLAY_SETTINGS. Die
Schriftrollen stehen in HZ. Diese Seite ist Teil des Informationsbesuchs und
setzt keine Hinweisanker zurück; kein zusätzliches Beenden-Widget oder manueller
Hinweisreset. Rückweg, Scroll-/Fokuskontext und Flush-/Recoveryguard folgen oben.

## Speicher- und Fehlergrenzen

Vor einer Zielanimation werden gültige Ziel-ID und nötiger Flush geprüft.
Fehler erhalten Quelle, ausstehenden Zustand und erreichbaren Retry-/Recoveryweg.
Die Präsentation eines angenommenen Ziels aktiviert oder sichert es nicht erneut:
Capture, Endpose und Reparenting erzeugen keine Saveaktion.

Saveformate, Slot-Recovery und Revisionswechsel stehen in P1 bzw. den dort
zugeordneten Quellen. Ein ungültiger Slot sperrt nur sein Blatt. Gültiger
Leerbestand und Ladefehler sind unterscheidbar. Einstellungen/Hilfe/Beenden
benötigen keine Session.

Katalog-Beenden und native Fensterschließung invalidieren zuerst Übergänge und
nutzen danach den vorhandenen Flush. Fehler lassen die App offen. Die eigene
Web-Beendenaktion wartet auf bestätigten Save- und Präferenzsync; Fehler bleiben
mit Retry erreichbar. Browsergesteuerter Tab-/Prozessabbruch hat die Grenzen aus
WEB_HOSTING.

## Prüfzuordnung

Aktuelle Auswahl und bewusst nicht automatisch abgedeckte Lifecyclefälle stehen
im [nativen Modulvertrag](../ci/CI_C_NATIVE_GROUPS.md). `tools/book_lifecycle.py`
verwendet bei ausdrücklichem Diagnoseauftrag den regulären Produktroot und einen
synthetischen Katalog; historische Studien-/Vollmatrizen sind keine Dauerpflicht.
Logik der Hilfe-Beispielschlüsse, Komponentenlayout, echte Buchbedienung und
persönliche Sichtabnahme sind unterschiedliche Nachweise.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#493](https://github.com/venomenon328/picross/issues/493), [#496](https://github.com/venomenon328/picross/issues/496), [#498](https://github.com/venomenon328/picross/issues/498), [#500](https://github.com/venomenon328/picross/issues/500), [#548](https://github.com/venomenon328/picross/issues/548) und [#549](https://github.com/venomenon328/picross/issues/549).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/BOOK_INTEGRATION.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
