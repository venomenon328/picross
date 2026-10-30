# RP-1 bis RP-5: Deduktionskern, Bildproduktion und Reparatur

**AT · Umsetzungsvorbereitung V4 vom 19.10.2026; AT-A nach AT-A-R01 mit PR #263 integriert:**
[AT](../../docs/REVEAL_TRANSPARENCY.md) ergänzt mit AT-A den Produktionsstandard
für transparente Abschlussbilder und einen eigenen eng begrenzten Bildupdateweg.
AT-B stellt danach den gebundenen Bestand mit tatsächlichen Bildfreigaben um.
Reine Bildrevisionen verwenden den eigenen `catalog_reveal`-Weg; `plan-update`/
`update` bleibt auf den gesonderten Rasterersatz begrenzt und erhält aktive
Bildfassungen. Die technische AT-A-Lieferung übernimmt keine realen Bilder
oder Metadaten.
[AT-B-V01](../../docs/AT_B_VERIFICATION.md) liefert die vollständige
Bild-/Endfreigabevorlage im frühen Authoringstatus `reveal_review`.
Die anschließende [Eigentümerabnahme](../../docs/AT_B_OWNER_APPROVAL.md) erlaubt
AT-B-F01 mit kontrolliertem `catalog_reveal plan/adopt` und AT-B-T01.
Kein produktiver Request oder Plan mit ausstehenden Zustimmungen.

**Aktuelle Prüfregel (12.10.2026):** Konkrete Rätsel werden während ihrer Produktion
und Integration geprüft, niemals routinemäßig in CI. Keine rätselspezifischen
Unit-Tests anlegen. CI führt bei Werkzeugänderungen allgemeine Tests an festen
synthetischen Eingängen aus; reine Rätseldateien erhalten nur den schlanken
Inhaltspfad. Historische Korpusläufe sind nur im gebundenen Altcheckout verfügbar;
frühere Jobangaben sind abgelöst.
Maßgeblich: [CI-Policy](../../docs/CI_POLICY.md) und
[Regelwerk](../../docs/ai-workflows/PUZZLE_AUTHORING.md).

KAT-1 ergänzt [Kategorien und Zuordnung](../../docs/CATEGORIES.md): neue ZA-1-Exporte verlangen `--category-id` und `--categories`; Snapshot, Manifest v2, Zielregistry und Runtimeprojektion werden gemeinsam geprüft. `sync-runtime --checkout .` übernimmt geprüfte Metadaten in die Projektion. `check-registry --checkout .` prüft laufende Produktionspakete per Replay, abgeschlossene Produktion über die kompakte Integrationsbindung. Alte Exporte bleiben prüfbar, benötigen zur neuen Registrierung aber einen kategorisierten Neu-Export.

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

**RI-A-V01 · Implementierung zu #478, getrennte Abnahme offen:**
[RI](../../docs/PUZZLE_INTEGRATION.md) und [RI-A-T01](../../docs/RI_A_VERIFICATION.md)
binden Umfang, Messungen und Gates. Nur `register` akzeptiert
`--publication-seconds S` und `--recovery-seconds S` (jeweils Default 1800).
`recover-registration --recovery-seconds S` gilt nur für sicher erkannte
Registrierungsjournale; andere Operationen lehnen diesen Override ab und
behalten sonst 300 s plus bestehende Außenbudgets. Die feste Warnung nach
300 s bricht keinen Lauf ab. API: `registration`/`integrate` erhalten
`publication_seconds=None, recovery_seconds=None`; `recover` erhält
`recovery_seconds=None`. Plan/Update lehnen mutierende Overrides ab.
`S` ist positiv und endlich, API exakt `int`/`float` ohne `bool`, inklusive
endlicher berechneter Deadline.
Noch unbekannte Recoveryoperationen bleiben während der lesenden Klassifikation
unter höchstens 300 s beziehungsweise einem kürzeren Override. Erst sichere
Zuordnung erlaubt den Registrierungsrahmen ab dem ursprünglichen Aufrufstart;
abgelaufene Erst-/Außenfristen werden nicht verlängert. Die anschließende
vollständige Journal-/Quellenprüfung bleibt vor Mutation erforderlich.

`export`, `plan`, `register`, `recover-registration` ergänzen stdout ausschließlich
um `operation_diagnostics`; es bleibt genau ein JSON-Ergebnis. Fortschritt,
300-s-Warnung und Abschluss stehen auf stderr, regulär höchstens alle 30 s.
`--operation-report <neue-datei>` veröffentlicht dieselbe Hülle
`picross-ri-a-operation-v1` atomar außerhalb des Checkouts und aller Eingänge.
Der Elternordner muss existieren; keine Überschreibung. Ein Berichtsfehler nach
Commit bleibt ein Diagnosefehler auf stderr, kein fehlgeschlagener Commit.
Verschachtelte Phasen sind inklusive, nicht additiv; Zähler zählen tatsächliche
Aufrufe/Bytes, benannte Messlücken bleiben offen. Ressourcen/Signale: Exit 4
auch nach Rollback; fachliche Fehler: Exit 2. Dauerhaftes P6 einschließlich
Lockentfernung bleibt Erfolg bei erst danach bemerktem Fristablauf.
Ein harter Prozessabbruch kann den Abschlussbericht verhindern.
`*_attempts` zählt begonnene Kandidaten-/Input-/Exportprüfungen, die drei
`full_*`-Zähler nur deren erfolgreichen vollständigen Rücklauf. Fehler und
Fristabläufe bleiben als Versuche/Teilzeiten erhalten. Phasen P0–P6/R0–R2
bezeichnen die gerade ausgeführte Arbeit einschließlich wiederholter Dateien;
Checkpointfortschritt ist kein vorgezogener Phasenabschluss. Details und
Zählernamen stehen im [ZA-1-Vertrag](../../docs/ZA1_ADAPTER.md).

Andere Writer, `catalog_reveal --seconds` 1…300, Authoring-Eingangsprüfung,
Solver-/Import-/Proof- und Datei-/Bytegrenzen bleiben unverändert.

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

ZA-1 ergänzt mit `picross-manual-authorization-v6` die ausdrücklich angenommene
monochrome Pixelvorlage aus einem versiegelten manuellen Neuentwurf. Die separate
Eigentümererklärung bindet Originalpaket, Motivannahme, Parameter und Endabnahme;
eine eng geprüfte Präfixbindung erhält historische Revealfreigabe und Provenienz.
Der vollständige RP-3-Pixelimport wird frisch unabhängig zertifiziert, ohne alte
Gates oder Dateien umzuschreiben. V1–v5, Randregel und Inhaltsgates bleiben erhalten.
Schema und Grenzen stehen in [ZA-1](../../docs/ZA1_ADAPTER.md); CLI weiterhin
`--manual-authorization`, Export v3/v4. Synthetische Regressionen prüfen diesen
Weg; reale Rätsel bleiben reine Produktionsinputs.

## Instrumentierte Einzelanalyse (SD-A) und feste Bewertung (SD-B)

Der freigegebene [SD-Vertrag](../../docs/PUZZLE_DIFFICULTY.md), Ursprung
[#235](https://github.com/venomenon328/picross/issues/235), bindet die getrennte
Bewertungsspur mit instrumentierten R0–R3-Regeln und synchronen Wellen.
Bestehende Proofverträge und der unabhängige R4-Notwendigkeitsbeleg bleiben
unverändert. SD-B bindet feste Skalen- und Größenregeln an unabhängige synthetische
Referenzen; der reale Katalog ist weder Kalibrierungskorpus noch Testbestand.
Auch Kopien realer Rätsel dürfen keine automatisierten Bewertungsfälle werden.

SD-C1 führt den gemeinsamen manuellen Weg für ausgewählte Bestandsrätsel und
neue Rätsel nach finaler Deduktionsprüfung ein: Bericht erzeugen, Bindungen prüfen,
ausdrücklich beauftragt übernehmen. Passende Berichte sind wiederverwendbar.
Die [Methode 0.3](../../docs/SD_CALIBRATION.md) ist als opt-in Einzelbewertung
implementiert; [SD-C1](../../docs/SD_CATALOG.md) liefert die technische Übernahme.
Reale Bestandsbewertung/Übernahme bleibt der separate Auftrag SD-C2. Neue Registrierung
und logikrelevante Updates verlangen zusätzlich den vollständig geprüften 0.3-Input.
Authoring 0.5.0 und Produktionsfreigaben bleiben erhalten. Keine reale Analyse in CI,
gewöhnlichem Build, Registryprüfung oder Katalogstart.

```sh
python -m tools.puzzle_production analyze-difficulty --input tests/puzzle_production/fixtures/sd-runtime.json --input-kind runtime --output-dir artifacts/sd-a-example
python -m tools.puzzle_production check-analysis --input tests/puzzle_production/fixtures/sd-runtime.json --bundle artifacts/sd-a-example
python -m tools.puzzle_production analyze-difficulty --input tests/puzzle_production/fixtures/deductive.json --output-dir artifacts/sd-a-logic
python -m unittest discover -s tests/puzzle_production -p 'test_analysis.py' -v
```

Für den eingefrorenen Methodenstand **zusätzlich bei Erzeugung und Prüfung**:

```sh
python -m tools.puzzle_production analyze-difficulty --input tests/puzzle_production/fixtures/sd-runtime.json --input-kind runtime --method picross-difficulty-0.3 --output-dir artifacts/sd-b-example
python -m tools.puzzle_production check-analysis --input tests/puzzle_production/fixtures/sd-runtime.json --bundle artifacts/sd-b-example --method picross-difficulty-0.3
python -m unittest discover -s tests/puzzle_production -p 'test_difficulty_rating.py' -v
```

SD-B schreibt zusätzlich `rating.json` (`picross-difficulty-rating-v1`, maximal
64 KiB). Es bindet den vollständigen festen Methodensatz, exakte Konfiguration,
Referenzen, Kalibrierungsbelege und Quellmodule sowie geprüften v1-Ergebnishash und
Quellidentität. Der Checker prüft zuerst das gesamte v1-Bundle unabhängig neu,
danach sämtliche Ratingfelder gegen die eingefrorene Berechnung. Fehlende oder
veränderte Bindungen sind Fehler, auch bei neu berechnetem Hash. Keine Ratingpfade
aus Berichten werden geöffnet. API: `analyze_file(..., method="picross-difficulty-0.3")`
und `check_bundle(..., method="picross-difficulty-0.3")`; die reinen mathematischen
Reducer sind selbst keine Proofprüfer und erwarten bereits geprüfte Metriken.

Logische Basis, Größenbeitrag und Endstufe werden getrennt berichtet. Ein gültiger
Wert ist `instrumented`/`medium`, ohne menschliche Kalibrierung oder Lösungszeit.
Abbruch, Widerspruch und unvollständige Deduktion liefern `unrated` mit null als
Stufe. Vollständiger Paarproof ohne unabhängig bewiesene R4-Notwendigkeit genügt
nicht. Nur geprüftes notwendiges R4 erhält 5 bei unvollständigem Linienverlauf.
Die vorhandenen Exitcodes und getrennten R4-Dateien gelten weiter.

Ohne `--method` bleiben Erzeugung und Prüfung exakt SD-A/v1. Sie behaupten keine
Ratingprüfung, auch wenn daneben ein Rating liegt. Die historische v1-Erklärung
„SD-B ausstehend“ bleibt zur exakten alten Ergebnisrekonstruktion erhalten;
die neue CLI zeigt bei gewählter Methode die aktuelle Ratingerklärung.

Der erste Eingang ist ein fester künstlicher 3×2-Balken, ohne Produktionspaket
oder Revealdatei. Nur das **neue** Analyseverzeichnis wird geschrieben. Es enthält
`input.json` (exakte Quellbytes), `logic.json` (eigener kanonischer Analyseinput),
`trace.json` und `report.json`. Bestehende Ausgabeordner werden abgewiesen.
Der lesende Checker vergleicht die aktuelle explizite Quelle mit der Kopie und
prüft Dateihashes, Regelstärken, vollständige gleichzeitige Möglichkeiten,
schwächere Fixpunkte, Endstatus und rekonstruierte Berichtsfelder.

`--input-kind logic` (Standard) liest unveränderte Logik v1/v2. `runtime` liest
ausschließlich die benannte Schema-2-Definition und normalisiert numerische
Farben auf `c1`…`c8` unter Farbregeln; auch bei einer Farbe wird kein historischer
Produktionsmodus behauptet. Die Sollmatrix wird erst nach der Ableitung geprüft.
Analysehash, Engine-Logikhash und tatsächlicher Definitions-Dateihash bleiben
getrennt. Kein Bestandscheck und keine Rekonstruktion alter Produktionspakete.

Der vollständige [SD-A-Vertrag](../../docs/SD_ANALYZER.md) definiert die endlichen
Regeln, Wellen, Zähler/Nenner, Symmetrie und die Formate
`picross-analysis-input-v1`, `picross-analysis-trace-v1` sowie
`picross-analysis-report-v1`. `result` mit `result_hash` ist deterministisch;
Dateibindungen, `operation` mit Budgets/Verbrauch/Laufzeit und Prüfstatus sind
getrennt. Kein Score: `method`, `level`, `confidence` und `estimated_minutes`
bleiben im v1-Bericht null. Bei `stalled` ist der Linienfixpunkt geprüft, aber der Lösungsverlauf
unvollständig. Ein geprüfter Abbruchpräfix bleibt `aborted`.

Budgets: `--seconds 120`, `--max-lines 100000`, `--max-rule-work 20000000`,
`--max-waves 80000`; eigene Prüfgrenzen `--verify-seconds 120`,
`--verify-max-lines 100000`, `--verify-max-rule-work 20000000`.
Der Checker verwendet seine eigenen `--seconds`/`--max-*`-Grenzen.
Abbruch in einer Welle übernimmt keinen Teilfortschritt. Kann der gespeicherte
Trace nicht fertig geprüft werden, entsteht kein erfolgreicher `report.json`.
Teilartefakte können zur Diagnose bleiben; ein harter Prozessabbruch garantiert
keine JSON-Abschlussausgabe. Fehler liefern auf stdout ein eigenes Fehlerobjekt.

| Status / Exit | Bedeutung |
| --- | --- |
| `solved`, `stalled`, `contradiction` / 0 | Unabhängig geprüfter jeweiliger Linienstatus; nur solved ist vollständiger Linienverlauf. |
| `invalid_input` / 2 | Ungültiger Eingang/Parameter oder vorhandenes Ausgabeziel. |
| `invalid_analysis` / 3 | Falsche Spur, veraltete Bindung oder widersprüchlicher Bericht. |
| `aborted` / 4 | Zeit-/Arbeits-/Wellen-/Speicherende oder Abbruch; keine Einstufung. |
| `technical_error` / 5 | Datei-/interner Fehler, kein logisches Rätselurteil. |

Optional bindet `--parameters <json>` genau `{"aggregation":null}` oder das
im Vertrag definierte `sd-aggregation-1`-Objekt. Die angegebenen Engstellen- und
Restaufräumkriterien erscheinen explizit im Trace; es gibt keine kalibrierten
Defaults. SD-B verwendet die Rohmetriken mit exakt `{"aggregation":null}` und
seine eigene gebundene Bewertungsaggregation. Andere Parameter zusammen mit
`--method picross-difficulty-0.3` werden vor dem Analyselauf abgewiesen.

Optional und ausschließlich zusammen: `--r4-proof <proof-v3.json>` und
`--r4-baseline <linienproof.json>`. Beide werden unverändert kopiert und mit dem
vorhandenen unabhängigen Verifier geprüft. Die Nachweise müssen exakt zur
Engine-Logik passen; nach Runtime-Farbnormalisierung passen alte semantische IDs
nicht automatisch. Nur eine bestätigte stalled-Linienbaseline und ein vollständiger
Paarproof bei ebenso abgeschlossenem SD-Linienfixpunkt begründen R4. Seine Schritte
bleiben außerhalb der Wellenzählung. `--max-pair-work` und `--max-pair-records`
behalten die bestehenden Paarbudgets. Kein automatischer Paar-/Suchlauf.

Python-API: `analysis.analyze(Puzzle, config, AnalysisBudget)` erzeugt eine noch
ungeprüfte Spur; `analysis_verifier.verify_trace` beziehungsweise `verify_result`
prüfen sie. `analysis_io.analyze_file` und `check_bundle` binden die gespeicherten
Bytes. Vorhandene Proof-v1/v2/v3-Verifikation und `quality.assess()` bleiben erhalten.

## SD2-A: Separater Analyseweg

Der [technische Vertrag 1.0](../../docs/SD2_ANALYZER.md) wurde vor Code versioniert.
Der eigene Analysator und unabhängige Prüfer verwenden E0–E3 und liefern getrennte
Rohprofile für Denkanspruch, Suchaufwand und Bearbeitungsumfang. Die eigene CLI
ist ohne Pillow oder Engine ausführbar:

```sh
python -m tools.puzzle_production.sd2_cli analyze --input tests/puzzle_production/fixtures/sd-runtime.json --input-kind runtime --output-dir artifacts/sd2-example
python -m tools.puzzle_production.sd2_cli check --input tests/puzzle_production/fixtures/sd-runtime.json --bundle artifacts/sd2-example
python -m unittest discover -s tests/puzzle_production -p 'test_sd2_analysis.py' -v
```

Das Beispiel ist ein fester synthetischer Balken. Ohne `--input-kind runtime`
werden Logikdateien v1/v2 gelesen. Ausgabeordner müssen neu sein. Das Bundle
enthält `input.json`, `logic.json`, `trace.json`, `report.json`; optional die
beiden expliziten `--r4-proof`/`--r4-baseline`-Dateien. Der Checker ist lesend,
prüft die ganze Spur und rekonstruiert sämtliche Profile. Keine Registry wird
gelesen. Alle Dateiformate besitzen eigene `picross-sd2-*-v1`-Kennungen.

`--seconds 120 --max-lines 100000 --max-rule-work 20000000 --max-waves 80000`
sowie `--max-pair-work 20000000 --max-pair-records 250000` begrenzen den Lauf.
Analyze hat eigene `--verify-seconds`, `--verify-max-lines`,
`--verify-max-rule-work` mit denselben Defaults. Unterbrochene Wellen werden
verworfen; Prüfabbruch schreibt keinen Erfolgsbericht. Exit 0 bestätigt den
jeweiligen Status solved/stalled/contradiction, 2 ungültigen Input, 3 ungültige
Analyse, 4 Abbruch und 5 technischen Fehler. Ein Fixpunkt ist kein vollständiger
Lösungsverlauf. Proxys sind keine gemessenen menschlichen Zeiten oder Klickzahlen.

Auch vollständige SD2-A-Berichte enthalten keine Endnote oder aktive Bewertung;
`method`, `level`, `confidence`, `estimated_minutes` bleiben null. Alte Aufrufe
und der vollständige 0.3-Freeze bleiben erhalten. A ist nach separatem Review
über PR #408 integriert. [Historische Prüfzuordnung](../../docs/SD2_A_VERIFICATION.md).

## SD2-C: gemeinsamer Integrationsvertrag

[SD2-C-V01](../../docs/SD2_INTEGRATION.md) bindet vor Code die neuen Checked-/
Rating-/Kontext-/Reportformate, Runtime-v5 und Journalgenerationen. Die bisherigen
0.3-Formate und eigenständigen A-/B-CLIs bleiben geschlossen. Der reale
Produktionsdefault ist nach [D-F01/T01](../../docs/SD2_D_ADOPTION.md)
auf dem Arbeitsbranch 0.4. Neue `--method`-Auswahl und explizites
`catalog_method plan/adopt` folgen diesem Vertrag.
[SD2-C-T01](../../docs/SD2_C_VERIFICATION.md) ordnet die synthetischen Nachweise zu.
C ist nach separatem R01 über PR #410 integriert;
[D-V01](../../docs/SD2_D_VERIFICATION.md) liefert den gesondert beauftragten
Bestandsvergleich und Planungsstand vor der anschließenden F01-Übernahme/Aktivierung.

Einzelanalyse und frischer Import verwenden eine ausdrücklich übergebene
Definition. Das neue äußere Arbeitsverzeichnis enthält `catalog-context.json`
und das unveränderte geschlossene B-Bundle in `rating/`. Aktive Ratingquellen
enthalten keine vollständigen Spuren; das Arbeitsbundle bleibt der vollständige
externe Analysebeleg. Beispiel mit dem festen technischen Input:

```sh
python -m tools.puzzle_production.catalog_analysis analyze --method picross-difficulty-0.4 --production-mode mono --input tests/puzzle_production/fixtures/sd-runtime.json --work-dir artifacts/sd2-c-single --output artifacts/sd2-c-checked.json
python -m tools.puzzle_production.catalog_analysis import --input tests/puzzle_production/fixtures/sd-runtime.json --bundle artifacts/sd2-c-single --output artifacts/sd2-c-imported.json
```

Für eine freigegebene neue Produktion bleibt der vorbereitende Weg
`candidate --design ... --matrix ... --logic ... --puzzle-id ... --runtime-revision ... --output ...`,
danach `analyze` oder `import`, abschließend
`rebind --input <fertige-Definition> --rating <checked.json> --production-mode mono|color --output <neue-checked.json>`.
Die geprüfte Datei geht als `--difficulty` an `target_adapter plan/register/update`.
Register/Update verlangen für neue oder tatsächlich geänderte Logik genau die
aktive Produktionsmethode; ohne Defaultdatei ist dies **0.3**. Ein 0.4-Checked-
Ergebnis aktiviert die Methode nicht. Einfarb-Color bleibt explizit Color.
Metadaten-Rebind erhält den ursprünglichen Analysebeleg einschließlich seiner
Methode, sofern Logik, Matrix und Produktionsmodus gleich bleiben. Ursprüngliche
Authoringbewertungen und Freigaben werden nicht ersetzt.

Auswahl und Übernahme sind getrennt. Die folgenden Aufrufe setzen einen
**isolierten synthetischen Checkout** und passende gebundene Dateien voraus;
sie sind kein Auftrag zur Ausführung am echten Bestand:

```sh
python -m tools.puzzle_production.catalog_analysis preview-checked --method picross-difficulty-0.4 --checkout /tmp/sd2-c-checkout --id pz-sd-synthetic --checked pz-sd-synthetic /tmp/checked.json --work-dir /tmp/sd2-c-preview --run-id synthetic-c --source-commit 0000000000000000000000000000000000000000
python -m tools.puzzle_production.catalog_analysis plan-adoption --checkout /tmp/sd2-c-checkout --work-dir /tmp/sd2-c-preview
python -m tools.puzzle_production.catalog_analysis adopt --checkout /tmp/sd2-c-checkout --work-dir /tmp/sd2-c-preview
```

`preview` analysiert nur die explizite Auswahl; `preview-checked` konsumiert
vorhandene geprüfte Ergebnisse. `--all` ersetzt die ID-Auswahl für einen ausdrücklich
beauftragten Gesamtlauf. Ohne `--method` bleibt auch hier 0.3. JSON/Markdown nennen
Alt-/Neumethode, Stufe, vollständiges 0.4-Assessment und offene Fälle. Unvollständige
Versuche erhalten keine Ersatzstufe und verdrängen keinen aktiven Altwert.
Plan/Adopt prüfen vollständige Quellen einschließlich Standarddatei; gleiche
Übernahme ist nur bei exakt passendem Zielzustand ein byte-/mtimegleicher No-op.

Explizite Aktivierung ist ein eigener Plan ohne Rating-/Runtimeänderung:

```sh
python -m tools.puzzle_production.catalog_method plan --checkout /tmp/sd2-c-checkout --expected-method picross-difficulty-0.3 --target-method picross-difficulty-0.4 --target-method-hash 5508f0742aa858a6adc31aa621433e68298b915fb0fd6b8d9e74e576ba87caaf --output /tmp/sd2-c-activation.json
python -m tools.puzzle_production.catalog_method adopt --checkout /tmp/sd2-c-checkout --plan /tmp/sd2-c-activation.json
```

Der Plan bindet vollständige Quellen, erwartete Vorgängerrevision und beide
Methodenfreezes. `adopt` ändert ausschließlich `content/difficulty-method.json`
über das gemeinsame Journal. Nach Unterbrechung zuerst `content_registry recover`;
fremde Bytes bleiben mit offenem Journal erhalten. Exitcodes 0/2/4 bedeuten
Erfolg/Vertragsfehler/Abbruch. C aktiviert ausschließlich synthetische Checkouts.
Die echte Aktivierung, Analyse und Umstellung bleiben #406.

## SD2-B: Eigenständige Bewertung 0.4

Der [B-Vertrag](../../docs/SD2_CALIBRATION.md) bindet vorab festgelegte unabhängige
synthetische Referenzen, getrennte Validierung, genaue rationale Arithmetik und
den eingefrorenen Methodensatz. Der folgende Weg bewertet nur den ausdrücklich
übergebenen Input. 0.3 bleibt aktiv; gemeinsame Integration und reale Umstellung
gehören ausschließlich zu SD2-C/D.

```sh
python -m tools.puzzle_production.sd2_rating_cli analyze --input tests/puzzle_production/fixtures/sd-runtime.json --input-kind runtime --output-dir artifacts/sd2-rating-example
python -m tools.puzzle_production.sd2_rating_cli check --input tests/puzzle_production/fixtures/sd-runtime.json --bundle artifacts/sd2-rating-example
python -m tools.puzzle_production.sd2_rating_cli rate --input tests/puzzle_production/fixtures/sd-runtime.json --analysis-bundle artifacts/sd2-example --output-dir artifacts/sd2-rated-raw
python -m unittest discover -s tests/puzzle_production -p 'test_sd2_rating.py' -v
```

Das Balkenbeispiel demonstriert nur die CLI, nicht den neuen B-Referenzsatz.
Die Hülle enthält exakt `analysis/` (unverändertes A-v1-Rohbundle),
`rating.json` und den deterministischen `report.md`. `rate` kopiert ein vorhandenes
A-Bundle bytegetreu und prüft es frisch; `check` rekonstruiert Rohprofile,
R4-Notwendigkeit und Bewertung unabhängig von gespeicherten Ergebnissen.
Jeder Einstieg prüft den vollständigen Methoden-/Quellenfreeze.

Alle drei Beiträge, Score, Stufe, Wert ohne Umfang und exakte Grenzabstände
bleiben sichtbar. Zahlen sind gekürzte `[Zähler,Nenner]`; Gleichheit gehört zur
höheren Stufe. Ohne vollständigen Liniennachweis oder separat nachgewiesenes
notwendiges R4 bleibt die Bewertung leer. R4 verwendet einen festen L5-Anker und
kennzeichnet Linienprofile als Präfixe. Keine menschlichen Minuten; bewertete
Fälle sind Modellschätzungen höchstens mittlerer Aussagekraft.

Analyse- und Prüfgrenzen entsprechen den oben aufgeführten A-Budgets;
`analyze` hat ein getrenntes Verifikationsbudget. Exit 0 heißt vollständig
geprüft, auch wenn stalled/contradiction keine Note erlauben. Exit 2/3/4/5
bezeichnen Eingabe-/Beleg-/Abbruch-/Technikfehler. Ein verifizierter abgebrochener
Präfix bleibt unrated und liefert Exit 4; Prüfabbrüche schreiben kein Rating.
Ausgabeordner müssen neu sein. Explizites R4 erfordert beide `--r4-proof` und
`--r4-baseline`; kein automatischer Paarlauf. [SD2-B-T01](../../docs/SD2_B_VERIFICATION.md)
bindet den historischen Lieferstand/Selbstreview; B ist nach separatem R01
über PR #409 integriert.

## SD-C1: Kandidat, geprüfter Input, Vorschau und Übernahme

[Daten-/Recoveryvertrag](../../docs/SD_CATALOG.md). Keine dieser Operationen läuft
automatisch bei Export, Registryprüfung, Build oder Spielstart. In C1 werden nur
synthetische Fälle geprüft; der echte Erstlauf und seine Übernahme bleiben SD-C2.
Alle Arbeits-/Ausgabepfade ausdrücklich wählen, außerhalb von `game/` und
`content/difficulty/`; neue Ausgaben dürfen nicht bereits existieren.

Nach endgültiger Deduktionsprüfung, vor redaktioneller Endfreigabe:

```sh
python -m tools.puzzle_production.catalog_analysis candidate --design <design.json> --matrix <matrix-array.json> --logic <logic.json> --puzzle-id <pz-ID> --runtime-revision 1 --output <work/provisional.json>
python -m tools.puzzle_production.catalog_analysis analyze --input <work/provisional.json> --production-mode <mono-oder-color> --work-dir <work/full-bundle> --output <work/checked.json>
```

`candidate` nutzt die validierte ZA-1-Farbabbildung; sein vorläufiger Reveal ist
keine Freigabe. `analyze` ruft die eingefrorenen SD-A/SD-B-APIs auf und prüft das
fertige Bundle vollständig. Den Produktionsmodus ausdrücklich aus dem geprüften
Design übernehmen: Schema 2 allein unterscheidet Mono und Einfarb-Color nicht.
Der Wrapper bindet den Modus an die analysierten Definitionsbytes in
`catalog-context.json`; das eingefrorene SD-B-Bundleformat bleibt unverändert.
Schon vorhandene Bundles werden ausdrücklich importiert:

```sh
python -m tools.puzzle_production.catalog_analysis import --input <runtime-or-provisional.json> --bundle <full-bundle> --output <checked.json>
```

Nur passende ausdrücklich übergebene `--r4-baseline <file> --r4-proof <file>`
ergänzen R4. Nach Farbremapping passen alte Produktionsproofs nicht automatisch.
Ohne Notwendigkeitsbeleg bleibt ein Linienfixpunkt `unrated`; kein versteckter
Paarlauf. `analyze`, `preview` und `import` bieten `--seconds` (120), `--max-lines`
(100000), `--max-rule-work` (20000000), `--max-waves` (80000), `--max-pair-work`
(20000000), `--max-pair-records` (250000). Analyse/Vorschau bieten dieselben
`--verify-*`-Grenzen separat. Vorab festlegen; Budgets ändern keine Methodengrenze.
Ein gültiger Bericht, auch `unrated`, beendet den Befehl mit 0; ungültige Daten
mit 2, ein nicht als Bericht abgeschlossener Budgetabbruch mit 4. Status/Grund
im Bericht sind maßgeblich, nicht allein der Prozessstatus.

Nach tatsächlicher Endfreigabe und unverändertem regulärem `target_adapter export`:

```sh
python -m tools.puzzle_production.catalog_analysis rebind --input <export/runtime/data/content/stem.json> --production-mode <mono-oder-color> --rating <work/checked.json> --output <work/final-checked.json>
python -m tools.puzzle_production.target_adapter plan --export <export> --checkout <checkout> --difficulty <work/final-checked.json>
python -m tools.puzzle_production.target_adapter register --export <export> --checkout <checkout> --difficulty <work/final-checked.json>
```

Rebind verlangt identische ID, Produktionsmodus, kanonische Logik und Zielmatrix; ursprüngliches
`rating.source` bleibt erhalten. Alternativ führt `--rebind-difficulty` im Plan/
Register/Update die ausdrücklich gewählte Neubindung durch. Neue Registrierung
und logisch geänderte Definitionen brauchen vollständiges 0.3. Für einen
Metadatenupdate mit vorhandener aktiver Bewertung genügt bei gleichem Modus/Logik/Matrix
`--rebind-difficulty`. Identische Legacy-Wiederholungen brauchen keine neue Analyse.
`plan-update`/`update` behalten zusätzlich ihren Erwartungshash, neue Paket-/Runtime-
Revision und vollständige ZA-1-Prüfung. Reine Bewertungsänderung benutzt sie nicht.

Neue checked-/aktive Hüllen verwenden v2 mit separatem `production_mode`.
Alte v1-Hüllen bleiben lesbar, aber ohne erfundene Modusherkunft: Rebind und neue
Integration benötigen eine frische modegebundene Analyse. `import` kann ohne
Kontextdatei nur checked-v1 liefern; es gibt keine nachträgliche Modusoption.
Ein Moduswechsel verlangt auch bei gleichen numerischen Hinweisen eine neue Analyse.

Ausdrücklich ausgewählte bestehende IDs werden in ein neues Arbeitsverzeichnis
analysiert; `--id` darf wiederholt werden, `--all` wählt ausdrücklich alle:

```sh
python -m tools.puzzle_production.catalog_analysis preview --checkout <checkout> --id <pz-ID> --id <weitere-ID> --source-commit <volle-SHA> --run-id <run-id> --work-dir <work/preview>
python -m tools.puzzle_production.catalog_analysis preview --checkout <checkout> --all --source-commit <volle-SHA> --run-id <anderer-run> --work-dir <work/all-preview>
```

Optional pro ID: `--r4 <pz-ID> <baseline.json> <proof.json>`. Vorab importierte
Inputs verwenden stattdessen `preview-checked` mit denselben Auswahlargumenten
und wiederholtem `--checked <pz-ID> <checked.json>`. Fehlende oder unvollständige
Fälle bleiben mit Altwert, Status/Grund und Bindung sichtbar; keine ID entfällt.
JSON und Markdown enthalten beobachtende Alt-/Neuverteilungen. `source-commit`
ist ausdrücklich benannte Provenienz; die tatsächlichen Datei-/Ausgangshashes
sichern die Übernahme, ohne Git oder Paketreplay im Analyzer vorauszusetzen.

```sh
python -m tools.puzzle_production.catalog_analysis plan-adoption --checkout <checkout> --work-dir <work/preview>
python -m tools.puzzle_production.catalog_analysis adopt --checkout <checkout> --work-dir <work/preview>
```

Erst `adopt` schreibt aktive Ratings und beide Dauerberichte. Unvollständige
Versuche ersetzen keine gültigen aktiven Werte. Identische Übernahme ist No-op;
alte Produktionsbelege, Definitionen, Revisionen, Kategorien und Saves bleiben.
Report-v2 bindet zusätzlich alle gelesenen Quellen. `plan-adoption` und `adopt`
prüfen vor einem No-op den erwarteten Übernahmezustand einschließlich dieser
Quellen; nach zwischenzeitlicher Kategorie-/Registry-/Ratingänderung stoppen beide
konkret ohne Mutation. Alte Report-v1-Journale und identische Wiederholungen bleiben
unter ihren ursprünglichen Bindungen unterstützt; die zusätzliche vollständige
Quellenbindung gilt für neue v2-Berichte.
Der gemeinsame Lock schützt Register/Update/Sync/Adoption. Nach Unterbrechung:

```sh
python -m tools.puzzle_production.target_adapter recover-registration --checkout <checkout>
```

Recovery prüft vollständig vor Mutation und stellt eine gültige Altprojektion
her. Fremdänderungen erhalten Dateien und Journal; den Konflikt klären, nicht
den Lock löschen oder durch `sync-runtime` umgehen. Exakte KE-Altjournale bleiben
nur ohne ungebundene aktive Sidecars wiederaufnehmbar. Neue Formate und Grenzen
stehen im SD-C1-Vertrag.

Alle Quellen-/Recoverywege prüfen auch verwaiste oder falsch platzierte aktive
Ratingdateien. Nur `content/difficulty/<registrierte-ID>/rating.json` ist aktiv;
die erlaubten `reports/<run-id>/report.json|report.md` sind getrennt. Fremde und
aliasartige Dateien bleiben bei Blockade erhalten, statt einen Legacyfallback auszulösen.

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
zur Verfügung. CI2-B entfernt nach aktuellem Leserabgleich die ausschließlich historisch
verwendeten `rp4.inspect_trial`-/`rp5.unpack_archive`-Hilfen samt sechs Tests.
RP6/`export_p1`, aktuelle Größen-/Codecgrenzen und die aktive Archiveingangsprüfung
in `authoring_package.open_package()` bleiben erhalten.

Nach endgültiger Integration auf main:

```sh
python -m tools.puzzle_production.target_adapter retire-production --checkout . --integrated-commit <main-SHA> --puzzle-id <pz-ID>
```

[Authoring §9](../../docs/ai-workflows/PUZZLE_AUTHORING.md) und
[Integrationsformat](../../docs/ZA1_ADAPTER.md) regeln die Bereinigung.
Bestandsprüfungen lesen danach Runtimehashes und kompakte Integrationsdaten,
keine Quellen, Proofs, ZIPs oder Produktionsreplays. Die Entwicklung neuer Rätsel
verwendet weiterhin vollständige neue Eingänge/Freigaben und technische Prüfung.

Nachträgliche integrierte Bildarbeit besitzt einen eigenen revisionsgenauen Abschluss:

```sh
python -m tools.puzzle_production.target_adapter retire-reveal-production --checkout . --integrated-commit <main-SHA> --authoring-revision <pz-ID> <Authoringrevision>
```

Vorher `origin/main` aktualisieren. `--authoring-revision ID REVISION` ist wiederholbar;
alle ausgewählten Revisionen werden vor der ersten Löschung geprüft. Der enthaltene
Main-Stand muss den registrierten Authoringrecord, die finale Freigabe und exakt die
aktuelle Bildquelle binden. Ungültige Quellen, offene Journale, fremde Dateien,
Index-/Stagingkonflikte und unvollständige Entfernung blockieren. Nur der ausgewählte
Revisionsordner und dessen Indexzeile entfallen; andere, auch offene Revisionen bleiben.
Originalpaket beziehungsweise `picross-integrated-content-v1`, aktuelle Bildrecords,
Freigaben, Herkunft, Notices, Runtime und Ratings werden nicht geschrieben.
Erneuter Aufruf nach vollständiger Entfernung mit demselben Main-Beleg ist ein No-op
einschließlich mtimes. Kleine historische Index-/Record-/Freigabedaten und Git-Objekt-IDs
genügen; historische ZIP-Blobs werden nicht aus Git geladen oder rekonstruiert.
Vorhandene lokale Arbeitsdateien werden zum Bytevergleich gehasht. Der Befehl erstellt nur
einen prüfbaren Arbeitsbaumdiff. Fehler während einer tatsächlichen Dateisystemoperation
sind kein erfolgreicher Abschluss; eine Teilentfernung blockiert den nächsten Aufruf
und muss anhand des Git-Diffs geklärt werden. Kein automatisches Wiederherstellen.

Ab SD-C1 bleiben zusätzlich die kompakte aktive Bewertung,
ihre Eingangsbindungen und der gebundene Methoden-/Referenzstand außerhalb
versiegelter Produktion erhalten. Neue Bewertung nutzt dann Runtime-Logikeingänge
nach SD-D09/D10; sie verlangt keinen allgemeinen Produktions-Replay und keine
Wiederherstellung bereinigter Produktionspakete.

## KU-B: Hinzugefügt-Metadaten

`catalog_added` validiert ID-gebundene Sidecars und dauerhafte Quellenbelege;
Registryprojektion, Registrierung, Update, Sync, Bewertungsadoption und Recovery
verwenden denselben Transaktionsweg. Neue Runtime ist v4; alte exakte v2/v3 bleiben
lesbar. Der separate historische Nachtrag läuft ausdrücklich und ohne Analyse:

```powershell
python -m tools.puzzle_production.catalog_added_history plan --root . --run <run> --base <vollstaendiger-main-SHA> --repository venomenon328/picross --output <plan.json>
python -m tools.puzzle_production.catalog_added_history adopt --root . --plan <plan.json>
python -m tools.puzzle_production.catalog_added_history adopt --root . --plan <plan.json> --apply
```

Nur `plan` liest Git und optional eindeutig gebundene gemergte PR-Vorgeschichten.
Direkte bereits geprüfte Erstregistrierungsbelege können mit `--direct-evidence`
als JSON-Liste übergeben werden. `adopt` ohne `--apply` bleibt lesend; beide Wege
prüfen vollständige Quellbindungen. Eine identische Übernahme ist ein echter
Byte-/mtime-No-op. Bestehende Metadaten bleiben bei Folgeplänen erhalten, neue IDs
oder geänderte Quellen verlangen einen neuen Plan. Fremde Bytes blockieren
Recovery vor Mutation. Details: [KU-B-Vertrag](../../docs/CATALOG_SORTING.md),
[Bestandsplan](../../docs/KU_B_BACKFILL.md).

## AT: Noch zu implementierender Bildupdateweg

Der freigegebene [AT-A-Vertrag](../../docs/REVEAL_TRANSPARENCY.md) verlangt eine
eigene Bildrevision mit neuer tatsächlicher Freigabe und nachvollziehbarer
Alt-/Neuhashbindung außerhalb historischer Produktions-/Integrationsbelege.
PNG-Alpha wird durch den bestehenden Revealexport bereits bytegleich erhalten;
der Austausch eines registrierten Bilds benötigt dennoch den zusätzlichen
abgesicherten Weg. Ein bloßes Überschreiben des PNGs oder nachträgliches
Umschreiben seiner alten Freigabe-/Manifestbindung ist keine gültige Übernahme.

P01 legt vor der ersten betroffenen Codeänderung die exakten Eingänge, Pfade,
Felder, Versionen, Grenzen und die nachfolgende Soll-Syntax gemeinsam in
[ZA-1](../../docs/ZA1_ADAPTER.md), [Projektion](../../docs/CATEGORIES.md) und dem
[Transaktionsvertrag](../../docs/SD_CATALOG.md) fest. Die AT-A-Implementierung
und ihr Prüfstand sind in [AT-A-T01](../../docs/AT_A_VERIFICATION.md) gebunden.
Lesender Plan, aktuelle
Erwartungshashes, gemeinsame Quellenprüfung, versionierter Binärersatz,
kontrollierter Rollback und echte Wiederholungs-No-ops gehören zusammen.
Ein zulässiger Altstand ohne neue Bildquelle und eine vorhandene ungültige
Bildquelle bleiben unterscheidbar; fremde Bytes werden einschließlich Journal
erhalten.

Reine Bildupdates erhalten Definitionen, Runtime-Revisionen, Raster/Hinweise,
IDs/Keys, Ressourcenpfade, Slots, Kategorien, Ratings und Hinzugefügt-Daten
bytegleich. Keine neue Analyse, Zertifizierung oder Wiederherstellung gelöschter
Produktionspakete. Bestehende Register-/Rasterupdate-/Sync-/Adopt-/Cleanup-/
Recoverywege müssen die aktive Bildbindung gemeinsam erhalten; alte exakte
Formate werden nicht gelockert. Synthetische technische Regressionen gehören
zu AT-A, konkrete Bestandsfreistellung, Bildabnahme und Motivprüfung zu AT-B.

### AT-P01-D04 · CLI für Bildrevisionen

Eigener Moduleinstieg `tools.puzzle_production.catalog_reveal`. Genau zwei
Unterbefehle, keine automatische Bestandsauswahl, kein Force/Resume/Skip-Schalter:

```sh
# Nur explizit freigegebene Bildrevisionen; keine automatische Bestandsauswahl.
python -m tools.puzzle_production.catalog_reveal plan --checkout <checkout> --id <pz-ID> [--id <weitere-ID>] --input <externe-anfrage.json> --output-dir <neuer-externer-planordner> [--seconds 300]
python -m tools.puzzle_production.catalog_reveal adopt --checkout <checkout> --plan <planordner/plan.json> [--seconds 300]
# Gemeinsamer Recovery-Einstieg, einschließlich AT-Binärjournalen:
python -m tools.puzzle_production.target_adapter recover-registration --checkout <checkout>
```

`--checkout`, `--input`, `--output-dir`, `--plan` sind einzelne Pfadargumente,
`--id` wiederholbar, mindestens einmal, eindeutig und kanonisch. Keine `--all`-
Option oder implizite Auswahl. Anfrageliste und ID-Auswahl stimmen exakt überein;
beide werden lexikografisch normalisiert, doppelte IDs bleiben Fehler.
`--seconds` Ganzzahl 1…300, Default 300, kumulative monotone Deadline vom ersten
Eingabelesen bis zur Abschlussprüfung; keine Identitätswirkung. Recoverybudget
und Unterbrechungsregeln stehen im Transaktionsvertrag. Argparsefehler Exit 2.

Alle Eingangsbilder liegen neben/unter der externen Anfragedatei; relative
Pfade nach ZA-1, keine Links/Hardlinks/Reparsepunkte/Traversal oder Kollisionen.
Die geprüften absoluten Ein-/Ausgabewurzeln müssen außerhalb des gesamten
Checkouts liegen und dürfen einander nicht überdecken. Kein automatisches Laden
von URLs/Git/Chats. `plan` erzeugt nur einen **neuen nicht vorhandenen** externen
Ordner; ein vorhandener leerer Ordner ist ebenfalls Fehler. Darin exakt
`plan.json`, `images/<pz-ID>.png|svg` (neu) und `previous/<pz-ID>.png|svg` (alt),
je mit zur vorhandenen Revealendung passendem Suffix. Alte Live-Bildbytes werden
für die unabhängige Altprüfung beim Wiederholungs-No-op ebenfalls extern gesichert.
Bildbytes werden unverändert kopiert; keine Formatkonvertierung oder
Bildbearbeitung. Keine zusätzlichen/aliasierenden Dateien. Fehler dürfen ein
als unvollständig bezeichnetes externes Arbeitsverzeichnis hinterlassen; ohne
vollständig geschriebenen und frisch geprüften Plan ist es kein `adopt`-Input.

Inputformat `picross-reveal-request-v1`, exakt `format,entries`.
1…10000 Zeilen, je exakt `id,image,approval,provenance,notice_append`.
`image` ist der sichere relative Eingangsbildpfad; `approval` und `provenance`
sind die vollständigen geschlossenen Objekte nach ZA-1, keine Dateiverweise.
`notice_append` ist null für identische Notice oder nichtleerer UTF-8/LF-Text
ohne BOM/NUL, endet LF; Zielnotice ist exakt alte Notice + LF + dieser Text.
Das alte Präfix bleibt erhalten, Gesamtlimit 64 KiB. Freigabe bindet den Hash
dieser vollständigen Zielnotice. Nur Bildrevisionen mit tatsächlich anderen
Bildbytes sind planbar; bereits erreichter Stand wird durch denselben Plan
wiederholt, nicht durch künstliche neue Revision einer identischen Datei.

PNG/SVG-Grenzen bleiben: 32 MiB je Datei, 8192 je Achse, höchstens 8000000 Pixel,
Detailauflösung mindestens zwei Pixel je aktueller Rasterzelle; lokales begrenztes
SVG-Profil bis 10000 Elemente ohne externe Referenzen/Ausführung/Entities.
Kein JPEG oder Endungswechsel am bestehenden Pfad. PNG wird vollständig geprüft,
keine Animation/trunkierten Daten; vorhandene gültige Altformate bleiben erhalten.
Transparenzqualität ist eine tatsächliche Bildentscheidung nach AT, kein
automatisches Akzeptieren allein wegen eines Alphakanals.
Anfrage maximal 8 MiB, Plan-JSON maximal 128 MiB, bis 10000 Zeilen;
kopierte alte und neue Bilder zusammen maximal 96 MiB. JSON-/String-/Tiefen-/Hashregeln wie
ZA-1, sämtliche Objektfelder exakt. Engeres Journal-/Zielrecordlimit gilt schon
bei Planung: ein nicht journalisierbarer Mehrfachplan darf nicht erfolgreich
ausgegeben werden. Zu große Anfragen ausdrücklich aufteilen, keine Teilübernahme.

### Gespeicherter Plan und Ergebnis

`picross-reveal-plan-v1` hat exakt
`format,ids,snapshot,entries,writes,plan_hash`. Keine Zeit/Git-HEAD/absoluten
Maschinenpfade im Identitätskern; `plan_hash=H(Plan ohne plan_hash)` nach ZA-1.
Datei exakt kanonisches JSON plus LF. `ids` ist die eindeutige sortierte Auswahl.

| Feld | Geschlossener Untervertrag |
| --- | --- |
| `snapshot` | Exakt `sources,namespaces`. `sources` ist die vollständige Pfad→Dateihash/null-Map aus T/K des Transaktionsvertrags, einschließlich erwarteter AT-/Rating-/Added-Abwesenheiten und erlaubter fehlender neuer Textziele; maximal 100000 Pfade. `namespaces` exakt `reveals,difficulty,added,packages`, jeweils lexikografisch sortierte Liste aller bei der Quellenprüfung relevanten regulären Dateipfade, ohne doppelte Pfade. Leere erlaubte Verzeichnisse haben keine Identitätswirkung. |
| `entries[]` | Sortiert nach Auswahl, je exakt `id,old_image_revision,new_image_revision,binding_hash,old_reveal,new_reveal,old_record,new_record,old_notice,new_notice`. Altbildrevision 0 nur bei noch fehlendem Record, sonst letzte; neue genau +1. Bindung ist aktuelle geprüfte Bindung beziehungsweise neue erste Bindung aus Altproduktion. |
| `old_reveal` | Exakt `file,sha256,bytes`, `file` genau `previous/<id>.<vorhandene-Endung>`, externe unveränderte Kopie der geprüften alten Live-Bildbytes, nicht null. |
| `new_reveal` | Exakt `file,sha256,bytes`, `file` genau `images/<id>.<vorhandene-Endung>` im Planordner, Hash/Bytezahl der kopierten neuen Bytes. |
| `old_record` | Null bei bisher fehlender Quelle, sonst exakt `text,sha256`, ursprünglicher vollständiger kanonischer UTF-8-Record samt LF und Dateihash. |
| `new_record` | Exakt `text,sha256`, vollständige nach Appendregel hergeleitete neue Quelle, inklusive Freigabe/Herkunft/Historie; nicht null. |
| `old_notice,new_notice` | Exakt `text,sha256` nach ZA-1; unveränderte Notice ist in beiden gleich. |
| `writes[]` | Nur tatsächlich geänderte Ziele, lexikografisch nach Pfad; je exakt `path,kind,old_sha256,new_sha256,bytes`. `kind` ist `binary-replace`, `text-add` oder `text-replace`; `bytes` neue Dateibytes, positiver Integer. Althash nur bei Textneuanlage null. |

`old/new_record.sha256` sind Dateihashes, `record_hash` innen ist der eigene
kanonische Objekthash. Alle Inhalte/Hashes/Bytezahlen werden selbst berechnet und
bei `adopt` neu geprüft. Schreibpfade werden **ausschließlich** aus geprüfter
Registry/ID hergeleitet und gegen `writes` exakt verglichen. Keine Eingabepfade
in den Checkout kopieren. Alt-/Neubildgrößen und Notice-/Recordgrößen folgen
ihren strengeren Einzelgrenzen. Ganze Plandatei und Bildinventar werden beim
Planabschluss frisch gelesen und unmittelbar vor sowie unter Lock erneut geprüft.

`adopt` konsumiert genau diesen unveränderten gespeicherten Plan; keine neue
Freigabe, ID-Auswahl oder Bilddateioption. Vollständige Quellen-/Namespacebindung
erneut prüfen, Alt-/Zielzustand isoliert validieren, Journal nach SD_CATALOG
erzeugen, gemeinsame Transaktion ausführen, abschließend den Zielcheckout prüfen.
Geänderter Registry-/Kategorie-/Runtime-/Definitions-/Rating-/Added-/AT-/Bild-/
Notice-/Produktionsstand einer beliebigen gebundenen ID ist stale. Keine neue
Analyse, kein Produktionsreplay allein wegen des Bildwechsels.

**Eigener No-op:** Alle `writes` müssen exakt ihre vollständigen eigenen Zielbytes
besitzen, sämtliche übrigen Quellen und Inventare weiterhin passen. Hinzugekommene
eigene AT-Recordpfade werden nur im rekonstruierten Namespaceinventar entfernt. Die
gebundenen Alttexte/Bildhashes werden nur im Speicher eingesetzt und ergeben
exakt den ursprünglichen Snapshot; der ursprüngliche Altcheckout wird ebenfalls
isoliert geprüft. Planbilder, Freigaben, Historie, Zielrevisionen und Recordbytes
müssen vollständig passen. Das Erreichen nur einer Teilmenge ist kein No-op.
Bei offener Transaktion zuerst Recovery, niemals No-op am Lock vorbei.
Erfolg vor Journalanlage, ohne Byte-/Revisions-/mtimeänderung oder Rewrite.
Fehlendes Ziel, andere Freigabe, ähnliche Pixel oder inzwischen dritte Bildrevision
blockieren als stale/conflict. Ein alter Plan nach Cleanup ist ebenfalls stale.

Stdout ist genau ein JSON-Objekt `picross-reveal-result-v1`, exakt
`format,status,plan_hash,ids,changes,error,recovery_required`.
`status`: `planned,adopted,no-op,invalid_input,aborted`; `plan_hash` Hash oder
null falls noch kein gültiger Plan ermittelt; `ids` geprüfte sortierte Auswahl
oder leere Liste vor gültiger Auswahl; `changes` bei `planned/adopted` exakt
`writes`, sonst `[]`. `error` null bei Erfolg, sonst exakt `code,message`:
Code `invalid_input,stale,conflict,io_error,resource_limit,interrupted`, Nachricht
1…2048 Zeichen, keine Secrets. `recovery_required` Boolean, true ausschließlich
bei erhaltenem offenen Lock oder konkret blockierendem Journalstagingrest.
Kein zusätzliches dauerhaftes Ergebnisformat: stdout darf extern protokolliert
werden; die dauerhafte Freigabe-/Revisionshistorie steht im aktiven Record.

| Exit | Ergebnis und Grenze |
| --- | --- |
| 0 | Nur `planned`, `adopted`, `no-op`; vollständige Prüfung erfolgreich. `planned` verändert keine Repositoryquelle. |
| 2 | Ungültiger/blockierter Eingang, stale Plan, Fremdkonflikt oder gewöhnlicher Datei-/Schreibfehler. Nach Mutation nur mit erfolgreichem Rollback oder ausdrücklich erhaltenem Journal samt `recovery_required=true`. |
| 4 | Zeit-/Speicher-/Signalabbruch; keine Erfolgsaussage. Journal-/Rollbackzustand nach Transaktionsvertrag. |

Unbekannte Optionen sind Fehler; kein Exit 0 für Teiladoption. Harter Kill kann
kein stdout garantieren. Der bestehende Recoveryeinstieg behält seine Ausgabe
`rolled-back/registered=false` bei Erfolg und seine 0/2/4-Konvention.
