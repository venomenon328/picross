# RP-1 bis RP-5: Deduktionskern, Bildproduktion und Reparatur

**Aktuelle Prüfregel (12.10.2026):** Konkrete Rätsel werden während ihrer Produktion
und Integration geprüft, niemals routinemäßig in CI. Keine rätselspezifischen
Unit-Tests anlegen. CI führt bei Werkzeugänderungen allgemeine Tests an festen
synthetischen Eingängen aus; reine Rätseldateien erhalten nur den schlanken
Inhaltspfad. Historische Korpusläufe sind nur im gebundenen Altcheckout verfügbar;
frühere Jobangaben sind abgelöst.
Maßgeblich: [CI-Policy](../../docs/CI_POLICY.md) und
[Regelwerk](../../docs/ai-workflows/PUZZLE_AUTHORING.md).

KAT-1 ergänzt [Kategorien und Zuordnung](../../docs/CATEGORIES.md): neue ZA-1-Exporte verlangen `--category-id` und `--categories`; Snapshot, Manifest v2, Zielregistry und Runtimeprojektion werden gemeinsam geprüft. `sync-runtime --checkout .` übernimmt geprüfte Metadaten in die Projektion, `check-registry --checkout .` prüft inklusive Paket-Replay. Alte Exporte bleiben prüfbar, benötigen zur neuen Registrierung aber einen kategorisierten Neu-Export.

ZA-1 ergänzt den allgemeinen Authoring-v2-Zieladapter und Datenregistrierung:
[CLI, Schemas und Fehlerverhalten](../../docs/ZA1_ADAPTER.md),
[Prüfzuordnung](../../docs/ZA1_VERIFICATION.md). Diese Befehle benötigen die
isolierte Image-Umgebung mit Pillow 12.3.0. Alte Pilotprofile bleiben erhalten.
Das reguläre Ziel unterstützt 1…8 Vordergrundfarben plus Leer. Ein ausdrücklich
beauftragter Rasterersatz verwendet `plan-update` → `update` mit
`--expected-definition-sha256`, höherer Runtime-Revision und neuer Paketrevision;
Identität, Slot, Kategorie und Reveal bleiben erhalten. Recovery nutzt weiterhin
`recover-registration`; Details und Grenzen im ZA-1-Vertrag. `register` allein
überschreibt weiterhin keine vorhandenen Inhalte.

KE-N1: `recover-registration` übernimmt gültige alte Runtime-v2-Snapshots in
Registrierungsjournal v2 bzw. Updatejournal v1 und stellt direkt einen vollständig
geprüften v3-Checkout her. Beide Snapshots müssen kanonisch und formatgleich sein.
Die gesamte Zielansicht wird vor Änderungen ohne Produktionsreplay geprüft;
Wiederaufnahme erlaubt nur exakt gebundene alte/neue Bytes oder die eigene
hergeleitete v3-Projektion. Fremde Änderungen erhalten alle Dateien samt Journal.
Kein nachgeschobenes Sync, keine realen Saveänderungen; Journal v1 bleibt gesperrt.
Feste Altformatregressionen: `tests/puzzle_production/test_ke_recovery.py`.

Python **3.11+**, ausschließlich Standardbibliothek, ohne Installation von Paketen,
Netzwerk-/Modellaufrufe oder P1-Abhängigkeit. Aus dem Repository-Root ausführen;
unter Windows einen tatsächlichen Python-Interpreter statt eines Store-Alias nutzen.
Fachvertrag: [Rätselproduktion](../../docs/PUZZLE_PRODUCTION.md).
Prüfzuordnung: [RP1_VERIFICATION.md](../../docs/RP1_VERIFICATION.md).
Farberweiterung: [RP2_VERIFICATION.md](../../docs/RP2_VERIFICATION.md).
RP-1/RP-2 sind nach unabhängigem Review über PR #42/#43 in `main` integriert.
RP-3-Bildbefehle benötigen die separate Image-Umgebung weiter unten; die bisherigen
Kernbefehle bleiben ohne Pillow nutzbar. [RP-3-Prüfzuordnung](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/docs/RP3_VERIFICATION.md).

## Aufruf an gespeicherten Beispielen

Die Ausgabe muss ein neuer Pfad ohne `proof.json`/`result.json` sein. Eine Wiederholung
verwendet einen neuen Pfad, damit ein altes Zertifikat nicht als neues Ergebnis erscheint.

```sh
python3 -m tools.puzzle_production solve --input tests/puzzle_production/fixtures/deductive.json --output-dir artifacts/rp1-example
python3 -m tools.puzzle_production verify --input tests/puzzle_production/fixtures/deductive.json --proof artifacts/rp1-example/proof.json
python3 -m tools.puzzle_production solve --input tests/puzzle_production/fixtures/unique-stalled.json --output-dir artifacts/rp1-unique-stalled
python3 -m tools.puzzle_production solve --input tests/puzzle_production/fixtures/color-four.json --output-dir artifacts/rp2-four
python3 -m tools.puzzle_production verify --input tests/puzzle_production/fixtures/color-four.json --proof artifacts/rp2-four/proof.json
python3 -m tools.puzzle_production solve --input tests/puzzle_production/fixtures/color-propagation.json --output-dir artifacts/rp2-propagation
python3 -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python3 -m tools.puzzle_production.benchmark --output-dir artifacts/puzzle-production
```

`solve` serialisiert den zunächst ungeprüften Nachweis und prüft die gespeicherte Datei
mit dem unabhängigen Prüfer. `verify` kann diese Datei in einem frischen Prozess
prüfen; `--report <datei>` speichert zusätzlich das Prüfungsergebnis. Jede CLI gibt
ein JSON-Ergebnis auf stdout aus. `proof_verified` bezeichnet die geprüfte Spur und
den beanspruchten Status, `certified` ist ausschließlich bei `solved` wahr.
Eine korrekt geprüfte Abbruchspur bleibt `aborted`, ohne Zertifikat.

| Status / Exitcode | Bedeutung |
| --- | --- |
| `solved` / 0 | Vollständiges gültiges Raster und unabhängig geprüfter Nachweis; `certified=true`. |
| `stalled` / 0 | Unvollständiger, unabhängig bestätigter Fixpunkt; kein Eindeutigkeits-/Mehrdeutigkeitsurteil. |
| `contradiction` / 0 | Unabhängig bestätigte unmögliche Linie nach den bewiesenen Einschränkungen. |
| `invalid_input` / 2 | Ungültiges oder nicht unterstütztes Logikformat/Parameter. Auch argparse-Aufruffehler verwenden 2. |
| `invalid_proof` / 3 | Manipulierter, unpassender oder fehlerhaft formatierter Nachweis. |
| `aborted` / 4 | Zeit-/Arbeitslimit, Abbruchsignal oder `MemoryError`; kein Zertifikat. |
| `technical_error` / 5 | Datei-/interner Laufzeitfehler; kein logisches Rätselurteil. |

Ein wohlgeformter Eingang mit überfüllter Linie oder unvereinbaren Hinweisen ist
`contradiction`, kein Formatfehler. SIGKILL und ein harter OS-Prozessabbruch können
keinen JSON-Abschluss garantieren; der übergeordnete Benchmark wertet sie als
nicht erfolgreich. Ergebnisse sind nur aus erfolgreich beendeten Aufrufen zu übernehmen.

## Versionierter Datenvertrag

Alle Objekte sind UTF-8-JSON. Unbekannte Schlüssel, doppelte JSON-Schlüssel,
NaN/Infinity, numerische Überläufe zu nicht-endlichen Werten, boolesche Dimensionen und versteckte Startannahmen werden abgewiesen.
Dimensionen liegen in 1..100, Rechtecke und 1D eingeschlossen. Hinweislisten sind
geordnet; Leerlinien verwenden `[]`, jeder Block positive Länge 1..100 und
`color="ink"` im alten Monoformat. Maximal 100 Hinweise pro Linie. Auch formal übervolle Listen bleiben
wohlgeformte, logisch widersprüchliche Eingänge.

Ein minimales vollständiges Beispiel für 1×1:

```json
{
  "format": "picross-logic-v1",
  "width": 1,
  "height": 1,
  "colors": ["ink"],
  "empty": "empty",
  "rules": {"id": "mono-gap-v1", "same_color_gap": 1},
  "initial_domain": ["empty", "ink"],
  "row_clues": [[{"length": 1, "color": "ink"}]],
  "column_clues": [[{"length": 1, "color": "ink"}]]
}
```

`initial_domain` ist eine Broadcast-Domain für **jede** Zelle, keine Matrix mit
Vorbelegungen. Der Leerwert und die stabile Vordergrund-ID bleiben getrennt;
Domainmengen werden als geordnete Arrays `["empty","ink"]`, `["empty"]` oder
`["ink"]` serialisiert. Intern nutzt RP-1 Bitmengen 1/2/3. RP-2 erweitert die
Bitmengen um Farben, ohne Kanalzerlegung. Keine Motive, Bilder, Lösungsmatrix,
Vorbelegungen oder Assetmetadaten gehören in den Logikeingang.

Kanonische Hashbytes: `json.dumps(obj, sort_keys=True, separators=(',', ':'),
ensure_ascii=False, allow_nan=False).encode('utf-8')`; **ohne** BOM/Abschlusszeile.
SHA-256 als 64 kleine Hexzeichen. Der Logikhash umfasst das vollständig validierte,
über `Puzzle.to_wire()` normalisierte Logikobjekt, einschließlich aller Regeln und
der Startdomain. Gespeicherte Dateien besitzen zusätzlich eine LF-Abschlusszeile.
Dateihashes wie `proof_sha256` umfassen die tatsächlich gespeicherten Bytes.
Zeitmessungen, Auswertungsreihenfolge und Betriebssystemdaten sind keine Logikidentität.

Das Regelprofil ist exakt:

```json
{"id":"full-line-mono","version":1,"start":"unknown","deduction":"all-line-supported-values","search":false}
```

Sein kanonischer SHA-256 ist
`e49e4cd74c4c4c02e08170ce670a40f48b82490a6bea52c3c764143d7a0af4b0`.
Es gibt kein auswählbares schwächeres/anderes Zertifizierungsprofil.

### Farbvertrag und Kompatibilität

Die ursprünglichen Monoformate, `mono-gap-v1` und `full-line-mono` Version 1 behalten
ihre Bedeutung und kanonischen Hashbytes. Ein vor RP-2 mit `main@b18a234` erzeugter
unveränderter [Referenzbeleg](../../tests/puzzle_production/fixtures/rp1-proof.json)
wird tatsächlich erneut eingelesen. Seine Herkunft und Dateihashes stehen im RP-2-Prüfbericht.

`picross-logic-v2` hat dieselben neun Top-Level-Felder wie v1, unterstützt jedoch
**1..8 Vordergrundfarben plus Leer**. Farb-IDs sind eindeutig, 1..32 ASCII-Zeichen
nach `[a-z][a-z0-9_-]{0,31}`; `empty` ist reserviert. Es gibt keine RGB-/Bildfelder.
Die Eingabepalette kann beliebig geordnet sein; `initial_domain` muss exakt
`["empty", *colors]` in dieser Eingabereihenfolge enthalten. Nach Validierung wird
die Palette lexikografisch sortiert; Hinweise behalten ihre Reihenfolge und binden
ihre semantische ID. Das normalisierte Objekt bestimmt den Logikhash. Eine andere
Reihenfolge derselben Palette ändert diesen Hash nicht; andere IDs/Regeln/Hinweise schon.

Die Regeln sind exakt
`{"id":"color-gap-v1","same_color_gap":1,"different_color_gap":0}`.
Gleiche Nachbarfarben brauchen Leer; verschiedene Farben können direkt berühren
oder durch Leer getrennt sein. Der gemeinsame Zellautomat berücksichtigt alle Farben.
Intern ist Leer Bit 0, Farbe i der normalisierten Palette Bit i+1. Domains sind
nichtleere Bitmengen; Wire-Domains folgen immer `empty`, danach der sortierten Palette.
Partielle Startdomains sind weiterhin unzulässig; Einschränkungen entstehen nur
durch Deduktion oder in isolierten Linientests.

Das zugehörige Profil ist exakt
`{"id":"full-line-color","version":1,"start":"unknown","deduction":"all-line-supported-values","search":false}`
mit SHA-256 `f63ee6c88e6baa9f6a22f386ae532482d7ffb7b9a2237867f0d7cd9960ab608f`.
`picross-proof-v2` nutzt dieselben Proof-Felder/Schrittregeln wie v1, jetzt mit
farbigen Domains. Logik v2 verlangt Proof v2 und das Farbprofil; v1 verlangt weiterhin
Proof v1 und das Monoprofil. Kein stiller Profilwechsel und keine frei auswählbaren Regeln.
Eine einzelne ausgeschlossene Farbe zählt auch bei noch mehrwertiger Restdomain
als Fortschritt und führt die kreuzende Linie erneut aus.

`picross-proof-v1` besitzt genau die Felder `format`, `logic_hash`, `profile`,
`profile_hash`, `steps`, `status`, `final_domains`, `contradiction`, `reason`.
Jeder Schritt beider Versionen hat `axis` (`row`/`column`), nullbasierten `index` und `changes`.
Jede Änderung hat nullbasierten `offset` sowie `before`/`after`-Domains. Sie umfasst
alle unabhängig erzwungenen Einschränkungen dieser Linie im rekonstruierten Zustand.
Die Reihenfolge der Änderungen ist aufsteigend; Linien ohne Fortschritt erzeugen
keinen Schritt. Der Prüfer erlaubt verschiedene zulässige Linienreihenfolgen.
`final_domains` ist die vollständige Domainmatrix nach Replay; kein Zielbild.
`contradiction` ist bei Widerspruch eine Linienreferenz, sonst `null`.
`reason` ist nur bei Abbruch `time_limit`, `work_limit` oder `cancelled`, sonst `null`.
Ein CLI-`MemoryError` liefert einen Abbruchbericht und keinen beanspruchten Nachweis.

`picross-result-v1` führt Status, `certified`, `proof_verified`, erfolgreiche
Logik-/Profilbindung (einschließlich des tatsächlichen Profils), Schritt-/Linienzahlen und getrennte Zeiten; Fehlermeldungen
führen `error`/`message`. Zusätzliche technische Berichtsfelder sind keine Beweisvoraussetzungen.
Eine erfolgreiche Prozessausführung ist von vollständiger Zertifizierung zu unterscheiden.
Python-API: zuerst `validate_logic`, dann `solve` und separat `verify`;
`solve(Puzzle, Budget, order)` allein liefert einen **ungeprüften** Nachweis.

## Separate Eindeutigkeitsdiagnose (#139/A)

```sh
python -m tools.puzzle_production diagnose --input tests/puzzle_production/fixtures/unique-stalled.json --output-dir artifacts/uniqueness-1
python -m tools.puzzle_production check-diagnosis --input tests/puzzle_production/fixtures/unique-stalled.json --bundle artifacts/uniqueness-1
```

Python-API: `diagnosis.diagnose(Puzzle, DiagnosisBudget)` liefert unabhängig
geprüfte Zeugenobjekte im Speicher; `diagnosis.diagnose_file(input_path, output_dir,
DiagnosisBudget)` schreibt das dateigebundene Bundle.
`diagnosis_verifier.verify_witness` prüft vollständige Matrizen durch eigene
Runextraktion ohne Solverimport. Kein Sollraster wird akzeptiert; Eingang bleibt
das strikte Logikformat v1/v2 mit Rechtecken/1D, 1..100 je Achse und 1..8
Vordergrundfarben im Farbformat. Keine zusätzliche Produktionszertifizierung.

| Diagnose / Exitcode | Voraussetzung |
| --- | --- |
| `unique` / 0 | Genau eine unabhängig geprüfte Lösung; Suchraum vollständig erschöpft. |
| `multiple` / 0 | Zwei verschiedene unabhängig geprüfte Lösungen; weitere Suche endet. |
| `no_solution` / 0 | Suchraum vollständig erschöpft, keine Lösung. |
| `unknown` / 4 | Untersuchung unvollständig, auch nach genau einer gefundenen Lösung. |
| `invalid_input` / 2 | Ungültiges Logikformat, Budget oder bereits vorhandenes Ausgabeziel. |
| `invalid_diagnosis` / 3 | Checker: beschädigte, unpassende oder ungültige Belege. |
| `technical_error` / 5 | Datei-/interner Fehler; kein logisches Negativurteil. |

Aufruffehler verwenden argparse-Exitcode 2. Alle JSON-Ausgaben setzen
`certified=false`. Fehler verwenden `picross-uniqueness-error-v1` mit `status`,
`error` und `message`. Harte OS-Abbrüche garantieren keinen Abschluss. Nur
geschriebene Berichte nach beendetem Aufruf übernehmen; Exitcode 4 kennzeichnet
ausschließlich eine Teiluntersuchung.

**Vollständigkeit und Reihenfolge:** `domain-dfs-line-support` Version 1 startet
mit voller Domain jeder Zelle. Der vorhandene Zellautomat entfernt ausschließlich
Werte ohne Unterstützung in einer zulässigen Linienbelegung. Jede tatsächliche
Lösung des aktuellen Zweigs bleibt erhalten. Nach vollständiger Linienpropagation
wird die erste Zelle mit kleinster mehrwertiger Domain gewählt (Gleichstand:
Zeile, Spalte). Ihre Werte werden aufsteigend untersucht: Leer, danach sortierte
Palette. Diese Zweige sind disjunkt und decken den Elternsuchraum vollständig ab.
Jeder Abstieg bestimmt mindestens eine weitere Zelle; Tiefe höchstens Breite·Höhe.
Unmögliche Linien verwerfen nur ihren aktuellen Zweig. Ein reversibler Änderungspfad
stellt beim Rücksprung den Elternzustand wieder her; iterative Tiefensuche vermeidet
Rekursionslimits und vollständige Rasterkopien je Knoten. Endmatrizen werden
separat direkt gegen alle Hinweise geprüft. Erschöpfung beweist daher Eindeutigkeit
beziehungsweise Unlösbarkeit; zwei verschiedene geprüfte Matrizen beweisen
Mehrdeutigkeit. Worst-Case-Aufwand bleibt exponentiell; Erfolg im Budget ist keine Zusage.

**Kumulative Budgets:** `--seconds` 120, `--max-lines` 100000 und `--max-nodes`
100000 standardmäßig; Zählergrenzen jeweils 0..1000000. Ein Knoten ist die Wurzel
oder ein betretenes Kind vor Propagation. Jede Linienauswertung und jede Zeilen-/
Spaltenprüfung eines Zeugen verbraucht denselben Linienvorrat. Kein Zweig erhält
neue Budgets. Die monotone CLI-Deadline beginnt vor Eingabelesen und umfasst
Schreiben/Neueinlesen sowie notwendige Prüfung der Zeugen; abschließende kleine
Berichtsserialisierung erfolgt danach. Kooperative Grenzen gelten zwischen den
durch 100 Zellen begrenzten Linienoperationen; kein hartes RSS-/OS-Limit.
`node_limit`, `work_limit`, `time_limit`, `cancelled` und `memory_limit` ergeben
`unknown`. Ein während der Prüfung abgebrochener Zeuge zählt nicht als Lösung.
Nullbudgets erlauben deterministische Abbruchproben. Zeitlimits garantieren
keine identischen Teilverläufe auf anderer Hardware.

**Dateivertrag:** Das Ausgabeziel muss neu/nicht vorhanden sein, auch ein leerer
vorhandener Ordner wird zurückgewiesen. Es enthält `input.json` als exakte
Eingabekopie, null bis zwei `solution-1.json`/`solution-2.json` und `diagnosis.json`.
Unvollständig geprüfte Kandidaten können unreferenziert zurückbleiben; nur
referenzierte Zeugen zählen. Fehler können eine Eingabekopie hinterlassen,
niemals einen erfolgreichen Bericht. Limits: Logik 2 MiB, einzelne Zeugen 512 KiB,
Berichte 64 KiB. 100×100 Werte mit maximal langen IDs passen ins Zeugenlimit.
Dateihashes umfassen tatsächliche Bytes einschließlich Abschlusszeile.

`picross-solution-witness-v1` hat exakt `format`, normalisierten `logic_hash`
und `matrix`: vollständige Zellmatrix aus Leer-/Paletten-IDs, keine Domains.
`picross-uniqueness-v1` hat exakt `format`, `tool` (`picross-uniqueness`, Version 1),
`method` (ID/Version, obige `branch_order`/`value_order`, `search=true`), `logic_hash`,
`status`, `search_complete`, `reason`, `certified`, `budgets` (`seconds`, `max_lines`,
`max_nodes`), `statistics` (`nodes`, `line_evaluations`, `witness_line_evaluations`,
`elapsed_seconds`), `input` und `witnesses`. Die letzten beiden binden `file`,
`sha256` und `bytes`. In der Speicher-API stehen unter `witnesses` stattdessen
Zeugenobjekte; `input` fehlt. `search_complete=true` gilt ausschließlich bei
`unique`/`no_solution` mit `exhausted`; `multiple` endet mit `two_solutions`.

`check-diagnosis` prüft Berichtskonsistenz, exakte Eingabebytes, referenzierte
Dateibindungen, vollständige gültige Zeugen und deren Verschiedenheit. Feste lokale
Dateinamen verhindern frei gewählte Pfade; Symlinks werden zurückgewiesen.
Sein `picross-uniqueness-check-v1` meldet `file_bindings_verified`, die Zahl
`witnesses_verified`, `reported_status`, `logic_hash`, `search_replayed=false`
und `certified=false`. `confirmed_status` ist nur mit zwei Zeugen `multiple`, sonst
`null`: keine unabhängige Bestätigung der erschöpfenden Suche oder Zertifizierung
für `unique`/`no_solution`. Dafür ist der Diagnosealgorithmus mit vollständiger
Suchraumabdeckung zu reviewen. Hashbindungen sind keine Signaturen. Der Checker
hat ein eigenes kumulatives Zeit-/Linienbudget; Abbruch liefert keinen Prüferfolg.

Ein Eindeutigkeitsurteil ersetzt kein Produktionsmanifest, keinen vollständigen
Deduktionsnachweis und keine redaktionelle Abnahme. Der verifizierte Linienfixpunkt
bleibt `stalled`, auch wenn die Suche `unique` ergibt. Import, Reparatur, ZA-1
und Schwierigkeit L1–L5 werden durch diese Diagnose nicht verändert.

## Paarlinienprofil und Schwierigkeit 0.2 (#139 B/C)

Der [Paarlinienvertrag](../../docs/PAIRED_LINES.md) ergänzt ausdrücklich gewählte
`paired-lines-mono`/`paired-lines-color` v1 und `picross-proof-v3`. Exakte Beziehungen
zweier beliebiger paralleler Linien werden nach dem vollständigen Linienfixpunkt
ausgewertet. Der getrennte Prüfer leitet sie selbst her. Standardaufrufe,
`full-line-*`, alte Proofbytes und Diagnose A behalten ihren Vertrag.

```sh
python -m tools.puzzle_production solve --input tests/puzzle_production/fixtures/unique-stalled.json --profile paired-lines-mono --output-dir artifacts/paired-example
python -m tools.puzzle_production verify --input tests/puzzle_production/fixtures/unique-stalled.json --proof artifacts/paired-example/proof.json
python -m tools.puzzle_production assess --input tests/puzzle_production/fixtures/unique-stalled.json --proof artifacts/paired-example/proof.json --baseline artifacts/paired-example/baseline-proof.json --report artifacts/paired-assessment.json
```

`solve` schreibt zusätzlich `baseline-proof.json` und `assessment.json`, prüft
beide Proofdateien unabhängig und berichtet die gemeinsame Arbeit unter
`certification_line_evaluations`/`certification_seconds`. `--max-pair-work`
(20.000.000) und `--max-pair-records` (250.000) begrenzen innere Arbeit und
gleichzeitig gespeicherte Struktureinträge, auch im unabhängigen Prüfer.
Verbrauchte Arbeit wird niemals zurückgesetzt; unvollständige Projektionen
werden nicht angewendet. Ressourcenende ist `aborted`, kein starker Fixpunkt.

`import-image` erhält dieselbe ausdrückliche `--profile`-Auswahl und Paarbudgets.
Es schreibt Manifest v2 mit `certification` und je Variante Baseline/Assessment.
Reparaturen binden diese Konfiguration im [Plan v2](../../examples/rp5/README.md).
Handoff-v2 bindet sie in `candidate.certification`; Regelwerk 0.5.0 ist Pflicht.
Alte Import-/Reparaturmanifeste und Authoring 0.4.x legitimieren keine Paarproofs.
Neue ZA-1-Exporte verwenden v4, unveränderte Linienfälle weiter v2/v3.

`assess` prüft die übergebenen gespeicherten Proofs frisch. Optionales
`--diagnosis <A-Verzeichnis>` ergänzt den unveränderten A-Dateicheck, ohne eine
erschöpfende Suche als unabhängig nachgewiesen auszugeben. Der Bericht trennt
`multiple`, `reported_unique_without_complete_deduction`, `diagnosis_incomplete`,
`line_logic_solved`, `paired_lines_solved` und vollständige Deduktion ohne
Notwendigkeitsbeleg. Difficulty 0.2 meldet R4/L5 nur bei geprüfter Linienbaseline
`stalled` und vollständigem Paarproof derselben Logik. Umfang, Zeit und
redaktionelle Freigabe bleiben eigene Angaben; kein vollständiger R0–R3-Analysator.

## Linienverfahren und Ressourcen

Solver: Vorwärts-/Rückwärtserreichbarkeit eines Zellautomaten aus Gap- und
Blockfortschrittszuständen, Aufwand O(n·(Summe der Blocklängen + Blockzahl + 1)).
Übervolle Linien werden vorher erkannt. Die Warteschlange führt betroffene
kreuzende Linien nach; nur Domainausschlüsse, kein Probing/Backtracking.
`--order rows-first|columns-first|reverse` bestimmt die deterministische Reihenfolge.

Prüfer: separat implementierter DAG mit Knoten (vollständige Blockzahl, verbrauchte
Zellen) und Kanten für ganze Blockintervalle samt Pflichtseparator bei gleicher
Nachbarfarbe oder ein Leerfeld. Unterschiedliche Farben benötigen keinen Separator.
Intervallkompatibilität verwendet eigene Präfixsummen je vorkommender Farbe. Vorwärts-/Rückwärtserreichbarkeit
liefert die unterstützten Intervalle. Aufwand höchstens O(n²·(Blockzahl + 1)),
Speicher O(n·(Blockzahl + 1)); keine vollständigen Belegungslisten. Der Prüfer importiert
keine Solverroutine. Gemeinsam sind Datentypen, Schema, Domains, Budget und Hashes.
Vollständige Endraster werden zusätzlich durch direkte Länge-/Farbrunextraktion geprüft;
Fixpunkte durch jede Zeile/Spalte, Widersprüche durch die angegebene unmögliche Linie.

CLI-Limits: **2 MiB Logikdatei**, **8 MiB Mono-/64 MiB Farbnachweisdatei**.
Auch 200 Linien mit je 100 Hinweisen und maximal langen Farb-IDs passen unter 2 MiB
in kanonischer Speicherung. Maximal **Breite·Höhe·Vordergrundfarbzahl** Proof-Schritte:
jeder Schritt entfernt mindestens einen Wert; jede Zelle behält mindestens einen
von anfangs K+1 Werten. Für Mono bleibt die Grenze Breite·Höhe; für acht Farben
auf 100×100 sind es 80000. Eine konservative obere kanonische Proof-Größe mit
einzelnem Wertverlust je Zelle/Schritt, längsten IDs und vollen Enddomains liegt unter
64 MiB; der Grenztest rechnet dies aus und prüft den Loader auch oberhalb der alten
8-MiB-Grenze. Zusätzlicher beliebiger JSON-Whitespace bleibt durch das Dateilimit begrenzt.
`--seconds` (Standard 120) und `--max-lines` (Standard 100000, höchstens 1000000)
gelten kooperativ für die ganze Solver-/Prüferarbeit; `--max-lines 0` demonstriert
einen kontrollierten Abbruch. Eine einzelne Linienauswertung ist durch die
Dimensionen polynomial begrenzt. Die CLI erzwingt kein OS-RSS-Limit.

**Vorab festgelegte RP1-/RP2-A05-Budgets:** je Referenzfall 120 Sekunden einschließlich
Solve, Serialisierung, frischer Prüfung und Prozessstart; je isoliertem Prozess
512 MiB gemessener Peak-RSS auf Linux. Der Benchmark misst selbstständige Solve-
und Verify-Prozesse via `getrusage(RUSAGE_SELF).ru_maxrss` (Linux-KiB → Bytes).
Zusätzlich setzt jeder Worker `RLIMIT_AS=1024 MiB` als hartes virtuelles Speicherlimit;
dies ist ausdrücklich **kein** RSS-Limit/-Messwert. Der Parent erzwingt das gemeinsame
120-Sekunden-Prozesslimit. Fehlende RSS-Messung führt zu `accepted=false` (Windows),
auch wenn der logische Lauf erfolgreich ist. Neue Ausgabepfade für Wiederholungen verwenden.

Referenzen: 40×40/100×100 verschachtelte Balken mit variierenden Hinweisen,
Leer-/Füllzellen und echter Propagation; zusätzlich 100×100 mit je zwanzig
Einserblöcken pro Linie und `C(81,20)=4694436188839116720` Belegungsmöglichkeiten
je unbekannter Linie. Der letzte Fall bleibt ein geprüfter unvollständiger Fixpunkt.
Farbreferenzen: `color-woven-40`/`color-woven-100` mit wechselnden zusammenhängenden
Farbblöcken in beiden Achsen, Leerfeldern und tausenden partiellen Domainänderungen.
`color-sparse-100` stammt aus einem dünn besetzten diagonalen Vierfarbenraster;
20 Einserblöcke je Linie mit unterschiedlichen Nachbarfarben erlauben
`C(100,20)=535983370403809682970` Belegungen pro unbekannter Linie. Der unabhängig
geprüfte Fixpunkt bleibt unvollständig. Die drei Mono-Referenzen bleiben unverändert.
Diese technischen Referenzen behaupten keine Motiv-/Pilotqualität.

## CI und Artefakte

[puzzle-production.yml](../../.github/workflows/puzzle-production.yml) läuft bei
PRs und Pushes nach `main` auf Ubuntu 24.04, Python 3.11+, lesenden Repositoryrechten
ohne projektspezifisches CI-Joblaufzeitbudget. Der eigene Testort liegt außerhalb des bestehenden
`tools`-Discoverys. `docs`, `product` und `preflight` bleiben unverändert aktiv.

`artifacts/puzzle-production/benchmark.json` (`picross-benchmark-v2`) bindet Source-Head,
Checkout/Test-Merge, Basis und Arbeitsbaum; Profil/Profilhash und Eingänge stehen
**je Fall**, kein pauschales Monoprofil für Farbläufe. Die bisherigen CI-Umgebungsnamen
`RP1_SOURCE_HEAD`/`RP1_BASE_COMMIT` gelten für den gemeinsamen Lauf weiter.
Pro Fall liegen Logik, Proof, Ergebnis,
frische Prüfung, getrennte Prozessmessdaten und Logs vor. Der CI-Artefaktname enthält
den Source-Head. Laufartefakte werden nicht eingecheckt. Ein anderer Head/eine neue
Basis braucht passend zugeordnete aktuelle Checks. #41/#42/#43 sind integriert;
Die Machbarkeitsphase #34 ist abgeschlossen; neue Produktionspakete benötigen eigene Aufträge.

## RP-3: isolierte Image-Umgebung und reale Befehle

Pillow **exakt 12.3.0**, ausschließlich für Bildbefehle/-tests. Die CI installiert
[requirements-image.txt](requirements-image.txt) in einer temporären venv. Lokal:

```sh
python3 -m venv .venv/rp3
.venv/rp3/bin/python -m pip install --only-binary=:all: -r tools/puzzle_production/requirements-image.txt
.venv/rp3/bin/python -m tools.puzzle_production import-image --input examples/rp3/source.png --design examples/rp3/design.json --output-dir artifacts/rp3-import
.venv/rp3/bin/python -m tools.puzzle_production export-p1 --bundle artifacts/rp3-import --variant area-128 --reveal examples/rp3/reveal.svg --name Fliegenpilz --output-dir artifacts/rp3-export
.venv/rp3/bin/python -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
```

Unter Windows entsprechend `.venv/rp3/Scripts/python.exe`; keine globale
Installation. Jedes Ausgabeziel muss **neu/nicht vorhanden** sein. Die mitgelieferte
[reale Quelle samt Produktionsbundle](../../examples/rp3/README.md) enthält bereits
einen offline öffnenden Vergleich: `examples/rp3/production/index.html`.
PNG/JSON/Briefing können ohne Dienst an ChatGPT/Codex übergeben werden.

### Entwurf, Normalisierung und Rasterverfahren

`picross-image-design-v1` hat exakt die Schlüssel des
[Beispielentwurfs](../../examples/rp3/design.json). `source_id` und Varianten-/Farb-IDs
folgen `[a-z][a-z0-9_-]{0,31}`, `empty` ist reserviert. Herkunft, Nutzungsgrundlage
und Briefing haben jeweils 1..4096 Zeichen. `working_mode` ist ausdrücklich
`faithful` oder `free`; Eingriffe sind im Briefing festzuhalten. Zielbreite/-höhe
1..100, Rechtecke/1D eingeschlossen. Palette 1..8 eindeutige Vordergrund-IDs und
`#rrggbb`-Werte; Mono verlangt genau `ink`. Hintergrund/Leer-RGB ist von jeder
Vordergrundfarbe verschieden, auch von Weiß. Palette wird nach ID sortiert.

PNG/JPEG: 32 MiB kodierte Bytes, 8 Millionen dekodierte Pixel, höchstens 8192 je
Quellachse, ein Frame. Beschädigte/trunkierte Dateien, Animation, andere Formate,
High-depth-Modi und unprofiliertes CMYK werden ausdrücklich abgewiesen. Unterstützt
werden 1/L/LA/P/RGB/RGBA sowie profiliertes CMYK. EXIF 1..8 einschließlich Spiegelung
wird angewendet. ICC wird mit LittleCMS nach sRGB, perceptual intent 0, konvertiert;
ungültiges/unpassendes ICC wird abgewiesen. Ungetaggtes RGB/Grau gilt als sRGB;
abweichendes PNG-gamma ohne sRGB-Tag/ICC wird abgewiesen. Alpha bleibt separat
erhalten. Normalisiertes PNG: RGBA, ohne EXIF/ICC/Text; Metadaten dokumentieren
Quellmodus/-maße, Orientierung, Behandlung und ursprünglichen ICC-Hash.

`crop=[left,top,right,bottom]` verwendet orientierte Quellpixel und muss vollständig
innerhalb des Bilds liegen. `fit=exact` fordert gleiche Seitenverhältnisse.
`contain` wählt ausdrücklich zentrierten Leerraum statt Strecken: Zielrechteck
mittels ganzzahligem Verhältnis, mindestens eine Zelle je Achse; Restpixel rechts/
unten. Sehr schmale Verhältnisse können dadurch um eine Zielzelle quantisiert sein.
RGBA wird auf den gewählten Hintergrund komponiert, dann mit Pillow BOX auf
Zellauflösung reduziert; Alpha wird separat mit BOX gemittelt. Unter
`alpha_below` (1..255) bleibt die Zelle leer. Rechnen erfolgt im kodierten sRGB,
keine behauptete lineare/perzeptuell optimale Bildabstraktion.

Höchstens acht Varianten: `area` nutzt im Mono-Modus Luminanz `< threshold`
(0..255), im Farbmodus nächstes RGB per quadriertem euklidischem Abstand zur
Palette einschließlich Leer. Gleiche Entfernung: Leer, dann lexikografische ID.
Bei Farbe ist der Area-Schwellwert wirkungslos und dennoch explizit gespeichert.
`contour` nutzt FIND_EDGES auf der Zellluminanz, innere Werte `> threshold`,
äußerste Zeile/Spalte stets leer (Pillow erhält dort sonst Quellwerte). Ausgewählte
Konturzellen werden Mono-ink oder der nächsten Farbe zugeordnet. 1D-Konturen sind
damit leer; Area bleibt nutzbar. Finale Werte sind ausschließlich IDs, keine
Zwischenfarben. Hinweise werden durch vollständige Länge-/Farbruns abgeleitet.

### Identität, Nachweis und P1-Grenze

`picross-image-candidate-v1` führt Revision 1, Quellen-ID, normalisierten Datei-
SHA-256, kompletten Entwurf/Variante, Werkzeug `rp3-image-1`, Pillow und tatsächlich
verwendete JPEG-/LittleCMS-/zlib-Versionen, Matrix und normalisierten Logikhash.
Sein SHA-256 verwendet die kanonischen JSON-Bytes des Kerns, ohne das `id`-Feld.
Messzeiten sind ausgeschlossen. Gleiche Normalisierung/Parameter/Versionen liefern
denselben Kandidaten. Unterschiedliche Codecbuilds können identische Pixel anders
komprimieren und erhalten deshalb unterschiedliche neue Kandidatenkennungen.
Bestehende Bundles behalten ihre tatsächlichen Produzentenbytes/-versionen.
Replay verlangt dieselbe Werkzeug-/Pillowversion und zusätzlich **exakte** RGBA-
Pixel-/Normalisierungsmetadaten-Gleichheit zur neu dekodierten Originaldatei,
neu berechnete Matrix/Hinweise und exakte Vergleichsrasterpixel. Schon ein
abweichendes Normalisierungspixel wird abgewiesen. JPEG/ICC-Rundungsunterschiede
werden damit nicht toleriert. Keine plattformübergreifende Byteidentität versprochen.

`picross-image-manifest-v1` bindet Originalbytes, normalisiertes PNG, Entwurf,
Kandidat, Logik, tatsächlichen Proof, Ergebnis, Zell-PNG, HTML und Briefing per
Dateihash. Alle Kandidaten bleiben vergleichbar, auch bei Fixpunkt/Abbruch.
Solver und unabhängiger Prüfer erhalten ausschließlich den bestehenden v1-/v2-
Logikeingang ohne Matrix/Bild/Motiv. `--seconds` 120 und `--max-lines` 100000
gelten getrennt pro Solver/Prüfer je Variante, keine gemeinsame Bildlaufzeitgrenze.
OS-Prozess-/RSS-Limits werden vom Import selbst nicht behauptet. CLI-Fehlercodes
entsprechen dem Kern; `import-image` meldet bei erfolgreicher Bundle-Erstellung
`produced`/0, auch wenn einzelne Kandidaten **nicht** zertifiziert sind.

`export-p1` rekonstruiert Original→Normalisierung→Matrix→Hinweise, prüft sämtliche
gebundenen Dateien und replayt den **geschriebenen** Proof unabhängig neu.
Ergebnisflags/Exitcode reichen nicht. Nur `solved`/zertifiziert und Singleton-
Enddomains gleich der beabsichtigten Matrix erlauben Export. Geänderte Raster,
Hinweise oder Farbsemantik binden andere Logik; ein alter unpassender Proof scheitert.
Reine RGB-/Assetänderungen können Logik erhalten, erfordern aber aktuelle
Herkunft/Identität/Assetbindung und separate Motivkontrolle.

Erster Adapter `rp3-p1-square-mono-1`: ausschließlich quadratisches Mono mit
mindestens einer Füllzelle, feste neutrale ID **F-04**, Revision 1..1000000,
Name 1..128 Zeichen erst nach Abschluss. Farb-IDs werden deterministisch auf
1..N, Leer auf 0 abgebildet; keine Domain-Bitmasken im P1-Raster. Schema 2 mit
exakt abgeleiteten Hinweisen, `res://art/f04.svg` als gebundener Reveal.
SVG: lokale begrenzte Shape-/Gradientressource, quadratische numerische Maße,
mindestens zwei Bildpixel je Zelle, höchstens 8192; keine externen Referenzen/
Ausführung/Entities. PNG-Enthüllungen und Rechteck-/Farbexporte werden in diesem
Adapter ausdrücklich abgewiesen. Kein automatisches Überschreiben/Registrieren
beliebiger Inhalte, keine öffentliche Importoberfläche oder zweite Spiellogik.

`picross-p1-export-v1` bindet Produktionsmanifest, Kandidat, Logik/Proof,
Definition/Revision, Farbzuordnung und Reveal-Dateihash. Der historische
RP3-Demo-Replay gehört nicht mehr zum aktiven Checkout. Für neue Inhalte gilt
ZA-1 mit expliziter Freigabe, Kategorie und Registrierung.

## RP-5: motivgeschützte Reparatur

Für ausdrücklich autorisierte feste manuelle Mono-Entfernungen ohne Suchlauf
unterstützt ZA-1 zusätzlich einen versionierten Replay-/Autorisierungsweg.
Vertrag, `--manual-authorization`, unveränderte Originalbindungen und v3-Export:
[ZA-1: manuelle Ableitungen](../../docs/ZA1_ADAPTER.md#autorisierte-manuelle-ableitungen).
Dieser Weg ersetzt weder RP-5 noch dessen Such-/Nachweisvertrag.

Die additive v2-Autorisierung unterstützt auch feste manuelle Einfügungen in
gespeicherten Mono-Rasterimporten und eine ausdrücklich an die Endauswahl
gebundene Randregel-Ausnahme. Beide RP-3-Bündel, sämtliche feste Edits und der
Endproof werden frisch geprüft; Original-ZIP/Handoff/Inventar bleiben unverändert.
Schema, Grenzen und synthetische Tests: [ZA-1-v2-Vertrag](../../docs/ZA1_ADAPTER.md).

Die additive v3-Autorisierung bindet bereits versiegelte feste Farbkorrekturen
mit nachträglicher menschlicher Motiv-/Parameterannahme. Sie replayt eine begrenzte
Kette gespeicherter Edits mit exakten Schutzmasken und prüft sämtliche RP-3-/RP-5-
Herkunfts- und Proofbindungen frisch. Originale bleiben unverändert, alle übrigen
Inhaltsgates einschließlich Randregel Pflicht. CLI bleibt `--manual-authorization`,
Exportformat v3. [ZA-1-v3-Vertrag](../../docs/ZA1_ADAPTER.md).

Die additive v4-Autorisierung unterstützt feste manuelle Farbkorrekturen aus
einer bereits freigegebenen Motivvorlage. Original-ZIP, Handoff, Inventar und
Motivfreigabe bleiben unverändert; Parameter werden am Originalimport geprüft,
danach die exakte feste Zellkette und sämtliche unabhängigen Proofs. Alle
Inhaltsgates und echte Endabnahme bleiben Pflicht. CLI und v3-Exportformat
bleiben gleich. [ZA-1-v4-Vertrag](../../docs/ZA1_ADAPTER.md).

V5 ergänzt ausdrücklich freigegebene feste Farbkorrekturen aus einem unabhängig
bestätigten ursprünglichen `stalled`-Direktimport. Die Originalquelle und der
vollständige Fixpunkt werden frisch geprüft; alle korrigierten Kindstufen
benötigen vollständige Zertifikate. Eigentümerbindung, Masken und Endabnahme
bleiben Pflicht; v1–v4 werden nicht gelockert. CLI/Exportformate bleiben gleich.
[ZA-1-v5-Vertrag](../../docs/ZA1_ADAPTER.md).

[Versionierter Vertrag, Status-/Exitcodes, Schema-/Hash-/Ressourcengrenzen](../../examples/rp5/README.md),
[Prüfzuordnung](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/docs/RP5_VERIFICATION.md), [Offlinevergleich](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/examples/rp5/index.html).
Gleiche isolierte Image-Umgebung; keine neue Abhängigkeit. P1-Export und Spiel
bleiben unverändert; `export-p1` weist das eigene Reparaturmanifest zurück.

```sh
python -m tools.puzzle_production.repair search --reference <aktuelles-importbundle> --plan <reparaturplan.json> --output-dir <neues-reparaturbundle>
python -m tools.puzzle_production.repair verify --reference <aktuelles-importbundle> --bundle <reparaturbundle> --report <neuer-pruefbericht.json>
```

Alle Ausgabepfade neu. Während der Produktion rekonstruiert der Verifier jeden
Kandidaten und Proof unabhängig, auch bei Nichtfund/Abbruch. Ein ursprünglicher
Abbruch wird nicht zur logischen Freigabe aufgewertet. Vorher/Nachher, feste
Änderungen und Schutzmaske gehören bis zur Endabnahme zum aktuellen Paket.
Die CI prüft das allgemeine Verfahren mit synthetischen Eingängen; der alte
RP5-Korpus, seine Suchpläne und der separate Replayjob werden nicht benötigt.

## Historische Produktionen und Abschluss

RP3-Demo, RP4-Vergleichskorpus, RP5-Korpusreplay, RP6-Sechserpilot und VS1-Produktion
werden im aktuellen Checkout nicht neu aufgebaut. Für historische Untersuchungen
steht der [damalige vollständige Stand](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/tools/puzzle_production/README.md)
zur Verfügung. Die kleinen `rp4.inspect_trial`-/`rp5.unpack_archive`-Hilfen bleiben
vorerst für bestehende synthetische Tests; ihre alten Produktions-CLIs entfallen.

Nach endgültiger Integration auf main:

```sh
python -m tools.puzzle_production.target_adapter retire-production --checkout . --integrated-commit <main-SHA> --puzzle-id <pz-ID>
```

[Authoring §9](../../docs/ai-workflows/PUZZLE_AUTHORING.md) und
[Integrationsformat](../../docs/ZA1_ADAPTER.md) regeln die Bereinigung.
Bestandsprüfungen lesen danach Runtimehashes und kompakte Integrationsdaten,
keine Quellen, Proofs, ZIPs oder Produktionsreplays. Die Entwicklung neuer Rätsel
verwendet weiterhin vollständige neue Eingänge/Freigaben und technische Prüfung.
