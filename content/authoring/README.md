# Arbeitsablage für die Rätselproduktion

## Freigegebener neuer Produktionsassistent · noch nicht implementiert

[PW / #578](../../docs/PRODUCTION_WORKSPACE.md) spezifiziert den Git-gestützten
Assistenten mit Launcher, Originalbildern und künftig fünf Schritten. PW-A
ergänzt für neu veröffentlichte Arbeitsstände eine geprüfte `workspace.json`
neben dem Record; der Dienst findet sie über den bestehenden Index und löst
Bilder selbst aus Git/Paketen auf. Keine manuellen Bild-/ZIP-/Routine-JSON-Importe.
Der Projektor erstellt ausschließlich die neue Ansichtsdatei; der HTTP-Dienst
ändert keine Projektdateien. Git-Sicherung bleibt beauftragte Produktionsarbeit.

**Bestehende WIP sind kein Kompatibilitätsziel:** keine Migration, nachträgliche
Projektion oder Alt-Sitzungsunterstützung erforderlich. Das ist kein Auftrag,
vorhandene Arbeitsdateien zu löschen. Integrierte Inhalte und kompakte Belege
bleiben erhalten. Die nachstehenden Ablageformen beschreiben den derzeitigen
Iststand. PW-B führt die neue fünfstufige Authoringfassung samt Verbrauchern
konsistent ein; Hintergrundgestaltung wird Schritt 4, Integration Schritt 5.
Dieser Dokumentstand allein aktiviert den neuen Default noch nicht.

## Derzeitige Ablage

[KAT-1](../../docs/CATEGORIES.md): Zu Beginn Kategorienquelle und vorhandenen Fundus lesen. Neue äußere Records führen `category_id`, sobald die Motivzuordnung feststeht; ein offenes Briefing darf `null` führen. Alte Records ohne Kategorie bleiben lesbar. Vor kategorisiertem ZA-1-v2-Export ist eine gültige ID Pflicht. Bei versiegelten Paketen nur den äußeren Record ergänzen: Paket, Handoff, Inventar, Freigaben, Phasenstatus und bestehende Integrationsbelege bleiben erhalten.

Einstieg: [Produktionsindex](index.json), verbindliche Regeln in
[PUZZLE_AUTHORING](../../docs/ai-workflows/PUZZLE_AUTHORING.md), Abschnitte 6 und 8.

Für Rasterproduktion enthält `<puzzle_id>/<revision>/package.zip` den aktuellen schlanken Arbeitsstand.
Die lesbare Handoffkopie und `record.json` daneben ermöglichen die Suche ohne
ZIP-Volltextindex. Eine echte finale Freigabe liegt separat in `approval.json`.
Die Dateibindungen im Record vor jeder Weiterarbeit prüfen.

HP-I1b2 ergänzt eine ausdrücklich getrennte Arbeitsfamilie für nachträgliche
Hintergrundänderungen: `picross-background-adoption-request-v1` liegt unveränderlich
als `<puzzle_id>/<revision>/record.json` neben seinem vollständigen gebundenen
Dateisatz. Kein Raster-ZIP, Dummyhandoff oder nachträglich erfundener Status
`registered`. Der Index v1 behält seine Zeilen `{puzzle_id,revision,record}`;
Reader dispatchen anhand der tatsächlichen Recordkennung. Erstablage und Indexpflege
über `catalog_background_change store`, Planung/Übernahme über dessen eigene
Befehle nach [Werkzeuganleitung](../../tools/puzzle_production/README.md#hp-i1b2-eigenständiger-hintergrundwechsel-und-revisionsgenauer-abschluss)
und [Hintergrundvertrag §11](../../docs/PUZZLE_BACKGROUNDS.md#11-hp-i1b2-eigenständiger-hintergrundwechsel).
Die Mehrjob-Sheetbedienung dieses eigenen Wegs ist mit MJ-B / #490 geliefert;
sein aktueller Stand ist nicht mit dem neuen PW-Assistenten gleichzusetzen.

Dieser Index beschreibt Produktionen, nicht den Spielkatalog. Auch ungeprüfte
Bildphasen und noch nicht endabgenommene Pakete dürfen hier liegen. Der Status
und nächste erlaubte Schritt müssen diese Grenzen ausdrücklich nennen.
Registrierte Inhalte verwaltet der Adapter unter `content/packages/` und in
`content/registry.json`. Die gepflegte Vorlage des
[Offline-Cheat-Sheets](../../docs/ai-workflows/Picross_Raetselproduktion_Cheat-Sheet.html)
liegt unter `docs/ai-workflows/`; persönliche Sitzungen und Auftragsexporte gehören
nicht als zusätzliche Sheetkopien in die Authoringablage. Inhalts-/Cleanup-PRs
führen einen eigenen aktuellen `.ci/package.json` gemäß allgemeinem CI-Vertrag.

## Abschluss

Diese Ablage enthält ausschließlich laufende Produktion. Nach Endabnahme und
nachgewiesenem Merge auf main wird ausschließlich die vollständig belegte
abgeschlossene Arbeit samt zugehörigen Indexzeilen entfernt, gemäß PUZZLE_AUTHORING §9.
`retire-background-production` wählt jede Hintergrundrevision ausdrücklich; auch
eine bereits durch ein neueres Bild abgelöste tatsächliche Mainadoption darf mit
ihrem eigenen Mainbeleg abgeschlossen werden. Neuere/offene Geschwister bleiben
erhalten. `retire-production` erhält gültig getrennte Hintergrundarbeit oder
blockiert vor Mutation, statt den ganzen ID-Baum zu entfernen. Unter `content/packages/`
bleibt nur der kompakte Integrationsdatensatz. Keine dauerhafte Replaypflicht;
Runtime-Dateien und Nutzungshinweise bleiben erhalten.

