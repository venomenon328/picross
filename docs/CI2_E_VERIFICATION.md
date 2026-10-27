# CI2-E-T01 · Revisionsabschluss und begrenzter aktiver Bestand

Stand 27.10.2026 · [#417](https://github.com/venomenon328/picross/issues/417),
einschließlich „Umsetzungsvorbereitung V1 · 27.10.2026“.
Basis nach Aktualisierung: `main@8c31a69916941aed60ecd7e4d35a8d0d00637bf9` (PR #422).
Arbeitsbranch `chore/417-ci2-e-cleanup`; Ziel `main`. Unabhängiges CI2-E-R01
bleibt **vor Merge offen**. Kein Merge, Deployment oder Release beauftragt.

## Abschlussvertrag

`target_adapter retire-reveal-production --checkout . --integrated-commit SHA
--authoring-revision ID REVISION` wählt ausschließlich ausdrückliche Paare.
Der aktualisierte Main-Beleg muss Vorfahr von `origin/main` und Checkout-HEAD sein.
Aktive Quellen werden vor historischen Arbeitsdaten validiert: kein Rückfall bei
ungültigem Revealrecord, kein offenes Journal oder Stagingrest. Registrierter
Authoringrecord, aktuelle Bildrevision, Recordhash und finale Freigabe müssen genau
zusammenpassen. Originalreceipt, aktuelle Bild-/Noticebytes, Definition, Rating und
Hinzugefügt-Metadaten sind gegen den Main-Baum gebunden. Git-Baum-IDs prüfen die
lokalen Arbeitsbytes; nur kleine Index-/Record-/Freigabedokumente werden aus Git
gelesen. Keine alten Pakete rekonstruiert, kein Solver-/Produktionsreplay.

Die gesamte Auswahl wird vor Mutation geprüft, einschließlich unversionierter,
fehlender oder veränderter Revisionsdateien, Index und betroffener gestagter Quellen.
Nur gewählte Revisionsordner und ihre Indexzeilen entfallen. Geschwisterrevisionen
derselben ID bleiben erhalten. Originalpakete und versiegelte
`picross-integrated-content-v1`-Receipts werden nicht geschrieben. Vollständige
Wiederholung ist ein No-op einschließlich mtimes; Teilentfernung blockiert.
Ein I/O-Fehler während der Löschung ist kein erfolgreicher Abschluss und verlangt
Klärung des Git-Diffs; kein automatischer Restore historischer Pakete.

## Leser, Quellen und tatsächliche Bereinigung

Vor der Löschung wurden die sechs Pfadklassen gegen aktuelle Leser in `tools/`,
`tests/`, `game/` und `.github/`, vollständigen Main-Baum, lokale Dateimengen,
Git-Blob-IDs und Staging abgeglichen. Kein aktiver Produkt-/Testleser benötigt
diese sechs Klassen. `ci_scope.inert_path` bindet nur deren historische Pfadmetadaten;
synthetische Auswahltests erzeugen eigene Beispiele. Die `source`-Angaben der
aktiven Reveal-Provenienz sind erhaltene Herkunftstexte, keine Dateilader.

AT-A/B sind über PR #263/#264 integriert, HZ-A/B/C über PR #288/#289/#296.
Ihre damaligen Berichte und Eigentümerfreigaben bleiben erhalten. Verbleibende
Links auf entfernte Originale binden den vollständigen Commit
`8c31a69916941aed60ecd7e4d35a8d0d00637bf9`; frühere Resultate und offene Gates
werden nicht rückwirkend verändert. Aktuelle Einstiege führen D als über PR #422
integriert und E als implementiert mit offenem R01.

| Entfernte Klasse | Dateien | Bytes |
| --- | ---: | ---: |
| `content/authoring/*/at-b-r01/` | 755 | 270.602.991 |
| `docs/design/at_b_integration/` | 145 | 235.447.936 |
| `docs/evidence/hz-c/` | 60 | 121.580.344 |
| `docs/evidence/hz-b/` | 44 | 119.652.165 |
| `docs/evidence/hz-a/` | 7 | 62.539.334 |
| `docs/evidence/at-a/` | 145 | 27.220.954 |
| **Gesamt** | **1.156** | **837.043.724** |

Keine Abweichung von den sechs Kandidatenklassen. Der tatsächliche aktuelle
Ausgangsbaum enthält **2.340 Dateien / 983.764.166 Bytes**; die historische
Spezifikationsmessung 2.336 / 983.725.762 gehört zum älteren SD2-D-Stand.
Finaler Lieferbaum: **1188 Dateien / 146798515 Bytes**; Nettoänderung
**−1152 Dateien / −836965651 Bytes**. Größen sind summierte Datei-Bytes des
aktiven Git-Trees, keine behauptete Verkleinerung der Git-Historie.

660 geschützte Dateien wurden vor/nach der tatsächlichen Bereinigung per SHA-256
und mtime verglichen: gesamtes `game/`, aktive `content/`-Daten einschließlich
aller ursprünglichen Receipts, Ratings/Reports, offene Authoringrevisionen,
aktive Buch-/Sidebarquellen sowie `docs/evidence/kk/native-crops.json`. Alle gleich.
Die 26 AT-B-Revisionen wurden über den neuen Abschlussweg entfernt; die unmittelbar
anschließende Wiederholung war ohne Schreibwirkung. Beide Aufrufe zusammen:
72,026 s auf der Windows-Arbeitsumgebung, einschließlich Quellenvalidierung.
Das ist eine einmalige manuelle Bestandsoperation, kein CI-Test am echten Katalog.

Der Index schrumpft von 30 auf vier Einträge: `pz-4ec5ac61e2c447bd98c8508a993cbd32`
mit `r01/r02/r03` und `pz-cc522b3f66bc4d6eafe1f8a387d18d1f` mit `r01`.
Senf/Level-1-1, Pentagramm und offene Designarbeit bleiben erhalten. Die bereits
vorhandenen unversionierten lokalen Designbestände wurden weder geändert noch
in die Lieferung aufgenommen. Keine Ersatzarchive, Inventarmanifeste oder alten
Laufkopien werden neu eingecheckt.

## Kleiner Metadatencheck

`tools/ci_growth.py` läuft im vorhandenen Docs-Auswahlschritt, auch bei reinen
Inhaltsdiffs. GitHub liefert für exakte Base-/Head-Commits rekursive Git-Tree-
Metadaten samt Größen; unvollständige/trunkierte Antworten blockieren. Lokal nutzt
der Check `git --no-lazy-fetch ls-tree -rlz`; fehlende Größen blockieren ohne
historischen Blobdownload. Keine Engine, Bildöffnung, ZIP-Analyse oder neue Matrix.

Neue Dateien unter `docs/evidence/`, der abgeschlossenen AT-B-Integrationsklasse
und `at-b-r01`, generierte Output-/Build-/Cache-/Galerieklassen, Logs/Playerbinaries
und Archive außerhalb kanonischer Authoring-/Exportpfade blockieren. Aktive
Spielassets, Fonts/Lizenzen, Designquellen, kompakte Dokumente und echte offene
Authoring-/Exportarbeit bleiben möglich. Bereits aktive technische Inputs werden
nicht nach Dateiendung entfernt. Der Check ersetzt keine fachliche Prüfung, ob eine
Authoringrevision tatsächlich offen ist. Diese Entscheidung bleibt im Produktions-
und Diffreview; Metadaten können sie nicht aus ZIP-Inhalten ableiten.

Der begrenzte Bericht nennt Gesamtdateien/-bytes vorher/nachher, Nettoänderung,
neue/entfernte Dateien und modifizierte Dateizahl. Er liegt zusammen mit der
CI-Auswahl im bestehenden sieben Tage aufbewahrten Artefakt und im Joblog.
Kein zusätzlicher Job oder permanenter Archivkatalog. Die CI-Werkzeuge sind
ausdrücklich dem konservativen Nichtbrowserumfang zugeordnet; der neue
Produktionshelfer folgt der bestehenden Adapter-/Katalogabhängigkeit.

## Prüfungen und Gates

- Drei gezielte synthetische Abschlusstests bestanden, 63,388 s einschließlich
  gemeinsamem Exportaufbau. Kompaktes/vollständiges Originalpaket, offene neuere
  Revision derselben ID, Byte-/mtime-Erhalt, Indexpräzision und echter No-op.
  21 Negativvarianten prüfen fremde/fehlende Dateien, Teilentfernung, Index,
  gestagte Index-/aktive Änderungen bei wiederhergestelltem Worktree, ungültige/
  fehlende Bildquelle, Journal, fehlenden Main-Merge, offene Revision,
  Doppelauswahl, Pfadausbruch, Freigabe, veraltete Bindung, Hardlink und gemischte
  gültige/ungültige Auswahl sowie leere fremde Verzeichnisse und ungültige
  Bindungsobjekte; jeweils keine Mutation. Die erweiterte Negativprüfung wurde
  separat erneut ausgeführt: erfolgreich, 39,581 s einschließlich Fixtureaufbau.
- Vier synthetische Metadatentests bestanden, 0,335 s: erlaubtes Wachstum,
  Archive/Output-/Renameziele, API-Grenzen und lokale Größen ohne Lazy Fetch.
  Ein zusätzlicher echter gefilterter Git-Transportfall prüft, dass fehlende
  historische Blobdaten nach dem abgelehnten Größencheck weiterhin fehlen.
- Lokale Werkzeugprüfung: 230 Tests, 49,273 s, erfolgreich, drei vorhandene
  umgebungsbedingte Skips. Nach der letzten Ergänzung folgt der gezielte
  Auswahllauf mit 41 Tests in 26,343 s, erfolgreich; die abschließende vollständige
  Prüfung übernimmt CI.
- Dokumentprüfung der vollständigen sauberen Indexkopie: erfolgreich, 4,996 s;
  lokale unversionierte Arbeitsbestände gehören nicht zur geprüften Lieferung.
  `git diff --cached --check`: erfolgreich. Vollständige Diffauswahl, separater
  Selbstreview und tatsächliche Pflichtjobresultate einschließlich `ci-required`
  werden am finalen Head im Draft-PR gebunden; lokale Tests allein sind kein
  Gesamt-CI-Nachweis.
- Chromium ist **nicht angefordert** und wird nicht gestartet. Unabhängiges
  **CI2-E-R01 bleibt vor Merge offen**; Selbstreview ersetzt es nicht.

Getrennter Selbstreview: vollständige Änderungsliste, sämtliche Code-/Test-/
Workflowänderungen, Dokumentkonsistenz, historische Linktransformation und alle
1.156 Löschungen gegen die sechs freigegebenen Main-Klassen geprüft. Aktive
Quellen und Methodenfreezes bleiben im Git-Diff unverändert. Zusätzlich erkannte
Grenzen bei leeren fremden Unterordnern und ungültigen Bindungsobjekten wurden
geschlossen und synthetisch ergänzt. Kein unabhängiges Review behauptet.
