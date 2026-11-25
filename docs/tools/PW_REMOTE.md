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

Ein v1-Request hat genau die Felder `format=pw-remote-v1`,
`repository=venomenon328/picross`, `operation`, `job`, `expected` (volle
Arbeitscommit-SHA), `record_sha256`, `tools`, `main` und `input` sowie die
unten angegebenen Zusatzfelder. `tools` und `main` bezeichnen den beim Start
frisch zurückgelesenen Maincommit. Jede Folgeoperation bindet ihre tatsächlichen
Eingänge erneut.

| Operation | Zusatzfelder | Inhalt von `input` und Ergebnis |
| --- | --- | --- |
| `inspect`, `inspect-product` | bei Produktprüfung `product`, `pr` | Explizite `items` aus dem aktuellen Record gemäß Originalabruf oben. Liefert die Originale mit Herkunft und Ablauf. |
| `step3` | – | `motif_sha256`, vollständiges bestehendes Bilddesign unter `design` mit einem benannten Kandidaten, dazu `profile=line\|paired` und `label`. Die gewählte Motivdatei durchläuft Bild-/Rasterhelfer, Proof und unabhängigen Verifier. Der Builder ergänzt Kandidat und Zähler, der Publisher sichert die Ergebnisse zur Sichtung. |
| `step5` | `issue` (in v2 JSON-null oder tatsächlich zugeordnete positive Issue-ID, in v1 bestehende ID) | `background` enthält die tatsächlich gewählte ID, `none`, `standard` oder JSON-null zur Wiederverwendung. `decisions` enthält nur tatsächlich erklärte, noch benötigte PW-B-Entscheidungen für background/final/integration mit Scope, Inhaltsbindung, Akteur, UTC-Zeit und Erklärung. Bereits abgenommener Record: `{"background":null,"decisions":[]}`. |
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
Der v2-Worker bestätigt die publizierte Generation. Der Akteur übernimmt
den Draft-PR und dessen PR-CI nach dem folgenden Ablauf.

### Draft-PR und Package CI über den Connector

Vor Step 5 im aktuellen Repository die tatsächlichen Connector-Wege für
PR-Neuanlage, Git-Refs/Commitobjekte, Contents/Blobs, Release/Assets,
Commitvergleich, PRs und Actions prüfen. Repositoryname und numerische ID
an `GET /repos/OWNER/REPO` binden. Lesezugriff und angebotene Schreiboperation
belegen noch keine erfolgreiche Mutation. Fehlende notwendige Fähigkeiten
konkret melden. Für die reguläre Erstintegration `format=pw-remote-v2`,
`operation=step5` und `issue:null` verwenden. Ein ausdrücklich zugeordnetes
tatsächliches Issue kann als positive Zahl mitgegeben werden. Der Worker
liefert nach Doppelpush und vollständiger Publisherprüfung `pr-ready` oder
`pr-bound`. Er gibt Arbeitscommit, Recordhash, Produkthead, Basis,
Requestdigest und kanonische Draft-Metadaten aus.

Den [Offline-Reader](../../tools/production_remote_reader.py) an der verbindlichen
`tools`-SHA lesen und mit Python 3.11+ ausführen. Die JSON-Hülle enthält die
ursprünglichen REST-Antworten unter den folgenden Schlüsseln. Alle GETs liegen
unter `/repos/OWNER/REPO`; bei Connectorantworten
`structuredContent.content` als JSON dekodieren. Request-SHA und Job stammen
aus der bestätigten Einreichung bzw. der gebundenen Übergabe.

| Schlüssel | Original |
| --- | --- |
| `repository`, `main_ref`, `main_commit` | Repoobjekt, `git/ref/heads/main`, `git/commits/MAIN` |
| `request_sha`, `request_commit` | Bestätigte Einreichungs-SHA, `git/commits/REQUEST_SHA` auch nach Entfernung des Requestrefs |
| `work_ref`, `work_commit` | `git/ref/heads/content/pw/JOB`, `git/commits/WORK` |
| `input_record`, `completion_record` | `contents/content/authoring/JOB/current/record.json?ref=SHA`, einmal für den Requesteingang, einmal für den publizierten Arbeitsref; Base64-Originale |
| `product_ref`, `product_commit`, `product_diff` | `git/ref/heads/content/integrate-JOB`, `git/commits/HEAD`, vollständiges `compare/MAIN...HEAD` |
| `work_tag`, `release` | `git/ref/tags/work-prod-JOB`, `releases/ID` mit vollständigem Assetbestand, ID aus dem Record |
| `pulls`, `pr` | `pulls?head=OWNER%3Acontent%2Fintegrate-JOB&state=all&per_page=2`; bei genau einem Treffer zusätzlich `pulls/NUMMER` |

```text
python production_remote_reader.py originals.json
```

Bei `pr-ready` die zurückgegebenen `draft_pr`-Felder verwenden und
`content/integrate-JOB` → `main` direkt über den Connector als Draft eröffnen.
Der Body enthält den vollständigen Marker
`<!-- picross-production JOB REQUESTDIGEST -->`. Übergib die optionale
Issue-Referenz im Body und lasse den API-Parameter `issue` weg.
Anschließend die getrennten Ref- und PR-Reads am aktuellen Stand bestätigen
und mit `--expect-draft` prüfen. Bei Antwortverlust oder gleichzeitigem
Anlageversuch zuerst erneut alle Zustände über denselben Head suchen.
Ein offener zugehöriger PR ergibt `pr-bound`. Ein geschlossener, fremder,
veränderter oder mehrdeutiger Treffer blockiert die Anlage. Bei Abweichungen
den konkreten Befund festhalten. Ein frischer Chat setzt so am bestätigten
Completionstand fort. Bei bereits erfolgreicher Veröffentlichung sind
Fachrechnung, Wahl und Budgetstand abgeschlossen.

CI mit demselben Reader auswerten. Dazu `ci` mit folgenden Originalen ergänzen:

| Schlüssel in `ci` | Original |
| --- | --- |
| `workflow` | `actions/workflows/ci-modular.yml` mit aktivem Status und exakter ID |
| `runs` | Seitenarray aus `actions/workflows/ID/runs?event=pull_request&branch=content%2Fintegrate-JOB&head_sha=HEAD&per_page=100&page=N`; alle Treffer lesen |
| `run`, `attempt` | `actions/runs/RUN` und `actions/runs/RUN/attempts/ATTEMPT` für den passenden höchsten `run_number` und dessen aktuellen Versuch |
| `jobs` | Bei abgeschlossenem Run alle Seiten aus `actions/runs/RUN/attempts/ATTEMPT/jobs?per_page=100&page=N` |
| `test_merge` | `git/commits/TESTMERGE` aus dem aktuellen offenen PR, Eltern in der Reihenfolge Basis und Head |

Nur `checks-passed` bestätigt erfolgreiche `docs`, `verify (source)` und
`ci-required` samt übersprungenem `review-attachment` im tatsächlich
gebundenen Versuch. Der erfolgreiche Checkout-Schritt in `docs` muss
`PR N / HEAD / BASE / TESTMERGE` exakt enthalten. Bei ausstehendem Versuch
die aktuellen Antworten nach der tatsächlichen GitHub-Ausführung erneut lesen.
`status` ist der bedarfsweise Ersatz, falls der Connector notwendige
Originalmetadaten nicht liefern kann. Ein allgemeiner Workflow-Dispatch
belegt keinen PR-Testmerge.

Im Produkt-PR Eingang, Completion, Request, Produktcommit, Auswahl und
Endabnahme kompakt belegen. Den vollständigen Diff, gebundene Lieferoriginale,
das eigene Selbstreview und den tatsächlichen CI-Lauf verlinken.
Vor einem autorisierten Merge Main, Head, Basis, Testmerge und CI erneut
prüfen sowie Konfliktfreiheit und Schutzstatus bestätigen. Nach bestätigtem
Main die passende Generation mit `retire` abschließen. Bestätigten
Main/Retirement und gegebenenfalls offene Reste im Produkt-PR kommentieren.
Der normale Produktionsauftrag läuft ohne eigenständiges Produktionsissue.

## Aufrufzugang und Betrieb

Für die bedingte Neuanlage benötigt der Aufrufer Contents-Schreibzugriff auf das konkrete Repository. Der Worker verwendet Contents und Pull requests zum
Schreiben, Actions und Issues zum Lesen. Git, REST und Originalreader erhalten
dieselbe ausgewählte Laufidentität. Die lesende Diagnose unterscheidet von einer
tatsächlich bestätigten Mutation. Zugangsdaten gehören ausschließlich in den
Laufkontext. Ein konfigurierter App-Zugang verwendet die Repositoryinstallation
über `PW_REMOTE_APP_ID` und `PW_REMOTE_APP_PRIVATE_KEY`. Der Worker beschränkt
das kurzlebige Installationstoken auf das aktuelle Repository und die benannten
Operationen. Die Bereitstellung gehört zum Betreiberauftrag.

Für bestehende v1-Aufträge bleibt Worker-PR-Anlage samt
`pr-access-required` nach bestätigtem Doppelpush verfügbar. Ohne App nutzt
Actions sein Repositorytoken. Ein v1-PR-Ereignis kann eine Genehmigung
erfordern. Der Akteur kann aus der gebundenen Completion mit der
Connector-Route fortsetzen und den tatsächlichen PR-Lauf lesen.
[GitHub-Tokenverhalten](https://docs.github.com/en/actions/concepts/security/github_token)
und [Triggerregeln](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).

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

`pw-remote-v1` deckt die Einzeloperationen ab. Die nachfolgenden
[D-Erweiterungen](#pw-remote-d) verwenden `pw-remote-v2`.
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
Der Worker prüft frühere Beschnitte am neuen Korridor und Motivschutz. Kompatible
Beschnitte behalten ihre Originalbelege. Inkompatible entfernt der Builder aus
der aktuellen Auswahl, die Antwort nennt ihre IDs in `retired_crops`.
Bereits verbrauchte Versuche zählen weiter.
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
Eine tatsächliche Korridoränderung und eine Rasterableitung erfordern zwei
gebundene Requests. Bei unverändertem Korridor kann die neue Schutzbindung
mit der festen Ableitung über v2 erfolgen. Vor der Wahl die neue
Qualifikation und aktuelle Source am bestätigten Arbeitsref zurücklesen.

Die Workerantwort nennt Requestdigest, Vorgänger, Arbeitscommit, Recordhash und
gemessene Sekunden. Bei Festkorrektur, Profilprüfung oder RP-5 kommen Kandidat,
Proofstatus und Zertifizierung bzw. bei Nichtfund Suchendgrund und Verbrauch
hinzu. Die Zahl tatsächlich vorhandener Alternativen kann unter dem kumulativen
Versuchszähler liegen. Nach Publikation die Ansichten über `inspect` öffnen.
Bei RP-5 teilen sich die Solverläufe und die unabhängige Verifikation der
Endproofs das reservierte Abschlussbudget. Auch die erneuten R4-Prüfungen
für die aktuelle SD2-Bewertung verwenden dieselben verbleibenden Linien,
dieselbe Paararbeit und dieselbe monotone Frist. Die eigenständige SD2-Analyse
und deren Spurprüfung behalten ihre eigenen Budgets. Ein kontrollierter Abbruch
speichert den konkreten Endgrund und den Verbrauch am bisherigen Entwurf.
Der Worker verwendet
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

## PW-REMOTE-D

Die bisherige Einzelzustellung mit `pw-remote-v1` und `inspect-product`
bleibt verfügbar. `pw-remote-v2` gilt für `inspect`, `step3`, `step4` und `step5`.
Der Requestumschlag, der kanonische Digest und der erwartete Requestref
bleiben dieselben. Alle Felder und Rollen sind geschlossen.

- Ein `step3.input.fixed` darf zusätzlich `protection` mit den Feldern
  `actor`, `timestamp_utc` und `statement` enthalten. Die tatsächliche
  Erklärung gilt für die im selben Fixed-Plan gebundenen Zellen und den
  dortigen `mask_sha256`. `feature_cells` ordnet alle genehmigten
  Schutzmerkmale den geschützten Koordinaten zu. Der veröffentlichte
  Parameterkorridor und die Budgetgrenzen gelten unverändert. Die Ergänzung
  setzt eine neue Maskenbindung für genau diese Quelle voraus und
  bewahrt bestehende Crop-Freigaben. Der Builder speichert die Bindung und
  die abgeleitete Variante gemeinsam. Ein unveränderter Ausschnitt ohne
  Zelledit bleibt ein No-op. Eine dann noch benötigte Maskenbindung erfordert
  eine eigene Parameterentscheidung.
- `inspect.input.items` in v2 nennt explizit jedes Paar aus `candidate`
  und `role`. Zum Beispiel können drei angebotene Hintergründe mit
  jeweils `background` und `prepared` in einem ZIP angefordert werden.
  Jede Rolle wird aus demselben gepinnten Record und aus ihrer eigenen
  Kandidatenrevision aufgelöst. Dateinamen haben die Form
  `<candidate>--<role>.<suffix>`. Der Consumer prüft auch bei gleichnamigen
  Rollen Pfad, Originalreferenz, Medienart, Länge und Digest je Paar.
- Ein v2-Schreibrequest kann das Feld `delivery` mit derselben Liste von
  Rollenpaaren enthalten. Für Fixed, Import und RP-5 muss mindestens
  eine Rasterrolle die deklarierte Ergebnis-ID nennen. Bei Profilprüfung
  ist die Ergebnis-ID der überprüfte Kandidat. Bei `step4.input.prepare`
  stehen ausschließlich die benannten Hintergrund-IDs und die Rollen
  `background` und `prepared` zur Verfügung. Der Zustelljob liest die
  tatsächlich veröffentlichte unmittelbare Folgegeneration im selben Run.
  Der v2-Manifestteil `missing` nennt angeforderte Proof-, Difficulty- oder
  Crop-Rollen, für die der Record keinen Beleg enthält. Bricht die
  Beschaffung eines gebundenen Originals ab, bleibt die Zustellung offen.
  Duplikate, reine Nichtfunde und No-ops liefern keine erfundene Variante.
  Bei Bedarf den existierenden Kandidaten anschließend gezielt sichten.

Für ein v2-Ergebnis-ZIP zusätzlich zum bisherigen Consumer-Aufruf
`--input-commit`, `--result-commit` und `--result-record` übergeben.
Die beiden Git-Commitobjekte und die exakten Recordbytes an Eingang und
Nachfolger unabhängig via Connector lesen. Den Nachfolger am aktuellen
Jobref abgleichen. Der Consumer prüft den einzigen Parent, den
`PW-Remote`-Requestdigest, beide Recordhashes, Job- und Releasegeneration
sowie die ursprünglichen Trigger-, Worker-, Attempt- und Artefaktdaten.
Für lokal fehlgeschlagene oder abgelaufene Abrufe zuerst den tatsächlichen
Jobref, die Publikation und den erwarteten Requestref zurücklesen.
Bei bestätigter Publikation und offener Zustellung denselben Workflow-Run
vollständig neu starten oder einen gezielten Inspect am gebundenen
Nachfolger einreichen. Beim identischen Request erkennt der Worker den
eigenen Nachfolger und lässt Berechnung, Publikation und Verbrauch aus.
Der ursprüngliche Requestref wird erst nach erfolgreichem Rückdownload
und erneuter Bindungsprüfung der zuständigen Ack-Operation entfernt.
Bei einem gezielten Inspect zuerst dessen eigenes Zustellergebnis prüfen.

Zell-/Hinweisansichten verwenden den offiziellen Editorarchivpin aus
`p1_preflight`. Der Actions-Schlüssel bindet Cacheformat, Repository-ID,
System, Architektur, Release und Archiv-SHA-256. Jeder Lauf prüft die
reguläre Datei und den Digest vor dem Entpacken. Bei beschädigtem
Cacheinhalt wird der lokale Eintrag isoliert und der offizielle Download
wiederholt. Editor und Import des isolierten Projekts bleiben pro Lauf
gemeinsam für mehrere Ansichten. Definitionen und Ansichten liegen
außerhalb des Importscans. Der Renderer erhält keine Schreibidentität.
Cachezustand, Archivbytes und Zeiten für Prüfung, Download, Entpacken,
Import und Ansichten erscheinen im Staging-Ergebnis.

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
mit derselben privaten Wurzel fortsetzen. Für einen bereits gepushten
v2-Nachfolger mit ausstehendem Publisherabschluss den unveränderten Request
auf stdin an `python -B -m tools.production_remote recover --auth gh --root PRIVAT`
übergeben. Dafür die ursprünglich gebundene saubere Werkzeugrevision und die
ursprüngliche private Wurzel verwenden. Für Step5-v2 stattdessen denselben
unveränderten Request mit `execute` im eigenen privaten Ordner fortsetzen.
Der jeweilige Einstieg verlangt das passende
Journal. Eine noch belegte Lease erfordert den dazugehörigen lokalen Besitzbeleg.
Die Wiederaufnahme bestätigt den vorhandenen Arbeitscommit, bereinigt seine
gebundenen Vorgängerreste und führt das Journal nach. Fachrechnung, Zähler und
Arbeitscommit bleiben dabei erhalten. Für die Zustellung anschließend denselben
gebundenen Actions-Request erneut ausführen. Der Worker bestätigt den
Nachfolger und stellt die angeforderten Originale zu.

Nach Verlust eines Runners kann ein
neuer Prozess bestätigte Ergebnisse aus Git und gebundenen Originalen wiederfinden.
Eine noch belegte Lease ohne den ursprünglichen privaten Besitzbeleg blockiert.
Der ursprüngliche Akteur muss die geschützte Arbeitswurzel wiederherstellen
oder die konkrete Transaktion separat klären. Eine abgelaufene Uhr überträgt
keine Lease. Nach bestätigtem Abschluss die entbehrlichen eigenen Arbeitsdaten
entsprechend dem Auftrag entfernen. Es entsteht kein Recovery-Download.
