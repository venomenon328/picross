# PW-PERF-B: befristete Originale für A01

Empfänger: unabhängiger technischer Reviewer von PR #656. Zweck: T01/T02 und
K01–K08 gemäß [Paketentscheidung](https://github.com/venomenon328/picross/issues/653#issuecomment-6887731468).
Produkthead `58e8fb32ac61e432268c771f972f5442bc226866`, Basis
`c243d9ce95f7cfe55332840f3bf44b313d3b9128`, CI-Testmerge
`e4223a97934132e30da647c7fc3a853a57fb3411`.

Nur auf `review/653-pw-perf-b-final-until-20261122`, abgezweigt vom Produkthead.
Nicht in main oder den Produktbranch übernehmen. Bereitgestellt bis **2026-11-22**.
Der zuständige Paketbearbeiter entfernt den Ref nach A01 im beauftragten Rückbau;
bei offenem A01 am Ablaufdatum zuerst Zustellung/Bedarf erneut prüfen. Git-Refs
laufen nicht automatisch ab. Kein dauerhaftes Leistungsarchiv.

## Ergebnis und Originalzuordnung

| Register-/Planwert | Vorher v9 | Nachher v10 | K07 |
| --- | ---: | ---: | ---: |
| Plan, Sekunden | 44,864 | 15,833 | <=46 |
| Register, Sekunden | 132,141 | 38,640 | <=136 |
| Sichere catalog_io-Reads | 20.377 | 2.773 | <=15.759 |
| Gelesene catalog_io-Bytes | 6.667.817.833 | 1.229.828.452 | <=4.592.885.636 |
| Vollständige Katalogprüfkopien | 3 | 0 | 0 |
| Bytes dieser Kopien | 507.635.319 | 0 | 0 |
| Vollständige neue Replays / Readbacks / Grenzen | 2 / 2 / 5 | 2 / 2 / 5 | 2 / 2 / 5 |

Nachher: keine Reads/Hashes/Decodes unbeteiligter alter Paket-/Liveassetdateien
in Plan und Register; `plan-work.json.old` und `register-old.json` sind leer.
Der synthetische T01-Fall prüft zusätzlich den frischen No-op und zusätzliche
unbeteiligte Archive/Livebilder. Die reale Integration wurde nur je einmal positiv
ausgeführt; keine negative Echtintegration, kein zweiter Nachherlauf nötig.

- [comparison.json](comparison.json): abgeleitete Tabelle, vollständige Zahlen,
  Budgets und disjunkte Zeitanteile; kein Ersatz für die Originale.
- [before](before), [after](after): unveränderte `inputs`, `plan-operation`,
  `register-operation`, `plan-work`, `register-old`, `work-amounts`,
  `observations`, `registration-diff`, `summary` JSON-Dateien.
- [T01-Laufbindung](t01/run.json) und [unverändertes Testlog](t01/unittest.log).
- [measure.py](measure.py) und [t01.py](t01.py): tatsächlich verwendete Runner.
- [full-packages.json](full-packages.json): drei Vollpakete im unveränderten
  56er-Basisbestand; keine Retirement-/Kompaktierungsänderung.
- [manifest.json](manifest.json): Bytezahlen/SHA-256 aller Belege außer sich selbst.
  Lokale `.gitattributes` verhindert Git-Zeilenumbruchänderungen der Originale.

## Bindung nach der Testkorrektur

Der finale Head ändert gegenüber dem Messhead ausschließlich die Testdatei
`test_registration_publication.py`: v10 wird in der bestehenden Dispatch-Assertion
akzeptiert, unbekanntes v11 weiterhin abgewiesen. [measurement-reuse.json](measurement-reuse.json)
bindet beide Commits und die identischen Git-Bäume tools/content/game/docs/.ci.
Die originalen T02-Dateien behalten ehrlich ihren gemessenen Toolhead; kein neuer
Lauf wird behauptet. T01 (zwölf Fälle) und die vollständige CI laufen am finalen Head.
Der erste CI-Lauf hatte 355 erfolgreiche Tests und ausschließlich diese veraltete
Dispatch-Erwartung als Fehler; die finale CI prüft wieder alle 356 Katalogtests.

## T02-Aufbau und Messgrenzen

Windows 11 `10.0.26200`, Python 3.13.14, Pillow 12.3.0, festes Laufwerk E:,
NTFS (Get-Volume bestätigt). Derselbe lokale Datenträger, Interpreter und
Instrumentierungsrunner für beide Läufe. Python wurde als normales venv unter
der beauftragten Arbeitswurzel verwendet: Der Systemlauncher ist ein Reparsepunkt
und wird von der unveränderten Methodenbindung zu Recht nicht akzeptiert.

Je ein isolierter Checkout des obigen main-Stands mit 56 Einträgen und drei
vollständigen Obstpaketen (Birne r05, Erdbeere r06, Zitrone r05; target-export-v6).
Fliegenpilz r07 aus `e3b177673011c5477dd605c24420fef589e8f878` wurde nur in diesen
Testcheckouts bereitgestellt. ZIP und Freigabe sind in beiden `inputs.json`
identisch gebunden. Original-ZIP: 24.734.843 Bytes,
`0ca64ae2eee8c317d7ed1d34978180f26029cb91e3276bf7201a682b444057bd`.
Approval: `b360b8c5f3c686d8fc717887ca62a0ffbf69a89851a23698c70cab4033af426f`.

Vorher nutzt unveränderten main-Code, nachher den sauberen Messhead
`5070cb0e2b0893734d790a333653d09e22f698e7`; beide
`tool_diff_sha256` sind SHA-256 leerer Bytes. Export erzeugt frische Prüfinputs,
danach Plan und Register. Jede Messung startet in einem frischen Pythonprozess;
OS-Dateicache wird nicht geleert. Checkoutbereitstellung, Inventarlesen und
Export wärmen die Dateien, Plan wärmt Register zusätzlich. Vergleichbarer warmer
Arbeitsablauf, keine Kaltstartbehauptung, kein künstliches Cache-Tuning. Während
der Messungen liefen keine weiteren lokalen Tests. Einrichtung, Export und
abschließender gesonderter Gesamtaudit liegen außerhalb der Registerzeit.

Runner basierend auf dem [A-Original](https://github.com/venomenon328/picross/blob/1b2a3e195846b4ab5dace9931f8a1db61283cebb/review/pw-perf-a/repeat.py).
Observer rufen immer die originalen Validatoren auf: catalog_io.read/file_hash,
Pillow Image.open (Pfad/BytesIO), tx._stage_check und seine Path.write_bytes,
verify_export und Guards.full. Keine Validatorersetzung oder Grenzanhebung.
Native Operationslogs liefern Reads/Hashbytes, zwei Replays, zwei bytegebundene
Readbacks und fünf Grenzen; `observations` liefert Route/Journalhash, neue
Zielmenge und G0/G2/G5a/G5b/G6. Kein vollständiges Journal mit alten Paketbytes
wird als Nachweis benötigt.

Die `register-old`-Observer klassifizieren nur tatsächliche Altdateien im
Zielcheckout. `work-amounts.io.old-package` zählt zusätzlich alte Paketpfade in
Prüfkopien: vor Register 4.618 Reads / 2.074.932.197 Bytes, danach 0. Deshalb
weichen diese beiden Vorher-Zählperspektiven absichtlich voneinander ab.
Die übrigen `work-amounts.io`-Labels sind Pfadheuristiken: insbesondere wird
`baseline/tools` anders als `repo/tools` einsortiert. Für Gesamtbudgets gelten
ausschließlich die nativen catalog_io-Zahlen, nicht ein Labelvergleich.
Fehlende Countereinträge bedeuten null beobachtete Ereignisse, nicht ausgelassene
Instrumentierung. catalog_io erfasst keine beliebigen Betriebssystem-I/Os.

Native Phasen sind **inklusive** und dürfen nicht rekursiv addiert werden.
`comparison.disjoint_seconds` trennt Input/Plan ohne Publication, Publication
und äußeren Messoverhead. P0–P6 sind unmittelbare Kinder von Publication;
Guard-, Methoden- und Readbackzeiten sind darin enthalten. Vorher: 69,432 s
Planarbeit + 62,663 s Publication; nachher: 19,043 + 19,549 s. Die eigenständige
CLI-Planzeit ist eine andere Operation. Die Kopienmessung zählt vollständige
Stagingkopien auf Disk; die fehlende gleich große RAM-Rekonstruktion ist zusätzlich
am Produktdiff (begrenzte Indizes/neue Paketprojektion) zu prüfen, kein behaupteter
RAM-Profilerfolg.

`registration-diff` bindet die Inventare vor/nach und bestätigt: von 925 vorhandenen
Dateien blieben 923 unverändert, nur beide Registries änderten sich; sämtliche
neuen Dateien entsprechen den tatsächlichen Zielen. Alle 56 alten Entries,
Metadaten und Backgroundsourcewerte bleiben erhalten. Der zusätzliche explizite
Gesamtaudit besteht; er ist keine versteckte v10-Transaktionsvoraussetzung.
Keine Inhalts-/Paketdatei dieser Messcheckouts wurde auf den Produktbranch
übernommen. Keine echte Rätselveröffentlichung, keine Retirementmutation.

## T01/T03 und offene Abnahme

T01 läuft am unveränderten Produkthead; Originalprotokoll und Runner sind oben
verlinkt. Die fokussierten Fälle decken v10-Dispatch/Indexdelta, alte v9-Recovery,
No-op, Nullzugriffe/Kopien, neue Hintergrundbindung, Input-/Zielkonflikte,
P3/P4/P5 und wiederholt unterbrochene Recovery sowie frische Guardkonflikte ab.
Weitere historische Recovery und andere Writer werden durch das vollständig
gewählte Modul production.catalog geprüft.

[T03 CI-Lauf 43671948059, Versuch 1](https://github.com/venomenon328/picross/actions/runs/43671948059)
prüft genau production.catalog und production.adapter plus Kern und Windows-x64.
Die Resultreader prüfen ihre Originale im Lauf; evidence.mode bleibt none.
[CI-Zuordnung](ci.json) nennt Bindung und Job-/Downloadlinks; finaler Status und Modulzahlen stehen im Produkt-PR und in den originalen CI-Joblogs.
Windows wurde in Linux-CI gebaut und paketgeprüft, dort nicht interaktiv gestartet.

Die v10-Route bescheinigt die neue Produktion, gemeinsame gültige Indizes und
abhängige Quellen/Ziele. Sie bescheinigt keine Existenz/Hashes/Semantik fremder
Altdateien. Deren Defekte werden beim zuständigen Reader oder expliziten Audit
sichtbar. Das Implementierer-Selbstreview ersetzt **PW-PERF-B-A01 before_merge**
nicht. A01 bleibt offen; kein Merge, kein persönliches Spiel-/Bildgate.
