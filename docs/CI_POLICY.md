# Aktuelle CI-Policy

Stand: 13.10.2026 · Version 1.5 · Aufträge [#63](https://github.com/venomenon328/picross/issues/63) und [#70](https://github.com/venomenon328/picross/issues/70)

## Geltung und Ablösung

Der Eigentümer hat nach der Analyse vom 09.10.2026 die CI-Bereinigung und diesen
Prüfumfang zur Umsetzung freigegeben. Diese Policy ersetzt für neue Änderungen
die früheren pauschalen Pflichten, sämtliche sechs Jobs, historische Studien,
Vorherprojekte und vollständige Reviewgalerien bei jedem PR neu zu produzieren.
Sie gilt auch dort, wo Projektprofil, ältere Paketbeschreibungen oder historische
Prüfberichte noch den damaligen Vollumfang nennen. Fachliche Produktverträge,
gezielte aktuelle Abnahmen und die Zuordnung zum tatsächlichen Quell-/Basisstand
bleiben verbindlich. Historische Berichte behalten ihr damaliges Urteil.

Die [Eigentümerentscheidung N70-HIST-01](https://github.com/venomenon328/picross/pull/71#issuecomment-6111613992)
löst historische PERF-A-Herstellung/Reproduktion, Altzeichnerproben und A/B-
Vergleichsrekonstruktion als aktuelle Pflichten ab. R1/B-01 ist supersediert.
Die sechs produktiven Atlanten und sämtliche aktiven Runtimeverträge bleiben.
Es gibt keinen PERF-A-CI-Schalter und kein getarntes historisches Laufzeitbudget.

Der Abschlussstatus für Pull Requests heißt `ci-required` im Workflow
[CI verification](../.github/workflows/setup.yml). Er verlangt tatsächlichen
Erfolg aller ausgewählten Bereiche. Fehler, Abbruch, fehlende Auswahl und
übersprungene erforderliche Jobs sind kein Pass. Nichtzutreffen wird mit
Änderungsauswahl und Grund ausgewiesen. Es wurde kein Branchschutz verändert.

## Einmalige Inhaltsprüfung und feste Regressionen

Eigentümerentscheidung vom 12.10.2026: Rätsel werden bei ihrer Erstellung und
gezielten Integration vollständig geprüft; diese Prüfungen werden **kein Teil
der CI**. Nachweise bleiben dateigebunden im Produktionspaket. Änderungen an
Raster/Quelle verlangen die im [Regelwerk](ai-workflows/PUZZLE_AUTHORING.md)
bestimmten Neuprüfungen außerhalb der CI. Das gilt auch bei späteren Codeänderungen:
keine routinemäßige Neuzertifizierung vorhandener Rätsel.

Für reine Inhaltsintegration gilt [PUZZLE_AUTHORING §8](ai-workflows/PUZZLE_AUTHORING.md):
Adapterexport, Registrierungsplan/-transaktion und Kontrolle der übernommenen Dateien
genügen. Keine obligatorischen nativen Spiel-/Neustart-/Render-/PCK-Tests oder
Spielerbuilds außerhalb der CI je Rätsel. Zusätzliche Proben nur bei konkretem
Befund; keine doppelten manuellen Adapter-/Bestands-Replays. Allgemeine Regressionen
bei relevanten Codeänderungen bleiben unverändert.

Keine rätselspezifischen Unit-Tests oder Testgenerierung aus dem Produktionsfundus.
F01/F02-Zertifikatstests, reale RP-/VS-Korpus-Replays, der Knoblauch-Referenztest
und deren CI-Jobs sind entfallen. Historische Daten/Proofs bleiben erhalten.
Allgemeine Solver-, Verifier-, Import-, Reparatur- und Adaptertests verwenden feste
synthetische Eingänge; Registrierungstests kopieren keine produktiven Pakete.
Sämtliche nativen Funktions-/Renderläufe verwenden einen festen temporären
Katalog; zusätzliche produktive Runtime-Inhalte werden nicht hineinkopiert.
Erst für den regulären Spielerexport werden die tatsächliche Registry und ihre
Runtimeassets übernommen, ohne Rätselzertifizierung. Paketgröße/Build-I/O dieses
Code-Prüfwegs können mit dem Spiel wachsen; die Testmatrix wächst nicht.
Save- und PCK-Funktionstests nutzen feste technische Beispiele statt einer Schleife
über jeden neuen Katalogeintrag. Bestehende Motive als feste Eingabe allgemeiner
Spiel-/Darstellungstests sind keine erneute Rätselzertifizierung und werden bei
Inhaltserweiterungen nicht ergänzt.

## Auswahl nach vollständigem Änderungsumfang

[ci_scope.py](../tools/ci_scope.py) vergleicht die exakten Base-/Head-Dateibäume.
Umbenennungen zählen als alter und neuer Pfad; Löschungen werden mit erfasst.
Die beiden Commitobjekte werden gezielt flach geladen. Bei divergierter Basis
können zusätzliche Prüfungen ausgewählt werden; Basisänderungen werden dadurch
nicht versehentlich übersehen. Der tatsächliche Checkout bleibt der Test-Merge.
Auswahlbericht und Logs nennen Head, Basis, Checkout, Run und ausgewählte Pfade.

| Änderung | Automatischer Pflichtumfang im PR |
| --- | --- |
| Nur neue/geänderte Rätselpakete, Registry/Kategorien und einzelne Runtime-Inhalte | `docs`: Pfad-/Dateimodusprüfung; `ci-required`: Ergebnisgate. Keine Tests, Rekonstruktion, Bilder oder Exporte. |
| Reine normative Dokumentation/Anleitung | Schnelle Tooltests, Dokumentvalidator, vollständiger Diffcheck |
| Spielzustand, Eingabe, Save, History, Navigation | Aktuelle Kernregression, echte Prozess-Roundtrips, 500er-Route, aktuelle Pixelprüfungen und Spielerexport |
| Reine Stiftzeichnung/Capture oder aktive Buchassets | Kernregression, aktuelle Pixelprüfungen, PERF-B und Spielerexport |
| Reguläre Atlasanzeige/Cache/aktive Zelltexturen | Kernregression, aktuelle Pixelprüfungen, PERF-B und Export |
| Produktionswerkzeug-/Adaptercode, technische Fixtures oder Pilotprobes | Allgemeine Fachtests mit festen synthetischen Eingängen; ausgewählte allgemeine Spiel-/Pixel-/Exportregressionen. Keine echten Rätselreplays. |
| CI/Harness/Toolchain oder nicht zugeordneter Codepfad | Alle aktuellen Bereiche einschließlich Preflight |


**Schlanker Inhaltspfad:** Ausschließlich `content/categories.json`,
`content/registry.json`, `content/authoring/index.json`/`README.md`,
`content/authoring/<pz-ID>/<Revision>/…`, `content/packages/<pz-ID>/<Revision>/…`,
`game/data/registry.json`, `game/data/content/<stem>.json` und
`game/art/content/<stem>.png|svg|txt` gemäß der engen Positivliste in `ci_scope.py`.
Pakete erlauben ausschließlich bekannte Dokument-/Bild-/ZIP-Endungen; keine
Code-, Workflow-, Importkonfigurations- oder gemeinsamen UI-Assetpfade.
Umbenennung/Löschung zählt auf beiden Seiten. Geänderte Symlinks, ausführbare
Dateien und Submodule werden im Inhaltspfad abgewiesen.

Dieser Pfad gilt für PR und Main-Push. Sparse-/Partial-Checkout lädt nur den
Auswahlprüfer; der Git-Treevergleich liest keine Paket-, Bild- oder Proofblobs.
`docs` startet weder Tooltests noch Dokumentbaumscan. Das abschließende Gate
verlangt trotzdem Erfolg und korrekte Nichtauswahl aller übrigen Jobs.
Der CI-Bericht behauptet ausdrücklich keine Inhaltsabnahme. Kein Solver,
Proof-Replay, Hashscan des Fundus, Godot, Screenshot, PCK-Export oder Artefaktpaket
pro Rätsel. Die Job-/Testanzahl ist unabhängig vom Fundus; Git-Metadaten und der
Änderungsbericht hängen weiterhin von der Anzahl geänderter Dateien ab.
Code/Dokumentation im selben PR oder ausdrücklich erweiterter Scope verlässt
den reinen Inhaltspfad. Allgemeine Dokumentprüfung überspringt die vier
rätselspezifischen Ablagebäume; gebundene Paketdokumente prüft die Produktion.

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
Ressourcenbindungen, importiert die temporäre reguläre
Spielkopie mit festem temporärem Testkatalog, führt die aktuelle Godot-Kernsuite einschließlich
Save/Recovery und ZS2-Verhalten einmal aus und prüft echten Mehrprozess-Save,
kontrollierten Start sowie den regulären Windows-Export. Der kurze absichtliche
Fehler durchläuft dieselbe `check()`-/Ergebnis-/Exit-23-Strecke wie die Suite.

Die native Regression verwendet ausschließlich den festen technischen Katalog aus
`tests/puzzle_production/fixtures/catalog/runtime.json`. `tools/product_fixtures.py`
erzeugt sechs synthetische Definitionen/Reveals nur in temporären Projekten.
Eingefrorene KAT-1-Saves behalten separate Definitionsinputs unter `game/tests/`.
Vor dem Spielerexport ersetzt der Harness die temporären Ressourcen durch den
Produktionsbestand. Echte Inhalte werden nicht erneut zertifiziert und erhalten
keine rätselspezifischen CI-Tests. Die einmalige Katalog-/PCK-Sichtung für #114
ist ein PR-Liefernachweis, keine neue Testmatrix.

`--integration` ergänzt die 500 Aktionen in fünf echten Prozessen plus Neustart
und unabhängigem Python-Orakel. `--pilots` prüft die synthetischen Muster T04/T06/T08/T09 vollständig;
T04 enthält dabei die einzigartigen bisherigen RP3-Assertions einschließlich
Pfadablehnung, Spoilergrenze und Bindung des verdienten Motivs. `--visual` ergänzt
die aktuelle native Renderprüfung. Die jeweiligen `--no-*`-Schalter werden von
CI ausdrücklich übergeben; lokal sind alle vier ergänzenden Bereiche aktiv.
`--perf-b` prüft den regulären Atlasrenderer samt Cache-/Invalidierungslebenszyklus,
auch ohne den allgemeinen Visualbereich. Aktuelle Darstellung, Texturen und ihre
Referenz wählen PERF-B; CI/Harness/Toolchain wählen alle aktuellen Bereiche.

`tools/perf_b_resources.py` prüft exakt sechs aktive PNGs samt Importdateien,
Dateihashes, RGBA8-Maßen, Speicherobergrenze und Importparametern gegen die eigene
`tools/cell_atlas_reference.json`. Die Referenz enthält aktuelle Datei-/Pixelbindungen
und Mappingdaten; keine Herstellerquellen, Originalbilder oder Vergleichsarchive.
Positive Prüfung ohne diese Archive und Negativfälle für fehlende/zusätzliche/
veränderte Ressourcen, falsche Imports, leere/doppelte/unsichere Inventare sowie
falsche Maße/Hashes/Versionen laufen im schnellen Toolpfad. Die native B-Probe
prüft tatsächlich importierte Pixel, sechs Texturen und 48.906.240 dekodierte
Bytes; Pixelmutation, falsche Variante, stale Cache und Vollinvalidierung bleiben
Gegenproben. Shaderfarbe/Alpha, Zeitbilder, Vorschau, Undo/Redo, Sessionwechsel
und Ressourcenplateau werden im regulären Projekt und separat im gelieferten PCK
geprüft. Aktuelle goldene Varianten-/Zeit-/Region-/Fugenfälle laufen in der Kernsuite.
Historische Laufzeit-/Quellhashvergleiche sind keine Ersatzpflicht mehr.

Ein Lauf mit ausgeschaltetem Bereich wird nicht als dessen erfolgreicher Nachweis
ausgegeben. Vollständige Produktionsrekonstruktionen echter Inhalte gehören ausschließlich
in deren Produktionsauftrag, nicht in den Fachlauf oder Runtime-Harness.

T04 prüft nach Abschluss außerdem die bekannten unveränderten T01/T02/T06-Zellstände
(400/1600/2500 unbekannte Zellen) und nach dem zweiten Neustart den semantischen
T01-Save (`fresh` oder gültig `loaded` mit 400 unbekannten Zellen). Die isolierte
Partialinstanz sichert den unveränderten T01-Startstand, damit der zweite Neustart
auch die gültig geladene Variante tatsächlich prüft. JSON-Zellwerte werden numerisch
verglichen. Erstmals erzeugte Dateien und reguläre Start-/Flush-Metadaten bleiben
zulässig. Eine zusätzliche kurze
T04-Lesegegenprobe verwendet ausschließlich eine Kopie des temporären Profils:
Ein kurzer Schreibprozess erzeugt dort über eine echte T01-Zellaktion den gültigen
veränderten Save samt History, auch wenn zuvor noch keine T01-Datei existierte.
Die neue Leseinstanz muss ihn nativ als `loaded`
mit 399 unbekannten Zellen erkennen und genau an der Isolationsassertion
mit Exit 4 scheitern. Erfolg, Recovery, Parserfehler oder andere Fehler werden
nicht als erfolgreiche Gegenprobe akzeptiert. Kein weiteres RP3-Durchspiel.

## KAT-2 im Integrationspfad

`--integration` ergänzt die nativen Katalogprüfungen aus
[tools/kat2_product.py](../tools/kat2_product.py): reguläre Hauptszene mit echten
Pointerereignissen, gesonderter Prozessneustart, gültiger Leerbestand,
ungültige Registry, isolierter KAT-1-Adapterzuwachs und synthetische 300 Einträge.
Jede Instanz nutzt ein temporäres Projekt und Saveprofil. Kataloglast ist keine
300-fache Produktions-/Solverprüfung. Der Produktharness bindet alle Berichte
und die kleinen nativen Originalausschnitte an Head/Basis/Checkout; vollständige
Framekontexte bleiben lokal. Pflichtausschnitte dürfen nicht still aus der
begrenzten Lieferung fallen. Die bisherigen 30-/75-MB-Grenzen und Laufzeitlimits
bleiben unverändert. [KAT-2-Prüfzuordnung](KAT2_VERIFICATION.md).

## Native Renderabdeckung und Speicherung

ZA-1 ergänzt im ausgewählten Pilotenpfad vier temporär registrierte künstliche
Authoring-Pakete und zehn echte Prozesse für Mono/Farbe, Rechtecke, Neustarts und
Slotisolation. Native Pixelprüfungen liefern kleine Originalausschnitte samt
Koordinaten/Reports; vollständige Kontexte bleiben lokal. Der echte Windows-PCK
wird für regulären und isolierten Katalog geprüft. Der feste synthetische Adapterdurchstich liefert
nur den kompakten Bericht. Reine Inhalte wählen ausschließlich den schlanken
Inhaltspfad; Änderungen am Produktharness wählen Integration und Preflight. Keine
Budgetausnahme. [Prüfzuordnung](ZA1_VERIFICATION.md).

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

PERF-B-E1 / #68 vom 11.10.2026 hebt ausschließlich das technische Budget auf
30.000.000 Bytes an; Gesamtgrenze, Laufzeiten und Pflichtnachweise bleiben erhalten.

## Artefakte und Laufzeitbudgets

Die vollständigen aktuellen VS2-/V1-Geometriematrizen werden als `.json.gz`
verlustfrei aufbewahrt; der Artefaktleser unterstützt diese und frühere JSON-Dateien.
Die Kompression prüft den bytegleichen Rückweg. Pflichtbilder bleiben native PNGs;
die deckenden V3-Aufnahmen verwenden pixelgleiches RGB statt redundantem RGBA.
Messumfang, Pflichtnachweise und die folgenden Budgets bleiben unverändert.

| Bereich | Ziel/Budget |
| --- | --- |
| Dokumentjob | Ziel unter einer Minute; hartes Joblimit drei Minuten |
| Gewöhnlicher Product-Lauf | Ziel fünf bis acht Minuten; hartes Joblimit zehn Minuten |
| Product einschließlich aller Piloten | Hartes Joblimit 15 Minuten |
| Toolchain-Preflight | Hartes Joblimit fünf Minuten; nur relevante Änderungen/manueller Auftrag |
| Regulärer Spieler plus technische Product-Daten | Höchstens 75.000.000 Bytes vor äußerem Actions-Container |
| Technische Product-Daten | Höchstens 30.000.000 Bytes |

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
Der Fachjob führt nur allgemeine Tests, sechs synthetische Leistungsreferenzen
und den festen künstlichen Adapterdurchstich aus. Keine historischen
Produzentencommits oder RP4-/RP5-Korpus-/Windows-Replays mehr in CI.

## Separater manueller main-Player-Build

Der Workflow [Build playable main](../.github/workflows/build-main-player.yml) wird
ausschließlich über `workflow_dispatch` gestartet und checkt ausdrücklich den
aktuellen `main` aus. Er nutzt die bestehende verifizierte Godot-Toolchain und
den regulären tatsächlichen Spielkatalog, führt aber **keine** Kern-, Integrations-,
Render-, Solver- oder Rätseltests aus. Er erstellt nur den unsignierten
Windows-x64-Debugexport und kontrolliert vollständige, nicht leere Exportdateien.

`upload-artifact` übernimmt das direkte Player-Verzeichnis (EXEs, gegebenenfalls
PCK, Anleitung und benötigte Lizenzen) und erzeugt selbst das einzige
herunterladbare ZIP; kein weiteres Spieler-ZIP oder Technikartefakt. Der
bestehende Product-Verifikationsworkflow und dessen gebundene Nachweise bleiben
unverändert. Ein Build ist weder persönliche Windows-Abnahme noch Release.

## Archiv und gebundene Referenzen

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

VS2, Sidebar und PERF-A/B sind über PR #62/#66 integriert. Die alte offene
Vollsichtnacharbeit ist kein aktueller CI-Auftrag. Ihre ursprünglichen Rätselzertifikate bleiben gebunden erhalten; CI prüft
sie nicht erneut. Weitere Quellenentscheidungen und
Dateibindungen stehen im [Bestandsinventar](DEVELOPMENT_ARCHIVE.md).

## Verifikation dieses Pakets

Auswahltests umfassen reine Dokumentation, tatsächliche Daten-/Asset-/Pilotpfade,
Renderer, gebundene Markdowninputs, unbekannten Code und echte Umbenennungen mit
Löschung des alten Pfades. Gatetests prüfen Erfolg, Nichtzutreffen und sämtliche
fehlenden/abgebrochenen/fehlgeschlagenen Pflichtresultate. Dazu kommen aktuelle
Tool-/Fachtests, Workflowvalidierung und der echte native Product-/Windowslauf.
Konkrete gemessene Resultate, Head-/Test-Merge-Bindung und der getrennte Selbstreview
stehen im PR zu #70 (Vorgängermessungen in #63/#66). Persönliche Produktabnahmen und Mergefreigabe bleiben separat.
