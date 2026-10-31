# Buchstudie B-A · B-A-N01-T01

Stand: 31.10.2026 · isolierte Nacharbeit zu
[#493 / B-A-E01 und N01–N05](https://github.com/venomenon328/picross/issues/493),
[Umsetzungsvorbereitung B-A-V02](https://github.com/venomenon328/picross/pull/495#issuecomment-6536305108).
Ausgangshead: `70ffcb8150f38113290ef34bda7299ce1e5c0dda`;
Basis: `864c4e6289df15ea7b3522b850542ece3489160f`.
Branch `feat/493-book-study`, bestehender Draft-PR #495 gegen `main`.
B-B bleibt unimplementiert. Aktueller Head, CI, Originalbelege und getrenntes
Selbstreview werden im PR gebunden; dieses Dokument ist der ausführbare Prüfvertrag.

## Doppelseite und Katalog

Der ruhende Katalog liegt auf zwei vollständigen Papierseiten mit mittiger Bindung.
Die Kamera steht weiter zurück als bei der Rätselarbeit. Links und rechts stehen
die unveränderten regulären Karten, Metadaten, Miniaturen und Resetaktionen.
Die studieneigene Unterklasse verteilt die von der regulären Kataloglogik erzeugten
Karten; sie ersetzt weder Filterung, Sortierung, Blattnummern noch ID-Aktionen.

Eine logische Seite enthält höchstens 24 aktive Karten, auf beide Hälften verteilt.
Filter und Sortierung wirken auf den Gesamtbestand vor der Seitenauswahl.
27 feste synthetische IDs aus nur drei Formen liefern eine volle und eine letzte
unvollständige Doppelseite. Die zweite Seite zeigt zwei Karten links und eine rechts.
Die Schrift und die Controls werden in tatsächlichen Fensterpixeln angeordnet,
nicht durch eine verkleinerte UI-Textur eingepasst. Bei knapper Breite sinkt die
Spaltenzahl; die Karten bleiben scrollbar. Beide Hälften teilen den Scrollkontext.
Die obere Zeile verteilt Kategorie und Sortierung auf die Seiten; Einstellungen,
Beenden und Blättern bleiben ohne Überlagerung des Falzes erreichbar.

Ein echter Weiterbefehl blättert rechts nach links, Zurück links nach rechts.
Beide dauern **0,85 Sekunden**, ohne zusätzliche Kamerafahrt. Am Rand und bei
unverändertem Ziel entsteht keine Bewegung. Filter und Sortierung wirken unmittelbar.
Eine laufende Bewegung verwirft weitere Filter-, Sortier-, Blatt- und Öffnungsbefehle.

## Öffnung und Arbeitskapazität

Neu oder begonnen öffnet mit **drei getrennten Blättern** und insgesamt
**3,0 Sekunden** Bewegung. Die Blätter beginnen zeitversetzt, haben eigene
Winkel und Krümmung und bewegen sich rechts nach links. Zusätzliche Blätter
bleiben neutral. Die Kamera fährt während des zweiten Bewegungsteils auf die
rechte Arbeitsseite und endet frontal und ruhig: die Bindung liegt links.

Die physische Seite ist höher als der nahe Arbeitsausschnitt. Dadurch bleiben
im Katalog beide ganzen Seiten sichtbar und bei der Arbeit die vollständigen
bisherigen Pixelbudgets erhalten. Obere und untere Buchkante liegen in der
Nahansicht außerhalb des Ausschnitts; Papier, linke Bindung und rechter
Einband-/Seitenrand bleiben sichtbar. UI-Inhalte werden niemals gespiegelt.

Boardfläche, Rasterfit, gewünschte Zellgröße, Hinweisfont, Slots, Reserven,
Miniatur, Originalpalette und sechs SL-Werkzeuge stammen aus der regulären UI.
Nur Katalogreiter und Platzwarnung werden innerhalb der rechten Papierfläche
positioniert. Ein gelöstes Blatt öffnet direkt seine Endansicht. Der bestätigte
Reset aus dieser Ansicht öffnet dasselbe leere Blatt ohne Buchanimation.
Die vorhandene separate 2,15-s-Abschlussdarstellung bleibt unverändert.

## Materialien und Vergleich

Materialquelle ist das unveränderte bisherige A-Buch
`game/art/book/bp2-a-inventarband.png`, SHA-256
`957c2eab39b2334825fb159287b9d36a17b77fff1c628ea88110f2cfb5f7a71a`.
Die Shader lesen dessen UI-freie Papier- und Einbandbereiche. Es entsteht kein
neues Fremdasset und keine umgeschriebene Bildfreigabe. Eigene Meshes trennen
Papier, Lederdeckel, Seitenlagen, Bindung und sparsamen Untergrund.
Gerichtete Blattabdunklung, Falz- und Kontaktschatten ergänzen die vorhandene
Papierstruktur und die abgenutzten Einbandkanten.

Der native Nachweis liefert die alte reguläre Ansicht und die neue rechte
Arbeitsansicht jeweils bei denselben drei Fenster-/UI-Konfigurationen, zusätzlich
unverkleinerte Bindungsdetails. Der direkte Vergleich betrifft Papierzeichnung,
Kanten, Einband, Bindung, Seitenblock und Licht. Die alte linke Arbeitsseite mit
rechter Bindung und ganzem Buchrand ist keine positionsgleiche Sollmaske für
die neue rechte Nahansicht. **Materialqualität wird visuell beurteilt**;
Pixelgleichheit gilt ausschließlich für die identische neue Textur-/Direktübergabe.

Die Implementierung wird an tatsächlichen nativen Bildern iteriert. Der PR nennt
die gesichteten Fassungen, konkrete Korrekturen und das eigene Materialurteil.
Das ersetzt weder die visuelle Prüfung in B-A-N01-R02 noch die persönliche
Kandidatenwahl B-A-M01. Historische Erstlieferung und B-A-R01 bleiben ausschließlich
an ihren damaligen Head gebunden.

## Texturübergabe und Eingabebesitz

Ruhende Ansichten verwenden direkte Controls. Nur während der Bewegung liegt
dieselbe UI in einem transparenten SubViewport mit tatsächlicher Fensterauflösung.
Ein eingefrorener Quellkatalog folgt dem bewegten Blatt; die aktuelle Ziel-UI
liegt auf der Zielseite. Beim Katalogblättern trägt die Blattrückseite die
gebundene andere Zielhälfte, bei der Rätselöffnung bleibt sie neutral.
Die UV-Abbildung folgt der jeweiligen Seite und spiegelt keine Schrift.

Am Ende verschwinden bewegte Blätter und Texturverweise vor der direkten
Eingabeübergabe. Premultiplizierte Alphakomposition erhält geglättete Text- und
Rasterkanten. Derselbe Endzustand wird als Textur und als direkte UI nativ
aufgenommen und unabhängig auf Originalpixeln verglichen:
höchstens vier Kanalstufen und 0,1 mittlere Kanalstufen Differenz.
Ein Pixel Versatz und eine Alphamutation müssen als Gegenproben scheitern.

`CATALOG → PREPARING → OPENING → CATALOG/WORK` bindet Ziel, Quelle,
Scrollkontext und Öffnungs-ID vor dem ersten Await. Generationen entwerten
veraltete Fortsetzungen. Vorbereitung und Bewegungsdauer werden getrennt gemessen.

| Unterbrechung in Vorbereitung oder Bewegung | Stabile Wirkung |
| --- | --- |
| Resize, UI-Skalierung, Fokusverlust | Gebundene Ziel-Doppelseite beziehungsweise gewählte rechte Arbeitsseite; gültig neu vermessen. |
| Escape oder ausdrückliche Rückkehr | Erhaltener Quellkatalog mit Seite, Scrollposition, Sortierung, Filter und Auswahl. |
| Weitere Eingabe | Verwerfen; keine Warteschlange, kein Durchklicken und kein späteres Nachholen. |
| Normales Ende | Gebundenes Ziel; gehaltene Tasten loslassen, danach frisches Down. |
| Beenden | Generation ungültig machen, Ressourcen lösen, Prozess beenden. |

Die UI-Unterstruktur einschließlich globaler Board-Eingabe ist während Vorbereitung
und Bewegung deaktiviert. Bestehende Zell-/Hinweisgesten, Tooltips und Dropdowns
werden vorher geschlossen. Radereignisse sind keine gehaltenen Tasten.
Zellen, History/Redo und Save-Aktionen ändern sich durch die Präsentation nicht.
Bearbeitung und Sortierung bleiben ausschließlich im RAM; reale Saves werden
weder gelesen noch geschrieben. Vor Abschluss erscheinen auf keiner Fläche
verdiente Namen oder Reveals; Miniaturen zeigen nur eigene, auch falsche Einträge.

Die komplette reguläre Navigation mit Pflicht-Flush, Recovery und den Anschlüssen
aus #485–#487 bleibt B-B. Informations-/Hilfswege in B-A sind vorhandene unmittelbare
UI; ihre vollständige Buchnavigation wird hier nicht vorgezogen.

## Aktuelle Nachweise

| Fenster / UI | Technischer Fall | Hauptprüfung |
| --- | --- | --- |
| 1280×720 / 125 % | T01, 20×20 Mono | Kleine Fläche, ungekürzte Kartenbudgets, vollständige Controls. |
| 1920×1080 / 100 % | T06, 50×50 Farbe | Lange Hinweise, Großfall, Materialdetails und Bewegungsbelege. |
| 2560×1440 / 125 % | T08, 40×30 Farbe | Rechteck, getrennte UI-/Rastergrößen, Texturübergabe. |

Keine neue Kreuzmatrix und keine Produktionsrätsel. `verify.gd` liefert
Kataloggeometrie, echte Pointerrouten auf beiden Hälften, Vorwärts/Rückwärts,
Teil-/Leerseiten, globale Reihenfolge, Rand-No-op, blockierte Eingaben,
drei getrennte Blätter, eigene fehlerhafte Miniaturen, Popup-/Gestenabbruch,
16 Kombinationen aus Wechselart, Phase und Unterbrechung, Ressourcenfreigabe,
frische Zellgeste sowie direkte Wiederöffnung und Reset.
Die bisherigen Arbeitskapazitäts- und Eingabeprüfungen bleiben erhalten.

`opening.avi` enthält echte Engineframes mit normaler 30-fps-Wiedergabe:
Vorwärts, Rückwärts und die volle Rätselöffnung, jeweils mit ruhenden Zuständen.
`movie.json` bindet Richtung, Dauer, Framefolge und Endzustand.
Der Film endet auf der lebenden stabilen Arbeitsansicht; kein freigeräumter
Schlussframe. Kompakte native Zwischenbilder ergänzen den Film.
Ein ruhiger nativer Durchgang misst Frameabstände ohne Screenshot-/PNG-Arbeit.
Movie-Aufnahmezeit, feste Filmzeit, Vorbereitung und tatsächliche native
Bewegungszeit bleiben getrennt; keine daraus abgeleitete Hardware-FPS-Garantie.

## Ressourcen, Exporte und CI

Maximal drei bewegte Blätter mit je 1105 Vertices/2048 Dreiecken, zwei ruhende
Papierflächen und feste Deckel-/Seitenlagen. Kein Katalogtexturcache.
Höchstens ein UI-Renderziel und ein RGBA8-Snapshot in Fenstergröße:
**7,03/15,82/28,13 MiB** bei 720p/1080p/1440p.
Mit konservativ zusätzlichen vier Depthbytes pro Pixel:
**10,55/23,73/42,19 MiB**. Beim Einfrieren kommt vorübergehend eine CPU-Bildkopie
von vier Bytes je Pixel hinzu. Die schon vorhandene Materialquelle umfasst
14.745.600 dekodierte RGBA-Bytes. Font-/Zellatlanten, SL-Rahmen, Hauptframebuffer
und Treiberoverhead sind separat. Nach Ende und Abbruch sind Renderziel, Snapshot
und bewegte Flächen inaktiv beziehungsweise freigegeben.

Godot Standard 4.7.2, GL Compatibility, Web ohne Threads oder Erweiterungen.
Der Harness erzeugt tatsächliche getrennte Windows-/Webstudienpakete und prüft
ihre PCKs extern, einschließlich Einstieg, Skripten, Materialien und synthetischen
Inputs. Beide regulären Windows-/Webpakete werden ebenfalls wirklich exportiert
und auf Ausschluss der Studie geprüft. Windows startet zusätzlich den exportierten
Studienplayer und führt dessen Bewegung aus; Linux behauptet keinen Windowsstart.

Webexport ist kein Browserdarstellungs- oder Eingabenachweis. Chromium ist nicht
beauftragt und wird nicht gestartet. B-B muss den passenden Browsernachweis liefern.
Es gibt kein Deployment, Release oder Zugriff auf echte Spielprofile.

`report.json` bindet Commit, Basis, Checkout, Run/Attempt, Quellen, Materialhash,
Originaldateien, Phasen, Pixelprüfzeit und tatsächliche Dateimengen/-bytes.
Der vorhandene Productjob führt die Studie einmal in der Exportgruppe aus.
Der native Ergebnisguard liest originale Einzelassertions, die feste Szenariomenge,
Geometrie-, Bewegungs- und Unterbrechungsberichte, Film und Pflichtdateien.
Die alte feste Zahl 96 ist kein Ersatz für den erweiterten Vertrag.
Fehlende, manipulierte oder fehlgeschlagene Resultate scheitern.

Der vollständige Base-/Head-Diff bestimmt alle Pflichtjobs. Kein neuer CI-Job
und keine Testunterdrückung. `docs`, ausgewählte Gruppen und `ci-required`
müssen am finalen Stand erfolgreich sein. CI2-Laufzeitziele werden anhand
tatsächlicher Messwerte beurteilt. Laufbilder, Filme, Exporte und Iterationen
bleiben in ignorierter Arbeitsablage beziehungsweise im befristeten Technikartefakt.
Quellen, Rechte und Startbefehle: [Studienanleitung](../game/study/book/README.md).

## Getrennte Gates

B-A-N01-T01: Implementierer liefert aktuelle Technik-, Material-, Bewegungs-,
Export- und CI-Nachweise sowie getrenntes vollständiges Selbstreview.
B-A-N01-R02: neues qualifiziertes technisches und visuelles Review des revidierten
Heads vor Merge. Das frühere B-A-R01 nimmt N01 nicht ab.
B-A-M01: persönliche Kandidatenwahl vor vollständigem B-A-Abschluss und vor B-B;
darf nach technischem isoliertem Merge auf main erfolgen und ist dafür kein
zusätzliches Mergegate. Mergefreigabe bleibt separat. #493 bleibt offen.
