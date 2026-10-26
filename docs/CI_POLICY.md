# Aktuelle CI-Policy

**Auftragsspezifische Ausführungssperre #406 / PR #411 · 26.10.2026:** Der
Eigentümer untersagt den Web-Job für diesen Auftrag. Ausschließlich bei
`pull_request.number == 411` sperrt der Scheduler diesen Job trotz automatischer
Auswahl. Andere PRs und alle übrigen Jobs behalten ihre Bedingungen. Selektor,
Browserumfang und `ci-required` bleiben unverändert: ausgewähltes, übersprungenes
Web ist ein fehlender Pflichtnachweis und ergibt keinen vollständigen CI-Pass.
Diese Sperre erteilt weder eine Mergefreigabe noch eine Ausnahme vom finalen
Gesamtgate. [F01/T01](SD2_D_ADOPTION.md) bindet tatsächliche Ausführung und Lücke.

**SD2 · 25.10.2026:** [Der freigegebene Sollvertrag](PUZZLE_DIFFICULTY_V2.md)
ändert keine automatische Prüfauswahl. Referenz-/Validierungssätze und allgemeine
Regressionen bleiben unabhängig synthetisch; echte Katalogfälle, daraus kopierte
oder abgeleitete Fälle und Bestandsverteilungen werden keine CI-Tests. Der reale
0.4-Vergleich, Übernahme und Aktivierung gehören ausschließlich zum gesonderten
manuellen Inhaltsauftrag SD2-D. Reine Spezifikationspflege nutzt Docs/Werkzeugtests,
Dokumentvalidator, Diffcheck und `ci-required`; spätere A/B/C/D-Diffs folgen der
vollständigen bestehenden Auswahl, ohne pauschale SD2-Ausnahme.

Stand: 19.10.2026 · Version 2.6 · CI-Spezifikation [#246](https://github.com/venomenon328/picross/issues/246), bestehende Aufträge [#63](https://github.com/venomenon328/picross/issues/63), [#70](https://github.com/venomenon328/picross/issues/70), [#116](https://github.com/venomenon328/picross/issues/116), [SD-Vertrag](PUZZLE_DIFFICULTY.md) und [AT-Spezifikation](REVEAL_TRANSPARENCY.md)

## Geltung und Ablösung

Der Eigentümer hat nach der Analyse vom 09.10.2026 die CI-Bereinigung und diesen
Prüfumfang zur Umsetzung freigegeben. Diese Policy ersetzt für neue Änderungen
die früheren pauschalen Pflichten, sämtliche sechs Jobs, historische Studien,
Vorherprojekte und vollständige Reviewgalerien bei jedem PR neu zu produzieren.
Sie gilt auch dort, wo Projektprofil, ältere Paketbeschreibungen oder historische
Prüfberichte noch den damaligen Vollumfang nennen. Fachliche Produktverträge,
gezielte aktuelle Abnahmen und die Zuordnung zum tatsächlichen Quell-/Basisstand
bleiben verbindlich. Historische Berichte behalten ihr damaliges Urteil.

Die [Eigentümerentscheidung N70-HIST-01](https://github.com/venomenon328/picross/pull/71#issuecomment-6111613992)
löst historische PERF-A-Herstellung/Reproduktion, Altzeichnerproben und A/B-
Vergleichsrekonstruktion als aktuelle Pflichten ab. R1/B-01 ist supersediert.
Die sechs produktiven Atlanten und sämtliche aktiven Runtimeverträge bleiben.
Es gibt keinen PERF-A-CI-Schalter und kein getarntes historisches Laufzeitbudget.

Der Abschlussstatus für Pull Requests heißt `ci-required` im Workflow
[CI verification](../.github/workflows/ci-chromium.yml). Er verlangt tatsächlichen
Erfolg aller ausgewählten Bereiche. Fehler, Abbruch, fehlende Auswahl und
übersprungene erforderliche Jobs sind kein Pass. Nichtzutreffen wird mit
Änderungsauswahl und Grund ausgewiesen. Es wurde kein Branchschutz verändert.

## Chromium als einzige CI-Browserpflicht

Eigentümerentscheidung vom 19.10.2026 in
[#261](https://github.com/venomenon328/picross/issues/261): Firefox entfällt
vollständig und dauerhaft aus automatisierter CI. Chromium behält sämtliche
27 Szenarien in `regular`, `catalog`, `input`, `completion` und `persistence`,
einschließlich KU-B, Live-DPI, echter IndexedDB-Sicherung, Reload, Prozessneustart,
zweitem Export, Fehler-/Recoveryfällen und allen bisherigen Pflichtdateien.
Diese Entscheidung ersetzt auch noch formulierte Firefox-CI-Pflichten in
älteren Paket-/Prüfzuordnungen. Historische Nachweise behalten ihre damalige
Commit-, Browser- und Runbindung; sie werden weder umgeschrieben noch als
aktuelle Chromium-Nachweise ausgegeben. Spielverhalten, Browser-Saves, Windows,
Godot und Deployment ändern sich dadurch nicht.

`browser-chromium.yml` weist jeden Browserwert außer `chromium` im ersten Schritt
vor Installation ab und installiert ausschließlich Chromium. `run_groups.py`,
`browser.py` und `smoke.py` akzeptieren ebenfalls ausschließlich `chromium`;
die direkten Runner-/Launchwege prüfen dieselbe Positivliste. Das Ergebnisgate
verlangt nur `chromium_attempt` und Chromium-Artefakte, bleibt aber vollständig
fail-closed für Gruppen, Szenarien, Quell-/Run-/Versuchsbindungen und Dateiinhalt.

Eigentümerentscheidung S3 in #261 ersetzt die frühere historische Rerun-
Garantiepflicht: Alte Runs und ihre theoretische Wiederholbarkeit sind kein
Mergegate. Sie bleiben unverändert und werden nicht erneut gestartet.
Firefox-Prozesse, neue Firefox-Jobs und die Reaktivierung der alten IDs bleiben
ausnahmslos verboten. Vor Wiederfreigabe sind die aktuellen automatischen
Startpfade einschließlich offener PRs zu prüfen; historische Rerun- oder
Supportgarantien sind dafür nicht erforderlich.

Die neue Kette verwendet eigene Dateipfade und GitHub-Workflow-IDs:
`ci-chromium.yml` → `web-chromium.yml` → `browser-chromium.yml`.
Die alten IDs `364105131` (`setup.yml`), `385932454` (`web.yml`) und
`388435392` (`web-browser.yml`) bleiben administrativ `disabled_manually`.
Die alten Dateien sind im neuen Tree entfernt; lokale Aufrufe und Pflichtdatei-
prüfungen verwenden ausschließlich die neue Kette. Die übrigen aktiven
Workflows dürfen weder Firefox installieren/starten noch alte Webketten aufrufen.
Neue Änderungen an automatischen Startpfaden müssen diese Grenze erhalten.

Nach Quellenprüfung und Zurücklesen der Sperren darf der autorisierte
Administrator Actions kontrolliert wieder aktivieren. Der erste Vor-Merge-Lauf
verwendet ein neues `pull_request`-Ereignis und dessen tatsächlichen Test-Merge;
kein historischer Rerun und kein Dispatch einer noch nicht auf dem Defaultbranch
registrierten Datei. Neue registrierte IDs, Ereignis, Head/Basis/Test-Merge und
Originalbelege werden in #261/PR #262 dokumentiert. Fehlende Registrierung oder
Ausführung ist ein technischer Blocker, kein Ersatz-Pass. `ci-required` und alle
automatisch ausgewählten Pflichtchecks bleiben unverändert verbindlich.

## Freigegebene CI-Straffung

Eigentümerentscheidung vom 18.10.2026:
[#246](https://github.com/venomenon328/picross/issues/246) ist als Spezifikation
freigegeben. Ziel ist eine deutlich kürzere notwendige Wartezeit durch passende
Prüfauswahl und schnellere Ausführung. **CI-A, CI-B und CI-C sind implementiert;
CI-C-T01/R01 und Merge bleiben separat im Paket-PR gebunden.** Die folgenden Entscheidungen sind verbindlich;
sie erlauben vor Integration des jeweiligen Pakets kein Überspringen eines
derzeit ausgewählten Pflichtchecks. Ausgangsbasis ist
`main@72ba39391833f6fd834d0a6afaf881c86c7bdc3a`; konkrete Lieferstände und Messungen
stehen in den Paket-Issues/PRs, nicht als laufende Chronik in dieser Policy.

### Pakete und Wirksamkeit

| Paket | Eigenständig abnehmbarer Umfang | Wirksamkeit |
| --- | --- | --- |
| [CI-A · Prüfbedarf auswählen (#247)](https://github.com/venomenon328/picross/issues/247) | Enge Fach-/Vorlagenzuordnung; Product, Browser und SSH/HTTP-Zustellung unabhängig auswählen und ausführen; vollständiges Ergebnisgate | Zuerst. Danach bleiben alle weiterhin ausgewählten Browserrouten bis CI-B vollständig. |
| [CI-B · Webprüfungen aufteilen und beschleunigen (#248)](https://github.com/venomenon328/picross/issues/248) | Regulärer Start und unabhängige Browsergruppen; Chromium auf eigenem Runner (Browserpflicht gemäß #261); feine Messung und belegte Harnesskorrektur | Nach integrierter CI-A. Erst danach gilt die selektive Browser-Szenarienauswahl. |
| [CI-C · Native Produktprüfung straffen (#249)](https://github.com/venomenon328/picross/issues/249) | Native Gruppen entkoppeln; Bildkosten messen und verlustfrei beschleunigen | Nach CI-A. CI-B davor ist empfohlen, keine technische Voraussetzung. Erst CI-C ersetzt die native Integrationskopplung. |

Standard ist ein Implementierungs-PR je Paket einschließlich Tests und
Dokumentationsfortschreibung. Ein reiner Spezifikations-PR ist eine getrennte
Dokumentlieferung und nimmt kein Implementierungsgate ab. Technische Startprüfung
und gegebenenfalls Modellauswahl gehören zur späteren Umsetzungsvorbereitung.

### Gezielte Auswahl

Productbedarf impliziert nicht pauschal Browserbedarf; Browserbedarf
impliziert nicht pauschal eine SSH-Referenz. Die ausführbare Zuordnung samt
Abhängigkeitsprüfung und manuellen Scopes steht in [CI-A-Auswahl](CI_A_SELECTION.md).
Grundlage sind geprüfte gemeinsame Abhängigkeiten und die Vereinigung aller
geänderten Bereiche.

| Änderungsbezug | Freigegebene Zuordnung |
| --- | --- |
| Geprüfte reine Analyse-/Solver-/Bewertungsmodule, fachliche Konfigurationen und synthetische Tests | Nur `docs` und `production`; keine pauschale Ausnahme für ganz `tools/puzzle_production/`. Gemeinsame Runtime-/Schema-/Export-/Harnesshelfer bleiben entsprechend breit. |
| Ausschließlich vorhandene `.github/pull_request_template.md` | Dokument-/Werkzeugtestpfad und `ci-required`; keine Ausnahme für andere `.github/`-Dateien oder Workflows. |
| Browserrelevante Runtime-/Darstellungsänderung | Bis CI-B vollständige bisherige Browserroute; nach CI-B regulärer Start und sämtliche betroffenen Gruppen in Chromium. |
| Reine Deploy-/SSH-/HTTP-Zustellungsänderung | Eigenständig ausführbare Referenz mit benötigtem regulärem Bündel, ohne Browserinstallation/-start und ohne sachfremde technische Browserexporte. |
| Gemeinsame UI-, Save-, Ressourcen-, Bündel-, Export-, Harness- oder Toolchainwirkung | Mehrere beziehungsweise alle betroffenen Bereiche; keine bloße Pfadnamensannahme. Insbesondere `game/ui/main.gd` ist keine reine Katalogausnahme. |
| Unbekannte Wirkung oder gemischter Diff | Konservativ umfassende Prüfung beziehungsweise Vereinigung aller Pflichten. |

Der vollständige exakte Base-/Head-Diff, Rename-/Löschungsseiten und der
Inhalts-Dateimodusschutz bleiben erhalten. Keine Auswahl nur aus dem letzten
Commit, kein neuer Base→Test-Merge-Vergleich und keine Wiederverwendung alter
Prüfergebnisse. Manuelle Scopes erweitern ausschließlich. CI-A dokumentiert die
Semantik aller vorhandenen Scopes ausdrücklich; das Entfernen der bisherigen
Transitivität darf keine beabsichtigte manuelle Prüfung verlieren.
`all` und `toolchain` umfassen auch die eigenständige Zustellung.

Reine Inhalte und Dokumente behalten ihre bestehenden kurzen Pfade. Der
automatische Main-Nachlauf wiederholt Product, Browser, SSH und Preflight nach
einem Merge nicht; die PR-/Test-Merge-Bindung bleibt maßgeblich. Der bestehende
Abbruch überholter PR-Läufe bleibt. Weder Nachtläufe noch neue geplante Automation,
Caches für Ergebnisse, neue CI-Infrastruktur oder Live-Deployment gehören dazu.

### Ausführbare Browsergruppen (CI-B)

[CI-B-Gruppenvertrag](CI_B_BROWSER_GROUPS.md) dokumentiert Inventar, genaue
Abhängigkeiten, unabhängige Voraussetzungen, Runner und Fail-closed-Belegprüfung.
Vor Integration von CI-B bleibt auf `main` die vollständige bisherige Route aktiv.

Die logischen Gruppen sind unabhängig startbar; ihre Benennung legt keine
bestimmte CLI oder Anzahl von Jobs fest:

| Gruppe | Erhaltene Aussage |
| --- | --- |
| Regulärer Start | Uninstrumentierter Spielerexport startet und erreicht den bestehenden Startzustand in Chromium. |
| Katalog/Darstellung | Aktuelle Katalog-, Metadaten- und Darstellungsfälle mit den geforderten Zustands-/Bildbelegen. |
| Eingabe/Geometrie | Echte Zeigeraktionen, Gesten und relevante Fenster-/Zoom-/Geometriefälle einschließlich ausdrücklich browserspezifischer Gegenproben. |
| Abschluss/Reset | Echte Abschlüsse, Animation/Abbruch, Bestätigung und Reset; keine Verkürzung des Produktvertrags. |
| Persistenz/Lifecycle | Echte IndexedDB-Sicherung, Reload, Prozessneustart, Exportwechsel, Sperren, Fehler/Recovery, Revisionen, Offline- und Beenden-Verhalten. |

Vor der Aufteilung wird jede aktive positive/negative Prüfaussage einschließlich
technischer Startvoraussetzungen und Pflichtartefakte zugeordnet. Der vollständige
Browserlauf ist die Vereinigung aller Gruppen; SSH gehört nur bei eigenem
Änderungsbezug dazu. Jede ausgewählte Gruppe besitzt kontrollierte synthetische
Voraussetzungen, ohne von einer vorherigen Gruppe abzuhängen. Vorbereiteter
Speicher ersetzt keine zu prüfende echte Eingabe oder Persistenz.

Chromium läuft auf einem eigenen Runner mit getrennten Profilen, Ports,
veränderlichen Hosting-/Releaseverzeichnissen und Reports je Gruppe, aus
auf denselben geprüften Quellstand gebundenen Builds. Sämtliche bisherigen
Chromium-Szenarien bleiben erforderlich. Reale Reloads, Browserprozess-Neustarts
und zwei eigenständig erzeugte Exporte bleiben in den relevanten Fällen Pflicht. Ein
umbenannter Export oder ein Starttest allein ersetzt diese Nachweise nicht.
Der [Webvertrag](WEB_HOSTING.md) konkretisiert Isolation und Speichergrenzen.

### Ausführbare native Gruppen und Bildaufbereitung (CI-C)

[CI-C-Gruppenvertrag](CI_C_NATIVE_GROUPS.md) und das ausführbare Inventar ordnen
Kern/Save, History/500er-Route, Katalog, Abschluss, Adapter/Piloten, Grafik/Atlas
und Export ausdrücklich zu. Der Gesamtlauf vereinigt alle aktiven
Checks, Orakel und Belege. Katalog und Abschluss hängen nicht mehr allein am
500er-Integrationsschalter; gemeinsame Abhängigkeiten wählen weiterhin mehrere
oder alle Gruppen. Keine Entfernung allein wegen eines historischen Testnamens.

Gruppen verwenden getrennte temporäre Projekte, Profilwurzeln und Ausgaben.
Absichtlich gemeinsame Profile und die nötige Prozessreihenfolge innerhalb
echter Neustart-/Save-/Reset-/Slotprüfungen bleiben erhalten. Eingabe und Fokus
begrenzen Parallelität; unabhängige CLI-Schalter allein beweisen keine Isolation.

Rendering, Lesen/Zuschneiden, PNG-Schreiben, Verpacken und Upload werden getrennt
gemessen; Eingangsframes, Ausschnitte und tatsächlich gelieferte Dateien/Bytes
werden gezählt. Schnellere Bildaufbereitung muss auf denselben nativen Frames
identische dekodierte RGBA-Pixel einschließlich Alpha, Maße, Ausschnitte und
Pflichtbildmenge liefern. Andere verlustfreie PNG-Datei-Bytes sind zulässig;
Skalierung, Ersatzbilder oder fehlende Pflichtausschnitte sind es nicht.

### Ergebnisgate, Messung und Abnahme

`ci-required` bleibt der stabile Abschlussstatus. Auswahl und Berichte müssen
erwartete/tatsächliche Bereiche, nach ihrer Einführung auch Gruppen und Szenarien
je Browser, Quell-/Runbindung und Pflichtbelege vollständig zuordnen. Fehlende,
leere, doppelte, falsche, fehlgeschlagene, abgebrochene oder unzulässig übersprungene
Pflichtresultate sind kein Erfolg. Ein nicht erforderlicher Bereich wird als
solcher begründet, nicht als erfolgreich ausgeführt ausgewiesen.

Webmessungen trennen je Szenario Start/Navigation, Zustandsabfragen, Eingaben,
Save/Bestätigung, Wartephasen und Screenshots. Native Messungen trennen die
Bildphasen. Vergleichbare Produkt-/Fixture-/Toolchain- und Runnerbedingungen
sowie Warm-/Kaltzustand werden genannt. Warteschlange, Jobdauer, summierte
Rechenzeit und paralleler kritischer Pfad bleiben unterscheidbar. Ursachen und
erreichte Verkürzungen müssen gemessen sein; theoretische Parallelitätsgewinne
oder weniger Auswahlflags genügen nicht. Keine festen Minuten-/Bytebudgets
und keine kürzeren Timeouts als Optimierungsersatz.

Jedes Paket erhält eigenes CI-A-/CI-B-/CI-C-T01: tatsächliche ausgewählte
technische Checks, gezielte Gegenproben, Quellen-/Runbindung und getrenntes
Selbstreview durch den Implementierer. Das jeweilige R01 ist ein separater
qualifizierter Review des finalen Heads. Beide Gates liegen vor Merge.
Bestehende Windows-/Eigentümergates und aktuelle Spiel-/Speicherverträge bleiben
eigenständig; ein reiner CI-Umbau erzeugt kein neues persönliches Probespielgate.
Insbesondere bleiben die gezielten KU-Verhaltensnachweise aus
[#244](https://github.com/venomenon328/picross/issues/244) in Windows und Chromium
erforderlich; die frühere Firefox-CI-Pflicht entfällt gemäß #261. Bloßer Start
genügt dafür nicht.

## Einmalige Inhaltsprüfung und feste Regressionen

Eigentümerentscheidung vom 12.10.2026: Rätsel werden bei ihrer Erstellung und
gezielten Integration vollständig geprüft; diese Prüfungen werden **kein Teil
der CI**. Nachweise bleiben bis zur finalen Integration dateigebunden im Produktionspaket;
danach gilt die Bereinigung aus PUZZLE_AUTHORING §9. Änderungen an
Raster/Quelle verlangen die im [Regelwerk](ai-workflows/PUZZLE_AUTHORING.md)
bestimmten Neuprüfungen außerhalb der CI. Das gilt auch bei späteren Codeänderungen:
keine routinemäßige Neuzertifizierung vorhandener Rätsel.

Für reine Inhaltsintegration gilt [PUZZLE_AUTHORING §8](ai-workflows/PUZZLE_AUTHORING.md):
Adapterexport, Registrierungsplan/-transaktion und Kontrolle der übernommenen Dateien
genügen. Keine obligatorischen nativen Spiel-/Neustart-/Render-/PCK-Tests oder
Spielerbuilds außerhalb der CI je Rätsel. Zusätzliche Proben nur bei konkretem
Befund; keine doppelten manuellen Adapter-/Bestands-Replays. Allgemeine Regressionen
bei relevanten Codeänderungen bleiben unverändert.

Keine rätselspezifischen Unit-Tests oder Testgenerierung aus dem Produktionsfundus.
F01/F02-Zertifikatstests, reale RP-/VS-Korpus-Replays, der Knoblauch-Referenztest
und deren CI-Jobs sind entfallen. Historische Daten/Proofs müssen nicht im aktiven Tree erhalten bleiben.
Allgemeine Solver-, Verifier-, Import-, Reparatur- und Adaptertests verwenden feste
synthetische Eingänge; Registrierungstests kopieren keine produktiven Pakete.
Sämtliche nativen Funktions-/Renderläufe verwenden einen festen temporären
Katalog; zusätzliche produktive Runtime-Inhalte werden nicht hineinkopiert.
Erst für den regulären Spielerexport werden die tatsächliche Registry und ihre
Runtimeassets übernommen, ohne Rätselzertifizierung. Paketgröße/Build-I/O dieses
Code-Prüfwegs können mit dem Spiel wachsen; die Testmatrix wächst nicht.
Save- und PCK-Funktionstests nutzen feste technische Beispiele statt einer Schleife
über jeden neuen Katalogeintrag. Bestehende Motive als feste Eingabe allgemeiner
Spiel-/Darstellungstests sind keine erneute Rätselzertifizierung und werden bei
Inhaltserweiterungen nicht ergänzt.

## AT · Bildrevisionen und einmalige Bestandsumstellung

Eigentümerentscheidung vom 19.10.2026:
[AT / #256](https://github.com/venomenon328/picross/issues/256) und der
[Transparenzvertrag](REVEAL_TRANSPARENCY.md) sind als Spezifikation freigegeben;
AT-A-P01 ist mit PR #257 integriert. Umsetzungsvorbereitung V3 beauftragt
ausschließlich AT-A samt T01 und Draft-PR; AT-B bleibt unbegonnen. Die reine
Spezifikationslieferung blieb auf dem Dokument-/Werkzeugtestpfad mit
Dokumentvalidator, vollständigem Diffcheck und `ci-required`.

AT-A liefert den gemeinsamen Bildrevisions-/Transaktionsweg und feste
synthetische Regressionen für Alpha-Erhalt, helle Motivteile, Aussparungen,
Darstellung, unveränderte Saves/Definitionen und binäre Wiederherstellung.
Register-/Update-/Sync-/Bewertungs-/Added-/Export-/Recoverywirkung wird anhand
des tatsächlichen Gesamtdiffs ausgewählt; kein pauschaler Kurzpfad für
Produktionswerkzeug- oder CI-Code. Bestehende Pflichtchecks und getrennte
qualifizierte Paketreviews bleiben. AT ändert keine Plattformmatrix und
überträgt keine früheren paketbezogenen Ausnahmen auf neue Lieferungen.

AT-B inventarisiert und prüft den tatsächlichen Bildbestand im ausdrücklich
beauftragten Inhaltsprozess außerhalb der CI. Neue Bildfreigabe, Motiv-/Raster-
konsistenz, Kanten-/Kontextsichtung und kontrollierte Dateiübernahme sind
Inhaltsnachweise, kein dauerhafter Katalog-Replay und kein obligatorischer
vollständiger Spieldurchlauf pro Rätsel. Bei unveränderter Definition gibt es
keine neue Logik-/Proof-/Schwierigkeitsproduktion allein wegen der Bildrevision.

Ein ausschließlich aus zugelassenen Inhaltsdateien bestehender Bild-PR nutzt
weiterhin die enge Pfad-/Dateimodusprüfung und `ci-required`. P01 legt die spätere
Erweiterung exakt auf `content/reveals/pz-[a-z0-9][a-z0-9-]{0,59}.json` fest,
ausschließlich kanonische registrierte IDs und regulärer nicht ausführbarer
Dateimodus 100644. Kein weiterer AT-Unterpfad, Freitext-, Bildfreigabe-, Journal-
oder Tempnamensraum. Alias-/Fremdpfad-/Modus-/Rename-/Löschungsgegenproben gehören
zu AT-A; die Auswahl prüft beide Diffseiten. Registrierung und Datenvalidierung
prüfen zusätzlich die tatsächliche ID-/Quellenbindung; der reine CI-Inhaltspfad
behauptet keine Bild-/Freigabevalidierung. Neue SD-v3-/Added-v2-Berichte bleiben
an den bestehenden engen Berichtpfaden. P01 spezifizierte diese Positivliste;
AT-A implementiert sie mit positiven und negativen Scopeproben. Dokument-/Codebeimischungen
folgen der bestehenden Vereinigung aller betroffenen Prüfbereiche. Die Anzahl
allgemeiner Regressionen wächst nicht mit den umgestellten Katalogbildern.

AT-P01 verwendet allein Dokumentvalidator, vollständigen Diffcheck und den
tatsächlich automatisch ausgewählten Docs-/Werkzeugpfad einschließlich
`ci-required` auf aktuellem Head/Test-Merge. Keine Produkt-/Windows-/Browser-/
Solver-/Bestandsläufe allein wegen dieses Dokumentabschlusses und keine manuelle
Unterdrückung automatisch erforderlicher Jobs. Die integrierte Chromium-Kette
und der Leergruppenfix aus #258/#259 bleiben vollständig wirksam; historische
fehlgeschlagene Runs werden nicht rückwirkend zu Erfolgen. Die spätere
[AT-Prüfzuordnung](REVEAL_TRANSPARENCY.md) bindet synthetische Quellen-/Recovery-
fälle und tatsächliche native Windows-/Chromium-Darstellungs-/Savewechsel.
Kein neues P01-Produktgate und kein AT-A-M01; T01 und separates R01 bleiben
vor dem späteren Implementierungsmerge, konkrete Bestandsbildabnahmen in AT-B.

## SD · Manuelle Schwierigkeitsbewertung und Datenintegration

Eigentümerentscheidung vom 17.10.2026:
[SD](PUZZLE_DIFFICULTY.md) wird als ausdrücklich gestarteter Werkzeugprozess
außerhalb der CI ausgeführt. Keine Bewertung bei Commit, Merge, Build,
Spiel-/Katalogstart oder nach Zeitplan. Auch die erste Gesamteinstufung ist ein
gesonderter manueller Inhaltsauftrag; sie erzeugt keinen dauerhaften Replayjob.

Automatisierte SD-Regressionen verwenden ausschließlich feste synthetische
technische Eingänge. Der aktuelle Rätselkatalog darf weder direkt noch als
kopierter Snapshot oder zur Testgenerierung verwendet werden. Das gilt für
Solver-/Bewertungsfälle, erwartete Stufen, Verteilungsprüfungen und
Integrations-/Runtimeprüfungen; ein Umbenennen realer Rätsel macht sie nicht
synthetisch. Vorhandene allgemeine technische Regressionen bleiben erhalten.

SD-B bestimmt feste Schwellen anhand unabhängiger Referenzfälle. Der aktuelle
Katalog darf weder die Skalenenden direkt kalibrieren noch durch Quantile oder
bewusst veränderte Grenzen alle fünf Stufen besetzen. Seine spätere manuelle
Auswertung ist eine Plausibilitätsbeobachtung. Ein unbelegtes Extrem oder eine
verlangte Histogrammform ist kein Abnahmekriterium; unbesetzte Stufen sind zulässig.

SD-C1 erweitert die enge Inhaltspfad-Positivliste ausschließlich um:

- `content/difficulty/pz-[a-z0-9][a-z0-9-]{0,59}/rating.json`
- `content/difficulty/reports/[a-z][a-z0-9-]{0,63}/report.json`
- denselben Reportpfad mit `report.md`.

Nur reguläre nicht ausführbare Dateien sind erlaubt; keine beliebigen Unterpfade,
Endungen, Punktsegmente, Großschreibungsvarianten, Windows-Gerätenamen oder Links. Löschungen prüfen
auch den alten Modus; Umbenennungen zählen als Löschung plus Neuanlage.
Ein später reiner C2-Daten-PR wählt `content_only=true`: `docs` prüft ausschließlich
Pfad-/Dateimodus, danach `ci-required`. Die konkrete Bewertungsprüfung bleibt im
manuellen Auftrag nach [SD-C1](SD_CATALOG.md), nicht in CI.

Die C1-Code-/Loader-/CI-Änderung selbst wählt alle aktuellen Bereiche aus dem
vollständigen Base-/Head-Diff: docs, production, product, preflight, web und
ci-required; Product einschließlich integration/pilots/visual/perf_b. Die frühere
SD-B-Web-Ausnahme gilt nicht. Synthetische Auswahl-/Modus-/Rename-/Löschungsgegenproben
prüfen diese Trennung. Kein automatisierter Lauf analysiert reale Katalogrätsel.

## Auswahl nach vollständigem Änderungsumfang

[ci_scope.py](../tools/ci_scope.py) vergleicht die exakten Base-/Head-Dateibäume.
Umbenennungen zählen als alter und neuer Pfad; Löschungen werden mit erfasst.
Die beiden Commitobjekte werden gezielt flach geladen. Bei divergierter Basis
können zusätzliche Prüfungen ausgewählt werden; Basisänderungen werden dadurch
nicht versehentlich übersehen. Der tatsächliche Checkout bleibt der Test-Merge.
Auswahlbericht und Logs nennen Head, Basis, Checkout, Run und ausgewählte Pfade.
Der vollständige Auswahlbericht wird als Datei über das Artefakt desselben Laufs
an das Ergebnisgate übergeben. Joboutputs enthalten nur die Auswahlflags;
Umgebungsvariablen enthalten nur die sechs Jobergebnisse, Auswahlflags und
Quell-/Runbindung. Das Gate prüft die Auswahl erneut gegen die Pfadliste,
vergleicht die Scheduleroutputs und verlangt dieselbe Head-/Base-/Checkout-/
Run-/Eventbindung und die Versuchsbinding des Auswahljobs. Doppelte JSON-Schlüssel
sind ungültig. Auswahl- und Ergebnisartefakte tragen ihren jeweiligen Runversuch.
Bei einem Retry darf GitHub erfolgreiche Jobs desselben unveränderten Runs
beibehalten; der Auswahlversuch darf nicht nach dem Gateversuch liegen.
Andere Runs oder Quellstände sind nicht wiederverwendbar. Große Aufräum-PRs dürfen
nicht an Betriebssystemgrenzen für Argumente/Umgebungsvariablen scheitern; die
Pfadliste und die erforderlichen Prüfungen werden dafür nicht gekürzt.

Die Tabelle beschreibt die Bereichsauswahl nach CI-A. CI-C wählt native
Gruppen gemäß [nativem Gruppenvertrag](CI_C_NATIVE_GROUPS.md); CI-B wählt innerhalb
von Web gemäß [Browservertrag](CI_B_BROWSER_GROUPS.md).

| Änderung | Automatischer Pflichtumfang im PR |
| --- | --- |
| Nur neue/geänderte Rätselpakete, Registry/Kategorien und einzelne Runtime-Inhalte | `docs`: Pfad-/Dateimodusprüfung; `ci-required`: Ergebnisgate. Keine Tests, Rekonstruktion, Bilder oder Exporte. |
| Reine normative Dokumentation/Anleitung | Schnelle Tooltests, Dokumentvalidator, vollständiger Diffcheck |
| Spielzustand, Eingabe, Save, History, Navigation | Aktuelle Kernregression, echte Prozess-Roundtrips, 500er-Route, aktuelle Pixelprüfungen und Spielerexport |
| Reine Stiftzeichnung/Capture oder aktive Buchassets | Kernregression, aktuelle Pixelprüfungen, PERF-B und Spielerexport |
| Reguläre Atlasanzeige/Cache/aktive Zelltexturen | Kernregression, aktuelle Pixelprüfungen, PERF-B und Export |
| Geprüfte reine Analyse-/Solver-/Bewertungsdateien | `docs` und `production`; genaue Positivliste und Abhängigkeiten in CI-A-Auswahl. |
| Einzelne `.github/pull_request_template.md` | Dokument-/Werkzeugtestpfad und `ci-required`. |
| Reine Deploy-/SSH-Dateien | `docs` und eigenständige `delivery` mit regulärem Export. |
| Produktionswerkzeug-/Adaptercode außerhalb der engen Positivliste, technische Fixtures oder Pilotprobes | Allgemeine Fachtests mit festen synthetischen Eingängen; ausgewählte allgemeine Spiel-/Pixel-/Exportregressionen. Keine echten Rätselreplays. |
| CI/Harness/Toolchain oder nicht zugeordneter Codepfad | Alle aktuellen Bereiche einschließlich Preflight |

Product, `web` (Browser) und `delivery` (SSH/HTTP) sind unabhängig ausgewählt.
Runtime-/Darstellungsänderungen wählen weiterhin Browser; native Ressourcenprüfer
können allein Product benötigen. Gemeinsame Bündel-/Export-/Hostingdateien wählen
Browser und Zustellung. CI-B verlangt regulären Start und alle betroffenen Browsergruppen.
Der reine Inhaltspfad bleibt ausgenommen.

**Schlanker Inhaltspfad:** Ausschließlich `content/categories.json`,
`content/registry.json`, kanonische `content/added/<pz-ID>.json`,
`content/authoring/index.json`/`README.md`,
`content/authoring/<pz-ID>/<Revision>/…`, `content/packages/<pz-ID>/<Revision>/…`,
`game/data/registry.json`, `game/data/content/<stem>.json` und
`game/art/content/<stem>.png|svg|txt` gemäß der engen Positivliste in `ci_scope.py`.
Pakete erlauben ausschließlich bekannte Dokument-/Bild-/ZIP-Endungen; keine
Code-, Workflow-, Importkonfigurations- oder gemeinsamen UI-Assetpfade.
Umbenennung/Löschung zählt auf beiden Seiten. Geänderte Symlinks, ausführbare
Dateien und Submodule werden im Inhaltspfad abgewiesen.

Dieser Pfad gilt für PR und Main-Push. Sparse-/Partial-Checkout lädt nur den
Auswahlprüfer; der Git-Treevergleich liest keine Paket-, Bild- oder Proofblobs.
`docs` startet weder Tooltests noch Dokumentbaumscan. Das abschließende Gate
verlangt trotzdem Erfolg und korrekte Nichtauswahl aller übrigen Jobs.
Der CI-Bericht behauptet ausdrücklich keine Inhaltsabnahme. Kein Solver,
Proof-Replay, Hashscan des Fundus, Godot, Screenshot, PCK-Export oder Artefaktpaket
pro Rätsel. Die Job-/Testanzahl ist unabhängig vom Fundus; Git-Metadaten und der
Änderungsbericht hängen weiterhin von der Anzahl geänderter Dateien ab.
Code/Dokumentation im selben PR oder ausdrücklich erweiterter Scope verlässt
den reinen Inhaltspfad. Allgemeine Dokumentprüfung überspringt die vier
rätselspezifischen Ablagebäume; gebundene Paketdokumente prüft die Produktion.

Dateien unter `docs/` sind nicht automatisch reine Dokumentation: Buchbilder,
Fontinputs und Manifeste gehören zum Produkt. Ebenso können Markdowndateien wie
`examples/rp4/SELECTION.md` hashgebundene Produktionsinputs sein. Diese Bereiche
werden vor der Dokumentabkürzung zugeordnet. Mehrere Änderungen vereinigen ihre
Pflichten. Manuelle Auswahl im Hauptworkflow erweitert den tatsächlichen Diff.

Aktive Markdowninputs des regulären Spielerpakets bleiben im kurzen docs-Pfad:
Ein schneller Tooltest ruft denselben `package_player()`-Pfad wie Product auf,
mit den echten `player_extras()`- und README-Quellen sowie kleinen EXE-Platzhaltern.
Er prüft die tatsächliche Verpackung und Quellbytes ohne Engine/Export. Fehlende
oder nicht nachgeführte verschobene Inputs lassen diesen Pflichtjob und damit
`ci-required` scheitern. Löschung/Umbenennung jedes tatsächlichen Markdownextras
werden gezielt negativ geprüft; es gibt keine zweite Paketinputliste.

Auf `main` bleiben die bisher üblichen Integritätsprüfungen aktiv: Dokumente und
bei relevanten Änderungen die Rätselproduktion. Product/Preflight werden nach
einem Merge nicht nochmals automatisch wiederholt; ebenso wenig der Browserlauf
und die eigenständige SSH-Referenz. Ihre maßgebliche Bindung ist
der PR-/Test-Merge-Lauf. Direkte Änderungen an `main` sind weiterhin nicht erlaubt.

## Aktuelle Produktregression

Der Pflichtjob [Webprüfung](../.github/workflows/web-chromium.yml) läuft bei
ausgewähltem Browserbedarf. Reine Inhalte wählen ihn
weiterhin nicht; Main-Merges veröffentlichen nichts. Ein Buildjob erzeugt den
regulären Spieler und zwei eigenständige feste technische Exporte. Der eigene
Chromium-Runner prüft den regulären Start und die ausgewählten Gruppen
samt allen zugeordneten positiven/negativen Szenarien und echter Browserpersistenz.
Die vollständige Vereinigung ist im [CI-B-Inventar](CI_B_BROWSER_GROUPS.md) gebunden.
Die [Zustellungsprüfung](../.github/workflows/delivery.yml)
baut unabhängig nur den regulären Spieler und prüft Loopback-OpenSSH/HTTP.
Sie installiert und startet keine Browser. Bei gemeinsamer Auswahl haben beide
Jobs eigene Runner, Ausgaben und Artefaktnamen. `ci-required` verlangt den
tatsächlichen Erfolg jedes ausgewählten Jobs, ohne Zustellung als Browsererfolg
auszugeben. Spielerdateien bleiben 14 Tage, kompakte Berichte/Bilder und
Fehlerlogs sieben Tage. Keine echten Saves, VPS-Zugangsdaten oder Testprofile im
Artefakt. [WEB-1-Anleitung und Abnahmegrenzen](WEB_HOSTING.md).

Der GPU-lose Linux-Webjob verwendet weiterhin Mesa-Software-Rendering.
Chromium-Berichte protokollieren Profiloptionen und den tatsächlich erzeugten
WebGL-2-Kontext. Die frühere temporäre Firefox-Profiloption entfällt mit dessen
CI-Runner. Der Spieler meldet weiterhin fehlende WebGL-2-Unterstützung.

Der [Product-Harness](../tools/p1_product.py) prüft die unveränderten aktiven
Ressourcenbindungen, importiert die temporäre reguläre
Spielkopie mit festem temporärem Testkatalog, führt die aktuelle Godot-Kernsuite einschließlich
Save/Recovery und ZS2-Verhalten einmal aus und prüft echten Mehrprozess-Save,
kontrollierten Start sowie den regulären Windows-Export. Der kurze absichtliche
Fehler durchläuft dieselbe `check()`-/Ergebnis-/Exit-23-Strecke wie die Suite.

Die native Regression verwendet ausschließlich den festen technischen Katalog aus
`tests/puzzle_production/fixtures/catalog/runtime.json`. `tools/product_fixtures.py`
erzeugt sechs synthetische Definitionen/Reveals nur in temporären Projekten.
Eingefrorene KAT-1-Saves behalten separate Definitionsinputs unter `game/tests/`.
Vor dem Spielerexport ersetzt der Harness die temporären Ressourcen durch den
Produktionsbestand. Echte Inhalte werden nicht erneut zertifiziert und erhalten
keine rätselspezifischen CI-Tests. Die einmalige Katalog-/PCK-Sichtung für #114
ist ein PR-Liefernachweis, keine neue Testmatrix.

CI-C verwendet `--groups core,history,catalog,completion,adapters,graphics,export`;
die Auswahl kann jede Gruppe unabhängig starten. Lokal ist die vollständige
Vereinigung Standard, CI übergibt die exakte Auswahl ausdrücklich. `history`
prüft 500 Aktionen in fünf echten Prozessen plus Neustart und unabhängigem
Python-Orakel. `adapters` prüft die synthetischen Muster T04/T06/T08/T09 vollständig;
T04 enthält dabei die einzigartigen bisherigen RP3-Assertions einschließlich
Pfadablehnung, Spoilergrenze und Bindung des verdienten Motivs. `graphics` enthält
die aktuelle native Renderprüfung und den regulären Atlasrenderer samt Cache-/
Invalidierungslebenszyklus. Die alten manuellen Flags bleiben ausschließlich als
erweiternde Kompatibilitätsauswahl erhalten; Details im Gruppenvertrag. Aktuelle Darstellung, Texturen und ihre
Referenz wählen PERF-B; CI/Harness/Toolchain wählen alle aktuellen Bereiche.

`tools/perf_b_resources.py` prüft exakt sechs aktive PNGs samt Importdateien,
Dateihashes, RGBA8-Maßen, Speicherobergrenze und Importparametern gegen die eigene
`tools/cell_atlas_reference.json`. Die Referenz enthält aktuelle Datei-/Pixelbindungen
und Mappingdaten; keine Herstellerquellen, Originalbilder oder Vergleichsarchive.
Positive Prüfung ohne diese Archive und Negativfälle für fehlende/zusätzliche/
veränderte Ressourcen, falsche Imports, leere/doppelte/unsichere Inventare sowie
falsche Maße/Hashes/Versionen laufen im schnellen Toolpfad. Die native B-Probe
prüft tatsächlich importierte Pixel, sechs Texturen und 48.906.240 dekodierte
Bytes; Pixelmutation, falsche Variante, stale Cache und Vollinvalidierung bleiben
Gegenproben. Shaderfarbe/Alpha, Zeitbilder, Vorschau, Undo/Redo, Sessionwechsel
und Ressourcenplateau werden im regulären Projekt und separat im gelieferten PCK
geprüft. Aktuelle goldene Varianten-/Zeit-/Region-/Fugenfälle laufen in der Kernsuite.
Historische Laufzeit-/Quellhashvergleiche sind keine Ersatzpflicht mehr.

Ein Lauf mit ausgeschaltetem Bereich wird nicht als dessen erfolgreicher Nachweis
ausgegeben. Vollständige Produktionsrekonstruktionen echter Inhalte gehören ausschließlich
in deren Produktionsauftrag, nicht in den Fachlauf oder Runtime-Harness.

T04 prüft nach Abschluss außerdem die bekannten unveränderten T01/T02/T06-Zellstände
(400/1600/2500 unbekannte Zellen) und nach dem zweiten Neustart den semantischen
T01-Save (`fresh` oder gültig `loaded` mit 400 unbekannten Zellen). Die isolierte
Partialinstanz sichert den unveränderten T01-Startstand, damit der zweite Neustart
auch die gültig geladene Variante tatsächlich prüft. JSON-Zellwerte werden numerisch
verglichen. Erstmals erzeugte Dateien und reguläre Start-/Flush-Metadaten bleiben
zulässig. Eine zusätzliche kurze
T04-Lesegegenprobe verwendet ausschließlich eine Kopie des temporären Profils:
Ein kurzer Schreibprozess erzeugt dort über eine echte T01-Zellaktion den gültigen
veränderten Save samt History, auch wenn zuvor noch keine T01-Datei existierte.
Die neue Leseinstanz muss ihn nativ als `loaded`
mit 399 unbekannten Zellen erkennen und genau an der Isolationsassertion
mit Exit 4 scheitern. Erfolg, Recovery, Parserfehler oder andere Fehler werden
nicht als erfolgreiche Gegenprobe akzeptiert. Kein weiteres RP3-Durchspiel.

## KAT-2 als unabhängige native Kataloggruppe

`--groups catalog` führt die vollständige aktuelle Katalogprüfung unabhängig
von History und Abschluss aus, mit sämtlichen Neustart-, Last-, Eingabe-, Fehler-
und nativen Bildbelegen. Die Gruppe verwendet
[tools/kat2_product.py](../tools/kat2_product.py): reguläre Hauptszene mit echten
Pointerereignissen, gesonderter Prozessneustart, gültiger Leerbestand,
ungültige Registry, isolierter KAT-1-Adapterzuwachs und synthetische 300 Einträge.
Jede Instanz nutzt ein temporäres Projekt und Saveprofil. Kataloglast ist keine
300-fache Produktions-/Solverprüfung. Der Produktharness bindet alle Berichte
und die kleinen nativen Originalausschnitte an Head/Basis/Checkout; vollständige
Framekontexte bleiben lokal. Pflichtausschnitte dürfen nicht still aus der
begrenzten Lieferung fallen. Größen und Laufzeiten werden ohne feste Optimierungsbudgets gemessen. [KAT-2-Prüfzuordnung](KAT2_VERIFICATION.md).

## Native Renderabdeckung und Speicherung

ZA-1 ergänzt im ausgewählten Pilotenpfad vier temporär registrierte künstliche
Authoring-Pakete und zehn echte Prozesse für Mono/Farbe, Rechtecke, Neustarts und
Slotisolation. Native Pixelprüfungen liefern kleine Originalausschnitte samt
Koordinaten/Reports; vollständige Kontexte bleiben lokal. Der echte Windows-PCK
wird für regulären und isolierten Katalog geprüft. Der feste synthetische Adapterdurchstich liefert
nur den kompakten Bericht. Reine Inhalte wählen ausschließlich den schlanken
Inhaltspfad; Änderungen am gemeinsamen Produktharness wählen alle nativen Gruppen und Preflight. Keine zusätzliche CI-Fallliste je Inhalt. [Prüfzuordnung](ZA1_VERIFICATION.md).

Eigentümerfreigabe vom 14.10.2026 / #116: Die wiederholten Grafikmatrizen
verwenden drei gemeinsame Konfigurationen: **1280×720/UI125, 1920×1080/UI100
und 2560×1440/UI125**. Das deckt enge, normale und große Fenster ab; der frühere
vollständige Kreuzvergleich aller vier Auflösungen mit beiden UI-Skalierungen
ist keine Standardpflicht mehr. Gezielte Sonderfälle dürfen weitere Größen nutzen.

- Reguläre Vollansicht: alle 16 technischen Muster, beide Ansichten G/V,
  96 statt 256 Fälle. Rahmen, Hinweisgeometrie und Schriftgrenzen bleiben geprüft.
- Arbeits-/Fit-, Eingabe- und Schriftsonderfälle: 32 unverändert; Wiederherstellung
  für drei Muster in beiden Ansichten: 18 statt 48. Zusammen 50 statt 80 Fälle.
- Sidebar-/Arbeits-/Fit-Matrix: drei Muster und beide Ansichten, 36 statt 96 Fälle.
  Gezielte Ressourcen-, Rahmen-, Warnungs- und Wiederherstellungsprüfungen bleiben.
- H1: sechs aktuelle Off/On-Paare (drei Konfigurationen × G/V) sowie sechs
  Reveal-/Albumzustände. Keine Wiederholung der ersetzten Rasterkomponente.

Im allgemeinen Capture-Harness gilt `--ci-compact`:

- Zellgrößen 12/16/18/22/24/72 decken Minimum, Maximum und beide Seiten der
  tatsächlichen Zeichen-/Fontwechsel ab: 54 Zellszenarien.
- Layout: Album und drei Fixtures bei 720p/UI125 sowie 1080p/UI100+125,
  insgesamt zehn Bilderzustände.
- Die wirkungslose Ansichts-/Pan-Galerie ohne Pixelassertionen sowie die erzwungenen
  alten Raster-Clipping-/Pan- und Hinweis-Drag-Replays entfallen. Die aktuellen
  Vollansichts-/Rahmenprüfungen bleiben; Rasterpanning ist keine Spielfunktion.
- Beide Hinweisachsen, Einrastgrenzen .49/.51, Richtungen und aktuelle
  Außenanschläge bleiben in den gezielten nativen VS2-Prüfungen erhalten.
- Alpha, Papierfugen, alle Farben, Hoverkreuz und G1-Zähler, Vorschau, Hinweisink,
  aktuelle Buch-/ZS2-Pixelverträge und Spoilergrenzen bleiben erhalten.

Die vollständigen günstigen Logik-/Zoom-/Geometrietests bleiben bestehen.
Gerenderte Bilder werden für Assertions direkt im Speicher verwendet. Der
allgemeine kompakte Capturepfad speichert fünf ausgewählte Erfolgsbilder;
Fehler sichern die zuletzt relevanten Originalframes. Die Buchprüfung wertet
alle bisherigen 17 Bildzustände und Textkontraste weiter aus, schreibt im
kompakten Erfolgspfad aber keine ungenutzten PNGs. Fehlerbilder bleiben erhalten.
ZS2 und gegebenenfalls Pilotprüfungen liefern ihre gezielte technische Auswahl.
Anzahl gerenderter und gespeicherter Fälle sind getrennt. Unabhängige Prüfungen
verlangen die genaue erwartete Matrix und erkennen auch doppelte/fehlende Fälle.

Abgeschlossene ZS1-/VS1-Studien, GP48-/ZV50-/Z2-Vorherprojekte, H1-Ownerprogramme
und alte Review-ZIPs werden im Standardlauf weder importiert, gerendert noch
verpackt. Für einen konkreten historischen Vergleich wird ein separater Checkout
des gebundenen ursprünglichen Commits verwendet. Dabei dessen damalige Quellen
und Verträge lesen; keine alten Studienharnesses unbemerkt gegen neue APIs ausführen.

Die früheren 30-/75-MB-Grenzen aus PERF-B-E1 sind durch #116 aufgehoben.

## Artefakte und Laufzeiten

Eigentümerentscheidung vom 14.10.2026 / #116: Laufzeit und Artefaktvolumen möglichst
klein halten, **ohne feste CI-Joblaufzeit- oder Artefaktgrößenbudgets**. Die Workflows
setzen keine projektspezifischen `timeout-minutes`; Anbietergrenzen gelten weiterhin.
Es gibt kein 30-/75-MB-Erfolgsgate und keine bytebedingte Auslassung angeforderter
Nachweise. Reports messen Phasen und tatsächlich gelieferte Bytes. Beibehalten:
gezielte Auswahl kompakter Originalbilder, verlustfreie JSON-Kompression und kurze
Aufbewahrung. Keine historischen Produktionsarchive, vollständigen Arbeitsgalerien
oder obsoleten Ownerhilfen in Spielerpaketen.

Prozess-/Netzwerk-Abbruchschutz und explizite funktionale Solver-/Import-/Reparatur-
Ressourcenverträge sind Schutz vor Hängern bzw. Teil des getesteten Fehlerverhaltens,
keine CI-Optimierungsziele. Diese werden nicht stillschweigend als Tests entfernt.
Der Umfang bestehender Prüfbereiche wird erst nach verständlicher Kosten-/Zweckliste
und Eigentümerentscheidung reduziert. Kein Test gilt wegen seines alten Namens als
obsolet; aktuelle Aufrufer und Verhalten sind maßgeblich.

Die vollständigen aktuellen VS2-/V1-Geometriematrizen bleiben verlustfrei `.json.gz`;
der bytegleiche Rückweg ist geprüft. Native Bildinhalte bleiben unverändert;
CI-C erlaubt verlustfreie Neucodierung bei nachgewiesener Pixel-/Alpha-, Maß- und
Ausschnittgleichheit. Eine
größere Lieferung ist ein zu erklärender Messwert, kein automatischer Fehler.

Erfolgreiche Product-Läufe liefern das reguläre Windows-Spielerpaket und eine
begrenzte technische Auswahl. Technische Daten werden sieben Tage, Spielerpakete
14 Tage aufbewahrt. Erforderliche persönliche Referenzen werden vor Ablauf gezielt
dauerhaft gesichert. Preflight exportiert weiterhin wirklich, lädt standardmäßig
aber nur den kleinen Bericht und Logs hoch. Fachberichte sind ebenfalls begrenzt.

Product schreibt Bericht und laufende Phasenlogs von Anfang an unter `technical/`;
dieser Ordner wird auch nach Fehlern/Abbrüchen hochgeladen. Fehlermarker werden am vollständigen Log geprüft; Logs werden nicht bytebedingt gekürzt. Abgebrochene Phasen bleiben als solche sichtbar.
Laufzeitziele werden erst durch neue Messungen als erreicht ausgewiesen;
Warteschlangenzeit und Runnerzeit werden getrennt betrachtet.

Godot-Editor und Exportvorlagen bleiben offiziell und exakt hashgebunden. Ein
nach OS/Version/Archivhashes benannter Cache speichert nur Downloadarchive;
jedes wiederhergestellte Archiv wird erneut geprüft. Keine Prüfergebnisse cachen.
Der Fachjob führt nur allgemeine Tests, sechs synthetische Leistungsreferenzen
und den festen künstlichen Adapterdurchstich aus. Keine historischen
Produzentencommits oder RP4-/RP5-Korpus-/Windows-Replays mehr in CI.

## Spielerexport mit separaten Ressourcen

Der reguläre Export verwendet `binary_format/embed_pck=false`. Das offizielle
Debug-Template bleibt unverändert. `picross-p1.exe`, die Konsolenhilfe und
`picross-p1.pck` sind verpflichtende, nicht leere Paketdateien. EXE und PCK müssen
nach dem Entpacken im selben Ordner liegen. Das verschiebt Ressourcen aus der
EXE, reduziert aber nicht automatisch die Gesamtgröße des Downloads.

Product prüft die tatsächlich exportierte PCK mit einem externen nativen Probe-
Skript, einschließlich ausgeschlossener Test-/Produktionsdateien, und bindet
EXE sowie PCK per Hash an den Bericht. Der manuelle main-Build prüft weiterhin
nur Paketvollständigkeit; er ersetzt keinen Product-Prüflauf.

## Separater manueller main-Player-Build

Der Workflow [Build playable main](../.github/workflows/build-main-player.yml) wird
ausschließlich über `workflow_dispatch` gestartet und checkt ausdrücklich den
aktuellen `main` aus. Er nutzt die bestehende verifizierte Godot-Toolchain und
den regulären tatsächlichen Spielkatalog, führt aber **keine** Kern-, Integrations-,
Render-, Solver- oder Rätseltests aus. Er erstellt nur den unsignierten
Windows-x64-Debugexport und kontrolliert vollständige, nicht leere Exportdateien.

`upload-artifact` übernimmt das direkte Player-Verzeichnis (EXEs, separate
PCK, Anleitung und benötigte Lizenzen) und erzeugt selbst das einzige
herunterladbare ZIP; kein weiteres Spieler-ZIP oder Technikartefakt. Der
bestehende Product-Verifikationsworkflow und dessen gebundene Nachweise bleiben
unverändert. Ein Build ist weder persönliche Windows-Abnahme noch Release.

## Archiv und gebundene Referenzen

Das [BP-Archiv](design/book_inventory/ARCHIVE.md) bindet die 136 entfernten alten
Dateien mit 161.102.998 Bytes an unveränderliche Git-Objekte. Aktive Ressourcen, Fonts/Lizenzen und noch verwendete technische Testinputs bleiben.
Abgeschlossene RP-/VS-Produktionsquellen liegen ausschließlich in der Git-Historie.
Die drei großen Paketrekonstruktionen entfallen aus `unittest discover -s tools`;
die 13 günstigen BP-Hilfsregressionen bleiben. Keine Historienumschreibung.

[#61](https://github.com/venomenon328/picross/issues/61) benötigt weiterhin die
Originalreferenz `regular-F-01-G-ui100.png` aus Run `37948444207`, Artefakt
`11626179754`, Quelle `2c332ad688315bfa851f7c0d8642d2ab4ac3709c`.
Die unveränderten 2.088.706 Bytes sind als geschützte
[Eigentümerreferenz](https://chatgpt.com/api/library/files/libfile_658dd3b665588191a86b36e51d240320/download)
dauerhaft gesichert. PNG-SHA-256:
`0a7c386f3f52760e98bb15cbf8991cc4ae3c62d3f03af2db6d0d8c92d04c9392`;
inneres ursprüngliches Review-ZIP:
`38a908bb11bc7b27ec26c92af030b3605e00637fdaafb3bf2a4286d4908f25b5`.
Die neue Sicherung macht den Ablauf des ursprünglichen Actions-Artefakts am
23.10.2026 für diese benötigten Bytes unschädlich. Sie ist kein neues Renderbild.

VS2, Sidebar und PERF-A/B sind über PR #62/#66 integriert. Die alte offene
Vollsichtnacharbeit ist kein aktueller CI-Auftrag. Ihre ursprünglichen Rätselzertifikate liegen in der Git-Historie; CI prüft sie nicht erneut. Weitere Quellenentscheidungen und
Dateibindungen stehen im [Bestandsinventar](DEVELOPMENT_ARCHIVE.md).

## Verifikation der bestehenden Lieferung und der Folgepakete

Die folgenden Nachweise gehören zur bestehenden #70-Lieferung, nicht zur
CI-A-/CI-B-/CI-C-Lieferung. Deren T01/R01 sind oben und in den
Paket-Issues festgelegt. Der reine Spezifikationsdiff benötigt den aktuellen
Dokument-/Werkzeugtestpfad, Dokumentvalidator, vollständigen Diffcheck und
`ci-required`; maßgeblich bleibt die tatsächlich automatische Auswahl.

Auswahltests umfassen reine Dokumentation, tatsächliche Daten-/Asset-/Pilotpfade,
Renderer, gebundene Markdowninputs, unbekannten Code und echte Umbenennungen mit
Löschung des alten Pfades. Gatetests prüfen Erfolg, Nichtzutreffen und sämtliche
fehlenden/abgebrochenen/fehlgeschlagenen Pflichtresultate. Dazu kommen aktuelle
Tool-/Fachtests, Workflowvalidierung und der echte native Product-/Windowslauf.
Konkrete gemessene Resultate, Head-/Test-Merge-Bindung und der getrennte Selbstreview
stehen im PR zu #70 (Vorgängermessungen in #63/#66). Persönliche Produktabnahmen und Mergefreigabe bleiben separat.
