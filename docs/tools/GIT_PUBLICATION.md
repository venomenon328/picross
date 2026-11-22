# Geprüfte Git-Veröffentlichung

Geltung: Arbeits-, Integrations- und Reviewquellen von Picross. Der
[Entwicklungsworkflow](../dev-rules/WORKFLOW.md#5-umsetzen) regelt Befugnisse und
Branchwahl. [REPO-SLIM-B, B-K07](https://github.com/venomenon328/picross/issues/717#issuecomment-6996094828)
verlangt die Vorabprüfung vor dem ersten Upload von Gitobjekten.

| Situation | Geprüfter Einstieg |
| --- | --- |
| ChatGPT, geeigneter neuer Entwicklungsbranch | [Connector-Publisher](../../tools/publish_connector.py) und Connector-Git-Data-Operationen gemäß Ablauf unten |
| Neuer Arbeitsbranch über Git | `python -m tools.publish_git BRANCH --expected new` |
| Bestehender Arbeitsbranch über Git | `python -m tools.publish_git BRANCH --expected SHA` |
| Einzelner API-Commit auf bestehendem Arbeitsbranch | `python -m tools.publish_git BRANCH --expected SHA --api` mit Git-/gh-Zugriff |

Beide Publisher verwenden dieselbe [Objektprüfung](../../tools/publish_git.py)
und [Dateiklassifikation](../../tools/ci_growth.py). Sie erfassen alle ausgehenden
Commits, auch vorübergehend hinzugefügte Dateien, Umbenennungsziele, Änderungen
an bestehenden Dateien und Seitenlinien. Sie verlangen eine vollständige lokale
Git-Datenbank und die bereinigte Historie. Die Arbeitsref-/PR-CI diagnostiziert
nach einem Upload und kann ihn nicht rückgängig machen. Revieworiginale folgen
dem [Zustellvertrag](../dev-rules/CI_CONTRACT.md#zustellung-an-einen-unabhängigen-reviewer).

## Connector für neue Entwicklungsbranches

Voraussetzungen sind der autorisierte eigene Arbeitsbranch (`feat/`, `fix/`,
`chore/` oder `docs/`), lokale Git-Objekte und genau ein lokaler Commit direkt
auf dem über den Connector aktuell gelesenen `main`. Für diesen Weg genügt ein
vollständiger bereits verfügbarer lokaler Checkout auf dieser Basis. Der
Publisher selbst benötigt kein GitHub-Netz und keine `gh`-Anmeldung. Wenn der
frische Main-Commit lokal fehlt, die vollständige Basis beschaffen oder den
konkreten fehlenden Schritt melden. Arbeitsbaumänderungen zuerst am committed
Diff prüfen. Issue-/PR-Metadaten können entsprechend dem Auftrag unabhängig
von diesem Commitweg über den Connector bearbeitet werden.

Der Connector muss vollständige Git-Referenz- und Git-Commit-Metadaten lesen,
Git-Blobs, -Trees und -Commits erstellen und einen Ref **ausschließlich bei
Abwesenheit** anlegen können. Die dokumentierte [GitHub-Neuanlage](https://docs.github.com/en/rest/git/refs#create-a-reference)
verwendet `POST /git/refs`. Der Connector-Aufruf erhält dabei direkt die geprüfte
Kandidaten-SHA. Der normale [REST-Refupdate](https://docs.github.com/en/rest/git/refs#update-a-reference)
hat nur Ziel-SHA und Fast-Forward-/Force-Option. Ein davor ausgeführter
SHA-Abgleich oder ein Feld `expected_sha` ohne nachgewiesene atomare Semantik
genügt für bestehende Branches nicht. Der lokale `--api`-Weg verwendet die
serverseitige `expectedHeadOid`-Bindung seiner Commitmutation. Einen laufenden
PR auf seinem Branch fortführen. Fehlt dafür die sichere Schreibfähigkeit,
bleiben Quellen-, Issue-, PR- und CI-Zugriff separat nutzbar.

### Ausführung

Die Python-Befehle laufen im lokalen Checkout. JSON-Dateien und Manifest liegen
in der eigenen Arbeitsablage. Antworten müssen aus den genannten Connector-GETs
stammen. Bei `github_fetch` die JSON-Nutzlast aus `structuredContent.content`
dekodieren. Werkzeugfehler, fehlende Felder oder Abweichungen beenden die
Operation. Das Manifest enthält Quellbytes und gehört weder in Git noch ins PR-Log.

1. Lese-URLs mit `python -m tools.publish_connector reads BRANCH` bestimmen.
   Die GitHub-JSON-Antworten für `main` und `branch_refs` unter den gleichnamigen
   Schlüsseln in `observation.json` hinterlegen. Mit
   `python -m tools.publish_connector prepare BRANCH --head QUELL_SHA --input observation.json`
   das Manifest erzeugen, bevor ein Gitobjekt an GitHub gesendet wird. Es
   enthält die feste `head`- und `main`-SHA, den vollständigen strukturellen Diff
   und die aus den geprüften Git-Blobs gelesenen Base64-Bytes. Der Ref muss
   anfangs abwesend sein. Für Pfade, die GitHub nicht identisch darstellen kann,
   bricht der Baumabgleich ab. Der geprüfte Git-Transport bleibt verfügbar,
   wenn die Umgebung ihn unterstützt.
2. Die Werte aus `blobs` unverändert als `create_blob`-Argumente verwenden.
   Jede zurückgegebene SHA muss dem zugehörigen Manifest-Schlüssel entsprechen.
   Mit `tree` unverändert `create_tree` aufrufen. Nur wenn dessen SHA exakt
   `commit.tree_sha` entspricht, `commit` unverändert an `create_commit`
   übergeben. Der Gitbaum-Hash bindet alle Pfade, Typen, Modi und Bytes
   einschließlich der unveränderten Teile des Baums. GitHub kann wegen Autor-
   und Committermetadaten eine andere Commit-SHA als die lokale Vorlage erzeugen.
3. Den erzeugten Commit unabhängig über `GET /git/commits/SHA` lesen. `main` und
   `branch_refs` erneut über die Manifest-URLs lesen. Diese beiden Antworten
   zusammen mit `blobs` (Zuordnung erwarteter SHA zu tatsächlich zurückgegebener
   SHA), `tree_sha`, `created_commit_sha` und dem rohen Commitobjekt `commit` in
   `candidate.json` ablegen. Mit
   `python -m tools.publish_connector authorize-ref BRANCH --head QUELL_SHA --main MAIN_SHA --input candidate.json`
   erneut Objektprüfung, genauen Main, freien Ref, Blob-SHAs, vollständigen Baum,
   einzigen Parent und Nachricht prüfen. Das Ergebnis unverändert an
   `create_branch` übergeben. Eine inzwischen belegte Referenz muss GitHub bei
   dieser Neuanlage ablehnen. Bei einem Konflikt keine Refänderung versuchen.
4. Den Zielref separat über die URL `branch` lesen. `readback.json` enthält
   `request` (die Ausgabe aus `authorize-ref`) und `ref` (die rohe Antwort).
   `python -m tools.publish_connector verify-ref BRANCH --input readback.json`
   bestätigt ausschließlich die konkret autorisierte SHA. Auch nach einer
   verlorenen Neuanlageantwort zuerst diesen exakten Readback ausführen und
   nur einen Treffer als Erfolg behandeln. Bei einer anderen SHA vorhandene
   Arbeit erhalten und den tatsächlichen Refzustand prüfen. Ein Draft-PR nutzt
   die verifizierte Remote-SHA als Head.

## Prüfungen

`python -m unittest tools.test_publish_connector -v` prüft den Offline-Ablauf
mit synthetischem Git-Verlauf. Ein tatsächlicher Connector-Durchstich muss
seine GitHub-Mutationen und den getrennten Ref-Readback einzeln belegen. Ein
lokaler Test oder ein erfolgreiches Issue-Schreiben allein belegt weder die
Git-Data-Schreibfähigkeit noch eine erfolgreiche Commitpublikation.
