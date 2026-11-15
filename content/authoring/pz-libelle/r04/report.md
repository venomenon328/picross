# Libelle · korrigiertes Raster LIB-R-r04

Stand 2026-11-15T20:13:44.853350+00:00. pz-libelle/r04 · Authoring 0.8.0 Dokumentrevision 7.
Quell-, Regel- und Werkzeugstand: be85306d4fc1bfd51506e846da0a2fc4c08435a1 (aktueller gelesener main).
Wiederaufnahme: r03 am Commit 40ac5e4c4d1122149382056fed5097b66c8279cc.
Die tatsächliche neue Erklärung in correction-order.txt verlangt Kopf-/Flügelkorrektur,
erlaubt Beinverlust und beauftragt Commit/Push/Draft-PR ohne Merge.

## Ergebnis und Entscheidung

LIB-R-r04: **20 × 15, Mono, genau eine tatsächlich genutzte Vordergrundfarbe
ink #263238 plus empty; L5 nach aktiver Methode 0.4**. Gegenüber r03 bleibt
das Kopfvolumen erhalten und erhält einen schmalen einzelligen Hals. Flügelansätze
werden verjüngt, der rechte Keil tiefer, Spitzen/Schultern abgerundet. Ein Beinrest
entfällt. Vier Flügel, Flugrichtung, Negativräume und zusammenhängender langer
Hinterleib bleiben erhalten. Kleine Monoauflösung bleibt deutlich abstrahiert.

Endmatrixhash 97d04514ac4b70370f5fce2fa1bf466497c3271b0ab2b68261ba73452af2ad06
Endlogikhash 768d1f8514c31db81fe96d3f4b969a89525ee95a3f4031575c8e07e83ad4530d
Reveal SHA-256 fa9115bf5ba8ad8bce8af8f19c5b5d50578e5f388692adc3c14ccc0d89a5b4da
Motiv SHA-256 a6d74de785be1908b9121d139230191ef405fa6b14548a44aa493e0e16c5e411

Originalbilder und ihre Entscheidungen bleiben bytegleich. Die Bildkorrektur
betrifft ausschließlich die diskrete Rasterableitung, keine neue Motivvorlage.
Die offenen Rasterbytes sind noch nicht gewählt. Rasterwahl, background und
Endabnahme bleiben null/offen. Erst nach tatsächlicher Wahl von LIB-R-r04 folgt
Schritt 4 mit drei unterschiedlichen Kontextzeichnungen. Kein Spieleinbau.

## Ableitung, Budgets und vollständige Prüfung

Direkte unveränderte RP-3-Referenz import22-paired/area-180; keine Ableitungskette.
Fester Plan fixed-plan-r04.json **vor dem Lauf** gespeichert: 16 Änderungen gegen
den direkten Import einschließlich der fünf früheren Änderungen, davon elf
zusätzliche Entfernungen gegenüber r03. Vollständige Schutzmaske schützt alle
übrigen erhaltenen gefüllten und leeren Zellen. Crop [1,1,21,16] entfernt weiterhin
nur ursprüngliche leere ungeschützte Außenlinien. Schutzmerkmale und Maße innerhalb
des freigegebenen Korridors; Beinverlust durch aktuelle Erklärung erlaubt.
Planbegründung ordnet jede Änderungsgruppe dem sichtbaren Defizit zu.
views-r04/diff-from-r03.png markiert genau die elf entfernten Zellen.

Kumulativ vier unterschiedliche Matrizen (zwei direkte Importe, zwei feste
Ableitungen), zwei feste Runden, 21 angewendete Editpositionen über beide Pläne
gezählt (5 + 16, wiederholte Referenzänderungen sind nicht zusätzlich neue
Bildstellen); 16 eindeutige veränderte Positionen gegen den direkten Import.
Keine Suchkandidaten oder Suchvorschläge. Maximal sechs Rasterkandidaten je Runde
bleiben eingehalten; keine weitere Kandidatenerzeugung nach Erfolg.
Solve/Verify jeweils 120 Sekunden und 100000 Linien, Paararbeit 20000000 und
250000 gleichzeitige Einträge. Endproof solved, 97 Schritte, unabhängiger frischer
Prüferprozess und exakter Endmatrixvergleich. Linienbaseline stalled, notwendiges
R4 bestätigt; vollständige Deduktion belegt zugleich Eindeutigkeit ohne zusätzliche
Suchdiagnose. Rekonstruktion, Plan und Replay über das bestehende feste Werkzeug.

100/300 Zellen (33,33%), keine leeren Innenlinien, keine orthogonal isolierte
Füllzelle; links/rechts/oben/unten Motivzellen, Randregel ohne Ausnahme erfüllt.
Pillow 12.3.0, keine neuen Werkzeuge oder Rätsel-Dauertests.

## Gebundene Einzelurteile

Norm docs/PUZZLE_QUALITY.md Vertrag 1.0, Dokumentrevision 10, SHA-256
2a5df3b78b8b6f2d11828043449e05579640fd54e8f3c4e30a0b354e688116f0 am oben genannten Commit.
Prüfer Codex, tatsächliche Sichtung 2026-11-15T20:13:44.853350+00:00. Kandidat LIB-R-r04 und Endhashes wie
oben; quality.json bindet die tatsächlich betrachteten Dateien mit Hashes.

- Q-M01 erfüllt: Unveränderte Originale B-r01/M-r02 direkt verglichen: identische schräge Aufsicht, Kopf rechts oben, vier asymmetrische Fächerflügel, langer Hinterleib links unten.

- Q-M02 erfüllt: Motivvorlage unverändert; feste Konturkorrektur bewahrt die tragenden Formen im genehmigten Maßkorridor.

- Q-M03 erfüllt: Eine tatsächliche Vordergrundfarbe ink #263238 für Silhouette; empty für Negativräume. Revealpalette bleibt reichhaltiger.

- Q-R01 erfüllt: Exakte Zellvorschau, NEAREST-Großbild und native Gittersichten mit Motiv/Reveal verglichen; Identität und Flugrichtung erhalten.

- Q-R02 erfüllt: Breiter Kopf bleibt erhalten, links und unten durch Aussparungen mit einzelligem Hals abgesetzt. Linker unterer Flügel verjüngt sich auf eine Ansatzzeile; rechter Keil vertieft, äußere Spitze und untere Schulter abgerundet. Vier Flügel bleiben getrennt lesbar. Beinrest entfällt wie ausdrücklich erlaubt. Kleine Monoauflösung bleibt stufig und abstrahiert.

- Q-R03 erfüllt: 100/300 Zellen gefüllt (33,33%), keine leere Innenzeile/-spalte und keine orthogonal isolierte Füllzelle. Freiraum trennt Flügel und Hals; Randregel an allen vier Kanten erfüllt.

- Q-R04 erfüllt: Genau ink #263238, keine Vordergrund-Farbpaare. Dunkle Flächen auf tatsächlichem Papier klar lesbar; numerischer Monobefund ersetzt keine Sichtung.

- Q-H01 erfüllt: Aktive native Atlaszellen mit Kontur/Schraffur und aktueller Papiertextur in 16/24px angesehen. Füllung, Leergrund, Fünferlinien und Zellgrenzen unterscheidbar.

- Q-H02 erfüllt: Tatsächliche Hinweise beider Achsen, ein-/zweistellig einschließlich 18, bei 16/24px normal, abgeschwächt und zusätzlich ausgekreuzt angesehen. Aktuelle Delight-Coffee-Typografie, keine Abschneidung. Mono-Hinweise neutral Ink; C1-Farbkontur im Mono-Pfad nicht einschlägig.

- Q-H03 erfüllt: 63 Hinweise, davon 31 kurze Blöcke; langer 18er-Block als Einstieg, Flügelkeile/Hals/Hinterleib erfordern Kreuzinformation. 97 Proofschritte mit notwendiger Paarlogik; Umfang und Schwierigkeit getrennt.

- H-01 erfüllt: 20x15 innerhalb ungefähr 20x16 / 18–22 x 14–18; genau eine Farbe, diskrete Werte, Hinweise und Randregel geprüft.

- H-02 erfüllt: Vollständiger Paarproof solved vom unbekannten Start; unabhängiger frischer Prüferprozess und exakte Endmatrix. Separate unabhängig bestätigte Linienbaseline stalled; R4 erforderlich. Vollständige Deduktion belegt Eindeutigkeit.

- H-03 erfüllt: Original → B-r01 → freigegebene M-r02 → unveränderter direkter RP-3-Import → fester vorab gebundener Plan/Schutzmaske → Matrix/Hinweise rekonstruiert; Nutzungsgrundlage der eigenen beauftragten ImageGen-Originale erhalten.

- H-04 erfüllt: Bild- und Motivfreigaben samt Parameter unverändert; aktuelle Erklärung erlaubt gezielte Kopf-/Flügelkorrektur und Beinverlust. Keine neue Pose, Identität, Palette oder Abstraktionsvorlage. Entscheidung über die neuen Rasterbytes bleibt offen.

- H-06 erfüllt: Aktive 0.4-Bewertung L5, Score 9/2, notwendiges R4 durch separate vollständige Belege nachgewiesen. Vollständiger unabhängiger Import des A/B-Bundles stimmt mit Checked-v3 überein; mittlere Aussagekraft, keine Lösungszeit.

H-05: Die vollständige Paket-/Inventarprüfung wird am geschriebenen ZIP frisch
durch den Builder ausgeführt; nur bei erfolgreicher Inhaltsinspektion wird
raster_ready veröffentlicht. Menschliche Rasterwahl/Endabnahme bleiben offen.

## Aktive Bewertung und Originale

0.4-Analyse und frischer unabhängiger Import: L5, Score 9/2, Denkanspruch 9/2,
Such-/Umfangsbeitrag 0 als fester R4-Anker, keine Behauptung vollständiger
Paarverlaufsmetriken. SD2-Linienpräfix: vier Wellen, 44/300 Zellen bestimmt,
bestätigter Fixpunkt stalled; separate passende Baseline stalled und Paarproof
solved, alle Belege frisch unabhängig geprüft. Gegenüber r03 steigt die
Schwierigkeit von L4 auf L5. Mittlere Aussagekraft, keine menschlichen Zeiten.
63 Hinweise, 31 kurze Blöcke. Die rein numerische Farb-ID-Abbildung für den
Runtimeanalyseinput c1 ist keine Raster-/Palettenänderung. Dazu wurde der passende
Paarproof explizit separat erzeugt und geprüft; keine Umetikettierung des Mono-Proofs.
Checked-v3 und frischer Import sind bytegleich und inventarisiert. Vollständige
unveränderte A/B-Originale werden zusätzlich unter r04/analysis/ gesichert. Der
bestehende Builder-Referenzreader unterstützt verschachtelte Dateimetadaten des
Rohberichts nicht im ZIP; deshalb getrennte Originalablage wie zuvor, keine
Umformung oder Werkzeugänderung.

Native Windows/OpenGL-Ansichten verwenden aktuellen Board-/Atlas-/Schriftcode und
Papiertextur bei 16/24px in drei Hinweiszuständen; sechs Dateien direkt gesichtet.
Alle layout_valid=true, glyph_risk=false. Isolierte eigene Ressourcenkopie,
keine Bestandsrätsel geladen, kein Buchtest, kein Katalogbild, keine Spielspeicherung.
Probe-Statusübersteuerung dient nur der Diagnosesicht und behauptet keinen
Spielerfortschritt. Quelldateien der Diagnose stehen nur als lesbare .txt-Belege.

Der stabile Produktionsbranch bleibt content/pw/pz-libelle. Frühere r01/r02/r03
und ihre Pakete bleiben unverändert am vorherigen Sicherungscommit erreichbar.
Arbeitsindex, Projektion und current-view werden gemeinsam gesichert. Keine
Zusatzbereinigung beauftragt; Arbeitsquellen für Wiederaufnahme erhalten.
