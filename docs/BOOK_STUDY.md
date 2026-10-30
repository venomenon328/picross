# Buchstudie B-A · B-A-T01

Stand: 30.10.2026 · isolierte Studie zu
[#493 / B-A-V01](https://github.com/venomenon328/picross/issues/493).
Erneut geprüfte Basis: `864c4e6289df15ea7b3522b850542ece3489160f`.
Branch `feat/493-book-study`, Ziel `main`. B-B bleibt unimplementiert.
Der Draft-PR bindet technische Nachweise, aktuellen CI-Stand und den getrennten
Selbstreview an Head, Basis und tatsächlichen Test-Merge. Kein Mergeauftrag.

## Gewählter Kandidat und technische Verbindung

Dunkler matter Inventarband, warme helle Papierfläche, geschichteter Seitenblock,
seitliche Bindung und ein kleiner sichtbarer Holzuntergrund. Meshes und Materialien
sind eigene deterministische prozedurale Quellen. Die gezeichneten Inhalte stammen
aus der tatsächlichen regulären Katalog-/Arbeits-UI: Tidy Hand, Bakso, Delight,
HZ-Controls, Zellrenderer, Originalpalette und die drei SL-Rahmen bleiben erhalten.
Die persönliche Auswahl dieser konkreten Fassung bleibt B-A-M01.

Ruhende Ansichten sind frontal. Nach Auswahl tritt die orthogonale Kamera um
höchstens 17 % zurück und neigt sich kurz. Das Blatt wendet sich mit elastischer
Krümmung um die rechte Bindung; danach endet die Kamera wieder exakt frontal.
Die gesamte Bewegung dauert **3 Sekunden**. Vorbereitung ist separat; native
Bewegung folgt einer monotonen realen Uhr, der Enginefilm der festen Movie-Zeit.

Die vorhandene UI wechselt vorübergehend in einen transparenten 1:1-SubViewport.
Ein eingefrorenes Katalogbild folgt dem Blatt, dahinter liegt die gewählte
Arbeits-UI als Viewporttextur. Die Unterseite bleibt neutrales Papier. Danach
wechselt dieselbe UI ohne Layoutänderung zur direkten Eingabe im Hauptviewport.
Texturverweise und Renderziel werden freigegeben; die leere gegenüberliegende
Blattseite bleibt in ihrer endgültigen Lage außerhalb der Arbeitsfläche.

Premultiplizierte Alphakomposition verhindert dunkle AA-Säume. UVs entsprechen
der ganzen bisherigen Fensterfläche einschließlich des Buchreiters. Keine
kleinere Schrift oder Fitfläche als Ausgleich. Ein dauerhaft texturierter
Viewport würde zusätzlich eine Eingabeabbildung und ein dauerhaftes Renderziel
benötigen; ausgewählt ist deshalb die direkte ruhende UI. Kein zweiter
Produktionsrenderer und keine Aktivierung im normalen Spiel.

## Endlicher Zustandsvertrag

`CATALOG → PREPARING → OPENING → WORK`; Rückkehr wieder zu `CATALOG`.
Die Ziel-ID wird vor dem ersten Await gebunden. Unterbrechungen erhöhen die
Generation; alte Fortsetzungen prüfen sie vor jeder weiteren Wirkung.

| Ereignis in Vorbereitung/Bewegung | Stabiler Endzustand und Wirkung |
| --- | --- |
| Weitere Auswahl, Klick, Rad oder Tastatur | Verwerfen, keine Warteschlange, kein Durchklicken oder nachgeholter Befehl. |
| Resize | Gewählte Arbeitsseite, neu vermessen und frontal; alte Generation wirkungslos. |
| UI-Skalierung | Gewählte Arbeitsseite mit neuem Maßstab und bisheriger Fitberechnung. |
| Fokusverlust | Gewählte Arbeitsseite, frontal; keine Wiederholung bei Fokusgewinn. |
| Escape/Katalogrückkehr | Erhaltener Katalogkontext, keine spätere Rückkehr ins Rätsel. |
| Beenden | Präsentation abbrechen, Prozessende ohne ausstehende Navigation. |
| Reguläres Ende | Gewählte Arbeitsseite; gehaltene Tasten zuerst loslassen, danach frisches Ereignis. |

Die ganze UI-Unterstruktur bleibt während PREPARING und OPENING deaktiviert,
einschließlich globaler Board-Eingabe. Bestehende Zell-/Hinweisgesten, Tooltips
und BookChoice-Popups werden vorher über die vorhandene Abbruchstrecke beendet.
Rad gilt nicht als gehaltene Taste. Die abschließende Freigabe wird konsumiert.
Keine Besuchshistorie und keine Präsentationsdaten im Save. Die Studie hält
Bearbeitung und Sortierung ausschließlich im RAM und öffnet keine echten Saves.

**B-B-Anschlüsse:** Abbruch → Pflicht-Flush/Recovery → ID-Wechsel → Präsentation
erhalten. Flushfehler belässt die sichere vorherige Ansicht mit Retry. Herkunft
unterscheiden: neu/begonnen, direkt gelöst, Reset, Info-Rückkehr, kurzer
Katalogseitenwechsel und unmittelbarer Filter-/Sortierwechsel. Die separate
2,15-s-Enthüllung bleibt erhalten. #485–#487 erneut gegen den tatsächlichen Stand
prüfen. Diese vollständige Navigations-/Save-/Recoveryintegration gehört nicht B-A.

## Nachweise und begrenzte Matrix

Die vorhandenen Konfigurationen aus `game/tests/current_visual_cases.gd` werden
einmal verteilt, ohne zusätzliche Kreuzmatrix oder echte Produktionsrätsel:

| Konfiguration | Synthetischer Fall | Schwerpunkt |
| --- | --- | --- |
| 1280×720/UI125 | T01, 20×20 Mono | Enge Fläche, unvergrößerter Zoomwunsch, vollständige Controls. |
| 1920×1080/UI100 | T06, 50×50 Farbe | Großfall, lange Hinweise, vier Originalfarben, Fit und Schärfe. |
| 2560×1440/UI125 | T08, 40×30 Farbe | Rechteck, größere Fläche, getrennte UI-/Rastergröße. |

Je Fall vergleicht eine separate bisherige Haupt-UI Board-/Rasterhülle, Zellgröße,
Fitgrenze, Schriftgrad, Slots, Hinweisplätze, belegte Fläche, Miniatur, Palette,
Werkzeuge und Titel. Direkte Baselinebilder ergänzen die numerischen Vergleiche.
Originale Textur-/Direktpaare prüfen die gesamte Übergabe: höchstens vier
Kanalstufen und 0,1 mittlere Kanalstufen Differenz. Gegenproben müssen eine
Verschiebung um einen Pixel und eine Alphamutation abweisen.
Bestehende Hinweise auf kleine/eng stehende Zahlen bleiben auch beim T06-Großfall
sichtbar. Gleiche Geometrie ist kein neues Komfortzertifikat für diese Hinweislast.

Echte Viewport-Pointerereignisse prüfen Auswahl, blockierte Klicks, Geste und
frischen Neubeginn. Hinzu kommen unveränderte Zellen/History/Redo, keine zusätzliche
Speicheraktion, Mehrfachauslösung, Abbruch während Vorbereitung und Bewegung,
Popupschließung, Rad und Ressourcenfreigabe. Magenta-Reveal und geheimer Name sind
synthetische Spoilersentinels; Katalog, bewegte Vorder-/Unterseite und Endansichten
bleiben ohne diese Daten. Begonnene Miniaturen zeigen auch eigene falsche Füllungen.

Der Film besteht aus tatsächlichen Engineframes bei normaler 30-fps-Wiedergabe,
ohne Interpolation. Movie-Aufnahmezeit, feste Filmzeit und unbeschleunigte native
Bewegung bleiben getrennt. Ein zusätzlicher ruhiger Durchgang misst Frameabstände
ohne Screenshot-/PNG-Arbeit; der erste protokolliert diese Eingriffe gesondert.
Keine daraus abgeleitete Hardware-FPS- oder Eingabelatenzgarantie.

## Ressourcen, Exporte und Plattformgrenzen

Höchstens ein temporäres UI-Renderziel plus eine RGBA8-Katalogtextur in Fenstergröße,
zusammen 8 Bytes je Pixel: bei 720p/1080p/1440p **7,03/15,82/28,13 MiB**.
Mit konservativ weiteren 4 Bytes je Pixel für Depth: **10,55/23,73/42,19 MiB**.
Beim Einfrieren vorübergehend zusätzlich eine CPU-Bildkopie von bis zu 4 Bytes je
Pixel. Driver, Hauptframebuffer, Fontatlanten und gemeinsame Ressourcen bleiben
außerhalb dieser Abschätzung; die vorhandenen 48.906.240 dekodierten Atlasbytes
werden nicht ersetzt. `resource_report()` liefert die aktuellen Ziel-/Texturzahlen.
Nach jedem Ende/Abbruch sind beide Studienressourcen freigegeben.

Godot Standard 4.7.2 und `gl_compatibility` bleiben gebunden. Web ohne Threads,
Erweiterungen, Compute-/Forward+-Funktionen oder neue Bibliotheken. Echte getrennte
Windows-/Webstudienexporte samt externen PCK-Proben prüfen Einstieg, ausführbare
Abhängigkeiten, synthetische Inputs und fehlende Produktionsinhalte. Zusätzlich
werden die unveränderten regulären Windows-/Webpresets wirklich exportiert und
beide PCKs auf Abwesenheit der Studie geprüft. `study/*` bleibt regulär ausgeschlossen;
nur die temporäre Studienkopie erhält eigene Presets mit expliziten Ausschlüssen.

Nativer Windowslauf und Start/Bewegung des Windowsstudienexports sind getrennte
Belege. Linux exportiert und prüft dessen Paket, startet aber kein Windowsprogramm.
Webexport und statischer Featureabgleich sind **kein Browserdarstellungs- oder
Eingabenachweis**. Chromium ist nicht beauftragt und wird nicht gestartet. Diese
echte Browserprobe bleibt für B-B offen; bekannte Inkompatibilität wäre ein Befund,
keine bloße Nachweislücke.

Quellen, deterministische Erzeugung und Rechte: [Startanleitung](../game/study/book/README.md).
`report.json` bindet Commit, Basis, Checkout, CI-Run/Attempt, Quellen-/Artefakthashes,
Umgebung, Phasenzeiten und Paketgrößen. Rohframes, Film, Logs und Exporte liegen
nur in ignorierter Arbeitsablage beziehungsweise im sieben Tage aufbewahrten
technischen CI-Artefakt. Keine dauerhafte Bildgalerie.

Der tatsächliche Diff mit neuem Studien- und gemeinsamem Produktharness wählt konservativ alle nativen
und Nichtbrowserbereiche. Der Studiennachweis ist ein Schritt im vorhandenen
Productjob bei Grafik-/Exportauswahl; kein neuer CI-Job, keine unterdrückten Tests.
`docs`, `ci-required` und sämtliche ausgewählten Jobs benötigen Erfolg am finalen
Head/Test-Merge. Zusätzliche Exportkosten bleiben Messwerte; CI2-Ziele werden
nicht ohne passende Messung als erreicht ausgegeben.

## Offene Gates

B-A-T01 verlangt technische Lieferung, tatsächliche Bewegung/Endansichten, Pakete,
aktuelle Pflicht-CI und getrennten Selbstreview. B-A-R01 bleibt ein separates
qualifiziertes technisches und visuelles Review des konkreten Heads vor Merge.
B-A-M01 wählt die konkrete Material-/Kamera-/Bewegungsfassung vor vollständigem
B-A-Abschluss und vor B-B; darf nach technischem isoliertem Merge auf main erfolgen
und ist hierfür kein Mergeblocker. Mergefreigabe bleibt separat, Gesamtissue offen.
