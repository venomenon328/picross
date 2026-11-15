# PW-PERF-E · befristete Revieworiginale

Produkt-Head: 0926debcecdb77c4c4525e6f0f61498216aff9e9.
Basis/Vorhercode: d50eeb71b9e017bfe82f3d58563b779d9df1c145.
Tatsächlicher Testmerge: 229dcd5a7cdec27e70a5207b88cad8496dda3841.
PR: https://github.com/venomenon328/picross/pull/659
Entscheidung: https://github.com/venomenon328/picross/issues/653#issuecomment-6894952911

Zweck: unabhängiges A01-Review von K01–K08/T01–T02. Nur synthetische Inhalte.
Verfügbarkeit bis A01, spätestens 2026-11-22; danach Bedarf neu prüfen und diesen
separaten Reviewref im beauftragten Rückbau entfernen. Kein Merge nach main.
Repositoryzugriff ist erforderlich. Keine Bildoriginale, Galerien oder privaten
Nutzerdaten erforderlich. Die Dateien liegen unverändert und ohne ZIP vor.

## Originale und Reproduktion

Die CI fand am Vorgängerhead zwei Regressionen. Der allgemeine Main-Guard
verdeckte die konkrete Hintergrunddiagnose; eingefrorene Methodenquellen
außerhalb des Katalogs wurden vom neuen Reader abgewiesen. Die vorhandene
sichere Leseprüfung gilt dort wieder ohne Retirementcache, und der konkrete
Hintergrundguard läuft zuerst. Beide vorhandenen Tests bestehen lokal
(217,915 s; ci-regressions.log), ohne Änderung ihrer Anforderungen.
T01, Präferenzmatrix, Zähler und Nachhermessung wurden auf diesem Head erneuert.

`t01-final.log` ist die erfolgreiche Windowsausgabe der acht dauerhaften T01-Tests
und der einmaligen standard/none-Matrix. `current-cases.json` nennt deren tatsächliche
Paket-/Registry-/Authoringdeltas und bestätigt identische Livebytes/mtimes sowie No-op.
`operation-counters.json` enthält die beiden erwarteten negativen Quellenfälle und
den erfolgreichen v6-Import: jeweils eine begründete ZIP-Metadatenöffnung, kein
Solver-/Produktionsreplay und keine Bilddekodierung.

T02 verwendet auf beiden Codeständen denselben kleinen gültigen historischen
Exportfall aus IntegratedContentTests.prepare(), unveränderte ursprüngliche
Paketmenge: 30 Dateien / 31.504 Bytes. Kein v6-Erfolgswert wird rückwirkend erfunden.
Windows 11 / Python 3.13.14 / Pillow 12.3.0, ein erster und ein begrenzter warmer
Aufruf, kein Cacheflush. Fixtureaufbau liegt außerhalb der Messung. Git-Commits und die bei Fixture-Registrierung erzeugten Added-Records enthalten
unterschiedliche Zeitstempel. Verglichen werden dieselbe Fixturedefinition,
dieselben Dateimengen und derselbe ursprüngliche Paketbyteumfang; es wird keine
vollständige Byteidentität dieser unabhängig erzeugten Zeitstempelfelder behauptet.
Vorher/Nachher instrumentieren dieselben tatsächlichen catalog_io-Bytezugriffe und
SHA-256-Hasharbeiten: vor Änderung io.read/checksum, danach deren physische
_read/_checksum-Grenze unter dem aufrufgebundenen Reader. Pure Hashes außerhalb
catalog_io und Gitinterne Objektzugriffe sind keine dieser Zählmetriken.
`comparison.json` ordnet die vollständigen Pfadwerte disjunkten Quellgruppen zu.
Der Originalhash und neue Receipthash sind getrennt; Readback der neu geschriebenen
Dateien gehört zum gemessenen I/O. Die Lesegrenze bestätigt keinen fremden Bestand.

Die vier Originalmessungen enthalten vollständige Pfadwerte, Umgebung und Resultat.
Warm: 420 → 49 Reads, 432.165 → 45.071 Readbytes, 331 → 35 SHA-256-Aufrufe,
350.594 → 34.692 Hashbytes, 3,489 → 2,552 Sekunden. Auch der erste Aufruf ist schneller
(3,533 → 2,775 s). Die endgültige Nachhermessung wurde nach der Korrektur der
Methodenreader und Hintergrunddiagnostik erneuert; keine Optimierung durch Auswahl eines günstigeren Wiederholungswerts.

Die unveränderten Auftragsskripte sind beigefügt. Sie erwarten ihren eigenen
Arbeitsordner mit `repo/` auf dem jeweils genannten Stand und importierbaren
Tests; TEMP/TMP zeigen auf dessen eigene temporäre Ablage. `measure.py` wird auf
der Basis ausgeführt, `measure_after.py`, `validate_current.py` und
`operation_counters.py` auf dem Produkt-Head. Python aus einer isolierten Umgebung
mit Pillow exakt 12.3.0 starten. Diese Skripte gehören nicht zum Produkt oder
zur regulären Testdiscovery. Der Produktionsdiff enthält keine Reviewdateien.

Die aktiven Quellen werden vollständig geprüft, bestehende technische Export-
Originale innerhalb eines Aufrufs nur einmal gelesen. Der Reader begrenzt seine
flüchtigen ausgewählten Eingangsbytes auf 512 MiB; größere Auswahlen sperren vor
Mutation und können in getrennten autorisierten Aufrufen bearbeitet werden.
Dateiidentitätsguards einschließlich tatsächlicher Windows-ChangeTime sind keine
Garantie gegen nichtkooperierendes OS-/ABA-Racing. Der gemeinsame Marker schützt
kooperierende Katalogwriter. Teilfehler erhalten Marker und tatsächlichen Diff;
es gibt keinen automatischen Rollback aus bereits entfernten Originalen.

Die CI-Originale stehen im aktuellen Package-CI-Lauf 43725097262; hier werden sie
nicht als zweite Logsammlung kopiert. Alle für T01/T02 benötigten lokalen Originale
sind mit Bytezahl und SHA-256 in `manifest.json` gebunden. A01 bleibt unabhängig offen.
