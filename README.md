# picross

Ein geplantes thematisch zusammenhängendes Nonogramm-Spiel für PC: kuratierte klassische und farbige Bildrätsel, ein substanzielles Angebot großer Raster und eine präzise, komfortable Bedienung. Logische Erkenntnisse und größere Projekte stehen im Mittelpunkt; ein sich füllendes illustriertes Album, Sterneprogression und freiwillige Leistungsvergleiche ergänzen das Spiel. Eine perfekte Lösung erfordert einen Durchgang ohne Fehler und ohne Undo.

Unter [prototypes/p1](prototypes/p1/README.md) liegt der integrierte P1.4/G1/H1/Z2-Stand:
20×20 monochrom, 40×40 mit vier Farben und ein 100×100-UI-Stressraster. RP-3 ergänzt
im Draft ein neues aus einer realen Bilddatei importiertes 20×20-Blatt. Mausstriche mit direkter
Füllung↔X-Umwandlung, Undo/Redo, feinem monotonem Zoom/Pan, eigene interaktive Miniatur,
unnummerierte farbige Teilhinweise mit unabhängigem Zeilen-/Spalten-Panning und
motivtreuer Abschluss. Isolierte lokale Spielstände je Blatt mit Undo/Redo,
Raster-/Hinweisansicht und Primary/Backup-Recovery sind ergänzt. Keine Wertung.
P1.4 ist mit 500-Aktionen-Prüfweg und bestätigter Eigentümerprobe integriert;
[Ergebnisbericht](docs/P1_4_VERIFICATION.md). Z2-M01/M02/M03 wurden nicht durchgeführt
und für PR #33 als Gate aufgehoben. RP-1/RP-2 sind über #42/#43 integriert.
[Bildwerkzeug](tools/puzzle_production/README.md), [reale Importdateien](examples/rp3/README.md)
und [RP-3-Nachweise](docs/RP3_VERIFICATION.md) dokumentieren den neuen Produktionsweg;
unabhängiges technisches/visuelles RP-3-Review bleibt offen.

## Einstieg

- [Produktdefinition](docs/PRODUCT_DEFINITION.md): abgestimmte Ausrichtung, Rätselqualität, Varianten, UX, Progression, Spielmodi, offene Entscheidungen und grober Entwicklungsablauf.
- [Gestaltungskonzept](docs/DESIGN_CONCEPT.md): bestätigte Album-/Stilentscheidungen, noch offene Themenwahl, Umgang mit den exemplarischen Mocks und zu untersuchende Interaktionen.
- [Rätselproduktion](docs/PUZZLE_PRODUCTION.md): spezifiziertes externes Werkzeug mit Deduktionsnachweisen, Bildimport, Motivschutz und Pilotproduktion; KI ausschließlich in ChatGPT/Codex, ohne direkte Modell-API.
- [P1-Spezifikation](docs/PROTOTYPE_P1.md): Windows-/Godot-Bedienprototyp, bestätigte Eingaberegeln, Testdaten, Speicherung, Technikbindung und Abnahmevertrag. Auftrag und Ausführungsstand in [Issue #5](https://github.com/venomenon328/picross/issues/5).
- [P1-Preflight](docs/P1_PREFLIGHT.md): reproduzierbarer Download-, Hash-, Smoke-, Export- und CI-Nachweis für die gebundene Godot-Toolchain.
- [P1-Anleitung](prototypes/p1/README.md), [historischer P1.3-Prüfbericht](docs/P1_3_VERIFICATION.md) und [P1.4-Ergebnisbericht](docs/P1_4_VERIFICATION.md): Start, Mausbedienung, lokale Speicherung/Recovery und integrierte Produktprüfung mit damaliger Eigentümerabnahme.
- [AGENTS.md](AGENTS.md): verbindlicher Einstieg für ChatGPT und Coding Agents.
- [Projektprofil](docs/PROJECT_PROFILE.md): aktueller Projekt- und Prüfrahmen sowie situationsbezogene Pflichtquellen.
- [Gemeinsamer Workflow](docs/dev-rules/WORKFLOW.md): Spezifikation, Umsetzung, Review und Freigaben.
- [Herkunft und Aktivierung](docs/DEV_RULES_ADOPTION.md): exakter dev-rules-Stand und Übernahmeweg.
- [ChatGPT-Projekteinstellungen](docs/CHATGPT_PROJECT_INSTRUCTIONS.md): nach dem Setup-Merge einzusetzender Text.

Produktdefinition, Gestaltungskonzept und P1-Spezifikation trennen bestätigte Entscheidungen von Vorschlägen und offenen Details. P1 verwendet Godot Standard 4.7.2-stable als native Windows-Desktopfassung. Nach D-06 ist Maus der einzige verpflichtende P1-Eingabepfad; spätere alternative Produkteingaben bleiben unverändert. Die endgültige Produkttechnik und Betriebssystemmatrix werden damit nicht festgelegt. Python prüft Dokumente, die F-01-/F-02-Zertifikate und den isolierten Toolchain-/Produktweg. P1.1 bis P1.4, G1/H1 und Z2 sind in `main` integriert; RP-3 wird im eigenen Draft-PR geprüft. Es gibt keinen Release.

## Dokumentation prüfen

Python 3.11 oder neuer; keine zusätzlichen Pakete. Im Repository-Root:

```sh
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/check_docs.py
```

Die [Setup-CI](.github/workflows/setup.yml) führt beide Prüfungen und einen vollständigen Whitespace-Diffcheck aus. Zusätzlich prüft [P1 product verification](.github/workflows/p1-product.yml) Import, Godot-Tests, kontrollierten Start und Windows-Export und liefert ein commitgebundenes ZIP. Diese technischen Nachweise ersetzen die reale Mausprobe nicht.
