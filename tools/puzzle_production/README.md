# RP-1 bis RP-4: Deduktionskern und Bildproduktion

Python **3.11+**, ausschließlich Standardbibliothek, ohne Installation von Paketen,
Netzwerk-/Modellaufrufe oder P1-Abhängigkeit. Aus dem Repository-Root ausführen;
unter Windows einen tatsächlichen Python-Interpreter statt eines Store-Alias nutzen.
Fachvertrag: [Rätselproduktion](../../docs/PUZZLE_PRODUCTION.md).
Prüfzuordnung: [RP1_VERIFICATION.md](../../docs/RP1_VERIFICATION.md).
Farberweiterung: [RP2_VERIFICATION.md](../../docs/RP2_VERIFICATION.md).
RP-1/RP-2 sind nach unabhängigem Review über PR #42/#43 in `main` integriert.
RP-3-Bildbefehle benötigen die separate Image-Umgebung weiter unten; die bisherigen
Kernbefehle bleiben ohne Pillow nutzbar. [RP-3-Prüfzuordnung](../../docs/RP3_VERIFICATION.md).

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
Basis braucht passend zugeordnete aktuelle Checks. #41/#42/#43 sind integriert;
Parent #34 und spätere Produktionspakete bleiben offen.

## RP-3: isolierte Image-Umgebung und reale Befehle

Pillow **exakt 12.3.0**, ausschließlich für Bildbefehle/-tests. Die CI installiert
[requirements-image.txt](requirements-image.txt) in einer temporären venv. Lokal:

```sh
python3 -m venv .venv/rp3
.venv/rp3/bin/python -m pip install --only-binary=:all: -r tools/puzzle_production/requirements-image.txt
.venv/rp3/bin/python -m tools.puzzle_production import-image --input examples/rp3/source.png --design examples/rp3/design.json --output-dir artifacts/rp3-import
.venv/rp3/bin/python -m tools.puzzle_production export-p1 --bundle artifacts/rp3-import --variant area-128 --reveal examples/rp3/reveal.svg --name Fliegenpilz --output-dir artifacts/rp3-export
.venv/rp3/bin/python -m tools.puzzle_production.rp3_demo --output-dir artifacts/rp3-demo
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
Definition/Revision, Farbzuordnung und Reveal-Dateihash. `rp3_demo` importiert real
erneut, prüft das eingecheckte Bundle frisch und vergleicht Matrix/Logik/Entwurf
sowie den neuen Definitions-/Assetexport bytegenau mit dem registrierten P1-Inhalt.
Auch der gespeicherte Export wird aus seinem gebundenen Produktionsbundle frisch
rekonstruiert. Der Bericht führt ursprüngliche und neu erzeugte Kandidatenkennung
samt beiden Codecständen. `product` ergänzt reguläre Hauptszene,
drei isolierte Neustartprozesse und native Arbeits-/Abschluss-/Albumrenders.
RP3-A01 bis A06 einschließlich unabhängigem technischem/visuellem Review R2
sind über PR #44 integriert. Eine echte Eigentümer-Lösung bleibt RP-6-Gate.

## RP-4: feste Vergleichsbaseline

[Zwölf Quellen und Offlinevergleich](../../examples/rp4/README.md),
[Methodik/Ergebnis/Prüfzuordnung](../../docs/RP4_VERIFICATION.md).
Gleiche Image-Umgebung, keine neue Abhängigkeit. Beispiel für eine eigene venv:

```sh
python3 -m venv .venv/rp4
.venv/rp4/bin/python -m pip install --only-binary=:all: -r tools/puzzle_production/requirements-image.txt
.venv/rp4/bin/python -m tools.puzzle_production.rp4 verify --output-dir artifacts/rp4-replay
.venv/rp4/bin/python -m unittest discover -s tests/puzzle_production -p 'test_rp4*.py' -v
```

Der Korpusprüfer validiert alle zwölf Quellen, sechs Fotopaare, vier zusätzliche
100×100-Quellen, vollständige Entwürfe/Budgets und sämtliche originalen Resultate.
Die vorhandene RP-3-Rekonstruktion erzeugt Normalisierung/Matrix/Hinweise neu und
replayt die geschriebenen Proofs unabhängig. Original und Replay bleiben getrennt;
ein später erfolgreich geprüftes ursprüngliches Abbruchresultat erhöht die
Originalausbeute nicht. Raster-/Kandidathashes binden die 48 redaktionellen Urteile.
Maschinelle Urteilsbindung ersetzt keine echte Sichtprüfung.

Eigene Illustrationen werden getrennt in temporären Dateien neu erzeugt und auf
exakte Dateimenge, ursprünglichen Modus, Abmessungen und dekodierte Pixel geprüft.
Andere PNG-Kompression bei gleichem Bild ist zulässig. Gespeicherte Originaldateien
und das ebenfalls im Input-Lock enthaltene Erzeugungsskript bleiben dagegen strikt
per SHA-256 gebunden. Positive Codec- sowie negative Pixel-/Modus-/Dimensionsfälle
und die Zurückweisung umkodierter gespeicherter Originale sichern R1/B-01 ab.

Der gemeinsame CI-Job führt das Replay mit 600 s Gesamtbudget und maximal 11 Minuten
für diesen Schritt aus; bestehende Fachoracles, Referenzbudgets und P1-Demo bleiben
aktiv. Ergebnisse stehen im Fachartefakt unter `rp4/verification.json` mit
Source-/Checkout-/Basis-/Runbindung. Kein nativer Bildaufruf in CI.

Ein separater Windows-x64-Job führt ausschließlich die RP-4-Tests mit Python 3.12.10
und dem offiziellen Pillow-12.3.0-Wheel in temporärer venv aus. Er hat lesende Rechte
und zehn Minuten hartes Joblimit, reproduziert die dokumentierte R1-PNG-Abweichung
am Ausgangstest und verlangt danach vollständig erfolgreiche aktuelle Tests.
Laufzeit-/Codec- und Commitbindung stehen in einem kleinen separaten Artefakt.
Die Linux-RSS-Referenzen und der vollständige Fachjob bleiben erhalten.

R1/A-01: Der [tatsächlich ausgelesene Original-Commitpayload](../../examples/rp4/provenance/producer-726e89d.commit)
ist im Paket erhalten. [Prüfanleitung](../../examples/rp4/README.md) und zusätzlicher
Fachtest binden die Originalbytes an Git-Objekt-ID, veröffentlichten Tree und
unveränderten Produktionsreport. Dafür ist kein historisches Originalobjekt in der
lokalen Git-Datenbank erforderlich.

Optional `rp4 produce --output-dir <neuer-pfad>` für neue deterministische Imports;
die versionierte Baseline niemals überschreiben. `freeze` verweigert erneutes
Fixieren bereits gesperrter Inputs. `views` und `index` bauen nur Dateiansichten.
19 Zertifikate bedeuten hier 14 zusätzlich motivisch brauchbare Varianten aus
sechs Quellen, keine abgeschlossene Pilotproduktion. Unabhängiges RP-4-Review R1
ist durchgeführt; die commitgebundene Nachprüfung von B-01/A-01 und Integration
stehen in PR #45. Eigentümer-Lösung bleibt RP-6-Gate.
