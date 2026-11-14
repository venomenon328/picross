# Fachmodule und manueller Diagnosepfad

## Auswahl in der Haupt-CI

[Package CI](CI_WORKFLOW_V2.md) verwendet ausschließlich den aktuellen
`.ci/package.json`. Die alten Pfadzuordnungen in `ci_scope.py`, `native_contract.py`
und `production_contract.py` starten dort keine zusätzlichen Module. Sie bleiben
Hilfen zur Abhängigkeitsanalyse und Teil des ausdrücklich manuellen Diagnosewegs.
Auch gemeinsame oder unbekannte Pfade verlangen eine begründete Paketentscheidung,
keine automatische Vollauswahl. Der Quellen-/Plankern gilt für alle PRs; reine Dokumente und reine Rätselproduktion bleiben ohne Windowsbau.

## Fachgruppen

| Paketmodul | Ausführbarer Bereich |
| --- | --- |
| `production.solver` | Solver, unabhängige Verifier, Analyse/Rating und sechs feste synthetische Mono-/Farbreferenzen |
| `production.images` | Bildimport, Paarproduktion, Reparatur und synthetische RP6-Regressionen |
| `production.adapter` | Authoring-Paketbuilder, Zieladapter und unterstützte Ableitungswege, einschließlich synthetischem ZA-1-Durchstich |
| `production.catalog` | Kategorien, Inhalts-/Bild-/Bewertungs-/Hinzugefügt-Daten, Transaktionen, Recovery und Registrierungsbudgets |

[production_contract.py](../tools/production_contract.py) ordnet jedes aktive
Fachtestmodul genau einer Gruppe zu und benennt zugehörige Integrationen.
[production_ci.py](../tools/production_ci.py) prüft tatsächliche Discovery gegen
Quelldeklarationen und führt genau die angeforderten Gruppen aus. Fehlende,
unbekannte oder doppelte Tests, übersprungene Fälle und fehlgeschlagener Aufbau
sind kein Erfolg. Die Import-/Konsumentenzuordnung dient der nachvollziehbaren
Auswahl; neue Quellen erhalten keine bloße Präfixausnahme.

Der unabhängige [Ergebnisleser](../tools/production_results.py) prüft Originalberichte,
tatsächliche Test-IDs, Gruppen, Integrationen, nichtleere Logs/Proofs und Datei-/
Bytehashes samt Head, Basis, Checkout, Run und Versuch. Package CI ruft ihn im
selben erzeugenden Job auf; anschließend werden temporäre Originale verworfen.
Vor dem Aufruf stellt der Paketrunner eine temporäre kompakte Belegansicht nach
dem bestehenden Producerinventar bereit. Interne synthetische ZA-1-Checkouts
bleiben Arbeitsdaten; der unveränderte Reader prüft die Originalbelege weiterhin
exakt gegen deklarierte Dateiliste, Hashes und Pflichtumfang.
Nur eine aktuelle befristete Evidenceanforderung bewirkt einen technischen Upload.
In Package CI läuft jede angeforderte Fachgruppe auf einem eigenen isolierten
Runner; ihr vollständiger Producer/Reader bindet weiterhin denselben Gesamtplan,
Quellhead und Testmerge. Test- und Fixturebeginn/-ende sowie 30-sekündige echte
Operationszähler stehen live im Joblog. Die Trennung verändert weder Discovery
noch Prüfinhalt und benötigt keinen technischen Transport zwischen Jobs.
Ein positives Joblabel oder eine leere Gruppe ersetzt diese Prüfung nicht.

Alle Fachtests verwenden feste synthetische Eingänge. Der echte Katalog wird
nicht analysiert, neu zertifiziert oder zum wachsenden Testkorpus. Inhaltsprüfung
bleibt im Produktionsauftrag; ein ausdrücklich angeforderter Windowsbau ist keine Inhaltsabnahme.

## Ausdrücklich manueller Diagnoseweg

[ci-chromium.yml](../.github/workflows/ci-chromium.yml) hat ausschließlich
`workflow_dispatch`. Seine sichtbaren Checks heißen `Diagnostic selection` und
`Diagnostic result`; die alten internen Job-IDs bleiben kompatibel. Er ersetzt
kein aktuelles Package-CI-Gate und läuft weder bei PR/Push noch als Main-Nachlauf.

| Dispatchinput | Wirkung |
| --- | --- |
| `scope=auto` | Bisherige Nichtbrowser-Pfadauswahl des gebundenen Dispatchvergleichs |
| `scope=native-<gruppe>` | Zusätzliche benannte native Gruppe |
| `scope=runtime` | Native core/history/catalog/completion/export |
| `scope=visual` oder `perf-b` | Native core/graphics/export |
| `scope=production` | Breiter Fach-/Native-/Zustellungsumfang |
| `scope=all` oder `toolchain` | Alle Nichtbrowserbereiche einschließlich Preflight/Zustellung |
| `browser_scope=none` | Kein Browser, auch bei allgemeinen Vollscopes |
| `browser_scope=regular/catalog/input/completion/persistence/short/all/export` | Nur der ausdrücklich gewählte [Chromiumumfang](CI_B_BROWSER_GROUPS.md) |

Scopes dieses alten Diagnosewegs erweitern dessen Nichtbrowserauswahl. Bei leerem
Dispatchdiff und `scope=auto` startet nur ein ausdrücklich gewählter Browserumfang
neben Auswahl/Gate. Ein Dispatch testet seinen Branchcommit, keinen PR-Test-Merge.
Für einen begrenzten aktuellen Nichtbrowserlauf ist die manuelle Modulauswahl von
Package CI vorzuziehen. Diagnosezweck, Umfang und erforderliche temporäre Belege
im Auftrag festhalten; kein routinemäßiger Vollaufruf zur Absicherung kleiner Diffs.

Der Diagnoseweg behält `picross-ci-selection-v6`/`picross-ci-result-v6`, kanonische
Gruppenoutputs und den ursprünglichen Event-/Dispatchinputschutz. Das Gate bindet
exakte Base-/Head-Trees, Checkout und Originalergebnisse aus demselben Run.
Rename/Delete berücksichtigt beide Seiten. Erfolgreiche Jobs dürfen nur bei
passender Quelle im selben Run wiederverwendet werden; Auswahlversuch ≤
Producerversuch ≤ Gateversuch. Fehlende/fehlerhafte ausgewählte Ergebnisse bleiben rot.

Anders als die Haupt-CI überträgt dieser explizite Diagnoseweg Belege zwischen
Jobs: Auswahl/Ergebnis, gebundene Fach-/Native-/Browserberichte und benötigte
Builds. Technikretention sieben Tage, tatsächlich angeforderte Spieler vierzehn.
Diese ausführbare Kompatibilitätsroute ist kein Grund für automatische Uploads
in Package CI. Alte deaktivierte Workflowketten oder historische Reruns werden
nicht reaktiviert; aktuelle Workflows laufen unter den vorhandenen aktiven IDs.

## Historische Herkunft

[CI2-B-T01](CI2_B_VERIFICATION.md) dokumentiert die Einführung der Fachgruppen.
Der vollständige [CI-A-Verlauf vor v2](https://github.com/venomenon328/picross/blob/f3626f28899a48fa4d783716925f7425a3eb1784/docs/CI_A_SELECTION.md)
enthält frühere v4/v5-Schemata, automatische Auswahl, Firefox-/33-Fall-Matrizen
und damalige Liefergates. Diese Beschreibungen werden nicht als heutige Regeln
fortgeführt. Aktueller Testlebenszyklus: [CI_CONTRACT](dev-rules/CI_CONTRACT.md).
