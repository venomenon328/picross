# HC · aktive Hinweis-Typografie (#92)

## Fortschreibung HS / #186

Bei Hinweisarbeit zusätzlich [Hinweisstatus HS](CLUE_STATUS.md) vollständig lesen.
HS-D01–D04 ersetzen die bisherige 78-%-Abschwächung
nur des mittleren Zustands und den geraden Durchstrich: beide positiven Zustände
bleiben gleich blass (60 %), CLOSED erhält zusätzlich ein deutlicheres
handschriftliches X über dem gesamten Token. Zahlfarbe, C1-Semantik und H1/GP48 bleiben.
Zeichnung, tatsächliche Hüllen, Tooltipmessung und Web-Fit-Vorselektion werden
zusammen angepasst. Die aktiven P1-/Design-/Zeichensprachepassagen und Anleitungen
sind inline nachgeführt. [HS-Prüfzuordnung](HS_VERIFICATION.md) bindet die technische
Lieferung; erneutes unabhängiges Review bleibt offen. HS-M01 ist für die unveränderte
Darstellung persönlich erteilt (Issue #186/V2), ohne nachgereichte Prüfmetadaten.
Fonts und übrige HC-/HF-Verträge bleiben.

[Issue #92](https://github.com/venomenon328/picross/issues/92) ersetzt für aktive
Hinweise Chalkboard und feste 24/18-Slots. Historische ZS1-/VS2-Lieferberichte
behalten ihre Bindung. Bakso, Fraunces und Plex behalten ihre übrigen UI-Rollen.

## Schrift und Rechtequelle

`game/art/drawing/DelightCoffee-Regular.ttf`: unveränderte Delight Coffee Regular,
Version 1.000, Syafrizal a.k.a. Khurasan (2023), 32268 Bytes, SHA-256
`4031afdb556558ffdecd48488fd1ae7eee857e804f4622ac5154cc7bb0c4cb23`.
Das [Originalarchiv](font-inputs/delight_coffee.zip) ist bytegleich zum
DaFont-Download. Originalhinweise, Quellenprüfung und Eigentümerentscheidung
HC-E01 stehen in der [NOTICE](../game/art/drawing/DelightCoffee-NOTICES.md).
`fsType=4` und die allgemeine App-/Game-Lizenzseite sind offengelegt; keine OFL
oder zusätzliche Autorenfreigabe wird behauptet.

Offline geladen; Ziffern haben keine Fallbacks, Systemfontsuche ist aus. Nur `…`
und `–` wählen ausdrücklich gebündeltes Plex. TTF und Originalhinweise werden
ins PCK exportiert; der Spieler-Lizenzordner enthält zusätzlich die NOTICE.

## Zusammenhängende Geometrie

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
aktuellen Slotmaße. Nur bestätigte semantische Lesepositionen werden gespeichert;
Vorübergehende Vollanzeige überschreibt weder Rand- noch Mittelanker, auch nicht
beim Speichern. Nach erneutem Verengen wird daraus die Lesestelle rekonstruiert.
Zoomwunsch und Schema 1 bleiben. Größen-/UI-/Modus-/Definitionswechsel messen neu.
Typografie-, Reserve- und Glyphcaches sind transient und begrenzt; ihre Schlüssel
enthalten relevante Tokens, Achse, Schriftgrad, Slotmaße und UI-Skalierung.
History, Farbwerte, Reveal und Zellrenderer bleiben erhalten.

## Aktueller Prüfweg und Abnahme

Die reguläre Product-Prüfung nach [CI-Policy](CI_POLICY.md) enthält:

- Kern-/Eingabe-/Save-/Recoveryregressionen und echte Prozessneustarts.
  Komponenten-Überlaufprüfungen verwenden ausdrücklich schmale Testbereiche:
  kompakte Slots machen zuvor überlaufende F06-Zeilen vollständig sichtbar.
- VS2-Matrix: G/V, 1280×720, 1600×900, 1920×1080, 2560×1440, UI 100/125 %,
  Mono/Farbe, Rechtecke und Fitgrenzen; native Glyphen-/Kontur-/Statushüllen.
- Unabhängige Python-Rekonstruktion aus nativen RID-Messdaten, ausgewählter und
  nächster Schriftgrad, gemeinsame Slots, Fitbudget und nicht mehr passender
  nächster Hundertstelkandidat; negative Kontrollberichte.
- `hc92_capture.gd` / `hc92_verify.py`: 72 native Vorher-/Nachherproben bei
  16/24/40 Pixel Zelle, UI 100/125 %, Mono/Farbe, drei Zuständen, `1/11/17/40`
  auf beiden Achsen. Pixelgrenzen, sichtbares Wachstum und kompakte Slots.
  Der alte Renderer dient nur als enger Fontvergleich.
  Der begrenzte technische Download enthält verpflichtend zwölf unveränderte
  offene Mono-Vorher-/Nachher-PNGs (alle drei Zellmaße, beide UI-Skalierungen)
  und Messdaten aller 72 Proben. Weitere PNGs bleiben budgetabhängig optional.
- Frisch heruntergeladener Windows-Player: native Starts und Save-Neustarts,
  tatsächliche separate PCK, Fontdatenhash, Glyphen 0–9 aus deren Font-RID
  und unveränderte Originalhinweise (`hc92_pack.gd`).

Konkrete Ergebnisse stehen im Draft-PR, gebunden an Head, Basis, getesteten
Checkout und Run, einschließlich getrenntem vollständigem Selbstreview.
Unabhängiges Review und **HC-M01 durch den Eigentümer vor Merge bleiben offen**.
HC-M01 verlangt ein geeignetes Farbrätsel im gebundenen Windows-Export bei
kleinem, mittlerem und großem Zoom samt Lesbarkeit, Zellraumnutzung, beiden
Slotabständen und Linksdrag gemäß [HN](CLUE_INTERACTION.md). Technische Bilder ersetzen diese Sichtabnahme
nicht. Commit, Push und Draft-PR sind beauftragt; kein Merge oder Release.

## HF · vollständiges Hinweis-Overlay (#149)

Die nichtmodale Ergänzung zeigt ausschließlich bei echtem Überlauf die ganze Folge.
„Vollständiger Hinweis“ verwendet die vorhandene Fraunces 600 bei 13 × UI;
Delight-Zahlen behalten ihre vom Rasterzoom unabhängige Overlaylesegröße.
Dieselbe baselinebezogene Zahlen-/X-Hülle einschließlich C1/AA bestimmt Innenränder,
Zeilenhöhen, Tokenumbruch und den sichtbaren Abstand zur kleineren Überschrift.
Die inhaltsabhängige Box bleibt im geschützten Board-/Papierbereich. Das ruhige
Papier ist ein Ausschnitt des vorhandenen A-Arbeitsassets; der unveränderte
SL-65-Vorschaurahmen wird mit festen Ecken und gekachelten Kanten wiederverwendet.
Dessen sichere Innenfläche bleibt frei. Keine neue Bild- oder Fontauswahl.
Layout-/Kapazitäts-/Blattwechsel prüfen Quelle und Trefferrechteck auch unter
ruhender Maus neu; Boxklicks werden konsumiert. Vollständige Folgen öffnen keine
Box und bieten keine wirkungslose Navigation. [Prüfzuordnung](HF149_VERIFICATION.md).

## WEB-1: temporäre Glyphenatlanten

Der Webexport behält bei der vollständigen Schriftgradsuche höchstens acht
zuletzt gemessene Rastergrößen je Font-RID. Weitere Größenatlanten werden über
TextServer freigegeben und bei Bedarf identisch neu erzeugt. Die numerischen
Messwerte, Schriftwahl, Suchmenge und Fitgrenze bleiben unverändert; es gibt
keine neue Schriftgradkappung. Dies verhindert Heaperschöpfung bei kleinen
Rastern im begrenzten WebAssembly-Speicher. Der native Pfad bleibt unverändert.
Die Webregression öffnet und beendet dafür einen festen 5×5-Monofall.

HS entfernt die frühere Vorablehnung anhand der Vorschubbreite des geraden
Querstrichs. Das X folgt der tatsächlichen Glyphenhülle; die alte Breite wäre
keine sichere Untergrenze mehr. Web und nativ messen jeden Kandidaten vollständig
mit derselben Hülle, ohne neue Monotonieannahme oder Schriftgradkappung.
Die acht temporären Größenatlanten pro Font-RID bleiben erhalten.
