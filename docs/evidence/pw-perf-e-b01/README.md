# PW-PERF-E-B01 · technische Nacharbeit

Nur B01 aus [Review 5911494549](https://github.com/venomenon328/picross/pull/659#pullrequestreview-5911494549), zu [Paketentscheidung PW-PERF-E](https://github.com/venomenon328/picross/issues/653#issuecomment-6894952911).
Produkthead `f10ef329e6a98e1bb9e50c9c409998f2b518340f`, Basis `d50eeb71b9e017bfe82f3d58563b779d9df1c145`, CI-Testmerge `4f0f66f40bf55ddeb79e65e8e003749d3ebe34af`.
Empfänger: unabhängiger A01-Reviewer. Zweck: B01-Erfolgskriterien und aktuellen Produktstand prüfen. Ende: nach erforderlicher Abnahme, spätestens 2026-11-22; bei weiter offenem Gate Bedarf neu prüfen. Eigener Ref `review/653-pw-perf-e-b01-until-20261122`, kein Merge-PR. Lokale Kopien werden nach gesicherter Zustellung entfernt; den Remote-Belegref erst im passenden Rückbau entfernen. Zugriff erfordert Repositoryberechtigung.

## Originale und Reproduktion

- `b01-before.log`: gezielte Negativprobe vor der Codekorrektur. Der neue Test war bereits vorhanden, der Retirementcode entsprach e9b8f233. Der Root-Tree passiert Paket-/Record-/Rechteprüfungen bis zur absichtlich abgefangenen Locknahme: `unexpected lock`. Erwarteter Testfehlschlag, kein tatsächlich angelegter Lock und kein behaupteter abgeschlossener Retirementlauf.
- `b01-after.log`: dieselbe Testdatei nach der Korrektur, alle acht Fälle erfolgreich. Der B01-Fall weist denselben Paketbaum und registered-Record nach, fängt Lock-/Lösch-/atomare Schreibversuche ab und vergleicht alle Dateibytes/mtimes sowie Gitstatus nach Ablehnung. Danach erfolgreicher v4-Abschluss mit dem echten Quellcommit aus einer getrennten Historie; Herkunft/Rechte, Main-/Importbezüge und Livebytes bleiben geprüft.
- `core-tests.log`: 21 schlanke Plan-/Ergebnisregressionen erfolgreich.
- `docs.log`: tatsächlicher Dokumentcheck samt ausgewiesenen Prüfgrenzen.
- `b01-test.patch`: nur die Teständerung zum vorherigen Produkthead, für die Vorherreproduktion.
- `b01-fix.diff`: vollständiger Nacharbeitsdiff e9b8f233 → f10ef329, fünf Dateien, darunter genau zwei zusätzliche Produktcodezeilen.
- `source-and-results.json`: exakte Quellen, Kommandos, Umgebung, Zeiten und Quellbytebindungen.
- `sd2-followup.log` und `ci-attempt-1.json`: der einzelne SD2-CLI-Ausreißer in Versuch 1 und drei erfolgreiche lokale Folgeproben (201,981 s), einschließlich des vorherigen Cleanupfalls. Kein nachgewiesener aktueller Traceback; Heartbeat/stdout-Kollision ist nur eine bekannte mögliche Ursache.
- `ci-attempt-2.json`: vollständiger Ergebnisrecord aus dem [aktuellen Katalog-Joblog](https://github.com/venomenon328/picross/actions/runs/43731528915/job/132872340398), als JSON formatiert; kein Originaldownload der temporären production-result.json. Accepted/tests_accepted/source_unchanged=true, exakte Head-/Testmerge-/Versuchsbindung.

Windows/NTFS, Python 3.13, isoliertes Pillow 12.3.0. Tempdateien lagen unter der beauftragten Codex-Arbeitswurzel. Für die Vorherprobe auf einem isolierten e9b8f233-Checkout nur `b01-test.patch` anwenden und den in `source-and-results.json` genannten Einzeltest ausführen; die Lockfalle verhindert echte Inhaltsmutation. Für den Nachherlauf den unveränderten Produkthead und die dort genannte gesamte Testdatei verwenden. Keine echten Katalogdaten oder Nutzersaves verwenden.

## CI und wiederverwendete Belege

[Package CI 43731528915 / Versuch 2](https://github.com/venomenon328/picross/actions/runs/43731528915/attempts/2) ist vollständig erfolgreich: docs, Windows-x64-Paket, production.catalog, production.adapter und ci-required. Der aktuelle Katalogjob bestätigt accepted/tests_accepted/source_unchanged=true am oben genannten Testmerge. GitHubzeit des zweiten Versuchs 1094 s (run_started_at bis updated_at), Katalogproducer 1063,181 s. Der [erste Versuch](https://github.com/venomenon328/picross/actions/runs/43731528915/attempts/1) scheiterte ausschließlich im bereits früher auffälligen SD2-CLI-Test, während sämtliche acht Retirementtests bestanden. Der unveränderte Produkthead wurde mit den fehlgeschlagenen Jobs wiederholt; es gab keine Korrektur außerhalb B01. Erfolgreicher Retry und lokale Folgeprobe sind kein Beweis der konkreten Fehlerursache des ersten Versuchs. Kein unabhängiges Review und kein ausgeführter Windowsstart.

Die [17 bisherigen T01/T02-Originale](https://github.com/venomenon328/picross/blob/2dec5c084702422aceeb18fb72636c3e2afe1a48/docs/evidence/pw-perf-e/manifest.json) bleiben separat für die unveränderten Arbeitsmengen-/Lifecycleaussagen erreichbar, mit ihrem damaligen Codehead und Ablauf 2026-11-22. Sie wurden im ursprünglichen Review unabhängig geprüft. B01 ergänzt ausschließlich die direkte Typprüfung ausdrücklich übergebener Quell-SHAs vor Capture/Lock; der damalige Standard-T02-Pfad ohne `source_commits` ändert sich nicht. Die damaligen Messwerte werden nicht als neue Messung von f10ef329 ausgegeben und belegen keine heutige End-to-End-Dauer.

## Abgleich und offene Zuständigkeit

B01 / K01: Commitobjektart normativ im ZA-1-v4-Vertrag und in der CLI beschrieben, keine neue Formatgeneration. K04: Treeish-Erfolg ist kein Quellcommitbeweis; echter separater Quellcommit bleibt zulässig. K05: alle ausdrücklich angegebenen Quell-SHAs werden im gemeinsamen Preflight vor Capture und Writersperre geprüft. Der Receiptreader bleibt ein geschlossener lesender Validator; er öffnet keine entfernten historischen Git-/ZIP-Originale neu. Der v4-Producer ist intern nur über diesen geprüften Aufruf erreichbar.

Technische Nacharbeit durch Implementierer geliefert. A01 bleibt before_merge beim unabhängigen Reviewer; historische Reviewurteile bleiben unverändert. Keine persönlichen Abnahmen erklärt, keine echte Rätselbereinigung, kein Merge.
