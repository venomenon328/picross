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
