# SD2-B: Referenzen und Bewertungsvertrag 0.4

Stand: 25.10.2026 · Vertrag 1.0 in Entwicklung · #404

Basis `c7c6156ac27dc033036443bc06ef398bbf94f32f`, integriertes SD2-A / PR #408.
[Fachvertrag](PUZZLE_DIFFICULTY_V2.md), [Analysevertrag](SD2_ANALYZER.md),
[unveränderter 0.3-Freeze](SD_CALIBRATION.md). Dieser eigenständige B-Weg
aktiviert keine Methode und verändert keine Katalog-/Produktionsdaten.

## 1. Referenzen vor Parametern

Der [feste Satz](../tools/puzzle_production/sd2_references_0_4.json) bindet 36
vollständige neue synthetische Rätsel, Herkunft, Ausgangsmatrix, daraus extrahierte
Hinweise, Logik-/Analysehash, Auswahlgrund, Erwartungsstufe und Mustergruppe.
20 Fälle gehören zur Kalibrierung, 16 zur zurückgehaltenen Validierung.
Die Matrix dokumentiert die Konstruktion und den nachgelagerten Endvergleich;
der Analysator erhält ausschließlich Hinweise und unbekannte Startdomains.
Keine Katalogdatei, Kopie, A-Regeltestmatrix oder alte 0.3-Referenz wurde übernommen.

Die geometrischen Muster wurden neu konstruiert. Die unabhängigen Zufallsmatrizen
stammen aus vier separaten deterministischen Untersuchungen; vollständiger
Erzeugertext, Seeds, Kandidatenzahlen und ausgewählte Indizes stehen im Satz.
Die Untersuchung endet nach 2200/2200 beziehungsweise 5281/4731 Kandidaten.
Sie ist kein CI-Befehl und wird nicht bei späteren Rätseln fortgesetzt.
Auswahl nach vollständigem Rohverlauf, niemals nach Score oder Histogramm.
Alle ausgewählten Spuren wurden mit dem unabhängigen SD2-Prüfer bestätigt;
Paarfälle zusätzlich mit vollständiger separater Linienbaseline und Paarproof.
Der bewiesene Endstand stimmt jeweils mit der konstruierten Matrix überein.

Die Erwartungen sind technische, begründete Modellanker, keine menschlichen
Messungen. Ihre Begründungen und Vergleichsordnungen sind vor der ersten
Scoreberechnung festgelegt. Numerischer Vertrag, Alternativenvergleich,
Implementierung und Freeze folgen als weitere versionierte Schritte desselben
Pakets. Dieser erste Stand behauptet ausdrücklich noch keinen Methodenfreeze.

## 2. Vorab gebundene Abdeckung und Gruppentrennung

`s<Seed>-<Index>` bezeichnet exakt einen Fall im JSON. Jeder Fall besitzt eine
eigene Gruppe; Transformationen und spätere nahe Ableitungen müssen in derselben
Gruppe bleiben. Die unabhängigen Zufallsmatrizen wurden nicht aus gemeinsamen
Stammrastern mutiert. Geometrische Konstruktionen verbleiben vollständig in der
Kalibrierung; die Validierung verwendet unabhängige Zufallsmuster. Alle
Erwartungen, Gruppen und Splitzuordnungen werden nach Ergebnissen nicht geändert.

| Abdeckung / erwartete Stufe | Kalibrierung | Zurückgehaltene Validierung |
| --- | --- | --- |
| L1, unmittelbare Voll-/Leer-/Restregeln | full-50, bands-40, packed-colors | s40499-9, s40499-710 |
| L1, flüssige einfache Überlappungen | s40401-3, s40401-1080 | s40499-173 |
| L2, übliche eingeschränkte Überlappungen/Verlängerungen | s40401-10, s40401-44, s40401-98 | s40499-2, s40499-48 |
| L3, kleinteilige Suche ohne stärkere Schlussfamilie | s40401-526, s40401-1111 | s40499-654, s40499-957 |
| L3, gemeinsame Blockzuordnung mit gutem Fortschritt | s40401-6, s40401-1574 | s40499-747, s40499-1744 |
| L4, Kombinationen und wiederkehrende enge Phasen | s40401-1495, s40401-2093, s40401-888 | s40499-1564, s40499-656 |
| L5, reine allgemeine Linienlogik | s40405-230, s40405-3463, s40405-5280 | s40495-1729, s40495-2540, s40495-4730 |
| L5, notwendiges R4 | s40405-65, s40405-79 | s40495-103, s40495-109 |
| Frühe / späte / wiederholte Engstellen | s40401-1495 / s40405-3463 / s40401-888 | s40499-654 / s40495-4730 / s40499-656 |
| Kleine schwierige / große einfache Fälle | s40405-5280 / full-50, bands-40 | s40495-4730 / keine zusätzliche große Validierung behauptet |
| Mono / Farbe, partielle Farbausschlüsse | s40401-10 / s40401-44, s40401-888 | s40499-2 / s40499-48, s40499-1564 |
| Lange Füllzüge / viele gepackte kleine Zahlen | full-50, bands-40 / packed-colors | s40499-710 / keine vollständige Kreuzproduktquote |

Größen reichen von 35 bis 2500 Zellen; Rechtecke, quadratische Muster und beide
Farbsemantiken sind enthalten. E1-Rohbelege enthalten direkte Überlappung,
sicher eingeschränkte Überlappung und eindeutige Anker. Die konkrete Regelanwendung
bleibt in der reproduzierbaren vollständigen Spur prüfbar. Frühe/späte Phasen
beziehen sich auf den Fortschritt bei Phasenbeginn gemäß A-Vertrag; ein später
E3-Schritt kann innerhalb einer früh begonnenen Phase liegen.

Die breite Auswahl wird nicht als statistisch repräsentative Stichprobe bezeichnet.
Die seltenen E3-Fälle wurden bewusst gesucht, um technische Erreichbarkeit und
Schutz später Schlüsselstellen zu prüfen. Jeder Skalenwert hat mehrere
voneinander unabhängige ganze Muster. Künstliche Profilfolgen werden später nur
Formelgrenzen isolieren und niemals diese Rätselbelege ersetzen.

## 3. Chronologie und Aussagegrenzen

Die Referenzfestlegung wird vor dem numerischen Vertragsauftakt committed.
Validierungsrohprofile wurden ausschließlich für die Kuratierung betrachtet;
sie werden nicht zur Parameterwahl oder Alternativenauswahl verwendet.
Nach Vertrags-/Implementierungsabschluss werden ihre Bewertungen separat geöffnet.
Eine spätere Änderung aufgrund dieser Ergebnisse müsste die Fälle als verwendet
kennzeichnen und einen neuen unabhängigen Validierungssatz binden.

Menschliche Vergleichsdaten liegen nicht vor. Deshalb höchstens mittlere
Aussagekraft, keine Lösungsminuten und keine behauptete empirische Kalibrierung.
SD2-B-T01 und getrennter Selbstreview werden in
`docs/SD2_B_VERIFICATION.md` und dem Implementierungs-PR gebunden; das separate
SD2-B-R01 und Merge bleiben nachgelagerte Gates. #405/#406 bleiben außerhalb.
