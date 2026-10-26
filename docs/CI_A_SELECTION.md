# CI-A: Ausführbare Prüfauswahl

## Aktuelle Ergänzung: CI2-B / #414

A ist nach separatem R01 über PR #419 auf
`94e3ea7d9674babbdcd6bde6251e233191fd096f` integriert. B ist nach separatem R01 über PR #420 auf `dd56d310` integriert und liefert
den vierteiligen Fachumfang:
`solver`, `images`, `adapter`, `catalog`. [CI2-B-T01](CI2_B_VERIFICATION.md)
bindet Zuordnung, Fixtureänderungen, Leserabgleich und tatsächliche Messungen.
Die nachfolgenden A-Lieferangaben behalten ihren historischen Bezug.

`production_contract.py` ordnet jedes aktive Fachtestmodul genau einer Gruppe zu.
Eine geprüfte transitive Konsumentenzuordnung berücksichtigt auch Funktionsimporte,
CLI-Module und testübergreifend benutzte Fixtures. Der schnelle Werkzeugpfad
weist unzugeordnete Module und abweichende aktuelle Importe ab. Unbekannte Quellen
und gemeinsame Änderungen bleiben konservativ; es gibt keine Präfixausnahme.
Die sechs unabhängigen Solver-/Verifier-Referenzen gehören zu `solver`, der feste
synthetische ZA-1-Durchstich zu `adapter`. Die native/Preflight-/Zustellungsauswahl
aus A wird dadurch nicht unterdrückt. Kein Kataloglauf oder Browserauftrag.

Auswahl und Ergebnis heißen jetzt `picross-ci-selection-v6` beziehungsweise
`picross-ci-result-v6`. `production_groups` ist wie `native_groups` ein zwingender
kanonischer JSON-Array-String im Scheduler; keine Gruppe ist exakt `[]`.
Der Bericht bindet außerdem `production_expected`. Der wiederverwendbare
Fachworkflow erhält Gruppen und Auswahlversuch ausdrücklich. Sein Runner führt
genau diese Tests und Integrationen aus; neue/fehlende Module, abweichende
Discovery, übersprungene Tests oder fehlgeschlagener Aufbau sind kein Erfolg.

Das bestehende `ci-required` lädt `puzzle-production-<head>-<producer-attempt>`.
Originalberichte, Test-IDs aus den aktuellen Quelldeklarationen, Gruppen,
Integrationsergebnisse, nichtleere Logs/Proofs und Datei-/Bytehashes müssen passen.
Head, Basis, Checkout, Run und Auswahlversuch stimmen überein;
Auswahlversuch ≤ Fachversuch ≤ Gateversuch. Fehlend, leer, doppelt, unbekannt,
falsch gebunden, abgebrochen oder fehlgeschlagen scheitert. Keine alten Ergebnisse
aus anderen Runs. Der Main-Nachlauf bleibt kurz; `production_groups=[]`.
Keine neue Testverwaltung, kein weiterer Job und kein neuer Artefaktweg.

## Aktueller Browserumfang: CI2-C / #415

[CI2-C](CI_B_BROWSER_GROUPS.md) ersetzt die nachfolgenden historischen A-Angaben
zu drei Pflichtbauten und 33 Fällen: `short` und Browseralias `all` wählen neun
Kernfälle und zwei Exporte; `regular` nur einen Export. Der getrennte ausdrückliche
Browserwert `export` wählt regular-start/E01 mit drei echten Exporten. Allgemeine
Scopes bleiben browserfrei. Auswahl-/Ergebnisschema v6 und Originaleventschutz
bleiben, Build-/Browserbelege verwenden v2. [C-T01](CI2_C_VERIFICATION.md) bindet
Messungen und Abnahmen; CI2-C-R01 bleibt separat vor Merge offen.

## Integrierte A-Lieferung / #413

[CI2](CI_SLIMMING.md) und [Issue #413](https://github.com/venomenon328/picross/issues/413)
binden die Umsetzung auf `chore/413-ci2-a-auswahl`, Basis
`main@7b7ea9ce6b5dc2e3ea024207a605cce31847f66b`. T01, finaler Head,
PR-Test-Merge, Run, Zeiten und Selbstreview stehen im integrierten PR #419.
Das separate A-R01 wurde vor dessen Merge erfüllt; die Angaben bleiben historisch.

Automatische PR-/Push-Ereignisse und alle allgemeinen manuellen Scopes sind
browserfrei. Das gilt auch für unbekannte/gemeinsame Pfade, Runtime, Toolchain,
`all`, `production`, `visual` und `perf-b`. Die automatische Main-Pushroute
führt nur den kurzen Docs-/Integritätsweg aus. Eine bewusste manuelle Fachprüfung
auf Main bleibt möglich; die Ausnahme hängt am Ereignis, nicht am Branchnamen.
Native Gruppen, Fachsuite, Preflight und Zustellung behalten für PR/Dispatch ihre
bisherigen voneinander unabhängigen Auswahlpflichten. Der reine Inhaltspfad bleibt.

### Ausdrücklicher Browserauftrag

Der registrierte Einstieg ist `ci-chromium.yml` / `workflow_dispatch`:

| Input | Default | Bedeutung |
| --- | --- | --- |
| `scope` | `auto` | Allgemeine Nichtbrowserauswahl; nur Erweiterung des tatsächlichen Diffs. |
| `browser_scope` | `none` | Eigenständige explizite Auswahl: `regular`, `catalog`, `input`, `completion`, `persistence` oder `all`. |

Jede technische Einzelgruppe enthält `regular` als Voraussetzung. `all` im
Browserinput wählt alle fünf Gruppen. Ein leerer Dispatchdiff mit `scope=auto`
und allein gewähltem Browserumfang startet nur Auswahl/Gate und genau diese
Browserroute. Änderungen oder zusätzlich gewählte allgemeine Scopes behalten
ihre Nichtbrowserpflichten; sie erweitern niemals den Browserteilumfang.
Die alten `browser-*`-Werte des allgemeinen Scopeinputs sind entfernt.

`picross-ci-selection-v5` enthält den kanonischen `browser_request`: `null`
oder `{"browser":"chromium","scope":"<Umfang>"}`. Derselbe kompakte JSON-String
ist ein zwingender Scheduleroutput. Der Plan prüft den Auftrag vor Git-Fetches,
das Gate unabhängig gegen `GITHUB_EVENT_PATH` und `GITHUB_EVENT_NAME`, also die
ursprünglichen Dispatchinputs des Runners. Ein selbstkonsistent umgeschriebener
Plan/Scheduler oder ein allein gesetztes `web=true` genügt nicht. Auch der
allgemeine Dispatchscope wird gegen die ursprünglichen Inputs geprüft.

Beide wiederverwendbaren Workflows erhalten `browser_request` und `browser_scope`
ausdrücklich. Shellguards prüfen vor Checkout/Cache/Build bzw. Browserinstallation
Ereignis, ursprünglichen Browserinput, gültigen Umfang und kanonischen Auftrag.
Ein zusätzlicher CLI-Check prüft den heruntergeladenen Plan, tatsächlichen Checkout
und Quell-/Runbindung vor Abhängigkeiten/Build. Build- und Browserbelege binden
auch den Auftrag. Erfolgreiche Wiederholungen desselben Runs behalten die vorhandene
Reihenfolge Auswahlversuch ≤ Buildversuch ≤ Browserversuch ≤ Gateversuch.
Dispatch-Branchcommits werden nicht als PR-Test-Merge-Prüfung ausgegeben.
Die Concurrencygruppe trennt Ereignis und beide Scopes am selben Ref; automatische
Runs brechen dadurch keinen manuellen Browserlauf ab.

Ohne Auftrag sind Browsergruppen/-erwartungen leer; Scheduler und Gate laden
keine Browserartefakte und starten keinen Unterworkflow. Das Ergebnis lautet
`not requested`; ein unerwartet erfolgreicher Browserjob scheitert trotzdem.
Mit Auftrag müssen Job, Gruppen/Szenarien und Originalbelege vollständig passen.
Fehlend, übersprungen, abgebrochen, fehlgeschlagen oder falsch gebunden ist kein
Erfolg. Die PR411-Sonderbedingung und ihr spezifischer Test sind entfernt.
Die bisherigen 33 Szenarien, Bildpflichten und **drei echten Exporte auch bei
Einzelgruppen** bleiben in A erhalten. Erst CI2-C kürzt diese innere Route.
CI2-B/D/E, native Historykürzung und Bestandslöschung sind nicht Teil von A.

### Enge Fachauswahl und inerte Belege

Die exakt 20 SD2-Pfade aus CI2 §1 ergänzen `ANALYSIS_PATHS`: 13 Rechen-/CLI-/
Prüfmodule, fünf eingefrorene JSON-Dateien, zwei synthetische Tests. Der aktuelle
Leserabgleich zeigt explizite Analyse-/Bewertungseinstiege und Katalogadapter als
Konsumenten; Engine/Browser importieren diese Module nicht. Gemeinsamer Vertrag,
Katalogmethodik/-analyse/-bewertung, Registry, Exporte, Transaktionen und Fixtures
bleiben außerhalb. Neue `sd2*`-Namen erben keine Ausnahme. Keine echten Katalogtests.

Die sechs bestätigten inerten Klassen aus [dem Inventar](DEVELOPMENT_ARCHIVE.md)
werden eng anhand von Pfad, bekanntem Datenformat und Git-Metadaten zugeordnet.
Die genehmigten Namen stammen ausschließlich aus dem unveränderlichen Tree
`7b7ea9ce6b5dc2e3ea024207a605cce31847f66b`; es gibt kein wachsendes Archivmanifest.
Nur dort vorhandene Dateien mit altem Modus `100644` und neuem Modus `100644`
oder `000000` erhalten den Metadatenweg. Neue Namen, Code, benachbarte Bereiche
und aktive Inputs wie `docs/evidence/kk/native-crops.json` bleiben außerhalb.
Ausführbare Dateien, Symlinks und Gitlinks in den Belegformatpfaden werden auf
beiden Diffseiten abgewiesen.

`fetch_diff_blobs()` lädt für diese geänderten/gelöschten Belege weder alte noch
neue Blobs; der genehmigte Tree wird ausschließlich als Metadaten gelesen/geholt.
`git diff --check` prüft alle verbleibenden aktiven Pfade wortgetreu in begrenzten
Argumentblöcken gegen dieselben exakten Base-/Head-Trees. Reine Inhaltslieferungen
behalten ihren bisherigen Metadatenweg. Rename bleibt Delete plus Add: eine aktive
Seite verliert weder Auswahl noch Whitespaceprüfung. Neue Belegnamen erhalten
keine Snapshotausnahme. Der Docsjob materialisiert weiterhin seine vollständigen
aktuellen Quellen; A behauptet keinen allgemeinen Checkout-/Bestandsabbau.

Neue Module und neue Dateibereiche müssen im Review eine passende Fachzuordnung
mitliefern; unbekannte Wirkung bleibt konservativ bei allen Nichtbrowserbereichen.
Die gezielten Tests verwenden vorhandene Unittest-, temporäre Git-/Partial-Clone-,
CLI- und Shellproben; keine zusätzliche schwere Testverwaltung oder Browserproduktion.

## Gebundener CI-A-Ausgangsstand

Alle folgenden Abschnitte dokumentieren den bisherigen Liefervertrag und seine
Ergänzungen. Automatische oder implizite Browserpflichten, breite manuelle Scopes
und vollständige Wiederholungspflichten daraus gelten nicht als CI2-Ziel.
Historische Ergebnisse behalten ihre Quellenbindung; alte Voll-/Browserläufe
müssen nicht erneut als Baseline erzeugt werden. Die bisherige Implementierung
bleibt bis zur jeweiligen Umstellung unverändert; ein noch ausgewählter Altjob
wird durch Überspringen nicht nachträglich erfolgreich.

Lieferung für [#247](https://github.com/venomenon328/picross/issues/247), gemäß
[CI-Policy](CI_POLICY.md). Ausgangsbasis der Umsetzung ist
`df6405fe17c4fe15600e141700ad210d58586e7c`, identisch zur Vorbereitung CI-A/V1.
Technische Abnahme CI-A-T01, finaler Head/Base/Test-Merge/Run, Messwerte und
getrennter vollständiger Selbstreview stehen im Implementierungs-PR. CI-A-R01
bleibt ein separater qualifizierter Review vor Merge. Keine Produktänderung,
kein Deployment, keine vorgezogene CI-B-/CI-C-Ausführung.

## Abhängigkeiten und enge Ausnahme

Die exakte Positivliste `ANALYSIS_PATHS` in [ci_scope.py](../tools/ci_scope.py)
enthält die sechs `analysis*.py`-Module, `solver.py`, `paired_solver.py`,
`difficulty_identity.py`, `difficulty_rating.py`, die drei gebundenen
`difficulty_*_0_3.json` sowie vier feste synthetische Tests (`test_analysis`,
`test_difficulty_rating`, `test_lines`, `test_color_lines`). Nur diese Dateien
wählen ausschließlich `docs` und `production`. Neue Namen/Methodenversionen
erben keine Ausnahme. Dokumente behalten ihren Dokumentpfad.

Prüfung der Aufrufer am Ausgangsstand:

| Grenze | Folgerung für Auswahl |
| --- | --- |
| Analyse/Rating berechnen und prüfen explizite Werkzeuginputs; Solver wird von CLI, Import/Reparatur und synthetischen Fachfixtures benutzt. | Fachsuite einschließlich Import-/Export-/Registrierungsgegenproben bleibt vollständig. Kein automatisches Bewerten echter Katalogrätsel. |
| `analysis_io` liest die Runtime-Definition ausschließlich als expliziten Analyseinput; Katalogbewertung verwendet diesen Adapter beim manuellen Bewerten. | Keine Runtime-/Buildausführung der Analyse. Der Adapter bleibt Teil der eng geprüften Analysegruppe. |
| `catalog_rating` verwendet Analyse/Rating für Sidecarprüfung; Registry und Transaktionen verwenden Kataloghelfer. | `catalog_*.py`, `content_*.py`, gemeinsamer `contract.py`, Paketeinstiege und Schemas bleiben außerhalb der Ausnahme. Änderungen daran wählen weiterhin Fach-/Product-/Browser-/Zustellungsprüfungen. |
| `za1_product` verwendet `za1_fixtures` und Registry; Webbuild verwendet Product-Verpackung, Preflight und Webbundle. | Fixtures, Registry, Export, Produktionskonfigurationen und Harnesses bleiben breit; kein Präfixfreibrief für Produktionswerkzeuge. |
| `deploy_web.py` und `ssh_reference.py` benötigen Webbundle und Loopback-HTTP, kein Playwright. | Nur `delivery` zusätzlich zu `docs`. |
| `serve.py` und `web_bundle.py` dienen beiden Webwegen; Build und Exportkonfiguration definieren deren reales Bündel. | Browser und Zustellung. `game/project.godot`, Exportpresets und Webshell/-storage wählen zusätzlich ihre native Runtimeabdeckung. |
| Browserprobe, Browserruntime, Startprobe und technische Webfixtures betreffen nur Browsernachweise. | Nur `web` zusätzlich zu `docs`; vollständige Routen bis CI-B. |
| `game/ui/main.gd`, Spiellogik und Darstellung wirken im nativen Spieler und Browser. | Product mit bestehenden Untergruppen und vollständiges Web; keine pauschale SSH-Pflicht. |
| Native PERF-B-Prüfer/-Referenz wirken in nativen Prüfungen; aktive Spielatlanten wirken auch im Browser. | Native Prüfer wählen Product, die Spielressourcen zusätzlich Web. |

Die Fachausnahme erfasst alle 17 tatsächlichen Pfade von PR #241 einschließlich
der Dokumente. Der Test hält nur deren Pfadnamen, keine realen Rätsel oder
Katalogsnapshots. Die einzelne `.github/pull_request_template.md` wählt nur
`docs`; andere `.github/`-Dateien wählen alle Bereiche. Mischdiffs vereinigen
die Anforderungen, unbekannte Pfade bleiben konservativ vollständig.

## Manuelle Scopes

Alle Scopes erweitern die automatische Auswahl. [CI-C](CI_C_NATIVE_GROUPS.md)
führt die native Auswahl mit sieben unabhängigen Gruppen fort. Die Tabelle
bezeichnet die bisherigen manuellen Pflichten; CI-C erhält oder erweitert sie.

| Scope | Zusätzlich angeforderte Bereiche |
| --- | --- |
| `auto` | Keine Erweiterung |
| `runtime` | Product + Integration + vollständige Browserroute |
| `visual`, `perf-b` | Product + Visual + PERF-B + vollständige Browserroute |
| `production` | Fachsuite + Product + Piloten + Visual + PERF-B + Browser + Zustellung |
| `all`, `toolchain` | Alle Flags einschließlich Zustellung und Preflight |

`runtime`/`visual`/`perf-b` behalten die bisher implizite Browserabdeckung
ausdrücklich. Ihre bisher sachfremde SSH-Kopplung entfällt; für einen ausdrücklich
vollständigen Lauf stehen `all`/`toolchain` zur Verfügung. `production` bleibt
der breite manuelle Produktions-/Integrationsweg, auch wenn ein enger Fachdiff
automatisch nur die Fachsuite auswählt. Automatische Main-Pushes wählen nur
Dokument-/Inhaltsintegrität und bei Bedarf Fachtests; keine erneuten Product-,
Preflight-, Browser- oder Zustellungsläufe.

## Ausführung und Ergebnisgate

Gesondert beauftragte Nacharbeit AT-B-V01-SR01-B01 / [#256](https://github.com/venomenon328/picross/issues/256):
Der Fetchpfad stellt vor dem vollständigen Whitespacecheck fehlende Diff-Blobs
beider exakten Vergleichsseiten gebündelt bereit. Die Existenzprüfung verwendet
`git --no-lazy-fetch cat-file`; der Abruf lädt die fehlenden Objekt-IDs per
Standardeingabe, einschließlich alter gelöschter/umbenannter Dateien. Ein Fehler
bleibt fatal. Pfadklassifikation, vollständiger Diffcheck, Prozessgrenze und
Ergebnisgate bleiben unverändert. Reine Inhaltslieferungen betreten diesen
Blobpfad nicht. Synthetische partielle Cloneproben und die aktuelle Lieferbindung
stehen im [AT-B-Bericht](AT_B_VERIFICATION.md#gesonderte-technische-nacharbeit-b01).

Die nachfolgende serielle Webausführung beschreibt den gebundenen CI-A-Lieferstand.
[CI-B](CI_B_BROWSER_GROUPS.md) ersetzt sie durch unabhängige Gruppen und
zusätzliche Szenarien-/Belegprüfung. Die Eigentümerentscheidung vom 19.10.2026
in [#261](https://github.com/venomenon328/picross/issues/261) /
[CI-Policy](CI_POLICY.md) beschränkt die aktuelle Browser-CI auf Chromium;
alle bisherigen Chromium-Szenarien bleiben. Die nachfolgende Beschreibung
beider Browser ist ausschließlich der historische CI-A-Lieferstand.
CI-A-Auswahl, Zustellung
und Quell-/Run-/Retrybindung bleiben erhalten.

`web` und `delivery` hängen jeweils nur am Auswahl-/Dokumentjob. Web installiert
Playwright mit Chromium/Firefox, baut den regulären Spieler und zwei echte
technische Exporte und führt beide vorhandenen Start-/Browserrouten vollständig
aus. Zustellung installiert OpenSSH, baut genau einen regulären Export und
führt alle vorhandenen positiven/negativen SSH-/HTTP-Szenarien aus. Beide Jobs
verwenden getrennte Runner, Verzeichnisse und Artefakte. Bei gemeinsamer Auswahl
wird der reguläre Export in beiden Jobs gebaut; Build-Sharing ist keine CI-A-
Optimierung und wird hier nicht eingeführt.

Der unveränderte exakte Base-/Head-Treevergleich berücksichtigt beide Seiten
von Rename/Delete und den bisherigen Inhalts-Dateimodusschutz. Checkout bleibt
der Test-Merge. Das Gate verlangt exakt sechs eindeutige Jobergebnisse:
`docs`, `production`, `product`, `preflight`, `web`, `delivery`. Ausgewählt
bedeutet `success`, nicht erforderlich bedeutet `skipped`. Fehlend, leer,
abgebrochen, fehlgeschlagen, unerwartet oder widersprüchlich scheitert.

Der vollständige Auswahlbericht wird als Datei übertragen. Das Gate berechnet
die Auswahl aus den gespeicherten Pfaden/Scope/Event erneut, prüft Gründe und
Flags und vergleicht sie mit den tatsächlichen Scheduleroutputs. Head, Base,
Checkout, Event und Run müssen zur aktuellen Gateausführung passen; der
Auswahlversuch ist zusätzlich als Joboutput gebunden und darf nicht nach dem
Gateversuch liegen. GitHub darf bei einem Retry erfolgreiche Jobs desselben
unveränderten Runs beibehalten. Andere Runs oder Quellstände sind ausgeschlossen.
Doppelte JSON-Schlüssel werden abgewiesen. Der Ergebnisbericht enthält den
vollständigen Auswahlbericht und jedes tatsächlich gemeldete Jobergebnis.
Fehlt der Bericht oder seine Bindung, ist dies kein grüner Abschluss.

CI-C ergänzt das native Gruppen-/Artefaktgate und `native_groups` als gebundenen
Scheduleroutput. Die sechs Bereichsergebnisse und diese Retryregeln bleiben erhalten.

**CI-258 / #258 – kanonischer Transport:** Das Joboutput `native_groups` ist
immer ein nichtleerer, kompakter JSON-Array-String; keine nativen Gruppen sind
genau `[]`, eine Gruppe etwa `["catalog"]`. Der Auswahlbericht selbst behält
sein Array. Das Ergebnisgate vergleicht den vollständigen Scheduleroutput
bytegenau mit der kanonischen Serialisierung der gebundenen Auswahl. Fehlende
Schlüssel (auch bei leerer Auswahl), falsche Typen, zusätzliche Felder,
abweichende Reihenfolge und nichtkanonische Werte bleiben Fehler. Product
erhält die bestehende CSV-Eingabe nach Dekodierung der JSON-Liste; die
Exportpflicht wird aus ihrer tatsächlichen Mitgliedschaft bestimmt.


Auswahl/Ergebnis heißen `ci-selection-<head>-<attempt>` und
`ci-result-<head>-<attempt>`. Browserbelege/Spieler heißen `picross-web-*`,
Zustellungsbelege/Spieler `picross-delivery-*`, jeweils mit Head im Namen.
Buildmanifeste und Fachberichte binden die geprüfte Revision; der Run ordnet
Artefakte und tatsächliche Jobausführung zu. Technische Belege bleiben sieben,
Spieler vierzehn Tage erhalten. Erfolgreiche Zustellung ist kein Browsernachweis.

## Gegenproben und Wirkung

[test_ci_scope.py](../tools/test_ci_scope.py) erhält die bisherigen Inhalts-,
Modus-, Rename-/Delete-, Main- und Gateprüfungen.
[test_ci_a.py](../tools/test_ci_a.py) ergänzt die exakte #241-Dateimenge,
Positivlisten-/gemeinsame Abhängigkeiten, Vorlage, UI, getrennte und gemeinsame
Webwege, alle manuellen Scopes sowie manipulierte Auswahl-/Run-/Outputbindung.
Ein echter temporärer Gitverlauf beweist, dass ein späterer Dokumentcommit die
frühere Löschung/Umbenennung einer Zustellungsdatei nicht verdeckt.

Unter Linux werden die tatsächlichen Shellblöcke beider Webworkflows mit
protokollierenden synthetischen Außenwerkzeugen ausgeführt. Die Probe verlangt
genau einen regulären Export ohne Browserbefehle für Zustellung und drei Exporte
samt vollständigen Browserbefehlen ohne SSH für Web. Injizierte Build-/Prüffehler
müssen Exit 23 weitergeben. `CI_A_EXECUTION_PROBE` im Tooltestlog hält die
ausgeführten Befehle fest. Das ist eine synthetische Ausführungsgegenprobe;
echte Browser-/SSH-Aussagen liefert der vollständige Implementierungs-PR-Lauf.

Für #241 und reine Fachfälle entfallen damit native Productausführung, sämtliche
Webexports, Browserinstallation/-routen und SSH-Referenz; die vollständige
Fachsuite bleibt. Für die einzelne Vorlage entfällt auch die Fachsuite. Ein
reiner Zustellungsfall führt einen statt drei Exporte aus und startet keine
Browser. Der Implementierungsdiff selbst wählt alle sechs Bereiche. Gemessene
Jobzeiten und Artefakte im PR unterscheiden reale Ausführung, synthetische
Gegenprobe und historisches Vergleichsbeispiel; aus Flagzahlen wird keine
Minutenersparnis oder zukünftige Runnerlaufzeit behauptet.
