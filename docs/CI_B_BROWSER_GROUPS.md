# CI-B: Browserinventar und Ausführungsvertrag

## Vorrangiger Sollvertrag: CI2-A und CI2-C

Der freigegebene [CI2-Vertrag vom 26.10.2026](CI_SLIMMING.md),
[Gesamtissue #412](https://github.com/venomenon328/picross/issues/412), ersetzt
die automatische Browserpflicht und die ungekürzte Fall-/Bildmatrix dieses
Dokuments. [CI2-A / #413](https://github.com/venomenon328/picross/issues/413)
liefert den ausdrücklichen Browserauftrag;
[CI2-C / #415](https://github.com/venomenon328/picross/issues/415) liefert den
kleinen Chromiumumfang. A ist auf dem #413-Arbeitsbranch implementiert (Details in
[CI_A_SELECTION](CI_A_SELECTION.md)); C ist weiterhin unbegonnen.
Die ausführbare Ausgangsbasis bleibt `main@967314538df376a281020fb4c34f93f370a491df`.

Automatische PR-/Push-Ereignisse und allgemeine manuelle Scopes starten keinen
Browser. Ein ausdrücklich angeforderter Chromiumlauf bindet Quellstand und
Umfang. Der kurze Umfang ersetzt die 33 Szenarien durch ungefähr 8–10 aktuelle
Kernfälle: regulärer Start, Katalog/Sortierung, echte Bearbeitung/Undo/Redo,
relevanter Resize-/DPI-Wechsel, kleiner Abschluss/Reset, bestätigte Sicherung mit
Reload und Prozessneustart, Zweittab/Sperre sowie Schreibfehler/Retry.
KU-/AT-/HZ-Katalogschichten werden konsolidiert; zusätzliche Viewports und
Bildserien benötigen eine tatsächliche Geometrieaussage. Seltene aktuelle Fälle
werden möglichst auf einer günstigeren Ebene geprüft.

Der kurze Lauf einschließlich benötigtem Build soll höchstens acht Minuten dauern
(typisch fünf bis acht); ein ausdrücklich gewähltes zusätzliches Browserprofil
bleibt unter zehn Minuten und hat einen konkreten Zweck und begrenzten Umfang.
Kein Default hängt die alte Vollmatrix an. Nur benötigte Builds werden erzeugt;
ein angeforderter Exportwechsel verlangt weiterhin zwei echte Exporte. Echte
Eingaben, bestätigte IndexedDB-Sicherung, Reload und Prozessneustart bleiben für
ihre jeweiligen Aussagen erforderlich. Firefox bleibt aus CI ausgeschlossen.

Das neue gewählte Inventar bindet Auswahl, Producer und Gate gemeinsam. Für seine
Pflichtresultate bleiben eindeutige Vollständigkeit, Originalberichte, Dateihashes
und Quell-/Run-/Versuchsbindung verbindlich; fehlend, falsch oder übersprungen ist
kein Erfolg. Nicht angeforderte Browserprüfung benötigt keine Browserbelege.
Laufzeitziele ersetzen weder funktionale Speicher-/Animationszusagen noch die
gemessene Wirkung. Alte Logs dienen als Baseline, ohne die alte Vollroute erneut
zu starten.

## Gebundener CI-B-Ausgangsstand

Alle folgenden Fall-/Bildlisten, Auswahlregeln und Abnahmeformulierungen
dokumentieren den bisherigen Lieferstand und seine Erweiterungen. Sie sind
keine Pflicht, diese Mengen unter CI2 fortzuführen. Die bisherige ausführbare
Route und ihr Gate bleiben bis zur zusammenhängenden Umstellung unverändert;
historische Messungen und Abnahmen behalten ihren geprüften Stand.

Ausgangsbestand vor Aufteilung: `main@9ec73a5f35173d1f4f772feabba451c1d4ccd92a`.
[Issue #248](https://github.com/venomenon328/picross/issues/248) und
[CI-Policy](CI_POLICY.md) bestimmen B01–B08. Technische Abnahme und Messungen
werden im Implementierungs-PR gebunden; CI-B-R01 bleibt separat vor Merge.

## Browserpflicht der gebundenen Ausgangsbasis

Eigentümerentscheidung vom 19.10.2026 / [#261](https://github.com/venomenon328/picross/issues/261):
Firefox entfällt vollständig aus automatisierter CI. Die folgende aktuelle
Matrix umfasst ausschließlich Chromium mit allen bisherigen 27 Szenarien;
AT-A ergänzt die drei unten gebundenen Fälle auf insgesamt 30.
Historische CI-A-/CI-B-Messungen und Abnahmen behalten ihre damaligen Quellen
und Browser; die geänderte Pflicht erklärt keinen alten Lauf rückwirkend für
erfolgreich. Der sichere CI-Neustart einschließlich aktueller automatischer
Ereignisse auf alten offenen PRs folgt der [CI-Policy](CI_POLICY.md). S3 nimmt
historische Reruns aus dem Mergegate; sie werden nicht gestartet. Die alte
Workflowkette bleibt administrativ deaktiviert, Chromium erhält neue Pfade/IDs.

## Bisherige vollständige Zuordnung

Die unveränderten Szenarionamen identifizieren die vorhandenen positiven und
negativen Assertions. Chromium ist der einzige CI-Browser; die Live-DPI-Probe
nutzt weiterhin CDP. Hinzu kommt der reguläre uninstrumentierte Start.

| ID | Gruppe | Bestehende Aussage einschließlich Gegenproben |
| --- | --- | --- |
| regular-start | regular | Echter regulärer Export; Storage bereit und bestätigt, Startmeldung verborgen, keine technische Probe, tatsächlicher WebGL2-Kontext, offline nach Start, keine Konsolen-/Seitenfehler; reguläres Katalogbild. |
| B01 | persistence | delayed exclusive lock handoff waits before IndexedDB hydration |
| B02 | catalog | export/catalog startup |
| B03 | catalog | KU-A single-line metadata, footer, tooltip boundaries and passive click routes |
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

Pflichtbilder: `regular-catalog.png`, `ku-no-difficulty-tooltip.png`,
`ku-mode-tooltip.png`, `ku-1280-ui125.png`, `ku-1920-ui100.png`,
`ku-2560-ui125.png`, `ku-solved-footer.png`, `mono.png`, `colour-row-clues.png`,
`colour-column-clues.png` und die unten genannten KU-B-Bilder
(jeweils mit Chromium-Präfix). Fehlerbilder bleiben
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
Auswahl, Ausführung und Gate. `picross-ci-selection-v4` enthält zusätzlich
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

`web-chromium.yml` baut drei echte Exporte in einem eigenen Buildjob. Jeder Build verwendet
ein eigenes temporäres Projekt und den vorhandenen hashgeprüften Toolchainweg.
`builds.json` bindet Head, Base, Test-Merge, Event, Run und Auswahlversuch sowie
Buildversuch und die vollständigen Manifeste samt Manifest-SHA-256. Die beiden
technischen Exporte müssen unterschiedliche Buildkennungen und Bauzeiten besitzen.
Es werden aktuelle Builddateien desselben Runs übertragen, keine Prüfergebnisse
gecacht. Alle Chromium-Gruppen verwenden dieselbe gebundene Buildhülle.

Der Job `chromium` ruft `browser-chromium.yml` auf einem eigenen Ubuntu-24.04-Runner
auf. Dessen erster Schritt weist jeden Browserwert außer `chromium` vor jeglicher
Installation ab. Playwright 1.58.0 installiert ausdrücklich nur Chromium;
sämtliche Bundlebytes werden nach dem Download erneut geprüft. Auch
`run_groups.py`, `browser.py`, `smoke.py` und der gemeinsame direkte Launchweg
weisen unzulässige Browserwerte vor Browserstart ab. Godot bleibt 4.7.2-stable;
Mesa bleibt erhalten, die Firefox-Profiloption entfällt. Buildjob und Chromium
melden ihre eigenen Versuche; einziges Browseroutput ist `chromium_attempt`.

`ci-required` verlangt weiterhin alle ausgewählten CI-A-Jobergebnisse und
verifiziert zusätzlich Chromiums tatsächliches `web-result.json` gegen das neu
berechnete Gruppen-/Szenarieninventar. Es prüft eindeutige vollständige Gruppen,
Szenario-IDs, erfolgreiche Prozesse, Messbelege, WebGL-Daten, Originalberichte,
Pflichtbilder und sämtliche gelieferten Dateihashes. Die Originalberichte müssen
mit den aggregierten Ergebnissen und Buildmanifesten übereinstimmen. Fehlende,
leere, doppelte, unerwartete, abgebrochene, übersprungene oder
fehlgeschlagene Pflichtresultate sind kein Erfolg. Ein grünes `web`-Jobergebnis
allein genügt dem CLI-Gate ausdrücklich nicht.

Downloads verwenden den vom Scheduler gemeldeten konkreten Producer-Versuch.
Erfolgreiche Jobs dürfen beim Retry desselben unveränderten Runs erhalten bleiben:
Auswahlversuch ≤ Buildversuch ≤ Browserversuch ≤ Gateversuch. Head/Base/Test-Merge,
Event und Run müssen unverändert übereinstimmen. Keine Wildcardauswahl historischer
Resultate. Artefakte heißen `ci-web-builds-<head>-<attempt>`,
`picross-web-chromium-<head>-<attempt>` und
`picross-web-player-<head>-<attempt>`. Technische Dateien bleiben sieben Tage,
der reguläre Spieler vierzehn Tage. Profile und veränderliche Hostingbäume werden
nicht hochgeladen. SSH/HTTP und seine Artefakte bleiben vollständig eigenständig.

## Nachweise und Abnahmegrenzen

`test_ci_b.py` prüft die exakte Szenarienvereinigung, Pfadabhängigkeiten,
Misch-/Main-/manuelle Auswahl, Prozessaufrufe nach injiziertem Gruppenfehler,
fehlende/doppelte/falsche Chromium-Belege, Quell-/Run-/Versuchsbindungen,
Exportidentität und den tatsächlichen Gate-CLI-Fehler bei nur grünem Webjob.
Linux-CI führt zusätzlich die wirklichen Workflow-Shellblöcke mit synthetischen
Außenwerkzeugen aus und verlangt die Weitergabe injizierter Exit-23-Fehler.
`test_ci_chromium.py` prüft außerdem alle Browser-CLIs vor Playwright-Import,
den direkten Launchschutz und den ersten Workflow-Schritt mit unerlaubten
Browserwerten. Diese Gegenproben ersetzen keine echten Browserläufe.

CI-B-T01 bindet im PR den vollständigen realen Lauf, repräsentative gezielte
Läufe, Baseline-/Nachhermessung, tatsächliche Job-/Phasendauern, Cache-/Runner-
bedingungen und den getrennten Selbstreview. Warteschlange, summierte Runnerzeit
und parallele Wartezeit werden getrennt ausgewiesen. CI-B-R01 bleibt eine
separate qualifizierte Prüfung vor Merge. Keine Produktabnahme, CI-C-Umsetzung,
Merge- oder Livefreigabe durch diese technische Lieferung.

## KU-B-Erweiterung der Ausgangsbasis

KU-B ergänzt `KU-B01` in `catalog` (vier Kriterien, beide Richtungen,
Gleichstände, stabile Rückkehr-ID) und `KU-B02` in `persistence` (Präferenz über
Reload, echten Prozessneustart, zweiten Export, isolierten IndexedDB-Fehler und
Wiederholung mit letzter Auswahl). Pflichtbilder sind `ku-b-sorting.png` und
`ku-b-preference-error.png`, jeweils für Chromium. Damit enthält das aktuelle
KU-B-Inventar 27 Chromium-Szenarien. Die bisherigen 26 Firefox-Szenarien
bleiben in ihren historischen Nachweisen gebunden. Die Auswahlpolitik und der
separat bekannte rote Main-Push-Befund werden hierdurch nicht repariert.

## AT-A-Erweiterung der Ausgangsbasis

`AT-W01-C` in `catalog` prüft kleine transparente Karte und Hover;
`AT-W01-E` in `completion` prüft Überblendung, Endbild und Wiederöffnung.
Beide verwenden die feste Matrix 1280×720/UI125, 1920×1080/UI100 und
2560×1440/UI125. `AT-W01-P` in `persistence` bindet begonnene und gelöste Saves
über zwei echte Bildexporte, Reload und Browserprozessneustart am gleichen
isolierten Origin/Profil. Definitionen, Registry und Saves müssen gleich bleiben.

Das Gate verlangt die 18 Originalbilder, die importierten RGBA-Proben sowie
die exportgebundenen Fixturehashes und vergleicht die angegebenen Pixel mit den
tatsächlichen PNGs. `tools/test_at_evidence.py` enthält davon getrennte
synthetische Negativkontrollen. Die zusätzliche Bildabhängigkeit ist in beiden
isolierten Web-Umgebungen über `requirements-image.txt` gepinnt. Die bestehende
Timeout- und Szenarienpflicht bleibt erhalten. Aktuelle Originalnachweise und
offene Abnahmen: [AT-A-T01](AT_A_VERIFICATION.md).

## HZ-A-Erweiterung der Ausgangsbasis

`HZ-A-W01` ergänzt `catalog` um Tidy Hand mit lokalem Fallback, vollständig
gemessene Metadaten, echte native Menüöffnung und vollständige scrollbare Hilfe
bei 1280×720/UI125, 1920×1080/UI100 und 2560×1440/UI125. Sechs zusätzliche
Originalbilder `hz-menu-<Breite>.png` und `hz-help-<Breite>.png` mit Chromium-
Präfix sind Pflicht. Das Inventar enthält damit 31 Chromium-Szenarien.
Bestehende Fälle und ihre Eingabe-/Save-/Pixelassertions bleiben erhalten.
Die AT-Katalogprüfung scrollt die verdiente Bildkarte samt Hoverziel vor dem
Pixelvergleich über echte Radereignisse vollständig in den sichtbaren Bereich.
Damit hängt sie nicht von einer bestimmten Spaltenzahl ab; sämtliche bisherigen
Weiß-, Loch-, Farb- und Alpha-Stichproben bleiben unverändert.

## HZ-C-Erweiterung der Ausgangsbasis

Auf HZ-A und HZ-B ergänzt `HZ-C-W01` in `catalog` die gemeinsame kleine
Schriftgröße, vollständige Metadaten, feste Kategorie-/Fußbereiche, alle drei
Dropdownarten offen/geschlossen und den UI-Rückwechsel. Echte Chromium-
Maus-/Tastatureingaben und unveränderte Zell-/History-/Abschlusswerte gehören
dazu. Die Beobachtungsprobe erhält keine Zustandssetter. Die 15 Originalbilder
`hz-c-{catalog,category,sort,settings,view}-{1280,1920,2560}.png` mit Chromium-
Präfix sind Pflicht; insgesamt sind es nun 33 Szenarien. Bestehende Auswahl,
Szenarien und Belegprüfungen bleiben. [HZ-C-Prüfzuordnung](HZ_C_VERIFICATION.md).
