# Arbeitsablage für die Rätselproduktion

[KAT-1](../../docs/CATEGORIES.md): Zu Beginn Kategorienquelle und vorhandenen Fundus lesen. Neue äußere Records führen `category_id`, sobald die Motivzuordnung feststeht; ein offenes Briefing darf `null` führen. Alte Records ohne Kategorie bleiben lesbar. Vor kategorisiertem ZA-1-v2-Export ist eine gültige ID Pflicht. Bei versiegelten Paketen nur den äußeren Record ergänzen: Paket, Handoff, Inventar, Freigaben, Phasenstatus und bestehende Integrationsbelege bleiben erhalten.

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

## Abschluss

Diese Ablage enthält ausschließlich laufende Produktion. Nach Endabnahme und
nachgewiesenem Merge auf main werden alle Arbeitsrevisionen der fertigen ID samt
Indexeinträgen entfernt, gemäß PUZZLE_AUTHORING §9. Unter `content/packages/`
bleibt nur der kompakte Integrationsdatensatz. Keine dauerhafte Replaypflicht;
Runtime-Dateien und Nutzungshinweise bleiben erhalten.
