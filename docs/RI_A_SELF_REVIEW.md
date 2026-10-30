# RI-A: getrenntes Selbstreview der Nacharbeit

30.10.2026 · [#478](https://github.com/venomenon328/picross/issues/478) ·
[Draft-PR #484](https://github.com/venomenon328/picross/pull/484).
Ausgangshead `29349ffbfa9fd42d4e20e7065d2d0c4f9b721211`,
Werkzeug-/Teststand `bca790bf4a8a0e5f32e746cc0d2e0723e3f878c8`.
Dies ist eine getrennte Prüfung durch den implementierenden Autor, kein
unabhängiges qualifiziertes Review und keine Mergefreigabe.

## Auftrag, Quellen und Diff

Die aktuelle AGENTS.md, Workflow, Projektprofil und auftragsbezogenen
Integrations-, Adapter-, Katalog-, Produktions- und CI-Quellen wurden vor
Änderungen gelesen. Verbindlicher Befundstand:
[RI-A-R01](https://github.com/venomenon328/picross/pull/484#pullrequestreview-5709431225)
und [RI-A-N01](https://github.com/venomenon328/picross/pull/484#issuecomment-6517789353).
Geprüft wurden sowohl der vollständige PR-Diff gegen
`main@8f903d7ecb6c111451ae359ecca44156987daa19` als auch die Nacharbeit seit
`29349ffb`. Die damalige positive Selbstbewertung der Diagnostik ist durch R01
widerlegt; der [alte Bericht](https://github.com/venomenon328/picross/blob/29349ffbfa9fd42d4e20e7065d2d0c4f9b721211/docs/RI_A_SELF_REVIEW.md)
bleibt ausschließlich historische Quelle.

## Einzelbefunde und Gegenprüfung

| Befund | Änderung und kontrolliertes Orakel |
| --- | --- |
| B-01 | Unklassifiziert höchstens 300 s oder kürzerer Override. Ticks bei 100/299/301 s innerhalb des JSON-Lesens stoppen vor weiterer Arbeit; Checkoutbytes und mtimes bleiben gleich. Nach sicherer Zuordnung gelten 1800/600/10 s vom ursprünglichen Start, einschließlich bereits verbrauchter Klassifikationszeit. Kürzere äußere Katalog- und Operationsframes sowie bereits abgelaufene Fristen bleiben wirksam. Klassifikator, geschlossene Schemas, Staginghash und vollständige folgende Quellenprüfung sind unverändert. |
| B-02 | Beobachtungsbeginn vor P0–P6/R0–R2, unabhängig von unveränderten Fehler-Checkpoints. Ungleiche kontrollierte Arbeitsdauern prüfen sämtliche Phasen einschließlich erster und weiterer P3/P4/R1-Dateien. Eltern-/Unterphasen bleiben inklusive. P0-Abbruch meldet 1801 s Teilzeit, keine P1-Arbeit; automatische Recovery wird nicht der pausierten P3 zugeschlagen. Checkpoints heißen im Fortschritt ausdrücklich Checkpoints. |
| B-03 | Eigene Versuchs- und erfolgreiche Vollprüfungszähler für Kandidat, Input und Export. Positivfall sowie ungültige Proofbytes, I/O-Fehler und tatsächlicher Deadline-Tick innerhalb der Verifikation erhalten begonnene Arbeit, zählen aber keinen falschen Abschluss. Eine erfolgreiche und eine abgebrochene Kandidatenprüfung meldeten vorher zwei vollständige Prüfungen; jetzt zwei Versuche und eine vollständige Prüfung. Innere Einzelproofs bleiben davon getrennt. |

Alle 22 RI-A-Fälle bestehen auf Linux und Windows, einschließlich der alten
No-op-, Fremdbyte-, unabhängigen Recovery- und dauerhaften Abschlussfälle.
Drei ausgewählte neue Regressionen wurden zusätzlich am alten Head ausgeführt
und scheitern dort. Exakte Zuordnung, Laufzeiten und Messbindung stehen in
[RI-A-T01](RI_A_VERIFICATION.md).

## Erhaltene Verträge und Prüfgrenzen

Separater AST-Vergleich gegen `29349ffb`: Guards, Read-/Write-Helfer,
Klassifikator und Journalvalidator sind unverändert. Nach Herausfiltern allein
der neuen Beobachtungsaufrufe sind auch moderne und historische
Publikations-/Recoverykörper identisch; insbesondere bleiben Checkpoints,
Guards, Mutationsreihenfolge und Lock-/Flushabschluss an denselben Stellen.
`catalog_io.py` und Methodenvertragsdateien sind bytegleich; keine weitere
I/O-Ausdünnung. Fachformate und echte Katalog-/Rätselbytes bleiben unverändert.

CLI/API und Recoveryvertrag erklären die konservative Erstfrist und getrennte
Zählersemantik. Der Authoringtext bleibt in dieser Nacharbeit unverändert;
sein bereits im PR enthaltener Offline-Snapshot wurde erneut exakt verglichen.
Keine neue dauerhafte Datei, kein Benchmarkjob, kein Produktionsinput.
Der bestehende manuelle Messtreiber ergänzt ausschließlich die optionale
Beobachtung für den erneuten, quellgebundenen Vergleich. Alte Laufzeiten werden
nicht als Messungen des neuen Codes übernommen.

232 Werkzeugtests bestehen lokal mit drei bestehenden Plattform-Skips;
Dokumentvalidator und vollständiger Whitespacecheck bestehen. Der vollständige
Diff wählt alle vier Fachgruppen, alle sieben nativen Gruppen, Docs, Preflight
und Delivery. Chromium bleibt ohne Auftrag unangefordert. Aktuelle Pflicht-CI
und `ci-required` müssen den endgültigen Head und zugehörigen Test-Merge binden;
die konkrete Run-/Head-/Base-/Merge-Zuordnung steht im PR, kein Ersatz durch
lokale oder alte grüne Ergebnisse.

## Offene Abnahme

B-01/B-02/B-03 sind aus Autorensicht durch Umsetzung und Regressionen erledigt.
Erforderlich bleibt das erneute unabhängige qualifizierte Review auf dem neuen
Head. O-01 bleibt außerhalb dieses Auftrags; native CI wurde weder verkürzt
noch als neue Ausnahme behandelt. Keine RI-B-/RI-C-Arbeit, echte Integration,
zusätzliche Produktänderung oder Merge. Der PR bleibt Draft.
