# P1: Großraster- und Bedienprototyp

Stand: 23.09.2026 · Spezifikation 0.6 · Fachvertrag D-16/D-17 umgesetzt; Eigentümerabnahme offen

## 1. Geltung, Auftrag und Quellen

Paketquelle ist [Issue #5](https://github.com/venomenon328/picross/issues/5). Hier stehen die versionierten P1-Verträge; das Issue führt Auftrag, aktuellen Ausführungsstand, offene Prüfungen und spätere Entscheidungen. Änderungen an diesen Verträgen sind in Datei und Issue-Verweis konsistent nachzuführen, nicht in einer zweiten parallelen Vollspezifikation.

Maßgebliche Grundlagen sind [Produktdefinition](PRODUCT_DEFINITION.md), [Gestaltungskonzept](DESIGN_CONCEPT.md), [Projektprofil](PROJECT_PROFILE.md) und [lokaler Workflow](dev-rules/WORKFLOW.md); Einstieg bleibt [AGENTS.md](../AGENTS.md). Vor Ausführung die aktuellen Quellen und Issue-Kommentare prüfen.

Die Spezifikationspflege 0.2 wurde über PR #6 gemergt, der technische P1.0-Preflight über PR #13. [P1.1 / Issue #8](https://github.com/venomenon328/picross/issues/8) liegt auf `feat/5-p1-prototype` in Draft-PR #14 vor: Implementierungshead `64dcca4df9ed00cecedfdb8cabba09bcb7179ae8`, Zielbasis `main@7f5f945edecdad0c5b86ecbe66ab3d81c7bfedac`. Die anschließende Eigentümerprobe ergab vier Folgepunkte. Die anschließende Vorbereitung hat diese in den Vertrag übernommen; der neue Implementierungsauftrag liefert #9 auf demselben Branch/PR, ohne Merge.

**Ist/Soll:** D-07 bis D-17 sind mit #9 umgesetzt; technische Nachweise und verbleibende
Abnahmen stehen im [P1.2-Prüfbericht](P1_2_VERIFICATION.md) und PR #14. Die früheren
P1.1-Prüfungen bleiben historische Nachweise ihres damaligen Vertrags, keine
Eigentümerabnahme des neuen Verhaltens.

**Paketgrenze:** Diese Spezifikation beschreibt den gesamten P1-Vertrag. #8 liefert F-01, Mausstriche, eigene Miniatur, Undo/Redo und Abschluss. #9 übernimmt das Mausproben-Feedback und ergänzt F-02/F-03, Farben, Zoom/Pan und interaktive Miniaturnavigation. Dauerhafte Speicherung folgt mit #11, integrierte Prüfung mit #12. Diese späteren Verträge sind keine Behauptung bereits implementierter Funktionen. Aktuelle [Anleitung](../prototypes/p1/README.md) und [P1.2-Prüfbericht](P1_2_VERIFICATION.md); historischer [P1.1-Prüfbericht](P1_1_VERIFICATION.md).

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
| D-16 | Überlauf kürzt auf Ebene vollständiger einzelner Hinweise. | Ein möglichst großer zusammenhängender Ausschnitt bleibt sichtbar; `…` markiert ausschließlich verborgene Präfixe/Suffixe. Tooltip nur ergänzend. |
| D-17 | Spalten- und Zeilenhinweisbereich sind unabhängig pannbar. | Spaltenfolgen nur vertikal, Zeilenfolgen nur horizontal; Rasterzuordnung, Rasteransicht und Spielzustand bleiben unverändert. |

D-07 bis D-10 übernehmen die vier Punkte der ersten Nutzer-Mausprobe. D-11 bis D-15
übernehmen den ausdrücklich supersedierenden Sollstand der anschließenden P1.2-Probe.
D-16/D-17 ersetzen für diese Folgearbeit die vollständige Ganzfolgen-Ersetzung durch
einen Marker. Soweit ältere D-09-/Hinweisformulierungen widersprechen, gelten D-11 bis
D-17.
D-10 präzisiert die bereits im Produkt-/Gestaltungskonzept erlaubte höhere
Detaillierung; es ist keine Freigabe für unabhängige Belohnungsbilder.

2560×1440 bezeichnet die gemeldete Bildschirmauflösung, nicht automatisch logische UI-Pixel oder 100 % Windows-Skalierung. Fehlende Testmetadaten nicht aus Screenshotabmessungen ableiten.

## 3. Ziel, Umfang und Nichtziele

**Untersuchungsfrage:** Kann der Nutzer große klassische und farbige Nonogramme präzise bearbeiten, darin navigieren und später nach Unterbrechung weiterarbeiten, ohne die Orientierung zu verlieren?

### 3.1 Enthalten

- Kleine Album-Testauswahl mit neutraler Kennung, Größe, Rätselart und Bearbeitungsstand. Alle Testfälle direkt zugänglich; keine Freischaltlogik.
- Zellbearbeitung, Farbwahl, Achsenbindung, elastische Vorschau, kontrollierte Rücknahmen sowie Undo/Redo.
- Arbeitsansicht mit unnummerierten, farbigen zugeordneten Hinweisen, atomaren Teilfolgen und zwei eigenständig pannbaren Hinweisbereichen, interaktiver eigener Miniatur, Raster-Zoom/Pan und getrennt skalierbarer Oberfläche.
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
| F-02 | 40×40 mit vier Farben | Farbwahl, direkt angrenzende verschiedenfarbige Blöcke, lange Hinweise und vollständiger spielbarer Abschluss. |
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

Escape oder Fokusverlust verwirft vollständig. Außerhalb des sichtbaren Rasterbereichs bleibt der letzte gültige Endpunkt stehen. Kein Zeichnen unter UI-Flächen, kein Auto-Scrollen, kein Zoom/Pan während Zellgesten. Werkzeug-/Farbwechsel wirken frühestens in der nächsten Geste. Reguläres Verlassen verwirft eine laufende Vorschau vor einem späteren Speichern.

Ein wirksamer Strich ist ein Undo-Schritt; Redo stellt exakt wieder her. Neue wirksame Änderung nach Undo verwirft den Redo-Zweig; No-ops nicht. Navigation ist keine Zellaktion. Direktes Neutralisieren wird als normale Bearbeitungsaktion rückgängig machbar, ruft nicht heimlich Undo auf und löscht kein bestehendes Undo-verwendet-Merkmal. Keine Wertungsentscheidung daraus ableiten.

### 5.2 Fenster, Zoom, Hinweise und Miniatur

D-07: Größerer Fensterstart und echte Nutzung von 1920×1080/2560×1440 ohne Zwang zu übergroßen Zellen. Technischer Ausgangswert für #9: 1600×900 logische Fensterfläche, soweit der tatsächlich verfügbare Monitorarbeitsbereich einschließlich Rahmen/Skalierung dies erlaubt; andernfalls passend begrenzen. 1280×720 bleibt logischer Mindest-/Fallback-Test, nicht das unveränderliche Wunschstandardfenster. Kein abgeschnittenes/offscreen geöffnetes Fenster.

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

Hinweise beziehen sich stets auf ganze Zeilen/Spalten und sind korrekt zugeordnet,
aber nicht zusätzlich laufend nummeriert. Aktive Linie und die separate Koordinatenanzeige
unterstützen die Orientierung. Jede regulär passende Folge steht vollständig direkt
am Raster. Bei Überlauf bleibt pro Linie ein möglichst großer zusammenhängender
Ausschnitt vollständiger Hinweise in unveränderter Reihenfolge sichtbar. Zahl, Farbe
und optionale A–D-Kennung bilden eine unteilbare Einheit; mehrstellige Zahlen werden
nicht angeschnitten. Standardmäßig bleibt das rasternahe Ende sichtbar: unten bei
Spalten, rechts bei Zeilen. `…` steht nur an tatsächlich verborgenen Seiten, also
oben/links für ein verborgenes Präfix und unten/rechts für ein verborgenes Suffix;
ein mittlerer Ausschnitt darf beide Marker tragen. Leere Folgen bleiben `–`, kurze
Nachbarfolgen vollständig.

Der Spaltenhinweisbereich lässt sich unabhängig vertikal entlang der Folgen, der
Zeilenhinweisbereich unabhängig horizontal verschieben. Mittlere Taste und Linkszug
mit Hand-Werkzeug wählen Ziel und Achse am Gestenstart; ein Grenzübertritt wird weder
Raster-Pan noch Zellbearbeitung. Die X-Zuordnung der Spalten und Y-Zuordnung der Zeilen
bleibt unverändert. Kurze Folgen werden pro Linie begrenzt und nicht mit einer langen
Nachbarfolge aus dem Bereich geschoben. Scrollgrenzen verhindern leeren Raum;
„Hinweise rasterseitig ausrichten“ stellt beide Standardausschnitte wieder her.
Raster-Pan behält die Leseposition. Zoom, Resize, UI-Skalierung und A–D-Umschaltung
berechnen Fenster/Marker neu und erhalten die normierte Leseposition soweit möglich.
Beim Testblattwechsel werden beide Hinweisansichten neu initialisiert.

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
ohne Zellmutation. Vier Farben über Mauspalette mit stabilen Symbol-/Buchstabenkennungen;
Hinweiszahlen verwenden standardmäßig allein die zugehörige Rätselfarbe. Eine sichtbare
Option ergänzt die A–D-Suffixe in den Hinweisen. Auswahl/Fokus/Leerzustand dürfen keine
zusätzliche Rätselfarbe vortäuschen. Keine beliebigen Nutzerpaletten.

Layouttests umfassen 1280×720, den gewählten größeren Start sowie 1920×1080 und 2560×1440 als logische Testflächen. Reale Windows-Bildschirmauflösung, Fenster-/Clientfläche und Anzeigeskalierung zusätzlich getrennt protokollieren; logische Tests sind kein Nachweis physischer DPI-Verhältnisse. Keine versteckten Werkzeuge/Hinweise; unter der Mindestfläche klare Meldung statt beschädigtem Layout.

### 5.3 Alternative Eingaben außerhalb P1

D-06 stellt Tastatur-/Controllerbedienung für P1 zurück. Kein Controllergerät/-Tester und keine entsprechende Abnahme erforderlich. [Issue #10](https://github.com/venomenon328/picross/issues/10) ist für P1 entfallen. Produktweite alternative Eingaben bleiben davon unberührt. Escape ist weiterhin der vereinbarte optionale Abbruchweg einer Mausgeste.

### 5.4 Abschluss und detaillierteres Ergebnisbild

Nach einer übernommenen Aktion gilt das Rätsel genau dann als gelöst, wenn jede Motivzelle in der richtigen Farbe gefüllt ist und jeder Lösungshintergrund unbekannt oder leer markiert ist. Zusatzfüllung, fehlende Füllung, falsche Farbe oder leer markierte Motivzelle verhindern den Abschluss. Keine Fehlermeldung, Prozent-richtig-Anzeige oder korrigierte Miniatur vor dem vollständigen Treffer.

Danach Abschlussansicht „Prototyp ohne Wertung“, Motivname und fertiger Albumeintrag. D-10: Das Ergebnisbild darf höhere Auflösung, feinere Konturen, zusätzliche Oberflächendetails, Schattierungen und kleine passende Motivelemente besitzen. Das Rätsel muss sehr deutlich als Stilisierung dieses Bilds erkennbar bleiben: gleicher Hauptgegenstand, nachvollziehbarer Bildaufbau, wesentliche Formen und Proportionen. Keine unabhängige Belohnungsillustration, aber auch keine Pflicht zu identischen belegten Rasterzellen.

#9 demonstriert diese Richtung bereits am F-01-Ergebnisbild. F-01s Rätsel, Hinweise und Deduktionsnachweis bleiben logisch unverändert; bloßes Hochskalieren/Umfärben desselben Pixelbilds genügt nicht als Detaillierungsnachweis. Eine für alle Rätsel verpflichtende hochaufgelöste Neuzeichnung oder neue Assetpipeline wird daraus nicht abgeleitet. F-02 bleibt bereits als Farbraster erkennbar. F-03 ist auch nach Solltreffer ausdrücklich technischer Test, kein kuratiertes Rätsel.

## 6. Speicherung und Wiederaufnahme

Mit #11: isolierter P1-Speicherbereich, keine fremden Spielstände, Cloudkonten oder Repositorydateien. Pro Puzzle Definitions-ID/Revision, Zellmatrix, wirksame Undo-/Redo-Aktionen, Undo-verwendet-Merkmal ohne Perfektionsaussage, Zoom/Ausschnitt, aktive Farbe/Werkzeug, Rasterfokus und Abschlussstatus. Keine Hypothesenfelder. Redo oder Fortsetzen löschen das Undo-Merkmal nicht. Keine vollständige Fehlerhistorie oder Zusicherung späterer Produktkompatibilität.

Nach bestätigten Zellaktionen und beim Verlassen sichern. Ansichtsänderungen dürfen zusammengefasst werden, müssen vor regulärem Schließen enthalten sein. Keine halben Striche speichern; Schreibfehler sichtbar machen, nicht fälschlich „gespeichert“ anzeigen.

Neue Fassung vollständig schreiben und validieren, dann gültigen Stand ersetzen; vorige gültige Fassung erhalten. Unterbrochene Schreibvorgänge, defekte/unbekannt versionierte oder inkompatible Daten ohne stilles Überschreiben behandeln. Erklärung und bewussten Neustart nur des ausgewählten Teststands mit Bestätigung anbieten. Keine spätere Wertungsregel daraus ableiten.

Bei geänderter Fenstergröße Rasterfokus erhalten und Ausschnitt gültig begrenzen. Tests ausschließlich mit eigenen temporären Daten. #9 darf vorhandene Spielstände innerhalb derselben Sitzung erhalten, implementiert aber noch keine dauerhafte Speicherung.

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
| A-04 | Gemeinsame Ansichts-/Hit-Test-/Miniaturtransformation bei Zoom, Raster-Pan, UI-Skalierung und Resize; getrennte echte Mauspfade für beide Hinweisbereiche einschließlich Abbruch/Grenzen. Navigation mutiert keine Zellen. Zellgröße bleibt bei reinem Resize im Arbeitszoom stabil. |
| A-05 | Mit #11 Speicherung/Recovery ohne stillen Datenverlust oder fremden Zugriff. |
| A-06 | Unkorrigierte eigene Miniatur, keine frühen Motivdaten, richtiger Abschluss mit unbekanntem Hintergrund, kein Abschluss bei Zusatz-/Fehl-/Falschfüllung oder leerer Motivzelle. Detailliertere Ressourcen ändern die Abschlusslogik nicht. |
| A-07 | Import, begrenzter Start/Exit und Windows-Export; vollständige Artefakte/Logs einem konkreten Stand zugeordnet. |

Bestehende Dokumentprüfung zusätzlich: `python3 -m unittest discover -s tools -p 'test_*.py' -v`, `python3 tools/check_docs.py`, vollständiger `git diff --check`. Headless-Prüfungen sind kein Beleg für Lesbarkeit, echte Maussignale oder Windows-Grafikverhalten. Zeichnungs-/Layoutregressionen auch mit tatsächlichen Renderbildern prüfen.

### 8.2 Manuelle Prüfungen am gelieferten Commit/Artefakt

| ID | Szenario | Zuständigkeit |
| --- | --- | --- |
| M-01 | F-01 per Maus setzen/neutralisieren, X↔Füllung direkt umwandeln, zurückziehen, Rücknahmetyp schützen, Radierer/Undo/Redo und Abschluss ohne Auskreuzpflicht. Neuer F-01-Reveal sichtbar detaillierter und eindeutig zugehörig. | Eigentümer |
| M-02 | F-02 mit vier Farben und langen Hinweisen; atomare Teilfolgen, farbige Zahlen ohne Nummerierung, optionale A–D-Kennung, beide Hinweis-Panachsen, ergänzender Tooltip, Farbwahl, Zelltrennung und direkte Umwandlung klar bedienbar. | Eigentümer |
| M-03 | F-03-Koordinate bearbeiten, bei kleinen Arbeitsstufen echte Hinweiszahlen lesen, beide Hinweisbereiche unabhängig pannen, Raster stark zoomen/verschieben und über Miniatur/Koordinaten wiederfinden. | Eigentümer |
| M-04 | Mit #11 Teilstand schließen, neu starten und samt Historie/Ansicht fortsetzen. | Eigentümer |
| M-05 | Durch D-06 nicht anwendbar: Tastatur/Controller außerhalb P1. | Kein P1-Gate |
| M-06 | Größerer Start, 1080p/1440p und logische Referenzflächen; tatsächliche Skalierung erfassen. Keine verdeckten Elemente, aufgezwungenen Riesenraster oder verschmolzenen Füll-/Fünferlinien. | Eigentümer |
| M-07 | 100×100 auf der Referenzhardware: keine verlorenen/falschen Aktionen oder wahrnehmbaren Hänger. Im integrierten Paket 500 reproduzierbare Zell-/Navigationsaktionen gegen Sollzustand; Messung und Beobachtung getrennt. | Implementierer / Eigentümer |

Protokoll: tatsächliche Commit-/Artefaktkennung, Betriebssystem, verwendete Eingaben, Fenster-/Bildschirmgröße, reale Skalierung, Szenario und Ergebnis. Hardware-/Skalierungswerte nicht erfinden und keine pauschale FPS-Zusage aus der Referenz ableiten.

### 8.3 Gate-Zeitpunkte und bisherige Mausprobe

Vor Gesamt-P1-Merge A-01 bis A-07, Dokumentprüfung und M-01 bis M-04, M-06/M-07 nachweisen. Zwischenpakete #8/#9/#11/#12 bleiben gemäß #5 im gemeinsamen Draft-PR; keine vorgezogene Mergefreigabe durch diesen Implementierungsauftrag.

K-06: Der Nutzer hat die angebotene F-01-Spielprobe verwendet und anschließend zwei Screenshots sowie vier konkrete Rückmeldungen geliefert; der Abschlussbildschirm ist sichtbar. Bezug der Unterhaltung ist Artefakt `10719712143` / Implementierungshead `64dcca4df9ed00cecedfdb8cabba09bcb7179ae8`. Eine separate Versionsanzeige des Nutzerlaufs, tatsächliche Windows-Skalierung und vollständige Einzelbestätigung aller K-06-Szenarien liegen nicht vor.

Die Probe ist **durchgeführt mit Änderungsbedarf**, nicht pauschal bestanden. Der Nutzer beauftragt auf Basis dieses Feedbacks ausdrücklich die Vorbereitung von #9. Die frühe Feedbackschleife blockiert diesen Folgeschritt daher nicht; ihre Änderungen werden in #9 bearbeitet. Fehlende Metadaten/Einzelnachweise bleiben offen und werden mit der erneuten Maus-/Layoutprobe des neuen Artefakts erfasst. Keine vollständige M-01/M-06-/Produktabnahme aus den Screenshots ableiten. Technische Tests ersetzen diese nicht.

## 9. Aktueller Lieferstand

#9 ist der technische Lieferstand auf `feat/5-p1-prototype` / Draft-PR #14:
Feedbackänderungen D-07 bis D-17 und Farb-/Großrasterbedienung, einschließlich Tests,
Anleitung, Windows-Zwischenartefakt und nachvollziehbaren visuellen Nachweisen. Genaue
technische Nachweise und ausstehende Eigentümerabnahme stehen in #9 und im
P1.2-Prüfbericht.

#11/#12, endgültige Themenwahl, Wertung und Releasefähigkeit bleiben außerhalb dieses Schritts. Rätselproduktion/Solver und Verbundraster bleiben getrennte frühe Risikostränge.
