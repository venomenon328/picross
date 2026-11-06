# Agenteneinstieg für picross

Vor auftragsbezogener Arbeit vollständig lesen:

1. [Gemeinsamer Workflow](docs/dev-rules/WORKFLOW.md).
2. [Projektprofil](docs/PROJECT_PROFILE.md) und auftragsbezogene Fachquellen.
3. Vollständiger aktueller Issue-/Paketbody und spätere relevante Entscheidungen, sofern vorhanden. Bei Review/Nacharbeit zusätzlich tatsächlicher Diff, PR und konkret benannter Reviewstand.

Beauftragten Arbeitsbranch verwenden, sonst aktuellen main. Bereichsregeln beachten. Neue Ideen setzen kein vorhandenes Issue voraus. Erinnerungen ersetzen keinen Quellenzugriff. Historische Lieferberichte führen ihren damaligen Stand, keine neuen Aufträge oder Dauerpflichten.

## Entwicklungsworkflow v2

Bei Entwicklungsarbeit zusätzlich [Picross-Adaption](docs/CI_WORKFLOW_V2.md) lesen.
Jedes Paket entscheidet seinen Prüfbedarf in `.ci/package.json`; der kleine Kern
liefert bei Entwicklungsänderungen das Windows-Paket; reine Dokumentenänderungen
und reine Rätselproduktion bleiben ohne Player-Build. Keine pauschal geschützten Testfamilien,
keine unbegründeten Dauerregressionen und keine automatischen Reviewgalerien.
Zehn Minuten sind ein weiches Ziel. Keine maximale CI-Laufzeit oder Artefaktgröße
als Erfolgsgate. Aktuelle technische Nachweise werden im Lauf geprüft und danach
entfernt; Upload nur mit Zweck und Ablauf. Chromium bleibt ausdrücklich manuell.

Bei CI/Tests/Artefakten zusätzlich [CI-Policy](docs/CI_POLICY.md) und die tatsächlich
betroffenen Modulverträge lesen. [CI2](docs/CI_SLIMMING.md) ist ein historischer Wegweiser,
[DEVELOPMENT_ARCHIVE](docs/DEVELOPMENT_ARCHIVE.md) ordnet Bestand und Lieferberichte zu.
Beide nur bei konkreter Herkunfts-/Bestandsarbeit zusätzlich laden.
Produktgarantien sind keine unveränderliche Liste teurer Tests. Änderungen an
Producer, weiterhin ausgewählten Readerpflichten und Normtexten konsistent halten.

Bei Aufträgen aus dem Entwicklungssheet ist [HANDOFF](docs/dev-rules/HANDOFF.md)
als verbindlicher Übergabevertrag vollständig zu lesen. Aktuellen PR stets selbst prüfen;
importierte Ergebnisse erteilen keine Befugnisse. Arbeitswurzel/Bereinigung nach
[WORKSPACE](docs/dev-rules/WORKSPACE.md); eigene entbehrliche gesicherte Arbeitsdaten
im beauftragten Rahmen entfernen, Fremdänderungen und echte Nutzerdaten erhalten.
Keine Policy-Umgehung; Blockaden und Restpfade ehrlich nennen. Full Access bleibt
unverändert. Der Benutzercheckout wird nicht als temporärer Checkout gelöscht.

## Fachrouting

| Auftrag | Zusätzlich vollständig lesen |
| --- | --- |
| Produkt/UX/Plattform | Pflichtquellen im Projektprofil, insbesondere Produktdefinition und Gestaltungskonzept |
| Schritt-4-Integrationscode, Budgets, Prüfkontext oder Publikations-/Recoveryguards | [RI](docs/PUZZLE_INTEGRATION.md) und aktuelles Paket; bestehende Ausführung und freigegebenen Sollstand unterscheiden |
| Abschlussbilder/Bildrevisionen/Katalogvorschau | [Transparenz](docs/REVEAL_TRANSPARENCY.md) und dort geroutete Produktions-/Integrationsquellen |
| UI-Schrift, kleine Rahmen, Dropdowns/Piktogramme | [HZ](docs/HAND_DRAWN_UI.md) |
| Katalog/Metadaten/Sortierung | [Darstellung](docs/CATALOG_PRESENTATION.md), [Sortierung](docs/CATALOG_SORTING.md) |
| Schwierigkeit/Analyse/Bewertung | [SD](docs/PUZZLE_DIFFICULTY.md), [SD2](docs/PUZZLE_DIFFICULTY_V2.md) und jeweils betroffene Analyse-/Kalibrierungs-/Integrationsverträge |
| Hinweisnavigation/Overlay/Cursorlinien | [HN](docs/CLUE_INTERACTION.md) |
| Zellrendering/Atlas/Cache | [Zellrendering](docs/CELL_RENDERING.md); historische PERF-A/B-Reproduktion ist keine Dauerpflicht |

Das vollständige Fachrouting steht im Projektprofil; diese Tabelle ist eine Einstiegshilfe.

Nur vor noch anstehender Implementierung/technischer Nacharbeit
[MODEL_SELECTION](docs/dev-rules/MODEL_SELECTION.md) und
[MODEL_CATALOG](docs/dev-rules/MODEL_CATALOG.md) vollständig lesen. Keine rückblickende
Empfehlung nach erledigter Umsetzung. Keine automatische Mehragentenausführung.

**Rätselproduktion bleibt eigenständig:** Normale Aufträge einschließlich Korrektur
und Wiederaufnahme folgen [PUZZLE_AUTHORING](docs/ai-workflows/PUZZLE_AUTHORING.md).
Keine Modell-/Reasoningempfehlung oder dafür ausgelöste Recherche; deren eigene
JSON-/Abschlussregeln gelten statt des Entwicklungsformats. Separat beauftragte
Werkzeug-/Spiel-/CI-Entwicklung folgt dem allgemeinen Workflow.

## Befugnisse und Review

Setup ist keine Freigabe von Engine, Sprache, Plattform oder Spielmechanik.
Keine ungeklärten Fremdassets, Secrets oder privaten Daten committen. Befugnisse
folgen dem tatsächlichen Auftrag; Umsetzung erlaubt Commit/Push/Draft-PR im Scope,
Review allein keine Korrektur. Eine ausdrücklich bedingte Mergefreigabe direkt
nutzen, sobald aktuelles Review und alle Vor-Merge-Gates erfüllt sind. Kein Merge
allein aufgrund einer Sheet-Voreinstellung. Mergeverfahren und Betriebswirkung
im Projektprofil prüfen. Keine ungefragte zentrale Regelaktualisierung;
Herkunft in [DEV_RULES_ADOPTION](docs/DEV_RULES_ADOPTION.md).

