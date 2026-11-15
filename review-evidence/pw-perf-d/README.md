# PW-PERF-D · T01–T03 · Revieworiginale

Produkthead `77392b2b07021a88b8eb02e74ceb213fb83d187d`, Basis `a559e8b38be7e658ff1d3d2aa667380657c89f4d`, PR #658. Empfänger: unabhängiger Reviewer
mit Repositoryzugang. Ablauf **2026-11-22** oder Abschluss von PW-PERF-D-A01,
anschließend temporären Reviewref entfernen. Keine Integration dieser Dateien nach main.

## T01 · vollständige Normabdeckung und aktives Routing

`norm-coverage.json` enthält alle 31 ursprünglichen Überschriften und 123 einzelne
Norm-/Tabellen-/Textblöcke, vollständige Alttexte, SHA-256 und jeweils eine neue
kanonische Autorität samt geprüftem Dateipfad/Anker. Containerüberschriften verteilen
sich über ihre ausdrücklich getrennten Normeinheiten; keine konkurrierende Kurzregel.
`routing-links.json`: 76 aktive Markdown-/HTML-Verweise auf Authoringquellen,
0 fehlende Dateien und 0 fehlende Anker. Historische feste HTTPS-Quellen bleiben
historische Bindungen, keine neue Routinelektüre.

| Alter Abschnitt/Anker | Neue Autorität nach Normeinheit |
| --- | --- |
| 1. Einstieg und Befugnisse |  |
| 1.1 Pflichtquellen nach Phase | `docs/ai-workflows/PUZZLE_AUTHORING.md#11-pflichtquellen-nach-phase` |
| 1.2 Gemeinsame Arbeitsregeln | `docs/ai-workflows/PUZZLE_AUTHORING.md#12-gemeinsame-arbeitsregeln` |
| Prüfungen gehören zur Produktion, nicht zur CI | `docs/ai-workflows/PUZZLE_AUTHORING.md#prüfungen-gehören-zur-produktion-nicht-zur-ci` |
| 2. Abschlussbild zuerst, danach Abstraktion |  |
| 2.1 Eingaben und Konfiguration | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_1.md#21-eingaben-und-konfiguration`; `docs/ai-workflows/PUZZLE_AUTHORING_STEP_2.md#21-konfiguration-nach-bildfreigabe` |
| 2.2 Darstellungen auseinanderhalten | `docs/ai-workflows/PUZZLE_AUTHORING.md#darstellungen-und-sichtung` |
| 2.3 Styleguide | `docs/ai-workflows/PUZZLE_AUTHORING.md#darstellungen-und-sichtung` |
| 2.4 Abschlussbildauswahl und Abstraktionsfreigabe | `docs/ai-workflows/PUZZLE_AUTHORING.md#gemeinsame-bildkorrektur`; `docs/ai-workflows/PUZZLE_AUTHORING_STEP_1.md#24-abschlussbildauswahl-und-abstraktionsfreigabe`; `docs/ai-workflows/PUZZLE_AUTHORING_STEP_2.md#24-abstraktionsfreigabe` |
| 3. Standardablauf: fünf Aufträge | `docs/ai-workflows/PUZZLE_AUTHORING.md#3-gesamtfolge`; `docs/ai-workflows/PUZZLE_AUTHORING_STEP_1.md#2-abschlussbild-zuerst`; `docs/ai-workflows/PUZZLE_AUTHORING_STEP_2.md#2-motivvorlage-nach-revealfreigabe`; `docs/ai-workflows/PUZZLE_AUTHORING_STEP_3.md#4-rasterproduktion-und-technische-pflichtprüfung`; `docs/ai-workflows/PUZZLE_AUTHORING_STEP_4.md#63-hintergrundarbeit-in-schritt-4`; `docs/ai-workflows/PUZZLE_AUTHORING_STEP_5.md#8-abgenommenes-paket-ins-spiel-integrieren` |
| 4. Rasterproduktion und technische Pflichtprüfung | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_3.md#4-rasterproduktion-und-technische-pflichtprüfung` |
| 4.1 Import und Rastervarianten | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_3.md#41-import-und-rastervarianten` |
| 4.2 Harte Kriterien | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_3.md#42-harte-kriterien` |
| 4.2.1 Profilwahl und Produktionsnachweise | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_3.md#421-profilwahl-und-produktionsnachweise` |
| 4.3 Redaktionelle Kriterien | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_3.md#43-redaktionelle-kriterien` |
| 4.4 Reparaturen und Änderungen | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_3.md#44-reparaturen-und-änderungen` |
| 4.5 Geprüfte Raster zur menschlichen Auswahl | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_3.md#45-geprüfte-raster-zur-menschlichen-auswahl` |
| 5. Schwierigkeit L1–L5 | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_3.md#5-schwierigkeit-l1l5` |
| 5.1 Historische Produktionsmethoden 0.1 und 0.2 | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_3.md#52-aktueller-zusätzlicher-integrationsstandard-sd` |
| 5.2 Aktueller zusätzlicher Integrationsstandard SD | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_3.md#52-aktueller-zusätzlicher-integrationsstandard-sd` |
| 6. Dateien, Übergabe und Wiederaufnahme |  |
| 6.1 Repositoryablage während der laufenden Produktion | `docs/ai-workflows/PUZZLE_AUTHORING.md#61-repositoryablage-während-der-laufenden-produktion` |
| 6.2 Übergabedatensatz | `docs/ai-workflows/PUZZLE_AUTHORING.md#62-übergabedatensatz` |
| 6.3 Hintergrundarbeit in Schritt 4 | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_4.md#63-hintergrundarbeit-in-schritt-4` |
| 7. Freigaben und Abschlussausgabe | `docs/ai-workflows/PUZZLE_AUTHORING.md#7-freigaben-und-abschlussausgabe` |
| 8. Abgenommenes Paket ins Spiel integrieren | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_5.md#8-abgenommenes-paket-ins-spiel-integrieren` |
| 9. Produktionsabschluss und Bereinigung | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung` |
| Abschluss nachträglicher Bildrevisionen · CI2 vom 26.10.2026 | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_5.md#abschluss-nachträglicher-bildrevisionen--ci2-vom-26102026` |
| Abschluss der Hintergrundarbeit | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_5.md#abschluss-der-hintergrundarbeit` |
| HP-I1b2: eigene Hintergrundrevision und ihr Abschluss | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_5.md#hp-i1b2-eigene-hintergrundrevision-und-ihr-abschluss` |
| PW-PERF-B · Begrenzte Erstregistrierungsprüfung | `docs/ai-workflows/PUZZLE_AUTHORING_STEP_5.md#pw-perf-b--begrenzte-erstregistrierungsprüfung` |

Gemeinsame Regeln aus §§6.1/6.2/7 und Korrektur/Wiederaufnahme stehen einmalig im
Kern. §3 ist dort die Gesamtfolge; Bild-/Motivübergaben sind zusätzlich in ihrer
zuständigen Phase vollständig. Die Bilddarstellungen und Originalsichtung aus
§§2.2/2.3 sind gemeinsame Regeln. Der alte §2.1 ist nach frühen Eingaben und
Konfiguration nach Bildfreigabe getrennt. §2.4 Punkte 1–3 gehören zu Schritt 1,
Punkte 4–5 zu Schritt 2; Bildkorrektur bleibt gemeinsam. §§4/5.2 sind vollständig
Schritt 3; §5.1 bleibt historisch erreichbar. §6.3 gehört ausschließlich zu Schritt 4,
§§8/9 und revisionsgenaue Abschlusswege zu Schritt 5. Laufende Produktionsgates,
Rechte, 50-Zellen-/Farblimits, Budgets, Proof, echte menschliche Freigaben und
Integrationsbefugnisse sind unverändert. Keine reale Produktion oder Retirementaktion.

Farbe liest ausschließlich operative Q §§8.4–8.5. Q-R04/Q-H01/Q-H02, negativ bleibende
Paarbefunde, echte Endfreigaben, visuelle Warn-/Ausnahmeentscheidungen bleiben Pflicht.
Qualität §§8.1–8.3.1 und 0.7-/Liefertexte bleiben Herkunft, keine Routinequelle.
Formeln, Grenzen, Referenzwerte und historische Eigentümerurteile wurden nicht geändert.

Aktive Caller: AGENTS, Projektprofil, PW-Einstieg, Tool-/PW-README und HTML-Verweissheet
führen denselben Kern/Phasenrouter. `ui/workflow.js` nennt die tatsächlich geroutete
Phase; der CMD-Launcher ist aus genau diesen Quellen regeneriert und geprüft.

## T02 · geschlossene Generation und tatsächliche Consumer

Neue Formen: Request v4, Handoff v5, Record/Result v4 und rulebook-v2. Acht Dateien
werden vollständig inventarisiert; neue Builder vergleichen Gitblobbytes und
Commitabstammung. Dokumentrevision 7 ist unter alten 0.8-Formen nicht zulässig.
Historische Handoff-/Record-/Snapshotbytes behalten ihre eigene Generation.

| Consumer | Tatsächliche Änderung / Grenze |
| --- | --- |
| authoring_rulebook / Buildvertrag / Builder | Geschlossene Quellenmenge, Pfade, Bytes/Hashes, Header, Revision, Commit; capture aus echten Gitobjekten; kein Fetch/Writer |
| Package / Finalizer / Record / Handoff | Neue und alte Generationen ausdrücklich getrennt; vollständige neue Originalprüfung |
| presentation / projector / current_view / deliveries | Neue Records und alle Quellen; historische Ansicht behält ihre alte reine Datei-/Inventarprüfung |
| background_package / fixed_raster / Export v6 | Neue Originalgeneration; Export/Offlineprüfung erreicht den zentralen Reader, keine neue Solver-/Bildlogik |
| palette_gate | Vollständige neue Regelbindung, äußerer Ausnahme-v2-Dispatch; alte Ausnahme v1 ausschließlich bei alten Originalen; keine Farbmetrikänderung |
| batch_operations / batch_runner | Aktuelle Regelquellen in Werkzeugbindung, BA-A weiterhin nur lokale 0.6/0.7-Eingänge; historischer Einzeltext aus eigenem Gitursprung |
| integration_batch_operations / integration_batch_runner | Vollständige neue Quellenmenge/Hashbindung vor Reservierung, natives Export weiterhin Pflicht |
| integrated_content | Ausschließlich Record-v4-Erkennung ergänzt, keine E-Reader-/Retirementkorrektur oder Bestandsaktion |

Am Produkthead sind drei kleine synthetische Regressionen im vorhandenen Helfer
`test_authoring_workflow.py` erfolgreich: Mono und Farbe jeweils über Builder,
Paket-/Ansichtsreader, Auswahl/Finalizer und Export/Offlineprüfung; fehlende oder
manipulierte Quellen, auch intern neu gehashte fremde Gitbytes, fehlende Menge,
falsche Revision/Commit/Form, alte Form mit Rev7 und blockierte Publikation;
zusätzlich unveränderte historische 0.7-Originaldatei mit ihrem damaligen Reader.
Keine Eigentümerfreigabe wird durch diese TEST-ONLY-Fixtures behauptet.

CI-Original: https://github.com/venomenon328/picross/actions/runs/43711656445
Quellhead `77392b2b07021a88b8eb02e74ceb213fb83d187d`, Testmerge `e7223edc0d547ace45a7c0c98292b8c1de045c74`.
Kern docs/ci-required, tools und production.adapter sowie regulärer Windows-x64-Build
sind erfolgreich. Tools: 505 Tests, ein bestehender Windows-Kernel-Mutex-Fall auf
Linux ausdrücklich ausgelassen; Windowsbau ist kein behaupteter manueller Windowsstart.
Adapter inklusive ZA-1-Durchstich und unabhängiger Originalreader erfolgreich.
`evidence.mode=none`, keine zusätzlichen technischen CI-Downloads oder Dauermatrix.

## T03 · reproduzierbare gleiche-kanalige Quellenprobe

| Phase | Vorher UTF-8/LF-Bytes | Nachher | Obergrenze | Dateien/Abrufe | Median ms vorher → nachher |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 35,494 | 29,442 | 35,494 | 5 → 6 | 2.404 → 1.429 |
| 2 | 33,552 | 27,873 | 33,552 | 4 → 5 | 2.276 → 1.283 |
| 3mono | 56,378 | 56,370 | 56,378 | 4 → 5 | 2.618 → 1.282 |
| 3color | 78,413 | 63,496 | 67,593 | 4 → 5 | 2.930 → 1.863 |
| 4 | 46,592 | 45,686 | 46,592 | 5 → 6 | 3.362 → 2.100 |
| 5 | 35,761 | 33,687 | 35,761 | 3 → 4 | 2.127 → 0.776 |

101 vorab festgelegte Paare; Reihenfolge vor/nach wechselt, ein geplanter Warmlauf
je Route. Alle Einzelwerte und Quell-/Abschnitts-/Hashlisten stehen in
`source-map.json`. E: wurde als NTFS geprüft. Gleicher Python-/NTFS-Kanal,
gleiche Pfadtiefe, kein persistenter Ergebniscache; Setupkopien machen dies zu einer
warmen Probe, kein behaupteter Kaltstart. Es wird keine dauerhafte Modellkontext-
Wiederverwendung angenommen. Jede der sechs Routen steht für einen unabhängigen Auftrag.

Summierte Abruf-/Auswahlzeit über 101 komplette Paare: vorher
1.636874 s, nachher 0.913048 s.
Median des gesamten Sechs-Routen-Pakets: 16.1183 →
8.9335 ms. Setup (Gitobjekte/Kopien) separat
359.597 ms, außerhalb des Vergleichs. API-/Netzwartezeit ist in diesem
lokalen Abrufkanal nicht enthalten. Ein zusätzlicher gezielter Abruf je Phase wird
benötigt und offen ausgewiesen. Alle Byte-/Zeitbudgets sind erfüllt.

0 Routineabrufe separater historischer Snapshot-/Lieferdateien, 0 abgeschnittene
Auswahlantworten und 0 ungeplante Wiederholungsabrufe innerhalb der definierten Probe.
Das sind lokale Helperausgaben; keine gemessenen Modelltokens. Aktuelle Qualitätsdatei
wird intern ganz gelesen, nur operative Abschnitte gehen in die berechnete Ausgabe.
Die Nullen behaupten keinen lückenlosen Zähler der Entwicklungslektüre; dort gab es
auch abgeschnittene Sammelantworten. Geplante 101 Messwiederholungen bleiben sichtbar.

Technische Zusatzquellen sind in `technical-sources.json` getrennt nach Operation
mit vorherigen/nachherigen ganzen Dateibytes und Hashes erfasst, ausdrücklich außerhalb
dieser Basisprobe. Ihre tatsächliche Bedarfslektüre bleibt im Router Pflicht; kein
pauschaler Vollabruf. PW-B wächst durch den neuen geschlossenen Vertrag. Daher keine
Behauptung gleicher technischer Zusatzkosten, Solver-/Registerbeschleunigung,
Tokenersparnis oder Verringerung der 21-Minuten-Gesamtauftragszeit.

Reproduktion: `source_probe.py` in eine eigene temporäre Ablage außerhalb des
Produktcheckouts kopieren, dann `python source_probe.py <checkout-am-Produkthead>`.
Die gebundene Basis muss lokal als Gitobjekt erreichbar sein; das Skript holt keine Netzwerkquellen. Es erstellt dort eigene probe-before/probe-after-Verzeichnisse und das
Messoriginal. Diese temporären Daten nach der Prüfung entfernen.

## Getrennter Selbstreview / offenes Gate

Tatsächlicher PR-Diff, Head/Basis, neue/alte Consumers, vollständige Normzuordnung,
aktive Links und Nichtziele selbst geprüft. Keine Inhalte/game-Daten oder dev-rules
geändert. Kleine technische Nachweise bleiben außerhalb des Produktbranches.
Der anfängliche Toolsfehler wurde im Scope korrigiert: keine neue historische
Ansichtsheaderpflicht, neue Importzuordnung, regenerierter gebundener Launcher.
Das ist **keine unabhängige Abnahme**. PW-PERF-D-A01 bleibt beim unabhängigen
Reviewer `before_merge`; kein Merge in diesem Auftrag.
