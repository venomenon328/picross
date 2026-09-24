# P1: Großraster- und Bedienprototyp

Stand: 24.09.2026 · Spezifikation 0.10 · P1.3-Variante A nach R7; Eigentümerabnahme offen

## 1. Geltung, Auftrag und Quellen

Paketquelle ist [Issue #5](https://github.com/venomenon328/picross/issues/5). Hier stehen die versionierten P1-Verträge; das Issue führt Auftrag, aktuellen Ausführungsstand, offene Prüfungen und spätere Entscheidungen. Änderungen an diesen Verträgen sind in Datei und Issue-Verweis konsistent nachzuführen, nicht in einer zweiten parallelen Vollspezifikation.

Maßgebliche Grundlagen sind [Produktdefinition](PRODUCT_DEFINITION.md), [Gestaltungskonzept](DESIGN_CONCEPT.md), [Projektprofil](PROJECT_PROFILE.md) und [lokaler Workflow](dev-rules/WORKFLOW.md); Einstieg bleibt [AGENTS.md](../AGENTS.md). Vor Ausführung die aktuellen Quellen und Issue-Kommentare prüfen.

Die Spezifikationspflege 0.2 wurde über PR #6 gemergt, der technische P1.0-Preflight über PR #13. [P1.1 / Issue #8](https://github.com/venomenon328/picross/issues/8) und [P1.2 / Issue #9](https://github.com/venomenon328/picross/issues/9) wurden über PR #14 als `acc9c51161a18cca17813a8e44c07b2cf074cd44` in `main` integriert. Die Eigentümerprobe und ihre noch offenen Einzelergebnisse bleiben davon getrennt. [P1.3 / Issue #11](https://github.com/venomenon328/picross/issues/11) wird auf `feat/11-p1-persistence` gegen diesen Stand geliefert.

**Ist/Soll:** D-07 bis D-22 sind mit #9 umgesetzt; technische Nachweise und verbleibende
Abnahmen stehen im [P1.2-Prüfbericht](P1_2_VERIFICATION.md) und PR #14. Die früheren
P1.1-Prüfungen bleiben historische Nachweise ihres damaligen Vertrags, keine
Eigentümerabnahme des neuen Verhaltens.

**Paketgrenze:** Diese Spezifikation beschreibt den gesamten P1-Vertrag. #8 liefert F-01, Mausstriche, eigene Miniatur, Undo/Redo und Abschluss. #9 ergänzt F-02/F-03, Farben, Zoom/Pan und interaktive Miniaturnavigation. #11 ergänzt lokale Persistenz und Recovery; die integrierte 500-Aktionen-Prüfung folgt getrennt mit #12. Aktuelle [Anleitung](../prototypes/p1/README.md), [P1.3-Prüfbericht](P1_3_VERIFICATION.md) und historischer [P1.2-Prüfbericht](P1_2_VERIFICATION.md).

Die P1-Entscheidungen konkretisieren den begrenzten Bedienversuch. Sie legen weder die endgültige Produktengine noch die gesamte Betriebssystemmatrix, Wertung oder Themenwahl fest. Frühere P1-Vorschläge in Issue-Revision 0.1 und Gestaltungskonzept Abschnitt 7 sind innerhalb dieses Scopes abgelöst; globale Produktfragen bleiben offen.

## 2. Bestätigte Entscheidungen und Referenzumgebung

| ID | Entscheidung für P1 | Stand und Grenze |
| --- | --- | --- |
| D-01 | Native Windows-Desktopfassung mit Godot Standard und typisiertem GDScript, Windows-11-Testplattform. | Kein C#/.NET-/Browserparallelweg; keine endgültige Produktstackentscheidung. Versionsbindung in Abschnitt 7. |
| D-02 | Reduzierte Spielprobe: reale Bearbeitung, Abschluss und später Speicherung; keine Sterne-/Fehlerwertung, Live-Fehlerhilfe oder Hypothesen. | Bestätigte Funktionen des späteren Produkts werden nicht gestrichen. |
| D-03A | Elastische Strichvorschau: Rückwärtsziehen verkürzt; Loslassen übernimmt eine atomare Aktion. | Unverändert, auch für die neuen Rücknahmestriche. |
| D-03B | Werkzeug und Modus bleiben je Strich eingefroren; kein Mehrfachtoggle beim Zurückziehen. | Der frühere allgemeine Schutz vorhandener Gegenmarkierungen ist durch D-15 für Füllung↔X abgelöst. |
| D-04 | Hintergrundfelder müssen für den Abschluss nicht vollständig ausgekreuzt werden. | Richtige vollständige Füll-/Farbverteilung erforderlich. |
| D-05 | Referenz: Windows 11, 2560×1440, Maus, Ryzen 7 5800X, RTX 3070. | Frühere Nutzerangaben; tatsächliche Fenstergröße und Anzeigeskalierung der Probe noch nicht vollständig protokolliert. |
| D-06 | P1 wird mit Maus umgesetzt und abgenommen. | Tastatur-/Controllerbedienung und M-05 sind kein P1-Scope oder Gate; spätere alternative Produkteingaben bleiben erhalten. |
| D-07 | Größeres Standardfenster, nutzbar bei 1080p und 1440p, ohne automatische Riesenraster. | Fenster-/UI-Größe und Arbeitszoom getrennt; Abschnitt 5.2. |
| D-08 | Gefüllte Zellen bleiben auch an dicken Fünferlinien visuell getrennt. | Kontrast und Zwischenraum für alle vier Farben und Arbeitszoomstufen; keine verschmolzenen L-/Blockformen. |
| D-09 | Normales Werkzeug neutralisiert Füllungen mit links und Leermarkierungen mit rechts. | Grundregel der Rücknahmestriche; die frühere Gegenmarkierungs-Schutzregel ist durch D-15 abgelöst. |
| D-10 | Ergebnisbild darf deutlich detaillierter sein als das abstrahierte Rastermotiv. | Klar erkennbar dasselbe Motiv, keine Pflicht zu identischer Pixelmaske oder Bildauflösung; Abschnitt 5.4. |
| D-11 | An den Rasterrändern stehen keine laufenden Zeilen-/Spaltennummern. | Dort erscheinen ausschließlich Lösungshinweise beziehungsweise deren Überlaufmarker. Koordinaten bleiben separat im Arbeitsbereich sichtbar. |
| D-12 | Hinweise bleiben direkt im Arbeitsbild; keine separate Hinweisansicht. | Regulär passende Folgen werden vollständig gezeichnet. Physischer Überlauf erhält je betroffener Linie einen kompakten Marker und vollständigen farbigen Hover-Tooltip im Arbeitskontext. |
| D-13 | Arbeitszoom hat eine deutlich feinere monotone Stufenfolge. | Gesamtansicht bleibt separat; `+`/Rad hoch vergrößert nur, `−`/Rad runter verkleinert nur oder bleibt am jeweiligen Grenzwert. |
| D-14 | Farbhinweise zeichnen die Zahl selbst in der Rätselfarbe. | A–D-Suffixe sind standardmäßig aus und als optionale Accessibility-Darstellung einschaltbar. |
| D-15 | Links wandelt X direkt in die aktive Farbe, rechts eine Füllung direkt in X um. | Rücknahmestriche entfernen weiterhin nur den am Start vorhandenen Zieltyp; direkte Gegenmarkierungsumwandlung gilt für Setzstriche. |
| D-16 | Überlauf kürzt auf Ebene vollständiger einzelner Hinweise. | Ein unter direkter monotoner Draggeometrie und festen Markerplätzen maximal sinnvoller zusammenhängender Ausschnitt bleibt sichtbar; `…` markiert ausschließlich verborgene Präfixe/Suffixe. Tooltip nur ergänzend. |
| D-17 | Spalten- und Zeilenhinweisbereich sind unabhängig pannbar. | Spaltenfolgen nur vertikal, Zeilenfolgen nur horizontal; Rasterzuordnung, Rasteransicht und Spielzustand bleiben unverändert. |
| D-18 | Lösungshinweise zeigen ausschließlich vollständige einzeilige Zahlen in der Rätselfarbe. | Keine A–D-Suffixe, gestapelten Ziffern, Kompaktkästchen oder Umschaltoption; interne Farb-IDs und Mauspalette bleiben. |
| D-19 | Alle Folgen einer Orientierung verwenden ein gemeinsames regelmäßiges Hinweisraster. | Feste Slotmaße, rasterseitige Ausrichtung, ganze eingerastete Schritte und reservierte Markerslots statt variabler Textpackung. |
| D-20 | Jede konkrete Zeile und Spalte besitzt eine eigene Leseposition. | Achse und Linienindex werden am Gestenstart eingefroren; Nachbarfolgen bleiben unverändert. |
| D-21 | 1920×1080 ist primäre Layoutbasis und gewünschte Start-Clientfläche. | Gesamter Fensterrahmen bleibt im Arbeitsbereich; kleinere Fallbacks, stabile Arbeitszellen und getrennte UI-/Rasterskalierung bleiben. |
| D-22 | F-02 erhält wie F-01 ein eigenständiges verfeinertes Abschlussmotiv. | Leuchtturm, Bildaufbau, Proportionen und Farbverteilung bleiben klar zum Raster zugehörig; Rätsellogik bleibt unverändert. |
| D-23 | Nur die angefasste Hinweisfolge folgt während des Drags kontinuierlich der Maus. | Achse und Linie bleiben fest; beim Drop aus den unmittelbar zuvor sichtbaren Positionen derselben Zahlen die geometrisch nächste gültige ganzzahlige Slotlage wählen und erst dann den semantischen Lesezustand bestätigen. Markerwechsel dürfen keine zusätzliche Zahlenverschiebung erzeugen. Abbruch verwirft den temporären Versatz. |
| D-24 | Füllungen und Vorschau belegen geringfügig mehr Zellfläche. | Der kontrastierende Zwischenraum aus D-08 bleibt an normalen und kräftigen Fünferlinien in allen Farben und Arbeitszoomstufen erhalten. |
| D-25 | Die gültige Cursorzeile und -spalte werden im Raster dezent hervorgehoben. | Schnittpunkt nicht doppelt betonen; Inhalte und Linien bleiben lesbar. Ohne Zellgeste verschwindet das Band beim Verlassen der Rasterfläche. |
| D-26 | X und Preview-X werden an angeschnittenen Zellen geometrisch am Rasterviewport geclippt. | Normale X-Geometrie beibehalten, nicht in den sichtbaren Rest verschieben oder eine teilweise sichtbare Zelle pauschal verwerfen. |
| D-27 | Linke und rechte Zellgesten zeigen einen kleinen Live-Zähler der gesamten aktuellen Strichlänge. | Geometrisches gerades Segment inklusive Start/Ende und übersprungener oder vorbesetzter Zellen; elastisches Zurückziehen aktualisiert sofort. Keine Navigation und kein gespeicherter Zustand. |

D-07 bis D-10 übernehmen die vier Punkte der ersten Nutzer-Mausprobe. D-11 bis D-15
übernehmen den ausdrücklich supersedierenden Sollstand der anschließenden P1.2-Probe.
D-16/D-17 ersetzen die vollständige Ganzfolgen-Ersetzung durch atomare Ausschnitte.
D-18 bis D-22 ersetzen anschließend die optionale A–D-Darstellung, variable
Hinweispackung, gemeinsame Bereichspositionen, den 1600×900-Start und die bloße
F-02-Rasterpräsentation. Soweit ältere D-07-/D-09-/D-14-/D-17- oder
Hinweisformulierungen widersprechen, gelten D-18 bis D-22. D-23 ersetzt ausschließlich
das alte schrittweise Einrasten während des Drags; der bestätigte Zustand bleibt
ein gemeinsamer ganzzahliger Slot.
D-10 präzisiert die bereits im Produkt-/Gestaltungskonzept erlaubte höhere
Detaillierung; es ist keine Freigabe für unabhängige Belohnungsbilder.

2560×1440 bezeichnet die gemeldete Bildschirmauflösung, nicht automatisch logische UI-Pixel oder 100 % Windows-Skalierung. Fehlende Testmetadaten nicht aus Screenshotabmessungen ableiten.

## 3. Ziel, Umfang und Nichtziele

**Untersuchungsfrage:** Kann der Nutzer große klassische und farbige Nonogramme präzise bearbeiten, darin navigieren und später nach Unterbrechung weiterarbeiten, ohne die Orientierung zu verlieren?

### 3.1 Enthalten

- Kleine Album-Testauswahl mit neutraler Kennung, Größe, Rätselart und Bearbeitungsstand. Alle Testfälle direkt zugänglich; keine Freischaltlogik.
- Zellbearbeitung, Farbwahl, Achsenbindung, elastische Vorschau, kontrollierte Rücknahmen sowie Undo/Redo.
- Arbeitsansicht mit unnummerierten, farbigen einzeiligen Hinweisen, atomaren Teilfolgen in einem gemeinsamen Slotraster und eigener Leseposition je Zeile/Spalte, interaktiver eigener Miniatur, Raster-Zoom/Pan und getrennt skalierbarer Oberfläche.
- Mit #11 ein fortsetzbarer lokaler Arbeitsstand je Testfall einschließlich Ansicht und Undo/Redo.
- Tatsächlicher Abschluss und motivtreue, auch detailliertere Darstellung im Album.
- Tests, Start-/Bedien-/Resetanleitung, Windows-Testartefakte und nachvollziehbare manuelle Erprobung.

### 3.2 Nicht enthalten

Keine Sterneberechnung, Perfektionsanzeige, Fehlerstatistik, Rangliste, Freischaltungen, Bonuslogik, Live-Fehlerhilfe oder Hypothesen. Kein allgemeiner Solver, Produktionseditor, Bildimport, Community-Funktion, Audio, aufwendige Buchanimation, finale A/B-Entscheidung, Verbundraster oder Regionenregeln. Kein Hosting, Steam, Release, Installer, Cloudkonto oder kostenpflichtiger Dienst. Keine Tastatur-/Controllerbedienung, globale Tastenumbelegung oder vollständiges Accessibility-Optionsmenü. Der ausdrücklich vereinbarte Escape-Abbruch bleibt Teil des Mausgestenvertrags.

Die spätere Perfektionsregel „ohne Fehler und ohne Undo“ bleibt erhalten. P1 weist mangels Wertung keinen Durchgang als perfekt aus. Ob direktes Neutralisieren oder Radieren später wertungsrelevante Rücknahmen sind, bleibt offen. D-09 entscheidet Bedienung, nicht Fehlerzählung, Sterne oder Perfektion.

### 3.3 Gestaltung und Spoilergrenze

Warmes, ruhiges handgezeichnetes 2D-Album mit klaren Konturen und Farbflächen. Thematik dezent im Arbeitsbildschirm, Raster sachlich und präzise. Keine Buchfalte, Dekoration oder unleserliche Handschrift über Arbeitszellen/Hinweisen. Sammelalbum und Reisealbum bleiben offene Themenalternativen.

Vor Abschluss weder fertiges Motivbild noch Motivname oder verräterischer Albumplatzhalter. Während des Lösens stets eine Miniatur nur des eigenen Zustands einschließlich Fehlern. Mocks sind Stilreferenzen, keine gültigen Rätseldaten oder vorweggenommenen Produktabnahmen.

## 4. Testdaten und Datenvertrag

| Kennung | Testfall | Zweck und Nachweis |
| --- | --- | --- |
| F-01 | 20×20 monochrom | Grundbedienung, Rücknahmeregression und mit #9 sichtbar detailliertere motivtreue Enthüllung. Bestehende logische Lösung und Hinweise beibehalten. |
| F-02 | 40×40 mit vier Farben | Farbwahl, direkt angrenzende verschiedenfarbige Blöcke, lange Hinweise, vollständiger spielbarer Abschluss und verfeinertes motivtreues Leuchtturmbild. |
| F-03 | Vollständig navigierbares 100×100-Stressraster | Großraster und lange Hinweise, kein statisches Ausschnittbild. Sichtbar „UI-Testdatensatz – Rätselqualität nicht abgenommen“. |

F-01/F-02 dürfen einfach sein, benötigen aber ein erkennbares Motiv, geklärte Herkunft und eine endliche überprüfbare Deduktionsfolge ohne zusätzliche Startfelder oder notwendiges Raten. Eine Lösung oder passende Zahlen allein beweisen das nicht. Kein allgemeiner erklärender Solver beauftragt. F-03 erlaubt keine ungeprüften regulären Produkträtsel.

Randfälle: leere Linie, voller Block, gleichfarbige Blöcke mit notwendigem Abstand, direkt angrenzende verschiedenfarbige Blöcke, lange vollständige Hinweisfolge. Für F-02 keinen monochromen Nachweis ungeprüft wiederverwenden. Die Nachweisprüfung darf Linienmöglichkeiten untersuchen, aber keine Rasterannahmen als Deduktion ausgeben.

Definition und Spielerstand getrennt; P1-intern JSON, keine Datenbank. Stabile ID/Revision, Dimensionen, Palette mit stabilen Farbkennungen, Lösungsmatrix, vollständige Zeilen-/Spaltenhinweise sowie erst nach Abschluss sichtbare Motivdaten. Intern nullbasierte Indizes von oben/links; UI einsbasiert.

Zellen: `unbekannt`, `leer`, `gefüllt(Farbkennung)`. Farbindizes unabhängig von Darstellungsfarben. Hinweise aus Lösung reproduzierbar: gleiche Farben benötigen Abstand, verschiedene dürfen direkt angrenzen. Gespeicherte Hinweise gegen Ableitung prüfen. Dimensionen, Matrixform, Wertebereiche, Versionen und Farbverweise validieren; Leerlinie eindeutig darstellen.

**Abschlussressource ab #9:** Auflösung und Detailgrad unabhängig von den Rätseldimensionen. Der Validator prüft Format/Version, vorhandene und gültige Bilddaten beziehungsweise lokale Ressourcen und Zuordnung zur Definition, nicht pixelidentische Belegung zur Lösung. Motivtreue wird durch visuellen Vergleich geprüft. Fehlende/defekte Ressourcen nicht still durch ein fremdes Bild ersetzen. Geändertes Schema, Fixtures, Loader, Tests, Exportfilter und Dokumentation gemeinsam aktualisieren; Revisions-/Zertifikatbezüge von F-01 konsistent halten. Keine Änderung seiner Lösung nur für eine reichere Illustration. Keine Spielstandmigration aus #11 vorwegnehmen.

## 5. Interaktionsvertrag

### 5.1 Werkzeuge, direkte Umwandlung und Strichgrenzen

Beim normalen Werkzeug bestimmt die Maustaste zusammen mit dem **bestätigten Startzellzustand** einmalig den Aktionsmodus:

| Taste / Startzustand | Aktion für den gesamten Strich | Veränderbare Zellen |
| --- | --- | --- |
| Links / unbekannt oder leer markiert | Aktive Farbe setzen | Unbekannte und leer markierte Zellen werden zur aktiven Farbe. Vorhandene Füllungen bleiben geschützt. |
| Links / gefüllt, unabhängig von Farbe | Füllungen neutralisieren | Nur gefüllte Zellen werden unbekannt, auch andere vorhandene Farben. Unbekannte und leere Zellen bleiben unverändert. |
| Rechts / unbekannt oder gefüllt | Leer markieren | Unbekannte und gefüllte Zellen werden zu X. Vorhandene X bleiben geschützt. |
| Rechts / leer markiert | Leermarkierungen neutralisieren | Nur leer markierte Zellen werden unbekannt; Füllungen bleiben geschützt. |

Ein Einzelklick ist ein Strich der Länge eins. Damit gilt direkt: links
`unbekannt → aktive Farbe`, `gefüllt → unbekannt`, `X → aktive Farbe`; rechts
`unbekannt → X`, `X → unbekannt`, `gefüllt → X`. Eine andersfarbige Füllung
wird links weiterhin neutralisiert und nicht direkt umgefärbt. Bei Strichen wandelt
ein linker Setzmodus unbekannte/X-Zellen in die eingefrorene aktive Farbe um, ein
rechter Setzmodus unbekannte/gefüllte Zellen in X. Ein auf einer Füllung gestarteter
linker Rücknahmestrich neutralisiert nur Füllungen; ein auf X gestarteter rechter
Rücknahmestrich neutralisiert nur X.

Der explizite Radierer bleibt als Universalwerkzeug: links setzt alle vorhandenen Markierungen auf unbekannt. Rechts folgt weiterhin der Leer-/Leerrücknahme-Regel. Beim Hand-Werkzeug verschiebt links ausschließlich die Ansicht. Werkzeug, Aktionsmodus und Setzfarbe bleiben bis zum Ende der Geste eingefroren; keine Neuerkennung pro überfahrener Zelle und kein wiederholtes Umschalten beim Rückwärtsziehen.

Die erste eindeutige Bewegung in eine andere Zelle verriegelt horizontal oder vertikal. Bei diagonalem Gleichstand bleibt nur die Startzelle in der Vorschau, bis eine Richtung dominiert. Danach feste Achse bis zum Ende; Eingabesprünge erfassen alle Zwischenzellen.

Die elastische Vorschau wird aus dem bestätigten Zustand am Gestenbeginn und dem aktuellen geraden Abschnitt berechnet. Zurückziehen verkürzt auch Rücknahmestriche; außerhalb des Abschnitts erscheint der unveränderte Ausgangszustand wieder. Überqueren des Starts bleibt auf derselben Achse. Loslassen übernimmt nur wirksame Änderungen atomar. Beispiel 5→12→9 bearbeitet nur 5–9 nach dem eingefrorenen Modus. Keine Abschlussprüfung aus der Vorschau.

Während einer linken oder rechten Zellgeste zeigt ein kleiner Zähler am aktuellen
Strichende, am Viewportrand nach innen versetzt, die geometrische Länge des aktuellen
geraden Abschnitts einschließlich Start und Ende. 5→12 zeigt 8, zurück auf 9 zeigt 5,
ein Einzelfeldabschnitt zeigt 1. Vorbelegungen und Eingabesprünge verkürzen den Zähler
nicht. Nach Übernahme oder Abbruch verschwindet er; Navigation zeigt keinen Zähler.

Escape oder Fokusverlust verwirft vollständig. Außerhalb des sichtbaren Rasterbereichs bleibt der letzte gültige Endpunkt stehen. Kein Zeichnen unter UI-Flächen, kein Auto-Scrollen, kein Zoom/Pan während Zellgesten. Werkzeug-/Farbwechsel wirken frühestens in der nächsten Geste. Reguläres Verlassen verwirft eine laufende Vorschau vor einem späteren Speichern.

Ein wirksamer Strich ist ein Undo-Schritt; Redo stellt exakt wieder her. Neue wirksame Änderung nach Undo verwirft den Redo-Zweig; No-ops nicht. Navigation ist keine Zellaktion. Direktes Neutralisieren wird als normale Bearbeitungsaktion rückgängig machbar, ruft nicht heimlich Undo auf und löscht kein bestehendes Undo-verwendet-Merkmal. Keine Wertungsentscheidung daraus ableiten.

### 5.2 Fenster, Zoom, Hinweise und Miniatur

D-21 präzisiert D-07: 1920×1080 ist die primäre Layoutreferenz und die gewünschte
Clientfläche beim Fensterstart, soweit diese einschließlich des tatsächlichen Rahmens
in den verfügbaren Monitorarbeitsbereich passt. Andernfalls wird die Clientfläche so
begrenzt, dass der ganze Rahmen sichtbar bleibt. Kein Vollbildzwang, Offscreen-Start
oder Eingriff in Windows-Einstellungen. 1280×720 bleibt Mindest-/Fallback-Test,
1600×900 kleinerer Regressionstest und 2560×1440 unterstützte größere Fläche.

Arbeitszoom, UI-/Hinweisskalierung und Fenstergröße sind getrennt. Technischer Ausgangswert: 24 logische Einheiten Zellabstand bei 100 % Arbeitszoom; eine begründete Feinanpassung nach Darstellungstests ist reversibles Implementierungsdetail. Vergrößern/Maximieren des Fensters vergrößert bei gleichem Zoom und UI-Maßstab nicht automatisch die Zellen. Stattdessen mehr Raster zeigen oder kleine Raster mit ruhigen Rändern platzieren. Eine ausdrücklich gewählte Gesamtansicht ist vom Arbeitszoom zu unterscheiden; „Arbeitsgröße“ stellt eine brauchbare Bearbeitungsgröße wieder her.

Mausrad zoomt möglichst ortsstabil am Zeiger. Mittlere Taste oder Hand-Werkzeug
verschieben. Sichtbare Zoomknöpfe, Gesamtansicht und Rückkehr zur Arbeitsgröße.
Die #9-Referenzfolge umfasst 20 streng steigende Zellabstände von 12 bis 72 logischen
Einheiten (`12/14/16/18/20/22/24/26/28/30/32/34/36/40/44/48/54/60/66/72`).
Aus einer Gesamtansicht unterhalb beziehungsweise oberhalb dieser Folge springt eine
gegenläufige Bedienung nicht in die falsche Richtung: ohne kleinere/größere Stufe
bleibt sie stehen, in Gegenrichtung wechselt sie zur nächsten tatsächlich kleineren/
größeren Arbeitsstufe. 100×100 bleibt vollständig navigierbar; Viewportgrenzen,
Hinweise und Hit-Tests verwenden dieselbe Transformation. Bei Resize/Zoom Fokus soweit
geometrisch möglich erhalten und Pan gültig begrenzen. Navigieren verändert keine
Zellen und keine Undo-Historie.

D-08: Füllungen haben zu anderen Füllungen und insbesondere den Fünferlinien einen sichtbar kontrastierenden Zwischenraum. Dunkle Füllung und dunkle Linie dürfen an Kreuzungen nicht zu einer gemeinsamen L-/Blockform verschmelzen. Fünfergruppen bleiben erkennbar; Umrissstärke, Füll-Inset und Renderingreihenfolge gemeinsam abstimmen. Dies gilt für alle vier Farben, Vorschau und die angebotenen Bearbeitungszoomstufen. Eine verdichtete Gesamtansicht ist kein Ersatz für diese Arbeitsansicht. Zeichnung und tatsächliche Trefferflächen bleiben korrekt zugeordnet.

D-24 vergrößert die Füllfläche geringfügig innerhalb dieser Trennungsgrenze. D-25
betont die gültige Cursorzeile und -spalte als dezente Hintergrundbänder nur im
sichtbaren Raster. Die Kreuzung erhält dieselbe Stärke wie jedes Band; Füllungen,
X, Vorschau und Rasterlinien werden darüber gezeichnet. D-26 clippt die normalen
X-Liniensegmente bestätigter und vorläufiger Leermarkierungen am Viewportrand,
auch bei nur teilweise sichtbaren Zellen und Ecken. Wo kein X-Segment den sichtbaren
Rest schneidet, entsteht keine Ersatzmarkierung.

Hinweise beziehen sich stets auf ganze Zeilen/Spalten und sind korrekt zugeordnet,
aber nicht zusätzlich laufend nummeriert. Aktive Linie und die separate Koordinatenanzeige
unterstützen die Orientierung. Sie zeigen nur vollständige einzeilige Zahlen in der
jeweiligen Rätselfarbe; mehrstellige Zahlen bleiben horizontal und ungeteilt. Für P1
gibt es keine A–D-Suffixe, gestapelten Ziffern, Kompaktkästchen oder entsprechende
Umschaltoption. Interne Farb-IDs und die A–D-Beschriftung der vorläufigen Mauspalette
sind davon nicht betroffen.

Alle Zeilenfolgen verwenden dieselben festen horizontalen Hinweisplätze, alle
Spaltenfolgen dieselben festen vertikalen Reihen. Die gemeinsame Slotgeometrie wird
je Orientierung und aktueller Ansicht bestimmt, bleibt von individuellen Zahlenbreiten,
Folgenlängen und Kürzungszuständen unabhängig und ist quer zur Folge exakt der
Rasterzeile/-spalte zugeordnet. Kurze Folgen und `–` stehen rasterseitig rechts
beziehungsweise unten. Bei Überlauf bleibt ein maximal sinnvoller zusammenhängender
Ausschnitt vollständiger Tokens in unveränderter Reihenfolge sichtbar, unter Wahrung
direkter monotoner Draggeometrie und fester Markerplätze. `…` belegt
einen festen Randplatz nur auf tatsächlich verborgenen Seiten. Keine zusätzlichen
sichtbaren Hinweisgitterlinien.

Jede konkrete Zeile und Spalte besitzt eine eigene ganzzahlige bestätigte Leseposition.
Mittlere Taste oder Linkszug mit Hand-Werkzeug frieren Achse und Linienindex am
Gestenstart ein. Während des Drags bewegt sich nur die angefasste Folge kontinuierlich
entlang ihrer Achse, auch zwischen Slots; beim Loslassen rastet sie auf die nächste
gültige ganzzahlige Position ein. Escape, Fokusverlust oder regulärer Übergang
verwerfen den temporären Versatz und erhalten die letzte bestätigte Position.
Die Eigentümerentscheidung Variante A zu #11/R7 priorisiert den geometrisch nächsten
Snap und direkte monotone Manipulation. Der geometrische Außenanschlag ist selbst
`outer_start`; dort darf ein physisch möglicher Tokenplatz frei bleiben, wenn seine
Belegung die Zahlen entgegen der bisherigen Dragrichtung verschieben würde.
Es gibt keinen zusätzlichen, nur durch Gegenbewegung erreichbaren Randzustand.
Wiederholtes Ziehen mit gleichem Vorzeichen führt vom Rasterende bis zum äußeren
Anfang; der Rückweg verwendet durchgehend das Gegenzeichen. Die Darstellung wird
bereits während des Drags an diesen geometrischen Grenzen begrenzt. Alle Tokens
müssen über die erreichbare Zustandsfolge vollständig lesbar bleiben.
Überfahren benachbarter Linien, des
Rasters oder anderer UI übernimmt keine andere Folge und wird weder Raster-Pan noch
Zellbearbeitung. Leere/kurze Folgen pannen nicht in leeren Raum. Anfang, Mitte und Ende
jeder langen Folge bleiben erreichbar; „Hinweise rasterseitig ausrichten“ setzt alle
Einzelpositionen bewusst zurück.

Raster-Pan und Miniaturnavigation erhalten sämtliche individuellen Lesepositionen.
Zoom, Resize und UI-Skalierung bewahren denselben gelesenen Bereich soweit möglich,
begrenzen danach gültig und bleiben auf dem gemeinsamen Slotraster. Beim bewussten
Testblattwechsel wird ab P1.3 die individuelle Hinweisansicht des Zielblatts
wiederhergestellt; nur dessen bestätigter Reset initialisiert sie neu.

Während einer Zellgeste ist Hinweisnavigation gesperrt. Freigabe, Escape und
Fokusverlust beenden sie; falsche Tastenfreigabe nicht. Hinweis-Panning verändert
weder Zellen/Preview, History/Undo-Metadatum oder Abschluss noch Rasterzentrum,
Rasterzoom oder Miniaturrahmen. Darüberfahren einer gekürzten Folge zeigt weiterhin
die vollständige farbige Folge als umbrechenden Tooltip im Arbeitsbild. Dieser ist
Ergänzung, nicht der einzige Zugriff; es gibt keinen eigenen Hinweisbildschirm oder
modalen Ersatzdialog. Keine automatische Fehler-/Erfüllungsmarkierung durch
Lösungsvergleich. Hinweisabhaken ist nicht erforderlich.

Die stets sichtbare Miniatur enthält nur Spielerzustand und gegebenenfalls dieselbe
Vorschau, keine korrigierte Lösung. Unbekannt/leer/gefüllt unterscheidbar; richtige
Rätselfarben darstellen. Ein Ausschnittrahmen zeigt den Viewport. Klick/Ziehen navigiert
ohne Zellmutation. Vier Farben über die vorläufige Mauspalette mit stabilen internen
Farb-IDs und A–D-Beschriftung; dies ist keine Zusatzkennung an Lösungshinweisen.
Auswahl/Fokus/Leerzustand dürfen keine zusätzliche Rätselfarbe vortäuschen. Keine
beliebigen Nutzerpaletten und kein vorgezogener Neuentwurf der Farbauswahl.

Layouttests umfassen 1280×720, 1600×900, die primäre 1920×1080-Fläche und 2560×1440
als logische Testflächen. Reale Windows-Bildschirmauflösung, Fenster-/Clientfläche,
Rahmen und Anzeigeskalierung zusätzlich getrennt protokollieren; logische Tests sind
kein Nachweis physischer DPI-Verhältnisse. Keine versteckten Werkzeuge/Hinweise; unter
der Mindestfläche klare Meldung statt beschädigtem Layout.

### 5.3 Alternative Eingaben außerhalb P1

D-06 stellt Tastatur-/Controllerbedienung für P1 zurück. Kein Controllergerät/-Tester und keine entsprechende Abnahme erforderlich. [Issue #10](https://github.com/venomenon328/picross/issues/10) ist für P1 entfallen. Produktweite alternative Eingaben bleiben davon unberührt. Escape ist weiterhin der vereinbarte optionale Abbruchweg einer Mausgeste.

### 5.4 Abschluss und detaillierteres Ergebnisbild

Nach einer übernommenen Aktion gilt das Rätsel genau dann als gelöst, wenn jede Motivzelle in der richtigen Farbe gefüllt ist und jeder Lösungshintergrund unbekannt oder leer markiert ist. Zusatzfüllung, fehlende Füllung, falsche Farbe oder leer markierte Motivzelle verhindern den Abschluss. Keine Fehlermeldung, Prozent-richtig-Anzeige oder korrigierte Miniatur vor dem vollständigen Treffer.

Danach Abschlussansicht „Prototyp ohne Wertung“, Motivname und fertiger Albumeintrag. D-10: Das Ergebnisbild darf höhere Auflösung, feinere Konturen, zusätzliche Oberflächendetails, Schattierungen und kleine passende Motivelemente besitzen. Das Rätsel muss sehr deutlich als Stilisierung dieses Bilds erkennbar bleiben: gleicher Hauptgegenstand, nachvollziehbarer Bildaufbau, wesentliche Formen und Proportionen. Keine unabhängige Belohnungsillustration, aber auch keine Pflicht zu identischen belegten Rasterzellen.

#9 demonstriert diese Richtung an den eigenständigen Ergebnisbildern von F-01 und F-02.
Das positiv bestätigte F-01-Segelboot bleibt die Stil-/Abstraktionsreferenz. F-02 zeigt
denselben Leuchtturmaufbau wie das Raster – Sonne oben links, Turm rechts, Wasser unten
und dieselbe dominante Farbverteilung – mit feineren Architekturkonturen, Laterne,
Turmbändern, Oberflächen- und Wasserdetails. Bloßes Hochskalieren/Umfärben desselben
Pixelbilds genügt für keines der beiden Motive. Lösungen, Hinweise und die 48/80
Deduktionsschritte bleiben logisch unverändert. Eine allgemeine Assetpipeline oder
Pflicht-Neuzeichnung aller späteren Rätsel folgt daraus nicht. F-03 ist auch nach
Solltreffer ausdrücklich technischer Test, kein kuratiertes Rätsel.

## 6. Speicherung und Wiederaufnahme

P1.3 verwendet ausschließlich `user://p1/saves/` mit aus den drei bekannten Fixture-IDs gebildeten Dateinamen. Schema 1 speichert je Blatt Definitions-ID und -Revision, Dimensionen, bestätigte flache Zellmatrix, vollständige wirksame History samt Redo-Zweig/Cursor und bleibendem `undo_used`, Abschlussstatus, Rasterfokus in Zellkoordinaten, gültigen Arbeitszoom oder Gesamtansichtsmodus, aktive Farbe/Werkzeug sowie individuelle semantische `row_clue_reads` und `column_clue_reads`. Nicht gespeichert werden laufende Gesten, Lösung/Reveal, Wertung, Fehlerstatistik, UI-Skalierung, Fenstergeometrie, Miniaturrahmen oder konkrete Hinweis-Slot-Offets.

Vor Anwendung werden Schema, exakte Definition/Revision, Matrix/Palette, jede nichtleere atomare History-Aktion mit eindeutigen Indizes und gültigen Vor-/Nachwerten, das widerspruchsfreie Replay ab unbekanntem Raster einschließlich Redo, Cursor-Matrix-Gleichheit, `undo_used`, Abschluss und View vollständig geprüft. Unbekannte oder unpassende Daten werden weder teilweise geladen noch still migriert. Der Rasterfokus wird bei Resize gültig begrenzt; Hinweis-Offsets werden aus Rasterende, äußerem Anfang oder mittlerem Tokenfenster für die aktuelle Geometrie neu abgeleitet.

Jede wirksame bestätigte Zellaktion und Undo/Redo werden sofort gesichert; Werkzeug/Farbe ebenfalls. Reine Ansicht darf kurz gebündelt werden, wird aber vor Album, Blattwechsel, Beenden und regulärer Window-Close-Anforderung geflusht. Vorschau wird zuerst verworfen. Fehler erscheinen sichtbar und dürfen keinen gesicherten Stand vortäuschen.

Schreiben erfolgt als vollständige Tempfassung im selben Speicherroot mit Flush, Schließen und erneuter Parse-/Vertragsvalidierung. Nur ein gültiges bisheriges Primary wird als genau eine gültige Backupfassung rotiert; erst danach ersetzt der Kandidat das Primary. Ein Abbruch lässt wenigstens die vorherige gültige Fassung ladbar. Ein verwaistes Tempfile wird nicht geladen. Gültiges Primary hat Vorrang; bei fehlendem/defektem Primary wird ein gültiges Backup sichtbar geladen. Defekte oder inkompatible Fassungen werden nicht still überschrieben; das bewusste Übernehmen eines gültigen Backups erlaubt wieder Speichern. Bei gültigem Primary und defektem Backup wird der Primärstand geladen; eine bestätigte Backup-Erneuerung erlaubt wieder Speichern. Ohne gültige Fassung erscheint ein Fehlerzustand. Der bestätigte Reset entfernt ausschließlich Primary, Backup und Temp des ausgewählten Blatts und setzt nur dessen Session zurück.

Tests verwenden ausschließlich eigene temporäre User-Daten; ein echter Zwei-Prozess-Roundtrip gehört zum Produktweg. Dies ist keine Produktmigration oder Zusicherung zukünftiger Save-Kompatibilität. Ein fehlgeschlagener Pflicht-Flush blockiert Album, Blattwechsel, Beenden und Window-Close bis zu einem erfolgreichen Retry. Ein aus gültigem Backup geladener Stand bleibt auch bei fehlendem Primary bis zur bewussten Übernahme schreibgesperrt. Temporäre Hintdrag-Subslots, Hoverbänder und Strichzähler gehören nicht zum Save.
Im Album zeigt jedes ungelöste Blatt ausschließlich seine eigene gespeicherte
Spielerminiatur unter neutralem Blattnamen; nur ein valider abgeschlossener Slot
zeigt die bisherige Motiv-/Abschlussdarstellung.

## 7. Technikbindung und Prüfweg

### 7.1 P1-Technik

Godot Standard **4.7.2-stable** mit typisiertem GDScript, passenden Standard-Exportvorlagen und Windows-x86_64-Testexport. Kein .NET-SDK oder Runtime-Backend. Primärquelle: [offizieller Release](https://github.com/godotengine/godot-builds/releases/tag/4.7.2-stable). Der gebundene Editor-/Template-/Hash-/CI-Weg ist durch [P1.0](P1_PREFLIGHT.md) nachgewiesen. Kein ungeprüfter Wechsel zu `latest`; Archive vor Verwendung prüfen, nicht einchecken oder global installieren.

Projektpfad `prototypes/p1/`. Eigene Rasterzeichen-/Hit-Test-Komponente, UI-Bausteine für Menüs/Palette/Fokus. Raster-/Aktionsmodell, Ansichtskoordinaten und später Speicherung getrennt testbar. Keine Abstraktionsplattform für hypothetische Engines oder unnötigen Drittanbieterabhängigkeiten. Deutsche UI, keine vollständige Lokalisierungsinfrastruktur.

### 7.2 Ausführbarer Befehlsvertrag

Die folgenden Bestandteile existieren aus #8; #9 erweitert deren tatsächlichen Prüfumfang. `godot` bezeichnet den gebundenen Standard-Editor, unter Windows dessen Konsolenprogramm. Vollständig isolierter Prüfweg in der [Anleitung](../prototypes/p1/README.md).

```sh
godot --version
godot --headless --path prototypes/p1 --import
godot --headless --path prototypes/p1 --script res://tests/run_tests.gd
godot --path prototypes/p1
godot --headless --path prototypes/p1 --export-debug "P1 Windows x86_64" build/windows/picross-p1.exe
```

Der Testrunner führt vereinbarte Logikprüfungen aus, gibt Anzahl/Ergebnis aus und endet bei Fehler mit Fehlerstatus. Import-, Start- und Exportfehler sind Fehlschläge. Begrenzte Laufzeiten; isolierter Speicher bei Tests/Smoke. Technischen Start-Smoke und reale GUI-Erprobung trennen.

Exportpreset exakt `P1 Windows x86_64`; vorher passende Templates und `prototypes/p1/build/windows/` anlegen. Exportpfad relativ zum Godot-Projekt. ZIP mit allen Startdateien, Anleitung und Commitkennung; keine Godot-Installation beim Nutzer voraussetzen. Keine Signaturzertifikate, Releases oder Änderung von Windows-Schutzfunktionen beauftragt.

`tools/p1_product.py` und [Produkt-CI](../.github/workflows/p1-product.yml) liefern Import, Godot-Tests, absichtlichen Negativtest, kontrollierten Start und Windows-Export; unter Windows zusätzlich exportierten Start. #9 aktualisiert Fixture-/Ressourcenprüfung und Nachweise mit der Implementierung. Bestehende Dokument-/Preflight-CI bleibt zusätzlich bestehen. Aktuelle Head-/Basis-/Test-Merge-/Artefaktzuordnung im PR; alte grüne Prüfungen belegen nicht die neuen Funktionen.

## 8. Akzeptanz und Abnahme

### 8.1 Automatisiert durch Implementierer / CI

| ID | Prüffall und Erfolg |
| --- | --- |
| A-01 | Definitionen/Hinweise einschließlich Farben, Leerlinien und ungültiger Daten validieren; F-01/F-02 mit Deduktionsfolge, F-03 als Stressfixture. Abschlussressourcen technisch unabhängig von Rasterauflösung prüfen. |
| A-02 | Setz-/Neutralisierungs-/Radiergesten: direkte Füllung↔X-Umwandlung, Achsenbindung, diagonaler Start, Sprünge, elastisches Zurückziehen, gemischte Vorbelegung, Rand/UI, Abbruch und No-op. Nur zum eingefrorenen Modus passende Zellen ändern sich. |
| A-03 | Atomarer Strich, exakte Vorzustände bei Undo/Redo, korrekte Verzweigung; Neutralisieren nicht als versteckten Undo-Aufruf behandeln. |
| A-04 | Gemeinsame Ansichts-/Hit-Test-/Miniaturtransformation bei Zoom, Raster-Pan, UI-Skalierung und Resize; echte Mauspfade bewegen nur die konkret gestartete Zeile/Spalte kontinuierlich und rasten beim Drop in gemeinsame Slots ein, einschließlich Abbruch/Grenzen. Navigation mutiert keine Zellen. Zellgröße bleibt bei reinem Resize im Arbeitszoom stabil. |
| A-05 | Mit #11 Speicherung/Recovery ohne stillen Datenverlust oder fremden Zugriff. |
| A-06 | Unkorrigierte eigene Miniatur, keine frühen Motivdaten, richtiger Abschluss mit unbekanntem Hintergrund, kein Abschluss bei Zusatz-/Fehl-/Falschfüllung oder leerer Motivzelle. Detailliertere Ressourcen ändern die Abschlusslogik nicht. |
| A-07 | Import, begrenzter Start/Exit und Windows-Export; vollständige Artefakte/Logs einem konkreten Stand zugeordnet. |

Bestehende Dokumentprüfung zusätzlich: `python3 -m unittest discover -s tools -p 'test_*.py' -v`, `python3 tools/check_docs.py`, vollständiger `git diff --check`. Headless-Prüfungen sind kein Beleg für Lesbarkeit, echte Maussignale oder Windows-Grafikverhalten. Zeichnungs-/Layoutregressionen auch mit tatsächlichen Renderbildern prüfen.

### 8.2 Manuelle Prüfungen am gelieferten Commit/Artefakt

| ID | Szenario | Zuständigkeit |
| --- | --- | --- |
| M-01 | F-01 per Maus setzen/neutralisieren, X↔Füllung direkt umwandeln, zurückziehen, Rücknahmetyp schützen, Radierer/Undo/Redo und Abschluss ohne Auskreuzpflicht. Neuer F-01-Reveal sichtbar detaillierter und eindeutig zugehörig. | Eigentümer |
| M-02 | F-02 mit vier Farben und langen Hinweisen; einzeilige farbige Zahlen ohne Zusatzkennung, gemeinsames Slotraster, mehrere Einzelketten unabhängig pannen, ergänzender Tooltip, Farbwahl, Zelltrennung, direkte Umwandlung und verfeinertes Leuchtturmmotiv klar bedienbar. | Eigentümer |
| M-03 | F-03-Koordinate bearbeiten, bei kleinen Arbeitsstufen echte Hinweiszahlen lesen, mehrere konkrete Zeilen/Spalten unabhängig pannen, Raster stark zoomen/verschieben und über Miniatur/Koordinaten wiederfinden. | Eigentümer |
| M-04 | Mit #11 Teilstand schließen, neu starten und samt Historie/Ansicht fortsetzen. | Eigentümer |
| M-05 | Durch D-06 nicht anwendbar: Tastatur/Controller außerhalb P1. | Kein P1-Gate |
| M-06 | 1080p-Startziel beziehungsweise arbeitsbereichbegrenzter Fallback, 1080p/1440p und logische Referenzflächen; tatsächliche Skalierung erfassen. Keine verdeckten Elemente, aufgezwungenen Riesenraster oder verschmolzenen Füll-/Fünferlinien. | Eigentümer |
| M-07 | 100×100 auf der Referenzhardware: keine verlorenen/falschen Aktionen oder wahrnehmbaren Hänger. Im integrierten Paket 500 reproduzierbare Zell-/Navigationsaktionen gegen Sollzustand; Messung und Beobachtung getrennt. | Implementierer / Eigentümer |

Protokoll: tatsächliche Commit-/Artefaktkennung, Betriebssystem, verwendete Eingaben, Fenster-/Bildschirmgröße, reale Skalierung, Szenario und Ergebnis. Hardware-/Skalierungswerte nicht erfinden und keine pauschale FPS-Zusage aus der Referenz ableiten.

### 8.3 Gate-Zeitpunkte und bisherige Mausprobe

Vor Gesamt-P1-Merge A-01 bis A-07, Dokumentprüfung und M-01 bis M-04, M-06/M-07 nachweisen. #8/#9 sind über PR #14 integriert; #11 liegt auf einem neuen Draft-PR gegen `main`, #12 bleibt getrennt. Kein Zwischenstand erteilt eine vorgezogene Merge- oder Eigentümerfreigabe für #11.

K-06: Der Nutzer hat die angebotene F-01-Spielprobe verwendet und anschließend zwei Screenshots sowie vier konkrete Rückmeldungen geliefert; der Abschlussbildschirm ist sichtbar. Bezug der Unterhaltung ist Artefakt `10719712143` / Implementierungshead `64dcca4df9ed00cecedfdb8cabba09bcb7179ae8`. Eine separate Versionsanzeige des Nutzerlaufs, tatsächliche Windows-Skalierung und vollständige Einzelbestätigung aller K-06-Szenarien liegen nicht vor.

Die Probe ist **durchgeführt mit Änderungsbedarf**, nicht pauschal bestanden. Der Nutzer beauftragt auf Basis dieses Feedbacks ausdrücklich die Vorbereitung von #9. Die frühe Feedbackschleife blockiert diesen Folgeschritt daher nicht; ihre Änderungen werden in #9 bearbeitet. Fehlende Metadaten/Einzelnachweise bleiben offen und werden mit der erneuten Maus-/Layoutprobe des neuen Artefakts erfasst. Keine vollständige M-01/M-06-/Produktabnahme aus den Screenshots ableiten. Technische Tests ersetzen diese nicht.

## 9. Aktueller Lieferstand

#9 ist als P1.2-Zwischenstand in `main` integriert. #11 ergänzt P1.3 auf eigenem
Branch/Draft-PR; tatsächliche technische Nachweise stehen im P1.3-Prüfbericht und PR.
M-04 bleibt bis zur realen Eigentümerprobe am commitgebundenen Windows-Artefakt offen.
#12, endgültige Themenwahl, Wertung und Releasefähigkeit bleiben außerhalb dieses
Schritts. Rätselproduktion/Solver und Verbundraster bleiben getrennte Risikostränge.
