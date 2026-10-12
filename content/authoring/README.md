# Arbeitsablage für die Rätselproduktion

Einstieg: [Produktionsindex](index.json), verbindliche Regeln in
[PUZZLE_AUTHORING](../../docs/ai-workflows/PUZZLE_AUTHORING.md), Abschnitte 6 und 8.

`<puzzle_id>/<revision>/package.zip` enthält den aktuellen schlanken Arbeitsstand.
Die lesbare Handoffkopie und `record.json` daneben ermöglichen die Suche ohne
ZIP-Volltextindex. Eine echte finale Freigabe liegt separat in `approval.json`.
Die Dateibindungen im Record vor jeder Weiterarbeit prüfen.

Dieser Index beschreibt Produktionen, nicht den Spielkatalog. Auch ungeprüfte
Bildphasen und noch nicht endabgenommene Pakete dürfen hier liegen. Der Status
und nächste erlaubte Schritt müssen diese Grenzen ausdrücklich nennen.
Registrierte Inhalte verwaltet der Adapter unter `content/packages/` und in
`content/registry.json`. Das Offline-Cheat-Sheet gehört nicht ins Repository.
