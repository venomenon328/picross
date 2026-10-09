# VS-D01 · bestätigte Vollsichtstrategie

## Aktueller Stand · VS2-Erstlieferung und VS2-E1

VS2 überträgt die entschiedene Strategie samt GF1 auf den regulären Pfad.
Die Erstlieferung liegt in [Draft-PR #62](https://github.com/venomenon328/picross/pull/62)
auf `2c332ad688315bfa851f7c0d8642d2ab4ac3709c`; sie ist noch nicht gemergt.
[Review R1](https://github.com/venomenon328/picross/pull/62#pullrequestreview-5472592800)
ist für diesen Stand abgeschlossen. Nachfolgend bestätigte der Eigentümer
**VS2-E1 als Spezifikation**, noch nicht als Implementierung oder Abnahme.
Der neue [Darstellungsvertrag](UI_DRAWING_STYLE.md) §7 ergänzt kompakte Zeilenhinweise,
ausgewogene Platzierung und eine konsequentere Scribble-Optik mit reiner Füllminiatur.
VS-D01 selbst wird dadurch nicht erneut zur Wahl gestellt.

Bedien-/Speichergrundlage: [P1](PROTOTYPE_P1.md). Die
[Prüfzuordnung](VS2_VERIFICATION.md) und [Windows-Probe](VS2_OWNER_TRIAL.md)
trennen alte Nachweise und neue offene Kriterien. VS2-M01 hat Änderungsfeedback,
ist nicht vollständig positiv abgenommen. Vor Merge bleiben die neue Nacharbeit,
aktuelle technische Prüfung, unabhängiges Review des neuen Heads, VS2-M01 und
passende Mergefreigabe nötig. Historische VS-M01-Langzeitbefunde bleiben persönlich
unvollständig; keine rückwirkende Abnahme alter oder neuer Komfortfälle.

Stand: 09.10.2026 · Entscheidung 1.1 · VS-D01 bestätigt, VS2-E1 ergänzend spezifiziert

Maßgebliche Strategieentscheidung: [#57 §1](https://github.com/venomenon328/picross/issues/57)
unter [Zieldesign #21](https://github.com/venomenon328/picross/issues/21).
Der Eigentümer hat Option A mit format- und hinweisabhängiger Eignungsprüfung
bestätigt. VS-D01 ist entschieden und benötigt keine erneute Grundsatzfreigabe.

## Beschlossene Richtung

Reguläre Einzelrätsel folgen dem Vollsichtziel: das ganze Raster einschließlich
äußerem Rahmen bleibt sichtbar, ohne erforderliches manuelles Rasterverschieben.
40×40 bleibt das Ziel; mindestens 30×30 muss brauchbar erreichbar bleiben.
Kleinere Rätsel sind weiterhin möglich. 40×30 und geeignete 50×30 sind
gleichberechtigte Formate (Spalten × Zeilen). 30×40 braucht eine eigene
Eignungsprüfung; daraus folgt keine Zusage für 50×40 oder 50×50.

1080p ist als maßgebliches Mindestziel beziehungsweise spätere Mindestauflösung
akzeptiert. Tatsächliche Fensterclientfläche, Windows-Skalierung und UI-Skalierung
werden getrennt geprüft. Kein Vollbildzwang. 720p bleibt zusätzlicher Befund/Fallback
und darf die angestrebte Größenkapazität nicht unter 30×30 reduzieren.

Rasteransicht (interne bisherige Kennung G) ist die bevorzugte Bedienrichtung:
ganzes Raster und mindestens min(5,n) zusammenhängende vollständige tatsächliche
Zahlen pro Hinweisfolge, mit unabhängiger Hinweisbewegung bei Bedarf. Fünf ist eine
Untergrenze. Kurze Folgen beanspruchen nur ihren tatsächlichen Bedarf; zusätzliche
verfügbare Breite darf mehr Zahlen zeigen. Die Gesamtansicht mit allen Hinweisen
(bisher V) bleibt ergänzend. Ihre größere Hinweislast und gegebenenfalls kleinere
Zellen sind kein alleiniger Maßstab der praktischen Nutzbarkeit der Rasteransicht.
Die benannte Auswahl liegt ausschließlich in den Einstellungen, nicht im Arbeitsbild.

Sehr große Rätsel, beispielsweise um 60×60/100×100, bleiben perspektivisch als
Sonderkategorie mit gesonderter Navigation möglich. Keine konkrete Menge, neue
Kategorie-UI oder Navigation ist dadurch implementiert. Die frühere pauschale
Forderung nach einem substanziellen regulären Bestand jenseits 40×40 und um 100×100
ist durch diese reguläre Vollsicht-Zielrichtung präzisiert/abgelöst.

Format, tatsächliche Hinweislast, verfügbare Fläche, lesbare vollständige Ziffern
und belegte Bedienbarkeit entscheiden gemeinsam. Geometrischer Fit ist keine
persönliche Komfortabnahme, Zellzahl keine Schwierigkeit und zehn Beispiele keine
allgemeine Kataloggarantie. Genaue Verteilung, Langzeitkomfort und Sondernavigation
bleiben Folgearbeit, ohne VS-D01 erneut zu öffnen.

## Ergänzende Anordnungsentscheidung VS2-E1

Die horizontalen Zeilenhinweisslots werden gegenüber der 26-×-UI-Erstlieferung
sichtbar enger, ohne kleinere Hinweisziffern als Ersatz. Gemeinsame Slots, vollständige
Zahlen, Mindestfünfergarantie, Status-/Marker-/Drag-/Snapregeln und 18-×-UI-Spaltenslots
bleiben. Der konkrete engere Wert wird in der späteren Umsetzung nativ begründet.

Auf der sicheren Papierarbeitsfläche gilt weiterhin: Mindestreserven und Fit zuerst,
zusätzliche vollständige Zeilenkapazität anschließend. **Danach** wird bei übrigem
horizontalem Freiraum der ganze belegte Raster-/Hinweisblock ausgewogener Richtung
Mitte dieser Arbeitsfläche platziert. Keine künstlichen leeren Hinweisslots, keine
reduzierte Hinweiskapazität oder weitere Fit-/Schriftverkleinerung zum Zentrieren.
Miniatur-/Palettengruppe wird etwas nach unten/links mit Abstand zum Buchrand
angeordnet; ihre realen Flächen und die übrigen Controls begrenzen den Arbeitsraum.
Zeichnung und Eingabe teilen die neue Anordnung; kein manuelles Pan oder Springen
aufgrund von Zell-/Hinweiszuständen. Details und Ablösung älterer Positionswerte:
[UI_DRAWING_STYLE.md, VS2-E1/N01–N04](UI_DRAWING_STYLE.md).

Die subtil handgezeichneten Rasterstriche ändern keine logischen Zellkoordinaten;
ihre tatsächlichen Zeichenränder gehören zum Vollsichtnachweis. Die passive
Miniatur zeigt gemäß N05 nur eigene Füllungen, einschließlich Fehlern und bestehender
Vorschau, nicht X/Leerzeichen oder eine korrigierte Lösung. Dies ist spezifiziert,
noch nicht im Produkt umgesetzt. Kein neuer Navigations- oder Katalogauftrag.

## Integration und aktuelles Paket

VS-1 wurde über [PR #58](https://github.com/venomenon328/picross/pull/58) am 08.10.2026
als `c19b3547eef81fbb7c3c5389834f7cc896c86069` integriert. Lieferhead
`7a0ebf65e1d14b3aa693f155c9de329de21603a5`, unabhängiges R3, sechs erfolgreiche
Pflichtjobs und die konkrete Mergefreigabe bleiben historische Nachweise.
Der Eigentümer hat positive Sichtbeobachtungen abgegeben; das umfassende
VS-M01-Protokoll ist dennoch nicht vollständig persönlich durchgeführt.

[VS-GF1/#59](https://github.com/venomenon328/picross/issues/59) erweiterte ausschließlich
die horizontale G-Flächenverteilung der integrierten Studie. Mindestreserve und
Fit zuerst, zusätzliche sichere Zeilenkapazität anschließend; unveränderter
Lesemaßstab, obere Reserve, vollständiger Rahmen und semantische Fortsetzung.
Der eigene [Prüfplan](../examples/vs1/gf1-plan.json) und die
[Prüfzuordnung](VS1_VERIFICATION.md) binden die technische Lieferung.
GF-M01 und das Review von #59 sind nach PR #60 abgeschlossen; maßgeblich ist
[die abschließende Klarstellung](https://github.com/venomenon328/picross/pull/60#issuecomment-6076039228).
#53 einschließlich N01–N03 ist über PR #56 integriert. VS2/#61 überträgt diese
Vollsicht auf die reguläre Hauptszene. Die neun Inhalte und der 720p-Fallback
bleiben erhalten; manuelle Raster-/Miniaturnavigation entfällt. Die neuen Teilpakete
VS2-V1 und VS2-V2 bleiben in PR #62. Ihre Gates stehen in der Prüfzuordnung;
historische Freigaben gelten nur für ihren jeweiligen Head.

## Herkunft und historische Daten

Die ausdrückliche Zustimmung nach Integration von #58 und der anschließende Wunsch
nach besserer Nutzung freier Breite sind in den Bodies von #57/#59 konsolidiert.
VS2-E1 aus der jüngeren Eigentümerfreigabe wird im aktuellen #61 und diesem
Darstellungsvertrag ergänzt. Beschriebene Screenshots sind persönliche Sichtbefunde,
keine erfundenen vollständigen Lösungen, Zeitmessungen oder DPI-Abnahmen.
Alte Reports, `manifest.json`, `production.json`, `plan-vb1.json` und die endliche
E1-initial/correction-1/correction-2-Reihe bleiben bytegebundene historische
Nachweise. Ihre damaligen offenen Entscheidungsfelder werden nicht nachträglich
überschrieben. Aktuelle Berichte referenzieren die neue Entscheidung separat;
[GF-M01-Protokoll](../examples/vs1/gf1-owner-protocol.json) bleibt als historische
Lieferdatei unausgefüllt, die spätere positive GF-M01-Bestätigung bleibt maßgeblich.
