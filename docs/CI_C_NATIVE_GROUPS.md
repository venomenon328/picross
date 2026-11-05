# CI-C: Native Prüfgruppen und Belegvertrag

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
neu gehashte manipulierte Payloads scheitern. Der sparse Checkout des Gates enthält
den Reader; die Workflowdatei autorisiert dadurch keinen Chromiumlauf.

Keine neuen Prozesse, Bilddateien oder Studien. Kleine Python-Gegenproben sind
aktuelle dauerhafte Integritätsregression, keine Abnahmearchivierung. Technische
Logs bleiben sieben Tage, Spielerpakete 14 Tage. Lokale Messungen und endgültige
CI-/Head-/Run-/Attempt-/Kostenbindung stehen im P2-F-B-V01-T01 des zugehörigen PR;
R01 und ausdrückliche Mergefreigabe bleiben separat. Das CI2-Ziel unter 600 s ist
offen: Die bisherige gesamte ZS2-Phase von 84,737 s reicht allein nicht, um die
native Auswahl von 755,347 s unter 600 s zu bringen.

## Aktueller Minimalumfang · #502 / P2-C-V03

Die [ersetzende Eigentümerentscheidung](https://github.com/venomenon328/picross/issues/502#issuecomment-6637589747)
und der [vollständige 435-Pflichten-Audit](P2_C_V03_AUDIT.md) ersetzen die unten
historisch beschriebenen V02-/CI2-D-Bildmengen. Erfolgreiche Standardprüfungen
liefern grundsätzlich keine Sichtbilder. Einzige aktuelle Rohpixelausnahmen:
fünf AT-Kompositionssamples (je 5×2 RGB8) und fünf HN-Bandsamples (je 50×100 RGBA8),
die das unabhängige Ergebnisgate selbst fachlich liest; Einzelzweck, Trigger,
Kosten und Reviewfrist stehen im Audit. 423+5+7 ist ausschließlich die Baseline.

HZ-/KE-/HC-Einführungsbilder, separate V1-/V3-/Z2-Läufe, ZS-Studienmatrix,
EA-Film/Phasenbilder und HIL-Sichtdateien sind keine aktive Pflicht mehr.
Die dazugehörige Produktion, Reader, Prozess-/Bildinventare und Gates entfallen.
Mit den unten geregelten Ausnahmen P2-E-A-V02, P2-E-B-V01 und P2-F-A-V01 behalten
KAT/HF/V2/ZA1/RP6/PERF/Raster ihre aktuellen Fach-/Pixel-/Saveassertions
ohne Erfolgsbilder. Aktuelle Layoutmathematik nutzt die vorhandenen VS2-Messungen.
HS liest fünf temporäre Layerbilder, ZS 24 temporäre Bewegungs-Crops; beide
prüfen echte Originale und Pixelmutanten vor dem Löschen. Die Arbeitsmessung
zählt diese konsumierten Daten weiterhin, unabhängig vom gelieferten Inventar.

`native_contract.py`, `native_artifacts.json` und `native_results.py` bilden dieses
neue Soll gemeinsam ab. Alle sieben Gruppen bleiben vorhanden; Änderungen an
gemeinsamen Prüfquellen wählen weiterhin konservativ alle. Source/Head/Basis/Run/
Versuch, Fachfehler, Save-/Recovery-/PCK-/Playerbytes und unabhängige AT/HN-Pixel
bleiben fail-closed. Historische Aliasdateien werden nicht rekonstruiert, um alte
Pflichten aufrechtzuerhalten. HIL-M01 und weitere persönliche Abnahmen bleiben offen;
Einmalbelege nur auf konkreten Auftrag außerhalb der Regel-CI. Kein Chromium.

Die folgenden Lieferbeschreibungen bleiben historische Quellen ihrer jeweiligen
Revision, soweit sie alte Bilder, Reader, Mengen oder Einführungsprozesse nennen.
Die 300-/KK-600-s-Grenzen, Scheduler und funktionalen Zeitfenster ändern sich nicht.
Das CI2-Ziel unter zehn Minuten bleibt ein Optimierungsbefund.
P3-B-D01 verwirft den alten 75-MiB-Richtwert und feste Mengenobergrenzen.


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

Baseline ist Run 42027188774/2 auf Test-Merge
`5f13633003ceafecad6fa2d5b14d417c28f5d662`, treegleich zur Arbeitsbasis
`4a65157063a71ca8f3239fd04994dc6a5e90598c`: vier Captures 80,427 s,
Adapters 373,777 s, native Gesamtzeit 826,476 s. Der T01 am Liefer-PR vergleicht
echte Linux-/Xvfb-/Mesa-Zeiten, CPU soweit gemessen, serielle Lane und Bytes;
andere Gruppenschwankungen sind keine kausal zugerechnete Einsparung. <600 s
bleibt Ziel, kein Hardgate. Auswahl, Scheduler, Budgets, Technikretention sieben
und Playerretention vierzehn Tage bleiben. Unabhängiges P2-F-A-V01-R01 und
ausdrückliche Mergefreigabe sind getrennte offene Gates; #502 bleibt offen.

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

Baseline: Matrix 101,988 s, fünf Stufen 96,872 s, Grafikgruppe 495,543 s,
gesamter nativer Lauf 806,678 s. Die Grafik endete bereits vor den seriellen
Adaptern; eingesparte Grafikzeit ist daher kein behaupteter gleich großer
Gewinn auf dem kritischen CI-Pfad. Tatsächliche Nachherzeiten, CPU-Zeit soweit
gemessen, Dateizahlen/Bytes/PNGs, Selbstreview und ausgewählte Pflicht-CI werden
im P2-E-B-V01-T01 der Liefer-PR an deren exakten Stand gebunden.
Technische Artefakte bleiben sieben, Player vierzehn Tage erhalten; keine
neuen Mengenlimits und keine Löschung geschützter oder fremder Daten.
Unabhängiges R01 und ausdrückliche Eigentümerfreigabe bleiben vor Merge offen.

## Risikobasierte Katalogstichprobe · #502 / P2-E-A-V02

[Auftrag P01](https://github.com/venomenon328/picross/issues/502#issuecomment-6655568794)
und [Eigentümerentscheidung D02](https://github.com/venomenon328/picross/issues/502#issuecomment-6655391391)
ersetzen für KE/KK ausdrücklich die bisherige Abdeckungsneutralität. Dieser
Abschnitt ist der aktuelle Dauerprüfvertrag; frühere vollständige Größen-/Status-/
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

Die gestrichenen Kreuzprodukte sind aus der Standard-CI entfernt, nicht heimlich
in einen anderen Pflichtjob verlagert. Eine gezielte künftige Untersuchung einer
konkreten Regression kann sie auf eigenen Auftrag wieder aufgreifen. Historische
U01-Originale bleiben die Baseline. T01 am Liefer-PR bindet reale Linux-/Godot-/
Xvfb-/Mesa-Kosten je KE, KK, Catalog, Gesamtauswahl und kritischem Pfad sowie
bewusste Prüflücken. Keine isolierte Windowszeit als Linuxvergleich, keine
unbelegte 1:1-Verkürzung der Gesamtlaufzeit. KK-Warnung 300 s/Schutz 600 s,
übrige Phasenbudgets, fachliche Timer, Scheduler und CI2-Ziele bleiben unverändert.
Unabhängiges P2-E-A-V02-R01 und ausdrückliche Mergefreigabe bleiben offen.

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
reduziert ausschließlich die Captureauswahl wie oben festgelegt. CI-Auswahl,
Scheduler, Zeitbudgets und fachliche Orakel ändern sich nicht. Die konkrete
Wirkung und die Grenzen der Messung werden in P2-D-V01-T01 am PR gebunden.

## Zweckgebundene Zustellung · #502 / P3-B-L01

[Eigentümerentscheidung P3-B-D01](https://github.com/venomenon328/picross/issues/502#issuecomment-6641721279)
ersetzt frühere feste Byte-/Datei-/PNG-Grenzen, auch die historischen P3-B-Pläne.
`native_delivery.py` stellt im CI-Runner ein frisches Zustellungsverzeichnis bereit.
Bei Producer-Erfolg und gebundenem erfolgreichem `native-result.json` übernimmt es
sämtliche ursprünglichen Technikbytes unverändert unter demselben Artefaktnamen.
Das unabhängige Gate prüft weiterhin Quelle/Run/Versuch, Inventar, Pixel und Player.

Bei Fehlern bleiben das ursprüngliche Laufergebnis, kompakte Gruppenstatus und
nur die betroffenen Gruppenberichte/Phasen-/Prozesslogs sowie echte nominierte
Oracle-/Fehleroriginale erhalten. Validierungsfehler binden ihre Gruppe; deren
benötigte Originale bleiben einschließlich physischer Aliasquellen verfügbar.
Mehrere Fehler liefern mehrere Bereiche. Unterbrochene Producer dürfen vorhandene
Teilberichte und Phasenoriginale liefern, ohne ein Erfolgsergebnis zu erzeugen.
`diagnostics.json` weist ausdrücklich `accepted=false` aus; auch fehlende Dateien,
Bindungsfehler oder Zustellungsstörungen bleiben Fehler. GitHub-Joblogs erhalten
den frühen Fehlerpfad. Keine Wiederverwendung fremder Runs und kein Gesamtbaumdump.
Technik-/Fehlerbelege sieben Tage, echte ausgewählte Spielerpakete vierzehn Tage;
Feature-/Sichtbelege nur bis konkreter Abnahme/Review oder Ablauf. Keine neue
historische Belegsammlung und kein impliziter Browserauftrag.

## Neue Prüfungen und Featureabschluss · #502 / P3-A

Der [Lebenszyklusvertrag](CI_POLICY.md#testlebenszyklus-und-featureabschluss--502--p3-a)
gilt vor neuer nativer Prüf-/Bildlast: dauerhafte aktuelle Spiel-/Save-/Pixel-/
Exportregression oder befristeter Einführungs-/Abnahmenachweis, jeweils mit
Zweck, minimaler Ebene, Leser, Auswahl, CPU-/Wandzeit-/Datei-/Byte-/PNGkosten,
Verantwortung und konkreter Ablauf-/Reviewentscheidung. Neue Maschinen,
Frame-/Filmmatrizen, Generatoren und Artefaktklassen benötigen diese Erklärung
auch bei anderem Namen, Ausgabeordner oder optionalem Einstieg. Schwere neue
Dauerpflichten benötigen die separat gebundene Eigentümerentscheidung.
Der schnelle Docs-Guard prüft Quell-/Leser-/Auswahlbindung und Ablauf; T01 und
unabhängiges R01 prüfen Abdeckung und tatsächliche Kosten. Vor Featureabschluss
temporäre Last zurückbauen und verbleibende Dauerregressionen begründen.

Das heutige logische Pflichtinventar, seine physischen Aliase, alle Assertions,
Quellen-, Head-/Basis-/Run-/Versuchsbindungen und Pixel-/Exportgates bleiben
erhalten. Laufzeit, erzeugte/gelieferte PNGs und physische/logische Dateien/Bytes
werden weiter gemessen. P3-A setzt keine globale 75-MiB-/10-Minuten-Grenze,
ändert keine funktionalen Zeitfenster und erteilt keinen Browserauftrag. P2-C/P3-B bleiben
separat; bestehende Produktprüfungen werden nicht rückwirkend nach Namen verboten.

## Verlustfreie Originalkodierung · #502 / P2-C-V02

`game/tests/native_png.gd` schreibt ausgewählte native Originale direkt beim
Producer. Ausschließlich RGBA8 ohne Mipmaps wird auf einer Kopie nach RGB8 und
zurück nach RGBA8 konvertiert. Nur bei vollständiger Bytegleichheit darf die
RGB-Kopie in den bisherigen Godot-PNG-Writer gelangen. Alpha 254, weiche oder
transparente Pixel behalten RGBA; andere Formate bleiben unverändert. Das
gemessene Quellbild, Maße, Ausschnitte und RGBA-Hashes bleiben unberührt. Keine
Quantisierung, Skalierung, Palette oder nachträgliche Umschreibung gebundener
Originaldateien; keine zusätzliche Kompressionsstufe oder Bildproduktion.

| Originalfamilie | Tatsächliche Producer | Leser, Pixelorakel und Gate |
| --- | --- | --- |
| Graphics Render-/V1-Flächen und Glyphen | `capture.gd`, `vs2_tests.gd`, `vs2_v1_tests.gd` | Native Vergleichs-/Geometrieassertions vor dem Schreiben; `vs2_delivery`, `vs2_v1_verify`, Captureberichte und originale SHA-/Inventarbindungen |
| Graphics Vollhinweis / V2 / PERF-B | `hf149_probe.gd`, `vs2_v2_tests.gd`, `perf_b_probe.gd` | Native Pixel-/Cache-/Saveprüfungen; `hf149_verify`, `vs2_delivery.verify_v2`, PERF-Bericht und Originalhashes. Externe PCK-Proben laden den Encoder neben ihrem Skript; Tests bleiben außerhalb des PCK. |
| Catalog Layout / HZ / KE | `kat2_probe.gd`, `hz_native.gd`, `ke_graphics.gd` | Unveränderte native Assertions; `native_images.crop_native` dekodiert KAT-RGBA erneut und prüft Maße/Quellhash, `validate_catalog_images` und `validate_catalog_originals` binden Originale und Inventar. KAT ersetzt den bisherigen strikten Alpha-Loop durch denselben exakten Vertrag. |
| Catalog / Completion AT | `at_alpha.gd` | Importierte Alpha-Fixture, native Kompositionswerte und `at_evidence.native` lesen tatsächliche Bild-/Papierpixel einschließlich Weißdetails, Alpha 80 und transparentem Hintergrund. Der Standardbibliothek-Decoder unterstützt RGB und RGBA bereits. |
| Completion statische und gepufferte Bewegungsframes | `ea_probe.gd` | Native Commit-/Save-/Restart-/Zeit-/Geometrieassertions; `ea_product.prepare_images` behält die tatsächlichen Zeitstempel, fünf abgeleitete Phasen und APNG. Kodierung der gepufferten Bewegung erfolgt weiterhin erst nach dem Zeitfenster. |
| Export sieben HIL-Flächen | `help_native.gd` | Native Hilfe-/Save-/Recoveryassertions; `book_contract.SOURCES` bindet zusätzlich den Encoder, auch im Sparse-Checkout des unabhängigen `validate_book_lifecycle`. Originalmaße 1920×1080, Dateihashes, Assertions und Pack-/Exportgates bleiben Pflicht. |

Unverändert bleiben HN-Samples (`hn192_probe`/`hn_evidence`: rohe RGBA-Hashbindung),
HC92/HS186, Zeichnungs-/Zeitfolgen aus ZS1/ZS2, bereits RGB-kodierte V3-Originale,
RP6/ZA-1, separate PCK-/Fensterproben und sämtliche Produkt-/Reveal-/Atlasassets.
Die APNG wird nicht neu optimiert. `Evidence.retain_files`, `native_artifacts.json`,
`native_contract.py` und `native_results.py` behalten ihre exakten Original-,
Alias-, Quellen-, Zeit-, Save-/Recovery- und Exportanforderungen. Der gemeinsame
neue Testpfad wählt konservativ alle nativen Gruppen; kein Chromiumauftrag.
Fehlende/manipulierte Pflichtdaten scheitern weiter unabhängig. Kleine native
PNG-Puffer-Gegenproben über alle 256 Alphawerte laufen im bestehenden Coreprozess,
ohne zusätzliche Dateien oder Prozesse; der HN-Gegentest verwirft auch RGB-Samples.

Die begrenzte Untersuchung verwendet den tatsächlichen V01-Erfolg aus
[Run 41851661750](https://github.com/venomenon328/picross/actions/runs/41851661750),
Versuch 1: 147.554.626 Archivbytes, 555/624 physische/logische Dateien,
366/435 PNGs und 914,310 s native Gesamtdauer. Alle 366 statischen Originale
wurden in der einmaligen A/B-Probe mit vollständigem RGBA-/Maßvergleich geprüft;
eine zusätzliche 15-Bild-ABBA-Probe misst CPU, Wandzeit, Spitzenspeicher und ZIP.
Pillow-Stufen 1/3/6 rechtfertigten keine zusätzliche Rekodierung. Vollständige
Istwerte, Producergrenzen, lokale Befristung und finaler CI-Vergleich gehören in
V02-T01 am tatsächlichen Head/Run. Keine Behauptung eines kausalen CI-Zeitgewinns
aus verschiedenen Runnern. Der damalige 75-MiB-Richtwert ist durch P3-B-D01 überholt.

## Phasenschutz · #502 / P3-A-F02

Die [Eigentümerentscheidung vom 04.11.2026](https://github.com/venomenon328/picross/pull/506#issuecomment-6631521834)
ersetzt ausschließlich für `kat2-kk` den bisherigen 300-s-Abbruch: Während der
laufenden Phase wird bei 300 s einmal eine nicht-fatale Warnung in Konsole und
geflushtes Phasenlog geschrieben; der harte Schutz endet bei 600 s. Warnung und
Protokollierung verbrauchen denselben Rahmen. Erfolg zwischen den Grenzen bleibt
zulässig, sofern normale Exit-/Enginefehler-, Marker-, Fach- und Ergebnisprüfungen
bestehen. Alle 3.440 KK-Checks und Pflichtbilder bleiben erhalten.

Die bestehenden Phasenergebnisse in `product-report.json` enthalten tatsächliche
`seconds`, wirksame `timeout_seconds`, `warning_seconds`, `warning_emitted` und
`timed_out`; das gebundene Originalphasenlog hält Warnung bzw. Timeouttext fest.
Bei Timeout bleiben Fehlerstatus und die Bereinigung der eigenen Linux-
Prozessgruppe samt Nachkommen erhalten. Andere Phasen, auch `kat2-kk-import`,
übernehmen unverändert das jeweilige Aufruferbudget. Der Workflow bleibt bei
`--process-timeout-seconds 300`; Scheduler, Renderer und Threadpolicy bleiben
unverändert. Der gesonderte Buchproducer behält seine bestehenden Grenzen.

Kontrollierte Uhr-/Waitfälle und ein kurzer echter Linux-Kind-/Enkelprozessfall
prüfen diese Grenze im bestehenden Toolpfad ohne minutenlange Wartezeiten.
600 s sind ein Hangschutz, kein Leistungsziel. Tatsächliche CI-Zeiten und
verbleibende CI2-Zielverfehlungen werden in T01 am geprüften Head/Run ausgewiesen.

## Laufzeit und Originalpixel · #502 / P2-B

Die aktuelle Auswahl, sämtliche Produktassertions, KAT-2-Modi, nativen Prozesse,
funktionalen Zeitgrenzen und isolierten Projekte/Profile bleiben erhalten;
den selektiven KK-Hangschutz ersetzt F02 wie oben beschrieben. Nur Linux-
Softwarerenderprozesse erhalten `LP_NUM_THREADS=1`, ausgenommen die aktuellen
kurzen Save-/Schraffur-/Atlasbewegungs- und echten Buch-Lifecyclezeitfenster
(`kat2-information`, `current-drawing-capture`, `perf-b-native`, `book-integration`).
Die Gegenmessung mit einem Worker auch in diesen Zeitfenstern war fehlgeschlagen;
dort bleibt der ursprüngliche Mesa-Pool erhalten. Windows behält seine serielle
Fokusgrenze. Bereits vorhandene Editor-/Vorlagenarchive dürfen die Parallelität
nach erneuter vollständiger SHA-Prüfung sofort freigeben. Bei fehlendem/falschem
Cache bleibt zuerst ein echter serieller Gruppenlauf erforderlich. Jeder Producer
prüft weiterhin seine Archive und extrahiert eigene Werkzeuge. Kein importiertes
Projekt, Save oder Prüfergebnis wird gruppenübergreifend geteilt. Der Python-
Downloadpfad nutzt das vorhandene kurzlebige Jobtoken mit den unveränderten
Leserechten gegen anonyme GitHub-API-Limits; Godot erhält dieses Token nicht.
Export wartet
weiter auf beide Rendergruppen. Start-/Endoffsets, Cachevorbereitung, CPU-/
Kontextwechselkosten und Ergebnisprüfung werden separat gemessen; RSS ist der
bisherige Höchststand aller beendeten Kindprozesse, keine isolierte Phasenmessung.

KAT-2 behält alle 53 Layoutaufnahmen und unveränderten Ausschnittkoordinaten.
Der native Producer speichert sofort das bisher in Python ausgeschnittene
Rechteck. Originalframe-Maße/RGBA-Hash, Ausschnitt/RGBA-Hash und native PNG-Bytes
bleiben gebunden. Python prüft dekodierte RGBA-Pixel einschließlich Alpha und
liefert dieses native PNG nach Umbenennung einmal aus. Vollbildencoding,
erneutes Zuschneiden/Encoding und doppelte Kontextdateien entfallen. Die
unveränderten direkten KE-/HZ-/AT-Bilder bleiben im Pflichtinventar. Der bestehende
ausdrückliche PNG-Vergleich prüft zusätzlich den unabhängigen Pythonzuschnitt
eines identischen nativen Vollframes; Vergleichskopien entfallen nach Gleichheit.

HN behält alle 15 Fälle und sämtliche bisherigen Pixel-/Eingabe-/Cacheassertions.
Statt 15 Vollbildern liefert jeder Fall die exakt verglichenen 2.500 Originalpixel
und ihre 2.500 Basispixel in einem 50×100-PNG: oben Ist, unten Basis, ohne
Interpolation. Quellframe-/Basis-/Sample-RGBA-Hashes, Client, Board, Rasterursprung,
Zellgröße, Overlay und Kontext bleiben im Originalbericht. `hn_evidence.py`
wiederholt unabhängig alle Band-/Phantomvergleiche einschließlich Alpha und
natürlicher Overlayausschlüsse. Fehlende Fälle, falsche Maße/Bindungen oder
auch konsistent neu gehashte falsche Pixel scheitern. Dies sind Pixelsamples,
keine verkleinerten Kontextbilder; die übrigen Vollhinweis-/Schriftoriginale
behalten ihre eigenen unabhängigen Leser.

Byteidentische PNGs werden nach erfolgreicher Erzeugung nur einmal physisch
geliefert. `image_aliases` bindet jeden logischen Originalpfad mit Bytezahl/SHA
an ein tatsächlich geliefertes, identisches PNG; Ketten, Fremdpfade, doppelte
Ziele, Nicht-PNGs oder Überschreiben sind verboten. Producer und unabhängiges
Gate rekonstruieren die exakten Originalbytes nur für die bestehenden Leser und
entfernen diese temporären Kopien auch nach Fehlern. Das feste logische Inventar,
Originalberichte und Einzelbindungen bleiben unverändert verpflichtend. Fehler-
artefakte werden nicht dedupliziert. Physische und logische Dateien/PNGs/Bytes,
erzeugte Arbeitsdateien sowie direkt im Technikbereich erzeugte HIL-PNGs werden
getrennt ausgewiesen. Globale Mengenguards sind durch P3-B-D01 verworfen; Lebenszyklusregeln
stehen oben unter P3-A. CI2-Ziele gelten
erst nach tatsächlicher Messung als erreicht. Messwerte und Restbefunde im P2-B-T01.

## Studienrückbau · #502 / P2-A

`tools/book_lifecycle.py` enthält ausschließlich den unveränderten kurzen
Hilfe-/Produktlebenszyklus. `p1_product.py` ruft ihn als
`regular-book-integration` auf; `validate_book_lifecycle` bleibt das unabhängige
Ergebnisgate. `book_contract.SOURCES`, alle Pflichtassertions, sieben HIL-Originale,
Phasen-, Hash-, Head-/Basis-/Checkout-/Run-/Versuchsbindung bleiben erhalten.
Die manuelle CLI desselben Producers verlangt `--cache-dir` und `--output-dir`.
Es gibt keinen Vollstudien-, Fixturegenerator- oder Studienexportmodus mehr.

Entfernt sind `tools/book_study.py`, dessen exklusive Tests und
`validate_book_study` samt N04–N06-/F01-/Projektions-/Pixelmatrixguards sowie
`game/study/book/`: 27 Definitionen, 27 Reveal-SVGs, Registry/RAM-Adapter,
Szenen-/Shaderdiagnosen, Tooltip-Vollmatrix, Packprüfer und Webshell. Die
[historische Quelle](https://github.com/venomenon328/picross/tree/fc86d2a2eff543f5b0c4ff328a71e815e4bc43a7/game/study/book)
und [B-A-/B-B-Liefernachweise](BOOK_STUDY.md) ersetzen deren aktive Reproduktion.
P1 hat die Filmproduktion bereits vollständig entfernt; sie wird nicht ersetzt.

Aktuelle `core`-/`history`-/`catalog`-/`completion`-/`adapters`-/`graphics`-/`export`-
Regressionen bleiben ausgewählt wie bisher. Insbesondere KAT-2 `kb` prüft echte
Hover nach Zellaktionen, lesbaren Text, Clientgrenzen und Abbau beim Seitenwechsel;
`kk`/`ke` prüfen Reset-/Modustooltips. Der vorhandene `kb`-Pfad ergänzt ohne neue
Bilder einen verzögerten Whitespacehover, verzögerten Popupabbau und erneuten
beschrifteten Hover. Das ist eine kleine aktuelle Prüfaussage, keine Behauptung,
den wechselnden Windowsbefund P1-R01-O01 reproduziert oder behoben zu haben.

Der weiterhin ausdrücklich manuelle `book_windows_probe.py` baut ausschließlich
den regulären synthetischen Windowsplayer und behält beide echten negativen
PCK-Überlagerungen, Hashbindung, Tooltip-/Release-/Fokus-/Save-/Retrydiagnosen.
Sein externer rein lesender Beobachter liegt in
`game/tests/book_windows_observer.gd`; beide verwenden den echten SaveStore,
keinen historischen RAM-Adapter. `product_fixtures.copy_regression_game` versorgt
beide aktiven Producer. `tests/*` und `study/*` bleiben im Runtimeexport gesperrt;
der PCK-Audit prüft weiterhin die tatsächlichen Verzeichnisse und den Entrypoint.
B-B-M01/HIL-M01 und P1-R01-O01 bleiben offen; kein automatischer Desktoplauf oder
Chromiumauftrag. Die persönliche Prüfung erfolgt am regulären Spieler.

Die Vollstudie lief bereits seit #501 nicht mehr in CI. Ihr Quellenrückbau
belegt keine CI-Beschleunigung; aktuelle Kosten stehen im P2-A-T01 des PRs.
Laufzeitoptimierung und neue Größen-/Lebenszyklusguards bleiben P2-B/P3.

## Aktuelle gezielte Buchintegration · HIL-1 / #500

Eigentümeranweisung vom 03.11.2026: In CI keine komplette Buchprüfung und keine
Filmproduktion. `regular-book-integration` führt deshalb ausschließlich
`book-version`, `book-import` und `book-integration` aus. Die letzte Phase nutzt
den regulären Produktroot mit festen synthetischen Inputs für Hilfe, Navigation
und unveränderten Spiel-/Savezustand; keine vollständige Studien-/Materialroute.
`book_lifecycle` und `book-lifecycle/report.json` binden denselben begrenzten
Umfang an Head, Basis, Checkout, Producer-Versuch und aktuelle Quellbytes.
Das Ergebnisgate verlangt sämtliche Lifecycle-/HIL-Einzelassertions, genau die
sieben unten genannten 1920×1080-Originale, den Assertionbericht und drei Logs.
Zusätzlicher Film oder eine Galerie werden abgewiesen; Spielprofile werden nicht
ausgeliefert. Die vollständige Studienroute ist aus dem aktiven Tree entfernt.
Historische B-B-Nachweise behalten ihren damaligen Umfang und werden dadurch
weder erneut verlangt noch nachträglich als verkürzte Prüfung ausgegeben.

## Historischer B-B-Vollumfang / #493, #498

Die folgenden Absätze beschreiben den damaligen Liefernachweis. Für aktuelle
automatische Läufe gilt ausschließlich der gezielte Umfang oben.

Die Exportgruppe verlangt einmalig `regular-book-integration` und dessen
[B-B-T01-Belege](B_B_VERIFICATION.md). Das Gate prüft originale Einzelassertions,
die feste Szenariomenge, Doppelseitengeometrie, beide Blätterrichtungen,
24 Unterbrechungsfälle, gültige ID-/Revealinstanzen, gerenderte Glyphen-/Konturabstände,
Rückkehr mit aktuellem Fortschritt, Quellbindung, Materialvergleich und Papierstabilität,
vollständige Phasen, Film mit stabilem Katalogende und neun Übergabepaare samt
Dateihashes. Der reale Produktlebenszyklus ergänzt eingefrorene Schema-1-Bytes,
Redo-/View-Wiederherstellung, Schreibfehler/Retry, ID-gebundene Recovery,
Abbruch-/Generationskontrollen sowie leere und fehlerhafte Kataloge.
Der unabhängige Guard bindet die gemeinsamen Runtimequellen an den aktuellen
Checkout und verlangt sämtliche Lifecycle-Assertions. Die regulären Export-
und Paketprüfungen bleiben zuständig für Windows/Web; die zusätzliche B-A-
Exportmatrix entfällt. Prüfskripte und Studieninputs bleiben im Technikartefakt.
N03 bindet zusätzlich die eigene Ledertextur samt Importkosten, 15 unskalierte
Randdetails, echte verzögerte Tooltipfälle in den drei bestehenden Konfigurationen,
deren Inhalt/Geometrie/Lebensdauer und Gegenbeispiele für leeren Rahmen und alten
Hoverstrich. Producer, Originalbericht, unabhängiger Guard und Mutationstests
folgen gemeinsam diesem Umfang. Keine neue Gruppe und kein Browserauftrag.
N04 erhält diese Nachweise, ergänzt genau eine gezielte 1920×1200/UI100-Fläche
mit fünfter Übergabe sowie günstige Nachbar-/UI125-Geometrieprüfungen. 24
unskalierte Randdetails binden beide inneren Enden und tatsächliche Quellmaße.
Das Gate kontrolliert links beginnende Belegung, unabhängige Offsets einschließlich
Abbruch/Resize, Originalglyphenhüllen und explizite Breite/Höhe statt 16:9-Ableitung.
Tischquelle/Importkosten und beidseitige Paketisolation bleiben gebunden. Ein
tatsächlicher Windows-Exportlauf ergänzt Standard/Maximieren/Wiederherstellen;
Linux behauptet diese Probe nicht. Für B-B erhält ausschließlich `book-native`
nach Eigentümerklarstellung vom 02.11.2026 einen 600-s-Hangschutz statt 300 s;
Laufzeitziele werden berichtet, sind aber keine zusätzlichen Abnahmeblocker.
N05 erweitert denselben Lauf um zehn echte Informationsrouten, zwei nahe
Seitenlayouts in vier gezielten Flächen, sechs native Unterbrechungen und eine
günstige vollständige Entscheidungstabelle. Fünf bisherige plus vier neue
Handoffs behalten die Grenzen 4/0,1 samt Versatz-/Alphagegenprobe. Der unabhängige
Guard prüft Ursprung, ungleiche Offsets, tatsächliche Kamera-/Blattspuren, native
Hüllen, Optionsänderung und Film. N05 führte keine neue CI-Gruppe, Budgeterhöhung
oder Browserpflicht ein; die spätere B-B-Ausnahme steht oben.
N06 ergänzt vier 640×128-Tiefenbilder des echten Mesh-/Vertexpfads:
Ruhe, gegenüberliegende Landung, verbreiterter Spalt und flache Geometrie.
Die beiden Gegenbeispiele müssen scheitern; tatsächliche Leder-/Blockarrays
prüfen Gelenktiefe und positiven Abstand unter den bestehenden Mengenbudgets.
Ein echter Tree-Exit prüft den unter Windows gefundenen reentranten Fokusabbruch
und die Bindung an dieselbe Bewegung. Der Guard verlangt Fälle, PNG-Maße und
Messwerte mit acht Mutationen.
Die obigen N03–N06-Prüfungen bleiben unverändert auf die gemeinsame Darstellung
angewendet. B-A-R08/M01 sind auf PR #497 abgeschlossen. B-B bindet neue reguläre
Windowsoriginale und echte OS-Eingaben für sein getrenntes Selbstreview sowie
das spätere unabhängige B-B-R01; die persönliche B-B-M01 bleibt gesondert.

HIL-1 / #500 erweitert dieselbe Integration um passive Lehrbeispiele und die
vier Hilfekapitel. `help_cases.gd` enumeriert die tatsächlich dargestellten
kleinen Belegungen unabhängig; `help_native.gd` prüft echte GUI-Ereignisse,
verschachtelte Schriftrollen, Platz-/Scrollgrenzen, Besuchs-/Rückkehrkontext und
unveränderte Spiel-/Savewerte. Keine neue Gruppe und keine zusätzliche
Spielprozessmatrix. Sieben Originale (`integration/hil-{work,principle,
combination,colors,overlap,legend,pan}.png`) sind über `book_contract.py` gebunden;
der Guard verlangt Quellen, Assertions und Dateien. Ein gezielter Pan mit dem
neuen Seiteninhalt gehört zur Hilferoute; die vollständige Übergabematrix und
Filmproduktion werden in CI nicht ausgeführt. Die
PCK-Prüfung verlangt die drei aktiven Hilfemodule; Tests bleiben ausgeschlossen.
Es entsteht kein Chromiumauftrag und kein exklusiver Desktop-Eingabelauf.

## Aktuelle Umsetzung: CI2-D / #416

Der freigegebene [CI2-Vertrag vom 26.10.2026](CI_SLIMMING.md),
[Gesamtissue #412](https://github.com/venomenon328/picross/issues/412), ersetzt
die nachfolgenden ungekürzten History-/Bild-/Prozesspflichten.
[CI2-D / #416](https://github.com/venomenon328/picross/issues/416) ist auf
`chore/416-ci2-d-native` von `main@8e5e99647596bc3ef9d7bd22bd746b73fbb424d5`
implementiert. [T01, Messungen und Selbstreview](CI2_D_VERIFICATION.md) binden
die tatsächlichen Prüfungen. Separates D-R01 bleibt vor Merge offen.

Die neue Historyroute umfasst insgesamt höchstens 20 semantische Benutzerkommandos,
höchstens sechs neue wirksame History-Transaktionen und genau zwei tatsächliche
Spielprozesse zum Schreiben und frischen Laden/Redo im selben isolierten
synthetischen Profil. Werkzeug-/Farbwahl, Blattwahl, Navigation, Undo/Redo und
reguläres Beenden zählen mit; ein zusammenhängender Down/Move/Up-Strich zählt
als ein Kommando. Passive Assertions und Prozessstarts zählen nicht. Versteckte
Setup-Bearbeitungen, Mengenauffüllung oder Wiederholungen je Region/Fenstergröße
sind ausgeschlossen. Die 500er-Route entfällt aus Standard, `history`, `runtime`,
`all`, `--integration` und gewöhnlichen manuellen Vollläufen; sie wird nicht
automatisch als Stressroute weitergeführt.

Atomarer Strich, exakte Vor-/Nachwerte, Undo/Redo und Redo-Verzweigung, History
ohne Navigationsmutation, Zustand/Ansicht/Undo-Merkmal nach echtem Neustart,
tatsächlicher Redo und fremde Slotbytes bleiben geschützt. Das unabhängige
Python-Orakel importiert keine produktive Historylogik; zwei billige Gegenproben
weisen manipulierte Zelländerung und unvollständige Spur ohne weitere
Spielprozesse ab. Producer, Trace, Zusammenfassung und Gate binden die kurze
Folge; 500 Aktionen, mehr als 500 geänderte Zellen, fünf 100er-Segmente und das
künstliche 560px-Board sind keine aktive Pflicht.

Abgeschlossene HZ-C-14/15-Vergleiche und 36 HC92-before-Bilder entfallen;
aktuelle Schrift-/Layoutzusagen bleiben geprüft. Animationen erhalten relevante
Anfangs-/Zwischen-/Endzustände und einen echten Bewegungsnachweis. Katalogmodi
und wiederholte Importe werden konsolidiert; eine verifizierte unveränderliche
Importbasis darf geteilt/kopiert werden, veränderliche Daten bleiben isoliert.
Lastmatrizen mit 256 Kategorien, 128 Zeichen oder 300 Einträgen werden nur gezielt
gewählt. Untersuchungsziel sind mindestens 50 % weniger routinemäßige Bildbelege
gegenüber 858 festen PNGs; erzeugte und gelieferte Mengen werden getrennt gemessen.
CI2 §6 ersetzt den pauschalen Verzicht auf Laufzeitziele: übliche Standard-CI
möglichst unter fünf Minuten, aufwendigere relevante Integration unter zehn.

Auswahl, Producer und Gate werden zusammen auf das begrenzte Inventar umgestellt.
Tatsächlich gewählte native Gruppen behalten vollständige Ergebnisse, echte
Originalbelege und Quell-/Run-/Versuchs-/Dateibindungen; fehlende oder übersprungene
Pflichtresultate scheitern weiterhin. Native Scopes begründen nach CI2-A keinen
impliziten Browserauftrag. Alte Logs sind die Baseline; die 500er- oder volle
Vergleichsmatrix wird dafür nicht erneut ausgeführt.

Die feste aktuelle Lieferung umfasst 423 PNGs: 152 catalog, 240 graphics,
22 completion, neun adapters (zuvor 858). Die Dateien werden tatsächlich nicht
mehr erzeugt, wenn ihr Fall entfällt; Layoutbelege bündeln zuvor überlappende
Ausschnitte. ZS2 liefert 42 statt 201 kontrollierter/Echtzeitframes; drei echte
Bewegungsframes je Variante behalten die zeit-/pixelbezogenen Gegenorakel.
HC92 liefert 36 aktuelle Bilder, HZ-C die gewählten 15/19-Grundlinien ohne
14/15-Galerie; KE liefert 27 aktuelle Bilder ohne Legacy-Zeichner.

Der feste Historyplan enthält 17 Kommandos und vier neue Transaktionen. Das
Gate liest alle sechs Originaldateien (Plan, Trace, beide Saves, Fremdslot-Hashes,
Summary) und rekonstruiert Zellen, vollständige History, Cursor und Ansicht.
Katalogkopien sind vor jeder Mutation bytegleich zur verifizierten Importbasis;
elf Projekte bleiben getrennt, nur regular/restart teilen ihr Testprofil.
Unter Linux überlappen catalog und graphics mit den übrigen seriellen Gruppen
auf eigenen Xvfb-Displays, nach Cachevorbereitung durch die erste serielle Gruppe.
Unter Windows bleiben native Fenster wegen Fokus vollständig seriell.

## Gebundener CI-C-Ausgangsstand

Alle folgenden Mengen, Prozessfolgen, Pflichtdateien und Abnahmeformulierungen
dokumentieren den bisherigen Lieferstand und seine Erweiterungen. Ihre
Quellenbindungen bleiben erhalten; sie erzwingen keine Fortführung der alten
Mengen unter CI2. Für aktuelle Producer, Inventar und Gate gelten die oben
beschriebenen D-Umfänge; tatsächlich ausgewählte fehlende Resultate scheitern.

Inventar vor Umstellung: `main@019b4dba98ef56c549ef5e7da10402dba0c9e93a`,
[Issue #249](https://github.com/venomenon328/picross/issues/249), CI-C/V1.
[CI-Policy](CI_POLICY.md) bestimmt Auswahl und Abnahme. Keine Produktänderung.

## Bisherige vollständige Zuordnung

| Gruppe | Erhaltene ausführbare Aussagen und Pflichtbelege |
| --- | --- |
| core | `run_tests.gd` einschließlich Save/Recovery, KAT-2-Status, goldener Atlas-/Geometriefälle; ZS2-Logik; echter Exit-23-Fehlerpfad; p13 write/read in zwei Prozessen; kontrollierter Start. Vollständige gebundene Phasenlogs. |
| history | Fünf Prozesse mit je 100 echten Aktionen, unabhängiges Python-Zell-/History-/Redo-Orakel, sechster Neustartprozess, Navigation und negative Kontrollen; `integration/summary.json`. |
| catalog | Zehn KAT-2-Modi regular/restart/large/empty/invalid/adapter/information/kb/kk/ke einschließlich aller inneren Pointer-, Slot-, Reset-, Fehler-, Last-, KE-Pixelassertions. Temporäre synthetische Adapterregistrierung gehört hierzu, nicht pauschal alle Piloten. Zehn Originalberichte, Zusammenfassung, 244 unverkleinerte Python-Crops plus 72 unveränderte, bereits nativ erzeugte KE-Bilder. |
| completion | Eigener EA-Import; native und restart mit gemeinsamem Profil, sofortiger Commit/Save, Bewegung/Abbruch, Geometrie und ursprungsgebundener Reset. Beide Berichte, alle End-/Rechteckbilder, fünf anhand echter Zeitstempel ausgewählte Phasenbilder und unveränderte native APNG-Zeitfolge. |
| adapters | Vier RP6-Fälle partial/finish/read, fremde Slotbytes und T04-Negativkontrolle nach echter T01-Schreibaktion; anschließend alle vier Pilotcaptures aus genau diesen Saves. ZA-1: vier synthetische Pakete, echte Registrierung, Save-/Recoveryguards, zehn Prozesse einschließlich seed/oldreset, Pixel-/Slotisolation, eigener Windows-Export und tatsächlicher PCK-Audit; Windows zusätzlich EXE-Start. Alle bisherigen Pilot-/ZA-1-Berichte und Pflichtbilder. |
| graphics | VS2 write/read, GF1, HF149 write/read/native, vollständige 96er-Matrix, V1-Fokus, V2 write/read, V3/Sidebar, HC92-, HS186-, HN192-Pixel-/Eingabenachweise; fünf kompakte Capturestufen, 17 Buchzustände, aktuelle ZS2-/ZS1-Bewegungsorakel. PERF-B echte Ressourcen/Cache/Alpha/Mutation/Invalidierung. Alle bisherigen ausgewählten Originalbilder und vollständigen komprimierten Geometrieberichte. |
| export | Regulären Inhaltsbestand ausschließlich für Export übernehmen/importieren; echter Windows-Debugexport, separate EXE/Konsolenhilfe/PCK, externer nativer PCK-Audit, vollständiges Spieler-ZIP und Verpackungsprüfung. Windows zusätzlich headless und GUI-EXE-Start. |

AT-A ergänzt den elften Katalogmodus `at`: drei Fenster-/UI-Kombinationen mit
kleinem transparentem Bild und echtem Hover, zwölf unveränderte native Bild-/
Papierausschnitte und `at.json`/`at-fixture.json`. Die Completion-Gruppe ergänzt
drei Kombinationen für Endbild, Wiederöffnung und Überblendung, dazu 18 native
Bild-/Papierausschnitte und die feste Fixturebindung. Das unabhängige Gate liest
die Originalpixel und vergleicht sie mit importiertem RGBA und tatsächlichem
Papierhintergrund. Bisherige Fälle und ihre Originalbelege bleiben Pflicht.
Der gesonderte echte Windows-Export-/Savewechsel und die Abschlussbindung
stehen in [AT-A-T01](AT_A_VERIFICATION.md).

Jede Gruppe behält die hashgeprüfte Toolchain, aktive Buch-/Atlasressourcenprüfung
und ihren eigenen isolierten Editorimport. Die genaue Pflichtdateimenge steht in
[native_artifacts.json](../tools/native_artifacts.json), ausschließlich Dateinamen
aus der aktiven technischen Matrix. Keine historischen Daten oder Korpusreplays.
EA-Phasenbilder werden weiterhin aus den tatsächlichen nativen Zeitstempeln abgeleitet.
Die vollständige Vereinigung erhält jede bisherige aktive Prüfaussage; Pilotcapture
ist jetzt auch bei allein gewählter Adaptergruppe Pflicht.

## Auswahl und Ausführung

`native_contract.py` ist die gemeinsame Quelle für Auswahl und Gate.
`picross-ci-selection-v4` ergänzt `native_groups` und `native_expected` mit exakter
Teilprüfungsmenge. Die sechs CI-A-Jobergebnisse und CI-B-Browserbelege bleiben Pflicht.
Der vollständige Base-/Head-Treevergleich, beide Rename-/Delete-Seiten, Inhalts-
Dateimodusschutz, Main-Abkürzung und konservative unbekannte Wirkung bleiben.

**CI-258 / #258:** Zwischen Docs-Producer und Scheduler/Gate ist `native_groups`
ein kanonischer kompakter JSON-Array-String (`[]` bei keiner Auswahl),
nicht mehr CSV beziehungsweise ein leerer Outputwert. Für den bestehenden
Product-Workflow wird die Liste bei Übergabe zu CSV dekodiert/verbunden;
die Entscheidung zum Spieler-/PCK-Download beruht auf Listenmitgliedschaft.
Format der Selection-/Result-Artefakte bleibt v4 mit echtem JSON-Array.
Fehlende beziehungsweise nichtkanonische Outputs werden auch bei
leerem Array abgewiesen; die Quell-/Run-/Retryprüfung bleibt unverändert.

| Geprüfte exakte Abhängigkeit | Native Gruppen |
| --- | --- |
| `tools/kat2_product.py`, `tools/native_images.py`, `game/tests/kat2_probe.gd` | catalog |
| `tools/ea_product.py`, `game/tests/ea_probe.gd` | completion |
| `tools/p14_integration.py`, `game/tests/p14_integration.gd` | history |
| `catalog_ink.gd`, `catalog_tip.gd` unter `game/ui/` | core, catalog, adapters, graphics, export; RP6-/ZA-1-Kartencaptures und kompakter Album-Capture verwenden die Darstellung |
| `catalog.gd`, `catalog_card.gd` unter `game/ui/` | core, catalog, completion, adapters, graphics, export; Karten öffnen, Reset, Pilot-/Adapter-Slotisolation und Album-Capture |
| `game/model/catalog_difficulty.gd` | alle sieben Gruppen; Anzeige über `catalog_card.gd` und gemeinsame Registryvalidierung über `content_registry.gd` |
| `game/ui/completion.gd` | core, catalog, completion, adapters, graphics, export; KAT-2/KE rendert die Abschlussansicht, RP6/ZA-1 prüfen echte Abschlüsse/Reveals |
| `tools/za1_product.py` | adapters, export; gemeinsamer PCK-Auditor |
| RP6-/ZA-1-Probes | adapters; `content_pack_probe.gd` zusätzlich export |
| Exakt benannte native Render-/Atlasprüfer und aktive Renderer im Vertrag | core, graphics, export |
| Gemeinsame UI (`main.gd`), Save/Session, Fixtures, unbekannte Namen, gemeinsame Harness-/Toolchainwirkung | alle sieben Gruppen |

Keine Präfixausnahme für neue Dateien. Mischdiffs vereinigen alle betroffenen
Gruppen. CI-A entscheidet weiterhin unabhängig über Browser, Fachtests, Preflight
und Zustellung; deren eigene Abhängigkeiten bleiben erhalten. Ein reiner nativer
Katalogharness benötigt keinen Browser-/SSH-Lauf. Runtime-Katalogänderungen behalten
ihre CI-B-Browsergruppen. Kern-/Exportpflichten folgen der tatsächlichen Wirkung.

Die UI-Zuordnung folgt den aktiven Aufrufern: `rp6_probe.gd` und `za1_probe.gd`
öffnen Karten über die Hauptszene, prüfen Slotisolation und verdiente Reveals;
`rp6_capture.gd` liefert auch Albumzustände. `capture.gd` rendert mit
`capture_compact_layout()` den Katalog und mit `capture_h1()` verdiente Albumzustände.
`ke_graphics.gd` wird vom KAT-2-Modus `ke` ausgeführt und prüft `Completion` direkt.
History bleibt bei den fünf UI-Modulen ungewählt: die 500er-Route wählt ihre Session
direkt und prüft Zell-/History-/Ansichtszustand, keine Karten-/Abschlussdarstellung.
Ink/Tip wählen auch nicht allein die EA-Gruppe. Das Difficulty-Modul ist dagegen
kein reiner Anzeigeleaf: `content_registry.gd.validate()` verwendet `Difficulty.valid()`
für jeden v3-Eintrag. Registryladung, Definitionen/Slots und der native PCK-Audit
betreffen deshalb auch History, Adapter, Grafik und Export. Die explizite Zuordnung
aller sieben Gruppen ist hier begründet; der unbekannte Fallback ist kein Pfadnachweis.
`test_ci_c.py` prüft die sechs realen Einzelpfade, den Difficulty-Import beider
direkten Verbraucher, Mischdiffs, sichere Nichtauswahlen und manuelle Erweiterung
über `ci_scope.classify()` einschließlich Schedulerflags und unveränderter Browserwahl.

`native-core`, `native-history`, `native-catalog`, `native-completion`,
`native-adapters`, `native-graphics`, `native-export` erweitern manuell um die
benannte Gruppe. `runtime` erhält core/history/catalog/completion/export plus
vollständige Browserprüfung. `visual`/`perf-b` verlangen core/graphics/export plus
Browser. `production`, `all` und `toolchain` erweitern auf alle nativen Gruppen;
Browser-/Zustellungs-/Preflightpflichten folgen weiterhin ihrer bisherigen Zuordnung.
Kein Scope kann automatisch erforderliche Gruppen entfernen.

Lokaler Standard ist die vollständige Vereinigung. `p1_product.py --groups catalog`
startet ausschließlich Katalog; analog für alle anderen Gruppen. Die alten lokalen
Flags bleiben kompatibel erweiternd: `--integration` bedeutet history/catalog/
completion, `--pilots` adapters, `--visual` oder `--perf-b` jeweils graphics;
core/export bleiben bei Verwendung dieser alten Flagfamilie erhalten.
CI verwendet ausschließlich die neue explizite Gruppenliste.

Jede Gruppe startet einen eigenen Pythonprozess mit neuem temporären Projekt,
eigenen APPDATA/LOCALAPPDATA- beziehungsweise XDG-Wurzeln und eigenem Ausgabe-
und Technikverzeichnis. Die absoluten temporären Grenzen werden im Bericht
festgehalten und im Gate auf getrennte Wurzeln geprüft. Nur hashgeprüfte
Downloadarchive werden geteilt; jeder Prozess prüft sie erneut und extrahiert
seine eigene Engine/Exportvorlage. Keine gemeinsamen importierten Projekte/Saves.
Der erste echte Gruppenlauf füllt gegebenenfalls den Downloadcache vor Parallelität.

Unter Linux überlappt graphics mit den übrigen seriellen Gruppen, jeweils mit
`xvfb-run -a` und eigenen Displays. Unter Windows laufen sämtliche Gruppen
seriell: keine konkurrierenden interaktiven Fenster während Katalog-/EA-Dialogen.
Der vorhandene innere Grafikworker bleibt ebenfalls projekt-/profilisoliert.
Fehler einer Gruppe verhindern nicht die Diagnose der übrigen Gruppen, verhindern
aber den Gesamterfolg. Laufende Phasenlogs liegen direkt im späteren Technikartefakt.

Die inneren Prozessfolgen bleiben: KAT-2 regular → restart mit gemeinsamem Save;
EA native → restart; fünf History-Schreibprozesse → unabhängiges Orakel → read;
RP6 partial → finish → read → Capture aus echten Saves. T04-Negativkontrolle
verändert nur eine Profilkopie über echte Zellaktion. ZA-1 seed/partial/finish/read/
oldreset/reset erhält seine gegenseitigen Slotbyteprüfungen. Der isolierte
serielle Editorimport mit Wiederherstellung der Projektbytes bleibt erhalten.

## Bilder, Messung und Gate

P2-C kopiert für EA die bereits importierten unveränderlichen Eingaben derselben
Gruppe in ein eigenes Projekt. Datei-/Byte-/SHA-Inventar vor/nach Kopie und nach
EA bindet die Isolation; ein neues Profil sowie der echte `ea-import` nach den
EA-Fixtureänderungen und beide Spielprozesse bleiben erhalten. Die Messwerte
stehen unter `ea.import_reuse`. Es werden keine Ergebnisse oder Saves übernommen.

Die bereits nativ zugeschnittenen KAT-2-Kompositionen können als RGB-PNG
gespeichert werden, wenn **jedes** Alpha-Byte exakt 255 ist. Godots tolerante
`detect_alpha()`-Erkennung reicht dafür nicht. Der unveränderte RGBA-Readback
bindet weiterhin den Python-Pixelvergleich und das Originaldatei-Gate; bei
jedem anderen Alpha-Wert bleibt RGBA erhalten. Pflichtbildmenge, Rechtecke,
Direktbilder und Fehlerbelege bleiben unverändert. Dies setzt die bereits
zulässige verlustfreie Byteänderung aus der CI-Policy um.

Katalogaufbereitung liest jeden der 56 tatsächlichen Kontextframes einmal, schneidet die
unveränderten nativen Rechtecke und schreibt PNGs mit `optimize=False`,
`compress_level=1`. Kein Resize, keine Palettenreduktion, keine neue Grafik.
`--compare-native-png` beziehungsweise der gleichnamige Dispatchschalter schreibt
zuerst den bisherigen `optimize=True`-Weg und danach den neuen Codec auf denselben
Crops. Jede Ausgabe wird wieder zu RGBA dekodiert und bytegenau verglichen,
einschließlich Alpha und Maßen. Vergleichskopien werden erst nach Gleichheit
entfernt. Kontextmaße/-SHA, Regionen und beide RGBA-Identitäten bleiben im Bericht.
Der Vergleich ist eine ausdrückliche Abnahmemessung, keine dauerhafte Altpfadpflicht.

`kat2/image-costs.json` wird ab Beginn und nach jedem Eingangsframe fortgeschrieben;
Fehler bleiben sichtbar. Er trennt Frame-I/O/Dekodierung, Zuschneiden, PNG-Encoding/
Schreiben, Quellbindung und Vergleich samt Eingangsframes, Crops und Dateibytes.
Wandzeit und CPU-Prozesszeit der Bildaufbereitung werden getrennt angegeben.
Native Rendering-/Interaktionsphasen stehen mit Start/Ende und Dauer in den
Prozessberichten; sie enthalten auch Assertions und funktionale Wartezeiten und
sind keine reine GPU-Zeit. EA misst Frame-I/O und APNG-Schreiben getrennt, behält
alle echten Zeitabstände und die bisherige RGB/APNG-Ausgabe unverändert.

Dateiselektion und Spieler-ZIP-Verpackung besitzen eigene Dauern. Der Runner
bindet tatsächliche gelieferte Technikdateizahl/-bytes; Upload-/Kompressionsdauer
und tatsächlich gespeicherte Actions-Artefaktbytes werden aus den betreffenden
Actions-Schritten und API-Metadaten ermittelt. Upload ist nicht Teil der nativen
Renderzeit. Referenz, Nachhermessung, Runner/Cache/Toolchain, Queue, Jobdauer,
summierte Runnerbelegung und überlappende Spanne werden im PR getrennt ausgewiesen.
Keine Zeit-/Bytegrenze, kein verkürzter funktionaler Timeout.

`native-result.json` bindet jede erwartete und tatsächliche Gruppe, Prozessausgänge,
Originalberichte, vollständige Teilprüfungsmenge, Quellen und Dateien. Das Inventar
verlangt die bisherigen Pflichtbilder auch dann, wenn ein Producer sie aus seiner
Selbstauskunft entfernt. Die fünf variablen EA-Phasenbilder werden aus den echten
Sequenzzeitstempeln unabhängig neu bestimmt. Originale Fehler-/Checkfelder und
KAT-/EA-Unterberichte müssen mit dem aggregierten Bericht übereinstimmen.
Die originale History-Zusammenfassung muss 500 Aktionen, Kategoriengesamtzahl,
verbleibenden Redo-Zweig, Zellhash, beide Negativkontrollen und Neustart ausweisen
und mit dem Gruppenbericht übereinstimmen.

`ci-required` lädt Technik und gegebenenfalls Spieler vom konkreten Product-
Producer-Versuch herunter und prüft tatsächliche Datei-/SHA-/Größenbindungen,
eindeutige Vollständigkeit, Gruppen-/Phasenstatus und EXE/PCK-Bytes im Spieler-ZIP.
Ein grüner Productjob allein reicht nicht. Fehlend, leer, doppelt, falsch,
fehlgeschlagen, abgebrochen, nicht gestartet oder ausgewählt+skipped scheitert.
Nicht ausgewählte Gruppen erscheinen ausdrücklich als nicht ausgeführt.

Head, Base, tatsächlicher Test-Merge, Event und Run müssen übereinstimmen;
Auswahlversuch ≤ Productversuch ≤ Gateversuch. Erfolgreiche Jobs dürfen nur
innerhalb desselben unveränderten Runs wiederverwendet werden. Artefaktnamen sind
`picross-p1-technical-<head>-<attempt>` (sieben Tage) und
`picross-p1-player-<head>-<attempt>` (vierzehn Tage). Kein Wildcarddownload alter
Resultate, keine Ergebnis-Caches. Technische Originalframes bleiben lokal, soweit
sie nicht zu den bisherigen Pflicht- oder konkreten Fehlerbildern gehören.

## Abnahme

HZ-A ergänzt den bestehenden `kk`-Modus um lokale Tidy-Hand-Zeichen-/Ellipsen-
und Layoutprüfungen, vollständige Größenangaben, 128 Zeichen lange Kategorien,
256 auswählbare Kategorien, Hilfe und native Dialoge. Die drei HZ-Fenster-/UI-
Kombinationen liefern zusätzlich 18 unveränderte native `hz-*.png`-Ausschnitte
beziehungsweise Kontextbilder; sie stehen im verpflichtenden Direktbildinventar.
Bestehende KAT-/KE-/AT-Prüfungen und ihre Bilder bleiben erhalten.

HZ-C erweitert denselben `kk`-Modus um stabile rollenbezogene Grundlinien,
unveränderte Anfangsglyphenpixel bei Wort-/Fallbackwechsel, feste Kategorie-
und Fußbereiche sowie den korrigierten Größenvergleich 14/15. Die 21 zusätzlichen
Originalausschnitte `hz-c-*.png` und die Messwerte in `hzc_measurements` gehören
zum selben verpflichtenden Direktbild-/Berichtsweg; Auswahl und bestehende
Pflichten bleiben unverändert. [HZ-C-Prüfzuordnung](HZ_C_VERIFICATION.md).

CI-C-T01 bindet technische Ergebnisse, Messungen, finalen Head/Base/Test-Merge/Run
und getrennten vollständigen Selbstreview im Draft-PR. CI-C-R01 bleibt ein separater
qualifizierter Review vor Merge. Bestehende Windows-/Eigentümergates bleiben separat.
