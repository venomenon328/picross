# Picross: modularer Entwicklungsworkflow v2

Stand: 05.11.2026 · Auftrag [#517](https://github.com/venomenon328/picross/issues/517).

## Geltung und Herkunft

[WORKFLOW](dev-rules/WORKFLOW.md), [CI-Vertrag](dev-rules/CI_CONTRACT.md), [Arbeitsablage](dev-rules/WORKSPACE.md) und [Übergabe](dev-rules/HANDOFF.md) sind generisch. Dieses Profil bindet ihre tatsächliche Picross-Ausführung. Der lokale Regelstand wird ausdrücklich weiterentwickelt; `venomenon328/dev-rules` und andere Projekte werden nicht geändert.

Diese Lieferung ersetzt frühere automatische Vollauswahl, verpflichtende Gesamtlaufzeiten, feste CI-Artefaktmengen, pauschale technische Uploads und den P3-A-Fingerprint-Freigabeprozess. Die alten CI2-/P3-A-Berichte bleiben historische Nachweise. Produktgarantien und erforderliche aktuelle Abnahmen werden dadurch nicht aufgehoben. PR #516 und dessen tatsächliche Integration werden separat behandelt; neue Module verwenden die jeweils aktuellen nativen Reader/Verträge.

## Automatischer Kern

[Package CI](../.github/workflows/ci-modular.yml) läuft für PRs und main; die stabilen Checks heißen `docs` und `ci-required`.

- `docs`: aktuellen Paketplan prüfen, kleine Plan-/Ergebnisregressionen, Dokumentintegrität und Metadatencheck gegen neue generierte Archivklassen. Kein vollständiges `unittest discover` im Kern.
- `ci-required`: echte erfolgreiche Kernprüfung voraussetzen, Plan aus ursprünglichem Ereignis/Quellcommit erneut lesen, reguläres Windows-x64-Paket erstellen und ausschließlich angeforderte Zusatzmodule ausführen. Originale der gewählten nativen/Fachmodule werden im selben Job unabhängig geprüft.
- Windows-Download: EXE, Konsolenhilfe, PCK, Anleitung und Lizenzen; ein flaches ZIP durch den Uploaddienst. Kein Technikbaum. Ein Linuxexport ist kein behaupteter nativer Windows-Start. Bei gewähltem `native.export` wird dessen geprüftes Paket wiederverwendet statt doppelt gebaut.
- main führt nur diesen Kern aus und übernimmt keine Zusatzmodule des gerade abgeschlossenen Pakets. Reine Dokument-/Inhalts-PRs erhalten ebenfalls den Windows-Build; dies ersetzt ausdrücklich den früheren buildfreien Inhaltspfad, ohne neue Rätselzertifizierung.

## Paketplan und verfügbare Module

[.ci/package.json](../.ci/package.json) gehört zum aktuellen PR und muss gegenüber dessen Basis geändert sein. Kein Plan, unbekannte/duplizierte Module oder fehlende Testlebenszyklusentscheidung sind Fehler; es wird nicht ersatzweise alles gestartet. Der Plan bindet Issue, Paket, Auswahl, Zweck, bewusst ausgelassene Abdeckung, Änderungen an Tests/Kern und optionale technische Aufbewahrung. Neue Pakete setzen `evidence.mode` standardmäßig auf `none`.

| Modul | Tatsächlicher Umfang |
| --- | --- |
| `tools` | Vorhandene Python-Werkzeugtests; nur bei passendem Paketbedarf |
| `preflight` | Gebundene Toolchain-/Smoke-/Exportprüfung |
| `native.core`, `native.history`, `native.catalog`, `native.completion`, `native.adapters`, `native.graphics`, `native.export` | Unabhängige Gruppen des aktuellen nativen Harness; aktuelle Gruppenverträge und Reader |
| `production.solver`, `production.images`, `production.adapter`, `production.catalog` | Bestehende synthetische Fachgruppen und zugeordnete Integrationen |
| `delivery` | Regulärer Webbuild und isolierte lokale SSH-/HTTP-Referenz; kein Live-Deployment |

Chromium bleibt ein separat ausdrücklich manuell gestarteter Diagnosepfad. Allgemeine Module, `tools` oder ein gemeinsamer Dateipfad starten keinen Browser. Der alte [Diagnoseworkflow](../.github/workflows/ci-chromium.yml) besitzt keine automatischen PR-/Push-Trigger; sein Ergebnis heißt `Diagnostic result`, nicht `ci-required`. Alte Auswahl-/Lifecyclehelfer sind kein zweiter aktueller Normvertrag. Ein manueller Diagnosevollumfang erteilt keine dauerhafte Pflicht.

Der manuelle Einstieg in Package CI erlaubt die ausdrücklich angegebenen Module, standardmäßig keine; er übernimmt keine gespeicherte Feature-Uploadanforderung. Die Auswahl allein beweist keine fachlich ausreichende Abdeckung: diese Entscheidung gehört in Spezifikation und Review.

## Laufzeit und Artefakte

Weiches Ziel: **600 Sekunden / zehn Minuten**. Der Runner warnt bei Überschreitung und arbeitet weiter. Die weiche Uhr beginnt vor dem ersten Checkout und umfasst Kernprüfung, Wartezeit zwischen Jobs, Setup und Verifikation bis zum Upload. Verifikation, Modulzeiten und Byteumfang werden getrennt gemessen; anfängliche Queuezeit und endgültige Gesamtlaufzeit einschließlich Upload kommen aus Actions. Es gibt keine maximale Gesamtlaufzeit oder Artefaktgröße als Projekt-Erfolgsgate. Bestehende Prozess-/Netzwerk-Hängerschutzgrenzen bleiben getrennt. Allgemeine Workflow-Timeouts des alten Browserpfads werden entfernt; Plattformgrenzen werden nicht umgangen.

Ohne gesonderte Anforderung bleiben technische Originale nur im eigenen temporären Laufordner. Nach den Readerprüfungen beseitigt der Kontextmanager diesen Ordner. Der kompakte Ergebnistext steht in Actions-Log/Summary. Ein dauerhafter Sammlungskatalog entsteht nicht.

`evidence.mode=review` liefert aktuelle begrenzte Originale/Logs für den benannten Reviewer; `failure` nur bei einem Fehllauf. Beide verlangen einen Zweck und ein Datum. Uploadretention höchstens sieben Tage und nicht über die gewählte Frist hinaus, Windows vierzehn Tage. Das ist eine Aufbewahrungsregel, kein Mengenlimit. Ein späterer Bedarf wird neu angefordert. Persönliche Abnahmen dürfen erst danach terminiert werden, wenn ihr Kandidat bis dahin verfügbar bleibt oder gezielt neu gebaut wird.

## Lokale Arbeitsablage

Die im Sheet gespeicherte Codex-Wurzel wird in den Auftrag übernommen; neue eigene Daten bleiben darunter. Bereinigung ist standardmäßig beauftragt, sobald eigene Änderungen gesichert und erforderliche Reviewdaten übergeben sind. Fremde Checkouts und ungesicherte Änderungen bleiben erhalten. Dies konkretisiert [HIL-F01](https://github.com/venomenon328/picross/pull/501#issuecomment-6601103689); Full Access bleibt unverändert. Historisch blockierte Altpfade werden nicht als bereits bereinigt gemeldet.

## Sheet und Abnahme

[Entwicklungssheet](workflow/Entwicklungsworkflow_Cheat-Sheet.html): Offline-Datei mit Projekten, Browserpersistenz, Sicherungsexport, geprüftem JSON-Import und aktiver bedingter Mergeoption. Einstellungen sind browser-/originabhängig; ein anderer Browser oder verschobene lokale Datei kann einen Sicherungsimport benötigen. JSON-Import ändert keine Merge-/Bereinigungsfreigabe oder lokale Arbeitswurzel.

Squash-Merge nur auf passenden Nutzerauftrag. Review bezieht sich auf aktuellen Head und tatsächliche Package-CI; bei Befunden Nacharbeit, bei erfüllter bedingter Freigabe direkt Merge. Kein Release oder Deployment. Der Implementierer liefert ein getrenntes Selbstreview; die neue Workflowlieferung benötigt ein unabhängiges Review vor Merge.
