# SD2-A: Technischer Analysevertrag

Stand: 25.10.2026 · Vertrag 1.0 · #403, Umsetzungsvorbereitung V2.
Vertragsauftakt vor Regel- und Formatcode auf Basis
`7709a50d0f34482e5be54c17cc5f0a6167ee8821`.
[Fachvertrag](PUZZLE_DIFFICULTY_V2.md), [Altanalyse](SD_ANALYZER.md),
[Freeze](SD_CALIBRATION.md) und [CLI](../tools/puzzle_production/README.md).

## 1. Grenzen und Identität

Der getrennte Weg heißt `picross-sd2-analyzer-1`, Regeln `sd2-rules-1`.
Dies ist keine Methode 0.4 und kein neuer Zertifizierungsproof. Keine Endnote,
Kalibrierung, Katalog-/Produktionsaktivierung oder Änderung der dreizehn
0.3-Freezequellen. Alle R0–R4-Namen und alten Aufrufe bleiben unverändert.
Der Kern akzeptiert ausschließlich validierte Logik v1/v2 vom unbekannten
Raster, bis 100 je Achse, 1…8 Farben plus Leer, gleiche Farben mit Abstand,
verschiedene ohne Pflichtabstand. Keine Lösung, Suchhypothese oder Eindeutigkeit.

## 2. Endliche Regeln

Nullbasierte Positionen; Leerbit 1, Farben einzelne Bits. Jede Folgerung schneidet
die alte Domain. Für Block i sind Länge l(i), Farbe c(i), Pflichtabstand g=1
bei gleicher Nachbarfarbe, sonst 0. G(i) ist das geometrische Startintervall
aus gepackten Vorgängern und Nachfolgern unter ausschließlich diesen Angaben.
Überfüllung ist Widerspruch. L(i) entsteht einmalig aus G(i) durch lokale Prüfung:

- Jede Zelle des Kandidaten erlaubt c(i).
- Kein direkter Nachbar ist bereits Singleton c(i).
- Bei gleichfarbigem Vorgänger/Nachfolger erlaubt die unmittelbar angrenzende
  Separatorzelle Leer und liegt innerhalb der Linie.

Diese notwendigen Bedingungen betrachten weder andere Kandidaten noch die
gemeinsame Abdeckung mehrerer bekannter Füllungen. Jeder wirkliche Blockstart
überlebt. Sichere Grenzen und Leerfelder schränken damit gewöhnliche Überlappung
ein, ohne vollständige Linienlogik zu verwenden.

| Regel | Voraussetzung und exakt erlaubte Folgerung |
| --- | --- |
| `E0-empty` | Keine Hinweise: alle Zellen leer. |
| `E0-packed` | Mindestlänge gleich Linienlänge: einzige Packung; größere Mindestlänge: Nullprojektion als Widerspruch. |
| `E0-cleanup` | Maximale bereits singleton-bestimmte Farbruns entsprechen exakt der gesamten Hinweisfolge: alle übrigen Zellen leer. |
| `E1-overlap` | Für jeden Block Schnitt aller Intervalle aus L(i) färben. Leeres L(i): Widerspruch. Keine Nachbarkandidatenpropagation. |
| `E1-exclusion` | Farbe an Position ausschließen, wenn kein lokaler Kandidat dieser Farbe sie abdeckt. Leer bleibt erlaubt. Leeres L(i): Widerspruch. |
| `E1-anchored` | Jeden maximalen Singleton-Farbrun unabhängig betrachten. Besitzer sind gleichfarbige Blöcke mit einem lokalen Kandidaten, der den ganzen Run enthält. Kein Besitzer: Widerspruch. Genau ein Besitzer: Schnitt seiner diesen einen Run enthaltenden Kandidaten färben; bei genau einem Start außerdem diese Farbe unmittelbar davor/dahinter ausschließen. Mehrere Besitzer: kein Schluss. Einschränkungen verschiedener Runs nicht als neue Voraussetzungen kombinieren. |
| `E2-combination` | Lokale Kandidaten bis zum unten definierten gemeinsamen Fixpunkt reduzieren und konservativ projizieren. |
| `E3-support` | Exakte Unterstützung aller vollständigen Belegungen der Linie unter allen Domains; Zellautomat im Erzeuger, unabhängig implementierter Block-DAG im Prüfer. |

E2 beginnt mit L(i), entfernt Kandidaten ohne geordneten disjunkten unmittelbaren
Vorgänger-/Nachfolgerkandidaten unter g und betrachtet jede Zelle ohne Leer:
kein möglicher Besitzer ist Widerspruch; genau ein Blockbesitzer beschränkt dessen
Kandidaten auf solche, die diese Zelle abdecken. Beides bis zum Fixpunkt wiederholen.
Leere Blockmenge ist Widerspruch. Projektion erlaubt Farbe nur in der Vereinigung
ihrer verbleibenden Kandidaten und schließt Leer nur im Schnitt aller Kandidaten
eines einzelnen Blocks aus. Keine Prüfung kompletter optionaler Lücken oder
gemeinsamer alternativer Besitzer; dies bleibt E3. Kandidaten werden nur entfernt,
daher endliche Terminierung und Erhalt jeder wirklichen Belegung.

Familie Ek enthält sämtliche Regeln bis k. Jede Stufe wird vollständig über beide
Achsen aus demselben Vorzustand ausgewertet, auch gelöste Linien zur Fehlerkontrolle.
Die erste produktive Stufe wird verwendet; nach jeder Welle Neustart bei E0.
Alle produktiven Regeln/Linien bleiben im Beleg; Zell-/Wertverluste werden einmal
vereinigt. Widerspruch hat innerhalb der vollständig geprüften Stufe Vorrang;
Nullschnitt an Kreuzungen ebenfalls. Terminalwelle nie anwenden. Ohne Fortschritt
in E0…E3: `solved` bei ausschließlich Singletons, sonst `stalled`.
Ausgabeordnung: Zeilen vor Spalten, Index, obige Regelreihenfolge, Zellkoordinaten.

### Hand- und Gegenbeispiele (ausschließlich synthetisch)

`?` volle Domain, `.` Leer, `A/B` sichere Farben:

- `.????`, A3: L={1,2}, E1-overlap bestimmt Positionen 2 und 3: `.?AA?`.
  Ohne leeren Rand ergibt `?????` nur `??A??`; sechs Unbekannte haben keinen Schnitt.
- `A????`, A3: einziger Besitzer des Randankers mit Start 0;
  E1-anchored ergibt `AAA.?`. `??A??`, A1/A1 bleibt mehrdeutig zugeordnet.
- `??A?A??`, A3: lokale Starts {0,2,4}; jeder Anker einzeln erlaubt zwei Starts.
  E1 macht keinen Fortschritt. Erst gemeinsame Abdeckung beider Anker in E2
  erzwingt Start 2 und `..AAA..`. Damit werden alte R2-Schlüsse nicht pauschal einfach.
- `???A.??`, A1/A2: E0…E2 ohne Fortschritt; E3 schließt A an Position 1 aus.
- A2/B2 in Länge 4 ist direkt `AABB`; A2/A2 braucht Länge 5 `AA.AA`.
- Ein volles 3×2-Rechteck hat fünf produktive Linienbegründungen, aber nur sechs
  neue Singletons; sein Umfangsproxy ist zwei horizontale Abschnitte der Länge 3.

## 3. Drei Rohprofile, exakte Messdefinitionen

Alle Zähler nichtnegative Ganzzahlen. Rationale Messwerte sind gekürzte
`[Zähler,Nenner]` mit positivem Nenner; undefinierte Quotienten sind `null`.
Leere Summen/Maxima sind 0, höchste nicht benutzte Familie null. Keine Floats in
fachlichen Resultaten, keine Zeit-/Hardware-/UI-Merkmale. Keine Bewertung aus
einer unvollständigen Analyse. Präfixmetriken bleiben ausdrücklich Präfixmetriken.

N=W·H, K=Vordergrundfarbzahl. Pro Welle O=offene Zellen (Domaingröße >1),
L=offene Linien beider Achsen, P=produktive offene Linien. Gelöste Linien fehlen
in L und P. Jede Welle besitzt mindestens eine Änderung und daher O,L>0.
Für eine einmal zusammengeführte Änderung seien a,b Domaingrößen vorher/nachher.

| Profil/Feld | Zählweise, Nenner und Nullfall |
| --- | --- |
| `demand.highest_family`, `family_waves`, `family_line_applications`, `rule_applications` | Höchste benötigte Familie; Häufigkeiten produktiver Wellen, Linien und Unterregeln. Häufigkeit ist kein Gewicht für mehrfach begründete Zellen. |
| `demand.information_by_family` | Je Familie Summe (a−b)/(N·K). Über alle Wellen höchstens 1. Partielle Farbverluste zählen proportional zu ursprünglichem K; keine Farbzahlstrafe. |
| `demand.strong_information_fraction` | Summe des obigen Anteils für E2/E3. |
| `demand.trajectory` | Je Welle `family`, `new_singletons`, `partial_changes`, `restricted_context_cells`, `interacting_blocks`, `ambiguous_required_cells`. Kontext: Summe eingeschränkter Positionen bzw. Hinweisblöcke über produktive Linien; eine Kreuzungsposition kann hier zweimal vorkommen. Kein Nachweis einer minimalen Prämissenzahl, kein zusätzlicher Informationsgewinn. Mehrdeutigkeit gemäß Zustandsdefinition unten, ausschließlich offene Linien. |
| `search.trajectory` | Je Welle `offer=P/L`, `gain=Σ((a−b)/(a−1))/O`, `changed_fraction=Änderungspositionen/O`, `singletons_per_productive_line=neue Singletons/P`, `strain=(1−offer)(1−gain)`, `progress_before=bereits bestimmte Zellen/N`, `state` und `bottleneck`. Teilfortschritte bleiben separat sichtbar. |
| `search.bottleneck_phases` | Maximale zusammenhängende Wellenfolgen mit offer≤1/4 und gain≤1/4; exakt `start,end,duration,stage,peak_strain`. Indizes nullbasiert, end exklusiv. stage `early` wenn erste Welle progress_before<1/2, sonst `late`. Schwelle ist deskriptives Messkriterium, keine kalibrierte Note; auch einfache Engstellen sichtbar. |
| `search.bottleneck_waves`, `longest_bottleneck`, `peak_strain` | Summe Dauern, Maximum Dauer, größter Wellenstrain; leere Folge 0. Frühe/späte und wiederkehrende Phasen bleiben einzeln erhalten. |
| `workload.structure` | `width,height,cells,colors,total_clues,total_clue_length,clue_length_histogram,short_blocks,adjacent_color_changes,mandatory_gaps,geometric_slack`. Kurze Blöcke Länge≤2; Histogrammschlüssel dezimale Länge, positive Häufigkeit. Slack=Summe max(0,Linienlänge−Mindestpackung). Keine pauschale Farb-/Kleinzahlbewertung. |
| `workload.trajectory` | Je Welle `changed_cells,new_singletons,partial_changes,removed_values,first_changed_cells,filled_singletons,empty_singletons,fill_spans,empty_spans,isolated_fills,fill_run_lengths`. Nur neue Singletons werden zu Strichproxies; partielle Ausschlüsse sind keine Eingaben. |
| `workload.cell_change_events`, `unique_changed_cells`, `unique_partial_cells`, `new_singletons`, `partial_change_events`, `removed_values` | Ereignissummen versus Positionsvereinigung getrennt; Singleton einer Position entsteht höchstens einmal. |
| `workload.fill_spans`, `empty_spans`, `isolated_fills` | Summe der jeweiligen Wellenproxies, keine gemessenen Klicks oder Gesten. |

`state` hat exakt `open_lines,solved_lines,open_cells,local_candidates,
geometric_candidates,placement_freedom,ambiguous_required_cells,
unique_owner_required_cells,restricted_cells,color_options,open_blocks,
open_short_blocks,undetermined_blocks,undetermined_short_blocks,open_hint_colors`.
Alle Kandidaten-/Besitzerwerte beziehen sich auf offene Linien im Vorzustand.
G/L wie §2, jeweils vor E2. `placement_freedom` ist Summe max(0,|L(i)|−1)
geteilt durch Summe max(0,|G(i)|−1), bei Nenner 0 null. Besitzer einer Pflichtzelle
(Leer ausgeschlossen) sind verschiedene abdeckende Blöcke; >1 mehrdeutig, =1
eindeutig. `restricted_cells` zählt eingeschränkte Positionen in offenen Linien.
`color_options`=Summe der erlaubten Vordergrundwerte in offenen Rasterzellen
geteilt durch O·K, bei O=0 null. Diese Werte sind Zustandsindizien, keine neue
Ableitungsregel und kein globaler Lösungsmengen- oder menschlicher Zeitmesser.
`open_blocks/open_short_blocks` zählen Hinweise in offenen Linien, kurze mit
Länge≤2. `undetermined_blocks/undetermined_short_blocks` zählen davon diejenigen
mit mehr als einem lokalen Start. `open_hint_colors` zählt verschiedene Farben
in Hinweisen offener Linien. Damit bleibt kurze/farbige Hinweisstruktur auch am
jeweiligen Zustand sichtbar, getrennt von statischen Summen über alle Linien.

Strichproxy: maximal zusammenhängende neue Singletonpositionen derselben Farbe
je Zeile und separat je Spalte; `fill_spans`=Minimum der beiden Abschnittszahlen.
`empty_spans` analog für neue Leerzellen. Keine Orientierung bevorzugt, keine
Mischoptimierung oder Behauptung tatsächlich genutzter Striche. `fill_run_lengths`
ist das sortierte Histogramm beider Orientierungen zusammen (jede Position hat
zwei geometrische Ansichten); es wird nicht als zusätzliche Arbeitsmenge addiert.
`isolated_fills` zählt Positionen ohne neu bestimmte gleichfarbige orthogonale
Nachbarn. Lange Balken und verstreute Einzelfelder bleiben dadurch unterscheidbar.

## 4. Input-, Spur-, Bericht- und Dateiprotokoll

Eigene Formate: `picross-sd2-input-v1`, `picross-sd2-trace-v1`,
`picross-sd2-report-v1`, `picross-sd2-check-v1`, `picross-sd2-error-v1`.
Kanonisierung: sortierte Schlüssel, kompakt, UTF-8 ohne BOM, endliche JSON-Zahlen;
SHA-256 der kanonischen Bytes ohne LF. Geschriebene JSON-Dateien zusätzlich LF.
Unbekannte/doppelte Schlüssel, falsche Typen einschließlich bool statt Integer
sind ungültig. Hash ist Bindung, weder Signatur noch fachlicher Nachweis.

Input exakt `format,logic` mit normalisierter Logik v1/v2. Analysehash bindet diesen
Input und ist kein historischer Produktionshash. Runtimeadapter unverändert aus
`analysis_io`: Schema 2, 1…50 je Achse, numerische IDs 1…K auf c1…cK; Lösung erst
nach Ableitung separat validieren und vergleichen. Herkunft/Definitionsbytes,
ID/Runtime-Revision/Produktionsmodus bleiben getrennt von Engine-Logik.

Trace exakt `format,analysis_hash,analyzer,rules,parameters,waves,status,reason,
terminal,final_domains`. `parameters` exakt `{profile:"sd2-raw-profiles-1"}`.
Welle exakt `family,lines,changes`; Linienbeleg exakt `axis,index,rules`;
Regelbeleg exakt `rule,changes` mit `offset,before,after`;
vereinigte Änderungen exakt `row,column,before,after`. Domains sind Bitmasken.
Terminal null außer bei Widerspruch, dann vollständige nicht angewandte Welle.
Status `solved,stalled,contradiction,aborted`; reason null außer Abbruch mit
`time_limit,work_limit,rule_work_limit,wave_limit,trace_byte_limit,cancelled,
memory_limit`. Finaldomains sind immer der letzte atomar übernommene Stand.

Bericht exakt `format,result,result_hash,source,files,verification,target_check,
operation`. `result` exakt `analysis_hash,analyzer,rules,parameters,trace_hash,
status,reason,line_analysis_complete,line_fixpoint_confirmed,deduction_complete,
profiles,r4,method,level,confidence,estimated_minutes,explanation`.
`profiles` exakt `demand,search,workload` nach §3. method/level/confidence/minutes
immer null; explanation fester statusabhängiger Hinweis auf Modellproxies.
Vollständige Linienanalyse nur solved; Fixpunkt solved/stalled. R4 darf separat
vollständige Deduktion belegen, aber weder den Linienverlauf vervollständigen
noch in A eine Note erzeugen.

`source`, `verification`, `target_check`, `operation`, optionale `r4` und die
Dateibindungen behalten exakt die geschlossenen Unterfelder aus SD-A/analysis_io.
source: `sha256,bytes,kind,engine_logic_hash,definition_id,runtime_revision,
production_mode`; verification: `trace_verified,status,line_analysis_complete`.
target_check: `not_supplied,matched_complete,compatible_partial`.
operation: `analysis_limits,verification_limits,analysis_usage,verification_usage,
elapsed_seconds`; Limits `seconds,max_lines,max_rule_work,max_waves,max_pair_work,
max_pair_records`, Nutzung `lines,rule_work,pair_work,pair_peak_records`.
Diese Betriebsdaten und tatsächlichen Dateibindungen liegen außerhalb result_hash.
Der R4-Vertrag aus [SD-A](SD_ANALYZER.md) bleibt vollständig: beide ausdrücklich
übergebenen Originalproofs frisch unabhängig prüfen, Linienbaseline stalled und
passender vollständiger Paarproof sowie eigener stalled-Fixpunkt für Notwendigkeit.
Kein automatischer Paar-/Suchlauf; keine R4-Schritte in Wellen oder Profilen.

Neues Ausgabeverzeichnis exakt `input.json,logic.json,trace.json,report.json`,
optional gemeinsam `r4-proof.json,r4-baseline.json`. `files` bindet alle außer
report.json jeweils exakt mit `sha256,bytes`. Leser öffnet nur diese festen Namen,
keine Pfade aus Berichten; unbekannte Dateien, Links/Reparsepunkte ablehnen.
Eingang/normalisierte Logik maximal 2 MiB, Trace/Bericht jeweils 64 MiB, Proofs
unter ihren alten Limits. Kein vorhandenes Ausgabeziel überschreiben.
Fehler dürfen ein unvollständiges Bundle ohne Erfolgsbericht hinterlassen.
Checker bestätigt nur frisch vollständig geprüfte Bytes, nie nur einen Hash.

## 5. Ressourcen, Prüfung und CLI

Budgets wie SD-A: 120 s, 100000 Linien, 20000000 Regeloperationen, 80000 Wellen,
64 MiB Trace; Maxima 1000000 Linien/100000000 Regeloperationen. Nullbudgets
erlaubt. Kooperative Deadline, kein OS-RSS-Limit. Kandidaten und Zustandssignale
werden begrenzt innerhalb der Schleifen gezählt; eine lokale Linie hat höchstens
10000 Kandidaten. Vollständige Linienunterstützung bleibt polynomial begrenzt.
Byte-/Wellen-/Arbeitsende verwirft die gesamte begonnene Welle. Profilberechnung
und Bundleprüfung haben eigene vorab festgelegte Prüfbudgets; Abbruch erzeugt
keinen erfolgreichen Bericht. Betriebsabbrüche sind keine logischen Eigenschaften.

Unabhängiger Prüfer importiert keinen Erzeuger/Analyzer. Eigene Intervallmengen
statt Startlisten, eigene simultane E2-Elimination und unabhängiger E3-DAG;
rekonstruiert jede schwächere Stufe, vollständiges gleichstarkes Angebot,
Zusammenführung, Enddomains und Endstatus. Geteilte reine Formate/Messreducer
sind erlaubt; Orakel und handgerechnete Metriken prüfen diese zusätzlich.
Abbruchpräfix bestätigt nur enthaltene Schritte, nicht die historische Deadline.

Neue Module `sd2_analysis`, `sd2_rules`, `sd2_verifier`, `sd2_contract`,
`sd2_profiles`, `sd2_io`, `sd2_cli`. Unverändert wiederverwendet: contract,
analysis_contract-Budget/atomare Mergehelfer, analysis_io-Eingangsadapter/R4,
solver.line_support ausschließlich E3 und verifier.justified_support im Prüfer.

Geplante, erst mit Implementierung verfügbare Aufrufe:

```sh
python -m tools.puzzle_production.sd2_cli analyze --input <logic.json> --output-dir <neu>
python -m tools.puzzle_production.sd2_cli check --input <logic.json> --bundle <bundle>
```

Analyze zusätzlich `--input-kind logic|runtime`, beide R4-Dateioptionen und
`--verify-seconds,--verify-max-lines,--verify-max-rule-work`.
Beide Befehle `--seconds,--max-lines,--max-rule-work,--max-waves,
--max-pair-work,--max-pair-records` mit obigen Defaults. Kein --method oder
Katalogargument. Exit 0 für geprüfte solved/stalled/contradiction, 2 ungültiger
Input/Parameter, 3 ungültige Analyse, 4 Abbruch, 5 technischer Fehler.
CLI-Fehlerobjekt: format,status,line_analysis_complete=false,level=null,error,
message; Signalabbruch stattdessen reason=cancelled. Checkresult exakt
format plus verification-Felder, result_hash,file_bindings_verified=true,
report_verified=true,operational_measurements_verified=false.

## 6. Prüfzuordnung A01–A05

| Akzeptanz | Feste unabhängige synthetische Nachweise |
| --- | --- |
| A01 | Obige Handbeispiele einschließlich Zweianker-Kombination und allgemeiner Lückenlogik; schwache Regeln ohne Aufruf vollständiger Unterstützung. |
| A02 | Vollständige Mono-/Farblinienorakel für kleine Domainräume, zusätzliche längere Gegenbeispiele; falsche Stärke, fehlender gleichzeitiger Schluss, falsche Enddomains/Terminalstatus und Hashmanipulation abweisen. |
| A03 | Vollständige Mono-/Farbberichte, handgerechnete Proxy-/Nullfälle, frühe/späte/wiederkehrende Messphasen, Präfix/Widerspruch/Prüfabbruch ohne Note; frischer CLI-Durchstich. |
| A04 | Wiederholung, Achsentausch, beide Spiegelungen, Farb-ID-Bijektion; sämtliche skalaren Profile invariant, Achsenmaße transformieren; Teilfarbereignisse und Positionsvereinigung getrennt. |
| A05 | Unveränderte bestehende Analyse-/Ratingtests, Referenz-/Freezeprüfung aller 13 Quellen, alte CLI mit/ohne Methode; neue Formate werden vom alten Integrationsweg nicht als Rating akzeptiert. |

SD2-A-T01 und getrennter Selbstreview gehören zur Lieferung. Qualifiziertes
separates SD2-A-R01 am finalen Head und ausdrückliche Mergefreigabe bleiben offen.
CI wird aus dem vollständigen Diff ermittelt, ohne Änderung des Selektors.
