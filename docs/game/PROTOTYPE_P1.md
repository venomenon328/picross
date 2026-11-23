# P1 · Spiel-, Eingabe- und Speichervertrag

## Kontosave mit Empfangsbasis

Der getrennte Kontopfad verwendet picross-account-save/v1 mit format,
definition_id, definition_revision, width, height, baseline, cells, history,
cursor, undo_used, completed und view. Die Baseline enthält genau cells,
undo_used und completed. Beide Raster müssen zur eigenen Definition passen.
Der vollständige Replay einschließlich Redozweig startet bei der Baseline.
Identischer Fortschritt erhält lokale Ansicht und History. Die Übernahme
eines anderen Fortschritts setzt den Cursor auf null und die History auf
eine leere Liste. Der Gastpfad verwendet weiterhin das geschlossene Schema 1.
Protokoll und Kontopfade stehen in [SAVE_SYNC](SAVE_SYNC.md).

## 1. Geltung, Auftrag und Quellen

Dieses Dokument besitzt logische Zellbearbeitung, Undo/Redo, lösungsunabhängige
Hinweiserkennung, Abschluss und lokale Rätselspeicherung. Die Regeln im aktuellen
Git-Stand sind der Fachvertrag. Technische Lieferung, Review und persönliche
Abnahme werden separat am konkreten Head im zuständigen Issue/PR nachgewiesen.

| Fachbereich | Maßgebliche Quelle |
| --- | --- |
| Aktueller Produktumfang | [PRODUCT_DEFINITION](../project/PRODUCT_DEFINITION.md) |
| Registrierte Inhalte, Runtime und Adapter | [CATEGORIES](CATEGORIES.md), [ZA1_ADAPTER](../production/ZA1_ADAPTER.md) |
| Fenster-/UI-Auswahl | [DISPLAY_SETTINGS](DISPLAY_SETTINGS.md) |
| Vollsichtstrategie / Hinweisgeometrie | [VS1_DECISION](VS1_DECISION.md), [CLUE_TYPOGRAPHY](CLUE_TYPOGRAPHY.md) |
| Hinweisdrag, Overlay und Cursorlinien | [CLUE_INTERACTION](CLUE_INTERACTION.md) |
| Sichtbare Hinweiszustände | [CLUE_STATUS](CLUE_STATUS.md) |
| Zellrandverhalten und Längenzähler | [CELL_DRAG](CELL_DRAG.md) |
| Raster-/Zellzeichnung, Miniatur und Effekte | [UI_DRAWING_STYLE](UI_DRAWING_STYLE.md), [CELL_RENDERING](CELL_RENDERING.md) |
| UI-Schrift und Controls / Sidebar | [HAND_DRAWN_UI](HAND_DRAWN_UI.md), [SL65_IMPLEMENTATION](SIDEBAR.md) |
| Buchnavigation und Informationsbesuche | [BOOK_INTEGRATION](BOOK_INTEGRATION.md) |
| Katalogkarten, Filter / Sortierung | [CATALOG_PRESENTATION](CATALOG_PRESENTATION.md), [CATALOG_SORTING](CATALOG_SORTING.md) |
| Namens-/Kategoriepflege und Revisionswechsel | [PUZZLE_EDITOR](../tools/PUZZLE_EDITOR.md) |
| Bildproduktion und Motivtreue | [PUZZLE_QUALITY](../production/PUZZLE_QUALITY.md), [REVEAL_TRANSPARENCY](../production/REVEAL_TRANSPARENCY.md) |
| Browserpersistenz | [WEB_HOSTING](../operations/WEB_HOSTING.md) |

## 2. Bestätigte Entscheidungen und Referenzumgebung

Die bisherigen D-Kennungen bleiben für vorhandene Verweise erhalten. Ihre
heutige Autorität steht in der folgenden Zuordnung; ersetzte Zwischenstände
werden nicht als zusätzliche Regeln weitergeführt.

| Kennung | Aktiver Fachvertrag |
| --- | --- |
| D-01 | Technikbindung in §7; Webgrenzen im Webvertrag. |
| D-02 | Spielumfang in §3 und Produktdefinition. |
| D-03A, D-03B | Elastische Vorschau und eingefrorener Gestenmodus in §5.1. |
| D-04 | Abschluss ohne Auskreuzpflicht in §5.4. |
| D-05 | Historisch gemeldete Referenzhardware; tatsächliche Prüfmetadaten am Lieferhead erfassen. |
| D-06 | P1-Eingabegrenze in §5.3. |
| D-07, D-21 | Native Fensterwahl ausschließlich in DISPLAY_SETTINGS. |
| D-08, D-24, D-26 | Sichtbare Zelltrennung, Füllfläche und X-Clipping in UI_DRAWING_STYLE/CELL_RENDERING. |
| D-09, D-15 | Zustandsabhängige Setz-/Rücknahmetabelle in §5.1. |
| D-10 | Abschlussdarstellung in §5.4; Motivtreue in den Produktionsquellen. |
| D-11, D-12, D-18 | Unnummerierte vollständige farbige Zahlen in §5.2; Typografie/Overlay in den Hinweisquellen. |
| D-13 | Monotone fitbegrenzte Zoomstufen in §5.2. |
| D-14 | Durch D-18 ersetzt; keine A–D-Option. |
| D-16, D-17, D-19, D-20, D-23 | Hinweisgeometrie/-interaktion in CLUE_TYPOGRAPHY/CLUE_INTERACTION; semantische Fortsetzung in §5.2/§6. |
| D-22 | Historischer F-02-Assetauftrag; kein aktueller Inhaltsbestand oder Produktionsgate. |
| D-25 | Cursorlinien in CLUE_INTERACTION. |
| D-27 | Längenzähler in CELL_DRAG. |
| D-28 | Durch reguläre Vollsicht in §5.2 abgelöst. |
| D-29, D-30, D-31, D-32 | Zeichensprache, statische Vorschau und Zellanimationen in UI_DRAWING_STYLE. |
| D-33 | Historische Chalkboard-/26-/18-Auswahl; heutige Geometrie ausschließlich in CLUE_TYPOGRAPHY. |

Bildschirmauflösung, reale Clientfläche, Betriebssystemskalierung und UI-Skala
sind getrennte Prüfwerte. Fehlende Metadaten werden nicht aus Screenshotmaßen
oder früheren Nutzerangaben abgeleitet.

## 3. Ziel, Umfang und Nichtziele

### 3.1 Enthalten

Der Spieler öffnet registrierte Rätsel, bearbeitet ihre Zellen, kann wirksame
Aktionen rückgängig machen bzw. wiederholen und nach Unterbrechung fortsetzen.
Die Arbeitsansicht enthält direkt zugeordnete Hinweise, eigene Vorschau und
fitbegrenzten Rasterzoom. Ein korrekter vollständiger Treffer schaltet Motivname
und Ergebnisbild frei. Katalog- und Produktumfang haben die Quellen aus §1.

### 3.2 Nicht enthalten

P1 leitet aus Bedienung keine Sterne, Perfektion, Fehlerstatistik, Rangliste,
Freischaltung, Live-Fehlerhilfe oder Hypothesen ab. Die spätere Perfektionsregel
„ohne Fehler und ohne Undo“ bleibt Produktarbeit. Ob Neutralisieren oder Radieren
später wertungsrelevante Rücknahmen sind, ist durch diesen Eingabevertrag nicht
entschieden. Produktionswerkzeuge und Plattformbetrieb haben eigene Verträge.

### 3.3 Gestaltung und Spoilergrenze

Vor gültigem Abschluss erscheinen weder Motivname noch fertiges Motivbild oder
verräterischer Platzhalter. Eigene Miniaturen zeigen unverfälschte Füllungen
inklusive möglicher Fehler nach UI_DRAWING_STYLE. Gestaltung und Buchkomposition
folgen ihren Fachquellen. Mocks sind Stilreferenzen, keine gültigen Rätseldaten
oder vorweggenommenen Produktabnahmen.

## 4. Testdaten und Datenvertrag

Der reguläre Katalog und Export enthalten registrierte Workflow-Rätsel.
Historische F-01–F-09-Piloten sind kein aktiver Katalogbestand. Allgemeine
Regressionen verwenden isolierte synthetische Definitionen; ausgewählte aktuelle
Fälle und Größenlimits stehen in den Produktions-/CI-Verträgen.

Definition und Spielerstand bleiben getrennt; P1-intern JSON, keine Datenbank.
Die Definition bindet stabile ID/Revision, Dimensionen, Palette mit stabilen
Farbkennungen, Lösungsmatrix, vollständige Zeilen-/Spaltenhinweise sowie erst
nach Abschluss sichtbare Motivdaten. Interne Indizes sind nullbasiert von
oben/links; sichtbare Koordinaten einsbasiert.

Zellen sind `unbekannt`, `leer` oder `gefüllt(Farbkennung)`. Farbindizes sind
unabhängig von Darstellungsfarben. Hinweise sind aus der Lösung reproduzierbar:
gleiche Farben benötigen Abstand, verschiedene dürfen direkt angrenzen.
Gespeicherte Hinweise werden gegen ihre Ableitung geprüft. Dimensionen,
Matrixform, Wertebereiche, Versionen und Farbverweise werden validiert;
Leerlinien werden eindeutig dargestellt. Exakte Runtimeformate, Versionsleser
und Registrierung gehören zu CATEGORIES/ZA1_ADAPTER.

Abschlussressourcen dürfen eine andere Auflösung als das Raster haben.
Format/Version, gültige lokale Bilddaten und Definitionsbindung werden geprüft;
Motivtreue folgt dem Produktionsvertrag. Fehlende oder defekte Ressourcen
werden nicht durch ein fremdes Bild ersetzt. Schema, Loader, Validator,
Export und zugehörige Dokumentation müssen bei Vertragsänderungen konsistent bleiben.

## 5. Interaktionsvertrag

### 5.1 Werkzeuge, direkte Umwandlung und Strichgrenzen

Beim normalen Werkzeug bestimmt die Maustaste zusammen mit dem **bestätigten Startzellzustand** einmalig den Aktionsmodus:

Bewertung immer aus dem ursprünglichen Zellsnapshot; gefüllt ist eine Kategorie unabhängig von der Farb-ID.

| Start / Taste | Unbekannte Zelle | X | Füllung |
| --- | --- | --- | --- |
| Unbekannt / links | Aktive Farbe | Geschützt | Geschützt |
| Unbekannt / rechts | X | Geschützt | Geschützt |
| X / links | Aktive Farbe | Aktive Farbe | Geschützt |
| X / rechts | Unverändert | Unbekannt | Geschützt |
| Gefüllt / links | Unverändert | Geschützt | Unbekannt, auch andere Farben |
| Gefüllt / rechts | X | Geschützt | X, auch andere Farben |

Einzelklicks sind Gesten der Länge eins; bewusste X↔Füllung-Umwandlung bleibt
möglich. Vorhandene Füllungen werden links nicht direkt umgefärbt. Startzustand,
Taste, Modus und aktive Farbe bleiben auch bei Rückzug und G1-Achsenneuwahl fest.

Der explizite Radierer bleibt als Universalwerkzeug: links setzt alle vorhandenen Markierungen auf unbekannt. Rechts folgt weiterhin der Leer-/Leerrücknahme-Regel. Das Hand-Werkzeug entfällt mit VS2. Werkzeug, Aktionsmodus und Setzfarbe bleiben bis zum Ende der Geste eingefroren; keine Neuerkennung pro überfahrener Zelle und kein wiederholtes Umschalten beim Rückwärtsziehen.

Die erste eindeutige Bewegung in eine andere Zelle verriegelt horizontal oder vertikal. Bei diagonalem Gleichstand bleibt nur die Startzelle in der Vorschau, bis eine Richtung dominiert. Trifft die aktive Zellgeste die tatsächliche Startzelle wieder, verkürzt sich die Vorschau auf diese Zelle und die Achse wird ohne Loslassen freigegeben. Die nächste eindeutige Bewegung wählt sie erneut; dies kann innerhalb derselben Geste mehrfach geschehen. Sonst bleibt die Achse fest und der Strich gerade. Eingabesprünge erfassen alle Zwischenzellen des aktuellen Abschnitts, schalten die Achse aber ohne gelieferten Startzelltreffer nicht frei. Ein nur auf die Achse projizierter Endpunkt am Start genügt ebenfalls nicht.

Die elastische Vorschau wird aus dem bestätigten Zustand am Gestenbeginn und dem aktuellen geraden Abschnitt berechnet. Zurückziehen verkürzt auch Rücknahmestriche; außerhalb des Abschnitts erscheint der unveränderte Ausgangszustand wieder. Eine Startüberquerung ohne tatsächlichen Treffer bleibt auf derselben Achse; nach einem Treffer ist eine neue Achsenwahl möglich. Ursprung, Modus, Werkzeug und Setzfarbe bleiben dabei eingefroren. Loslassen übernimmt nur wirksame Änderungen atomar. Beispiel 5→12→9 bearbeitet nur 5–9 nach dem eingefrorenen Modus. Keine Abschlussprüfung aus der Vorschau.

Statische Zielvorschau, zellweiser Vorrang und Effekte nach dem Commit folgen
[ZS-D06–D09](UI_DRAWING_STYLE.md). Modell, History, Abschlussprüfung und Save
werden sofort aktualisiert und warten nicht auf die Darstellung.

Längenzähler, unbegrenzte relative Pointerposition, Begrenzung an der Rasterkante,
Außen-Up und Abbruch folgen [CELL_DRAG](CELL_DRAG.md). Ein regulärer Wechsel
verwirft die Vorschau vor späterem Speichern. Während einer Zellgeste gibt es
kein Zoom, Pan, Scrollen oder Hinweisdrag; Werkzeug-/Farbwechsel gelten frühestens
für die nächste Geste.

Während einer linken/rechten Zellgeste bricht das Down der jeweils anderen Taste
die gesamte Vorschau samt Zähler ab, auch außerhalb des Boards innerhalb des
Fensters. Beide zugehörigen Ups werden ohne Commit verbraucht. Erst nach Loslassen
beider Tasten darf ein frisches Down eine neue Geste starten. Down/Bewegung bei
noch gehaltener Taste bleiben gesperrt. Escape/Fokusverlust dürfen weder
Phantom-Commit noch hängende Sperre erzeugen. Ein falsches Up ohne vorheriges
Gegentasten-Down beendet die Geste nicht.

Ein wirksamer Strich ist ein Undo-Schritt; Redo stellt exakt wieder her. Neue wirksame Änderung nach Undo verwirft den Redo-Zweig; No-ops nicht. Navigation ist keine Zellaktion. Direktes Neutralisieren wird als normale Bearbeitungsaktion rückgängig machbar, ruft nicht heimlich Undo auf und löscht kein bestehendes Undo-verwendet-Merkmal. Keine Wertungsentscheidung daraus ableiten.

### 5.2 Fenster, Zoom, Hinweise und Miniatur

Der Start zeigt den Katalog. Fenster-/Bildschirmmodus, Clientpresets und
UI100/125 folgen DISPLAY_SETTINGS. Fenstergröße, UI-Skala und gewünschter
Rasterzoom sind getrennte Größen.

Rasteransicht G ist der Sitzungsdefault; Gesamtansicht V zeigt alle Hinweise.
Die benannte Wahl steht ausschließlich in den Einstellungen und wird nicht als
Rätselsavewert eingeführt. Die gemeinsame Font-/Slot-/Fitberechnung und
G-Mindestgarantie stehen in CLUE_TYPOGRAPHY.

Jeder angebotene Zoom hält das vollständige Raster samt Außenrahmen sichtbar.
Mausrad und Plus/Minus sind monoton und stoppen am aktuellen Fit. Der gültige
Schema-1-Zoomwunsch verwendet
`12/14/16/18/20/22/24/26/28/30/32/34/36/40/44/48/54/60/66/72`.
Die tatsächliche Zellgröße ist `min(Wunsch, Fit)`; berechneter Fit darf zwischen
oder unter diesen Stufen liegen. Eine größere freie Fläche vergrößert die Zellen
nicht über den gespeicherten Wunsch. Es gibt keine reguläre Einpassen-/Arbeitsgrößen-
Aktion, Handsteuerung oder Raster-/Miniaturpan. Bei nicht bedienbarer Geometrie
bleiben Optionen und Rückweg erreichbar; keine Zell-/Historymutation durch Layout.

Hinweise gehören zu ganzen Zeilen/Spalten und werden nicht zusätzlich laufend
nummeriert. Sie zeigen vollständige einzeilige Zahlen in der Rätselfarbe;
mehrstellige Zahlen bleiben horizontal. Keine A–D-Suffixe, gestapelten Ziffern,
Kompaktkästchen oder Umschaltoption. Interne Farb-IDs bleiben erhalten.
Darstellung, Marker, unabhängiger Drag, geometrischer Snap, Vollhinweis-Overlay
und Cursorlinien folgen CLUE_TYPOGRAPHY/CLUE_INTERACTION.

Jede konkrete Zeile und Spalte besitzt eine eigene bestätigte semantische
Leseposition. Temporärer Drag wird erst beim gültigen Drop bestätigt; Abbruch
behält den vorherigen Anker. Vollanzeige erhält Rand-/Mittelanker auch beim
Speichern und Neustart; erneutes Verengen rekonstruiert sie. Zoom, Resize und
UI-Skala bewahren den gelesenen Bereich soweit möglich und begrenzen danach
für die gültige Geometrie. Zielblattwechsel stellt dessen eigene Anker wieder
her; bestätigter Reset initialisiert nur dieses Blatt neu. Ein Informationsbesuch
oder wirkungsloser Raster-/Miniaturpanversuch setzt keinen Hinweisanker zurück.
Hinweisnavigation ändert weder Zellen, History, Undo-Merkmal noch Abschluss.

**H1 / [Issue #19](https://github.com/venomenon328/picross/issues/19):** Die optionale,
standardmäßig aktive Erfüllungsmarkierung analysiert ausschließlich vollständige
Linienwerte und deren geordnete Längen-/Farbhinweise. Unbekannt bleibt offen, X ist
leer, eine Füllung legt die Farbe fest. Gleichfarbige Nachbarblöcke benötigen Abstand,
verschiedenfarbige dürfen angrenzen. Ein Hinweis ist genau dann erfüllt, wenn es
mindestens eine kompatible vollständige Linienbelegung gibt, sein Block in allen
solchen Belegungen dasselbe Intervall hat und dieses bereits vollständig in der
richtigen Farbe gesetzt ist. Eindeutig erzwungene, aber noch unbekannte Zellen genügen
nicht. Die Zustände sind OPEN (offen), FILLED (eindeutig vollständig gesetzt) und
CLOSED (zusätzlich beidseitig abgegrenzt). Ihre Darstellung gehört zu
[CLUE_STATUS](CLUE_STATUS.md).
Ein mehrdeutiger Mittelblock bei `3 3` bleibt auch
mit Rand-X normal. Existiert keine kompatible Belegung, bleiben alle Hinweise
dieser Linie unmarkiert. Andere Linien werden unabhängig bewertet.

Keine Verwendung von Lösung, Reveal, Abschluss, Fehlerstatistik, Proof oder kreuzenden
Hinweisen; auch ein gegenüber der Lösung falsch platzierter, linienintern eindeutiger
Block wird markiert. Keine automatischen Zellen oder zusätzliche Widerspruchsanzeige.
Die Markierung folgt `visible_cells()` einschließlich elastischer Vorschau und wird
nach Rückzug, Abbruch, Commit, Undo/Redo, Blattwechsel, Reset, Restore und Recovery
frisch abgeleitet. Die nebenwirkungsfreie Analyse verwendet begrenzte dynamische
Programmierung statt vollständiger Enumeration. Ein Cache hält nur den letzten
Eingang jeder Linie; reine Geometrie-/Hover-/Panänderungen starten keine neue Suche.

Für das Auskreuzen muss jedes Ende unmittelbar an X, den tatsächlichen
Linienrand oder eine vorhandene Füllung mit anderer Farb-ID grenzen. Gemischte
Abgrenzungen sind erlaubt; der andere Farbblock muss nicht selbst vollständig sein.
Unbekannte Nachbarn, entfernte X und Ausschnittränder aus Zoom/Pan zählen nicht.
Die exakte widerspruchsfreie eindeutige Zuordnung bleibt für beide positiven
Zustände erforderlich; keine neue Farb-/Abstandsregel und keine Auskreuzpflicht
für den Rätselabschluss.

Der Schalter „Erfüllte Hinweise markieren“ gilt sitzungsweit für alle Blätter, bleibt
bei Album-/Blattwechsel und Reset erhalten und startet nach App-Neustart wieder an.
Aus zeigt alle Zahlen ohne Abschwächung/X, erneutes Einschalten den aktuellen Stand. Schalter und
Analyse erzeugen weder Rasteraktion noch History, `undo_used`, Save/Autosave oder
Abschluss und verändern keine semantische Leseposition. Flags und Option gehören
nicht zum Puzzle-Saveformat; Pflicht-Flush und Recovery bleiben unverändert.

Die passive Miniatur folgt ZS-D05 in UI_DRAWING_STYLE. Die Mauspalette zeigt
unbeschriftete Originalfarbfelder mit stabilen IDs; äußere Eckmarkierungen
kennzeichnen die Auswahl. Status/Tooltip nennen die Farbnummer. Farbwahl
aktiviert Füllen, auch nach Radierer. Auswahl, Fokus oder Leerzustand dürfen
keine zusätzliche Rätselfarbe vortäuschen; keine beliebigen Nutzerpaletten.

### 5.3 Alternative Eingaben außerhalb P1

D-06 bindet die reguläre Zellbearbeitung an Maus. Tastatur-/Controllerbedienung
und das historische M-05 sind kein P1-Gate; spätere alternative Produkteingaben
bleiben davon unberührt. Escape bleibt der vereinbarte Abbruch einer Mausgeste.

### 5.4 Abschluss und detaillierteres Ergebnisbild

Die Ergänzungen zu Hintergrund, gelöster Buchöffnung und Dancing-Script-Motivname
aus [VIS-A / #728](https://github.com/venomenon328/picross/issues/728) sind
Bestandteil der regulären Buchpräsentation. Den Abnahmestand führt das Paket.

Nach einer übernommenen Aktion ist das Rätsel genau dann gelöst, wenn jede
Motivzelle in der richtigen Farbe gefüllt ist und jeder Lösungshintergrund
unbekannt oder leer markiert ist. Zusatzfüllung, fehlende/falsche Füllung oder
eine leer markierte Motivzelle verhindern den Abschluss. Vorher gibt es keine
Fehlermeldung, Prozent-richtig-Anzeige oder korrigierte Miniatur.

Die EA-Präsentation dauert insgesamt 2,15 s:

| Phase | Dauer | Darstellung |
| --- | ---: | --- |
| Arbeitsdarstellung ausblenden | 250 ms | Bestätigter Zustand bleibt logisch wirksam. |
| Füllungen zentrieren | 650 ms | Eigene bestätigte Füllungen unverzerrt und lückenlos darstellen. |
| Halten | 400 ms | Zentrierter Rasterstand. |
| Überblenden | 650 ms | Bestehendes freigegebenes farbiges Motivbild. |
| Name und Reset einblenden | 200 ms | Verdienter Motivname und bestätigbarer Reset. |

Der neutrale Titel „Blatt NN · W × H“ bleibt an derselben Stelle und nutzt die
HZ-Schriftrolle. Bild und Raster behalten unabhängig ihr Seitenverhältnis;
Name, Reset und Abschlussumschalter sind von Anfang an reserviert. Der Motivname
verwendet die eigene vergrößerte Dancing-Script-Rolle nach HZ.

Gelöste Blätter öffnen über die reguläre Buchanimation nach BOOK_INTEGRATION
in den stabilen Endzustand in Bildansicht, ohne Replay der Abschlusspräsentation.
Die zugelassene Hintergrundzeichnung bleibt während der Präsentation und in
beiden stabilen Ansichten gemäß PUZZLE_BACKGROUNDS sichtbar. Commit, History und
Schema-1-Sicherung bleiben sofortig; Präsentation wird nicht gespeichert.
Fokusverlust, Resize und UI-Skalierung zeigen das stabile Ende. Navigation
beendet die Präsentation ohne verspätete Rückkehr. Keine Vergleichsüberschriften,
doppelten Motivnamen oder Prototyptexte. Motivtreue und Bildgestaltung stehen
in den Produktionsquellen; lokale Revealglättung in CATALOG_PRESENTATION.

Reset bindet beim Öffnen des Dialogs stabile ID und Ursprung. Aus der Endansicht
öffnet er nach Erfolg dasselbe leere Blatt; aus dem Katalog bleibt er im Katalog.
Fehler-/Recoverywege bleiben erreichbar.

AR-A ergänzt im stabilen Abschluss ein einzelnes rechteckiges **Bild | Raster**-
Control mit hellem Schieber; dunkle Bereiche sind schraffiert und Konturen
handgezeichnet. Es ist erst nach der Enthüllung bedienbar. Jeder neue Besuch
beginnt bei Bild. Refresh, Resize, UI-Skala, Fokusverlust und Resetabbruch
behalten die Auswahl innerhalb desselben Besuchs.

Raster zeigt ausschließlich bestätigte Spielerfüllungen in Originalpalette mit
statischem Atlasstift, normalen/Fünferlinien und Außenrand. X/unbekannter
Hintergrund bleiben leer; Hinweise, Werkzeuge und neue Zoom-/Panbedienung
entfallen. Beide Ansichten passen proportional und zentriert in denselben
Papierbereich. Umschalten ändert weder Spielzustand, History, Abschluss,
gespeicherte Ansicht noch Savebytes und startet keine Sicherung/Enthüllung.
Katalog-/Informationsnavigation und bestätigter Reset verwerfen diese transiente
Auswahl samt zusätzlichen Darstellungsdaten.

## 6. Speicherung und Wiederaufnahme

Der [SYNC-Vertrag](SAVE_SYNC.md) beschreibt den eigenständigen Snapshotdienst
und die noch ausstehende Kontoanbindung der Spielclients. Dieser Abschnitt bleibt der
maßgebliche lokale Save-/Recoveryvertrag; der bisherige kontolose Speicherroot,
Schema 1 und vollständige Validierung ändern sich dadurch nicht. Der native
B1-Profilkern bindet eigene Saves, Fortsetzen-Merker und Syncmetadaten an den
ausdrücklich geöffneten Kontext. Die reguläre Anwendung startet im Gastprofil.
Der Syncstand projiziert daraus ausschließlich Identität, Revision, Dimensionen, Zellen, `undo_used` und `completed`. History, Cursor, Werkzeug, Farbe und Ansicht werden lokal gespeichert.
Serverrevision/Resetmarker liegen außerhalb des Schema-1-Snapshots. Ein
Serverempfang ersetzt keine vollständige Validierung vor Anwendung im Spiel.

WEB-1 ergänzt für den Browser die bestätigte IDBFS-Synchronisation, Einzeltab-
Schreibsperre und eigene Beenden-Aktion gemäß [Webvertrag](../operations/WEB_HOSTING.md).
Schema/Validierung/Recovery bleiben gleich. Browsergesteuertes Schließen kann
anders als die eigene Beenden-Aktion nicht universell blockiert werden; laufende
Sicherung, Fehleranzeige und das dokumentierte Verlustfenster gelten zusätzlich.
Der native Pflicht-Flush-/Close-Vertrag bleibt unverändert.

`user://p1/saves/` enthält die aus gültigen registrierten Inhalts-IDs gebildeten Slots. Schema 1 speichert je Blatt Definitions-ID und -Revision, Dimensionen, bestätigte flache Zellmatrix, vollständige wirksame History samt Redo-Zweig/Cursor und bleibendem `undo_used`, Abschlussstatus, Rasterfokus in Zellkoordinaten, gewünschte gültige Arbeitszoomstufe und Einpassen-Flag (overview), aktive Farbe/Werkzeug sowie individuelle semantische `row_clue_reads` und `column_clue_reads`. Nicht gespeichert werden laufende Gesten, Lösung/Reveal, Wertung, Fehlerstatistik, UI-Skalierung, Fenstergeometrie, Miniaturrahmen oder konkrete Hinweis-Slot-Offsets.

Vor Anwendung werden Schema, exakte Definition/Revision, Matrix/Palette, jede nichtleere atomare History-Aktion mit eindeutigen Indizes und gültigen Vor-/Nachwerten, das widerspruchsfreie Replay ab unbekanntem Raster einschließlich Redo, Cursor-Matrix-Gleichheit, `undo_used`, Abschluss und View vollständig geprüft. Unbekannte oder unpassende Daten werden weder teilweise geladen noch still migriert. Der Rasterfokus wird bei Resize gültig begrenzt; Hinweis-Offsets werden aus Rasterende, äußerem Anfang oder mittlerem Tokenfenster für die aktuelle Geometrie neu abgeleitet.

Erst nach vollständiger Schema-1-, Zell-/History-/Cursor-, Abschluss- und
Viewvalidierung normalisiert die reguläre Anzeige `overview=false`, `hand→fill`
und Mittelpunkt statt Pan. `overview` muss vor dieser Normalisierung als gültiges
boolesches Feld vorhanden sein. Gültiger `requested_cell` bleibt erhalten;
Istmaß ist `min(Wunsch, Fit)`. Neue Saves behalten Schema 1 und schreiben
`overview=false`. Zellen, History/Redo, `undo_used`, Abschluss, Farbe, Radierer
und semantische Hinweisanker bleiben erhalten; Recovery erhält keine zusätzliche
Schreibfreigabe.

Der sichere automatische Neustart eindeutig zuordenbarer älterer Revisionen
ist ausschließlich in [PE §9.3](../tools/PUZZLE_EDITOR.md#93-sicherer-automatischer-save-neustart)
spezifiziert. Er gilt nur für die dort validierten eigenen alten Bytes und
Marker. Fehler, fremde/neue Revisionen, laufende Recovery und allgemeine
Präferenzen werden dadurch nicht still migriert oder gelöscht.

Jede wirksame bestätigte Zellaktion und Undo/Redo werden sofort gesichert; Werkzeug/Farbe ebenfalls. Reine Ansicht darf kurz gebündelt werden, wird aber vor Album, Blattwechsel, Beenden und regulärer Window-Close-Anforderung geflusht. Vorschau wird zuerst verworfen. Fehler erscheinen sichtbar und dürfen keinen gesicherten Stand vortäuschen.

Schreiben erfolgt als vollständige Tempfassung im selben Speicherroot mit Flush, Schließen und erneuter Parse-/Vertragsvalidierung. Nur ein gültiges bisheriges Primary wird als genau eine gültige Backupfassung rotiert; erst danach ersetzt der Kandidat das Primary. Ein Abbruch lässt wenigstens die vorherige gültige Fassung ladbar. Ein verwaistes Tempfile wird nicht geladen. Gültiges Primary hat Vorrang; bei fehlendem/defektem Primary wird ein gültiges Backup sichtbar geladen. Defekte oder inkompatible Fassungen werden nicht still überschrieben; das bewusste Übernehmen eines gültigen Backups erlaubt wieder Speichern. Bei gültigem Primary und defektem Backup wird der Primärstand geladen; eine bestätigte Backup-Erneuerung erlaubt wieder Speichern. Ohne gültige Fassung erscheint ein Fehlerzustand. Der bestätigte Reset entfernt ausschließlich Primary, Backup und Temp des ausgewählten Blatts und setzt nur dessen Session zurück.

Prüfungen verwenden isolierte temporäre User-Daten; die aktuelle Prozessprüfung
steht im [nativen CI-Vertrag](../ci/CI_C_NATIVE_GROUPS.md). Ein fehlgeschlagener Pflicht-Flush blockiert Album, Blattwechsel, Beenden und Window-Close bis zu einem erfolgreichen Retry. Ein aus gültigem Backup geladener Stand bleibt auch bei fehlendem Primary bis zur bewussten Übernahme schreibgesperrt. Temporäre Hintdrag-Subslots, Hoverbänder und Strichzähler gehören nicht zum Save.
Im Album zeigt jedes ungelöste Blatt ausschließlich seine eigene gespeicherte
Spielerminiatur unter neutralem Blattnamen; nur ein valider abgeschlossener Slot
zeigt die bisherige Motiv-/Abschlussdarstellung.


## K-B: unabhängiger Fortsetzen-Merker

[Paketentscheidung #485](https://github.com/venomenon328/picross/issues/485#issuecomment-6705799391).
`user://p1/recent-puzzle.json` enthält höchstens 1024 UTF-8-Bytes mit genau
`format: picross-recent-puzzle-v1`, kanonischer `id` und positiver ganzzahliger
`revision` der Sessiondefinition. Keine Zeit-/Verlaufsliste und keine Savemigration.
Fehlende, doppelte, unbekannte, übergroße oder beschädigte Daten werden ohne
Ladeschreibvorgang ignoriert. Sichtbare Registry-ID, Definitionsrevision und normal
validierter begonnener, nicht abgeschlossener Slot müssen zusammenpassen; Redo-only
zählt als begonnen. Der Start bleibt immer der Katalog.

Nur wirksame abgeschlossene Zellaktion oder echte Undo-/Redo-Änderung setzt nach
validiertem erfolgreichem Save den Merker. Der Bearbeitungsanlass bleibt bei Savefehler
für den ausdrücklichen Retry erhalten. Navigation, Werkzeuge, Vorschau, Abbruch,
No-op und reine Ansichtssicherung markieren nicht. Abschluss/Reset eines anderen
Rätsels überschreibt den Merker nicht. Eine fehlgeschlagene Abschluss-Sicherung
behauptet keinen dauerhaften Abschluss; beim Neustart gilt der validierte Diskstand.
Metadatenfehler erhalten alte gültige Bytes und einen separaten nichtmodalen Retry.

Ein vollständiger Geschwister-Temp wird geflusht, geschlossen und strikt zurückgelesen.
Der [Windows-Publisher](../../game/model/windows_publisher.gd) startet beim Spielstart
und bedient auch den Fortsetzen-Merker über seine private Pipe. Der Austausch
verwendet MoveFileExW mit REPLACE_EXISTING und WRITE_THROUGH im selben Verzeichnis.
Die Pfadprüfung liest die Windows-Dateiattribute für Ziel und Vorfahren bei jedem
Zugriff erneut. POSIX/Web verwenden Rename. Ein identischer gültiger Merker
überspringt den Austausch. Fehler beim Merker zeigt der Katalog separat an.
Verzeichnisse, Links, ungültige Pfade und fremde Dateinamen werden zurückgewiesen.

## 7. Technikbindung und Prüfweg

### 7.1 P1-Technik

Projektpfad ist `game/`; Godot Standard mit typisiertem GDScript und passenden
Standard-Exportvorlagen. Konkrete Version, offizielle Archive und Hashprüfungen
stehen in [P1_PREFLIGHT](../ci/TOOLCHAIN.md). Kein ungeprüftes `latest`, keine globale
Installation oder eingecheckte Enginearchive.

Raster-/Aktionsmodell, Ansichtskoordinaten und Speicherung bleiben getrennt
testbar. Deutsche UI; keine Abstraktionsplattform für hypothetische Engines
oder vollständige Lokalisierungsinfrastruktur.

### 7.2 Ausführbarer Befehlsvertrag

`godot` bezeichnet den gebundenen Standard-Editor, unter Windows dessen
Konsolenprogramm. Isolierte Umgebung und Bedienung stehen in
[game/README](../../game/README.md). Der Paketplan wählt die benötigten Module.

```sh
godot --version
godot --headless --path game --import
godot --headless --path game --script res://tests/run_tests.gd
godot --path game
godot --headless --path game --export-debug "P1 Windows x86_64" build/windows/picross-p1.exe
```

Der Testrunner führt vereinbarte Logikprüfungen aus, gibt Anzahl/Ergebnis aus und endet bei Fehler mit Fehlerstatus. Import-, Start- und Exportfehler sind Fehlschläge. Begrenzte Laufzeiten; isolierter Speicher bei Tests/Smoke. Technischen Start-Smoke und reale GUI-Erprobung trennen.

Exportpreset exakt `P1 Windows x86_64`; vorher passende Templates und `game/build/windows/` anlegen. Exportpfad relativ zum Godot-Projekt. ZIP mit allen Startdateien, Anleitung und Commitkennung; keine Godot-Installation beim Nutzer voraussetzen. Keine Signaturzertifikate, Releases oder Änderung von Windows-Schutzfunktionen beauftragt.

`tools/p1_product.py` bietet die [nativen Gruppen](../ci/CI_C_NATIVE_GROUPS.md) für Import,
Godot-Tests, Negativpfad, Save-Roundtrip, Start und Export. Lokal mit `--groups`
gezielt wählen; ohne Auswahl bleibt der vollständige Umfang aktiv. Package CI
startet nur die im Paketplan gewählten Module. Ihr obligatorischer Windowsbau ist
keine automatische Auswahl aller nativen Export-/Funktionsprüfungen. Die alte
[p1-product.yml](../../.github/workflows/p1-product.yml) ist nur manuell/wiederverwendbar.
`preflight` nach tatsächlichem Toolchain-/Harnessbedarf auswählen.
Aktuelle Ergebnisse werden am konkreten Head/Basisstand im PR gebunden.

## 8. Akzeptanz und Abnahme

### 8.1 Automatisiert durch Implementierer / CI

Die A-Kennungen bleiben als fachliche Zuordnung erhalten. Der
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und [native Modulvertrag](../ci/CI_C_NATIVE_GROUPS.md)
bestimmen tatsächliche Auswahl, kurze Historyroute und aktuelle Erfolgsgates.
Historische Vollmatrizen oder 500-Aktionen-Läufe sind keine Dauerpflicht.

| ID | Fachliche Prüfeigenschaft |
| --- | --- |
| A-01 | Strikte Definitions-/Hinweis-/Ressourcenvalidierung nach §4 und Produktionsverträgen. |
| A-02 | Setzen, Neutralisieren, Radieren, Achsenwahl, Rückzug, Grenzen, Abbruch und No-op nach §5.1. |
| A-03 | Atomarer Strich, exaktes Undo/Redo und korrekte Verzweigung nach §5.1. |
| A-04 | Gemeinsame Zeichen-/Hit-Geometrie, Vollsicht und individuelle Hinweisanker nach §5.2. |
| A-05 | Vollständige Saveprüfung, Wiederaufnahme und Recovery nach §6. |
| A-06 | Eigene unkorrigierte Miniatur, Spoilergrenze und exakter Abschluss nach §3.3/§5.4. |
| A-07 | Gebundener Import, Start/Exit und Export nach §7. |

### 8.2 Manuelle Prüfungen am gelieferten Commit/Artefakt

Reale Bedienung, Lesbarkeit und Windows-Grafikverhalten benötigen tatsächliche
Beobachtung. Headless- oder Dokumenttests ersetzen diese nicht. Protokolle nennen
Commit/Artefakt, Betriebssystem, Eingaben, Client-/Bildschirmmaße, reale Skalierung,
Szenario und Ergebnis. Keine erfundenen Metadaten oder allgemeine FPS-Zusage.

### 8.3 Gate-Zeitpunkte und historische Mausproben

M-01–M-07 und frühere Paketgates beschreiben ihre ursprünglichen Lieferungen.
Deren Nachweise und Änderungen stehen in den jeweiligen Issues/PRs; sie werden
nicht durch einen Dokumentationscommit neu erfüllt oder als offen behauptet.
Aktuelle Arbeit folgt dem gegenwärtigen Auftrag und Paketplan.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#5](https://github.com/venomenon328/picross/issues/5), [#8](https://github.com/venomenon328/picross/issues/8), [#12](https://github.com/venomenon328/picross/issues/12), [#19](https://github.com/venomenon328/picross/issues/19), [#48](https://github.com/venomenon328/picross/issues/48), [#170](https://github.com/venomenon328/picross/issues/170), [#485](https://github.com/venomenon328/picross/issues/485) und [#486](https://github.com/venomenon328/picross/issues/486).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PROTOTYPE_P1.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.

## Katalogprofile für Abschlussbilder

Runtime v9 prüft beim Start die deklarierten Maße, Profilpfade und Ressourcenexistenz ohne Texturdekodierung. Eine gelöste Katalogkarte lädt nach der Sessionfreigabe ein Profil. Abschluss und erneutes Öffnen eines gelösten Blatts laden das Original. Fehlende oder inkonsistente Bindungen ergeben einen Katalogfehler. Saveformat und frühere Runtime-Lesepfade bleiben erhalten.
