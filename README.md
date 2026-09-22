# picross

Ein geplantes thematisch zusammenhängendes Nonogramm-Spiel für PC: kuratierte klassische und farbige Bildrätsel, ein substanzielles Angebot großer Raster und eine präzise, komfortable Bedienung. Logische Erkenntnisse und größere Projekte stehen im Mittelpunkt; ein sich füllendes illustriertes Album, Sterneprogression und freiwillige Leistungsvergleiche ergänzen das Spiel. Eine perfekte Lösung erfordert einen Durchgang ohne Fehler und ohne Undo.

Das Repository enthält bisher die Produktdefinition, das frühe Gestaltungskonzept, die Spezifikation des ersten Bedienprototyps, Entwicklungsregeln, die Dokumentprüfung und eine isolierte technische Godot-Preflight-Probe, noch keine Spielimplementierung.

## Einstieg

- [Produktdefinition](docs/PRODUCT_DEFINITION.md): abgestimmte Ausrichtung, Rätselqualität, Varianten, UX, Progression, Spielmodi, offene Entscheidungen und grober Entwicklungsablauf.
- [Gestaltungskonzept](docs/DESIGN_CONCEPT.md): bestätigte Album-/Stilentscheidungen, noch offene Themenwahl, Umgang mit den exemplarischen Mocks und zu untersuchende Interaktionen.
- [P1-Spezifikation](docs/PROTOTYPE_P1.md): Windows-/Godot-Bedienprototyp, bestätigte Eingaberegeln, Testdaten, Speicherung, Technikbindung und Abnahmevertrag. Auftrag und Ausführungsstand in [Issue #5](https://github.com/venomenon328/picross/issues/5).
- [P1-Preflight](docs/P1_PREFLIGHT.md): reproduzierbarer Download-, Hash-, Smoke-, Export- und CI-Nachweis für die gebundene Godot-Toolchain.
- [AGENTS.md](AGENTS.md): verbindlicher Einstieg für ChatGPT und Coding Agents.
- [Projektprofil](docs/PROJECT_PROFILE.md): aktueller Projekt- und Prüfrahmen sowie situationsbezogene Pflichtquellen.
- [Gemeinsamer Workflow](docs/dev-rules/WORKFLOW.md): Spezifikation, Umsetzung, Review und Freigaben.
- [Herkunft und Aktivierung](docs/DEV_RULES_ADOPTION.md): exakter dev-rules-Stand und Übernahmeweg.
- [ChatGPT-Projekteinstellungen](docs/CHATGPT_PROJECT_INSTRUCTIONS.md): nach dem Setup-Merge einzusetzender Text.

Produktdefinition, Gestaltungskonzept und P1-Spezifikation trennen bestätigte Entscheidungen von Vorschlägen und offenen Details. P1 ist als native Windows-Desktopfassung mit Godot und reduziertem Umfang ohne Wertung, Live-Fehlerhilfe oder Hypothesen spezifiziert. Die endgültige Produkttechnik und Betriebssystemmatrix werden damit nicht festgelegt. Die Python-Werkzeuge prüfen Dokumente und führen den isolierten P1.0-Toolchain-Smoke aus. P1-Spielimplementierung und manuelle Bedienabnahme sind noch nicht erfolgt; der technische Smoke ist kein Prototyp-Merge.

## Dokumentation prüfen

Python 3.11 oder neuer; keine zusätzlichen Pakete. Im Repository-Root:

```sh
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/check_docs.py
```

Die [Setup-CI](.github/workflows/setup.yml) führt beide Prüfungen und einen vollständigen Whitespace-Diffcheck aus. Diese Ergebnisse belegen keine Spiellogik, Rätselqualität, Bedienbarkeit oder Plattformunterstützung. Echte Produktprüfungen werden mit dem ersten ausführbaren Produktpaket ergänzt.
