# Paarlinienprofil und Schwierigkeit 0.2 (#139 B/C)

Dokument-ID: `paired-lines`
Status: `active`
Zuständigkeit: Paarlinien-Deduktion, unabhängiger Proof und R4-Assessment.
Die historischen Produktionshüllen in diesem Dokument gelten nur für ihre
benannte Generation. Neue Übergaben folgen [ZA-1](ZA1_ADAPTER.md), aktuelle
Bewertungsmethoden [SD2](../difficulty/PUZZLE_DIFFICULTY_V2.md).

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

`assess` erzeugt den unten beschriebenen begrenzten R4-Bericht, keinen
vollständigen R0–R3-Analysator. Die eigenständigen Bewertungsmethoden, aktive
Defaultauswahl und Kalibrierung werden in [SD2](../difficulty/PUZZLE_DIFFICULTY_V2.md) sowie
dem lesbaren [0.3-Vertrag](../difficulty/PUZZLE_DIFFICULTY.md) geführt. Profile, Proofs und
historische Einstufungen werden durch eine spätere Methode nicht umgedeutet.

`picross-difficulty-0.2` ergänzt genau R4. Nur separat unabhängig geprüftes
`full-line-* / stalled` plus vollständiger geprüfter Paarproof derselben Logik
belegen Notwendigkeit: L5, `linienübergreifend / besonders hoher logischer Anspruch`.
Ein abgebrochener Baseline-Lauf oder bloße Verwendung eines Paarschritts genügt
nicht. Linienfälle behalten R0–R3/L1–L5; keine nachträgliche Umdeutung von 0.1.
Die Instrumentierung belegt nur R4-Notwendigkeit, keinen vollständigen R0–R3-
Analysator und keine menschliche Kalibrierung. Umfang/Zeit bleiben getrennt.

Historische Authoring-0.5.0-Eingänge erlaubten diese Profile ausdrücklich. Alte 0.4.x-Snapshots und
Schwierigkeit 0.1 legitimieren keinen Paarproof. Der damalige ZA-1-Vertrag prüfte die Baseline und
Assessmentdatei frisch, band das Profil im Export-/Inspektionsformat v4
und erhielt sämtliche Herkunfts-, Masken-, Freigabe-, Kategorie- und Produktgrenzen.
Manuelle Ableitungen binden ihre neue Profilwahl ausdrücklich im Plan; alte
Autorisierungen/Originale werden nicht umgeschrieben. Kein Solver im Spiel.
Eine bereits mit Paarprofil geprüfte Referenz darf nicht in einen alten
Reparatur-/Ableitungsvertrag zurückfallen; auch Zwischenstufen führen die
ausdrückliche Paarbindung weiter.

Die späteren Authoringgenerationen verwenden dieselben Profil-/Proof-/
Budgetregeln. Ihre äußeren Hüllen sind in [PW-B](../tools/PW_B_CONTRACT.md) und
[ZA-1](ZA1_ADAPTER.md) definiert. Die 0.5.0-/0.6.0- und v4-Bindungen unten
sind generationengebundene Kompatibilitätsformen, keine aktuelle Quellenroute.

### Konkrete Produktionsbindungen und historische Hüllen

Die Profil-/Proofregeln bleiben aktiv. Die folgenden Handoff-v2-/Export-v4-
Angaben beschreiben dagegen ihre historischen Originalgenerationen und versprechen
keinen heutigen Exportreader oder Writer. Aktuelle kreative Formen stehen in
[PW-B](../tools/PW_B_CONTRACT.md); die heutige Integration konsumiert ausschließlich
den aktuellen [ZA-1-Eingang](ZA1_ADAPTER.md).

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
R4 zusätzlich `logical_demand` mit dem obigen Label. Der zugehörige historische Regelwerksnapshot
muss seine tatsächliche Version 0.5.0 beziehungsweise 0.6.0 selbst ausweisen; eine umbenannte Handoff-Versionsangabe
allein genügt nicht. Die bestehenden Freigabe-/Inventarbindungen bleiben Pflicht.

| Ableitung mit neuem Paarprofil | Neuer technischer Vertrag |
| --- | --- |
| Feste manuelle Mono-Entfernung | `picross-manual-edit-plan-v2` mit `certification`, `picross-manual-candidate-v2`; Proof/Baseline/Assessment im Bundle |
| Fester bearbeiteter Mono-Import | `picross-fixed-mono-import-plan-v2` mit `certification`, Importmanifest v2 |
| Redaktioneller Farbraster-Neuentwurf | `picross-editorial-raster-redraw-v2` und `picross-editorial-raster-redraw-plan-v2` mit `certification` im Plan |
| Feste Farbkorrektur | `picross-editorial-fixed-cell-derivation-v2` und `picross-editorial-fixed-cell-plan-v2` mit `certification` im Plan |

Die externe menschliche Autorisierung v1–v4 bleibt ihrem jeweiligen Pfad
zugeordnet. Ein neuer Plan braucht neue tatsächliche Bindungen; dieser Vertrag
erteilt keine Änderungsbefugnis an alten Originalen. Der damalige ZA-1-Vertrag lieferte
`picross-target-inspection-v4` und `picross-target-export-v4` mit
`deduction={profile,profile_hash,assessment}` sowie gegebenenfalls der bisherigen
manuellen Autorisierung. Seine Registrierung prüfte diese Exporte frisch offline.

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
verwenden ausschließlich künstliche Pakete. Alte Proofs und Diagnoseformen behalten
ihre jeweils unterstützte Lesesemantik; abgelöste Exporthüllen bleiben historische
Referenzen mit ihren Originalbytes. Die tatsächlich nötigen Regressionen
wählt das aktuelle Paket nach [CI_WORKFLOW_V2](../ci/CI_WORKFLOW_V2.md), ohne historische
Produktionsreplays. Resultate, Head/Basis/Test-Merge und getrenntes Selbstreview
stehen im zugehörigen PR; aktuellen Paketstatus in #139 prüfen.

