# SD2-B-T01: Referenzen, Standalone-Bewertung und Freeze

Stand: 25.10.2026 · #404 / Umsetzungsvorbereitung V1 · Draft-PR #409

Basis: `c7c6156ac27dc033036443bc06ef398bbf94f32f`, integriertes und separat
abgenommenes SD2-A / PR #408. Arbeitsbranch `feat/404-sd2-calibration`.
[B-Vertrag](SD2_CALIBRATION.md), [Fachvertrag](PUZZLE_DIFFICULTY_V2.md),
[A-Vertrag](SD2_ANALYZER.md), [0.3-Freeze](SD_CALIBRATION.md).

## 1. Auftrag und versionierte Reihenfolge

Der ausdrückliche Ausführungsauftrag umfasst das vollständige B-Paket bis
Commit, Push und Draft-PR. Keine #405/#406-Implementierung, Bestandsanalyse,
Übernahme, Aktivierung, echten Saves, Merge oder Issue-Schließung.
Startprüfung: main erneut gefetcht, A-Merge bestätigt, vollständiger aktueller
Issue-Body und leere Kommentarliste gelesen; kein vorhandener 404-Branch/PR.
Der alte A-Arbeitsbranch blieb erhalten. Unversionierte fremde Dateien unter
`docs/design/` sind weder verändert noch aufgenommen.

| Schritt | Unveränderlicher Bezug / Ergebnis |
| --- | --- |
| Referenzen vor Scores | `ca31207e7e70b2610ec0ba5accb386fd6e7a017b`: 36 neue vollständige synthetische Muster, Herkunft/Erwartungen/20:16-Split gebunden |
| Zahlen- und Technikvertrag vor Bewertungscode | `99411e3`: exakte Formel, zehn Kalibrierungsvergleiche, eigene B-Hülle/CLI/Prüf-/Hash-/Fehlerverträge |
| Implementation und unabhängige Reproduktion | Neue isolierte B-Module; sämtliche A- und 13 gebundenen 0.3-Quelldateien unverändert |
| Getrennte Validierung | 16/16 Erwartungen und 2/2 Vergleichsordnungen erfüllt, keine Nachjustierung oder Umetikettierung |
| Freeze | `db882ea14b17de725bf75e64904579cc7790c875d557f036fdd89586f303a97c`, 27 Quellen / sieben JSON-Artefakte |

Der Referenzhash bleibt
`fb98b7c619f9933d111ad5f988579f38ae4fb72dd016a871d8fbb65b46a98456`.
Numerischer Vergleich und beide Evidenzdateien sind im Methodenmanifest gebunden.
Die Kuration sah vollständige Rohverläufe, aber keine Scores; nur Kalibrierung
beeinflusste die Formelwahl. Die Validierung ist damit kein menschlicher
Blindversuch. Menschliche Vergleichslösungen liegen nicht vor.

## 2. Akzeptanzzuordnung

| Kriterium | Tatsächlicher Prüfgegenstand |
| --- | --- |
| B01 | Vorab committed Herkunft, vollständige Matrix/Logik/Spur-/Proofhashes, Auswahlgründe, Stufen und Ordnungen; unabhängige Gruppen, Symmetrie-/Farbkanonisierung findet keine Dubletten; keine Kataloginputs |
| B02 | 20 Kalibrierungs- und 16 Validierungsrätsel vollständig deduziert und unabhängig aus Dateien geprüft; jede Stufe mehrfach in jedem Split; reines E3 und notwendiges R4 auf L5; exakte Gleichheit und ±1/10³⁰ an allen vier Schwellen |
| B03 | Getrennte feste Evidenzdateien: 20/20 und 16/16 Erwartungen, 3/3 und 2/2 Ordnungen; Vergleich ohne Kontext/Suche/Umfang, mittlere Suche, verdünnte Stärke, Zellzahl, fehlende Wiederholung, ±10 % Suchgewicht |
| B04 | Ganze 50×50-Vollfläche, 40×30-Bänder, 31×25-gepackte Farbeinser und flüssiges E1 bleiben L1; enge E1/E2/E3 unterschieden; zusätzliche triviale Profilwellen verdünnen späte Spitze nicht; monotone Umfangsgrenzen, maximal eine Nachbarstufe und Schutz vor alleiniger L4/L5-Erhöhung |
| B05 | Getrennte drei Beiträge, exakter Gesamtscore/Stufe, Wert ohne Umfang, untere/obere/nächste Grenzentfernung; Markdown bytegenau geprüft; medium/keine Minuten; unrated und R4-Präfixe ausdrücklich erkennbar |
| B06 | Wiederholung gleicher Ergebnis-/Markdownbytes, acht Symmetrien für vier ganze E1/E2/E3-/Farbmuster, Farb-ID-Bijektion, gedrehter vollständiger R4-Fall; Eingabe-/Beleg-/Datei-/Budget-/Abbruch-/Freeze-Manipulationen; alle 13 alten Quellen und kompletter 0.3-Freeze unverändert |

Die neuen Tests stehen in
[test_sd2_rating.py](../tests/puzzle_production/test_sd2_rating.py).
[reference_evidence](../tools/puzzle_production/sd2_reference_checks.py)
berechnet ausschließlich den festen synthetischen Satz, prüft A-Bundles frisch,
bestätigt vollständige Endmatrizen und bindet Paarfälle an die frisch geprüfte
Linienbaseline und den vollständigen Paarproof. Isolierte Profilgegenproben
sind ausdrücklich keine Stufenbelege und werden vom öffentlichen Filechecker
nicht als gültige Eingabe akzeptiert.

Die Datei-Gegenproben ändern Beiträge, Stufe, Grenzabstand, Aussagekraft,
Minuten, Methodenhash, Profilumfang, Rohprofile, Spuren, Zielbindung, zusätzliche
Freigabefelder und Dateimengen; neu berechnete Selbsthashes retten diese Fälle
nicht. Auch ein vollständiger Paarproof mit abgebrochener Baseline und
`deduction_complete=true` bleibt ohne Rating. Der A-Checker weist weiterhin
ein zusätzliches `rating.json` zurück. Prüfung nutzt keine Analysatorfunktion
als Beweisersatz; vorhandene A-Verifier-Regressionen sichern die Trennung.

## 3. Laufnachweise und CI-Bindung

Lokal: Python 3.13.14 unter Windows; ausschließlich synthetische Tooltests und
temporäre Verzeichnisse. Der erste gezielte B-Lauf bestand mit 19/19 Tests
(51,494 s); nach ergänzten Fehler-/Datei-/Runtime-/R4-Proben bestand der
vollständige B-Lauf mit **23/23 Tests (57,033 s)**. Alle aufgeführten negativen
Proben erreichten ihre erwartete Ablehnung. Vollständige CI folgt der tatsächlichen Base-/Head-Auswahl.
Es gibt keine Änderung am Selektor und keine pauschale SD2-Ausnahme.

Der [Implementierungs-PR #409](https://github.com/venomenon328/picross/pull/409)
bindet den finalen vollständigen Head, Basis, Test-Merge, Run, tatsächliche
Jobauswahl und Ergebnisse. Zwischenläufe gelten nicht als finale CI.
Der erfolgreiche A-Lauf ist ausschließlich Basisnachweis, kein B-Pass.
Technische Laufzeiten messen keine menschliche Lösungsgeschwindigkeit.

## 4. Getrennter Selbstreview und offene Gates

Nach Implementation wird der vollständige Base-/Head-Diff in einem getrennten
Prüfschritt gegen B01–B06 und die aufgeführten Fach-/Dateiverträge gelesen.
Der PR bindet diesen Selbstreview an den endgültigen Head und protokolliert
eventuelle Korrekturen sowie den anschließenden CI-Stand. Die großen JSON-Dateien
werden vollständig geparst und semantisch samt Herkunft, Gruppen, Formeln,
Erwartungen, Belegen und Hashbindungen geprüft; keine bloße Diffstat-Abnahme.

- **A-SD2-B-R01:** Qualifizierter separater Review des finalen Heads durch einen
  anderen Reviewlauf vor Merge. Selbstreview ersetzt diesen nicht.
- **A-SD2-B-MERGE:** Ausdrückliche Eigentümerfreigabe nach erfüllten Gates vor
  Merge. Dieser Auftrag enthält keinen Merge.
- Menschliche Vergleichslösungen bleiben freiwillig und nicht blockierend;
  Aussagekraft höchstens mittel, keine empirische Genauigkeit oder Minuten.

Gemeinsame Integration und Aktivierung sind offen in #405/#406, außerhalb
dieses Pakets. Aktive Werte, Definitionen/Bilder/Added-Daten, Runtime-/Journal-
Formate, Produktionsfreigaben und Spielstände bleiben unverändert.
