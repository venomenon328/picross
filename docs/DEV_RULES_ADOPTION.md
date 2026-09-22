# Herkunft und Aktivierung von dev-rules

| Merkmal | Wert |
| --- | --- |
| Quellrepository | `venomenon328/dev-rules` |
| Vollständiger Quellcommit | `a662d3c2c1ba004de5bb65fbd16f8091c4abcce4` |
| Quellordner / Ziel | `rules/` / `docs/dev-rules/` |
| Paketversion | `0.1.0-rc.2` |
| Identischer Quell-/Ziel-Tree | `76f2e0b84f447658b234e1ecb41328cb541ec0ce` |
| Umfang | Fünf Dateien, bytegleich und ohne lokale Änderungen |
| Auftrag | [Issue #1](https://github.com/venomenon328/picross/issues/1), zugehöriger Setup-PR |
| Initialcommit / PR-Basis | `e7710c1244bccfa66fb73656ba84f8194bc5e586` |

Setup und Bereitstellung der Projekteinstellungen wurden am 22. September 2026 beauftragt; ein Merge ist dadurch nicht freigegeben. Der Initialcommit enthält nur eine minimale README für die notwendige PR-Basis. Die Einrichtung wird auf dem Arbeitsbranch geprüft und mit dessen ausdrücklichem Merge projektweit aktiviert. PR-Nummer, geprüfter Head, Nachweise und tatsächlicher Mergecommit stehen im verknüpften PR, ohne eine selbstreferenzierende SHA im Dateitext zu verlangen.

Kein Pilot oder Release-Tag ist Voraussetzung. Die bereits abgenommene Quellfassung wird bewusst commitgebunden übernommen; keine automatische Aktualisierung beim Agentenstart. Ihre Modellinformationen behalten das ursprüngliche Prüfdatum und sind kein neuer Verfügbarkeitsnachweis vom Setup-Tag.

Es waren keine vorhandenen Repositoryregeln zu migrieren. Lokale/globale Codex-Einstellungen außerhalb des Repositories wurden nicht geprüft oder verändert. Projektspezifische Ergänzungen stehen ausschließlich im [Projektprofil](PROJECT_PROFILE.md), nicht im Snapshot. Eine spätere Aktualisierung vergleicht Quelle und Ziel und führt Herkunft, Integration und relevante Abnahmen gemeinsam in einem Update-PR nach.

Die beiden Dokumentprüfskripte und der CI-Aufbau sind aus demselben dev-rules-Quellstand abgeleitet. Sie liegen bewusst außerhalb des unveränderten Regelpakets; angepasst sind insbesondere Zielpfade, erforderliche Setup-Dateien und Prüfgrenzen. Die CI benutzt den vorhandenen vollständigen Checkout-SHA-Pin der Quelle, keine bewegliche Action-Version.

Nach Setup-Merge den [bereitgestellten Einstellungstext](CHATGPT_PROJECT_INSTRUCTIONS.md) separat in ChatGPT einsetzen und etwaige alte allgemeine Prozess-/Modelltexte ersetzen. Diese Datei oder ein Git-Merge ändert die ChatGPT-Oberfläche nicht. Andere Projekte bleiben unverändert.
