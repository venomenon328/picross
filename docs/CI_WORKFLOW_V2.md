# Picross: modularer Entwicklungsworkflow v2

Stand: 05.11.2026 · Auftrag [#517](https://github.com/venomenon328/picross/issues/517).

## Geltung und Herkunft

[WORKFLOW](dev-rules/WORKFLOW.md), [CI-Vertrag](dev-rules/CI_CONTRACT.md), [Arbeitsablage](dev-rules/WORKSPACE.md) und [Übergabe](dev-rules/HANDOFF.md) sind generisch. Dieses Profil bindet ihre tatsächliche Picross-Ausführung. Der lokale Regelstand wird ausdrücklich weiterentwickelt; `venomenon328/dev-rules` und andere Projekte werden nicht geändert.

Dieser Vertrag ersetzt frühere automatische Vollauswahl, verpflichtende Gesamtlaufzeiten, feste CI-Artefaktmengen, pauschale technische Uploads und den P3-A-Fingerprint-Freigabeprozess. Die alten CI2-/P3-A-Berichte bleiben historische Nachweise. Produktgarantien und erforderliche aktuelle Abnahmen werden dadurch nicht aufgehoben. Module verwenden die jeweils aktuellen nativen Reader/Verträge; [P2-F-C/D03](CI_C_NATIVE_GROUPS.md#p2-f-c-v01--502-buch-lifecycle-nur-auf-ausdrücklichen-anlass) entfernt den eigenen Buch-Lifecycle auch aus dem ausdrücklich gewählten `native.export`.

## Automatischer Kern

[Package CI](../.github/workflows/ci-modular.yml) läuft für PRs und main; die stabilen Checks heißen `docs` und `ci-required`.

- `docs`: aktuellen Paketplan prüfen, kleine Plan-/Ergebnisregressionen, Dokumentintegrität und Metadatencheck gegen neue generierte Archivklassen. Kein vollständiges `unittest discover` im Kern.
- `ci-required`: echte erfolgreiche Kernprüfung voraussetzen, Plan aus ursprünglichem Ereignis/Quellcommit erneut lesen, bei buildpflichtigem Umfang das reguläre Windows-x64-Paket erstellen und ausschließlich angeforderte Zusatzmodule ausführen. Originale der gewählten nativen/Fachmodule werden im selben Job unabhängig geprüft.
- Windows-Download: EXE, Konsolenhilfe, PCK, Anleitung und Lizenzen; ein flaches ZIP durch den Uploaddienst. Kein Technikbaum. Ein Linuxexport ist kein behaupteter nativer Windows-Start. Bei gewähltem `native.export` wird dessen geprüftes Paket wiederverwendet statt doppelt gebaut.
- main führt nur diesen Kern aus und übernimmt keine Zusatzmodule des gerade abgeschlossenen Pakets. Reine Dokumentenänderungen und reine Rätselproduktion bleiben ohne Player-Build; das gilt auch im Main-Nachlauf. Quellen-/Planintegrität und Ergebnisgate bleiben erforderlich.

### Buildfreie Änderungen

Die Auswahl bindet den vollständigen Ereignis-Diff, einschließlich Löschungen und
beider Seiten einer Umbenennung. Dokumente (Markdown in den Dokumentationsbereichen,
HTML-Sheets und ihre Dokumentressourcen), reine Produktionsdateien gemäß
[`content_path`](../tools/ci_paths.py) und der aktuelle Paketplan lösen allein
keinen Player-Build aus. Das umfasst Authoringablage, registrierte Rätselinhalte,
generierte Runtime-Daten/-Bilder und deren reine Datenbereinigung. Code, gemeinsame
Spielgrafik, Werkzeug-/CI-Änderungen, unbekannte Pfade oder nicht reguläre Dateimodi
fallen nicht unter die Ausnahme. Ein gemischter Dokument-/Inhalts-PR bleibt buildfrei,
solange er ausschließlich diese Klassen enthält.

`player.required` und der Auswahlgrund stehen im Laufplan. Ohne Buildpflicht werden
weder Player erzeugt/hochgeladen noch Enginearchive wiederhergestellt. Die Wahl von
`tools` oder `production.*` erzwingt allein keinen Player. Ausdrücklich angeforderte
`native.*`, `preflight` und `delivery` benötigen dagegen die Toolchain und aktivieren
den Build; das ist zusätzlicher technischer Prüfauftrag, keine Pflicht je Rätsel.
Ein manueller Package-CI-Dispatch bleibt ein ausdrücklicher Bauauftrag. Ohne sicher
klassifizierbaren Diff wird die Ausnahme nicht angenommen.

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

Weiches Ziel: **600 Sekunden / zehn Minuten**. Der Runner warnt bei Überschreitung und arbeitet weiter. Die weiche Uhr beginnt vor dem ersten Checkout und umfasst Kernprüfung, Wartezeit zwischen Jobs, Setup und Verifikation bis zum Upload. Verifikation, Modulzeiten und Byteumfang werden getrennt gemessen; anfängliche Queuezeit und endgültige Gesamtlaufzeit einschließlich Upload kommen aus Actions. Es gibt keine maximale Gesamtlaufzeit oder Artefaktgröße als Projekt-Erfolgsgate. Bestehende Prozess-/Netzwerk-Hängerschutzgrenzen bleiben getrennt. Allgemeine Workflow-Timeouts des alten Browserpfads sind entfernt; Plattformgrenzen werden nicht umgangen.

Ohne gesonderte Anforderung bleiben technische Originale nur im eigenen temporären Laufordner. Nach den Readerprüfungen beseitigt der Kontextmanager diesen Ordner. Der kompakte Ergebnistext steht in Actions-Log/Summary. Ein dauerhafter Sammlungskatalog entsteht nicht.

`evidence.mode=review` liefert aktuelle begrenzte Originale/Logs für den benannten Reviewer; `failure` nur bei einem Fehllauf. Beide verlangen einen Zweck und ein Datum. Uploadretention höchstens sieben Tage und nicht über die gewählte Frist hinaus, Windows vierzehn Tage. Das ist eine Aufbewahrungsregel, kein Mengenlimit. Ein späterer Bedarf wird neu angefordert. Liegt eine persönliche Abnahme nach dem Ablauf, muss ihr passender Kandidat bis dahin anderweitig gesichert oder gezielt neu gebaut werden; die verfügbaren Bytes nicht nur behaupten.

### Gezielte Reviewdateien

Für erforderliche unabhängige Abnahmen gilt der [Zustellvertrag](dev-rules/CI_CONTRACT.md#zustellung-an-einen-unabhängigen-reviewer).
Der aktuelle Package-Runner stellt mit `evidence.mode=review` die Logs und die von
den gewählten Modulen bereitgestellten Diagnosedateien zusammen. Der Paketplan
hat keinen Dateifilter. Vor Wahl dieses Wegs prüfen, welche Dateien tatsächlich
im Download landen. Für gezielt lokal erzeugte PNGs oder wenn das Modul mehr
Material liefern würde, die erforderlichen Dateien auf dem separaten Reviewbranch
bereitstellen. Private lokale Laufwerkspfade werden dadurch für den Reviewer
entbehrlich. Ein konkreter Reviewbedarf löst keine allgemeinen CI-Uploads aus.

## Lokale Arbeitsablage

Die im Sheet gespeicherte Codex-Wurzel wird in den Auftrag übernommen; neue eigene Daten bleiben darunter. Bei aktivierter Bereinigungsoption beauftragt der kopierte Sheet-Prompt die Bereinigung, sobald eigene Änderungen gesichert und erforderliche Reviewdaten übergeben sind. Außerhalb des Sheets gilt der tatsächliche Auftrag. Fremde Checkouts und ungesicherte Änderungen bleiben erhalten. Dies konkretisiert [HIL-F01](https://github.com/venomenon328/picross/pull/501#issuecomment-6601103689); Full Access bleibt unverändert. Historisch blockierte Altpfade werden nicht als bereits bereinigt gemeldet.

## Sheet und Abnahme

[Entwicklungssheet](workflow/Entwicklungsworkflow_Cheat-Sheet.html): Offline-Datei mit Projekten, Browserpersistenz, wählbarer Darstellung (System/Hell/Dunkel), Sicherungsexport, geprüftem JSON-Import und aktiver bedingter Mergeoption. Einstellungen sind browser-/originabhängig; ein anderer Browser oder verschobene lokale Datei kann einen Sicherungsimport benötigen. JSON-Import ändert keine Merge-/Bereinigungsfreigabe oder lokale Arbeitswurzel.

Squash-Merge nur auf passenden Nutzerauftrag. Review bezieht sich auf aktuellen Head und tatsächliche Package-CI; bei Befunden gilt der beauftragte Review-/Nacharbeitsumfang, bei erfüllter bedingter Freigabe direkt Merge. Ein Merge startet den Main-Kern, kein Deployment. Release und manuelles Deployment brauchen eigenen Auftrag gemäß [Projektprofil](PROJECT_PROFILE.md). Der Implementierer liefert ein getrenntes Selbstreview; für #517 bleibt ein unabhängiges Review vor Merge erforderlich.

