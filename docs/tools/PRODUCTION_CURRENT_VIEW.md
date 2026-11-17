# Motivbezogene aktuelle Ansichtsübergabe

Status: active · [PROD-SLIM / #700](https://github.com/venomenon328/picross/issues/700)

## Aktueller Vertrag

Neue Produktion verwendet einen kanonischen aktuellen Record und den gemeinsamen
Verweisindex nach [PW-B](PW_B_CONTRACT.md). Es entsteht kein zweiter dauerhafter
Ansichtssnapshot und kein Pointer pro Job. Liste, Angebote, Originalbilder und
Folgeauftrag werden direkt aus demselben fixierten Gitstand abgeleitet.
Der lesende Dienst erzeugt keine Dateien oder Entscheidungen im Inhaltscheckout.

## Lesen und Quellenrelation

Die Hauptauswahl gruppiert nach ID. Im konfigurierten Remotebetrieb führt die
aktuelle gültige Spitze von `content/pw/<id>` vor Main. Ohne offenen Arbeitsbranch
bleibt tatsächlich offene Mainarbeit sichtbar. Lokale Refs dienen Diagnose und
P2, ohne Remoteangebote zu ersetzen. Fehler, fehlende Dateien, Konflikte und
unbestätigter Remotestand bleiben sichtbar. Offline wird nur der letzte gebundene
Remotecache angezeigt, keine frische Bestätigung behauptet.

Passive Suche erhält Ansicht und Eingaben. Erst ausdrückliches Laden oder
Job-/Quellwechsel verwirft ungesendete Auswahlabsichten. Öffnen und Kopieren
sind keine Bildwahl oder Freigabe. Bildabrufe binden aktuelle Kandidatenkennung,
Rolle und Datei-/Inhaltsbytes. Kein Verzeichnisscan rät Angebote oder Auswahl.

## Abschluss und Prüfgrenzen

Completion bindet die tatsächlich registrierte aktuelle Lieferung. Die aktive
Liste vergleicht dieses Produktresultat mit dem frisch bestätigten Remote-Main
nach [RI-ONE](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md). Das funktioniert
auch bei einem sauberen Produktcommit ohne Arbeitsarchive und nach Squash.
Abweichender Inhalt, neue/offene Arbeit oder fehlende Mainbestätigung bleibt
sichtbar. Nach bestätigtem Abschluss entfernt Retirement ausschließlich eigene
zugeordnete aktuelle Arbeit und ihren Indexverweis. Keine defekten Ansichtslinks
und keine neue historische Receiptdatei.

Die konkrete sichere Publikation, Zustände, Invalidierung und Completionform
besitzt PW-B; Remote-/Origin-/P2-Schutz und Bedienung besitzt [PW](PRODUCTION_WORKSPACE.md).
Die gezielten synthetischen Regressionen liegen in den ausgewählten Modulen.
Es entsteht keine zusätzliche Bild-, Browser- oder persönliche Abnahmeschleife.

## Historische Formen

`picross-production-current-view-v1` und persistierte workspace-Projektionen
sind ausdrücklich alte Formen. Ihr gebundener Vertrag bleibt am
[Mainanker vor PROD-SLIM](https://github.com/venomenon328/picross/blob/d389fbad01dd01860ed949a4e1e8e0b52c21362a/docs/tools/PRODUCTION_CURRENT_VIEW.md)
erreichbar. Keine automatische WIP-Migration, Rekonstruktion oder neue normale
Publikation einer historischen Quellenkette.
