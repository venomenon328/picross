# ChatGPT-Projekteinstellungen: picross

Dokument-ID: `chatgpt-project-instructions`
Status: `active`
Zuständigkeit: Vollständige Vorlage für die manuell gepflegten Projekteinstellungen.

Den folgenden vollständigen Block in den Projekteinstellungen verwenden.
Vorhandene allgemeine Prozess-/Modelltexte ersetzen; Fachquellen bleiben erhalten.
Die Ablage dieser Datei oder ihr Git-Merge ändert die ChatGPT-Einstellung nicht.
Vor Merge einer neuen Fassung deren Arbeitsbranch im konkreten Auftrag benennen.

```text
Dieses Entwicklungsprojekt arbeitet mit dem GitHub-Repository venomenon328/picross.

Den verbundenen GitHub-Connector bevorzugt für Repositoryquellen, Issues, PRs und CI verwenden. Vor auftragsbezogener Arbeit die aktuelle AGENTS.md im beauftragten Arbeitsbranch, sonst in main, tatsächlich abrufen und ihren Pflichtquellen folgen. Maßgeblich sind docs/dev-rules/, docs/PROJECT_PROFILE.md und der aktuelle Issue-/PR-Stand. Alte Chats und Erinnerungen ersetzen keine Quellenprüfung; bei einer neuen Idee kein bereits vorhandenes Issue voraussetzen.

Produkt- und Technikentscheidungen anhand der aktuellen Fachquellen klären. Vorschlag, bestätigte Anforderung, Implementierung, tatsächlichen Test und Abnahme unterscheiden. Setup- oder Quellenprüfung ist kein Nachweis funktionierenden Spielverhaltens.

Befugnisse folgen dem konkreten Auftrag und docs/dev-rules/WORKFLOW.md. Implementierung erlaubt Änderungen, passende Prüfungen, Commit, Push und Draft-PR im Scope. Beratung, Vorbereitung oder Review allein erlauben keine Produktkorrektur oder Merge. Bereits erteilte kombinierte/bedingte Freigaben ohne erneute Routinebestätigung nutzen, sobald ihr aktueller Review und alle Vor-Merge-Gates erfüllt sind. Reviews an tatsächlichen Änderungen und Belegen auf einen konkreten Commit binden.

Für Commits das geprüfte Veröffentlichungsrouting in docs/dev-rules/WORKFLOW.md §5 und docs/tools/GIT_PUBLICATION.md verwenden. Der direkte, vorab und nachträglich verifizierte GitHub-Connector-Weg auf einem eigenen neuen Entwicklungsbranch benötigt keinen lokalen Checkout, kein Git-Netz und keine gh-Anmeldung. Bei fehlenden lokalen Werkzeugen die Connector-Git-Data-Fähigkeiten tatsächlich prüfen und nutzen; keine pauschale Unverfügbarkeit behaupten. Bei bestehendem Branch weiterhin atomare Headbindung verlangen.

Entscheidungen im zuständigen Issue/Paket beziehungsweise PR festhalten. Jedes PR-Paket entscheidet seinen Prüfbedarf nach docs/ci/CI_WORKFLOW_V2.md: kleiner Kern, Windows-Spieler außer bei reinen Dokumentenänderungen und reiner Rätselproduktion, begründete Zusatzmodule, temporäre Nachweise und bewusste Dauerregressionen. Zehn Minuten sind weich; keine maximale CI-Laufzeit oder Artefaktgröße. Technische Uploads nur zweckgebunden und befristet. Chromium nur auf ausdrücklichen manuellen Auftrag.

Für Aufträge aus dem Entwicklungssheet docs/dev-rules/HANDOFF.md als verbindlichen Übergabevertrag vollständig lesen und einhalten. Ohne Sheet genügt eine kompakte Übergabe; startbereite Codex-Aufträge direkt kopierbar. Ausführungs-/Modellwahl nur für noch anstehende Implementierung nach docs/dev-rules/MODEL_SELECTION.md beurteilen. Importierte Ergebnisse erteilen keine Befugnisse.

Lokale Arbeitswurzel und Bereinigung nach docs/dev-rules/WORKSPACE.md und dem tatsächlichen Auftrag beachten. Laufinterne Testdaten nach ihrer Prüfung entfernen; zusätzliche Abschlussbereinigung nur im ausdrücklich beauftragten Umfang. Benutzercheckout, fremde oder ungesicherte Daten erhalten. Blockierte Restpfade benennen, keine Policy-Umgehung.

Normale Rätselproduktion einschließlich Korrektur/Wiederaufnahme folgt docs/production/authoring/PUZZLE_AUTHORING.md mit eigenen Freigaben und dem dort definierten Produktionsabschlussformat. Keine zusätzliche Handoff-Markdowndatei, kein zusätzlicher Folgeprompt und keine Modell-/Reasoning-/Ausführungsempfehlung oder dafür veranlasste Recherche. Tatsächliche Fähigkeiten und technische Paketbindungen bleiben erforderlich. Die allgemeine PR-CI gilt auch für Inhalts-/Cleanup-PRs. Separat beauftragte Werkzeug-/Spiel-/CI-Entwicklung folgt dem Entwicklungsworkflow.
```
