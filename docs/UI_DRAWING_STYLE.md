# Zeichnerische Spieloberfläche und Zellanimationen

Stand: 07.10.2026 · Spezifikation 0.4 · E3: Chalkboard/Stift/Timing gewählt; kompakte Zeilenhinweise festgelegt

## 1. Auftrag, Quellen und Status

Der Eigentümer hat am 07.10.2026 die besprochene Weiterentwicklung des Buchdesigns
als Spezifikation freigegeben und ihre Übernahme in Issues und Repository-Dokumente
beauftragt. Seine letzte Präzisierung ist verbindlich: Die Vorschau während einer
Zellgeste bleibt statisch und heller beziehungsweise transparenter; Zellanimationen
beginnen erst beim tatsächlichen Anwenden des Strichs. Die frühere Empfehlung,
bereits während des Ziehens zu animieren, ist ausdrücklich verworfen.

Dieses Dokument beschreibt die dauerhaften Gestaltungs- und Darstellungsverträge.
[ZS-1](https://github.com/venomenon328/picross/issues/52) liefert die native
Vergleichsprobe und konkrete Auswahl, [ZS-2](https://github.com/venomenon328/picross/issues/53)
integriert die gewählte Fassung. Beide gehören zu
[Zieldesign #21](https://github.com/venomenon328/picross/issues/21);
[Z3/#24](https://github.com/venomenon328/picross/issues/24) bleibt die anschließende
längere Spielerprobung. Paketstatus, Lieferhead, Nachweise und Abnahme stehen in den
Issues/PRs. Spezifikationsfreigabe ist weder Produktimplementierung noch Mergefreigabe.

Ausgangsbasis ist main ec99954268f1ad959d9ea779dbbd9e28edf7d8fa mit integriertem
Z2, GP-48, ZV-50 und RP-6. Vor einer späteren Ausführung den dann aktuellen Stand
prüfen. [AGENTS.md](../AGENTS.md), [lokaler Workflow](dev-rules/WORKFLOW.md),
[Projektprofil](PROJECT_PROFILE.md), [Produktdefinition](PRODUCT_DEFINITION.md),
[Gestaltungskonzept](DESIGN_CONCEPT.md), [P1-Vertrag](PROTOTYPE_P1.md) und
[aktive Z2-Auswahl](Z2_SELECTION.md) bleiben Pflichtquellen im jeweiligen Geltungsbereich.

[Eigentümerentscheidung ZS1-E1](https://github.com/venomenon328/picross/pull/55#issuecomment-6040480659)
konkretisiert die Auswahl: Stiftfüllung und kurzes Timing sind gewählt. N01–N06
ersetzen die offene Tinte-/Stiftwahl, frühere Fraunces-Hinweiskandidaten, bloßes Fade
und zusätzliche Rand-UI. R1 bleibt an `4ae4f5a20273808f99d257a3812da86d72307a5f`
gebunden. [Fontinput](ZS1_FONT_INPUT.md): beide Original-TTFs samt Nutzungshinweisen durch
[ZS1-E2](https://github.com/venomenon328/picross/pull/55#issuecomment-6042067344)
für die beauftragte Studienlieferung akzeptiert; zusätzliche Lizenztexte sind kein Startblocker.


[Eigentümerentscheidung ZS1-E3](https://github.com/venomenon328/picross/pull/55#issuecomment-6043750653)
wählt **Chalkboard Regular** als Hinweisfont und reduziert die gemeinsame horizontale
Slotweite der Zeilenhinweise links vom Raster auf **26 logische Pixel bei UI 100 %**
(UI-skaliert). Die Spaltenhinweise bleiben bei 18 logischen Pixeln. Der Eigentümer
hat die Mergefreigabe ausdrücklich vor die kombinierte Sichtprüfung gezogen: Die
visuelle Gesamtprüfung wurde anschließend auf `main@985cf08e` erfolgreich
abgeschlossen und am 07.10.2026 bestätigt; #52 ist abgeschlossen.

## 2. Ziel und begrenzte Ablösung

Das Spielen soll wie das Bearbeiten eines gezeichneten Rätselbuchs wirken.
Hinweisziffern, Zellmarkierungen, Werkzeuge und Umgebung erhalten eine zusammengehörige
Handschrift. Das Raster bleibt geometrisch präzise; seine visuelle Gestaltung darf
charaktervoll und spielerisch sein. Die frühere pauschale Forderung nach einem
sachlichen Raster bedeutet für diesen Schritt keine sterile Darstellung mehr.

Der bereitgestellte Squeakross-Screenshot dient ausschließlich als Qualitätsvergleich.
Keine Nachbildung seiner Oberfläche, Anordnung, Palette, Figuren oder Zellmotive;
keine Übernahme fremder Assets. Die Vergleichsbilder im Chat sind keine Pflichtassets
oder mathematischen Rätseldaten für die spätere Umsetzung.

Die gewählte A-Buchkomposition bleibt Grundlage. GD-03/GP-03 werden nur für die
gezielte Untersuchung der Hinweisziffern geöffnet: Schriftform, Gewicht, optischer
Schriftgrad und gegebenenfalls bewusst gewählte gemeinsame Slotmaße. Fraunces-Titel,
Plex-Sans-Bedientexte, die übrige Z2-Komposition und die C1-Farbkontur bleiben Grundlage.
Eine neue allgemeine Hintergrund-, Schrift- oder Layoutauswahl ist nicht beauftragt.

Die Stiftfüllung ist gewählt. Der enge E2-Vergleich enthielt Bakso Daging Regular
und Chalkboard Regular; E3 wählt **Chalkboard Regular**. Bakso Daging und Plex bleiben
nur Vergleichsreferenzen der Studie. Für Chalkboard verwendet die gewählte Fassung
kompaktere gemeinsame Zeilenhinweisslots von 26 logischen Pixeln bei UI 100 %;
die vertikalen Spaltenslots bleiben 18 Pixel. Historische Tinte-/Stiftbilder und R1/R2
bleiben Referenzen ihrer Lieferstände, keine erneut offene Grundsatzwahl.

## 3. Zeichensprache

### ZS-D01: Hinweiszahlen

Kräftige, kompakte Ziffern mit klaren Innenräumen und höherem optischem Flächenanteil
im verfügbaren Platz. Zuerst Form, Gewicht und optische Größe untersuchen; bloßes
Einschalten von Fettdruck reicht als Lieferziel nicht. Die Ausgangsfassung fordert
bereits Plex-Sans-Gewicht 600 an. Dessen sichtbare Wirkung muss nativ beurteilt werden.

Keine absichtlich schwer lesbare Handschrift, verzogenen Ziffern oder zufälligen
Zeichenabstände. Ein- und mehrstellige Zahlen bis zu den vorhandenen 100er-Fällen
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


**E3 / konkrete Hinweisgeometrie:** Chalkboard Regular ist gewählt. Im Buchlayout
verwenden die Zeilenhinweise links vom Raster gemeinsame horizontale Slots von
**26 × UI-Skalierung** statt 30 × UI-Skalierung. Die Spaltenhinweise oberhalb des
Rasters bleiben bei **18 × UI-Skalierung**. Die kompaktere Zeilenstaffel ändert
weder Slotprinzip noch Marker-, Drag-, Snap-, Tooltip- oder gespeicherte
Lesepositionssemantik.

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
der Zellidentität; Neuzeichnen, Pan, Zoom und Wiederherstellung würfeln nichts neu. Kreuze bleiben eindeutig, übertönen aber auch auf einem stark
ausgekreuzten Blatt das gefüllte Motiv nicht. Unbekannt, X und Füllung sind
unmittelbar unterscheidbar. Normale und teilweise sichtbare Zellen verwenden
dieselbe Geometrie mit korrektem Anschnitt; keine Ersatzmarkierung am Viewportrand.

### ZS-D04: Buch und funktionale UI ohne zusätzliche Randdekoration

Die zusätzliche Studien-Randdekoration wird nach E1/N05 entfernt. Funktionale
Buchmontierungen, Werkzeuge und Miniaturfassung bleiben erhalten. Eine spätere
Hintergrundbildanpassung ist zurückgestellt, kein aktueller Assetauftrag und kein
Gate für #52/#53. Hintergrund und historische Artworkpakete bleiben unverändert.

Hinweise und Raster erhalten einen ruhigen Untergrund. Dekoration gibt weder
Motivnamen noch eine vorzeitige Skizze der Lösung preis und enthält keine eingebrannten
Bedienattrappen, Fülltexte oder Pseudoschrift. Bei engeren Ansichten beziehungsweise
höherem Zoom tritt sie zugunsten der Arbeitsfläche zurück. ZV-50-Flächennutzung und
die Erreichbarkeit aller bestehenden Werkzeuge werden nicht eingeschränkt.
Historische hashgebundene Designpakete bleiben unverändert; neue Lieferassets sind
gesondert nach Herkunft, Rechten und Version zu dokumentieren.

### ZS-D05: Miniatur

Die Miniatur zeigt unmittelbar den eigenen logischen Spielerzustand einschließlich
der aktuellen elastischen Vorschau und möglicher Fehler. Sie bleibt unanimiert und
verwendet eine vereinfachte Darstellung ohne verkleinerte Schraffurdetails oder
Animationszwischenbilder. Unbekannt, X und Füllung bleiben unterscheidbar.
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

### ZS-D07: Commit und parallele Effekte

Erst das tatsächliche Anwenden bei Mouse-Up startet die kurze Zellanimation.
Einzelklicks bleiben Striche der Länge eins. Alle effektiv geänderten Zellen eines
Strichs erhalten denselben Animationsstart; keine Sequenz pro Zelle, künstliche
Warteschlange oder mit der Strichlänge wachsende Gesamtdauer.
Geschützte Felder und No-ops lösen keine Animation aus.

Füllung baut sich räumlich entlang aufeinanderfolgender kurzer Stiftzüge auf;
das X zeichnet erst den ersten, dann den zweiten Zug. Bloßes globales Fade oder
bewegte Dekorstriche auf schon kräftiger Endfüllung genügen nicht. Die kräftige
Markierung wird über den zurückgenommenen statischen Zielzustand gezeichnet. Sie verschwindet nicht erst vollständig für einen
zweiten Aufbau. Beim Neutralisieren darf eine zuvor entfernte Füllung oder ein X
nicht nochmals als Löschanimation auftauchen; stattdessen kann die Vorschaukontur
oder ein neutraler kurzer Löschhinweis auslaufen.

Das positiv beurteilte kurze Timing bleibt bei **140 ms insgesamt** für
Setzen/Umwandeln und **80 ms** Entfernen. Teilzüge innerhalb einer Zelle folgen
aufeinander; alle wirksamen Zellen starten gleichzeitig. Keine 140 ms pro Teilzug.

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
| Escape/Fokusverlust | P1-Abbruchregel erhalten; statische Vorschau sofort verwerfen. Rein visuelle Restzustände dürfen beendet werden. |
| Blattwechsel, Reset, Restore, Album/Informationsseite | Keine Effekte in eine andere Session übertragen, speichern oder beim Wiederöffnen erneut abspielen. Bestehender Abbruch-/Flush-/Recoveryvertrag bleibt. |
| Letzter erfolgreicher Strich | Sofortiger bestehender Abschluss-/Speicher-/Enthüllungspfad; laufende Effekte dürfen enden. Kein neues Warten auf das Animationsende. |
| Pan/Zoom/Resize nach Commit | Effekte bleiben der richtigen Zelle und aktuellen Geometrie zugeordnet oder werden sauber beendet; keine Eingabe- oder Navigationssperre durch Effekte. |

Animation ist eine transiente Darstellungsschicht. Sie verändert weder Zellen,
History, Hinweislogik, Bewertung noch Saveformat. Effekte sind innerhalb der
jeweiligen Zelle/des Viewports begrenzt; keine springenden Raster oder dauerhaft
bewegten fertigen Markierungen.

### ZS-D09: Abschaltmöglichkeit

Ein einfacher Schalter „Zellanimationen“ schaltet diese Effekte ab.
Ausschalten beendet laufende Effekte sofort und zeigt den gültigen Endzustand.
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
| ZS-1 | Gewählte Stiftfüllung, neues X und räumlicher Strichaufbau; E2-Fontvergleich, E3-Auswahl Chalkboard und kompaktere 26-px-Zeilenhinweisslots. | PR #55 ist nach R3 integriert; kombinierte Eigentümersichtprüfung auf main erfolgreich abgeschlossen. |
| ZS-2 | Gewählte Hinweis-/Zellsprache ohne zusätzliche Rand-UI, statische Vorschau, parallele Commit-Effekte und Schalter in der regulären Arbeitsansicht. | ZS-1-Auswahl und integrierte nutzbare Grundlage; aktuelle technische Nachweise, unabhängiges Review und gezielte reale Eigentümerprobe vor Merge. |
| Z3/#24 | Längere reale Spielerprobung der integrierten neuen Fassung und Abschluss der Designphase. | Nach ZS-2; ersetzt keine davor erforderlichen technischen oder gezielten manuellen Gates. |

ZS-1 verwendet insbesondere F-01/20×20 Mono, F-02/40×40 Farbe und F-03/100×100
für identische Vergleiche. ZS-2 ergänzt die vorhandenen regulären großen RP-6-Inhalte,
darunter F-07/100×100 Farbe. Relevante Flächen sind 1280×720, 1600×900,
1920×1080 und 2560×1440 sowie UI 100/125 % und kleine/größere Arbeitszoomstufen.
Gezielte Referenzen statt unnötiger vollständiger Kreuzprodukte; verpflichtende
bestehende Regressionen bleiben aktiv.

Der Spielerdownload bleibt schlank. Technische Vergleiche und der kleine
Bewegungsnachweis liegen getrennt in gezielten Reviewartefakten; vollständige
Arbeitsrender werden weiterhin nur über den bestehenden optionalen Vollnachweis
veröffentlicht. Head, Basis/Test-Merge, Run und relevante Datei-Hashes binden die
Nachweise. Quellen-/Nachweis-/Sichtprüfung gehört zu jedem Umsetzungspaket.

## 6. Nichtziele

Keine neue Themen-/Kapitelwahl, Progression, Wertung, Fehlerhilfe, Hypothesen,
Rätselproduktion, Audio, Hintergrundbewegung, aufwendige Abschlussinszenierung,
Engine-/Plattformänderung oder globale Accessibility-/Einstellungsplattform.
Keine Integration alter PRs #25/#28 als Voraussetzung, kein verstecktes Übernehmen
ihrer offenen Befunde. Keine Änderung historischer Designartefakte oder Rätselproofs.

ZS1-M01 ist nach Merge von PR #55 auf `main@985cf08e` am 07.10.2026 vom Eigentümer erfolgreich abgeschlossen und die Kombination bestätigt. #52 ist abgeschlossen. Die [reguläre ZS-2-Integration](ZS2_VERIFICATION.md) ist separat beauftragt; ZS2-M01, unabhängiges aktuelles Review und Mergefreigabe bleiben vor Merge offen. Kein Release. E1 ersetzt gezielt die genannten Teile des alten #54-Vertrags; die übrigen
P1-/ZS-Invarianten bleiben erhalten.
