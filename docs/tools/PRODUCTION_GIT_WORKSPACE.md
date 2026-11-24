# PW-LOCAL: gemeinsame lokale Git-Arbeitsbasis

Dokument-ID: `production-git-workspace`
Status: Werkzeugvertrag PW-LOCAL-A
Entscheidung: 23.11.2026 · [#859 / PW-LOCAL-A](https://github.com/venomenon328/picross/issues/859#pw-local-a)
Zuständigkeit: lokale Objektablage, Produktionsworktrees, Sparse-Materialisierung
und ihre Anbindung an die sichere Publikation.

## Einstieg und Wiederaufnahme

Der Akteur startet im vertrauenswürdigen Werkzeugcheckout und bindet die
vollständigen Commit-SHAs. Der lesende Preflight aus [PW-B](PW_B_CONTRACT.md)
prüft frühzeitig den für eine geplante Veröffentlichung gewählten Transport.

```text
python -B -m tools.production_git_workspace ID --root WURZEL --tools TOOL_SHA --main MAIN_SHA --expected new
python -B -m tools.production_git_workspace ID --root WURZEL --tools TOOL_SHA --main MAIN_SHA --expected JOB_SHA --originals
```

Der erste Aufruf setzt einen freien Arbeitsref voraus. Der zweite prüft
`content/pw/ID` und lädt dessen größen-, hash- und eigentumsgebundene Originale.
Für private Originale kann der Akteur mit `--auth env` oder einer expliziten
Tokenquelle denselben Lesezugang für Git und REST wählen. Ein lokaler
Credentialhelper ist für Git ebenfalls möglich. Reine Berechnung benötigt Git,
Python und die Werkzeugabhängigkeiten. Der Akteur kann für eine einzelne
ChatGPT-Sitzung eine frische temporäre Arbeitswurzel verwenden.

Das Ergebnis nennt `tools`, `tool_commit`, `job`, `data_commit`, `main`,
`store` und `temporary`. Folgeprogramme mit Python `-B` aus `tools` ausführen,
`PYTHONDONTWRITEBYTECODE=1` für Kinder und `TMPDIR`, unter Windows auch
`TMP` und `TEMP`, auf `temporary` setzen. Den Jobpfad ausdrücklich als
`--repository`, `--publish-to` bzw. `work_publish --workspace` übergeben.
Nach einem Publish mit der zurückgelesenen SHA und `--originals` weiterarbeiten.
Nach unterbrochenem Publish zuerst denselben Publisheraufruf im vorhandenen
Jobordner mit der ursprünglichen erwarteten SHA wiederholen. Das persistierte
Journal bindet Entwurf, Index und Kandidatencommit. Der Publisher gleicht den
Remote-Ref, den lokalen detached HEAD, den Gitindex und beide Metadateien ab.

In Schritt 5 ergänzt `--integration content/BRANCH` einen separaten
Produktworktree auf der frisch geprüften Mainbasis. Für einen schon publizierten
Integrationsbranch zusätzlich dessen tatsächliche SHA als `--integration-head`
angeben. Beim Wiederöffnen nach der Registrierung erweitert Git das Profil
im selben Arbeitsordner. Bereits vorhandene neue Zielpfade müssen bytegleich
und als reguläre Dateien in diesem Commit und im Index gebunden sein.
Nach Finalizer und Export den Adapter mit `--checkout INTEGRATION`
planen und frisch registrieren lassen. Die einzeln geprüften Pfade aus
`changes` über `git add --sparse -- PFAD ...` stagen, den vollständigen Diff
prüfen und den Produktstand committen. Completion erhält im Jobworktree die
SHA dieses sauberen Integrationsworktrees und denselben geprüften Eingang.
Produkt-PR, Mergefreigabe und Retirement folgen dem Auftrag für den Job.
Der [Remote-Einstieg](PW_REMOTE.md) verwendet diese Arbeitsplätze für die gebundene Rasterproduktion und die Erstintegration. Seine Betriebsabnahme verlangt den isolierten Remote-Durchstich.

## 1. Gemeinsame Basis und stabile Arbeitsorte

Je Repository und tatsächlicher lokaler Arbeitswurzel eine eigene gemeinsame
Git-Datenbank verwenden. Ihre Objektablage wird von den verknüpften Worktrees
geteilt; pro Produktionsschritt entsteht weder ein neuer Clone noch ein
erneut vollständig materialisierter Arbeitsbaum.

Ein Rätsel behält einen stabilen eigenen Arbeitsworktree über seine Phasen,
Korrekturen und Wiederaufnahmen. Unterschiedliche Rätsel haben getrennte
Arbeitsbytes und Indizes. Der veröffentlichte Arbeitsref bleibt
`content/pw/<puzzle_id>`; lokale HEAD-/Refbindung und bestätigte Remote-SHA
werden ausdrücklich zugeordnet.

Der Integrationsbranch erhält einen eigenen sauberen Worktree derselben
Datenbank, aus frisch gebundenem main. Bei fortgesetzter Arbeit wird der
zugeordnete vorhandene Integrationsbranch/PR respektiert. Ein erforderlicher
zusätzlicher Sichtungsworktree nutzt ebenfalls die gemeinsame Datenbank.
Die Trennung von Produktions- und Integrationsdaten bleibt erhalten.

Ein wiederholter Einrichtungsaufruf findet den eigenen Store und passenden
Jobworktree wieder. Repositoryidentität, kanonische Arbeitswurzel, Besitz,
Rätsel-ID, Gitzuordnung und erwarteter Datenstand müssen übereinstimmen.
Unbekannte oder abweichende Pfade werden nicht überschrieben. Fehlende Rechte,
belegte Pfade und eine nicht verfügbare Arbeitswurzel werden konkret gemeldet;
kein Ausweichen in einen weiteren Vollclone.

Die [Arbeitsablage](../dev-rules/WORKSPACE.md) bestimmt Arbeitswurzel,
Eigentum und Löschbefugnisse. Lokale Besitz-/Verwaltungsdaten enthalten nur
technische Bindungen und erforderlichen Recoveryzustand, keine zweite
fachliche Produktionsakte. Persönliche absolute Pfade werden nicht committed.

## 2. Werkzeugstand und Datenstand

Der Programmeinstieg stammt aus einem ausdrücklich gebundenen
vertrauenswürdigen Entwicklungsstand. Ein kleiner gemeinsamer Sparse-Worktree
für Werkzeuge ist zulässig. Ein älterer gültiger Produktionsbranch muss den
neuen Helfer nicht enthalten und wird nicht auf main zurückgesetzt, um ihn
verfügbar zu machen.

Werkzeugrevision, erwarteter veröffentlichter Arbeitscommit und Mainbasis
einer Integration sind verschiedene Bindungen. Befehle erhalten den
Datenworktree eindeutig; dessen Arbeitsverzeichnis darf nicht versehentlich
den verwendeten Programmstand bestimmen. Der bisherige Schutz des lesenden
[Produktionsassistenten](PRODUCTION_WORKSPACE.md) bleibt erhalten: keine
ausführbaren Programme aus betrachteten Produktionsdaten.

Die gemeinsame Ablage liegt unter `picross-production` in der jeweiligen Wurzel.
Der Helfer prüft Besitzvermerk, Repository, Git-Zuordnung, Rolle und Revision.
Die Werkzeuganleitung beschreibt die [Fachbefehle](../../tools/puzzle_production/README.md).

## 3. Sparse-Checkout

Neue Worktrees zunächst ohne Arbeitsbaum-Materialisierung erzeugen, danach
das erforderliche Sparse-Profil setzen. Ein vorübergehender Vollcheckout
mit anschließender Ausdünnung erfüllt diesen Vertrag nicht. Sparse-Einstellungen
und Indexzustand gehören zum jeweiligen Worktree und dürfen andere Jobs
nicht umkonfigurieren. Eine `.git`-Datei ist eine reguläre Worktreebindung;
Gitpfade über die dafür vorgesehenen Gitbefehle auflösen.

Das Profil stellt die tatsächlichen Abhängigkeiten bereit:

- aktuelle Pflichtquellen und benötigte Werkzeug-/Methodenressourcen;
- Arbeitsindex, Kategorien, maßgebliche Registry und aktuelle Jobdateien;
- die konkret gebundenen aktiven Repositoryreferenzen;
- für Integration zusätzlich gemeinsame Registrierungs-/Runtime-Metadaten,
  Capabilitydaten und die tatsächlich betroffenen Produktziele.

Benötigte Dateien gezielt aus dem fixierten Gitbestand ergänzen. Der gesamte
fremde Rätsel-/Bildbestand wird nicht vorsorglich ausgecheckt. Ein fehlender
Pfad ist ein konkreter Abhängigkeitsbefund, kein stiller Vollcheckout-Fallback.
Paketprüfung und synthetischer Durchstich belegen die tatsächliche
Abhängigkeitsschließung; eine vermutete Verzeichnisliste genügt nicht.

**Nicht materialisiert bedeutet nicht im Repository abwesend.** Vor
Neuanlage, Ersetzung, Löschung und Registrierung die Zielbelegung am gebundenen
Gitbaum/Index prüfen. Eine ausgeblendete versionierte Datei darf weder als
freier Zielpfad gelten noch durch unvollständiges Staging aus dem nächsten
Commit verschwinden. Gegenprüfung und gezielte Materialisierung können im
Arbeitsplatzhelfer oder gleichwertig in den betroffenen Readern erfolgen.

Profilwechsel dürfen keine unbekannten, ungesicherten oder weiterhin
benötigten Originale entfernen; das schließt ignorierte Dateien ein.
Gebundene Originalbytes, Entscheidungen und verbrauchte Budgets bleiben
unverändert. Reine lokale Pfad-/Materialisierungsänderungen erzeugen keine
erneute kreative Wahl. Der aktuelle Record nach [PW-B](PW_B_CONTRACT.md)
bleibt alleinige fachliche Autorität.

## 4. Publisher und Wiederaufnahme

Die zunächst vollständige gemeinsame Gitbasis darf die benötigten
Publikationsobjekte für alle Worktrees bereitstellen. Eine eigene vollständige
Git-Datenbank je Arbeitsbaum ist nicht erforderlich. Sparse-Checkout betrifft
die materialisierten Arbeitsdateien, nicht die Prüfbarkeit der gespeicherten
Gitobjekte.

Änderungen an `work_publish`, `publish_git` und ihren auftragsbezogenen
Hilfsfunktionen sind Teil des freigegebenen Umfangs. Bestehende technische
Implementierungsannahmen dürfen passend ersetzt werden. Verbindlich bleiben
die funktionalen Garantien aus [Git-Publikation](GIT_PUBLICATION.md) und PW-B:
ausgehende Objekte vor dem ersten Upload prüfen, erlaubte Dateiklassen und
bereinigte Herkunft erhalten, erwartete Remote-SHA atomar binden, eigene
Assets zuordnen und tatsächlichen Remoteerfolg zurücklesen. Ein allgemeiner
zusätzlicher Shallow-/Partial-Clone-Modus ist für PW-LOCAL-A nicht nötig.

Ein erfolgreicher Publish muss im selben Jobarbeitsplatz sicher fortsetzbar
sein. Lokaler Entwurf, publizierter Record, HEAD und Index werden ausdrücklich
abgeglichen. Ein legitimer lokaler Entwurf kann von den veröffentlichten
Transportmetadaten abweichen; eine unbekannte Änderung darf dadurch nicht als
harmlos gelten.

Auch nach bestätigtem Remoteerfolg mit verlorener Antwort oder nach Abbruch
zwischen lokaler Ref-, Index- und Recordnachführung muss dieselbe Operation
fortsetzbar sein. Bereits bestätigte Ergebnisse und aktueller lokaler
Recoveryzustand werden geprüft statt blind erneut erzeugt. Keine
Datenrettung durch neuen Checkout, blindes Pull, Hard-Reset, automatisches
Stash oder pauschales Clean. Unzuordenbare Abweichungen bleiben als konkreter
Konflikt erhalten.

Gemeinsame Gitverwaltung, Jobwriter und Remote-Katalogtransaktion brauchen
passende Sperren und eine feste Reihenfolge. Vorhandene geeignete Locks
wiederverwenden. Der lokale Katalogbesitz und seine Nonce müssen einen Abbruch
überstehen; ein anderer Job oder eine nicht zugeordnete Operation darf sie
nicht übernehmen. Ein neuer Prozess darf ausschließlich die nachweislich
zugeordnete unterbrochene Operation mit derselben Besitzbindung fortsetzen.
Git-`worktree lock` zum Schutz der Worktreeverwaltung ersetzt keine
Prozesssperre für fachliche Schreiboperationen.

## 5. Integration, vorhandene Arbeit und Lebenszyklus

Die [Authoringintegration](../production/authoring/PUZZLE_AUTHORING_STEP_5.md)
übernimmt nur ausgewählte finale Produktdaten in den sauberen
Integrationsworktree. Der Arbeitsbranch mit Alternativen wird weiterhin
nicht nach main gemergt. Completion und Retirement prüfen die tatsächlich
gebundene Lieferung; der lokale Store erweitert weder Integrations- noch
Merge- oder Löschbefugnisse.

Die lesende PW-App behält ihren getrennten flachen/partiellen Cache. Dieser
Cache ist keine vollständige Writer-Datenbank. Die App erhält durch
PW-LOCAL-A keine neue schreibende Oberfläche.

Vorbestehende Vollcheckouts, fremde Worktrees und ungesicherte Änderungen
werden nicht automatisch migriert, verändert oder gelöscht. Ein aktueller
remote gesicherter Job darf im neuen eigenen Arbeitsplatz fortgesetzt werden;
das behauptet keine Sicherung lokaler unveröffentlichter Altänderungen.
Bei einem belegten erwarteten Arbeitsplatz oder unklarer Zuordnung stoppen.

Die dauerhafte Wiederverwendung ersetzt keine Aufbewahrungsentscheidung.
Ohne gesonderten Löschauftrag keine nachgelagerte Checkoutbereinigung und
keine pauschale Prune- oder Altordneraktion. Kleine eigene
laufinterne Testdaten folgen weiterhin WORKSPACE. Gemeinsame Datenbank,
aktive Worktrees und erforderlicher Recoveryzustand bleiben erhalten.

## 6. Nachweis und Quellen

PW-LOCAL-A belegt die gemeinsame Objektablage über den kanonischen
`git-common-dir`, den stabilen Jobpfad über wiederholte Phasenwechsel und
die Sparse-Wirkung an gezielt ausgelassenen versionierten Daten.
Gemeinsame Gitobjekte, materialisierte Arbeitsdateien und aktive Nutzdaten
getrennt messen; aus einer logischen Ordnergröße keine feste physische
GB-Einsparung ableiten. Windows-Pfad-/Sperrverhalten braucht einen tatsächlichen
Windows-Lauf. Szenarien, Module, Akteur und Lebenszyklus stehen im
[Prüfplan](https://github.com/venomenon328/picross/issues/859#prüfplan).

Technische Referenzen:
[Git worktree](https://git-scm.com/docs/git-worktree),
[Git sparse-checkout](https://git-scm.com/docs/git-sparse-checkout).
Die freigegebenen Produkt- und Befugnisgrenzen bestimmt dieses Repository.
