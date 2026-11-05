# Herkunft und Pflege der lokalen Regeln

## Aktueller Stand

Das Repository verwendet den ausdrücklich beauftragten lokalen Fork
`0.2.0-rc.2` aus [#517](https://github.com/venomenon328/picross/issues/517).
[WORKFLOW](dev-rules/WORKFLOW.md), CI_CONTRACT, WORKSPACE, HANDOFF und Modellregeln
bilden das portable Paket unter `docs/dev-rules/`. Projektwerte und Fachrouting
stehen im [Projektprofil](PROJECT_PROFILE.md), die technische CI-Adaption in
[CI_WORKFLOW_V2](CI_WORKFLOW_V2.md). Die Dateien sind keine unveränderte Upstreamkopie.

Änderungen am lokalen Paket erfolgen bewusst im beauftragten PR und werden in
[VERSION](dev-rules/VERSION) und [CHANGELOG](dev-rules/CHANGELOG.md) geführt.
Kein automatisches Nachladen beim Agentenstart. Eine spätere Upstreamübernahme
muss gegen die lokalen Änderungen abgeglichen werden; nicht blind überschreiben.
`venomenon328/dev-rules` und andere Projekte werden dadurch nicht geändert.
Eine Übernahme dorthin benötigt einen eigenen Auftrag.

Die Regeln des beauftragten Branches gelten für dessen Arbeit; main führt erst
nach tatsächlichem Merge die neue Fassung. Das Sheet ist eine Bedienhilfe und
aktiviert keine Repositoryregeln oder Befugnisse. Die
[ChatGPT-Projekteinstellungen](CHATGPT_PROJECT_INSTRUCTIONS.md) setzt der Nutzer
separat ein; vorhandene allgemeine Regeltexte ersetzen statt widersprüchlich ergänzen.
Lokale/globale Einstellungen außerhalb des Repositorys sind damit nicht geprüft
oder geändert.

## Ursprüngliche Übernahme

| Merkmal am Setup vom 22.09.2026 | Historischer Wert |
| --- | --- |
| Quelle | `venomenon328/dev-rules`, `rules/` |
| Quellcommit | `a662d3c2c1ba004de5bb65fbd16f8091c4abcce4` |
| Ziel | `docs/dev-rules/` |
| damalige Paketversion | `0.1.0-rc.2` |
| damaliger identischer Quell-/Ziel-Tree | `76f2e0b84f447658b234e1ecb41328cb541ec0ce` |
| Umfang | Fünf damals bytegleiche Dateien |
| Auftrag | [Issue #1](https://github.com/venomenon328/picross/issues/1) und zugehöriger Setup-PR |
| Initialcommit / PR-Basis | `e7710c1244bccfa66fb73656ba84f8194bc5e586` |

Dokumentprüfer und damaliger CI-Aufbau wurden aus demselben Quellstand abgeleitet
und projektspezifisch angepasst. #502/P3-A ergänzte später lokal den
Testlebenszyklus. #517 ersetzt diesen Zwischenstand durch den generischen
Paketvertrag und konsolidiert die aktuellen Quellen. Die vollständige
[frühere Herkunftsbeschreibung](https://github.com/venomenon328/picross/blob/f3626f28899a48fa4d783716925f7425a3eb1784/docs/DEV_RULES_ADOPTION.md)
bleibt erreichbar; damalige Setup-/Mergeaufträge sind keine heutigen Sperren oder
Freigaben. Datierte Modellquellen werden gesondert geprüft und aktualisiert.
