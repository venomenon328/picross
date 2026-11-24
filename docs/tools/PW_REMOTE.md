# Remote-Ausführung für Rasterangebote und Erstintegration

PW-REMOTE-A verwendet den [portablen Arbeitsplatz](PRODUCTION_GIT_WORKSPACE.md),
den [Publisher](PW_B_CONTRACT.md) und genau einen auf Main gebundenen
[Actions-Worker](../../.github/workflows/pw-remote.yml). Der Produktionsakteur
übersetzt den kurzen Auftrag und die tatsächlichen Wahlen in den geschlossenen
Aufruf. Das Ergebnis nennt den gesicherten Arbeitsstand und den nächsten Schritt.

Der Worker hält den qualifizierten Eingang und die Katalogprofile für Plan und Registrierung in einem Aufruf. Bei getrennter lokaler Ausführung bindet der Adapter dieselbe Auswahl über den [Jobworktree](PRODUCTION_GIT_WORKSPACE.md#einstieg-und-wiederaufnahme).

## Originale in ChatGPT sichten

Fehlen dem aufrufenden Chat die geprüften Bildbytes, stellt er selbst einen
gebundenen `inspect`-Request, bevor er weitere Binärdownloads versucht. Das
gilt auch für einen frischen Chat. Der kurze Produktionsauftrag genügt.
`input.items` enthält je benötigter Rolle genau einen Eintrag, etwa
`{"role":"motif","candidate":"motif-a"}`. Kandidaten, Profil und Referenzen
aus dem frisch gelesenen Record nehmen. Vor der Wahl für jedes Hintergrundangebot
die Rollen `background` und `prepared` mit derselben ID anfordern. Bei
`prepared:null` rendert der lesende Worker genau diese Zeichnung mit HP-W2.
Für die reguläre Vorlage zuerst mit `step4` vorbereiten. Der Abruf liefert dann die gespeicherten Ausgabebytes. Für `none` und
`standard` entfällt dieser Abruf.

Für Schritt 3 das benötigte `reveal` und `motif` öffnen. Nach dem Schritt-3-
Publish den neuen Arbeitscommit und Record lesen. Für das konkrete Angebot
`definition`, `preview`, `cells-clues`, `proof` und eine vorhandene
`difficulty` anfordern. Bei einem Crop-Nachweis stehen auch `crop-before`,
`crop-preview` und `crop-protection` zur Verfügung. Die Zell-/Hinweisansicht
zeigt die vollständige Lösung und beide Hinweisachsen auf Spielpapier. Oben
stehen die 24-Pixel-Zellen, unten 14 Pixel. Von links nach rechts werden
normale, abgeschwächte und ausgekreuzte Hinweise mit der aktuellen
Spielschrift und Kontur gezeichnet. Nur diese Rolle lädt den gebundenen
Godot-Editor und die benötigten Zeichenressourcen. Zur Produktprüfung den
vollständigen gebundenen PR-Diff lesen und benötigte Lieferoriginale mit
`inspect-product`, `product`, `pr` und den Rollen `product-definition`,
`product-reveal` oder `product-background` am bestätigten Integrationscommit abrufen.

Der normale Requestref-Ablauf unten startet den Main-Worker. Sein Lesejob
braucht keine Kataloglease. Er prüft den aktuellen Record, die konkrete
Releasegeneration und die ausgewählten Originale und lädt ein Actions-Artefakt
mit einem Tag Retention hoch. Erst nach dem erneuten Download, vollständiger
Archivprüfung und erneuter Quellenprüfung quittiert ein eigener Job den Ref
mit erwarteter SHA. Die Actions-Schrittlaufzeiten und die gemeldeten
Originalzahlen, Bytezahlen und Aufbereitungszeiten sind getrennte Messungen.

Der Akteur führt diese Schritte im selben Chat aus:

1. Den erfolgreichen Push-Trigger für den vollständigen Requestref und dessen
   Commit sowie den erfolgreichen Worker auf dem aktuellen Main lesen. Die
   konkreten Run- und Attempt-IDs prüfen. Die Artefaktliste des Workerlaufs
   lesen, das Artefakt mit Namen `pw-<operation>-<Requestdigest>-<Run>-<Attempt>`
   eindeutig zuordnen. Die REST-Metadaten über die ID erneut lesen. Ist der
   Einzelendpunkt im Connector gesperrt, dieselbe ID in der frisch gelesenen
   Artefaktliste dieses Workerlaufs mitsamt `workflow_run` prüfen.
2. Die ZIP-Datei **über den Artifact-Download des Connectors** im eigenen
   Chat-Arbeitsbereich materialisieren. Den [eigenständigen Python-Reader](../../tools/production_remote_delivery.py)
   als vertrauenswürdige Quelle am geprüften Werkzeugcommit lesen. Er benötigt
   nur Python 3.11+. Seine CLI übernimmt mit `--request`, `--record` (exakte
   Gitbytes), `--trigger`, `--worker`, `--artifact`, `--archive` und
   `--output` die bereits vom Akteur gelesenen Dateien. Die beiden Run- und
   die Artefaktdatei enthalten die ursprünglichen REST-Objekte. Der Reader
   erzeugt erst nach vollständiger Prüfung ein neues Sichtungsverzeichnis.
3. PNGs dort mit dem Bilddecoder öffnen, Original und Ableitung nach ihren
   Bildnormen sichten. Die Hashes und tatsächlichen Urteile an die betrachteten
   Dateien binden. Neue Befunde mit dem PW-FIND-Verfahren behandeln. Vor der
   Folgeoperation Main, Arbeitsref, Record, Release/Assetbestand und ggf.
   Produktref/PR erneut prüfen. Der Folgeauftrag bindet diesen Stand.
4. Bei Antwortverlust zuerst die vorhandenen Runs/Attempts und das benannte
   Artefakt nachlesen. Bei abgelaufenem oder fehlerhaftem Ergebnis auf frischer
   Bindung einmal gezielt neu zustellen. Bei noch vorhandenem identischem Ref
   den fehlgeschlagenen Worker nach erneuter Quellenprüfung wiederholen. Bleibt
   der Fehler bestehen, konkreten Run, Status und nächsten Akteur melden.
   Ein offener Publish-/Retirement-Vorgang verbleibt beim belegten Besitzer.
   Download, Sichtung, Entscheidung, Publikation, PR/CI, Merge und Rückbau
   mit ihrem tatsächlichen Stand ausweisen.

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
| `inspect`, `inspect-product` | bei Produktprüfung `product`, `pr` | Explizite `items` aus dem aktuellen Record gemäß Originalabruf oben. Liefert die Originale mit Herkunft und Ablauf. |
| `step3` | – | `motif_sha256`, vollständiges bestehendes Bilddesign unter `design` mit einem benannten Kandidaten, dazu `profile=line\|paired` und `label`. Die gewählte Motivdatei durchläuft Bild-/Rasterhelfer, Proof und unabhängigen Verifier. Der Builder ergänzt Kandidat und Zähler, der Publisher sichert die Ergebnisse zur Sichtung. |
| `step5` | `issue` (bestehendes Produktionsissue) | `background` enthält die tatsächlich gewählte ID, `none`, `standard` oder JSON-null zur Wiederverwendung. `decisions` enthält nur tatsächlich erklärte, noch benötigte PW-B-Entscheidungen für background/final/integration mit Scope, Inhaltsbindung, Akteur, UTC-Zeit und Erklärung. Bereits abgenommener Record: `{"background":null,"decisions":[]}`. |
| `step4` | – | `prepare` listet die IDs aller vorgesehenen Hintergrundangebote. Der Worker sichert jede kanonische PNG-Ausgabe. Nach dem Originalabruf schreibt `assessment` die tatsächliche Sichtung je Kandidat fort. |
| `status` | `product` (Commit), `pr` (Nummer) | Leeres Objekt. Aktueller Produkt-PR und tatsächlicher PR-Lauf mit Head, Basis, Testmerge, Run, Attempt und Checkzuständen. Fehlende, ausstehende oder genehmigungspflichtige Läufe verlangen einen späteren Statusabruf. |
| `retire` | `product`, `pr` | Leeres Objekt. Separater Prozess mit der nach Completion veröffentlichten Arbeits-SHA und dem aktuellen Main. Er prüft den gemergten zugeordneten PR, die Integration seines Mergecommits und die gelieferte Generation vor dem Retirement. |

Eine bereits erklärte, noch ungesicherte Motiv-/Parameterwahl kann `step3`
vor dem Design mit `input.choice` fortschreiben. Es enthält `candidate`,
`motif_sha256`, `approved` und die tatsächliche `declaration` (Akteur,
UTC-Zeit, Erklärung, ggf. `crop_protection`). Zur Sichtungsfortsetzung
nimmt `input.assessment` genau `candidate`, `definition_sha256`,
`preview_sha256`, `review`, `observations` und `ready`. Der Builder prüft die
Angebotsreife. Eine Sichtung verbraucht keinen weiteren Rasterversuch.
Der Finalizer kann die Inhaltsbindung einer tatsächlich übermittelten
Entscheidung aus den gebundenen Bytes, aktuellen Sichturteilen und akzeptierten
Befunden selbst berechnen. Mitgelieferte Bindungen müssen übereinstimmen.
`step4` mit `input.assessment.observations` nimmt aktuelle konkrete PW-FIND-Beobachtungen
an der Ableitung auf. Unveränderte kombinierte Erklärungen bleiben maßgeblich.

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

### Schritt 3 am veröffentlichten Kandidaten

| Vorgang | Vor C | Aufruf in `step3.input` | Verbrauch (Rasterversuche, Reparaturrunden) und neu fällige Prüfung |
| --- | --- | --- | --- |
| Motivwahl, Import, Originalabruf, Sichtung | A/B | `choice`, `design`, separate `inspect`-Operation, `assessment` | Import 1/0. Eigene Definition, Proof, Difficulty und Ansichten prüfen. Sichtung 0/0. |
| Offene Domains, Kreuzlinien, bei Bedarf Lösungszeugen | Proof abrufbar | `diagnosis` | 0/0. Gelesene Definition und Proof binden. Suche nur bei ausdrücklicher Anforderung für einen offenen Fall. |
| Profilprüfung | lokaler Rasterhelfer | `profile_check` | 0/0. Definition, Revision und gestalterische Urteile bleiben gebunden. Geänderten Proof, Difficulty und Q-H03 prüfen. |
| Feste Korrektur, leerer Randbeschnitt | lokale feste Ableitung, Crop-Reader | `fixed` | 1/0 je tatsächlichem Ableitungsversuch. Voller unveränderter Ausschnitt ohne Edit 0/0. Nach Zell- oder Maßänderung neue Revision und Rasterprüfung. |
| RP-5 | Suchkern mit Importbundle | `repair` | 1/1 für die tatsächlich ausgeführte Suche einschließlich Nichtfund oder Abbruch. Nur einen neuen Nutzstand bei Fund aufnehmen. |
| Korridor, Motivschutz oder Budget anpassen | Builder | `parameters`, `budget` | 0/0. Tatsächliche Erklärung binden. Nur betroffene technische Fakten aktualisieren. |
| Technische Ausnahme, Befundannahme, Wahl | PW-B und PW-FIND | `exception`, `findings`, `select` | 0/0. Konkrete Belege bzw. angenommene Befunde an den Kandidaten binden. Die erklärte Wahl führt direkt zu `background_review`. |

Keine dieser Operationen verbraucht eine Bildkorrektur. Ungültige Eingänge
scheitern vor der Fortschreibung. Die bestätigte Arbeits-SHA und der
Requestdigest identifizieren die Wiederaufnahme nach Antwortverlust.

Alle neuen Aufrufe verwenden den bestehenden Umschlag `pw-remote-v1`.
`input` enthält genau einen Operationsnamen mit einem Objekt. Dessen
`source` enthält `candidate,revision,definition_sha256,matrix_sha256,proof_sha256,motif_sha256,parameters_sha256`.
Dateihashes beziehen sich auf die unveränderten Bytes. Der Matrixhash bindet
das kanonische JSON der numerischen `solution`, der Parameterhash die vollständige
Liste `parameters.approved` (SHA-256 ohne Abschluss-LF, wie `contract.digest`).
Ein fehlender Proof hat den Wert null. Der äußere Recordhash bindet zusätzlich
Releasegeneration, Asset-IDs, Befunde und Entscheidungen.

| Objekt | Weitere Pflichtfelder neben `source` |
| --- | --- |
| `diagnosis` | `uniqueness` (bool), `max_nodes` (0–100000). Antwort enthält offene Domains mit Originalkoordinaten, Zeilen/Spalten, Profil und Endgrund. Bei angeforderter Suche kommen Ressourcen, geprüfte Zeugen und bei zwei Lösungen deren Differenzpositionen hinzu. |
| `profile_check` | `profile` (line oder paired), `rationale`. Eine vollständige Zertifizierung wird wiederverwendet. Das aktuelle Runtimeformat verwendet auch für eine Vordergrundfarbe v2-Hinweise. Der konkrete Paarproof nennt sein passendes Wireprofil. |
| `fixed` | `output,label,profile,rationale,cells,mask_sha256,edits,crop,max_changes`. Die Maske ist eine vollständige boolesche Matrix. Ihr Hash gilt für die kanonischen Dateibytes einschließlich LF von `{before_sha256,motif_sha256,cells}`. `edits` verwendet numerische IDs und 0 für leer, `crop` ist das halboffene Originalrechteck. Beispiel für einen einzelnen Edit ist `{"x":4,"y":0,"before":0,"after":1}`. |
| `repair` | Dieselben Felder bis einschließlich `mask_sha256`, dazu `config,extra_changes_reason`. Das Config-Objekt enthält die [RP-5-Suchparameter](../../examples/rp5/README.md). Nur zulässige Regionen der Hypothese freilassen. Ein höheres Zellbudget in einer späteren Runde braucht eine konkrete Vorabbegründung, sonst ist `extra_changes_reason` null. |
| `exception` | `criterion,evidence,declaration`. Für einen diagnostizierten Randbefund `frame` verwenden, für ein konkretes negatives Farbpaar z. B. `palette:1:2`. Der Worker speichert die erklärten Belegbytes und bindet die Definition. |
| `findings`, `select` | `finding_decisions` enthält pro behandeltem Befund `id,expected,action,treatment,actor,timestamp_utc,statement`. `expected` ist dessen aktueller PW-FIND-Bindungshash. Die Wahl enthält zusätzlich `declaration`. Für eine bereits wirksame Annahme genügt die leere Liste. |

`parameters` verwendet anstelle von `source` die Felder
`previous,motif_sha256,approved,declaration`. `previous` bindet die alte
Parameterliste. Die neue Erklärung bindet den tatsächlich genehmigten vollständigen
Korridor und gegebenenfalls `crop_protection` (Definitionshash → Maskendateihash).
Für geänderte Grenzen bei `budget` gelten `previous,limits,declaration` mit
dem Digest der alten Limits. Jede Erklärung enthält `actor,timestamp_utc,statement`.
Für ein gespeichertes Raster ohne frühere Maskendatei können RP-5 und feste
Zelledits die vorhandene Merkmalsfreigabe direkt nutzen. Dazu in
`feature_cells` jeden genehmigten Merkmaltext als `feature` mit zugehörigen
geschützten Originalkoordinaten `cells:[[x,y],…]` angeben und die tatsächlich
richtige Maske anhand des Motivs prüfen. Eine bereits gebundene Maske muss
bytegenau passen. Für einen Beschnitt an geschützten Motiven gilt zusätzlich
die PW-B-Bindung der Schutzdatei in der tatsächlichen Motiventscheidung.
Bei RP-5 ist die Suchregion durch die ungeschützten Zellen festgelegt.
Mit `region:[[x,y],…]` lässt sie sich vor der Suche auf einzelne
ungeschützte Originalkoordinaten einschränken, etwa auf eine offene Lasche.
Eine kombinierte Korridor- und Rasterentscheidung kann der Akteur aus derselben
Erklärung in zwei gebundenen Requests vollziehen. Vor der Wahl die neue
Qualifikation und aktuelle Source am bestätigten Arbeitsref zurücklesen.

Die Workerantwort nennt Requestdigest, Vorgänger, Arbeitscommit, Recordhash und
gemessene Sekunden. Bei Festkorrektur, Profilprüfung oder RP-5 kommen Kandidat,
Proofstatus und Zertifizierung bzw. bei Nichtfund Suchendgrund und Verbrauch
hinzu. Die Zahl tatsächlich vorhandener Alternativen kann unter dem kumulativen
Versuchszähler liegen. Nach Publikation die Ansichten über `inspect` öffnen.
Der Worker reserviert für die Endzertifizierung die finalen RP-5-Budgets,
bei fester Korrektur und Profilprüfung standardmäßig 120 Sekunden und 100000
Linienauswertungen für den Solver sowie dieselben Grenzen für den Prüfer.

### Hintergrundwahl und Befundannahmen in Schritt 5

Vor der Auswahl fordert der Akteur in Schritt 4 die Vorbereitung aller
angebotenen IDs an. Danach öffnet er die gespeicherten Originale und Ausgaben
über `inspect`. Je Kandidat enthält `input.assessment` die Felder `candidate`,
`original_sha256`, `profile`, `sha256` der Ausgabe, die vollständigen Urteile
in `review` und die konkreten `observations`. Nach der Veröffentlichung genügt
in Schritt 5 die gebundene Wahl mit den tatsächlichen Schlusserklärungen.
Für `none` und `standard` entfällt der Ableitungsnachweis.

Mit `input.finding_decisions` kann derselbe Auftrag offene Befunde der Auswahl
oder ihrer Kombination annehmen. Jeder Eintrag nennt `target`, Befund-`id`,
den erwarteten PW-FIND-Bindungshash `expected`, `action=accept`, `treatment`,
`actor`, `timestamp_utc` und `statement`. End- und Integrationsentscheidung
binden den Stand einschließlich Befundannahmen, Sichturteilen und Ausgabehash.

## Antwortverlust und Wiederaufnahme

Vor einer Erfolgsmeldung und der Produkt-PR-Anlage prüft der Remote-Einstieg
den tatsächlichen Assetbestand der gebundenen Releasegeneration. Meldet er
offene Rest-IDs aus dem Vorgänger, führt der Besitzer denselben Auftrag im
ursprünglichen privaten Operationsordner fort. Ungebundene IDs sind separat
zu klären. Der frische Aufruf führt dafür keine Löschung aus.

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
