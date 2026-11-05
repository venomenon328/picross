# picross

Ein thematisch zusammenhängendes Nonogramm-Spiel in Entwicklung: kuratierte
Bildrätsel, präzise Mausbedienung und ein illustriertes Album.

Das reguläre Godot-Spielprojekt liegt unter [game/](game/README.md). Der integrierte
Stand bietet sechs unveränderte Katalogrätsel (F01, F02, F04, F06, F08, F09),
Vollsicht, unabhängige Hinweisnavigation, Undo/Redo und lokale Save-/Backup-Recovery.
Sidebar und Atlasrenderer sind über [PR #66](https://github.com/venomenon328/picross/pull/66)
in `main` integriert. Es gibt keinen Release. Godot Standard 4.7.2-stable und
Windows sind die aktuelle Entwicklungsbindung; die endgültige Engine- und
Plattformentscheidung bleibt offen.

## Entwickeln und starten

Mit der [gebundenen Toolchain](docs/P1_PREFLIGHT.md) im Repository-Root:

```sh
godot --headless --path game --import
godot --headless --path game --script res://tests/run_tests.gd
godot --path game
```

[Spiel- und Windows-Anleitung](game/README.md) beschreibt Bedienung, Speicherort
und isolierte Exportprüfung. [Werkzeuganleitung](tools/puzzle_production/README.md)
beschreibt die separate Python-/Pillow-Umgebung für Bilder und Rätselproduktion.
Automatische Prüfungen verwenden temporäre Projekte und Profile.

## Aktuelle Entwicklungsverträge

- [AGENTS.md](AGENTS.md), [Workflow](docs/dev-rules/WORKFLOW.md) und
  [Projektprofil](docs/PROJECT_PROFILE.md): Einstieg, Pflichtquellen und Befugnisse.
- [Produktdefinition](docs/PRODUCT_DEFINITION.md) und
  [Gestaltungskonzept](docs/DESIGN_CONCEPT.md): beschlossene Ausrichtung und offene Entscheidungen.
- [P1-Vertrag](docs/PROTOTYPE_P1.md): weiterhin geltende Eingabe-, Spiel- und Saveverträge.
- [Zeichensprache](docs/UI_DRAWING_STYLE.md), [Zellrendering](docs/CELL_RENDERING.md)
  und [Rätselproduktion](docs/PUZZLE_PRODUCTION.md): aktuelle Fachverträge.
- [CI-Policy](docs/CI_POLICY.md): Paketmodule, Pflichtgate `ci-required`, weiches Laufzeitziel und befristete Nachweise.
- [Entwicklungssheet](docs/workflow/Entwicklungsworkflow_Cheat-Sheet.html): als HTML speichern
  und lokal öffnen; Projekteinstellungen und JSON-Übergaben für den nächsten Auftrag.

## Prüfen

Python 3.11+, Standardbibliothek für den kleinen Dokument-/Paketkern:

```sh
python -m unittest discover -s tools -p 'test_ci_modular.py' -v
python tools/check_docs.py
```

Die [Package-CI](.github/workflows/ci-modular.yml) liefert immer das Windows-Paket
und ergänzt ausschließlich die in `.ci/package.json` begründet gewählten Module.
Der [Paketvertrag](docs/CI_WORKFLOW_V2.md) beschreibt Auswahl und Lebenszyklus;
`tools` aktiviert bei Bedarf die vollständige Werkzeugtestsuite. `ci-required`
verlangt echte erfolgreiche Prüfungen am zugeordneten Head/Test-Merge.
Technische Uploads sind standardmäßig aus, Chromium ausschließlich manuell.
Native Renderprüfung und Windows-Spielerexport ersetzen keine persönliche Mausprobe.

## Historische Nachweise

P1 bleibt als Name des ursprünglichen Vertrags und der unveränderten Appidentität
bestehen. Frühere Prüfberichte sind Nachweise ihres jeweiligen Commits.
[Archiv und Bestandsinventar](docs/DEVELOPMENT_ARCHIVE.md) erklärt erhaltene
Referenzen, entfernte Studienprogramme und deren Commit-/Hashbindungen.
[Regelherkunft](docs/DEV_RULES_ADOPTION.md) bindet die lokale Workflowkopie;
[ChatGPT-Projekteinstellungen](docs/CHATGPT_PROJECT_INSTRUCTIONS.md) werden durch den Nutzer eingesetzt.
