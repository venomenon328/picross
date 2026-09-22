# Projektprofil: picross

## Zweck, Quellen und aktueller Rahmen

`venomenon328/picross` befindet sich in der Produktkonzeption. Das Repository enthält Entwicklungsregeln, Projekteinstellungen, die konsolidierte Produktdefinition, ein frühes Gestaltungskonzept und eine kleine Dokumentprüfung, noch keine Spielimplementierung. Der [Workflow](dev-rules/WORKFLOW.md) ist die gemeinsame Prozessgrundlage; [AGENTS.md](../AGENTS.md) der Einstieg. Aktueller Lieferumfang und Freigaben stehen im jeweiligen Issue/PR, nicht in einer parallel gepflegten Roadmap.

Die [Produktdefinition](PRODUCT_DEFINITION.md) ist die zuständige Quelle für die bisher bestätigte Produktausrichtung. Bei Arbeiten an Produktkonzept, Rätselregeln/-inhalten, Progression/Wertung, UX/UI, Eingabe, Plattformkonzept oder Produktarchitektur vollständig lesen. Sie unterscheidet bestätigte Entscheidungen, noch zu prüfende Vorschläge und offene Details. Ihr grober Entwicklungsablauf ist keine Implementierungsfreigabe oder eigenständige Fortschrittsverwaltung.

Das [Gestaltungskonzept](DESIGN_CONCEPT.md) konkretisiert die bestätigte visuelle Grundlage und dokumentiert die noch offene Themenwahl sowie Interaktionsvorschläge. Bei Arbeiten an Thematik, Album, Motiventhüllung, UX/UI, Eingabe/Wertung oder entsprechenden Prototypen zusätzlich vollständig lesen. Die positive Rückmeldung zu den exemplarischen Mocks ist keine Abnahme sämtlicher dargestellter Details und kein Nachweis funktionierender Bedienung.

Der [Herkunftsnachweis](DEV_RULES_ADOPTION.md) bezeichnet die unveränderte Regelkopie. Eine detaillierte Umsetzungsspezifikation, Architektur und produktspezifische Teststrategie existieren noch nicht. Solche Quellen erst mit tatsächlich beschlossenen Inhalten anlegen und hier situationsbezogen verlinken; keine nicht vorhandenen Pflichtdokumente erfinden.

## Beschlossene Richtung und offene Produkt-/Technikentscheidungen

Die Produktdefinition legt das PC-Nonogramm-Konzept mit klassischen und farbigen kuratierten Bildrätseln, Großrasterfokus, früher visueller/UI-Konzeption, Offline-Solo-Spiel sowie den grundsätzlichen Progressions- und Wertungsrahmen fest. Sie ist für diese Entscheidungen maßgeblich; das ursprüngliche Repositorysetup hatte sie noch nicht getroffen.

Beschlossen sind außerdem ein sich füllendes Album, warme und ruhige handgezeichnete 2D-Gestaltung mit klaren Konturen und Farbflächen, motivtreue farbige Abschlussrepräsentationen monochromer Rätsel sowie Perfektion nur ohne Fehler und ohne Undo. Thematisches Sammelalbum und regionales Reisetagebuch bleiben Alternativen. Hypothesen und ihre Wertungswirkung, die Abgrenzung manueller Korrekturen sowie konkrete Layout-/Interaktionsdetails sind nicht allein durch den Mock entschieden.

Engine/Framework, Anwendungssprache, konkrete PC-Betriebssysteme, Datenhaltung, genaue Rätsel-/Solververträge, Fehlerzählung, Sternschwellen und Veröffentlichungs-/Lizenzdetails bleiben offen. Vor davon abhängiger Implementierung die konkreten Entscheidungen und Abnahmekriterien klären. Bereits ausdrücklich getroffene neue Nutzerentscheidungen nachvollziehbar in ihre zuständigen Quellen übernehmen, statt sie ungefragt neu festzulegen.

Insbesondere keine Godot-, Java-, Datenbank-, Windows-Werkzeugpfad- oder lokalen Testverbote allein aus anderen Projekten übernehmen. Python ist hier ausschließlich Werkzeug für die Dokumentprüfung.

## Branches und Befugnisse

Zielbranch ist `main`. Neue Arbeitsbranches gemäß gemeinsamem Workflow; Vorbereitung erzeugt standardmäßig noch keinen Branch oder PR. Ein Implementierungsauftrag erlaubt Branch, Commits, Push und Draft-PR im beauftragten Umfang. Standardmerge ist Squash nach ausdrücklicher oder passender bedingter Freigabe. Keine automatische Branchlöschung, kein Force-Push und keine direkten Änderungen am Zielbranch ohne entsprechende Befugnis.

Die einmalige Initialisierung des tatsächlich leeren Repositories ist in [Issue #1](https://github.com/venomenon328/picross/issues/1) dokumentiert. Danach läuft auch das Setup über einen eigenen PR. Technischer Branchschutz wurde nicht eingerichtet oder als wirksam verifiziert; die vereinbarten Prüfungen gelten unabhängig davon.

## Prüfweg für den Dokumentationsstand

Python 3.11 oder neuer, ausschließlich Standardbibliothek. Kleine lokale Prüfungen in einer geeigneten bestehenden Umgebung sind zulässig; ein passender aktueller CI-Nachweis kann die Abschlussprüfung liefern. Keine pauschale doppelte lokale Vollprüfung neben demselben belastbaren CI-Stand. Unbekannte lokale Ressourcen- oder Konfigurationsgrenzen vor davon betroffener Arbeit prüfen; globale Codex-Einstellungen der Nutzerworkstation sind hier nicht als geprüft bestätigt.

Verbindliche Befehle im Repository-Root:

```sh
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/check_docs.py
```

Vor Merge muss [Setup verification](../.github/workflows/setup.yml), Job `docs`, für den aktuellen PR-Head beziehungsweise zugehörigen Test-Merge-Stand erfolgreich sein. Er führt die Tests, Dokumentprüfung und `git diff --check` über das vollständige Änderungspaket aus. Fehlende, fehlgeschlagene oder übersprungene Pflichtprüfungen nicht als bestanden werten. Head, Basis und gegebenenfalls Test-Merge den Belegen zuordnen.

[check_docs.py](../tools/check_docs.py) und [seine Tests](../tools/test_check_docs.py) sind aus dem in der Herkunftsnotiz genannten dev-rules-Stand abgeleitet und auf `docs/dev-rules/` sowie die tatsächlichen Setup-Dateien angepasst. Sie prüfen erforderliche Dateien, UTF-8/LF/Abschlusszeile, nachgestellte Leerzeichen, Versionsformat und einfache lokale Inline-Markdown-Links einschließlich Paketgrenzen. Keine externe URL-Prüfung, Linkanker-, Referenzlink- oder vollständige Markdownvalidierung. Byteidentität des Regelpakets beim Einführen/Aktualisieren separat gegen den Quellcommit prüfen; der Dokumentvalidator beweist sie nicht.

## Abnahme und spätere Erweiterung

Den vollständigen Diff inhaltlich gegen den Auftrag prüfen: keine versteckten Produktentscheidungen, keine unerreichbaren Pflichtquellen, unveränderte Regelkopie und konsistente Projekteinstellungen. Bei der Übernahme des Produktgesprächs insbesondere bestätigte Anforderungen von Empfehlungen und offenen Fragen trennen. Die fachliche Dokumentabnahme erfolgt vor Merge durch den Eigentümer. Ein getrennter Selbstreview ist keine unabhängige Zweitprüfung. Reine Dokumentpakete liefern kein Produktverhalten und benötigen keine vorgetäuschte Spiel-/Grafikabnahme.

Sobald ausführbarer Produktcode hinzukommt, im selben Paket die echten Build-, Test- und gegebenenfalls Export-/manuellen Abnahmewege ergänzen und dieses Profil aktualisieren. Eine grüne Setup-CI allein ist dann kein ausreichender Produktnachweis. Konkrete manuelle Szenarien mit Akteur, Stand, Ergebnis und Zeitpunkt vor Merge oder Release bestimmen. Offene Detailentscheidungen blockieren nicht eigenständig prüfbare Dokumentänderungen, wohl aber davon abhängige Produktimplementierung.

## Daten und Betriebswirkung

Aktuell richtet das Repository keine Laufzeitdienste oder Produktionsdaten ein. Prüfungen verwenden isolierte temporäre Testdaten; kein Zugriff auf echte Spielstände, private Daten oder kostenpflichtige Dienste aus einer bloßen Entwicklungsfreigabe. Neue Abhängigkeiten und Assets vor Aufnahme auf Notwendigkeit und Nutzungsrechte prüfen; keine Secrets einchecken.

Der eingerichtete Merge-Prüfpfad startet ausschließlich die Setup-CI mit lesenden Repositoryrechten. Kein Produktdeployment, kein Release, Tag oder Hosting wird eingerichtet. Externe Automatisierungen außerhalb der gelesenen Repositoryquellen sind nicht als überprüft behauptet. Spätere Änderungen der Betriebswirkung im zuständigen Paket dokumentieren.

Die [ChatGPT-Projekteinstellungen](CHATGPT_PROJECT_INSTRUCTIONS.md) werden nach dem Setup-Merge separat durch den Nutzer eingesetzt. Die neue lokale Modellheuristik ersetzt allgemeine alte Modellanweisungen einschließlich eines etwaigen Pflichtverweises auf `Codex-Empfehlung.txt`; keine zweite Heuristik parallel aktivieren.
