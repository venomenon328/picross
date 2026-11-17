# HS · Darstellung erfüllter Hinweise

## Geltung und Zuständigkeit

Dieser Vertrag besitzt Abschwächung und Ganzzahl-X der abgeleiteten Hinweis-
zustände. H1/GP48-Erkennung und Sitzungsschalter stehen in [P1](PROTOTYPE_P1.md),
Schrift-/Mess-/Fitgeometrie in [CLUE_TYPOGRAPHY](CLUE_TYPOGRAPHY.md), Interaktion
in [CLUE_INTERACTION](CLUE_INTERACTION.md). Die Regeln im aktuellen Git-Stand
sind vom Liefer- und persönlichen Abnahmestand im Issue/PR zu unterscheiden.

## HS-D01: gemeinsame Abschwächung beider positiven Zustände

| Zustand | Zahl und vorhandene C1-Kontur | Erledigtmarkierung |
| --- | --- | --- |
| OPEN | Unverändert normale Deckkraft, 100 % | Keine |
| FILLED: eindeutig vollständig gesetzt, noch nicht beidseitig abgegrenzt | Gemeinsame Deckkraft 60 % | Keine |
| CLOSED: zusätzlich beidseitig abgegrenzt | Genau dieselbe Abschwächung wie FILLED | Handschriftliches X über der ganzen Zahl |

Beide positiven Zustände verwenden immer denselben Wert; beim Abgrenzen wird
die Zahl nicht wieder kräftiger. Eine begründete Feinabstimmung bleibt ein
reversibles Ausarbeitungsdetail und wird mit Wert und Sichtbefund im PR gebunden.

Die tatsächliche Rätselfarbe bleibt erhalten. Ausgrauen bedeutet reduzierte
Deckkraft, nicht Umwandlung aller Hinweise in dasselbe Grau oder Änderung der
Palette. Vorhandene C1-Konturen werden mit der Zahl abgeschwächt; deren bisherige
Farbzuordnung bleibt. Trotz Abschwächung müssen Zahl und Farbzugehörigkeit auf dem
Papier lesbar bleiben, auch bei hellen Hinweisfarben und kleinem Zoom.

## HS-D02: ein handschriftliches X je Hinweis

CLOSED erhält zwei deutlich erkennbare diagonale Stiftzüge anstelle des bisherigen
Querstrichs. Leichte, begrenzte Unterschiede in Krümmung, Winkel, Enden und Stärke
geben Handschrift, nicht unruhige oder schwer lesbare Geometrie. Das X ist etwas
kontrastreicher als die blasse Zahl, ohne offene Hinweise optisch zu übertönen.
Aktive Ausarbeitungswerte: X-Deckkraft 76 %, Stiftbreiten
`max(1, fs/18) × 1,08/0,96`. Zwei Vierpunktzüge verwenden FNV-1a über
Rätsel-ID/Achse/Linie/Originaltokenindex für begrenzte Biegungs-/Endvarianten.
Keine neue Warnfarbe oder zusätzliche Richtig-/Falsch-Semantik einführen.

Das X erstreckt sich über Höhe und Breite des vollständigen Zahlentokens. `11`,
`23` oder `40` erhalten jeweils ein gemeinsames X, nicht eines pro Ziffer. Kein
kleines Kreuzchen nur im Zeicheninneren, kein zusätzlicher horizontaler Strich,
kein Ersatz der ursprünglichen Zahl durch ein X-Zeichen. Die Zahl bleibt lesbar.

Geometrie und gegebenenfalls Varianten bleiben an der ursprünglichen Hinweisidentität
stabil: Rätsel, Achse, Linie und ursprünglicher Tokenindex statt Bildschirmposition,
aktuellem Slot, Hover, Zeit oder Tooltipumbruch. Nach Neuzeichnen, Zoom-Rundweg,
Hinweisdrag/Snap und Wiederaufnahme entsteht dieselbe normierte Form. Beide Achsen
und der vollständige Hinweis-Tooltip verwenden dieselbe Zeichenregel; unterschiedliche
Darstellungsgrößen dürfen passend skalieren, nicht neu würfeln.

Kleine Darstellungen dürfen feine Unregelmäßigkeiten reduzieren, müssen aber klar
zwei diagonale Züge zeigen. Kein neuer Animationstakt, keine neue Option und keine
Änderung der Zell-X, Zellatlanten oder Zellanimationen. `…` und Leerlinien-`–`
erhalten weder Abschwächung als erledigt noch ein X.

## HS-D03: Zeichnung und Messhülle gemeinsam ändern

Zahlen, beide X-Züge, größte erlaubte Strichvariation, Strichstärke, wirksame
Konturen und Antialiasing gehören gemeinsam in die tatsächliche Zeichenhülle.
Dies gilt für Zeilen, Spalten, kontinuierlichen Drag, Markergrenzen und das
vollständige Hinweis-Overlay einschließlich Umbruch, Titelabstand und Innenrändern.
Eine gemeinsame geometrische Grundlage verhindert auseinanderlaufende Mess-/Zeichenregeln.

Die Hülle reserviert das erforderliche Maximum unabhängig vom aktuellen Status.
Ein Wechsel OPEN/FILLED/CLOSED ändert daher weder Schriftgrad, Grundlinie,
Slotposition, Slotabstand, Raster-Fit noch Tooltipumbruch. Ein X darf nicht in
Nachbarzahlen, Nachbarlinien, Marker, Rahmen oder Raster reichen und nicht erst
durch Abschneiden passend gemacht werden. Die neue Hülle wird in dieselbe
HC-Schrift-/Slot-/Fitberechnung einbezogen, nicht nur als ungemessene Dekoration.

Die Gestaltung soll den vorhandenen kompakten Zahlenraum nutzen. Keine unnötig
großen Kreuzreserven oder pauschale Schriftverkleinerung als Abkürzung. Notwendige
Unterschiede gegenüber der alten Hülle messen und begründen; ein erheblicher Konflikt
mit Lesbarkeit oder Vollsicht wird offengelegt, nicht durch eine verdeckte Kappung
der Schriftgröße oder Hinweisanzahl kaschiert. Die größtmögliche passende Schrift,
G-Mindestgarantie und V-Vollanzeige bleiben ihre jeweiligen Ziele. Reine
Zustandswechsel dürfen auch nach einer begründeten Geometrieanpassung nichts verschieben.

Konkrete Radien-/AA-Abstände, Fontsuche, Status-unabhängiger Fit und die
Web-Atlasbegrenzung stehen ausschließlich in [CLUE_TYPOGRAPHY](CLUE_TYPOGRAPHY.md).

Mess-/Varianten-/Overlaycaches bleiben transient und begrenzt. Relevante Schrift-,
Skalierungs-, Definitions- und Geometriewechsel dürfen keine alten Hüllen verwenden.
Kein Neuwürfeln oder Vollwiederaufbau der ruhenden Zellmarkierungen durch Hinweisstatus
oder Hover. Der [Zellrendering-Vertrag](CELL_RENDERING.md) bleibt unverändert.

## HS-D04: reine Darstellung auf unveränderter H1/GP48-Semantik

OPEN/FILLED/CLOSED werden ausschließlich nach [P1 §5.2](PROTOTYPE_P1.md#52-fenster-zoom-hinweise-und-miniatur)
aus der vollständigen eigenen Linie abgeleitet. Die Darstellung verwendet stets
denselben aktuellen sichtbaren Zustand einschließlich elastischer Vorschau.
Ein entferntes oder ungültig gewordenes CLOSED verliert unmittelbar sein X.
Status und X werden nicht eigenständig gespeichert. Keine zusätzliche
Lösungsprüfung, Fehlerhilfe, automatische Zellmarkierung oder Abschlussbedingung.

Der P1-Sitzungsschalter zeigt bei Aus normale Zahlen ohne Abschwächung/X, bei
An den aktuell abgeleiteten Stand. Zellvorschau und Animationen sind unabhängig
und folgen [UI_DRAWING_STYLE](UI_DRAWING_STYLE.md).

## Prüfung und Abnahme

HS-A01–A06 und ursprüngliche T01/R01/M01-Ergebnisse stehen in
[#186 / PR #187](https://github.com/venomenon328/picross/pull/187).
Messdaten und native Pixel-/Sichtprüfung ergänzen einander; eine Alpha-Konstante
oder größere Hülle allein belegt keine Lesbarkeit. Aktuelle Modulauswahl folgt
dem [Paketvertrag](../ci/CI_WORKFLOW_V2.md), gewählte Stichproben dem
[nativen Modulvertrag](../ci/CI_C_NATIVE_GROUPS.md). Historische Einführungsbilder und
Gates sind keine erneute Dauerpflicht.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#186](https://github.com/venomenon328/picross/issues/186) und [PR #187](https://github.com/venomenon328/picross/pull/187).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CLUE_STATUS.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
