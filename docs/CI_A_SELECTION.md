# CI-A: Ausführbare Prüfauswahl

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

Die nachfolgende serielle Webausführung beschreibt den gebundenen CI-A-Lieferstand.
[CI-B](CI_B_BROWSER_GROUPS.md) ersetzt sie durch unabhängige Gruppen, zwei
Browserrunner und zusätzliche Szenarien-/Belegprüfung. CI-A-Auswahl, Zustellung
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
