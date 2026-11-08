# RI-C-T01 · Phasenweise Registrierungsguards

Auftrag RI-C-F01 / RI-C-V01 aus [#480](https://github.com/venomenon328/picross/issues/480),
Basis `6d9982bb6f6e5b50a1a9bdb194ff1dd471db328b`. Die Lieferung betrifft nur
Erstregistrierung v6 und ihre Recovery. Kein Merge, keine echte Rätselproduktion.
Die verbindliche Quellen-/Erkennungszuordnung steht im
[Transaktionsvertrag](SD_CATALOG.md#ri-c--phasengrenzen-für-erstregistrierung-v6).

## Vorab festgelegter Prüf- und Messumfang

`tools`, `production.catalog`, `production.adapter` sowie docs/ci-required und
regulärer Windows-Build laut [.ci/package.json](../.ci/package.json).
Keine neue CI-Jobfamilie, kein Chromium, keine echten Kataloginputs.
Neue Fälle sind paketbezogene Tests; kein zusätzlicher CI-Kern oder Dauerbenchmark.

Der [manuelle Messtreiber](../tests/puzzle_production/ri_c_measurement.py) verwendet
zwei vor Ausführung festgelegte Reihen: Katalog 0/1/2 bei festem Neupaket und
Neupaket mit 0/4/8 zusätzlichen gebundenen Textdateien bei Bestand 1. Alle Quellen
sind künstliche 3×3-Mono-Pakete; Bestandsproduktionen werden zu gültigen Receipts
kompaktiert. Gleiche Neupaketidentität, feste Added-Zeit, unveränderte Eingangsbytes
für Basis/Head und alle Plattformen; drei frische Wiederholungen pro Punkt.
Setup, Wallclock, P0–P6, volle Guards, G-Grenzen, gelesene/gehashte Bytes,
isolierte Checkoutrekonstruktionen und vollständige Proofprüfungen werden getrennt
gemessen. Phasen sind inklusiv, nicht additiv zu enthaltenen Teilprüfungen.
I/O-Zähler erfassen `catalog_io`, nicht sämtliche OS-/Python-Lesevorgänge.

Geplant: unveränderte main-Basis gegen Lieferung, natives Linux und Windows/NTFS
mit kurzem und normal verschachteltem Pfad. Rohprofile und synthetische Checkouts
sind temporär; kompakte Tabellen und genaue Commit-/Runbindungen bleiben im PR.
Ein nicht tatsächlich gemessener Plattformpunkt bleibt ausdrücklich T01-Gate.

## Kriterienzuordnung

| Kriterium | Konkreter Nachweis |
| --- | --- |
| C01 | Neues `test_registration_publication`: echte Fremdänderung an G0/G2/G5a/G5b/G6, GR0/GR2 und lokalen Ziel-/Temp-/Elternprüfungen; alle T-/K-Dateien eines synthetischen Altbestands, erwartete Abwesenheiten, fremde Verzeichnisse, Alias/Hardlink und tatsächliche Freeze-Dateien. Gültige Bytes in falscher Phase werden abgewiesen; eine direkt vor OS-Rename injizierte Textneuanlage bleibt atomar no-replace geschützt. |
| C02/C08 | Obige festgelegte Reihen; kompakte tatsächliche Tabellen, Plattform- und Quellbindung im RI-C-T01-M01-Anhang des PR. Der Treiber prüft 30/34/38 tatsächliche Exportdateien; die Zusätze sind im synthetischen Handoff als Gatebelege gebunden. |
| C03–C05/C07 | Unterbrechungen P0, partielles/vollständiges Journal, P1/P2, mehrere P3/P4-Schritte, vor/nach Runtime, P6 und wiederholte R0/R1/R2-Recovery; echte Kill-/Rekill-/Signalprozesse. RI-A-Fälle prüfen getrennte Deadlines und dauerhaft abgeschlossenen Erfolg. |
| C06 | Expliziter v6/Operationsdispatch; vorhandene vollständige Katalog-/Adaptertests prüfen alte Registrierung, Update, Sync, Metadaten, Bild- und Methodenpfade. RI-B-Positivfall erhält zwei vollständige Proofprüfungen, No-op-Bytes/mtimes und eigenständige Recovery. |
| C09 | Ein Draft-PR mit finaler Head-/Basis-/Test-Mergebindung, ausgewählten tatsächlichen Checks und getrenntem Selbstreview. Qualifiziertes unabhängiges RI-C-R01 bleibt vor Merge erforderlich. |

Der Abschlussstand, RI-C-T01-M01 mit Messwerten und RI-C-T01-CI mit tatsächlicher
Head-/Basis-/Test-Mergebindung stehen im [Draft-PR #544](https://github.com/venomenon328/picross/pull/544).
Dort wird auch der getrennte Selbstreview dokumentiert. Ein fehlender oder
fehlgeschlagener Nachweis ist kein Pass; das unabhängige RI-C-R01 bleibt separat.
