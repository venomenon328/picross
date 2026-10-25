# SD2-D-OM01 · Om klären, Eigentümerabnahme und VR01-Ausnahme

Stand: 26.10.2026. Folgeauftrag zu [#406](https://github.com/venomenon328/picross/issues/406)
und [Draft-PR #411](https://github.com/venomenon328/picross/pull/411) auf
`chore/406-sd2-bestandsumstellung`, Ziel `main`.

## Eigentümerentscheidungen und Grenzen

Nach [V01](SD2_D_VERIFICATION.md) am Lieferhead
`d963687473d036a62b17f73e59f2640e0ef7fefc` hat der Eigentümer erklärt:
„Die Vorschläge sind abgenommen, fahre fort.“ Die 44 gültigen Vorschläge sind
damit fachlich abgenommen. Auf die anschließend getrennt gestellten Fragen
antwortete er ausdrücklich:

- **„Zunächst Om klären“**: keine Teilumstellung der 44 Ratings mit Om auf 0.3.
- **„Auf separates VR01 ausdrücklich verzichten“**: SD2-D-VR01 wird für
  diesen Auftrag erlassen. Es wurde nicht durchgeführt und gilt nicht als
  bestandener unabhängiger Review. Selbstreview und technische Nachweise
  bleiben erforderlich; finales SD2-D-R01 und Merge sind nicht erfasst.

Die Entscheidungen sind im aktuellen Issue-Body festgehalten. OM01 untersucht
gezielt den offenen Fall und erstellt gegebenenfalls die neue vollständige
Vorschau. Übernahme und Aktivierung werden in diesem Klärungsschritt nicht
ausgeführt. Die unveränderten alten V01-Dateien bleiben historische Belege;
ihre damaligen offenen Statusaussagen werden nicht rückwirkend umgeschrieben.
Das Verbot des Web-CI-Jobs bleibt wirksam.

## Befund aus den vorhandenen Belegen

ID `pz-87bf2975c82540a399a3d0c7fa180a25`, Definition `om_001`, 29×29,
Produktionsmodus `mono`, Puzzle-Revision 1. Definitions-SHA-256:
`2021497d6e79578feca61b836986280a54f33e7a91eac06dfe6c970567068912`.
Normalisierte Logik-v2, Engine-Logikhash:
`c0751a6de35f2519e3ea99c3cc7e0e8ae221a3c73d0b48a9f4c0b56a1d6299fc`.

Der V01-Versuch endete bei genau 20.000.000 Paaroperationen, nach etwa 13,52 s,
Peak 7.462 von 250.000 Records und 2.472 von 100.000 Linienauswertungen.
Er erreichte weder Zeit- noch Speicher- oder Liniengrenze. Der unveränderte
Solver zählt untersuchte Paartransitionen, auch wenn keine informative
Änderung entsteht. Nach jeder Paaränderung beginnen Linieniteration und
lexikografische Paarfolge erneut. Dieser Aufwand erklärt, weshalb die
informative Spur deutlich kürzer als die Menge geprüfter Paare ist.

Die bestätigte Linienbaseline bestimmt 54 von 841 Zellen und bleibt `stalled`.
Der abgebrochene Paarlauf enthält 40 aufgezeichnete informative Schritte,
darunter zwölf Paarschritte; seine gespeicherten Domains bestimmen 104 Zellen,
737 bleiben offen. Diese Präfixdaten sind keine vollständige Lösung und kein
neuer R4-Notwendigkeitsnachweis. Insbesondere ist ein Budgetabbruch weder
Unlösbarkeit noch ein bestätigter Paarfixpunkt.

Die aktive alte 0.3-Hülle bindet dieselbe Definition und dieselbe Baseline
(`f2d5011080f17a6b7dec48546266c41d85754755290501b014e72d8e1832b828`).
Sie verzeichnet einen historischen vollständigen Paarproof
(`d740e93a7a975ad7ede1c41924710ef7a60428706062d8d0b70a61fd2427ed62`).
[PR #304](https://github.com/venomenon328/picross/pull/304) berichtet damals
306 Schritte und einen eigenen normalisierten 0.3-/R4-Nachweis;
[PR #305](https://github.com/venomenon328/picross/pull/305) bindet die spätere
Integration. Gelesen wurden aktuelle kompakte Metadaten und diese Berichte,
keine alten Produktionsarchive oder Proofpakete wiederhergestellt. Das ist
ein Plausibilitätshinweis für den nächsten Versuch, keine Umetikettierung
historischer Daten zu 0.4.

## Vorab gebundener einzelner Folgelauf

Die neue Ausführungswahl wurde vor Start im Issue und in der externen
`binding.json` festgehalten. Sie nutzt den ausdrücklichen Om-Klärungsauftrag;
V01 selbst wird nicht wiederholt und sein ursprünglicher Abbruch bleibt stehen.
Der [Paarlinienvertrag](PAIRED_LINES.md) erlaubt bis 100.000.000 Paaroperationen.
Dieses zulässige Maximum wird einmalig für Om verwendet; keine zusätzliche
Schleife, Profiländerung, Heuristik, Suche oder Methodenänderung.

| Phase | Vorab gesetztes Budget |
| --- | --- |
| Ein zusätzlicher `solve` mit `paired-lines-color`, `rows-first` | Ein kumulatives Budget: 120 s, 100.000 Linien, 100.000.000 Paaroperationen, 250.000 Records für beide Erzeugungen und beide Prüfungen. |
| Ein 0.4-Anschluss nur bei vollständigem frischem R4-Erfolg | Getrennt für Analyse und Verifikation: je 120 s, 100.000 Linien, 20.000.000 Regeloperationen, 80.000 Wellen, 100.000.000 Paaroperationen, 250.000 Records. |
| Sammelvorschau/Plan | Ausschließlich bestehende Checked-Dateien wiederverwenden; nur Om darf einen neuen Eingang erhalten. Kein erneuter Gesamtlauf. |

Auch dieses Mono-Rätsel verwendet die unveränderte normalisierte innere
Logik-v2/`color-gap-v1` als `solve`-Eingang; die äußere SD2-Hülle ist kein
Solverinput. Neue Ausgabepfade verhindern die Änderung alter geschlossener
Bundles. Beim erneuten Abbruch endet dieser Versuch ohne weitere Erhöhung.
Die Ressourcenparameter begrenzen Ausführung und Prüfung; sie ändern keine
Regel, Formel, Grenze, Profildefinition oder Freezebindung.

Quell-/Werkzeugbasis bleibt `4e23e644f3457362e02b75f78fdb575a99265494`;
vor Wiederaufnahme und Lauf bestätigt. Beide Freezes und alle 322 Quellen
passen weiterhin zur V01-Bindung; alle 511 im V01-Arbeitsmanifest gebundenen
Dateien und das Archiv sind unverändert. Externer neuer Arbeitsroot:
`E:/Zeuch/Coding/picross-sd2d-evidence/sd2-d-20261026-om01`.

## Ergebnis des frischen Nachweises

Der neue kumulative Paarlauf ist vollständig erfolgreich (Exit 0). Die
unabhängige Baselineprüfung bestätigt den Linienfixpunkt; die unabhängige
Paarprüfung bestätigt die vollständige Lösung ab unbekanntem Start ohne Suche.
306 informative Schritte bestimmen alle 841 Zellen. Verbrauch: 71.045.756
kumulative Paaroperationen, 7.595 Linienauswertungen, Peak 7.462 Records,
46,54 Sekunden. Die Paarverifikation selbst verbraucht 1.052.759
Paaroperationen; dieser kleinere Wert ist nicht der kumulative Laufverbrauch.

Die frisch erzeugten Baseline- und Proofbytes haben dieselben Hashes wie die
historisch verzeichneten Dateien. Das ist eine frische Reproduktion durch den
unveränderten deterministischen Solver, kein Import historischer Nachweise.
Die eigenständige `solve`-Bewertung führt weiterhin ihre alte Kennung 0.2 für
die R4-Notwendigkeit. Die neue Endnote stammt ausschließlich aus dem danach
einmal ausgeführten, ausdrücklich gewählten **0.4-Bewertungsweg**.

| Gegenstand | Ergebnis / Bindung |
| --- | --- |
| Neue 0.4-Bewertung | `rated`, `required_r4`, **L5**, D = 9/2, S = 0, W = 0; Score = 9/2. |
| Grenznähe | Abstand 1/2 zur unteren Grenze 4; keine obere Grenze. L5 auch ohne W. |
| Aussagegrenze | Konfidenz `medium`, keine Zeitschätzung oder menschliche Kalibrierung. R4 nutzt den eingefrorenen Anker; S/W sind keine Vollmessung der Paarlösung. |
| Unveränderte Linienprofile | Vier Wellen, 54 neue Singleton-Zellen; bestätigter Linienfixpunkt, Linienanalyse weiterhin `stalled` und unvollständig. Gesamtdeduktion durch separaten R4-Nachweis vollständig. |
| Checked-Hash | `d441e00b08fdd179ad25cfdeac84b7cad043f95cc20cc81d14f48f96935caf98` |
| SD2-Analyse-Ergebnishash | `173e88f24d2494b40be3384d1859345ff0a211016ad6a72e5f6d038a178d1909` |
| Profilhash | `9917716be8b364a833df0fba46c1f66ab1b2fca3e66a4eaaa5a67fe68e878440` |
| Spurhash | `27c3aeb4f1ac8906429b56f94b3a4d4dde4a6df7747d3c2364fba5441651669e` |

Definitionsbytes, Produktionsmodus, Puzzle-Revision und normalisierte
Matrixbindung bleiben unverändert. Der 0.4-Anschluss prüft die eigene
Linienanalyse und beide frischen R4-Belege erneut innerhalb seines getrennten
Verifikationsbudgets. Die Bewertung bleibt wie die alte 0.3-Bewertung L5,
erhält aber eine neue überprüfte Methoden- und Ergebnisbindung.

## Aktualisierter vollständiger Vergleich und Plan

Die [vollständige neue Vorschau](evidence/sd2-d-om01/PREVIEW.md) bindet
`sd2-d-20261026-om01` und den Ergebnishash
`a0d1908573a253978273736e86d66d32fa027068480654f1837d5cd570a46c2a`.
Alle 45 IDs sind gültig, keine bleibt offen. Verteilung L1/L2/L3/L4/L5:
**4/9/6/23/3** gegenüber bisher **0/0/32/10/3**. Nur Om ersetzt den bislang
offenen Vorschlag durch L5. Alle anderen 44 Checked-Dateien und ihre
vollständigen Ergebniszeilen sind byte- beziehungsweise strukturgleich zur
abgenommenen V01-Vorschau; kein erneuter Gesamtlauf fand statt.

Der [V01-Gruppenvergleich](evidence/sd2-d-v01/COMPARISON.md) bleibt für diese
44 IDs unverändert gültig. Für die Om enthaltenden Gruppen lautet der neue
Stand (Reihenfolge L1/L2/L3/L4/L5/offen):

| Gruppe | Neue Verteilung | Neue Score-Spanne |
| --- | --- | --- |
| Produktionsmodus mono, 26 IDs | 0/9/5/10/2/0 | 1,5696–4,5000 |
| Eine Logikfarbe, 26 IDs | 0/9/5/10/2/0 | 1,5696–4,5000 |
| Fläche 401–900, 16 IDs | 2/3/2/8/1/0 | 0,2500–4,5000 |
| Hinweise 101–200, 12 IDs | 1/2/0/8/1/0 | 0,3086–4,5000 |
| Kurzblockanteil <50 %, 25 IDs | 3/7/4/10/1/0 | 0,3086–4,5000 |

Om und GameBoy erhalten denselben festen R4-Anker trotz unterschiedlicher
Größe und Paarlaufkosten. Das entspricht dem eingefrorenen Vertrag und ist
keine gemessene Gleichheit ihres vollständigen menschlichen Aufwands.
Die bisherigen Grenzfälle und Größen-/Modusrelationen ändern sich dadurch
nicht. Es gibt weiterhin keine Katalogquantile, Anpassung von Grenzen oder
Benutzung dieser Bestandsdaten zur Kalibrierung.

Der [reine Übernahmeplan](evidence/sd2-d-om01/PLAN.md) beendet sich mit Exit 0
und `open_ids: []`. Er nennt genau 48 Pfade: 45 Ratings, zwei neue Dauerberichte
und `game/data/registry.json`. Dieser Plan wurde nicht angewendet. Die
vollständige Quellenbindung erfasst weiterhin auch unveränderte Definitionen,
Metadaten und Abwesenheitsnachweise. Eine zwischenzeitliche Quellenänderung
macht die gebundene Vorschau stale.

## Getrenntes Selbstreview und weitere Gates

Nach dem Lauf folgt ein eigener Integritätsprüfschritt ohne weiteren Solver-
oder Analyseaufruf. Er prüft die 322 Quellenbindungen, Bytes und Zeitstempel
der 302 vorhandenen Dateien, beide Freezes, die unveränderten V01-Belege,
alle 45 Checked-Eingänge, die 44 unveränderten Ergebniszeilen, Om-Arithmetik
und Grenznähe, sämtliche neuen Bundle-Dateihashes, aufgezeichnete unabhängige
Prüfergebnisse sowie den exakten 48-Pfade-Plan. Ergebnis und SHA-256 stehen
im [Arbeitsbelegindex](evidence/sd2-d-om01/WORK_EVIDENCE.md).

Die erste Ausführung dieses Selbstreviewskripts verglich irrtümlich die
T/K-Gesamtbindung mit dem kleineren `sources`-Feld des Berichts und brach
dort ab. Drei Registry-/Kategoriebindungen liegen vertragsgemäß separat in
`snapshot`. Korrigiert wurde nur diese Auditzuordnung; Analyse, Proofs,
Berichte und Plan wurden nicht erneut erzeugt oder verändert.

Das bleibt ein Selbstreview. Das unabhängige SD2-D-VR01 ist auf ausdrücklichen
Eigentümerwunsch erlassen, nicht bestanden. D-V01-B01 (offener Om-Nachweis)
ist durch OM01 erledigt. D03 verlangt weiterhin tatsächliche vollständige
Übernahme und Aktivierung; eine Vorschau erfüllt es nicht.

Die 44 bereits abgenommenen Vorschläge bleiben gebunden erhalten. Om ist der
jetzt neu vorgelegte 45. Vorschlag. OM01 endet vor Ratingübernahme und
Aktivierung. Ein anschließender passender Auftrag verwendet diesen
vollständigen Plan: Übernahme → unmittelbarer echter No-op → frischer
Aktivierungsplan auf übernommenem Stand → Aktivierung → echter No-op.
Technisches T01 und finales separates Daten-/Integrationsreview SD2-D-R01
bleiben vor einem eigenen Mergeauftrag erforderlich.

Der Repositorydiff enthält ausschließlich Markdown. Die reguläre CI-Auswahl
muss `docs` auswählen und `web` ausschließen; kein Web-Job wird angefordert.
Der tatsächliche Head, der Test-Merge-Stand und die aktuellen CI-Ergebnisse
werden in Draft-PR #411 und #406 gebunden. Historische V01-CI wird nicht als
Nachweis des neuen Heads ausgegeben. Keine neuen Tests am echten Bestand,
keine Produkt-/Methodenänderung und keine Wiederholung historischer Produktion.
