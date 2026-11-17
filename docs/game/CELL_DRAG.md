# ZR · Zellstriche am Rasterrand und Cursorzähler

## Geltung und Zuständigkeit

Dieser Vertrag besitzt Randfortsetzung einer begonnenen Zellgeste, finale
Releaseposition und den cursorgebundenen Längenzähler. Die Regeln im aktuellen
Git-Stand sind der Fachvertrag. Technische Lieferung, echte Windowszustellung
und persönliche Sichtabnahme werden getrennt am konkreten Head nachgewiesen.

| Detail | Maßgebliche Quelle |
| --- | --- |
| Startzustand, Achsenbindung, elastischer Abschnitt, Commit und Save | [P1](PROTOTYPE_P1.md) |
| Statische Vorschau und Effekte | [UI_DRAWING_STYLE](UI_DRAWING_STYLE.md) |
| Zahlenressource und Glyphen | [CLUE_TYPOGRAPHY](CLUE_TYPOGRAPHY.md) |
| Hinweisdrag und Eingabebesitz | [CLUE_INTERACTION](CLUE_INTERACTION.md) |
| Buch-/GUI-Releasebarriere | [BOOK_INTEGRATION](BOOK_INTEGRATION.md) |

## ZR-D01: Bedeutung und Darstellung des Zählers

Nur aktive linke und rechte Zellgesten mit geometrischer Länge mindestens 2 zeigen
eine Zahl. Die vorhandenen Setz-, Umwandlungs-, Rücknahme- und Radiermodi bleiben
Zellgesten; Hover und Links-Hinweisnavigation gemäß [HN](CLUE_INTERACTION.md) zeigen keinen Zähler. Die Länge umfasst
Start- und Endfeld sowie alle Zwischenfelder des aktuellen geraden Abschnitts.
Vorbelegungen, geschützte Felder und ausgelassene Mausabtastpositionen zählen mit.
Die Anzahl wirksamer Änderungen ist ausdrücklich nicht die Zählgrundlage.

Rückzug auf ein Feld blendet die Zahl sofort aus. Übernahme, Abbruch, Session-/
Seitenwechsel und ausgeblendete Arbeitsansicht hinterlassen keine Anzeige. Intern
darf der Einzelfeldabschnitt weiterhin Länge 1 haben; der Einzelklick bleibt eine
normale Zellgeste. Von Spalte 5 bis 30 ist die geometrische Länge 26.

Der Zähler verwendet die aktive Zahlenressource und ihre Bindungen aus
[CLUE_TYPOGRAPHY](CLUE_TYPOGRAPHY.md); kein zusätzlicher Font oder stiller Ersatz.
Eine dunkle Zahl mit dünner heller Kontur ist die freigegebene Ausgangsgestaltung.
Kein Hintergrund, Panel, Kasten oder rechteckiger Rahmen. Kontur und Zifferninnenräume
müssen auf Papier, Füllzellen und Seitenleiste klar bleiben.

Die optische Größe folgt der UI-Skalierung und bleibt bei Rasterzoom stabil.
Gleiche Schriftart bedeutet nicht Übernahme des zellabhängigen Hinweis-Schriftgrads.
Die gebundene ZR-Umsetzung verwendet 24×UI Schriftgrad, eine dünne helle Kontur,
12×UI Cursorabstand und 4×UI Sicherheitsrand innerhalb der Clientfläche.
Native Glyphenlager, Kontur und Antialiasing bestimmen die vollständige Hülle.
Dies dokumentiert die aktuelle Ausarbeitung; es entsteht kein neues Einstellungsmenü.

## ZR-D02: Cursoranker und sichtbarer innerer Fensterrand

Die Anzeige folgt der tatsächlichen Mausposition, auch bei Bewegung innerhalb
derselben Zelle oder über der Seitenleiste. Der logische, an Achse/Raster begrenzte
Linienendpunkt ist nicht ihr Positionsanker. Standard ist ein kleiner Abstand rechts
oberhalb des Cursors. Reicht der Platz nicht, wird der Versatz auf die andere Seite
gelegt und die vollständige Zahl einschließlich Kontur mit Sicherheitsabstand innerhalb
der Fensterclientfläche gehalten. Die Raster-/Boardgrenze ist keine Anzeigegrenze.

Verlässt der Cursor bei aktiver Geste die Fensterclientfläche, bleibt die Zahl am
entsprechenden inneren Fensterrand oder an der Ecke sichtbar. Sie wird nicht auf dem
Desktop gezeichnet und benötigt kein weiteres Fenster. Die Sichtbarkeitsbedingung
Länge mindestens 2 und die Abbruchregeln gelten auch dort.

Die rein darstellende Überlagerung darf nicht vom Board-Clipping abgeschnitten oder
von der Seitenleiste verdeckt werden und fängt keine Mausereignisse ab. Zähler,
Cursorposition und Kontur sind transiente Darstellung: kein Saveinhalt, keine
Historyaktion und keine Auswertung der versteckten Lösung.

## ZR-D03: Beginn, Endpunkt und vollständiger Abschnitt

Eine neue Zellgeste beginnt nur auf einer gültigen editierbaren Rasterzelle. Strenge
Start-/Hovertreffer und Endpunktfortsetzung sind verschiedene Aufgaben: Ein außerhalb
des Rasters begonnener Klick darf durch die neue Randbegrenzung keine Zelle treffen.

Während einer laufenden Geste werden Mauspositionen unabhängig vom aktuell
überfahrenen Control verarbeitet. Dieselbe tatsächliche Rastertransformation wie bei
Zeichnung und Hit-Test liefert die Position relativ zum Raster. Bei gebundener Achse
folgt der Endpunkt nur dieser Zeile beziehungsweise Spalte und wird auf deren erste
oder letzte Zelle begrenzt. Andere UI-Flächen frieren ihn nicht mehr ein. Es entstehen
keine Zellen außerhalb des Rasters und keine Zellbearbeitung unter der Seitenleiste.

Die Achsenwahl folgt [P1 §5.1](PROTOTYPE_P1.md#51-werkzeuge-direkte-umwandlung-und-strichgrenzen). Das gilt
auch, wenn der erste gelieferte Bewegungs- oder Loslasspunkt bereits außerhalb des
Rasters liegt. Die Richtung aus der unbegrenzten relativen Rasterposition bestimmen;
vorzeitiges Begrenzen beider Koordinaten darf die Achsenwahl nicht verzerren.

Nur ein echter erneuter Treffer der tatsächlichen Startzelle gibt die Achse gemäß
G1 frei. Ein auf den Ursprung projizierter oder begrenzter Außenpunkt sowie ein
Eingabesprung über den Ursprung lösen keine Freigabe aus. Tatsächlichen Starttreffer
und rechnerischen Endpunkt getrennt behandeln, insbesondere bei Start am Rasterrand.

Alle Zwischenzellen des aktuellen geraden Abschnitts gehören zur Geste, auch ohne
einzelne Motion-Ereignisse. Im 30 Spalten breiten Raster ergibt Start in Spalte 5 und
Zug rechts hinaus das Ende 30 und Länge 26. Alle nach den bestehenden Schutzregeln
bearbeitbaren Zellen 5–30 werden berücksichtigt. Das gilt symmetrisch für links,
oben und unten sowie für rechteckige Raster und beide Maustasten.

Elastischer Rückzug, ursprünglicher Snapshot und eingefrorener Modus folgen P1.
Die Außenbewegung wird entlang derselben gebundenen Achse ausgewertet; sie
vereinigt nicht alle jemals überfahrenen Zellen.

## ZR-D04: Finale Position, atomare Übernahme und Eingabeabgrenzung

Die Freigabe der Ursprungstaste wertet ihre eigene letzte Position aus, auch wenn
zuvor kein Motion-Ereignis für diese Lage ankam. Der so bestimmte Endpunkt muss vor
Ermittlung der finalen Änderungsmenge und Animationsrichtung sowie vor dem Commit
feststehen. Zähler, statische Vorschau, wirksame Änderungen, Miniatur und gerichtete
Animation dürfen keine unterschiedlichen Endpunkte verwenden.

Die bestehende Aufteilung zwischen `board.gd` und `drawing_board.gd` ist dabei zu
beachten: Die Zeichenschicht darf nicht vor einer letzten Endpunktkorrektur eine
veraltete Änderungsliste erfassen. Ein gemeinsamer Endpunktweg verhindert abweichende
Move-/Release-/Animationsfassungen; ein zweiter Gestenkern ist nicht beauftragt.

Atomarer Commit, No-op, Undo/Redo, Gegentastenabbruch und Sperren während
der Geste folgen P1; Vorschau-/Effektpriorität folgt UI_DRAWING_STYLE.
Loslassen über einem Button darf keine zusätzliche Buttonaktion auslösen.
Der native GUI-Releaseweg ist in BOOK_INTEGRATION beschrieben.

## ZR-D05: Native Fenstergrenze und Fokusverlust

Bei gehaltener Ursprungstaste und erhaltenem Spielfokus wird die begonnene Geste in
der nativen Windows-Fassung über die Fensterclientgrenze hinaus weitergeführt.
Loslassen außerhalb übernimmt den gültig begrenzten finalen Abschnitt. Der Cursor
bleibt sichtbar und frei beweglich: kein Einschließen im Fenster, Verstecken,
Zentrieren, Teleportieren oder dauerhaft übernommene Eingabeerfassung.

Die konkrete Ereigniszustellung und gegebenenfalls nötige vorübergehende Erfassung
werden auf der gebundenen Godot-/Windows-Fassung geprüft. Kein ungeprüftes Versprechen
aus synthetischen Viewportevents oder einem allgemeinen Betriebssystemmechanismus.
Eine Engineänderung oder neue native Abhängigkeit ist keine pauschale Freigabe dieses
Pakets; falls erforderlich, den konkreten Bedarf vor dieser Scope-Erweiterung klären.

Echter Fokusverlust, etwa Alt-Tab, bleibt vollständiger Abbruch ohne Commit. Verlorene
oder nicht mehr verlässlich zuordenbare Eingabe wird ebenfalls sicher verworfen.
Vorschau und Zähler verschwinden; aktive und wartende Effekte enden nach ZS. Kein
verspäteter Commit bei Rückkehr, keine Phantomgeste und keine hängende Tastensperre
oder Erfassung. Rückkehr nach außen losgelassener Taste startet keine neue Geste.

Ein sicherer Abbruch bei verlorener Eingabe ist kein bestandener Nachweis für das
geforderte fokussierte Außenloslassen. Beides muss getrennt berichtet werden.

## Verifikation, Paketgrenze und Abnahme

ZR-A01–A07 und ursprüngliche T01/R01/M01-Entscheidungen stehen in
[#143 / PR #145](https://github.com/venomenon328/picross/pull/145).
Gezielte synthetische Eingänge prüfen Endpunkt, Längenzähler, Sprünge,
Mouse-Up ohne Motion, Rückzug, echte/projizierte Starttreffer und Abbruch.
Native Darstellung ergänzt die Prüfung von Glyphen-/Konturhüllen und Rändern.
Aktuelle Auswahl und Stichprobe stehen in [CI_WORKFLOW_V2](../ci/CI_WORKFLOW_V2.md)
und [CI_C_NATIVE_GROUPS](../ci/CI_C_NATIVE_GROUPS.md); keine erneute historische Vollmatrix.

ZR-A06 betrifft die tatsächliche Windowszustellung: fokussiertes Außenloslassen,
Rückkehr gehalten bzw. nach Loslassen und echten Fokusverlust getrennt beobachten.
SubViewportereignisse ersetzen diese Betriebssystemgrenze nicht. Commit/Artefakt,
Client-/Bildschirmmaße, Windows-/UI-Skala und Ergebnis binden den Nachweis.
Historische Mergeausnahmen gelten nur ihrem damaligen Head und erteilen keine
neue Freigabe oder pauschale Wiederholungspflicht.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#143](https://github.com/venomenon328/picross/issues/143) und [PR #145](https://github.com/venomenon328/picross/pull/145).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CELL_DRAG.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
