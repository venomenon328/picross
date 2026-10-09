# Aktuelle CI-Policy

Stand: 09.10.2026 · Version 1.1 · Auftrag [#63](https://github.com/venomenon328/picross/issues/63)

## Geltung und Ablösung

Der Eigentümer hat nach der Analyse vom 09.10.2026 die CI-Bereinigung und diesen
Prüfumfang zur Umsetzung freigegeben. Diese Policy ersetzt für neue Änderungen
die früheren pauschalen Pflichten, sämtliche sechs Jobs, historische Studien,
Vorherprojekte und vollständige Reviewgalerien bei jedem PR neu zu produzieren.
Sie gilt auch dort, wo Projektprofil, ältere Paketbeschreibungen oder historische
Prüfberichte noch den damaligen Vollumfang nennen. Fachliche Produktverträge,
gezielte aktuelle Abnahmen und die Zuordnung zum tatsächlichen Quell-/Basisstand
bleiben verbindlich. Historische Berichte behalten ihr damaliges Urteil.

Der Abschlussstatus für Pull Requests heißt `ci-required` im Workflow
[CI verification](../.github/workflows/setup.yml). Er verlangt tatsächlichen
Erfolg aller ausgewählten Bereiche. Fehler, Abbruch, fehlende Auswahl und
übersprungene erforderliche Jobs sind kein Pass. Nichtzutreffen wird mit
Änderungsauswahl und Grund ausgewiesen. Es wurde kein Branchschutz verändert.

## Auswahl nach vollständigem Änderungsumfang

[ci_scope.py](../tools/ci_scope.py) vergleicht die exakten Base-/Head-Dateibäume.
Umbenennungen zählen als alter und neuer Pfad; Löschungen werden mit erfasst.
Die beiden Commitobjekte werden gezielt flach geladen. Bei divergierter Basis
können zusätzliche Prüfungen ausgewählt werden; Basisänderungen werden dadurch
nicht versehentlich übersehen. Der tatsächliche Checkout bleibt der Test-Merge.
Auswahlbericht und Logs nennen Head, Basis, Checkout, Run und ausgewählte Pfade.

| Änderung | Automatischer Pflichtumfang im PR |
| --- | --- |
| Reine normative Dokumentation/Anleitung | Schnelle Tooltests, Dokumentvalidator, vollständiger Diffcheck |
| Spielzustand, Eingabe, Save, History, Navigation | Aktuelle Kernregression, echte Prozess-Roundtrips, 500er-Route, aktuelle Pixelprüfungen und Spielerexport |
| Reine Stiftzeichnung/Capture oder aktive Buchassets | Aktuelle Kernregression, kompakte native Pixelprüfungen und Spielerexport |
| Rätseldaten, Pilotassets/-probes, Produktion, Proofs und Quellenkorpora | Fachtests und vollständige relevante Replays, alle sechs Piloten, aktuelle Pixelprüfungen und Spielerexport |
| CI/Harness/Toolchain oder nicht zugeordneter Codepfad | Alle aktuellen Bereiche einschließlich Preflight |

Dateien unter `docs/` sind nicht automatisch reine Dokumentation: Buchbilder,
Fontinputs und Manifeste gehören zum Produkt. Ebenso können Markdowndateien wie
`examples/rp4/SELECTION.md` hashgebundene Produktionsinputs sein. Diese Bereiche
werden vor der Dokumentabkürzung zugeordnet. Mehrere Änderungen vereinigen ihre
Pflichten. Manuelle Auswahl im Hauptworkflow erweitert den tatsächlichen Diff.

Aktive Markdowninputs des regulären Spielerpakets bleiben im kurzen docs-Pfad:
Ein schneller Tooltest ruft denselben `package_player()`-Pfad wie Product auf,
mit den echten `player_extras()`- und README-Quellen sowie kleinen EXE-Platzhaltern.
Er prüft die tatsächliche Verpackung und Quellbytes ohne Engine/Export. Fehlende
oder nicht nachgeführte verschobene Inputs lassen diesen Pflichtjob und damit
`ci-required` scheitern. Löschung/Umbenennung jedes tatsächlichen Markdownextras
werden gezielt negativ geprüft; es gibt keine zweite Paketinputliste.

Auf `main` bleiben die bisher üblichen Integritätsprüfungen aktiv: Dokumente und
bei relevanten Änderungen die Rätselproduktion. Product/Preflight werden nach
einem Merge nicht nochmals automatisch wiederholt; ihre maßgebliche Bindung ist
der PR-/Test-Merge-Lauf. Direkte Änderungen an `main` sind weiterhin nicht erlaubt.

## Aktuelle Produktregression

Der [Product-Harness](../tools/p1_product.py) prüft die unveränderten aktiven
Ressourcenbindungen und F-01/F-02-Nachweise, importiert die temporäre reguläre
Spielkopie, führt die vollständige aktuelle Godot-Kernsuite einschließlich
Save/Recovery und ZS2-Verhalten einmal aus und prüft echten Mehrprozess-Save,
kontrollierten Start sowie den regulären Windows-Export. Der kurze absichtliche
Fehler durchläuft dieselbe `check()`-/Ergebnis-/Exit-23-Strecke wie die Suite.

`--integration` ergänzt die 500 Aktionen in fünf echten Prozessen plus Neustart
und unabhängigem Python-Orakel. `--pilots` prüft die sechs RP6-Piloten vollständig;
F04 enthält dabei die einzigartigen bisherigen RP3-Assertions einschließlich
Pfadablehnung, Spoilergrenze und Bindung des verdienten Motivs. `--visual` ergänzt
die aktuelle native Renderprüfung. Die jeweiligen `--no-*`-Schalter werden von
CI ausdrücklich übergeben; lokal sind alle drei Bereiche standardmäßig aktiv.
Ein Lauf mit ausgeschaltetem Bereich wird nicht als dessen erfolgreicher Nachweis
ausgegeben. Vollständige Produktionsrekonstruktionen gehören in den Fachlauf,
nicht zusätzlich in den Runtime-Harness.

F04 prüft nach Abschluss außerdem die bekannten unveränderten F01–F03-Zellstände
(400/1600/10000 unbekannte Zellen) und nach dem zweiten Neustart den semantischen
F01-Save (`fresh` oder gültig `loaded` mit 400 unbekannten Zellen). Erstmals erzeugte
Dateien und reguläre Start-/Flush-Metadaten bleiben zulässig. Eine zusätzliche kurze
F04-Lesegegenprobe verwendet ausschließlich eine Kopie des temporären Profils:
Ein kurzer Schreibprozess erzeugt dort über eine echte F01-Zellaktion den gültigen
veränderten Save samt History, auch wenn zuvor noch keine F01-Datei existierte.
Die neue Leseinstanz muss ihn nativ als `loaded`
mit 399 unbekannten Zellen erkannt werden und genau an der Isolationsassertion
mit Exit 4 scheitern. Erfolg, Recovery, Parserfehler oder andere Fehler werden
nicht als erfolgreiche Gegenprobe akzeptiert. Kein weiteres RP3-Durchspiel.

## Native Renderabdeckung und Speicherung

Im Standardpfad gilt `--ci-compact` für den allgemeinen Capture-Harness:

- Zellgrößen 12/16/18/22/24/72 decken Minimum, Maximum und beide Seiten der
  tatsächlichen Zeichen-/Fontwechsel ab: 54 statt 180 Zellszenarien.
- Layout: Album und drei Fixtures bei 720p/UI125 sowie 1080p/UI100+125,
  insgesamt zehn statt 41 Bilderzustände.
- H1: acht ausgewählte Off/On-Paare statt 64, ergänzt um Partialzustand,
  identische Zahlen, Tooltip und echte Drag-/Dropfälle auf beiden Achsen.
- Beide Hinweisachsen, Einrastgrenzen .49/.51, Richtungen und aktuelle
  Außenanschläge bleiben nativ geprüft. Das alte erzwungene Six-Slot-Layout
  gehört nicht mehr zum Standardpfad.
- Alpha, Papierfugen, alle Farben, X-Clipping, Hoverkreuz, Vorschau, Hinweisink,
  echte aktuelle Buch-/ZS2-Pixelverträge und Spoilergrenzen bleiben erhalten.

Die vollständigen günstigen Logik-/Zoom-/Geometrietests bleiben bestehen.
Gerenderte Bilder werden für Assertions direkt im Speicher verwendet. Der
allgemeine kompakte Capturepfad speichert fünf ausgewählte Erfolgsbilder;
Fehler sichern die zuletzt relevanten Originalframes. Die aktuelle Buch-/ZS2-
und gegebenenfalls Pilotprüfung liefert ebenfalls nur eine begrenzte Auswahl
an technischen Bildern. Anzahl gerenderter und gespeicherter Fälle sind getrennt.

Abgeschlossene ZS1-/VS1-Studien, GP48-/ZV50-/Z2-Vorherprojekte, H1-Ownerprogramme
und alte Review-ZIPs werden im Standardlauf weder importiert, gerendert noch
verpackt. Für einen konkreten historischen Vergleich wird ein separater Checkout
des gebundenen ursprünglichen Commits verwendet. Dabei dessen damalige Quellen
und Verträge lesen; keine alten Studienharnesses unbemerkt gegen neue APIs ausführen.

## Artefakte und Laufzeitbudgets

| Bereich | Ziel/Budget |
| --- | --- |
| Dokumentjob | Ziel unter einer Minute; hartes Joblimit drei Minuten |
| Gewöhnlicher Product-Lauf | Ziel fünf bis acht Minuten; hartes Joblimit zehn Minuten |
| Product einschließlich aller Piloten | Hartes Joblimit 15 Minuten |
| Toolchain-Preflight | Hartes Joblimit fünf Minuten; nur relevante Änderungen/manueller Auftrag |
| Regulärer Spieler plus technische Product-Daten | Höchstens 75.000.000 Bytes vor äußerem Actions-Container |
| Technische Product-Daten | Höchstens 20.000.000 Bytes |

Erfolgreiche Product-Läufe liefern das reguläre Windows-Spielerpaket und eine
begrenzte technische Auswahl. Technische Daten werden sieben Tage, Spielerpakete
14 Tage aufbewahrt. Erforderliche persönliche Referenzen werden vor Ablauf gezielt
dauerhaft gesichert. Preflight exportiert weiterhin wirklich, lädt standardmäßig
aber nur den kleinen Bericht und Logs hoch. Fachberichte sind ebenfalls begrenzt.

Product schreibt Bericht und laufende Phasenlogs von Anfang an unter `technical/`;
dieser Ordner wird auch nach Fehlern/Abbrüchen hochgeladen. Fehlermarker werden vor
einer eventuellen Logkürzung geprüft. Abgebrochene Phasen bleiben als solche sichtbar.
Laufzeitziele werden erst durch neue Messungen als erreicht ausgewiesen;
Warteschlangenzeit und Runnerzeit werden getrennt betrachtet.

Godot-Editor und Exportvorlagen bleiben offiziell und exakt hashgebunden. Ein
nach OS/Version/Archivhashes benannter Cache speichert nur Downloadarchive;
jedes wiederhergestellte Archiv wird erneut geprüft. Keine Prüfergebnisse cachen.
Die Fachjobs laden zusätzlich ausschließlich den benötigten RP5-Produzentencommit
`55f9e0f143bc79a4d5ff81d83d1c901b90f1797c`. Die aktuelle Windows-RP4-Regression
verlangt weiterhin offizielle isolierte Runtime/Wheel-/Commitbindung, aber keine
erneute Reproduktion des bekannten Fehlers eines alten Commits.

## Archiv und aktive Vollsichtnacharbeit

Das [BP-Archiv](design/book_inventory/ARCHIVE.md) bindet die 136 entfernten alten
Dateien mit 161.102.998 Bytes an unveränderliche Git-Objekte. Originalbilder,
aktives Papier, Fonts/Lizenzen, Manifeste und fachliche RP-/VS-Quellen bleiben.
Die drei großen Paketrekonstruktionen entfallen aus `unittest discover -s tools`;
die 13 günstigen BP-Hilfsregressionen bleiben. Keine Historienumschreibung.

[#61](https://github.com/venomenon328/picross/issues/61) benötigt weiterhin die
Originalreferenz `regular-F-01-G-ui100.png` aus Run `37948444207`, Artefakt
`11626179754`, Quelle `2c332ad688315bfa851f7c0d8642d2ab4ac3709c`.
Die unveränderten 2.088.706 Bytes sind als geschützte
[Eigentümerreferenz](https://chatgpt.com/api/library/files/libfile_658dd3b665588191a86b36e51d240320/download)
dauerhaft gesichert. PNG-SHA-256:
`0a7c386f3f52760e98bb15cbf8991cc4ae3c62d3f03af2db6d0d8c92d04c9392`;
inneres ursprüngliches Review-ZIP:
`38a908bb11bc7b27ec26c92af030b3605e00637fdaafb3bf2a4286d4908f25b5`.
Die neue Sicherung macht den Ablauf des ursprünglichen Actions-Artefakts am
23.10.2026 für diese benötigten Bytes unschädlich. Sie ist kein neues Renderbild.

PR #62 ist kein Bestandteil dieser Änderung. Vor seiner weiteren Umsetzung ist
der neue CI-Stand zu integrieren und seine zusätzliche aktuelle VS2-Prüfung in
den neuen Harness einzuordnen. Die neun regulären und zehn technischen VS-Fälle
sowie die zugesagten V1-Nachweise bleiben für diese fachliche Arbeit erforderlich.
Der alte GP48-Importfehler wird nicht als bestandener aktueller Product-Lauf
umgedeutet; #61 benötigt nach Integration passende neue Nachweise. Auf `main`
geltende Pan-Verträge bleiben bis zur tatsächlichen Vollsichtintegration aktiv.

## Verifikation dieses Pakets

Auswahltests umfassen reine Dokumentation, tatsächliche Daten-/Asset-/Pilotpfade,
Renderer, gebundene Markdowninputs, unbekannten Code und echte Umbenennungen mit
Löschung des alten Pfades. Gatetests prüfen Erfolg, Nichtzutreffen und sämtliche
fehlenden/abgebrochenen/fehlgeschlagenen Pflichtresultate. Dazu kommen aktuelle
Tool-/Fachtests, Workflowvalidierung und der echte native Product-/Windowslauf.
Konkrete gemessene Resultate, Head-/Test-Merge-Bindung und der getrennte Selbstreview
stehen im PR zu #63. Persönliche Produktabnahmen und Mergefreigabe bleiben separat.
