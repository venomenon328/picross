# Reguläre Buchdarstellung · B-B / #498

Arbeitsvertrag zu [B-B-V01](https://github.com/venomenon328/picross/issues/498)
unter [#493](https://github.com/venomenon328/picross/issues/493), Basis
`2a0d9e4ae21802637dc26ff8fdf904bf27772972`. Die gewählte B-A-N06-Fassung ist
über PR #497 integriert; R08-V02 und persönliche B-A-M01 sind abgeschlossen.
[BOOK_STUDY](BOOK_STUDY.md) bewahrt die gebundenen Vorgängerbelege.
Die aktuelle B-B-Lieferung und ihre noch getrennten Gates stehen in
[B-B-T01](B_B_VERIFICATION.md). Dieser Arbeitsstand ist keine Merge-/Webfreigabe.

## Einstieg und gemeinsame Quellen

`game/main.tscn` startet ohne Zusatzargument den regulären 3D-Buchroot
`game/book/main.gd`. Windows und Web verwenden dieselbe Szene. `book/content.gd`
ergänzt die Darstellung des vorhandenen `ui/main.gd`; Registry, Definitionen,
Session, SaveStore, Sortierpräferenz, Recovery und Webstorage bleiben gemeinsam.
Der Runtimekatalog bleibt `game/data/registry.json`, abgeleitet aus der
autoritativen Inhaltsregistry. Keine festen Studienrätsel im Spieler.

`game/book/` enthält Buchkörper, Seiten, Informationsnavigation und die drei
unveränderten Materialbilder Papier/Leder/Tisch samt Import- und Herkunftsdaten.
Die Generierungsangaben bleiben erhalten; die zusätzliche B-B-Adoption erweitert
ihren Verwendungsbereich auf beide regulären Spieler. Die Nutzungsbelege liegen
auch unter `licenses/Book-{paper,leather,table}.json` im Export. Das A-Original
bleibt bytegleich als gebundene Referenz und geerbte Ressourcenabhängigkeit.
Fonts, Hinweis-/Zellgrafik und SL-Rahmen behalten ihre bisherigen Bytes/Rechte.

`game/study/book/` ist ausschließlich eine isolierte synthetische Hülle um
denselben Präsentationskern. Ihre RAM-Speicher, 27 Instanzen, Beobachter,
Prüf-/Filmprogramme und Berichte werden aus regulären Paketen ausgeschlossen.
Der PCK-Audit prüft den tatsächlichen Entrypoint und benötigte gemeinsame
Ressourcen zusätzlich zu den bisherigen Ausschlüssen; er erlaubt nicht pauschal
den Studienbaum. Die technische Webprobe erweitert denselben Buchroot und
beobachtet die laufende Präsentation auch während gesperrter UI-Captures.
Die Startprüfung `--p1-smoke` bestätigt nur Ressourcen, Fenster und Katalog;
sie spielt keine echten Katalogrätsel nach. Input und History werden in den
getrennten synthetischen Prüfwegen nachgewiesen.

## Navigation und Darstellung

Der Start zeigt den echten Katalog mit höchstens 24 aktiven Karten: zunächst
bis zu zwölf links, dann bis zu zwölf rechts. Vorhandene Filter und Sortierung
wirken global vor Pagination. Beide Hälften scrollen unabhängig; neue Filter/
Sortierung beginnen auf Seite 1, unveränderte Auswahl und Rückkehr erhalten
Seite und beide Offsets. Miniaturen zeigen den aktuellen eigenen Stand;
Motivname und Reveal bleiben bis zum gültigen Abschluss gesperrt.

Katalogblättern dauert 0,85 s; vorwärts rechts nach links, rückwärts umgekehrt.
Neue/begonnene Blätter öffnen mit drei getrennten Blättern in insgesamt 3 s.
Die große rechte Arbeitsseite erhält unveränderte Raster-, Hinweis-, Schrift-
und Trefferbudgets. Der Pfeil im rechten Kopf kehrt in 1,8 s zum gebundenen
Katalogkontext zurück. Menü öffnet Einstellungen links, Fragezeichen Hilfe
rechts. Eintritt/Rückkehr dauern 0,85 s; Wechsel zwischen beiden Informations-
seiten pannt in 0,65 s. Beide Informationsscrollstände und der Besuchsursprung
bleiben getrennt vom Arbeits-/Katalogursprung. Bewusste Optionsänderungen bleiben.

Gelöste Blätter öffnen direkt den stabilen Abschluss. Der separate Abschluss
nach einem erfolgreichen Zellcommit behält seine 2,15-s-Enthüllung und sofortige
Sicherung. Reset bleibt bestätigt und an seine konkrete ID und Herkunft gebunden.
Idle-Escape ist keine Katalognavigation. Während einer Bewegung gelten die
N01–N21-/N06-Abbruchziele; Fokusbehandlung bleibt an die Bewegungsgeneration
gebunden und erfolgt außerhalb reentranter Reparent-Callbacks. Gehaltene Eingabe
bleibt bis zum Loslassen gesperrt. F01-Tooltip-/Releaseverhalten bleibt erhalten.

Maximal drei bewegte Blätter, ein Capture-Viewport und drei Informationssnapshots;
nach Abschluss/Abbruch werden Texturen und Capture freigegeben. Materialzuordnung,
Falzgeometrie und mindestens acht physische Pixel Abstand zur ebenen Papiergrenze
folgen den abgenommenen gemeinsamen Verträgen. Die neun Textur-/Direktübergaben
behalten maximal vier Kanalstufen und mittlere Abweichung höchstens 0,1 sowie
Einpixel-/Alpha-Gegenproben.

## Speicher- und Fehlergrenzen

Vor einer Zielanimation werden gültige Ziel-ID und notwendiger Flush geprüft.
Fehlschläge lassen Quelle, ausstehenden Zustand und einen erreichbaren
Fehler-/Retry-/Recoveryweg bestehen. Die reine Präsentation eines bereits
angenommenen Ziels ist vom falliblen Wechsel getrennt: keine erneute Aktivierung
oder Sicherung durch Capture, Endpose oder Reparenting. Generation, Quellkontext
und konkrete Sessionbindung werden vor Await fixiert. Veraltete Fortsetzungen
dürfen weder neue Navigation noch verlorene Eingaben erzeugen.

Appidentität `picross · P1`, `user://p1/saves/`, Schema 1, registrierte Slots,
Definition/Revision und `user://p1/catalog-preference.json` bleiben unverändert.
Es gibt keine Migration. Gültiges Backup ohne Primary bleibt bis zur bestätigten
Übernahme schreibgesperrt; ungültige Daten werden nicht automatisch ersetzt.
Ein ungültiger Save sperrt nur sein Blatt. Leerer Katalog und Ladefehler bleiben
verschiedene Anzeigen; Einstellungen, Hilfe und Beenden benötigen keine Session.

Beenden-Button und native Fensterschließung invalidieren zunächst ausstehende
Übergänge und nutzen anschließend den vorhandenen Flush. Fehler lassen die App
offen. Web wartet bei der eigenen Beendenaktion auf bestätigten Save- und
Präferenzsync; Fehler bleiben mit Retry erreichbar. Browsergesteuerter Tab- oder
Prozessabbruch behält die Grenzen aus [WEB-1](WEB_HOSTING.md).

## Prüfzuordnung

Die nativen Gruppen bleiben nach dem vollständigen Diff ausgewählt. Kleine
bisherige Komponentenfälle hängen über `tests/book_fixture.gd` am tatsächlichen
regulären Entrypoint und gemeinsamen Layout; sie stabilisieren Bewegungen
ausdrücklich synchron. Das ist kein Zeit-/Bewegungsnachweis. Der unveränderte
Produktroot in `tests/book_integration.gd`, die gemeinsamen nativen Original-
und Handoffprüfungen sowie Windows-/Chromium-Eingaben prüfen die echten Übergänge.
`tests/book-save-v1.json` ist ein festes synthetisches Schema-1-Input mit History,
Redo, Werkzeug/Farbe, Zoom und Hinweisankern; kein echter Benutzerstand.

Die Exportgruppe führt die gemeinsame Darstellungs-/Lifecycleprüfung einmal
aus. Eine zusätzliche Studienexportmatrix ist nicht Teil von B-B. Producer,
Quellinventar `tools/book_contract.py` und unabhängiger Ergebnisguard binden
gemeinsam Originalberichte, notwendige Assertions, Phasen und Datei-Hashes.
Die 300-s-Phasengrenze bleibt. Die kurze Historyroute behält höchstens 20
Kommandos, sechs neue Transaktionen und genau zwei echte Prozesse.
Die Exportgruppe wartet unter Linux auf die bereits laufenden Katalog-/Grafik-
gruppen, bevor sie den neuen 3D-Buchnachweis beginnt. So konkurrieren diese
Software-Renderer nicht im unveränderten 300-s-Fenster; Prüfungen, Auflösung
und Phasengrenzen bleiben vollständig erhalten.
Der gemeinsame Tooltipprüfer dispatcht Austritt und Eintritt vor demselben
Frame und beobachtet nach der unveränderten Hoverwartezeit den abgeschlossenen
nativen Draw. Zusätzliche unveränderte Zwischenframes entfallen; statische
Katalogwechsel warten drei Layoutzyklen. Alle Hover-/Popup-/Pixelassertions,
Originalbilder, Gegenproben und die getrennte Bewegungsfolge bleiben erhalten.
Dies nutzt die dokumentierte Reihenfolge von
[Viewport-Eingabe](https://docs.godotengine.org/en/stable/classes/class_viewport.html#class-viewport-method-push-input)
und [SceneTree-Timern](https://docs.godotengine.org/en/stable/classes/class_scenetree.html#class-scenetree-method-create-timer),
keine beschleunigte Produktuhr oder erhöhte Abbruchgrenze.

`tools/book_windows_probe.py --build-cache <cache> --source <ziel>` exportiert
headless den regulären Windowsroot mit synthetischen Daten. Zwei kleine
Ressourcenüberlagerungen müssen den tatsächlichen PCK-Guard am alten Einstieg
beziehungsweise einer Studienbeigabe scheitern lassen. Der getrennte Desktoplauf
`--source <ziel> --output <belege> --head <sha> --fold` verwendet bytegleiche
EXE/PCK, isolierte Profile und den rein lesenden externen Beobachter. OS-Eingaben
prüfen auch einen realen Dateisystemfehler, verweigertes Fensterschließen und Retry.
Dieser exklusive Desktoplauf ist nach Eigentümerentscheidung vom 02.11.2026
nur für die aktuelle B-B-Entwicklung beauftragt. Er wird nicht automatisch in
Standardprüfungen aufgenommen. Spätere Läufe mit Fenstern/Maussteuerung benötigen
einen passenden ausdrücklichen Auftrag und vorherige Desktopfreigabe.

Chromium ist für diesen Auftrag ausdrücklich als `browser_scope=short`
beauftragt. C01–C08 verwenden die neue Buchpräsentation mit echter Eingabe,
bestätigtem IndexedDB-Sync, Reload, Prozessneustart, Tab-Sperre und Fehler/Retry.
Die neun Kernfälle und zwei benötigten Exporte bleiben der begrenzte Umfang;
kein zusätzliches Exportprofil, Firefox oder Livehosting.
Für den Linux-Softwarelauf wählt der Chromium-Harness ANGLE/OpenGL über die
vorhandene Mesa-/Xvfb-Umgebung (`PICROSS_WEB_SOFTWARE=1`) im neuen Headlessmodus
des bereits installierten Chromium (`channel=chromium`, `--enable-gpu`).
Die Diagnose auf dem Runner meldete Mesa 25.2.8/llvmpipe mit funktionierender
OpenGL-Initialisierung, aber deaktiviertem WebGL. Chromiums
[Softwaretreiberliste, Eintrag 3](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/gpu/config/software_rendering_list.json)
sperrt diesen Renderer pauschal. Ausschließlich der ausdrücklich gewählte
isolierte Linux-Softwarelauf ergänzt deshalb `--ignore-gpu-blocklist`;
normale Spielerstarts und andere Plattformen erhalten keine Startschalter.
Der implizite SwiftShader-Pfad übersprang in der neuen 3D-Szene bei etwa
360 ms pro Frame den unverändert
geforderten Alpha-Bereich 0,3–0,7. Der Lauf berichtet tatsächliche Startoptionen,
Renderer und beobachtete Überblendungsframes. Auflösung, 2,15-s-Produktuhr,
Pixelgrenzen und Zeitbudgets werden nicht verändert.

Unabhängiges B-B-R01, persönliche B-B-M01, Merge und Deployment bleiben getrennt.
Offene persönliche Abnahme schließt #498/#493 nicht automatisch.
