# HS: klar unterscheidbare Erledigtzustände der Hinweiszahlen

Stand: 16.10.2026 · Spezifikation 0.1 · vom Eigentümer freigegeben, noch nicht implementiert

## Geltung und Liefergrenze

[HS / Issue #186](https://github.com/venomenon328/picross/issues/186) führt die
Hinweisdarstellung aus H1/GP48/HC fort. Dieses Dokument enthält die dauerhaften
Entscheidungen; das Issue führt Paket, Vorbereitung, Akzeptanz und Abnahmen.
Bei Hinweisarbeit zusammen mit [Typografie](CLUE_TYPOGRAPHY.md),
[P1](PROTOTYPE_P1.md), [Zeichensprache](UI_DRAWING_STYLE.md) und
[Projektprofil](PROJECT_PROFILE.md) lesen. Einstieg bleibt [AGENTS](../AGENTS.md).

Der Eigentümer bestätigt die deutlichere Abschwächung und das handschriftliche X
als Spezifikation. Das ist keine Bestätigung einer schon gelieferten Darstellung,
kein Auftrag zur jetzigen Produktimplementierung und keine Mergefreigabe.
Quellendiagnose: `main@09ffa51f2cc2bb8a97c71b26113d2892f98be6c9` zeichnet nur
FILLED mit 78 %, CLOSED dagegen mit voller Zahlendeckkraft plus geradem Querstrich.
Dies wird gezielt gestalterisch ersetzt; kein Fehler der Erkennung ist nachgewiesen.
Der bereitgestellte Screenshot ist Feedback ohne verifizierte Build-/DPI-Bindung.

## HS-D01: gemeinsame Abschwächung beider positiven Zustände

| Zustand | Zahl und vorhandene C1-Kontur | Erledigtmarkierung |
| --- | --- | --- |
| OPEN | Unverändert normale Deckkraft, 100 % | Keine |
| FILLED: eindeutig vollständig gesetzt, noch nicht beidseitig abgegrenzt | Deutlich blasser als bisher; gemeinsamer Ausarbeitungs-Ausgangswert 60 % | Keine |
| CLOSED: zusätzlich beidseitig abgegrenzt | Genau dieselbe Abschwächung wie FILLED | Handschriftliches X über der ganzen Zahl |

Die 60 % sind ein freigegebener Ausgangswert, keine bereits erfolgte native
Sichtabnahme. Eine begründete Feinabstimmung bleibt reversibles Ausarbeitungsdetail;
gewählten Wert und Sichtbefund im PR festhalten. Beide positiven Zustände verwenden
immer denselben Wert. Beim Abgrenzen darf die Zahl nicht wieder kräftiger werden.

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
Seine konkrete Deckkraft und Strichstärke sind zu dokumentierende Ausarbeitungswerte.
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
Die separate bisherige Querstrichmessung im Overlay darf nicht zurückbleiben.
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

Die frühe Web-Ablehnung durch `Typography.strike_width()` ist im bisherigen Code
nur deshalb eine sichere Untergrenze, weil die alte Querstrichhülle immer reserviert
wird. Nach dem X-Ersatz muss diese Begründung für die neue Hülle tatsächlich gelten
oder die betreffende Vorablehnung entfallen. Keine zulässigen Kandidaten aufgrund
einer nicht mehr zutreffenden alten Strichbreite verwerfen, keine neue Monotonieannahme
oder feste Fontobergrenze. Die Begrenzung temporärer Web-Fontgrößenatlanten bleibt.

Mess-/Varianten-/Overlaycaches bleiben transient und begrenzt. Relevante Schrift-,
Skalierungs-, Definitions- und Geometriewechsel dürfen keine alten Hüllen verwenden.
Kein Neuwürfeln oder Vollwiederaufbau der ruhenden Zellmarkierungen durch Hinweisstatus
oder Hover. Der [Zellrendering-Vertrag](CELL_RENDERING.md) bleibt unverändert.

## HS-D04: reine Darstellung auf unveränderter H1/GP48-Semantik

Erfüllt ist weiterhin nur ein bereits vollständig gesetzter Block mit derselben
eindeutigen Zuordnung in allen kompatiblen Belegungen seiner vollständigen Linie.
Beide unmittelbaren Enden müssen für CLOSED jeweils an X, einen echten Linienrand
oder eine vorhandene Füllung anderer Farb-ID grenzen. Unbekannte Nachbarn,
entfernte X und Ausschnittränder sind keine Abgrenzung. Widerspruch oder verlorene
Eindeutigkeit nehmen die Markierung zurück; keine versteckte Lösungsprüfung.

Nur eigene Linienhinweise und sichtbare Zellen einschließlich elastischer Vorschau
zählen. Rückzug, Abbruch, Commit, Undo/Redo, Reset, Blattwechsel, Restore und Recovery
leiten die Darstellung aus demselben aktuellen Zustand ab. Das X darf nach dem
Entfernen einer Abgrenzung nicht stehen bleiben und nicht unabhängig vom Status
im Save gespeichert werden. Kein manuelles Abhaken, automatische Hintergrund-X,
zusätzliche Fehlerhilfe oder veränderte Abschlussbedingung.

Der Sitzungsschalter „Erfüllte Hinweise markieren“ bleibt unverändert: Aus zeigt
normale Zahlen ohne Abschwächung und ohne X, An den aktuellen abgeleiteten Stand.
Er bleibt über Blatt-/Seitenwechsel und Reset erhalten und startet nach App-Neustart
wieder aktiv. Keine neue persistente Einstellung, History-, Save- oder Zellaktion.
Die 56-%-Zellvorschau und alle bisherigen Zellbewegungsregeln bleiben unabhängig.

## Gezielte Ablösung und Dokumentationsübergang

Die folgenden älteren Formulierungen sind ausschließlich hinsichtlich der
Hinweisdarstellung durch HS-D01–D04 ersetzt:

| Zuständige Quelle | Abgelöster Teil |
| --- | --- |
| [Produktdefinition](PRODUCT_DEFINITION.md), §5.1 | Abgegrenzte Hinweise nur als durchgestrichen beschrieben; künftig gleich blass plus X. |
| [Gestaltungskonzept](DESIGN_CONCEPT.md), §5.1 | Nur der mittlere Zustand erhält 78 %; CLOSED wird durchgestrichen. |
| [P1](PROTOTYPE_P1.md), §5.2 | 78-%-Mittelzustand und Durchstrichdarstellung; Abschwächung und X folgen jetzt HS. |
| [Zeichensprache](UI_DRAWING_STYLE.md), ZS-D01 | Die drei semantischen Zustände bleiben, die beiden positiven Darstellungen ändern sich. |
| [Hinweis-Typografie](CLUE_TYPOGRAPHY.md) | Alte Querstrichhülle und davon abhängige Web-Untergrenze als unveränderte Zielgeometrie. |

Bis zur Inline-Nachführung in der zugehörigen Implementierung gilt diese ausdrückliche
Ablösung. Die technische alte Darstellung bleibt bis dahin der Iststand; weder neue
Spezifikation noch grüne Dokumentprüfung ändern den Player. Bei Umsetzung betroffene
aktive Fachpassagen sowie Anwenderanleitung und native Hilfe konsistent nachführen.
Nicht betroffene Quellen, Font-/Assetbytes, historische Pläne, Reports und Abnahmen
bleiben unverändert. Das Projektprofil routet Hinweisarbeit bereits über
CLUE_TYPOGRAPHY und damit auf diese Spezifikation; keine Änderung gemeinsamer dev-rules.

## Prüfung und Abnahme

[Issue #186](https://github.com/venomenon328/picross/issues/186) bindet HS-A01–A06,
den technischen Lieferweg HS-T01 und die getrennten Abnahmen HS-R01/HS-M01 vor
Implementierungsmerge. Messdaten und native Pixel-/Sichtprüfung ergänzen einander;
eine Alpha-Konstante oder eine größere Hülle allein beweist keine lesbare Zeichnung.
Ein nicht ausgeführter Windows-Start oder eine fehlende Eigentümerprobe wird nicht
als bestanden ausgegeben. Die [aktuelle CI-Policy](CI_POLICY.md) entscheidet die
Prüfauswahl, einschließlich Web bei Product, ohne Bestandsrätsel neu zu zertifizieren.

Das gesamte Paket bleibt bis zur beauftragten Implementierung und Abnahme offen.
Kein automatischer Merge, Release oder Deployment durch diese Spezifikation.
