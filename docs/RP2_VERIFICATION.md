# RP-2: Prüfvertrag und Nachweiszuordnung

Stand: 04.10.2026 · Arbeitsfassung 0.1 · implementiert, unabhängiges Review offen

Auftrag: [Issue #36](https://github.com/venomenon328/picross/issues/36), vollständiger
Body einschließlich Umsetzungsvorbereitung vom 04.10.2026; [Parent #34](https://github.com/venomenon328/picross/issues/34)
bleibt offen. [Fachvertrag](PUZZLE_PRODUCTION.md), [Werkzeuganleitung](../tools/puzzle_production/README.md),
[RP-1-Historie](RP1_VERIFICATION.md). Keine Motiv-/Spielabnahme, kein Releaseauftrag.

## Startprüfung und Vertragsbindung

Aktuelles `main@b18a23460708509adac2f04e724809cf0cc8b959` entspricht der Vorbereitung.
#41/#42 integriert, #35 geschlossen; #34/#35/#36 ohne spätere Kommentarentscheidungen.
Kein vorhandener RP-2-Branch/PR, sauberer Arbeitsbaum, keine weiteren AGENTS-Regeln.
Arbeitsbranch `feat/36-color-deduction-core` vom aktuellen `main`; eigener Draft-PR
gegen `main`. Keine Änderung gemeinsamer Regeln, P1-Daten oder Produktworkflows.
Technische Vorbereitung und Umsetzung erfolgen im vollständigen Codex-Checkout;
Python 3.12.10 ist lokal verfügbar, Repository-/CI-Zugriff über Git/gh geprüft.

Neue Verträge: `picross-logic-v2`, `picross-proof-v2`, `color-gap-v1`,
`full-line-color` Version 1. 1..8 Vordergrundfarben plus Leer, 1..100 je Achse;
32-Zeichen-ID-Grenze und normalisierte Palette. Alte Monoformate/-profile behalten
ihre Hashbedeutung. Solver-Zellautomat und Prüfer-Blockintervall-DAG sind getrennt;
keine gemeinsame Übergangs-/Folgerungsroutine. Fortschritt folgt jedem Domainverlust.

## Akzeptanzzuordnung

| Kriterium | Ausführbarer Nachweis |
| --- | --- |
| RP2-A01 | `test_color_lines.py`: alle Wertbelegungen, daraus realisierbaren Hinweisfolgen plus drei übervolle Folgen und sämtliche Domainkombinationen einschließlich leerer Domains. Zwei Farben n=1..4: 191152; vier Farben n=1..2: 24832; acht Farben n=1: 6144. Insgesamt 222128 Vergleiche, jeweils Solver UND Prüfer gegen reine unabhängige Wertfolgenaufzählung. Dazu gleiche/verschiedene Nachbarfarben, getrennte/berührende Blöcke, 100er-Linien einschließlich Bit 8. `test_color_core.py` prüft vier Farben, Rechtecke und 1×100/100×1; Palette 1/8 sowie ungültig 0/9 und maximale IDs/Hinweislisten. |
| RP2-A02 | Gespeicherter 4×4-Fall `color-propagation.json`, unabhängiger kreuzender Linienoracle und vollständig iterierter Singleton-Gegenlauf; konkreter Kausalbeleg unten. |
| RP2-A03 | Farbige vollständige Nachweise, Fixpunkte, widersprüchliche Hinweise und kontrollierte Teilabbrüche; drei Reihenfolgen mit gleichem Fixpunkt. Direkte Länge-/Farbrunprüfung inklusive berührender verschiedener Farben; gezielt vergifteter Supportchecker beweist die zusätzliche Endkontrolle. Angriffe auf Farbverluste, Voraussetzungen, Palette, Regeln, Profil, Formate, Enddomains, Spurkürzung und unbegründeten Widerspruch werden abgewiesen; gesperrte Solverfunktionen verhindern keine unabhängige Prüfung. Farb-CLI speichert und prüft in frischen Prozessen, Abbruch ohne Zertifikat. |
| RP2-A04 | Alle ursprünglichen 23 RP-1-Tests bleiben erhalten, einschließlich JSON-Fehlerklassifikation aus Review B-01. Unveränderter alter Proof mit SHA-/Profilbindung wird eingelesen und gegen neu erzeugte Monoableitung verglichen. Außerhalb des Logikeingangs umbenannte Bild-/Motivmetadaten ändern dieselbe Ableitung nicht; solche Felder bleiben im strikten Eingang unzulässig. |
| RP2-A05 | Gemeinsamer Benchmark mit drei unveränderten Mono- und drei festgelegten Vierfarbenfällen, isoliertem Solve/Serialisierung und frischer unabhängiger Prüfung; Linux-Messung/Budgets unten. Woven-Fälle bestimmen tatsächlich vier Farben plus Leer mit vielen partiellen Änderungen. Schwierige Langlinien haben mehr als 5·10²⁰ mögliche Belegungen, ohne sie im Kern aufzulisten. |
| RP2-A06 | Gemeinsamer CI-Job, gespeicherte Mono-/Farbaufrufe in der Anleitung, nachvollziehbare Schema-/Profilversionen, Grenzen und konsistente Quellen. Benchmark v2 bindet das tatsächlich verwendete Profil je Fall; aktuelle CI-/Head-/Basis-/Artefaktnachweise und Selbstreview stehen im Draft-PR. Unveränderte `product`-/`preflight`-Jobs werden separat ausgewiesen. |

Die Oracles liegen ausschließlich in den Fachtests. Der große Bereich wird durch
gezielte Grenz-/Regressionstests geprüft; die kleine Matrix ist keine erschöpfende
Enumeration aller 100er-Linien oder aller Achtfarbenraster.

## Notwendige partielle Propagation

Der 4×4-Fall besitzt Zeilenhinweise R1/B2, B1/R2, R1/B1, R1/B1 und
Spaltenhinweise B1/R2, R1/B2, B1/R1, B1/R1. Jede Zelle startet E/B/R.
Zeile 0 schließt B an (0,0) aus, obwohl B in derselben Linie vorkommt; E/R bleibt
mehrwertig. Nach den vier ersten Zeilenableitungen sieht Spalte 0
`[E/R, E/B, E/R, E/R]`. Der unabhängige vollständige Linienoracle erhält
`[E, B, R, R]`. Wird ausschließlich an (0,0) die ausgeschlossene Farbe B
wieder zugelassen, erhält derselbe Oracle `[E/B, E/B, R, R]`: die Festlegung
von (1,0) auf B benötigt genau diese Einschränkung der kreuzenden Zelle.

Der gesamte unabhängige Gegenlauf übernimmt nur Singleton-Folgerungen und erreicht
den unveränderten Fixpunkt (Bits E=1/B=2/R=4):
`[[7,7,2,7],[7,7,4,7],[4,2,1,1],[7,7,1,7]]`.
Der vollständige Domainlauf löst das Raster dagegen mit elf geprüften Schritten.
Der Test vergleicht beide und die Kreuzung kausal; kein folgenloser Ausschluss
einer gar nicht vorkommenden Farbe dient als Nachweis.

## Unveränderter RP-1-Beleg

Vor jeder Farberweiterung mit dem Originalkern auf `main@b18a23460708509adac2f04e724809cf0cc8b959`
aus `deductive.json` erzeugt, als kleine Fixture `rp1-proof.json` byteidentisch übernommen.
Eingangsdatei-SHA-256: `fdca848d541c4205c907dd8d7186cca556c57a35999632e9873fc70a3d89ac2b`.
Proof-Datei-SHA-256: `4886034235a2681ce4d7699ab212d978b1de9f7be3396d4edc034ff2c880a12d`.
Logikhash: `dc6699f16ee7df3960bad1e8b457acfaa7605bd407fcfaaf8e083687c453d241`.
Das ursprüngliche Mono-Profil und dessen Hash bleiben gebunden. Laufzeiten gehören
nicht in den Proof; der aktuelle Kompatibilitätstest erzeugt keinen Ersatz für diese Fixture.

## Vorab festgelegte Referenzen und Budgets

Vor dem CI-Abschlusslauf festgelegt: `bars-40`, `bars-100`, `sparse-100` bleiben
unverändert. Dazu `color-woven-40` und `color-woven-100`: zentrierte verschachtelte
Flächen mit internen Farbblöcken nach `(x//5+y//7)%4`, also Farbwechseln in beiden
Achsen statt umbenannter Monohinweise. `color-sparse-100` verwendet Hinweise eines
diagonalen Rasters: belegt genau bei `(x+y)%5=0`, Farbe `1+((x+y)//5)%4`.
Jede Linie enthält 20 Einserblöcke wechselnder Farben, mit
`C(100,20)=535983370403809682970` möglichen unbekannten Platzierungen.
Erwartet: die beiden Woven-Fälle vollständig, der Sparse-Fall unvollständiger Fixpunkt.
Existenz-/Zielmatrizen dienen ausschließlich Fixtureerzeugung und separaten Solltests.

Unverändert aus #36: **120 Sekunden je Fall** inklusive Solve/interner Prüfung,
Serialisierung, frischer Prüfung und Prozessstarts; **512 MiB gemessener Linux-Peak-RSS
je isoliertem Prozess**. Ubuntu 24.04, Python 3.11+, 15 Minuten Joblimit, lesende Rechte.
Zusätzlich erzwingt jeder Linux-Worker `RLIMIT_AS=1024 MiB`; das ist kein RSS-Messwert.
Hardware/Python, getrennte Zeiten, Peakwerte, tatsächliche Schritte, Hashes und
Source-Head/Basis/Checkout stehen in `benchmark.json` und den zugehörigen Fallartefakten.
Timeout, Prozessfehler, fehlende RSS-Messung oder Budgetüberschreitung führen zu
`accepted=false`. Budgets bleiben unverändert; keine universelle Laufzeitgarantie.

Lokale Windows-Entwicklungsprüfung führt alle sechs Fälle und frische Prüfungen aus.
Woven-40: 131 Schritte/1588 partielle Änderungen; Woven-100: 431/11630;
Sparse-Farbe: 271/1333. Linux-RSS ist lokal nicht verfügbar, deshalb ist lokale
Benchmark-Abnahme korrekt `accepted=false`; sie ersetzt RP2-A05-CI nicht.
Konkrete aktuelle CI-Messwerte und Ergebnisse gehören in den Draft-PR.

## Abschlussprüfung und offene Gates

```sh
python3 -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python3 -m tools.puzzle_production.benchmark --output-dir artifacts/puzzle-production
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/check_docs.py
git diff --check <tatsaechliche-pr-basis> <head>
```

Aktuelle erfolgreiche `puzzle-production`-/`docs`-Jobs, vollständiger Paketdiffcheck
und RP2-A01 bis A06 sind vor Merge erforderlich. Das unabhängige technische Review
des kombinierten RP-1/RP-2-Kerns am benannten Head bleibt separat offen; Selbstreview
erfüllt es nicht. Basisänderungen benötigen passende Integrations-/Checkbindung.
Reale Eigentümer-/Motiv-/Spielprobe ist für diesen externen Logikkern nicht anwendbar.
Kein Merge/Release, Parent #34 bleibt offen; RP-3 bis RP-6 werden nicht vorweggenommen.
