# CI-B: Browserinventar und Ausführungsvertrag

Ausgangsbestand vor Aufteilung: `main@9ec73a5f35173d1f4f772feabba451c1d4ccd92a`.
[Issue #248](https://github.com/venomenon328/picross/issues/248) und
[CI-Policy](CI_POLICY.md) bestimmen B01–B08. Technische Abnahme und Messungen
werden im Implementierungs-PR gebunden; CI-B-R01 bleibt separat vor Merge.

## Vollständige Zuordnung vor Aufteilung

Die unveränderten Szenarionamen identifizieren die vorhandenen positiven und
negativen Assertions. Beide Browser sind Pflicht; nur die Live-DPI-Probe nutzt
Chromiums CDP. Hinzu kommt der reguläre uninstrumentierte Start je Browser.

| ID | Gruppe | Bestehende Aussage einschließlich Gegenproben |
| --- | --- | --- |
| regular-start | regular | Echter regulärer Export; Storage bereit und bestätigt, Startmeldung verborgen, keine technische Probe, tatsächlicher WebGL2-Kontext, offline nach Start, keine Konsolen-/Seitenfehler; reguläres Katalogbild. |
| B01 | persistence | delayed exclusive lock handoff waits before IndexedDB hydration |
| B02 | catalog | export/catalog startup |
| B03 | catalog | KE neutral new labels and passive mode/difficulty click routes |
| B04 | input | left/right elastic stroke, atomic undo and redo branch |
| B05 | input | Escape/opposite-button/focus cancellation without phantom commit |
| B06 | persistence | second writer blocked |
| B07 | persistence | reload restores cells, complete history/redo and view |
| B08 | persistence | real browser process restart at DPI125 restores history and redo works |
| B09 | persistence | second genuine compatible export retains IndexedDB identity and progress |
| B10 | input | UI125, 720p/1080p, wheel zoom, fullscreen fit and hit geometry |
| B11 (nur Chromium) | input | live DPI change to 150 percent preserves hit geometry |
| B12 | input | left mouse moves long row/column clue windows and preserves cells |
| B13 | completion | EA completion, late caption, neutral heading, cancel, durable browser reload, origin-bound reset and repeated animation |
| B14 | completion | mono and eight-colour completion through real mouse events |
| B15 | input | 50x30 rectangle, colour ID 8 and full-grid fit |
| B16 | persistence | actual IndexedDB write failure is visible; own quit stays open; retry commits |
| B17 | persistence | abrupt tab close loses unacknowledged edit but retains last acknowledged state |
| B18 | persistence | corrupt primary reload uses valid backup without silent overwrite |
| B19 | persistence | explicit backup confirmation repairs primary through existing validation |
| B20 | persistence | incompatible revisions rejected without migration or overwrite |
| B21 | persistence | confirmed reset and slot isolation |
| B22 | persistence | real subpath startup, stable saves and offline-after-load input |
| B23 | persistence | own quit acknowledges durable sync, exits zero and reload restores saved state |
| B24 | persistence | blocked IndexedDB startup displays failure before gameplay |

Die Szenarien behalten ihre inneren Assertions: insbesondere kein IDB-Zugriff
vor Lockbesitz, dauerhaft entfernte abgebrochene Lockanfrage, volle History/Redo/
View beim Reload und Prozessneustart, zwei echte Exportbauten mit derselben
Speicheridentität, unveränderte Bytes bei Recovery-/Revisionsfehlern und echte
Bestätigungsdialoge mit fremder Slotisolation. Keine künstliche Savevorbelegung
ersetzt diese Benutzeraktionen.

Pflichtbilder: je Browser `regular-catalog.png`, `ke-difficulty-tooltip.png`,
`ke-mode-tooltip.png`, `mono.png`, `colour-row-clues.png`,
`colour-column-clues.png` (jeweils mit Browserpräfix). Fehlerbilder bleiben
zusätzliche Diagnose. Versions-/Launch-/WebGLdaten, Viewports, Lockhandoff und
die eng erlaubten Engine-Exitdiagnosen gehören weiterhin zum Bericht.

## Instrumentierte Ausgangsmessung

Der erste Implementierungscommit ergänzt ausschließlich passive Messung am
bestehenden seriellen Ablauf. `timing.py` misst tatsächliche synchrone
Playwright-Aufrufe mit exklusiven Wandzeiten und Aufrufzahlen: Navigation,
Prozessstart, Abfragen/übertragene Zustandsbytes, Eingaben, Savebestätigung,
Warten, Viewport und Screenshot. Verschachtelte Zeiten werden nicht addiert.
Die Produkt-/Fixture-/Timeoutverträge bleiben unverändert. Ein späterer
Vergleich bindet Baseline und neuen Gruppenlauf an tatsächliche Runs/Jobs.

## Unabhängige Ausführung und Auswahl

`tools/web_tests/contract.py` ist das gemeinsame versionierte Inventar für
Auswahl, Ausführung und Gate. `picross-ci-selection-v3` enthält zusätzlich
`browser_groups` und `browser_expected` (Gruppen und Szenario-IDs je Browser).
Die sechs CI-A-Bereichsergebnisse, der exakte Base-/Head-Treevergleich,
Rename-/Löschungsseiten, Inhaltsmodusschutz und enge Fachauswahl bleiben erhalten.

| Exakt geprüfte Abhängigkeit | Browsergruppen zusätzlich zu `regular` |
| --- | --- |
| `catalog_ink.gd`, `catalog_tip.gd`, `catalog_difficulty.gd` | `catalog`: reine Kartenzeichen-/Tooltip-/Etikettprojektion |
| `catalog.gd`, `catalog_card.gd` | `catalog`, `completion`, `persistence`: Karten öffnen, Reset und Recoverybedienung |
| `completion.gd` | `completion`: transiente Enthüllungsansicht |
| `gesture_counter.gd`, `clue_overlay.gd`, `clue_layout.gd` | `input`: Zeiger-/Hinweisgeometrie und transiente Anzeige |
| `gesture.gd`, `board.gd`, `full_view_board.gd`, `grid_view.gd` | `input`, `completion`, `persistence`: Eingaben erzeugen Abschlüsse und gespeicherte Zustände |
| Einzelnes `group_catalog.py`, `group_input.py`, `group_completion.py`, `group_persistence.py` | Die benannte technische Gruppe |
| Gemeinsame UI, Save/Session/Player, Webstorage, Ressourcen, Export, Fixtures, Browseraktionen, Probe, Toolchain oder unbekannte Wirkung | Alle Gruppen |

Die Runtime-Namen oben meinen die exakten Pfade unter `game/ui/` beziehungsweise
`game/model/` im ausführbaren Inventar. Neue Dateien erben keine Ausnahme.
`game/ui/main.gd` ist ausdrücklich gemeinsam. Ein Mischdiff vereinigt die
Pflichten aller Pfade. Die nach CI-A unabhängig bestimmte Zustellung bleibt
unverändert; auch ein voller Browserlauf fordert sie nicht automatisch an.

Die bisherigen manuellen Scopes behalten ihren vollständigen Browserbedarf.
Zusätzlich erweitern `browser-catalog`, `browser-input`, `browser-completion`
und `browser-persistence` um regulären Start plus die benannte Gruppe. Diese
Scopes können niemals automatisch ausgewählte Gruppen oder andere Jobs entfernen.
Automatische Main-Pushes wiederholen weiterhin keine Product-/Web-/Zustellungs-
oder Preflightläufe. Die eigene CI-B-Implementierung wählt wegen des vollständigen
Workflow-/Harnessdiffs alle bisherigen Bereiche, einschließlich nativer Untergruppen.

Jede technische Gruppe startet einen eigenen CLI-Prozess mit leerem Profil,
eigenem Loopbackport und kopiertem Hosting-/Releasebaum. `regular` verwendet den
uninstrumentierten Export. `catalog` startet frisch und prüft alle neuen Labels
und beide passiven Klickwege. `input` startet bei DPI125, richtet echte
Strich-/Undozustände ein und prüft Abbruch, Geometrie, Hinweise und Farbrechteck.
`completion` verändert einen fremden Slot durch echte Eingabe und prüft danach
beide tatsächlichen Abschlüsse samt Reload und ursprungsgebundenem Reset.
`persistence` erzeugt eigene echte Striche, Undo/Redo und einen abgeschlossenen
Farbslot, bevor seine Fehler-/Recovery-/Reset-/Unterpfadprüfungen stattfinden.
Kein Gruppenresultat oder vorbefüllter Save wird als Voraussetzung übernommen.

Die absichtlich innerhalb von `persistence` geteilte Profil-/Originfolge bleibt:
Lockhandoff → Eingaben/Undo → blockierter Zweittab → Reload → echter Prozessneustart
bei DPI125 → echter zweiter Export → bestätigte und verlorene Schreibstände →
Recovery/Revision/Reset → Unterpfad/Offline → Beenden/Reload → gesondertes Profil
mit verweigertem IndexedDB. Sämtliche Assertions und unveränderten funktionalen
Warte-/Animationszeiten bleiben erhalten. Gruppenfehler verhindern nicht den
Start der anderen ausgewählten Gruppen; sie verhindern den Gesamterfolg.

## Runner, Builds und Ergebnisgate

`web.yml` baut drei echte Exporte in einem eigenen Buildjob. Jeder Build verwendet
ein eigenes temporäres Projekt und den vorhandenen hashgeprüften Toolchainweg.
`builds.json` bindet Head, Base, Test-Merge, Event, Run und Auswahlversuch sowie
Buildversuch und die vollständigen Manifeste samt Manifest-SHA-256. Die beiden
technischen Exporte müssen unterschiedliche Buildkennungen und Bauzeiten besitzen.
Es werden aktuelle Builddateien desselben Runs übertragen, keine Prüfergebnisse
gecacht. Beide Browser müssen exakt dieselbe Buildhülle verwenden.

Die Jobs `chromium` und `firefox` rufen `web-browser.yml` auf getrennten
Ubuntu-24.04-Runnern auf. Jeder installiert ausschließlich seinen Browser aus
Playwright 1.58.0 und prüft nach dem Download sämtliche Bundlebytes erneut.
Godot bleibt 4.7.2-stable; Mesa und die dokumentierte temporäre Firefoxoption
bleiben unverändert. Der Buildjob und beide Browser melden ihre eigenen Versuche.

`ci-required` verlangt weiterhin alle ausgewählten CI-A-Jobergebnisse und
verifiziert zusätzlich beide tatsächlichen `web-result.json` gegen das neu
berechnete Gruppen-/Szenarieninventar. Es prüft eindeutige vollständige Gruppen,
Szenario-IDs, erfolgreiche Prozesse, Messbelege, WebGL-Daten, Originalberichte,
Pflichtbilder und sämtliche gelieferten Dateihashes. Die Originalberichte müssen
mit den aggregierten Ergebnissen und Buildmanifesten übereinstimmen. Fehlende,
leere, doppelte, unerwartete, einseitige, abgebrochene, übersprungene oder
fehlgeschlagene Pflichtresultate sind kein Erfolg. Ein grünes `web`-Jobergebnis
allein genügt dem CLI-Gate ausdrücklich nicht.

Downloads verwenden den vom Scheduler gemeldeten konkreten Producer-Versuch.
Erfolgreiche Jobs dürfen beim Retry desselben unveränderten Runs erhalten bleiben:
Auswahlversuch ≤ Buildversuch ≤ Browserversuch ≤ Gateversuch. Head/Base/Test-Merge,
Event und Run müssen unverändert übereinstimmen. Keine Wildcardauswahl historischer
Resultate. Artefakte heißen `ci-web-builds-<head>-<attempt>`,
`picross-web-<browser>-<head>-<attempt>` und
`picross-web-player-<head>-<attempt>`. Technische Dateien bleiben sieben Tage,
der reguläre Spieler vierzehn Tage. Profile und veränderliche Hostingbäume werden
nicht hochgeladen. SSH/HTTP und seine Artefakte bleiben vollständig eigenständig.

## Nachweise und Abnahmegrenzen

`test_ci_b.py` prüft die exakte Szenarienvereinigung, Pfadabhängigkeiten,
Misch-/Main-/manuelle Auswahl, Prozessaufrufe nach injiziertem Gruppenfehler,
fehlende/einseitige/doppelte/falsche Belege, Quell-/Run-/Versuchsbindungen,
Exportidentität und den tatsächlichen Gate-CLI-Fehler bei nur grünem Webjob.
Linux-CI führt zusätzlich die wirklichen Workflow-Shellblöcke mit synthetischen
Außenwerkzeugen aus und verlangt die Weitergabe injizierter Exit-23-Fehler.
Diese Gegenproben ersetzen keine echten Browserläufe.

CI-B-T01 bindet im PR den vollständigen realen Lauf, repräsentative gezielte
Läufe, Baseline-/Nachhermessung, tatsächliche Job-/Phasendauern, Cache-/Runner-
bedingungen und den getrennten Selbstreview. Warteschlange, summierte Runnerzeit
und parallele Wartezeit werden getrennt ausgewiesen. CI-B-R01 bleibt eine
separate qualifizierte Prüfung vor Merge. Keine Produktabnahme, CI-C-Umsetzung,
Merge- oder Livefreigabe durch diese technische Lieferung.
