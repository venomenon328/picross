# VS-D01 · bestätigte Vollsichtstrategie

## Aktueller regulärer Stand · VS2 (#61)

VS2 überträgt die entschiedene Strategie samt GF1 auf den regulären Pfad.
Historische VS-M01-Langzeitbefunde bleiben persönlich unvollständig. Die neue
Integration ist keine rückwirkende Abnahme alter oder neuer Komfortfälle.

Bedien-/Speichervertrag: [P1](PROTOTYPE_P1.md). Aktuelle
[Prüfzuordnung](VS2_VERIFICATION.md) und [Windows-Probe](VS2_OWNER_TRIAL.md).
VS2-M01, unabhängiges technisches/visuelles Review und passende Mergefreigabe
bleiben vor Merge offen. Historische Nachweise bleiben commitgebunden.


Stand: 09.10.2026 · Entscheidung 1.0 · ausdrücklich angenommen durch den Eigentümer

Maßgebliche Entscheidung: [#57 §1](https://github.com/venomenon328/picross/issues/57)
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

G ist die bevorzugte Bedienrichtung: ganzes Raster und mindestens min(5,n)
zusammenhängende vollständige tatsächliche Zahlen pro Hinweisfolge, mit unabhängiger
Hinweisbewegung bei Bedarf. Fünf ist eine Untergrenze. Kurze Folgen beanspruchen nur
ihren tatsächlichen Bedarf; zusätzliche verfügbare Breite darf mehr Zahlen zeigen.
V bleibt die ergänzende vollständige Blattansicht mit allen Hinweisen. Ihre größere
Hinweislast und gegebenenfalls kleinere Zellen sind kein alleiniger Maßstab der
praktischen G-Nutzbarkeit.

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

## Integration und aktuelles Paket

VS-1 wurde über [PR #58](https://github.com/venomenon328/picross/pull/58) am 08.10.2026
als `c19b3547eef81fbb7c3c5389834f7cc896c86069` integriert. Lieferhead
`7a0ebf65e1d14b3aa693f155c9de329de21603a5`, unabhängiges R3, sechs erfolgreiche
Pflichtjobs und die konkrete Mergefreigabe bleiben historische Nachweise.
Der Eigentümer hat positive Sichtbeobachtungen abgegeben; das umfassende
VS-M01-Protokoll ist dennoch nicht vollständig persönlich durchgeführt.

[VS-GF1/#59](https://github.com/venomenon328/picross/issues/59) erweitert ausschließlich
die horizontale G-Flächenverteilung der integrierten Studie. Mindestreserve und
Fit zuerst, zusätzliche sichere Zeilenkapazität anschließend; unveränderter
Lesemaßstab, obere Reserve, vollständiger Rahmen und semantische Fortsetzung.
Der eigene [Prüfplan](../examples/vs1/gf1-plan.json) und die
[Prüfzuordnung](VS1_VERIFICATION.md) binden die technische Lieferung.
GF-M01 und das Review von #59 sind nach PR #60 abgeschlossen; maßgeblich ist
[die abschließende Klarstellung](https://github.com/venomenon328/picross/pull/60#issuecomment-6076039228).
#53 einschließlich N01–N03 ist über PR #56 integriert. VS2/#61 überträgt diese
Vollsicht auf die reguläre Hauptszene. Die neun Inhalte und der 720p-Fallback
bleiben erhalten; manuelle Raster-/Miniaturnavigation entfällt. Neue VS2-Gates
stehen in der oben verlinkten Prüfzuordnung. Historische Freigaben gelten nur
für ihren jeweiligen Head.

## Herkunft und historische Daten

Die ausdrückliche Zustimmung nach Integration von #58 und der anschließende Wunsch
nach besserer Nutzung freier Breite sind in den aktuellen Bodies von #57/#59
konsolidiert. Der beschriebene VS08-Screenshot ist persönliches Teilfeedback,
keine erfundene vollständige Lösung, Zeitmessung oder DPI-Abnahme.
Alte Reports, `manifest.json`, `production.json`, `plan-vb1.json` und die endliche
E1-initial/correction-1/correction-2-Reihe bleiben bytegebundene historische
Nachweise. Ihre damaligen offenen Entscheidungsfelder werden nicht nachträglich
überschrieben. Aktuelle Berichte referenzieren diese Entscheidung separat;
[GF-M01-Protokoll](../examples/vs1/gf1-owner-protocol.json) bleibt unausgefüllt.
