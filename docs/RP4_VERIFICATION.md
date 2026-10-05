# RP-4: Vergleichsproduktion und Prüfzuordnung

Stand: 05.10.2026 · Arbeitsfassung 0.1 · Baseline geliefert, unabhängiges Review offen

Auftrag: [#38](https://github.com/venomenon328/picross/issues/38),
[Draft-PR #45](https://github.com/venomenon328/picross/pull/45),
Branch `feat/38-comparative-production`, Basis
`aa9cc23244c60d647d8468a8d76a819f977e85a6`. [Parent #34](https://github.com/venomenon328/picross/issues/34)
bleibt offen. Fachvertrag: [Rätselproduktion](PUZZLE_PRODUCTION.md), insbesondere
§§3, 7.1–7.2 und 10. Kein P1-/Solverumbau, keine Reparatursuche oder Pilotfreigabe.

## Ergebnis und Reichweite

Zwölf feste Quellen, sechs reale Foto-/KI-Paare, 24 Imports und 48 tatsächliche
Kandidaten wurden vollständig ausgewertet. Je Arm exakt zwei vorab bestimmte
Varianten. Neun native KI-Aufrufe lieferten drei Vorlagen und sechs Stilisierungen.
Vier unterschiedliche Quellen wurden zusätzlich direkt aus ihren hochauflösenden
Bildern nach 100×100 verarbeitet; bei den zwei Fotofällen beide Vergleichsarme.
Alle Originale, Prompts, Zwischenreferenzen, Normalisierungen, Raster, Hinweise,
Proofs und Ergebnisse sind vorhanden. Keine Quelle/Variante wurde ausgetauscht.

**19/48 Kandidaten sind logisch vollständig zertifiziert; 29/48 bleiben unabhängig
bestätigte Fixpunkte.** Keine Importfehler, Widersprüche oder Ressourcenabbrüche.
Die eigene Sichtprüfung bewertet **14/48 Kandidaten aus sechs Quellen** zusätzlich
als motivisch brauchbar für diesen Vergleich. Alternative Schwellen und Größen
desselben Motivs sind darin enthalten; dies sind weder 14 unabhängige Katalogrätsel
noch freigegebene Pilotinhalte. Der Unterschied von 19 zu 14 zeigt konkret, warum
ein Zertifikat keine Motivabnahme ersetzt.

Die gespeicherte Baseline bleibt unverändert für RP-5. Ein Fixpunkt ist kein
Mehrdeutigkeitsbeweis. Laufzeit, Schrittzahl, Füllumfang und offene Zellen sind
keine menschliche Schwierigkeitsskala. Kalibrierte Schwierigkeit, reale Lösung
und finale Enthüllungsbilder wurden in RP-4 nicht geprüft.

## Dateien und vorab festgelegte Methodik

[Paketübersicht und Commit-/Hashbindung](../examples/rp4/README.md),
[Auswahl und Rechte](../examples/rp4/SELECTION.md),
[Plan](../examples/rp4/plan.json), [Input-Lock](../examples/rp4/inputs.json),
[KI-Provenienz](../examples/rp4/generation.json),
[ursprünglicher Produktionsreport](../examples/rp4/baseline/production.json),
[dateibasierter Vergleich](../examples/rp4/index.html),
[Einzelurteile](../examples/rp4/reviews.json).

Die Startprüfung las aktuelle AGENTS-/Workflow-/Profilquellen, Produktdefinition,
Gestaltungskonzept, Produktionsspezifikation, RP-2/RP-3-Prüfverträge und Anleitung
sowie #38 und Parent samt Kommentaren. Main entsprach der Vorbereitung; keine
andere RP-4-Arbeit oder Bereichsregel vorhanden. RP-2/RP-3 sind integriert;
deren historische Draftstatus werden im Dokumentationsumfang nachgeführt.

Der erste veröffentlichte Commit fixiert zwölf Dateien und Vergleichsplan.
Der zweite fixiert vor dem ersten Solverlauf alle sechs tatsächlich erzeugten
Stilisierungen und die 24 vollständigen Entwürfe. Die Veröffentlichung des zweiten
Commits ist baumidentisch zum sauberen lokalen Produzentencommit; beide Identitäten
stehen im Paket und im Git-Committext. Die ursprünglichen Ergebnisse werden nicht
mit späteren Replay-Zeiten/Status überschrieben.

Die drei klaren Illustrationen sind eigene geometrische Zeichnungen, keine
KI-Ausgaben. Die drei KI-Vorlagen sind echte native Bildausgaben. Alle sechs
Fotooriginale stammen mit dokumentierter Freigabe aus einem gepinnten öffentlichen
scikit-image-Bestand; keine fotorealistischen KI-Bilder ersetzen Fotos. Gleiches
Motivbriefing, Zielgröße, Palette, BOX-Verfahren, Weiß/Leer, Alpha-Schwelle, `contain`
und Variantenbudget gelten je Paar. Die Stilisierung darf Textur/Hintergrund
vereinfachen. Ihre tatsächlichen Formabweichungen bleiben Teil des Ergebnisses.

Mono: `area-128`, `area-176`. Farbe: `area-128`, `contour-40`.
Je Solver und unabhängigem Prüfer maximal 30 s / 100000 Linien, keine Lockerung
der bestehenden RP-1/RP-2-Referenzbudgets. Ursprüngliche Importzeiten umfassen
beide Varianten und Datei-/Bildarbeit. `elapsed_seconds` je Kandidat umfasst
Solve, Proofserialisierung und anschließende Prüfung, keine reine Solverzeit.

## Kontrollierter Fotovergleich

Nur Hauptgrößen; jeweils zwei Kandidaten je Arm. „Brauchbar“ ist die Schnittmenge
aus ursprünglichem Zertifikat, frischer unabhängiger Bestätigung und eigenem
positivem Motivurteil. Alle Varianten bleiben in der Gesamtbilanz.

| Paar | Direkt: zertifiziert / brauchbar | KI: zertifiziert / brauchbar | Beobachtung |
| --- | --- | --- | --- |
| Fotograf, 40×40 Mono | 2 / 0 | 0 / 0 | Direkt verliert Stativ/Hintergrundtrennung; KI-176 erhält brauchbare Form, bleibt logisch offen. |
| Tasse, 60×40 Farbe | 1 / 1 | 1 / 1 | Stilisierung trennt Tasse, Henkel und Löffel klarer; kein zusätzlicher Logikerfolg. |
| Rakete, 40×60 Farbe | 1 / 0 | 1 / 1 | KI erhält erkennbare Spitze/Körper, verändert Breite und Symmetrie; Direct verliert die charakteristische Spitze. |
| Uhr, 40×30 Mono | 1 / 0 | 0 / 0 | Direktraster verliert Ring; KI erfindet Innenformen aus unscharfer Information. Beide unbrauchbar. |
| Astronautin, 50×50 Farbe | 0 / 0 | 0 / 0 | Motiv bleibt erkennbar, Gesicht detailarm; beide logisch offen. |
| Katze, 60×40 Farbe | 1 / 1 | 1 / 1 | Beide Area-Raster zertifiziert; KI klärt Augen/Schnauze, verändert Fellzeichnung und Augenproportionen. |
| **Summe / je 12 Kandidaten** | **6 / 2** | **3 / 3** | Keine generelle Überlegenheit der KI aus sechs gezielt ausgewählten Fällen ableitbar. |

Die Stilisierung ist ein Gesamtverfahren einschließlich semantischer Vereinfachung
und Hintergrundbereinigung. Dieser Versuch isoliert nicht den Effekt einzelner
Filter oder ausschließlich der KI selbst. Nur eine Bildrunde je Motiv, eine feste
Palette je Paar, ein gemeinsamer Fotobestand und fehlende menschliche Zeitmessung
begrenzen die Aussage. Auch die gezielten Vorlagen entsprechen dem Flächenbriefing
nicht vollständig: Tonwechsel/zu dünne Binnenlinien erzeugen weitere Rasterfragmente.

## Große Raster und redaktionelle Sichtprüfung

Kanne, Eule, Tasse und Katze erhalten jeweils einen echten separaten 100×100-Import
aus 800×800 beziehungsweise den nativen hochauflösenden Bildern/Fotooriginalen.
Kein 40er-/60er-Zellraster wird hochskaliert. Kanne (beide Schwellen) und Katze
(Area in beiden Armen) sind logisch und motivisch brauchbar; Eule und beide
Tassenarme bleiben Fixpunkte. Rechteckige Tassen-/Katzenbilder nutzen mit `contain`
etwa 100×66 innerhalb des 100×100-Rasters; Leerstreifen sind sichtbar. Sie belegen
echte 100×100-Produktion, keine vollflächige quadratische 100×100-Komposition.
Die Kanne ist bewusst eine einfache Silhouette; ihre Größe beweist keine hohe
Detaildichte oder interessante menschliche Schwierigkeit.

Der Implementierer öffnete die zwölf Vergleichs-PNGs mit allen 24 Eingangs-/Raster-
Gruppen und 48 Varianten tatsächlich. Die neu sRGB-normalisierten Kontaktansichten
der drei ICC-Fotofälle wurden erneut kontrolliert. Die Urteile binden jeden
Kandidaten und sein Raster per Hash; wesentliche Form-/Innenraumverluste und
Änderungsbedarf stehen je Versuch in `reviews.json`. Farbmotive müssen im Raster
erkennbar sein. Mono darf durch eine motivtreue Enthüllung verständlicher werden;
`reveal_supported` dokumentiert das explizit beim KI-Fotografen. Vollständiger
Verlust wesentlicher Formen wird dadurch nicht rückwirkend geheilt.

Dies ist die geforderte eigene redaktionelle Sichtprüfung, keine unabhängige
Zweitprüfung und kein Eigentümer-Spieltest. Ein `needs_revision`-Urteil kann noch
erkennbare Teile enthalten, zählt aber nicht als brauchbarer Kandidat der Bilanz.
Die Übersicht enthält sämtliche schwachen Konturvarianten und Fehlschläge.

## Aufwand und Maschinendaten

[Aufwandserhebung](../examples/rp4/effort.json) trennt Vorbereitung, KI-Runden,
Rasterbearbeitung und Sichtprüfung. Für menschliche Minuten steht überall
**nicht beobachtet / null**; weder Null Minuten noch erfundene Schätzungen.
Die Durchführung und Sichtprüfung erfolgten durch den Agenten. Daraus lässt sich
keine belastbare Ausbeute je menschlicher Stunde berechnen; die wirtschaftliche
Produktionsfrage bleibt in diesem Punkt offen. Das ist eine sichtbare Messlücke,
kein fehlender Bild-/Logikversuch.

- Neun native KI-Aufrufe, je eine Runde, keine verworfenen/ersetzten KI-Ausgaben.
- 24 Imports, 48 Kandidaten, 48 ursprüngliche Solveraufrufe und 48 anschließende
  unabhängige Prüfungen. Keine manuellen Rasteränderungen oder Reparaturkandidaten.
- Lokaler Originaldurchlauf: 17,639 s Summe der Import-Wandzeiten, davon 10,526 s
  Summe der kandidatweisen Solve-/Serialisierungs-/Prüfzeiten. Python 3.12,
  Pillow 12.3.0. Vollständige Einzelwerte bleiben ungerundet in den JSON-Dateien.
- Je neuem vollständigen Replay weitere 48 unabhängige Proofprüfungen, keine neuen
  Solveraufrufe. Entwicklungsreplay mit Urteilsbindung: 11,614 s. Aktuelle
  commitgebundene CI-Zeiten stehen im PR/Artefakt, nicht als lokale Werte ausgegeben.
- Einzelne native Bilderzeugungszeiten wurden nicht separat gemessen; der gemeinsame
  Wartezeitblock wird nicht künstlich auf Bilder oder menschliche Minuten verteilt.

## Ansatzpunkte für RP-5

1. Gute motivische Baselines mit kleinem Rest zuerst untersuchen: Eule 40×40 Area
   (8 offene Zellen), Segelboot Area (12), Tulpe Area (16), Tasse 100×100 direkt
   (14) beziehungsweise stilisiert (13). Augen, Henkelinnenraum, Segellücke und
   Stielverbindungen als harte Schutzbereiche behandeln. Das ist ein Vorschlag
   für das separate Paket, noch keine Maskenfreigabe oder Reparatur.
2. Die direkte Astronautin hat nur vier offene Zellen, die KI-Fassung 117.
   Wenige offene Zellen garantieren keine kleine motivtreue Reparatur; Gesicht,
   Halsring und überlagerter Helm brauchen separate Sichtkontrolle.
3. Eule 100×100 (394 offen) und KI-Fotograf 176 (242 offen) zeigen Grenzen des
   bisherigen Profils/Briefings. Nicht durch unbeschränkte Änderungen „erfolgreich“
   machen. Die Ausgangsmatrix bleibt die unveränderte Änderungsreferenz.
4. Konturvarianten verlieren mit dem bestehenden Verfahren regelmäßig ganze
   Flächen; zertifiziertes Segelboot-Contour ist das Gegenbeispiel zur Gleichsetzung
   von Logik und Qualität. Für RP-5 die motivisch erhaltenen Area-Stände bevorzugen.
5. Informationsarme Uhr zurückstellen. Neue Aufnahme/Stilisierung, andere Palette,
   Größe oder Framing wären ein neuer Entwurfsauftrag, keine versteckte Reparatur
   dieser Baseline. KI-Bilderzeugung bleibt dateibasiert in ChatGPT/Codex.

## Akzeptanz, Prüfweg und offene Gates

| Kriterium | Tatsächlich gelieferter Nachweis |
| --- | --- |
| RP4-A01 | Zwölf Originale, Klassen 3/3/3/3, Herkunft/Freigabe/Hashes und dokumentierte Auswahl vor Ergebnissen; keine Ersetzung. |
| RP4-A02 | Sechs echte Direkt-/KI-Paare, vier zusätzliche 100×100-Quellen, Mono/Farbe/Rechtecke; 24 gebundene Entwürfe mit identischen Paarbudgets. |
| RP4-A03 | Alle 48 originalen Resultate/Proofs vorhanden; `inspect_candidate` rekonstruiert und replayt unabhängig, Enddomains müssen zur Matrix passen. 19 vollständig, 29 bestätigte Fixpunkte. |
| RP4-A04 | Native Aufrufe/Varianten/Solveraufrufe, echte Vorher-/Nachher-Dateien, technische Zeiten; menschliche Zeit und native Einzelzeiten ausdrücklich fehlend. Kein unzulässiger Produktivitätsquotient. |
| RP4-A05 | Tatsächliche eigene Sichtprüfung aller Raster, dateigebundene Einzelurteile und Formverluste; Mono-Enthüllungsbeitrag erlaubt, keine Pilot-/Eigentümerprobe behauptet. |
| RP4-A06 | Bericht, reproduzierbare Korpusprüfung und Hilfswerkzeugtests, unveränderte Fachoracles/Referenzen, aktueller `docs`-Job/Diffcheck im PR. Eigenes getrenntes Selbstreview; unabhängiges Review offen. |

Neue Hilfe: `tools/puzzle_production/rp4.py`; vorhandene Bild-/Solver-/Prüfalgorithmen
bleiben unverändert. Tests prüfen vollständige Abdeckung, Quellen-/Prompt-/Paar-
Manipulationen, ICC-Referenzen, fehlende Sichturteile und manipulierte Statusflags
auch nach neu gebundenen Dateihashes. Ein später erfolgreiches Replay eines
ursprünglichen Prüfungsabbruchs darf dessen Ausbeute nicht verbessern. Eigene
Illustrationen werden bytegenau aus der Quellenautorisierung reproduziert.

```sh
python3 -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python3 -m tools.puzzle_production.benchmark --output-dir artifacts/puzzle-production
python3 -m tools.puzzle_production.rp4 verify --output-dir artifacts/puzzle-production/rp4
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/check_docs.py
git diff --check aa9cc23244c60d647d8468a8d76a819f977e85a6 HEAD
```

Image-Befehle in der isolierten venv. Der vorhandene `puzzle-production`-Job führt
zusätzlich die begrenzte Korpusprüfung aus: 600 s Gesamtbudget, CI-Schritt maximal
11 Minuten; bestehendes Joblimit 15 Minuten und alle bisherigen Schritte bleiben.
KI-Erzeugung wird in CI nicht wiederholt. `product`/`preflight` bleiben aktiv und
werden im PR gesondert ausgewiesen; keine P1-Datei oder Registrierung verändert.

**Vor Merge offen:** unabhängiges qualifiziertes Review von Daten, Methodik,
tatsächlichen Bildern und technischen Nachweisen am finalen PR-Head. Eigene
Sichtprüfung/Selbstreview ersetzt es nicht. Reale Eigentümer-Lösung bleibt RP-6-Gate.
Der Auftrag erlaubt weder Merge noch Release; #34 und Folgepakete bleiben offen.

## Vollständige Fallübersicht

Variantenreihenfolge wie vorab festgelegt; die Einzelbegründungen und Originalwerte
stehen in den verlinkten Dateien. `recognizable` = im Raster erkennbar,
`reveal_supported` = zulässiger Mono-Enthüllungsbeitrag, `needs_revision` = weitere
Motivarbeit nötig, `rejected` = wesentlicher Motivverlust.

| Versuch | technische Status (in Variantenreihenfolge) | Motivurteile | Import gesamt (s) |
| --- | --- | --- | --- |
| i01-direct-40x40 | solved / solved | recognizable / recognizable | 0.109 |
| i01-direct-100x100 | solved / solved | recognizable / recognizable | 0.524 |
| i02-direct-60x40 | stalled / solved | recognizable / rejected | 0.168 |
| i03-direct-40x40 | stalled / stalled | recognizable / rejected | 0.127 |
| a01-direct-40x40 | stalled / stalled | recognizable / needs_revision | 0.611 |
| a01-direct-100x100 | stalled / stalled | recognizable / needs_revision | 1.934 |
| a02-direct-60x40 | solved / solved | recognizable / recognizable | 0.549 |
| a03-direct-50x50 | solved / stalled | recognizable / needs_revision | 0.678 |
| p01-direct-40x40 | solved / solved | needs_revision / rejected | 0.147 |
| p01-stylized-40x40 | stalled / stalled | needs_revision / reveal_supported | 0.480 |
| p02-direct-60x40 | solved / stalled | recognizable / needs_revision | 0.399 |
| p02-stylized-60x40 | solved / stalled | recognizable / needs_revision | 0.771 |
| p02-direct-100x100 | stalled / stalled | recognizable / needs_revision | 1.567 |
| p02-stylized-100x100 | stalled / stalled | recognizable / needs_revision | 1.626 |
| p03-direct-40x60 | solved / stalled | needs_revision / needs_revision | 0.239 |
| p03-stylized-40x60 | solved / stalled | recognizable / needs_revision | 0.564 |
| h01-direct-40x30 | stalled / solved | rejected / rejected | 0.073 |
| h01-stylized-40x30 | stalled / stalled | needs_revision / needs_revision | 0.371 |
| h02-direct-50x50 | stalled / stalled | recognizable / needs_revision | 0.549 |
| h02-stylized-50x50 | stalled / stalled | recognizable / needs_revision | 0.847 |
| h03-direct-60x40 | solved / stalled | recognizable / needs_revision | 0.412 |
| h03-stylized-60x40 | solved / stalled | recognizable / needs_revision | 1.000 |
| h03-direct-100x100 | solved / stalled | recognizable / needs_revision | 1.429 |
| h03-stylized-100x100 | solved / stalled | recognizable / needs_revision | 2.466 |
