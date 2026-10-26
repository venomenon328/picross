# CI-B: Browserinventar und Ausführungsvertrag

## Aktuelle Umsetzung: CI2-C / #415

CI2-A und CI2-B sind über PR #419/#420 in `main` integriert; Basis dieses Pakets
ist `dd56d310d942eee47448df4cdcca5e4af4a49b00`. CI2-C ist auf
`chore/415-ci2-c-chromium` implementiert. [T01 und Messbericht](CI2_C_VERIFICATION.md)
binden die tatsächlichen Prüfungen; separates CI2-C-R01 bleibt vor Merge offen.
Native Umfänge und Bestandsbereinigung bleiben CI2-D/E.

Automatische CI und allgemeine Scopes bleiben browserfrei. Nur der registrierte
`ci-chromium.yml`-Dispatch mit explizitem `browser_scope` startet Chromium.
`short` und der kompatible Browserwert `all` wählen genau neun Kernfälle;
`all` im allgemeinen `scope` bleibt browserfrei. Keine automatische Zusatzmatrix.

| ID | Gruppe | Tatsächlich geprüfter Übergang |
| --- | --- | --- |
| regular-start | regular | Uninstrumentierter Spielerstart, WebGL2, Storage, offline nach Start, keine Fehler |
| C01 | catalog | Metadaten/Tidy-Hand-Rollen, Kategorie-/Sortier-/Ansichtsmenü, Sortierung/Richtung, stabile Öffnungs-ID |
| C02 | input | Echter elastischer Strich, Rechtsstrich, atomarer Undo/Redo, Escape ohne Phantomcommit |
| C03 | input | UI100→125→100, 720p/1080p, Live-DPI150 und tatsächlicher Zelltreffer mit Undo |
| C04 | completion | 5×5-Lösung durch einen Strich, natürliche Überblendung, Endbild/Wiederöffnung, verdientes Katalogbild samt Hover, Resetabbruch und bestätigter Reset mit fremden Savebytes |
| C05 | persistence | Echter Sperrhandoff vor Hydration und abgewiesener Zweittab ohne IDB-Zugriff |
| C06 | persistence | Bestätigter IDBFS-Sync und Reload mit Zellen, History, Redo, Ansicht und Sortierpräferenz |
| C07 | persistence | Echter zweiter Browserprozess im gleichen Profil, DPI125, geladener Stand und wirksamer Redo |
| C08 | persistence | Fehler an der tatsächlichen IDB-Transaktionsgrenze, blockiertes Beenden, sichtbarer Retry und erneuter Reload |

Der normale Viewport 1920×1080/UI100 trägt die ausführliche Katalog-/Bildprüfung.
Weitere Größen stehen ausschließlich in C03. Der HZ-Rückwechsel liefert
Zustandsmessungen, keine wiederholte Fünfergalerie. Es entstehen zwölf
Erfolgs-PNGs (eins davon ein beobachteter echter Übergangsframe), ohne Überschreiben.
Keine großen Vorbereitungsdurchspiele; sämtliche Zustandsübergänge oben verwenden
Browserinput, keine Probe-Setter. Produktanimationen bleiben unverändert.

`browser_scope=regular` benötigt nur `web-player`; jede technische Kerngruppe
zusätzlich `web-test`. Der kurze Gesamtumfang baut somit zwei Exporte.
`browser_scope=export` ist ein **separates** Profil für Export-/Bildkompatibilität:
regular-start plus E01, zwei Fälle, drei Exporte einschließlich eigenständigem
`web-test-update` mit zweiter Bildrevision. E01 prüft begonnenen und gelösten
Stand über Reload und echten Prozessneustart am selben Origin. Unterschiedliche
Build-IDs/Bauzeiten und exportgebundene Bildbytes sind Pflicht; kein Alias.
Dieses Profil wird von `short`/`all` und Dateipfaden niemals ergänzt. Es benötigt
einen eigenen konkreten Auftrag; Ziel unter zehn Minuten einschließlich Build.

Build-/Browserberichte heißen `picross-web-builds-v2` und
`picross-browser-result-v2`; Auswahl-/Gesamtergebnis bleiben im v6-Schema.
Das Gate prüft exakt benötigte Exporte, Originalberichte, eindeutige Szenarien,
Ausführungslog, endliche Phasen-/Operationsmessungen, Pflichtdateien und Hashes.
Leere/fehlende/doppelte/fehlgeschlagene Ausführung scheitert. Originalinput-,
Head-/Base-/Checkout-/Run-/Versuchsbindung und Wiederholungsregeln aus A/B bleiben.
Browserkürzung ändert `at_evidence.MATRIX` für native Prüfungen nicht;
`BROWSER_MATRIX` ist getrennt. Die Originalpixelprüfung bleibt erhalten.

Seltene Varianten bleiben auf ihrer günstigsten passenden Ebene: Savevalidierung,
Recovery/Revision und Slotisolation in den bestehenden nativen Savefällen;
Sortierschlüssel/Gleichstände/Präferenzen in `game/tests/ku_b_cases.gd`;
Glyphen-/Popup-/Geometriegrenzen in HZ-/VS2-Fällen. Der schnelle Node-Test der
unveränderten `game/web/storage.js` prüft serialisierte echte Bridgecallbacks
gegen synthetische FS-Antworten, fehlende Persistenzfähigkeit, Generationen,
Ansichtspending, Fehler/Retry und getrennte Präferenz-/Savefehler. Das sind keine
IndexedDB-Nachweise; diese liefern C06–C08. Node kommt vom vorhandenen Runner,
keine npm-Pakete, kein neuer Job. Native History-/Bildmengen werden hier nicht gekürzt.

Build und Browser haben Hängergrenzen von vier beziehungsweise sieben Minuten;
ein Gruppenprozess endet spätestens nach 360 Sekunden als Fehler. Diese Grenzen
behaupten keine Zielerreichung: der kurze Lauf einschließlich benötigtem Build
muss anhand tatsächlicher Jobzeiten höchstens acht Minuten erreichen. Queue,
Runner/Cache, Gruppen-/Operationszeiten sowie erzeugte/gelieferte Bilder werden
im T01 getrennt ausgewiesen. Originale dienen als Baseline; kein historischer Vollrerun.

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
