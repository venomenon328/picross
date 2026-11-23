# Geprüfte Git-Veröffentlichung

Geltung: Arbeits-, Integrations- und Reviewquellen von Picross. Der
[Entwicklungsworkflow](../dev-rules/WORKFLOW.md#5-umsetzen) regelt Befugnisse und
Branchwahl. [REPO-SLIM-B, B-K07](https://github.com/venomenon328/picross/issues/717#issuecomment-6996094828)
verlangt die Vorabprüfung vor dem ersten Upload von Gitobjekten.

| Situation | Geprüfter Einstieg |
| --- | --- |
| ChatGPT, neuer Entwicklungsbranch ohne lokalen Checkout | Direkter geprüfter Connector-Git-Data-Ablauf gemäß Abschnitt unten |
| ChatGPT mit bereits vorhandenem lokalen Checkout | Optional [Connector-Publisher](../../tools/publish_connector.py) mit Manifest und Git-Data-Operationen |
| Neuer Arbeitsbranch über Git | `python -m tools.publish_git BRANCH --expected new` |
| Bestehender Arbeitsbranch über Git | `python -m tools.publish_git BRANCH --expected SHA` |
| Einzelner API-Commit auf bestehendem Arbeitsbranch | `python -m tools.publish_git BRANCH --expected SHA --api` mit Git-/gh-Zugriff |

Die lokalen Publisher verwenden die gemeinsame [Objektprüfung](../../tools/publish_git.py)
und [Dateiklassifikation](../../tools/ci_growth.py). Sie prüfen sämtliche
ausgehenden Commits einschließlich Seitenlinien und benötigen dafür eine
vollständige lokale Git-Datenbank. Der direkte Connector-Weg prüft dagegen
seinen **einzigen neuen Commit** auf dem frisch gelesenen `main` anhand des
vollständigen Remote-Baums, des Diffs und seiner einzigen Elternbindung.
Beide Wege beachten dieselben verbotenen Dateiklassen. Ein lokaler Checkout
ist für den direkten Connector-Weg **keine Voraussetzung**. Die Arbeitsref-/PR-CI
diagnostiziert nach einem Upload und ersetzt keine Vorabkontrolle. Revieworiginale
folgen dem [Zustellvertrag](../dev-rules/CI_CONTRACT.md#zustellung-an-einen-unabhängigen-reviewer).

## Direkter GitHub-Connector ohne lokalen Checkout

Dies ist der bevorzugte ChatGPT-Publikationsweg für einen neuen, vom Auftrag
gedeckten eigenen Branch (`feat/`, `fix/`, `chore/` oder `docs/`). Er erstellt
genau **einen Commit mit dem frisch gelesenen `main` als einzigem Parent**.
Dafür sind keine lokale Git-Datenbank, kein lokales Git-Netz und keine
`gh`-Anmeldung erforderlich. Fehlen diese lokalen Werkzeuge, zunächst die
tatsächlich verfügbaren GitHub-Connector-Git-Data-Fähigkeiten prüfen statt den
Commit pauschal als unmöglich zu melden.

1. **Vor dem ersten Upload:** `main`-Ref, Git-Commit und vollständigen
   Basisbaum über den Connector lesen; den gewählten neuen Branchnamen und
   die Abwesenheit auch kollidierender Refpräfixe prüfen. Alle ausgehenden
   Pfade und Bytes vorab gegen den beauftragten Scope, vorhandene Datei-/Blob-
   IDs und Modi, Geheimnisse und die verbotenen Klassen aus
   [`ci_growth.py`](../../tools/ci_growth.py) kontrollieren. Nicht verifizierbare
   Änderungen sind ein konkreter Blocker, kein Freibrief für ungeprüfte Uploads.
2. **Blobs und Baum:** Ausschließlich die geprüften Änderungen über
   `create_blob` erzeugen und jede resultierende Blob-SHA mit den ursprünglichen
   Bytes durch einen echten Readback abgleichen. Den neuen Baum mit
   `create_tree` auf dem gebundenen Basisbaum und genau diesen Änderungen
   erstellen; den vollständigen Baum nachlesen und alle geänderten und
   unveränderten Pfade samt Modus, Typ und Blob-SHA vergleichen. Bei Binärdaten
   ist ein exakter Byte-/Hashweg nötig, kein bloßer Link oder Dateiname.
3. **Commit und Diff:** `create_commit` ausschließlich mit einem Parent
   (`main`-SHA) und dem kontrollierten Baum ausführen. Den Commit unabhängig
   nachlesen, Parent, Baum und Nachricht prüfen und den vollständigen GitHub-
   Commitvergleich gegen `main` auf genau den beauftragten Diff und die
   unveränderten übrigen Dateien kontrollieren. Fehlende Diffdaten nicht als
   erfolgreichen Vollvergleich ausgeben.
4. **Branch bedingt erstellen:** Vor der Refmutation `main` und die
   Abwesenheit des neuen Branches erneut lesen. Nur mit `create_branch` auf
   die geprüfte Commit-SHA anlegen; eine bereits vorhandene Referenz darf
   nicht überschrieben werden. Den Remote-Ref separat nachlesen und nur
   die erwartete SHA als veröffentlicht melden. Wenn `main` geändert wurde,
   zuerst die Prüfung auf frischer Basis erneuern.
5. **PR und Gates:** Draft-PR auf dem verifizierten Head erstellen und
   vollständigen Diff, echte CI-/Review-Gates und Mergebefugnis nach WORKFLOW
   auswerten. Noch nicht referenzierte Git-Objekte sind keine veröffentlichte
   Branchänderung.

Bei **bestehenden PR-Branches** ist die Fortführung auf demselben Branch
erforderlich. Ein Connector-Refupdate ist nur mit nachweislich **atomarer
Headbindung in derselben Mutation** zulässig. Ein vorheriger SHA-Read oder
ein nicht als atomar belegtes `expected_sha`-Feld am üblichen REST-Refupdate
reicht nicht. Ohne solche Funktion für genau diese Branchfortschreibung den
lokalen Publisher mit echter Lease verwenden und nur den betroffenen Schritt
als blockiert melden. Nicht daraus auf generelle Connector-Unverfügbarkeit
schließen und keinen neuen Ersatzbranch für denselben laufenden PR erfinden.

## Optionaler lokaler Connector-Publisher

Für einen bereits vorhandenen vollständigen lokalen Checkout bleibt
[`publish_connector.py`](../../tools/publish_connector.py) verfügbar. Dieser
**optionale** Weg erwartet lokale Git-Objekte und genau einen lokalen Commit
direkt auf dem über den Connector frisch gelesenen `main`. Der lokale Publisher
selbst braucht weder GitHub-Netz noch eine `gh`-Anmeldung. Fehlt die lokale
Gitbasis, ist der oben beschriebene direkte Connector-Weg zu prüfen und zu
verwenden; das Fehlen eines Checkouts ist kein allgemeiner Commitblocker.
Arbeitsbaumänderungen werden auf dem lokalen Weg zuerst am committed Diff
geprüft. Issue-/PR-Metadaten sind unabhängig von beiden Commitwegen zugänglich.

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

### Lokaler Manifestablauf

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
mit synthetischem Git-Verlauf. Ein tatsächlicher Connector-Durchstich – direkt oder mit lokalem Manifest –
muss seine GitHub-Mutationen, die Basis-/Baumbindung und den getrennten Ref-
Readback belegen. Der direkte Weg wurde für [#850 / PR #852](https://github.com/venomenon328/picross/pull/852)
an einem neuen Dokumentenbranch mit Blob-, Baum-, Commit- und Ref-Readback
sowie vollständigem GitHub-Diff und grüner PR-CI ausgeführt. Ein lokaler Test
oder erfolgreiches Issue-Schreiben allein belegt keinen Commit-Upload.
