# ZR: Zellstriche am Rasterrand und Cursorzähler

Stand: 15.10.2026 · Spezifikation 0.2 · **Laufzeit umgesetzt; Verifikation und Abnahme getrennt**

## Geltung und Entscheidungsbindung

[Issue #143](https://github.com/venomenon328/picross/issues/143) führt das gemeinsame
Entwicklungspaket, Akzeptanz ZR-A01 bis ZR-A07 und den späteren Liefer-/Abnahmestand.
Der Eigentümer hat die besprochene Lösung am 15.10.2026 als Spezifikation freigegeben
und ausdrücklich entschieden: Bei Cursor außerhalb des Fensters bleibt die Zahl am
inneren Fensterrand sichtbar. Die Spezifikationspflege ist kein Implementierungs-,
Merge- oder Releaseauftrag und keine bestandene Maus-/Sichtprüfung.

Die Spezifikationsbasis ist `main@3b64e1368735a1e9221389a48c51eaed0b881515`.
Die Umsetzung führt PR #145 nach Abgleich und konfliktfreier Integration von
`main@662453af36befdd4b61041d69f0229075f949a3e` fort. Laufzeit und
[Spielanleitung](../game/README.md) sind umgestellt; [Prüfzuordnung](CELL_DRAG_VERIFICATION.md),
Issue und PR trennen CI, native Windows-Nachweise und Eigentümergates.
Dieses Dokument ersetzt ausschließlich
die folgenden entgegenstehenden Sollformulierungen; historische Nachweise bleiben
an ihren jeweiligen Commit gebunden:

| Bestehende Quelle | Gezielte Ablösung durch ZR |
| --- | --- |
| [P1](PROTOTYPE_P1.md), D-27 und §5.1 | Sichtbarer Einzelfeldzähler und Verankerung am Strichende/Rasterviewport werden durch Sichtbarkeit ab Länge 2 und Cursor-/Fensteranker ersetzt. Die geometrische Zählregel bleibt. |
| [P1](PROTOTYPE_P1.md), §5.1 | Einfrieren am letzten gültigen Rastertreffer außerhalb des Rasters entfällt. Eine im Raster begonnene Geste folgt der Maus entlang ihrer Achse bis zur gültigen Rastergrenze, auch über anderer UI. Fokusverlust bleibt vollständiger Abbruch. |
| [Gestaltungskonzept](DESIGN_CONCEPT.md), §5.1 | Die Zahl 1 wird nicht mehr angezeigt; Schrift und Platzierung des Zählers folgen ZR-D01/D02. G1, GP-48 und die elastische Vorschau bleiben. |
| [Hinweis-Typografie](CLUE_TYPOGRAPHY.md) und übrige UI-Schriftrollen | Nur der Zellgestenzähler verwendet zusätzlich dieselbe aktive Hinweisfont. Zellabhängige Hinweisgrößen, Slots, Fit, Farben und andere UI-Schriften ändern sich nicht. |

Die [Produktdefinition](PRODUCT_DEFINITION.md), nicht ersetzte P1-Regeln,
[Zeichensprache](UI_DRAWING_STYLE.md) und das [Projektprofil](PROJECT_PROFILE.md)
bleiben verbindlich. Anleitung und native Bedienhilfe beschreiben die gelieferte
Randfortsetzung und den Cursorzähler. Aktueller Paketstatus
steht in #143, nicht in historischen offenen Gate-Texten älterer Lieferberichte.

## ZR-D01: Bedeutung und Darstellung des Zählers

Nur aktive linke und rechte Zellgesten mit geometrischer Länge mindestens 2 zeigen
eine Zahl. Die vorhandenen Setz-, Umwandlungs-, Rücknahme- und Radiermodi bleiben
Zellgesten; Hover und MMB-Hinweisnavigation zeigen keinen Zähler. Die Länge umfasst
Start- und Endfeld sowie alle Zwischenfelder des aktuellen geraden Abschnitts.
Vorbelegungen, geschützte Felder und ausgelassene Mausabtastpositionen zählen mit.
Die Anzahl wirksamer Änderungen ist ausdrücklich nicht die Zählgrundlage.

Rückzug auf ein Feld blendet die Zahl sofort aus. Übernahme, Abbruch, Session-/
Seitenwechsel und ausgeblendete Arbeitsansicht hinterlassen keine Anzeige. Intern
darf der Einzelfeldabschnitt weiterhin Länge 1 haben; der Einzelklick bleibt eine
normale Zellgeste. Von Spalte 5 bis 30 ist die geometrische Länge 26.

Der Zähler verwendet dieselbe tatsächlich aktive Schriftressource wie die
Hinweisziffern, aktuell Delight Coffee. Fontbytes, Herkunft und Nutzungshinweise
bleiben unverändert; kein neuer Font, keine Systemfontsuche und kein stiller Ersatz.
Eine dunkle Zahl mit dünner heller Kontur ist die freigegebene Ausgangsgestaltung.
Kein Hintergrund, Panel, Kasten oder rechteckiger Rahmen. Kontur und Zifferninnenräume
müssen auf Papier, Füllzellen und Seitenleiste klar bleiben.

Die optische Größe folgt der UI-Skalierung und bleibt bei Rasterzoom stabil.
Gleiche Schriftart bedeutet nicht Übernahme des zellabhängigen Hinweis-Schriftgrads.
Konkreter Schriftgrad, dünne Konturstärke und Abstand werden anhand nativer Glyphen
und der bestehenden UI-Maßstäbe gewählt; kein neues Einstellungsmenü.

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

Die erste eindeutige Bewegung wählt wie bisher horizontal oder vertikal. Das gilt
auch, wenn der erste gelieferte Bewegungs- oder Loslasspunkt bereits außerhalb des
Rasters liegt. Die Richtung aus der unbegrenzten relativen Rasterposition bestimmen;
vorzeitiges Begrenzen beider Koordinaten darf die Achsenwahl nicht verzerren. Bei
diagonalem Gleichstand bleibt nur die Startzelle, bis eine Richtung eindeutig ist.

Nur ein echter erneuter Treffer der tatsächlichen Startzelle gibt die Achse gemäß
G1 frei. Ein auf den Ursprung projizierter oder begrenzter Außenpunkt sowie ein
Eingabesprung über den Ursprung lösen keine Freigabe aus. Tatsächlichen Starttreffer
und rechnerischen Endpunkt getrennt behandeln, insbesondere bei Start am Rasterrand.

Alle Zwischenzellen des aktuellen geraden Abschnitts gehören zur Geste, auch ohne
einzelne Motion-Ereignisse. Im 30 Spalten breiten Raster ergibt Start in Spalte 5 und
Zug rechts hinaus das Ende 30 und Länge 26. Alle nach den bestehenden Schutzregeln
bearbeitbaren Zellen 5–30 werden berücksichtigt. Das gilt symmetrisch für links,
oben und unten sowie für rechteckige Raster und beide Maustasten.

Zurückziehen verkürzt weiterhin elastisch: Vorschau und finaler Commit enthalten nur
den aktuellen Abschnitt, nicht die Vereinigung aller jemals überfahrenen Zellen.
Eine fortgesetzte Außenbewegung wird ebenfalls entlang der gebundenen Achse ausgewertet.
Startsnapshot, ursprüngliche Startzustandskategorie, Modus, Werkzeug und Farbe bleiben
über Rückzug und Achsenneuwahl eingefroren. GP-48 schützt Vorbelegungen unverändert.

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

Ein wirksamer Strich bleibt genau eine atomare Aktion mit exaktem Undo/Redo.
No-ops erzeugen keine History. Der bestätigte Zustand und seine Speicherung oder
Abschlussprüfung warten weiterhin nicht auf Animationen. Die vorhandenen Vorschau-,
Schutz-, Miniatur-, Hinweisstatus-, Effekt- und Save-/Recoveryverträge bleiben.

Die laufende Zellgeste behält ihre zugehörigen Eingaben: Loslassen über einem Button
darf nicht zusätzlich den Button auslösen. Escape und Gegentasten-Down brechen gemäß
P1/ZS vollständig ab; nach Gegentastenabbruch beide Tasten freigeben und erst mit
frischem Down beginnen. Falsches Up ohne vorangehenden Gegentastenabbruch bleibt
unbeachtlich. Keine Navigation, kein Zoom oder Auto-Scrollen während der Zellgeste.

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

Ein gemeinsames Entwicklungspaket in #143 umfasst Endpunkt-/Ereignisverarbeitung,
Cursoranzeige, notwendige Tests und aktualisierte Bedienhilfe. Keine unabhängigen
Zwischenmerges mit widersprüchlichem Zähler-/Gestenverhalten. Die Spezifikation ist
freigegeben; die Laufzeitumsetzung liegt im selben Draft-PR. Konkrete Prüfergebnisse
und offene Abnahmen sind commitgebunden im Issue/PR auszuweisen.

Die Akzeptanzkennungen ZR-A01–A07 im Issue konkretisieren diesen Vertrag. Automatisierte
gezielte Regressionen verwenden feste synthetische technische Eingaben und isolierte
Profile: alle vier Ränder, beide Tasten, Rechtecke, große Eingabesprünge, Mouse-Up ohne
letztes Motion, Rückzug, echte versus projizierte Starttreffer, diagonaler Gleichstand,
Vorbelegungsschutz, Abbruch, No-op, Undo/Redo und unveränderte Save-/Animationspfade.

Native Darstellungsproben prüfen tatsächliche Schrift, Kontur, Hintergrundfreiheit,
Cursoranker und vollständige Anzeige an Clienträndern/Ecken. Die aktuelle
[CI-Policy](CI_POLICY.md) bestimmt Pflichtselektion und kompakte Fenster-/UI-Matrix;
keine neue vollständige Kreuzproduktgalerie oder rätselspezifische CI-Fallliste.
Reine Spezifikationspflege verlangt keine behaupteten neuen Spielnachweise.

ZR-A06 benötigt den tatsächlichen nativen Windows-Export: schnelle Züge hinaus,
Loslassen außerhalb, Rückkehr gehalten oder nach Außenloslassen sowie Fokusverlust
getrennt prüfen. Synthetische SubViewport-Tests ersetzen nicht die Ereigniszustellung
über die Betriebssystem-Fenstergrenze. Commit/Artefakt, reale Client-/Bildschirmgröße,
Windows-/UI-Skalierung und Ergebnis binden den Nachweis.

Vor einem späteren Implementierungsmerge müssen ausgewählte Pflicht-CI, unabhängiges
Review des konkreten Heads, native Windows-Nachweise und Eigentümerprobe ZR-M01
vorliegen. Der technische Bearbeiter liefert Reproduktion und Belege; der Eigentümer
prüft schnellen linken/rechten Randzug, Außenloslassen, Randzähler und Lesbarkeit.
Die längere [Spielerprobung #24](https://github.com/venomenon328/picross/issues/24)
bleibt separat; alte Abnahmen werden weder erweitert noch wieder geöffnet.
Eine passende spätere Mergefreigabe bleibt erforderlich.

Nicht enthalten sind neue Rätsel, Solver-/Adapterarbeit, Fontproduktion, Hinweis-
oder Sidebarlayout, Zellstil-/Timingänderung, Saveformatmigration, Wertung, zusätzliche
Werkzeuge/Optionen/Modifier, allgemeine Eingabeplattform, Auto-Scrollen/Pan,
Engine-/Plattformwechsel oder CI-Optimierung. Die vorhandene Schriftressource wird
wiederverwendet; keine neuen Rechtebehauptungen oder geänderten Fontdateien.
