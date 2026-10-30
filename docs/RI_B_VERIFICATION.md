# RI-B-T01: Prozesslokaler Paketprüfkontext

## Auftrag, Vertrag und Quellen

Beauftragt: #479 auf `feat/479-ri-b-verified-context`, Basis
`864c4e6289df15ea7b3522b850542ece3489160f` (RI-A/PR #484).
RI-B-V01 wurde vor der ersten Codeänderung am 30.10.2026 im
[Issue #479](https://github.com/venomenon328/picross/issues/479) gespeichert und
exakt zurückgelesen (`updatedAt=2026-10-30T15:08:53Z`); der unabhängige
[B/C-Schnittstellenabgleich](https://github.com/venomenon328/picross/issues/480)
ebenso (`15:08:58Z`). Die frühere Kontoblockade ist behoben.
Keine echte Rätselintegration, kein Merge und kein Chromiumauftrag.

RI-A-T01/N01 meldete historisch 4 Kandidaten-/Proof-/Exportprüfungen und
80 Guards je Registrierung; Export/Plan/Register 2/2/4. Historische
Registermediane Linux/Windows kurz/verschachtelt: 4,340/24,126/28,897 s;
P3 2,8836/16,6250/19,9770 s. Guards dominieren. Das sind keine Messungen
der aktuellen A-Basis oder des neuen B-Codes. Deshalb wird A erneut gemessen.

## Fachnachweise

Das neue [Testmodul](../tests/puzzle_production/test_registration_verification.py)
erweitert kleine unabhängige synthetische Fälle. Ein unveränderliches Export-
Grundfixture wird isoliert kopiert; keine echten Kataloginputs oder Cachematrix.

| Vertrag | Nachweis |
| --- | --- |
| B01/B02 | Tatsächlich erfolgreicher Eingang plus unabhängiger Staging-Replay; spätere P3/P5-Nachprüfungen kontrollieren vollständige sichere Inventare, Bytes und Identitäten. Byte-/Freigabeänderung, zusätzliche/fehlende Dateien, leeres Zusatzverzeichnis, bytegleicher Datei-/Stagingaustausch und Austausch des geschriebenen Pakets werden abgewiesen. |
| B01/B03 | Originalexport, Checked-Datei samt Identität, Ausgangssnapshot, vollständiges Journal, Addition-Mapping und tatsächliche Methoden-/Werkzeugbytes sind gebunden. Geänderte Kategorie bleibt durch die eigenständigen vollständigen Guards blockiert. Externes Pass-Objekt, rekonstruierte/kopierte/serialisierte, fremde Prozess-/Thread- oder beendete Instanz autorisieren keine Wiederverwendung. Fehlgeschlagener Replay erzeugt keinen aktiven Kontext. |
| B04/B05/B06 | Plan bleibt lesend und vollständig prüfend; positiver Registerlauf zählt zwei vollständige Kandidatenprüfungen, zwei gebundene Nachprüfungen und weiterhin exakt 80 Guards. Runtime-Definition/Reveal sind bytegleich zum Export. No-op erhält Bytes/mtimes; Updates und getrennte Befehle behalten ihren bisherigen Weg. |
| B07 | Gewöhnlicher Fehler, Ressourcenabbruch und Crash entziehen den Kontext. Automatischer/expliziter Rollback erhält den Altzustand. Fremde Bytes blockieren Recovery ohne Mutation; nach kontrollierter Rückgabe eigener Bytes gelingt sie ohne Kontext. Bestehende RI-A-Uhr-/Budget-/Journalregressionen bleiben aktiv. |

Globale Guard-Aufrufstellen/-frequenz, P0–P6/R0–R2 und Recoverysemantik bleiben
unverändert. Keine neue Journalgeneration; beide Methodenfreezes bleiben bytegleich.
Die eigenständigen Quell-/Namespacebindungen sind keine Autorität des B-Paketbeweises.

## Messung, aktuelle CI und Review

Messung und CI sind während der laufenden Implementierung noch offen.
Finaler Head, Basis, Test-Merge, konkrete Run-/Ergebnisbindung, Plattformwerte,
Rohberichthashes und getrenntes Selbstreview werden vor der Übergabe ergänzt.
Fehlende Plattformmessungen oder Pflichtjobs sind kein Erfolg.
Ein gesondertes qualifiziertes Review und ausdrückliche Mergefreigabe bleiben
vor Merge getrennte Gates; dieser Auftrag endet mit Draft-PR.
