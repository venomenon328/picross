# Zeichnerische Spieloberfläche und Zellanimationen

## Aktueller Stand · V1 technisch geliefert, V2 freigegeben und offen

Die reguläre VS2-Erstlieferung liegt in [Draft-PR #62](https://github.com/venomenon328/picross/pull/62)
auf `2c332ad688315bfa851f7c0d8642d2ab4ac3709c`, Basis
`fad885344874534629365917a2ab6a8d311cd3a7`. Sie erhält den ausgewählten
Chalkboard-/Stiftzeichner und ZS2-N01–N03. Nur MMB auf überlaufenden Hinweisfolgen
bleibt Navigation; Hand-/Raster-/Miniaturpan entfallen. Fit und Rendering
verwenden dieselbe Vollsichtgeometrie. Diese Lieferung ist noch nicht gemergt.

[Review R1](https://github.com/venomenon328/picross/pull/62#pullrequestreview-5472592800)
ist für diesen Head und seinen damaligen Vertrag abgeschlossen, ohne B-Befund.
Der Eigentümer hat anschließend **VS2-E1 / N01–N05 als Spezifikation freigegeben**:
kompaktere Zeilenhinweise, ausgewogenere Platzierung, subtile Scribble-Optik und
Miniatur/Palette weiter innerhalb des Buches; Miniaturen zeigen nur Füllungen.
Der verbindliche Vertrag steht in Abschnitt 7. **S0 abgeschlossen; V1/N01/N02/N04
auf `40829b43db6509447863c9d27dbb87dcfaf2a988` technisch geliefert; V2/N03/N05 offen.**
[Parameter, Präzisierung der Glyphenprobe und Nachweise](VS2_V1_IMPLEMENTATION.md).
[Review R2](https://github.com/venomenon328/picross/pull/62#pullrequestreview-5479141642)
prüfte V1-Code und verfügbare native Bilder positiv; R2-B01 verlangt die hier
nachgeführte Quellenkonsistenz. Die Nacharbeit ändert keinen Produktcode.
VS2-M01 hat Rückmeldung mit Änderungsbedarf, keine vollständige positive Abnahme.

Bedien-/Speichergrundlage: [P1](PROTOTYPE_P1.md). Die
[Prüfzuordnung](VS2_VERIFICATION.md) und [Windows-Probe](VS2_OWNER_TRIAL.md)
unterscheiden Erstlieferung, geprüften V1-Zwischenstand und noch offene V2-Nachweise.
Vor Merge bleiben V2, aktuelle kombinierte technische Prüfung,
unabhängiges Review des kombinierten Heads, VS2-M01 und passende Mergefreigabe nötig.
Historische Nachweise bleiben commitgebunden; keine Produktänderung durch diese
Dokumentationsnacharbeit.

Stand: 10.10.2026 · Spezifikation 0.7 · R2-B01: S0/V1-Status und Glyphenpräzisierung konsolidiert

## 1. Auftrag, Quellen und Status

Der Eigentümer hat am 07.10.2026 die besprochene Weiterentwicklung des Buchdesigns
als Spezifikation freigegeben und ihre Übernahme in Issues und Repository-Dokumente
beauftragt. Die Bewegungsregel bleibt verbindlich: Die Vorschau während einer
Zellgeste bleibt statisch und heller beziehungsweise transparenter; Zellanimationen
beginnen erst beim tatsächlichen Anwenden des Strichs. Die frühere Empfehlung,
bereits während des Ziehens zu animieren, ist ausdrücklich verworfen.

Dieses Dokument beschreibt die dauerhaften Gestaltungs- und Darstellungsverträge.
[ZS-1](https://github.com/venomenon328/picross/issues/52) lieferte die native
Vergleichsprobe und konkrete Auswahl, [ZS-2](https://github.com/venomenon328/picross/issues/53)
deren reguläre Integration. Die aktuelle Vollsichtintegration mit VS2-E1 steht in
[Issue #61](https://github.com/venomenon328/picross/issues/61). Die Pakete gehören zu
[Zieldesign #21](https://github.com/venomenon328/picross/issues/21);
[Z3/#24](https://github.com/venomenon328/picross/issues/24) bleibt die anschließende
längere Spielerprobung. Paketstatus, Lieferhead, Nachweise und Abnahme stehen in den
Issues/PRs. Spezifikationsfreigabe ist weder Produktimplementierung noch Mergefreigabe.

Historische ZS-Ausgangsbasis ist main ec99954268f1ad959d9ea779dbbd9e28edf7d8fa
mit integriertem Z2, GP-48, ZV-50 und RP-6. Vor einer späteren Ausführung den dann
aktuellen Stand prüfen. [AGENTS.md](../AGENTS.md),
[lokaler Workflow](dev-rules/WORKFLOW.md), [Projektprofil](PROJECT_PROFILE.md),
[Produktdefinition](PRODUCT_DEFINITION.md), [Gestaltungskonzept](DESIGN_CONCEPT.md),
[P1-Vertrag](PROTOTYPE_P1.md) und [aktive Z2-Auswahl](Z2_SELECTION.md) bleiben
Pflichtquellen im jeweiligen Geltungsbereich.

[Eigentümerentscheidung ZS1-E1](https://github.com/venomenon328/picross/pull/55#issuecomment-6040480659)
konkretisiert die Auswahl: Stiftfüllung und kurzes Timing sind gewählt. N01–N06
ersetzen die offene Tinte-/Stiftwahl, frühere Fraunces-Hinweiskandidaten, bloßes Fade
und zusätzliche Rand-UI. R1 bleibt an `4ae4f5a20273808f99d257a3812da86d72307a5f`
gebunden. [Fontinput](ZS1_FONT_INPUT.md): beide Original-TTFs samt Nutzungshinweisen durch
[ZS1-E2](https://github.com/venomenon328/picross/pull/55#issuecomment-6042067344)
für die beauftragte Studienlieferung akzeptiert; zusätzliche Lizenztexte sind kein Startblocker.

[Eigentümerentscheidung ZS1-E3](https://github.com/venomenon328/picross/pull/55#issuecomment-6043750653)
wählt **Chalkboard Regular** als Hinweisfont und reduzierte die gemeinsame horizontale
Slotweite der Zeilenhinweise links vom Raster auf **26 logische Pixel bei UI 100 %**
(UI-skaliert). Die Spaltenhinweise blieben bei 18 logischen Pixeln. Der Eigentümer
hat die Mergefreigabe ausdrücklich vor die kombinierte Sichtprüfung gezogen: Die
visuelle Gesamtprüfung wurde anschließend auf `main@985cf08e` erfolgreich
abgeschlossen und am 07.10.2026 bestätigt; #52 ist abgeschlossen.
Diese 26/18-Werte beschreiben die ZS-/VS2-Erstlieferung. **VS2-V1/N01 verwendet
regulär 24 × UI horizontal und unverändert 18 × UI vertikal.**
Die historische Auswahl und ihre Nachweise werden nicht rückwirkend verändert.

## 2. Ziel und begrenzte Ablösung

Das Spielen soll wie das Bearbeiten eines gezeichneten Rätselbuchs wirken.
Hinweisziffern, Zellmarkierungen, Werkzeuge und Umgebung erhalten eine zusammengehörige
Handschrift. Das Raster bleibt in Modell, Zellzuordnung und Eingabe geometrisch präzise;
seine visuelle Gestaltung darf charaktervoll und spielerisch sein. VS2-E1/N03 erweitert
diese Richtung ausdrücklich auf leicht handgezeichnete Rasterlinien, Miniatur und Palette.
Die frühere pauschale Forderung nach einem sachlichen Raster bedeutet keine sterile
Darstellung und verbietet nicht die hier bestätigten begrenzten Strichabweichungen.

Der bereitgestellte Squeakross-Screenshot dient ausschließlich als Qualitätsvergleich.
Keine Nachbildung seiner Oberfläche, Anordnung, Palette, Figuren oder Zellmotive;
keine Übernahme fremder Assets. Die Vergleichsbilder im Chat sind keine Pflichtassets
oder mathematischen Rätseldaten für die spätere Umsetzung.

Die gewählte A-Buchkomposition bleibt Grundlage. GD-03/GP-03 wurden für die
gezielte Untersuchung der Hinweisziffern geöffnet: Schriftform, Gewicht, optischer
Schriftgrad und gegebenenfalls bewusst gewählte gemeinsame Slotmaße. Fraunces-Titel,
Plex-Sans-Bedientexte und die C1-Farbkontur bleiben Grundlage. VS2-E1 erlaubt die
begrenzte neue Flächenverteilung und Scribble-Fassung, keine allgemeine Hintergrund-,
Schrift-, Themen- oder Albumneuauswahl.

Die Stiftfüllung ist gewählt. Der enge E2-Vergleich enthielt Bakso Daging Regular
und Chalkboard Regular; E3 wählt **Chalkboard Regular**. Bakso Daging und Plex bleiben
nur Vergleichsreferenzen der Studie. Die ausgewählte Erstlieferung verwendet
26 logische Pixel horizontale Zeilenslots und 18 vertikale Spaltenslots bei UI 100 %.
V1 verdichtet nur die Zeilenslots auf 24 × UI; Auswahl und technische Nachweise
stehen in [VS2_V1_IMPLEMENTATION.md](VS2_V1_IMPLEMENTATION.md). Historische Tinte-/Stiftbilder
und R1/R2 bleiben Referenzen ihrer Lieferstände, keine erneut offene Grundsatzwahl.

## 3. Zeichensprache

### ZS-D01: Hinweiszahlen

Kräftige, kompakte Ziffern mit klaren Innenräumen und höherem optischem Flächenanteil
im verfügbaren Platz. Zuerst Form, Gewicht und optische Größe untersuchen; bloßes
Einschalten von Fettdruck reicht als Lieferziel nicht. Die historische Ausgangsfassung
forderte bereits Plex-Sans-Gewicht 600. Dessen sichtbare Wirkung musste nativ
beurteilt werden; die konkrete Chalkboard-Auswahl ist inzwischen bestätigt.

Keine absichtlich schwer lesbare Handschrift, verzogenen Ziffern oder zufälligen
Zeichenabstände. Ein- und mehrstellige tatsächlich vorkommende Zahlen
bleiben horizontal, vollständig und klar unterscheidbar. Alle Folgen einer Orientierung
verwenden gemeinsame regelmäßige Slots. Eine Anpassung ihrer Maße ist nur als
dokumentierte Auswahl zulässig und erhält unabhängige Liniennavigation, vollständige
Erreichbarkeit, Randmarker, geometrischen Snap und semantische gespeicherte Lesepositionen.

Normal, abgeschwächt und durchgestrichen bleiben dieselben drei GP-48-Zustände.
Farb-IDs, Hinweisreihenfolge und Originalindex sowie die lösungsunabhängige H1/GP-48-
Analyse einschließlich Vorschau bleiben unverändert. Alle Zustände müssen auf beiden
Achsen, im kontinuierlichen Hinweisdrag und im vollständigen Tooltip funktionieren.
Helle Rätselfarben bleiben durch C1 erkennbar; Statuswechsel verändern weder Slot
noch Schriftgröße. Auslassungsmarker und Leerlinienzeichen erhalten keine neue Bedeutung.

**E3 / historische Hinweisgeometrie:** Chalkboard Regular ist gewählt. Die Erstlieferung
verwendet im Buchlayout **26 × UI-Skalierung** horizontal statt der früheren 30 × UI.
Die Spaltenhinweise oberhalb des Rasters bleiben bei **18 × UI-Skalierung**.
**Aktueller V1-Vertrag VS2-E1/N01:** Die horizontalen Abstände betragen **24 × UI**
bei unverändertem Schriftmaßstab. Slotprinzip, Marker-/Drag-/Snap-/Tooltip- und
semantische gespeicherte Lesepositionen bleiben. Die Glyphenpräzisierung in §7
begrenzt den gezielten V1-Abnahmefall, nicht den Bestand großer Regressionsblätter.

### ZS-D02: Gefüllte Zellen

Eine klar erkennbare Grundfläche in der jeweiligen Rätselfarbe trägt wenige
zurückhaltende Schraffur-, Strich- oder Auftragsspuren. Die Textur unterstützt
zusammenhängende Motive und ersetzt die Füllung nicht durch luftige Einzelstriche.
Farben und ihre Zuordnung bleiben eindeutig; keine Änderung von Palette,
Farb-IDs, Lösung oder Definition für den Stil.

Leichte organische Variation liegt innerhalb der Zelle. Varianten bleiben pro Zelle
stabil, auch nach Neuzeichnen, Pan, Zoom und Fortsetzung; kein Flimmern durch neue
Zufallswerte pro Frame. Bei kleinen Zellgrößen und Gesamtansicht wird die Textur
vereinfacht. Der Zustand bleibt ohne Erkennen einzelner Texturstriche ablesbar.

Sichtbare Trennung zu Nachbarfüllungen und Fünferlinien bleibt verpflichtend.
Zeichnung und Effekte sind an der tatsächlichen Zell-/Viewportgeometrie geclippt.
Trefferflächen, Koordinaten, Rastergröße und Rätselfarben werden nicht dekorativ verzerrt.

### ZS-D03: Ausgekreuzte Zellen

Das X besteht aus zwei erkennbaren handschriftlichen Stiftzügen mit begrenzter
Variation in Krümmung, Winkel, Länge und Stärke. Die Variation hängt stabil an
der Zellidentität; Neuzeichnen, Pan, Zoom und Wiederherstellung würfeln nichts neu.
Kreuze bleiben eindeutig, übertönen aber auch auf einem stark ausgekreuzten Blatt
das gefüllte Motiv nicht. Unbekannt, X und Füllung sind im Hauptraster unmittelbar
unterscheidbar. Normale und teilweise sichtbare Zellen verwenden dieselbe Geometrie
mit korrektem Anschnitt; keine Ersatzmarkierung am Viewportrand. N05 ändert nur die
Miniaturprojektion, nicht diesen Hauptraster- oder Zellzustandsvertrag.

### ZS-D04: Buch und funktionale UI ohne zusätzliche Randdekoration

Die zusätzliche Studien-Randdekoration wird nach E1/N05 entfernt. Funktionale
Buchmontierungen, Werkzeuge und Miniaturfassung bleiben erhalten. VS2-E1/N03/N04
erlaubt die stilistische Überarbeitung und begrenzte Verschiebung der vorhandenen
Miniatur-/Palettengruppe, keine zusätzliche dekorative Rand-UI. Eine spätere
Hintergrundbildanpassung ist zurückgestellt, kein aktueller Assetauftrag und kein
Gate für #52/#53. Hintergrund und historische Artworkpakete bleiben unverändert.

Hinweise und Raster erhalten einen ruhigen Untergrund. Dekoration gibt weder
Motivnamen noch eine vorzeitige Skizze der Lösung preis und enthält keine eingebrannten
Bedienattrappen, Fülltexte oder Pseudoschrift. Bei engeren Ansichten beziehungsweise
höherem Zoom tritt sie zugunsten der Arbeitsfläche zurück. ZV-50-Flächennutzung und
die Erreichbarkeit aller bestehenden Werkzeuge werden nicht eingeschränkt.
Historische hashgebundene Designpakete bleiben unverändert; neue Lieferassets sind
gesondert nach Herkunft, Rechten und Version zu dokumentieren.

### ZS-D05: Miniatur – Folgespezifikation VS2-E1/N05

Die Miniatur zeigt unmittelbar nur die eigenen **gefüllten Felder** in ihren
Rätselfarben, einschließlich der aktuellen elastischen Füllvorschau und möglicher
Fehler. Ausgekreuzt und unbekannt haben denselben neutralen Hintergrund; keine X,
Punkte oder anderen Leer-Ersatzzeichen. Diese freigegebene Folgeregel ist noch nicht
implementiert und ersetzt die frühere visuelle Dreizustandsunterscheidung nur in
Miniaturen. Der Hauptraster-/Spielzustand behält alle drei Zustände.

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
aber heller beziehungsweise transparenter. 56 % bleiben der unveränderte
Ausarbeitungswert; eine neue gesonderte Eigentümerabnahme dafür fehlt.

Bei X-zu-Füllung und Füllung-zu-X zeigt die Vorschau nur den neuen Zielzustand;
die bisherige Gegenmarkierung wird nicht darunter stehen gelassen.
Bei Neutralisierung oder Radieren ist das Ziel unbekannt: Die bisherige Markierung
verschwindet bereits in der Vorschau. Eine dezente statische Vorschaukontur macht
die betroffene Zelle weiterhin sichtbar.

Elastischer Rückzug, echte Startzell-Rückkehr mit Achsenneuwahl und Abbruch
aktualisieren die Vorschau unmittelbar gemäß P1. Entfallene Vorschauänderungen
zeigen sofort den bestätigten Ausgangszustand; keine nachlaufenden Spuren.
Vorschautransparenz ist kein neuer gespeicherter Zell- oder Hypothesenzustand.

### ZS-D07: Commit und gerichtete Effekte (ZS2-E2 plus Nacharbeit 09.10.2026)

Erst das tatsächliche Anwenden bei Mouse-Up startet die kurze Zellanimation.
Einzelklicks bleiben Striche der Länge eins. Maßgeblich ist die bestätigte
[ZS2-E2-Nacharbeit N01–N03](https://github.com/venomenon328/picross/pull/56#issuecomment-6061611805).
Nach sofortigem atomarem Commit beginnen Setzen/Umwandeln vom tatsächlichen
Start zum finalen geraden Abschnittsende; Rückzug und G1-Neuwahl bestimmen diesen
Endabschnitt. Nur die `m` effektiv geänderten Füllungen/X zählen. Für `m > 1` gilt
`Δ = min(12 ms, 180 ms / (m - 1))`, Start der Zelle `i` bei `i × Δ`; bei `m = 1`
ohne Verzögerung. Mikrosekunden werden auf die nächste ganze Zahl gerundet.
Geschützte Felder/No-ops animieren nicht und erzeugen keine Zeitlücken.
Wartende Zellen zeigen bereits das gültige Ziel abgeschwächt; nie alte Gegenmarken.
Die reine Darstellung hat keine Modell-/Save-Callbacks oder Eingabesperre.

Die bestätigte Nacharbeit vom 09.10.2026 verlangt deutlich handschriftliches
Ausfüllen: Füllung baut sich sichtbar entlang aufeinanderfolgender kurzer, leicht
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

Die bestätigte Tempo-Nacharbeit ersetzt die historischen 140/80/8/120/260 ms
durch **210 ms insgesamt pro Zelle** für
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
| Letzter erfolgreicher Strich | Sofortiger bestehender Abschluss-/Speicher-/Enthüllungspfad; laufende Effekte dürfen enden. Kein neues Warten auf das Animationsende. |
| Pan/Zoom/Resize nach Commit | Aktive und wartende Effekte beenden; keine Eingabe- oder Navigationssperre durch Effekte. |

Während einer linken/rechten Zellgeste bricht das Down der jeweils anderen
Taste die gesamte Vorschau samt Zähler ab, auch außerhalb des Boards innerhalb
des Fensters. Beide zugehörigen Ups werden ohne Commit verbraucht; erst nach
Loslassen beider Tasten darf ein frisches Down wieder eine Zellgeste starten.
Erneutes Down/Bewegung bei noch gehaltener Taste bleibt gesperrt; Escape/Fokusverlust
dürfen weder Phantom-Commit noch hängende Sperre erzeugen. Ein falsches Up ohne
vorheriges Gegentasten-Down bleibt gemäß G1 unbeachtlich. Die mittlere Taste
bewegt nach VS2 ausschließlich überlaufende Hinweisfolgen; Hand- und Rasterpan
entfallen. N04/Zählmöglichkeit ohne Commit ist zurückgestellt.

Animation ist eine transiente Darstellungsschicht. Sie verändert weder Zellen,
History, Hinweislogik, Bewertung noch Saveformat. Effekte sind innerhalb der
jeweiligen Zelle/des Viewports begrenzt; keine springenden Raster oder dauerhaft
bewegten fertigen Markierungen.

### ZS-D09: Abschaltmöglichkeit

Ein einfacher Schalter „Zellanimationen“ schaltet diese Effekte ab.
Ausschalten beendet aktive und wartende Effekte sofort und zeigt den gültigen Endzustand.
Wiedereinschalten wirkt nur auf künftige Strich-Commits; alte Aktionen werden nicht
nachgespielt. Die statische, abgeschwächte Vorschau bleibt unverändert erhalten.

Begrenzter Ausarbeitungsdefault nach bestehendem P1-Vorbild: Der Schalter startet
aktiv und gilt sitzungsweit, auch nach Blattwechsel, Reset und Informationsseite.
Er wird nicht im Rätselsave oder in einem neu eingeführten Einstellungsformat
persistiert und startet nach App-Neustart wieder aktiv. Dies konkretisiert den
begrenzten Prototyp; eine dauerhafte Produkt-Einstellungsarchitektur bleibt separat.
Der Schalter verändert keine Zellen, History, undo_used, Hinweislesepositionen,
Autosaves oder Abschlusslogik. Kein zusätzliches globales Bewegungsmenü oder Zeitregler.

### ZS-D10: Großraster und Nachweise

Der Stil und die Effekte müssen auch an kleinen Zellen, langen Hinweisfolgen,
farbigen 40×40- und 100×100-Rastern sowie stark ausgekreuzten Zuständen funktionieren.
Repräsentative vorhandene Inhalte und der gekennzeichnete F-03-Stressfall bleiben
unverändert. Keine abweichende Rätsellogik oder neue Inhalte zur Erleichterung der Probe.

Technischer Leitfaden: nur laufende visuelle Übergänge verwalten, stabil gezeichnete
Varianten wiederverwenden und den Animationstakt beenden, sobald kein Effekt mehr aktiv ist.
Animationstakte sollen keinen vollständigen UI-/Miniatur-/Analyse-Refresh auslösen.
Die konkrete Umsetzung und Leistung werden nativ gemessen; keine ungeprüfte FPS-Zusage.

Verifikation verbindet Zustands-/Gestenregressionen, gezielte native Bilder zu
bekannten Zeitpunkten, eine kleine Strichsequenz mit Negativkontrollen gegen
gleichmäßiges Fade und falsche X-Zugreihenfolge
und reale schnelle Mauseingaben. Ein Endzustands-Screenshot allein beweist keine
Animation; erfolgreiche Dokumenttests beweisen keine Lesbarkeit oder Eingabeflüssigkeit.

## 5. Lieferpakete und Abnahme

| Paket | Ergebnis | Abhängigkeit und Gate |
| --- | --- | --- |
| ZS-1 | Gewählte Stiftfüllung, neues X und räumlicher Strichaufbau; E2-Fontvergleich, E3-Auswahl Chalkboard und kompaktere 26-px-Zeilenhinweisslots. | PR #55 nach R3 integriert; kombinierte Eigentümersichtprüfung auf main erfolgreich abgeschlossen. |
| ZS-2 | Gewählte Hinweis-/Zellsprache ohne zusätzliche Rand-UI, statische Vorschau, gerichtete Commit-Effekte und Schalter in der regulären Arbeitsansicht. | PR #56 auf `fad8853` integriert, R3 und ZS2-M01 für diesen Vorgänger bestanden. |
| VS2-V1 | Kompakte Zeilenhinweise und ausgewogene Flächenaufteilung einschließlich Miniatur-/Palettenposition. | N01/N02/N04 auf `40829b4` technisch geliefert und in R2 positiv geprüft; V1-Zwischenstand, kombinierte Abnahme offen. |
| VS2-V2 | Subtile Scribble-Linien, Miniatur/Palette und reine Füllminiatur. | N03/N05 freigegeben, noch nicht implementiert; auf der V1-Geometrie, gemeinsame Nachprüfung vor Merge. |
| Z3/#24 | Längere reale Spielerprobung der integrierten neuen Fassung und Abschluss der Designphase. | Nach der integrierten Zielansicht; ersetzt keine davor erforderlichen technischen oder gezielten manuellen Gates. |

ZS-1 verwendete insbesondere F-01/20×20 Mono, F-02/40×40 Farbe und F-03/100×100
für identische Vergleiche. ZS-2 ergänzte die vorhandenen regulären großen RP-6-Inhalte,
darunter F-07/100×100 Farbe. Relevante Flächen bleiben 1280×720, 1600×900,
1920×1080 und 2560×1440 sowie UI 100/125 % und kleine/größere Arbeitszoomstufen.
Gezielte Referenzen statt unnötiger vollständiger Kreuzprodukte; verpflichtende
bestehende Regressionen bleiben aktiv.

Der Spielerdownload bleibt schlank. Maßgeblich ist die aktuelle
[CI-Policy #63](CI_POLICY.md): ausgewählte aktuelle Prüfungen und begrenzte technische
Nachweise, kein allgemeiner Full-Evidence-Schalter und keine historischen Importe
im Standardlauf. Head, Basis/Test-Merge, Run und relevante Datei-Hashes binden die
Nachweise. Quellen-/Nachweis-/Sichtprüfung gehört zu jedem Umsetzungspaket.

## 6. Nichtziele

Keine neue Themen-/Kapitelwahl, Progression, Wertung, Fehlerhilfe, Hypothesen,
Rätselproduktion, Audio, Hintergrundbewegung, aufwendige Abschlussinszenierung,
Engine-/Plattformänderung oder globale Accessibility-/Einstellungsplattform.
Keine Integration alter PRs #25/#28 als Voraussetzung, kein verstecktes Übernehmen
ihrer offenen Befunde. Keine Änderung historischer Designartefakte oder Rätselproofs.

ZS1-M01 ist nach Merge von PR #55 auf `main@985cf08e` am 07.10.2026 vom Eigentümer
bestätigt; #52 ist abgeschlossen. Die [reguläre ZS-2-Integration](ZS2_VERIFICATION.md)
ist über PR #56 abgeschlossen. S0 und die technische V1-Lieferung sind abgeschlossen.
V2, aktuelle kombinierte Nachweise, unabhängiges Review des kombinierten Heads,
VS2-M01 und passende Mergefreigabe bleiben offen. Diese Dokumentationsnacharbeit
implementiert weder V2 noch einen Merge.

## 7. VS2-E1 – kompakte, ausgewogene Scribble-Arbeitsansicht

**Status am 10.10.2026: S0 abgeschlossen; V1/N01/N02/N04 technisch geliefert und
in R2 positiv geprüft; V2/N03/N05 freigegeben, noch nicht implementiert.**
Auftrag und Teilpakete stehen in [#61](https://github.com/venomenon328/picross/issues/61).
Aktuelle V1-Produktreferenz ist `40829b43db6509447863c9d27dbb87dcfaf2a988`
auf Basis `d7ec4e1e4a29d82b6979537a33868d57732d3713`; `2c332ad…` bleibt die
historische reguläre Erstlieferung, nicht die spätere V2-Vergleichsbasis.
Die fünf Regeln bilden eine begrenzte Erweiterung bestehender Fachverträge,
keine zweite P1-Vollspezifikation. Technische Lieferung ist keine persönliche Abnahme.

### VS2-N01: engere Zeilenhinweise – V1 geliefert

Die horizontalen Abstände zwischen den Zahlen derselben Zeilenhinweisfolge betragen
regulär **24 × UI statt 26 × UI**. Ein gemeinsamer regelmäßiger Slotabstand bleibt;
keine variable Einzelpackung, keine kleinere Schrift als Ersatz. Chalkboard und dessen
bestehender Schriftmaßstab bleiben, Spaltenslots weiterhin **18 × UI**. Kandidat A
aus dem vorab gebundenen [V1-Plan](../examples/vs2/v1-plan.json) wurde gewählt.
Reale Zahlen **1/11/17/40**, C1/AA, drei Statuszustände, Marker und kontinuierliche
Draggeometrie bilden den gezielten V1-Glyphennachweis.

**Eigentümerpräzisierung vom 10.10.2026:** Der separate
[V1-Plan-Nachtrag](../examples/vs2/v1-plan-amendment.json), versioniert in `a41cf9b`,
nimmt die synthetische Hinweiszahl **100** aus der V1-Abnahme. Ihre dafür erprobte
Sonderbehandlung ist entfernt. Das ersetzt die frühere Aufzählung 1/11/17/40/100
im aktiven V1-Vertrag; der ursprüngliche Plan bleibt als historischer Nachweis unverändert.
Bestehende 100×100- und andere Großfallregressionen bleiben erhalten. Keine neue
Größenvalidierung, Datenmigration oder erneute Sonderbehandlung folgt daraus.

Rasteransicht erhält mindestens min(5,n) zusammenhängende ganze Zahlen auch zwischen
Snaplagen; Gesamtansicht zeigt sämtliche Hinweise. Vollständige Originalzahlen,
monotone direkte Bewegung, geometrischer Drop, Nachbarlinienunabhängigkeit und
semantische Leseanker bleiben. Parameter und technische Belege stehen in
[VS2_V1_IMPLEMENTATION.md](VS2_V1_IMPLEMENTATION.md) und im commitgebundenen PR.

### VS2-N02: ausgewogene belegte Arbeitsfläche – V1 geliefert

Nach der Fit-/Kapazitätsberechnung werden Raster und beide Hinweisflächen als ein
belegter Block bei ausreichender Restbreite weiter Richtung Mitte der nutzbaren
Papierarbeitsfläche platziert. Maßgeblich ist die Fläche ohne sichere Miniatur-/
Palettengruppe und andere Controls, nicht blind die ganze Fenstermitte.
Bei knapper Breite haben vollständige Inhalte und Bedienbarkeit Vorrang.

Reihenfolge: tatsächliche Mindestreserven und Fit, GF1-Zusatzkapazität für vollständige
Zeilenhinweise, danach Ausgleich des verbleibenden Freiraums. Nicht durch künstliche
leere Hinweisslots, Kürzen sichtbarer Zahlen, kleinere gewählte Zellen oder Schrift
zentrieren. Der Anordnungsschritt darf die gültige Fitgrenze nicht nochmals senken.
Alle Hinweise, Rasterdarstellung, Cursor-/Gestenabbildung und Hit-Tests teilen den
Versatz. Fortschritt, H1-Status oder Hinweisdrag ändern die Anordnung nicht.

F-01 und geeignete VS09-Breitenfälle dienen als reproduzierbare Freiraumbeispiele;
VS08/VS04 und knappe Flächen sichern die Kapazitätsgrenzen. Die Chatbezeichnung
„Analyseausgabe 1“ ist keine eindeutig identifizierte Datei und keine Pflichtquelle.

### VS2-N03: subtile, stabile handgezeichnete Elemente – V2 offen

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

Miniatur samt Fassung und Farbauswahl erhalten dieselbe zurückhaltende Scribble-Sprache.
Miniaturfüllungen bleiben vereinfachte ruhige Farbformen, keine dominante Mikroschraffur.
Palettenfarb-IDs und Originalfarbflächen bleiben eindeutig; Auswahl, Hover und Fokus
müssen erkennbar sein, ohne neue Rätselfarben vorzutäuschen. Die optische Strichkante
verkleinert oder verzerrt keine Hitbox. Fraunces/Plex und das A-Hintergrundbild bleiben.
„Kleine Vorschau“ bezeichnet hier die Miniatur; die statische Zielvorschau im Raster
bleibt ebenfalls stilistisch konsistent, aber ohne neu eingeführte Bewegung.

### VS2-N04: Miniatur-/Palettengruppe mit Buchrandabstand – V1 geliefert

V1 verschiebt die vorhandene Gruppe im großzügigen Referenzfall um **(−16, +24) × UI**
nach links/unten; knappe Flächen begrenzen den Abwärtsversatz. Fassung, Halterungen,
Beschriftungen und Auswahlmarkierungen werden mitgeführt; sichtbar Abstand zum
oberen/rechten Buchrand, keine angeschnittenen Konturen. Gemeinsam mit N02 bleiben
Raster/Hinweise, Navigation, Koordinaten, Werkzeuge und Save-/Recoverymeldungen frei.
Keine Verkleinerung als Ersatz; Mindesthitflächen von **44/55 px bei UI100/125** bleiben.
Die tatsächlichen neuen Strichränder aus V2 sind erneut gegen diese V1-Anordnung
zu prüfen; V1s alte Pixelbilder nehmen die kombinierte Abnahme nicht vorweg.

### VS2-N05: reine Füllprojektion der Miniaturen – V2 offen

ZS-D05 ist der neue Miniaturvertrag: ausschließlich eigene Füllungen einschließlich
bereits bestehender Vorschau, keine X/Punkte/Leer-Ersatzzeichen. Unbekannt und X
haben denselben neutralen Miniaturhintergrund. Zwei Stände mit identischen Füllungen
und unterschiedlichen X/unbekannt ergeben dasselbe Miniaturbild.

Der logische Zellzustand, X im Hauptraster, History/Redo, H1/GP-48, Speicherformat
und Abschluss ändern sich nicht. Eigene fehlerhafte Füllungen bleiben sichtbar.
Füllung↔X-/Neutralisierungsvorschau, Rückzug, Abbruch, Undo/Redo und Neustart müssen
die reine Projektion unmittelbar erhalten; keine Lösungskorrektur und kein früher Reveal.
Vorhandene ungelöste Albumminiaturen folgen derselben Projektion; keine neue Album-UI.

### Geltung gegenüber älteren Fachtexten und Abnahme

Die ausdrückliche Eigentümerfreigabe ersetzt gezielt D-33/ZS1-E3 als unveränderliche
horizontale 26er-Zielweite und die frühere linke Anordnung/Positionierung durch V1.
Die Ablösung ausschließlich mathematisch gerader sichtbarer Rasterstriche, der
bisherigen Miniatur-/Palettenfassung und der Dreizustandsdarstellung in Miniaturen
ist dagegen weiterhin **V2-Sollstand**. Dies gilt entsprechend für
[Produktdefinition](PRODUCT_DEFINITION.md) §§3.3/5,
[Gestaltungskonzept](DESIGN_CONCEPT.md) §§2/4.1/4.4/5.1,
[P1](PROTOTYPE_P1.md) D-29/D-33 und §5.2 sowie die betroffenen Z2-Auswahlpassagen.
Deren nicht ersetzte Regeln bleiben verbindlich; **logische Regelmäßigkeit,
Präzision und die drei Spielzustände sind ausdrücklich nicht abgelöst**.

Historische Pläne, Proofs, Asset-/Fonthashes, Bilder, Abnahmen und Reports bleiben
unverändert. Der separate V1-Nachtrag und die aktuelle Statuskonsolidierung ändern
keine historischen Ergebnisdaten. R1 gilt für `2c332ad`, R2 für `40829b4`; keiner
nimmt V2 oder die persönliche kombinierte Abnahme vorweg. Bei V2 sind Bedienhilfe
und betroffene Pixel-/Strichoracles konsistent nachzuführen.

V1/NA01/NA02/NA04 ist technisch geprüft; V2/NA03/NA05 und die kombinierte Regression
bleiben offen. Aktuelle Nachweiszuordnung steht in [VS2_VERIFICATION.md](VS2_VERIFICATION.md),
Vorbereitung und Auftrag in #61. Vor V2-Vergleichen eine eigene endliche Planung
binden, ohne ursprünglichen VS2-/V1-Plan zu überschreiben. Beide Teilpakete bleiben
in PR #62, mit kombinierter technischer/visueller Prüfung und VS2-M01 vor einem
gesondert freizugebenden Merge.
