# KU-B · Prüfzuordnung und technische Übergabe

Auftrag: ausschließlich KU-B aus [#244](https://github.com/venomenon328/picross/issues/244),
Branch `feat/244-katalogsortierung`, Ziel `main`, geprüfte Basis
`04b77dc6c6487890e0de5a5711ed5e496ee0d4af`. Die Verträge wurden vor der ersten
Produktänderung in Commit `ae0881e` festgelegt. Der vollständige historische Plan
wurde separat in `dcc9006` versioniert; [Bestandsnachtrag](KU_B_BACKFILL.md).

## Prüfrouten

| Kriterien | Implementierung und synthetische Nachweise |
| --- | --- |
| A01–A03 | Katalogsortierung über redaktionelle Kategorie, Zellanzahl, bestehende Stufe und UTC; Primärrichtung, kanonische Gleichstände, unbekannte Werte hinten. `ku_b_cases.gd`, native 300-Karten-Matrix und Browser `KU-B01`. |
| A04 | Eigene atomare native Präferenz; echte Dateisystemfehler, Lesefallback, Wiederholung und getrennte Browser-Flushgenerationen. `ku_b_cases.gd`, nativer Zwei-Prozess-`p13_roundtrip.gd`, Browser `KU-B02` einschließlich echtem Prozessneustart und IndexedDB-Fehler. |
| A05 | Gesamten Filter sortieren, dann 24 Karten; Rückkehr-/Seiten-/Scrollzustand und feste IDs. Bestehende KAT/KK-Reset-/Recoveryrouten bleiben erhalten; Adapter-/Saveprüfungen adressieren ihre ID unabhängig von Anzeigeindizes. |
| A06–A07 | Gemeinsamer Projektor, neue und alte Journale, Namespace-/Quellen-/Fremdbyteguards, Registrierung ohne Planzeit, unveränderte Updates und Recovery direkt nach v4. `test_catalog_added`, bestehende Integrations-/Updatefälle und eingefrorene Legacy-Recoverybytes. |
| A08–A09 | Getrennter expliziter Git-/PR-Plan, dauerhaft gebundene Quellen und tatsächliche Übernahme für alle 26 IDs. Identische Wiederholung: 28 Dateien byte-/mtimegleich, kein Journal. Kein Rätsel-/Bewertungs-/Produktionsreplay und keine Saveänderung. Synthetische Verläufe prüfen Quellenpriorität, Konflikt, unbekannt, Stale-Plan und No-op. |
| A10 | Bedienanleitung, Werkzeug-/Datenverträge, native und Browserinventare sowie vollständige tatsächlich ausgewählte PR-CI. |

Die echte Bestandsrekonstruktion ist ein separater redaktioneller Nachweis,
kein allgemeiner Testkorpus. Bestehende Rätseldefinitionen, Bewertungen,
Methodenfreeze, Produktionspakete und Runtime-Revisionen bleiben unverändert.

## Reproduktion und Bindung

Aus dem sauber ausgecheckten Prüfhead:

```powershell
python -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python tools/p1_product.py --groups core,history,catalog,completion,adapters,graphics,export --cache-dir <Archivcache> --output-dir <neues-Verzeichnis>
python tools/ku_b_windows_probe.py --head <voller-Head> --run <PR-CI-Run> --engine <gebundene-console.exe> --cache-dir <Archivcache> --output-dir <neues-Verzeichnis>
```

Godot 4.7.2, Archivhashes, RTX-3070-Grafikstart und lokale Chromium-/Firefoxstarts
wurden vor Produktänderungen geprüft. Native Proben verwenden isolierte Profile;
Webnachweise verwenden beide tatsächlichen Browser, IDBFS und den vorhandenen
exklusiven Web-Lock. Der finale PR führt Head, Basis, CI-Checkout, Run/Attempt,
Originalberichte/-dateien und den getrennten Selbstreview. Diagnoseläufe auf
uncommittetem Stand sind keine finale Head-Abnahme.

## Offene Gates

Der aktuelle KU-B-T01-Status mit unveränderlichen Originalnachweisen steht im
[Implementierungs-PR #255](https://github.com/venomenon328/picross/pull/255).
Er wird erst nach den vollständig gebundenen finalen Prüfungen als erfüllt geführt.
KU-B-R01 (separater qualifizierter Review) und KU-B-M01 (Eigentümerprobe) sind
weiterhin getrennt vor Merge erforderlich. Kein Merge, Deployment oder Abschluss
von Issue #244 durch diese Lieferung.

Main-Push-Run [39149747167](https://github.com/venomenon328/picross/actions/runs/39149747167)
auf der Ausgangsbasis ist bereits rot: CI-A-Auswahltest und anschließende
Ergebnisbindung. KU-B repariert diesen separat dokumentierten Befund nicht.
Ausgelassene/fehlgeschlagene Pflichtjobs gelten nicht als bestanden; etwaige
Integrationsblocker werden im PR und Issue offen ausgewiesen.
