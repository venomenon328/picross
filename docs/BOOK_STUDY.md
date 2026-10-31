# Buchstudie B-A · B-A-N02-T01

Stand: 31.10.2026 · isolierte Nacharbeit zu
[#493 / B-A-E02, N06–N10](https://github.com/venomenon328/picross/issues/493),
[Umsetzungsvorbereitung B-A-V03](https://github.com/venomenon328/picross/pull/495#issuecomment-6541551895)
und [B-A-R02-B01](https://github.com/venomenon328/picross/pull/495#pullrequestreview-5721985216).
Ausgangshead: `6677d3e339701be9aa3cfa9f9a55f7ff78990d86`;
Basis: `864c4e6289df15ea7b3522b850542ece3489160f`.
Branch `feat/493-book-study`, bestehender Draft-PR #495 gegen `main`.
Aktueller Lieferhead, CI, Originalbelege und getrenntes Selbstreview werden im PR
gebunden. Dieses Dokument beschreibt den ausführbaren Prüfvertrag. B-B bleibt
unimplementiert, #493 offen; dieser Auftrag erlaubt keinen Merge.

## Doppelseite und Arbeitskapazität

Der ruhende Katalog liegt auf zwei vollständigen Papierseiten mit mittiger Bindung.
Die reguläre Kataloglogik behält Filter, globale Sortierung, Metadaten, Blattnummern,
ID-Aktionen, Miniaturen und Reset. Höchstens 24 aktive Karten verteilen sich auf
beide Hälften; 27 synthetische Instanzen liefern eine volle und eine teilweise
belegte Doppelseite. Die zweite Seite zeigt zwei Karten links und eine rechts.
Beide Hälften teilen den Scrollkontext. Bei knapper Breite sinkt die Spaltenzahl;
Schrift, Kartengrößen und Trefferflächen werden nicht verkleinert.

Ein echter Weiterbefehl blättert rechts nach links, Zurück links nach rechts,
jeweils **0,85 s**. Randbefehle und unveränderte Ziele bewegen nichts. Filter und
Sortierung wirken sofort auf den Gesamtbestand vor der Seitenauswahl.

Neu oder begonnen öffnet mit **drei getrennten Blättern und insgesamt 3,0 s**
Bewegung nach links. Die Kamera fährt im zweiten Teil auf die rechte Arbeitsseite
mit Bindung links. Zusätzliche Blätter bleiben neutral. Schrift wird nie gespiegelt.
Die Arbeitskamera zeigt jetzt zusätzlich die obere Buchkante samt Deckel und
Seitenblock. Breitere Deckel bleiben seitlich sichtbar. Die untere Kante liegt
weiterhin außerhalb des Arbeitsausschnitts; der Katalog zeigt das ganze Buch.

Boardfläche, Rasterfit, gewünschte Zellgröße, Hinweisfont, Slots, Reserven,
Miniatur, Originalpalette und die drei SL-Rahmen behalten ihre regulären Budgets.
Kleine Rätsel werden nicht künstlich vergrößert. Titel, Katalogreiter und obere
Navigation orientieren sich an der projizierten Papierkante. Im Katalog bestimmen
Papierkante und Falzwölbung Außenabstand, Fußzeile und Seitenabstand. Die Hüllen
der tatsächlich gerenderten Glyphen und Konturen müssen in allen drei gebundenen
Konfigurationen mindestens **acht Pixel** innerhalb des flachen Papierbereichs
liegen. Diese Aussage ersetzt kein Raster-/Hinweisbudget durch kleinere Controls.

Gelöst öffnet direkt die stabile Endansicht. Deren bestätigter Reset öffnet dasselbe
leere Blatt ohne Buchanimation. Die separate 2,15-s-Abschlussdarstellung bleibt.

## Material, Wölbung und Controls

Die bestehende A-Quelle `art/book/bp2-a-inventarband.png` bleibt bytegleich:
SHA-256 `957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a`.
Die Einbandshader verwenden deren UI-freie Leder-/Bindungsbereiche. Meshes trennen
Papier, Deckel, Seitenlagen, Bindung und sparsamen Untergrund.

Die Innenflächen verwenden die originale neue Bildtextur `study/book/paper.png`,
1254×1254, 2.564.246 Bytes, SHA-256
`1af9f61957619d7cea98b69021688b0b78997d84baf93698c9f02dcbb866362f`.
[Herkunft, vollständiger Prompt, Rechte und Import](../game/study/book/paper.json)
binden die unverändert kopierte imagegen-Ausgabe ohne Fremdvorlage. Verlustloser
Import, Mipmaps, lineare Filterung, kein Repeat; das Mischen mit 55 % hellem
Elfenbein hält Fasern und Alterung unter Hinweisen zurückhaltend. Katalogseite,
Seitenhälfte und Arbeits-ID bestimmen feste Ausschnitte. Vorder- und Rückseite
besitzen eigene Zuordnungen. Keine Spiegelung oder Zufallsvariation pro Frame;
dieselbe Seite behält nach Rückkehr ihre Papierpixel.

Die ruhende Wölbung ist reale Vertexgeometrie: 0,26 Welteinheiten hoch und nach
0,75 Einheiten vollständig flach. Sie verändert Normalen und die sichtbare obere/
untere Papierkontur. Eine schmale geometrische Lücke lässt die Bindung frei.
Das Licht folgt der Wölbung. Die UI-Sicherheitsfläche liegt außerhalb dieses
Streifens, die präzise Rasterfläche bleibt eben. Bewegte Inhalte folgen den
Blattvertices; kein nachträglich über die ganze UI gelegter Verzerrungseffekt.

Studienbuttons und geschlossene Dropdowns haben transparente Füllung. Normal,
Hover, Gedrückt, Auswahl, Deaktiviert und Fokus behalten unterscheidbare Konturen;
Auswahl erhält einen zusätzlichen Strich. Ein nativer Alphavergleich prüft die
nicht nur farblichen Unterschiede. Die native Standardbeschriftung wird im
Opt-in unterdrückt, damit der eigene Text genau einmal erscheint. Farbproben
behalten ihre Originalpixel; Popup-, Dialog- und Fehlerflächen bleiben deckend.
Die zwei gemeinsamen Controls haben einen expliziten, standardmäßig deaktivierten
Schalter. Die reguläre Produktdarstellung bleibt unverändert.

## Zustände, Rückkehr und Eingabebesitz

Ruhende Ansichten verwenden direkte Controls. Während der Bewegung liegt dieselbe
UI in einem transparenten SubViewport in tatsächlicher Fensterauflösung. Ein
Snapshot bindet den Quellzustand, die aktuelle UI den Zielzustand. Beim Blättern
trägt die Rückseite die andere Zielhälfte; bei der Öffnung bleibt sie neutral.
Premultiplizierte Alphakomposition erhält geglättete Text-/Rasterkanten.

Der tatsächliche Katalogreiter löst aus ruhender Arbeit oder stabiler Endansicht
eine **1,8-s-Rückkehr** mit Herauszoomen und drei Blättern von links nach rechts aus.
Der Snapshot enthält die aktuelle Bearbeitung. Vor dem bestehenden RAM-Flush wird
eine laufende Geste abgebrochen. Danach bleiben Filter, Sortierung, Richtung,
Seite, Scrollposition und Auswahl erhalten; die Miniatur zeigt den neuen Fortschritt.
`show_album()` selbst bleibt unmittelbar für Start, Reset, Information und interne
Stabilisierung. Idle-Escape navigiert nicht. Eine aktive Endanimation nimmt noch
keinen Rückkehrbefehl an.

`CATALOG/WORK → PREPARING → OPENING → CATALOG/WORK` bindet Quelle, Ziel und IDs
vor dem ersten Await. Generationen entwerten alte Fortsetzungen. Vorbereitung,
Bewegungszeit und Frameabstände werden getrennt gemessen.

| Unterbrechung in Vorbereitung oder Bewegung | Stabile Wirkung |
| --- | --- |
| Resize, UI-Skalierung, Fokusverlust | Gebundenes Ziel: Katalog oder ausgewählte rechte Arbeitsseite; gültig neu vermessen. |
| Escape oder ausdrücklicher Abbruch | Blättern/Öffnen: erhaltener Quellkatalog. Rückkehr: gebundener Zielkatalog, jeweils mit vollständigem Kontext. |
| Weitere Eingabe | Verwerfen, keine Warteschlange, kein Durchklicken oder späteres Nachholen. |
| Normales Ende | Gebundenes Ziel; gehaltene Tasten loslassen, danach frisches Down. |
| Beenden | Generation entwerten, Ressourcen lösen, Prozess beenden. |

Die UI einschließlich globaler Board-Eingabe ist während Vorbereitung und Bewegung
deaktiviert. Gesten, Tooltips und Dropdowns werden vorher geschlossen. Radereignisse
sind keine gehaltenen Tasten. Die Eingabesperre erfasst nur ihre eigenen Ereignisse;
eine von Board konsumierte normale Release-Aktion darf keinen alten Down-Merker
hinterlassen. Zellen, History/Redo und Save-Aktionen ändern sich durch Präsentation
nicht. Bearbeitung und Sortierung bleiben im RAM; echte Profile bleiben unberührt.
Vor Abschluss erscheinen auf keiner Fläche verdiente Namen/Reveals, auch nicht
auf Rückseiten. Miniaturen zeigen eigene, auch falsche Einträge.

Reguläre Save-/Recovery-Integration und #485–#487 bleiben B-B. Informations-/Hilfswege
sind vorhandene unmittelbare UI; ihre vollständige Buchnavigation wird nicht vorgezogen.

## Gültige Instanzen und Nachweise

`inputs.gd` prüft die Registry mit dem unveränderten regulären Validator, bevor sie
den Cache erreicht. Jede der 27 IDs besitzt einen eigenen Schlüssel, Slot,
Definitionspfad und Revealpfad. 27 tatsächliche JSON-Dateien und 27 kleine eigene
SVG-Sentinels liegen unter `study/book/data` beziehungsweise `study/book/art`.
Der einzige Adapter ist der feste Studienpräfix vor den regulären relativen
`data/`-/`art/`-Pfaden. Jede Definition wird geladen, gegen ID/Pfadbindung und den
unveränderten Definitionsvalidator mit dessen vorhandener expliziter Study-Asset-
Allowlist geprüft. Auch `reveal.definition_id` gehört zur jeweiligen Instanz.
Der Generator wiederholt drei Formen; er erzeugt keine weiteren Puzzleformen.
Geprüfter Tree, Runtime und beide PCKs verwenden dieselben Dateien.

| Fenster / UI | Fall | Hauptprüfung |
| --- | --- | --- |
| 1280×720 / 125 % | T01, 20×20 Mono | Kleine Fläche, unverkleinerte Karten und Controls. |
| 1920×1080 / 100 % | T06, 50×50 Farbe | Lange Hinweise, Großfall, Material und Bewegung. |
| 2560×1440 / 125 % | T08, 40×30 Farbe | Rechteck, getrennte UI-/Rastergrößen, Übergabe. |

Native Prüfungen liefern Pointerrouten auf beiden Kataloghälften, Rand-/Leerfälle,
globale Sortierung, drei Einzelblätter, Popup-/Gestenabbruch, 24 Kombinationen aus
Wechselart/Phase/Unterbrechung, Ressourcenfreigabe, gehaltene Taste/frisches Down,
bearbeitete Rückkehr, direkte Endansicht und Reset. Ein kopiertes T34 auf der zweiten
Seite beweist die verdiente Revealzuordnung. Billige Gegenproben weisen doppelte
IDs/Schlüssel/Slots/Pfade sowie fremde Definitions-/Revealzuordnungen ab.

Drei Arbeitsübergaben und eine Rückkehrübergabe werden auf vollständigen nativen
Originalframes geprüft: höchstens vier Kanalstufen und 0,1 mittlere Kanalstufen
Differenz. Ein Pixel Versatz und eine Alphamutation müssen scheitern. Die Geometrie
bezieht sich auf das neue Layout, nicht auf alte absolute Titelpositionen.

`opening.avi` enthält echte Engineframes bei normaler 30-fps-Wiedergabe: Blättern
in beide Richtungen, volle Öffnung, echte Zellbearbeitung und Rückkehr. Der Film
endet im lebenden Katalog mit aktuellem Fortschritt. `movie.json` bindet Phasen,
Vorbereitung und Zeit-/Framefolgen. Ein ruhiger nativer Öffnungslauf misst ohne
Screenshotarbeit. Aufnahme-Wandzeit, Filmzeit und native Bewegungszeit bleiben
getrennt; daraus folgt keine Hardware-FPS-Garantie.

Die eigenen Sichtprüfungen vergleichen alte A-Ansicht, gebundene N01-Bilder und N02
in denselben drei Konfigurationen, mit nativen Details und zwei Papierseiten samt
Rückkehr. Iterationen, Korrekturen und Materialurteil stehen im PR. Das ersetzt
weder B-A-R03 noch die persönliche Kandidatenwahl. Alte Belege bleiben historisch.

## Ressourcen, Export, CI und Gates

Höchstens drei bewegte Blätter mit je 1105 Vertices/2048 Dreiecken, zwei ruhende
Papierflächen und feste Deckel-/Seitenlagen. Kein Katalogtexturcache. Ein UI-Renderziel
plus RGBA-Snapshot benötigt 7,03/15,82/28,13 MiB bei 720p/1080p/1440p; einschließlich
konservativ vier Depthbytes je Pixel 10,55/23,73/42,19 MiB. Einfrieren benötigt kurz
zusätzlich eine CPU-Bildkopie. A umfasst 14.745.600 RGBA-Bytes, das neue Papier
6.290.064, mit Mipmaps höchstens 8.386.752 Bytes (ca. 8 MiB). Tatsächliche Import-
und Paketgrößen werden gemessen. Font-/Zellatlanten, SL-Rahmen, Hauptframebuffer
und Treiberoverhead sind separat. Nach Ende/Abbruch sind Übergaberessourcen frei.

Godot Standard 4.7.2, GL Compatibility, Web ohne Threads oder Erweiterungen.
Tatsächliche separate Windows-/Webstudienpakete erhalten externe PCK-Prüfungen
auf Einstieg, Quellen, Textur und alle Instanzen. Beide regulären Pakete werden
ebenfalls exportiert und auf Ausschluss geprüft. Windows startet den exportierten
Player und prüft Öffnung, echte Zellbearbeitung und Rückkehr. Linux behauptet
keinen Windowsstart. Chromium ist nicht beauftragt; Webexport ist kein Browser-
Darstellungsnachweis. Kein Deployment oder Release.

`report.json` bindet Quellen, Commit/Basis/Checkout/Run/Attempt, Materialhashes,
Importkosten, Originaldateien, Phasen, Pixelprüfzeit und tatsächliche Mengen/Bytes.
Die Exportgruppe führt die Studie einmal aus. Der Ergebnisguard liest originale
Einzelassertions, die feste Szenariomenge, Geometrie, Bewegung, Unterbrechungen,
Film und Dateien. Fehlende, manipulierte oder fehlgeschlagene Ergebnisse scheitern.
Der vollständige Base-/Head-Diff bestimmt alle Pflichtjobs. `docs`, ausgewählte
Jobs und `ci-required` müssen am Lieferstand erfolgreich sein. CI2-Ziele werden
gemessen; es gibt keinen neuen Erfolgsverzicht oder allgemeinen CI-Umbau.
Laufbilder, Filme und Exporte bleiben in ignorierter Arbeitsablage beziehungsweise
befristeten Technikartefakten, keine neue permanente Bildgalerie.

B-A-N02-T01 verlangt aktuelle Technik-, Sicht-, Export- und CI-Nachweise sowie
getrenntes Selbstreview. **B-A-R03 bleibt ein separates qualifiziertes technisches
und visuelles Review vor Merge.** R01/R02 nehmen N02 nicht ab. **B-A-M01** bleibt
persönliche Kandidatenwahl vor vollständigem B-A-Abschluss und vor B-B; sie darf
nach einem separat freigegebenen isolierten Merge auf main erfolgen. Der aktuelle
Auftrag enthält keine Mergefreigabe und lässt den PR als Draft.

Start und Reproduktion: [Studienanleitung](../game/study/book/README.md).
