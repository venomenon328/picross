# RP-6 · Pilotnachweis und offene Abnahmen

Stand: 06.10.2026 · Umsetzung zu [#40](https://github.com/venomenon328/picross/issues/40).
Basis `cd4a8db86e51891f13e305b589837a1a4354c5a2`; bei Start keine Änderung seit
der vorbereiteten Basis. Branch `feat/40-pilot-production`, Ziel `main`.
RP-3/#44, RP-4/#45 R2 und RP-5/#46 R1 sind integriert. Die historischen
Baselinezeiten, Originaldateien und damaligen Reviewfelder bleiben unverändert.

Der vor neuer Bildarbeit erstellte Commit `56f25ae` bindet den vollständigen
[Plan](../examples/rp6/plan.json): sechs feste Piloten, Quellen-/Kandidaten-/
Reparatur-/Matrix-/Proof-/Bildhashes, Briefings und Versuchsbudgets. F-04 bleibt
byteidentisch; fünf Registrierungen kommen hinzu. Zwei native Bildaufrufe
(Kanne/Tulpe, je Erstfassung) von maximal zehn; keine verworfene Bildfassung,
keine neue Rasterproduktion, keine neue Reparatursuche. Drei vorhandene
Illustrationen dienen nach tatsächlicher Paarprüfung; Katze erhält nur einen
unverzerrten weißen Rahmen. [Dateien, Prompts und Operationen](../examples/rp6/artwork/preparation.json).

## Akzeptanzzuordnung

| Kriterium | Konkreter Nachweis und verbleibendes Gate |
| --- | --- |
| A01 | `manifest.json` bindet alle sechs Quellen, Revisionen, finalen Matrizen, Hinweise/Paletten über Definitionen, Proofs über Exportmanifest und Ressourcen. `rp6.verify_package` rekonstruiert alle Exporte frisch. V2-Reparaturen durchlaufen `inspect_repair` vollständig. Technisch zertifiziert, `editorial_release=false`; keine Pilotgesamtfreigabe. |
| A02 | `rp6_probe.gd` lädt die reguläre Hauptszene, wählt über Mausereignisse, prüft absichtlich falsche eigene Miniatur, Spoilergrenze, Undo/Redo, alle Farbwerkzeuge, Abschluss und korrekte Ressource. Je Pilot getrennte Prozesse partial/finish/read. Andere Slotzustände und bereits erzeugte fremde Pilotdateien bleiben erhalten. |
| A02 visuell | `rp6_capture.gd`: zehn native Bilder je Pilot, Gesamtansicht/Arbeitsdetail/Teilalbum/Abschluss/Album bei 1920×1080/UI 100 % und 1280×720/UI 125 %. Eigene Miniatur zusätzlich per Pixel geprüft, Fontressource und sichtbare Bedienelemente kontrolliert; sämtliche neun Albumknöpfe scrollbar erreichbar. Neue Paletten/Hinweise benutzen dieselbe Plex-Sans-/C1-Zeichenroutine; bestehende C1-/Z2-Pixelregressionen bleiben aktiv. |
| A03 Technik | Neue positive/negative Export-/Manifest-/Reparatur-/Assettests; alle bisherigen Fachoracles, sechs Benchmarkreferenzen, RP-3-Demo, vollständige RP-4-/RP-5-Replays, Werkzeugtests, Dokumentvalidator und Basis→Head-Diffcheck. Aktuelle sechs CI-Jobs und Windows-Artefakt sind im Draft-PR commitgebunden zu dokumentieren. |
| A03 unabhängig | Eigenes getrenntes Selbstreview und tatsächliche Bildsichtung sind keine unabhängige technische/visuelle Zweitprüfung. Diese Abnahme bleibt offen. |
| M01 | Tatsächliche eigene Paarprüfung je Pilot mit begründetem Sichturteil und Matrix-/Revealhash im Manifest. Alle sechs für den Pilot geeignet; redaktionelle Endfreigabe bleibt separat offen, kein freigegebener Katalogbestand behauptet. |
| M02 | Eigentümer löst F-04 und mindestens ein neues Farbrätsel vollständig am benannten Windows-Stand. Nicht durchgeführt; neutrale Anleitung und leeres Protokoll vorbereitet. |
| M03 | Bevorzugt F-07; vor Beginn Umfang, Revision und Beobachtungen festlegen. Zwei mal 45 Minuten sind nur ein Vorschlag. Nicht durchgeführt; keine automatische Festlegung oder vollständige Lösung behauptet. |
| M04 | Eigentümer entscheidet anhand Bilanz und tatsächlicher Spielbefunde über nächste Phase. Offen. Fehlende Probe ist kein negatives Machbarkeitsergebnis. |

## Reproduktion und Artefakte

Isolierte Python-3.11+-Image-Umgebung, Pillow 12.3.0; Godot 4.7.2-stable mit
unverändert gepinnten offiziellen Archiven. Produktprozesse maximal 300 s,
Import-/Exportprüfungen 120 s/100000 Linien; Reparaturreplay 60 s/1000000 Linien.

```sh
python -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python -m tools.puzzle_production.rp6 --output-dir artifacts/rp6-replay
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/check_docs.py
git diff --check origin/main...HEAD
python tools/p1_product.py --cache-dir <externer-cache> --output-dir <neues-ziel>
```

`product` erzeugt den kompletten Windows-Spielstand als ZIP **ohne gespeicherte
Teststände**, mit neutraler Anleitung und isoliertem `rp6-owner.ps1`-Launcher.
Die EXE bindet alle Ressourcen offline ein. Der Produktworkflow veröffentlicht
genau diese `picross-p1-windows-x86_64.zip` zusätzlich als eigenständiges
`picross-p1-player-<Head>`-Artefakt für die Eigentümerprobe. Dieses schlanke
Artefakt enthält keine Entwicklungsrender, Logs, Replays oder Teststände; der
direkte Link sowie Actions-Digest, innerer ZIP-Hash und EXE-Hashes stehen im PR.
Der vollständige technische Produktoutput bleibt davon getrennt als Evidenz erhalten.

`rp6-review-<Head>` enthält separat Manifest/Plan, sechs Paaransichten, native
Bildausgaben, alle 60 unverkleinerten RP-6-Renderbilder, Produkt-/Replayreport und
Datei-Hashinventar. `report.json` bindet Quellhead, Basis, getesteten
Checkout/Test-Merge, Run, vollständiges Windows-ZIP und EXE-Dateien. Native
Bilddateien werden nicht durch Montagen ersetzt.

Erfolgreicher Linux-CI-Export ist kein Windows-Start. Ein isolierter Windows-
Start des tatsächlich heruntergeladenen Artefakts wird gegebenenfalls zusätzlich
im PR mit EXE-Hash und eigenem Befund dokumentiert. Keine dieser technischen
Proben ersetzt M02/M03. Vorhandene vollständige Produktregression bleibt aktiv.

## Produktionsbilanz und nächste Fragen

RP-4: 19/48 logisch vollständig, 14/48 zusätzlich nach eigener Sichtung geeignet,
aus sechs Quellen. RP-5: zwei neue motivisch erhaltene Zertifikate nach je zwei
Zelländerungen; potentielle Variantenbilanz 21/48 logisch und 16/48 geeignet.
113 begonnene Bewertungen, 275 Vorschläge, 82,799 s ursprüngliche kumulative
Suchzeit. Sieben Referenzen ohne freigegebenes Endresultat bleiben ausgewiesen;
drei logisch verbesserte Teilstände sind visuell schlechter. Originalzeiten
und Abbruch bleiben im RP-5-Paket, keine Umdeutung durch späteren Replay.

RP-6 wählt sechs unterschiedliche vorhandene Motive aus: zwei Mono/vier Farbe,
drei mit beiden Dimensionen >40, zwei echte 100×100-Raster. Das ist eine Auswahl
und keine allgemeine Trefferquote. Alle sechs sind technisch zertifiziert und
nach eigener Sichtung geeignet; **null redaktionell endfreigegebene Pilotplätze**
solange die erforderliche Abnahme fehlt. Kanne: einfache Silhouette. Katze:
Motivfläche ungefähr 100×66 in 100×100. Rechtecke wurden im P1-Pilot nicht erprobt.
Größe belegt weder gefühlte Schwierigkeit noch interessante Arbeitsmenge.

Neue native Bildwerkzeugzeit: 23,7 s und 21,1 s; zwei Aufrufe, keine Korrekturrunde.
Neue technische Export-/Replay-/Prozesszeiten stehen pro Lauf im Report. Eigene
Agentenarbeit umfasst Quellenbindung, Bildaufträge, Rahmenaufbereitung, Sichtung,
Implementierung, Testnacharbeit und Dokumentation. Aktive Agentenminuten wurden
nicht separat gemessen; menschliche Minuten sind `null`/nicht beobachtet.
Keine reale Spielzeit, Lösungsstrategie oder Produktivitätsquote erfunden.

Getrennte Folgearbeit empfehlen: Erst tatsächliche Pilotspielbefunde auswerten;
danach bei erneut relevanten Fixpunkten ein ausdrücklich spezifiziertes stärkeres
Logikprofil mit eigenem Nachweisvertrag untersuchen. Eine Produktionsoberfläche
sollte zunächst Herkunft, Masken, Budget und Paarvergleich transparent machen.
Beides ist hier weder beschlossen noch implementiert. M04 entscheidet der Eigentümer.

Kein Merge, Release, Schließen von #40 oder vorzeitiger Abschluss von Parent #34.
Positiver Pilotmerge bleibt an A01–A03 und M01–M04 gebunden; einen negativen
Untersuchungsabschluss darf nur der Eigentümer ausdrücklich entscheiden.
