# Paarlinienprofil und Schwierigkeit 0.2 (#139 B/C)

Implementierungsvertrag zu VB-139-BC2, B-D01/B-D02, festgelegt vor der
Implementierung am 15.10.2026. Basis: `b900b39eda01b0a6ad8ffa2c11cbaef483cf982b`.

## Regel und unabhängige Prüfung

`paired-lines-mono` und `paired-lines-color`, jeweils Version 1, starten unbekannt.
Zuerst vollständige Einzellinieniteration. Danach alle ungeordneten Zeilenpaare,
anschließend Spaltenpaare lexikografisch; nach einer Änderung erneut Linieniteration
und Paarfolge von vorn. Nicht benachbarte Paare sind eingeschlossen.
Für jede Kreuzung werden alle in der vollständigen Kreuzlinie unterstützten
Wertepaare berechnet. Die Projektion aller damit verträglichen Belegungspaare
der gewählten Linien ist die neue Domain. Leere Relation bedeutet Widerspruch.
Jede Gesamtlösung bleibt enthalten; keine Zielmatrix/Eindeutigkeitsannahme,
probeweise Rasterfortsetzung oder Diagnose-Suche dient als Prämisse.

Der Solver koppelt Zellautomaten. Der Prüfer baut unabhängig ganze Blockintervalle
mit Pflichtseparatoren auf und synchronisiert deren beschriftete Intervalle.
Er rekonstruiert Kreuzungsrelationen und Projektionen ohne Solverimport.
Vollständige Belegungslisten dienen ausschließlich kleinen Testorakeln.
`stalled` verlangt alle Einzel- und Paarlinien ohne Fortschritt; Budgetende
ist `aborted`. Ein vollständiges Raster wird zusätzlich durch Runextraktion geprüft.

## Wire und Kompatibilität

Logik v1/v2 und ihre Hashes bleiben unverändert. Neue Profile unterscheiden sich
von `full-line-*` durch ID und `deduction=all-paired-line-supported-values`.
Version, `start=unknown`, `search=false` und kanonische Hashbildung bleiben gleich.
Die bisherigen Standardaufrufe und Proofs v1/v2 bleiben erhalten.

`picross-proof-v3` behält die neun Top-Level-Felder alter Proofs. Schritte haben
`kind=line|pair`, `axis`, `indices` (ein Index oder zwei aufsteigende Indizes),
`changes`. Änderungen haben `row`, `column`, `before`, `after`, geordnet nach
Zeile/Spalte. Sie umfassen genau alle erzwungenen Änderungen. Widerspruchsreferenzen
haben `kind`, `axis`, `indices`. Zusätzliche Hilfsrelationen sind nicht zulässig.
Der Prüfer bestätigt Profil, exakte Änderungen, Vorzustand und Abschluss selbst.

Die Auswahl erfolgt ausdrücklich per Profil-ID. Neue Produktionsmanifeste
`picross-image-manifest-v2` und Reparaturplan/-verlauf/-manifest v2 führen diese
Auswahl über `certification={profile,max_pair_work,max_pair_records}`. Alte
Manifestversionen erlauben ausschließlich ihre bisherigen Linienprofile.
Der Kandidaten-/Matrixvertrag bleibt gleich: Profilwahl verändert keine Bildbytes.
Neue Nachweise führen zusätzlich eine eigene `*-baseline-proof.json` und
`*-assessment.json`; sämtliche Dateien werden im jeweiligen Inventar gebunden.
Reparaturen verwenden dieselbe Konfiguration kumulativ über alle Kandidaten;
der frische Abschluss erhält sein vorher festgelegtes eigenes Budget.

## Ressourcen

Vor Ausführung festgelegte Defaults: 20.000.000 elementare Paararbeitsoperationen
und höchstens 250.000 gleichzeitig gehaltene Relations-/DP-Einträge je Budget.
Zulässige Parameter: 0..100.000.000 Arbeit, 0..1.000.000 Einträge. Jede untersuchte
Transition, Intervallkompatibilität und Produktkante wird innerhalb der Schleifen
gezählt; jeder neu gespeicherte Graph-/DP-/Relationseintrag wird vor Allokation
gegen das Speicherbudget geprüft. Freigegebene temporäre Tabellen geben nur
Speicherbelegung zurück, niemals Arbeit. Berichte nennen Arbeit und Peak-Einträge.
Die Grenze ist ein nachvollziehbares Strukturmaß, kein behauptetes OS-/RSS-Limit.
Die konservativen Defaults begrenzen insbesondere schwierige 100er-Paarprodukte;
sie garantieren keine Lösung jedes erlaubten Eingangs.

Zeit-/Linienbudgets gelten weiter; kein neuer CI-Deckel. Verifikation besitzt
eigene begrenzte Arbeit oder teilt ausdrücklich das kumulative Aufrufbudget.
Neue Abbruchgründe: `pair_work_limit`, `pair_memory_limit`. Keine unvollständige
Relation wird angewendet. Proof-v3 nutzt die bestehenden 8-MiB-Mono-/64-MiB-Farblimits
und höchstens W·H·K informative Schritte. Assessment höchstens 64 KiB.

## Schwierigkeit und Freigabe

**Freigegebene Folgearbeit SD / [#235](https://github.com/venomenon328/picross/issues/235):**
[Rätselschwierigkeit](PUZZLE_DIFFICULTY.md) führt nach SD-C eine neue aktive
Bewertungsmethode ein. Die nachstehenden 0.2-/R4-Nachweise und historischen
Einstufungen behalten ihren Vertrag. SD-A ergänzt R0–R3-Instrumentierung und
eine eigene synchrone Bewertungsspur, ohne bestehende Proofverträge zu lockern.
SD-B bindet feste Grenzen an unabhängige synthetische Referenzen, nicht an den
realen Katalog. Stufe 5 bleibt auch mit reiner Linienlogik erreichbar.
Die neue kalibrierte Methode ist noch nicht implementiert; der separate
[SD-A-Analysator](SD_ANALYZER.md) prüft optional ausdrücklich übergebene
Baseline-/Paarproofs, zählt ihre Schritte aber nicht als Bewertungswellen.
`assess` bleibt der nachstehend
beschriebene begrenzte Bericht, kein vollständiger R0–R3-Analysator.

`picross-difficulty-0.2` ergänzt genau R4. Nur separat unabhängig geprüftes
`full-line-* / stalled` plus vollständiger geprüfter Paarproof derselben Logik
belegen Notwendigkeit: L5, `linienübergreifend / besonders hoher logischer Anspruch`.
Ein abgebrochener Baseline-Lauf oder bloße Verwendung eines Paarschritts genügt
nicht. Linienfälle behalten R0–R3/L1–L5; keine nachträgliche Umdeutung von 0.1.
Die Instrumentierung belegt nur R4-Notwendigkeit, keinen vollständigen R0–R3-
Analysator und keine menschliche Kalibrierung. Umfang/Zeit bleiben getrennt.

Authoring 0.5.0 erlaubt diese Profile ausdrücklich. Alte 0.4.x-Snapshots und
Schwierigkeit 0.1 legitimieren keinen Paarproof. ZA-1 prüft die Baseline und
Assessmentdatei frisch, bindet das Profil im neuen Export-/Inspektionsformat v4
und erhält sämtliche Herkunfts-, Masken-, Freigabe-, Kategorie- und Produktgrenzen.
Manuelle Ableitungen binden ihre neue Profilwahl ausdrücklich im Plan; alte
Autorisierungen/Originale werden nicht umgeschrieben. Kein Solver im Spiel.
Eine bereits mit Paarprofil geprüfte Referenz darf nicht in einen alten
Reparatur-/Ableitungsvertrag zurückfallen; auch Zwischenstufen führen die
ausdrückliche Paarbindung weiter.

### Konkrete Produktionsbindungen

Die Konfiguration hat genau drei Schlüssel, beispielsweise
`{"profile":"paired-lines-color","max_pair_work":20000000,"max_pair_records":250000}`.
Bei Bildimporten heißt die Baseline `<variant>-baseline-proof.json`, das Assessment
`<variant>-assessment.json`. Im Reparaturbundle liegen sie neben jedem
Kandidatenproof und dem frischen Abschlussproof mit demselben Namenspräfix.
Die vollständigen Dateiinventare und Reparatur-ID binden diese zusätzlichen Bytes.
`picross-deduction-assessment-v1` führt Logik-/Profilhash, tatsächliche SHA-256
beider Proofdateien, beide Status-/Prüfflags, Outcome, R4-Notwendigkeit, L5/Label,
Vertrauen, begrenzten Instrumentierungsumfang und keine geschätzte Lösungszeit.
Eine frische Inspektion rekonstruiert den Inhalt; ursprünglich negative Prüfflags
werden nicht nachträglich zu einer Produktionsfreigabe aufgewertet.

Handoff-v2 ergänzt `candidate.certification`. `difficulty` bindet Methode 0.2,
`profile_hash`, `evidence` als Pfad genau dieses Assessments und bei notwendigem
R4 zusätzlich `logical_demand` mit dem obigen Label. Der neue Regelwerksnapshot
muss seine Version 0.5.0 selbst ausweisen; eine umbenannte Handoff-Versionsangabe
allein genügt nicht. Die bestehenden Freigabe-/Inventarbindungen bleiben Pflicht.

| Ableitung mit neuem Paarprofil | Neuer technischer Vertrag |
| --- | --- |
| Feste manuelle Mono-Entfernung | `picross-manual-edit-plan-v2` mit `certification`, `picross-manual-candidate-v2`; Proof/Baseline/Assessment im Bundle |
| Fester bearbeiteter Mono-Import | `picross-fixed-mono-import-plan-v2` mit `certification`, Importmanifest v2 |
| Redaktioneller Farbraster-Neuentwurf | `picross-editorial-raster-redraw-v2` und `picross-editorial-raster-redraw-plan-v2` mit `certification` im Plan |
| Feste Farbkorrektur | `picross-editorial-fixed-cell-derivation-v2` und `picross-editorial-fixed-cell-plan-v2` mit `certification` im Plan |

Die externe menschliche Autorisierung v1–v4 bleibt ihrem jeweiligen Pfad
zugeordnet. Ein neuer Plan braucht neue tatsächliche Bindungen; dieser Vertrag
erteilt keine Änderungsbefugnis an alten Originalen. ZA-1 liefert
`picross-target-inspection-v4` und `picross-target-export-v4` mit
`deduction={profile,profile_hash,assessment}` sowie gegebenenfalls der bisherigen
manuellen Autorisierung. Registrierung prüft diese Exporte frisch offline.

Der gesonderte CLI-Aufruf `assess` erzeugt `picross-quality-report-v1`:
Diagnose-A-Dateicheck, geprüfte Deduktion, Baseline, Umfang, Difficulty und
Redaktion bleiben getrennte Felder. Eine A-Meldung `unique` ist als berichtet
gekennzeichnet; ihr Checker bestätigt keine erschöpfende Suche. Weder eine
Eindeutigkeitsmeldung noch bloße Profilnutzung erzeugt R4 oder eine Endfreigabe.

## Prüfzuordnung

Feste synthetische Mono-/Farbfälle B-T01/B-T02, Transponate, nicht benachbarte
Paare, partielle Domains, Farbkontakt/-abstand und kleine vollständige Orakel.
Negativtests für überstarke/fehlende/veraltete Änderungen, falsche Bindungen,
Widerspruch/Fixpunkt/Abschluss, Ressourcen-/Dateigrenzen und fehlende Freigaben.
Durchstiche für Import, Reparatur, manuelle Ableitungen, ZA-1 und Registrierung
verwenden ausschließlich künstliche Pakete. Alte Proofs/Diagnose/Exporte bleiben
Regressionen. Tatsächliche Resultate, Head/Basis/Test-Merge und getrennter
Selbstreview werden im gemeinsamen Draft-PR dokumentiert. #139 bleibt offen.
