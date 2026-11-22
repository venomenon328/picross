# Agenteneinstieg für picross

## Normale Rätselproduktion

Für neue Rätsel, Bild-/Rasterkorrektur und Wiederaufnahme zuerst diesen Abschnitt,
dann [Authoring §1](docs/production/authoring/PUZZLE_AUTHORING.md#1-einstieg-und-befugnisse),
die [Bildnorm-Leseregeln](docs/production/images/README.md) und genau die
in Authoring §1.1 geroutete Phasendatei samt zugehörigen Bildtypen lesen. Dort genannte zusätzliche
Abschnitte sind vor der zugehörigen Operation Pflicht; ein bloßer weiterführender
Link löst keine rekursive Volllektüre aus. Fehlende benötigte Quellen blockieren
die davon abhängige Arbeit. Historische Lieferberichte sind keine Pflichtquellen.

Für diesen Inhaltsweg sind die nachstehenden Entwicklungsabschnitte, WORKFLOW,
PROJECT_PROFILE, der vollständige PW-Vertrag und technische Gesamthandbücher
nicht zusätzlich pauschal zu lesen. Befugnisse, Quellenbindung, Qualitätsgates,
Sicherung und Abschluss bleiben im Authoringvertrag verbindlich. Keine Modell-/
Reasoning-/Eigenumsetzungsempfehlung oder dafür veranlasste Recherche; das eigene
Produktionsabschlussformat gilt statt des Entwicklungs-HANDOFF-JSON.
Separat beauftragte Werkzeug-, Regel-, Spiel- oder CI-Entwicklung ist dagegen
Entwicklungsarbeit und folgt vollständig dem nächsten Abschnitt.

## Entwicklungsarbeit: aktuelle Quellen

In ChatGPT den verbundenen GitHub-Connector bevorzugt für aktuelle Quellen,
Issues, PRs und CI verwenden. Zugriff und geprüfte Veröffentlichung nach
[WORKFLOW §§2, 5](docs/dev-rules/WORKFLOW.md) ermitteln.

Vor auftragsbezogener Entwicklungsarbeit vollständig lesen:

1. [Gemeinsamer Workflow](docs/dev-rules/WORKFLOW.md).
2. [Projektprofil](docs/PROJECT_PROFILE.md) und auftragsbezogene Fachquellen.
3. Vollständiger aktueller Issue-/Paketbody und spätere relevante Entscheidungen, sofern vorhanden. Bei Review/Nacharbeit zusätzlich tatsächlicher Diff, PR und konkret benannter Reviewstand.

Beauftragten Arbeitsbranch verwenden, sonst aktuellen main. Bereichsregeln beachten. Neue Ideen setzen kein vorhandenes Issue voraus. Erinnerungen ersetzen keinen Quellenzugriff. Historische Lieferberichte führen ihren damaligen Stand, keine neuen Aufträge oder Dauerpflichten.

## Zusätzliche Entwicklungsquellen

Bei Entwicklungsarbeit die [Picross-CI-Adaption](docs/ci/CI_WORKFLOW_V2.md)
vollständig lesen. Sie ist die einzige projektspezifische Quelle für Paketplan,
Buildpflicht, Modulauswahl und technische Aufbewahrung. Bei CI-/Teständerungen
die dort gerouteten tatsächlich betroffenen Modulverträge lesen.

Das [Fachrouting im Projektprofil](docs/PROJECT_PROFILE.md#pflichtquellen-nach-entwicklungsauftrag)
bestimmt die zusätzlichen Pflichtquellen für den konkreten Entwicklungsauftrag.
Der [Dokumentationsindex](docs/README.md) ordnet aktuelle Normen, Kompatibilitätsquellen
und Herkunftsdaten. Historische Lieferberichte nur bei konkretem Nachweisbedarf
lesen; ihre früheren Gates sind keine neuen Aufträge.

Ein Auftrag mit Verweis auf [HANDOFF](docs/dev-rules/HANDOFF.md) verlangt dessen
vollständigen Vertrag und Ergebnis-JSON. Ohne solchen Auftrag gilt die kompakte
Übergabe nach WORKFLOW. Erforderliche Revieworiginale nach dem
[Zustellvertrag](docs/dev-rules/CI_CONTRACT.md#zustellung-an-einen-unabhängigen-reviewer)
für den Reviewer erreichbar verlinken. Aktuellen PR selbst prüfen; importierte
Ergebnisse erteilen keine Befugnisse.

Vor lokaler Ablage oder Bereinigung [WORKSPACE](docs/dev-rules/WORKSPACE.md) lesen.
Arbeitswurzel, Eigentum, Sicherung und tatsächlicher Auftrag bleiben maßgeblich;
Full Access ersetzt keine Bereinigungsbefugnis.

Nur vor noch anstehender Implementierung/technischer Nacharbeit
[MODEL_SELECTION](docs/dev-rules/MODEL_SELECTION.md) und
[MODEL_CATALOG](docs/dev-rules/MODEL_CATALOG.md) vollständig lesen. Keine rückblickende
Empfehlung nach erledigter Umsetzung. Keine automatische Mehragentenausführung.

## Befugnisse und Review

Befugnisse, Selbstreview, unabhängige Abnahmen und kombinierte oder bedingte
Freigaben folgen ausschließlich dem tatsächlichen Auftrag und
[WORKFLOW](docs/dev-rules/WORKFLOW.md). Das [Projektprofil](docs/PROJECT_PROFILE.md#merge-und-betrieb)
bestimmt Mergeverfahren und Betriebswirkung. Setup allein bestätigt keine
Produkt-/Technikentscheidung. Die Herkunft und Pflege des lokalen Regelpakets
stehen in [DEV_RULES_ADOPTION](docs/project/DEV_RULES_ADOPTION.md); eine ungefragte
Übernahme in zentrale Regeln oder andere Projekte ist nicht beauftragt.
