# RP-1/RP-2: monochromer und farbiger Deduktionskern

Python **3.11+**, ausschließlich Standardbibliothek, ohne Installation von Paketen,
Netzwerk-/Modellaufrufe oder P1-Abhängigkeit. Aus dem Repository-Root ausführen;
unter Windows einen tatsächlichen Python-Interpreter statt eines Store-Alias nutzen.
Fachvertrag: [Rätselproduktion](../../docs/PUZZLE_PRODUCTION.md).
Prüfzuordnung: [RP1_VERIFICATION.md](../../docs/RP1_VERIFICATION.md).
Farberweiterung: [RP2_VERIFICATION.md](../../docs/RP2_VERIFICATION.md).
RP-1 ist über PR #42 in `main` integriert; RP-2 bleibt bis zum unabhängigen
technischen Review im eigenen Draft-PR gegen `main`.

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

## Verfahren und Ressourcen

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
und 15 Minuten Joblimit. Der eigene Testort liegt außerhalb des bestehenden
`tools`-Discoverys. `docs`, `product` und `preflight` bleiben unverändert aktiv.

`artifacts/puzzle-production/benchmark.json` (`picross-benchmark-v2`) bindet Source-Head,
Checkout/Test-Merge, Basis und Arbeitsbaum; Profil/Profilhash und Eingänge stehen
**je Fall**, kein pauschales Monoprofil für Farbläufe. Die bisherigen CI-Umgebungsnamen
`RP1_SOURCE_HEAD`/`RP1_BASE_COMMIT` gelten für den gemeinsamen Lauf weiter.
Pro Fall liegen Logik, Proof, Ergebnis,
frische Prüfung, getrennte Prozessmessdaten und Logs vor. Der CI-Artefaktname enthält
den Source-Head. Laufartefakte werden nicht eingecheckt. Ein anderer Head/eine neue
Basis braucht passend zugeordnete aktuelle Checks. RP2-A01 bis A06 und unabhängiges
technisches Review des kombinierten Kerns sind Mergegates. #41/#42 sind integriert;
Parent #34 und spätere Produktionspakete bleiben offen.
