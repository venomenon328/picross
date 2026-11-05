# Änderungen am Regelpaket

## 0.2.0-rc.2 — 2026-11-05

Lokale Konsolidierung im selben beauftragten Picross-Fork (#517), kein zentraler Release.
Auswahl von CI-Modulen und weiterhin verbindliche Akzeptanzkriterien getrennt;
verbundene Review-/Korrekturaufträge ausdrücklich von reinem Review abgegrenzt.
Sheet-JSON statt parallelem Codex-Prompt in die Ausgaberegel integriert.
Modellkatalog anhand aktueller offizieller Quellen datiert aktualisiert.
Reine Dokumente und reine Inhaltsproduktion ausdrücklich vom Player-Build ausgenommen;
Picross setzt die Ausnahme diffgebunden auch im Main-Nachlauf um.

## 0.2.0-rc.1 — 2026-11-05

Ausdrücklich beauftragter lokaler Picross-Fork (#517), kein zentraler Release.
Generischer modularer CI-/Test-/Artefaktlebenszyklus, Arbeitswurzel und Bereinigung,
versioniertes JSON-Handoff und überarbeitetes Review mit bedingter Mergefreigabe.
Picross-Ausführung steht außerhalb dieses Pakets im Projektprofil/CI_WORKFLOW_V2.


## 0.1.0-rc.2 – 2026-09-09

Überarbeiteter Abnahmekandidat nach der inhaltlichen Rückmeldung zur Modellwahl; weiterhin kein Release oder automatischer Rollout.

- Ergebnisqualität neben Zuverlässigkeit und Gesamtkosten als eigenständiges Auswahlkriterium verankert. Qualitätsgewinne können Mehrkosten auch ohne eingesparte Korrekturschleifen rechtfertigen.
- High ersetzt Medium als Standard-Reasoning. Absenkungen benötigen eine konkrete aufgabenbezogene Begründung ohne erwartbaren relevanten Qualitätsverlust.
- Redaktionelle/kuratorische Qualität von rein mechanischen Textänderungen abgegrenzt. Modellklassen und höhere Reasoning-Stufen sind keine starren Obergrenzen für kleine oder nichttechnische Aufgaben.
- Erwarteten Qualitätsnutzen auch beim bevorzugten Ausführungsweg berücksichtigen; reine Umsetzbarkeit erzwingt keine Eigenumsetzung.
- Modellkatalog, Strukturbegründung und fünf zusätzliche inhaltliche Abnahmeszenarien abgestimmt. Der inhaltlich akzeptierte Workflow, die Empfehlungstrigger und die Befugnis-/Mergegrenzen bleiben unverändert.

## 0.1.0-rc.1 – 2026-09-09

Erster Abnahmekandidat; kein veröffentlichter Release und keine automatische Aktivierung in anderen Projekten.

- Zuständigkeit von Issue, Projektprofil, Workflow und PR ausdrücklich getrennt.
- Angemessene Rückfragen und Pakete, umgebungsbezogene Startprüfung sowie kurze Übergaben definiert.
- Reviewbefunde, Abnahmen, Nacharbeiten und commitgebundene Mergefreigaben getrennt.
- Modellheuristik gegenüber der bisherigen `Codex-Empfehlung.txt` vereinfacht: Paket vor Modell prüfen, Gesamtkosten bis zur Abnahme betrachten, bevorzugten Ausführungsweg nennen.
- Aktuelle Modellnamen und Bezeichnungen in einen datierten Katalog ausgelagert.
- Im Aufbau-Review präzisiert: neue Ideen setzen kein vorhandenes Issue voraus; Schutz vor direkten Zielbranchänderungen gilt auch ohne technische GitHub-Erzwingung.

Die erste Fassung ersetzt bestehende Projektanweisungen erst nach deren expliziter, widerspruchsfreier Migration. Herkunftscommit und Übernahmeentscheidung werden im Zielrepository dokumentiert, nicht durch diese Versionsnummer allein bewiesen.

