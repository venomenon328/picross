# VS-D01 · Vollsichtstrategie

## Geltung und Zuständigkeit

Dieses Dokument führt die bestätigte Strategie für reguläre Einzelrätsel.
Es bestimmt Größenrichtung und Eignungsmaßstab, keine feste Hinweisgeometrie.
Die Entscheidung stammt aus [#57](https://github.com/venomenon328/picross/issues/57)
und [#59](https://github.com/venomenon328/picross/issues/59). Die Regeln im aktuellen
Git-Stand sind der Fachvertrag; Implementierung, Review und persönliche Abnahme
werden am jeweiligen Head im zuständigen Issue/PR nachgewiesen.

| Detail | Maßgebliche Quelle |
| --- | --- |
| Spiel, Vollsicht, gewünschter Zoom und Speicherung | [P1](PROTOTYPE_P1.md) |
| Hinweisfont, gemessene Slots und Fit | [Hinweistypografie](CLUE_TYPOGRAPHY.md) |
| Freiraumverteilung und sichtbare Rasterlinien | [Zeichensprache · VS2-N02/N03](UI_DRAWING_STYLE.md) |
| Miniatur, Palette und Werkzeuge | [Sidebar](SIDEBAR.md) |
| Fenster-/UI-Konfigurationen | [Anzeigeeinstellungen](DISPLAY_SETTINGS.md) |

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
ganzes Raster und zusammenhängende vollständige Hinweisfenster mit unabhängiger
Hinweisbewegung bei Bedarf. Mindestanzahl, tatsächlicher Bedarf und Nutzung
zusätzlicher Breite folgen der [Hinweisgeometrie](CLUE_TYPOGRAPHY.md#zusammenhängende-geometrie).
Die Gesamtansicht mit allen Hinweisen
(bisher V) bleibt ergänzend. Ihre größere Hinweislast und gegebenenfalls kleinere
Zellen sind kein alleiniger Maßstab der praktischen Nutzbarkeit der Rasteransicht.
Die benannte Auswahl liegt ausschließlich in den Einstellungen, nicht im Arbeitsbild.

Sehr große Rätsel, beispielsweise um 60×60/100×100, sind eine Perspektive für
eine gesonderte Navigation. Der aktuelle Produktumfang richtet sich nach der
[Produktdefinition](../project/PRODUCT_DEFINITION.md); diese Perspektive erweitert ihn nicht. Die frühere pauschale
Forderung nach einem substanziellen regulären Bestand jenseits 40×40 und um 100×100
ist durch diese reguläre Vollsicht-Zielrichtung präzisiert/abgelöst.

Format, tatsächliche Hinweislast, verfügbare Fläche, lesbare vollständige Ziffern
und belegte Bedienbarkeit entscheiden gemeinsam. Geometrischer Fit ist keine
persönliche Komfortabnahme, Zellzahl keine Schwierigkeit und zehn Beispiele keine
allgemeine Kataloggarantie. Genaue Verteilung, Langzeitkomfort und Sondernavigation
bleiben Folgearbeit, ohne VS-D01 erneut zu öffnen.

## Ergänzende Anordnungsentscheidung VS2-E1

Die konkrete Arbeitsflächenverteilung und Scribble-Zeichnung stehen ausschließlich
in [UI_DRAWING_STYLE](UI_DRAWING_STYLE.md), die heutige Hinweisgeometrie in
[CLUE_TYPOGRAPHY](CLUE_TYPOGRAPHY.md). Historische Chalkboard-/26-/24-/18-Werte
sind keine parallelen Zielmaße. Die Sidebarposition folgt ihrem eigenen Vertrag.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#57](https://github.com/venomenon328/picross/issues/57), [#59](https://github.com/venomenon328/picross/issues/59) und [#61 / PR #62](https://github.com/venomenon328/picross/pull/62).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/VS1_DECISION.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
