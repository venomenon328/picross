# Native Prüfmodule und Originalnachweise

## HIL-REG-A / #548: festes Kapitelregister

Bei ausgewähltem `native.catalog` prüft der bestehende `catalog/information`-
Prozess die vier Kapitel per Pointer und Fokus-Accept, aktiven stabilen Unterstrich
mit getrenntem Fokus, gemessenen breiten/kompakten Umbruch und eine engere
Papierfläche mit mehrzeiliger Leiste. Registerrechtecke bleiben beim Scrollen
fest; Artikelende, vollständige passive Diagramme, begrenzte Absatzspalte,
Einstellungenrückkehr und UI100→125→100-Leseanker werden geprüft. Bestehende
BTI-/HIL-TYPO-Assertions bleiben; Titelzentrierung bezieht sich auf die ganze
Hilfepapierfläche, nicht auf die versetzte Artikelspalte. Keine neue Prozess-,
Ergebnis- oder Dauerbildfamilie. `help_native.gd` passt nur die Containment-
und untere Navigationsannahmen des ausdrücklich manuellen Lifecycle an.
Einmalige native Windows-/Buchoriginale und unabhängige/persönliche Gates bleiben
an die [Paketentscheidung #548](https://github.com/venomenon328/picross/issues/548#issuecomment-6724300292)
gebunden. Keine Wiederaufnahme des Lifecycle in Standard-CI.

## AR-A / #486: stabile Abschlussumschaltung

Im vorhandenen EA-native-Prozess prüfen fünf synthetische Kontexte den erst
stabil freigegebenen Bild-/Rasterwechsel mit genau einem rechteckigen
Schiebercontrol und nativer Handschraffur, Originalpalette und Atlasvarianten,
Kleindetailstufe, vollständige Linien, proportionale Bounds, reale Viewportklicks,
Refresh/Resize/UI/Fokus, Resetabbruch und Katalog-/Informationswiedereintritt.
Session/History/Ansicht und sämtliche isolierten Slotbytes bleiben unverändert.
Vorhandene EA-Zeit-/Alpha-/Resetfehler-/Neustartprüfungen bleiben erhalten.
`ar_measurements` bindet Matrix, bestätigte Zellen/Palette, native Farb-/Leerproben,
Geometrie und Zustandsbeobachtungen; `native_results.py` liest diese unabhängig.
Günstige Mutanten verwerfen verfrühte Freigabe, falsche Farbquelle und Saveänderung.
Keine neue Prozessfamilie oder dauerhafte Bilder. Die sechs einmaligen nativen
Revieworiginale entstehen nur bei ausdrücklich gesetztem `AR_REVIEW_DIR` und
werden gemäß [AR-A-Prüfplan](https://github.com/venomenon328/picross/issues/486)
auf einem separaten befristeten Reviewref zugestellt. R01/M01 bleiben getrennt.


## SBR-A / #539: gemeinsame native Scrollbarfamilie

Der bestehende `catalog/pages`-Prozess ergänzt den Checkpoint `sbr-scrollbars`:
geerbte und explizite Themes samt horizontalem Fallback, helle geschlossene
Dreiecke und Hover/Druck, begrenzte deterministische kurze/lange Schraffur,
tatsächlicher Kataloggutter bei UI100/125 und 16:10, symmetrische 12/12-Zuordnung,
native Range-/Pfeil-/Spur-/Thumb-/Radwege, Informations-/Katalogoffsets sowie
Popup-Escape ohne Auswahl oder Durchklick. Die übrigen ausgewählten Katalog-
und Informationsfälle laufen vollständig weiter. Vorhandener unabhängiger
Reader und Missing-/Duplicate-/Zero-Checkpoint-Gegenproben binden denselben
zusätzlichen Record. Keine neue Prozess- oder Dauerbildfamilie.
Die einmaligen nativen Originale für SBR-A-R01 und die persönliche Windows-
Bedien-/Stilabnahme SBR-A-M01 bleiben paketgebunden gemäß
[Prüfplan #539](https://github.com/venomenon328/picross/issues/539).

## RF-A / #541: unmittelbare Miniatur und binäre Panelbreite

Im vorhandenen `catalog/pages`-/`k-b-recent`-Checkpoint prüft die kleine
synthetische Regression die synchrone Zielbindung bei abgeschaltetem Prozess,
tatsächliche eigene Füll-/Neutralpixel ohne Hover, Undo/Redo bis zur leeren
Redo-Miniatur und den Zielwechsel. Reale Buchprojektion bei UI100/125 und
16:10 sowie ein aus Schriftmaßen hergeleitetes Fit-Grenzpaar sichern exakt
halbe/volle Breite, unveränderten linken Rand, Text-/Miniaturabstände und
den 8×UI-Sortierabstand. Die bestehenden ID-/Reset-/Retryfälle bleiben erhalten.
Kein neues Ergebnisformat, Prozess oder dauerhafte Bilder. Der unabhängige
Reader verlangt weiterhin denselben echten Checkpoint mit allen Assertions.
Einmalige Windows-Maus-/Originalnachweise bleiben am [RF-A-PR](https://github.com/venomenon328/picross/issues/541)
für das separate R01/M01 erreichbar, danach werden sie zurückgebaut.

## K-B / #485: begrenzte Merkerregression

[Paketentscheidung](https://github.com/venomenon328/picross/issues/485#issuecomment-6705799391):
`native.catalog`, `native.history`, `tools`. Im vorhandenen Pages-Prozess folgt auf
die K-A-Filterfälle `k-b-recent`: strikte Format-/Dateigrenzen, Unterbrechung vor
atomarem Austausch, eigene Wiederholung/Löschung, kanonische ID/Revision/Status,
wirksamer Bearbeitungsanlass samt Save-Retry sowie ausgefilterte Panelnavigation.
Producer, native_contract und unabhängiger Reader verlangen denselben Checkpoint.
Die Historyroute bleibt bei 17 semantischen Kommandos, vier neuen wirksamen
Transaktionen und genau zwei Prozessen; passive Diskmerker-/Auflösungsoracles prüfen
Aktion, Ansicht und echten Neustart. Günstige Reader-Gegenproben verwerfen manipulierte
Merker. Die tatsächliche JS-Bridge wird unter Node über einen tools-Unittest geprüft;
kein Browserstart und kein stilles Überspringen bei fehlendem Node.
K-B-T02 ist eine einmalige Windows-Buchprobe mit isolierten synthetischen Profilen.
K-B-W01, unabhängiges R01 und persönliches M01 bleiben separate Gates. Keine neue
Bild-/HIL-Familie, kein echter Produktionskatalog als automatisierter Testbestand.
Die kleine B-01-Dauerregression bleibt im selben `k-b-recent`-Checkpoint:
1280×720 und 1920×1080 jeweils UI100/125, Merker-/Savefehler, vollständig
sichtbare 44/55-px-Trefferrechtecke nach Scrollen sowie echte Pointerklicks an
allen vier Ecken und in der Mitte beider Retrybuttons. Überlange Meldungen
dürfen Sortierung, Filter, Kartenflächen und Fortsetzen-Panel nicht verschieben.
Aktuelle echte Windows-Originale bleiben ein einmaliger befristeter Reviewbeleg.

## Geltung und Auswahl

Die sieben Module `native.core/history/catalog/completion/adapters/graphics/export`
werden in [Package CI](CI_WORKFLOW_V2.md) ausdrücklich im aktuellen Paketplan
gewählt. Keine automatische Vollauswahl gemeinsamer Pfade. Die alten `PATHS`-/
`select_groups`-Regeln in [native_contract.py](../tools/native_contract.py) gehören
zum manuellen Diagnoseweg und zur Abhängigkeitsanalyse; `checks`, `coverage` und
[native_artifacts.json](../tools/native_artifacts.json) binden den tatsächlichen
Umfang einer ausgewählten Gruppe.

Dieser Vertrag beschreibt die derzeitigen Module und bewusst akzeptierte Lücken.
Er schützt keine Testfamilie vor begründeter Änderung nach
[CI_CONTRACT](dev-rules/CI_CONTRACT.md). Eine Änderung von Auswahl oder Testinventar
muss mit Producer, unabhängigem Reader und fachlicher Risikobewertung zusammenpassen.
Produktgarantien und paketbezogene Abnahmen bestehen unabhängig vom CI-Ausführungsort.

| Modul | Aktueller Umfang bei Auswahl |
| --- | --- |
| `native.core` | Logik-/Save-/Recoverytests, aktuelle ZS2-Stichprobe, echter Exit-23-Negativpfad, P1.3 write/read und kontrollierter Start |
| `native.history` | Kurze echte Schreib-/Neustartfolge mit unabhängigem Zell-/History-/Redo-Orakel |
| `native.catalog` | Elf KAT-2-Modi regular/restart/pages/empty/invalid/adapter/information/kb/kk/ke/at, repräsentative KE-/KK-Stichprobe und synthetische Registrierung |
| `native.completion` | EA-Import, native/restart mit eigenem Profil, sofortiger Commit/Save, Übergang/Abbruch, Geometrie, Reset und AT-Pixelprüfung |
| `native.adapters` | Vier RP6-Spiel-/Save-/Readketten, Fremdslots, zwei RP6-Darstellungscaptures, synthetische ZA-1-Registrierung/Recovery und Windows-/PCK-Prüfung |
| `native.graphics` | VS2/HF/HN/HS, 18er-Geometriestichprobe, fünf kompakte Renderstufen mit 66 Frames, aktuelle ZS2-Bewegungsorakel und PERF-B |
| `native.export` | Regulärer Inhaltsimport, Windows-Debugexport, externe PCK-Prüfung; auf Windows zusätzlich tatsächliche EXE-Starts |

KL-A / #523 ergänzt im vorhandenen `catalog/pages`-Prozess eine kleine
synthetische Zeilen-/Geometrieprobe: drei bzw. zwei Referenzspalten, selbständig
zentrierte volle/angebrochene Zeilen für 1/2/5/11/12/13/23/24 Karten, gezielte
UI-/Seitenverhältnis-Fallbacks, gleiche Karten-/Hitboxbudgets und erhaltene
IDs/Scrollstände beim Umbruch sowie rechte Öffnung/Reset. Keine neue Prozess- oder
Bildfamilie. Die KE-Kapazitätsprüfung im unabhängigen Reader berücksichtigt
dieselbe Obergrenze drei. Einmalige gerenderte KL-Einführungsbelege stehen am
gebundenen PR, nicht als neue dauerhafte Galerie im Modul.

K-A / #485 ergänzt im selben `catalog/pages`-Prozess eine kleine synthetische
Filterregression: Status inklusive leerem Save, Redo, Fehler und Recovery,
Modus, vorhandene L1–L5/fehlende Stufe, inklusive Spannen und unabhängige Breiten-/Höhengrenzen,
Rechteckorientierung, gegenseitig begrenzte Schwierigkeitsoptionen und Anpassung der
Gegengrenze, UND-Kombination, mehrseitige Sortier-/ID-Zuordnung, No-op/Reset,
beide Scrollstände, Return und Clamping nach Abschluss/Reset sowie sichtbare
Fehler außerhalb der Treffer und unveränderte Save-/Präferenzbytes beim Filtern.
Die fünf Checkpoints layout/pages/sorting/filter-rules/filter-navigation werden
vom bestehenden unabhängigen Reader in exakter Reihenfolge und mit tatsächlichen
positiven Assertions geprüft; kleine Gegenproben sichern das geschlossene Protokoll.
Keine neue Prozess-/Bildfamilie, kein Browser-/Buch-Lifecycle. Die einmalige echte
Windows-Sicht K-A-T02 bleibt ein paketgebundener Reviewbeleg.

ANZ-A / #527 ergänzt im vorhandenen `catalog/information`-Prozess günstige
synthetische Displayfälle: dekorierte Presetgrenzen einschließlich 720p/4K/16:10,
negative Monitorpositionen/DPI-Rahmen, strikte Präferenz-/Ersetzungsfehler,
Vorschau/Annahme/Timeout/Rücknahme und sichere Bestätigung bei UI100/125.
Der injizierte Fensterserver erzwingt keinen physischen Modus. Echte Windowsmodi
und kurze UI-Originale bleiben einmalige paketgebundene W01-/R01-Nachweise.
N01 ergänzt in derselben Informationsprobe Gruppenfolge, kompakte linksbündige
Breiten und 44/55-px-Trefferflächen bei 1080p/720p × UI100/125, Scroll-Erreichbarkeit,
Popupgrenzen/-Abbau sowie Desktopwert und sichtbare Fehler-/Fallbackzustände ohne
positive Dauerzeile. Keine neue Prozess-/Bildfamilie; die gezielte echte Windows-
Sichtprobe bleibt historisch an N01-R02 gebunden. N02 ersetzt die günstigen
Gruppen-/Reset-/Beendenassertions durch zwei zentrierte HZ-Rahmen, Titelrolle,
horizontale Felder, Skalauswahl und separate Hover-/Fokushilfen. Kein manueller
Rücksetzbefehl; Testinputs setzen ihre Leseanker ausschließlich im Testaufbau.
Saveblockade/Retry prüft den vorhandenen Katalog-Ausgang und WM-close am echten
Buchroot; reguläres Beenden beendet weiterhin tatsächlich den Informationsprozess.
N03 korrigiert in derselben Probe den Vergleich mit der tatsächlichen Bakso-
Katalogtitelressource bei UI100/125, nach N03-E01 auch die kleinere Bakso-Gruppenrolle
und prüft nur zwei Hilfen, volle Dropdownbreite ohne Fokus-/Hitboxplatzhalter
sowie den sichtbaren Rücktext „Zurück“ bei unverändertem kontextabhängigem
Rückziel, Saveblockade und Retry auf beiden Informationsseiten.
Die einmalige Windows-Originalsicht für N03-R04 erzeugt keine neue Dauerfamilie.

BTI-C / #533 ersetzt die abgelösten sichtbaren Bakso-Seitentitelannahmen
durch Bildtitel-/Fallbackrollen. Eine kleine Probe im bestehenden
`catalog/information`-Prozess prüft die drei lokalen Ressourcen, semantischen
Titel, unveränderte V2-rev1-Ressourcen, optisch zentrierte proportionale Titelbereiche, getrennte untere Navigation und
erreichbare Scrollenden bei UI100/125 sowie 16:10. Keine neue Prozess- oder
Screenshotfamilie; echte Windowsdarstellungen und Bewegungs-/PCK-Nachweise
bleiben einmalige paketgebundene Belege.

Der Windowsbau des **CI-Kerns** außerhalb reiner Dokument-/Rätselinhaltsänderungen
ist kein automatisch ausgewähltes
`native.export` und behauptet dessen zusätzlichen Funktionsnachweis nicht. Bei
gewähltem Modul wird sein geprüftes Spielerpaket ohne technische Berichte als
Kerndownload wiederverwendet. Der eigene Buch-/Hilfe-Lifecycle gehört seit
P2-F-C/D03 auch bei Auswahl von `native.export` nicht mehr dazu.

## Originale und Aufbewahrung

Erfolgreiche native Prüfungen liefern keine Sichtgalerien. Das aktuelle
Originalinventar enthält fünf AT-Kompositionssamples (je 5×2 RGB8) und fünf
HN-Bandsamples (je 50×100 RGBA8) für unabhängige Pixelreader. HS/ZS prüfen eigene
temporäre Layer-/Bewegungsoriginale samt Mutanten und löschen sie danach.
Kein EA-Film, keine HZ-/HC-Einführungsgalerie, keine HIL-Sichtdateien.
Die [P2-C-V03-Entscheidung](P2_C_V03_AUDIT.md) bindet den damaligen Rückbau.

„Benötigtes Original“ bezeichnet einen Prüfeingang im Lauf, keinen Dauerupload.
[native_results.py](../tools/native_results.py) prüft die Originalberichte,
Teilprüfungen, Phasen-/Fehlerfelder, Datei-/Bytehashes, Quell-/Head-/Basis-/Checkout-
und Run-/Versuchsbindung unabhängig von der Producerzusammenfassung. Package CI
führt diese Prüfung im erzeugenden Job aus und entfernt den temporären Technikbaum.
Ein positives Joblabel, ein leeres Modul oder ein ausgelassener Pflichtinput reicht nicht.

Aufbewahrung und technische Uploadanforderung stehen ausschließlich in
[CI_WORKFLOW_V2](CI_WORKFLOW_V2.md). Der ausdrücklich manuelle Diagnoseweg nutzt
weiterhin gebundene Producer-/Gate-Transporte; `native_delivery.py` begrenzt dort
Fehlerdiagnosen auf betroffene Berichte/Logs/Originale. Fehler bleiben Fehler,
auch bei geliefertem `diagnostics.json`; keine fremden Runs oder Gesamtbaumdumps.
Byteidentische Bildaliase dürfen nur tatsächliche Originalbytes repräsentieren;
keine Rekodierung/Skalierung zur Umgehung der Reader. Erzeugte, geprüfte und
hochgeladene Dateien/Bytes werden getrennt gemessen.

## Kurze Historyroute

In `native.history` und der entsprechenden lokalen Auswahl gelten höchstens
20 semantische Benutzerkommandos, sechs neue wirksame Transaktionen und genau
zwei echte Spielprozesse (Schreiben, frisches Laden/Redo). Der aktuelle feste Plan
enthält 17 Kommandos und vier neue Transaktionen. Blatt-/Werkzeug-/Farbwahl,
Navigation, Undo/Redo und reguläres Beenden zählen mit; eine Down/Move/Up-Geste
zählt einmal, passive Assertions und Prozessstarts nicht.

Geprüft werden atomarer Strich, exakte Vor-/Nachwerte, Undo/Redo und Verzweigung,
Navigation ohne Historymutation, Zustand/Ansicht/Undo-Merkmal nach Save/Neustart,
echter Redo und fremde Slotbytes. Das unabhängige Python-Orakel importiert keine
produktive Historylogik und liest Plan, Trace, beide Saves, Fremdslot-Hashes und
Summary. Zwei günstige Gegenproben verwerfen manipulierte Zellen und unvollständige
Spuren. Keine versteckten Setupaktionen, 500er-Route oder automatische Stressmatrix.
[CI2-D-T01](CI2_D_VERIFICATION.md) bleibt der historische Einführungsnachweis.

## P2-F-C-V01 / #502: Buch-Lifecycle nur auf ausdrücklichen Anlass

[D03](https://github.com/venomenon328/picross/issues/502#issuecomment-6665280802)
und die [aktualisierte Vorbereitung](https://github.com/venomenon328/picross/issues/502#issuecomment-6664748225)
heben im P2-F-C-Scope den pauschalen Schutz von Testfamilien und Mindestfallzahlen
auf. Produktfunktionen und Datenintegrität bleiben verbindlich. Der frühere
U01-Abschluss betrachtete nur die kleine HIL-Matrix unter dem inzwischen
abgelösten Schutzrahmen; er begrenzt diese neue Entscheidung nicht.

Die gesamte Phase `regular-book-integration` entfällt aus `export`, Standard-CI,
`all` und gewöhnlichen manuellen Vollläufen. Kein Ersatz-Smoke, keine automatische
Änderungs-/Zeitplanroute und keine Pflicht, alle Kapitel oder Viewports anzuklicken.
Damit entfallen drei Unterprozesse (Version, Import, gerenderte Integration),
die aggregierte `book_lifecycle`-Pflicht und fünf Dateien unter `book-lifecycle/`
(report.json, integration/integration.json und drei Logs). Der unabhängige
Standardreader verlangt die verbleibenden Exportphasen exakt und weist
mitgelieferte alte Lifecyclephasen, -Aggregate und -Verzeichnisse zurück.
Die Sparse-Quellenbindung dieses Diagnosepfads entfällt im CI-Gate.

`tools/book_lifecycle.py` bleibt ausschließlich als ausdrücklich aufrufbare
Diagnose bei konkreten Buch-/Help-/Save-Navigationsänderungen oder Fehlerbefunden:
`python tools/book_lifecycle.py --cache-dir <cache> --output-dir <leeres-ziel>`.
Es gibt keinen obligatorischen Aufruf bei solchen Änderungen; der Auftrag entscheidet.
Dann laufen die bisherigen Fälle vollständig mit isolierten synthetischen Daten,
300-s-Phasengrenzen und ohne Bilder/Film. Die CLI liest das Ergebnis anschließend
mit dem separaten `validate_book_lifecycle`: Originale, Assertions, Quellen,
Hashes und Identität müssen stimmen. Diese Integritätsregeln sind keine
Mindestabdeckung der Standard-CI. Der kleine Python-Test dieses weiterhin
aufrufbaren Diagnosevertrags bleibt im bestehenden Toolpfad.

Die historische Kostenbasis vor Workflow v2 ist PR-Run `42058446334/2`, Technikoriginal `13434724730`:
79,167 s für den gesamten Lifecycle, darin 9,241 s Import und 68,768 s Integration
mit 201,050 s Kindprozess-CPU; fünf Dateien/110.787 Rohbytes, null PNGs.
Lokale instrumentierte Kopien auf derselben Basis bestätigen die Größenordnung
und trennen die Familien; keine der lokalen Zeiten ist eine CI-Prognose.
Die kleine Matrixreduktion des U01 sparte nur 1,29–1,43 s. Der eigene Prozess
ist deshalb die sinnvolle Kürzungseinheit, einschließlich seiner Start-/Importkosten.

| Bisherige Familie / lokale Diagnosezeit | Verbleibende Stufe, konkrete Lücke und Risikobewertung |
| --- | --- |
| HIL-Lehrbeispiele `help_cases.gd`, 0,0053 s | Bleiben bei Auswahl von `native.core` in dessen vorhandenem Prozess: unabhängige kleine Enumeration der tatsächlich dargestellten Daten. Falsche Lehrschlüsse können neue Spieler fehlleiten; sehr geringe Mehrkosten, kein eigener Prozess/Renderer. Keine pauschale Schutzpflicht, sondern positive Nutzenabwägung. |
| Kapitel/Font/Diagramm/Clip/Wheel-Matrix, 3,705 s innerhalb HIL | Alle zwölf Varianten und 960 Wheel-Aktionen entfallen aus Standard-CI, auch die sieben U01-Kandidaten. Abgeschnittene Hilfe, falsche HZ-Trefferflächen, unerreichbares Ende oder Eingaben auf dem verdeckten Brett können unerkannt bleiben. Mittlere UX-Schwere, konkrete Auslöser sind Helptext-, Layout-, Font- oder GUI-Änderungen; keine gemessene Fehlerhäufigkeit. Nur ausdrückliche Diagnose, kein gleichwertiger Ersatz. |
| HIL insgesamt, 17,215 s | Settings-Pan, Kapitel-/Scrollgedächtnis, Captureteilnahme, Work-/Catalog-Rückweg und passive Eingaben nicht mehr in dieser realzeitlichen Kette geprüft. Verlorene Position, falscher Rückweg oder unerwartete Zustandsmutation sind akzeptierte Testlücken; das Produkt darf sie weiterhin nicht haben. Semantikprüfung der Beispiele ersetzt diese Kette nicht. |
| Start, Frozen-Schema-1 und erstes Öffnen, 6,710 s | Bestehende Core-/History-/PCK-Proben prüfen andere Start-/Persistenzaspekte. Spezifische Wiederherstellung von Redo, Werkzeug/Farbe, Zoom und Hinweisankern beim echten Buchöffnen bleibt als Lücke. Hoher Schaden bei Zustandsverlust, plausibler Auslöser ist Änderung der Aktivierungs-/Viewbindung; nur ausdrückliche Lifecycle-Diagnose deckt genau diese Kopplung ab. |
| Work-Schreibfehler/Retry/Rückkehr, 2,526 s; Catalog-Fehler/Retry/Information, 2,356 s | Core/P13, ZA-1-Save-Recovery und KAT-2-Pages behalten tatsächliche Fehler-/Slot-/Retryproben. Sie sind kein Ersatz für den unbeschleunigten Buch-Flush, blockiertes Beenden oder sichtbares Retry während dieser Folge. Ungesicherter Fortschritt oder ein unbedienbarer Fehlerweg wären schwerwiegend. Teilweise gemeinsame SaveStorelogik rechtfertigt geringere Frequenz, nicht behauptete Abdeckungsneutralität. |
| Frozen-View, Abbruch, stale callback, falsche ID, Slotwechsel, 4,776 s | Book-Generation-/Capture-Rennen werden nicht mehr realzeitlich durch diese Folge geprüft. Falsches Blatt oder falsche Slotbindung kann bis zu Datenverlust reichen. Hohe Schwere; Änderungen an asynchroner Navigation sind der konkrete Diagnoseanlass. Verbleibende Fremdslotproben prüfen andere Wege. |
| Work→Settings→Help→Return, 3,878 s; letzte Rückkehr/Freigabe, 2,263 s | Verlust von Optionen/Besuchsursprung oder Ressourcenleck kann unbemerkt bleiben. Komponentenprüfungen mit `book_fixture.gd` stabilisieren synchron und belegen keine echte Bewegungs-/Freigabereihenfolge. Kein zusätzlicher Dauer-Smoke; explizite Diagnose bei betreffenden Änderungen/Befunden. |
| Backup-only-Recovery, 6,888 s | ZA-1/P13 und KAT-2-KK behalten Recovery-/Fremdslotfälle. Die besondere Kopplung aus read-only Backup, Buch-Informationsseite, sichtbarer Reparatur und geänderter Katalogauswahl wird nur noch anlassbezogen geprüft. Überschriebenes Backup/falscher Slot wäre schwerer Datenverlust; die Produktgarantie bleibt, die reale Kopplungsprobe wird bewusst nicht dauerhaft verlangt. |
| Leerer/ungültiger Katalog ohne Session, 9,210 s; realer Close, 1,264 s | KAT-2 prüft leere/ungültige Daten, aber nicht diese vollständigen Buchrouten und den tatsächlichen Close. Nicht erreichbare Hilfe/Einstellungen, Absturz oder hängenbleibender Prozess sind akzeptierte Prüflücken. Bei Registry-/Nullsession-/Closeänderungen ist die Diagnose sinnvoll, kein automatisches Pflichtprogramm. |
| Version/Import und Diagnose-Reader | Kein eigener Standardprozess und keine Standardquell-/Dateipflicht mehr. Regulärer Import, echter Windows-Export, Entrypoint-/Ressourcen-/Player-PCK-Prüfung bleiben in Export; die zusätzliche Diagnosekopie liefert dafür keinen proportionalen Dauernutzen. Der erhaltene manuelle Reader bleibt fail-closed. |

Die Zeiten der Matrix sind in HIL enthalten; CPU wird nicht zur Wandzeit addiert.
Für seltene Fehler gibt es keine belastbare Frequenzstatistik. Die Entscheidung
stützt sich auf konkrete Änderungsanlässe, teilweise vorhandene günstigere
Prüfungen und den hohen wiederkehrenden eigenen Prozessaufwand. Insbesondere
Save-/Recoverylücken sind ausdrücklich akzeptierte Risiken der Prüfstrategie,
keine Aufhebung eines Datenversprechens. Kein Produktcode wird geändert.

Die genannten verbleibenden Prüfungen laufen nur bei Auswahl ihrer jeweiligen
Module im aktuellen Paketplan. `native.core` ist kein Bestandteil des obligatorischen
kleinen CI-Kerns. Andere Core-/History-/Catalog-/Completion-/Adapters-/Graphics-/
Exportprüfungen bleiben in diesem Paket inhaltlich unverändert; ihre Namen schützen
sie nicht vor einer späteren Neubewertung. Die alten manuellen Auswahlregeln starten
den Lifecycle ebenfalls nicht bei Diagnosequelländerungen.

Der Integrationsplan von PR #516 wählt `tools` für bestehende kleine Producer-/Reader-
und Negativfälle sowie `native.export` für den tatsächlich geänderten Exportweg samt
wiederverwendetem Windows-Kerndownload. Spielcode, Ressourcen und Produktionslogik
ändern sich nicht; weitere Module werden nicht angefordert. Technische Originale
werden im erzeugenden Job unabhängig gelesen und danach entfernt (`evidence.mode=none`).
Alte T01-Vollmatrixmessungen bleiben an ihren damaligen Head/Base/Run/Attempt gebunden;
sie belegen keinen neuen Workflow-v2-Lauf. Neue Ergebnisse stehen im Paket-PR.
600 s sind ein weiches Ziel. Tests, Selbstreview, technisches Review und Mergefreigabe
bleiben gemäß aktuellem Workflow getrennt. Kein Chromium oder automatischer Retry.

## P2-F-B-V01 / #502: risikobasierte ZS2-Core-Stichprobe

Die [beauftragte Vorbereitung](https://github.com/venomenon328/picross/issues/502#issuecomment-6661639913)
ersetzt ausschließlich Wiederholungsmatrizen in `core/current-drawing-tests`.
D02 erlaubt bewusst geringere Abdeckung. Die separate Graphics-Phase
`current-drawing-pixel-oracles`, ihre Echtzeitframes und Fehlerwege bleiben
unverändert; daraus folgt keine neue Ausnahme oder Retry-Erlaubnis.

| Länge | Tatsächlich ausgeführte Richtung / Maustaste |
| --- | --- |
| 1 | rechts / links; links / rechts |
| 4 | unten / links; oben / rechts |
| 16 | rechts / links; unten / rechts |
| 17 | links / links; oben / rechts |
| 50 | unten / links; rechts / rechts |

Dies sind zehn statt 40 reale Striche auf T-06 (50×50 Farbe). Jede Längenklasse
und beide Buttonbedeutungen bleiben erhalten; beide Achsen und Vorzeichen sind
repräsentiert. Bei Länge eins ist die Richtung geometrisch wirkungslos. Die
16/17-Grenze prüft reale Starts bei 12-ms-Schritten beziehungsweise
180-ms-Verteilung, der Maximalstrich beide Ziele. Jede Probe prüft alle wirksamen
Zellen, sofortige Miniatur/Modell/History und echte Savebytes sowie das Ende des
letzten Effekts bei 209/210 ms ohne verzögerte Zustandsmutation.

| Bewusst entfallene Variante | Möglicher unentdeckter Defekt / Spielerwirkung / Risikodisposition |
| --- | --- |
| Die übrigen sechs Richtungs-/Tastenkombinationen je Länge (30 gesamt) | Fehler nur bei einer bestimmten Länge plus Achse/Vorzeichen/Button können die gerichtete Zeichnung falsch ordnen oder betroffene Eingaben falsch zuordnen. Länge eins hat keine echte Richtung; bei längeren Strichen ist das Restrisiko real. Gemeinsamer Gesten-/Staffelcode und unveränderte G1-/Chord-/Saveproben begründen die Stichprobe, nicht behauptete Gleichwertigkeit. Keine 1:1-Ersatzprüfung und keine manuelle Vollmatrix als neue Pflicht. Die Datenintegritätsanforderung selbst gilt weiter. |
| T-02/T-04/T-08/T-09 jeweils UI100/125 bei Schrift/Slots (acht von zwölf) | Nur auf einem mittleren Raster, einer konkreten Hinweislänge oder Palette auftretende Slot-/Fallbackabweichungen können übersehen werden; schlechter lesbare Hinweise sind die mögliche UX-Folge. T-01 Mono und T-06 maximale Farbe/Hinweise jeweils UI100/125 bleiben als vier Referenzen. Keine Behauptung vollständiger Blattabdeckung. |
| Animation-aus-Seite/Reset auf T-02/T-04/T-08/T-09 (vier von sechs) | Ein blattspezifischer Verlust der Sitzungsoption könnte Effekte wieder einschalten. T-01/T-06 behalten dieselbe vollständige Wechsel-/Info-/Rückkehr-/Resetfolge. Echter Checkboxweg, Savebytes/View/History, erneutes An ohne Replay und frische App mit Default An bleiben. |

`protection_and_g1`, `lifecycle`, `chords` und die geerbte `gesture_probe`
bleiben inhaltlich unverändert, ebenso die abschließende G1-/Abbruch- und
119/120/209/210-ms-Probe. Kein Eingriff in Produkt-/Rendererquellen, allgemeine
Core-Tests, P13-Zweiprozessprüfung, Exit 23, Start oder andere native Gruppen.
Die kleineren Schrift-/Schalterfolgen verlassen weniger geänderte synthetische
Slots vor der weiterhin echten neuen App; deren Initialisierung wird mitgemessen.

Quellabgleich: `run_tests.gd` schützt unter anderem echte Fokusabbruch-/Spoiler-
und Abschlusswege, nicht die entfallene Fontkreuzmatrix. `hf149_probe.gd` prüft
unabhängige Slotkapazität, semantische Leseanker samt Neustart und Overlaytext/
Geometrie; `hn192_probe.gd` echte Hinweispointer-/Abbruch-/Fokuswege;
`vs2_tests.gd` Ansichtsoption, Layout und Navigation. Diese bleiben ausgewählt,
sind aber kein gleichwertiger Ersatz für jede entfernte ZS2-Kombination.
Originalfont-/Lizenzprüfung über `z2_resources.py`, HC-/HF-/HN-Lesbarkeitsverträge,
Offline-Fallback, Checkbox-/Spoiler- und Saveanforderungen bleiben verbindlich.

Der reale Godot-Prozess schreibt 24 geordnete `ZS2_CASE`-Records in sein ohnehin
gebundenes vollständiges Log: Setup, vier Fontfälle, Gestenprobe, zehn Striche,
G1-Schutz, Lifecycle, Chords, Checkbox, zwei Blattfolgen, Neustart und Zeitgrenzen.
Jeder enthält tatsächliche positive/negative Assertions und Zeit, die Striche
zusätzlich beobachtete Effektstarts, vollständige Modell-/Miniatur-/Savezellhashes,
echte History/Cursor und Savebytehash/-länge vor/nach Ablauf. Der unabhängige
`tools/zs2_evidence.py`-Reader berechnet Zellmatrix, kanonische History und gerichtete
Starts separat und prüft IDs, Assertions und Gesamtbilanz ohne feste Checkzahl.
Er läuft im Harness und erneut im Ergebnisgate auf dem hashgebundenen Originallog.
Fehlende/gedoppelte/umetikettierte Fälle, falsche Beobachtungen und auch nachträglich
neu gehashte manipulierte Payloads scheitern. Package CI führt den Reader auch im Ergebnisgate auf den temporären Originalen aus;
der manuelle Diagnoseweg lädt dafür seine gebundenen Quellen. Kein Chromiumauftrag.

Die kleinen Reader-/Payloadgegenproben prüfen den aktuellen Integritätsvertrag.
Keine neue Prozess-/Bildfamilie und kein Studienreplay. Frühere Baselines und
Liefergates stehen im zugehörigen #502-PR, nicht als offener Auftrag in dieser Quelle.

## Risikobasierte RP6-Darstellung · #502 / P2-F-A-V01-P01

Die [verbindliche Vorbereitung](https://github.com/venomenon328/picross/issues/502#issuecomment-6659141735)
und [D02](https://github.com/venomenon328/picross/issues/502#issuecomment-6655391391)
ersetzen ausschließlich die bisherige RP6-Darstellungsmatrix. Zwei echte native
Captureprozesse mit zehn Zuständen ersetzen vier Prozesse mit 40 Zuständen:

| Fixture | Verbleibende Konfiguration | Verbleibende Zustände |
| --- | --- | --- |
| T04, Mono 20×20 | 1920×1080/UI100 | work, detail, album-partial, completion, album-completed |
| T06, vier Farben 50×50 | 1280×720/UI125 | dieselben fünf Zustände |

`work` erhält die unkorrektierte eigene Füllung, falschen 3×3-Block, echte
Undo-/Redo-Eingaben, Miniaturpixel, Hinweisfont, Fit und erreichbare Controls.
`detail` beobachtet den Zustand nach neun echten Undo-Klicks und Plus-Klick;
`album-partial` eigene falsche Vorschau und Spoilergrenze. Für `completion`
wird die erste App verworfen und der zuvor in den echten Partial/Finish/Read-
Prozessen erspielte Abschluss frisch geladen; `album-completed` beobachtet
denselben verdienten Inhalt im Album. Beide Abschlussansichten prüfen konkrete
native Weiß-/Hintergrundpixel und proportionale, slotgebundene Bildfläche.
Kein vorbereiteter Abschlusssave ersetzt die reale Kette. Die bestehenden
Komponentenproben verwenden `book_fixture.gd`; sie behaupten keinen zusätzlichen
unbeschleunigten Buch-Lifecyclelauf.

**Bewusster Entfall ohne gleichwertigen Ersatz:** T04 bei 1280/UI125, T06 bei
1920/UI100 und T08/T09 jeweils bei beiden Konfigurationen verlieren jeweils
alle fünf Zustände. T08/T09 sind weitere synthetische 40×40-Vierfarbmuster;
ihre Integritätsketten bleiben vollständig. Die folgende Risikotabelle gilt für
jede dieser sechs entfernten Fixture-/Fensterkombinationen, also 30 Zustände:

| Entfernter Zustand | Nun möglicherweise unentdeckter Fehler / Spielerwirkung | Verbleibende Ebene und Risikodisposition |
| --- | --- | --- |
| work | Nur dort falsche Miniaturfarbe, Hinweis-/Buttonclipping oder unzugängliche Historyschaltfläche | Zwei ausgewählte RP6-Fälle, VS2/Graphics und Kataloggrundfälle prüfen gemeinsame Darstellung; keine identische Variantenabdeckung. Mittleres lokales Bedienrisiko bewusst akzeptiert. |
| detail | Nur dort falsches Zoomlayout nach Undo/Plus oder versetzte Vorschau | Echte RP6-Undo-/Saveketten aller vier Fixtures und VS2 bleiben; das spezielle Ansichtsbild entfällt. Niedriges bis mittleres Darstellungsrisiko. |
| album-partial | Nur dort abgeschnittene Karte oder falsche Darstellung eigener Markierung | Alle vier RP6-Partialprozesse prüfen weiter eigene Füllung, Undo/Redo und verborgene Payload/Namen; Katalog prüft Scroll-/Statuswege. Kosmetische Kombination nicht mehr beobachtet. |
| completion | Nur dort falsch skalierte/gefärbte Abschlussanzeige | Alle vier Finish-/Readprozesse prüfen Lösung, Asset und Persistenz; EA und die zwei ausgewählten Captures prüfen Darstellung. Niedriges bis mittleres visuelles Risiko ohne Datenverlust. |
| album-completed | Nur dort abgeschnittenes oder falsch gezeichnetes verdientes Albumbild | Alle vier Readprozesse binden verdientes Asset/Name; Katalog und zwei Captures bleiben. Niedriges bis mittleres visuelles Risiko. |

T06 behält die größte Raster-/Farblast in der engen Konfiguration, T04 den
normalen Monopfad. Seltene 40×40- oder jeweils größenabhängige Fehler können
bewusst durchrutschen. Der bisherige positive Lauf enthielt keinen ungültigen
RP6-Geometriefall; dessen Prüfzweig ist kein behaupteter neuer Nachweis.
Keine Änderung an Spiel-/Save-/Registry-/Renderer-/Atlascode, ZA-1 oder PCK.
Alle zwölf RP6-Partial/Finish/Read-Prozesse, die zwei T04-Fremdslotprozesse und
deren Byteprüfungen sowie sämtliche ZA-1-Phasen bleiben unverändert.

`RP6_CAPTURES`/`RP6_STATES` in `native_contract.py`, der Producer und
`native_artifacts.json` verlangen nur die beiden Originalberichte und Phasen.
`native_results.py` liest jeden ausgewählten Bericht unabhängig: exakte eindeutige
Zustandsfolge, echte Slot-/Definitions-/Palette-/Viewportbindung, Einzelassertions
mit positiven Ergebnissen, Checksumme, falsche eigene Zellen vor/nach Undo,
Spoiler-/Abschlusszustand und tatsächliche Pixelwerte. Fehlende ausgewählte
Originale, neu gehashte Manipulationen, Duplikate oder Fachfehler scheitern.
Quell-/Head-/Basis-/Run-/Versuchsbindung und unveränderte übrige Gates bleiben.
Drei kleine Python-Testmethoden sichern Auswahl, Reader und kompletten Payloadweg.
Keine neue Prozess-/Bildfamilie; Erfolg weiterhin ohne RP6-PNGs.

## Risikobasierte Grafikstichprobe · #502 / P2-E-B-V01-P01

Die [verbindliche Umsetzungsvorbereitung](https://github.com/venomenon328/picross/issues/502#issuecomment-6657459064)
und [D02](https://github.com/venomenon328/picross/issues/502#issuecomment-6655391391)
erlauben ausdrücklich den folgenden Verlust automatischer Abdeckung.
Ausgangsbasis ist `d5d3a0c5c7ab1a0e79a4133e5ea47cd675cf02cf`,
Vergleichslauf 42013628529/1. Dies ist keine abdeckungsneutrale Konsolidierung.

Die VS2-Matrix sinkt von 96 auf 18 Fälle (G/V sind die beiden Ansichten):

| Client/UI | Beibehaltene Fälle | Zweck |
|---|---|---|
| 1280×720/125 | T-01 G; T-02 G/V; T-06 G/V; VS06 V; VS09 G | enger Mono-/Farbfall, großes Raster, beide bisher ungültigen V-Geometrien, breites Rechteck |
| 1920×1080/100 | T-01 G; T-06 G; VS04 G/V; VS08 G/V; VS09 G/V | sämtliche bisherigen acht Rahmenpixel-Fälle |
| 2560×1440/125 | T-02 G/V; VS07 V | großer Farbfall und hohes Rechteck |

Die übrigen 78 Kombinationen entfallen ohne gleichwertigen Ersatz. Beispielsweise
können ein nur bei T-08 auftretender Hinweisüberlauf oder ein ausschließlich bei
VS03/1280/V falsches Fit-Limit unentdeckt bleiben. Die Assertions pro gewähltem
Fall bleiben: unabhängige Layout-/Schriftmathematik, Fit/Zoom, Ecktreffer,
gesperrte Eingabe bei ungültiger Geometrie und passive proportionale Miniatur.
Alle 15 Bildfall-Metadaten einschließlich echter vierseitiger Rahmenpixel und
die gesonderten fünf Rechteck-Eingabe-/Undo-/Reveal-Fälle bleiben erhalten.

Die fünf getrennten kompakten Renderprozesse bleiben. Ihre Auswahl wird:

| Stufe | Vorher → danach (Frames) | Entfall und akzeptiertes Risiko |
|---|---:|---|
| layout | 10 → 3 | Album, enger T-06 mit unabhängigen Slots und normaler T-02 bleiben. Sieben reine Aufnahmen ohne eigene Pixelassertion entfallen; deren zustandsabhängige Renderfehler werden nicht mehr durch diese Aufnahmen ausgelöst. |
| cells-f1 | 18 → 10 | Schritte 12/16/18/24/72 bleiben, 22 und reine Removal-Aufnahmen entfallen. Ein nur bei 22 oder in der Removal-Komposition sichtbarer Fehler kann durchrutschen. |
| cells-f2 | 36 → 13 | Bestätigte Füllungen aller Farben bei jedem gewählten Schritt; Preview aller Farben bei 24, sonst Farbe 1. Fehler einer anderen Previewfarbe nur bei kleinem/großem Schritt sind nicht mehr direkt geprüft. |
| axis | 76 → 30 | Zehn feste Fälle unverändert. ZR: alle elf Positionen bei 1280/UI125/Zoom12; bei Zoom72 Cursor und gegenüberliegende Ecken (0/7/10) in allen drei Clients. 46 weitere ZR-Kreuzungen entfallen; z. B. ein nur rechts bei 2560/Zoom12 abgeschnittener Zähler kann unentdeckt bleiben. |
| h1 | 18 → 10 | Off/On bei eng/G, normal/V und groß/V; Mono-/Farb-Reveal und Album bleiben. Drei weitere Ansichts-/Client-Paare und dritter Reveal entfallen; z. B. ein ausschließlich großes G betreffender Strichfehler bleibt möglich. |

Zusammen 158 → 66 Frames. Füll-/Moat-/Alpha-Pixelassertions, beide vorhandenen
Zellpixelmutanten, ZR-Glyph-/Hintergrund-/Randprüfung und H1-Token-/Cache-/Raster-/
Miniaturassertions werden in den verbleibenden Fällen unverändert ausgeführt.
HN/HF/HS, VS2-Save/Restart/V2/GF1, ZS2-Bewegungsoriginale und Mutanten,
Atlas-/Cache-/Ressourcenprüfungen, PERF-B sowie Buch-/Playerexport bleiben
unverändert. Es gibt keine Produktänderung, neue native Phase oder Erfolgs-PNG.
Producer und unabhängiger Ergebnisleser verlangen exakt diese Auswahl;
fehlende, doppelte und fremde Fälle sowie widersprüchliche Summen schlagen fehl.

## Risikobasierte Katalogstichprobe · #502 / P2-E-A-V02

[Auftrag P01](https://github.com/venomenon328/picross/issues/502#issuecomment-6655568794)
und [Eigentümerentscheidung D02](https://github.com/venomenon328/picross/issues/502#issuecomment-6655391391)
ersetzen für KE/KK ausdrücklich die bisherige Abdeckungsneutralität. Dieser
Abschnitt beschreibt den Umfang bei ausgewähltem `native.catalog`; frühere vollständige Größen-/Status-/
Metadatenkreuzprodukte in KE/KU/KK-Berichten sind keine zusätzliche Pflicht.
Produktfunktionen und Unterstützung der Difficulty-Methoden 0.1–0.4 ändern sich nicht.

| Fallgruppe | Bisher / jetzt regulär | Bewusst verlorene Erkennung und Risikobegründung |
| --- | --- | --- |
| KE Grunddarstellung | Drei Flächen → 1280×720/UI125 und 1920×1080/UI100, jeweils null und aktuelle L1–L5, Schrift-/Metadaten-/Footer-/Spoilergeometrie | Nur bei 2560×1440 auftretende Metadaten-/Iconfehler werden nicht mehr in dieser Detailmatrix entdeckt. Enge Fläche und beide UI-Rollen bleiben; geringe kosmetische Wirkung ohne Saveeingriff. |
| KE Mutation/Readback | 3×5 Formen → einmal null, aktive 0.4 und editoriale 0.1 mit breitem plausible_range; native Kreismitte, unbekanntes Motiv größeninvariant; ein UI-Rundweg statt 15 | 0.2-/0.3-spezifische native Farbe, Hover oder Geometrie sowie nur bei anderer Größe auftretende Legacyfehler können entgehen. Vorhandene günstige Core-/Schema-Kompatibilitätsprüfungen bleiben, ersetzen diese Grafikfälle aber nicht. |
| KE Tooltip | Negativer verzögerter Kreis-/Texthover und positiver Modustooltip jeweils einmal unter UI125, unveränderte 0,8-s-Wartefenster | Legacy-/größenspezifische Popups oder fehlende Modushilfe bei anderer Größe werden nicht mehr vollständig beobachtet; begrenzte Bedienhilfe, keine Integritätswirkung. |
| KE Resize | 41 Breiten → fünf: 1280, 1920, 2560 bei 16:9/UI125 plus abgeleitetes Grenzpaar | Zwischenbreiten und weitere Spaltengrenzen können Clipping-/Rundungsfehler verbergen. Beide Seiten einer echten Grenze sowie schmal/normal/groß bleiben; kein Anspruch auf alle Pixelabstände. |
| KE Pointer | 8 Kindflächen × 3 Größen → einmal echte Karte und überlagernder Difficulty-Kreis unter UI125 | Ausschließlich auf Papier, Blatt, Status, Notiz, Modus oder Text beziehungsweise bei anderer Skalierung verlorene Klicks werden nicht mehr einzeln gefunden. Repräsentative echte Ereignisse bleiben, keine gleichwertige Hitflächenabdeckung. |
| KE eigene Vorschau | Falsche eigene Füllung → Undo/Redo-only → X-only unverändert einmal | Kein Verzicht auf die bestehende Spielstand-/Spoileraussage. |
| KK Zustand/Bild/Tooltip | Drei volle Ketten → eine bei 1280×720/UI125; UI100/1920 und UI125/2560 prüfen nur frische Grundgeometrie, Schrift, Status-/Reset-/Spoilergrenzen | Nur bei entfernter Größe und Begonnen/Gelöst/langem Namen/Reset auftretende Clips, Bild-/Häkchen-/Tooltipfehler können entgehen. Der enge Fall schützt den kompletten Lebenszyklus; die weggefallenen Größenkreuzprodukte werden bewusst nicht ersetzt. |
| KK Resize | Sechs feste Zahlen → zwei Seitenverhältnis-Endpunkte 1279×1080 und 1921×1080 | Mittlere Seitenverhältnisse ohne Vollmatrix. Dies sind keine behaupteten Spaltenwechsel; der echte Grenzfall liegt in KE. |
| KK Save/Recovery | Vollständiger Save-/Resetpfad einmal; recovery_pointer_cases und empty_write_error unverändert vollständig | Keine Streichung ihrer Fehler-, Fremdslot-, Ziel-ID-, Flush-, Reparatur-, Drag-/Rad-/Mauscapturegarantien. |

KKs vollständige enge Kette enthält frisch/leeren Save, echte Pointerbearbeitung
mit Undo, Begonnen ohne Reveal, Lösung über Session/Gesten und tatsächliches Save,
Gelöst mit verdientem Titel und unabhängigem Häkchen-Pixelvergleich, breites/hohes
Bild, langen Namen/Kategorie, negativen Karten-/positiven Resettooltip samt
UI-Rundweg und bestätigten Reset bei Filterwechsel mit Fremdslot-Bytevergleich.
Die weiteren neun Katalogmodi, Core, Graphics, Export/PCK bleiben unverändert.
Elf echte native Spielprozesse und deren bestehende Projekt-/Profilisolation bleiben.

Die Resize-Stichprobe misst verfügbare Scrollbreite abzüglich Balkenreserve und
2×UI sowie Kartenminimum und Spaltengap. Aus den Messungen bei 1920/2560 wird
bei gleichem Seitenverhältnis die physische Zweispaltengrenze interpoliert:
`available = 2 * minimum_width + gap`. Das Paar liegt acht Pixel unter dem
abgerundeten beziehungsweise über dem aufgerundeten Schnitt. Beide nativen
Messungen müssen tatsächlich eine beziehungsweise zwei Spalten zeigen; ansonsten
scheitert die Prüfung. Das Gate prüft zusätzlich Herleitung, 16:9, UI125,
Referenzgrößen, identisches Minimum und gemessene Spaltenzahl. Keine willkürlichen
Pseudo-Grenzzahlen und keine neue Suchschleife durch Zwischenbreiten.

`CATALOG_CASES` in `native_contract.py` bindet elf KE- und zwölf KK-Checkpoints in
Ausführungsreihenfolge. `kat2_probe.gd` meldet dort die tatsächlich seit dem letzten
Checkpoint ausgeführten Checks; positive Anzahl und Summe müssen dem Original
entsprechen. Producer und unabhängiger `native_results.py` lesen die verbleibenden
Fälle und KE-Resize-Messwerte. Die Checkpoints belegen Pfadausführung, keine
Ersatzorakel für gestrichene Varianten. Native Assertions und Gesamtfehlerliste
bleiben maßgeblich. Alle Originaldateien, elf Phasen, Summarygleichheit, Hashes und
Source/Base/Test-Merge/Run/Attempt bleiben unabhängig gebunden; das vorhandene
Artefaktinventar bleibt unverändert. Drei kleine Python-Testmethoden prüfen
Auswahl, fehlende/doppelte/unausgeführte Fälle und gefälschte Grenzbelege.

Die gestrichenen Kreuzprodukte werden nicht in einen anderen Pflichtjob verlagert.
Gezielte Untersuchungen konkreter Regressionen bleiben separat möglich. Frühere
U01-/T01-Läufe sind Baselines ihrer tatsächlichen Commits, keine heutige Volltestpflicht.

## Adaptervorbereitung · #502 / P2-D-V01

ZA-1 erhält eine eigene vollständige Kopie der gerade importierten synthetischen
Basis, unmittelbar nach `import` und vor den ersten nativen Tests. Dateiliste,
Größen und SHA-256 müssen für Quelle und Kopie übereinstimmen. Vor der späteren
Registrierung wird die wartende Kopie nochmals gegen dieses Inventar geprüft.
Danach gehören Projekt, Registrierung und Importe ausschließlich ZA-1;
RP6 verwendet weiterhin sein eigenes Projekt und seine echten Spielstände.
Das bestehende `za1-import` verarbeitet weiterhin alle vier neu registrierten
Pakete. Es entfallen nur die erneuten Importe unveränderter Basisressourcen.

`za1/summary.json` und der Gruppenbericht binden Inventardigest, Datei-/Bytezahl
und Kopier-/Prüfzeit. Vier eigene Registrierungen, zehn ZA-1-Spielprozesse,
Save-/Recovery-/Fremdslotprüfungen, Windows-Export und externer PCK-Audit sowie
sämtliche RP6-Prozesse und damaligen Captures blieben in P2-D erhalten; P2-F-A
reduziert ausschließlich die Captureauswahl wie oben festgelegt. Diese Importoptimierung erweitert die Modulauswahl nicht. P2-D-V01-T01 am
zugehörigen PR bindet die damalige Wirkung und Messgrenzen.

## Buch-/Hilfeprüfung und Studienrückbau

`native.export` enthält seit [P2-F-C/D03](#p2-f-c-v01--502-buch-lifecycle-nur-auf-ausdrücklichen-anlass)
keinen `regular-book-integration`-Prozess mehr. `tools/book_lifecycle.py` bleibt ein
nur ausdrücklich aufrufbarer Diagnoseweg mit `book-version`, `book-import` und
`book-integration`. Nur dieser Weg bindet Quellen, Lifecycle-/HIL-Assertions,
`integration/integration.json` und drei Prozesslogs. Keine Hilfe-PNGs; sein
Inventar hat `pngs=0`. Die bewusst entfallende automatische Kopplungsprüfung und
verbleibende modulabhängige Abdeckung stehen im Risiko-/Resttestvertrag oben.

Die frühere Vollstudie, Filmproduktion, Material-/Tooltip-/N03–N06-Matrix und
Studienexporte sind aus dem aktiven Pfad entfernt. Historische B-A-/B-B-Nachweise
stehen in [BOOK_STUDY](BOOK_STUDY.md) und [B_B_VERIFICATION](B_B_VERIFICATION.md).
Die reguläre [Buchintegration](BOOK_INTEGRATION.md) und ihre Produktressourcen bleiben.
`book_fixture.gd` stabilisiert Komponentenproben synchron; dies ist kein
unbeschleunigter Bewegungsnachweis. `book-save-v1.json` bleibt ein synthetischer
Schema-1-Input. `tests/*` und `study/*` gehören nicht in das Spieler-PCK.

`book_windows_probe.py` und der externe lesende Windowsbeobachter sind gezielte
Diagnosewerkzeuge. Tatsächliche Desktop-/Mauseingaben benötigen passenden Auftrag
und Umgebungsfreigabe; keine automatische Wiederholung aus einem historischen
B-B-/HIL-Auftrag. Offene persönliche Abnahmen und Befunde im aktuellen Issue/PR
prüfen, nicht aus alten Lieferstatusabsätzen übernehmen.

## Isolation, CLI und Prozessschutz

Für einen lokalen gezielten Lauf `p1_product.py --groups <gruppe>` verwenden.
Ohne Auswahl startet der lokale Harness weiterhin die vollständige Vereinigung;
das ist kein empfohlener Routineaufruf. Alte Flags bleiben kompatibel erweiternd:
`--integration` wählt history/catalog/completion, `--pilots` adapters,
`--visual`/`--perf-b` graphics; core/export bleiben in dieser Flagfamilie enthalten.
Package CI übergibt ausschließlich die gewählte explizite Gruppenliste.

Jede Gruppe verwendet einen eigenen Pythonprozess, temporäres Projekt und
APPDATA/LOCALAPPDATA- beziehungsweise XDG-Profil. Nur hashgeprüfte Downloadarchive
werden geteilt und erneut geprüft; keine gemeinsamen veränderlichen Saves oder
Ergebniscaches. Bytegleich geprüfte Importbasiskopien für Katalog, EA und ZA-1
sparen Imports, bleiben aber anschließend getrennt. Die Herkunft/Messung ist
im jeweiligen Originalbericht gebunden.

Unter Linux können catalog/graphics mit den übrigen seriellen Gruppen auf
eigenen Xvfb-Displays überlappen; export wartet auf beide Rendergruppen.
Unter Windows laufen native Fenster wegen des Fokus seriell. Linux-Software-
Rendering verwendet die vorhandene Threadpolicy einschließlich der Ausnahmen
für echte Save-/Bewegungszeitfenster. Eine kürzere CPU-Zeit ist nicht automatisch
ein gleich großer Gewinn des kritischen Pfads. Laufzeiten, Queue, CPU soweit
messbar, Cachezustand und Uploadkosten getrennt ausweisen.

Bestehende Prozess-/Netzwerk-Hängerschutzgrenzen bleiben technische Grenzen:
der native Prozessstandard beträgt 300 s; `kat2-kk` warnt einmal bei 300 s und
stoppt bei 600 s. Normale Exit-/Engine-/Marker-/Fachprüfungen gelten auch zwischen
diesen Werten. Der Originalbericht bindet wirksame Timeout-/Warnwerte und tatsächliche
Dauer; ein Timeout bleibt Fehler und räumt die eigene Prozessgruppe auf.
Das ist keine maximale CI-Gesamtlaufzeit. Zehn Minuten bleiben das weiche Ziel.
Die frühere `book-native`-Ausnahme betrifft eine entfernte Studienphase.

## Historische Quellen

Der [vollständige Vorgänger](https://github.com/venomenon328/picross/blob/f3626f28899a48fa4d783716925f7425a3eb1784/docs/CI_C_NATIVE_GROUPS.md)
bindet frühere 500er-/96er-/423-PNG-Matrizen, Originalkodierungsversuche,
Uploadregeln und damalige Liefergates. Diese werden nicht als heutige Normen
wiederholt. Die oben erhaltenen risikobasierten Stichproben dokumentieren die
bewusst entfallene Erkennung; sie sind keine Behauptung vollständiger Abdeckung.
Aktuelle Änderungen und ihre Abnahmen stehen im zuständigen Issue/PR.
