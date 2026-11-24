# Remote-Ausführung für Rasterangebote und Erstintegration

PW-REMOTE-A verwendet den [portablen Arbeitsplatz](PRODUCTION_GIT_WORKSPACE.md),
den [Publisher](PW_B_CONTRACT.md) und genau einen auf Main gebundenen
[Actions-Worker](../../.github/workflows/pw-remote.yml). Der Produktionsakteur
übersetzt den kurzen Auftrag und die tatsächlichen Wahlen in den geschlossenen
Aufruf. Das Ergebnis nennt den gesicherten Arbeitsstand und den nächsten Schritt.

## Aufruf und Bindungen

Der Akteur liest den veröffentlichten Record an der erwarteten Arbeits-SHA.
Er prüft dessen Originalreferenzen, Wahlen, verbrauchte Budgets und den Auftrag.
Der gesamte Record einschließlich Releasegeneration, Asset-IDs, Entscheidungen,
Bytezahlen und Originalhashes ist durch `record_sha256` an die unveränderten
Git-Blob-Nutzbytes gebunden. Der Worker liest diese Bytes vor dem Bootstrap erneut.

Der Akteur übergibt UTF-8-JSON auf stdin an die [CLI](../../tools/production_remote.py).
Mit `submit --auth gh` erstellt sie einen Requestref. Der Connector kann dieselbe
Operation mit Git Data ausführen. Dazu `mode=preflight|execute` und den
vollständigen Request in das Objekt `{"mode": mode, "request": request}` setzen.
`tools.production_remote.envelope` liefert den genauen Branchnamen und die
kanonische Commitnachricht. Vor jedem Upload die Daten auf Scope, Geheimnisse
und Größe prüfen. Über `create_commit` genau einen Commit mit dem frisch
gelesenen Main als einzigem Parent und **identischem Baum** erzeugen. Den
Commit unabhängig lesen, vollständige Nachricht, Parent und Baum vergleichen.
Den freien Ref `work-prod-control/remote/<job>/<Digest des Objekts>` auf genau
diese SHA mit `create_branch` bedingt anlegen und zurücklesen. Eine identische
Wiederholung prüft einen vorhandenen Auftrag. Es wird keine Workflowdatei aus
einem Rätselbranch verwendet.

Der Push löst den vorhandenen Working ref publication check aus. Dessen
erfolgreiches Ereignis startet den Worker auf Main. Dieser prüft Repository,
Triggerpfad, unveränderten Baum, Parent, Nachricht, Digest und tatsächliche
Refs. Der Aufrufer liest beide Run-IDs und den Ergebnistext. Der Worker
entfernt ausschließlich den eigenen bestätigten Requestref mit erwarteter SHA.
Ein fehlgeschlagener Lauf lässt ihn für den erneuten Aufruf erreichbar.
Ein eigener autorisierter Rechner kann denselben Kern aus sauberem Main mit
`python -B -m tools.production_remote execute --auth gh --root PRIVAT` ausführen.
Die Wurzel ist ein vorhandenes privates Verzeichnis für diesen Akteur.

Jeder Request hat genau die Felder `format=pw-remote-v1`,
`repository=venomenon328/picross`, `operation`, `job`, `expected` (volle
Arbeitscommit-SHA), `record_sha256`, `tools`, `main` und `input` sowie die
unten angegebenen Zusatzfelder. `tools` und `main` bezeichnen den beim Start
frisch zurückgelesenen Maincommit. Jede Folgeoperation bindet ihre tatsächlichen
Eingänge erneut.

| Operation | Zusatzfelder | Inhalt von `input` und Ergebnis |
| --- | --- | --- |
| `step3` | – | `motif_sha256`, vollständiges bestehendes Bilddesign unter `design` mit einem benannten Kandidaten, dazu `profile=line\|paired` und `label`. Die gewählte Motivdatei durchläuft Bild-/Rasterhelfer, Proof und unabhängigen Verifier. Der Builder ergänzt Kandidat und Zähler, der Publisher sichert die Ergebnisse zur Sichtung. |
| `step5` | `issue` (bestehendes Produktionsissue) | `background` enthält die tatsächlich gewählte ID, `none`, `standard` oder JSON-null zur Wiederverwendung. `decisions` enthält nur tatsächlich erklärte, noch benötigte PW-B-Entscheidungen für background/final/integration mit Scope, Inhaltsbindung, Akteur, UTC-Zeit und Erklärung. Bereits abgenommener Record: `{"background":null,"decisions":[]}`. |
| `status` | `product` (Commit), `pr` (Nummer) | Leeres Objekt. Aktueller Produkt-PR und tatsächlicher PR-Lauf mit Head, Basis, Testmerge, Run, Attempt und Checkzuständen. Fehlende, ausstehende oder genehmigungspflichtige Läufe verlangen einen späteren Statusabruf. |
| `retire` | `product`, `pr` | Leeres Objekt. Separater Prozess mit der nach Completion veröffentlichten Arbeits-SHA und dem aktuellen Main. Er prüft den gemergten zugeordneten PR, die Integration seines Mergecommits und die gelieferte Generation vor dem Retirement. |

Für Schritt 5 laufen Finalizer, Vorbereitung/Export, lesender Plan, frische
Registrierung und Prüfung des vollständigen gestagten Produktdiffs in dieser
Reihenfolge. Der Produktcommit enthält die ausgewählte Lieferung und ihren
buildfreien Paketplan. Completion vergleicht genau diesen Commit und denselben
Eingang. Der Publisher überträgt den abgeschlossenen Arbeitsrecord und
`content/integrate-<job>` in einem atomaren Push mit zwei erwarteten Refwerten.
Erst nach dem Readback wird der zugehörige Draft-PR angelegt oder wiedergefunden.
Ein belegter fremder Branch/PR blockiert. Die PR-Checks stammen aus dem
tatsächlichen PR-Ereignis und seinem getesteten Mergecommit. Eine Mergeentscheidung
verbleibt beim Akteur gemäß [Authoring §8](../production/authoring/PUZZLE_AUTHORING_STEP_5.md).

## Aufrufzugang und Betrieb

Für die bedingte Neuanlage benötigt der Aufrufer Contents-Schreibzugriff auf das konkrete Repository. Der Worker verwendet Contents und Pull requests zum
Schreiben, Actions und Issues zum Lesen. Git, REST und Originalreader erhalten
dieselbe ausgewählte Laufidentität. Die lesende Diagnose unterscheidet von einer
tatsächlich bestätigten Mutation. Zugangsdaten gehören ausschließlich in den
Laufkontext. Ein konfigurierter App-Zugang verwendet die Repositoryinstallation
über `PW_REMOTE_APP_ID` und `PW_REMOTE_APP_PRIVATE_KEY`. Der Worker beschränkt
das kurzlebige Installationstoken auf das aktuelle Repository und die benannten
Operationen. Die Bereitstellung gehört zum Betreiberauftrag.

Ohne konfigurierte App verwendet Actions sein Repositorytoken. Ein damit
erzeugtes PR-Ereignis kann auf Genehmigung warten. Der Akteur liest den
tatsächlichen Laufstatus. Für den Regelbetrieb ist der ereignisauslösende
App-Zugang im isolierten Kontext zu erproben. Meldet der Worker nach geprüftem
Doppelpush `pr-access-required`, kann der aufrufende Akteur den gebundenen
Request im eigenen autorisierten Kontext fortsetzen. Bei Nutzung des Connectors
zuerst Basis, Produkthead und vorhandene PRs lesen. Für die bedingte Neuanlage
die Daten aus `production_remote_pr.product_pr` einschließlich der vollständigen
Markierung übernehmen. Den zugehörigen PR und die Checks mit `status` bestätigen.
[GitHub-Tokenverhalten](https://docs.github.com/en/actions/concepts/security/github_token)
und [Triggerregeln](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).

Der Connector bietet die bedingte Neuanlage und das Lesen von Commits und
Actions-Läufen. Der Push-Trigger ist an einer früheren Connector-Publikation
belegt. Die Wirkung des vollständigen Produktionswegs aus einem tatsächlichen
ChatGPT-Auftrag sowie sein produktiver Authkontext sind gesondert abzunehmen.
[Referenzlauf](https://github.com/venomenon328/picross/actions/runs/45095575946).

Der isolierte Testmodus `PICROSS_PW_REMOTE_TEST=1` bindet ausschließlich
`venomenon328/picross-remote-test`, dessen numerische Repository-ID, ursprünglichen
Git-Anker und synthetischen Job `pz-remote-t02`. Der Publisher prüft `test_only`;
die Registrierung verlangt den committed synthetischen Katalogmarker. Die
[Paketentscheidung](https://github.com/venomenon328/picross/issues/859#issuecomment-7131900027)
trennt den isolierten Nachweis von der produktiven Betriebsfreigabe.

## Antwortverlust und Wiederaufnahme

Bei gleichem Auftrag bleibt die Request-ID stabil. Nach verlorener Ref-/PR-Antwort
prüft der Akteur zuerst den gebundenen Nachfolgecommit, dessen Eltern, den
Produktref und die PR-Zuordnung. Die getrennten Zeitfelder sind Sekunden für
tatsächlich gemessene Abschnitte. Unbeobachtete Queue-, CI- und Wartezeiten
sind offen; die Dauer eines API-Abrufs misst nur diesen Abruf.

Der eigene private Operationsordner enthält die Publish-Absicht und gegebenenfalls
das PW-LOCAL-Journal sowie den Besitzbeleg für die Kataloglease. Dieselbe Operation
mit derselben privaten Wurzel fortsetzen. Nach Verlust eines Runners kann ein
neuer Prozess bestätigte Ergebnisse aus Git und gebundenen Originalen wiederfinden.
Eine noch belegte Lease ohne den ursprünglichen privaten Besitzbeleg blockiert.
Der ursprüngliche Akteur muss die geschützte Arbeitswurzel wiederherstellen
oder die konkrete Transaktion separat klären. Eine abgelaufene Uhr überträgt
keine Lease. Nach bestätigtem Abschluss die entbehrlichen eigenen Arbeitsdaten
entsprechend dem Auftrag entfernen. Es entsteht kein Recovery-Download.
