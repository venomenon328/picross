# CI2-F-T01 · Katalogkosten ohne Verlust der Prüfdeckung

27.10.2026 · [#424](https://github.com/venomenon328/picross/issues/424).
Basis: `main@53f9c1f6d87d752e6b0f3152985fd0a83de2278b`, integriertes CI2-E / PR #423
nach finalem separatem E-R01. Branch `chore/424-ci2-f-catalog-perf`, Ziel `main`.
Der zu #424 gehörende Draft-PR bindet den tatsächlichen finalen Head, Basis,
Test-Merge, Run/Versuch, Originalartefakte, Messwerte und das getrennte Selbstreview.
T01 ist erst mit den dort zugeordneten erfolgreichen Pflichtresultaten erfüllt.
Separates qualifiziertes CI2-F-R01 bleibt vor Merge erforderlich.

## Messung vor Eingriff

Die gebundene Linux-CI-Ausgangsmessung aus #424 ist Run `40486884116`, Versuch 2,
Head `c29e188a88d21a3c371eaf8adc5add5f03446a26`, Test-Merge
`c0d9f27965f539330533e942c477fed111468683`; der vollständige Fachbericht stammt
aus Originalartefakt `12728985641` aus Versuch 1 desselben Runs. Ubuntu 24.04,
Python 3.12.3/Pillow 12.3.0: 120 Katalogtests einschließlich Fixtures in
**833,015 s**, gesamte Fachsuite 366 Tests / **1.188,179 s**, gesamter Harness
mit Referenzen und ZA-1 **1.363,397 s**. Solver 24,650 s, Images 128,089 s,
Adapter 202,307 s. Diese CI-Baseline wird weder neu gestartet noch umgeschrieben.

Die zusätzliche lokale Diagnose verwendet die unveränderten Fachquellen der
obigen Main-Basis in einem isolierten Ubuntu-24.04-Container, Python 3.12.3 und
Pillow 12.3.0. Ein vor der Optimierung abgebrochenes cProfile-Diagnosepräfix
(kein erfolgreicher Suitebeleg) misst 66,900 s, davon 58,108 s in 53.956
`catalog_io.safe`-Aufrufen. `Path.iterdir` und die Konstruktion unbenutzter
Geschwisterpfade sind ein gemessener Kostenanteil; die bloße Zahl früherer
Checkout-/Exportprüfungen war dafür kein Ursachenbeweis.

Der vollständige zusätzliche Vorherlauf und der Nachherlauf verwenden denselben
Container seriell, frische Pythonprozesse und isolierte temporäre Daten. Keine
Testparallelisierung oder neue Jobmatrix. Containerzeiten sind ein lokaler
Vergleich; das Ziel **höchstens 400 s** verlangt den gebundenen Linux-PR-Run.
Die tatsächlichen Zeiten, Aufruftypen, langsamsten zehn Tests, Fixturekosten und
Vergleichsgrenzen stehen in der abschließenden T01-Zuordnung im PR.

| Lokaler serieller Kataloglauf | Tests | Fixtures (s) | Gesamt (s) |
| --- | ---: | ---: | ---: |
| Unveränderte Fachquellen der Main-Basis | 120/120 | 95,955 | 823,510 |
| Geteilte Voraussetzungen und reine Namensenumeration | 120/120 | 59,153 | 577,149 |
| Zusätzlich Komponentenprüfung mit Pfadstrings | 120/120 | 42,660 | 427,030 |
| Zusätzlich direkte Präsenzprüfung durch Enumeration und kompakte Metadatenvoraussetzungen | 120/120 | 38,207 | 384,478 |

Die ersten beiden Zwischenstände verfehlen das 400-s-Ziel. Ein supersedierter
zusätzlicher Pfadsyntax-Versuch wurde lokal unterbrochen und zählt nicht als Pass.
Nach dem letzten Vollstand wurde ausschließlich die identische vollständige
Revisions-7-Retirementvoraussetzung konsolidiert; ihre fünf Fälle plus die
erweiterte Isolation bestehen gezielt in 28,896 s. Der vollständige Nachweis des
tatsächlichen finalen Heads kommt aus der PR-CI, kein weiterer ritueller lokaler
Vollauf. Der synthetische Pfadmikrovergleich (2.000 Aufrufe derselben Datei bei
128 Geschwistern) misst 0,979 → 0,348 s; er ersetzt keinen Katalogtest.

Gemessene Ursachentrennung am lokalen Vorher-/letzten Vollstand: sichere
Pfadprüfung 1.306.557 / 665,644 s → 1.127.017 / 250,587 s; Dateilesen
522.013 / 439,467 s → 461.882 / 171,995 s; Quellensnapshot 598 / 95,051 s →
595 / 35,782 s; Guards 5.856 / 513,491 s → 5.616 / 222,742 s; Recovery
85 / 88,300 s → 85 / 39,240 s; Kopien 258 / 3,669 s → 253 / 3,151 s;
Export 42 / 2,102 s → 39 / 1,796 s; Exportprüfung 288 / 5,056 s →
271 / 4,339 s; Registrierung 84 / 309,698 s → 81 / 144,584 s;
Checkoutprüfung 1.573 / 81,957 s → 1.569 / 38,800 s. Zeiten sind inklusive
Unteraufrufen und dürfen nicht summiert werden. Im lokalen Vorherzähler wurde
die früh gebundene Importaliasfunktion nicht beobachtet, keine Nullarbeit
behauptet; die abschließende Messung erfasst auch diese Aliasbindung. Die
historische vollständige CI-Baseline enthält ihre ursprünglichen fünf Zählertypen.

Gezielte aktuelle Gegenproben: alle sieben ausgewählten Isolations-, Hidden-,
Quellen-/Recovery-, Full-Export-/Retirement- und SD2-No-op-Fälle in Vorwärtsfolge
7/7 erfolgreich (29,877 s), in umgekehrter Folge ebenfalls 7/7 (29,475 s),
jeweils frischer Linuxprozess. Windows 11/Python 3.13.14/Pillow 12.3.0:
Isolation aller drei Voraussetzungen, Root-/Schreibweisen-/Junctionschutz und
Retirement-Lifecycle 3/3 erfolgreich, 124,689 s. Die POSIX-chmod-Probe stammt
aus den vollständigen Linuxläufen, nicht aus einer behaupteten Windowsprüfung.
Der schnelle Werkzeuglauf besteht 232 Tests in 50,207 s mit drei vorhandenen
plattformbedingten Windows-Skips. Dokumentvalidator und vollständiger
Whitespacecheck sind erfolgreich; die finale Linux-CI führt ihre tatsächlich
ausgewählten Pflichten ohne Übernahme dieser lokalen Skips aus.

## Gezielte Änderungen und erhaltene Aussagen

| Änderung | Semantische Grenze und Gegenprobe |
| --- | --- |
| Sichere Pfadprüfung | `catalog_io.safe` liest dieselben Namen mit `os.listdir` und durchläuft die Komponenten als Pfadstrings mit frischen lstat-Aufrufen. Der Rückgabewert bleibt ein `Path`. Unbenutzte Geschwisterobjekte und wiederholte Path-Konstruktion entfallen. Die tatsächliche Verzeichnisenumeration deckt zugleich die frühere redundante Existenzvorabfrage ab; jede Komponente wird weiterhin per lstat auf Typ/Link/Hardlink/Reparse geprüft. casefold-/Schreibweisen-, Root- und Budgetprüfung bleiben aktiv; andere Enumerationsfehler als Abwesenheit blockieren. Keine gecachten Dateisystem-, Hash-, Namensraum- oder Prüfergebnisse. |
| Identische Registrierungsgrundstände | `catalog_fixtures.registered` erzeugt pro identischem Stem/Slot/Runtime-Revision einmal einen echten Export, extern geprüften Ratinginput, echte Registrierung und gültigen kompakten Beleg. Es speichert ausschließlich unveränderliche Eingabebytes, Moduswerte und den bereits bisher geteilten Checked-Arbeitsinput. Jede Klasse erhält eigene Dateien und ein neues Eingabeobjekt. Der Builder wird innerhalb desselben gemessenen Aufbau-/Testaufrufs entfernt; keine ungemessene spätere Dateibereinigung. |
| Metadaten-/Recoveryvoraussetzungen | Added- und SD-Metadatenfälle sowie die geeigneten Bildfälle beginnen mit gültigen kompakten Integrationsbelegen. Definition, Bild, Notice und Rating bleiben dieselben synthetischen Inputs. Jede geprüfte Änderung, Adoption, Quellenprüfung, Recovery und No-op läuft weiterhin wirklich. |
| Gemischte SD2-Updates und Mehr-ID-Bericht | Der SD2-Updatefall beginnt mit gültigem kompaktem Altbestand; alle neuen Exporte, echten Updates, Stagingprüfungen und Rollbacks bleiben. Vollständiger Altpaketerhalt bleibt in den zuständigen Updatefällen geprüft. Der Mehr-ID-Metadatenfall integriert seinen zweiten Export weiterhin wirklich und verwendet danach dessen gültigen kompakten Beleg für Bericht/Adoption. |
| Vollständige Produktionsgrenzen | Neue Registrierungen und Rasterupdates behalten echte Exporte und unabhängige Stagingprüfung. Die vollständigen Bild-/Cleanup-/Rebind-/Paketquellenfälle bekommen die vollständige Basis. Alle vier E-Revisionsabschlusstests starten weiterhin vollständig und durchlaufen ihre ursprünglichen tatsächlichen Übergänge einschließlich POSIX-chmod-Gegenprobe. |
| Retirementgrundstand | Die fünf vorhandenen Retirementfälle kopieren denselben einmal tatsächlich registrierten vollständigen Revisions-7-Grundstand. Jeder erzeugt weiterhin seinen eigenen Gitverlauf, Main-Beleg und Stagingkontext und führt die echte Retirement-/Fremddatenprüfung aus. Der Lifecyclefall integriert sein zusätzliches Farbrätsel weiterhin wirklich. |
| Isolation | Der bestehende Isolationstest prüft alle drei geteilten Voraussetzungen in beiden Richtungen, exportierte und kompakte Bytes, unabhängige Checked-Objekte und jeweils eine dritte unveränderte Kopie. Eine nach vorheriger erfolgreicher Prüfung veränderte Receiptdatei wird erneut abgewiesen. |
| Pfadrennen zwischen Aufrufen | Der vorhandene Root-/Linktest prüft zusätzlich falsche Schreibweise, auf POSIX eine neu hinzugefügte casefold-Kollision, deren Entfernung und tatsächlich geänderte Dateibytes nach erfolgreichem Lesen. Die bestehenden Link-/Hardlink-/Junction- und fremden Quellenfälle bleiben. |

Alle **120 Katalog-Testidentitäten** aus `production_contract.py` bleiben erhalten,
einschließlich aller Positiv-/Negativvarianten, echten Unterprozesse und
Recoverygrenzen. Keine geänderte Rastergröße, reduzierte Fallmenge, gestrichene
fachlich geprüfte Transaktion oder Zusammenfassung zum Megatest. Relevante Full-Export-, Notice-,
Rechte-, Fremdslot-, Quellen-, Journal-, Rollback-, Staging- und No-op-Aussagen
bleiben an ihren tatsächlichen Einstiegen gebunden. Der Importaudit kontrolliert
die unveränderte Fachzuordnung der betroffenen Dateien.

## Messbericht und technische Prüfung

Der bestehende Fachbericht misst weiterhin jeden Test einschließlich setUp,
tearDown und Cleanups sowie Klassen-/Modul-Fixtures in der Gruppensumme.
`operations` ergänzt Aufrufzahl, inklusive Dauer und Eigenzeit ohne andere
gemessene Unteraufrufe; geschachtelte inklusive Zeiten sind nicht addierbar.
Aliasbindungen werden ebenfalls beobachtet. Rekursive copytree-Aufrufe zählen
als eine äußere Isolationskopie. Fehler bleiben Fehler und gehen mit ihrer
tatsächlichen Dauer ein. Der schnelle Werkzeugtest kontrolliert Rückgabewert,
Fehlerweitergabe und geschachtelte Zeitabrechnung. Die Messung speichert keine
Operationsergebnisse und verändert weder Aufrufargumente noch Resultate.

Der vollständige Base→Head-Diff wählt die bestehenden Pflichtjobs. Aktuelles
`docs`, alle ausgewählten Fach-/nativen-/Preflight-/Deliverypflichten und
`ci-required` müssen tatsächlich erfolgreich sein. Originalberichte nennen
Testanzahl und genaue Identitäten, Quellen-/Run-/Versuchsbindung, Gruppen,
Integrationen und Dateien; deren unabhängiger Ergebnisprüfer bleibt unverändert.
Queue, Setup, eigentliche Testzeit, Job-/Workflowdauer und Runner-/Cachezustand
werden im PR auseinandergehalten. Reihenfolgegegenproben verwenden eigene
Prozesse und Roots und sind als zusätzliche lokale Proben ausgewiesen.

Produktkatalog, Gameplay, Runtime-/Saveformate, Produktions-/Bewertungsmethoden
und beide Freezes, native History-/Grafikprüfung, Browsergruppen, Selektor,
Scheduler und Ergebnisgate bleiben unverändert. Nur die wirkungsgleiche
Katalog-Verzeichnisenumeration ändert produktiven Pythoncode. Die vier verlangten
CI-Einstiege schreiben den tatsächlichen E-Merge fort; historische E-/B-/AT-/HZ-
Berichte bleiben an ihren damaligen Commits gebunden. Keine Bestandslöschung.

Chromium bleibt **not requested**. Auch ein erreichtes Katalogziel belegt das
allgemeine Fachharnessziel unter zehn Minuten nicht; **CI2-B-/E-O01 und
CI2-D-O01 bleiben offen**. Getrennter vollständiger Selbstreview und unabhängiges
qualifiziertes R01 sind verschiedene Prüfungen. Kein Merge, Deployment oder Release.
