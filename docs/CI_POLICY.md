# Aktuelle CI-Policy

Maßgeblich ist [Picross Workflow v2](CI_WORKFLOW_V2.md) aus [#517](https://github.com/venomenon328/picross/issues/517), zusammen mit dem generischen [CI-Vertrag](dev-rules/CI_CONTRACT.md). Die ausführbare Haupt-CI ist [Package CI](../.github/workflows/ci-modular.yml).

## Verbindliche aktuelle Auswahl

Kleiner Kern, tatsächlicher Windows-Build und genau die im aktuellen Paketplan gewählten Module. Keine pauschal geschützten Testfamilien, keine automatische Vollauswahl unbekannter Pfade und kein Fortführen vergangener Featurepflichten durch veraltete Liefertexte. Bewusste Testkürzungen brauchen Gründe und konsistente Producer-/Reader-/Vertragsänderung; Produktgarantien bleiben bestehen.

Ausgewählte native und Fachmodule behalten ihre aktuellen tatsächlichen Prüfungen gemäß [nativen Gruppen](CI_C_NATIVE_GROUPS.md) und [Fachgruppen](CI_A_SELECTION.md). Deren frühere automatische Auswahl, Uploadpflicht und Vollumfangsstandards sind durch v2 ersetzt. Fehlende oder ungültige angeforderte Originale bleiben Fehler. Chromium ausschließlich ausdrücklich manuell, keine automatische Browserinstallation. Der echte Rätselkatalog wird weder neu zertifiziert noch als wachsender Testkorpus verwendet.

Zehn Minuten sind ein weiches Ziel, kein Hardgate. Keine maximale CI-Artefaktgröße. Prozess-Hängerschutz und funktionale Ressourcen-/Zeitverträge bleiben eigenständige technische Regeln. Neue allgemeine Workflow-Zeitlimits sind kein Ersatz für Optimierung.

## Ausgabe und Aufbewahrung

Das reguläre Windows-Paket ist verpflichtend. Technische Dateien werden im erzeugenden Job geprüft und danach verworfen. Nur befristet und zweckgebunden angeforderte Review-/Fehlerdaten werden zusätzlich hochgeladen. Kein technischer Dauerupload, keine routinemäßigen Filme/Galerien und keine Doppelverpackung des Spielers. Dauerhafte Bildreferenzen dienen einer aktuellen Regression und enthalten nur deren letzten abgenommenen Stand.

Aktive Produktressourcen, Nutzungsrechte, echte Nutzerdaten und kompakte Freigaben sind keine entbehrlichen Prüfarbeitsdaten. Die Bereinigung eigener Arbeitsordner folgt [WORKSPACE](dev-rules/WORKSPACE.md). Historische Policyblockaden werden nicht umgangen oder rückwirkend als erledigt ausgegeben.

## Historische Quellen

Die umfassende Vorgängerpolicy mit CI2-, P3-A-, P2- und einzelnen Produktlieferständen ist am [Vorgängercommit](https://github.com/venomenon328/picross/blob/50b5a291495a8f6a024c049abd7dc5f94d05646e/docs/CI_POLICY.md) abrufbar. Sie ist kein zweiter aktueller CI-Vertrag. [CI2](CI_SLIMMING.md), [Bestandsinventar](DEVELOPMENT_ARCHIVE.md) und frühere Lieferberichte behalten ihre historischen Bindungen; sie werden nicht routinemäßig reproduziert. Spezifische noch offene Produktabnahmen stehen im jeweiligen Issue/PR.
