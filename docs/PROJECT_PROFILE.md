# Projektprofil: picross

## Zweck, Quellen und aktueller Rahmen

`venomenon328/picross` enthält neben Produktkonzeption, Entwicklungsregeln und Dokumentprüfung den technischen [P1.0-Preflight](P1_PREFLIGHT.md) und den ersten ausführbaren [P1.1-Mausschnitt](../prototypes/p1/README.md) unter `prototypes/p1/`. Dieser Zwischenstand aus #8 liefert F-01, noch keine vollständige P1-Lieferung oder Produktabnahme. Der [Workflow](dev-rules/WORKFLOW.md) ist die gemeinsame Prozessgrundlage; [AGENTS.md](../AGENTS.md) der Einstieg. Aktueller Lieferumfang und Freigaben stehen im jeweiligen Issue/PR, nicht in einer parallel gepflegten Roadmap.

Die [Produktdefinition](PRODUCT_DEFINITION.md) ist die zuständige Quelle für die bisher bestätigte Produktausrichtung. Bei Arbeiten an Produktkonzept, Rätselregeln/-inhalten, Progression/Wertung, UX/UI, Eingabe, Plattformkonzept oder Produktarchitektur vollständig lesen. Sie unterscheidet bestätigte Entscheidungen, noch zu prüfende Vorschläge und offene Details. Ihr grober Entwicklungsablauf ist keine Implementierungsfreigabe oder eigenständige Fortschrittsverwaltung.

Das [Gestaltungskonzept](DESIGN_CONCEPT.md) konkretisiert die bestätigte visuelle Grundlage und dokumentiert die noch offene Themenwahl sowie Interaktionsvorschläge. Bei Arbeiten an Thematik, Album, Motiventhüllung, UX/UI, Eingabe/Wertung oder entsprechenden Prototypen zusätzlich vollständig lesen. Die positive Rückmeldung zu den exemplarischen Mocks ist keine Abnahme sämtlicher dargestellter Details und kein Nachweis funktionierender Bedienung.

Für den Großraster-/Bedienprototyp zusätzlich die vollständige [P1-Spezifikation](PROTOTYPE_P1.md), [Issue #5](https://github.com/venomenon328/picross/issues/5) einschließlich späterer Entscheidungen und das beauftragte Teilpaket lesen. Die Datei enthält den versionierten Vertrag, die Issues den aktuellen Auftrag und Ausführungs-/Abnahmestand. Für technische P1-Arbeit außerdem [P1.0](P1_PREFLIGHT.md), [P1.1-Anleitung](../prototypes/p1/README.md) und [P1.1-Prüfbericht](P1_1_VERIFICATION.md) lesen. Die bestätigten P1-Entscheidungen gelten innerhalb dieses begrenzten Scopes; sie entscheiden nicht die endgültige Produkttechnik oder globale Wertungsfragen. Technischen Nachweis und reale Produktabnahme unterscheiden.

Der [Herkunftsnachweis](DEV_RULES_ADOPTION.md) bezeichnet die unveränderte Regelkopie. Eine P1-Spezifikation liegt vor; eine abschließende Produktarchitektur und erprobte produktspezifische Teststrategie existieren noch nicht. Weitere Quellen erst mit tatsächlich beschlossenen Inhalten anlegen und hier situationsbezogen verlinken; keine nicht vorhandenen Pflichtdokumente erfinden.

## Beschlossene Richtung und offene Produkt-/Technikentscheidungen

Die Produktdefinition legt das PC-Nonogramm-Konzept mit klassischen und farbigen kuratierten Bildrätseln, Großrasterfokus, früher visueller/UI-Konzeption, Offline-Solo-Spiel sowie den grundsätzlichen Progressions- und Wertungsrahmen fest. Sie ist für diese Entscheidungen maßgeblich; das ursprüngliche Repositorysetup hatte sie noch nicht getroffen.

Beschlossen sind außerdem ein sich füllendes Album, warme und ruhige handgezeichnete 2D-Gestaltung mit klaren Konturen und Farbflächen, motivtreue farbige Abschlussrepräsentationen monochromer Rätsel sowie Perfektion nur ohne Fehler und ohne Undo. Thematisches Sammelalbum und regionales Reisetagebuch bleiben Alternativen. Hypothesen und ihre Wertungswirkung, die Abgrenzung manueller Korrekturen sowie konkrete Layout-/Interaktionsdetails sind nicht allein durch den Mock entschieden.

Für P1 bestätigt: native Windows-Desktopfassung, typisiertes GDScript mit Godot Standard 4.7.2-stable und passenden Exportvorlagen, reduzierter Umfang ohne Wertung/Live-Fehlerhilfe/Hypothesen, elastische Strichvorschau, geschützte Einträge und Abschluss ohne vollständiges Auskreuzen. **D-06:** P1 wird mit Maus umgesetzt und abgenommen; Tastatur-/Controllerbedienung sind kein Scope, Start- oder Merge-/Abnahme-Gate. Das ersetzt die überholten P1-0.2-Passagen, ohne spätere alternative Produkteingaben umzuschreiben. Nutzerreferenz: Windows 11, 2560×1440, Maus, Ryzen 7 5800X und GeForce RTX 3070. Die reale Anzeigeskalierung wird bei K-06 erfasst.

Die endgültige Produktengine/-sprache, gesamte PC-Betriebssystemmatrix, Produktdatenhaltung, genaue Rätsel-/Solververträge, Fehlerzählung, Sternschwellen und Veröffentlichungs-/Lizenzdetails bleiben außerhalb der begrenzten P1-Festlegungen offen. Vor davon abhängiger Implementierung die konkreten Entscheidungen und Abnahmekriterien klären. Bereits ausdrücklich getroffene neue Nutzerentscheidungen nachvollziehbar in ihre zuständigen Quellen übernehmen, statt sie ungefragt neu festzulegen.

Insbesondere keine Java-, Datenbank-, Windows-Werkzeugpfad- oder lokalen Testverbote allein aus anderen Projekten übernehmen. Die Godot-Wahl für P1 beruht auf dem ausdrücklichen Nutzerentscheid, nicht auf dem ursprünglichen Setup. Python dient der Dokumentprüfung und dem isolierten P1.0-Toolchain-Smoke, nicht als Produktstackentscheidung.

## Branches und Befugnisse

Zielbranch ist `main`. Neue Arbeitsbranches gemäß gemeinsamem Workflow; Vorbereitung erzeugt standardmäßig noch keinen Branch oder PR. Ein Implementierungsauftrag erlaubt Branch, Commits, Push und Draft-PR im beauftragten Umfang. Standardmerge ist Squash nach ausdrücklicher oder passender bedingter Freigabe. Keine automatische Branchlöschung, kein Force-Push und keine direkten Änderungen am Zielbranch ohne entsprechende Befugnis.

Die einmalige Initialisierung des tatsächlich leeren Repositories ist in [Issue #1](https://github.com/venomenon328/picross/issues/1) dokumentiert. Danach läuft auch das Setup über einen eigenen PR. Technischer Branchschutz wurde nicht eingerichtet oder als wirksam verifiziert; die vereinbarten Prüfungen gelten unabhängig davon.

Der aktuelle Auftrag erlaubt ausschließlich die Umsetzung von #8 auf `feat/5-p1-prototype`, Tests, Commit/Push und Draft-PR gegen `main`; keinen Merge. Der gemeinsame P1-Draft bleibt für die später einzeln beauftragten Pakete #9, #11 und #12 bestehen. Issue #5 bleibt bis zur vollständigen Prototyplieferung und Abnahme offen.

## Prüfweg für den Dokumentationsstand

Python 3.11 oder neuer, ausschließlich Standardbibliothek. Kleine lokale Prüfungen in einer geeigneten bestehenden Umgebung sind zulässig; ein passender aktueller CI-Nachweis kann die Abschlussprüfung liefern. Keine pauschale doppelte lokale Vollprüfung neben demselben belastbaren CI-Stand. Unbekannte lokale Ressourcen- oder Konfigurationsgrenzen vor davon betroffener Arbeit prüfen; globale Codex-Einstellungen der Nutzerworkstation sind hier nicht als geprüft bestätigt.

Verbindliche Befehle im Repository-Root:

```sh
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/check_docs.py
```

Vor Merge muss [Setup verification](../.github/workflows/setup.yml), Job `docs`, für den aktuellen PR-Head beziehungsweise zugehörigen Test-Merge-Stand erfolgreich sein. Er führt die Tests, Dokumentprüfung und `git diff --check` über das vollständige Änderungspaket aus. Fehlende, fehlgeschlagene oder übersprungene Pflichtprüfungen nicht als bestanden werten. Head, Basis und gegebenenfalls Test-Merge den Belegen zuordnen.

[check_docs.py](../tools/check_docs.py) und [seine Tests](../tools/test_check_docs.py) sind aus dem in der Herkunftsnotiz genannten dev-rules-Stand abgeleitet und auf `docs/dev-rules/` sowie die tatsächlichen Setup-Dateien angepasst. Sie prüfen erforderliche Dateien, UTF-8/LF/Abschlusszeile, nachgestellte Leerzeichen, Versionsformat und einfache lokale Inline-Markdown-Links einschließlich Paketgrenzen. Keine externe URL-Prüfung, Linkanker-, Referenzlink- oder vollständige Markdownvalidierung. Byteidentität des Regelpakets beim Einführen/Aktualisieren separat gegen den Quellcommit prüfen; der Dokumentvalidator beweist sie nicht.

## Technischer P1.0-Preflight

Issue #7 wird durch `tools/p1_preflight.py`, die ausschließlich technische Probe unter `tools/p1_preflight_smoke/` und den Workflow [P1 toolchain preflight](../.github/workflows/p1-preflight.yml) geprüft. Der Preflight bleibt bei Godot Standard 4.7.2-stable und lädt Editor sowie Standard-Exportvorlagen ausschließlich aus dem offiziellen Release. Live-Release-Metadaten und die vollständigen Archive werden gegen die festgeschriebenen SHA-256-Werte geprüft; Binärarchive werden nicht versioniert oder global installiert.

Der vollständige lokale Befehl und die Speicher-/Timeoutvoraussetzungen stehen im [Preflightbericht](P1_PREFLIGHT.md). Seine Offline-Harnesstests laufen bereits mit dem verbindlichen `unittest discover`-Befehl. Bei Änderungen am Preflight muss zusätzlich der echte Download-/Import-/Test-/Start-/Exportweg lokal oder in der dafür bestimmten CI ausgeführt werden; ein reiner Mock- oder Dokumenttest reicht nicht.

P1.0 wurde nach erfolgreichem `preflight`- und `docs`-Job über PR #13 gemergt. Sein Artefakt bleibt eine technische Probe, kein Release oder Nachweis für Spielverhalten. Das frühere Controller-Planungsgate ist inzwischen ausdrücklich durch D-06 entfallen.

## Ausführbarer P1.1-Produktprüfweg

Der [Produkt-Harness](../tools/p1_product.py) verwendet die unveränderten P1.0-Funktionen für offizielle Release-Metadaten, vollständige SHA-256-Prüfung, Editor/Exportvorlagen und isolierte Prozessumgebung. Er arbeitet mit einer temporären Projektkopie und eigenen APPDATA-/LOCALAPPDATA- beziehungsweise XDG-Pfaden. P1.1 schreibt keine Spielstände. Lokale Windows-Prüfungen sind erlaubt; Prozesslimit 300 Sekunden, Downloadlimit 1200 Sekunden, CI-Joblimit 40 Minuten.

```powershell
$p1Cache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $p1Cache --output-dir artifacts/p1-product
```

Unter Linux denselben Befehl mit `python3` und einem externen Cachepfad verwenden. Er prüft F-01s Deduktionszertifikat, importiert `prototypes/p1`, führt `res://tests/run_tests.gd` mit Erfolgsmarker und Fehlerstatus aus, kontrolliert den erwarteten Negativtest (Exit 23), startet die echte Hauptszene mit begrenztem Smoke, exportiert `P1 Windows x86_64` und prüft unter Windows zusätzlich den exportierten Start. Bericht, Phasenlogs und vollständiges ZIP mit EXE-Paar, Anleitung und Commitkennung werden ausgegeben. Der Bericht trennt Quellhead, getesteten Checkout/Test-Merge und veränderten Arbeitsbaum. Produkt-CI speichert das Zwischenartefakt für 14 Tage, ohne Release oder Deployment.

Für K-05 müssen der Job `product` aus [P1 product verification](../.github/workflows/p1-product.yml) und `docs` aus [Setup verification](../.github/workflows/setup.yml) für den aktuellen PR-Stand tatsächlich erfolgreich sein. Der bestehende technische `preflight` bleibt zusätzlich aktiv. Ein Headless-Start oder eine synthetische Eingabe ist keine reale Maus-/GUI-Abnahme. Bedienung, direkter Engineaufruf und Export stehen in der [P1.1-Anleitung](../prototypes/p1/README.md); Prüfumfang und offene Gates im [Prüfbericht](P1_1_VERIFICATION.md).

## Abnahme und spätere Erweiterung

Den vollständigen Diff inhaltlich gegen den Auftrag prüfen: keine versteckten Produktentscheidungen, keine unerreichbaren Pflichtquellen, unveränderte Regelkopie und konsistente Projekteinstellungen. Bei der Übernahme des Produktgesprächs insbesondere bestätigte Anforderungen von Empfehlungen und offenen Fragen trennen. Die fachliche Dokumentabnahme erfolgt vor Merge durch den Eigentümer. Ein getrennter Selbstreview ist keine unabhängige Zweitprüfung. Reine Dokumentpakete liefern kein Produktverhalten und benötigen keine vorgetäuschte Spiel-/Grafikabnahme.

Für den gesamten P1-Produktmerge gelten A-01 bis A-07 und M-01 bis M-04, M-06/M-07 aus [PROTOTYPE_P1.md](PROTOTYPE_P1.md), Abschnitt 8. M-05 ist durch D-06 nicht anwendbar. #8 ist eine Zwischenlieferung im Draft, keine vorgezogene Mergefreigabe. **K-06 bleibt offen:** Eigentümer prüft das gelieferte Windows-Artefakt mit echter Maus vor Start von #9 oder überspringt dies ausdrücklich. Szenario, Artefaktkennung, tatsächliche Skalierung und Ergebnis sind zu protokollieren.

Eine grüne Setup-CI allein reicht für Produktarbeit nicht. Spätere Pakete erweitern ihren tatsächlichen Test-/Export- und Abnahmeumfang im selben Paket; F-02/F-03, Zoom/Pan, Persistenz und integrierte Abnahme sind mit #8 noch nicht geliefert. Eine technisch oder visuell geprüfte Fassung ist nicht automatisch manuell abgenommen.

## Daten und Betriebswirkung

Aktuell richtet das Repository keine Laufzeitdienste oder Produktionsdaten ein. Prüfungen verwenden isolierte temporäre Testdaten; kein Zugriff auf echte Spielstände, private Daten oder kostenpflichtige Dienste aus einer bloßen Entwicklungsfreigabe. Der P1.0-Preflight lädt die zwei benannten öffentlichen Godot-Release-Assets, verwendet sie ausschließlich temporär beziehungsweise in einem expliziten externen Cache und erzeugt ein kurzlebiges CI-Artefakt. Neue Abhängigkeiten und Assets vor Aufnahme auf Notwendigkeit und Nutzungsrechte prüfen; keine Secrets einchecken.

Die eingerichteten Prüfpfade starten Setup-, Preflight- und P1-Produkt-CI mit lesenden Repositoryrechten. Kein Produktdeployment, Release, Tag oder Hosting wird eingerichtet. Externe Automatisierungen außerhalb der gelesenen Repositoryquellen sind nicht als überprüft behauptet. Spätere Änderungen der Betriebswirkung im zuständigen Paket dokumentieren.

Die [ChatGPT-Projekteinstellungen](CHATGPT_PROJECT_INSTRUCTIONS.md) werden nach dem Setup-Merge separat durch den Nutzer eingesetzt. Die neue lokale Modellheuristik ersetzt allgemeine alte Modellanweisungen einschließlich eines etwaigen Pflichtverweises auf `Codex-Empfehlung.txt`; keine zweite Heuristik parallel aktivieren.
