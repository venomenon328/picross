# Zeichnerische Spieloberfläche und Zellanimationen

## 1. Geltung und Zuständigkeit

Dieses Dokument besitzt sichtbare Raster-/Zellzeichnung, reine Füllminiaturen,
statische Zielvorschau, Zellanimationen und die Verteilung freier Arbeitsfläche.
Die Regeln im aktuellen Git-Stand sind vom Liefer- und Abnahmestand zu trennen;
konkrete Ergebnisse stehen am jeweiligen Head im zuständigen Issue/PR.

| Detail | Maßgebliche Quelle |
| --- | --- |
| Logische Eingabe, H1, Abschluss und Speicherung | [P1](PROTOTYPE_P1.md) |
| Hinweisfont und Slots / Interaktion / Statuszeichnung | [Typografie](CLUE_TYPOGRAPHY.md), [Interaktion](CLUE_INTERACTION.md), [Status](CLUE_STATUS.md) |
| Kleine Controls, UI-Schrift und Piktogramme | [HZ](HAND_DRAWN_UI.md) |
| Sidebargeometrie und große Rahmen | [Sidebar](SIDEBAR.md) |
| Buchnavigation, Übergänge und Capture | [Buchdarstellung](BOOK_INTEGRATION.md) |
| Atlanten, Varianten, Zeitabbildung und Cachegrenzen | [Zellrendering](CELL_RENDERING.md) |
| Rätselgebundene Hintergrundbilder | [PUZZLE_BACKGROUNDS](../production/PUZZLE_BACKGROUNDS.md) |

## 2. Zeichnerisches Ziel

Das Spielen wirkt wie die Bearbeitung eines gezeichneten Rätselbuchs. Sichtbare
Rasterlinien, Füllungen, Kreuze, Miniatur und Palette dürfen kontrolliert
handschriftlich wirken. Modell, Zellzuordnung und Eingabe bleiben geometrisch
präzise. Dekoration enthält keine Bedienattrappen, Fülltexte oder Pseudoschrift
und verrät weder Motivnamen noch eine Skizze der Lösung vor ihrem Abschluss.
Der historische Squeakross-Vergleich war ein Qualitätsbezug, keine Freigabe zur
Übernahme seiner Oberfläche, Palette, Figuren oder Assets.

## 3. Zeichensprache

### ZS-D01: Hinweiszahlen

Hinweise müssen kräftig, kompakt und klar unterscheidbar bleiben. Aktive
Schrift, regelmäßige gemeinsame Slots, gemessene Zahl-/X-/C1-/AA-Hüllen und
vollständige Erreichbarkeit gehören zu [CLUE_TYPOGRAPHY](CLUE_TYPOGRAPHY.md).
Die drei Hinweiszustände und ihr Auskreuzen stehen in [CLUE_STATUS](CLUE_STATUS.md).
Historische Chalkboard-/26-/24-/18-Angaben sind keine parallelen aktiven Maße.

### ZS-D02: Gefüllte Zellen

Eine klar erkennbare Grundfläche in der jeweiligen Rätselfarbe trägt wenige
zurückhaltende Schraffur-, Strich- oder Auftragsspuren. Die Textur unterstützt
zusammenhängende Motive und ersetzt die Füllung nicht durch luftige Einzelstriche.
Farben und ihre Zuordnung bleiben eindeutig; keine Änderung von Palette,
Farb-IDs, Lösung oder Definition für den Stil.

Leichte organische Variation liegt innerhalb der Zelle. Varianten bleiben pro Zelle
stabil, auch nach Neuzeichnen, Zoom, Ansichtswechsel und Fortsetzung; kein Flimmern durch neue
Zufallswerte pro Frame. Bei kleinen Zellgrößen und Gesamtansicht wird die Textur
vereinfacht. Der Zustand bleibt ohne Erkennen einzelner Texturstriche ablesbar.

Sichtbare Trennung zu Nachbarfüllungen und Fünferlinien bleibt verpflichtend.
Zeichnung und Effekte sind an der tatsächlichen Zell-/Viewportgeometrie geclippt.
Trefferflächen, Koordinaten, Rastergröße und Rätselfarben werden nicht dekorativ verzerrt.

### ZS-D03: Ausgekreuzte Zellen

Das X besteht aus zwei erkennbaren handschriftlichen Stiftzügen mit begrenzter
Variation in Krümmung, Winkel, Länge und Stärke. Die Variation hängt stabil an
der Zellidentität; Neuzeichnen, Zoom, Ansichtswechsel und Wiederherstellung würfeln nichts neu.
Kreuze bleiben eindeutig, übertönen aber auch auf einem stark ausgekreuzten Blatt
das gefüllte Motiv nicht. Unbekannt, X und Füllung sind im Hauptraster unmittelbar
unterscheidbar. Normale und teilweise sichtbare Zellen verwenden dieselbe Geometrie
mit korrektem Anschnitt; keine Ersatzmarkierung am Viewportrand. N05 ändert nur die
Miniaturprojektion, nicht diesen Hauptraster- oder Zellzustandsvertrag.

### ZS-D04: Buch und passive Randzeichnungen

Rätselgebundene Hintergründe folgen ausschließlich dem
[Hintergrundvertrag §13](../production/PUZZLE_BACKGROUNDS.md#13-hp-i2--runtime-darstellung-und-besuch).
Dort stehen selected/none, gemeinsamer Papieranker, proportionaler Fit,
Zoomverhalten und Einbindung in die Capturehierarchie. Die aktuelle Runtimeform
und Spieler-Lesekompatibilität stehen in [RI-ONE](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md#21-geschlossene-aktuelle-runtimeprojektion).

Für den Hintergrundstatus `legacy` und den Hilfepiloten gelten die vorhandenen
RAND-P1-Paare Wasserwelt, Landschaften & Natur und Hilfe. Ihre
[Originale und Herkunft](../../game/art/drawing/margins/provenance.json) bleiben
getrennt platzierbar: große helle Graphitskizze unten rechts, kleinere Antwort
unten links. Auswahl ausschließlich nach sichtbarer Kategorie bzw. Hilfe,
niemals nach Lösung oder Fortschritt. Katalog und Einstellungen zeigen diese
Pilotmotive nicht.

Das Funktionslayout bestimmt den verfügbaren Dekorraum. Zeichnungen bleiben
im Buch-Capture und ignorieren Pointer, Fokus und Scrollen. Eine geringe
Überlagerung unter Raster oder Hilfetext setzt einen bestätigten ruhigen
Untergrund und Lesbarkeit im nativen Mit-/Ohne-Vergleich voraus. Bei 1440p
bleibt freie Anordnung das Ziel. Dichte Überlagerungen oder harte Bedienflächen
lassen den betroffenen Motivteil entfallen; keine beliebige Verkleinerung oder
Verschiebung des Funktionslayouts. Bei engen Ansichten oder höherem Zoom tritt
der Legacy-Pilot zugunsten der Arbeitsfläche zurück. Für `selected`
gilt der oben verlinkte eigene Vertrag. Historische Asset- und Abnahmebindungen
werden nicht rückwirkend verändert.

### ZS-D05: Miniatur · VS2-E1/N05

Die Miniatur zeigt unmittelbar nur die eigenen **gefüllten Felder** in ihren
Rätselfarben, einschließlich der aktuellen elastischen Füllvorschau und möglicher
Fehler. Ausgekreuzt und unbekannt haben denselben neutralen Hintergrund; keine X,
Punkte oder anderen Leer-Ersatzzeichen. Der Hauptraster-/Spielzustand behält alle drei Zustände.

Die Miniatur bleibt passiv, proportional und unanimiert. Ihre vereinfachten Füllformen
und Fassung passen gemäß N03 zur Scribble-Sprache, ohne dominante Mikroschraffur oder
Zellanimationszwischenbilder. Vorgesehene Füllung wird sofort sichtbar; Vorschau auf
X/Neutralisierung entfernt eine vorherige Füllung nur aus dem Vorschauabbild. Rückzug
oder Abbruch stellt die bestätigten Füllungen wieder her. Dieselbe reine Darstellung
gilt für vorhandene ungelöste Albumminiaturen, ohne neue Albumgestaltung.
Motivname und fertige Illustration erscheinen weiterhin erst nach tatsächlichem Abschluss.

## 4. Statische Vorschau und Animation nach dem Anwenden

### ZS-D06: Vorschauvertrag

Die Vorschau zeigt nur wirksame Änderungen des aktuellen geraden Strichabschnitts.
Füllung oder X erscheinen vollständig, ohne Animation, in der gewählten Endform,
aber heller beziehungsweise transparenter. Der Darstellungswert beträgt 56 %. Persönliche Sichtabnahme wird am
konkreten Produkt-Head im zuständigen Issue/PR geführt.

Bei X-zu-Füllung und Füllung-zu-X zeigt die Vorschau nur den neuen Zielzustand;
die bisherige Gegenmarkierung wird nicht darunter stehen gelassen.
Bei Neutralisierung oder Radieren ist das Ziel unbekannt: Die bisherige Markierung
verschwindet bereits in der Vorschau. Eine dezente statische Vorschaukontur macht
die betroffene Zelle weiterhin sichtbar.

Elastischer Rückzug, echte Startzell-Rückkehr mit Achsenneuwahl und Abbruch
aktualisieren die Vorschau unmittelbar gemäß P1. Entfallene Vorschauänderungen
zeigen sofort den bestätigten Ausgangszustand; keine nachlaufenden Spuren.
Vorschautransparenz ist kein neuer gespeicherter Zell- oder Hypothesenzustand.

### ZS-D07: Commit und gerichtete Effekte

Erst das tatsächliche Anwenden bei Mouse-Up startet die kurze Zellanimation.
Einzelklicks bleiben Striche der Länge eins. Nach sofortigem atomarem Commit beginnen Setzen/Umwandeln vom tatsächlichen
Start zum finalen geraden Abschnittsende; Rückzug und G1-Neuwahl bestimmen diesen
Endabschnitt. Nur die `m` effektiv geänderten Füllungen/X zählen. Für `m > 1` gilt
`Δ = min(12 ms, 180 ms / (m - 1))`, Start der Zelle `i` bei `i × Δ`; bei `m = 1`
ohne Verzögerung. Mikrosekunden werden auf die nächste ganze Zahl gerundet.
Geschützte Felder/No-ops animieren nicht und erzeugen keine Zeitlücken.
Wartende Zellen zeigen bereits das gültige Ziel abgeschwächt; nie alte Gegenmarken.
Die reine Darstellung hat keine Modell-/Save-Callbacks oder Eingabesperre.

Handschriftliches Ausfüllen: Füllung baut sich sichtbar entlang aufeinanderfolgender kurzer, leicht
schräger Schraffur-/Füllstriche auf;
das X zeichnet erst den ersten, dann den zweiten Zug. Bloßes globales Fade oder
bewegte Dekorstriche auf schon kräftiger Endfüllung genügen nicht. Bei gestarteten
Füllungen bleibt unbeschriebenes Papier frei; die volle blasse Unterzeichnung entfällt
auch hier. Ruhende Endform und statische Ziehvorschau bleiben erhalten.
Beim gestarteten X bleiben ebenfalls noch nicht geschriebene Zugteile unsichtbar,
damit Zug eins und danach Zug zwei bei normaler Spielgröße sichtbar entstehen.
Die vollständige 56-%-Vorschau beim Ziehen und das abgeschwächte wartende Ziel
bleiben statisch; Endgeometrie, Farben und Clipping bleiben erhalten. Beim Neutralisieren
darf eine zuvor entfernte Füllung oder ein X nicht nochmals als Löschanimation auftauchen;
stattdessen kann die Vorschaukontur oder ein neutraler kurzer Löschhinweis auslaufen.

Es gelten **210 ms insgesamt pro Zelle** für
Setzen/Umwandeln und **120 ms** Entfernen. Teilzüge innerhalb einer Zelle folgen
aufeinander; die beiden X-Züge teilen sich die 210 ms. Die gesamte Setzfolge endet
spätestens nach 390 ms (maximal 180 ms Startspreizung plus 210 ms). Entfernen
beginnt für alle wirksamen Zellen sofort und endet nach 120 ms, ohne Staffelung.

Der Strich wird weiterhin sofort als eine atomare Aktion übernommen.
History, Hinweiszustände, Abschlussprüfung und Sicherung warten nicht auf Effekte.
Die nächste Eingabe bleibt unmittelbar möglich; bestehende P1-Sperren während
einer tatsächlich aktiven Zellgeste werden dadurch weder erweitert noch aufgehoben.

### ZS-D08: Vorrang und Lebenszyklus

| Ereignis | Verbindliches Darstellungsverhalten |
| --- | --- |
| Neue wirksame Vorschau auf noch animierter Zelle | Statische neue Vorschau hat Vorrang; alten Effekt dieser Zelle endgültig beenden. Andere Effekte dürfen weiterlaufen. |
| Rückzug/Abbruch dieser neuen Vorschau | Bestätigten Endzustand sofort zeigen; den zuvor beendeten Effekt nicht wieder starten. |
| Erneuter Commit derselben Zelle | Nur der jüngste bestätigte Zielzustand ist maßgeblich; kein alter Callback darf später Zellen oder Darstellung zurücksetzen. |
| Undo/Redo | Exakten Zustand sofort herstellen, betroffene Effekte beenden; keine eigene neue Setzanimation und keine zusätzliche Eingabesperre. |
| Escape/Fokusverlust/Gegentaste | Vorschau verwerfen und aktive sowie wartende Effekte beenden. Kein Commit oder verspäteter Wiederanlauf. |
| Blattwechsel, Reset, Restore, Album/Informationsseite | Keine Effekte in eine andere Session übertragen, speichern oder beim Wiederöffnen erneut abspielen. Bestehender Abbruch-/Flush-/Recoveryvertrag bleibt. |
| Letzter erfolgreicher Strich | Sofortiger Abschluss-/Speicherpfad; laufende Zelleffekte dürfen enden. Die Abschlussdarstellung folgt [P1 §5.4](PROTOTYPE_P1.md#54-abschluss-und-detaillierteres-ergebnisbild); Logik und Sicherung warten nicht auf das Animationsende. |
| Ansichts-/Zoom-/Größenwechsel nach Commit | Aktive und wartende Effekte beenden; keine Eingabe- oder Navigationssperre durch Effekte. |

Gegentastenabbruch, zu verbrauchende Ups und erneuter Gestenstart folgen
[P1 §5.1](PROTOTYPE_P1.md#51-werkzeuge-direkte-umwandlung-und-strichgrenzen).
Hinweisdrag folgt [HN](CLUE_INTERACTION.md). Die Darstellung führt keine
zusätzlichen Eingabe-, Hand- oder Rasterpanwege ein.

Animation ist eine transiente Darstellungsschicht. Sie verändert weder Zellen,
History, Hinweislogik, Bewertung noch Saveformat. Effekte sind innerhalb der
jeweiligen Zelle/des Viewports begrenzt; keine springenden Raster oder dauerhaft
bewegten fertigen Markierungen.

### ZS-D09: Abschaltmöglichkeit

Ein einfacher Schalter „Zellanimationen“ schaltet diese Effekte ab.
Ausschalten beendet aktive und wartende Effekte sofort und zeigt den gültigen Endzustand.
Wiedereinschalten wirkt nur auf künftige Strich-Commits; alte Aktionen werden nicht
nachgespielt. Die statische, abgeschwächte Vorschau bleibt unverändert erhalten.

Der Schalter startet
aktiv und gilt sitzungsweit, auch nach Blattwechsel, Reset und Informationsseite.
Er wird nicht im Rätselsave oder in einem neu eingeführten Einstellungsformat
persistiert und startet nach App-Neustart wieder aktiv.
Der Schalter verändert keine Zellen, History, undo_used, Hinweislesepositionen,
Autosaves oder Abschlusslogik. Kein zusätzliches globales Bewegungsmenü oder Zeitregler.

### ZS-D10: Großraster und Nachweise

Kleine Zellen, lange Hinweisfolgen, farbige Raster und stark ausgekreuzte
Zustände müssen lesbar bleiben. Historische 40×40-/100×100-Stressfälle sind
synthetische oder gebundene Prüfbelege; sie erweitern nicht den aktuellen
Produktumfang. Auswahl und Umfang neuer Regressionen folgen dem Paketplan.

Technischer Leitfaden: nur laufende visuelle Übergänge verwalten, stabil gezeichnete
Varianten wiederverwenden und den Animationstakt beenden, sobald kein Effekt mehr aktiv ist.
Animationstakte sollen keinen vollständigen UI-/Miniatur-/Analyse-Refresh auslösen.
Die konkrete Umsetzung und Leistung werden nativ gemessen; keine ungeprüfte FPS-Zusage.

Verifikation verbindet Zustands-/Gestenregressionen, gezielte native Bilder zu
bekannten Zeitpunkten, eine kleine Strichsequenz mit Negativkontrollen gegen
gleichmäßiges Fade und falsche X-Zugreihenfolge
und reale schnelle Mauseingaben. Ein Endzustands-Screenshot allein beweist keine
Animation; erfolgreiche Dokumenttests beweisen keine Lesbarkeit oder Eingabeflüssigkeit.

## 5. Prüfbarkeit

Der [Paketvertrag](../ci/CI_WORKFLOW_V2.md) und
[native Modulvertrag](../ci/CI_C_NATIVE_GROUPS.md) bestimmen die aktuelle risikobasierte
Auswahl. Historische Vollmatrizen, Referenzbilder und damalige Mengen-/ZIP-Grenzen
sind keine Dauerpflicht. Produktgarantien bleiben trotz kleinerer Stichprobe
bestehen. Pixelorakel, Zeitsequenzen und echte schnelle Eingaben werden nur im
begründeten betroffenen Umfang gewählt; ein Endbild belegt keine Animation.

## 6. Fachliche Grenzen

Dieser Darstellungsvertrag ergänzt keine Spielmechanik, Wertung, Fehlerhilfe,
Hypothesen, Audio oder neue Produktions-/Plattformfunktion. Produktumfang steht
in [PRODUCT_DEFINITION](../project/PRODUCT_DEFINITION.md); Abschlussdarstellung und
Sitzungsoptionen haben ihre oben zugeordneten Fachquellen. Historische Design-
und Rätselproofs bleiben unverändert.

## 7. VS2-E1 · kompakte, ausgewogene Arbeitsansicht

### VS2-N01: gemeinsame Hinweisgeometrie

Der aktive Vertrag steht in [CLUE_TYPOGRAPHY](CLUE_TYPOGRAPHY.md).
Die frühere Verdichtung von 26 auf 24 logische Pixel ist historische Herkunft.

### VS2-N02: ausgewogene belegte Arbeitsfläche

Nach der Fit-/Kapazitätsberechnung werden Raster und beide Hinweisflächen als ein
belegter Block bei ausreichender Restbreite weiter Richtung Mitte der nutzbaren
Papierarbeitsfläche platziert. Maßgeblich ist die Fläche ohne sichere Miniatur-/
Palettengruppe und andere Controls, nicht blind die ganze Fenstermitte.
Bei knapper Breite haben vollständige Inhalte und Bedienbarkeit Vorrang.

**VS2-V1: belegte Hülle.** Vollständig sichtbare Hinweisfolgen tragen ihre
tatsächliche zustandsunabhängige Glyphen-/Statushülle zum Block bei. Bei Überlauf
gehört der gesamte mögliche Lesebereich dazu, damit kontinuierliches Hinweislesen
keinen neuen Layoutversatz erzeugt. Leere Slots zählen nicht als belegte Fläche.
Der verbleibende gemeinsame Versatz wird auf ganze Pixel gerundet und an der
sicheren Arbeitsfläche begrenzt.

Reihenfolge: tatsächliche Mindestreserven und Fit, GF1-Zusatzkapazität für vollständige
Zeilen- und Spaltenhinweise aus freier Breite/Höhe (HF / #149), danach Ausgleich des verbleibenden Freiraums. Nicht durch künstliche
leere Hinweisslots, Kürzen sichtbarer Zahlen, kleinere gewählte Zellen oder Schrift
zentrieren. Der Anordnungsschritt darf die gültige Fitgrenze nicht nochmals senken.
Alle Hinweise, Rasterdarstellung, Cursor-/Gestenabbildung und Hit-Tests teilen den
Versatz. Fortschritt, H1-Status oder Hinweisdrag ändern die Anordnung nicht.

### VS2-N03: subtile, stabile handgezeichnete Elemente

Sichtbare Rasterlinien erhalten kleine kontrollierte Abweichungen von vollkommen
gleichmäßiger Strichführung und -stärke. Logische quadratische Zellen, Koordinaten,
Achsenbindung und Trefferflächen bleiben regelmäßig. Gemeinsame Kanten dürfen nicht
auseinanderfallen; Fünfergruppen, Ecken und gefüllte Nachbarzellen bleiben klar.
Der gesamte sichtbare Strichumfang einschließlich Abweichung/AA gehört zum Fit- und
Clippingbudget. Alle vier Rahmenkanten bleiben vollständig sichtbar.

Variation hängt stabil an Raster-/Elementidentitäten, nicht an aktuellen Zellwerten,
Mausposition oder jedem neuen Frame. Neuzeichnen und Fortsetzen würfeln nichts neu.
Bei kleinen Zellen wird sie reduziert, statt Lesbarkeit und Trennung zu verschlechtern.
Keine neue Rasteranimation und keine veränderten ZS-D06–D09-Timings oder Abbruchregeln.

**V3-01: aktiver Rasterkorridor.** Die Abweichung von der regelmäßigen Rasterlinie
beträgt höchstens 0,28 px und nimmt bei kleinen Zellen ab. Dünne Linien verwenden
0,70–0,90 px, Fünferlinien und Rahmen 1,40–1,64 px Strichbreite. Die Außenkanten
und äußeren Linienenden liegen 1,10 px innerhalb der logischen Rastergrenze.
Mit 1,00 px AA-Reserve ergibt sich das vorhandene Rahmenbudget:
`0,28 + 1,64 / 2 + 1,00 − 1,10 = 1,00 px`.
Dieser Korridor erhält die bestehenden Fit-, Zell- und Trefferflächen;
er begründet keine zusätzliche Verkleinerung des Rasters.

Miniatur samt Fassung und Farbauswahl erhalten dieselbe zurückhaltende Scribble-Sprache.
Miniaturfüllungen bleiben vereinfachte ruhige Farbformen, keine dominante Mikroschraffur.
Palettenfarb-IDs und Originalfarbflächen bleiben eindeutig; Auswahl, Hover und Fokus
müssen erkennbar sein, ohne neue Rätselfarben vorzutäuschen. Die optische Strichkante
verkleinert oder verzerrt keine Hitbox. Die normale UI-Schriftrolle folgt [HZ](HAND_DRAWN_UI.md),
die räumliche Buchdarstellung ihrem [Buchvertrag](BOOK_INTEGRATION.md).
„Kleine Vorschau“ bezeichnet hier die Miniatur; die statische Zielvorschau im Raster
bleibt ebenfalls stilistisch konsistent, aber ohne neu eingeführte Bewegung.

### VS2-N04: sichere Miniatur-/Palettengruppe

Aktuelle Mittelachse, sichere Hüllen und Platzierung stehen in
[SL65_IMPLEMENTATION](SIDEBAR.md). Der frühere V1-Versatz von
(−16,+24) × UI ist kein zusätzlicher Positionsauftrag.

### VS2-N05: reine Füllprojektion der Miniaturen

ZS-D05 ist die einzige Inhaltsregel für diese Projektion. Zwei Stände mit
gleichen Füllungen und unterschiedlichen X/unbekannt ergeben dasselbe
Miniaturbild; History, Logik und Hauptraster behalten alle drei Zustände.

## 8. VS2-E2 / V3 · aktive Zuordnung

Die Kennungen bleiben für bestehende Verweise erhalten. Ersetzte Varianten
werden nicht als zweite aktive Regel fortgeschrieben.

| Kennung | Aktiver Vertrag |
| --- | --- |
| V3-01 | Stabile handgezeichnete Rasterlinien nach VS2-N03; tatsächliche Strich-/AA-Hülle gehört zum vorhandenen Fitbudget, keine weitere Fitverkleinerung. |
| V3-02 | Drei organische helle Stiftzüge variieren in Lage, Enden, Neigung, Abstand und Krümmung stabil je Zelle. Satte Originalfarbe und Trennung bleiben. Zielvorschau, wartendes Ziel und letzter Animationsdurchgang teilen die Endtextur. Kleine Darstellungen verwenden die ruhige vereinfachte Stufe des Zellrenderingvertrags. ZS-D02/D06/D07 und der Zellrenderingvertrag bestimmen die übrige Darstellung. |
| V3-03 | Navigation folgt [BOOK_INTEGRATION](BOOK_INTEGRATION.md); alte Positionsversätze werden nicht zusätzlich angewandt. |
| V3-04 | Keine dauerhafte Werkzeug-/Farbtextzeile. Auswahlmarkierungen, Tooltips, Farberhalt und Funktion bleiben. |
| V3-05 | Keine numerische Zoomanzeige. Nichtnumerische Platz-/Hinweiswarnungen erscheinen bei Bedarf getrennt unten. Die aktuellen sechs Aktionen stehen im Sidebarvertrag. |
| V3-06 | Werkzeuganordnung folgt [SL65_IMPLEMENTATION](SIDEBAR.md); die frühere Acht-Werkzeug-Spalte ist abgelöst. |
| V3-07 | Schriftrollen und lokale Fallbacks folgen [HAND_DRAWN_UI](HAND_DRAWN_UI.md). |

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#52](https://github.com/venomenon328/picross/issues/52), [#53 / PR #56](https://github.com/venomenon328/picross/pull/56), [#61 / PR #62](https://github.com/venomenon328/picross/pull/62) und [RAND-P1 / #550](https://github.com/venomenon328/picross/issues/550).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/UI_DRAWING_STYLE.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
