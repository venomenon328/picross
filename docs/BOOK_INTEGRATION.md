# Reguläre Buchdarstellung · B-B / #498

**AR-A / #486:** Die stabile Abschlussansicht bietet **Bild | Raster** zum
Vergleich mit den bestätigten Spielerfüllungen in Originalpalette und statischer
Stift-/Rasteroptik. Die Auswahl bleibt innerhalb des Besuchs erhalten und wird
nicht gespeichert. Jeder neue Eintritt beginnt bei Bild; Enthüllung, Spoiler-,
Save- und Resetgrenzen bleiben. Kein interaktives Arbeitsboard oder neue Galerie.
[Verhalten](PROTOTYPE_P1.md#54-abschluss-und-detaillierteres-ergebnisbild),
[Paket und getrennte Gates](https://github.com/venomenon328/picross/issues/486).


## K-B: direkte Fortsetzung

[Paketentscheidung #485](https://github.com/venomenon328/picross/issues/485#issuecomment-6705799391).
Das reduzierte rechte Katalogkopfpanel ruft dieselbe kanonische ID-Route wie eine Karte
auf. Erneute Auflösung unmittelbar beim Klick, vorheriger fallibler Slotflush,
PREPARING-/Capture-/Releasebarriere und Generationen bleiben verbindlich. Filter,
Kategorie, Seite und beide Scrollstände bleiben im Rückkehrkontext; kein Scrollen zur
gegebenenfalls ausgefilterten Karte. Recovered/backup_invalid darf bei gültigem
rekonstruiertem begonnenem Stand angeboten werden, behält aber seine Reparaturgrenzen.
K-B-T02 prüft diesen Weg einmalig im echten Windows-Buch; keine neue Dauer-HIL-Suite.

**RF-A / #541:** Schon die Katalogpräsentation während der gesperrten
Buchaufnahme bindet die eigene Fortschrittsminiatur synchron; die normale
Aktualisierung beobachtet zusätzlich Zelländerungen im offenen Katalog.
Der Kasten bleibt links an der rechten Kopfzone ausgerichtet und verwendet
ausschließlich deren halbe oder volle sichere Breite. Gemessener Textumbruch,
aktuelle UI-Skala, vollständige Miniatur und Innenränder bestimmen den Fit;
bei 2560×1440/UI100 passt Halbbreite. Die feste Kopfhöhe, Fehlerclip,
Sortier-/Filterabstand, Karten und Fußnavigation bleiben geometrisch unabhängig.
Die kleine Regression bleibt im vorhandenen `catalog/pages`-Prozess;
[RF-A-T02/R01/M01](https://github.com/venomenon328/picross/issues/541) sind
einmalige Windows-/Sichtgates am Lieferhead.

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

P2-A / #502 entfernt die historische Hülle `game/study/book/` mit ihren
27 Instanzen und Vollprüfern. Die Quellen bleiben über [BOOK_STUDY](BOOK_STUDY.md)
commitgebunden erreichbar. `tools/book_lifecycle.py` prüft auf ausdrücklichen
Diagnoseauftrag den aktuellen Produktroot und HIL mit synthetischem Testkatalog.
P2-F-C/D03 entfernt diesen eigenen Prozess aus `native.export` und normalen Vollläufen.
Der externe Windows-Beobachter liegt unter `game/tests/`; technische Inputs,
Prüfprogramme und Berichte bleiben aus regulären Paketen ausgeschlossen.
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

**K-A / #485:** Der gemeinsame Filterzustand umfasst Kategorie, Status, Modus,
Schwierigkeitsspanne sowie unabhängige maximale Breite und Höhe gemäß
[K-A-Katalogvertrag](CATALOG_PRESENTATION.md#k-a--kombinierbare-sitzungsfilter-485).
Neben Sortierauswahl und Richtungspfeil in der rechten Kopfzeile öffnet **Filter**
ein kompaktes Papierpanel; sein Entwurf
verändert die Treffer erst nach gültigem Übernehmen. Die Schwierigkeitsdropdowns
verhindern widersprüchliche Spannen durch gegenseitige Optionsgrenzen und
Anpassung der Gegengrenze. Die beiden Maßfelder stehen nebeneinander.
Ungültige Maßgrenzen bleiben sichtbar; Schließen
verwirft den Entwurf. Das Panel begrenzt sich auf das Fenster und
scrollt bei knapper Höhe, ohne Karten-/Bildbudgets zu reduzieren. Seine Höhe folgt
dem Inhalt; Übernehmen / Zurücksetzen / Schließen stehen gleich groß in einer
Zeile. Schmale Breite-/Höhe-Felder stehen rechtsbündig unter Von/Bis. Seiten-/UI-/
Ansichtswechsel schließen es. Filterreset erhält die Sortierung. Beide unabhängigen
Scrollstände, Seite und passende Auswahl bleiben bei Rückkehr erhalten;
Abschluss/Reset aktualisieren und begrenzen die Trefferposition. Kein zusätzliches
Speicherformat oder K-B-Button. Die kleine Filterprobe läuft im vorhandenen
catalog/pages-Prozess; die einmalige Windows-Buchsicht liefert der K-A-PR.

**KL-A / #523 · responsives Katalograster (Implementierung, Abnahmen im Issue/PR):**
Innerhalb jeder Hälfte bestimmt die tatsächliche nutzbare
Papier-/Scrollbreite bei gemessenen Kartenmindestmaßen eine gemeinsame
Kapazität von maximal drei Spalten. Bei 2560×1440/UI100 sind drei
Spalten × vier Zeilen für zwölf Karten je Hälfte nachzuweisen; bei knapper
Breite sicher zwei bzw. eine Spalte. Auch unvollständige letzte Zeilen werden
je Hälfte für sich horizontal zentriert. Die bisherige 12/12-Zuordnung,
unabhängige Scrollpositionen, Projektion, sichere Falzabstände und
Animationsbudgets bleiben erhalten; [KL-D01](CATALOG_PRESENTATION.md#kl-d01--responsives-katalograster-523)
regelt vollständige Karteninhalte und Fallbacks.
Die gemeinsame Kapazität verwendet die schmalere der beiden sicheren
Scrollbreiten einschließlich Balkenreserve. Der flache Zeilencontainer zentriert
vollständige und angebrochene Reihen ohne zusätzliche Controls oder Reparenting
beim Umbruch. Rechte Scrolländerungen lösen dieselbe Neuberechnung wie linke aus.

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

## Bildhaupttitel · BTI-C / #533 (Arbeitsbranch, noch nicht integriert)

[BTI](VIEW_TITLE_ART.md) führt auf dem Arbeitsbranch drei
reine, unveränderte freigegebene V2-rev1-Schriftzugbilder ein: `Rätselkatalog` im linken Katalogkopf,
`Hilfe` im rechten Infokopf und `Einstellungen` im linken Infokopf, jeweils
innerhalb der sicheren projizierten Papierhälfte zentriert. Haupttitel der
Informationsseiten liegen außerhalb ihrer Scrollflächen. Die zuvor
oben angeordneten Buttons `Zurück` und Hilfe-/Einstellungswechsel liegen jetzt
als feste untere Navigation außerhalb der Scrollflächen; der Kapitelzugang,
Gruppenrahmen, Besuchskontext und alle Daten-/Save-/Recoverywege bleiben.
**Implementierung ist keine unabhängige oder persönliche Abnahme; R01/M01 offen.**
Aktuelle Kriterien und Abnahme in [#533](https://github.com/venomenon328/picross/issues/533).

## Spielerhilfe · HIL-1 / #500

Der gemeinsame `help_panel` enthält vier direkt anwählbare Kapitel, kurze
Absätze und passive Lehrdiagramme aus `ui/help_panel.gd`, `help_examples.gd`
und `help_example.gd`. Die rechte eigene Scroll-/Clipfläche, Papier-/Falzränder,
untere Rücknavigation und der Meldungsraum aus `information.gd` bleiben Grundlage.
Ein neuer Informationsbesuch setzt Hilfe auf Spielprinzip zurück. Die Kapitelwahl
zeigt dessen Anfang; ein Pan zu Einstellungen und zurück erhält Kapitel und
Scrollstand. Das ist transienter Besuchskontext, kein Saveformat oder neue Option.

**HIL-REG-A / #548:** Die vier Kapitelzugänge stehen außerhalb des Artikelclips
in einem festen, linksbündigen Register. Bei ausreichend gemessener Papierbreite
liegt es links vom Artikel; andernfalls bilden dieselben Controls eine kompakte,
bei Bedarf mehrzeilige Leiste darüber. Schriftmetrik, UI-Skala, vollständige
44/55-px-Trefferflächen, Diagramme und Scrollbarreserve bestimmen den Wechsel.
Der aktive Eintrag erhält eine stabile leicht unregelmäßige Unterstreichung;
Hover und Fokus bleiben eigenständig sichtbar. Nur der Artikel scrollt.
Die erste vorhandene Abschnittsüberschrift beginnt den Artikel. Pangolin-Absätze
verwenden 20/25 px bei UI100/125 und sind bei hinreichender Breite auf 75
mittlere Zeichenbreiten begrenzt (mit Wortumbruch Richtwert 60–75 Zeichen); Lehrbilder dürfen den weiteren Artikelraum nutzen.
Kapitelwechsel beginnt oben, Einstellungenpan und Reflow erhalten die Lesestelle
innerhalb des Besuchs. Register, Text und Diagramme bleiben in derselben
Capturehierarchie. Bildhaupttitel, äußere untere Navigation, Papier/Falz und
Status-/Retryraum haben Vorrang. Inhalte, Regeln und Besuchsursprung bleiben.
Die kleine Layout-/Bedienregression läuft bei ausgewähltem `native.catalog` im
vorhandenen Informationsprozess; die einmaligen Buch-/Windowsbelege und
getrennten T01/R01/M01-Gates stehen in der
[Paketentscheidung](https://github.com/venomenon328/picross/issues/548#issuecomment-6724300292).

Alle verschachtelten Labels tragen `base_font` und werden rekursiv skaliert;
Überschriften erhalten ausdrücklich die Informationsrolle. Auch Kapitelbuttons
tragen transparente Papierdarstellung und skalierte HZ-Trefferflächen. Die
Diagramme besitzen keine Session, Eingabe- oder Effektsteuerung. Zellmasken
liegen auf einer eigenen Shader-Ebene, Zahlen und Raster außerhalb davon.
Die aktiven Zahlen-/X- und Rasterzeichenhelfer werden gemeinsam verwendet.
Captures nehmen die vollständige Controls-Hierarchie mit; kein eigenes Overlay
oder stehenbleibendes Lehrbild während eines Übergangs.

Die günstige Prüfung der tatsächlichen Beispielschlüsse bleibt im wählbaren Modul
`native.core`. Kapitelpointer, Scrollenden, Einstellungenpan, Katalog-/Rätselrückweg
und Hilfe ohne Session werden seit P2-F-C/D03 nur noch bei ausdrücklich angeforderter
Lifecycle-Diagnose geprüft. Der [Risiko-/Resttestvertrag](CI_C_NATIVE_GROUPS.md#p2-f-c-v01--502-buch-lifecycle-nur-auf-ausdrücklichen-anlass)
benennt die bewusst entfallende automatische Abdeckung. Spielstand, History,
Werkzeug/Farbe, Zoom, Hinweisanker und Pflicht-Flush echter Seitenwechsel bleiben
Produktanforderungen. Sieben HIL-Bilder sind schon seit P2-C keine aktuelle Pflicht;
die Diagnose liefert ausschließlich JSON und Logs. Die B-B-Lieferberichte und
historischen Abnahmen werden dadurch nicht nachträglich geändert.
Die getrennten HIL-T01/R01/M01-Gates stehen in
[Issue #500](https://github.com/venomenon328/picross/issues/500).

## Einstellungsseite · ANZ-A-N03 / #527

Zwei handgezeichnete Gruppen Anzeige/Rätselansicht stehen als begrenzter Block
mittig in der sicheren linken Scrollfläche. Label und Dropdown bleiben in einer
Zeile; nur Fenstergröße und Rätselansicht besitzen rechts eine fokussierbare
Fragezeichenhilfe. Die anderen beiden Dropdowns füllen den freien Raum samt
bisherigem Zwischenabstand. Bestehende Tooltipgestaltung trägt die Erklärungen.
UI100/125 ist eine sitzungsgebundene Auswahl. Der Seitentitel nutzt wie der
tatsächliche Katalogtitel Bakso Daging bei 28 × UI; beide Gruppentitel erhalten
nach N03-E01 ebenfalls Bakso bei kleineren 20 × UI. Die N02-Fraunces-Annahme für
den Katalogtitel ist damit korrigiert. Kein
Beenden-Widget und kein manueller Hinweisreset auf dieser Seite. Einstellungen
setzen keine Hinweisleseposition zurück; Katalog-Ausgang und OS-Schließen bleiben
samt Fehlerblockade/Retry erhalten. [Anzeigevertrag](DISPLAY_SETTINGS.md).
Beide Informationsseiten beschriften ihren oberen Rückbutton nur mit „Zurück“.
Tooltip und Accessibilityname nennen das tatsächliche Katalog-/Rätselziel;
Besuchsursprung, Übergang, Scroll-/Fokuskontext und Flush-/Recoveryguard bleiben.

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

Der Katalog-Beenden-Button und native Fensterschließung invalidieren zunächst ausstehende
Übergänge und nutzen anschließend den vorhandenen Flush. Fehler lassen die App
offen. Web wartet bei der eigenen Beendenaktion auf bestätigten Save- und
Präferenzsync; Fehler bleiben mit Retry erreichbar. Browsergesteuerter Tab- oder
Prozessabbruch behält die Grenzen aus [WEB-1](WEB_HOSTING.md).

## Prüfzuordnung

P2-A aus [#502](https://github.com/venomenon328/picross/issues/502) entfernt die
historischen manuellen Vollstudien-/Matrix-/Exportwege samt exklusiven Guards.
Der [aktuelle Belegvertrag](CI_C_NATIVE_GROUPS.md#buch-hilfeprüfung-und-studienrückbau)
bindet erhaltene Reader und kurze Produktprüfungen. P1 hat die Filmproduktion
bereits vollständig entfernt. Historische B-A-/B-B-Nachweise werden nicht
umgeschrieben oder durch diesen technischen Rückbau erneut abgenommen.

Die nativen Gruppen werden im aktuellen Paketplan nach dem vollständigen Diff begründet gewählt. Kleine
bisherige Komponentenfälle hängen über `tests/book_fixture.gd` am tatsächlichen
regulären Entrypoint und gemeinsamen Layout; sie stabilisieren Bewegungen
ausdrücklich synchron. Das ist kein Zeit-/Bewegungsnachweis. Der unveränderte
Produktroot in `tests/book_integration.gd` prüft nur auf ausdrücklichen Diagnoseauftrag
Hilfe und echte Kernübergänge. Keine automatische Mindestfallzahl daraus ableiten.
Die umfangreichen Original-/Handoffprüfungen sowie Windows-/Chromium-Eingaben
gehören zum historischen B-B-Liefernachweis; sie werden für HIL-1 nicht wiederholt.
`tests/book-save-v1.json` ist ein festes synthetisches Schema-1-Input mit History,
Redo, Werkzeug/Farbe, Zoom und Hinweisankern; kein echter Benutzerstand.

Die frühere automatische Hilfe-/Lifecyclepflicht vom 03.11.2026 wird durch
[D03](https://github.com/venomenon328/picross/issues/502#issuecomment-6665280802)
und P2-F-C ausdrücklich aufgehoben. Auch das gewählte Modul `native.export` führt
keinen eigenen Buch-Lifecycle mehr aus; alle zugehörigen Fälle/Unterphasen und
fünf Dateien entfallen aus seinem Pflichtinventar. Kein neuer Ersatz-Smoke.
Die manuelle CLI
`python tools/book_lifecycle.py --cache-dir <cache> --output-dir <leeres-ziel>`
bleibt als Diagnose bei konkreten Änderungen/Befunden erhalten, ohne automatische
Aufrufpflicht. Nur dann binden Producer, `tools/book_contract.py` und separater
Ergebnisreader echte Originalberichte, Assertions, Quellen, Phasen und Hashes.
Die historische 600-s-Ausnahme für `book-native` gehört zum damaligen
B-B-Vollnachweis. Diese Phase entfällt mit dem Vollstudienpfad; die drei manuell
angeforderten Lifecyclephasen behalten ihre 300-s-Grenzen.
Die kurze Historyroute im gewählten Modul `native.history` behält höchstens 20
Kommandos, sechs neue Transaktionen und genau zwei echte Prozesse.
Die bestehende Abhängigkeit der Exportgruppe von ebenfalls gewählten Katalog-/
Grafikgruppen bleibt in diesem Paket unverändert; sie startet keine
3D-Hilfeintegration mehr. Für ausdrücklich angeforderte Diagnosen gilt weiterhin
die bestehende Renderer-Vorgabe.

`tools/book_windows_probe.py --build-cache <cache> --source <ziel>` exportiert
headless den regulären Windowsroot mit synthetischen Daten. Zwei kleine
Ressourcenüberlagerungen müssen den tatsächlichen PCK-Guard am alten Einstieg
beziehungsweise einer Studienbeigabe scheitern lassen. Der getrennte Desktoplauf
`--source <ziel> --output <belege> --head <sha> --fold` verwendet bytegleiche
EXE/PCK, isolierte Profile und den rein lesenden externen Beobachter. OS-Eingaben
prüfen auch einen realen Dateisystemfehler, verweigertes Fensterschließen und Retry.
Dieser exklusive Desktoplauf ist nach Eigentümerentscheidung vom 02.11.2026
nur für die damalige B-B-Entwicklung beauftragt. Der Diagnoseweg bleibt für
die offenen B-B-M01/HIL-M01 und P1-R01-O01 am aktuellen Spieler erhalten. Er wird nicht automatisch in
Standardprüfungen aufgenommen. Spätere Läufe mit Fenstern/Maussteuerung benötigen
einen passenden ausdrücklichen Auftrag und vorherige Desktopfreigabe.

Für die historische B-B-Lieferung war Chromium ausdrücklich als
`browser_scope=short` beauftragt; daraus folgt kein neuer Browserauftrag. C01–C08 verwenden die neue Buchpräsentation mit echter Eingabe,
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

Technisches Review, persönliche B-B-/HIL-Abnahmen, Merge und Deployment bleiben
getrennt. Den aktuellen Status in #498/#493/#500 und ihren PRs prüfen; diese
Produktquelle erklärt keine historische Abnahme erneut für offen oder bestanden.
