# HC · Hinweis-Typografie und Fitgeometrie

## Geltung und Zuständigkeit

Dieser Vertrag besitzt aktive Zahl-/Markerressourcen, Messhüllen, Schriftgrad-
und Slotwahl, Fit, C1-Farbkontur und Vollhinweis-Typografie. Die Regeln im
aktuellen Git-Stand sind der Fachvertrag; Liefer- und Abnahmebelege stehen am
konkreten Head im Issue/PR.

| Detail | Maßgebliche Quelle |
| --- | --- |
| Ableitung von OPEN/FILLED/CLOSED und semantische Speicherung | [P1](PROTOTYPE_P1.md) |
| Deckkräfte, X-Zeichnung und stabile Statusidentität | [CLUE_STATUS](CLUE_STATUS.md) |
| Hinweisdrag, Drop, Overlayinteraktion und Cursorlinien | [CLUE_INTERACTION](CLUE_INTERACTION.md) |
| Normale UI-/Überschriftrollen | [HAND_DRAWN_UI](HAND_DRAWN_UI.md) |
| Zählergröße und Cursoranker | [CELL_DRAG](CELL_DRAG.md) |
| Arbeitsflächen-Translation nach Fit | [UI_DRAWING_STYLE · VS2-N02](UI_DRAWING_STYLE.md) |

Historische Chalkboard-/24-/18-Slots sind keine parallelen aktiven Maße.

## Schrift und Rechtequelle

`game/art/drawing/DelightCoffee-Regular.ttf`: unveränderte Delight Coffee Regular,
Version 1.000, Syafrizal a.k.a. Khurasan (2023), 32268 Bytes, SHA-256
`4031afdb556558ffdecd48488fd1ae7eee857e804f4622ac5154cc7bb0c4cb23`.
Das [Originalarchiv](../font-inputs/delight_coffee.zip) ist bytegleich zum
DaFont-Download. Originalhinweise, Quellenprüfung und Eigentümerentscheidung
HC-E01 stehen in der [NOTICE](../../game/art/drawing/DelightCoffee-NOTICES.md).
`fsType=4` und die allgemeine App-/Game-Lizenzseite sind offengelegt; keine OFL
oder zusätzliche Autorenfreigabe wird behauptet.

Offline geladen; Ziffern haben keine Fallbacks, Systemfontsuche ist aus. Nur `…`
und `–` wählen ausdrücklich gebündeltes Plex. TTF und Originalhinweise werden
ins PCK exportiert; der Spieler-Lizenzordner enthält zusätzlich die NOTICE.

## C1 · Farbkontur

Hinweisfarben 2/4 erhalten eine feste dunkle Kontur auf beiden Achsen, beim
Hinweisdrag und im Vollhinweis-Overlay. RGB-Füllung, Farb-IDs und Originalindizes
bleiben erhalten; es gibt keine neue Option. Der Statusvertrag bestimmt die
gemeinsame Abschwächung von Zahl und Kontur.

Godots ganzzahlige Outline-API verwendet vierfachen Glyphenmaßstab mit
Rückskalierung: Außenradius 0,25 px bei UI100 und 0,3125 px bei UI125. Die
originale Füllglyphe wird zuletzt gezeichnet. Konturbreite hängt an UI-Skalierung,
nicht Zellzoom. Browser- und Godot-Antialiasing gelten nicht als pixelidentisch.

## Zusammenhängende Geometrie

Kurze Folgen und das Leerlinienzeichen `–` stehen rasterseitig rechts bzw.
unten. Überlauf zeigt einen maximal sinnvollen zusammenhängenden Ausschnitt
vollständiger Tokens in Originalreihenfolge unter den monotonen Drag-/Snapregeln
von HN. `…` belegt einen festen Randplatz ausschließlich auf einer tatsächlich
verborgenen Seite. Keine zusätzlichen sichtbaren Hinweisgitterlinien.

`ui/clue_typography.gd` misst native TextServer-Glyphenoffsets, Rastergrenzen und
Vorschübe der tatsächlich vorkommenden Zahlen. Die Basislinie zentriert die
gemeinsamen vertikalen Grenzen von 0–9 und beiden Plex-Markern. Zahlen bleiben
proportional, vollständig und ungeteilt.

Für jede reale Zelle wählt `full_view_board.gd` den größten passenden ganzen
Schriftgrad. Die Suchschranke wächst mit der Zelle (4× Zelle, oberhalb der nativen
Glyphengröße dieser gebundenen Schrift); es gibt keine feste Fontobergrenze.
Die gemeinsamen Hüllen schließen beide X-Züge mit größter Stärke, Variation,
C1 und AA ein. Die Zugmittellinien liegen um Stift-/C1-Radius plus 0,5 Pixel
innerhalb des nativen Zahlentokens; Polyline-AA reserviert 1 Pixel, Glyphen-AA
mindestens 0,5 Pixel. Das nutzt den kompakten Zahlenraum ohne unnötige Kreuzreserven.
Zusätzlich bleiben 2× UI-Skalierung Pixel
Abstand. Zeilenhöhe und Spaltenbreite müssen in die reale Zelle passen;
mehrstellige Spaltenhinweise können den gemeinsamen Schriftgrad begrenzen.

Alle Zeilen teilen einen ganzzahligen horizontalen Slotabstand aus der größten
symmetrischen Zahlen-/Markerhülle plus Abstand; alle Spalten analog einen
vertikalen Abstand. Farbe, Status und Folgelänge ändern diese Maße nicht.
Kleine Zellen erhalten kompakte Slots, größere Zellen größere Schrift und Slots.
UI 125 % vergrößert den Abstand, vervielfacht jedoch nicht das reale Zellmaß.

Ein begrenzter Fit-Suchlauf durch absteigende gemessene Schriftgradintervalle
prüft Kandidatenzelle, Schriftgrad, Slots und Mindestreserven gemeinsam. Er setzt
keine monotone Änderung von Hinting oder Reserveanzahl voraus; das erste
passende Intervall liefert das größte Zellmaß auf Hundertstelpixel. Das Budget ist Rasterdimension
× Zelle + Reserve × Slot + 14 Pixel pro Achse. G beweist an allen Glyph-/Marker-/
Clip-Übergängen mindestens min(5,n) vollständige zusammenhängende Hinweise im
kontinuierlichen Drag. V reserviert alle Hinweise. Erst nach Fit bietet freie
Breite beziehungsweise Höhe weitere ganze Zeilen- beziehungsweise Spaltenslots,
je Achse maximal sicher passend und durch den tatsächlichen Bedarf begrenzt, ohne
Raster-, Schrift- oder Slotverkleinerung (HF / #149). Die anschließende
gemeinsame Translation balanciert die tatsächliche Hülle ohne Leerplätze.

Drag, Marker, Snap, Tooltipzuordnung und semantische Anker verwenden dieselben
aktuellen Slotmaße. Bestätigte semantische Anker, Zoomwunsch und Speicherung folgen P1;
Hinweisdrag/Drop und Außenanschlag folgen CLUE_INTERACTION.
Größen-/UI-/Modus-/Definitionswechsel messen neu.
Typografie-, Reserve- und Glyphcaches sind transient und begrenzt; ihre Schlüssel
enthalten relevante Tokens, Achse, Schriftgrad, Slotmaße und UI-Skalierung.
History, Farbwerte, Reveal und Zellrenderer bleiben erhalten.

## HF · vollständiges Hinweis-Overlay (#149)

Die nichtmodale Ergänzung zeigt ausschließlich bei echtem Überlauf die ganze Folge.
Die Überschriftrolle von „Vollständiger Hinweis“ steht in [HZ-D01](HAND_DRAWN_UI.md).
Glyphenmaße, Umbruch und sichere Box bleiben
getrennt von den Zahlentoken gemessen;
Delight-Zahlen behalten ihre vom Rasterzoom unabhängige Overlaylesegröße.
Dieselbe baselinebezogene Zahlen-/X-Hülle einschließlich C1/AA bestimmt Innenränder,
Zeilenhöhen, Tokenumbruch und den sichtbaren Abstand zur kleineren Überschrift.
Die inhaltsabhängige Box bleibt im geschützten Board-/Papierbereich. Das ruhige
Papier ist ein Ausschnitt des vorhandenen A-Arbeitsassets; der unveränderte
SL-65-Vorschaurahmen wird mit festen Ecken und gekachelten Kanten wiederverwendet.
Die gebundene HF-Ausarbeitung verwendet den 128×128-px-Papierausschnitt ab
`(700,400)`, Rahmenzeichnung mit dem Faktor `0,5×UI` und `28×UI` Textinset.
Diese Wiederverwendung ändert weder die Originalassets noch ihre Herkunft.
Die sichere Innenfläche des Rahmens bleibt frei. Quellenzuordnung, Eingabebesitz,
Boxklicks und Lebenszyklus bei Geometrie-/Blattwechseln stehen in
[CLUE_INTERACTION](CLUE_INTERACTION.md). Vollständige Folgen öffnen keine Box.

## WEB-1: temporäre Glyphenatlanten

Der Webexport behält bei der vollständigen Schriftgradsuche höchstens acht
zuletzt gemessene Rastergrößen je Font-RID. Weitere Größenatlanten werden über
TextServer freigegeben und bei Bedarf identisch neu erzeugt. Die numerischen
Messwerte, Schriftwahl, Suchmenge und Fitgrenze bleiben unverändert; es gibt
keine neue Schriftgradkappung. Dies verhindert Heaperschöpfung bei kleinen
Rastern im begrenzten WebAssembly-Speicher. Der native Pfad bleibt unverändert.

Eine Vorablehnung anhand der früheren Querstrich-Vorschubbreite ist unzulässig:
Das X folgt der tatsächlichen Glyphenhülle; jene Breite ist keine sichere Untergrenze. Web und nativ messen jeden Kandidaten vollständig
mit derselben Hülle, ohne neue Monotonieannahme oder Schriftgradkappung.


## Aktueller Prüfweg und Abnahme

Schriftwahl, tatsächliche Glyphen-/Konturhülle und maximaler Fit werden gemeinsam
geprüft; ein Fontdateihash allein belegt keine lesbare Darstellung. Aktuelle
Auswahl und verbleibende Stichprobe stehen im [Paketvertrag](../ci/CI_WORKFLOW_V2.md)
und [nativen Modulvertrag](../ci/CI_C_NATIVE_GROUPS.md). Frühere HC-Einführungs-
matrizen, Vorher-/Nachherbilder und Windowsbelege bleiben historische Nachweise.
Technische Bilder ersetzen keine persönliche Sichtabnahme.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#92](https://github.com/venomenon328/picross/issues/92), [#149](https://github.com/venomenon328/picross/issues/149) und [#186 / PR #187](https://github.com/venomenon328/picross/pull/187).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CLUE_TYPOGRAPHY.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
