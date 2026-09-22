# picross

Arbeitsgrundlage für das neue Projekt `picross`. Dieses Setup enthält Entwicklungsregeln, Projektanweisungen und deren Dokumentprüfung, noch keine Spielimplementierung.

## Einstieg

- [AGENTS.md](AGENTS.md): verbindlicher Einstieg für ChatGPT und Coding Agents.
- [Projektprofil](docs/PROJECT_PROFILE.md): aktueller Projekt- und Prüfrahmen, offene künftige Entscheidungen.
- [Gemeinsamer Workflow](docs/dev-rules/WORKFLOW.md): Spezifikation, Umsetzung, Review und Freigaben.
- [Herkunft und Aktivierung](docs/DEV_RULES_ADOPTION.md): exakter dev-rules-Stand und Übernahmeweg.
- [ChatGPT-Projekteinstellungen](docs/CHATGPT_PROJECT_INSTRUCTIONS.md): nach dem Setup-Merge einzusetzender Text.

Lieferumfang und Fortschritt stehen in den jeweiligen Issues und PRs. Das Setup trifft keine Engine-, Plattform-, Spielumfangs- oder Lizenzentscheidung. Die Python-Werkzeuge sind ausschließlich Dokumentprüfer, keine Festlegung der späteren Anwendungstechnik.

## Setup prüfen

Python 3.11 oder neuer; keine zusätzlichen Pakete. Im Repository-Root:

```sh
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/check_docs.py
```

Die [Setup-CI](.github/workflows/setup.yml) führt beide Prüfungen und einen vollständigen Whitespace-Diffcheck aus. Diese Ergebnisse belegen keine Spiellogik, Rätselqualität, Bedienbarkeit oder Plattformunterstützung. Echte Produktprüfungen werden mit dem ersten ausführbaren Produktpaket ergänzt.
