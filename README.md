# picross

Ein geplantes thematisch zusammenhängendes Nonogramm-Spiel für PC: kuratierte klassische und farbige Bildrätsel, ein substanzielles Angebot großer Raster und eine präzise, komfortable Bedienung. Logische Erkenntnisse und größere Projekte stehen im Mittelpunkt; fehlerbasierte Progression und freiwillige Leistungsvergleiche ergänzen das Spiel.

Das Repository enthält bisher die Produktdefinition, Entwicklungsregeln, Projektanweisungen und deren Dokumentprüfung, noch keine Spielimplementierung.

## Einstieg

- [Produktdefinition](docs/PRODUCT_DEFINITION.md): abgestimmte Ausrichtung, Rätselqualität, Varianten, UX, Progression, Spielmodi, offene Entscheidungen und grober Entwicklungsablauf.
- [AGENTS.md](AGENTS.md): verbindlicher Einstieg für ChatGPT und Coding Agents.
- [Projektprofil](docs/PROJECT_PROFILE.md): aktueller Projekt- und Prüfrahmen sowie situationsbezogene Pflichtquellen.
- [Gemeinsamer Workflow](docs/dev-rules/WORKFLOW.md): Spezifikation, Umsetzung, Review und Freigaben.
- [Herkunft und Aktivierung](docs/DEV_RULES_ADOPTION.md): exakter dev-rules-Stand und Übernahmeweg.
- [ChatGPT-Projekteinstellungen](docs/CHATGPT_PROJECT_INSTRUCTIONS.md): nach dem Setup-Merge einzusetzender Text.

Die Produktdefinition trennt bestätigte Entscheidungen von Vorschlägen und offenen Details. Lieferumfang und Fortschritt konkreter Arbeiten stehen in den jeweiligen Issues und PRs. Engine, Anwendungssprache, konkrete PC-Betriebssysteme und Architektur sind noch nicht festgelegt. Die Python-Werkzeuge sind ausschließlich Dokumentprüfer, keine Festlegung der späteren Anwendungstechnik.

## Dokumentation prüfen

Python 3.11 oder neuer; keine zusätzlichen Pakete. Im Repository-Root:

```sh
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/check_docs.py
```

Die [Setup-CI](.github/workflows/setup.yml) führt beide Prüfungen und einen vollständigen Whitespace-Diffcheck aus. Diese Ergebnisse belegen keine Spiellogik, Rätselqualität, Bedienbarkeit oder Plattformunterstützung. Echte Produktprüfungen werden mit dem ersten ausführbaren Produktpaket ergänzt.
